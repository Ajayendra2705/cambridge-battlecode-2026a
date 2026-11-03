# Status (updated Tue, Nov 3, 2026 11:40 PM IST)

## Note at 23:40 IST 11-03 (session 94, branch `night-1101`)

- **Live and selected: v1536** (`bots/bamboo1536`, test copy `bots/exp/rf1`), the user's choice at 23:30 IST: v1533 + 8 more Bamboo maps + `fa4`. On the added maps against v1531: 63 to 51 of 125 pinned, margin +133 +- 58, team gold r1000 +541 +- 142, deaths -1.6 +- 0.5. Most of the gain is 00breadcrumbs and 01corridors; the written bar on `nr3` missed on wins by a hair (`rule_route2.md`).
- **Running:** `data/run_rfnb.sh`: `live rf1_nb1 nb1`, `live rf1_nb2 nb2`, 125 games against `e1531_nb*` and `ra2_nb*` (whole-bot check and `fa4`; bars in `rule_route2.md`, `rule_nuke.md`).
- **New tool:** local gold per map predicts the Bamboo arm's platform gold per map (`tools/local/lmapgold.py`, `tools/replay/pgoldmap.py`): 01corridors +2323 local, +2187 on the platform; the default arm has blind spots there.
- **Next:** `exp/rh1` = v1536 without 00gemfight, 00reverse_spiral, 00gem_fields and with 01broken_curve, 00eight, 00vault, 02gift_wrapping, 02uncharted_lands. Panel `nr4`, base `live e1536_nr4 nr4` (no flip), then `rh1` (an upload: ask the user first). Bar in `rule_route2.md`.
- **Lock:** 05:29 IST 11-04. Combine at 00:29 IST. Start no gate after about 04:30 IST. Check the selected bot before the lock.

## Note at 22:30 IST 11-03 (session 94, branch `night-1101`)

- **Live and selected: v1531.** Someone on the team selected it at about 21:21 IST, after v1535 scored 12 of 60 on the teammate's top-team panel. So the note below is out of date on the live bot. v1531's source is in the repo.
- **Candidate: `exp/rf1`** = v1531's router + `ra1` in the default arm + 8 more maps on the Bamboo arm (01corridors, 00quadrants, 00gemfight, 00breadcrumbs, 00reverse_spiral, 03shrines, 00contest, 00gem_fields) + `fa4`. Local regression on 85 maps against `exp.ra1`, 679 paired: wins +0.02 +- 0.01, margin +20 +- 16, deaths -0.20 +- 0.20, no fault.
- **Running:** `data/run_rf.sh` (user approved at about 22:05 IST): when the team's tests are quiet it uploads `rf1`, plays `nr2` (75 games, base `e1531_nr2@nr2` 29 of 75), and selects the version live before it again. Rule in `rule_route2.md`. rf1 stays live only if the user says so.
- **Next on the platform (ask first):** `fa4` and the whole of `rf1` on `nb1` + `nb2` against `ra2_nb*` and `e1531_nb*` (25 groups); a fresh panel for the maps that join.
- **Running locally:** `exp/hm3`, Willow's heal threshold 0.6 to 0.3 (`rule_heal.md`).
- **Combine at 00:29 IST:** if a teammate pushes a newer source, apply `ra1.patch`, `fa4.patch`, the router lines and check `std::min(5` (`six.patch`, only for six bodies). Otherwise the candidate is `rf1` or a variant of it. Keep about 50 groups for the final base and bot, start no gate after about 04:30 IST, and check the selected bot before 05:29 IST.

## Note at 21:30 IST 11-03 (session 94, branch `night-1101`)

- **Deadline.** International Qualifiers lock at 05:29 IST 11-04. The selected bot enters. User: keep working until 5 hours are left (00:29 IST), then combine.
- **Live and selected: v1535**, the teammate's "Bamboo RT33" (uploaded 20:46 IST): v1534 ("RT32": v1531 + nav fuel fix + Willow peel, no-trade, HP build, behind) + top-5 drafts (five picks Heart, Marcella, Vendetta, Vesper, Cassi and Issac). **Sources of v1534 and v1535 are not in the repo**; `origin/Bamboo8` stops at 1530, and `cambc` has no download. The combine needs them: the user was asked to ask the teammate to push.
- **Parts for the combine** (`results/patches/README.md`): `ra1.patch`, `fa4.patch`, `six.patch`, and the router table lines of `rd1` (8 more maps on the Bamboo arm).
- **Running:** `live e1535_nr2 nr2`, v1535's base on the 8 candidate maps; it selects nothing. Then `exp/rf1` needs the live slot on `nr2` (rule in `rule_route2.md`) and, for `fa4`, on `nb1` and `nb2` against `ra2_nb*`: ask the user first, wait for a quiet slot with `data/teamclear.sh`, select the live bot again after it.
- **Running locally:** `data/run_c3x.sh`: `exp/c30` (v1530 with v1535's five-pick draft and `six.patch`) and `exp/c31` (`ra1` with the same) on the 51 five-pick maps. Bar in `results/analysis/rule_final.md`: does `ra1` still gain with the pair in the draft.
- **Found tonight:** up to v1533 the sixth body with the pair on five picks has no abilities (`idx` stays -1 and `ainfo[idx]` overwrites them; Issac 0 casts locally). v1535's Issac casts normally, so it is fixed there or never applied. All earlier five-pick tests of the pair were flawed (`docs/findings.md`, "The sixth body").
- **Quota is shared and scarce:** the teammate takes it within about 40 seconds of release. Keep about 50 groups after 00:29 IST for the final base and merged bot on `nb1` + `nb2`, and start no gate after about 04:30 IST.
- **After the combine:** local fault check, the same 125 pinned games with its base, ask the user before it stays live, and check the selected bot before 05:29 IST.

## Note at 20:13 IST 11-03 (session 94, branch `night-1101`)

- **Live: v1533** (`bots/bamboo1533`, test copy `bots/exp/ra2`): v1531's router with `ra1` in the default arm; user, 19:40 IST: "Yes, v1533 live". Against v1531 on `nb1` + `nb2`, 125 pinned games: team gold r300 +60 +- 38, margin +3 +- 48, tributed r1000 -6 +- 22, deaths r1000 +0.3 +- 0.3, wins 65 against 62. A modest gain. Ladder: rank 40 at 19:53 IST.
- **Gates are allowed by the user** (one chain at a time). A new bot stays live only after the user says so. Select 1533 after every chain: `cambc submissions activate 1533`.
- **Chain running or waiting:** `data/run_rc.sh`, plan `data/plan_rc.txt`: `exp/rc1 rc1_nb2 nb2`, then `v1534 rc1_nb1 nb1` (check that 1534 is rc1). The plan does not end on the live bot. **If the session is closing, stop the chain by pid (`tools/platform/procs.sh`) and select 1533.**
- **Candidates.** `exp/rc1`: v1533 plus `fa4`, Marcella next to a target uses hit + reset (a stun) before the nuke; rule in `results/analysis/rule_nuke.md`, judged against `ra2_nb1@nb1` and `ra2_nb2@nb2` with no base rerun, because a pinned panel replays exactly. `exp/rd0` (8 more maps on Bamboo) failed its local bar and did not play (`rule_route2.md`); the map filter for its successor `rd1` is written there, and `exp/rall` plays the Bamboo arm on all 85 maps locally to feed it.
- **Quota is shared.** At 19:33-19:35 IST a teammate played 15 groups against the top teams while my base rerun had v1531 selected, so those games may have played v1531 or v1533, not one bot. Quota was 50 of 50 at 19:53 IST.
- **Rejected locally tonight:** `esw75`, `esw100`, `pk5`, `rd0` (`docs/experiments.md`). Disk has under 2 GB free: delete each screen run after judging it.
- **Next ideas:** Bamboo arm fuel on 00dunes and 00corners (54 and 14 exhausted turns with an enemy near, per game); the teammate's rivals on other maps (32 groups) if the user wants it.

## Note at 16:15 IST 11-03 (session 94, branch `night-1101`)

- **Live rule: v1531** (user, 15:50 IST: "keep 1531 live after your test"). It is live and selected (checked 16:13 IST), and nothing of ours runs.
- **The queue stopped before any gate played.** The user asked for it ("queue all ours"), then closed the chat at 16:12 IST. A chain needs a running session to select v1531 after its last gate, or a test bot stays live on the ladder, so I killed `data/run_q1.sh` at 16:13 IST while it still waited for quota. None of its 8 gates ran, so `ra1`'s map arms have not been played on the platform.
- **To resume:** read `tools/platform/procs.sh` and `cambc submissions list`, check that no teammate is testing (`tools/platform/recentgroups.py`), then start `bash data/run_q1.sh` once with the tool's background option. **Select v1531 again when it ends.** `data/` and `bots/exp/` are gitignored and exist only on this laptop. The script runs `GATE_Q=gateq_fast.sh GATE_RESTORE=none QUIET=30 QWAIT=6 bash tools/platform/gatechain.sh data/plan_q1.txt`, and the plan is:

  ```
  v1532 ra1_nb1 nb1
  v1531 e1531_nb1 nb1
  exp/vfx2 vfx2_t03pa t03pa
  exp/vfx1 vfx1_t03pa t03pa
  exp/vfx3 vfx3_t03pa t03pa
  exp/vmr2 vmr2_t03pa t03pa
  exp/vgv2 vgv2_t03pa t03pa
  exp/vfu2 vfu2_t03pa t03pa
  ```

  Judge with `tools/platform/rcmp.py` and `tools/replay/pgold.py`: `ra1_nb1` and `e1531_nb1` against `e1530_nb1@nb1` (bar in `results/analysis/rule_arms.md`), the others against `b1512_t03pa@t03pa` (bars in `rule_nuke.md`, `rule_vesper.md`, `rule_setup.md`).
- **`ra1` (v1532) on the teammate's panel `tm1`:** passes its bar: Vesper gold r300 +72 +- 25, team gold r300 +35 +- 23; wins 12 against 12, margin +14 +- 33. v1531 on the same panel: 26 wins, margin +216 +- 68 (`docs/findings.md`, "On near maps v1531 wins without early gold").
- **`exp/ra2`** = the 7-map Bamboo router with `ra1` elsewhere; builds, needs a local screen. `esw75`, `esw100`, `pk5` also wait for one. The user asked for a break from local runs because the laptop was hot, and has not said when they may start again. `ra1` and `ra2` use the map arms in `results/analysis/a8.json`.

## Note at 14:40 IST 11-03 (session 94, branch `night-1101`)

- **Live: v1530.** A teammate pushed `bots/bamboo1523` and `bots/bamboo1530` to `origin/Bamboo8` (exact sources) and made v1530 live at 08:28 UTC. The user's rule named 1523, and the choice is theirs to change; I did not flip it. Both folders are now in this branch, and `exp/b30`, `exp/b23` are their test copies.
- **New base for local screens: `exp.b30`.** Run `b30base` screens both bots against `multi-031107`.
- **`exp/ra1`** is v1530 with rt8's table (arms on 8 maps, book on 2, Vesper's rules, `vpa1`), `tools/variant/mk_rt.py`, `mk_vbk2.py`, `mk_rt8.py` with `SRC=src`. Bar in `rule_arms.md`.
- **`exp/ra1` passes its local screen against `exp.b30`:** team gold r300 +45 +- 10, r600 +88 +- 25, captures +1.3 +- 0.4, deaths -0.15 +- 0.17, margin +9 +- 14 (`rule_arms.md`). It is the next gate candidate; asking the user first.
- **Waiting, not built or played:** `exp/esw75`, `exp/esw100` (`P_ENEMY_SIDE_W`, rivals earn 316 against our 87 gold on the far half by r600) and `exp/pk5` (elk pack on five picks), bar in `results/analysis/rule_gold.md`.
- **Head-to-head against v1503 (`tools/local/h2h.py`)** is not a better predictor yet: it ranks 1523 below v1503, where the platform ranks it above.
- **Break at 15:30 IST:** the user asked for a pause because the laptop runs hot. No local runs until they say so. The user's ffmpeg jobs also leave little memory (bash forks failed at times).
- **Gold gap against hard neighbours is capture count:** rewards to r600 23.2 against 28.7 a game at the same gold a reward; rival Vesper 10.7 rewards at 137 gold, ours 6.1 at 99 (`tools/replay/goldsrc.py`).

## Note at 14:03 IST 11-03 (session 94, branch `night-1101`)

- **Live: 1523**, by the user's rule. No gate runs. Asked the user at 13:02 for one gate of `rt8` on `a7p`; no answer yet.
- **New view: ranked neighbours decide the rating** (`docs/findings.md`, "Neighbours decide the rating"). Win rates by size, map, rival and draft come from `data/rk8.json` and `data/rk9.json`; `data/fights/q_all` holds the decoded games. Hard rivals near our rank: Sheeesh---, jazz, Jupiter, MFF1. `tools/platform/rkpanel.py` makes a pinned panel of the newest ranked groups: with `--since` set after 1523 went live, the source groups are 1523's own games, so they serve as the base with no rerun.
- **`exp/rt8` passes its local screen** (`rule_arms.md`). **`exp/rt9`** = rt8 plus the siege from spawn tiles on 03homonoliths (`mk_vhm.py`, base 5 of 12, vhm120 12 of 12 locally; 1523 has this already by its note). Only that map changes between rt8 and rt9.
- **Rejected locally:** later guard siege on gated altars (`vsb7` +0.07 wins over four seeds, bar +0.15; `rule_gate.md`).
- **`data/map_info.json`** holds every map's altars, spawn tiles and camp groups (from a temporary probe). Gated altars: 01boss_battle, 02guardians. Heavy maps: 00contest, 00great_wall, 00stampede, 01starvation, 02fields, 03homonoliths. Single-altar maps: 19 of 85.
- **1523's source is still missing:** the Chrome extension is offline and the newest zip in Downloads is older. With the source a 1523-based router can be built (`tools/variant/nsbot.py`).

## Note at 12:51 IST 11-03 (session 94, branch `night-1101`)

- **Live: 1523, by the user's rule** (12:20 IST: "keep live as v1523 until you find any better things"). The gate chain is stopped and its remaining lines are skipped. A match group plays the active version and `cambc` has no version option, so any gate makes the tested bot live, and it plays one ranked set (5 games) first. An upload takes the selection too. Ask the user before any gate or upload.
- **rt5 and 1523 are level over 175 pinned games against ranks 1-20:** 43 against 46 wins, mean margin -382 against -378 (`t03pa`, `t03pb`, `a7p`). They win on different maps: 01hooks 3 against 0 of 7, 01shortcut 5 against 1 of 8, 02the_pack 6 against 4 of 8, 00split 2 against 6 of 8.
- **Next candidate needs 1523's source.** 1523 drafts as v1503 does, so it is on the v1503 code line (notes of 1513: v1503 + every-turn recall + bush wards): rt5's arms and the Bamboo map routes can go on top of it. The user approved downloading the zip (11-03 12:15), but the Chrome extension is offline and the CLI has no download command. The user can reconnect it or click "Download .zip" on the Submissions page; it lands in Downloads.
- **rt7 rejected on the platform:** team gold r300 1109 to 1302 and r600 2629 to 2917, but tributed to r1000 -51 +- 30, final margin -96 +- 74, wins 16 against 17 (`rule_arms.md`). Gold weights trade gems for gold.
- **`exp/rt8`** (light arms on 5 maps, four arms that held on the platform and locally, GN on 03one_gem, Vesper's vvk1 rules, `vpa1`) is on its local screen; rule in `rule_arms.md`.
- **Rejected or closed locally:** `vfg1`, `vfg2` (fuel gates x0.1, x0.5: gold falls), four-pick and five-pick draft arms (first sample did not repeat), gem weight outside 03one_gem. `vpa1` (fights know Cassi and Issac die together) passes against pair opponents.
- **Cleanup:** 114 run folders from 10-30 to 11-02 deleted with the user's OK. Deleting older decoded games, replays and summaries was refused by the auto mode classifier; summaries are compressed instead. Disk has 13 GB free.

## Note at 10:53 IST 11-03 (session 94, branch `night-1101`; the user asked for work through the night)

- **1523 leads rt5** on the t03p parts: part a 16 against 13 of 60 (flips 5 against 2), margin 82 +- 46 for 1523; part b 16 against 13 of 55, margin 31 +- 55. Part c's 1523 gate is skipped. The source of 1523 is not in the repo.
- **Arm tables grew** (`results/analysis/rule_arms.md`, findings 'Per-map gold and gem weights'): gold weight 2 passes the table rule on 15 of 26 maps in fresh samples. `exp/rt7` holds 21 maps of arms and Vesper's gold value (vgv2). Chain order after the fight variants: `rt5_a7p`, `rt7_a7p`, `e1523_a7p`, then `vfx2`, `vfx3`.
- **Setup fuel** (`results/analysis/rule_setup.md`, findings 'Setup fuel'): every map loses the first turn. `exp/vfu2` reads a draft plan and ends its setup on r1 on 78 maps, 0 mismatches on 85. Locally, acting earlier does not raise gold (r600 -88 +- 37), the same as `vfi1` earlier tonight. Deaths no longer rise (+0.08). It passes the written bar, so it may go to the platform at low priority.
- **Rejected locally:** `vms1`, `vms2` (strike first), `vfu1`, `vfu4`.
- **Needs the user:** deleting old `data/runs` folders (compressed for now, refused by the auto mode rule), and downloading the 1523 source zip from the submissions page.
- **The chain leaves the bot under test live.** Select the team's best bot by hand when the plan ends.

## Note at 07:35 IST 11-03 (session 94, branch `night-1101`; the user asked for work through the night)

- **Router tables closed.** `b2p` (8 against 9 of 60) and `b3p` (Bamboo 7 against v1503 21 of 60 on the `03*` maps) add no map to `exp/rt3`; v1503 wins 35% of the `03*` games against the top 12 and only 15% on the `b2p` maps.
- **New measured gap: captures go to the wrong champions** (`docs/findings.md`, 07:00 section). Rewards of at least 60 gold by r150: ours Vendetta 0.89, Heart 0.79, Marcella 0.64, Vesper 0.36; theirs Marcella 1.13, Vesper 1.11, Heart 0.45, Vendetta 0.41. Vesper's first capture r69 with 0.7 helpers against r43 with 1.8. Spent gold at r100 110 against 229 with equal unspent gold, so it is earning, not shopping.
- **Rejected locally tonight:** wolf-first (`vwf1`-`vwf3`), route detours (`vdt1`, `vdt2`), shorter tank waits (`vpw1`, `vpw2`), Vesper's capture weight alone (`vcv1`), the opening book (`vbk1`, `vbk2`). Copying the rivals' targets without their fight strength loses gold locally.
- **Queued local screens, in order:** `vj` (Vesper follows the team and captures; `rule_vesper.md`), then `ce` (captures go to carriers) with `d5` (Tavi or Ryth for Willow; `rule_ci.md`), then `nt` (joiner's share), then `ch` (no solo chipping; `rule_share.md`).
- **Chain** `data/run_tg6.sh`: `rt3_l5p` done, then `vlm1_l5p`, `s5p` base and `dci5f` moved ahead of the `t03p` lines, then `vvg1`, then rt3 against 1523 on `t03p`. The bot under test stays live: select the team's best bot by hand when the plan ends.

## Note at 06:15 IST 11-03 (session 94, branch `night-1101`; the user asked for work through the night)

- **Live: 1523**, the teammate's upload ("Bamboo v1513 + fuel fixes + spawn-tile siege, homonoliths"; it replaced our 1522 = `exp/rt3` at 05:19). Sources of 1513 and 1523 are not in the repo; the router could use 1523 as its default arm if they are pushed. `t03p` parts of rt3 against 1523 are queued; the rule is in `results/analysis/rule_route2.md`.
- **Chain** `data/run_tg6.sh`, plan `data/plan_tg6.txt`, through the new `tools/platform/gateq_fast.sh`: no restore between gates. A change of the active bot waits for the running ranked set, so each restore cost a full 10-minute cycle (20 minutes a gate). The bot under test stays live until the next line, so **select the team's best bot by hand when the plan ends**. The unranked quota (50 groups an hour, shared) is now the limit: 12 groups a gate, about 4 gates an hour.
- **New factor: the first 100 rounds** (`data/openmap_t03.txt`, 510 games against ranks 1-20). Hits on camps to r100: wolves 33 against 56, elks 44 against 48, total 103 against 135. Team gold r50 87 against 144, r100 250 against 373, r150 409 against 613; first reward r50 against r32. Local screens running (`data/screen_wf.log`): `exp/vwf1-3` (wolves before elks, `rule_wolf.md`) and `exp/vdt1-2` (cheap harmless groups near the route, `rule_detour.md`).
- **Fights:** in the same situation (`decoded.py assist`) the rivals' teammates die 0.05 against ours 0.22 and enemies die 0.64 against 0.25; every champion type shows it at equal numbers near. Their bodies carry more health from r150 (1228 against 1049), and much more from r400 (2168 against 1439). So the fights follow the gold, and the gold gap opens in the first 100 rounds.
- **Disk:** C: filled at 05:34 and stopped two screens. NTFS compression of `data/runs` freed about 28 GB; `tools/local/screen.sh` now hard-links the base's files. Deleting old `data/runs` folders was refused by the auto-mode classifier and needs the user's decision.
- **Local passes:** `exp/vvg1` (Vesper takes harmless gold groups first before r200: her gold r300 +37 +- 10, team +17 +- 8) is at the end of the plan. `vgw2`, `vge15` held, `vge2`, `vvg2` rejected.

## Note at 05:12 IST 11-03 (session 94, branch `night-1101`; the user asked for work through the night)

- **Live: 1522 = `exp/rt3`**, the per-map router: Bamboo v1472 on 7 near maps (00interlock, 00fragment, adgato_gemcombat1, 02crossing, 00corners, 00anvil, 00dunes), v1503 with logs off on the rest. On those maps pinned (`r7p`), the router against v1503: 15 wins against 8 of 60, flips 9 against 2, margin +152 +- 63. No-log arm locally: exhausted turns 10.19 to 7.73 a game on default maps, gold r300 +30, deaths -0.35 +- 0.17. It replaced 1519 (pack opening, level on the platform and rejected). Rule: `results/analysis/rule_route2.md`.
- **New gap: the 15 `03*` maps** are 15% of our ranked games and were in no platform panel. We win 46% there; 03one_gem 1 of 9. That map has one gem cluster, and v1503 ignores it until about r700 (0 of 16 locally, Bamboo 7 of 8). Panel `b3p` (v1472 against v1512 on these maps) is queued.
- **New measure: gem income per map** (`data/map_rates.json`). Against ranks 1-20 we win 9 of 112 on the 11 maps under 2.5 gems a round, collected 272 against 808, deaths 14.4 against 5.0; ranked 39 of 105 there against 55% elsewhere. On 01elk_arena the rivals send a pair to the centre and the rest to gold clusters; we walk five to the elks at once and lose the first fight with no gold.
- **Chain** `data/run_tg4.sh`, plan `data/plan_tg4.txt`, `GATE_RESTORE=1522`: base1503 and v1472 on `b2p` (15 more candidate maps), then on `b3p`, then rt3 on `t03p` parts, then base1503 and dci5f on `s5p`.
- **Closed:** early contact (vtg70, vpk3: local gain in deaths does not reach the platform). Within-line variants have no correlation between local and platform per-map differences (0.0-0.17), while the Bamboo line against the bot_10 line has 0.46-0.54, so a map table only makes sense across different lines.
- **Next:** extend the router from `b2p` and `b3p`; per-map light-camps arm for elk maps; read how we lose on 03 maps.

## Note at 02:30 IST 11-03 (session 94, branch `night-1101`; the user asked for work through the night)

- **Ladder: rank 33** at the last check (2142; rank 1 Fish 2577). Live: **1513**, the teammate's upload. Our gates restore it. The teammate is active too: at 01:37 they selected 1513 during `v1472_b1p`, so its last 25 games are 1513's, not 1472's.
- **Factor now: first contact** (`results/analysis/rule_pack.md`). Our team splits in the first rounds. vtg70 did not change that and is rejected on the platform. `exp/vpk3` walks as one pack before r60 on maps with spawns at most 61 steps apart; local deaths r300 -0.20 +- 0.09, on near maps -0.40 +- 0.15, gold and wins level. Queued on t03p parts a-c.
- **New: every champion skips round 1 on every map** (`if (fuel() < 120000) return;`, `results/analysis/rule_firstturn.md`, `tools/local/firstturn.py`). `exp/vfi1` (50k) and `exp/vfi2` (25k) are in their local screen (`data/screen_fi1.log`).
- **Map choice:** the router `exp/rt1` waits for `v1472_b1pb` (the 25 games still missing); the first 35 games of `v1472_b1p` were 7 wins against 4 for v1503, margin +153 +- 96.
- **Draft:** d3m on s3p is running; dci5f on s5p follows the pack test.
- **Chain** `data/run_tg2.sh`, plan `data/plan_tg.txt`, one run only; it waits for the teammate's quiet periods (`QUIET=240`).
- Rejected: vtg70 and vtg40 (platform), vpk1 (wins guard), wag1, dci5m, dci4, d3c, d3r, vci1 (local). All in `docs/experiments.md`.

## Note at 01:20 IST 11-03 (session 94, branch `night-1101`; the user asked for work through the night)

- **Ladder: rank 33** (2142; rank 1 Fish 2577, rank 2 Mite 2568). Live: **1513**, Eric's upload (v1503 + every-turn recall + bush wards), the best paired gain so far (42 against 36 of 160); its source is not in the repo. Our gates restore it.
- **Factor now: map choice and draft.** `exp/rt1`, a per-map router (16 maps to Bamboo, the rest to v1503), passed its local screen (`results/analysis/rule_route2.md`). Pinned panel `b1p` (v1472 against v1503 on 15 candidate maps) is queued; the table is decided from that.
- **New lead: Cassi and Issac** (findings, "Per-map differences between our bot lines, and Cassi and Issac"). We win 3 of 34 five-a-side games against them, and ranks 1 and 2 play them. `exp/dci5m`, `exp/dci5f`, `exp/dci4` are in their local screen (`data/screen_ci1.log`, rule `results/analysis/rule_ci.md`).
- **Chain** (`data/run_tg2.sh`, plan `data/plan_tg.txt`): vtg70 on t03p (parts a, b done, c running), then base1503 and v1472 on b1p, then base1503 and d3m on s3p. It waits for the teammate's quiet periods (`QUIET=240`).
- Rejected locally: vfc1, vsg1, vsg2, vop1, vtr1 (`docs/experiments.md`).
- Next: judge vtg70 and b1p, set the router table, make the best bot live; if a C&I draft passes locally, panels `s4p`, `s5p`.

## Note at 22:30 IST 11-02 (session 94, branch `night-1101`)

- **Ladder: rank 33** (2151; rank 1 Mite 2574). Live: 1504 (the teammate's v607); our gates restore it.
- **h1503 rejected on the platform** (t03p, 170 games pinned to the teammate's 1503 games): our deaths -0.6 +- 0.4
  but the rivals' -0.9 +- 0.4, collected -31 +- 16, margin -70 +- 29, 28 wins against 37. More caution in fights
  costs kills and farming; wre1 and whc2 (the same kind of change) were taken off the chain unplayed.
- **wos1, wdg1, wdh1 failed their local screens** (`docs/experiments.md`).
- **New factor: early team gold** (findings, "Early massacres, pack fights and Vesper's gold"). A third of the games
  against ranks 1-20 are decided by r300 (we win 1 of 64 massacres); after sighting a pack we choose as the top
  teams do but lose the fight (items, health). Team gold is 0.71 of theirs at r100; the gap sits with Vesper (camp
  gold by r150 97 against 263, first capture r83 against r44) and Marcella. Their Vesper captures the groups the
  team kills. Variant `exp/vj1` (Vesper joins the team's gold-rich kills before r250) is in its local screen
  (`data/screen_vj1.log`; bar in `results/analysis/rule_1498.md`, "Vesper joins the team's kills on 1503").
- **Chain** (`data/run_h1503.sh`): pool/v1491 on t03p (bridges everywhere against 1503's games); part a 10 of 60
  against the base's 13. Then nothing queued.
- New tools: `tools/replay/packmove.py`, `tools/replay/soloshare.py`, `tools/local/lgold2.py`.

## Note at 21:05 IST 11-02 (session 94, branch `night-1101`)

- **Working line: the teammate's (chejibt001, team "cheji bt") v548 line.** Every upload is "v548 + one flagged
  change", tested at once in 135-345 unranked games against ranks 1-20 (findings, "How the teammate chejibt001
  works"). Their sources are on the website (Submissions, "Code"; `docs/WORKFLOW.md`): `pool/v548` is the exact 1490,
  `pool/v1491` and `pool/v1503` were downloaded (hashes checked), `pool/v1502r` rebuilds 1502.
- **Live: 1504** (the teammate's v607) between our gates; our gates select their own uploads (1506 = h1503).
- **Factor: our deaths against ranks 1-20.** Our champions are dead 14.2% of champion-rounds against 6.2%, and every
  champion type dies 2-2.7 times as often as the same type of theirs (`decoded.py types` on `t1503_tm@t03`). Their
  Marcellas (1700-4000 health) one-shot our 1000-health Vesper and Vendetta from 4 tiles.
- **Local passes** (85 maps, 680 paired games each, `tools/local/lbar.py`): whc (on 1502), h1503 and h1491 (whc on
  1503 / 1491), wre1 (enemy damage x1.3 in the fight sim), whc2 (stronger whc). wmp and wc failed. Screens running:
  wdg1 (danger weight), wos1 (one-shot guard).
- **Platform chain running** (`data/run_h1503.sh`, plan `data/plan_h1503.txt`; the user, 20:38: "queue all"; the
  user, 20:15: no need to wait for the teammate): each variant on t03p in three parts (12 + 11 + 11 groups) pinned to
  the teammate's own 1503 games (`t1503_tm@t03`, 170 games, 37 won). Order: h1503, h1491, wre1, whc2, then whatever
  `data/autoq.sh` adds. h1503 part a: 12 of 60 against the base's 13, flips 2 and 3, our deaths 669 to 622, theirs
  342 to 246. Rule: `results/analysis/rule_whc_t03.md`.
- Next: judge each variant on decoded deaths (`paired.py` against `t1503_tm@t03`), stack the passes, make the best
  live.


## Note at 03:05 IST 11-02 (session 92 closed by the user)

- **Live bot: 1488, made live by a teammate at 02:26 IST** ("v540 = v484 with shorter waits"; active, selected,
  pinned). Its ranked drafts are bot_10's on every map (near maps and three a side too), so it is a bot_10 build,
  not the 1478 hybrid; its source is not in this repo (no branch has v540). First 15 ranked games 21:00-21:20 UTC:
  10 won. Platform evidence that bears on it: three a side, bot_10 (hy3b) won 16 of 90 on b40p against the Bamboo
  bot's 29 (1478); five a side, the local per-map screens show the Bamboo bot ahead on most near maps.
- **15 new maps in the ranked pool since about 02:20 IST** (`03ambush_field`, `03colosseum`, `03contours`, `03fan`,
  `03homonoliths`, `03honeycomb`, `03membrane`, `03one_gem`, `03reef`, `03riverbed`, `03showdown`, `03shrines`,
  `03the_front`, `03twisty`, `03ultrastarvation`): 85 maps, none removed. Pulled into `maps/` with
  `cambc maps pull` (existing maps unchanged). Not yet in `data/map_features.json`, `data/map_sizes.json` or
  `tools/local/allmaps.txt`.
- No chain or local run is running. hym (00monolith to bot_10 inside the hybrid) passed locally but was not gated
  (moot while 1488 is live); its folder `bots/exp/hym` and panel m42 are kept. The 48-map screen
  (`rule_route.md`) stopped at 1195 of 1536 games, no verdict.
- Next: agree with the teammate which line is live (1488's bot_10 or the 1478 hybrid) before any gate, since a gate
  takes the live slot; then screen both parts on the 15 new maps (18% of ranked games) and finish the per-map
  screen; the trB proposal (tribute restart loops) still waits for the user.

## Note at 02:45 IST 11-02 (session 92, branch `night-1101`)

- **Live bot: 1478** (until 02:26; see above), selected and pinned (restored 02:24 IST after dv5's upload 1487 was cancelled). Ladder at 02:45:
  rank 44, 2077.5 (`data/ladder_1102_0245.json`).
- **New rule (user, 02:25): a variant goes to the platform only after it passes its local screen** (CLAUDE.md,
  `docs/WORKFLOW.md`).
- **Factor: five a side on near maps** (65% of ranked games are five a side; the Bamboo bot's near maps are the weak
  cell: 9 of 26 won on `l1478_b38`). Our camp hits are weaker (76.6 camp health per champion-round against 99.7,
  `tools/replay/campdmg.py`) and our gold falls behind (0.76 of theirs by r1000). Findings: "Five a side on near
  maps: weaker camp hits, and 00monolith".
  1. dv5 (Vendetta in Willow's place five a side, `kFifthPick = 4`): failed locally (deaths +2.5 a game, wins 18 to
     14 of 24); its gate was stopped before any game. Row R. The base run `hy1_b41@b41` (41 of 90, five-a-side near
     panel) and its pinned panel b41p remain for the next variant of this factor.
  2. **hym** (00monolith routed to bot_10; ranked 0 of 12 there with the Bamboo bot): passed its local bar (00monolith
     4 of 16 to 14 of 16, other maps unchanged). **Running on the platform** (`data/run_hym.sh`, started 02:43):
     hy1 (1484) on panel m42 (18 teams ranked 35-53, one 00monolith game each plus four other maps), then hym on
     m42p; judge `data/judge_hym.txt` (`tools/platform/mapcmp.py`). Rule: `results/analysis/rule_route.md`.
- Next candidates for the factor (each needs a local pass first): Vesper's emblem line toward the rivals' (Prospector
  of strength first; their Vesper lands 180 a camp hit against our 115), and less stacking five a side.
- trB proposal (tribute restart loops) still waits for the user's decision (note below).

## Note at 00:55 IST 11-02 (session 92, branch `night-1101`)

- **Live bot: 1478**, selected and pinned (restored 00:16 IST 11-02 after the last test gate; hy1, 1484, was active
  about 23:50-23:57 and 00:06-00:16 for its gates). Ladder at 00:57: rank 43, 2071.0 (19:55: 43, 2077.5).
- **Three a side, done:** the Bamboo bot stays. hy3v (vx1, upload 1482) 22 of 90 and hy3b (bot_10, 1483) 16 of 90
  on b40p against 1478's 29 (rows R); hy3s and hy3t (solo farming, short opening) local only, rows N. Findings:
  "Three a side against ranks 18-38: the Bamboo bot farms as a pack".
- **hy1 identity check** (`hy1_b38q`, upload 1484): 7 of 20 against 1478's 8 on the same games, same winner in 15.
  Close, not byte-identical; hy1 is the base of the small-factor variants.
- **Working directive (user, 21:07): one very small factor at a time, and improve only that.**
  1. Gold clusters by r300 three a side (hg3a-c, `kGoldEarly3`): R locally; a heavier gold weight only moves picks
     from gem clusters to gold clusters (`results/analysis/rule_hg3.md`, `tools/replay/goldpair.py`).
  2. **Tribute restart loops** (`results/analysis/rule_tr.md`, `tools/replay/loops.py`): the channel watch cancels
     a big tribute and the start rule restarts it at once, for 20-30 rounds at the altar. 1478 restarts 2.4 times a
     game on b38 and b40 (rivals 0.2-0.4). trA (`kReviewFix` 1) and trB (`kKeepChannel`) both pass locally (restarts
     5.72 to 0.34 and 0.11 a game, deaths and collected level). **trB passes on the platform** against its own
     build: hy1 (1484 selected) and trB (1485) on b38p and b40p, 180 pinned games; restarts 2.07 to 0.09 a game,
     23 games differ (13 better, 10 worse, flips 1 and 1, margin +13 a game), deaths and gems level
     (`data/judge_trB_hy1.txt`). Against 1478's games it missed the deaths bar by 0.006 (+0.306), which is the
     spread between hy1 and 1478 (hy1 itself +0.29). **Proposal, for the user to decide:** put the two lines
     (`results/analysis/trB_bamboo458sf.patch`) into the team's 1478 source and upload that; or select 1485 (trB
     on hy1), level with 1478 on these games (68 against 72 wins, margin +4 a game). Nothing was made live.
- **Incidents and fixes:** an upload takes the live selection and goes live by itself once it compiles (`pinned`
  turns false; `docs/WORKFLOW.md`), and a selection becomes active only 2.5-10 minutes after `activate`. So 1482
  (hy3v) played ranked sets 20:22-20:51, and trB (1485) probably played the 22:20, 22:30, 22:50 and 23:00 sets
  (ranked results then 1-4, 3-2, 2-3, 2-3). Selecting 1478 while upload 1486 compiled cancelled 1486 and stalled
  the chain (stopped 22:34). `gateq_live.sh`: `ver()` strips the CR of Windows python (the gate had waited for ever
  on "1482\r"); uploads wait for the ranked window; a refused selection is logged. A second gate of the same code
  selects the version (`vN`) instead of uploading it again.

## Note at 20:06 IST 11-01 (session 92, local branch `night-1101`)

- **Live bot: 1478** (pinned selection, unchanged). Ladder at 19:55: rank 43, 2077.5 (`data/ladder_1101_1955.json`).
  Final tournament: season end 18 Nov.
- **Factor: three a side**, our widest gap against teams above us (1472 ranked: 5 of 17, collected 473 against 701 to
  r1000; since 1478 went live 2 of 7). 1478 plays the Bamboo bot on every three-a-side map.
- **Chain `data/run_b40.sh` running** (started 20:04): 1478 as live on b40 (nine teams ranked 18-38, 90
  three-a-side games, `results/panels/specs_b40.txt`), pin to b40p, then hy3v (vx1 three a side) and hy3b (bot_10
  three a side) selected for their games, then hy1 on b38q (identity check of our copy of 1478). The live version is
  selected again after each gate. Judges: `data/judge_b40.sh` (outputs `data/judge_hy3v.txt`, `data/judge_hy3b.txt`).
  Rule: `results/analysis/rule_hy3_b40.md` (collected to r1000 +40 and 1.5 se; deaths and flips as guards).
- The cambc login had expired; `cambc login` in a tool call opened the browser, which approved it at once.


## Note at 17:12 IST 11-01 (session 91, local branch `night-1101`, not pushed; paused at the user's request)

- **Live bot: 1478 since 17:20:46 IST**, selected (`cambc submissions activate 1478`, no upload) at the user's request
  ("are you sure it is a better bot / if yes / upload it"). Before it, 1472, chosen again by a teammate after 1479
  (live from 15:41). Ladder at 17:12: rank 49. Nothing of ours was uploaded today.
- **Best evidence: 1478 ("Bamboo v1472 + bot_10 on far maps") beats the live bots** against teams above us. On b38p
  (ranks 21-45) 43 of 90 against 1479's 30; on b39p (ranks 22-39, other teams) 32 of 90 against 1472's 28; pooled
  flips 36 against 19, p = 0.03 (`results/analysis/rule_1478_b39.md`). The gain is bot_10 on far maps five a side
  (spawn walk 61+). It passes the rule written before b39; selected at 17:20 at the user's request.
- **hy1** (`bots/exp/hy1`): our own copy of 1478's rule (bamboo458sf near, b10n far, picked before the draft by a
  spawn walk that matches `sd >= 61` on all 70 maps). Next: the identity check `hy1_b38q` (four pinned b38p groups,
  `results/panels/specs_b38q.txt`; identical games to 1478 would prove the copy), then improvements on top of it.
- **Rejected today (local):** e_c3 / e_c4 (three economy constants: more captures, not more gems on 1479), e_cs,
  e_sp3, e_sp15, e_op60. 1479's own flags (r1479) trail 1472 three and four a side locally.
- **Tool change:** `tools/platform/gateq_live.sh` restores only what its gate changed (a selection made by someone
  else during the games stays live; a "live" gate never selects).


## Note at 15:35 IST 11-01 (session 91, local branch `night-1101`, not pushed)

- **Live bot:** 1472 (Bamboo v458 + Spell), selected by a teammate after 14:46 and pinned (`pinned: true`). Bamboo
  uploaded 1477 and 1478 ("Bamboo v1472 + bot_10 on far maps (hybrid 61)"); 1478 was live 14:24-14:46+. Ladder at
  15:34: rank 50, 2030.4 (48, 2050.6 at 13:35). Teammates keep the shared unranked quota full (50 of 50).
- **Platform (the user allowed it at 14:2x):** panel b38 (nine teams ranked 21-45, 90 games); base `l1478_b38@b38` =
  1478 without an upload, 43 of 90; b38p pins it. The cmb7 gate waited for quota and was stopped before any upload
  at 15:34, when the live bot had changed to 1472. `tools/platform/gateq_live.sh` restores by selection, not upload
  (`GATE_RESTORE=auto`: the version live before each gate).
- **Gap against teams above us** (95 decoded ranked games of 1472, `data/fights/rk1472_above`): gems collected to
  r1000 473 / 763 / 795 three / four / five a side against 701 / 889 / 859; 33 captures a game against 50; 2.15 own
  hitters per capture against 1.54 (3+ hitters 35% against 15%). Drafts explain little after rating (findings).
- **Local economy variants of 1472** (rows e_elk, e_mw, e_tw, e_lk): kElkBonus 1.0, kTravelWeight 1.4 and kLookahead
  0.5 each raise collected (+18 to +40 a game) with wins level or up; e_c3 combines them (screen stopped when the
  laptop ran short of memory; rerun at 2-3 jobs). Next on the platform: v1472 and e_c3 on b38p.


## Note at 13:10 IST 11-01 (read only)

`cambc submissions list --json` at 13:01 shows **1472 active again** (321,687 bytes, `bots/bamboo458sf`, the Sprint 3
bot); 1475 (the teammate's v519) and 1476 (uploaded 09:10 IST) are inactive. Wherever the 08:12 section below says the
live bot is 1475, read 1472. cmb7 head to head (140 games each, `multi-070127`): 66 against 1472, 72 against bot_10
(b10n), 73 against bamboo8, 91 against vx1, 108-125 against the pool. Level with the three teams' bots, ahead of ours.
Local work continues on the weakest part: three a side (10 of 24 against 1472).

## Update at 08:12 IST 11-01 (session 91, local branch `night-1101`, not pushed): best of all worlds, locally

Platform tests stay off until the user says so (04:36). Everything below is local and nothing was submitted. At 06:50
`cambc submissions list --json` showed 1472 (`bots/bamboo458sf`, the Sprint 3 bot) still active. **At 08:12 the team's
live bot is 1475** (69,252 bytes, uploaded 07:36 IST, note "v519 spawns<45 apart: pack opening to r120 + Ryth for
Vendetta at 5 (v484)"): the teammate's bot_10 line, newer than our `bots/exp/b10n` (bot_10 as of 02:34 IST). Its
source is not on origin, so cmb7's five-a-side part is the older bot_10; with v519's source, `src/cj` of cmb7 can be
replaced the same way (`nsbot.py SRC exp/NAME cj cjb`).

**Bots compared** (all on all 70 maps against cand1, cp3, dh3 and each other; facts in `docs/findings.md`, "Three teams'
bots in one program, locally"): vx1 (`bots/main`), b10n (bot_10 with its log off, `bots/exp/b10n`), bamboo8 (v1469)
and Bamboo's #458 line, pushed to branch `Bamboo8` at 10:25 AEDT and merged here: `bots/bamboo458` (v1471),
`bots/bamboo458sf` (v1472) and `bots/bamboo479`. Team size follows the map: 42 of the 70 maps are five a side, 16 four,
12 three.

**Best bot per size** (rule written at 06:22, row bamboo458; paired wins against the same six opponents):

| Size (share of maps) | Pick | Evidence |
|---|---|---|
| Three a side (17%) | vx1 | no bot passes: the Sprint 3 bot +0.056 +- 0.052 over all six opponents but -0.069 +- 0.067 against the pool |
| Four a side (23%) | the Sprint 3 bot (bamboo458sf) | +0.052 +- 0.040 against vx1, pool level; beats vx1 21 of 32 and bamboo8 21 of 32 |
| Five a side (60%) | bot_10 (b10n) | +0.087 +- 0.027 against the Sprint 3 bot (pool 210 of 252 against 183); beats vx1 59 of 84 |

**cmb7** (`bots/pool/cmb7`; vx1, the Sprint 3 bot and bot_10 by size in one program, `tools/variant/nsbot.py`) plays
each size as its part (within one standard error per size), with no fault in 980 games. Against the Sprint 3 bot alone
it gains +0.091 +- 0.027 a game five a side and gives back -0.069 +- 0.053 three a side (head to head 66 of 140). It is
the candidate for the platform when the user allows; it would replace the team's live bot only with the team's
agreement.
Caution: the five-a-side gain rests mostly on our local pool, which understates the Bamboo bots five a side. On the
ladder 1472 won 30 of 52 five-a-side games (58%) while the team rose to rank 44 (2057.3 at 07:55), where vx1 had won
21 of 59 (36%). Head to head over five fuel values (`multi.py --fuel`, 420 games a pairing) bot_10 beats 1472 0.560 +-
0.041 five a side and is level with bamboo8 (0.524 +- 0.041); three a side vx1 and 1472 are level (0.467 +- 0.077, 120
games), and four a side 1472 beats vx1 0.650 +- 0.061 and is level with bot_10 (0.562 +- 0.063, 160 games). So the
local evidence keeps cmb7 as built; only the platform can settle the size of the gain.

**cmb8** (`bots/exp/cmb8`) is cmb7 with bb458c four a side (below): on the 16 four-a-side maps it halves the fuel
exhaustions of cmb7 (27.1 to 13.7 a game) with wins level (-0.018 +- 0.035), no fault in 224 games. To make it from
`bots/pool/cmb7`, set `kSightCache`, `kPairWalkCache` and `kScoutWindow` to true in `src/bb/bot.cpp`. The platform
would choose between cmb7 and cmb8.

**Other measured parts** (rows in `docs/experiments.md`):
- Bamboo's #458 bots run out of fuel 117-121 times a game five a side (bamboo8, with three exact fuel caches, 84;
  bot_10 4). **bb458c** (the Sprint 3 bot with bamboo8's three caches `kSightCache`, `kPairWalkCache`, `kScoutWindow`)
  passes its fuel rule: 82.0 to 48.7 exhaustions a game, wins -0.015 +- 0.018, collected 98.8%, no fault. It is the
  one change here the team can put into its own Sprint bot without the platform's judgement. A fourth cache
  (`kCampCache`, bb458cc) adds exhaustions instead. Even with the caches, Bamboo's bot stays behind bot_10 five a side
  (pool 185 against 210 of 252).
- Bamboo's allocator in vx1 (vx1fa) cuts its exhaustions from 1.16 to 0.47 a game, wins level; in bot_10 it fails.
- Bamboo's spell finish in vx1 (vx1sf) and in bot_10 (b10sf) is level locally (a fight change: platform only).
- bot_10 fix variants b10hor and b10cap passed their screens (fight and item changes: platform only).
- Older combinations: cmb2 (vx1 three and four a side, bot_10 five; pushed for the teammate at 04:22), cmb5 (cmb2 with
  the allocator), cmb6 (bamboo8 four a side). All dispatch correctly with no fault.

**When the user allows platform tests:** gate cmb7 against the team's live bot in the same session on panels of teams
above us (`tools/platform/gatechain.sh`; batch panels of 40-90 games), with the rule written first: target the
five-a-side win share, guard three a side. Then the platform-only parts (vx1sf, b10sf, b10hor, b10cap) one at a time.

**Hazard before any gate:** `bots/main` is still vx1, but the team's live bot is 1475 (the teammate's v519, not in
this repo; 1472 = `bots/bamboo458sf` before it).
`tools/platform/gateq.sh` (under `gatechain.sh`) treats `main` as the bot already on the platform: a `main` plan line
plays without an upload, so it would measure the live bot under vx1's name, and after every gate it resubmits
`bots/main`, which would replace the team's live bot with vx1. So first agree with the team which bot is the base and
put it in `bots/main` (for 1475 that needs the teammate's source), or resubmit the team's bot by hand after the chain
and use an explicit bot name, not `main`, for the base line.

## Update at 04:28 IST 11-01 (session 91, local branch `night-1101`, not pushed)

- **The teammate made the Sprint 3 choice:** version 1468 (66,903 bytes, note "v428 baseline 1 Nov", uploaded from
  another team member's account at 04:19 IST) is active since 04:25 and is the Sprint 3 entry (`cambc submissions list
  --json` at 04:28). Its size is about bot_10's (cmb1 minus vx1). It is not overridden: no gate runs after 04:08, and
  the watcher `data/watch_subs.sh` only reads.
- **Sprint 3 lock (05:29 IST):** at 05:30 `cambc submissions list --json` shows active 1472 (321,687 bytes, note "Bamboo
  v458 + Spell"), `frozen` true and no upcoming tournament, so 1472 is the Sprint 3 bot, chosen by the merged team.
  Before it the team tried 1468 (v428 baseline, bot_10's size), 1469 (Bamboo G3, = `bots/bamboo8`), 1470 ("v484 bundle
  (ranked best)", 68,498 bytes) and 1471 (Bamboo v458); 1473 ("Bamboo v479 fixed") came after and is inactive.
- Local only from here: the bot_10 variant screen (rows b10n to b10d4, `tools/local/lscreen.py`).
- **User (recorded 04:36 IST):** "Now a team is merged ... Keep all test on local till i give out the next information for this.
  let them iterate on platform for some time. You dont do it until I say so." So no gates, uploads or platform tests
  from this side until the user says so; the merged team's other members iterate on the platform. (This also settles
  the rules caveat above: cheji bt and our team are now one team.)
- **Three bots now** (user, after 04:36: "One more member bamboo has uploaded his code ... I want the best of all
  worlds now"): vx1 (`bots/main`), bot_10 (`bots/pool/bot_10`; b10n with its log off) and bamboo8 (`bots/bamboo8`,
  branch `Bamboo8`, Bamboo Teahouse G3, platform v1469). Local results so far (rows bamboo8, cmb3, vx1fa, b10fa, cmb4):
  - Per size against the common pool (cand1, cp3, dh3): three a side vx1 60 of 72, bot_10 59, bamboo8 55; four a side
    vx1 87 of 96, bamboo8 82, bot_10 80; five a side bot_10 210 of 252, bamboo8 193, vx1 180. The pick rule (written
    before the games) gives cmb2's assignment: vx1 three and four a side, bot_10 five a side.
  - Head to head bamboo8 beats vx1 (83 of 140; four a side 20 of 32) and is level with bot_10 (71 of 140).
  - bamboo8's allocator in vx1 (vx1fa) cuts turns out of fuel from 1.16 to 0.47 a game with no loss; in bot_10 (b10fa)
    it fails the collected guard (97.8%).
  - The 15 bot_10 fix variants: none of the economy ones hits its target; b10hor and b10cap pass the screen (fight and
    item changes, for the platform); b10shot never acts.
  - cmb4 (vx1 three, bamboo8 four, bot_10 five a side, one program, `tools/variant/nsbot.py`) is on the local screen.
  Nothing of this is submitted: platform tests wait for the user.

## Update at 04:22 IST 11-01 (session 91): the Sprint 3 choice is the teammate's

The bot live at 05:29 IST (Sun 1 Nov) is the tournament bot. The user asked that the teammate (chejibt001) pick it, so
nothing below has been adopted: **main is still vx1**, live as version 1467 (76,154 bytes), which is also the Sprint 3
entry (`cambc submissions list --json` at 04:11). A read-only watcher (`data/watch_subs.sh`, log
`data/watch_subs.log`) records the active version and the Sprint 3 entry every 4 minutes until 05:20; it submits
nothing. No gate runs, and none may run before the lock: gates submit bots.

| Candidate | Folder | What it is | Local | Platform (three panels of teams above us, same session) |
|---|---|---|---|---|
| vx1 | `bots/main` | our bot, live as 1467 | pool screen 327 of 420 | b37 21 of 50, b32p 26 of 50, b36p 25 of 40, b33p 22 of 50: 94 of 190 |
| **cmb1** | `bots/pool/cmb1` | vx1 three a side; bot_10 (log off) four and five a side | pool screen 342 of 420; 85 of 140 head to head with vx1 | b37 28, b32p 29, b36p 28, b33p 22: **107 of 190**; passes its rule |
| cmb2 | `bots/pool/cmb2` | vx1 three and four a side; bot_10 (log off) five a side | pool screen 352 of 420 | cmb1's five-a-side games plus vx1's three and four a side (82 of 140 by count on the first three panels); passes too |
| bot_10 | `bots/pool/bot_10` | the teammate's bot as given (team cheji bt, ladder rank 51) | 87 of 140 head to head with vx1 | not gated by us; **its compact log is on** (`BOT_LOGC 1`, `src/common.h`) |

**cmb1 against its rule** (written 03:09, before any game; row cmb1): **passes.** Over the 140 paired games (whole game,
`pooled.py --round 2000`, `data/judge_cmb1_all.txt`): margin +62.4 +- 48.4, win share 0.51 to 0.61. In the 118 games
where our units diverged first (`whofirst.py`): 34 losses turned to wins, 21 wins to losses. Guards: no bot fault in 140
games; the 20 three-a-side games of b32p are identical to vx1's. It fights more: deaths +0.98 a game for us and +2.16
for the rivals, our gems lost on death 152 to 84, the rivals' collected -113 +- 57.

**A fourth panel** (row cmb1q, rule written 03:49): vx1 and then cmb1 on the three- and four-a-side panel b33p, 22 of
50 each. Over all four panels (190 paired games): margin +64.6 +- 40.3, win share 0.49 to 0.56 (+0.07 +- 0.04), flips
where our units diverged first 37 to 26.

**cmb1 or cmb2** (rules written 03:19 and 03:49, rows cmb2 and cmb1q): four a side over b32p and b33p (60 games) the
whole-game margin is +91.4 +- 88.4, at least 0, so the rule names cmb1. But four a side the wins are level (0.48 to
0.53, flips 10 to 9) and both sides die about 2-3 more times a game. cmb2 differs from cmb1 only four a side, so it is
the safer pick there; five a side is where bot_10 clearly helps.

The agent's recommendation, by the rules written before the results: **cmb1** (cmb2 if the teammate prefers vx1's
four-a-side game), if the rules question below is settled. Otherwise keep vx1, which is live now and needs no action.

Notes for the choice:
- Three a side bot_10 and vx1 are level (row cja), so cmb1 and cmb2 keep vx1 there.
- bot_10 runs out of fuel more often (about 8 events a game on the five-a-side panels against vx1's 6.7), mostly in
  rounds 1-3 and after 30. A turn that runs out resumes on the next turn, so it costs turns, not faults.
- Its weak maps locally (against 12 pool bots): 01boss-battle 7 of 24 (vx1 10), 01yellow-brick-road 14 (vx1 18).
- The teammate's own notes and 15 untested bot_10 fix variants are in `docs/bot_10.md` (`tools/variant/b10_ideas.py`).
- **Rules:** cheji bt is a separate team on the ladder (rank 51 at 02:34). If chejibt001 is still a member of that
  team, a bot that contains its code, submitted by our team, may break the competition's rules on teams and shared
  code. Check the rules, and that chejibt001 has left cheji bt, before submitting cmb1, cmb2 or bot_10.

To submit one (a version takes 1 to 11 minutes to compile; submit well before 05:29):

```
powershell -File tools/cambc.ps1 submit pool/cmb1        # or pool/cmb2, pool/bot_10, main
powershell -File tools/cambc.ps1 submissions list --json # active and upcomingTournament.submission must name it
```

Bundle sizes: vx1 76,154 bytes; cmb1 143,007. A version that fails to compile leaves the previous one active, so check
its status field. cmb1 was live twice tonight as a gate upload (1462 and 1464) and compiled both times.

## Update at 02:12 IST 11-01 (session 91): main reverted to vx1, the Sprint 3 submission

- **Confirmed at 02:11:** `cambc submissions list --json` shows active and selected 1456 (76,154 bytes, vx1), and the
  Sprint 3 entry names 1456. Ladder at 02:11: rank 71, 1962.7 (`data/ladder_1101_0212_p3.json`), from 65, 1991.4 at
  01:28 (fin1 was live in between). The gate runner `data/run_after12.sh` is stopped; no gate runs.
- **Repo (02:28):** one branch, `master` (default), at the current state; work and push there. The old working
  branch `batch-loop-2026-10-24` and `h3/cloud-1028` were merged and deleted. The unmerged `h2/cloud-1028` and
  `mic_mlmodels---ml` are kept as tags `archive/h2-cloud-1028` and `archive/mic-mlmodels-ml`. PR #4 is closed.
- **For later rules:** judge a change that acts late in the game (a wait, a give-up, a bank) over the whole game, not
  to r1000. Whole-game wins can be judged with `tools/replay/whofirst.py`: games the opponent played identically until
  our change acted carry no opponent-upload noise.

- **Main is vx1 again** (version 1456, uploaded 02:00 with `adopt.sh vx1r fin1`, a copy of `bots/pool/vx1`; source
  equal to main before fin1; bundle 76,154 bytes). The Sprint 3 entry names version 1456. fin1 is `bots/pool/fin1`.
- **Why:** fin1 passed its rule (to r1000) and the three- and four-a-side check fin1c by the letter, but over whole
  games it lost games vx1 won. On its five pinned panels (240 paired games) it is level to r1000 and behind over the
  whole game (margin -18.1 +- 12.4, win share 0.50 to 0.47). In the 84 games where fin1's units diverged first (the
  opponent had played identically until fin1 acted), 10 wins turned to losses and 2 losses to wins (p = 0.039); ten of
  the twelve are not on 02guardians, so lk1w's 25-turn altar wait made them. Rows fin1 and fin1c, `docs/findings.md`.
- **Before 05:29:** confirm with `cambc submissions list --json` that the active version is 1456 (76,154 bytes) and the
  Sprint 3 entry names it. A teammate's upload would replace it. `data/hold_gates` stays until after the lock.

## Update at 01:13 IST 11-01 (session 91): fin1 is main and the Sprint 3 submission (superseded at 02:00)

- **Main is fin1** (adopted 01:12 with `adopt.sh fin1 vx1`, version 1455; vx1 to `bots/pool/vx1`). Sprint 3 lock: Sun 1
  Nov 05:29 IST. `cambc submissions list --json` at 01:19: active and selected 1455 (bundle 76,941 bytes; vx1's was
  76,154), and the Sprint 3 entry names version 1455. fin1 = vx1 plus two banking fixes
  tested on 10-31: lk1w (in tribute range of an altar the bank walk gives up after 25 stalled turns, not 6) and gf2 (on
  02guardians the altar field leads to the dead guard's tile). Row fin1, `docs/lineage.md`.
- **How it was chosen** (no new ideas): of the changes not in main, only these two had a measured gain on their own
  targets against 10-30+ opponents and touched parts vx1 does not. Left out: s3p (sq34 contradicts it), op1 (inside the
  noise, same branch as vx1), ib1 (retest failed), sq75 (sqx: does not stack with vx1), dm0 (local only).
- **Result:** local screen 331 of 420 (vx1 327), no bot fault; worst maps locally 68 against 64 wins of 120. Platform,
  140 paired games to r1000 against vx1's runs on b30p, b31p and b36p (b36 pinned by hand as `b36p`): margin +0.60 +-
  9.55 (target up: met by the letter, level in fact), deaths +0.01, collected 101.3%, tributed 100.6%; short lock
  episodes with no tribute after 0.49 to 0.25 a game; win share 0.52 to 0.49 (recorded, not judged). fin2 (vx1 plus gf2
  only, the prepared fallback) was not gated.
- **Gating is over for Sprint 3.** `data/hold_gates` is in place and every line of `data/queue12.txt` starts with "#",
  so the runner `data/run_after12.sh` starts nothing; keep it that way until after 05:29.

## Update at 21:53 IST 10-31 (session 90)

- **Ladder at 21:33: rank 77, 1951.1** (`data/ladder_now.json`), down from 69 (1979.3) at 20:45. Main is vx1 (live as
  1428 between gates). Sprint 3 lock: Sun 1 Nov 05:29 IST.
- **Five a side collapsed after vx1 went live** (19:56): ranked five-a-side games 7 of 32 since then (vx1 itself 5 of
  18; the vx1-based gate variants 2 of 14), against 51 of 99 under bb2 from 13:30 to 19:56. Three and four a side, where
  vx1 plays as bb2, 10 of 18. In those five-a-side games our deaths were 6.47 a game against 5.08 under bb2 and our
  collected 798 against 932; every type of ours is worse. On the pinned panels b30p + b31p vx1 had matched bb2, so the
  check runs against today's neighbours: **row bb2r**, `main_b36@b36` (vx1) and `bb2r_b36@b36` (bb2) back to back on the
  fresh five-a-side panel b36 (the five teams that beat us after 19:56). Rule: keep vx1 only if it collects at least
  bb2's and dies at most 0.3 a game more; otherwise revert main to bb2.
- **qs1b** (bb2 plus spread when quiet five a side: a champion with no enemy seen for 40 rounds counts a joiner's share
  as n) won 344 of 420 locally (bb2 332), quiet maps 45 of 60 (36), their r1000 collection +5.0%, no fault. qs1 (the same
  on vx1) also 344. qs1b gates next: b35 (quiet panel) pinned from `bb2r_b35`, and b30p + b31p against bb2's runs.
- **mbk1 R** (21:51): the melee bag in contact did not move (12.5 against 12.5), deaths +0.42.
- **qs2b** (qs1b's quiet spread at every team size) is on the local screen.
- **Queue** (`data/queue12.txt`): bb2r:b36 (running), bb2r:b35p, qs1b:b35p, qs1b:b30p, qs1b:b31p, qs1:b35p, qs1:b30p,
  qs1:b31p, sq34:b32p, sq34:b33p. Done: `main_b35@b35` (vx1 on the quiet panel, 20 of 50; pinned as b35p at 21:55) and
  `main_b36@b36` (vx1, 25 of 40).


## Update at 21:05 IST 10-31 (session 90)

- **Main is vx1** (version 1420; live as 1428+, resubmitted after each gate). Ladder at 20:45: rank 69, 1979.3
  (`data/ladder_1031_2045.json`). Sprint 3 lock: Sun 1 Nov 05:29 IST; keep main submitted.
- **sq100 R** (20:39) and **sqx R** (20:59): spreading the other four types on top of vx1's farming Vesper met the
  collected bar (+2.3%) but raised our deaths 0.57 a game (empty-bag deaths in our own half). The spreading changes do
  not stack five a side; main stays vx1. sq75 alone (on bb2) had the best margin of the three (+43 against bb2's base).
- **Three and four a side** (46% of our ranked games): the fresh panels `b32` and `b33` (ranks 53-65, three- and
  four-pick maps only). `main_b32@b32` 26 of 50: the rivals collect 730 against our 643 by r1000 (tributed 599 against
  481) and every type of ours sits beside a teammate more. **sq34** (sq75's n^0.75 share three and four a side, Vesper
  included; five a side vx1) is queued on b32p; queue its b33p line after `main_b33@b33` runs and
  `python -I tools/platform/pin.py main_b33@b33` writes `specs_b33p.txt`. `bots/exp/vx34` (vx1's farming Vesper at
  every size) is built as a backup, untested, no row yet.
- **Queue** (`data/queue12.txt`): main:b33, mbk1 on b30p and b31p (row mbk1), sq34 on b32p (row sq34).
- **Disk** (20:48): C: from 2.7 to 14 GB free (old raw replays with complete decoded copies deleted; the rest
  compressed in place with `tools/local/compact_old.py`).

## Update at 20:06 IST 10-31 (session 90)

- **Main is vx1** (adopted 19:56, version 1420; bb2 to `bots/pool/bb2`): bb2 plus a farming Vesper five a side (her
  joiner's share counts n) with Capture of strength as her second emblem. Against bb2 on b30p + b31p (100 paired games):
  collected +3.7%, tributed +3.5%, our deaths -0.23, their deaths +0.80; the best of the nine bots decoded there (row
  vx1, `docs/lineage.md`). Ladder at 19:05: rank 72, 1966.8 (`data/ladder_1031_1905.json`). Sprint 3 lock: Sun 1 Nov
  05:29 IST; keep main submitted.
- **ve1r N** (19:10, by judgment): its +2% collected bar was met by 0.05 inside the noise of null variants, with Vesper's
  gems flat. vx1 (ve1r plus the Capture emblem) passed its own rule.
- **Gap** (`docs/findings.md`, "Where the collection gap sits, and what is level"): team captures are level; the rivals
  take more in the middle and our half, every type of theirs collects more, our champions sit beside teammates more,
  and our melee die carrying twice the gems (45 against 22 a game).
- **Queued** (`data/queue12.txt`; rules in the rows): sq75 (bb2-based, judged against bb2: share n^0.75 five a side;
  b30p 19 and b31p 28 of 50, decoding), then sq100 (on vx1: every type's share n five a side) and mbk1 (on vx1: melee
  bank smaller bags), each on b30p and b31p against vx1's runs. Gates take 8-13 min; the quota allows about 5 an hour.
- **Runner:** `data/run_after12.sh` (PID 16708) gates the lines of `data/queue12.txt` and decodes each run. Stop gating
  by about 04:30 and check that main is the active submission.

## Update at 18:41 IST 10-31 (session 90)

- **Main is bb2**, live as version 1407 (resubmitted by the lx1 gate at 18:39). Ladder at 17:40: rank 77, 1957.3
  (`data/ladder_1740_p4.json`). Sprint 3 lock: Sun 1 Nov 05:29 IST.
- **lk1w N** (17:59): the lock walk-off fix on our worst maps; zero-tribute guard-map games 17 of 40 as the base (01boss_battle
  unaffected), guards held, margin +20 +- 12.
- **lx1** (lock denial of any visible rival channel; row lx1): gated on b30p (18:13) and b31p (18:26); the locks fire
  (rival 50+ channels broken by our locks 0.02 to 0.12 a game on b30p) but the effect is small; judged when b31p is decoded.
- **The collection gap is Vesper** (`docs/findings.md`, "Channel denial, close losses and Vesper's farming"): their
  Vesper 152 gems by r600 against ours 91, her hits feed her own captures 60% against ours 40%. **ve1r** (Vesper scores
  shared groups with share n: she farms her own) gates on b30p from 18:39, then b31p; **vx1** (ve1r plus a Capture emblem
  as her second) is queued after it. Rules in the rows.
- **Runner:** `data/run_after12.sh` (PID 16708) gates the lines of `data/queue12.txt` and decodes each run.

## Update at 17:17 IST 10-31 (session 90)

- **Main is bb2**, live as version 1401 (resubmitted by the dc1 gate at 15:44). Ladder at 15:12: rank 74, 1961.4
  (`data/ladder_1512.json`). Sprint 3 lock: Sun 1 Nov 05:29 IST.
- **Verdicts:** eg1 **N** (close-out of a win in hand: median 46 to 38 rounds, -17% against -25%, and 5 wins in hand
  lost against 1), dc1 **N** (deny call in shared bytes 5-6: the rivals lost 1 of 13 games with a long winning
  channel against the bar of 3; the decisive channels ran out of every champion's sight). Both folders deleted.
- **Not a regression** (`docs/findings.md`, "Is the bot worse than when we reached 2045?"): v1287, live at the 2045.1
  reading on 10-30 18:54, is bb2 with the same 75,799-byte bundle as v1401; bb2 played 580 of our 600 ranked games
  since 10-30 18:40 and won 48%, gate variants 20. The rating fell while rank 40 rose 25 points: the field moved.
- **Tools:** `tools/replay/winchan.py` (long winning channels and how many were broken), `closeout.py`.
- **Runner:** `data/run_after12.sh` (PID 16708) waits for lines in `data/queue12.txt`.

## Update at 14:56 IST 10-31 (session 90)

- **Main is still bb2** (version 1393, resubmitted by the gf2 gate at 14:30). Ladder at 13:35: rank 71, 1965.4
  (`data/ladder_now.txt`); 2100 is about rank 33. Sprint 3 deadline: Sun 1 Nov 05:29 IST (v1391 was the selection
  shown at 13:58; whatever is submitted then enters the tournament).
- **Verdicts this session** (rows in `docs/experiments.md`): au19 (audit probe, never shipped: 20 caught errors in 140
  games, no turn-use bug), gf2 **N** (guarded-altar walk on 02guardians: tributed +10.9% against +15%, delay -24%
  against -33%).
- **New panel `wk` / `wkp`** (`results/panels/specs_wk.txt`, `specs_wkp.txt`): the 20 teams ranked 50-69 at 13:35 on
  our five worst maps (02guardians, 01boss_battle, 00lost_world, 01concentrated_wealth, 01yellow_brick_road), 100
  games; base `main_wk@wk` 33 of 100 (lost_world 5 of 20, the others 7 of 20).
- **Ranked picture** (our newest 100 ranked games, 50 won, decoded in `data/fights/rk1031`): to r1000 we are level
  with the rivals on average (collected 714 against 711, tributed 600 against 595, deaths 3.7 against 4.4). The
  losses split into 9 massacres (0 won, deaths 14.4 against 3.8, most of ours in our own half while fleeing) and 14
  mixed games (2 won); in the 74 even games we win 62% (`deathfactors.py rk1031`, `data/df_rk1031.txt`). Wins per
  map over 600 ranked games (`data/ourmaps_1031.txt`): worst 00lost_world 1/12, 00expanse 1/9, 00contest 1/7.
- **Close-out gap** (`tools/replay/closeout.py`, new): from the first round our tributed gems plus our bags reach
  1000 to the game end takes us 52 rounds (median) against the rivals' 28; we lost 6 of 53 such games (00rushbait_v2:
  924 tributed and 126 in four small bags, none enough alone; 00monolith: a 256-gem winning bag kept off two altars by
  enemy reach for 110 rounds). **eg1** (close out a win in hand, team bags included, through enemy reach) is in its
  local fault screen; its rule (panels b30p + b31p) is in its row.


## Update at 10:34 IST 10-31 (session 89)

- **Main is still bb2** (version 1379, resubmitted after the hx1 gate at 10:06). Ladder at 10:06: rank 68, 1975.2
  (`data/ladder_1006.jsonl`); 2100 is rank 33 now (Noobot 2099.7).
- **hx1 N** (help calls in the middle; row hx1): our deaths +0.02 +- 0.25 against the -0.3 target, guards held.
- **Fresh panels b30p and b31p** (`results/panels/README.md`): five-a-side maps, ten teams ranked 46-64 at 10:06, none in
  b26, b28 or b29, pinned to bb2's base runs `main_b30@b30` (23 of 50) and `main_b31@b31` (24 of 50). Against these teams
  deaths are level (b30 303 against 312, b31 233 against 268) and the gap is gems: on b30 we collect 737 against 842 by
  r1000, level at r150 (86 against 82), behind from r300 (190 against 201; r600 430 against 501). By group kind
  (`capkind.py`, b30 + b31, to r1000) they capture more pure gem-cluster groups (7.3 against 5.0 a game: 136 gems against
  101) and we more pure gold-cluster groups (8.7 against 7.7) with team gold level; they steal 1.33 of our kills a game
  (31 gems) and we 0.85 of theirs (17 gems; `steals.py`).
- **Local opening finding:** bb2 trails the old bots by r100 on 02treasure-box, 00lost-world, 01corridors, 01big-world,
  02cuts and 02fields; a bisect over the ladder bots (`data/local_bisect_open.log`) puts the drop at sq2 and tw13b, and a
  probe showed why: before r40 all five score groups as if alone, so after the first capture they walk together to one
  4-gem group after another, and at r40 they switch together to one far group. **op1** (the as-if-alone opening ends with
  the first group; row op1) passed its local screen (collected +2.4%, five a side +3.4%, deaths +0.07, 330 wins against
  332) and gates on b30p (from 10:32) and b31p; its rule (collected +3%, deaths at most +0.3, tributed 98%) is in the
  row. op0 (no as-if-alone opening at all) lost 24 local wins: not gated.
- **Runner:** `data/run_after12.sh` (PID 16708) is alive and gates the lines of `data/queue12.txt` (decodes run
  beside it). Disk: C: has 4.4 GB free; `data/summaries` holds 5 GB of match summaries cached on 10-30 (deletion needs the
  user's approval in this session).

## Update at 09:54 IST 10-31 (session 88; a handoff: a new session continues from here)

- **Main is still bb2.** Every gate resubmits it (version 1377 at 09:35); the base check `main:b28p` (09:43) submitted
  bb2 itself. Ladder: rank 61, 1992.8 at 09:28 (rank 65, 1979.4 at 08:07). 2100 is about rank 30-35 (rank 22 was 2192).
- **In flight:** `data/run_after12.sh` (PID 16708) started **hx1** on b28p at 09:53 (help calls into the middle; rule in
  its row). Nothing else is queued in `data/queue12.txt`, so after hx1 the runner waits for new lines. If the runner died
  with the old session: once hx1's games end, check that `data/chain_cands.log` ends with "Submitted bot version" after
  the hx1 gate; if not, run `powershell -File tools/cambc.ps1 submit main`. Then decode
  (`bash tools/replay/decode_run.sh hx1_b28p@b28p 6`), judge (`python -I tools/replay/pooled.py main_b28@b28
  hx1_b28p@b28p`) by hx1's row (target our deaths -0.3 a game; guards collected and tributed at least 98%), record it,
  and delete `bots/exp/hx1`. A passer goes to b29p against `main_b29@b29`.
- **hx1's games ended at 10:06 IST and the chain resubmitted main (version 1379).** Raw: 19 of 50, our gems 37523
  against 44853, deaths 320 against 204 (base 20, 37896 against 44571, 323 against 212), so our deaths fell by
  only 0.06 a game against the -0.3 target; the runner decodes it (`data/decode_hx1_b28p.log`) and the judge and
  the row are still to do. The queue is empty; the runner waits for new lines.
- **Verdicts since 09:08** (rows in `docs/experiments.md`): tv1 **N** (Tavi for Varg: tributed -4.7%, our deaths +1.12),
  sw2 **N** (collected -0.8%; guards held), fr1 **N** (focus calls within reach: collected -3.2%, the rivals' deaths
  -0.70, tributed 97.0%).
- **The base is exact:** bb2 on b28p at 09:43 repeated its 02:58 run on b28 game for game (20 of 50, gems 37896 against
  44571, deaths 323 against 212; `docs/findings.md`, "Pinned panels are deterministic"). None of the 13 variants gated
  on b28p since 03:17 (kb5 to fr1) passed: small behaviour, item and draft changes around bb2 no longer find gains on
  this panel.
- **Measured this morning** (`docs/findings.md`, "Top-20 drafts, carriers in contact and 00road_of_riches"): the top 20
  field Heart of Ruin, Marcella, Ryth, Vendetta, Vesper most (Ryth for our Varg; Ryth already failed three times: ry1,
  dq4, ry2); our carriers in contact with an enemy act as the rivals' do, so banking is not the gap; on
  00road_of_riches (1 win of 7) our champions die alone against two to four in the middle, most carrying 20-60 gems.
- **Suggested next steps:** (1) the ladder moved (we are rank 61; b28 and b29 were ranks 41-61 at 05:00): build fresh
  pinned panels of teams ranked just above us now, run bb2 once on each as the base, and test there; (2) aim at the
  measured five-a-side gap (gang-ups: our deaths with 3+ hitters 2.30 a game against 0.83) with new mechanisms rather
  than more doses of the tested ones; (3) local: bb2 wins 332 of 420 (`data/runs/multi-083529`); 36 of its 88 losses
  are quiet economy races (01big-world, 00expanse, 02harvest, 02geodes, 02cuts, 02famine, 02uncharted-lands), where the
  old bots collect faster from the opening (01big-world against cp3 at r600: 340 against 426).
- **Quota:** 50 match groups per rolling hour, 10 per gate (about 5 gates an hour). **Sprint 3 lock:** Sun 1 Nov 05:29
  IST: the bot submitted then is the tournament bot, so make sure main is submitted well before it.


## Update at 09:08 IST 10-31 (session 88; a handoff: a new session can continue from here)

- **Main is still bb2** (every gate resubmits it; version 1373 at 09:06). Ladder: rank 65, 1979.4 at 08:07.
- **Verdicts since 08:12** (rows in `docs/experiments.md`, all on b28p against `main_b28@b28`, 50 games to r1000):
  pp1 **N** (prey up to 8 tiles: the rivals' deaths -0.78, ours +0.46, tributed -7.1%), pp2 **N** (edge 0.05 when we
  outnumber: our deaths +0.64, theirs +0.06), pp3 not gated, ls1 **N** (trade in even fights: our deaths +0.52,
  tributed -7.8%), sw1 **N** (no chase out of reach while working a camp: collected -5.5%, camp-hit rounds -7.5).
  tv1 (Tavi for Varg) played 16 of 50 with our deaths up 49 (raw); its judge runs (`data/decode_tv1_b28p.log`).
- **Pattern:** 9 of the 10 variants judged since 05:01 score below bb2 on b28p (tributed -2.5% to -10%); behaviour in
  both directions (more fighting or less, chasing or staying) loses. bb2 sits at a local optimum against ranks 41-61;
  the measured gaps left are the draft's fight openings (`docs/findings.md`, "Fight openings against ranks 41-61") and
  the middle (we die there 67% more often per champion-round; deaths by region in `opendeaths.py`, scratch).
- **Running:** `data/run_after12.sh` (PID 16708; queue `data/queue12.txt`) gates **sw2** (keep working under threat
  below half health), **fr1** (focus calls answered within 4 tiles), **hx1** (help calls into the middle) on b28p, then
  waits for new lines. Rules in their rows; passers go to b29p against `main_b29@b29`.
- **Quota:** 50 match groups per rolling hour, 10 per gate: about 5 gates an hour; a gate plays in 4-10 minutes and its
  decode takes about 5 more.
- **Disk:** C: was full at 08:17 (287 MB); old `data/runs` folders were deleted (kept: `multi-083529`, bb2's local
  screen, and `multi-023931`). Check `df -h /c` before local runs; `data/summaries` (6 GB) and `data/fights` (3 GB) are
  the next candidates for cleanup.

## Update at 08:12 IST 10-31 (session 88)

- **Ladder:** rank 60, 1989.7 at 07:2x; rank 65, 1979.4 at 08:07 (`data/ladder_now_*.json`). 2100 is about rank 33.
  Main is still bb2 (every gate resubmits it; version 1361 at 07:54).
- **Verdicts since 05:01** (rows in `docs/experiments.md`): ci1 **N** (b29p deaths +2.02), ci2 **N** (ci1's draft on b28p,
  tributed -5.8%), op100 **N** (five together to r100: tributed -10.3%, deaths +0.56), ft7p **N** (higher engage bar: our
  deaths +0.16, theirs -0.28), rn1 **N** (Ren for Varg five a side: deaths -0.32 but collected 95.8%, tributed -3.3%).
- **New finding** (`docs/findings.md`, "How our champions die against ranks 41-61"): gang-ups of 3+ hitters carry the
  death gap (2.30 a game against 0.83); in outnumbered meetings our champions take about twice the hits the rivals' take
  from us, so the rivals press harder; bv1 and ft7p (less fighting) cut the rivals' deaths more than ours.
- **Running:** `data/run_after12.sh` (queue `data/queue12.txt`) gates the pressing family on b28p, each against
  `main_b28@b28`: **pp1** (prey up to 8 tiles when we outnumber around it; from 08:05), **pp2** (fight-simulation edge
  0.05 when we outnumber), **pp3** (both), **ls1** (no power-ratio retreat in even, healthy fights). Rules in their rows:
  factor kills, target the rivals' deaths +0.3, guards our deaths at most +0.3 and tributed 98%; passers go to b29p
  (stage 2, against `main_b29@b29`); among several passers the largest rise in the rivals' deaths is adopted.

## Update at 05:01 IST 10-31 (session 88)

- **Ladder at 04:34:** rank 67, 1967.9 (`data/ladder_now_*.json`); 2100 is rank 32-33. Main is still bb2 (every gate
  resubmits it).
- **Verdicts since 02:52** (rows in `docs/experiments.md`): sn5 **N** (b26p collected -3.9%), sd5 and dm0 **N** locally,
  kb5 **N** (b28p tributed +2.5% against +3%), kb5r **N** (b26p tributed -5.9%), mz1 **N** (b28p tributed -5.2%), bz1p
  and cz1 **N** locally against the pack testbed bz0 (`bots/exp/bz0`: main with every champion scoring groups as if
  alone, fights counted lost only above 1.3 times our power, help called with any number of enemies; main beats it 55 of
  84 on its maps).
- **New panels:** b29 (five a side, ranks 50-61 at 03:28): `main_b29@b29` 15 of 50, pinned as **b29p**; b28p (ranks
  41-49) documented in `results/panels/README.md`.
- **Where the five-a-side gap sits** (`docs/findings.md`, "Where the five-a-side gap sits against ranks 41-61"): half the
  tributed gap is bags lost to kills; camp work is level; our victims start contacts with fewer allies near and the
  rivals bring more champions during the contact; every one of our types dies 2-3 times as often as theirs.
- **Running:** `data/run_after12.sh` (queue `data/queue12.txt`): **ci1** (Cassi & Issac for Varg five a side, row ci1) on
  b29p. Its local screen (`data/runs/multi-045456`, 252 five-pick games, 4 minutes at 8 jobs): wins 186 to 172, collected
  +1.9%, deaths 2.80 to 4.56 (the pair dies together, 1.14 times a game each); no fault.
- **Local screens are fast:** 252 games take about 4 minutes at `--jobs 8`, so screen widely before gating.

## Update at 02:52 IST 10-31 (session 86)

- **The user's goals (stated between 02:41 and 02:51 IST):** ladder 2100 *and* 375 of 420 wins on the local screen (all 70 maps against cand1, cp3
  and dh3, both sides; bb2 has 332); the end goal is a bot that wins the tournament.
- **Local games replay exactly.** main's run `multi-023931` (02:39) gave bb2's 24 big-map games of 08:35 to the gem, so a
  variant is compared game by game with bb2's run `multi-083529` (scratch `lpair.py BASEDIR exp.bb2 NEWDIR exp.X`); a
  one-line change still flips about 50 games each way (chaos), so read collected and deaths by team size, not the win
  count alone.
- **Where bb2 loses locally:** 88 losses, 66 five a side; 61 are economy losses (deaths within 3; the old bots collect
  1047 a game to our 858 in them), 27 fight losses (our deaths 9.1 against 3.7).
- **Verdicts since 02:18:** tb1 N (three-a-side bags), mq3 N (three-a-side Marcella: deaths -0.42 but tributed -7.7%),
  wt1 and wt2 N (middle respawn waits; collected level locally), sn1 N locally (327 wins) but five a side collected +4.1%
  with level deaths, so **sn5** (sn1 five a side only) is gating on b26p from 02:51 (row sn5; adopt on a pass).
- **Running:** `data/run_after12.sh` (re-reads `data/queue12.txt`; stop it with `procs.sh` + `kill` when done), local
  screen of dm0 (no death marks in the pick).

## Update at 02:18 IST 10-31 (session 86; handoff, the session hit its usage limit)

- **Ladder read at 02:07:** rank 71, 1959.0 (`data/ladder_now.jsonl`). Main is still bb2 (every gate resubmits it).
- **Verdicts since 00:48** (rows in `docs/experiments.md`): vg1 **N** (b26p tributed -4.6% against bb2), vc1 **N** (b26p +
  b25p tributed -5.2%; Vesper's gold rose, the team's gems fell), hy1 **N** locally (deaths), bb3 **N** five a side (b26p
  tributed -12.2%, collected -10.1%: smaller bags hurt five a side), bb4 dropped, tb2 not gated. bb2's own gain over tw13b
  was three and four a side (`sizecond.py` on b19p-b21p), but bb3 three a side came out flat raw (b25p gems 31923
  against 32220): judge tb1 from `bb3_b25p@b25p` once `data/decode_bb3_b25p.log` is done.
- **Running:** `data/run_after12.sh` (queue `data/queue12.txt`) gates **mq3** (3-pick draft Heart, Vesper, Marcella;
  row mq3) on b25p from about 02:15, then waits for new queue lines: stop it with `tools/platform/procs.sh` and `kill`
  once mq3 is decoded. mq3's local fault screen writes `data/local_all70_mq3.log` (check its run with the scratch
  `ltypes.py`; a fault voids the gate).
- **Next:** judge mq3 by its row; on a pass adopt it in a gap (`touch data/hold_gates`, wait for no `gatechain`,
  `bash tools/platform/adopt.sh mq3 bb2`, `rm data/hold_gates`). Panel b27 (four a side, ranks 40-45) is written but has
  no base run (`main:b27`); the rivals' four-a-side drafts match ours. Five a side the rivals field Ryth in 82 of 132
  games where we field Varg (ry1 and ry2 were rejected earlier).
- **Disk:** C: was full at 01:36 and local screens lost games; old `data/runs` folders were deleted. Check `df -h /c`
  before a local run.

## Update at 00:48 IST 10-31 (session 86; a handoff: a new session can continue from here)

- **Ladder read between 00:38 and 00:42:** rank 68, 1967.3 (bb2 keeps losing rating: 2045 at 18:54, 1983 at 23:45).
- **Pinned panels replay exactly.** `main_b24p@b24p` (00:21) and `main_b25p@b25p` (00:32) gave bb2's games of 20:16 and
  21:03 to the last gem, so a fresh base on a pinned panel is never needed. b22p, b23p and b24p mix three-, four- and
  five-a-side maps (`data/map_sizes.json`, three 5-pick maps added: 00ribs, 02crossing, adgato_gemcombat5).
- **`tools/replay/sizecond.py`** rebuilds a size-conditional variant's games from two runs without a gate. vp3's Vesper
  build helps only five a side (82 games: tributed +4.3%, deaths -0.43 +- 0.29); three and four a side it does nothing or
  harm. vp3c (that build five a side only) failed its rule on the mixed panels (b22p + b24p tributed +2.56%, bar +3%).
- **Running:** `data/run_after11.sh` with `data/queue11.txt`: `vp3c_b26p@b26p` (row vp3c6, on the new five-a-side panel
  b26, pinned to `main_b26@b26`, bb2 19 of 50), then `vg1_b26p@b26p` (row vg1). Judge vp3c6 by its row as soon as its
  decode is in (`pooled.py main_b26@b26 vp3c_b26p@b26p`); on a pass adopt vp3c at once in a gap (`touch data/hold_gates`,
  wait for no `gatechain`, `bash tools/platform/adopt.sh vp3c bb2`, `rm data/hold_gates`), then judge vg1 against
  `vp3c_b26p@b26p`.

## Update at 00:04 IST 10-31 (session 86; superseded above where they differ)

- **Ladder at 23:45:** rank 64, 1982.7 (`data/ladder_now*.json`). Main is still bb2 (resubmitted after every gate).
- **Verdicts since 23:11:** hd1 N, vp3r N (r600 farming -0.8% against +3%; rows). vp3 five a side looked better on all
  three panels (win share 0.37 against 0.27 over 150 games, tributed +3.9%) and worse three a side (12 against 17 on b25p),
  against bases from 19:00-21:00.
- **Candidate: vp4c** (`bots/exp/vp4c`): vp4's shooter build (Jungle of the main stat after Treasure, no Power) five a
  side only; three and four a side it builds as bb2. Local screen passes (`multi-235644`, no fault). Its rule (row vp4c)
  judges it from vp4's five-a-side run against a fresh bb2 base: `vp4_b24p@b24p` against `main_b24p@b24p`, tributed +3%,
  deaths at most +0.2, collected at least 99%; then confirmed pooled with the b22p pair (`vp4_b22p`, `main_b22p`). vp4
  itself has an adoption rule against the fresh bases on b24p + b25p (row vp4); if vp4 passes outright, adopt vp4.
- **Runner:** `data/run_after11.sh` (started 23:43, background) gates vp4 on b24p (done 23:57: 20 of 50, deaths 270 against
  vp3's 273 and bb2's 307) and b25p (from 00:11), then the lines of `data/queue11.txt` (`main:b24p`, `main:b25p`,
  `main:b22p`, then `#exp/vp4c:b22p` and `#exp/vp3c:b22p`: remove the `#` of the one vp4's rule picks; the file is re-read
  before each gate), decoding each in the background. The quota (50 groups a rolling hour, 10 a gate) holds each gate
  until 40 or fewer are used: about one gate every 12 minutes.
- **vp3c** (`bots/exp/vp3c`, row vp3c): vp3's build five a side only; local screen passes (`multi-000617`). vp4's own
  rule picks between vp3c and vp4c (vp4 on b24p: Vesper's deaths 1.00 to 1.04 against vp3's, her damage 4223 to 3603).
- **Adopting in a gap:** `touch data/hold_gates` (the runner then starts no new gate), wait until `procs.sh` shows no
  `gatechain`, run `bash tools/platform/adopt.sh vp4c bb2`, then `rm data/hold_gates`. After the adoption a `main:` line
  in the queue would play vp4c, not bb2: replace `main:b22p` by a copy of bb2 (`cp -r bots/pool/bb2 bots/exp/bb2r`,
  line `exp/bb2r:b22p`) before it is due.

## Session 87 (from 23:14 IST 10-30)

- **Ladder at 23:15:** rank 60, 1986.9 (`data/ladder_2318_p*.json`; 2100 is rank 30-31). The user's goal: 2100 by 02:00
  IST 10-31. About 15 ranked sets (5 games each) remain before then; reaching it needs about 14 of them won, while bb2
  wins 50% of ranked games (200 of the 400 since 10:00 IST: three a side 36 of 75, four 64 of 102, five 100 of 223;
  `data/ranked_2320*.json`). The rating fell 21.8 from 22:14 to 23:15 with 2 of 6 sets won.
- **Plan:** the runners of the 23:11 handoff keep going (hd1 b23p, then vp3r on b24p and b25p, then vc1). Judge each by
  its row as soon as its decode is done, and adopt a pass at once in a gap between gates, so it plays the most ranked sets.

## Handoff at 23:11 IST 10-30 (session 86 ends here on the user's request; a new session continues from this section)

- **Main is bb2** (resubmitted by every gate; v1319 at 22:56). **Ladder at 22:14:** rank 52, 2008.6
  (`data/ladder_now_*.json`). Sprint 3 lock: Sun 1 Nov 05:29 IST. The user's goal: 2100.
- **Judged since 21:56** (rows in `docs/experiments.md`): vp1 **N** (Vesper damage -11%, deaths +0.37), vp2 not gated,
  mgc1 **N** (middle cluster gems +16% against +30%, deaths +0.74), vp3 **N** on its rule (Vesper damage -6.6%, her
  deaths +0.16 against +0.15) but the best lead of the night: 34 of 100 won against bb2's 27, collected by r600 +3.8%,
  tributed to r1000 +2.2%. Folders vp1, vp2, mgc1 deleted; `bots/exp/vp3` kept for vp3r.
- **Running** (check `bash tools/platform/procs.sh`; never start a second chain; do not edit a running runner script):
  1. `data/run_after8.sh`: hd1 on b22p (gating since 23:04) then b23p; decodes in the background.
  2. `data/run_after10.sh`: after (1), vp3 on b24p and b25p (row **vp3r**), then vc1 on b22p and b23p (row **vc1**).
     `data/run_after9.sh` was stopped before it gated anything (replaced by run_after10).
  3. A gate submits the variant it tests. If these runners died with the old session (none listed by `procs.sh`), first
     make sure main (bb2) is the submitted bot (the last line of `data/chain_cands.log` should be a resubmit of main;
     else resubmit main as `gateq.sh` does), then restart the missing gates with one new runner like `run_after10.sh`
     (`run_pipe3.sh` skips decodes already done; drop a gate already in `results/gate.log`).
- **How to judge** (rules are in the rows, written before the games):
  - hd1: `decoded.py types data/fights/hd1_b22p_b22p data/fights/hd1_b23p_b23p` (Heart of Ruin deaths down 0.2 from
    1.48; its champion damage at least 2359) and `pooled.py bb2_b22@b22 hd1_b22p@b22p bb2_b23@b23 hd1_b23p@b23p`
    (our deaths at most +0.1; collected and tributed at least 98%). Locally its Heart damage fell 30%: watch that guard.
  - vp3r: `decoded.py gems --round 600 data/fights/vp3_b24p_b24p data/fights/vp3_b25p_b25p` (collected by r600 at least
    370 against 359) and `pooled.py bb2_b24@b24 vp3_b24p@b24p bb2_b25@b25 vp3_b25p@b25p` (deaths at most +0.2; collected
    and tributed at least 99%). **If it passes, adopt at once** in a gap between gates: `bash tools/platform/adopt.sh vp3
    bb2` (it refuses while a gate runs), then update `docs/lineage.md` and this file, and check main is live.
  - vc1: `decoded.py champs` on vc1's two runs (Vesper camp gold by r600 at least 796 against 637), `waste.py 600` (team
    gold from captures at least 1890), `pooled.py` guards (deaths at most +0.2; collected and tributed at least 98%).
    Its local screen had deaths +21%, so its deaths guard is at risk.
- **Next levers** (`docs/findings.md`, "Where the time and the deaths go"):
  1. If vp3 is adopted: keep Vesper's health while she gains strength (the band's Vesper: Bruiser of strength, 2120 max
     health), for example Bruiser of strength in place of Power for a shooter, and pair it with vc1's gold if vc1 holds.
  2. Travel waste: per capture we walk 33.7 rounds with no enemy within 6 against the band's 25.8
     (`tools/replay/capcycle.py`). Find the cause locally first (target switches, walks to groups a teammate captures,
     bank detours) with the bot's own `A` and `R` log lines.
  3. Out-of-reach drift near enemies (`tools/replay/stateact.py`): ours move level or idle in a third of the rounds with
     enemies within 6, the band in a fifth; the death gap is there already by r300.
- Uncommitted on purpose: never add `alk_home();,+40p` or `image.png`.

## Update at 21:56 IST 10-30 (session 86; a handoff: a new session can continue from here)

- **Main is bb2.** Rejected since 21:23: s3p (collected +3.1% against +5%), d3m (their deaths minus ours +2.18 a game,
  far past its bar, but collected 94.2% and tributed 92.3% against 97%: Marcella wins three-a-side fights and farms
  slower than Vendetta; a lead if the farming loss can be removed).
- **Running** (check `bash tools/platform/procs.sh`; one chain at a time):
  1. `data/run_after5.sh`: vp1 on b22p (done, 11 of 50, bb2 12) and b23p (gating since 21:52). Judge by row vp1
     (`decoded.py types` for Vesper's damage, `pooled.py bb2_b22@b22 vp1_b22p@b22p bb2_b23@b23 vp1_b23p@b23p`).
     vp2 (milder) is gated only if vp1 passes its damage target and fails only the deaths guard.
  2. `data/run_after6.sh`: then mgc1 on b22p and b23p (row mgc1: cluster-only groups skip the death discounts;
     target: middle cluster-only gems by r600 +30%, `tools/replay/gclass.py 600 0`).
- **Measured tonight** (findings and rows): five a side the band takes 3.7 middle gem-cluster groups by r600 to our 1.0;
  our Heart of Ruin dies within 10 rounds after 9% of its engaging dashes at 80%+ health, theirs after 1% (same counts,
  targets and numbers); fights are started on our champions 1.7 times as often and we hit back less (`decoded.py defend`).

## Update at 21:23 IST 10-30 (session 86; a handoff: a new session can continue from here)

- **Main is bb2** (resubmitted after every gate). **Ladder at 20:52:** rank 53, 2009.3 (`data/ladder_1030d.jsonl`;
  rank 30 is 2111.9, rank 40 2067.4); the user reported 2000 a little later. Last 30 ranked games: 14 won.
- **Rejected:** ib1r (deaths +0.16 on b24p), hb1 (deaths -0.16 against -0.3; tributed 97.9%). ib2 and ib3 not gated.
- **Running** (check `bash tools/platform/procs.sh`; one chain at a time):
  1. `data/run_after4.sh`: base `bb2_b25@b25` on the three-pick panel b25 (gating since 21:04), pin as b25p, then s3p
     and d3m on b25p. Judge each by its row (`pooled.py bb2_b25@b25 s3p_b25p@b25p`, and d3m the same).
  2. `data/run_after5.sh`: when (1) is done, vp1 on b22p and b23p (row vp1; base `bb2_b22@b22`, `bb2_b23@b23`).
- **New lever, vp1** (findings, "Our Vesper buys health"): our Vesper's lone basic hit stays at a median of 70 from r0 to
  r600 while the band's goes 65 to 112 (b22 + b23, `tools/replay/perhit.py`), because after Treasure she buys Jungle of
  health and Durability. vp1 gives a shooter Jungle of strength and no Durability. Target: her champion damage +15%.
- **Against the band by team size** (bb2 on b22-b24): three a side 1 of 28 won, four a side 21 of 40, five a side 19 of
  82. Five a side the rounds spent in each local state (enemies and allies within 6, health) match theirs, yet we die
  about twice as often in each.

## Update at 20:26 IST 10-30 (session 86; a handoff: a new session can continue from here)

- **Main is bb2** (v1297 live at 20:16). hg2 **N** (stopped after b22p: collected -10%, deaths +0.38).
- **Running** (check `bash tools/platform/procs.sh`; one chain at a time):
  1. `data/run_after2.sh`: base `bb2_b24@b24` done (14 of 50; pinned as b24p), now ib1 on b24p (started 20:22).
  2. `data/run_after3.sh`: when (1) is done, applies row ib1r's rule (`data/judge_ib1r.txt`). Pass: runs
     `adopt.sh ib1 bb2` at once (no gate runs then) and gates ib3 on b22p and b23p (base ib1's runs). Fail: gates hb1
     there (base bb2's runs). Then s3p on b22p and b23p. Judge ib3 / hb1 / s3p by hand by their rows.
  After an adoption: update `docs/lineage.md`, this file and the ib1r row; check `submissions list` shows main live.
- **Ruled out tonight** (findings): our gold is not idle (unspent lower than theirs; item value 9% lower from income);
  focus fire is level; assist and join-when-ahead were already rejected (as1, ja1); Varg swaps rejected five times.

## Update at 20:09 IST 10-30 (session 86; a handoff: a new session can continue from here)

- **Main is bb2** (resubmitted after every gate). **Ladder at 19:40:** rank 49, 2011.8 (ladder `data/ladder_1030c.jsonl`);
  2100 is about rank 33. Last 40 ranked games: 16 won; 8 losses had 9-24 of our deaths (gold snowballs, findings).
- **Rejected:** ib1 on its rule (collected +2.3% against +3%; but deaths -0.48 ± 0.22 a game, five a side -0.8 to -0.9,
  tributed +3.6%), gw10 (gems per camp damage +10% to r600, collected +0.1% to r1000). ib2 not gated (needed ib1).
- **Queued** (check `bash tools/platform/procs.sh`; one chain at a time):
  1. `data/run_after_hg2.sh`: hg2 on b22p (11 of 50, decoding), then b23p.
  2. `data/run_after2.sh` (started with `NEWP=b24 GATES="exp/ib1:b24p exp/s3p:b22p exp/s3p:b23p"`): base `bb2_b24@b24`
     on the new panel b24 (jazz, BattleCats, SkuBap, estrogen :3, Nameless; ranks 30-44, all above us), pin as b24p,
     then ib1 on b24p (row ib1r: judged on deaths, target -0.3 a game), then s3p on b22p and b23p.
- **Ready:** ib3 (ib1 + Treasure of health for melee types; local screen passes), gated only if ib1r passes and ib1 is
  adopted (`bash tools/platform/adopt.sh ib1 bb2` in a gap between gates).
- **Measured five a side** (findings): own-half captures level, middle 6.8 against 13.1 a game; same time budget except
  dead rounds (7.8% against 4.7%); in the same local situation we die 2-2.8 times as often; they start 36 fights a game
  to our 22 and stun us about four times as often.

## Update at 19:13 IST 10-30 (session 86; a handoff: a new session can continue from here)

- **Main is bb2** (resubmitted after every gate). **Ladder:** rank 42, 2045.1 at 18:54 (17:46: rank 51, 2014.3). The
  user's target is 2100.
- **Panels: only teams rated above us** (the user's rule of 17:50, restated in the session). `b22p` (base `bb2_b22@b22`, 12 of 50) and the
  new `b23p` (new team(4), :3, ひななー, SALUTE TO TUNG, 剑桥夜爬者; base `bb2_b23@b23`, 15 of 50). b19p and b20p now hold
  teams at or below our rating (Sheeesh---, SquidProxyLovers, test4, HBH): no longer used.
- **Rejected:** dn1 (giant-bag games 12 against 12), cy1 (Prism carry; local screen 145 of 420 wins against 332).
- **Running** (check `bash tools/platform/procs.sh`): `data/run_pipe3.sh` (task started 19:08) gates ib1 and gw10 on
  b22p then b23p and decodes each run; `data/run_after_hg2.sh` then gates hg2 the same way. Rules are in the rows; judge
  by hand with `pooled.py bb2_b22@b22 X_b22p@b22p bb2_b23@b23 X_b23p@b23p` and the scratch readers named in the rows
  (`waste.py`, `early2.py`; copies in `results/analysis/` once used for a verdict).
- **Measured against the band above us** (b22 + b23 base, 100 games): we collect 596 to r1000 against 791 and win 27%;
  even with level deaths by r300 we won 5 of 31. To r600 they deal 4% more camp damage and take 16% more gems per
  damage (gold per damage level); their builds are Bruiser and Jungle of the main stat; our deaths in r100-300 are 1.12
  a game against 0.69.


## Update at 18:12 IST 10-30 (session 86; a handoff: a new session can continue from here)

- **Main is bb2** (resubmitted after every gate; version 1283 at 17:49). **Ladder at 17:46:** rank 51, 2014.3. The
  user's target is 2100 (rank 30-31). Measured gap: ranked since 10:00 we won 45% against teams rated 2000-2050 and 1 of
  5 above 2050; on the new panel b22 (ranks 20-39) bb2 won 12 of 50 (findings, "Hoarders and giant channels").
- **The user's rule (17:50): test only against teams better than us.** New panel `b22` (procless, Let's LARP again,
  Jupiter, Rogue Lock Pickers, 0xDEADBEEF; 2066-2162), pinned as `b22p` to `bb2_b22@b22`, which is its exact base.
  b19p and b20p keep 4 of 5 teams above us; b21p has two below (1988-1990), so new candidates gate on b20p, b22p, b19p
  (`data/run_pipe2.sh`, panels and bases as parameters).
- **pz1 N** (17:18-17:49; collected -3.7%): our Prism banks and stays weak. SilverSamurai's Prism hoards instead.
- **Running:** `data/run_pipe2.sh dn1` (task started 18:08 with `PANELS="b20p b22p b19p"`, `BASE="bb2_b20p@b20p
  bb2_b22@b22 bb2_b19p@b19p"`): dn1 denies giant channels (row dn1: altar watch after seeing a hoarder, lock bought then,
  locks and stuns on channels of 800+ total or 300+ gems). It writes `data/judge_dn1.txt`.
- **Next:** judge dn1 by its row. Where the band above us beats us: massacres (a fifth of b22's games) and economy in
  the even games (10 of 31 won); procless out-fights us at every count.

## Update at 17:19 IST 10-30 (session 86)

- **Main is bb2** (resubmitted after every gate; version 1277 at 16:37). **Ladder at 17:19:** rank 53, 2007.9 (16:08:
  rank 59, 1989.8; 13:28: rank 73, 1947.8). The user's target is 2100 (about rank 31 at 16:08).
- **Rejected since 15:23:** bv1, ow1, rh1 on the platform (all raised or kept our deaths; leaving does not save
  champions), bv2 and ow2-ow5 not gated (descendants of those), og1 locally (gem groups on the way: collection level,
  deaths +28%). Rows in `docs/experiments.md`; findings section "Leaving does not save champions; five a side and twelve
  bad maps".
- **Running:** `data/run_pipe.sh pz1` (task started 17:08 with BASE = bb2's pinned runs): pz1 is Prism for Varg as the
  fifth pick on 5-pick maps (row pz1: collected +2% pooled, guards deaths +0.3 and tributed 98%). It gates b19p, b20p,
  b21p one at a time in the :x1-:x2 windows, then writes `data/judge_pz1.txt`. Check `bash tools/platform/procs.sh`.
- **Where the gaps are now** (findings): five a side we win 37-45% (smaller teams 53-64%) and trail on gem-cluster gems
  (by r600 134 against 188 a game); twelve maps hold 21 wins in 119 ranked games (00ribs and 01boss_battle: we tribute
  nothing in our losses; 00split: golem groups; 01starvation and adgato_gemcombat5: massacres).
- **Machine:** free commit memory runs near 3 GB with the user's other programs open; Git Bash forks fail below that
  (errno 13) and a decode failed with "paging file too small" (rh1_b21p kept 19 of 50 games). Run local screens with
  4-6 jobs and not beside a decode.

## Update at 15:23 IST 10-30 (session 86)

- **Main is bb2** (version 1217, resubmitted after every gate). **Ladder at 15:10:** rank 61, 1984.4 (13:28: rank 73,
  1947.8). The user's target is 2100 (rank 40 was about 2055 at 13:28).
- **Rejected today since 11:20:** ms1, vw2, dr0p, ww2p, cs1 on the platform; jm1 on its local screen. Rows in
  `docs/experiments.md`.
- **Test bots no longer play ranked sets.** Since 13:51 `tools/platform/gateq.sh` uploads a test bot only from :x1:00 to
  :x2:59 (ranked sets start at :x0:05 and last about a minute); before that 23 of 80 sets were played by the bot under test.
- **The whole economy gap sits in the games where we die fast** (`docs/findings.md`, session 86 section): on bb2's 150
  pinned games, the 37 where our deaths reach 3 + one per 100 rounds after r200 were won 7 times (deaths 11.1 against 5.9,
  collected 472 against 852); in the other 113 we won 58 with collection level (830 against 827). In those games the
  rivals travel in threes and win fights at any count. The ow family acts there: ow1 (under that trigger, leave when
  outnumbered in view), ow2 (ow1 plus target avoidance), ow3 (ow2 plus leaving a lone enemy when we are one or two), ow4
  (ow3 with an earlier trigger, 2 + one per 100 rounds after r100). bv1 (enemy-ball avoidance) is the older attempt.
- **Running (one gate at a time, each in the :x1-:x2 window):**
  - `data/run_after4.sh` (task bj0lf9x1q) runs `run_pipe.sh bv1 ow1 bv2 rh1` against bb2's pinned runs: bv1 gated
    14:49-15:11 (its judge decodes now), ow1 gates from 15:21; bv2 and rh1 are parked (`bots/exp/bv2_hold`,
    `bots/exp/rh1_hold`, rows bv2 and rh1), so it skips them, then waits for its judges and exits.
  - `data/run_after7.sh` (task bzwwisguo) waits for ow1's last gate, then runs `run_pipe.sh ow3 ow2` (ow2 is parked, so
    this pipe gates ow3 only).
  - `data/run_after8.sh` (task brgypzssa, started 15:24) waits for ow3's last gate (plus a minute, so the ow3 pipe skips
    the parked `bots/exp/ow2_hold`), restores ow2 and runs `run_pipe.sh ow4 ow2`. ow4 passed its local screen at 15:24
    (deaths 997, the lowest of the family).
- **Next:** judge bv1, ow1, ow3, ow2 by their rows (`data/judge_NAME.txt`; for the ow family also run scratch
  `caution.py` on base and new runs for the mechanism). Adopt a pass with `bash tools/platform/adopt.sh NAME bb2` between
  gates (stop the runners first), then restart the queued runners with `BASE=` the new main's judge runs and amend the
  queued rows before any of their games. If two ow variants pass, adopt the one with the larger deaths cut whose guards
  hold.

## Update at 11:20 IST 10-30 (session 86; a handoff: a new session can continue from here)

- **Main is bb2** (version 1217, adopted 10:01). Each gate resubmits main when it ends; the last chain resubmitted it as
  version 1229 at 11:08. **Ladder at 11:05:** rank 62, 1979.1 (10:23: rank 57, 1992.1; the dip came while the test bots
  bb15 and lv15 were live during their gates). Target 2050 (rank 40 was 2054.7).
- **bb15 N** (bags at factor 1.5): tributed -5.7%, collected 95.8%, our deaths +0.33 (row bb15). **vw1 N locally**
  (Vesper keeps her captures, shards counted half: deaths 1129 against the bar 1125).
- **Running:** `data/run_cands2.sh` (task started 10:03 with BASE = bb2's pinned runs) is decoding lv15 (raw 20, 22, 22 of 50
  against bb2's 20, 21, 24); it writes `data/judge_lv15.txt`, then finds the other names parked and exits. The parked
  folders are `bots/exp/ww2p_hold`, `ms1_hold`, `rh1_hold`, `dr0p_hold` (renamed at 11:03 to reorder the queue).
- **Next, once that runner has exited** (check `bash tools/platform/procs.sh`):
  1. Judge lv15 by its row's rule (collected +2%; guards deaths +0.3, tributed 98%); record it; delete or adopt
     (`bash tools/platform/adopt.sh lv15 bb2`, then rebuild the queued candidates on the new main and amend their rows).
  2. Rename the parked folders back (`mv bots/exp/ms1_hold bots/exp/ms1`, and so on).
  3. Start one runner in the background: `BASE="bb2_b19p@b19p bb2_b20p@b20p bb2_b21p@b21p" bash data/run_cands2.sh ms1 vw2
     dr0p ww2p rh1` (BASE changes if lv15 is adopted: its judge runs become the pinned bases).
- **vw2** (Vesper's shards count three quarters in the capture claims) passed its local screen and is queued after ms1.
  Its cause, and today's other measures, are in `docs/findings.md`, "The rivals' Vesper farms, ours hands her groups
  over": the largest gap by champion type is the Vesper (296 gems a game against our 164), our Vesper hands 3.7 of the
  groups she clears to teammates by r600 (`tools/replay/handoffs.py`); 20 of 150 games are massacres, none won.
- **Local screens:** read collected and lost on death without 01boss-battle (one game there can collect 16,590 gems).
  Check that the summary shows 420 games: at 10:50 the disk was full and a screen silently lost 48 games
  (`docs/WORKFLOW.md`, local quirks); 12 GB were freed at 11:02.

## Update at 10:03 IST 10-30 (session 86)

- **Main is bb2** (tw13b with tribute bags about 18% smaller: the bank batch's trip-cost factor 2.0 in `bot.cpp`), adopted
  at 10:01 as version 1217; tw13b is `bots/pool/tw13b`. Over b19p, b20p and b21p against tw13b's pinned runs (150 games, to
  r1000): tributed +3.0%, collected +1.7%, our deaths -0.35, lost on death -10 a game, win share 0.39 to 0.43. Its judge runs
  are main's pinned bases now: `bb2_b19p@b19p`, `bb2_b20p@b20p`, `bb2_b21p@b21p`.
- **Ladder at 09:27:** rank 59, rating 1981.0.
- **Running since 10:03:** `data/run_cands2.sh` (once, in the background, BASE = bb2's runs): bb15, lv15, ww2p, ms1, rh1, dr0p in
  that order, three gates each, judges in `data/judge_NAME.txt`; rules in the rows (amended at 10:02, before any game: all
  rebuilt on bb2). bb15 is the next bag dose (factor 1.5); lv15 counts gold 0.15 gem from r300 (pure gem-cluster groups:
  we capture 6.0 a game, the rivals 11.9, `tools/replay/capkind.py`).
- **To adopt between gates:** stop the runner while no gate runs (TaskStop, then `kill` its bash process, which survives),
  adopt, and restart the runner with the remaining names; `adopt.sh` refuses while a gate runs.


## Update at 09:11 IST 10-30 (session 86)

- **Ladder at 09:01:** rank 64, rating 1966.6 (08:23: 68, 1953.5).
- **tw16q N** (`TRAVEL_W` 1.6): collected +0.0%, our deaths +0.31. **rd1 N** on its local screen (raids on the enemy half
  only near fresh sightings: deaths +30%).
- **Platform queue** (one runner at a time; each gate resubmits main when it ends):
  - `data/run_cands.sh bb2 rd1 dr0p` (started 08:46; rd1 skipped): bb2 (smaller tribute bags, factor tributed), then dr0p
    (no recent-death discount on contested groups, factor collected). bb2 on b19p: 20 of 50, gems +4.4% (raw).
  - `data/run_after.sh ww2p ms1` waits for it, then runs `run_cands.sh ww2p ms1`: ww2p (middle respawn waits count
    twice) and ms1 (Monster emblem in the shop formula; local screen running, its folder is deleted if it fails).
  - Rules are in the rows; judges land in `data/judge_NAME.txt`.
- **New measures** (main's 150 pinned games, to r1000): champions idle by dead middle groups 108 champion-rounds a game
  against the rivals' 53 (`tools/replay/waits.py`); camp hits take 19.4 champion-rounds per group killed against 17.1, and
  the rivals carry Monster emblems (Vesper 0.50 at r600), we none; our home visits 35.1 a game against 41.8 (shop trips are
  not the gap); fuel exhaustion after round 30 about 1 a game.


## Update at 08:30 IST 10-30 (session 86)

- **Ladder at 08:23:** rank 68, rating 1953.5 (06:48: 62, 1974.3). Rank 50 is 2011.0, rank 40 2056.6. Main is tw13b; each
  chain ends by resubmitting it (version 1204 at 08:03).
- **N on the platform:** lv3t (collected +1.7%, bar +2%; the rivals gained more) and ry2 (our deaths +0.17, target -0.3;
  their deaths -0.33, guard -0.3). Ryth raised the stuns we land from 7.7 to 12.5 a game and saved none of our champions.
- **Where the gem gap is** (main's 150 pinned games, to r1000, `decoded.py captures`, `lives`): captures 40.3 against
  46.1 a game. Our half level (391 gems against their 382 on theirs); middle 224 against 276; raids 37 against 62. The
  rivals hit 4.8 of our home groups first a game (median 25 rounds after the group comes up), we hit 2.3 of theirs. Our
  capturer's cycle is 85.5 rounds against 70.7, the hop 13.3 tiles against 12.2.
- **Local screens:** three bars of about one run's spread each reject about half of neutral changes, and local results
  have not predicted platform ones. tw16p (`TRAVEL_W` 1.6) failed its screen by 3 gems of 1078, so it now goes to the
  platform as tw16q under a rule written first. New local screens use bars of about two run spreads (wins at least main -
  24, deaths at most main x 1.10, collected at least main x 0.95), written before the run.
- **Running since 08:30:** `data/run_w8.sh` (once, in the background): tw16q on b19p, b20p, b21p; writes
  `data/judge_tw16q.txt` (rule in row tw16q).


## Update at 06:59 IST 10-30 (session 86)

- **Ladder at 06:48:** rank 62, rating 1974.3 (05:26: 69, 1946.3); tw13b on the ladder since 06:26 (version 1190, resubmitted
  as 1192 by the w5 chain).
- **tw13b confirmed on the fresh panel b21** (`data/judge_b21.txt`): against mi8 pinned to the same opponents, collected
  +7.0%, tributed +12.5%, our deaths -0.18.
- **Running since 06:59:** `data/run_w6.sh` (once, in the background): lv3t (near own-side gem clusters x1.6, rebuilt on
  tw13b) on b19p, b20p, b21p; writes `data/judge_lv3t.txt` (rule in row lv3t). Local screen: collected +4.8%, wins and
  deaths level.
- **Queued: ry2** (Ryth for Varg on 5-pick maps; row ry2, rule written; built as `exp/rf1`, renamed because an ML-era row
  rf1 exists). Local fault screen clean. Its runner `data/run_w7.sh` (started 07:05, once) waits for any chain and for 10
  free groups before each of its three gates, then writes `data/judge_ry2.txt`.
- **N:** ww05 (wins -44 locally), fu100, ww2, gw15 (gold weight 0.15: deaths +29%).

## Update at 06:29 IST 10-30 (session 86)

- **Main is tw13b** (mi8 + `TRAVEL_W` = 1.3 in `targets.h`), adopted at 06:26 as version 1190; mi8 is `bots/pool/mi8`.
  Pooled over b19p and b20p (100 games, to r1000): collected +6.4%, our deaths -0.22, tributed +4.5%; wins 21 and 17 of
  50 (mi8 12 and 18). The predicted mechanism (shorter hops between captures) did not show: the gain is real on the
  metric but unexplained.
- **td1m N** (our deaths +0.03 pooled; bar -0.3). **dl6 N.**
- **Running since 06:29:** `data/run_w5.sh` (started once, in the background): main on the new panel `b21` (five teams
  ranked 41-48, the band of the 2050 target), pins it as `b21p`, then mi8 on `b21p`; writes `data/judge_b21.txt`
  (tw13b against mi8 on current neighbours, recorded, not judged). Later variants then have three pinned bases:
  `tw13b_b19p@b19p`, `tw13b_b20p@b20p`, `tw13b_b21@b21`.
- **Local screening is weak at this effect size.** Ten one-constant variants of tw13b on all 70 maps (420 games each):
  wins spread 301-333 and deaths 1025-1185 around tw13b's own 333 / 1025, so one run's spread is about 12 wins and 5%
  deaths; none passed (rows gd50 / dm40 / fu100 / sq03 / sq07, cs10 / ww2 / tw145, sq03b / gw40 / gw15). Use local runs to
  reject harmful changes, not to rank small ones.

## Update at 05:47 IST 10-30 (session 86)

- **Ladder at 05:26:** rank 69, rating 1946.3 (rank 50 is 2012.1, rank 40 2061.8). Target set by the user: 2050.
- **dl6 N** (row dl6): the rivals' big channels near one of ours still complete 84% (main 86%, bar 68%); the lock rarely
  fires. Folders `exp/dl6` and `exp/dl6m` deleted.
- **w3 chain running since 05:36** (`data/run_w3.sh`, started once in the background; it now waits for 10 free groups
  before its first gate). `tw13b_b19p`: 21 of 50 wins against main's 12, our gems 34699 against 31090, our deaths 375
  against 446. Then `td1m_b20p` and `tw13b_b20p`; the runner writes `data/judge_tw13b.txt` and `data/judge_td1m.txt`.
  `td1m_b19p` alone (`data/judge_td1m_b19p.txt`): our deaths -0.20 +- 0.32, collected 96.9%.
- **Local runs are cheap:** `multi.py` plays 420 games (all 70 maps, cand1, cp3, dh3, both sides) in about 5 minutes per
  candidate with `--jobs 11`, and takes several candidates in one call (one build of the pool). On all 70 maps tw13b
  (copy `exp/tw13c`) beats main (copy, deleted) by 11 wins, -2.5% deaths, +1.7% collected (`data/local_all70_m8a_tw13c.log`).
- **Running locally:** five one-constant variants built on tw13b (row gd50 / dm40 / fu100 / sq03 / sq07), judged against
  tw13c's 420 games. A variant that passes goes to b19p and b20p with tw13b's pinned runs as the base, once tw13b is
  adopted.

## Update at 05:24 IST 10-30 (session 86)

- **Main is mi8** (version 1183 after the dl6 chain and a manual resubmit at 05:13).
- **dl6 chain done** (04:36-05:05): raw `dl6m_b19p` 12/50 and `dl6m_b20p` 19/50 against main's 12 and 18; `td1m_b19p`
  11/50, our deaths 421 against 446. `data/run_dl6.sh` is still decoding; it writes `data/judge_dl6.txt` and
  `data/judge_td1m_b19p.txt`.
- **Pinned panels are deterministic** (findings): `mi8g_b19p` / `mi8g_b20p` repeated `mi8_b19p` / `mi8_b20p` game for game,
  so a variant on b19p or b20p needs no new base run. `data/plan_w3.txt` is now tw13b on b19p and b20p plus td1m on
  b20p (30 groups), with `mi8_b19p` and `mi8_b20p` as bases (rules amended before any game).
- **Do not start a chain while the quota is spent:** `gate.sh` submits the variant first and then waits for groups. At
  05:12 the w3 chain put tw13b on the ladder while waiting; it was stopped and main resubmitted (1183). Start
  `data/run_w3.sh` (once, in the background) after 05:36, when groups free up (`cambc match-groups quota --json`).
- **Lead: tw13b** (travel weight 1.3 in `pick_group`): on two local map sets (20 maps, 120 games) +5 wins each, deaths
  155 and 72 against 173 and 87, collected +5.5% and +4.0%; gains spread over many maps, most on big ones (01islands 2 to
  5 wins, 01broken-curve 2 to 5). 1.6 and 2.0 and 0.8 are worse. Sixteen other one-constant variants (side and
  recent-death discounts, banking batch, hysteresis, shop threshold, help range, engage thresholds) moved collection
  by under 2%: none passed.

## Update at 04:31 IST 10-30 (session 86)

- **Main is mi8** (dl4 + the exact fuel cut in `sim.h`), adopted and submitted at 04:28 as version 1175; dl4 is
  `bots/pool/dl4`. mi8 passed its rule on b19p + b20p against fresh dl4 runs (row mi8): fuel exhaustions after r30 73%
  of the base's, our deaths -0.21 a game, collected 103.5%, tributed 103.6%; wins 30 and 28 of 100.
- **New local baseline:** main's numbers on dl3's 10 maps are now mi7's run `data/runs/multi-033723` (the same code):
  48 wins, deaths 173, collected 1021. Local bars for a variant on main: wins at least 46, deaths at most 187.
- **Running since 04:36:** `data/run_dl6.sh` (started once, in the background): the chain `data/plan_dl6.txt` gates
  `exp/dl6m` (dl6 rebased on mi8) and fresh main runs `mi8g_b19p`, `mi8g_b20p`, then `exp/td1m` on b19p (50 groups; the
  first gate used the last 10 of the old window, the rest wait for the 04:46 reset). It resubmits main at its end and
  writes `data/judge_dl6.txt` and `data/judge_td1m_b19p.txt` (rules in rows dl6 and td1m). td1m (td1's danger rule on
  mi8) passed its local check: deaths 158 against main's 173.
- **N tonight:** mx1 (mi8 + dl6 as a pair; superseded by mi8's adoption and dl6m), cap1b (Capture emblem second: local
  deaths 201).
- **Ladder at 04:00:** rank 68, rating 1957.5 (rank 51 is 2012.2, rank 40 2042.2).
- **Findings** ("Quiet and loud games ..."): the economy gap sits in loud games (we collect 69% of the rivals'); quiet
  games are close (92%) but the rivals hold bigger bags late; the largest share of our deaths is pile-ons in fights we
  are already in (12.1 starts a game, P(death) 0.28, against 6.9 and 0.13).

## Update at 03:57 IST 10-30 (session 86)

- **Running:** `data/run_mi8.sh` (started 03:46): the chain `data/plan_mi8.txt` (mi8 and a fresh main on b19p, then on
  b20p), then it decodes the four runs and writes `data/judge_mi8.txt` (rule in row mi8). b19p: mi8 12/50, main
  (`dl4f_b19p`) 11/50. The chain resubmits main at its end.
- **Queued, not started:** `data/run_dl6.sh` (dl6 and a fresh main on b19p and b20p, 40 groups). The match-group quota
  (50) was at 30 used at 03:55 and resets at 04:46 IST; start it after that, once `procs.sh` shows no chain.
- dl5 is N locally (its early lock purchase changes play); dl6 (the same lock rule with dl2's lock only) passed locally.

## Update at 03:40 IST 10-30 (session 86)

- **Main is dl4** (version 1170, submitted at 02:09). No gate since then; nothing runs.
- **Ladder:** rank 62, rating 1966.9 at 03:38 (rank 51 is 2008.9). The user's target is now 2050 (about rank 40).
- **Local N tonight, none gated:** pk1 (camp ring breach), wl1 (Willow for Varg), cm4 (cm2's churn fix rebased),
  mi7 (mi6's exact fuel cut rebased; 0 mismatches). Each failed the local deaths guard (155 on dl3's 10 maps); the
  calibration rows nop1 / nop2 show the guard's noise is about 6 deaths, so the rises are real.
- **Where the gap is** (findings, "Where the gap is after dl4"): the rivals start twice as many fights; above half
  health we die about twice as often as they do in the same spot; our captures trail in the middle (8.9 against 11.1
  a game by r1000) and in their half (1.8 against 4.9); their Vesper collects about twice what ours does.

## Update at 02:35 IST 10-30 (session 86)

- **Main is dl4**, resubmitted as version 1170 at the end of the wn3 chain (02:09). No gate or local run is going.
- **Ladder:** rank 69, rating 1955.3 at 02:30 (rank 51 is 2010.6, rank 60 1971.9). Last 100 ranked games: 57 wins.
- **wn3 is N** (target missed on b20p: 13.4 to 11.4 rounds, 85% of the base, bar 75%). **pk1 is N** locally: the camp-ring breach for 02the-pack made that map worse (margin -1935 against main's -227 over 6 local games) and raised deaths on the 10 guard maps to 160 (bar 155). Locally main banks on 02the-pack, so the ranked 0-1097 is not its usual result. pk0 was its probe.
- **Maps lost in every recent ranked game** (`data/ranked100.txt`, 100 games): 01islands 0 of 3 (562-1002, 659-1004, 810-1002), adgato_gemcombat4 0 of 3, 01boss_battle 0 of 2 (0-1103 and 162-1014: the altar guard of two monoliths, a known gap). 01starfish 81-1006 had 24 of our deaths to their 2.
- Next: the death gap (b19p: our deaths 6.9 a game to r1000 against the rivals' 3.4) is still the largest general gap.

## Update at 02:12 IST 10-30 (session 86)

- **Main is dl4** (version 1164, resubmitted as 1168 by the cd2 chain). Its guard check on b20p held (row dl4: our deaths +0.00, collected 99.2%, tributed 98.0% against sc1).
- **Ladder:** rank 69, rating 1949.0 at 02:03 (rank 51 is 2013.6). Flat since 01:30.
- **cd1 and cd2 are N** (rows cd1, cd2): hitting or stunning the rivals' tribute channels. On b19p with one of ours within 4 of their 30+ channel we cast on the channeller in 3% of the channels, they on ours in about 30%; cd2 raised ours to 6% only (target missed), because our only stuns are Heart of Ruin's landing dash and Marcella's reset hit. Guards held and wins were 14 against 11 (not judged).
- **Running at 02:12:** the gate chain `data/run_wn3.sh` (wn3 = wn2's winning-carrier change on main, b20p against `dl4_b20p@b20p`; target: rounds from a winning bag to its tribute start at most 75% of the base's). It resubmits main at its end and writes `data/judge_wn3.txt`.

## Update at 01:31 IST 10-30 (session 86)

- **Main is dl4** (sc1 + a chase of the rivals' winning carrier, `abilities.h` and `bot.cpp`), adopted and submitted at 01:30 as version 1164; sc1 is `bots/pool/sc1`. Its guards held on b19p, the death guard close to its bar (+0.26, bar +0.3): watch our deaths on the next panel, and go back to sc1 if they rise.
- **Ladder:** rank 69, rating 1949.1 at 01:30 (1946.6 at 01:13, 1926.8 at 00:57; rank 51 is 2004.1). Ranked 00:20-01:10: 14 wins in 20.
- Close ranked losses of 00:40-01:10 (`data/fights/rk_close`): we held no winning bag in any; the rivals' winning carrier had one of ours within 2 tiles (adgato_gemcombat4) or 6 (01broken_curve) in two of four.

## Update at 01:10 IST 10-30 (session 86)

- **Main is sc1** (dl2 + the split winning capture, `targets.h` and `bot.cpp`), adopted and submitted at 01:09 as version 1161; dl2 is `bots/pool/dl2`. sc1 held its guards on b19p (equal to dl2 to r1000; it acts only at the capture that completes our 1000).
- **Ladder at 00:57:** rank 76, rating 1926.8 (rank 51: 2008.0, rank 60: 1975.2).
- **td2 is N** locally (td1's danger rule at the full ratio: our deaths 166 against main's 145); **dl3 is N** (a lock-less stun and hit on the winning carrier never fired in 124 local games).

## Update at 00:55 IST 10-30 (session 86; supersedes the sections below where they differ)

- **Main is dl2** (cm3m + an altar lock against the rivals' game-winning tribute; `abilities.h`, `bot.cpp`, `shop.h`), adopted and submitted at 00:52 as version 1158; cm3m is `bots/pool/cm3m`. dl2 passed its guard rule on b19p against a same-session cm3m base (row dl2): our deaths -0.23 a game, collected 102%, tributed 101%; games lost before r2000 33 to 29.
- **td1 is N** (row td1): our deaths -0.18 +- 0.40 a game against mi6 on b19p (bar -0.3); guards held.
- **wn2 is N** (row wn2, the successor of wn1): on b19p the hit rounds while holding a winning bag fell 10 to 5 (bar 30%), the rounds from a winning bag to its tribute start 19.8 to 10.8, guards held. The remaining hits land while the carrier walks. **wd1** (dl2 + wn2) passed its local check but is not adopted, since wn2 failed.
- **dl1 is N** locally (deaths 115% of main's, bar 110%; the lock was bought at the first shop and shifted every game's item timing); dl2 buys it only once the rivals reach 600.
- A second session (cambridge-battlecode-45, the one that wrote the 00:08 update) stood down at 00:20 so that only one session gates; it runs nothing.
- Ranked, the 30 games before 00:30: 15 wins. Several losses were close endgames (00ambush 961-1009, 01islands 810-1002).
- Next: capture splitting in the endgame (lever c of the handoff: a big winning capture split among the allies on the tiles keeps each channel short; needs `pick_group` to send allies onto a teammate's held group, `targets.h`), and the death gap on b19p (our deaths 6.9 a game to r1000 against the rivals' 3.4).

## Update at 00:08 IST 10-30 (supersedes the handoff below where they differ)

- **Main is cm3m** (mi5 + cm3's contested-group rule in `targets.h`), adopted and submitted at 00:05 as version 1153; mi5 is `bots/pool/mi5`. cm3m passed its rule on bcgp (row cm3m): steals by the rivals 1.04 to 0.82 a game (bar -0.2), our deaths -0.06, collected 109%, tributed 106%; wins 5 to 11 of 50.
- **mi6 is N** (row mi6): exhaustions after r30 fell only to 89% of mi5's (bar 70%); guards held.
- The gate chain ended at 00:01 (no gate runs). Raw b19p: `mi6_b19p` 10/50 (deaths 399 to 234), `td1_b19p` 11/50 (deaths 384 to 244). The judge runner `data/run_judge6.sh` was still decoding both at 00:08 and writes `data/judge_td1.txt` (td1's rule: our deaths -0.3 a game against mi6_b19p; guards: their deaths at least base -0.3, collected and tributed 97%).
- **If td1 passes:** main is now cm3m, so build the candidate as cm3m plus td1's `knowledge.h` and mi6's `sim.h` (td1 carries mi6's exact fuel change), with a local build check, then adopt and submit.

## Handoff at 23:52 IST 10-29 (the session ran out of context; the next session continues from here)

- **Main was mi5** (version 1138, submitted). Its guard check passed at 23:46 (row mi5, `data/judge_mi5g.txt`: our deaths -0.13 a game against cm1r over 134 games, collected and tributed 103%).
- **Ladder at 23:10:** rank 80, rating 1915.6 (1918.9 at 22:58). Last 30 ranked games: 17 wins. Of the 13 losses, 6 were massacres (12-17 of our deaths to their 1-2), 6 were economy losses at even deaths, and 1 was the endgame (02geodes 997-1002).
- **Still running at 23:52** (check `bash tools/platform/procs.sh`; never start a second copy of a runner):
  - The gate chain `data/run_cm3m.sh` over `data/plan_cm3m.txt` (log `data/chain_cm3m.log`). Done: `mi5_bcgp` (base, 5/50, our gems 27555 against 49584, deaths 194/133), `cm3m_bcgp` (11/50, 31930 against 47342, deaths 196/179) and `mi6_bcgp` (7/50, 30263 against 49148, deaths 204/163). Playing: `mi6_b19p` (from 23:28). Next: `td1_b19p`. At its end the chain resubmits main and the runner decodes the two bcgp runs and writes `data/judge_cm3m.txt` (steals and pooled numbers for cm3m's rule).
  - The judge runner `data/run_judge6.sh` decodes the runs as they finish (2 jobs) and writes `data/judge_mi6.txt` (mi6's fuel rule: `fuel_events.py` exhaustions after r30 at most 70% of mi5's, plus pooled guards) and then `data/judge_td1.txt` (td1's rule: our deaths -0.3 a game against `mi6_b19p`, guards).
  - If the session that started them is gone, the processes may be gone too: then rerun only the missing parts by hand (the decode and judge commands are in the two scripts; `decode_run.sh` and `pextract.py` skip games already decoded).
- **Next steps:**
  1. Judge cm3m, mi6 and td1 strictly by the rules in their rows (written before any game). Record platform results and verdicts in `docs/experiments.md`.
  2. Adopt the ones that pass. They change one file each: cm3m `targets.h`, mi6 `sim.h`, td1 `knowledge.h` (td1 already contains mi6). Combine them as td1 plus cm3m's `targets.h` if all pass. Use `tools/platform/adopt.sh` (it refuses while a gate runs), then make sure main is submitted.
  3. Commit and push (plain `git push` of `batch-loop-2026-10-24`), and delete the `bots/exp/` folders of recorded variants: fx1, mi4, mi4c, mainc, mi3, mi3pf, mainpf, rp1, sp1, mi5c, mi6c, mi6p, then cm3m, mi6 and td1 once they are recorded.
- **New this hour (rows wn1 and the findings section "Endgame: winning bags and the rivals' last channel"):** **wn1** (a bag that alone lifts our tributed gems to 1000 banks through camp hits) fixed the camp part locally (camp hits while holding such a bag 14 to 0) but failed its written bar (camp plus champion hits 50% of main's, bar 30%). It was not gated. The next idea is to deny the rivals' winning channel: in 35% of the games we lose, one of ours is within 6 tiles of their game-winning tribute channel, which a stun cancels (`tools/replay/deny.py`).

## Evening 10-29 (agent, from 21:00 IST; the user's goal: rating 2000 tonight)

- **Ladder:** rank 86, rating 1902 at 21:30 IST; rank 81, 1908 at 22:20 (2000 is rank 51-52). Ranked plays one group of 5 games every 10 minutes. Since mi5 went live (groups of 22:20, 22:30, 22:40): 8 wins of 15.
- **Main is mi5** (cm1r + mi4's fight layer: `micro.h`, the per-tile fight evaluator, and the exact damage model of the 10-29 audit), adopted 22:16, version 1138, on mi4's pass on b19p + b20p (our deaths -0.33 a game against rz20, bar -0.3; guards held). Its guard check passed at 23:46 (see the handoff above).
- **fx1** (mi4's model with rz20's engaging) is N: our deaths +0.00 against the -0.3 target.
- **Queued in one chain on bcgp** (`data/run_cm3m.sh`, after the mi5 guards): a fresh mi5 base, then **cm3m** (cm3's rule on mi5: a defeated group is kept when contested; target: groups we killed that the rivals capture, -0.2 a game) and **mi6** (mi5 with a cheaper `read_slots`: the same slot data on every read, checked over 91,474 reads, at 478 fuel a call instead of 1084; target: our platform fuel exhaustions after round 30 at most 70% of mi5's). On the platform mi4 ran out of fuel after round 30 about three times as often as rz20 (b19p 1.48 against 0.46 a game). Judge numbers go to `data/judge_cm3m.txt`; mi6's are read by hand from `fuel_events.py` and `pooled.py`.
- **Seen in ranked (decoded `data/fights/rk_atnam`, atnaM 22:40):** the 14-1 and 12-1 death games are late fights against champions with twice our health (their Vesper 4-5k, Vendetta 3-6k): our healthy champions walk into their reach because the danger tiles count only one-turn bursts of 30% of our health or more, and a tank's burst is below that. Deaths after a melee chase of 3+ rounds are 9% of mi4's platform deaths (0.43 a game, 100 games), so not the main gap.
- Pinned panels play 50 games in about 4 minutes; the quota (50 groups an hour) and decoding (about 15 minutes a run at 2 jobs) set the pace.


## Summary of the night's tasks (10-28, agent alone; the user's task list)

- **Main and ladder bot: nm2** (sq2 + Heart, Vesper, Marcella in the 3-pick draft on maps without gold camps, of the 70 only adgato_gemcombat1; adopted 23:54 IST, submitted as v1034; sq2 is `bots/pool/sq2`). Its bases: `nm2_bwmp@bwmp`, `nm2_b13p2@b13p2`, `nm2_b16p@b16p`; on brkp2 `sq2_brkp2@brkp2` (brkp2 holds no gemcombat1 game, and off gemcombat1 nm2 replays sq2's platform games exactly). Before it **sq2** (cov1 + company in the pick: a group is scored only for the champions heading there, and a joiner's share counts sqrt(n); adopted 18:21 IST, submitted as v1009; cov1 is `bots/pool/cov1`, go1 `bots/pool/go1`). Its exact bases: `sq2_bwmp@bwmp`, `sq2_b13p2@b13p2`; `sq2_brkp2@brkp2` (18:23-18:31: 37/100 wins, cov1 19). Ladder rank 96, rating 1865 at 18:35 IST (72 and 1915 at 15:38, 85 and 1884 at 11:50); ranked groups 15:20-17:00 IST (go1 live but for two gates): 18 wins in 55; 17:10-18:30 (cov1, then sq2): 21 in 45 (`data/ranked_1028d.json`).
- **Turn order, found 05:10 on the user's 04:05 redirect (simple ideas, maps), was the largest lever of the night** (`docs/findings.md`, "Turn order: the rivals act first in contact"). **go1** (an enemy within 5: act first next round, the most hurt first) on brkp against cr3, paired to r1000 over 100 games: our deaths -1.1 +- 0.4 and theirs +0.9 +- 0.4 per game, collected +13%, tributed +14%; it held every b13p guard and was adopted. **go2** (first within 3, last at 4-8) and **go3** (go2 + the fight simulator striking first) were rejected: go2 raised our deaths 0.7 per game on brkp (farming near enemies at 4-6 while acting last), go3 raised them locally.
- **Task 1, the 00ribs opening: closed at 03:05, target not met** (ce1-ce5; ce5 kept as `results/analysis/ce5_on_cr3.patch`). **Task 2, the user's two queued games: done 03:11** (`docs/findings.md`, "The user's two queued games").
- **Task 3, 00contest: closed at 06:10 on its 3-hour budget, target not met.** Cause in `docs/findings.md` ("00contest: who takes the monoliths"); go1 cut our 00contest deaths from 15.0 to 11.2 per game, but our tributed stayed near 10 (bar 100).
- **Task 4, 00crater: closed at 10:30 on its 3-hour budget, target not met** (collected +15% with deaths not higher, on brkp's 20 00crater games). Cause (`docs/findings.md`, "00crater: one altar in a pocket, and the opening order"): the only altar sits in a walled pocket above the middle elk, so both teams meet there; in the opening our champions split (a pick probe: all five pick our top wolves at r1, four leave for the elk at r4-r7 once teammates' claims halve the wolves' share), while the top teams take their wolves with all five and reach the elk together; after r150 we spread (teammates within 6 0.80 against 1.31) and the rivals take 62% of the middle strong camps we wake once they arrive. **cl1** (score a group with its claimants only) and **tg1** (cl1 + before r40 each champion scores as if alone, so the five stay together) both failed the 00crater target but held every guard: tg1 on brkp, paired over 99 games against go1, our deaths -0.9 +- 0.5 and theirs +2.1 +- 0.6 per game, collected +32 +- 23, tribute margin +109 +- 47 (the largest gain of the night), 00crater collected +8% (bar 15%). **sq1** (tg1 + a joiner's share counts sqrt(n)) reached the top teams' mid-game cohesion locally (teammates within 6 at r300-1000 1.25-1.31 against tg1's 1.01-1.05) at 11% more deaths; not gated (the budget ran out during a usage pause, 09:13-11:11). Folders kept: `bots/exp/tg1`, `bots/exp/sq1`.
- **Daily re-pin (11:25):** fresh unpinned go1 runs `main_brk1028@brk` (19/100) and `main_b13_1028@b13` (13/50) pinned as `brkp2` and `b13p2` (`results/panels/README.md`); the bases from task 5 on. Main go1 live as v993. Ladder rank 85, rating 1884 at 11:50 IST.
- **Task 5, 00eight: closed at 14:08 IST, target not met** (3 variants; no fourth gate fits before 14:17). Factor: gems lost on death (brkp2 base 104 against the rivals' 32 per game, deaths 10.0 against 5.0). Cause (`docs/findings.md`, "00eight: the first centre fight"): go1 loses the first centre fight 3 for 1 at r50-60, and the big bags (59 = the triple elk group taken by one champion) die beside the centre altar: the carrier kites out of reach and walks back each turn without starting the channel, while the rivals tribute next to it. **tg1e** (tg1 unchanged): 30/100 wins against 19, margin +146 +- 48, 00eight deaths -1.6 and tributed +27%, lost on death -3%: N. **wb1** (tg1 + a fix of a stale bank walk that gave up banking for 40 rounds; found with the probe bp1l): carrier rounds -36% on 00eight, lost on death -2.5%: N. **uf1** (tg1 + tribute under fire at the altar when the carrier outlasts the channel): the trigger rarely holds on the platform, lost on death +2%, and against tg1e collected -14 +- 5 per game: N. tg1 stays the strongest candidate (`bots/exp/tg1`, `results/analysis/tg1_on_go1.patch`); main stays go1 (live as v997).
- **Task 6, 01yellow_brick_road: closed at 17:14 IST, target met, cov1 adopted.** Cause (helper h3, `docs/findings.md`, "01yellow_brick_road and the cover lock"): the `covered` rule in `pick_group` let sleeping elk groups lock the groups within 4 for good (7 of 70 maps; yellow's corner and centre pairs, captures 0.9 per game against the rivals' 13.0). cov1 (an elk group covers only while awake) on bwmp: yellow collected +29%, wins 5 to 11 of 20, but N on a 20-game death bar it could not resolve (+0.8 +- 1.0). Retest cov1r on the new 100-game lock-map panel `lkmp`: our deaths -2.3 +- 0.7, collected +46%, tributed +65%, wins 30 to 50; b13p2 guard held (deaths +0.1, tributed 108%). cov2 (+ h2's help fix) rejected locally. The user's ranked 00vault loss (0-1000 at r325) is in `docs/findings.md`: they captured the 343-gem vault three times and we never stepped in to reset a capture (fix idea: capture denial).
- **Task 7, 00interlock: closed at 18:21 IST, target met, sq2 adopted.** Cause (`docs/findings.md`, "00interlock: lone waiters in our own half"): our deaths in our own half 2.85 per game against the rivals' 0.70, champions alone and far out (allies within 6 0.72 against 1.08; strong camps tanked alone 322 rounds per game against 160); leaving on sight (ev1, ev2) failed locally. tg2 (tg1's scoring on main) did not move cohesion locally (**R**). sq2 (tg2 + a joiner's share by sqrt(n)) on bwmp: allies within 6 1.02, solo tank rounds 173, own-half deaths 1.15 per game, all interlock deaths 6.0 to 2.6, tributed +158; the other 80 games held (deaths -0.6, collected 97.3%); b13p2 deaths -1.4, collected 98.6%, wins 14 to 26 of 50. bwmp wins 36 to 44 of 100. sq3 (the same scoring only under threat) recorded, not gated.
- **Task 8, adgato_gemcombat5: closed at 21:05 IST, target met by esc4; not adopted (22:05, the b15 guard failed).** Base `sq2_bwmp@bwmp`; gap (to r1000): tributed 547 against 918, lost on death 297 against 102. Causes (`docs/findings.md`, "adgato_gemcombat5: big bags on a long trip"): the 140-gem middle group's capturer walks the bag to the one altar alone, and in the opening it freezes on the group's tiles and holds back the respawn its team waits for. bq2 (40-gem cap) N; esc2 (60-gem cap; its escort never ran: ally snapshots carry no gem count) N; esc3 (escort fixed) N at 225 against a bar of 200; **esc4** (esc3 + respawn-wait fixes) on bwmp: gemcombat5 lost on death 297 to 198, tributed 547 to 688, frozen carrier-rounds 94 to 11, other 78 games level, 49/100 wins (sq2 44); b13p2 guard held (deaths -0.4, collected 100.5%, tributed 102.6%). The user then asked for a fresh batch (`b14`, ranks 80-90: esc4 32/50, sq2 29/50; paired: deaths +0.0, collected 100.1%, tributed 100.4%, so its bars hold) and a stronger one (`b15`, ranks 58-70: esc4 20/50, sq2 21/50; paired: deaths -0.4, collected 95.0% against the bar of 97%, tributed 97.9%), so main stays sq2. esc4's source is kept as `results/analysis/esc4_on_sq2.patch`.
- **Task 9, adgato_gemcombat1: closed at 23:54 IST, target met, nm2 adopted** (from 21:40 IST; budget 5 variants or 3 hours, to 00:40; 2 variants gated). Base `sq2_bwmp@bwmp`. Gap (to r1000): lost on death 191 against 39, deaths 5.3 against 2.8, tributed 598 against 881; the tribute gap is mostly the death gap counted twice (their kill gems are our bags). Cause and target in `docs/findings.md`, "adgato_gemcombat1: deaths at the altar and no gold": we lose the fights at the centre altar and in our half (our Heart dies 2.1 times per game against 0.5) with about 40% of the rivals' team gold at r600 (no gold camps there; our 3-pick draft has no Marcella and Vesper's gold passive gives nothing). Target: lost on death 115 or less with tributed not below 598. Variants: nm1 (Marcella in the 3-pick draft on gold-less maps, built on esc4): against `esc4_bwmp@bwmp` gold r600 213 to 820, lost on death 150 to 85, tributed 604 to 752, deaths 5.0 to 3.2 (theirs 3.1 to 6.5), the other 78 games identical; nm2 (the same on sq2, the main candidate) met the target on bwmp (23:06): gemcombat1 lost on death 191 to 98 (-93 +- 31), tributed 598 to 723, team gold r600 210 to 678, deaths 5.3 to 4.2 (theirs 2.8 to 4.8), wins 44 to 54 of 100 (10 L->W, 0 W->L), the other 80 games identical. Guards held: b13p2 identical to the base (26/50 wins both, every paired difference 0.0); the fresh batch b16 (Gamblr, Quant Merch Traders, will think later, cheji bt, Gem Simons; main `sq2_b16@b16` 27/50, then nm2 on it pinned as `b16p`): 28/50 wins (main 27); the one gemcombat1 game (Quant Merch Traders) went L->W (tributed 693 to 924, lost on death 84 to 21) and the other 49 games replayed the base exactly; paired to r1000 our deaths +0.0, collected 711.6 to 713.3 (100.2%), tributed 623.2 to 627.8 (100.7%): the bars hold. Adopted 23:54 as v1034. Ready, not gated: esc5 (esc4's three fixes on gold-less maps only, on nm2; rule in its row in `docs/experiments.md`) and the 20-gem batch cap for gemcombat1 (`results/analysis/bc1_on_sq2.patch`).
- **Helpers (from 12:25 IST, the user's other Claude accounts):** h2 audits the bot for stale state (`docs/helper/NOTES.md`, patches in `docs/helper/patches/`), h3 does map research (`docs/helper3/NOTES.md`, patches in `docs/helper3/patches/`, tools in `tools/helper3/`). Both work locally only: the lead alone gates, submits and edits the shared docs. Pushing to GitHub is allowed since 10-28 13:50 (`CLAUDE.md`).
- **Maps (the user's 04:05 request):** we lose where contact is forced (altars in the middle, spawns under 30 steps apart). The top teams draft the same five on all maps and win equally on our bad and good maps, so the bad maps punish our fighting and our early farming.

## Now
- **micro.h (10-29 evening, the user's go at about 19:35 IST: "DO it and take us to the path to victory").** The per-tile fight evaluator of STRATEGY section 4 is built as `exp/mi1` (rows mi1 and mi2: threat per tile summed over the visible enemies from their live cooldowns, doubled under a ready stun; used for closing in, the step after a melee hit, the dash after a shot, kite, flee dash and flee step, and as a 60% trigger to leave). Its rule (written 20:00 IST) judges our deaths on the pinned b19p + b20p against the rz20 bases, guards on b13p2, b16p, b17p. mi1 failed its local fuel check, mi2 is mi1 with the threat loops made cheap; mi2 passed it (out of fuel after round 3 12 times against main's 6 on the same 48 games, bar 2x; locally our deaths -0.54 per game but kills -1.04 and collected 95.3%, so the platform guards on their deaths and collected are the risk). mi3 = mi2 + a prey our hit kills this turn adds no threat (locally Vendetta's kills had fallen 146 to 95 with her deaths level): on the same 48 games kills 502 (mi2 488, main 538), deaths 180 (193, 219), collected 984 (968, 1016), fuel 11. mi3 took mi2's queued slot at 20:17 IST before any platform game (rule amended then): runner `data/run_mi3.sh` waits for the cm1r chain, gates mi3 on b19p and b20p and writes `data/judge_mi3.txt`. In parallel, cm1r's remaining guards (b13p2, b16p, b17p with fresh rz20 bases, which mi2's guards reuse) run as chains plan_cm1rg (19:42, stopped with the previous session after its third line) and plan_cm1rg2 (19:56); judge in `data/judge_cm1rg.txt`. Main is rz20, live as version 1124.
- **Study day (10-29 afternoon and evening, the user's request; no bot change).** `docs/STUDY.md` collects how teams solve Battlecode-type games (MIT 2019-2026 postmortems, UNSW Battlecode 2026, CodeWizards, Ants, Halite, CodinGame) and what they agree on; its section 6 compares our process with theirs. `docs/STRATEGY.md` 2.8-2.12 derives numbers from the rules: reach and stun reach per champion, time to kill, camp yield per champion-round, tribute and Marcella, what a champion can read. The proposed next step is the per-tile `micro.h` (STRATEGY section 4), waiting for the user's go. rz21 (danger from the enemies together) is N (row rz21); main stays rz20, live as version 1122 since the 14:47 resubmit.
- **Main is rz20 since 10-29 14:05 IST (version 1118; session t10).** rz20 = rz12 + two steps out of fights: the flee step (`move.h` `walk_home(true)`: the step towards spawn that ends farthest from the enemy champions) and the shooter step (in the kite branch a ranged champion steps out of danger first, then shoots with the attack reset, `abilities.h` `reset_shot_after_walk`). Passed its rule on the fresh batch b20 (teams 31-39) against `rz12_b20@b20` in the same chain (50 paired games to r1000): our deaths 4.68 to 3.92 (-0.76 +- 0.40), theirs +0.46, collected 103.2%, tributed 107.6%, win share 0.26 to 0.36 (row rz20). rz12 is `bots/pool/rz12`. Rebase variants onto `bots/main`. Bases: `rz20_b20@b20` (same games as `rz12_b20@b20`, whose opponents `b20p` pins); on b13p2, b16p, b17p and b19p run a fresh rz20 base first.
- **Main was rz12 from 10-29 10:34 to 14:05 IST (version 1099, live as 1113 after the 13:31 resubmit; session t10).** rz12 = rz9 + Vendetta dashes in only with the numbers at the landing, or level against a target at 40% health or less (`abilities.h` `dash_next_to`, `margin_at`). Passed its rule on b13p2 + b16p + b17p (144 paired games to r1000): Vendetta deaths 1.22 to 1.01 per game, our deaths -0.04, theirs +0.05, collected +1.4%, tributed +0.1% (row rz12). rz9 is `bots/pool/rz9`. Rebase variants onto `bots/main`. Bases: `rz12_b13p2@b13p2`, `rz12_b16p@b16p`, `rz12_b17p@b17p`
- **Main was rz9 from 10-29 07:48 to 10:34 IST (version 1072; session t10).** rz9 = nm2 + no striking dash at the top of the threat branch (`abilities.h` `use_champion_abilities`): a threatened, losing Heart of Ruin no longer dashes next to its prey before it kites or flees. Passed its rule on b13p2 + b16p + b17p (144 paired games to r1000): Heart deaths 1.32 to 0.95 per game, our deaths -0.20, theirs +0.02, collected +1.7%, tributed +3.2% (row rz9). nm2 is `bots/pool/nm2`. Rebase variants onto `bots/main`. Bases: `rz9_b13p2@b13p2` (45 games: snoc left the competition), `rz9_b16p@b16p`, `rz9_b17p@b17p`.
- **Main is nm2 again since 10-29 04:31 IST (version 1060; lead session t9).** The b17 check of lv1 tripped its death guard (our deaths to r1000 +0.54 per game, bar 0.5; gems collected +7.8, tributed +25.3), so `adopt.sh nm2 lv1` put nm2 back; lv1 is `bots/pool/lv1` (row "lv1 (b17 check)"). Bases: `nm2_b13p2@b13p2`, `nm2_b16p@b16p`, `nm2_b17p@b17p`, `nm2_bwmp@bwmp`, `nm2_bglp`-pinned `bglp`.
- **Main from 03:41 to 04:31 IST was lv1 (version 1057; lead session t9).** lv1 = nm2 + one change in `camps.h`: `gold_weight` counts a gold as 0.1 gem from round 300 (was 0.25 to r1400), so `pick_group` takes gem groups over gold groups once the early stat buys are done (row lv1 in `docs/experiments.md`). nm2 is `bots/pool/nm2`. Rebase variants onto `bots/main`. Bases: `lv1_b13p2@b13p2`, `lv1_b16p@b16p`; on other panels run lv1's base first (lv1 plays every map with gold differently from nm2; gold-less maps as nm2).
- **Main before lv1: nm2, 10-28 23:54 to 10-29 03:41 IST (version 1034; lead session, task 9).** nm2 = sq2 + one draft change (Heart, Vesper, Marcella on 3-pick maps with no gold camps; only adgato_gemcombat1), so its play on every other map is sq2's. sq2 is `bots/pool/sq2`. Rebase variants onto `bots/main`. Bases: `nm2_bwmp@bwmp`, `nm2_b13p2@b13p2`, `nm2_b16p@b16p`, and on brkp2 `sq2_brkp2@brkp2` (off gemcombat1 nm2 replayed sq2's games exactly: 179 of the 180 guard games, every paired difference 0.0).
- **Task 10 (second session t10, from 21:50 IST on 10-28; updated 10-29 14:10).** Closed: ranged hits outside fights (rz1-rz6 N, `docs/findings.md` "Ranged hits outside fights"), fight openings from 4 tiles (rz7 N, "Deaths in fights the rivals start"; patch `results/analysis/rz7_on_nm2.patch`), tribute timing (no gap, "Bags at the end of games, and the ranked losses"). **Factor since 03:46: our deaths on 5-champion maps.** After rz9 (adopted 07:48, Heart deaths -0.37 per game) the gaps by type in five-a-side games, us against them: Vesper 0.84 / 0.38, Vendetta 1.08 / 0.72, Varg 0.97 / 0.77, Heart of Ruin 0.91 / 0.83, Marcella 0.61 / 0.73 (findings "Deaths by champion type after rz9"). rz10 (Heart's first emblem Durability of health) is **N**: its max health at r400 rose 1230 to 1457 but its deaths did not fall (0.87 to 0.86; patch `results/analysis/rz10_on_rz9.patch`). **rz12** (Vendetta dashes in only with the numbers at the landing, or level against a target at 40% or less; `abilities.h` `dash_next_to`) passed its rule over b13p2 + b16p + b17p against rz9's runs (144 paired games, `data/judge_rz12b.txt`): the dives it refuses 1.65 to 0.45 per game, Vendetta deaths 1.22 to 1.01 (-0.21 +- 0.08), our deaths 4.22 to 4.17, theirs 4.58 to 4.63, collected 101%, tributed 100%; **adopted 10:34 as version 1099**. Findings "Outnumbered" (09:35): with three or more enemies within 6 and at most one ally we die 1.66 times per game against the rivals' 0.70 while being there as often; we stand closer, keep hitting and move sideways (23% of those rounds against 13%). **rz14** (rz12 + the flee step towards spawn that ends farthest from the enemies, `move.h` `walk_home(true)`) is **N** (10:58): on b13p2 + b16p the outnumbered deaths fell 0.31 per game (bar 0.2) but the sideways share only to 0.175 and 0.185 (bar 0.17), and its b17p check failed the target (-0.05). Over the three panels (145 paired games) it cut our deaths 4.15 to 3.68 (-0.47 +- 0.24) with theirs +0.22, collected 101.6%, tributed 102.3%, win share 0.54 to 0.51; patch `results/analysis/rz14_on_rz12.patch` for a retest that names our deaths as the target on a fresh panel. rz15 N (not gated). Findings "Vesper's contacts while short" (10:55, `tools/replay/contacts.py`): our Vesper (0.82 deaths per game against 0.51) begins a contact while short 2.11 times per game against 1.10, and 0.97 of ours (0.34) come right after her shot from 2 tiles: the kite step's free shot costs a shooter its step. **rz13** (rz12 + no walk-in next to an enemy while short, for Vendetta, Varg and Vesper) is **N** (11:08): walk-ins one or more short -20% (bar -40%), Vendetta + Varg + Vesper deaths -0.19 (bar -0.2); patch `results/analysis/rz13_on_rz12.patch`. **rz17** (rz12 + a shooter in danger steps out first, then shoots with the attack reset) is **N by its rule** (12:20) on b13p2 + b16p: Vesper's deaths -0.13 +- 0.07 (bar -0.12), our deaths -0.27, theirs +0.25, collected 102.4%, tributed 102.0%, win share 0.51 to 0.58, but its mechanism fell 0.89 to 0.68 per game, not to 0.45; all of our fewer deaths came in the games with fewer than five a side. Its b17p check (12:52, `data/judge_rz17b.txt`) is **N** as well: her deaths fell 0.12 per game on b17p and over the three panels and every guard held (three panels, 145 games: our deaths -0.23 +- 0.16, theirs +0.13, collected 100.5%, tributed 101.7%, win share 0.54 to 0.58), but on b17p the mechanism rose (1.20 to 1.30 per game, bar 0.96); patch `results/analysis/rz17_on_rz12.patch`. **rz19** (main + rz14's flee step: the retest with our deaths as the target) is **N by its rule** (13:20, `data/judge_rz19.txt`) on the fresh batch `b19` (Olympus 34, Noobot 37, PENTAKILL 48, Sheeesh--- 55, SquidProxyLovers 60; we were 72 at 12:40; pinned as `b19p`, base `rz12_b19@b19`, free for both sessions): our deaths 6.76 to 6.24 (-0.52 +- 0.41, bar -0.2) and every guard held, but the sideways share with one ally rose 0.22 to 0.23 (needed below). Over four panels (195 games) the flee step cuts our deaths by 0.48 +- 0.21 per game, with no win share gained. Findings 'Against teams 34-60 we lose the group fights' (13:20): on b19 with five a side we die 6.61 times per game against 2.71, every type about three times as often; we are as grouped as they are, but with an enemy within 8 and two or more allies near we die 0.70 times per 100 rounds against 0.09; 4.50 of our 6.8 deaths a game come in fights they start; their gold is 1.27 times ours at r300 and r600 and their Marcella has 2536 max health at r600 against 1862. **rz20** (main + the flee step + rz17's shooter step, rz18's source) **passed its rule and was adopted at 14:05 as version 1118** (`data/judge_rz20.txt`): on the fresh batch `b20` (subscribe to caterpillow 31, Zarzorki 35, SilverSamurai 36, test4 38, HBH 39; pinned as `b20p`) against `rz12_b20@b20`, our deaths 4.68 to 3.92 per game to r1000 (-0.76 +- 0.40, bar -0.3), theirs 3.26 to 3.72, collected 103.2%, tributed 107.6%, gems lost on death 55 to 37, Vesper deaths 0.98 to 0.62, win share 0.26 to 0.36 (18 of 50 wins against 13). Next in the queue: what loses the group fights against the stronger teams (health from the builds: the rivals' Bruiser-health and Bruiser-focus emblems on Marcella and Heart of Ruin; heals missing from the fight simulation). Night coordination with t9: `data/coord/PROTOCOL.md`, events in `data/coord/board.md`, claims in `data/coord/t10.md`.
- **Task 9 line (lead session, tag t9; night loop under `data/coord/PROTOCOL.md` from 01:00 IST, events on `data/coord/board.md`, claims in `data/coord/t9.md`).** Task 9 closed at 23:54 with nm2 adopted (v1034): esc4 failed its b15 guard (collected 95.0%, bar 97%); nm1 (22:22) and nm2 (22:45) gated on bwmp; nm2's guards b13p2 (23:12) and the fresh batch b16 / b16p (23:22-23:43) held (`data/task9_scratch/judge_b13p2.txt`, `judge_b16.txt`). nm2 replays sq2 on brkp2, so `sq2_brkp2@brkp2` is its brkp2 base. esc5 on bwmp (00:09-00:33): **N** at 00:58 (gemcombat5 lost on death 297 to 204 against a bar of 200; source kept as `results/analysis/esc5_on_nm2.patch`). Found on the way (00:20): 96% of main's bank blocks are false (`docs/findings.md`, "False bank blocks after a break"). Its fix **bk1** on brkp2 (01:12-01:26): **N** at 01:45 (tributed 360 to 359, bar 378; our deaths +0.4 per game, bar 0.3; source `results/analysis/bk1_on_nm2.patch`). New gold-less panel `bgl` (adgato_gemcombat1-5 against five eligible teams 14-29 ranks above us, `results/panels/specs_bgl.txt`), pinned as `bglp` to main's base `nm2_bgl@bgl` (24/50: gemcombat1 9/10, gemcombat2 7, gemcombat3 2, gemcombat4 5, gemcombat5 1; gemcombat5 tributed 359 against 902). **esc8d** (esc5's gold-less changes, the 60-gem cap only after a 60+ capture, and bk1's fix, all behind `cashless_map()`) on bglp (01:59-02:17): **N** at 02:25 (18/50; the gemcombat5 haul banking held, 16% to 52% of hauls tributed first, tributed there 359 to 564; but lost on death 113.5 to 122.6 against a bar of 91 and our deaths +1.0 per game, from gemcombat1 and gemcombat2, where the extra deaths are light-bagged champions and the games first leave the base's mostly at escort starts; scratch `data/task9_scratch/deathkinds.py`, `diverge.py`). **esc9** (esc5's package rebuilt on main: every bag capped at 60 on gold-less maps, the escort, the respawn-wait fixes, no bank fix) on bglp (02:39-02:48): **N** at 02:57 (24/50, base 24; gemcombat5 tributed 359 to 604, but lost on death 113.5 to 127.4 over the panel against a bar of 91, and our deaths +0.7 per game, bar 0.3). esc10 (esc9 without the escort) checked locally only: the gold-less line closes (those maps are about 7% of ranked games). At 02:49 a second copy of my runner started a duplicate esc9 chain, stopped at 02:53 before any group was created; main resubmitted (v1052), and `tools/platform/procs.sh` now lists runner and judge scripts. **lv1 adopted at 03:41 (version 1057):** factor gems collected on maps with gold (`docs/findings.md`, "Gems per camp hp: gold groups over gem clusters"); lv1 (gold counts 0.1 gem from r300 in `pick_group`, was 0.25) on b13p2 and b16p (03:12-03:20) against the pinned bases, paired to r1000 over 100 games: collected +38.8 +- 13.9 (bar +25), tributed +41.1 +- 13.9, our deaths +0.27 +- 0.22 (bar 0.3), pure gem-cluster captures on b13p2 5.80 to 7.62 (bar 6.80); wins 54 to 52 (row lv1). By team size the gain is largest on 3-pick maps; on 5-pick maps our deaths rose (b13p2 5.21 to 5.93), and those deaths are now t10's factor (board 03:39). From 03:30 the two sessions share findings and readers on the board (`capkind.py`, `mapgap.py`, `pairsize.py` in `tools/replay`). **Now:** the next camp-choice gap on top of lv1. Scratch readers: `data/task9_scratch/` (gitignored). Ladder rank 82 at 03:18 IST. **04:15:** fresh batch `b17` built (Nyx, dromedaries, smurphy, KKB, Tatakai; `results/panels/README.md`); lv1 played it (`lv1_b17@b17`, 22/50, deaths 332 against 346), pinned as `b17p`; nm2 on b17p and the judge (`data/task9_scratch/judge_b17.txt`, rule in `data/coord/t9.md`) run unattended. Next: 01the_farm bank timing (board FINDING 04:15) and the b17 economic gap. **04:31:** the b17 check sent nm2 back as main (v1060; deaths +0.54 against the bar of 0.5); lv1 is `bots/pool/lv1`. Next: a gem gain without the extra deaths (lv1 on 3-pick maps only, where its deaths were flat), and 01the_farm bank timing. **06:14:** next variant `ek1` (nm2 + `clear_time` in `camps.h` charges every point of camp damage as a share of a heal trip): we hit elks 7-28% more than the rivals at every team size and wolves 6-17% less (nm2, b13p2 + b16p + b17p). Rule in the ek1 row. **06:23: ek1 N on its local check** (8 elk maps x cand1, cp3, dh3, 48 games each): our elk camp-hit rounds fell only 3.6% (bar 10%), wolves 12%, and collected to r1000 fell 929 to 892; not gated. Next: cluster fields. On 00lost_world (14 ranked games since 10-27, 5 wins) the rivals stand in the gem-cluster field around the centre altar (18,15) and tribute there 784 gems per game in 40 trips (ours 387 in 11); from r300 our champions walk home (own-region champion-rounds r300-700: 800 against their 287) and our middle gem-cluster captures fall to 0.6-2.4 per 100 rounds against their 8-11, with fewer deaths than theirs (6.8 against 10.1). Champions with a recent death spend 36% of rounds in the middle against 53% without (theirs 79% either way): the recent-death and danger divisors of `pick_group` are the suspects. snoc has left the competition (create answers HTTP 409 'no longer taking part'): `gate.sh` now skips such a team, and b13, b13p, b13p2, lkm, lkmp give 45 games. Main resubmitted unchanged as version 1062 at 06:13 (t10's rz9 gate hung on snoc from 05:03 with rz9 live). **07:10:** the gate slot is blocked: t10's chain `plan_rz9` has hung on snoc since 05:03 (its processes stay untouched; board 06:10-06:12), so the t9 line works locally until it ends. Where the gap sits on b13p2 + b16p + b17p (nm2, 150 games to r1000): lives captured are level (41.5 against 42.5 per game, `decoded.py lives`) and so are camp-hit rounds (607 against 608), but the rivals take gem-richer groups (gems by the camp last hit: gem clusters 252 against 312, monoliths 3 against 14; `decoded.py sources`). Harmless one- and two-cluster gem groups in our own half lose nearly every pick to solo mixed groups whose gold counts (probe `lv2pl` on 00road-of-riches, row lv2pl), where the rivals take 30.5 such captures a game and we 0.5. Next variant `lv2` (those groups count their gems 1.6 times in `pick_group`); its local check runs now (rule in the lv2 row, written before the run). **07:20:** lv2 is N on its local check (`data/runs/multi-070808`, 54 games each against cand1, cp3, dh3 on 9 maps): own-half pure gem captures rose from 9.35 to 19.81 a game and collected from 896 to 938, but team gold at r600 fell to 89.7% of main (bar 90%) and the opponents took most of it back in the middle we left (their collected +31, so our margin grew 11 and our tributed margin 6). Next variant `lv3`: the same boost only within 8 steps, for passing or respawned champions; its local check runs now (`data/runs/multi-072028`; rules in the lv3 row, written before the run). t10's chain `plan_rz9` moved on at 07:16 (rz9 on b16p); I gate lv3 after it if the local check passes. **07:35:** lv3 passes its local check (own-half pure gem captures 9.35 to 19.04 a game, collected 896 to 946, the opponents' 739 to 712, team gold at r600 94.7% of main; row lv3) and gates now: chain `plan_t9p` (b13p2 + b16p, pinned, from 07:33), then b17p; judge `data/task9_scratch/judge_lv3.txt`; platform rule in the lv3 row, written before the gate. **08:01:** on b13p2 + b16p (95 paired games against the nm2 bases, to r1000) lv3 meets its rule so far: collected +26.4 +- 12.7 a game (target +15), tributed +16.7 +- 11.8, deaths -0.24 +- 0.18 (b13p2 -0.42, b16p -0.08), own-half pure gem captures 2.41 to 3.46 a game, team gold at r600 100% of the base; wins 53 to 54. Its b17p line ran 07:52-07:56; the three-panel judge runs now (`data/task9_scratch/judge_lv3b.txt`). t10 adopted rz9 as main at 07:52, so lv3 is rebuilt as `lv3r` (rz9 + lv3's `targets.h`); if the three-panel judge passes, lv3r gates on b13p2 + b16p against rz9's runs after t10's rz10 chain (rule in the lv3r row, written before that gate). **08:18:** lv3 passes its platform rule on all three panels (145 paired games against the nm2 bases, to r1000): collected +35.2 +- 11.2 a game, tributed +30.3 +- 11.3, deaths -0.39 +- 0.18 (b13p2 -0.42, b16p -0.08, b17p -0.66), own-half pure gem captures 3.16 to 4.68, team gold at r600 100.6%; the opponents' collected -22.4 and tributed -26.1; wins 77 to 83 (row lv3). lv3r waits for the gate slot (runner `data/task9_scratch/run_lv3r.sh`, `data/gate_wait/t9` set); lv4 (the near boost for middle clusters too, on lv3r) is in its local check (`data/runs/multi-080402`, row lv4). **08:27:** lv4 passes its local check (66 games each against cand1, cp3, dh3 on 11 maps, against lv3r): middle pure gem captures 5.97 to 8.74 a game, collected 946 to 985, the opponents' 727 to 718, deaths level at 2.7, team gold at r600 95.6% of lv3r's; it gates on b13p2 + b16p after lv3r, against main's runs there. **09:04:** lv3r is **N** on its platform rule (b13p2 + b16p against rz9's runs, 95 paired games to r1000, `data/task9_scratch/judge_lv3r.txt`): own-half pure gem captures 2.52 to 3.49 a game and collected +7.6 +- 16.8, but tributed -2.1 +- 14.6 against the bar 'not below rz9'; deaths -0.11, team gold r600 99.7%; wins 48 to 50. Main stays rz9; the change is kept in `results/analysis/lv3r_on_rz9.patch` and goes on inside lv4 (rz9 + lv3's change + the middle's harmless clusters, `targets.h` only), which gates on b13p2 + b16p against rz9's runs in t9's next turn (`data/plan_t9s.txt`, runner `data/task9_scratch/run_lv4.sh`). Then a fresh stronger batch `b18` (procless, conqueror_of_openai, Jupiter, Rogue Lock Pickers, SALUTE TO TUNG; ranks 18-34; `results/panels/specs_b18.txt`) to find the gap against the teams above. Ranked record and the panels' camp economy: `docs/findings.md` ('Ranked record at 10-29 08:35', 'Gem clusters in rounds 300-600'). **10:55:** lv4 is **N** on its platform rule (b13p2 + b16p against rz9's runs, 95 paired games, `data/task9_scratch/judge_lv4.txt`): middle pure gem captures 1.76 to 2.78 a game, but collected -2.4 +- 18.7 (target +15) and tributed -6.4 +- 16.5; deaths -0.08; wins 48 and 48. The cluster line (lv2-lv4) is closed. Golem groups are the next gap (`docs/findings.md`, 'Golem groups: nobody starts them alone'): we kill 1.10 golems a game on 02famine against the rivals' 4.30, 2.12 against 3.62 on 00split, 0.75 against 1.88 on 00quadrants, because a lone champion scores them at a quarter of its pick (probe `lv5pl`). `lv5` (a crew of one more teammate in the score, and a gather for it) is **N** locally (golem kills 1.50 to 2.83 a game, but captures 52 to 42 and deaths +0.9). Main is rz12 (t10, 10:35). The t9 session stops at 12:00 IST. **11:12:** `lv6` (lv5 narrowed to golem groups outside the enemy's half, on rz12) is **N** locally as well: golem kills 1.69 to 2.81 a game, but captures 52.5 to 45.1, collected 1055 to 963, deaths +0.46 a game; the opponents collect more where our crews go. Golem crews in `pick_group` are closed (rows lv5, lv6; patches in `results/analysis/`). The rivals clear golems no differently (same distances, same health lost per hit; they spend more hits on them and still out-collect us elsewhere), so the golem gap follows from a wider gap on 02famine, 00split and 00quadrants (`docs/findings.md`, 'Golem groups'). **11:18:** after rz12 the collection gap sits on six maps (`docs/findings.md`, 'Where the gap is after rz12'): over 145 pinned games we collect 692 against 706, but 00ribs, 00eight, 00vault, 00quarry, 02crossing and 00crater (14 games) carry about 49 a panel game of it and we out-collect the rivals on the other 131. Next for t9: 02crossing's pure gem clusters (the rivals capture 42 a game against our 12.5, 13.5 against 0.5 in the middle, 8.5 in our half) and 00vault's middle gem groups; 00ribs, 00eight and 00crater are death maps (t10's factor). **11:44:** new panel `bcg` (those maps but 00ribs, 00eight and 00crater, plus 00expanse and 02famine, against procless, conqueror_of_openai, Jupiter, Rogue Lock Pickers and SALUTE TO TUNG, ranks 18-34), pinned as `bcgp`: main (rz12) won 2 of 50, collected 504 against 942 by r1000 and 171 against 261 already by r300, deaths 4.0 against 2.8 (`docs/findings.md`, 'The gap maps against teams 18-34'). Next for t9: farming speed from the opening, judged on `bcgp` by collected and captures; 00expanse (deaths 0.7 against 1.0, collected 750 against 948) is its cleanest map. In r300-700 about 220 more of our champion-rounds a game walk or wait empty-handed in our own half while the rivals farm the middle and our half (238 rounds a game there against our 67 in theirs): start from what those champions wait for. The t9 session ended at 11:50; main (rz12, v1107) is live. **13:40:** the t9 session resumed at 12:34 on that factor (`docs/findings.md`, 'Where the idle own-half time goes on bcg'). On 00quarry each side's outer gold group has a cluster on a bush tile, seen only from inside the bush; after killing the outer cluster our champion stands on its tile while the engine says the group is alive (359 champion-rounds a game to r1000 on bcgp, the rivals 52), and teammates wait beside it. Only 00quarry and 02harvest have camps on bush tiles. The 5-pick maps lose time to target churn mid-walk (14.5 switches a game away from a live target, 44% flip back), and 00vault to the wait at its 343-gem group. Target metric: gems collected by r600 on bcgp. `cm1` (walk into the bush when the group is up and unseen, `camp_fight.h`) gates from 13:34 on bcgp and b13p2 (rule in the cm1 row; b16p and b17p in t9's next turn). **14:35:** cm2 (walk churn: futility counted only near the group, a walk's target held at 1.5) is **N** on its local check (walk waste unchanged, captures 90%). cm1 passed what it played: on bcgp the outer-tile wait fell 359 to 35 champion-rounds a game and 00quarry collected by r600 rose 162 to 264, and the bcgp and b13p2 guards held (bcgp deaths +0.30, at the bar). Main became rz20 at 14:04 (t10), so the change goes on as `cm1r` (rz20 + cm1's `camp_fight.h`): bcgp from 14:22 against a fresh rz20 base `rz20_bcgp@bcgp`, then b13p2, b16p and b17p with rz20 bases that both sessions may use (rule in the cm1r row).
- **Night 10-28 (agent, 00:00-01:00 IST; bad maps, 00ribs first). Main is now cr3.** cr3 (cw1 + dm1 + hw1 + mr1; v968 on 10-27) was adopted as main and ladder bot at 00:50 (v974) on the user's call: under cw1 the ladder fell from 1973 to 1932 (rank 60; ranked 23 of 55 after v968's 13 of 20), and cr3 is at worst equal on b13p (23 vs 23 of 50, our deaths -0.9 per game). cw1 is now `bots/pool/cw1`. Bases of a variant on cr3: `cr3_b13p@b13p`, `cr3_b10p@b10p` and `cr3_brk@brkp` (its gate started 00:42 and waits for quota until 01:02; check `data/chain_c3.log`, then decode it with `bash tools/replay/decode_run.sh cr3_brk@brkp 3`). New panel `brk` / `brkp` (ten teams of ranks 40-58 on 00ribs, 00contest, 00crater, 00packs and 00eight, 20 games each; `results/panels/README.md`): cw1 26 of 100 (`main_brk@brk`, decoded). Fresh unpinned b13: `main_b13n@b13` 24 of 50 (cw1, not decoded; pin it when b13p is renewed). Findings (`docs/findings.md`, "00ribs opening, meetings and tank assist"): the 00ribs opening is lost in every game by r90-r120 because our arrivals wake the two elks one at a time, alone, and split over groups, and in any meeting at a camp our champion is the one who dies. tk1 (tank assist) was rejected by its rule but raised our 00ribs gems by 56%. hg1 and nf1 were built on cw1 and never gated: rebuild them on cr3 before testing. **Next (one factor, in a fresh chat):** the 00ribs opening: take the bottom elks together (converge on one strong camp, wake it with four or more of us, focus it), judged on brkp's 00ribs games against `cr3_brk@brkp`. Still queued by the user for later: the ranked 1000-0 loss to EggsAfter11AM on 02guardians and the unranked game against ha²t on 01elk_arena.
- **Late night 10-27 (agent, 23:00-24:00 IST; bad maps, 00ribs first).** Verdicts in `docs/experiments.md`: rv2, ha1, cr1, dm1 and cr3 rejected on the fresh panels (every child of cw1 lost on b10p by 6-11 wins, so cw1's b10p draw is likely lucky too); cg1 and cg2 (contested-group wait / join) rejected locally. Bad-map panel `bmp` (ten b11p/b12p teams on 00ribs, 00contest, 02guardians, 01elk_arena, 00crater; `results/panels/specs_bmp.txt`, base `cw1_bmp@bmp` 8 of 50, decoded `data/fights/cw1_bmp_bmp`), per map to r1000, us vs them: 00ribs collected 90 vs 738, deaths 14.9 vs 2.6; 00contest deaths 23.0 vs 5.2; 00crater collected 335 vs 934, deaths 14.8 vs 3.6; 01elk_arena 249 vs 520, deaths equal; 02guardians collected 605 vs 889 but tributed 4 vs 183 (a banking failure). Middle strong-camp wakes (`tools/replay/midwake.py`): ours stolen 44%, theirs 12%; second wakes equal. Ranked since 10-26 22:10 UTC (600 games, 51%): 00ribs 0/10, 01boss_battle 0/5, adgato_gemcombat1 0/5, 00packs 1/9, 00eight 1/8, 00contest 3/15, 00crater 3/12; the twelve worst maps 23/125. 00ribs on bmp: 117 of our 149 deaths are on the hill, median 30 rounds after entering, with 2.96 enemies and 0.75 allies within 6 (theirs 1.15 and 1.08); the rivals keep 2.94 champions on the hill (we 1.17) and go home at 51% health, mostly by recall (`go_home` recalls only with no enemy within 5 and none seen for 3 rounds). A trace (bda9c08a, r560-700) shows our arrivals splitting jobs (one tanks the elk alone from 94% to 28%), a lone first strike (`bot.cpp`, 'first strike in a lone 1v1') turning into 1 against 3, and a capturer standing idle beside a teammate's death. Next: decode the ten ranked 00ribs losses (downloaded with index in `data/replays/platform/rk_ribs`) with `tools/replay/pextract.py`; build a 00ribs panel against teams near our rating; test there one at a time: earlier recall home, regroup before entering the hill, no lone first strike in the middle, and cr3. Then the 02guardians banking failure. Ladder: rank 51 at 1965 (00:00 IST); main v969 live (11/20 since 22:50 IST), v968 = cr3 inactive (13/20 in its window; the user liked it): `cambc submissions activate 968` only on the user's word.
- **Night 10-27 (agent, from 20:10 IST; the user asked for deep thinking and good improvements).** Running: chain `data/plan_fs.txt` (cr1_b10p, then dm1 and cr3 on the fresh panels b13p and b10p; rules in their rows in `docs/experiments.md`). Results so far against cw1 on the fresh panels: rv2 b13p 26 vs 23 but b10p 36 vs 44 (D -8, gems -6.5%), so rv2 fails its rule; ha1 b13p 22 vs 23 (ha1_b10p skipped); cr1 b13p 24 vs 23. cr2 (cr1 + dm1 + hw1 + mr1) was replaced before its gates by **cr3 = dm1 + hw1 + mr1**, because rv2 costs farming and ha1 does nothing. Findings of the night (`docs/findings.md`, "Audit of cw1, gifted clears and 00ribs"): the audit build au18 of cw1 shows no engine errors and almost no missed attacks; 7.1% of our camp hits go to groups the enemy then captures (theirs 4.1%), up to 64% on 00ribs, where our whole team shuttles 130 steps a round trip to the bottom elk group and collects 0 gems by r300. Queued by the user (10-27 21:35 IST), after the 00ribs work: analyse the ranked 1000-0 loss to EggsAfter11AM on 02guardians and the unranked game against ha²t on 01elk_arena. Next: judge cr1, dm1 and cr3 with their rules (decode with `bash tools/replay/decode_run.sh RUN@PANEL 6`, `decoded.py gems`), adopt a passer with `tools/platform/adopt.sh`, and make sure main is submitted when the chain ends.
- **Evening 10-27 (agent; the user asked for deep thinking before any test):** tj1 (team fight: commit teammates to an enemy in contact when not outnumbered) is rejected: our multi-hitter rounds rose from 14.3 to 17.8 per game but the rivals' hits rose as much, and the death exchange fell 0.49 (`docs/experiments.md`). Two findings (`docs/findings.md`): (1) the death gap is the stunned deaths. The rivals land 21 stuns per game to our 9.5, mostly from Ryth, Tavi, Prism and Cassi; conversion per stun is equal; our own Ryth (ry1) added stuns without kills. (2) **cw1's base runs on b11p and b12p are a lucky draw** (first of 13 against its own children in wins and tributed; ordinary on bvp and bhp), worth 0.25 deaths, 0.5 in the death exchange and 4.6% tributed per game over the four panels. That is more than the guards most of today's rules used. dm1, fw2 and rv2 were rejected by margins inside that bias. Running now: null variants nl1 and nl2 (direction order permuted) on b11p and b12p (`data/plan_nl.txt`) to measure cw1's real level there. Next: if the nulls confirm, re-judge dm1, fw2 and rv2 from their decoded runs against the mean of cw1 and the nulls with their own rules, and rebuild any that passes from its row (the folders are deleted). hw1 and mr1 stay ready to gate.
- **Session 10-26 from 16:35 IST.** The patch watcher runs in the background (`bash tools/platform/patchwatch.sh 10 > data/patchwatch.log 2>&1`; restart it after a handoff). Check gates, judges and local runs with `bash tools/platform/procs.sh`. Commits stay local: never push (`CLAUDE.md`); read the teammate's work with `git fetch origin` and merge `origin/master` (nothing new at 16:50).
- **Ladder bot:** `rz9` (= `bots/main`) since 10-29 07:48 IST (version 1072; nm2 plus no striking dash at the top of the threat branch). Before it `nm2` (`bots/pool/nm2`) again from 10-29 04:31 IST (version 1060), and `lv1` (`bots/pool/lv1`) from 03:41 to 04:31 (version 1057; nm2 plus gold weight 0.1 from r300). Before it `nm2` since 10-28 23:54 IST (version 1034; sq2 plus Marcella in the 3-pick draft on gold-less maps). Before it `sq2` (`bots/pool/sq2`) since 10-28 18:21 IST (version 1009; cov1 plus company in the pick). Before it `cov1` since 10-28 17:14 IST (version 1004; go1 plus the cover fix), and before that `go1` since 10-28 06:27 IST (version 985; cr3 plus turn order, see the summary at the top). Before it `cr3` (`bots/pool/cr3`) from 10-28 00:50 IST (version 974; see the Night 10-28 bullet). Before it `cw1` (`bots/pool/cw1`), adopted at 05:38 IST on 10-27 (version 838): dh3 plus a fix of the gather crawl before big groups (`docs/ARCHITECTURE.md`, "Changes in cw1"): bvp 19 vs 16 and bhp 20 vs 20 of 50, gems collected by r1000 +5.4% over both panels, deaths equal. `dh3` is `bots/pool/dh3`. The exact bases of a variant on cw1 are `cw1_bvp@bvp` and `cw1_bhp@bhp` (both decoded in `data/fights`).
- **Afternoon 10-27 (agent; the user asked for postmortems of massacres and of the damage gap, then to keep working until midnight and fix the major issues):** postmortem in `results/analysis/postmortem_2026-10-27.md` (findings section "Massacres and the damage gap"): captures are equal, the gem gap is bags taken from our dead, 40 massacre games of 150 hold the losses, pack sightings carry the whole death gap, and the rivals deal about 30% more champion damage. Rejected since (rows in `docs/experiments.md`): pr2 (Prospector first), ja1 (join when ahead: more hits, fewer kills), vfs1 (Vesper shoots more: her damage +11%, team deaths +0.34 and gems 93-95%), ta1 (Tavi as the fifth pick: 1922 damage against Varg's 1498, team deaths +0.44), ou1 (no step-ins and no champion abilities when outnumbered: on b11p + b12p deaths +1.0 and kills -1.2 per game; stopped after two panels). Lesson: holding back in outnumbered spots gives up the kills made there; the rivals answer packs by fighting. Then rejected: fw2 (the flee step works as meant, but deaths 6.3 against 6.4 over the four panels) and pb1 (a pack's summed burst makes danger tiles: on b11p + b12p deaths +1.0, kills -1.1, tributed 84% of base; stopped after three panels). Mechanism probes (`docs/findings.md`, "Mechanism probes"; `tools/local/probe_lines.py`) confirmed that pb1, fw2, hw1 and mr1 act as written. **Next (the session ended at 16:12 with nothing running; main resubmitted as v935):** restart the patch watcher, then gate `hw1` (no help call while 3+ enemies stand within 6 of the caller) and after it `mr1` (Marcella skips her rooting spell at the top of the threat branch) on the four panels, one chain each. Both folders are built; their plan lines and rules are in their rows. Decode each run with `bash tools/replay/decode_run.sh RUN@PANEL 3` and judge with `decoded.py gems`, `decoded.py types` and `tools/replay/chain.py`. To skip a line of a plan that a chain is reading, overwrite its first character with `#` in place (same file, same length): `sed -i` replaces the file and the chain keeps reading the old one (fw2's and pb1's bhp panels ran that way).
- **Midday 10-27 (agent alone, from 10:35 IST):** pa1 R (outnumbered deaths 3.43 against 3.39; collected -5.7%), rv2 R on its b11p + b12p confirmation, ha1 R (holding off `bank_gems` at altars two enemies hold did not change the walks into them: 1.82 per game against 1.70). Seven pack-avoidance variants have now failed; the margin is lost in lopsided games (`docs/findings.md`, "Builds after the patch, and where the margin is lost": the 40 of 150 games with 6+ more deaths than the rivals hold 107% of the deficit). **Current factor: the first emblem.** After engine 2.0.0 cut Treasure to +10% gold the rivals moved to Prospector and Capture (Vesper Prospector 35%, Treasure 30%, Capture 19%); we buy Treasure first in 75-96%. `pr2` (Prospector first, same stat) gates on b11p, b12p, bvp, bhp (`data/chain_pr2.log`, rule in its row: gem-cluster gems by r600 +8%, collected by r1000 660+, gold and death guards). Next on the same factor: Capture first (`ce1`, not built), since the rivals' Capture-first Vespers collect 309 gems by r1000 against 254 (Prospector), 216 (Treasure) and our 144 (`tools/replay/firstemb.py`). **Fresh panel b13** (ten teams of ranks 41-77, 50 games): `main_b13@b13` 23 of 50 at 11:48, pinned as `b13p` (`results/panels/README.md`); use it to re-validate main and the last candidates before the lock. Rank 79 at 11:45 (requester rank in the quota reply).
- **Morning of 10-27 (agent alone, 05:40-10:05 IST):** six variants on cw1, none adopted (rows in `docs/experiments.md`): du1 (pairs in `pick_group`) R, os1 (opening stack) R locally, kb1 (wider berth around packs) R, rv1 and rv2 (carrier health reserve) N (every carrier metric moved our way, short of the bars), dm1 (death marks in `pick_group`) R on its b11p + b12p confirmation after passing on bvp + bhp. **Current factor: deaths outnumbered by two or more** (`tools/replay/packs.py`): 3.39 per game against the rivals' 1.13 over cw1's four pinned runs (bvp, bhp, b11p, b12p, 150 games, to r1000), which is the whole death gap (at even or better numbers we die 1.32 per game, they 2.21); the victims saw the pack about 19 rounds before (`docs/findings.md`, "Packs"). `pa1` (a pack of 3+ that outnumbers us by two ends the camp fight for a re-pick, and `pick_group` weighs danger squared) gated on all four panels (chain done 10:15, `data/chain_pa1.log`: bvp 12 of 50 against cw1's 19, bhp 18 against 20, b11p 7 of 25 against 12, b12p 7 against 9; all four runs decoded in `data/fights/pa1_*`); its verdict against the rule in its row of `docs/experiments.md` is still to be written (likely R: partial bvp numbers show outnumbered deaths 3.28 against 3.36, collected -39, tributed -47), then delete `bots/exp/pa1`. The exact bases on main are `cw1_bvp@bvp`, `cw1_bhp@bhp`, `cw1_b11p@b11p`, `cw1_b12p@b12p`, all decoded; a pinned panel replays the same games, but dm1 showed that a result on bvp + bhp alone does not carry over, so judge variants on all four. Ranked: 15 of our last 40 games won (10-27 09:20). Disk C: fell to 45 MB free at 10:30; on the user's request the agent deleted the match summaries older than 12 hours (`data/summaries` 20 GB to 2.6 GB; `fuel_events.py` re-downloads them), leaving 17 GB free. `data/runs` (13 GB, 83 old `multi-*` runs) is the next thing to prune; keep `multi-050951` (cw1's local base).
- **Rank 60** at 10-27 04:10 IST (68-69 the day before). Night findings (`docs/findings.md`, "Idle time and deaths near home"): 1.55 of our 1.84 extra deaths per game fall within 20 tiles of our own spawn, mostly champions caught on the way home by groups that outnumber them (00swirl, 00eight, 01gold_rush, 00stampede are the worst); rw1 (vault walk-out) and gk2/gk3 (boss_battle guard) were rejected.
- **Previous ladder bot:** `dh3`, adopted at 03:42 IST on 10-27 (version 831): cc2 plus dash routes over one-tile hole lines on the four maps where they cut the walk to the altar by 40+ steps (road_of_riches, shortcut, concentrated_wealth, fracture); identical to cc2 elsewhere (`docs/ARCHITECTURE.md`, "Changes in dh3"). On the new pinned panel `bhp` it won 20 of 50 against cc2's 10, tribute margin +290 per game on those maps; it was adopted although our deaths there rose 2.5 per game against the rule's 1.0 guard (theirs rose 2.8; the reasoning is in the dh3 row of `docs/experiments.md`). `cc2` is `bots/pool/cc2`.
- **Night of 10-27 (agent alone, user asleep, full freedom granted):** the user's losses analysed (`docs/findings.md`: "Hole maps", "Massacres in ranked games", "boss_battle: we never hit the guard", "Ranked record by map"). dh1 (holes everywhere) rejected, dh2 superseded, dh3 adopted. Next candidates, by ladder record: boss_battle 0 of 6 (we never hit the altar guard; `bots/exp/gk2` exempts it from the covered rule but kills it only at r818-r971 locally, so it needs the team to commit earlier), quarry 0 of 5 and vault 0 of 4 (we collect a third of the rivals' gems; cause not found yet), eight 1 of 7 and ribs 1 of 5 (massacres).
- **Before dh3:** `cc2` (= `bots/main` then), adopted at 00:05 IST on 10-27 (version 796). It is mw1 plus carrier caution: a champion with 30+ gems never engages and counts any threat as a lost fight (`docs/ARCHITECTURE.md`, "Changes in cc2"; `docs/lineage.md`). The previous ladder bot `mw1` (version 766, resubmitted by each gate up to 795) is in `bots/pool/mw1`, `hc2` in `bots/pool/hc2`. Rank 70 at 16:35 IST on 10-26.
- **10-26 results on the pinned panel b9p** (120 games per run, deterministic opponents): main1026h 33 wins, dq3 44 (accepted), js1 34, js2 29, dq4 41, hc1 39, hc2 43 (accepted), fpd3 40, mw1 47 (accepted, target metric flat), mb1 40 (rejected, deaths +15%), md1 42, fb1 48 (rejected by its rule: deaths did not fall, but gems collected rose 672 to 699), fb2 40; mb2 dropped after a local run. Unpinned main on b9 at 17:59: 42 (morning main 33). Rules and decoded numbers are in the rows of `docs/experiments.md`. The base for a variant on main on b9p is `mw1_b9p@b9p`.
- **New panel b10 (ranks 20-40, from 19:40):** all 21 eligible teams of ladder ranks 20-40, one 5-map window each, 105 games per run (`results/panels/specs_b10.txt`, README row). Main on it: `mw1_b10@b10` 29 of 105, deaths 843 vs 624, gems tributed 64.6k vs 95.5k. Pinned to that run as `b10p` (`specs_b10p.txt`): `mw1_b10@b10` is the exact base of every run on b10p. Its decoded analysis is in `data/analysis_b10/` (all readers). `sc1` (big dead groups shared among claimants) lost there, 27 of 105, and was rejected.
- **How we judge now (user, 10-26 22:50 and 23:10):** a variant's rule names the targeted factor's metric, a bar for it and guards that the other metrics hold; wins are recorded, not judged (opponents change bots fast). Tests run on the 5-team pinned panel `b11p` (25 games, about 5 match groups, so up to 10 gates an hour): Zarzorki, Sheeesh---, dromedaries, SSSA, Let's LARP again (ranks 23-39 at 18:10), pinned to `mw1_b10@b10`, whose 25 games are the exact base (7 wins). The base's 5 groups are logged as `mw1_b11p@b11p` (decoded in `data/fights/mw1_b11p_b11p`). Judge with `bash tools/platform/judge.sh NAME_b11p@b11p BASE_b11p@b11p`. The exact base of a variant on main (cc2) is `cc2_b11p@b11p` (7 wins, decoded in `data/fights/cc2_b11p_b11p`); `mw1_b11p@b11p` stays the base of variants on mw1. cc2's b11p run was the better of two picks (cc1, cc2) on those 25 games, and every variant judged against it since showed tributed 36-50 lower, so it is a lucky base: judge variants on b11p and the second panel `b12p` together. **b12p** (from 10-27 00:45): Oldenkamp (rank 37), ひななー (25), FürFortnite (40), test4 (32), Jupiter (24), five windows of b10p (`results/panels/specs_b12p.txt`); bases `mw1_b12p@b12p` (7 of 25) and `cc2_b12p@b12p` (8 of 25), both decoded. We were rank 71 at 00:50.
- **Current factor (from 10-27 01:00): Marcella's build and deaths.** Decoded at r600, our Marcella holds Power-focus 0.94-1.42 and Treasure 0.83-0.95 emblems with 1756-1800 max health and dies 1.89 (b11p) and 1.19 (b12p) times per game by r1000; the rivals' Marcella holds Bruiser-focus 2.35-2.41 and Bruiser-health 0.77-1.65 emblems, 2732-2817 max health, and dies 0.22-0.62 times. In the 13 b12p games we lose with her on both runs, her max health at r600 is 1423 against their 2854: much of the gap is gold (fewer items), not only the order. `mc1` (her build counts Bruiser's strength and can take Bruiser of health; row in `docs/experiments.md`) gates on b12p and b11p from 01:05 (`data/chain_b16.log`); judges in `data/judge_mc1b12.txt`, `data/judge_mc1b11.txt` and the Marcella-only pairings `data/paired_mc1b1{2,1}_marc.txt` (`paired.py --type marcella`). Next lever if the build holds: her capture priority (`capture_priority` gives her 4; she gets +2 gold per gem she tributes).
- **Previous factor (10-26 23:00 to 10-27 01:00): gems lost on death by carriers** (`docs/findings.md`, "Gems lost on death: carriers"). On b11p's base (mw1) we lost 141 gems per game on death by r1000 against the rivals' 33; per 1000 rounds alive our champions with 30-59 / 60+ gems died 1.97 / 3.70 times, the rivals' 0.50 / 0.63. Results on b11p (rows in `docs/experiments.md`): `kl1` (cancel enemy tributes) and `sg1` (bank on sight) rejected, `at1` (tribute at every altar passed) not accepted (banks +40 but loses as much on death), `cc1` (no fights with 50+ gems) passed with -32, `cc2` (the same at 30+) passed with -60 and is main. cc2 still dies 1.35 / 1.46 times per 1000 rounds with 30-59 / 60+ gems (rivals 0.50 / 0.18) and lands 14 fewer hit rounds per game. Next (user, 10-27 00:05): replace the fixed gem bar by a rule derived from the factors that decide a death in contact. Decoded on b10 + b9p (scratch `factors.py`, `riskfit.py`, `cdeath.py`, `contact.py`): the bag itself barely changes our risk; what decides it is the team hp share near (own hp plus allies within 5 over enemies within 6), own health, enemies within 4 and hitting; half our carrier deaths start in a favourable contact that turns. The fitted model is `tools/replay/riskfit.py`. Graded rules built on it lost to cc2's fixed bar on b11p (gems lost on death by r1000, cc2 80): `rk1` (leave when P x stake exceeds the gain) 110, `rk2` (lower threshold) 118, `rk3` (risk budget) 94; `ca1` (cc2 + at1) 84 and `cc3` (bar 15) 89 were rejected too. Turn-by-turn graded rules flip between staying and leaving where the fixed bar commits, and letting carriers fight raises fighting team-wide. cc2's confirmation on b12p could not confirm the gain (lost 42 to 41: mw1 loses only 42 there) but every guard moved our way (deaths -0.7, tributed +2.8%), so cc2 stays main. Enemy altar locks: 4.4 lock-hit episodes per game on b11p, 73% end in a tribute, about 6 gems per game lost, so a lock-aware bank is not worth it.
- **Repeat deaths (factor 20:20-23:00):** `kz2` (kill zones, 300-round memory) cut our deaths by r1000 on b10p (-0.65 per game, gems held) but on b9p gems collected fell 672 to 627 (-6.7%) with deaths 5.7 to 5.4: it gives up groups near the marks, and the rivals collect them. Rejected by the factor rule's 2% guard; `kz1` on b9p is the last run of this factor (`data/judge_kz1b9.txt`). (`docs/findings.md`, "Repeat deaths against ranks 20-40"). On b10 the whole death gap sits in 17 massacre games (21.2 deaths per game; in the other 88 we die 5.5 times per game and they 6.5). 3.37 of our 6.45 deaths per game fall within 6 tiles and 150 rounds of a teammate's death (rivals 2.13 of 4.69), and 1.19 per game come over 10 rounds later with the victim outnumbered by 2+ (rivals 0.34). Alone against 2+ enemies at 3-6 tiles the rivals step away more (29-36% of rounds vs 17-27%) and die 3-4 times less. Results on b10p (base `mw1_b10@b10`, 29 of 105): `ob1` (back off when alone against 2+) 26, rejected (it stepped away far more, but deaths by r1000 did not move); `kz1` (a shared kill-zone mark in bytes 5-6 that `pick_group` avoids for 150 rounds) 31, not accepted by its rule (deaths by r1000 -0.36 per game against a 0.4 bar, gems collected -1.2%): it cut returns within 60 rounds of a teammate's death, not those 61-150 rounds later. `kz2` (kz1 with a 300-round memory) gates from 21:55 (`data/chain_kz2.log`, judge `data/judge_kz2.txt`). `obkz` (ob1 + kz1) is held. Target metric: our deaths per game by r1000 (paired, `paired.py` stats), guard gems collected by r1000; readers `tools/replay/repeat.py` and `alone.py`. `kl1` (cancel enemy tributes with a lock) is deferred to a later quota window. Decoding note: with a decode, a local run and extra extractions at once, Git Bash failed to start processes ("fork: Permission denied") and `judge.sh` decoded 0 games; decoding now runs through `tools/replay/pextract.py` (native processes), which fixed that; `tools/platform/group.py` no longer crashes when a rate-limited summary download leaves no file (that froze the gate and judge polls of kz2_b9p at 22:30).
- **Altar locks (answered 20:00):** our lock code sees and breaks enemy locks (5 hits). What loses bags is the channel length: a channel takes bag / 10 turns, and an enemy lock placed during it cancels it. Our own lock does not protect the altar: the enemy can lock an altar that holds ours (probe sl1d vs lkc, `docs/MECHANICS.md` section 9). On b9p our broken channels leave 74 gems per game unbanked against the rivals' 41 (49 of ours with no death and no enemy cast, so mostly locks). `bots/exp/lkc` (main that locks any altar where the enemy tributes) is the local opponent for channel tests.
- **Gate timing:** a b9p gate plays its 120 games in about 11 minutes; decoding them is the slow part (`judge.sh` now decodes with 11 jobs and polls every 20 s). Two b9p gates use 48 of the 50 match groups an hour; a b10p gate uses 21, so two fit in one quota window (`match-groups quota --json` gives `used` and `resetsAt`). A gate started with the quota used up waits silently in `gate.sh` until the reset.
- **Previous factor: captures in the middle (mw1 accepted; mb1, mb2, md1 rejected).** After hc2 (decoded, per game by r1000, us vs the rivals): captures 41.0 vs 43.0, of them middle 8.2 vs 9.9 (189 vs 235 gems); gems collected 673 vs 777, tributed 532 vs 656, our deaths 5.6. Holding is solved (holds left before the capture 5.8 per game vs the rivals' 8.0). What is left is arrival: whoever was nearer when a middle group came up hits it first, the rivals keep more champions near the middle (1.37 within 10 tiles at that moment vs our 1.18; the top 12 1.59) and spend about 5 points less of their time in their own half (`docs/findings.md`, "The middle race is decided by position"). Next variant: get champions near middle groups when they come up, in `pick_group` (`targets.h`): a respawning group's wait counts x4 per round on our side and x2 on contested ones, and there is no middle bonus since ge4 (`mid_push = false`). Target metrics: `python -I tools/replay/race.py 1000 data/fights/RUN_b9p` (champions within 10 when a middle group comes up, middle first hits) and `decoded.py captures` (middle), then gems collected by r1000; write the rule before the gate.
- **How to test** (one variant at a time): build `bots/exp/NAME` on main (`tools/variant/mkvar.py`), a local 140-game crash check (`python -I tools/local/multi.py exp/NAME --pool pool/cand1,pool/cp3 --maps <35 maps> --jobs 11`; local wins do not judge), the row and its rule in `docs/experiments.md` (`tools/variant/addrow.py`), then a gate with a one-line plan (`exp/NAME NAME_b9p b9p`) through `bash tools/platform/gatechain.sh PLAN > data/chainN.log 2>&1` and the judge in the background (`bash tools/platform/judge.sh NAME_b9p hc2_b9p > data/judge_NAME.txt 2>&1`). Afterwards make sure main is the submitted bot (`powershell -File tools/cambc.ps1 submit main`, or `adopt.sh` for a winner).
- **Panel freshness:** b9p replays the opponents' bots of 10-26 morning. Before the final pick for the Sprint 3 lock, run main unpinned on b9 and re-pin from that run (`tools/platform/pin.py RUN@PANEL NAME`, `results/panels/README.md`), or build a stronger panel from the current ladder (`tools/platform/mkpanel.py`, `eligible.py`).
- **Teammate (Michael):** his ML work came in from `origin/master` on 10-26 (merge commit 74992bc): `ml/` (`ml/README.md`), his rows in the section "ML variants on hb4" of `docs/experiments.md`, findings bullets, `results/analysis/diagnosis_2026-10-27.md`. All of it was built on hb4 and tested locally. His one positive result, fpr (a learned P(our team captures the group) multiplying `pick_group`'s best scores), lost on b9p when ported onto dq3 (fpd3: 40 vs 44). He submitted nothing to the platform (all 20 recent submissions are ours).
- **Other candidates in `bots/exp/`** (gitignored, none gated on 2.0.0; the folders of finished variants were deleted on 10-27 01:05, `ba2` and `gk1` with them): `mc1` (gating), `lkc` (the local lock opponent), `pr1` (Prospector instead of Treasure; an item change, platform only), `vs1` (Vesper keeps shooting in the kite branch; held back after vh1m raised her deaths 25%), and `cv1` (from the patch morning, no matching row: check `diff -r bots/exp/cv1/src bots/pool/m4/src` before using or deleting it).
- **Next deadline:** Sprint 3 locks Sat 31 Oct 23:59 GMT (Sun 1 Nov 05:29 IST). The bot submitted at that moment is the tournament bot. Season ends 18 Nov.
- **Event:** cambc2026a, https://2026a.battlecode.co.uk, account Ajay_2705 (team "Velvet Tributers", id `118dbffc-87ec-48a6-ac9c-dc1e371ba364`). The ladder lists 25 teams a page: `powershell -File tools/cambc.ps1 ladder --page 3 --json`. The unranked quota is 50 match groups an hour (a b9p gate uses 24).
- **Branch:** `batch-loop-2026-10-24` (local; `master` holds Michael's work).

## Next steps (in order of expected value)

Each step names the measured gap, where to change the code and how to judge it. Measure with
`bash tools/replay/decode_run.sh RUN@PANEL` then `python -I tools/replay/decoded.py CMD data/fights/RUN_PANEL` (numbers
below are cp3 on b56, 70 decoded games, per game, us vs the rivals; full tables in `docs/findings.md`).

0000. **Middle arrival (the current factor, from 10-26 16:45).** Target: champions within 10 tiles of a middle group when it comes up (`tools/replay/race.py`, averaged over the captured middle lives; hc2_b9p: 1.21 against the rivals' 1.37, the top 12 1.59; middle first hits 8.1 against 9.4 per game), then middle captures (`decoded.py captures`, 8.2 against 9.9) and gems collected by r1000 (673 against 777). Levers in `pick_group` (`targets.h`), one at a time: (a) the respawn wait of middle groups (now x4 per round on our side, x2 contested) so that a champion with nothing better near goes to a middle group about to come up; (b) a middle bonus again (removed by ge4 on 10-24, when collection by r300 was the gap; Michael's op2 removing it on hb4 was neutral locally). Gate each on b9p against `hc2_b9p@b9p`.
000. **Gold income (the factor from 10-26 11:00 to 16:00; js1 and js2 rejected, so the build lever is open).** Target: team gold at r300 and r600 (`decoded.py gold`) level with b9's, then towards the top 12 (5-champion teams r300 1424-1541, r600 3682-4039; we 1055 and 2684), without losing gems. Two levers, one at a time: (a) target choice: the gold weight in the pick is ruled out (gw2 and gw3 rejected at 13:00: they buy gold with gems, and the rivals take the gem clusters we leave); what remains there is the opening (our Vesper starts on an elk in 46% of games, the top 12's in 21-24%); (b) clearing speed through the build, now on the platform (js1: Jungle of the main stat second; js2: js1 plus one Durability only for strength users; target `decoded.py champs` camp damage per hitting round, Vesper 93 against the top 12's 127-133, which at equal strength shards is the same damage, so the build and the gold decide it). Further build differences seen in `docs/findings.md` and the emblem orders (`tools/replay/emblemorder.py`): the stronger teams' melee champions often take Treasure of health first (top 12 Heart of Ruin 48-52%, Vendetta 38-46%), and our Heart of Ruin completes its first emblem at r374 against their r275-331. Kill gold (100 a kill) follows deaths. Run every test on a pinned panel (`b9p`) so main1026h is the exact base.
00. **Sprint 3 patch day** (notes in `docs/MECHANICS.md` section 0; `tools/platform/patchwatch.sh` exits when PyPI or the platform engine changes). Steps 1 to 4b were done on 10-26 between 04:40 and 07:50 (SDK 4.0.0 in the repo, engine probe, decoder item list and visualiser for 2.0.0, crash check, wf1's fuel fix, main submitted as version 734). Open: step 5 (items) and step 6 (draft). Kept for the next patch:
    1. `python -m pip install -U cambc`, then `cambc init SCRATCH --yes` in an empty scratch folder (rehearsed on 10-26 with 3.0.5: it writes `sdk/`, `cmake/`, `maps/` with all platform maps, starter bots and `cambc.toml`). Copy its `sdk/`, `cmake/` and `maps/` over ours, set `sdk_version` in `cambc.toml` to the new version, and check with `git status` that nothing else changed.
    2. Build `main`; fix compile errors (new item enum names). Platform builds use the platform's SDK, so a submission that compiles locally is the check.
    3. Rebuild and run the engine probe (`tools/local/engine_probe.patch` on a copy of main as `exp/ps1`; `cambc run exp/ps1 exp/ps1 --map 00ambush --rounds 40 --release -o DIR`), then `python -I tools/local/engine_probe.py DIR/*.repl26a` prints the champion, settings and item tables and the item list. Update `docs/MECHANICS.md` sections 6, 7, 9, 10, 11 with [engine] values and add the item list to `tools/replay/decoded.py` `ITEMS` (keyed by engine; `items` stops on an engine it has no list for).
    3b. Replay decoding: `python -I tools/replay/vis_assets.py NEW_REPLAY` puts the new visualiser in `data/vis/<engine>/` (older replays keep the flat `data/vis/`). Decode one new platform game with `node tools/replay/rounds_extract.mjs DIR REPLAY` and check that its meta line names the new engine and that moves, attacks, casts, tributes and items appear (step kinds in `rounds_extract.mjs` `KIND` may change).
    4. Quick pool crash check of main, submit main, and start a fresh base run on b8 (results from before the patch do not carry over).
    4b. Submit main as soon as the platform runs the new engine, even before the checks above finish: `sdk_champion_items` writes one count per item type with no length, so a binary built for 42 item types would overrun its buffer if the platform kept running it on an engine with more.
    5. Items: Treasure gives 10% now, and Greed (25 shards for 35 shards of stats), Monster (15% camp damage), Prospector, Tribute and Capture are new options; `shop.h` buys Treasure first. Estimates from b8 are in `docs/findings.md`, "The Sprint 3 items against our b8 economy". Prospector turned out to raise only the cluster camps of a group (probe pp0), which makes it about +40 gems and -212 gold per game against Treasure, and none of the top 12 teams buys any new item yet. `exp/pr1` (Prospector in place of Treasure, 356/420 locally against main's 359) is built but not gated. Next candidates: a second passive (Capture or Tribute), then Greed against Power. Judge them on the platform (local runs do not judge items).
    6. Draft after the nerfs (Vesper base strength 45, Heart of Ruin focus growth 10) and buffs (Varg base strength 45).
0. **plan9 verdicts (b8, the stronger panel).** Adopt each variant that passes its written rule. If two or more pass, gate their combination against a fresh main run (b8) before adopting it. Then measure the b8 gaps against the stronger teams (`decoded.py types|items|channels|starts|shots`) and pick the largest for plan10; `exp/kd1fz` (rt1 + kd1 on main) is a ready candidate.
0b. **Fuel in fights** (measured 10-25 evening): deaths after our own fuel exhaustion were 0.45-1.12 per game vs the rivals' 0.03-0.14; fz1 (now in main) fixed the two largest costs. The contact turns that still run out (pf21, per 32 games: pick 10, camp-fight choice 7, post-turn step 6, retreat 4) are the next exact targets; measure with the probe (`tools/local/fuel_probe.patch`, `fuel_probe.py`) and judge on the platform with `decoded.py fuel`.
1. **Heart of Ruin is built too thin.** At r600 it has 1184 max health vs the rivals' 1700 and dies 1.79 times per game by r1000 vs 1.27 (champion damage 3032 vs 3739). cp3's item formula (`shop.h`) gives it Power-focus because focus growth 12 looks big against its focus, but Heart of Ruin trades blows in melee; the rivals build it Bruiser-focus, Treasure-focus and Jungle. Make the formula count health for melee front-liners (or use Bruiser for them, as before sp1). Judge by `decoded.py types` (deaths, damage) and `items`.
2. **Vendetta still does little.** Champion damage 2972 vs 4317 per game, gems 91 vs 168, hit-round share 0.029 vs 0.041, hit rate at 2-3 tiles 0.16 vs 0.23. Her kills reset all cooldowns: chain dash and attack reset after a kill. Code: `bot.cpp` attack on sight (cp3 dash-in) and the pvp step. Judge by `decoded.py types`.
3. **Big tributes break less than thought.** The 61% figure counted game-ending tributes as breaks (`docs/findings.md`, "Tribute channels without game-end tributes"). Corrected: bags over 100 complete 78% (rivals 94%), about 47 gems per game lost. The bigger difference is that the rivals tribute small bags more often (21 vs 13 tributes of 50 gems or less per game). The worst case is boss_battle, where a bag of 3300 gems never reaches the guarded altar (step 6). Judge by `decoded.py channels`. Remeasured for cand1 on b3456 (main1025g, `docs/findings.md`, last section): bags over 100 complete 63% vs 88%, channels break 5 times as often with an enemy within 10 of the altar, and we carry 128 vs 75 unbanked gems at round 1000 (tributed 511 vs 588 with collection equal). After fuel this is the largest score gap.
4. **Carriers still lose bags.** By r1000 we lose 68 gems on death (rivals 31) and carry 117 at any time (87). Order-quantity banking (`bot.cpp`, "Order quantity") uses a fitted trip overhead x3 from one panel; fit it on b56 instead, and check the hazard term `h` against `decoded.py risk`.
5. **Centre groups on b5/b34 maps.** cp3 lost elk_arena (576-648; dr3 won 1008-108), contest and corridors that dr3 won. ge4 removed the mid-push x2 (`targets.h`); test restoring it inside cp3 as one variant, on b56 + b34.
6. **Maps every version loses:** boss_battle (whoever kills the guard monolith beside the altar first owns the only altar; HouseOfCoders did it by r550-700), hooks (4v4 centre fight, 0-1012), road_of_riches and gemfight (rivals cross hole lines with dashes; our routing cannot, and gd1's dash routing failed locally because champions without a dash split off), shortcut (we collect 398 vs 1161 by r1000), contest and eight (5-stacks).
7. **Draft:** we field Varg where the rivals field Ryth or Marcella; Varg deals the least champion damage of ours (2411 per game) and dies 1.74 times. Only the platform can judge a draft change.

Method for every step: one change at a time on `main`, local quick pool as a breakage filter (floor about 165/240), then one combined gate on `b56` (90 games, `tools/platform/gatechain.sh`) with a fresh base run of main in the same session, compared with `rcmp.py` and the decoded metric. 50-game win counts move by about 3 wins from chaos alone (`docs/findings.md`, "Platform noise"), so a change needs its metric to move, not only its wins.

## Mistakes to avoid (from 10-24/25)

- Judging variants on 50-game win counts: near-identical bots differ by about 3 wins from chaos alone. Use decoded continuous metrics and the always-lost games.
- Winner's curse: dr3 was picked as the best of about 40 variants on b3/b4, so its 28/50 there was inflated, and later candidates were judged against it on the same games. Compare on a fresh panel, with a fresh base run.
- Comparing with old base runs: opponents change bots (dr3's evening b5 score of 23 reproduced only 19 of 50 game scores 9 hours later and became 21).
- Building before checking the whole flow: an hour went into dash routing over holes (gd1) before checking what happens to champions without a dash.
- Deleting variant folders before their platform verdict, then rebuilding them.
- Hunting map by map before measuring where the gap is overall: the biggest gap (rival champions land 40% more hits) was found late.
- Process control in Git Bash: `ps | grep` shows only `/usr/bin/bash`, so a kill matched nothing and two gate chains ran at once (their results are void). Use `bash tools/platform/procs.sh` (it reads `/proc/PID/cmdline`).
- `rm -rf data/runs/multi-*` while a local run was writing there: it lost most of that run.
- Editing bot code through shell and Python string escapes: `'\n'` became a real newline and broke three builds. Edit files directly, then build.
- Starting a long chain without checking the platform: on 10-25 the cambc login was lost mid-chain (gates then fail at the submit), and the unranked quota of 50 match groups an hour stopped plan7 after one gate. Before a chain, run `powershell -File tools/cambc.ps1 match-groups quota --json` (it needs the login, and shows `used` and `resetsAt`), and size the plan to the quota.
- Printing in fight turns: one log line with float formatting cost 37.6k fuel and made fight turns run out. Keep prints out of turns that can fight.

## History

### 10-26 day: engine 2.0.0, panels b9 and b9p (the "Now" notes of that day)

- **Handoff 10-26 14:50 IST.** Chain plan11 (`data/chain11.log`) runs dq4 on b9p (since 14:21), then hc1 and hc2 (hold-capture variants on dq3; rows and rules in `docs/experiments.md`, cause in `docs/findings.md` "Captures given up on the tile"). js1 rejected. js2's judge writes `data/judge_js2.txt`; the dqjs2 plan line is commented out, so append `exp/dqjs2 dqjs2_b9p b9p` to `data/plan11.txt` only if js2 passes its rule. Judge dq4, hc1 and hc2 against dq3_b9p@b9p (`rcmp.py dq3_b9p@b9p RUN@b9p`, decode, `decoded.py holds|captures|gems`). When the chain is idle, adopt dq3 (or a passing variant built on it) with `bash tools/platform/adopt.sh dq3 m4` and make sure main is submitted. Local hc runs (`data/runs/multi-141836`, `multi-142454`, the second with kept replays to delete) were mixed by map and judge nothing.

- **Teammate's ML work (Michael), merged from `master` on 10-26:** `ml/` (see `ml/README.md`) and the section "ML variants on hb4" in `docs/experiments.md` (fq1-fq5, rf1-rf7, op1-op4, bk4, bk5, fpr1-fpr5). All of it was built on hb4 and tested locally only. The one positive result is `fpr`: a small MLP trained on 261k platform capture attempts gives P(our team captures the group), and `pick_group` multiplies the scores of its top 8 live-camp groups by it (fpr5: 391 vs hb4's 384 in 560 local games, captures +13%, deaths -24%). It targets our current gap (captures), so it gets one b9p gate on dq3: build with `python -I ml/bot/make_fpr_variant.py BASE exp/NAME`, which stops where the base differs from hb4 at a patch point (then port that part by hand).
- **Rank 61 at 13:15 IST on 10-26** (67 at 11:48, 71 at 10:00, 81 at 07:45).
- **dq3 accepted (13:45), not yet adopted:** on the pinned panel b9p it won 44 of 120 against main1026h's 33 on the same games; 4-pick maps 11 of 26 (main 6) with our deaths by r1000 7.08 against 9.69, 5-pick 23 of 73 (17), 3-pick identical (10 of 21). It drafts Heart of Ruin, Vesper, Marcella, Vendetta, Varg on 4- and 5-pick maps (the 4-pick team drops Varg for Marcella). Adoption waits until the chain is idle (`adopt.sh` refuses during a gate): `bash tools/platform/adopt.sh dq3 m4`, unless dqjs2 (dq3 + js2) or dq4 (dq3 with Ryth as the fifth pick, the top 12's commonest 5-pick team) pass on top of it first; both are queued in plan11 with dq3_b9p as their exact base.
- **Pinned panels (new, CLI 4.0.0).** `results/panels/specs_b9p.txt` pins the b9 opponents to the bots they played in main1026h_b9@b9 (`match-groups create --source-group`, a fourth spec field in `gate.sh`). Games are deterministic, so main1026h is the exact base of every b9p run: all 120 games count and no base re-runs are needed (`docs/WORKFLOW.md`, `results/panels/README.md`). Pin checked at 12:19: main replaying main1026g's smurphy group, pinned to it, repeated all five games exactly although smurphy had changed bots since.
- **plan11 on b9** (`data/plan11.txt`, log `data/chain11.log`): main1026f 40/120, kd1m 42, bz1m 47, vh1m 42, main1026g 31, dq2m 42, main1026h 33, gw2 29, gw3 30, main1026i 30; then on b9p dq3 44 (accepted), js1 (running since 13:24), js2, dqjs2, dq4. Rejected by their written rules: kd1m, bz1m, vh1m, dq2m, gw2, gw3 (and gw1 without a gate).
- **Gold is the current factor.** The pick weight is ruled out as a lever: on the 60 games of the 6 b9 opponents that kept their bots between main1026h and main1026i, gw2 (gold counts as a gem before r400) raised team gold at r600 10% and gw3 15%, but collected 5-6% fewer gems by r600 while the rivals collected 9-11% more, with 13 and 15 wins against main's 16. The build is the remaining lever (`docs/findings.md`, "The gold gap is items held and starts in the opening"): at equal strength shards our camp damage per round equals the top 12's, and their Vesper holds 16.5 strength shards on average in her hitting rounds to r600 against our 7.4 (at r600 26-32 strength and 12.5-13 health against our 13.4 and 9.4). **js1** (Jungle of the main stat as the second emblem) and **js2** (js1, and strength users take one Durability emblem only, then Bruiser or Power of the main stat, as the top 12's Vesper does) go to b9p after dq3, each with its rule in `docs/experiments.md`. The gap opens before r100 (team gold at r50 / r100: ours 106 / 260, top 12 147-154 / 355-374): our Vesper's first target is an elk in 46% of games (top 12 21-24%) and her first camp hit comes at r19 (r12-14); gw2 fixed that but paid in gems.
- **Patch notes on the site** (`docs/reference/patch_notes_2_0_0.md`, revision 28, published 10-26 04:59 IST) match `docs/MECHANICS.md` on every number. Hunter is +50 gold per kill (the first notes said 100; Discord settled on 50 at 04:07), which engine 2.0.0 already plays. We never buy Hunter.
- `decoded.py gold` (team gold by round and team size, camp kills by type) and `decoded.py champs` (per champion type: camp gold, kill gold, captures, camp hits, camp damage per hitting round) are the gold metrics.

- **Ladder bot:** `m4` (= `bots/main`), submitted as version 734 at 07:50 IST on 10-26. It is `fd2z` (`bots/pool/fd2z`, versions 723-733: cand1 plus the audit and fuel line cand6, fd2's flee dash, fz1's fight-turn fuel fixes and gs1's per-shard growth from the engine; `docs/ARCHITECTURE.md`, "Changes in fd2z") plus wf1 (exact fuel fix: each item type's shard weight read once; SDK 4.0.0's 84 item types had doubled `wealth_of`) and ag4 (altar guards as a set of groups, for 02guardians). 70-map quick pool: 358/420 (fd2z 359), 0 bot faults, turns out of fuel after round 3 386 (fd2z 934). The previous ladder bot `cand1` (version 712) is in `bots/pool/cand1`.
- **Engine 2.0.0 (Sprint 3) everywhere:** on the platform since about 04:20 IST, cambc 4.0.0 on PyPI since 06:05; the repo's `sdk/` and `cambc.toml` are 4.0.0 (commit 54648e0), so local runs play 2.0.0 too. Engine tables, the new items and the measured Prospector rule (cluster camps only) are in `docs/MECHANICS.md` sections 0, 10 and 11.
- **Rank 81 (rating 1853) at 07:45** (history), down from 59 (1899) at 01:00. Ranked games since the patch: 05:30-06:30 IST 5 of 20 (version 732, built on SDK 3.0.5, playing engine 2.0.0; blowouts with 22-45 deaths on 01hooks, 00oasis and 00vault), 06:30-07:30 17 of 30 and 07:30-07:50 7 of 15 (version 733, SDK 4.0.0). 60 of the 65 games had us on side b (26 won). On 01hooks we banked 0 gems in all three games (22, 45 and 24 deaths, almost all with an empty bag), while locally we win it 6 of 6 against the pool.
- **The top 12 teams on 2.0.0** (66 ranked games of theirs, 05:00-07:30 IST, both sides decoded in `data/fights/top12_20`, fetched with `tools/replay/teamdl.py`): no champion on either side holds any of the seven new item families at the end of a game. Builds are still Treasure first, then Bruiser of the main stat and of health.
- **plan11 started at 08:00** on b9 (the 12 b8 teams, ranks 17-57 that morning, on the 70-map pool; 120 games each). kd1m, bz1m and vh1m are kd1fz, bz1 and vh1 rebased on m4.
- **plan8 verdict (b3456, 10-25 21:00 to 10-26 01:52):** main1025g 77/140, cand6 70, fd2 78, rt1 71, kd1 73, fz1 67, main1025h 78. `sandwich.py` dropped :3, DOOMSDAY and HouseOfCoders (their results changed between the two main runs). On the other 95 games: main 48, cand6 41, fd2 49, rt1 40, kd1 44, fz1 41. By the rules written before the results: cand6 alone rejected (-7), fd2 (cand6 + flee dash) passed (+8 against cand6, +1 against main), fz1 passed (+0 against cand6; deaths after our own fuel run-out 0.00 vs 0.29 per game), rt1 rejected (-8), kd1 passed only against rt1. Adopted: fd2 + fz1 = fd2z. Paired decoded games against main (`paired.py --drop`): fd2 margin +18 per game, our deaths -0.8, theirs +0.7. `exp/kd1fz` (= main + rt1 + kd1, best paired margin +36 +- 50) is kept as a candidate.
- **Panel b8 (built 10-26 01:00 from the ladder; we were 59 at 1899):** 12 teams from ranks 18-40 (ratings 1958-2101), 120 games, and bb8, the same teams on boss_battle + 4 maps (60 games): `results/panels/README.md`.
- **First 2.0.0 ranked games** (04:20-05:00 IST, between lower-ranked teams): every team checked drafts exactly as on 1.0.3, the platform's champion numbers did not change, no bot faults in 12 summaries.
- **plan9 stopped at the engine change** (10-26 04:30): main1026a 29/120, vi1 31, bh1 26, ro1 27, as1 30 on b8 (engine 1.0.3), all four rejected by their written rules against main1026a (no closing main run; rows in `docs/experiments.md`). main1026b's 120 games straddle the engine change and are not used. dq2, ba2 and gk1 (plan9) were not run; plan10 became plan11 on 2.0.0.
- **Sprint 2 entry:** `cp3` (`bots/pool/cp3`), version 691 at 03:30 IST on 10-25, before that lock.
- **Next deadline:** Sprint 3 locks Sat 31 Oct 23:59 GMT (Sun 1 Nov 05:29 IST). The bot submitted at that moment is the tournament bot. Season ends 18 Nov.
- **Event:** cambc2026a, https://2026a.battlecode.co.uk, account Ajay_2705 (team "Velvet Tributers", id `118dbffc-87ec-48a6-ac9c-dc1e371ba364`). Rank 71 (rating 1873) at 10:00 on 10-26 (81 at 07:45, 59 and 1899 at 01:00; rating moves while test bots play ranked games during gates). The ladder lists 25 teams a page: `powershell -File tools/cambc.ps1 ladder --page 3 --json`.
- **Branch:** the work of 10-24/25 is on `batch-loop-2026-10-24` (not merged into `master`).

### 10-25 afternoon to 10-26 night: audit, fuel, plan4-plan8

- **plan4 (b56, 10-25 afternoon):** cand3 40 vs main1025d 49 (an opponent changed bots during the run; on the same opponent versions -2, so it continued as cand4 and then cand6); cand2 48 vs 49, rejected.
- **Audit (10-25 evening, `docs/findings.md`, "Code audit", third pass):** `exp/cand6` = cand3 + exact fuel speed-ups (cand4) + fixes for every engine error the audit builds still caught + two opening-turn fuel fixes. Its audit builds (au15-au17, au17 with fd2's flee dash) had 0 caught engine errors and 0 bot errors in 480 local games; turns out of fuel: 0.85 per game after round 5.
- **Fuel in fights (10-25 evening, `docs/findings.md`, "Deaths, fight starts and fuel in fights"):** the largest single cause of our death gap found then. On b56 and b3456 our champions died within 5 rounds after their own turn ran out of fuel 0.45-1.12 times per game; the rivals 0.03-0.14. The probe pf20 found the big-hit "H" log line (37.6k fuel a line) and the fight simulator's vector growth; fz1 fixed both.
- **Platform runs (10-25 evening):** plan5 stopped after its first run when the cambc login was lost; plan7 stopped on the new unranked quota of 50 match groups an hour (HTTP 429). plan8 then ran overnight (verdict under "Now").

### Night of 10-24/25: gems, fights, final pick (batches b5, b6)

- **Gem phase (18:50-22:15, team decision: only gem collection until matched).** On b5 dr3 collected 108 gems by r300 vs the rivals' 133. Cause: before the first emblem gold counted double, so a gold cluster scored 40 against a gem cluster's 7. ge4 (no x2, no mid-push) collected 140 vs 127 by r300 and 319 vs 320 by r600; tributes stayed behind (200 vs 256 by r600) because carriers died with bags. Eight banking and carrier-safety variants gave no platform gain.
- **Fight phase (22:15-23:20).** We lost fights we started (0.36-0.55 own deaths vs 0.31-0.38 kills per start; rivals 0.2 vs 0.5-0.64) because we hit less. fh1 (free hit before kiting) and fh2 (melee hits before fleeing) raised hits and cut deaths on b5, b34 and b6.
- **Batch b6 (fresh panel at rank 77) and the final comparison (23:25-03:30).** The banking formula was missing a factor (ef1, ef3), items were bought from a fixed health-heavy list (sp1, sp3), a capture rule never ran (cp1), Vesper held fire when hurt (cp2), and Vendetta did not dash in (cp3). Tonight's runs on the same games:

| bot | b6 (40) | b5 (50) | b34 (50) | total |
|---|---|---|---|---|
| dr3g (dr3 + guard fixes) | 15 | 21 | 24 | 60 / 140 |
| **cp3** (adopted) | **20** | 19 | 20 | 59 / 140 |
| cf1 (dr3 + fight layers + guard) | 18 | 19 | - | 37 / 90 |
| sp3 / sp1 / ef3 | 18 / 17 / 17 | - / - / 18 | - / - / 25 | - |
| fh2 | 13 | 20 | 25 | 58 / 140 |

  dr3's b5 score from 18:14 (23) did not reproduce later: b5 opponents changed bots in between. b6 matched in 29 of 40 games.

### Batch b4 (10-24 16:25, ranks 79-83)

fx1 13/25, c5 12, dr3 14. Over b3 + b3x + b4 (75 games) dr3 41, c5 39, fx1 36: dr3 beat fx1 on every set and was adopted below the 17/25 bar at the user's call.

### Batch b3 (10-24 09:20-16:25, ranks 62-66)

Base fx1: b3 12/25, b3x 11/25. Gap: early deaths while fleeing near our spawn, enemy rushes (swirl: all four of ours dead by r90). About 40 variants; best c5 (27/50) and dr3 (c5 + Varg instead of Ryth, 27/50). 'will think later' (rank 66) beat us 8 of 10.

### Batch b2 (10-24 06:55-09:20, ranks 83-87)

Base fe1: b2 11/25, b2x 15/25. Accepted `fx1`: b2 19/25, b2x 15/25. Fight-behaviour variants and teleports did not hold on b2x.

### Batch b1 (10-24 03:00-06:55, ranks 81-85)

Base hb4: 15/25 (12/25 after Shawn changed bot). Accepted `fe1`: b1 17/25, b1x 13/25, local 414/560. Still lost by every variant: starvation, road_of_riches, interlock, rows, gem_fields.

### Rank 30 AlphaSlop push (10-23 evening)

hb4 11/40 against AlphaSlop on all 40 maps, exactly repeatable. Best variant pk4 13/40 but 22 vs 24 on ranks 70-80, so not adopted. Teams that beat AlphaSlop take the middle before round 600 and bank within 15 rounds; pushing us into the middle (md1) lost, because we lost the fights there.

## Parked ideas (not settled on the platform)

- `lc1`: flee at enemy power > 0.7x ours (more caution). Local 385, never gated.
- `fl3`: also count as losing when hit for > 40% health last round. Its small-gate groups may still hold results (`rcmp.py hb4l@p8s fl3l@p8s`).
- Altar locks: rivals buy 4-6 per game. Our tries (lk1-lk3, lke, lkh, pl1) gave no gain; lk3 (lock only to cancel an enemy tribute) never fired.
- cp1's passive-aware capture rule and cp2/cp3's fight rules are in cp3; their separate platform effect is unknown.

**11-03 08:57 IST, night session.** `vlm1` passed on the platform on four of its five maps (16 against 9 of 60, gold r300 997 to 1118), so per-map arms are the current line of work (`results/analysis/rule_arms.md`): a fresh local sample of the arms on 23 maps is running (`data/run_arm2.sh`). `rt5` (router, light camps on 4 maps, Vesper's gold rules) is playing against `v1523` on the `t03p` parts. `dci5f` is decoded for its deaths rule. New gap measured: against strong teams our fight sim reads low and our Marcella holds her nuke (0.18 of chances against the rivals' 0.34, 0.41 locally); `vfx1` is on its local screen (`results/analysis/rule_nuke.md`). Rejected locally this morning: vce1-3, dta5, dry5, vnt1-3, vch1-2.
