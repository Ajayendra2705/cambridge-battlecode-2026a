// winsum.ts GROUPFILE : per version window (by group creation time) and kind, games, wins, margin and opponents, for Velvet Tributers
const T = "118dbffc-87ec-48a6-ac9c-dc1e371ba364", B = "https://2026a.battlecode.co.uk";
const W: [string, string, string][] = [["v1470", "01:51", "02:11"], ["v1475", "02:11", "03:03"], ["v1476", "03:03", "04:11"], ["v1469 G3", "04:11", "07:21"],
  ["v1472", "07:21", "08:04"], ["v1477 H", "08:04", "08:32"], ["v1478", "08:32", "23:59"]];
const acc = new Map<string, { n: number; w: number; m: number; opp: Map<string, [number, number]> }>();
const lines = (await Deno.readTextFile(Deno.args[0])).split("\n").filter(Boolean);
await Promise.all(lines.map(async (l) => {
  const [gid, kind, created] = l.split(" ");
  const hm = created.slice(11, 16); if (created.slice(0, 10) !== "2026-11-01") return;
  const v = W.find(([, a, b]) => hm >= a && hm < b); if (!v) return;
  const d: any = await (await fetch(`${B}/api/v1/match-groups/${gid}`)).json();
  for (const m of d.matches ?? []) {
    const f = m.sides.findIndex((s: any) => s.teamId === T); if (f < 0 || m.status !== "finished") continue;
    const key = `${v[0]} ${kind}`; if (!acc.has(key)) acc.set(key, { n: 0, w: 0, m: 0, opp: new Map() });
    const a = acc.get(key)!; const won = m.sides[f].result === "win" ? 1 : 0; a.n++; a.w += won; a.m += m.sides[f].score - m.sides[1 - f].score;
    const o = m.sides[1 - f].teamName; const x = a.opp.get(o) ?? [0, 0]; x[0]++; x[1] += won; a.opp.set(o, x);
  }
}));
for (const [k, a] of [...acc].sort()) {
  const top = [...a.opp].sort((x, y) => y[1][0] - x[1][0]).slice(0, 6).map(([o, [n, w]]) => `${o.slice(0, 14)} ${w}/${n}`).join(", ");
  console.log(`${k.padEnd(22)} games ${String(a.n).padStart(3)} wins ${String(a.w).padStart(3)} (${Math.round(100 * a.w / a.n)}%) margin/game ${Math.round(a.m / a.n)} | ${top}`);
}
