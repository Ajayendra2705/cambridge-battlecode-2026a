# Join a log_rounds probe's W lines ("W round slot target activity") with its decoded local games: our champions'
# contact rounds (nearest enemy champion within reach + 1 at the round start; melee at distance 2 by default) by what
# they did (hit champion, move closer / level / away, hit camp only, nothing) and the bot's activity that round.
# usage: python -I tools/replay/probe_contact.py RUNDIR CAND FIGHTSDIR [--upto R] [--dist D]
import sys, os, re, glob, zipfile, collections
sys.path.insert(0, 'tools/replay')
import decoded as D
run, cand, fdir = sys.argv[1:4]
UPTO = 300; DIST = 2; TYPE = None
a = sys.argv[4:]
for i, x in enumerate(a):
    if x == '--upto': UPTO = int(a[i + 1])
    if x == '--dist': DIST = int(a[i + 1])
    if x == '--type': TYPE = a[i + 1]
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
    idx_slot = {}
    for i, c in enumerate(rows[0]['c']):
        if c['t'] != us: continue
        for s, nm in slot_name.items():
            if nm[:4] == D.NAMES[c['ty']][:4]: idx_slot[i] = s
    ng += 1
    for k in range(len(rows) - 1):
        ra, rb = rows[k], rows[k + 1]
        if ra['r'] > UPTO: break
        for i in range(n):
            c = ra['c'][i]
            if c['t'] != us or not c['a'] or 'x' not in c or i not in idx_slot: continue
            q = (c['x'], c['y']); rg = D.RANGE.get(c['ty'], 1)
            ens = [(D.dist(q, (o['x'], o['y'])), j) for j, o in enumerate(ra['c']) if o['t'] != c['t'] and o['a'] and 'x' in o]
            if not ens: continue
            d0, j0 = min(ens)
            if (TYPE is None and rg != 1) or (TYPE is not None and D.NAMES[c['ty']] != TYPE) or d0 != DIST: continue
            acts = ra['act'][i] if i < len(ra['act']) else []
            if D.enemy_hits(ra, i, n): kind = 'hit' + ('+dash' if any(x[0] == 'cast' and x[1] == 1 and len(x) == 4 for x in acts) else '')
            else:
                mv = [x for x in acts if x[0] == 'move']
                if mv:
                    o = ra['c'][j0]; d1 = D.dist((mv[-1][3], mv[-1][4]), (o['x'], o['y']))
                    kind = 'closer' if d1 < d0 else 'away' if d1 > d0 else 'level'
                elif D.camp_hits(ra, i): kind = 'camp'
                else: kind = 'nothing'
            act = W.get((ra['r'], idx_slot[i]), '?')
            E[(act, kind)] += 1; E[(act,)] += 1; E[('ALL', kind)] += 1; E[('ALL',)] += 1
kinds = ('hit', 'hit+dash', 'closer', 'level', 'away', 'camp', 'nothing')
print(f'{ng} games to r{UPTO}: our melee champions with the nearest enemy champion at distance {DIST}, by activity; per game, shares')
for act in sorted(set(k[0] for k in E if len(k) == 1), key=lambda s: -E[(s,)]):
    t = E[(act,)]
    print(f'  {act:12} {t / max(1, ng):6.2f}/g  ' + '  '.join(f'{kd} {E[(act, kd)] / t:.2f}' for kd in kinds) + f'   level/g {E[(act, "level")] / max(1, ng):.2f}')
