"""Per-map draft table in a router's v1503 arm: python -I mk_dr.py NAME SPEC.json [--base bots/exp/rt3] [--src src/cj] [--note TEXT]

SPEC maps a map name to a list of picks, as named in cambc::champion_draft, for example {"03one_gem": ["heart_of_ruin", "marcella", "vendetta", "vesper_vale", "tavi"]}.
The list replaces the team's draft order on that map when the team size equals its length. Signatures come from data/map_sigs.json.
"""
import json, os, shutil, sys
args = sys.argv[1:]
name, specf = args[0], args[1]
base = args[args.index('--base') + 1] if '--base' in args else 'bots/exp/rt3'
srcd = args[args.index('--src') + 1] if '--src' in args else 'src/cj'
note = args[args.index('--note') + 1] if '--note' in args else None
dst = 'bots/exp/' + name
if base != dst:
    if os.path.exists(dst):
        shutil.rmtree(dst)
    shutil.copytree(base, dst, ignore=shutil.ignore_patterns('.cambc'))
spec = json.load(open(specf, encoding='utf-8'))
sig = json.load(open('data/map_sigs.json', encoding='utf-8'))
rows = []
for m, picks in spec.items():
    s = sig.get(m.replace('-', '_'))
    assert s, m
    ps = list(picks) + [picks[-1]] * (5 - len(picks))
    rows.append('        {%d, %d, %d, %d, %d, %d, %d, { %s }},  // %s' % (s[0], s[1], s[2], s[3], s[4], s[5], len(picks), ', '.join('D::' + p for p in ps), m))
f = dst + '/' + srcd + '/draft.cpp'
s = open(f, encoding='utf-8', newline='').read()
a = "    const std::size_t k = mine.size();"
assert s.count(a) == 1
s = s.replace(a, """    {
        // Per-map draft table (results/analysis/rule_draftarms.md).
        struct DraftArm { short w, h, walls, holes, altars, bushes, n; D picks[5]; };
        static const DraftArm kDraftArms[] = {
""" + '\n'.join(rows) + """
        };
        const int mw = cambc::map::width(), mh = cambc::map::height();
        const int mwalls = static_cast<int>(cambc::map::walls().count()), mholes = static_cast<int>(cambc::map::holes().count());
        const int maltars = static_cast<int>(cambc::map::altars().count()), mbushes = static_cast<int>(cambc::map::bushes().count());
        for (const DraftArm& m : kDraftArms)
            if (m.w == mw && m.h == mh && m.walls == mwalls && m.holes == mholes && m.altars == maltars && m.bushes == mbushes && static_cast<unsigned>(m.n) == n)
                order.assign(m.picks, m.picks + m.n);
    }
""" + a)
open(f, 'w', encoding='utf-8', newline='').write(s)
open(dst + '/NOTE.txt', 'w').write((note or f'Map router: draft table on {len(spec)} maps') + '\n')
print('ok', dst, len(rows))
