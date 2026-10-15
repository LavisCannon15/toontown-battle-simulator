"""Persistent ordinary traps and their source-specific Lure activation reactions."""
from panda3d.core import Vec3
from direct.actor.Actor import Actor
from direct.interval.IntervalGlobal import Sequence,Parallel,Func,Wait,ActorInterval,LerpPosInterval,LerpScaleInterval,LerpHprInterval,LerpFunc
from game_resources import SOURCE
from battle_engine import GAGS
import json
from pathlib import Path
COG_CODES=json.loads((Path(__file__).with_name("cog_art.json")).read_text())
from battle_movies import MOVIES

# MovieUtil distances, converted by the actual Suit model scale rather than
# one fixed offset for all seven props and all Suit bodies.
TRAP_DISTANCES={1:2.6,2:4.5,3:3.7,4:2.6,5:2.6,6:5.1}
RAKE_OFFSETS=dict(zip(('gh','f','cc','tw','bf','sc','ym','mm','tm','nd','pp','bc','b','dt','ac','ds','hh','cr','tbc','bs','sd','le','bw','nc','mb','ls','rb','ms','tf','m','mh'),(1.4,1,.7,1.3,1,.8,.1,.05,.07,.07,.04,.36,.41,.31,.39,.41,.8,2.1,1.4,.4,1.02,1.3,1.4,.6,1.85,1.4,1.6,.7,.75,.9,1.3)))
def trap_position(app,index,level):
 actor=app.cog_actors[index];scale=actor.getScale(app.characters).z
 distance=TRAP_DISTANCES[level]
 if level==2:
  distance+=RAKE_OFFSETS.get(COG_CODES[app.game.cogs[index].name],0)
 pos=Vec3(app.cog_nodes[index].getPos())
 pos.y-=distance*scale;pos.z+=.4*scale if level==6 else .08 if level in (4,5) else .025
 return pos

def thrown(app,action,index):
 level=GAGS[action.gag].level;name=MOVIES['tracks']['Trap'][1][level-1]
 prop,actor=app.movie_prop(name,None);hand=app.toon_actors[action.toon]['torso'].find('**/joint_Rhold')
 release=2.55 if level==1 else 2.5;flight=.9 if level==1 else 1.1 if level==2 else .2
 roll=.8 if level==1 else 1 if level==3 else 0
 target=trap_position(app,index,level);landing=Vec3(target)
 if level==1:landing.y-=2*.6
 if level==3:landing.y+=2*.6
 state={}
 def hold():
  prop.reparentTo(hand);prop.setPos(0,0,0);prop.setHpr(0,0,0);prop.setScale(1);prop.show()
 def release_prop():
  prop.wrtReparentTo(app.characters);state['origin']=Vec3(prop.getPos())
 def arc(t):
  origin=state['origin'];pos=origin+(landing-origin)*t
  if level!=3:pos.z+=.5*32.144*.62*flight**2*t*(1-t)
  prop.setPos(pos)
 motion=Sequence(Func(hold),Wait(release),Func(release_prop),
  Parallel(LerpFunc(arc,fromData=0,toData=1,duration=flight),LerpScaleInterval(prop,flight,.42 if level==2 else .6),LerpHprInterval(prop,flight,Vec3(63.43,-90,63.43) if level==2 else Vec3(0,0,0))))
 if roll:motion.append(LerpPosInterval(prop,roll,target))
 motion.append(Func(prop.hide));motion.append(Func(sync,app,[index]))
 sound={1:'TL_banana.ogg',2:'TL_rake_throw_only.ogg',3:'TL_marbles.ogg'}[level]
 clips=[motion,Sequence(Wait(release+(.1 if level==3 else 0)),app.sound_clip(sound,1.1) if level==2 else app.sound_clip(sound))]
 if actor:clips.append(Sequence(Wait(release),ActorInterval(actor,'prop',startTime=3.2 if level==1 else 3.1 if level==3 else 0,duration=flight+roll)))
 return Parallel(*clips)

def clear(app):
 for root,actor,name in getattr(app,'placed_traps',{}).values():
  if actor:actor.cleanup()
  root.removeNode()
 app.placed_traps={}

def remove_for_cog(app,index):
 saved=getattr(app,'placed_traps',{}).pop(index,None)
 if saved:
  root,actor,_=saved
  if actor:actor.cleanup()
  root.removeNode()
 # Railroad is shared; retain it while another living Cog still owns the trap.
 app.sync_railroad()

def sync(app,indices=None):
 if not hasattr(app,'placed_traps'):app.placed_traps={}
 for i,(root,actor,name) in list(app.placed_traps.items()):
  c=app.game.cogs[i] if i<len(app.game.cogs) else None
  if not c or not c.alive or not c.trap or c.trap[0]!=name:
   if actor:actor.cleanup()
   root.removeNode();del app.placed_traps[i]
 for i,c in enumerate(app.game.cogs):
  if indices is not None and i not in indices:continue
  if not c.alive or not c.trap or c.trap[0]=='Railroad' or i in app.placed_traps:continue
  name=c.trap[0];level=GAGS[name].level if name in GAGS else 6;prop='rake-react' if level==2 else MOVIES['tracks']['Trap'][1][level-1];files=['phase_5/models/props/rake-step-mod.bam','phase_5/models/props/rake-step-chan.bam'] if level==2 else MOVIES['props'][prop]
  root=app.characters.attachNewNode('placed-trap-'+str(i))
  actor=Actor(str(SOURCE/files[0]),{'prop':str(SOURCE/files[1])}) if len(files)>1 else None
  model=actor if actor else app.loader.loadModel(str(SOURCE/files[0]));model.reparentTo(root);model.setScale(.6)
  if actor:actor.pose('prop',0 if prop in ('tnt','rake-react') else actor.getNumFrames('prop')-1)
  # TTR's rake-step bind pose is already flat; the classic 270-degree
  # pitch sends this extracted mesh underground. Keep its native plane.
  if prop=='rake-react':model.setScale(.42)
  if level in (4,5):model.setScale(1.7*app.cog_actors[i].getScale(app.characters).z);model.setLightOff()
  if prop=='marbles':model.setH(94)
  root.setH(app.cog_actors[i].getH(app.characters))
  root.setPos(trap_position(app,i,level))
  if prop=='banana':model.setZ(-.35*.6)
  if prop=='tnt':
   # MovieTrap.placeTrap: (0, 90, 0) in the Suit's coordinate system.
   # Our persistent trap lives under characters, so preserve the Suit heading.
   root.setH(app.cog_actors[i].getH(app.characters));model.setHpr(0,90,0)
   root.setZ(trap_position(app,i,level).z)
  app.placed_traps[i]=(root,actor,name)

def place(app,event):
 clips=[];placement_sounds=set()
 for action in event.get('actions',[]):
  g=GAGS[action.gag]
  if g.level==6:
   from tnt_movie import placement
   clips.append(placement(app,action,event.get('targets',{}).get(action.toon,[])))
   continue
  if g.level==7:
   from audited_gags import perform
   def grow_tracks():
    app.sync_railroad()
    if app.railroad_root:app.railroad_root.setScale(.1)
   def scale_tracks(t):
    if app.railroad_root:app.railroad_root.setScale(t)
   clips.extend([perform(app,action.toon,'pushbutton'),app.hand_prop(action.toon,'button',app.toon_actors[action.toon]['torso'].getDuration('pushbutton')),Sequence(Wait(2.5),Func(grow_tracks),LerpFunc(scale_tracks,fromData=.1,toData=1,duration=1.2)),Sequence(Wait(2.3),app.sound_clip('TL_train_track_appear.ogg')),Sequence(Wait(2.3),app.sound_clip('AA_drop_trigger_box.ogg',.67))]);continue
  from audited_gags import perform
  placed=g.level in (4,5);anim='pushbutton' if placed else 'toss'
  clips.append(perform(app,action.toon,anim))
  if placed:
   clips.append(app.hand_prop(action.toon,'button',app.toon_actors[action.toon]['torso'].getDuration(anim)))
   targets=event.get('targets',{}).get(action.toon,[])
   def grow(t,targets=targets):
    for index in targets:
     saved=app.placed_traps.get(index)
     if saved:saved[0].setScale(t)
   clips.append(Sequence(Wait(2.5),Func(sync,app,targets),LerpFunc(grow,fromData=.01,toData=1,duration=1.2)))
   sound='TL_quicksand.ogg' if g.level==4 else 'TL_trap_door.ogg'
   # Several simultaneous button traps share one audible cue per sound.
   # Keep the source's .3-second gap after the .67-second button excerpt.
   if 'button' not in placement_sounds:
    clips.append(Sequence(Wait(2.3),app.sound_clip('AA_drop_trigger_box.ogg',.67)))
    placement_sounds.add('button')
   if sound not in placement_sounds:
    clips.append(Sequence(Wait(3.27),app.sound_clip(sound,.5)))
    placement_sounds.add(sound)
  else:
   for target in event.get('targets',{}).get(action.toon,[]):clips.append(thrown(app,action,target))
 return Parallel(*clips)

def triggered(app,event):
 before=event.get('trap_before',[])
 return {i:before[i][0] for k,i,n in event.get('health',[]) if k=='cog' and n<0 and i<len(before) and before[i] and before[i][0]!='Railroad'}

def lure_contact(event,index):
 # End of the native Cog reaction, independent of the Toon/prop cleanup.
 times={1:7.0,2:5.71,3:7.0,4:5.71,5:7.0,6:4.7,7:6.9}
 return max((times[GAGS[a.gag].level] for a in event.get('actions',[]) if index in event.get('targets',{}).get(a.toon,[])),default=7.0)+.001

def activate(app,event,targets,windup):
 clips=[]
 for i,name in targets.items():
  level=GAGS[name].level if name in GAGS else 6;node=app.cog_nodes[i];origin=Vec3(node.getPos());land=Vec3(origin.x,2.2,origin.z)
  saved=app.placed_traps.get(i);prop=saved[0] if saved else None
  if level==5:
   body=trapdoor_reaction(app,event,i,prop,origin)
   clips.append(Sequence(Wait(lure_contact(event,i)),body,return_to_formation(app,i,origin)))
   continue
  if level==6:
   from tnt_movie import activation
   body=activation(app,event,i,prop,saved[1] if saved else None,land)
   clips.append(Sequence(Wait(lure_contact(event,i)),body,return_to_formation(app,i,origin)))
   continue
  impact=3.5 if level in (4,5) else 2.3 if level==6 else .5
  health=dict(event,health=[h for h in event['health'] if h[0]=='cog' and h[1]==i],misses=[],custom_cog_reaction=True)
  reaction='rake-react' if level==2 else 'flail' if level in (4,5,6) else 'slip-backward'
  body=[ActorInterval(app.cog_actors[i],reaction,**({'duration':3.125} if level==2 else {})),app.health_movie(health,impact)]
  if level in (4,5):
   body.append(Sequence(Wait(.9 if level==4 else 2.2),LerpPosInterval(node,.8,land-Vec3(0,0,4)),Func(node.hide),Wait(.8),Func(node.setPos,land+Vec3(0,0,5)),Func(node.show),LerpPosInterval(node,.4,land)))
  if level==2 and saved and saved[1]:body.append(ActorInterval(saved[1],'prop'))
  if level==6:
   body.append(Sequence(Wait(2.3),app.positioned_prop('explosion',land+Vec3(0,0,2),.6,2)))
  sound={1:'Toon_bodyfall_synergy.ogg',2:'TL_step_on_rake.ogg',3:'Toon_bodyfall_synergy.ogg',4:'TL_quicksand.ogg',5:'TL_trap_door.ogg',6:'TL_dynamite.ogg'}[level]
  if level in (1,3):body.append(Sequence(app.sound_clip('AA_pie_throw_only.ogg',.55),app.sound_clip(sound)))
  elif level in (4,5):body.append(Sequence(Wait(.7 if level==4 else .8),app.sound_clip(sound),Wait(.1 if level==4 else .8),app.sound_clip('Toon_bodyfall_synergy.ogg')))
  else:body.append(Sequence(Wait(.6),app.sound_clip(sound)))
  clips.append(Sequence(Wait(lure_contact(event,i)),Parallel(*body),return_to_formation(app,i,origin)))
 remaining=dict(event,health=[h for h in event['health'] if h[0]!='cog' or h[1] not in targets],misses=[])
 rest=app.railroad_trigger_movie(dict(remaining,actions=[])) if getattr(app,'railroad_targets',set()) and any(k=='cog' and i in app.railroad_targets and n<0 for k,i,n in remaining['health']) else app.health_movie(remaining,.5)
 return Sequence(Parallel(windup,*clips,Sequence(Wait(windup.getDuration()),rest)),Func(sync,app))

def return_to_formation(app,index,origin):
 # Backwards walking is a recovery only; approach belongs to the Lure movie.
 return Sequence(Parallel(ActorInterval(app.cog_actors[index],'walk',playRate=-1,duration=.5),LerpPosInterval(app.cog_nodes[index],.5,origin)),Func(app.restore_cog_pose,index))


def trapdoor_reaction(app,event,index,prop,origin):
 """MovieLure trapdoor slices; TTR native channels and a visible floor decal."""
 actor=app.cog_actors[index];node=app.cog_nodes[index]
 land=Vec3(prop.getPos(app.characters)) if prop else Vec3(origin.x,2.2,0)
 land.z=origin.z
 scale=actor.getScale(app.characters).z
 sink=land-Vec3(0,0,9.1*scale);drop=land+Vec3(0,0,15*scale)
 # Preserve the reference's spliced .7-second wind-up with .25s of waits.
 windup=Sequence()
 for frame in range(21):
  windup.append(Wait(.25/21))
  windup.append(ActorInterval(actor,'flail',startTime=frame/30,duration=1/30))
 def open_hole():
  if prop and not prop.isEmpty():prop.setColor(0,0,0,1)
 body=Sequence(windup,Func(open_hole),ActorInterval(actor,'flail',startTime=.7,endTime=0),
  ActorInterval(actor,'idle',duration=.5),ActorInterval(actor,'flail',startTime=1.1),
  Wait(1.1),ActorInterval(actor,'slip-forward',duration=2.1))
 move=Sequence(Wait(2.2),LerpPosInterval(node,.4,sink),Func(node.hide),Func(node.setPos,drop),
  Wait(1.6),Func(node.show),LerpPosInterval(node,.3,land))
 health=dict(event,health=[h for h in event['health'] if h[0]=='cog' and h[1]==index],misses=[],custom_cog_reaction=True)
 clips=[body,move,app.health_movie(health,3.5),
  Sequence(Wait(.8),app.sound_clip('TL_trap_door.ogg'),Wait(.8),app.sound_clip('Toon_bodyfall_synergy.ogg'))]
 if prop:clips.append(Sequence(Wait(2.4),LerpScaleInterval(prop,.8,.01)))
 return Parallel(*clips)
