// Part of bot.cpp: Few-round fight simulator between nearby champions, and this champion's own damage per round.
// Unity build: bot.cpp includes this inside its anonymous namespace; not a standalone header.

// ---- Fight simulation ----
// A few rounds of focus fire between the champions near a fight, using live cooldowns. Each unit closes on the
// other side (melee may step and hit, ranged either steps or shoots), casts its best ready spell (stuns first)
// and hits the weakest living opponent. Cassi and Issac fall together.
// reach: the farthest distance at which the cast lands (a dash travels 2 and hits radius 1 around its landing: 3).
struct SimSlot { float dmg = 0; int cd = 99; bool stun = false, reset = false; int reach = 4; };
struct SimUnit {
    float hp = 0, str = 0;
    int range = 1, d = 99;
    std::array<SimSlot, 2> slots{};
    int link = -1;       // Index of the linked body (Cassi/Issac), -1 if none.
    bool stunned = false;
};

template <class C> std::array<SimSlot, 2> read_slots(const C& c) {
    std::array<SimSlot, 2> out{};
    // Live cooldowns need the champion in view: out of view every read threw (726 per 80 games in the bf2 audit).
    cambc::detail::champion_info info{};
    if (cambc::detail::sdk_champion(handle_id(c), &info) != 0 || info.x < 0 || !in_view(vec2{info.x, info.y}))
        return out;
    int i = 0;
    for (const auto& ab : c.abilities()) {
        if (i >= 2) break;
        auto& s = out[i++];
        try {
            s.cd = ab.cooldown();
            s.stun = ab.is_cc();
            s.reset = ab.is_attack_reset();
            if (ab.is_damage() || ab.is_aoe_damage() || ab.is_cc() || ab.is_dash()) s.dmg = ab.damage_amount();
            // Reach and stun from the metadata: Heart of Ruin's dash lands within 3 and stuns, but counted as a range-4
            // spell without stun before.
            if (ab.info())
                std::visit([&](const auto& a) {
                    using T = std::decay_t<decltype(a)>;
                    if constexpr (std::is_same_v<T, cambc::ability_dash>) {
                        s.reach = static_cast<int>(a.range) + std::max(1, static_cast<int>(a.radius));
                        if (a.duration > 0) s.stun = true;
                    } else if constexpr (requires { a.range; a.radius; }) {
                        s.reach = static_cast<int>(a.range) + static_cast<int>(a.radius);
                    } else if constexpr (requires { a.range; }) {
                        s.reach = static_cast<int>(a.range);
                    }
                }, *ab.info());
        } catch (const cambc::error&) {
            s.cd = 99;
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
SimResult simulate_fight(std::array<std::vector<SimUnit>, 2> u, int rounds, bool them_first) {
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
                t->hp -= dmg;
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

float my_dps() {
    if (S.round - cached_dps_round < 10) return cached_dps;
    auto& me = cambc::self();
    float d = S.str, spell = 0;
    for (const auto& ab : me.abilities()) {
        if (ab.is_damage() || ab.is_aoe_damage()) d += ab.damage_amount() / 8.0f;
        // Stuns that also deal damage (Tavi, Ren) report as crowd control, not damage.
        if (ab.is_damage() || ab.is_aoe_damage() || ab.is_cc()) {
            try {
                spell += ab.damage_amount() / 8.0f;
            } catch (const cambc::error&) {
            }
        }
        if (ab.is_attack_reset()) d += S.str / 8.0f;
    }
    cached_dps = d;
    cached_spell_dps = spell;
    cached_dps_round = S.round;
    return cached_dps;
}

// Damage per round from spells alone: they reach 4 tiles, one beyond any camp's attack range.
float my_spell_dps() {
    my_dps();
    return cached_spell_dps;
}
