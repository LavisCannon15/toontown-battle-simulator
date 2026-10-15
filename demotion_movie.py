"""Classic doDemotion: slowed cringe, frozen hold and snow breakup."""
from panda3d.core import Vec3
from direct.interval.IntervalGlobal import Sequence,Parallel,Func,Wait,ActorInterval
from battle_movies import MOVIES
from game_resources import resource


def reaction(app,index):
 parts=list(app.toon_actors[index].values())
 def segment(start,end,duration):
  clips=[]
  for actor in parts:
   if 'cringe' not in actor.getAnimNames():continue
   fps=actor.getFrameRate('cringe');first=round(start*fps);last=max(first,round(end*fps)-1)
   clips.append(ActorInterval(actor,'cringe',startFrame=first,endFrame=last,playRate=((last-first+1)/fps)/duration))
  return Parallel(*clips)
 def idle():
  if app.game.toons[index].alive:app.play_toon_animation(index,'idle',True)
 return Sequence(segment(0,.5,.5),segment(.5,.9,.5),segment(.9,1.2,.5),segment(1.2,1.5,.6),Wait(2.6),Parallel(*(ActorInterval(a,'cringe',startTime=1.5) for a in parts if 'cringe' in a.getAnimNames())),Func(idle))


def movie(app,event):
 index=event['cog'];target=event['targets'][0];actor=app.cog_actors[index];root=app.cog_nodes[index];toon=app.toon_nodes[target];hit=target not in event['misses']
 anim=MOVIES['suits'][app.game.cogs[index].name]['attacks']['Demotion'];native=actor.getDuration(anim);clips=[];tracks=[]
 art=app.loader.loadModel(str(resource('phase_3.5/models/props/suit-particles.bam')));art.hide();app.movie_props.append((art,None));sprite=art.find('**/snow-particle')
 def particles(name,owner,start,length,face=False):
  effect=app.source_particle(name,index)
  for system in effect.getParticlesList():system.renderer.setFromNode(sprite)
  if face:
   effect.setScale(effect.getScale()*.62)
   head=app.toon_actors[target]['torso'].find('**/def_head');bounds=head.getTightBounds(toon)
   height=(bounds[0].z+bounds[1].z)/2 if bounds and bounds[0] is not None else 2
   effect.setPos(0,0,height)
  clips.append(Sequence(Wait(start),Func(effect.start,owner),Wait(length),Func(effect.softStop),Wait(.7),Func(effect.disable)))
 particles('demotionSpray',actor,.7,1.1)
 if hit:
  particles('demotionFreeze',toon,1.4,2.9,True);particles('demotionUnFreeze',toon,6.65,.5,True)
  r=reaction(app,target)
  def start():
   if not app.game.toons[target].alive:return
   tracks.append(r);app.live_departures=getattr(app,'live_departures',[])+[r];r.start()
  clips.append(Sequence(Wait(1.01),Func(start),Wait(r.getDuration())))
 else:
  # Classic dodge starts at the default near-zero delay, from duck second .8.
  duck=Parallel(*(ActorInterval(a,'duck',startTime=.8) for a in app.toon_actors[target].values() if 'duck' in a.getAnimNames()))
  clips.append(Sequence(Wait(.0001),duck,Func(app.play_toon_animation,target,'idle',True)))
  clips.append(Sequence(Wait(1.6001),app.float_text(toon,0,3,start=False,text='MISSED')))
 e=dict(event,misses=[],custom_toon_reaction=True,custom_toon_tracks=tracks,reaction='cringe')
 clips.extend([app.health_movie(e,2.3),Sequence(Wait(1.2),app.sound_clip('SA_demotion.ogg'))])
 duration=max(native,*[c.getDuration() for c in clips]);heading=Vec3(root.getHpr())
 def face():root.headsUp(toon);root.setH(root.getH()-actor.getH())
 clips.extend([Sequence(Func(face),ActorInterval(actor,anim),Wait(duration-native),Func(root.setHpr,heading),Func(app.restore_cog_pose,index)),app.attack_caption(index,'Demotion',duration)])
 return Parallel(*clips)
