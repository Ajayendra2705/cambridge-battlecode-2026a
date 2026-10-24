// Part of bot.cpp: Few-round fight simulator between nearby champions, and this champion's own damage per round.
// Unity build: bot.cpp includes this inside its anonymous namespace; not a standalone header.

// ---- Fight simulation ----
// A few rounds of focus fire between the champions near a fight, using live cooldowns. Each unit closes on the
// other side (melee may step and hit, ranged either steps or shoots), casts its best ready spell (stuns first)
// and hits the weakest living opponent. Cassi and Issac fall together.
struct SimSlot { float dmg = 0; int cd = 99; bool stun = false, reset = false; };
struct SimUnit {
    float hp = 0, str = 0;
    int range = 1, d = 99;
    std::array<SimSlot, 2> slots{};
    int link = -1;       // Index of the linked body (Cassi/Issac), -1 if none.
    bool stunned = false;
};

template <class C> std::array<SimSlot, 2> read_slots(const C& c) {
    std::array<SimSlot, 2> out{};
    int i = 0;
    for (const auto& ab : c.abilities()) {
        if (i >= 2) break;
        auto& s = out[i++];
        try {
            s.cd = ab.cooldown();
            s.stun = ab.is_cc();
            s.reset = ab.is_attack_reset();
            if (ab.is_damage() || ab.is_aoe_damage() || ab.is_cc() || ab.is_dash()) s.dmg = ab.damage_amount();
        } catch (const cambc::error&) {
            s.cd = 99;
        }
    }
    return out;
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
                // Close in until the spell (4) or basic range lands.
                const int want = std::max(x.range, 4);
                bool spell_ready = false;
                for (const auto& sl : x.slots) if (sl.cd <= 0 && (sl.dmg > 0 || sl.stun)) spell_ready = true;
                if (x.d > (spell_ready ? want : x.range)) { --x.d; moved = true; }
                float dmg = 0;
                const bool melee = x.range <= 1;
                // One cast: a stun if the target is not stunned yet, else the biggest damage spell, else a reset.
                SimSlot* cast = nullptr;
                if (!moved && x.d <= 4) {
                    for (auto& sl : x.slots) if (sl.cd <= 0 && sl.stun && !t->stunned) cast = &sl;
                    if (!cast) for (auto& sl : x.slots) if (sl.cd <= 0 && sl.dmg > 0 && (!cast || sl.dmg > cast->dmg)) cast = &sl;
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
