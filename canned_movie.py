"""Classic doCanned: arcing can, hit attachment and miss bounces."""
from panda3d.core import Vec3
from direct.interval.IntervalGlobal import Sequence,Parallel,Func,Wait,ActorInterval,LerpPosInterval,LerpScaleInterval,LerpHprInterval
from classic_cog_movies import appear,arc,TOON_SCALE
from battle_movies import MOVIES


def movie(app,event):
 i=event['cog'];target=event['targets'][0];actor=app.cog_actors[i];root=app.cog_nodes[i];toon=app.toon_nodes[target];hit=target not in event['misses']
 spec=MOVIES['suits'][app.game.cogs[i].name];anim=spec['attacks']['Canned'];native=actor.getDuration(anim);body_c='suitC' in spec['anims'][anim]
 release=2.43 if body_c else 3.13;arrival=release+1.5;dodge=3.1 if body_c else 3.6
 can,_=app.movie_prop('can',None);hpr=Vec3(-173.47,-.42,162.09);scale=Vec3(2.63,2.63,1.7975)*(26*TOON_SCALE)
 lo,hi=app.toon_actors[target]['legs'].getTightBounds(toon);height=hi.z-lo.z
 # Fit the extracted can to the current Toon; old raw dimensions differ.
 can.setScale(scale);can.setHpr(hpr);lo,hi=can.getTightBounds();scale*=height*.8/max(.001,hi.z-lo.z)
 can.setScale(scale);lo,hi=can.getTightBounds();offset=(lo+hi)*.5;can.setHpr(0,0,0);can.setScale(1)
 def point():
  if hit:return toon.getPos(app.render)+Vec3(0,0,height*.4)-offset
  return toon.getPos(app.render)+Vec3(1.1*TOON_SCALE,-.5*TOON_SCALE,height+1.1*TOON_SCALE)
 path=Sequence(appear(can,actor.find('**/joint_Rhold'),(-.14,.15,.08),(-10.584,11.945,-161.684),(6,)*3,.8),Wait(release-1.3),Func(can.wrtReparentTo,app.render),Parallel(arc(can,point,1.5),LerpScaleInterval(can,1.5,scale if hit else 11*TOON_SCALE),LerpHprInterval(can,1.5,hpr)))
 if hit:
  path.append(Func(can.wrtReparentTo,app.toon_actors[target]['legs'].find('**/joint_hips')));path.append(Wait(2.4))
 else:
  # Ground bounce path and rotations from source, converted to scene scale.
  positions=[(0,0,.7),(0,-1.5,3.2),(0,-2.1,.5),(0,-3.1,2.2),(0,-4.1,1)]
  durations=[.4,.4,.3,.3,.3]
  bounce=Sequence()
  for pos,time in zip(positions,durations):bounce.append(LerpPosInterval(can,time,lambda p=Vec3(*pos):toon.getPos(app.render)+p*TOON_SCALE))
  spins=Sequence(Wait(.4),LerpHprInterval(can,.4,Vec3(83.27,19.52,-177.92)),LerpHprInterval(can,.3,Vec3(95.24,-72.09,88.65)),LerpHprInterval(can,.2,Vec3(-96.34,-2.63,179.89)))
  path.append(Parallel(bounce,spins));path.append(Wait(1.1));path.append(LerpScaleInterval(can,.3,.001))
 path.append(Func(can.hide));clips=[path];tracks=[]
 if hit:
  parts=list(app.toon_actors[target].values())
  r=Sequence(Parallel(*(ActorInterval(a,'struggle',startTime=.01,duration=.7) for a in parts if 'struggle' in a.getAnimNames())),Wait(.01),Parallel(*(ActorInterval(a,'slip-backward',startTime=.45) for a in parts if 'slip-backward' in a.getAnimNames())))
  def idle():
   if app.game.toons[target].alive:app.play_toon_animation(target,'idle',True)
  r.append(Func(idle))
  def start():
   if not app.game.toons[target].alive:return
   tracks.append(r);app.live_departures=getattr(app,'live_departures',[])+[r];r.start()
  clips.append(Sequence(Wait(arrival),Func(start),Wait(r.getDuration())))
 sound=Sequence(Wait(2.6),app.sound_clip('SA_canned_tossup_only.ogg'))
 if hit:sound.append(app.sound_clip('SA_canned_impact_only.ogg'))
 clips.extend([sound,app.health_movie(dict(event,custom_toon_reaction=True,custom_toon_tracks=tracks,reaction='struggle',dodge='sidestep-left',dodge_at=dodge),release+2.4 if hit else dodge+.5)])
 duration=max(native,*[c.getDuration() for c in clips]);heading=Vec3(root.getHpr())
 def face():root.headsUp(toon);root.setH(root.getH()-actor.getH())
 clips.extend([Sequence(Func(face),ActorInterval(actor,anim),Wait(duration-native),Func(root.setHpr,heading),Func(app.restore_cog_pose,i)),app.attack_caption(i,'Canned',duration)])
 return Parallel(*clips)
