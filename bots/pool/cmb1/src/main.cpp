// Dispatch draft and gameplay; a failed turn is logged and still yields.
// Three a side this bot plays; four and five a side the teammate's bot in src/cj (namespace cjb) plays.
#include <cambc.h>
#include <iostream>
#include "bot.h"
#include "draft.h"

namespace cjb { int run(); }

// Champions per team. The draft API knows it; a program that starts after the draft counts its team.
static unsigned team_n() {
    try { return cambc::draft::team_size(); } catch (...) {}
    try { return static_cast<unsigned>(cambc::champions(cambc::team::ally).size()); } catch (...) {}
    return 5;
}

int main() {
    if (team_n() != 3) return cjb::run();
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
