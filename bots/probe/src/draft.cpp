#include <cambc.h>
#include "draft.h"
#include <algorithm>
#include <iostream>
#include <vector>

// Print map summary once, then pick the lowest-index free champion.
void play_draft() {
    static bool printed = false;
    if (!printed) {
        printed = true;
        namespace m = cambc::map;
        std::cout << "MAP " << m::width() << "x" << m::height() << " team_size=" << cambc::draft::team_size()
                  << " sym=" << cambc::to_string(m::symmetry()) << " walls=" << m::walls().count()
                  << " holes=" << m::holes().count() << " bushes=" << m::bushes().count() << "\n";
        auto spawn = m::spawn_region(cambc::team::ally).positions();
        auto espawn = m::spawn_region(cambc::team::enemy).positions();
        std::cout << "SPAWN " << cambc::to_string(spawn[0]) << " n=" << spawn.size() << " ENEMY " << cambc::to_string(espawn[0]) << "\n";
        std::cout << "ALTARS";
        for (auto a : m::altars().positions()) std::cout << " " << cambc::to_string(a);
        std::cout << "\n";
        auto blocked = m::walls() | m::holes() | m::altars();
        cambc::distance_field field;
        cambc::bitboard visited, roots;
        roots.clear();
        roots.set(spawn[0]);
        field.compute(blocked, roots, visited);
        for (const auto& g : m::camp_groups()) {
            std::cout << "GROUP gems=" << g.gem_value() << " gold=" << g.gold_value() << " resp=" << g.max_respawn_timer()
                      << " camps=";
            for (const auto& c : g.camps()) std::cout << cambc::to_string(c.kind()) << "@" << cambc::to_string(c.spawn_position()) << ",";
            std::cout << " dist=" << field.get(g.camps()[0].spawn_position()) << "\n";
        }
        std::cout << "FUEL " << cambc::fuel_remaining() << "\n";
    }
    const auto chosen = cambc::draft::current_draft(cambc::team::ally);
    for (int i = 0; i < 11; ++i) {
        auto pick = static_cast<cambc::champion_draft>(i);
        if (std::find(chosen.begin(), chosen.end(), pick) == chosen.end()) {
            cambc::draft::pick(pick);
            return;
        }
    }
}
