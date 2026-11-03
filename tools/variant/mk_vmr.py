"""Marcella next to a target uses the attack reset (a second hit that stuns) before the nuke: python -I mk_vmr.py NAME [BASE]"""
import os, shutil, sys
name = sys.argv[1]
base = sys.argv[2] if len(sys.argv) > 2 else 'bots/exp/vnl1'
dst = 'bots/exp/' + name
if os.path.exists(dst):
    shutil.rmtree(dst)
shutil.copytree(base, dst, ignore=shutil.ignore_patterns('.cambc'))
f = dst + '/src/fight.cpp'
s = open(f, encoding='utf-8', newline='').read()
a = """            if (abs[s].cooldown() > 0) continue;
            if ((k == ability_kind::damage || k == ability_kind::cc) && d <= static_cast<int>(arange[s])) {
                if (abs[s].use(e.c)) { cast_this_turn = true; return true; }"""
assert s.count(a) == 1
s = s.replace(a, """            if (abs[s].cooldown() > 0) continue;
            if (k == ability_kind::damage && d <= 1 && me.can_attack()) {
                // Next to the target with the basic hit still free: the hit and the reset come first (a second hit that stuns); the nuke waits.
                const int rs = ability_slot(ability_kind::attack_reset);
                if (rs >= 0 && abs[rs].cooldown() == 0) continue;
            }
            if ((k == ability_kind::damage || k == ability_kind::cc) && d <= static_cast<int>(arange[s])) {
                if (abs[s].use(e.c)) { cast_this_turn = true; return true; }""")
x = """        const int r = static_cast<int>(arange[s]);
        const Seen* best = nullptr;
        float bs = -1e9f;
        for (const auto* e : near) {
            if (round != e->seen_round || cheb(e->pos, p) > r) continue;
            float sc;"""
assert s.count(x) == 1
s = s.replace(x, """        if (k == ability_kind::damage && !kill_only && me.can_attack()) {
            // An enemy next to me, the basic hit free and the reset ready: hit and reset first (a second hit that stuns); the nuke waits a turn.
            const int rs = ability_slot(ability_kind::attack_reset);
            bool wait = false;
            try {
                if (rs >= 0 && abs[rs].cooldown() == 0)
                    for (const auto* e : near)
                        if (round == e->seen_round && cheb(e->pos, p) <= 1) wait = true;
            } catch (...) {}
            if (wait) continue;
        }
""" + x)
open(f, 'w', encoding='utf-8', newline='').write(s)
open(dst + '/NOTE.txt', 'w').write('Fight: Marcella next to a target uses hit + reset (stun) before the nuke\n')
print('ok', dst)
