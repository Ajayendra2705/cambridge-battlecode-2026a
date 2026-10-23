// Part of bot.cpp: Known units, take_snapshot (one engine call per unit), unseen awake camps, group state updates.
// Unity build: bot.cpp includes this inside its anonymous namespace; not a standalone header.

// Known units, built once: camps by spawn tile (camps never move) and every champion's handle.
struct KnownCamp { cambc::camp camp; int group; float max_hp, str; int range; int idx; };

// Camp attack range straight from the engine (3.0: elks reach 4, monoliths 5); the table is only a fallback.
int camp_kind_range(const cambc::camp& c) {
    try {
        return c.attack_range();
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
    for (int gi = 0; gi < static_cast<int>(W.groups.size()); ++gi) {
        const auto& g = W.groups[gi];
        const auto camps = g.group.camps();
        for (size_t i = 0; i < camps.size(); ++i) {
            const vec2 pos = g.spawns[i];
            camp_index[pos.y * cm::width() + pos.x] = static_cast<std::int16_t>(known_camps.size());
            known_camps.push_back({camps[i], gi, g.max_hp[i], g.strength[i], camp_kind_range(camps[i]), static_cast<int>(i)});
        }
    }
    // A group inside another group's monolith or golem range cannot be farmed while that camp is alive.
    W.covered_by.assign(W.groups.size(), {});
    for (const auto& k : known_camps) {
        if (k.range <= CAMP_RANGE || k.group < 0) continue;
        const vec2 at = W.groups[k.group].spawns[k.idx];
        W.strong_camps.push_back({at, k.range, k.group});
        for (int gi = 0; gi < static_cast<int>(W.groups.size()); ++gi) {
            if (gi == k.group) continue;
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
        S.hp = info.health;
        S.max_hp = info.max_health;
        S.str = info.strength;
        S.range = info.attack_range;
    }
    S.visible = cv::visible_tiles();
    S.camps.clear();
    S.occ = cv::teleport_tiles();
    // Engine 3.0 reports which camps are awake; camps can attack without our damage having woken them.
    static std::vector<char> awake_at;
    awake_at.assign(static_cast<size_t>(cm::width() * cm::height()), 0);
    for (const auto pos : cv::awake_camp_tiles().positions()) awake_at[pos.y * cm::width() + pos.x] = 1;
    for (const auto pos : cv::camp_tiles().positions()) {
        S.occ.set(pos);
        const int idx = camp_index[pos.y * cm::width() + pos.x];
        if (idx < 0) continue;
        const auto& k = known_camps[idx];
        cambc::detail::camp_state cs{};
        if (cambc::detail::sdk_camp(static_cast<std::uint32_t>(static_cast<cambc::handle_camp_t>(k.camp)), &cs) != 0) continue;
        if (cs.health <= 0) continue;
        S.camps.push_back({k.camp, pos, cs.health, k.max_hp, k.str, k.group, k.range, awake_at[pos.y * cm::width() + pos.x] != 0});
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
void build_phantoms() {
    S.phantoms.clear();
    for (const auto& k : known_camps) {
        if (k.group < 0 || k.str <= 0) continue;
        const auto& g = W.groups[k.group];
        if (g.state != 0 || S.round - g.awake_round > 4) continue;
        const vec2 pos = g.spawns[k.idx];
        if (S.visible.is_set(pos) || g.hp[k.idx] <= 0) continue;
        S.phantoms.push_back({k.camp, pos, g.hp[k.idx], k.max_hp, k.str, k.group, k.range, true});
    }
}

void update_knowledge() {
    const int round = S.round;
    for (auto& g : W.groups) {
        bool seen = false;
        for (auto sp : g.spawns) if (S.visible.is_set(sp)) { seen = true; break; }
        if (!seen) {
            if (g.state == 2 && round >= g.respawn_round) { g.state = 0; g.reset(); }
            continue;
        }
        // Any visible member alive means the group is up; read live health from the snapshot.
        bool any_live = false;
        for (const auto& c : S.camps) if (c.group >= 0 && &W.groups[c.group] == &g) { any_live = true; break; }
        if (any_live) {
            g.state = 0;
            for (size_t i = 0; i < g.spawns.size(); ++i) {
                if (!S.visible.is_set(g.spawns[i])) continue;
                g.hp[i] = 0;
                for (const auto& c : S.camps) if (c.pos == g.spawns[i]) { g.hp[i] = c.hp; break; }
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
