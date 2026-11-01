// games.ts : one row per game for Velvet Tributers' groups in groups_since2330.txt, version from banners.txt, plus the panel tag of the group
const SP = Deno.args[0], B = "https://2026a.battlecode.co.uk";
const ver = new Map<string, string>();
for (const l of (await Deno.readTextFile(`${SP}/dash/banners.txt`)).split("\n")) { const [g, m, ...v] = l.trim().split(/\s+/); if (m) ver.set(m, v.join(" ").replace("BAMBOO ", "")); }
const tagOf = new Map<string, string>();
for (const [t, lab] of [["q1472_top", "panel"], ["q1472_fn", "panel"], ["q1473_top", "panel"], ["q1473_fn", "panel"], ["q1470_top", "panel"]]) {
  try { for (const id of (await Deno.readTextFile(`${SP}/scrim_${t}.ids`)).split(/\s+/).filter(Boolean)) tagOf.set(id, lab); } catch { /* none */ }
}
const rows: any[] = [];
for (const l of (await Deno.readTextFile(`${SP}/dash/groups_since2330.txt`)).split("\n")) {
  const [gid, kind, created] = l.trim().split(/\s+/); if (!gid) continue;
  const d: any = await (await fetch(`${B}/api/v1/match-groups/${gid}`)).json();
  for (const m of d.matches ?? []) {
    const f = m.sides.findIndex((s: any) => s.teamName === "Velvet Tributers"); if (f < 0 || m.status !== "finished") continue;
    const v = ver.get(m.id) ?? "?";
    rows.push({ match: m.id, group: gid, kind: kind === "ranked" ? "ranked" : (tagOf.has(gid) ? "panel scrim" : "other scrim"), created: created.replace("T", " ") + " UTC",
      version: v === "none" ? "v1470" : v, opponent: m.sides[1 - f].teamName, map: m.map, side: "ab"[f], won: m.sides[f].result === "win" ? 1 : 0,
      margin: m.sides[f].score - m.sides[1 - f].score });
  }
}
console.log(JSON.stringify(rows));
