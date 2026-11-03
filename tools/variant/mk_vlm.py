"""Light camps first on chosen maps only, on the no-log v1503: python -I mk_vlm.py NAME LIGHT_W ENABLE_EARLY R MAP1,MAP2,..."""
import json, os, shutil, sys

name, lw, en, r, maps = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5].split(',')
dst = 'bots/exp/' + name
if os.path.exists(dst):
    shutil.rmtree(dst)
shutil.copytree('bots/exp/vnl1', dst, ignore=shutil.ignore_patterns('.cambc'))
sig = json.load(open('data/map_sigs.json', encoding='utf-8'))


def sub(path, a, b, cnt=1):
    s = open(path, encoding='utf-8', newline='').read()
    assert s.count(a) == cnt, (a, s.count(a))
    s = s.replace(a, b)
    open(path, 'w', encoding='utf-8', newline='').write(s)


rows = []
for m in maps:
    s = sig.get(m.replace('-', '_'))
    assert s, m
    rows.append('    {%d, %d, %d, %d, %d, %d},  // %s' % (s[0], s[1], s[2], s[3], s[4], s[5], m))
p = dst + '/src/params.h'
s = open(p, encoding='utf-8', newline='').read()
s = s.rstrip('\n') + f"""

#ifndef P_LIGHT_W
#define P_LIGHT_W {lw}f        // on the maps of kLightMaps, before P_LIGHT_R a harmless group (clusters only) counts this many times in a champion's pick
#endif
#ifndef P_ENABLE_EARLY
#define P_ENABLE_EARLY {en}f   // P_ENABLE before P_LIGHT_R on those maps
#endif
#ifndef P_LIGHT_R
#define P_LIGHT_R {r}
#endif
"""
open(p, 'w', encoding='utf-8', newline='').write(s)
sub(dst + '/src/world.h', '    bool central_altars = false;', '    bool light_map = false;               // kLightMaps: light camps first in the opening\n    bool central_altars = false;')
f = dst + '/src/world.cpp'
sub(f, """    camp_tiles->clear();
    auto api_groups = map::camp_groups();""", """    camp_tiles->clear();
    {
        struct MapSig { short w, h, walls, holes, altars, bushes; };
        static constexpr MapSig kLightMaps[] = {
""" + '\n'.join(rows) + """
        };
        const int mw = map::width(), mh = map::height();
        const int mwalls = static_cast<int>(map::walls().count()), mholes = static_cast<int>(map::holes().count());
        const int maltars = static_cast<int>(map::altars().count()), mbushes = static_cast<int>(map::bushes().count());
        for (const MapSig& m : kLightMaps)
            if (m.w == mw && m.h == mh && m.walls == mwalls && m.holes == mholes && m.altars == maltars && m.bushes == mbushes) light_map = true;
    }
    auto api_groups = map::camp_groups();""")
f = dst + '/src/farm.cpp'
sub(f, """    const float my_hp = me.health(), my_mhp = me.max_health();
    const float my_spare = std::max(0.f, my_hp - P_TANK_FLOOR * my_mhp);
    const bool on_mainland = W.on_main(p);""", """    const bool light_first = W.light_map && round < P_LIGHT_R;
    const float enable_w = light_first ? P_ENABLE_EARLY : P_ENABLE;
    const float my_hp = me.health(), my_mhp = me.max_health();
    const float my_spare = std::max(0.f, my_hp - P_TANK_FLOOR * my_mhp);
    const bool on_mainland = W.on_main(p);""")
sub(f, """        if (value <= 0) continue;
        if (g.side < -P_SIDE_MARGIN) value *= P_ENEMY_SIDE_W;  // their half: farmed and guarded by them""", """        if (value <= 0) continue;
        if (light_first && g.dps <= 0) value *= P_LIGHT_W;
        if (g.side < -P_SIDE_MARGIN) value *= P_ENEMY_SIDE_W;  // their half: farmed and guarded by them""")
sub(f, """        if (value * P_ENABLE / (static_cast<float>(d) + 1.5f * wait + 3.f) <= best) continue;""", """        if (value * enable_w / (static_cast<float>(d) + 1.5f * wait + 3.f) <= best) continue;""")
sub(f, """        const float s = value * (enabler ? P_ENABLE : 1.f) / n_team / std::max(1.f, Ttot);""", """        const float s = value * (enabler ? enable_w : 1.f) / n_team / std::max(1.f, Ttot);""")
open(dst + '/NOTE.txt', 'w').write(f'Map arm: light camps first before r{r} on {len(maps)} elk and low-gem maps\n')
print('ok', dst, len(maps))
