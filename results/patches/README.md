# Patches for the combined bot

Each patch applies to the source of a bot on the v1530 line, in `src/` of a plain bot or `src/cj/` of a router:

```
git apply --directory=bots/NEW/src/cj --whitespace=nowarn results/patches/ra1.patch
```

Add `--3way` or `--reject` if a teammate's change touches the same lines. Then build, run a local fault check and play it on the pinned panels. `ra1.patch` was checked against `bots/bamboo1530/src`: the result equals `bots/exp/ra1/src`, line endings aside.

| Patch | What it does | Evidence | State |
|---|---|---|---|
| `ra1.patch` | v1530 to `ra1`, the default arm of v1533: map arms (`results/analysis/a8.json`: L on 01elk_arena, 01hooks, 00quarry, 00pilgrimage, 01fracture; G2 on 00rows, 02arena; GN on 03one_gem), the opening book on 2 maps, Vesper's gold rules, fights that know Cassi and Issac die together | Against v1531 on `nb1` + `nb2`, 125 pinned games: team gold r300 +60 +- 38, margin +3 +- 48, tributed r1000 -6 +- 22, deaths r1000 +0.3 +- 0.3, wins 65 against 62 (`rule_arms.md`). A modest gain | Live as v1533 from 19:40 to 20:23 IST |
| `fa4.patch` | Marcella next to a target uses hit + reset (a stun) before her nuke | 672 paired local games: wins +0.01, margin +3.8 +- 5.2, collected -0.7 +- 2.7, deaths -0.03 +- 0.07, no fault (`rule_nuke.md`) | Passes locally, not played on the platform (`exp/rc1`) |
| `six.patch` | Six bodies: `n_allies` up to 6, `ainfo` and the other ally arrays to 6 entries, a rally of 5 means everyone. Without it the sixth body with Cassi and Issac on five picks keeps `idx` -1 and overwrites its own ability data (`docs/findings.md`, "The sixth body") | Local: Issac 0 casts without it. Check of the fix itself is in `results/analysis/rule_final.md` | v1535's Issac casts normally, so v1535 probably has its own fix: look for `std::min(5` at `n_allies` in its `bot.cpp` first. The `farm.cpp` hunk may need the two `where` and `home` lines by hand (`ra1` changes the line above them) |
