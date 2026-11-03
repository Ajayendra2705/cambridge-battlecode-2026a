"""Router with per-map opening arms in its v1503 part: python -I mk_rt.py NAME SPEC.json [--base bots/exp/rt3] [--note "text"]

SPEC.json maps a map name to an arm name. Arms (light, wolf, heavy, enable, round): L = vlc1 (1.5, 1, 1, 1.6, 150), L3 = vlc3 (1.5, 1, 1, 1, 150), W1 = vwf1 (1.5, 1.5, 1, 1.6, 120), W2 = vwf2 (1, 1, 0.6, 1.2, 120).
Before `round`, on that map, a harmless group's value counts `light` times, a group whose hardest camp is a wolf `wolf` times, a group with an elk, golem or monolith `heavy` times, and P_ENABLE is `enable`.
"""
import json, os, shutil, sys

args = sys.argv[1:]
base = 'bots/exp/rt3'
note = None
if '--base' in args:
    k = args.index('--base'); base = args[k + 1]; del args[k:k + 2]
if '--note' in args:
    k = args.index('--note'); note = args[k + 1]; del args[k:k + 2]
name, spec = args[0], json.load(open(args[1], encoding='utf-8'))
ARMS = {'L': (1.5, 1, 1, 1.6, 150), 'L3': (1.5, 1, 1, 1, 150), 'W1': (1.5, 1.5, 1, 1.6, 120), 'W2': (1, 1, 0.6, 1.2, 120),
        'G2': (1, 1, 1, 1, 0, 2, 3), 'GW': (1, 1, 1, 1, 0, 1, 2), 'LG': (1.5, 1, 1, 1.6, 150, 2, 3), 'LW': (1.5, 1, 1, 1.6, 150, 1, 2), 'G3': (1, 1, 1, 1, 0, 3, 3), 'LG3': (1.5, 1, 1, 1.6, 150, 3, 3), 'GM': (1, 1, 1, 1, 0, 1, 30), 'GN': (1, 1, 1, 1, 0, 1, 12), 'WG': (1.5, 1.5, 1, 1.6, 120, 2, 3), 'HG': (1, 1, 0.6, 1.2, 120, 2, 3)}  # last two: gold weight before r300, gem weight
dst = 'bots/exp/' + name
if os.path.exists(dst):
    shutil.rmtree(dst)
shutil.copytree(base, dst, ignore=shutil.ignore_patterns('.cambc'))
sig = json.load(open('data/map_sigs.json', encoding='utf-8'))


def sub(path, a, b, cnt=1):
    s = open(path, encoding='utf-8', newline='').read()
    assert s.count(a) == cnt, (a, s.count(a))
    s = s.replace(a, b)
    open(path, 'w', encoding='utf-8', newline='').write(s)


rows = []
for m, arm in spec.items():
    s = sig.get(m) or sig.get(m.replace('-', '_')) or sig.get(m.replace('_', '-'))
    assert s, m
    a = ARMS[arm] + ((1, 3) if len(ARMS[arm]) == 5 else ())
    rows.append('    {%d, %d, %d, %d, %d, %d, %.2ff, %.2ff, %.2ff, %.2ff, %d, %.2ff, %.2ff},  // %s (%s)' % (s[0], s[1], s[2], s[3], s[4], s[5], a[0], a[1], a[2], a[3], a[4], a[5], a[6], m, arm))
src = dst + '/' + os.environ.get('SRC', 'src/cj') + '/'  # SRC=src for a bot without the router's folders
sub(src + 'world.h', '    bool central_altars = false;', '    // Per-map opening arm (kMapArms): before arm_r the pick weighs groups by these (rule_light.md, rule_arms.md).\n    int arm_r = 0;\n    float arm_light = 1.f, arm_wolf = 1.f, arm_heavy = 1.f, arm_enable = 1.f;\n    bool central_altars = false;')
sub(src + 'world.h', '    bool big = false;       // golem or monolith inside', '    bool big = false;       // golem or monolith inside\n    bool heavy = false;     // elk, golem or monolith inside')
sub(src + 'world.cpp', '            if (cp.type == camp_type::golem || cp.type == camp_type::monolith) g.big = true;', '            if (cp.type == camp_type::golem || cp.type == camp_type::monolith) g.big = true;\n            if (cp.type == camp_type::golem || cp.type == camp_type::monolith || cp.type == camp_type::elk) g.heavy = true;')
sub(src + 'world.cpp', """    camp_tiles->clear();
""", """    camp_tiles->clear();
    {
        struct MapArm { short w, h, walls, holes, altars, bushes; float light, wolf, heavy, enable; short r; float gold, gem; };
        static constexpr MapArm kMapArms[] = {
""" + '\n'.join(rows) + """
        };
        const int mw = map::width(), mh = map::height();
        const int mwalls = static_cast<int>(map::walls().count()), mholes = static_cast<int>(map::holes().count());
        const int maltars = static_cast<int>(map::altars().count()), mbushes = static_cast<int>(map::bushes().count());
        for (const MapArm& m : kMapArms)
            if (m.w == mw && m.h == mh && m.walls == mwalls && m.holes == mholes && m.altars == maltars && m.bushes == mbushes) {
                arm_r = m.r; arm_light = m.light; arm_wolf = m.wolf; arm_heavy = m.heavy; arm_enable = m.enable; arm_gold = m.gold; arm_gem = m.gem;
            }
    }
""")
f = src + 'farm.cpp'
sub(f, """    const float my_hp = me.health(), my_mhp = me.max_health();
    const float my_spare = std::max(0.f, my_hp - P_TANK_FLOOR * my_mhp);
    const bool on_mainland = W.on_main(p);""", """    const bool arm_on = round < W.arm_r;
    const float enable_w = arm_on ? W.arm_enable : P_ENABLE;
    const float my_hp = me.health(), my_mhp = me.max_health();
    const float my_spare = std::max(0.f, my_hp - P_TANK_FLOOR * my_mhp);
    const bool on_mainland = W.on_main(p);""")
sub(f, """        if (value <= 0) continue;
        if (g.side < -P_SIDE_MARGIN) value *= P_ENEMY_SIDE_W;  // their half: farmed and guarded by them""", """        if (value <= 0) continue;
        if (arm_on) value *= g.heavy ? W.arm_heavy : (g.dps > 0 ? W.arm_wolf : W.arm_light);
        if (g.side < -P_SIDE_MARGIN) value *= P_ENEMY_SIDE_W;  // their half: farmed and guarded by them""")
sub(f, """        if (value * P_ENABLE / (static_cast<float>(d) + 1.5f * wait + 3.f) <= best) continue;""", """        if (value * enable_w / (static_cast<float>(d) + 1.5f * wait + 3.f) <= best) continue;""")
sub(f, """        const float s = value * (enabler ? P_ENABLE : 1.f) / n_team / std::max(1.f, Ttot);""", """        const float s = value * (enabler ? enable_w : 1.f) / n_team / std::max(1.f, Ttot);""")
sub(src + 'world.h', '    int arm_r = 0;', '    int arm_r = 0;\n    float arm_gold = P_GOLD_W_EARLY, arm_gem = P_GEM_W;  // value weights of gold before r300 and of gems on this map')
fs = open(f, encoding='utf-8', newline='').read()
assert fs.count('P_GEM_W') >= 4 and fs.count('P_GOLD_W_EARLY') >= 4
fs = fs.replace('P_GEM_W', 'world().arm_gem').replace('P_GOLD_W_EARLY', 'world().arm_gold')
open(f, 'w', encoding='utf-8', newline='').write(fs)
open(dst + '/NOTE.txt', 'w').write((note or f'Map router: per-map opening arms on {len(spec)} maps') + '\n')
print('ok', dst, len(rows))
