import sys
# Inject the gb2l combat-log block (V lines) into a bot.cpp after the H-line block.
dst = sys.argv[1]
b = open(dst, 'rb').read().decode()
crlf = '\r\n' in b
b = b.replace('\r\n', '\n')
g = open('bots/gb2l/src/bot.cpp', 'rb').read().decode().replace('\r\n', '\n')
s = g.index('    // Combat log: every turn')
e = g.index('\n\n', s) + 2
blk = g[s:e]
if '// Combat log: every turn' in b:
    sys.exit('already has log')
i = b.index('last=" << last_activity')
anchor = "        std::cout << '" + chr(92) + "n';\n    }\n\n"
j = b.index(anchor, i) + len(anchor)
b = b[:j] + blk + b[j:]
if crlf:
    b = b.replace('\n', '\r\n')
open(dst, 'wb').write(b.encode())
print('ok', len(blk))
