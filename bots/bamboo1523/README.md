# bamboo1523 (v1503 + recall, wards, fuel fixes, spawn siege; platform version 1523)

The team bot v1503 (`v606`, cheji bt's bot_10 line) plus the Bamboo edits below, uploaded to Velvet Tributers as **v1523** on 2 Nov 23:47 UTC
(note "Bamboo v1513+fuel fixes (-90% fuel limits)+spawn-tile siege, homonoliths"). The source is exactly what was submitted. Build it
with `cambc build bamboo1523`. Every change is a `P_*` switch in `src/params.h`; the comments name the edit script that added it (those
scripts live in the Bamboo repo, `tools/edits/edit_vt*.py`, and patch v1503's source by exact anchors).

| Edit | Switches | What it does |
|---|---|---|
| vtreport | `kReportRound` | prints both teams' banked gems at a set round (local screens cut games at r800) |
| vtrecall | `P_RECALL_PRIME`, `P_RECALL_READ` | the top teams' pre-started recall: a recall is queued at every turn end and kept next turn only to go home (4-turn trip) |
| vtwards | `P_WARDS` and friends | wards in bushes and at fights instead of on open ground |
| vtfuel 1-3 | caches, measured guards | fuel savings that keep every decision: fuel-limit turns after r3 735 -> 46 on the local pool |
| vtspawn | `P_SPAWN_HIT`, `P_SPAWN_SIEGE` | a hurt champion on its spawn still hits what is in reach; a big gem group touching the spawn (03homonoliths' monoliths) is sieged from the spawn tiles, which heal fully every turn |

## Known bug (fixed in bamboo1530)

vtspawn's `P_SIEGE_HP 1.25f` is defined before params.h's team-siege `P_SIEGE_HP 3000.f`, so the second `#ifndef` never applies: on gated
and heavy maps farm.cpp's whole-team siege starts at round 400 with any max health (it needed 3000 max health or round 900). Found by the
Nov 3 code review; bamboo1530 renames the spawn one to `P_SPAWN_SIEGE_HP`.

## Results

- Ladder half panel (16 groups of the v1504 panel replayed with the same opponent bots, maps and sides, 80 games): 22 wins (margin -27,619);
  v1513 25, v1512 (= v1503) 19.
- Your pinned panels (`t03pa`, `t03pb`, `a7p`, 175 games against ranks 1-20, from docs/findings.md): 46 wins (margin -378) against rt5's 43.
