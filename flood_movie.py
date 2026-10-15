"""TTR Flood presentation reconstruction; modern sequencing is not in phase files.
Blue pool and jump dodge follow the TTR wiki animation description. Timing and
particle parameters are simulator adaptations, not verified TTR source values.
"""
from panda3d.core import Vec3,Vec4
from direct.interval.IntervalGlobal import Sequence,Parallel,Func,Wait,ActorInterval,LerpScaleInterval

def movie(app,event):
 index=event['cog'];actor=app.cog_actors[index];impact=1.8
 event=dict(event,reaction='slip-backward',dodge='jump',dodge_at=1.25)
 effect=app.source_particle('waterfall',index)
 effect.setPos(0,-1,.12);effect.setHpr(0,0,0);effect.setScale(.01)
 system=effect.getParticlesNamed('particles-1');system.setPoolSize(800);system.setBirthRate(.015);system.setLitterSize(16)
 system.factory.setLifespanBase(.7);system.factory.setLifespanSpread(.2)
 system.emitter.setRadius(1);system.emitter.setAmplitude(.1)
 system.renderer.setCenterColor(Vec4(.15,.6,1,.8));system.renderer.setEdgeColor(Vec4(.05,.3,.9,.3));system.renderer.setBirthRadius(.06);system.renderer.setDeathRadius(.1)
 miss=bool(event['targets']) and all(i in event['misses'] for i in event['targets'])
 sound='ttr_s_ene_bat_floodTheMarketMiss.ogg' if miss else 'ttr_s_ene_bat_floodTheMarket.ogg'
 duration=max(actor.getDuration('magic1'),3.5)
 return Parallel(Sequence(ActorInterval(actor,'magic1'),Func(app.restore_cog_pose,index)),app.attack_caption(index,event['name'],duration),app.health_movie(event,impact),Sequence(Wait(.6),app.sound_clip(sound)),Sequence(Wait(.7),Func(effect.start,app.render),LerpScaleInterval(effect,1,Vec3(8,5,.3)),Wait(1.2),Func(effect.softStop),Wait(1),Func(effect.disable)))
