// Draft: fixed composition by team size. Pick order sets ally ids; camps break distance ties
// towards the lowest id, so ids follow the tanking order: Heart of Ruin, Marcella, Ryth, then damage.
#include <cambc.h>
#include "draft.h"
#include "params.h"
#include <vector>

void play_draft() {
    using D = cambc::champion_draft;
    const auto mine = cambc::draft::current_draft(cambc::team::ally);
    const unsigned n = cambc::draft::team_size();
    std::vector<D> order;
    if (n <= 3) order = { D::heart_of_ruin, D::vendetta, D::vesper_vale };
    else if (P_MAR_FIRST && n == 4) order = { D::marcella, D::heart_of_ruin, D::vendetta, D::vesper_vale };
    else if (P_MAR_FIRST) order = { D::marcella, D::heart_of_ruin, D::ryth, D::vendetta, D::vesper_vale };
    else if (n == 4) order = { D::heart_of_ruin, D::marcella, D::vendetta, D::willow };
    else if (P_WILLOW) order = { D::heart_of_ruin, D::marcella, D::vendetta, D::vesper_vale, D::willow };
    else order = { D::heart_of_ruin, D::marcella, D::ryth, D::vendetta, D::vesper_vale };
    const std::size_t k = mine.size();
    D pick = k < order.size() ? order[k] : D::ryth;
    try {
        cambc::draft::pick(pick);
    } catch (...) {
        for (int i = 0; i < 13; ++i) {
            try { cambc::draft::pick(static_cast<D>(i)); return; } catch (...) {}
        }
    }
}
