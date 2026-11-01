# Paired wins of two candidates per team size over every common opponent (not only the pool):
#   python -I tools/local/pairall.py DIR_A CAND_A DIR_B CAND_B   (from the repo root; CAND as in the file names)
# Per size: all common opponents (games, wins A -> B, paired difference B - A +- se), then the pool opponents alone.
import glob, json, math, os, sys

sz = json.load(open('data/map_sizes.json'))


def load(d, c):
    out = {}
    for f in glob.glob(os.path.join(d, c + '~*.json')):
        _, opp, mp, side = os.path.basename(f)[:-5].split('~')
        out[(opp, mp, side)] = json.load(open(f, encoding='utf-8'))['match']['outcome'] == 'team' + side
    return out


def line(tag, ks, A, B):
    d = [B[k] - A[k] for k in ks]
    if len(d) < 2:
        return f'{tag}: {len(d)} games'
    mu = sum(d) / len(d)
    se = math.sqrt(sum((x - mu) ** 2 for x in d) / (len(d) - 1) / len(d))
    return f'{tag}: {len(ks)} games  wins {sum(A[k] for k in ks)} -> {sum(B[k] for k in ks)}  diff {mu:+.3f} +- {se:.3f}'


A, B = load(sys.argv[1], sys.argv[2]), load(sys.argv[3], sys.argv[4])
for s in (3, 4, 5):
    ks = [k for k in A if k in B and sz.get(k[1].replace('-', '_')) == s]
    print(f'{s}v{s}  ' + line('all', ks, A, B) + '  |  ' + line('pool', [k for k in ks if k[0].startswith('pool.')], A, B))
