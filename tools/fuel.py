"""Summarise per-turn fuel use from a replay bundle's team fuel log (format guessed: 13-byte header, u64 values)."""
import struct, sys, zipfile

path, team = sys.argv[1], (sys.argv[2] if len(sys.argv) > 2 else 'a')
b = zipfile.ZipFile(path).read(f'team-{team}.fuel')
n = (len(b) - 13) // 8
v = struct.unpack('<%dQ' % n, b[13:13 + n * 8])
config, used = v[:8], v[8:]
print('config', config)
print('turns', len(used), 'max', max(used), 'mean', sum(used) // len(used))
for limit in (50000, 80000, 95000, 100000):
    print(f'>= {limit}:', sum(1 for x in used if x >= limit))
print('largest', sorted(used)[-8:])
