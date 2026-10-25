// Part of bot.cpp: Known units, take_snapshot (one engine call per unit), unseen awake camps, group state updates.
// Unity build: bot.cpp includes this inside its anonymous namespace; not a standalone header.

// Known units, built once: camps by spawn tile (camps never move) and every champion's handle.
struct KnownCamp { cambc::camp camp; int group; float max_hp, str; int range; int idx; };

// Camp attack range straight from the engine (3.0: elks reach 4, monoliths 5), read once per kind (camp::attack_range()
// is the same design query as base_stats); the table is only a fallback.
int camp_kind_range(const cambc::camp& c) {
    try {
        return camp_stats_of(c).base_attack_range;
    } catch (const cambc::error&) {
    }
    switch (c.kind()) {
        case cambc::camp_type::monolith: return 5;
        case cambc::camp_type::golem: return 4;
        default: return CAMP_RANGE;
    }
}
struct KnownChamp { cambc::champion ch; cambc::champion_type type; bool ally; FightCoef coef{}; };
std::vector<KnownCamp> known_camps;
std::vector<std::int16_t> camp_index;  // Per tile, index into known_camps or -1.
std::vector<KnownChamp> known_champs;

void init_units() {
    camp_index.assign(static_cast<size_t>(cm::width() * cm::height()), -1);
    std::size_t total = 0;
    for (const auto& g : W.groups) total += g.spawns.size();
    known_camps.reserve(total);
    for (int gi = 0; gi < static_cast<int>(W.groups.size()); ++gi) {
        auto& g = W.groups[gi];
        const auto camps = g.group.camps();
        g.first_camp = static_cast<int>(known_camps.size());
        g.camp_count = static_cast<int>(camps.size());
        for (size_t i = 0; i < camps.size(); ++i) {
            const vec2 pos = g.spawns[i];
            camp_index[pos.y * cm::width() + pos.x] = static_cast<std::int16_t>(known_camps.size());
            known_camps.push_back({camps[i], gi, g.max_hp[i], g.strength[i], camp_kind_range(camps[i]), static_cast<int>(i)});
        }
    }
    // A group inside another group's monolith or golem range cannot be farmed while that camp is alive.
    // Fuel: every strong camp (elks reach 4 too) against every spawn of every group took 430k on boss_battle, four
    // opening rounds (pf5 probe). A group's bounding box rules most pairs out with four comparisons.
    W.covered_by.assign(W.groups.size(), {});
    struct Box { int x0, y0, x1, y1; };
    std::vector<Box> box(W.groups.size(), Box{1 << 20, 1 << 20, -(1 << 20), -(1 << 20)});
    for (size_t gi = 0; gi < W.groups.size(); ++gi)
        for (auto sp : W.groups[gi].spawns)
            box[gi] = {std::min(box[gi].x0, sp.x), std::min(box[gi].y0, sp.y), std::max(box[gi].x1, sp.x), std::max(box[gi].y1, sp.y)};
    W.strong_camps.reserve(known_camps.size());
    for (const auto& k : known_camps) {
        if (k.range <= CAMP_RANGE || k.group < 0) continue;
        const vec2 at = W.groups[k.group].spawns[k.idx];
        W.strong_camps.push_back({at, k.range, k.group});
        for (int gi = 0; gi < static_cast<int>(W.groups.size()); ++gi) {
            if (gi == k.group) continue;
            const Box& b = box[gi];
            if (at.x + k.range < b.x0 || at.x - k.range > b.x1 || at.y + k.range < b.y0 || at.y - k.range > b.y1) continue;
            auto& cov = W.covered_by[gi];
            if (std::find(cov.begin(), cov.end(), k.group) != cov.end()) continue;
            for (auto sp : W.groups[gi].spawns)
                if (dist(sp, at) <= k.range) { cov.push_back(k.group); break; }
        }
    }
    const auto self_id = handle_id(cambc::self());
    for (const auto side : {team::ally, team::enemy})
        for (const auto& c : cambc::champions(side))
            if (handle_id(c) != self_id) known_champs.push_back({c, c.champion_name(), side == team::ally});
}

// One engine call per visible unit: read the raw state structs instead of one accessor at a time.
void take_snapshot() {
    auto& me = cambc::self();
    S.round = static_cast<int>(cambc::round_number());
    {
        cambc::detail::champion_info info{};
        cambc::detail::check(cambc::detail::sdk_champion(handle_id(me), &info));
        S.me = {info.x, info.y};
        S.start = S.me;
        S.hp = info.health;
        S.max_hp = info.max_health;
        S.str = info.strength;
        S.range = info.attack_range;
        S.state = static_cast<std::uint32_t>(info.state);
    }
    S.walked = S.attacked = S.view_moved = false;
    S.visible = cv::visible_tiles();
    S.camps.clear();
    // Every champion the engine shows us, in one call: champions read one by one below can miss some, and a move onto
    // a tile the engine knows is taken throws ("Known occupied destination": 87 per 80 games in the bf2 audit).
    S.occ = cv::teleport_tiles() | cv::champion_tiles();
    S.occ.set(S.me, false);
    // Fuel: each bitboard is_set is a host call, and the group update asked it for every spawn tile and scanned every
    // visible camp per group (up to 38k fuel a turn on yellow_brick_road, bf6 profile). Read the view once into packed
    // bits (see in_view), and each visible camp's health into a per-camp array.
    const int w = cm::width();
    const std::size_t view_bytes = bitboard::linear_buffer_size();
    if (view_bits.empty()) view_bits.resize((view_bytes + 7) / 8 * 8);
    S.visible.export_linear_buffer(std::span<std::uint8_t>(view_bits.data(), view_bytes));
    {
        // Rows of the first and last set bit, a word at a time (bit k of word j is tile 64 j + k).
        const std::size_t words = view_bits.size() / 8;
        const auto word = [&](std::size_t j) {
            std::uint64_t v;
            std::memcpy(&v, view_bits.data() + 8 * j, 8);
            return v;
        };
        std::size_t a = 0, b = words;
        std::uint64_t x = 0;
        while (a < words && (x = word(a)) == 0) ++a;
        if (a == words) {
            view_row_lo = 0, view_row_hi = -1;
        } else {
            view_row_lo = (static_cast<int>(64 * a) + __builtin_ctzll(x)) / w;
            while ((x = word(b - 1)) == 0) --b;
            view_row_hi = (static_cast<int>(64 * (b - 1)) + 63 - __builtin_clzll(x)) / w;
        }
    }
    camp_hp_now.assign(known_camps.size(), 0.0f);
    group_live_now.assign(W.groups.size(), 0);
    // Engine 3.0 reports which camps are awake; camps can attack without our damage having woken them. A round stamp per
    // known camp: clearing a per-tile flag array every turn cost about 12k fuel on big_world (pf9 probe), and filling a
    // per-tile array once about 50k (40 kB on the first turn, pf12).
    static std::vector<int> awake_at;
    if (awake_at.empty()) awake_at.assign(known_camps.size(), -1);
    for (const auto pos : cv::awake_camp_tiles().positions()) {
        const int idx = camp_index[pos.y * w + pos.x];
        if (idx >= 0) awake_at[idx] = S.round;
    }
    for (const auto pos : cv::camp_tiles().positions()) {
        S.occ.set(pos);
        const int idx = camp_index[pos.y * w + pos.x];
        if (idx < 0) continue;
        const auto& k = known_camps[idx];
        cambc::detail::camp_state cs{};
        if (cambc::detail::sdk_camp(static_cast<std::uint32_t>(static_cast<cambc::handle_camp_t>(k.camp)), &cs) != 0) continue;
        if (cs.health <= 0) continue;
        S.camps.push_back({k.camp, pos, cs.health, k.max_hp, k.str, k.group, k.range, awake_at[idx] == S.round});
        camp_hp_now[idx] = cs.health;
        if (k.group >= 0) group_live_now[k.group] = 1;
        if (S.camps.back().awake && k.group >= 0) W.groups[k.group].awake_round = S.round;
    }
    S.allies.clear();
    S.enemies.clear();
    for (auto& k : known_champs) {
        cambc::detail::champion_info info{};
        if (cambc::detail::sdk_champion(handle_id(k.ch), &info) != 0) continue;
        if (info.x < 0 || info.y < 0 || info.health <= 0) continue;
        const vec2 pos{info.x, info.y};
        S.occ.set(pos);
        ChampSnap snap{k.ch, pos, info.health, info.max_health, info.strength, info.attack_range, 0};
        snap.type = k.type;
        // Killers take every carried gem: knowing who carries what makes them targets.
        if (!k.ally) {
            try {
                snap.gems = k.ch.gem_count();
            } catch (const cambc::error&) {
            }
        }
        if (!k.coef.ready) {
            try {
                k.coef = read_coef(k.ch);
            } catch (const cambc::error&) {
            }
        }
        const float scale = damage_scale(k.type, info.health, info.max_health);
        snap.dps = champion_dps(k.coef, info.strength, info.focus) * scale;
        // Teams alternate turns and the first team swaps each round, so an enemy can act twice between two of our turns:
        // count its second basic attack (platform big hits: reset champions dealt 1.3-1.8x the one-turn burst).
        snap.burst = (champion_burst(k.coef, info.strength, info.focus) + (k.ally ? 0.0f : info.strength)) * scale;
        snap.reach = std::max(snap.range, k.coef.spell_range) + 1;
        // A dash adds two tiles before a basic attack.
        if (k.coef.dash) snap.reach = std::max(snap.reach, snap.range + 3);
        (k.ally ? S.allies : S.enemies).push_back(snap);
    }
    // Damage spells cannot follow a step, so a caster threatens its spell range; melee threatens a step plus reach.
    S.danger.clear();
    S.avoid_danger = false;
    for (const auto& e : S.enemies) {
        if (W.enemy_spawn.is_set(e.pos) || e.burst < S.hp * (fragile ? 0.15f : 0.3f)) continue;
        S.danger.push_back({e.pos, (e.reach > e.range + 1 ? e.reach - 1 : e.range + 1) + (fragile ? 1 : 0)});
    }
}

void broadcast_respawn(int group, int respawn_round);

// Camps never move, so a known camp that is out of sight is still where it was. Its group is treated as awake
// for a few rounds after a member was last seen awake or an unexplained hit came from its range.
// Fuel: one pass over every known camp cost 3-6k a turn on maps with 150 camps (pf11 probe). known_camps holds each
// group's camps together, so groups that are not up or not recently awake are skipped whole (same list, same order).
void build_phantoms() {
    S.phantoms.clear();
    for (const auto& g : W.groups) {
        if (g.state != 0 || S.round - g.awake_round > 4) continue;
        for (int ki = g.first_camp; ki < g.first_camp + g.camp_count; ++ki) {
            const auto& k = known_camps[ki];
            if (k.group < 0 || k.str <= 0) continue;
            const vec2 pos = g.spawns[k.idx];
            if (in_view(pos) || g.hp[k.idx] <= 0) continue;
            S.phantoms.push_back({k.camp, pos, g.hp[k.idx], k.max_hp, k.str, k.group, k.range, true});
        }
    }
}

void update_knowledge() {
    const int round = S.round;
    const int w = cm::width();
    for (size_t gi = 0; gi < W.groups.size(); ++gi) {
        auto& g = W.groups[gi];
        bool seen = false;
        // Fuel: checking every spawn tile of every group against the view cost 4.5-9k a turn (pf11 probe); a group
        // whose rows lie outside the view's rows cannot be in view.
        if (g.row_hi >= view_row_lo && g.row_lo <= view_row_hi)
            for (auto sp : g.spawns) if (in_view(sp)) { seen = true; break; }
        if (!seen) {
            if (g.state == 2 && round >= g.respawn_round) { g.state = 0; g.reset(); }
            continue;
        }
        // Any visible member alive means the group is up; read live health from the snapshot.
        if (group_live_now[gi]) {
            g.state = 0;
            for (size_t i = 0; i < g.spawns.size(); ++i) {
                if (!in_view(g.spawns[i])) continue;
                const int idx = camp_index[g.spawns[i].y * w + g.spawns[i].x];
                g.hp[i] = idx >= 0 ? camp_hp_now[idx] : 0.0f;
            }
            continue;
        }
        const int prev = g.state;
        const auto handle = static_cast<std::uint32_t>(static_cast<cambc::handle_camp_group_t>(g.group));
        std::uint32_t raw = 0;
        if (cambc::detail::sdk_camp_group_state(handle, &raw) == 0) {
            if (raw == 1) g.state = 0;
            else if (raw == 2) g.state = 1;
            else if (raw == 3) {
                std::int32_t timer = 0;
                cambc::detail::sdk_camp_group_cooldown(handle, &timer);
                g.state = 2;
                g.respawn_round = round + timer;
                if (prev != 2) broadcast_respawn(static_cast<int>(&g - W.groups.data()), g.respawn_round);
            }
        }
        if (g.state == 0 && prev == 2) g.reset();
        if (g.state != 0) std::fill(g.hp.begin(), g.hp.end(), 0.0f);
    }
}
