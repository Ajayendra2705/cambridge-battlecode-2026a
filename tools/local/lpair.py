# Paired local games: python -I lpair.py BASEDIR BASECAND NEWDIR NEWCAND   (multi.py folders; CAND as in file names, e.g. exp.bb2)
# Prints flips (L->W, W->L) by map size and the maps that flipped, plus collected and deaths per game.
import sys, os, glob, json, collections
sz = json.load(open('data/map_sizes.json'))
def load(d, c):
    out = {}
    for f in glob.glob(os.path.join(d, c + '~*.json')):
        _, pool, mp, side = os.path.basename(f)[:-5].split('~')
        j = json.load(open(f, encoding='utf-8'))
        us = [ch for ch in j['champions'] if ch['team'][-1] == side]
        out[(pool, mp, side)] = (j['match']['outcome'].endswith(side), sum(float(ch['metrics']['collectedGems']) for ch in us),
                                 sum(float(ch['metrics']['deaths']) for ch in us))
    return out
A, B = load(sys.argv[1], sys.argv[2]), load(sys.argv[3], sys.argv[4])
ks = [k for k in A if k in B]
up = [k for k in ks if B[k][0] and not A[k][0]]; dn = [k for k in ks if A[k][0] and not B[k][0]]
print(f'{len(ks)} paired games: base {sum(A[k][0] for k in ks)} wins, new {sum(B[k][0] for k in ks)}; L->W {len(up)}, W->L {len(dn)}')
for s in (3, 4, 5):
    kk = [k for k in ks if sz.get(k[1].replace('-', '_')) == s]
    if kk: print(f'  size {s}: {len(kk)} games, wins {sum(A[k][0] for k in kk)} -> {sum(B[k][0] for k in kk)}, collected {sum(A[k][1] for k in kk)/len(kk):.0f} -> {sum(B[k][1] for k in kk)/len(kk):.0f}, deaths {sum(A[k][2] for k in kk)/len(kk):.2f} -> {sum(B[k][2] for k in kk)/len(kk):.2f}')
c = collections.Counter(k[1] for k in up); d = collections.Counter(k[1] for k in dn)
print('  L->W maps:', ' '.join(f'{m}:{n}' for m, n in c.most_common()))
print('  W->L maps:', ' '.join(f'{m}:{n}' for m, n in d.most_common()))
