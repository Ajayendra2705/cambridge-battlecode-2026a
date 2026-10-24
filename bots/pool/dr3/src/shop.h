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

// Items a champion owns, in shards (an emblem was five shards): item counts are public for every visible champion.
int wealth_of(const cambc::champion& c) {
    const auto counts = c.item_count();
    int w = 0;
    for (int i = 0; i < static_cast<int>(cambc::item_type::enum_type::count); ++i) {
        const auto x = cambc::item_type{static_cast<cambc::item_type::enum_type>(i)};
        w += static_cast<int>(counts[x]) * (x.result() ? 1 : 5);
    }
    return w;
}
// Wealth of the champion in a slot, or -1 when that teammate is out of view (and so not at this capture).
int slot_wealth_now(int s) {
    if (s == W.slot) return wealth_of(cambc::self());
    for (const auto& a : S.allies) {
        if (handle_id(a.ch) != W.slot_ids[s]) continue;
        try {
            return wealth_of(a.ch);
        } catch (const cambc::error&) {
            return -1;
        }
    }
    return -1;
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
    for (int guard = 0; guard < 20; ++guard) {
        const auto counts = me.item_count();
        it choice = plan[3];
        // Vendetta: top-10 teams end with Bruiser strength and Bruiser health about 2:1 instead of Power.
        if (t == cambc::champion_type::vendetta) {
            auto owned = [&](it x) { const auto e = x.result(); return static_cast<int>(counts[x]) + (e ? 5 * static_cast<int>(counts[*e]) : 0); };
            choice = owned(it::bruiser_shard_of_strength) <= 2 * owned(it::bruiser_shard_of_health) ? it::bruiser_shard_of_strength : it::bruiser_shard_of_health;
        }
        for (int i = 0; i < 3; ++i) {
            const auto emblem = plan[i].result();
            if (emblem && counts[*emblem] == 0) { choice = plan[i]; break; }
        }
        if (me.gold_count() < choice.cost() || !me.can_buy(choice)) break;
        me.buy(choice);
        cached_dps_round = -100;
    }
}
