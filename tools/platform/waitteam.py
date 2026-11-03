"""Wait for a teammate's panel to end before queueing ours: python -I tools/platform/waitteam.py SINCE_ISO NGROUPS VERSION MINUTES

A match group plays the team's active version, so a test queued during a teammate's test plays the wrong bot. Polls once a minute and exits when one of these holds, printing which: NGROUPS or more unranked groups created
since SINCE_ISO on the teammate's clock have all finished and no new one started for three minutes (their panel is done); the selection moved away from VERSION; or MINUTES have passed. Other teams' scrims against us count, so
pass a number near the panel's size. Only reads from the platform.
"""
import collections, datetime, json, os, subprocess, sys, time

since, ngroups, version, minutes = sys.argv[1], int(sys.argv[2]), sys.argv[3], int(sys.argv[4])
C = os.path.expandvars(r'%LOCALAPPDATA%\Packages\PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0\LocalCache\local-packages\Python311\Scripts\cambc.exe')
OUR = '118dbffc-87ec-48a6-ac9c-dc1e371ba364'
end = time.time() + minutes * 60
last = None
while time.time() < end:
    try:
        s = subprocess.run([C, 'submissions', 'list'], capture_output=True, text=True, encoding='utf-8', timeout=60).stdout
        head = next(x for x in s.splitlines() if x.startswith('Live:'))
        parts = head.split()
        selected = parts[parts.index('Selected:') + 1]
        d = json.loads(subprocess.run([C, 'matches', 'list', '--team', OUR, '--kind', 'unranked', '--limit', '100', '--json'], capture_output=True, text=True, encoding='utf-8', timeout=60).stdout)
        G = collections.defaultdict(list)
        for m in d['matches']:
            if m['createdAt'] >= since:
                G[m['groupId']].append(m)
        fin = sum(all(m['status'] == 'finished' for m in g) for g in G.values())
        newest = max((m['createdAt'] for g in G.values() for m in g), default='')
        state = f'{head.strip()} groups {len(G)} finished {fin} newest {newest[11:19]}'
        if state != last:
            print(datetime.datetime.utcnow().strftime('%H:%M'), state, flush=True)
            last = state
        if selected != version:
            print('selection moved to', selected, flush=True)
            sys.exit(0)
        if len(G) >= ngroups and fin == len(G) and newest:
            age = (datetime.datetime.utcnow() - datetime.datetime.strptime(newest[:19], '%Y-%m-%dT%H:%M:%S')).total_seconds()
            if age > 180:
                print('panel done', flush=True)
                sys.exit(0)
    except Exception as e:
        print('read failed', str(e)[:80], flush=True)
    time.sleep(60)
print('timed out', flush=True)
