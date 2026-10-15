import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from panda3d.core import loadPrcFileData
loadPrcFileData('','audio-library-name null')
from panda_battle import PandaBattle
from battle_engine import Action
from support import SOS
from sos_movies import arrival,remove
app=PandaBattle(offscreen=True,timed=False,seed=1)
def finish():
 for _ in range(160):
  for c in getattr(app,'live_departures',[]):
   if c.isPlaying():c.finish()
  if app.animation:app.animation.finish()
  app.taskMgr.step()
  if not app.animating:return
 raise AssertionError('Battle stalled')
try:
 for name in SOS:
  a=Action(0,name,None);clip=arrival(app,a);clip.start();clip.finish()
  guest=app.sos_guests[0]
  assert guest['root'].getY()>app.toon_nodes[0].getY() and len(app.toon_nodes)==4
  if name=='SOS: Flippy':
   app.animating=True;app.make_hud();app.position_nametags()
   for _ in range(3):app.graphicsEngine.renderFrame()
   app.win.saveScreenshot(str(Path('reports/sos-npc-arrival.png').resolve()));app.animating=False
  remove(app,0);app.clear_movie_props()
 for name in ('SOS: Flippy','SOS: Barnacle Bessie','SOS: Lil Oldman','SOS: Professor Pete','SOS: Clerk Clara'):
  app.new_battle();app.game.toons[0].hp=50
  app.selected={0:Action(0,name,None)};app.resolve();finish()
  assert not app.sos_guests and len(app.toon_nodes)==4
 app.new_battle();app.game.toons[0].hp=20
 app.selected={0:Action(0,'SOS: Flippy',None),1:Action(1,'SOS: Daffy Don',None)}
 app.resolve();finish();assert not app.sos_guests and len(app.toon_nodes)==4
 print('All SOS guest models loaded; five live reward tracks, front-of-caller placement and cleanup passed.')
finally:app.destroy()
