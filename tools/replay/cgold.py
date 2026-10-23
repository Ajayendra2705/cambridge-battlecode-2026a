import json,sys,collections,os
P=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..') + '/'
S=collections.defaultdict(collections.Counter); n=0
for D in sys.argv[1:]:
  for l in open(P+D+'/index.txt'):
    mid,mp,side,res=l.split(); us='team'+side.upper(); p=P+f'data/summaries/{mid}.json'
    if not os.path.exists(p): continue
    d=json.load(open(p,encoding='utf-8')); n+=1
    for c in d['champions']:
      s='U' if c['team']==us else 'T'; m=c['metrics']
      for k in ('earnedGold','spentGold','collectedGems','monsterDamageDone','championDamageDone','deaths'): S[s,c['name']][k]+=float(m.get(k,0))
      S[s,c['name']]['n']+=1
    # gold earned by r500 per champion from championTimelines
    for t in d['championTimelines']:
      if t['metric']!='earnedGold': continue
      o=t['owner']; s='U' if o['team']==us else 'T'; r=0; v500=0
      for run in t['runs']:
        if r<=500: v500=float(run['value'])
        r+=run['duration']
      S[s,o['name']]['g500']+=v500
print('games',n)
for c in ('Heart of Ruin','Vendetta','Vesper Vale','Ryth','Marcella'):
  u=S['U',c]; t=S['T',c]
  f=lambda x,k: x[k]/max(x['n'],1)
  print(f"{c:13} gold us {f(u,'earnedGold'):5.0f} them {f(t,'earnedGold'):5.0f} | gold@r500 us {f(u,'g500'):5.0f} them {f(t,'g500'):5.0f} | spent us {f(u,'spentGold'):5.0f} them {f(t,'spentGold'):5.0f} | gems us {f(u,'collectedGems'):4.0f} them {f(t,'collectedGems'):4.0f} | deaths {f(u,'deaths'):.1f}/{f(t,'deaths'):.1f}")
