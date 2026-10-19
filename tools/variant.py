"""Clone bots/main into bots/<name>, optionally replacing text in its sources.

usage: python tools/variant.py NAME [--sub FILE OLD NEW]...
"""
import os, shutil, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
name = sys.argv[1]
dst = os.path.join(ROOT, 'bots', name)
os.makedirs(os.path.join(dst, 'src'), exist_ok=True)
for f in os.listdir(os.path.join(ROOT, 'bots', 'main', 'src')):
    shutil.copy(os.path.join(ROOT, 'bots', 'main', 'src', f), os.path.join(dst, 'src', f))
for f in ('.clangd', '.gitignore'):
    src = os.path.join(ROOT, 'bots', 'main', f)
    if os.path.exists(src):
        shutil.copy(src, os.path.join(dst, f))
args = sys.argv[2:]
while args:
    assert args[0] == '--sub'
    path, old, new = os.path.join(dst, 'src', args[1]), args[2], args[3]
    text = open(path).read()
    assert old in text, (path, old)
    open(path, 'w').write(text.replace(old, new))
    args = args[4:]
print('created', dst)
