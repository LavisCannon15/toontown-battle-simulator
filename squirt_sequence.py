"""MovieSquirt target grouping and stagger (BattleBase: .5 / 1.0 seconds)."""
from direct.interval.IntervalGlobal import Sequence,Parallel,Wait

TOON_SQUIRT_DELAY=.5
TOON_SQUIRT_SUIT_DELAY=1.0

def schedule(event):
 groups={}
 for action in event.get('actions',[]):
  targets=event.get('targets',{}).get(action.toon,[])
  if targets:groups.setdefault(targets[0],[]).append(action)
 return [(action,group*TOON_SQUIRT_SUIT_DELAY+slot*TOON_SQUIRT_DELAY)
         for group,actions in enumerate(sorted(groups.values(),key=len))
         for slot,action in enumerate(actions)]

def movie(app,event):
 from audited_gags import squirt
 clips=[];last={};first={};hit_contacts={};geyser_seen=False
 for action,delay in schedule(event):
  targets=event['targets'][action.toon]
  contacts={}
  if action.gag=='Geyser':
   single=dict(event,actions=[action],health=[],scheduled_geyser=True,suppress_health=True,geyser_clone=geyser_seen)
   geyser_seen=True
   clip=app.geyser_movie(single);contacts=single['geyser_contacts'];contact=2.9
  else:clip,contact=squirt(app,action,targets,event.get('misses',[]))
  clips.append(Sequence(Wait(delay),clip))
  for target in targets:
   at=delay+contacts.get(target,contact)
   hit_contacts.setdefault(target,[]).append((at,action.toon))
   if action.gag=='Storm Cloud' and target not in event.get('misses',[]) and any(k=='cog' and i==target and n<0 for k,i,n in event.get('health',[])):
    reaction_event=dict(event,actions=[action])
    clips.append(Sequence(Wait(at),app.cog_damage_reaction(reaction_event,target)))
   if target not in last or at>=last[target][0]:last[target]=(at,action)
   dodge=delay+(contacts.get(target,2.9)-1.1 if action.gag=='Geyser' else 2.1 if action.gag=='Fire Hose' else max(0,contact-.5))
   if target not in first or at<first[target][0]:first[target]=(at,dodge)
 # Split the clamped total across actual contacts and delayed bonuses.
 # Older recorded events retain their aggregate fallback.
 for target in {i for kind,i,n in event.get('health',[]) if kind=='cog'}:
  at,action=last.get(target,(0,None))
  health=dict(event,health=[h for h in event['health'] if h[0]=='cog' and h[1]==target],misses=[])
  if action is not None:
   health['actions']=[action]
   if action.gag in ('Geyser','Storm Cloud'):health['custom_cog_reaction']=True
  from hit_damage import movie as damage_movie
  damage=damage_movie(app,health,target,hit_contacts.get(target,[]))
  clips.append(damage if damage is not None else app.health_movie(health,at))
 for target in set(event.get('misses',[])):
  at,dodge=first.get(target,(0,0))
  clips.append(app.health_movie(dict(event,health=[],misses=[target],dodge_at=dodge),at))
 return Parallel(*clips)
