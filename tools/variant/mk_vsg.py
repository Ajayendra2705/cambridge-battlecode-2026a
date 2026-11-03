"""Gated altars: the team starts the siege of the gate camps later, and believes the gate is open when the enemy tributes: python -I tools/variant/mk_vsg.py NAME FROM BELIEF [BASE] [SRC]

On a gated altar map (01boss_battle: the only altar sits behind two monoliths) the bot calls the whole team to the guards from r400. Ranked games show that a team breaking them early
stands at the altar poorer than its rival (gold 4600 against 8000 when they fell before r520), while a break at r843 found us ahead. FROM replaces P_SIEGE_FROM on gated maps only.
BELIEF (rounds, 0 off): the enemy's tributed total can only rise with the gate open, so for that many rounds after a rise carriers go there even if the guards look alive in our
memory; seeing a live guard on the gate tile ends the belief.
"""
import os, shutil, sys
name, frm, belief = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
base = sys.argv[4] if len(sys.argv) > 4 else 'bots/exp/vnl1'
src = sys.argv[5] if len(sys.argv) > 5 else 'src'
dst = 'bots/exp/' + name
if os.path.exists(dst):
    shutil.rmtree(dst)
shutil.copytree(base, dst, ignore=shutil.ignore_patterns('.cambc'))


def patch(path, pairs):
    f = f'{dst}/{src}/{path}'
    s = open(f, encoding='utf-8', newline='').read()
    for a, b in pairs:
        assert s.count(a) == 1, a
        s = s.replace(a, b)
    open(f, 'w', encoding='utf-8', newline='').write(s)


patch('farm.cpp', [("(W.gated || W.heavy_map) ? (round >= P_SIEGE_FROM && ", "(W.gated || W.heavy_map) ? (round >= (W.gated ? P_GATE_FROM : P_SIEGE_FROM) && ")])
patch('params.h', [('#ifndef P_SIEGE_FROM', f'#ifndef P_GATE_FROM\n#define P_GATE_FROM {frm}\n#endif\n#ifndef P_GATE_BELIEF\n#define P_GATE_BELIEF {belief}\n#endif\n#ifndef P_SIEGE_FROM')])
patch('world.h', [("    bool gated = false;", "    int enemy_sg_seen = 0;\n    int gate_belief_until = 0;\n    bool gate_believed = false;\n    bool gated = false;")])
patch('world.cpp', [
    ("void World::observe(int round, vec2 me) {\n", """void World::observe(int round, vec2 me) {
    if (gated && P_GATE_BELIEF > 0) {
        const int es = static_cast<int>(global_submitted_gems(team::enemy));
        if (es > enemy_sg_seen) { enemy_sg_seen = es; gate_belief_until = round + P_GATE_BELIEF; }
    }
"""),
    ("""                g.state = GState::Respawning;
                g.respawn_round = round + timer;
                for (auto& c : g.camps) c.hp = 0;
            }
        }
    }
}
""", """                g.state = GState::Respawning;
                g.respawn_round = round + timer;
                for (auto& c : g.camps) c.hp = 0;
            }
        }
    }
    if (gated) {
        // A live guard in view on the gate tile ends the belief.
        for (const auto& gt : gates) {
            if (gt.group < 0) continue;
            const Group& g = groups[static_cast<std::size_t>(gt.group)];
            if (g.seen_round != round || g.state != GState::Alive) continue;
            for (const auto& c : g.camps)
                if (c.pos == gt.tile && c.hp > 0) gate_belief_until = 0;
        }
        gate_believed = round < gate_belief_until;
    }
}
"""),
    ("""        bool dead = g.state != GState::Alive;
        if (!dead)
            for (const auto& c : g.camps)
                if (c.pos == gt.tile && c.hp <= 0) dead = true;
""", """        bool dead = g.state != GState::Alive || gate_believed;
        if (!dead)
            for (const auto& c : g.camps)
                if (c.pos == gt.tile && c.hp <= 0) dead = true;
"""),
])
print('ok', name, frm, belief)
