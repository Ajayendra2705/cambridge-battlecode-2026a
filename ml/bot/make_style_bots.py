import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AGG = [-2, -1, 0, 1, 2, 3]
BANK = [0.5, 1.0, 1.8]


def name(a, b):
    return f"exp/sty_a{a:+d}_b{str(b).replace('.', 'p')}".replace("+", "p").replace("-", "m")


PATCHES = [
    ("bot.cpp", "namespace {\n", "namespace {\nconstexpr int STY_AGG = {AGG};\nconstexpr double STY_BANK = {BANK};\n"),
    ("targets.h", "        if (side > 0) score /= 1.0 + std::min(side, 20) / 20.0;",
     "        if (side > 0) score /= std::max(0.5, 1.0 + std::min(side, 20) / 20.0 * (1.0 - 0.75 * STY_AGG));"),
    ("bot.cpp", "    if (!big_bag && prey && (winning || finisher || rich || (at_spawn && dist(p, prey->pos) <= S.range))) {",
     "    // Skilled aggression: take even fights when healthy and not outnumbered, never ones the sim says kill us.\n"
     "    const bool sty_aggro = STY_AGG >= 1 && prey && !sim_me_dies && S.hp > S.max_hp * (0.75f - 0.05f * STY_AGG) && enemy_count <= ally_count;\n"
     "    const bool sty_ok = STY_AGG >= 0 || finisher || (STY_AGG == -1 && enemy_count < ally_count);\n"
     "    if (!big_bag && prey && sty_ok && (winning || finisher || rich || sty_aggro || (at_spawn && dist(p, prey->pos) <= S.range))) {"),
    ("bot.cpp", "S.hp < S.max_hp * 0.4f", "S.hp < S.max_hp * (STY_AGG < 0 ? 0.4f - 0.1f * STY_AGG : 0.4f)"),
    ("bot.cpp", "        const double batch = std::sqrt(2.0 * c * tau / (m * h));",
     "        const double batch = STY_BANK * std::sqrt(2.0 * c * tau / (m * h));"),
]


def make(a, b):
    bot = name(a, b)
    if (ROOT / "bots" / bot).exists():
        shutil.rmtree(ROOT / "bots" / bot)
    args = []
    for f, old, new in PATCHES:
        args += [f, old, new.replace("{AGG}", str(a)).replace("{BANK}", str(b))]
    subprocess.run([sys.executable, "-I", "tools/variant/mkvar.py", "main", bot, *args], cwd=ROOT, check=True, stdout=subprocess.DEVNULL)
    return bot


def main():
    bots = [make(a, b) for a in AGG for b in BANK]
    print(",".join(bots))


if __name__ == "__main__":
    main()
