# python -I tools/replay/lgold.py MULTIDIR : per-champion gold/gems/damage for each candidate in a local multi run
import json,glob,collections,sys,os
S=collections.defaultdict(collections.Counter)
for f in glob.glob(os.path.join(sys.argv[1],'*.json')):
  b,o,m,s=os.path.basename(f)[:-5].split('~')
  try: d=json.load(open(f,encoding='utf-8'))
  except Exception: continue
  for c in d['champions']:
    if c['team']!='team'+s: continue
    k=S[b,c['name']]; mt=c['metrics']; k['n']+=1
    for x in ('earnedGold','collectedGems','submittedGems','championDamageDone','deaths'): k[x]+=float(mt.get(x,0))
for b in sorted({k[0] for k in S}):
  print(b)
  for c in ('Heart of Ruin','Vendetta','Vesper Vale','Ryth','Marcella'):
    k=S[b,c]; n=max(k['n'],1)
    print(f"  {c:13} gold {k['earnedGold']/n:5.0f} gems {k['collectedGems']/n:4.0f} trib {k['submittedGems']/n:4.0f} champdmg {k['championDamageDone']/n:5.0f} deaths {k['deaths']/n:.2f}")
