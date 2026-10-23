import json,sys,collections,os,zipfile,re,statistics
P='C:/Users/ajiit/Desktop/Future/Projects/Cambridge Battlecode/'
H=collections.defaultdict(list); NE=collections.defaultdict(collections.Counter)
for D in sys.argv[1:]:
  for l in open(P+D+'/index.txt'):
    mid,mp,side,res=l.split(); us='team'+side.upper(); p=P+f'ladder_replays/{mid}.json'; r=P+f'{D}/{mid}.repl26a'
    if not (os.path.exists(p) and os.path.exists(r)): continue
    d=json.load(open(p,encoding='utf-8')); dr=collections.defaultdict(list)
    for e in d['events']:
      if e['kind']=='death' and e['owner']['team']==us:
        for x in e['entries']:
          if x['context']=='champion': dr[x['timestamp']['round']].append(e['owner']['name'])
    st=zipfile.ZipFile(r).read(f'team-{side}.stdout').decode('utf8','replace').replace('\0','')
    for m in re.finditer(r'^D(\d+) s\d r\d+ hp=\S+ \S+ en:(.*)$',st,re.M):
      rd=int(m.group(1)); names=dr.get(rd) or dr.get(rd-1) or dr.get(rd+1)
      if not names or len(set(names))!=1: continue
      en=[(t,int(dd),float(h)) for t,dd,h in re.findall(r'(\w+)@(\d+)/([\d.]+)',m.group(2))]
      near=[x for x in en if x[1]<=2]
      NE[names[0]][min(len([x for x in en if x[1]<=5]),4)]+=1
      if near: H[names[0]].append(min(x[2] for x in near))
for c in H: print(c,'n',len(H[c]),'median lowest-hp adjacent enemy',statistics.median(H[c]),'enemies<=5:',sorted(NE[c].items()))
