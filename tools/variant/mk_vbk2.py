"""Per-map opening book, on the no-log v1503: python -I mk_vbk.py NAME BOOK.json R A WMIN WMAX [BASE] [--maps m1,m2]
Before round R a group's value is multiplied by clamp((f_them + A) / (f_us + A), WMIN, WMAX), where f are the shares of games in which the rivals and we hit the group early (tools/replay/openbook.py)."""
import json, math, os, shutil, sys
args = sys.argv[1:]
only = None
if '--maps' in args:
    k = args.index('--maps'); only = set(args[k + 1].split(',')); del args[k:k + 2]
name, book, r, a, wmin, wmax = args[0], args[1], args[2], float(args[3]), float(args[4]), float(args[5])
base = args[6] if len(args) > 6 else 'bots/exp/vnl1'
dst = 'bots/exp/' + name
if os.path.exists(dst):
    shutil.rmtree(dst)
shutil.copytree(base, dst, ignore=shutil.ignore_patterns('.cambc'))
B = json.load(open(book, encoding='utf-8'))
SIG = json.load(open('data/map_sigs.json', encoding='utf-8'))
def sub(path, x, y, cnt=1):
    s = open(path, encoding='utf-8', newline='').read()
    assert s.count(x) == cnt, (x, s.count(x))
    s = s.replace(x, y)
    open(path, 'w', encoding='utf-8', newline='').write(s)
rows, maps = [], []
for mp in sorted(B):
    b = B[mp]
    if only is not None and mp not in only:
        continue
    if b['nthem'] < 6 or b['nus'] < 3 or b['symhit'] < 0.8:
        continue
    first = len(rows)
    for g in b['groups']:
        w = (g['them'] + a) / (g['us'] + a)
        w = max(wmin, min(wmax, w))
        if abs(math.log(w)) < math.log(1.25):
            continue
        rows.append('    {%d, %d, %d, %d, %d},' % (g['tile'][0], g['tile'][1], g['tile1'][0], g['tile1'][1], round(w * 10)))
    n = len(rows) - first
    if n:
        s = SIG[mp]
        maps.append('    {%d, %d, %d, %d, %d, %d, %d, %d, %d, %d},  // %s' % (s[0], s[1], s[2], s[3], s[4], s[5], b['start0'][0], b['start0'][1], first, n, mp))
print(len(maps), 'maps', len(rows), 'rows')
p = dst + '/' + os.environ.get('SRC', 'src') + '/params.h'
s = open(p, encoding='utf-8', newline='').read()
s = s.rstrip('\n') + f"""

#ifndef P_BOOK_R
#define P_BOOK_R {r}       // before this round the opening book weights a group's value (kBookRows, from the top teams' first targets per map)
#endif
"""
open(p, 'w', encoding='utf-8', newline='').write(s)
sub(dst + '/' + os.environ.get('SRC', 'src') + '/world.h', '    bool big = false;       // golem or monolith inside', '    bool big = false;       // golem or monolith inside\n    float book_w = 1.f;     // opening book weight of this group on this map')
sub(dst + '/' + os.environ.get('SRC', 'src') + '/world.cpp', """        g.side = g.enemy_dist - g.spawn_dist;
    }
    // Gated altars:""", """        g.side = g.enemy_dist - g.spawn_dist;
    }
    {
        // Opening book: the top teams' first targets on this map against ours (tools/replay/openbook.py).
        struct BookMap { short w, h, walls, holes, altars, bushes, sx, sy, first, count; };
        struct BookRow { unsigned char x0, y0, x1, y1, w10; };
        static constexpr BookRow kBookRows[] = {
""" + '\n'.join(rows) + """
        };
        static constexpr BookMap kBookMaps[] = {
""" + '\n'.join(maps) + """
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
    // Gated altars:""")
f = dst + '/' + os.environ.get('SRC', 'src') + '/farm.cpp'
sub(f, """        if (value <= 0) continue;
        if (g.side < -P_SIDE_MARGIN) value *= P_ENEMY_SIDE_W;  // their half: farmed and guarded by them""", """        if (value <= 0) continue;
        if (round < P_BOOK_R) value *= g.book_w;
        if (g.side < -P_SIDE_MARGIN) value *= P_ENEMY_SIDE_W;  // their half: farmed and guarded by them""")
open(dst + '/NOTE.txt', 'w').write(f'Economy: per-map opening book from top teams first targets before r{r}\n')
print('ok', dst)
