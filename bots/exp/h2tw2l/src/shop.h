// Part of bot.cpp: Item build per champion type and who takes capture gold.
// Unity build: bot.cpp includes this inside its anonymous namespace; not a standalone header.

// ---- Shopping ----
bool uses_focus(cambc::champion_type t) {
    using ct = cambc::champion_type;
    // Heart of Ruin: its shield and stunning dash scale with focus and its base strength is 30 (engine 3.0.4);
    // top-10 teams build it on focus.
    // Marcella: focus per shard is 15 (strength 5) and her spell deals 2x focus (patch 1.0.0).
    return t == ct::stellar || t == ct::cassi || t == ct::prism || t == ct::ren || t == ct::willow || t == ct::heart_of_ruin
        || t == ct::marcella;
}

// Per item type, in shards: 1 for a shard (it combines into a result), 5 for an emblem. Read once: SDK 4.0.0 has 84 types,
// and asking each for its result on every call doubled wealth_of from 2.1k to 4.0k fuel (fb1 probe, engine 2.0.0).
constexpr int ITEM_TYPES = static_cast<int>(cambc::item_type::enum_type::count);
const std::array<int, ITEM_TYPES>& shard_weights() {
    static const auto weights = [] {
        std::array<int, ITEM_TYPES> w{};
        for (int i = 0; i < ITEM_TYPES; ++i)
            w[i] = cambc::item_type{static_cast<cambc::item_type::enum_type>(i)}.result() ? 1 : 5;
        return w;
    }();
    return weights;
}
int shards_in(const cambc::enum_map<cambc::item_type>& counts) {
    const auto& weights = shard_weights();
    int w = 0, i = 0;
    for (const auto n : counts) w += static_cast<int>(n) * weights[i++];
    return w;
}

// Items a champion owns, in shards (an emblem was five shards): item counts are public for every visible champion.
int wealth_of(const cambc::champion& c) { return shards_in(c.item_count()); }
// Wealth of the champion in a slot, or -1 when that teammate is out of view (and so not at this capture).
// Read once per slot per round: capture claims ask it for every claimant of every reward in a pick, and each read is a
// host call (picks ran out of fuel 116 times per 80 games in the au8 audit once the gold-spread claim used it).
int slot_wealth_now(int s) {
    static std::array<int, MAX_SLOTS> cached{};
    static std::array<int, MAX_SLOTS> cached_round{-1, -1, -1, -1, -1, -1};
    if (s < 0 || s >= MAX_SLOTS) return -1;
    if (cached_round[s] == S.round) return cached[s];
    int w = -1;
    if (s == W.slot) {
        w = wealth_of(cambc::self());
    } else {
        for (const auto& a : S.allies) {
            if (handle_id(a.ch) != W.slot_ids[s]) continue;
            // A teammate can be known while its items are not in our view (117 "Unit is not in vision" per 80 games in
            // the au8 audit, with the tile in view): read them raw and take a refusal as out of view, without a throw.
            cambc::enum_map<cambc::item_type> counts;
            if (cambc::detail::sdk_champion_items(handle_id(a.ch), counts.ptr()) == 0) w = shards_in(counts);
            break;
        }
    }
    cached[s] = w;
    cached_round[s] = S.round;
    return w;
}

// Who should take capture rewards (and so the gold): champions whose damage grows most from shards.
int capture_priority(cambc::champion_type t) {
    using ct = cambc::champion_type;
    switch (t) {
        case ct::varg: return 9;
        case ct::stellar: return 8;
        case ct::vendetta: return 7;
        case ct::ren: return 6;
        case ct::vesper_vale: return 6;
        case ct::issac: return 5;
        case ct::tavi: return 5;
        case ct::ryth: return 4;
        case ct::marcella: return 4;
        case ct::cassi: return 3;
        default: return 2;
    }
}

int pr_ss_n = 0;  // probe h2pr2l (SS)
void shop() {
    auto& me = cambc::self();
    using it = cambc::item_type;
    if (me.gold_count() < 30) return;
    // Emblems in order (Monster for camp damage, then Durability and Bruiser of health to survive bursts),
    // then power shards of the main stat.
    const bool focus = uses_focus(me.champion_name());
    // Melee bruisers that trade blows (Heart of Ruin, Marcella, Ryth) take Bruiser emblems after the core three: 5
    // shards of the main stat plus one of each other stat beats Power (6 of the main stat) once health decides
    // fights. This is how the top-10 teams build them (engine 3.0.4).
    const auto t = me.champion_name();
    // Vesper too: ranks 20-28 build her Bruiser strength 40 : Power strength 31.
    const bool bruiser = t == cambc::champion_type::heart_of_ruin || t == cambc::champion_type::marcella
        || t == cambc::champion_type::ryth || t == cambc::champion_type::vesper_vale;
    const std::array<it, 4> plan = focus
        ? std::array<it, 4>{it::treasure_shard_of_focus, it::durability_shard_of_health, it::jungle_shard_of_health,
                            bruiser ? it::bruiser_shard_of_focus : it::power_shard_of_focus}
        : std::array<it, 4>{it::treasure_shard_of_strength, it::durability_shard_of_health, it::jungle_shard_of_health,
                            bruiser ? it::bruiser_shard_of_strength : it::power_shard_of_strength};
    // Burst casters stay at range and win fights by damage: straight to power after the Monster emblem.
    const auto self_type = me.champion_name();
    const bool burst_caster = self_type == cambc::champion_type::stellar || self_type == cambc::champion_type::tavi;
    // After the Treasure emblem, buy for fight power. Fights go roughly by health x damage, so a purchase is worth its
    // relative gain d(health)/health + d(main)/main, judged per emblem (the emblem bonus comes on completion):
    //   Power:      6 growth of the main stat;  Bruiser: 5 of the main stat + 1 health growth;
    //   Durability: 5 health growth, plus -10% incoming damage (about +11% effective health) on the first one.
    // The old fixed plan bought two health emblems (Durability, Jungle) before any damage: b6 at r500 we held 0.07
    // Power and 0.33 Bruiser emblems per champion against the rivals' 0.43 and 0.77, and lost even fights.
    // Per-shard growth from the engine's champion design, read once (patches change it: the Sprint 3 notes cut Heart of
    // Ruin's focus growth 12 -> 10 and Marcella's 15 -> 14). Same values as the old table on engine 1.0.3 (probe ps1).
    static const cambc::champion_stats design = me.base_stats();
    const auto growth = [&](bool health) -> float {
        return health ? design.health_growth : focus ? design.focus_growth : design.strength_growth;
    };
    const it power = focus ? it::power_shard_of_focus : it::power_shard_of_strength;
    const it bruis = focus ? it::bruiser_shard_of_focus : it::bruiser_shard_of_strength;
    const it dur = it::durability_shard_of_health;
    const it jun = it::jungle_shard_of_health;
    for (int guard = 0; guard < 20; ++guard) {
        const auto counts = me.item_count();
        it choice = plan[0];
        const auto e0 = plan[0].result();
        if (!e0 || counts[*e0] == 0) {
            choice = plan[0];
        } else {
            bool in_progress = false;
            for (it x : {power, bruis, dur, jun})
                if (counts[x] > 0 && counts[x] < 5) choice = x, in_progress = true;
            if (!in_progress) {
                const float hp = std::max(1.0f, me.max_health()), main = std::max(1.0f, focus ? me.focus() : S.str);
                const float gh = growth(true), gm = growth(false);
                const auto ed = dur.result();
                // Heart of Ruin's basic attack scales with strength (30 + 3.5 per shard), which Bruiser-focus also grows; the
                // rivals build it Bruiser-focus (b56 r400: 0.32 emblems per champion, Power none).
                const float v_str = me.champion_name() == cambc::champion_type::heart_of_ruin ? design.strength_growth / std::max(1.0f, S.str) : 0.f;
                const float v_power = 6.f * gm / main, v_bruis = 5.f * gm / main + gh / hp + v_str;
                const float v_dur = 5.f * gh / hp + (ed && counts[*ed] == 0 ? 0.11f : 0.f);
                // Jungle: -30% damage from camps, which deal about half of what we take (0.57 locally, ab2 on four
                // maps): about +15% effective health on the first one. sp1 without it died more mid-game where dr3 won
                // (b6 gem_fields 11 deaths to 3 by r600, elkring 18 to 13 by r800).
                const auto ej = jun.result();
                const float v_jun = 5.f * gh / hp + (ej && counts[*ej] == 0 ? 0.15f : 0.f);
                const float best = std::max({v_power, v_bruis, v_dur, v_jun});
                choice = best == v_power ? power : best == v_bruis ? bruis : best == v_dur ? dur : jun;
                {  // probe h2pr2l (SS): the same choice with the strength read now (S.str is the snapshot's)
                    const float main_now = std::max(1.0f, focus ? me.focus() : me.strength());
                    const float vs_now = me.champion_name() == cambc::champion_type::heart_of_ruin ? design.strength_growth / std::max(1.0f, me.strength()) : 0.f;
                    const float p2 = 6.f * gm / main_now, b2 = 5.f * gm / main_now + gh / hp + vs_now;
                    const float best2 = std::max({p2, b2, v_dur, v_jun});
                    const it choice2 = best2 == p2 ? power : best2 == b2 ? bruis : best2 == v_dur ? dur : jun;
                    if (choice2 != choice) {
                        ++pr_ss_n;
                        std::cout << "SS " << S.round << " " << W.slot << " " << static_cast<int>(S.str) << " " << static_cast<int>(me.strength())
                                  << " " << static_cast<int>(main_now) << '\n';
                    }
                }
            }
        }
        if (me.gold_count() < choice.cost() || !me.can_buy(choice)) break;
        me.buy(choice);
        cached_dps_round = -100;
    }
}
