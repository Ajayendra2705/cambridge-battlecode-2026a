#pragma once
#include "common.h"
#include "comms.h"
#include "nav.h"
#include "world.h"

struct BuildStep {
    item_family fam;
    item_stat stat;
    int count;
};

struct Sighting {
    vec2 pos;
    int round;
    float power;
};

struct Seen {
    champion c;
    int index;  // ally index (allies only), enemy handle index for enemies
    vec2 pos;
    float hp, max_hp, str, foc;
    int range;
    unsigned gems;
    bool channeling;
    champion_type type{};
    int seen_round = 0;
    // Ability readiness (enemy cooldowns are readable in vision): rounds until ready, 99 = no such ability.
    int dash_cd = 99, nuke_cd = 99, reset_cd = 99;
    float nuke_dmg = 0;  // damage of its ready-or-not damaging abilities (modifier x focus)
    bool dash_hits = false;
    bool cd_known = false;
    // Burst it can land `delay` rounds from now (cooldowns that will be ready by then).
    float burst_at(int round, int delay) const {
        float b = str;
        if (cd_at(reset_cd, round) <= delay) b += str;
        if (cd_at(nuke_cd, round) <= delay) b += nuke_dmg;
        return b;
    }
    // Rounds until ready as of `round` (cooldowns tick once per round).
    int cd_at(int cd, int round) const { return cd >= 99 ? 99 : std::max(0, cd - (round - seen_round)); }
    // Damage it can deal in one round now: an attack, the reset's second attack, ready damaging abilities.
    float burst_now(int round) const {
        float b = str;
        if (cd_at(reset_cd, round) == 0) b += str;
        if (cd_at(nuke_cd, round) == 0) b += nuke_dmg;
        return b;
    }
};

// Per enemy handle: ability kinds and modifiers (fixed per champion design).
struct AbilMeta {
    bool known = false;
    std::array<ability_kind, 2> kind{};
    std::array<float, 2> mod{};
    std::array<bool, 2> has{};
};

// Amortised damage per round against champions, and the one-off burst a champion can deal right now
// if its abilities are ready (fight.cpp).
float champ_dps_est(champion_type t, float str, float foc);
float champ_burst_est(champion_type t, float str, float foc);
int burst_reach(champion_type t, int range);
struct Seen;
int enemy_strike_reach(const Seen& e, int round);

struct EnemyMem {
    std::optional<Seen> s;
    int seen_round = -1000;
    vec2 prev_pos{ -1, -1 };  // the sighting before the latest one
    int prev_round = -1000;
};

// What we know about an ally (refreshed when visible).
struct AllyInfo {
    champion_type type{};
    float str = 0, foc = 0, hp = 0, max_hp = 0;
    vec2 pos{ -1, -1 };
    int seen_round = -1000;
};

class Bot {
public:
    void play_turn();

private:
    bool inited = false;
    int idx = -1;
    int n_allies = 0;
    champion_type ctype{};
    bool ranged = false;
    std::vector<BuildStep> plan;
    std::vector<int> bought;
    std::array<ability_kind, 2> akind{};
    std::array<bool, 2> ahas{};
    std::array<bool, 2> aexcl{};
    std::array<float, 2> arange{}, amod{};
    std::array<AllyInfo, 5> ainfo{};

    // farming state
    int task = -1;
    int task_since = 0;
    float task_score = 0;
    int gather_since = -1;     // round I started waiting at a heavy group's staging area
    int chip_task = -1;        // task taken solo over several healing trips
    int still_rounds = 0;
    float burst_seen = 0;     // biggest enemy burst seen recently (decays)
    int burst_seen_round = -1000;  // turns in a row without moving or attacking while supposedly busy (stuck watchdog)
    int trib_altar = -1, trib_round = -100;  // altar I am heading for (sticky choice)
    int abort_rounds = 0;      // consecutive rounds my group looked too heavy for the committed team
    int last_retreat_round = -100;  // last round I retreated from champions (hysteresis)
    vec2 still_pos{ -1, -1 };       // trapped check: where I have been standing since still_since
    int still_since = 0, trap_check = -100, last_attack_round = -100;
    int vt_spawn_round = -100;  // edit_vtfix1.py: the last round my turn began on the spawn
    bool heading_home = false; // decided to go heal: committed until healed
    float siege_hp0 = -1;      // siege target's health when the current siege was first seen
    int opening_gid = -2;      // -2 = not computed, -1 = none
    bool opening_done = false;
    // edit_vtelk.py: the team elk chain (elk maps)
    struct VtElk { int gid; float value, T; };
    std::vector<VtElk> vt_elk_list;
    bool vt_elk = false;
    int vt_elk_done = 0;
    vec2 vt_elk_ref{ -1, -1 };
    int vt_elk_r0 = -1;  // edit_vtelkfish.py: the target's respawn round when chosen while respawning
    std::vector<int> blacklist;  // group id -> round until which it is skipped
    int rally_since = -1;
    int rally_pause_until = -1;  // leader: no new rally before this round        // round the current team rally was first seen (leader bookkeeping)
    int rally_seen = -1;
    int replan_skips = 0;
    // edit_vtfuel3.py: dearest complete choose_task / escape planner measured, and the fuel the guards before them now ask for
    std::uint64_t vt_ct_cost = 0, vt_esc_cost = 0;
    bool vt_ct_broke = false;  // the last choose_task stopped at P_CT_FUEL (its cost is no full measure)
    std::uint64_t vt_replan_need() const {
        const World& WV = world();
        const std::uint64_t floor = static_cast<std::uint64_t>(WV.groups.size()) * 700 + 5000;  // before a measure (~1k a group)
        return std::min<std::uint64_t>(P_REPLAN_MIN, std::max(vt_ct_cost, floor) * 5 / 4 + P_REPLAN_REST);
    }
    std::uint64_t vt_esc_need() const {
        const World& WV = world();
        const std::uint64_t floor = static_cast<std::uint64_t>(WV.w) * static_cast<std::uint64_t>(WV.h) / 2 + 8000;
        return std::min<std::uint64_t>(P_ESC_MIN_FUEL, std::max(vt_esc_cost, floor) * 5 / 4 + P_ESC_REST);
    }
    std::array<int, 6> ally_last_task{ -1, -1, -1, -1, -1, -1 };
    std::array<int, 6> ally_last_task_round{};         // rally group id that rally_since refers to

    unsigned last_gems = 0, last_gold = 0;
    float last_hp = 0;
    int last_on_group = -1;
    int on_tile_since = -1;
    int tribute_until = -1;    // committed to tributing until this round (or the gems are in)
    int submit_end = -1;       // round my current tribute channel completes
    int round = 0;
    bool hurt = false;
    bool cast_this_turn = false;
    bool moved_this_turn = false;
    bool attacked_this_turn = false;
    const char* act = "";

    Nav nav;
    Comms comms;
    std::optional<bitboard> threat;
    std::optional<bitboard> camp_threat;  // reach of awake camps only (part of threat)
    int threat_for = -2;  // task the threat map was built for (its camps are not avoided)
    std::vector<Seen> enemies, allies;
    std::vector<EnemyMem> emem;  // last sighting per enemy champion
    std::vector<AbilMeta> emeta;  // per enemy handle
    std::array<AbilMeta, 6> ameta{};  // per ally index
    void read_cooldowns(champion& c, AbilMeta& m, Seen& s);
    std::vector<Sighting> sightings;

    // bot.cpp
    void init();
    void shop();
    void see_units();
    // edit_vtrecall.py
    bool recall_counts(champion& c, unsigned state, std::vector<std::pair<int, int>>& mem, std::size_t k);
    bool rp_keep(vec2 p, float hp_frac);
    void rp_prime(vec2 p, int on_group);
    std::vector<std::pair<int, int>> rc_enemy, rc_ally;  // per index: (round last seen recalling, rounds left then)
    bool rp_primed = false;                               // I pre-started a recall at my last turn end
    void build_threat(vec2 pos, int ignore_group);
    bool go_home();
    bool yield_path();
    bool recent_enemy() const;
    bool should_tribute(float hp_frac);
    bool tribute();
    bool move_to(const bitboard& goals, const distance_field* field, bool avoid, vec2 anchor = { -1, -1 });
    int siege_gid();                // edit_vtspawn.py
    bool siege_attack(Group& g);    // edit_vtspawn.py
    bool spawn_siege();             // edit_vtspawn.py
    void spawn_hit();               // edit_vtspawn.py
    int ability_slot(ability_kind k) const;
    bool try_cast_on_camp(const camp& c, bool tanking = false);
    bool try_attack_reset_followup(const unit& target, Group* g = nullptr);
    // fight.cpp
    bool combat();
    bool retreat(const std::vector<vec2>& dangers, const std::vector<int>& ranges);
    int escape(const std::vector<const Seen*>& near, bool& safe_here);
    bool try_cast_on_enemy(const Seen& e);
    bool dash_strike(const Seen& e);
    void spread_goals(bitboard& goals, const std::vector<const Seen*>& near);
    void set_turn_priority();
    int prio_set = 0;
    void free_cast(const std::vector<const Seen*>& near, bool may_stand);
    bool try_support();
    void pro_shield();
    int shield_check_round = -1;  // sustain.py: the shield is on cooldown until about this round
    // farm.cpp
    float camp_dps_of(int ally) const;     // estimated damage per round against camps
    float camp_taken_mult(int ally) const;
    bool has_emblem(item_family f) const;
    mutable int emb_round = -1;
    mutable unsigned emb_mask = 0;
    float shield_per_round(int ally) const;
    float hp_of(int ally) const;
    float max_hp_of(int ally) const;
    float heal_for(int gid, bool me_in) const;
    bool tank_type(int ally) const;
    bool alive_free(int ally) const;
    int choose_task();
    int choose_opening();
    int vt_elk_first();  // edit_vtelk.py
    int vt_elk_pick();   // edit_vtelk.py
    int choose_rally(int& k);
    void update_rally();
    bool leader() const;
    bool is_gate_group(int gid) const;
    bool retire_near(Group& g);
    void farm();
    bool work_group(Group& g);
    bool attack_camps(Group& g, int tank, vec2 tank_pos);
    void hor_land_on_group(Group& g, int tank, vec2 tank_pos);
    int land_check_round = -1;  // horland.py: the landing is on cooldown until about this round (saves the ability reads)
    void camp_hit_after_move(Group& g, bool i_tank);
    bool camp_step_after_kill(Group& g, int bi);
    bool stage_at(Group& g);
    bool capture(Group& g);
    void capture_hit(const Group& own);  // edit_vtcap.py
    bool has_crystal();
    bool travel_to_island(Group& g);
    bool travel_tp_spawn(Group& g);
    int crystal_cache = -1;
    int lock_cache = -1;
    bool lock_tried = false;
    bool has_lock();
    bool tp_shortcut(const distance_field& f);
    int want_crystal_round = -1000;  // a shortcut was available lately but I had no crystal
    int tp_check_round = -1;
    void place_ward();
    bool warm_up();  // edit_vtfuel2.py
    std::uint64_t vt_first_need() const {  // edit_vtfuel3.py: fuel the first acting turn may need on this map (120k at most)
        const World& WV = world();
        const std::uint64_t cells = static_cast<std::uint64_t>(WV.w) * static_cast<std::uint64_t>(WV.h);
        std::uint64_t big = 0;
        for (const auto& g : WV.groups) big = std::max<std::uint64_t>(big, g.camps.size());
        return std::min<std::uint64_t>(120000, 30000 + static_cast<std::uint64_t>(WV.groups.size()) * 1200 + cells * 3 + big * (cells / 3 + 1500));
    }
    bool vt_warm_more = false;  // edit_vtfuel2.py: one more set-up turn to warm caches before acting
    bool retreat_step(const std::vector<vec2>& dangers);  // edit_vtfuel2.py
    std::uint64_t vt_home_cost = 0;  // edit_vtfuel2.py: dearest retreat search home seen (fuel)
    int ward_next = 0;  // round of the next placement attempt
};
