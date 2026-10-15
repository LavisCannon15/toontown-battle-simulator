import sys,traceback
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from panda3d.core import loadPrcFileData,Vec3
loadPrcFileData('','audio-library-name null')
from panda_battle import PandaBattle
app=PandaBattle(offscreen=True,timed=False,seed=1)
try:
 for miss in (False,True):
  e={'kind':'cog','cog':0,'name':'Razzle Dazzle','targets':[1],'misses':[1] if miss else [],'health':[]}
  heading=Vec3(app.cog_nodes[0].getHpr());c=app.cog_movie(e)
  sign=next(n for n,a in app.movie_props if n.getName()=='battle-prop-smile');effect=app.movie_particles[-1]
  c.start();c.pause();c.setT(.3);assert sign.isHidden()
  c.setT(.75);assert not sign.isHidden() and 1<sign.getScale().x<1.39
  assert sign.getParent()==app.cog_actors[0].find('**/joint_Rhold')
  c.setT(1.51);assert effect.getParent()==app.render
  start=Vec3(effect.getPos());c.setT(2.5);assert (effect.getPos()-start).length()>.5
  c.setT(3.5);end=app.toon_nodes[1].getPos()+Vec3(0,0,2.5)
  distance=(effect.getPos()-end).length();assert abs(distance-(5 if miss else 0))<.01
  c.finish();assert sign.isHidden() and (app.cog_nodes[0].getHpr()-heading).length()<.01
  app.clear_movie_props();assert not app.movie_particles and sign.isEmpty()
 Path('work/razzle-result.txt').write_text('PASS: sign timing/attachment/growth, moving sparkle hit/miss endpoints, heading restoration and cleanup.')
except Exception:
 Path('work/razzle-result.txt').write_text(traceback.format_exc());raise
finally:app.destroy()
