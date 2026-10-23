#pragma once

// Last decision stage reached this turn, reported when a turn throws.
inline const char* bot_stage = "";

// Per-champion bot. State persists between turns; the team coordinates through shared memory claims.
class Bot {
public:
    void play_turn();
};
