import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from panda3d.core import loadPrcFileData
loadPrcFileData('','audio-library-name null')
from panda_battle import PandaBattle
app=PandaBattle(offscreen=True,timed=False,seed=1)
try:
 actor=app.cog_actors[0]
 app.animating=True
 clip=app.cog_clip(0,'finger-wag',1);clip.start();clip.finish()
 assert actor.getCurrentAnim()=='idle'
 app.game.toons[0].hp=0;app.restore_cog_pose(0);assert actor.getCurrentAnim()=='idle'
 for toon in app.game.toons:toon.hp=0
 assert app.game.result
 app.restore_cog_pose(0);assert actor.getCurrentAnim()=='idle','Celebrated before the last movie ended'
 app.finish_round();assert all(a.getCurrentAnim()=='victory' for a in app.cog_actors)
 app.new_battle();assert all(a.getCurrentAnim()=='idle' for a in app.cog_actors)
 for toon in app.game.toons:toon.escaped=True
 app.animating=True;app.restore_cog_pose(0);assert app.cog_actors[0].getCurrentAnim()=='idle'
 app.finish_round();assert all(a.getCurrentAnim()=='victory' for a in app.cog_actors)
 app.new_battle();app.finish_round();assert all(a.getCurrentAnim()=='idle' for a in app.cog_actors)
 print('Cog victory waits for completed defeat/escape playback; attacks and continuing rounds return to idle.')
finally:app.destroy()
