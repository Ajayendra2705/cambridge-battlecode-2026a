"""Emblem choices made in the same turn as a strength emblem completed (helper agent h2, the stale-strength shop bug).

usage: python -I tools/helper/h2_spree.py FIGHTDIR [FIGHTDIR...]
  FIGHTDIR  a decoded run (data/fights/RUN_PANEL with index.txt, engine 2.0.0 games)

`shop()` judges each new emblem with the strength of the turn's snapshot, so when one shopping turn completes a strength
emblem and starts the next, the next is chosen as if the first had not been bought, which favours another strength emblem
over a health one (local probe h2pr3l). For our strength users (Vesper, Vendetta, Varg) this finds every emblem start
(the first shard of a non-Treasure family appears) and splits them by whether a strength emblem was completed in the same
round step; for each class it prints the share of starts that are strength (Power, Bruiser and other families of strength)
against health (Durability, Jungle, ... of health). Ours only: the side in index.txt.
"""
import collections, glob, gzip, json, os, sys

FAMILIES2 = ('monster', 'power', 'durability', 'treasure', 'jungle', 'home', 'bruiser',
             'tribute', 'capture', 'prospector', 'hunter', 'skirmish', 'greed', 'collectors')
STATS = ('str', 'focus', 'hp')
STRENGTH_USERS = {1: 'vesper', 2: 'vendetta', 10: 'varg'}


def item(i):
    return FAMILIES2[i // 6], STATS[(i // 2) % 3], 'emblem' if i % 2 else 'shard'


tab = collections.Counter()
games = 0
for d in sys.argv[1:]:
    sides = {}
    for line in open(os.path.join(d, 'index.txt'), encoding='utf-8'):
        f = line.split()
        if len(f) >= 3: sides[f[0]] = 0 if f[2] == 'a' else 1
    for path in glob.glob(os.path.join(d, '*.jsonl.gz')):
        gid = os.path.basename(path).split('.')[0]
        if gid not in sides: continue
        us = sides[gid]
        games += 1
        prev = {}
        with gzip.open(path, 'rt') as fh:
            meta = json.loads(fh.readline())
            if meta.get('engine') != 'v2_0_0': continue
            for line in fh:
                r = json.loads(line)
                for k, c in enumerate(r['c']):
                    if c.get('t') != us or c.get('ty') not in STRENGTH_USERS: continue
                    now = collections.Counter({i: n for i, n in c.get('it', [])})
                    old = prev.get(k)
                    prev[k] = now
                    if old is None: continue
                    str_emblem_done = any(item(i)[1] == 'str' and item(i)[2] == 'emblem' and now[i] > old[i] for i in now)
                    for i in now:
                        fam, stat, kind = item(i)
                        if kind != 'shard' or fam == 'treasure' or old[i] > 0 or now[i] == 0: continue
                        cls = 'same turn as a strength emblem' if str_emblem_done else 'other turns'
                        tab[cls, 'strength' if stat == 'str' else stat] += 1
                        tab[cls, 'n'] += 1
print(f'{games} games')
for cls in ('same turn as a strength emblem', 'other turns'):
    n = tab[cls, 'n']
    print(f'{cls:32} emblem starts {n:4}: strength {tab[cls, "strength"] / max(1, n):.0%}, health {tab[cls, "hp"] / max(1, n):.0%}, '
          f'focus {tab[cls, "focus"] / max(1, n):.0%}')
