"""Copy a bot into a subfolder of another bot, inside its own namespace, so that one program can hold several bots.
usage: python -I tools/variant/nsbot.py SRC DEST SUB NS [NAME ...]   (bots/SRC/src/* -> bots/DEST/src/SUB/, in namespace NS)

Every #include line of a file moves to the top (in order, after #pragma once), and the rest of the file goes inside
`namespace NS { ... }`, so the bots' same-named classes and functions (Bot, play_draft, ...) do not clash. Quoted
includes resolve in the including file's folder, so the copy finds its own headers. main.cpp's `int main()` becomes
`int run()`, which the dispatcher calls as `NS::run()`. A file that replaces the global operator new (bamboo8's
fastalloc.h) must stay global: it is copied unwrapped and its #include is dropped from main.cpp, so the dispatcher
decides whether to include it (once, at global scope). The build compiles src/**/*.cpp (cmake GLOB_RECURSE).
Each NAME is one of the bot's own functions that its code calls as ::NAME (bamboo8: neighbour_value); those calls become
::NS::NAME, since the function now lives in NS. (A ::NAME of a real global, such as a C library function, stays.)
"""
import os, re, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))


def wrap(text, ns, is_main, names=()):
    lines = text.split('\n')
    pragma = [l for l in lines if l.strip() == '#pragma once']
    incs = [l for l in lines if l.lstrip().startswith('#include')]
    if is_main:
        incs = [l for l in incs if 'fastalloc' not in l]
    body = [l for l in lines if l.strip() != '#pragma once' and not l.lstrip().startswith('#include')]
    while body and body[-1] == '':
        body.pop()
    out = '\n'.join(body)
    for name in names:
        out = re.sub(r'(?<![A-Za-z0-9_>:])::' + re.escape(name) + r'\b', f'::{ns}::{name}', out)
    if is_main:
        out, n = re.subn(r'\bint\s+main\s*\(\s*\)', 'int run()', out)
        assert n == 1, 'main.cpp: no single int main()'
    return '\n'.join(pragma + incs + [f'namespace {ns} {{', out, f'}}  // namespace {ns}', ''])


def main():
    src, dest, sub, ns = sys.argv[1:5]
    names = sys.argv[5:]
    sdir = os.path.join(ROOT, 'bots', src, 'src')
    ddir = os.path.join(ROOT, 'bots', dest, 'src', sub)
    os.makedirs(ddir, exist_ok=True)
    for name in sorted(os.listdir(sdir)):
        if not name.endswith(('.cpp', '.h', '.hpp')):
            continue
        with open(os.path.join(sdir, name), encoding='utf-8', newline='') as f:
            text = f.read()
        crlf = '\r\n' in text
        text = text.replace('\r\n', '\n')
        if re.search(r'\boperator\s+new\s*\(', text):
            out = text  # global allocator: stays outside any namespace
        else:
            out = wrap(text, ns, name == 'main.cpp', names)
        with open(os.path.join(ddir, name), 'w', encoding='utf-8', newline='') as f:
            f.write(out.replace('\n', '\r\n') if crlf else out)
        print(f'{sub}/{name}')


if __name__ == '__main__':
    main()
