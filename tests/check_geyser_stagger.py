import sys,traceback,random
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from panda3d.core import loadPrcFileData
loadPrcFileData('','audio-library-name null')
from panda_battle import PandaBattle
from battle_engine import Action
app=PandaBattle(offscreen=True,timed=False,seed=1)
try:
 class Delays:
  def __init__(self):self.values=iter((0,.2,.5,.9))
  def random(self):return next(self.values)
 app.presentation_rng=Delays();state=app.game.rng.getstate()
 app.display_cog_hp=[c.hp for c in app.game.cogs];app.display_toon_hp=[t.hp for t in app.game.toons]
 original=list(app.display_cog_hp)
 e={'kind':'gags','track':'Squirt','actions':[Action(0,'Geyser')],'targets':{0:[0,1,2,3]},'health':[('cog',i,-1) for i in range(4)],'misses':[]}
 c=app.geyser_movie(e);assert app.game.rng.getstate()==state
 props=[n for n,a in app.movie_props if n.getName()=='battle-prop-geyser'][::2]
 c.start();c.pause();c.setT(2.6)
 assert [not p.isHidden() for p in props]==[True,False,False,False]
 c.setT(3);assert app.display_cog_hp==[original[0]-1,*original[1:]]
 assert app.cog_nodes[0].getZ()>0 and all(n.getZ()==0 for n in app.cog_nodes[1:])
 c.setT(3.5);assert app.display_cog_hp==[original[0]-1,original[1]-1,original[2]-1,original[3]]
 c.finish();assert app.display_cog_hp==[n-1 for n in original]
 app.clear_movie_props();app.presentation_rng=random.Random(4)
 app.new_battle();app.game.roll=lambda _:True;app.selected={0:Action(0,'Geyser')};app.resolve()
 for _ in range(180):
  for clip in getattr(app,'live_departures',[]):
   if clip.isPlaying():clip.finish()
  if app.animation:app.animation.finish()
  app.taskMgr.step()
  if not app.animating:break
 assert not app.animating and app.display_cog_hp==[c.hp for c in app.game.cogs]
 Path('work/geyser-stagger-result.txt').write_text('PASS: independent eruptions, launch/HP synchronization, combat RNG untouched, one HP application, live round.')
except Exception:
 Path('work/geyser-stagger-result.txt').write_text(traceback.format_exc());raise
finally:app.destroy()
