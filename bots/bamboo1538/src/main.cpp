// Per-map router: one program, two bots, picked once per game from a map signature read before the draft (six SDK counts, cheap, the
// same for both sides on these symmetric maps). The maps in kBambooMaps play the Bamboo bot (src/bb, namespace bbt, platform 1472: Bamboo #458
// + spell finisher, with its free-list allocator on, as it runs alone); every other map, unseen maps too, plays v1503 (src/cj, namespace cjb,
// the teammate's v606). Table: tools/platform/mapstrat.py (the Bamboo line against the bot_10 line within the same opponent) and the pinned
// panel b1p (results/analysis/rule_route2.md). Signatures: tools/local/mapsig.py (data/map_sigs.json).
#include <cambc.h>
#include "fastalloc_switch.h"

namespace cjb { int run(); }
namespace bbt { int run(); }

namespace {
struct MapSig { short w, h, walls, holes, altars, bushes; };

// w, h, walls, holes, altars, bushes
constexpr MapSig kBambooMaps[] = {
    {40, 40, 76, 16, 4, 38},  // 00interlock
    {30, 30, 24, 320, 2, 24},  // 00fragment
    {31, 31, 18, 50, 1, 44},  // adgato_gemcombat1
    {51, 51, 186, 10, 3, 210},  // 02crossing
    {71, 71, 44, 84, 5, 60},  // 00corners
    {37, 31, 134, 12, 1, 40},  // 00anvil
    {79, 79, 1082, 10, 2, 252},  // 00dunes
    {51, 40, 378, 30, 2, 144},  // 01corridors
    {45, 45, 204, 0, 4, 104},  // 00quadrants
    {29, 29, 0, 310, 1, 70},  // 00breadcrumbs
    {35, 35, 114, 109, 4, 28},  // 03shrines
    {50, 50, 40, 0, 2, 26},  // 00contest
    {40, 40, 274, 0, 4, 68},  // 01broken_curve
    {41, 30, 36, 22, 1, 24},  // 00eight
    {31, 31, 114, 4, 2, 38},  // 00vault
    {45, 45, 23, 0, 4, 152},  // 02gift_wrapping
    {50, 46, 0, 1186, 4, 216},  // 02uncharted_lands
    {41, 41, 198, 264, 1, 28},  // 03fan
    {30, 30, 38, 224, 2, 96},  // 02the_pond
    {50, 40, 148, 0, 6, 76},  // 01the_farm
    {31, 31, 0, 0, 6, 62},  // 00packs
    {51, 51, 0, 0, 3, 612},  // 02fields
};

bool bamboo_map() {
    const int w = cambc::map::width(), h = cambc::map::height();
    const int walls = static_cast<int>(cambc::map::walls().count()), holes = static_cast<int>(cambc::map::holes().count());
    const int altars = static_cast<int>(cambc::map::altars().count()), bushes = static_cast<int>(cambc::map::bushes().count());
    for (const MapSig& m : kBambooMaps)
        if (m.w == w && m.h == h && m.walls == walls && m.holes == holes && m.altars == altars && m.bushes == bushes) return true;
    return false;
}
}  // namespace

int main() {
    if (!bamboo_map()) return cjb::run();
    fastalloc::on = true;
    return bbt::run();
}
