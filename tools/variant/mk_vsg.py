"""Gated altars: the team starts the siege of the gate camps later: python -I tools/variant/mk_vsg.py NAME FROM [BASE] [SRC]

On a gated altar map (01boss_battle: the only altar sits behind two monoliths) the bot calls the whole team to the guards from r400. Ranked games show that a team breaking them early
stands at the altar poorer than its rival (gold 4600 against 8000 when they fell before r520), while a break at r843 found us ahead. FROM replaces P_SIEGE_FROM on gated maps only.
"""
import os, shutil, sys
name, frm = sys.argv[1], int(sys.argv[2])
base = sys.argv[3] if len(sys.argv) > 3 else 'bots/exp/vnl1'
src = sys.argv[4] if len(sys.argv) > 4 else 'src'
dst = 'bots/exp/' + name
if os.path.exists(dst):
    shutil.rmtree(dst)
shutil.copytree(base, dst, ignore=shutil.ignore_patterns('.cambc'))
f = f'{dst}/{src}/farm.cpp'
s = open(f, encoding='utf-8', newline='').read()
a = "(W.gated || W.heavy_map) ? (round >= P_SIEGE_FROM && "
assert s.count(a) == 1
s = s.replace(a, "(W.gated || W.heavy_map) ? (round >= (W.gated ? P_GATE_FROM : P_SIEGE_FROM) && ")
open(f, 'w', encoding='utf-8', newline='').write(s)
f = f'{dst}/{src}/params.h'
s = open(f, encoding='utf-8', newline='').read()
a = '#ifndef P_SIEGE_FROM'
assert s.count(a) == 1
s = s.replace(a, f'#ifndef P_GATE_FROM\n#define P_GATE_FROM {frm}\n#endif\n' + a)
open(f, 'w', encoding='utf-8', newline='').write(s)
print('ok', name, frm)
