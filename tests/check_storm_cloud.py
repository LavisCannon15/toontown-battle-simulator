import sys,traceback
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from panda3d.core import loadPrcFileData
loadPrcFileData('','audio-library-name null')
from panda_battle import PandaBattle
from battle_engine import Action
from audited_gags import squirt
app=PandaBattle(offscreen=True,timed=False,seed=1)
try:
 lengths=[]
 for miss in (False,True):
  c,impact=squirt(app,Action(0,'Storm Cloud',0),[0],[0] if miss else [])
  assert impact==2.9 and len(app.movie_particles)==4
  cloud,actor=next((n,a) for n,a in app.movie_props if n.getName()=='battle-prop-stormcloud')
  assert not any(n.getName()=='battle-prop-spray' for n,a in app.movie_props)
  c.start();c.pause();c.setT(.5);assert 0<cloud.getScale().x<3*app.cog_actors[0].getScale().z
  c.setT(1.5);assert abs(cloud.getScale().x-3*app.cog_actors[0].getScale().z)<.01
  c.setT(2);assert actor.getCurrentFrame('prop')==0
  lengths.append(c.getDuration());c.finish();assert cloud.isHidden();app.clear_movie_props();assert not app.movie_particles
 assert lengths[0]>lengths[1]
 e={'actions':[Action(0,'Storm Cloud',0)],'targets':{0:[0]},'track':'Squirt'}
 assert 'Actor-soak' in str(app.cog_damage_reaction(e,0))
 for hit in (True,False):
  app.new_battle();app.game.roll=lambda chance:hit
  app.selected={0:Action(0,'Storm Cloud',0)};app.resolve()
  for _ in range(180):
   for c in getattr(app,'live_departures',[]):
    if c.isPlaying():c.finish()
   if app.animation:app.animation.finish()
   app.taskMgr.step()
   if not app.animating:break
  assert not app.animating and not app.movie_particles
  assert app.display_cog_hp==[c.hp for c in app.game.cogs]
 Path('work/storm-result.txt').write_text('PASS: growth, rain stages, hit/miss durations, soak, live rounds and cleanup.')
except Exception:
 Path('work/storm-result.txt').write_text(traceback.format_exc());raise
finally:app.destroy()
