#pragma once
#include <memory>
namespace bbt {

class Champion;

// Per-champion state survives between turns. The champion logic is built on
// the first gameplay turn, since self is unavailable in draft (the map is: the
// draft precomputes the static map plan into draft memory, kDraftPlan).
class Bot {
    std::unique_ptr<Champion> champion_;

public:
    Bot();
    ~Bot();

    // Priorities: fight enemies in range, retreat when hurt, bank gems, then farm camps.
    void play_turn();
};

// Draft, first turn: compute the static map plan and submit it as draft memory (false: not written).
bool bamboo_submit_draft_plan();
}  // namespace bbt
