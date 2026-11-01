// mkpanel.ts GROUPFILE FROM TO OUTSPEC OUTIDS : the unranked groups created in [FROM, TO) (HH:MM, Nov 1) as a bench2qs panel - spec lines
// "<opponent team id> <map1,..,map5> --sides <s1,..,s5>" (our side per game) and their group ids as the source groups (same opponent bots)
const T = "118dbffc-87ec-48a6-ac9c-dc1e371ba364", B = "https://2026a.battlecode.co.uk";
const [file, from, to, outSpec, outIds] = Deno.args; const spec: string[] = [], ids: string[] = [];
for (const l of (await Deno.readTextFile(file)).split("\n").filter(Boolean).reverse()) {
  const [gid, kind, created] = l.split(" "); const hm = created.slice(11, 16);
  if (kind !== "unranked" || created.slice(0, 10) !== "2026-11-01" || hm < from || hm >= to) continue;
  const d: any = await (await fetch(`${B}/api/v1/match-groups/${gid}`)).json();
  const ms = (d.matches ?? []); if (ms.length !== 5) continue;
  const opp = ms[0].sides.find((s: any) => s.teamId !== T)?.teamId; if (!opp) continue;
  const maps = ms.map((m: any) => m.map), sides = ms.map((m: any) => m.sides.find((s: any) => s.teamId === T)?.side ?? "a");
  spec.push(`${opp} ${maps.join(",")} --sides ${sides.join(",")}`); ids.push(gid);
}
await Deno.writeTextFile(outSpec, spec.join("\n") + "\n"); await Deno.writeTextFile(outIds, ids.join("\n") + "\n");
console.log(spec.length, "groups");
