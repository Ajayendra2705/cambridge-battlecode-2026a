"""Banking numbers of a local multi.py run from its statistics JSONs, per map and candidate, to round R (h3, 10-28).

usage: python -I tools/helper3/h3_jsonbank.py RUNDIR CAND [CAND ...] [--upto R]   (CAND as in the file names: main, exp.h3bq1)

From each `CAND~OPP~MAP~SIDE.json` (our team is teamA for SIDE A): `gemSubmission` events (one per completed tribute,
value = gems banked), `gemLoss` events owned by our champions (value = gems lost at a death) and `death` events. Per
game to round R (default 1000): tributes and their median bag, tributed, lost on death (deaths with a bag and its
median), our deaths, and our champion-rounds carrying 40+ and 80+ gems (from the `gems` championTimelines, run-length
per round); also wins over the whole game. No decode needed; on a decode, `decoded.py gems` gives the same tributed
and lost on death.
"""
import collections, glob, json, os, statistics, sys

args = sys.argv[1:]
R = 1000
if '--upto' in args:
    i = args.index('--upto'); R = int(args[i + 1]); del args[i:i + 2]
run, cands = args[0], args[1:]
C = collections.Counter(); B = collections.defaultdict(list); L = collections.defaultdict(list)
for cand in cands:
    for f in sorted(glob.glob(os.path.join(run, cand + '~*.json'))):
        _, opp, mp, side = os.path.basename(f)[:-5].split('~')
        us = 'teamA' if side == 'A' else 'teamB'
        d = json.load(open(f, encoding='utf-8'))
        for key in (mp, 'all'):
            C[cand, key, 'games'] += 1; C[cand, key, 'wins'] += d['match']['outcome'] == us
        for tl in d.get('championTimelines', []):
            if tl['metric'] != 'gems' or tl['owner'].get('team') != us: continue
            t = 0
            for run_ in tl['runs']:
                dur = min(int(run_['duration']), max(0, R - t)); t += int(run_['duration'])
                v = float(run_['value'])
                for key in (mp, 'all'):
                    if v >= 40: C[cand, key, 'x40'] += dur
                    if v >= 80: C[cand, key, 'x80'] += dur
        for e in d['events']:
            if e['owner'].get('team') != us: continue
            for en in e['entries']:
                if en['timestamp']['round'] > R: continue
                v = float(en.get('value') or 0)
                for key in (mp, 'all'):
                    if e['kind'] == 'gemSubmission': C[cand, key, 'trib'] += v; C[cand, key, 'n'] += 1; B[cand, key].append(v)
                    elif e['kind'] == 'gemLoss':
                        C[cand, key, 'lost'] += v
                        if v > 0: L[cand, key].append(v)
                    elif e['kind'] == 'death': C[cand, key, 'deaths'] += 1
maps = sorted({k[1] for k in C if k[2] == 'games'}, key=lambda m: (m == 'all', m))
print(f'per game to r{R}: wins (whole game), tributes, median bag tributed, tributed, lost on death, our deaths')
for mp in maps:
    for cand in cands:
        n = max(1, C[cand, mp, 'games'])
        med = statistics.median(B[cand, mp]) if B[cand, mp] else 0
        lmed = statistics.median(L[cand, mp]) if L[cand, mp] else 0
        print(f'{mp:20} {cand:10} {C[cand, mp, "games"]:3} games {C[cand, mp, "wins"]:3} wins | tributes {C[cand, mp, "n"] / n:5.1f}'
              f' median bag {med:5.0f} | tributed {C[cand, mp, "trib"] / n:6.0f} | lost {C[cand, mp, "lost"] / n:5.0f}'
              f' ({len(L[cand, mp]) / n:4.2f} deaths with a bag, median {lmed:4.0f}) | deaths {C[cand, mp, "deaths"] / n:4.1f}'
              f' | rounds carrying 40+ {C[cand, mp, "x40"] / n:5.0f}, 80+ {C[cand, mp, "x80"] / n:4.0f}')
