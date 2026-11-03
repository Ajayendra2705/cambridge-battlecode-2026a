import os, shutil

import sys
name = sys.argv[1]
src = sys.argv[2] if len(sys.argv) > 2 else 'bots/exp/vnl1'
dst = 'bots/exp/' + name
if os.path.exists(dst):
    shutil.rmtree(dst)
shutil.copytree(src, dst, ignore=shutil.ignore_patterns('.cambc'))


def sub(path, a, b):
    s = open(path, encoding='utf-8', newline='').read()
    assert s.count(a) == 1, (a, s.count(a))
    s = s.replace(a, b)
    open(path, 'w', encoding='utf-8', newline='').write(s)


f = dst + '/src/fight.cpp'
s = open(f, encoding='utf-8', newline='').read()
i = s.index('struct SimUnit {')
pass
# The pair dies together: a unit of a linked pair that falls takes its partner with it.
sub(f, 'void apply_damage(std::vector<SimUnit>& v, float dmg) {\n    // Focus fire: the weakest unit first, overflow to the next.\n    std::size_t i = 0;\n    while (dmg > 0 && i < v.size()) {\n        if (v[i].hp <= 0) { ++i; continue; }\n        const float d = std::min(dmg, v[i].hp);\n        v[i].hp -= d;\n        dmg -= d;\n        if (v[i].hp <= 0) ++i;\n    }\n}',
    'void apply_damage(std::vector<SimUnit>& v, float dmg) {\n    // Focus fire: the weakest unit first, overflow to the next.\n    std::size_t i = 0;\n    while (dmg > 0 && i < v.size()) {\n        if (v[i].hp <= 0) { ++i; continue; }\n        const float d = std::min(dmg, v[i].hp);\n        v[i].hp -= d;\n        dmg -= d;\n        if (v[i].hp <= 0) {\n            // Cassi and Issac die together.\n            if (v[i].linked) for (auto& o : v) if (o.linked) o.hp = 0;\n            ++i;\n        }\n    }\n}')
sub(f, '        u.burst = champ_burst(e->type, e->str, e->foc);\n        int d = cheb(e->pos, p);\n        if (P_SIM_SYM) {',
    '        u.burst = champ_burst(e->type, e->str, e->foc);\n        u.linked = e->type == champion_type::cassi || e->type == champion_type::issac;\n        int d = cheb(e->pos, p);\n        if (P_SIM_SYM) {')
sub(f, '            u.burst = champ_burst(m.s->type, m.s->str, m.s->foc);\n            u.delay = approach_delay(d, m.s->range) + 1;',
    '            u.burst = champ_burst(m.s->type, m.s->str, m.s->foc);\n            u.linked = m.s->type == champion_type::cassi || m.s->type == champion_type::issac;\n            u.delay = approach_delay(d, m.s->range) + 1;')
# Target: the pair is worth two bodies, and Cassi is the cheap way to kill it.
sub(f, '        if (e->channeling) sc -= 300.f;\n        sc -= static_cast<float>(e->gems) * 4.f;\n        if (d <= range) sc -= 150.f;\n        if (sc < bscore) { bscore = sc; tgt = e; }',
    '        if (e->channeling) sc -= 300.f;\n        sc -= static_cast<float>(e->gems) * 4.f;\n        if (d <= range) sc -= 150.f;\n        if (e->type == champion_type::cassi) sc -= 200.f;       // either death kills both: Cassi is the cheap way\n        else if (e->type == champion_type::issac) sc -= 100.f;\n        if (sc < bscore) { bscore = sc; tgt = e; }')
open(dst + '/NOTE.txt', 'w').write('Fight: Cassi and Issac die together, sim and target know it (Cassi first)\n')
print('ok')
