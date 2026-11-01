# bamboo458sf (Bamboo Teahouse #458 + spell finisher, platform version 1472)

#458 (`bots/bamboo458`) with one new behaviour, uploaded to Velvet Tributers as **v1472** on 31 Oct 23:22 UTC. Built from the newer Bamboo source
(every new switch off except `kSpellFinish 1`); every #458 setting is identical. Build it with `cambc build bamboo458sf`.

`kSpellFinish 1`: at the start of each turn, a ready single-target damage spell goes at the weakest visible enemy champion that is under
30% of its max health or within the spell's damage (not while recalling or tributing). Copied from Intercontinental Fish: with a nuke
ready and an enemy under 30% at 3-4 tiles their Marcella casts 56% of the time, ours 22%. Local screens vs four pool bots (1,120 games
each): +32 +-18 (seeds 1-2) and +9 +-18 (seeds 3-4) over #458. No ladder games yet.
