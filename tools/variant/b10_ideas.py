"""Make the bot_10 idea variants in bots/exp/ (see docs/bot_10.md): python -I tools/variant/b10_ideas.py [NAME...]

Each variant is bots/pool/bot_10 with exact-once substitutions applied through mkvar.py. Every variant turns the
per-turn compact log off (BOT_LOGC 0), so b10n is the base to compare the others against: one factor per variant.
Without names, all variants are made. The variants are untested ideas; record each result in docs/experiments.md.
"""
import os, subprocess, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
MKVAR = os.path.join(ROOT, 'tools', 'variant', 'mkvar.py')

LOG_OFF = [('common.h', '#define BOT_LOGC 1', '#define BOT_LOGC 0')]

# Shop plans of the build bot_10 plays (P_BUILD 4, bot.cpp plan_for): exact lines, each found once.
HOR = '            return plan_cycle({ {F::jungle, S::focus, 5}, {F::durability, S::health, 5} },'
DPS = ('        case champion_type::vendetta:\n'
       '            return plan_cycle({ {F::jungle, S::strength, 5}, {F::durability, S::health, 5}, {F::monster, S::strength, 5} },')
MAR = '            return plan_cycle({ {F::jungle, S::focus, 5}, {F::durability, S::health, 5}, {F::monster, S::focus, 5} },'
WIL = '    case champion_type::willow: return { {F::jungle, S::focus, 5}, {F::bruiser, S::focus, 9999} };'

# Lock-interrupt: placing a lock on an altar cancels the enemy tribute channels there (docs/MECHANICS.md section 9).
LKI_FN = '''// Lock-interrupt (b10lki): a lock placed on an altar within 2 tiles cancels the enemy tribute channels there
// (docs/MECHANICS.md section 9). Carry one and use it on an enemy that is tributing next to me.
bool Bot::lock_interrupt() {
    if (enemies.empty() || !has_lock()) return false;
    auto& me = self();
    const vec2 p = me.position();
    const World& W = world();
    for (const auto& e : enemies) {
        if (!e.channeling) continue;
        for (const vec2 a : W.altars) {
            if (cheb(e.pos, a) > constants::submit_gems_range || cheb(p, a) > 2) continue;
            bool tributing = false;
            try { tributing = e.c.is_submitting_gems(); } catch (...) {}
            if (!tributing) break;
            try {
                if (me.consumables()[consumable_type::altar_lock].use(a)) {
                    lock_cache = 0;
                    act = "lock_interrupt";
                    return true;
                }
            } catch (...) {}
        }
    }
    return false;
}

void Bot::shop() {'''

VARIANTS = {
    # Base for comparisons: bot_10 as sent, with the per-turn log off (the team ships no logging bots).
    'b10n': [],
    # Altar locks on (an existing bot_10 switch): carry one (10 gold, carry limit 1) and lock contested or
    # enemy-side altars we tribute at. Engine 2.0.0 needs 5 hits to break a lock.
    'b10lock': [('params.h', '#define P_LOCKS 0', '#define P_LOCKS 1')],
    # Lock-interrupt (P_LOCKS stays 0): buy one lock on spawn (10 gold) and place it only to cancel an enemy tribute
    # in progress at an altar within 2 tiles of me. Main's dl2 locks against the rivals' game-winning tribute.
    'b10lki': [
        ('bot.h', '    bool has_lock();', '    bool has_lock();\n    bool lock_interrupt();'),
        ('bot.cpp', 'void Bot::shop() {', LKI_FN),
        ('bot.cpp', '    if (P_LOCKS && me.gold_count() >= 80 && !has_lock()) {', '    if (me.gold_count() >= 10 && !has_lock()) {'),
        ('bot.cpp', '    if (P_WARDS) place_ward();', '    lock_interrupt();\n    if (P_WARDS) place_ward();'),
    ],
    # Smaller tribute bags: bank at 48 gems instead of 60 (tribute takes ceil(0.1 x gems) rounds, so banking is
    # cheap; main's bb2 gained from bags about 18% smaller).
    'b10bag': [('params.h', '#define P_TRIB_GEMS 60', '#define P_TRIB_GEMS 48')],
    # Teleport shortcuts off (P_TP_SHORTCUT): main's four teleport-shortcut tries (tp1, tp2, tpe, tpd) were rejected,
    # net 0 or worse. Island maps still use crystals (world().any_island).
    'b10notp': [('params.h', '#define P_TP_SHORTCUT 1', '#define P_TP_SHORTCUT 0')],
    # No bank-everything sweep at 850 tributed (P_END_TRIB above the 1000 to win): main's sweeps es1, es2, dr7 were
    # neutral or rejected. The rule that banks a winning bag (bot.cpp should_tribute) stays.
    'b10noend': [('params.h', '#define P_END_TRIB 850', '#define P_END_TRIB 2000')],
    # Four a side, Vesper instead of Willow: main's four-pick lineup Heart, Vesper, Marcella, Vendetta won 11 of 26
    # four-pick maps against 5-6 (bots/main/src/draft.cpp comment, dq2m on b9). Five a side is unchanged.
    'b10d4': [('draft.cpp', '    else if (n == 4) order = { D::heart_of_ruin, D::marcella, D::vendetta, D::willow };',
               '    else if (n == 4) order = { D::heart_of_ruin, D::marcella, D::vendetta, D::vesper_vale };')],
    # Carrier caution, main's cc2 (gems lost on death 141 -> 80 a game, deaths -0.4, tributed +58): with 30+ gems
    # (fight.cpp `loaded`) never engage, skip the hold, assist, join and skirmish branches, and count any fight as lost.
    'b10cc': [
        ('fight.cpp', '    const float need = loaded ? 0.45f : P_ENGAGE;', '    const float need = loaded ? 99.f : P_ENGAGE;'),
        ('fight.cpp', '    if (tgt && !low && outcome > (P_CONTACT ? P_HOLD_C : -0.15f) && threatened) {',
                      '    if (tgt && !low && !loaded && outcome > (P_CONTACT ? P_HOLD_C : -0.15f) && threatened) {'),
        ('fight.cpp', '    if (P_ASSIST && !low && outcome > P_ASSIST_MIN) {', '    if (P_ASSIST && !low && !loaded && outcome > P_ASSIST_MIN) {'),
        ('fight.cpp', '    if (P_NODEAD && !low) {', '    if (P_NODEAD && !low && !loaded) {'),
        ('fight.cpp', '    if (P_SKIRMISH && tgt && td <= range && !low && outcome > P_SKIRMISH_MIN && me.can_attack()) {',
                      '    if (P_SKIRMISH && tgt && td <= range && !low && !loaded && outcome > P_SKIRMISH_MIN && me.can_attack()) {'),
        ('fight.cpp', '    bool losing = outcome < P_FLEE || low || (loaded && outcome < 0.2f) || nd_leave;',
                      '    bool losing = outcome < P_FLEE || low || loaded || nd_leave;'),
        ('fight.cpp', '    if (P_CONTACT) losing = (threatened ? outcome <= P_HOLD_C : outcome < P_AVOID) || low || (loaded && outcome < 0.2f) || nd_leave;',
                      '    if (P_CONTACT) losing = (threatened ? outcome <= P_HOLD_C : outcome < P_AVOID) || low || loaded || nd_leave;'),
    ],
    # Company on groups, main's sq2 (a joiner's share counts sqrt(n), not n): choose_task scores a group by
    # value / sqrt(n) instead of value / n, so champions stop spreading out alone (farm.cpp, choose_task).
    'b10sq': [('farm.cpp', '        const float s = value * (enabler ? P_ENABLE : 1.f) / n_team / std::max(1.f, Ttot);',
               '        const float s = value * (enabler ? P_ENABLE : 1.f) / std::sqrt(n_team) / std::max(1.f, Ttot);')],
    # Capture emblem (engine 2.0.0: the team's capture time is capped at 3 turns instead of 5 while the holder
    # takes part). Second on Heart of Ruin (lowest id, farms solo), fourth on Vesper Vale and Vendetta (the
    # preferred capturers in capture_bonus). Costs 2 stat points against the bruiser emblem it displaces.
    'b10cap': [
        ('bot.cpp', HOR, HOR.replace('{F::jungle, S::focus, 5}, ', '{F::jungle, S::focus, 5}, {F::capture, S::health, 5}, ')),
        ('bot.cpp', DPS, DPS.replace('{F::monster, S::strength, 5} },', '{F::monster, S::strength, 5}, {F::capture, S::strength, 5} },')),
    ],
    # Home emblem (recall 5 -> 3 rounds) on every champion of the lineup, after its core emblems: bot_10 recalls
    # for every healing and shop trip, and spawn heals fully in one round.
    'b10home': [
        ('bot.cpp', HOR, HOR.replace('{F::durability, S::health, 5} },', '{F::durability, S::health, 5}, {F::home, S::health, 5} },')),
        ('bot.cpp', DPS, DPS.replace('{F::monster, S::strength, 5} },', '{F::monster, S::strength, 5}, {F::home, S::strength, 5} },')),
        ('bot.cpp', MAR, MAR.replace('{F::monster, S::focus, 5} },', '{F::monster, S::focus, 5}, {F::home, S::health, 5} },')),
        ('bot.cpp', WIL, WIL.replace('{F::jungle, S::focus, 5}, ', '{F::jungle, S::focus, 5}, {F::home, S::focus, 5}, ')),
    ],
}


def make(name):
    args = [sys.executable, '-I', MKVAR, 'pool/bot_10', 'exp/' + name]
    for path, old, new in LOG_OFF + VARIANTS[name]:
        assert old != new, f'{name}: substitution in {path} changes nothing'
        args += [path, old, new]
    subprocess.run(args, check=True)


if __name__ == '__main__':
    names = sys.argv[1:] or list(VARIANTS)
    unknown = [n for n in names if n not in VARIANTS]
    if unknown:
        sys.exit(f'unknown variant(s) {unknown}; known: {list(VARIANTS)}')
    for n in names:
        make(n)
