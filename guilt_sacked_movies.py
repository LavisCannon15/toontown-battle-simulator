"""Classic doGuiltTrip and doSacked using bundled art and reference sequencing."""
from panda3d.core import Vec3,Vec4
from direct.interval.IntervalGlobal import Sequence,Parallel,Func,Wait,ActorInterval,LerpPosInterval,LerpHprInterval,LerpScaleInterval,LerpColorScaleInterval
from battle_movies import MOVIES
from classic_cog_movies import appear,arc,TOON_SCALE


def movie(app,event):
 i=event['cog'];name=event['name'];actor=app.cog_actors[i];root=app.cog_nodes[i]
 anim=MOVIES['suits'][app.game.cogs[i].name]['attacks'][name];native=actor.getDuration(anim);clips=[];heading=Vec3(root.getHpr())
 if name=='Guilt Trip':
  center=Vec4(1,.2,.2,.9);edge=Vec4(.9,.9,.9,.4)
  def colors(effect):
   for system in effect.getParticlesList():system.renderer.setCenterColor(center);system.renderer.setEdgeColor(edge)
  for h in (-90,90):
   effect=app.source_particle('guiltTrip',i);effect.setPos(0,6.1,.4);effect.setHpr(h,0,0);effect.setScale(5);colors(effect)
   clips.append(Sequence(Wait(.7),Func(effect.start,actor),Wait(.4),LerpPosInterval(effect,1,Vec3(0,15,.4)),LerpColorScaleInterval(effect,.4,Vec4(1,1,1,0)),Func(effect.disable)))
  waterfall=app.source_particle('waterfall',i);waterfall.setScale(11);colors(waterfall)
  clips.append(Sequence(Wait(.6),Func(waterfall.start,actor),Wait(.6),Func(waterfall.softStop),Wait(.5),Func(waterfall.disable)))
  clips.extend([Sequence(Wait(1.1),app.sound_clip('SA_guilt_trip.ogg')),app.health_movie(dict(event,reaction='slip-forward',dodge='jump',dodge_at=.86),1.5)])
  face=Wait(0)
 else:
  target=event['targets'][0];toon=app.toon_nodes[target];hit=target not in event['misses'];sack,_=app.movie_prop('sandbag',None,pose_frame=None)
  release=2.98;arrival=3.88;scale=Vec3(1.05,1.67,.98)*(4.1*TOON_SCALE);hpr=Vec3(-154.33,-6.33,163.8)
  # The extracted bag's bind geometry is larger than the classic prop.
  # Fit its oriented bounds around this Toon, preserving the source rotation
  # and nonuniform scale proportions instead of burying the mesh underground.
  lo,hi=app.toon_actors[target]['legs'].getTightBounds(toon);toon_height=hi.z-lo.z
  sack.setHpr(hpr);sack.setScale(scale);lo,hi=sack.getTightBounds()
  scale*=toon_height*1.08/max(.001,hi.z-lo.z)
  sack.setScale(scale);lo,hi=sack.getTightBounds();center=(lo+hi)*.5
  sack.setHpr(0,0,0);sack.setScale(1)
  def point():
   base=toon.getPos(app.render)
   if hit:return base+Vec3(0,0,toon_height*.5)-center
   return base+Vec3(0,0,-.2*TOON_SCALE)
  path=Sequence(appear(sack,actor.find('**/joint_Rhold'),(.51,-2.03,-.73),(90,-24.98,77.73),(.65,1.47,1.28),.85,grow=.2),Wait(1.93),Func(sack.wrtReparentTo,app.render))
  if hit:
   path.append(Parallel(arc(sack,point,.9),LerpScaleInterval(sack,.9,scale),LerpHprInterval(sack,.9,hpr)))
   path.append(Func(sack.wrtReparentTo,app.toon_actors[target]['legs'].find('**/joint_hips')))
   # One visible Toon LOD needs one bag; preserve world placement at attachment.
   path.append(Parallel(Wait(2.4),Sequence(Wait(1.8),LerpScaleInterval(sack,.3,.001))))
  else:path.append(arc(sack,point,.9));path.append(Wait(1.1));path.append(LerpScaleInterval(sack,.3,.001))
  path.append(Func(sack.hide));clips.append(path)
  tracks=[]
  if hit:
   parts=list(app.toon_actors[target].values())
   r=Sequence(Wait(.01),Parallel(*(ActorInterval(a,'struggle',startTime=.01,duration=.7) for a in parts if 'struggle' in a.getAnimNames())),Wait(.01),Parallel(*(ActorInterval(a,'slip-backward',startTime=.45) for a in parts if 'slip-backward' in a.getAnimNames())))
   def idle():
    if app.game.toons[target].alive:app.play_toon_animation(target,'idle',True)
   r.append(Func(idle))
   def start():
    if not app.game.toons[target].alive:return
    tracks.append(r);app.live_departures=getattr(app,'live_departures',[])+[r];r.start()
   clips.append(Sequence(Wait(arrival),Func(start),Wait(r.getDuration())))
  clips.append(app.health_movie(dict(event,reaction='struggle',custom_toon_reaction=True,custom_toon_tracks=tracks,dodge='sidestep-left',dodge_at=3),5.68 if hit else 3.8))
  def aim():root.headsUp(toon);root.setH(root.getH()-actor.getH())
  face=Func(aim)
 duration=max(native,*[c.getDuration() for c in clips])
 clips.extend([Sequence(face,ActorInterval(actor,anim),Wait(duration-native),Func(root.setHpr,heading),Func(app.restore_cog_pose,i)),app.attack_caption(i,name,duration)])
 return Parallel(*clips)
