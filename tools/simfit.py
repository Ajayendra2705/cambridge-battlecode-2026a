"""Fit the fight simulator's free parameters to real fight outcomes.

usage: python tools/simfit.py DIR [DIR...]
Reads S lines (fight states logged at each decision by bots/k_sim) from our stdout, labels each with
  me_dies   : this champion dies within 10 rounds (D line of its slot)
  kill      : an enemy champion dies within 10 rounds within 8 tiles (match summary death events)
re-runs the simulator (a port of simulate_fight in bot.cpp) over a grid of enemy-damage scale, our-damage
scale and horizon, and reports how well each setting predicts both outcomes (balanced accuracy).
"""
import collections, glob, itertools, json, os, re, sys, zipfile


def simulate(units, rounds, them_first, sa, sb):
    u = [[dict(x, hp=x['hp'], slots=[dict(s) for s in x['slots']], stunned=False) for x in side] for side in units]
    for side, sc in ((u[0], sb), (u[1], sa)):
        for x in side:
            x['str'] *= sc
            for s in x['slots']: s['dmg'] *= sc
    start = [sum(x['hp'] for x in s) for s in u]
    for _ in range(rounds):
        for k in range(2):
            s = 1 - k if them_first else k
            o = 1 - s
            for x in u[s]:
                if x['hp'] <= 0: continue
                if x['stunned']: x['stunned'] = False; continue
                alive = [y for y in u[o] if y['hp'] > 0]
                if not alive: break
                t = min(alive, key=lambda y: y['hp'])
                moved = False
                spell_ready = any(sl['cd'] <= 0 and (sl['dmg'] > 0 or sl['stun']) for sl in x['slots'])
                want = max(x['range'], 4)
                if x['d'] > (want if spell_ready else x['range']): x['d'] -= 1; moved = True
                dmg = 0; melee = x['range'] <= 1; cast = None
                if not moved and x['d'] <= 4:
                    for sl in x['slots']:
                        if sl['cd'] <= 0 and sl['stun'] and not t['stunned']: cast = sl
                    if cast is None:
                        for sl in x['slots']:
                            if sl['cd'] <= 0 and sl['dmg'] > 0 and (cast is None or sl['dmg'] > cast['dmg']): cast = sl
                if cast is None and x['d'] <= x['range'] and (melee or not moved):
                    for sl in x['slots']:
                        if sl['cd'] <= 0 and sl['reset']: cast = sl
                if x['d'] <= x['range'] and (melee or not moved): dmg += x['str']
                if cast is not None:
                    if cast['reset']: dmg += x['str']
                    dmg += cast['dmg']
                    if cast['stun']: t['stunned'] = True
                    cast['cd'] = 9
                t['hp'] -= dmg
                if t['hp'] <= 0 and t['link'] >= 0: u[o][t['link']]['hp'] = 0
        for side in u:
            for x in side:
                for sl in x['slots']:
                    if sl['cd'] > 0: sl['cd'] -= 1
    dead = [sum(1 for x in s if x['hp'] <= 0) for s in u]
    frac = [sum(max(0, x['hp']) for x in u[i]) / max(start[i], 1) for i in range(2)]
    return dead, frac, u[0][0]['hp'] <= 0


samples = []
for d in sys.argv[1:]:
    for path in glob.glob(os.path.join(d, '*.repl26a')):
        base = os.path.basename(path)
        m = re.match(r'(.+?)~(.+?)~(.+?)~([AB])\.repl26a', base)
        if not m: continue
        us = 'team' + m[4]
        js = path[:-8] + '.json'
        if not os.path.exists(js): continue
        try:
            text = zipfile.ZipFile(path).read(f'team-{m[4].lower()}.stdout').decode('latin1')
        except Exception:
            continue
        summary = json.load(open(js, encoding='utf-8'))
        enemy_deaths = [(e['timestamp']['round'], e['x'], e['y']) for ev in summary['events'] if ev['kind'] == 'death'
                        and ev['owner'].get('team') != us for e in ev['entries']]
        my_deaths = collections.defaultdict(list)
        for dm in re.finditer(r'^D(\d+) s(\d)', text, re.M): my_deaths[int(dm[2])].append(int(dm[1]))
        for line in re.finditer(r'^S (.*)$', text, re.M):
            f = line[1].split()
            try:
                rnd, slot, x, y, cal = int(f[0]), int(f[1]), int(f[2]), int(f[3]), float(f[4])
                n0, n1 = int(f[5]), int(f[6])
                vals = f[7:]
                units = [[], []]; i = 0
                for side, n in ((0, n0), (1, n1)):
                    for _ in range(n):
                        hp, st, rg, dd, link = int(vals[i]), int(vals[i + 1]), int(vals[i + 2]), int(vals[i + 3]), int(vals[i + 4])
                        slots = []
                        for j in range(2):
                            dmg, cd, fl = int(vals[i + 5 + 3 * j]), int(vals[i + 6 + 3 * j]), vals[i + 7 + 3 * j]
                            slots.append(dict(dmg=dmg / (cal if side == 1 else 1), cd=cd, stun=fl[0] == '1', reset=fl[1] == '1'))
                        units[side].append(dict(hp=hp, str=st / (cal if side == 1 else 1), range=rg, d=dd, link=link, slots=slots))
                        i += 11
            except (ValueError, IndexError):
                continue
            me_dies = any(rnd < t <= rnd + 10 for t in my_deaths[slot])
            kill = any(rnd < r <= rnd + 10 and max(abs(ex - x), abs(ey - y)) <= 8 for r, ex, ey in enemy_deaths)
            samples.append((units, me_dies, kill))
print('fights', len(samples), 'me_dies', sum(s[1] for s in samples), 'kills', sum(s[2] for s in samples))
step = max(1, len(samples) // 6000)
samples = samples[::step]


def bacc(pred, truth):
    tp = sum(p and t for p, t in zip(pred, truth)); tn = sum((not p) and (not t) for p, t in zip(pred, truth))
    P = sum(truth); N = len(truth) - P
    return 0.5 * (tp / max(P, 1) + tn / max(N, 1))


res = []
for sa, sb, h in itertools.product((0.5, 0.75, 1.0, 1.5, 2.0, 3.0), (0.5, 0.75, 1.0, 1.5), (2, 3, 4, 5)):
    pd, pk = [], []
    for units, md, kl in samples:
        dead, frac, me = simulate(units, h, True, sa, sb)
        pd.append(me); pk.append(dead[1] > 0)
    a1 = bacc(pd, [s[1] for s in samples]); a2 = bacc(pk, [s[2] for s in samples])
    res.append((a1 + a2, a1, a2, sa, sb, h))
res.sort(reverse=True)
print('enemy_scale our_scale horizon  bacc(me_dies) bacc(kill)')
for r in res[:10]: print(f'  {r[3]:4} {r[4]:4} {r[5]}   {r[1]:.3f} {r[2]:.3f}')
cur = [r for r in res if r[3] == 1.0 and r[4] == 1.0 and r[5] == 3][0]
print(f'current (1,1,3): {cur[1]:.3f} {cur[2]:.3f}')
