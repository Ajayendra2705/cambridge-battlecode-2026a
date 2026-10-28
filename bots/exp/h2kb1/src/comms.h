// Part of bot.cpp: Shared memory: target claims, help call, respawn broadcast. Bit layout documented inline.
// Unity build: bot.cpp includes this inside its anonymous namespace; not a standalone header.

// ---- Shared memory ----
int read_byte(int i) {
    std::byte b{};
    cambc::shared_memory.read(i, std::span{&b, 1});
    return static_cast<int>(b);
}
void write_byte(int i, int v) {
    std::byte b{static_cast<unsigned char>(v)};
    cambc::shared_memory.write(i, std::span{&b, 1});
}

// Layout: bytes 0-4 hold six 6-bit claims (group + 1); bytes 5-6 broadcast an observed respawn (group + 1,
// respawn round low byte); byte 7 holds a coarse enemy sighting ((x / 7 + 1) << 4 | y / 7).
std::array<int, MAX_SLOTS> claim_cache{};
int my_claim = -1;
std::array<std::byte, 8> shared_cache{};

std::uint64_t claim_bits() {
    std::uint64_t bits = 0;
    for (int i = 0; i < 5; ++i) bits |= static_cast<std::uint64_t>(shared_cache[i]) << (8 * i);
    return bits;
}

void refresh_claims() {
    cambc::shared_memory.read(0, std::span{shared_cache});
    const auto bits = claim_bits();
    for (int s = 0; s < MAX_SLOTS; ++s)
        claim_cache[s] = s < W.team_count && s != W.slot ? static_cast<int>(bits >> (6 * s) & 63) - 1 : -1;
}

// Bytes 0-4 hold every champion's claim and the help call, so each write reads them again first: on a dead turn (no
// knowledge stage) or a turn resumed after running out of fuel the cache is from an earlier round, and writing it back put
// teammates' claims and the help call back to older values; an owner does not rewrite a claim it thinks it holds (probe
// h2pr1l, 18 local games: 17 of 33 dead-turn writes reverted a teammate's claim, ghosts lasted up to 39 rounds).
void reload_claim_word() { cambc::shared_memory.read(0, std::span{shared_cache.data(), 5}); }

void write_claim(int group) {
    if (W.slot >= MAX_SLOTS || group == my_claim) return;
    my_claim = group;
    reload_claim_word();
    auto bits = claim_bits();
    bits &= ~(std::uint64_t{63} << (6 * W.slot));
    bits |= static_cast<std::uint64_t>((group + 1) & 63) << (6 * W.slot);
    for (int i = 0; i < 5; ++i) shared_cache[i] = static_cast<std::byte>(bits >> (8 * i) & 0xff);
    cambc::shared_memory.write(0, std::span{shared_cache.data(), 5});
}

// Help call in the claim word's spare bits 30-39 (slot 5 is unused with five champions): a champion caught by an
// enemy on our half writes its position in cells of `help_res` tiles ((x / r) * rows + y / r + 1, 0 = none); teammates
// nearby come to turn a 2v1 into a 2v2. Platform gb2 vs ranks 40-49: early deaths on our half start as ~1 ally
// vs 1.1 enemies within 5 and end as 0.7 vs 2.1, half with no ally left within 5.
// The cell size is the smallest of 3 or more that fits the map into 10 bits. The old fixed 3-tile code with 22 rows
// assumed maps of at most 66 tiles: on 8 of the 40 maps (100x100, 80x80, 90x30, 30x80, 71x71, 61x71) calls far out
// were ignored or decoded to the wrong place (from (20, 80) on a 100x100 map to (22, 13)).
int help_res() {
    int r = 3;
    while (((cm::width() + r - 1) / r) * ((cm::height() + r - 1) / r) + 1 > 1023) ++r;
    return r;
}
int help_rows() { return (cm::height() + help_res() - 1) / help_res(); }
int my_help = 0;
void write_help(int v) {
    if (W.team_count > 5 || v == my_help) return;
    my_help = v;
    reload_claim_word();
    auto bits = claim_bits();
    bits &= ~(std::uint64_t{1023} << 30);
    bits |= static_cast<std::uint64_t>(v & 1023) << 30;
    for (int i = 0; i < 5; ++i) shared_cache[i] = static_cast<std::byte>(bits >> (8 * i) & 0xff);
    cambc::shared_memory.write(0, std::span{shared_cache.data(), 5});
}
int help_code(vec2 p) { return (p.x / help_res()) * help_rows() + p.y / help_res() + 1; }
// The called position (the centre of its cell), or (-1, -1) when there is no call (or it is our own).
vec2 read_help() {
    if (W.team_count > 5) return {-1, -1};
    const int v = static_cast<int>(claim_bits() >> 30 & 1023);
    const int r = help_res(), rows = help_rows(), cols = (cm::width() + r - 1) / r;
    if (v == 0 || v == my_help || v > cols * rows) return {-1, -1};
    const int q = v - 1;
    vec2 h{std::min((q / rows) * r + r / 2, cm::width() - 1), std::min((q % rows) * r + r / 2, cm::height() - 1)};
    return h;
}
// Our half or the middle: walking distance from our spawn at most 4 more than from theirs.
bool home_side(vec2 t) {
    const int a = W.spawn_field.get(t), b = W.enemy_field.get(t);
    return a != UNREACH && b != UNREACH && a - b <= 4;
}

// Tell teammates when a group was seen going down, so nobody walks to it before it is back.
int last_broadcast = -1;
void broadcast_respawn(int group, int respawn_round) {
    const int key = group * 4096 + respawn_round;
    if (key == last_broadcast) return;
    last_broadcast = key;
    write_byte(5, group + 1);
    write_byte(6, respawn_round & 0xff);
}

void read_broadcast() {
    const int g = static_cast<int>(shared_cache[5]) - 1;
    if (g < 0 || g >= static_cast<int>(W.groups.size())) return;
    // Rebuild the full round from its low byte: the nearest value not long past.
    int r = (S.round & ~0xff) | static_cast<int>(shared_cache[6]);
    if (r < S.round - 64) r += 256;
    if (r > S.round + 192) r -= 256;
    // Once the respawn has passed the broadcast says nothing, and left in place it decoded 65-255 rounds later as a respawn
    // 256 rounds after the real one: every champion out of view of that group then held it as respawning until then (probe
    // h2pr1l, 18 local games: twice, once 00eight's north double elk from r395 to r586). Clear it.
    if (r <= S.round) {
        if (!stale()) write_byte(5, 0), shared_cache[5] = std::byte{0};
        return;
    }
    auto& grp = W.groups[g];
    if (r > S.round && (grp.state == 0 || grp.respawn_round != r)) {
        bool seen = false;
        for (auto sp : grp.spawns) if (in_view(sp)) { seen = true; break; }
        if (!seen) {
            grp.state = 2;
            grp.respawn_round = r;
            std::fill(grp.hp.begin(), grp.hp.end(), 0.0f);
        }
    }
}
int claimants(int group) {
    int n = 0;
    for (int s = 0; s < MAX_SLOTS; ++s)
        if (claim_cache[s] == group) ++n;
    return n;
}
