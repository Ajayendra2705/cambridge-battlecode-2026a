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
