import sys,traceback
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from panda3d.core import loadPrcFileData,Vec3
loadPrcFileData('','audio-library-name null')
from panda_battle import PandaBattle,Cog
app=PandaBattle(offscreen=True,timed=False,seed=1)
try:
 for name in ('Micromanager','Mover & Shaker'):
  for miss in (False,True):
   app.game.cogs=[Cog(name,6)];app.spawn_characters();app.game.toons[0].hp=100
   app.display_toon_hp=[t.hp for t in app.game.toons];app.display_cog_hp=[c.hp for c in app.game.cogs]
   c=app.cog_movie(dict(kind='cog',cog=0,name='Brain Storm',targets=[0],misses=[0] if miss else [],health=[] if miss else [('toon',0,-5)],live=True));c.start();c.pause()
   cloud,channel=next((n,a) for n,a in app.movie_props if n.getName()=='battle-prop-stormcloud');effects=app.movie_particles
   assert [e.getName() for e in effects]==['brainstorm-box','brainstorm-env','brainstorm-track']
   for step in range(1,int(c.getDuration()*100)+1):
    c.setT(step/100)
    if step==290:
     assert (cloud.getPos(app.render)-app.toon_nodes[0].getPos()-Vec3(0,0,3.86)).length()<.01
     assert channel.getCurrentFrame('prop')==0
    if step==410:assert effects[0].getParent()==cloud and effects[1].getParent()!=cloud
    if step==460:assert effects[1].getParent()==cloud and effects[2].getParent()!=cloud
    if step==510:assert effects[2].getParent()==cloud and channel.getCurrentFrame('prop')!=0
    if step==449:assert app.game.toons[0].hp==100
   c.finish();assert app.game.toons[0].hp==(100 if miss else 95)
   for r in getattr(app,'live_departures',[]):r.finish()
   app.live_departures=[];assert cloud.isHidden();app.clear_movie_props();assert not app.movie_particles
 Path('work/brain-storm-result.txt').write_text('PASS: both Cogs hit/miss, cloud travel, three staggered sprites, native cloud channel, live damage and cleanup.')
except Exception:
 Path('work/brain-storm-result.txt').write_text(traceback.format_exc());raise
finally:app.destroy()
