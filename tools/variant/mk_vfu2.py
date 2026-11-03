"""Cheaper setup, same decisions: python -I mk_vfu2.py NAME GATE [--base bots/exp/vnl1] [--src src] [--check]

The draft writes spawn distances, altar sides and the central flag to draft memory; champions read them. Group tile bitboards become lazy,
tile_group needs no fill, the camp layout words are read once without building objects, the altar loop shares one mask.
--check builds a probe that also computes the numbers and prints mismatches and the fuel left at the end of the setup (never ship it).
"""
import os, re, shutil, sys
args = sys.argv[1:]
name, gate = args[0], args[1]
base = args[args.index('--base') + 1] if '--base' in args else 'bots/exp/vnl1'
srcd = args[args.index('--src') + 1] if '--src' in args else 'src'
check = '--check' in args
dst = 'bots/exp/' + name
if base != dst:
    if os.path.exists(dst):
        shutil.rmtree(dst)
    shutil.copytree(base, dst, ignore=shutil.ignore_patterns('.cambc'))
S = dst + '/' + srcd + '/'


def rd(p):
    return open(p, encoding='utf-8', newline='').read()


def wr(p, s):
    open(p, 'w', encoding='utf-8', newline='').write(s)


def sub(path, a, b, cnt=1):
    s = rd(path)
    assert s.count(a) == cnt, (a, s.count(a))
    wr(path, s.replace(a, b))


# common.h: raw bit set
sub(S + 'common.h', 'inline bool bb_test(const bitboard& b, vec2 p) {', """// One bit of an in-bounds tile, without the host call of bitboard::set.
inline void bb_put(bitboard& b, vec2 p) {
    const auto& L = detail::layout();
    b.ptr()[static_cast<std::size_t>((p.y >> 3) * static_cast<int>(L.chunk_stride) + (p.x >> 3))] |= 1ull << (((p.y & 7) << 3) | (p.x & 7));
}

inline bool bb_test(const bitboard& b, vec2 p) {""")

# world.h
h = S + 'world.h'
sub(h, '    std::vector<std::int16_t> tile_group;  // tile -> group id (-1 none)', '    std::int16_t* tile_group = nullptr;  // tile -> group id + 1 (0 none); static storage, so no fill')
sub(h, '    int group_at(vec2 p) const { return in_bounds(p) ? tile_group[p.y * w + p.x] : -1; }', """    int group_at(vec2 p) const { return in_bounds(p) ? tile_group[p.y * w + p.x] - 1 : -1; }
    // The group's tiles as a bitboard, built on first use (a bitboard for every group cost about 40k of the setup).
    const bitboard& tiles_of(Group& g) const {
        if (!g.tiles) {
            g.tiles.emplace();
            for (const auto& c : g.camps) bb_put(*g.tiles, c.pos);
        }
        return *g.tiles;
    }""")

# world.cpp
w = S + 'world.cpp'
s = rd(w)
a = '    tile_group.assign(static_cast<std::size_t>(w) * h, -1);'
assert s.count(a) == 1
s = s.replace(a, """    {
        static std::int16_t tile_group_store[100 * 100];  // maps run up to 100x100
        tile_group = static_cast<std::size_t>(w) * h <= 100 * 100 ? tile_group_store : new std::int16_t[static_cast<std::size_t>(w) * h]();
    }""")
i, j = s.index('    auto api_groups = map::camp_groups();'), s.index('    // altar tribute spots')
s = s[:i] + """    // The engine's layout words, read once: map::camp_groups() builds an object for every camp and group.
    static std::uint32_t layout_words[4096];
    std::vector<std::uint32_t> layout_big;
    std::uint32_t layout_count = 0;
    const std::uint32_t* lw = layout_words;
    detail::check(detail::sdk_map_camp_layout(layout_words, 4096, &layout_count));
    if (layout_count > 4096) {
        layout_big.resize(layout_count);
        detail::check(detail::sdk_map_camp_layout(layout_big.data(), layout_count, &layout_count));
        lw = layout_big.data();
    }
    {
        std::size_t n_groups = 0;
        for (std::size_t i = 0; i + 5 <= layout_count; i += 5 + 4 * static_cast<std::size_t>(lw[i + 4])) ++n_groups;
        groups.reserve(n_groups);
    }
    for (std::size_t i = 0; i + 5 <= layout_count;) {
        Group g;
        g.id = static_cast<int>(groups.size());
        g.handle = lw[i];
        g.gold = static_cast<int>(lw[i + 1]);
        g.gems = static_cast<int>(lw[i + 2]);
        g.respawn = static_cast<std::int32_t>(lw[i + 3]);
        const std::uint32_t n_camps = lw[i + 4];
        i += 5;
        g.camps.reserve(n_camps);
        long sx = 0, sy = 0;
        bool only_clusters = true;
        for (std::uint32_t m = 0; m < n_camps && i + 4 <= layout_count; ++m, i += 4) {
            const camp_type kind = static_cast<camp_type>(lw[i + 1]);
            Camp cp{ vec2{ static_cast<std::int32_t>(lw[i + 2]), static_cast<std::int32_t>(lw[i + 3]) }, kind, camp_max_hp(kind), camp_max_hp(kind) };
            cp.handle = lw[i];
            g.camps.push_back(cp);
            bb_put(*camp_tiles, cp.pos);
            tile_group[cp.pos.y * w + cp.pos.x] = static_cast<std::int16_t>(g.id + 1);
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
        groups.push_back(std::move(g));
    }

""" + s[j:]
wr(w, s)
sub(w, """    *altar_spots &= ~*blocked;
    *altar_spots &= ~*camp_tiles;

    for (auto a : altars) {
        bitboard b;
        b.clear();
        b.draw_chebyshev(a, static_cast<float>(constants::submit_gems_range));
        b &= ~*blocked;
        b &= ~*camp_tiles;
        altar_spot_of.push_back(b);
        altar_spot_list.push_back(b.positions());
""", """    const bitboard free_ground = ~(*blocked | *camp_tiles);
    *altar_spots &= free_ground;

    altar_spot_of.reserve(altars.size());
    altar_spot_list.reserve(altars.size());
    altar_field.reserve(altars.size());
    altar_jump_ok.reserve(altars.size());
    altar_enemy_lock.reserve(altars.size());
    altar_launch.reserve(altars.size());
    altar_land.reserve(altars.size());
    altar_land_dist.reserve(altars.size());
    altar_launch_field.reserve(altars.size());
    altar_side.reserve(altars.size());
    for (auto a : altars) {
        bitboard b;
        b.draw_chebyshev(a, static_cast<float>(constants::submit_gems_range));
        b &= free_ground;
        altar_spot_list.push_back(b.positions());
        altar_spot_of.push_back(std::move(b));
""")
# plan helpers before World::init
sub(w, 'void World::init() {', """namespace {
// Draft plan: the first draft turn has 100 times the fuel and draft memory is the only channel to the champions.
// 'V' 'P' version flags, groups (2), altars (2), checksum (2), then 2 bytes per group (steps from our spawn) and 2 per altar (side).
constexpr std::size_t kPlanHeader = 10, kPlanBytes = 1024;
constexpr std::uint8_t kPlanVersion = 1;
std::uint8_t plan_buf[kPlanBytes];

std::uint16_t plan_sum(const std::vector<Group>& groups) {
    std::uint32_t s = 0;
    for (const auto& g : groups) s = (s * 31 + static_cast<std::uint32_t>(g.camps[0].pos.x * 101 + g.camps[0].pos.y) + static_cast<std::uint32_t>(g.camps.size())) & 0xFFFF;
    return static_cast<std::uint16_t>(s);
}

int plan_u16(const std::uint8_t* p) { return p[0] | (p[1] << 8); }

void plan_put(std::uint8_t* p, int v) {
    p[0] = static_cast<std::uint8_t>(v & 0xFF);
    p[1] = static_cast<std::uint8_t>((v >> 8) & 0xFF);
}
}  // namespace

void World::init() {""")
sub(w, """    if (P_BRIDGES) {
        try {""", """    if (P_BRIDGES && !cambc::is_draft()) {
        try {""")
sub(w, """    central_altars = !P_CENTRAL_GATE;
    if (P_CENTRAL_GATE && !altars.empty()) {""", """    // The draft's numbers, when they match this map.
    const std::uint8_t* plan = nullptr;
    if (!cambc::is_draft()) {
        std::uint32_t plan_size = 0;
        detail::check(detail::sdk_draft_memory_size(&plan_size));
        if (plan_size >= kPlanHeader && plan_size <= kPlanBytes) {
            detail::check(detail::sdk_read_draft_memory(0, reinterpret_cast<std::byte*>(plan_buf), plan_size));
            const std::size_t ng = static_cast<std::size_t>(plan_u16(plan_buf + 4)), na = static_cast<std::size_t>(plan_u16(plan_buf + 6));
            if (plan_buf[0] == 'V' && plan_buf[1] == 'P' && plan_buf[2] == kPlanVersion && ng == groups.size() && na == altars.size() &&
                kPlanHeader + 2 * (ng + na) <= plan_size && plan_u16(plan_buf + 8) == plan_sum(groups))
                plan = plan_buf;
        }
    }
    central_altars = !P_CENTRAL_GATE;
    if (plan && !PLAN_CHECK) {
        central_altars = (plan[3] & 1) != 0;
    } else if (P_CENTRAL_GATE && !altars.empty()) {""")
sub(w, """    // Reachability: some walkable neighbour of a camp tile is reachable from spawn.
    for (auto& g : groups) {
        int best = distance_field::unreachable;""", """    // Reachability: some walkable neighbour of a camp tile is reachable from spawn.
    // The plan holds the numbers of a champion without bridges.
    const bool plan_fields = plan && !PLAN_CHECK && bridges->is_empty();
    if (plan_fields) {
        const std::uint8_t* q = plan + kPlanHeader;
        for (auto& g : groups) {
            const int best = plan_u16(q);
            q += 2;
            g.reachable = best != distance_field::unreachable;
            g.spawn_dist = best;
            if (!g.reachable) any_island = true;
        }
        for (std::size_t k = 0; k < altars.size(); ++k, q += 2) altar_side.push_back(static_cast<std::int16_t>(plan_u16(q)));
    } else for (auto& g : groups) {
        int best = distance_field::unreachable;""")
sub(w, """    for (std::size_t k = 0; k < altars.size(); ++k) {
        const vec2 a = altars[k];
        vec2 m = a;
        try {
            m = sym == symmetry::horizontal""", """    if (!plan_fields) for (std::size_t k = 0; k < altars.size(); ++k) {
        const vec2 a = altars[k];
        vec2 m = a;
        try {
            m = sym == symmetry::horizontal""")
extra = ''
if check:
    extra = """    if (plan && !cambc::is_draft() && bridges->is_empty()) {
        const std::uint8_t* q = plan + kPlanHeader;
        for (const auto& g : groups) { if (plan_u16(q) != g.spawn_dist) ++plan_mismatch; q += 2; }
        for (std::size_t k = 0; k < altars.size(); ++k, q += 2) if (static_cast<std::int16_t>(plan_u16(q)) != altar_side[k]) ++plan_mismatch;
        if (((plan[3] & 1) != 0) != central_altars) ++plan_mismatch;
        bitboard ct;
        for (const auto& g : groups) for (const auto& c : g.camps) ct.set(c.pos);
        if (!(ct ^ *camp_tiles).is_empty()) ++plan_mismatch;
    }
    plan_seen = plan != nullptr;
"""
sub(w, '    // Gated altars: no walkable tribute spot', extra + """    if (cambc::is_draft()) {
        // Draft: only the plan's numbers are needed. They are the numbers of a champion without bridges, because dasher stays false here.
        const std::size_t ng = groups.size(), na = altars.size(), used = kPlanHeader + 2 * (ng + na);
        if (used > kPlanBytes) return;
        plan_buf[0] = 'V';
        plan_buf[1] = 'P';
        plan_buf[2] = kPlanVersion;
        plan_buf[3] = central_altars ? 1 : 0;
        plan_put(plan_buf + 4, static_cast<int>(ng));
        plan_put(plan_buf + 6, static_cast<int>(na));
        plan_put(plan_buf + 8, plan_sum(groups));
        std::uint8_t* q = plan_buf + kPlanHeader;
        for (const auto& g : groups) { plan_put(q, g.spawn_dist); q += 2; }
        for (const int v : altar_side) { plan_put(q, v); q += 2; }
        cambc::draft_memory_buffer mem;
        mem = std::span<const std::byte>(reinterpret_cast<const std::byte*>(plan_buf), used);
        return;
    }
    // Gated altars: no walkable tribute spot""")
sub(w, """    walls &= ~*g.tiles;
    bitboard visited;
    g.field = std::make_unique<distance_field>();
    g.field->compute(walls, *g.tiles, visited);""", """    const bitboard& gt = tiles_of(g);
    walls &= ~gt;
    bitboard visited;
    g.field = std::make_unique<distance_field>();
    g.field->compute(walls, gt, visited);""")
s = rd(w)
s = s.replace('World& world() {', ('#define PLAN_CHECK 1\nint plan_mismatch = 0; bool plan_seen = false;\n' if check else '#define PLAN_CHECK 0\n') + 'World& world() {', 1)
wr(w, s)

# group tile tests through the table
for fn in ('farm.cpp', 'fight.cpp'):
    s = rd(S + fn)
    s = re.sub(r'(\w+)\.tiles && bb_test\(\*\1\.tiles, ([^()]+?)\)', r'(world().group_at(\2) == \1.id)', s)
    s = re.sub(r'bb_test\(\*(\w+)\.tiles, ([^()]+?)\)', r'(world().group_at(\2) == \1.id)', s)
    s = s.replace('bitboard goals = *g.tiles;', 'bitboard goals = world().tiles_of(g);')
    assert not re.search(r'[.]tiles[^_]', s), fn
    wr(S + fn, s)

# gate
sub(S + 'bot.cpp', 'if (fuel() < 120000) return;  // big maps: finish setup, act next turn', f'if (fuel() < {gate}) return;  // the setup ran out: act on the next turn')
if check:
    s = rd(S + 'bot.cpp')
    s = s.replace('#include "bot.h"', '#include "bot.h"\n#include <iostream>\n#include <string>\nextern int plan_mismatch; extern bool plan_seen;', 1)
    a = '    inited = true;\n}'
    assert s.count(a) == 1
    s = s.replace(a, '    inited = true;\n    if (idx == 0) std::cout << "FP mism=" << plan_mismatch << " plan=" << plan_seen << " r=" << round_number() << " fuel=" << fuel() << std::endl;\n}')
    wr(S + 'bot.cpp', s)

# draft writes the plan first
d = S + 'draft.cpp'
s = rd(d)
s = s.replace('#include "params.h"', '#include "params.h"\n#include "world.h"', 1)
a = 'void play_draft() {\n'
assert s.count(a) == 1
s = s.replace(a, a + """    static bool plan_done = false;
    if (!plan_done) {
        plan_done = true;
        try { world().init(); } catch (...) {}
    }
""")
wr(d, s)
wr(dst + '/NOTE.txt', 'Fuel: setup from the draft plan, first move on round 1-2 on every map (was round 2-6)\n')
print('ok', dst)
