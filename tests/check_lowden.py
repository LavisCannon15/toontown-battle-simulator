import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from panda3d.core import loadPrcFileData
loadPrcFileData('','audio-library-name null')
from panda_battle import PandaBattle
from battle_engine import Action
app=PandaBattle(offscreen=True,timed=False,seed=1)
try:
 action=Action(0,'SOS: Lord Lowden Clear',None)
 stock=app.game.toons[0].rewards[action.gag]
 app.selected={0:action};app.resolve();app.animation.pause();app.animation.setT(4.8)
 guest=app.render.find('**/sos-lord-lowden-clear');assert not guest.isEmpty() and not guest.isHidden()
 assert app.render.findAllMatches('**/fire-cannon').getNumPaths()==4
 assert app.render.find('**/battle-prop-dust').isEmpty()
 assert app.render.find('**/cog-breakup').isEmpty()
 app.position_nametags()
 for _ in range(3):app.graphicsEngine.renderFrame()
 app.win.saveScreenshot(str(Path('reports/lowden-group-fire.png').resolve()))
 for _ in range(80):
  if app.animation:app.animation.finish()
  app.taskMgr.step()
  if not app.animating:break
 assert not app.animating and all(not c.alive for c in app.game.cogs)
 assert app.game.toons[0].rewards[action.gag]==stock-1
 assert all(n.isHidden() for n in app.cog_nodes)
 print('Lowden disguise, four cannons, no dust/breakup, one card spent, victory and cleanup passed.')
finally:app.destroy()
