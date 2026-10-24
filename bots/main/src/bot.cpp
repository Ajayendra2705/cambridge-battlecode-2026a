// Champion decisions: farm camp groups as a team, bank gems, recall to heal and shop.
//
// Facts this relies on (measured locally): camps never regenerate health, they do not chase, a whole group
// wakes when one member is hit, each camp attacks its nearest champion, and standing on spawn heals almost
// fully in one round. So damage dealt to a camp is banked: fight until low, step out of range, heal, return.
//
// Every engine query costs fuel (100k per turn), so each turn starts by reading what it needs into a snapshot.
#include <cambc.h>
#include "bot.h"
#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>
#include <iostream>
#include <memory>
#include <optional>
#include <span>
#include <variant>
#include <vector>

using cambc::vec2;
using cambc::team;
using cambc::bitboard;
using cambc::distance_field;
namespace cm = cambc::map;
namespace cv = cambc::vision;

namespace {
#include "core.h"
#include "world.h"
#include "snapshot.h"
#include "sim.h"
#include "knowledge.h"
#include "comms.h"
#include "move.h"
#include "shop.h"
#include "abilities.h"
#include "camps.h"
#include "enemies.h"
#include "state.h"
#include "targets.h"
#include "camp_fight.h"

}  // namespace

void Bot::play_turn() {
    if (!W.ready) {
        init_world();
        splash = cambc::self().passive() == cambc::passive_type::splash_attack;
        const auto type = cambc::self().champion_name();
        fragile = type == cambc::champion_type::cassi || type == cambc::champion_type::issac;
    }
    auto& me = cambc::self();
    const int round = static_cast<int>(cambc::round_number());
    tracing = false;
    log_rounds = false;

    if (round % 20 == 0 || (!me.is_alive() && was_alive)) {
        std::cout << "R" << round << " s" << W.slot << " " << cambc::to_string(me.champion_name()) << " hp=" << me.health() << "/"
                  << me.max_health() << " gems=" << me.gem_count() << " gold=" << me.gold_count() << " tgt=" << current_target
                  << (me.is_alive() ? " pos=" + cambc::to_string(me.position()) : std::string(" DEAD")) << '\n';
    }
    if (W.slot == 0 && round % 10 == 0)
        std::cout << "G " << round << " " << cambc::global_submitted_gems(team::ally) << " "
                  << cambc::global_submitted_gems(team::enemy) << '\n';
    if (log_rounds && round > 1) std::cout << "W " << round - 1 << " " << W.slot << " " << current_target << " " << activity << '\n';
    count_activity();
    last_activity = activity;
    activity = "other";
    if (round % 250 == 0 || round == 30) {
        std::cout << "A s" << W.slot << " r" << round << " atk=" << n_attack << " reset=" << n_reset << " cc=" << n_cc
                  << " aoe=" << n_aoe << " dmg=" << n_dmg;
        for (size_t i = 0; i < act_names.size() && act_names[i]; ++i) std::cout << " " << act_names[i] << "=" << act_counts[i];
        std::cout << '\n';
    }
    if (!me.is_alive() && was_alive && round > 1) {
        if (death_ctx.n > 0) death_rounds.push_back(round);  // Camp deaths say nothing about enemy control.
        print_death(round);
        ++my_deaths;
        if (death_ctx.n > 0) ++kill_deaths;
    }
    was_alive = me.is_alive();
    if (!was_alive) {
        write_help(0);
        ACT("dead");
        prev_gems = 0;
        shop();
        write_claim(-1);
        retreating = false;
        return;
    }
    if (me.is_recalling()) { ACT("recall"); return; }
    if (me.is_submitting_gems()) { ACT("tribute"); return; }
    if (me.is_teleporting()) return;
    {
        const int now = static_cast<int>(me.gem_count());
        if (now > prev_gems) collected += now - prev_gems;
        if (now == 0 && prev_gems > 0) ++trib_n, trib_gems += prev_gems;
        prev_gems = now;
        ++alive_rounds;
    }

    prof_n = 0;
    STAGE("snapshot");
    take_snapshot();
    STAGE("knowledge");
    refresh_claims();
    update_knowledge();
    build_phantoms();
    read_broadcast();
    record_sightings();
    record_death_ctx();
    {
        bool caught = false;
        for (const auto& e : S.enemies)
            if (!W.enemy_spawn.is_set(e.pos) && dist(S.me, e.pos) <= 3) caught = true;
        write_help(caught && home_side(S.me) ? help_code(S.me) : 0);
    }
    STAGE("enemies");
    place_ward_forward();
    const vec2 p = S.me;
    const bool at_spawn = W.ally_spawn.is_set(p);
    if (at_spawn) {
        shop();
        retreating = false;
    }

    // Damage not explained by camps comes from an enemy, possibly hidden in a bush.
    const float incoming = camp_incoming(p);
    const float taken = last_round + 1 == round ? last_hp - S.hp : 0.0f;
    // Some champions act only every other round: camps then land several hits per step we take.
    const int turn_gap = round - last_round >= 1 && round - last_round <= 3 ? round - last_round : 1;
    const float taken_rate = round - last_round <= 3 ? (last_hp - S.hp) / turn_gap : 0.0f;
    last_hp = S.hp;
    last_round = round;
    if (taken > incoming + 1.0f) {
        bool blamed = false;
        for (const auto& k : known_camps) {
            if (k.group < 0 || k.str < (taken - incoming) * 0.8f) continue;
            auto& g = W.groups[k.group];
            const vec2 pos = g.spawns[k.idx];
            if (g.state != 0 || S.visible.is_set(pos) || dist(p, pos) > k.range) continue;
            g.awake_round = round;
            blamed = true;
        }
        if (!blamed) enemy_seen_round = enemy_seen_at = round;
    }
    // Big hits are rare; log the situation so platform replays show how we get caught.
    if (taken > S.max_hp * 0.25f) {
        std::cout << "H" << round << " s" << W.slot << " " << cambc::to_string(me.champion_name()) << " at " << cambc::to_string(p)
                  << " hp=" << S.hp << "/" << S.max_hp << " took=" << taken << " camp=" << incoming << " last=" << last_activity
                  << " allies=" << S.allies.size() << " enemies:";
        for (const auto& e : S.enemies)
            std::cout << " " << cambc::to_string(e.ch.champion_name()) << "@" << dist(p, e.pos) << "(" << e.hp << "/b" << e.burst << ")";
        std::cout << '\n';
    }

    // Feature log for the death-hazard model (tools/hazard.py): every 10 rounds per champion.
    if (false) {
        int ne = 0, nd = 99, na = 0;
        float eburst = 0;
        for (const auto& e : S.enemies) {
            if (W.enemy_spawn.is_set(e.pos)) continue;
            ++ne;
            nd = std::min(nd, dist(p, e.pos));
            if (dist(p, e.pos) <= 6) eburst += e.burst;
        }
        for (const auto& a : S.allies) if (dist(p, a.pos) <= 5) ++na;
        const int ef = W.enemy_field.get(p), hf = W.spawn_field.get(p);
        std::cout << "F " << round << " " << W.slot << " " << cambc::self().gem_count() << " " << static_cast<int>(100 * S.hp / S.max_hp) << " " << ne << " " << nd
                  << " " << std::min(999, round - enemy_seen_round) << " " << W.altar_field.get(p) << " " << hf << " " << ef << " " << na
                  << " " << static_cast<int>(eburst) << " " << static_cast<int>(S.max_hp) << '\n';
    }
    // Calibration log: predicted champion damage on us this round (enemies in reach, live cooldowns) vs the
    // champion damage actually taken since our last turn. Analysed by tools/calib.py.
    {
        static float prev_pred = -1;
        float pred = 0;
        bool near = false;
        for (const auto& e : S.enemies) {
            if (W.enemy_spawn.is_set(e.pos)) continue;
            const int d = dist(p, e.pos);
            if (d <= 8) near = true;
            const bool basic = e.range <= 1 ? d <= 2 : d <= e.range;
            float spell = 0;
            if (d <= 5)
                for (const auto& sl : cached_slots(e.ch)) if (sl.cd <= 0) spell = std::max(spell, sl.dmg);
            pred += (basic ? e.str : 0.0f) + spell;
        }
        const float actual = std::max(0.0f, taken - incoming);
        if (prev_pred >= 0 && (prev_pred > 0 || actual > 0))
            cal_pred += prev_pred, cal_act += actual;
            cal_f = static_cast<float>(std::clamp((cal_act + 3000.0 * 0.18) / (cal_pred + 3000.0) / 0.18, 1.0, 2.0));
            // (calibration log line removed in the lean build)
        prev_pred = near ? pred : -1.0f;
    }
    // Compare nearby strength with visible enemies.
    // Lanchester-style strength: total health times total damage per round on each side.
    float enemy_hp = 0, enemy_dps = 0, ally_hp = S.hp, ally_dps = my_dps();
    int enemy_count = 0, ally_count = 1;
    const ChampSnap* prey = nullptr;
    for (const auto& e : S.enemies) {
        if (dist(p, e.pos) > 6) continue;
        // Enemies resting on their own spawn only matter when they can already hit us; they cannot be hit.
        const bool safe_home = W.enemy_spawn.is_set(e.pos);
        if (safe_home && dist(p, e.pos) > e.range) continue;
        enemy_seen_round = round;
        enemy_hp += e.hp;
        enemy_dps += e.dps;
        ++enemy_count;
        // Focus whoever dies fastest relative to the damage they deal.
        if (!safe_home && dist(p, e.pos) <= std::max(S.range, 4) && (!prey || e.hp < prey->hp)) prey = &e;  // Rivals hit the lowest-health enemy in reach.
    }
    // An enemy fighting a nearby ally is our fight too: go and help.
    if (!prey)
        for (const auto& e : S.enemies) {
            if (W.enemy_spawn.is_set(e.pos) || dist(p, e.pos) > 8) continue;
            bool engaged = false;
            for (const auto& a : S.allies) if (dist(a.pos, e.pos) <= 3) engaged = true;
            if (engaged && (!prey || e.hp < prey->hp)) prey = &e;
        }
    // Answer a team focus call on a visible enemy close enough to reach.
    if (const auto* f = focus_target(); f && dist(p, f->pos) <= 8 && !W.enemy_spawn.is_set(f->pos)) prey = f;
    for (const auto& a : S.allies)
        if (dist(p, a.pos) <= 5) ally_hp += a.hp, ally_dps += a.dps, ++ally_count;
    const float enemy_power = enemy_hp * enemy_dps, ally_power = ally_hp * ally_dps;

    // Enemies whose combined one-round burst could kill us from where they stand (after a step).
    float lethal = 0;
    for (const auto& e : S.enemies)
        if (!W.enemy_spawn.is_set(e.pos) && dist(p, e.pos) <= e.reach + 1) lethal += e.burst;
    const bool in_kill_range = lethal >= S.hp * 0.9f;
    // Fight when stronger and not outnumbered, when the target is nearly dead, or from the safety of spawn.
    // Cassi and Issac die together, so they only join fights with a clear edge.
    // Play the fight out a few rounds with live cooldowns instead of comparing raw totals.
    bool winning = false, sim_me_dies = false;
    if (prey) {
        using ct = cambc::champion_type;
        std::array<std::vector<SimUnit>, 2> side;
        std::vector<vec2> pos[2];
        std::vector<ct> types[2];
        auto add = [&](int s, float hp, float str, int range, vec2 at, std::array<SimSlot, 2> slots, ct type) {
            SimUnit x;
            x.hp = hp, x.str = str, x.range = range, x.slots = slots;
            side[s].push_back(x);
            pos[s].push_back(at);
            types[s].push_back(type);
        };
        add(0, S.hp, S.str, S.range, p, read_slots(cambc::self()), cambc::self().champion_name());
        for (const auto& a : S.allies)
            if (dist(p, a.pos) <= 8) add(0, a.hp, a.str, a.range, a.pos, cached_slots(a.ch), a.type);
        for (const auto& e : S.enemies)
            if (dist(p, e.pos) <= 8 && !(W.enemy_spawn.is_set(e.pos) && dist(p, e.pos) > e.range))
                {
                    auto sl = cached_slots(e.ch);
                    for (auto& x : sl) x.dmg *= cal_f;
                    add(1, e.hp, e.str * cal_f, e.range, e.pos, sl, e.type);
                }
        for (int s = 0; s < 2; ++s) {
            for (size_t i = 0; i < side[s].size(); ++i) {
                int d = 99;
                for (auto q : pos[1 - s]) d = std::min(d, dist(pos[s][i], q));
                side[s][i].d = d;
                for (size_t j = 0; j < side[s].size(); ++j)
                    if ((types[s][i] == ct::cassi && types[s][j] == ct::issac) || (types[s][i] == ct::issac && types[s][j] == ct::cassi))
                        side[s][i].link = static_cast<int>(j);
            }
        }
        const SimResult res = simulate_fight(side, 3, true);
        sim_me_dies = res.unit0_dead;
        winning = !side[1].empty()
            && (res.dead[1] > res.dead[0] || (res.dead[1] == res.dead[0] && res.hp_frac[0] > res.hp_frac[1] + 0.2f))
            && !(sim_me_dies && res.dead[1] == 0);
    }
    // First strike in a lone 1v1 with a close kill race: being caught later means fleeing with free hits taken.
    if (prey && !winning && enemy_count == 1 && S.hp >= S.max_hp * 0.5f) {
        auto& self = cambc::self();
        const float mine = champion_dps(read_coef(self), S.str, self.focus());
        if (mine > 0 && prey->dps > 0 && prey->hp / mine < 1.2f * S.hp / prey->dps) winning = true;
    }
    const bool finisher = prey && prey->hp <= ally_dps * 2.5f && S.hp > S.max_hp * 0.3f && !sim_me_dies;
    // A carrier with a full bag is worth a risky fight: the kill takes all of it.
    const bool rich = prey && prey->gems >= 30 && ally_power >= enemy_power * 0.5f && S.hp > S.max_hp * 0.5f && !sim_me_dies;
    // A big bag is worth more banked than any fight: its carrier never engages (boss_battle: 1446-3289 gem bags lost in fights).
    const bool big_bag = me.gem_count() >= 150;
    if (!big_bag && prey && (winning || finisher || rich || (at_spawn && dist(p, prey->pos) <= S.range))) {
        STAGE("fight enemy");
        ACT("pvp");
        call_focus(*prey);
        // Favourable fight: focus the weakest enemy, spells first; an unused cast raises the shield.
        use_champion_abilities(*prey);
        use_support_abilities(true);
        if (dist(S.me, prey->pos) <= S.range) {
            if (attack_unit(prey->ch)) try_attack_reset_and_hit(prey->ch);
            return;
        }
        // Close in through the tile least exposed to enemy bursts; melee strikes after the step.
        if (me.can_move()) {
            vec2 best{-1, -1};
            float best_exposure = 0;
            int best_d = 99;
            for (auto d : DIRS) {
                const vec2 t{S.me.x + d.x, S.me.y + d.y};
                if (!cm::is_in_bounds(t) || W.terrain.is_set(t) || S.occ.is_set(t)) continue;
                const int pd = dist(t, prey->pos);
                if (pd >= dist(S.me, prey->pos)) continue;
                float exposure = 0;
                for (const auto& e : S.enemies)
                    if (!W.enemy_spawn.is_set(e.pos) && dist(t, e.pos) <= e.reach) exposure += e.burst;
                const bool better = best.x < 0 || (pd <= S.range) > (best_d <= S.range)
                    || ((pd <= S.range) == (best_d <= S.range) && (exposure < best_exposure || (exposure == best_exposure && pd < best_d)));
                if (better) best = t, best_exposure = exposure, best_d = pd;
            }
            if (best.x >= 0 ? safe_move(best) : (me.move_towards(prey->pos), false)) {
                if (dist(S.me, prey->pos) <= S.range && attack_unit(prey->ch)) try_attack_reset_and_hit(prey->ch);
            }
        }
        return;
    }
    bool threatened = false;
    for (const auto& e : S.enemies)
        if (dist(p, e.pos) <= std::max(e.range + 2, e.dps > e.str * 1.15f ? 6 : 0) && !W.enemy_spawn.is_set(e.pos))
            threatened = true;
    const bool hit_by_enemy = taken > incoming + 1.0f;
    const bool losing = (sim_me_dies && !winning) || enemy_count > ally_count || enemy_power > ally_power * 0.9f || S.hp < S.max_hp * 0.4f
        || in_kill_range;
    // Not engaging: from here on, moves keep out of enemy reach.
    S.avoid_danger = !S.danger.empty();
    if ((threatened && losing) || (hit_by_enemy && !prey)) {
        if (prey) use_champion_abilities(*prey);
        const bool healthy = S.hp >= S.max_hp * 0.5f && !hit_by_enemy;
        if (healthy && !in_danger(S.me)) {
            // Already out of reach: keep working, staying out of it.
        } else if (healthy && [&] {
                       // Hit before stepping away when the hit is free: melee keeps its move after attacking, and a target
                       // that cannot reach us cannot answer (b5 ge4: with an enemy within 3 the rivals hit a champion in
                       // 50% of rounds, we in 35%, and stand idle 12% vs 6%).
                       const ChampSnap* t = nullptr;
                       for (const auto& e : S.enemies)
                           if (!W.enemy_spawn.is_set(e.pos) && dist(S.me, e.pos) <= S.range && (S.range <= 1 || dist(S.me, e.pos) > e.range)
                               && (!t || e.hp < t->hp)) t = &e;
                       if (t && attack_unit(t->ch)) try_attack_reset_and_hit(t->ch);
                       return step_out_of_danger();
                   }()) {
            ACT("kite");
            return;
        } else {
            // Caught by a lone chaser far from home: it is as fast as we are, so running only hands it free hits.
            const ChampSnap* chaser = nullptr;
            int near_enemies = 0;
            for (const auto& e : S.enemies) {
                if (W.enemy_spawn.is_set(e.pos) || dist(p, e.pos) > 5) continue;
                ++near_enemies;
                if (dist(p, e.pos) <= 1) chaser = &e;
            }
            // Duel only when we kill first: its health over our damage per round against our health over its damage
            // per round (both from engine ability metadata). Platform pv1: duels cost 13.9 deaths per 100 duel
            // rounds against 3.5 for fleeing, mostly against chasers near full health.
            bool we_kill_first = false, turn_and_fight = false;
            if (chaser) {
                auto& self = cambc::self();
                const float mine = champion_dps(read_coef(self), S.str, self.focus());
                we_kill_first = mine > 0 && chaser->dps > 0 && chaser->hp / mine < S.hp / chaser->dps;
                // A melee chaser keeps adjacent and hits every round of the run home; when that run is fatal anyway
                // and the kill race is close, trading blows beats taking free hits (platform traces: 440 of 538
                // deaths start as a 1v1 at full health and end fleeing).
                const bool futile = chaser->range <= 1 && chaser->dps * W.spawn_field.get(p) >= S.hp;
                turn_and_fight = futile && mine > 0 && chaser->dps > 0 && chaser->hp / mine < 1.5f * S.hp / chaser->dps;
            }
            if (chaser && near_enemies == 1 && W.spawn_field.get(p) > 4 && (we_kill_first || turn_and_fight)) {
                ACT("duel");
                use_champion_abilities(*chaser);
                if (dist(S.me, chaser->pos) <= S.range && attack_unit(chaser->ch)) try_attack_reset_and_hit(chaser->ch);
                return;
            }
            ACT("flee");
            // Call for help on the closest chaser.
            {
                const ChampSnap* c = nullptr;
                for (const auto& e : S.enemies)
                    if (!W.enemy_spawn.is_set(e.pos) && dist(p, e.pos) <= 2 && (!c || dist(p, e.pos) < dist(p, c->pos))) c = &e;
                if (c) call_focus(*c);
            }
            // Hurt, hit by something unseen, or cornered: run home, striking whoever is still in reach.
            S.avoid_danger = false;
            use_support_abilities(true);
            // Melee hits before running: it keeps its move after attacking, and after the step the chaser is often out of
            // reach (fh1 b5 decoded: with an enemy adjacent we hit in 58% of rounds, the rivals in 82%). The weakest first.
            if (S.range <= 1) {
                const ChampSnap* t = nullptr;
                for (const auto& e : S.enemies)
                    if (!W.enemy_spawn.is_set(e.pos) && dist(S.me, e.pos) <= S.range && (!t || e.hp < t->hp)) t = &e;
                if (t && attack_unit(t->ch)) try_attack_reset_and_hit(t->ch);
            }
            if (!at_spawn && !flee_bush()) walk_home();
            for (const auto& e : S.enemies)
                if (!W.enemy_spawn.is_set(e.pos) && dist(S.me, e.pos) <= S.range && attack_unit(e.ch)) break;
            write_claim(-1);
            return;
        }
    }

    // Attack on sight, as every top team does: hit the weakest enemy in reach (spells within 4) before the plan.
    // Melee keeps its move after attacking; ranged attacks cost the move, so only when healthy.
    {
        const ChampSnap* t = nullptr;
        for (const auto& e : S.enemies) {
            if (W.enemy_spawn.is_set(e.pos) || dist(S.me, e.pos) > std::max(S.range, 4)) continue;
            if (!t || e.hp / e.max_hp < t->hp / t->max_hp) t = &e;
        }
        if (t) {
            call_focus(*t);
            use_champion_abilities(*t);
            // Vendetta closes 2 tiles with her dash and hits the same round: with an enemy 2-3 tiles away the rivals'
            // Vendettas hit a champion in 26% of rounds, ours in 16% (b6 decoded). Only when the fight is not lost
            // (we are past the flee branch) and the simulation does not say we die.
            if (me.champion_name() == cambc::champion_type::vendetta && !sim_me_dies && dist(S.me, t->pos) >= 2 && dist(S.me, t->pos) <= 3
                && me.can_attack() && me.can_cast()) {
                for (const auto& ab : me.abilities()) {
                    if (!ab.is_ready() || !ab.is_dash()) continue;
                    vec2 best{-1, -1};
                    for (auto land : ab.valid_tiles().positions()) {
                        if (S.occ.is_set(land) || W.terrain.is_set(land) || dist(land, t->pos) > S.range) continue;
                        if (best.x < 0 || dist(land, S.me) < dist(best, S.me)) best = land;
                    }
                    if (best.x < 0) continue;
                    try {
                        if (ab.use(best)) { S.me = best; break; }
                    } catch (const cambc::error&) {
                    }
                }
            }
            // Ranged champions also shoot when hurt unless the enemies near can burst them this round: our Vespers hit in
            // 41% of rounds with an enemy in range, the rivals' 53% (b6 decoded).
            if (dist(S.me, t->pos) <= S.range && (S.range <= 1 || S.hp > S.max_hp * 0.5f || dist(S.me, t->pos) > t->range || !in_kill_range)
                && attack_unit(t->ch))
                try_attack_reset_and_hit(t->ch);
        }
    }

    if (at_spawn && S.hp < S.max_hp * 0.9f) {
        ACT("heal_wait");
        write_claim(-1);
        return;
    }

    STAGE("retreat");
    // Leave camp range before the next hits could kill. Each camp hits only its nearest champion, so count the
    // camps nobody else is closer to, or what we just took.
    // Every camp aiming at us hits each round until we are out of all their reaches, so sum them and count the
    // real path out (stepping away from one camp can keep us inside another's range).
    float strongest = 0;
    int steps_out = 0;
    bool in_camp_range = false;
    std::vector<CampSnap> near_camps = S.camps;
    near_camps.insert(near_camps.end(), S.phantoms.begin(), S.phantoms.end());
    bitboard reach;
    reach.clear();
    for (const auto& c : near_camps) {
        const int d = dist(p, c.pos);
        if (d > c.range + 3 || !camp_awake(c)) continue;
        reach.draw_chebyshev(c.pos, static_cast<float>(c.range));
        if (d > c.range) continue;
        in_camp_range = true;
        steps_out = std::max(steps_out, c.range + 1 - d);
        bool someone_closer = false;
        for (const auto& a : S.allies) if (dist(a.pos, c.pos) < d) { someone_closer = true; break; }
        if (!someone_closer)
            for (const auto& e : S.enemies) if (dist(e.pos, c.pos) < d) { someone_closer = true; break; }
        if (!someone_closer) strongest += c.str;
    }
    const auto safe_tiles = ~reach & ~W.terrain;
    if (in_camp_range) {
        const int path = steps_to_tiles(safe_tiles);
        if (path != UNREACH) steps_out = std::max(steps_out, path);
    }
    const float danger = std::max(strongest, taken);
    // Camps land one more hit as we step out of reach, so leaving takes steps_out + 1 hits after this one.
    // With no enemy around, a heal trip home (often 50+ tiles) is the real cost: use more of our health per trip.
    const bool quiet = round - enemy_seen_round > 30;
    if ((danger > 0 || lethal > 0) && S.hp < danger * (steps_out + 1.0f) + lethal + (quiet ? 15.0f : 40.0f)) retreating = true;
    if (retreating) {
        if (in_camp_range) {
            ACT("retreat");
            if (!step_to_tiles(safe_tiles)) step_away(camp_threats(p, 1));
            return;
        }
        // Out of reach: rejoin if still healthy, otherwise go home to heal.
        const float hardest = current_target >= 0 ? W.groups[current_target].hardest() : 0.0f;
        // Rejoin only with health for every camp of the group (shared among its claimants) for the walk in, a hit and
        // the walk out: rejoining at 30-50% against 4 elks (240 per round) killed us (local interlock, rows, shortcut).
        float pressure = 0;
        if (current_target >= 0) {
            const auto& tg = W.groups[current_target];
            pressure = tg.strength_left() * (clear_stats(tg).range + 2) / std::max(1, claimants(current_target));
        }
        if (S.hp >= S.max_hp * (quiet ? 0.3f : 0.5f) && S.hp >= hardest * (quiet ? 4.0f : 6.0f) + 40.0f && S.hp >= pressure + 40.0f) {
            retreating = false;
        } else {
            write_claim(-1);
            ACT("home_heal");
            if (me.gem_count() > 0 && W.altar_field.get(p) <= 3 && bank_gems()) return;
            go_home();
            return;
        }
    }

    // Heal when worn down and no fight holds us.
    if (!at_spawn && S.hp < S.max_hp * (quiet ? 0.2f : 0.5f) && incoming == 0) {
        retreating = true;
        write_claim(-1);
        ACT("home_heal");
        go_home();
        return;
    }

    STAGE("bank");
    // Bank carried gems when holding a lot or an altar is close.
    const int gems = static_cast<int>(me.gem_count());
    // Game-end horizon: the enemy's recent tribute rate says how many rounds remain; carried gems are worth
    // nothing once they reach 1000, so start the trip when k times its length no longer fits.
    static std::array<int, 2101> enemy_hist{};
    const int e_sub = static_cast<int>(cambc::global_submitted_gems(team::enemy));
    if (round >= 0 && round <= 2100) enemy_hist[round] = e_sub;
    const int back = std::max(0, round - 150);
    const double e_rate = std::max(0.2, (e_sub - enemy_hist[back]) / static_cast<double>(std::max(1, round - back)));
    const double t_end = std::min((cambc::constants::winning_gems - e_sub) / e_rate, 2000.0 - round);
    const int trip = W.altar_field.get(p) + (gems + 9) / 10 + 1;
    const bool deadline = gems > 0 && 2.0 * trip >= t_end;
    if (gems > 0 && (incoming == 0 || deadline || gems >= 150)) {
        const int altar_d = W.altar_field.get(p);
        const bool endgame = round > 1900 || deadline
            || cambc::global_submitted_gems(team::ally) + gems >= cambc::constants::winning_gems;
        const double c = (collected + 0.15 * 200.0) / (alive_rounds + 200.0);
        const double h = (my_deaths + 1.0) / (alive_rounds + 600.0) + 1.0 / std::max(1.0, t_end);
        const double m = 1.0 + (kill_deaths + 0.85 * 2.0) / (my_deaths + 2.0);
        // Trip cost: the detour through the altar on the way to our target (altar beside the route costs little), not a
        // round trip. Rivals tribute 2-3x as often (road_of_riches by r600: 30 tributes vs our 0, altars mid-map).
        double walk = 2.0 * altar_d;
        if (current_target >= 0 && travel_built >= static_cast<int>(W.groups.size())) {
            const auto& tg = W.groups[current_target];
            int target_altar = UNREACH;
            for (auto sp : tg.spawns) target_altar = std::min<int>(target_altar, W.altar_field.get(sp));
            const int to_target = travel_fields[current_target]->get(p);
            if (target_altar != UNREACH && to_target != UNREACH && altar_d != UNREACH)
                walk = std::min(walk, std::max(0.0, static_cast<double>(altar_d + target_altar - to_target)));
        }
        const double tau = walk + (gems + 9) / 10 + 1;
        // Order quantity: a trip costs c * tau gems of lost collection (the old form used tau, a factor 1/sqrt(c), about
        // 2.8x too big: our median tribute 32 gems vs the rivals' 15). Per gem banked the cost is c tau / g for trips plus
        // g (m h / 2c) for the bag at risk plus g lambda / 10 for the channel (bag / 10 turns at the altar), so
        // g* = sqrt(2 c^2 tau / (m h + lambda c / 5)). lambda, the per-turn chance a channel is broken, is fitted on 5.8k
        // of our platform tributes (b5, b6, b34): 0.0065 + 0.009 per enemy within 10 of the altar (0.0068 / 0.0152 / 0.0254).
        int near_altar = 0;
        for (const auto& e : S.enemies)
            for (auto a : W.altars)
                if (!W.enemy_spawn.is_set(e.pos) && dist(e.pos, a) <= 10 && W.altar_field.get(a) <= altar_d + 1) { ++near_altar; break; }
        const double lambda = 0.0065 + 0.009 * std::min(near_altar, 3);
        // Measured trip overhead: with the plain c * tau trip cost (ef1) the b6 bags halved (median about 15) and collection
        // fell 12% by r600 (316 vs 358), while fh2's bags (about 32) lost more on death; tributed by r1000 434 (fh2) vs 411
        // (ef1). A trip also breaks the farming flow (claims, respawn timing), so it costs about 3 x c x tau: bags near 26.
        const double batch = std::sqrt(2.0 * 3.0 * c * c * tau / (m * h + lambda * c / 5.0));
        if ((gems >= batch && S.round >= bank_blocked_until) || endgame) {
            // Give up for a while if the way to the altar makes no progress (blocked or contested).
            if (altar_d < bank_best) bank_best = altar_d, bank_stall = 0;
            else if (++bank_stall > 6) bank_blocked_until = S.round + 40, bank_best = UNREACH, bank_stall = 0;
            write_claim(-1);
            ACT("bank");
            if (bank_gems()) return;
        } else {
            bank_best = UNREACH;
            bank_stall = 0;
        }
    }

    STAGE("shop");
    // Spend gold: shards add permanent stats, so a trip home pays off once enough has piled up.
    const bool remote_shop = me.passive() == cambc::passive_type::remote_shop;
    if (remote_shop) shop();
    const int gold = static_cast<int>(me.gold_count());
    if (!at_spawn && incoming == 0 && round < 1850 && !remote_shop) {
        const int home = W.spawn_field.get(p);
        if (gold >= 150 || (gold >= 90 && home <= 8)) {
            ACT("shop_trip");
            write_claim(-1);
            go_home();
            return;
        }
    }

    // Answer a teammate's help call: healthy, light bag, not capturing and nothing in our own view.
    {
        const vec2 h = read_help();
        bool quiet_here = true;
        for (const auto& e : S.enemies) if (!W.enemy_spawn.is_set(e.pos) && dist(p, e.pos) <= 8) quiet_here = false;
        const bool capturing = current_target >= 0 && W.groups[current_target].state == 1 && W.groups[current_target].tiles.is_set(p);
        if (h.x >= 0 && quiet_here && !capturing && S.hp >= S.max_hp * 0.6f && gems < 100 && dist(p, h) >= 3 && dist(p, h) <= 14
            && home_side(h) && me.can_move()) {
            ACT("help");
            write_claim(-1);
            me.move_towards(h);
            return;
        }
    }
    STAGE("pick");
    // Keep fighting an awake target; one champion captures; the rest follow the team target.
    const bool in_fight = current_target >= 0 && W.groups[current_target].state == 0
        && !camp_threats(p, 1).empty();
    // Re-plan every few rounds, or at once when the target's state changes.
    const int target_state = current_target >= 0 ? W.groups[current_target].state : -1;
    if (!in_fight && (S.round - last_pick_round >= 3 || target_state != last_pick_state)) {
        current_target = pick_group(current_target);
        last_pick_round = S.round;
        last_pick_state = current_target >= 0 ? W.groups[current_target].state : -1;
    } else if (cambc::fuel_remaining() > 50000) {
        build_travel_field();  // A big-map field costs about 30k: build only with room left this turn.
    }
    write_claim(current_target);
    if (group_invested.empty()) group_invested.assign(W.groups.size(), 0);
    for (size_t i = 0; i < W.groups.size(); ++i) if (W.groups[i].state != 0) group_invested[i] = 0;
    if (current_target >= 0 && W.groups[current_target].state == 0) ++group_invested[current_target];
    STAGE("camp fight");
    if (current_target < 0) {
        if (gems > 0) bank_gems();
    } else {
        fight_or_approach(current_target);
    }
    STAGE("end");
    if (tracing) {
        std::cout << "P s" << W.slot;
        for (int i = 1; i < prof_n; ++i) std::cout << " " << prof_names[i - 1] << "=" << (prof_fuel[i - 1] - prof_fuel[i]);
        std::cout << '\n';
    }
}
