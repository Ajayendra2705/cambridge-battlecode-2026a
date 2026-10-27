# Damage postmortem, to r1000, per champion type and side. Champion damage (target health lost, split among that round's
# hitters) = contact rounds x hit share x damage per hit round, where a contact round has an enemy champion (off spawn)
# within the champion's reach + 1. In contact rounds without a champion hit: what it did instead (hit a camp, moved,
# cast elsewhere, nothing). Damage per hit round against main-stat shards held (emblem = 5). Damage by phase, by numbers
# (allies incl. self minus enemies within 6), and the share of damage on champions that died within 10 rounds.
# usage: python -I tools/replay/damage.py DIR...
import sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import decoded as D
FOCUS = {'cassi', 'stellar', 'prism', 'ren', 'willow', 'heart', 'marcella'}  # bots/main shop.h uses_focus
A = collections.defaultdict(collections.Counter); G = collections.Counter(); ng = 0
for us, res, mp, meta, rows in D.games(sys.argv[1:]):
    ng += 1; n = len(rows[0]['c'])
    start = {t: [(o['x'], o['y']) for o in rows[0]['c'] if 'x' in o and o['t'] == t] for t in (0, 1)}
    if not start[0] or not start[1]: continue
    def off(o): return o['a'] and 'x' in o and min(D.dist((o['x'], o['y']), q) for q in start[o['t']]) > 1
    for c in rows[0]['c']: G[(D.who(c['t'], us), D.NAMES[c['ty']])] += 1
    names = {}
    for k, (a, b) in enumerate(zip(rows, rows[1:])):
        if b['r'] > 1000: break
        targets = collections.defaultdict(list)
        for i in range(n):
            for x in D.enemy_hits(a, i, n): targets[x[-1]].append(i)
        dmg_by = collections.Counter()
        for t, hitters in targets.items():
            loss = max(0, a['c'][t].get('hp', 0) - (b['c'][t].get('hp', 0) if b['c'][t]['a'] else 0))
            died = any(not rows[kk]['c'][t]['a'] for kk in range(k + 1, min(len(rows), k + 11)))
            for i in hitters:
                dmg_by[i] += loss / len(hitters)
                if died: A[(D.who(a['c'][i]['t'], us), D.NAMES[a['c'][i]['ty']])]['dmg_kill'] += loss / len(hitters)
        ph = '0-300' if a['r'] <= 300 else '301-600' if a['r'] <= 600 else '601-1000'
        for i in range(n):
            c = a['c'][i]
            if not off(c): continue
            ty = D.NAMES[c['ty']]; w = D.who(c['t'], us); C = A[(w, ty)]
            p = (c['x'], c['y']); rng = D.RANGE.get(c['ty'], 1)
            C['alive'] += 1; C['dmg'] += dmg_by[i]; C['dmg ' + ph] += dmg_by[i]
            ens = [(D.dist(p, (a['c'][j]['x'], a['c'][j]['y'])), j) for j in range(n) if a['c'][j]['t'] != c['t'] and off(a['c'][j])]
            if not ens: continue
            dn = min(ens)[0]
            acts = a['act'][i] if i < len(a['act']) else []
            hitc = bool(D.enemy_hits(a, i, n))
            if hitc:
                C['hit rounds'] += 1; C['hit dmg'] += dmg_by[i]
                if any(x[0] == 'cast' for x in D.enemy_hits(a, i, n)): C['cast hit rounds'] += 1
                # Main-stat shards held.
                sh = 0
                for idx, cnt in c.get('it', []):
                    nm = D.item_name(meta, idx)
                    stat = nm.split(' ')[0].split('_')[-1]; kind = nm.split(' ')[1]
                    if stat == ('focus' if ty in FOCUS else 'str') and not nm.startswith('greed'): sh += cnt * (5 if kind == 'emblem' else 1)
                C['shards'] += sh
            if dn > rng + 1: continue
            C['contact'] += 1; C['contact ' + ph] += 1
            if hitc: C['contact hit'] += 1
            else:
                kinds = {x[0] for x in acts}
                inreach = dn <= rng
                if any(x[0] in ('attack', 'cast') and len(x) >= 5 and x[-2] == 'm' for x in acts): why = 'hit a camp'
                elif 'cast' in kinds: why = 'cast (no champion hit)'
                elif 'move' in kinds and inreach: why = 'moved, enemy in reach'
                elif 'move' in kinds: why = 'moved, enemy at reach+1'
                elif 'tribute' in kinds: why = 'tribute'
                elif inreach: why = 'nothing, enemy in reach'
                else: why = 'nothing, enemy at reach+1'
                C['why ' + why] += 1
            al = sum(1 for j in range(n) if j != i and a['c'][j]['t'] == c['t'] and off(a['c'][j]) and D.dist(p, (a['c'][j]['x'], a['c'][j]['y'])) <= 6)
            e6 = sum(1 for d, j in ens if d <= 6)
            nb = al + 1 - e6; nb = 'outnumbering' if nb >= 1 else 'even' if nb == 0 else 'outnumbered'
            C['n ' + nb] += 1; C['n ' + nb + ' hit'] += hitc
            hf = c.get('hp', 0) / max(1, c.get('mhp', 1))
            hb = 'hp80+' if hf >= 0.8 else 'hp50-80' if hf >= 0.5 else 'hp<50'
            C['h ' + hb] += 1; C['h ' + hb + ' hit'] += hitc
print(f'{ng} games to r1000, per champion-game. contact = enemy champion within reach+1')
WHY = ('hit a camp', 'cast (no champion hit)', 'moved, enemy in reach', 'moved, enemy at reach+1', 'tribute', 'nothing, enemy in reach', 'nothing, enemy at reach+1')
for ty in sorted({k[1] for k in G}):
    for w in ('us', 'them'):
        g = G[(w, ty)]
        if g < 15: continue
        C = A[(w, ty)]; ct = max(1, C['contact']); hr = max(1, C['hit rounds'])
        print(f"{ty:9} {w:4} n={g:3} dmg {C['dmg'] / g:6.0f} (r0-300 {C['dmg 0-300'] / g:5.0f}, 301-600 {C['dmg 301-600'] / g:5.0f}, 601-1000 {C['dmg 601-1000'] / g:5.0f})"
              f" = contact {C['contact'] / g:5.1f} x hit {C['contact hit'] / ct:.2f} ; dmg/hit round {C['hit dmg'] / hr:5.0f} with {C['shards'] / hr:4.1f} main shards,"
              f" cast in {C['cast hit rounds'] / hr:.0%} ; on champions dying within 10 {C['dmg_kill'] / max(1, C['dmg']):.0%}")
        nh = '  '.join(f"{b} {C['n ' + b] / ct:.0%} hit {C['n ' + b + ' hit'] / max(1, C['n ' + b]):.2f}" for b in ('outnumbering', 'even', 'outnumbered'))
        hh = '  '.join(f"{b} hit {C['h ' + b + ' hit'] / max(1, C['h ' + b]):.2f}" for b in ('hp80+', 'hp50-80', 'hp<50'))
        print(f"              contact by numbers: {nh} | {hh}")
        print('              no hit: ' + '  '.join(f"{y} {C['why ' + y] / ct:.0%}" for y in WHY if C['why ' + y]))
