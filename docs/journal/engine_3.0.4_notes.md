---
name: cambc-engine304
description: Engine 3.0.4 champion stat changes (probed 2026-10-21) and the new top-10 draft meta; local cambc upgraded to 3.0.4
metadata:
  node_type: memory
  type: project
  originSessionId: 01e8e91c-95c7-4084-9321-9578f9435b07
  modified: 2026-10-21T16:00:17.878Z
---

On 2026-10-21 the user said champions changed. pip had cambc 3.0.4 (we ran 3.0.1); the same bots give different results on 3.0.4, so local tests before that date used an outdated engine. Local cambc upgraded to 3.0.4, sdk/ and cmake/ replaced from a fresh `cambc init` (old copy in the session scratchpad sdk_backup_301), cambc.toml sdk_version = "3.0.4". Running a downloaded cambc.exe from the scratchpad needs the sandbox disabled ("Access is denied").

Base stats probed with bots/probeA..C (print own stats and ability metadata on turn 1):
- Stellar hp 650 str 30 focus 70 (was 750/35/100): heavy nerf. Ren str 35, stun 0.75F (was 40, 1.25F). Varg str 40 (was 50).
- Tavi hp 900 str 45 focus 110, stun 1.4F (was 750/35/100, 2.2F). Vendetta hp 1000. Vesper hp 1000 str 55. Marcella focus 60. Ryth str 45. Cassi hp 600. Willow str 55 focus 120. Prism 1.5 focus per carried gem.
- Heart of Ruin: hp 1000 str 30 focus 100, shield 1.5F (5 turns), stunning dash 1.5F radius 1.

Top-10 ranked drafts (draftPicks use the champion_draft enum: 0 Ryth 1 Vesper 2 Vendetta 3 C&I 4 Stellar 5 Prism 6 Marcella 7 Willow 8 Ren 9 Varg 10 Tavi 11 HoR): HoR 76%, Marcella 74%, Vesper 72%, Ryth 68%, Vendetta 63%; Stellar 23%, Tavi 12%, Varg 6%. HoR is the usual first pick. We drafted Stellar, Ren, Tavi, Varg, Vendetta. Hard-coded spell coefficients in champion_burst/champion_dps (Ren 1.25, Tavi 2.2, Stellar) are stale.

**Why:** draft and fight math depend on these numbers. **How to apply:** read stats from the API where possible; re-probe after any CLI update. See [[cambc-status]].
