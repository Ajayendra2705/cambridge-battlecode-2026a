import json,sys,collections,os
P=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..') + '/'
for D in sys.argv[1:]:
  S=collections.defaultdict(collections.Counter); n=0
  for l in open(P+D+'/index.txt'):
    mid,mp,side,res=l.split(); us='team'+side.upper(); p=P+f'data/summaries/{mid}.json'
    if not os.path.exists(p): continue
    d=json.load(open(p,encoding='utf-8')); n+=1
    for c in d['champions']:
      s='U' if c['team']==us else 'T'; m=c['metrics']
      for k in ('championDamageDone','kills','deaths','championDamageTaken'): S[s,c['name']][k]+=float(m.get(k,0))
      S[s,c['name']]['n']+=1
  out=[]
  for c in ('Heart of Ruin','Marcella','Ryth','Vendetta','Vesper Vale'):
    u=S['U',c]; t=S['T',c]
    if u['n']: out.append(f"{c[:5]} {u['championDamageDone']/u['n']:.0f}({u['kills']/u['n']:.1f}/{u['deaths']/u['n']:.1f}) vs {t['championDamageDone']/max(t['n'],1):.0f}")
  print(D.split('/')[-1],n,' | '.join(out))
