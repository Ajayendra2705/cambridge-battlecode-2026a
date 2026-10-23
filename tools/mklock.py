"""Add altar-lock play to a bot: python -I tools/mklock.py BOTDIR [--debug] [--keep N] [--enemy-only]
Buys altar locks (10 gold) when shopping and places one on every unlocked altar within 2 tiles."""
import sys
bot = sys.argv[1]
debug = '--debug' in sys.argv
keep = int(sys.argv[sys.argv.index('--keep') + 1]) if '--keep' in sys.argv else 1
enemy_only = '--enemy-only' in sys.argv
cancel = '--cancel' in sys.argv
p = f'bots/{bot}/src/bot.cpp'
s = open(p, 'rb').read().decode()
crlf = '\r\n' in s
s = s.replace('\r\n', '\n')

D = (lambda x: x) if debug else (lambda x: '')
func = '''// Altar locks (10 gold): a lock cancels enemy tribute channels at its altar and blocks enemy tributes there until
// broken with 5 hits; our own team still tributes. Platform panel 8 rivals bought 6.6 per game, we bought none.
int lock_fail = 0;
void place_altar_lock() {
    if (lock_fail > 5) return;
    auto& me = cambc::self();
    try {
        const auto& lk = me.consumables()[cambc::consumable_type::altar_lock];
        if (lk.count() == 0) return;
        for (auto a : W.altars) {
            if (dist(S.me, a) > 2 || cambc::vision::has_altar_lock(a)) continue;
''' + ('''            bool enemy_here = false;
            for (const auto& e : S.enemies) if (dist(e.pos, a) <= 3) enemy_here = true;
            if (!enemy_here) continue;
''' if enemy_only else '') + ('''            bool tributing = false;
            for (const auto& e : S.enemies)
                if (dist(e.pos, a) <= 1) try { if (e.ch.is_submitting_gems()) tributing = true; } catch (const cambc::error&) {}
            if (!tributing) continue;
''' if cancel else '') + '''            if (lk.use(a)) {
''' + D('''                std::cout << "LK place r" << S.round << " s" << W.slot << " altar " << a.x << "," << a.y << " left " << lk.count() << "\\n";
''') + '''                return;
            }
        }
    } catch (const cambc::error& e) {
        ++lock_fail;
''' + D('''        std::cout << "LK place error r" << S.round << " " << e.what() << "\\n";
''') + '''    }
}

'''
anchor = 'void place_ward_forward() {'
assert s.count(anchor) == 1
s = s.replace(anchor, func + anchor)

call = '    place_ward_forward();\n'
assert s.count(call) == 1
s = s.replace(call, call + '    place_altar_lock();\n')

buy_anchor = '    if (me.gold_count() < 30) return;\n'
assert s.count(buy_anchor) == 1
buy = f'''    try {{
        for (int k = 0; k < {keep} && me.gold_count() >= 10
                        && me.consumables()[cambc::consumable_type::altar_lock].count() < {keep}u; ++k) {{
            me.buy(cambc::consumable_type::altar_lock);
''' + D('''            std::cout << "LK buy r" << cambc::round_number() << " count " << me.consumables()[cambc::consumable_type::altar_lock].count() << "\\n";
''') + '''        }
    } catch (const cambc::error& e) {
''' + D('''        std::cout << "LK buy error " << e.what() << "\\n";
''') + '''    }
'''
s = s.replace(buy_anchor, buy + buy_anchor)
if crlf: s = s.replace('\n', '\r\n')
open(p, 'wb').write(s.encode())
print('lock added to', bot, 'debug' if debug else '', 'keep', keep, 'enemy_only' if enemy_only else '', 'cancel' if cancel else '')
