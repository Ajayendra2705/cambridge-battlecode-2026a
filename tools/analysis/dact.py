# death activity per champion: match our D lines (round) to summary death events
import json,sys,collections,os,zipfile,re
P='C:/Users/ajiit/Desktop/Future/Projects/Cambridge Battlecode/'
A=collections.defaultdict(collections.Counter)
for D in sys.argv[1:]:
  for l in open(P+D+'/index.txt'):
    mid,mp,side,res=l.split(); us='team'+side.upper(); p=P+f'ladder_replays/{mid}.json'; r=P+f'{D}/{mid}.repl26a'
    if not (os.path.exists(p) and os.path.exists(r)): continue
    d=json.load(open(p,encoding='utf-8'))
    dr=collections.defaultdict(list)
    for e in d['events']:
      if e['kind']=='death' and e['owner']['team']==us:
        for x in e['entries']:
          if x['context']=='champion': dr[x['timestamp']['round']].append(e['owner']['name'])
    st=zipfile.ZipFile(r).read(f'team-{side}.stdout').decode('utf8','replace').replace('\0','')
    for m in re.finditer(r'^D(\d+) s\d r\d+ hp=\S+ (\S+)',st,re.M):
      rd=int(m.group(1)); names=dr.get(rd) or dr.get(rd-1) or dr.get(rd+1)
      if names and len(set(names))==1: A[names[0]][m.group(2)]+=1
for c,v in A.items(): t=sum(v.values()); print(c,t,{k:f'{n/t:.0%}' for k,n in v.most_common(6)})
