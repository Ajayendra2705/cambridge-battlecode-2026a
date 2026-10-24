"""Gems collected (coll) and tributed (sub) by our team by a given round, per candidate, from a local multi.py run (the replay json timelines).
usage: python -I tools/local/coll_at.py RUNDIR [ROUND ...]   (default rounds 300 600). File names are
CANDIDATE~OPPONENT~MAP~SIDE.json with our candidate on SIDE (A = teamA)."""
import collections, glob, json, os, sys


def at(runs, r):
    t, v = 0, 0
    for run in runs:
        if t >= r: break
        v = int(run['value']); t += run['duration']
    return v


def main():
    d, rounds = sys.argv[1], [int(x) for x in sys.argv[2:]] or [300, 600]
    acc = collections.defaultdict(lambda: collections.defaultdict(list))
    for f in glob.glob(os.path.join(d, '*.json')):
        cand, _, _, side = os.path.basename(f)[:-5].split('~')
        j = json.load(open(f))
        team = 'team' + side
        tl = [t for t in j['championTimelines'] if t['metric'] == 'collectedGems']
        sub = {t['owner']: t['runs'] for t in j['teamTimelines'] if t['metric'] == 'submittedGems'}
        for r in rounds:
            for who in ('us', 'them'):
                acc[cand][(r, who)].append(sum(at(t['runs'], r) for t in tl if (t['owner']['team'] == team) == (who == 'us')))
                acc[cand][(r, 'sub ' + who)].append(sum(at(v, r) for k, v in sub.items() if (k == team) == (who == 'us')))
    print(f"{'candidate':16}" + ''.join(f'{f"r{r} {w}":>13}' for r in rounds for w in ('us', 'them', 'sub us', 'sub them')))
    for cand, a in sorted(acc.items()):
        print(f'{cand:16}' + ''.join(f'{sum(a[(r, w)]) / len(a[(r, w)]):13.1f}' for r in rounds for w in ('us', 'them', 'sub us', 'sub them')))


if __name__ == '__main__':
    main()
