"""Which local games can a winning-bag change touch? python -I tools/local/wbsel.py RUN_DIR BASE NEW_BOT OUT_MATCHES [MIN_RIVAL]

Local games replay exactly, and a change that acts only once our tributed gems plus bags reach 1000 leaves every game the same
up to that round. From the base's statistics (teamTimelines submittedGems, championTimelines gems) this finds, per game of BASE
in RUN_DIR, the first round our hand (tributed plus all bags) reached 1000 and the first round one bag alone did. It writes a
run-batch file for NEW_BOT with the games worth replaying: every loss that held 1000 in hand, and every win that held it where
the rivals ended at MIN_RIVAL (default 700) or more, since a win further ahead cannot flip. It prints the counts.
"""
import glob, json, os, sys


def series(runs, n):
    out = []
    for r in runs:
        out += [float(r['value'])] * int(r['duration'])
    last = out[-1] if out else 0.0
    return (out + [last] * n)[:n]


def hands(path):
    """(us, won, rounds, ours, theirs, first round hand reaches 1000, first round one bag does, biggest hand gap at the end)."""
    d = json.load(open(path, encoding='utf-8'))
    us = 'team' + path.rsplit('~', 1)[1][0]
    n = int(d['match']['roundsCompleted']) + 2
    sub = {}
    for t in d['teamTimelines']:
        if t['metric'] == 'submittedGems':
            sub[t['owner']] = series(t['runs'], n)
    bags = [series(t['runs'], n) for t in d['championTimelines'] if t['metric'] == 'gems' and t['owner'].get('team') == us]
    first_hand = first_bag = None
    su = sub.get(us, [0.0] * n)
    for r in range(n):
        vals = [b[r] for b in bags]
        if first_hand is None and su[r] + sum(vals) >= 1000:
            first_hand = r
        if first_bag is None and vals and su[r] + max(vals) >= 1000 and max(vals) > 0:
            first_bag = r
    final = {t['team']: int(t['submittedGems']) for t in d['teams']}
    rival = [k for k in final if k != us][0]
    return us, d['match']['outcome'] == us, int(d['match']['roundsCompleted']), final[us], final[rival], first_hand, first_bag


if __name__ == '__main__':
    run, base, new, out = sys.argv[1:5]
    min_rival = int(sys.argv[5]) if len(sys.argv) > 5 else 700
    pick, stats = [], dict(games=0, wins=0, loss_hand=0, loss_bag=0, win_close=0)
    for p in sorted(glob.glob(os.path.join(run, base + '~*.json'))):
        us, won, rounds, ours, theirs, fh, fb = hands(p)
        stats['games'] += 1
        stats['wins'] += won
        if fh is None:
            continue
        lost = not won
        if lost:
            stats['loss_hand'] += 1
            stats['loss_bag'] += fb is not None
        if won and theirs >= min_rival:
            stats['win_close'] += 1
        if lost or theirs >= min_rival:
            name = os.path.basename(p)[:-5]
            opp, mp, side = name.split('~')[1:]
            a = '../../../bots/' + new.replace('.', '/', 1)
            b = '../../../bots/' + opp.replace('.', '/', 1)
            new_name = f'{new}~{opp}~{mp}~{side}'
            first, second = (a, b) if side == 'A' else (b, a)
            pick.append(f'"{first}" "{second}" "../../../maps/{mp}.map26a" "{new_name}.repl26a" --statistics "{new_name}.json" --json')
    os.makedirs(os.path.dirname(out) or '.', exist_ok=True)
    open(out, 'w').write('\n'.join(pick) + '\n')
    print(stats, 'picked', len(pick))
