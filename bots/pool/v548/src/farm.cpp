// Farming: which camp group to work on (task choice with shared commitments) and how to work it.
//
// Every champion scores camp groups by its share of the reward per round of its time, where the time
// includes travel, killing with the allies already committed (shared memory), capture and the healing
// cost of the damage taken. Groups that the committed team cannot kill safely need more helpers: only
// tank-type champions open those (they wait out of reach until enough helpers have arrived); others
// join groups a tank has opened. The opening is a whole-team kill of the best heavy group near spawn.
#include "bot.h"
#include "params.h"

std::vector<champion>& ally_handles();

namespace {

bool type_tank(champion_type t) {
    return t == champion_type::heart_of_ruin || t == champion_type::marcella || t == champion_type::ryth || t == champion_type::varg;
}

// Damage per round against camps: basic attacks plus focus abilities and attack resets, amortised.
float type_camp_dps(champion_type t, float str, float foc) {
    switch (t) {
    case champion_type::ryth: return str * 1.125f + foc * 1.0f / 8.f;
    case champion_type::vesper_vale:
    case champion_type::vendetta:
    case champion_type::issac:
    case champion_type::varg:
    case champion_type::willow: return str * 1.125f;
    case champion_type::marcella: return str * 1.125f + 2.f * foc / 8.f;
    case champion_type::cassi:
    case champion_type::stellar: return str + 2.f * foc / 8.f;
    case champion_type::prism: return str + 1.5f * foc / 8.f;
    case champion_type::tavi: return str + 1.6f * foc / 8.f;
    case champion_type::heart_of_ruin: return str + 1.5f * foc / 8.f;
    case champion_type::ren: return str;
    }
    return str;
}

}  // namespace

bool Bot::tank_type(int a) const { return type_tank(ainfo[static_cast<std::size_t>(a)].type); }

bool Bot::has_emblem(item_family f) const {
    // Cached per round (the plan has ~60 steps and this ran per camp group in choose_task: 2.5k fuel a group).
    if (emb_round != round) {
        emb_round = round;
        emb_mask = 0;
        std::array<int, 16> cnt{};
        for (std::size_t k = 0; k < plan.size() && k < bought.size(); ++k) {
            const int fi = static_cast<int>(plan[k].fam);
            if (fi >= 0 && fi < 16) cnt[static_cast<std::size_t>(fi)] += bought[k];
        }
        for (int fi = 0; fi < 16; ++fi)
            if (cnt[static_cast<std::size_t>(fi)] >= 5) emb_mask |= 1u << fi;
    }
    const int fi = static_cast<int>(f);
    return fi >= 0 && fi < 16 && ((emb_mask >> fi) & 1u);
}

float Bot::camp_dps_of(int a) const {
    const auto& i = ainfo[static_cast<std::size_t>(a)];
    float d = std::max(10.f, type_camp_dps(i.type, i.str, i.foc));
    if (a == idx && has_emblem(item_family::monster)) d *= 1.15f;
    return d;
}

// Damage taken from camps relative to base (Jungle emblem: -30%); allies' items are unknown.
float Bot::camp_taken_mult(int a) const {
    return (a == idx && has_emblem(item_family::jungle)) ? 0.7f : 1.f;
}

float Bot::shield_per_round(int a) const {
    const auto& i = ainfo[static_cast<std::size_t>(a)];
    if (i.type == champion_type::heart_of_ruin) return 1.5f * i.foc / 8.f;
    if (i.type == champion_type::varg) return 2.5f * i.foc / 8.f;
    return 0.f;
}

// Heals a Willow working the same group puts into the tank each round (3x focus every 8 rounds, not all on the tank).
float Bot::heal_for(int gid, bool me_in) const {
    if (!P_HEAL_SUSTAIN) return 0.f;
    float h = 0;
    for (int a = 0; a < n_allies; ++a) {
        const auto& i = ainfo[static_cast<std::size_t>(a)];
        if (i.type != champion_type::willow) continue;
        if (a == idx ? me_in : (comms.task_of(a) == gid && alive_free(a))) h = std::max(h, 3.f * i.foc / 8.f);
    }
    return h * P_HEAL_EFF;
}

float Bot::max_hp_of(int a) const { return std::max(1.f, ainfo[static_cast<std::size_t>(a)].max_hp); }

float Bot::hp_of(int a) const {
    if (a == idx) return self().health();
    const auto& i = ainfo[static_cast<std::size_t>(a)];
    if (round - i.seen_round > 25) return i.max_hp;  // probably healed since
    return i.hp;
}

// Alive and able to help (not dead, healing or fighting champions).
bool Bot::alive_free(int a) const {
    const int c = comms.code_of(a);
    return c != slot::kDead && c != slot::kHome && c != slot::kFight && c != slot::kRetreat;
}

int Bot::choose_opening() {
    World& W = world();
    float dps = 0, spare = 0, shield = 0;
    for (int a = 0; a < n_allies; ++a) {
        dps += camp_dps_of(a);
        spare += max_hp_of(a) * (1.f - P_TANK_FLOOR);
        shield += shield_per_round(a);
        if (P_HEAL_SUSTAIN && ainfo[static_cast<std::size_t>(a)].type == champion_type::willow) shield += P_HEAL_EFF * 3.f * ainfo[static_cast<std::size_t>(a)].foc / 8.f;
    }
    float best = 0;
    int bi = -1;
    for (const auto& g : W.groups) {
        if (!g.reachable || g.dps <= 0 || g.spawn_dist > P_OPEN_MAX_DIST) continue;
        const float T = g.total_max_hp / std::max(1.f, dps);
        if ((P_SEQ_DMG ? g.fight_damage(dps, true) : g.dps * T) > spare * P_OPEN_SAFE + shield * T) continue;
        const float value = static_cast<float>(g.gems) * P_GEM_W + static_cast<float>(g.gold);
        const float s = value / (static_cast<float>(g.spawn_dist) + T + 5.f);
        if (s > best) { best = s; bi = g.id; }
    }
    return bi;
}

bool Bot::is_gate_group(int gid) const {
    const World& W = world();
    if (W.gated)
        for (const auto& gt : W.gates)
            if (gt.group == gid) return true;
    // Monoliths (every map): 200-470 gems a capture, taken by the whole team over several trips.
    if (P_MONO_SIEGE && gid >= 0 && gid < static_cast<int>(W.groups.size())) {
        const Group& g = W.groups[static_cast<std::size_t>(gid)];
        if (g.monolith && g.gems > 0) return true;
    }
    // Heavy maps: sieges on the heavy gem groups too.
    if (W.heavy_map && gid >= 0 && gid < static_cast<int>(W.groups.size())) {
        const Group& g = W.groups[static_cast<std::size_t>(gid)];
        if ((g.dps > 150.f || g.monolith) && g.gems > 0) return true;
    }
    return false;
}

// Lowest-index champion still alive (by the shared slots) leads team rallies.
bool Bot::leader() const {
    for (int a = 0; a < n_allies; ++a) {
        if (a == idx) return true;
        if (comms.code_of(a) != slot::kDead) return false;
    }
    return true;
}

// Best heavy group and squad size for a rally, if its value per champion-round (the squad's travel,
// waiting and fighting counted) beats normal farming. Returns the group id, sets k.
int Bot::choose_rally(int& kbest) {
    World& W = world();
    const float gold_w = round < 300 ? P_GOLD_W_EARLY : round < 700 ? 0.5f * (P_GOLD_W_EARLY + P_GOLD_W_LATE) : P_GOLD_W_LATE;
    std::array<vec2, 5> where{};
    std::array<bool, 5> home{}, alive{};
    int n_alive = 0;
    for (int a = 0; a < n_allies; ++a) {
        const int code = comms.code_of(a);
        if (a != idx && code == slot::kDead) continue;
        alive[static_cast<std::size_t>(a)] = true;
        ++n_alive;
        const auto& ai = ainfo[static_cast<std::size_t>(a)];
        const int t = comms.task_of(a);
        if (a == idx || round - ai.seen_round <= 8) where[static_cast<std::size_t>(a)] = ai.pos;
        else if (t >= 0 && t < static_cast<int>(W.groups.size())) where[static_cast<std::size_t>(a)] = W.groups[static_cast<std::size_t>(t)].center;
        else home[static_cast<std::size_t>(a)] = true;
    }
    if (n_alive < 3) return -1;
    float best = P_RALLY_RATE;
    int bi = -1;
    kbest = n_allies;
    for (auto& g : W.groups) {
        if (!g.reachable || g.island != 0 || g.dps < P_RALLY_MIN_DPS || g.monolith || g.id >= 62) continue;
        if (P_RALLY_BIG_ONLY && !g.big) continue;
        if (blacklist[static_cast<std::size_t>(g.id)] > round) continue;
        if (g.side < -P_SIDE_MARGIN) continue;  // deep in their half
        if (g.state == GState::Reward) continue;
        const float value = static_cast<float>(g.gems) * P_GEM_W + static_cast<float>(g.gold) * gold_w;
        const float hp = g.state == GState::Alive ? g.hp_left() : g.total_max_hp;
        for (int k = 3; k <= n_allies; ++k) {
            float dps = 0, spare = 0, shield = 0, travel = 0, wait = 0;
            int dmax = 0, dmin = 1 << 20, members = 0;
            bool missing = false;
            for (int a = 0; a < n_allies; ++a) {
                if (!Comms::rally_member(a, k, n_allies)) continue;
                const auto sa = static_cast<std::size_t>(a);
                if (!alive[sa]) { missing = true; break; }
                dps += camp_dps_of(a);
                spare += max_hp_of(a) * (1.f - P_TANK_FLOOR);  // hurt members heal first (muster)
                shield = std::max(shield, shield_per_round(a));
                int d = home[sa] ? g.spawn_dist + 3 : W.dist_to_group(g, where[sa]);
                if (d >= (1 << 20)) d = g.spawn_dist + 10;
                // Hurt members heal at spawn first (muster): recall, then the whole walk.
                if (!home[sa] && hp_of(a) < 0.6f * max_hp_of(a)) d = g.spawn_dist + 8;
                travel += static_cast<float>(d);
                dmax = std::max(dmax, d);
                dmin = std::min(dmin, d);
                if (g.state == GState::Respawning) wait += static_cast<float>(std::max(0, g.respawn_round - round - d));
                ++members;
            }
            if (missing || members < 3 || dps <= 0) continue;
            if (dmax > P_RALLY_DMAX) break;  // farther with more members
            if (dmax - dmin > P_RALLY_SPREAD) continue;  // early arrivals would idle too long
            if (g.state == GState::Respawning && g.respawn_round - round - dmax > 12) break;  // too early to call
            const float T = hp / dps;
            const float dmg = P_SEQ_DMG ? g.fight_damage(dps, g.state != GState::Alive) : g.dps * T;
            if (dmg > spare * 0.8f + shield * T) continue;  // too heavy for this squad
            const float gather = static_cast<float>(members) * static_cast<float>(dmax) - travel;
            const float cost = travel + wait + P_RALLY_GATHER_W * gather + static_cast<float>(members) * (T + 6.f);
            const float rate = value / std::max(1.f, cost);
            LOG("    rally cand g%d k=%d travel=%.0f dmax=%d wait=%.0f T=%.0f dmg=%.0f spare=%.0f rate=%.2f\n", g.id, k, travel, dmax, wait, T, dmg, spare, rate);
            if (rate > best) { best = rate; bi = g.id; kbest = k; }
            break;  // the smallest feasible squad
        }
    }
    return bi;
}

// Rally bookkeeping (every turn): the leader calls and times out rallies; anyone ends one on capture.
void Bot::update_rally() {
    World& W = world();
    int r = comms.rally();
    if (r >= static_cast<int>(W.groups.size())) r = -1;
    if (r != rally_seen) { rally_seen = r; rally_since = round; siege_hp0 = -1; }
    if (r >= 0) {
        const Group& g = W.groups[static_cast<std::size_t>(r)];
        // Captured since the rally was called (respawn timers start at the capture).
        const bool captured = g.state == GState::Respawning && g.respawn_round - g.respawn >= rally_since - 2;
        if (captured) { comms.set_rally(-1); rally_seen = -1; return; }
        if (leader() && round - rally_since > (is_gate_group(r) ? P_SIEGE_MAX : P_RALLY_MAX)) {
            blacklist[static_cast<std::size_t>(r)] = round + 120;
            rally_pause_until = round + 60;  // the squad did not come together: farm normally for a while
            comms.set_rally(-1);
            rally_seen = -1;
            return;
        }
        // A siege that is getting us killed or going nowhere (cramped approach, too strong for us): drop it for long.
        if (leader() && is_gate_group(r)) {
            int dead = 0;
            for (int a = 0; a < n_allies; ++a)
                if (comms.code_of(a) == slot::kDead) ++dead;
            if (siege_hp0 < 0) siege_hp0 = g.hp_left();
            const bool stalled = round - rally_since >= P_SIEGE_CHECK && g.hp_left() > 0.7f * siege_hp0;
            if ((dead >= P_SIEGE_DEATHS || stalled) && !W.gated) {
                siege_hp0 = -1;
                blacklist[static_cast<std::size_t>(r)] = round + 500;
                rally_pause_until = round + 150;
                comms.set_rally(-1);
                rally_seen = -1;
            }
        }
        return;
    }
    // Gated altar: the whole team breaks the gate camp (over several trips; camps never regenerate).
    bool mono_map = false;
    if (P_MONO_SIEGE && !W.gated && !W.heavy_map)
        for (const auto& g : W.groups)
            if (g.monolith && g.gems > 0 && g.reachable && g.island == 0 && g.side >= -P_SIDE_MARGIN) { mono_map = true; break; }
    const bool siege_ok = (W.gated || W.heavy_map) ? (round >= P_SIEGE_FROM && (self().max_health() >= P_SIEGE_HP || round >= P_SIEGE_LATE))
                                                   : (mono_map && round >= P_MONO_FROM && (self().max_health() >= P_MONO_HP || round >= P_SIEGE_LATE));
    if ((W.gated || W.heavy_map || mono_map) && leader() && siege_ok && round >= rally_pause_until && (round + idx + P_SALT + (P_SALT >= 4 ? round / (37 + P_SALT) : 0)) % 4 == 0) {
        int gate_g = -1, best_d = 1 << 30;
        for (const auto& g : W.groups) {
            if (g.id >= 62 || !is_gate_group(g.id) || !g.reachable || g.island != 0) continue;
            if (g.state != GState::Alive || blacklist[static_cast<std::size_t>(g.id)] > round) continue;
            if (!W.gated && g.side < -P_SIDE_MARGIN) continue;  // not deep in their half
            // Nearest to us, the richest first among equals.
            const int score = g.spawn_dist * 10 - std::min(g.gems, 400) / 10;
            if (score < best_d) { best_d = score; gate_g = g.id; }
        }
        if (gate_g >= 0) {
            LOG("[r%d] SIEGE call g%d\n", round, gate_g);
            comms.set_rally(gate_g, n_allies);
            rally_seen = gate_g;
            rally_since = round;
            return;
        }
    }
    if (!P_RALLY || round < P_RALLY_FROM || round < rally_pause_until || !opening_done || !leader() || (round + idx + P_SALT + (P_SALT >= 4 ? round / (37 + P_SALT) : 0)) % 4 != 0) return;
    if (fuel() < 40000) return;
    int k = n_allies;
    const int c = choose_rally(k);
    if (c >= 0) {
        LOG("[r%d] RALLY call g%d k=%d\n", round, c, k);
        comms.set_rally(c, k);
        rally_seen = c;
        rally_since = round;
    }
}

int Bot::choose_task() {
    World& W = world();
    auto& me = self();
    const vec2 p = me.position();
    const float gold_w = round < 300 ? P_GOLD_W_EARLY : round < 700 ? 0.5f * (P_GOLD_W_EARLY + P_GOLD_W_LATE) : P_GOLD_W_LATE;
    const float my_hp = me.health(), my_mhp = me.max_health();
    const float my_spare = std::max(0.f, my_hp - P_TANK_FLOOR * my_mhp);
    const bool on_mainland = W.on_main(p);
    const bool at_spawn_now = bb_test(*W.my_spawn, p);

    // Helpers that could still come to a heavy group: alive, not busy with damaging groups.
    int n_free = 0;
    float free_dps = 0, free_spare = 0;
    for (int a = 0; a < n_allies; ++a) {
        if (a == idx || !alive_free(a)) continue;
        const int t = comms.task_of(a);
        if (t >= 0 && t < static_cast<int>(W.groups.size()) && W.groups[static_cast<std::size_t>(t)].dps > 0) continue;
        ++n_free;
        free_dps += camp_dps_of(a);
        free_spare += max_hp_of(a) * (1.f - P_TANK_FLOOR);
    }
    const float avg_dps = n_free ? free_dps / static_cast<float>(n_free) : 0.f;
    const float avg_spare = n_free ? free_spare / static_cast<float>(n_free) : 0.f;
    // Committed allies per group (one pass over the slots).
    std::array<int, 5> atask{};
    std::array<float, 5> adps{}, aspare{};
    for (int a = 0; a < n_allies; ++a) {
        atask[static_cast<std::size_t>(a)] = (a == idx || !alive_free(a)) ? -1 : comms.task_of(a);
        if (P_SUP_FIX && P_SUPPORT && round >= P_SUPPORT_FROM && ainfo[static_cast<std::size_t>(a)].type == champion_type::willow) atask[static_cast<std::size_t>(a)] = -1;
        if (atask[static_cast<std::size_t>(a)] < 0) continue;
        adps[static_cast<std::size_t>(a)] = camp_dps_of(a);
        aspare[static_cast<std::size_t>(a)] = std::max(0.f, hp_of(a) - P_TANK_FLOOR * max_hp_of(a));
    }
    const float my_dps = camp_dps_of(idx);
    const bool i_tank = tank_type(idx);

    float best = 0, cur = 0;
    int bi = -1;
    bool best_chip = false;
    float fb_best = 0;
    int fb_id = -1;
    const bool crystal = has_crystal();
    const int ct_n = static_cast<int>(W.groups.size());
    const int ct_start = ct_n > 0 ? (round * 7 + idx * 13) % ct_n : 0;
    for (int ct_i = -1; ct_i < ct_n; ++ct_i) {
        int ct_g;
        if (ct_i < 0) {
            if (task < 0 || task >= ct_n) continue;
            ct_g = task;  // the current task first (switch hysteresis needs its score)
        } else {
            ct_g = (ct_start + ct_i) % ct_n;
            if (ct_g == task) continue;
            if (fuel() < P_CT_FUEL) break;  // out of fuel soon: best so far
        }
        auto& g = W.groups[static_cast<std::size_t>(ct_g)];
        if (!g.reachable && g.island != 1) continue;
        if (blacklist[static_cast<std::size_t>(g.id)] > round) continue;
        int d = W.dist_to_group(g, p);
        if (d >= (1 << 20) && g.island == 1 && on_mainland) {
            // Reach the island by teleport crystal (fetch one from spawn first if needed).
            d = W.island_dist(g, p);
            if (!crystal) d += me.gold_count() >= 10 ? (at_spawn_now ? 0 : std::min(W.spawn_dist_at(p), 12) + 2) : 1 << 20;
        }
        if (d >= (1 << 20)) continue;
        float wait = 0, hp_left = 0, D = 0;
        bool fresh = false;
        if (g.state == GState::Respawning) {
            wait = static_cast<float>(std::max(0, g.respawn_round - round - d));  // idle rounds after arrival
            if (wait > P_MAX_WAIT) {
                // Nothing else to do: wait at the group that respawns soonest (worth most per round of waiting).
                if (P_PREWAIT && g.side >= -P_SIDE_MARGIN) {
                    float v = static_cast<float>(g.gems) * P_GEM_W + static_cast<float>(g.gold) * gold_w;
                    int taken = 0;
                    for (int a = 0; a < n_allies; ++a)
                        if (atask[static_cast<std::size_t>(a)] == g.id) ++taken;
                    if (taken == 0 && v > 0) {
                        const float fs = v / (static_cast<float>(d) + wait + 10.f);
                        if (fs > fb_best) { fb_best = fs; fb_id = g.id; }
                    }
                }
                continue;
            }
            hp_left = g.total_max_hp;
            D = g.dps;
            fresh = true;
        } else if (g.state == GState::Alive) {
            hp_left = g.hp_left();
            D = g.live_dps();
        }
        float value = static_cast<float>(g.gems) * P_GEM_W + static_cast<float>(g.gold) * gold_w;
        // Marcella earns 2 gold per gem she tributes: gem groups are worth more when she captures them.
        if (ctype == champion_type::marcella) value += P_MAR_ROUTE * 2.f * static_cast<float>(g.gems) * gold_w;
        if (value <= 0) continue;
        if (g.side < -P_SIDE_MARGIN) value *= P_ENEMY_SIDE_W;  // their half: farmed and guarded by them
        if (P_DANGER_W < 1.f) {
            // Enemy champions seen around it lately: they fight for it (and pick off whoever comes alone).
            int seen = 0;
            for (const auto& x : sightings)
                if (round - x.round <= 20 && cheb(x.pos, g.center) <= g.radius + 5) ++seen;
            for (const auto& e : enemies)
                if (cheb(e.pos, g.center) <= g.radius + 5) ++seen;
            if (seen > 0) value *= P_DANGER_W;
        }
        // Upper bound (alone, instant kill): skip groups that cannot beat the best so far.
        if (value * P_ENABLE / (static_cast<float>(d) + 1.5f * wait + 3.f) <= best) continue;
        // Allies committed to this group.
        int nc = 0, tank = idx;
        bool tank_in = i_tank;
        float team_dps = my_dps, team_spare = my_spare;
        for (int a = 0; a < n_allies; ++a) {
            if (atask[static_cast<std::size_t>(a)] != g.id) continue;
            ++nc;
            team_dps += adps[static_cast<std::size_t>(a)];
            team_spare += aspare[static_cast<std::size_t>(a)];
            tank = std::min(tank, a);
            if (tank_type(a)) tank_in = true;
        }
        if (g.state == GState::Reward) {
            if (nc > 0) continue;  // an ally captures it
            const float s = value / (static_cast<float>(d) + 6.f);
            if (g.id == task) cur = s;
            if (s > best) { best = s; bi = g.id; }
            continue;
        }
        const float tmult = camp_taken_mult(tank);
        D *= tmult;
        float T = hp_left / team_dps;
        const float heal_g = heal_for(g.id, true);
        float shield = (shield_per_round(tank) + heal_g) * T;
        float dmg = P_SEQ_DMG ? g.fight_damage(team_dps, fresh) * tmult : D * T;
        int extra = 0;
        bool enabler = false;  // my joining makes a heavy group feasible (or starts it)
        // Solo over several trips: camps never regenerate, so damage dealt before a healing trip stays.
        float s_chip = 0;
        // Golems too (not monoliths): a long-term sink for spare health, chipped by whoever has some (shared).
        const bool big_chip = P_CHIP_BIG && g.big && !g.monolith && g.side >= -P_SIDE_MARGIN;
        if (P_CHIP && D > 0 && (nc == 0 || big_chip) && (!g.big || big_chip) && dmg > team_spare * 0.85f + shield) {
            const float cdps = big_chip ? team_dps : my_dps;
            const float Ts = hp_left / cdps;
            const float Dm = D;  // nobody committed: I am the tank
            const float dmg_all = std::max(0.f, (P_SEQ_DMG ? g.fight_damage(cdps, fresh) * camp_taken_mult(idx) : Dm * Ts) - shield_per_round(idx) * Ts);
            const float dmg_s = big_chip ? dmg_all / static_cast<float>(nc + 1) : dmg_all;  // my share when several chip it
            // Each trip ends with enough health to walk out of the camps' reach (they keep hitting).
            const float keep = big_chip ? std::max(P_CHIP_FLOOR * my_mhp, 1.2f * D * camp_taken_mult(idx) * static_cast<float>(g.max_range + 1)) : P_CHIP_FLOOR * my_mhp;
            const float per_trip = my_mhp - keep;
            if (per_trip > 0.f) {
                const float trips = std::max(0.f, dmg_s - std::max(0.f, my_hp - keep)) / std::max(1.f, per_trip);
                const float trip_cost = P_CHIP_TRIP_W * static_cast<float>(g.spawn_dist) + 8.f;  // recall, heal, walk back
                if (trips <= (big_chip ? P_CHIP_BIG_TRIPS : P_CHIP_MAX_TRIPS) && my_hp >= P_CHIP_START * my_mhp && my_hp > keep + 2.f * D) {
                    const float Tc = static_cast<float>(d) + 1.5f * wait + Ts + 5.f + trips * trip_cost + P_HP_COST * std::min(dmg_s, my_spare);
                    s_chip = value / static_cast<float>(big_chip ? nc + 1 : 1) / std::max(1.f, Tc);
                }
            }
        }
        if (D > 0) {
            // Could the committed allies do it without me?
            const float o_dps = team_dps - my_dps, o_spare = team_spare - my_spare;
            const float oT = o_dps > 1.f ? hp_left / o_dps : 1e9f;
            const bool others_ok = nc > 0 && (P_SEQ_DMG ? g.fight_damage(o_dps, fresh) * tmult : D * oT) <= o_spare * 0.85f + (shield_per_round(tank) + heal_for(g.id, false)) * oT;
            if (dmg > team_spare * 0.85f + shield) {
                // Needs more helpers than are committed now.
                float tdps = team_dps, tsp = team_spare;
                bool ok = false;
                const int max_extra = P_EXTRA_FIX ? n_free : std::max(0, n_free - nc);  // n_free already excludes allies on damaging groups
                while (extra < max_extra) {
                    ++extra;
                    tdps += avg_dps;
                    tsp += avg_spare;
                    T = hp_left / tdps;
                    dmg = P_SEQ_DMG ? g.fight_damage(tdps, fresh) * tmult : D * T;
                    shield = (shield_per_round(tank) + heal_g) * T;
                    if (dmg <= tsp * 0.85f + shield) { ok = true; break; }
                }
                if (!ok || !tank_in) {  // only tanks open heavy groups; others join a tank's
                    if (s_chip > 0) {
                        if (g.id == task) cur = s_chip;
                        if (s_chip > best) { best = s_chip; bi = g.id; best_chip = true; }
                    }
                    continue;
                }
                enabler = true;
            } else if (!others_ok && nc > 0) {
                enabler = true;
            }
        }
        if (D <= 0 && nc > 0) {
            // Harmless group already taken: join only if they need longer than my trip.
            const float others = std::max(1.f, team_dps - my_dps);
            if (hp_left / others < static_cast<float>(d) + 3.f) continue;
        }
        const float n_team = static_cast<float>(nc + 1 + extra);
        const float gather = extra > 0 ? 6.f + 3.f * static_cast<float>(extra) : 0.f;
        const float Ttot = static_cast<float>(d) + 1.5f * wait + T + gather + 5.f / n_team + P_HP_COST * dmg / n_team;
        const float s = value * (enabler ? P_ENABLE : 1.f) / n_team / std::max(1.f, Ttot);
#if BOT_LOG
        if (s > best * 0.5f) LOG("    cand g%d st=%d d=%d wait=%.0f nc=%d extra=%d T=%.0f dmg=%.0f val=%.0f s=%.2f\n", g.id, (int)g.state, d, wait, nc, extra, T, dmg, value, s);
#endif
        const bool use_chip = s_chip > s;
        const float sc = use_chip ? s_chip : s;
        if (g.id == task) cur = sc;
        if (sc > best) { best = sc; bi = g.id; best_chip = use_chip; }
    }
    if (bi < 0 && fb_id >= 0) bi = fb_id;  // pre-position instead of idling
    LOG("    choose: best g%d %.2f cur %.2f (task %d) n_free=%d chip=%d\n", bi, best, cur, task, n_free, (int)best_chip);
    if (task >= 0 && cur > 0 && bi != task && best < cur * P_SWITCH) return task;
    chip_task = best_chip ? bi : -1;
    return bi;
}

// Wait near the group without attacking (camps only wake when their group is attacked).
bool Bot::stage_at(Group& g) {
    World& W = world();
    const vec2 p = self().position();
    bitboard goals;
    goals.clear();
    if (g.field) {
        // Walking distance 2..3 from the group (Chebyshev rings can sit behind walls).
        bitboard box;
        box.clear();
        for (const auto& c : g.camps) box.draw_chebyshev(c.pos, 3.f);
        box &= ~*W.blocked;
        box &= ~*W.camp_tiles;
        bitboard near1;
        near1.clear();
        for (vec2 q : box.positions()) {
            const int d = df_get(*g.field, q);
            if (d >= 2 && d <= 3) goals.set(q);
            else if (d == 1) near1.set(q);
        }
        if (goals.is_empty()) goals = near1;  // cramped (walled pockets): wait right next to it
    }
    if (goals.is_empty()) {
        bitboard inner;
        inner.clear();
        for (const auto& c : g.camps) {
            goals.draw_chebyshev(c.pos, 3.f);
            inner.draw_chebyshev(c.pos, 1.f);
        }
        goals &= ~inner;
        goals &= ~*W.blocked;
        goals &= ~*W.camp_tiles;
    }
    // Never wait on a camp tile: camps cannot respawn while their tile is occupied.
    if (bb_test(*W.camp_tiles, p)) {
        for (auto d : kDirs) {
            const vec2 q = p + d;
            if (nav.passable(q) && !bb_test(*W.camp_tiles, q)) {
                try { if (self().move_absolute(q)) { moved_this_turn = true; nav.begin_turn(); return true; } } catch (...) {}
            }
        }
    }
    if (goals.is_empty() || bb_test(goals, p)) return false;
    return move_to(goals, g.field.get(), true, g.center);
}

// Gold a champion's passive adds to this group's capture: Vesper +33% gold, Marcella +2 gold per gem tributed.
static float capture_bonus(champion_type t, const Group& g) {
    if (P_CAPTURE_MODE == 0) {
        if (t == champion_type::vesper_vale) return 0.33f * static_cast<float>(g.gold);
        if (t == champion_type::marcella) return 2.f * static_cast<float>(g.gems);
        return 0.f;
    }
    // Reward gold as the team values it: passives (Vesper +33%, Marcella +2 per tributed gem) times how much
    // camp damage that champion buys per gold (Vendetta's strength scales best).
    float gold = static_cast<float>(g.gold), eff = 0.6f;
    switch (t) {
    case champion_type::vendetta: eff = 1.f; break;
    case champion_type::vesper_vale: gold *= 1.33f; eff = 0.85f; break;
    case champion_type::marcella: gold += 2.f * static_cast<float>(g.gems); eff = P_MAR_EFF; break;
    case champion_type::heart_of_ruin: eff = 0.45f; break;
    default: break;
    }
    return gold * eff;
}

bool Bot::capture(Group& g) {
    World& W = world();
    auto& me = self();
    const vec2 p = me.position();
    if (bb_test(*g.tiles, p)) {
        // Several of us on its tiles split the reward and all stand idle: only the best capturer stays.
        if (P_SINGLE_CAPTURE && g.state == GState::Reward) {
            const bool me_hurt = me.health() < 0.45f * me.max_health();
            const float mine = capture_bonus(ctype, g) + (me_hurt ? 1000.f : 0.f);
            for (const auto& a : allies) {
                if (!bb_test(*g.tiles, a.pos)) continue;
                const float ab = capture_bonus(ainfo[static_cast<std::size_t>(a.index)].type, g) + (a.hp < 0.45f * a.max_hp ? 1000.f : 0.f);
                if (ab > mine || (ab == mine && a.index < idx)) {
                    task = -1;
                    act = "yield_capture";
                    for (auto d : kDirs) {
                        const vec2 q = p + d;
                        if (nav.passable(q) && !bb_test(*g.tiles, q)) {
                            try { if (me.move_absolute(q)) { moved_this_turn = true; nav.begin_turn(); } } catch (...) {}
                            break;
                        }
                    }
                    return false;
                }
            }
        }
        act = "capture";
        // Going home soon anyway (hurt or gold to spend): recall now, the capture completes during the channel.
        const bool want_home = me.health() < P_CAP_RECALL_HP * me.max_health() || me.gold_count() >= P_CAP_RECALL_GOLD || !W.on_main(p);
        if (P_CAP_RECALL && want_home && on_tile_since >= 0 && round - on_tile_since >= 1 && enemies.empty()) {
            try { me.recall(); act = "capture+recall"; } catch (...) {}
        }
        return true;
    }
    if (P_SINGLE_CAPTURE) {
        // One capturer: whoever already stands on it, else a hurt champion (it recalls while capturing),
        // else the best capture bonus among those present.
        const bool me_hurt = me.health() < 0.45f * me.max_health();
        const float mine = capture_bonus(ctype, g) + (me_hurt ? 1000.f : 0.f);
        // Leaving it to an ally: do not pick it again while they take it.
        auto leave = [&]() {
            if (P_LEAVE_BL > 0) blacklist[static_cast<std::size_t>(g.id)] = std::max(blacklist[static_cast<std::size_t>(g.id)], round + P_LEAVE_BL);
            task = -1;
            return false;
        };
        for (const auto& a : allies) {
            if (bb_test(*g.tiles, a.pos)) return leave();
            // Marcella on her way to it takes gem captures (her tribute passive): leave it to her.
            if (P_MAR_ROUTE > 0.f && ctype != champion_type::marcella && g.gems >= 10 && ainfo[static_cast<std::size_t>(a.index)].type == champion_type::marcella &&
                comms.task_of(a.index) == g.id && cheb(a.pos, g.center) <= g.radius + 8 && !me_hurt) return leave();
            if (cheb(a.pos, g.center) > g.radius + 3) continue;
            // Only an ally that is going to take it: one walking home to heal or running from a fight is not
            // (a hurt tank leaving a dead golem made everyone else yield to it and nobody captured).
            if (P_CAP_FIX && comms.task_of(a.index) != g.id) continue;
            const float ab = capture_bonus(ainfo[static_cast<std::size_t>(a.index)].type, g) + (a.hp < 0.45f * a.max_hp ? 1000.f : 0.f);
            if (ab > mine || (ab == mine && a.index < idx && comms.task_of(a.index) == g.id)) return leave();
        }
    }
    bitboard goals = *g.tiles;
    goals &= ~nav.occupied();
    if (goals.is_empty()) {
        goals.clear();
        for (const auto& c : g.camps) goals.draw_chebyshev(c.pos, 1.f);
        goals &= ~*W.blocked;
    }
    act = "to_capture";
    return move_to(goals, g.field.get(), true, g.center);
}

// Heart of Ruin's landing (dash 2, 1.5 x Focus in radius 1) on the camps of the group whenever it is ready (horland.py).
void Bot::hor_land_on_group(Group& g, int tank, vec2 tank_pos) {
    if (cast_this_turn || moved_this_turn || round < land_check_round) return;
    const int ds = ability_slot(ability_kind::dash);
    if (ds < 0 || amod[static_cast<std::size_t>(ds)] <= 0) return;  // a landing that deals damage
    auto& me = self();
    auto abs = me.abilities();
    try {
        const int cd = abs[static_cast<std::size_t>(ds)].cooldown();
        if (cd > 0) { land_check_round = round + cd; return; }  // cast elsewhere (fights): look again when it is ready
    } catch (...) { return; }
    const bool i_tank = tank == idx;
    bool damaging = false;
    for (const auto& c : g.camps)
        if (c.hp > 0 && camp_str(c.type) > 0) damaging = true;
    if (i_tank && damaging) {
        // A tank about to face damaging camps shields first (try_cast_on_camp), then lands.
        const int sh = ability_slot(ability_kind::shield);
        if (sh >= 0) {
            try { if (abs[static_cast<std::size_t>(sh)].cooldown() == 0) return; } catch (...) {}
        }
    }
    const vec2 p = me.position();
    vec2 bq = p;
    int bs = 0, bd = 99;
    for (int dx = -2; dx <= 2; ++dx)
        for (int dy = -2; dy <= 2; ++dy) {
            const vec2 q{ p.x + dx, p.y + dy };
            if (q == p || !in_bounds(q) || !nav.passable(q)) continue;
            int hit = 0;
            bool unsafe = false;
            for (const auto& c : g.camps) {
                if (c.hp <= 0) continue;
                const int d = cheb(q, c.pos);
                if (d <= 1) ++hit;
                if (!i_tank && camp_str(c.type) > 0) {
                    const int td = cheb(tank_pos, c.pos);
                    if (d < td || (d == td && idx < tank)) unsafe = true;
                }
            }
            if (unsafe || hit == 0) continue;
            const int dd = cheb(q, p);
            if (hit > bs || (hit == bs && dd < bd)) { bs = hit; bd = dd; bq = q; }
        }
    if (bs == 0) return;
    try {
        if (abs[static_cast<std::size_t>(ds)].use(bq)) { cast_this_turn = true; nav.begin_turn(); land_check_round = round + 8; }
    } catch (...) {}
}

bool Bot::attack_camps(Group& g, int tank, vec2 tank_pos) {
    auto& me = self();
    World& W = world();
    if (P_HOR_LAND_ANY) hor_land_on_group(g, tank, tank_pos);
    const vec2 p = me.position();
    const int range = me.attack_range();
    const bitboard* vis = W.vis ? &*W.vis : nullptr;
    const bool i_tank = tank == idx;
    act = i_tank ? "tank" : "attack";
    const Camp* best = nullptr;
    for (const auto& c : g.camps) {
        if (c.hp <= 0 || cheb(p, c.pos) > range || (vis && !bb_test(*vis, c.pos))) continue;
        if (!best) { best = &c; continue; }
        const bool cd = camp_str(c.type) > 0, bd = camp_str(best->type) > 0;
        if (cd != bd ? cd : c.hp < best->hp) best = &c;
    }
    if (best && me.can_attack()) {
        bool ok = false;
        try {
            const camp cc = vision::camp_at(best->pos);
            try_cast_on_camp(cc, i_tank);
            me.attack(cc);
            ok = true;
            attacked_this_turn = true;
            try_attack_reset_followup(cc, &g);
        } catch (...) {}
        if (ok && !camp_step_after_kill(g, static_cast<int>(best - g.camps.data()))) return true;
    }
    // Cast at range even before arriving.
    for (const auto& c : g.camps)
        if (c.hp > 0 && cheb(p, c.pos) <= 4 && (!vis || bb_test(*vis, c.pos))) {
            try { try_cast_on_camp(vision::camp_at(c.pos), i_tank); } catch (...) {}
            break;
        }
    // Live camp tiles block movement; dead ones are walkable (needed to dig into packed groups).
    bitboard live;
    live.clear();
    for (const auto& c : g.camps)
        if (c.hp > 0) live.set(c.pos);
    bitboard goals;
    goals.clear();
    for (auto& c : g.camps)
        if (c.hp > 0) goals |= W.attack_spots(c, range);
    goals &= ~*W.blocked;
    goals &= ~live;
    if (!i_tank) {
        // Never nearer than the tank to a damaging camp (camps break distance ties towards the lowest id,
        // so a lower id than the tank must stay strictly farther).
        bitboard keep;
        keep.clear();
        const int slack = idx < tank ? 0 : 1;
        for (const auto& c : g.camps) {
            if (c.hp <= 0 || camp_str(c.type) <= 0) continue;
            const int td = cheb(tank_pos, c.pos);
            if (td - slack >= 1) keep.draw_chebyshev(c.pos, static_cast<float>(td - slack));
        }
        bitboard g2 = goals & ~keep;
        if (!g2.is_empty()) {
            goals = g2;
        } else if (idx < tank) {
            // Rotated out (hurt): wait just outside the tank's distance, ready to capture.
            bitboard wait;
            wait.clear();
            for (const auto& c : g.camps) {
                if (c.hp <= 0 || camp_str(c.type) <= 0) continue;
                wait.draw_chebyshev(c.pos, static_cast<float>(cheb(tank_pos, c.pos) + 2));
            }
            wait &= ~keep;
            wait &= ~*W.blocked;
            wait &= ~live;
            if (!wait.is_empty()) goals = wait;
        }
    }
    if (goals.is_empty()) {
        for (const auto& c : g.camps) goals.draw_chebyshev(c.pos, 1.f);
        goals &= ~*W.blocked;
        goals &= ~live;
    }
    if (bb_test(goals, p)) {
        // In range but no live camp in sight (bushes, walls block it): step next to them; a camp that stays
        // unseen from right next to it is gone.
        if (P_SIGHT_FIX && vis && !best) {
            bool seen_live = false;
            for (const auto& c : g.camps)
                if (c.hp > 0 && bb_test(*vis, c.pos)) seen_live = true;
            if (!seen_live) {
                bitboard adj;
                adj.clear();
                for (const auto& c : g.camps)
                    if (c.hp > 0) adj.draw_chebyshev(c.pos, 1.f);
                adj &= ~*W.blocked;
                adj &= ~live;
                if (!adj.is_empty() && !bb_test(adj, p)) {
                    const bool mv = move_to(adj, g.field.get(), false, g.center);
                    if (P_CAMP_MOVEHIT) camp_hit_after_move(g, i_tank);
                    return mv;
                }
                for (auto& c : g.camps)
                    if (c.hp > 0 && cheb(p, c.pos) <= 1 && !bb_test(*vis, c.pos)) c.hp = 0;
            }
        }
        return false;
    }
    const bool mv = move_to(goals, g.field.get(), false, g.center);
    if (P_CAMP_MOVEHIT) camp_hit_after_move(g, i_tank);
    return mv;
}

// Melee champions can walk and basic-attack in one turn (camphit.py): after a step towards the camps, hit the best one now
// in reach (damaging camps first, then the lowest health).
void Bot::camp_hit_after_move(Group& g, bool i_tank) {
    auto& me = self();
    if (ranged || !moved_this_turn || attacked_this_turn || !me.can_attack()) return;
    const vec2 p = me.position();
    const int range = me.attack_range();
    const Camp* best = nullptr;
    for (const auto& c : g.camps) {
        if (c.hp <= 0 || cheb(p, c.pos) > range) continue;
        if (!best) { best = &c; continue; }
        const bool cd = camp_str(c.type) > 0, bd = camp_str(best->type) > 0;
        if (cd != bd ? cd : c.hp < best->hp) best = &c;
    }
    if (!best) return;
    try {
        const camp cc = vision::camp_at(best->pos);
        if (cc.health() <= 0) return;
        try_cast_on_camp(cc, i_tank);
        me.attack(cc);
        attacked_this_turn = true;
        try_attack_reset_followup(cc, &g);
    } catch (...) {}
}

// After a hit (P_CAMP_MOVEHIT 2): the camp died and no other live camp of the group is in reach - step on now (melee can
// hit, then move). True when the caller should go on to its step.
bool Bot::camp_step_after_kill(Group& g, int bi) {
    auto& me = self();
    if (P_CAMP_MOVEHIT < 2 || ranged || moved_this_turn || !me.can_move() || bi < 0 || bi >= static_cast<int>(g.camps.size())) return false;
    Camp& b = g.camps[static_cast<std::size_t>(bi)];
    bool dead = false;
    try { dead = vision::camp_at(b.pos).health() <= 0; } catch (...) { dead = true; }
    if (!dead) return false;
    b.hp = 0;
    const vec2 p = me.position();
    const int range = me.attack_range();
    bool left = false;
    for (const auto& c : g.camps) {
        if (c.hp <= 0) continue;
        if (cheb(p, c.pos) <= range) return false;  // more in reach: stay
        left = true;
    }
    return left;
}

// Hurt while allies keep fighting my group: stand off out of reach and take the capture (recalling
// during it) instead of walking home now. False when that does not apply.
bool Bot::retire_near(Group& g) {
    auto& me = self();
    World& W = world();
    const vec2 p = me.position();
    if (!enemies.empty() || !W.on_main(p)) return false;
    if (cheb(p, g.center) > g.radius + 8) return false;
    if (g.state == GState::Reward) {
        if (!capture(g)) return false;
        return true;
    }
    if (g.state != GState::Alive) return false;
    const float D = g.live_dps();
    if (D <= 0 || me.health() < 1.5f * D) return false;
    // Someone healthy is fighting it.
    bool fighting = false;
    for (const auto& a : allies)
        if (comms.task_of(a.index) == g.id && cheb(a.pos, g.center) <= g.radius + 4 && a.hp > std::max(P_TANK_FLOOR * a.max_hp, 2.5f * D)) fighting = true;
    if (!fighting) return false;
    act = "retire";
    bitboard reach;
    reach.clear();
    for (const auto& c : g.camps)
        if (c.hp > 0 && camp_str(c.type) > 0) reach.draw_chebyshev(c.pos, static_cast<float>(camp_range(c.type) + 1));
    if (!bb_test(reach, p)) return true;  // safe here: wait
    bitboard goals;
    goals.clear();
    goals.draw_chebyshev(g.center, static_cast<float>(g.radius + 8));
    goals &= ~reach;
    goals &= ~*W.blocked;
    goals &= ~*W.camp_tiles;
    if (goals.is_empty()) return false;
    move_to(goals, nullptr, false);
    return true;
}

bool Bot::has_crystal() {
    if (crystal_cache < 0) {
        crystal_cache = 0;
        try { crystal_cache = static_cast<int>(self().consumables()[consumable_type::tp_crystal].count()); } catch (...) {}
    }
    return crystal_cache > 0;
}

// Reach an island group: fetch a crystal from spawn, walk to the launch tile, jump onto the island.
bool Bot::travel_to_island(Group& g) {
    auto& me = self();
    World& W = world();
    const vec2 p = me.position();
    if (!has_crystal()) {
        if (bb_test(*W.my_spawn, p)) {
            try { me.buy(consumable_type::tp_crystal); crystal_cache = 1; } catch (...) {}
            if (!has_crystal()) { task = -1; return false; }
        } else {
            act = "island_fetch";
            return go_home();
        }
    }
    if (cheb(p, g.tp_land) <= 4) {
        // Best free landing tile within jump range on the island.
        vec2 best{ -1, -1 };
        int bd = distance_field::unreachable;
        for (int dx = -3; dx <= 3; ++dx)
            for (int dy = -3; dy <= 3; ++dy) {
                const vec2 q{ p.x + dx, p.y + dy };
                if (!in_bounds(q) || bb_test(*W.blocked, q) || bb_test(*W.camp_tiles, q) || bb_test(*W.mainland, q)) continue;
                if (bb_test(nav.occupied(), q)) continue;
                const int d = df_get(*g.field, q);
                if (d < bd) { bd = d; best = q; }
            }
        if (best.x >= 0) {
            try {
                if (me.consumables()[consumable_type::tp_crystal].use(best)) {
                    act = "teleport";
                    crystal_cache = 0;
                    return true;
                }
            } catch (...) {}
        }
    }
    act = "to_launch";
    W.ensure_launch_field(g);
    bitboard goal;
    goal.clear();
    goal.set(g.tp_launch);
    if (bb_test(goal, p)) return false;
    return move_to(goal, g.launch_field.get(), true);
}

bool Bot::work_group(Group& g) {
    auto& me = self();
    const vec2 p = me.position();
    if (g.island == 1 && world().on_main(p)) return travel_to_island(g);
    if (g.state == GState::Reward) return capture(g);
    if (g.state == GState::Respawning) {
        act = "wait_respawn";
        gather_since = -1;
        return stage_at(g);
    }
    const bool rally = comms.rally() == g.id;
    const bool chip = P_CHIP && chip_task == g.id;  // solo over several trips: no gathering, no abort
    // Team present at the group: me plus visible allies working on it. The tank is the lowest index
    // with health to spare (camps hit the nearest champion, ties to the lowest id): hurt tanks rotate out.
    const float Draw = g.live_dps();
    // A tank keeps enough health to walk out of reach afterwards (camps keep hitting while it leaves).
    // With another champion able to take over, one step back hands the camps over: two rounds of hits.
    const float leave_solo = static_cast<float>(g.max_range + 2) * Draw * camp_taken_mult(idx);
    const float leave_team = 2.f * Draw * camp_taken_mult(idx);
    struct Mem { int index; float hp, mhp; vec2 pos; };
    std::array<Mem, 6> mem{};
    int nm = 0;
    mem[static_cast<std::size_t>(nm++)] = Mem{ idx, me.health(), me.max_health(), p };
    float team_dps = camp_dps_of(idx), team_spare = std::max(0.f, me.health() - P_TANK_FLOOR * me.max_health());
    std::array<bool, 5> counted{};
    int present = 1;  // me
    for (const auto& a : allies) {
        if (comms.task_of(a.index) != g.id || cheb(a.pos, g.center) > g.radius + 7) continue;
        counted[static_cast<std::size_t>(a.index)] = true;
        ++present;
        team_dps += camp_dps_of(a.index);
        team_spare += std::max(0.f, a.hp - P_TANK_FLOOR * a.max_hp);
        if (nm < 6) mem[static_cast<std::size_t>(nm++)] = Mem{ a.index, a.hp, a.max_hp, a.pos };
    }
    // Allies waiting at this group out of sight (walls, bushes) report it in their slot flag.
    for (int a = 0; a < n_allies; ++a) {
        if (a == idx || counted[static_cast<std::size_t>(a)] || comms.task_of(a) != g.id || !comms.flag_of(a)) continue;
        ++present;
        const float ahp = hp_of(a), amax = max_hp_of(a);
        team_dps += camp_dps_of(a);
        team_spare += std::max(0.f, ahp - P_TANK_FLOOR * amax);
        if (nm < 6) mem[static_cast<std::size_t>(nm++)] = Mem{ a, ahp, amax, g.center };
    }
    auto tank_ok = [&](float hp, float mhp, float leave) { return hp > std::max(P_TANK_FLOOR * mhp, std::max(2.5f * Draw, leave)); };
    int able = 0;
    for (int i = 0; i < nm; ++i)
        if (tank_ok(mem[static_cast<std::size_t>(i)].hp, mem[static_cast<std::size_t>(i)].mhp, leave_team)) ++able;
    const float leave = (P_TANK_HANDOVER && able >= 2) ? leave_team : leave_solo;
    int tank = -1;
    vec2 tank_pos = p;
    int lowest = idx;
    vec2 lowest_pos = p;
    for (int i = 0; i < nm; ++i) {
        const Mem& m = mem[static_cast<std::size_t>(i)];
        if (m.index < lowest) { lowest = m.index; lowest_pos = m.pos; }
        if (tank_ok(m.hp, m.mhp, leave) && (tank < 0 || m.index < tank)) { tank = m.index; tank_pos = m.pos; }
    }
    if (tank < 0) { tank = lowest; tank_pos = lowest_pos; }
    bool awake = false;
    for (const auto& c : g.camps)
        if (c.hp > 0 && camp_str(c.type) > 0 && round - c.awake_round <= 1) awake = true;
    const float D = Draw * camp_taken_mult(tank);
    if (D <= 0 || awake) {
        gather_since = -1;
        const bool opening = P_ABORT_FIX && !opening_done && g.id == opening_gid;  // the whole team is on its way
        if (D > 0 && awake && !rally && !chip && !opening) {
            // Can the champions here still finish it? Otherwise back off before someone dies to it.
            // Count every ally committed to it (not only those in my sight: walls and bushes hid arriving
            // allies, and one champion's abort made the next one abort too).
            float c_dps = team_dps, c_spare = team_spare;
            if (P_ABORT_FIX)
                for (int a = 0; a < n_allies; ++a) {
                    if (a == idx || a >= 5 || counted[static_cast<std::size_t>(a)] || comms.task_of(a) != g.id) continue;
                    if (comms.flag_of(a)) continue;  // already counted as waiting out of sight
                    c_dps += camp_dps_of(a);
                    c_spare += std::max(0.f, hp_of(a) - P_TANK_FLOOR * max_hp_of(a));
                }
            const float Tl = g.hp_left() / std::max(1.f, c_dps);
            const float need_l = P_SEQ_DMG ? g.fight_damage(c_dps) * camp_taken_mult(tank) : D * Tl;
            const bool bad = need_l > P_ABORT_SLACK * (c_spare + (shield_per_round(tank) + heal_for(g.id, true)) * Tl);
            abort_rounds = bad ? abort_rounds + 1 : 0;
            if (bad && (!P_ABORT_FIX || abort_rounds >= 2)) {
                abort_rounds = 0;
                blacklist[static_cast<std::size_t>(g.id)] = round + 30;
                task = -1;
                act = "abort";
                std::vector<vec2> dangers;
                for (const auto& c : g.camps)
                    if (c.hp > 0 && camp_str(c.type) > 0 && cheb(c.pos, p) <= camp_range(c.type) + 1) dangers.push_back(c.pos);
                if (!dangers.empty() && nav.flee(dangers, nullptr)) moved_this_turn = true;
                return false;
            }
        }
        return attack_camps(g, tank, tank_pos);
    }
    const bool near = g.field ? World::field_at(*g.field, p) <= 4 : cheb(p, g.center) <= g.radius + 3;
    // Not started: pull only when the present team can finish it.
    const float T = g.hp_left() / std::max(1.f, team_dps);
    const float need_t = P_SEQ_DMG ? g.fight_damage(team_dps) * camp_taken_mult(tank) : D * T;
    bool ok = need_t <= team_spare * 0.85f + (shield_per_round(tank) + heal_for(g.id, true)) * T;
    if (!ok && chip && me.health() >= P_CHIP_START * me.max_health()) ok = true;
    if (!ok && rally) {
        // A called squad: go once all of it is here (or after a while) when it is about feasible.
        int alive_n = 0;
        for (int a = 0; a < n_allies; ++a)
            if (a == idx || comms.code_of(a) != slot::kDead) ++alive_n;
        const int squad = std::min(comms.rally_size(), alive_n);
        const float need = need_t, have = team_spare + (shield_per_round(tank) + heal_for(g.id, true)) * T;
        const bool waited = gather_since >= 0 && round - gather_since > 15;
        if ((present >= squad && need <= have * 1.1f) || (waited && need <= have)) ok = true;
        if (is_gate_group(g.id) && (present >= squad || waited)) ok = true;  // siege: several trips if need be
    }
    if (ok) {
        if (tank == idx) {
            gather_since = -1;
            return attack_camps(g, tank, tank_pos);
        }
        // The tank pulls; wait at the staging area until it does (not forever).
        if (gather_since < 0 && near) gather_since = round;
        // Pulling it myself makes me the camps' target: only when I could take the whole fight alone.
        const float my_spare = std::max(0.f, me.health() - P_TANK_FLOOR * me.max_health());
        const float Dme = Draw * camp_taken_mult(idx);
        const bool solo_safe = (P_SEQ_DMG ? g.fight_damage(team_dps) * camp_taken_mult(idx) : Dme * T) <= my_spare * 0.85f + shield_per_round(idx) * T;
        const int wait_for = (P_PULL_WAIT > 0 && !solo_safe) ? P_PULL_WAIT : P_WAIT_TANK;
        if (gather_since >= 0 && round - gather_since > wait_for) return attack_camps(g, tank, tank_pos);
        act = "wait_tank";
        return stage_at(g);
    }
    if (gather_since < 0 && near) gather_since = round;  // the wait starts on arrival
    // Nobody else is coming soon: chip it with whoever is here (camps never regenerate) instead of waiting.
    if (P_GATHER_CHIP >= 0 && !rally && gather_since >= 0 && round - gather_since >= P_GATHER_CHIP &&
        me.health() >= P_CHIP_START * me.max_health() && g.side >= -P_SIDE_MARGIN && (!g.big || present >= P_GATHER_CHIP_BIG)) {
        bool coming = false;  // an ally on its way here (not yet present)
        for (int a = 0; a < n_allies; ++a)
            if (a != idx && comms.task_of(a) == g.id && !counted[static_cast<std::size_t>(a)] && !comms.flag_of(a) && comms.code_of(a) != slot::kDead) coming = true;
        bool enemy_near = false;
        for (const auto& x : sightings)
            if (round - x.round <= 15 && cheb(x.pos, g.center) <= g.radius + 8) enemy_near = true;
        if (!coming && !enemy_near) {
            chip_task = g.id;
            gather_since = -1;
            return attack_camps(g, tank, tank_pos);
        }
    }
    if (!rally && gather_since >= 0 && round - gather_since > P_GATHER_WAIT) {
        blacklist[static_cast<std::size_t>(g.id)] = round + 40;
        task = -1;
        gather_since = -1;
        act = "give_up";
        return false;
    }
    act = rally ? "rally_gather" : "gather";
    return stage_at(g);
}

void Bot::farm() {
    World& W = world();
    const vec2 p = self().position();
    // Stay committed while fighting a group or capturing it.
    bool locked = false;
    if (task >= 0) {
        const Group& g = W.groups[static_cast<std::size_t>(task)];
        if (g.state == GState::Reward && bb_test(*g.tiles, p)) locked = true;
        if (g.state == GState::Alive)
            for (const auto& c : g.camps)
                if (c.hp > 0 && round - c.awake_round <= 1 && cheb(c.pos, p) <= 5) locked = true;
    }
    // Team rally on a heavy group: join once the current fight or capture is done.
    const int rally = comms.rally();
    bool in_rally = false;
    if (rally >= 0 && rally < static_cast<int>(W.groups.size()) && Comms::rally_member(idx, comms.rally_size(), n_allies) && (!locked || task == rally)) {
        const Group& rg = W.groups[static_cast<std::size_t>(rally)];
        // Being captured by someone else: nothing left for me there.
        bool taken = false;
        if (rg.state == GState::Reward && !bb_test(*rg.tiles, p))
            for (const auto& a : allies)
                if (bb_test(*rg.tiles, a.pos)) taken = true;
        if (!taken && rg.reachable && rg.island == 0 && W.on_main(p)) {
            if (task != rally) { task = rally; task_since = round; gather_since = -1; }
            in_rally = true;
            opening_done = true;
        }
    }
    if (!in_rally && P_OPENING && !opening_done) {
        if (opening_gid == -2) opening_gid = choose_opening();
        if (opening_gid < 0 || round > 150) opening_done = true;
        else {
            const Group& g = W.groups[static_cast<std::size_t>(opening_gid)];
            bool taken = g.state == GState::Respawning || (P_OPEN_ABORT && blacklist[static_cast<std::size_t>(opening_gid)] > round);
            if (g.state == GState::Reward && !bb_test(*g.tiles, p))
                for (const auto& a : allies)
                    if (bb_test(*g.tiles, a.pos)) taken = true;
            if (taken) opening_done = true;
            else task = opening_gid;
        }
    }
    for (int a = 0; a < n_allies && a < 6; ++a) {
        const int t = comms.task_of(a);
        if (t >= 0) { ally_last_task[static_cast<std::size_t>(a)] = t; ally_last_task_round[static_cast<std::size_t>(a)] = round; }
    }
    bool supporting = false;
    if (P_SUPPORT && ctype == champion_type::willow && !in_rally && opening_done && round >= P_SUPPORT_FROM && !locked) {
        // A healer farming alone earns little and dies most: go where the nearest working ally is.
        int bt = -1, bd = 1 << 20;
        for (int a = 0; a < n_allies && a < 6; ++a) {
            if (a == idx) continue;
            const int c = comms.code_of(a);
            if (c == slot::kDead || c == slot::kHome || c == slot::kTribute) continue;
            const int t = ally_last_task[static_cast<std::size_t>(a)];
            if (t < 0 || t >= static_cast<int>(W.groups.size()) || round - ally_last_task_round[static_cast<std::size_t>(a)] > 12) continue;
            const Group& tg = W.groups[static_cast<std::size_t>(t)];
            if (!tg.reachable || tg.island != 0 || blacklist[static_cast<std::size_t>(t)] > round) continue;
            int d = W.dist_to_group(tg, p);
            if (P_SUPPORT_MAR && ainfo[static_cast<std::size_t>(a)].type == champion_type::marcella) d -= 1000;  // Marcella first
            if (d < bd) { bd = d; bt = t; }
        }
        if (bt >= 0) {
            supporting = true;
            if (task != bt) { task = bt; task_since = round; gather_since = -1; }
        }
    }
    if (!in_rally && opening_done && !supporting) {
        // Re-plan every few rounds (staggered) or when the current task is gone.
        const bool due = task < 0 || (round + idx + P_SALT + (P_SALT >= 4 ? round / (37 + P_SALT) : 0)) % 4 == 0 || W.groups[static_cast<std::size_t>(task)].state == GState::Respawning;
        bool go = !locked && due;
        if (go && task >= 0 && W.groups[static_cast<std::size_t>(task)].state != GState::Respawning && fuel() < P_REPLAN_MIN && replan_skips < 2) {
            ++replan_skips;  // little fuel left this turn: re-plan next turn (an exhausted turn loses its move)
            go = false;
        }
        if (go) {
            replan_skips = 0;
            const int t = choose_task();
            if (t != task) {
                task = t;
                task_since = round;
                gather_since = -1;
            }
        }
    }
    if (task < 0) {
        act = "idle";
        comms.write_task(idx, -1, false);
        if (!W.on_main(p)) go_home();  // stranded on an island: recall
        else if (self().health() < P_IDLE_HEAL * self().max_health()) {
            act = "idle_heal";  // nothing worth doing at this health: heal so that heavier groups open up
            go_home();
            comms.write_raw(idx, slot::kHome, false);
        }
        return;
    }
    Group& g = W.groups[static_cast<std::size_t>(task)];
    if (in_rally && g.state != GState::Reward && !bb_test(*W.my_spawn, p)) {
        // Muster: heal before a long fight (no regeneration in the field).
        bool started = false;
        for (const auto& c : g.camps)
            if (c.hp > 0 && c.hp < c.max_hp) started = true;
        const float frac = self().health() / std::max(1.f, self().max_health());
        const bool waited = gather_since >= 0 && round - gather_since > 8;
        if (!started && (frac < 0.6f || (frac < 0.85f && waited))) {
            act = "rally_heal";
            gather_since = -1;
            go_home();
            comms.write_raw(idx, slot::kHome, false);
            return;
        }
    }
    if (threat_for != task) build_threat(p, task);
    if (fuel() > 70000) W.ensure_field(g);
    const bool did = work_group(g);
    if (P_LEAVE_BL > 0 && task < 0 && !did && !moved_this_turn && self().can_move() && fuel() > 50000) {
        // Gave the group up (an ally takes it): pick the next task now instead of wasting the turn.
        const int t = choose_task();
        if (t >= 0) {
            task = t;
            task_since = round;
            gather_since = -1;
            Group& g2 = W.groups[static_cast<std::size_t>(task)];
            if (threat_for != task) build_threat(p, task);
            work_group(g2);
        }
    }
    // Flag: waiting at the group or working on it (allies that cannot see me still count me as present).
    bool engaged = gather_since >= 0;
    if (P_ABORT_FIX && !engaged && task >= 0 && task < static_cast<int>(W.groups.size())) {
        const Group& tg = W.groups[static_cast<std::size_t>(task)];
        engaged = cheb(self().position(), tg.center) <= tg.radius + 3;
    }
    comms.write_task(idx, task, engaged);
}
