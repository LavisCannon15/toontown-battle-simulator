import sys,traceback
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from panda3d.core import loadPrcFileData,Vec3
loadPrcFileData('','audio-library-name null')
from panda_battle import PandaBattle,Cog
app=PandaBattle(offscreen=True,timed=False,seed=1)
try:
 for miss,cancel,lethal in [(False,False,False),(True,False,False),(False,True,False),(False,False,True)]:
  app.game.cogs=[Cog('Downsizer',7)];app.spawn_characters();app.game.toons[0].hp=3 if lethal else 100
  app.display_toon_hp=[t.hp for t in app.game.toons];app.display_cog_hp=[c.hp for c in app.game.cogs]
  c=app.cog_movie(dict(kind='cog',cog=0,name='Pink Slip',targets=[0],misses=[0] if miss else [],health=[] if miss else [('toon',0,-5)],live=True));c.start();c.pause()
  paper=next(n for n,a in app.movie_props if n.getName()=='battle-prop-pink-slip');pos=app.toon_nodes[0].getPos(app.render)
  for step in range(1,int((3.9 if cancel else c.getDuration())*100)+1):
   c.setT(step/100)
   if step==150:
    assert paper.getParent()==app.cog_actors[0].find('**/joint_Rhold')
    lo,hi=paper.getTightBounds(app.render);assert .1<(hi-lo).length()<3
   if step==320:assert paper.getParent()==app.render
   if step==353:assert (paper.getPos()-pos-Vec3(0,0,.124)).length()<.01
   if step==374 and not miss:assert abs(paper.getZ()-(pos.z+2.604))<.01
   if step==370:assert app.game.toons[0].hp==(3 if lethal else 100)
   if step==380:assert app.game.toons[0].hp==(0 if lethal else 100 if miss else 95)
  if cancel:c.pause()
  else:c.finish();assert paper.isHidden()
  for r in getattr(app,'live_departures',[]):r.pause() if cancel or lethal else r.finish()
  app.live_departures=[];app.clear_movie_props();assert paper.isEmpty()
 Path('work/pink-slip-result.txt').write_text('PASS: hit/miss paths, hand model size, ground arrival, tumble height, live damage timing, fatal/cancel and cleanup.')
except Exception:
 Path('work/pink-slip-result.txt').write_text(traceback.format_exc());raise
finally:app.destroy()
