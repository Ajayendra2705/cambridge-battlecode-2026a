"""Apply the farm prediction model (fpr) to a bot: python -I ml/bot/make_fpr_variant.py BASE NAME (e.g. main exp/fpr).

Copies bots/BASE to bots/NAME with tools/variant/mkvar.py, adds ml/bot/fpr.h and ml/bot/fpr_weights.h, and patches
pick_group (targets.h) so its best live-camp candidates are rescored as formula score x P(our team captures the group).
Each patch must match exactly once; if BASE has diverged from the code fpr was written against, mkvar stops and names
the patch that failed.
"""
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

PATCHES = [
    ("bot.cpp", '#include "knowledge.h"\n', '#include "knowledge.h"\n#include "fpr.h"\n'),
    ("snapshot.h", "    float hp = 0, max_hp = 0, str = 0;\n    int range = 1;\n    bitboard visible",
     "    float hp = 0, max_hp = 0, str = 0, focus = 0;\n    int range = 1;\n    bitboard visible"),
    ("knowledge.h", "        S.str = info.strength;\n", "        S.str = info.strength;\n        S.focus = info.focus;\n"),
    ("targets.h", "    double best = 0, current_score = 0;\n", "    double best = 0, current_score = 0;\n    std::vector<FprCand> fpr_cands;\n"),
    ("targets.h", "        if (score > best) best = score, best_i = i, best_n = score_n;\n",
     "        if (score > best) best = score, best_i = i, best_n = score_n;\n"
     "        if (score > 0) fpr_cands.push_back({score, i, score_n, g.state, travel});\n"),
    ("targets.h", "    if (current >= 0 && current_score > 0 && current_score * 1.05 >= best) {",
     """    // Farm prediction model (fpr, ml/fpr_*): weight the best live-camp candidates by the learned P(our team captures
    // the group). Cleared or respawning groups keep the formula (the model only saw attempts on live camps).
    if (!fpr_cands.empty() && cambc::fuel_remaining() > 30000) {
        std::sort(fpr_cands.begin(), fpr_cands.end(), [](const FprCand& a, const FprCand& b) { return a.score > b.score; });
        if (fpr_cands.front().state == 0) {
            fpr_init();
            alignas(16) float hs[FPR_H];
            fpr_self_part(hs);
            double ml_best = -1, ml_current = -1;
            int ml_i = -1, ml_n = 1, ml_current_n = 1, seen = 0;
            for (const auto& c : fpr_cands) {
                if (c.state != 0 || !fpr_static[c.group].ready) continue;
                if (++seen > FPR_TOP) break;
                float pr, t;
                fpr_predict(c.group, hs, pr, t);
                const double s = c.score * pr;
                if (c.group == current) ml_current = s, ml_current_n = c.team;
                if (s > ml_best) ml_best = s, ml_i = c.group, ml_n = c.team;
            }
            if (ml_i >= 0) {
                if (current >= 0 && ml_current > 0 && ml_current * 1.05 >= ml_best) {
                    planned_team = ml_current_n;
                    return current;
                }
                planned_team = ml_n;
                return ml_i;
            }
        }
    }
    if (current >= 0 && current_score > 0 && current_score * 1.05 >= best) {"""),
]


def main():
    base, name = sys.argv[1], sys.argv[2]
    if (ROOT / "bots" / name).exists():
        sys.exit(f"bots/{name} exists: delete it first")
    args = [x for patch in PATCHES for x in patch]
    subprocess.run([sys.executable, "-I", "tools/variant/mkvar.py", base, name, *args], cwd=ROOT, check=True)
    for f in ["fpr.h", "fpr_weights.h"]:
        shutil.copy(ROOT / "ml/bot" / f, ROOT / "bots" / name / "src" / f)
    print(f"made bots/{name} with fpr; build with: cambc build {name} --release")


if __name__ == "__main__":
    main()
