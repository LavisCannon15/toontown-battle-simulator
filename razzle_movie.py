"""MovieSuitAttacks.doRazzleDazzle: smile sign and travelling sparkle ring."""
from panda3d.core import Vec3
from direct.interval.IntervalGlobal import Sequence,Parallel,Func,Wait,ActorInterval,LerpPosInterval,LerpScaleInterval

def movie(app,event):
 index=event['cog'];actor=app.cog_actors[index];root=app.cog_nodes[index]
 target=event['targets'][0];toon=app.toon_nodes[target];heading=Vec3(root.getHpr())
 sign,animated=app.movie_prop('smile',None);hand=actor.find('**/joint_Rhold')
 effect=app.source_particle('smile',index)
 def face():
  root.headsUp(toon);root.setH(root.getH()-actor.getH())
 def show():
  sign.reparentTo(hand);sign.setPos(0,-.42,-.04);sign.setHpr(105.715,73.977,65.932);sign.setScale(1);sign.show()
 def destination():
  end=toon.getPos(app.render)+Vec3(0,0,2.5)
  if target in event['misses']:
   direction=end-effect.getPos(app.render)
   if direction.length():end+=direction.normalized()*5
  return end
 native=actor.getDuration('smile');duration=max(native,4)
 event=dict(event,reaction='cringe',dodge='sidestep-left',dodge_at=1.9)
 return Sequence(Parallel(
  Sequence(Func(face),ActorInterval(actor,'smile'),Func(root.setHpr,heading),Func(app.restore_cog_pose,index)),
  app.attack_caption(index,event['name'],duration),
  Sequence(Wait(.5),Func(show),LerpScaleInterval(sign,.5,1.39),Wait(.5),Func(effect.start,sign),Func(effect.wrtReparentTo,app.render),LerpPosInterval(effect,2,destination),Func(effect.disable)),
  ActorInterval(animated,'prop',duration=4,startTime=0),
  Sequence(Wait(1.6),app.sound_clip('SA_razzle_dazzle.ogg')),
  app.health_movie(event,2.6)),Func(sign.hide))
