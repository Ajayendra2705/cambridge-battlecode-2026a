"""Paired screen of several candidates against a base candidate in the same local multi.py run.
usage: python -I tools/local/lscreen.py RUNDIR BASECAND [ROUND]   (CAND as in file names, e.g. exp.b10n; ROUND for the
collected and tributed columns, default 1000). Pairs every candidate's game with the base's game on the same pool bot,
map and side, and prints per candidate the mean difference and its standard error for: wins, final margin (tributed us
minus them), our collected and tributed by ROUND, the rivals' tributed by ROUND, deaths, kills, gems lost on death,
camp clears, and the bot faults of our side (diagnostics.botFaults)."""
import collections, glob, json, math, os, sys

def at(runs, r):
    t, v = 0, 0
    for run in runs:
        if t >= r: break
        v = int(run['value']); t += run['duration']
    return v

def game(path, side, R):
    j = json.load(open(path, encoding='utf-8'))
    us = 'team' + side
    m = {'win': float(j['match']['outcome'] == us), 'fault': float(j['diagnostics']['botFaults'].get(us, 0))}
    sub = {t['team']: int(t['submittedGems']) for t in j['teams']}
    m['margin'] = sum(v if k == us else -v for k, v in sub.items())
    for k in ('deaths', 'kills'):
        m[k] = sum(float(c['metrics'][k]) for c in j['champions'] if c['team'] == us)
    m['lost'] = sum(float(x['value']) for e in j['events'] if e['kind'] == 'gemLoss' and e['owner'].get('team') == us
                    for x in e['entries'])
    m['caps'] = sum(len(e['entries']) for e in j['events'] if e['kind'] == 'campClear' and e['owner'].get('team') == us)
    m['coll R'] = sum(at(t['runs'], R) for t in j['championTimelines']
                      if t['metric'] == 'collectedGems' and t['owner'].get('team') == us)
    for t in j['teamTimelines']:
        if t['metric'] == 'submittedGems':
            m['trib R' if t['owner'] == us else 'their trib R'] = at(t['runs'], R)
    return m

def main():
    d, base = sys.argv[1], sys.argv[2]
    R = int(sys.argv[3]) if len(sys.argv) > 3 else 1000
    runs = collections.defaultdict(dict)
    for f in glob.glob(os.path.join(d, '*.json')):
        cand, opp, mp, side = os.path.basename(f)[:-5].split('~')
        runs[cand][(opp, mp, side)] = (f, side)
    B = {k: game(f, s, R) for k, (f, s) in runs[base].items()}
    keys = ['win', 'margin', 'coll R', 'trib R', 'their trib R', 'deaths', 'kills', 'lost', 'caps']
    print(f'base {base}: {len(B)} games; columns: new - base per game (+- se); R = r{R}')
    print(f"{'candidate':16} {'n':>4} {'faults':>6} " + ' '.join(f'{k:>16}' for k in keys))
    for cand in sorted(runs):
        if cand == base: continue
        ks = [k for k in runs[cand] if k in B]
        N = {k: game(*runs[cand][k], R) for k in ks}
        cells = []
        for key in keys:
            diff = [N[k][key] - B[k][key] for k in ks]
            mu = sum(diff) / len(diff)
            se = math.sqrt(sum((x - mu) ** 2 for x in diff) / (len(diff) - 1) / len(diff)) if len(diff) > 1 else 0
            cells.append(f'{mu:+8.2f} +-{se:6.2f}')
        print(f'{cand:16} {len(ks):4} {sum(N[k]["fault"] for k in ks):6.0f} ' + ' '.join(f'{c:>16}' for c in cells))
    print(f"{'base means':16} {len(B):4} {sum(v['fault'] for v in B.values()):6.0f} "
          + ' '.join(f'{sum(v[k] for v in B.values()) / len(B):16.2f}' for k in keys))

if __name__ == '__main__':
    main()
