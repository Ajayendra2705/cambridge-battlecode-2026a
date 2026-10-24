"""Analyses of decoded platform games (datasets from rounds_extract.mjs), us vs the opponents.

usage: python -I tools/replay/decoded.py CMD DIR [DIR ...] [--round R ...]

DIR is a folder of <match>.jsonl.gz files with an index.txt ("match map side result", side a = team 0), as written by
tools/replay/decode_run.sh. Several DIRs are pooled. Commands:

  gems      collected, tributed, lost on death, carried bag and deaths per game by round (default 300 600 1000)
  fights    by round 800: hits on enemy champions, champion damage dealt, deaths; outcome of fight starts
  channels  tribute channels by bag size (share completed) and the per-turn break rate by enemies near the altar
  types     per champion type: deaths, champion damage, gems, share of alive rounds hitting a champion, and the hit
            rate by distance to the nearest enemy
  items     emblems and shards per champion type at a round (default 600)
  risk      P(death within 10 rounds) by enemies / allies within 6 and health above or below half
  sources   gems collected by camp type by a round (default 600), credited to the camp type last hit
"""
import collections, glob, gzip, json, math, os, sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
NAMES = ['ryth', 'vesper', 'vendetta', 'cassi', 'issac', 'stellar', 'prism', 'marcella', 'willow', 'ren', 'varg', 'tavi',
         'heart']
RANGE = {0: 1, 1: 3, 2: 1, 3: 3, 4: 1, 5: 3, 6: 3, 7: 1, 8: 3, 9: 1, 10: 1, 11: 3, 12: 1}
CAMPS = {0: 'wolf', 1: 'elk', 2: 'gem', 3: 'gold', 4: 'monolith', 5: 'golem'}
ITEMS = [f'{fam}_{stat}' for fam in ('monster', 'power', 'durability', 'treasure', 'jungle', 'home', 'bruiser')
         for stat in ('str', 'focus', 'hp')]  # item_type i is ITEMS[i // 2]: a shard when i is even, its emblem when odd


def dist(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))


def games(dirs):
    """Yield (us, result, map, meta, rows) per decoded game; rows keep only rounds with every champion listed."""
    for d in dirs:
        index = os.path.join(d, 'index.txt')
        side = {}
        for line in open(index, encoding='utf-8', errors='replace'):
            p = line.strip().split()
            if len(p) >= 4: side[p[0]] = (0 if p[2] == 'a' else 1, p[3], p[1])
        for f in sorted(glob.glob(os.path.join(d, '*.jsonl.gz'))):
            mid = os.path.basename(f).split('.')[0]
            if mid not in side: continue
            lines = [json.loads(l) for l in gzip.open(f, 'rt')]
            rows = [r for r in lines[1:] if r.get('c')]
            if not rows: continue
            n = max(len(r['c']) for r in rows)
            rows = [r for r in rows if len(r['c']) == n]
            us, res, mp = side[mid]
            yield us, res, mp, lines[0], rows


def who(team, us):
    return 'us' if team == us else 'them'


def enemy_hits(row, i, n):
    """Attacks and casts of champion i that hit an enemy champion this round."""
    me = row['c'][i]
    return [x for x in (row['act'][i] if i < len(row['act']) else []) if x[0] in ('attack', 'cast') and len(x) >= 5
            and x[-2] == 'c' and x[-1] < n and row['c'][x[-1]]['t'] != me['t']]


def camp_hits(row, i):
    return [x for x in (row['act'][i] if i < len(row['act']) else []) if x[0] in ('attack', 'cast') and len(x) >= 5 and x[-2] == 'm']


def cmd_gems(dirs, rounds):
    rounds = rounds or [300, 600, 1000]
    for R in rounds:
        A = {w: collections.Counter() for w in ('us', 'them')}
        ng = 0
        for us, res, mp, meta, rows in games(dirs):
            ng += 1
            last = rows[0]
            for a, b in zip(rows, rows[1:]):
                if b['r'] > R: break
                last = b
                for i, c in enumerate(b['c']):
                    pc = a['c'][i]; w = who(c['t'], us)
                    if c['a'] and pc['a'] and c.get('g', 0) > pc.get('g', 0): A[w]['collected'] += c['g'] - pc['g']
                    if pc['a'] and not c['a']: A[w]['lost on death'] += pc.get('g', 0); A[w]['deaths'] += 1
            for c in last['c']:
                if c['a']: A[who(c['t'], us)]['bag'] += c.get('g', 0)
            for t in (0, 1): A[who(t, us)]['tributed'] += last['sg'][t]
        print(f'r{R} ({ng} games)  ' + '  |  '.join(
            w + ' ' + ' '.join(f'{k} {A[w][k] / max(1, ng):.0f}' if k != 'deaths' else f'{k} {A[w][k] / max(1, ng):.1f}'
                               for k in ('collected', 'tributed', 'lost on death', 'bag', 'deaths')) for w in ('us', 'them')))


def cmd_fights(dirs, rounds):
    R = (rounds or [800])[0]
    H, D, De, S = collections.Counter(), collections.Counter(), collections.Counter(), collections.Counter()
    ng = 0
    for us, res, mp, meta, rows in games(dirs):
        ng += 1
        n = len(rows[0]['c'])
        last_hit = {}
        for k, (a, b) in enumerate(zip(rows, rows[1:])):
            if b['r'] > R: break
            for i, c in enumerate(b['c']):
                if a['c'][i]['a'] and not c['a']: De[who(c['t'], us)] += 1
            targets = collections.defaultdict(list)
            for i in range(n):
                for x in enemy_hits(a, i, n): targets[x[-1]].append(i)
            for t, hitters in targets.items():
                loss = max(0, a['c'][t].get('hp', 0) - (b['c'][t].get('hp', 0) if b['c'][t]['a'] else 0))
                for i in hitters:
                    w = who(a['c'][i]['t'], us); H[w] += 1; D[w] += loss / len(hitters)
            # Fight starts: the first hit between two champions after 15 quiet rounds; deaths within 8 tiles over 20 rounds.
            for i in range(n):
                for x in enemy_hits(a, i, n):
                    key = frozenset((i, x[-1]))
                    if k - last_hit.get(key, -99) > 15 and k + 21 < len(rows):
                        att = a['c'][i]['t']; pos = (a['c'][i].get('x', 0), a['c'][i].get('y', 0))
                        own = foe = 0
                        for j, o in enumerate(a['c']):
                            if not o['a'] or 'x' not in o or dist(pos, (o['x'], o['y'])) > 8: continue
                            if any(not rows[k + t]['c'][j]['a'] for t in range(1, 21)):
                                if o['t'] == att: own += 1
                                else: foe += 1
                        w = who(att, us); S[(w, 'n')] += 1; S[(w, 'own')] += own; S[(w, 'foe')] += foe
                    last_hit[key] = k
    print(f'by r{R} ({ng} games): ' + ' | '.join(f'{w} hits {H[w] / ng:.0f} champion damage {D[w] / ng:.0f} deaths {De[w] / ng:.1f}'
                                                  for w in ('us', 'them')))
    for w in ('us', 'them'):
        n = max(1, S[(w, 'n')])
        print(f'  fights {w} start: {S[(w, "n")] / ng:.1f} per game, starter loses {S[(w, "own")] / n:.2f}, kills {S[(w, "foe")] / n:.2f} per start')


def cmd_channels(dirs, rounds):
    C = collections.Counter(); L = collections.defaultdict(lambda: [0.0, 0, 0])
    ng = 0
    for us, res, mp, meta, rows in games(dirs):
        ng += 1
        n = len(rows[0]['c'])
        for k, b in enumerate(rows):
            for i, acts in enumerate(b['act'][:n]):
                tr = [x for x in acts if x[0] == 'tribute']
                c = b['c'][i]; g = c.get('g', 0)
                if not tr or g <= 0: continue
                turns = max(1, -(-g // 10)); j = min(len(rows) - 1, k + turns + 2)
                ok = rows[j]['sg'][c['t']] - b['sg'][c['t']] >= g * 0.9
                w = who(c['t'], us); size = '<=20' if g <= 20 else '21-50' if g <= 50 else '51-100' if g <= 100 else '>100'
                C[(w, size, 'n')] += 1; C[(w, size, 'ok')] += ok; C[(w, size, 'g')] += g; C[(w, size, 'banked')] += g * ok
                altar = (tr[0][1], tr[0][2])
                near = sum(1 for o in b['c'] if o['t'] != c['t'] and o['a'] and 'x' in o and dist(altar, (o['x'], o['y'])) <= 10)
                L[(w, min(near, 2))][0] += turns; L[(w, min(near, 2))][1] += 1; L[(w, min(near, 2))][2] += not ok
    print(f'{ng} games; tribute channels per game by bag size:')
    for w in ('us', 'them'):
        for size in ('<=20', '21-50', '51-100', '>100'):
            n = C[(w, size, 'n')]
            if n: print(f'  {w:4} {size:6} starts {n / ng:4.1f}  completed {100 * C[(w, size, "ok")] / n:3.0f}%  gems started {C[(w, size, "g")] / ng:4.0f}  banked {C[(w, size, "banked")] / ng:4.0f}')
    print('per-turn break rate by enemies within 10 of the altar (failures / channel turns):')
    for k in sorted(L):
        turns, n, fails = L[k]
        print(f'  {k[0]:4} {k[1]} enemies: {n} channels, break rate {fails / max(1, turns):.4f}')


def cmd_types(dirs, rounds):
    R = (rounds or [1000])[0]
    A = collections.defaultdict(collections.Counter); G = collections.Counter()
    for us, res, mp, meta, rows in games(dirs):
        n = len(rows[0]['c'])
        for c in rows[0]['c']: G[(who(c['t'], us), c['ty'])] += 1
        for a, b in zip(rows, rows[1:]):
            if b['r'] > R: break
            targets = collections.defaultdict(list)
            for i in range(n):
                for x in enemy_hits(a, i, n): targets[x[-1]].append(i)
            for t, hitters in targets.items():
                loss = max(0, a['c'][t].get('hp', 0) - (b['c'][t].get('hp', 0) if b['c'][t]['a'] else 0))
                for i in hitters: A[(who(a['c'][i]['t'], us), a['c'][i]['ty'])]['dmg'] += loss / len(hitters)
            for i, c in enumerate(a['c']):
                k = (who(c['t'], us), c['ty']); C = A[k]; nc = b['c'][i]
                if not c['a']: continue
                C['alive'] += 1
                if not nc['a']: C['deaths'] += 1
                elif nc.get('g', 0) > c.get('g', 0): C['gems'] += nc['g'] - c['g']
                if 'x' not in c: continue
                hit = bool(enemy_hits(a, i, n)); C['hit rounds'] += hit
                enemies = [o for o in a['c'] if o['t'] != c['t'] and o['a'] and 'x' in o]
                if not enemies: continue
                dn = min(dist((c['x'], c['y']), (o['x'], o['y'])) for o in enemies)
                rng = RANGE.get(c['ty'], 1)
                band = 'in range' if dn <= rng else 'range+1-2' if dn <= rng + 2 else None
                if band: C[band] += 1; C[band + ' hit'] += hit
    print(f'per champion type, rounds to {R} (per game unless marked):')
    for k in sorted(G, key=lambda k: (NAMES[k[1]], k[0])):
        g, C = G[k], A[k]
        if g < 10: continue
        alive = max(1, C['alive'])
        bands = '  '.join(f'{b} hit {C[b + " hit"] / max(1, C[b]):.2f}' for b in ('in range', 'range+1-2'))
        print(f'  {NAMES[k[1]]:9} {k[0]:4} games {g:3}  deaths {C["deaths"] / g:.2f}  champion dmg {C["dmg"] / g:5.0f}  gems {C["gems"] / g:4.0f}'
              f'  hit-round share {C["hit rounds"] / alive:.3f}  {bands}')


def cmd_items(dirs, rounds):
    R = (rounds or [600])[0]
    I = collections.defaultdict(collections.Counter); N = collections.Counter(); HP = collections.Counter()
    for us, res, mp, meta, rows in games(dirs):
        row = next((r for r in rows if r['r'] >= R), None)
        if not row: continue
        for c in row['c']:
            k = (who(c['t'], us), c['ty']); N[k] += 1; HP[k] += c.get('mhp', 0)
            for it, cnt in c.get('it', []): I[k][ITEMS[it // 2] + (' emblem' if it % 2 else ' shard')] += cnt
    print(f'items per champion at r{R} (emblems and shards):')
    for k in sorted(N, key=lambda k: (NAMES[k[1]], k[0])):
        if N[k] < 10: continue
        top = ', '.join(f'{name} {v / N[k]:.2f}' for name, v in sorted(I[k].items(), key=lambda x: -x[1]) if v / N[k] >= 0.1)
        print(f'  {NAMES[k[1]]:9} {k[0]:4} n {N[k]:3} max hp {HP[k] / N[k]:5.0f}  {top}')


def cmd_risk(dirs, rounds):
    C = collections.Counter()
    for us, res, mp, meta, rows in games(dirs):
        for k in range(0, len(rows) - 11, 2):
            a = rows[k]
            for i, c in enumerate(a['c']):
                if c['t'] != us or not c['a'] or 'x' not in c: continue
                pos = (c['x'], c['y'])
                ne = sum(1 for o in a['c'] if o['t'] != us and o['a'] and 'x' in o and dist(pos, (o['x'], o['y'])) <= 6)
                na = sum(1 for j, o in enumerate(a['c']) if j != i and o['t'] == us and o['a'] and 'x' in o and dist(pos, (o['x'], o['y'])) <= 6)
                dies = any(not rows[k + t]['c'][i]['a'] for t in range(1, 11))
                key = (min(ne, 3), min(na, 2), 'below half' if c.get('hp', 0) < 0.5 * max(1, c.get('mhp', 1)) else 'above half')
                C[key + ('n',)] += 1; C[key + ('d',)] += dies
    print('our champions: P(death within 10 rounds) by enemies within 6, allies within 6, health')
    for key in sorted({k[:3] for k in C}):
        n = C[key + ('n',)]
        print(f'  enemies {key[0]} allies {key[1]} {key[2]:10}: {C[key + ("d",)] / n:.3f}  (n {n})')


def cmd_sources(dirs, rounds):
    R = (rounds or [600])[0]
    H = {w: collections.Counter() for w in ('us', 'them')}; ng = 0
    for us, res, mp, meta, rows in games(dirs):
        ng += 1
        camps = {int(k): v for k, v in meta.get('camps', {}).items()}
        n = len(rows[0]['c']); last = {}
        for a, b in zip(rows, rows[1:]):
            if b['r'] > R: break
            for i in range(n):
                for x in camp_hits(a, i): last[i] = CAMPS.get(camps.get(x[-1]), '?')
            for i, c in enumerate(b['c']):
                if c['a'] and a['c'][i]['a'] and c.get('g', 0) > a['c'][i].get('g', 0):
                    H[who(c['t'], us)][last.get(i, '?')] += c['g'] - a['c'][i]['g']
    for w in ('us', 'them'):
        print(f'{w} gems by r{R} per game: ' + ', '.join(f'{k} {v / ng:.0f}' for k, v in sorted(H[w].items(), key=lambda x: -x[1])))


def main():
    args = sys.argv[1:]
    if len(args) < 2 or args[0] not in CMDS: sys.exit(__doc__)
    rounds = []
    if '--round' in args:
        j = args.index('--round'); rounds = [int(x) for x in args[j + 1:]]; args = args[:j]
    CMDS[args[0]](args[1:], rounds)


CMDS = {'gems': cmd_gems, 'fights': cmd_fights, 'channels': cmd_channels, 'types': cmd_types, 'items': cmd_items,
        'risk': cmd_risk, 'sources': cmd_sources}

if __name__ == '__main__':
    main()
