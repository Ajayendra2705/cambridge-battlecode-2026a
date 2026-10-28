"""Paired per-game comparison of two candidates in local `multi.py` runs (helper agent h2).

usage: python -I tools/helper/h2_localpair.py BASE_RUNDIR BASE_CAND NEW_RUNDIR NEW_CAND [NEW_CAND...]
  e.g. python -I tools/helper/h2_localpair.py data/runs/multi-120939 exp.wb1 data/runs/multi-124154 exp.h2fc1 exp.h2cx1

Local games are deterministic, so a candidate that differs from its base only in a rare decision plays most games exactly
as the base did. Games are paired by (opponent, map, side) from the statistics JSON files (no decoding needed). For each
candidate: games identical to the base (same winner, both teams' tributed gems, rounds and our deaths), then over all
paired games and over the changed ones only, the mean difference and its standard error of: our tributed gems, the tribute
margin (ours minus theirs), our deaths, their deaths, our gems collected, our gems lost on death, and wins.
"""
import glob, json, math, os, sys


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
    return {'win': float(d['match']['outcome'] == us), 'trib': sub[us], 'margin': sub[us] - sub[them], 'deaths': deaths[us],
            'their_deaths': deaths[them], 'coll': coll, 'lost': lost, 'rounds': d['match']['roundsCompleted']}


def mean_se(xs):
    if not xs: return 0.0, 0.0
    m = sum(xs) / len(xs)
    if len(xs) < 2: return m, 0.0
    v = sum((x - m) ** 2 for x in xs) / (len(xs) - 1)
    return m, math.sqrt(v / len(xs))


base_dir, base_cand, new_dir, cands = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4:]
keys = ('trib', 'margin', 'deaths', 'their_deaths', 'coll', 'lost', 'win')
for cand in cands:
    diffs, changed = {k: [] for k in keys}, {k: [] for k in keys}
    same = 0
    for p in sorted(glob.glob(os.path.join(new_dir, cand + '~*.json'))):
        name = os.path.basename(p)
        b = os.path.join(base_dir, base_cand + name[len(cand):])
        if not os.path.exists(b): continue
        us = 'teamA' if name.endswith('~A.json') else 'teamB'
        s1, s0 = game_stats(p, us), game_stats(b, us)
        identical = all(s1[k] == s0[k] for k in ('win', 'trib', 'margin', 'deaths', 'rounds'))
        same += identical
        for k in keys:
            diffs[k].append(s1[k] - s0[k])
            if not identical: changed[k].append(s1[k] - s0[k])
    n = len(diffs['trib'])
    print(f'{cand} against {base_cand}: {n} paired games, {same} identical, {n - same} changed')
    for label, data in (('all', diffs), ('changed', changed)):
        print(f'  {label:8}' + ''.join(f'  {k} {mean_se(data[k])[0]:+.2f}+-{mean_se(data[k])[1]:.2f}' for k in keys))
