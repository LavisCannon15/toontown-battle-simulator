import sys,traceback
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from panda3d.core import loadPrcFileData,Vec3
loadPrcFileData('','audio-library-name null')
from panda_battle import PandaBattle,Cog
app=PandaBattle(offscreen=True,timed=False,seed=1)
try:
 for name in ('Yesman','Bottom Feeder','Double Talker','Glad Hander'):
  app.game.cogs=[Cog(name,5)];app.spawn_characters()
  for miss in (False,True):
   app.game.toons[0].hp=100;app.display_toon_hp=[t.hp for t in app.game.toons];app.display_cog_hp=[c.hp for c in app.game.cogs]
   c=app.cog_movie(dict(kind='cog',cog=0,name='Rubber Stamp',targets=[0],misses=[0] if miss else [],health=[] if miss else [('toon',0,-5)],live=True));c.start();c.pause()
   props={n.getName():n for n,a in app.movie_props};stamp=props['battle-prop-rubber-stamp'];pad=props['battle-prop-pad'];mark=props['rubber-stamp-cancelled']
   assert mark.find('**/CANCELLED').node().getText()=='CANCELLED\nCANCELLED\nCANCELLED'
   assert mark.getNumChildren()==2
   for step in range(1,int(c.getDuration()*100)+1):
    c.setT(step/100)
    if step==100:
     assert stamp.getParent()==app.cog_actors[0].find('**/joint_Rhold')
     assert pad.getParent()==app.cog_actors[0].find('**/joint_Lhold')
     assert abs(pad.getX()-(.19 if name in ('Bottom Feeder','Glad Hander') else -.65))<.001
    if step==300:assert mark.isHidden()
    if step==311:
     assert not mark.isHidden();launch=Vec3(mark.getPos())
    if step==359:
     assert (mark.getPos()-launch).length()>.1
    if step==361:
     assert mark.isHidden()
     distance=(mark.getPos()-app.toon_nodes[0].getPos()-Vec3(0,0,2)).length()
     assert abs(distance-(3.1 if miss else 0))<.01,distance
   c.finish();assert app.game.toons[0].hp==(100 if miss else 95)
   for r in getattr(app,'live_departures',[]):r.finish()
   app.live_departures=[];app.clear_movie_props();assert mark.isEmpty()
 Path('work/rubber-stamp-result.txt').write_text('PASS: four Cogs, hit/miss, body-specific hand transforms, three-line/two-sided imprint, flight endpoints, live damage and cleanup.')
except Exception:
 Path('work/rubber-stamp-result.txt').write_text(traceback.format_exc());raise
finally:app.destroy()
