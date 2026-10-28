"""Summarise the stale-state probe lines of a `multi.py --keep` run (helper agent h2).

usage: python -I tools/helper/h2_probe_sum.py RUNDIR [PREFIX]
  RUNDIR  a data/runs/multi-HHMMSS folder with kept replays
  PREFIX  the probe's file prefix (default exp.h2pr1l)

Reads our side's stdout (team-a in ~A files, team-b in ~B) and counts the probe's tagged lines:
  SW  dead-turn writes of shared bytes 0-4 from the last live turn's cache: teammates' claim slots reverted, help field
  GC/GE  ghost claims: a champion's own claim slot no longer holds what it wrote (start, then end with its length)
  FG  focus calls older than 3 rounds read as fresh (the 5-bit round wraps every 32): age, distance, engaged
  BC  respawn broadcasts decoded 256 rounds late (group held as respawning while it is up)
  EH  bank decisions that differ when the enemy's tributed total is read from an every-turn history
  RS/RE  recalls: started with an enemy seen within 6 in the last 3 rounds or not, and how they ended
  PS/PT/PU/PV  the probes' counters every 250 rounds; the last line of each champion in each game is summed (probe_lines.py
  keys lines by map and side only, which merges the three opponents' games, so read the files here)
  BW  ally waits at a big group carried into the group's next life (probe h2pr5l)
  HT  waits at one hole edge for the dash that ran past the intended 10 rounds (h2pr5l)
  MD  teammate deaths seen, with the rounds since this champion last ran (h2pr5l)
"""
import collections, glob, os, re, sys, zipfile

run = sys.argv[1]
prefix = sys.argv[2] if len(sys.argv) > 2 else 'exp.h2pr1l'
lines = collections.defaultdict(list)  # tag -> [(game, fields)]
games = 0
for path in sorted(glob.glob(os.path.join(run, prefix + '~*.repl26a'))):
    games += 1
    game = os.path.basename(path)[:-len('.repl26a')]
    side = game.split('~')[-1][0].lower()
    text = re.sub(r'[^\x20-\x7e\n]', '', zipfile.ZipFile(path).read(f'team-{side}.stdout').decode('latin1'))
    for line in text.splitlines():
        f = line.split()
        if f and f[0] in ('SW', 'GC', 'GE', 'FG', 'BC', 'EH', 'RS', 'RE', 'PS', 'PT', 'PU', 'SP', 'HZ', 'HP', 'HG', 'HX', 'PV',
                          'BW', 'HT', 'MD'):
            lines[f[0]].append((game, f[1:]))
print(f'{games} games of {prefix} in {run}')


def last_sums(tag, names):
    """Sum the last summary line (highest round) of each champion in each game, per named field (field 2 on)."""
    last = {}
    for g, f in lines[tag]:
        key = (g, f[1])
        if key not in last or int(f[0]) > int(last[key][0]): last[key] = f
    sums = collections.Counter()
    for f in last.values():
        for i, n in enumerate(names):
            if n: sums[n] += float(f[2 + i])
    return sums, len(last)


if lines['PS']:
    s, n = last_sums('PS', ('gc_n', 'gc_turns', 'help_missing', 'help_clears_other', 'bc_n', 'bc_turns', 'eh_eval', 'eh_holes', 'eh_changed', 'fg'))
    print(f'PS counters ({n} champion-games, to each one\'s last 250-round mark): ' + ', '.join(f'{k} {v:.0f}' for k, v in s.items()))
if lines['PT']:
    s, n = last_sums('PT', ('hz', 'hg_turns', 'hp', 's1', 'help_turns', 'help_overwritten', 'help_erased', 'erase_live', 'erase_dead', 'er', 'ss'))
    print(f'PT counters ({n} champion-games): ' + ', '.join(f'{k} {v:.0f}' for k, v in s.items()))
if lines['PU']:
    s, n = last_sums('PU', ('hv', 'emblem_starts_stale_str', 'emblem_starts_changed', 'dps_turns', 'dps_stale_turns', '', '', '', '', 'cal_gaps', 'cal_gap_pred', 'cal_pred'))
    print(f'PU counters ({n} champion-games): ' + ', '.join(f'{k} {v:.0f}' for k, v in s.items()))
if lines['PV']:
    pv = ('bw_events', 'bw_lost', 'bw_skip', 'ht_restart', 'ht_over', 'ht_long', 'md_det', 'md_late', 'md_gap', 'deaths')
    s, n = last_sums('PV', pv)
    print(f'PV counters ({n} champion-games): ' + ', '.join(f'{k} {v:.0f}' for k, v in s.items()))
    # Each of our deaths could be seen by every teammate: per game, deaths times (champions - 1), to the last 250 mark.
    last, per = {}, collections.defaultdict(lambda: [0, 0.0])
    for g, f in lines['PV']:
        if (g, f[1]) not in last or int(f[0]) > int(last[g, f[1]][0]): last[g, f[1]] = f
    for (g, _), f in last.items():
        per[g][0] += 1
        per[g][1] += float(f[2 + pv.index('deaths')])
    chances = sum(d * (c - 1) for c, d in per.values())
    print(f'MD teammate deaths seen {s["md_det"]:.0f} of {chances:.0f} chances ({s["md_det"] / max(1, chances):.0%}); seen late '
          f'{s["md_late"]:.0f}, mean delay {s["md_gap"] / max(1, s["md_late"]):.1f} rounds')
bw = lines['BW']  # round slot group carried present need would_wait old_life new_life
if bw:
    print(f'BW waits carried into a new group life {len(bw)} in {len({g for g, _ in bw})} games: would wait '
          f'{sum(1 for _, f in bw if f[6] == "1")}, of those with all 25 used (no wait at all) '
          f'{sum(1 for _, f in bw if f[6] == "1" and int(f[3]) >= 25)}, carried rounds {sum(int(f[3]) for _, f in bw)}')
ht = lines['HT']  # round slot start x y
if ht:
    print(f'HT hole-edge waits past 10 rounds {len(ht)} in {len({g for g, _ in ht})} games: ' +
          ', '.join(f'{g.split("~")[2]} r{f[2]}' for g, f in ht[:12]))
md = lines['MD']  # round observer dead_slot gap marked
if md:
    gaps = collections.Counter('1' if int(f[3]) <= 1 else '2-5' if int(f[3]) <= 5 else '6-20' if int(f[3]) <= 20 else '21+'
                               for _, f in md)
    print(f'MD deaths seen {len(md)}: rounds since the observer last ran ' + ', '.join(f'{k}: {gaps[k]}' for k in ('1', '2-5', '6-20', '21+'))
          + f'; with a fresh claim (a death mark) {sum(1 for _, f in md if f[4] == "1")}')
sp = lines['SP']  # round slot S.str strength choice fresh_choice
if sp:
    print(f'SP emblems started on a stale strength {len(sp)}: ' + ', '.join(f'{k} {v}' for k, v in collections.Counter(f'{f[4]}->{f[5]}' for _, f in sp).most_common()))

sw = lines['SW']  # round slot reverted_slots fresh_help cache_help my_help my_claim
rev = sum(1 for _, f in sw if int(f[2]) > 0)
erased = sum(1 for _, f in sw if int(f[3]) not in (0, int(f[5])) and int(f[5]) != 0)  # cleared another's live call
print(f'SW dead-turn writes {len(sw)}: reverted a teammate claim {rev} (slots {sum(int(f[2]) for _, f in sw)}), '
      f'erased another champion\'s help call {erased}')
ge = [int(f[2]) for _, f in lines['GE']]
print(f'GC ghost claims {len(lines["GC"])}, ended {len(ge)}, rounds {sum(ge)}, longest {max(ge) if ge else 0}, '
      f'on a reward (state 1) {sum(1 for _, f in lines["GC"] if f[4] == "1")}')
fg = lines['FG']  # round slot age dist prev_prey_dist engaged
print(f'FG ghost focus reads {len(fg)}: no prey before {sum(1 for _, f in fg if f[4] == "-1")}, engaged {sum(1 for _, f in fg if f[5] == "1")}, '
      f'ages {collections.Counter(int(f[2]) // 32 * 32 for _, f in fg).most_common(4)}')
bc = lines['BC']  # round slot group r_decoded r_true state gems gold dist
print(f'BC late broadcasts {len(bc)} in {len({g for g, _ in bc})} games: ' +
      ', '.join(sorted({f'{g.split("~")[2]} g{f[2]} r{f[0]}->{f[3]} (true {f[4]})' for g, f in bc})))
eh = lines['EH']  # round slot gems hist_s hist_t e_sub batch_s batch_t dl dl_t t_end_s t_end_t
print(f'EH bank decisions changed {len(eh)}: stale banks earlier {sum(1 for _, f in eh if int(f[6]) <= int(f[2]) < int(f[7]))}, '
      f'deadline only from the gap {sum(1 for _, f in eh if f[8] == "10")}')
starts = {(g, int(f[1]), int(f[0])): f for g, f in lines['RS']}  # round slot seen_age seen_at_age near hp gems
ends = {(g, int(f[1]), int(f[3])): f for g, f in lines['RE']}  # round slot outcome start hp
tab = collections.Counter()
for k, f in starts.items():
    e = ends.get(k)
    cls = 'enemy seen within 3' if int(f[2]) <= 3 else 'no enemy seen in 3'
    tab[cls, 'n'] += 1
    tab[cls, e[2] if e else 'open'] += 1
for cls in ('enemy seen within 3', 'no enemy seen in 3'):
    n = tab[cls, 'n']
    print(f'RS {cls}: recalls {n}, home {tab[cls, "0"]}, cut off {tab[cls, "1"]} ({tab[cls, "1"] / max(1, n):.0%}), died {tab[cls, "2"]}')
