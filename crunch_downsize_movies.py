"""Classic doCrunch and doDownsize, using bundled TTR art and source particles."""
import random
from panda3d.core import Vec3
from direct.interval.IntervalGlobal import Sequence,Parallel,Func,Wait,ActorInterval,LerpScaleInterval,LerpFunc
from battle_movies import MOVIES
from game_resources import resource


def reaction(app,index,name):
 parts=list(app.toon_actors[index].values());r=Sequence()
 stages=[('cringe',.14,.28),('cringe',.16,.3),('cringe',.13,.22),('slip-forward',.6,None)] if name=='Crunch' else [('juggle',.87,.5),('lose',2.17,.93),('lose',3.1,-.93),('struggle',.8,1.8),('sidestep-right',2.97,1.49)]
 for anim,start,length in stages:
  args={} if length is None else {'endTime':start+length} if length<0 else {'duration':length}
  r.append(Wait(.01));r.append(Parallel(*(ActorInterval(a,anim,startTime=start,**args) for a in parts if anim in a.getAnimNames())))
 def idle():
  if app.game.toons[index].alive:app.play_toon_animation(index,'idle',True)
 r.append(Func(idle));return r


def movie(app,event):
 i=event['cog'];target=event['targets'][0];name=event['name'];actor=app.cog_actors[i];root=app.cog_nodes[i];toon=app.toon_nodes[target];hit=target not in event['misses']
 anim=MOVIES['suits'][app.game.cogs[i].name]['attacks'][name];native=actor.getDuration(anim);clips=[]
 def particle(stem,parent,start,length,sprite=None):
  effect=app.source_particle(stem,i)
  if sprite is not None:
   for system in effect.getParticlesList():system.renderer.setFromNode(sprite)
  clips.append(Sequence(Wait(start),Func(effect.start,parent),Wait(length),Func(effect.softStop),Wait(2.1 if stem=='numberSpray' else 1),Func(effect.disable)))
  return effect
 if name=='Crunch':
  if not hasattr(app,'presentation_rng'):app.presentation_rng=random.Random()
  rng=app.presentation_rng
  art=app.loader.loadModel(str(resource('phase_3.5/models/props/suit-particles.bam')));art.hide();app.movie_props.append((art,None))
  numbers=[art.find('**/audit-'+n) for n in ['one','two','three','four','five','six']]
  particle('numberSpill',actor,1.1,2.2,rng.choice(numbers));particle('numberSpill',actor,1.5,1,rng.choice(numbers))
  count=rng.randint(5,9)
  for n in range(count-1):
   sprite=rng.choice(numbers);start=3.03+rng.random()*.6;length=1.4+rng.random()*.4
   particle('numberSpray',actor,start,length,sprite)
  for n in range(count):
   number=rng.choice(numbers).copyTo(actor.find('**/joint_Rhold'));number.setName('crunch-held-number');number.setColor(0,0,0,1);number.setScale(.01);number.setPos(*(rng.random()*.6-.3 for _ in range(3)));number.setHpr(-1.15,86.58,-76.78);number.hide();app.movie_props.append((number,None))
   clips.append(Sequence(Wait(.9),Func(number.show),LerpScaleInterval(number,.6,1),Wait(1.7),Func(number.hide)))
 else:
  particle('downsizeSpray',actor,1,1.28)
  if hit:
   cloud=particle('downsizeCloud',toon,2.1,1.9);cloud.setScale(cloud.getScale()*.62)
   lo,hi=app.toon_actors[target]['legs'].getTightBounds(toon);cloud.setPos(0,0,(hi.z-lo.z)*.55)
   initial=Vec3(toon.getScale());state={'previous':1.0,'from':1.0,'active':False}
   def restore():
    if state['active'] and not toon.isEmpty() and app.game.toons[target].alive:toon.setScale(initial)
    state['active']=False
   app.movie_restorers=getattr(app,'movie_restorers',[])+[restore]
   def segment(value,duration):
    def begin():state['from']=state['previous']
    def apply(t):
     if not app.game.toons[target].alive:return
     factor=state['from']*(1-t)+value*t;toon.setScale(initial*factor);state['active']=True;state['previous']=factor
    return Sequence(Func(begin),LerpFunc(apply,fromData=0,toData=1,duration=duration))
   shrink=Sequence(Wait(2.8))
   for factor,time in [(.44,1),(.36,.1),(.42,.1),(.38,.1),(.4,.1)]:shrink.append(segment(factor,time))
   shrink.append(Wait(2.1))
   for factor,time in [(1.5,.5),(.5,.15),(1.2,.15),(.8,.15),(1,.15)]:shrink.append(segment(factor,time))
   shrink.append(Func(restore));clips.append(shrink)
 impact=4.7 if name=='Crunch' else 2.3
 clips.append(app.health_movie(dict(event,reaction='cringe',dodge='sidestep-left',dodge_at=3.6 if name=='Crunch' else .6),impact))
 duration=max(native,*[c.getDuration() for c in clips]);heading=Vec3(root.getHpr())
 def face():root.headsUp(toon);root.setH(root.getH()-actor.getH())
 clips.extend([Sequence(Func(face),ActorInterval(actor,anim),Wait(duration-native),Func(root.setHpr,heading),Func(app.restore_cog_pose,i)),app.attack_caption(i,name,duration)])
 return Parallel(*clips)
