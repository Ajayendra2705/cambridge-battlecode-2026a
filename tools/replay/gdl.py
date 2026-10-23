# python -I tools/replay/gdl.py RUN  -> data/replays/platform/RUN/{mid}.repl26a + index.txt (mid map side result)
import os,re,subprocess,sys,json,time
from concurrent.futures import ThreadPoolExecutor
C=os.path.expandvars(r'%LOCALAPPDATA%\Packages\PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0\LocalCache\local-packages\Python311\Scripts\cambc.exe')
OUR='118dbffc-87ec-48a6-ac9c-dc1e371ba364'
run=sys.argv[1]; out=f'data/replays/platform/{run.replace("@","_")}'; os.makedirs(out,exist_ok=True)
ids=[l.split()[1:] for l in open('results/gate.log') if l.split()[:1]==[run]][-1]
rows=[]
for g in ids:
    for a in range(5):
        t=subprocess.run([C,'match-groups','show',g],capture_output=True,text=True,encoding='utf-8',errors='replace').stdout
        ms=re.findall(r'^(\S{36})\s+finished\s+(\S+)\s*\n\s+(\S{36})\s+.*?\n\s+(\S{36})',t,re.M)
        if ms: break
        time.sleep(5)
    for mid,mp,ta,tb in ms:
        side='a' if ta==OUR else 'b'
        p=f'data/summaries/{mid}.json'
        if not os.path.exists(p): subprocess.run([C,'matches','summary',mid,'--json','-o',p],capture_output=True)
        try: d=json.load(open(p,encoding='utf-8')); res='win' if d['match']['outcome']=='team'+side.upper() else 'loss'
        except Exception: res='?'
        rows.append((mid,mp,side,res))
open(out+'/index.txt','w').write('\n'.join(' '.join(r) for r in rows))
def get(r):
    p=f'{out}/{r[0]}.repl26a'
    for a in range(3):
        if os.path.exists(p): return
        subprocess.run([C,'matches','download',r[0],'-o',p],capture_output=True)
with ThreadPoolExecutor(2) as ex: list(ex.map(get,rows))
print(run,len(rows),sum(r[3]=='win' for r in rows),len(os.listdir(out))-1)
