#include "world.h"
#include "params.h"
namespace cjb {

World& world() {
    static World w;
    return w;
}

// edit_vtfuel2.py: the set-up in five steps, run in order. Step 0 runs in the first turn (2x fuel); a later one starts only when the
// fuel left covers its estimate, else the set-up resumes at the next turn (on 100x100 maps it cost ~310k and every champion's first
// turn was suspended twice, into round 3). With fuel to spare all steps run at once, exactly as before.
void World::init() {
    while (!ready) {
        // a step dearer than a whole turn runs at the start of one (it cannot wait for more fuel than a turn holds)
        if (init_step > 0 && fuel() < std::min<std::uint64_t>(init_need(), P_INIT_MAX_NEED)) return;
        switch (init_step) {
        case 0: init_a(); break;
        case 1: init_b(); break;
        case 2: if (!init_c()) return; break;
        case 3: init_d(); break;
        default: init_e(); break;
        }
        ++init_step;
    }
}

// edit_vtfuel2.py: fuel the next step needs (a full-map search costs ~3.1 a tile on 100x100 maps; margins on top)
std::uint64_t World::init_need() const {
    const std::uint64_t bfs = init_bfs();
    std::uint64_t ncamps = 0;
    for (const auto& g : groups) ncamps += g.camps.size();
    switch (init_step) {
    case 1: return P_CENTRAL_GATE && !altars.empty() ? bfs : 3000;
    case 2: {  // dash bridges: their first part (~10k of board shifts) - the candidate holes are then checked while fuel lasts
        const bool brid = dasher && central_altars && !map::holes().is_empty();
        return brid ? 15000 : 4000 + (vt_plain ? 0 : bfs);
    }
    case 3: return bfs;
    default: return 5000 + ncamps * 260 + groups.size() * 200 + altars.size() * 1000;  // init_e: ~230 a camp, ~800 an altar, ~190 a group
    }
}

// edit_vtfuel2.py: reads of a distance field's chunked buffer F (chunked width cw) for in-map tiles of a w x h map.
// vt_min8: the least value over the in-map 8-neighbours of (x, y) (any tile); vt_field_at: World::field_at's value.
static inline int vt_min8(const std::uint16_t* F, int cw, int w, int h, int x, int y) {
    int best = distance_field::unreachable;
    const int bx = x & 7, by = y & 7;
    if (bx >= 1 && bx <= 6 && by >= 1 && by <= 6 && x + 1 < w && y + 1 < h) {  // all 8 inside the tile's own chunk
        const std::uint16_t* c = F + static_cast<std::size_t>(((y >> 3) * cw + (x >> 3)) * 64 + (by << 3) + bx);
        const int a = std::min(std::min(c[-9], c[-8]), std::min(c[-7], c[-1]));
        const int b = std::min(std::min(c[1], c[7]), std::min(c[8], c[9]));
        return std::min(a, b);
    }
    auto row = [cw](int yy) { return (yy >> 3) * cw * 64 + ((yy & 7) << 3); };
    auto col = [](int xx) { return ((xx >> 3) << 6) + (xx & 7); };
    if (x >= 0 && y >= 0 && x < w && y < h) {  // on the map: the 8 reads unrolled, edges skipped
        const bool yl = y > 0, yh = y + 1 < h, xl = x > 0, xh = x + 1 < w;
        const int r1 = row(y), c1 = col(x);
        const int c0 = xl ? col(x - 1) : 0, c2 = xh ? col(x + 1) : 0;
        if (yl) {
            const int r0 = row(y - 1);
            if (xl) best = std::min<int>(best, F[r0 + c0]);
            best = std::min<int>(best, F[r0 + c1]);
            if (xh) best = std::min<int>(best, F[r0 + c2]);
        }
        if (xl) best = std::min<int>(best, F[r1 + c0]);
        if (xh) best = std::min<int>(best, F[r1 + c2]);
        if (yh) {
            const int r2 = row(y + 1);
            if (xl) best = std::min<int>(best, F[r2 + c0]);
            best = std::min<int>(best, F[r2 + c1]);
            if (xh) best = std::min<int>(best, F[r2 + c2]);
        }
        return best;
    }
    for (int dy = -1; dy <= 1; ++dy) {
        const int yy = y + dy;
        if (yy < 0 || yy >= h) continue;
        for (int dx = -1; dx <= 1; ++dx) {
            const int xx = x + dx;
            if ((dx == 0 && dy == 0) || xx < 0 || xx >= w) continue;
            const int v = F[static_cast<std::size_t>(row(yy) + col(xx))];
            if (v < best) best = v;
        }
    }
    return best;
}
static inline int vt_field_at(const std::uint16_t* F, int cw, int w, int h, vec2 p) {
    if (p.x >= 0 && p.y >= 0 && p.x < w && p.y < h) {
        const int d = F[static_cast<std::size_t>(((p.y >> 3) * cw + (p.x >> 3)) * 64 + ((p.y & 7) << 3) + (p.x & 7))];
        if (d != distance_field::unreachable) return d;
    }
    const int v = vt_min8(F, cw, w, h, p.x, p.y);
    return v == distance_field::unreachable ? v : v + 1;
}

void World::init_a() {
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

    // edit_vtfuel2.py: the camp groups read from the engine's batched layout query (the words map::camp_groups() parses) straight
    // into place: the same groups, camps, handles, order and boards. map::camp_groups() first built SDK groups with a camp vector
    // each (25-36k fuel on big maps), and the Group moves, camp vector regrowth, host bit sets and the dense tile table cost as much
    // again. Group::api is no longer filled (nothing reads it).
    tg_cw = (w + 7) >> 3;
    tg_chunk.assign(static_cast<std::size_t>(tg_cw) * static_cast<std::size_t>((h + 7) >> 3), -1);
    camp_tiles.emplace();
    camp_tiles->clear();
    {
        struct MapArm { short w, h, walls, holes, altars, bushes; float light, wolf, heavy, enable; short r; float gold, gem; };
        static constexpr MapArm kMapArms[] = {
    {50, 50, 222, 0, 2, 186, 1.50f, 1.00f, 1.00f, 1.60f, 150, 1.00f, 3.00f},  // 01elk_arena (L)
    {31, 31, 88, 0, 1, 60, 1.50f, 1.00f, 1.00f, 1.60f, 150, 1.00f, 3.00f},  // 01hooks (L)
    {35, 29, 62, 109, 2, 54, 1.50f, 1.00f, 1.00f, 1.60f, 150, 1.00f, 3.00f},  // 00quarry (L)
    {50, 65, 0, 654, 4, 152, 1.50f, 1.00f, 1.00f, 1.60f, 150, 1.00f, 3.00f},  // 00pilgrimage (L)
    {61, 71, 374, 540, 3, 276, 1.50f, 1.00f, 1.00f, 1.60f, 150, 1.00f, 3.00f},  // 01fracture (L)
    {50, 50, 214, 0, 2, 140, 1.00f, 1.00f, 1.00f, 1.00f, 0, 2.00f, 3.00f},  // 00rows (G2)
    {30, 30, 96, 0, 2, 40, 1.00f, 1.00f, 1.00f, 1.00f, 0, 2.00f, 3.00f},  // 02arena (G2)
    {51, 41, 222, 10, 2, 32, 1.00f, 1.00f, 1.00f, 1.00f, 0, 1.00f, 12.00f},  // 03one_gem (GN)
        };
        const int mw = map::width(), mh = map::height();
        const int mwalls = static_cast<int>(map::walls().count()), mholes = static_cast<int>(map::holes().count());
        const int maltars = static_cast<int>(map::altars().count()), mbushes = static_cast<int>(map::bushes().count());
        for (const MapArm& m : kMapArms)
            if (m.w == mw && m.h == mh && m.walls == mwalls && m.holes == mholes && m.altars == maltars && m.bushes == mbushes) {
                arm_r = m.r; arm_light = m.light; arm_wolf = m.wolf; arm_heavy = m.heavy; arm_enable = m.enable; arm_gold = m.gold; arm_gem = m.gem;
            }
    }
    std::uint32_t lcap = 4096, lcount = 0;
    std::unique_ptr<std::uint32_t[]> words(new std::uint32_t[lcap]);
    detail::check(detail::sdk_map_camp_layout(words.get(), lcap, &lcount));
    if (lcount > lcap) {
        lcap = lcount;
        words.reset(new std::uint32_t[lcap]);
        detail::check(detail::sdk_map_camp_layout(words.get(), lcap, &lcount));
    }
    lcount = std::min(lcount, lcap);
    std::size_t ngroups = 0, ncamps = 0;
    for (std::size_t i = 0; i + 5 <= lcount;) {
        const std::uint32_t size = words[i + 4];
        i += 5;
        ++ngroups;
        for (std::uint32_t m = 0; m < size && i + 4 <= lcount; ++m, i += 4) ++ncamps;
    }
    groups.reserve(ngroups);
    tg_cell.reserve(std::min(ncamps, tg_chunk.size()) * 64);
    const auto& LY = detail::layout();
    const int lcs = static_cast<int>(LY.chunk_stride);
    std::uint64_t* const CT = camp_tiles->ptr();
    for (std::size_t i = 0; i + 5 <= lcount;) {
        const int gid = static_cast<int>(groups.size());
        Group& g = groups.emplace_back();
        g.id = gid;
        g.handle = words[i];
        g.gold = static_cast<int>(words[i + 1]);
        g.gems = static_cast<int>(words[i + 2]);
        g.respawn = static_cast<std::int32_t>(words[i + 3]);
        const std::uint32_t size = words[i + 4];
        i += 5;
        g.tiles.emplace();
        g.tiles->clear();
        std::uint64_t* const GT = g.tiles->ptr();
        g.camps.reserve(size);
        long sx = 0, sy = 0;
        bool only_clusters = true;
        for (std::uint32_t m = 0; m < size && i + 4 <= lcount; ++m, i += 4) {
            const camp_type ct = static_cast<camp_type>(words[i + 1]);
            Camp& cp = g.camps.emplace_back();  // the fields Camp{ pos, type, max_hp, max_hp } set, built in place
            cp.pos = vec2{ static_cast<std::int32_t>(words[i + 2]), static_cast<std::int32_t>(words[i + 3]) };
            cp.type = ct;
            cp.max_hp = camp_max_hp(ct);
            cp.hp = cp.max_hp;
            cp.handle = words[i];
            if (cp.pos.x >= 0 && cp.pos.y >= 0 && cp.pos.x < w && cp.pos.y < h) {
                const std::size_t wi = static_cast<std::size_t>((cp.pos.y >> 3) * lcs + (cp.pos.x >> 3));
                const std::uint64_t bit = 1ull << (((cp.pos.y & 7) << 3) | (cp.pos.x & 7));
                GT[wi] |= bit;
                CT[wi] |= bit;
            }
            tg_set(cp.pos, g.id);
            g.total_max_hp += cp.max_hp;
            g.dps += camp_str(cp.type);
            g.max_range = std::max(g.max_range, camp_range(cp.type));
            if (cp.type == camp_type::golem || cp.type == camp_type::monolith) g.big = true;
            if (cp.type == camp_type::golem || cp.type == camp_type::monolith || cp.type == camp_type::elk) g.heavy = true;
            if (cp.type == camp_type::monolith) g.monolith = true;
            if (cp.type != camp_type::gem_cluster && cp.type != camp_type::gold_cluster) only_clusters = false;
            sx += cp.pos.x;
            sy += cp.pos.y;
        }
        g.harmless = only_clusters;
        const long n = static_cast<long>(g.camps.size());
        g.center = { static_cast<int>(sx / n), static_cast<int>(sy / n) };
        for (const auto& c : g.camps) g.radius = std::max(g.radius, cheb(c.pos, g.center));
    }

    // altar tribute spots
    altar_spots.emplace();
    altar_spots->clear();
    for (auto a : altars) altar_spots->draw_chebyshev(a, static_cast<float>(constants::submit_gems_range));
    *altar_spots &= open_tiles();  // edit_vtfuel2.py: ~blocked & ~camp_tiles, cached (edit_vtfuel.py V4)

    {  // edit_vtfuel2.py: no regrowth of the per-altar vectors
        const std::size_t na = altars.size();
        altar_spot_of.reserve(na);
        altar_spot_list.reserve(na);
        altar_field.reserve(na);
        altar_jump_ok.reserve(na);
        altar_enemy_lock.reserve(na);
        altar_launch.reserve(na);
        altar_land.reserve(na);
        altar_land_dist.reserve(na);
        altar_launch_field.reserve(na);
    }
    for (auto a : altars) {
        bitboard b;
        b.draw_chebyshev(a, static_cast<float>(constants::submit_gems_range));
        b &= open_tiles();  // edit_vtfuel2.py
        altar_spot_list.push_back(b.positions());
        altar_spot_of.push_back(std::move(b));
        altar_field.emplace_back();
        altar_jump_ok.push_back(0);
        altar_enemy_lock.push_back(-1);
        altar_launch.push_back({ -1, -1 });
        altar_land.push_back({ -1, -1 });
        altar_land_dist.push_back(0);
        altar_launch_field.emplace_back();
    }
}

void World::init_b() {  // edit_vtfuel2.py: the central-gate check (the plain spawn search, kept in vt_plain for init_c)
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
        vt_plain_vis.emplace(std::move(vis0));  // edit_vtfuel.py
        vt_plain.emplace(std::move(plain));
    }
}

bool World::init_c() {  // edit_vtfuel2.py: dash bridges (over several turns if need be), f_spawn, mainland
    if (dasher && central_altars && !map::holes().is_empty()) {
        // Ground reachable on foot from spawn: a bridge needs one landing there (one hop onto an island at most:
        // island chains cost 8 rounds of dash cooldown per hop and stranded champions on islands).
        if (!vt_bfoot) {  // edit_vtfuel2.py: first call: the foot region and the candidate holes, kept until the check is done
            vt_bfoot.emplace();
            bitboard& foot = *vt_bfoot;
            if (vt_plain_vis) {
                foot = *vt_plain_vis;  // edit_vtfuel.py: the same search as the plain field above
            } else {
                distance_field fw;
                fw.compute((*blocked) | *camp_tiles, *my_spawn, foot);
            }
            const bitboard fl = ~*blocked;
            const bitboard& ho = map::holes();
            bitboard cand = ho & fl.shift_right(1) & fl.shift_right(-1);
            cand |= ho & fl.shift_up(1) & fl.shift_up(-1);
            cand |= ho & fl.shift_right(1).shift_up(1) & fl.shift_right(-1).shift_up(-1);
            cand |= ho & fl.shift_right(1).shift_up(-1) & fl.shift_right(-1).shift_up(1);
            vt_bcand = cand.positions();
            vt_bi = 0;
        }
        const bitboard& foot = *vt_bfoot;
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
        for (; vt_bi < vt_bcand.size(); ++vt_bi) {
            if (fuel() < P_INIT_LOOP_FUEL) return false;  // edit_vtfuel2.py: the rest next turn
            const vec2 hp = vt_bcand[vt_bi];
            for (const auto d : kOpp) {
                const vec2 a{ hp.x - d.x, hp.y - d.y }, b{ hp.x + d.x, hp.y + d.y };
                if (!in_bounds(a) || !in_bounds(b) || bb_test(*blocked, a) || bb_test(*blocked, b)) continue;
                if (!(bb_test(foot, a) || bb_test(foot, b)) || !ground(a) || !ground(b)) continue;
                bridges->set(hp);
                break;
            }
        }
        // edit_vtfuel2.py: the bridge zone (~4 x P_BRIDGE_RESERVE board shifts) and the spawn search below only with the fuel for both
        if (fuel() < std::min<std::uint64_t>(bridges->is_empty() ? (vt_plain ? 4000 : 4000 + init_bfs()) : 20000 + init_bfs(), P_INIT_MAX_NEED)) return false;
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
    if (vt_plain && bridges->is_empty()) {  // edit_vtfuel.py: no bridge: fwalls == blocked, so this is the plain search
        f_spawn = std::make_unique<distance_field>(std::move(*vt_plain));
        visited = *vt_plain_vis;
    } else {
        f_spawn = std::make_unique<distance_field>();
        f_spawn->compute(walls, *my_spawn, visited);
    }
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
    vt_plain.reset();  // edit_vtfuel2.py
    vt_plain_vis.reset();
    vt_bfoot.reset();
    vt_bcand.clear();
    return true;
}

void World::init_d() {  // edit_vtfuel2.py: f_altar (walls as in init_c)
    const bitboard walls = *fwalls | *camp_tiles;
    bitboard visited;
    f_altar = std::make_unique<distance_field>();
    if (!altar_spots->is_empty()) f_altar->compute(walls, *altar_spots, visited);
}

void World::init_e() {  // edit_vtfuel2.py: reachability, map halves, gates, heavy map
    // Reachability: some walkable neighbour of a camp tile is reachable from spawn.
    // edit_vtfuel2.py: the same minimum over the 8 in-map neighbours, read straight from f_spawn's chunked buffer (bounds-checked
    // df_get calls cost ~45 a read: 31-55k on big maps)
    const auto& L = detail::layout();
    const int cw = static_cast<int>(L.chunked_width);
    const std::uint16_t* const FS = f_spawn->ptr();
    for (auto& g : groups) {
        int best = distance_field::unreachable;
        for (const auto& c : g.camps) {
            const int v = vt_min8(FS, cw, w, h, c.pos.x, c.pos.y);
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
        const int dm = vt_field_at(FS, cw, w, h, a), de = vt_field_at(FS, cw, w, h, m);  // edit_vtfuel2.py: = field_at(*f_spawn, .)
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
    {
        // Opening book: the top teams' first targets on this map against ours (tools/replay/openbook.py).
        struct BookMap { short w, h, walls, holes, altars, bushes, sx, sy, first, count; };
        struct BookRow { unsigned char x0, y0, x1, y1, w10; };
        static constexpr BookRow kBookRows[] = {
    {61, 10, 38, 89, 25},
    {73, 24, 26, 75, 6},
    {52, 27, 47, 72, 15},
    {15, 16, 14, 16, 6},
    {8, 20, 21, 20, 16},
    {20, 22, 9, 22, 5},
    {8, 2, 21, 2, 40},
    {2, 8, 27, 8, 24},
    {2, 13, 27, 13, 35},
    {2, 18, 27, 18, 31},
    {4, 22, 25, 22, 23},
    {1, 24, 28, 24, 14},
        };
        static constexpr BookMap kBookMaps[] = {
    {100, 100, 636, 538, 6, 302, 78, 11, 0, 3},  // 01big_world
    {30, 30, 162, 40, 2, 22, 1, 1, 3, 9},  // 02stalactites
        };
        const int mwalls = static_cast<int>(map::walls().count()), mholes = static_cast<int>(map::holes().count());
        const int maltars = static_cast<int>(map::altars().count()), mbushes = static_cast<int>(map::bushes().count());
        for (const BookMap& m : kBookMaps) {
            if (m.w != w || m.h != h || m.walls != mwalls || m.holes != mholes || m.altars != maltars || m.bushes != mbushes) continue;
            const bool team0 = bb_test(*my_spawn, vec2{ m.sx, m.sy });
            for (int k = m.first; k < m.first + m.count; ++k) {
                const BookRow& b = kBookRows[k];
                const int gid = group_at(team0 ? vec2{ b.x0, b.y0 } : vec2{ b.x1, b.y1 });
                if (gid >= 0) groups[static_cast<std::size_t>(gid)].book_w = static_cast<float>(b.w10) / 10.f;
            }
            break;
        }
    }
    // Gated altars: no walkable tribute spot, but a camp tile within range whose neighbours are walkable.
    int open_altars = 0;
    for (std::size_t k = 0; k < altars.size(); ++k) {
        bool open = false;  // edit_vtfuel2.py: (altar_spot_of[k] & mainland) not empty, from the spot list (no board)
        for (const vec2 q : altar_spot_list[k])
            if (bb_test(*mainland, q)) { open = true; break; }
        if (open) { ++open_altars; continue; }
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
    const std::uint64_t f0 = fuel();
    g.field->compute(walls, *g.tiles, visited);
    const std::uint64_t f1 = fuel();
    if (f1 < f0) vt_field_cost = std::max(vt_field_cost, f0 - f1 + 2000);  // edit_vtfuel3.py (+ the walls and the tp check)
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
    // edit_vtfuel3.py: an altar's field is a full-map search plus the jump check for a cut-off altar (~10k); a group field costs
    // what the dearest one did (vt_field_need) - was a fixed 65k / 30k and cells x 4 + 8k, so at a turn's end (reserve 45k) no
    // field of a 100x100 map was ever built and far groups kept estimated distances all game
    const std::uint64_t per_field = vt_field_need();
    vt_altar_need = reserve + per_field + 10000;
    if (fuel() > vt_altar_need) ensure_altar_fields();
    if (any_island)
        for (auto& g : groups)
            if (!g.reachable && !g.island_done && fuel() > std::max<std::uint64_t>(std::max<std::uint64_t>(reserve + 25000, reserve + per_field + 12000), 42000)) analyse_island(g);  // edit_vtfuel3.py
    // Build fields for the nearest groups first.
    while (fuel() > reserve + vt_field_need()) {  // edit_vtfuel3.py: the dearest field so far, also the ones built in this loop
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
        // edit_vtfuel3.py: the same values read straight from the field's chunked buffer
        const std::uint16_t* const F = g.field->ptr();
        const int cw = static_cast<int>(detail::layout().chunked_width);
        if (p.x >= 0 && p.y >= 0 && p.x < w && p.y < h) {
            const int d = F[static_cast<std::size_t>(((p.y >> 3) * cw + (p.x >> 3)) * 64 + ((p.y & 7) << 3) + (p.x & 7))];
            if (d != distance_field::unreachable) return d;
        }
        // Standing on a camp tile (walls in the static fields): go through a neighbour.
        const int v = vt_min8(F, cw, w, h, p.x, p.y);
        return v == distance_field::unreachable ? 1 << 20 : v + 1;
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
    if (this->vis) vision::visible_tiles_into(*this->vis);  // edit_vtfuel.py: same board, no allocation
    else this->vis.emplace(vision::visible_tiles());
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
                if (cs == 1) { c.awake_round = round; g.awake_max = std::max(g.awake_max, round); }  // edit_vtfuel.py
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
        if (fuel() < vt_altar_need) return;  // edit_vtfuel3.py: set by precompute (was 65k)
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
    const int vcw = static_cast<int>(detail::layout().chunked_width);  // edit_vtfuel3.py
    const int vcs = static_cast<int>(detail::layout().chunk_stride);
    const std::uint64_t* const TB = threat ? threat->ptr() : nullptr;
    auto tb = [&](vec2 q) {  // = bb_test(*threat, q)
        if (q.x < 0 || q.y < 0 || q.x >= w || q.y >= h) return false;
        return ((TB[static_cast<std::size_t>((q.y >> 3) * vcs + (q.x >> 3))] >> (((q.y & 7) << 3) | (q.x & 7))) & 1ull) != 0;
    };
    for (std::size_t k = 0; k < altars.size(); ++k) {
        if (!altar_field[k]) continue;
        int d = vt_field_at(altar_field[k]->ptr(), vcw, w, h, p);  // edit_vtfuel3.py: = field_at(*altar_field[k], p)
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
        if (d >= bd) continue;  // edit_vtfuel3.py: cannot beat the best free altar: its threat tests change nothing
        if (threat) {
            bool free_spot = false;
            for (const vec2 q : altar_spot_list[k])
                if (!tb(q)) { free_spot = true; break; }
            if (!free_spot) continue;
        }
        if (threat && tb(altars[k])) continue;  // enemies seen around it
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
}  // namespace cjb
