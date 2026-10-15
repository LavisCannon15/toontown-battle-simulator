"""Classic doSchmooze: alternating compliment sprites and spliced reactions."""
from panda3d.core import Vec3,Vec4
from direct.interval.IntervalGlobal import Sequence,Parallel,Func,Wait,ActorInterval
from battle_movies import MOVIES
from game_resources import resource


def reaction(app,target,hit):
 parts=list(app.toon_actors[target].values());anim='conked' if hit else 'duck'
 ranges=[(.3,.71)]*3+[(.3,None)] if hit else [(.2,2.7),(1.22,1.28),(3.16,None)]
 sequence=Sequence()
 for start,duration in ranges:
  sequence.append(Wait(.01));sequence.append(Parallel(*(ActorInterval(a,anim,startTime=start,**({'duration':duration} if duration is not None else {})) for a in parts if anim in a.getAnimNames())))
 def idle():
  if app.game.toons[target].alive:app.play_toon_animation(target,'idle',True)
 sequence.append(Func(idle));return sequence


def movie(app,event):
 index=event['cog'];target=event['targets'][0];actor=app.cog_actors[index];root=app.cog_nodes[index];toon=app.toon_nodes[target];hit=target not in event['misses']
 spec=MOVIES['suits'][app.game.cogs[index].name];anim=spec['attacks']['Schmooze'];native=actor.getDuration(anim)
 body='A' if 'suitA' in spec['anims'][anim] else 'B' if 'suitB' in spec['anims'][anim] else 'C'
 onset={'A':1.8,'B':2.5,'C':2.7}[body] if hit else {'A':1.1,'B':1.8,'C':.9}[body]
 clips=[];tracks=[];art=app.loader.loadModel(str(resource('phase_3.5/models/props/suit-particles.bam')));art.hide();app.movie_props.append((art,None))
 for n,name in enumerate(['schmooze-genius','schmooze-instant','schmooze-master','schmooze-viz']):
  sprite=art.find('**/'+name)
  for lower in (False,True):
   effect=app.source_particle('schmoozeLowerSpray' if lower else 'schmoozeUpperSpray',index);effect.setName(name+('-lower' if lower else '-upper'))
   for system in effect.getParticlesList():system.renderer.setFromNode(sprite);system.renderer.setColor(Vec4(0,0,1,1))
   clips.append(Sequence(Wait(1.3+n*.65+(.7 if lower else 0)),Func(effect.start,actor),Wait(1 if lower else .8),Func(effect.softStop),Wait(1.9),Func(effect.disable)))
 r=reaction(app,target,hit)
 def start():
  if not app.game.toons[target].alive:return
  tracks.append(r);app.live_departures=getattr(app,'live_departures',[])+[r];r.start()
 clips.append(Sequence(Wait(onset),Func(start),Wait(r.getDuration())))
 e=dict(event,misses=[],custom_toon_reaction=True,custom_toon_tracks=tracks,reaction='conked')
 clips.append(app.health_movie(e,onset+1.1))
 if not hit:clips.append(Sequence(Wait(onset+1.9),app.float_text(toon,0,3,start=False,text='MISSED')))
 duration=max(native,*[c.getDuration() for c in clips]);heading=Vec3(root.getHpr())
 def face():root.headsUp(toon);root.setH(root.getH()-actor.getH())
 clips.extend([Sequence(Func(face),ActorInterval(actor,anim),Wait(duration-native),Func(root.setHpr,heading),Func(app.restore_cog_pose,index)),app.attack_caption(index,'Schmooze',duration)])
 return Parallel(*clips)
