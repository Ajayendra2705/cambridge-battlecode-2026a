// Part of bot.cpp: Banking statistics, per-champion turn state, death context log.
// Unity build: bot.cpp includes this inside its anonymous namespace; not a standalone header.

// Banking as an order-quantity problem. A trip costs c * tau gems of collection (c = our gems collected per
// round alive, tau = rounds to walk to the altar, tribute and walk back); carried gems are lost at hazard h per
// round (deaths, plus the game ending), and a champion kill also hands them to the enemy (loss counted twice).
// Banking every L rounds costs c * tau / L + m * h * c * L / 2 per round, minimal at g* = sqrt(2 c tau / (m h)).
// Rates are measured this game, starting from platform averages: 0.15 gems and 1/600 deaths per round alive.
// A death hands the bag to the enemy when a champion kills us (85% of platform deaths at every bag size, top-10
// and our ranked games), so the loss counts 1 + P(champion kill) times; that share is measured per game too.
int prev_gems = 0, collected = 0, alive_rounds = 0, my_deaths = 0, kill_deaths = 0;
// Our tributes this game: one altar trip carries several captures, so a group is charged only its share of a trip.
int trib_n = 0, trib_gems = 0;
double bank_share(const Group& g) {
    if (g.gems <= 0) return 0.0;  // Gold-only groups never need an altar.
    const double avg = (trib_gems + 24.0 * 2) / (trib_n + 2);  // Prior: the top-10 median tribute, 24 gems.
    return std::min(1.0, g.gems / avg);
}

// ---- Per-champion turn state ----
int current_target = -1;
bool was_alive = true;
std::vector<int> death_rounds;  // Rounds this champion died: repeated deaths mean the enemy controls the middle.
bool retreating = false;
int hold_since = -1, hold_group = -1;  // First round on a tile of the capture we hold, and its group.
float last_hp = 0;
int last_round = -10, enemy_seen_round = -100;
int last_pick_round = -100, last_pick_state = -2;
int big_wait = 0;
int big_wait_group = -1;  // The group big_wait counts for: the wait runs once per group life.
int bank_best = UNREACH, bank_stall = 0, bank_blocked_until = 0;
int planned_team = 1;
int alive_cache = 1, alive_round = -10;

// What this champion last saw, printed if it dies before its next turn: when it acted, its health and
// activity, then visible enemies (type, distance, health) and the strength of awake camps in reach.
// Only raw values are stored each turn; formatting costs fuel and happens on death.
struct DeathCtx {
    int round = 0, n = 0;
    float hp = 0;
    const char* act = "";
    std::array<cambc::champion_type, 4> type{};
    std::array<int, 4> d{};
    std::array<float, 4> ehp{};
} death_ctx;

void record_death_ctx() {
    death_ctx.round = S.round;
    death_ctx.hp = S.hp;
    death_ctx.act = last_activity;
    death_ctx.n = 0;
    for (const auto& e : S.enemies) {
        if (death_ctx.n == 4) break;
        const int i = death_ctx.n++;
        death_ctx.type[i] = e.type;
        death_ctx.d[i] = dist(S.me, e.pos);
        death_ctx.ehp[i] = e.hp;
    }
}

void print_death(int round) {
    std::cout << "D" << round << " s" << W.slot << " r" << death_ctx.round << " hp=" << death_ctx.hp << " " << death_ctx.act
              << " en:";
    for (int i = 0; i < death_ctx.n; ++i)
        std::cout << " " << cambc::to_string(death_ctx.type[i]) << "@" << death_ctx.d[i] << "/" << death_ctx.ehp[i];
    std::cout << '\n';
}

int alive_allies() {
    if (alive_round == S.round) return alive_cache;
    int n = 0;
    for (const auto& a : cambc::champions(team::ally))
        if (a.is_alive()) ++n;
    alive_cache = std::max(1, n);
    alive_round = S.round;
    return alive_cache;
}
