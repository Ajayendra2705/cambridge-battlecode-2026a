"""Analyses of decoded platform games (datasets from rounds_extract.mjs), us vs the opponents.

usage: python -I tools/replay/decoded.py CMD DIR [DIR ...] [--round R ...]

DIR is a folder of <match>.jsonl.gz files with an index.txt ("match map side result", side a = team 0), as written by
tools/replay/decode_run.sh. Several DIRs are pooled. Commands:

  gems      collected, tributed, lost on death, carried bag and deaths per game by round (default 300 600 1000)
  fights    by round 800: hits on enemy champions, champion damage dealt, deaths; outcome of fight starts
  channels  tribute channels by bag size (share completed), the per-turn break rate by enemies near the altar, and bags
            over 30 by whether an enemy came within 4 of the channeler (completed, cast on)
  types     per champion type: deaths, champion damage, gems, share of alive rounds hitting a champion, and the hit
            rate by distance to the nearest enemy
  items     emblems and shards per champion type at a round (default 600)
  risk      P(death within 10 rounds) and rounds per game by enemies / allies within 6 and health above or below half,
            us and them (default to round 1000)
  sources   gems collected by camp type by a round (default 600), credited to the camp type last hit
  starts    fight starts (first hit between a pair after 15 quiet rounds): each side's champions within 6 of the target,
            outnumbered / even / outnumbering shares; deaths by which side started that fight (default to round 1000)
  fuel      deaths within 5 rounds after the champion's own fuel exhaustion, and exhaustions per game in rounds 1-3, with
            an enemy within 6 and without; needs data/summaries/<match>.json (tools/replay/fuel_events.py fetches them)
  assist    a healthy (60%+) champion whose teammate within 6 is hit by an enemy champion: its action by distance to the
            nearest enemy, and, with an enemy within 4, how joining (hit or step closer) and holding went over the next 10
            rounds by numbers within 6, once per champion and teammate per 15 rounds (default to round 1000)
  guard     boss_battle only: the first round a guard monolith died, each side's hits on the guards, tributed by a round
            (default 1000) and the result, one line per game
"""
import collections, glob, gzip, json, math, os, sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
NAMES = ['ryth', 'vesper', 'vendetta', 'cassi', 'issac', 'stellar', 'prism', 'marcella', 'willow', 'ren', 'varg', 'tavi',
         'heart']
RANGE = {0: 1, 1: 3, 2: 1, 3: 3, 4: 1, 5: 3, 6: 3, 7: 1, 8: 3, 9: 1, 10: 1, 11: 3, 12: 1}
CAMPS = {0: 'wolf', 1: 'elk', 2: 'gem', 3: 'gold', 4: 'monolith', 5: 'golem'}
ITEMS = [f'{fam}_{stat}' for fam in ('monster', 'power', 'durability', 'treasure', 'jungle', 'home', 'bruiser')
         for stat in ('str', 'focus', 'hp')]  # item_type i is ITEMS[i // 2]: a shard when i is even, its emblem when odd


def dist(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))


def games(dirs):
    """Yield (us, result, map, meta, rows) per decoded game; rows keep only rounds with every champion listed."""
    for d in dirs:
        index = os.path.join(d, 'index.txt')
        side = {}
        for line in open(index, encoding='utf-8', errors='replace'):
            p = line.strip().split()
            if len(p) >= 4: side[p[0]] = (0 if p[2] == 'a' else 1, p[3], p[1])
        for f in sorted(glob.glob(os.path.join(d, '*.jsonl.gz'))):
            mid = os.path.basename(f).split('.')[0]
            if mid not in side: continue
            lines = [json.loads(l) for l in gzip.open(f, 'rt')]
            rows = [r for r in lines[1:] if r.get('c')]
            if not rows: continue
            n = max(len(r['c']) for r in rows)
            rows = [r for r in rows if len(r['c']) == n]
            us, res, mp = side[mid]
            yield us, res, mp, lines[0], rows


def who(team, us):
    return 'us' if team == us else 'them'


def enemy_hits(row, i, n):
    """Attacks and casts of champion i that hit an enemy champion this round."""
    me = row['c'][i]
    return [x for x in (row['act'][i] if i < len(row['act']) else []) if x[0] in ('attack', 'cast') and len(x) >= 5
            and x[-2] == 'c' and x[-1] < n and row['c'][x[-1]]['t'] != me['t']]


def camp_hits(row, i):
    return [x for x in (row['act'][i] if i < len(row['act']) else []) if x[0] in ('attack', 'cast') and len(x) >= 5 and x[-2] == 'm']


def cmd_gems(dirs, rounds):
    rounds = rounds or [300, 600, 1000]
    for R in rounds:
        A = {w: collections.Counter() for w in ('us', 'them')}
        ng = 0
        for us, res, mp, meta, rows in games(dirs):
            ng += 1
            last = rows[0]
            for a, b in zip(rows, rows[1:]):
                if b['r'] > R: break
                last = b
                for i, c in enumerate(b['c']):
                    pc = a['c'][i]; w = who(c['t'], us)
                    if c['a'] and pc['a'] and c.get('g', 0) > pc.get('g', 0): A[w]['collected'] += c['g'] - pc['g']
                    if pc['a'] and not c['a']: A[w]['lost on death'] += pc.get('g', 0); A[w]['deaths'] += 1
            for c in last['c']:
                if c['a']: A[who(c['t'], us)]['bag'] += c.get('g', 0)
            for t in (0, 1): A[who(t, us)]['tributed'] += last['sg'][t]
        print(f'r{R} ({ng} games)  ' + '  |  '.join(
            w + ' ' + ' '.join(f'{k} {A[w][k] / max(1, ng):.0f}' if k != 'deaths' else f'{k} {A[w][k] / max(1, ng):.1f}'
                               for k in ('collected', 'tributed', 'lost on death', 'bag', 'deaths')) for w in ('us', 'them')))


def cmd_fights(dirs, rounds):
    R = (rounds or [800])[0]
    H, D, De, S = collections.Counter(), collections.Counter(), collections.Counter(), collections.Counter()
    ng = 0
    for us, res, mp, meta, rows in games(dirs):
        ng += 1
        n = len(rows[0]['c'])
        last_hit = {}
        for k, (a, b) in enumerate(zip(rows, rows[1:])):
            if b['r'] > R: break
            for i, c in enumerate(b['c']):
                if a['c'][i]['a'] and not c['a']: De[who(c['t'], us)] += 1
            targets = collections.defaultdict(list)
            for i in range(n):
                for x in enemy_hits(a, i, n): targets[x[-1]].append(i)
            for t, hitters in targets.items():
                loss = max(0, a['c'][t].get('hp', 0) - (b['c'][t].get('hp', 0) if b['c'][t]['a'] else 0))
                for i in hitters:
                    w = who(a['c'][i]['t'], us); H[w] += 1; D[w] += loss / len(hitters)
            # Fight starts: the first hit between two champions after 15 quiet rounds; deaths within 8 tiles over 20 rounds.
            for i in range(n):
                for x in enemy_hits(a, i, n):
                    key = frozenset((i, x[-1]))
                    if k - last_hit.get(key, -99) > 15 and k + 21 < len(rows):
                        att = a['c'][i]['t']; pos = (a['c'][i].get('x', 0), a['c'][i].get('y', 0))
                        own = foe = 0
                        for j, o in enumerate(a['c']):
                            if not o['a'] or 'x' not in o or dist(pos, (o['x'], o['y'])) > 8: continue
                            if any(not rows[k + t]['c'][j]['a'] for t in range(1, 21)):
                                if o['t'] == att: own += 1
                                else: foe += 1
                        w = who(att, us); S[(w, 'n')] += 1; S[(w, 'own')] += own; S[(w, 'foe')] += foe
                    last_hit[key] = k
    print(f'by r{R} ({ng} games): ' + ' | '.join(f'{w} hits {H[w] / ng:.0f} champion damage {D[w] / ng:.0f} deaths {De[w] / ng:.1f}'
                                                  for w in ('us', 'them')))
    for w in ('us', 'them'):
        n = max(1, S[(w, 'n')])
        print(f'  fights {w} start: {S[(w, "n")] / ng:.1f} per game, starter loses {S[(w, "own")] / n:.2f}, kills {S[(w, "foe")] / n:.2f} per start')


def cmd_channels(dirs, rounds):
    C = collections.Counter(); L = collections.defaultdict(lambda: [0.0, 0, 0])
    ng = 0
    for us, res, mp, meta, rows in games(dirs):
        ng += 1
        n = len(rows[0]['c'])
        for k, b in enumerate(rows):
            for i, acts in enumerate(b['act'][:n]):
                tr = [x for x in acts if x[0] == 'tribute']
                c = b['c'][i]; g = c.get('g', 0)
                if not tr or g <= 0: continue
                turns = max(1, -(-g // 10)); j = min(len(rows) - 1, k + turns + 2)
                # A channel that would end the game (the game stops first, or the score is capped at 1000) is not a break.
                if k + turns + 2 >= len(rows) or b['sg'][c['t']] + g >= 1000: continue
                ok = rows[j]['sg'][c['t']] - b['sg'][c['t']] >= g * 0.9
                w = who(c['t'], us); size = '<=20' if g <= 20 else '21-50' if g <= 50 else '51-100' if g <= 100 else '>100'
                C[(w, size, 'n')] += 1; C[(w, size, 'ok')] += ok; C[(w, size, 'g')] += g; C[(w, size, 'banked')] += g * ok
                altar = (tr[0][1], tr[0][2])
                near = sum(1 for o in b['c'] if o['t'] != c['t'] and o['a'] and 'x' in o and dist(altar, (o['x'], o['y'])) <= 10)
                L[(w, min(near, 2))][0] += turns; L[(w, min(near, 2))][1] += 1; L[(w, min(near, 2))][2] += not ok
                if g <= 30: continue
                # Bags over 30: was an enemy champion within 4 of the channeler (stun reach) on any channel turn, did one cast on it.
                close = cast = False
                for r in rows[k:k + turns + 1]:
                    me = r['c'][i]
                    if not me['a'] or 'x' not in me: break
                    close |= any(o['t'] != c['t'] and o['a'] and 'x' in o and dist((me['x'], me['y']), (o['x'], o['y'])) <= 4 for o in r['c'])
                    cast |= any(x[0] == 'cast' and x[-1] == i for e in range(n) for x in enemy_hits(r, e, n))
                q = (w, close); C[q + ('n',)] += 1; C[q + ('ok',)] += ok; C[q + ('cast',)] += cast
    print(f'{ng} games; tribute channels per game by bag size:')
    for w in ('us', 'them'):
        for size in ('<=20', '21-50', '51-100', '>100'):
            n = C[(w, size, 'n')]
            if n: print(f'  {w:4} {size:6} starts {n / ng:4.1f}  completed {100 * C[(w, size, "ok")] / n:3.0f}%  gems started {C[(w, size, "g")] / ng:4.0f}  banked {C[(w, size, "banked")] / ng:4.0f}')
    print('per-turn break rate by enemies within 10 of the altar (failures / channel turns):')
    for k in sorted(L):
        turns, n, fails = L[k]
        print(f'  {k[0]:4} {k[1]} enemies: {n} channels, break rate {fails / max(1, turns):.4f}')
    print('bags over 30 by whether an enemy champion came within 4 of the channeler during the channel:')
    for w in ('us', 'them'):
        for close in (True, False):
            m = C[(w, close, 'n')]
            if m: print(f'  {w:4} {"enemy within 4" if close else "no enemy near"}  {m / ng:4.2f} per game  completed'
                        f' {100 * C[(w, close, "ok")] / m:3.0f}%  an enemy cast on the channeler {100 * C[(w, close, "cast")] / m:3.0f}%')


def cmd_types(dirs, rounds):
    R = (rounds or [1000])[0]
    A = collections.defaultdict(collections.Counter); G = collections.Counter()
    for us, res, mp, meta, rows in games(dirs):
        n = len(rows[0]['c'])
        for c in rows[0]['c']: G[(who(c['t'], us), c['ty'])] += 1
        for a, b in zip(rows, rows[1:]):
            if b['r'] > R: break
            targets = collections.defaultdict(list)
            for i in range(n):
                for x in enemy_hits(a, i, n): targets[x[-1]].append(i)
            for t, hitters in targets.items():
                loss = max(0, a['c'][t].get('hp', 0) - (b['c'][t].get('hp', 0) if b['c'][t]['a'] else 0))
                for i in hitters: A[(who(a['c'][i]['t'], us), a['c'][i]['ty'])]['dmg'] += loss / len(hitters)
            for i, c in enumerate(a['c']):
                k = (who(c['t'], us), c['ty']); C = A[k]; nc = b['c'][i]
                if not c['a']: continue
                C['alive'] += 1
                if not nc['a']: C['deaths'] += 1
                elif nc.get('g', 0) > c.get('g', 0): C['gems'] += nc['g'] - c['g']
                if 'x' not in c: continue
                hit = bool(enemy_hits(a, i, n)); C['hit rounds'] += hit
                enemies = [o for o in a['c'] if o['t'] != c['t'] and o['a'] and 'x' in o]
                if not enemies: continue
                dn = min(dist((c['x'], c['y']), (o['x'], o['y'])) for o in enemies)
                rng = RANGE.get(c['ty'], 1)
                band = 'in range' if dn <= rng else 'range+1-2' if dn <= rng + 2 else None
                if band: C[band] += 1; C[band + ' hit'] += hit
    print(f'per champion type, rounds to {R} (per game unless marked):')
    for k in sorted(G, key=lambda k: (NAMES[k[1]], k[0])):
        g, C = G[k], A[k]
        if g < 10: continue
        alive = max(1, C['alive'])
        bands = '  '.join(f'{b} hit {C[b + " hit"] / max(1, C[b]):.2f}' for b in ('in range', 'range+1-2'))
        print(f'  {NAMES[k[1]]:9} {k[0]:4} games {g:3}  deaths {C["deaths"] / g:.2f}  champion dmg {C["dmg"] / g:5.0f}  gems {C["gems"] / g:4.0f}'
              f'  hit-round share {C["hit rounds"] / alive:.3f}  {bands}')


def cmd_items(dirs, rounds):
    R = (rounds or [600])[0]
    I = collections.defaultdict(collections.Counter); N = collections.Counter(); HP = collections.Counter()
    for us, res, mp, meta, rows in games(dirs):
        row = next((r for r in rows if r['r'] >= R), None)
        if not row: continue
        for c in row['c']:
            k = (who(c['t'], us), c['ty']); N[k] += 1; HP[k] += c.get('mhp', 0)
            for it, cnt in c.get('it', []): I[k][ITEMS[it // 2] + (' emblem' if it % 2 else ' shard')] += cnt
    print(f'items per champion at r{R} (emblems and shards):')
    for k in sorted(N, key=lambda k: (NAMES[k[1]], k[0])):
        if N[k] < 10: continue
        top = ', '.join(f'{name} {v / N[k]:.2f}' for name, v in sorted(I[k].items(), key=lambda x: -x[1]) if v / N[k] >= 0.1)
        print(f'  {NAMES[k[1]]:9} {k[0]:4} n {N[k]:3} max hp {HP[k] / N[k]:5.0f}  {top}')


def cmd_risk(dirs, rounds):
    R = (rounds or [1000])[0]
    C = collections.Counter(); ng = 0
    for us, res, mp, meta, rows in games(dirs):
        ng += 1
        for k in range(0, len(rows) - 11, 2):
            a = rows[k]
            if a['r'] > R: break
            for i, c in enumerate(a['c']):
                if not c['a'] or 'x' not in c: continue
                pos = (c['x'], c['y']); t = c['t']
                ne = sum(1 for o in a['c'] if o['t'] != t and o['a'] and 'x' in o and dist(pos, (o['x'], o['y'])) <= 6)
                na = sum(1 for j, o in enumerate(a['c']) if j != i and o['t'] == t and o['a'] and 'x' in o and dist(pos, (o['x'], o['y'])) <= 6)
                dies = any(not rows[k + s]['c'][i]['a'] for s in range(1, 11))
                key = (who(t, us), min(ne, 3), min(na, 2), 'lo' if c.get('hp', 0) < 0.5 * max(1, c.get('mhp', 1)) else 'hi')
                C[key + ('n',)] += 1; C[key + ('d',)] += dies
    # Rounds are sampled every 2, so twice the samples is rounds per game in that state.
    print(f'{ng} games to r{R}: P(death within 10 rounds) and rounds per game, by enemies / allies within 6 and health half')
    print(f'  {"state":10} {"us P":>6} {"us rounds":>9} {"them P":>7} {"them rounds":>11}')
    for key in sorted({k[1:4] for k in C}):
        nu, nt = C[('us',) + key + ('n',)], C[('them',) + key + ('n',)]
        print(f'  e{key[0]} a{key[1]} {key[2]:4} {C[("us",) + key + ("d",)] / max(1, nu):6.3f} {2 * nu / max(1, ng):9.1f}'
              f' {C[("them",) + key + ("d",)] / max(1, nt):7.3f} {2 * nt / max(1, ng):11.1f}')


def cmd_starts(dirs, rounds):
    R = (rounds or [1000])[0]
    S = collections.Counter(); F = collections.Counter(); ng = 0
    for us, res, mp, meta, rows in games(dirs):
        ng += 1
        n = len(rows[0]['c']); last_hit = {}
        for k, a in enumerate(rows):
            if a['r'] > R or k + 1 >= len(rows): break
            # Fight starts: the first hit between two champions after 15 quiet rounds; each side's champions within 6 of the target.
            for i in range(n):
                for x in enemy_hits(a, i, n):
                    key = frozenset((i, x[-1]))
                    tc = a['c'][x[-1]]
                    if k - last_hit.get(key, -99) > 15 and 'x' in tc:
                        att = a['c'][i]['t']; tp = (tc['x'], tc['y']); w = who(att, us)
                        na = sum(1 for o in a['c'] if o['t'] == att and o['a'] and 'x' in o and dist(tp, (o['x'], o['y'])) <= 6)
                        nd = sum(1 for o in a['c'] if o['t'] != att and o['a'] and 'x' in o and dist(tp, (o['x'], o['y'])) <= 6)
                        S[(w, 'n')] += 1; S[(w, 'att')] += na; S[(w, 'def')] += nd
                        S[(w, 'down' if na < nd else 'even' if na == nd else 'up')] += 1
                    last_hit[key] = k
            # Fatal fights: walk back from each death through champion hits within 8 of the victim until 15 quiet rounds.
            b = rows[k + 1]
            for i in range(n):
                if not (a['c'][i]['a'] and not b['c'][i]['a']): continue
                vt = a['c'][i]['t']; w = who(vt, us); s = k; quiet = 0; starter = None
                while s >= 0 and quiet <= 15:
                    r = rows[s]; v = r['c'][i]
                    if not v['a'] or 'x' not in v: break
                    sides = {r['c'][j]['t'] for j in range(n) for x in enemy_hits(r, j, n)
                             if 'x' in r['c'][x[-1]] and dist((v['x'], v['y']), (r['c'][x[-1]]['x'], r['c'][x[-1]]['y'])) <= 8}
                    if sides:
                        quiet = 0; starter = 'both' if len(sides) == 2 else 'victim side' if vt in sides else 'killer side'
                    else: quiet += 1
                    s -= 1
                F[(w, starter or 'no champion fight')] += 1
    print(f'{ng} games to r{R}')
    for w in ('us', 'them'):
        m = max(1, S[(w, 'n')])
        print(f'  {w:4} start {S[(w, "n")] / ng:4.1f} fights per game: own champions within 6 of the target {S[(w, "att")] / m:.2f} vs'
              f' {S[(w, "def")] / m:.2f}; outnumbered {100 * S[(w, "down")] / m:.0f}%, even {100 * S[(w, "even")] / m:.0f}%,'
              f' outnumbering {100 * S[(w, "up")] / m:.0f}%')
    for w in ('us', 'them'):
        print(f'  {w:4} deaths per game by who started that fight: ' + ', '.join(
            f'{s} {F[(w, s)] / ng:.2f}' for s in ('victim side', 'killer side', 'both', 'no champion fight')))


def cmd_fuel(dirs, rounds):
    """Needs the platform match summaries in data/summaries/<match>.json (tools/replay/fuel_events.py fetches them)."""
    R = (rounds or [1000])[0]
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    C = collections.Counter(); M = collections.Counter(); MG = collections.Counter(); ng = missing = 0
    for us, res, mp, meta, rows in games(dirs):
        p = os.path.join(root, 'data', 'summaries', meta['file'].split('.')[0] + '.json')
        if not os.path.exists(p): missing += 1; continue
        ng += 1; MG[mp] += 1
        ev = collections.defaultdict(set)
        for e in json.load(open(p, encoding='utf-8'))['events']:
            if e['kind'] == 'fuelExhausted' and e['owner'].get('kind') == 'champion':
                for x in e['entries']: ev[e['owner']['id']].add(x['timestamp']['round'])
        byround = {r['r']: r for r in rows}
        for cid, rs in ev.items():
            w = who(0 if cid < 5 else 1, us)  # Summary champion ids 0-4 are team A, 5-9 team B, in the decoded order.
            for r in rs:
                row = byround.get(r)
                if r <= 3 or r > R: C[(w, 'r1-3' if r <= 3 else 'late')] += 1; continue
                if not row or cid >= len(row['c']) or 'x' not in row['c'][cid]: C[(w, 'unknown')] += 1; continue
                me = row['c'][cid]
                hot = any(o['a'] and 'x' in o and o['t'] != me['t'] and dist((me['x'], me['y']), (o['x'], o['y'])) <= 6 for o in row['c'])
                C[(w, 'contact' if hot else 'quiet')] += 1
                if w == 'us' and hot: M[mp] += 1
        for a, b in zip(rows, rows[1:]):
            if b['r'] > R: break
            for i, c in enumerate(b['c']):
                if a['c'][i]['a'] and not c['a']:
                    w = who(c['t'], us); C[(w, 'deaths')] += 1
                    if any(r in ev.get(i, ()) for r in range(b['r'] - 5, b['r'] + 1)): C[(w, 'after fuel')] += 1
    print(f'{ng} games to r{R} ({missing} without a summary)')
    for w in ('us', 'them'):
        print(f'  {w:4} deaths {C[(w, "deaths")] / max(1, ng):.2f}, of them within 5 rounds after their own fuel exhaustion'
              f' {C[(w, "after fuel")] / max(1, ng):.2f}; exhaustions per game: rounds 1-3 {C[(w, "r1-3")] / max(1, ng):.1f},'
              f' with an enemy within 6 {C[(w, "contact")] / max(1, ng):.1f}, without {C[(w, "quiet")] / max(1, ng):.1f}')
    print('  ours with an enemy within 6, per game on that map: ' + ', '.join(f'{m} {v / MG[m]:.1f}' for m, v in M.most_common(8)))


def cmd_sources(dirs, rounds):
    R = (rounds or [600])[0]
    H = {w: collections.Counter() for w in ('us', 'them')}; ng = 0
    for us, res, mp, meta, rows in games(dirs):
        ng += 1
        camps = {int(k): v for k, v in meta.get('camps', {}).items()}
        n = len(rows[0]['c']); last = {}
        for a, b in zip(rows, rows[1:]):
            if b['r'] > R: break
            for i in range(n):
                for x in camp_hits(a, i): last[i] = CAMPS.get(camps.get(x[-1]), '?')
            for i, c in enumerate(b['c']):
                if c['a'] and a['c'][i]['a'] and c.get('g', 0) > a['c'][i].get('g', 0):
                    H[who(c['t'], us)][last.get(i, '?')] += c['g'] - a['c'][i]['g']
    for w in ('us', 'them'):
        print(f'{w} gems by r{R} per game: ' + ', '.join(f'{k} {v / ng:.0f}' for k, v in sorted(H[w].items(), key=lambda x: -x[1])))


def cmd_assist(dirs, rounds):
    R = (rounds or [1000])[0]
    A = collections.Counter(); O = collections.Counter(); ng = 0
    for us, res, mp, meta, rows in games(dirs):
        ng += 1
        n = len(rows[0]['c']); last = {}
        for k in range(len(rows) - 11):
            a, b = rows[k], rows[k + 1]
            if a['r'] > R: break
            hit_by = collections.defaultdict(list)  # champion index -> enemy champions hitting it this round
            for i in range(n):
                for x in enemy_hits(a, i, n): hit_by[x[-1]].append(i)
            for i, c in enumerate(a['c']):
                if not c['a'] or 'x' not in c or not b['c'][i]['a'] or 'x' not in b['c'][i]: continue
                if c.get('hp', 0) < 0.6 * max(1, c.get('mhp', 1)): continue
                p = (c['x'], c['y'])
                mates = [j for j in hit_by if j != i and a['c'][j]['t'] == c['t'] and 'x' in a['c'][j]
                         and dist(p, (a['c'][j]['x'], a['c'][j]['y'])) <= 6]
                foes = [o for o in a['c'] if o['t'] != c['t'] and o['a'] and 'x' in o]
                if not mates or not foes: continue
                w = who(c['t'], us); hits = bool(enemy_hits(a, i, n))
                dn0 = min(dist(p, (o['x'], o['y'])) for o in foes)
                dn1 = min(dist((b['c'][i]['x'], b['c'][i]['y']), (o['x'], o['y'])) for o in foes)
                act = 'hit' if hits else 'camp' if camp_hits(a, i) else 'closer' if dn1 < dn0 else 'away' if dn1 > dn0 else 'still'
                band = '1-2' if dn0 <= 2 else '3-4' if dn0 <= 4 else '5+'
                A[(w, band, 'n')] += 1; A[(w, band, act)] += 1
                if dn0 > 4: continue
                al6 = sum(1 for o in a['c'] if o['t'] == c['t'] and o['a'] and 'x' in o and dist(p, (o['x'], o['y'])) <= 6)
                en6 = sum(1 for o in foes if dist(p, (o['x'], o['y'])) <= 6)
                key = (w, 'even' if al6 == en6 else 'ahead' if al6 > en6 else 'behind', 'join' if hits or dn1 < dn0 else 'hold')
                for j in mates:
                    fresh = k - last.get((i, j), -99) > 15; last[(i, j)] = k
                    if not fresh: continue
                    jp = (a['c'][j]['x'], a['c'][j]['y'])
                    O[key + ('n',)] += 1
                    O[key + ('mate',)] += any(not rows[k + t]['c'][j]['a'] for t in range(1, 11))
                    O[key + ('self',)] += any(not rows[k + t]['c'][i]['a'] for t in range(1, 11))
                    O[key + ('kills',)] += sum(1 for e in range(n) if a['c'][e]['t'] != c['t'] and a['c'][e]['a'] and 'x' in a['c'][e]
                                               and dist(jp, (a['c'][e]['x'], a['c'][e]['y'])) <= 8
                                               and any(not rows[k + t]['c'][e]['a'] for t in range(1, 11)))
    print(f'{ng} games to r{R}; healthy (60%+) champion, teammate within 6 hit by an enemy champion this round')
    print('  its action by distance to the nearest enemy (share of those rounds):')
    for w in ('us', 'them'):
        for band in ('1-2', '3-4', '5+'):
            m = max(1, A[(w, band, 'n')])
            print(f'    {w:4} enemy {band:3} {A[(w, band, "n")] / ng:5.1f}/game  '
                  + '  '.join(f'{x} {100 * A[(w, band, x)] / m:4.1f}%' for x in ('hit', 'camp', 'closer', 'still', 'away')))
    print('  enemy within 4, joined or held, by numbers within 6; within the next 10 rounds:')
    for w in ('us', 'them'):
        for odds in ('ahead', 'even', 'behind'):
            for way in ('join', 'hold'):
                m = O[(w, odds, way, 'n')]
                if m: print(f'    {w:4} {odds:6} {way} {m / ng:5.2f}/game: teammate dies {O[(w, odds, way, "mate")] / m:.2f},'
                            f' self {O[(w, odds, way, "self")] / m:.2f}, enemies within 8 of the teammate die {O[(w, odds, way, "kills")] / m:.2f}')


def cmd_guard(dirs, rounds):
    R = (rounds or [1000])[0]
    print(f'boss_battle games: first round a guard monolith died, hits on the guards, tributed by r{R}')
    for us, res, mp, meta, rows in games(dirs):
        if 'boss' not in mp: continue
        mono = [int(k) for k, v in meta['camps'].items() if v == 4]  # boss_battle's only monoliths are the two guards
        n = len(rows[0]['c']); hits = collections.Counter(); first = None
        for r in rows:
            for i in range(n):
                hits[who(r['c'][i]['t'], us)] += sum(1 for x in camp_hits(r, i) if x[-1] in mono)
            if first is None and any(r['mh'][m] <= 0 for m in mono if m < len(r['mh'])): first = r['r']
        last = [r for r in rows if r['r'] <= R][-1]
        print(f"  {meta['file'][:8]} {res:4} guard first dead r{first}  hits us {hits['us']} them {hits['them']}"
              f"  tributed us {last['sg'][us]} them {last['sg'][1 - us]}")


def main():
    args = sys.argv[1:]
    if len(args) < 2 or args[0] not in CMDS: sys.exit(__doc__)
    rounds = []
    if '--round' in args:
        j = args.index('--round'); rounds = [int(x) for x in args[j + 1:]]; args = args[:j]
    CMDS[args[0]](args[1:], rounds)


CMDS = {'gems': cmd_gems, 'fights': cmd_fights, 'channels': cmd_channels, 'types': cmd_types, 'items': cmd_items,
        'risk': cmd_risk, 'sources': cmd_sources, 'starts': cmd_starts, 'fuel': cmd_fuel, 'assist': cmd_assist,
        'guard': cmd_guard}

if __name__ == '__main__':
    main()
