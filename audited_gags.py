"""Per-track choreography from the MovieThrow/Squirt/Sound/Heal/Lure/Trap/Drop references.
Original resource origins and animation channels are retained; distances fit this scene.
"""
from panda3d.core import Vec3,Vec4
from direct.interval.IntervalGlobal import Sequence,Parallel,Func,Wait,ActorInterval,LerpPosInterval,LerpScaleInterval,LerpHprInterval
from battle_engine import GAGS
from battle_movies import MOVIES


def perform(app,index,anim,minimum=0):
 clips=[ActorInterval(actor,anim) for actor in app.toon_actors[index].values() if anim in actor.getAnimNames()]
 return Sequence(Parallel(Wait(minimum),*clips),Func(app.play_toon_animation,index,'idle',True))

def opera_pose(app,index):
 clips=[]
 for actor in app.toon_actors[index].values():
  if 'sound' in actor.getAnimNames():clips.append(Sequence(ActorInterval(actor,'sound',startTime=0,endTime=2.8),Wait(6),ActorInterval(actor,'sound',startTime=2.8)))
 return Sequence(Parallel(*clips),Func(app.play_toon_animation,index,'idle',True))

def held(app,index,name,duration,pos=(0,0,0),hpr=(0,0,0),scale=1,left=False,delay=0,joint=None):
 prop,actor=app.movie_prop(name,None)
 hand=app.toon_actors[index]['legs' if joint=='joint_hips' else 'torso'].find('**/'+joint if joint else '**/joint_Lhold' if left else '**/joint_Rhold')
 def attach():prop.reparentTo(hand);prop.setPos(*pos);prop.setHpr(*hpr);prop.setScale(scale);prop.show()
 return prop,Sequence(Wait(delay),Func(attach),app.prop_clip(actor,duration),Func(prop.hide))

def cue(app,name,t,duration=None):
 return Sequence(Wait(t),app.sound_clip(name) if duration is None else app.sound_clip(name,duration))
def sound_for(track,level,miss=False):
 table=MOVIES['sound_tracks'][track]
 return table.get('miss' if miss else 'hit',table['hit'])[level-1]

def stream(app,start,end,t,width=.2,hold=.5,color=(.7,.85,1,.8),ramp=.15):
 prop,_=app.movie_prop('spray',None);lo,hi=prop.getTightBounds();length=max(hi.y-lo.y,.01)
 def show():
  a=start();b=end();prop.setPos(a);prop.lookAt(b);prop.setScale(.001);prop.setColor(*color);prop.setLightOff();prop.setTwoSided(True);prop.setTransparency(1);prop.show()
 def full():
  ratio=(end()-start()).length()/length
  return Vec3(width*ratio,ratio,width*ratio)
 return Sequence(Wait(t),Func(show),LerpScaleInterval(prop,ramp,full),Wait(hold),LerpScaleInterval(prop,ramp,.001),Func(prop.hide))

def splat(app,target,name,t):
 prop,actor=app.movie_prop('splat',None);prop.setScale(.7);prop.setPos(app.cog_nodes[target].getPos()+Vec3(0,-.45,2.5));prop.setBillboardPointEye()
 return Sequence(Wait(t),Func(prop.show),app.prop_clip(actor,.7),Func(prop.hide))

def throw(app,a,targets,misses):
 g=GAGS[a.gag];prop=MOVIES['tracks']['Throw'][1][g.level-1];clips=[perform(app,a.toon,'throw',4.2)]
 if g.level==7 and targets:
  cake,_=app.movie_prop(prop,None);hand=app.toon_actors[a.toon]['torso'].find('**/joint_Rhold')
  def show():cake.reparentTo(hand);cake.setPos(0,0,0);cake.setScale(1.5);cake.show()
  clips.append(Sequence(Func(show),Wait(2.7)))
  parts=['cake1','cake2','cake3','caketop']
  groups={1:[parts],2:[parts[:2],parts[2:]],3:[parts[:2],parts[2:3],parts[3:]],4:[[n] for n in parts]}[len(targets)]
  for target,names in zip(targets,groups):
   for n in names:
    piece=cake.find('**/'+n)
    if piece.isEmpty():raise ValueError('Missing wedding cake tier '+n)
    app.movie_props.append((piece,None))
    dest=app.cog_nodes[target].getPos()+Vec3(1.8 if target in misses else 0,0,2.4)
    clips.append(Sequence(Wait(2.7),Func(piece.wrtReparentTo,app.render),LerpPosInterval(piece,.45 if target in misses else .3,dest),Func(piece.hide)))
  clips.append(Sequence(Wait(3.2),Func(cake.hide)))
 for target in targets:
  if g.level!=7:clips.append(app.projectile(a.toon,target,prop,miss=target in misses))
  if target not in misses:clips.append(splat(app,target,prop,3))
 if g.level==7:
  clips.append(cue(app,'AA_throw_wedding_cake.ogg',1))
  clips.append(cue(app,'AA_throw_wedding_cake_miss.ogg' if all(i in misses for i in targets) else 'AA_throw_wedding_cake_cog.ogg',3))
 else:clips.extend([cue(app,'AA_pie_throw_only.ogg',2.5),cue(app,sound_for('Throw',g.level,all(i in misses for i in targets)),3)])
 return Parallel(*clips),3

def drop(app,a,targets,misses,react_miss=True,animate_toon=True):
 g=GAGS[a.gag];level=g.level-1;name=MOVIES['tracks']['Drop'][1][level]
 clips=([perform(app,a.toon,'pushbutton',4.5),app.hand_prop(a.toon,'button',4.5),cue(app,'AA_drop_trigger_box.ogg',2.14)] if animate_toon else [])
 if level<6:clips.append(cue(app,'incoming_whistleALT.ogg',2.81))
 victims=targets
 if level==6 and targets:victims=[targets[len(targets)//2]]
 for i in victims:
  miss=all(j in misses for j in targets) if level==6 else i in misses
  node,actor=app.movie_prop(name,None)
  pos=Vec3(app.cog_nodes[i].getPos())
  # MovieDrop.posObject / posShadow use battle-space +Y, not a side offset.
  # Lured Cogs use their original formation slot; small Drops stay there.
  if app.game.cogs[i].lure and miss:
   pos.y=3.7+(2 if level>=3 else 0)
  elif miss and level>=3:pos.y+=5
  pos.z+=.08
  if level<3 and not miss:pos.z+=2.5
  if level==6:pos.x=sum(app.cog_nodes[j].getX() for j in targets)/len(targets)
  node.setPos(pos);node.setScale(.6 if level<6 else .42);node.setH(270 if level==6 else 180)
  shadow,_=app.movie_prop('drop-shadow',None)
  shadow.setName('falling-gag-shadow');shadow.setPos(pos.x,pos.y,.095);shadow.setScale(.01);shadow.setLightOff()
  # Extracted geometry uses TTR's custom ground bin. Render after our opaque
  # pavement, with normal depth testing so the shadow cannot cover characters.
  shadow.setBin('transparent',0,1);shadow.setDepthWrite(False,1);shadow.setTransparency(1,1)
  # MovieDrop copies the Suit shadow, whose model has a .45 base scale.
  for child in shadow.getChildren():child.setScale(.45*.6)
  clips.append(Sequence(Wait(2.44),Func(shadow.show),LerpScaleInterval(shadow,1.86,(.5,.8,.8,2,2.3,3.6,4)[level]),Wait(.3),Func(shadow.hide)))
  if actor:
   if miss and level>=3:
    fall=Sequence(ActorInterval(actor,'prop',startFrame=0,endFrame=(12,4,1,11,11,11,2)[level]),Func(actor.pose,'prop',(12,4,1,11,11,11,2)[level]),Wait(1))
   else:fall=ActorInterval(actor,'prop')
  else:
   fall=Sequence(Func(node.setZ,pos.z+5),LerpPosInterval(node,(12,4,1,11,11,11,2)[level]/24,pos),Wait(.5))
  shrink=.1 if miss else .3
  prop_duration=fall.getDuration()
  clips.append(Sequence(Wait(4.3),Func(node.show),Parallel(fall,Sequence(Wait(max(0,prop_duration-shrink)),LerpScaleInterval(node,shrink,.001))),Func(node.hide)))
  cog=app.cog_actors[i]
  if not miss:
   anim='flatten' if level>=3 else 'drop-react'
   clips.append(Sequence(Wait(4.3),ActorInterval(cog,anim),Func(app.restore_cog_pose,i)))
  elif react_miss:
   if level>=3 and not app.game.cogs[i].lure:
    clips.append(Sequence(Wait(4.3),ActorInterval(cog,'victory',startTime=.5,endTime=1.9),Func(app.restore_cog_pose,i)))
   elif level<3 and not app.game.cogs[i].lure:clips.append(Sequence(Wait(3.75),app.cog_clip(i,'sidestep-left',1)))
   clips.append(Sequence(Wait(4.5),app.float_text(app.cog_nodes[i],0,4,start=False,text='MISSED')))
 for i in targets:
  if i in victims:continue
  if i not in misses:clips.append(Sequence(Wait(4.3),ActorInterval(app.cog_actors[i],'flatten'),Func(app.restore_cog_pose,i)))
  elif react_miss:clips.append(Sequence(Wait(4.5),app.float_text(app.cog_nodes[i],0,4,start=False,text='MISSED')))
 clips.append(cue(app,sound_for('Drop',g.level,all(i in misses for i in targets)),2.44 if level==6 else 4.31))
 return Parallel(*clips),4.3

SOUND_APPEAR=('MG_tag_1.ogg','LB_receive_evidence.ogg','m_match_trumpet.ogg','TL_step_on_rake.ogg','toonbldg_grow.ogg','mailbox_full_wobble.ogg','mailbox_full_wobble.ogg')
def sound(app,a,targets,misses):
 level=GAGS[a.gag].level-1;name=MOVIES['tracks']['Sound'][1][level]
 duration=9 if level==6 else 4.3
 positions=[(-1.1,-1.4,.1),(-1.2,-1.3,.1),(-1.3,-1.4,.1),(-1,-1.5,.2),(-.6,-.9,.15),(-.8,-.9,.2),(-1.04,-1.17,.26)]
 scales=(.325,.1,.2,.25,.5,.5,.85)
 prop,_=app.movie_prop(name,None);hand=app.toon_actors[a.toon]['torso'].find('**/joint_Rhold')
 def show():prop.reparentTo(hand);prop.setPos(*positions[level]);prop.setHpr(145,0,(0,85,85,85,85,0,90)[level]);prop.setScale(.001);prop.show()
 effects=[]
 if level==6:
  # MovieSound.__doOpera: two growth stages, six-second hold, quick shrink.
  visual=Sequence(Func(show),Wait(1),LerpScaleInterval(prop,1,.85,blendType='easeOut'),LerpScaleInterval(prop,1.1,1.1,blendType='easeIn'),Wait(6),LerpScaleInterval(prop,.1,.001),Wait(2),Func(prop.hide))
  effect=app.source_particle('soundWave',a.toon)
  effect.setScale(effect.getScale()*app.toon_actors[a.toon]['legs'].getScale().z)
  def wave_origin():
   effect.setPos(app.render.getRelativePoint(prop,Vec3(0,1.6,-.18)))
   effect.start(app.render)
  effects.append(Sequence(Wait(2.8),Func(wave_origin),Wait(2.5),Func(effect.softStop),Wait(3.5),Func(effect.disable)))
  duration=max(visual.getDuration(),opera_pose(app,a.toon).getDuration())
 elif level==2:
  # MovieSound.__doBugle starts the bugle clip with growth at 1.7s.
  # It loads an appearance sound but never plays it; do not add a second cue.
  duration=5.3
  shake=Sequence(*(LerpScaleInterval(prop,.2,.25 if n%2 else .2,blendType='easeInOut') for n in range(4)))
  visual=Sequence(Func(show),Wait(1.7),LerpScaleInterval(prop,1,.2,blendType='easeInOut'),Parallel(shake,Wait(1)),LerpScaleInterval(prop,.1,.001),Wait(1.5),Func(prop.hide))
 elif level==5:
  # MovieSound.__doFoghorn: source scales multiplied by .5, not the
  # generic instrument scale/squash used for other Sound props.
  duration=5.1
  visual=Parallel(
   Sequence(Func(show),Wait(1),LerpScaleInterval(prop,1,.05),LerpScaleInterval(prop,.1,.15),Wait(.35),LerpScaleInterval(prop,.3,.20,blendType='easeOut'),Wait(.5),LerpScaleInterval(prop,1,.001,blendType='easeIn'),Wait(.85),Func(prop.hide)),
   Sequence(Wait(2.65),LerpHprInterval(prop,1.5,Vec3(145,0,90),startHpr=Vec3(145,0,0),blendType='easeInOut')))
 else:
  visual=Sequence(Func(show),Wait(1),LerpScaleInterval(prop,.2,scales[level]),Wait(1.25),LerpScaleInterval(prop,.2,Vec3(scales[level]*.8,scales[level]*1.35,scales[level]*.8)),LerpScaleInterval(prop,.2,scales[level]),Wait(duration-2.95),LerpScaleInterval(prop,.1,.001),Func(prop.hide))

 appearance=Wait(0) if level==2 else cue(app,SOUND_APPEAR[level],1 if level==6 else 1.15 if level==0 else 1.05)
 return Parallel(*effects,opera_pose(app,a.toon) if level==6 else perform(app,a.toon,'sound',duration),app.hand_prop(a.toon,'megaphone',duration),visual,appearance,cue(app,sound_for('Sound',level+1),1.7 if level==2 else 2.15 if level==6 else 2.45)),2.6

def flower_movie(app,a,targets,misses):
 # MovieSquirt.__doFlower: chest attachment, delayed scale-in, short spray.
 torso=app.toon_actors[a.toon]['torso'];joint=torso.find('**/def_joint_attachFlower')
 if joint.isEmpty():raise ValueError('Missing Toon chest flower attachment')
 prop,_=app.movie_prop(MOVIES['tracks']['Squirt'][1][0],None)
 def attach():prop.reparentTo(joint);prop.setPos(0,0,0);prop.setHpr(0,0,0);prop.setScale(.001);prop.show()
 missed=all(i in misses for i in targets);spray=3.0 if missed else 2.5
 duration=torso.getDuration('pushbutton')
 clips=[perform(app,a.toon,'pushbutton'),app.hand_prop(a.toon,'button',duration),cue(app,sound_for('Squirt',1,missed),2.1)]
 clips.append(Sequence(Wait(1),Func(attach),LerpScaleInterval(prop,.5,1.5),Wait(spray-1.5+.5),LerpScaleInterval(prop,.5,.001),Func(prop.hide)))
 for i in targets:
  target=app.cog_nodes[i];offset=Vec3(1.8 if i in misses else 0,0,2.4)
  clips.append(stream(app,lambda p=prop:p.getPos(app.render),lambda n=target,o=offset:n.getPos()+o,spray,.2,.1,color=(.75,.75,1,.8),ramp=.2))
 return Parallel(*clips),2.7

def squirt(app,a,targets,misses):
 level=GAGS[a.gag].level
 if level==1:return flower_movie(app,a,targets,misses)
 if level==6:
  from storm_cloud import movie
  return movie(app,a,targets,misses)
 anim,name=(x[level-1] for x in MOVIES['tracks']['Squirt'])
 if level==1:anim='pushbutton'
 rate=app.toon_actors[a.toon]['torso'].getFrameRate(anim)
 spray=(2.5,82/rate,48/rate,53/rate+.05,2.8,2.9)[level-1]
 duration=max(4.2,spray+1.1,app.toon_actors[a.toon]['torso'].getDuration(anim));clips=[perform(app,a.toon,anim,duration)]
 if level==1:
  clips.append(app.hand_prop(a.toon,'button',3))
  prop,_=app.movie_prop(name,None);joint=app.toon_actors[a.toon]['torso'].find('**/def_joint_attachFlower')
  if joint.isEmpty():joint=app.toon_actors[a.toon]['torso'].find('**/joint_Rhold')
  def flower():prop.reparentTo(joint);prop.setPos(0,0,0);prop.setScale(1.5);prop.show()
  clips.append(Sequence(Func(flower),Wait(duration),Func(prop.hide)))
 else:
  prop,clip=held(app,a.toon,name,duration,pos=(.28,.1,.08) if level==3 else (0,0,0),hpr=(85.6,-4.44,94.43) if level==3 else (0,0,0));clips.append(clip)
 if level==5:
  hydrant,_=app.movie_prop('hydrant',None);hydrant.setPos(app.toon_nodes[a.toon].getPos()+Vec3(.7,0,.1));hydrant.setScale(.3)
  clips.append(Sequence(Wait(.7),Func(hydrant.show),Wait(duration-.7),Func(hydrant.hide)))
 for i in targets:
  target=app.cog_nodes[i];offset=Vec3(1.8 if i in misses else 0,0,2.4)
  nozzle=prop.find('**/joint_nozzle') if level==3 else prop
  if nozzle.isEmpty():nozzle=prop
  clips.append(stream(app,lambda p=nozzle:p.getPos(app.render),lambda n=target,o=offset:n.getPos()+o,spray,(.12,.18,.12,.35,.45)[level-1]))
 # MovieSquirt has individual audio lead-ins, not a shared spray offset.
 sound_start={2:1.7,3:1.8,4:spray-.1,5:2.8}[level]
 clips.append(cue(app,sound_for('Squirt',level,all(i in misses for i in targets)),sound_start))
 return Parallel(*clips),spray+.15

def magnet_reaction(app,index):
 # MovieLure.__createMagnetMultiTrack: reverse landing, three shakes,
 # recovery and neutral. Explicit source frames avoid play-rate/time remapping.
 actor=app.cog_actors[index];fps=actor.getFrameRate('landing')
 def segment(start,end,duration=None):
  return ActorInterval(actor,'landing',startFrame=start*fps,endFrame=end*fps,**({'duration':duration} if duration is not None else {}))
 body=Sequence(Wait(2.6),segment(2.37,1.82),
  *(segment(1.82,1.16,.8/3) for _ in range(3)),segment(1.16,.7),segment(.7,2.0,1.3),Func(app.restore_cog_pose,index))
 clips=[Func(setattr,app.game.cogs[index],'lure_pose','idle'),body]
 if app.game.cogs[index].lure or index in getattr(app,'lure_movie_destinations',{}):
  node=app.cog_nodes[index]
  clips.append(Sequence(Wait(3.95),LerpPosInterval(node,.8,Vec3(node.getX(),getattr(app,'lure_movie_destinations',{}).get(index,2.2),0))))
 return Parallel(*clips)

def lure(app,a,targets,misses):
 level=GAGS[a.gag].level;anim,name=(x[level-1] for x in MOVIES['tracks']['Lure'])
 clips=[];impact=(3.5,2.6,3.5,2.6,3.5,1.6)[level-1];duration=7 if level<6 else 3.6
 clips.append(perform(app,a.toon,anim,duration))
 if level in (1,3,5):
  clips.append(held(app,a.toon,'fishing-pole',duration)[1])
  for i in targets:
   prop,actor=app.movie_prop(name,None);prop.setPos(app.cog_nodes[i].getPos()+Vec3(0,-1.5,.1));prop.setScale(.6)
   clips.append(Sequence(Func(prop.show),app.prop_clip(actor,5),LerpPosInterval(prop,.2,app.toon_nodes[a.toon].getPos()+Vec3(0,0,3)),Func(prop.hide)))
 elif level in (2,4):
  clips.append(held(app,a.toon,name,6.3,(-.27,.19 if level==2 else .08,.29),(-90,84.17,-180),.85 if level==2 else 1.32,True,.7)[1])
 else:
  prop,actor=app.movie_prop(name,None);hand=app.toon_actors[a.toon]['torso'].find('**/joint_Lhold')
  def goggles():
   prop.reparentTo(hand);prop.setPos(-1.03,1.04,-.3);prop.setHpr(-96.55,36.14,-170.59);prop.setScale(1.5);prop.show()
  clips.append(Sequence(Wait(.6),Func(goggles),ActorInterval(actor,'prop',duration=2.2),Func(prop.hide)))
 clips.append(cue(app,sound_for('Lure',level),.7 if level in (2,4) else .5))
 for i in targets:
  if i not in misses:
   if level in (2,4):
    clips.append(magnet_reaction(app,i));continue
   if level==6:
    node=app.cog_nodes[i]
    clips.append(Sequence(Wait(1.6),Func(setattr,app.game.cogs[i],'lure_pose','idle'),ActorInterval(app.cog_actors[i],'hypnotized',duration=3.1),Func(app.restore_cog_pose,i)))
    if app.game.cogs[i].lure or i in getattr(app,'lure_movie_destinations',{}):clips.append(Sequence(Wait(3.3),LerpPosInterval(node,.7,Vec3(node.getX(),getattr(app,'lure_movie_destinations',{}).get(i,2.2),0))))
    continue
   dollar=level in (1,3,5)
   if dollar and i in getattr(app,'lure_movie_destinations',{}):
    node=app.cog_nodes[i];clips.append(Sequence(Wait(impact),LerpPosInterval(node,1.5,Vec3(node.getX(),app.lure_movie_destinations[i],0))))
   # MovieLure fishing-pole sequence uses reach, then neutral; not hypno.
   clips.append(Sequence(Wait(impact),Func(setattr,app.game.cogs[i],'lure_pose','idle' if dollar else 'hypnotized'),app.cog_clip(i,'reach' if dollar else 'hypnotized',3.5 if dollar else 1.5)))
 return Parallel(*clips),impact

def heal(app,a,targets,misses):
 level=GAGS[a.gag].level;anim,name=(x[level-1] for x in MOVIES['tracks']['Toon-Up']);impact=(3,2.5,4.2,3,2.5,4,7)[level-1]
 if level==3:impact=115/app.toon_actors[a.toon]['torso'].getFrameRate('smooch')+.5
 duration=max(impact+1.4,app.toon_actors[a.toon]['torso'].getDuration(anim));clips=[]
 if level==7:
  from heal_dive import movie
  clips.append(movie(app,a.toon))
 else:
  if level==5 and targets:
   # MovieHeal.__healSprinkle.face90: sprinkle-dust throws sideways (+X).
   # Evaluate after running to the healing spot, not while building the movie.
   def face_pixie_target():
    node=app.toon_nodes[a.toon];target=app.toon_nodes[targets[0]]
    origin=node.getPos(app.render);delta=target.getPos(app.render)-origin;delta.z=0
    node.headsUp(app.render,origin+Vec3(-delta.y,delta.x,0))
   clips.append(Sequence(Func(face_pixie_target),perform(app,a.toon,anim,duration)))
  else:clips.append(perform(app,a.toon,anim,duration))
  feather_scale=max(.5,(app.toon_nodes[targets[0]].getPos().length()-.3)/(2.4*.62)) if level==1 and targets else 1
  clips.append(held(app,a.toon,name,duration,pos=(-.27,-.24,-.95) if level==3 else (-.28,0,.14) if level==4 else (0,0,0),hpr=(-118,-10.6,-25.9) if level==3 else (0,0,-150) if level==4 else (0,0,0),scale=feather_scale,left=level==4,joint='joint_hips' if level==6 else None)[1])
  if level==5:
   for particle,delay,hold in [('pixieSpray',1.5,.5),('pixieDrop',1.9,2),('pixieExplode',2.7,1),('pixiePoof',3.4,1),('pixieWall',4.05,1.2)]:
    effect=app.source_particle(particle,a.toon);effect.setScale(effect.getScale()*.5);effect.setPos(effect.getPos()*.5)
    parent=app.toon_nodes[targets[0]] if particle in ('pixieDrop','pixiePoof') and targets else app.toon_nodes[a.toon]
    clips.append(Sequence(Wait(delay),Func(effect.start,parent),Wait(hold),Func(effect.softStop),Wait(1),Func(effect.disable)))
  if level==4:clips.append(held(app,a.toon,'hat',duration,pos=(.23,.09,.69),hpr=(180,0,0))[1])
  if level==3:
   for i in targets:
    lips,_=app.movie_prop('lips',None);lips.setPos(Vec3(0,0,2.5));lips.setScale(.001);lips.setBillboardPointEye()
    hand=app.toon_actors[a.toon]['torso'].find('**/joint_Rhold')
    clips.append(Sequence(Wait(2.5),Func(lambda n=lips,h=hand:n.setPos(h.getPos(app.render))),Func(lips.show),LerpScaleInterval(lips,.5,3),Wait(max(0,impact-3.5)),LerpPosInterval(lips,.5,app.toon_nodes[i].getPos()+Vec3(0,0,2.5)),Func(lips.hide)))
 # MovieHeal's per-gag lead-ins and intentional audio durations.
 sound_start=(1,2,2,.2,2,.7,.6)[level-1]
 sound_duration=(None,None,None,6.4,4.1,7.7,9.0)[level-1]
 clips.append(cue(app,sound_for('Toon-Up',level),sound_start,sound_duration))
 return Parallel(*clips),impact

BUILDERS={'Throw':throw,'Drop':drop,'Sound':sound,'Squirt':squirt,'Lure':lure,'Toon-Up':heal}
def track_movie(app,event):
 if event['track']=='Throw':
  from throw_sequence import movie
  return movie(app,event)
 if event['track']=='Squirt':
  from squirt_sequence import movie
  return movie(app,event)
 if event['track']=='Sound':
  from sound_sequence import movie
  return movie(app,event)
 if event['track']=='Drop':
  from drop_sequence import movie
  return movie(app,event)
 clips=[];impact=0
 for action in event.get('actions',[]):
  movie,t=BUILDERS[event['track']](app,action,event.get('targets',{}).get(action.toon,[]),event.get('misses',[]));clips.append(movie);impact=max(impact,t)
 health=dict(event,dodge_at=2.45 if event['track']=='Throw' else 3.75 if event['track']=='Drop' else max(0,impact-.5))
 clips.append(app.health_movie(health,impact))
 return Parallel(*clips)
