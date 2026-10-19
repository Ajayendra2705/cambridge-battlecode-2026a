// Experiment: discover the bit order of bitboard::export_linear_buffer and the fuel cost of host calls.
#include <cambc.h>
#include "bot.h"
#include <iostream>

void Bot::play_turn() {
    static bool done = false;
    if (done) return;
    done = true;
    const int w = cambc::map::width(), h = cambc::map::height();
    std::cout << "W " << w << " H " << h << " linear " << cambc::bitboard::linear_buffer_size()
              << " field " << cambc::distance_field::linear_buffer_size() << '\n';
    for (cambc::vec2 p : {cambc::vec2{0, 0}, cambc::vec2{1, 0}, cambc::vec2{0, 1}, cambc::vec2{9, 3}}) {
        cambc::bitboard b;
        b.clear();
        b.set(p);
        const auto bytes = b.export_linear_buffer();
        for (size_t i = 0; i < bytes.size(); ++i)
            for (int bit = 0; bit < 8; ++bit)
                if (bytes[i] >> bit & 1) std::cout << "set " << cambc::to_string(p) << " -> bit " << i * 8 + bit << '\n';
    }
    cambc::distance_field f;
    cambc::bitboard roots, visited, walls;
    roots.clear();
    walls.clear();
    roots.set({0, 0});
    f.compute(walls, roots, visited);
    const auto vals = f.export_linear_buffer();
    std::cout << "field size " << vals.size() << " at(3,2)=" << f.get({3, 2}) << " lin[2*w+3]=" << vals[2 * w + 3] << '\n';
    auto f0 = cambc::fuel_remaining();
    int sum = 0;
    for (int i = 0; i < 100; ++i) sum += walls.is_set({i % w, 0});
    auto f1 = cambc::fuel_remaining();
    for (int i = 0; i < 100; ++i) sum += f.get({i % w, 0});
    auto f2 = cambc::fuel_remaining();
    for (int i = 0; i < 100; ++i) sum += vals[i % w];
    auto f3 = cambc::fuel_remaining();
    std::cout << "100x is_set=" << f0 - f1 << " 100x get=" << f1 - f2 << " 100x local=" << f2 - f3 << " " << sum << '\n';
}
