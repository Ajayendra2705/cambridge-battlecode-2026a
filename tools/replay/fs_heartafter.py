# Heart of Ruin striking dashes (slot 1 cast, an enemy champion within 3 of the landing), to r1000, per side: what the
# Heart did in the same turn after the cast (basic hit on a champion, walk away / level / closer to the nearest enemy,
# nothing), over the next 5 rounds (rounds hitting a champion, rounds walking away from the nearest enemy, shield cast),
# its health at the cast, P(it dies within 10), P(an enemy within 3 of the landing dies within 10). Split by the landing:
# enemies within 3 > allies within 3 + 1 ('outnumbered') or not. --probe RUNDIR CAND: our dashes also by the bot's
# activity that round (log_rounds W lines), for local probe games. The row 'hit, then a walk' counts the dashes followed
# by a basic hit on a champion and a walk in the same turn (what the threat branch did before rz9: dash in, hit, walk home).
# usage: python -I tools/replay/fs_heartafter.py [--size N] [--probe RUNDIR CAND] DIR...
import sys, os, re, glob, zipfile, collections
sys.path.insert(0, 'tools/replay')
import decoded as D
SIZE = None; PROBE = None; args = sys.argv[1:]
while args and args[0].startswith('--'):
    if args[0] == '--size': SIZE = int(args[1]); args = args[2:]
    elif args[0] == '--probe': PROBE = (args[1], args[2]); args = args[3:]
HEART = D.NAMES.index('heart')
def p(c): return (c['x'], c['y']) if c.get('a') and 'x' in c else None
WL = {}
if PROBE:
    for path in glob.glob(os.path.join(PROBE[0], PROBE[1] + '~*.repl26a')):
        fname = os.path.basename(path); side = fname[:-len('.repl26a')].split('~')[-1][0].lower()
        st = re.sub(r'[^\x20-\x7e\n]', '', zipfile.ZipFile(path).read(f'team-{side}.stdout').decode('latin1'))
        sn = {int(m.group(1)): m.group(2) for m in re.finditer(r'^R\d+ s(\d+) (\S+) hp=', st, re.M)}
        hs = [s for s, nm in sn.items() if nm[:4] == 'hear']
        W = {}
        for m in re.finditer(r'^W (\d+) (\d+) (-?\d+) (\S+)$', st, re.M):
            if hs and int(m.group(2)) == hs[0]: W[int(m.group(1))] = m.group(4)
        WL[fname] = W
C = collections.Counter(); ng = 0
for us, res, mp, meta, rows in D.games(args):
    n = len(rows[0]['c'])
    if SIZE and n != 2 * SIZE: continue
    ng += 1
    W = WL.get(meta.get('file'), {})
    for k in range(len(rows) - 11):
        a = rows[k]
        if a['r'] > 1000: break
        for i, c in enumerate(a['c']):
            if c['ty'] != HEART or not p(c): continue
            acts = a['act'][i] if i < len(a['act']) else []
            q = next((x for x, y in enumerate(acts) if y[0] == 'cast' and y[1] == 1), None)
            if q is None: continue
            land = (acts[q][2], acts[q][3])
            ens = [(j, p(o)) for j, o in enumerate(a['c']) if p(o) and o['t'] != c['t']]
            e3 = [j for j, e in ens if D.dist(land, e) <= 3]
            if not e3: continue
            al = sum(1 for j, o in enumerate(a['c']) if j != i and p(o) and o['t'] == c['t'] and D.dist(land, p(o)) <= 3)
            band = 'outnumbered' if len(e3) > al + 1 else 'even+'
            w = D.who(c['t'], us)
            after = acts[q + 1:]
            hit = any(y[0] == 'attack' and y[-2] == 'c' and a['c'][y[-1]]['t'] != c['t'] for y in after)
            mv = [y for y in after if y[0] == 'move']
            if mv:
                d0 = min(D.dist(land, e) for j, e in ens); d1 = min(D.dist((mv[-1][3], mv[-1][4]), e) for j, e in ens)
                walk = 'away' if d1 > d0 else 'closer' if d1 < d0 else 'level'
            else: walk = 'none'
            same = ('hit+' if hit else '') + 'walk ' + walk
            hitr = away = shield = 0
            for t in range(k + 1, k + 6):
                b = rows[t]; cb = b['c'][i]
                if not p(cb): break
                ac = b['act'][i] if i < len(b['act']) else []
                hitr += bool(D.enemy_hits(b, i, n))
                shield += any(y[0] == 'cast' and y[1] == 0 for y in ac)
                mvb = [y for y in ac if y[0] == 'move']
                eb = [p(o) for o in b['c'] if p(o) and o['t'] != c['t']]
                if mvb and eb:
                    d0 = min(D.dist(p(cb), e) for e in eb); d1 = min(D.dist((mvb[-1][3], mvb[-1][4]), e) for e in eb)
                    away += d1 > d0
            hd = any(not rows[t]['c'][i]['a'] for t in range(k + 1, k + 11))
            ed = any(not rows[t]['c'][j]['a'] for j in e3 for t in range(k + 1, k + 11))
            shp = any(y[0] == 'cast' and y[1] == 0 for t in range(max(0, k - 5), k) for y in (rows[t]['act'][i] if i < len(rows[t]['act']) else []))
            keys = [(w, band), (w, 'all')]
            if hit and walk != 'none': keys.append((w, 'hit, then a walk'))
            if w == 'us' and W: keys.append((w, 'act ' + W.get(a['r'], '?')))
            for kk in keys:
                C[kk] += 1; C[kk + ('hp',)] += c.get('hp', 0) / max(1, c.get('mhp', 1)); C[kk + ('hd',)] += hd; C[kk + ('ed',)] += ed
                C[kk + ('hitr',)] += hitr; C[kk + ('away',)] += away; C[kk + ('shield',)] += shield > 0; C[kk + ('shp',)] += shp
                C[kk + ('same', same)] += 1; C[kk + ('same', same, 'hd')] += hd
print(f'{ng} games{" of team size " + str(SIZE) if SIZE else ""}, to r1000: Heart of Ruin striking dashes with an enemy champion within 3 of the landing')
for kk in sorted(set(k[:2] for k in C if len(k) >= 2 and isinstance(k[1], str) and k[0] in ('us', 'them') and len(k) == 2), key=lambda x: (x[0], x[1])):
    d = C[kk]
    if d < 5: continue
    sm = sorted(((C[kk + ('same', s)], s) for s in set(k[3] for k in C if len(k) == 4 and k[:2] == kk and k[2] == 'same')), reverse=True)
    print(f'  {kk[0]:4} {kk[1]:22} {d / ng:5.2f}/g  hp {C[kk + ("hp",)] / d:.2f}  Heart dies {C[kk + ("hd",)] / d:.2f}  enemy dies {C[kk + ("ed",)] / d:.2f}'
          f'  next 5: hit-rounds {C[kk + ("hitr",)] / d:.2f} away-steps {C[kk + ("away",)] / d:.2f} shield {C[kk + ("shield",)] / d:.2f}  shield in the 5 before {C[kk + ("shp",)] / d:.2f}')
    print('       same turn: ' + ', '.join(f'{s} {v / d:.2f} (dies {C[kk + ("same", s, "hd")] / max(1, v):.2f})' for v, s in sm[:5]))
