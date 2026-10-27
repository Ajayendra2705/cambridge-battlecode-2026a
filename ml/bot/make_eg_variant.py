"""Apply the enemy gain model (eg) to a bot: python -I ml/bot/make_eg_variant.py BASE NAME THRESHOLD (e.g. main exp/eg1 50).

Copies bots/BASE to bots/NAME with tools/variant/mkvar.py, adds ml/bot/eg.h and ml/bot/eg_weights.h, reads our own
champions' bags into ChampSnap::bag, and adds a fight trigger next to `rich`: engage a prey whose bag plus predicted gain
over the next 60 rounds reaches THRESHOLD gems, under rich's safety conditions. Each patch must match exactly once.
"""
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def patches(threshold):
    return [
        ("bot.cpp", '#include "knowledge.h"\n', '#include "knowledge.h"\n#include "eg.h"\n'),
        ("snapshot.h", "    std::uint32_t gems;\n", "    std::uint32_t gems;\n    std::uint32_t bag = 0;\n"),
        ("knowledge.h", "        snap.type = k.type;\n",
         "        snap.type = k.type;\n        try {\n            snap.bag = k.ch.gem_count();\n        } catch (const cambc::error&) {\n        }\n"),
        ("bot.cpp", "    const bool big_bag = me.gem_count() >= 150;\n",
         "    const bool big_bag = me.gem_count() >= 150;\n"
         "    // Enemy gain model (eg, ml/eg_*): a prey about to gain or carrying many gems is worth rich's risk.\n"
         f"    const bool eg_rich = prey && !rich && ally_power >= enemy_power * 0.5f && S.hp > S.max_hp * 0.5f && !sim_me_dies\n"
         f"        && cambc::fuel_remaining() > 20000 && static_cast<float>(prey->gems) + eg_predict(*prey) >= {threshold}.0f;\n"),
        ("bot.cpp", "(winning || finisher || rich || (at_spawn", "(winning || finisher || rich || eg_rich || (at_spawn"),
    ]


def main():
    base, name, threshold = sys.argv[1], sys.argv[2], int(sys.argv[3])
    if (ROOT / "bots" / name).exists():
        sys.exit(f"bots/{name} exists: delete it first")
    args = [x for patch in patches(threshold) for x in patch]
    subprocess.run([sys.executable, "-I", "tools/variant/mkvar.py", base, name, *args], cwd=ROOT, check=True)
    for f in ["eg.h", "eg_weights.h"]:
        shutil.copy(Path(__file__).resolve().parent / f, ROOT / "bots" / name / "src" / f)
    print(f"made bots/{name} with eg (threshold {threshold}); build with: cambc build {name} --release")


if __name__ == "__main__":
    main()
