# early deaths (<=r300): where (fraction of the way from our spawn to theirs), activity, enemies, by outcome
import json,sys,collections,os,zipfile,re,statistics as st
P='C:/Users/ajiit/Desktop/Future/Projects/Cambridge Battlecode/'
D=sys.argv[1]; rows=[l.split() for l in open(P+D+'/index.txt')]
A=collections.defaultdict(collections.Counter); F=collections.defaultdict(list); n=collections.Counter()
for mid,mp,side,res in rows:
    p=P+f'ladder_replays/{mid}.json'; f=P+f'{D}/{mid}.repl26a'
    if not (os.path.exists(p) and os.path.exists(f)): continue
    d=json.load(open(p,encoding='utf-8')); us='team'+side.upper()
    # spawn estimates: first position seen per team (earliest event with x,y in first 30 rounds) is unreliable; use first R line pos instead
    s=zipfile.ZipFile(f).read(f'team-{side}.stdout').decode('utf8','replace').replace('\0','')
    sp=[tuple(map(int,m)) for m in re.findall(r'^R20 s\d \w+ .*pos=\((\d+), (\d+)\)',s,re.M)]
    if not sp: continue
    ours=(st.mean(x[0] for x in sp),st.mean(x[1] for x in sp))
    # enemy spawn = point reflection (maps symmetric): unknown symmetry; use enemy champion positions at R lines? skip; use map centre mirror
    cat='win' if res=='win' else 'loss'
    n[cat]+=1
    for m in re.finditer(r'^D(\d+) s(\d) r\d+ hp=\S+ (\S+) en:(.*)$',s,re.M):
        r=int(m.group(1))
        if r>300: continue
        A[cat][m.group(3)]+=1
        en=re.findall(r'(\w+)@(\d+)/',m.group(4)); F[cat].append(sum(int(e[1])<=5 for e in en))
    # positions of our early deaths from summary
    for e in d['events']:
        if e['kind']!='death' or e['owner']['team']!=us: continue
        for x in e['entries']:
            if x['context']=='champion' and x['timestamp']['round']<=300:
                A[cat+'_dist'][min(9,int(max(abs(x['x']-ours[0]),abs(x['y']-ours[1]))//5))]+=1
for c in ('win','loss'):
    print(c,'games',n[c],'early deaths/game',round(sum(A[c].values())/max(n[c],1),2),'acts',A[c].most_common(5),'enemies<=5 mean',round(st.mean(F[c]),2) if F[c] else '-')
    print('   distance from our spawn (x5 tiles)',sorted(A[c+'_dist'].items()))
