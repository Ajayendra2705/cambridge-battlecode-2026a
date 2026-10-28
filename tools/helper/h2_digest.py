"""Per-game digest of a local multi.py run, and paired comparisons between digests (helper agent h2).

usage: python -I tools/helper/h2_digest.py RUNDIR CAND > FILE              one line per game of CAND in the run
       python -I tools/helper/h2_digest.py --pair BASE_FILE NEW_FILE [NEW_FILE...]
  e.g. python -I tools/helper/h2_digest.py data/runs/multi-083411 exp.tg1 > data/helper/h2_ref/tg1_multi-083411.txt

The statistics JSON files are about 1 MB each. A digest keeps what tools/helper/h2_localpair.py compares in one line per
game, keyed by opponent, map and side without the candidate's name: winner, rounds, both teams' tributed gems, both teams'
deaths, our gems collected and our gems lost on death. Two runs of the same bot on different machines (this PC, a cloud
Linux box) can then be checked for identical play with `diff`, and a cloud run's numbers travel in a git branch without the
JSON files. --pair prints what h2_localpair.py prints (identical games, mean +- SE of the paired differences), from digests.
"""
import glob, json, math, os, sys

FIELDS = ('win', 'rounds', 'trib', 'their_trib', 'deaths', 'their_deaths', 'coll', 'lost')


def game_stats(path, us):
    d = json.load(open(path, encoding='utf-8'))
    them = 'teamB' if us == 'teamA' else 'teamA'
    sub = {t['team']: int(t['submittedGems']) for t in d['teams']}
    deaths = {us: 0.0, them: 0.0}
    for c in d['champions']:
        deaths[c['team']] = deaths.get(c['team'], 0.0) + float(c['metrics']['deaths'])
    lost = sum(float(x['value']) for e in d['events'] if e['kind'] == 'gemLoss' and e['owner'].get('team') == us for x in e['entries'])
    coll = sum(float(tl['runs'][-1]['value']) for tl in d.get('championTimelines', [])
               if tl['owner'].get('team') == us and tl['metric'] == 'collectedGems' and tl['runs'])
    return {'win': float(d['match']['outcome'] == us), 'rounds': d['match']['roundsCompleted'], 'trib': sub[us],
            'their_trib': sub[them], 'deaths': deaths[us], 'their_deaths': deaths[them], 'coll': coll, 'lost': lost}


def load(path):
    out = {}
    for line in open(path, encoding='utf-8'):
        f = line.split()
        if len(f) != 1 + len(FIELDS): continue
        s = dict(zip(FIELDS, map(float, f[1:])))
        s['margin'] = s['trib'] - s['their_trib']
        out[f[0]] = s
    return out


def mean_se(xs):
    if not xs: return 0.0, 0.0
    m = sum(xs) / len(xs)
    if len(xs) < 2: return m, 0.0
    return m, math.sqrt(sum((x - m) ** 2 for x in xs) / (len(xs) - 1) / len(xs))


if sys.argv[1] == '--pair':
    base = load(sys.argv[2])
    keys = ('trib', 'margin', 'deaths', 'their_deaths', 'coll', 'lost', 'win')
    for path in sys.argv[3:]:
        new = load(path)
        diffs, changed = {k: [] for k in keys}, {k: [] for k in keys}
        same = 0
        for g in sorted(new):
            if g not in base: continue
            s1, s0 = new[g], base[g]
            identical = all(s1[k] == s0[k] for k in ('win', 'trib', 'margin', 'deaths', 'rounds'))
            same += identical
            for k in keys:
                diffs[k].append(s1[k] - s0[k])
                if not identical: changed[k].append(s1[k] - s0[k])
        n = len(diffs['trib'])
        print(f'{os.path.basename(path)} against {os.path.basename(sys.argv[2])}: {n} paired games, {same} identical, {n - same} changed')
        for label, data in (('all', diffs), ('changed', changed)):
            print(f'  {label:8}' + ''.join(f'  {k} {mean_se(data[k])[0]:+.2f}+-{mean_se(data[k])[1]:.2f}' for k in keys))
else:
    run, cand = sys.argv[1], sys.argv[2]
    for p in sorted(glob.glob(os.path.join(run, cand + '~*.json'))):
        name = os.path.basename(p)[len(cand) + 1:-len('.json')]
        s = game_stats(p, 'teamA' if name.endswith('~A') else 'teamB')
        print(name, *(f'{s[k]:g}' for k in FIELDS))
