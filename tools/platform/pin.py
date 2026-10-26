"""Pin a panel to the opponents' bots of one run: python -I tools/platform/pin.py RUN@PANEL [NAME]

Writes results/panels/specs_NAME.txt (default PANEL + 'p'): each group of results/panels/specs_PANEL.txt with the run's
group id as a fourth field, which gate.sh passes as --source-group, so the opponent plays the bot it used in that run.
Games are deterministic, so RUN is then the exact base of every run on the pinned panel.
"""
import os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
run = sys.argv[1]
panel = run.split('@')[1]
name = sys.argv[2] if len(sys.argv) > 2 else panel + 'p'
specs = open(os.path.join(ROOT, 'results', 'panels', f'specs_{panel}.txt'), encoding='utf-8').read().split()
ids = [l.split()[1:] for l in open(os.path.join(ROOT, 'results', 'gate.log'), encoding='utf-8') if l.split()[:1] == [run]]
if not ids: sys.exit(f'{run} is not in results/gate.log')
ids = ids[-1]
# A skipped opponent ("no eligible bot") leaves no group id, which would shift every later pin onto the wrong team.
if len(ids) != len(specs): sys.exit(f'{run} has {len(ids)} groups for {len(specs)} specs: pin by hand')
for s in specs:
    if len(s.split(':')) != 3: sys.exit(f'spec without sides, or already pinned: {s}')
out = os.path.join(ROOT, 'results', 'panels', f'specs_{name}.txt')
open(out, 'w', encoding='utf-8', newline='\n').write(' '.join(f'{s}:{g}' for s, g in zip(specs, ids)) + '\n')
print(f'wrote {out}: {len(ids)} groups pinned to {run}')
