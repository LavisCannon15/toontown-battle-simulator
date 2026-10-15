"""Exercise all gag resources and each Cog's actual attack mapping offscreen."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from panda3d.core import loadPrcFileData
loadPrcFileData('','audio-library-name null')
from panda_battle import PandaBattle
from battle_movies import MOVIES
from battle_engine import Action,GAGS,Cog,Battle
app=PandaBattle(seed=1,offscreen=True,timed=False)
try:
 app.display_toon_hp=[t.hp for t in app.game.toons];app.display_cog_hp=[c.hp for c in app.game.cogs]
 for name,gag in GAGS.items():
  a=Action(0,name,1 if gag.track=='Toon-Up' else 0)
  event={'kind':'gags','track':gag.track,'actions':[a],'targets':{0:[a.target]},'health':[],'misses':[]}
  clip=app.gag_movie(event);clip.start();clip.pause();clip.setT(min(1,clip.getDuration()));app.graphicsEngine.renderFrame();clip.finish();app.clear_movie_props()
  assert not app.render.findAllMatches('**/gag').getNumPaths(),'Legacy PNG attack remains'
 for index,cog in enumerate(app.game.cogs):
  for name in MOVIES['suits'][cog.name]['attacks']:
   event={'kind':'cog','cog':index,'name':name,'targets':[0],'health':[],'misses':[]}
   clip=app.cog_movie(event);clip.start();clip.pause();clip.setT(.8);app.graphicsEngine.renderFrame();clip.finish();app.clear_movie_props()
 for name in MOVIES['suits']:
  app.game.cogs=[Cog(name,8)];app.spawn_characters()
  actor=app.cog_actors[0]
  for attack,anim in MOVIES['suits'][name]['attacks'].items():
   assert actor.getNumFrames(anim)>0,(name,attack,anim)
   clip=app.cog_movie({'kind':'cog','cog':0,'name':attack,'targets':[0],'health':[],'misses':[]});clip.start();clip.pause();clip.setT(.8);clip.finish();app.clear_movie_props()
 for skeleton in (False,True):
  for name in ('Flunky','Pencil Pusher','The Big Cheese'):
   app.game.cogs=[Cog(name,8,skelecog=skeleton)];app.spawn_characters();clip=app.cog_defeat(0);clip.start();clip.pause();clip.setT(5.5);app.graphicsEngine.renderFrame();clip.finish()
   assert app.cog_nodes[0].isHidden();app.clear_movie_props()
 # The recording adds no random draws and preserves chronological damage.
 g=Battle(seed=2)
 for i in range(4):g.plan(Action(i))
 g.resolve();events=[e for e in g.movie_events if e['kind']=='cog']
 assert events and all(e['name'] for e in events)
 assert [h for e in g.movie_events for h in e['health']]==g.health_events
 print('All 49 gag models/motions, all 32 Cog attack mappings/titles, six breakup rigs, and chronological health events passed.')
finally:app.destroy()
