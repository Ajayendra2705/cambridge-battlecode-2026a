"""Our results per map by bot line, the line read from our own draft, ranked and unranked: python -I tools/platform/draftline.py SINCE_ISO [--refresh]

The two lines draft differently, so no version windows are needed: a draft with Ryth (pick 0) is the Bamboo line (`bamboo`: 3 picks Marcella, Vesper,
Ryth; 4 adds Willow; 5 Heart of Ruin, Vesper, Ryth, Marcella, Willow); a draft with Heart of Ruin (pick 11) and no Ryth is the bot_10 line (`b10`,
which holds the v548 line and 1478 on far maps). Other drafts count as `other`. Each cell is wins/games; the gap is pooled bamboo minus pooled b10.
Opponents differ between the lines, so the gap is a lead, not a measure. Matches are cached in data/draftline.json.
"""
import collections, json, os, subprocess, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CACHE = os.path.join(ROOT, 'data', 'draftline.json')
C = os.path.expandvars(r'%LOCALAPPDATA%\Packages\PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0\LocalCache\local-packages\Python311\Scripts\cambc.exe')


def run(args):
    for k in range(8):
        r = subprocess.run([C] + args, capture_output=True, text=True, encoding='utf-8')
        out = r.stdout.lstrip('﻿')
        try:
            return json.loads(out[out.index('{'):])
        except (ValueError, json.JSONDecodeError):
            time.sleep(15)
    raise SystemExit('cambc failed')


def fetch(since):
    data = {}
    for kind in ('ranked', 'unranked'):
        ms, cur = [], None
        while True:
            a = ['matches', 'list', '--team', 'me', '--kind', kind, '--limit', '100', '--json']
            if cur: a += ['--cursor', cur]
            d = run(a)
            ms += d['matches']
            cur = d.get('nextCursor')
            if not cur or ms[-1]['createdAt'] < since: break
        data[kind] = [m for m in ms if m['createdAt'] >= since]
    json.dump(data, open(CACHE, 'w', encoding='utf-8'))
    return data


def main():
    since = sys.argv[1]
    data = fetch(since) if '--refresh' in sys.argv or not os.path.exists(CACHE) else json.load(open(CACHE, encoding='utf-8'))
    T = collections.defaultdict(collections.Counter)
    picks = collections.Counter()
    for kind, ms in data.items():
        for m in ms:
            us = [x for x in m['teams'] if x['name'] == 'Velvet Tributers']
            if not us or us[0]['result'] is None: continue
            us = us[0]
            p = us['draftPicks']
            line = 'bamboo' if 0 in p else 'b10' if 11 in p else 'other'
            picks[(line, len(p), tuple(sorted(p)))] += 1
            T[m['map']][(kind, line, 'n')] += 1
            T[m['map']][(kind, line, 'w')] += us['result'] == 'win'
            T[m['map']]['size'] = len(p)
    print('commonest drafts:', picks.most_common(10))
    print('map                      picks | ranked bamboo | ranked b10    | unranked bamboo | unranked b10 | pooled bamboo b10  gap')
    rows = []
    for mp, c in T.items():
        bw = c[('ranked', 'bamboo', 'w')] + c[('unranked', 'bamboo', 'w')]; bn = c[('ranked', 'bamboo', 'n')] + c[('unranked', 'bamboo', 'n')]
        vw = c[('ranked', 'b10', 'w')] + c[('unranked', 'b10', 'w')]; vn = c[('ranked', 'b10', 'n')] + c[('unranked', 'b10', 'n')]
        rows.append(((bw / max(1, bn) - vw / max(1, vn)) if bn >= 8 and vn >= 8 else -9, mp, c, bw, bn, vw, vn))
    for gap, mp, c, bw, bn, vw, vn in sorted(rows, key=lambda r: -r[0]):
        def cell(k, l): return f'{c[(k, l, "w")]:3}/{c[(k, l, "n")]:<3} {100 * c[(k, l, "w")] / max(1, c[(k, l, "n")]):3.0f}%'
        print(f'{mp:24} {c["size"]:3}  | {cell("ranked", "bamboo")} | {cell("ranked", "b10")} | {cell("unranked", "bamboo")} | {cell("unranked", "b10")} | {100 * bw / max(1, bn):3.0f}% {100 * vw / max(1, vn):3.0f}% {100 * gap if gap > -9 else 0:+4.0f}')
    tot = collections.Counter()
    for mp, c in T.items():
        for k, v in c.items():
            if k != 'size': tot[k] += v
    print({f'{k[0]} {k[1]}': f'{tot[(k[0], k[1], "w")]}/{tot[(k[0], k[1], "n")]}' for k in tot if k[2] == 'n'})


if __name__ == '__main__':
    main()
