// Movement helpers: greedy steps on static fields, dynamic BFS, fleeing.
#pragma once
#include "common.h"
#include "world.h"

struct Nav {
    std::optional<bitboard> occ;  // visible champions, camps and teleport reservations (minus self)
    int dash_slot = -1;           // set by the bot when a travel dash may be used this turn
    int dash_cd = 99;             // dash cooldown this turn (99: no dash)
    int cross_slot = -1;          // dash slot when ready, even with enemies in sight (bridge crossings only)
    bool bridge_wait = false;     // this turn's travel waited at a bridge for the dash
    bool dash_hits = false;       // landing damages/stuns neighbours (Heart of Ruin): keep clear of camps
    bool dashed = false;

    void begin_turn() { occ.reset(); refused_any = false; }

    const bitboard& occupied() {
        if (!occ) {
            occ.emplace(vision::champion_tiles() | vision::camp_tiles() | vision::teleport_tiles());
            if (refused_any) *occ |= refused;
            occ->set(self().position(), false);
        }
        return *occ;
    }

    bool passable(vec2 q) {
        const World& W = world();
        return in_bounds(q) && !bb_test(*W.blocked, q) && !bb_test(occupied(), q);
    }

    // Tiles the engine refused as occupied this turn (units we cannot see, e.g. allies in bushes).
    bitboard refused;
    bool refused_any = false;
    void note_refused(vec2 q) {
        if (!refused_any) { refused.clear(); refused_any = true; }
        refused.set(q);
        if (occ) occ->set(q);
    }

    // Greedy step to a strictly better tile of a static field. Threat tiles cost ~2.5 steps.
    bool step_field(const distance_field& f, const bitboard* threat) {
        auto& me = self();
        if (!me.can_move()) return false;
        const vec2 p = me.position();
        const int cur = df_get(f, p);
        const int cur_s = (cur == distance_field::unreachable ? 1 << 24 : cur * 16) + (threat && bb_test(*threat, p) ? 40 : 0);
        for (int attempt = 0; attempt < 3; ++attempt) {
            int best = 1 << 30;
            vec2 bp = p;
            for (auto d : kDirs) {
                const vec2 q = p + d;
                if (!passable(q)) continue;
                const int v = df_get(f, q);
                if (v == distance_field::unreachable) continue;
                int s = v * 16;
                if (threat && bb_test(*threat, q)) s += 40;
                if (s < best) { best = s; bp = q; }
            }
            if (best >= cur_s) return false;
            try {
                if (me.move_absolute(bp)) return true;
                return false;
            } catch (...) {
                note_refused(bp);  // occupied by something out of sight: try the next best tile
            }
        }
        return false;
    }

    // BFS from goal tiles back to us with current obstacles; step along it.
    bool step_bfs(const bitboard& goals, const bitboard* extra_walls) {
        auto& me = self();
        if (!me.can_move()) return false;
        const vec2 p = me.position();
        if (bb_test(goals, p)) return false;
        const World& W = world();
        const bool br = P_BRIDGES && W.dasher && !W.bridges->is_empty();
        bitboard walls = (br ? *W.fwalls : *W.blocked) | occupied();
        if (extra_walls) walls |= *extra_walls;
        walls.set(p, false);
        bitboard roots = goals;
        roots &= ~walls;
        if (roots.is_empty()) return false;
        bitboard dest;
        dest.set(p);
        distance_field f;
        bitboard visited;
        f.compute_to(walls, roots, dest, visited);
        vec2 at = p;
        // Near a bridge the dash is kept for crossing it (a speed dash would leave us waiting at the hole); with
        // enemies in sight only crossings are dashed (the dash is kept for fights otherwise).
        const bool reserve = br && bb_test(*W.bridge_zone, p);
        const int dslot = dash_slot >= 0 ? dash_slot : (br ? cross_slot : -1);
        if (dslot >= 0 && !dashed) {
            const int v0 = df_get(f, p);
            int bv = v0 - 2;
            vec2 best = p;
            for (int dx = -2; dx <= 2; ++dx)
                for (int dy = -2; dy <= 2; ++dy) {
                    const vec2 q{ p.x + dx, p.y + dy };
                    if (q == p || !in_bounds(q) || bb_test(walls, q) || bb_test(*W.blocked, q)) continue;
                    bool cross = false;
                    if (br)
                        for (auto d : kDirs) {
                            const vec2 m = p + d;
                            if (cheb(m, q) == 1 && bb_test(*W.bridges, m)) { cross = true; break; }
                        }
                    if ((reserve || dash_slot < 0) && !cross) continue;
                    if (dash_hits && !cross) {
                        bool near_camp = false;
                        for (auto d : kDirs) {
                            const vec2 r = q + d;
                            if (in_bounds(r) && bb_test(*world().camp_tiles, r)) { near_camp = true; break; }
                        }
                        if (near_camp) continue;
                    }
                    const int v = df_get(f, q);
                    if (v <= bv) { bv = v; best = q; }
                }
            if (best != p) {
                try {
                    if (me.abilities()[static_cast<std::size_t>(dslot)].use(best)) { dashed = true; at = me.position(); occ.reset(); }
                } catch (...) {}
            }
        }
        if (at != p && bb_test(goals, at)) return true;
        const auto mv = f.next_move_from(at);
        if (!mv) return at != p;
        if (br && bb_test(*W.bridges, at + *mv)) {
            // The way goes over a hole: the dash is due soon -> wait here; else walk around this turn.
            if (at != p) return true;
            if (dash_cd > 0 && dash_cd <= P_BRIDGE_WAIT) { bridge_wait = true; return true; }
            bitboard w2 = *W.blocked | occupied();
            if (extra_walls) w2 |= *extra_walls;
            w2.set(p, false);
            bitboard r2 = goals;
            r2 &= ~w2;
            if (r2.is_empty()) return false;
            distance_field f3;
            bitboard vis3;
            f3.compute_to(w2, r2, dest, vis3);
            const auto mv3 = f3.next_move_from(p);
            if (!mv3) return false;
            try { return me.move(*mv3); } catch (...) { note_refused(p + *mv3); return false; }
        }
        if (at != p && bb_test(occupied(), at + *mv)) return true;
        try {
            return me.move(*mv) || at != p;
        } catch (...) {
            if (at != p) return true;
            // Refused (occupied out of sight): replan once around that tile.
            note_refused(at + *mv);
            bitboard walls2 = walls | refused;
            distance_field f2;
            bitboard visited2;
            f2.compute_to(walls2, roots & ~refused, dest, visited2);
            const auto mv2 = f2.next_move_from(at);
            if (!mv2) return false;
            try { return me.move(*mv2); } catch (...) { note_refused(at + *mv2); return false; }
        }
    }

    // Travel towards goals with a consistent policy: BFS avoiding threat tiles, then BFS through them,
    // then the static field as a last resort.
    bool travel(const bitboard& goals, const distance_field* field, const bitboard* threat, vec2 anchor = { -1, -1 }) {
        (void)anchor;
        auto& me = self();
        if (!me.can_move()) return false;
        // Low on fuel: the static field only (a BFS here could run the turn out of fuel and lose the move).
        if (field && fuel() < P_NAV_LOW && step_field(*field, threat)) return true;
        // Far from the goal: descend the static field (cheap); near it, plan around live obstacles.
        if (field && dash_slot < 0) {
            const int d = df_get(*field, me.position());
            if (d != distance_field::unreachable && d > 8 && step_field(*field, threat)) return true;
        }
        if (step_bfs(goals, threat)) return true;
        if (threat && fuel() > P_NAV_LOW && step_bfs(goals, nullptr)) return true;
        if (field) return step_field(*field, nullptr);
        return false;
    }

    // Inside a threat zone: take the shortest way out, towards the field's goal among equally short exits.
    bool escape(const bitboard& threat, const distance_field* field) {
        auto& me = self();
        if (!me.can_move()) return false;
        const vec2 p = me.position();
        if (!bb_test(threat, p)) return false;
        const World& W = world();
        bitboard walls = *W.blocked | occupied();
        walls.set(p, false);
        bitboard roots = ~threat;
        roots &= ~walls;
        if (roots.is_empty()) return false;
        bitboard dest, visited;
        dest.clear();
        dest.set(p);
        distance_field f;
        f.compute_to(walls, roots, dest, visited);
        int best = 1 << 30;
        vec2 bp = p;
        for (auto d : kDirs) {
            const vec2 q = p + d;
            if (!passable(q)) continue;
            const int e = df_get(f, q);
            if (e == distance_field::unreachable) continue;
            int h = field ? df_get(*field, q) : 0;
            if (h == distance_field::unreachable) h = 500;
            const int s = e * 1000 + h;
            if (s < best) { best = s; bp = q; }
        }
        if (bp == p) return false;
        try { return me.move_absolute(bp); } catch (...) { note_refused(bp); return false; }
    }

    // Step away from danger points, preferring tiles closer to home.
    bool flee(const std::vector<vec2>& dangers, const bitboard* threat) {
        auto& me = self();
        if (!me.can_move()) return false;
        const vec2 p = me.position();
        const World& W = world();
        int best = -(1 << 30);
        vec2 bp = p;
        auto score = [&](vec2 q) {
            int mind = 1000;
            for (auto d : dangers) mind = std::min(mind, cheb(q, d));
            int home = df_get(*W.f_spawn, q);
            if (home == distance_field::unreachable) home = 500;
            int s = std::min(mind, 7) * 100 - home * 3;
            if (threat && bb_test(*threat, q)) s -= 150;
            return s;
        };
        const int cur = score(p);
        for (auto d : kDirs) {
            const vec2 q = p + d;
            if (!passable(q)) continue;
            const int s = score(q);
            if (s > best) { best = s; bp = q; }
        }
        if (best <= cur) return false;
        try { return me.move_absolute(bp); } catch (...) { return false; }
    }
};
