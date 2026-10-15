"""Money Talks presentation reconstructed from documented TTR behavior.
The phase files supply jargon art and distinct sounds, not the modern movie code;
wall spacing and cue timing below remain an explicit approximation.
"""
from panda3d.core import Vec3
from direct.interval.IntervalGlobal import Sequence,Parallel,Func,Wait,ActorInterval,LerpPosInterval,LerpScaleInterval
from game_resources import resource

def movie(app,event):
 i=event['cog'];actor=app.cog_actors[i];root=app.cog_nodes[i];wall=app.render.attachNewNode('money-talks-wall');wall.hide();app.movie_props.append((wall,None))
 art=app.loader.loadModel(str(resource('phase_3.5/models/props/suit-particles.bam')));art.hide();app.movie_props.append((art,None))
 names=['jargon-brow','jargon-deep','jargon-hoop','jargon-ipo'];targets=event['targets']
 center=sum((app.toon_nodes[t].getPos(app.render) for t in targets),Vec3())/len(targets)
 width=max(3,max(app.toon_nodes[t].getX(app.render) for t in targets)-min(app.toon_nodes[t].getX(app.render) for t in targets)+2)
 for row in range(3):
  for column in range(5):
   word=art.find('**/'+names[(column+row)%4]).copyTo(wall);word.setName('money-talks-jargon');word.setColor(0,.85,.15,1);word.setLightOff();word.setBillboardPointEye();word.setTwoSided(True)
   lo,hi=word.getTightBounds();word.setScale(.62/max(hi.x-lo.x,hi.z-lo.z,.01));word.setPos((column-2)*width/4,0,(row-1)*.55)
 def launch():
  right=actor.find('**/joint_Rhold');left=actor.find('**/joint_Lhold')
  wall.setPos((right.getPos(app.render)+left.getPos(app.render))*.5);wall.setScale(.01);wall.show()
 destination=center+Vec3(0,0,1.9);duration=max(5,actor.getDuration('speak'))
 hit=any(t not in event['misses'] for t in targets)
 return Parallel(Sequence(ActorInterval(actor,'speak'),Wait(max(0,duration-actor.getDuration('speak'))),Func(app.restore_cog_pose,i)),app.attack_caption(i,'Money Talks',duration),
  Sequence(Wait(1),Func(launch),LerpScaleInterval(wall,.4,1),LerpPosInterval(wall,1.4,destination),LerpPosInterval(wall,.5,destination+Vec3(0,-2,0)),LerpScaleInterval(wall,.2,.001),Func(wall.hide)),
  Sequence(Wait(1),app.sound_clip('ttr_s_ene_bat_moneyTalks.ogg' if hit else 'ttr_s_ene_bat_moneyTalksMiss.ogg')),
  app.health_movie(dict(event,reaction='conked',dodge='duck',dodge_at=2.1),2.8))
