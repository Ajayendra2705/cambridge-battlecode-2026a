# Per champion type on our side of a multi.py run: deaths, kills, champion damage done and taken, collected gems; bot faults.
import json, glob, sys, os, collections
d = sys.argv[1]; cand = sys.argv[2] if len(sys.argv) > 2 else ''  # optional: one candidate of the run, as in its file names (exp.vd2)
A = collections.defaultdict(collections.Counter); faults = 0; n = 0
for f in glob.glob(os.path.join(d, (cand + '~' if cand else '') + '*.json')):
    us = 'teamA' if f.endswith('~A.json') else 'teamB'
    j = json.load(open(f))
    faults += j['diagnostics']['botFaults'][us]; n += 1
    for c in j['champions']:
        if c['team'] != us: continue
        m = c['metrics']; a = A[c['name']]
        a['g'] += 1; a['deaths'] += int(m['deaths']); a['kills'] += int(m['kills'])
        a['dmg'] += m['championDamageDone']; a['taken'] += m['championDamageTaken']; a['coll'] += int(m['collectedGems'])
print(d, 'games', n, 'bot faults', faults)
for t, a in sorted(A.items()):
    g = a['g']
    print(f"  {t:14} games {g:4} deaths {a['deaths']/g:5.2f} kills {a['kills']/g:5.2f} dmg {a['dmg']/g:6.0f} taken {a['taken']/g:6.0f} coll {a['coll']/g:5.0f}")
