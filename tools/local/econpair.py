# Paired economy readout of local variants against a base, game by game (local games replay exactly):
#   python -I tools/local/econpair.py BASEDIR BASECAND NEWDIR NEWCAND [NEWCAND...]   (from the repo root)
# CAND as in the file names (exp.bb458c). Pairs the games both runs played (same opponent, map, side) and prints, per
# team size and overall: games, the mean difference new - base of gems collected, captures (campClear entries of our
# team) and deaths per game, and of wins, each with its standard error over the paired games.
import collections, glob, json, math, os, sys

sz = json.load(open('data/map_sizes.json'))


def load(d, c):
    out = {}
    for f in glob.glob(os.path.join(d, c + '~*.json')):
        _, opp, mp, side = os.path.basename(f)[:-5].split('~')
        j = json.load(open(f, encoding='utf-8'))
        us = 'team' + side
        coll = sum(float(ch['metrics']['collectedGems']) for ch in j['champions'] if ch['team'] == us)
        deaths = sum(float(ch['metrics']['deaths']) for ch in j['champions'] if ch['team'] == us)
        caps = sum(len(e['entries']) for e in j['events'] if e['kind'] == 'campClear' and e['owner'].get('team') == us)
        out[(opp, mp, side)] = (coll, caps, deaths, int(j['match']['outcome'] == us), sz.get(mp.replace('-', '_')))
    return out


def ms(v):
    if len(v) < 2: return 0.0, 0.0
    m = sum(v) / len(v)
    return m, math.sqrt(sum((x - m) ** 2 for x in v) / (len(v) - 1) / len(v))


base = load(sys.argv[1], sys.argv[2])
for cand in sys.argv[4:]:
    new = load(sys.argv[3], cand)
    keys = [k for k in new if k in base]
    print(f'{cand} against {sys.argv[2]}: {len(keys)} paired games')
    for size in (3, 4, 5, None):
        ks = [k for k in keys if size is None or base[k][4] == size]
        if len(ks) < 2: continue
        row = []
        for i, name in ((0, 'collected'), (1, 'captures'), (2, 'deaths'), (3, 'wins')):
            m, se = ms([new[k][i] - base[k][i] for k in ks])
            row.append(f'{name} {m:+7.2f} +- {se:5.2f}')
        b = sum(base[k][0] for k in ks) / len(ks)
        print(f'  {"all" if size is None else f"{size}v{size}"}: {len(ks):4} games, base collected {b:6.1f}  ' + '  '.join(row))
