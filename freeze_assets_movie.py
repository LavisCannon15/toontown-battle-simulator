"""Classic doFreezeAssets: a posed cloud travels, then sheds snow."""
from panda3d.core import Vec3
from direct.interval.IntervalGlobal import Sequence,Parallel,Func,Wait,ActorInterval,LerpPosInterval,LerpScaleInterval
from classic_cog_movies import appear,TOON_SCALE
from battle_movies import MOVIES


def movie(app,event):
 index=event['cog'];target=event['targets'][0];actor=app.cog_actors[index];root=app.cog_nodes[index];toon=app.toon_nodes[target]
 anim=MOVIES['suits'][app.game.cogs[index].name]['attacks']['Freeze Assets'];native=actor.getDuration(anim)
 cloud,channel=app.movie_prop('stormcloud',None);snow=app.source_particle('freezeAssets',index)
 # Measure in Suit-local space; the parent's scale converts to scene units.
 lo,hi=actor.getTightBounds(actor);height=hi.z-lo.z
 def detach():cloud.wrtReparentTo(app.render)
 def destination():return app.render.getRelativePoint(toon,Vec3(0,0,2+3*TOON_SCALE))
 snowfall=Sequence(Func(snow.start,cloud),Wait(2.1),Func(snow.softStop),Wait(.7),Func(snow.disable))
 cloud_end=Sequence(Wait(2.1),Wait(.4),LerpScaleInterval(cloud,.5,.001),Func(cloud.hide))
 cloud_track=Sequence(Func(channel.pose,'prop',0),appear(cloud,actor,(0,3,height+3),(0,0,0),(3,)*3,.000001,grow=.7),Func(detach),Wait(1.1),LerpPosInterval(cloud,1,destination),Wait(.2),Parallel(snowfall,cloud_end))
 duration=max(cloud_track.getDuration(),native+.9);heading=Vec3(root.getHpr())
 def face():root.headsUp(toon);root.setH(root.getH()-actor.getH())
 return Parallel(cloud_track,Sequence(Func(face),Wait(.9),ActorInterval(actor,anim),Wait(duration-native-.9),Func(root.setHpr,heading),Func(app.restore_cog_pose,index)),app.attack_caption(index,'Freeze Assets',duration),app.health_movie(dict(event,reaction='cringe',dodge='sidestep-left',dodge_at=2.3),3.5))
