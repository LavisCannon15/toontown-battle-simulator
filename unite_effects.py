"""ResistanceChat.doEffect choreography using bundled art and classic particle configs.
Unites have a separate lifetime: ordinary movie cleanup must not interrupt them.
"""
import random
from pathlib import Path
from panda3d.core import Filename,Vec4,TextNode
from direct.particles.ParticleEffect import ParticleEffect
from direct.interval.IntervalGlobal import Sequence,Parallel,Func,Wait,LerpColorScaleInterval
from game_resources import resource
from battle_engine import GAGS,TRACKS
ROOT=Path(__file__).resolve().parent

def play(app,index,name,recipients):
 app.enableParticles()
 healing=name.startswith('Unite: Toon-Up ')
 config='resistanceEffectSparkle' if healing else 'resistanceEffectSprite'
 particle=ParticleEffect();particle.loadConfig(Filename.fromOsSpecific(str(ROOT/'assets/particle_effects'/f'{config}.ptf')))
 root=app.toon_nodes[index].attachNewNode('unite-effect');root.setScale(.62)
 # Keep cosmetic selection independent of the battle's seeded random generator.
 inventory=None;chosen=[]
 if not healing:
  from panda_battle import ICON_STEMS
  inventory=app.loader.loadModel(str(resource('phase_3.5/models/gui/inventory_icons.bam')))
  inventory.setScale(4);inventory.flattenLight()
  track=name.removeprefix('Unite: Gag-Up ')
  if track=='All':
   tracks=random.sample(list(TRACKS),6)
   chosen=[random.choice([g for g in GAGS.values() if g.track==t and g.level<=6]) for t in tracks]
  else:chosen=[g for g in GAGS.values() if g.track==track and g.level<=6]
  for j,g in enumerate(chosen):
   stem=ICON_STEMS[g.track][g.level-1];icon=inventory.find('**/inventory_'+stem)
   if icon.isEmpty():raise ValueError('Missing Unite inventory icon '+stem)
   particle.getParticlesNamed('particles-'+str(j+1)).renderer.setFromNode(icon)
 root.setPythonTag('unite-particle',particle);root.setPythonTag('unite-icons',[(g.track,g.level) for g in chosen])
 text=TextNode('unite-phrase');text.setFont(app.font);text.setAlign(TextNode.ACenter)
 text.setText('Toons of the World, '+('Toon-Up!' if healing else 'Gag-Up!'))
 text.setWordwrap(18);text.setTextColor(.05,.1,.08,1);text.setCardColor(1,1,.96,1);text.setCardAsMargin(.3,.3,.2,.2)
 phrase=root.attachNewNode(text);phrase.setScale(.75);phrase.setZ(7.5);phrase.setBillboardPointEye();phrase.setLightOff();phrase.setTwoSided(True);phrase.setDepthTest(False);phrase.setDepthWrite(False);phrase.setBin('fixed',30)
 pulses=[];tints=getattr(app,'unite_tints',{});app.unite_tints=tints
 for i in recipients:
  # Tint only the character branch, not its floating labels or selection ring.
  node=app.toon_actors[i]['legs']
  old=tints.get(i)
  if old:old.finish()
  original=Vec4(node.getColorScale());color=Vec4(1,.5,1,1) if healing else Vec4(0,0,1,1)
  pulse=Sequence(Wait(.2),LerpColorScaleInterval(node,.3,color),LerpColorScaleInterval(node,.3,original))
  tints[i]=pulse;pulses.append(pulse);pulse.start()
 def cleanup():
  particle.cleanup()
  if inventory is not None:inventory.removeNode()
  root.removeNode()
  for i,pulse in zip(recipients,pulses):
   if tints.get(i) is pulse:
    pulse.finish();tints.pop(i,None)
 effect=Sequence(Func(particle.start,root),Wait(3),Func(cleanup))
 app.unite_intervals=[e for e in getattr(app,'unite_intervals',[]) if e.isPlaying()]+[effect]
 effect.start()
 return effect
