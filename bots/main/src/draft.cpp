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
    // Teams of up to 5 picks need bodies that survive alone: no linked pair (Cassi and Issac).
    // Engine 3.0.4 meta (top-10 ranked drafts, 2026-10-21): Heart of Ruin, Vendetta, Vesper, Ryth, Marcella.
    // Batch b3: our Ryth dealt 6854 damage per game against theirs 11207 (K/D 1.3/2.6); rivals draft Varg often.
    static constexpr std::array small_pref{cd::heart_of_ruin, cd::vendetta, cd::vesper_vale, cd::varg, cd::marcella};
    // 4- and 5-pick maps: Heart of Ruin, Vesper, Marcella, Vendetta, Varg (dq2m on b9, 10-26: 4-pick maps 11 of 26 wins
    // against main's 5-6, where main fields Varg and dies 8.0 times per game by r1000 to the rivals' 4.1; 5-pick 22 of 66
    // against 16-17). 3-pick maps keep Heart, Vendetta, Vesper (dq2m's Heart, Vesper, Marcella won 8 of 21, main 10).
    static constexpr std::array big_pref{cd::heart_of_ruin, cd::vesper_vale, cd::marcella, cd::vendetta, cd::varg};
    if (cambc::draft::team_size() <= 5)
        for (auto pick : cambc::draft::team_size() >= 4 ? big_pref : small_pref)
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
