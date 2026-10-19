// Champion decisions: farm camp groups as a coordinated team, bank gems, recall to heal and shop.
//
// Facts this relies on (measured locally): camps never regenerate health, they do not chase, a whole group
// wakes when one member is hit, and standing on spawn heals almost fully in one round. So damage dealt to a
// camp is banked: fight until low, step out of range, recall, heal and come back.
#include <cambc.h>
#include "bot.h"
#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>
#include <iostream>
#include <memory>
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
constexpr int MAX_SLOTS = 6;  // Shared memory bytes 0..5 hold each champion's claimed group + 1.
constexpr int CAMP_RANGE = 3;

int dist(vec2 a, vec2 b) { return static_cast<int>(a.chebyshev_distance(b)); }

bool tracing = false;
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
    std::unique_ptr<distance_field> field;

    float hp_left() const { float s = 0; for (float h : hp) s += h; return s; }
    float strength_left() const {
        float s = 0;
        for (size_t i = 0; i < hp.size(); ++i) if (hp[i] > 0) s += strength[i];
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
    bitboard ally_spawn, altar_tiles;
    std::vector<vec2> altars;
    std::vector<Group> groups;
    distance_field altar_field, spawn_field;
    int slot = 0, team_count = 1;
};

World W;

void compute_field(distance_field& field, const bitboard& roots) {
    bitboard visited;
    field.compute(W.terrain & ~roots, roots, visited);
}

distance_field& group_field(Group& g) {
    if (!g.field) {
        g.field = std::make_unique<distance_field>();
        compute_field(*g.field, g.tiles);
    }
    return *g.field;
}

std::uint32_t handle_id(const cambc::champion& c) {
    return static_cast<std::uint32_t>(static_cast<cambc::handle_champion_t>(c));
}

void init_world() {
    auto& me = cambc::self();
    W.terrain = cm::walls() | cm::holes() | cm::altars() | cm::spawn_region(team::enemy);
    W.ally_spawn = cm::spawn_region(team::ally);
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
    compute_field(W.altar_field, cm::altars());
    compute_field(W.spawn_field, W.ally_spawn);

    std::vector<std::uint32_t> ids;
    for (const auto& a : cambc::champions(team::ally)) ids.push_back(handle_id(a));
    std::sort(ids.begin(), ids.end());
    W.team_count = static_cast<int>(ids.size());
    W.slot = static_cast<int>(std::find(ids.begin(), ids.end(), handle_id(me)) - ids.begin());
    W.ready = true;
}

int group_of_camp(vec2 spawn) {
    for (int i = 0; i < static_cast<int>(W.groups.size()); ++i)
        if (W.groups[i].tiles.is_set(spawn)) return i;
    return -1;
}

void update_knowledge() {
    const auto visible = cv::visible_tiles();
    const int round = static_cast<int>(cambc::round_number());
    for (auto& g : W.groups) {
        if ((g.tiles & visible).is_empty()) {
            if (g.state == 2 && round >= g.respawn_round) { g.state = 0; g.reset(); }
            continue;
        }
        int prev = g.state;
        try {
            const auto st = g.group.state();
            if (std::holds_alternative<cm::camp_group_alive>(st)) g.state = 0;
            else if (std::holds_alternative<cm::camp_group_reward_available>(st)) g.state = 1;
            else {
                g.state = 2;
                g.respawn_round = round + std::get<cm::camp_group_respawning>(st).timer;
            }
        } catch (const cambc::error&) {
        }
        if (g.state == 0 && prev == 2) g.reset();
        if (g.state != 0) {
            std::fill(g.hp.begin(), g.hp.end(), 0.0f);
            continue;
        }
        for (size_t i = 0; i < g.spawns.size(); ++i) {
            if (!visible.is_set(g.spawns[i])) continue;
            g.hp[i] = 0;
            if (cv::has_camp(g.spawns[i])) {
                const auto c = cv::camp_at(g.spawns[i]);
                g.hp[i] = c.health();
            }
        }
    }
}

// ---- Shared memory claims ----
int read_claim(int slot) {
    std::byte b{};
    cambc::shared_memory.read(slot, std::span{&b, 1});
    return static_cast<int>(b) - 1;
}
void write_claim(int group) {
    if (W.slot >= MAX_SLOTS) return;
    std::byte b{static_cast<unsigned char>(group + 1)};
    cambc::shared_memory.write(W.slot, std::span{&b, 1});
}
int claimants(int group) {
    int n = 0;
    for (int s = 0; s < std::min(W.team_count, MAX_SLOTS); ++s)
        if (s != W.slot && read_claim(s) == group) ++n;
    return n;
}

// ---- Movement ----
bitboard occupied_tiles() {
    auto occ = cv::champion_tiles() | cv::camp_tiles() | cv::teleport_tiles();
    occ.set(cambc::self().position(), false);
    return occ;
}

constexpr std::array<vec2, 8> DIRS{vec2{1, 0}, vec2{-1, 0}, vec2{0, 1}, vec2{0, -1}, vec2{1, 1}, vec2{1, -1},
    vec2{-1, 1}, vec2{-1, -1}};

bool safe_move(vec2 t) {
    try {
        return cambc::self().move_absolute(t);
    } catch (const cambc::error&) {
        return false;
    }
}

// Take the free neighbour with the lowest field value below `here`; hidden blockers are skipped.
bool descend(const distance_field& field, bitboard occ, int here) {
    auto& me = cambc::self();
    const vec2 p = me.position();
    for (int attempt = 0; attempt < 3; ++attempt) {
        vec2 best = p;
        int best_d = here;
        for (auto d : DIRS) {
            vec2 t{p.x + d.x, p.y + d.y};
            if (!cm::is_in_bounds(t) || W.terrain.is_set(t) || occ.is_set(t)) continue;
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
bool step_static(const distance_field& field, const bitboard& occ, int here) {
    auto& me = cambc::self();
    const vec2 p = me.position();
    if (here >= 4 && me.can_cast()) {
        for (const auto& ab : me.abilities()) {
            if (!ab.is_dash() || !ab.is_ready()) continue;
            vec2 best = p;
            int best_d = here - 1;
            for (auto t : ab.valid_tiles().positions()) {
                if (occ.is_set(t) || W.terrain.is_set(t)) continue;
                const int d = field.get(t);
                if (d < best_d) best_d = d, best = t;
            }
            try {
                if (best != p && ab.use(best)) {
                    if (me.can_move()) descend(field, occupied_tiles(), field.get(me.position()));
                    return true;
                }
            } catch (const cambc::error&) {
            }
        }
    }
    return descend(field, occ, here);
}

// Step towards `roots` (field value `stop_at` or less counts as arrived); route around occupants if needed.
bool step_field(const distance_field& field, const bitboard& roots, int stop_at = 0) {
    auto& me = cambc::self();
    if (!me.can_move()) return false;
    const int here = field.get(me.position());
    if (here <= stop_at) return false;
    const auto occ = occupied_tiles();
    if (step_static(field, occ, here)) return true;
    if (!me.can_move()) return false;
    distance_field local;
    bitboard visited, mine;
    mine.clear();
    mine.set(me.position());
    const auto free_roots = roots & ~occ;
    local.compute_to((W.terrain | occ) & ~free_roots & ~mine, free_roots, mine, visited);
    const int local_here = local.get(me.position());
    if (local_here == UNREACH) return false;
    return descend(local, occ, local_here);
}

// Walk to any free tile of `goals` using a fresh field around current occupants.
bool step_to_tiles(const bitboard& goals) {
    auto& me = cambc::self();
    if (!me.can_move() || goals.is_set(me.position())) return false;
    const auto occ = occupied_tiles();
    bitboard visited, mine;
    mine.clear();
    mine.set(me.position());
    const auto free_goals = goals & ~occ & ~W.terrain;
    if (free_goals.is_empty()) return false;
    distance_field local;
    local.compute_to((W.terrain | occ) & ~free_goals & ~mine, free_goals, mine, visited);
    const int here = local.get(me.position());
    if (here == UNREACH) return false;
    return step_static(local, occ, here);
}

// Move to the free neighbour that maximises distance from the given threats, preferring home.
bool step_away(const std::vector<vec2>& threats) {
    auto& me = cambc::self();
    if (!me.can_move() || threats.empty()) return false;
    const vec2 p = me.position();
    const auto occ = occupied_tiles();
    auto score = [&](vec2 t) {
        int m = 1 << 20;
        for (auto th : threats) m = std::min(m, dist(t, th));
        return std::min(m, CAMP_RANGE + 1) * 1000 - W.spawn_field.get(t);
    };
    vec2 best = p;
    int best_s = score(p);
    for (auto d : DIRS) {
        vec2 t{p.x + d.x, p.y + d.y};
        if (!cm::is_in_bounds(t) || W.terrain.is_set(t) || occ.is_set(t)) continue;
        const int s = score(t);
        if (s > best_s) best_s = s, best = t;
    }
    return best != p && safe_move(best);
}

// ---- Shopping ----
enum class Role { tank, fighter, caster };

Role role_of(cambc::champion_type t) {
    using ct = cambc::champion_type;
    switch (t) {
        case ct::ryth: case ct::marcella: case ct::varg: case ct::issac: case ct::ren: return Role::tank;
        case ct::stellar: case ct::prism: case ct::cassi: return Role::caster;
        default: return Role::fighter;
    }
}

void shop() {
    auto& me = cambc::self();
    using it = cambc::item_type;
    const auto role = role_of(me.champion_name());
    std::array<it, 3> plan;
    if (role == Role::tank)
        plan = {it::jungle_shard_of_health, it::monster_shard_of_strength, it::power_shard_of_strength};
    else if (role == Role::caster)
        plan = {it::monster_shard_of_focus, it::jungle_shard_of_health, it::power_shard_of_focus};
    else
        plan = {it::monster_shard_of_strength, it::jungle_shard_of_health, it::power_shard_of_strength};
    for (int guard = 0; guard < 20; ++guard) {
        const auto counts = me.item_count();
        it choice = plan[2];
        for (int i = 0; i < 2; ++i) {
            const auto emblem = plan[i].result();
            if (emblem && counts[*emblem] == 0) { choice = plan[i]; break; }
        }
        if (me.gold_count() < choice.cost() || !me.can_buy(choice)) return;
        me.buy(choice);
    }
}

// ---- Combat helpers ----
float my_dps() {
    auto& me = cambc::self();
    float d = me.strength();
    for (const auto& ab : me.abilities()) {
        if (ab.is_damage() || ab.is_aoe_damage()) d += ab.damage_amount() / 8.0f;
        if (ab.is_attack_reset()) d += me.strength() / 8.0f;
    }
    return d;
}

bool use_offensive_abilities(const cambc::unit& target, bool target_is_camp) {
    auto& me = cambc::self();
    if (!me.can_cast()) return false;
    for (const auto& ab : me.abilities()) {
        if (!ab.is_ready()) continue;
        try {
            if (ab.is_damage() || ab.is_cc()) {
                if (!ab.valid_tiles().is_set(target.position())) continue;
                const bool ok = target_is_camp ? ab.use(static_cast<const cambc::camp&>(target))
                                               : ab.use(static_cast<const cambc::champion&>(target));
                if (ok) return true;
            } else if (ab.is_aoe_damage()) {
                if (!ab.valid_tiles().is_set(target.position())) continue;
                if (ab.use(target.position())) return true;
            }
        } catch (const cambc::error&) {
        }
    }
    return false;
}

// Spend one cast on camps: stun the strongest unstunned attacker, else the best area hit, else burst `focus`.
bool use_camp_abilities(const std::vector<cambc::camp>& live, const cambc::camp& focus, bool awake) {
    auto& me = cambc::self();
    if (!me.can_cast()) return false;
    for (const auto& ab : me.abilities()) {
        if (!ab.is_ready() || !ab.is_cc()) continue;
        const auto tiles = ab.valid_tiles();
        const cambc::camp* best = nullptr;
        for (const auto& c : live) {
            if (c.strength() <= 0 || !tiles.is_set(c.position())) continue;
            if (awake && c.buffs().has_stun()) continue;
            if (!best || c.strength() > best->strength()) best = &c;
        }
        // Stuns only matter once the group fights back.
        if (!best || !awake) continue;
        try {
            if (ab.can_target_ground() ? ab.use(best->position()) : ab.use(*best)) return true;
        } catch (const cambc::error&) {
        }
    }
    for (const auto& ab : me.abilities()) {
        if (!ab.is_ready() || !ab.is_aoe_damage()) continue;
        const auto tiles = ab.valid_tiles();
        vec2 best_tile{-1, -1};
        int best_hits = 0;
        for (const auto& c : live) {
            for (int dx = -1; dx <= 1; ++dx) for (int dy = -1; dy <= 1; ++dy) {
                const vec2 t{c.position().x + dx, c.position().y + dy};
                if (!cm::is_in_bounds(t) || !tiles.is_set(t)) continue;
                int hits = 0;
                for (const auto& o : live) if (dist(o.position(), t) <= 1) ++hits;
                if (hits > best_hits) best_hits = hits, best_tile = t;
            }
        }
        if (best_hits == 0) continue;
        try {
            if (ab.use(best_tile)) return true;
        } catch (const cambc::error&) {
        }
    }
    for (const auto& ab : me.abilities()) {
        if (!ab.is_ready() || !ab.is_damage()) continue;
        if (!ab.valid_tiles().is_set(focus.position())) continue;
        try {
            if (ab.use(focus)) return true;
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
            if (ab.use() && me.can_attack() && target.health() > 0) {
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
                const cambc::champion* best = nullptr;
                float best_missing = ab.heal_amount() * 0.6f;
                const auto allies = cv::champions(team::ally);
                for (const auto& a : allies) {
                    if (handle_id(a) == handle_id(me) || !a.is_alive() || !a.is_visible()) continue;
                    const float missing = a.max_health() - a.health();
                    if (missing > best_missing && ab.valid_tiles().is_set(a.position())) best_missing = missing, best = &a;
                }
                if (best && ab.use(*best)) return;
            }
            if (ab.is_shield() && in_combat && me.health() < me.max_health() * 0.85f) {
                if (ab.use()) return;
            }
        } catch (const cambc::error&) {
        }
    }
}

// Live camps of awake (damaged) groups within camp range of a tile.
std::vector<vec2> camp_threats(vec2 at, int range) {
    std::vector<vec2> out;
    for (const auto& c : cv::camps()) {
        if (!c.is_visible() || c.health() <= 0 || dist(at, c.position()) > range) continue;
        const int gi = group_of_camp(c.spawn_position());
        if (gi >= 0 && W.groups[gi].damaged()) out.push_back(c.position());
    }
    return out;
}

float camp_incoming(vec2 at) {
    float d = 0;
    for (const auto& c : cv::camps()) {
        if (!c.is_visible() || c.health() <= 0 || dist(at, c.position()) > c.attack_range()) continue;
        const int gi = group_of_camp(c.spawn_position());
        if (gi >= 0 && W.groups[gi].damaged()) d += c.strength();
    }
    return d;
}

// Estimated rounds of this champion's time to clear a group, including heal trips.
double clear_time(const Group& g, int n, float dps, float hp, int home_dist) {
    const double team_dps = std::max(1.0, static_cast<double>(dps) * n);
    const double t_fight = g.hp_left() / team_dps;
    const double damage = t_fight * g.strength_left() * (g.spawns.size() > 1 ? 0.7 : 1.0);
    const double budget = 0.6 * hp * n;
    const double trips = std::max(0.0, damage / budget - 1.0);
    return t_fight + trips * (6.0 + home_dist) / n;
}

// Gold buys stats early; late it only matters as a tiebreak.
double gold_weight(int round) { return round < 1400 ? 0.15 : 0.05; }

// ---- Per-champion turn state ----
int current_target = -1;
bool was_alive = true;
bool retreating = false;
float last_hp = 0;
int last_round = -10, enemy_seen_round = -100;

int planned_team = 1;  // Team size the chosen group was scored with.
int gather_turns = 0;

int alive_allies() {
    int n = 0;
    for (const auto& a : cambc::champions(team::ally))
        if (a.is_alive()) ++n;
    return n;
}

// Score each group per champion-round, letting big groups assume more teammates will join.
int pick_group() {
    auto& me = cambc::self();
    const vec2 p = me.position();
    const int round = static_cast<int>(cambc::round_number());
    const float dps = my_dps();
    const float hp = me.max_health();
    const int team_alive = std::max(1, alive_allies());
    double best = 0;
    int best_i = -1;
    for (int i = 0; i < static_cast<int>(W.groups.size()); ++i) {
        auto& g = W.groups[i];
        auto& field = group_field(g);
        const int travel = field.get(p);
        if (travel == UNREACH) continue;
        const double value = g.gems + g.gold * gold_weight(round);
        if (value <= 0) continue;
        const int claimed = claimants(i) + 1;
        for (int n = claimed; n <= std::max(claimed, team_alive); ++n) {
            double time = travel + 5;
            if (g.state != 1) {
                const int home = W.spawn_field.get(g.spawns[0]);
                time += clear_time(g, n, dps, hp, home == UNREACH ? 30 : home);
                if (g.state == 2) time += std::max(0, g.respawn_round - round - travel);
                // Gathering extra teammates costs time.
                time += (n - claimed) * 4;
            }
            const double score = value / (time * n);
            if (score > best) best = score, best_i = i, planned_team = n;
            if (g.state == 1) break;
        }
    }
    return best_i;
}

bool bank_gems() {
    auto& me = cambc::self();
    const vec2 p = me.position();
    for (auto altar : W.altars) {
        if (dist(p, altar) <= cambc::constants::submit_gems_range && !cv::has_altar_lock(altar)) {
            me.submit_gems(altar);
            return true;
        }
    }
    return step_field(W.altar_field, W.altar_tiles, cambc::constants::submit_gems_range);
}

// Best camp to hit: biggest strength removed per point of damage; clusters (no strength) last.
const cambc::camp* choose_camp(const std::vector<cambc::camp>& live) {
    const cambc::camp* best = nullptr;
    double best_s = -1;
    for (const auto& c : live) {
        const double s = (c.strength() + 1.0) / std::max(1.0f, c.health());
        if (s > best_s) best_s = s, best = &c;
    }
    return best;
}

void fight_or_approach(int gi) {
    auto& me = cambc::self();
    auto& g = W.groups[gi];
    const vec2 p = me.position();
    const int range = me.attack_range();
    std::vector<cambc::camp> live;
    for (const auto& c : cv::camps())
        if (c.is_visible() && c.health() > 0 && g.tiles.is_set(c.spawn_position())) live.push_back(c);
    TRACE("grp" << gi << " st=" << g.state << " live=" << live.size() << " hp_left=" << g.hp_left() << " me=" << cambc::to_string(p));

    if (live.empty()) {
        if (g.state == 2) {
            // Respawning: a ward or body on a spawn tile delays it, so wait beside the group.
            if (g.tiles.is_set(p)) {
                const auto occ = occupied_tiles() | g.tiles;
                for (auto d : DIRS) {
                    vec2 t{p.x + d.x, p.y + d.y};
                    if (cm::is_in_bounds(t) && !W.terrain.is_set(t) && !occ.is_set(t) && safe_move(t)) break;
                }
            } else if (group_field(g).get(p) > 2) {
                step_field(group_field(g), g.tiles, 2);
            }
            return;
        }
        // Dead or unseen: walk onto a spawn tile to capture.
        if (g.tiles.is_set(p)) { use_support_abilities(false); return; }
        step_field(group_field(g), g.tiles, 0);
        return;
    }

    // A big asleep group waits for the planned team so one champion does not soak every hit.
    if (!g.damaged() && planned_team > 1) {
        int present = 1;
        for (const auto& a : cv::champions(team::ally)) {
            if (handle_id(a) == handle_id(me) || !a.is_alive() || !a.is_visible()) continue;
            for (const auto& c : live)
                if (dist(a.position(), c.position()) <= 6) { ++present; break; }
        }
        if (present < planned_team && gather_turns < 30) {
            ++gather_turns;
            if (group_field(g).get(p) > 5) step_field(group_field(g), g.tiles, 5);
            return;
        }
    }
    gather_turns = 0;

    const cambc::camp* target = choose_camp(live);
    // Spells reach further than camps: cast before closing in.
    if (dist(p, target->position()) > range) {
        if (use_camp_abilities(live, *target, g.damaged()) && !me.can_move()) return;
        bitboard goals;
        goals.clear();
        goals.draw_chebyshev(target->position(), static_cast<float>(range));
        if (!step_to_tiles(goals)) step_field(group_field(g), g.tiles, 0);
    }
    // Re-pick among camps now in range.
    const cambc::camp* hit = nullptr;
    for (const auto& c : live)
        if (dist(me.position(), c.position()) <= range && (!hit || c.health() < hit->health())) hit = &c;
    if (hit && dist(me.position(), target->position()) <= range) hit = target;
    if (!hit) return;
    if (me.can_attack()) {
        try {
            me.attack(*hit);
        } catch (const cambc::error& e) {
            std::cout << "attack fail " << e.what() << " hit=" << cambc::to_string(hit->position()) << " kind="
                      << cambc::to_string(hit->kind()) << " hp=" << hit->health() << " vis=" << hit->is_visible()
                      << " me=" << cambc::to_string(me.position()) << '\n';
        }
    }
    if (hit->is_visible() && hit->health() > 0 && !use_camp_abilities(live, *hit, true)) try_attack_reset_and_hit(*hit);
    use_support_abilities(true);
}

}  // namespace

void Bot::play_turn() {
    if (!W.ready) init_world();
    auto& me = cambc::self();
    const int round = static_cast<int>(cambc::round_number());
    tracing = false;

    if (round % 20 == 0 || (!me.is_alive() && was_alive)) {
        std::cout << "R" << round << " s" << W.slot << " " << cambc::to_string(me.champion_name()) << " hp=" << me.health() << "/"
                  << me.max_health() << " gems=" << me.gem_count() << " gold=" << me.gold_count() << " tgt=" << current_target
                  << (me.is_alive() ? " pos=" + cambc::to_string(me.position()) : std::string(" DEAD")) << '\n';
    }
    if (W.slot == 0 && round % 10 == 0)
        std::cout << "G " << round << " " << cambc::global_submitted_gems(team::ally) << " "
                  << cambc::global_submitted_gems(team::enemy) << '\n';
    was_alive = me.is_alive();
    if (!me.is_alive()) {
        shop();
        write_claim(-1);
        retreating = false;
        return;
    }
    if (me.is_recalling() || me.is_submitting_gems() || me.is_teleporting()) return;

    bot_stage = "knowledge";
    update_knowledge();
    bot_stage = "enemies";
    const vec2 p = me.position();
    const bool at_spawn = W.ally_spawn.is_set(p);
    if (at_spawn) {
        shop();
        retreating = false;
    }

    // Damage not explained by camps comes from an enemy, possibly hidden in a bush.
    const float incoming = camp_incoming(p);
    const float taken = last_round + 1 == round ? last_hp - me.health() : 0.0f;
    last_hp = me.health();
    last_round = round;
    if (taken > incoming + 1.0f) enemy_seen_round = round;

    // Compare nearby strength with visible enemies.
    float enemy_power = 0, ally_power = me.health() * my_dps();
    const cambc::champion* prey = nullptr;
    const auto enemies = cv::champions(team::enemy);
    for (const auto& e : enemies) {
        if (!e.is_visible() || !e.is_alive() || dist(p, e.position()) > 5) continue;
        // Enemies resting on their own spawn only matter when they can already hit us.
        if (cm::spawn_region(team::enemy).is_set(e.position()) && dist(p, e.position()) > e.attack_range()) continue;
        enemy_seen_round = round;
        enemy_power += e.health() * (e.strength() * 1.2f);
        if (!cm::spawn_region(team::enemy).is_set(e.position()) && dist(p, e.position()) <= std::max(me.attack_range(), 4) && (!prey || e.health() < prey->health())) prey = &e;
    }
    for (const auto& a : cv::champions(team::ally))
        if (handle_id(a) != handle_id(me) && a.is_alive() && a.is_visible() && dist(p, a.position()) <= 4)
            ally_power += a.health() * a.strength() * 1.2f;

    if (prey && (ally_power >= enemy_power * 0.8f || (at_spawn && dist(p, prey->position()) <= me.attack_range()))) {
        bot_stage = "fight enemy";
        // Favourable fight: focus the weakest enemy, spells first.
        use_offensive_abilities(*prey, false);
        if (!prey->is_alive()) return;
        if (dist(p, prey->position()) <= me.attack_range()) {
            if (me.can_attack()) {
                try {
                    me.attack(*prey);
                } catch (const cambc::error& e) {
                    std::cout << "prey fail " << e.what() << " at " << cambc::to_string(prey->position()) << " vis="
                              << prey->is_visible() << " hp=" << prey->health() << " seen="
                              << cv::visible_tiles().is_set(prey->position()) << " me=" << cambc::to_string(p) << '\n';
                }
            }
            if (prey->is_alive()) try_attack_reset_and_hit(*prey);
            return;
        }
        if (me.can_move()) me.move_towards(prey->position());
        return;
    }
    if (enemy_seen_round >= round - 1 && (enemy_power > 0 || taken > incoming + 1.0f)) {
        // Unfavourable or unseen attacker: run home, stunning the chaser if possible.
        if (prey) use_offensive_abilities(*prey, false);
        if (!at_spawn) step_field(W.spawn_field, W.ally_spawn, 0);
        write_claim(-1);
        return;
    }

    if (at_spawn && me.health() < me.max_health() * 0.9f) {
        write_claim(-1);
        return;
    }

    // Leave camp range before the next hits could kill; camps never chase or heal, so progress is kept.
    // Each camp hits only its nearest champion, so plan for the strongest camp in range or what we just took.
    float strongest = 0;
    int nearest_threat = 99;
    auto others = cv::champion_tiles();
    others.set(p, false);
    for (const auto& c : cv::camps()) {
        if (!c.is_visible() || c.health() <= 0) continue;
        const int d = dist(p, c.position());
        if (d > CAMP_RANGE) continue;
        const int gi = group_of_camp(c.spawn_position());
        if (gi < 0 || !W.groups[gi].damaged()) continue;
        nearest_threat = std::min(nearest_threat, d);
        // Someone strictly closer draws this camp's attacks.
        bitboard closer;
        closer.clear();
        if (d > 1) closer.draw_chebyshev(c.position(), static_cast<float>(d - 1));
        if (d > 1 && !(closer & others).is_empty()) continue;
        strongest = std::max(strongest, c.strength());
    }
    const float danger = std::max(strongest, taken);
    const int steps_out = nearest_threat <= CAMP_RANGE ? CAMP_RANGE + 1 - nearest_threat : 0;
    TRACE("hp=" << me.health() << " danger=" << danger << " steps=" << steps_out << " retreating=" << retreating);
    if (danger > 0 && me.health() < danger * (steps_out + 1.0f) + 40.0f) retreating = true;
    bot_stage = "retreat";
    if (retreating) {
        const auto threats = camp_threats(p, CAMP_RANGE + 1);
        const bool in_range = !camp_threats(p, CAMP_RANGE).empty();
        if (in_range) {
            step_away(threats);
            return;
        }
        // Out of reach: rejoin if still healthy, otherwise go home to heal.
        float hardest = 0;
        if (current_target >= 0) {
            const auto& g = W.groups[current_target];
            for (size_t i = 0; i < g.hp.size(); ++i) if (g.hp[i] > 0) hardest = std::max(hardest, g.strength[i]);
        }
        if (me.health() >= me.max_health() * 0.5f && me.health() >= hardest * 6.0f + 40.0f) {
            retreating = false;
        } else {
            write_claim(-1);
            if (me.gem_count() > 0 && W.altar_field.get(p) <= 3) { if (bank_gems()) return; }
            if (W.spawn_field.get(p) > 5) me.recall();
            else step_field(W.spawn_field, W.ally_spawn, 0);
            return;
        }
    }

    // Heal when worn down and no fight holds us.
    if (!at_spawn && me.health() < me.max_health() * 0.35f && incoming == 0) {
        retreating = true;
        if (W.spawn_field.get(p) > 5) me.recall();
        else step_field(W.spawn_field, W.ally_spawn, 0);
        write_claim(-1);
        return;
    }

    bot_stage = "bank";
    // Bank carried gems when holding a lot or an altar is close.
    const int gems = static_cast<int>(me.gem_count());
    if (gems > 0 && incoming == 0) {
        const int altar_d = W.altar_field.get(p);
        const bool endgame = round > 1900
            || cambc::global_submitted_gems(team::ally) + gems >= cambc::constants::winning_gems;
        if (gems >= 60 || altar_d <= 4 || endgame || (gems >= 30 && altar_d <= 10)) {
            if (bank_gems()) return;
        }
    }

    bot_stage = "shop";
    // Spend gold: shards add permanent stats, so a trip home pays off once enough has piled up.
    if (me.passive() == cambc::passive_type::remote_shop && me.gold_count() >= 30) shop();
    const int gold = static_cast<int>(me.gold_count());
    if (!at_spawn && incoming == 0 && round < 1850 && me.passive() != cambc::passive_type::remote_shop) {
        const int home = W.spawn_field.get(p);
        if (gold >= 300 || (gold >= 150 && home <= 12)) {
            write_claim(-1);
            if (home > 5) me.recall();
            else step_field(W.spawn_field, W.ally_spawn, 0);
            return;
        }
    }

    // Keep fighting an awake target; otherwise choose the best group.
    const bool in_fight = current_target >= 0 && W.groups[current_target].state == 0
        && !camp_threats(p, CAMP_RANGE + 1).empty();
    bot_stage = "pick";
    if (!in_fight) current_target = pick_group();
    bot_stage = "camp fight";
    write_claim(current_target);
    if (current_target < 0) {
        if (gems > 0) bank_gems();
        return;
    }
    fight_or_approach(current_target);
}
