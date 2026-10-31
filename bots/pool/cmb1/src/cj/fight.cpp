// Fighting enemy champions, ability use against champions, support casts.
#include "bot.h"
#include "params.h"
namespace cjb {


bool Bot::try_cast_on_enemy(const Seen& e) {
    auto& me = self();
    if (cast_this_turn) return false;
    const vec2 p = me.position();
    auto abs = me.abilities();
    const int d = cheb(p, e.pos);
    for (int s = 0; s < 2; ++s) {
        if (!ahas[s]) continue;
        if (aexcl[s] && moved_this_turn) continue;
        const auto k = akind[s];
        try {
            if (abs[s].cooldown() > 0) continue;
            if ((k == ability_kind::damage || k == ability_kind::cc) && d <= static_cast<int>(arange[s])) {
                if (abs[s].use(e.c)) { cast_this_turn = true; return true; }
            } else if (k == ability_kind::aoe_damage && d <= static_cast<int>(arange[s])) {
                if (abs[s].use(e.pos)) { cast_this_turn = true; return true; }
            } else if (k == ability_kind::dash && amod[s] > 0 && d <= 3 && d >= 1) {
                // Heart of Ruin: land next to the target to damage and stun around it.
                vec2 best = p;
                if (P_HOR_AOE) {
                    // ... where the blast (radius 1) catches the most enemies, the target first.
                    int bs = 0;
                    for (int dx = -2; dx <= 2; ++dx)
                        for (int dy = -2; dy <= 2; ++dy) {
                            const vec2 q{ p.x + dx, p.y + dy };
                            if (q == p || !nav.passable(q) || cheb(q, e.pos) > 1) continue;
                            int sc = 0;
                            for (const auto& o : enemies)
                                if (round == o.seen_round && cheb(o.pos, q) <= 1) sc += (o.index == e.index ? 30 : 20) + (o.hp < 400.f ? 5 : 0);
                            sc = sc * 10 - cheb(q, p);
                            if (sc > bs) { bs = sc; best = q; }
                        }
                } else {
                    int bd = 99;
                    for (int dx = -2; dx <= 2; ++dx)
                        for (int dy = -2; dy <= 2; ++dy) {
                            const vec2 q{ p.x + dx, p.y + dy };
                            if (q == p || !nav.passable(q) || cheb(q, e.pos) > 1) continue;
                            const int dd = cheb(q, p);
                            if (dd < bd) { bd = dd; best = q; }
                        }
                }
                if (best != p && abs[s].use(best)) { cast_this_turn = true; return true; }
            } else if (k == ability_kind::shield && (hurt || d <= 2) && me.health() < me.max_health() * 0.95f) {
                if (abs[s].use(me)) { cast_this_turn = true; return true; }
            }
        } catch (...) {}
    }
    return false;
}

// Dash to strike a target just out of reach: a melee dasher steps (if needed), dashes next to it and hits
// (move 1 + dash 2 + attack: reach 4); a ranged dasher dashes into range and shoots (the dash does not use up the
// attack: reach range + 2). Turns a hopeless chase into hits every round (a melee champion within 2 keeps up).
bool Bot::dash_strike(const Seen& e) {
    if (!P_DASH_ENGAGE || cast_this_turn || round != e.seen_round) return false;
    const int ds = ability_slot(ability_kind::dash);
    if (ds < 0 || amod[static_cast<std::size_t>(ds)] > 0) return false;  // Heart of Ruin's landing dash: try_cast_on_enemy
    auto& me = self();
    if (!me.can_attack()) return false;
    try {
        if (me.abilities()[static_cast<std::size_t>(ds)].cooldown() > 0) return false;
    } catch (...) { return false; }
    const vec2 p = me.position();
    const int range = me.attack_range();
    const int d = cheb(p, e.pos);
    auto other_enemies_adj = [&](vec2 q) {
        int n = 0;
        for (const auto& o : enemies)
            if (o.index != e.index && cheb(o.pos, q) <= std::max(1, o.range)) ++n;
        return n;
    };
    if (!ranged) {
        if (d <= 2 || d > 4) return false;  // within 2: walking in and hitting works without the dash
        vec2 from = p;
        if (d == 4) {
            if (!me.can_move() || moved_this_turn) return false;
            vec2 bq = p;
            int bs = 1 << 30;
            for (auto dv : kDirs) {
                const vec2 q = p + dv;
                if (!nav.passable(q) || cheb(q, e.pos) != 3) continue;
                const int sc = other_enemies_adj(q) * 10 + (bb_test(*world().camp_tiles, q) ? 1 : 0);
                if (sc < bs) { bs = sc; bq = q; }
            }
            if (bq == p) return false;
            try {
                if (!me.move_absolute(bq)) return false;
            } catch (...) { nav.note_refused(bq); return false; }
            moved_this_turn = true;
            nav.begin_turn();
            from = bq;
        }
        vec2 best = from;
        int bs = 1 << 30;
        for (int dx = -2; dx <= 2; ++dx)
            for (int dy = -2; dy <= 2; ++dy) {
                const vec2 q{ from.x + dx, from.y + dy };
                if (q == from || cheb(q, e.pos) != 1 || !nav.passable(q)) continue;
                const int sc = other_enemies_adj(q) * 10 + cheb(q, from);
                if (sc < bs) { bs = sc; best = q; }
            }
        if (best == from) return d == 4;  // stepped already
        try {
            if (!me.abilities()[static_cast<std::size_t>(ds)].use(best)) return d == 4;
        } catch (...) { return d == 4; }
        cast_this_turn = true;
        nav.begin_turn();
        try { me.attack(e.c); attacked_this_turn = true; } catch (...) {}
        LOGC("%d %d DASH_STRIKE d%d\n", round, idx, d);
        return true;
    }
    // Ranged: dash so that the target is within range, keeping as far from it (and the rest) as possible.
    if (d <= range || d > range + 2 || moved_this_turn) return false;
    vec2 best = p;
    int bs = -(1 << 30);
    for (int dx = -2; dx <= 2; ++dx)
        for (int dy = -2; dy <= 2; ++dy) {
            const vec2 q{ p.x + dx, p.y + dy };
            if (q == p || cheb(q, e.pos) > range || !nav.passable(q)) continue;
            const int sc = cheb(q, e.pos) * 10 - other_enemies_adj(q) * 25;
            if (sc > bs) { bs = sc; best = q; }
        }
    if (best == p) return false;
    try {
        if (!me.abilities()[static_cast<std::size_t>(ds)].use(best)) return false;
    } catch (...) { return false; }
    cast_this_turn = true;
    nav.begin_turn();
    try { me.attack(e.c); attacked_this_turn = true; } catch (...) {}
    LOGC("%d %d DASH_STRIKE d%d\n", round, idx, d);
    return true;
}

// Enemy area blasts ready (Heart of Ruin's landing, Ryth/Prism/Stellar areas, Varg's splash): keep a tile between
// me and my allies so one blast does not catch (and stun) several of us.
void Bot::spread_goals(bitboard& goals, const std::vector<const Seen*>& near) {
    if (!P_SPREAD) return;
    bool aoe = false;
    for (const auto* e : near) {
        if (round - e->seen_round > 1) continue;
        if (e->type == champion_type::varg) { aoe = true; break; }
        const bool caster = e->type == champion_type::heart_of_ruin || e->type == champion_type::ryth ||
                            e->type == champion_type::prism || e->type == champion_type::stellar;
        if (!caster) continue;
        const int cd = e->type == champion_type::heart_of_ruin ? e->dash_cd : e->nuke_cd;
        if (!e->cd_known || e->cd_at(cd, round) <= 1) { aoe = true; break; }
    }
    if (!aoe) return;
    const vec2 p = self().position();
    bitboard crowd;
    crowd.clear();
    for (const auto& a : allies)
        if (cheb(a.pos, p) <= 6) crowd.draw_chebyshev(a.pos, 1.f);
    bitboard g2 = goals;
    g2 &= ~crowd;
    if (!g2.is_empty()) goals = g2;
}

// Scheduling priority (takes effect next round): within the team, champions near enemies act first (a chaser
// hits before its target walks off, a hurt champion steps out of reach before they swing), hurt ones first of all.
void Bot::set_turn_priority() {
    if (!P_PRIO) return;
    auto& me = self();
    const vec2 p = me.position();
    int dmin = 99;
    for (const auto& e : enemies) dmin = std::min(dmin, cheb(e.pos, p));
    int pr = 0;
    if (dmin <= P_PRIO_R) {
        const float frac = me.health() / std::max(1.f, me.max_health());
        pr = 100 + (frac < 0.5f ? 50 : 0) + (P_PRIO_R - dmin);
    }
    if (pr == prio_set) return;
    try {
        me.set_priority(pr);
        prio_set = pr;
    } catch (...) {}
}

bool Bot::try_support() {
    auto& me = self();
    if (cast_this_turn) return false;
    const int s = ability_slot(ability_kind::heal);
    if (s < 0) return false;
    const vec2 p = me.position();
    const Seen* best = nullptr;
    float worst = 0.7f;
    for (const auto& a : allies) {
        if (cheb(a.pos, p) > static_cast<int>(arange[s])) continue;
        const float f = a.hp / std::max(1.f, a.max_hp);
        if (f < worst) { worst = f; best = &a; }
    }
    if (!best) return false;
    try {
        auto abs = me.abilities();
        if (abs[s].cooldown() > 0) return false;
        if (abs[s].use(best->c)) { cast_this_turn = true; return true; }
    } catch (...) {}
    return false;
}

// Retreat: follow a path home that avoids enemy reach; otherwise maximise path distance from them.
bool Bot::retreat(const std::vector<vec2>& dangers, const std::vector<int>& ranges) {
    auto& me = self();
    if (!me.can_move() || dangers.empty()) return false;
    World& W = world();
    const vec2 p = me.position();
    bitboard walls = *W.blocked | nav.occupied();
    bitboard danger;
    danger.clear();
    for (std::size_t i = 0; i < dangers.size(); ++i) danger.draw_chebyshev(dangers[i], static_cast<float>(ranges[i] + 1));
    bitboard w2 = walls | danger;
    w2.set(p, false);
    bitboard roots = *W.my_spawn & ~w2;
    if (!roots.is_empty()) {
        distance_field f;
        bitboard vis, dest;
        dest.clear();
        dest.set(p);
        f.compute_to(w2, roots, dest, vis);
        if (const auto mv = f.next_move_from(p)) {
            try { if (me.move(*mv)) return true; } catch (...) {}
        }
    }
    // No safe path: step to maximise walking distance from the enemies, preferring home.
    bitboard eroots;
    eroots.clear();
    for (auto d : dangers) eroots.set(d);
    distance_field fe;
    bitboard vis2;
    fe.compute(*W.blocked, eroots, vis2, 24);
    auto score = [&](vec2 q) {
        int e = df_get(fe, q);
        if (e == distance_field::unreachable) e = 24;
        int h = df_get(*W.f_spawn, q);
        if (h == distance_field::unreachable) h = 300;
        return std::min(e, 12) * 100 - h;
    };
    const int cur = score(p);
    int best = cur;
    vec2 bq = p;
    for (auto d : kDirs) {
        const vec2 q = p + d;
        if (!nav.passable(q)) continue;
        const int sc = score(q);
        if (sc > best) { best = sc; bq = q; }
    }
    if (bq == p) return false;
    try { return me.move_absolute(bq); } catch (...) { return false; }
}

// Tiles from which a champion's opening burst lands: targeted abilities are cast from 4 tiles, dashers close 2 more.
int burst_reach(champion_type t, int range) {
    if (!P_BURST_REACH) return range;
    switch (t) {
    case champion_type::marcella:
    case champion_type::cassi:
    case champion_type::stellar:
    case champion_type::prism:
    case champion_type::tavi:
    case champion_type::ren:
    case champion_type::willow: return 4;
    case champion_type::ryth: return 5;  // area burst: 4 tiles plus its radius
    case champion_type::heart_of_ruin:
    case champion_type::vendetta:
    case champion_type::issac: return 3;  // dash 2, then strike next to it
    case champion_type::vesper_vale: return 5;  // dash 2, then shoot 3
    default: return range;
    }
}

// Race-based escape. Each chaser threatens the tiles within its attack range (+1 for a dash); that front
// spreads one tile per round at walking speed. A tile is safe if I get there before the front does.
// Target: the nearest tile where a recall would complete before the front (or a nuke) arrives, else the
// tile that keeps me furthest ahead, homewards on ties. Returns 1 moved, 0 no move (safe_here: already
// at a recall spot), -1 caught (no tile in reach stays ahead of them).
int Bot::escape(const std::vector<const Seen*>& near, bool& safe_here) {
    safe_here = false;
    auto& me = self();
    if (!me.can_move() || near.empty()) return 0;
    World& W = world();
    const vec2 p = me.position();
    bitboard roots;
    roots.clear();
    int extra = 0;  // nukes reach a recalling champion from beyond the chase front
    for (const auto* e : near) {
        bool dasher = e->type == champion_type::vendetta || e->type == champion_type::vesper_vale || e->type == champion_type::issac ||
                      e->type == champion_type::heart_of_ruin || e->type == champion_type::ren;
        if (P_ENEMY_CD && e->cd_known) dasher = e->cd_at(e->dash_cd, round) <= 1;  // its dash is (nearly) ready
        const int reach = std::max(1, e->range) + (dasher ? 1 : 0);
        roots.draw_chebyshev(e->pos, static_cast<float>(reach));
        extra = std::max(extra, burst_reach(e->type, e->range) - reach);
    }
    roots &= ~*W.blocked;
    if (roots.is_empty()) return 0;
    distance_field ft;
    {
        bitboard vis;
        ft.compute(*W.blocked, roots, vis, static_cast<std::uint16_t>(P_ESC_R + P_ESC_FT_EXTRA));
    }
    bitboard walls = *W.blocked | nav.occupied();
    walls.set(p, false);
    bitboard mr;
    mr.clear();
    mr.set(p);
    distance_field fm;
    bitboard reached;
    fm.compute(walls, mr, reached, static_cast<std::uint16_t>(P_ESC_R));
    const int need = 6 + extra;  // recall: 5 rounds of channel after arriving
    // Hurt: the nearest spot where a recall completes. Healthy: just stay a few tiles ahead of them, homewards.
    const bool hurt_flee = P_ESC_CAP <= 0 || me.health() < P_ESC_RECALL_HP * me.max_health();
    // Direct chunk-indexed reads (fields and boards share the 8x8 chunk order; host reads cost too much here).
    const auto& L = detail::layout();
    const int cw = static_cast<int>(L.chunked_width), cs = static_cast<int>(L.chunk_stride);
    const std::uint16_t* FT = ft.ptr();
    const std::uint16_t* FM = fm.ptr();
    const std::uint16_t* FS = W.f_spawn->ptr();
    const std::uint64_t* RB = reached.ptr();
    constexpr int kFar = 60;
    constexpr std::uint16_t kUn = distance_field::unreachable;
    auto fidx = [&](vec2 q) { return ((q.y >> 3) * cw + (q.x >> 3)) * 64 + ((q.y & 7) << 3) + (q.x & 7); };
    std::int64_t best_sc = -(static_cast<std::int64_t>(1) << 40);
    vec2 bq = p;
    int bm = -99;
    const int cx0 = std::max(0, (p.x - P_ESC_R) >> 3), cx1 = std::min(cw - 1, (p.x + P_ESC_R) >> 3);
    const int cy0 = std::max(0, (p.y - P_ESC_R) >> 3), cy1 = std::min(static_cast<int>(L.chunked_height) - 1, (p.y + P_ESC_R) >> 3);
    for (int cy = cy0; cy <= cy1; ++cy)
        for (int cx = cx0; cx <= cx1; ++cx) {
            std::uint64_t wv = RB[cy * cs + cx];
            const int base = (cy * cw + cx) * 64;
            while (wv) {
                const int bit = __builtin_ctzll(wv);
                wv &= wv - 1;
                const int dm = FM[base + bit];
                if (dm == kUn) continue;
                const int dt = FT[base + bit] == kUn ? kFar : FT[base + bit];
                const int m = dt - dm;
                const std::int64_t prim = !hurt_flee ? 10000L * std::min(m, P_ESC_CAP) : m >= need ? 10000000L - 10000L * dm : 10000L * m;
                if (prim + 10000 <= best_sc) continue;  // cannot win even with the best tie-break
                const int h = FS[base + bit] == kUn ? 400 : FS[base + bit];
                const std::int64_t sc = prim - std::min(h, 9999);
                if (sc > best_sc) { best_sc = sc; bq = { cx * 8 + (bit & 7), cy * 8 + (bit >> 3) }; bm = m; }
            }
        }
    if (bm <= 0) return -1;
    if (bq == p) {
        safe_here = bm >= need;
        return 0;
    }
    // Walk back from the target along my distances, keeping the widest margin.
    vec2 cur = bq;
    int dcur = FM[fidx(cur)];
    while (dcur > 1) {
        vec2 nxt = cur;
        int nm = -1000;
        for (auto d : kDirs) {
            const vec2 q = cur + d;
            if (q.x < 0 || q.y < 0 || q.x >= L.width || q.y >= L.height) continue;
            const int i = fidx(q);
            if (FM[i] != dcur - 1) continue;
            const int m = (FT[i] == kUn ? kFar : FT[i]) - (dcur - 1);
            if (m > nm) { nm = m; nxt = q; }
        }
        if (nxt == cur) return 0;
        cur = nxt;
        --dcur;
    }
    if (dcur != 1) return 0;
    try {
        if (me.move_absolute(cur)) return 1;
    } catch (...) {
        nav.note_refused(cur);
    }
    return 0;
}

namespace {
struct SimUnit {
    float hp, dps;
    float burst = 0;  // damage on its first active round (abilities ready)
    int delay = 0;    // rounds before it can hit (closing the distance)
    int bdelay = -1;  // rounds before its ability burst can land (-1: with the first attack)
};

// Damage per round against champions: basic attacks plus focus abilities and attack resets, amortised.
float champ_dps(champion_type t, float str, float foc) {
    switch (t) {
    case champion_type::ryth: return str * 1.125f + foc / 8.f;
    case champion_type::vesper_vale:
    case champion_type::vendetta:
    case champion_type::issac:
    case champion_type::varg:
    case champion_type::willow: return str * 1.125f;
    case champion_type::marcella: return str * 1.125f + 2.f * foc / 8.f;
    case champion_type::cassi:
    case champion_type::stellar: return str + 2.f * foc / 8.f;
    case champion_type::prism: return str + 1.5f * foc / 8.f;
    case champion_type::tavi: return str + 1.6f * foc / 8.f;
    case champion_type::heart_of_ruin: return str + 1.5f * foc / 8.f;
    case champion_type::ren: return str;
    }
    return str;
}
// Damage dealt at once when its abilities are ready: nukes and attack resets on top of one attack.
float champ_burst(champion_type t, float str, float foc) {
    switch (t) {
    case champion_type::marcella: return 2.f * foc + 2.f * str;
    case champion_type::cassi:
    case champion_type::stellar: return 2.f * foc + str;
    case champion_type::heart_of_ruin: return 1.5f * foc + str;
    case champion_type::tavi: return 1.6f * foc + str;
    case champion_type::prism: return 1.5f * foc + str;
    case champion_type::ryth: return foc + 2.f * str;
    case champion_type::vesper_vale:
    case champion_type::vendetta:
    case champion_type::issac:
    case champion_type::varg:
    case champion_type::willow: return 2.f * str;
    case champion_type::ren: return str;
    }
    return str;
}
// Shields add effective health over a short fight.
float champ_ehp(champion_type t, float hp, float foc) {
    if (t == champion_type::heart_of_ruin) return hp + 1.5f * foc;
    if (t == champion_type::varg) return hp + 2.5f * foc;
    return hp;
}

void apply_damage(std::vector<SimUnit>& v, float dmg) {
    // Focus fire: the weakest unit first, overflow to the next.
    std::size_t i = 0;
    while (dmg > 0 && i < v.size()) {
        if (v[i].hp <= 0) { ++i; continue; }
        const float d = std::min(dmg, v[i].hp);
        v[i].hp -= d;
        dmg -= d;
        if (v[i].hp <= 0) ++i;
    }
}

// Focus-fire attrition fight; returns our surviving health fraction minus theirs, in [-1, 1].
// Units join after their approach delay and open with their burst.
float simulate(std::vector<SimUnit> a, std::vector<SimUnit> b, float extra_b_dps = 0.f, float extra_a_dps = 0.f) {
    auto by_hp = [](const SimUnit& x, const SimUnit& y) { return x.hp < y.hp; };
    std::sort(a.begin(), a.end(), by_hp);
    std::sort(b.begin(), b.end(), by_hp);
    float a0 = 0, b0 = 0;
    int last = 0;
    for (const auto& u : a) { a0 += u.hp; last = std::max(last, u.delay); }
    for (const auto& u : b) { b0 += u.hp; last = std::max(last, u.delay); }
    if (a0 <= 0) return -1.f;
    if (b0 <= 0) return 1.f;
    for (const auto& u : a) last = std::max(last, u.bdelay);
    for (const auto& u : b) last = std::max(last, u.bdelay);
    auto dealt = [](const std::vector<SimUnit>& v, int t) {
        float d = 0;
        for (const auto& u : v) {
            if (u.hp <= 0) continue;
            if (u.bdelay < 0) {
                if (u.delay > t) continue;
                d += (t == u.delay && u.burst > u.dps) ? u.burst : u.dps;
            } else {
                if (t >= u.delay) d += u.dps;
                if (t == u.bdelay) d += std::max(0.f, u.burst - (t >= u.delay ? u.dps : 0.f));
            }
        }
        return d;
    };
    auto alive = [](const std::vector<SimUnit>& v) {
        for (const auto& u : v) if (u.hp > 0) return true;
        return false;
    };
    for (int t = 0; t < 60; ++t) {
        float da = dealt(a, t), db = dealt(b, t);
        if (t > last && (da <= 0 || db <= 0)) break;
        if (da > 0 || db > 0) {
            db += extra_b_dps;  // awake camps keep hitting whichever side stands nearest to them
            da += extra_a_dps;
        }
        apply_damage(b, da);
        apply_damage(a, db);
        if (!alive(a) || !alive(b)) break;
    }
    float a1 = 0, b1 = 0;
    for (const auto& u : a) a1 += std::max(0.f, u.hp);
    for (const auto& u : b) b1 += std::max(0.f, u.hp);
    return a1 / a0 - b1 / b0;
}
// Rounds before a unit at distance d with attack range r can hit (melee move and attack in one turn).
int approach_delay(int d, int r) {
    const int gap = d - r;
    if (gap <= 0) return 0;
    return r <= 1 ? gap - 1 : gap;
}
}  // namespace

float champ_dps_est(champion_type t, float str, float foc) { return champ_dps(t, str, foc); }
float champ_burst_est(champion_type t, float str, float foc) { return champ_burst(t, str, foc); }

bool Bot::combat() {
    auto& me = self();
    const vec2 p = me.position();
    // Enemies that matter: visible within 8, plus ones seen in the last few rounds (bushes, edge of vision).
    std::vector<const Seen*> near;
    for (const auto& e : enemies)
        if (cheb(e.pos, p) <= 8) near.push_back(&e);
    for (const auto& m : emem) {
        if (!m.s || round - m.seen_round > 3 || round == m.seen_round || cheb(m.s->pos, p) > 8) continue;
        near.push_back(&*m.s);
    }
    if (near.empty()) return false;
    int closest = 99;
    for (const auto* e : near) closest = std::min(closest, cheb(e->pos, p));
    for (const auto* e : near) sightings.push_back({ e->pos, round, e->hp });

    // Both sides of the local fight.
    std::vector<SimUnit> ours, theirs;
    auto nearest_enemy = [&](vec2 q) {
        int d = 99;
        for (const auto* e : near) d = std::min(d, cheb(e->pos, q));
        return d;
    };
    {
        // My cooldowns are known: burst only with a ready ability.
        bool ready = false;
        try {
            auto abs = me.abilities();
            for (int s = 0; s < 2; ++s) if (ahas[s] && abs[s].cooldown() == 0) ready = true;
        } catch (...) {}
        SimUnit u{ champ_ehp(ctype, me.health(), me.focus()), champ_dps(ctype, me.strength(), me.focus()) };
        u.burst = ready ? champ_burst(ctype, me.strength(), me.focus()) : 0.f;
        u.delay = approach_delay(closest, me.attack_range());
        if (P_BURST_REACH) u.bdelay = std::max(0, closest - burst_reach(ctype, me.attack_range()));
        ours.push_back(u);
    }
    float our_dps = ours.back().dps;
    std::vector<vec2> fighters{ p };  // where the champions counted on our side stand
    for (const auto& a : allies) {
        if (cheb(a.pos, p) > 7) continue;
        const int c = comms.code_of(a.index);
        if (c == slot::kHome || c == slot::kTribute || c == slot::kDead) continue;  // leaving or channelling
        // Running away itself: no help, unless healthy and right here (champions retreating side by side all
        // excluded each other and the whole team ran from fights it would win).
        if (P_RETREAT_CODE && c == slot::kRetreat &&
            !(P_RETREAT_COUNT_R > 0 && cheb(a.pos, p) <= P_RETREAT_COUNT_R && a.hp >= P_RETREAT_COUNT_HP * a.max_hp)) continue;
        const int de = nearest_enemy(a.pos);
        if (de > 8 && !(P_SIM_JOIN_R > 0 && cheb(a.pos, p) <= P_SIM_JOIN_R)) continue;  // cannot see the fight: will not join it (unless right next to me)
        if (a.hp < 0.2f * a.max_hp) continue;  // about to run home
        const auto t = ainfo[static_cast<std::size_t>(a.index)].type;
        SimUnit u{ champ_ehp(t, a.hp, a.foc), champ_dps(t, a.str, a.foc) };
        u.burst = champ_burst(t, a.str, a.foc);
        u.delay = approach_delay(de, a.range) + P_SIM_REACT;  // reacts a turn later
        if (P_BURST_REACH) u.bdelay = std::max(0, de - burst_reach(t, a.range)) + P_SIM_REACT;
        if (P_ALLY_CD && a.cd_known) u.burst = a.burst_at(round, std::max(0, P_BURST_REACH ? u.bdelay : u.delay));
        ours.push_back(u);
        fighters.push_back(a.pos);
        our_dps += u.dps;
    }
    for (const auto* e : near) {
        SimUnit u{ champ_ehp(e->type, e->hp, e->foc), champ_dps(e->type, e->str, e->foc) };
        u.burst = champ_burst(e->type, e->str, e->foc);
        int d = cheb(e->pos, p);
        if (P_SIM_SYM) {
            for (vec2 q : fighters) d = std::min(d, cheb(e->pos, q));  // they reach the fight where our fighters stand
        } else {
            for (const auto& a : allies) d = std::min(d, cheb(e->pos, a.pos));
        }
        u.delay = approach_delay(d, e->range);
        if (P_BURST_REACH) u.bdelay = std::max(0, d - burst_reach(e->type, e->range));
        if (P_ENEMY_CD && e->cd_known) u.burst = e->burst_at(round, std::max(0, P_BURST_REACH ? u.bdelay : u.delay));  // abilities on cooldown do not burst
        theirs.push_back(u);
    }
    // Awake camps around the fight hit the nearest champion of either side (third-party fights at camps).
    float camp_on_us = 0, camp_on_them = 0;
    for (const auto& g : world().groups) {
        if (g.state != GState::Alive || g.dps <= 0 || cheb(g.center, p) > g.radius + 8) continue;
        for (const auto& c : g.camps) {
            if (c.hp <= 0 || camp_str(c.type) <= 0 || round - c.awake_round > 1) continue;
            int du = cheb(c.pos, p);
            for (const auto& a : allies) du = std::min(du, cheb(c.pos, a.pos));
            int de = 99;
            for (const auto* e : near) de = std::min(de, cheb(c.pos, e->pos));
            const int rr = camp_range(c.type);
            if (du <= de && du <= rr + 1) camp_on_us += camp_str(c.type);
            else if (de < du && de <= rr + 1) camp_on_them += camp_str(c.type);
        }
    }
    const float outcome = simulate(ours, theirs, camp_on_us, camp_on_them);
    // Before walking into a fight: enemies seen around here lately and out of sight now probably join it.
    float outcome_e = outcome;
    if (P_REINF_ENGAGE > 0) {
        std::vector<SimUnit> more = theirs;
        for (const auto& m : emem) {
            if (!m.s || round - m.seen_round > P_REINF_ENGAGE || round - m.seen_round <= 3) continue;
            bool listed = false;
            for (const auto* e : near) if (e->index == m.s->index) listed = true;
            if (listed) continue;
            const int d = cheb(m.s->pos, p);
            if (d > 10) continue;
            SimUnit u{ champ_ehp(m.s->type, m.s->hp, m.s->foc), champ_dps(m.s->type, m.s->str, m.s->foc) };
            u.burst = champ_burst(m.s->type, m.s->str, m.s->foc);
            u.delay = approach_delay(d, m.s->range) + 1;
            if (P_BURST_REACH) u.bdelay = std::max(0, d - burst_reach(m.s->type, m.s->range)) + 1;
            more.push_back(u);
        }
        if (more.size() > theirs.size()) outcome_e = simulate(ours, more, camp_on_us, camp_on_them);
    }

    const bool low = me.health() < me.max_health() * 0.35f;
    const bool loaded = me.gem_count() >= 30;
    const int range = me.attack_range();
    const int reach = ranged ? range : range + 1;

    // Focus target (same rule for every ally): least health to chew through, then distance.
    const Seen* tgt = nullptr;
    float bscore = 1e9f;
    for (const auto* e : near) {
        if (round - e->seen_round > 0) continue;  // remembered, not visible: cannot attack
        const int d = cheb(e->pos, p);
        float sc = std::floor(e->hp / 100.f) * 100.f + 40.f * static_cast<float>(d);
        if (e->channeling) sc -= 300.f;
        sc -= static_cast<float>(e->gems) * 4.f;
        if (d <= range) sc -= 150.f;
        if (sc < bscore) { bscore = sc; tgt = e; }
    }
    // Kill shots: an enemy I can finish this turn within my strike reach is worth going for.
    const Seen* fin = nullptr;
    if (P_KILLSHOT && !low) {
        float burst = me.strength();
        int strike = reach;
        try {
            auto abs = me.abilities();
            for (int s = 0; s < 2; ++s) {
                if (!ahas[s] || abs[s].cooldown() > 0) continue;
                if (akind[s] == ability_kind::attack_reset) burst += me.strength();
                else if ((akind[s] == ability_kind::damage || akind[s] == ability_kind::aoe_damage) && amod[s] > 0) {
                    burst += amod[s] * me.focus();
                    strike = std::max(strike, static_cast<int>(arange[s]));
                } else if (akind[s] == ability_kind::dash && !cast_this_turn) {
                    if (amod[s] > 0) burst += amod[s] * me.focus();
                    strike = std::max(strike, ranged ? range + 2 : 4);
                }
            }
        } catch (...) {}
        for (const auto* e : near) {
            if (round != e->seen_round) continue;
            if (cheb(e->pos, p) > strike || e->hp > burst) continue;
            if (!fin || e->hp < fin->hp) fin = e;
        }
        if (fin) tgt = fin;
    }
    const int td = tgt ? cheb(tgt->pos, p) : 99;
    const bool killable = tgt && ((td <= reach && tgt->hp <= me.strength() * 1.2f) || (fin && tgt == fin));
    // Ranged damage abilities (Marcella's 2x-focus nuke, Ryth's stunning area blast) go off whenever an enemy is
    // in their range, whatever else this turn does (they were cast only next to the target, rarely at all).
    if (P_FREE_CAST && !cast_this_turn) free_cast(near, !low && !loaded && outcome > P_FREE_EXCL_MIN);
    const float need = loaded ? 0.45f : P_ENGAGE;
    LOGC("%d %d C o=%.2f u%zu t%zu cl%d td%d lo%d", round, idx, outcome, ours.size(), theirs.size(), closest, td, (int)low);
#if BOT_LOGC
    for (const auto* e : near) LOGC(" %c%d,%d:%.0f", "rsvcitpmwngah"[std::min(12, static_cast<int>(e->type))], e->pos.x, e->pos.y, e->hp);
    LOGC("\n");
#endif
    LOG("  combat r%d: ours=%zu theirs=%zu outcome=%.2f closest=%d td=%d low=%d loaded=%d\n", round, ours.size(), theirs.size(), outcome, closest, td, (int)low, (int)loaded);

    auto hit = [&]() {
        if (!tgt || cheb(me.position(), tgt->pos) > range || !me.can_attack()) return false;
        try_cast_on_enemy(*tgt);
        try { me.attack(tgt->c); } catch (...) { return false; }
        bool dead = false;
        try { dead = !tgt->c.is_visible() || tgt->c.health() <= 0; } catch (...) { dead = true; }
        if (!dead) {
            try_attack_reset_followup(tgt->c);
        } else {
            // Killed: the reset goes to the next enemy in reach.
            const Seen* nxt = nullptr;
            for (const auto* e : near)
                if (e != tgt && round == e->seen_round && cheb(me.position(), e->pos) <= range && (!nxt || e->hp < nxt->hp)) nxt = e;
            if (nxt) try_attack_reset_followup(nxt->c);
        }
        return true;
    };
    // Whoever is in reach (weakest first): when the focus target cannot be hit this turn.
    auto hit_any = [&]() {
        if (!P_HITFIX || !me.can_attack()) return false;
        const vec2 q = me.position();
        const Seen* best = nullptr;
        for (const auto* e : near) {
            if (round != e->seen_round || cheb(e->pos, q) > range || false) continue;
            if (!best || e->hp < best->hp) best = e;
        }
        if (!best) return false;
        const Seen* keep = tgt;
        tgt = best;
        const bool ok = hit();
        tgt = keep;
        return ok;
    };

    // Capturing a valuable group: hold the tile (damage does not stop a capture, leaving does).
    if (P_CAP_STAY && !low && task >= 0 && task < static_cast<int>(world().groups.size())) {
        const Group& cg = world().groups[static_cast<std::size_t>(task)];
        if (cg.state == GState::Reward && cg.tiles && bb_test(*cg.tiles, p) && (cg.gems >= P_CAP_STAY_GEMS || cg.gold >= P_CAP_STAY_GOLD)) {
            float bur = 0;
            for (const auto* e : near) {
                if (round - e->seen_round > 1) continue;
                const int d = cheb(e->pos, p);
                if (d <= burst_reach(e->type, e->range) + 1) bur += (P_ENEMY_CD && e->cd_known ? e->burst_at(round, 1) : champ_burst(e->type, e->str, e->foc)) + champ_dps(e->type, e->str, e->foc);
            }
            if (me.health() > 1.5f * bur) {
                act = "cap_hold";
                hit_any();
                return true;
            }
        }
    }
    // Chase discipline: an enemy that is not fighting anyone (kiting bait) is not worth leaving awake camps
    // or running after at equal speed; respond only when it comes into reach.
    bool no_chase = false;
    int dash_reach = reach;
    if (P_DASH_ENGAGE && !cast_this_turn) {
        const int ds = ability_slot(ability_kind::dash);
        if (ds >= 0 && amod[static_cast<std::size_t>(ds)] <= 0) {
            try { if (me.abilities()[static_cast<std::size_t>(ds)].cooldown() == 0) dash_reach = ranged ? range + 2 : 4; } catch (...) {}
        }
    }
    if (P_CHASE_DISCIPLINE && tgt && !killable && td > dash_reach) {
        bool busy_camps = false;
        if (task >= 0 && task < static_cast<int>(world().groups.size())) {
            const Group& g = world().groups[static_cast<std::size_t>(task)];
            if (g.state == GState::Alive)
                for (const auto& c : g.camps)
                    if (c.hp > 0 && camp_str(c.type) > 0 && round - c.awake_round <= 1 && cheb(c.pos, p) <= camp_range(c.type) + 2) busy_camps = true;
        }
        bool tgt_threat = cheb(tgt->pos, p) <= tgt->range + 1;
        for (const auto& a : allies)
            if (cheb(a.pos, p) <= 6 && cheb(tgt->pos, a.pos) <= tgt->range + 1) tgt_threat = true;
        // A target busy with camps (tanking them) or a capture or a channel cannot kite: worth closing in on.
        bool tgt_busy = P_ENGAGE_BUSY && tgt->channeling;
        if (P_ENGAGE_BUSY && !tgt_busy)
            for (const auto& g : world().groups) {
                if (cheb(g.center, tgt->pos) > g.radius + 5) continue;
                if (g.state == GState::Reward && g.tiles && bb_test(*g.tiles, tgt->pos)) { tgt_busy = true; break; }
                if (g.state != GState::Alive) continue;
                for (const auto& c : g.camps)
                    if (c.hp > 0 && camp_str(c.type) > 0 && round - c.awake_round <= 1 && cheb(c.pos, tgt->pos) <= camp_range(c.type)) { tgt_busy = true; break; }
                if (tgt_busy) break;
            }
        if (!tgt_threat && (busy_camps || (td > dash_reach + 1 && !tgt_busy))) no_chase = true;
    }
    if (tgt && !no_chase && (killable || (!low && outcome_e > need))) {
        // Engage: abilities, then attack; close in when out of range.
        act = "engage";
        if (td <= range) {
            hit();
            return true;
        }
        if (dash_strike(*tgt)) { act = "dash_strike"; return true; }
        if (ranged && !(fin && tgt == fin) && hit_any()) { act = "engage_near"; return true; }
        try_cast_on_enemy(*tgt);
        bitboard goals;
        goals.clear();
        goals.draw_chebyshev(tgt->pos, static_cast<float>(range));
        goals &= ~*world().blocked;
        spread_goals(goals, near);
        if (!ranged || td > range) move_to(goals, nullptr, false);
        if (!ranged && !hit()) hit_any();
        return true;
    }
    // Someone can hit me now or after one step: walking on (or away) just gives them free hits.
    bool threatened = closest <= 2;
    const Seen* shooter = nullptr;
    for (const auto* e : near) {
        if (round - e->seen_round > 0) continue;
        if (cheb(e->pos, p) <= e->range + 1) {
            threatened = true;
            if (!shooter || e->hp < shooter->hp) shooter = e;
        }
    }
    if (tgt && !low && outcome > (P_CONTACT ? P_HOLD_C : -0.15f) && threatened) {
        // Even fight on top of us: hit back (running hands out free hits); a melee champion shot at from range closes in on the shooter.
        act = "holdfight";
        if (P_HOLD_NUKE && P_FREE_CAST && !cast_this_turn && !moved_this_turn) free_cast(near, true);
        if (!hit()) {
            const Seen* t2 = (td <= reach || !shooter) ? tgt : shooter;
            const int d2 = cheb(t2->pos, p);
            if (d2 > range + 1 && dash_strike(*t2)) { act = "dash_strike"; return true; }
            if (!ranged && d2 <= range + 2) {
                tgt = t2;
                bitboard goals;
                goals.clear();
                goals.draw_chebyshev(tgt->pos, static_cast<float>(range));
                goals &= ~*world().blocked;
                spread_goals(goals, near);
                move_to(goals, nullptr, false);
                hit();
            }
        }
        if (me.can_attack() && !hit_any() && P_HITFIX >= 2 && !moved_this_turn && me.can_move()) {
            // Nobody in reach (the focus target stands just out of it): close in instead of standing idle.
            const Seen* t3 = nullptr;
            int d3 = 99;
            for (const auto* e : near) {
                if (round != e->seen_round || false) continue;
                const int de = cheb(e->pos, p);
                if (de < d3 || (de == d3 && t3 && e->hp < t3->hp)) { d3 = de; t3 = e; }
            }
            if (t3 && d3 <= 4) {
                tgt = t3;
                bitboard goals;
                goals.clear();
                goals.draw_chebyshev(tgt->pos, static_cast<float>(range));
                goals &= ~*world().blocked;
                spread_goals(goals, near);
                move_to(goals, nullptr, false);
                if (!ranged && !hit()) hit_any();
                act = "hold_close";
            }
        }
        return true;
    }
    // An ally near me is being hit: join that fight unless it is clearly lost (fight together, not one by one).
    if (P_ASSIST && !low && outcome > P_ASSIST_MIN) {
        const Seen* att = nullptr;
        for (const auto& a : allies) {
            if (cheb(a.pos, p) > P_ASSIST_R) continue;
            const int c = comms.code_of(a.index);
            if (c == slot::kHome || c == slot::kDead || c == slot::kRetreat) continue;
            for (const auto* e : near) {
                if (round != e->seen_round || cheb(e->pos, a.pos) > e->range + 1) continue;
                if (!att || e->hp < att->hp) att = e;
            }
        }
        if (att) {
            act = "assist";
            tgt = att;
            const int ta = cheb(tgt->pos, p);
            if (ta <= range) {
                hit();
                return true;
            }
            if (dash_strike(*tgt)) { act = "dash_strike"; return true; }
            if (ranged && hit_any()) { act = "assist_near"; return true; }
            try_cast_on_enemy(*tgt);
            bitboard goals;
            goals.clear();
            goals.draw_chebyshev(tgt->pos, static_cast<float>(range));
            goals &= ~*world().blocked;
            spread_goals(goals, near);
            move_to(goals, nullptr, false);
            if (!ranged && !hit()) hit_any();
            return true;
        }
    }
    // An enemy in my reach and the fight not lost: hit it rather than keep working on camps beside it
    // (farming next to enemies handed them free hits while we kept attacking camps).
    // A teammate is being hit next to me: fight with it or get out, never keep farming beside it.
    bool nd_leave = false;
    if (P_NODEAD && !low) {
        const Seen* att = nullptr;
        for (const auto& a : allies) {
            if (cheb(a.pos, p) > P_ND_R) continue;
            const int c = comms.code_of(a.index);
            if (c == slot::kHome || c == slot::kDead) continue;
            for (const auto* e : near) {
                if (round != e->seen_round) continue;
                if (cheb(e->pos, a.pos) > std::max(1, e->range) + 1) continue;
                if (!att || e->hp < att->hp) att = e;
            }
        }
        if (att && outcome > P_ND_JOIN) {
            act = "nd_join";
            tgt = att;
            const int ta = cheb(tgt->pos, p);
            if (ta <= range) { hit(); return true; }
            if (dash_strike(*tgt)) { act = "dash_strike"; return true; }
            if (ranged && hit_any()) return true;
            try_cast_on_enemy(*tgt);
            bitboard goals;
            goals.clear();
            goals.draw_chebyshev(tgt->pos, static_cast<float>(range));
            goals &= ~*world().blocked;
            spread_goals(goals, near);
            move_to(goals, nullptr, false);
            if (!ranged && !hit()) hit_any();
            return true;
        }
        if (att) nd_leave = true;
    }
    if (P_SKIRMISH && tgt && td <= range && !low && outcome > P_SKIRMISH_MIN && me.can_attack()) {
        act = "skirmish";
        hit();
        return true;
    }
    // Not clearly losing: keep working, but avoid stepping into their reach.
    bool losing = outcome < P_FLEE || low || (loaded && outcome < 0.2f) || nd_leave;
    // Out of contact, stepping away is cheap: avoid fights that are not clearly ours. In contact, only a
    // clearly lost fight is worth running from (handled above: holding otherwise).
    if (P_CONTACT) losing = (threatened ? outcome <= P_HOLD_C : outcome < P_AVOID) || low || (loaded && outcome < 0.2f) || nd_leave;
    // Outnumbered and not clearly ahead: leave before contact (top teams pick off champions caught alone).
    if (P_OUTNUM && theirs.size() > ours.size() && outcome < P_ENGAGE) losing = true;
    // Burst they can land on me next round (dashes add two tiles of reach): leave before it lands.
    if (P_BURST_GUARD > 0.f) {
        float bur = 0;
        for (const auto* e : near) {
            const int d = cheb(e->pos, p);
            const int reach_e = P_BURST_REACH ? burst_reach(e->type, e->range) + 1 :
                                e->range + 1 + (e->type == champion_type::vendetta || e->type == champion_type::vesper_vale ||
                                                 e->type == champion_type::issac || e->type == champion_type::heart_of_ruin ? 2 : 0);
            if (d <= reach_e) bur += (P_ENEMY_CD && e->cd_known ? e->burst_at(round, 1) : champ_burst(e->type, e->str, e->foc)) + champ_dps(e->type, e->str, e->foc);
        }
        if (bur > 0 && me.health() < P_BURST_GUARD * bur && outcome < P_ENGAGE) losing = true;
    }
    // Hysteresis: an enemy flickering in and out of sight made champions alternate retreat and work (stepping
    // back and forth in place). Having just retreated, keep away unless the fight now looks clearly better.
    // Enemies keeping their distance (farming beside us, not chasing): no reason to leave the work.
    bool calm = false;
    if (P_CALM_AVOID && !threatened && !low && !loaded && closest >= P_CALM_D && me.health() >= P_CALM_HP * me.max_health()) {
        calm = true;
        for (const auto* e : near) {
            if (e->index < 0 || static_cast<std::size_t>(e->index) >= emem.size()) { calm = false; break; }
            const auto& m = emem[static_cast<std::size_t>(e->index)];
            if (m.prev_round >= round - 2 && cheb(e->pos, p) < cheb(m.prev_pos, p)) { calm = false; break; }
        }
        if (calm && outcome > P_HOLD_C - 0.3f) losing = false;
    }
    if (P_RETREAT_HYST > 0.f && !losing && !calm && round - last_retreat_round <= P_RETREAT_HYST_R && outcome < P_AVOID + P_RETREAT_HYST) losing = true;
    if (!losing || (closest > 6 && !hurt)) {
        if (threat) for (const auto* e : near) threat->draw_chebyshev(e->pos, static_cast<float>(std::max(e->range + 3, P_BURST_REACH ? burst_reach(e->type, e->range) + 2 : 0)));
        return false;
    }
    // Running from a melee champion already next to me only gives it free hits (it moves and attacks in
    // the same turn): trade blows instead, unless a dash breaks contact.
    if (P_NO_FUTILE_FLEE) {
        bool melee_on_me = false;
        for (const auto* e : near)
            if (round == e->seen_round && e->range <= 1 && cheb(e->pos, p) <= 1) melee_on_me = true;
        bool dash_ready = false;
        const int ds0 = ability_slot(ability_kind::dash);
        if (ds0 >= 0 && !cast_this_turn) {
            try { dash_ready = me.abilities()[static_cast<std::size_t>(ds0)].cooldown() == 0; } catch (...) {}
        }
        if (melee_on_me && !dash_ready) {
            const Seen* weakest = nullptr;
            for (const auto* e : near)
                if (round == e->seen_round && cheb(e->pos, p) <= range && (!weakest || e->hp < weakest->hp)) weakest = e;
            if (weakest) {
                act = "trade";
                tgt = weakest;
                hit();
                return true;
            }
        }
    }
    act = "retreat";
    last_retreat_round = round;
    // Hit and run: a melee champion moves and attacks in the same turn, so leaving does not stop me from
    // hitting whoever is next to me first (retreats used to hand out free hits and deal none).
    if (P_HIT_RUN && !ranged && me.can_attack()) {
        const Seen* adj = nullptr;
        for (const auto* e : near)
            if (round == e->seen_round && cheb(e->pos, p) <= range && (!adj || e->hp < adj->hp)) adj = e;
        if (adj) {
            try {
                me.attack(adj->c);
                attacked_this_turn = true;
                act = "retreat_hit";
            } catch (...) {}
        }
    }
    std::vector<vec2> dangers;
    std::vector<int> ranges;
    for (const auto* e : near) { dangers.push_back(e->pos); ranges.push_back(e->range); }
    int esc = 0;
    bool safe_here = false;
    if (P_ESCAPE && fuel() > P_ESC_MIN_FUEL) {  // low on fuel: the cheap retreat below (an exhausted turn loses its move)
        esc = escape(near, safe_here);
        LOGC("%d %d E%d%s\n", round, idx, esc, safe_here ? " safe" : "");
        if (esc == 1) {
            moved_this_turn = true;
            nav.begin_turn();
        } else if (esc == 0 && safe_here) {
            // Out of their reach for a whole recall: heal now if worth it, else carry on with the work.
            if (me.health() < P_ESC_RECALL_HP * me.max_health() && !me.is_recalling()) {
                try { me.recall(); act = "esc_recall"; return true; } catch (...) {}
            }
            if (threat) for (const auto* e : near) threat->draw_chebyshev(e->pos, static_cast<float>(std::max(e->range + 3, P_BURST_REACH ? burst_reach(e->type, e->range) + 2 : 0)));
            return false;
        } else if (esc == -1 && P_CAUGHT_FIGHT && tgt && td <= range) {
            act = "caught";  // they reach every tile before me: hit back rather than give free hits
            hit();
        }
    }
    if (P_ESCAPE && (esc == 1 || act == std::string_view("caught"))) {
        // done moving
    } else if (retreat(dangers, ranges)) {
        moved_this_turn = true;
        nav.begin_turn();
    } else if (tgt && td <= range) {
        hit();  // cornered
    } else if (!world().on_main(me.position()) && has_crystal() && !me.is_teleporting()) {
        // Stranded on an island under fire I cannot answer: jump back to the mainland, away from them.
        World& W = world();
        const vec2 q0 = me.position();
        vec2 best{ -1, -1 };
        int bs = -100000;
        for (int dx = -3; dx <= 3; ++dx)
            for (int dy = -3; dy <= 3; ++dy) {
                const vec2 q{ q0.x + dx, q0.y + dy };
                if (!in_bounds(q) || !bb_test(*W.mainland, q) || bb_test(*W.blocked, q) || bb_test(*W.camp_tiles, q) || bb_test(nav.occupied(), q)) continue;
                int mind = 99;
                for (auto dp : dangers) mind = std::min(mind, cheb(q, dp));
                const int sc = mind * 100 - df_get(*W.f_spawn, q);
                if (sc > bs) { bs = sc; best = q; }
            }
        if (best.x >= 0) {
            try {
                if (me.consumables()[consumable_type::tp_crystal].use(best)) { crystal_cache = -1; act = "island_escape"; }
            } catch (...) {}
        }
    }
    // Escape dash.
    const int ds = ability_slot(ability_kind::dash);
    if (ds >= 0 && !cast_this_turn && (hurt || closest <= 3)) {
        try {
            auto abs = me.abilities();
            if (abs[static_cast<std::size_t>(ds)].cooldown() == 0) {
                const vec2 q0 = me.position();
                vec2 best = q0;
                int bs = -1000;
                for (int dx = -2; dx <= 2; ++dx)
                    for (int dy = -2; dy <= 2; ++dy) {
                        const vec2 q{ q0.x + dx, q0.y + dy };
                        if (q == q0 || !nav.passable(q)) continue;
                        int mind = 99;
                        for (auto dp : dangers) mind = std::min(mind, cheb(q, dp));
                        const int sc = mind * 10 - df_get(*world().f_spawn, q) / 4;
                        if (sc > bs) { bs = sc; best = q; }
                    }
                if (best != q0 && abs[static_cast<std::size_t>(ds)].use(best)) cast_this_turn = true;
            }
        } catch (...) {}
    }
    // Shield while being chased.
    if (!cast_this_turn && hurt) {
        const int sh = ability_slot(ability_kind::shield);
        if (sh >= 0) {
            try {
                auto abs = me.abilities();
                if (abs[static_cast<std::size_t>(sh)].cooldown() == 0 && abs[static_cast<std::size_t>(sh)].use(me)) cast_this_turn = true;
            } catch (...) {}
        }
    }
    return true;
}

void Bot::free_cast(const std::vector<const Seen*>& near, bool may_stand) {
    auto& me = self();
    const vec2 p = me.position();
    auto abs = me.abilities();
    for (int s = 0; s < 2 && !cast_this_turn; ++s) {
        if (!ahas[s]) continue;
        const auto k = akind[s];
        if (k != ability_kind::damage && k != ability_kind::aoe_damage && k != ability_kind::cc) continue;
        if (aexcl[s] && moved_this_turn) continue;
        bool kill_only = false;
        if (aexcl[s] && !may_stand) {  // casting it pins me for the turn: not when I may have to run, unless it kills
            if (!P_KILLSHOT || k != ability_kind::damage) continue;
            kill_only = true;
        }
        try {
            if (abs[s].cooldown() > 0) continue;
        } catch (...) { continue; }
        const int r = static_cast<int>(arange[s]);
        const Seen* best = nullptr;
        float bs = -1e9f;
        for (const auto* e : near) {
            if (round != e->seen_round || cheb(e->pos, p) > r) continue;
            float sc;
            if (k == ability_kind::aoe_damage) {
                // most enemies within one tile of the blast centre, then the weakest
                int cnt = 0;
                for (const auto* f : near)
                    if (round == f->seen_round && cheb(f->pos, e->pos) <= 1) ++cnt;
                sc = 1000.f * static_cast<float>(cnt) - e->hp;
            } else if (k == ability_kind::cc) {
                sc = champ_dps(e->type, e->str, e->foc);  // stop their biggest hitter
            } else {
                sc = -e->hp;  // finish the weakest
                if (e->hp <= amod[s] * me.focus()) sc += 5000.f;  // a kill
                else if (kill_only) continue;
            }
            if (sc > bs) { bs = sc; best = e; }
        }
        if (!best) continue;
        try {
            bool ok = false;
            if (k == ability_kind::aoe_damage) ok = abs[s].use(best->pos);
            else ok = abs[s].use(best->c);
            if (ok) cast_this_turn = true;
        } catch (...) {}
    }
}
}  // namespace cjb
