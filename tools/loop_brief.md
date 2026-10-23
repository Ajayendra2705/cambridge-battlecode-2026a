# Overnight loop brief (user, 2026-10-23 ~14:25 IST). Re-read every tick.

Best / ladder bot: bots/hb4 (logging copy bots/hb4l). Baseline hb4l@p8@20 38/100; fresh baseline hb4l2@p8@20.
Deadline: Sprint 2 locks Sat 24 Oct 23:59 BST (Sun 25 Oct 04:29 IST). From Sat 20:00 BST (Sun 00:30 IST) submit only the best proven bot.
Never leave a test bot on the ladder; resubmit hb4 (or best proven) after every gate. No questions, no progress messages. Log everything in memory cambc-status.md.

USER 14:45 IST: KEEP PLATFORM TESTS SMALL, ~20 GAMES. Use tools/gate8s.sh BOT (groups need EXACTLY 5 maps: 4 fixed groups = kitfunso, Patient Builder, SkibidiSloppers, bentheboss on their first @20 window, the most outcome-variable games; logged BOT@p8s; 4 quota groups; rcmp "hb4l@p8s" "NEW@p8s" or vs hb4l@p8@20). Noise at 20 games ~±3 wins: only big effects show; chain base->variants->base.
Full gate chain (old, 100 games) (PowerShell, background, sandbox disabled):
  $env:GATE_OFFSET='20'; & "C:\Program Files\Git\bin\bash.exe" tools/gate8.sh NEWl *> tools/gate_NEW.out;
  powershell -File tools/bc.ps1 submit hb4 *>> tools/gate_NEW.out; Remove-Item Env:GATE_OFFSET;
  python -I tools/rcmp.py "hb4l@p8@20" "NEWl@p8@20" *>> tools/gate_NEW.out
Local: multi.py CANDS --pool b_log,dm1,pd1,pgq,pw3,tf1,tf3 --maps (tools/allmaps.txt) --jobs 6 ; hb4 = 384/560; <10 wins = noise. Delete replays/multi-* after.

LOOP: 1 PLAY (ladder refresh, keep panel 8, play logging copy, gdl.py replays) -> 2 ANALYSE every game (gems, tributes, clears, gold, deaths by round; every death: pos/activity/hp/allies vs enemies/killer; what opponents do better; rank mistakes by games+gems cost) -> 3 FIX ONE MISTAKE (exact cause, probe unclear rules -> MECHANICS.md; build on best bot, diff, debug-print fires, remove debug, build) -> local 560 -> platform full panel @20 with rcmp. Noise ~±5/100. Keep only clear platform gains (ideally confirmed at a second offset).

HOW TO JUDGE A FIX (opponents drift):
- Analysis first; goal = remove mistakes, not chase wins.
- Before building, name the TARGET METRIC (e.g. elk_arena deaths before r300 / within 10 of our spawn; flee: deaths while fleeing, dmg taken per flee round; banking: gems lost per death, tributes by r600).
- Measure it in base AND variant replays (logging copies, V/D/A lines), write both numbers to cambc-status.md.
- Metric unmoved -> fix failed whatever wins say; find why. Metric moved, wins flat -> works, other bottleneck; keep as stacking candidate if not worse. Metric moved + wins up -> keep.
- Same-time comparison: base -> variant -> base on same games (same GATE_OFFSET). If the two base runs disagree much more than noise, opponents changed: discard and redo. Never compare with a baseline many hours old.
- Recheck old: th2, fp1, bt8l (rk_replays/) against their target metrics.

ALREADY TRIED: banking bt1/bt8 (platform 74 vs 79 pooled); tribute hunt tr/th2 (33 vs 38); altar locks lk1/lk2; fight entry pa1/bpt*/pc1; Ryth draft swaps; shop/heal/respawn-wait thresholds; boss_battle assault ag1/ag2; gathering ga1 (worse) and gx1-3 (noise); flee path fp1 (33 vs 38).
KEY FINDINGS: PvP deaths ~1190 vs 780/100 games mostly fleeing; our champ dmg ~1/3 theirs; elk_arena 0/5 (centre group, enemy 5-stack r17-30, deaths near own spawn fleeing); boss_battle altar guard; time split to_capture 25 fight 18 dead 10 resp_wait 10.
OPEN: bad maps (the_farm, starvation, road_of_riches, lost_world, gemfight, starfish, hooks, elk_arena, boss_battle); early deaths on own half; damage per gold; camp denial (stand on enemy group spawn tile); MECHANICS 18 (reduction stacking, set_priority, interleaving).
RULES: one platform gate at a time (quota 50 groups/h, gate = 20); never trust local alone for PvP; cp -r copies .cambc (delete it; mkvar fine); if a job is killed resubmit hb4 at once, log, restart with fewer jobs.
Report which variant wins.
