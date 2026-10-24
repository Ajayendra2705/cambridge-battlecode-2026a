// Part of bot.cpp: Ability use: stuns, area hits, landing dashes, wards, heals, shields, attacks.
// Unity build: bot.cpp includes this inside its anonymous namespace; not a standalone header.

// ---- Abilities ----
int n_cc = 0, n_aoe = 0, n_dmg = 0, n_attack = 0, n_reset = 0;
// Spend one cast on camps: stun the strongest unstunned attacker, else the best area hit, else burst `focus`.
// Dashes that hit on landing (Heart of Ruin): land where the most targets sit within the landing radius.
bool strike_dash(const std::vector<vec2>& targets, bool skip_danger) {
    auto& me = cambc::self();
    if (!me.can_cast() || targets.empty()) return false;
    for (const auto& ab : me.abilities()) {
        if (!ab.is_ready() || !ab.is_dash() || !ab.info()) continue;
        const auto* d = std::get_if<cambc::ability_dash>(&*ab.info());
        if (!d || (d->modifier <= 0 && d->duration <= 0)) continue;
        const int radius = std::max(1, static_cast<int>(d->radius));
        vec2 best{-1, -1};
        int best_hits = 0, best_d = 99;
        for (auto t : ab.valid_tiles().positions()) {
            if (S.occ.is_set(t) || W.terrain.is_set(t)) continue;
            if (skip_danger && in_danger(t)) continue;
            int hits = 0, nearest = 99;
            for (auto x : targets) {
                const int dd = dist(t, x);
                if (dd <= radius) ++hits;
                nearest = std::min(nearest, dd);
            }
            if (hits > best_hits || (hits == best_hits && hits > 0 && nearest < best_d)) best_hits = hits, best = t, best_d = nearest;
        }
        if (best_hits == 0) continue;
        try {
            if (ab.use(best)) { S.me = best; return true; }
        } catch (const cambc::error&) {
        }
    }
    return false;
}

// Keep the free ward a couple of tiles towards the enemy approach so attackers show up before they reach us.
void place_ward_forward() {
    auto& me = cambc::self();
    if (W.ally_spawn.is_set(S.me)) return;
    try {
        if (me.ward_cooldown() > 0) return;
        for (auto w : me.ward_positions()) if (dist(w, S.me) <= 5) return;
        vec2 best{-1, -1};
        int best_v = UNREACH;
        for (auto t : me.ward_placement_tiles().positions()) {
            if (W.terrain.is_set(t)) continue;
            const int v = W.enemy_field.get(t);
            if (v < best_v) best_v = v, best = t;
        }
        if (best.x >= 0) me.place_ward(best);
    } catch (const cambc::error&) {
    }
}

bool use_camp_abilities(const std::vector<const CampSnap*>& live, const CampSnap& focus, bool awake) {
    auto& me = cambc::self();
    if (!me.can_cast()) return false;
    for (const auto& ab : me.abilities()) {
        if (!ab.is_ready() || !ab.is_cc() || !awake) continue;
        const auto tiles = ab.valid_tiles();
        const CampSnap* best = nullptr;
        for (const auto* c : live) {
            if (c->str <= 0 || !tiles.is_set(c->pos)) continue;
            if (!best || c->str > best->str) {
                try {
                    if (c->camp.buffs().has_stun()) continue;
                } catch (const cambc::error&) {
                    continue;
                }
                best = c;
            }
        }
        if (!best) continue;
        try {
            if (ab.can_target_ground() ? ab.use(best->pos) : ab.use(best->camp)) { ++n_cc; return true; }
        } catch (const cambc::error&) {
        }
    }
    if (awake) {
        std::vector<vec2> pts;
        for (const auto* c : live) if (c->str > 0) pts.push_back(c->pos);
        if (strike_dash(pts, false)) { ++n_cc; return true; }
    }
    for (const auto& ab : me.abilities()) {
        if (!ab.is_ready() || !ab.is_aoe_damage()) continue;
        const auto tiles = ab.valid_tiles();
        vec2 best_tile{-1, -1};
        int best_hits = 0;
        for (const auto* c : live) {
            for (int dx = -1; dx <= 1; ++dx) for (int dy = -1; dy <= 1; ++dy) {
                const vec2 t{c->pos.x + dx, c->pos.y + dy};
                if (!cm::is_in_bounds(t) || !tiles.is_set(t)) continue;
                int hits = 0;
                for (const auto* o : live) if (dist(o->pos, t) <= 1) ++hits;
                if (hits > best_hits) best_hits = hits, best_tile = t;
            }
        }
        if (best_hits == 0) continue;
        try {
            if (ab.use(best_tile)) { ++n_aoe; return true; }
        } catch (const cambc::error&) {
        }
    }
    for (const auto& ab : me.abilities()) {
        if (!ab.is_ready() || !ab.is_damage()) continue;
        if (!ab.valid_tiles().is_set(focus.pos)) continue;
        try {
            if (ab.use(focus.camp)) { ++n_dmg; return true; }
        } catch (const cambc::error&) {
        }
    }
    return false;
}

// From spell range: the best area hit, else any damaging spell (stuns included) on the focus target.
bool cast_from_range(const std::vector<const CampSnap*>& live, const CampSnap& focus) {
    auto& me = cambc::self();
    if (!me.can_cast()) return false;
    if (use_camp_abilities(live, focus, false)) return true;
    for (const auto& ab : me.abilities()) {
        if (!ab.is_ready() || !ab.is_cc() || ab.can_target_ground()) continue;
        try {
            if (ab.damage_amount() > 0 && ab.valid_tiles().is_set(focus.pos) && ab.use(focus.camp)) { ++n_dmg; return true; }
        } catch (const cambc::error&) {
        }
    }
    return false;
}

int nearest_enemy_dist(vec2 t) {
    int m = 99;
    for (const auto& e : S.enemies) if (!W.enemy_spawn.is_set(e.pos)) m = std::min(m, dist(t, e.pos));
    return m;
}
bool flee_bush() {
    if (!cambc::self().can_move()) return false;
    const int here = W.spawn_field.get(S.me);
    if (here == UNREACH) return false;
    for (auto d : DIRS) {
        const vec2 t{S.me.x + d.x, S.me.y + d.y};
        if (!cm::is_in_bounds(t) || W.terrain.is_set(t) || S.occ.is_set(t) || !cm::bushes().is_set(t)) continue;
        if (W.spawn_field.get(t) < here && nearest_enemy_dist(t) >= nearest_enemy_dist(S.me)) return safe_move(t);
    }
    return false;
}
// Stun the most dangerous enemy in reach first, then burst the focus target.
bool use_champion_abilities(const ChampSnap& target) {
    auto& me = cambc::self();
    if (!me.can_cast()) return false;
    for (const auto& ab : me.abilities()) {
        if (!ab.is_ready() || !ab.is_cc()) continue;
        const auto tiles = ab.valid_tiles();
        const ChampSnap* best = nullptr;
        for (const auto& e : S.enemies) {
            if (!tiles.is_set(e.pos) || W.enemy_spawn.is_set(e.pos)) continue;
            if (e.ch.passive() == cambc::passive_type::stun_immunity) continue;
            if (!best || e.dps > best->dps) best = &e;
        }
        if (!best) continue;
        try {
            if (best->ch.buffs().has_stun()) continue;
            if (ab.can_target_ground() ? ab.use(best->pos) : ab.use(best->ch)) return true;
        } catch (const cambc::error&) {
        }
    }
    if (strike_dash({target.pos}, false)) return true;
    for (const auto& ab : me.abilities()) {
        if (!ab.is_ready()) continue;
        try {
            if (ab.is_damage()) {
                if (ab.valid_tiles().is_set(target.pos) && ab.use(target.ch)) return true;
            } else if (ab.is_aoe_damage()) {
                if (ab.valid_tiles().is_set(target.pos) && ab.use(target.pos)) return true;
            }
        } catch (const cambc::error&) {
        }
    }
    return false;
}

bool try_attack_reset_and_hit(const cambc::unit& target) {
    auto& me = cambc::self();
    if (me.can_attack() || !me.can_cast()) return false;
    for (const auto& ab : me.abilities()) {
        if (!ab.is_attack_reset() || !ab.is_ready()) continue;
        try {
            if (ab.use() && me.can_attack()) {
                ++n_reset;
                me.attack(target);
                return true;
            }
        } catch (const cambc::error&) {
        }
    }
    return false;
}

void use_support_abilities(bool in_combat) {
    auto& me = cambc::self();
    if (!me.can_cast()) return;
    for (const auto& ab : me.abilities()) {
        if (!ab.is_ready()) continue;
        try {
            if (ab.is_heal()) {
                const ChampSnap* best = nullptr;
                float best_missing = ab.heal_amount() * 0.6f;
                for (const auto& a : S.allies) {
                    const float missing = a.max_hp - a.hp;
                    if (missing > best_missing && ab.valid_tiles().is_set(a.pos)) best_missing = missing, best = &a;
                }
                if (best && ab.use(best->ch)) return;
            }
            // A shield absorbs most when raised before the hits land: any fight, any health.
            if (ab.is_shield() && in_combat) {
                if (ab.use()) return;
            }
        } catch (const cambc::error&) {
        }
    }
}

bool attack_unit(const cambc::unit& target) {
    auto& me = cambc::self();
    if (!me.can_attack()) return false;
    try {
        me.attack(target);
        ++n_attack;
        return true;
    } catch (const cambc::error&) {
        return false;
    }
}
