"""Summarise unranked match groups: python -I tools/platform/group.py GROUP_ID [GROUP_ID ...]

Downloads each finished match's summary JSON into data/summaries/ and prints gems, rounds, kills and deaths.
"""
import json, os, re, subprocess, sys, time

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
CAMBC = os.path.expandvars(r'%LOCALAPPDATA%\Packages\PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0'
                           r'\LocalCache\local-packages\Python311\Scripts\cambc.exe')
OUR_TEAM = '118dbffc-87ec-48a6-ac9c-dc1e371ba364'


def run(*args):
    return subprocess.run([CAMBC, *args], cwd=ROOT, capture_output=True, text=True, encoding='utf-8', errors='replace').stdout


for gid in sys.argv[1:]:
    # The API sometimes answers empty (rate limit): retry before giving up on the group.
    for attempt in range(6):
        text = run('match-groups', 'show', gid)
        if re.search(r'^\S{36}\s', text, re.M):
            break
        time.sleep(10)
    matches = re.findall(r'^(\S{36})\s+(\S+)\s+(\S+)\s*\n\s+(\S{36})\s+(.*?)\s+(\[.*?\])\s*\n\s+(\S{36})\s+(.*?)\s+(\[.*?\])', text, re.M)
    total = [0, 0]
    for mid, status, mapname, ta, na, da, tb, nb, db in matches:
        side = 'teamA' if ta == OUR_TEAM else 'teamB'
        opp = nb if side == 'teamA' else na
        if status != 'finished':
            print(f'{mapname:12} {status} vs {opp}')
            continue
        path = os.path.join(ROOT, 'data', 'summaries', f'{mid}.json')
        # A rate-limited download leaves no file: retry, then report the match as pending instead of crashing (a crash
        # here stopped the gate and judge polls from ever counting the group's other finished matches).
        for attempt in range(3):
            if os.path.exists(path):
                break
            run('matches', 'summary', mid, '--json', '-o', path)
            if not os.path.exists(path):
                time.sleep(5)
        if not os.path.exists(path):
            print(f'{mapname:12} no summary yet vs {opp}')
            continue
        d = json.load(open(path, encoding='utf-8'))
        gems = {t['team']: int(t['submittedGems']) for t in d['teams']}
        other = 'teamB' if side == 'teamA' else 'teamA'
        deaths = {s: sum(int(c['metrics']['deaths']) for c in d['champions'] if c['team'] == s) for s in (side, other)}
        won = d['match']['outcome'] == side
        total[0 if won else 1] += 1
        print(f'{mapname:12} {"WIN " if won else "loss"} {gems[side]:5} - {gems[other]:5}  r{d["match"]["roundsCompleted"]:5}'
              f'  deaths us {deaths[side]:2} them {deaths[other]:2}  vs {opp}')
    print(f'group {gid[:8]}: {total[0]}-{total[1]}')
