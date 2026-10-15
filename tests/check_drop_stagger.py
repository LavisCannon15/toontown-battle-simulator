import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from panda3d.core import loadPrcFileData
loadPrcFileData('','audio-library-name null')
from panda_battle import PandaBattle
from battle_engine import Action
from drop_sequence import schedule
app=PandaBattle(offscreen=True,timed=False,seed=1)
try:
 for targets,expected in [([0,0,0,0],[0,.8,1.6,2.4]),([0,1,2,3],[0,1,2,3])]:
  actions=[Action(i,'Grand Piano',target) for i,target in enumerate(targets)]
  event={'kind':'gags','track':'Drop','actions':actions,'targets':{a.toon:[a.target] for a in actions},'health':[],'misses':[]}
  assert all(abs(x-y)<.001 for x,y in zip([d for a,d in schedule(event)[0]],expected))
  clip=app.gag_movie(event);assert 'Actor-flatten' in str(clip)
  assert 'Actor-drop-react' not in str(clip)
  clip.start();clip.finish();app.clear_movie_props()
 event['misses']=[0,1,2,3]
 clip=app.gag_movie(event);assert 'Actor-sidestep' not in str(clip)
 clip.start();clip.finish();app.clear_movie_props()
 for c in app.game.cogs:c.lure=2
 clip=app.gag_movie(event);assert 'Actor-victory' not in str(clip)
 clip.start();clip.finish();app.clear_movie_props()
 print('Four piano timing, flatten reaction, miss tease, lured miss and cleanup passed.')
finally:app.destroy()
