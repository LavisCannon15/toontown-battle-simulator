"""Classic doRubOut and BattleParticles.__makeRubOut with bundled assets."""
from panda3d.core import Vec3,Vec4,ColorScaleAttrib,TransparencyAttrib
from direct.interval.IntervalGlobal import Sequence,Parallel,Func,Wait,ActorInterval,LerpFunc
from classic_cog_movies import appear,vanish
from battle_movies import MOVIES
from game_resources import resource
from scene_art import COLORS


def movie(app,event):
 index=event['cog'];target=event['targets'][0];actor=app.cog_actors[index];root=app.cog_nodes[index];toon=app.toon_nodes[target]
 anim=MOVIES['suits'][app.game.cogs[index].name]['attacks']['Rub Out'];native=actor.getDuration(anim)
 clips=[]
 for name,hand,pos,hpr in [('pad','Lhold',(-.66,.81,-.06),(14.93,-2.29,180)),('pencil','Rhold',(.04,-.38,-.1),(-170.223,-3.762,-62.929))]:
  prop,_=app.movie_prop(name,None)
  clips.append(Sequence(appear(prop,actor.find('**/joint_'+hand),pos,hpr,(1,)*3,.5),vanish(prop,2.57)))
 if target not in event['misses']:
  actors=app.toon_actors[target];head=actors['torso'].find('**/def_head')
  head_meshes=set(head.findAllMatches('**/+GeomNode'))
  torso_meshes=set(actors['torso'].findAllMatches('**/+GeomNode'))-head_meshes
  legs_meshes=set(actors['legs'].findAllMatches('**/+GeomNode'))-head_meshes-torso_meshes
  groups=[head_meshes,torso_meshes,legs_meshes];saved={}
  def restore():
   for mesh,attrs in saved.items():
    if mesh.isEmpty():continue
    for kind,value in attrs:
     if value is None:mesh.clearAttrib(kind)
     else:mesh.setAttrib(value)
   saved.clear()
  app.movie_restorers=getattr(app,'movie_restorers',[])+[restore]
  def fade(alpha,meshes):
   # Immediate sadness takes precedence over being temporarily erased.
   if not app.game.toons[target].alive:restore();return
   for mesh in meshes:
    if mesh.isEmpty():continue
    if mesh not in saved:saved[mesh]=[(k,mesh.getAttrib(k)) for k in (ColorScaleAttrib,TransparencyAttrib)]
    mesh.setTransparency(TransparencyAttrib.MAlpha)
    original=saved[mesh][0][1]
    color=Vec4(original.getScale()) if original else Vec4(1)
    color.w*=alpha;mesh.setColorScale(color)
  clips.append(Sequence(Wait(2.2),LerpFunc(fade,fromData=1,toData=0,duration=.2,extraArgs=[groups[0]]),Wait(.4),LerpFunc(fade,fromData=1,toData=0,duration=.2,extraArgs=[groups[1]]),Wait(.4),LerpFunc(fade,fromData=1,toData=0,duration=.2,extraArgs=[groups[2]]),Wait(1),Func(restore)))
  art=app.loader.loadModel(str(resource('phase_3.5/models/props/suit-particles.bam')));art.hide();app.movie_props.append((art,None));sprite=art.find('**/snow-particle')
  for n,meshes in enumerate(groups):
   effect=app.source_particle('demotionUnFreeze',index);effect.setName('rub-out-'+('head','torso','legs')[n]);effect.setScale(effect.getScale()*.62)
   for system in effect.getParticlesList():
    renderer=system.renderer;renderer.setFromNode(sprite);renderer.setInitialXScale(.03);renderer.setFinalXScale(0);renderer.setInitialYScale(.02);renderer.setFinalYScale(0);renderer.setColor(Vec4(*COLORS[target%len(COLORS)]))
   bounds=[m.getTightBounds(toon) for m in meshes if not m.isHidden()];bounds=[b for b in bounds if b and b[0] is not None]
   height=(min(b[0].z for b in bounds)+max(b[1].z for b in bounds))/2 if bounds else (2,1.2,.5)[n]
   effect.setPos(effect.getX()*.62,(effect.getY()-(1.5,1,.6)[n])*.62,height)
   clips.append(Sequence(Wait(2.5+n*1.1),Func(effect.start,toon),Wait(.5),Func(effect.softStop),Wait(1.5),Func(effect.disable)))
 duration=max(native,*[c.getDuration() for c in clips]);heading=Vec3(root.getHpr())
 def face():root.headsUp(toon);root.setH(root.getH()-actor.getH())
 e=dict(event,reaction='conked',dodge='jump',dodge_at=2)
 clips.extend([Sequence(Func(face),ActorInterval(actor,anim),Wait(duration-native),Func(root.setHpr,heading),Func(app.restore_cog_pose,index)),Sequence(Wait(1.7),app.sound_clip('SA_rubout.ogg')),app.attack_caption(index,'Rub Out',duration),app.health_movie(e,2.2)])
 return Parallel(*clips)
