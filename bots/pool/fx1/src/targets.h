// Part of bot.cpp: Target choice: pick_group scores every camp group; bank_gems walks to an altar and tributes.
// Unity build: bot.cpp includes this inside its anonymous namespace; not a standalone header.

// ---- Targets ----
distance_field from_me_field() {
    distance_field f;
    bitboard roots, visited;
    roots.clear();
    roots.set(S.me);
    f.compute(W.terrain & ~roots, roots, visited);
    return f;
}

int travel_to(const distance_field& f, const Group& g) {
    int t = UNREACH;
    for (auto s : g.spawns) t = std::min<int>(t, f.get(s));
    return t;
}

// Per-champion choice: rate of value per champion-round, assuming teammates already heading to a group help
// clear it. A defeated group needs only one capturer.
// Opening: until this champion owns its first emblem, it farms alone. The top-10 teams make 16 solo captures and
// 1 shared one in the first 300 rounds (we made 6 and 5): parallel farms beat pairs while nobody has items.
bool solo_phase() {
    static bool done = false;
    if (done) return false;
    const auto counts = cambc::self().item_count();
    for (int i = 0; i < static_cast<int>(cambc::item_type::enum_type::count); ++i) {
        const auto x = cambc::item_type{static_cast<cambc::item_type::enum_type>(i)};
        if (!x.result() && counts[x] > 0) { done = true; return false; }  // An emblem has no further result.
    }
    return true;
}

// Fuel: the BFS from us costs about 30k on big maps. Walking distance is symmetric, so the distance from us to a
// group's nearest camp is that group's own field (rooted at its camps) read at our tile: same numbers for one read
// each. The fields are built once, one per turn without a pick (build_travel_field); until all exist we use the BFS.
std::vector<std::unique_ptr<distance_field>> travel_fields;
int travel_built = 0;
void build_travel_field() {
    if (travel_fields.empty()) travel_fields.resize(W.groups.size());
    if (travel_built >= static_cast<int>(W.groups.size())) return;
    bitboard roots;
    roots.clear();
    for (auto s : W.groups[travel_built].spawns) roots.set(s);
    auto f = std::make_unique<distance_field>();
    bitboard visited;
    f->compute(W.terrain & ~roots, roots, visited);
    travel_fields[travel_built++] = std::move(f);
}

std::vector<int> group_invested;  // Per group: rounds we targeted it since it was last seen defeated.
int pick_group(int current) {
    const int round = S.round;
    std::uint64_t gd_fuel = 0;
    const auto pf0 = cambc::fuel_remaining();
    const bool fields_ready = travel_built >= static_cast<int>(W.groups.size()) && travel_built > 0;
    const distance_field f = fields_ready ? distance_field{} : from_me_field();
    const auto pf1 = cambc::fuel_remaining();
    const float dps = my_dps();
    // Fastest our damage can take a group down, for the bound: its health over our best damage per round.
    const double bound_dps = std::max({1.0, static_cast<double>(dps), static_cast<double>(my_spell_dps())});
    const int team_alive = alive_allies();
    const bool solo = solo_phase();
    double best = 0, current_score = 0;
    int best_i = -1, best_n = 1, current_n = 1;
    // Fuel: big_world and road_of_riches ran out of fuel 200-380 times per game in this loop. Score every group's
    // upper bound first (travel weight, side and mid factors; the rest only lowers a score), then do the costly
    // estimate in bound order and skip groups whose bound cannot beat the best so far.
    struct Cand { double ub, value; int i, travel; };
    std::vector<Cand> cands;
    for (int i = 0; i < static_cast<int>(W.groups.size()); ++i) {
        const auto& g = W.groups[i];
        const int travel = fields_ready ? travel_fields[i]->get(S.me) : travel_to(f, g);
        if (travel == UNREACH) continue;
        // Before the first emblem gold is worth a gem: it buys the stats that win the next fights (top-10 teams take
        // 6.9 gold clusters and 7.0 small groups before round 300, we took 4.0 and 3.5).
        const double value = g.gems + g.gold * (solo ? 2.0 : gold_weight(round));
        if (value <= 0) continue;
        const int side = W.group_side[i];
        const bool safe_speed = side <= 0 || round - enemy_seen_round > 30;
        const bool mid_push = W.team_count > 4;  // Small teams lose the early middle fights (b2: 3-4 champion maps).
        double mult = mid_push && round < 400 && side >= -6 && side <= 6 && travel <= 20 ? 2.0 : 1.0;
        if (side > 0) mult /= 1.0 + std::min(side, 20) / 20.0;
        // Clearing takes at least its health over our damage (champion-rounds), except a defeated group: capture only.
        const double fight = g.state == 1 ? 0.0 : g.hp_left() / bound_dps;
        cands.push_back({value * mult / ((safe_speed ? 1.0 : 0.7) * travel + fight + 5.0), value, i, travel});
    }
    std::sort(cands.begin(), cands.end(), [](const Cand& a, const Cand& b) { return a.ub > b.ub; });
    for (const auto& cand : cands) {
        const int i = cand.i, travel = cand.travel;
        const double value = cand.value;
        if (i != current && cand.ub <= best) continue;
        const auto& g = W.groups[i];
        // Speed where it is safe: on our half, or with no enemy seen for 30 rounds, favour near groups and never wait
        // for respawns (farm race vs starter: -4% rounds). Contested groups keep the careful weights: there the faster
        // picks walked into enemies (concentrated_wealth, corridors: flee deaths +21%).
        const bool safe_speed = W.group_side[i] <= 0 || round - enemy_seen_round > 30;
        bool covered = false;
        // A sleeping monolith or golem attacks nobody: only an awake one (seen within 10 rounds) makes its neighbours
        // unfarmable. Contest: the enemy farmed the four centre gold clusters next to sleeping monoliths all game.
        for (int b : W.covered_by[i]) {
            const auto& cb = W.groups[b];
            if (cb.state != 0) continue;
            const bool strong = *std::max_element(cb.strength.begin(), cb.strength.end()) >= 100.0f;
            // Elks reach 4 since 3.0 and count as covering camps. Asleep they hit nobody: a cluster (no strength, cleared
            // in a few hits) beside sleeping elks is free (starvation: the enemy farmed one 19 times, we never did).
            const bool cluster = *std::max_element(g.strength.begin(), g.strength.end()) <= 0.0f;
            if ((!strong && !cluster) || round - cb.awake_round <= 10) covered = true;
        }
        // The altar guard is itself a monolith group: its own range must not exclude it.
        if (covered) continue;
        const int others = claimants(i);
        double score = 0;
        int score_n = 1;
        if (g.state == 1) {
            // One capturer: the claimant who gains most from the gold keeps it, everyone else moves on.
            const int mine = 16 * 16;
            bool better_claim = false;
            for (int s = 0; s < MAX_SLOTS && s < static_cast<int>(W.slot_types.size()); ++s)
                if (claim_cache[s] == i && capture_priority(W.slot_types[s]) * 16 + s > mine) better_claim = true;
            if (better_claim || (others > 0 && i != current)) continue;
            // At most two share a capture: the two with the fewest items stay, so gold reaches the poorest champions
            // (platform lg1: slot order starved Ryth and Marcella, slots 3 and 4, to half the gold of the others).
            if (others >= 2) {
                const int mine_w = slot_wealth_now(W.slot);
                int poorer = 0;
                for (int s = 0; s < MAX_SLOTS && s < static_cast<int>(W.slot_ids.size()); ++s) {
                    if (s == W.slot || claim_cache[s] != i) continue;
                    const int w = slot_wealth_now(s);
                    if (w >= 0 && (w < mine_w || (w == mine_w && s < W.slot))) ++poorer;
                }
                if (poorer >= 2) continue;
            }
            score = value / (travel + 5.0 + g.bank_cost * bank_share(g));
        } else if (standoff(g)) {
            const float spell = my_spell_dps();
            if (spell <= 0) continue;
            const int n = others + 1;
            double time = travel + g.hp_left() / (spell * n);
            if (g.state == 2) time += (safe_speed ? 4.0 : 2.0) * std::max(0, g.respawn_round - round - travel);
            score = value / (time * n + 5 + g.bank_cost * 0.5 * bank_share(g));
            score_n = n;
        } else {
            const int home = W.spawn_field.get(g.spawns[0]);
            const ClearStats cs = clear_stats(g);
            const std::array<int, 3> sizes{others + 1, std::min(std::max(others + 1, team_alive), others + 2),
                                           std::max(others + 1, team_alive)};
            for (int n : sizes) {
                double time = travel * (safe_speed ? 1.0 : 0.7) + clear_time(cs, n, dps, S.max_hp, home == UNREACH ? 30 : home);
                if (g.state == 2) time += (safe_speed ? 4.0 : 2.0) * std::max(0, g.respawn_round - round - travel);
                time += (n - others - 1) * 4;  // Waiting for extra teammates.
                // One champion then captures (5 rounds), walks to an altar and tributes.
                const double sc = value / (time * n + 5 + g.bank_cost * 0.5 * bank_share(g));
                if (sc > score) score = sc, score_n = n;
            }
        }
        // Groups nearer the enemy spawn are contested: worth less unless they are clearly closer for us.
        const int side = W.group_side[i];
        if (side > -8) {
            int recent = 0;
            for (int r : death_rounds) if (round - r < 400) ++recent;
            (void)recent;  // Aggressive: keep contesting even after deaths.
        }
        if (side > 0) score /= 1.0 + std::min(side, 20) / 20.0;
        // Take the middle first: in losses the enemy took 4.9 mid groups before round 300 (1.9 in our wins) and killed
        // us twice there; we farmed our own half. Contested groups are worth more to us before they are worth it to them.
        if (W.team_count > 4 && round < 400 && side >= -6 && side <= 6 && travel <= 20) score *= 2.0;
        // Avoid walking into enemy groups; a lone enemy matters less than several.
        const auto gd0 = cambc::fuel_remaining();
        const double danger = sightings.empty() ? 0.0 : group_danger(g);
        gd_fuel += gd0 - cambc::fuel_remaining();
        if (danger > 0) score /= 1.0 + danger * 0.25;
        // Futility: rounds this champion already spent on the group since it last went down. Platform starvation and
        // rows: the team worked one contested group for 250-400 rounds per champion while the enemy farmed and took it.
        if (!group_invested.empty()) score /= 1.0 + group_invested[i] / 150.0;
        // The altar guard blocks every tribute: its worth grows with the gems we cannot bank, and it takes the team.
        if (i == current) current_score = score, current_n = score_n;
        if (score > best) best = score, best_i = i, best_n = score_n;
    }
    TRACE("pick bfs=" << (pf0 - pf1) << " loop=" << (pf1 - cambc::fuel_remaining()) << " danger=" << gd_fuel);
    if (current >= 0 && current_score > 0 && current_score * 1.05 >= best) {
        planned_team = current_n;
        return current;
    }
    planned_team = best_n;
    return best_i;
}

// A defeated group nearby that nobody is capturing yet: one champion stays to capture it.
bool bank_gems() {
    // While the altar guard lives, every tile in tribute range is blocked: a trip there only wastes rounds.
    if (W.altar_guard >= 0 && W.groups[W.altar_guard].state == 0) return false;
    auto& me = cambc::self();
    for (auto altar : W.altars) {
        if (dist(S.me, altar) <= cambc::constants::submit_gems_range) {
            // An enemy altar lock makes submit_gems throw (altar_locked): break it with basic attacks first.
            // Platform boss_battle: 330-370 rounds of bank attempts per champion and zero tributes against locks.
            try {
                if (cambc::vision::has_altar_lock(altar)) {
                    const auto lock = cambc::vision::altar_lock_at(altar);
                    if (lock.is_enemy()) {
                        if (me.can_attack() && dist(S.me, lock.position()) <= S.range) {
                            me.attack(lock);
                            return true;
                        }
                        if (me.can_move() && dist(S.me, lock.position()) > S.range) me.move_towards(lock.position());
                        return true;
                    }
                }
            } catch (const cambc::error&) {
            }
            try {
                me.submit_gems(altar);
                return true;
            } catch (const cambc::error&) {
            }
        }
    }
    return step_field(W.altar_field, W.altar_tiles, cambc::constants::submit_gems_range);
}

// Best camp to hit: biggest strength removed per point of damage; clusters (no strength) last.
// Splash attackers (Varg) also value camps whose neighbours take the splash.
bool splash = false;

const CampSnap* choose_camp(const std::vector<const CampSnap*>& live) {
    const CampSnap* best = nullptr;
    double best_s = -1;
    for (const auto* c : live) {
        double s = (c->str + 1.0) / std::max(1.0f, c->hp);
        if (splash) {
            int neighbours = 0;
            for (const auto* o : live) if (o != c && dist(o->pos, c->pos) <= 1) ++neighbours;
            s *= 1 + neighbours;
        }
        if (s > best_s) best_s = s, best = c;
    }
    return best;
}
