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
#include <cstring>
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
#include "micro.h"
#include "camps.h"
#include "enemies.h"
#include "state.h"
#include "targets.h"
#include "camp_fight.h"

}  // namespace

static void play_turn_core();

// The decision pipeline, then a free hit with any attack it left unused, then a step out of enemy reach when the
// turn ended standing in it: moves avoid danger tiles once we are not engaging, so a champion whose ways forward were
// all in danger stood still, also on a danger tile itself (410 such stalls per 80 games in the bf4 audit).
void Bot::play_turn() {
    play_turn_core();
    free_hit();
    if (W.ready && S.round == static_cast<int>(cambc::round_number()) && S.avoid_danger && !S.walked && in_danger(S.me)
        && !(S.holding && S.hp >= S.max_hp * 0.5f)) {
        try {
            auto& me = cambc::self();
            if (me.is_alive() && !me.is_recalling() && !me.is_submitting_gems() && !me.is_teleporting()) step_out_of_danger();
        } catch (const cambc::error&) {
        }
    }
    // A walk to the target that stayed put twice while moves avoid enemy danger: the way is held. Leave that group for
    // 20 rounds and pick again (bf5 audit: champions stood 5 rounds and more beside rewards they could not reach).
    static int held_turns = 0;
    const bool walking = !std::strcmp(activity, "to_capture") || !std::strcmp(activity, "approach");
    if (W.ready && !stale() && walking && S.avoid_danger && S.me == S.start && current_target >= 0 && !S.dash_wait) {
        if (++held_turns >= 2) {
            if (!blocked_until.empty()) blocked_until[current_target] = S.round + 20;
            last_pick_round = -100;
            held_turns = 0;
        }
    } else {
        held_turns = 0;
    }
    // Turn order for the next round (`set_priority`; within a team a higher priority acts first, then draft order): a
    // champion within 5 of an enemy acts before the others, the most hurt first, so it can strike or step away before the
    // enemies near it act. Top teams order their turns this way (top12 replays: 70 of 80 team-games reorder; a champion
    // under 40% health within 2 of an enemy acts first among its team nearly always); against cr3 on brkp, rivals that
    // reorder acted before our champion in 63% of contact rounds (46% for rivals that do not).
    if (W.ready) {
        try {
            auto& me = cambc::self();
            int pri = 0;
            if (me.is_alive() && S.round == static_cast<int>(cambc::round_number()) && S.max_hp > 0)
                for (const auto& e : S.enemies)
                    if (!W.enemy_spawn.is_set(e.pos) && dist(S.me, e.pos) <= 5) {
                        pri = 2000 - static_cast<int>(1000.0f * S.hp / S.max_hp);
                        break;
                    }
            me.set_priority(pri);
        } catch (const cambc::error&) {
        }
    }
}

static void play_turn_core() {
    if (!W.ready) {
        const int init_round = static_cast<int>(cambc::round_number());
        init_world();
        splash = cambc::self().passive() == cambc::passive_type::splash_attack;
        const auto type = cambc::self().champion_name();
        fragile = type == cambc::champion_type::cassi || type == cambc::champion_type::issac;
        // Setup can leave too little for the rest of the turn (big_world: 161k of the first turn's 200k, pf12): that
        // turn ran out of fuel, resumed next round on its stale snapshot and acted on neither round. End it here; the
        // next turn starts with a full budget and a fresh snapshot. Setup itself runs into later rounds on 17 of 40 maps
        // (up to 310k on road_of_riches, pf16 probe); the first pick and route then cost 50-95k, so with 52-75k left the
        // turn ran out again and champions first acted at round 4 or 5 (pf14 probe, 8 maps): there require 80k.
        const bool spilled = static_cast<int>(cambc::round_number()) != init_round;
        if (cambc::fuel_remaining() < (spilled ? 80000u : 50000u)) return;
    }
    auto& me = cambc::self();
    const int round = static_cast<int>(cambc::round_number());
    tracing = false;
    log_rounds = false;

    // Status lines (tools/replay/acts.py reads the champion types), integers only. Printed every 20 rounds with floats
    // and strings, this cost about 13k fuel a champion, and 1.6% of those turns ran out of fuel against 0.17% of the
    // others (au10 audit).
    if (round % 100 == 0 || (!me.is_alive() && was_alive)) {
        std::cout << "R" << round << " s" << W.slot << " " << cambc::to_string(me.champion_name()) << " hp="
                  << static_cast<int>(me.health()) << "/" << static_cast<int>(me.max_health()) << " gems=" << me.gem_count()
                  << " gold=" << me.gold_count() << " tgt=" << current_target;
        if (me.is_alive()) std::cout << " pos=" << me.position().x << "," << me.position().y << '\n';
        else std::cout << " DEAD\n";
    }
    if (W.slot == 0 && round % 100 == 0)
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
        if (death_ctx.n > 0) death_rounds.push_back(round), add_death_mark(S.me);  // Camp deaths say nothing about enemy control.
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
    track_mate_deaths();
    update_knowledge();
    build_phantoms();
    read_broadcast();
    refresh_altar_field();
    record_sightings();
    record_death_ctx();
    // No call when three or more enemies stand within 6: helpers come from up to 14 tiles, one at a time, and feed the
    // pack. cw1 on four panels, to r1000 (`tools/replay/chain.py`): we die within 60 rounds and 8 tiles of a teammate's
    // death 2.16 times per game, the rivals 1.16; 19% of our later victims were 11+ tiles from the spot at the first death
    // (theirs 7%), and 2.7 enemies stood within 6 of it (1.8).
    {
        bool caught = false;
        int near = 0;
        for (const auto& e : S.enemies) {
            if (W.enemy_spawn.is_set(e.pos)) continue;
            if (dist(S.me, e.pos) <= 3) caught = true;
            if (dist(S.me, e.pos) <= 6) ++near;
        }
        write_help(caught && near < 3 && home_side(S.me) ? help_code(S.me) : 0);
    }
    // Stunned: no action is allowed this turn. Acting anyway threw "Champion cannot act" (recall, ward placement) and
    // aborted the turn.
    if (!S.can_act()) {
        ACT("stunned");
        last_hp = S.hp;
        last_round = round;
        return;
    }
    STAGE("enemies");
    place_ward_forward();
    {
        // The rivals' game-winning channel within 10 tiles: walk to its altar (the lock goes down once within 2),
        // hitting whoever is in reach on the way. The game is lost when that channel completes.
        vec2 to;
        const ChampSnap* carrier = nullptr;
        if (deny_channel(to, carrier) && dist(S.me, to) <= 10) {
            ACT("deny");
            walk_towards(to);
            for (const auto& e : S.enemies)
                if (!W.enemy_spawn.is_set(e.pos) && dist(S.me, e.pos) <= S.range && attack_unit(e.ch)) break;
            deny_channel(to, carrier);
            return;
        }
        // A rival carrying a game-winning bag within 6 tiles, walking or channelling: a stun or its death cancels the
        // channel (damage does not), and its killer takes the whole bag, so cast every stun at it and hit it (dl4).
        // deny.py on the cm3m and dl2 runs of b19p: one of ours within 6 of that carrier during its walk or channel in
        // 11 of 33 and 9 of 29 losses (within 4: 6 and 7).
        if (carrier && dist(S.me, carrier->pos) <= 6) {
            ACT("deny_hit");
            const ChampSnap c = *carrier;
            auto& self = cambc::self();
            if (self.can_cast() && c.ch.passive() != cambc::passive_type::stun_immunity)
                for (const auto& ab : self.abilities()) {
                    if (stale() || !castable_now(ab) || !ab.is_cc()) continue;
                    try {
                        if (ab.valid_tiles().is_set(c.pos) && (ab.can_target_ground() ? ab.use(c.pos) : ab.use(c.ch))) break;
                    } catch (const cambc::error&) {
                    }
                }
            if (!stale()) strike_dash({c.pos}, false);
            if (dist(S.me, c.pos) > S.range) walk_towards(c.pos);
            if (dist(S.me, c.pos) <= S.range && attack_unit(c.ch)) try_attack_reset_and_hit(c.ch);
            use_champion_abilities(c);
            return;
        }
    }
    const vec2 p = S.me;
    // Holding a capture: our target's camps are dead and we stand on one of its spawn tiles. The capture takes 5 rounds
    // and resets the round none of us stands there. On b9p (dq3, decoded) we stepped off before the capture 12.1 times
    // per game, the rivals 8.2 and the top 12 about 6; in the local probe cl0, re-picks and bank trips caused 3.4 of
    // those per game. Only the last of us on the tiles holds: with a teammate on one the capture goes on without us.
    // Hold for at most 8 rounds, in case the capture never comes.
    {
        const bool on = current_target >= 0 && W.groups[current_target].state == 1 && W.groups[current_target].tiles.is_set(p);
        bool shared = false;
        if (on)
            for (const auto& a : S.allies) if (W.groups[current_target].tiles.is_set(a.pos)) shared = true;
        if (!on) hold_since = -1;
        else if (hold_since < 0 || hold_group != current_target) hold_since = round, hold_group = current_target;
        S.holding = on && (!shared || split_capture(W.groups[current_target])) && round - hold_since < 8;
    }
    const bool at_spawn = W.ally_spawn.is_set(p);
    if (at_spawn) {
        shop();
        retreating = false;
    }

    // Damage not explained by camps comes from an enemy, possibly hidden in a bush. Our Jungle and Durability emblems
    // cut the camps' hits (guard_of): unscaled, a camp's 100 hid an enemy's 25 from a Jungle holder.
    const float incoming = camp_incoming(p) * guard_of(me).camp;
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
            if (g.state != 0 || in_view(pos) || dist(p, pos) > k.range) continue;
            g.awake_round = round;
            blamed = true;
        }
        if (!blamed) enemy_seen_round = enemy_seen_at = round;
    }
    // (A log line of every big hit was printed here: 37.6k fuel a line with its float formatting, about 5 times a game in
    // fights, so the rest of those turns often ran out of fuel (pf20 probe). Decoded replays show the same.)

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
    // champion damage actually taken since our last turn. Analysed by tools/calib.py. A basic attack carries the Heart
    // of Ruin bonus (casts report theirs), and our Durability emblem cuts both (guard_of).
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
            pred += (basic ? e.str * damage_scale(e.type, e.hp, e.max_hp) : 0.0f) + spell;
        }
        if (pred > 0) pred *= guard_of(me).mit;
        const float actual = std::max(0.0f, taken - incoming);
        if (prev_pred >= 0 && (prev_pred > 0 || actual > 0)) {
            cal_pred += prev_pred, cal_act += actual;
            cal_f = static_cast<float>(std::clamp((cal_act + 3000.0 * 0.18) / (cal_pred + 3000.0) / 0.18, 1.0, 2.0));
        }
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
    // Answer a team focus call on a visible enemy close enough to reach, unless our prey is already in attack reach: the
    // call pulled champions off an enemy they could hit to walk up to 8 tiles towards another.
    if (const auto* f = focus_target(); f && dist(p, f->pos) <= 8 && !W.enemy_spawn.is_set(f->pos)
        && !(prey && dist(p, prey->pos) <= S.range && dist(p, f->pos) > S.range))
        prey = f;
    for (const auto& a : S.allies)
        if (dist(p, a.pos) <= 5) ally_hp += a.hp, ally_dps += a.dps, ++ally_count;
    const float enemy_power = enemy_hp * enemy_dps, ally_power = ally_hp * ally_dps;

    // Enemies whose combined one-round burst could kill us from where they stand (after a step).
    float lethal = 0;
    for (const auto& e : S.enemies)
        if (!W.enemy_spawn.is_set(e.pos) && dist(p, e.pos) <= e.reach + 1) lethal += e.burst;
    const bool in_kill_range = lethal >= S.hp * 0.9f;
    // A capture is not worth the champion: inside kill range the hold ends and the usual threat rules apply.
    if (in_kill_range) S.holding = false;
    // Fight when stronger and not outnumbered, when the target is nearly dead, or from the safety of spawn.
    // Cassi and Issac die together, so they only join fights with a clear edge.
    // Play the fight out a few rounds with live cooldowns instead of comparing raw totals.
    bool winning = false, sim_me_dies = false;
    if (prey) {
        using ct = cambc::champion_type;
        // Buffers kept across turns: six vectors grown one unit at a time cost up to 24 allocations (about 400 fuel each)
        // per fight turn.
        static std::array<std::vector<SimUnit>, 2> side;
        static std::vector<vec2> pos[2];
        static std::vector<ct> types[2];
        for (int s = 0; s < 2; ++s) side[s].clear(), pos[s].clear(), types[s].clear();
        // A basic attack carries the Heart of Ruin bonus (casts report theirs); a unit's Durability emblem cuts what it
        // takes and its shield absorbs first (guard_of).
        auto add = [&](int s, const cambc::champion& c, float hp, float max_hp, float str, int range, vec2 at,
                       std::array<SimSlot, 2> slots, ct type) {
            const Guard g = guard_of(c);
            SimUnit x;
            x.hp = hp + g.shield, x.mit = g.mit, x.str = str * damage_scale(type, hp, max_hp), x.range = range, x.slots = slots;
            side[s].push_back(x);
            pos[s].push_back(at);
            types[s].push_back(type);
        };
        add(0, me, S.hp, S.max_hp, S.str, S.range, p, cached_slots(me), me.champion_name());
        for (const auto& a : S.allies)
            if (dist(p, a.pos) <= 8) add(0, a.ch, a.hp, a.max_hp, a.str, a.range, a.pos, cached_slots(a.ch), a.type);
        for (const auto& e : S.enemies)
            if (dist(p, e.pos) <= 8 && !(W.enemy_spawn.is_set(e.pos) && dist(p, e.pos) > e.range))
                {
                    auto sl = cached_slots(e.ch);
                    for (auto& x : sl) x.dmg *= cal_f;
                    add(1, e.ch, e.hp, e.max_hp, e.str * cal_f, e.range, e.pos, sl, e.type);
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
    // Kill races from sustained damage per round (engine metadata, the Heart of Ruin bonus included) with each side's
    // Durability and shield (guard_of): the rounds we need to kill `e`, and the rounds it needs to kill us.
    static const FightCoef my_coef = read_coef(me);
    const float mine = champion_dps(my_coef, S.str, me.focus()) * damage_scale(me.champion_name(), S.hp, S.max_hp);
    const auto race = [&](const ChampSnap& e, float& ours, float& theirs) {
        const Guard g = guard_of(e.ch), us = guard_of(me);
        ours = mine > 0 ? (e.hp + g.shield) / (mine * g.mit) : 1e9f;
        theirs = e.dps > 0 ? (S.hp + us.shield) / (e.dps * us.mit) : 1e9f;
    };
    // First strike in a lone 1v1 with a close kill race: being caught later means fleeing with free hits taken.
    if (prey && !winning && enemy_count == 1 && S.hp >= S.max_hp * 0.5f) {
        float ours, theirs;
        race(*prey, ours, theirs);
        if (mine > 0 && prey->dps > 0 && ours < 1.2f * theirs) winning = true;
    }
    const bool finisher = prey && prey->hp + guard_of(prey->ch).shield <= ally_dps * guard_of(prey->ch).mit * 2.5f
        && S.hp > S.max_hp * 0.3f && !sim_me_dies;
    // A carrier with a full bag is worth a risky fight: the kill takes all of it.
    const bool rich = prey && prey->gems >= 30 && ally_power >= enemy_power * 0.5f && S.hp > S.max_hp * 0.5f && !sim_me_dies;
    // A big bag is worth more banked than any fight: its carrier never engages, and a threat counts as a lost fight (it
    // kites or flees). The killer takes the whole bag. Rivals keep their carriers out of fights: per 1000 rounds alive
    // their champions with 60+ gems die 0.63 times and those with none 1.38 (b11p base, to r1000; b10 0.82 vs 1.35, the
    // top 12 0.79 vs 1.83); ours die 3.70 times with 60+ and 2.26 with none (b10 2.05 vs 1.92), with an enemy within 8
    // in 38% of those rounds against 26%. We lose 141 gems per game on death by r1000, they 33 (was 150: boss_battle
    // bags of 1446-3289 lost in fights).
    const bool big_bag = me.gem_count() >= 30;
    // The per-tile threat (micro.h): what the visible enemies can deal on our tile before our next turn, summed, from
    // their live cooldowns, doubled under a ready stun. A fight the simulation calls won is still not taken from a tile
    // where that would kill us, unless the prey is nearly dead.
    build_foes();
    const float threat_now = foes.empty() ? 0.0f : threat_at(p);
    // A prey in reach that our hit kills this turn deals nothing back.
    const float threat_fight = prey && dist(p, prey->pos) <= S.range && kills(*prey, false, true) ? threat_at(p, prey->pos) : threat_now;
    if (!big_bag && prey && (winning || finisher || rich || (at_spawn && dist(p, prey->pos) <= S.range))
        && (threat_fight < 0.9f * S.hp || finisher)) {
        STAGE("fight enemy");
        ACT("pvp");
        call_focus(*prey);
        // Favourable fight: focus the weakest enemy, spells first; an unused cast raises the shield. Not when the kill
        // needs the attack reset's second hit: the cast goes to the reset.
        const bool reset_kill = needs_reset_kill(*prey);
        if (!reset_kill) {
            use_champion_abilities(*prey);
            use_support_abilities(true);
        }
        // In reach: hit. A shooter under heavy threat then dashes out instead of the reset hit; melee steps to a safer
        // tile that keeps the prey in reach (micro.h).
        if (dist(S.me, prey->pos) <= S.range) {
            if (attack_unit(prey->ch)) {
                drop_foe(*prey);
                if (reset_kill || !micro_shot_dash()) try_attack_reset_and_hit(prey->ch);
            }
            micro_after_hit(*prey);
            return;
        }
        // A capturer does not chase off its tile: the prey comes into reach or the capture completes (local probe cl0:
        // 2.6 chases per game left a capture).
        if (S.holding) return;
        // Close in on the tile micro.h picks (a hit this turn when the threat there allows, else a safe step closer,
        // else stay); around a wall, walk the path while little threatens us.
        if (micro_close_in(*prey) < 0 && threat_now < 0.3f * S.hp && walk_towards(prey->pos) && dist(S.me, prey->pos) <= S.range
            && attack_unit(prey->ch))
            try_attack_reset_and_hit(prey->ch);
        return;
    }
    bool threatened = false;
    for (const auto& e : S.enemies)
        if (dist(p, e.pos) <= std::max(e.range + 2, e.dps > e.str * 1.15f ? 6 : 0) && !W.enemy_spawn.is_set(e.pos))
            threatened = true;
    const bool hit_by_enemy = taken > incoming + 1.0f;
    const bool losing = (sim_me_dies && !winning) || enemy_count > ally_count || enemy_power > ally_power * 0.9f || S.hp < S.max_hp * 0.4f
        || in_kill_range || big_bag;
    // Not engaging: from here on, moves keep out of enemy reach.
    S.avoid_danger = !S.danger.empty();
    // Also leave, while still healthy, a tile where the enemies can take 60% of our health before our next turn: our
    // deaths start in contacts at high health, and the victim has about one enemy more within 6 at the death than ten
    // rounds before (findings, "Stuns carry the death gap").
    if ((threatened && losing) || (hit_by_enemy && !prey) || threat_now >= 0.6f * S.hp) {
        // No rooting spell and no striking dash yet: the branch below may kite or flee, and a rooted champion cannot walk
        // this turn, nor walk home from where the dash lands (the duel casts everything). cw1 on four panels, to r1000
        // (scratch castrisk.py): our Marcella cast her rooting spell while outnumbered or under 40% health 4.2 times per
        // game, and died within 10 rounds after 23% of those casts against 16% of her other rounds there; the rivals'
        // Marcella 2.3 times, 11% against 12%.
        if (prey) use_champion_abilities(*prey, false);
        const bool healthy = S.hp >= S.max_hp * 0.5f && !hit_by_enemy;
        // A healthy capturer holds its tile too, until a hit lands: stepping away resets the capture, and the enemy
        // then takes the group (b9p, dq3 decoded: 2.6 holds per game left with an enemy 5-8 tiles away, the rivals 1.2).
        if (healthy && (S.holding || threat_now < 0.25f * S.hp)) {
            // Already out of reach: keep working, staying out of it.
        } else if (healthy && [&] {
                       // Hit before stepping away when the hit is free: melee keeps its move after attacking, and a target
                       // that cannot reach us cannot answer (b5 ge4: with an enemy within 3 the rivals hit a champion in
                       // 50% of rounds, we in 35%, and stand idle 12% vs 6%).
                       // Not for a shooter: its shot costs the step, so it stayed in danger and the melee enemy stepped in.
                       // It steps out first and shoots with the attack reset. rz12 on b13p2, b16p and b17p, five a side, to
                       // r1000 (`tools/replay/contacts.py`): our Vesper began a contact while short 2.11 times per game, the
                       // rivals' 1.10, and 0.97 of ours (theirs 0.34) came right after her shot from 2 tiles; she died within
                       // 10 rounds after 0.28 of her contacts (theirs 0.22).
                       if (S.range > 1) return micro_kite(true);
                       const ChampSnap* t = nullptr;
                       for (const auto& e : S.enemies)
                           if (!W.enemy_spawn.is_set(e.pos) && dist(S.me, e.pos) <= S.range && (S.range <= 1 || dist(S.me, e.pos) > e.range)
                               && (!t || e.hp < t->hp)) t = &e;
                       if (t && attack_unit(t->ch)) try_attack_reset_and_hit(t->ch);
                       return micro_kite(false);
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
                float ours, theirs;
                race(*chaser, ours, theirs);
                we_kill_first = mine > 0 && chaser->dps > 0 && ours < theirs;
                // A melee chaser keeps adjacent and hits every round of the run home; when that run is fatal anyway
                // and the kill race is close, trading blows beats taking free hits (platform traces: 440 of 538
                // deaths start as a 1v1 at full health and end fleeing).
                const bool futile = chaser->range <= 1 && theirs <= W.spawn_field.get(p);
                turn_and_fight = futile && mine > 0 && chaser->dps > 0 && ours < 1.5f * theirs;
            }
            if (chaser && near_enemies == 1 && W.spawn_field.get(p) > 4 && (we_kill_first || turn_and_fight)) {
                ACT("duel");
                if (!needs_reset_kill(*chaser)) use_champion_abilities(*chaser);
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
            if (!at_spawn && micro_flee_dash()) ACT("flee_dash");
            if (!at_spawn && !flee_bush() && !micro_flee_step()) walk_home(true);
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
            // Ranged champions also shoot when hurt unless the enemies near can burst them this round: our Vespers hit in
            // 41% of rounds with an enemy in range, the rivals' 53% (b6 decoded).
            const auto may_hit = [&] {
                const int d = dist(S.me, t->pos);
                return d <= S.range && (S.range <= 1 || S.hp > S.max_hp * 0.5f || d > t->range || !in_kill_range);
            };
            // A kill that needs the attack reset's second hit keeps the cast for it.
            if (!(may_hit() && needs_reset_kill(*t))) use_champion_abilities(*t);
            // Vendetta closes in and hits the same round: with an enemy 2-3 tiles away the rivals' Vendettas hit a
            // champion in 26% of rounds, ours in 16% (b6 decoded). Only when the fight is not lost (we are past the flee
            // branch) and the simulation does not say we die. At 2 tiles a step does it and keeps the cast for the reset
            // (two hits); cp3 dashed there too, spending the cast on a one-hit turn. At 3 tiles only the dash reaches.
            if (me.champion_name() == cambc::champion_type::vendetta && !sim_me_dies && me.can_attack() && !S.holding) {
                if (dist(S.me, t->pos) == 2) step_next_to(*t);
                else if (dist(S.me, t->pos) == 3) dash_next_to(*t);
            }
            if (may_hit() && attack_unit(t->ch)) try_attack_reset_and_hit(t->ch);
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
    bool in_camp_range = false, passing = false;
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
        if (c.group != current_target) passing = true;
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
    // Camps of another group hit us while we walk past them to our target, and this turn's walk can take us one tile
    // deeper: count one more round of their hits. The bf4 audit traced camp deaths to this (00fragment: at 300 health
    // in reach of two elks, 120 a round, the walk to a capture went deeper and three retreat steps never left reach).
    const float extra = passing ? danger : 0.0f;
    if ((danger > 0 || lethal > 0) && S.hp < danger * (steps_out + 1.0f) + extra + lethal + (quiet ? 15.0f : 40.0f)) retreating = true;
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
        const double batch = std::sqrt(2.0 * 2.0 * c * c * tau / (m * h + lambda * c / 5.0));
        if ((gems >= batch && S.round >= bank_blocked_until && !S.holding) || endgame) {
            // Give up for a while if the way to the altar makes no progress (blocked or contested).
            // Waiting at a hole edge for the dash is not a blocked way (dh1).
            // In tribute range the walk is done: hitting an enemy lock (5 hits) or waiting to channel is progress, so the
            // give-up comes much later there (lk1; ranked 01boss_battle: our Marcella hit the lock on the only open altar
            // tile 4 times, gave up and left; wk panel: 10 of 20 boss_battle games and 7 of 20 on 02guardians without a
            // tribute, 150 lock breaks in 100 games ended short).
            bool at_altar = false;
            for (auto a : W.altars) if (dist(p, a) <= cambc::constants::submit_gems_range) at_altar = true;
            if (altar_d < bank_best) bank_best = altar_d, bank_stall = 0;
            else if (!hole_ahead(W.altar_field, altar_d) && ++bank_stall > (at_altar ? 25 : 6))
                bank_blocked_until = S.round + 40, bank_best = UNREACH, bank_stall = 0;
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
    if (!at_spawn && incoming == 0 && round < 1850 && !remote_shop && !S.holding) {
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
            walk_towards(h);
            return;
        }
    }
    STAGE("pick");
    // Keep fighting an awake target; one champion captures; the rest follow the team target.
    const bool in_fight = current_target >= 0 && W.groups[current_target].state == 0
        && !camp_threats(p, 1).empty();
    // Re-plan every few rounds, or at once when the target's state changes.
    const int target_state = current_target >= 0 ? W.groups[current_target].state : -1;
    // A pick costs 35-45k fuel on big maps (bf6 profile: the scoring loop alone 36-41k on big_world and
    // yellow_brick_road), plus a full search from us until every travel field exists: with less left the turn would
    // run out and resume next round on a stale snapshot, so keep the target one more turn (a dead or missing target
    // still needs the pick).
    // (A guard from the largest measured pick plus a forced pick every 10 rounds was tried: later exhaustions on four
    // heavy maps rose from 133 to 286, big_world from 1 to 75 per game.)
    const std::uint64_t pick_cost = 45000 + (travel_ready() ? 0 : field_cost);
    const bool can_pick = cambc::fuel_remaining() > pick_cost || current_target < 0;
    // The target changed state (taken, captured, back up) but this turn has no fuel for a pick: drop it for this turn
    // rather than walk on to it (bf7 audit: 228 walks to a reward whose tiles a teammate already held). A missing
    // target may always pick, so the next turn picks.
    // A held capture keeps its target: it ends within 5 rounds, and every re-pick scored it against the next target as if
    // one excluded the other.
    if (!in_fight && !can_pick && !S.holding && current_target >= 0 && target_state != last_pick_state) {
        current_target = -1;
        last_pick_state = -1;
    }
    if (!in_fight && can_pick && !S.holding && (S.round - last_pick_round >= 3 || target_state != last_pick_state)) {
        current_target = pick_group(current_target);
        last_pick_round = S.round;
        last_pick_state = current_target >= 0 ? W.groups[current_target].state : -1;
    } else {
        // Build travel fields while this turn has room for one more at its measured cost (until all exist, picks run
        // a full search from us instead).
        while (!travel_ready() && cambc::fuel_remaining() > field_cost + 30000) build_travel_field();
    }
    write_claim(current_target);
    if (group_invested.empty()) group_invested.assign(W.groups.size(), 0);
    for (size_t i = 0; i < W.groups.size(); ++i) if (W.groups[i].state != 0) group_invested[i] = 0;
    if (current_target >= 0 && W.groups[current_target].state == 0) ++group_invested[current_target];
    // A camp fight that starts with little fuel runs out (pf14 probe, rounds 1-40: 28 of 43 that started under 15k,
    // 15 of 156 at 15-24k, 2 of 11,600 from 25k up): end the turn instead, the next one has the budget (a turn that
    // runs out loses the next round to its stale rest as well).
    if (current_target >= 0 && cambc::fuel_remaining() < 15000) return;
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
