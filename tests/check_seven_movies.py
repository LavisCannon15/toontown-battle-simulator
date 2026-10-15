"""Exercise native attachments and animation stages at their playback timestamps."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from panda3d.core import loadPrcFileData,Vec3
loadPrcFileData('','audio-library-name null')
from panda_battle import PandaBattle
from battle_engine import Action
from audited_gags import heal,squirt,lure
app=PandaBattle(offscreen=True,timed=False,seed=1)
def prop(name):return next(n for n,a in app.movie_props if n.getName()=='battle-prop-'+name)
def seek(c,t):c.start();c.pause();c.setT(t)
try:
 c,_=heal(app,Action(0,'Lipstick'),[1],[]);seek(c,3.1)
 assert abs(prop('lips').getScale().x-3)<.01
 c.finish();app.clear_movie_props()
 c,_=heal(app,Action(0,'Bamboo Cane'),[1],[]);seek(c,1)
 assert 'Lhold' in prop('cane').getParent().getName()
 assert 'Rhold' in prop('hat').getParent().getName()
 c.finish();app.clear_movie_props()
 c,_=squirt(app,Action(0,'Squirt Gun'),[0],[]);seek(c,1)
 assert abs(prop('water-gun').getH()-85.6)<.01
 assert not prop('water-gun').find('**/joint_nozzle').isEmpty()
 c.finish();app.clear_movie_props()
 app.game.cogs[0].lure=3
 c,_=lure(app,Action(0,'Hypno-goggles'),[0],[]);seek(c,4)
 assert abs(app.cog_nodes[0].getY()-2.2)<.01
 c.finish();assert app.game.cogs[0].lure_pose=='idle';app.clear_movie_props()
 app.toon_nodes[0].setPos(0,0,0);app.toon_nodes[0].setH(180)
 original=Vec3(app.toon_actors[0]['legs'].getScale())
 c,_=heal(app,Action(0,'High Dive'),[1],[]);seek(c,4)
 assert abs(app.toon_nodes[0].getZ())<.01, 'Climb root must not be lifted twice'
 c.setT(6.5);assert not prop('splashdown').isHidden()
 c.finish();assert (app.toon_actors[0]['legs'].getScale()-original).length()<.001
 app.clear_movie_props()
 Path('work/seven-check-result.txt').write_text('Attachment and stage checks passed.\n')
except Exception:
 import traceback
 Path('work/seven-error.txt').write_text(traceback.format_exc());raise
finally:app.destroy()
