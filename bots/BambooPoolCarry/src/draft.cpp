#include <cambc.h>
#include "bot.h"
#include "draft.h"
#include <algorithm>
#include <array>

namespace {

// Steps between the two spawn regions, around walls. Close spawns mean early
// and frequent fights, which ranged stun casters win (locally +350 on
// corners and interlock); distant ones make the game a farming race, where
// melee farmers are faster (rows, lanes, expanse: 73-85 steps).
int spawn_steps() {
    static int steps = -1;
    if (steps >= 0) return steps;
    steps = 1 << 20;
    try {
        const cambc::bitboard blocked = cambc::map::walls() | cambc::map::holes() | cambc::map::altars();
        const cambc::bitboard roots = cambc::map::spawn_region(cambc::team::ally);
        cambc::distance_field dist;
        cambc::bitboard reach;
        reach.clear();
        dist.compute(blocked, roots, reach);
        for (const cambc::vec2 p : cambc::map::spawn_region(cambc::team::enemy).positions()) {
            if (reach.is_set(p)) steps = std::min(steps, static_cast<int>(dist.get(p)));
        }
    } catch (const cambc::error&) {
    }
    return steps;
}

// Camp groups with two or more fighting monsters within 20 tiles of our
// spawn (packs: three wolf pairs on each home row; collision: none).
int home_packs() {
    static int n = -1;
    if (n >= 0) return n;
    n = 0;
    try {
        const auto home = cambc::map::spawn_region(cambc::team::ally).positions();
        for (const auto& cg : cambc::map::camp_groups()) {
            int hostile = 0, count = 0;
            cambc::vec2 sum{0, 0};
            for (const cambc::camp& c : cg.camps()) {
                if (c.base_stats().base_strength > 0) ++hostile;
                sum += c.spawn_position();
                ++count;
            }
            if (hostile < 2 || count == 0) continue;
            const cambc::vec2 center = sum / static_cast<std::int32_t>(count);
            int d = 1 << 20;
            for (const cambc::vec2 t : home) d = std::min(d, static_cast<int>(center.chebyshev_distance(t)));
            if (d <= 20) ++n;
        }
    } catch (const cambc::error&) {
    }
    return n;
}

// The layout that makes the whole team farm together all game (bot.cpp,
// kAutoTeam): camps of two or more fighting monsters within 20 tiles of our
// spawn, and nothing worth farming alone there (rows: three wolf trios).
// Spawns close together (rushbait-v2: 4 apart): fights start at the spawns.
bool spawns_close(int within) {
    static int cached = -1;
    if (cached >= 0) return cached == 1;
    cached = 0;
    try {
        const auto ours = cambc::map::spawn_region(cambc::team::ally).positions();
        const auto theirs = cambc::map::spawn_region(cambc::team::enemy).positions();
        int best = 1 << 20;
        for (const auto& a : ours) {
            for (const auto& b : theirs) best = std::min(best, static_cast<int>(a.chebyshev_distance(b)));
        }
        cached = best <= within ? 1 : 0;
    } catch (const cambc::error&) {
    }
    return cached == 1;
}

bool whole_team_map() {
    static int cached = -1;
    if (cached >= 0) return cached == 1;
    cached = 0;
    try {
        const auto home = cambc::map::spawn_region(cambc::team::ally).positions();
        float team_value = 0, solo_value = 0;
        for (const auto& cg : cambc::map::camp_groups()) {
            int hostile = 0, count = 0;
            cambc::vec2 sum{0, 0};
            for (const cambc::camp& c : cg.camps()) {
                if (c.base_stats().base_strength > 0) ++hostile;
                sum += c.spawn_position();
                ++count;
            }
            if (count == 0) continue;
            const cambc::vec2 center = sum / static_cast<std::int32_t>(count);
            int d = 1 << 20;
            for (const cambc::vec2 t : home) d = std::min(d, static_cast<int>(center.chebyshev_distance(t)));
            if (d > 20) continue;
            (hostile >= 2 ? team_value : solo_value) += static_cast<float>(cg.gem_value()) + 0.35f * static_cast<float>(cg.gold_value());
        }
        cached = team_value > 0 && solo_value <= 0 ? 1 : 0;
    } catch (const cambc::error&) {
    }
    return cached == 1;
}

// Every camp group holds a strong monster (elkring: ten elk camps). Fights
// there are rare beside the race to retake elks on respawn, which strength
// farmers win (红包控股's six farmers took 30 elk camps to our casters' 23).
bool elk_map() {
    static int cached = -1;
    if (cached >= 0) return cached == 1;
    cached = 0;
    try {
        int groups = 0, elk = 0;
        for (const auto& cg : cambc::map::camp_groups()) {
            ++groups;
            bool strong = false;
            for (const cambc::camp& c : cg.camps()) strong = strong || c.base_stats().base_strength >= 50;
            elk += strong ? 1 : 0;
        }
        cached = groups > 0 && elk == groups ? 1 : 0;
    } catch (const cambc::error&) {
    }
    return cached == 1;
}

// Camp groups anywhere on the map with two or more fighting monsters
// (lanes: none - single wolves, elks and clusters; monolith: six wolf pairs).
int multi_hitter_groups() {
    static int n = -1;
    if (n >= 0) return n;
    n = 0;
    try {
        for (const auto& cg : cambc::map::camp_groups()) {
            int hostile = 0;
            for (const cambc::camp& c : cg.camps()) hostile += c.base_stats().base_strength > 0 ? 1 : 0;
            n += hostile >= 2 ? 1 : 0;
        }
    } catch (const cambc::error&) {
    }
    return n;
}

// Keep equal to bot.cpp's kBossMaxStr and kBossGemShare (boss mode's camp strength cap and gem share).
constexpr float kDraftBossMaxStr = 100.0f;
constexpr float kDraftBossShare = 0.8f;

// Most camp gems sit in huge camps whose monsters hit no harder than kDraftBossMaxStr
// (stampede: one 17.4k camp), as bot.cpp's boss mode decides it.
bool boss_map() {
    static int cached = -1;
    if (cached >= 0) return cached == 1;
    cached = 0;
    try {
        float all = 0, boss = 0;
        for (const auto& cg : cambc::map::camp_groups()) {
            float hp = 0, hardest = 0;
            for (const cambc::camp& c : cg.camps()) {
                const auto stats = c.base_stats();
                hp += stats.base_health;
                hardest = std::max(hardest, static_cast<float>(stats.base_strength));
            }
            const float gems = static_cast<float>(cg.gem_value());
            all += gems;
            if (hp >= 10000.0f && gems > 0 && hardest <= kDraftBossMaxStr) boss += gems;
        }
        cached = boss > 0 && boss >= kDraftBossShare * all ? 1 : 0;
    } catch (const cambc::error&) {
    }
    return cached == 1;
}

}  // namespace

// Patch test (Oct 20, user: Cassi & Issac fall off in the mid and late game; Marcella and Vesper Vale were buffed): wherever
// our lists pick Cassi & Issac, pick 1 Marcella, 2 Vesper Vale or 3 Heart of Ruin instead (0: off). One pick then brings one
// champion, not two.
constexpr int kTwinSwap = 1;
// User (Oct 20): someone else in Tavi's slot: 1 Marcella, 2 Vesper Vale, 3 Vendetta, 4 Prism, 5 Heart of Ruin (0: off).
// A swap to a champion we already hold throws, and the list moves on to its next pick.
constexpr int kTaviSwap = 0;
constexpr int kVargSwap = 0;  // user (Oct 20): someone else in Varg's slot, same numbering (5: Heart of Ruin)
cambc::champion_draft swap_pick(int k) {
    using cambc::champion_draft;
    return k == 1 ? champion_draft::marcella : k == 2 ? champion_draft::vesper_vale : k == 3 ? champion_draft::vendetta
         : k == 4 ? champion_draft::prism : champion_draft::heart_of_ruin;
}
void draft_pick(cambc::champion_draft p) {
    if (kTwinSwap > 0 && p == cambc::champion_draft::cassi_and_issac) p = kTwinSwap == 3 ? cambc::champion_draft::heart_of_ruin : swap_pick(kTwinSwap);
    else if (kTaviSwap > 0 && p == cambc::champion_draft::tavi) p = swap_pick(kTaviSwap);
    else if (kVargSwap > 0 && p == cambc::champion_draft::varg) p = swap_pick(kVargSwap);
    cambc::draft::pick(p);
}

// Patch test (Oct 20): a fixed composition on every map, picked in this order (0: the map-dependent lists below).
// 1: C&I, Willow, Varg, Vendetta, Prism (sustain + the buffed farmers); 2: C&I, Stellar, Willow, Vendetta, Varg;
// 3: Heart of Ruin, C&I, Willow, Prism, Vendetta; 4: C&I, Stellar, Varg, Ryth, Ren (the old meta, for reference).
constexpr int kForceDraft = 0;

static void pick_champion() {
    using cambc::champion_draft;
    if (kForceDraft > 0) {
        constexpr std::array<champion_draft, 11> force1{champion_draft::cassi_and_issac, champion_draft::willow, champion_draft::varg, champion_draft::vendetta, champion_draft::prism, champion_draft::stellar, champion_draft::ren, champion_draft::ryth, champion_draft::tavi, champion_draft::marcella, champion_draft::vesper_vale};
        constexpr std::array<champion_draft, 11> force2{champion_draft::cassi_and_issac, champion_draft::stellar, champion_draft::willow, champion_draft::vendetta, champion_draft::varg, champion_draft::ren, champion_draft::ryth, champion_draft::prism, champion_draft::tavi, champion_draft::marcella, champion_draft::vesper_vale};
        constexpr std::array<champion_draft, 11> force3{champion_draft::heart_of_ruin, champion_draft::cassi_and_issac, champion_draft::willow, champion_draft::prism, champion_draft::vendetta, champion_draft::varg, champion_draft::stellar, champion_draft::ren, champion_draft::ryth, champion_draft::tavi, champion_draft::marcella};
        constexpr std::array<champion_draft, 11> force4{champion_draft::cassi_and_issac, champion_draft::stellar, champion_draft::varg, champion_draft::ryth, champion_draft::ren, champion_draft::vendetta, champion_draft::tavi, champion_draft::prism, champion_draft::willow, champion_draft::marcella, champion_draft::vesper_vale};
        const auto& order = kForceDraft == 1 ? force1 : kForceDraft == 2 ? force2 : kForceDraft == 3 ? force3 : force4;
        const auto chosen = cambc::draft::current_draft(cambc::team::ally);
        for (const auto pick : order) {
            if (std::find(chosen.begin(), chosen.end(), pick) != chosen.end()) continue;
            try { cambc::draft::pick(pick); return; } catch (const cambc::error&) {}
        }
    }
    // Ladder leaders draft this core in every game:
    // Vendetta, Varg and Cassi & Issac, then Ryth; Stellar fifth (as SSSA
    // and Cabbage) beat Tavi in a four-seed league, +346 vs +307.
    // 0: melee farmers (above). 1: the ladder leader's ranged core by team
    // size (Univ: Stellar in every draft, Ren as tank, Tavi/Prism stunning
    // casters; Cassi & Issac only when fewer than five picks). 2: the ranged
    // core when the spawns are at most kRangedSteps apart, farmers otherwise.
    constexpr int kDraftStyle = 2;
    constexpr int kRangedSteps = 45;
    constexpr std::array farmers{
        champion_draft::vendetta, champion_draft::varg, champion_draft::cassi_and_issac, champion_draft::ryth, champion_draft::stellar, champion_draft::tavi, champion_draft::marcella, champion_draft::ren, champion_draft::vesper_vale, champion_draft::willow, champion_draft::prism,
    };
    // Stellar's area spell before Ryth: rows' wolves stand in threes (Univ's
    // Stellar dealt 25k damage to camps there, our Cassi 6k).
    // (four picks only - rows: +22 +-8 paired on rows, pace 478 vs 483, +37 vs v48 there; with five picks the reorder
    // moved roster slots: lanes -28, monolith -101)
    constexpr bool kFarmerStellar = true; 
    constexpr std::array farmers_aoe{
        champion_draft::vendetta, champion_draft::varg, champion_draft::cassi_and_issac, champion_draft::stellar, champion_draft::ryth, champion_draft::tavi, champion_draft::marcella, champion_draft::ren, champion_draft::vesper_vale, champion_draft::willow, champion_draft::prism,
    };
    constexpr bool kSmallTavi = true;   // three picks: Tavi (stun, 2.2 x Focus) before Ren (Cabbage on collision; +41 on collision, others unchanged)
    constexpr std::array small_ranged_ren{
        champion_draft::cassi_and_issac, champion_draft::stellar, champion_draft::ren, champion_draft::tavi, champion_draft::varg, champion_draft::prism, champion_draft::ryth, champion_draft::vendetta, champion_draft::vesper_vale, champion_draft::willow, champion_draft::marcella,
    };
    constexpr std::array small_ranged_tavi{
        champion_draft::cassi_and_issac, champion_draft::stellar, champion_draft::tavi, champion_draft::ren, champion_draft::varg, champion_draft::prism, champion_draft::ryth, champion_draft::vendetta, champion_draft::vesper_vale, champion_draft::willow, champion_draft::marcella,
    };
    const auto& small_ranged = kSmallTavi ? small_ranged_tavi : small_ranged_ren;
    // Three picks with wolf packs at home: Varg's splash instead of Ren (the
    // ladder's packs winners: Univ, Mite, Full Damage draft C&I, Stellar, Varg).
    constexpr int kPacksPick = 2;    // on those maps 0 Varg, 1 Tavi, 2 Ren (2.2.0 ranked: Fish, Mite, Sneaky, procless, kryoton, World Machine draft Ren, Stellar, C&I on packs)
                                     // (packs + fragment, 8 seeds: 2 +174 +-62 (fragment +282, packs +65), 1 +118; 3 builds x 4 fresh seeds: 2 +81 +-56)
    constexpr bool kPacksVarg = true; 
    constexpr std::array small_ranged_varg{
        champion_draft::cassi_and_issac, champion_draft::stellar, champion_draft::varg, champion_draft::ren, champion_draft::tavi, champion_draft::prism, champion_draft::ryth, champion_draft::vendetta, champion_draft::vesper_vale, champion_draft::willow, champion_draft::marcella,
    };
    constexpr std::array four_ranged{
        champion_draft::cassi_and_issac, champion_draft::stellar, champion_draft::tavi, champion_draft::ren, champion_draft::varg, champion_draft::prism, champion_draft::ryth, champion_draft::vendetta, champion_draft::vesper_vale, champion_draft::willow, champion_draft::marcella,
    };
    constexpr std::array five_ranged{
        champion_draft::stellar, champion_draft::prism, champion_draft::ren, champion_draft::tavi, champion_draft::ryth, champion_draft::varg, champion_draft::cassi_and_issac, champion_draft::vendetta, champion_draft::vesper_vale, champion_draft::willow, champion_draft::marcella,
    };
    // Whole-team maps: the rows leader's draft (hello: Cassi & Issac, Tavi,
    // Varg, Stellar; 16 wolf captures by r330 in parties of 2-3; Gem Simons wins rows with it in 2.2.0).
    // (v74 bot, rows 8 seeds: -131 +-12, pace 431 -> 475: our play does not use Tavi as they do)
    constexpr bool kWholeTeamDraft = false;
    constexpr std::array whole_team{
        champion_draft::cassi_and_issac, champion_draft::tavi, champion_draft::varg, champion_draft::stellar, champion_draft::ryth, champion_draft::vendetta, champion_draft::ren, champion_draft::prism, champion_draft::vesper_vale, champion_draft::willow, champion_draft::marcella,
    };
    // The ladder's power-farming core: Varg (splash farming), Stellar,
    // Cassi & Issac, then Tavi and Ren (top teams' drafts on 5-pick maps;
    // rows: Varg in 19 of 19 winning drafts). Ours with it: -50 +-22 (8 seeds;
    // rows -83, packs -108, elkring -94): our play does not use it as they do.
    constexpr bool kVargDraft = false;
    constexpr std::array varg3{
        champion_draft::varg, champion_draft::stellar, champion_draft::cassi_and_issac, champion_draft::tavi, champion_draft::ren, champion_draft::ryth, champion_draft::prism, champion_draft::vendetta, champion_draft::vesper_vale, champion_draft::willow, champion_draft::marcella,
    };
    constexpr std::array varg4{
        champion_draft::cassi_and_issac, champion_draft::stellar, champion_draft::tavi, champion_draft::varg, champion_draft::ren, champion_draft::ryth, champion_draft::prism, champion_draft::vendetta, champion_draft::vesper_vale, champion_draft::willow, champion_draft::marcella,
    };
    constexpr std::array varg5{
        champion_draft::varg, champion_draft::stellar, champion_draft::cassi_and_issac, champion_draft::tavi, champion_draft::ren, champion_draft::ryth, champion_draft::prism, champion_draft::vendetta, champion_draft::vesper_vale, champion_draft::willow, champion_draft::marcella,
    };
    const int size = static_cast<int>(cambc::draft::team_size());
    // Elk-only maps (elkring): 1 the farmers (pace +33 but -89 margin locally);
    // 2 the twins in the ranged core (their pick is two bodies: ladder elkring
    // drafts field 6 to our 5 and earn 30-50% more gold); 3 twins and Varg.
    // (elkring only, 8 seeds: 1 -89 +-41 pace 522; 2 -706, pace 1525 (no one clears elks); 3 +6 +-44, pace 528 vs 555)
    constexpr int kElkFarmers = 3;
    constexpr std::array elk_ranged{
        champion_draft::cassi_and_issac, champion_draft::stellar, champion_draft::ren, champion_draft::tavi, champion_draft::ryth, champion_draft::prism, champion_draft::varg, champion_draft::vendetta, champion_draft::vesper_vale, champion_draft::willow, champion_draft::marcella,
    };
    // kElkPick: 1 Ryth for Tavi (2.2.0 ranked: 5 teams that beat us on elkring draft C&I, Ren, Ryth, Stellar, Varg)
    constexpr int kElkPick = 0;
    constexpr std::array elk_ryth{
        champion_draft::cassi_and_issac, champion_draft::varg, champion_draft::stellar, champion_draft::ren, champion_draft::ryth, champion_draft::tavi, champion_draft::prism, champion_draft::vendetta, champion_draft::vesper_vale, champion_draft::willow, champion_draft::marcella,
    };
    constexpr std::array elk_varg{
        champion_draft::cassi_and_issac, champion_draft::varg, champion_draft::stellar, champion_draft::ren, champion_draft::tavi, champion_draft::ryth, champion_draft::prism, champion_draft::vendetta, champion_draft::vesper_vale, champion_draft::willow, champion_draft::marcella,
    };
    const bool ranged = kDraftStyle == 1 || (kDraftStyle == 2 && spawn_steps() <= kRangedSteps && !(kElkFarmers == 1 && elk_map()));
    const bool elk_draft = kElkFarmers >= 2 && ranged && elk_map();
    const bool packs = kPacksVarg && size <= 3 && home_packs() > 0;
    // kStunDraft (user, Oct 20): melee champions with stuns (Heart of Ruin's landing area stun, Ryth's area stun, Ren,
    // Marcella) plus a ranged burst (Stellar) beat ranged-heavy drafts early and are strong on camps. 1 on farming maps
    // (spawns more than kRangedSteps apart), 2 also on any map once the enemy's revealed picks are mostly ranged (picks
    // are simultaneous and revealed as they go). Pick order is turn order: the dash opens, Ryth's stun follows.
    // kMetaDraft (Oct 20 top-team replays, 30 ranked games each): procless, Sponge and Sneaky draft Heart of Ruin and Ren in
    // every game (Ryth in most) on every map. 1 procless (HoR, Ren, Ryth, Tavi, Marcella; 3 picks HoR, Ren, Ryth), 2 Sponge
    // (HoR, Ren, Stellar, Ryth, Varg; 3 picks HoR, Ren, Stellar), 3 Sneaky (HoR, Ren, Ryth, Stellar, Tavi) (0: our lists).
    constexpr int kMetaDraft = 4;
    if (kMetaDraft > 0) {
        constexpr std::array meta1{champion_draft::heart_of_ruin, champion_draft::ren, champion_draft::ryth, champion_draft::tavi, champion_draft::marcella, champion_draft::stellar,
                                   champion_draft::varg, champion_draft::prism, champion_draft::vendetta, champion_draft::vesper_vale, champion_draft::cassi_and_issac};
        constexpr std::array meta2{champion_draft::heart_of_ruin, champion_draft::ren, champion_draft::stellar, champion_draft::ryth, champion_draft::varg, champion_draft::tavi,
                                   champion_draft::marcella, champion_draft::prism, champion_draft::vendetta, champion_draft::vesper_vale, champion_draft::cassi_and_issac};
        constexpr std::array meta3{champion_draft::heart_of_ruin, champion_draft::ren, champion_draft::ryth, champion_draft::stellar, champion_draft::tavi, champion_draft::varg,
                                   champion_draft::marcella, champion_draft::prism, champion_draft::vendetta, champion_draft::vesper_vale, champion_draft::cassi_and_issac};
        // 4: the Oct 21 meta on engine 1.0.2 (procless; Eric): HoR, Vesper, Ryth, Marcella, Vendetta (edit_meta4.py)
        constexpr std::array meta4{champion_draft::heart_of_ruin, champion_draft::vesper_vale, champion_draft::ryth, champion_draft::marcella, champion_draft::vendetta, champion_draft::ren,
                                   champion_draft::stellar, champion_draft::varg, champion_draft::tavi, champion_draft::cassi_and_issac, champion_draft::prism};
        // kPrismMeta (review 2026-10-23 #1/#5: :3 drafts Prism on 4 of 5 maps; its area spell edge-casts elk packs from 5 for
        // 220-650): 1 Prism in Marcella's place, 2 in Vendetta's (0: meta4 as it is)
        constexpr int kPrismMeta = 0;
        constexpr std::array meta4p1{champion_draft::heart_of_ruin, champion_draft::vesper_vale, champion_draft::ryth, champion_draft::prism, champion_draft::vendetta, champion_draft::marcella,
                                     champion_draft::ren, champion_draft::stellar, champion_draft::varg, champion_draft::tavi, champion_draft::cassi_and_issac};
        constexpr std::array meta4p2{champion_draft::heart_of_ruin, champion_draft::vesper_vale, champion_draft::ryth, champion_draft::marcella, champion_draft::prism, champion_draft::vendetta,
                                     champion_draft::ren, champion_draft::stellar, champion_draft::varg, champion_draft::tavi, champion_draft::cassi_and_issac};
        // kMarcDraft (edit_marcdraft.py): Marcella earlier in meta4 (1 third, 2 second, 3 first with HoR fourth) (0: off)
        constexpr int kMarcDraft = 0;
        constexpr std::array meta4m1{champion_draft::heart_of_ruin, champion_draft::vesper_vale, champion_draft::marcella, champion_draft::ryth, champion_draft::vendetta, champion_draft::ren,
                                     champion_draft::stellar, champion_draft::varg, champion_draft::tavi, champion_draft::cassi_and_issac, champion_draft::prism};
        constexpr std::array meta4m2{champion_draft::heart_of_ruin, champion_draft::marcella, champion_draft::vesper_vale, champion_draft::ryth, champion_draft::vendetta, champion_draft::ren,
                                     champion_draft::stellar, champion_draft::varg, champion_draft::tavi, champion_draft::cassi_and_issac, champion_draft::prism};
        constexpr std::array meta4m3{champion_draft::marcella, champion_draft::vesper_vale, champion_draft::ryth, champion_draft::heart_of_ruin, champion_draft::vendetta, champion_draft::ren,
                                     champion_draft::stellar, champion_draft::varg, champion_draft::tavi, champion_draft::cassi_and_issac, champion_draft::prism};
        // kWillowMeta (edit_willowmeta.py): Willow fifth instead of Vendetta (1) or fourth before Marcella (2) (0: off)
        constexpr int kWillowMeta = 1;
        constexpr std::array meta4w1{champion_draft::heart_of_ruin, champion_draft::vesper_vale, champion_draft::ryth, champion_draft::marcella, champion_draft::willow, champion_draft::vendetta,
                                     champion_draft::ren, champion_draft::stellar, champion_draft::varg, champion_draft::tavi, champion_draft::cassi_and_issac};
        constexpr std::array meta4w2{champion_draft::heart_of_ruin, champion_draft::vesper_vale, champion_draft::ryth, champion_draft::willow, champion_draft::marcella, champion_draft::vendetta,
                                     champion_draft::ren, champion_draft::stellar, champion_draft::varg, champion_draft::tavi, champion_draft::cassi_and_issac};
        constexpr std::array meta4w3{champion_draft::heart_of_ruin, champion_draft::vesper_vale, champion_draft::marcella, champion_draft::willow, champion_draft::ryth, champion_draft::vendetta,
                                     champion_draft::ren, champion_draft::stellar, champion_draft::varg, champion_draft::tavi, champion_draft::cassi_and_issac};
        constexpr std::array meta4w4{champion_draft::marcella, champion_draft::vesper_vale, champion_draft::ryth, champion_draft::willow, champion_draft::heart_of_ruin, champion_draft::vendetta,
                                     champion_draft::ren, champion_draft::stellar, champion_draft::varg, champion_draft::tavi, champion_draft::cassi_and_issac};
        // kSmallMarc (edit_smallmarc.py): 3 picks or fewer -> Marcella, Vesper, Ryth (0: off)
        constexpr int kSmallMarc = 1;
        // kFourPick / kFivePick (edit_picksize.py): lists for 4- and 5-pick drafts (0: the list below)
        constexpr int kFourPick = 2;
        constexpr int kFivePick = 0;
        using cd = champion_draft;
        constexpr std::array p4a{cd::heart_of_ruin, cd::vesper_vale, cd::ryth, cd::willow, cd::marcella, cd::vendetta, cd::ren, cd::stellar, cd::varg, cd::tavi, cd::cassi_and_issac};
        constexpr std::array p4b{cd::marcella, cd::vesper_vale, cd::ryth, cd::willow, cd::heart_of_ruin, cd::vendetta, cd::ren, cd::stellar, cd::varg, cd::tavi, cd::cassi_and_issac};
        constexpr std::array p4c{cd::heart_of_ruin, cd::marcella, cd::vesper_vale, cd::willow, cd::ryth, cd::vendetta, cd::ren, cd::stellar, cd::varg, cd::tavi, cd::cassi_and_issac};
        constexpr std::array p4d{cd::marcella, cd::vesper_vale, cd::ryth, cd::heart_of_ruin, cd::willow, cd::vendetta, cd::ren, cd::stellar, cd::varg, cd::tavi, cd::cassi_and_issac};
        constexpr std::array p5a{cd::marcella, cd::vesper_vale, cd::ryth, cd::willow, cd::tavi, cd::heart_of_ruin, cd::vendetta, cd::ren, cd::stellar, cd::varg, cd::cassi_and_issac};
        constexpr std::array p5b{cd::heart_of_ruin, cd::marcella, cd::vesper_vale, cd::willow, cd::tavi, cd::ryth, cd::vendetta, cd::ren, cd::stellar, cd::varg, cd::cassi_and_issac};
        constexpr std::array p5c{cd::heart_of_ruin, cd::vesper_vale, cd::vendetta, cd::marcella, cd::willow, cd::ryth, cd::ren, cd::stellar, cd::varg, cd::tavi, cd::cassi_and_issac};
        constexpr std::array p5d{cd::heart_of_ruin, cd::willow, cd::vesper_vale, cd::ryth, cd::marcella, cd::vendetta, cd::ren, cd::stellar, cd::varg, cd::tavi, cd::cassi_and_issac};
        constexpr std::array p5e{cd::heart_of_ruin, cd::marcella, cd::vesper_vale, cd::ryth, cd::willow, cd::vendetta, cd::ren, cd::stellar, cd::varg, cd::tavi, cd::cassi_and_issac};
        constexpr std::array p5f{cd::vesper_vale, cd::heart_of_ruin, cd::ryth, cd::marcella, cd::willow, cd::vendetta, cd::ren, cd::stellar, cd::varg, cd::tavi, cd::cassi_and_issac};
        constexpr std::array p5g{cd::heart_of_ruin, cd::vesper_vale, cd::marcella, cd::ryth, cd::willow, cd::vendetta, cd::ren, cd::stellar, cd::varg, cd::tavi, cd::cassi_and_issac};
        constexpr int kThreePick = 0;
        constexpr std::array p5h{cd::marcella, cd::vesper_vale, cd::ryth, cd::willow, cd::heart_of_ruin, cd::vendetta, cd::ren, cd::stellar, cd::varg, cd::tavi, cd::cassi_and_issac};
        constexpr std::array p5i{cd::marcella, cd::vesper_vale, cd::ryth, cd::willow, cd::vendetta, cd::heart_of_ruin, cd::ren, cd::stellar, cd::varg, cd::tavi, cd::cassi_and_issac};
        constexpr std::array p5j{cd::marcella, cd::vesper_vale, cd::ryth, cd::willow, cd::varg, cd::heart_of_ruin, cd::vendetta, cd::ren, cd::stellar, cd::tavi, cd::cassi_and_issac};
        constexpr std::array p3a{cd::marcella, cd::vesper_vale, cd::willow, cd::ryth, cd::heart_of_ruin, cd::vendetta, cd::ren, cd::stellar, cd::varg, cd::tavi, cd::cassi_and_issac};
        constexpr std::array p3b{cd::marcella, cd::ryth, cd::vesper_vale, cd::heart_of_ruin, cd::willow, cd::vendetta, cd::ren, cd::stellar, cd::varg, cd::tavi, cd::cassi_and_issac};
        constexpr std::array p3c{cd::vesper_vale, cd::marcella, cd::ryth, cd::heart_of_ruin, cd::willow, cd::vendetta, cd::ren, cd::stellar, cd::varg, cd::tavi, cd::cassi_and_issac};
        // kDraftAlt (edit_draftalt.py): 1 three picks with HoR for Ryth; 2 Vendetta for Willow in the 4- and 5-pick lists (0: off)
        constexpr int kDraftAlt = 2;
        constexpr std::array p3h{cd::marcella, cd::vesper_vale, cd::heart_of_ruin, cd::ryth, cd::vendetta, cd::ren, cd::stellar, cd::varg, cd::tavi, cd::cassi_and_issac, cd::willow};
        constexpr std::array p4v{cd::marcella, cd::vesper_vale, cd::ryth, cd::vendetta, cd::heart_of_ruin, cd::willow, cd::ren, cd::stellar, cd::varg, cd::tavi, cd::cassi_and_issac};
        constexpr std::array m5v{cd::heart_of_ruin, cd::vesper_vale, cd::ryth, cd::marcella, cd::vendetta, cd::willow, cd::ren, cd::stellar, cd::varg, cd::tavi, cd::cassi_and_issac};
        const auto& list = (kDraftAlt & 1) && size <= 3 && kThreePick == 0 && kSmallMarc > 0 ? p3h
                         : (kDraftAlt & 2) && size == 4 && kFourPick == 2 ? p4v
                         : (kDraftAlt & 2) && size >= 5 && kFivePick == 0 && kWillowMeta == 1 && kMetaDraft == 4 && kPrismMeta == 0 && kMarcDraft == 0 ? m5v
                         : kThreePick > 0 && size <= 3 ? (kThreePick == 1 ? p3a : kThreePick == 2 ? p3b : p3c)
                         : kFivePick >= 8 && size >= 5 ? (kFivePick == 8 ? p5h : kFivePick == 9 ? p5i : p5j)
                         : kFourPick > 0 && size == 4 ? (kFourPick == 1 ? p4a : kFourPick == 2 ? p4b : kFourPick == 3 ? p4c : p4d)
                         : kFivePick > 0 && size >= 5 ? (kFivePick == 1 ? p5a : kFivePick == 2 ? p5b : kFivePick == 3 ? p5c : kFivePick == 4 ? p5d : kFivePick == 5 ? p5e : kFivePick == 6 ? p5f : p5g)
                         : kSmallMarc > 0 && size <= 3 ? meta4m3 : kMetaDraft == 1 ? meta1 : kMetaDraft == 2 ? meta2 : kMetaDraft == 3 ? meta3 : kPrismMeta == 1 ? meta4p1 : kPrismMeta == 2 ? meta4p2
                         : kMarcDraft == 1 ? meta4m1 : kMarcDraft == 2 ? meta4m2 : kMarcDraft == 3 ? meta4m3 : kWillowMeta == 1 ? meta4w1 : kWillowMeta == 2 ? meta4w2 : kWillowMeta == 3 ? meta4w3 : kWillowMeta == 4 ? meta4w4 : meta4;
        const auto mine = cambc::draft::current_draft(cambc::team::ally);
        for (const auto pick : list) {
            if (std::find(mine.begin(), mine.end(), pick) != mine.end()) continue;
            try { draft_pick(pick); return; } catch (const cambc::error&) {}
        }
    }
    constexpr int kStunDraft = 1;
    if (kStunDraft > 0) {
        bool stun = !ranged;
        if (kStunDraft == 2 && !stun) {
            int far = 0, near = 0;
            for (const auto e : cambc::draft::current_draft(cambc::team::enemy)) {
                const bool r = e == champion_draft::stellar || e == champion_draft::prism || e == champion_draft::tavi || e == champion_draft::vesper_vale ||
                               e == champion_draft::willow || e == champion_draft::cassi_and_issac;
                (r ? far : near) += 1;
            }
            stun = far >= 2 && far > near;
        }
        if (stun) {
            constexpr std::array stun_list{
                champion_draft::heart_of_ruin, champion_draft::ryth, champion_draft::stellar, champion_draft::ren, champion_draft::marcella, champion_draft::varg,
                champion_draft::cassi_and_issac, champion_draft::tavi, champion_draft::prism, champion_draft::vendetta, champion_draft::vesper_vale,
            };
            const auto mine = cambc::draft::current_draft(cambc::team::ally);
            for (const auto pick : stun_list) {
                if (std::find(mine.begin(), mine.end(), pick) != mine.end()) continue;
                try { draft_pick(pick); return; } catch (const cambc::error&) {}
            }
        }
    }
    // Four-pick experiments: kFarmer4 (rows) 1 C&I, Varg, Stellar, Ren; 2 C&I, Varg, Ren, Ryth.
    // kRanged4 (interlock) 1 C&I, Stellar, Ren, Ryth; 2 C&I, Stellar, Ren, Varg.
    constexpr int kFarmer4 = 0;
    constexpr int kRanged4 = 0;
    constexpr int kCloseRyth = 8;
    // kCloseRen: close spawns and no camp of two or more fighting monsters (rushbait-v2: single monsters only), Ren for Varg:
    // Varg's splash needs packed monsters (user, Oct 19; ladder: Fish, Nyx, Tartarus draft C&I, Stellar, Ren, Ryth there and we
    // lost all six bench games with C&I, Varg, Stellar, Ryth)
    constexpr bool kCloseRen = false;
    constexpr std::array f4_ren{
        champion_draft::cassi_and_issac, champion_draft::varg, champion_draft::stellar, champion_draft::ren, champion_draft::vendetta, champion_draft::ryth, champion_draft::tavi, champion_draft::marcella, champion_draft::vesper_vale, champion_draft::willow, champion_draft::prism,
    };
    constexpr std::array f4_renryth{
        champion_draft::cassi_and_issac, champion_draft::varg, champion_draft::ren, champion_draft::ryth, champion_draft::stellar, champion_draft::vendetta, champion_draft::tavi, champion_draft::marcella, champion_draft::vesper_vale, champion_draft::willow, champion_draft::prism,
    };
    // 3: Mite's rows draft (C&I, Varg, Vendetta, Ryth); 4: Univ's (C&I, Varg, Stellar, Tavi) (Oct 17 top-team study;
    // rows only: 3 -15, 4 -120 (seeds 72-75): off)
    constexpr std::array f4_mite{
        champion_draft::cassi_and_issac, champion_draft::varg, champion_draft::vendetta, champion_draft::ryth, champion_draft::stellar, champion_draft::ren, champion_draft::tavi, champion_draft::marcella, champion_draft::vesper_vale, champion_draft::willow, champion_draft::prism,
    };
    constexpr std::array f4_univ{
        champion_draft::cassi_and_issac, champion_draft::varg, champion_draft::stellar, champion_draft::tavi, champion_draft::vendetta, champion_draft::ryth, champion_draft::ren, champion_draft::marcella, champion_draft::vesper_vale, champion_draft::willow, champion_draft::prism,
    };
    constexpr std::array r4_ryth{
        champion_draft::cassi_and_issac, champion_draft::stellar, champion_draft::ren, champion_draft::ryth, champion_draft::tavi, champion_draft::varg, champion_draft::prism, champion_draft::vendetta, champion_draft::vesper_vale, champion_draft::willow, champion_draft::marcella,
    };
    // Spawns close (rushbait): Mite's C&I, Varg, Stellar, Ryth (they take each of their 5 wolves every ~68 rounds, we every ~140)
    // (rushbait 8 seeds vs C&I/Stellar/Ren/Ryth: +10 +-71, pace 871 -> 805; v76 scrims with Ryth for Tavi: procless 540 -> 284, Mite 476 -> 534)
    constexpr std::array r4_close{
        champion_draft::cassi_and_issac, champion_draft::varg, champion_draft::stellar, champion_draft::ryth, champion_draft::ren, champion_draft::tavi, champion_draft::prism, champion_draft::vendetta, champion_draft::vesper_vale, champion_draft::willow, champion_draft::marcella,
    };
    constexpr std::array r4_varg{
        champion_draft::cassi_and_issac, champion_draft::stellar, champion_draft::ren, champion_draft::varg, champion_draft::tavi, champion_draft::ryth, champion_draft::prism, champion_draft::vendetta, champion_draft::vesper_vale, champion_draft::willow, champion_draft::marcella,
    };
    {
        const bool farm4 = kFarmer4 > 0 && !ranged && size == 4 && !elk_draft && !kVargDraft && !(kWholeTeamDraft && whole_team_map());
        // kCloseRyth: four ranged picks with the spawns this close: r4_close (v76: Ryth for Tavi) (2.2.0 ranked rushbait: 0/11 since v66 with
        // C&I/Stellar/Tavi/Ren; nearly every team that beat us drafted Ryth, Ren, Stellar, C&I) (local, 4 seeds: rushbait -197
        // margin but pace 969 -> 935, all 32 still won)
        const bool close_ryth = kCloseRyth > 0 && kRanged4 == 0 && ranged && size == 4 && !elk_draft && !kVargDraft && !packs && spawns_close(kCloseRyth);
        const bool rng4 = (kRanged4 > 0 && ranged && size == 4 && !elk_draft && !kVargDraft && !packs) || close_ryth;
        if (farm4 || rng4) {
            const bool close_ren = close_ryth && kCloseRen && multi_hitter_groups() == 0;
            const auto& f4 = farm4 ? (kFarmer4 == 1 ? f4_ren : kFarmer4 == 3 ? f4_mite : kFarmer4 == 4 ? f4_univ : f4_renryth) : (close_ren ? r4_ryth : close_ryth ? r4_close : kRanged4 == 1 ? r4_ryth : r4_varg);
            const auto chosen4 = cambc::draft::current_draft(cambc::team::ally);
            for (const auto pick : f4) {
                if (std::find(chosen4.begin(), chosen4.end(), pick) != chosen4.end()) continue;
                try { draft_pick(pick); return; } catch (const cambc::error&) {}
            }
        }
    }
    // Three-pick farmer drafts (expanse): 0 as farmers (Ven, Var, C&I); 1 C&I, Stellar, Ren; 2 C&I, Varg, Ren;
    // 3 Vendetta, Varg, Stellar; 4 C&I, Varg, Stellar
    // (2.2.0, collision+expanse 6 seeds vs 4 bots: 4 +25 +-7 (expanse +51, pace 431 -> 417; top teams draft C&I, Stellar, Varg there))
    constexpr int kFarmer3 = 3;
    constexpr std::array farmers3_sr{
        champion_draft::cassi_and_issac, champion_draft::stellar, champion_draft::ren, champion_draft::varg, champion_draft::vendetta, champion_draft::ryth, champion_draft::tavi, champion_draft::marcella, champion_draft::vesper_vale, champion_draft::willow, champion_draft::prism,
    };
    constexpr std::array farmers3_vr{
        champion_draft::cassi_and_issac, champion_draft::varg, champion_draft::ren, champion_draft::stellar, champion_draft::vendetta, champion_draft::ryth, champion_draft::tavi, champion_draft::marcella, champion_draft::vesper_vale, champion_draft::willow, champion_draft::prism,
    };
    constexpr std::array farmers3_nt{
        champion_draft::vendetta, champion_draft::varg, champion_draft::stellar, champion_draft::cassi_and_issac, champion_draft::ren, champion_draft::ryth, champion_draft::tavi, champion_draft::marcella, champion_draft::vesper_vale, champion_draft::willow, champion_draft::prism,
    };
    constexpr std::array farmers3_vs{
        champion_draft::cassi_and_issac, champion_draft::varg, champion_draft::stellar, champion_draft::vendetta, champion_draft::ren, champion_draft::ryth, champion_draft::tavi, champion_draft::marcella, champion_draft::vesper_vale, champion_draft::willow, champion_draft::prism,
    };
    // 5: C&I, Varg, Vendetta (2.2.x ranked expanse after the map update: Nameless and Sneaky won 5 of 5 with it)
    constexpr std::array farmers3_vv{
        champion_draft::cassi_and_issac, champion_draft::varg, champion_draft::vendetta, champion_draft::stellar, champion_draft::ren, champion_draft::ryth, champion_draft::tavi, champion_draft::marcella, champion_draft::vesper_vale, champion_draft::willow, champion_draft::prism,
    };
    if (kFarmer3 > 0 && !ranged && size <= 3 && !elk_draft && !kVargDraft) {
        const auto& f3 = kFarmer3 == 1 ? farmers3_sr : kFarmer3 == 2 ? farmers3_vr : kFarmer3 == 3 ? farmers3_nt : kFarmer3 == 5 ? farmers3_vv : farmers3_vs;
        const auto chosen3 = cambc::draft::current_draft(cambc::team::ally);
        for (const auto pick : f3) {
            if (std::find(chosen3.begin(), chosen3.end(), pick) != chosen3.end()) continue;
            try { draft_pick(pick); return; } catch (const cambc::error&) {}
        }
    }
    // Five-pick farmer drafts (lanes, monolith): 0 as farmers; 1 Ren for Stellar; 2 Ren for Vendetta; 3 Tavi for Ryth;
    // 4 Ren for Ryth (ranked lanes/monolith winners field Ren in most drafts). kFarmer5SinglesOnly: only on maps with no
    // camp of two or more fighting monsters (Vendetta's kill resets pay on packs).
    // (8 seeds lanes+monolith: 2 lanes +103, monolith -89, vs v48 +41; 16 seeds lanes: 2 +93 +-21, vs v48 +124 vs -31,
    // deaths 2.57 vs 3.93 a game; 4 +20 +-20; 1 -52, 3 -75)
    // v58 (2.2.0 engine): Ren for Vendetta on every 5-pick farmer map but boss maps (17 of 19 ranked monolith drafts that
    // beat us field Ren; Nameless's is ours with Ren for Vendetta): alone +40 on those maps, with the twins economy
    // +26 / +32 overall (monolith +94 / +37, ambush +67 / +106, pilgrimage +102 / +162)
    constexpr int kFarmer5 = 2;
    constexpr bool kFarmer5SinglesOnly = false;
    constexpr std::array farmers5_ren{
        champion_draft::vendetta, champion_draft::varg, champion_draft::cassi_and_issac, champion_draft::ryth, champion_draft::ren, champion_draft::stellar, champion_draft::tavi, champion_draft::marcella, champion_draft::vesper_vale, champion_draft::willow, champion_draft::prism,
    };
    constexpr std::array farmers5_noven{
        champion_draft::ren, champion_draft::varg, champion_draft::cassi_and_issac, champion_draft::ryth, champion_draft::stellar, champion_draft::vendetta, champion_draft::tavi, champion_draft::marcella, champion_draft::vesper_vale, champion_draft::willow, champion_draft::prism,
    };
    constexpr std::array farmers5_tavi{
        champion_draft::vendetta, champion_draft::varg, champion_draft::cassi_and_issac, champion_draft::tavi, champion_draft::stellar, champion_draft::ryth, champion_draft::marcella, champion_draft::ren, champion_draft::vesper_vale, champion_draft::willow, champion_draft::prism,
    };
    // 5: Mite's monolith draft (Ryth, C&I, Stellar, Varg, Tavi); 6: Univ's (C&I, Stellar, Ren, Varg, Tavi) (Oct 17 top-team study;
    // seeds 76-79: 5 -19 +-8 (monolith -211, ambush -212), 6 -5 +-8 (monolith -156))
    constexpr std::array farmers5_mite{
        champion_draft::varg, champion_draft::cassi_and_issac, champion_draft::ryth, champion_draft::stellar, champion_draft::tavi, champion_draft::ren, champion_draft::vendetta, champion_draft::marcella, champion_draft::vesper_vale, champion_draft::willow, champion_draft::prism,
    };
    constexpr std::array farmers5_univ{
        champion_draft::ren, champion_draft::varg, champion_draft::cassi_and_issac, champion_draft::stellar, champion_draft::tavi, champion_draft::ryth, champion_draft::vendetta, champion_draft::marcella, champion_draft::vesper_vale, champion_draft::willow, champion_draft::prism,
    };
    constexpr std::array farmers5_noryth{
        champion_draft::vendetta, champion_draft::varg, champion_draft::cassi_and_issac, champion_draft::ren, champion_draft::stellar, champion_draft::ryth, champion_draft::tavi, champion_draft::marcella, champion_draft::vesper_vale, champion_draft::willow, champion_draft::prism,
    };
    // kFarmer5Boss: also on boss maps (stampede: Ren's draft 140 rounds faster alone, but -232 margin vs local bots).
    constexpr bool kFarmer5Boss = false;
    // kRanged5Farm: the 5-pick farmer draft on 5-pick maps with close spawns too (corners: 5 teams that beat us draft C&I, Ren, Ryth, Stellar, Varg)
    constexpr bool kRanged5Farm = false;
    // kWillowBig: on 5-pick farmer maps 60+ tiles across (ambush, lanes, pilgrimage, stampede), Willow for the last
    // farmer (Stellar): her heals keep the tanks farming instead of walking home across the map.
    // (4 big maps, 8 seeds, with bot.cpp kWillowHeal: -20 +-41, ambush +29, lanes +9, pilgrimage +3, stampede -120;
    // also kWillowMedic -235; every 5-pick farmer map (kWillowSpan 0) -102: eight -326, monolith -127)
    constexpr bool kWillowBig = false;
    constexpr int kWillowSpan = 60;  // map width or height that counts as big (0: every 5-pick farmer map)
    constexpr int kWillowFor = 0;    // 0 for Stellar; 1 for Ren, and not on boss maps (stampede)
                                     // (1: ambush, lanes, pilgrimage 8 seeds -3 +-27: pilgrimage +59 (pace 801 -> 750), lanes +34, ambush -103)
    const bool willow = kWillowBig && !ranged && size == 5 && !elk_draft && !kVargDraft &&
                        std::max(cambc::map::width(), cambc::map::height()) >= kWillowSpan && (kWillowFor == 0 || !boss_map());
    constexpr std::array farmers5_willow_stellar{
        champion_draft::ren, champion_draft::varg, champion_draft::cassi_and_issac, champion_draft::ryth, champion_draft::willow, champion_draft::stellar, champion_draft::vendetta, champion_draft::tavi, champion_draft::marcella, champion_draft::vesper_vale, champion_draft::prism,
    };
    constexpr std::array farmers5_willow_ren{
        champion_draft::varg, champion_draft::cassi_and_issac, champion_draft::ryth, champion_draft::stellar, champion_draft::willow, champion_draft::ren, champion_draft::vendetta, champion_draft::tavi, champion_draft::marcella, champion_draft::vesper_vale, champion_draft::prism,
    };
    const auto& farmers5_willow = kWillowFor == 1 ? farmers5_willow_ren : farmers5_willow_stellar;
    constexpr std::array farmers_willow{
        champion_draft::vendetta, champion_draft::varg, champion_draft::cassi_and_issac, champion_draft::ryth, champion_draft::willow, champion_draft::stellar, champion_draft::tavi, champion_draft::marcella, champion_draft::ren, champion_draft::vesper_vale, champion_draft::prism,
    };
    if (kFarmer5 > 0 && !ranged && size == 5 && !elk_draft && !kVargDraft && !(kFarmer5SinglesOnly && multi_hitter_groups() > 0) &&
        (kFarmer5Boss || !boss_map())) {
        const auto& f5 = willow ? farmers5_willow : kFarmer5 == 1 ? farmers5_ren : kFarmer5 == 2 ? farmers5_noven : kFarmer5 == 3 ? farmers5_tavi : kFarmer5 == 5 ? farmers5_mite : kFarmer5 == 6 ? farmers5_univ : farmers5_noryth;
        const auto chosen5 = cambc::draft::current_draft(cambc::team::ally);
        for (const auto pick : f5) {
            if (std::find(chosen5.begin(), chosen5.end(), pick) != chosen5.end()) continue;
            try { draft_pick(pick); return; } catch (const cambc::error&) {}
        }
    }
    const auto& preferences = elk_draft ? (kElkFarmers == 2 ? elk_ranged : kElkPick == 1 ? elk_ryth : elk_varg) : kVargDraft ? (size <= 3 ? varg3 : size == 4 ? varg4 : varg5) : kWholeTeamDraft && whole_team_map() ? whole_team : willow ? farmers_willow : !ranged ? (kFarmerStellar && size == 4 ? farmers_aoe : farmers) : packs ? (kPacksPick == 2 ? small_ranged_ren : kPacksPick == 1 ? small_ranged_tavi : small_ranged_varg) : size <= 3 ? small_ranged : size == 4 ? four_ranged : kRanged5Farm ? farmers5_noven : five_ranged;

    const auto chosen = cambc::draft::current_draft(cambc::team::ally);
    for (const auto pick : preferences) {
        if (std::find(chosen.begin(), chosen.end(), pick) != chosen.end()) continue;
        try {
            draft_pick(pick);
            return;
        } catch (const cambc::error&) {
            // Rejected (e.g. already ours); try the next preference.
        }
    }
}

void play_draft() {
    static bool planned = false;
    pick_champion();
    // The first draft turn has 10x fuel: after the pick, the static map plan for the champions' set-up (bot.cpp
    // kDraftPlan, ~100-150k fuel). Skipped when the turn has too little left, so the next pick is never at risk.
    if (!planned && cambc::fuel_remaining() > 400000) {
        planned = true;
        bamboo_submit_draft_plan();
    }
}
