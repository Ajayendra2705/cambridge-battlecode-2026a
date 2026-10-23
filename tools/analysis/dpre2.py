# Before each death: first combat line of the fatal engagement (V lines within 15 rounds before death, same slot)
import zipfile,sys,re,os,collections,statistics as st
P='C:/Users/ajiit/Desktop/Future/Projects/Cambridge Battlecode/'
D=P+sys.argv[1]; NM={0:'Ryth',1:'Vesper',2:'Vendetta',7:'Marcella',12:'HoR'}
A=collections.defaultdict(lambda: collections.defaultdict(list))
def cheb(a,b): return max(abs(a[0]-b[0]),abs(a[1]-b[1]))
for mid,mp,side,res in [l.split() for l in open(D+'/index.txt')]:
    f=f'{D}/{mid}.repl26a'
    if not os.path.exists(f): continue
    s=zipfile.ZipFile(f).read(f'team-{side}.stdout').decode('utf8','replace').replace('\0','')
    V=collections.defaultdict(list)
    for l in s.splitlines():
        if not l.startswith('V'): continue
        head,al,en=l.split('|'); h=head.split()
        r=int(h[0][1:]); slot=int(h[1]); typ=int(h[2]); me=tuple(map(int,h[3].split(','))); hp,mhp=map(int,h[4].split('/'))
        E=[(int(m[0]),(int(m[1]),int(m[2])),int(m[3]),int(m[4])) for m in re.findall(r'(\d+)@(\d+),(\d+)/(\d+)/(\d+)/\d+',en)]
        Al=[tuple(map(int,xy.split(','))) for t,xy,hpv in re.findall(r'(\d+)@(\d+,\d+)/(\d+)',al)]
        V[slot].append((r,typ,me,hp,mhp,h[7],E,Al))
    for m in re.finditer(r'^D(\d+) s(\d) r\d+ hp=\S+ (\S+)',s,re.M):
        dr=int(m.group(1)); slot=int(m.group(2))
        seq=[v for v in V[slot] if dr-25<=v[0]<dr]
        if not seq: continue
        # start of engagement: walk back while consecutive lines are <=2 rounds apart
        i=len(seq)-1
        while i>0 and seq[i][0]-seq[i-1][0]<=2: i-=1
        v=seq[i]; typ=v[1]; c=NM.get(typ,typ)
        ne=sum(cheb(v[2],e[1])<=5 for e in v[6]); na=1+sum(cheb(v[2],a)<=5 for a in v[7])
        A[c]['hp_frac_start'].append(v[3]/v[4]); A[c]['dur'].append(dr-v[0])
        A[c]['first_act'].append(v[5]); A[c]['enemies5'].append(ne); A[c]['allies5'].append(na)
        A[c]['enemy_hpfrac'].append(st.mean([e[2]/e[3] for e in v[6]]) if v[6] else 1)
        A[c]['nearest'].append(min(cheb(v[2],e[1]) for e in v[6]) if v[6] else 9)
        L=seq[-1]
        A[c]['end_en'].append(sum(cheb(L[2],e[1])<=5 for e in L[6])); A[c]['end_al'].append(1+sum(cheb(L[2],a)<=5 for a in L[7]))
        A[c]['end_act'].append(L[5]); A[c]['end_hp'].append(L[3]/L[4])
        mx=max(sum(cheb(x[2],e[1])<=5 for e in x[6]) for x in seq[i:]); A[c]['max_en'].append(mx)
        acts=[x[5] for x in seq[i:]]; A[c]['flee_first'].append(next((k for k,a in enumerate(acts) if a=='flee'),-1))
        A[c]['seq'].append(' '.join(acts[:8]))
for c,d in A.items():
    print(c,'end enemies5',round(st.mean(d['end_en']),1),'end allies5',round(st.mean(d['end_al']),1),'max enemies5',round(st.mean(d['max_en']),1),'last-seen hp',round(st.median(d['end_hp']),2),'end act',collections.Counter(d['end_act']).most_common(3))
    print('   first flee at line #',collections.Counter(d['flee_first']).most_common(6))
    print('   sample',d['seq'][:3])
for c,d in []:
    print(f"{c:8} n {len(d['dur']):3} dur {st.median(d['dur'])} startHP {st.median(d['hp_frac_start']):.2f} enemyHP {st.median(d['enemy_hpfrac']):.2f} nearest {st.median(d['nearest'])} enemies5 {st.mean(d['enemies5']):.1f} allies5 {st.mean(d['allies5']):.1f} first {collections.Counter(d['first_act']).most_common(4)}")
