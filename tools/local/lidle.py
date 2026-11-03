"""Idle bodies in a local multi.py run: python -I tools/local/lidle.py RUN_DIR CAND [--round 1000] [--top 40]

Per map and champion type, over the candidate's games on that map: gold earned, gems collected, monster damage, champion damage and deaths by the round, and the type's share of
the team's gold and gems. Lists the lowest shares first. A body with almost no gold and no gems and few deaths on a map where the team does well is idle or stuck, not losing fights.
"""
import collections, glob, json, os, sys

args = sys.argv[1:]
def opt(name, default):
    if name in args:
        k = args.index(name)
        v = args[k + 1]
        del args[k:k + 2]
        return int(v)
    return default
rnd, top = opt('--round', 1000), opt('--top', 40)
run, cand = args


def at(runs, r):
    k = 0
    for x in runs:
        k += x['duration']
        if r < k:
            return float(x['value'])
    return float(runs[-1]['value']) if runs else 0.0


A = collections.defaultdict(lambda: collections.defaultdict(collections.Counter))
N = collections.Counter()
for p in glob.glob(os.path.join(run, cand + '~*.json')):
    _, o, m, s = os.path.basename(p)[:-5].split('~')
    d = json.load(open(p, encoding='utf-8'))
    team = 'team' + s
    N[m] += 1
    for t in d['championTimelines']:
        if t['owner'].get('team') == team and t['metric'] in ('earnedGold', 'collectedGems', 'monsterDamageDone', 'championDamageDone', 'deaths'):
            A[m][t['owner'].get('name')][t['metric']] += at(t['runs'], rnd)
rows = []
for m, types in A.items():
    n = N[m]
    tg = sum(c['earnedGold'] for c in types.values()) / n
    te = sum(c['collectedGems'] for c in types.values()) / n
    k = len(types)
    for name, c in types.items():
        g, e = c['earnedGold'] / n, c['collectedGems'] / n
        share = (g / max(1, tg) + e / max(1, te)) / 2 * k  # 1 = a fair share of the team's gold and gems
        rows.append((share, m, name, g, e, c['monsterDamageDone'] / n, c['championDamageDone'] / n, c['deaths'] / n, tg, te))
rows.sort()
print(f"{'share':5} {'map':24} {'type':14} {'gold':>6} {'gems':>5} {'mon dmg':>8} {'ch dmg':>7} {'deaths':>6} | team gold gems")
for r in [x for x in rows if x[2] != 'Willow'][:top]:
    print(f'{r[0]:5.2f} {r[1]:24} {r[2]:14} {r[3]:6.0f} {r[4]:5.0f} {r[5]:8.0f} {r[6]:7.0f} {r[7]:6.1f} | {r[8]:6.0f} {r[9]:5.0f}')
