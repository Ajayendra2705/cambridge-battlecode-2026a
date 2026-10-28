"""Read the h3bql probe's bank-batch lines from a local multi.py --keep run (h3, 10-28).

usage: python -I tools/helper3/h3_bqprobe.py RUNDIR [PREFIX]   (PREFIX default exp.h3bql)

The probe (`bots/exp/h3bql`, never shipped) prints, every 10 rounds while a champion carries 10+ gems and the bank
stage is reached: `BQ r<round> s<slot> g<gems> b<batch> c<collection rate x1000> tau<trip> mh<m*h x1e5>
lam<lambda x1e4> alt<altar steps> go<1 if it banks now>`. Per map: lines, the batch's quartiles, the bag's quartiles,
the share of lines carrying 40+ gems while still under the batch (go 0), and the medians of c, tau and m*h.
"""
import collections, glob, os, re, statistics, sys, zipfile

run = sys.argv[1]
prefix = sys.argv[2] if len(sys.argv) > 2 else 'exp.h3bql'
P = re.compile(r'^BQ r(\d+) s(\d+) g(\d+) b(\d+) c(\d+) tau(\d+) mh(\d+) lam(\d+) alt(-?\d+) go(\d)')
M = collections.defaultdict(list)
for path in sorted(glob.glob(os.path.join(run, prefix + '~*.repl26a'))):
    parts = os.path.basename(path)[:-len('.repl26a')].split('~')
    team = parts[-1][0].lower()
    text = re.sub(r'[^\x20-\x7e\n]', '', zipfile.ZipFile(path).read(f'team-{team}.stdout').decode('latin1'))
    for line in text.splitlines():
        m = P.match(line)
        if m: M[parts[2]].append(tuple(int(x) for x in m.groups()))


def qs(v):
    if len(v) < 4: return 'n/a'
    q = statistics.quantiles(v, n=4)
    return f'{q[0]:.0f}/{q[1]:.0f}/{q[2]:.0f}'


print(f'{"map":22} lines  batch q1/med/q3  bag q1/med/q3  40+ and holding  c med  tau med  m*h med (x1e5)')
for mp in sorted(M) + ['all']:
    rows = [r for k in M for r in M[k]] if mp == 'all' else M[mp]
    if not rows: continue
    b = [r[3] for r in rows]; g = [r[2] for r in rows]
    hold40 = sum(1 for r in rows if r[2] >= 40 and r[9] == 0) / len(rows)
    print(f'{mp:22} {len(rows):5}  {qs(b):>15}  {qs(g):>13}  {hold40:15.0%}  {statistics.median(r[4] for r in rows):5.0f}'
          f'  {statistics.median(r[5] for r in rows):7.0f}  {statistics.median(r[6] for r in rows):7.0f}')
