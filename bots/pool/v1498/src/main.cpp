// Dispatch draft and gameplay; a failed turn is logged and still yields.
#include <cambc.h>
#include <cstdio>
#include "bot.h"
#include "common.h"
#include "draft.h"

int main() {
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
        LOGC_FLUSH();
        cambc::end_turn();
    }
}
