"""Why a champion takes no action with an enemy champion in reach: python -I tools/replay/stillwhy.py RMIN RMAX DIR...

Counts rounds per game, us / them, over living champions with an enemy within reach (melee 2, ranged 3) and an empty action list, by the first cause that fits:
stun (a stun aimed at it this round or the last), recall channel (it jumps 4+ tiles without dying within the next 6 rounds), tribute channel (a tribute act in the last
30 rounds and no move since), fuel (a fuelExhausted event of that champion this round, from data/summaries), other. Also prints the same by champion type for "other" and
for all causes together, and the health of "other" rounds.
"""
import collections, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import decoded as D
D.SKIP = []
RANGED = {'vesper', 'cassi', 'willow', 'tavi', 'prism', 'stellar'}
r0, r1 = int(sys.argv[1]), int(sys.argv[2])
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
N = collections.defaultdict(collections.Counter)
ng = 0


def stunned(rows, k, i):
    """A stun aimed at champion i in round index k or k-1."""
    me = rows[k]['c'][i]
    p = (me['x'], me['y'])
    n = len(rows[k]['c'])
    for rr in (k - 1, k):
        if rr < 0:
            continue
        row = rows[rr]
        for j in range(n):
            if row['c'][j]['t'] == me['t'] or j >= len(row['act']):
                continue
            tn = D.NAMES[row['c'][j]['ty']]
            for x in row['act'][j]:
                if x[0] == 'cast':
                    if tn == 'heart' and x[1] == 1 and len(x) >= 4 and D.dist((x[2], x[3]), p) <= 2:
                        return True
                    if tn == 'ryth' and x[1] == 0 and len(x) >= 4 and D.dist((x[2], x[3]), p) <= 2:
                        return True
                    if tn in ('ren', 'prism', 'tavi', 'cassi') and len(x) >= 6 and x[-2] == 'c' and x[-1] == i:
                        return True
                elif x[0] == 'attack' and tn == 'marcella' and len(x) >= 5 and x[-2] == 'c' and x[-1] == i:
                    for q in range(max(0, rr - 3), rr + 1):
                        if j < len(rows[q]['act']) and any(y[0] == 'cast' and y[1] == 0 for y in rows[q]['act'][j]):
                            return True
    return False


for us, res, mp, meta, rows in D.games(sys.argv[3:]):
    ng += 1
    ev = collections.defaultdict(set)
    p = os.path.join(ROOT, 'data', 'summaries', meta['file'].split('.')[0] + '.json')
    if os.path.exists(p):
        try:
            for e in json.load(open(p, encoding='utf-8'))['events']:
                if e['kind'] == 'fuelExhausted' and e['owner'].get('kind') == 'champion':
                    for x in e['entries']:
                        ev[e['owner']['id']].add(x['timestamp']['round'])
        except Exception:
            pass
    last_trib = {}
    last_move = {}
    n = len(rows[0]['c'])
    for k, row in enumerate(rows):
        R = row['r']
        if R > r1:
            break
        for i in range(min(n, len(row['act']))):
            for x in row['act'][i]:
                if x[0] == 'tribute':
                    last_trib[i] = R
                elif x[0] == 'move':
                    last_move[i] = R
        if R < r0:
            continue
        for i, c in enumerate(row['c']):
            if not c['a'] or 'x' not in c:
                continue
            name = D.NAMES[c['ty']]
            reach = 3 if name in RANGED else 2
            pos = (c['x'], c['y'])
            if not any(e['t'] != c['t'] and e['a'] and 'x' in e and D.dist(pos, (e['x'], e['y'])) <= reach for e in row['c']):
                continue
            w = D.who(c['t'], us)
            N[w]['rounds'] += 1
            if i < len(row['act']) and row['act'][i]:
                continue
            cause = None
            if stunned(rows, k, i):
                cause = 'stun'
            if cause is None:
                for q in range(k + 1, min(k + 7, len(rows))):
                    d = rows[q]['c'][i]
                    if not d['a'] or 'x' not in d:
                        break
                    if D.dist(pos, (d['x'], d['y'])) >= 4:
                        cause = 'recall'
                        break
            if cause is None and i in last_trib and R - last_trib[i] <= 30 and last_move.get(i, -1) < last_trib[i]:
                cause = 'tribute'
            if cause is None and R in ev.get(i, ()):
                cause = 'fuel'
            cause = cause or 'other'
            N[w][cause] += 1
            N[w]['still'] += 1
            N[w][cause + ':' + name] += 1
            if cause == 'other':
                hp = c['hp'] / max(1, c['mhp'])
                N[w]['other hp ' + ('>.7' if hp > .7 else '.4-.7' if hp > .4 else '<.4')] += 1
                N[w]['other bag ' + ('30+' if c.get('g', 0) >= 30 else 'less')] += 1
print(f'{ng} games, r{r0}-{r1}: rounds per game with an enemy in reach, then no-action rounds by cause, us / them')
for key in ['rounds', 'still', 'stun', 'recall', 'tribute', 'fuel', 'other', 'other hp >.7', 'other hp .4-.7', 'other hp <.4', 'other bag 30+', 'other bag less'] + [f'other:{t}' for t in ('heart', 'marcella', 'vendetta', 'vesper', 'willow', 'ryth', 'tavi')] + [f'stun:{t}' for t in ('heart', 'vendetta', 'vesper', 'willow')]:
    print(f"  {key:16} {N['us'][key] / ng:6.2f} / {N['them'][key] / ng:6.2f}")
