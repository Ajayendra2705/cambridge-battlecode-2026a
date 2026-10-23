import zipfile,sys,re,os,collections
P=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..') + '/'
D=P+sys.argv[1]; T=collections.defaultdict(collections.Counter); N=collections.Counter()
for mid,mp,side,res in [l.split() for l in open(D+'/index.txt')]:
    f=f'{D}/{mid}.repl26a'
    if not os.path.exists(f): continue
    s=zipfile.ZipFile(f).read(f'team-{side}.stdout').decode('utf8','replace').replace('\0','')
    typ={}; last={}
    for m in re.finditer(r'^R\d+ s(\d) (\w+)',s,re.M): typ[m.group(1)]=m.group(2)
    for m in re.finditer(r'^A s(\d) r(\d+) (.*)$',s,re.M): last[m.group(1)]=m.group(3)
    for sl,txt in last.items():
        c=typ.get(sl,'?'); N[c]+=1
        for k,v in re.findall(r'(\w+)=(\d+)',txt): T[c][k]+=int(v)
keys=['to_capture','capture','fight','approach','pvp','flee','kite','resp_wait','dead','bank','tribute','recall','heal_wait','home_heal','idle','other','retreat']
print('per game rounds'.ljust(14),' '.join(k[:8].rjust(8) for k in keys))
for c in T: print(c[:13].ljust(14),' '.join(f'{T[c][k]/N[c]:8.0f}' for k in keys))
