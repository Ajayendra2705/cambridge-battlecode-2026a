// Probe: dump the engine's own data tables (settings, champion/camp/item designs, map camp groups) once per game.
// Output lines start with a tag so tools/probe_dump.py can parse them.
#include <cambc.h>
#include "bot.h"
#include <iostream>

namespace {
using namespace cambc;

void dump_ability(int slot, const detail::ability_props& a) {
    const auto& p = a.payload;
    std::cout << "  slot" << slot << " kind=" << a.kind << " cooldown=" << a.cooldown << " charges=" << a.max_charges
              << " targets=" << a.targets << " attrs=" << a.attributes;
    // Every payload variant is at most three floats and an int; print the raw union both ways.
    std::cout << " dmg(range,mod)=" << p.damage.range << "," << p.damage.modifier
              << " aoe(range,radius,mod,dur)=" << p.aoe_damage.range << "," << p.aoe_damage.radius << ","
              << p.aoe_damage.modifier << "," << p.aoe_damage.duration
              << " cc(range,mod,dur)=" << p.cc.range << "," << p.cc.modifier << "," << p.cc.duration << '\n';
}

void dump_stats(const char* tag, const champion_stats& s) {
    std::cout << tag << " vision=" << s.vision_radius << " move=" << s.base_move_speed << " range=" << s.base_attack_range
              << " hp=" << s.base_health << "+" << s.health_growth << " str=" << s.base_strength << "+" << s.strength_growth
              << " focus=" << s.base_focus << "+" << s.focus_growth << " campmult=" << s.camp_damage_multiplier << '\n';
}

void dump_tables() {
    const auto& g = detail::cached_game_settings;
    std::cout << "SET capture_time=" << g.capture_time << " camp_sleep_time=" << g.camp_sleep_time
              << " respawn_time=" << g.respawn_time << " recall_time=" << g.recall_time
              << " submit_mult=" << g.submit_gem_duration_multiplier << " submit_base=" << g.submit_gem_base_duration
              << " submit_min=" << g.submit_gem_minimum_duration << " submit_range=" << g.submit_gems_range
              << " max_rounds=" << g.max_rounds << " winning_gems=" << g.winning_gems << " kill_gold=" << g.kill_gold
              << " assist_gold=" << g.assist_gold << " passive_gold=" << g.passive_gold << " spawn_healing=" << g.spawn_healing
              << " active_wards=" << g.active_wards << " ward_charges=" << g.ward_charges
              << " shared_mem=" << g.shared_memory_bytes << " draft_mem=" << g.draft_memory_bytes
              << " tile_reveal=" << g.tile_reveal_rounds << " ward_cooldown=" << g.ward_cooldown
              << " ward_lifetime=" << g.ward_lifetime << " ward_vision=" << g.ward_vision_radius
              << " ward_place=" << g.ward_placement_radius << " ctrl_ward_vision=" << g.control_ward_vision_radius
              << " ctrl_ward_place=" << g.control_ward_placement_radius << " lock_hits=" << g.altar_lock_hits
              << " tp_crystal_time=" << g.tp_crystal_time << '\n';
    for (int t = 0; t <= 12; ++t) {
        detail::champion_design d{};
        if (detail::sdk_champion_design(t, &d) != 0) continue;
        std::cout << "CHAMP " << t << " " << to_string(static_cast<champion_type>(t)) << " passive=" << int(d.definition.passive_type)
                  << " attack_type=" << int(d.definition.attack_type) << " vision_type=" << d.definition.vision_type << '\n';
        dump_stats(" STATS", d.base_stats);
        for (int s = 0; s < 2; ++s) dump_ability(s, d.definition.abilities[s]);
    }
    for (int k = 0; k <= 5; ++k) {
        detail::camp_design d{};
        if (detail::sdk_camp_design(k, &d) != 0) continue;
        const auto& s = d.base_stats;
        std::cout << "CAMP " << k << " " << to_string(static_cast<camp_type>(k)) << " vision=" << s.vision_radius
                  << " move=" << s.base_move_speed << " range=" << s.base_attack_range << " hp=" << s.base_health << "+"
                  << s.health_growth << " str=" << s.base_strength << "+" << s.strength_growth << " focus=" << s.base_focus
                  << "+" << s.focus_growth << " passive=" << int(d.definition.passive_type) << '\n';
        for (int a = 0; a < 2; ++a) dump_ability(a, d.definition.abilities[a]);
    }
    const int n_items = static_cast<int>(item_type::enum_type::count);
    for (int i = 0; i < n_items; ++i) {
        detail::item_info x{};
        if (detail::sdk_item_info(static_cast<std::uint32_t>(i), &x) != 0) continue;
        std::cout << "ITEM " << i << " " << to_string(item_type{static_cast<item_type::enum_type>(i)}) << " cost=" << x.cost
                  << " buy=" << x.purchasable << " hp=" << x.health_points << " str=" << x.strength_points
                  << " focus=" << x.focus_points << " passive=" << x.passive << " mag=" << x.passive_magnitude
                  << " combine=" << x.combine_count << " result=" << x.result << " combine_cost=" << x.combine_cost << '\n';
    }
    for (int c = 0; c < 2; ++c) {
        detail::consumable_info x{};
        if (detail::sdk_consumable_info(static_cast<std::uint32_t>(c), &x) != 0) continue;
        std::cout << "CONS " << c << " " << to_string(consumable_type{static_cast<consumable_type::enum_type>(c)})
                  << " cost=" << x.cost << " carry=" << x.carry_limit << '\n';
    }
}

void dump_map() {
    namespace cm = cambc::map;
    std::cout << "MAP w=" << cm::width() << " h=" << cm::height() << " symmetry=" << static_cast<int>(cm::symmetry())
              << " altars=" << cm::altars().count() << " walls=" << cm::walls().count() << " holes=" << cm::holes().count()
              << " bushes=" << cm::bushes().count() << " ally_spawn=" << cm::spawn_region(team::ally).count()
              << " groups=" << cm::camp_groups().size() << '\n';
    for (auto a : cm::altars().positions()) std::cout << "ALTAR " << a.x << "," << a.y << '\n';
    int gi = 0;
    for (const auto& group : cm::camp_groups()) {
        std::int32_t respawn = -1;
        detail::sdk_bc_camp_group_max_respawn(static_cast<std::uint32_t>(static_cast<handle_camp_group_t>(group)), &respawn);
        std::cout << "GROUP " << gi++ << " gems=" << group.gem_value() << " gold=" << group.gold_value() << " respawn=" << respawn
                  << " camps=";
        for (const auto& c : group.camps())
            std::cout << to_string(c.kind()) << "@" << c.spawn_position().x << "," << c.spawn_position().y << ";";
        std::cout << '\n';
    }
}
}  // namespace

void Bot::play_turn() {
    static bool done = false;
    if (done) return;
    done = true;
    // One instance prints: the champion with the lowest handle on our team.
    auto& me = cambc::self();
    std::uint32_t lowest = ~0u;
    for (const auto& a : cambc::champions(team::ally))
        lowest = std::min(lowest, static_cast<std::uint32_t>(static_cast<handle_champion_t>(a)));
    if (static_cast<std::uint32_t>(static_cast<handle_champion_t>(me)) != lowest) return;
    std::cout << "ME " << to_string(me.champion_name()) << " round=" << cambc::round_number() << '\n';
    dump_tables();
    dump_map();
    std::cout << "END" << std::endl;
}
