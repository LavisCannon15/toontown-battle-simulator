"""Embezzle hit/miss presentation with TTR assets; modern timing is reconstructed."""
from panda3d.core import Vec3,Vec4
from direct.interval.IntervalGlobal import Sequence,Parallel,Func,Wait,ActorInterval,LerpPosInterval,LerpScaleInterval,LerpHprInterval,LerpColorScaleInterval
from game_resources import resource

def movie(app,event):
 index=event['cog'];actor=app.cog_actors[index];root=app.cog_nodes[index];target=event['targets'][0]
 heading=Vec3(root.getHpr());hand=actor.find('**/joint_Rhold');hit=target not in event['misses']
 def face():root.headsUp(app.toon_nodes[target]);root.setH(root.getH()-actor.getH())
 duration=actor.getDuration('pickpocket');impact=.85
 event=dict(event,reaction='cringe',dodge='jump',dodge_at=.25)
 clips=[Sequence(Func(face),ActorInterval(actor,'pickpocket'),Func(root.setHpr,heading),Func(app.restore_cog_pose,index)),app.attack_caption(index,event['name'],duration),app.health_movie(event,impact),Sequence(Wait(.2),app.sound_clip('ttr_s_ene_bat_embezzle.ogg'))]
 if hit:
  bill,animated=app.movie_prop('1dollar',None)
  def show():
   bill.reparentTo(hand);bill.setPos(-.01,.45,-.25);bill.setHpr(136.424,-46.434,-129.712);bill.setScale(1.41);bill.show()
  # Preserve the bill's resting mesh instead of playing the fishing-lure channel.
  clips.append(Sequence(Wait(impact),Func(show),Wait(1.25),LerpScaleInterval(bill,.3,.001),Func(bill.hide)))
  art=app.loader.loadModel(str(resource('phase_3.5/models/props/suit-particles.bam')))
  app.movie_props.append((art,None));sprite=art.find('**/dollar-sign')
  for n in range(5):
   dollar=sprite.copyTo(app.render);dollar.setName('embezzle-dollar-sign');dollar.setScale(.25);dollar.setBillboardPointEye();dollar.setLightOff();dollar.setTransparency(1);dollar.hide();app.movie_props.append((dollar,None))
   def launch(node=dollar,n=n):node.setPos(hand.getPos(app.render)+Vec3((n%3-1)*.18,0,.2));node.show()
   clips.append(Sequence(Wait(1.05+n*.12),Func(launch),Parallel(LerpPosInterval(dollar,.75,lambda node=dollar:node.getPos()+Vec3(0,0,1.1)),LerpColorScaleInterval(dollar,.75,Vec4(1,1,1,0))),Func(dollar.hide)))
 return Parallel(*clips)
