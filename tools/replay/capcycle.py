# Time budget between a champion's group captures, us vs them (default to r600): the decoded.py captures numbers (clear,
# claim, cycle, moves, hop) plus, per interval, rounds dead, tribute starts, hitting champions, hitting camps, moving (with
# an enemy within 6 or not, and with gems in the bag) and idle. Usage: python -I tools/replay/capcycle.py DIR... [--round R]
import sys, collections
sys.path.insert(0, 'tools/replay')
from decoded import *
def cmd_cycle(dirs, rounds):
    R = (rounds or [1000])[0]
    N = collections.Counter(); V = collections.defaultdict(list); ng = 0
    for us, res, mp, meta, rows in games(dirs):
        ng += 1
        n = len(rows[0]['c'])
        grp, members, gtiles = camp_groups(rows, n)
        start = {t: [(o['x'], o['y']) for o in rows[0]['c'] if 'x' in o and o['t'] == t] for t in (0, 1)}
        if not start[0] or not start[1]: continue
        first_hit, dmg, pending, last_cap, moves = {}, collections.defaultdict(list), {}, {}, collections.Counter()
        X = collections.defaultdict(collections.Counter)
        for a, b in zip(rows, rows[1:]):
            if b['r'] > R: break
            hitters = collections.defaultdict(set)
            for i in range(n):
                for x in camp_hits(a, i):
                    hitters[x[-1]].add(who(a['c'][i]['t'], us))
                    if x[-1] in grp: first_hit.setdefault(grp[x[-1]], a['r'])
                c, nb = a['c'][i], b['c'][i]
                acts = a['act'][i] if i < len(a.get('act', [])) else []
                if not c['a']: X[i]['dead'] += 1
                elif any(x[0] == 'tribute' for x in acts): X[i]['trib'] += 1
                elif enemy_hits(a, i, n): X[i]['champ'] += 1
                elif camp_hits(a, i): X[i]['camp'] += 1
                elif 'x' in c and 'x' in nb and (c['x'], c['y']) != (nb['x'], nb['y']):
                    X[i]['move'] += 1
                    near = any(o['t'] != c['t'] and o['a'] and 'x' in o and dist((c['x'], c['y']), (o['x'], o['y'])) <= 6 for o in a['c'])
                    X[i]['mnear' if near else 'mfar'] += 1
                    if c.get('g', 0) >= 1: X[i]['mbag'] += 1
                else: X[i]['idle'] += 1
                if c['a'] and nb['a'] and 'x' in c and 'x' in nb and (c['x'], c['y']) != (nb['x'], nb['y']): moves[i] += 1
            for j, (h0, h1) in enumerate(zip(a['mh'], b['mh'])):
                if j in grp and h1 < h0 and len(hitters.get(j, ())) == 1: dmg[grp[j]].append((b['r'], next(iter(hitters[j])), h0 - h1))
            for g, js in members.items():
                if g not in pending and any(a['mh'][j] > 0 for j in js) and all(b['mh'][j] == 0 for j in js):
                    by = collections.Counter()
                    for r0, w, d in dmg.pop(g, []):
                        if r0 > b['r'] - 30: by[w] += d
                    pending[g] = (b['r'], first_hit.pop(g, b['r']), by.most_common(1)[0][0] if by else 'none')
            for i, c in enumerate(b['c']):
                pc = a['c'][i]
                if not (c['a'] and pc['a'] and 'x' in c) or (c.get('g', 0) <= pc.get('g', 0) and c.get('au', 0) <= pc.get('au', 0)) or c.get('k', 0) > pc.get('k', 0): continue
                p = (c['x'], c['y'])
                g = next((g for g in pending if p in gtiles[g]), None)
                if g is None: continue
                dead, hit0, killer = pending.pop(g)
                w = who(c['t'], us)
                do = min(dist(p, q) for q in start[c['t']]); de = min(dist(p, q) for q in start[1 - c['t']])
                region = 'own' if do < de - 3 else 'enemy' if de < do - 3 else 'middle'
                N[(w, region)] += 1; N[(w, region, 'gems')] += c['g'] - pc['g']; N[(w, min(b['r'] // 250, 3))] += 1
                N[(w, 'killed by ' + ('own side' if killer == w else 'nobody' if killer == 'none' else 'other side'))] += 1
                V[(w, 'clear')].append(dead - hit0); V[(w, 'claim')].append(b['r'] - dead)
                if i in last_cap:
                    V[(w, 'cycle')].append(b['r'] - last_cap[i][0]); V[(w, 'moves')].append(moves[i])
                    V[(w, 'hop')].append(dist(p, last_cap[i][1]))
                    for k in ('dead', 'trib', 'champ', 'camp', 'move', 'idle', 'mnear', 'mfar', 'mbag'): V[(w, 'x' + k)].append(X[i][k])
                    V[(w, 'n_trib')].append(1 if X[i]['trib'] else 0); V[(w, 'n_dead')].append(1 if X[i]['dead'] else 0)
                last_cap[i] = (b['r'], p); moves[i] = 0; X[i] = collections.Counter()
    print(f'{ng} games to r{R}: group captures per game (a capture is a gem or gold gain without a kill on a tile of a group whose '
          f'camps all died), region by distance to each side\'s start tiles')
    for w in ('us', 'them'):
        tot = sum(N[(w, r)] for r in ('own', 'middle', 'enemy'))
        print(f'  {w:4} {tot / ng:5.1f} captures: ' + ', '.join(f'{r} {N[(w, r)] / ng:.1f} ({N[(w, r, "gems")] / ng:.0f} gems)' for r in ('own', 'middle', 'enemy'))
              + '; by 250 rounds ' + ' '.join(f'{N[(w, k)] / ng:.1f}' for k in range(4))
              + '; groups killed (most damage in their last 30 rounds) by ' + ', '.join(f'{k} {N[(w, "killed by " + k)] / ng:.1f}' for k in ('own side', 'other side', 'nobody')))
    print('  per capture, mean (median): clear = first hit to last camp dead, claim = to the capture, cycle = the capturer\'s rounds since '
          'its previous capture, moves = its moves in between, hop = straight distance between the two')
    for w in ('us', 'them'):
        print(f'  {w:4} ' + '  '.join(f'{k} {sum(V[(w, k)]) / max(1, len(V[(w, k)])):5.1f} ({sorted(V[(w, k)])[len(V[(w, k)]) // 2] if V[(w, k)] else 0})'
                                     for k in ('clear', 'claim', 'cycle', 'moves', 'hop')))
    print('  per interval between captures, mean rounds: dead, channel start, hitting champions, hitting camps, moving, idle; share with a tribute / a death')
    for w in ('us', 'them'):
        print(f'  {w:4} ' + '  '.join(f'{k[1:]} {sum(V[(w, k)]) / max(1, len(V[(w, k)])):5.1f}' for k in ('xdead', 'xtrib', 'xchamp', 'xcamp', 'xmove', 'xmnear', 'xmfar', 'xmbag', 'xidle'))
              + f"  with tribute {sum(V[(w, 'n_trib')]) / max(1, len(V[(w, 'n_trib')])):.2f} with death {sum(V[(w, 'n_dead')]) / max(1, len(V[(w, 'n_dead')])):.2f}")



if __name__ == '__main__':
    args = sys.argv[1:]
    R = [600]
    if '--round' in args: k = args.index('--round'); R = [int(args[k + 1])]; del args[k:k + 2]
    cmd_cycle(args, R)
