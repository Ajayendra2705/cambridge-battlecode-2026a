// vtgroups.ts SINCE : Velvet Tributers' match groups created since SINCE (ISO), newest first: id kind created opponent ourWins theirWins ourVersion
const T = "118dbffc-87ec-48a6-ac9c-dc1e371ba364", B = "https://2026a.battlecode.co.uk/api/v1/match-groups";
const since = Deno.args[0]; let next = ""; const out: string[] = [];
for (let page = 0; page < 20; page++) {
  const d: any = await (await fetch(`${B}?team=${T}` + (next ? `&before=${encodeURIComponent(next)}` : ""))).json();
  let stop = false;
  for (const g of d.groups ?? []) {
    if (g.createdAt < since) { stop = true; break; }
    const us = g.sides.find((s: any) => s.teamId === T), them = g.sides.find((s: any) => s.teamId !== T);
    out.push([g.id, g.kind, g.createdAt.slice(0, 19), (them?.teamName ?? "?").replace(/\s+/g, "_"), us?.wins, them?.wins, us?.version ?? "-", g.status].join(" "));
  }
  if (stop || !d.more) break; next = d.next;
}
console.log(out.join("\n"));
