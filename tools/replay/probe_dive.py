# Join a log_rounds probe's W lines (rz11l) with its decoded local games: our Vendetta dives (slot 1 cast landing within 1 of an enemy
# champion) by the activity of that turn and the numbers margin at the landing (enemies within 3 minus allies within 3
# plus her), with P(she dies within 10) and P(a target dies within 10).
# usage: python -I tools/replay/probe_dive.py RUNDIR CAND FIGHTSDIR [TYPE]
import sys, os, re, glob, zipfile, collections
sys.path.insert(0, 'tools/replay')
import decoded as D
run, cand, fdir = sys.argv[1:4]
TY = D.NAMES.index(sys.argv[4] if len(sys.argv) > 4 else 'vendetta')
games = {}
for us, res, mp, meta, rows in D.games([fdir]): games[meta['file']] = (us, res, mp, rows)
E = collections.Counter(); ng = 0
def pos(c): return (c['x'], c['y'])
for path in sorted(glob.glob(os.path.join(run, cand + '~*.repl26a'))):
    fname = os.path.basename(path)
    if fname not in games: continue
    us, res, mp, rows = games[fname]
    if len(rows[0]['c']) != 10: continue
    side = fname[:-len('.repl26a')].split('~')[-1][0].lower()
    st = re.sub(r'[^\x20-\x7e\n]', '', zipfile.ZipFile(path).read(f'team-{side}.stdout').decode('latin1'))
    slot_name = {}
    for m in re.finditer(r'^R\d+ s(\d+) (\S+) hp=', st, re.M): slot_name[int(m.group(1))] = m.group(2)
    W = {}
    for m in re.finditer(r'^W (\d+) (\d+) (-?\d+) (\S+)$', st, re.M): W[(int(m.group(1)), int(m.group(2)))] = m.group(4)
    idx_slot = {}
    for i, c in enumerate(rows[0]['c']):
        if c['t'] != us: continue
        for s, nm in slot_name.items():
            if nm[:4] == D.NAMES[c['ty']][:4]: idx_slot[i] = s
    ng += 1
    deaths = {k: [r for r in range(1, len(rows)) if not rows[r]['c'][k]['a'] and rows[r - 1]['c'][k]['a']] for k in range(10)}
    for r in range(len(rows)):
        if rows[r]['r'] > 1000: break
        row = rows[r]
        for i, c in enumerate(row['c']):
            if c['ty'] != TY or not c['a'] or 'x' not in c or i >= len(row['act']): continue
            for x in row['act'][i]:
                if x[0] != 'cast' or x[1] != 1 or len(x) < 4: continue
                land = (x[2], x[3])
                near1 = [k for k, e in enumerate(row['c']) if e['a'] and 'x' in e and e['t'] != c['t'] and D.dist(land, pos(e)) <= 1]
                if not near1: continue
                en3 = sum(1 for e in row['c'] if e['a'] and 'x' in e and e['t'] != c['t'] and D.dist(land, pos(e)) <= 3)
                al3 = sum(1 for j, e in enumerate(row['c']) if j != i and e['a'] and 'x' in e and e['t'] == c['t'] and D.dist(land, pos(e)) <= 3)
                dd = en3 - al3 - 1; m = 'd<=-1' if dd <= -1 else 'd=0' if dd == 0 else 'd>=1'
                act = W.get((row['r'], idx_slot.get(i, -1)), '?') if c['t'] == us else 'opp'
                for key in ((act, m), ('ALL ours' if c['t'] == us else 'ALL opp', m)):
                    E[key] += 1; E[key + ('die',)] += any(0 < dr - r <= 10 for dr in deaths[i])
                    E[key + ('kill',)] += any(any(0 < dr - r <= 10 for dr in deaths[k]) for k in near1)
                break
print(f'{ng} 5-a-side games: dives by activity and margin, per game (P she dies 10 / P a target dies 10)')
for act in sorted(set(k[0] for k in E if len(k) == 2), key=lambda a: -sum(E[(a, m)] for m in ('d<=-1', 'd=0', 'd>=1'))):
    print(f'  {act:12} ' + '   '.join(f"{m} {E[(act, m)] / max(1, ng):.2f} ({E[(act, m, 'die')] / max(1, E[(act, m)]):.2f}/{E[(act, m, 'kill')] / max(1, E[(act, m)]):.2f})" for m in ('d<=-1', 'd=0', 'd>=1')))
