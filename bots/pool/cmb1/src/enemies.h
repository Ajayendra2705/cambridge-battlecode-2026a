// Part of bot.cpp: Enemy sightings, team focus call (shared byte 7), danger near a group.
// Unity build: bot.cpp includes this inside its anonymous namespace; not a standalone header.

// ---- Enemy sightings ----
// Where enemies were seen recently; targets near them are risky. Each champion keeps its own (not shared).
struct Sighting { vec2 pos; int round; int count; };
std::vector<Sighting> sightings;
int shared_sighting_seen = -1;

// Merge a sighting into a nearby cluster, or replace the oldest one; at most 8 are kept.
void add_sighting(vec2 pos, int count) {
    for (auto& s : sightings) {
        if (dist(s.pos, pos) <= 5) {
            s.count = s.round == S.round ? std::max(s.count, count) : count;
            s.pos = pos;
            s.round = S.round;
            return;
        }
    }
    if (sightings.size() < 8) {
        sightings.push_back({pos, S.round, count});
        return;
    }
    auto oldest = std::min_element(sightings.begin(), sightings.end(),
                                   [](const Sighting& a, const Sighting& b) { return a.round < b.round; });
    *oldest = {pos, S.round, count};
}

void record_sightings() {
    std::erase_if(sightings, [](const Sighting& s) { return S.round - s.round > 40; });
    for (const auto& e : S.enemies) {
        if (W.enemy_spawn.is_set(e.pos)) continue;
        int count = 0;
        for (const auto& o : S.enemies) if (dist(o.pos, e.pos) <= 4) ++count;
        add_sighting(e.pos, count);
    }
}

// ---- Team focus (shared memory byte 7) ----
// One champion that engages an enemy, or is chased by one, calls it: ((enemy index + 1) << 5) | (round & 31). Allies
// that see the called enemy within 8 tiles take it as their prey, so two or three of us hit the same target (top-10
// teams average 15.8 assists per game to our 5.1). Calls older than 3 rounds expire. The index is stored + 1: with the
// plain index a call on enemy 0 in a round divisible by 32 was the byte 0, which reads as no call.
std::vector<std::uint32_t> enemy_ids;  // Enemy champion handles, sorted: the same order for every bot of our team.
int enemy_index(const ChampSnap& e) {
    if (enemy_ids.empty()) {
        for (const auto& k : known_champs) if (!k.ally) enemy_ids.push_back(handle_id(k.ch));
        std::sort(enemy_ids.begin(), enemy_ids.end());
    }
    const auto it = std::find(enemy_ids.begin(), enemy_ids.end(), handle_id(e.ch));
    return it == enemy_ids.end() ? -1 : static_cast<int>(it - enemy_ids.begin());
}
void call_focus(const ChampSnap& e) {
    const int idx = enemy_index(e);
    if (idx < 0 || idx > 6) return;
    write_byte(7, ((idx + 1) << 5) | (S.round & 31));
}
const ChampSnap* focus_target() {
    const int b = static_cast<int>(shared_cache[7]);
    if (b == 0 || ((S.round - (b & 31)) & 31) > 3) return nullptr;
    const int idx = (b >> 5) - 1;
    for (const auto& e : S.enemies)
        if (enemy_index(e) == idx) return &e;
    return nullptr;
}

// Recent enemy presence near a group: 0 safe, larger is more dangerous.
double group_danger(const Group& g) {
    double danger = 0;
    for (const auto& s : sightings) {
        int d = 99;
        for (auto sp : g.spawns) d = std::min(d, dist(sp, s.pos));
        if (d > 8) continue;
        const double fresh = 1.0 - (S.round - s.round) / 40.0;
        danger = std::max(danger, fresh * s.count);
    }
    return danger;
}
