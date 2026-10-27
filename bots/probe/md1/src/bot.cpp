// Map dump probe: the lowest-handle champion of team A prints the whole map once as text rows, then every champion idles.
// Legend: . floor, # wall, o hole, , bush, A altar, S our (team A) spawn, s enemy spawn; camps: w wolf, E elk,
// g gem cluster, $ gold cluster, M monolith, G golem.
#include <cambc.h>
#include <iostream>
#include <string>
#include <vector>
#include "bot.h"

void Bot::play_turn() {
    static bool done = false;
    if (done) return;
    done = true;
    auto& me = cambc::self();
    std::uint32_t lowest = ~0u;
    for (const auto& a : cambc::champions(cambc::team::ally))
        lowest = std::min(lowest, static_cast<std::uint32_t>(static_cast<cambc::handle_champion_t>(a)));
    if (static_cast<std::uint32_t>(static_cast<cambc::handle_champion_t>(me)) != lowest) return;
    namespace cm = cambc::map;
    const int w = cm::width(), h = cm::height();
    std::vector<std::string> g(h, std::string(w, '.'));
    for (int y = 0; y < h; ++y)
        for (int x = 0; x < w; ++x) {
            const cambc::vec2 p{x, y};
            if (cm::walls().is_set(p)) g[y][x] = '#';
            else if (cm::holes().is_set(p)) g[y][x] = 'o';
            else if (cm::altars().is_set(p)) g[y][x] = 'A';
            else if (cm::spawn_region(cambc::team::ally).is_set(p)) g[y][x] = 'S';
            else if (cm::spawn_region(cambc::team::enemy).is_set(p)) g[y][x] = 's';
            else if (cm::bushes().is_set(p)) g[y][x] = ',';
        }
    int gi = 0;
    for (const auto& group : cm::camp_groups()) {
        std::cout << "GROUP " << gi++ << " gems=" << group.gem_value() << " gold=" << group.gold_value() << " respawn=" << group.max_respawn_timer() << '\n';
        for (const auto& c : group.camps()) {
            const auto p = c.spawn_position();
            const char k[] = {'w', 'E', 'g', '$', 'M', 'G'};
            g[p.y][p.x] = k[static_cast<int>(c.kind())];
        }
    }
    std::cout << "MAPDUMP " << w << " " << h << " " << cambc::to_string(cm::symmetry()) << '\n';
    for (int y = 0; y < h; ++y) std::cout << "ROW " << y << " " << g[y] << '\n';
    std::cout << "MAPEND" << std::endl;
}
