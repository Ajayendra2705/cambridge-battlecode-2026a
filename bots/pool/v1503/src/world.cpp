#include "world.h"
#include "params.h"

World& world() {
    static World w;
    return w;
}

void World::init() {
    w = map::width();
    h = map::height();
    my_spawn.emplace(map::spawn_region(team::ally));
    enemy_spawn.emplace(map::spawn_region(team::enemy));
    blocked.emplace(map::walls() | map::holes() | map::altars() | *enemy_spawn);
    // Dash bridges (dashers): a dash (2 tiles) crosses a 1-tile hole between two walkable tiles (straight, diagonal
    // or knight-wise) but never lands on a hole nor passes a wall. Computed with the static fields below.
    bridges.emplace();
    bridges->clear();
    fwalls.emplace(*blocked);
    bridge_zone.emplace();
    bridge_zone->clear();
    dasher = false;
    if (P_BRIDGES) {
        try {
            auto abs = self().abilities();
            for (int s = 0; s < 2; ++s) {
                const auto& inf = abs[static_cast<std::size_t>(s)].info();
                if (!inf) continue;
                std::visit([&](const auto& v) { if (v.kind == ability_kind::dash) dasher = true; }, *inf);
            }
        } catch (...) {}
    }
    altars = map::altars().positions();
    opaque.emplace(map::walls() | map::bushes());

    // spawn centres
    {
        auto sp = my_spawn->positions();
        long sx = 0, sy = 0;
        for (auto p : sp) { sx += p.x; sy += p.y; }
        if (!sp.empty()) spawn_center = { static_cast<int>(sx / (long)sp.size()), static_cast<int>(sy / (long)sp.size()) };
        auto ep = enemy_spawn->positions();
        sx = sy = 0;
        for (auto p : ep) { sx += p.x; sy += p.y; }
        if (!ep.empty()) enemy_spawn_center = { static_cast<int>(sx / (long)ep.size()), static_cast<int>(sy / (long)ep.size()) };
    }

    tile_group.assign(static_cast<std::size_t>(w) * h, -1);
    camp_tiles.emplace();
    camp_tiles->clear();
    auto api_groups = map::camp_groups();
    groups.reserve(api_groups.size());
    for (auto& ag : api_groups) {
        Group g;
        g.id = static_cast<int>(groups.size());
        g.gold = static_cast<int>(ag.gold_value());
        g.gems = static_cast<int>(ag.gem_value());
        g.respawn = ag.max_respawn_timer();
        g.tiles.emplace();
        g.tiles->clear();
        long sx = 0, sy = 0;
        bool only_clusters = true;
        for (const auto& c : ag) {
            Camp cp{ c.spawn_position(), c.kind(), camp_max_hp(c.kind()), camp_max_hp(c.kind()) };
            cp.handle = static_cast<std::uint32_t>(static_cast<handle_camp_t>(c));
            g.camps.push_back(cp);
            g.tiles->set(cp.pos);
            camp_tiles->set(cp.pos);
            tile_group[cp.pos.y * w + cp.pos.x] = static_cast<std::int16_t>(g.id);
            g.total_max_hp += cp.max_hp;
            g.dps += camp_str(cp.type);
            g.max_range = std::max(g.max_range, camp_range(cp.type));
            if (cp.type == camp_type::golem || cp.type == camp_type::monolith) g.big = true;
            if (cp.type == camp_type::monolith) g.monolith = true;
            if (cp.type != camp_type::gem_cluster && cp.type != camp_type::gold_cluster) only_clusters = false;
            sx += cp.pos.x;
            sy += cp.pos.y;
        }
        g.harmless = only_clusters;
        const long n = static_cast<long>(g.camps.size());
        g.center = { static_cast<int>(sx / n), static_cast<int>(sy / n) };
        for (const auto& c : g.camps) g.radius = std::max(g.radius, cheb(c.pos, g.center));
        g.handle = static_cast<std::uint32_t>(static_cast<handle_camp_group_t>(ag));
        g.api.emplace(std::move(ag));
        groups.push_back(std::move(g));
    }

    // altar tribute spots
    altar_spots.emplace();
    altar_spots->clear();
    for (auto a : altars) altar_spots->draw_chebyshev(a, static_cast<float>(constants::submit_gems_range));
    *altar_spots &= ~*blocked;
    *altar_spots &= ~*camp_tiles;

    for (auto a : altars) {
        bitboard b;
        b.clear();
        b.draw_chebyshev(a, static_cast<float>(constants::submit_gems_range));
        b &= ~*blocked;
        b &= ~*camp_tiles;
        altar_spot_of.push_back(b);
        altar_spot_list.push_back(b.positions());
        altar_field.emplace_back();
        altar_jump_ok.push_back(0);
        altar_enemy_lock.push_back(-1);
        altar_launch.push_back({ -1, -1 });
        altar_land.push_back({ -1, -1 });
        altar_land_dist.push_back(0);
        altar_launch_field.emplace_back();
    }
    central_altars = !P_CENTRAL_GATE;
    if (P_CENTRAL_GATE && !altars.empty()) {
        // Plain walking distances from our spawn (no bridges yet); an altar is central when its mirror image (the other
        // team's view of it) is about as far.
        bitboard vis0;
        distance_field plain;
        plain.compute((*blocked) | *camp_tiles, *my_spawn, vis0);
        const auto sym0 = map::symmetry();
        bool all = true;
        for (const vec2 a : altars) {
            vec2 m = a;
            try {
                m = sym0 == symmetry::horizontal ? map::reflect_horizontal(a) : sym0 == symmetry::vertical ? map::reflect_vertical(a) : map::rotate_180(a);
            } catch (...) {}
            const int da = field_at(plain, a), dm = field_at(plain, m);
            if (da >= distance_field::unreachable || dm >= distance_field::unreachable || std::abs(dm - da) > P_CENTRAL_SLACK) { all = false; break; }
        }
        // v606: only where the spawns are far apart (the gate's ladder evidence is from maps more than 61 walking steps apart;
        // on near maps the bridges and the spawn flash were not measured and v559 lost locally there).
        if (all && P_CENTRAL_MIN_STEPS > 0) {
            int ds = distance_field::unreachable;
            for (const vec2 q : enemy_spawn->positions()) ds = std::min(ds, field_at(plain, q));
            if (ds <= P_CENTRAL_MIN_STEPS) all = false;
        }
        central_altars = all;
    }
    if (dasher && central_altars && !map::holes().is_empty()) {
        // Ground reachable on foot from spawn: a bridge needs one landing there (one hop onto an island at most:
        // island chains cost 8 rounds of dash cooldown per hop and stranded champions on islands).
        bitboard foot;
        {
            distance_field fw;
            fw.compute((*blocked) | *camp_tiles, *my_spawn, foot);
        }
        const bitboard fl = ~*blocked;
        const bitboard& ho = map::holes();
        bitboard cand = ho & fl.shift_right(1) & fl.shift_right(-1);
        cand |= ho & fl.shift_up(1) & fl.shift_up(-1);
        cand |= ho & fl.shift_right(1).shift_up(1) & fl.shift_right(-1).shift_up(-1);
        cand |= ho & fl.shift_right(1).shift_up(-1) & fl.shift_right(-1).shift_up(1);
        static constexpr std::array<vec2, 4> kOpp{ vec2{ 1, 0 }, vec2{ 0, 1 }, vec2{ 1, 1 }, vec2{ 1, -1 } };
        // Both landings need walkable ground around them (no stepping stones in a pond: the-pond).
        auto ground = [&](vec2 a) {
            int n = 0;
            for (auto d : kDirs) {
                const vec2 q = a + d;
                if (in_bounds(q) && !bb_test(*blocked, q)) ++n;
            }
            return n >= P_BRIDGE_GROUND;
        };
        for (const vec2 hp : cand.positions())
            for (const auto d : kOpp) {
                const vec2 a{ hp.x - d.x, hp.y - d.y }, b{ hp.x + d.x, hp.y + d.y };
                if (!in_bounds(a) || !in_bounds(b) || bb_test(*blocked, a) || bb_test(*blocked, b)) continue;
                if (!(bb_test(foot, a) || bb_test(foot, b)) || !ground(a) || !ground(b)) continue;
                bridges->set(hp);
                break;
            }
        if (!bridges->is_empty()) {
            *fwalls = *blocked & ~*bridges;
            bitboard x = *bridges;
            for (int k = 1; k <= P_BRIDGE_RESERVE; ++k) { x |= bridges->shift_right(k); x |= bridges->shift_right(-k); }
            bitboard y = x;
            for (int k = 1; k <= P_BRIDGE_RESERVE; ++k) { y |= x.shift_up(k); y |= x.shift_up(-k); }
            *bridge_zone = y;
        }
    }
    // static fields to spawn and altars
    const bitboard walls = *fwalls | *camp_tiles;
    bitboard visited;
    f_spawn = std::make_unique<distance_field>();
    f_spawn->compute(walls, *my_spawn, visited);
    mainland.emplace(visited);
    *mainland &= ~*bridges;
    if (P_TP_SPAWN && central_altars) {
        bitboard land;
        land.clear();
        for (const vec2 s : my_spawn->positions()) land.draw_chebyshev(s, 3.f);
        land &= ~*blocked;
        land &= ~*camp_tiles;
        land &= ~*my_spawn;
        tp_spawn_land = land.positions();
    }
    f_altar = std::make_unique<distance_field>();
    if (!altar_spots->is_empty()) f_altar->compute(walls, *altar_spots, visited);
    // Reachability: some walkable neighbour of a camp tile is reachable from spawn.
    for (auto& g : groups) {
        int best = distance_field::unreachable;
        for (const auto& c : g.camps)
            for (auto d : kDirs) {
                const vec2 q = c.pos + d;
                if (!in_bounds(q)) continue;
                const int v = df_get(*f_spawn, q);
                if (v < best) best = v;
            }
        g.reachable = best != distance_field::unreachable;
        g.spawn_dist = best;
        if (!g.reachable) any_island = true;
    }
    // Map halves: the mirrored group's distance from our spawn is this group's distance from theirs.
    const auto sym = map::symmetry();
    for (std::size_t k = 0; k < altars.size(); ++k) {
        const vec2 a = altars[k];
        vec2 m = a;
        try {
            m = sym == symmetry::horizontal ? map::reflect_horizontal(a) : sym == symmetry::vertical ? map::reflect_vertical(a) : map::rotate_180(a);
        } catch (...) {}
        const int dm = field_at(*f_spawn, a), de = field_at(*f_spawn, m);
        altar_side.push_back(dm >= distance_field::unreachable || de >= distance_field::unreachable ? 0 : de - dm);
    }
    for (auto& g : groups) {
        const vec2 c0 = g.camps[0].pos;
        vec2 m = c0;
        try {
            m = sym == symmetry::horizontal ? map::reflect_horizontal(c0) : sym == symmetry::vertical ? map::reflect_vertical(c0) : map::rotate_180(c0);
        } catch (...) {}
        const int mg = group_at(m);
        g.enemy_dist = mg >= 0 ? groups[static_cast<std::size_t>(mg)].spawn_dist : g.spawn_dist;
        g.side = g.enemy_dist - g.spawn_dist;
    }
    // Gated altars: no walkable tribute spot, but a camp tile within range whose neighbours are walkable.
    int open_altars = 0;
    for (std::size_t k = 0; k < altars.size(); ++k) {
        bitboard spots = altar_spot_of[k] & *mainland;
        if (!spots.is_empty()) { ++open_altars; continue; }
        const vec2 a = altars[k];
        for (int dx = -1; dx <= 1; ++dx)
            for (int dy = -1; dy <= 1; ++dy) {
                const vec2 c{ a.x + dx, a.y + dy };
                if (!in_bounds(c) || !bb_test(*camp_tiles, c)) continue;
                bool reach = false;
                for (auto d : kDirs) {
                    const vec2 q = c + d;
                    if (in_bounds(q) && bb_test(*mainland, q)) reach = true;
                }
                if (reach) gates.push_back({ static_cast<int>(k), group_at(c), c });
            }
    }
    gated = open_altars == 0 && !gates.empty();
    // Share of gem income (gems per respawn round) held by groups too heavy for normal farming.
    {
        float tot = 0, heavy = 0;
        for (const auto& g : groups) {
            const float r = static_cast<float>(g.gems) / static_cast<float>(std::max(1, g.respawn));
            tot += r;
            if (g.dps > 150.f || g.monolith) heavy += r;
        }
        heavy_map = tot > 0 && heavy / tot >= P_HEAVY_SHARE;
    }
    ready = true;
}

int World::open_gate(vec2 p, int& dist) const {
    int best = -1;
    dist = distance_field::unreachable;
    for (std::size_t i = 0; i < gates.size(); ++i) {
        const Gate& gt = gates[i];
        if (gt.group < 0) continue;
        const Group& g = groups[static_cast<std::size_t>(gt.group)];
        bool dead = g.state != GState::Alive;
        if (!dead)
            for (const auto& c : g.camps)
                if (c.pos == gt.tile && c.hp <= 0) dead = true;
        if (!dead) continue;
        int d = dist_to_group(g, p);
        if (d >= (1 << 20)) d = cheb(p, gt.tile) * 5 / 4 + 2;
        if (d < dist) { dist = d; best = static_cast<int>(i); }
    }
    return best;
}

void World::ensure_field(Group& g) {
    if (g.field) return;
    bitboard walls = *fwalls | *camp_tiles;
    walls &= ~*g.tiles;
    bitboard visited;
    g.field = std::make_unique<distance_field>();
    g.field->compute(walls, *g.tiles, visited);
    ++total_fields_built;
    set_tp_spawn(g);
}

void World::set_tp_spawn(Group& g) {
    if (!g.field || tp_spawn_land.empty()) return;
    int best = 1 << 20;
    vec2 bl{ -1, -1 };
    for (const vec2 q : tp_spawn_land) {
        const int v = df_get(*g.field, q);
        if (v != distance_field::unreachable && v + 4 < best) { best = v + 4; bl = q; }
    }
    g.tp_spawn = best;
    g.tps_land = bl;
    if (g.reachable && best + 8 < g.spawn_dist) tp_useful = true;
}

void World::precompute(std::uint64_t reserve, vec2 me) {
    if (fuel() > reserve + 30000) ensure_altar_fields();
    if (any_island)
        for (auto& g : groups)
            if (!g.reachable && !g.island_done && fuel() > reserve + 25000) analyse_island(g);
    // Build fields for the nearest groups first.
    const std::uint64_t per_field = static_cast<std::uint64_t>(w) * h * 4 + 8000;
    while (fuel() > reserve + per_field) {
        Group* best = nullptr;
        int bd = 1 << 30;
        for (auto& g : groups) {
            if (g.field) continue;
            int d = cheb(g.center, me);
            if (d < bd) { bd = d; best = &g; }
        }
        if (!best) return;
        ensure_field(*best);
    }
}

int World::dist_to_group(const Group& g, vec2 p) const {
    if (g.field) {
        const auto d = df_get(*g.field, p);
        if (d != distance_field::unreachable) return d;
        // Standing on a camp tile (walls in the static fields): go through a neighbour.
        int best = 1 << 20;
        for (auto dd : kDirs) {
            const vec2 q = p + dd;
            if (!in_bounds(q)) continue;
            const auto v = df_get(*g.field, q);
            if (v != distance_field::unreachable) best = std::min(best, static_cast<int>(v) + 1);
        }
        return best;
    }
    // estimate: chebyshev plus detour allowance
    return cheb(g.center, p) * 5 / 4 + 2;
}

void World::mark_captured(int gid, int round) {
    if (gid < 0 || gid >= static_cast<int>(groups.size())) return;
    auto& g = groups[gid];
    g.state = GState::Respawning;
    g.respawn_round = round + g.respawn;
    for (auto& c : g.camps) c.hp = 0;
}

void World::observe(int round, vec2 me) {
    // Respawn timers expiring.
    for (auto& g : groups) {
        if (g.state == GState::Respawning && round >= g.respawn_round) {
            g.state = GState::Alive;
            for (auto& c : g.camps) c.hp = c.max_hp;
        }
    }
    this->vis.emplace(vision::visible_tiles());
    const bitboard& vis = *this->vis;
    for (std::size_t k = 0; k < altars.size(); ++k) {
        if (!bb_test(vis, altars[k])) continue;
        detail::altar_lock_info li{};
        altar_enemy_lock[k] = detail::sdk_altar_lock(altars[k].x, altars[k].y, detail::absolute_team(team::enemy), &li) == 0 ? round : -1;
    }
    for (auto& g : groups) {
        if (cheb(g.center, me) > g.radius + 10) continue;
        bool any_vis = false;
        for (const auto& c : g.camps)
            if (bb_test(vis, c.pos)) { any_vis = true; break; }
        if (!any_vis) continue;
        g.seen_round = round;
        // Direct engine queries: the group is known to be visible (the SDK wrapper would rebuild vision).
        std::uint32_t st = 0;
        if (detail::sdk_camp_group_state(g.handle, &st) != 0) continue;
        if (st == 1) {
            if (g.state != GState::Alive) {
                g.state = GState::Alive;
                for (auto& c : g.camps) c.hp = c.max_hp;
            }
            for (auto& c : g.camps) {
                if (!bb_test(vis, c.pos)) continue;
                std::uint32_t cs = 0;
                if (detail::sdk_camp_state(c.handle, &cs) != 0) continue;
                if (cs == 0) { c.hp = 0; continue; }
                if (cs == 1) c.awake_round = round;
                detail::camp_state info{};
                if (detail::sdk_camp(c.handle, &info) == 0) c.hp = info.health;
            }
        } else if (st == 2) {
            g.state = GState::Reward;
            for (auto& c : g.camps) c.hp = 0;
            detail::camp_group_capture_state cs{};
            if (detail::sdk_camp_group_capture_state(g.handle, &cs) == 0) {
                g.capture_timer = cs.timer;
                g.capture_kind = cs.state;
            }
        } else if (st == 3) {
            std::int32_t timer = 0;
            if (detail::sdk_camp_group_cooldown(g.handle, &timer) == 0) {
                g.state = GState::Respawning;
                g.respawn_round = round + timer;
                for (auto& c : g.camps) c.hp = 0;
            }
        }
    }
}

void World::ensure_altar_fields() {
    const bitboard walls = *fwalls | *camp_tiles;
    for (std::size_t k = 0; k < altars.size(); ++k) {
        if (altar_field[k] || altar_spot_of[k].is_empty()) continue;
        if (fuel() < 65000) return;
        bitboard region;
        altar_field[k] = std::make_unique<distance_field>();
        altar_field[k]->compute(walls, altar_spot_of[k], region);
        if (!(region & *mainland).is_empty()) continue;
        // Not reachable on foot: try one crystal jump.
        region &= ~*blocked;
        region &= ~*camp_tiles;
        int ld = 0;
        if (find_jump(region, *altar_field[k], altar_launch[k], altar_land[k], altar_land_dist[k], ld)) {
            altar_jump_ok[k] = 1;
            any_island = true;
        } else {
            altar_jump_ok[k] = -1;
        }
    }
}

int World::best_altar(vec2 p, const bitboard* threat, int& dist, bool crystal, bool* jump) {
    int best = -1, bd = distance_field::unreachable, best_any = -1, bda = distance_field::unreachable;
    bool bjump = false, ajump = false;
    const bool on_main = this->on_main(p);
    for (std::size_t k = 0; k < altars.size(); ++k) {
        if (!altar_field[k]) continue;
        int d = field_at(*altar_field[k], p);
        bool via_jump = false;
        if (d >= distance_field::unreachable && altar_jump_ok[k] == 1 && on_main) {
            // Over the gap with a crystal (fetch one from spawn first if needed).
            int to_launch = altar_launch_field[k] ? field_at(*altar_launch_field[k], p) : cheb(p, altar_launch[k]) * 5 / 4 + 2;
            if (to_launch >= distance_field::unreachable) continue;
            d = to_launch + 3 + altar_land_dist[k] + (crystal ? 0 : std::min(spawn_dist_at(p), 12) + 2);
            via_jump = true;
        }
        if (d >= distance_field::unreachable) continue;
        if (altar_enemy_lock[k] >= 0) d += 6;  // break their lock first (5 hits)
        if (d < bda) { bda = d; best_any = static_cast<int>(k); ajump = via_jump; }
        if (threat) {
            bool free_spot = false;
            for (const vec2 q : altar_spot_list[k])
                if (!bb_test(*threat, q)) { free_spot = true; break; }
            if (!free_spot) continue;
        }
        if (threat && bb_test(*threat, altars[k])) continue;  // enemies seen around it
        if (d < bd) { bd = d; best = static_cast<int>(k); bjump = via_jump; }
    }
    if (best < 0) { best = best_any; bd = bda; bjump = ajump; }
    if (jump) *jump = bjump;
    if (best < 0 && f_altar && !altar_spots->is_empty()) {  // per-altar fields not built yet: use the joint field
        dist = field_at(*f_altar, p);
        return -1;
    }
    dist = bd;
    return best;
}

namespace {
bitboard dilate(const bitboard& b, int r) {
    bitboard x = b;
    for (int k = 1; k <= r; ++k) {
        x |= b.shift_right(k);
        x |= b.shift_right(-k);
    }
    bitboard y = x;
    for (int k = 1; k <= r; ++k) {
        y |= x.shift_up(k);
        y |= x.shift_up(-k);
    }
    return y;
}
}  // namespace

bool World::analyse_island(Group& g) {
    if (g.island_done) return true;
    if (fuel() < 40000) return false;
    // Region around the group reachable on foot (holes and walls block); the group's own tiles are roots.
    bitboard walls = *fwalls | *camp_tiles;
    walls &= ~*g.tiles;
    bitboard region;
    if (!g.field) {
        g.field = std::make_unique<distance_field>();
        g.field->compute(walls, *g.tiles, region);
        ++total_fields_built;
        set_tp_spawn(g);
    } else {
        distance_field tmp;
        tmp.compute(walls, *g.tiles, region);
    }
    region &= ~*camp_tiles;
    region &= ~*blocked;
    g.island_done = true;
    g.island = -1;
    int ld = 0;
    if (!find_jump(region, *g.field, g.tp_launch, g.tp_land, g.tp_land_dist, ld)) return true;
    g.island = 1;
    g.spawn_dist = ld + 3 + g.tp_land_dist;
    return true;
}

bool World::find_jump(const bitboard& region, const distance_field& target, vec2& launch, vec2& land, int& land_dist, int& launch_dist) {
    const bitboard cand = dilate(region, 3) & *mainland;
    if (cand.is_empty()) return false;
    int best = distance_field::unreachable;
    for (vec2 q : cand.positions()) {
        const int d = df_get(*f_spawn, q);
        if (d < best) { best = d; launch = q; }
    }
    if (best == distance_field::unreachable) return false;
    bitboard near;
    near.clear();
    near.draw_chebyshev(launch, 3.f);
    near &= region;
    int bl = distance_field::unreachable;
    for (vec2 q : near.positions()) {
        const int d = df_get(target, q);
        if (d < bl) { bl = d; land = q; }
    }
    if (bl == distance_field::unreachable) return false;
    land_dist = bl;
    launch_dist = best;
    return true;
}

void World::ensure_launch_field(Group& g) {
    if (g.launch_field || g.island != 1 || fuel() < 50000) return;
    const bitboard walls = *fwalls | *camp_tiles;
    bitboard root, visited;
    root.clear();
    root.set(g.tp_launch);
    g.launch_field = std::make_unique<distance_field>();
    g.launch_field->compute(walls, root, visited);
}

int World::island_dist(Group& g, vec2 p) {
    if (g.island != 1) return 1 << 20;
    int to_launch;
    if (g.launch_field) {
        to_launch = field_at(*g.launch_field, p);
        if (to_launch >= distance_field::unreachable) return 1 << 20;
    } else {
        to_launch = cheb(p, g.tp_launch) * 5 / 4 + 2;
    }
    return to_launch + 3 + g.tp_land_dist;
}
