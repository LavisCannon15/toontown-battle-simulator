"""High Dive stages from MovieHeal.__healDive; preserve native climb root motion."""
from panda3d.core import Vec3,Vec4
from direct.interval.IntervalGlobal import Sequence,Parallel,Func,Wait,ActorInterval,LerpPosInterval,LerpScaleInterval,LerpColorScaleInterval

def movie(app,index):
 node=app.toon_nodes[index];geom=app.toon_actors[index]['legs'];scale=Vec3(geom.getScale());state={}
 ladder,_=app.movie_prop('ladder',None);glass,_=app.movie_prop('glass',None,pose_frame=None)
 splash,actor=app.movie_prop('splashdown',None)
 def initialize():
  state['origin']=Vec3(node.getPos());state['hpr']=Vec3(node.getHpr())
  def point(offset):return app.render.getRelativePoint(node,Vec3(*offset))
  state['climb']=point((0,4+scale.z/.66,0));state['swim']=point((0,1.2,.2))
  ladder.setPos(point((0,4,0)));ladder.setH(node.getH());ladder.setScale(.001);ladder.show()
  glass.setPos(point((0,1.1,.2)));glass.setHpr(0,90,0);glass.setScale(4);glass.show()
  splash.setPos(glass.getPos()+Vec3(0,0,-.01));splash.setScale(.4)
 def native(anim,**kwargs):return Parallel(*(ActorInterval(a,anim,**kwargs) for a in app.toon_actors[index].values() if anim in a.getAnimNames()))
 def face_ladder():
  # The walk ends beyond the ladder base. Turn back toward the rungs
  # before native climb root motion; keeping the approach heading faces away.
  target=ladder.getPos(node.getParent());target.z=node.getZ();node.headsUp(target)
 def restore():
  geom.setScale(scale);geom.clearTransparency();geom.clearColorScale();node.setPos(state['origin']);node.setHpr(state['hpr']);app.play_toon_animation(index,'idle',True)
 props=Sequence(LerpScaleInterval(ladder,1.5,Vec3(.5,.5,.45)*(scale.z/.66)),Wait(6.4),LerpScaleInterval(ladder,1.5,.001),Func(ladder.hide),Func(glass.hide))
 dive=Sequence(Wait(4.6),Func(geom.setTransparency,1),LerpColorScaleInterval(geom,.25,Vec4(1,1,1,0)),LerpScaleInterval(geom,.01,.1),Func(lambda:node.setHpr(state['hpr'])),Func(lambda:node.setPos(state['swim'])),Func(geom.clearTransparency),Func(geom.clearColorScale),native('swim',startTime=0,endTime=1))
 body=Sequence(Parallel(Sequence(native('walk',duration=1),Wait(.1)),LerpPosInterval(node,1,lambda:state['climb']),Wait(1.5)),Sequence(Func(face_ladder),Parallel(native('climb',endFrame=116),dive,Sequence(Wait(4.6),Func(splash.show),ActorInterval(actor,'prop',duration=1),Func(splash.hide)))),Wait(.5),Parallel(native('jump',startTime=.2),LerpScaleInterval(geom,.5,scale)),Func(restore))
 return Sequence(Func(initialize),Parallel(props,body))
