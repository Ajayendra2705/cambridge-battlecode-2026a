#include <cambc.h>
#include "draft.h"
#include <algorithm>
#include <array>
// Probe: pick a fixed list so every champion type gets drafted across the two probe bots.
void play_draft() {
    using cd = cambc::champion_draft;
    static constexpr std::array pref{cd::prism, cd::marcella, cd::willow, cd::ren, cd::varg};
    const auto chosen = cambc::draft::current_draft(cambc::team::ally);
    for (auto p : pref)
        if (std::find(chosen.begin(), chosen.end(), p) == chosen.end()) { cambc::draft::pick(p); return; }
}
