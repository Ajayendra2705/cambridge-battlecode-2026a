"""Wait until no unranked match of our team was created in the last N seconds: python -I tools/platform/quiet.py [N]   (default 240)

A gate takes the shared live slot; a teammate's panel playing at that moment would play our upload and ours theirs. Prints the
time of the last match it saw. Run it right before a gate starts.
"""
import datetime as dt, json, os, subprocess, sys, time

C = os.path.expandvars(r'%LOCALAPPDATA%\Packages\PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0\LocalCache\local-packages\Python311\Scripts\cambc.exe')
N = int(sys.argv[1]) if len(sys.argv) > 1 else 240
while True:
    r = subprocess.run([C, 'matches', 'list', '--team', 'me', '--kind', 'unranked', '--limit', '1', '--json'], capture_output=True, text=True, encoding='utf-8')
    try:
        s = r.stdout
        last = json.loads(s[s.index('{'):])['matches'][0]['createdAt']
    except Exception:
        time.sleep(30); continue
    age = (dt.datetime.now(dt.timezone.utc) - dt.datetime.fromisoformat(last.replace('Z', '+00:00'))).total_seconds()
    if age >= N:
        print(f'quiet: last unranked match {int(age)} s ago ({last})')
        break
    time.sleep(max(20, min(60, N - age)))
