import sys,traceback
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from panda3d.core import loadPrcFileData,Vec3
loadPrcFileData('','audio-library-name null')
from panda_battle import PandaBattle,Cog
app=PandaBattle(offscreen=True,timed=False,seed=1)
try:
 for name in ('Penny Pincher','Tightwad','Cold Caller'):
  app.game.cogs=[Cog(name,5)];app.spawn_characters()
  for miss in (False,True):
   app.game.toons[0].hp=100;app.display_toon_hp=[t.hp for t in app.game.toons];app.display_cog_hp=[c.hp for c in app.game.cogs]
   c=app.cog_movie(dict(kind='cog',cog=0,name='Freeze Assets',targets=[0],misses=[0] if miss else [],health=[] if miss else [('toon',0,-5)],live=True));c.start();c.pause()
   cloud,channel=next((n,a) for n,a in app.movie_props if n.getName()=='battle-prop-stormcloud')
   assert len(app.movie_particles)==1;snow=app.movie_particles[0]
   for step in range(1,int(c.getDuration()*100)+1):
    c.setT(step/100)
    if step==100:initial=Vec3(cloud.getPos(app.render))
    if step==290:
     assert (cloud.getPos(app.render)-initial).length()>1
     assert (cloud.getPos(app.render)-app.toon_nodes[0].getPos()-Vec3(0,0,3.86)).length()<.01
    if step==320:
     assert snow.getParent()==cloud
     assert channel.getCurrentFrame('prop')==0
   c.finish();assert app.game.toons[0].hp==(100 if miss else 95)
   for r in getattr(app,'live_departures',[]):r.finish()
   app.live_departures=[];assert cloud.isHidden()
   app.clear_movie_props();assert cloud.isEmpty() and not app.movie_particles
 Path('work/freeze-assets-result.txt').write_text('PASS: three Cogs hit/miss; cloud travels above target, stays posed, emits snow; live health and cleanup.')
except Exception:
 Path('work/freeze-assets-result.txt').write_text(traceback.format_exc());raise
finally:app.destroy()
