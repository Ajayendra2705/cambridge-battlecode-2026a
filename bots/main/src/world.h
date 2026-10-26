// Part of bot.cpp: Static map knowledge built once (camp groups, altars, distance fields, team slots) plus observed group state.
// Unity build: bot.cpp includes this inside its anonymous namespace; not a standalone header.

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
    int first_camp = 0, camp_count = 0;  // This group's entries in known_camps (init_units stores them group by group).
    int row_lo = 0, row_hi = -1;          // Rows of its spawn tiles: a view that misses them cannot see the group.
    double bank_cost = 0;         // Rounds to walk the reward to the nearest altar and tribute it.
    std::unique_ptr<distance_field> field;
    std::uint64_t field_key = 0;  // Which strong camps' reaches `field` avoids (bit per W.strong_camps entry).
    int opened_round = -100;      // When `field` was last rebuilt to let us out of a reach we stood in (see group_field).
    std::unique_ptr<bitboard> open_reach;  // The reach `field` lets us through until we are out of it.

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
    std::vector<std::vector<int>> covered_by;  // Per group: other groups whose monolith or golem reaches its tiles.
    struct StrongCamp { vec2 pos; int range, group; };
    std::vector<StrongCamp> strong_camps;  // Monoliths and golems: their range is deadly to walk through.
    std::vector<int> group_side;  // Per group: own-spawn distance minus enemy-spawn distance (positive = their half).
    int slot = 0, team_count = 1;
    std::vector<std::int16_t> camp_owner;  // Group index per tile, -1 elsewhere.
    // Groups whose camps fill every free tile next to every altar: nobody banks while each of those tiles holds a living
    // camp. boss_battle: one group; 02guardians: two monoliths, each its own group, one on each side of the altar.
    std::vector<int> altar_guards;
    std::vector<cambc::champion_type> slot_types;
    std::vector<std::uint32_t> slot_ids;
};

World W;

void compute_field(distance_field& field, const bitboard& roots) {
    bitboard visited;
    field.compute(W.terrain & ~roots, roots, visited);
}

// Fuel one full-map field takes on this map, measured on each build (a 100x100 field can take over 50k: building one
// with less left ran the turn out of fuel, bf7 first try on big_world).
std::uint64_t field_cost = 30000;

// Route to a group around the reaches of other live monoliths and golems (defined in move.h: it reads our position).
distance_field& group_field(Group& g);

std::uint32_t handle_id(const cambc::champion& c) {
    return static_cast<std::uint32_t>(static_cast<cambc::handle_champion_t>(c));
}

int group_of_camp(vec2 spawn) {
    if (!cm::is_in_bounds(spawn)) return -1;
    return W.camp_owner[spawn.y * cm::width() + spawn.x];
}

void init_units();

// Design stats per camp kind. camp::base_stats() is a design query costing about 730 fuel, and it was asked for every
// camp twice (stats here, attack range in init_units): 230k on boss_battle's 158 camps, more than the 200k first turn,
// so the opening spread over 8 rounds (pf4 probe). Six kinds need six queries.
cambc::camp_stats camp_stats_of(const cambc::camp& c) {
    static std::vector<std::pair<cambc::camp_type, cambc::camp_stats>> cache;
    for (const auto& [k, s] : cache) if (k == c.kind()) return s;
    cache.push_back({c.kind(), c.base_stats()});
    return cache.back().second;
}

void init_world() {
    auto& me = cambc::self();
    W.ally_spawn = cm::spawn_region(team::ally);
    W.enemy_spawn = cm::spawn_region(team::enemy);
    W.terrain = cm::walls() | cm::holes() | cm::altars() | W.enemy_spawn;
    W.altars = cm::altars().positions();
    W.altar_tiles = cm::altars();
    // Moved, not copied, and stored without regrowing the vector (copies and regrowth cost about 45k on boss_battle).
    auto all = cm::camp_groups();
    W.groups.reserve(all.size());
    for (auto& group : all) {
        Group g{std::move(group)};
        g.tiles = g.group.spawn_tiles();
        g.gems = static_cast<int>(g.group.gem_value());
        g.gold = static_cast<int>(g.group.gold_value());
        // A heap allocation costs about 400 fuel: growing three vectors camp by camp cost 66k on boss_battle.
        const auto nc = g.group.camps().size();
        g.spawns.reserve(nc), g.max_hp.reserve(nc), g.strength.reserve(nc);
        for (const auto& c : g.group.camps()) {
            const auto s = camp_stats_of(c);
            g.spawns.push_back(c.spawn_position());
            g.max_hp.push_back(s.base_health);
            g.strength.push_back(s.base_strength);
        }
        g.row_lo = cm::height();
        for (auto sp : g.spawns) g.row_lo = std::min(g.row_lo, sp.y), g.row_hi = std::max(g.row_hi, sp.y);
        g.reset();
        W.groups.push_back(std::move(g));
    }
    W.camp_owner.assign(static_cast<size_t>(cm::width() * cm::height()), -1);
    for (int i = 0; i < static_cast<int>(W.groups.size()); ++i)
        for (auto s : W.groups[i].spawns) W.camp_owner[s.y * cm::width() + s.x] = static_cast<std::int16_t>(i);
    {
        std::vector<int> guards;
        bool open = false;
        const auto blocked = cm::walls() | cm::holes() | cm::altars();
        for (auto a : W.altars)
            for (int dx = -1; dx <= 1; ++dx)
                for (int dy = -1; dy <= 1; ++dy) {
                    const vec2 t{a.x + dx, a.y + dy};
                    if (!cm::is_in_bounds(t) || blocked.is_set(t)) continue;
                    const int o = W.camp_owner[t.y * cm::width() + t.x];
                    if (o < 0) open = true;
                    else if (std::find(guards.begin(), guards.end(), o) == guards.end()) guards.push_back(o);
                }
        if (!open) W.altar_guards = guards;
    }
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
    for (const auto& [id, type] : ids) W.slot_types.push_back(type), W.slot_ids.push_back(id);
    W.team_count = static_cast<int>(ids.size());
    W.slot = 0;
    while (W.slot < static_cast<int>(ids.size()) && ids[W.slot].first != handle_id(me)) ++W.slot;
    init_units();
    W.ready = true;
}
