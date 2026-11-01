// benchcmp.ts TAG... : bench results per tag (scrim_TAG.ids): per game "opp map" our margin, then wins and margin sum
// per tag; games keyed by opponent+map so tags line up.
const B = "https://2026a.battlecode.co.uk";
const SP = new URL(".", import.meta.url).pathname.replace(/^\/([A-Za-z]:)/, "$1");
const tags = Deno.args;
const table = new Map<string, Map<string, string>>();
const tot: Record<string, { w: number; n: number; m: number; pending: number }> = {};
for (const t of tags) {
  tot[t] = { w: 0, n: 0, m: 0, pending: 0 };
  const ids = (await Deno.readTextFile(`${SP}/scrim_${t}.ids`)).split(/\s+/).filter(Boolean);
  for (const id of ids) {
    // deno-lint-ignore no-explicit-any
    const d: any = await (await fetch(`${B}/api/v1/match-groups/${id}`)).json();
    for (const m of d.matches ?? []) {
      // deno-lint-ignore no-explicit-any
      const f = m.sides.findIndex((s: any) => (s.teamName === "Bamboo Teahouse" || s.teamName === "Velvet Tributers"));
      const opp = String(m.sides[1 - f]?.teamName ?? "?").replace(/[^A-Za-z0-9]/g, "").slice(0, 10);
      const key = `${opp.padEnd(10)} ${String(m.map).padEnd(11)} ${"ab"[f]}`;
      if (!table.has(key)) table.set(key, new Map());
      if (m.status !== "finished") { table.get(key)!.set(t, "  ..."); tot[t].pending++; continue; }
      const margin = m.sides[f].score - m.sides[1 - f].score;
      const won = m.sides[f].result === "win";
      table.get(key)!.set(t, `${won ? "W" : "L"}${String(margin).padStart(5)}`);
      tot[t].n++; tot[t].m += margin; if (won) tot[t].w++;
    }
  }
}
console.log("game".padEnd(22), tags.map((t) => t.padStart(7)).join(" "));
for (const [k, row] of [...table].sort()) console.log(k, tags.map((t) => (row.get(t) ?? "     -").padStart(7)).join(" "));
console.log("wins".padEnd(22), tags.map((t) => `${tot[t].w}/${tot[t].n}`.padStart(7)).join(" "));
console.log("margin".padEnd(22), tags.map((t) => String(tot[t].m).padStart(7)).join(" "), tags.some((t) => tot[t].pending) ? "(pending games)" : "");
