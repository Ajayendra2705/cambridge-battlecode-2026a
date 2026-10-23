#include <cambc.h>
#include "draft.h"
#include <algorithm>
#include <array>
#include <vector>

// Pick the most preferred champion our team has not drafted yet.
void play_draft() {
    using cd = cambc::champion_draft;
    static constexpr std::array preference{cd::cassi_and_issac, cd::stellar, cd::ren, cd::varg, cd::heart_of_ruin, cd::tavi, cd::ryth, cd::vendetta, cd::vesper_vale,
        cd::tavi, cd::marcella, cd::stellar, cd::ren, cd::willow, cd::prism};
    const auto chosen = cambc::draft::current_draft(cambc::team::ally);
    // Small teams (3-4 picks) need bodies that survive alone: no linked pair.
    // Engine 3.0.4 meta (top-10 ranked drafts, 2026-10-21): Heart of Ruin, Vendetta, Vesper, Ryth, Marcella.
    static constexpr std::array small_pref{cd::heart_of_ruin, cd::vendetta, cd::vesper_vale, cd::varg, cd::marcella};
    if (cambc::draft::team_size() <= 5)
        for (auto pick : small_pref)
            if (std::find(chosen.begin(), chosen.end(), pick) == chosen.end()) {
                cambc::draft::pick(pick);
                return;
            }
    for (auto pick : preference) {
        if (std::find(chosen.begin(), chosen.end(), pick) == chosen.end()) {
            cambc::draft::pick(pick);
            return;
        }
    }
}
