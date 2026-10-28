// Part of bot.cpp: fight_or_approach: respawn wait, capture, standoff casting, gathering, hitting camps.
// Unity build: bot.cpp includes this inside its anonymous namespace; not a standalone header.

void fight_or_approach(int gi) {
    auto& me = cambc::self();
    auto& g = W.groups[gi];
    const int range = S.range;
    std::vector<const CampSnap*> live;
    for (const auto& c : S.camps)
        if (c.group == gi) live.push_back(&c);

    if (live.empty()) {
        if (g.state == 2) {
            // Respawning: a body on a spawn tile delays it, so wait beside the group.
            if (g.tiles.is_set(S.me)) {
                if (!me.can_move()) { ACT("resp_wait"); return; }
                const auto occ = S.occ | g.tiles;
                for (auto d : DIRS) {
                    vec2 t{S.me.x + d.x, S.me.y + d.y};
                    if (cm::is_in_bounds(t) && !W.terrain.is_set(t) && !occ.is_set(t) && safe_move(t)) break;
                }
            } else if (group_field(g).get(S.me) > 2) {
                step_field(group_field(g), g.tiles, 2);
            }
            ACT("resp_wait");
            return;
        }
        // Dead or unseen: walk onto a spawn tile (captures when the group is down).
        if (g.tiles.is_set(S.me)) { ACT("capture"); use_support_abilities(false); return; }
        ACT("to_capture");
        step_field(group_field(g), g.tiles, 0);
        return;
    }


    // Stellar out-ranges ordinary camps (spells 4, camps 3): it farms them from spell range and takes no hits.
    bool caster_standoff = me.champion_name() == cambc::champion_type::stellar;
    bool any_strong = false;
    for (const auto* c : live) {
        if (c->str > 0) any_strong = true;
        if (c->str > 0 && c->range > CAMP_RANGE) caster_standoff = false;
    }
    if (standoff(g) || (caster_standoff && any_strong)) {
        // Stand exactly at spell range of the target and outside every dangerous camp's reach; cast only.
        const CampSnap* target = choose_camp(live);
        bitboard goals, near;
        goals.clear();
        near.clear();
        goals.draw_chebyshev(target->pos, 4.0f);
        for (const auto* c : live)
            if (c->str > 0) near.draw_chebyshev(c->pos, static_cast<float>(c->range));
        goals = goals & ~near;
        ACT("standoff");
        if (goals.is_set(S.me)) {
            cast_from_range(live, *target);
            return;
        }
        if (near.is_set(S.me)) {
            std::vector<vec2> threats;
            for (const auto* c : live) if (c->str > 0) threats.push_back(c->pos);
            step_away(threats);
        } else {
            step_to_tiles(goals);
        }
        if (goals.is_set(S.me)) cast_from_range(live, *target);
        return;
    }

    // Big groups (many elks) shred champions who arrive one by one: wait for most of the team, at most 25 rounds per
    // group life. The count used to restart after every approach step, so a champion waited 25 rounds per step
    // (platform 00monolith: 10 idle rounds per 100 alive off camps and enemies, the rivals 3.6).
    if (gi != big_wait_group || g.damaged()) big_wait = 0, big_wait_group = gi;
    // probe h2pr2l (HG): the gather rule skipped only because members out of view kept the dead group's 0 health.
    if (!g.damaged() && g.strength_left() < 200 && g.strength_left() + pr_hz_str(gi) >= 200) {
        ++pr_hg_turns;
        if (pr_hg_last != gi) {
            pr_hg_last = gi;
            std::cout << "HG " << S.round << " " << W.slot << " " << gi << " " << static_cast<int>(g.strength_left()) << " "
                      << static_cast<int>(pr_hz_str(gi)) << '\n';
        }
    }
    if (!g.damaged() && g.strength_left() >= 200) {
        int present = 1;
        for (const auto& a : S.allies)
            for (const auto* c : live)
                if (dist(a.pos, c->pos) <= 6) { ++present; break; }
        if (present < std::min(4, alive_allies()) && big_wait < 25) {
            ++big_wait;
            if (group_field(g).get(S.me) > 5) step_field(group_field(g), g.tiles, 5);
            ACT("gather");
            return;
        }
    }
    STAGE("cf choose");
    const CampSnap* target = choose_camp(live);
    // Spells reach further than camps: cast before closing in.
    if (dist(S.me, target->pos) > range) {
        if (use_camp_abilities(live, *target, g.damaged()) && !me.can_move()) return;
        bitboard goals;
        goals.clear();
        goals.draw_chebyshev(target->pos, static_cast<float>(range));
        if (!step_to_tiles(goals)) {
            // Every free tile in reach of the chosen camp can be taken (teammates, other camps): 678 stuck approach
            // turns per 80 games in the bf2 audit. Then take a tile in reach of any live camp of the group.
            bitboard any;
            any.clear();
            for (const auto* c : live) any.draw_chebyshev(c->pos, static_cast<float>(range));
            // (A last walk_towards here, for turns whose searches were skipped for fuel, ran the same path search
            // without the fuel check: it costs as much as one of ours.)
            if (!step_to_tiles(any)) step_field(group_field(g), g.tiles, 0);
        }
    }
    STAGE("cf hit");
    // Hit the chosen camp if in range, otherwise the weakest one in range.
    const CampSnap* hit = dist(S.me, target->pos) <= range ? target : nullptr;
    if (!hit) {
        std::vector<const CampSnap*> reach;
        for (const auto* c : live) if (dist(S.me, c->pos) <= range) reach.push_back(c);
        if (!reach.empty()) hit = choose_camp(reach);
    }
    ACT("approach");
    if (!hit) return;
    ACT("fight");
    attack_unit(hit->camp);
    if (!use_camp_abilities(live, *hit, true)) try_attack_reset_and_hit(hit->camp);
    use_support_abilities(true);
}
