"""Classic doPinkSlip; separate from Toon fires and Lord Lowden Clear."""
from panda3d.core import Vec3
from direct.interval.IntervalGlobal import Sequence,Parallel,Func,Wait,ActorInterval,LerpPosInterval,LerpHprInterval,LerpScaleInterval
from classic_cog_movies import appear,TOON_SCALE
from battle_movies import MOVIES


def movie(app,event):
 i=event['cog'];target=event['targets'][0];actor=app.cog_actors[i];root=app.cog_nodes[i];toon=app.toon_nodes[target];hit=target not in event['misses']
 anim=MOVIES['suits'][app.game.cogs[i].name]['attacks']['Pink Slip'];native=actor.getDuration(anim)
 paper,_=app.movie_prop('pink-slip',None);points={}
 def detach():
  paper.wrtReparentTo(app.render)
  ground=toon.getPos(app.render)+Vec3(0,0,.2*TOON_SCALE)
  points['ground']=ground;points['slide']=ground+Vec3(0,-5*TOON_SCALE,4*TOON_SCALE);points['land']=ground+Vec3(0,-5*TOON_SCALE,0)
 path=Sequence(appear(paper,actor.find('**/joint_Rhold'),(.07,-.06,-.18),(-172.075,-26.715,-89.131),(8,)*3,.8),Wait(1.73),Func(detach),Parallel(LerpPosInterval(paper,.5,lambda:points['ground']),LerpHprInterval(paper,.5,Vec3(300,0,0))))
 if hit:
  path.append(Wait(.01));path.append(Parallel(Sequence(LerpPosInterval(paper,.2,lambda:points['slide']),LerpPosInterval(paper,1.1,lambda:points['land'])),LerpHprInterval(paper,1.3,Vec3(-200,100,100))))
 else:path.append(Parallel(LerpPosInterval(paper,.5,lambda:points['land']),LerpHprInterval(paper,.5,Vec3(10,0,0))))
 path.append(LerpScaleInterval(paper,.4,.001));path.append(Func(paper.hide));tracks=[];clips=[path]
 if hit:
  parts=list(app.toon_actors[target].values())
  r=Sequence(Wait(.01),Parallel(*(ActorInterval(a,'jump',startTime=.3,duration=.7) for a in parts if 'jump' in a.getAnimNames())),Wait(.01),Parallel(*(ActorInterval(a,'slip-forward') for a in parts if 'slip-forward' in a.getAnimNames())))
  def idle():
   if app.game.toons[target].alive:app.play_toon_animation(target,'idle',True)
  r.append(Func(idle))
  def start():
   if not app.game.toons[target].alive:return
   tracks.append(r);app.live_departures=getattr(app,'live_departures',[])+[r];r.start()
  clips.append(Sequence(Wait(2.81),Func(start),Wait(r.getDuration())))
 clips.extend([app.health_movie(dict(event,custom_toon_reaction=True,custom_toon_tracks=tracks,reaction='slip-forward',dodge='jump',dodge_at=2.8),3.71 if hit else 3.3),Sequence(Wait(2.9),app.sound_clip('SA_pink_slip.ogg',1.1))])
 duration=max(native,*[c.getDuration() for c in clips]);heading=Vec3(root.getHpr())
 def face():root.headsUp(toon);root.setH(root.getH()-actor.getH())
 clips.extend([Sequence(Func(face),ActorInterval(actor,anim),Wait(duration-native),Func(root.setHpr,heading),Func(app.restore_cog_pose,i)),app.attack_caption(i,'Pink Slip',duration)])
 return Parallel(*clips)
