import json,sys,collections,os
P=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..') + '/'
B=collections.defaultdict(collections.Counter); N=collections.Counter(); n=0
for D in sys.argv[2:]:
  for l in open(P+D+'/index.txt'):
    mid,mp,side,res=l.split(); us='team'+side.upper(); p=P+f'data/summaries/{mid}.json'
    if not os.path.exists(p): continue
    d=json.load(open(p,encoding='utf-8')); n+=1
    for c in d['champions']: N['U' if c['team']==us else 'T',c['name']]+=1
    for e in d['events']:
      if e['kind'] not in ('buyItem','buyConsumable','itemCombination','sellItem','wardPlacement'): continue
      o=e['owner']
      if o.get('kind')!='champion': continue
      s='U' if o['team']==us else 'T'
      for x in e['entries']:
        nm=x.get('target',{}).get('name','?') if e['kind']!='wardPlacement' else 'ward'
        B[s,o['name']][e['kind'][:4]+':'+nm]+=1
for c in sys.argv[1].split(','):
  for s in 'UT':
    k=(s,c); m=max(N[k],1)
    print(s,c,N[k],[(i,round(v/m,1)) for i,v in B[k].most_common(12)])
