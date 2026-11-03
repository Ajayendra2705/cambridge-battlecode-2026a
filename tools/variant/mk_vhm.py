"""Siege from the spawn tiles: monoliths in reach of our spawn are hit from the first rounds: python -I tools/variant/mk_vhm.py NAME [FROM] [BASE] [SRC]

On 03homonoliths three monoliths (600 gems, 900 gold) touch each spawn corner, and a spawn tile heals fully every round, so the monoliths' 200 a round does not matter. The bot waits for r400 and
3000 health (r900 without) as on any heavy map. Here the siege starts at FROM (default 8) on a map with a monolith within 3 tiles of our spawn. Rebuilt from the note of teammate's upload 1523.
"""
import os, shutil, sys
name = sys.argv[1]
frm = int(sys.argv[2]) if len(sys.argv) > 2 else 8
base = sys.argv[3] if len(sys.argv) > 3 else 'bots/exp/vnl1'
src = sys.argv[4] if len(sys.argv) > 4 else 'src'
dst = 'bots/exp/' + name
if os.path.exists(dst):
    shutil.rmtree(dst)
shutil.copytree(base, dst, ignore=shutil.ignore_patterns('.cambc'))


def patch(path, pairs):
    f = f'{dst}/{src}/{path}'
    s = open(f, encoding='utf-8', newline='').read()
    for a, b in pairs:
        assert s.count(a) == 1, a
        s = s.replace(a, b)
    open(f, 'w', encoding='utf-8', newline='').write(s)


patch('params.h', [('#ifndef P_SIEGE_FROM', f'#ifndef P_SPAWN_SIEGE_FROM\n#define P_SPAWN_SIEGE_FROM {frm}\n#endif\n#ifndef P_SIEGE_FROM')])
patch('farm.cpp', [
    ("""    int r = comms.rally();
    if (r >= static_cast<int>(W.groups.size())) r = -1;
""", """    // A monolith in reach of our spawn tiles: a spawn tile heals fully every round, so the siege needs no health and never stalls.
    static int spawn_mono = -1;
    if (spawn_mono < 0) {
        spawn_mono = 0;
        if (W.my_spawn)
            for (const auto& g : W.groups) {
                if (!g.monolith || g.gems <= 0) continue;
                for (const auto& c : g.camps)
                    for (vec2 q : W.my_spawn->positions())
                        if (cheb(q, c.pos) <= 3) spawn_mono = 1;
            }
    }
    int r = comms.rally();
    if (r >= static_cast<int>(W.groups.size())) r = -1;
"""),
    ("if (leader() && round - rally_since > (is_gate_group(r) ? P_SIEGE_MAX : P_RALLY_MAX)) {", "if (leader() && spawn_mono != 1 && round - rally_since > (is_gate_group(r) ? P_SIEGE_MAX : P_RALLY_MAX)) {"),
    ("if ((dead >= P_SIEGE_DEATHS || stalled) && !W.gated) {", "if ((dead >= P_SIEGE_DEATHS || stalled) && !W.gated && spawn_mono != 1) {"),
    ("""    const bool siege_ok = (W.gated || W.heavy_map) ? (round""", """    const bool siege_ok = (spawn_mono == 1 && round >= P_SPAWN_SIEGE_FROM) || ((W.gated || W.heavy_map) ? (round"""),
    ("(self().max_health() >= P_MONO_HP || round >= P_SIEGE_LATE));", "(self().max_health() >= P_MONO_HP || round >= P_SIEGE_LATE)));"),
])
print('ok', name, frm)
