"""MovieSquirt.__doStormCloud stages, using bundled cloud channels and rain sprites."""
from panda3d.core import Vec3
from direct.interval.IntervalGlobal import Sequence,Parallel,Func,Wait,ActorInterval,LerpScaleInterval
from audited_gags import perform,cue,sound_for

def movie(app,action,targets,misses):
 duration=app.toon_actors[action.toon]['torso'].getDuration('pushbutton')
 clips=[perform(app,action.toon,'pushbutton'),app.hand_prop(action.toon,'button',duration)]
 missed=bool(targets) and all(i in misses for i in targets)
 clips.extend(cue(app,sound_for('Squirt',6,missed),t) for t in (2.3,4.6))
 for index in targets:
  cloud,actor=app.movie_prop('stormcloud',None)
  suit=app.cog_actors[index];size=suit.getScale(app.render).z
  height=3.5+.06*app.game.cogs[index].level
  cloud.setPos(app.cog_nodes[index].getPos()+Vec3(0,0,height+3*size));cloud.setScale(.001)
  hold=1.7 if index in misses else 4.7;trickle=hold*.25
  def rain(name,start,length):
   effect=app.source_particle(name,index)
   return Sequence(Wait(start),Func(effect.start,cloud),Wait(length),Func(effect.softStop),Wait(.4),Func(effect.disable))
  # Source: scale in 1.5, wait 1, trickle, stagger three rain emitters,
  # then play the cloud channel from second 1 at native speed.
  heavy=Parallel(*(rain('liquidate',trickle+n*.3,hold-2*trickle) for n in range(3)),Sequence(Wait(.9),ActorInterval(actor,'prop',startTime=1,duration=hold)))
  storm=Sequence(Func(cloud.show),Func(actor.pose,'prop',0),LerpScaleInterval(cloud,1.5,3*size),Wait(1),Parallel(rain('trickleLiquidate',0,trickle),Sequence(Wait(trickle),heavy)),LerpScaleInterval(cloud,.5,.001),Func(cloud.hide))
  clips.append(storm)
 return Parallel(*clips),2.9
