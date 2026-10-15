"""Explicit classic MovieSuitAttacks sequences using bundled TTR models.
Reference distances are converted to the simulator's .62 Toon scene scale.
"""
from panda3d.core import Vec3,Vec4
from direct.interval.IntervalGlobal import (Sequence,Parallel,Func,Wait,ActorInterval,
 LerpPosInterval,LerpScaleInterval,LerpFunc,LerpColorScaleInterval)
from battle_movies import MOVIES
from game_resources import resource

TOON_SCALE=.62

def appear(prop,parent,pos,hpr,scale,delay,grow=.5,start=.01):
 def show():
  prop.reparentTo(parent);prop.setPos(*pos);prop.setHpr(*hpr);prop.show()
 return Sequence(Wait(delay),Func(show),LerpScaleInterval(prop,grow,Vec3(*scale),startScale=Vec3(start)))

def vanish(prop,hold,grow=.5):
 return Sequence(Wait(hold),LerpScaleInterval(prop,grow,.001),Func(prop.hide))

def arc(prop,target,duration):
 values={}
 def start():values['origin']=Vec3(prop.getPos());values['target']=Vec3(target())
 def update(t):
  p=values['origin']*(1-t)+values['target']*t
  p.z+=.5*32.144*TOON_SCALE*duration*duration*t*(1-t)
  prop.setPos(p)
 return Sequence(Func(start),LerpFunc(update,fromData=0,toData=1,duration=duration))

def movie(app,event):
 i=event['cog'];actor=app.cog_actors[i];root=app.cog_nodes[i];name=event['name']
 target=event['targets'][0];toon=app.toon_nodes[target];hit=target not in event['misses']
 right=actor.find('**/joint_Rhold');left=actor.find('**/joint_Lhold')
 anim=MOVIES['suits'][app.game.cogs[i].name]['attacks'][name]
 body_a='suitA' in MOVIES['suits'][app.game.cogs[i].name]['anims'][anim]
 impact={'Bounce Check':5.1 if body_a else 4.4,'Red Tape':3.4,'Write Off':3.4,'Liquidate':3.5}[name]
 dodge={'Bounce Check':4.3 if body_a else 3.6,'Red Tape':2.8,'Write Off':2.4,'Liquidate':2.45}[name]
 event=dict(event,reaction={'Bounce Check':'conked','Red Tape':'struggle','Write Off':'slip-forward','Liquidate':'melt'}[name],dodge='jump' if name=='Red Tape' else 'sidestep-left',dodge_at=dodge)
 clips=[]
 def sound(file,t,length=None):clips.append(Sequence(Wait(t),app.sound_clip(file,length)))
 def point(height=0,forward=0):return app.render.getRelativePoint(toon,Vec3(0,forward,height))
 if name=='Bounce Check':
  check,_=app.movie_prop('bounced-check',None);release=3.0 if body_a else 2.3
  def detach():check.wrtReparentTo(app.render);check.setHpr(toon,0,-90,0)
  path=Sequence(appear(check,right,(0,0,0),(95.247,79.025,88.849),(8.5,)*3,.00001,start=1),Wait(release-.5),Func(detach),
   arc(check,lambda:point(0,8*TOON_SCALE),.5),arc(check,lambda:point(0,5*TOON_SCALE),.9),arc(check,lambda:point(2 if hit else 0),.7))
  if not hit:path.append(arc(check,lambda:point(0,-5*TOON_SCALE),.7));path.append(LerpScaleInterval(check,.3,.001))
  path.append(Func(check.hide));clips.append(path)
  sound('SA_pink_slip.ogg',release);sound('SA_pink_slip.ogg',release+1)
 elif name=='Red Tape':
  tape,_=app.movie_prop('redtape',None)
  x=-.24 if app.game.cogs[i].name=='Two-Face' else .24
  def detach():tape.wrtReparentTo(app.render)
  clips.append(Sequence(appear(tape,right,(x,.09,-.38),(-1.152,86.581,-76.784),(.9,.9,.24),.8),Wait(1.73),Func(detach),LerpPosInterval(tape,.5,lambda:point(1.2 if hit else 0,.7*TOON_SCALE if not hit else 0)),Func(tape.hide)))
  if hit:
   tube,_=app.movie_prop('redtape-tube',None)
   hips=app.toon_actors[target]['legs'].find('**/joint_hips')
   # One rendered Toon LOD: one tube, rather than the source's three LOD copies.
   tube_pos=(0,0,-.87) if app.game.toons[target].animal in ('dog','horse') else (0,0,-.8)
   tube_scale=(1.69,1.69,.67) if app.game.toons[target].animal in ('dog','horse') else (2.03,2.03,.7975)
   body_scale={'mouse':.6,'cat':.73,'duck':.66,'bunny':.74,'horse':.85,'dog':.85,'monkey':.68,'bear':.85,'pig':.77}.get(app.game.toons[target].animal,.73)
   tube_scale=tuple(v*body_scale for v in tube_scale)
   clips.append(Sequence(appear(tube,hips,tube_pos,(0,0,0),tube_scale,3.25),vanish(tube,3.17)))
  sound('SA_red_tape.ogg',2.9)
 elif name=='Write Off':
  pad,_=app.movie_prop('pad',None);pencil,_=app.movie_prop('pencil',None)
  clips.append(Sequence(appear(pad,left,(-.25,1.38,-.08),(-19.078,-6.603,-171.594),(1.89,)*3,.5),vanish(pad,2.57)))
  clips.append(Sequence(appear(pencil,right,(-.47,1.08,.28),(21.045,12.702,-176.374),(1.5,)*3,.5),vanish(pencil,2.8)))
  art=app.loader.loadModel(str(resource('phase_3.5/models/props/suit-particles.bam')));app.movie_props.append((art,None))
  mark=art.find('**/checkmark').copyTo(app.render);mark.setName('write-off-checkmark');mark.setBillboardPointEye();mark.setLightOff();mark.hide();app.movie_props.append((mark,None));art.hide()
  def launch():mark.setPos(pencil.getPos(app.render));mark.setScale(1.6*TOON_SCALE);mark.show()
  clips.append(Sequence(Wait(3),Func(launch),LerpPosInterval(mark,.5,lambda:point(2,0)+Vec3(1.8 if not hit else 0,0,0)),Func(mark.hide)))
  sound('SA_writeoff_pen_only.ogg',2.3,.9);sound('SA_writeoff_ding_only.ogg',3.2)
 elif name=='Liquidate':
  cloud,channel=app.movie_prop('stormcloud',None)
  # Suit-local height is converted from the rendered model's bounds.
  lo,hi=actor.getTightBounds(actor);height=hi.z-lo.z
  def detach():cloud.wrtReparentTo(app.render)
  rain=[]
  for delay,length in ((0,2.1),(.1,2),(.1,2)):
   effect=app.source_particle('liquidate',i)
   rain.append(Sequence(Wait(delay),Func(effect.start,cloud),Wait(length),Func(effect.softStop),Wait(.3),Func(effect.disable)))
  rain.append(Sequence(ActorInterval(channel,'prop',startTime=3,duration=.1),ActorInterval(channel,'prop',startTime=1,duration=2.3)))
  clips.append(Sequence(appear(cloud,actor,(0,3,height+3),(180,0,0),(3,)*3,.000001,grow=.7),Func(detach),Wait(1.1),LerpPosInterval(cloud,1,lambda:point(2+3*TOON_SCALE)),Wait(.2),Parallel(*rain),Wait(.4),LerpScaleInterval(cloud,.5,.001),Func(cloud.hide)))
  if hit:
   puddle,_=app.movie_prop('quicksand',None);puddle.setColor(0,0,1,1);puddle.setTransparency(1)
   def show_puddle():puddle.setPos(point(.02));puddle.setH(120);puddle.show()
   clips.append(Sequence(Wait(2.8),Func(show_puddle),LerpScaleInterval(puddle,1.7,1.7*TOON_SCALE,startScale=.001),Wait(3.2),LerpColorScaleInterval(puddle,.8,Vec4(1,1,1,0)),Func(puddle.hide)))
  sound('SA_liquidate.ogg',2)
 duration=max([impact+2,actor.getDuration(anim)+(.9 if name=='Liquidate' else 0)]+[c.getDuration() for c in clips])
 heading=Vec3(root.getHpr())
 def face():root.headsUp(toon);root.setH(root.getH()-actor.getH())
 delay=.9 if name=='Liquidate' else 0
 clips.extend([Sequence(Func(face),Wait(delay),ActorInterval(actor,anim),Wait(max(0,duration-delay-actor.getDuration(anim))),Func(root.setHpr,heading),Func(app.restore_cog_pose,i)),app.attack_caption(i,name,duration),app.health_movie(event,impact)])
 return Parallel(*clips)
