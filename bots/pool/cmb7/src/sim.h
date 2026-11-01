// Part of bot.cpp: Few-round fight simulator between nearby champions, and this champion's own damage per round.
// Unity build: bot.cpp includes this inside its anonymous namespace; not a standalone header.

// ---- Fight simulation ----
// A few rounds of focus fire between the champions near a fight, using live cooldowns. Each unit closes on the
// other side (melee may step and hit, ranged either steps or shoots), casts its best ready spell (stuns first)
// and hits the weakest living opponent. Cassi and Issac fall together.
// reach: the farthest distance at which the cast lands (a dash travels 2 and hits radius 1 around its landing: 3).
// dash, move: a dash and its travel; roots: the spell cannot share a turn with a walk (micro.h reads these).
struct SimSlot { float dmg = 0; int cd = 99; bool stun = false, reset = false; int reach = 4; bool dash = false, roots = false; int move = 0; };
struct SimUnit {
    float hp = 0, str = 0;  // hp: health plus shield; str: basic attack damage (the Heart of Ruin bonus included).
    float mit = 1.0f;       // Damage this unit takes per point dealt (a Durability emblem: 0.9).
    int range = 1, d = 99;
    std::array<SimSlot, 2> slots{};
    int link = -1;       // Index of the linked body (Cassi/Issac), -1 if none.
    bool stunned = false;
};

// Fuel (mi6, rebased as mi7 and mi8): a slot's design (kind, stun, reset, reach, dash travel, rooting) never changes, so
// it is read once per champion; each round reads only the cooldown and the cast's damage, through the raw host calls,
// whose error codes stand in for the accessors' throws. About 480 fuel a champion instead of 1,080 (0 mismatches against
// the accessor version: mi6 in 91,474 reads, mi7 in 24 games).
struct SlotDesign {
    std::uint32_t slot = 0;
    bool reads_dmg = false, cc = false;  // cc: the kind's stun, before a dash's landing stun is added.
    SimSlot s{};                         // Everything but the cooldown and the damage.
};
std::array<SlotDesign, 2> slot_designs(const cambc::champion& c) {
    struct Entry { std::uint32_t id; std::array<SlotDesign, 2> d; };
    static std::vector<Entry> cache;
    const std::uint32_t id = handle_id(c);
    for (const auto& e : cache) if (e.id == id) return e.d;
    std::array<SlotDesign, 2> d{};
    int i = 0;
    for (const auto& ab : c.abilities()) {
        if (i >= 2) break;
        auto& x = d[i++];
        x.slot = ab.slot();
        x.cc = x.s.stun = ab.is_cc();
        x.s.reset = ab.is_attack_reset();
        x.reads_dmg = ab.is_damage() || ab.is_aoe_damage() || ab.is_cc() || ab.is_dash();
        // Reach and stun from the metadata: Heart of Ruin's dash lands within 3 and stuns, but counted as a range-4
        // spell without stun before.
        if (ab.info())
            std::visit([&](const auto& a) {
                using T = std::decay_t<decltype(a)>;
                x.s.roots = a.exclusive_with_movement;
                if constexpr (std::is_same_v<T, cambc::ability_dash>) {
                    x.s.reach = static_cast<int>(a.range) + std::max(1, static_cast<int>(a.radius));
                    x.s.dash = true;
                    x.s.move = static_cast<int>(a.range);
                    if (a.duration > 0) x.s.stun = true;
                } else if constexpr (requires { a.range; a.radius; }) {
                    x.s.reach = static_cast<int>(a.range) + static_cast<int>(a.radius);
                } else if constexpr (requires { a.range; }) {
                    x.s.reach = static_cast<int>(a.range);
                }
            }, *ab.info());
    }
    cache.push_back({id, d});
    return d;
}

template <class C> std::array<SimSlot, 2> read_slots(const C& c) {
    std::array<SimSlot, 2> out{};
    // Live cooldowns need the champion in view: out of view every read threw (726 per 80 games in the bf2 audit).
    cambc::detail::champion_info info{};
    const std::uint32_t id = handle_id(c);
    if (cambc::detail::sdk_champion(id, &info) != 0 || info.x < 0 || !in_view(vec2{info.x, info.y}))
        return out;
    std::array<SlotDesign, 2> d;
    try {
        d = slot_designs(c);
    } catch (const cambc::error&) {
        for (auto& s : out) s.cd = 99;
        return out;
    }
    for (int i = 0; i < 2; ++i) {
        // A turn that ran out of fuel resumes next round, when the champion can have left our view (au14 audit).
        if (stale()) return out;
        auto& s = out[i];
        std::int32_t cd = 0;
        float dmg = 0;
        if (cambc::detail::sdk_champion_cooldown(id, d[i].slot, &cd) != 0) {
            s.cd = 99;
        } else if (d[i].reads_dmg && cambc::detail::sdk_champion_ability_damage(id, d[i].slot, &dmg) != 0) {
            s.cd = 99, s.stun = d[i].cc, s.reset = d[i].s.reset;
        } else {
            s = d[i].s;
            s.cd = cd;
            s.dmg = dmg;
        }
    }
    return out;
}

// Fuel: a champion's slots are read with about 14 host calls; enemies were read twice per turn (damage prediction and
// the fight sim). Their cooldowns cannot change during our turn, so one read per champion per round is exact.
std::array<SimSlot, 2> cached_slots(const cambc::champion& c) {
    struct Entry { std::uint32_t id; int round; std::array<SimSlot, 2> slots; };
    static std::vector<Entry> cache;
    const std::uint32_t id = handle_id(c);
    const int round = static_cast<int>(cambc::round_number());
    for (auto& e : cache)
        if (e.id == id) {
            if (e.round != round) e.slots = read_slots(c), e.round = round;
            return e.slots;
        }
    cache.push_back({id, round, read_slots(c)});
    return cache.back().slots;
}

struct SimResult { int dead[2] = {0, 0}; float hp_frac[2] = {1, 1}; bool unit0_dead = false; };

// side 0 = us (unit 0 is this champion), side 1 = them; `them_first` makes the enemy act first each round.
SimResult simulate_fight(const std::array<std::vector<SimUnit>, 2>& in, int rounds, bool them_first) {
    // A working copy in buffers kept across calls (a copy by value allocated two vectors per call).
    static std::array<std::vector<SimUnit>, 2> u;
    for (int s = 0; s < 2; ++s) u[s].assign(in[s].begin(), in[s].end());
    std::array<float, 2> start{0, 0};
    for (int s = 0; s < 2; ++s) for (const auto& x : u[s]) start[s] += x.hp;
    for (int r = 0; r < rounds; ++r) {
        for (int k = 0; k < 2; ++k) {
            const int s = them_first ? 1 - k : k, o = 1 - s;
            for (auto& x : u[s]) {
                if (x.hp <= 0) continue;
                if (x.stunned) { x.stunned = false; continue; }
                SimUnit* t = nullptr;
                for (auto& y : u[o]) if (y.hp > 0 && (!t || y.hp < t->hp)) t = &y;
                if (!t) break;
                bool moved = false;
                // Close in until a ready spell or the basic attack lands.
                int want = x.range;
                for (const auto& sl : x.slots) if (sl.cd <= 0 && (sl.dmg > 0 || sl.stun)) want = std::max(want, sl.reach);
                if (x.d > want) { --x.d; moved = true; }
                float dmg = 0;
                const bool melee = x.range <= 1;
                // One cast: a stun if the target is not stunned yet, else the biggest damage spell, else a reset.
                SimSlot* cast = nullptr;
                if (!moved) {
                    for (auto& sl : x.slots) if (sl.cd <= 0 && sl.stun && x.d <= sl.reach && !t->stunned) cast = &sl;
                    if (!cast)
                        for (auto& sl : x.slots)
                            if (sl.cd <= 0 && sl.dmg > 0 && x.d <= sl.reach && (!cast || sl.dmg > cast->dmg)) cast = &sl;
                }
                if (!cast && x.d <= x.range && (melee || !moved))
                    for (auto& sl : x.slots) if (sl.cd <= 0 && sl.reset) cast = &sl;
                if (x.d <= x.range && (melee || !moved)) dmg += x.str;
                if (cast) {
                    if (cast->reset) dmg += x.str;
                    dmg += cast->dmg;
                    if (cast->stun) t->stunned = true;
                    cast->cd = 9;  // Cooldown 8 after this turn's tick.
                }
                t->hp -= dmg * t->mit;
                if (t->hp <= 0 && t->link >= 0) u[o][t->link].hp = 0;
            }
        }
        for (auto& side : u) for (auto& x : side) for (auto& sl : x.slots) if (sl.cd > 0) --sl.cd;
    }
    SimResult res;
    for (int s = 0; s < 2; ++s) {
        float left = 0;
        for (const auto& x : u[s]) { if (x.hp <= 0) ++res.dead[s]; else left += x.hp; }
        res.hp_frac[s] = start[s] > 0 ? left / start[s] : 0;
    }
    res.unit0_dead = !u[0].empty() && u[0][0].hp <= 0;
    return res;
}

// Our damage per round: basic attacks and resets plus every damaging cast over its 8-turn cooldown, like a ChampSnap's
// dps. Cached without the Heart of Ruin bonus, which moves with our health and is applied at each call (damage_amount()
// includes the bonus as of its call: divided out).
float my_dps() {
    auto& me = cambc::self();
    const float scale = damage_scale(me.champion_name(), S.hp, S.max_hp);
    if (S.round - cached_dps_round < 10) return cached_dps * scale;
    float d = S.str, spell = 0;
    for (const auto& ab : me.abilities()) {
        // Stuns that also deal damage (Ren, Tavi, Prism) report as crowd control, a landing strike as a dash; only
        // the spells reach 4 tiles (my_spell_dps).
        const bool cast = ab.is_damage() || ab.is_aoe_damage() || ab.is_cc();
        if (cast || ab.is_dash()) {
            try {
                const float x = ab.damage_amount() / scale / 8.0f;
                d += x;
                if (cast) spell += x;
            } catch (const cambc::error&) {
            }
        }
        if (ab.is_attack_reset()) d += S.str / 8.0f;
    }
    cached_dps = d;
    cached_spell_dps = spell;
    cached_dps_round = S.round;
    return cached_dps * scale;
}

// Damage per round from spells alone: they reach 4 tiles, one beyond any camp's attack range.
float my_spell_dps() {
    my_dps();
    return cached_spell_dps * damage_scale(cambc::self().champion_name(), S.hp, S.max_hp);
}
