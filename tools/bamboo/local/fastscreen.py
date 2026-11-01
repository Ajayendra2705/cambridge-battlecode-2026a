"""fastscreen.py BASE "edits" [BASE "edits"]... : tools/evaluatec.sh without the shell.

Same candidates (BASE's src + kSeed + `s/old/new/@@...` edits, one copy C<i>s<seed> per seed), same game cache
(results/cache, shared with tools/sweepc.sh), same summary (tools/evalsum.py), but every game not in the cache is played
by one `cambc run-batch` process instead of a `cambc run` per game driven from Git Bash. Under Git Bash each process
launch costs ~0.1 s and the shell screen spent ~10 of them per game plus a polling loop: 0.9 games/s on this PC, against
~4.5 games/s for run-batch with the compiled-module cache (Oct 21 measurement, tools/SCREENING.md).

Environment (defaults in brackets):
  MAPS      maps to play, names as in maps/ without .map26a [every pool map, sprint_1_* excluded]
  OPP       opponents ["B7Live B7Base"]          SEEDS ["1"]        JOBS [11]        BUILD_JOBS [5]
  ROUNDS    stop every game after this many rounds: a fast reject filter. Candidates print both teams' banked gems
            just before the cut-off (kReportRound, tools/edits/edit_report.py) and the margin is that difference; it
            finds losses as reliably as full games but misses late-game gains (SCREENING.md) [play to the end]
  CAMBC     the cambc exe [%LOCALAPPDATA%/cambc/bin/cambc-4.0.0.exe (engine 2.0.0, Oct 26)]
  KEEP=1    keep the candidate copies under bots/
  MATCH_TIMEOUT  wall-clock seconds per match passed to run-batch --timeout (a hung game otherwise blocks the screen)
"""
import concurrent.futures, hashlib, json, os, re, shutil, subprocess, sys, tempfile, time

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))  # tools/bamboo/local -> the repository root
os.chdir(ROOT)
CAMBC = os.environ.get("CAMBC") or os.path.join(os.environ["LOCALAPPDATA"], "cambc", "bin", "cambc-4.0.0.exe")
CACHE = os.environ.get("SWEEP_CACHE", os.path.join(ROOT, "results", "cache"))
os.makedirs(CACHE, exist_ok=True)
os.makedirs(os.path.join(ROOT, "results", "ev"), exist_ok=True)
OPPS = os.environ.get("OPP", "B7Live B7Base").split()
SEEDS = os.environ.get("SEEDS", "1").split()
JOBS = int(os.environ.get("JOBS", "11"))
BUILD_JOBS = int(os.environ.get("BUILD_JOBS", "5"))
ROUNDS = int(os.environ.get("ROUNDS", "0") or 0)
env = dict(os.environ, CAMBC_WASMTIME_CACHE=os.environ.get("CAMBC_WASMTIME_CACHE", os.path.join(ROOT, ".cambc", "wasmtime-cache")))
UUID = re.compile(r"-[0-9a-f]{8}(-[0-9a-f]{4}){3}-[0-9a-f]{12}$")


def log(*a):
    print(*a, flush=True)


def map_list():
    files = sorted(f for f in os.listdir("maps") if f.endswith(".map26a"))
    want = os.environ.get("MAPS", "").split()
    out, seen = [], set()
    for f in files:
        m = UUID.sub("", f[:-7])
        if m in seen or (want and m not in want) or (not want and m.startswith("sprint_1")):
            continue
        seen.add(m)
        out.append((m, os.path.join("maps", f)))
    return out


def sha(path, n, algo):
    h = hashlib.new(algo)
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()[:n]


def build(name):
    r = subprocess.run([CAMBC, "build", name], capture_output=True, env=env)
    with open(os.path.join("bots", name, "build.log"), "wb") as f:
        f.write(r.stdout + r.stderr)
    return name, r.returncode == 0 and os.path.isfile(os.path.join("bots", name, ".cambc", "build", "bot-injected.wasm"))


def stale(name):
    """No wasm, or any source file newer than it (review 2026-10-22: a stale opponent binary wore its directory's name)."""
    w = os.path.join("bots", name, ".cambc", "build", "bot-injected.wasm")
    if not os.path.isfile(w):
        return True
    wt = os.path.getmtime(w)
    src = os.path.join("bots", name, "src")
    return any(os.path.getmtime(os.path.join(dp, f)) > wt for dp, _, fs in os.walk(src) for f in fs)


def at_end(runs):
    return float(runs[-1]["value"]) if runs else 0.0


def synth(stats, a, b, mapfile):
    """A log in the shape tools/evalsum.py parses, from a run-batch statistics JSON (None when unusable)."""
    d = stats
    per = {"teamA": {"kills": 0, "deaths": 0, "gold": 0.0, "carried": 0.0}, "teamB": {"kills": 0, "deaths": 0, "gold": 0.0, "carried": 0.0}}
    for tl in d.get("championTimelines", []):
        t = tl["owner"]["team"]
        if t not in per:
            continue
        v = at_end(tl["runs"])
        if tl["metric"] == "kills": per[t]["kills"] += int(v)
        elif tl["metric"] == "deaths": per[t]["deaths"] += int(v)
        elif tl["metric"] == "earnedGold": per[t]["gold"] += v
        elif tl["metric"] == "gems": per[t]["carried"] += v
    banked = {t["team"]: int(t["submittedGems"]) for t in d.get("teams", [])}
    faults = d.get("diagnostics", {}).get("botFaults", {})
    rounds = d.get("match", {}).get("roundsStarted", d.get("match", {}).get("roundsCompleted", 0))
    outcome = d.get("match", {}).get("outcome")
    gems = dict(banked)
    if ROUNDS:
        # cut-off: banked + carried decides, ties to the team with more gold earned
        gems = {t: banked.get(t, 0) + int(per[t]["carried"]) for t in ("teamA", "teamB")}
        outcome = "teamA" if (gems["teamA"], per["teamA"]["gold"]) >= (gems["teamB"], per["teamB"]["gold"]) else "teamB"
        reason = f"cutoff at round {rounds} (banked + carried gems)"
    elif outcome not in ("teamA", "teamB"):
        return None
    else:
        reason = f"reached 1000 gems in round {rounds}" if max(banked.values() or [0]) >= 1000 else f"round limit reached in round {rounds}"
    letter = "A" if outcome == "teamA" else "B"
    win = a if letter == "A" else b
    rows = []
    for t, bot, L in (("teamA", a, "A"), ("teamB", b, "B")):
        rows.append(f"  {L}    {bot}  {gems.get(t, 0)}     {per[t]['kills']}     {per[t]['deaths']}        {int(per[t]['gold'])}        {faults.get(t, 0)}  -")
    return "\n".join([
        f"{a} vs {b} on maps/{os.path.basename(mapfile)}",
        f"Team {letter} ({win}) wins: {reason}",
        "  team bot     gems kills deaths gold earned  crashes  draft",
        *rows, ""])


def synth_cut(a, b, mapfile, cand_a, ours, theirs, r):
    """A cut-off result: the candidate's and the opponent's banked gems at the REPORT round."""
    ga, gb = (ours, theirs) if cand_a else (theirs, ours)
    letter = "A" if ga >= gb else "B"
    win = a if letter == "A" else b
    return "\n".join([
        f"{a} vs {b} on maps/{os.path.basename(mapfile)}",
        f"Team {letter} ({win}) wins: cutoff at round {r} (banked gems)",
        "  team bot     gems kills deaths gold earned  crashes  draft",
        f"  A    {a}  {ga}     0     0        0        0  -",
        f"  B    {b}  {gb}     0     0        0        0  -", ""])


def report_of(replay, side):
    """(round, our banked, their banked) from the first REPORT line of side's stdout in a replay bundle, or None."""
    import zipfile
    try:
        with zipfile.ZipFile(replay) as z:
            t = z.read(f"team-{side}.stdout").decode("utf-8", "replace")
    except (OSError, KeyError, zipfile.BadZipFile):
        return None
    m = re.search(r"REPORT (\d+) (\d+) (\d+) (\d+)", t.replace(chr(0), ""))  # the bundle pads lines with NULs
    return (int(m.group(1)), int(m.group(2)), int(m.group(3))) if m else None


def src_hashes(name):
    """sha256 (16 hex) of every file under bots/<name>/src, by relative path."""
    out = {}
    root = os.path.join("bots", name, "src")
    for dp, _, fs in os.walk(root):
        for f in sorted(fs):
            p = os.path.join(dp, f)
            out[os.path.relpath(p, root).replace("\\", "/")] = sha(p, 16, "sha256")
    return dict(sorted(out.items()))


def write_manifest(run, args, names, ver, wasm, maps, mh):
    """Screening audit 2026-10-22: persist what was run - git state, cambc, settings, each candidate's base, edits, seed,
    source and wasm hashes plus a zip of its edited source, the opponents' hashes and the maps - in <run>/manifest.json."""
    import zipfile
    os.makedirs(run, exist_ok=True)
    git = lambda *a: subprocess.run(["git", *a], capture_output=True, text=True).stdout.strip()
    cands = []
    for i in range(len(args) // 2):
        for sd in SEEDS:
            n = f"C{i + 1}s{sd}"
            if n not in names:
                continue
            cands.append({"name": n, "base": args[2 * i], "edits": args[2 * i + 1], "seed": sd, "src": src_hashes(n), "wasm": wasm.get(n)})
            if sd == SEEDS[0]:
                zp = os.path.join(run, f"C{i + 1}-src.zip")
                with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
                    root = os.path.join("bots", n, "src")
                    for dp, _, fs in os.walk(root):
                        for f in fs:
                            z.write(os.path.join(dp, f), os.path.relpath(os.path.join(dp, f), root))
    man = {
        "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "argv": sys.argv, "cwd": ROOT,
        "git_head": git("rev-parse", "HEAD"), "git_dirty_files": len([l for l in git("status", "--porcelain").splitlines() if l and not l.startswith("??")]),
        "cambc": CAMBC, "cambc_version": ver,
        "env": {k: os.environ.get(k) for k in ("SEEDS", "MAPS", "OPP", "ROUNDS", "JOBS", "BUILD_JOBS")},
        "candidates": cands,
        "opponents": [{"name": o, "src": src_hashes(o), "wasm": wasm.get(o)} for o in OPPS],
        "maps": [{"name": m, "file": f, "sha256": mh[m]} for m, f in maps],
    }
    with open(os.path.join(run, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(man, f, indent=1)
    log(f"manifest {os.path.join(run, 'manifest.json')}")


def main():
    args = sys.argv[1:]
    if not args or len(args) % 2:
        sys.exit(__doc__)
    lock = os.path.join("results", "ev", ".screen.lock")
    os.makedirs(os.path.dirname(lock), exist_ok=True)
    try:
        os.mkdir(lock)
    except FileExistsError:
        sys.exit(f"another screen is running or left {lock} behind: aborting")
    names = []
    try:
        t0 = time.time()
        # candidates
        for i in range(len(args) // 2):
            base, edits = args[2 * i], args[2 * i + 1]
            for sd in SEEDS:
                n = f"C{i + 1}s{sd}"
                shutil.rmtree(os.path.join("bots", n), ignore_errors=True)
                shutil.copytree(os.path.join("bots", base, "src"), os.path.join("bots", n, "src"))
                p = os.path.join("bots", n, "src", "bot.cpp")
                s = open(p, encoding="utf-8").read()
                s = s.replace("constexpr int kSeed = 0; ", f"constexpr int kSeed = {sd}; ", 1)
                if ROUNDS:
                    if "constexpr int kReportRound = 0;" not in s:
                        sys.exit(f"{base} has no kReportRound (tools/edits/edit_report.py): ROUNDS mode needs it")
                    s = s.replace("constexpr int kReportRound = 0;", f"constexpr int kReportRound = {max(1, ROUNDS - 5)};", 1)
                open(p, "w", encoding="utf-8").write(s)
                r = subprocess.run([sys.executable, "tools/bamboo/local/apply_edits.py", p, edits])
                if r.returncode:
                    sys.exit(f"EDIT FAILED {n}: aborting")
                names.append(n)
            log(f"C{i + 1} = {base} + [{edits}]")
        need = names + [o for o in OPPS if stale(o)]
        with concurrent.futures.ThreadPoolExecutor(BUILD_JOBS) as ex:
            for n, ok in ex.map(build, need):
                if not ok:
                    sys.exit(f"BUILD FAILED {n}")
        log(f"built {len(need)} in {time.time() - t0:.0f} s")
        wasm = {b: sha(os.path.join("bots", b, ".cambc", "build", "bot-injected.wasm"), 16, "sha1") for b in names + OPPS}
        ver = subprocess.run([CAMBC, "--version"], capture_output=True, text=True).stdout.splitlines()[0]
        engine = re.sub(r"[^A-Za-z0-9.]", "_", ver)
        maps = map_list()
        mh = {m: sha(f, 12, "sha256") for m, f in maps}
        run = os.path.join("results", "ev", f"run{int(time.time())}")
        write_manifest(run, args, names, ver, wasm, maps, mh)
        todo, hits = [], 0
        for n in names:
            for o in OPPS:
                d = os.path.join(run, f"{n}-{o}")
                os.makedirs(d, exist_ok=True)
                for m, f in maps:
                    for a, b in ((n, o), (o, n)):
                        key = os.path.join(CACHE, f"{engine}-{wasm[a]}-{wasm[b]}-{m}-{mh[m]}" + (f"-r{ROUNDS}" if ROUNDS else ""))
                        out = os.path.join(d, f"{m}-{a}-{b}.log")
                        if os.path.isfile(key + ".log"):
                            t = open(key + ".log", encoding="utf-8", errors="replace").read()
                            open(out, "w", encoding="utf-8").write(t.replace("@@BOTA@@", a).replace("@@BOTB@@", b))
                            hits += 1
                        else:
                            todo.append((a, b, m, f, key, out))
        log(f"{len(todo)} games to play, {hits} from the cache")
        tmp = tempfile.mkdtemp(prefix="fastscreen-")
        for attempt in range(3):
            if not todo:
                break
            man = os.path.join(tmp, f"manifest{attempt}.txt")
            with open(man, "w", encoding="utf-8") as fm:
                for j, (a, b, m, f, key, out) in enumerate(todo):
                    rep = os.path.join(tmp, f"g{attempt}_{j}.repl26a")
                    stats = "" if ROUNDS else f' --statistics "{rep}.json"'
                    fm.write(f'"{os.path.join(ROOT, "bots", a)}" "{os.path.join(ROOT, "bots", b)}" "{os.path.join(ROOT, f)}" "{rep}"{stats}\n')
            cmd = [CAMBC, "run-batch", man, "--jobs", str(JOBS), "--json", "--color", "never"]
            if os.environ.get("MATCH_TIMEOUT"):  # wall-clock seconds per match (a hung game otherwise blocks the whole screen)
                cmd += ["--timeout", os.environ["MATCH_TIMEOUT"]]
            if not ROUNDS:
                cmd += ["--log-limit", "0"]  # cut-off mode reads the REPORT line from the bundle's stdout
            if ROUNDS:
                cmd += ["--rounds", str(ROUNDS)]
            t1 = time.time()
            r = subprocess.run(cmd, capture_output=True, env=env)
            open(os.path.join(tmp, f"batch{attempt}.log"), "wb").write(r.stdout + r.stderr)
            left = []
            for j, (a, b, m, f, key, out) in enumerate(todo):
                js = os.path.join(tmp, f"g{attempt}_{j}.repl26a.json")
                text = None
                if ROUNDS:
                    cand_a = a in names
                    rep = report_of(os.path.join(tmp, f"g{attempt}_{j}.repl26a"), "a" if cand_a else "b")
                    if rep:
                        text = synth_cut(a, b, f, cand_a, rep[1], rep[2], rep[0])
                elif os.path.isfile(js):
                    try:
                        text = synth(json.load(open(js, encoding="utf-8")), a, b, f)
                    except (ValueError, KeyError):
                        text = None
                if text is None:
                    left.append((a, b, m, f, key, out))
                    continue
                open(out, "w", encoding="utf-8").write(text)
                ph = text.replace(f"{a} vs {b} on", "@@BOTA@@ vs @@BOTB@@ on").replace(f"({a})", "(@@BOTA@@)").replace(f"({b})", "(@@BOTB@@)")
                ph = re.sub(rf"^(  A    ){re.escape(a)}(\s)", r"\1@@BOTA@@\2", ph, flags=re.M)
                ph = re.sub(rf"^(  B    ){re.escape(b)}(\s)", r"\1@@BOTB@@\2", ph, flags=re.M)
                open(key + ".log.tmp", "w", encoding="utf-8").write(ph)
                os.replace(key + ".log.tmp", key + ".log")
            log(f"played {len(todo) - len(left)} games in {time.time() - t1:.0f} s ({(len(todo) - len(left)) / max(1e-9, time.time() - t1):.1f}/s)" + (f", {len(left)} to retry" if left else ""))
            todo = left
        if os.environ.get("KEEPTMP"):
            log(f"kept {tmp}")
        else:
            shutil.rmtree(tmp, ignore_errors=True)
        e = dict(os.environ, EXPECT_MAPS=" ".join(m for m, _ in maps), EXPECT_OPPS=" ".join(OPPS))
        r = subprocess.run([sys.executable, "tools/bamboo/local/evalsum.py", run, *names], env=e)
        log(f"total {time.time() - t0:.0f} s")
        if r.returncode:
            log(f"EVALUATION INVALID (exit {r.returncode}): see INCOMPLETE above")
        return r.returncode
    finally:
        if not os.environ.get("KEEP"):
            for n in names:
                shutil.rmtree(os.path.join("bots", n), ignore_errors=True)
        try:
            os.rmdir(lock)
        except OSError:
            pass


if __name__ == "__main__":
    sys.exit(main())
