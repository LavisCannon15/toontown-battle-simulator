import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from panda3d.core import loadPrcFileData
loadPrcFileData('','audio-library-name null')
from panda_battle import PandaBattle
app=PandaBattle(offscreen=True,timed=False,seed=1)
try:
 app.display_toon_hp=[t.hp for t in app.game.toons];app.display_cog_hp=[c.hp for c in app.game.cogs];app.animating=True;app.make_hud()
 for attack in ('Power Trip','Synergy'):
  index=next(i for i,c in enumerate(app.game.cogs) if attack in __import__('battle_movies').MOVIES['suits'][c.name]['attacks'])
  event={'kind':'cog','cog':index,'name':attack,'targets':[0,1],'health':[('toon',0,-10)],'misses':[1]}
  movie=app.cog_movie(event);movie.start();movie.pause();movie.setT(1.75)
  assert len(app.movie_particles)==(2 if attack=='Synergy' else 3)
  for effect in app.movie_particles:effect.accelerate(.3)
  app.position_nametags()
  for _ in range(3):app.graphicsEngine.renderFrame()
  app.win.saveScreenshot(str(Path('reports',attack.lower().replace(' ','-')+'-effects.png').resolve()))
  movie.finish();app.clear_movie_props();assert not app.movie_particles
 print('Power Trip/Synergy source effects, hit/miss playback and cleanup passed.')
finally:app.destroy()
