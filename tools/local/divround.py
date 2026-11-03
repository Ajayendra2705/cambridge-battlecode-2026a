"""Where do paired local games part? python -I tools/local/divround.py BASE_DIR BASE NEW_DIR NEW

Local games replay exactly only while both bots use the same fuel, since fuel left steers some choices. For each game of NEW paired
with BASE: the first round any champion's gems, earned gold or a team's tributed gems differ, and the first round our hand
(tributed plus bags) reached 600 in the base, which is the earliest a rule near the end could act. Prints how many games part
before that round, by result flips, so a screen limited to end-of-game games is not read when the games have diverged anyway.
"""
import glob, json, os, sys


def series(runs, n):
    out = []
    for r in runs:
        out += [float(r['value'])] * int(r['duration'])
    last = out[-1] if out else 0.0
    return (out + [last] * n)[:n]


def load(path):
    d = json.load(open(path, encoding='utf-8'))
    n = int(d['match']['roundsCompleted']) + 2
    tl = {}
    for t in d['championTimelines']:
        if t['metric'] in ('gems', 'earnedGold'):
            tl[(t['metric'], t['owner']['team'], t['owner']['id'])] = series(t['runs'], n)
    for t in d['teamTimelines']:
        if t['metric'] == 'submittedGems':
            tl[('sub', t['owner'], 0)] = series(t['runs'], n)
    return d, n, tl


base_dir, base, new_dir, new = sys.argv[1:5]
early = same = late = 0
flips = {'early': [0, 0], 'late': [0, 0]}
rounds = []
for p in sorted(glob.glob(os.path.join(new_dir, new + '~*.json'))):
    tail = os.path.basename(p).split('~', 1)[1]
    q = os.path.join(base_dir, base + '~' + tail)
    if not os.path.exists(q):
        continue
    us = 'team' + tail[:-5].rsplit('~', 1)[1]
    dn, nn, tn = load(p)
    db, nb, tb = load(q)
    m = min(nn, nb)
    div = None
    for k in tb:
        if k not in tn:
            continue
        for r in range(m):
            if tb[k][r] != tn[k][r]:
                div = r if div is None else min(div, r)
                break
    hand600 = None
    sub = tb.get(('sub', us, 0))
    bags = [v for k, v in tb.items() if k[0] == 'gems' and k[1] == us]
    for r in range(nb):
        if sub[r] + sum(b[r] for b in bags) >= 600:
            hand600 = r
            break
    wb = db['match']['outcome'] == us
    wn = dn['match']['outcome'] == us
    if div is None:
        same += 1
        continue
    rounds.append(div)
    kind = 'early' if hand600 is None or div < hand600 else 'late'
    if kind == 'early':
        early += 1
    else:
        late += 1
    flips[kind][0] += wn and not wb
    flips[kind][1] += wb and not wn
rounds.sort()
print('identical', same, '| parted before the hand reached 600:', early, 'flips up/down', flips['early'], '| after:', late, 'flips up/down', flips['late'])
if rounds:
    print('parting round: median', rounds[len(rounds) // 2], 'first quartile', rounds[len(rounds) // 4], 'smallest', rounds[0])
