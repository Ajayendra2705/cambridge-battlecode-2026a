# Join a log_rounds probe's W lines with its decoded local games: our champions' rounds with an enemy champion (off its
# spawn) within the champion's basic reach at the round start, that did not hit an enemy champion: the bot's activity,
# by type, per game; plus the hit share per activity. --brawl: only rounds with 3+ of each side within 6 of the champion.
# usage: python -I tools/replay/probe_inreach.py RUNDIR CAND FIGHTSDIR [--upto R] [--brawl]
import sys, os, re, glob, zipfile, collections
sys.path.insert(0, 'tools/replay')
import decoded as D
run, cand, fdir = sys.argv[1:4]
UPTO = 1000; BRAWL = '--brawl' in sys.argv
a = sys.argv[4:]
for i, x in enumerate(a):
    if x == '--upto': UPTO = int(a[i + 1])
games = {}
for us, res, mp, meta, rows in D.games([fdir]):
    games[meta['file']] = (us, res, mp, rows)
E = collections.Counter(); ng = 0
for path in sorted(glob.glob(os.path.join(run, cand + '~*.repl26a'))):
    fname = os.path.basename(path)
    if fname not in games: continue
    us, res, mp, rows = games[fname]
    side = fname[:-len('.repl26a')].split('~')[-1][0].lower()
    st = re.sub(r'[^\x20-\x7e\n]', '', zipfile.ZipFile(path).read(f'team-{side}.stdout').decode('latin1'))
    slot_name = {}
    for m in re.finditer(r'^R\d+ s(\d+) (\S+) hp=', st, re.M): slot_name[int(m.group(1))] = m.group(2)
    W = {}
    for m in re.finditer(r'^W (\d+) (\d+) (-?\d+) (\S+)$', st, re.M): W[(int(m.group(1)), int(m.group(2)))] = m.group(4)
    n = len(rows[0]['c'])
    sp = {t: set((c['x'], c['y']) for c in rows[0]['c'] if c['t'] == t and 'x' in c) for t in (0, 1)}
    idx_slot = {}
    for i, c in enumerate(rows[0]['c']):
        if c['t'] != us: continue
        for s, nm in slot_name.items():
            if nm[:4] == D.NAMES[c['ty']][:4]: idx_slot[i] = s
    ng += 1
    for k in range(len(rows) - 1):
        ra = rows[k]
        if ra['r'] > UPTO: break
        for i in range(n):
            c = ra['c'][i]
            if c['t'] != us or not c['a'] or 'x' not in c or i not in idx_slot: continue
            q = (c['x'], c['y']); rg = D.RANGE.get(c['ty'], 1)
            ens = [D.dist(q, (o['x'], o['y'])) for o in ra['c'] if o['t'] != c['t'] and o['a'] and 'x' in o and (o['x'], o['y']) not in sp[o['t']]]
            if not ens or min(ens) > rg: continue
            if BRAWL:
                own = sum(1 for o in ra['c'] if o['t'] == c['t'] and o['a'] and 'x' in o and D.dist(q, (o['x'], o['y'])) <= 6)
                if own < 3 or sum(1 for d in ens if d <= 6) < 3: continue
            hit = bool(D.enemy_hits(ra, i, n))
            act = W.get((ra['r'], idx_slot[i]), '?')
            ty = D.NAMES[c['ty']]
            for key in (('ALL', act), (ty, act)):
                E[key] += 1; E[key + ('hit',)] += hit
            E[('ALL', '*')] += 1; E[('ALL', '*', 'hit')] += hit; E[(ty, '*')] += 1; E[(ty, '*', 'hit')] += hit
print(f'{ng} games to r{UPTO}{" (brawl rounds)" if BRAWL else ""}: our rounds with an enemy champion in basic reach; per game: rounds, hit share; misses = rounds without a hit')
for ty in ['ALL'] + sorted(set(k[0] for k in E if k[0] != 'ALL')):
    tot = E[(ty, '*')]
    if not tot: continue
    print(f'  {ty:9} {tot / ng:6.1f}/g hit {E[(ty, "*", "hit")] / tot:.2f}; misses by activity: ' + ', '.join(
        f'{act} {(E[(ty, act)] - E[(ty, act, "hit")]) / ng:.1f} (hit {E[(ty, act, "hit")] / max(1, E[(ty, act)]):.2f})'
        for act in sorted(set(k[1] for k in E if k[0] == ty and len(k) == 2 and k[1] != '*'), key=lambda s: -(E[(ty, s)] - E[(ty, s, 'hit')]))[:9]))
