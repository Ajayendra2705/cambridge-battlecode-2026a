// Champion decisions: farm camp groups as a team, bank gems, recall to heal and shop.
//
// Facts this relies on (measured locally): camps never regenerate health, they do not chase, a whole group
// wakes when one member is hit, each camp attacks its nearest champion, and standing on spawn heals almost
// fully in one round. So damage dealt to a camp is banked: fight until low, step out of range, heal, return.
//
// Every engine query costs fuel (100k per turn), so each turn starts by reading what it needs into a snapshot.
#include <cambc.h>
#include "bot.h"
#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>
#include <iostream>
#include <memory>
#include <optional>
#include <span>
#include <variant>
#include <vector>

using cambc::vec2;
using cambc::team;
using cambc::bitboard;
using cambc::distance_field;
namespace cm = cambc::map;
namespace cv = cambc::vision;

namespace {

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

// ---- Static map knowledge plus what this champion has observed ----
struct Group {
    cm::camp_group group;
    std::vector<vec2> spawns;     // One per member camp, same order as group.camps().
    std::vector<float> max_hp, strength, hp;
    bitboard tiles;
    int gems = 0, gold = 0;
    int state = 0;                // 0 alive, 1 reward available, 2 respawning.
    int respawn_round = 0;
    int awake_round = -100;      // Last round a member was seen awake (or hit us from fog).
    double bank_cost = 0;         // Rounds to walk the reward to the nearest altar and tribute it.
    std::unique_ptr<distance_field> field;

    // Health and strength still to beat; a group that is not up will come back at full health.
    float hp_left() const {
        float s = 0;
        for (size_t i = 0; i < hp.size(); ++i) s += state == 0 ? hp[i] : max_hp[i];
        return s;
    }
    float strength_left() const {
        float s = 0;
        for (size_t i = 0; i < hp.size(); ++i) if (state != 0 || hp[i] > 0) s += strength[i];
        return s;
    }
    float hardest() const {
        float s = 0;
        for (size_t i = 0; i < hp.size(); ++i) if (state != 0 || hp[i] > 0) s = std::max(s, strength[i]);
        return s;
    }
    bool damaged() const {
        for (size_t i = 0; i < hp.size(); ++i) if (hp[i] > 0 && hp[i] < max_hp[i]) return true;
        return false;
    }
    void reset() { hp = max_hp; }
};

struct World {
    bool ready = false;
    bitboard terrain;             // Never walkable for us.
    bitboard ally_spawn, enemy_spawn, altar_tiles;
    std::vector<vec2> altars;
    std::vector<Group> groups;
    distance_field altar_field, spawn_field;
    distance_field enemy_field;  // Walking distance from the enemy spawn: where attackers come from.
    std::vector<std::vector<int>> covered_by;
    struct StrongCamp { vec2 pos; int range, group; };
    std::vector<StrongCamp> strong_camps;  // Monoliths and golems: their range is deadly to walk through.  // Per group: other groups whose monolith or golem reaches its tiles.
    std::vector<int> group_side;  // Per group: own-spawn distance minus enemy-spawn distance (positive = their half).
    int slot = 0, team_count = 1;
    std::vector<std::int16_t> camp_owner;  // Group index per tile, -1 elsewhere.
    std::vector<cambc::champion_type> slot_types;
};

World W;

void compute_field(distance_field& field, const bitboard& roots) {
    bitboard visited;
    field.compute(W.terrain & ~roots, roots, visited);
}

distance_field& group_field(Group& g) {
    if (!g.field) {
        g.field = std::make_unique<distance_field>();
        const int gi = static_cast<int>(&g - W.groups.data());
        bitboard zone;
        zone.clear();
        for (const auto& c : W.strong_camps)
            if (c.group != gi && W.groups[c.group].state == 0) zone.draw_chebyshev(c.pos, static_cast<float>(c.range));
        bitboard visited;
        g.field->compute((W.terrain | zone) & ~g.tiles, g.tiles, visited);
        // Fall back to the plain route when the detour cuts the group off from home.
        bool ok = false;
        for (const auto sp : W.ally_spawn.positions()) { ok = g.field->get(sp) != UNREACH; break; }
        if (!ok) compute_field(*g.field, g.tiles);
    }
    return *g.field;
}

std::uint32_t handle_id(const cambc::champion& c) {
    return static_cast<std::uint32_t>(static_cast<cambc::handle_champion_t>(c));
}

int group_of_camp(vec2 spawn) {
    if (!cm::is_in_bounds(spawn)) return -1;
    return W.camp_owner[spawn.y * cm::width() + spawn.x];
}

void init_units();

void init_world() {
    auto& me = cambc::self();
    W.ally_spawn = cm::spawn_region(team::ally);
    W.enemy_spawn = cm::spawn_region(team::enemy);
    W.terrain = cm::walls() | cm::holes() | cm::altars() | W.enemy_spawn;
    W.altars = cm::altars().positions();
    W.altar_tiles = cm::altars();
    for (const auto& group : cm::camp_groups()) {
        Group g{group};
        g.tiles = group.spawn_tiles();
        g.gems = static_cast<int>(group.gem_value());
        g.gold = static_cast<int>(group.gold_value());
        for (const auto& c : group.camps()) {
            const auto s = c.base_stats();
            g.spawns.push_back(c.spawn_position());
            g.max_hp.push_back(s.base_health);
            g.strength.push_back(s.base_strength);
        }
        g.reset();
        W.groups.push_back(std::move(g));
    }
    W.camp_owner.assign(static_cast<size_t>(cm::width() * cm::height()), -1);
    for (int i = 0; i < static_cast<int>(W.groups.size()); ++i)
        for (auto s : W.groups[i].spawns) W.camp_owner[s.y * cm::width() + s.x] = static_cast<std::int16_t>(i);
    compute_field(W.altar_field, cm::altars());
    compute_field(W.spawn_field, W.ally_spawn);
    for (auto& g : W.groups) {
        int d = UNREACH;
        for (auto sp : g.spawns) d = std::min<int>(d, W.altar_field.get(sp));
        g.bank_cost = (d == UNREACH ? 40 : d) + std::ceil(g.gems / 10.0);
    }
    {
        // Distances from the enemy spawn, walking as they would.
        distance_field& enemy_field = W.enemy_field;
        bitboard visited;
        const auto walls = (cm::walls() | cm::holes() | cm::altars() | W.ally_spawn) & ~W.enemy_spawn;
        enemy_field.compute(walls, W.enemy_spawn, visited);
        for (const auto& g : W.groups) {
            int ours = UNREACH, theirs = UNREACH;
            for (auto sp : g.spawns) {
                ours = std::min<int>(ours, W.spawn_field.get(sp));
                theirs = std::min<int>(theirs, enemy_field.get(sp));
            }
            W.group_side.push_back(ours == UNREACH || theirs == UNREACH ? 0 : ours - theirs);
        }
    }

    std::vector<std::pair<std::uint32_t, cambc::champion_type>> ids;
    for (const auto& a : cambc::champions(team::ally)) ids.push_back({handle_id(a), a.champion_name()});
    std::sort(ids.begin(), ids.end(), [](const auto& x, const auto& y) { return x.first < y.first; });
    for (const auto& [id, type] : ids) W.slot_types.push_back(type);
    W.team_count = static_cast<int>(ids.size());
    W.slot = 0;
    while (W.slot < static_cast<int>(ids.size()) && ids[W.slot].first != handle_id(me)) ++W.slot;
    init_units();
    W.ready = true;
}

// ---- Per-turn snapshot ----
struct CampSnap {
    cambc::camp camp;
    vec2 pos;
    float hp, max_hp, str;
    int group;
    int range;
    bool awake;
};

struct ChampSnap {
    cambc::champion ch;
    vec2 pos;
    float hp, max_hp, str;
    int range;
    std::uint32_t gems;
    float dps = 0;
    float burst = 0;   // Damage it can deal in one round with every spell ready.
    int reach = 1;     // Distance from which that burst lands after one step.
    cambc::champion_type type{};
};

// One-round damage with all spells ready, and the spell range that delivers it.
float champion_burst(cambc::champion_type t, float str, float focus, int& spell_range) {
    using ct = cambc::champion_type;
    spell_range = 4;
    switch (t) {
        case ct::stellar: return str + focus * 3.4f;
        case ct::cassi: return str + focus * 2.0f;
        case ct::prism: return str + focus * 2.5f;
        case ct::tavi: return str * 2 + focus * 2.2f;
        case ct::marcella: return str * 2 + focus * 2.0f;
        case ct::ren: return str + focus * 1.25f;
        case ct::ryth: return str * 2 + focus * 1.0f;
        // Stunning area dash plus up to +50% damage when hurt.
        case ct::heart_of_ruin: spell_range = 0; return str * 3.0f + focus * 1.5f;
        default: spell_range = 0; return str * 2;
    }
}

// Rough sustained damage per round against champions: basic attacks plus spells averaged over cooldowns.
float champion_dps(cambc::champion_type t, float str, float focus) {
    using ct = cambc::champion_type;
    switch (t) {
        case ct::stellar: return str + focus * 0.425f;
        case ct::cassi: return str + focus * 0.25f;
        case ct::prism: return str + focus * 0.31f;
        case ct::tavi: return str * 1.125f + focus * 0.275f;
        case ct::marcella: return str * 1.125f + focus * 0.25f;
        case ct::ren: return str + focus * 0.16f;
        case ct::ryth: return str * 1.125f + focus * 0.125f;
        case ct::heart_of_ruin: return str * 1.4f + focus * 0.2f;
        default: return str * 1.125f;
    }
}

struct Snap {
    int round = 0;
    vec2 me;
    float hp = 0, max_hp = 0, str = 0;
    int range = 1;
    bitboard visible, occ;        // occ: visible champions, camps and teleports, excluding us.
    std::vector<CampSnap> camps;  // Live visible camps.
    std::vector<CampSnap> phantoms;  // Unseen live camps of recently awake groups: they still hit.
    std::vector<ChampSnap> allies, enemies;
    // Tiles where a visible enemy could hit us hard on its next turn, and whether moves should avoid them.
    std::vector<std::pair<vec2, int>> danger;
    bool avoid_danger = false;
};

Snap S;

bool fragile = false;  // Cassi or Issac: losing either loses both.

bool in_danger(vec2 t) {
    for (const auto& [src, radius] : S.danger)
        if (static_cast<int>(t.chebyshev_distance(src)) <= radius) return true;
    return false;
}
float cached_dps = 0, cached_spell_dps = 0;
int cached_dps_round = -100;

// ---- Fight simulation ----
// A few rounds of focus fire between the champions near a fight, using live cooldowns. Each unit closes on the
// other side (melee may step and hit, ranged either steps or shoots), casts its best ready spell (stuns first)
// and hits the weakest living opponent. Cassi and Issac fall together.
struct SimSlot { float dmg = 0; int cd = 99; bool stun = false, reset = false; };
struct SimUnit {
    float hp = 0, str = 0;
    int range = 1, d = 99;
    std::array<SimSlot, 2> slots{};
    int link = -1;       // Index of the linked body (Cassi/Issac), -1 if none.
    bool stunned = false;
};

template <class C> std::array<SimSlot, 2> read_slots(const C& c) {
    std::array<SimSlot, 2> out{};
    int i = 0;
    for (const auto& ab : c.abilities()) {
        if (i >= 2) break;
        auto& s = out[i++];
        try {
            s.cd = ab.cooldown();
            s.stun = ab.is_cc();
            s.reset = ab.is_attack_reset();
            if (ab.is_damage() || ab.is_aoe_damage() || ab.is_cc() || ab.is_dash()) s.dmg = ab.damage_amount();
        } catch (const cambc::error&) {
            s.cd = 99;
        }
    }
    return out;
}

struct SimResult { int dead[2] = {0, 0}; float hp_frac[2] = {1, 1}; bool unit0_dead = false; };

// side 0 = us (unit 0 is this champion), side 1 = them; `them_first` makes the enemy act first each round.
SimResult simulate_fight(std::array<std::vector<SimUnit>, 2> u, int rounds, bool them_first) {
    std::array<float, 2> start{0, 0};
    for (int s = 0; s < 2; ++s) for (const auto& x : u[s]) start[s] += x.hp;
    for (int r = 0; r < rounds; ++r) {
        for (int k = 0; k < 2; ++k) {
            const int s = them_first ? 1 - k : k, o = 1 - s;
            for (auto& x : u[s]) {
                if (x.hp <= 0) continue;
                if (x.stunned) { x.stunned = false; continue; }
                SimUnit* t = nullptr;
                for (auto& y : u[o]) if (y.hp > 0 && (!t || y.hp < t->hp)) t = &y;
                if (!t) break;
                bool moved = false;
                // Close in until the spell (4) or basic range lands.
                const int want = std::max(x.range, 4);
                bool spell_ready = false;
                for (const auto& sl : x.slots) if (sl.cd <= 0 && (sl.dmg > 0 || sl.stun)) spell_ready = true;
                if (x.d > (spell_ready ? want : x.range)) { --x.d; moved = true; }
                float dmg = 0;
                const bool melee = x.range <= 1;
                // One cast: a stun if the target is not stunned yet, else the biggest damage spell, else a reset.
                SimSlot* cast = nullptr;
                if (!moved && x.d <= 4) {
                    for (auto& sl : x.slots) if (sl.cd <= 0 && sl.stun && !t->stunned) cast = &sl;
                    if (!cast) for (auto& sl : x.slots) if (sl.cd <= 0 && sl.dmg > 0 && (!cast || sl.dmg > cast->dmg)) cast = &sl;
                }
                if (!cast && x.d <= x.range && (melee || !moved))
                    for (auto& sl : x.slots) if (sl.cd <= 0 && sl.reset) cast = &sl;
                if (x.d <= x.range && (melee || !moved)) dmg += x.str;
                if (cast) {
                    if (cast->reset) dmg += x.str;
                    dmg += cast->dmg;
                    if (cast->stun) t->stunned = true;
                    cast->cd = 9;  // Cooldown 8 after this turn's tick.
                }
                t->hp -= dmg;
                if (t->hp <= 0 && t->link >= 0) u[o][t->link].hp = 0;
            }
        }
        for (auto& side : u) for (auto& x : side) for (auto& sl : x.slots) if (sl.cd > 0) --sl.cd;
    }
    SimResult res;
    for (int s = 0; s < 2; ++s) {
        float left = 0;
        for (const auto& x : u[s]) { if (x.hp <= 0) ++res.dead[s]; else left += x.hp; }
        res.hp_frac[s] = start[s] > 0 ? left / start[s] : 0;
    }
    res.unit0_dead = !u[0].empty() && u[0][0].hp <= 0;
    return res;
}

float my_dps() {
    if (S.round - cached_dps_round < 10) return cached_dps;
    auto& me = cambc::self();
    float d = S.str, spell = 0;
    for (const auto& ab : me.abilities()) {
        if (ab.is_damage() || ab.is_aoe_damage()) d += ab.damage_amount() / 8.0f;
        // Stuns that also deal damage (Tavi, Ren) report as crowd control, not damage.
        if (ab.is_damage() || ab.is_aoe_damage() || ab.is_cc()) {
            try {
                spell += ab.damage_amount() / 8.0f;
            } catch (const cambc::error&) {
            }
        }
        if (ab.is_attack_reset()) d += S.str / 8.0f;
    }
    cached_dps = d;
    cached_spell_dps = spell;
    cached_dps_round = S.round;
    return cached_dps;
}

// Damage per round from spells alone: they reach 4 tiles, one beyond any camp's attack range.
float my_spell_dps() {
    my_dps();
    return cached_spell_dps;
}

// Known units, built once: camps by spawn tile (camps never move) and every champion's handle.
struct KnownCamp { cambc::camp camp; int group; float max_hp, str; int range; int idx; };

// Camp attack range straight from the engine (3.0: elks reach 4, monoliths 5); the table is only a fallback.
int camp_kind_range(const cambc::camp& c) {
    try {
        return c.attack_range();
    } catch (const cambc::error&) {
    }
    switch (c.kind()) {
        case cambc::camp_type::monolith: return 5;
        case cambc::camp_type::golem: return 4;
        default: return CAMP_RANGE;
    }
}
struct KnownChamp { cambc::champion ch; cambc::champion_type type; bool ally; };
std::vector<KnownCamp> known_camps;
std::vector<std::int16_t> camp_index;  // Per tile, index into known_camps or -1.
std::vector<KnownChamp> known_champs;

void init_units() {
    camp_index.assign(static_cast<size_t>(cm::width() * cm::height()), -1);
    for (int gi = 0; gi < static_cast<int>(W.groups.size()); ++gi) {
        const auto& g = W.groups[gi];
        const auto camps = g.group.camps();
        for (size_t i = 0; i < camps.size(); ++i) {
            const vec2 pos = g.spawns[i];
            camp_index[pos.y * cm::width() + pos.x] = static_cast<std::int16_t>(known_camps.size());
            known_camps.push_back({camps[i], gi, g.max_hp[i], g.strength[i], camp_kind_range(camps[i]), static_cast<int>(i)});
        }
    }
    // A group inside another group's monolith or golem range cannot be farmed while that camp is alive.
    W.covered_by.assign(W.groups.size(), {});
    for (const auto& k : known_camps) {
        if (k.range <= CAMP_RANGE || k.group < 0) continue;
        const vec2 at = W.groups[k.group].spawns[k.idx];
        W.strong_camps.push_back({at, k.range, k.group});
        for (int gi = 0; gi < static_cast<int>(W.groups.size()); ++gi) {
            if (gi == k.group) continue;
            auto& cov = W.covered_by[gi];
            if (std::find(cov.begin(), cov.end(), k.group) != cov.end()) continue;
            for (auto sp : W.groups[gi].spawns)
                if (dist(sp, at) <= k.range) { cov.push_back(k.group); break; }
        }
    }
    const auto self_id = handle_id(cambc::self());
    for (const auto side : {team::ally, team::enemy})
        for (const auto& c : cambc::champions(side))
            if (handle_id(c) != self_id) known_champs.push_back({c, c.champion_name(), side == team::ally});
}

// One engine call per visible unit: read the raw state structs instead of one accessor at a time.
void take_snapshot() {
    auto& me = cambc::self();
    S.round = static_cast<int>(cambc::round_number());
    {
        cambc::detail::champion_info info{};
        cambc::detail::check(cambc::detail::sdk_champion(handle_id(me), &info));
        S.me = {info.x, info.y};
        S.hp = info.health;
        S.max_hp = info.max_health;
        S.str = info.strength;
        S.range = info.attack_range;
    }
    S.visible = cv::visible_tiles();
    S.camps.clear();
    S.occ = cv::teleport_tiles();
    // Engine 3.0 reports which camps are awake; camps can attack without our damage having woken them.
    static std::vector<char> awake_at;
    awake_at.assign(static_cast<size_t>(cm::width() * cm::height()), 0);
    for (const auto pos : cv::awake_camp_tiles().positions()) awake_at[pos.y * cm::width() + pos.x] = 1;
    for (const auto pos : cv::camp_tiles().positions()) {
        S.occ.set(pos);
        const int idx = camp_index[pos.y * cm::width() + pos.x];
        if (idx < 0) continue;
        const auto& k = known_camps[idx];
        cambc::detail::camp_state cs{};
        if (cambc::detail::sdk_camp(static_cast<std::uint32_t>(static_cast<cambc::handle_camp_t>(k.camp)), &cs) != 0) continue;
        if (cs.health <= 0) continue;
        S.camps.push_back({k.camp, pos, cs.health, k.max_hp, k.str, k.group, k.range, awake_at[pos.y * cm::width() + pos.x] != 0});
        if (S.camps.back().awake && k.group >= 0) W.groups[k.group].awake_round = S.round;
    }
    S.allies.clear();
    S.enemies.clear();
    for (const auto& k : known_champs) {
        cambc::detail::champion_info info{};
        if (cambc::detail::sdk_champion(handle_id(k.ch), &info) != 0) continue;
        if (info.x < 0 || info.y < 0 || info.health <= 0) continue;
        const vec2 pos{info.x, info.y};
        S.occ.set(pos);
        ChampSnap snap{k.ch, pos, info.health, info.max_health, info.strength, info.attack_range, 0};
        snap.type = k.type;
        // Killers take every carried gem: knowing who carries what makes them targets.
        if (!k.ally) {
            try {
                snap.gems = k.ch.gem_count();
            } catch (const cambc::error&) {
            }
        }
        snap.dps = champion_dps(k.type, info.strength, info.focus);
        int spell_range = 0;
        snap.burst = champion_burst(k.type, info.strength, info.focus, spell_range);
        snap.reach = std::max(snap.range, spell_range) + 1;
        // A dash adds two tiles before a basic attack.
        using ct = cambc::champion_type;
        if (k.type == ct::issac || k.type == ct::vendetta || k.type == ct::vesper_vale || k.type == ct::ren
            || k.type == ct::heart_of_ruin)
            snap.reach = std::max(snap.reach, snap.range + 3);
        (k.ally ? S.allies : S.enemies).push_back(snap);
    }
    // Damage spells cannot follow a step, so a caster threatens its spell range; melee threatens a step plus reach.
    S.danger.clear();
    S.avoid_danger = false;
    for (const auto& e : S.enemies) {
        if (W.enemy_spawn.is_set(e.pos) || e.burst < S.hp * (fragile ? 0.15f : 0.3f)) continue;
        S.danger.push_back({e.pos, (e.reach > e.range + 1 ? e.reach - 1 : e.range + 1) + (fragile ? 1 : 0)});
    }
}

void broadcast_respawn(int group, int respawn_round);

// Camps never move, so a known camp that is out of sight is still where it was. Its group is treated as awake
// for a few rounds after a member was last seen awake or an unexplained hit came from its range.
void build_phantoms() {
    S.phantoms.clear();
    for (const auto& k : known_camps) {
        if (k.group < 0 || k.str <= 0) continue;
        const auto& g = W.groups[k.group];
        if (g.state != 0 || S.round - g.awake_round > 4) continue;
        const vec2 pos = g.spawns[k.idx];
        if (S.visible.is_set(pos) || g.hp[k.idx] <= 0) continue;
        S.phantoms.push_back({k.camp, pos, g.hp[k.idx], k.max_hp, k.str, k.group, k.range, true});
    }
}

void update_knowledge() {
    const int round = S.round;
    for (auto& g : W.groups) {
        bool seen = false;
        for (auto sp : g.spawns) if (S.visible.is_set(sp)) { seen = true; break; }
        if (!seen) {
            if (g.state == 2 && round >= g.respawn_round) { g.state = 0; g.reset(); }
            continue;
        }
        // Any visible member alive means the group is up; read live health from the snapshot.
        bool any_live = false;
        for (const auto& c : S.camps) if (c.group >= 0 && &W.groups[c.group] == &g) { any_live = true; break; }
        if (any_live) {
            g.state = 0;
            for (size_t i = 0; i < g.spawns.size(); ++i) {
                if (!S.visible.is_set(g.spawns[i])) continue;
                g.hp[i] = 0;
                for (const auto& c : S.camps) if (c.pos == g.spawns[i]) { g.hp[i] = c.hp; break; }
            }
            continue;
        }
        const int prev = g.state;
        const auto handle = static_cast<std::uint32_t>(static_cast<cambc::handle_camp_group_t>(g.group));
        std::uint32_t raw = 0;
        if (cambc::detail::sdk_camp_group_state(handle, &raw) == 0) {
            if (raw == 1) g.state = 0;
            else if (raw == 2) g.state = 1;
            else if (raw == 3) {
                std::int32_t timer = 0;
                cambc::detail::sdk_camp_group_cooldown(handle, &timer);
                g.state = 2;
                g.respawn_round = round + timer;
                if (prev != 2) broadcast_respawn(static_cast<int>(&g - W.groups.data()), g.respawn_round);
            }
        }
        if (g.state == 0 && prev == 2) g.reset();
        if (g.state != 0) std::fill(g.hp.begin(), g.hp.end(), 0.0f);
    }
}

// ---- Shared memory ----
int read_byte(int i) {
    std::byte b{};
    cambc::shared_memory.read(i, std::span{&b, 1});
    return static_cast<int>(b);
}
void write_byte(int i, int v) {
    std::byte b{static_cast<unsigned char>(v)};
    cambc::shared_memory.write(i, std::span{&b, 1});
}

// Layout: bytes 0-4 hold six 6-bit claims (group + 1); bytes 5-6 broadcast an observed respawn (group + 1,
// respawn round low byte); byte 7 holds a coarse enemy sighting ((x / 7 + 1) << 4 | y / 7).
std::array<int, MAX_SLOTS> claim_cache{};
int my_claim = -1;
std::array<std::byte, 8> shared_cache{};

std::uint64_t claim_bits() {
    std::uint64_t bits = 0;
    for (int i = 0; i < 5; ++i) bits |= static_cast<std::uint64_t>(shared_cache[i]) << (8 * i);
    return bits;
}

void refresh_claims() {
    cambc::shared_memory.read(0, std::span{shared_cache});
    const auto bits = claim_bits();
    for (int s = 0; s < MAX_SLOTS; ++s)
        claim_cache[s] = s < W.team_count && s != W.slot ? static_cast<int>(bits >> (6 * s) & 63) - 1 : -1;
}

void write_claim(int group) {
    if (W.slot >= MAX_SLOTS || group == my_claim) return;
    my_claim = group;
    auto bits = claim_bits();
    bits &= ~(std::uint64_t{63} << (6 * W.slot));
    bits |= static_cast<std::uint64_t>((group + 1) & 63) << (6 * W.slot);
    for (int i = 0; i < 5; ++i) shared_cache[i] = static_cast<std::byte>(bits >> (8 * i) & 0xff);
    cambc::shared_memory.write(0, std::span{shared_cache.data(), 5});
}

// Tell teammates when a group was seen going down, so nobody walks to it before it is back.
int last_broadcast = -1;
void broadcast_respawn(int group, int respawn_round) {
    const int key = group * 4096 + respawn_round;
    if (key == last_broadcast) return;
    last_broadcast = key;
    write_byte(5, group + 1);
    write_byte(6, respawn_round & 0xff);
}

void read_broadcast() {
    const int g = static_cast<int>(shared_cache[5]) - 1;
    if (g < 0 || g >= static_cast<int>(W.groups.size())) return;
    // Rebuild the full round from its low byte: the nearest value not long past.
    int r = (S.round & ~0xff) | static_cast<int>(shared_cache[6]);
    if (r < S.round - 64) r += 256;
    if (r > S.round + 192) r -= 256;
    auto& grp = W.groups[g];
    if (r > S.round && (grp.state == 0 || grp.respawn_round != r)) {
        bool seen = false;
        for (auto sp : grp.spawns) if (S.visible.is_set(sp)) { seen = true; break; }
        if (!seen) {
            grp.state = 2;
            grp.respawn_round = r;
            std::fill(grp.hp.begin(), grp.hp.end(), 0.0f);
        }
    }
}
int claimants(int group) {
    int n = 0;
    for (int s = 0; s < MAX_SLOTS; ++s)
        if (claim_cache[s] == group) ++n;
    return n;
}

// ---- Movement ----
constexpr std::array<vec2, 8> DIRS{vec2{1, 0}, vec2{-1, 0}, vec2{0, 1}, vec2{0, -1}, vec2{1, 1}, vec2{1, -1},
    vec2{-1, 1}, vec2{-1, -1}};

bool safe_move(vec2 t) {
    try {
        if (cambc::self().move_absolute(t)) {
            S.me = t;
            return true;
        }
    } catch (const cambc::error&) {
    }
    return false;
}

// Take the free neighbour with the lowest field value below `here`; hidden blockers are skipped.
bool descend(const distance_field& field, bitboard occ, int here) {
    const vec2 p = S.me;
    for (int attempt = 0; attempt < 3; ++attempt) {
        vec2 best = p;
        int best_d = here;
        for (auto d : DIRS) {
            vec2 t{p.x + d.x, p.y + d.y};
            if (!cm::is_in_bounds(t) || W.terrain.is_set(t) || occ.is_set(t)) continue;
            if (S.avoid_danger && in_danger(t)) continue;
            const int v = field.get(t);
            if (v < best_d) best_d = v, best = t;
        }
        if (best == p) return false;
        if (safe_move(best)) return true;
        occ.set(best);
    }
    return false;
}

// Dash along the field when it skips ahead, then walk.
bool step_static(const distance_field& field, int here) {
    auto& me = cambc::self();
    const vec2 p = S.me;
    if (here >= 4 && me.can_cast()) {
        for (const auto& ab : me.abilities()) {
            if (!ab.is_dash() || !ab.is_ready()) continue;
            vec2 best = p;
            int best_d = here - 1;
            for (auto t : ab.valid_tiles().positions()) {
                if (S.occ.is_set(t) || W.terrain.is_set(t)) continue;
                if (S.avoid_danger && in_danger(t)) continue;
                const int d = field.get(t);
                if (d < best_d) best_d = d, best = t;
            }
            try {
                if (best != p && ab.use(best)) {
                    S.me = best;
                    if (me.can_move()) descend(field, S.occ, field.get(S.me));
                    return true;
                }
            } catch (const cambc::error&) {
            }
        }
    }
    return descend(field, S.occ, here);
}

// Step towards `roots` (field value `stop_at` or less counts as arrived); route around occupants if needed.
bool step_field(const distance_field& field, const bitboard& roots, int stop_at = 0) {
    auto& me = cambc::self();
    if (!me.can_move()) return false;
    const int here = field.get(S.me);
    if (here <= stop_at) return false;
    if (step_static(field, here)) return true;
    if (!me.can_move()) return false;
    distance_field local;
    bitboard visited, mine;
    mine.clear();
    mine.set(S.me);
    const auto free_roots = roots & ~S.occ;
    local.compute_to((W.terrain | S.occ) & ~free_roots & ~mine, free_roots, mine, visited);
    const int local_here = local.get(S.me);
    if (local_here == UNREACH) return false;
    return descend(local, S.occ, local_here);
}

// Walk to any free tile of `goals` using a fresh field around current occupants.
bool step_to_tiles(const bitboard& goals) {
    auto& me = cambc::self();
    if (!me.can_move() || goals.is_set(S.me)) return false;
    bitboard visited, mine;
    mine.clear();
    mine.set(S.me);
    const auto free_goals = goals & ~S.occ & ~W.terrain;
    if (free_goals.is_empty()) return false;
    distance_field local;
    local.compute_to((W.terrain | S.occ) & ~free_goals & ~mine, free_goals, mine, visited);
    const int here = local.get(S.me);
    if (here == UNREACH) return false;
    return step_static(local, here);
}

// Steps of the shortest walk to any free tile of `goals` (0 if already on one, UNREACH if blocked).
int steps_to_tiles(const bitboard& goals) {
    if (goals.is_set(S.me)) return 0;
    bitboard visited, mine;
    mine.clear();
    mine.set(S.me);
    const auto free_goals = goals & ~S.occ & ~W.terrain;
    if (free_goals.is_empty()) return UNREACH;
    distance_field local;
    local.compute_to((W.terrain | S.occ) & ~free_goals & ~mine, free_goals, mine, visited);
    return local.get(S.me);
}

// Move to the free neighbour that maximises distance from the given threats, preferring home.
bool step_away(const std::vector<vec2>& threats) {
    if (!cambc::self().can_move() || threats.empty()) return false;
    const vec2 p = S.me;
    int cap = CAMP_RANGE;
    for (auto th : threats) {
        const int idx = camp_index[th.y * cm::width() + th.x];
        if (idx >= 0) cap = std::max(cap, known_camps[idx].range);
    }
    auto score = [&](vec2 t) {
        int m = 1 << 20;
        for (auto th : threats) m = std::min(m, dist(t, th));
        return std::min(m, cap + 1) * 1000 - W.spawn_field.get(t);
    };
    vec2 best = p;
    int best_s = score(p);
    for (auto d : DIRS) {
        vec2 t{p.x + d.x, p.y + d.y};
        if (!cm::is_in_bounds(t) || W.terrain.is_set(t) || S.occ.is_set(t)) continue;
        const int s = score(t);
        if (s > best_s) best_s = s, best = t;
    }
    return best != p && safe_move(best);
}

// Step to a neighbour outside every enemy's reach, preferring the way home.
bool step_out_of_danger() {
    if (!cambc::self().can_move()) return false;
    const vec2 p = S.me;
    vec2 best = p;
    int best_d = UNREACH;
    for (auto d : DIRS) {
        vec2 t{p.x + d.x, p.y + d.y};
        if (!cm::is_in_bounds(t) || W.terrain.is_set(t) || S.occ.is_set(t) || in_danger(t)) continue;
        const int v = W.spawn_field.get(t);
        if (v < best_d) best_d = v, best = t;
    }
    return best != p && safe_move(best);
}

int enemy_seen_at = -100;  // Mirrors enemy_seen_round, which is declared later.

// Recall is cancelled by damage, so never start it with an enemy close by: walk instead (top teams do this).
bool walk_home();
void go_home() {
    bool exposed = S.round - enemy_seen_at <= 3;
    for (const auto& e : S.enemies) if (dist(e.pos, S.me) <= 5) exposed = true;
    if (W.spawn_field.get(S.me) > 5 && !exposed) { cambc::self().recall(); return; }
    if (!walk_home() && !exposed) cambc::self().recall();
}

// Step toward spawn without crossing an awake camp's reach (a monolith beside the path kept hitting us).
// Returns false when the only way down enters a reach and we stay put.
bool walk_home() {
    bitboard reach;
    reach.clear();
    for (const auto& c : S.camps) if (c.awake) reach.draw_chebyshev(c.pos, static_cast<float>(c.range));
    for (const auto& c : S.phantoms) reach.draw_chebyshev(c.pos, static_cast<float>(c.range));
    if (!reach.is_set(S.me) && cambc::self().can_move()) {
        const int here = W.spawn_field.get(S.me);
        vec2 best = S.me;
        int best_v = here;
        for (auto d : DIRS) {
            vec2 t{S.me.x + d.x, S.me.y + d.y};
            if (!cm::is_in_bounds(t) || W.terrain.is_set(t) || S.occ.is_set(t)) continue;
            const int v = W.spawn_field.get(t);
            if (v < best_v) best_v = v, best = t;
        }
        if (best != S.me && reach.is_set(best)) {
            // Detour: any free downhill neighbour outside reach, else wait here (recall when nobody is near).
            best = S.me;
            for (auto d : DIRS) {
                vec2 t{S.me.x + d.x, S.me.y + d.y};
                if (!cm::is_in_bounds(t) || W.terrain.is_set(t) || S.occ.is_set(t) || reach.is_set(t)) continue;
                if (W.spawn_field.get(t) <= here && (best == S.me || W.spawn_field.get(t) < W.spawn_field.get(best))) best = t;
            }
            if (best == S.me) return false;
            safe_move(best);
            return true;
        }
    }
    step_field(W.spawn_field, W.ally_spawn, 0);
    return true;
}

// ---- Shopping ----
bool uses_focus(cambc::champion_type t) {
    using ct = cambc::champion_type;
    return t == ct::stellar || t == ct::cassi || t == ct::prism || t == ct::ren || t == ct::willow;
}

// Who should take capture rewards (and so the gold): champions whose damage grows most from shards.
int capture_priority(cambc::champion_type t) {
    using ct = cambc::champion_type;
    switch (t) {
        case ct::varg: return 9;
        case ct::stellar: return 8;
        case ct::vendetta: return 7;
        case ct::ren: return 6;
        case ct::vesper_vale: return 6;
        case ct::issac: return 5;
        case ct::tavi: return 5;
        case ct::ryth: return 4;
        case ct::marcella: return 4;
        case ct::cassi: return 3;
        default: return 2;
    }
}

void shop() {
    auto& me = cambc::self();
    using it = cambc::item_type;
    if (me.gold_count() < 30) return;
    // Emblems in order (Monster for camp damage, then Durability and Bruiser of health to survive bursts),
    // then power shards of the main stat.
    const bool focus = uses_focus(me.champion_name());
    const std::array<it, 4> plan = focus
        ? std::array<it, 4>{it::monster_shard_of_focus, it::durability_shard_of_health, it::jungle_shard_of_health,
                            it::power_shard_of_focus}
        : std::array<it, 4>{it::monster_shard_of_strength, it::durability_shard_of_health, it::jungle_shard_of_health,
                            it::power_shard_of_strength};
    // Burst casters stay at range and win fights by damage: straight to power after the Monster emblem.
    const auto self_type = me.champion_name();
    const bool burst_caster = self_type == cambc::champion_type::stellar || self_type == cambc::champion_type::tavi;
    for (int guard = 0; guard < 20; ++guard) {
        const auto counts = me.item_count();
        it choice = plan[3];
        for (int i = 0; i < 3; ++i) {
            const auto emblem = plan[i].result();
            if (emblem && counts[*emblem] == 0) { choice = plan[i]; break; }
        }
        if (me.gold_count() < choice.cost() || !me.can_buy(choice)) break;
        me.buy(choice);
        cached_dps_round = -100;
    }
}

// ---- Abilities ----
int n_cc = 0, n_aoe = 0, n_dmg = 0, n_attack = 0, n_reset = 0;
// Spend one cast on camps: stun the strongest unstunned attacker, else the best area hit, else burst `focus`.
// Dashes that hit on landing (Heart of Ruin): land where the most targets sit within the landing radius.
bool strike_dash(const std::vector<vec2>& targets, bool skip_danger) {
    auto& me = cambc::self();
    if (!me.can_cast() || targets.empty()) return false;
    for (const auto& ab : me.abilities()) {
        if (!ab.is_ready() || !ab.is_dash() || !ab.info()) continue;
        const auto* d = std::get_if<cambc::ability_dash>(&*ab.info());
        if (!d || (d->modifier <= 0 && d->duration <= 0)) continue;
        const int radius = std::max(1, static_cast<int>(d->radius));
        vec2 best{-1, -1};
        int best_hits = 0, best_d = 99;
        for (auto t : ab.valid_tiles().positions()) {
            if (S.occ.is_set(t) || W.terrain.is_set(t)) continue;
            if (skip_danger && in_danger(t)) continue;
            int hits = 0, nearest = 99;
            for (auto x : targets) {
                const int dd = dist(t, x);
                if (dd <= radius) ++hits;
                nearest = std::min(nearest, dd);
            }
            if (hits > best_hits || (hits == best_hits && hits > 0 && nearest < best_d)) best_hits = hits, best = t, best_d = nearest;
        }
        if (best_hits == 0) continue;
        try {
            if (ab.use(best)) { S.me = best; return true; }
        } catch (const cambc::error&) {
        }
    }
    return false;
}

// Keep the free ward a couple of tiles towards the enemy approach so attackers show up before they reach us.
void place_ward_forward() {
    auto& me = cambc::self();
    if (W.ally_spawn.is_set(S.me)) return;
    try {
        if (me.ward_cooldown() > 0) return;
        for (auto w : me.ward_positions()) if (dist(w, S.me) <= 5) return;
        vec2 best{-1, -1};
        int best_v = UNREACH;
        for (auto t : me.ward_placement_tiles().positions()) {
            if (W.terrain.is_set(t)) continue;
            const int v = W.enemy_field.get(t);
            if (v < best_v) best_v = v, best = t;
        }
        if (best.x >= 0) me.place_ward(best);
    } catch (const cambc::error&) {
    }
}

bool use_camp_abilities(const std::vector<const CampSnap*>& live, const CampSnap& focus, bool awake) {
    auto& me = cambc::self();
    if (!me.can_cast()) return false;
    for (const auto& ab : me.abilities()) {
        if (!ab.is_ready() || !ab.is_cc() || !awake) continue;
        const auto tiles = ab.valid_tiles();
        const CampSnap* best = nullptr;
        for (const auto* c : live) {
            if (c->str <= 0 || !tiles.is_set(c->pos)) continue;
            if (!best || c->str > best->str) {
                try {
                    if (c->camp.buffs().has_stun()) continue;
                } catch (const cambc::error&) {
                    continue;
                }
                best = c;
            }
        }
        if (!best) continue;
        try {
            if (ab.can_target_ground() ? ab.use(best->pos) : ab.use(best->camp)) { ++n_cc; return true; }
        } catch (const cambc::error&) {
        }
    }
    if (awake) {
        std::vector<vec2> pts;
        for (const auto* c : live) if (c->str > 0) pts.push_back(c->pos);
        if (strike_dash(pts, false)) { ++n_cc; return true; }
    }
    for (const auto& ab : me.abilities()) {
        if (!ab.is_ready() || !ab.is_aoe_damage()) continue;
        const auto tiles = ab.valid_tiles();
        vec2 best_tile{-1, -1};
        int best_hits = 0;
        for (const auto* c : live) {
            for (int dx = -1; dx <= 1; ++dx) for (int dy = -1; dy <= 1; ++dy) {
                const vec2 t{c->pos.x + dx, c->pos.y + dy};
                if (!cm::is_in_bounds(t) || !tiles.is_set(t)) continue;
                int hits = 0;
                for (const auto* o : live) if (dist(o->pos, t) <= 1) ++hits;
                if (hits > best_hits) best_hits = hits, best_tile = t;
            }
        }
        if (best_hits == 0) continue;
        try {
            if (ab.use(best_tile)) { ++n_aoe; return true; }
        } catch (const cambc::error&) {
        }
    }
    for (const auto& ab : me.abilities()) {
        if (!ab.is_ready() || !ab.is_damage()) continue;
        if (!ab.valid_tiles().is_set(focus.pos)) continue;
        try {
            if (ab.use(focus.camp)) { ++n_dmg; return true; }
        } catch (const cambc::error&) {
        }
    }
    return false;
}

// From spell range: the best area hit, else any damaging spell (stuns included) on the focus target.
bool cast_from_range(const std::vector<const CampSnap*>& live, const CampSnap& focus) {
    auto& me = cambc::self();
    if (!me.can_cast()) return false;
    if (use_camp_abilities(live, focus, false)) return true;
    for (const auto& ab : me.abilities()) {
        if (!ab.is_ready() || !ab.is_cc() || ab.can_target_ground()) continue;
        try {
            if (ab.damage_amount() > 0 && ab.valid_tiles().is_set(focus.pos) && ab.use(focus.camp)) { ++n_dmg; return true; }
        } catch (const cambc::error&) {
        }
    }
    return false;
}

// Stun the most dangerous enemy in reach first, then burst the focus target.
bool use_champion_abilities(const ChampSnap& target) {
    auto& me = cambc::self();
    if (!me.can_cast()) return false;
    for (const auto& ab : me.abilities()) {
        if (!ab.is_ready() || !ab.is_cc()) continue;
        const auto tiles = ab.valid_tiles();
        const ChampSnap* best = nullptr;
        for (const auto& e : S.enemies) {
            if (!tiles.is_set(e.pos) || W.enemy_spawn.is_set(e.pos)) continue;
            if (e.ch.passive() == cambc::passive_type::stun_immunity) continue;
            if (!best || e.dps > best->dps) best = &e;
        }
        if (!best) continue;
        try {
            if (best->ch.buffs().has_stun()) continue;
            if (ab.can_target_ground() ? ab.use(best->pos) : ab.use(best->ch)) return true;
        } catch (const cambc::error&) {
        }
    }
    if (strike_dash({target.pos}, false)) return true;
    for (const auto& ab : me.abilities()) {
        if (!ab.is_ready()) continue;
        try {
            if (ab.is_damage()) {
                if (ab.valid_tiles().is_set(target.pos) && ab.use(target.ch)) return true;
            } else if (ab.is_aoe_damage()) {
                if (ab.valid_tiles().is_set(target.pos) && ab.use(target.pos)) return true;
            }
        } catch (const cambc::error&) {
        }
    }
    return false;
}

bool try_attack_reset_and_hit(const cambc::unit& target) {
    auto& me = cambc::self();
    if (me.can_attack() || !me.can_cast()) return false;
    for (const auto& ab : me.abilities()) {
        if (!ab.is_attack_reset() || !ab.is_ready()) continue;
        try {
            if (ab.use() && me.can_attack()) {
                ++n_reset;
                me.attack(target);
                return true;
            }
        } catch (const cambc::error&) {
        }
    }
    return false;
}

void use_support_abilities(bool in_combat) {
    auto& me = cambc::self();
    if (!me.can_cast()) return;
    for (const auto& ab : me.abilities()) {
        if (!ab.is_ready()) continue;
        try {
            if (ab.is_heal()) {
                const ChampSnap* best = nullptr;
                float best_missing = ab.heal_amount() * 0.6f;
                for (const auto& a : S.allies) {
                    const float missing = a.max_hp - a.hp;
                    if (missing > best_missing && ab.valid_tiles().is_set(a.pos)) best_missing = missing, best = &a;
                }
                if (best && ab.use(best->ch)) return;
            }
            if (ab.is_shield() && in_combat && S.hp < S.max_hp * 0.85f) {
                if (ab.use()) return;
            }
        } catch (const cambc::error&) {
        }
    }
}

bool attack_unit(const cambc::unit& target) {
    auto& me = cambc::self();
    if (!me.can_attack()) return false;
    try {
        me.attack(target);
        ++n_attack;
        return true;
    } catch (const cambc::error&) {
        return false;
    }
}

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
ClearStats clear_stats(const Group& g) {
    int range = CAMP_RANGE;
    const int gi = static_cast<int>(&g - W.groups.data());
    for (const auto& c : W.strong_camps) if (c.group == gi) range = std::max(range, c.range);
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
    float full = 0;
    for (float s : g.strength) full += s;
    return g.hardest() < 150.0f && full >= 300.0f;
}

// Gold buys stats early; late it only matters as a tiebreak.
double gold_weight(int round) { return round < 1400 ? 0.1 : 0.03; }

// ---- Enemy sightings ----
// Where enemies were seen recently; targets near them are risky. The latest group sighting is shared through
// shared memory bytes 6 (x + 1) and 7 (y + 1).
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
    int first = -1;
    for (int i = 0; i < static_cast<int>(S.enemies.size()); ++i) {
        const auto& e = S.enemies[i];
        if (W.enemy_spawn.is_set(e.pos)) continue;
        int count = 0;
        for (const auto& o : S.enemies) if (dist(o.pos, e.pos) <= 4) ++count;
        add_sighting(e.pos, count);
        if (first < 0) first = i;
    }
    if (first >= 0) {
        const vec2 e = S.enemies[first].pos;
        write_byte(7, (std::min(e.x / 7, 14) + 1) << 4 | std::min(e.y / 7, 15));
    } else {
        const int packed = static_cast<int>(shared_cache[7]);
        if (packed != 0 && packed != shared_sighting_seen) {
            shared_sighting_seen = packed;
            add_sighting(vec2{((packed >> 4) - 1) * 7 + 3, (packed & 15) * 7 + 3}, 1);
        }
    }
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

// ---- Per-champion turn state ----
int current_target = -1;
bool was_alive = true;
std::vector<int> death_rounds;  // Rounds this champion died: repeated deaths mean the enemy controls the middle.
bool retreating = false;
float last_hp = 0;
int last_round = -10, enemy_seen_round = -100;
int last_pick_round = -100, last_pick_state = -2;
int big_wait = 0;
int bank_best = UNREACH, bank_stall = 0, bank_blocked_until = 0;
int planned_team = 1;
int alive_cache = 1, alive_round = -10;

// What this champion last saw, printed if it dies before its next turn: when it acted, its health and
// activity, then visible enemies (type, distance, health) and the strength of awake camps in reach.
// Only raw values are stored each turn; formatting costs fuel and happens on death.
struct DeathCtx {
    int round = 0, n = 0;
    float hp = 0;
    const char* act = "";
    std::array<cambc::champion_type, 4> type{};
    std::array<int, 4> d{};
    std::array<float, 4> ehp{};
} death_ctx;

void record_death_ctx() {
    death_ctx.round = S.round;
    death_ctx.hp = S.hp;
    death_ctx.act = last_activity;
    death_ctx.n = 0;
    for (const auto& e : S.enemies) {
        if (death_ctx.n == 4) break;
        const int i = death_ctx.n++;
        death_ctx.type[i] = e.type;
        death_ctx.d[i] = dist(S.me, e.pos);
        death_ctx.ehp[i] = e.hp;
    }
}

void print_death(int round) {
    std::cout << "D" << round << " s" << W.slot << " r" << death_ctx.round << " hp=" << death_ctx.hp << " " << death_ctx.act
              << " en:";
    for (int i = 0; i < death_ctx.n; ++i)
        std::cout << " " << cambc::to_string(death_ctx.type[i]) << "@" << death_ctx.d[i] << "/" << death_ctx.ehp[i];
    std::cout << '\n';
}

int alive_allies() {
    if (alive_round == S.round) return alive_cache;
    int n = 0;
    for (const auto& a : cambc::champions(team::ally))
        if (a.is_alive()) ++n;
    alive_cache = std::max(1, n);
    alive_round = S.round;
    return alive_cache;
}

// ---- Targets ----
distance_field from_me_field() {
    distance_field f;
    bitboard roots, visited;
    roots.clear();
    roots.set(S.me);
    f.compute(W.terrain & ~roots, roots, visited);
    return f;
}

int travel_to(const distance_field& f, const Group& g) {
    int t = UNREACH;
    for (auto s : g.spawns) t = std::min<int>(t, f.get(s));
    return t;
}

// Per-champion choice: rate of value per champion-round, assuming teammates already heading to a group help
// clear it. A defeated group needs only one capturer.
int pick_group(int current) {
    const int round = S.round;
    std::uint64_t gd_fuel = 0;
    const auto pf0 = cambc::fuel_remaining();
    const auto f = from_me_field();
    const auto pf1 = cambc::fuel_remaining();
    const float dps = my_dps();
    const int team_alive = alive_allies();
    double best = 0, current_score = 0;
    int best_i = -1, best_n = 1, current_n = 1;
    for (int i = 0; i < static_cast<int>(W.groups.size()); ++i) {
        const auto& g = W.groups[i];
        const int travel = travel_to(f, g);
        if (travel == UNREACH) continue;
        const double value = g.gems + g.gold * gold_weight(round);
        if (value <= 0) continue;
        bool covered = false;
        for (int b : W.covered_by[i]) if (W.groups[b].state == 0) covered = true;
        if (covered) continue;
        const int others = claimants(i);
        double score = 0;
        int score_n = 1;
        if (g.state == 1) {
            // One capturer: the claimant who gains most from the gold keeps it, everyone else moves on.
            const int mine = 16 * 16;
            bool better_claim = false;
            for (int s = 0; s < MAX_SLOTS && s < static_cast<int>(W.slot_types.size()); ++s)
                if (claim_cache[s] == i && capture_priority(W.slot_types[s]) * 16 + s > mine) better_claim = true;
            if (better_claim || (others > 0 && i != current)) continue;
            // At most two share a capture; extra champions move on.
            if (others >= 2) {
                int lower = 0;
                for (int s = 0; s < W.slot && s < MAX_SLOTS; ++s) if (claim_cache[s] == i) ++lower;
                if (lower >= 2) continue;
            }
            score = value / (travel + 5.0 + g.bank_cost);
        } else if (standoff(g)) {
            const float spell = my_spell_dps();
            if (spell <= 0) continue;
            const int n = others + 1;
            double time = travel + g.hp_left() / (spell * n);
            if (g.state == 2) time += 2.0 * std::max(0, g.respawn_round - round - travel);
            score = value / (time * n + 5 + g.bank_cost * 0.5);
            score_n = n;
        } else {
            const int home = W.spawn_field.get(g.spawns[0]);
            const ClearStats cs = clear_stats(g);
            const std::array<int, 3> sizes{others + 1, std::min(std::max(others + 1, team_alive), others + 2),
                                           std::max(others + 1, team_alive)};
            for (int n : sizes) {
                double time = travel + clear_time(cs, n, dps, S.max_hp, home == UNREACH ? 30 : home);
                if (g.state == 2) time += 2.0 * std::max(0, g.respawn_round - round - travel);
                time += (n - others - 1) * 4;  // Waiting for extra teammates.
                // One champion then captures (5 rounds), walks to an altar and tributes.
                const double sc = value / (time * n + 5 + g.bank_cost * 0.5);
                if (sc > score) score = sc, score_n = n;
            }
        }
        // Groups nearer the enemy spawn are contested: worth less unless they are clearly closer for us.
        const int side = W.group_side[i];
        if (side > -8) {
            int recent = 0;
            for (int r : death_rounds) if (round - r < 400) ++recent;
            (void)recent;  // Aggressive: keep contesting even after deaths.
        }
        if (side > 0) score /= 1.0 + std::min(side, 20) / 20.0;
        // Avoid walking into enemy groups; a lone enemy matters less than several.
        const auto gd0 = cambc::fuel_remaining();
        const double danger = sightings.empty() ? 0.0 : group_danger(g);
        gd_fuel += gd0 - cambc::fuel_remaining();
        if (danger > 0) score /= 1.0 + danger * 0.25;
        if (i == current) current_score = score, current_n = score_n;
        if (score > best) best = score, best_i = i, best_n = score_n;
    }
    TRACE("pick bfs=" << (pf0 - pf1) << " loop=" << (pf1 - cambc::fuel_remaining()) << " danger=" << gd_fuel);
    if (current >= 0 && current_score > 0 && current_score * 1.05 >= best) {
        planned_team = current_n;
        return current;
    }
    planned_team = best_n;
    return best_i;
}

// A defeated group nearby that nobody is capturing yet: one champion stays to capture it.
bool bank_gems() {
    for (auto altar : W.altars) {
        // A locked altar still works: the engine turns the tribute into hits on the lock.
        if (dist(S.me, altar) <= cambc::constants::submit_gems_range) {
            try {
                cambc::self().submit_gems(altar);
                return true;
            } catch (const cambc::error&) {
            }
        }
    }
    return step_field(W.altar_field, W.altar_tiles, cambc::constants::submit_gems_range);
}

// Best camp to hit: biggest strength removed per point of damage; clusters (no strength) last.
// Splash attackers (Varg) also value camps whose neighbours take the splash.
bool splash = false;

const CampSnap* choose_camp(const std::vector<const CampSnap*>& live) {
    const CampSnap* best = nullptr;
    double best_s = -1;
    for (const auto* c : live) {
        double s = (c->str + 1.0) / std::max(1.0f, c->hp);
        if (splash) {
            int neighbours = 0;
            for (const auto* o : live) if (o != c && dist(o->pos, c->pos) <= 1) ++neighbours;
            s *= 1 + neighbours;
        }
        if (s > best_s) best_s = s, best = c;
    }
    return best;
}

void fight_or_approach(int gi) {
    auto& me = cambc::self();
    auto& g = W.groups[gi];
    const int range = S.range;
    std::vector<const CampSnap*> live;
    for (const auto& c : S.camps)
        if (c.group == gi) live.push_back(&c);

    if (live.empty()) {
        if (g.state == 2) {
            // Respawning: a body on a spawn tile delays it, so wait beside the group.
            if (g.tiles.is_set(S.me)) {
                const auto occ = S.occ | g.tiles;
                for (auto d : DIRS) {
                    vec2 t{S.me.x + d.x, S.me.y + d.y};
                    if (cm::is_in_bounds(t) && !W.terrain.is_set(t) && !occ.is_set(t) && safe_move(t)) break;
                }
            } else if (group_field(g).get(S.me) > 2) {
                step_field(group_field(g), g.tiles, 2);
            }
            ACT("resp_wait");
            return;
        }
        // Dead or unseen: walk onto a spawn tile (captures when the group is down).
        if (g.tiles.is_set(S.me)) { ACT("capture"); use_support_abilities(false); return; }
        ACT("to_capture");
        step_field(group_field(g), g.tiles, 0);
        return;
    }


    // Stellar out-ranges ordinary camps (spells 4, camps 3): it farms them from spell range and takes no hits.
    bool caster_standoff = me.champion_name() == cambc::champion_type::stellar;
    bool any_strong = false;
    for (const auto* c : live) {
        if (c->str > 0) any_strong = true;
        if (c->str > 0 && c->range > CAMP_RANGE) caster_standoff = false;
    }
    if (standoff(g) || (caster_standoff && any_strong)) {
        // Stand exactly at spell range of the target and outside every dangerous camp's reach; cast only.
        const CampSnap* target = choose_camp(live);
        bitboard goals, near;
        goals.clear();
        near.clear();
        goals.draw_chebyshev(target->pos, 4.0f);
        for (const auto* c : live)
            if (c->str > 0) near.draw_chebyshev(c->pos, static_cast<float>(c->range));
        goals = goals & ~near;
        ACT("standoff");
        if (goals.is_set(S.me)) {
            cast_from_range(live, *target);
            return;
        }
        if (near.is_set(S.me)) {
            std::vector<vec2> threats;
            for (const auto* c : live) if (c->str > 0) threats.push_back(c->pos);
            step_away(threats);
        } else {
            step_to_tiles(goals);
        }
        if (goals.is_set(S.me)) cast_from_range(live, *target);
        return;
    }

    // Big groups (many elks) shred champions who arrive one by one: wait for most of the team.
    if (!g.damaged() && g.strength_left() >= 200) {
        int present = 1;
        for (const auto& a : S.allies)
            for (const auto* c : live)
                if (dist(a.pos, c->pos) <= 6) { ++present; break; }
        if (present < std::min(4, alive_allies()) && big_wait < 25) {
            ++big_wait;
            if (group_field(g).get(S.me) > 5) step_field(group_field(g), g.tiles, 5);
            ACT("gather");
            return;
        }
    }
    big_wait = 0;
    STAGE("cf choose");
    const CampSnap* target = choose_camp(live);
    // Spells reach further than camps: cast before closing in.
    if (dist(S.me, target->pos) > range) {
        if (use_camp_abilities(live, *target, g.damaged()) && !me.can_move()) return;
        bitboard goals;
        goals.clear();
        goals.draw_chebyshev(target->pos, static_cast<float>(range));
        if (!step_to_tiles(goals)) step_field(group_field(g), g.tiles, 0);
    }
    STAGE("cf hit");
    // Hit the chosen camp if in range, otherwise the weakest one in range.
    const CampSnap* hit = dist(S.me, target->pos) <= range ? target : nullptr;
    if (!hit) {
        std::vector<const CampSnap*> reach;
        for (const auto* c : live) if (dist(S.me, c->pos) <= range) reach.push_back(c);
        if (!reach.empty()) hit = choose_camp(reach);
    }
    ACT("approach");
    if (!hit) return;
    ACT("fight");
    attack_unit(hit->camp);
    if (!use_camp_abilities(live, *hit, true)) try_attack_reset_and_hit(hit->camp);
    use_support_abilities(true);
}

}  // namespace

void Bot::play_turn() {
    if (!W.ready) {
        init_world();
        splash = cambc::self().passive() == cambc::passive_type::splash_attack;
        const auto type = cambc::self().champion_name();
        fragile = type == cambc::champion_type::cassi || type == cambc::champion_type::issac;
    }
    auto& me = cambc::self();
    const int round = static_cast<int>(cambc::round_number());
    tracing = false;
    log_rounds = false;

    if (round % 20 == 0 || (!me.is_alive() && was_alive)) {
        std::cout << "R" << round << " s" << W.slot << " " << cambc::to_string(me.champion_name()) << " hp=" << me.health() << "/"
                  << me.max_health() << " gems=" << me.gem_count() << " gold=" << me.gold_count() << " tgt=" << current_target
                  << (me.is_alive() ? " pos=" + cambc::to_string(me.position()) : std::string(" DEAD")) << '\n';
    }
    if (W.slot == 0 && round % 10 == 0)
        std::cout << "G " << round << " " << cambc::global_submitted_gems(team::ally) << " "
                  << cambc::global_submitted_gems(team::enemy) << '\n';
    if (log_rounds && round > 1) std::cout << "W " << round - 1 << " " << W.slot << " " << current_target << " " << activity << '\n';
    count_activity();
    last_activity = activity;
    activity = "other";
    if (round % 250 == 0 || round == 30) {
        std::cout << "A s" << W.slot << " r" << round << " atk=" << n_attack << " reset=" << n_reset << " cc=" << n_cc
                  << " aoe=" << n_aoe << " dmg=" << n_dmg;
        for (size_t i = 0; i < act_names.size() && act_names[i]; ++i) std::cout << " " << act_names[i] << "=" << act_counts[i];
        std::cout << '\n';
    }
    if (!me.is_alive() && was_alive && round > 1) {
        if (death_ctx.n > 0) death_rounds.push_back(round);  // Camp deaths say nothing about enemy control.
        print_death(round);
    }
    was_alive = me.is_alive();
    if (!was_alive) {
        ACT("dead");
        shop();
        write_claim(-1);
        retreating = false;
        return;
    }
    if (me.is_recalling()) { ACT("recall"); return; }
    if (me.is_submitting_gems()) { ACT("tribute"); return; }
    if (me.is_teleporting()) return;

    prof_n = 0;
    STAGE("snapshot");
    take_snapshot();
    STAGE("knowledge");
    refresh_claims();
    update_knowledge();
    build_phantoms();
    read_broadcast();
    record_sightings();
    record_death_ctx();
    STAGE("enemies");
    place_ward_forward();
    const vec2 p = S.me;
    const bool at_spawn = W.ally_spawn.is_set(p);
    if (at_spawn) {
        shop();
        retreating = false;
    }

    // Damage not explained by camps comes from an enemy, possibly hidden in a bush.
    const float incoming = camp_incoming(p);
    const float taken = last_round + 1 == round ? last_hp - S.hp : 0.0f;
    // Some champions act only every other round: camps then land several hits per step we take.
    const int turn_gap = round - last_round >= 1 && round - last_round <= 3 ? round - last_round : 1;
    const float taken_rate = round - last_round <= 3 ? (last_hp - S.hp) / turn_gap : 0.0f;
    last_hp = S.hp;
    last_round = round;
    if (taken > incoming + 1.0f) {
        bool blamed = false;
        for (const auto& k : known_camps) {
            if (k.group < 0 || k.str < (taken - incoming) * 0.8f) continue;
            auto& g = W.groups[k.group];
            const vec2 pos = g.spawns[k.idx];
            if (g.state != 0 || S.visible.is_set(pos) || dist(p, pos) > k.range) continue;
            g.awake_round = round;
            blamed = true;
        }
        if (!blamed) enemy_seen_round = enemy_seen_at = round;
    }
    // Big hits are rare; log the situation so platform replays show how we get caught.
    if (taken > S.max_hp * 0.25f) {
        std::cout << "H" << round << " s" << W.slot << " " << cambc::to_string(me.champion_name()) << " at " << cambc::to_string(p)
                  << " hp=" << S.hp << "/" << S.max_hp << " took=" << taken << " camp=" << incoming << " last=" << last_activity
                  << " allies=" << S.allies.size() << " enemies:";
        for (const auto& e : S.enemies)
            std::cout << " " << cambc::to_string(e.ch.champion_name()) << "@" << dist(p, e.pos) << "(" << e.hp << "/b" << e.burst << ")";
        std::cout << '\n';
    }

    // Compare nearby strength with visible enemies.
    // Lanchester-style strength: total health times total damage per round on each side.
    float enemy_hp = 0, enemy_dps = 0, ally_hp = S.hp, ally_dps = my_dps();
    int enemy_count = 0, ally_count = 1;
    const ChampSnap* prey = nullptr;
    for (const auto& e : S.enemies) {
        if (dist(p, e.pos) > 6) continue;
        // Enemies resting on their own spawn only matter when they can already hit us; they cannot be hit.
        const bool safe_home = W.enemy_spawn.is_set(e.pos);
        if (safe_home && dist(p, e.pos) > e.range) continue;
        enemy_seen_round = round;
        enemy_hp += e.hp;
        enemy_dps += e.dps;
        ++enemy_count;
        // Focus whoever dies fastest relative to the damage they deal.
        if (!safe_home && dist(p, e.pos) <= std::max(S.range, 4) && (!prey || e.dps / e.hp * (1.0f + e.gems / 40.0f) > prey->dps / prey->hp * (1.0f + prey->gems / 40.0f))) prey = &e;
    }
    // Enemies seen in the last 3 rounds but now hidden (bush, fog, behind a wall) still fight: count them.
    {
        struct Seen { std::uint32_t id; vec2 pos; float hp, dps; int round; };
        static std::vector<Seen> seen;
        for (const auto& e : S.enemies) {
            const auto id = handle_id(e.ch);
            bool found = false;
            for (auto& s : seen) if (s.id == id) { s = {id, e.pos, e.hp, e.dps, round}; found = true; }
            if (!found) seen.push_back({id, e.pos, e.hp, e.dps, round});
        }
        for (const auto& s : seen) {
            if (s.round == round || round - s.round > 3 || dist(p, s.pos) > 5 || W.enemy_spawn.is_set(s.pos)) continue;
            enemy_hp += s.hp;
            enemy_dps += s.dps;
            ++enemy_count;
        }
    }
    // An enemy fighting a nearby ally is our fight too: go and help.
    if (!prey)
        for (const auto& e : S.enemies) {
            if (W.enemy_spawn.is_set(e.pos) || dist(p, e.pos) > 8) continue;
            bool engaged = false;
            for (const auto& a : S.allies) if (dist(a.pos, e.pos) <= 3) engaged = true;
            if (engaged && (!prey || e.hp < prey->hp)) prey = &e;
        }
    for (const auto& a : S.allies)
        if (dist(p, a.pos) <= 5) ally_hp += a.hp, ally_dps += a.dps, ++ally_count;
    const float enemy_power = enemy_hp * enemy_dps, ally_power = ally_hp * ally_dps;

    // Enemies whose combined one-round burst could kill us from where they stand (after a step).
    float lethal = 0;
    for (const auto& e : S.enemies)
        if (!W.enemy_spawn.is_set(e.pos) && dist(p, e.pos) <= e.reach + 1) lethal += e.burst;
    const bool in_kill_range = lethal >= S.hp * 0.9f;
    // Fight when stronger and not outnumbered, when the target is nearly dead, or from the safety of spawn.
    // Cassi and Issac die together, so they only join fights with a clear edge.
    // Play the fight out a few rounds with live cooldowns instead of comparing raw totals.
    bool winning = false, sim_me_dies = false;
    if (prey) {
        using ct = cambc::champion_type;
        std::array<std::vector<SimUnit>, 2> side;
        std::vector<vec2> pos[2];
        std::vector<ct> types[2];
        auto add = [&](int s, float hp, float str, int range, vec2 at, std::array<SimSlot, 2> slots, ct type) {
            SimUnit x;
            x.hp = hp, x.str = str, x.range = range, x.slots = slots;
            side[s].push_back(x);
            pos[s].push_back(at);
            types[s].push_back(type);
        };
        add(0, S.hp, S.str, S.range, p, read_slots(cambc::self()), cambc::self().champion_name());
        for (const auto& a : S.allies)
            if (dist(p, a.pos) <= 8) add(0, a.hp, a.str, a.range, a.pos, read_slots(a.ch), a.type);
        for (const auto& e : S.enemies)
            if (dist(p, e.pos) <= 8 && !(W.enemy_spawn.is_set(e.pos) && dist(p, e.pos) > e.range))
                add(1, e.hp, e.str, e.range, e.pos, read_slots(e.ch), e.type);
        for (int s = 0; s < 2; ++s) {
            for (size_t i = 0; i < side[s].size(); ++i) {
                int d = 99;
                for (auto q : pos[1 - s]) d = std::min(d, dist(pos[s][i], q));
                side[s][i].d = d;
                for (size_t j = 0; j < side[s].size(); ++j)
                    if ((types[s][i] == ct::cassi && types[s][j] == ct::issac) || (types[s][i] == ct::issac && types[s][j] == ct::cassi))
                        side[s][i].link = static_cast<int>(j);
            }
        }
        const SimResult res = simulate_fight(side, 3, true);
        sim_me_dies = res.unit0_dead;
        winning = !side[1].empty()
            && (res.dead[1] > res.dead[0] || (res.dead[1] == res.dead[0] && res.hp_frac[0] > res.hp_frac[1] + 0.2f))
            && !(sim_me_dies && res.dead[1] == 0);
    }
    const bool finisher = prey && prey->hp <= ally_dps * 2.5f && S.hp > S.max_hp * 0.3f && !sim_me_dies;
    // A carrier with a full bag is worth a risky fight: the kill takes all of it.
    const bool rich = prey && prey->gems >= 30 && ally_power >= enemy_power * 0.5f && S.hp > S.max_hp * 0.5f && !sim_me_dies;
    if (prey && (winning || finisher || rich || (at_spawn && dist(p, prey->pos) <= S.range))) {
        STAGE("fight enemy");
        ACT("pvp");
        // Favourable fight: focus the weakest enemy, spells first.
        use_champion_abilities(*prey);
        if (dist(S.me, prey->pos) <= S.range) {
            if (attack_unit(prey->ch)) try_attack_reset_and_hit(prey->ch);
            return;
        }
        // Close in through the tile least exposed to enemy bursts; melee strikes after the step.
        if (me.can_move()) {
            vec2 best{-1, -1};
            float best_exposure = 0;
            int best_d = 99;
            for (auto d : DIRS) {
                const vec2 t{S.me.x + d.x, S.me.y + d.y};
                if (!cm::is_in_bounds(t) || W.terrain.is_set(t) || S.occ.is_set(t)) continue;
                const int pd = dist(t, prey->pos);
                if (pd >= dist(S.me, prey->pos)) continue;
                float exposure = 0;
                for (const auto& e : S.enemies)
                    if (!W.enemy_spawn.is_set(e.pos) && dist(t, e.pos) <= e.reach) exposure += e.burst;
                const bool better = best.x < 0 || (pd <= S.range) > (best_d <= S.range)
                    || ((pd <= S.range) == (best_d <= S.range) && (exposure < best_exposure || (exposure == best_exposure && pd < best_d)));
                if (better) best = t, best_exposure = exposure, best_d = pd;
            }
            if (best.x >= 0 ? safe_move(best) : (me.move_towards(prey->pos), false)) {
                if (dist(S.me, prey->pos) <= S.range && attack_unit(prey->ch)) try_attack_reset_and_hit(prey->ch);
            }
        }
        return;
    }
    bool threatened = false;
    for (const auto& e : S.enemies)
        if (dist(p, e.pos) <= std::max(e.range + 2, e.dps > e.str * 1.15f ? 6 : 0) && !W.enemy_spawn.is_set(e.pos))
            threatened = true;
    const bool hit_by_enemy = taken > incoming + 1.0f;
    const bool losing = enemy_count > ally_count || enemy_power > ally_power * 0.9f || S.hp < S.max_hp * 0.4f
        || in_kill_range;
    // Not engaging: from here on, moves keep out of enemy reach.
    S.avoid_danger = !S.danger.empty();
    if ((threatened && losing) || (hit_by_enemy && !prey)) {
        if (prey) use_champion_abilities(*prey);
        const bool healthy = S.hp >= S.max_hp * 0.5f && !hit_by_enemy;
        if (healthy && !in_danger(S.me)) {
            // Already out of reach: keep working, staying out of it.
        } else if (healthy && step_out_of_danger()) {
            ACT("kite");
            return;
        } else {
            // Caught by a lone chaser far from home: it is as fast as we are, so running only hands it free hits.
            const ChampSnap* chaser = nullptr;
            int near_enemies = 0;
            for (const auto& e : S.enemies) {
                if (W.enemy_spawn.is_set(e.pos) || dist(p, e.pos) > 5) continue;
                ++near_enemies;
                if (dist(p, e.pos) <= 1) chaser = &e;
            }
            if (chaser && near_enemies == 1 && W.spawn_field.get(p) > 4) {
                ACT("duel");
                use_champion_abilities(*chaser);
                if (dist(S.me, chaser->pos) <= S.range && attack_unit(chaser->ch)) try_attack_reset_and_hit(chaser->ch);
                return;
            }
            ACT("flee");
            // Hurt, hit by something unseen, or cornered: run home, striking whoever is still in reach.
            S.avoid_danger = false;
            if (!at_spawn) walk_home();
            for (const auto& e : S.enemies)
                if (!W.enemy_spawn.is_set(e.pos) && dist(S.me, e.pos) <= S.range && attack_unit(e.ch)) break;
            write_claim(-1);
            return;
        }
    }

    // Attack on sight, as every top team does: hit the weakest enemy in reach (spells within 4) before the plan.
    // Melee keeps its move after attacking; ranged attacks cost the move, so only when healthy.
    {
        const ChampSnap* t = nullptr;
        for (const auto& e : S.enemies) {
            if (W.enemy_spawn.is_set(e.pos) || dist(S.me, e.pos) > std::max(S.range, 4)) continue;
            if (!t || e.hp / e.max_hp < t->hp / t->max_hp) t = &e;
        }
        if (t) {
            use_champion_abilities(*t);
            if (dist(S.me, t->pos) <= S.range && (S.range <= 1 || S.hp > S.max_hp * 0.5f) && attack_unit(t->ch))
                try_attack_reset_and_hit(t->ch);
        }
    }

    if (at_spawn && S.hp < S.max_hp * 0.9f) {
        ACT("heal_wait");
        write_claim(-1);
        return;
    }

    STAGE("retreat");
    // Leave camp range before the next hits could kill. Each camp hits only its nearest champion, so count the
    // camps nobody else is closer to, or what we just took.
    // Every camp aiming at us hits each round until we are out of all their reaches, so sum them and count the
    // real path out (stepping away from one camp can keep us inside another's range).
    float strongest = 0;
    int steps_out = 0;
    bool in_camp_range = false;
    std::vector<CampSnap> near_camps = S.camps;
    near_camps.insert(near_camps.end(), S.phantoms.begin(), S.phantoms.end());
    bitboard reach;
    reach.clear();
    for (const auto& c : near_camps) {
        const int d = dist(p, c.pos);
        if (d > c.range + 3 || !camp_awake(c)) continue;
        reach.draw_chebyshev(c.pos, static_cast<float>(c.range));
        if (d > c.range) continue;
        in_camp_range = true;
        steps_out = std::max(steps_out, c.range + 1 - d);
        bool someone_closer = false;
        for (const auto& a : S.allies) if (dist(a.pos, c.pos) < d) { someone_closer = true; break; }
        if (!someone_closer)
            for (const auto& e : S.enemies) if (dist(e.pos, c.pos) < d) { someone_closer = true; break; }
        if (!someone_closer) strongest += c.str;
    }
    const auto safe_tiles = ~reach & ~W.terrain;
    if (in_camp_range) {
        const int path = steps_to_tiles(safe_tiles);
        if (path != UNREACH) steps_out = std::max(steps_out, path);
    }
    const float danger = std::max(strongest, taken);
    // Camps land one more hit as we step out of reach, so leaving takes steps_out + 1 hits after this one.
    if (danger > 0 && S.hp < danger * (steps_out + 1.0f) + 40.0f) retreating = true;
    if (retreating) {
        if (in_camp_range) {
            ACT("retreat");
            if (!step_to_tiles(safe_tiles)) step_away(camp_threats(p, 1));
            return;
        }
        // Out of reach: rejoin if still healthy, otherwise go home to heal.
        const float hardest = current_target >= 0 ? W.groups[current_target].hardest() : 0.0f;
        if (S.hp >= S.max_hp * 0.5f && S.hp >= hardest * 6.0f + 40.0f) {
            retreating = false;
        } else {
            write_claim(-1);
            ACT("home_heal");
            if (me.gem_count() > 0 && W.altar_field.get(p) <= 3 && bank_gems()) return;
            go_home();
            return;
        }
    }

    // Heal when worn down and no fight holds us.
    if (!at_spawn && S.hp < S.max_hp * 0.35f && incoming == 0) {
        retreating = true;
        write_claim(-1);
        ACT("home_heal");
        go_home();
        return;
    }

    STAGE("bank");
    // Bank carried gems when holding a lot or an altar is close.
    const int gems = static_cast<int>(me.gem_count());
    if (gems > 0 && incoming == 0) {
        const int altar_d = W.altar_field.get(p);
        const bool endgame = round > 1900
            || cambc::global_submitted_gems(team::ally) + gems >= cambc::constants::winning_gems;
        const bool risky = S.round - enemy_seen_round < 30
            || cambc::global_submitted_gems(team::enemy) >= 500;
        // A far altar is worth one trip for two captures rather than one.
        const int threshold = altar_d > 10 ? 40 : 20;
        if ((gems >= threshold || altar_d <= 6 || risky) && S.round >= bank_blocked_until || endgame) {
            // Give up for a while if the way to the altar makes no progress (blocked or contested).
            if (altar_d < bank_best) bank_best = altar_d, bank_stall = 0;
            else if (++bank_stall > 6) bank_blocked_until = S.round + 40, bank_best = UNREACH, bank_stall = 0;
            write_claim(-1);
            ACT("bank");
            if (bank_gems()) return;
        } else {
            bank_best = UNREACH;
            bank_stall = 0;
        }
    }

    STAGE("shop");
    // Spend gold: shards add permanent stats, so a trip home pays off once enough has piled up.
    const bool remote_shop = me.passive() == cambc::passive_type::remote_shop;
    if (remote_shop) shop();
    const int gold = static_cast<int>(me.gold_count());
    if (!at_spawn && incoming == 0 && round < 1850 && !remote_shop) {
        const int home = W.spawn_field.get(p);
        if (gold >= 150 || (gold >= 90 && home <= 8)) {
            ACT("shop_trip");
            write_claim(-1);
            go_home();
            return;
        }
    }

    STAGE("pick");
    // Keep fighting an awake target; one champion captures; the rest follow the team target.
    const bool in_fight = current_target >= 0 && W.groups[current_target].state == 0
        && !camp_threats(p, 1).empty();
    // Re-plan every few rounds, or at once when the target's state changes.
    const int target_state = current_target >= 0 ? W.groups[current_target].state : -1;
    if (!in_fight && (S.round - last_pick_round >= 3 || target_state != last_pick_state)) {
        current_target = pick_group(current_target);
        last_pick_round = S.round;
        last_pick_state = current_target >= 0 ? W.groups[current_target].state : -1;
    }
    write_claim(current_target);
    STAGE("camp fight");
    if (current_target < 0) {
        if (gems > 0) bank_gems();
    } else {
        fight_or_approach(current_target);
    }
    STAGE("end");
    if (tracing) {
        std::cout << "P s" << W.slot;
        for (int i = 1; i < prof_n; ++i) std::cout << " " << prof_names[i - 1] << "=" << (prof_fuel[i - 1] - prof_fuel[i]);
        std::cout << '\n';
    }
}
