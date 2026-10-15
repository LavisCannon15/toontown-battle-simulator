"""Classic MovieFire cannon choreography adapted to the battle stage's scale."""
import math
from panda3d.core import Vec3,Vec4,TransparencyAttrib
from direct.actor.Actor import Actor
from direct.interval.IntervalGlobal import Sequence,Parallel,Func,Wait,ActorInterval,LerpPosInterval,LerpScaleInterval,LerpHprInterval,LerpColorScaleInterval
from game_resources import SOURCE

def movie(app,action,event,caller_clip=None):
 index=action.target;root=app.cog_nodes[index];suit=app.cog_actors[index]
 holder=root.attachNewNode('fire-cannon');holder.setH(getattr(action,'cannon_heading',180));holder.hide()
 cannon=app.loader.loadModel(str(SOURCE/'toon_cannon.bam'));cannon.reparentTo(holder);cannon.setScale(.35);cannon.setZ(-8.6*.35)
 barrel=cannon.find('**/cannon');barrel.setP(90);barrel.setScale(1.6,1,1.6)
 attach=barrel.attachNewNode('CannonAttach');attach.setScale(1/1.6,1,1/1.6);attach.setY(6.7)
 burst=barrel.attachNewNode('kapowAttach');burst.setPos(0,-.5,1.9)
 kapow=Actor(str(SOURCE/'kapow-mod.bam'),{'kapow':str(SOURCE/'kapow-chan.bam')});kapow.reparentTo(burst);kapow.setScale(.25);kapow.setBillboardPointEye();kapow.hide()
 smoke=app.loader.loadModel(str(SOURCE/'test_clouds.bam'));smoke.reparentTo(attach);smoke.setScale(.5);smoke.setBillboardPointEye();smoke.setTransparency(TransparencyAttrib.MAlpha);smoke.hide()
 app.movie_props.extend([(holder,None),(kapow,kapow)])
 scale=Vec3(suit.getScale());hpr=Vec3(suit.getHpr());level=app.game.cogs[index].level
 def insert():
  holder.show();suit.reparentTo(attach);suit.setPos(0,0,0);suit.setHpr(0,-90,0);suit.setScale(scale/.35);suit.show()
  if getattr(action,'preserve_cog_facing',False):suit.setHpr(root,hpr)
 def remove():
  suit.reparentTo(root);suit.setPos(0,0,0);suit.setHpr(hpr);suit.setScale(scale);suit.hide();root.hide();holder.hide()
 adjust=lambda pitch:Parallel(LerpHprInterval(barrel,.6,Vec3(0,pitch,0),blendType='easeIn'),app.sound_clip('MG_cannon_adjust.ogg',.6))
 mechanism=Sequence(LerpPosInterval(holder,2,Vec3(0,0,2.45),blendType='easeInOut'),adjust(45),Wait(2),adjust(90),LerpPosInterval(holder,1,Vec3(0),blendType='easeInOut'))
 loading=Parallel(ActorInterval(suit,'flail'),LerpScaleInterval(suit,1,scale/.35*(.9-math.sqrt(level)*.1)),Sequence(LerpPosInterval(suit,.25,Vec3(0,-1,0)),Parallel(app.sound_clip('ENC_cogafssm.ogg',1.5),LerpPosInterval(suit,1.5,Vec3(0,-(2.5+level*.2),0),blendType='easeIn'))))
 cloud=Sequence(Func(smoke.show),Parallel(LerpScaleInterval(smoke,.5,3),LerpColorScaleInterval(smoke,.5,Vec4(2,2,2,0))),Func(smoke.hide))
 launch=Sequence(Wait(2.5),Parallel(cloud,Sequence(Func(kapow.show),ActorInterval(kapow,'kapow'),Func(kapow.hide)),app.sound_clip('MG_cannon_fire_alt.ogg',1),app.sound_clip('firework_whistle_01.ogg',3),LerpPosInterval(suit,3,Vec3(0,150,0)),LerpScaleInterval(suit,3,.01)),Func(suit.hide))
 effects=[mechanism,loading,launch,app.health_movie(dict(event,custom_cog_reaction=True),0)]
 if caller_clip is None:
  stars=Actor(str(SOURCE/'stun-mod.bam'),{'stun':str(SOURCE/'stun-chan.bam')})
  stars.reparentTo(suit.find('**/joint_head'));stars.setZ(.5);stars.hide();app.movie_props.append((stars,stars))
  effects.append(Sequence(Wait(.3),Func(stars.show),ActorInterval(stars,'stun',loop=1,duration=1.3),Func(stars.hide)))
 response=Sequence(Func(insert),Parallel(*effects),Func(remove))
 if caller_clip is not None:return Sequence(caller_clip,response)
 toon=app.toon_nodes[action.toon];heading=Vec3(toon.getHpr())
 def face():toon.headsUp(root.getPos())
 def native(name):
  return Parallel(*(ActorInterval(actor,name) for actor in app.toon_actors[action.toon].values() if name in actor.getAnimNames()))
 for part,actor in app.toon_actors[action.toon].items():
  stem='avt_dog' if part=='head' else 'dgm_'+part
  if 'wave' not in actor.getAnimNames():actor.loadAnims({'wave':str(SOURCE/f'ttr_a_chr_{stem}_wave.bam')})
 button,ba=app.movie_prop('button',None);hand=app.toon_actors[action.toon]['torso'].find('**/joint_Lhold')
 def show_button():button.reparentTo(hand);button.setPos(0,0,0);button.setHpr(0,0,0);button.setScale(.01);button.show()
 prop=Sequence(Func(show_button),LerpScaleInterval(button,1,1),Wait(2.5),LerpScaleInterval(button,1,.01),Func(button.hide))
 caller=Sequence(Func(face),native('pushbutton'),app.toon_clip(action.toon,'wave',2),native('duck'),Func(app.play_toon_animation,action.toon,'idle',True),Func(toon.setHpr,heading))
 return Parallel(caller,prop,Sequence(Wait(2.15),app.sound_clip('AA_drop_trigger_box.ogg',.8)),Sequence(Wait(3),response))
