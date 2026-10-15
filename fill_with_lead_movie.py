"""Classic doFillWithLead choreography with bundled TTR props and particles."""
from panda3d.core import Vec3,Vec4,ColorScaleAttrib
from direct.interval.IntervalGlobal import Sequence,Parallel,Func,Wait,ActorInterval
from classic_cog_movies import appear,vanish
from battle_movies import MOVIES
from game_resources import resource


def movie(app,event):
 index=event['cog'];target=event['targets'][0];actor=app.cog_actors[index];root=app.cog_nodes[index];toon=app.toon_nodes[target]
 anim=MOVIES['suits'][app.game.cogs[index].name]['attacks'][event['name']]
 native=actor.getDuration(anim);reaction_tracks=[];hit=target not in event['misses'];clips=[]
 pencil,_=app.movie_prop('pencil',None);sharpener,_=app.movie_prop('sharpener',None)
 clips.append(Sequence(appear(pencil,actor.find('**/joint_Rhold'),(-.29,-.33,-.13),(160.565,-11.653,-169.244),(1,)*3,.7,grow=.2),vanish(pencil,3.2)))
 clips.append(Sequence(appear(sharpener,actor.find('**/joint_Lhold'),(0,0,-.03),(0,0,0),(1,)*3,1.3),vanish(sharpener,2.3)))
 art=app.loader.loadModel(str(resource('phase_3.5/models/props/suit-particles.bam')));art.hide();app.movie_props.append((art,None));sprite=art.find('**/roll-o-dex')
 def particles(name,parent,start,duration,pos=None,scale=1):
  effect=app.source_particle(name,index)
  for system in effect.getParticlesList():system.renderer.setFromNode(sprite);system.renderer.setColor(Vec4(0,0,0,1))
  effect.setScale(scale)
  if pos is not None:effect.setPos(*pos)
  clips.append(Sequence(Wait(start),Func(effect.start,parent),Wait(duration),Func(effect.softStop),Wait(.6 if name.endswith('Smother') else 3.3),Func(effect.disable)))
  return effect
 particles('fillWithLeadSpray',actor,2.5,1.9)
 if hit:
  actors=app.toon_actors[target];head=actors['torso'].find('**/def_head')
  head_meshes=set(head.findAllMatches('**/+GeomNode'))
  torso_meshes=set(actors['torso'].findAllMatches('**/+GeomNode'))-head_meshes
  legs_meshes=set(actors['legs'].findAllMatches('**/+GeomNode'))-torso_meshes-head_meshes
  groups=[head_meshes,torso_meshes,legs_meshes]
  # Mesh heights follow our assembled Toon, rather than stacking all effects
  # at the config's default root-relative location.
  for n,meshes in enumerate(groups):
   bounds=[mesh.getTightBounds(toon) for mesh in meshes if not mesh.isHidden()]
   bounds=[b for b in bounds if b and b[0] is not None]
   height=(min(b[0].z for b in bounds)+max(b[1].z for b in bounds))/2 if bounds else (2,1.2,.5)[n]
   particles('fillWithLeadSmother',toon,3.5+n*.7,1,(0,-(1.5,1,.6)[n]*.62,height),.62)
  saved={}
  def darken(meshes):
   for mesh in meshes:
    if mesh.isEmpty():continue
    if mesh not in saved:saved[mesh]=mesh.getAttrib(ColorScaleAttrib)
    mesh.setColorScale(0,0,0,1)
  def restore():
   for mesh,value in saved.items():
    if mesh.isEmpty():continue
    if value is None:mesh.clearColorScale()
    else:mesh.setAttrib(value)
   saved.clear()
  # Also restore if New Battle cancels the movie while the Toon is darkened.
  app.movie_restorers=getattr(app,'movie_restorers',[])+[restore]
  clips.append(Sequence(Wait(3.7),Func(darken,groups[0]),Wait(.7),Func(darken,groups[1]),Wait(.7),Func(darken,groups[2]),Wait(2.5),Func(restore)))
  # The source flinches before its damage number. Keep sad handling at the
  # damage event, and guard later splice stages against reviving a sad Toon.
  def stage(start,end=None):
   def build():
    if not app.game.toons[target].alive:return
    parts=Parallel(*(ActorInterval(a,'conked',startTime=start,**({'endTime':end} if end is not None else {})) for a in actors.values() if 'conked' in a.getAnimNames()))
    reaction_tracks.append(parts);app.live_departures=getattr(app,'live_departures',[])+[parts];parts.start()
   return Func(build)
  start=max(0,native-1.5)
  clips.append(Sequence(Wait(start),stage(.00001,1.4),Wait(1.4),stage(.7,1.4),Wait(.7),stage(.7,1.4),Wait(.7),stage(1.4)))
 duration=max(native,9.0,*[c.getDuration() for c in clips]);heading=Vec3(root.getHpr())
 def face():root.headsUp(toon);root.setH(root.getH()-actor.getH())
 def idle():
  if app.game.toons[target].alive:app.play_toon_animation(target,'idle',True)
 e=dict(event,reaction='conked',custom_toon_reaction=True,custom_toon_tracks=reaction_tracks,dodge='sidestep-left',dodge_at=max(0,native-3.1))
 clips.extend([Sequence(Func(face),ActorInterval(actor,anim),Wait(duration-native),Func(root.setHpr,heading),Func(app.restore_cog_pose,index)),Sequence(Wait(duration),Func(idle)),app.attack_caption(index,event['name'],duration),app.health_movie(e,4.5 if hit else max(0,native-1.5))])
 return Parallel(*clips)
