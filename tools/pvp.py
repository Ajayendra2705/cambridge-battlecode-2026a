"""PvP testbed: BOT vs a pool of opponents on fight-heavy maps, both sides, with exact kill/death counts.

usage: python -I tools/pvp.py BOT [--pool a,b,c] [--maps m1,m2] [--jobs N] [--rounds R]
Prints per opponent: wins, our kills/deaths, champion damage dealt/taken, submitted gems; then totals.
Each game writes a JSON match summary (run-batch --statistics) next to its replay.
"""
import argparse, collections, json, os, subprocess, sys, time

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
CAMBC = os.path.expandvars(r'%LOCALAPPDATA%\Packages\PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0'
                           r'\LocalCache\local-packages\Python311\Scripts\cambc.exe')

ap = argparse.ArgumentParser()
ap.add_argument('bot')
ap.add_argument('--pool', default='n_rec,n_agg,n_hunt')
ap.add_argument('--maps', default='00collision,00eight,00fragment,01elk-arena,00interlock,01hooks')
ap.add_argument('--jobs', type=int, default=10)
ap.add_argument('--rounds', type=int, default=0)
args = ap.parse_args()
pool, maps = args.pool.split(','), args.maps.split(',')

for bot in {args.bot, *pool}:
    r = subprocess.run([CAMBC, 'build', bot, '--release'], cwd=ROOT, capture_output=True, text=True)
    if r.returncode:
        print(bot, r.stdout[-3000:], r.stderr[-3000:]); sys.exit(1)

out_dir = os.path.join(ROOT, 'replays', 'pvp-' + args.bot + '-' + time.strftime('%H%M%S'))
os.makedirs(out_dir, exist_ok=True)
rows, jobs = [], []
for opp in pool:
    for m in maps:
        for a, b, us in ((args.bot, opp, 'teamA'), (opp, args.bot, 'teamB')):
            name = f'{opp}-{m}-{us[-1]}'
            rows.append(f'"../../bots/{a}" "../../bots/{b}" "../../maps/{m}.map26a" "{name}.repl26a" --statistics "{name}.json" --json')
            jobs.append((opp, m, us, name))
with open(os.path.join(out_dir, 'matches.txt'), 'w') as f:
    f.write('\n'.join(rows) + '\n')
cmd = [CAMBC, 'run-batch', os.path.join(out_dir, 'matches.txt'), '--jobs', str(args.jobs), '--release']
if args.rounds:
    cmd += ['--rounds', str(args.rounds)]
r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
open(os.path.join(out_dir, 'batch.log'), 'w').write(r.stdout + r.stderr)

keys = ['kills', 'deaths', 'championDamageDone', 'championDamageTaken']
per = collections.defaultdict(collections.Counter)
for opp, m, us, name in jobs:
    p = os.path.join(out_dir, name + '.json')
    if not os.path.exists(p):
        print('missing', name); continue
    d = json.load(open(p, encoding='utf-8'))
    c = per[opp]
    c['games'] += 1
    c['wins'] += d['match']['outcome'] == us
    for t in d['teams']:
        c['gems' if t['team'] == us else 'their_gems'] += int(t['submittedGems'])
    for ch in d['champions']:
        if ch['team'] == us:
            for k in keys: c[k] += float(ch['metrics'][k])
tot = collections.Counter()
print(f'{"opponent":12} games wins  kills deaths  dmg_done dmg_taken  gems  their')
for opp, c in list(per.items()) + [('TOTAL', None)]:
    if c is None: c = tot
    else: tot.update(c)
    print(f'{opp:12} {c["games"]:5} {c["wins"]:4} {c["kills"]:6.0f} {c["deaths"]:6.0f} {c["championDamageDone"]:9.0f} '
          f'{c["championDamageTaken"]:9.0f} {c["gems"]:5} {c["their_gems"]:5}')
import re, zipfile
acts = collections.Counter()
for opp, m, us, name in jobs:
    p = os.path.join(out_dir, name + '.repl26a')
    if not os.path.exists(p): continue
    text = zipfile.ZipFile(p).read(f'team-{us[-1].lower()}.stdout').decode('latin1')
    for a in re.findall(r'^D\d+ s\d r\d+ hp=\S+ (\S+)', text, re.M): acts[a] += 1
print('our deaths by activity:', dict(acts.most_common(8)))
champ = collections.defaultdict(collections.Counter)
for opp, m, us, name in jobs:
    p = os.path.join(out_dir, name + '.json')
    if not os.path.exists(p): continue
    for ch in json.load(open(p, encoding='utf-8'))['champions']:
        if ch['team'] == us:
            c = champ[ch['name']]; c['n'] += 1
            for k in ('monsterDamageDone', 'earnedGold', 'deaths', 'submittedGems'): c[k] += float(ch['metrics'][k])
print('per champion (avg): ' + '  '.join(f'{k}: mon {c["monsterDamageDone"]/c["n"]:.0f} gold {c["earnedGold"]/c["n"]:.0f} gems {c["submittedGems"]/c["n"]:.0f} D {c["deaths"]/c["n"]:.1f}' for k, c in champ.items()))
print('dir', out_dir)
