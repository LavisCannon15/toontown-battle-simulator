import sys,traceback
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from panda3d.core import loadPrcFileData
loadPrcFileData('','audio-library-name null')
from panda_battle import PandaBattle,Cog
app=PandaBattle(offscreen=True,timed=False,seed=1)
try:
 heights=[]
 for level in (4,8):
  for skeleton in (False,True):
   app.game.cogs=[Cog('Micromanager',level,skelecog=skeleton)];app.spawn_characters();a=app.cog_actors[0]
   assert abs(a.getScale().x-(2.5/4.14)*.62)<.0001
   if not skeleton:
    lo,hi=a.getTightBounds();heights.append(hi.z-lo.z)
 assert abs(heights[0]-heights[1])<.001 and 1.5<heights[0]<2.6,heights
 for name in ('Glad Hander','The Mingler'):
  for miss in (False,True):
   app.game.cogs=[Cog(name,8)];app.spawn_characters();app.game.toons[0].hp=100
   app.display_toon_hp=[t.hp for t in app.game.toons];app.display_cog_hp=[c.hp for c in app.game.cogs]
   c=app.cog_movie(dict(kind='cog',cog=0,name='Schmooze',targets=[0],misses=[0] if miss else [],health=[] if miss else [('toon',0,-5)],live=True));c.start();c.pause()
   effects=app.movie_particles;assert len(effects)==8 and len({e.getName() for e in effects})==8
   for step in range(1,int(c.getDuration()*100)+1):
    c.setT(step/100)
    if step==140:
     assert effects[0].getParent()==app.cog_actors[0]
     assert effects[1].getParent()!=app.cog_actors[0]
    if step==210:assert effects[1].getParent()==app.cog_actors[0]
   c.finish();assert app.game.toons[0].hp==(100 if miss else 95)
   for r in getattr(app,'live_departures',[]):r.finish()
   app.live_departures=[];app.clear_movie_props();assert not app.movie_particles
 Path('work/schmooze-size-result.txt').write_text(f'PASS: both Schmooze Cogs hit/miss, eight staggered effects, live damage and cleanup; Micromanager fixed scale at both levels, including skeleton. Rendered height {heights[0]:.3f}.')
except Exception:
 Path('work/schmooze-size-result.txt').write_text(traceback.format_exc());raise
finally:app.destroy()
