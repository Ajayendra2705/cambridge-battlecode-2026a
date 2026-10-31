// Part of bot.cpp: Ability use: stuns, area hits, landing dashes, wards, heals, shields, attacks.
// Unity build: bot.cpp includes this inside its anonymous namespace; not a standalone header.

// ---- Abilities ----
int n_cc = 0, n_aoe = 0, n_dmg = 0, n_attack = 0, n_reset = 0;

// A rooting spell ("excludes walking") cannot follow a walk in the same turn: the engine refuses it ("This spell
// cannot be cast after normal movement": 57 per 80 games in the bf2 audit).
bool roots(const cambc::ability& ab) {
    return ab.info() && std::visit([](const auto& a) { return a.exclusive_with_movement; }, *ab.info());
}
bool castable_now(const cambc::ability& ab) { return ab.is_ready() && !(S.walked && roots(ab)); }

// Alive and in view, read from the raw state structs without exceptions: the old check called health() and caught
// the throw for every dead target (about 250 exceptions per game), and an exception costs far more fuel than a call.
bool unit_alive(const cambc::champion& c) {
    cambc::detail::champion_info info{};
    return cambc::detail::sdk_champion(handle_id(c), &info) == 0 && info.x >= 0 && info.health > 0
        && in_view(vec2{info.x, info.y});
}
bool unit_alive(const cambc::camp& c) {
    cambc::detail::camp_state cs{};
    return cambc::detail::sdk_camp(static_cast<std::uint32_t>(static_cast<cambc::handle_camp_t>(c)), &cs) == 0 && cs.health > 0;
}

// Spend one cast on camps: stun the strongest unstunned attacker, else the best area hit, else burst `focus`.
// Dashes that hit on landing (Heart of Ruin): land where the most targets sit within the landing radius.
bool strike_dash(const std::vector<vec2>& targets, bool skip_danger) {
    if (stale()) return false;
    auto& me = cambc::self();
    if (!me.can_cast() || targets.empty()) return false;
    for (const auto& ab : me.abilities()) {
        if (!ab.is_ready() || !ab.is_dash() || !ab.info()) continue;
        const auto* d = std::get_if<cambc::ability_dash>(&*ab.info());
        if (!d || (d->modifier <= 0 && d->duration <= 0)) continue;
        const int radius = std::max(1, static_cast<int>(d->radius));
        vec2 best{-1, -1};
        int best_hits = 0, best_d = 99;
        for (auto t : dash_landings(ab).positions()) {
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
        if (stale()) return false;  // The landing search can run the turn out of fuel.
        try {
            if (ab.use(best)) { moved_to(best); return true; }
            S.occ.set(best);  // A hidden unit holds the landing tile.
        } catch (const cambc::error&) {
            S.occ.set(best);
        }
    }
    return false;
}

// Burst of the visible enemies that can reach a tile next turn.
float exposure_at(vec2 t) {
    float e = 0;
    for (const auto& x : S.enemies)
        if (!W.enemy_spawn.is_set(x.pos) && dist(t, x.pos) <= x.reach) e += x.burst;
    return e;
}

// Melee closing moves onto a tile in attack reach of `target`, the least exposed one: a step, or a dash (any dash;
// Heart of Ruin's striking dash goes through strike_dash).
bool step_next_to(const ChampSnap& target) {
    if (!cambc::self().can_move()) return false;
    vec2 best{-1, -1};
    float best_e = 0;
    for (auto d : DIRS) {
        const vec2 t{S.me.x + d.x, S.me.y + d.y};
        if (!cm::is_in_bounds(t) || W.terrain.is_set(t) || S.occ.is_set(t) || dist(t, target.pos) > S.range) continue;
        const float e = exposure_at(t);
        if (best.x < 0 || e < best_e) best = t, best_e = e;
    }
    return best.x >= 0 && safe_move(best);
}
// Enemy champions within 3 of a tile minus ours there (this champion and the allies within 3).
int margin_at(vec2 t) {
    int m = -1;
    for (const auto& e : S.enemies) if (dist(t, e.pos) <= 3) ++m;
    for (const auto& a : S.allies) if (dist(t, a.pos) <= 3) --m;
    return m;
}
bool dash_next_to(const ChampSnap& target) {
    if (stale()) return false;
    auto& me = cambc::self();
    if (!me.can_cast()) return false;
    // Dash in only with the numbers at the landing, or level against a hurt target: the dash is also the way out. Our
    // Vendetta dashed in 2.87 times per game (the rivals' 1.33) and died within 10 rounds after 0.16 of them (theirs
    // 0.05): level against a target above 40% health after 0.17 (theirs 0.04), one or more short after 0.43 (0.25), and
    // those targets died after 0.12 and 0.06 (rz9 on b13p2, b16p, b17p; `tools/replay/dives.py`).
    const int need = target.hp <= 0.4f * target.max_hp ? 0 : -1;
    for (const auto& ab : me.abilities()) {
        if (!ab.is_dash() || !castable_now(ab)) continue;
        vec2 best{-1, -1};
        float best_e = 0;
        for (auto t : dash_landings(ab).positions()) {
            if (dist(t, target.pos) > S.range || margin_at(t) > need) continue;
            const float e = exposure_at(t);
            if (best.x < 0 || e < best_e) best = t, best_e = e;
        }
        if (best.x < 0) continue;
        if (stale()) return false;
        try {
            if (ab.use(best)) { moved_to(best); return true; }
            S.occ.set(best);
        } catch (const cambc::error&) {
            S.occ.set(best);
        }
    }
    return false;
}

// Altar locks (10 gold): a lock cancels the enemy tribute channels at its altar and blocks enemy tributes there until
// broken with 5 hits; our own team still tributes, and a lock also cancels a channel at an altar holding the rivals'
// own lock (MECHANICS section 9). dl1 spends one only on a channel that wins the game for the rivals (their tributed
// gems plus the carrier's bag reach 1000): in 35% of the platform games we lost before r2000 one of ours stood within
// 6 tiles of that channel's carrier (findings, "Endgame: winning bags and the rivals' last channel"). Within 2 tiles
// of its altar the lock goes down at once; farther away the altar comes back in `to` for a walk. Any visible rival
// carrying a game-winning bag, walking or channelling, comes back in `carrier`, with or without a lock (dl4).
int lock_fail = 0;
bool deny_channel(vec2& to, const ChampSnap*& carrier) {
    carrier = nullptr;
    if (lock_fail > 5) return false;
    auto& me = cambc::self();
    try {
        const int e_sub = static_cast<int>(cambc::global_submitted_gems(team::enemy));
        for (const auto& e : S.enemies) {
            if (W.enemy_spawn.is_set(e.pos) || e_sub + static_cast<int>(e.gems) < cambc::constants::winning_gems) continue;
            carrier = &e;
            bool channel = false;
            try { channel = e.ch.is_submitting_gems(); } catch (const cambc::error&) {}
            if (!channel) continue;
            const auto& lk = me.consumables()[cambc::consumable_type::altar_lock];
            if (lk.count() == 0) return false;
            for (auto a : W.altars) {
                if (dist(e.pos, a) > 1) continue;
                if (cambc::vision::has_altar_lock(a) && !cambc::vision::altar_lock_at(a).is_enemy()) continue;
                if (dist(S.me, a) <= 2) {
                    if (!stale()) lk.use(a);
                    return false;
                }
                to = a;
                return true;
            }
        }
    } catch (const cambc::error&) {
        ++lock_fail;
    }
    return false;
}

// Keep the free ward a couple of tiles towards the enemy approach so attackers show up before they reach us.
void place_ward_forward() {
    if (stale()) return;
    auto& me = cambc::self();
    if (W.ally_spawn.is_set(S.me) || !S.can_act()) return;
    try {
        if (me.ward_cooldown() > 0) return;
        for (auto w : me.ward_positions()) if (dist(w, S.me) <= 5) return;
        vec2 best{-1, -1};
        int best_v = UNREACH;
        // A tile that already holds a ward is refused ("An allied ward already occupies this tile": 26 failed
        // placements per game in the audit build), so the ward never moved forward there.
        const bitboard warded = cv::ward_tiles();
        for (auto t : me.ward_placement_tiles().positions()) {
            if (W.terrain.is_set(t) || warded.is_set(t)) continue;
            const int v = W.enemy_field.get(t);
            if (v < best_v) best_v = v, best = t;
        }
        // The new ward shows units that were out of view at the snapshot, and a move onto one threw "Known occupied
        // destination" (3 of the 9 caught errors per 80 games in the au14 audit): read the occupancy again before it.
        if (best.x >= 0 && !stale()) me.place_ward(best), S.view_moved = true;
    } catch (const cambc::error&) {
    }
}

bool use_camp_abilities(const std::vector<const CampSnap*>& live, const CampSnap& focus, bool awake) {
    if (stale()) return false;
    auto& me = cambc::self();
    if (!me.can_cast()) return false;
    for (const auto& ab : me.abilities()) {
        if (!castable_now(ab) || !ab.is_cc() || !awake) continue;
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
        if (stale()) return false;
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
        if (!castable_now(ab) || !ab.is_aoe_damage()) continue;
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
        if (stale()) return false;
        try {
            if (ab.use(best_tile)) { ++n_aoe; return true; }
        } catch (const cambc::error&) {
        }
    }
    for (const auto& ab : me.abilities()) {
        if (!castable_now(ab) || !ab.is_damage()) continue;
        // The focus camp can have died to this turn's basic attack ("Target must be a visible unit": 55 per 80 games in
        // the bf4 audit): then the weakest other live camp in range.
        const auto tiles = ab.valid_tiles();
        const CampSnap* t = tiles.is_set(focus.pos) && unit_alive(focus.camp) ? &focus : nullptr;
        if (!t)
            for (const auto* c : live)
                if (c != &focus && tiles.is_set(c->pos) && (!t || c->hp < t->hp) && unit_alive(c->camp)) t = c;
        if (!t) continue;
        if (stale()) return false;
        try {
            if (ab.use(t->camp)) { ++n_dmg; return true; }
        } catch (const cambc::error&) {
        }
    }
    return false;
}

// From spell range: the best area hit, else any damaging spell (stuns included) on the focus target.
bool cast_from_range(const std::vector<const CampSnap*>& live, const CampSnap& focus) {
    if (stale()) return false;
    auto& me = cambc::self();
    if (!me.can_cast()) return false;
    if (use_camp_abilities(live, focus, false)) return true;
    for (const auto& ab : me.abilities()) {
        if (!castable_now(ab) || !ab.is_cc() || ab.can_target_ground()) continue;
        try {
            if (ab.damage_amount() > 0 && ab.valid_tiles().is_set(focus.pos) && !stale() && ab.use(focus.camp)) { ++n_dmg; return true; }
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
// Fleeing walked home one tile a turn and never dashed: a chaser that walks as fast kept hitting every round (cand1 on
// b56, decoded by r1000: Vesper died 1.60 times per game, the rivals' Vesper 0.77; Vendetta 1.92 against 1.38). A dash
// gains two tiles: land closer to home, as far from the enemies as possible and outside awake camps' reach.
bool flee_dash() {
    if (stale()) return false;
    auto& me = cambc::self();
    if (!me.can_cast()) return false;
    const int here = W.spawn_field.get(S.me);
    if (here == UNREACH) return false;
    bitboard reach;
    for (const auto& c : S.camps) if (c.awake) reach.draw_chebyshev(c.pos, static_cast<float>(c.range));
    for (const auto& c : S.phantoms) reach.draw_chebyshev(c.pos, static_cast<float>(c.range));
    for (const auto& ab : me.abilities()) {
        if (!ab.is_dash() || !castable_now(ab)) continue;
        vec2 best = S.me;
        int best_e = nearest_enemy_dist(S.me), best_h = here;
        for (auto t : dash_landings(ab).positions()) {
            if (S.occ.is_set(t) || W.terrain.is_set(t) || reach.is_set(t)) continue;
            const int h = W.spawn_field.get(t);
            if (h == UNREACH || h >= here) continue;
            const int e = nearest_enemy_dist(t);
            if (e > best_e || (e == best_e && h < best_h)) best = t, best_e = e, best_h = h;
        }
        if (best == S.me) continue;
        if (stale()) return false;  // The landing search can run the turn out of fuel.
        try {
            if (ab.use(best)) {
                moved_to(best);
                return true;
            }
            S.occ.set(best);
        } catch (const cambc::error&) {
            S.occ.set(best);
        }
    }
    return false;
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
// Stun the most dangerous enemy in reach first, then burst the focus target. Without may_root, spells that root the
// caster are skipped: the turn still has to walk. So is Heart of Ruin's striking dash, which lands next to the target,
// among the enemies the turn then walks away from (nm2 on b13p2, b16p and b17p, 5-champion maps: our Heart dashed, hit
// and walked on in the same turn 2.8 times per game and died within 10 rounds after 28% of those; the rivals' Heart
// 0.2 times).
bool use_champion_abilities(const ChampSnap& target, bool may_root = true) {
    if (stale()) return false;
    auto& me = cambc::self();
    if (!me.can_cast()) return false;
    for (const auto& ab : me.abilities()) {
        if (!castable_now(ab) || !ab.is_cc() || (!may_root && roots(ab))) continue;
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
            if (stale()) return false;
            if (ab.can_target_ground() ? ab.use(best->pos) : ab.use(best->ch)) return true;
        } catch (const cambc::error&) {
        }
    }
    if (may_root && !S.holding && strike_dash({target.pos}, false)) return true;  // A capturer keeps its tile.
    for (const auto& ab : me.abilities()) {
        if (!castable_now(ab) || (!may_root && roots(ab))) continue;
        try {
            if (ab.is_damage()) {
                // The focus target out of range: the weakest enemy in range instead. Marcella's spell was left unused in
                // 461 enemy-fight turns per 80 games (bf2 audit) while another enemy stood in its range.
                const auto tiles = ab.valid_tiles();
                const ChampSnap* t = tiles.is_set(target.pos) && unit_alive(target.ch) ? &target : nullptr;
                if (!t)
                    for (const auto& e : S.enemies)
                        if (tiles.is_set(e.pos) && !W.enemy_spawn.is_set(e.pos) && (!t || e.hp < t->hp) && unit_alive(e.ch)) t = &e;
                if (t && !stale() && ab.use(t->ch)) return true;
            } else if (ab.is_aoe_damage()) {
                if (ab.valid_tiles().is_set(target.pos) && !stale() && ab.use(target.pos)) return true;
            }
        } catch (const cambc::error&) {
        }
    }
    return false;
}

// The unit the reset hit goes to. When the basic attack killed the target, the reset used to be cast and its attack
// then threw ("Target must be a visible enemy or neutral camp"): 40 reset casts per game wasted in the audit build,
// each costing the turn's cast and an 8-turn cooldown. Then hit the weakest enemy champion in reach, else the weakest
// awake camp in reach (a sleeping one would wake), else keep the spell.
template <class U> const cambc::unit* reset_target(const U& target) {
    // Alive and in reach from where we stand now ("Attack target is out of range": 8 per 80 games in the bf4 audit).
    if (unit_alive(target)) {
        try {
            if (dist(S.me, target.position()) <= S.range) return &target;
        } catch (const cambc::error&) {
        }
    }
    const ChampSnap* champ = nullptr;
    for (const auto& e : S.enemies)
        if (dist(S.me, e.pos) <= S.range && !W.enemy_spawn.is_set(e.pos) && unit_alive(e.ch) && (!champ || e.hp < champ->hp))
            champ = &e;
    if (champ) return &champ->ch;
    const CampSnap* camp = nullptr;
    for (const auto& c : S.camps)
        if (c.awake && dist(S.me, c.pos) <= S.range && unit_alive(c.camp) && (!camp || c.hp < camp->hp)) camp = &c;
    return camp ? &camp->camp : nullptr;
}

// A reset restores a spent basic attack, so only after our attack this turn: an attack that is merely blocked (a ranged
// champion that walked) cannot be reset ("An available attack cannot be reset").
template <class U> bool try_attack_reset_and_hit(const U& target) {
    if (stale()) return false;
    auto& me = cambc::self();
    if (!S.attacked || me.can_attack() || !me.can_cast()) return false;
    for (const auto& ab : me.abilities()) {
        if (!ab.is_attack_reset() || !ab.is_ready()) continue;
        const cambc::unit* hit = reset_target(target);
        // The ability list and the target search are host calls: a turn that ran out of fuel here resumed next round
        // with a fresh attack and cast the reset on it (all 5 refusals in the au10 audit).
        if (!hit || stale()) return false;
        try {
            if (ab.use() && me.can_attack()) {
                ++n_reset;
                me.attack(*hit);
                return true;
            }
        } catch (const cambc::error&) {
        }
    }
    return false;
}

void use_support_abilities(bool in_combat) {
    if (stale()) return;
    auto& me = cambc::self();
    if (!me.can_cast()) return;
    for (const auto& ab : me.abilities()) {
        if (!castable_now(ab)) continue;
        try {
            if (ab.is_heal()) {
                const ChampSnap* best = nullptr;
                float best_missing = ab.heal_amount() * 0.6f;
                for (const auto& a : S.allies) {
                    const float missing = a.max_hp - a.hp;
                    if (missing > best_missing && ab.valid_tiles().is_set(a.pos)) best_missing = missing, best = &a;
                }
                if (best && !stale() && ab.use(best->ch)) return;
            }
            // A shield absorbs most when raised before the hits land: any fight, any health. The tile choices after it
            // count it (threat_at).
            if (ab.is_shield() && in_combat) {
                const float amount = ab.shield_amount();
                if (!stale() && ab.use()) {
                    S.guard.shield = std::max(S.guard.shield, amount);
                    return;
                }
            }
        } catch (const cambc::error&) {
        }
    }
}

template <class U> bool attack_unit(const U& target) {
    if (stale()) return false;
    auto& me = cambc::self();
    if (!me.can_attack()) return false;
    // This turn's own spell can have killed the target already (131 attacks on dead targets per 80 games in the audit
    // build): the basic attack then goes to the next unit in reach, as the reset does.
    const cambc::unit* hit = reset_target(target);
    if (!hit || stale()) return false;
    try {
        me.attack(*hit);
        ++n_attack;
        S.attacked = true;
        return true;
    } catch (const cambc::error&) {
        return false;
    }
}

// Walk, reset, shot: a shooter that walked this turn cannot shoot, but the attack reset restores the shot (probe rz5p:
// 63 of 63 landed). The weakest enemy in reach from the new tile.
bool reset_shot_after_walk() {
    if (stale()) return false;
    auto& me = cambc::self();
    if (S.range <= 1 || !S.walked || me.can_attack() || !me.can_cast()) return false;
    const ChampSnap* t = nullptr;
    for (const auto& e : S.enemies)
        if (!W.enemy_spawn.is_set(e.pos) && dist(S.me, e.pos) <= S.range && (!t || e.hp < t->hp)) t = &e;
    if (!t) return false;
    for (const auto& ab : me.abilities()) {
        if (!ab.is_attack_reset() || !ab.is_ready()) continue;
        if (stale()) return false;
        try {
            if (ab.use() && attack_unit(t->ch)) {
                ++n_reset;
                return true;
            }
        } catch (const cambc::error&) {
        }
        break;
    }
    return false;
}

// Every branch of the turn returns early, so an attack can be left unused with something in reach: the audit build
// counted about 2,900 such turns per 80 games (840 in enemy fights with an awake camp in reach, 262 with an enemy
// champion in reach, the rest while walking, capturing or leaving camps). Spend it at the end of the turn: the weakest
// enemy champion in reach, else the weakest awake camp (a sleeping one would wake) that is not fighting an enemy: a
// camp hits its nearest champion, and damage on a camp an enemy is clearing only speeds their capture.
void free_hit() {
    auto& me = cambc::self();
    if (!W.ready || S.round != static_cast<int>(cambc::round_number())) return;  // No snapshot this turn.
    try {
        if (!me.is_alive() || me.is_recalling() || me.is_submitting_gems() || me.is_teleporting() || !me.can_attack()) return;
        // move_towards does not update S.me (bf2 audit: 356 "Attack target is out of range" from the old tile).
        S.me = me.position();
    } catch (const cambc::error&) {
        return;
    }
    const ChampSnap* champ = nullptr;
    for (const auto& e : S.enemies)
        if (dist(S.me, e.pos) <= S.range && !W.enemy_spawn.is_set(e.pos) && unit_alive(e.ch) && (!champ || e.hp < champ->hp))
            champ = &e;
    if (champ) {
        if (attack_unit(champ->ch)) try_attack_reset_and_hit(champ->ch);
        return;
    }
    const CampSnap* camp = nullptr;
    for (const auto& c : S.camps) {
        if (!c.awake || dist(S.me, c.pos) > S.range || (camp && c.hp >= camp->hp)) continue;
        int ours = dist(S.me, c.pos);
        for (const auto& a : S.allies) ours = std::min(ours, dist(a.pos, c.pos));
        bool enemy_closer = false;
        for (const auto& e : S.enemies) if (dist(e.pos, c.pos) < ours) enemy_closer = true;
        if (!enemy_closer && unit_alive(c.camp)) camp = &c;
    }
    if (camp) attack_unit(camp->camp);
}
