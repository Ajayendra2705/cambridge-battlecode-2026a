"""rt8: rt5's light arms, the arms that held on platform and local samples, Vesper's vvk1 rules and the pair-aware fight. Run after mk_rt.py and mk_vbk2.py on NAME."""
import os, sys
name = sys.argv[1]
d = 'bots/exp/' + name + '/' + os.environ.get('SRC', 'src/cj') + '/'


def sub(path, a, b, cnt=1):
    s = open(path, encoding='utf-8', newline='').read()
    assert s.count(a) == cnt, (a, s.count(a))
    s = s.replace(a, b)
    open(path, 'w', encoding='utf-8', newline='').write(s)


# Book weight, after the value check (mk_vbk2's last anchor differs after mk_rt), and vvg1 in her pick.
sub(d + 'farm.cpp', '        if (value <= 0) continue;\n', '        if (value <= 0) continue;\n        if (round < P_BOOK_R) value *= g.book_w;\n        if (ctype == champion_type::vesper_vale && round < P_VES_LIGHT_R && g.dps <= 0 && g.gold > 0) value *= P_VES_LIGHT_W;\n')
# vvj3: her capture weight before P_VJ_R.
s = open(d + 'farm.cpp', encoding='utf-8', newline='').read()
a = 'static float capture_bonus(champion_type t, const Group& g) {\n'
assert s.count(a) == 1
s = s.replace(a, 'static int cb_round = 0;\n' + a + '    if (t == champion_type::vesper_vale && cb_round < P_VJ_R && g.gold > 0) return 2000.f + static_cast<float>(g.gold);\n')
a = 'bool Bot::capture(Group& g) {\n'
assert s.count(a) == 1
s = s.replace(a, a + '    cb_round = round;\n')
a = 'if (P_MAR_ROUTE > 0.f && ctype != champion_type::marcella && g.gems >= 10 &&'
assert s.count(a) == 1
s = s.replace(a, 'if (P_MAR_ROUTE > 0.f && ctype != champion_type::marcella && !(ctype == champion_type::vesper_vale && round < P_VJ_R && g.gold > 0) && g.gems >= 10 &&')
open(d + 'farm.cpp', 'w', encoding='utf-8', newline='').write(s)
p = d + 'params.h'
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
# vpa1.
f = d + 'fight.cpp'
sub(f, '    int bdelay = -1;  // rounds before its ability burst can land (-1: with the first attack)\n};', '    int bdelay = -1;  // rounds before its ability burst can land (-1: with the first attack)\n    bool linked = false;  // Cassi or Issac: either death kills both\n};')
s = open(f, encoding='utf-8', newline='').read()
a = 'if (v[i].hp <= 0) ++i;'
assert s.count(a) >= 1  # one copy in v1503's apply_damage; 1523 adds a second in the simulation's fast path
s = s.replace(a, 'if (v[i].hp <= 0) {\n            // Cassi and Issac die together.\n            if (v[i].linked) for (auto& o : v) if (o.linked) o.hp = 0;\n            ++i;\n        }')
a = '        u.burst = champ_burst(e->type, e->str, e->foc);\n        int d = cheb(e->pos, p);'
assert s.count(a) == 1
s = s.replace(a, '        u.burst = champ_burst(e->type, e->str, e->foc);\n        u.linked = e->type == champion_type::cassi || e->type == champion_type::issac;\n        int d = cheb(e->pos, p);')
a = '            u.burst = champ_burst(m.s->type, m.s->str, m.s->foc);\n            u.delay = approach_delay(d, m.s->range) + 1;'
assert s.count(a) == 1
s = s.replace(a, '            u.burst = champ_burst(m.s->type, m.s->str, m.s->foc);\n            u.linked = m.s->type == champion_type::cassi || m.s->type == champion_type::issac;\n            u.delay = approach_delay(d, m.s->range) + 1;')
a = '        if (d <= range) sc -= 150.f;\n        if (sc < bscore) { bscore = sc; tgt = e; }'
assert s.count(a) == 1
s = s.replace(a, '        if (d <= range) sc -= 150.f;\n        if (e->type == champion_type::cassi) sc -= 200.f;       // either death kills both: Cassi is the cheap way\n        else if (e->type == champion_type::issac) sc -= 100.f;\n        if (sc < bscore) { bscore = sc; tgt = e; }')
open(f, 'w', encoding='utf-8', newline='').write(s)
open('bots/exp/' + name + '/NOTE.txt', 'w').write('Map router: light camps on 5 maps, gold first on 2, book on 2, gems first on 03one_gem + Vesper takes gold + fights know Cassi and Issac die together\n')
print('ok', name)
