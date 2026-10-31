# Transparent NTFS compression (WOF, LZX) of run outputs older than an hour: reads stay unchanged, about 15 to 1 on game
# JSON; a write to a file undoes it. Skips .gz, .zip, .wasm, .tmp* and files under 8 KB.
# usage: python -I tools/local/compact_old.py DIR... (e.g. data/runs data/summaries; Windows only)
import os, sys, time, subprocess
cut = time.time() - 3600
F = []
for top in sys.argv[1:]:
    for r, _, fs in os.walk(top):
        for f in fs:
            p = os.path.join(r, f)
            if f.startswith('.tmp') or f.endswith(('.gz', '.zip', '.wasm')): continue
            try:
                if os.path.getmtime(p) < cut and os.path.getsize(p) > 8192: F.append(os.path.normpath(p))
            except OSError: pass
print(len(F), 'files', flush=True)
for i in range(0, len(F), 150):
    subprocess.run(['compact.exe', '/c', '/exe:lzx', '/i', '/q'] + F[i:i + 150], stdout=subprocess.DEVNULL)
    if i % 1500 == 0: print(i, time.strftime('%H:%M:%S'), flush=True)
print('done', time.strftime('%H:%M:%S'), flush=True)
