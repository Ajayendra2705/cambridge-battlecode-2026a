"""Add vvk1's Vesper rules (vvg1 harmless gold first before r200, vvj3 capture rule before r300) to a router's v1503 part: python -I mk_ves.py bots/exp/NAME "note" """
import sys
dst, note = sys.argv[1], sys.argv[2]
src = dst + '/src/cj/'


def sub(path, a, b, cnt=1):
    s = open(path, encoding='utf-8', newline='').read()
    assert s.count(a) == cnt, (a, s.count(a))
    s = s.replace(a, b)
    open(path, 'w', encoding='utf-8', newline='').write(s)


p = src + 'params.h'
s = open(p, encoding='utf-8', newline='').read()
s = s.rstrip('\n') + """

#ifndef P_VES_LIGHT_W
#define P_VES_LIGHT_W 2.0f     // Vesper before P_VES_LIGHT_R: a harmless group with gold counts this many times in her pick (vvg1)
#endif
#ifndef P_VES_LIGHT_R
#define P_VES_LIGHT_R 200
#endif
#ifndef P_VJ_R
#define P_VJ_R 300          // before this round her capture weight beats a hurt ally's on gold groups and she does not leave them to Marcella (vvj3)
#endif
"""
open(p, 'w', encoding='utf-8', newline='').write(s)
f = src + 'farm.cpp'
sub(f, """        if (arm_on) value *= g.heavy ? W.arm_heavy : (g.dps > 0 ? W.arm_wolf : W.arm_light);""", """        if (arm_on) value *= g.heavy ? W.arm_heavy : (g.dps > 0 ? W.arm_wolf : W.arm_light);
        if (ctype == champion_type::vesper_vale && round < P_VES_LIGHT_R && g.dps <= 0 && g.gold > 0) value *= P_VES_LIGHT_W;""")
sub(f, """static float capture_bonus(champion_type t, const Group& g) {
    if (P_CAPTURE_MODE == 0) {""", """static int cb_round = 0;
static float capture_bonus(champion_type t, const Group& g) {
    if (t == champion_type::vesper_vale && cb_round < P_VJ_R && g.gold > 0) return 2000.f + static_cast<float>(g.gold);
    if (P_CAPTURE_MODE == 0) {""")
sub(f, """bool Bot::capture(Group& g) {
    World& W = world();""", """bool Bot::capture(Group& g) {
    cb_round = round;
    World& W = world();""")
sub(f, """            if (P_MAR_ROUTE > 0.f && ctype != champion_type::marcella && g.gems >= 10 &&""",
    """            if (P_MAR_ROUTE > 0.f && ctype != champion_type::marcella && !(ctype == champion_type::vesper_vale && round < P_VJ_R && g.gold > 0) && g.gems >= 10 &&""")
open(dst + '/NOTE.txt', 'w').write(note + '\n')
print('ok', dst)
