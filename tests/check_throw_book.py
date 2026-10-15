"""Real law-book asset: arc, head contact, miss landing, fixed scale and health."""
import sys,traceback
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from panda3d.core import loadPrcFileData,Vec3
loadPrcFileData('','audio-library-name null')
from panda_battle import PandaBattle,Cog
from throw_book_movie import RELEASE,FLIGHT,IMPACT
app=PandaBattle(offscreen=True,timed=False,seed=1)
try:
 for target in (0,3):
  for miss in (False,True):
   app.game.cogs=[Cog('Big Wig',10)];app.spawn_characters();app.game.toons[target].hp=100
   app.display_toon_hp=[t.hp for t in app.game.toons];app.display_cog_hp=[app.game.cogs[0].hp]
   event=dict(kind='cog',cog=0,name='Throw Book',targets=[target],misses=[target] if miss else [],health=[] if miss else [('toon',target,-5)],live=True)
   clip=app.cog_movie(event);book=next(n for n,a in app.movie_props if n.getName()=='battle-prop-lawbook');clip.start();clip.pause();positions={}
   for step in range(1,int(clip.getDuration()*100)+2):
    time=min(step/100,clip.getDuration());clip.setT(time)
    if step==100:
     assert not book.isHidden() and 'Rhold' in book.getParent().getName()
     raw_lo,raw_hi=book.getChild(0).getTightBounds();extent=max(raw_hi-raw_lo)*book.getScale(app.render).x
     assert .3<extent<1.5,extent
     scale=Vec3(book.getScale(app.render))
    if RELEASE<=time<IMPACT:
     assert book.getParent()==app.render
     assert (book.getScale(app.render)-scale).length()<.00001
     assert app.game.toons[target].hp==100,'Damage before landing'
    if step in (303,363,423):positions[step]=Vec3(book.getPos(app.render))
    if step==423:
     if not miss:
      head=app.toon_actors[target]['torso'].find('**/def_head').getChild(0)
      assert book.getParent()==head
      # Exclude the newly attached book when measuring the head's bounds.
      book.wrtReparentTo(app.render);hl,hh=head.getTightBounds(app.render);bl,bh=book.getTightBounds(app.render)
      assert abs(bl.z-hh.z)<.05,(bl,hh)
      book.wrtReparentTo(head)
     else:
      bl,bh=book.getTightBounds(app.render);assert abs(bl.z-.04)<.05,bl
    if target==0 and not miss and step in (363,423):
     app.position_nametags()
     for _ in range(3):app.graphicsEngine.renderFrame()
     app.win.saveScreenshot(f'work/throw-book-{step}.png')
   assert positions[363].z>(positions[303].z+positions[423].z)/2+2,'Flight is still straight'
   assert app.game.toons[target].hp==(100 if miss else 95)
   clip.finish();assert book.isHidden()
   for r in getattr(app,'live_departures',[]):r.pause()
   app.live_departures=[];app.clear_movie_props();assert book.isEmpty()
 # Cancelling during flight must not apply damage later.
 app.game.toons[0].hp=100;app.spawn_characters();app.display_toon_hp=[t.hp for t in app.game.toons]
 clip=app.cog_movie(dict(kind='cog',cog=0,name='Throw Book',targets=[0],misses=[],health=[('toon',0,-5)],live=True));clip.start();clip.pause()
 for step in range(1,364):clip.setT(step/100)
 clip.pause();app.clear_movie_props();assert app.game.toons[0].hp==100
 Path('work/throw-book-result.txt').write_text('PASS: both outer targets hit/miss; curved flight, fixed held/released scale, head/ground contact, damage only at impact, prop cleanup and cancellation.')
except Exception:
 Path('work/throw-book-result.txt').write_text(traceback.format_exc());raise
finally:app.destroy()
