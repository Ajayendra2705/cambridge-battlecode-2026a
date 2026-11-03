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
    std::optional<map::camp_group> api;  // edit_vtfuel2.py: no longer filled at set-up (never read)
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
    std::shared_ptr<bitboard> stage_goals;  // edit_vtfuel.py: stage_at's goals with the static field (static data only)
    struct AcCache {  // edit_vtfuel.py: attack_camps' live board and attack spots for one live set
        std::uint64_t mask = 0;
        int range = -1;
        bool ok = false;
        std::optional<bitboard> live, goals;
    };
    std::shared_ptr<AcCache> ac;
    int awake_max = -100;  // edit_vtfuel.py: the latest awake_round of any of its camps
    struct VtFd {  // edit_vtfuel3.py: choose_task's fight-damage list over full health (static), and the damaging camps
        int n = 0;
        float alive0 = 0;
        std::array<float, 24> hs{}, ss{};
        std::vector<std::uint16_t> dmg;
    };
    mutable std::shared_ptr<VtFd> vt_fd;
    // Island access by teleport crystal (groups not reachable on foot from spawn).
    int island = 0;            // 0 not an island, 1 reachable with one crystal jump, -1 unreachable
    bool island_done = false;  // island analysis performed
    vec2 tp_launch{ -1, -1 }, tp_land{ -1, -1 };
    int tp_land_dist = 0;      // walking steps from the landing tile to the group
    std::unique_ptr<distance_field> launch_field;  // distance to the launch tile (lazy)
    int tp_spawn = 1 << 20;    // steps from the spawn zone with one crystal flash (set with the field)
    vec2 tps_land{ -1, -1 };   // landing tile of that flash

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
    std::optional<bitboard> fwalls;       // static-field walls: blocked minus the holes a dash crosses (dashers)
    std::optional<bitboard> bridges;      // 1-tile holes with walkable tiles on two opposite sides (dashers only)
    std::optional<bitboard> bridge_zone;  // tiles near a bridge: the dash is kept for the crossing
    bool dasher = false;
    bool central_altars = false;          // every altar between the spawns (centralgate.py)
    std::vector<vec2> tp_spawn_land;      // tiles one crystal flash (<= 3) away from the spawn zone
    bool tp_useful = false;               // some group is much closer by a flash from spawn
    void set_tp_spawn(Group& g);
    std::optional<bitboard> camp_tiles;   // all camp spawn tiles
    std::optional<bitboard> my_spawn, enemy_spawn;
    std::optional<bitboard> altar_spots;  // passable tiles within tribute range of an altar
    std::vector<vec2> altars;
    std::vector<Group> groups;
    // tile -> group id (-1 none), edit_vtfuel2.py: per 8x8 chunk, a 64-entry table only for chunks holding camp tiles (filling a dense
    // w*h table cost ~15k fuel on 100x100 maps); group_at reads the same ids
    int tg_cw = 0;
    std::vector<std::int32_t> tg_chunk;  // chunk -> offset into tg_cell (-1 none)
    std::vector<std::int16_t> tg_cell;
    void tg_set(vec2 p, int gid) {
        const std::size_t ci = static_cast<std::size_t>((p.y >> 3) * tg_cw + (p.x >> 3));
        if (tg_chunk[ci] < 0) {
            tg_chunk[ci] = static_cast<std::int32_t>(tg_cell.size());
            tg_cell.resize(tg_cell.size() + 64, -1);
        }
        tg_cell[static_cast<std::size_t>(tg_chunk[ci] + ((p.y & 7) << 3) + (p.x & 7))] = static_cast<std::int16_t>(gid);
    }
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
            if (cheb(g.center, q) > g.radius + g.max_range) continue;  // edit_vtfuel2.py: no camp of it reaches q
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
    std::optional<bitboard> vt_scr;  // edit_vtfuel2.py: scratch board for attack_spots' bush term (no board allocated per camp)
    // Attack positions for a camp at my range (cached; terrain is static).
    const bitboard& attack_spots(Camp& c, int range) {
        if (!c.los) {
            // Shadow casting from an opaque origin is an engine error: clear the origin (camps can sit in bushes).
            c.los = std::make_shared<bitboard>();  // edit_vtfuel2.py: born cleared (the second clear dropped)
            try {
                if (bb_test(*opaque, c.pos)) {
                    bitboard o = *opaque;
                    o.set(c.pos, false);
                    *c.los = o.shadow_cast(c.pos, static_cast<std::uint16_t>(range));
                } else {
                    opaque->shadow_cast_into(c.pos, static_cast<std::uint16_t>(range), *c.los);  // edit_vtfuel2.py: written in place
                }
                // edit_vtfuel2.py: no bush within reach (+1): the bush terms are empty (the cast stays inside the reach's box); else
                // the same board built in a kept scratch board
                const bool vt_bush = vt_any_in_box(map::bushes(), c.pos, range + 1);
                if (vt_bush && !bb_test(map::walls(), c.pos)) {
                    if (!vt_scr) vt_scr.emplace();
                    map::walls().shadow_cast_into(c.pos, static_cast<std::uint16_t>(range), *vt_scr);
                    *vt_scr &= map::bushes();
                    *c.los |= *vt_scr;
                }
                // A camp standing in a bush is hidden from viewers outside bushes: attack it from bush tiles.
                if (P_BUSH_CAMPS && vt_bush && bb_test(map::bushes(), c.pos)) {
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
    // edit_vtfuel.py: complements of the static masks, built once (each `x &= ~*blocked` allocated and filled a temporary board)
    mutable std::optional<bitboard> nblocked_, nopen_;
    const bitboard& not_blocked() const {
        if (!nblocked_) nblocked_.emplace(~*blocked);
        return *nblocked_;
    }
    const bitboard& open_tiles() const {  // ~blocked & ~camp_tiles
        if (!nopen_) {
            nopen_.emplace(~*blocked);
            *nopen_ &= ~*camp_tiles;
        }
        return *nopen_;
    }
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
    // edit_vtfuel2.py: the set-up in steps (init_a..init_e, in order); init() runs the next ones while fuel() covers init_need()
    int init_step = 0;
    void init_a();
    void init_b();
    bool init_c();  // false: resumes next turn (dash-bridge candidates checked while fuel lasts)
    std::uint64_t init_bfs() const { return static_cast<std::uint64_t>(w) * static_cast<std::uint64_t>(h) * 7 / 2 + 4000; }
    std::optional<bitboard> vt_bfoot;  // init_c's foot region, candidate holes and progress while it runs over several turns
    std::vector<vec2> vt_bcand;
    std::size_t vt_bi = 0;
    void init_d();
    void init_e();
    std::uint64_t init_need() const;
    std::optional<distance_field> vt_plain;  // init_b's plain spawn search, reused by init_c (edit_vtfuel.py V12)
    std::optional<bitboard> vt_plain_vis;
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
    std::uint64_t vt_field_cost = 0;  // edit_vtfuel3.py: dearest group field search seen (fuel)
    std::uint64_t vt_altar_need = 65000;  // edit_vtfuel3.py: fuel ensure_altar_fields needs left before an altar's field
    std::uint64_t vt_field_need() const {  // edit_vtfuel3.py: a group field (a full-map search ~3.1 a tile on 100x100 maps)
        return std::max<std::uint64_t>(vt_field_cost, static_cast<std::uint64_t>(w) * static_cast<std::uint64_t>(h) * 7 / 2 + 5000);
    }

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
    int group_at(vec2 p) const {
        if (!in_bounds(p)) return -1;
        const std::int32_t off = tg_chunk[static_cast<std::size_t>((p.y >> 3) * tg_cw + (p.x >> 3))];
        return off < 0 ? -1 : tg_cell[static_cast<std::size_t>(off + ((p.y & 7) << 3) + (p.x & 7))];
    }
    // Distance (steps) from p to the group, using the static field if available, else an estimate.
    int dist_to_group(const Group& g, vec2 p) const;
};

World& world();
