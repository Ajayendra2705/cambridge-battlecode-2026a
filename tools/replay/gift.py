# usage: python -I tools/replay/gift.py DIR... (decoded dirs with index.txt)
# Per game: our camp hits by who captured that group life (us / them / nobody), and the same for the rivals' hits.
# Groups: camps whose attack-target tiles touch (Chebyshev 1). A group life ends when all its camps are dead; the
# capture side is the side with more champion-rounds within 1 tile of the group's camps until the camps come back.
import gzip, json, os, sys, collections
sys.stdout.reconfigure(encoding='utf-8')
dirs = sys.argv[1:]
tot = collections.Counter(); bymap = collections.defaultdict(collections.Counter)
for d in dirs:
    idx = [l.split() for l in open(os.path.join(d, 'index.txt')) if l.strip()]
    for mid, mp, side, res in idx:
        f = os.path.join(d, mid + '.jsonl.gz')
        if not os.path.exists(f): continue
        us = 0 if side == 'a' else 1
        rows = [json.loads(l) for l in gzip.open(f, 'rt') if l.strip()]
        pos = {}; hits = []  # (round, side, camp)
        for r in rows[1:]:
            rr = r.get('r', 0)
            if rr > 1000: break
            for i, acts in enumerate(r.get('act', [])):
                t = r['c'][i]['t'] if i < len(r['c']) else None
                for a in acts:
                    if a[0] == 'attack' and len(a) >= 5 and a[3] == 'm':
                        pos[a[4]] = (a[1], a[2]); hits.append((rr, t, a[4]))
        # groups by touching camp tiles
        ids = list(pos); parent = {i: i for i in ids}
        def find(i):
            while parent[i] != i: parent[i] = parent[parent[i]]; i = parent[i]
            return i
        for a in ids:
            for b in ids:
                if a < b and max(abs(pos[a][0]-pos[b][0]), abs(pos[a][1]-pos[b][1])) <= 1: parent[find(a)] = find(b)
        grp = {i: find(i) for i in ids}
        members = collections.defaultdict(list)
        for i in ids: members[grp[i]].append(i)
        # life ends: all members dead (mh 0) after being alive; capture side until any member alive again
        alive_prev = {}; lives = collections.defaultdict(list)  # gid -> list of (end_round, capturer)
        state = {}  # gid -> ('dead', start, counts) or 'alive'
        for r in rows[1:]:
            rr = r.get('r', 0)
            if rr > 1100: break
            mh = r.get('mh', [])
            for g, mem in members.items():
                alive = any(m < len(mh) and mh[m] > 0 for m in mem)
                st = state.get(g)
                if not alive and (st is None or st == 'alive'):
                    state[g] = ['dead', rr, collections.Counter()]
                elif not alive and isinstance(st, list):
                    for c in r['c']:
                        if c.get('x') is None: continue
                        if any(max(abs(c['x']-pos[m][0]), abs(c['y']-pos[m][1])) <= 1 for m in mem): st[2][c['t']] += 1
                elif alive and isinstance(st, list):
                    cap = st[2].most_common(1)[0][0] if st[2] else None
                    lives[g].append((st[1], cap)); state[g] = 'alive'
                elif alive: state[g] = 'alive'
        for g, st in state.items():
            if isinstance(st, list): lives[g].append((st[1], st[2].most_common(1)[0][0] if st[2] else None))
        for rr, t, cid in hits:
            g = grp[cid]; cap = 'none'
            for end, c in sorted(lives[g]):
                if end >= rr:
                    cap = 'none' if c is None else ('own' if c == t else 'other'); break
            who = 'us' if t == us else 'them'
            tot[(who, cap)] += 1; bymap[mp][(who, cap)] += 1
def line(c, who):
    n = sum(v for (w, _), v in c.items() if w == who) or 1
    return f"{who}: hits {n:6d} own {c[(who,'own')]/n:5.1%} other {c[(who,'other')]/n:5.1%} none {c[(who,'none')]/n:5.1%}"
print(line(tot, 'us')); print(line(tot, 'them'))
rows = sorted(bymap.items(), key=lambda kv: -kv[1][('us','other')])
for mp, c in rows[:15]:
    print(f"{mp:22}", line(c, 'us'), '|', line(c, 'them'))
