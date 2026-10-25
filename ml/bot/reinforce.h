// Part of bot.cpp: learned reinforcement prediction (ml/reinforce_*.py). Expected number of enemies that are not
// visible now but come within 6 tiles in the next 7 rounds, from what this champion sees and remembers.
// Features must match ml/reinforce_data.py exactly. Unity build: included inside bot.cpp's anonymous namespace.

#include <wasm_simd128.h>
#include "rf_weights.h"

constexpr int RF_MEMORY = 10, RF_MAX_ALLIES = 5, RF_MAX_ENEMIES = 6, RF_MAX_MEM = 6, RF_V = RF_W / 4, RF_HV = RF_H / 4;

struct RfSeen { std::uint32_t id; int round; vec2 pos; float hp_frac, gems; int type; };
std::vector<RfSeen> rf_seen;
float rf_arrivals = 0;

template <class C> std::array<float, 2> rf_cooldowns(const C& c) {
    std::array<float, 2> out{};
    int i = 0;
    for (const auto& ab : c.abilities()) {
        if (i >= 2) break;
        try {
            out[i] = static_cast<float>(ab.cooldown());
        } catch (const cambc::error&) {
        }
        ++i;
    }
    return out;
}

inline void rf_axpy(v128_t* acc, const float* row, float x, int nv) {
    const v128_t s = wasm_f32x4_splat(x);
    for (int v = 0; v < nv; ++v) acc[v] = wasm_f32x4_add(acc[v], wasm_f32x4_mul(wasm_v128_load(row + 4 * v), s));
}

// One unit through phi (Linear + type embedding, ReLU), added into pool.
void rf_phi_add(const float* raw, int n, const float* mean, const float* std_, const float (*wx)[RF_W], const float* b, const float* emb, float* pool) {
    v128_t h[RF_V];
    for (int v = 0; v < RF_V; ++v) h[v] = wasm_f32x4_add(wasm_v128_load(b + 4 * v), wasm_v128_load(emb + 4 * v));
    for (int k = 0; k < n; ++k) rf_axpy(h, wx[k], (raw[k] - mean[k]) / std_[k], RF_V);
    const v128_t z = wasm_f32x4_splat(0.0f);
    for (int v = 0; v < RF_V; ++v) wasm_v128_store(pool + 4 * v, wasm_f32x4_add(wasm_v128_load(pool + 4 * v), wasm_f32x4_pmax(h[v], z)));
}

void rf_unit(vec2 me, vec2 pos, float hp, float max_hp, float gems, float str, float focus, std::array<float, 2> cd, int range, int type, float* pool) {
    const float dx = static_cast<float>(pos.x - me.x), dy = static_cast<float>(pos.y - me.y);
    const float raw[RF_UNIT] = {dx, dy, std::max(std::abs(dx), std::abs(dy)), hp, hp / max_hp, std::log1p(gems), str, focus, cd[0], cd[1],
                                static_cast<float>(range)};
    rf_phi_add(raw, RF_UNIT, RF_UNIT_MEAN, RF_UNIT_STD, RF_UNIT_X, RF_UNIT_B, RF_UNIT_EMB[std::clamp(type, 0, 12)], pool);
}

float rf_nearest(vec2 p, const std::vector<vec2>& pts) {
    int best = 99;
    for (auto q : pts) best = std::min(best, dist(p, q));
    return static_cast<float>(best);
}

// Call once per turn after take_snapshot(): updates the sighting memory and rf_arrivals.
void rf_update() {
    static std::vector<vec2> own_spawn, enemy_spawn;
    if (own_spawn.empty()) {
        for (auto q : W.ally_spawn.positions()) own_spawn.push_back(q);
        for (auto q : W.enemy_spawn.positions()) enemy_spawn.push_back(q);
    }
    auto& me = cambc::self();
    const vec2 p = S.me;
    rf_arrivals = 0;
    std::vector<const RfSeen*> mem;
    for (const auto& s : rf_seen) {
        if (S.round - s.round > RF_MEMORY) continue;
        bool visible = false;
        for (const auto& e : S.enemies) visible |= handle_id(e.ch) == s.id;
        if (!visible) mem.push_back(&s);
    }
    if (!S.enemies.empty() || !mem.empty()) {
        std::sort(mem.begin(), mem.end(), [](const RfSeen* a, const RfSeen* b) { return a->round > b->round; });
        alignas(16) float x[4 * RF_W + RF_GAME] = {};
        rf_unit(p, p, S.hp, S.max_hp, static_cast<float>(me.gem_count()), S.str, S.focus, rf_cooldowns(me), S.range,
                static_cast<int>(me.champion_name()), x);
        float ally_gems = 0, enemy_gems = 0;
        int n = 0;
        for (const auto& a : S.allies) {
            if (n++ >= RF_MAX_ALLIES) break;
            rf_unit(p, a.pos, a.hp, a.max_hp, static_cast<float>(a.gems), a.str, a.focus, rf_cooldowns(a.ch), a.range, static_cast<int>(a.type), x + RF_W);
            ally_gems += static_cast<float>(a.gems);
        }
        n = 0;
        for (const auto& e : S.enemies) {
            if (n++ >= RF_MAX_ENEMIES) break;
            rf_unit(p, e.pos, e.hp, e.max_hp, static_cast<float>(e.gems), e.str, e.focus, rf_cooldowns(e.ch), e.range, static_cast<int>(e.type), x + 2 * RF_W);
            enemy_gems += static_cast<float>(e.gems);
        }
        for (int i = 0; i < static_cast<int>(mem.size()) && i < RF_MAX_MEM; ++i) {
            const RfSeen& s = *mem[i];
            const float dx = static_cast<float>(s.pos.x - p.x), dy = static_cast<float>(s.pos.y - p.y);
            const float raw[RF_MEM] = {dx, dy, std::max(std::abs(dx), std::abs(dy)), static_cast<float>(S.round - s.round), s.hp_frac, std::log1p(s.gems)};
            rf_phi_add(raw, RF_MEM, RF_MEM_MEAN, RF_MEM_STD, RF_MEM_X, RF_MEM_B, RF_MEM_EMB[std::clamp(s.type, 0, 12)], x + 3 * RF_W);
        }
        const int us = cambc::global_submitted_gems(team::ally), them = cambc::global_submitted_gems(team::enemy);
        const float game[RF_GAME] = {static_cast<float>(S.round), static_cast<float>(us - them), std::log1p(static_cast<float>(me.gem_count())),
                                     std::log1p(ally_gems), std::log1p(enemy_gems), rf_nearest(p, own_spawn), rf_nearest(p, enemy_spawn),
                                     rf_nearest(p, W.altars)};
        for (int k = 0; k < RF_GAME; ++k) x[4 * RF_W + k] = (game[k] - RF_GAME_MEAN[k]) / RF_GAME_STD[k];
        v128_t h[RF_HV];
        for (int v = 0; v < RF_HV; ++v) h[v] = wasm_v128_load(RF_HEAD1_B + 4 * v);
        for (int k = 0; k < 4 * RF_W + RF_GAME; ++k) rf_axpy(h, RF_HEAD1[k], x[k], RF_HV);
        alignas(16) float hv[RF_H];
        const v128_t z = wasm_f32x4_splat(0.0f);
        for (int v = 0; v < RF_HV; ++v) wasm_v128_store(hv + 4 * v, wasm_f32x4_pmax(h[v], z));
        float out = RF_HEAD2_B;
        for (int j = 0; j < RF_H; ++j) out += RF_HEAD2[j] * hv[j];
        rf_arrivals = std::exp(out);
    }
    // Remember every enemy seen this turn (after the prediction, as in ml/reinforce_data.py).
    for (const auto& e : S.enemies) {
        const auto id = handle_id(e.ch);
        RfSeen s{id, S.round, e.pos, e.hp / e.max_hp, static_cast<float>(e.gems), static_cast<int>(e.type)};
        bool found = false;
        for (auto& old : rf_seen)
            if (old.id == id) old = s, found = true;
        if (!found) rf_seen.push_back(s);
    }
}
