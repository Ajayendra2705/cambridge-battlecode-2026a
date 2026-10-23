"""Test many candidate bots at once on all cores: every candidate vs every pool bot on every map, both sides.

usage: python -I tools/multi.py CAND1,CAND2,... [--pool a,b] [--maps m1,m2] [--jobs 12]
One run-batch over the whole grid; prints one row per candidate (wins, kills, deaths, gem margin, flee deaths).
"""
import argparse, collections, json, os, re, subprocess, sys, time, zipfile
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
CAMBC = os.path.expandvars(r'%LOCALAPPDATA%\Packages\PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0'
                           r'\LocalCache\local-packages\Python311\Scripts\cambc.exe')
ap = argparse.ArgumentParser()
ap.add_argument('cands')
ap.add_argument('--pool', default='n_q,n_d5,n_hunt,n_cr')
ap.add_argument('--maps', default='00collision,00eight,00fragment,01elk-arena,00interlock,01hooks,00contest,01broken-curve,00elkring,01concentrated-wealth')
ap.add_argument('--jobs', type=int, default=16)
ap.add_argument('--keep', action='store_true', help='keep .repl26a replays (deleted by default to save disk)')
args = ap.parse_args()
cands, pool, maps = args.cands.split(','), args.pool.split(','), args.maps.split(',')

def build(bot):
    r = subprocess.run([CAMBC, 'build', bot, '--release'], cwd=ROOT, capture_output=True, text=True)
    return bot, r.returncode, r.stdout[-1500:] + r.stderr[-1500:]
with ThreadPoolExecutor(4) as ex:
    for bot, rc, log in ex.map(build, sorted(set(cands + pool))):
        if rc: print('build failed', bot, log); sys.exit(1)

out = os.path.join(ROOT, 'replays', 'multi-' + time.strftime('%H%M%S'))
os.makedirs(out, exist_ok=True)
rows, jobs = [], []
for c in cands:
    for opp in pool:
        for m in maps:
            for a, b, us in ((c, opp, 'teamA'), (opp, c, 'teamB')):
                name = f'{c}~{opp}~{m}~{us[-1]}'
                rows.append(f'"../../bots/{a}" "../../bots/{b}" "../../maps/{m}.map26a" "{name}.repl26a" --statistics "{name}.json" --json')
                jobs.append((c, us, name))
open(os.path.join(out, 'matches.txt'), 'w').write('\n'.join(rows) + '\n')
subprocess.run([CAMBC, 'run-batch', os.path.join(out, 'matches.txt'), '--jobs', str(args.jobs), '--release'], cwd=ROOT,
               capture_output=True, text=True)

res = collections.defaultdict(collections.Counter)
for c, us, name in jobs:
    p = os.path.join(out, name + '.json')
    if not os.path.exists(p): continue
    d = json.load(open(p, encoding='utf-8'))
    r = res[c]
    r['games'] += 1
    r['wins'] += d['match']['outcome'] == us
    r['rnd'] += d['match']['roundsCompleted'] if d['match']['outcome'] == us else 2000
    for t in d['teams']:
        r['margin'] += int(t['submittedGems']) * (1 if t['team'] == us else -1)
    for ch in d['champions']:
        if ch['team'] == us:
            r['kills'] += float(ch['metrics']['kills']); r['deaths'] += float(ch['metrics']['deaths'])
            r['gold'] += float(ch['metrics']['earnedGold'])
            r['mon_' + ch['name']] += float(ch['metrics']['monsterDamageDone']); r['n_' + ch['name']] += 1
    for e in d['events']:
        if e['kind'] == 'campClear' and e['owner'].get('team') == us: r['caps'] += len(e['entries'])
        if e['kind'] == 'gemLoss' and e['owner'].get('team') == us:
            for x in e['entries']: r['lost'] += float(x['value'])
    for tl in d.get('championTimelines', []):
        if tl['owner'].get('team') == us and tl['metric'] == 'gems' and tl['runs']: r['carried'] += float(tl['runs'][-1]['value'])
        if tl['owner'].get('team') == us and tl['metric'] == 'collectedGems' and tl['runs']: r['coll'] += float(tl['runs'][-1]['value'])
    text = zipfile.ZipFile(os.path.join(out, name + '.repl26a')).read(f'team-{us[-1].lower()}.stdout').decode('latin1')
    r['flee'] += len(re.findall(r'^D\d+ s\d r\d+ hp=\S+ flee', text, re.M))
print(f'{"candidate":14} games wins  kills deaths  flee  margin   gold/g caps/g coll/g lost/g carry/g')
for c in cands:
    r = res[c]
    print(f'{c:14} {r["games"]:5} {r["wins"]:4} {r["kills"]:6.0f} {r["deaths"]:6.0f} {r["flee"]:5} {r["margin"]:+7} {r["gold"]/max(1,r["games"]):7.0f} {r["caps"]/max(1,r["games"]):5.1f} {r["coll"]/max(1,r["games"]):6.0f} {r["lost"]/max(1,r["games"]):6.0f} {r["carried"]/max(1,r["games"]):6.0f}')
for c in cands:
    r = res[c]
    print(f'  {c}: rnd {r["rnd"] / max(1, r["games"]):.0f} ' + ' '.join(f'{k[4:]}={r[k] / max(1, r["n_" + k[4:]]):.0f}' for k in sorted(r) if k.startswith('mon_')))
if not args.keep:
    for f in os.listdir(out):
        if f.endswith('.repl26a'): os.remove(os.path.join(out, f))
print('dir', out)
