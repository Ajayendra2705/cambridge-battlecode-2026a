# python -I tools/replay/fight.py DIR... : fights = champion deaths clustered (<=12 rounds apart, <=10 tiles); trade + metrics us vs them
import json,sys,collections,os
P=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..') + '/'
M={s:collections.Counter() for s in 'UT'}; n=0
F=collections.Counter(); FR=collections.Counter(); FW=collections.Counter(); first=collections.Counter()
pick={s:collections.Counter() for s in 'UT'}; kd={s:collections.Counter() for s in 'UT'}
for D in sys.argv[1:]:
  for l in open(P+D+'/index.txt'):
    mid,mp,side,res=l.split(); us='team'+side.upper(); p=P+f'data/summaries/{mid}.json'
    if not os.path.exists(p): continue
    d=json.load(open(p,encoding='utf-8')); n+=1; W=d['match'].get('width') or 40
    for c in d['champions']:
      s='U' if c['team']==us else 'T'; pick[s][c['name']]+=1
      for k,v in c['metrics'].items():
        try: M[s][k]+=float(v)
        except: pass
      kd[s][c['name'],'k']+=float(c['metrics'].get('kills',0)); kd[s][c['name'],'d']+=float(c['metrics'].get('deaths',0))
    ds=[]
    for e in d['events']:
      if e['kind']=='death':
        for x in e['entries']:
          if x['context']=='champion': ds.append((x['timestamp']['round'],'U' if e['owner']['team']==us else 'T',x.get('x'),x.get('y')))
    ds.sort(); fights=[]
    for dv in ds:
      for f in fights:
        if dv[0]-f[-1][0]<=12 and abs(dv[2]-f[-1][2])<=10 and abs(dv[3]-f[-1][3])<=10: f.append(dv); break
      else: fights.append([dv])
    for f in fights:
      u=sum(1 for x in f if x[1]=='U'); t=len(f)-u
      F['fights']+=1; F['U_dead']+=u; F['T_dead']+=t
      key='win' if t>u else ('loss' if u>t else 'even'); FR[key]+=1; FW[res,key]+=1
      first[f[0][1]]+=1
print('games',n)
for k in ('kills','deaths','assists','championDamageDone','championDamageTaken','healingDone','shieldingDone','monsterDamageDone','earnedGold','spentGold','collectedGems','submittedGems'):
  print(f'{k:20} us {M["U"][k]/n:8.0f} them {M["T"][k]/n:8.0f}')
print('fights/game',round(F['fights']/n,1),'outcomes',dict(FR),'first to die in fight',dict(first))
print('by game result',dict(FW))
print('their picks',pick['T'].most_common(8))
for s in 'UT': print(s,'K/D by champ',{c:f"{kd[s][c,'k']/max(pick[s][c],1):.1f}/{kd[s][c,'d']/max(pick[s][c],1):.1f}" for c,_ in pick[s].most_common(7)})
