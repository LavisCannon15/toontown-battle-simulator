import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from panda3d.core import loadPrcFileData,BitMask32
loadPrcFileData('','audio-library-name null')
from panda_battle import PandaBattle
from battle_engine import Cog
app=PandaBattle(seed=1,offscreen=True,timed=False)
try:
 assert set(app.reward_shortcuts)=={'FIRE','SOS','PASS','RUN'}
 for mask in range(1,16):
  for i in range(4):app.game.toons[i].hp=100 if mask&(1<<i) else 0;app.game.cogs[i].hp=100 if mask&(1<<i) else 0
  targets=list(app.formation_positions());expected=[4*(i-(mask.bit_count()-1)/2) for i in range(mask.bit_count())]
  move=app.formation_interval();move.start();move.finish()
  for nodes,team in [(app.toon_nodes,app.game.toons),(app.cog_nodes,app.game.cogs)]:assert [n.getX() for n,t in zip(nodes,team) if t.alive]==expected
 app.hide_defeated();app.open_fire();assert set(app.fire_buttons)=={0,1,2,3};app.close_modal()
 app.game.cogs[1].hp=0;app.open_fire();assert set(app.fire_buttons)=={0,2,3};app.close_modal()
 for toon in app.game.toons:toon.hp=0
 app.finish_round()
 assert all(n.isHidden() for n in app.toon_nodes)
 for c,a in zip(app.game.cogs,app.cog_actors):
  if c.alive:assert a.getCurrentAnim()=='victory' and a.getNumFrames('victory')>1
 for skeleton in (False,True):
  for name in ('Flunky','Pencil Pusher','The Big Cheese'):
   c=Cog(name,8,skelecog=skeleton);root=app.render.attachNewNode('test');actor=app.art.cog(c,root)
   assert actor.getNumFrames('victory')>1;actor.loop('victory');root.removeNode()
 app.new_battle();assert all(not n.isHidden() for n in app.toon_nodes+app.cog_nodes)
 print('All 15 surviving-slot formations, Fire living-target filtering, restored buttons, and regular/Skelecog victory clips passed.')
finally:app.destroy()
