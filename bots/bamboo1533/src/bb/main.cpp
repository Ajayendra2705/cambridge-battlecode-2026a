#include <cambc.h>
#include <iostream>
#include "bot.h"
#include "draft.h"
namespace bbt {
// Dispatch draft and gameplay; a failed turn is logged and still yields.

// Replace every new/delete with fastalloc.h's free lists (wasi-libc malloc/free cost 200-385 fuel a pair). 0: libc.
#define BAMBOO_FAST_ALLOC 1
#if BAMBOO_FAST_ALLOC
#endif

int run() {
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
}  // namespace bbt
