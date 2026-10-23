// Mechanics test 2: (a) Ren casts its rooting stun, then tries to dash and to walk in the same turn;
// (b) Heart of Ruin captures a gold-cluster group, stands on a spawn tile and logs the group's respawn timer.
#include <cambc.h>
#include "bot.h"
#include <iostream>

namespace {
using namespace cambc;
int dist(vec2 a, vec2 b) { return static_cast<int>(a.chebyshev_distance(b)); }
int ren_done = 1, hor_phase = 0, hor_gi = -1, stay_until = 0;
vec2 hor_tile{-1, -1};

int group_state(const map::camp_group& g, int& timer) {
    std::uint32_t s = 0;
    timer = -1;
    if (detail::sdk_camp_group_state(static_cast<std::uint32_t>(static_cast<handle_camp_group_t>(g)), &s) != 0) return -1;
    detail::sdk_camp_group_cooldown(static_cast<std::uint32_t>(static_cast<handle_camp_group_t>(g)), &timer);
    return static_cast<int>(s);
}

void ren_turn(int round) {
    auto& me = self();
    const vec2 p = me.position();
    if (ren_done) return;
    // Nearest wolf.
    vec2 w{-1, -1};
    for (const auto& g : map::camp_groups())
        for (const auto& c : g.camps())
            if (c.kind() == camp_type::wolf && (w.x < 0 || dist(c.spawn_position(), p) < dist(w, p))) w = c.spawn_position();
    if (dist(p, w) > 4) { me.move_towards(w); return; }
    for (const auto& c : vision::camps()) {
        if (c.position() != w) continue;
        auto ab = me.abilities();
        bool cast = false;
        try { cast = ab[0].use(c); } catch (const error& e) { std::cout << "REN cast error " << e.what() << '\n'; }
        std::cout << "REN " << round << " cast_stun=" << cast << " can_move=" << me.can_move() << " can_cast=" << me.can_cast() << '\n';
        bool dashed = false;
        try {
            for (auto t : ab[1].valid_tiles().positions()) { dashed = ab[1].use(t); break; }
        } catch (const error& e) { std::cout << "REN dash error " << e.what() << '\n'; }
        bool walked = false;
        try { walked = me.move_towards(map::spawn_region(team::ally).positions()[0]); } catch (const error& e) { std::cout << "REN walk error " << e.what() << '\n'; }
        std::cout << "REN " << round << " dash_after_cast=" << dashed << " walk_after_cast=" << walked << '\n';
        ren_done = 1;
        return;
    }
}

void hor_turn(int round) {
    auto& me = self();
    const vec2 p = me.position();
    const auto groups = map::camp_groups();
    if (hor_gi < 0) {
        int best = 999;
        for (int i = 0; i < static_cast<int>(groups.size()); ++i) {
            bool only_gold = true;
            for (const auto& c : groups[i].camps()) if (c.kind() != camp_type::gold_cluster) only_gold = false;
            const int d = dist(groups[i].camps()[0].spawn_position(), p);
            if (only_gold && d < best) best = d, hor_gi = i;
        }
        hor_tile = groups[hor_gi].camps()[0].spawn_position();
    }
    const auto& g = groups[hor_gi];
    int timer = -1;
    const int st = group_state(g, timer);
    std::cout << "H " << round << " phase=" << hor_phase << " pos=" << p.x << "," << p.y << " gold=" << me.gold_count()
              << " group_state=" << st << " timer=" << timer << " hp=" << me.health();
    for (const auto& c : vision::camps()) {
        try { if (c.is_awake()) std::cout << " awake:" << to_string(c.kind()) << "@" << dist(c.position(), p); } catch (const error&) {}
    }
    for (const auto& e : champions(team::enemy)) {
        try { if (e.is_alive()) std::cout << " enemy:" << to_string(e.champion_name()) << "@" << dist(e.position(), p); } catch (const error&) {}
    }
    std::cout << '\n';
    if (hor_phase == 0) {
        // Kill every cluster, then stand on the first spawn tile.
        for (const auto& c : vision::camps())
            if (c.camp_group() == g && c.is_alive()) {
                if (dist(p, c.position()) > 1) { me.move_towards(c.position()); return; }
                me.attack(c);
                return;
            }
        if (p != hor_tile) { me.move_towards(hor_tile); return; }
        if (st == 3) { hor_phase = 1; stay_until = round + 70; std::cout << "CAPTURED " << round << '\n'; }
    } else if (hor_phase == 1) {
        if (round >= stay_until) { hor_phase = 2; std::cout << "LEAVE " << round << '\n'; }
    } else if (hor_phase == 2) {
        if (dist(p, hor_tile) < 3) {
            for (auto d : {vec2{1, 0}, vec2{0, 1}, vec2{-1, 0}, vec2{0, -1}, vec2{1, 1}, vec2{-1, -1}})
                if (me.move(d)) return;
        }
    }
}
}  // namespace

void Bot::play_turn() {
    auto& me = self();
    const int round = static_cast<int>(round_number());
    if (round > 260 || !me.is_alive()) return;
    if (me.champion_name() == champion_type::ren) ren_turn(round);
    if (me.champion_name() == champion_type::heart_of_ruin) hor_turn(round);
}
