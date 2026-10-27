# Death factors (massacre postmortem): every champion death to r1000, split by game class (massacre: our deaths minus theirs by r1000 is
# 6 or more; mixed 3-5; even 2 or less), with the factors around each death, us vs them. Our deaths also get the bot's
# last activity from its D line (replay stdout).
# usage: [UPTO=300] python -I tools/replay/deathfactors.py RUN...  (UPTO: factors only for deaths by that round)   (RUN = name under data/fights and data/replays/platform, e.g. cw1_bvp_bvp)
import sys, os, re, zipfile, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import decoded as D

R = 1000
UPTO = int(os.environ.get('UPTO', '1000'))  # factors only for deaths by this round (classes still by r1000)
F = collections.Counter()   # (class, side, factor, value) -> deaths
G = collections.Counter()   # (class, key) -> games / sums


def dlines(run, fname, us):
    """Our D lines of one game: list of (last acted round, hp, activity, enemies listed)."""
    p = os.path.join('data', 'replays', 'platform', run, fname)
    if not os.path.exists(p): return None
    try:
        z = zipfile.ZipFile(p)
        name = next(n for n in z.namelist() if n.endswith('.stdout'))
        st = z.read(name).decode('utf8', 'replace').replace('\0', '')
    except Exception:
        return None
    out = []
    for m in re.finditer(r'^D(\d+) s(\d+) r(\d+) hp=(\S+) (\S+) en:(.*)$', st, re.M):
        out.append((int(m.group(3)), float(m.group(4)), m.group(5), len(re.findall('@', m.group(6)))))
    return out


def phase(r): return '0-150' if r <= 150 else '151-300' if r <= 300 else '301-600' if r <= 600 else '601-1000'


for run in sys.argv[1:]:
    for us, res, mp, meta, rows in D.games([os.path.join('data', 'fights', run)]):
        n = len(rows[0]['c'])
        start = {t: [(o['x'], o['y']) for o in rows[0]['c'] if 'x' in o and o['t'] == t] for t in (0, 1)}
        if not start[0] or not start[1]: continue
        home = lambda t, q: min(D.dist(q, s) for s in start[t])
        def off(o): return o['a'] and 'x' in o and home(o['t'], (o['x'], o['y'])) > 1
        # Deaths to r1000.
        deaths = []
        for k in range(len(rows) - 1):
            if rows[k + 1]['r'] > R: break
            for i in range(n):
                if rows[k]['c'][i]['a'] and not rows[k + 1]['c'][i]['a']: deaths.append((k, i))
        du = sum(1 for k, i in deaths if rows[k]['c'][i]['t'] == us); dt = len(deaths) - du
        cls = 'massacre' if du - dt >= 6 else 'mixed' if du - dt >= 3 else 'even'
        won = res == 'win'
        G[(cls, 'games')] += 1; G[(cls, 'wins')] += won; G[(cls, 'size', n // 2)] += 1
        G[(cls, 'map', mp)] += 1
        for t0 in (300, 600):
            G[(cls, 'diff', t0)] += sum(1 for k, i in deaths if rows[k + 1]['r'] <= t0 and rows[k]['c'][i]['t'] == us) \
                - sum(1 for k, i in deaths if rows[k + 1]['r'] <= t0 and rows[k]['c'][i]['t'] != us)
        # Team gold (unspent + 30 per shard) at r300 / r600.
        for t0 in (300, 600):
            row = next((r for r in rows if r['r'] >= t0), None)
            if row:
                for t in (0, 1):
                    gold = sum(D.gold_held(meta, c) for c in row['c'] if c['t'] == t)
                    G[(cls, 'gold', t0, D.who(t, us))] += gold
                G[(cls, 'goldn', t0)] += 1
        dl = dlines(run, meta.get('file', ''), us) or []
        used = set()
        respawns = [[] for _ in range(n)]
        for k in range(len(rows) - 1):
            for i in range(n):
                if not rows[k]['c'][i]['a'] and rows[k + 1]['c'][i]['a']: respawns[i].append(rows[k + 1]['r'])
        team_deaths = collections.defaultdict(list)  # side -> [(round, pos)]
        for k, i in sorted(deaths):
            c = rows[k]['c'][i]; t = c['t']; w = D.who(t, us)
            if rows[k + 1]['r'] > UPTO: continue
            if 'x' not in c: continue
            p = (c['x'], c['y']); r = rows[k + 1]['r']
            key = lambda f, v: F.__setitem__((cls, w, f, v), F[(cls, w, f, v)] + 1)
            key('all', 'deaths')
            key('phase', phase(r))
            hd = home(t, p); key('home dist', '<=10' if hd <= 10 else '11-20' if hd <= 20 else '>20')
            de = home(1 - t, p); key('region', 'own half' if hd < de - 3 else 'enemy half' if de < hd - 3 else 'middle')
            en6 = [j for j in range(n) if rows[k]['c'][j]['t'] != t and off(rows[k]['c'][j]) and D.dist(p, (rows[k]['c'][j]['x'], rows[k]['c'][j]['y'])) <= 6]
            al6 = [j for j in range(n) if j != i and rows[k]['c'][j]['t'] == t and off(rows[k]['c'][j]) and D.dist(p, (rows[k]['c'][j]['x'], rows[k]['c'][j]['y'])) <= 6]
            nd = len(al6) + 1 - len(en6)
            key('numbers at death', 'outnumbered 2+' if nd <= -2 else 'outnumbered 1' if nd == -1 else 'even' if nd == 0 else 'outnumbering')
            # Killers: enemy champions that hit the victim in its last 10 rounds.
            killers = set()
            for kk in range(max(0, k - 9), k + 1):
                for j in range(n):
                    if rows[kk]['c'][j]['t'] != t and any(x[-1] == i for x in D.enemy_hits(rows[kk], j, n)): killers.add(j)
            key('killers', 'none (camp?)' if not killers else '1' if len(killers) == 1 else '2' if len(killers) == 2 else '3+')
            for j in killers: key('killer type', D.NAMES[rows[k]['c'][j]['ty']])
            key('victim type', D.NAMES[c['ty']])
            # Fatal contact: back from the death while an enemy champion is within 6.
            k0 = k
            while k0 > 0 and k - k0 < 60:
                pr = rows[k0 - 1]; me = pr['c'][i]
                if not (me['a'] and 'x' in me): break
                q = (me['x'], me['y'])
                if not any(pr['c'][j]['t'] != t and off(pr['c'][j]) and D.dist(q, (pr['c'][j]['x'], pr['c'][j]['y'])) <= 6 for j in range(n)): break
                k0 -= 1
            dur = k - k0 + 1
            key('contact length', '<=3' if dur <= 3 else '4-10' if dur <= 10 else '11-30' if dur <= 30 else '31+')
            s0 = rows[k0]['c'][i]
            hf = s0.get('hp', 0) / max(1, s0.get('mhp', 1))
            key('hp at contact', '80%+' if hf >= 0.8 else '50-80%' if hf >= 0.5 else '<50%')
            q0 = (s0['x'], s0['y']) if 'x' in s0 else p
            en0 = sum(1 for j in range(n) if rows[k0]['c'][j]['t'] != t and off(rows[k0]['c'][j]) and D.dist(q0, (rows[k0]['c'][j]['x'], rows[k0]['c'][j]['y'])) <= 6)
            al0 = sum(1 for j in range(n) if j != i and rows[k0]['c'][j]['t'] == t and off(rows[k0]['c'][j]) and D.dist(q0, (rows[k0]['c'][j]['x'], rows[k0]['c'][j]['y'])) <= 6)
            n0 = al0 + 1 - en0
            key('numbers at contact', 'outnumbered 2+' if n0 <= -2 else 'outnumbered 1' if n0 == -1 else 'even' if n0 == 0 else 'outnumbering')
            # Before the contact (5 rounds).
            act = 'other'
            if k0 >= 5:
                pre = rows[k0 - 5:k0]
                if any(x[0] == 'tribute' for r0 in pre for x in (r0['act'][i] if i < len(r0['act']) else [])): act = 'banking'
                elif any(D.camp_hits(r0, i) for r0 in pre): act = 'farming camps'
                else:
                    a0 = pre[0]['c'][i]
                    if a0['a'] and 'x' in a0:
                        h0, h1 = home(t, (a0['x'], a0['y'])), home(t, q0)
                        if a0.get('x') == s0.get('x') and a0.get('y') == s0.get('y'): act = 'standing'
                        elif h1 <= h0 - 2: act = 'walking home'
                        elif h1 >= h0 + 2: act = 'walking out'
                        else: act = 'walking across'
                    else: act = 'just respawned'
            key('before contact', act)
            # The victim's hits on champions during the contact, and allies' hits on its killers.
            vh = sum(1 for kk in range(k0, k + 1) if D.enemy_hits(rows[kk], i, n))
            key('victim hit back', 'never' if vh == 0 else '1-2 rounds' if vh <= 2 else '3+ rounds')
            ah = any(rows[kk]['c'][j]['t'] == t and j != i and any(x[-1] in killers for x in D.enemy_hits(rows[kk], j, n))
                     for kk in range(k0, k + 1) for j in range(n))
            key('an ally hit a killer', 'yes' if ah else 'no')
            key('allies within 6 at death', str(min(len(al6), 2)) + ('+' if len(al6) >= 2 else ''))
            # Chains and respawn walks.
            chain = any(r - r1 <= 60 and D.dist(p, q1) <= 8 for r1, q1 in team_deaths[t])
            key('teammate died within 8 tiles, 60 rounds before', 'yes' if chain else 'no')
            team_deaths[t].append((r, p))
            prior = [x for x in respawns[i] if x <= rows[k]['r']]
            since = r - prior[-1] if prior else None
            key('since respawn', 'first life' if since is None else '<=40' if since <= 40 else '41-120' if since <= 120 else '121+')
            # Numbers at the first enemy hit on the victim in the contact, and the most enemies within 6 during it.
            fh = next((kk for kk in range(k0, k + 1) if any(any(x[-1] == i for x in D.enemy_hits(rows[kk], j, n)) for j in range(n) if rows[kk]['c'][j]['t'] != t)), None)
            if fh is not None and 'x' in rows[fh]['c'][i]:
                qf = (rows[fh]['c'][i]['x'], rows[fh]['c'][i]['y'])
                ef = sum(1 for j in range(n) if rows[fh]['c'][j]['t'] != t and off(rows[fh]['c'][j]) and D.dist(qf, (rows[fh]['c'][j]['x'], rows[fh]['c'][j]['y'])) <= 6)
                af = sum(1 for j in range(n) if j != i and rows[fh]['c'][j]['t'] == t and off(rows[fh]['c'][j]) and D.dist(qf, (rows[fh]['c'][j]['x'], rows[fh]['c'][j]['y'])) <= 6)
                nf = af + 1 - ef
                key('numbers at first hit', 'outnumbered 2+' if nf <= -2 else 'outnumbered 1' if nf == -1 else 'even' if nf == 0 else 'outnumbering')
                key('first hit to death', '<=3' if k - fh <= 2 else '4-10' if k - fh <= 9 else '11+')
            else:
                key('numbers at first hit', 'no champion hit')
            emax = max(sum(1 for j in range(n) if rows[kk]['c'][j]['t'] != t and off(rows[kk]['c'][j]) and 'x' in rows[kk]['c'][i]
                           and D.dist((rows[kk]['c'][i]['x'], rows[kk]['c'][i]['y']), (rows[kk]['c'][j]['x'], rows[kk]['c'][j]['y'])) <= 6) for kk in range(k0, k + 1))
            key('most enemies within 6 in contact', str(min(emax, 4)) + ('+' if emax >= 4 else ''))
            # Killer between the victim and its home at the contact start, and progress home over the contact.
            kh = [home(t, (rows[k0]['c'][j]['x'], rows[k0]['c'][j]['y'])) for j in killers if 'x' in rows[k0]['c'][j] and rows[k0]['c'][j]['a']]
            hv = home(t, q0)
            key('a killer nearer our home than the victim at contact', 'yes' if kh and min(kh) < hv else 'no' if kh else 'killer not in view')
            prog = hv - hd
            key('home distance gained over the contact', '<=0' if prog <= 0 else '1-4' if prog <= 4 else '5+')
            g = c.get('g', 0)
            key('bag', '0' if g == 0 else '1-29' if g < 30 else '30+')
            F[(cls, w, 'gems lost', 'sum')] += g
            # Warning: rounds from the first round (last 30) the victim saw one of its killers to the death.
            warn = None
            for kk in range(max(0, k - 30), k + 1):
                v = rows[kk].get('vis', [])
                if i < len(v) and any(j in killers for j in v[i]): warn = k - kk; break
            key('saw a killer first', 'not seen' if warn is None else '<=3 rounds before' if warn <= 3 else '4-10' if warn <= 10 else '11-30')
            # Our D line (activity label at death).
            if w == 'us':
                best = None
                for idx, (lr, hp, a, ne) in enumerate(dl):
                    if idx in used or abs(lr - rows[k]['r']) > 2: continue
                    sc = abs(lr - rows[k]['r']) * 1000 + abs(hp - c.get('hp', 0))
                    if best is None or sc < best[0]: best = (sc, idx, a)
                if best: used.add(best[1]); key('bot activity at death', best[2])
                else: key('bot activity at death', '(no D line)')

order = ('massacre', 'mixed', 'even')
print('Games by class (our deaths minus theirs by r1000): games, wins, mean death difference by r300 / r600, team gold us/them at r300, r600')
for cls in order:
    g = max(1, G[(cls, 'games')])
    gold = '  '.join(f"r{t0} {G[(cls, 'gold', t0, 'us')] / max(1, G[(cls, 'goldn', t0)]):.0f}/{G[(cls, 'gold', t0, 'them')] / max(1, G[(cls, 'goldn', t0)]):.0f}" for t0 in (300, 600))
    sizes = ' '.join(f"{s}-pick {G[(cls, 'size', s)]}" for s in (3, 4, 5))
    print(f"  {cls:8} {G[(cls, 'games')]:3} games, {G[(cls, 'wins')]:2} wins; diff r300 {G[(cls, 'diff', 300)] / g:+.1f} r600 {G[(cls, 'diff', 600)] / g:+.1f}; {gold}; {sizes}")
allmaps = collections.Counter(); mass = collections.Counter()
for k, v in G.items():
    if k[1] == 'map': allmaps[k[2]] += v; mass[k[2]] += v if k[0] == 'massacre' else 0
print('  massacre maps (massacres / games): ' + ', '.join(f'{m} {mass[m]}/{allmaps[m]}' for m, c in mass.most_common(16) if c))
factors = []
for k in F:
    if k[2] not in factors: factors.append(k[2])
print('\nDeaths per game by factor (to r1000). Columns: massacre us | massacre them | even us | even them  (share of that column\'s deaths)')
for f in factors:
    if f in ('all', 'gems lost'): continue
    vals = sorted({k[3] for k in F if k[2] == f}, key=lambda v: -sum(F[(c, w, f, v)] for c in order for w in ('us', 'them')))
    print(f'  {f}:')
    for v in vals[:12]:
        cells = []
        for cls, w in (('massacre', 'us'), ('massacre', 'them'), ('even', 'us'), ('even', 'them')):
            g = max(1, G[(cls, 'games')]); tot = max(1, F[(cls, w, 'all', 'deaths')])
            cells.append(f"{F[(cls, w, f, v)] / g:5.2f} ({F[(cls, w, f, v)] / tot:4.0%})")
        print(f'    {v:44} ' + ' | '.join(cells))
for cls in order:
    g = max(1, G[(cls, 'games')])
    print(f"  {cls}: deaths us {F[(cls, 'us', 'all', 'deaths')] / g:.2f} them {F[(cls, 'them', 'all', 'deaths')] / g:.2f}; gems lost on death us {F[(cls, 'us', 'gems lost', 'sum')] / g:.0f} them {F[(cls, 'them', 'gems lost', 'sum')] / g:.0f}")
