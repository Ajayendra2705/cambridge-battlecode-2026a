"""Deaths per game by the nearest camp group within 5 tiles (-1: none, i.e. on the way between camps), us vs them (h3, 10-28).

usage: python -I tools/helper3/h3_deathgrp.py MAPDUMP R DIR [DIR ...]

MAPDUMP is the md1 dump (data/maps_txt/<map>.txt). Each death's tile is turned into the victim team's own view (as
team A, through the map's symmetry), so group ids are those of tools/helper3/h3_layout.py seen from the victim's own
spawn: "us 4" and "them 4" are the same group of each side's own half. Bands 0-300, 301-600, 601+ up to round R.
"""
import sys, os, collections
sys.path.insert(0, os.path.join(os.getcwd(), 'tools', 'replay'))
import decoded as D
dump, R, dirs = sys.argv[1], int(sys.argv[2]), sys.argv[3:]
CAMP = set('wEg$GM')
L = open(dump, encoding='utf-8').read().splitlines(); W, H = int(L[0].split()[2]), int(L[0].split()[3]); g = [list(l) for l in L[1:1+H]]
tile, groups = {}, []
for y in range(H):
    for x in range(W):
        if g[y][x] in CAMP and (x, y) not in tile:
            st=[(x,y)]; tile[(x,y)]=len(groups); comp=[]
            while st:
                cx,cy=st.pop(); comp.append((cx,cy))
                for dx,dy in ((1,0),(-1,0),(0,1),(0,-1)):
                    t=(cx+dx,cy+dy)
                    if 0<=t[0]<W and 0<=t[1]<H and g[t[1]][t[0]] in CAMP and t not in tile: tile[t]=len(groups); st.append(t)
            groups.append(comp)
SA = {(x, y) for y in range(H) for x in range(W) if g[y][x] == 'S'}; SB = {(x, y) for y in range(H) for x in range(W) if g[y][x] == 's'}
TF = [lambda x, y: (W-1-x, H-1-y), lambda x, y: (W-1-x, y), lambda x, y: (x, H-1-y)]
tf = next((f for f in TF if {f(*p) for p in SA} == SB), TF[0])
def nearest(p):
    best = min(((max(abs(p[0]-x), abs(p[1]-y)), i) for i, c in enumerate(groups) for x, y in c))
    return best[1] if best[0] <= 5 else -1
C = collections.Counter(); ng = 0
for us, res, mp, meta, rows in D.games(dirs):
    ng += 1; n = len(rows[0]['c'])
    for a, b in zip(rows, rows[1:]):
        if b['r'] > R: break
        for i in range(n):
            pc, c = a['c'][i], b['c'][i]
            if pc['a'] and not c['a'] and 'x' in pc:
                p = (pc['x'], pc['y']); t = pc['t']
                if t == 1: p = tf(*p)   # into the victim team's own (team A) view
                w = 'us' if t == us else 'them'
                band = '0-300' if b['r'] <= 300 else '301-600' if b['r'] <= 600 else '601+'
                C[w, nearest(p), band] += 1; C[w, nearest(p), 'all'] += 1
print(f'{ng} games, deaths per game to r{R} by the nearest group within 5 (ids seen from the victim side), us / them')
for gi in sorted({k[1] for k in C}):
    print(f'{gi:3}  all {C["us", gi, "all"]/ng:5.2f} / {C["them", gi, "all"]/ng:5.2f}   ' + '  '.join(f'{bd} {C["us", gi, bd]/ng:4.2f}/{C["them", gi, bd]/ng:4.2f}' for bd in ('0-300', '301-600', '601+')))
