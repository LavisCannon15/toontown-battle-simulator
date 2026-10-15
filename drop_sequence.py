"""MovieDrop target-group ordering; shared engine health is applied once per target."""
from direct.interval.IntervalGlobal import Sequence,Parallel,Wait
from battle_engine import GAGS

def schedule(event):
 groups={};wide=[]
 for a in sorted(event.get('actions',[]),key=lambda a:GAGS[a.gag].level):
  if GAGS[a.gag].group:wide.append(a)
  else:
   targets=event.get('targets',{}).get(a.toon,[])
   if targets:groups.setdefault(targets[0],[]).append(a)
 result=[]
 for slot,actions in enumerate(sorted(groups.values(),key=len)):
  result.extend((a,slot*1.0+i*.8) for i,a in enumerate(actions))
 return result,wide

def movie(app,event):
 from audited_gags import drop
 clips=[];impacts={};missed=set();latest=0
 ordered,wide=schedule(event)
 for a,delay in ordered:
  targets=event['targets'][a.toon]
  clip,impact=drop(app,a,targets,event.get('misses',[]),react_miss=not any(i in missed for i in targets))
  missed.update(i for i in targets if i in event.get('misses',[]))
  clips.append(Sequence(Wait(delay),clip));latest=max(latest,delay+clip.getDuration())
  for i in targets:impacts[i]=max(impacts.get(i,0),delay+impact)
 for slot,a in enumerate(wide):
  targets=event['targets'][a.toon];delay=latest+slot
  clip,impact=drop(app,a,targets,event.get('misses',[]))
  clips.append(Sequence(Wait(delay),clip))
  for i in targets:impacts[i]=max(impacts.get(i,0),delay+impact)
 # Damage is already aggregated by track in the engine. Keep that total intact,
 # showing it on the final applicable impact instead of duplicating it per prop.
 for i in {i for kind,i,n in event['health'] if kind=='cog'}:
  health=dict(event,health=[h for h in event['health'] if h[0]=='cog' and h[1]==i],misses=[],custom_cog_reaction=True)
  clips.append(app.health_movie(health,impacts.get(i,4.3)))
 return Parallel(*clips)
