"""Beguile presentation reconstruction from TTR's documented attack description.
Modern movie source is unavailable: gesture selection and timestamps are adapted.
"""
from panda3d.core import Vec3
from direct.interval.IntervalGlobal import Sequence,Parallel,Func,Wait,ActorInterval

def movie(app,event):
 index=event['cog'];actor=app.cog_actors[index]
 # Use the leaning glower channel, not the unrelated finger-wag/handheld sign.
 head=actor.find('**/joint_head')
 effect=app.source_particle('smile',index);effect.setPos(0,.55,.15);effect.setHpr(0,0,0);effect.setScale(.18)
 native=actor.getDuration('glower');impact=1.8;duration=max(native,3.2)
 miss=bool(event['targets']) and all(i in event['misses'] for i in event['targets'])
 sound='ttr_s_ene_bat_beguileMiss.ogg' if miss else 'ttr_s_ene_bat_beguile.ogg'
 event=dict(event,reaction='slip-backward',dodge='duck',dodge_at=1.2)
 return Parallel(Sequence(ActorInterval(actor,'glower'),Func(app.restore_cog_pose,index)),app.attack_caption(index,event['name'],duration),app.health_movie(event,impact),Sequence(Wait(1),Func(effect.start,head),Wait(1.4),Func(effect.softStop),Wait(1),Func(effect.disable)),Sequence(Wait(1),app.sound_clip(sound)))
