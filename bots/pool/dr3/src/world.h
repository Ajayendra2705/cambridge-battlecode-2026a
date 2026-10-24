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
    int altar_guard = -1;  // Group whose camps fill every free tile next to every altar (boss_battle): nobody banks until it dies.
    std::vector<cambc::champion_type> slot_types;
    std::vector<std::uint32_t> slot_ids;
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
    {
        int guard = -2;
        const auto blocked = cm::walls() | cm::holes() | cm::altars();
        for (auto a : W.altars)
            for (int dx = -1; dx <= 1; ++dx)
                for (int dy = -1; dy <= 1; ++dy) {
                    const vec2 t{a.x + dx, a.y + dy};
                    if (!cm::is_in_bounds(t) || blocked.is_set(t)) continue;
                    const int o = W.camp_owner[t.y * cm::width() + t.x];
                    if (o < 0 || (guard >= 0 && o != guard)) guard = -1;
                    else if (guard == -2) guard = o;
                }
        W.altar_guard = guard >= 0 ? guard : -1;
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
