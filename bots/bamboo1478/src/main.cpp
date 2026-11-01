// Dispatch draft and gameplay; a failed turn is logged and still yields.
#include <cambc.h>
#include <iostream>
#include "bot.h"
#include "draft.h"

// Replace every new/delete with fastalloc.h's free lists (wasi-libc malloc/free cost 200-385 fuel a pair). 0: libc.
#define BAMBOO_FAST_ALLOC 1
#if BAMBOO_FAST_ALLOC
#include "fastalloc.h"
#endif

namespace cjb { int run(); }  // edit_hybrid.py: the teammates' bot_10 (src/cj)
bool hybrid_use_b10();         // kHybridWalk (bot.cpp)

int main() {
    if (hybrid_use_b10()) return cjb::run();  // kHybridWalk: far-spawn maps go to bot_10, draft included
    Bot bot;
    while (true) {
        try {
            if (cambc::is_draft())
                play_draft();
            else
                bot.play_turn();
        } catch (const std::exception& error) {
            std::cout << "bot error: " << error.what() << std::endl;
        } catch (...) {
            std::cout << "bot error: unknown exception" << std::endl;
        }

        cambc::end_turn();
    }
}
