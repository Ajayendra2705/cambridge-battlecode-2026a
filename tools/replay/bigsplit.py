"""Are big captures split? python -I tools/replay/bigsplit.py DIR [DIR ...]

A capture shows as gems arriving in bags in one round. Per side: rewards of at least 40 gems by size band, how many champions
shared them, the biggest bag held per game, gems lost with a death by bag size, and the fate of bags of 100+ (banked in one
channel, died holding it, game ended holding it). A bag of G gems is a channel of G / 10 rounds, so one champion holding 300
gems needs 30 rounds at an altar, and a death hands the whole bag over.
"""
import collections, sys
sys.path.insert(0, 'tools/replay')
import decoded as D

dirs = sys.argv[1:]
CAP = {'us': collections.Counter(), 'them': collections.Counter()}
SH = {'us': collections.defaultdict(list), 'them': collections.defaultdict(list)}
BIG = {'us': collections.Counter(), 'them': collections.Counter()}
LOST = {'us': collections.Counter(), 'them': collections.Counter()}
games = 0
wins_by = collections.Counter()


def band(g):
    return '40-59' if g < 60 else '60-99' if g < 100 else '100-199' if g < 200 else '200-399' if g < 400 else '400+'


for us, res, mp, meta, rows in D.games(dirs):
    games += 1
    prev = None
    maxbag = {0: 0, 1: 0}
    lost_in_game = {0: 0, 1: 0}
    for x in rows:
        if prev is not None:
            arr = {0: [], 1: []}
            for i, c in enumerate(x['c']):
                p = prev['c'][i]
                t = c['t']
                dg = c.get('g', 0) - p.get('g', 0)
                if dg > 0 and c.get('a'):
                    arr[t].append(dg)
                if p.get('a') and not c.get('a') and p.get('g', 0) > 0:
                    g = p.get('g', 0)
                    side = 'us' if t == us else 'them'
                    LOST[side]['all'] += g
                    LOST[side]['n'] += 1
                    if g >= 100:
                        LOST[side]['big'] += g
                        LOST[side]['big_n'] += 1
                    lost_in_game[t] += g
            for t in (0, 1):
                tot = sum(arr[t])
                if tot >= 40:
                    side = 'us' if t == us else 'them'
                    b = band(tot)
                    CAP[side][b] += 1
                    SH[side][b].append(len(arr[t]))
        for c in x['c']:
            if c.get('a'):
                maxbag[c['t']] = max(maxbag[c['t']], c.get('g', 0))
        prev = x
    for t in (0, 1):
        side = 'us' if t == us else 'them'
        BIG[side]['n'] += 1
        for cut in (100, 200, 400):
            if maxbag[t] >= cut:
                BIG[side][cut] += 1
    win = res == 'win'
    k = 'big' if maxbag[us] >= 200 else 'small'
    wins_by[k + '_n'] += 1
    wins_by[k + '_w'] += win

print('games', games)
for side in ('us', 'them'):
    print(side)
    for b in ('40-59', '60-99', '100-199', '200-399', '400+'):
        v = SH[side][b]
        if v:
            print(f"  reward {b:8s}: {len(v)/games:5.2f} a game, sharers {sum(v)/len(v):.2f}; alone {sum(1 for s in v if s == 1)/len(v):.0%}")
    n = BIG[side]['n']
    print(f"  games with a bag of 100+ {BIG[side][100]/n:.0%}, 200+ {BIG[side][200]/n:.0%}, 400+ {BIG[side][400]/n:.0%}")
    print(f"  gems lost on death a game {LOST[side]['all']/n:.1f}, of those from bags of 100+ {LOST[side]['big']/n:.1f} ({LOST[side]['big_n']/n:.2f} deaths a game)")
print('wins in games where our biggest bag was 200+:', wins_by['big_w'], 'of', wins_by['big_n'], '; under 200:', wins_by['small_w'], 'of', wins_by['small_n'])
