"""TNT choreography from MovieTrap/MovieLure, using bundled TTR resources.

The lab uses medium Toon bodies and a compact battlefield. Clip offsets and
audio segments follow the classic reference; world distances use lab units.
"""
from panda3d.core import Vec3,Vec4
from direct.actor.Actor import Actor
from direct.interval.IntervalGlobal import (
 Sequence,Parallel,Func,Wait,ActorInterval,LerpFunc,LerpHprInterval,LerpScaleInterval)
from game_resources import resource

RELEASE=2.5  # Medium torso: 2.3 second toss lead-in + .2 second TNT delay.
FLIGHT=.9
LANDING=RELEASE+FLIGHT

def placement(app,action,targets):
 from audited_gags import perform
 from trap_movies import sync,trap_position
 clips=[perform(app,action.toon,'toss')]
 for index in targets:
  prop,_=app.movie_prop('tnt',None)
  hand=app.toon_actors[action.toon]['torso'].find('**/joint_Rhold')
  cog=app.cog_nodes[index]
  target=trap_position(app,index,6)
  heading=app.cog_actors[index].getH(app.render)
  state={}
  def hold(prop=prop,hand=hand):
   prop.reparentTo(hand);prop.setPos(0,0,0);prop.setHpr(0,0,0);prop.setScale(1);prop.show()
  def release(prop=prop,state=state):
   prop.wrtReparentTo(app.render);state['origin']=Vec3(prop.getPos())
  def arc(t,prop=prop,state=state,target=target):
   # MovieTrap.createThrowingTrack's parabola, scaled to the lab's Toon size.
   origin=state['origin'];pos=origin+(target-origin)*t
   pos.z+=.5*32.144*.62*FLIGHT**2*t*(1-t)
   prop.setPos(pos)
  clips.append(Sequence(Func(hold),Wait(RELEASE),Func(release),
   Parallel(LerpFunc(arc,fromData=0,toData=1,duration=FLIGHT),
            LerpHprInterval(prop,FLIGHT,Vec3(heading,90,0)),
            LerpScaleInterval(prop,FLIGHT,.6)),Func(prop.hide)))
  # The placement uses a short segment of dynamite audio, not a pie throw.
  clips.append(Sequence(Wait(RELEASE+.8),app.sound_clip('TL_dynamite.ogg',.7)))
 clips.append(Sequence(Wait(LANDING),Func(sync,app,targets)))
 return Parallel(*clips)

def activation(app,event,index,trap_root,trap_actor,land):
 """Starts when the Cog reaches the trap; the sound/reaction clock is shared."""
 actor=app.cog_actors[index]
 original_color=Vec4(actor.getColorScale());had_color=actor.hasColorScale()
 def restore():
  if actor.isEmpty():return
  if had_color:actor.setColorScale(original_color)
  else:actor.clearColorScale()
 app.movie_restorers=getattr(app,'movie_restorers',[])+[restore]
 def detonate():
  actor.setColorScale(.2,.2,.2,1)
  if trap_root and not trap_root.isEmpty():trap_root.hide()
 # Native forward/reverse frames place the recoil at 2.3 seconds.
 body=Sequence(ActorInterval(actor,'flail',duration=.7),
  ActorInterval(actor,'flail',startTime=.7,endTime=0),
  ActorInterval(actor,'idle',duration=.4),
  ActorInterval(actor,'flail',startTime=.6,endTime=.7),Wait(.4),
  ActorInterval(actor,'slip-forward',startTime=2.48,duration=.1),
  Func(detonate),ActorInterval(actor,'slip-forward',startTime=2.58),
  Func(restore),Func(app.restore_cog_pose,index))
 kapow=Actor(str(resource('kapow-mod.bam')),{'kapow':str(resource('kapow-chan.bam'))})
 kapow.setName('tnt-kapow')
 kapow.reparentTo(app.render);kapow.setPos(land+Vec3(0,0,2.3*.6));kapow.setScale(.11)
 kapow.setBillboardPointEye();kapow.setLightOff();kapow.hide()
 app.movie_props.append((kapow,kapow))
 health=dict(event,health=[h for h in event['health'] if h[0]=='cog' and h[1]==index],misses=[],custom_cog_reaction=True)
 clips=[body,app.health_movie(health,2.3),
  Sequence(Wait(2.3),Func(kapow.show),ActorInterval(kapow,'kapow'),Func(kapow.hide)),
  Sequence(app.sound_clip('TL_dynamite.ogg',2),app.sound_clip('ENC_cogfall_apart.ogg',.6))]
 if trap_actor:clips.append(ActorInterval(trap_actor,'prop'))
 return Parallel(*clips)
