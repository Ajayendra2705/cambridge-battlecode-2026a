// Champion controller: turn pipeline, shop, tribute, travel and shared helpers.
#include "bot.h"
#include <string_view>
#include "params.h"

constexpr int kReportRound = 0;  // edit_vtreport.py: fastscreen ROUNDS cut-off report round (0: never)

std::vector<champion>& ally_handles() {
    static std::vector<champion> v = champions(team::ally);
    return v;
}
std::vector<champion>& enemy_handles() {
    static std::vector<champion> v = champions(team::enemy);
    return v;
}

namespace {

// One host call for a champion's full visible state; false when hidden or dead.
bool fetch(const champion& c, detail::champion_info& out) {
    const auto h = static_cast<std::uint32_t>(static_cast<handle_champion_t>(c));
    if (detail::sdk_champion(h, &out) != 0) return false;
    return out.x >= 0 && out.y >= 0 && (out.state & 1u) != 0;
}

// Fixed opening emblems, then a repeating cycle of bruiser emblems (health mixed in, like top teams).
std::vector<BuildStep> plan_cycle(std::vector<BuildStep> head, const std::vector<BuildStep>& cycle) {
    for (int k = 0; k < 60; ++k) head.push_back(cycle[static_cast<std::size_t>(k) % cycle.size()]);
    head.push_back({ cycle[0].fam, cycle[0].stat, 9999 });
    return head;
}

std::vector<BuildStep> plan_for(champion_type t) {
    using F = item_family;
    using S = item_stat;
    if (P_BUILD == 3) {
        // Monster emblem first on damage dealers (top teams), no treasure; tanks keep jungle first.
        switch (t) {
        case champion_type::vesper_vale:
            return plan_cycle({ {F::monster, S::strength, 5}, {F::jungle, S::strength, 5}, {F::durability, S::health, 5} },
                { {F::bruiser, S::strength, 5}, {F::bruiser, S::strength, 5}, {F::bruiser, S::health, 5} });
        case champion_type::vendetta:
            return plan_cycle({ {F::monster, S::strength, 5}, {F::jungle, S::strength, 5}, {F::durability, S::health, 5} },
                { {F::bruiser, S::strength, 5}, {F::bruiser, S::health, 5} });
        case champion_type::heart_of_ruin:
            return plan_cycle({ {F::jungle, S::focus, 5}, {F::monster, S::health, 5}, {F::durability, S::health, 5} },
                { {F::bruiser, S::health, 5}, {F::bruiser, S::focus, 5} });
        case champion_type::marcella:
            return plan_cycle({ {F::jungle, S::strength, 5}, {F::monster, S::strength, 5}, {F::durability, S::health, 5} },
                { {F::bruiser, S::strength, 5}, {F::bruiser, S::health, 5} });
        case champion_type::ryth:
            return plan_cycle({ {F::jungle, S::health, 5}, {F::monster, S::strength, 5}, {F::durability, S::health, 5} },
                { {F::bruiser, S::health, 5} });
        default: break;
        }
    }
    if (P_DPS_HP && (t == champion_type::vesper_vale || t == champion_type::vendetta)) {
        // Damage dealers get health early: top-team bursts one-shot 1000-health champions.
        if (t == champion_type::vesper_vale)
            return plan_cycle({ {F::jungle, S::strength, 5}, {F::durability, S::health, 5}, {F::monster, S::strength, 5} },
                { {F::bruiser, S::strength, 5}, {F::bruiser, S::health, 5} });
        return plan_cycle({ {F::jungle, S::strength, 5}, {F::durability, S::health, 5}, {F::monster, S::strength, 5} },
            { {F::bruiser, S::strength, 5}, {F::bruiser, S::health, 5} });
    }
    if (P_BUILD == 4) {
        // Health early (mid-ladder teams win the fights by outlasting us), no treasure.
        switch (t) {
        case champion_type::vesper_vale:
        case champion_type::vendetta:
            return plan_cycle({ {F::jungle, S::strength, 5}, {F::durability, S::health, 5}, {F::monster, S::strength, 5} },
                { {F::bruiser, S::strength, 5}, {F::bruiser, S::health, 5} });
        case champion_type::heart_of_ruin:
            return plan_cycle({ {F::jungle, S::focus, 5}, {F::durability, S::health, 5} },
                { {F::bruiser, S::health, 5}, {F::bruiser, S::health, 5}, {F::bruiser, S::focus, 5} });
        case champion_type::marcella:
            return plan_cycle({ {F::jungle, S::focus, 5}, {F::durability, S::health, 5}, {F::monster, S::focus, 5} },
                { {F::bruiser, S::health, 5}, {F::bruiser, S::focus, 5} });
        case champion_type::ryth:
            return plan_cycle({ {F::jungle, S::health, 5}, {F::durability, S::health, 5} }, { {F::bruiser, S::health, 5} });
        default: break;
        }
    }
    if (P_BUILD == 2 || P_BUILD == 3) {
        switch (t) {
        case champion_type::vesper_vale:
            return plan_cycle({ {F::jungle, S::strength, 5}, {F::treasure, S::strength, 5}, {F::monster, S::strength, 5}, {F::durability, S::health, 5} },
                { {F::bruiser, S::strength, 5}, {F::bruiser, S::strength, 5}, {F::bruiser, S::health, 5} });
        case champion_type::vendetta:
            return plan_cycle({ {F::jungle, S::strength, 5}, {F::treasure, S::strength, 5}, {F::monster, S::strength, 5}, {F::durability, S::health, 5} },
                { {F::bruiser, S::strength, 5}, {F::bruiser, S::health, 5} });
        case champion_type::heart_of_ruin:
            return plan_cycle({ {F::jungle, S::focus, 5}, {F::treasure, S::health, 5}, {F::durability, S::health, 5} },
                { {F::bruiser, S::health, 5}, {F::bruiser, S::focus, 5} });
        case champion_type::marcella:
            if (P_MAR_BUILD == 1)  // focus nuker (top teams): her 2x-focus nuke reaches 4 tiles
                return plan_cycle({ {F::monster, S::focus, 5}, {F::jungle, S::focus, 5}, {F::durability, S::health, 5} },
                    { {F::bruiser, S::focus, 5}, {F::bruiser, S::focus, 5}, {F::bruiser, S::health, 5} });
            return plan_cycle({ {F::jungle, S::strength, 5}, {F::durability, S::health, 5} },
                { {P_MAR_STR ? F::bruiser : F::bruiser, P_MAR_STR ? S::strength : S::focus, 5}, {F::bruiser, S::health, 5} });
        case champion_type::ryth:
            return plan_cycle({ {F::jungle, S::health, 5}, {F::treasure, S::health, 5}, {F::durability, S::health, 5} },
                { {F::bruiser, S::health, 5} });
        default: break;
        }
    }
    switch (t) {
    case champion_type::vesper_vale: return { {F::treasure, S::strength, 5}, {F::jungle, S::strength, 5}, {F::monster, S::strength, 5}, {F::durability, S::health, 5}, {F::bruiser, S::strength, 9999} };
    case champion_type::vendetta: return { {F::treasure, S::strength, 5}, {F::jungle, S::strength, 5}, {F::monster, S::strength, 5}, {F::durability, S::health, 5}, {F::bruiser, S::strength, 9999} };
    case champion_type::heart_of_ruin: return { {F::treasure, S::health, 5}, {F::jungle, S::focus, 5}, {F::durability, S::health, 5}, {F::bruiser, S::focus, 9999} };
    case champion_type::marcella:
        if (P_MAR_STR) return { {F::jungle, S::strength, 5}, {F::durability, S::health, 5}, {F::bruiser, S::strength, 9999} };
        return { {F::jungle, S::strength, 5}, {F::durability, S::health, 5}, {F::bruiser, S::focus, 9999} };
    case champion_type::cassi: return { {F::power, S::focus, 5}, {F::durability, S::health, 5}, {F::bruiser, S::focus, 9999} };
    case champion_type::issac: return { {F::treasure, S::strength, 5}, {F::jungle, S::strength, 5}, {F::bruiser, S::strength, 9999} };
    case champion_type::ryth: return { {F::jungle, S::health, 5}, {F::treasure, S::health, 5}, {F::bruiser, S::health, 9999} };
    case champion_type::willow: return { {F::jungle, S::focus, 5}, {F::bruiser, S::focus, 9999} };
    case champion_type::stellar:
    case champion_type::prism: return { {F::jungle, S::focus, 5}, {F::bruiser, S::focus, 9999} };
    case champion_type::ren: return { {F::jungle, S::health, 5}, {F::bruiser, S::health, 9999} };
    case champion_type::varg:
    case champion_type::tavi: return { {F::treasure, S::strength, 5}, {F::jungle, S::strength, 5}, {F::bruiser, S::strength, 9999} };
    }
    return { {F::bruiser, S::strength, 9999} };
}

}  // namespace

int Bot::ability_slot(ability_kind k) const {
    for (int s = 0; s < 2; ++s)
        if (ahas[s] && akind[s] == k) return s;
    return -1;
}

void Bot::init() {
    auto& me = self();
    World& W = world();
    if (!W.ready) W.init();
    if (!W.ready || fuel() < P_INIT_BOT_FUEL) return;  // edit_vtfuel2.py: the set-up goes on next turn (no suspension)
    auto& all = ally_handles();
    (void)enemy_handles();
    n_allies = std::min(5, static_cast<int>(all.size()));
    for (int i = 0; i < n_allies; ++i) {
        if (all[i] == me) idx = i;
        try {
            ainfo[i].type = all[i].champion_name();
            detail::champion_design d{};
            if (detail::sdk_champion_design(static_cast<std::int32_t>(ainfo[i].type), &d) == 0) {
                ainfo[i].str = d.base_stats.base_strength;
                ainfo[i].foc = d.base_stats.base_focus;
                ainfo[i].hp = ainfo[i].max_hp = d.base_stats.base_health;
            }
        } catch (...) {}
    }
    ctype = me.champion_name();
    ranged = me.attack_range() > 1;
    const auto abs = me.abilities();
    for (int s = 0; s < 2; ++s) {
        const auto& inf = abs[s].info();
        if (!inf) continue;
        ahas[s] = true;
        std::visit([&](const auto& v) {
            akind[s] = v.kind;
            aexcl[s] = v.exclusive_with_movement;
            if constexpr (requires { v.range; }) arange[s] = v.range;
            if constexpr (requires { v.modifier; }) amod[s] = v.modifier;
        }, *inf);
    }
    plan = plan_for(ctype);
    if (P_JUNGLE_FIRST && !(P_BUILD == 3 && (ctype == champion_type::vesper_vale || ctype == champion_type::vendetta)) &&
        !(P_MAR_BUILD == 1 && ctype == champion_type::marcella)) {
        // Jungle emblem first (top teams): -30% camp damage makes solo farming and tanking cheap.
        for (std::size_t k = 1; k < plan.size(); ++k)
            if (plan[k].fam == item_family::jungle) { std::rotate(plan.begin(), plan.begin() + static_cast<long>(k), plan.begin() + static_cast<long>(k) + 1); break; }
    }
    if (P_PROSP_FIRST) {
        item_stat st = item_stat::strength;
        bool carry = true;
        switch (ctype) {
        case champion_type::vesper_vale: case champion_type::vendetta: case champion_type::ryth: st = item_stat::strength; break;
        case champion_type::marcella: case champion_type::heart_of_ruin: st = item_stat::focus; break;
        default: carry = false; break;
        }
        if (carry) plan.insert(plan.begin(), BuildStep{ item_family::prospector, st, 5 });
    }
    bought.assign(plan.size(), 0);
    blacklist.assign(W.groups.size(), -1);
    if (!P_OPENING && P_ELK_CHAIN <= 0) opening_done = true;  // edit_vtelk.py: elk maps are found at the first farm turn
    last_hp = me.health();
    inited = true;
}

bool Bot::has_lock() {
    if (lock_cache < 0) {
        lock_cache = 0;
        try { lock_cache = static_cast<int>(self().consumables()[consumable_type::altar_lock].count()); } catch (...) {}
    }
    return lock_cache > 0;
}

void Bot::shop() {
    auto& me = self();
    if (P_TP_SPAWN && world().tp_useful && me.gold_count() >= 10 && !has_crystal()) {
        try { me.buy(consumable_type::tp_crystal); crystal_cache = 1; } catch (...) {}
    }
    if (P_LOCKS && me.gold_count() >= 80 && !has_lock()) {
        try { me.buy(consumable_type::altar_lock); lock_cache = 1; } catch (...) {}
    }
    if (P_TP_SHORTCUT && !world().any_island && round - want_crystal_round < P_TP_WANT_WINDOW && me.gold_count() >= 10) {
        // Shortcuts by crystal were available lately: carry some.
        int have = 0;
        try { have = static_cast<int>(me.consumables()[consumable_type::tp_crystal].count()); } catch (...) {}
        for (int k = have; k < P_TP_CRYSTALS && me.gold_count() >= 10; ++k) {
            try { me.buy(consumable_type::tp_crystal); crystal_cache = 1; } catch (...) { break; }
        }
    }
    if (world().any_island && me.gold_count() >= 10) {
        // Two crystals: one to reach an island, one to get off it again (stranded champions get shot from the shore).
        int have = 0;
        try { have = static_cast<int>(me.consumables()[consumable_type::tp_crystal].count()); } catch (...) {}
        for (int k = have; k < P_CRYSTALS && me.gold_count() >= 10; ++k) {
            try { me.buy(consumable_type::tp_crystal); crystal_cache = 1; } catch (...) { break; }
        }
    }
    for (std::size_t i = 0; i < plan.size(); ++i) {
        const int need = plan[i].count - bought[i];
        if (need <= 0) continue;
        const int n = std::min<int>(need, static_cast<int>(me.gold_count() / 30));
        if (n <= 0) return;
        try {
            me.buy(get_item_enum(plan[i].fam, plan[i].stat, true), static_cast<std::uint32_t>(n));
            bought[i] += n;
        } catch (...) {
            return;
        }
        if (bought[i] < plan[i].count) return;
    }
}

void Bot::read_cooldowns(champion& c, AbilMeta& m, Seen& s) {
    try {
        const auto abs = c.abilities();
        if (!m.known) {
            m.known = true;
            for (int k = 0; k < 2; ++k) {
                const auto& inf = abs[static_cast<std::size_t>(k)].info();
                if (!inf) continue;
                m.has[static_cast<std::size_t>(k)] = true;
                std::visit([&](const auto& v) {
                    m.kind[static_cast<std::size_t>(k)] = v.kind;
                    if constexpr (requires { v.modifier; }) m.mod[static_cast<std::size_t>(k)] = v.modifier;
                }, *inf);
            }
        }
        s.cd_known = true;
        for (int k = 0; k < 2; ++k) {
            const auto sk = static_cast<std::size_t>(k);
            if (!m.has[sk]) continue;
            const int cd = abs[sk].cooldown();
            switch (m.kind[sk]) {
            case ability_kind::attack_reset: s.reset_cd = std::min(s.reset_cd, cd); break;
            case ability_kind::damage:
            case ability_kind::aoe_damage:
            case ability_kind::cc:
                if (m.mod[sk] > 0) { s.nuke_cd = std::min(s.nuke_cd, cd); s.nuke_dmg += m.mod[sk] * s.foc; }
                break;
            case ability_kind::dash:
                s.dash_cd = std::min(s.dash_cd, cd);
                if (m.mod[sk] > 0) { s.dash_hits = true; s.nuke_cd = std::min(s.nuke_cd, cd); s.nuke_dmg += m.mod[sk] * s.foc; }
                break;
            default: break;
            }
        }
    } catch (...) {}
}

// Wards (one active per champion, 10-round recharge, vision radius 6, owner-only vision): keep one next to me,
// on the tile that reveals most of what I cannot see now, bushes first (champions hide in them).
void Bot::place_ward() {
    if (round < ward_next) return;
    auto& me = self();
    World& W = world();
    const vec2 p = me.position();
    if (bb_test(*W.my_spawn, p)) return;
    int cd = 0;
    try { cd = me.ward_cooldown(); } catch (...) { ward_next = round + 5; return; }
    if (cd > 0) { ward_next = round + cd; return; }
    // Not in fights: placing costs 10-15k fuel, which a fight turn cannot spare (exhausted turns lose their move).
    for (const auto& e : enemies)
        if (cheb(e.pos, p) <= P_WARD_ENEMY_R) { ward_next = round + 1; return; }
    if (fuel() < P_WARD_MIN_FUEL) return;
    bitboard cand;
    cand.clear();
    cand.draw_chebyshev(p, static_cast<float>(constants::ward_placement_radius));
    cand &= W.open_tiles();  // edit_vtfuel.py
    bitboard tmp;
    int best = -1;
    vec2 bq = p;
    std::vector<std::pair<int, vec2>> tops;  // edit_vtwards.py: every scored candidate, for retries
    const bitboard& bush = map::bushes();
    if (P_WARD_BUSH_ONLY) {  // edit_vtwards.py
        bool bush_ok = false;
        bitboard bc = cand;
        bc &= bush;
        if (!bc.is_empty() && !P_WARD_SKIP_ALLY) {  // edit_vtfuel.py: no allied wards to flood from: bc stays as it is
            cand.swap(bc);
            bush_ok = true;
        } else if (!bc.is_empty()) {
            // bush patches (8-connected bush tiles) that already hold an allied ward
            bitboard held;
            held.clear();
            bitboard own;
            own.clear();
            if (P_WARD_SKIP_ALLY) { try { own = vision::ward_tiles(team::ally); } catch (...) { own.clear(); } }
            own &= bush;
            std::vector<vec2> open;
            for (vec2 w : own.positions()) {
                if (held.is_set(w)) continue;
                held.set(w);
                open.push_back(w);
                while (!open.empty()) {
                    const vec2 a = open.back();
                    open.pop_back();
                    for (int dx = -1; dx <= 1; ++dx)
                        for (int dy = -1; dy <= 1; ++dy) {
                            const vec2 q{ a.x + dx, a.y + dy };
                            if ((dx || dy) && map::is_in_bounds(q) && bush.is_set(q) && !held.is_set(q)) { held.set(q); open.push_back(q); }
                        }
                }
            }
            bc &= ~held;
            if (!bc.is_empty()) { cand = bc; bush_ok = true; }
        }
        static int bush_since = -1;  // per champion (each runs its own program): first round a ward was due without a free bush
        if (bush_ok) {
            bush_since = -1;
        } else if (P_WARD_BUSH_ONLY >= 2) {
            if (bush_since < 0) bush_since = round;
            if (round - bush_since < P_WARD_OPEN_WAIT) { ward_next = round + 1; return; }
            bush_since = -1;  // an open-ground ward now; wait for a bush again afterwards
        }
    }
    bitboard notvis = W.vis ? ~*W.vis : bitboard{};  // edit_vtfuel.py: only when scoring
    for (vec2 q : cand.positions()) {
        try {
            ward::visible_tiles_from_into(q, tmp);
        } catch (...) { continue; }
        tmp &= notvis;
        int sc = static_cast<int>(tmp.count()) + (bb_test(bush, q) ? P_WARD_BUSH : 0);
        tops.push_back({ sc, q });  // edit_vtwards.py
        if (sc > best) { best = sc; bq = q; }
    }
    if (best < 0) return;
    // edit_vtwards.py: best first; a teammate's ward on the tile throws ally_ward_present without using the charge - try the next
    std::stable_sort(tops.begin(), tops.end(), [](const auto& a, const auto& b) { return a.first > b.first; });
    if (tops.empty() || tops.front().second != bq) tops.insert(tops.begin(), { best, bq });
    ward_next = round + 2;
    for (std::size_t i = 0; i < tops.size() && i < 3; ++i) {
        try {
            if (me.place_ward(tops[i].second)) { ward_next = round + 10; break; }
            // false (ward probe, Nov 2): a hidden teammate's ward stood there - now revealed, no charge used: try the next tile
        } catch (const cambc::error& e) {
            if (e.code() != error_code::invalid_action_place_ward_ally_ward_present) break;
        } catch (...) { break; }
    }
}

void Bot::see_units() {
    enemies.clear();
    allies.clear();
    detail::champion_info ci{};
    auto& eh = enemy_handles();
    while (emem.size() < eh.size()) emem.emplace_back();
    for (std::size_t k = 0; k < eh.size(); ++k) {
        auto& c = eh[k];
        if (!fetch(c, ci)) continue;
        if (bb_test(*world().enemy_spawn, { ci.x, ci.y })) continue;  // untouchable and fully healing
        Seen s{ c, static_cast<int>(k), { ci.x, ci.y }, ci.health, ci.max_health, ci.strength, ci.focus, ci.attack_range, 0, false };
        s.channeling = P_RECALL_READ ? ((ci.state & ((1u << 2) | (1u << 12))) != 0 || recall_counts(c, static_cast<unsigned>(ci.state), rc_enemy, k))
                                     : (ci.state & ((1u << 1) | (1u << 2) | (1u << 12))) != 0;  // edit_vtrecall.py
        s.type = static_cast<champion_type>(ci.type);
        s.seen_round = round;
        try { s.gems = c.gem_count(); } catch (...) {}
        if (P_ENEMY_CD) {
            while (emeta.size() <= k) emeta.emplace_back();
            read_cooldowns(c, emeta[k], s);
        }
        enemies.push_back(s);
        if (emem[k].s && emem[k].seen_round < round) { emem[k].prev_pos = emem[k].s->pos; emem[k].prev_round = emem[k].seen_round; }
        emem[k].s.emplace(s);
        emem[k].seen_round = round;
    }
    auto& me = self();
    for (int i = 0; i < n_allies; ++i) {
        auto& c = ally_handles()[static_cast<std::size_t>(i)];
        if (c == me) continue;
        if (!fetch(c, ci)) continue;
        const bool ach = P_RECALL_READ ? ((ci.state & ((1u << 2) | (1u << 12))) != 0 || recall_counts(c, static_cast<unsigned>(ci.state), rc_ally, static_cast<std::size_t>(i)))
                                       : (ci.state & ((1u << 1) | (1u << 2) | (1u << 12))) != 0;  // edit_vtrecall.py
        allies.push_back(Seen{ c, i, { ci.x, ci.y }, ci.health, ci.max_health, ci.strength, ci.focus, ci.attack_range, 0, ach, static_cast<champion_type>(ci.type), round });
        if (P_ALLY_CD && i < 6) read_cooldowns(c, ameta[static_cast<std::size_t>(i)], allies.back());
        auto& a = ainfo[static_cast<std::size_t>(i)];
        a.str = ci.strength;
        a.foc = ci.focus;
        a.hp = ci.health;
        a.max_hp = ci.max_health;
        a.pos = { ci.x, ci.y };
        a.seen_round = round;
    }
    ainfo[static_cast<std::size_t>(idx)].str = me.strength();
    ainfo[static_cast<std::size_t>(idx)].foc = me.focus();
    ainfo[static_cast<std::size_t>(idx)].hp = me.health();
    ainfo[static_cast<std::size_t>(idx)].max_hp = me.max_health();
    ainfo[static_cast<std::size_t>(idx)].pos = me.position();
    ainfo[static_cast<std::size_t>(idx)].seen_round = round;
}

void Bot::build_threat(vec2 pos, int ignore_group) {
    World& W = world();
    threat_for = ignore_group;
    if (!threat) threat.emplace();
    threat->clear();
    if (!camp_threat) camp_threat.emplace();
    camp_threat->clear();
    for (const auto& x : sightings)
        if (round - x.round <= 8 && cheb(x.pos, pos) <= 14) threat->draw_chebyshev(x.pos, 4.f);
    // Awake damaging camps only: camps never aggro by proximity, they wake when their group is attacked.
    for (auto& g : W.groups) {
        if (g.id == ignore_group || g.state != GState::Alive || g.dps <= 0) continue;
        if (round - g.awake_max > 2) continue;  // edit_vtfuel.py: no camp of it awake lately
        bool awake = false;
        for (const auto& c : g.camps)
            if (c.hp > 0 && camp_str(c.type) > 0 && round - c.awake_round <= 2) { awake = true; break; }
        if (awake) {
            *threat |= W.danger_of(g);
            *camp_threat |= W.danger_of(g);
        }
    }
}

// Enemies seen nearby recently: play safer with health.
bool Bot::recent_enemy() const {
    const vec2 p = self().position();
    for (const auto& x : sightings)
        if (round - x.round <= 20 && cheb(x.pos, p) <= 16) return true;
    return !enemies.empty();
}

// edit_vtrecall.py: a recall is a real channel once it counts down from the round before (or has 1 round left); a turn-end
// pre-start shows the full timer whenever it is seen. mem[k] = (round last seen recalling, rounds left then).
bool Bot::recall_counts(champion& c, unsigned state, std::vector<std::pair<int, int>>& mem, std::size_t k) {
    if (mem.size() <= k) mem.resize(k + 1, { -9, 0 });
    if ((state & (1u << 1)) == 0) {
        mem[k] = { -9, 0 };
        return false;
    }
    int left = 99;
    try { left = c.remaining_channel_time(); } catch (...) { return true; }
    // review fix: a pre-start shows the same full timer whenever it is seen, so any drop since the last sighting (within 6 rounds)
    // is a real channel - not only an exact one-round step (turn-order flips near enemies and vision gaps skip or repeat steps)
    const bool counting = mem[k].first >= 0 && round - mem[k].first <= 6 && left < mem[k].second;
    mem[k] = { round, left };
    return counting || left <= 1;
}

// edit_vtrecall.py: keep last turn's pre-started recall only when this turn goes home anyway (play_turn's heal / shoptrip triggers
// with go_home's own recall conditions: off spawn, home farther than 6, no danger).
bool Bot::rp_keep(vec2 p, float frac) {
    World& W = world();
    auto& me = self();
    if (!enemies.empty() || hurt || bb_test(*W.my_spawn, p) || W.spawn_dist_at(p) <= 6) return false;
    if (threat && bb_test(*threat, p)) return false;
    // review fix: play_turn does not go home beside its task group (finishing it, retiring next to it, capturing it)
    if (task >= 0 && task < static_cast<int>(W.groups.size())) {
        const Group& g = W.groups[static_cast<std::size_t>(task)];
        if (cheb(g.center, p) <= g.radius + (P_FIX_RPK ? 8 : 4)) return false;  // edit_vtfix1.py: retire_near reaches radius + 8
        if (P_FIX_RPK && g.state == GState::Reward) return false;  // edit_vtfix1.py
    }
    const unsigned gems = me.gem_count();
    const bool low = heading_home || frac < P_HOME_HP || (frac < P_HOME_HP_ENEMY && recent_enemy());
    if (low && gems > 0) {  // with a bag and an altar within 3, play_turn tributes instead
        int adist = 999;
        if (W.gated) { if (W.open_gate(p, adist) < 0) adist = 999; }
        else W.best_altar(p, threat ? &*threat : nullptr, adist);
        if (adist <= 3) return false;
    }
    const bool shop = gems == 0 && (me.gold_count() >= P_SHOP_GOLD || (me.gold_count() >= P_SHOP_GOLD_HURT && frac < 0.6f));
    if (!low && !shop) return false;
    // keep it: play_turn's heal / shoptrip bookkeeping (review fix)
    act = low ? "heal" : "shoptrip";
    if (low) heading_home = true;
    task = -1;
    comms.write_raw(idx, slot::kHome, false);
    return true;
}

// edit_vtrecall.py: queue a recall at the end of a full turn (Eric: every turn end; P_RECALL_PRIME_HIDDEN: out of enemy sight only),
// not channelling, not on a reward, not on spawn.
void Bot::rp_prime(vec2 p, int on_group) {
    World& W = world();
    auto& me = self();
    if ((P_RECALL_PRIME_HIDDEN && !enemies.empty()) || bb_test(*W.my_spawn, p)) return;  // Eric: queued at every turn end
    try {
        if (!me.is_alive() || me.is_recalling() || me.is_submitting_gems() || me.is_teleporting()) return;
    } catch (...) { return; }
    if (on_group >= 0 && on_group < static_cast<int>(W.groups.size()) && W.groups[static_cast<std::size_t>(on_group)].state == GState::Reward) return;
    try {
        me.recall();
        rp_primed = true;
    } catch (...) {}
}

bool Bot::go_home() {
    auto& me = self();
    World& W = world();
    const vec2 p = me.position();
    if (bb_test(*W.my_spawn, p)) return false;
    const int d = W.spawn_dist_at(p);
    const bool danger = hurt || !enemies.empty() || (threat && bb_test(*threat, p));
    if (!danger && d > 6) {
        try { me.recall(); return true; } catch (...) {}
    }
    // Leave camp reach and enemy sightings by the shortest way first, then head home.
    // (camps only: stepping sideways from a chasing enemy just prolongs the chase)
    if (camp_threat && bb_test(*camp_threat, p) && nav.escape(*camp_threat, W.f_spawn.get())) {
        moved_this_turn = true;
        nav.begin_turn();
        return true;
    }
    if (move_to(*W.my_spawn, W.f_spawn.get(), true)) return true;
    // Boxed in (narrow corridor, allies in the way): at least step to where fewer camps reach me.
    if (P_YIELD && me.can_move()) {
        const float cur = W.camp_dps_on(p);
        if (cur > 0) {
            float best = cur;
            int bh = 1 << 30;
            vec2 bq = p;
            for (auto d : kDirs) {
                const vec2 q = p + d;
                if (!nav.passable(q)) continue;
                const float v = W.camp_dps_on(q);
                int h = df_get(*W.f_spawn, q);
                if (h == distance_field::unreachable) h = 1 << 20;
                if (v < best || (v == best && v < cur && h < bh)) { best = v; bh = h; bq = q; }
            }
            if (bq != p) {
                try { if (me.move_absolute(bq)) { moved_this_turn = true; nav.begin_turn(); return true; } } catch (...) {}
            }
        }
    }
    return false;
}

// An ally heading home is boxed in behind me (narrow corridors): step out of its way, homewards if needed.
bool Bot::yield_path() {
    auto& me = self();
    if (!me.can_move()) return false;
    World& W = world();
    const vec2 p = me.position();
    const int fp = df_get(*W.f_spawn, p);
    if (fp == distance_field::unreachable) return false;
    for (const auto& a : allies) {
        if (cheb(a.pos, p) != 1 || a.channeling) continue;
        if (comms.code_of(a.index) != slot::kHome) continue;
        const int fa = df_get(*W.f_spawn, a.pos);
        if (fa == distance_field::unreachable || fp >= fa) continue;
        bool free_step = false;
        for (auto d : kDirs) {
            const vec2 q = a.pos + d;
            if (q == p || !in_bounds(q) || bb_test(*W.blocked, q)) continue;
            const int fq = df_get(*W.f_spawn, q);
            if (fq == distance_field::unreachable || fq >= fa) continue;
            if (!bb_test(nav.occupied(), q)) { free_step = true; break; }
        }
        if (free_step) continue;
        int best = 1 << 30;
        vec2 bq = p;
        for (auto d : kDirs) {
            const vec2 q = p + d;
            if (q == a.pos || !nav.passable(q)) continue;
            const int fq = df_get(*W.f_spawn, q);
            if (fq == distance_field::unreachable) continue;
            const bool in_way = cheb(q, a.pos) == 1 && fq < fa;
            int sc = (in_way ? 1000 : 0) + fq;
            if (camp_threat && bb_test(*camp_threat, q)) sc += 300;
            if (sc < best) { best = sc; bq = q; }
        }
        if (bq == p) return false;
        try {
            if (me.move_absolute(bq)) {
                act = "yield";
                moved_this_turn = true;
                nav.begin_turn();
                return true;
            }
        } catch (...) {}
        return false;
    }
    return false;
}

bool Bot::should_tribute(float hp_frac) {
    auto& me = self();
    const unsigned gems = me.gem_count();
    if (gems == 0) return false;
    World& W = world();
    int da = 0;
    if (W.gated) {
        // Gems only go in while a gate camp is down: then everything goes in before it respawns,
        // as long as I outlive the channel under the camps still standing around the gate tile.
        const int gi = W.open_gate(me.position(), da);
        if (gi < 0) return false;
        const vec2 t = W.gates[static_cast<std::size_t>(gi)].tile;
        const float dps = W.camp_dps_on(t) * camp_taken_mult(idx);
        const float chan = std::ceil(static_cast<float>(gems) * static_cast<float>(constants::submit_gem_duration_multiplier)) + 4.f;
        return dps <= 0 || me.health() > dps * (chan + 3.f);
    }
    W.best_altar(me.position(), threat ? &*threat : nullptr, da);
    if (da >= distance_field::unreachable) return false;
    if (round > static_cast<int>(constants::max_rounds) - 120) return true;
    if (gems + global_submitted_gems(team::ally) >= constants::winning_gems) return true;
    // End of the race: every submitted gem counts (close games are lost with gems still carried).
    if (static_cast<int>(global_submitted_gems(team::ally)) >= P_END_TRIB || static_cast<int>(global_submitted_gems(team::enemy)) >= P_END_TRIB) return true;
    if (static_cast<float>(gems) >= P_TRIB_GEMS + P_TRIB_SLOPE * static_cast<float>(da)) return true;
    // On my way to a team rally: no detours (the squad waits for me), only an altar right here.
    const bool rallying = comms.rally() >= 0 && comms.rally() == task;
    if (rallying) return da <= 2;
    if (da <= P_TRIB_NEAR) return true;
    if (gems >= P_TRIB_MID_GEMS && da <= P_TRIB_MID_DIST) return true;
    if (hp_frac < 0.45f && gems >= 8) return true;
    return false;
}

bool Bot::tribute() {
    auto& me = self();
    World& W = world();
    const vec2 p = me.position();
    for (std::size_t k = 0; k < W.altars.size(); ++k) {
        const vec2 a = W.altars[k];
        if (cheb(p, a) > constants::submit_gems_range) continue;
        detail::altar_lock_info li{};
        if (detail::sdk_altar_lock(a.x, a.y, detail::absolute_team(team::enemy), &li) == 0) {
            // Their lock blocks us: break it (basic attacks), then submit.
            W.altar_enemy_lock[k] = round;
            act = "unlock";
            if (cheb(p, a) <= me.attack_range() && me.can_attack()) {
                try { me.attack(altar_lock{ li }); return true; } catch (...) {}
            }
            continue;
        }
        W.altar_enemy_lock[k] = -1;
        // Lock it against them on the way (only blocks the enemy team).
        if (P_LOCKS && !lock_tried && W.altar_side[k] < P_LOCK_SIDE && has_lock()) {
            lock_tried = true;
            const bool ours = detail::sdk_altar_lock(a.x, a.y, detail::absolute_team(team::ally), &li) == 0;
            if (!ours) {
                try {
                    if (me.consumables()[consumable_type::altar_lock].use(a)) { lock_cache = 0; act = "lock"; return true; }
                } catch (...) {}
            }
        }
        try {
            const unsigned g = me.gem_count();
            me.submit_gems(a);
            const double d = std::ceil(static_cast<double>(g) * constants::submit_gem_duration_multiplier) + constants::submit_gem_base_duration;
            submit_end = round + std::max<int>(constants::submit_gem_minimum_duration, static_cast<int>(d));
            return true;
        } catch (...) {}
    }
    if (W.gated) {
        int dg = 0;
        const int gi = W.open_gate(p, dg);
        if (gi < 0) return false;
        const auto& gt = W.gates[static_cast<std::size_t>(gi)];
        Group& gg = W.groups[static_cast<std::size_t>(gt.group)];
        W.ensure_field(gg);
        act = "gate";
        bitboard goal;
        goal.clear();
        if (!bb_test(nav.occupied(), gt.tile)) {
            goal.set(gt.tile);
        } else {
            // An ally tributes there: queue near it, out of the reach of camps still standing.
            for (float r = 1.f; r <= 6.f && goal.is_empty(); r += 1.f) {
                goal.draw_chebyshev(gt.tile, r);
                goal &= W.open_tiles();  // edit_vtfuel.py
                if (camp_threat) goal &= ~*camp_threat;
                for (vec2 q : goal.positions())
                    if (W.camp_dps_on(q) > 0) goal.set(q, false);
            }
            if (goal.is_empty() || bb_test(goal, p)) return true;
        }
        return move_to(goal, gg.field.get(), true);
    }
    int da = 0;
    bool jump = false;
    int k = W.best_altar(p, threat ? &*threat : nullptr, da, has_crystal(), &jump);
    // Keep heading for the altar chosen last round unless it got clearly worse: threat zones that come and go
    // (camps falling asleep, stale sightings) made champions walk back and forth between two altars.
    if (P_ALTAR_STICKY > 0 && trib_altar >= 0 && round - trib_round <= 2 && k != trib_altar && static_cast<std::size_t>(trib_altar) < W.altars.size()) {
        const auto ts = static_cast<std::size_t>(trib_altar);
        if (W.altar_field[ts]) {
            const int ds = World::field_at(*W.altar_field[ts], p);
            bool champs_there = false;
            for (const auto& x : sightings)
                if (round - x.round <= 8 && cheb(x.pos, W.altars[ts]) <= 4) champs_there = true;
            if (ds < distance_field::unreachable && ds <= da + P_ALTAR_STICKY && !champs_there) { k = trib_altar; da = ds; jump = false; }
        }
    }
    trib_altar = k;
    trib_round = round;
    if (k < 0) return move_to(*W.altar_spots, W.f_altar.get(), true);
    const auto ks = static_cast<std::size_t>(k);
    if (jump) {
        // Altar cut off from the mainland: crystal jump next to it.
        if (!has_crystal()) {
            if (bb_test(*W.my_spawn, p)) {
                try { me.buy(consumable_type::tp_crystal); crystal_cache = 1; } catch (...) {}
                if (!has_crystal()) return false;
            } else {
                return go_home();
            }
        }
        if (cheb(p, W.altar_land[ks]) <= 4) {
            vec2 best{ -1, -1 };
            int bd = distance_field::unreachable;
            for (int dx = -3; dx <= 3; ++dx)
                for (int dy = -3; dy <= 3; ++dy) {
                    const vec2 q{ p.x + dx, p.y + dy };
                    if (!in_bounds(q) || bb_test(*W.blocked, q) || bb_test(*W.camp_tiles, q) || bb_test(*W.mainland, q)) continue;
                    if (bb_test(nav.occupied(), q)) continue;
                    const int d = df_get(*W.altar_field[ks], q);
                    if (d < bd) { bd = d; best = q; }
                }
            if (best.x >= 0) {
                try {
                    if (me.consumables()[consumable_type::tp_crystal].use(best)) { crystal_cache = 0; return true; }
                } catch (...) {}
            }
        }
        if (!W.altar_launch_field[ks] && fuel() > 50000) {
            const bitboard walls = *W.fwalls | *W.camp_tiles;
            bitboard root, visited;
            root.clear();
            root.set(W.altar_launch[ks]);
            W.altar_launch_field[ks] = std::make_unique<distance_field>();
            W.altar_launch_field[ks]->compute(walls, root, visited);
        }
        bitboard goal;
        goal.clear();
        goal.set(W.altar_launch[ks]);
        if (bb_test(goal, p)) return false;
        return move_to(goal, W.altar_launch_field[ks].get(), true);
    }
    bitboard goals = W.altar_spot_of[ks];
    if (threat) {
        bitboard safe = goals & ~*threat;
        if (!safe.is_empty()) goals = safe;
    }
    return move_to(goals, W.altar_field[ks].get(), true);
}

// Teleport-crystal shortcut (3 turn-ends channel, then a flash of up to 3 tiles): jump over holes and walls
// when it saves enough walking towards the goal of a static field.
bool Bot::tp_shortcut(const distance_field& f) {
    auto& me = self();
    World& W = world();
    const vec2 p = me.position();
    if (!enemies.empty() || hurt || me.is_teleporting() || !W.on_main(p)) return false;
    const int fp = World::field_at(f, p);
    if (fp == distance_field::unreachable || fp < P_TP_MIN) return false;
    const auto& L = detail::layout();
    const int cw = static_cast<int>(L.chunked_width);
    const std::uint16_t* F = f.ptr();
    vec2 best{ -1, -1 };
    int bgain = P_TP_GAIN;
    const bitboard& occ = nav.occupied();
    for (int dx = -3; dx <= 3; ++dx)
        for (int dy = -3; dy <= 3; ++dy) {
            const vec2 q{ p.x + dx, p.y + dy };
            if (q.x < 0 || q.y < 0 || q.x >= L.width || q.y >= L.height) continue;
            const int v = F[((q.y >> 3) * cw + (q.x >> 3)) * 64 + ((q.y & 7) << 3) + (q.x & 7)];
            if (v == distance_field::unreachable) continue;
            const int gain = fp - v - 4;
            if (gain <= bgain) continue;
            if (bb_test(*W.blocked, q) || bb_test(*W.camp_tiles, q) || bb_test(occ, q) || !bb_test(*W.mainland, q)) continue;
            if (threat && bb_test(*threat, q)) continue;
            bgain = gain;
            best = q;
        }
    if (best.x < 0) return false;
    if (!has_crystal()) {
        want_crystal_round = round;
        return false;
    }
    try {
        if (me.consumables()[consumable_type::tp_crystal].use(best)) {
            crystal_cache = -1;
            act = "tp_shortcut";
            return true;
        }
    } catch (...) {}
    return false;
}

bool Bot::move_to(const bitboard& goals, const distance_field* field, bool avoid, vec2 anchor) {
    if (P_TP_SHORTCUT && field && tp_check_round != round) {
        tp_check_round = round;
        if (tp_shortcut(*field)) return true;
    }
    nav.dash_slot = -1;
    nav.dashed = false;
    nav.dash_cd = 99;
    nav.cross_slot = -1;
    nav.bridge_wait = false;
    const int ds = ability_slot(ability_kind::dash);
    if (ds >= 0 && !cast_this_turn) {
        try { nav.dash_cd = static_cast<int>(self().abilities()[static_cast<std::size_t>(ds)].cooldown()); } catch (...) {}
        if (nav.dash_cd == 0) { nav.cross_slot = ds; nav.dash_hits = amod[static_cast<std::size_t>(ds)] > 0; }
    }
    if (ds >= 0 && !cast_this_turn && enemies.empty()) {
        try { if (self().abilities()[static_cast<std::size_t>(ds)].cooldown() == 0) nav.dash_slot = ds; } catch (...) {}
        nav.dash_hits = amod[static_cast<std::size_t>(ds)] > 0;
    }
    const bool ok = nav.travel(goals, field, avoid && threat ? &*threat : nullptr, anchor);
    if (nav.bridge_wait) LOGC("%d %d BW\n", round, idx);
    if (nav.dashed) cast_this_turn = true;
    if (ok) {
        moved_this_turn = true;
        nav.begin_turn();
    }
    return ok;
}

bool Bot::try_attack_reset_followup(const unit& target, Group* g) {
    auto& me = self();
    const int s = ability_slot(ability_kind::attack_reset);
    if (s < 0 || cast_this_turn || me.can_attack()) return false;
    try {
        auto abs = me.abilities();
        if (abs[s].cooldown() > 0) return false;
        const vec2 p = me.position();
        const int range = me.attack_range();
        bool first_ok = false;
        try { first_ok = target.is_visible() && target.health() > 0 && cheb(p, target.position()) <= range; } catch (...) {}
        // The first hit killed it: spend the reset on another camp of the group in reach (damaging ones first).
        std::optional<camp> alt;
        if (!first_ok && g) {
            float best = 1e9f;
            for (const auto& c : g->camps) {
                if (cheb(p, c.pos) > range) continue;
                try {
                    camp cc = vision::camp_at(c.pos);
                    const float h = cc.health();
                    if (h <= 0) continue;
                    const float sc = (camp_str(c.type) > 0 ? 0.f : 1e6f) + h;
                    if (sc < best) { best = sc; alt.emplace(cc); }
                } catch (...) {}
            }
        }
        if (!first_ok && !alt) return false;  // nothing to hit: keep the reset
        if (!abs[s].use()) return false;
        cast_this_turn = true;
        if (me.can_attack()) {
            if (first_ok) me.attack(target);
            else me.attack(*alt);
            return true;
        }
    } catch (...) {}
    return false;
}

// edit_vtspawn.py: siege groups this champion found it cannot hit from the spawn (walls: lost-world's wolves 3 tiles off the spawn behind a
// wall were "sieged" 480 turns without one hit), and its run of failed siege turns.
static bool vt_siege_bad[256];
static int vt_siege_fail[256];
// edit_vtspawn.py: the last round this champion sieged. 00contest: an enemy killed the big group beside our spawn at r403 and every one of
// our champions was handed its capture (rally to it, 24-29 deaths, two lost games); only the siegers take it now.
static int vt_siege_last = -1000;

// edit_vtspawn.py: the camp group all of whose members are within P_SIEGE_R of our spawn tiles (static geometry, found once), when it
// still holds a reward, is not respawning and has not proved unreachable from the spawn; -1 otherwise.
int Bot::siege_gid() {
    static std::vector<int> cands;
    static bool found = false;
    World& W = world();
    if (!found) {
        found = true;
        const auto sp = W.my_spawn->positions();
        for (const auto& g : W.groups) {
            if (g.camps.empty() || g.dps <= 0 || g.gems < P_SIEGE_MIN_GEMS) continue;
            bool all = true;
            for (const auto& c : g.camps) {
                bool near = false;
                for (vec2 s : sp)
                    if (cheb(s, c.pos) <= P_SIEGE_R) { near = true; break; }
                if (!near) { all = false; break; }
            }
            if (all) cands.push_back(g.id);
        }
    }
    for (int gid : cands) {
        const Group& g = W.groups[static_cast<std::size_t>(gid)];
        if (g.state != GState::Respawning && !(gid >= 0 && gid < 256 && vt_siege_bad[gid])) return gid;
    }
    return -1;
}

// edit_vtspawn.py: hit the siege group's live monster with the least health in my reach (damage / stun spells first, no dash).
bool Bot::siege_attack(Group& g) {
    auto& me = self();
    const vec2 p = me.position();
    const int range = std::max(1, me.attack_range());
    const bitboard* vis = world().vis ? &*world().vis : nullptr;
    const Camp* best = nullptr;
    for (const auto& c : g.camps) {
        if (c.hp <= 0 || cheb(p, c.pos) > range || (vis && !bb_test(*vis, c.pos))) continue;
        if (!best || c.hp < best->hp) best = &c;
    }
    if (!best || !me.can_attack()) return false;
    try {
        const camp cc = vision::camp_at(best->pos);
        try_cast_on_camp(cc, false);
        me.attack(cc);
        attacked_this_turn = true;
        return true;
    } catch (...) {}
    return false;
}

// edit_vtspawn.py: on my spawn and hurt (this turn's end heals me): hit what is in reach without leaving the tile.
void Bot::spawn_hit() {
    auto& me = self();
    const vec2 p = me.position();
    const int range = std::max(1, me.attack_range());
    const Seen* best = nullptr;
    for (const auto& e : enemies)
        if (cheb(e.pos, p) <= range && (!best || e.hp < best->hp)) best = &e;
    if (best) {
        if (!cast_this_turn) {
            auto abs = me.abilities();
            for (int s = 0; s < 2 && !cast_this_turn; ++s) {
                if (!ahas[s] || (aexcl[s] && moved_this_turn)) continue;
                const auto k = akind[s];
                if (k != ability_kind::damage && k != ability_kind::cc && k != ability_kind::aoe_damage) continue;
                if (cheb(p, best->pos) > static_cast<int>(arange[s])) continue;
                try {
                    if (abs[s].cooldown() > 0) continue;
                    if (k == ability_kind::aoe_damage ? abs[s].use(best->pos) : abs[s].use(best->c)) cast_this_turn = true;
                } catch (...) {}
            }
        }
        if (me.can_attack()) {
            try { me.attack(best->c); attacked_this_turn = true; act = "spawn_hit"; } catch (...) {}
        }
        return;
    }
    if (!P_SPAWN_SIEGE) return;
    const int gid = siege_gid();
    if (gid < 0) return;
    Group& g = world().groups[static_cast<std::size_t>(gid)];
    if (P_FIX_SIEGE && g.state == GState::Alive && round - g.awake_max > 1) {  // edit_vtfix1.py: spawn_siege's health check before a hit wakes it
        float inc = 0;
        for (const auto& c : g.camps)
            if (c.hp > 0) inc += camp_str(c.type);
        if (self().max_health() < P_SPAWN_SIEGE_HP * inc * camp_taken_mult(idx)) return;
    }
    if (g.state == GState::Alive && siege_attack(g)) act = "spawn_siege";
}

// edit_vtspawn.py: work the siege group from free spawn tiles in my reach; a killed group goes to the farm code for its capture.
bool Bot::spawn_siege() {
    const int gid = siege_gid();
    if (gid < 0) return false;
    World& W = world();
    auto& me = self();
    Group& g = W.groups[static_cast<std::size_t>(gid)];
    if (g.state == GState::Reward) {
        if (round - vt_siege_last <= P_SIEGE_KEEP && task != gid) { task = gid; task_since = round; gather_since = -1; }
        return false;
    }
    if (g.state != GState::Alive) return false;
    float inc = 0;
    for (const auto& c : g.camps)
        if (c.hp > 0) inc += camp_str(c.type);
    if (me.max_health() < P_SPAWN_SIEGE_HP * inc * camp_taken_mult(idx)) return false;
    const vec2 p = me.position();
    const int range = std::max(1, me.attack_range());
    if (P_FIX_SIEGE) {  // edit_vtfix1.py: not from across the map, not off farm()'s lock (a capture or fight of my task)
        if (W.spawn_dist_at(p) > P_SIEGE_NEAR) return false;
        if (task != gid && task >= 0 && task < static_cast<int>(W.groups.size())) {
            const Group& t = W.groups[static_cast<std::size_t>(task)];
            if (t.state == GState::Reward && bb_test(*t.tiles, p)) return false;
            if (t.state == GState::Alive)
                for (const auto& c : t.camps)
                    if (c.hp > 0 && round - c.awake_round <= 1 && cheb(c.pos, p) <= 5) return false;
        }
    }
    bitboard goals;
    goals.clear();
    int slots = 0;
    for (vec2 s : W.my_spawn->positions()) {
        bool reach = false;
        for (const auto& c : g.camps)
            if (c.hp > 0 && cheb(s, c.pos) <= range) { reach = true; break; }
        if (!reach) continue;
        ++slots;
        bool taken = false;
        for (const auto& a : allies)
            if (a.pos == s) taken = true;
        if (taken && s != p) continue;
        goals.set(s);
    }
    if (goals.is_empty()) return false;
    if (P_FIX_SIEGE && !bb_test(goals, p)) {  // edit_vtfix1.py: mates out of sight hold the tiles too (their task slots)
        int n = 0;
        for (int a = 0; a < 5; ++a)
            if (a != idx && comms.task_of(a) == gid) ++n;
        if (n >= slots) return false;
    }
    act = "siege";
    vt_siege_last = round;
    if (!bb_test(goals, p)) move_to(goals, P_FIX_SIEGE ? W.f_spawn.get() : nullptr, false);  // edit_vtfix1.py: field = fuel guard
    const bool could = me.can_attack();
    const bool hit_ok = siege_attack(g);
    if (gid < 256) {
        if (hit_ok) vt_siege_fail[gid] = 0;
        else if (could && bb_test(goals, me.position()) && ++vt_siege_fail[gid] >= 3) vt_siege_bad[gid] = true;  // no hit lands from here
    }
    if (task != gid) { task = gid; task_since = round; gather_since = -1; }
    comms.write_task(idx, gid, true);
    return true;
}

bool Bot::try_cast_on_camp(const camp& c, bool tanking) {
    auto& me = self();
    if (cast_this_turn) return false;
    const vec2 p = me.position();
    const vec2 cp = c.position();
    auto abs = me.abilities();
    if (tanking && camp_str(c.kind()) > 0) {
        const int sh0 = ability_slot(ability_kind::shield);
        if (sh0 >= 0) {
            try { if (abs[sh0].cooldown() == 0 && abs[sh0].use(me)) { cast_this_turn = true; return true; } } catch (...) {}
        }
        const int ds = ability_slot(ability_kind::dash);
        if (ds >= 0 && amod[static_cast<std::size_t>(ds)] > 0 && !moved_this_turn) {
            try {
                if (abs[ds].cooldown() == 0) {
                    vec2 bestq = p;
                    int bd = 99;
                    for (int dx = -2; dx <= 2; ++dx)
                        for (int dy = -2; dy <= 2; ++dy) {
                            const vec2 q{ p.x + dx, p.y + dy };
                            if (q == p || !nav.passable(q) || cheb(q, cp) > 1) continue;
                            const int dd = cheb(q, p);
                            if (dd < bd) { bd = dd; bestq = q; }
                        }
                    if (bestq != p && abs[ds].use(bestq)) { cast_this_turn = true; nav.begin_turn(); return true; }
                }
            } catch (...) {}
        }
    }
    for (int s = 0; s < 2; ++s) {
        if (!ahas[s]) continue;
        if (aexcl[s] && moved_this_turn) continue;
        const auto k = akind[s];
        const bool offensive = k == ability_kind::damage || k == ability_kind::aoe_damage || (k == ability_kind::cc && amod[s] > 0);
        if (!offensive || cheb(p, cp) > static_cast<int>(arange[s])) continue;
        try {
            if (abs[s].cooldown() > 0) continue;
            const bool ok = k == ability_kind::aoe_damage ? abs[s].use(cp) : abs[s].use(c);
            if (ok) { cast_this_turn = true; return true; }
        } catch (...) {}
    }
    // Self shield while tanking camps.
    const int sh = ability_slot(ability_kind::shield);
    if (sh >= 0 && hurt && me.health() < me.max_health() * 0.9f) {
        try {
            if (abs[sh].cooldown() == 0 && abs[sh].use(me)) { cast_this_turn = true; return true; }
        } catch (...) {}
    }
    return false;
}

// edit_vtfuel2.py: spare fuel of the set-up turn: sight boards of the camps of the groups nearest to the spawn (the order the first
// farm turns need them), then group fields. Sight boards are pure caches; earlier fields only give earlier exact distances.
// True when the boards of the P_WARM_GROUPS nearest groups are all built.
bool Bot::warm_up() {
    World& W = world();
    auto& me = self();
    if (fuel() < P_WARM_RESERVE + 20000 + W.groups.size() * 120) return false;  // the ordering below costs ~100 a group
    const int range = me.attack_range();
    std::vector<int> order;
    order.reserve(W.groups.size());
    for (const auto& g : W.groups)
        if (g.reachable && g.state == GState::Alive) order.push_back(g.id);
    std::sort(order.begin(), order.end(), [&W](int a, int b) {
        const int da = W.groups[static_cast<std::size_t>(a)].spawn_dist, db = W.groups[static_cast<std::size_t>(b)].spawn_dist;
        return da != db ? da < db : a < b;
    });
    const std::uint64_t per = static_cast<std::uint64_t>(W.w) * static_cast<std::uint64_t>(W.h) / 3 + 1500;  // one board (~0.5k-2.9k)
    bool done = true, out = false;
    for (std::size_t k = 0; k < order.size() && !out; ++k) {
        for (auto& c : W.groups[static_cast<std::size_t>(order[k])].camps) {
            if (c.los) continue;
            if (fuel() < P_WARM_RESERVE + 20000 + per) {  // keep room for fields of the nearest groups too
                done = k >= static_cast<std::size_t>(P_WARM_GROUPS);
                out = true;
                break;
            }
            W.attack_spots(c, range);
        }
    }
    if (fuel() > P_WARM_RESERVE + 4000) W.precompute(P_WARM_RESERVE, me.position());
    return done;
}

void Bot::play_turn() {
    auto& me = self();
    if (!inited) {
        init();
        if (!inited) return;  // edit_vtfuel2.py: set-up still running (fuel)
        if (fuel() < (P_FIRST_ADAPT ? vt_first_need() : 120000)) {  // big maps: finish setup, act next turn (edit_vtfuel3.py: G5)
            // edit_vtfuel2.py: the turn's spare fuel warms caches; when it could not warm the nearest groups' sight boards, one
            // more turn does before the first (heavy) farm turn - a first turn that runs out loses the next round anyway
            vt_warm_more = !warm_up();
            return;
        }
    } else if (vt_warm_more) {
        vt_warm_more = false;
        warm_up();
        return;
    }
    World& W = world();
    round = static_cast<int>(round_number());
    if (kReportRound > 0 && round == kReportRound) {  // edit_vtreport.py
        unsigned carried = 0;
        for (auto& c : ally_handles()) { try { if (c.is_alive()) carried += c.gem_count(); } catch (...) {} }
        std::printf("REPORT %d %u %u %u\n", round, global_submitted_gems(team::ally), global_submitted_gems(team::enemy), carried);
    }
    nav.begin_turn();
    if (attacked_this_turn) last_attack_round = round - 1;
    cast_this_turn = false;
    moved_this_turn = false;
    attacked_this_turn = false;
    crystal_cache = -1;
    lock_cache = -1;
    lock_tried = false;
    act = "";
    comms.read();
    const int ev = comms.poll_capture(round);
    if (ev >= 0 && ev < static_cast<int>(W.groups.size())) W.mark_captured(ev, round);

    if (me.gem_count() == 0) tribute_until = -1;
    if (!me.is_alive()) {
        tribute_until = -1;
        shop();
        comms.write_raw(idx, slot::kDead, false);
        task = -1;
        gather_since = -1;
        last_hp = 0;
        return;
    }
    const vec2 p = me.position();
    const float hp = me.health();
    hurt = hp < last_hp - 0.5f;
    last_hp = hp;
    W.observe(round, p);

    // Detect our own capture: rewards arrived while standing on a group tile.
    const unsigned gems = me.gem_count(), gold = me.gold_count();
    const int on_group = W.group_at(p);
    if ((gems > last_gems || gold > last_gold) && (on_group >= 0 || last_on_group >= 0)) {
        const int gid = on_group >= 0 ? on_group : last_on_group;
        if (W.groups[static_cast<std::size_t>(gid)].state != GState::Alive) {
            W.mark_captured(gid, round);
            comms.post_capture(gid, round);
            if (task == gid) task = -1;
            if (gid == opening_gid && !vt_elk) opening_done = true;  // edit_vtelk.py: the chain moves on in farm()
        }
    }
    last_gems = gems;
    last_gold = gold;
    if (on_group < 0 || on_group != last_on_group) on_tile_since = on_group >= 0 ? round : -1;
    last_on_group = on_group;
    update_rally();

    if (me.is_teleporting()) return;
    bool recalling = me.is_recalling();  // edit_vtrecall.py: may drop last turn's pre-start below
    const bool submitting = me.is_submitting_gems();
    see_units();
    if (P_RECALL_PRIME && rp_primed) {  // edit_vtrecall.py
        rp_primed = false;
        if (recalling && !rp_keep(p, hp / std::max(1.f, me.max_health()))) {
            try { me.cancel_recall(); recalling = false; } catch (...) {}
        }
    }
    set_turn_priority();
    if (P_WARDS) place_ward();
    if (P_HURT_AWAKE && hurt) {
        // Hit with no enemy champion around: camps I cannot see (behind bushes) are awake and hitting me.
        bool champ_near = false;
        for (const auto& e : enemies)
            if (cheb(e.pos, p) <= e.range + 2) champ_near = true;
        if (!champ_near) {
            const bitboard* vis = W.vis ? &*W.vis : nullptr;
            for (auto& g : W.groups) {
                if (g.state != GState::Alive || g.dps <= 0 || cheb(g.center, p) > g.radius + 6) continue;
                for (auto& c : g.camps)
                    if (c.hp > 0 && camp_str(c.type) > 0 && cheb(c.pos, p) <= camp_range(c.type) && (!vis || !bb_test(*vis, c.pos))) { c.awake_round = round; g.awake_max = std::max(g.awake_max, round); }  // edit_vtfuel.py
            }
        }
    }
    if (recalling || submitting) {
        // Keep channelling unless enemies are about to catch us in it. A short tribute is worth finishing
        // under fire (gems are lost on death anyway); restarting it every round would never complete.
        int closest = 99;
        float incoming = 0, burst = 0;  // what the enemies around can deal before the channel ends
        const int left = std::max(1, submit_end - round);
        for (const auto& e : enemies) {
            const int d = cheb(e.pos, p);
            closest = std::min(closest, d);
            if (d <= e.range + left) incoming += champ_dps_est(e.type, e.str, e.foc);
            if (d <= 4 + left) burst = std::max(burst, champ_burst_est(e.type, e.str, e.foc));
        }
        bool abort = closest <= 2 || (closest <= 4 && hurt);
        // Damage does not interrupt a tribute (only stuns do): bank the gems if we outlive the channel.
        if (submitting && abort && hp > 1.3f * (incoming * static_cast<float>(left) + burst) + 40.f) abort = false;
        if (!abort) {
            comms.write_raw(idx, recalling ? slot::kHome : slot::kTribute, false);
            return;
        }
        try {
            if (recalling) me.cancel_recall();
            else me.cancel_submit_gems();
        } catch (...) {}
    }

    const bool at_spawn = bb_test(*W.my_spawn, p);
    if (p != still_pos) { still_pos = p; still_since = round; }
    if (P_TRAP_RECALL && !at_spawn && !hurt && round - still_since >= 6 && round - last_attack_round >= 6 && round - trap_check >= 5) {
        // Trapped: camps respawned around me (a ring of camps around an altar) and no way home is left on foot.
        // Standing there idle for the rest of the game (and burning fuel on failed path searches): recall.
        trap_check = round;
        int closest = 99;
        for (const auto& e : enemies) closest = std::min(closest, cheb(e.pos, p));
        if (closest > 3) {
            bitboard walls = *W.fwalls | vision::camp_tiles();  // a dasher crosses bridges
            walls.set(p, false);
            bitboard roots = *W.my_spawn & ~walls;
            bitboard dest, vis;
            dest.clear();
            dest.set(p);
            distance_field f;
            f.compute_to(walls, roots, dest, vis);
            if (!roots.is_empty() && !f.next_move_from(p)) {
                try {
                    me.recall();
                    act = "trap_recall";
                    LOGC("%d %d trap_recall %d,%d\n", round, idx, p.x, p.y);
                    comms.write_raw(idx, slot::kHome, false);
                    return;
                } catch (...) {}
            }
        }
    }
    if (at_spawn || hp >= 0.9f * me.max_health()) heading_home = false;
    if (at_spawn) shop();
    // edit_vtfix1.py: began my last turn on the spawn and still here, so that turn's end healed me; the loss since is this round's hits
    const bool vt_healed = P_FIX_PIN && at_spawn && vt_spawn_round == round - 1 && hp >= P_PIN_HP * me.max_health();
    if (at_spawn) vt_spawn_round = round;
    if (at_spawn && hp < me.max_health() * 0.98f && !vt_healed) {
        if (P_SPAWN_HIT) spawn_hit();  // edit_vtspawn.py
        comms.write_raw(idx, slot::kHome, false);
        return;  // heal fully first
    }

    std::erase_if(sightings, [&](const Sighting& x) { return round - x.round > 15; });
    build_threat(p, task);
    try_support();
    pro_shield();
    // Under pressure with a gem stack: bank it if an altar is close, before fighting.
    if (!enemies.empty() && me.gem_count() >= 15 && W.altar_dist_at(p) <= 4) {
        int closest = 99;
        for (const auto& e : enemies) closest = std::min(closest, cheb(e.pos, p));
        bool bank = closest >= 3;
        if (bank && P_BANK_SAFE) {
            // Walk plus channel under their fire: only if I outlive it (gems are theirs if I die there).
            const int walk = W.altar_dist_at(p);
            const int chan = static_cast<int>(std::ceil(static_cast<float>(me.gem_count()) * static_cast<float>(constants::submit_gem_duration_multiplier))) +
                             static_cast<int>(constants::submit_gem_base_duration);
            float incoming = 0;
            for (const auto& e : enemies) {
                const int d = cheb(e.pos, p);
                const int arrive = std::max(0, d - std::max(1, e.range) - 1);
                const int exposed = std::max(0, walk + chan - arrive);
                if (exposed > 0) incoming += champ_dps_est(e.type, e.str, e.foc) * static_cast<float>(exposed) + champ_burst_est(e.type, e.str, e.foc);
            }
            if (incoming > P_BANK_SAFE_F * me.health()) bank = false;
        }
        LOGC("%d %d BANK? %d cl%d\n", round, idx, (int)bank, closest);
        if (bank) {
            act = "bank";
            tribute();
            comms.write_raw(idx, slot::kTribute, false);
            return;
        }
    }
    if (combat()) {
        const std::string_view fa(act);
        comms.write_raw(idx, (P_RETREAT_CODE && (fa == "retreat" || fa == "retreat_hit" || fa == "esc_recall")) ? slot::kRetreat : slot::kFight, false);
        if (fuel() >= P_LOG_MIN_FUEL) {  // edit_vtfuel.py: a log line must not cost the next turn
            const vec2 q = me.position();
            LOGC("%d %d F:%s %d,%d>%d,%d %.0f\n", round, idx, act, p.x, p.y, q.x, q.y, me.health());
        }
        return;
    }

    if (P_YIELD) yield_path();
    const float frac = hp / std::max(1.f, me.max_health());
    // Health to walk out of the reach of awake camps around me (they keep hitting on the way out).
    float escape_need = 0;
    {
        int worst = 0;
        float dps = 0, relief_need = 0;
        for (auto& g : W.groups) {
            if (g.state != GState::Alive || g.dps <= 0 || cheb(g.center, p) > g.radius + 6) continue;
            for (const auto& c : g.camps) {
                if (c.hp <= 0 || camp_str(c.type) <= 0 || round - c.awake_round > 2) continue;
                const int d = cheb(c.pos, p), r = camp_range(c.type);
                if (d > r) continue;
                if (P_ESCNEED_TARGET) {
                    // Camps hit the nearest champion (ties: lowest id): an ally in front keeps this one off me.
                    bool shielded = false;
                    for (const auto& a : allies) {
                        const int da = cheb(c.pos, a.pos);
                        if (da < d || (da == d && a.index < idx)) { shielded = true; break; }
                    }
                    if (shielded) continue;
                }
                dps += camp_str(c.type);
                worst = std::max(worst, r + 1 - d);
                int rounds = r + 1 - d;  // steps back until out of its reach
                if (P_ESC_RELIEF) {
                    // A healthy ally close behind takes this camp over once I am farther than it.
                    for (const auto& a : allies) {
                        if (a.hp < P_ESC_RELIEF_HP * a.max_hp) continue;
                        const int ca = comms.code_of(a.index);
                        if (ca == slot::kHome || ca == slot::kDead || ca == slot::kRetreat || ca == slot::kTribute) continue;
                        const int da = cheb(c.pos, a.pos);
                        if (da > r) continue;
                        rounds = std::min(rounds, std::max(1, da - d + 1));
                    }
                }
                relief_need += camp_str(c.type) * static_cast<float>(rounds);
            }
        }
        escape_need = P_ESC_RELIEF ? (relief_need + dps) * camp_taken_mult(idx) : dps * camp_taken_mult(idx) * static_cast<float>(worst + 1);
    }
    // Nearly dead group in my hands: finish it rather than walk home and back (the last 3% of a golem took
    // a whole healing trip), unless its next hits would put me down.
    bool finishing = false;
    if (P_FINISH > 0.f && task >= 0 && task < static_cast<int>(W.groups.size())) {
        const Group& g = W.groups[static_cast<std::size_t>(task)];
        if (g.state == GState::Alive && cheb(g.center, p) <= g.radius + 4) {
            float dps = camp_dps_of(idx);
            for (const auto& a : allies)
                if (comms.task_of(a.index) == g.id && cheb(a.pos, g.center) <= g.radius + 4) dps += camp_dps_of(a.index);
            const float left = g.hp_left();
            const float hits = g.live_dps() * camp_taken_mult(idx) * (left / std::max(1.f, dps) + 2.f);
            finishing = left <= P_FINISH * dps && hp > hits + 50.f;
        }
    }
    // Once on the way to heal, keep going (stepping out of reach is not being healed: no flip-flopping).
    // Enemy nukers about: keep enough health to survive their opening burst (Marcella's 2x-focus nuke reaches 4 tiles).
    if (round - burst_seen_round > 60) burst_seen = 0;
    for (const auto& e : enemies) {
        const float b = champ_burst_est(e.type, e.str, e.foc);
        if (b >= 0.8f * burst_seen) { burst_seen = std::max(burst_seen, b); burst_seen_round = round; }
    }
    const bool burst_low = P_BURST_HEAL > 0.f && round - burst_seen_round <= 40 && recent_enemy() && hp < P_BURST_HEAL * burst_seen &&
                           hp < P_BURST_HEAL_FULL * me.max_health();  // full health cannot heal further: no waiting at spawn
    const bool low = !finishing && (frac < P_HOME_HP || (frac < P_HOME_HP_ENEMY && recent_enemy()) || hp < 1.2f * escape_need || heading_home || burst_low);
    const bool under_camps = escape_need > 0;  // standing in reach of awake camps: an altar nearby is no reason to stay
    int adist = 999;
    if (low && me.gem_count() > 0) {
        if (W.gated) {
            if (W.open_gate(p, adist) < 0) adist = 999;
        } else {
            W.best_altar(p, threat ? &*threat : nullptr, adist);
        }
    }
    if (low && !(adist <= 3 && enemies.empty() && !under_camps) && task >= 0 && frac >= 0.12f && retire_near(W.groups[static_cast<std::size_t>(task)])) {
        comms.write_task(idx, task, false);
    } else if (low && !(adist <= 3 && enemies.empty() && !under_camps)) {
        act = "heal";
        heading_home = true;
        build_threat(p, -1);  // leaving my group too: avoid its reach on the way
        go_home();
        if (P_FIX_PIN && P_SPAWN_HIT && at_spawn) spawn_hit();  // edit_vtfix1.py: healed at every turn end here; hit what is in reach
        comms.write_raw(idx, slot::kHome, false);
        task = -1;
    } else if (should_tribute(frac)) {
        act = "tribute";
        tribute();
        comms.write_raw(idx, slot::kTribute, false);
    } else if (!at_spawn && ((me.gold_count() >= P_SHOP_GOLD) || (me.gold_count() >= P_SHOP_GOLD_HURT && frac < 0.6f))) {
        act = "shoptrip";
        go_home();
        comms.write_raw(idx, slot::kHome, false);
        task = -1;
    } else {
        if (!(P_SPAWN_SIEGE && spawn_siege())) farm();  // edit_vtspawn.py
    }
    if (P_WATCHDOG > 0) {
        // Stuck watchdog: standing still without attacking while supposedly busy (blocked paths, unseen camps,
        // give-up loops): drop the task for a while and let the planner pick another.
        const std::string_view a(act);
        const bool waiting = a == "capture" || a == "gather" || a == "wait_tank" || a == "wait_respawn" || a == "retire" ||
                             a == "rally_gather" || a == "tribute" || a == "bank" || a == "unlock" || a == "gate";
        const bool still = me.position() == p && !attacked_this_turn && !bb_test(*W.my_spawn, p) && !waiting && !me.is_recalling() && !me.is_submitting_gems();
        still_rounds = still ? still_rounds + 1 : 0;
        if (still_rounds >= P_WATCHDOG) {
            still_rounds = 0;
            // Stuck on the way home (blocked path): recall instead.
            if ((a == "heal" || a == "shoptrip" || a == "idle_heal" || a == "idle") && enemies.empty() && !me.is_recalling()) {
                try { me.recall(); } catch (...) {}
            }
            if (task >= 0 && task < static_cast<int>(W.groups.size())) blacklist[static_cast<std::size_t>(task)] = round + 40;
            task = -1;
            gather_since = -1;
            heading_home = false;
        }
    }
    if (round > 2 && fuel() > P_PRE_RESERVE + 12000) W.precompute(P_PRE_RESERVE, me.position());  // edit_vtfuel3.py (was 60k / 45k)
    if (P_RECALL_PRIME) rp_prime(me.position(), W.group_at(me.position()));  // edit_vtrecall.py
    if (fuel() >= P_LOG_MIN_FUEL) {  // edit_vtfuel.py: one position read (same text); no log line that would cost the next turn
        const vec2 q = me.position();
        LOGC("%d %d %s%s %d,%d>%d,%d %.0f g%u t%d e%zu\n", round, idx, act, attacked_this_turn ? "+A" : "", p.x, p.y, q.x, q.y, me.health(), me.gem_count(), task, enemies.size());
    }
    LOG("[r%d %s] %s%s pos=(%d,%d)->(%d,%d) hp=%.0f/%.0f gold=%u gems=%u task=%d st=%d fuel=%llu en=%zu\n", round, to_string(ctype).c_str(), act, attacked_this_turn ? "+A" : (me.position() != p ? "+M" : "+I"), p.x, p.y, me.position().x, me.position().y,
        me.health(), me.max_health(), me.gold_count(), me.gem_count(), task, task >= 0 ? (int)W.groups[static_cast<std::size_t>(task)].state : -1, (unsigned long long)fuel(), enemies.size());
}
