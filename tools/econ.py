"""Where each team's gems came from: python -I tools/econ.py MATCH_ID_OR_JSON [rounds]

Per team: gems collected by source (camp group id and its gem value, or champion kills), gems lost, and a
cumulative timeline of collected gems every `rounds` rounds (default 50).
"""
import collections, json, os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
p = sys.argv[1] if sys.argv[1].endswith('.json') else os.path.join(ROOT, 'ladder_replays', sys.argv[1] + '.json')
step = int(sys.argv[2]) if len(sys.argv) > 2 else 50
d = json.load(open(p, encoding='utf-8'))
end = d['match']['roundsCompleted']
print('rounds', end, 'winner', d['match']['outcome'])
for team in ('teamA', 'teamB'):
    src = collections.Counter()
    caps = collections.Counter()
    lost = 0
    timeline = collections.Counter()
    for e in d['events']:
        if e['owner']['team'] != team:
            continue
        for x in e['entries']:
            r = x['timestamp']['round']
            if e['kind'] == 'gemCollection':
                v = int(x['value'])
                key = f"g{x['target']['id']}" if x['context'] == 'campGroup' else x['context']
                src[key] += v
                caps[key] += 1
                timeline[r // step] += v
            elif e['kind'] == 'gemLoss':
                lost += int(x['value'])
    print(f'{team}: collected {sum(src.values())} lost {lost}')
    print('  by source:', ', '.join(f'{k} {v}/{caps[k]}x' for k, v in src.most_common()))
    acc = 0
    row = []
    for i in range(end // step + 1):
        acc += timeline[i]
        row.append(f'{(i + 1) * step}:{acc}')
    print('  cumulative:', ' '.join(row))
