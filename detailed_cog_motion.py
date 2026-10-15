"""Source-derived Spin, Paradigm Shift, Quake and Head Shrink motion."""
import random
from panda3d.core import Vec3,Vec4
from direct.interval.IntervalGlobal import Sequence,Parallel,Func,Wait,ActorInterval,LerpPosInterval,LerpHprInterval,LerpScaleInterval,LerpFunc
from battle_movies import MOVIES
S=.62
ATTACKS={'Spin','Paradigm Shift','Quake','Head Shrink'}

def movie(app,event):
 i=event['cog'];name=event['name'];actor=app.cog_actors[i];root=app.cog_nodes[i];clips=[];restorers={};tracks=[]
 by_toon={}
 event=dict(event,custom_toon_reaction=True,custom_toon_dodge=True,custom_toon_tracks=tracks,custom_toon_tracks_by_index=by_toon,toon_movie_restore=restorers)
 anim=MOVIES['suits'][app.game.cogs[i].name]['attacks'][name]
 impact,onset,dodge={'Spin':(3.8,1.7,.91),'Paradigm Shift':(4.65,1.95,.95),'Quake':(2.9,1.8,1.1),'Head Shrink':(2.1,2.1,1.4)}[name]
 def particle(stem,parent,start,length):
  p=app.source_particle(stem,i);clips.append(Sequence(Wait(start),Func(p.start,parent),Wait(length),Func(p.softStop),Wait(1),Func(p.disable)));return p
 if name=='Spin':particle('spinSpray',actor,1,1.9)
 elif name=='Paradigm Shift':particle('shiftSpray',actor,1,1.9).setPos(-5.2,4.6,2.7)
 elif name=='Head Shrink':particle('headShrinkSpray',actor,.3,1.4)
 def segment(t,anim,start=0,end=None,rate=1):
  return Parallel(*(ActorInterval(a,anim,startTime=start,**({'endTime':end} if end is not None else {}),playRate=rate) for a in app.toon_actors[t].values() if anim in a.getAnimNames()))
 def schedule(t,at,seq):
  r=Sequence(seq,Func(lambda:app.play_toon_animation(t,'idle',True) if app.game.toons[t].alive else None));tracks.append(r)
  by_toon.setdefault(t,[]).append(r)
  def start():
   if app.game.toons[t].alive:
    app.live_departures=getattr(app,'live_departures',[])+[r];r.start()
  clips.append(Sequence(Wait(at),Func(start),Wait(r.getDuration())))
 for t in event['targets']:
  toon=app.toon_nodes[t];hit=t not in event['misses'];motion=Wait(0)
  if name=='Spin' and hit:
   if not hasattr(app,'presentation_rng'):app.presentation_rng=random.Random()
   rng=app.presentation_rng
   for low in (.7,.4,.1):
    p=particle('spinEffect',app.render,2.1,3.9);p.setScale(p.getScale()*S)
    p.setPos(app.render.getRelativePoint(toon,Vec3(.8*S,-.7*S,2.8*(rng.random()*.2+low))));p.setHpr(toon,0,50,-rng.random()*10-85)
   initial=Vec3(toon.getHpr())
   def restore(n=toon,h=initial):
    if not n.isEmpty():n.setHpr(h)
   restorers[t]=restore;app.movie_restorers=getattr(app,'movie_restorers',[])+[restore]
   motion=Sequence(Wait(.9),*[LerpHprInterval(toon,d,initial+Vec3(h,0,0)) for h,d in [(-10,.7),(-30,.5),(-60,.2),(-700,.7),(-1310,1),(0,.4)]],Func(restore))
  elif name=='Paradigm Shift' and hit:
   lift=particle('pixieDrop',app.render,1.1,4.1);lift.setHpr(0,180,0);lift.setPos(toon.getPos()+Vec3(0,0,-1.3*S));lift.setScale(lift.getScale()*S)
   system=lift.getParticlesNamed('particles-1');system.renderer.setCenterColor(Vec4(1,1,0,.9));system.renderer.setEdgeColor(Vec4(1,1,0,.6));system.emitter.setRadius(.01)
   initial=Vec3(toon.getPos());rise=initial+Vec3(0,0,3*S)
   def restore(n=toon,p=initial):
    if not n.isEmpty():n.setPos(p)
   restorers[t]=restore;app.movie_restorers=getattr(app,'movie_restorers',[])+[restore]
   motion=Sequence(Wait(.25),LerpPosInterval(toon,1.1,rise))
   for _ in range(17):motion.append(LerpPosInterval(toon,.03,rise+Vec3(0,-.7*S,0)));motion.append(LerpPosInterval(toon,.03,rise+Vec3(0,.7*S,0)))
   motion.append(LerpPosInterval(toon,.1,rise));motion.append(LerpPosInterval(toon,.1,initial));motion.append(Func(restore))
  elif name=='Head Shrink':
   cloud=app.source_particle('headShrinkCloud',i);cloud.setScale(S);center=toon.getPos()+Vec3(0,-.4*S,8*S);cloud.setPos(center)
   circle=Sequence()
   for x,y in [(1,0),(.5,.5),(0,1),(-.5,.5),(-1,0),(-.5,-.5),(0,-1),(.5,-.5),(1,0),(0,0)]:circle.append(LerpPosInterval(cloud,.14,center+Vec3(x*.7*S,y*.7*S,0)))
   clips.append(Sequence(Wait(1.42),Func(cloud.start,app.render),circle,Sequence(*[LerpPosInterval(cloud,.14,center+Vec3(x*.7*S,y*.7*S,0)) for x,y in [(1,0),(.5,.5),(0,1),(-.5,.5),(-1,0),(-.5,-.5),(0,-1),(.5,-.5),(1,0),(0,0)]]),LerpFunc(cloud.setAlphaScale,fromData=1,toData=0,duration=.7),Func(cloud.disable)))
   drop=particle('headShrinkDrop',toon,1.5,2.5);drop.setScale(drop.getScale()*S);drop.setPos(0,-.4*S,7.5*S)
   if hit:
    head=app.toon_actors[t]['torso'].find('**/def_head').getChild(0);initial=Vec3(head.getScale())
    def restore(n=head,s=initial):
     if not n.isEmpty():n.setScale(s)
    restorers[t]=restore;app.movie_restorers=getattr(app,'movie_restorers',[])+[restore]
    motion=Sequence(Wait(.8),LerpScaleInterval(head,1.1,initial*.6),Wait(1.6))
    for f,d in [(3.2,.4),(.7,.4),(2.5,.3),(.8,.3),(1.9,.2),(.85,.2),(1.7,.15),(.9,.15),(1.3,.1),(1,.1)]:motion.append(LerpScaleInterval(head,d,initial*f))
    motion.append(Func(restore));clips.append(Sequence(Wait(2.1),app.sound_clip('SA_head_shrink_only.ogg',2.1),Wait(1.6),app.sound_clip('SA_head_grow_back_only.ogg')))
  if not hit:
   if name=='Quake':r=Sequence(segment(t,'jump'),Wait(.01),segment(t,'jump'),Wait(.01),segment(t,'jump'))
   elif name=='Paradigm Shift':r=Sequence(segment(t,'jump',0,.6),segment(t,'jump',.6,.91,.31),segment(t,'jump',.91))
   else:r=segment(t,'sidestep-left')
   schedule(t,dodge,r);continue
  if name=='Spin':r=Sequence(segment(t,'duck',0,1.1),segment(t,'think',2.26,2.92,.6),segment(t,'think',2.26,2.92,.6))
  elif name=='Paradigm Shift':r=Sequence(segment(t,'think',2.06,2.72,.66/1.9),segment(t,'slip-backward',.5))
  elif name=='Quake':r=Sequence(segment(t,'slip-forward'),Wait(.01),segment(t,'slip-forward'))
  else:r=Sequence(segment(t,'cringe',.65,.85),segment(t,'cringe',.85,1.49,.64),segment(t,'cringe',1.49),segment(t,'conked',3.6,2,1),segment(t,'conked',3.1,3.5))
  schedule(t,onset,Parallel(r,motion))
 if name=='Paradigm Shift' and any(t not in event['misses'] for t in event['targets']):clips.append(Sequence(Wait(2.1),app.sound_clip('SA_paradigm_shift.ogg')))
 # These dedicated hit/miss sounds are present in the extracted TTR phase files.
 if name=='Spin':clips.append(Sequence(Wait(1),app.sound_clip('SA_spin.ogg' if any(t not in event['misses'] for t in event['targets']) else 'SA_spin_miss.ogg')))
 clips.append(app.health_movie(event,impact));native=actor.getDuration(anim);duration=max(native,*[c.getDuration() for c in clips]);heading=Vec3(root.getHpr())
 def face():
  if len(event['targets'])==1:root.headsUp(app.toon_nodes[event['targets'][0]]);root.setH(root.getH()-actor.getH())
 clips.extend([Sequence(Func(face),ActorInterval(actor,anim),Wait(duration-native),Func(root.setHpr,heading),Func(app.restore_cog_pose,i)),app.attack_caption(i,name,duration)])
 return Parallel(*clips)
