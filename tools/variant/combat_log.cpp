    // Combat log: every turn with an enemy champion within 8 (off its spawn), our state, allies and enemies.
    {
        bool seen = false;
        for (const auto& e : S.enemies) if (!W.enemy_spawn.is_set(e.pos) && dist(p, e.pos) <= 8) seen = true;
        if (seen) {
            std::cout << "V" << round << " " << W.slot << " " << static_cast<int>(me.champion_name()) << " " << p.x << "," << p.y << " "
                      << static_cast<int>(S.hp) << "/" << static_cast<int>(S.max_hp) << " " << static_cast<int>(S.str) << "/"
                      << static_cast<int>(me.focus()) << " g" << me.gem_count() << " " << last_activity << " t" << static_cast<int>(taken)
                      << " |";
            for (const auto& a : S.allies)
                if (dist(p, a.pos) <= 8) std::cout << " " << static_cast<int>(a.type) << "@" << a.pos.x << "," << a.pos.y << "/" << static_cast<int>(a.hp);
            std::cout << " |";
            for (const auto& e : S.enemies) {
                if (W.enemy_spawn.is_set(e.pos)) continue;
                bool st = false;
                try { st = e.ch.buffs().has_stun(); } catch (const cambc::error&) {}
                std::cout << " " << static_cast<int>(e.type) << "@" << e.pos.x << "," << e.pos.y << "/" << static_cast<int>(e.hp) << "/"
                          << static_cast<int>(e.max_hp) << "/" << static_cast<int>(e.str) << (st ? "s" : "");
            }
            std::cout << '\n';
        }
    }

