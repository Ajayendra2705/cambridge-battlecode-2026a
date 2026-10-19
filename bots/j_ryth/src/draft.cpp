#include <cambc.h>
#include "draft.h"
#include <algorithm>
#include <array>
#include <vector>

// Pick the most preferred champion our team has not drafted yet.
void play_draft() {
    using cd = cambc::champion_draft;
    static constexpr std::array preference{cd::cassi_and_issac, cd::stellar, cd::ren, cd::varg, cd::ryth, cd::tavi, cd::vendetta, cd::vesper_vale,
        cd::tavi, cd::marcella, cd::stellar, cd::ren, cd::willow, cd::prism};
    const auto chosen = cambc::draft::current_draft(cambc::team::ally);
    for (auto pick : preference) {
        if (std::find(chosen.begin(), chosen.end(), pick) == chosen.end()) {
            cambc::draft::pick(pick);
            return;
        }
    }
}
