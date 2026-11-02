// Shared includes, logging and small helpers.
#pragma once
#include <cambc.h>
#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <memory>
#include <optional>
#include <variant>
#include <vector>

using namespace cambc;

// Set to 1 for local diagnostic logs (costs fuel; keep 0 for submissions).
#ifndef BOT_LOG
#define BOT_LOG 0
#endif
#if BOT_LOG
#define LOG(...) std::printf(__VA_ARGS__)
#else
#define LOG(...) ((void)0)
#endif
// Compact platform log (one line per champion turn, fight details): BOT_LOGC=1.
#ifndef BOT_LOGC
#define BOT_LOGC 1
#endif
#if BOT_LOGC
// Cheap formatter (printf's float formatting runs on soft long doubles in wasm and cost ~10k fuel per
// champion turn): integers and fixed-point floats into a turn buffer, written once at the end of the turn.
#include <cstdarg>
namespace logc {
inline char* buf() { static char b[16384]; return b; }
inline std::size_t& len() { static std::size_t n = 0; return n; }
inline void put(char c) { if (len() < 16383) buf()[len()++] = c; }
inline void put_s(const char* s) { while (*s) put(*s++); }
inline void put_u(unsigned long long v) {
    char t[24];
    int n = 0;
    do { t[n++] = static_cast<char>('0' + v % 10); v /= 10; } while (v);
    while (n) put(t[--n]);
}
inline void put_i(long long v) {
    if (v < 0) { put('-'); v = -v; }
    put_u(static_cast<unsigned long long>(v));
}
inline void put_f(double v, int dec) {
    if (v < 0) { put('-'); v = -v; }
    long long scale = 1;
    for (int i = 0; i < dec; ++i) scale *= 10;
    const long long x = static_cast<long long>(v * static_cast<double>(scale) + 0.5);
    put_u(static_cast<unsigned long long>(x / scale));
    if (dec > 0) {
        put('.');
        const long long fr = x % scale;
        for (long long d = scale / 10; d > 0; d /= 10) put(static_cast<char>('0' + (fr / d) % 10));
    }
}
inline void fmt(const char* f, ...) {
    va_list ap;
    va_start(ap, f);
    while (*f) {
        if (*f != '%') { put(*f++); continue; }
        ++f;
        int dec = -1;
        if (*f == '.') {
            ++f;
            dec = 0;
            while (*f >= '0' && *f <= '9') dec = dec * 10 + (*f++ - '0');
        }
        bool z = false;
        int l = 0;
        if (*f == 'z') { z = true; ++f; }
        while (*f == 'l') { ++l; ++f; }
        switch (*f) {
        case 'd':
            if (l >= 2) put_i(va_arg(ap, long long));
            else if (l == 1) put_i(va_arg(ap, long));
            else put_i(va_arg(ap, int));
            break;
        case 'u':
            if (z) put_u(va_arg(ap, std::size_t));
            else if (l >= 2) put_u(va_arg(ap, unsigned long long));
            else if (l == 1) put_u(va_arg(ap, unsigned long));
            else put_u(va_arg(ap, unsigned));
            break;
        case 's': put_s(va_arg(ap, const char*)); break;
        case 'c': put(static_cast<char>(va_arg(ap, int))); break;
        case 'f': put_f(va_arg(ap, double), dec < 0 ? 6 : dec); break;
        case '%': put('%'); break;
        default: break;
        }
        if (*f) ++f;
    }
    va_end(ap);
}
inline void flush() {
    if (len()) {
        std::fwrite(buf(), 1, len(), stdout);
        std::fflush(stdout);
        len() = 0;
    }
}
}  // namespace logc
#define LOGC(...) logc::fmt(__VA_ARGS__)
#define LOGC_FLUSH() logc::flush()
#else
#define LOGC(...) ((void)0)
#define LOGC_FLUSH() ((void)0)
#endif

inline int cheb(vec2 a, vec2 b) { return static_cast<int>(a.chebyshev_distance(b)); }
inline bool in_bounds(vec2 p) { return p.x >= 0 && p.y >= 0 && p.x < map::width() && p.y < map::height(); }

static constexpr std::array<vec2, 8> kDirs{ vec2{0, 1}, vec2{1, 1}, vec2{1, 0}, vec2{1, -1},
                                            vec2{0, -1}, vec2{-1, -1}, vec2{-1, 0}, vec2{-1, 1} };

inline std::uint64_t fuel() { return fuel_remaining(); }

// Local reads of engine-chunked storage (host calls cost ~70 fuel each).
// Bitboards: one u64 per 8x8 chunk, row stride = chunk_stride. Fields: 64 u16 per chunk, row stride = chunked_width.
inline bool bb_test(const bitboard& b, vec2 p) {
    const auto& L = detail::layout();
    if (p.x < 0 || p.y < 0 || p.x >= L.width || p.y >= L.height) return false;
    return (b.ptr()[static_cast<std::size_t>((p.y >> 3) * static_cast<int>(L.chunk_stride) + (p.x >> 3))] >> (((p.y & 7) << 3) | (p.x & 7))) & 1ull;
}
inline int df_get(const distance_field& f, vec2 p) {
    const auto& L = detail::layout();
    if (p.x < 0 || p.y < 0 || p.x >= L.width || p.y >= L.height) return distance_field::unreachable;
    return f.ptr()[static_cast<std::size_t>(((p.y >> 3) * static_cast<int>(L.chunked_width) + (p.x >> 3)) * 64 + ((p.y & 7) << 3) + (p.x & 7))];
}

// Camp design numbers (from the engine, verified by probe).
inline float camp_max_hp(camp_type t) {
    switch (t) {
    case camp_type::wolf: return 1350.f;
    case camp_type::elk: return 2400.f;
    case camp_type::gem_cluster: return 120.f;
    case camp_type::gold_cluster: return 120.f;
    case camp_type::monolith: return 20000.f;
    case camp_type::golem: return 5000.f;
    }
    return 1000.f;
}
inline float camp_str(camp_type t) {
    switch (t) {
    case camp_type::wolf: return 20.f;
    case camp_type::elk: return 60.f;
    case camp_type::monolith: return 200.f;
    case camp_type::golem: return 120.f;
    default: return 0.f;
    }
}
inline int camp_range(camp_type t) {
    switch (t) {
    case camp_type::wolf: return 3;
    case camp_type::elk: return 4;
    case camp_type::monolith: return 5;
    case camp_type::golem: return 4;
    default: return 3;
    }
}
