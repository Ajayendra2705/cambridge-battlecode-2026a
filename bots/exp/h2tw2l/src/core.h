// Part of bot.cpp: Constants, distance helper, debug tracing and per-activity round counters.
// Unity build: bot.cpp includes this inside its anonymous namespace; not a standalone header.

constexpr std::uint16_t UNREACH = distance_field::unreachable;
constexpr int MAX_SLOTS = 6;  // Shared memory bytes 0..5: each champion's target claim (group + 1).
constexpr int CAMP_RANGE = 3;

int dist(vec2 a, vec2 b) { return static_cast<int>(a.chebyshev_distance(b)); }

bool tracing = false;
bool log_rounds = false;
std::array<const char*, 16> prof_names{};
std::array<std::uint64_t, 16> prof_fuel{};
int prof_n = 0;
#define STAGE(name) do { bot_stage = name; if (tracing && prof_n < 16) { prof_names[prof_n] = name; prof_fuel[prof_n++] = cambc::fuel_remaining(); } } while (0)
// Rounds spent per activity, for tuning; printed every 250 rounds.
const char* activity = "idle";
const char* last_activity = "idle";
std::array<const char*, 24> act_names{};
std::array<int, 24> act_counts{};
#define ACT(name) (activity = name)
void count_activity() {
    for (size_t i = 0; i < act_names.size(); ++i) {
        if (act_names[i] == activity) { ++act_counts[i]; return; }
        if (!act_names[i]) { act_names[i] = activity; act_counts[i] = 1; return; }
    }
}
#define TRACE(x) do { if (tracing) std::cout << "T" << cambc::round_number() << " " << x << '\n'; } while (0)
