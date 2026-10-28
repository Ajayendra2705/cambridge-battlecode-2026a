// Part of bot.cpp: Movement: field descent, dashes, stepping away from threats, walking or recalling home.
// Unity build: bot.cpp includes this inside its anonymous namespace; not a standalone header.

// ---- Movement ----
constexpr std::array<vec2, 8> DIRS{vec2{1, 0}, vec2{-1, 0}, vec2{0, 1}, vec2{0, -1}, vec2{1, 1}, vec2{1, -1},
    vec2{-1, 1}, vec2{-1, -1}};

// Route to a group around the reaches of other live monoliths and golems. The field was built once and kept, so the
// detour stayed after the strong camp died (and was missing after it came back): rebuild when that set changes.
distance_field& group_field(Group& g) {
    const int gi = static_cast<int>(&g - W.groups.data());
    std::uint64_t key = 0;
    for (size_t i = 0; i < W.strong_camps.size() && i < 64; ++i) {
        const auto& c = W.strong_camps[i];
        if (c.group != gi && W.groups[c.group].state == 0) key |= std::uint64_t{1} << i;
    }
    const auto zone_of = [&] {
        bitboard zone;
        for (size_t i = 0; i < W.strong_camps.size() && i < 64; ++i)
            if (key >> i & 1) zone.draw_chebyshev(W.strong_camps[i].pos, static_cast<float>(W.strong_camps[i].range));
        return zone;
    };
    // A rebuild is a full-map field: on a turn with less fuel left than its measured cost, the old route serves one more
    // turn (a fixed 40k floor ran big_world turns out of fuel, where one field costs over 50k).
    const auto affordable = [] { return cambc::fuel_remaining() > field_cost + 15000; };
    const auto build = [&](const bitboard& blocked) {
        const auto f0 = cambc::fuel_remaining();
        bitboard visited;
        g.field->compute(blocked & ~g.tiles, g.tiles, visited);
        const auto f1 = cambc::fuel_remaining();
        if (f1 < f0) field_cost = std::max(field_cost, f0 - f1);
    };
    const auto build_detour = [&] {
        build(W.route_terrain | zone_of());
        // Fall back to the plain route when the detour cuts the group off from home (the old check read only the
        // first spawn tile); with no fuel left for it, finish on a later turn.
        bool ok = false;
        for (const auto sp : W.ally_spawn.positions())
            if (g.field->get(sp) != UNREACH) { ok = true; break; }
        if (ok) return;
        if (affordable()) build(W.route_terrain);
        else g.field_key = ~key;
    };
    if (!g.field || (key != g.field_key && affordable())) {
        if (!g.field) g.field = std::make_unique<distance_field>();
        g.field_key = key;
        g.opened_round = -100;
        g.open_reach.reset();
        build_detour();
    } else if (g.open_reach && !g.open_reach->is_set(S.me) && affordable()) {
        // Out of the reach the route was opened for: close it again, or a shorter way could lead back through it.
        g.open_reach.reset();
        build_detour();
    }
    // Standing in a reach the route avoids (a fight or a flight put us there), or behind one, the route read
    // unreachable here and walks to the group stood still: 66 of 80 traced stuck walks to a capture in the au9 audit.
    // Open the reach we stand in until we are out of it, else take the plain route; at most every 5 rounds.
    if (g.field->get(S.me) == UNREACH && S.round - g.opened_round >= 5 && affordable()) {
        g.opened_round = S.round;
        const bitboard zone = zone_of();
        if (zone.is_set(S.me)) {
            bitboard inside = (~zone | W.terrain).reachable_tiles(S.me, 255);
            inside.set(S.me);
            build(W.route_terrain | (zone & ~inside));
            g.open_reach = std::make_unique<bitboard>(inside);
        }
        if (g.field->get(S.me) == UNREACH && affordable()) {
            build(W.route_terrain);
            g.open_reach.reset();
        }
    }
    return *g.field;
}

bool safe_move(vec2 t) {
    // One move per turn. Loops that try each neighbour in turn hit "Movement already used" once the move was spent
    // (55 per 80 games in the au9 audit) and marked every tile they tried as occupied for the rest of the turn.
    if (stale() || S.walked || !cambc::self().can_move()) return false;
    refresh_occ();
    if (S.occ.is_set(t) || stale()) return false;
    try {
        if (cambc::self().move_absolute(t)) {
            moved_to(t);
            S.walked = true;
            return true;
        }
        // False means a hidden unit stands there. The tile is now known occupied, and a second try at it throws
        // ("Known occupied destination": 423 per 80 games in the audit build, when a later step chose the same tile).
        S.occ.set(t);
    } catch (const cambc::error&) {
        S.occ.set(t);  // Refused: do not pick it again this turn.
    }
    return false;
}

// One step along the shortest path to `t`, as the SDK's move_towards takes it, but around the tiles we know are held
// (S.occ also has hidden units that refused a move) and never onto `t` itself while a unit holds it: walking at an enemy
// or a camp from the next tile chose the goal's own tile ("Known occupied destination" in the au9 audit).
bool walk_towards(vec2 t) {
    if (stale() || S.walked || S.me == t || !cm::is_in_bounds(t) || !cambc::self().can_move()) return false;
    refresh_occ();
    bitboard blocked = W.terrain | S.occ | cv::camp_tiles();
    const bool goal_held = blocked.is_set(t);
    blocked.set(S.me, false);
    blocked.set(t, false);
    bitboard roots, mine, visited;
    roots.set(t);
    mine.set(S.me);
    distance_field field;
    field.compute_to(blocked, roots, mine, visited);
    vec2 best = S.me;
    int best_d = field.get(S.me);
    for (auto d : DIRS) {
        const vec2 n{S.me.x + d.x, S.me.y + d.y};
        if (!cm::is_in_bounds(n) || blocked.is_set(n) || (n == t && goal_held)) continue;
        const int v = field.get(n);
        if (v < best_d) best_d = v, best = n;
    }
    return best != S.me && safe_move(best);
}

// Take the free neighbour with the lowest field value below `here`; hidden blockers are skipped.
bool descend(const distance_field& field, bitboard occ, int here) {
    const vec2 p = S.me;
    for (int attempt = 0; attempt < 3; ++attempt) {
        vec2 best = p;
        int best_d = here;
        for (auto d : DIRS) {
            vec2 t{p.x + d.x, p.y + d.y};
            if (!cm::is_in_bounds(t) || W.terrain.is_set(t) || occ.is_set(t)) continue;
            if (S.avoid_danger && in_danger(t)) continue;
            const int v = field.get(t);
            if (v < best_d) best_d = v, best = t;
        }
        if (best == p) return false;
        if (safe_move(best)) return true;
        occ |= S.occ;  // With what safe_move found: the refused tile, units that came into view since our dash.
        occ.set(best);
    }
    return false;
}

// Tiles a dash can land on. valid_tiles() is the casting range only (SDK: it "does not filter visibility, occupancy or
// target categories"), so most picks from it failed: an audit build counted 94 failed landing dashes per game
// ("Destination is unreachable within movement range"). A dash moves along a path of up to `range` 8-direction steps
// that may cross holes but not walls, altars, enemy spawn tiles or units, and lands on a free walkable tile other than
// its start (the SDK's own walk avoids enemy spawn tiles too; with them left open, a landing reached only across them
// was refused: "Destination is unreachable within movement range", once per 80 games in the au14 audit).
bitboard dash_landings(const cambc::ability& ab) {
    int range = 2;
    if (ab.info())
        if (const auto* d = std::get_if<cambc::ability_dash>(&*ab.info())) range = std::max(1, static_cast<int>(d->range));
    refresh_occ();
    const bitboard path_block = cm::walls() | cm::altars() | W.enemy_spawn | S.occ;
    bitboard land = path_block.reachable_tiles(S.me, static_cast<std::uint16_t>(range));
    land = land & ~W.terrain & ~S.occ;
    land.set(S.me, false);
    return land;
}

// The field leads on across a hole next to us (a route over thin holes, dh1): only a dash takes that step.
bool hole_ahead(const distance_field& field, int here) {
    if (!W.has_dash) return false;
    for (auto d : DIRS) {
        const vec2 t{S.me.x + d.x, S.me.y + d.y};
        if (cm::is_in_bounds(t) && W.thin_holes.is_set(t) && field.get(t) < here) return true;
    }
    return false;
}

// Dash along the field when it skips ahead, then walk.
bool step_static(const distance_field& field, int here) {
    if (stale()) return false;
    auto& me = cambc::self();
    const vec2 p = S.me;
    if ((here >= 4 || hole_ahead(field, here)) && me.can_cast()) {
        for (const auto& ab : me.abilities()) {
            if (!ab.is_dash() || !ab.is_ready()) continue;
            vec2 best = p;
            int best_d = here - 1;
            for (auto t : dash_landings(ab).positions()) {
                if (S.occ.is_set(t) || W.terrain.is_set(t)) continue;
                if (S.avoid_danger && in_danger(t)) continue;
                const int d = field.get(t);
                if (d < best_d) best_d = d, best = t;
            }
            if (stale()) return false;  // The landing search can run the turn out of fuel.
            try {
                if (best != p && ab.use(best)) {
                    moved_to(best);
                    if (me.can_move()) {
                        refresh_occ();
                        descend(field, S.occ, field.get(S.me));
                    }
                    return true;
                }
                if (best != p) S.occ.set(best);  // A hidden unit holds the landing tile.
            } catch (const cambc::error&) {
                S.occ.set(best);
            }
        }
    }
    return descend(field, S.occ, here);
}

// A local search (a fresh field around occupants and danger) is not run on a turn that it could run out of fuel: a
// turn that runs out resumes next round on a stale snapshot. In the au10 audit one cost 4k fuel at the median, 11k at
// the 95th percentile and 25k at most (longer searches and some maps cost more). A fixed 20k floor skipped about 270
// searches per 80 games, and those turns stood still: require this map's recent worst cost plus a margin instead.
int local_cost_max = 12000;
bool local_search_affordable() { return cambc::fuel_remaining() >= static_cast<std::uint64_t>(local_cost_max) + 5000; }
void note_local_cost(std::uint64_t before) {
    const int cost = static_cast<int>(before - cambc::fuel_remaining());
    local_cost_max = std::max(local_cost_max - local_cost_max / 16, cost);
}

// Step towards `roots` (field value `stop_at` or less counts as arrived); route around occupants if needed.
bool step_field(const distance_field& field, const bitboard& roots, int stop_at = 0) {
    auto& me = cambc::self();
    if (!me.can_move()) return false;
    const int here = field.get(S.me);
    if (here <= stop_at) return false;
    if (step_static(field, here)) return true;
    // The way on crosses a hole and the dash is not back yet: wait at the edge (its cooldown is 8 turns) rather than set
    // off on the walk round, which the next turn's route would turn back from. After 10 turns of waiting (no free
    // landing, or danger on it) walk instead.
    static int wait_from = -100, wait_last = -100;
    if (hole_ahead(field, here)) {
        if (wait_last < S.round - 1) wait_from = S.round;
        wait_last = S.round;
        if (S.round - wait_from < 10) {
            S.dash_wait = true;
            return false;
        }
    }
    if (!me.can_move() || !local_search_affordable()) return false;
    const auto fuel_before = cambc::fuel_remaining();
    distance_field local;
    bitboard visited, mine;
    mine.clear();
    mine.set(S.me);
    const auto free_roots = roots & ~S.occ;
    // Route around occupants, and around enemy danger once moves avoid it: descend skips danger tiles, so a straight
    // way through them stood still (the bf5 audit traced most of 1,300 stuck walks per 80 games to this).
    const bitboard avoid = S.avoid_danger ? danger_tiles() & ~mine : bitboard{};
    local.compute_to((W.terrain | S.occ | avoid) & ~free_roots & ~mine, free_roots, mine, visited);
    note_local_cost(fuel_before);
    const int local_here = local.get(S.me);
    if (local_here == UNREACH) return false;
    return descend(local, S.occ, local_here);
}

// Walk to any free tile of `goals` using a fresh field around current occupants (and enemy danger once moves avoid it).
bool step_to_tiles(const bitboard& goals) {
    auto& me = cambc::self();
    if (!me.can_move() || goals.is_set(S.me) || !local_search_affordable()) return false;
    bitboard visited, mine;
    mine.clear();
    mine.set(S.me);
    const bitboard avoid = S.avoid_danger ? danger_tiles() & ~mine : bitboard{};
    const auto free_goals = goals & ~S.occ & ~W.terrain & ~avoid;
    if (free_goals.is_empty()) return false;
    const auto fuel_before = cambc::fuel_remaining();
    distance_field local;
    local.compute_to((W.terrain | S.occ | avoid) & ~free_goals & ~mine, free_goals, mine, visited);
    note_local_cost(fuel_before);
    const int here = local.get(S.me);
    if (here == UNREACH) return false;
    return step_static(local, here);
}

// Steps of the shortest walk to any free tile of `goals` (0 if already on one, UNREACH if blocked).
int steps_to_tiles(const bitboard& goals) {
    if (goals.is_set(S.me)) return 0;
    bitboard visited, mine;
    mine.clear();
    mine.set(S.me);
    const auto free_goals = goals & ~S.occ & ~W.terrain;
    if (free_goals.is_empty()) return UNREACH;
    distance_field local;
    local.compute_to((W.terrain | S.occ) & ~free_goals & ~mine, free_goals, mine, visited);
    return local.get(S.me);
}

// Move to the free neighbour that maximises distance from the given threats, preferring home.
bool step_away(const std::vector<vec2>& threats) {
    if (!cambc::self().can_move() || threats.empty()) return false;
    const vec2 p = S.me;
    int cap = CAMP_RANGE;
    for (auto th : threats) {
        const int idx = camp_index[th.y * cm::width() + th.x];
        if (idx >= 0) cap = std::max(cap, known_camps[idx].range);
    }
    auto score = [&](vec2 t) {
        int m = 1 << 20;
        for (auto th : threats) m = std::min(m, dist(t, th));
        return std::min(m, cap + 1) * 1000 - W.spawn_field.get(t);
    };
    vec2 best = p;
    int best_s = score(p);
    for (auto d : DIRS) {
        vec2 t{p.x + d.x, p.y + d.y};
        if (!cm::is_in_bounds(t) || W.terrain.is_set(t) || S.occ.is_set(t)) continue;
        const int s = score(t);
        if (s > best_s) best_s = s, best = t;
    }
    return best != p && safe_move(best);
}

// Step to a neighbour outside every enemy's reach, preferring the way home.
bool step_out_of_danger() {
    if (!cambc::self().can_move()) return false;
    const vec2 p = S.me;
    vec2 best = p;
    int best_d = UNREACH;
    for (auto d : DIRS) {
        vec2 t{p.x + d.x, p.y + d.y};
        if (!cm::is_in_bounds(t) || W.terrain.is_set(t) || S.occ.is_set(t) || in_danger(t)) continue;
        const int v = W.spawn_field.get(t);
        if (v < best_d) best_d = v, best = t;
    }
    return best != p && safe_move(best);
}

int enemy_seen_at = -100;  // Mirrors enemy_seen_round, which is declared later.

// Recall is cancelled by damage, so never start it with an enemy close by: walk instead (top teams do this).
bool walk_home();
void go_home() {
    if (stale()) return;
    bool exposed = S.round - enemy_seen_at <= 3;
    for (const auto& e : S.enemies) if (dist(e.pos, S.me) <= 5) exposed = true;
    if (W.spawn_field.get(S.me) > 5 && !exposed) { cambc::self().recall(); return; }
    if (!walk_home() && !exposed && !stale()) cambc::self().recall();  // The walk's search can run the turn out of fuel.
}

// Step toward spawn without crossing an awake camp's reach (a monolith beside the path kept hitting us).
// Returns false when the only way down enters a reach and we stay put.
bool walk_home() {
    bitboard reach;
    reach.clear();
    for (const auto& c : S.camps) if (c.awake) reach.draw_chebyshev(c.pos, static_cast<float>(c.range));
    for (const auto& c : S.phantoms) reach.draw_chebyshev(c.pos, static_cast<float>(c.range));
    if (!reach.is_set(S.me) && cambc::self().can_move()) {
        const int here = W.spawn_field.get(S.me);
        vec2 best = S.me;
        int best_v = here;
        for (auto d : DIRS) {
            vec2 t{S.me.x + d.x, S.me.y + d.y};
            if (!cm::is_in_bounds(t) || W.terrain.is_set(t) || S.occ.is_set(t)) continue;
            const int v = W.spawn_field.get(t);
            if (v < best_v) best_v = v, best = t;
        }
        if (best != S.me && reach.is_set(best)) {
            // Detour: any free downhill neighbour outside reach, else wait here (recall when nobody is near).
            best = S.me;
            for (auto d : DIRS) {
                vec2 t{S.me.x + d.x, S.me.y + d.y};
                if (!cm::is_in_bounds(t) || W.terrain.is_set(t) || S.occ.is_set(t) || reach.is_set(t)) continue;
                if (W.spawn_field.get(t) <= here && (best == S.me || W.spawn_field.get(t) < W.spawn_field.get(best))) best = t;
            }
            if (best == S.me) {
                // No step down outside the reach: route around it on a fresh field when that way is not much longer,
                // rather than stand still (the one-step detour above sees only downhill neighbours).
                if (!local_search_affordable()) return false;
                const auto fuel_before = cambc::fuel_remaining();
                distance_field local;
                bitboard visited, mine;
                mine.set(S.me);
                const auto goals = W.ally_spawn & ~S.occ;
                local.compute_to((W.terrain | S.occ | reach) & ~goals & ~mine, goals, mine, visited);
                note_local_cost(fuel_before);
                const int h = local.get(S.me);
                return h != UNREACH && h <= here + 8 && descend(local, S.occ, h);
            }
            safe_move(best);
            return true;
        }
    }
    step_field(W.spawn_field, W.ally_spawn, 0);
    return true;
}
