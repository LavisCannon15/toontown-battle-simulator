"""Classic doBrainStorm with bundled cloud, three sprites and native channels."""
from panda3d.core import Vec3,Vec4
from direct.interval.IntervalGlobal import Sequence,Parallel,Func,Wait,ActorInterval,LerpPosInterval,LerpScaleInterval
from classic_cog_movies import appear,TOON_SCALE
from battle_movies import MOVIES
from game_resources import resource


def movie(app,event):
 index=event['cog'];target=event['targets'][0];actor=app.cog_actors[index];root=app.cog_nodes[index];toon=app.toon_nodes[target]
 anim=MOVIES['suits'][app.game.cogs[index].name]['attacks']['Brain Storm'];native=actor.getDuration(anim)
 cloud,channel=app.movie_prop('stormcloud',None)
 art=app.loader.loadModel(str(resource('phase_3.5/models/props/suit-particles.bam')));art.hide();app.movie_props.append((art,None))
 effects=[]
 for n,texture in enumerate(['brainstorm-box','brainstorm-env','brainstorm-track']):
  sprite=art.find('**/'+texture);effect=app.source_particle('brainStorm',index);effect.setName(texture)
  for system in effect.getParticlesList():system.renderer.setFromNode(sprite);system.renderer.setColor(Vec4(.65,.79,.93,.85))
  effects.append(Sequence(Wait(n*.5),Func(effect.start,cloud),Wait(2.2-n*.5),Func(effect.disable)))
 effects.append(Sequence(ActorInterval(channel,'prop',startTime=3,duration=.5),ActorInterval(channel,'prop',startTime=2.5,duration=.5),ActorInterval(channel,'prop',startTime=1,duration=1.5)))
 lo,hi=actor.getTightBounds(actor);height=hi.z-lo.z
 def detach():cloud.wrtReparentTo(app.render)
 def destination():return app.render.getRelativePoint(toon,Vec3(0,0,2+3*TOON_SCALE))
 path=Sequence(Func(channel.pose,'prop',0),appear(cloud,actor,(0,3,height+3),(180,0,0),(3,)*3,.000001,grow=.7),Func(detach),Wait(1.1),LerpPosInterval(cloud,1,destination),Wait(1.2),Parallel(*effects),Wait(.4),LerpScaleInterval(cloud,.5,.001),Func(cloud.hide))
 duration=max(path.getDuration(),native+.9);heading=Vec3(root.getHpr())
 def face():root.headsUp(toon);root.setH(root.getH()-actor.getH())
 return Parallel(path,Sequence(Func(face),Wait(.9),ActorInterval(actor,anim),Wait(duration-native-.9),Func(root.setHpr,heading),Func(app.restore_cog_pose,index)),app.attack_caption(index,'Brain Storm',duration),app.health_movie(dict(event,reaction='cringe',dodge='sidestep-left',dodge_at=3.3),4.4 if target in event['misses'] else 4.5),Sequence(Wait(2.6),app.sound_clip('SA_brainstorm.ogg')))
