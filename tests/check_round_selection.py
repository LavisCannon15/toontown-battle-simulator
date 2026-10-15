"""Next Toon resets focus for the next round and honors manual control."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from panda3d.core import loadPrcFileData
loadPrcFileData('','audio-library-name null')
from panda_battle import PandaBattle
app=PandaBattle(offscreen=True,timed=False,seed=1)
try:
 app.auto_resolve=False
 app.auto_modes=[False]*4
 for i in range(4):
  assert app.active==i
  app.choose_action('Pass')
 assert app.active==3
 app.finish_round()
 assert app.active==0 and app.active_ring.getParent()==app.toon_nodes[0]
 assert not app.selected and app.choice is None
 app.auto_advance=False;app.select_toon(3);app.finish_round()
 assert app.active==3
 app.auto_advance=True;app.game.toons[0].escaped=True
 app.auto_modes[1]=True;app.finish_round()
 assert app.active==2 and app.active_ring.getParent()==app.toon_nodes[2]
 app.auto_modes=[True]*4;app.finish_round()
 assert app.active==1
 print('Round focus resets to first living manual Toon; toggle, escaped Toons, Auto Toons and selection ring passed.')
finally:app.destroy()
