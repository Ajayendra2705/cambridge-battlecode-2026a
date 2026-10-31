# bamboo479 (Bamboo Teahouse #479)

Bamboo Teahouse's #479 = #458 (`bots/bamboo458`) + `kCaptureHit`, Eric's chosen default on 31 Oct ~17:45 UTC. The exact source submitted
to the Bamboo Teahouse team as version 479 (`kBotVersion` 479; not uploaded to Velvet Tributers). Build it with `cambc build bamboo479`.

`kCaptureHit`: while standing on a tile of our running capture, the turn's unused basic attack goes to an enemy champion in reach, else
a harmless or already hurt monster of another group.

Results: ladder quick panel (50 games vs the top 10, paired with #458's) 18 wins vs 15, margin -9.4k vs -12.7k - the best ladder number
of the day, within noise. Local screens -49 +-17: a read-only audit found that a strength-0 resource cluster of a full-health hostile
node passes its "harmless" test, and hitting it wakes the whole node. The fix (`kCaptureHitFix`, in the newer Bamboo source behind
`bots/bamboo458sf` and `bots/bamboo8`) brings it to about -5 locally.
