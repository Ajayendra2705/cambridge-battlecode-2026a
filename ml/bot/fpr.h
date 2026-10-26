// Part of bot.cpp: farm prediction model (fpr) (ml/fpr_*.py, model A). For a camp group, predicts P(our team captures it)
// and the rounds until it does, from the group, this champion and the units in view. pick_group rescores its best
// candidates with value * P / (T + bank cost). Features must match ml/fpr_data.py features_at().
// Unity build: included inside bot.cpp's anonymous namespace.

#include <wasm_simd128.h>
#include "fpr_weights.h"

constexpr int FPR_TOP = 8;
// Camp kinds in ml/fpr_data.py CAMP_TYPES order, with their base health.
constexpr float FPR_CAMP_HP[6] = {1350, 2400, 120, 120, 5000, 20000};
struct FprCand { double score; int group, team, state, travel; };
struct FprGroupStatic { float counts[6] = {}; float hp = 0; bool ready = false; alignas(16) float h[FPR_H] = {}; };
std::vector<FprGroupStatic> fpr_static;
float fpr_score_diff = 0, fpr_gems_log = 0;  // Read once per pick in fpr_self_part().

int fpr_kind(cambc::camp_type k) {
    switch (k) {
        case cambc::camp_type::wolf: return 0;
        case cambc::camp_type::elk: return 1;
        case cambc::camp_type::gem_cluster: return 2;
        case cambc::camp_type::gold_cluster: return 3;
        case cambc::camp_type::golem: return 4;
        case cambc::camp_type::monolith: return 5;
        default: return -1;
    }
}

void fpr_init() {
    if (!fpr_static.empty()) return;
    fpr_static.resize(W.groups.size());
    for (const auto& k : known_camps) {
        if (k.group < 0) continue;
        const int kind = fpr_kind(k.camp.kind());
        if (kind < 0) continue;
        auto& s = fpr_static[k.group];
        s.counts[kind] += 1;
        s.hp += FPR_CAMP_HP[kind];
        s.ready = true;
    }
    // Inputs 0-8 (camp counts, camp hp, gems, gold) never change: their hidden contribution is computed once.
    for (size_t gi = 0; gi < fpr_static.size(); ++gi) {
        auto& s = fpr_static[gi];
        const float raw[9] = {s.counts[0], s.counts[1], s.counts[2], s.counts[3], s.counts[4], s.counts[5], s.hp,
                              static_cast<float>(W.groups[gi].gems), static_cast<float>(W.groups[gi].gold)};
        for (int k = 0; k < 9; ++k) {
            const float x = (raw[k] - FPR_GAME_MEAN[k]) / FPR_GAME_STD[k];
            for (int j = 0; j < FPR_H; ++j) s.h[j] += FPR_GAME_W[k][j] * x;
        }
    }
}

float fpr_nearest(vec2 p, const std::vector<vec2>& pts) {
    int best = 99;
    for (auto q : pts) best = std::min(best, dist(p, q));
    return static_cast<float>(best);
}

// Hidden pre-activation from this champion (shared by every group): type embedding + self features.
void fpr_self_part(float* h) {  // h: FPR_H floats, 16-byte aligned
    auto& me = cambc::self();
    std::array<float, 2> cd{};
    int n = 0;
    for (const auto& ab : me.abilities()) {
        if (n >= 2) break;
        try {
            cd[n] = static_cast<float>(ab.cooldown());
        } catch (const cambc::error&) {
        }
        ++n;
    }
    const float raw[FPR_SELF] = {0, 0, 0, S.hp, S.hp / S.max_hp, std::log1p(static_cast<float>(me.gem_count())), S.str, S.focus, cd[0], cd[1],
                                static_cast<float>(S.range)};
    const int type = std::clamp(static_cast<int>(me.champion_name()), 0, 12);
    fpr_score_diff = static_cast<float>(static_cast<int>(cambc::global_submitted_gems(team::ally)) - static_cast<int>(cambc::global_submitted_gems(team::enemy)));
    fpr_gems_log = raw[5];
    for (int j = 0; j < FPR_H; ++j) h[j] = FPR_GAME_B[j] + FPR_TYPE[type][j];
    for (int k = 0; k < FPR_SELF; ++k) {
        const float x = (raw[k] - FPR_SELF_MEAN[k]) / FPR_SELF_STD[k];
        for (int j = 0; j < FPR_H; ++j) h[j] += FPR_SELF_W[k][j] * x;
    }
    // Inputs 11-17 depend on this champion only (spawn and altar distances, round, score, bag; dist_group is 0).
    static std::vector<vec2> own_spawn, enemy_spawn;
    if (own_spawn.empty()) {
        for (auto q : W.ally_spawn.positions()) own_spawn.push_back(q);
        for (auto q : W.enemy_spawn.positions()) enemy_spawn.push_back(q);
    }
    const float mine[7] = {fpr_nearest(S.me, own_spawn), fpr_nearest(S.me, enemy_spawn), fpr_nearest(S.me, W.altars), static_cast<float>(S.round),
                           fpr_score_diff, fpr_gems_log, 0.0f};
    for (int k = 0; k < 7; ++k) {
        const float x = (mine[k] - FPR_GAME_MEAN[11 + k]) / FPR_GAME_STD[11 + k];
        for (int j = 0; j < FPR_H; ++j) h[j] += FPR_GAME_W[11 + k][j] * x;
    }
}

// P(capture) and expected rounds from the first hit to the capture, for group gi, given the shared hidden part.
void fpr_predict(int gi, const float* h_self, float& p, float& t) {
    const auto& g = W.groups[gi];
    const auto& st = fpr_static[gi];
    int allies = 0, enemies = 0;
    for (const auto& a : S.allies) allies += fpr_nearest(a.pos, g.spawns) <= 5;
    for (const auto& e : S.enemies) enemies += fpr_nearest(e.pos, g.spawns) <= 5;
    const float dyn[2] = {static_cast<float>(allies), static_cast<float>(enemies)};
    constexpr int V = FPR_H / 4;
    v128_t h[V];
    for (int v = 0; v < V; ++v) h[v] = wasm_f32x4_add(wasm_v128_load(h_self + 4 * v), wasm_v128_load(st.h + 4 * v));
    for (int k = 0; k < 2; ++k) {
        const v128_t x = wasm_f32x4_splat((dyn[k] - FPR_GAME_MEAN[9 + k]) / FPR_GAME_STD[9 + k]);
        for (int v = 0; v < V; ++v) h[v] = wasm_f32x4_add(h[v], wasm_f32x4_mul(wasm_v128_load(FPR_GAME_W[9 + k] + 4 * v), x));
    }
    const v128_t z = wasm_f32x4_splat(0.0f);
    v128_t a0 = z, a1 = z;
    for (int v = 0; v < V; ++v) {
        const v128_t r = wasm_f32x4_pmax(h[v], z);
        a0 = wasm_f32x4_add(a0, wasm_f32x4_mul(wasm_v128_load(FPR_OUT_W[0] + 4 * v), r));
        a1 = wasm_f32x4_add(a1, wasm_f32x4_mul(wasm_v128_load(FPR_OUT_W[1] + 4 * v), r));
    }
    float o[2] = {FPR_OUT_B[0] + wasm_f32x4_extract_lane(a0, 0) + wasm_f32x4_extract_lane(a0, 1) + wasm_f32x4_extract_lane(a0, 2) + wasm_f32x4_extract_lane(a0, 3),
                  FPR_OUT_B[1] + wasm_f32x4_extract_lane(a1, 0) + wasm_f32x4_extract_lane(a1, 1) + wasm_f32x4_extract_lane(a1, 2) + wasm_f32x4_extract_lane(a1, 3)};
    p = 1.0f / (1.0f + std::exp(-o[0]));
    t = std::exp(o[1]);
}
