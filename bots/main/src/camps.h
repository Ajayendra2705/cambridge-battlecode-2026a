// Part of bot.cpp: Camp danger, estimated clear time per group, standoff groups, gold weight.
// Unity build: bot.cpp includes this inside its anonymous namespace; not a standalone header.

// ---- Danger ----
bool camp_awake(const CampSnap& c) { return c.awake; }

// Live camps of awake groups within `range` of a tile.
std::vector<vec2> camp_threats(vec2 at, int slack) {
    std::vector<vec2> out;
    for (const auto& c : S.camps)
        if (dist(at, c.pos) <= c.range + slack && camp_awake(c)) out.push_back(c.pos);
    for (const auto& c : S.phantoms)
        if (dist(at, c.pos) <= c.range + slack) out.push_back(c.pos);
    return out;
}

float camp_incoming(vec2 at) {
    float d = 0;
    for (const auto& c : S.camps)
        if (dist(at, c.pos) <= c.range && camp_awake(c)) d += c.str;
    for (const auto& c : S.phantoms)
        if (dist(at, c.pos) <= c.range) d += c.str;
    return d;
}

// Estimated rounds to clear a group with n champions, including heal trips.
struct ClearStats { double hp, strength, hardest; bool several; int range = 3; };
// Fuel: the parts of clear_stats and standoff that never change are computed once per group.
std::vector<int> static_range;          // Max camp reach of the group.
std::vector<signed char> static_standoff;  // -1 unknown, else: full strength >= 300 and no camp reaching 4+.
ClearStats clear_stats(const Group& g) {
    const int gi = static_cast<int>(&g - W.groups.data());
    if (static_range.empty()) static_range.assign(W.groups.size(), -1);
    if (static_range[gi] < 0) {
        int r = CAMP_RANGE;
        for (const auto& c : W.strong_camps) if (c.group == gi) r = std::max(r, c.range);
        static_range[gi] = r;
    }
    const int range = static_range[gi];
    return {g.hp_left(), g.strength_left(), g.hardest(), g.spawns.size() > 1, range};
}

double clear_time(const ClearStats& g, int n, float dps, float hp, int home_dist) {
    const double team_dps = std::max(1.0, static_cast<double>(dps) * n);
    const double t_fight = g.hp / team_dps;
    const double damage = t_fight * g.strength * (g.several ? 0.7 : 1.0);
    // A champion leaves once the hits it takes walking out of range could kill it, so only health above that
    // margin is usable per trip.
    const double usable = hp - (g.range + 1) * g.hardest - 40.0;
    if (usable <= 50.0) return 1e6;
    const double budget = usable * n;
    const double trips = std::max(0.0, damage / budget - 1.0);
    return t_fight + trips * (6.0 + home_dist) / n;
}

// Groups too strong to stand next to (monoliths): only casters work on them, from spell range, where the camps
// cannot hit back. Camps never regenerate, so the damage keeps.
bool standoff(const Group& g) {
    const int gi = static_cast<int>(&g - W.groups.data());
    if (static_standoff.empty()) static_standoff.assign(W.groups.size(), -1);
    if (static_standoff[gi] < 0) {
        float full = 0;
        for (float s : g.strength) full += s;
        bool ok = full >= 300.0f;
        // Only when casters really outrange it: spells reach 4, so every attacking camp must reach less (elks reach 4).
        for (const auto& k : known_camps)
            if (k.group == gi && k.str > 0 && k.range >= 4) ok = false;
        static_standoff[gi] = ok ? 1 : 0;
    }
    return static_standoff[gi] == 1 && g.hardest() < 150.0f;
}

// Gold buys stats early; late it only matters as a tiebreak.
double gold_weight(int round) { return round < 1400 ? 0.25 : 0.05; }
