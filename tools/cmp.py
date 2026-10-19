"""Per-champion economy table for both teams of a match summary: python -I tools/cmp.py MATCH_ID_OR_JSON"""
import json, os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
p = sys.argv[1] if sys.argv[1].endswith('.json') else os.path.join(ROOT, 'ladder_replays', sys.argv[1] + '.json')
d = json.load(open(p, encoding='utf-8'))
print('rounds', d['match']['roundsCompleted'], 'winner', d['match']['outcome'])
cols = ['collectedGems', 'submittedGems', 'earnedGold', 'spentGold', 'monsterDamageDone', 'monsterDamageTaken', 'deaths', 'kills']
print(f'{"":16}' + ''.join(f'{c[:9]:>10}' for c in cols))
for team in ('teamA', 'teamB'):
    tot = [0.0] * len(cols)
    for c in d['champions']:
        if c['team'] != team:
            continue
        v = [float(c['metrics'][k]) for k in cols]
        tot = [a + b for a, b in zip(tot, v)]
        print(f'{team[-1]} {c["name"]:14}' + ''.join(f'{x:10.0f}' for x in v))
    print(f'{team[-1]} {"TOTAL":14}' + ''.join(f'{x:10.0f}' for x in tot))
