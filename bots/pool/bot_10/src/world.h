// Static map model plus per-champion knowledge of camp groups.
#pragma once
#include "common.h"
#include "params.h"

enum class GState : std::uint8_t { Alive, Reward, Respawning };

struct Camp {
    vec2 pos;
    camp_type type;
    float max_hp;
    float hp;  // last known health (max_hp when assumed fresh)
    std::uint32_t handle = 0;
    int awake_round = -100;  // last round seen awake (camps only attack after being aggroed)
    std::shared_ptr<bitboard> los;  // tiles within my attack range with line of sight (lazy cache)
};

struct Group {
    int id = 0;
    std::uint32_t handle = 0;
    std::optional<map::camp_group> api;
    std::vector<Camp> camps;
    std::optional<bitboard> tiles;
    int gold = 0, gems = 0, respawn = 0;
    float total_max_hp = 0, dps = 0;
    int max_range = 0, radius = 0;
    bool big = false;       // golem or monolith inside
    bool monolith = false;  // monolith inside (too heavy for normal play)
    bool harmless = false;  // clusters only
    std::optional<bitboard> danger;  // tiles within reach of the group's damaging camps (lazy)
    bool reachable = true;  // a walkable tile touches a camp tile
    int spawn_dist = 0;     // steps from our spawn
    int enemy_dist = 0;     // steps from the enemy spawn (our distance to the mirrored group)
    int side = 0;           // enemy_dist - spawn_dist: > 0 on our half
    vec2 center{};
    // knowledge
    GState state = GState::Alive;
    int respawn_round = 0;
    int seen_round = -1;
    int capture_timer = 5;
    int capture_kind = 0;   // camp_group_capture_type as int
    // static distance to the group's tiles
    std::unique_ptr<distance_field> field;
    // Island access by teleport crystal (groups not reachable on foot from spawn).
    int island = 0;            // 0 not an island, 1 reachable with one crystal jump, -1 unreachable
    bool island_done = false;  // island analysis performed
    vec2 tp_launch{ -1, -1 }, tp_land{ -1, -1 };
    int tp_land_dist = 0;      // walking steps from the landing tile to the group
    std::unique_ptr<distance_field> launch_field;  // distance to the launch tile (lazy)

    float hp_left() const {
        float s = 0;
        for (const auto& c : camps) s += c.hp;
        return s;
    }
    float live_dps() const {
        float s = 0;
        for (const auto& c : camps) if (c.hp > 0) s += camp_str(c.type);
        return s;
    }
    // Damage taken while a team dealing team_dps kills the group, damaging camps first, weakest first (as
    // attack_camps does): each damaging camp stops hitting once dead (a constant group dps over the whole
    // kill overestimated two-elk groups by ~30% and made champions wait for helpers or abort winnable fights).
    float fight_damage(float team_dps, bool fresh = false) const {
        if (team_dps <= 1.f) team_dps = 1.f;
        std::array<float, 24> hs{}, ss{};
        int n = 0;
        float alive = 0;
        for (const auto& c : camps) {
            const float hp = fresh ? c.max_hp : c.hp;
            const float st = camp_str(c.type);
            if (hp <= 0 || st <= 0 || n >= 24) continue;
            int k = n++;
            while (k > 0 && hs[static_cast<std::size_t>(k - 1)] > hp) {
                hs[static_cast<std::size_t>(k)] = hs[static_cast<std::size_t>(k - 1)];
                ss[static_cast<std::size_t>(k)] = ss[static_cast<std::size_t>(k - 1)];
                --k;
            }
            hs[static_cast<std::size_t>(k)] = hp;
            ss[static_cast<std::size_t>(k)] = st;
            alive += st;
        }
        float dmg = 0;
        for (int i = 0; i < n; ++i) {
            dmg += alive * hs[static_cast<std::size_t>(i)] / team_dps;
            alive -= ss[static_cast<std::size_t>(i)];
        }
        return dmg;
    }
};

struct World {
    int w = 0, h = 0;
    std::optional<bitboard> blocked;      // walls | holes | altars | enemy spawn
    std::optional<bitboard> camp_tiles;   // all camp spawn tiles
    std::optional<bitboard> my_spawn, enemy_spawn;
    std::optional<bitboard> altar_spots;  // passable tiles within tribute range of an altar
    std::vector<vec2> altars;
    std::vector<Group> groups;
    std::vector<std::int16_t> tile_group;  // tile -> group id (-1 none)
    std::unique_ptr<distance_field> f_spawn, f_altar;
    // Per-altar tribute spots and distance fields (fields built lazily).
    std::vector<bitboard> altar_spot_of;
    std::vector<std::vector<vec2>> altar_spot_list;  // altar_spot_of as tiles (cheap threat tests)
    std::vector<std::unique_ptr<distance_field>> altar_field;
    // Altars cut off from the mainland (e.g. ringed by camps): reached by one crystal jump.
    std::vector<int> altar_jump_ok;            // 1 jump possible, 0 walkable, -1 unreachable
    std::vector<int> altar_enemy_lock;         // round an enemy lock was last seen on the altar (-1 none)
    std::vector<int> altar_side;               // enemy distance minus ours (> 0 on our half)
    std::vector<vec2> altar_launch, altar_land;
    std::vector<int> altar_land_dist;
    std::vector<std::unique_ptr<distance_field>> altar_launch_field;
    void ensure_altar_fields();
    // Launch (mainland) and landing (region) tiles for one crystal jump into `region`; false if none.
    bool find_jump(const bitboard& region, const distance_field& target, vec2& launch, vec2& land, int& land_dist, int& launch_dist);
    // Nearest altar whose spots are not all threatened (falls back to any); returns index or -1, sets dist.
    int best_altar(vec2 p, const bitboard* threat, int& dist, bool crystal = true, bool* jump = nullptr);
    // Altars walled in by camps (monoliths): gems go in only from a dead gate camp's tile.
    struct Gate { int altar; int group; vec2 tile; };
    std::vector<Gate> gates;
    bool gated = false;  // no altar has a walkable tribute spot: everything goes through a gate
    bool heavy_map = false;  // most gem income sits in heavy groups (monoliths, elk fortresses): siege them
    // Nearest gate whose camp is dead (our knowledge), -1 if none; dist set to steps to its tile.
    int open_gate(vec2 p, int& dist) const;
    // Damage per round live camps deal to a champion standing on tile q (camps hit the nearest champion).
    float camp_dps_on(vec2 q) const {
        float s = 0;
        for (const auto& g : groups) {
            if (g.state != GState::Alive || g.dps <= 0) continue;
            for (const auto& c : g.camps)
                if (c.hp > 0 && camp_str(c.type) > 0 && cheb(c.pos, q) <= camp_range(c.type)) s += camp_str(c.type);
        }
        return s;
    }
    vec2 spawn_center{}, enemy_spawn_center{};
    int total_fields_built = 0;
    bool ready = false;
    std::optional<bitboard> vis;  // tiles visible to me this turn (refreshed by observe)
    std::optional<bitboard> opaque;  // walls | bushes (bushes block sight unless the viewer stands in one)
    // Attack positions for a camp at my range (cached; terrain is static).
    const bitboard& attack_spots(Camp& c, int range) {
        if (!c.los) {
            // Shadow casting from an opaque origin is an engine error: clear the origin (camps can sit in bushes).
            c.los = std::make_shared<bitboard>();
            c.los->clear();
            try {
                if (bb_test(*opaque, c.pos)) {
                    bitboard o = *opaque;
                    o.set(c.pos, false);
                    *c.los = o.shadow_cast(c.pos, static_cast<std::uint16_t>(range));
                } else {
                    *c.los = opaque->shadow_cast(c.pos, static_cast<std::uint16_t>(range));
                }
                if (!bb_test(map::walls(), c.pos)) *c.los |= map::walls().shadow_cast(c.pos, static_cast<std::uint16_t>(range)) & map::bushes();
                // A camp standing in a bush is hidden from viewers outside bushes: attack it from bush tiles.
                if (P_BUSH_CAMPS && bb_test(map::bushes(), c.pos)) {
                    bitboard b = map::walls().shadow_cast(c.pos, static_cast<std::uint16_t>(range)) & map::bushes();
                    if (!b.is_empty()) *c.los = b;
                }
            } catch (...) {
                c.los->draw_chebyshev(c.pos, static_cast<float>(range));
            }
        }
        return *c.los;
    }

    std::optional<bitboard> mainland;  // tiles reachable on foot from our spawn (camp tiles excluded)
    // On the walkable mainland, counting camp tiles that touch it (dead camps are stood on to capture).
    bool on_main(vec2 p) const {
        if (bb_test(*mainland, p)) return true;
        if (!in_bounds(p) || !bb_test(*camp_tiles, p)) return false;
        for (auto d : kDirs) {
            const vec2 q = p + d;
            if (in_bounds(q) && bb_test(*mainland, q)) return true;
        }
        return false;
    }
    bool any_island = false;           // some group needs a teleport crystal
    void init();
    void ensure_field(Group& g);
    // Island analysis for a group not reachable on foot (needs fuel; returns false if postponed).
    bool analyse_island(Group& g);
    void ensure_launch_field(Group& g);
    // Walking distance from p to an island group via its launch tile and one crystal jump.
    int island_dist(Group& g, vec2 p);
    // Observe visible camp groups near `me` and refresh knowledge.
    void observe(int round, vec2 me);
    // Mark a group captured (by us or seen) at `round`.
    void mark_captured(int gid, int round);
    // Build a few missing group fields when fuel allows.
    void precompute(std::uint64_t reserve, vec2 me);

    // Reach of a group's damaging camps (cached; terrain-independent Chebyshev disks).
    const bitboard& danger_of(Group& g) {
        if (!g.danger) {
            g.danger.emplace();
            g.danger->clear();
            for (const auto& c : g.camps)
                if (camp_str(c.type) > 0) g.danger->draw_chebyshev(c.pos, static_cast<float>(camp_range(c.type)));
        }
        return *g.danger;
    }
    // Field value at p; from a camp tile (a wall in static fields) go through the best neighbour.
    static int field_at(const distance_field& f, vec2 p) {
        const auto d = df_get(f, p);
        if (d != distance_field::unreachable) return static_cast<int>(d);
        int best = distance_field::unreachable;
        for (auto dd : kDirs) {
            const vec2 q = p + dd;
            if (!in_bounds(q)) continue;
            const auto v = df_get(f, q);
            if (v != distance_field::unreachable) best = std::min(best, static_cast<int>(v) + 1);
        }
        return best;
    }
    int spawn_dist_at(vec2 p) const { return field_at(*f_spawn, p); }
    int altar_dist_at(vec2 p) const { return altar_spots->is_empty() ? distance_field::unreachable : field_at(*f_altar, p); }
    int group_at(vec2 p) const { return in_bounds(p) ? tile_group[p.y * w + p.x] : -1; }
    // Distance (steps) from p to the group, using the static field if available, else an estimate.
    int dist_to_group(const Group& g, vec2 p) const;
};

World& world();
