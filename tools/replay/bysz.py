# Run a decoded.py command or a replay reader on the games of one team size only: python -I tools/replay/bysz.py SIZE decoded|READER ARGS...
import sys, runpy
sys.path.insert(0, 'tools/replay')
import decoded as D
size = int(sys.argv[1]); tool = sys.argv[2]
orig = D.games
def games(dirs):
    for g in orig(dirs):
        if len(g[4][0]['c']) == 2 * size: yield g
D.games = games
sys.argv = [tool] + sys.argv[3:]
if tool == 'decoded': D.main()
else: runpy.run_path(f'tools/replay/{tool}.py', run_name='__main__')
