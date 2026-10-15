"""NPC access to the same resource-backed gag builders as player Toons."""
from types import MethodType,SimpleNamespace
from direct.interval.IntervalGlobal import Sequence,Parallel,Func,Wait,LerpPosInterval,LerpScaleInterval
from panda3d.core import Vec3
# Classic high-tier movie choices, with verified special-card identities.
# Per-tier TTR alternatives need footage before replacing these reference choices.
GAG_MOVIES={
 'Madam Chuckle':'Juggling Cubes','Daffy Don':'Juggling Cubes','Flippy':'Juggling Cubes',
 'Clerk Will':'TNT','Clerk Penny':'TNT','Clerk Clara':'TNT',
 'Stinky Ned':'Hypno-goggles','Nancy Gas':'Hypno-goggles','Lil Oldman':'Hypno-goggles',
 'Barbara Seville':'Foghorn','Sid Sonata':'Foghorn','Moe Zart':'Foghorn',
 'Clumsy Ned':'Grand Piano','Franz Neckvein':'Grand Piano','Barnacle Bessie':'Grand Piano',
 'Rocky':'Wedding Cake','Loopy Loopenloop':'Geyser'}
class NPCView:
 def __init__(self,app,index,guest):
  object.__setattr__(self,'app',app)
  nodes=list(app.toon_nodes);nodes[index]=guest['root']
  actors=list(app.toon_actors);actors[index]=guest['actors']
  object.__setattr__(self,'toon_nodes',nodes);object.__setattr__(self,'toon_actors',actors)
 def __getattr__(self,name):
  value=getattr(self.app,name)
  if isinstance(value,MethodType) and value.__self__ is self.app:return MethodType(value.__func__,self)
  return value
 def __setattr__(self,name,value):setattr(self.app,name,value)

def gag_performance(app,index,guest):
 from battle_engine import Action,GAGS
 from audited_gags import BUILDERS
 gag=GAG_MOVIES[guest['action'].gag[5:]];track=guest['track'];proxy=NPCView(app,index,guest)
 targets=[i for i,c in enumerate(app.game.cogs) if app.display_cog_hp[i]>0 and not (track=='Drop' and c.lure)]
 if track=='Trap':targets=[i for i,c in enumerate(app.game.cogs) if c.trap and c.trap[0]==guest['action'].gag]
 owned=guest.get('event')
 if track=='Lure' and owned:
  from lure_targets import fresh_targets
  targets=fresh_targets(owned,targets)
 action=Action(index,gag)
 event={'kind':'gags','track':track,'actions':[action],'targets':{index:targets},'health':[],'misses':[],'custom_cog_reaction':True}
 if track=='Lure' and owned and owned.get('health'):
  # The trap owns damage/reaction timing when the NPC's Lure springs it.
  # Use the same TNT/ordinary-trap/Railroad dispatcher as player Lure.
  guest['handles_health']=True
  return proxy.base_gag_movie({**owned,**event,'health':owned['health'],'live':owned.get('live',False)})
 if track=='Trap':
  from trap_movies import place
  return place(proxy,event)
 if track=='Drop':
  # MovieDrop staggers target groups by TOON_DROP_SUIT_DELAY (1 second).
  # repeatNPC suppresses repeated button/Toon tracks, not the later props.
  clips=[];guest['impacts']={}
  for slot,target in enumerate(targets):
   clip,impact=BUILDERS[track](proxy,action,[target],[],animate_toon=slot==0)
   clips.append(Sequence(Wait(slot),clip));guest['impacts'][target]=slot+impact
  guest['impact']=max(guest['impacts'].values(),default=0)
  return Parallel(*clips)
 if gag=='Geyser':
  # Loopy uses the same randomized per-Cog eruptions as a regular Geyser.
  # Return each contact to the SOS health owner instead of applying all HP
  # at the shared 2.9-second wind-up boundary.
  event.update(scheduled_geyser=True,suppress_health=True)
  clip=proxy.geyser_movie(event)
  guest['impacts']=event['geyser_contacts']
  guest['impact']=max(guest['impacts'].values(),default=2.9)
  return clip
 if gag=='Presentation':
  guest['impact']=5.5
  return proxy.presentation_movie(event)
 if track=='Toon-Up':targets=[i for i,t in enumerate(app.game.toons) if t.alive]
 clip,impact=BUILDERS[track](proxy,action,targets,[])
 guest['impact']=impact
 if track=='Toon-Up':
  # Arrival ends facing the Cog line. Healing guests perform toward the
  # actual Toon team (including the caller), not NPCView's replaced slot.
  def face_toons():
   root=guest['root']
   points=[app.toon_nodes[i].getPos(root.getParent()) for i in targets]
   if points:
    center=sum(points,Vec3(0,0,0))/len(points);center.z=root.getZ()
    if (center-root.getPos()).lengthSquared()>.0001:root.headsUp(center)
  return Sequence(Func(face_toons),clip)
 return clip

def support_performance(app,index,guest):
 from audited_gags import perform,held,sound_for
 root=guest['root'];proxy=NPCView(app,index,guest);sequence=Sequence()
 targets=([node for i,node in enumerate(app.cog_nodes) if app.display_cog_hp[i]>0]
          if guest['track']=='Cogs Miss' else [node for i,node in enumerate(app.toon_nodes) if app.game.toons[i].alive])
 if guest['track'].startswith('Restock'):
  return restock_performance(app,index,guest,targets)
 return accuracy_performance(app,index,guest,targets)


def accuracy_performance(app,index,guest,targets):
 """One sprinkle performance; every living recipient receives it together."""
 from audited_gags import perform,sound_for
 if not targets:return Wait(0)
 root=guest['root'];proxy=NPCView(app,index,guest)
 def face_team():
  center=sum((n.getPos(root.getParent()) for n in targets),Vec3(0,0,0))/len(targets)
  delta=center-root.getPos();delta.z=0
  root.headsUp(root.getPos()+Vec3(-delta.y,delta.x,0))
 clips=[Sequence(Func(face_team),perform(proxy,index,'sprinkle-dust',5.25)),
        Sequence(Wait(2),app.sound_clip(sound_for('Toon-Up',5),3.1))]
 effects=[('pixieSpray',1.5,.5,root),('pixieExplode',2.7,1,root),('pixieWall',4.05,1.2,root)]
 for target in targets:
  effects.extend([('pixieDrop',1.9,2,target),('pixiePoof',3.4,1,target)])
 for name,delay,hold,parent in effects:
  effect=app.source_particle(name,index)
  effect.setScale(effect.getScale()*.5);effect.setPos(effect.getPos()*.5)
  clips.append(Sequence(Wait(delay),Func(effect.start,parent),Wait(hold),Func(effect.softStop),Wait(1),Func(effect.disable)))
 if guest['track']=='Cogs Miss':
  from cog_dialogue import speech
  # MovieNPCSOS.__healToon(hp=0) selects MovieHealLaughterHits1 at 2.5s.
  # Text is from the retained TTLocalizerEnglish, not invented attack taunts.
  phrases=('Ha Ha Ha','Hee Hee','Tee Hee','Ha Ha')
  for slot,target in enumerate(targets):
   cog_index=app.cog_nodes.index(target)
   clips.append(Sequence(Wait(2.5),speech(app,cog_index,phrases[slot%len(phrases)],2.75)))
 return Parallel(*clips)


def restock_performance(app,index,guest,targets):
 """One smooch with simultaneous recipients, using the bundled TTR props."""
 from audited_gags import perform,held,sound_for
 if not targets:return Wait(0)
 root=guest['root'];proxy=NPCView(app,index,guest)
 torso=guest['actors']['torso'];duration=torso.getDuration('smooch')
 throw_time=115/torso.getFrameRate('smooch');impact=throw_time+.5
 guest['impact']=impact
 def face_team():
  points=[node.getPos(root.getParent()) for node in targets]
  center=sum(points,Vec3(0,0,0))/len(points);center.z=root.getZ()
  if (center-root.getPos()).lengthSquared()>.0001:root.headsUp(center)
 clips=[perform(proxy,index,'smooch',duration),
  held(proxy,index,'lipstick',duration,pos=(-.27,-.24,-.95),hpr=(-118,-10.6,-25.9))[1],
  Sequence(Wait(2),app.sound_clip(sound_for('Toon-Up',3)))]
 hand=torso.find('**/joint_Rhold')
 for target in targets:
  lips,_=app.movie_prop('lips',None);lips.setBillboardPointEye();lips.setScale(.001)
  lips.setName('restock-lips');lips.setPythonTag('recipient',target)
  def show(lips=lips):
   torso.update(force=True)
   lips.setPos(app.render,hand.getPos(app.render));lips.show()
  # Coordinates are evaluated during playback, after the NPC has arrived.
  def endpoint(target=target):return target.getPos(app.render)+Vec3(0,0,2.5)
  clips.append(Sequence(Wait(2.5),Func(show),LerpScaleInterval(lips,.5,3),
   Wait(max(0,throw_time-3)),LerpPosInterval(lips,.5,endpoint),Func(lips.hide)))
 return Sequence(Func(face_team),Parallel(*clips))
