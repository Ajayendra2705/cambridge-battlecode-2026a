"""Print camp clears, gem collections/submissions and per-champion totals for one team from a stats JSON."""
import json, sys

d = json.load(open(sys.argv[1]))
team = 'team' + (sys.argv[2].upper() if len(sys.argv) > 2 else 'A')
print('rounds', d['match'].get('roundsCompleted'), 'outcome', d['match'].get('outcome'))
ev = []
for e in d['events']:
    if e['kind'] in ('campClear', 'gemCollection', 'gemSubmission', 'death', 'kill') and e['owner']['team'] == team:
        for x in e['entries']:
            t = x.get('target')
            tid = t.get('id') if isinstance(t, dict) else t
            ev.append((x['timestamp']['round'], e['owner']['name'], e['kind'], tid, x.get('value'), (x.get('x'), x.get('y'))))
for r in sorted(ev):
    print(*r)
for c in d['champions']:
    if c['team'] == team:
        m = c['metrics']
        print(c['name'], 'dmg', round(m['monsterDamageDone']), 'taken', round(m['monsterDamageTaken']), 'gold', m['earnedGold'],
              'deaths', m['deaths'], 'items', [(i['item'], i['quantity']) for i in c['items']])
