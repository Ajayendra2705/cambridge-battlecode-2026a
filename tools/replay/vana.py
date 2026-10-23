# python -I tools/replay/vana.py DIR : analyse V combat lines from lg1 platform replays
import zipfile,sys,re,os,collections,statistics as st
P=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..') + '/'
NM={0:'Ryth',1:'Vesper',2:'Vendetta',3:'Cassi',4:'Issac',5:'Stellar',6:'Prism',7:'Marcella',8:'Willow',9:'Ren',10:'Varg',11:'Tavi',12:'HoR'}
D=P+sys.argv[1]
rows=[l.split() for l in open(D+'/index.txt')]
stat=collections.defaultdict(list)   # (side,type,metric) -> values
cnt=collections.Counter()
def cheb(a,b): return max(abs(a[0]-b[0]),abs(a[1]-b[1]))
for mid,mp,side,res in rows:
    f=f'{D}/{mid}.repl26a'
    if not os.path.exists(f): continue
    s=zipfile.ZipFile(f).read(f'team-{side}.stdout').decode('utf8','replace').replace('\0','')
    prev={}  # slot -> (round, enemies list)
    for l in s.splitlines():
        if not l.startswith('V'): continue
        head,al,en=l.split('|')
        h=head.split(); r=int(h[0][1:]); slot=int(h[1]); typ=int(h[2]); me=tuple(map(int,h[3].split(',')))
        hp,mhp=map(int,h[4].split('/')); stv,fo=map(int,h[5].split('/')); act=h[7]; taken=int(h[8][1:])
        A=[(int(t),tuple(map(int,xy.split(','))),int(hpv)) for t,xy,hpv in re.findall(r'(\d+)@(\d+,\d+)/(\d+)',al)]
        E=[(int(m[0]),(int(m[1]),int(m[2])),int(m[3]),int(m[4]),int(m[5]),m[6]=='s') for m in re.findall(r'(\d+)@(\d+),(\d+)/(\d+)/(\d+)/(\d+)(s?)',en)]
        if not E: continue
        near=min(cheb(me,e[1]) for e in E)
        ne5=sum(cheb(me,e[1])<=5 for e in E); na5=1+sum(cheb(me,a[1])<=5 for a in A)
        stat['U',typ,'near'].append(near)
        stat['U',typ,'outnum'].append(ne5-na5)
        bucket=r//500
        stat['U',typ,f'str{bucket}'].append(stv); stat['U',typ,f'mhp{bucket}'].append(mhp)
        for e in E:
            stat['T',e[0],f'str{bucket}'].append(e[4]); stat['T',e[0],f'mhp{bucket}'].append(e[3])
        # damage we take when exactly one enemy is within 2 and it is type X (no camps assumption weak)
        adj=[e for e in E if cheb(me,e[1])<=1]
        if len(adj)==1 and all(cheb(me,e[1])>3 for e in E if e is not adj[0]) and r-prev.get(slot,(0,))[0]<=2:
            stat['T',adj[0][0],'dmg_to_us_1v1'].append(taken)
            # our damage to it: its hp now vs last observation of same type nearby
            pe=prev.get(slot,(0,[]))[1]
            pm=[x for x in pe if x[0]==adj[0][0] and cheb(x[1],adj[0][1])<=2]
            if pm: stat['U',typ,'dmg_to_them_1v1'].append(pm[0][2]-adj[0][2])
        stat['U',typ,'act:'+act].append(1)
        prev[slot]=(r,E)
    cnt['games']+=1
print('games',cnt['games'])
types=sorted({k[1] for k in stat})
for t in types:
    u={k[2]:v for k,v in stat.items() if k[0]=='U' and k[1]==t}; th={k[2]:v for k,v in stat.items() if k[0]=='T' and k[1]==t}
    if not u and not th: continue
    out=[NM.get(t,t)]
    for b in range(4):
        if f'str{b}' in u or f'str{b}' in th:
            out.append(f"r{b*500}: str us {st.median(u.get(f'str{b}',[0])):.0f} them {st.median(th.get(f'str{b}',[0])):.0f} hp us {st.median(u.get(f'mhp{b}',[0])):.0f} them {st.median(th.get(f'mhp{b}',[0])):.0f}")
    if 'dmg_to_us_1v1' in th: out.append(f"their dmg/turn 1v1 adjacent {st.mean(th['dmg_to_us_1v1']):.0f} (n {len(th['dmg_to_us_1v1'])})")
    if 'dmg_to_them_1v1' in u: out.append(f"our dmg/turn {st.mean(u['dmg_to_them_1v1']):.0f} (n {len(u['dmg_to_them_1v1'])})")
    if 'outnum' in u: out.append(f"lines {len(u['outnum'])} outnumbered share {sum(x>0 for x in u['outnum'])/len(u['outnum']):.0%}")
    acts=collections.Counter({k[4:]:len(v) for k,v in u.items() if k.startswith('act:')})
    if acts: out.append('acts '+str(acts.most_common(6)))
    print('\n  '.join(out))
