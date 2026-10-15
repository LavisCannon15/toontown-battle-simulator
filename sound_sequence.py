"""MovieSound level grouping adapted to the simulator's aggregated Sound damage."""
from direct.interval.IntervalGlobal import Sequence,Parallel,Wait,Func,ActorInterval,LerpPosInterval
from panda3d.core import Vec3
import random
from battle_engine import GAGS

TOON_SOUND_DELAY=1.0

def schedule(actions):
 levels=sorted({GAGS[a.gag].level for a in actions})
 # Classic __doSoundsLevel wraps the movie with Wait(delay); each instrument
 # also waits delay internally. Our instrument builder has no internal offset.
 offsets={level:2*slot*TOON_SOUND_DELAY for slot,level in enumerate(levels)}
 return [(a,offsets[GAGS[a.gag].level]) for a in sorted(actions,key=lambda a:GAGS[a.gag].level)]

def movie(app,event):
 from audited_gags import sound
 clips=[];impact=0;opera_targets=set()
 for action,delay in schedule(event.get('actions',[])):
  clip,_=sound(app,action,event.get('targets',{}).get(action.toon,[]),event.get('misses',[]))
  retreat=any(event.get('lure_before',[])[i] for i in event.get('targets',{}).get(action.toon,[]) if i<len(event.get('lure_before',[])))
  if retreat:clip=step_back(app,action.toon,clip)
  clips.append(Sequence(Wait(delay),clip))
  # tSuitReact=2.8; Opera adds its delayed glass-breaking impact.
  impact=max(impact,delay+(.5 if retreat else 0)+2.8+(2 if GAGS[action.gag].level==7 else 0))
  if GAGS[action.gag].level==7:opera_targets.update(event.get('targets',{}).get(action.toon,[]))
 # The engine supplies one track total. Apply it once, after the last group,
 # rather than repeatedly subtracting that total for each instrument.
 # MovieSound.__getSuitTrack plays glass once per hit Cog, not per singer.
 # Its random impact offset is presentation-only and must not consume battle RNG.
 hit_targets={i for kind,i,amount in event.get('health',[]) if kind=='cog' and amount<0}
 glass_targets=opera_targets & hit_targets - set(event.get('misses',[]))
 if glass_targets:
  if not hasattr(app,'presentation_rng'):app.presentation_rng=random.Random()
  for target in sorted(glass_targets):
   contact=impact+app.presentation_rng.random()
   clips.append(Sequence(Wait(contact),app.sound_clip('AA_sound_Opera_Singer_Cog_Glass.ogg')))
   clips.append(app.health_movie(dict(event,health=[h for h in event['health'] if h[0]=='cog' and h[1]==target],misses=[]),contact))
  remaining=dict(event,health=[h for h in event['health'] if h[0]!='cog' or h[1] not in glass_targets])
  clips.append(app.health_movie(remaining,impact))
 else:clips.append(app.health_movie(event,impact))
 return Parallel(*clips)


def step_back(app,index,performance):
 """MovieSound __createToonInterval, converted to this scene's .62 scale."""
 node=app.toon_nodes[index];origin=Vec3(node.getPos());back=origin+Vec3(0,-2.6*.75*.62,0)
 def walk(reverse):
  return Parallel(*(ActorInterval(actor,'walk',startTime=1 if reverse else .0001,
                    endTime=.0001 if reverse else 1,duration=.5)
                    for actor in app.toon_actors[index].values() if 'walk' in actor.getAnimNames()))
 def restore():
  if not node.isEmpty():node.setPos(origin)
 app.movie_restorers=getattr(app,'movie_restorers',[])+[restore]
 return Sequence(Parallel(walk(True),LerpPosInterval(node,.5,back)),performance,
                 Parallel(walk(False),LerpPosInterval(node,.5,origin)),
                 Func(app.play_toon_animation,index,'idle',True))
