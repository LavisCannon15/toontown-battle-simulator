import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from panda3d.core import loadPrcFileData
loadPrcFileData('','audio-library-name null\nwin-size 1440 900')
from panda_battle import PandaBattle
from battle_engine import GAGS,Action
from audited_gags import drop
app=PandaBattle(offscreen=True,timed=False)
try:
 app.animating=True;app.make_hud()
 for name,g in GAGS.items():
  if g.track!='Drop':continue
  for miss in (False,True):
   targets=list(range(4)) if g.group else [0]
   clip,_=drop(app,Action(0,name,0),targets,targets if miss else [])
   shadow=next(n for n,a in app.movie_props if n.getName()=='falling-gag-shadow')
   clip.start();clip.pause();clip.setT(2.4);assert shadow.isHidden()
   clip.setT(2.6);small=shadow.getSx();assert not shadow.isHidden()
   clip.setT(4.2);assert shadow.getSx()>small
   assert shadow.getBinName()=='transparent' and not shadow.getDepthWrite()
   assert shadow.getZ()>.06
   if miss and g.level>=4:assert shadow.getY()>app.cog_nodes[0].getY()
   if name=='Grand Piano' and not miss:
    for _ in range(3):app.graphicsEngine.renderFrame()
    app.win.saveScreenshot(str(Path('work/drop-shadow-fix/piano.png').resolve()))
   clip.setT(4.61);assert shadow.isHidden()
   clip.finish();app.clear_movie_props();assert shadow.isEmpty()
 from sos_movies import arrival,performance,remove
 app.new_battle();app.display_cog_hp=[c.hp for c in app.game.cogs]
 arrive=arrival(app,Action(0,'SOS: Barnacle Bessie'));arrive.start();arrive.finish()
 clip=performance(app,0);shadows=[n for n,a in app.movie_props if n.getName()=='falling-gag-shadow']
 assert len(shadows)==4
 clip.start();clip.pause();clip.setT(2.6);assert sum(not n.isHidden() for n in shadows)==1
 clip.setT(3.6);assert sum(not n.isHidden() for n in shadows)==2
 clip.finish();assert all(n.isHidden() for n in shadows)
 remove(app,0);app.clear_movie_props();assert all(n.isEmpty() for n in shadows)
 print('SOS Drop target staggering and shadow cleanup passed.')
 print('Seven Drop shadows: hit/miss positions, growth, draw order, timing and cleanup passed.')
finally:app.destroy()
