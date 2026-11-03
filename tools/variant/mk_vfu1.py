"""Setup gate lowered, on the no-log v1503: python -I mk_vfu1.py NAME GATE [BASE]"""
import os, shutil, sys
name, gate = sys.argv[1], sys.argv[2]
base = sys.argv[3] if len(sys.argv) > 3 else 'bots/exp/vnl1'
dst = 'bots/exp/' + name
if os.path.exists(dst):
    shutil.rmtree(dst)
shutil.copytree(base, dst, ignore=shutil.ignore_patterns('.cambc'))
p = dst + '/src/bot.cpp'
s = open(p, encoding='utf-8', newline='').read()
a = 'if (fuel() < 120000) return;  // big maps: finish setup, act next turn'
assert s.count(a) == 1
s = s.replace(a, f'if (fuel() < {gate}) return;  // big maps: setup ran out, act on the next turn')
open(p, 'w', encoding='utf-8', newline='').write(s)
open(dst + '/NOTE.txt', 'w').write('Fuel: act on the turn the setup ends (first move up to 1 round earlier on big maps)\n')
print('ok', dst)
