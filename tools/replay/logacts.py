"""Our bot's own action labels near an enemy, from the logs inside platform replays: python -I tools/replay/logacts.py RUN_DIR_NAME [--round R] [--upto D] [--type NAME]

RUN_DIR_NAME is a folder name under data/fights/ and data/replays/platform/ (e.g. t1503_tm_t03); the bot must log with BOT_LOGC=1 (lines "round idx act p>q hp g t e" in team-a.stdout). Each log line is
joined to the decoded round by position. For champion-rounds with the nearest enemy champion within D (default 3), to round R (default 1000): per label its count and share, and what the
champion did that round (hit a champion, hit a camp, closer, away, other move, still). Labels ending in +A hit something. Also prints the first round each team's champions moved.
"""
import collections, gzip, json, os, re, sys, zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import decoded as D

D.SKIP = []
args = sys.argv[1:]
R, U, TY = 1000, 3, None
if '--round' in args:
    k = args.index('--round'); R = int(args[k + 1]); del args[k:k + 2]
if '--upto' in args:
    k = args.index('--upto'); U = int(args[k + 1]); del args[k:k + 2]
if '--type' in args:
    k = args.index('--type'); TY = args[k + 1]; del args[k:k + 2]
run = args[0]
fd = os.path.join('data', 'fights', run)
rd = os.path.join('data', 'replays', 'platform', run)
LINE = re.compile(r'^(\d+) (\d+) ([A-Za-z_?:+0-9]+) (\d+),(\d+)>(\d+),(\d+) ')
T = collections.defaultdict(collections.Counter)
first = {'us': [], 'them': []}
joined = lost = 0
side = {}
for l in open(os.path.join(fd, 'index.txt'), encoding='utf-8', errors='replace'):
    p = l.split()
    if len(p) >= 4:
        side[p[0]] = 0 if p[2] == 'a' else 1
for mid, us in side.items():
    f = os.path.join(fd, mid + '.jsonl.gz')
    z = os.path.join(rd, mid + '.repl26a')
    if not (os.path.exists(f) and os.path.exists(z)):
        continue
    lines = [json.loads(x) for x in gzip.open(f, 'rt')]
    rows = [r for r in lines[1:] if r.get('c')]
    if not rows:
        continue
    start = {}
    seen = {}
    for r in rows:
        for i, c in enumerate(r['c']):
            if c.get('a') and 'x' in c:
                pos = (c['x'], c['y'])
                if i not in start:
                    start[i] = pos
                elif i not in seen and pos != start[i]:
                    seen[i] = r['r']
        if r['r'] > 40:
            break
    for i, v in seen.items():
        first['us' if rows[0]['c'][i]['t'] == us else 'them'].append(v)
    by = {r['r']: r for r in rows}
    n = len(rows[0]['c'])
    try:
        text = zipfile.ZipFile(z).read('team-a.stdout').decode('latin1').replace('\x00', '')
    except KeyError:
        continue
    for line in text.split('\n'):
        m = LINE.match(line)
        if not m:
            continue
        rn, idx, act = int(m.group(1)), int(m.group(2)), m.group(3)
        if rn > R or rn not in by:
            continue
        p = (int(m.group(4)), int(m.group(5)))
        q = (int(m.group(6)), int(m.group(7)))
        a = by[rn]
        al = [(i, c) for i, c in enumerate(a['c']) if c.get('a') and 'x' in c]
        me = [(i, c) for i, c in al if c['t'] == us and (c['x'], c['y']) == q]
        if not me:
            me = [(i, c) for i, c in al if c['t'] == us and (c['x'], c['y']) == p]
        if not me:
            lost += 1
            continue
        joined += 1
        i, c = me[0]
        if TY and not D.NAMES[c['ty']].startswith(TY):
            continue
        es = [(D.dist(p, (o['x'], o['y'])), j) for j, o in al if o['t'] != us]
        if not es:
            continue
        d, j = min(es)
        if d > U:
            continue
        jc = a['c'][j]
        dd = D.dist(q, (jc['x'], jc['y'])) - d
        kind = 'hitc' if D.enemy_hits(a, i, n) else 'camp' if D.camp_hits(a, i) else 'closer' if dd < 0 else 'away' if dd > 0 else 'moved' if q != p else 'still'
        T[act][kind] += 1
        T[act]['n'] += 1
        T['ALL'][kind] += 1
        T['ALL']['n'] += 1
print(f'joined {joined} lines, not joined {lost}')
for k in ('us', 'them'):
    v = sorted(first[k])
    if v:
        print(f'first move, {k}: mean r{sum(v) / len(v):.2f} median r{v[len(v) // 2]} | share by r2 {sum(x <= 2 for x in v) / len(v):.2f} r3 {sum(x <= 3 for x in v) / len(v):.2f} r4 {sum(x <= 4 for x in v) / len(v):.2f}')
tot = T['ALL']['n'] or 1
print(f'enemy within {U}, to r{R}{" " + TY if TY else ""}: label | n share | hitc camp closer away moved still')
for act, c in sorted(T.items(), key=lambda kv: -kv[1]['n'])[:40]:
    m = c['n'] or 1
    print(f'{act:18} {c["n"]:6} {c["n"] / tot:.3f} | ' + ' '.join(f'{c[k] / m:.2f}' for k in ('hitc', 'camp', 'closer', 'away', 'moved', 'still')))
