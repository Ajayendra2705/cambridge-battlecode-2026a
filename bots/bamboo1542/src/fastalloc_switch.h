#pragma once
// bamboo8's free-list allocator (bb/fastalloc.h) behind a switch, for a program that holds several bots. The global
// operator new/delete live here; bb/fastalloc.h itself is not included anywhere. With the switch off (the default),
// every block comes from malloc with the same 16-byte header the allocator writes, so blocks made before main() sets
// the switch (static initialisers) are freed correctly either way. main() turns it on only for the bot that was
// tested with it (bamboo8), so the other bots allocate through malloc as they do alone.
#include <cstddef>
#include <cstdint>
#include <cstdlib>
#include <new>

namespace fastalloc {

constexpr std::size_t kAlign = 16;
constexpr std::size_t kClasses = 64;
constexpr std::size_t kSlab = 256 * 1024;
constexpr std::size_t kLarge = 0;
constexpr std::size_t kAligned = ~std::size_t{0};

struct FreeNode {
    FreeNode* next;
};

inline bool on = false;
inline FreeNode* free_list[kClasses + 1] = {};
inline char* bump = nullptr;
inline char* bump_end = nullptr;

inline void* allocate(std::size_t n) {
    if (n > static_cast<std::size_t>(-1) - 2 * kAlign - 16) throw std::bad_alloc();
    const std::size_t c = n == 0 ? 1 : (n + kAlign - 1) / kAlign;
    if (!on || c > kClasses) {
        char* base = static_cast<char*>(std::malloc(n + kAlign));
        if (!base) throw std::bad_alloc();
        *reinterpret_cast<std::size_t*>(base) = kLarge;
        return base + kAlign;
    }
    if (FreeNode* f = free_list[c]) {
        free_list[c] = f->next;
        return f;
    }
    const std::size_t need = (c + 1) * kAlign;
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

// Replaceable global allocation functions (this header is included by main.cpp only).
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
