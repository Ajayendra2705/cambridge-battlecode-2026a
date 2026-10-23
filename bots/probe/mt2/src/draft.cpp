#include <cambc.h>
#include "draft.h"
#include <algorithm>
#include <array>
// Test draft: Ren (stun that roots + dash) first, Heart of Ruin second.
void play_draft() {
    using cd = cambc::champion_draft;
    static constexpr std::array pref{cd::ren, cd::heart_of_ruin, cd::vendetta, cd::vesper_vale, cd::marcella};
    const auto chosen = cambc::draft::current_draft(cambc::team::ally);
    for (auto pick : pref)
        if (std::find(chosen.begin(), chosen.end(), pick) == chosen.end()) { cambc::draft::pick(pick); return; }
}
