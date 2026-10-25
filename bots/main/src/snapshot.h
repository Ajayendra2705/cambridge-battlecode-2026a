// Part of bot.cpp: Per-turn snapshot types (camps, champions in view) and champion damage estimates from ability metadata.
// Unity build: bot.cpp includes this inside its anonymous namespace; not a standalone header.

// ---- Per-turn snapshot ----
struct CampSnap {
    cambc::camp camp;
    vec2 pos;
    float hp, max_hp, str;
    int group;
    int range;
    bool awake;
};

struct ChampSnap {
    cambc::champion ch;
    vec2 pos;
    float hp, max_hp, str;
    int range;
    std::uint32_t gems;
    float dps = 0;
    float burst = 0;   // Damage it can deal in one round with every spell ready.
    int reach = 1;     // Distance from which that burst lands after one step.
    cambc::champion_type type{};
};

// Fight coefficients read from a champion's ability metadata (engine values, so balance patches need no edits):
// the best single focus multiplier one cast deals (damage, area, damaging stun or landing dash), its range,
// the focus multipliers per round averaged over cooldowns, and attack resets per round.
struct FightCoef { bool ready = false; float cast = 0, per_round = 0, resets = 0; int spell_range = 0; bool dash = false; };

FightCoef read_coef(const cambc::champion& c) {
    FightCoef f;
    for (const auto& ab : c.abilities()) {
        if (!ab.info()) continue;
        std::visit([&](const auto& a) {
            using T = std::decay_t<decltype(a)>;
            const float cd = static_cast<float>(std::max(1, a.max_cooldown));
            if constexpr (std::is_same_v<T, cambc::ability_attack_reset>) f.resets += 1.0f / cd;
            if constexpr (std::is_same_v<T, cambc::ability_dash>) f.dash = true;
            if constexpr (!std::is_same_v<T, cambc::ability_shield> && !std::is_same_v<T, cambc::ability_heal>
                          && requires { a.modifier; }) {
                if (a.modifier > 0) {
                    f.per_round += a.modifier / cd;
                    f.cast = std::max(f.cast, a.modifier);
                    if constexpr (!std::is_same_v<T, cambc::ability_dash>) f.spell_range = std::max(f.spell_range, static_cast<int>(a.range));
                }
            }
        }, *ab.info());
    }
    f.ready = true;
    return f;
}

// Heart of Ruin deals up to +50% damage as its health drops.
float damage_scale(cambc::champion_type t, float hp, float max_hp) {
    if (t != cambc::champion_type::heart_of_ruin || max_hp <= 0) return 1.0f;
    return 1.0f + cambc::constants::passive_abilities::heart_of_ruin_missing_health_damage_max_bonus * (1.0f - hp / max_hp);
}

// One-round damage: a basic attack plus the best single cast (one cast per turn: an attack reset or a spell).
float champion_burst(const FightCoef& f, float str, float focus) {
    return str + std::max(f.resets > 0 ? str : 0.0f, f.cast * focus);
}

// Sustained damage per round: basic attacks and resets plus every damaging cast averaged over its cooldown.
float champion_dps(const FightCoef& f, float str, float focus) { return str * (1.0f + f.resets) + f.per_round * focus; }

struct Snap {
    int round = 0;
    vec2 me;
    float hp = 0, max_hp = 0, str = 0;
    int range = 1;
    bitboard visible, occ;        // occ: visible champions, camps and teleports, excluding us.
    std::vector<CampSnap> camps;  // Live visible camps.
    std::vector<CampSnap> phantoms;  // Unseen live camps of recently awake groups: they still hit.
    std::vector<ChampSnap> allies, enemies;
    // Tiles where a visible enemy could hit us hard on its next turn, and whether moves should avoid them.
    std::vector<std::pair<vec2, int>> danger;
    bool avoid_danger = false;
    // This turn so far: the engine's action flags at the snapshot (champion_state bits), whether we walked (rooting
    // spells cannot follow a walk) and whether our basic attack was spent (a reset needs a spent attack).
    std::uint32_t state = 0;
    bool walked = false, attacked = false;
    bool view_moved = false;  // We moved or dashed since `occ` was read (see refresh_occ).
    vec2 start;  // Our tile at the snapshot.
    // Stunned: the turn starts with no action allowed at all.
    bool can_act() const { return (state & ((1u << 3) | (1u << 4) | (1u << 11))) != 0; }
};

Snap S;
// Our own move or dash changes what we see, and the engine knows every unit that came into view: a later move or
// landing onto one throws ("Known occupied destination": 56 per 80 games in the au11 audit, each next to a tile just
// reached, on a tile out of view at the snapshot). Read the occupancy again before the next move or landing.
void moved_to(vec2 t) {
    S.me = t;
    S.view_moved = true;
}
void refresh_occ() {
    if (!S.view_moved) return;
    S.view_moved = false;
    S.occ |= cv::teleport_tiles() | cv::champion_tiles() | cv::camp_tiles();
    S.occ.set(S.me, false);
}
// The view at the snapshot as packed row-major bits, least significant first (take_snapshot exports it in one host
// call): in_view() answers without the host call of bitboard::is_set. Stamping a per-tile round from the view's
// positions cost about 10k fuel a turn on big_world (pf9 probe); the export costs about 600 and gave the same answer
// for every visible tile (pf10 check, 378 turns).
std::vector<std::uint8_t> view_bits;  // Padded to whole 64-bit words; the padding stays zero.
int view_row_lo = 0, view_row_hi = -1;  // Rows of the first and last tile in view (none: lo > hi).
bool in_view(vec2 p) {
    if (view_bits.empty()) return false;
    const int i = p.y * cm::width() + p.x;
    return (view_bits[i >> 3] >> (i & 7)) & 1;
}
// This turn's visible camp health per known camp (0 when not seen alive) and whether a group has a live camp in view.
std::vector<float> camp_hp_now;
std::vector<char> group_live_now;
// Online combat calibration: actual / predicted champion damage taken this game, relative to the 0.18 seen in
// local play (Bayesian prior worth 3000.0 predicted damage). Above 1 the opponent hits harder than usual.
double cal_pred = 0, cal_act = 0;
float cal_f = 1.0f;

bool fragile = false;  // Cassi or Issac: losing either loses both.

bool in_danger(vec2 t) {
    for (const auto& [src, radius] : S.danger)
        if (static_cast<int>(t.chebyshev_distance(src)) <= radius) return true;
    return false;
}
// The danger tiles as one board, for routing around them.
bitboard danger_tiles() {
    bitboard b;
    b.clear();
    for (const auto& [src, radius] : S.danger) b.draw_chebyshev(src, static_cast<float>(radius));
    return b;
}

// A turn that runs out of fuel resumes next round from the same point, with this snapshot. Teammates have moved since:
// the bf5 audit traced every "Known occupied destination" (127 per 80 games) to such a resumed turn moving onto a tile
// a teammate had stepped on, and its stale attacks ("out of range", "An available attack cannot be reset"). Every
// action helper refuses to act once the round has changed; the next turn starts with a fresh snapshot.
// A turn that runs out of fuel resumes next round from the same point, on the old snapshot, and an action then was
// refused (au14 audit: 5 of the 9 caught errors per 80 games came after such a split: a dash onto a tile taken since,
// a reset of the new round's attack, a read of an enemy that had left our view). Also stale with under 1000 fuel left,
// so a check right before an action leaves room for the call itself.
bool stale() { return static_cast<int>(cambc::round_number()) != S.round || cambc::fuel_remaining() < 1000; }
float cached_dps = 0, cached_spell_dps = 0;
int cached_dps_round = -100;
