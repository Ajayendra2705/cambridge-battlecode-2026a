// Part of bot.cpp: enemy gain model (eg, ml/eg_*). Expected gems an enemy champion adds to its team over the next 60
// rounds, from what this champion sees now. Feature order must match FEATURES in ml/eg_data.py.
#include "eg_weights.h"

void eg_features(const ChampSnap& e, float* x) {
    float d_altar = 99;
    for (auto a : W.altars) d_altar = std::min(d_altar, static_cast<float>(dist(e.pos, a)));
    const auto bag_me = static_cast<float>(cambc::self().gem_count());
    int us_near = dist(S.me, e.pos) <= 4, them_near = 0, d_us = dist(S.me, e.pos);
    float bag_near = d_us <= 4 ? bag_me : 0.0f;
    for (const auto& a : S.allies) {
        const int d = dist(a.pos, e.pos);
        d_us = std::min(d_us, d);
        if (d <= 4) ++us_near, bag_near = std::max(bag_near, static_cast<float>(a.bag));
    }
    for (const auto& o : S.enemies)
        if (o.ch != e.ch && dist(o.pos, e.pos) <= 5) ++them_near;
    int near[2] = {-1, -1}, nd[2] = {999, 999};
    for (int gi = 0; gi < static_cast<int>(W.groups.size()); ++gi) {
        int d = 999;
        for (auto p : W.groups[gi].spawns) d = std::min(d, dist(e.pos, p));
        if (d < nd[0]) near[1] = near[0], nd[1] = nd[0], near[0] = gi, nd[0] = d;
        else if (d < nd[1]) near[1] = gi, nd[1] = d;
    }
    float capturing = 0;
    float* g = x + 11;
    for (int k = 0; k < 2; ++k, g += 5) {
        if (near[k] < 0) { g[0] = 99, g[1] = g[2] = g[3] = g[4] = 0; continue; }
        const auto& G = W.groups[near[k]];
        float hp = 0;
        if (G.state == 0) for (float h : G.hp) hp += std::max(0.0f, h);
        const bool cleared = G.state != 0;
        if (cleared && nd[k] <= 1) capturing = 1;
        g[0] = static_cast<float>(nd[k]), g[1] = static_cast<float>(G.gems), g[2] = static_cast<float>(G.gold);
        g[3] = std::log1p(hp), g[4] = cleared ? 1.0f : 0.0f;
    }
    x[0] = e.hp / std::max(1.0f, e.max_hp);
    x[1] = std::log1p(static_cast<float>(e.gems));
    x[2] = d_altar;
    x[3] = static_cast<float>(dist(S.me, e.pos));
    x[4] = static_cast<float>(us_near);
    x[5] = static_cast<float>(them_near);
    x[6] = static_cast<float>(S.round);
    x[7] = capturing;
    x[8] = static_cast<float>(cambc::global_submitted_gems(team::enemy)) - static_cast<float>(cambc::global_submitted_gems(team::ally));
    x[9] = std::log1p(bag_near);
    x[10] = static_cast<float>(d_us);
}

float eg_predict(const ChampSnap& e) {
    float x[EG_N];
    eg_features(e, x);
    for (int i = 0; i < EG_N; ++i) x[i] = (x[i] - EG_MEAN[i]) / EG_STD[i];
    const int t = std::clamp(static_cast<int>(e.type), 0, 12);
    float out = EG_OUT_B[0];
    for (int j = 0; j < EG_H; ++j) {
        float h = EG_B[j] + EG_TYPE[t][j];
        for (int i = 0; i < EG_N; ++i) h += EG_W[j][i] * x[i];
        out += EG_OUT_W[0][j] * std::max(0.0f, h);
    }
    return std::exp(out);
}
