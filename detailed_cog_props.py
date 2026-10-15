"""Explicit classic prop choreography; raw extracted models retain hand origins."""
from panda3d.core import Vec3,ColorScaleAttrib
from direct.interval.IntervalGlobal import Sequence,Parallel,Func,Wait,ActorInterval,LerpPosInterval,LerpHprInterval,LerpScaleInterval
from classic_cog_movies import appear,arc,TOON_SCALE as S
from battle_movies import MOVIES

ATTACKS={'Evil Eye','Hang Up','Market Crash','Power Tie','Half Windsor','Fountain Pen','Rolodex','Glower Power'}

def movie(app,event):
 i=event['cog'];name=event['name'];cog=app.game.cogs[i];actor=app.cog_actors[i];root=app.cog_nodes[i]
 t=event['targets'][0];toon=app.toon_nodes[t];hit=t not in event['misses'];right=actor.find('**/joint_Rhold');left=actor.find('**/joint_Lhold')
 anim=MOVIES['suits'][cog.name]['attacks'][name];clips=[];body=__import__('scene_art').MODELS[cog.name]['body']
 impact,dodge,reaction,dodgeanim={
 'Evil Eye':(4.14,1.64,'duck','duck'),'Hang Up':(5.5,4.7,'slip-backward','jump'),
 'Market Crash':(4.2,2.4,'slip-forward','sidestep-left'),'Power Tie':(2.61 if body=='C' else 3.3,2.34 if body=='C' else 3.1,'conked','sidestep-left'),
 'Half Windsor':(3.4,2.4,'conked','sidestep-left'),'Fountain Pen':(1.81,.11,'conked','duck'),
 'Rolodex':(3.8 if body=='A' else 4 if body=='B' else 3.5,2.5,'conked','sidestep-left'),
 'Glower Power':(1.6,.7,'slip-backward','sidestep-left')}[name]
 def point(z=2,y=0,x=0):return app.render.getRelativePoint(toon,Vec3(x,y,z))
 def sound(file,time):clips.append(Sequence(Wait(time),app.sound_clip(file)))
 def prop(name):
  p,a=app.movie_prop(name,None);p.setName('attack-'+name);return p,a
 def particle(stem,parent,time,length):
  p=app.source_particle(stem,i);clips.append(Sequence(Wait(time),Func(p.start,parent),Wait(length),Func(p.softStop),Wait(1),Func(p.disable)));return p
 def segment(anim,start=0,end=None,rate=1):
  return Parallel(*(ActorInterval(a,anim,startTime=start,**({'endTime':end} if end is not None else {}),playRate=rate) for a in app.toon_actors[t].values() if anim in a.getAnimNames()))
 def scheduled_reaction(at,seq):
  r=Sequence(seq,Func(lambda:app.play_toon_animation(t,'idle',True) if app.game.toons[t].alive else None))
  event.setdefault('custom_toon_tracks',[]).append(r)
  def start():
   if app.game.toons[t].alive:app.live_departures=getattr(app,'live_departures',[])+[r];r.start()
  clips.append(Sequence(Wait(at),Func(start),Wait(r.getDuration())))
 event=dict(event)
 if hit and name in ('Evil Eye','Market Crash','Half Windsor','Glower Power'):
  event['custom_toon_reaction']=True
  if name=='Evil Eye':scheduled_reaction(2.44,Sequence(segment('duck',.01,1.41),segment('cringe',.3)))
  elif name=='Market Crash':scheduled_reaction(3.8,Sequence(segment('cringe',.21,.29),segment('slip-forward',.6,1.45),segment('slip-forward',1.2,1.51,.31/.95),segment('slip-forward',1.51)))
  elif name=='Half Windsor':scheduled_reaction(3.4,Sequence(segment('conked',.01,.41),segment('cringe',.7)))
  else:scheduled_reaction(1.6,segment('slip-backward',.35))
 if not hit and name=='Fountain Pen':
  event['custom_toon_dodge']=True;scheduled_reaction(.11,segment('duck',.6));impact=1.77
 if name=='Hang Up':
  phone,_=prop('phone');receiver,_=prop('receiver');tf=cog.name=='Two-Face'
  pos=(-.23,.01,-.26) if tf else (.23,.17,-.11);rp=(-.13,-.07,-.06) if tf else pos
  rh=(-1.854,2.434,-177.579) if tf else (5.939,2.763,-177.591)
  clips.append(Sequence(appear(receiver,left,rp,rh,(1,)*3,.3,grow=0),Wait(.5+(.44 if tf else .74)),
   Func(receiver.wrtReparentTo,right),Func(receiver.setScale,.8 if tf else 1),Func(receiver.setPos,-.53,.21,-.54),Func(receiver.setHpr,-99.49,-35.27,1.84),Wait(3.07),Func(receiver.wrtReparentTo,phone)))
  clips.append(Sequence(appear(phone,left,pos,(5.939,2.763,-177.591),(.75,)*3 if tf else (1,)*3,.3),Wait((.44 if tf else .74)+3.07+(.01 if tf else .69)),LerpScaleInterval(phone,.5,.001),Func(receiver.hide),Func(phone.hide)))
  sound('SA_hangup.ogg',1.3)
 elif name=='Evil Eye':
  eye,_=prop('evil-eye');pos={'Corporate Raider':(-.46,4.85,5.28),'Legal Eagle':(-.64,4.45,5.91)}.get(cog.name,(-.4,3.65,5.01))
  clips.append(Sequence(appear(eye,actor,pos,(-155,-20,0),(11,)*3,1.06,grow=.63),Wait(.33),LerpHprInterval(eye,.02,Vec3(205,40,0)),Wait(.77),Func(eye.wrtReparentTo,app.render),Parallel(LerpPosInterval(eye,1.1,lambda:point(2 if hit else 2-2*S,0 if hit else -5*S)),LerpHprInterval(eye,1.1,Vec3(0,0,-180))),Func(eye.hide)))
  sound('SA_evil_eye.ogg',1.3)
 elif name in ('Power Tie','Half Windsor'):
  half=name=='Half Windsor';tie,_=prop('half-windsor' if half else 'power-tie')
  pos=(.02,.88,.48) if half else (1.16,.24,.63);hpr=(99,-3,-108.2) if half else (171.561,1.745,-163.443)
  def dest():return point(2+.9*S if hit else 4*S,(-.7 if hit else -5)*S,-1.1*S) if half else point(2 if hit else .1*S)
  path=Sequence(appear(tie,right,pos,hpr,((7 if half else 3.5),)*3,.5),Wait(2.17 if half or body!='C' else 1.45),Func(tie.wrtReparentTo,app.render))
  if not half:path.append(Func(tie.setBillboardPointEye))
  path.append(LerpPosInterval(tie,.4 if hit else .8,dest))
  if not hit:path.append(LerpScaleInterval(tie,.3,.001))
  path.append(Func(tie.hide));clips.append(path)
  if not half:
   sound('SA_powertie_throw.ogg',2.3)
   if hit:sound('SA_powertie_impact.ogg',2.9)
 elif name=='Market Crash':
  paper,_=prop('newspaper')
  clips.append(Sequence(appear(paper,right,(-.07,.17,-.13),(161.867,-33.149,-48.086),(3,)*3,.6),Wait(1.32),Func(paper.wrtReparentTo,app.render),arc(paper,lambda:point(1.1*S if hit else 0,1.5*S,1.2*S),1.5),Wait(.6),LerpPosInterval(paper,.4,lambda:point((1.3 if hit else .2)*S,-.3*S,1.2*S)),Wait(.01),Func(paper.hide)))
  clips.append(Sequence(Wait(2.12),Parallel(LerpHprInterval(paper,1.5,Vec3(-360,0,0)),LerpScaleInterval(paper,1.5,Vec3(6*S))),Wait(.95),LerpScaleInterval(paper,.4,.001)))
 elif name=='Rolodex':
  p,_=prop('rollodex');b=body=='B'
  clips.append(Sequence(appear(p,left,(.12,.24,.01) if b else (-.51,-.03,-.1),(99.032,5.973,-179.839) if b else (89.673,2.166,177.786),((.91 if b else 1.2),)*3,.000001),Wait(4.7),LerpScaleInterval(p,.5,.001),Func(p.hide)))
  particle('rollodexWaterfall',actor,3.1 if b else 2.8,1.9);particle('rollodexStream',actor,3.5 if b else 3.2,1);sound('SA_rolodex.ogg',2.8)
 elif name=='Glower Power':
  x,y,z=(.3,4.3,5.3) if cog.name=='Head Hunter' else (.6,4.5,6) if cog.name=='The Big Cheese' else (.4,3.8,3.7)
  for side in (-1,1):
   for n in range(3):
    knife,_=prop('dagger');clips.append(Sequence(appear(knife,actor,(side*x,y,z),(0,0,0),(.4,)*3,1.1+n*.11,grow=.1),Func(knife.wrtReparentTo,app.render),LerpPosInterval(knife,.3,lambda:point(2,0,0 if hit else 1.8)),Func(knife.hide)))
  sound('SA_glower_power.ogg',1.1)
 elif name=='Fountain Pen':
  from audited_gags import stream
  pen,_=prop('pen');tip=pen.find('**/joint_toSpray')
  if tip.isEmpty():tip=pen
  clips.append(Sequence(appear(pen,right,(0,0,0),(0,0,0),(1.5,)*3,.01),Wait(1.65),LerpScaleInterval(pen,.5,.001),Func(pen.hide)))
  clips.append(stream(app,lambda:tip.getPos(app.render),lambda:point(2,0,0 if hit else 1.8),1.56,.1,.2,color=(0,0,0,1),ramp=.2))
  spill=particle('penSpill',pen,1.4,.7);spill.setPos(tip.getPos(pen))
  if hit:
   splash,channel=prop('splat');splash.setColor(0,0,0,1);splash.setScale(.15*S);splash.setBillboardPointWorld()
   head=app.toon_actors[t]['torso'].find('**/def_head').getChild(0);saved=head.getAttrib(ColorScaleAttrib)
   def restore():
    if not head.isEmpty():head.setAttrib(saved) if saved else head.clearColorScale()
   app.movie_restorers=getattr(app,'movie_restorers',[])+[restore]
   clips.append(Sequence(Wait(1.65),Func(splash.setPos,point()),Func(splash.show),ActorInterval(channel,'prop'),Func(splash.hide),Func(head.setColorScale,0,0,0,1),Wait(2.6),Func(restore)))
  sound('SA_fountain_pen.ogg',1.6)
 heading=Vec3(root.getHpr())
 def face():root.headsUp(toon);root.setH(root.getH()-actor.getH())
 # Evil Eye slows the glower hold instead of replaying a full unmodified gesture.
 bodyclip=Sequence(ActorInterval(actor,anim,endTime=1.06),ActorInterval(actor,anim,startTime=1.06,endTime=1.69,playRate=.63/1.1),ActorInterval(actor,anim,startTime=1.69)) if name=='Evil Eye' else ActorInterval(actor,anim)
 clips.append(app.health_movie(dict(event,reaction=reaction,dodge=dodgeanim,dodge_at=dodge),impact))
 duration=max(bodyclip.getDuration(),*[c.getDuration() for c in clips])
 clips.extend([Sequence(Func(face),bodyclip,Wait(max(0,duration-bodyclip.getDuration())),Func(root.setHpr,heading),Func(app.restore_cog_pose,i)),app.attack_caption(i,name,duration)])
 return Parallel(*clips)
