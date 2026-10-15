"""Resource-backed battle playback using classic Toon/Suit and BattleProps mappings.
Intervals adapt the original movies to this simulator's compact, fixed-camera scene.
"""
import json,re,math
from pathlib import Path
from types import SimpleNamespace
from panda3d.core import Vec3,Vec4,TextNode,TransparencyAttrib,Filename
from direct.actor.Actor import Actor
from direct.particles.ParticleEffect import ParticleEffect
from direct.interval.IntervalGlobal import Sequence,Parallel,Func,Wait,ActorInterval,SoundInterval,LerpPosInterval,LerpScaleInterval,LerpHprInterval,LerpColorScaleInterval
ROOT=Path(__file__).resolve().parent
from game_resources import SOURCE
MOVIES=json.loads((ROOT/'assets/battle_movies.json').read_text())

class BattleMovies:
 def sound_clip(self,name,duration=None,*,start_time=0,volume=.65):
  if name not in MOVIES['audio']:return Wait(0)
  if not hasattr(self,'movie_sounds'):self.movie_sounds=[]
  sound=self.loader.loadSfx(str(SOURCE/MOVIES['audio'][name]));self.movie_sounds.append(sound)
  def play():
   if self.sounds_enabled:
    sound.setVolume(volume)
    if start_time:sound.setTime(start_time)
    sound.play()
  return Sequence(Func(play),Wait(duration if duration is not None else max(0,sound.length()-start_time)),Func(sound.stop))
 def lure_transition(self,event):
  clips=[]
  for i,(before,after) in enumerate(zip(event.get('lure_before',[]),event.get('lure_after',[]))):
   if bool(before)==bool(after) or self.display_cog_hp[i]<=0:continue
   if not after and event.get('damage_components',{}).get(i,{}).get('knockback') and not any(a.gag=='Geyser' for a in event.get('actions',[])):continue
   node=self.cog_nodes[i];pos=Vec3(node.getX(),2.2 if after else 3.7,0)
   if (node.getPos()-pos).length()<.001:continue
   # This interval is built before the gag movie runs. Never choose a new
   # lure reaction from lure_pose here: the gag owns that animation and its
   # pose callback may not have executed yet. Only animate walking on release.
   clips.append(Parallel(Wait(.8) if after else self.cog_clip(i,'walk',.8),LerpPosInterval(node,.8,pos)))
   if not after:self.game.cogs[i].lure_pose='idle'
  return Parallel(*clips)
 def defeat_ducks(self):
  # MovieUtil.createSuitDeathTrack: native duck, then its recovery from 1.8s.
  clips=[]
  for i,toon in enumerate(self.game.toons):
   if not toon.alive:continue
   actors=self.toon_actors[i]
   duck=lambda start=0,actors=actors:Parallel(*(ActorInterval(a,'duck',startTime=start) for a in actors.values() if 'duck' in a.getAnimNames()))
   clips.append(Sequence(Wait(1),duck(),duck(1.8),Func(self.play_toon_animation,i,'idle',True)))
  for guest in getattr(self,'sos_guests',{}).values():
   actors=[a for a in guest['actors'].values() if 'duck' in a.getAnimNames()]
   if actors:
    clips.append(Sequence(Wait(1),Parallel(*(ActorInterval(a,'duck') for a in actors)),Parallel(*(ActorInterval(a,'duck',startTime=1.8) for a in actors)),Parallel(*(Func(a.loop,'idle') for a in actors))))
  return Parallel(*clips)
 def cog_defeat(self,index,duck=True):
  from scene_art import MODELS,expose_attachments
  from trap_movies import remove_for_cog
  cog=self.game.cogs[index];original=self.cog_actors[index];body=MODELS[cog.name]['body'];phase='3.5' if body=='C' else '4'
  skeleton=original.getPythonTag('skelecog')
  file=f'phase_5/models/char/cog{body}_robot-lose-mod.bam' if skeleton else f'phase_{phase}/models/char/suit{body}-lose-mod.bam'
  death=Actor(str(SOURCE/file),{'lose':str(SOURCE/f'phase_{phase}/models/char/suit{body}-lose.bam')})
  expose_attachments(death)
  holder=self.cog_nodes[index].attachNewNode('cog-breakup');death.reparentTo(holder);death.setScale(original.getScale());death.setHpr(original.getHpr())
  if not skeleton:
   neck=death.find('**/joint_head');source=original.find('**/joint_head')
   for child in source.getChildren():child.copyTo(neck)
  for geom in death.findAllMatches('**/+GeomNode'):
   match=original.find('**/'+geom.getName())
   if not match.isEmpty():geom.setState(match.getState())
  holder.hide();self.movie_props.append((holder,death))
  # MovieUtil.createSuitDeathTrack uses two excerpts of the spinning sound,
  # followed by the complete breakup sound. A single long clip loses the cue.
  death_audio=Sequence(Wait(.8),self.sound_clip('Cog_Death.ogg',1.2,start_time=1.5,volume=.2),self.sound_clip('Cog_Death.ogg',3,start_time=.6,volume=.8),self.sound_clip('ENC_cogfall_apart.ogg',volume=.32))
  effects=[Sequence(Func(remove_for_cog,self,index),Func(original.hide),Func(holder.show),ActorInterval(death,'lose'),Func(holder.hide)),death_audio]
  explosion=self.loader.loadModel(str(SOURCE/'phase_3.5/models/props/explosion.bam'));explosion.reparentTo(self.cog_nodes[index]);explosion.setZ(2.7);explosion.setScale(.6);explosion.setBillboardPointEye();explosion.hide();self.movie_props.append((explosion,None))
  effects.append(Sequence(Wait(5.4),Func(explosion.show),Wait(.6),Func(explosion.hide)))
  particle=self.loader.loadModel(str(SOURCE/'phase_3.5/models/props/suit-particles.bam')).find('**/gear')
  if not particle.isEmpty():
   for n in range(14):
    gear=particle.copyTo(self.cog_nodes[index]);gear.setScale(.18);gear.setPos(0,0,2.8);gear.hide();self.movie_props.append((gear,None))
    angle=n*math.tau/14;dest=Vec3(math.cos(angle)*2.5,math.sin(angle)*2.5,1+(n%4))
    effects.append(Sequence(Wait(5.2),Func(gear.show),Parallel(LerpPosInterval(gear,1.0,dest),LerpHprInterval(gear,1.0,Vec3(180,360,90))),Func(gear.hide)))
  if duck:effects.append(self.defeat_ducks())
  return Sequence(Parallel(*effects),Func(self.cog_nodes[index].hide))
 def run_away(self):
  if self.animating or self.modal or self.game.result or self.auto_modes[self.active]:return
  index=self.active;toon=self.game.toons[index]
  if not toon.alive:return
  toon.escaped=True;self.selected.pop(index,None);self.choice=None;self.game.plans.pop(index,None)
  self.game.log.append(toon.name+' ran from the battle.');self.animating=True;self.timer.pause()
  self.display_toon_hp=[t.hp for t in self.game.toons];self.display_cog_hp=[c.hp for c in self.game.cogs];self.make_hud()
  def done():
   self.animating=False;self.hide_defeated();self.active=next((i for i,t in enumerate(self.game.toons) if t.alive),index)
   self.active_ring.reparentTo(self.toon_nodes[self.active]);self.message=self.game.result or toon.name+' left the battle.'
   if not self.game.result:self.timer.resume()
   else:
    self.selected.clear();self.game.plans.clear()
    for cog,actor in zip(self.game.cogs,self.cog_actors):
     if cog.alive:actor.loop('victory')
   self.schedule_auto();self.make_hud()
  from escape_movie import movie
  self.animation=Sequence(movie(self,index),self.formation_interval(),Func(done));self.animation.start()
 def toon_defeat(self,index):
  return Sequence(Func(self.play_toon_animation,index,'lose'),Wait(5.333),LerpScaleInterval(self.toon_nodes[index],1.5,.01,blendType='easeInOut'),Func(self.toon_nodes[index].hide))
 def fire_movie(self,action,event,caller_clip=None):
  from fire_movie import movie
  return movie(self,action,event,caller_clip)
 def clear_movie_props(self,include_unites=True):
  for restore in getattr(self,'movie_restorers',[]):restore()
  self.movie_restorers=[]
  if include_unites:
   for effect in getattr(self,'unite_intervals',[]):effect.finish()
   self.unite_intervals=[]
  for effect in getattr(self,'movie_particles',[]):effect.cleanup()
  self.movie_particles=[]
  for sound in getattr(self,'movie_sounds',[]):sound.stop()
  self.movie_sounds=[]
  for holder,actor in getattr(self,'movie_props',[]):
   if actor:actor.cleanup()
   if not holder.isEmpty():holder.removeNode()
  self.movie_props=[]
 def movie_prop(self,name,size=.8,pose_frame=0):
  files=MOVIES['props'][name];holder=self.render.attachNewNode('battle-prop-'+name)
  actor=None
  if len(files)>1:
   actor=Actor(str(SOURCE/files[0]),{'prop':str(SOURCE/files[1])});model=actor
   if pose_frame is not None:actor.pose('prop',pose_frame)
  else:model=self.loader.loadModel(str(SOURCE/files[0]))
  model.reparentTo(holder);lo,hi=model.getTightBounds();extent=max(hi.x-lo.x,hi.y-lo.y,hi.z-lo.z,.001)
  if size is not None:model.setScale(size/extent);model.setPos(-(lo+hi)*(.5*size/extent))
  if name=='fruitpie':model.setColorScale(.216,.157,.58,1)
  holder.hide();self.movie_props.append((holder,actor));return holder,actor
 def prop_clip(self,actor,duration):
  if not actor:return Wait(duration)
  length=actor.getDuration('prop')
  return ActorInterval(actor,'prop',playRate=max(.01,length/duration))
 def toon_clip(self,index,anim,duration):
  clips=[]
  for actor in self.toon_actors[index].values():
   if anim in actor.getAnimNames():clips.append(ActorInterval(actor,anim,playRate=max(.01,actor.getDuration(anim)/duration)))
  return Sequence(Parallel(*clips),Func(self.play_toon_animation,index,'idle',True))
 def restore_cog_pose(self,index):
  cog=self.game.cogs[index];actor=self.cog_actors[index]
  if not cog.alive:return
  # An impact can settle the outcome before its movie has finished.
  # Only celebrate once playback ends and no active Toon remains.
  if not self.animating and not any(t.alive for t in self.game.toons):anim='victory'
  # Lure movies own their finite reaction. Lured status must never restart it.
  else:anim='controlidle' if cog.remote else 'idle'
  actor.loop(anim)
 def cog_clip(self,index,anim,duration):
  actor=self.cog_actors[index]
  return Sequence(ActorInterval(actor,anim,playRate=max(.01,actor.getDuration(anim)/duration)),Func(self.restore_cog_pose,index))
 def cog_damage_reaction(self,event,index):
  storm=any(a.gag=='Storm Cloud' and index in event.get('targets',{}).get(a.toon,[]) for a in event.get('actions',[]))
  components=event.get('damage_components',{}).get(index,{})
  if components.get('knockback') and event.get('track') in ('Throw','Squirt'):
   from scene_art import MODELS
   actor=self.cog_actors[index];node=self.cog_nodes[index]
   anim='pie-small-react' if event['track']=='Throw' else 'soak' if storm else 'squirt-small-react'
   start={'A':2.43,'B':1.94,'C':2.58}[MODELS[self.game.cogs[index].name]['body']]
   return Parallel(Sequence(ActorInterval(actor,anim,duration=.2),ActorInterval(actor,'slip-forward',startTime=start),Func(self.restore_cog_pose,index)),Sequence(Wait(.2),LerpPosInterval(node,.6,Vec3(node.getX(),3.7,node.getZ()))))
  # MovieSquirt.__doWaterGlass uses a full, native-speed squirt-small-react.
  # Match the target as well as the gag so mixed Squirt choices stay independent.
  if storm:return Sequence(ActorInterval(self.cog_actors[index],'soak'),Func(self.restore_cog_pose,index))
  glass=any(a.gag=='Glass of Water' and index in event.get('targets',{}).get(a.toon,[]) for a in event.get('actions',[]))
  anim='squirt-small-react' if glass else {'Drop':'drop-react','Trap':'rake-react','Squirt':'squirt-large-react','Sound':'squirt-small-react'}.get(event.get('track'),'pie-small-react')
  duration=self.cog_actors[index].getDuration(anim) if glass else .9
  return self.cog_clip(index,anim,duration)
 def hand_prop(self,index,name,duration,size=.75,cog=False):
  prop,actor=self.movie_prop(name,None)
  owner=self.cog_actors[index] if cog else self.toon_actors[index]['torso']
  hand=owner.find('**/'+('joint_Lhold' if name in ('golf-club','rollodex','phone','watercooler','button') else 'joint_Rhold'))
  if hand.isEmpty():hand=(self.cog_nodes if cog else self.toon_nodes)[index]
  def attach():
   prop.reparentTo(hand);prop.setPos(0,0,0)
   if name=='golf-club':prop.setHpr(63.097,43.988,-18.435)
   prop.setScale({'small-magnet':.5,'hypno-goggles':.65,'water-gun':.7,'bottle':.8,'golf-club':1.1,'feather':.7,'button':.8}.get(name,1.0));prop.show()
  return Sequence(Func(attach),self.prop_clip(actor,duration),Func(prop.hide))
 def attack_caption(self,index,name,duration):
  text=TextNode('cog-attack-name');text.setText(name.upper().rstrip('!')+'!');text.setFont(self.damage_font);text.setAlign(TextNode.ACenter);text.setTextColor(.95,.03,.03,1);text.setShadow(.055,.055);text.setShadowColor(0,0,0,1)
  node=self.ui.attachNewNode(text);node.setPos(0,0,.79);node.setScale(min(.115,2.7/max(text.getWidth(),1)));node.setLightOff();node.setDepthTest(False);node.setBin('fixed',110);node.hide()
  self.movie_props.append((node,None))
  return Sequence(Func(node.show),Wait(duration),Func(node.hide))
 def show_health_event(self,kind,index,amount):
  values=self.display_toon_hp if kind=='toon' else self.display_cog_hp
  old=values[index];values[index]=max(0,old+amount)
  if kind=='toon' and index<len(self.laff_faces):
   self.laff_faces[index].set_health(old,self.game.toons[index].maximum)
   self.laff_faces[index].set_health(values[index],self.game.toons[index].maximum,animate=True)
   if hasattr(self,'status_hp_labels'):self.status_hp_labels[index]['text']=f'{values[index]}/{self.game.toons[index].maximum}'
 def toon_damage_reaction(self,event,index):
  if event.get('name') in ('Crunch','Downsize'):
   from crunch_downsize_movies import reaction
   return reaction(self,index,event['name'])
  anim=event.get('reaction',MOVIES.get('attack_timing',{}).get(re.sub('[^a-z0-9]','',event.get('name','').lower()),{}).get('reaction','conked'))
  if event.get('name') in ('Freeze Assets','Brain Storm'):
   parts=self.toon_actors[index].values()
   cringe=Parallel(*(ActorInterval(a,'cringe',startTime=.4,duration=.8) for a in parts if 'cringe' in a.getAnimNames()))
   duck=Parallel(*(ActorInterval(a,'duck',startTime=1.6) for a in parts if 'duck' in a.getAnimNames()))
   return Sequence(Wait(.01),cringe,Wait(.000001 if event.get('name')=='Brain Storm' else .01),duck,Func(self.play_toon_animation,index,'idle',True))
  if event.get('name')=='Liquidate':
   parts=self.toon_actors[index].values()
   melt=Parallel(*(ActorInterval(a,'melt') for a in parts if 'melt' in a.getAnimNames()))
   jump=Parallel(*(ActorInterval(a,'jump',startTime=.4) for a in parts if 'jump' in a.getAnimNames()))
   return Sequence(melt,Wait(1.5),jump,Func(self.play_toon_animation,index,'idle',True))
  duration=max((a.getDuration(anim) for a in self.toon_actors[index].values() if anim in a.getAnimNames()),default=.9)
  return self.toon_clip(index,anim,duration)
 def health_movie(self,event,impact):
  effects=[];next_time={}
  for kind,index,amount in event['health']:
   components=event.get('damage_components',{}).get(index) if kind=='cog' and amount<0 else None
   if components and not event.get('suppress_damage_text'):
    at=impact
    for component in ('base','knockback','combo'):
     value=components[component]
     if not value:continue
     if component!='base':at+=.75
     effects.append(Sequence(Wait(at),self.float_text(self.cog_nodes[index],-value,4,start=False,bonus={'base':0,'knockback':2,'combo':1}[component])))
   if event.get('live'):
    effects.append(Sequence(Wait(impact),Func(self.live_health,event,kind,index,amount)))
    continue
   delay=next_time.get((kind,index),impact);next_time[kind,index]=delay+.3
   parent=(self.toon_nodes if kind=='toon' else self.cog_nodes)[index]
   effects.append(Sequence(Wait(delay),Func(self.show_health_event,kind,index,amount),Wait(0) if components else self.float_text(parent,amount,3.0 if kind=='toon' else 4.0,start=False)))
   if amount<0 and not event.get('custom_cog_reaction'):
    if kind=='toon':react=self.toon_defeat(index) if index in event.get('toon_deaths',[]) else Wait(0) if event.get('custom_toon_reaction') else self.toon_damage_reaction(event,index)
    else:
     react=self.cog_damage_reaction(event,index)
    effects.append(Sequence(Wait(delay),react))
  for index in set(event.get('misses',[])):
   # MovieUtil.indicateMissed -> showHpString: red text rises, holds, fades.
   is_cog_attack=event['kind']=='cog'
   parent=(self.toon_nodes if is_cog_attack else self.cog_nodes)[index]
   effects.append(Sequence(Wait(impact),self.float_text(parent,0,3.0 if is_cog_attack else 4.0,start=False,text='MISSED')))
   if event.get('custom_toon_dodge') and is_cog_attack:continue
   if event.get('track')=='Lure':continue
   key=re.sub('[^a-z0-9]','',event.get('name','').lower())
   timing=MOVIES.get('attack_timing',{}).get(key,{})
   dodge=event.get('dodge',timing.get('dodge',MOVIES['dodges'].get(key,'sidestep-left')))
   dodge_duration=max((a.getDuration(dodge) for a in self.toon_actors[index].values() if dodge in a.getAnimNames()),default=1.3) if is_cog_attack else 1
   reaction=(self.synergy_dodge(index) if event.get('name')=='Synergy' else self.toon_clip(index,dodge,dodge_duration)) if event['kind']=='cog' else self.cog_clip(index,'sidestep-left',1)
   storm=not is_cog_attack and any(a.gag=='Storm Cloud' and index in event.get('targets',{}).get(a.toon,[]) for a in event.get('actions',[]))
   dodge_at=1.8 if storm else event.get('dodge_at',timing.get('dodge_at',max(0,impact-.5)))
   effects.append(Sequence(Wait(dodge_at),reaction))
  return Parallel(*effects)
 def projectile(self,index,target,name,launch=2.7,flight=.3,miss=False,cog=False,size=.8):
  prop,actor=self.movie_prop(name,None)
  owner=(self.cog_nodes if cog else self.toon_nodes)[index];dest=(self.toon_nodes if cog else self.cog_nodes)[target].getPos()+Vec3(0,0,2.2)
  hand_owner=self.cog_actors[index] if cog else self.toon_actors[index]['torso'];hand=hand_owner.find('**/joint_Rhold')
  if hand.isEmpty():hand=owner
  if miss:dest+=Vec3(1.8,0,.6)
  def attach():prop.reparentTo(hand);prop.setPos(0,0,0);prop.setHpr(0,0,0);prop.setScale(1);prop.show()
  return Sequence(Func(attach),Wait(launch),Func(prop.wrtReparentTo,self.render),Parallel(LerpPosInterval(prop,flight,dest),self.prop_clip(actor,flight)),Func(prop.hide))
 def positioned_prop(self,name,pos,duration,size=1.5,fall=False):
  prop,actor=self.movie_prop(name,size);prop.setPos(pos+Vec3(0,0,6) if fall else pos)
  return Sequence(Func(prop.show),Parallel(LerpPosInterval(prop,.6,pos) if fall else Wait(0),self.prop_clip(actor,duration)),Func(prop.hide))
 def sync_railroad(self):
  targets={i for i,c in enumerate(self.game.cogs) if c.alive and c.trap and c.trap[0]=='Railroad'}
  root=getattr(self,'railroad_root',None)
  if not targets:
   if root is not None and not root.isEmpty():root.removeNode()
   self.railroad_root=None;self.railroad_targets=set();return
  if root is None or root.isEmpty():
   root=self.characters.attachNewNode('placed-railroad')
   model=self.loader.loadModel(str(SOURCE/MOVIES['props']['traintrack'][0]));model.reparentTo(root)
   for name in ('tunnel2','tunnel3'):model.find('**/'+name).hide()
   model.find('**/tracksA').clearBin()
   lo,hi=model.getTightBounds();scale=12/max(hi.x-lo.x,hi.y-lo.y,.01)
   model.setScale(scale);model.setPos(-(lo.x+hi.x)*scale/2,-(lo.y+hi.y)*scale/2,-lo.z*scale)
   self.railroad_root=root
  root.setPos(0,1.6,.09);self.railroad_targets=targets
 def railroad_trigger_movie(self,event):
  targets=set(self.railroad_targets)&{i for k,i,n in event['health'] if k=='cog' and n<0}
  # First show the Lure performance; its impact belongs to the passing train.
  lure=dict(event,health=[],custom_cog_reaction=True)
  saved=self.railroad_targets;self.railroad_targets=set()
  previous=getattr(self,'lure_movie_destinations',{})
  # Trap activation clears logical lure before playback. Supply the visual
  # destination explicitly so the lure reaction and movement stay together.
  self.lure_movie_destinations={i:1.6 for i in targets}
  try:windup=self.base_gag_movie(lure)
  finally:
   self.railroad_targets=saved;self.lure_movie_destinations=previous
  clips=[]
  train,actor=self.movie_prop('train',None);train.setH(90);train.setScale(.35);train.setPos(-14,1.6,.05)
  # MovieLure: 3s materialize, 45/35s passage, 3s dematerialize.
  # Keep the compact scene's endpoints; preserve the reference timing.
  travel=45/35;materialize=3.0;start=-14;end=14
  train.setTransparency(TransparencyAttrib.MAlpha);train.setColorScale(1,1,1,0)
  passage=[Sequence(Func(train.show),LerpColorScaleInterval(train,materialize,Vec4(1,1,1,1)),LerpPosInterval(train,travel,Vec3(end,1.6,.05)),LerpColorScaleInterval(train,materialize,Vec4(1,1,1,0)),Func(train.hide)),self.sound_clip('TL_train.ogg')]
  # MovieLure uses the actual tunnel meshes from traintrack and grows them
  # during materialization. Own these separately from persistent traps: a
  # fatal first impact must not remove the tunnel while the train is passing.
  from panda3d.core import PlaneNode,Plane
  tunnel_root=self.characters.attachNewNode('railroad-tunnels')
  self.movie_props.append((tunnel_root,None));tunnel_root.hide()
  track_model=self.loader.loadModel(str(SOURCE/MOVIES['props']['traintrack'][0]))
  tunnels=[]
  for name,x in [('tunnel3',-7.5),('tunnel2',7.5)]:
   mesh=track_model.find('**/'+name)
   lo,hi=mesh.getTightBounds(track_model)
   holder=tunnel_root.attachNewNode(name+'-placement');holder.setPos(x-(lo.x+hi.x)*.35/2,1.6,.09);holder.setScale(.35)
   tunnel=mesh.copyTo(holder);tunnel.setLightOff();tunnel.setTwoSided(True)
   tunnel.setTransparency(TransparencyAttrib.MAlpha);tunnel.setColorScale(1,1,1,0);tunnel.setScale(1,.01,.01);tunnel.show()
   tunnels.append(Parallel(LerpColorScaleInterval(tunnel,3,Vec4(1,1,1,1)),Sequence(LerpScaleInterval(tunnel,2,Vec3(1,2,2.5)),LerpScaleInterval(tunnel,.5,Vec3(1,3,1.5)),LerpScaleInterval(tunnel,.5,Vec3(1,2.5,2)))))
  track_model.removeNode()
  for name,normal,x in [('train-entry',Vec3(1,0,0),-7.5),('train-exit',Vec3(-1,0,0),7.5)]:
   plane=PlaneNode(name);plane.setPlane(Plane(normal,Vec3(x,0,0)))
   train.setClipPlane(tunnel_root.attachNewNode(plane))
  passage.append(Sequence(Func(tunnel_root.show),Parallel(*tunnels),Wait(travel+materialize),Func(tunnel_root.hide)))
  for i in targets:
   hit=materialize+max(0,min(travel,(self.cog_nodes[i].getX()-start)/(end-start)*travel))
   single=dict(event,health=[h for h in event['health'] if h[0]=='cog' and h[1]==i],misses=[],custom_cog_reaction=True)
   passage.append(self.health_movie(single,hit))
   passage.append(Sequence(Wait(hit),Parallel(Sequence(ActorInterval(self.cog_actors[i],'flatten'),Func(self.restore_cog_pose,i)),self.sound_clip('TL_train_cog.ogg'))))
  other=dict(event,health=[h for h in event['health'] if h[0]!='cog' or h[1] not in targets],misses=[],custom_cog_reaction=True)
  passage.append(self.health_movie(other,.8))
  returns=[Parallel(self.cog_clip(i,'walk',.8),LerpPosInterval(self.cog_nodes[i],.8,Vec3(self.cog_nodes[i].getX(),3.7,0))) for i in targets if self.game.cogs[i].alive]
  return Sequence(windup,Parallel(*clips),Parallel(*passage),Func(self.sync_railroad),Parallel(*returns))
 def geyser_movie(self,event):
  if not event.get('scheduled_geyser'):
   from squirt_sequence import movie
   return movie(self,event)
  clips=[];impact=2.9;shown=set();delays={}
  if not hasattr(self,'presentation_rng'):
   self.presentation_rng=__import__('random').Random()
  for action in event.get('actions',[]):
   if action.gag!='Geyser':
    other=dict(event,actions=[action],health=[],misses=event.get('misses',[]))
    clips.append(self.base_gag_movie(other));continue
   clips.extend([self.toon_clip(action.toon,'pushbutton',3.5),self.hand_prop(action.toon,'button',3.5,.4)])
   for i in event.get('targets',{}).get(action.toon,[]):
    if i in shown:continue
    shown.add(i)
    delay=delays[i]=self.presentation_rng.random()
    # MovieSquirt uberClone suppresses duplicate water and Cog launches.
    if event.get('geyser_clone'):continue
    pos=Vec3(self.cog_nodes[i].getPos());miss=i in event.get('misses',[])
    mound,_=self.movie_prop('geyser',None);water,_=self.movie_prop('geyser',None)
    for pattern in ('**/Splash*','**/spout'):
     for part in mound.findAllMatches(pattern):part.removeNode()
    for pattern in ('**/hole','**/shadow'):
     for part in water.findAllMatches(pattern):part.removeNode()
    mound.setPos(pos);mound.setScale(.6);water.setPos(pos);water.setScale(.001)
    clips.append(Sequence(Wait(2.5+delay),Func(mound.show),Func(water.show),LerpScaleInterval(water,1,1.8*.6),Wait(.25 if miss else .75),LerpScaleInterval(water,.5,.001),LerpScaleInterval(mound,.5,.001),Func(water.hide),Func(mound.hide)))
    if not miss:
     node=self.cog_nodes[i];origin=Vec3(node.getPos())
     from scene_art import MODELS
     actor=self.cog_actors[i];hold_frame=16 if MODELS[self.game.cogs[i].name]['body']=='A' else 15
     # MovieSquirt.__getSuitTrack: slow wind-up, held flail frame, native recovery.
     reaction=Sequence(ActorInterval(actor,'slip-backward',playRate=.5,startFrame=0,endFrame=hold_frame-1),Func(actor.pose,'slip-backward',hold_frame),Wait(.5),ActorInterval(actor,'slip-backward',startFrame=hold_frame),Func(self.restore_cog_pose,i))
     peak=origin+Vec3(0,0,14*actor.getScale(self.render).z)
     clips.append(Sequence(Wait(impact+delay),Parallel(reaction,Sequence(LerpPosInterval(node,1.1,peak),LerpPosInterval(node,.6,origin)))))
  clips.append(Sequence(Wait(1.8),self.sound_clip('AA_squirt_Geyser.ogg')))
  event['geyser_contacts']={i:impact+delay for i,delay in delays.items()}
  affected=set() if event.get('suppress_health') else shown|{i for kind,i,n in event['health'] if kind=='cog'}|set(event.get('misses',[]))
  for i in affected:
   delay=delays.get(i,0)
   health=dict(event,health=[h for h in event['health'] if h[0]=='cog' and h[1]==i],misses=[i] if i in event.get('misses',[]) else [],custom_cog_reaction=True,dodge_at=1.8+delay)
   clips.append(self.health_movie(health,impact+delay))
  return Parallel(*clips)
 def presentation_movie(self,event):
  clips=[];reacted=set()
  presentation_targets={i for a in event.get('actions',[]) if a.gag=='Presentation' for i in event.get('targets',{}).get(a.toon,[])}
  for action in event.get('actions',[]):
   if action.gag!='Presentation':
    targets=dict(event.get('targets',{}));targets[action.toon]=[i for i in targets.get(action.toon,[]) if i not in presentation_targets]
    clips.append(self.base_gag_movie(dict(event,actions=[action],targets=targets,health=[],misses=[])))
    continue
   index=action.toon
   screen,_=self.movie_prop('slideshow',None)
   screen.setPos(self.toon_nodes[index].getPos()+Vec3(0,2.5,.08));screen.setScale(.06)
   clips.append(Parallel(self.toon_clip(index,'pushbutton',3.5),self.hand_prop(index,'button',3.5,.4)))
   clips.append(Sequence(Wait(2.5),Func(screen.show),LerpScaleInterval(screen,1.2,.6),Wait(3),LerpScaleInterval(screen,.4,Vec3(.6,.6,.06)),Func(screen.hide)))
   clips.append(Sequence(Wait(2.3),self.sound_clip('TL_presentation.ogg')))
   clips.append(Sequence(Wait(2.5),self.sound_clip('AA_drop_trigger_box.ogg',.67)))
   for target in event.get('targets',{}).get(index,[]):
    if target not in event.get('misses',[]) and target not in reacted:
     reacted.add(target)
     # Source __lureSlideshow uses native playback for 3.1 seconds.
     # cog_clip rescales a whole clip into that duration and changes the motion.
     actor=self.cog_actors[target];node=self.cog_nodes[target]
     clips.append(Sequence(Wait(3.8),ActorInterval(actor,'hypnotized',duration=3.1),Func(self.restore_cog_pose,target)))
     destination=getattr(self,'lure_movie_destinations',{}).get(target,2.2)
     clips.append(Sequence(Wait(5.5),LerpPosInterval(node,.7,Vec3(node.getX(),destination,node.getZ()))))
  clips.append(self.health_movie(event,5.5))
  return Parallel(*clips)
 def gag_movie(self,event):
  from sos_movies import wrap_track
  regular=dict(event,health=event.get('regular_health',event['health']),
               lure_before=event.get('regular_lure_before',event.get('lure_before',[])),
               trap_before=event.get('regular_trap_before',event.get('trap_before',[])))
  movie=wrap_track(self,event,self.base_gag_movie(regular))
  # MovieThrow/Squirt/Trap/Drop face the target before performing, then
  # restore the formation heading. Group throws face the average target.
  # Toon-Up already handles facing after walking to the center.
  if event['track']=='Toon-Up':return movie
  headings={a.toon:Vec3(self.toon_nodes[a.toon].getHpr()) for a in event.get('actions',[])}
  def face_targets():
   for action in event.get('actions',[]):
    targets=event.get('targets',{}).get(action.toon,[])
    if not targets:continue
    node=self.toon_nodes[action.toon]
    points=[self.cog_nodes[i].getPos(node.getParent()) for i in targets]
    target=sum(points,Vec3(0,0,0))/len(points)
    target.z=node.getZ()
    if (target-node.getPos()).lengthSquared()>.0001:node.headsUp(target)
  def restore():
   for index,hpr in headings.items():self.toon_nodes[index].setHpr(hpr)
  return Sequence(Func(face_targets),movie,Func(restore))
 def base_gag_movie(self,event):
  if event.get('track')=='Lure':
   from lure_targets import fresh_targets
   event=dict(event,targets={toon:fresh_targets(event,targets) for toon,targets in event.get('targets',{}).items()})
  if event['track']=='Toon-Up' and not event.get('actions'):
   return self.health_movie(event,2)
  if event['track']=='Toon-Up' and not event.get('centered'):
   scenes=[]
   for action in event.get('actions',[]):
    node=self.toon_nodes[action.toon];origin=Vec3(node.getPos());heading=Vec3(node.getHpr())
    targets=event.get('targets',{}).get(action.toon,[])
    single=dict(event,actions=[action],centered=True)
    if len(event.get('actions',[]))>1:
     # Attribute each healing result only once while retaining sequential performers.
     single['health']=event.get('health_by_action',{}).get(action.toon,event['health'] if action==event['actions'][-1] else [])
    face=Func(node.setH,180) if __import__('battle_engine').GAGS[action.gag].group or not targets else Func(node.headsUp,self.toon_nodes[targets[0]])
    scenes.append(Sequence(Func(node.headsUp,Vec3(0,0,0)),Parallel(self.toon_clip(action.toon,'run',1),LerpPosInterval(node,1,Vec3(0,0,0))),face,self.base_gag_movie(single),Func(node.headsUp,origin),Parallel(self.toon_clip(action.toon,'run',1),LerpPosInterval(node,1,origin)),Func(node.setHpr,heading)))
   return Sequence(*scenes)
  from trap_movies import triggered,activate,place
  if event['track']=='Trap':return place(self,event)
  traps=triggered(self,event) if event['track']=='Lure' else {}
  if traps and not event.get('trap_windup'):
   previous=getattr(self,'lure_movie_destinations',{})
   self.lure_movie_destinations={**previous,**{i:self.placed_traps[i][0].getY(self.characters) if name=='Trapdoor' and i in self.placed_traps else 2.2 for i,name in traps.items()}}
   try:windup=self.base_gag_movie(dict(event,health=[],trap_windup=True))
   finally:self.lure_movie_destinations=previous
   return activate(self,event,traps,windup)
  if any(a.gag=='Geyser' for a in event.get('actions',[])):return self.geyser_movie(event)
  if event['track']=='Lure' and getattr(self,'railroad_targets',set()) and any(k=='cog' and i in self.railroad_targets and n<0 for k,i,n in event['health']):return self.railroad_trigger_movie(event)
  if any(a.gag=='Presentation' for a in event.get('actions',[])):return self.presentation_movie(event)
  if event['track']!='Trap':
   from audited_gags import track_movie
   return track_movie(self,event)
 def play_unite_effect(self,index,name,recipients=None):
  from unite_effects import play
  return play(self,index,name,recipients if recipients is not None else [i for i,t in enumerate(self.game.toons) if t.alive])
 def synergy_dodge(self,index):
  clips=[]
  for actor in self.toon_actors[index].values():
   if 'jump' in actor.getAnimNames():clips.append(Sequence(ActorInterval(actor,'jump',startTime=0,endTime=.6),ActorInterval(actor,'jump',startTime=.6,endTime=.91,playRate=.31/1.3),ActorInterval(actor,'jump',startTime=.91)))
  return Sequence(Parallel(*clips),Func(self.play_toon_animation,index,'idle',True))
 def source_particle(self,name,index):
  self.enableParticles()
  effect=ParticleEffect();effect.loadConfig(Filename.fromOsSpecific(str(ROOT/'assets/particle_effects'/f'{name}.ptf')))
  effect.setName('source-effect-'+name)
  self.movie_particles=getattr(self,'movie_particles',[])+[effect]
  return effect
 def power_synergy_movie(self,event):
  index=event['cog'];synergy=event['name']=='Synergy';owner=self.cog_actors[index]
  anim=MOVIES['suits'][self.game.cogs[index].name]['attacks'][event['name']]
  duration=max(3.5,owner.getDuration(anim));impact=1.7 if synergy else 1.8
  event=dict(event,dodge_at=.91 if synergy else 1.29,reaction='slip-forward')
  clips=[self.cog_clip(index,anim,duration),self.attack_caption(index,event['name'],duration),self.health_movie(event,impact)]
  if synergy:
   for name,delay in [('synergy',1),('synergyWaterfall',.8)]:
    effect=self.source_particle(name,index)
    clips.append(Sequence(Wait(delay),Func(effect.start,owner),Wait(1.9),Func(effect.softStop),Wait(1.6),Func(effect.disable)))
   clips.append(Sequence(Wait(.9),self.sound_clip('SA_synergy.ogg')))
   if any(k=='toon' and n<0 for k,i,n in event['health']):clips.append(Sequence(Wait(2.2),self.sound_clip('Toon_bodyfall_synergy.ogg')))
  else:
   for name,angle in [('powertrip',-60),('powertrip2',60)]:
    effect=self.source_particle(name,index);effect.setPos(0,6.1,.4);effect.setHpr(angle,0,0)
    renderer=effect.getParticlesNamed('particles-1').renderer;renderer.setCenterColor(Vec4(.1,.1,.1,.4));renderer.setEdgeColor(Vec4(.4,.1,.9,.7))
    from direct.interval.LerpInterval import LerpFunc
    clips.append(Sequence(Wait(1),Func(effect.start,owner),Wait(.4),LerpPosInterval(effect,1,Vec3(0,15,.4)),LerpFunc(effect.setAlphaScale,fromData=1,toData=0,duration=.4),Func(effect.disable)))
   effect=self.source_particle('waterfall',index);effect.setScale(11)
   if self.game.cogs[index].name=='Mr. Hollywood':effect.setPos(0,4,3.6)
   renderer=effect.getParticlesNamed('particles-1').renderer;renderer.setCenterColor(Vec4(.1,.1,.1,.4));renderer.setEdgeColor(Vec4(.4,.1,.9,.7))
   clips.append(Sequence(Wait(.6),Func(effect.start,owner),Wait(1.3),Func(effect.softStop),Wait(.3),Func(effect.disable)))
  return Parallel(*clips)
 def tee_off_movie(self,event):
  index=event['cog'];owner=self.cog_actors[index]
  duration=owner.getDuration('golf-club-swing');impact=max(2,duration-2.25)
  event=dict(event,dodge_at=max(0,duration-4.35),dodge='duck')
  ball,_=self.movie_prop('golf-ball',None)
  def place():
   ball.reparentTo(owner);ball.setPos({'Yesman':2.1,'The Big Cheese':4.1,'The Mingler':3.2,'Robber Baron':4.2}.get(self.game.cogs[index].name,2.1),0,.1);ball.setScale(1.5);ball.show()
  target=event['targets'][0];dest=self.toon_nodes[target].getPos(self.render)+Vec3(0,0,2.2)
  if target in event['misses']:dest+=Vec3(1.5,0,1)
  flight=Sequence(Wait(1.7),Func(place),Wait(max(0,impact-.4-1.7)),Func(ball.wrtReparentTo,self.render),LerpPosInterval(ball,.4,dest),Func(ball.hide))
  heading=Vec3(self.cog_nodes[index].getHpr())
  def face():
   self.cog_nodes[index].headsUp(self.toon_nodes[target]);self.cog_nodes[index].setH(self.cog_nodes[index].getH()-owner.getH())
  body=Sequence(Func(face),ActorInterval(owner,'golf-club-swing'),Func(self.cog_nodes[index].setHpr,heading),Func(self.restore_cog_pose,index))
  return Parallel(body,self.attack_caption(index,event['name'],duration),Sequence(Wait(.5),self.hand_prop(index,'golf-club',max(5.2,duration-.5),cog=True)),flight,Sequence(Wait(4.1),self.sound_clip('SA_tee_off.ogg')),self.health_movie(event,impact))

 def cog_movie(self,event):
  from cog_dialogue import movie
  attack=self.cog_attack_movie(event)
  return Parallel(attack,movie(self,event,attack.getDuration()))
 def cog_attack_movie(self,event):
  if event['name']=='Throw Book':
   from throw_book_movie import movie
   return movie(self,event)
  if event['name']=='Money Talks':
   from money_talks_movie import movie
   return movie(self,event)
  from detailed_cog_props import ATTACKS as prop_attacks
  from detailed_cog_motion import ATTACKS as motion_attacks
  if event['name'] in prop_attacks:
   from detailed_cog_props import movie
   return movie(self,event)
  if event['name'] in motion_attacks:
   from detailed_cog_motion import movie
   return movie(self,event)
  if event['name']=='Canned':
   from canned_movie import movie
   return movie(self,event)
  if event['name']=='Brain Storm':
   from brain_storm_movie import movie
   return movie(self,event)
  if event['name']=='Pink Slip':
   from pink_slip_movie import movie
   return movie(self,event)
  if event['name'] in ('Guilt Trip','Sacked'):
   from guilt_sacked_movies import movie
   return movie(self,event)
  if event['name'] in ('Crunch','Downsize'):
   from crunch_downsize_movies import movie
   return movie(self,event)
  if event['name']=='Schmooze':
   from schmooze_movie import movie
   return movie(self,event)
  if event['name']=='Demotion':
   from demotion_movie import movie
   return movie(self,event)
  if event['name']=='Freeze Assets':
   from freeze_assets_movie import movie
   return movie(self,event)
  if event['name']=='Rubber Stamp':
   from rubber_stamp_movie import movie
   return movie(self,event)
  if event['name']=='Rub Out':
   from rub_out_movie import movie
   return movie(self,event)
  if event['name']=='Fill With Lead':
   from fill_with_lead_movie import movie
   return movie(self,event)
  if event['name'] in ('Bounce Check','Red Tape','Write Off','Liquidate'):
   from classic_cog_movies import movie
   return movie(self,event)
  if event['name']=='Embezzle':
   from embezzle_movie import movie
   return movie(self,event)
  if event['name']=='Beguile':
   from beguile_movie import movie
   return movie(self,event)
  if event['name']=='Razzle Dazzle':
   from razzle_movie import movie
   return movie(self,event)
  if event['name'] in ('Power Trip','Synergy'):return self.power_synergy_movie(event)
  if event['name']=='Tee Off':return self.tee_off_movie(event)
  if event['name']=='Flood the Market':
   from flood_movie import movie
   return movie(self,event)
  from cog_choreography import movie
  return movie(self,event)
 def animate_round(self,actions,before_cogs,before_toons):
  self.clear_movie_props();self.display_cog_hp=list(before_cogs);self.display_toon_hp=list(before_toons)
  for i,toon in enumerate(self.game.toons):self.laff_faces[i].set_health(before_toons[i],toon.maximum)
  movies=[];remaining=list(before_cogs);remaining_toons=list(before_toons);fallen=set()
  for event in getattr(self.game,'movie_events',[]):
   movie=None;event['toon_deaths']=[]
   for kind,index,amount in event['health']:
    if kind=='toon':
     old=remaining_toons[index];remaining_toons[index]=max(0,old+amount)
     if old>0 and not remaining_toons[index]:event['toon_deaths'].append(index);fallen.add(index)
   if event['kind']=='gags' and (event.get('actions') or event.get('support_events') or event['health'] or any(g['track']==event['track'] for g in getattr(self,'sos_guests',{}).values())):movie=self.gag_movie(event)
   elif event['kind']=='cog':movie=self.cog_movie(event)
   elif event['kind']=='support' and any(a.gag=='Fire' for a in event.get('actions',[])):
    movie=Parallel(*(self.fire_movie(a,event) for a in event['actions'] if a.gag=='Fire'))
   elif event['kind']=='support':
    clips=[self.health_movie(event,1.8)]
    for a in event.get('actions',[]):
     anim='remoteAttack' if 'remote' in a.gag.lower() else 'callPet' if a.gag.startswith('Doodle:') else 'pushbutton' if a.gag=='Fire' else 'takePhone'
     clips.append(self.toon_clip(a.toon,anim,2.4))
     if anim=='remoteAttack':clips.append(self.hand_prop(a.toon,'remote',2.4))
     if anim=='takePhone' and 'receiver' in MOVIES['props']:clips.append(self.hand_prop(a.toon,'receiver',2.4,.5))
    movie=Parallel(*clips)
   elif event['health']:movie=self.health_movie(event,.5)
   deaths=[]
   for kind,index,amount in event['health']:
    if kind=='cog':
     old=remaining[index];remaining[index]=max(0,old+amount)
     fired=any(a.gag=='Fire' for a in event.get('actions',[]))
     if old>0 and not remaining[index] and not fired:deaths.append(self.cog_defeat(index,duck=False))
   # Lure transitions are determined by the engine event, without rerolling outcomes.
   transition=self.lure_transition(event)
   if movie is not None or deaths or transition.getDuration():movies.append(Sequence(movie or Wait(0),transition,Parallel(*deaths,self.defeat_ducks() if deaths else Wait(0))))
  if not movies and self.game.health_events:movies.append(self.health_movie({'health':self.game.health_events,'kind':'gags','misses':[]},.5))
  departures=[]
  for i,(old,toon) in enumerate(zip(before_toons,self.game.toons)):
   if old>0 and not toon.alive and i not in fallen:
    departures.append(Sequence(Func(self.play_toon_animation,i,'lose'),Wait(5.333),LerpScaleInterval(self.toon_nodes[i],1.5,.01,blendType='easeInOut'),Func(self.toon_nodes[i].hide)))
  self.animation=Sequence(*movies,Parallel(*departures),Func(self.hide_defeated),self.formation_interval(),Func(self.clear_movie_props),Func(self.finish_round));self.animation.start()
 def play_next_event(self):
  """Resolve only the next event; later attacks see any intervening Unite."""
  self.clear_movie_props(include_unites=False)
  before=[t.hp for t in self.game.toons]
  log_start=len(self.game.log)
  try:event=next(self.round_events)
  except StopIteration:
   self.animation=Sequence(Func(self.hide_defeated),self.formation_interval(),Func(self.finish_round));self.animation.start();return
  if event is None:return self.play_next_event()
  event['live']=True
  # Defer Toon HP changes until impact, allowing emergency healing during the wind-up.
  for i,t in enumerate(self.game.toons):t.hp=before[i]
  if event['kind']=='cog':
   self.game.log[log_start:]=[line for line in self.game.log[log_start:] if ' uses ' not in line or 'dodged!' in line]
  movie=None
  if event['kind']=='gags' and (event.get('actions') or event.get('support_events') or event['health'] or any(g['track']==event['track'] for g in getattr(self,'sos_guests',{}).values())):movie=self.gag_movie(event)
  elif event['kind']=='cog':movie=self.cog_movie(event)
  elif event['kind']=='support':
   clips=[];remote_sound_duration=0
   for a in event.get('actions',[]):
    if a.gag.startswith('SOS: '):
     from sos_movies import support_movie
     clips.append(support_movie(self,a,event));continue
    if a.gag=='Fire':clips.append(self.fire_movie(a,event));continue
    if a.gag.startswith('Doodle:'):
     from pet_movies import doodle_movie
     clips.append(doodle_movie(self,a,event));continue
    anim='remoteAttack' if 'remote' in a.gag.lower() else 'callPet' if a.gag.startswith('Doodle:') else 'takePhone'
    if anim=='remoteAttack' and a.target is not None:
     self.sync_remote_visuals()
     controlled=self.cog_actors[a.target]
     duration=controlled.getDuration('seizecontrol')
     clips.append(Sequence(Wait(.8),ActorInterval(controlled,'seizecontrol'),Func(controlled.loop,'controlidle')))
     remote_sound_duration=max(remote_sound_duration,duration)
    toon_duration=max(actor.getDuration(anim) for actor in self.toon_actors[a.toon].values() if anim in actor.getAnimNames()) if anim=='remoteAttack' else 2.4
    clips.append(self.toon_clip(a.toon,anim,toon_duration))
    if anim in ('remoteAttack','takePhone'):clips.append(self.hand_prop(a.toon,'remote' if anim=='remoteAttack' else 'receiver',toon_duration))
   if remote_sound_duration:clips.extend([self.sound_clip('AA_remote_control.ogg'),Sequence(Wait(.8),self.sound_clip('SA_remote_control.ogg'))])
   if not any(a.gag=='Fire' or a.gag.startswith(('Doodle:','SOS: ')) for a in event.get('actions',[])):clips.append(self.health_movie(event,1.8))
   movie=Parallel(*clips)
  elif event['kind']=='remote':movie=self.remote_movie(event)
  elif event['health']:movie=self.health_movie(event,.5)
  layers=event.get('layer_changes',[])
  deaths=[];dead_indices=set()
  for kind,index,amount in event['health']:
   if kind=='cog' and amount<0 and self.game.cogs[index].hp==0 and index not in layers and index not in dead_indices and not any(a.gag in ('Fire','SOS: Lord Lowden Clear') for a in event.get('actions',[])):
    deaths.append(self.cog_defeat(index,duck=False));dead_indices.add(index)
  changes=[self.layer_movie(index) for index in layers]
  self.animation=Sequence(movie or Wait(0),self.lure_transition(event),Parallel(*deaths,*changes,self.defeat_ducks() if deaths or changes else Wait(0)),Func(self.after_live_event));self.animation.start()

 def after_live_event(self):
  remaining=max((max(0,clip.getDuration()-clip.getT()) for clip in getattr(self,'live_departures',[]) if clip.isPlaying()),default=0)
  if remaining:
   self.animation=Sequence(Wait(remaining+.05),Func(self.after_live_event));self.animation.start();return
  self.live_departures=[]
  self.sync_remote_visuals()
  self.sync_railroad()
  from trap_movies import sync
  sync(self)
  self.animation=Sequence(Func(self.hide_defeated),self.formation_interval(),Func(self.play_next_event));self.animation.start()

 def live_health(self,event,kind,index,amount):
  if kind=='cog':
   self.show_health_event(kind,index,amount)
   if not event.get('damage_components',{}).get(index):self.float_text(self.cog_nodes[index],amount,4)
   if amount<0 and event.get('kind')!='support' and not event.get('custom_cog_reaction'):
    reaction=self.cog_damage_reaction(event,index)
    self.live_departures=getattr(self,'live_departures',[])+[reaction];reaction.start()
   return
  toon=self.game.toons[index];old=toon.hp
  amount=-event['raw_toon_damage'][index] if event['kind']=='cog' and index in event.get('raw_toon_damage',{}) else amount
  toon.hp=max(0,min(toon.maximum,old+amount));actual=toon.hp-old
  self.display_toon_hp[index]=old;self.show_health_event(kind,index,actual)
  if actual:self.float_text(self.toon_nodes[index],actual)
  if event['kind']=='cog':self.game.log.append(f"{self.game.cogs[event['cog']].name} uses {event['name']} → {toon.name}: {actual} Laff."+(' SAD!' if not toon.alive else ''))
  if not toon.alive:
   for track in event.get('custom_toon_tracks_by_index',{}).get(index,event.get('custom_toon_tracks',[])):track.pause()
   restore=event.get('toon_movie_restore',{}).get(index)
   if restore:restore()
   if hasattr(self,'team_card_roots'):self.team_card_roots[index].hide()
  if actual<0 and (not event.get('custom_toon_reaction') or not toon.alive):
   anim=event.get('reaction',MOVIES.get('attack_timing',{}).get(re.sub('[^a-z0-9]','',event.get('name','').lower()),{}).get('reaction','conked'))
   duration=max((a.getDuration(anim) for a in self.toon_actors[index].values() if anim in a.getAnimNames()),default=.9)
   reaction=self.toon_defeat(index) if not toon.alive else self.toon_damage_reaction(event,index)
   self.live_departures=getattr(self,'live_departures',[])+[reaction];reaction.start()

 def layer_movie(self,index):
  old=self.cog_actors[index]
  def replace():
   old.hide();new=self.art.cog(self.game.cogs[index],self.cog_nodes[index]);self.cog_actors[index]=new
   self.display_cog_hp[index]=self.game.cogs[index].hp;self.cog_nodes[index].show()
  return Sequence(self.cog_defeat(index,duck=False),Func(replace))

 def sync_remote_visuals(self,override=None):
  override=override or {}
  visuals=getattr(self,'remote_visuals',{})
  for i,(owner,antenna) in list(visuals.items()):
   if i>=len(self.game.cogs) or (not self.game.cogs[i].alive and i not in override) or not override.get(i,self.game.cogs[i].remote) or owner is not self.cog_actors[i]:
    antenna.cleanup();antenna.removeNode()
    if antenna in self.art.actors:self.art.actors.remove(antenna)
    del visuals[i]
  for i,cog in enumerate(self.game.cogs):
   if (not cog.alive and i not in override) or not override.get(i,cog.remote) or i in visuals:continue
   owner=self.cog_actors[i];neck=owner.find('**/joint_head')
   if neck.isEmpty():neck=owner
   antenna=Actor(str(SOURCE/'ttr_r_prp_bat_antenna.bam'),{name:str(SOURCE/f'ttr_a_prp_bat_antenna_{name}.bam') for name in ('open','speak')})
   antenna.setName('remote-antenna');antenna.reparentTo(neck)
   # The extracted base is centered at Y=-.17504, not at the rig origin.
   antenna.setPos(owner.getPythonTag('remote-head-anchor')+Vec3(0,.17504,0))
   # Frames 0..12 extend; the rest retract. Retain the extended pose.
   antenna.play('open',fromFrame=0,toFrame=12);self.art.actors.append(antenna);visuals[i]=(owner,antenna)
  for owner,antenna in visuals.values():
   antenna.show()
   if not antenna.getCurrentAnim():antenna.pose('speak',0)
  self.remote_visuals=visuals

 def remote_movie(self,event):
  index=event['cog'];kind=event.get('remote_kind','Healing')
  self.sync_remote_visuals({index:event['remote_before']} if event.get('remote_before') else None)
  candidates=('song-and-dance',) if kind=='Healing' else ('speak',)
  actor=self.cog_actors[index];anim=next((a for a in candidates if a in actor.getAnimNames()),'idle')
  duration=actor.getDuration(anim)
  impact=1.6 if kind=='Healing' else max(0,duration-.5)
  antenna=self.remote_visuals.get(index)
  antenna_clip=ActorInterval(antenna[1],'speak') if antenna else Wait(0)
  bubble_clip=Wait(0)
  if kind=='Damage' and antenna:
   bubble=Actor(str(SOURCE/'ttr_r_prp_bat_antennaBubble.bam'),{n:str(SOURCE/f'ttr_a_prp_bat_antennaBubble_{n}.bam') for n in ('open','speak')})
   origin=antenna[1].find('**/def_M_bubbleOrigin_01')
   bubble.reparentTo(origin if not origin.isEmpty() else antenna[1]);bubble.setName('remote-joke-bubble');bubble.setBillboardPointEye();bubble.setLightOff();bubble.hide()
   self.movie_props.append((bubble,bubble))
   # The animated speech effect and its 2.709s recording share a
   # timeline. Punchline begins when this 2.708s channel finishes.
   impact=bubble.getDuration('speak')
   bubble_clip=Sequence(Func(bubble.show),ActorInterval(bubble,'speak'),Func(bubble.hide))
  body=self.cog_clip(index,anim,duration) if kind=='Healing' else Sequence(ActorInterval(actor,'speak'),Func(self.restore_cog_pose,index))
  audio=self.sound_clip('SA_song_and_dance.ogg') if kind=='Healing' else Parallel(self.sound_clip('ttr_s_prp_bat_antennaBubble_speak.ogg'),Sequence(Wait(impact),self.sound_clip('ttr_s_prp_bat_antennaBubble_badJoke.ogg')))
  from cog_dialogue import remote_joke
  dialogue=remote_joke(self,event,impact,duration) if kind=='Damage' else Wait(0)
  return Parallel(antenna_clip,bubble_clip,audio,body,dialogue,self.attack_caption(index,'Song and Dance' if kind=='Healing' else 'Tell a Joke!',duration),self.health_movie(event,impact))

 def formation_interval(self):
  clips=[]
  for node,pos in self.formation_positions():
   if (node.getPos()-pos).length()<.01:continue
   toon=node in self.toon_nodes;index=(self.toon_nodes if toon else self.cog_nodes).index(node)
   heading=-90 if pos.x>node.getX() else 90
   if not toon:heading+=180
   duration=max(.65,(pos-node.getPos()).length()/4)
   walk=self.toon_clip(index,'walk',duration) if toon else self.cog_clip(index,'walk',duration)
   if toon and 'AV_footstep_walkloop.ogg' in MOVIES['audio']:walk=Parallel(walk,self.sound_clip('AV_footstep_walkloop.ogg',duration))
   clips.append(Sequence(LerpHprInterval(node,.12,Vec3(heading,0,0)),Parallel(walk,LerpPosInterval(node,duration,pos)),LerpHprInterval(node,.12,Vec3(0,0,0))))
  return Parallel(*clips)
