// Part of bot.cpp: the per-tile fight evaluator (micro, `docs/STRATEGY.md` section 4). The threat on a tile is the
// damage the visible enemy champions can deal there before our next turn, summed over the enemies, from their live
// cooldowns and reach (a walk, a dash, an attack reset, each ready spell), doubled when a ready stun reaches the tile
// (the stunned turn is lost inside their reach), plus the awake camps that would hit us there. The fight branches in
// bot.cpp choose their tiles with it: closing in on the prey, the step after a melee hit, the dash after a shot, the
// kite step, the flee dash and the flee step.
// Unity build: bot.cpp includes this inside its anonymous namespace; not a standalone header.

// One visible enemy champion and what it can do with one turn, from its ready slots. Damage as dealt, before our
// Durability, Jungle and shield (threat_at applies them).
struct Foe {
    vec2 pos;
    float str = 0;        // Basic attack damage (Heart of Ruin's missing-health bonus and the calibration included).
    int walk = 1;         // Farthest basic attack after an optional walk: melee range + 1; a shooter's walk spends its shot.
    int reset_walk = -1;  // A shooter's walk, attack reset and shot.
    bool reset = false;   // A ready attack reset: a second basic attack.
    int dash = -1;        // Farthest basic attack with a ready dash (melee: walk, dash, hit; shooter: dash, then shot).
    int dash_hit = -1;    // Farthest tile a ready striking dash hits (walk, travel, landing radius).
    float dash_dmg = 0;
    std::array<float, 2> spell{};           // Ready damage spells and their reach (a walk first unless the spell roots).
    std::array<int, 2> spell_reach{-1, -1};
    int stun = -1;        // Farthest tile its ready stun lands on.
    int far = 0;          // Farthest tile it reaches at all.
};
std::vector<Foe> foes;
// Awake camps near us. A camp hits the champion nearest to it: `other` is the distance of the nearest other champion.
struct FoeCamp { vec2 pos; int range, other; float str; };
std::vector<FoeCamp> foe_camps;
std::vector<vec2> foe_tiles;  // Enemy champions off their spawn (nearest_enemy_dist without its host calls).
int nearest_foe(vec2 t) {
    int m = 99;
    for (auto q : foe_tiles) m = std::min(m, dist(t, q));
    return m;
}

// Once per turn, after the snapshot: the enemies within 8 (one turn reaches 5 at most, and our tiles lie within 2) and
// the awake camps that can reach the tiles around us. Fuel: the tile choices evaluate up to 30 tiles, so everything a
// tile needs is read here once (mi1 ran out of fuel after round 3 28 times per 48 local games, main 6).
void build_foes() {
    foes.clear();
    foe_camps.clear();
    foe_tiles.clear();
    S.guard = Guard{};
    for (const auto& e : S.enemies) {
        if (dist(S.me, e.pos) > 8) continue;
        if (!W.enemy_spawn.is_set(e.pos)) foe_tiles.push_back(e.pos);
        Foe f;
        f.pos = e.pos;
        // A cast's damage_amount() includes the caster's Heart of Ruin bonus; a basic attack gets it here (mi3 counted
        // it twice on casts and once on our own striking dash).
        const float k = cal_f;
        f.str = e.str * damage_scale(e.type, e.hp, e.max_hp) * k;
        const bool melee = e.range <= 1;
        f.walk = melee ? e.range + 1 : e.range;
        int n = 0;
        for (const auto& s : cached_slots(e.ch)) {
            if (s.cd > 0) continue;
            if (s.reset) {
                // Marcella's stunning attack is a reset: it lands where her basic attack does.
                f.reset = true;
                if (!melee) f.reset_walk = e.range + 1;
                if (s.stun) f.stun = std::max(f.stun, melee ? f.walk : e.range + 1);
            } else if (s.dash) {
                f.dash = std::max(f.dash, s.move + e.range + (melee ? 1 : 0));
                if (s.dmg > 0 || s.stun) f.dash_hit = std::max(f.dash_hit, s.reach + 1), f.dash_dmg = std::max(f.dash_dmg, s.dmg * k);
                if (s.stun) f.stun = std::max(f.stun, s.reach + 1);
            } else if (s.dmg > 0 || s.stun) {
                const int r = s.reach + (s.roots ? 0 : 1);
                if (s.dmg > 0 && n < 2) f.spell[n] = s.dmg * k, f.spell_reach[n++] = r;
                if (s.stun) f.stun = std::max(f.stun, r);
            }
        }
        f.far = std::max({f.walk, f.reset_walk, f.dash, f.dash_hit, f.spell_reach[0], f.spell_reach[1], f.stun});
        foes.push_back(f);
    }
    auto add_camp = [](const CampSnap& c) {
        if (dist(S.me, c.pos) > c.range + 2) return;
        int other = 99;
        for (const auto& a : S.allies) other = std::min(other, dist(a.pos, c.pos));
        for (const auto& e : S.enemies) other = std::min(other, dist(e.pos, c.pos));
        foe_camps.push_back({c.pos, c.range, other, c.str});
    };
    for (const auto& c : S.camps) if (c.awake) add_camp(c);
    for (const auto& c : S.phantoms) add_camp(c);
    if (!foes.empty() || !foe_camps.empty()) S.guard = guard_of(cambc::self());
}

// The most one enemy deals on a tile at distance d with one turn: a basic attack after an optional walk plus one cast
// (a damage spell, or the reset's second hit), a shooter's walk, reset and shot, or a dash then a basic attack. Plus
// half a basic attack for the second action an enemy can get between two of our turns (the teams alternate one
// champion at a time and the starting team swaps every round: one enemy acts twice in half the gaps).
float foe_damage(const Foe& f, int d) {
    const bool basic = d <= f.walk;
    float cast = f.reset && basic ? f.str : 0.0f;
    for (int i = 0; i < 2; ++i) if (d <= f.spell_reach[i]) cast = std::max(cast, f.spell[i]);
    float best = (basic ? f.str : 0.0f) + cast;
    if (!basic && d <= f.reset_walk) best = std::max(best, f.str);
    if (d <= f.dash) best = std::max(best, f.str + (d <= f.dash_hit ? f.dash_dmg : 0.0f));
    else if (d <= f.dash_hit) best = std::max(best, f.dash_dmg);
    return best > 0 ? best + 0.5f * f.str : 0.0f;
}

// The health we lose on a tile before our next turn: our Durability and Jungle emblems cut the hits and our shield
// takes them first (guard_of). skip: the tile of an enemy our hit kills this turn (a dead enemy deals nothing).
float threat_at(vec2 t, vec2 skip = {-1, -1}) {
    float sum = 0, camps = 0;
    bool stunned = false;
    for (const auto& f : foes) {
        const int d = dist(t, f.pos);
        if (d > f.far || f.pos == skip) continue;
        sum += foe_damage(f, d);
        if (d <= f.stun) stunned = true;
    }
    if (stunned) sum *= 2.0f;
    for (const auto& c : foe_camps) {
        const int d = dist(t, c.pos);
        if (d <= c.range && d <= c.other) camps += c.str;
    }
    return std::max(0.0f, sum * S.guard.mit + camps * S.guard.camp - S.guard.shield);
}

// Threat in steps of a tenth of our health: tiles within one step count as equal, and the next key decides.
int threat_band(float t) { return static_cast<int>(t / std::max(1.0f, 0.1f * S.hp)); }

int allies_near(vec2 t) {
    int n = 0;
    for (const auto& a : S.allies) if (dist(t, a.pos) <= 2) ++n;
    return n;
}

// Free tiles one step away (none once we walked or cannot move).
const std::vector<vec2>& step_tiles() {
    static std::vector<vec2> out;
    out.clear();
    if (stale() || S.walked || !cambc::self().can_move()) return out;
    refresh_occ();
    for (auto d : DIRS) {
        const vec2 t{S.me.x + d.x, S.me.y + d.y};
        if (cm::is_in_bounds(t) && !W.terrain.is_set(t) && !S.occ.is_set(t)) out.push_back(t);
    }
    return out;
}

// Landings of our dash when it can be cast now (none otherwise).
const std::vector<vec2>& dash_tiles() {
    static std::vector<vec2> out;
    out.clear();
    if (stale()) return out;
    auto& me = cambc::self();
    if (!me.can_cast()) return out;
    for (const auto& ab : me.abilities()) {
        if (!ab.is_dash() || !castable_now(ab)) continue;
        for (auto t : dash_landings(ab).positions()) out.push_back(t);
        break;
    }
    return out;
}

bool dash_to(vec2 t) {
    if (stale()) return false;
    auto& me = cambc::self();
    if (!me.can_cast()) return false;
    for (const auto& ab : me.abilities()) {
        if (!ab.is_dash() || !castable_now(ab)) continue;
        if (stale()) return false;
        try {
            if (ab.use(t)) { moved_to(t); return true; }
            S.occ.set(t);  // A hidden unit holds the landing tile.
        } catch (const cambc::error&) {
            S.occ.set(t);
        }
        return false;
    }
    return false;
}

bool reset_ready() {
    auto& me = cambc::self();
    if (!me.can_cast()) return false;
    for (const auto& ab : me.abilities()) if (ab.is_attack_reset() && ab.is_ready()) return true;
    return false;
}

// Our damage on one enemy this turn: a basic attack, plus the reset's second hit (`reset`: melee, or a shooter that
// did not walk) or a striking dash's own damage (`dash`: the dash is the turn's one cast). The basic attack carries
// our Heart of Ruin bonus; the dash's damage_amount() has it already. Our slots as the turn began (asked before we
// cast; one read per round).
float hit_damage(bool dash, bool reset) {
    auto& me = cambc::self();
    const float hit = S.str * damage_scale(me.champion_name(), S.hp, S.max_hp);
    float extra = 0;
    if (me.can_cast())
        for (const auto& s : cached_slots(me))
            if (s.cd <= 0 && (dash ? s.dash : s.reset && reset)) extra = std::max(extra, dash ? s.dmg : hit);
    return hit + extra;
}

// A prey our hit kills this turn: its Durability emblem and shield counted (guard_of), a hundredth kept for rounding.
bool kills(const ChampSnap& prey, bool dash, bool reset) {
    const Guard g = guard_of(prey.ch);
    return prey.hp + g.shield <= 0.99f * g.mit * hit_damage(dash, reset);
}

// The prey is in reach and dies to our basic attack and the attack reset's second hit, not to the basic attack alone:
// the turn's one cast goes to the reset. A spell, a stun or a shield cast first left it alive, and so did a shooter's
// dash out after its shot. A shooter that walked has no second shot.
bool needs_reset_kill(const ChampSnap& prey) {
    return dist(S.me, prey.pos) <= S.range && (S.range <= 1 || !S.walked) && kills(prey, false, true) && !kills(prey, false, false);
}

// The prey died to our hit: it no longer threatens any tile.
void drop_foe(const ChampSnap& prey) {
    if (unit_alive(prey.ch)) return;
    for (size_t i = 0; i < foes.size(); ++i)
        if (foes[i].pos == prey.pos) { foes.erase(foes.begin() + static_cast<long>(i)); return; }
}

// The prey is out of reach: close in. First a tile we hit it from this turn (melee: a step or a dash next to it; a
// shooter: a walk into range with the reset's shot, or a dash into range, then the shot) where the threat stays under
// 60% of our health, the least threatened, a step before a dash, then the most allies within 2. Else a step closer
// whose threat stays under 30% of our health, or under what we face here: the nearest to the prey, then the least
// threatened. Else stay: the old closing step walked into the reach of ready stuns with nothing to hit. Returns 1 when
// it moved, 0 when it stayed by choice, -1 when no free step leads closer (the prey is around a wall).
int micro_close_in(const ChampSnap& prey) {
    auto& me = cambc::self();
    const bool melee = S.range <= 1;
    const bool can_hit = me.can_attack();
    const bool reset = !melee && reset_ready();
    const float here = threat_at(S.me);
    const int pd = dist(S.me, prey.pos);
    // Dash in only with the numbers at the landing, or level against a hurt target (dash_next_to, rz12).
    const int need = prey.hp <= 0.4f * prey.max_hp ? 0 : -1;
    // A prey our hit kills this turn adds no threat to the tiles we hit it from.
    const bool kill_step = kills(prey, false, melee), kill_dash = kills(prey, true, false);
    vec2 best{-1, -1};
    bool best_dash = false, best_hit = false, closer = false;
    int best_band = 0, best_pd = 99, best_allies = -1;
    auto consider = [&](vec2 t, bool dash) {
        const int d = dist(t, prey.pos);
        if (!dash && d < pd) closer = true;
        const bool hit = can_hit && d <= S.range && (melee || dash || reset);
        if (!hit && (dash || d >= pd)) return;
        const float th = threat_at(t, hit && (dash ? kill_dash : kill_step) ? prey.pos : vec2{-1, -1});
        if (hit ? th >= 0.6f * S.hp : th >= std::max(0.3f * S.hp, here)) return;
        const int band = threat_band(th), al = allies_near(t);
        bool better = best.x < 0;
        if (!better && hit != best_hit) better = hit;
        else if (!better && hit)
            better = band < best_band || (band == best_band && (dash < best_dash || (dash == best_dash && al > best_allies)));
        else if (!better)
            better = d < best_pd || (d == best_pd && (band < best_band || (band == best_band && al > best_allies)));
        if (better) best = t, best_dash = dash, best_hit = hit, best_band = band, best_pd = d, best_allies = al;
    };
    for (auto t : step_tiles()) consider(t, false);
    if (can_hit && pd <= S.range + 2)
        for (auto t : dash_tiles()) if (margin_at(t) <= need) consider(t, true);
    if (best.x < 0) return closer ? 0 : -1;
    if (best_dash ? !dash_to(best) : !safe_move(best)) return 0;
    if (best_hit) {
        if (melee || best_dash) {
            if (attack_unit(prey.ch)) try_attack_reset_and_hit(prey.ch);
        } else {
            reset_shot_after_walk();
        }
    }
    return 1;
}

// After a melee hit: step to the least threatened tile that keeps the prey in reach, when it is a band safer.
void micro_after_hit(const ChampSnap& prey) {
    if (S.holding || S.range > 1 || !unit_alive(prey.ch)) return;
    const float here = threat_at(S.me);
    vec2 best{-1, -1};
    float best_t = here;
    for (auto t : step_tiles()) {
        if (dist(t, prey.pos) > S.range) continue;
        const float th = threat_at(t);
        if (th < best_t) best_t = th, best = t;
    }
    if (best.x >= 0 && threat_band(best_t) < threat_band(here)) safe_move(best);
}

// A shooter that shot from a tile where the enemies can take half its health before its next turn: dash out (shot,
// then dash) to the least threatened landing, when it is a band safer. The dash is the turn's cast: no reset hit then.
bool micro_shot_dash() {
    if (S.range <= 1 || S.holding) return false;
    const float here = threat_at(S.me);
    if (here < 0.5f * S.hp) return false;
    vec2 best{-1, -1};
    float best_t = here;
    for (auto t : dash_tiles()) {
        const float th = threat_at(t);
        if (th < best_t) best_t = th, best = t;
    }
    return best.x >= 0 && threat_band(best_t) < threat_band(here) && dash_to(best);
}

// Kite: the least threatened step, a band safer than here; ties go to a tile with an enemy in reach for the reset's
// shot (a shooter, `shoot`), then home-wards. A shooter then shoots with the reset. False when no step is safer.
bool micro_kite(bool shoot) {
    const float here = threat_at(S.me);
    const int here_band = threat_band(here);
    const bool reset = shoot && reset_ready();
    vec2 best{-1, -1};
    int best_band = here_band, best_h = 0;
    bool best_shot = false;
    for (auto t : step_tiles()) {
        const int band = threat_band(threat_at(t));
        if (band >= here_band) continue;
        bool shot = false;
        if (reset)
            for (const auto& e : S.enemies)
                if (!W.enemy_spawn.is_set(e.pos) && dist(t, e.pos) <= S.range) { shot = true; break; }
        const int h = W.spawn_field.get(t);
        if (best.x < 0 || band < best_band || (band == best_band && (shot > best_shot || (shot == best_shot && h < best_h))))
            best = t, best_band = band, best_shot = shot, best_h = h;
    }
    if (best.x < 0 || !safe_move(best)) return false;
    if (shoot) reset_shot_after_walk();
    return true;
}

// Fleeing with a dash: a landing nearer home, the least threatened, then the farthest from the nearest enemy, then
// the nearest to home.
bool micro_flee_dash() {
    const int here_h = W.spawn_field.get(S.me);
    if (here_h == UNREACH) return false;
    vec2 best{-1, -1};
    int best_band = threat_band(threat_at(S.me)), best_e = nearest_foe(S.me), best_h = here_h;
    for (auto t : dash_tiles()) {
        const int h = W.spawn_field.get(t);
        if (h == UNREACH || h >= here_h) continue;
        const int band = threat_band(threat_at(t)), e = nearest_foe(t);
        if (band < best_band || (band == best_band && (e > best_e || (e == best_e && h < best_h))))
            best = t, best_band = band, best_e = e, best_h = h;
    }
    return best.x >= 0 && dash_to(best);
}

// Fleeing on foot: the step down to spawn with the least threat, then the farthest from the nearest enemy (up to 7),
// then the nearest to home. False when no step down is free: walk_home takes over (detours, the field).
bool micro_flee_step() {
    const int here_h = W.spawn_field.get(S.me);
    if (here_h == UNREACH) return false;
    vec2 best{-1, -1};
    int best_band = 0, best_e = 0, best_h = 0;
    for (auto t : step_tiles()) {
        const int h = W.spawn_field.get(t);
        if (h >= here_h) continue;
        const int band = threat_band(threat_at(t)), e = std::min(nearest_foe(t), 7);
        if (best.x < 0 || band < best_band || (band == best_band && (e > best_e || (e == best_e && h < best_h))))
            best = t, best_band = band, best_e = e, best_h = h;
    }
    return best.x >= 0 && safe_move(best);
}
