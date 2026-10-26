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
    // Terrain for the routes to groups and altars: a champion with a dash may cross a hole tile that has walkable tiles on
    // two opposite sides (a one-tile hole line), so those holes are open on its routes; everyone else walks round.
    bitboard route_terrain, thin_holes;
    bool has_dash = false;
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

void compute_field(distance_field& field, const bitboard& roots, const bitboard& terrain = W.terrain) {
    bitboard visited;
    field.compute(terrain & ~roots, roots, visited);
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

// Holes a dash (2 steps, may cross holes) jumps on a champion's routes to groups and altars (dh1, dh2). On road_of_riches
// the altar is 120 steps from our spawn walking and 20 with one dash; the rivals' dashers farmed the centre and tributed
// there while we never did (ladder 0-996 and 0-1005). A hole is opened only between two walkable tiles that we can walk
// to from our spawn, so every tile such a route reaches can still walk home (dh1 also hopped to islands only a dash
// reaches, 01islands 0 of 4 locally), and only where walking round it is 20 steps or more: the two sides' walking
// distances to our spawn or to an altar differ by 20+, and the walk round is at least that gap (triangle inequality).
// Smaller detours cost more than they save: a crossing spends the dash (Heart of Ruin's stun, everyone's escape) and can
// wait up to its 8-turn cooldown. Run after the walking altar and spawn fields; re-roots the altar field when it opens any.
// dh3: the holes stay shut unless they shorten the walk from our spawn to the altar by 40 steps or more (road_of_riches
// 121 to 22, shortcut 110 to 45, concentrated_wealth 86 to 26, fracture 76 to 35). Where they save less, crossing led
// into the rivals' fights: dh1 on the platform, gemfight (32 to 14) our deaths 4 to 22 and 1 to 8, gold_rush (12 to 5)
// 3 to 25, while concentrated_wealth went from 208 gems collected to 887 and shortcut from 504 to 930.
void open_thin_holes() {
    const auto spawns = W.ally_spawn.positions();
    if (spawns.empty()) return;
    // Most maps stop here for a few hundred fuel: no route is shorter than the straight line. This runs in the first
    // turn's init, so maps the switch leaves shut should spend next to nothing (a full field cost 49k on ambush).
    const int walk = W.altar_field.get(spawns[0]);
    int line = UNREACH;
    for (const auto a : W.altars) line = std::min(line, dist(a, spawns[0]));
    if (walk - line < 40) return;
    const bitboard reach = W.terrain.reachable_tiles(spawns[0], 4000);
    // Holes with reachable tiles on both sides along some axis (either shift convention: both pairs of each axis).
    const bitboard r = reach.shift_right(1), l = reach.shift_right(-1);
    const bitboard cand = cm::holes() & ((r & l) | (reach.shift_up(1) & reach.shift_up(-1))
        | (r.shift_up(1) & l.shift_up(-1)) | (r.shift_up(-1) & l.shift_up(1)));
    if (cand.is_empty()) return;
    // With every candidate open the walk must still shrink by 40: a field searched only that deep settles the rest.
    {
        distance_field probe;
        bitboard visited;
        probe.compute((W.terrain & ~cand) & ~cm::altars(), cm::altars(), visited, static_cast<std::uint16_t>(walk - 40));
        if (!visited.is_set(spawns[0])) return;
    }
    // Fields and reach read row-major in one call each: a get or is_set is a host call of about 40-50 fuel.
    const int w = cm::width();
    const auto sf = W.spawn_field.export_linear_buffer(), af = W.altar_field.export_linear_buffer();
    const auto rb = reach.export_linear_buffer();  // bits, least significant first
    const auto at = [w](const std::vector<std::uint16_t>& f, vec2 p) { return static_cast<int>(f[p.y * w + p.x]); };
    const auto reached = [w, &rb](vec2 p) {
        const int i = p.y * w + p.x;
        return cm::is_in_bounds(p) && (rb[i >> 3] >> (i & 7) & 1);
    };
    constexpr std::array<vec2, 4> axes{vec2{1, 0}, vec2{0, 1}, vec2{1, 1}, vec2{1, -1}};
    bitboard open;
    for (const auto h : cand.positions()) {
        for (const auto d : axes) {
            const vec2 a{h.x - d.x, h.y - d.y}, b{h.x + d.x, h.y + d.y};
            if (!reached(a) || !reached(b)) continue;
            const int gap = std::max(std::abs(at(sf, a) - at(sf, b)), std::abs(at(af, a) - at(af, b)));
            if (gap >= 20) {
                open.set(h);
                break;
            }
        }
    }
    if (open.is_empty()) return;
    const bitboard route = W.terrain & ~open;
    distance_field opened;
    compute_field(opened, cm::altars(), route);
    if (walk - static_cast<int>(opened.get(spawns[0])) < 40) return;
    W.thin_holes = open;
    W.route_terrain = route;
    W.altar_field = std::move(opened);
}

void init_world() {
    auto& me = cambc::self();
    W.ally_spawn = cm::spawn_region(team::ally);
    W.enemy_spawn = cm::spawn_region(team::enemy);
    W.terrain = cm::walls() | cm::holes() | cm::altars() | W.enemy_spawn;
    for (const auto& ab : me.abilities()) if (ab.is_dash()) W.has_dash = true;
    W.route_terrain = W.terrain;  // open_thin_holes() opens holes on it once the walking fields exist
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
    if (W.has_dash) open_thin_holes();
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
