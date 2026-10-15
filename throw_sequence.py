"""Classic MovieThrow scheduling with bundled TTR props and animation clips.

BattleBase: TOON_THROW_DELAY=.5, TOON_THROW_SUIT_DELAY=1.0.
MovieThrow.doThrows: stable target groups sorted by count, then group pies.
The extracted TTR assets do not contain modern client sequencing code.
"""
from direct.interval.IntervalGlobal import Sequence,Parallel,Wait
from battle_engine import GAGS

def schedule(event):
 groups={};wide=[]
 for action in event.get('actions',[]):
  targets=event.get('targets',{}).get(action.toon,[])
  if not targets:continue
  if GAGS[action.gag].group:wide.append(action)
  else:groups.setdefault(targets[0],[]).append(action)
 return [(a,group*1.0+slot*.5)
         for group,actions in enumerate(sorted(groups.values(),key=len))
         for slot,a in enumerate(actions)],wide

def movie(app,event):
 from audited_gags import throw
 clips=[];last={};first={};contacts={};single_end=0
 ordered,wide=schedule(event)
 def add(action,delay):
  targets=event['targets'][action.toon]
  clip,contact=throw(app,action,targets,event.get('misses',[]))
  clips.append(Sequence(Wait(delay),clip))
  for target in targets:
   contacts.setdefault(target,[]).append((delay+contact,action.toon))
   last[target]=max(last.get(target,0),delay+contact)
   first[target]=min(first.get(target,float('inf')),delay)
  return delay+clip.getDuration()
 for action,delay in ordered:single_end=max(single_end,add(action,delay))
 # The reference deliberately plays group pies together, after single pies.
 for action in wide:add(action,single_end)
 # Attribute base hits to their contacts; bonuses follow the last contact.
 # Older recorded events without attribution retain the aggregate fallback.
 for target in {i for kind,i,n in event.get('health',[]) if kind=='cog'}:
  health=dict(event,health=[h for h in event['health'] if h[0]=='cog' and h[1]==target],misses=[])
  from hit_damage import movie as damage_movie
  damage=damage_movie(app,health,target,contacts.get(target,[]))
  clips.append(damage if damage is not None else app.health_movie(health,last.get(target,3)))
 for target in set(event.get('misses',[])):
  start=first.get(target,0)
  clips.append(app.health_movie(dict(event,health=[],misses=[target],dodge_at=start+2.45),start+3))
 return Parallel(*clips)
