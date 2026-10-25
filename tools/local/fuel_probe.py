"""Fuel per turn and per stage from a fuel-probe build: python -I tools/local/fuel_probe.py RUNDIR

Build the probe by copying a candidate to bots/exp/pfN and applying tools/local/fuel_probe.patch inside it
(`patch -p1 < ../../../tools/local/fuel_probe.patch`; the patch is against exp/fz1, so fix rejected hunks by hand),
build with --release and run multi.py --keep. The probe prints "PF s<slot> r<round> contact|quiet ..." lines every 250
rounds (contact = an enemy champion within 6, off its spawn). This reads the last complete line per champion per game
and prints, for contact and quiet turns: turns, turns that ran out of fuel (per 1000), mean and max fuel, turns over
60k and 80k, fuel by champions within 8, mean / max / count per stage, the stage running when a turn ran out, and
run-outs per map."""
import collections, glob, os, re, sys, zipfile
run = sys.argv[1]; side_of = {'A': 'a', 'B': 'b'}
TOT = {k: collections.Counter() for k in ('contact', 'quiet')}
ST = {k: collections.defaultdict(lambda: [0, 0, 0]) for k in ('contact', 'quiet')}   # sum of means*n, max, n
SP = {k: collections.Counter() for k in ('contact', 'quiet')}
CR = {k: collections.defaultdict(lambda: [0, 0, 0]) for k in ('contact', 'quiet')}
MAPS = collections.defaultdict(collections.Counter)
games = 0
for f in sorted(glob.glob(os.path.join(run, '*.repl26a'))):
    base = os.path.basename(f)
    cand_side = base.split('~')[-1].split('.')[0]          # our side: A means candidate is team A
    mp = base.split('~')[2]
    z = zipfile.ZipFile(f)
    names = [n for n in z.namelist() if n.endswith(f'team-{side_of[cand_side]}.stdout')]
    if not names: continue
    games += 1
    txt = z.read(names[0]).decode('latin1')
    last = {}
    for line in txt.split('\n'):
        m = re.match(r'PF s(\d) r(\d+) (contact|quiet) (.*)$', line.strip())
        if m and m.group(4).count(' |') == 2: last[(m.group(1), m.group(3))] = m.group(4)
    for (slot, kind), body in last.items():
        head, stages, spills = body.split(' |')
        kv = dict(re.findall(r'(\w+)=(\d+)', head.split(' crowd')[0]))
        n, sp = int(kv['n']), int(kv['spill'])
        TOT[kind]['n'] += n; TOT[kind]['spill'] += sp; TOT[kind]['o60'] += int(kv['o60']); TOT[kind]['o80'] += int(kv['o80'])
        TOT[kind]['sum'] += int(kv['mean']) * (n - sp); TOT[kind]['full'] += n - sp
        TOT[kind]['max'] = max(TOT[kind]['max'], int(kv['max']))
        MAPS[mp][kind + ' spill'] += sp; MAPS[mp][kind + ' n'] += n
        for b, cn, mean, mx in re.findall(r' (\d):(\d+)/(\d+)/(\d+)', head.split(' crowd')[1]):
            c = CR[kind][b]; c[0] += int(cn) * int(mean); c[1] = max(c[1], int(mx)); c[2] += int(cn)
        for name, mean, mx, cnt in re.findall(r' ([a-z ]+?)=(\d+)/(\d+)/(\d+)', stages):
            s = ST[kind][name.strip()]; s[0] += int(mean) * int(cnt); s[1] = max(s[1], int(mx)); s[2] += int(cnt)
        for name, cnt in re.findall(r' ([a-z ]+?)=(\d+)', spills.replace('spill_at', '')):
            SP[kind][name.strip()] += int(cnt)
print(f'{games} games')
for kind in ('contact', 'quiet'):
    T = TOT[kind]
    print(f'{kind}: turns {T["n"]}, ran out {T["spill"]} ({1000 * T["spill"] / max(1, T["n"]):.2f} per 1000), mean {T["sum"] / max(1, T["full"]):.0f}, max {T["max"]}, over 60k {T["o60"]}, over 80k {T["o80"]}')
    print('   by champions within 8 (0-2, 3-4, 5-6, 7+): ' + ', '.join(f'{b}: n {c[2]} mean {c[0] / max(1, c[2]):.0f} max {c[1]}' for b, c in sorted(CR[kind].items())))
    print('   stages (mean / max / turns): ' + ', '.join(f'{k} {v[0] / max(1, v[2]):.0f}/{v[1]}/{v[2]}' for k, v in sorted(ST[kind].items(), key=lambda x: -x[1][0])))
    print('   ran out in stage: ' + ', '.join(f'{k} {v}' for k, v in SP[kind].most_common()))
print('ran out per map (contact / quiet): ' + ', '.join(f'{m} {c["contact spill"]}/{c["quiet spill"]}' for m, c in sorted(MAPS.items())))
