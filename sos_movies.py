"""NPC SOS guests, using bundled character assets and MovieNPCSOS staging."""
import json
from pathlib import Path
from types import SimpleNamespace
from panda3d.core import Vec3,TextNode
from direct.interval.IntervalGlobal import Sequence,Parallel,Func,Wait,ActorInterval,LerpScaleInterval
from direct.actor.Actor import Actor
from scene_art import configure_head,color_head
from support import SOS,TRACKS
from game_resources import SOURCE,resource
PORTRAITS=json.loads((Path(__file__).parent/'assets/sos_portraits.json').read_text())

def pose(app,guest,anim,duration,reverse=False):
 clips=[]
 for actor in guest['actors'].values():
  if anim in actor.getAnimNames():
   clips.append(ActorInterval(actor,anim,playRate=(-1 if reverse else 1)*max(.01,actor.getDuration(anim)/duration)))
 return Parallel(*clips)

def teleport(app,guest,incoming=False):
 # Toon.getTeleportInTrack/getTeleportOutTrack. One visible LOD here.
 hole=Actor(str(resource('phase_3.5/models/props/portal-mod.bam')),
            {'hole':str(resource('phase_3.5/models/props/portal-chan.bam'))})
 hole.setName('sos-teleport-hole');hole.setLightOff();hole.hide()
 guest.setdefault('props',[]).append(hole)
 legs=guest['actors']['legs']
 def ground():
  hole.reparentTo(legs);hole.setPos(0,-2.4 if incoming else 0,.15)
  # Keep foreground characters in front of the floor portal.
  hole.setBin('fixed',0);hole.setDepthTest(True);hole.setDepthWrite(False);hole.show()
 if incoming:
  body=Parallel(*(ActorInterval(a,'jump',startTime=.45) for a in guest['actors'].values() if 'jump' in a.getAnimNames()))
  return Parallel(Sequence(Func(ground),ActorInterval(hole,'hole',startTime=3.4,endTime=3.1),Wait(.6),ActorInterval(hole,'hole',startTime=3.1,endTime=3.4),Func(hole.hide)),
                  Sequence(Func(legs.hide),Wait(.3),Func(legs.show),body),
                  app.sound_clip('teleport_reappear.ogg'))
 def hand():
  hole.reparentTo(guest['actors']['torso'].find('**/joint_Rhold'))
  hole.setPos(0,0,0);hole.show()
 return Parallel(Sequence(Func(hand),Wait(1.708),Func(ground),Wait(3.4-1.708),Func(hole.hide)),
                 ActorInterval(hole,'hole',duration=3.4),
                 Parallel(*(ActorInterval(a,'teleport',duration=3.4) for a in guest['actors'].values() if 'teleport' in a.getAnimNames())),
                 Sequence(Wait(.5),app.sound_clip('AV_teleport.ogg')))

def remove(app,index):
 guest=getattr(app,'sos_guests',{}).pop(index,None)
 if not guest:return
 for prop in guest.get('props',[]):prop.cleanup();prop.removeNode()
 for actor in guest['actors'].values():
  actor.cleanup()
  if actor in app.art.actors:app.art.actors.remove(actor)
 guest['root'].removeNode()

def arrival(app,action):
 if not hasattr(app,'sos_guests'):app.sos_guests={}
 remove(app,action.toon)
 info=PORTRAITS.get(action.gag,{'dna':'dss','color':(.55,.65,.85,1)})
 species={'c':'cat','m':'mouse','d':'dog','r':'bunny','f':'duck','h':'horse','p':'pig','b':'bear','s':'monkey'}.get(info['dna'][0],'dog')
 root=app.characters.attachNewNode('sos-npc-'+action.gag.removeprefix('SOS: '));root.setPos(app.toon_nodes[action.toon].getPos()+Vec3(0,2.5,0))
 actors=app.art.toon(SimpleNamespace(animal=species),action.toon,root)
 for part,actor in actors.items():
  stem='avt_dog' if part=='head' else 'dgm_'+part
  actor.loadAnims({name:str(resource(f'ttr_a_chr_{stem}_{name}.bam')) for name in ('wave','bow')})
 for actor in actors.values():
  for mesh in actor.findAllMatches('**/+GeomNode'):
   name=mesh.getName().lower()
   if any(n in name for n in ('legs','feet','arms','neck')) and not any(n in name for n in ('eye','pupil','teeth','tongue')):mesh.clearColorScale();mesh.setColor(*info['color'])
 # Apply the same known NPC head variant and color as its SOS card portrait.
 torso=actors['torso'];head=torso.find('**/def_head')
 for child in head.getChildren():
  configure_head(child,'long' if info['dna'][1]=='l' else 'short')
  color_head(child,info['color'],species)
 label=TextNode('sos-npc-name');label.setText(action.gag.removeprefix('SOS: '));label.setFont(app.font);label.setAlign(TextNode.ACenter);label.setTextColor(.05,.25,.85,1)
 tag=root.attachNewNode(label);tag.setPos(0,0,3.3);tag.setScale(.4);tag.setBillboardPointEye();tag.setLightOff()
 guest={'root':root,'actors':actors,'action':action,'track':SOS[action.gag][0],'name_tag':tag};app.sos_guests[action.toon]=guest;root.hide()
 def idle():
  for actor in actors.values():actor.loop('idle')
 return Sequence(Func(root.setH,180),Func(root.show),teleport(app,guest,True),Parallel(pose(app,guest,'wave',1.5),speech(app,guest,'Hi '+app.game.toons[action.toon].name+'! Glad to help!',1.5)),Func(idle),Wait(.5),Func(root.setH,0))

def performance(app,index):
 guest=app.sos_guests[index];track=guest['track'];root=guest['root']
 if track in TRACKS:
  from sos_visuals import gag_performance
  return gag_performance(app,index,guest)
 from sos_visuals import support_performance
 return support_performance(app,index,guest)

def departure(app,index):
 guest=app.sos_guests[index]
 leaving=teleport(app,guest)
 return Sequence(Func(guest['root'].setH,180),pose(app,guest,'bow',1.2),Parallel(leaving,speech(app,guest,'See you later!',leaving.getDuration())),Func(remove,app,index))

def support_movie(app,action,event):
 if action.gag=='SOS: Lord Lowden Clear':
  from lowden_movie import movie
  return movie(app,action,event)
 # Track SOS cards are consumed in the support event, but their guest
 # arrives only when that gag track is presented.
 if SOS[action.gag][0] in TRACKS:return Wait(0)
 arrive=arrival(app,action)
 return Sequence(arrive,Parallel(performance(app,action.toon),app.health_movie(event,2)),departure(app,action.toon))

def wrap_track(app,event,base):
 arrivals=Sequence()
 for owned in event.get('support_events',{}).values():
  action=owned.get('action')
  if action is not None:arrivals.append(arrival(app,action))
 indices=[i for i,g in getattr(app,'sos_guests',{}).items() if g['track']==event['track']]
 if not indices:return base
 for i in indices:
  owned=event.get('support_events',{}).get(i)
  app.sos_guests[i]['event']=dict(owned,live=event.get('live',False)) if owned else None
 clips=[performance(app,i) for i in indices]
 if 'support_events' in event:
  for i in indices:
   owned=event['support_events'].get(i)
   if owned is None:continue
   owned=dict(owned,live=event.get('live',False))
   guest=app.sos_guests[i]
   if guest.get('handles_health'):continue
   if event['track']=='Drop' or guest.get('impacts'):
    clips.extend(app.health_movie(dict(owned,health=[h for h in owned['health'] if h[0]=='cog' and h[1]==target],custom_cog_reaction=True),t) for target,t in guest.get('impacts',{}).items())
   else:
    if guest['action'].gag=='SOS: Loopy Loopenloop':owned['custom_cog_reaction']=True
    clips.append(app.health_movie(owned,guest.get('impact',2)))
  return Sequence(arrivals,Parallel(base,*clips),Parallel(*(departure(app,i) for i in indices)))
 if not event.get('actions'):
  if event['track']=='Drop':
   impacts={}
   for i in indices:
    for target,t in app.sos_guests[i].get('impacts',{}).items():impacts[target]=max(impacts.get(target,0),t)
   base=Parallel(*(app.health_movie(dict(event,health=[h for h in event['health'] if h[0]=='cog' and h[1]==target],misses=[],custom_cog_reaction=True),t) for target,t in impacts.items()))
  else:base=app.health_movie(event,max(app.sos_guests[i].get('impact',2) for i in indices))
 return Sequence(arrivals,Parallel(base,*clips),Parallel(*(departure(app,i) for i in indices)))


def speech(app,guest,phrase,duration):
 from speech_balloon import build
 root=guest['root'].attachNewNode('sos-speech-bubble')
 root.setZ(guest.get('speech_height',3.3));root.setBillboardPointEye();root.setLightOff();root.hide()
 build(app,root,phrase,font=app.font)
 def show():
  root.show()
  if guest.get('name_tag'):guest['name_tag'].hide()
 def hide():
  if not root.isEmpty():root.hide()
  tag=guest.get('name_tag')
  if tag is not None and not tag.isEmpty():tag.show()
 return Sequence(Func(show),Wait(duration),Func(hide))
