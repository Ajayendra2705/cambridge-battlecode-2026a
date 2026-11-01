import { ReplayEngine } from '../replay/replay_engine.ts';
const eng = await ReplayEngine.create();
const names=['Ryth','Vesper','Vendetta','Cassi','Issac','Stellar','Prism','Marcella','Willow','Ren','Varg','Tavi','HoR'];
for(const match of [{map:'m',id:'x'}]){
 const dir=Deno.args[0], game=eng.load(Deno.readFileSync(dir+'/replay.repl26a'));
 const out:any={map:match.map,id:match.id,groups:{},champions:{},rounds:[],actions:[],recalls:[],damage:[],income:[],final:null};
 let prev:any=null, round=-1, lastKey='';
 const channels=new Map<number,any>();
 const compact=(c:any)=>({id:c.entity.index,team:c.team,name:names[c.type],p:c.position,hp:c.health,mx:c.maxHealth,alive:c.alive,gold:Number(c.gold),earned:Number(c.earnedGold),gems:Number(c.gems),channel:c.channelType,timer:c.channelTimer,range:c.attackRange,str:c.strength.effective,focus:c.focus.effective,items:c.items});
 game.walk((h:any,s:any)=>{
  const key=`${h.inputPosition}:${h.round}:${h.step.substep}`;if(key===lastKey)return;lastKey=key;
  for(const c of s.camps){if(c.position){
   const g=out.groups[c.group]??={tiles:[],members:[],type:[]};
   if(!g.members.includes(c.entity.index)){g.members.push(c.entity.index);g.tiles.push(c.position);g.type.push(c.type);}
  }}
  for(const c of s.champions){const id=c.entity.index;
   if(!out.champions[id])out.champions[id]={id,team:c.team,name:names[c.type],spawn:c.position};
   const old=prev?.champions.find((x:any)=>x.entity.index===id);
   if(old && Number(c.earnedGold)>Number(old.earnedGold))out.income.push({id,r:h.round,input:h.inputPosition,sub:h.step.substep,gold:Number(c.earnedGold)-Number(old.earnedGold),treasure:Number(c.treasureGold)-Number(old.treasureGold),prospector:Number(c.prospectorGold)-Number(old.prospectorGold)});
   if(c.channelType===1 && old?.channelType!==1){channels.set(id,{id,r:h.round,input:h.inputPosition,p:c.position,hp:c.health/maybe(c.maxHealth),gold:Number(c.gold),gems:Number(c.gems),timer:c.channelTimer});}
   if(c.channelType!==1 && channels.has(id)){
    const e=channels.get(id);out.recalls.push({...e,end:h.round,endInput:h.inputPosition,endP:c.position,alive:c.alive,endHp:c.health/maybe(c.maxHealth)});channels.delete(id);
   }
  }
  if(h.round!==round && s.champions.length){round=h.round;out.rounds.push({r:round,ch:s.champions.map(compact),bank:h.submittedGems.map(Number),groups:s.groups.map((g:any)=>({reward:g.rewardAvailable,respawn:g.respawnTimer}))});}
  const st=h.step, actor=st.actor?.kind===1?st.actor.index:null;
  if(actor!==null&&st.phase===10&&[4,5,6,23].includes(st.kind)){
   let gid=null;for(const [g,v] of Object.entries(out.groups) as any){if(v.tiles.some((p:any)=>p.x===st.to.x&&p.y===st.to.y)){gid=Number(g);break;}}
   out.actions.push({r:h.round,input:h.inputPosition,id:actor,kind:st.kind,from:st.from,to:st.to,group:gid,slot:st.abilitySlot});
  }
  if(prev){for(let j=0;j<s.camps.length;j++){
   const c=s.camps[j],p=prev.camps[j];if(!p)continue;
   const loss=Math.max(0,p.health-c.health);if(loss>0)out.damage.push({r:h.round,input:h.inputPosition,group:c.group,member:c.entity.index,amount:loss,actor:st.phase===10&&[5,6].includes(st.kind)?actor:null,kind:st.kind});
  }}
  prev=s;out.final={round:h.round,outcome:h.outcome,bank:h.submittedGems.map(Number),ch:s.champions.map(compact)};
 },()=>true);
 for(const e of channels.values())out.recalls.push({...e,end:null});
 game.destroy();
 Deno.writeTextFileSync(dir+'/trace.json',JSON.stringify(out));
 console.log(JSON.stringify({map:match.map,rounds:out.rounds.length,actions:out.actions.length,damage:out.damage.length,recalls:out.recalls.length,final:out.final.round,outcome:out.final.outcome,bank:out.final.bank}));
}
function maybe(n:number){return Math.max(n,1);}
