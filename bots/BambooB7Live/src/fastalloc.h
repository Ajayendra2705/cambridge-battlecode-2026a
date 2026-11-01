#pragma once
// Size-class free-list allocator behind global operator new/delete. wasi-libc's malloc/free cost 200-385 fuel a pair
// (measured Oct 19); a free-list pop/push costs ~20. With it, 10 local maps vs starter: fuel exhaustions after round 100
// 228 -> 61 (lanes 145 -> 32). Single-threaded (one bot instance per WASM store). Blocks up to
// kMaxSmall bytes come from 256 KB slabs and are recycled by size class, never returned to malloc; larger blocks go
// to malloc. Every block carries a 16-byte header holding its class (0: malloc'd), so unsized deletes work.
#include <cstddef>
#include <cstdint>
#include <cstdlib>
#include <new>

namespace fastalloc {

constexpr std::size_t kAlign = 16;                  // wasm32 max_align_t
constexpr std::size_t kClasses = 64;                // classes of 16..1024 bytes
constexpr std::size_t kMaxSmall = kAlign * kClasses;
constexpr std::size_t kSlab = 256 * 1024;
constexpr std::size_t kLarge = 0;                   // header class of a malloc'd block
constexpr std::size_t kAligned = ~std::size_t{0};   // header class of an over-aligned malloc'd block

struct FreeNode {
    FreeNode* next;
};

inline FreeNode* free_list[kClasses + 1] = {};
inline char* bump = nullptr;
inline char* bump_end = nullptr;

inline void* allocate(std::size_t n) {
    const std::size_t c = n == 0 ? 1 : (n + kAlign - 1) / kAlign;
    if (c > kClasses) {
        char* base = static_cast<char*>(std::malloc(n + kAlign));
        if (!base) throw std::bad_alloc();
        *reinterpret_cast<std::size_t*>(base) = kLarge;
        return base + kAlign;
    }
    if (FreeNode* f = free_list[c]) {
        free_list[c] = f->next;
        return f;
    }
    const std::size_t need = (c + 1) * kAlign;  // header + block
    if (bump == nullptr || static_cast<std::size_t>(bump_end - bump) < need) {
        bump = static_cast<char*>(std::malloc(kSlab));
        if (!bump) throw std::bad_alloc();
        bump_end = bump + kSlab;
    }
    char* base = bump;
    bump += need;
    *reinterpret_cast<std::size_t*>(base) = c;
    return base + kAlign;
}

inline void deallocate(void* p) noexcept {
    if (!p) return;
    char* base = static_cast<char*>(p) - kAlign;
    const std::size_t c = *reinterpret_cast<std::size_t*>(base);
    if (c == kLarge) {
        std::free(base);
        return;
    }
    if (c == kAligned) {
        std::free(*reinterpret_cast<void**>(base + sizeof(std::size_t)));
        return;
    }
    auto* f = static_cast<FreeNode*>(p);
    f->next = free_list[c];
    free_list[c] = f;
}

// Over-aligned requests (alignof > 16): malloc with room to align, remembering the original pointer in the header.
inline void* allocate_aligned(std::size_t n, std::size_t align) {
    if (align <= kAlign) return allocate(n);
    char* raw = static_cast<char*>(std::malloc(n + align + kAlign));
    if (!raw) throw std::bad_alloc();
    std::uintptr_t user = (reinterpret_cast<std::uintptr_t>(raw) + kAlign + align - 1) & ~(static_cast<std::uintptr_t>(align) - 1);
    char* base = reinterpret_cast<char*>(user) - kAlign;
    *reinterpret_cast<std::size_t*>(base) = kAligned;
    *reinterpret_cast<void**>(base + sizeof(std::size_t)) = raw;
    return reinterpret_cast<void*>(user);
}

}  // namespace fastalloc

// Replaceable global allocation functions (one definition each: include this header in exactly one .cpp file).
void* operator new(std::size_t n) { return fastalloc::allocate(n); }
void* operator new[](std::size_t n) { return fastalloc::allocate(n); }
void* operator new(std::size_t n, const std::nothrow_t&) noexcept {
    try { return fastalloc::allocate(n); } catch (...) { return nullptr; }
}
void* operator new[](std::size_t n, const std::nothrow_t&) noexcept {
    try { return fastalloc::allocate(n); } catch (...) { return nullptr; }
}
void* operator new(std::size_t n, std::align_val_t a) { return fastalloc::allocate_aligned(n, static_cast<std::size_t>(a)); }
void* operator new[](std::size_t n, std::align_val_t a) { return fastalloc::allocate_aligned(n, static_cast<std::size_t>(a)); }
void operator delete(void* p) noexcept { fastalloc::deallocate(p); }
void operator delete[](void* p) noexcept { fastalloc::deallocate(p); }
void operator delete(void* p, std::size_t) noexcept { fastalloc::deallocate(p); }
void operator delete[](void* p, std::size_t) noexcept { fastalloc::deallocate(p); }
void operator delete(void* p, std::align_val_t) noexcept { fastalloc::deallocate(p); }
void operator delete[](void* p, std::align_val_t) noexcept { fastalloc::deallocate(p); }
void operator delete(void* p, std::size_t, std::align_val_t) noexcept { fastalloc::deallocate(p); }
void operator delete[](void* p, std::size_t, std::align_val_t) noexcept { fastalloc::deallocate(p); }
void operator delete(void* p, const std::nothrow_t&) noexcept { fastalloc::deallocate(p); }
void operator delete[](void* p, const std::nothrow_t&) noexcept { fastalloc::deallocate(p); }
