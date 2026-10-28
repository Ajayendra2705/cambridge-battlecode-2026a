"""Ranged hits outside fights: basic hits by a ranged champion on an enemy champion that is not fighting, us vs them.

usage: python -I tools/replay/rangedhits.py DIR... [--maps a,b] [--skipmaps a,b]   (env UPTO, default 1000)

Every ranged basic hit on a champion is one of: in a fight (the victim hit an enemy champion that round or the one
before), walked in this round (the victim's round-start tile is out of the shooter's range), walked in last round (its
tile at the previous round start is out of range) or free. "Outside fights" = the last three. Exposure rounds: a
champion that hit no enemy champion this round or the last ends its turn within basic range of an enemy shooter (off
its spawn); the share shot by it in the next round. Shot response: a hit by enemy shooters only on a champion that is
not fighting, at 50%+ health after the round (one event per victim per 4 rounds): a round later it hit back, is out
of every enemy's basic range, is still inside one, or is dead.
Episodes join the free hits of one shooter on one victim with gaps of 3 rounds or less. Per episode: the victim's
activity when it started (hitting a camp, walking, standing), its answer over the next 3 rounds (hit the shooter,
closed in, kept the distance, moved away), and the outcome within 10 rounds of the episode's end (victim dead,
shooter dead). Numbers within 6 count the champions of each side (alive, off their spawn) around the victim.
"""
import collections, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from decoded import games, who, dist, enemy_hits, camp_hits, NAMES, RANGE

UPTO = int(os.environ.get('UPTO', 1000))


def pos(c):
    return (c['x'], c['y']) if c.get('a') and 'x' in c else None


def main():
    args = sys.argv[1:]
    maps = skip = None
    if '--maps' in args:
        j = args.index('--maps'); maps = args[j + 1].split(','); del args[j:j + 2]
    if '--skipmaps' in args:
        j = args.index('--skipmaps'); skip = args[j + 1].split(','); del args[j:j + 2]
    if not args: sys.exit(__doc__)
    H = collections.Counter()   # (victim side, key) -> count
    ng = 0
    for us, res, mp, meta, rows in games(args):
        if maps and not any(m in mp for m in maps): continue
        if skip and any(m in mp for m in skip): continue
        ng += 1
        n = len(rows[0]['c'])
        spawn = {t: set((c['x'], c['y']) for c in rows[0]['c'] if c['t'] == t and 'x' in c) for t in (0, 1)}
        fought = [set() for _ in rows]   # champions that hit an enemy champion in round k
        for k, r in enumerate(rows):
            for i in range(n):
                if enemy_hits(r, i, n): fought[k].add(i)
        # Exposure: a champion that hit no enemy champion this round or the last ends its turn (the next round's start)
        # within basic range of an enemy ranged champion off its spawn; hit = that shooter hits it in the next round.
        for k in range(1, len(rows) - 2):
            a, b, c2 = rows[k], rows[k + 1], rows[k + 2]
            if b['r'] > UPTO: break
            for j in range(n):
                v = b['c'][j]; pv = pos(v)
                if pv is None or j in fought[k] or j in fought[k - 1] or pv in spawn[v['t']]: continue
                w = who(v['t'], us)
                for i in range(n):
                    s = b['c'][i]; ps = pos(s)
                    if ps is None or s['t'] == v['t'] or RANGE.get(s['ty'], 1) < 3 or ps in spawn[s['t']]: continue
                    if dist(pv, ps) > RANGE[s['ty']]: continue
                    if any(camp_hits(rows[t], j) for t in (k - 1, k)): act = 'camp'
                    elif any(y[0] == 'move' for y in a['act'][j]): act = 'walk'
                    else: act = 'stand'
                    hit = any(y[0] == 'attack' and y[-2] == 'c' and y[-1] == j for y in b['act'][i])
                    for key in ('all', act, 'melee' if RANGE.get(v['ty'], 1) <= 1 else 'ranged'):
                        H[(w, 'expo', key)] += 1; H[(w, 'expohit', key)] += hit
        # Shot response: hits by enemy shooters only (attacks and casts) on a champion not fighting, 50%+ health after.
        last = {}
        for k in range(1, len(rows) - 2):
            if rows[k]['r'] > UPTO: break
            by = collections.defaultdict(list)
            for e in range(n):
                for x in enemy_hits(rows[k], e, n): by[x[-1]].append(e)
            b, c2 = rows[k + 1], rows[k + 2]
            for j, es in by.items():
                v = b['c'][j]
                if not v['a'] or pos(v) is None or j in fought[k] or j in fought[k - 1] or last.get(j, -99) >= k - 3: continue
                if any(RANGE.get(rows[k]['c'][e]['ty'], 1) < 3 for e in es) or v['hp'] < 0.5 * v['mhp']: continue
                last[j] = k
                w = who(v['t'], us)
                p2 = pos(c2['c'][j])
                if p2 is None: resp = 'dead'
                elif j in fought[k + 1]: resp = 'hit back'
                elif any(c2['c'][e]['t'] != v['t'] and pos(c2['c'][e]) and pos(c2['c'][e]) not in spawn[c2['c'][e]['t']]
                         and dist(p2, pos(c2['c'][e])) <= RANGE.get(c2['c'][e]['ty'], 1) for e in range(n)): resp = 'in range'
                else: resp = 'out of range'
                H[(w, 'shot')] += 1; H[(w, 'shot', resp)] += 1
        open_ep = {}   # (shooter, victim) -> episode dict
        eps = []
        for k in range(1, len(rows) - 1):
            a, z = rows[k], rows[k - 1]
            if a['r'] > UPTO: break
            for i in range(n):
                sh = a['c'][i]
                if not sh['a'] or RANGE.get(sh['ty'], 1) < 3 or 'x' not in sh: continue
                for x in (a['act'][i] if i < len(a['act']) else []):
                    if x[0] != 'attack' or len(x) < 5 or x[-2] != 'c': continue
                    j = x[-1]
                    if j >= n or a['c'][j]['t'] == sh['t']: continue
                    w = who(a['c'][j]['t'], us)
                    H[(w, 'ranged hits')] += 1
                    rs, ps, pk, pz = RANGE[sh['ty']], (sh['x'], sh['y']), pos(a['c'][j]), pos(z['c'][j])
                    kind = ('in a fight' if j in fought[k] or j in fought[k - 1] else 'walked in this round'
                            if pk is None or dist(pk, ps) > rs else 'walked in last round' if pz is None or dist(pz, ps) > rs else 'free')
                    H[(w, 'kind', kind)] += 1; H[(w, 'by shooter', NAMES[sh['ty']], kind)] += 1
                    if kind != 'free': continue
                    H[(w, 'free hits')] += 1
                    H[(w, 'free ' + NAMES[a['c'][j]['ty']])] += 1
                    e = open_ep.get((i, j))
                    if e and k - e['last'] <= 3:
                        e['last'] = k; e['hits'] += 1
                        continue
                    e = {'s': i, 'v': j, 'k0': k, 'last': k, 'hits': 1, 'w': w}
                    open_ep[(i, j)] = e
                    eps.append(e)
        for e in eps:
            i, j, k0, w = e['s'], e['v'], e['k0'], e['w']
            v0, s0 = rows[k0]['c'][j], rows[k0]['c'][i]
            pv, ps = pos(v0), pos(s0)
            if pv is None or ps is None: continue
            vty = NAMES[v0['ty']]
            melee = RANGE.get(v0['ty'], 1) <= 1
            # Activity at the start: camp hits this round or the 2 before, else a move this round, else standing.
            if any(camp_hits(rows[t], j) for t in range(max(0, k0 - 2), k0 + 1)): act = 'camp'
            elif any(y[0] == 'move' for y in rows[k0]['act'][j]): act = 'walk'
            else: act = 'stand'
            if v0.get('g', 0) >= 30: act += '+bag'
            # Numbers within 6 of the victim.
            mine = sum(1 for c in rows[k0]['c'] if c['t'] == v0['t'] and pos(c) and dist(pos(c), pv) <= 6
                       and pos(c) not in spawn[c['t']])
            theirs = sum(1 for c in rows[k0]['c'] if c['t'] != v0['t'] and pos(c) and dist(pos(c), pv) <= 6
                         and pos(c) not in spawn[c['t']])
            nb = 'out' if theirs > mine else 'even' if theirs == mine else 'up'
            # Answer over the next 3 rounds.
            hit_back = hit_any = False
            dmin = d0 = dist(pv, ps)
            dend = d0
            for t in range(k0 + 1, min(len(rows), k0 + 4)):
                for y in enemy_hits(rows[t], j, n):
                    hit_any = True
                    if y[-1] == i: hit_back = True
                cv, cs = pos(rows[t]['c'][j]), pos(rows[t]['c'][i])
                if cv and cs:
                    dend = dist(cv, cs); dmin = min(dmin, dend)
            if hit_back: ans = 'hit shooter'
            elif hit_any: ans = 'hit other'
            elif dmin < d0: ans = 'closed in'
            elif dend > RANGE[s0['ty']]: ans = 'left range'
            else: ans = 'stayed in range'
            end = e['last']
            vdead = any(not rows[t]['c'][j]['a'] for t in range(end + 1, min(len(rows), end + 11)))
            sdead = any(not rows[t]['c'][i]['a'] for t in range(end + 1, min(len(rows), end + 11)))
            hp0 = v0.get('hp', 0) / max(1, v0.get('mhp', 1))
            for key in ('all', 'melee' if melee else 'ranged', vty, 'act ' + act, 'nb ' + nb, 'ans ' + ans,
                        'hp ' + ('80+' if hp0 >= 0.8 else '50-80' if hp0 >= 0.5 else '<50')):
                H[(w, key, 'eps')] += 1
                H[(w, key, 'hits')] += e['hits']
                H[(w, key, 'vdead')] += vdead
                H[(w, key, 'sdead')] += sdead
            for key in ('melee' if melee else 'ranged',):
                H[(w, key + ' ans ' + ans, 'eps')] += 1
                H[(w, key + ' ans ' + ans, 'hits')] += e['hits']
                H[(w, key + ' ans ' + ans, 'vdead')] += vdead
                H[(w, key + ' ans ' + ans, 'sdead')] += sdead
    if not ng: sys.exit('no games')
    g = ng
    print(f'{ng} games, to r{UPTO}; per game, victim side: us = hits taken by our champions, them = by theirs')
    print(f"  ranged basic hits on champions   us {H[('us', 'ranged hits')] / g:6.1f}   them {H[('them', 'ranged hits')] / g:6.1f}")
    for kind in ('in a fight', 'walked in this round', 'walked in last round', 'free'):
        print(f"    {kind:30} us {H[('us', 'kind', kind)] / g:6.1f}   them {H[('them', 'kind', kind)] / g:6.1f}")
    for ty in sorted({k[2] for k in H if len(k) == 4 and k[1] == 'by shooter'}):
        print(f'    shooter {ty:9} ' + '   '.join(f"{w} " + ' '.join(f"{H[(w, 'by shooter', ty, kd)] / g:5.1f}" for kd in
              ('in a fight', 'walked in this round', 'walked in last round', 'free')) for w in ('us', 'them')))
    print('  exposure rounds (not fighting, ending the turn within basic range of an enemy shooter) per game, '
          'and the share shot next round:')
    for key in ('all', 'camp', 'walk', 'stand', 'melee', 'ranged'):
        print(f"    {key:30} " + '   '.join(
            f"{w} {H[(w, 'expo', key)] / g:6.1f} ({H[(w, 'expohit', key)] / max(1, H[(w, 'expo', key)]):.2f})" for w in ('us', 'them')))
    print(f"    {'outside fights':30} " + '   '.join(f"{w} {sum(H[(w, 'kind', kd)] for kd in ('walked in this round', 'walked in last round', 'free')) / g:6.1f}" for w in ('us', 'them')))
    print('  shot response (shooters only, victim not fighting, 50%+ health): events per game; a round later')
    print('    ' + '   '.join(f"{w} {H[(w, 'shot')] / g:5.1f}: " + ' '.join(f"{r} {H[(w, 'shot', r)] / max(1, H[(w, 'shot')]):.2f}"
          for r in ('hit back', 'out of range', 'in range', 'dead')) for w in ('us', 'them')))
    print(f"  free (victim not fighting)       us {H[('us', 'free hits')] / g:6.1f}   them {H[('them', 'free hits')] / g:6.1f}")
    tys = sorted({k[1][5:] for k in H if len(k) == 2 and k[1].startswith('free ') and k[1] != 'free hits'})
    print('  free hits by victim type: ' + '  '.join(
        f"{t} {H[('us', 'free ' + t)] / g:.1f}/{H[('them', 'free ' + t)] / g:.1f}" for t in tys))
    keys = sorted({k[1] for k in H if len(k) == 3}, key=lambda s: (s.split()[0] if ' ' in s else '', s))
    order = ['all', 'melee', 'ranged'] + [k for k in keys if k not in ('all', 'melee', 'ranged')]
    print('episodes (free hits of one shooter on one victim, gaps <= 3): per game eps / hits, P(victim dead in 10), '
          'P(shooter dead in 10)')
    for key in order:
        row = []
        for w in ('us', 'them'):
            m = H[(w, key, 'eps')]
            row.append(f"{w:4} {m / g:5.1f} / {H[(w, key, 'hits')] / g:5.1f}  vd {H[(w, key, 'vdead')] / max(1, m):.2f}"
                       f"  sd {H[(w, key, 'sdead')] / max(1, m):.2f}")
        print(f'  {key:28} ' + '   |   '.join(row))


if __name__ == '__main__':
    main()
