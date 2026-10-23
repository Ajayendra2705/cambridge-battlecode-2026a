#include <cambc.h>
#include "bot.h"
#include <algorithm>
#include <iostream>
// Probe: on the first turn, print every camp group (handle, gems, gold, camps, total health and strength, largest
// strength and attack range, centre, Chebyshev distance from our and the enemy spawn centre).
void Bot::play_turn() {
    static bool done = false;
    if (done) return;
    done = true;
    auto centre = [](const cambc::bitboard& b) {
        long sx = 0, sy = 0, n = 0;
        for (auto p : b.positions()) sx += p.x, sy += p.y, ++n;
        return n ? cambc::vec2{static_cast<int>(sx / n), static_cast<int>(sy / n)} : cambc::vec2{0, 0};
    };
    const auto ally = centre(cambc::map::spawn_region(cambc::team::ally));
    const auto enemy = centre(cambc::map::spawn_region(cambc::team::enemy));
    for (const auto& g : cambc::map::camp_groups()) {
        float hp = 0, str = 0, mx = 0; int rng = 0, n = 0; long sx = 0, sy = 0;
        std::string kinds;
        for (const auto& c : g.camps()) {
            const auto s = c.base_stats();
            hp += s.base_health; str += s.base_strength; mx = std::max(mx, s.base_strength); rng = std::max(rng, s.base_attack_range);
            const auto p = c.spawn_position(); sx += p.x; sy += p.y; ++n;
            kinds += std::to_string(static_cast<int>(c.kind()));
        }
        const cambc::vec2 cc{static_cast<int>(sx / std::max(1, n)), static_cast<int>(sy / std::max(1, n))};
        std::cout << "GRP " << static_cast<std::uint32_t>(static_cast<cambc::handle_camp_group_t>(g)) << " " << g.gem_value() << " " << g.gold_value()
                  << " " << n << " " << hp << " " << str << " " << mx << " " << rng << " k" << kinds << " " << cc.x << " " << cc.y
                  << " " << cc.chebyshev_distance(ally) << " " << cc.chebyshev_distance(enemy) << "\n";
    }
}
