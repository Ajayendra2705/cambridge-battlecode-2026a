// Part of bot.cpp: Movement: field descent, dashes, stepping away from threats, walking or recalling home.
// Unity build: bot.cpp includes this inside its anonymous namespace; not a standalone header.

// ---- Movement ----
constexpr std::array<vec2, 8> DIRS{vec2{1, 0}, vec2{-1, 0}, vec2{0, 1}, vec2{0, -1}, vec2{1, 1}, vec2{1, -1},
    vec2{-1, 1}, vec2{-1, -1}};

bool safe_move(vec2 t) {
    try {
        if (cambc::self().move_absolute(t)) {
            S.me = t;
            return true;
        }
    } catch (const cambc::error&) {
    }
    return false;
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
        occ.set(best);
    }
    return false;
}

// Dash along the field when it skips ahead, then walk.
bool step_static(const distance_field& field, int here) {
    auto& me = cambc::self();
    const vec2 p = S.me;
    if (here >= 4 && me.can_cast()) {
        for (const auto& ab : me.abilities()) {
            if (!ab.is_dash() || !ab.is_ready()) continue;
            vec2 best = p;
            int best_d = here - 1;
            for (auto t : ab.valid_tiles().positions()) {
                if (S.occ.is_set(t) || W.terrain.is_set(t)) continue;
                if (S.avoid_danger && in_danger(t)) continue;
                const int d = field.get(t);
                if (d < best_d) best_d = d, best = t;
            }
            try {
                if (best != p && ab.use(best)) {
                    S.me = best;
                    if (me.can_move()) descend(field, S.occ, field.get(S.me));
                    return true;
                }
            } catch (const cambc::error&) {
            }
        }
    }
    return descend(field, S.occ, here);
}

// Step towards `roots` (field value `stop_at` or less counts as arrived); route around occupants if needed.
bool step_field(const distance_field& field, const bitboard& roots, int stop_at = 0) {
    auto& me = cambc::self();
    if (!me.can_move()) return false;
    const int here = field.get(S.me);
    if (here <= stop_at) return false;
    if (step_static(field, here)) return true;
    if (!me.can_move()) return false;
    distance_field local;
    bitboard visited, mine;
    mine.clear();
    mine.set(S.me);
    const auto free_roots = roots & ~S.occ;
    local.compute_to((W.terrain | S.occ) & ~free_roots & ~mine, free_roots, mine, visited);
    const int local_here = local.get(S.me);
    if (local_here == UNREACH) return false;
    return descend(local, S.occ, local_here);
}

// Walk to any free tile of `goals` using a fresh field around current occupants.
bool step_to_tiles(const bitboard& goals) {
    auto& me = cambc::self();
    if (!me.can_move() || goals.is_set(S.me)) return false;
    bitboard visited, mine;
    mine.clear();
    mine.set(S.me);
    const auto free_goals = goals & ~S.occ & ~W.terrain;
    if (free_goals.is_empty()) return false;
    distance_field local;
    local.compute_to((W.terrain | S.occ) & ~free_goals & ~mine, free_goals, mine, visited);
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
    bool exposed = S.round - enemy_seen_at <= 3;
    for (const auto& e : S.enemies) if (dist(e.pos, S.me) <= 5) exposed = true;
    if (W.spawn_field.get(S.me) > 5 && !exposed) { cambc::self().recall(); return; }
    if (!walk_home() && !exposed) cambc::self().recall();
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
            if (best == S.me) return false;
            safe_move(best);
            return true;
        }
    }
    step_field(W.spawn_field, W.ally_spawn, 0);
    return true;
}
