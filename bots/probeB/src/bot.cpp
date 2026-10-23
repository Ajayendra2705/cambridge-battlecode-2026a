#include <cambc.h>
#include "bot.h"
#include <iostream>
#include <variant>
// Probe: print own base stats and ability metadata once, then idle.
void Bot::play_turn() {
    static bool done = false;
    if (done) return;
    done = true;
    auto& me = cambc::self();
    std::cout << "STAT " << cambc::to_string(me.champion_name()) << " hp=" << me.max_health() << " str=" << me.strength()
              << " foc=" << me.focus() << " range=" << me.attack_range();
    for (const auto& ab : me.abilities()) {
        if (!ab.info()) continue;
        std::visit([&](const auto& a) {
            std::cout << " | kind=" << static_cast<int>(a.kind) << " cd=" << a.max_cooldown;
            if constexpr (requires { a.modifier; }) std::cout << " mod=" << a.modifier;
            if constexpr (requires { a.range; }) std::cout << " rng=" << a.range;
            if constexpr (requires { a.radius; }) std::cout << " rad=" << a.radius;
            if constexpr (requires { a.duration; }) std::cout << " dur=" << a.duration;
        }, *ab.info());
    }
    std::cout << '\n';
}
