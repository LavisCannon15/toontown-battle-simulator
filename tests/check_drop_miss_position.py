import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from panda3d.core import loadPrcFileData
loadPrcFileData('','audio-library-name null')
from panda_battle import PandaBattle
from battle_engine import Action,GAGS
from audited_gags import drop
app=PandaBattle(offscreen=True,timed=False,seed=1)
try:
 for name,gag in GAGS.items():
  if gag.track!='Drop':continue
  for lured in (False,True):
   app.game.cogs[0].lure=2 if lured else 0;app.cog_nodes[0].setPos(-6,2.2 if lured else 3.7,0)
   clip,_=drop(app,Action(0,name,0),[0],[0])
   prop=next(n for n,a in app.movie_props if n.getName()!='battle-prop-button' and n.getName().startswith('battle-prop-') and n.getName()!='battle-prop-drop-shadow')
   shadow=next(n for n,a in app.movie_props if n.getName()=='battle-prop-drop-shadow')
   expected=3.7+(2 if lured else 5) if gag.level>=4 else 3.7
   assert abs(prop.getX()+6)<.001 and abs(prop.getY()-expected)<.001,(name,lured,prop.getPos())
   assert abs(shadow.getY()-expected)<.001
   clip.start();clip.finish();app.clear_movie_props()
 print('All seven Drop miss positions and shadows passed, both unlured and lured.')
finally:app.destroy()
