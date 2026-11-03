"""Vesper values gold over gems in her pick, on the no-log v1503: python -I mk_vgv.py NAME R GEM_W GOLD_W [BASE]"""
import os, shutil, sys
name, r, gm, gd = sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4])
base = sys.argv[5] if len(sys.argv) > 5 else 'bots/exp/vnl1'
dst = 'bots/exp/' + name
if os.path.exists(dst):
    shutil.rmtree(dst)
shutil.copytree(base, dst, ignore=shutil.ignore_patterns('.cambc'))
def sub(path, x, y, cnt=1):
    s = open(path, encoding='utf-8', newline='').read()
    assert s.count(x) == cnt, (x, s.count(x))
    s = s.replace(x, y)
    open(path, 'w', encoding='utf-8', newline='').write(s)
p = dst + '/src/params.h'
s = open(p, encoding='utf-8', newline='').read()
s = s.rstrip('\n') + f"""

#ifndef P_VG_R
#define P_VG_R {r}      // before this round Vesper's pick weighs gems P_VG_GEM and gold P_VG_GOLD (rivals' Vesper takes groups without gold in 9% of her first captures, ours 21%)
#endif
#ifndef P_VG_GEM
#define P_VG_GEM {gm}f
#endif
#ifndef P_VG_GOLD
#define P_VG_GOLD {gd}f
#endif
"""
open(p, 'w', encoding='utf-8', newline='').write(s)
f = dst + '/src/farm.cpp'
sub(f, """        float value = static_cast<float>(g.gems) * P_GEM_W + static_cast<float>(g.gold) * gold_w;
        // Marcella earns""", """        float value = static_cast<float>(g.gems) * P_GEM_W + static_cast<float>(g.gold) * gold_w;
        if (ctype == champion_type::vesper_vale && round < P_VG_R) value = static_cast<float>(g.gems) * P_VG_GEM + static_cast<float>(g.gold) * P_VG_GOLD;
        // Marcella earns""")
open(dst + '/NOTE.txt', 'w').write(f'Economy: Vesper values gold over gems before r{r}\n')
print('ok', dst)
