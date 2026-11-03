"""Fuel limits scaled, on the no-log v1503: python -I mk_vfg.py NAME SCALE [BASE] [SRC]. Every gate of the form fuel() < N or fuel() > N and the fuel parameters are scaled, except the setup gate."""
import glob, os, re, shutil, sys
name, scale = sys.argv[1], float(sys.argv[2])
base = sys.argv[3] if len(sys.argv) > 3 else 'bots/exp/vnl1'
srcd = sys.argv[4] if len(sys.argv) > 4 else 'src'
dst = 'bots/exp/' + name
if os.path.exists(dst):
    shutil.rmtree(dst)
shutil.copytree(base, dst, ignore=shutil.ignore_patterns('.cambc'))
n = 0
for f in glob.glob(dst + '/' + srcd + '/*.cpp') + glob.glob(dst + '/' + srcd + '/*.h'):
    s = open(f, encoding='utf-8', newline='').read()
    def rep(m):
        global n
        v = int(m.group(2))
        if v == 120000:
            return m.group(0)
        n += 1
        return 'fuel() %s %d' % (m.group(1), int(v * scale))
    t = re.sub(r'fuel\(\) ([<>]) (\d+)', rep, s)
    t = re.sub(r'W\.precompute\((\d+),', lambda m: 'W.precompute(%d,' % int(int(m.group(1)) * scale), t)
    t = re.sub(r'(#define P_CT_FUEL )(\d+)', lambda m: m.group(1) + str(int(int(m.group(2)) * scale)), t)
    t = re.sub(r'(#define P_WARD_MIN_FUEL )(\d+)', lambda m: m.group(1) + str(int(int(m.group(2)) * scale)), t)
    t = re.sub(r'(#define P_ESC_MIN_FUEL )(\d+)', lambda m: m.group(1) + str(int(int(m.group(2)) * scale)), t)
    if t != s:
        open(f, 'w', encoding='utf-8', newline='').write(t)
open(dst + '/NOTE.txt', 'w').write(f'Fuel: decision fuel limits x{scale} (fewer skipped path and task searches)\n')
print('ok', dst, n)
