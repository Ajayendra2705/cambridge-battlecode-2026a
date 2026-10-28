// Part of bot.cpp: Target choice: pick_group scores every camp group; bank_gems walks to an altar and tributes.
// Unity build: bot.cpp includes this inside its anonymous namespace; not a standalone header.

// ---- Targets ----
distance_field from_me_field() {
    distance_field f;
    bitboard roots, visited;
    roots.clear();
    roots.set(S.me);
    f.compute(W.route_terrain & ~roots, roots, visited);
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
    const auto& weights = shard_weights();
    int i = 0;
    for (const auto n : counts)  // An emblem (weight 5) has no further result.
        if (weights[i++] == 5 && n > 0) { done = true; return false; }
    return true;
}

// Fuel: the BFS from us costs about 30k on big maps. Walking distance is symmetric, so the distance from us to a
// group's nearest camp is that group's own field (rooted at its camps) read at our tile: same numbers for one read
// each. The fields are built once, one per turn without a pick (build_travel_field); until all exist we use the BFS.
std::vector<std::unique_ptr<distance_field>> travel_fields;
int travel_built = 0;
bool travel_ready() { return travel_built >= static_cast<int>(W.groups.size()) && travel_built > 0; }
void build_travel_field() {
    if (travel_fields.empty()) travel_fields.resize(W.groups.size());
    if (travel_built >= static_cast<int>(W.groups.size())) return;
    const auto f0 = cambc::fuel_remaining();
    bitboard roots;
    roots.clear();
    for (auto s : W.groups[travel_built].spawns) roots.set(s);
    auto f = std::make_unique<distance_field>();
    bitboard visited;
    f->compute(W.route_terrain & ~roots, roots, visited);
    travel_fields[travel_built++] = std::move(f);
    const auto f1 = cambc::fuel_remaining();
    if (f1 < f0) field_cost = std::max(field_cost, f0 - f1);
}

std::vector<int> group_invested;  // Per group: rounds we targeted it since it was last seen defeated.
// Per group: round until which the way there counts as blocked by enemy danger (set after two turns stuck on it).
std::vector<int> blocked_until;

// Death marks: where one of us was killed lately; the enemies that did it are likely still there. Repeat deaths (within
// 6 tiles and 150 rounds of an earlier death of ours) are 3.2 per game against the rivals' 1.9, and 1.35 of them die
// outnumbered by two or more (rivals 0.32): a teammate walks alone into the pack that just killed one of us (cw1 on
// bvp + bhp, tools/replay/repeat.py). Vision is not shared, but a teammate's death is: its handle's is_alive needs no
// vision. Its place is the group it last claimed (within 30 rounds); our own is where we stood.
struct DeathMark { vec2 pos; int round; };
std::vector<DeathMark> death_marks;
constexpr int DEATH_MARK_ROUNDS = 120;
void add_death_mark(vec2 pos) {
    std::erase_if(death_marks, [](const DeathMark& m) { return S.round - m.round >= DEATH_MARK_ROUNDS; });
    if (death_marks.size() >= 8) death_marks.erase(death_marks.begin());
    death_marks.push_back({pos, S.round});
}
std::array<int, MAX_SLOTS> mate_claim{}, mate_claim_round{};
std::array<bool, MAX_SLOTS> mate_alive{};
void track_mate_deaths() {
    static bool init = false;
    if (!init) mate_claim.fill(-1), mate_claim_round.fill(-1000), mate_alive.fill(true), init = true;
    const int groups = static_cast<int>(W.groups.size());
    for (int s = 0; s < W.team_count && s < MAX_SLOTS; ++s)
        if (s != W.slot && claim_cache[s] >= 0 && claim_cache[s] < groups) mate_claim[s] = claim_cache[s], mate_claim_round[s] = S.round;
    for (const auto& a : cambc::champions(team::ally)) {
        const auto id = handle_id(a);
        int s = 0;
        while (s < W.team_count && W.slot_ids[s] != id) ++s;
        if (s >= W.team_count || s >= MAX_SLOTS || s == W.slot) continue;
        const bool alive = a.is_alive();
        if (mate_alive[s] && !alive && mate_claim[s] >= 0 && S.round - mate_claim_round[s] <= 30)
            add_death_mark(W.groups[mate_claim[s]].spawns.front());
        mate_alive[s] = alive;
    }
}
// Fresh marks within 6 tiles of the group's spawns, each weighted 1 at the death down to 0 after DEATH_MARK_ROUNDS.
double death_mark_weight(const Group& g) {
    double w = 0;
    for (const auto& m : death_marks) {
        const int age = S.round - m.round;
        if (age >= DEATH_MARK_ROUNDS) continue;
        for (auto sp : g.spawns)
            if (dist(sp, m.pos) <= 6) { w += 1.0 - static_cast<double>(age) / DEATH_MARK_ROUNDS; break; }
    }
    return w;
}

int pick_group(int current) {
    const int round = S.round;
    if (blocked_until.empty()) blocked_until.assign(W.groups.size(), -1);
    std::uint64_t gd_fuel = 0;
    const auto pf0 = cambc::fuel_remaining();
    const bool fields_ready = travel_built >= static_cast<int>(W.groups.size()) && travel_built > 0;
    const distance_field f = fields_ready ? distance_field{} : from_me_field();
    const auto pf1 = cambc::fuel_remaining();
    const float dps = my_dps();
    // Fastest our damage can take a group down, for the bound: its health over our best damage per round.
    const double bound_dps = std::max({1.0, static_cast<double>(dps), static_cast<double>(my_spell_dps())});
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
        if (blocked_until[i] > round) continue;
        const int travel = fields_ready ? travel_fields[i]->get(S.me) : travel_to(f, g);
        if (travel == UNREACH) continue;
        // Before the first emblem gold is worth a gem: it buys the stats that win the next fights (top-10 teams take
        // 6.9 gold clusters and 7.0 small groups before round 300, we took 4.0 and 3.5).
        const double value = g.gems + g.gold * gold_weight(round);
        if (value <= 0) continue;
        const int side = W.group_side[i];
        const bool safe_speed = side <= 0 || round - enemy_seen_round > 30;
        // Small teams lose the early middle fights (b2: 3-4 champion maps); a full team pushes it only until an enemy
        // has killed this champion (the middle is contested: b3 3.5 deaths per lost game before r300).
        const bool mid_push = false;
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
        // Middle groups (side -6..6): a respawn wait counts once per round, so a champion with nothing better near
        // waits at a middle group about to come up (b9p: 1.21 of ours within 10 tiles when one comes up, rivals 1.37).
        const double wait_w = W.group_side[i] >= -6 && W.group_side[i] <= 6 ? 1.0 : safe_speed ? 4.0 : 2.0;
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
            // Fixed: 'mine' was the constant 16 * 16, which no claimant reaches, so this rule never ran. The claimant whose
            // passive adds most to the reward captures: Vesper +33% of the gold, Marcella +2 gold per gem she tributes;
            // then the champion whose damage grows most from shards.
            // The passive bonus is weighed against what the gold still adds: a shard's relative gain is about
            // growth / stat = 1 / (base/growth + shards), and base/growth is about 10 shards for most stats. Without this
            // the passive always won and every solo capture went to Vesper (cp3 on b56 at r400: Vesper 4.7 emblems, Heart
            // of Ruin and Vendetta 0.9 each; the rivals 2.5 and 1.6). A teammate out of view counts as wealthy as us.
            const int claim_mine_w = slot_wealth_now(W.slot);
            const auto claim_value = [&](int s) {
                using ct = cambc::champion_type;
                const auto t = W.slot_types[s];
                const double bonus = t == ct::vesper_vale ? 0.33 * g.gold : t == ct::marcella ? 2.0 * g.gems : 0.0;
                const int w = s == W.slot ? claim_mine_w : slot_wealth_now(s);
                const double gold = g.gold + bonus + 1.0;
                return gold / ((w >= 0 ? w : claim_mine_w) + 10.0) * (1.0 + 0.01 * capture_priority(t)) + s * 1e-6;
            };
            const double mine = W.slot < static_cast<int>(W.slot_types.size()) ? claim_value(W.slot) : 0.0;
            bool better_claim = false;
            for (int s = 0; s < MAX_SLOTS && s < static_cast<int>(W.slot_types.size()); ++s)
                if (s != W.slot && claim_cache[s] == i && claim_value(s) > mine) better_claim = true;
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
            if (g.state == 2) time += wait_w * std::max(0, g.respawn_round - round - travel);
            score = value / (time * n + 5 + g.bank_cost * 0.5 * bank_share(g));
            score_n = n;
        } else {
            const int home = W.spawn_field.get(g.spawns[0]);
            const ClearStats cs = clear_stats(g);
            // Only the champions already heading here clear it. Scoring with the whole team sent one champion to wake a
            // golem or elk alone while nothing brought the others (00crater, go1 on brkp to r300: 58.8 solo
            // strong-camp tank rounds per game against the rivals' 15.1, and 49% of our middle wakes taken by them).
            // Opening: before round 40 every champion scores as if alone, so the team stays on the group all five set out
            // for. On 00crater all five picked our top wolves at r1, then four left for the middle elk at r4-r7 once
            // teammates' claims cut the wolves' share, and the rivals' five, back from their own wolves, caught them on it.
            const int mates = round < 40 ? 0 : others;
            for (int n : {mates + 1}) {
                double time = travel * (safe_speed ? 1.0 : 0.7) + clear_time(cs, n, dps, S.max_hp, home == UNREACH ? 30 : home);
                if (g.state == 2) time += wait_w * std::max(0, g.respawn_round - round - travel);
                time += (n - mates - 1) * 4;  // Waiting for extra teammates.
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
            // Each recent death to an enemy (last 400 rounds) says they hold that ground: contested groups cost more.
            if (side > -3) score /= 1.0 + recent;
        }
        if (side > 0) score /= 1.0 + std::min(side, 20) / 20.0;
        // Take the middle first: in losses the enemy took 4.9 mid groups before round 300 (1.9 in our wins) and killed
        // us twice there; we farmed our own half. Contested groups are worth more to us before they are worth it to them.

        // Avoid walking into enemy groups; a lone enemy matters less than several.
        const auto gd0 = cambc::fuel_remaining();
        const double danger = sightings.empty() ? 0.0 : group_danger(g);
        gd_fuel += gd0 - cambc::fuel_remaining();
        if (danger > 0) score /= 1.0 + danger * 0.25;
        if (!death_marks.empty()) score /= 1.0 + 2.0 * death_mark_weight(g);
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
    if (best_i >= 0 && best_i != current && !pr_hz_mask.empty() && pr_hz_mask[best_i] != 0) {  // probe (HP)
        ++pr_hp_n;
        std::cout << "HP " << round << " " << W.slot << " " << best_i << " " << static_cast<int>(W.groups[best_i].strength_left()) << " "
                  << static_cast<int>(pr_hz_str(best_i)) << '\n';
    }
    return best_i;
}

// A defeated group nearby that nobody is capturing yet: one champion stays to capture it.
bool bank_gems() {
    if (stale()) return true;  // Stale turn: act no more.
    // While the altar guard lives, every tile in tribute range is blocked: a trip there only wastes rounds.
    // Unless the enemy is tributing: then a tile is free (b5 boss_battle: the enemy tributed 919 gems from round 800
    // while we, believing the unseen guard alive, carried 1072 and tributed none, and lost).
    static int enemy_sub = 0, enemy_rise = -1000;
    const int e_now = static_cast<int>(cambc::global_submitted_gems(team::enemy));
    if (e_now > enemy_sub) enemy_sub = e_now, enemy_rise = S.round;
    // Only the guard camps next to an altar block it: on boss_battle one of the two monoliths stands beside the altar,
    // and b6 dr3 carried 4295 gems to round 1953 with that one dead since r1350 (the other alive) and tributed none.
    // Blocked while every guard camp next to an altar lives (02guardians: one dead monolith opens its tile).
    bool guard_blocks = !W.altar_guards.empty();
    for (int gi : W.altar_guards) {
        const auto& g = W.groups[gi];
        for (size_t i = 0; i < g.spawns.size() && i < g.hp.size(); ++i)
            for (auto a : W.altars)
                if (dist(g.spawns[i], a) <= 1 && (g.state != 0 || g.hp[i] <= 0)) guard_blocks = false;
    }
    if (guard_blocks && S.round - enemy_rise > 100) return false;
    if (guard_blocks && S.round - pr_true_rise > 100) {  // probe (ER): let through only by a rise first noticed late
        ++pr_er_n;
        if (pr_er_last != S.round - 1)
            std::cout << "ER " << S.round << " " << W.slot << " " << enemy_rise << " " << pr_true_rise << " " << W.altar_field.get(S.me) << '\n';
        pr_er_last = S.round;
    }
    auto& me = cambc::self();
    for (auto altar : W.altars) {
        if (dist(S.me, altar) <= cambc::constants::submit_gems_range) {
            // An enemy altar lock makes submit_gems throw (altar_locked): break it with basic attacks first.
            // Platform boss_battle: 330-370 rounds of bank attempts per champion and zero tributes against locks.
            try {
                if (cambc::vision::has_altar_lock(altar)) {
                    const auto lock = cambc::vision::altar_lock_at(altar);
                    if (lock.is_enemy()) {
                        if (me.can_attack() && dist(S.me, lock.position()) <= S.range && !stale()) {
                            me.attack(lock);
                            return true;
                        }
                        if (me.can_move() && dist(S.me, lock.position()) > S.range) walk_towards(lock.position());
                        return true;
                    }
                }
            } catch (const cambc::error&) {
            }
            if (stale()) return true;
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
