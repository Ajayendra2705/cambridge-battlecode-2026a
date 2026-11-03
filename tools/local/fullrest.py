"""The rest of a full paired run: python -I tools/local/fullrest.py BASE_DIR BASE NEW_BOT NEW_DIR

Prints a run-batch file for every game of BASE in BASE_DIR that NEW_BOT has not yet played in NEW_DIR. A screen limited to the games
near the end of the race leans towards losses, because only close wins are picked and close losses without 1000 in hand are not:
any change in fuel use re-rolls those games. The full set has no such lean.
"""
import glob, os, sys
base_dir, base, new, new_dir = sys.argv[1:5]
for p in sorted(glob.glob(os.path.join(base_dir, base + '~*.json'))):
    opp, mp, side = os.path.basename(p)[:-5].split('~')[1:]
    name = new + '~' + opp + '~' + mp + '~' + side
    if os.path.exists(os.path.join(new_dir, name + '.json')):
        continue
    a = '../../../bots/' + new.replace('.', '/', 1)
    b = '../../../bots/' + opp.replace('.', '/', 1)
    first, second = (a, b) if side == 'A' else (b, a)
    print('"' + first + '" "' + second + '" "../../../maps/' + mp + '.map26a" "' + name + '.repl26a" --statistics "' + name + '.json" --json')
