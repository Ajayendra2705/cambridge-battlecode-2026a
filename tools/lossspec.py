"""Build a lost-matches spec from a gate run: python -I tools/lossspec.py RUN > tools/loss_spec.txt
Each line "OPP_ID:map1,..,map5:side1,..,side5" replays every game RUN lost (same opponent, map, our side), padded to 5 with maps we won against that opponent."""
import json, os, re, subprocess, sys, collections, time
CAMBC = os.path.expandvars(r'%LOCALAPPDATA%\Packages\PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0\LocalCache\local-packages\Python311\Scripts\cambc.exe')
OUR = '118dbffc-87ec-48a6-ac9c-dc1e371ba364'
run = sys.argv[1]
ids = [l.split()[1:] for l in open('tools/gate.log') if l.split()[:1] == [run]][-1]
lost = collections.defaultdict(list); won = collections.defaultdict(list)
for g in ids:
    for attempt in range(8):
        t = subprocess.run([CAMBC, 'match-groups', 'show', g], capture_output=True, text=True, encoding='utf-8', errors='replace').stdout
        if re.search(r'finished', t): break
        time.sleep(4)
    for mid, mp, ta, tb in re.findall(r'^(\S{36})\s+finished\s+(\S+)\s*\n\s+(\S{36})\s+.*?\n\s+(\S{36})', t, re.M):
        side = 'a' if ta == OUR else 'b'
        opp = tb if side == 'a' else ta
        d = json.load(open(f'ladder_replays/{mid}.json', encoding='utf-8'))
        (lost if d['match']['outcome'] != 'team' + side.upper() else won)[opp].append((mp, side))
for opp, games in lost.items():
    while games:
        chunk = games[:5]; games = games[5:]
        # Pad with maps we won against the same opponent (identical replays add nothing; wins check for regressions).
        pad = (chunk + [x for x in won[opp] if x not in chunk] + chunk * 5)[:5]
        print(f"{opp}:{','.join(m for m, s in pad)}:{','.join(s for m, s in pad)}")
