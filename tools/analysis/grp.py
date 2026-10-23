# python -I grp.py DIR... : grouping behaviour us vs them from summary events (positions at events)
import json,sys,collections,math,os
P='C:/Users/ajiit/Desktop/Future/Projects/Cambridge Battlecode/'
KP={s:collections.Counter() for s in 'UT'}   # participants per champion kill (kills made BY side)
NB={s:collections.Counter() for s in 'UT'}   # nearest same-team champion distance at collect/clear events
CC={s:collections.Counter() for s in 'UT'}   # clears per game with ally partner within 6 (camp clears)
DD={s:[] for s in 'UT'}
n=0
for D in sys.argv[1:]:
  for l in open(P+D+'/index.txt'):
    mid,mp,side,res=l.split(); us='team'+side.upper()
    p=P+f'ladder_replays/{mid}.json'
    if not os.path.exists(p): continue
    d=json.load(open(p,encoding='utf-8')); n+=1
    part=collections.defaultdict(set); pos=collections.defaultdict(list)  # (team,id)->[(round,x,y)]
    acts=[]
    for e in d['events']:
      o=e['owner']
      if o.get('kind')!='champion': continue
      for x in e['entries']:
        r=x['timestamp']['round']
        if 'x' in x: pos[(o['team'],o['id'])].append((r,x['x'],x['y']))
        if e['kind'] in('kill','assist') and x['target'].get('kind')=='champion':
          part[(o['team'],x['target']['id'],r)].add(o['id'])
        if e['kind'] in ('campClear','gemCollection'): acts.append((o['team'],o['id'],r,x.get('x'),x.get('y'),e['kind']))
    for (tm,tid,r),ps in part.items():
      if e is None: pass
      s='U' if tm==us else 'T'; KP[s][min(len(ps),3)]+=1
    for tm,i,r,x,y,k in acts:
      if x is None: continue
      s='U' if tm==us else 'T'; best=99
      for (t2,i2),pl in pos.items():
        if t2!=tm or i2==i: continue
        for (r2,x2,y2) in pl:
          if abs(r2-r)<=3: best=min(best,max(abs(x2-x),abs(y2-y)))
      NB[s][k,'<=4' if best<=4 else ('<=8' if best<=8 else 'far/unknown')]+=1
print('games',n)
for s in 'UT':
  t=sum(KP[s].values()); print(s,'kills made, participants 1/2/3+:',{k:f'{v/t:.0%}' for k,v in sorted(KP[s].items())},'kills/game',round(t/n,1))
for s in 'UT':
  for k in ('campClear','gemCollection'):
    t=sum(v for kk,v in NB[s].items() if kk[0]==k); print(s,k,'nearest ally (events +-3r):',{kk[1]:f'{v/t:.0%}' for kk,v in NB[s].items() if kk[0]==k},'n/game',round(t/n,1))
