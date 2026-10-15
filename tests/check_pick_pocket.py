"""Real-asset regression: bill remains posed in the moving right hand."""
import sys, traceback
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from panda3d.core import loadPrcFileData,Vec3
loadPrcFileData('', 'audio-library-name null')
from panda_battle import PandaBattle, Cog
app=PandaBattle(offscreen=True,timed=False,seed=1)
try:
 for name in ('Bottom Feeder','Short Change','Telemarketer','Name Dropper'):
  app.game.cogs=[Cog(name,3)];app.spawn_characters()
  for miss in (False,True):
   e=dict(kind='cog',cog=0,name='Pick Pocket',targets=[0],misses=[0] if miss else [],health=[])
   clip=app.cog_movie(e)
   bills=[(n,a) for n,a in app.movie_props if n.getName()=='battle-prop-1dollar']
   if miss:assert not bills
   clip.start();clip.pause()
   if not miss:
    bill,model=bills[0];clip.setT(.3);assert bill.isHidden()
    initial=model.getTightBounds()
    for t in (.8,1.1,1.5):
     clip.setT(t)
     assert not bill.isHidden()
     assert bill.getParent()==app.cog_actors[0].find('**/joint_Rhold')
     assert (bill.getPos()-Vec3(-.01,.45,-.25)).length()<.0001
     assert model.getCurrentFrame('prop')==0
     bounds=model.getTightBounds()
     assert all((a-b).length()<.0001 for a,b in zip(initial,bounds))
    assert abs(bill.getScale().x-1.41)<.0001
    clip.setT(2.16);assert bill.isHidden()
   clip.finish();app.clear_movie_props()
 Path('work/pick-pocket-result.txt').write_text('PASS: all four Cogs; posed bill attached to right hand; reference scale/timing; no bill on miss; cleanup.')
except Exception:
 Path('work/pick-pocket-result.txt').write_text(traceback.format_exc());raise
finally:app.destroy()
