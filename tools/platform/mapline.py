"""Per map: how each line of the team's bots does in the team's unranked tests, overall and paired on (opponent, map, side).

usage: python -I tools/platform/mapline.py SINCE_ISO [--refresh] [--base LINE] [--min N]
  e.g. python -I tools/platform/mapline.py 2026-11-01T00:00 --refresh

Each unranked match is given to the newest submission uploaded at least two minutes before it was created (as in teamvers.py; a gate that
selects an old version counts for the upload before it, so the lines stay rough at their edges). Versions fall into lines by LINES below. For
each map and line: wins/games, and against the base line the wins on the same (opponent, map, side) keys. Maps are sorted by the base line's win
rate. Matches are cached in data/mapline.json. Sides and opponents repeat across versions, so the paired columns are the ones to trust; a line
with fewer than --min paired games on a map prints no paired number.
"""
import collections, datetime as dt, json, os, subprocess, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CACHE = os.path.join(ROOT, 'data', 'mapline.json')
C = os.path.expandvars(r'%LOCALAPPDATA%\Packages\PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0\LocalCache\local-packages\Python311\Scripts\cambc.exe')
# Which uploads belong to which code line (notes in `cambc submissions list`; findings "How the teammate chejibt001 works").
LINES = {
    'bamboo': [1469, 1471, 1472, 1473, 1477, 1478, 1479, 1480, 1481, 1482, 1483, 1484, 1485, 1486, 1487, 1494, 1495],
    'b10old': [1470, 1474, 1475, 1476, 1488, 1489],
    'v548': [1490, 1491, 1492, 1493, 1496, 1497, 1498, 1499, 1500, 1501, 1502, 1505, 1506, 1507, 1508, 1509, 1510, 1511],
    'v1503': [1503, 1504, 1512],
    '1513': [1513],
}
LINE_OF = {v: k for k, vs in LINES.items() for v in vs}


def run(args):
    for k in range(8):
        r = subprocess.run([C] + args, capture_output=True, text=True, encoding='utf-8')
        out = r.stdout.lstrip('﻿')
        try:
            return json.loads(out[out.index('{'):])
        except (ValueError, json.JSONDecodeError):
            time.sleep(20)
    raise SystemExit('cambc failed: ' + ' '.join(args[:3]))


def fetch(since):
    subs = run(['submissions', 'list', '--json'])['submissions']
    b = None
    while True:  # older pages of submissions, until the window is covered
        last = subs[-1]['version']
        if subs[-1]['createdAt'] < since[:13]: break
        more = run(['submissions', 'list', '--json', '--before', str(last)])['submissions']
        if not more: break
        subs += more
    ms, cur = [], None
    while True:
        a = ['matches', 'list', '--team', 'me', '--kind', 'unranked', '--limit', '100', '--json']
        if cur: a += ['--cursor', cur]
        d = run(a)
        ms += d['matches']
        cur = d.get('nextCursor')
        if not cur or ms[-1]['createdAt'] < since: break
    team = run(['match-groups', 'quota', '--json'])['team']['name']
    data = {'since': since, 'team': team, 'subs': subs, 'ms': [m for m in ms if m['createdAt'] >= since]}
    json.dump(data, open(CACHE, 'w', encoding='utf-8'))
    return data


def t(x):
    return dt.datetime.fromisoformat(x.replace('Z', '+00:00'))


def main():
    args = sys.argv[1:]
    since = args[0]
    base = args[args.index('--base') + 1] if '--base' in args else 'v1503'
    mn = int(args[args.index('--min') + 1]) if '--min' in args else 3
    data = fetch(since) if '--refresh' in args or not os.path.exists(CACHE) else json.load(open(CACHE, encoding='utf-8'))
    subs = sorted(data['subs'], key=lambda s: s['createdAt'])
    games = collections.defaultdict(dict)   # line -> (opp, map, side) -> [wins, n]
    bymap = collections.defaultdict(lambda: collections.defaultdict(lambda: [0, 0]))
    size = {}
    for m in data['ms']:
        tm = t(m['createdAt'])
        v = None
        for s in subs:
            if t(s['createdAt']) + dt.timedelta(minutes=2) <= tm: v = s['version']
        us = [x for x in m['teams'] if x['name'] == data['team']]
        if v is None or not us or us[0]['result'] is None: continue
        line = LINE_OF.get(v)
        if not line: continue
        us = us[0]; op = [x for x in m['teams'] if x is not us][0]
        win = us['result'] == 'win'
        g = games[line].setdefault((op['name'], m['map'], us['side']), [0, 0])
        g[0] += win; g[1] += 1
        bymap[m['map']][line][0] += win; bymap[m['map']][line][1] += 1
        size[m['map']] = len(us['draftPicks'])
    lines = [l for l in LINES if l in games]
    print('map (picks) | ' + ' | '.join(f'{l:^24}' for l in lines) + '   (wins/games, then paired with ' + base + ': wins per game line vs base)')
    def rate(mp):
        w, n = bymap[mp][base]
        return (w / n if n else 2, mp)
    tot = collections.Counter()
    for mp in sorted(bymap, key=rate):
        cells = []
        for l in lines:
            w, n = bymap[mp][l]
            s = f'{w:3}/{n:<3}'
            if l != base:
                keys = [k for k in games[l] if k[1] == mp and k in games[base]]
                pl = sum(games[l][k][0] / games[l][k][1] for k in keys)
                pb = sum(games[base][k][0] / games[base][k][1] for k in keys)
                if len(keys) >= mn:
                    s += f' {pl:4.1f} v {pb:4.1f} ({len(keys):2})'
                    tot[(l, 'l')] += pl; tot[(l, 'b')] += pb; tot[(l, 'n')] += len(keys)
                else:
                    s += ' ' * 17
            else:
                s += ' ' * 17
            cells.append(s)
        print(f'{mp:24} {size.get(mp, 0)} | ' + ' | '.join(cells))
    for l in lines:
        if l != base and tot[(l, 'n')]:
            print(f'{l}: paired over maps {tot[(l, "l")]:.1f} v {tot[(l, "b")]:.1f} of {tot[(l, "n")]}')


if __name__ == '__main__':
    main()
