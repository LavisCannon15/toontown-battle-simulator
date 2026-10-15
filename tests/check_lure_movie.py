import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from panda3d.core import loadPrcFileData
loadPrcFileData('','audio-library-name null')
from panda_battle import PandaBattle
from battle_engine import Action
app=PandaBattle(seed=1,offscreen=True,timed=False)
try:
 app.game.roll=lambda chance:True
 app.selected={0:Action(0,'Hypno-goggles')};app.resolve();app.animation.finish()
 assert all(abs(n.getY()-2.2)<.001 for n in app.cog_nodes)
 assert all(c.lure for c in app.game.cogs)
 app.selected={0:Action(0,'Bike Horn')};app.resolve();app.animation.finish()
 assert all(abs(n.getY()-3.7)<.001 for n,c in zip(app.cog_nodes,app.game.cogs) if c.alive)
 assert not any(c.lure for c in app.game.cogs)
 app.game.toons[1].hp=0;clip=app.formation_interval();clip.start();clip.pause();clip.setT(.4)
 assert any((a['legs'].getCurrentFrame('walk') or 0)>0 for a in app.toon_actors)
 clip.finish();assert all(abs(n.getH())<.01 for n,t in zip(app.toon_nodes,app.game.toons) if t.alive)
 print('Successful Lure moves forward; Sound unlures and returns Cogs; formation gaps use walking and restore headings.')
finally:app.destroy()
