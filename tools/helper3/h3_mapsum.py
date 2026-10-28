"""One-screen summary of decoded games of one map, us vs them (h3, 10-28).

usage: python -I tools/helper3/h3_mapsum.py DIR [DIR ...] [--rounds 300,1000]

Per side and game, to each round R: gems collected (a champion's bag rises while alive, as `decoded.py gems`), the part
of it taken from kills (the bag rose in a round where the champion's kill count rose), tributed, lost on death (bag at
death) and deaths. Also the round of the side's first gem gain without a kill ("first capture"), its first tribute and
the game's final tributed totals. Per-game lines carry the opponent and the bot version that was live when the game was
created, from meta.tsv in data/replays/platform/<DIR name>/ (tools/helper3/h3_qmaps.py), when present.
"""
import collections, os, statistics, sys

sys.path.insert(0, os.path.join(os.getcwd(), 'tools', 'replay'))
import decoded as D

args = sys.argv[1:]
RS = [300, 1000]
if '--rounds' in args:
    i = args.index('--rounds'); RS = [int(x) for x in args[i + 1].split(',')]; del args[i:i + 2]
meta = {}
for d in args:
    p = os.path.join('data', 'replays', 'platform', os.path.basename(os.path.normpath(d)), 'meta.tsv')
    if os.path.exists(p):
        for line in open(p, encoding='utf-8'):
            f = line.rstrip('\n').split('\t')
            if len(f) >= 8: meta[f[0]] = (f[4], f[7], f[5][5:16])
# map game files to match ids: D.games does not yield the id, so read index order the same way
A = collections.defaultdict(list)
lines = []
for us, res, mp, m, rows in D.games(args):
    mid = m.get('file', '').split('.')[0]
    n = len(rows[0]['c'])
    acc = {s: collections.Counter() for s in (0, 1)}
    first_cap = {0: None, 1: None}; first_trib = {0: None, 1: None}
    snap = {}
    for a, b in zip(rows, rows[1:]):
        for i in range(n):
            c, pc = b['c'][i], a['c'][i]; s = c['t']
            if c['a'] and pc['a'] and c.get('g', 0) > pc.get('g', 0):
                gain = c['g'] - pc['g']
                acc[s]['collected'] += gain
                if c.get('k', 0) > pc.get('k', 0): acc[s]['from kills'] += gain
                elif first_cap[s] is None: first_cap[s] = b['r']
            if pc['a'] and not c['a']:
                acc[s]['lost on death'] += pc.get('g', 0); acc[s]['deaths'] += 1
        for s in (0, 1):
            if first_trib[s] is None and b['sg'][s] > 0: first_trib[s] = b['r']
            acc[s]['tributed'] = b['sg'][s]
        for R in RS:
            if b['r'] <= R: snap[R] = {s: collections.Counter(acc[s]) for s in (0, 1)}
    last = rows[-1]
    for R in RS:
        for s in (0, 1):
            w = 'us' if s == us else 'them'
            for k, v in snap[R][s].items(): A[w, R, k].append(v)
            for k in ('collected', 'from kills', 'tributed', 'lost on death', 'deaths'):
                if k not in snap[R][s]: A[w, R, k].append(0)
    for s in (0, 1):
        w = 'us' if s == us else 'them'
        A[w, 'first cap'].append(first_cap[s] or 999); A[w, 'first trib'].append(first_trib[s] or 9999)
    opp, ver, when = meta.get(mid, ('?', '?', '?'))
    lines.append(f'  {mid[:8]} {when} {ver:9} {res:4} {opp[:24]:24} end r{last["r"]:4} trib {last["sg"][us]:4}-{last["sg"][1 - us]:<4}'
                 f' deaths r1000 {snap[RS[-1]][us]["deaths"]:2}-{snap[RS[-1]][1 - us]["deaths"]:<2}'
                 f' first cap r{first_cap[us] or 999}-r{first_cap[1 - us] or 999} first trib r{first_trib[us] or 9999}-r{first_trib[1 - us] or 9999}')
ng = len(lines)
print(f'{ng} games: ' + ', '.join(args))
for l in lines: print(l)
for R in RS:
    print(f'r{R}: ' + '  |  '.join(w + ' ' + ' '.join(
        f'{k} {statistics.mean(A[w, R, k]):.1f}' if k == 'deaths' else f'{k} {statistics.mean(A[w, R, k]):.0f}'
        for k in ('collected', 'from kills', 'tributed', 'lost on death', 'deaths')) for w in ('us', 'them')))
for k in ('first cap', 'first trib'):
    print(f'{k}: median us r{statistics.median(A["us", k]):.0f} them r{statistics.median(A["them", k]):.0f}'
          f' (never counted as 999/9999)')
