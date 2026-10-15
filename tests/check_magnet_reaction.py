import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from panda3d.core import loadPrcFileData
loadPrcFileData('','audio-library-name null')
from panda_battle import PandaBattle
from battle_engine import Action
from audited_gags import lure
app=PandaBattle(offscreen=True,timed=False,seed=1)
try:
 for name in ('Small Magnet','Big Magnet'):
  app.new_battle()
  app.display_cog_hp=[c.hp for c in app.game.cogs]
  for c in app.game.cogs:c.lure=2
  clip,_=lure(app,Action(0,name),list(range(4)),[])
  assert 'Actor-hypnotized' not in str(clip) and 'Actor-landing' in str(clip)
  clip.start();clip.pause()
  for t in (2.6,3.2,3.7,4.0,4.8):clip.setT(t)
  clip.finish()
  for i,c in enumerate(app.game.cogs):
   assert c.lure_pose=='idle' and abs(app.cog_nodes[i].getY()-2.2)<.001
   assert app.cog_actors[i].getCurrentAnim()=='idle'
  transition=app.lure_transition({'lure_before':[0]*4,'lure_after':[2]*4})
  assert 'hypnotized' not in str(transition)
  miss,_=lure(app,Action(0,name),list(range(4)),list(range(4)))
  assert 'Actor-landing' not in str(miss) and 'Actor-hypnotized' not in str(miss)
  app.clear_movie_props()
 print('Both magnets: native landing reaction, neutral recovery, forward movement and no miss/hypno reaction passed.')
finally:app.destroy()
