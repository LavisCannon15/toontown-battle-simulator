"""Schedule each hit and bonus while applying the engine's clamped total once."""
from direct.interval.IntervalGlobal import Parallel,Sequence,Wait

def schedule(event,target,contacts):
 powers=event.get('damage_by_action',{}).get(target)
 components=event.get('damage_components',{}).get(target)
 if not powers or not components:return None
 hits=sorted((at,toon,powers[toon]) for at,toon in contacts if toon in powers)
 if not hits:return None
 remaining=-sum(n for kind,i,n in event['health'] if kind=='cog' and i==target and n<0)
 rows=[]
 for j,(at,toon,power) in enumerate(hits):
  amount=min(remaining,power);remaining-=amount
  rows.append((at,power,amount,0,j==len(hits)-1,toon))
 at=hits[-1][0]
 for name,bonus in [('knockback',2),('combo',1)]:
  value=components.get(name,0)
  if value:
   at+=.75;amount=min(remaining,value);remaining-=amount
   rows.append((at,value,amount,bonus,False,hits[-1][1]))
 return rows

def movie(app,event,target,contacts):
 rows=schedule(event,target,contacts)
 if rows is None:return None
 clips=[]
 for at,value,amount,bonus,react,toon in rows:
  clips.append(Sequence(Wait(at),app.float_text(app.cog_nodes[target],-value,4,start=False,bonus=bonus)))
  if amount:
   single=dict(event,health=[('cog',target,-amount)],misses=[],suppress_damage_text=True,
               custom_cog_reaction=event.get('custom_cog_reaction',False) or not react)
   clips.append(app.health_movie(single,at))
 return Parallel(*clips)
