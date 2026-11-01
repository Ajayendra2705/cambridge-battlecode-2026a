"""apply_edits.py FILE EDITS : EDITS is 's/old/new/' substitutions separated by '@@' (literal text, no regex).
Each edit applies to FILE, or to draft.cpp beside it when FILE lacks the text."""
import os, sys
path, edits = sys.argv[1], sys.argv[2]
files = {path: open(path, encoding="utf-8").read()}
draft = os.path.join(os.path.dirname(path), "draft.cpp")
if os.path.exists(draft): files[draft] = open(draft, encoding="utf-8").read()
for e in [x for x in edits.split("@@") if x.strip()]:
    assert e.startswith("s/") and e.endswith("/"), e
    old, new = e[2:-1].split("/", 1)
    for f, s in files.items():
        if old in s:
            files[f] = s.replace(old, new); break
    else:
        print("EDIT NOT FOUND:", old); sys.exit(1)
for f, s in files.items(): open(f, "w", encoding="utf-8").write(s)
