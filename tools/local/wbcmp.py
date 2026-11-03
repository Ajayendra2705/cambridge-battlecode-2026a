"""Winning-bag screen: python -I tools/local/wbcmp.py BASE_DIR BASE NEW_DIR NEW

Pairs each game of NEW in NEW_DIR with BASE in BASE_DIR (same pool bot, map, side; both from `tools/local/wbsel.py`'s statistics
reader) and prints: wins, flips, losses that held 1000 in hand, rounds from the first winning bag to the game's end, deaths, bot
faults, and the games whose result changed. Only the games played by NEW count, since the others replay the same.
"""
import glob, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wbsel

base_dir, base, new_dir, new = sys.argv[1:5]
N = dict(games=0, base_win=0, new_win=0, up=0, down=0, base_loss_hand=0, new_loss_hand=0, base_loss_bag=0, new_loss_bag=0, changed=0)
gap_b, gap_n, deaths_b, deaths_n, faults, margin_b, margin_n = [], [], 0, 0, 0, 0, 0
rows = []


def deaths(path, us):
    d = json.load(open(path, encoding='utf-8'))
    return sum(float(c['metrics']['deaths']) for c in d['champions'] if c['team'] == us), int(d['diagnostics']['botFaults'].get(us, 0))


for p in sorted(glob.glob(os.path.join(new_dir, new + '~*.json'))):
    tail = os.path.basename(p).split('~', 1)[1]
    q = os.path.join(base_dir, base + '~' + tail)
    if not os.path.exists(q):
        continue
    us, wn, rn, on, tn, hn, bn = wbsel.hands(p)
    _, wb, rb, ob, tb, hb, bb = wbsel.hands(q)
    N['games'] += 1
    N['base_win'] += wb
    N['new_win'] += wn
    N['up'] += wn and not wb
    N['down'] += wb and not wn
    N['changed'] += (rn, on, tn) != (rb, ob, tb)
    N['base_loss_hand'] += (not wb) and hb is not None
    N['new_loss_hand'] += (not wn) and hn is not None
    N['base_loss_bag'] += (not wb) and bb is not None
    N['new_loss_bag'] += (not wn) and bn is not None
    margin_b += ob - tb
    margin_n += on - tn
    if bb is not None:
        gap_b.append(rb - bb)
    if bn is not None:
        gap_n.append(rn - bn)
    db, _ = deaths(q, us)
    dn, f = deaths(p, us)
    deaths_b += db
    deaths_n += dn
    faults += f
    if wn != wb or (not wn and hn is not None):
        rows.append((tail[:-5], 'base', 'W' if wb else 'L', rb, ob, tb, bb, 'new', 'W' if wn else 'L', rn, on, tn, bn))
print(N)
print(f"rounds from first winning bag to end: base {sum(gap_b)/max(1,len(gap_b)):.2f} (n {len(gap_b)}) new {sum(gap_n)/max(1,len(gap_n)):.2f} (n {len(gap_n)})")
print(f"deaths base {deaths_b:.0f} new {deaths_n:.0f}; margin base {margin_b} new {margin_n}; bot faults new {faults}")
for r in rows:
    print(' ', *r)
