"""Head-to-head results of a local run: python -I tools/local/h2h.py RUNDIR [--maps] [--size]

For each candidate and opponent in the run: games, wins, final margin (tributed us minus them) with its standard error, deaths and kills a game. With --maps, one line per map (wins and margin), worst first. With --size,
the same split by team size. The old local pool loses 82% of its games to our bots, so it shows little of what ranked rivals do; a bot of the current line as the opponent starts from 50% (`b23` and `b30` against each other).
"""
import collections, glob, json, math, os, sys

d = sys.argv[1]
bymap = '--maps' in sys.argv
bysize = '--size' in sys.argv
R = collections.defaultdict(list)
for p in glob.glob(os.path.join(d, '*.json')):
    base = os.path.basename(p)[:-5].split('~')
    if len(base) != 4:
        continue
    cand, opp, mp, side = base
    try:
        j = json.load(open(p, encoding='utf-8'))
    except Exception:
        continue
    us = 'team' + side
    sub = {t['team']: int(t['submittedGems']) for t in j['teams']}
    margin = sum(v if k == us else -v for k, v in sub.items())
    deaths = sum(float(c['metrics']['deaths']) for c in j['champions'] if c['team'] == us)
    kills = sum(float(c['metrics']['kills']) for c in j['champions'] if c['team'] == us)
    size = sum(1 for c in j['champions'] if c['team'] == us)
    R[(cand, opp)].append((float(j['match']['outcome'] == us), margin, deaths, kills, mp, size, side))


def line(rows):
    n = len(rows)
    w = sum(r[0] for r in rows) / n
    m = sum(r[1] for r in rows) / n
    sd = math.sqrt(sum((r[1] - m) ** 2 for r in rows) / max(1, n - 1))
    return f"{n:4d} games, wins {w:.3f} +- {math.sqrt(w * (1 - w) / n):.3f}, margin {m:+7.1f} +- {sd / math.sqrt(n):5.1f}, deaths {sum(r[2] for r in rows) / n:5.2f}, kills {sum(r[3] for r in rows) / n:5.2f}"


for (cand, opp), rows in sorted(R.items()):
    print(f'{cand} against {opp}: {line(rows)}')
    if bysize:
        for s in sorted({r[5] for r in rows}):
            print(f'    size {s}: {line([r for r in rows if r[5] == s])}')
    if bymap:
        M = collections.defaultdict(list)
        for r in rows:
            M[r[4]].append(r)
        for mp, rr in sorted(M.items(), key=lambda kv: sum(r[1] for r in kv[1]) / len(kv[1])):
            print(f"    {mp:26s} {sum(r[0] for r in rr):3.0f}/{len(rr):<3d} {sum(r[1] for r in rr) / len(rr):+8.0f}")
