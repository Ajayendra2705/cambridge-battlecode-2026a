# Rule for d3m on the platform (written 11-02 23:18 IST, before any game of it)

- **Variant:** `exp/d3m` = 1503 with the three-a-side draft Heart of Ruin, Marcella, Vesper (Marcella for Vendetta). Local pass
  (`rule_1498.md`, "Drafts on 1503"; `multi-230151`, 120 games): team gold r300 +41.5 +- 32.8, collected +7 +- 21, deaths
  -0.81 +- 0.38, margin +66 +- 46, wins +0.02. The teammate's 1501 made the same change on v548 (0 against 5 of 14 paired).
- **Panel:** `s3p` (`tools/platform/sizepanel.py t03p 3 s3p`): 12 teams of ranks 1-20, five maps of three a side each, 60 games,
  the opponents pinned to their bots of `t1503_tm@t03`. Base `base1503_s3p@s3p` (pool/v1503) on the same panel in the same chain.
- **Factor and target:** our gems collected to r1000 (`paired.py`) up by at least one standard error.
- **Guards:** tributed not down by more than one standard error, our deaths not up by more than one, no bot fault.
- **Recorded, not judged:** wins and flips, the rivals' deaths, margin.
- **If it passes:** d3m's draft goes into the next live candidate. If it fails: dropped.
