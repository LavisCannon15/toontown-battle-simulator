"""MovieSuitAttacks.doRubberStamp / __makeCancelledNodePath, adapted scene scale."""
from panda3d.core import Vec3,TextNode
from direct.interval.IntervalGlobal import Sequence,Parallel,Func,Wait,ActorInterval,LerpPosInterval
from battle_movies import MOVIES
from classic_cog_movies import appear,vanish,TOON_SCALE


def movie(app,event):
 index=event['cog'];target=event['targets'][0];actor=app.cog_actors[index];root=app.cog_nodes[index];toon=app.toon_nodes[target]
 anim=MOVIES['suits'][app.game.cogs[index].name]['attacks']['Rubber Stamp'];native=actor.getDuration(anim)
 body_c='suitC' in MOVIES['suits'][app.game.cogs[index].name]['anims'][anim]
 pad_pos,pad_hpr=((.19,-.55,-.21),(-166.76,-4.001,-1.658)) if body_c else ((-.65,.83,-.04),(5.625,4.456,-165.125))
 stamp_pos=(-.64,-.08,.11) if body_c else (-.64,-.17,-.03)
 pad,_=app.movie_prop('pad',None);stamp,_=app.movie_prop('rubber-stamp',None)
 text=TextNode('CANCELLED');text.setFont(app.suit_font);text.setText('CANCELLED\nCANCELLED\nCANCELLED');text.setAlign(TextNode.ACenter)
 mark=app.render.attachNewNode('rubber-stamp-cancelled');front=mark.attachNewNode(text);front.setColor(.7,0,0,1)
 back=front.instanceUnderNode(mark,'backside');back.setH(180)
 mark.setLightOff();mark.hide();app.movie_props.append((mark,None))
 def launch():
  mark.setPos(app.render.getRelativePoint(stamp,Vec3(.81,-1.11,-.16)))
  mark.setHpr(stamp.getH(app.render),0,0);mark.setScale(.6*TOON_SCALE);mark.show()
 def destination():
  point=app.render.getRelativePoint(toon,Vec3(0,0,2))
  if target in event['misses']:
   direction=point-mark.getPos(app.render)
   if direction.lengthSquared():direction.normalize()
   point+=direction*(5*TOON_SCALE)
  return point
 clips=[Sequence(appear(pad,actor.find('**/joint_Lhold'),pad_pos,pad_hpr,(1,)*3,.000001),vanish(pad,3.2)),
  Sequence(appear(stamp,actor.find('**/joint_Rhold'),stamp_pos,(0,0,0),(1,)*3,0),Wait(2.6),Func(launch),LerpPosInterval(mark,.5,destination),Func(mark.hide),vanish(stamp,.3)),
  Sequence(Wait(1.3),app.sound_clip('SA_rubber_stamp.ogg',1.1)),
  app.health_movie(dict(event,reaction='conked',dodge='sidestep-left',dodge_at=1.9),3.4)]
 duration=max(native,*[c.getDuration() for c in clips]);heading=Vec3(root.getHpr())
 def face():root.headsUp(toon);root.setH(root.getH()-actor.getH())
 clips.extend([Sequence(Func(face),ActorInterval(actor,anim),Wait(duration-native),Func(root.setHpr,heading),Func(app.restore_cog_pose,index)),app.attack_caption(index,'Rubber Stamp',duration)])
 return Parallel(*clips)
