"""Free hits by ranged champions: basic attacks (range 3) on enemy champions that were not fighting, per shooter side.

usage: python -I tools/replay/freehits.py DIR... [--upto R]

A hit is free when the victim hit no enemy champion in that round or the round before and did not just walk into
range (over 3 tiles from the shooter at the previous round start, within 3 at this one). Free hits are split by the
victim's own step that round (from its round-start tile to the next round's, measured to the shooter's round-start
tile): toward, same distance, away; and by the victim's kind (melee, ranged). Also printed: the share of free hits
whose victim hit the shooter within the next 3 rounds. DIR is a decoded run (`decode_run.sh`); rounds 2 to R
(default 1000).
"""
import collections, gzip, json, os, sys

RANGED = {1, 3, 5, 6, 8, 11}  # Vesper, Cassi, Stellar, Prism, Willow, Tavi


def ch(a, b):
    return max(abs(a['x'] - b['x']), abs(a['y'] - b['y']))


def main(args):
    upto = 1000
    if '--upto' in args:
        k = args.index('--upto')
        upto = int(args[k + 1])
        del args[k:k + 2]
    C = collections.Counter()
    G = 0
    for d in args:
        for line in open(os.path.join(d, 'index.txt'), encoding='utf-8'):
            p = line.split()
            if len(p) < 3:
                continue
            f = os.path.join(d, p[0] + '.jsonl.gz')
            if not os.path.exists(f):
                continue
            us = 0 if p[2] == 'a' else 1
            R = [json.loads(x) for x in gzip.open(f, 'rt') if x.strip()][1:]
            R = [r for r in R if r.get('c') and r['r'] <= upto + 1]
            if len(R) < 3:
                continue
            G += 1
            n = len(R[0]['c'])
            tm = [c['t'] for c in R[0]['c']]
            ty = [c['ty'] for c in R[0]['c']]

            def acts_of(r, i):
                a = r.get('act') or []
                return a[i] if i < len(a) else []

            def champ_targets(r, i):
                out = []
                for a in acts_of(r, i):
                    j = a[4] if a[0] == 'attack' and len(a) >= 5 and a[3] == 'c' else a[5] if a[0] == 'cast' and len(a) >= 6 and a[4] == 'c' else None
                    if j is not None and j < n and tm[j] != tm[i]:
                        out.append(j)
                return out

            for k in range(1, len(R) - 3):
                r, rp, rn = R[k], R[k - 1], R[k + 1]
                if r['r'] > upto:
                    break
                for i in range(n):
                    if ty[i] not in RANGED:
                        continue
                    for a in acts_of(r, i):
                        if not (a[0] == 'attack' and len(a) >= 5 and a[3] == 'c'):
                            continue
                        j = a[4]
                        if j >= n or tm[j] == tm[i]:
                            continue
                        side = 'us' if tm[i] == us else 'them'
                        C[side, 'all'] += 1
                        if champ_targets(r, j) or champ_targets(rp, j):
                            continue
                        si, sj, pi, pj, nj = r['c'][i], r['c'][j], rp['c'][i], rp['c'][j], rn['c'][j]
                        if not all('x' in q and q.get('a') for q in (si, sj, pi, pj)):
                            continue
                        if ch(pi, pj) > 3 and ch(si, sj) <= 3:
                            continue
                        kind = 'ranged' if ty[j] in RANGED else 'melee'
                        if 'x' in nj and nj.get('a'):
                            d0, d1 = ch(sj, si), ch(nj, si)
                            mv = 'toward' if d1 < d0 else 'away' if d1 > d0 else 'same'
                        else:
                            mv = 'died'
                        back = any(i in champ_targets(R[k + q], j) for q in (1, 2, 3))
                        C[side, 'free'] += 1
                        C[side, kind, mv] += 1
                        C[side, 'back'] += back
    print('%d games, rounds 2-%d: basic hits by ranged champions on champions, per game' % (G, upto))
    for s in ('us', 'them'):
        g = max(G, 1)
        free = C[s, 'free']
        print('  shooter %-4s all %5.1f  free %5.1f (victim hit the shooter within 3 rounds: %.2f)' % (
            s, C[s, 'all'] / g, free / g, C[s, 'back'] / max(1, free)))
        for kind in ('melee', 'ranged'):
            print('     victim %-6s' % kind, '  '.join('%s %.1f' % (mv, C[s, kind, mv] / g) for mv in ('toward', 'same', 'away', 'died')))


if __name__ == '__main__':
    main(sys.argv[1:])
