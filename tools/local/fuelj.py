# Fuel exhaustions per game from the game JSONs (fuelExhausted events, rounds 3 on; rounds 1-2 are world init):
#   python -I tools/local/fuelj.py RUNDIR CAND [CAND...]   (from the repo root; CAND as in the file names)
# Per candidate and team size: games, our exhaustions a game, the rivals'.
import collections, glob, json, os, sys

sz = json.load(open('data/map_sizes.json'))
d = sys.argv[1]
for c in sys.argv[2:]:
    acc = collections.defaultdict(lambda: [0, 0, 0])  # size -> games, ours, theirs
    for f in glob.glob(os.path.join(d, c + '~*.json')):
        _, opp, mp, side = os.path.basename(f)[:-5].split('~')
        s = sz.get(mp.replace('-', '_'))
        j = json.load(open(f, encoding='utf-8'))
        a = acc[s]
        a[0] += 1
        for e in j['events']:
            if e['kind'] != 'fuelExhausted':
                continue
            n = sum(1 for x in e['entries'] if x['timestamp']['round'] >= 3)
            a[1 if e['owner']['team'] == 'team' + side else 2] += n
    print(c + '  ' + '  '.join(f'{s}v{s}: {g} games, ours {o / g:.2f}, rivals {t / g:.2f}'
                                for s, (g, o, t) in sorted(acc.items()) if g))
