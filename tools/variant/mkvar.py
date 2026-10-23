"""Clone bots/BASE into bots/NAME with exact text substitutions: python -I tools/variant/mkvar.py BASE NAME [FILE OLD NEW]...

Each substitution must match exactly once. The build cache is not copied.
"""
import os, shutil, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
base, name, subs = sys.argv[1], sys.argv[2], sys.argv[3:]
dst = os.path.join(ROOT, 'bots', name)
shutil.rmtree(dst, ignore_errors=True)
shutil.copytree(os.path.join(ROOT, 'bots', base), dst, ignore=shutil.ignore_patterns('.cambc'))
for i in range(0, len(subs), 3):
    path = os.path.join(dst, 'src', subs[i])
    s = open(path, encoding='utf-8', newline='').read()
    assert s.count(subs[i + 1]) == 1, f'{subs[i + 1]!r} matches {s.count(subs[i + 1])} times in {subs[i]}'
    open(path, 'w', encoding='utf-8', newline='').write(s.replace(subs[i + 1], subs[i + 2]))
print('made', name)
