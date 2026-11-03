"""A variant of exp/vnl1 with changed constants: python -I mkp.py NAME "NOTE" P_X=V ... [--base bots/exp/x]"""
import os, re, shutil, sys
args = sys.argv[1:]
base = 'bots/exp/vnl1'
if '--base' in args:
    k = args.index('--base'); base = args[k + 1]; del args[k:k + 2]
name, note, sets = args[0], args[1], args[2:]
dst = 'bots/exp/' + name
if os.path.exists(dst):
    shutil.rmtree(dst)
shutil.copytree(base, dst, ignore=shutil.ignore_patterns('.cambc'))
p = dst + '/src/params.h'
s = open(p, encoding='utf-8', newline='').read()
for kv in sets:
    k, v = kv.split('=')
    s, n = re.subn(r'(#define ' + k + r'\s+)\S+', lambda m: m.group(1) + v, s, count=1)
    assert n == 1, k
open(p, 'w', encoding='utf-8', newline='').write(s)
open(dst + '/NOTE.txt', 'w').write(note + '\n')
print('ok', dst, sets)
