// Dispatch draft and gameplay; a failed turn is logged and still yields.
// One program, three bots, picked once by team size: three a side this bot (vx1), four a side bamboo458sf (src/bb,
// namespace bbt, with its free-list allocator switched on), five a side bot_10 with its log off (src/cj, namespace cjb).
#include <cambc.h>
#include <iostream>
#include "bot.h"
#include "draft.h"
#include "fastalloc_switch.h"

namespace cjb { int run(); }
namespace bbt { int run(); }

// Champions per team. The draft API knows it; a program that starts after the draft counts its team.
static unsigned team_n() {
    try { return cambc::draft::team_size(); } catch (...) {}
    try { return static_cast<unsigned>(cambc::champions(cambc::team::ally).size()); } catch (...) {}
    return 5;
}

int main() {
    const unsigned n = team_n();
    if (n == 4) {
        fastalloc::on = true;
        return bbt::run();
    }
    if (n != 3) return cjb::run();
    Bot bot;
    while (true) {
        try {
            if (cambc::is_draft())
                play_draft();
            else
                bot.play_turn();
        } catch (const std::exception& error) {
            std::cout << "bot error: " << error.what() << " at " << bot_stage << std::endl;
        } catch (...) {
            std::cout << "bot error: unknown exception" << std::endl;
        }

        cambc::end_turn();
    }
}
