"""Another pick at one team size, on the no-log v1503: python -I mk_dz.py NAME SIZE c1,c2,...  (champion names as in cambc::champion_draft)."""
import os, shutil, sys
name, size, picks = sys.argv[1], int(sys.argv[2]), sys.argv[3].split(',')
dst = 'bots/exp/' + name
if os.path.exists(dst):
    shutil.rmtree(dst)
shutil.copytree('bots/exp/vnl1', dst, ignore=shutil.ignore_patterns('.cambc'))
f = dst + '/src/draft.cpp'
s = open(f, encoding='utf-8', newline='').read()
a = "    const std::size_t k = mine.size();"
assert s.count(a) == 1
s = s.replace(a, "    if (n == %d) order = { %s };\n" % (size, ', '.join('D::' + p for p in picks)) + a)
open(f, 'w', encoding='utf-8', newline='').write(s)
open(dst + '/NOTE.txt', 'w').write(f'Draft at {size} picks: {" ".join(picks)}\n')
print('ok', dst)
