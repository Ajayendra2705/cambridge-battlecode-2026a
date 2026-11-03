#include <cambc.h>
#include <cstdio>
#include "bot.h"
#include "common.h"
#include "draft.h"
namespace cjb {
// Dispatch draft and gameplay; a failed turn is logged and still yields.

int run() {
    static Bot bot;
    while (true) {
        try {
            if (cambc::is_draft())
                play_draft();
            else
                bot.play_turn();
        } catch (const std::exception& error) {
            std::printf("bot error: %s\n", error.what());
        } catch (...) {
            std::printf("bot error: unknown\n");
        }
        if (cambc::fuel_remaining() >= 1500) LOGC_FLUSH();  // edit_vtfuel.py: else next turn (a flush must not cost a turn)
        cambc::end_turn();
    }
}
}  // namespace cjb
