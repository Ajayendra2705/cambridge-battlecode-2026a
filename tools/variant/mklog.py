"""Add the combat log (V lines, read by tools/replay/vana.py and dpre2.py) to a bot: python -I tools/variant/mklog.py BOT
Inserts tools/variant/combat_log.cpp after the H-line debug block, in whichever src/*.cpp holds it.
Logging bots are named BOT + 'l' (hb4 -> hb4l); never put one on the ladder (prints cost fuel)."""
import glob, os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
blk = open(os.path.join(ROOT, 'tools', 'variant', 'combat_log.cpp'), encoding='utf-8').read()
anchor = "        std::cout << '\\n';\n    }\n\n"
for path in glob.glob(os.path.join(ROOT, 'bots', sys.argv[1], 'src', '*.cpp')):
    b = open(path, 'rb').read().decode()
    crlf = '\r\n' in b
    b = b.replace('\r\n', '\n')
    if 'last=" << last_activity' not in b: continue
    if '// Combat log: every turn' in b: sys.exit('already has log')
    j = b.index(anchor, b.index('last=" << last_activity')) + len(anchor)
    b = b[:j] + blk + b[j:]
    open(path, 'wb').write((b.replace('\n', '\r\n') if crlf else b).encode())
    sys.exit(f'ok {path}')
sys.exit('anchor not found')
