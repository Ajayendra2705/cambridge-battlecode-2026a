import json,sys,collections,os,statistics as st
P='C:/Users/ajiit/Desktop/Future/Projects/Cambridge Battlecode/'
D=sys.argv[1]; rows=[l.split() for l in open(P+D+'/index.txt')]
G=collections.defaultdict(list)
for mid,mp,side,res in rows:
    p=P+f'ladder_replays/{mid}.json'
    if not os.path.exists(p): continue
    d=json.load(open(p,encoding='utf-8')); us='team'+side.upper()
    def ch_at(metric,team,r):
        tot=0
        for t in d['championTimelines']:
            if t['metric']!=metric or t['owner'].get('team')!=team: continue
            rr=0; v=0
            for run in t['runs']:
                if rr<=r: v=float(run['value'])
                rr+=run['duration']
            tot+=v
        return tot
    def team_at(metric,team,r):
        for t in d['teamTimelines']:
            if t['metric']!=metric or t['owner']!=team: continue
            rr=0; v=0
            for run in t['runs']:
                if rr<=r: v=float(run['value'])
                rr+=run['duration']
            return v
        return 0
    them='teamB' if us=='teamA' else 'teamA'
    ev=collections.Counter()
    for e in d['events']:
        tm='U' if e['owner'].get('team')==us else 'T'
        for x in e['entries']:
            if x['timestamp']['round']>600: continue
            if e['kind'] in ('gemLoss','gemCollection','gemSubmission','campClear'): ev[tm,e['kind']]+=1
            if e['kind']=='gemLoss': ev[tm,'lostamt']+=float(x.get('amount') or x.get('value') or 0)
    cat='win' if res=='win' else ('blowout' if team_at('submittedGems',us,3000)<500 else 'close')
    G[cat].append((ch_at('collectedGems',us,600),ch_at('collectedGems',them,600),ev['U','campClear'],ev['T','campClear'],ev['U','gemLoss'],ev['T','gemLoss'],ev['U','lostamt'],ev['T','lostamt'],ev['U','gemSubmission'],ev['T','gemSubmission'],mp))
for c,v in G.items():
    m=lambda i: st.mean(x[i] for x in v)
    print(f"{c:8} n {len(v):2} | to r600: collected us {m(0):.0f} them {m(1):.0f} | clears {m(2):.1f}/{m(3):.1f} | gemLoss events {m(4):.1f}/{m(5):.1f} amount {m(6):.0f}/{m(7):.0f} | submissions {m(8):.1f}/{m(9):.1f}")
print('blowout maps', collections.Counter(x[10] for x in G['blowout']).most_common())
