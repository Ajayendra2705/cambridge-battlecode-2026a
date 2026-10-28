# Join a log_rounds probe's W lines with its decoded local games: our Vesper's rounds with an enemy champion (off its
# spawn) within her basic reach (3) at the round start, by what she did (shot a champion, shot + dash, dash only, walked
# closer / level / away from the nearest enemy, hit a camp, cast only, nothing) and the bot's activity that round.
# Also the same for the opponents' Vesper (no activity: column 'opp').
# usage: python -I tools/replay/probe_vesper.py RUNDIR CAND FIGHTSDIR [--upto R]
import sys, os, re, glob, zipfile, collections
sys.path.insert(0, 'tools/replay')
import decoded as D
run, cand, fdir = sys.argv[1:4]
UPTO = 1000
a = sys.argv[4:]
for i, x in enumerate(a):
    if x == '--upto': UPTO = int(a[i + 1])
games = {}
for us, res, mp, meta, rows in D.games([fdir]):
    games[meta['file']] = (us, res, mp, rows)
E = collections.Counter(); ng = 0
VES = D.NAMES.index('vesper')
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
            if c['ty'] != VES or not c['a'] or 'x' not in c: continue
            q = (c['x'], c['y'])
            ens = [(D.dist(q, (o['x'], o['y'])), j) for j, o in enumerate(ra['c']) if o['t'] != c['t'] and o['a'] and 'x' in o and (o['x'], o['y']) not in sp[o['t']]]
            if not ens: continue
            d0, j0 = min(ens)
            if d0 > 3: continue
            acts = ra['act'][i] if i < len(ra['act']) else []
            dash = any(x[0] == 'cast' and x[1] == 1 and len(x) == 4 for x in acts)
            if D.enemy_hits(ra, i, n): kind = 'shot+dash' if dash else 'shot'
            elif dash: kind = 'dash only'
            else:
                mv = [x for x in acts if x[0] == 'move']
                if mv:
                    o = ra['c'][j0]; d1 = D.dist((mv[-1][3], mv[-1][4]), (o['x'], o['y']))
                    kind = 'walk closer' if d1 < d0 else 'walk away' if d1 > d0 else 'walk level'
                elif D.camp_hits(ra, i): kind = 'camp'
                elif any(x[0] == 'cast' for x in acts): kind = 'cast only'
                else: kind = 'nothing'
            if c['t'] == us:
                act = W.get((ra['r'], idx_slot.get(i, -1)), '?')
            else:
                act = 'opp'
            hp = 'hp<50' if c.get('hp', 0) < 0.5 * c.get('mhp', 1) else 'hp50+'
            for key in ((act,), ('ALL ours' if c['t'] == us else 'ALL opp',)):
                E[key + (kind,)] += 1; E[key] += 1
kinds = ('shot', 'shot+dash', 'dash only', 'walk closer', 'walk level', 'walk away', 'camp', 'cast only', 'nothing')
print(f'{ng} games to r{UPTO}: Vesper rounds with an enemy champion within 3 (off its spawn), per game, by activity')
print(f'  {"activity":12} {"per g":>6}  ' + '  '.join(f'{k:>11}' for k in kinds))
for act in sorted(set(k[0] for k in E if len(k) == 1), key=lambda s: -E[(s,)]):
    tot = E[(act,)]
    if tot / max(1, ng) < 0.2: continue
    print(f'  {act:12} {tot / ng:6.2f}  ' + '  '.join(f'{E[(act, k)] / tot:11.2f}' for k in kinds))
