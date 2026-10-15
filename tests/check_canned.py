import sys,traceback
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from panda3d.core import loadPrcFileData
loadPrcFileData('','audio-library-name null')
from panda_battle import PandaBattle,Cog
app=PandaBattle(offscreen=True,timed=False,seed=1)
try:
 for name in ('Downsizer','Corporate Raider'):
  for miss in (False,True):
   app.game.cogs=[Cog(name,7)];app.spawn_characters();app.game.toons[0].hp=100
   app.display_toon_hp=[t.hp for t in app.game.toons];app.display_cog_hp=[c.hp for c in app.game.cogs]
   c=app.cog_movie(dict(kind='cog',cog=0,name='Canned',targets=[0],misses=[0] if miss else [],health=[] if miss else [('toon',0,-5)],live=True));c.start();c.pause()
   can=next(n for n,a in app.movie_props if n.getName()=='battle-prop-can');arrival=3.93 if name=='Corporate Raider' else 4.63
   for step in range(1,int(c.getDuration()*100)+1):
    c.setT(step/100)
    if step==150:assert can.getParent()==app.cog_actors[0].find('**/joint_Rhold')
    if step==round((arrival+.1)*100):
     assert can.getParent()==(app.render if miss else app.toon_actors[0]['legs'].find('**/joint_hips'))
     if not miss:
      lo,hi=can.getTightBounds(app.render);center=(lo+hi)*.5;pos=app.toon_nodes[0].getPos(app.render)
      assert abs(center.x-pos.x)<.05 and abs(center.y-pos.y)<.05 and lo.z>-.05
      assert 1.5<hi.z-lo.z<3
    if step==round((arrival+.8)*100):assert app.game.toons[0].hp==100
   c.finish();assert can.isHidden();assert app.game.toons[0].hp==(100 if miss else 95)
   for r in getattr(app,'live_departures',[]):r.finish()
   app.live_departures=[];app.clear_movie_props();assert can.isEmpty()
 Path('work/canned-result.txt').write_text('PASS: both body types hit/miss, hand/release/hip states, fitted can geometry, delayed health and cleanup.')
except Exception:
 Path('work/canned-result.txt').write_text(traceback.format_exc());raise
finally:app.destroy()
