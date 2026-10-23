"""Add altar-lock play to a bot: python -I tools/variant/mklock.py BOT [--debug] [--keep N] [--enemy-only]
Buys altar locks (10 gold) when shopping and places one on every unlocked altar within 2 tiles.
Each anchor is patched in whichever bots/BOT/src file holds it."""
import glob, sys
bot = sys.argv[1]
debug = '--debug' in sys.argv
keep = int(sys.argv[sys.argv.index('--keep') + 1]) if '--keep' in sys.argv else 1
enemy_only = '--enemy-only' in sys.argv
cancel = '--cancel' in sys.argv
raw = {p: open(p, 'rb').read().decode() for p in glob.glob(f'bots/{bot}/src/*.[ch]*')}
src = {p: t.replace('\r\n', '\n') for p, t in raw.items()}


def put(anchor, text):
    """Replace the single occurrence of anchor, in whichever source file holds it, with text."""
    hits = [p for p, t in src.items() if anchor in t]
    assert len(hits) == 1 and src[hits[0]].count(anchor) == 1, anchor
    src[hits[0]] = src[hits[0]].replace(anchor, text)


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
put('void place_ward_forward() {', func + 'void place_ward_forward() {')
put('    place_ward_forward();\n', '    place_ward_forward();\n    place_altar_lock();\n')

buy_anchor = '    if (me.gold_count() < 30) return;\n'
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
put(buy_anchor, buy + buy_anchor)
for p, t in src.items():
    if t != raw[p].replace('\r\n', '\n'):
        open(p, 'wb').write((t.replace('\n', '\r\n') if '\r\n' in raw[p] else t).encode())
print('lock added to', bot, 'debug' if debug else '', 'keep', keep, 'enemy_only' if enemy_only else '', 'cancel' if cancel else '')
