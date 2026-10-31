// 8-byte team shared memory protocol.
// bytes 0..4 : per-ally slot = (flag << 7) | code
//              code 0 = none, 1..120 = task group id + 1, 121 home, 122 tribute, 123 fight, 124 dead, 125 retreating
//              flag = ready/engaged at the task (at the staging area or attacking)
// byte  5    : capture event = (toggle << 7) | (group id + 1)
// byte  6    : capture event round & 0xFF
// byte  7    : team rally: heavy camp group id + 1 the whole team takes together (0 = none)
#pragma once
#include "common.h"
namespace cjb {

namespace slot {
constexpr int kNone = 0;
constexpr int kHome = 121;
constexpr int kTribute = 122;
constexpr int kFight = 123;
constexpr int kDead = 124;
constexpr int kRetreat = 125;
}  // namespace slot

struct Comms {
    std::array<std::uint8_t, 8> mem{};
    int last_cap_byte = -1, last_cap_round = -1;
    bool toggle = false;

    void read() {
        try { shared_memory.read(0, std::span<std::uint8_t>(mem.data(), 8)); } catch (...) {}
    }
    int code_of(int ally) const { return (ally < 0 || ally > 4) ? slot::kNone : (mem[ally] & 0x7F); }
    // Task group id of an ally, or -1.
    int task_of(int ally) const {
        const int c = code_of(ally);
        return (c >= 1 && c <= 120) ? c - 1 : -1;
    }
    bool flag_of(int ally) const { return ally >= 0 && ally <= 4 && (mem[ally] & 0x80); }
    void write_raw(int ally, int code, bool flag) {
        if (ally < 0 || ally > 4) return;
        const std::uint8_t v = static_cast<std::uint8_t>((flag ? 0x80 : 0) | (code & 0x7F));
        if (mem[ally] == v) return;
        mem[ally] = v;
        try { shared_memory.write(static_cast<std::size_t>(ally), std::span<const std::uint8_t>(&mem[ally], 1)); } catch (...) {}
    }
    void write_task(int ally, int gid, bool flag) { write_raw(ally, gid >= 0 ? gid + 1 : slot::kNone, flag); }

    void post_capture(int gid, int round) {
        toggle = !toggle;
        mem[5] = static_cast<std::uint8_t>((toggle ? 0x80 : 0) | ((gid + 1) & 0x7F));
        mem[6] = static_cast<std::uint8_t>(round & 0xFF);
        try { shared_memory.write(5, std::span<const std::uint8_t>(&mem[5], 2)); } catch (...) {}
        last_cap_byte = mem[5];
        last_cap_round = mem[6];
    }
    // Group id of a fresh capture event not yet processed (posted this or last round), else -1.
    int poll_capture(int round) {
        const int b = mem[5], rb = mem[6];
        if (b == 0) return -1;
        if (b == last_cap_byte && rb == last_cap_round) return -1;
        last_cap_byte = b;
        last_cap_round = rb;
        toggle = (b & 0x80) != 0;
        const int now = round & 0xFF, prev = (round - 1 + 256) & 0xFF, prev2 = (round - 2 + 256) & 0xFF;
        if (rb != now && rb != prev && rb != prev2) return -1;
        return (b & 0x7F) - 1;
    }

    // Team rally target (heavy group a squad takes together), -1 when none; squad size 3..5 in the top bits.
    int rally() const { return (mem[7] & 0x3F) ? (mem[7] & 0x3F) - 1 : -1; }
    int rally_size() const { return 3 + (mem[7] >> 6); }
    void set_rally(int gid, int k = 5) {
        const std::uint8_t v = static_cast<std::uint8_t>(gid >= 0 && gid < 63 ? ((gid + 1) | ((std::clamp(k, 3, 5) - 3) << 6)) : 0);
        if (mem[7] == v) return;
        mem[7] = v;
        try { shared_memory.write(7, std::span<const std::uint8_t>(&mem[7], 1)); } catch (...) {}
    }
    // Rally squads by size: 3 = tank, bruiser and the strongest striker; 4 adds the second bruiser; 5 everyone.
    static bool rally_member(int ally, int k, int n) {
        if (k >= n) return true;
        if (k == 4) return ally != n - 1;
        return ally == 0 || ally == 1 || ally == n - 2;
    }
};
}  // namespace cjb
