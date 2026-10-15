import sys,traceback
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from panda3d.core import loadPrcFileData
loadPrcFileData('','audio-library-name null')
from panda_battle import PandaBattle
from battle_engine import Action
from sound_sequence import schedule,movie
app=PandaBattle(offscreen=True,timed=False,seed=1)
try:
 actions=[Action(0,'Foghorn'),Action(1,'Bike Horn'),Action(2,'Aoogah'),Action(3,'Aoogah')]
 assert [(a.toon,t) for a,t in schedule(actions)]==[(1,0),(2,2),(3,2),(0,4)]
 e={'kind':'gags','track':'Sound','actions':actions,'targets':{i:[0,1,2,3] for i in range(4)},'health':[],'misses':[]}
 c=movie(app,e);c.start();c.pause();c.setT(.5)
 def props(name):return [n for n,a in app.movie_props if n.getName()=='battle-prop-'+name]
 assert not props('bikehorn')[0].isHidden()
 assert all(n.isHidden() for n in props('aoogah')+props('fog_horn'))
 c.setT(2.5);assert all(not n.isHidden() for n in props('aoogah'));assert props('fog_horn')[0].isHidden()
 c.setT(4.5);assert not props('fog_horn')[0].isHidden()
 c.finish();app.clear_movie_props()
 for names in [('Bike Horn','Whistle','Aoogah','Foghorn'),('Foghorn',)*4,('Bike Horn','Aoogah','Foghorn','Opera Singer')]:
  app.new_battle();app.game.roll=lambda _:True
  app.selected={i:Action(i,name) for i,name in enumerate(names)};app.resolve()
  for _ in range(180):
   for c in getattr(app,'live_departures',[]):
    if c.isPlaying():c.finish()
   if app.animation:app.animation.finish()
   app.taskMgr.step()
   if not app.animating:break
  assert not app.animating
  assert app.display_cog_hp==[c.hp for c in app.game.cogs]
 Path('work/sound-stagger-result.txt').write_text('PASS: level order, matching-group synchronization, staggered visibility, mixed/same/Opera live rounds and HP parity.')
except Exception:
 Path('work/sound-stagger-result.txt').write_text(traceback.format_exc());raise
finally:app.destroy()
