# Decision rule: Cassi and Issac in our drafts on v1503 (dci5m, dci5f, dci4), written 11-03 before any result

**Factor.** Early fight strength through the draft. On `t1503_tm@t03` (1503 against ranks 1-20) we win 3 of 34 five-a-side games against a rival Cassi and Issac pair, with deaths to r300 of
3.35 against 1.18, and 22 of 65 against other five-a-side drafts, with 2.09 against 1.46. On the ladder of 11-02 (`tools/platform/mapdrafts.py`, top 12 teams) ranks 1 and 2 both field the pair: Fish
plays Heart, Marcella, Vendetta, C&I, Willow (90 of 133, residual +3.6) and Mite plays Heart, Marcella, Vendetta, C&I, Vesper (176 of 271 with NEETCoders, residual +3.8); on four picks
both play Heart, Marcella, Vendetta, C&I. The pair is a sixth body on five picks. v1503 drafts Heart, Marcella, Vendetta, Vesper, Willow (five) and Heart, Marcella, Vendetta, Willow (four). The pair's residual against Elo is small, so
the gain is not proved: the question is what it does in our bot.

**Variants.** All are v1503 with the pair as the last pick, so Issac is the body without a comms slot.
- `dci5m`: five picks Heart, Marcella, Vendetta, Vesper, C&I (Mite's set, Willow out). Six-body support: `n_allies` up to 6, arrays of 6, a squad of 5 or more means everyone.
- `dci5f`: five picks Heart, Marcella, Vendetta, Willow, C&I (Fish's set, Vesper out). Same support.
- `dci4`: four picks Heart, Marcella, Vendetta, C&I (Willow out). Five bodies, so no six-body code.

**Local bar (before the screen; `tools/local/screen.sh`, 340 paired games against `pool.v1503`).** No bot fault; wins not down by more than 0.03 a game; gems collected to r1000 not down by more than 3%. Deaths are not judged by count locally, since a
pair's death counts twice, but gold to r300 must not fall by more than 2 se. On the maps of the changed size only, wins not down by more than 0.06 a game. Local cannot prove a draft (the pool does not rush); it can only reject one.

**Platform (after a local pass), panels of that team size only (`tools/platform/sizepanel.py`), with the base in the same session.** Target metric: our deaths to r300 minus theirs, counting the pair as one death on either side, down by at least 1 se in pairs
(`early2.py`, pair-corrected). Guards: team gold at r300 not down by more than 1 se, tributed to r1000 not down by more than 1 se, no fault. Wins are recorded, not judged.

**Three a side, added 11-03 before the screen.** `d3r` (Heart, Marcella, Ryth) and `d3c` (Marcella, Vesper, C&I; four bodies) against v1503's Heart, Vendetta, Vesper, on the 3-pick maps only (`SCREEN_MAPS=data/maps_size3.txt`, 120 paired games a variant). Same local bar: no fault, wins not down by more than 0.06 a game on these maps, gems collected to r1000 not down by more than 3%. Platform: panel `s3p`, against `base1503_s3p` of the same session, with the same target (deaths to r300 minus theirs, the pair counted once) and guards. Ladder evidence: Heart, Marcella, Ryth 42 of 63 at +17.0 +- 5.9 against Elo for Univardisty and T1; Marcella, Vesper, C&I 74 of 139 at -0.8 +- 4.0 for test4 and Fish, and 15-2 for Fish on close maps in late October.

**Fight link, added 11-03 before the screen.** `vci1` (v1503 with the pair's link in the fight simulation and in the target score, Cassi -200, Issac -100). The local pool does not draft the pair, so the screen plays v1503 and vci1 against our own C&I bots `exp/dci5f` and `exp/dci5m` on the 5-pick maps. Local bar: wins not down, our deaths to r300 minus theirs (the pair counted once) down by at least 1 se. Platform: t03p games against C&I teams, target the same metric on those games; guard on the games against other teams, where it should be level (only fuel noise differs).

**A stunner for Willow, added 11-03 07:35 before the screen.** Rivals land 21.0 stuns on our champions a game against our 9.5, and in 5-pick games against an extra stunner the death gap is all stunned deaths (`docs/findings.md`). Top teams' five picks are Vesper, Heart, Vendetta, Tavi or Ryth, Marcella (`top-builds-1031.md`); on `t1503_tm@t03` their Heart, Marcella, Tavi, Vendetta, Vesper wins 51 of 56 and their Heart, Marcella, Ryth, Vendetta, Vesper 32 of 44, against the same set with Willow 8 of 28. `dta5`: v1503 with Tavi for Willow at five picks, `dry5`: with Ryth. The local bar of this file on the 5-pick maps: no fault, wins not down by more than 0.06, gems collected to r1000 not down by more than 3%, gold to r300 not down by more than 2 SE. Platform: panel `s5p` with the same target (our deaths to r300 minus theirs down by at least 1 SE in pairs) and guards. Team strength confounds the win counts above: only the platform can say.
