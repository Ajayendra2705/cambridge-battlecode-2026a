// Mechanics test 1: (a) order of our champions within each round; (b) wolf hits per round on a champion standing
// in range after one hit wakes the group, and whether the group sleeps 2 rounds after the champion leaves.
#include <cambc.h>
#include "bot.h"
#include <iostream>
#include <span>

namespace {
using namespace cambc;
int phase = 0, phase_round = 0;
float last_hp = -1;
vec2 wolf_pos{-1, -1};

int dist(vec2 a, vec2 b) { return static_cast<int>(a.chebyshev_distance(b)); }

void log_order(int round) {
    std::array<std::byte, 2> b{};
    shared_memory.read(0, std::span{b});
    int seq = static_cast<int>(b[0]);
    if (static_cast<int>(b[1]) != (round & 0xff)) seq = 0;
    b[0] = static_cast<std::byte>(seq + 1);
    b[1] = static_cast<std::byte>(round & 0xff);
    shared_memory.write(0, std::span{b});
    std::cout << "O " << round << " " << to_string(self().champion_name()) << " seq=" << seq << '\n';
}
}  // namespace

void Bot::play_turn() {
    auto& me = self();
    const int round = static_cast<int>(round_number());
    if (round > 200) return;
    log_order(round);
    if (me.champion_name() != champion_type::heart_of_ruin || !me.is_alive()) return;
    const vec2 p = me.position();
    const float hp = me.health();
    const float taken = last_hp < 0 ? 0 : last_hp - hp;
    last_hp = hp;
    // Wolves in view and their states.
    int awake = 0, asleep = 0, inrange = 0;
    for (const auto& c : vision::camps()) {
        if (c.kind() != camp_type::wolf) continue;
        try {
            if (c.is_awake()) ++awake; else if (c.is_asleep()) ++asleep;
            if (c.is_alive() && dist(c.position(), p) <= 3) ++inrange;
        } catch (const error&) {
        }
    }
    std::cout << "T " << round << " phase=" << phase << " pos=" << p.x << "," << p.y << " hp=" << hp << " taken=" << taken
              << " wolves_awake=" << awake << " asleep=" << asleep << " in_range=" << inrange << '\n';
    if (phase == 0) {
        // Walk to the nearest wolf seen; once adjacent hit it once.
        if (wolf_pos.x < 0)
            for (const auto& g : map::camp_groups())
                for (const auto& c : g.camps())
                    if (c.kind() == camp_type::wolf && (wolf_pos.x < 0 || dist(c.spawn_position(), p) < dist(wolf_pos, p)))
                        wolf_pos = c.spawn_position();
        if (dist(p, wolf_pos) > 1) { me.move_towards(wolf_pos); return; }
        for (const auto& c : vision::camps())
            if (c.position() == wolf_pos) {
                me.attack(c);
                phase = 1, phase_round = round;
                std::cout << "HIT " << round << '\n';
                return;
            }
    } else if (phase == 1) {
        if (round - phase_round >= 12) phase = 2, phase_round = round;  // stand still 12 rounds, no attacks
    } else if (phase == 2) {
        if (inrange > 0 || dist(p, wolf_pos) <= 5) { me.move_towards(map::spawn_region(team::ally).positions()[0]); return; }
        std::cout << "OUT " << round << '\n';
        phase = 3, phase_round = round;
    } else if (phase == 3) {
        if (round - phase_round >= 4) phase = 4, phase_round = round;  // wait 4 rounds out of range
    } else if (phase == 4) {
        if (dist(p, wolf_pos) > 2) me.move_towards(wolf_pos);  // walk back into range, no attack
    }
}
