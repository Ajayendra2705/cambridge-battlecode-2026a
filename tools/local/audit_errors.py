"""Total the caught engine errors per call site in a local run of an audit build.

usage: python -I tools/local/audit_errors.py RUNDIR

The audit build (see bots/exp/au1 in docs/experiments.md) prints "X r<round> <file>:<line> n=<count> <message>" lines
every 500 rounds, per champion. This script takes each champion's last line per site in every replay of RUNDIR
(the candidate is team a in "~A" bundles and team b in "~B" bundles) and sums the counts over champions and games.
Builds from au14 on print each caught engine error once, when it happens, as
"E r<round> <file>:<line> split=<0|1> ward=<0|1> stage=<stage> act=<activity> what=<message>"; those lines are counted
one each, keyed by site plus "split" (the turn had run out of fuel and resumed since its snapshot) and "ward" (the turn
placed a ward), with the stage in the message column.
"""
import collections, glob, os, re, struct, sys, zipfile

run = sys.argv[1]
line_re = re.compile(r'^X r(\d+) (.+?):(\d+) n=(\d+) (.*)$')
event_re = re.compile(r'^E r(\d+) (.+?):(\d+) split=(\d) ward=(\d) stage=(.*?) act=(.*?) what=(.*)$')
total = collections.Counter()
what = {}
games = 0
for path in sorted(glob.glob(os.path.join(run, '*.repl26a'))):
    team = 'a' if path.endswith('~A.repl26a') else 'b'
    text = zipfile.ZipFile(path).read(f'team-{team}.stdout').decode('latin1')
    text = re.sub(r'[^\x20-\x7e\n]', '', text)
    games += 1
    # Lines carry no slot. Every champion prints every site it has hit at the same rounds, and its counts only grow,
    # so the lines of the last printing round hold each champion's total: sum them.
    last = {}
    for ln in text.splitlines():
        e = event_re.match(ln.strip())
        if e:
            f = os.path.basename(e[2].replace("\\", "/")) + (' split' if e[4] == '1' else '') + (' ward' if e[5] == '1' else '')
            key = (f, int(e[3]))
            total[key] += 1
            what[key] = f'{e[8]} @{e[6]}'
            continue
        m = line_re.match(ln.strip())
        if not m:
            continue
        rnd, f, l, n, msg = int(m[1]), os.path.basename(m[2].replace("\\", "/")), int(m[3]), int(m[4]), m[5]
        key = (f, l)
        last.setdefault(key, {})
        # Counts of one champion rise over time; several champions print the same site in the same round.
        last[key].setdefault(rnd, []).append(n)
        what[key] = msg
    for key, by_round in last.items():
        final = max(by_round)
        total[key] += sum(by_round[final])
    errors = sum(1 for ln in text.splitlines() if 'bot error' in ln)
    if errors:
        total[('bot error', 0)] += errors
    # Fuel log: 13 header bytes, then one little-endian uint64 per entry. The first 8 entries are the budgets (draft,
    # turn, first turn, ...); then fuel used per champion turn. A turn that used its whole 100k budget ran out of fuel
    # and resumes next turn from the same point. The first 5 rounds (init_world spreads over them) are skipped.
    raw = zipfile.ZipFile(path).read(f'team-{team}.fuel')
    n = (len(raw) - 13) // 8
    used = struct.unpack(f'<{n}Q', raw[13:13 + 8 * n])
    total[('fuel exhausted turns', 0)] += sum(1 for v in used[8 + 25:] if v >= 100000)
    total[('turns', 0)] += max(0, n - 8)
print(f'{games} games')
for key, n in total.most_common():
    print(f'{n:7d}  {key[0]}:{key[1]}  {what.get(key, "")[:100]}')
