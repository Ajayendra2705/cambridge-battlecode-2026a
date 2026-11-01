# pairsum.awk: benchcmp.ts output for two tags -> wins and margin over the games both tags played (paired). Result tokens are "W 123",
# "L -45" or, when the padded margin fills the field, "L-1000" (no space).
function take(   v) {
  v = $i
  if (v == "W" || v == "L") { res = v; mar = $(i + 1); i += 2; return 1 }
  if (v ~ /^[WL]-?[0-9]+$/) { res = substr(v, 1, 1); mar = substr(v, 2); i += 1; return 1 }
  i += 1; return 0
}
NF >= 4 && $1 != "game" && $1 != "wins" && $1 != "margin" {
  i = 4; ok1 = take(); r1 = res; m1 = mar
  ok2 = take(); r2 = res; m2 = mar
  if (ok1 && ok2) { n++; w1 += (r1 == "W"); w2 += (r2 == "W"); s1 += m1; s2 += m2 }
}
END { printf "paired %d games: wins %d %d margin %d %d\n", n, w1, w2, s1, s2 }
