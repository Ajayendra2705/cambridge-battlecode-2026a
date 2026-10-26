"""00vault games: the centre group (49 touching gem clusters, 343 gems) by side.

usage: python -I tools/replay/vault.py DIR [DIR ...]

Per game: the rounds the vault lies dead and who stands on its tiles meanwhile (a unit on a spawn tile stops the
group's respawn, so "only us" rounds are rounds we keep it from coming back), the dead spans (start round, length;
a normal cycle is about 55: clearing, a 5-round capture, the 50-round respawn), and each capture (a round where
champions on the vault gain 40+ gems at once: the 343 split among the capturers, 428 with Prospector).
Then the totals per game. DIR is a decoded folder (tools/replay/decode_run.sh, tools/local/local_decode.sh).
"""
import collections, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import decoded as D

T = collections.Counter()
for us, res, mp, meta, rows in D.games(sys.argv[1:]):
    if 'vault' not in mp: continue
    gem = [int(k) for k, v in meta['camps'].items() if v == 2]  # the vault is the map's only gem-cluster group
    inside = lambda c: c['a'] and 'x' in c and 12 <= c['x'] <= 18 and 12 <= c['y'] <= 18
    C, spans, caps, since = collections.Counter(), [], [], None
    for k, r in enumerate(rows):
        if all(r['mh'][i] == 0 for i in gem):
            since = r['r'] if since is None else since
            C['dead'] += 1
            sides = {D.who(c['t'], us) for c in r['c'] if inside(c)}
            C['only us' if sides == {'us'} else 'only them' if sides == {'them'} else 'both' if sides else 'empty'] += 1
        elif since is not None:
            spans.append((since, r['r'] - since)); since = None
        if k:
            gain = collections.Counter()
            for i, c in enumerate(r['c']):
                p = rows[k - 1]['c'][i]
                if inside(c) and p['a'] and c.get('g', 0) - p.get('g', 0) >= 40: gain[D.who(c['t'], us)] += c['g'] - p['g']
            for w, v in gain.items():
                caps.append(f"r{r['r']} {w} {v}"); T[w + ' captures'] += 1
    if since is not None: spans.append((since, rows[-1]['r'] - since + 1))
    T['games'] += 1
    for key in ('dead', 'only us', 'only them', 'both', 'empty'): T[key] += C[key]
    print(f"{meta['file'][:36]} {res:4} end r{rows[-1]['r']}: dead {C['dead']}, only us {C['only us']}, only them "
          f"{C['only them']}, both {C['both']}, empty {C['empty']}; spans {spans}; captures {', '.join(caps) or 'none'}")
n = max(1, T['games'])
print(f"{T['games']} vault games, per game: dead {T['dead'] / n:.0f} rounds, only us {T['only us'] / n:.0f}, only them "
      f"{T['only them'] / n:.0f}, both {T['both'] / n:.0f}; captures us {T['us captures'] / n:.2f} them {T['them captures'] / n:.2f}")
