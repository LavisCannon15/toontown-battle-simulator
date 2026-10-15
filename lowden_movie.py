"""Lowden: bundled dog head on a Cashbot disguise.

Appearance: TTR Silly Spotlight (2015-11-07). Head attachment follows
classic Toon.putOnSuit. Entrance/command timing is an adaptation: extracted
phase assets do not contain TTR's NPC battle sequencing code.
"""
from types import SimpleNamespace
from panda3d.core import Vec3,TextNode
from direct.actor.Actor import Actor
from direct.interval.IntervalGlobal import Sequence,Parallel,Func,Wait,ActorInterval,LerpPosInterval
from game_resources import SOURCE
from scene_art import expose_attachments,configure_head

def movie(app,action,event):
 root=app.characters.attachNewNode('sos-lord-lowden-clear')
 origin=app.toon_nodes[action.toon].getPos()+Vec3(0,2.5,0);root.setPos(origin);root.hide()
 suit=Actor(str(SOURCE/'ttr_r_ene_cga_suit.bam'),{name:str(SOURCE/f'ttr_a_ene_cga_{clip}.bam') for name,clip in [('idle','neutral'),('landing','landing'),('command','throw-object')]})
 expose_attachments(suit);suit.reparentTo(root);suit.setScale(.5);suit.setH(180)
 for part,suffix in [('torso','blazer'),('arms','sleeve'),('legs','leg')]:
  node=suit.find('**/'+part)
  if not node.isEmpty():node.setTexture(app.loader.loadTexture(str(SOURCE/f'phase_3.5/maps/m_{suffix}.jpg')),1)
 hands=suit.find('**/hands')
 if not hands.isEmpty():hands.setColor(1,1,1,1)
 head=app.loader.loadModel(str(SOURCE/'ttr_r_chr_avt_dog.bam'));configure_head(head,'short');head.reparentTo(suit.find('**/joint_head'));head.setScale(1.0);head.setZ(.2)
 for mesh in head.findAllMatches('**/+GeomNode'):
  # Only recolor the skin mesh; muzzle, black ears, nose and eyes retain
  # their original resource materials. A whole-head tint turns the muzzle red.
  if mesh.getName().lower().startswith('geo_m_head'):
   mesh.clearColorScale();mesh.setColor(.98,.1,.1,1)
 label=TextNode('lowden-name');label.setText('Lord Lowden Clear');label.setFont(app.font);label.setAlign(TextNode.ACenter);label.setTextColor(.1,.2,.8,1)
 suit.pose('idle',0);suit.update(force=True)
 speech_height=head.getTightBounds(root)[1].z+.31
 tag=root.attachNewNode(label);tag.setZ(speech_height);tag.setScale(.35);tag.setBillboardPointEye();tag.setLightOff()
 from sos_movies import remove,speech
 if not hasattr(app,'sos_guests'):app.sos_guests={}
 remove(app,action.toon)
 guest={'root':root,'actors':{'suit':suit},'head':head,'track':'Fire','action':action,'name_tag':tag,'speech_height':speech_height}
 app.sos_guests[action.toon]=guest
 targets=sorted({i for k,i,n in event['health'] if k=='cog' and n<0})
 cannons=[]
 for i in targets:
  single=dict(event,health=[h for h in event['health'] if h[0]=='cog' and h[1]==i])
  cannons.append(app.fire_movie(SimpleNamespace(toon=action.toon,target=i,cannon_heading=0,preserve_cog_facing=True),single,caller_clip=Wait(0)))
 # Red Tape uses throw-object; Lowden substitutes the bundled pink-slip card.
 # Its appearance/release offsets follow doRedTape; no tape tubes or binding effect.
 slip,_=app.movie_prop('pink-slip',None)
 hand=suit.find('**/joint_Rhold')
 def hold_slip():
  slip.reparentTo(hand);slip.setPos(.24,.09,-.38)
  slip.setHpr(-1.152,86.581,-76.784);slip.setScale(.9);slip.show()
 destination=sum((app.cog_nodes[i].getPos() for i in targets),Vec3(0))/max(1,len(targets))+Vec3(0,0,2.4)
 card=Sequence(Wait(.8),Func(hold_slip),Wait(2.23),Func(slip.wrtReparentTo,app.characters),LerpPosInterval(slip,.37,destination),Func(slip.hide))
 attack=Parallel(ActorInterval(suit,'command'),card,Sequence(Wait(3.4),Parallel(*cannons)))
 entrance=flight(app,root,suit,origin,True)
 departure=flight(app,root,suit,origin,False)
 # Arrival speech is visible in the user-supplied oQSXv7RyrH8 video (~10s).
 # Substitute the caller's name; exact modern TTR chat duration is unpublished.
 greeting="Thanks for the call-in, "+app.game.toons[action.toon].name+"! I'll take it from here..."
 return Sequence(entrance,Func(root.setH,180),Parallel(attack,speech(app,guest,greeting,3.4)),Func(suit.loop,'idle'),Wait(.5),Func(root.setH,0),Parallel(departure,speech(app,guest,'Happy to be of assistance, as always.',4.0)),Func(remove,app,action.toon))


def flight(app,root,suit,origin,incoming):
 # DistributedSuitBase.beginSupaFlyMove: contact at landing frame 28;
 # propeller frames 0..8 spin, the remainder folds into the head.
 prop=Actor(str(SOURCE/'propeller-mod.bam'),{'propeller':str(SOURCE/'propeller-chan.bam')})
 holder=suit.find('**/joint_head').attachNewNode('lowden-flight-propeller')
 prop.reparentTo(holder);holder.hide();app.movie_props.append((holder,prop))
 speed=6.5/4.0  # Complete each arrival/departure in 4 seconds.
 duration=suit.getDuration('landing');air=28/suit.getFrameRate('landing')
 settle=duration-air;travel=6.5-settle;wait=max(0,travel-air)
 pd=prop.getDuration('propeller');rate=prop.getFrameRate('propeller')
 spin=8/rate;opened=9/rate
 # Keep the classic timing; adapt altitude to this compact battle stage.
 sky=origin+Vec3(0,0,18)
 if incoming:
  movement=Sequence(Func(root.setPos,sky),Func(root.show),LerpPosInterval(root,travel/speed,origin),Wait(settle/speed))
  body=Sequence(Func(suit.pose,'landing',0),Wait(wait/speed),ActorInterval(suit,'landing',playRate=speed),Func(suit.loop,'idle'))
  blades=Sequence(Func(holder.show),ActorInterval(prop,'propeller',constrainedLoop=1,duration=(wait+spin)/speed,playRate=speed,startFrame=0,endFrame=8),ActorInterval(prop,'propeller',startFrame=9,playRate=speed),Func(holder.hide))
 else:
  movement=Sequence(Wait(settle/speed),LerpPosInterval(root,travel/speed,sky),Func(root.hide))
  body=ActorInterval(suit,'landing',startFrame=suit.getNumFrames('landing')-1,endFrame=0,playRate=speed)
  blades=Sequence(Func(holder.show),ActorInterval(prop,'propeller',startFrame=prop.getNumFrames('propeller')-1,endFrame=9,playRate=speed),ActorInterval(prop,'propeller',constrainedLoop=1,duration=max(0,6.5-(pd-opened))/speed,playRate=speed,startFrame=8,endFrame=0),Func(holder.hide))
 return Parallel(movement,body,blades,app.sound_clip('ENC_propeller_in.ogg' if incoming else 'ENC_propeller_out.ogg'))
