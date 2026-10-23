# early3 (true spawn from buy events): early deaths (<=r300): where (fraction of the way from our spawn to theirs), activity, enemies, by outcome
import json,sys,collections,os,zipfile,re,statistics as st
P=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..') + '/'
D=sys.argv[1]; rows=[l.split() for l in open(P+D+'/index.txt')]
A=collections.defaultdict(collections.Counter); F=collections.defaultdict(list); n=collections.Counter()
for mid,mp,side,res in rows:
    p=P+f'data/summaries/{mid}.json'; f=P+f'{D}/{mid}.repl26a'
    if not (os.path.exists(p) and os.path.exists(f)): continue
    d=json.load(open(p,encoding='utf-8')); us='team'+side.upper()
    # spawn estimates: first position seen per team (earliest event with x,y in first 30 rounds) is unreliable; use first R line pos instead
    s=zipfile.ZipFile(f).read(f'team-{side}.stdout').decode('utf8','replace').replace(chr(0),'')
    # true spawn: modal position of our buyItem events (shopping happens on own spawn tiles; dead buys excluded by mode)
    bp=collections.Counter((x['x'],x['y']) for e in d['events'] if e['kind'] in ('buyItem','buyConsumable') and e['owner']['team']==us for x in e['entries'])
    if not bp: continue
    ours=bp.most_common(1)[0][0]
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
