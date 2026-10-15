"""Panda checks for per-trick setup, any-caster Unites and seven real Doodle movies."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from panda3d.core import loadPrcFileData
loadPrcFileData('','audio-library-name null')
from panda_battle import PandaBattle
from battle_engine import Action
from pet_movies import doodle_movie,TRICKS
app=PandaBattle(offscreen=True,timed=False,seed=1)
try:
 app.open_setup();app.setup_switch(0);app.setup_inventory('doodle')
 app.setup_entries[3][0].enterText('5000')
 app.flush_setup()
 assert '5000' in app.setup_draft['toons'][0].doodle_skills.values()
 app.apply_setup();assert app.modal is None
 assert 5000 in app.game.toons[0].doodle_skills.values()
 app.animating=True;app.display_toon_hp=[t.hp for t in app.game.toons];app.display_cog_hp=[c.hp for c in app.game.cogs];app.make_hud()
 app.open_unites(1);assert app.unite_caster==1
 app.game.toons[0].hp=50;app.game.toons[1].hp=50
 app.use_unite('Unite: Toon-Up 20')
 assert app.game.toons[1].unite_cooldown==3 and app.game.toons[0].unite_cooldown==0
 for name in TRICKS:
  event={'kind':'support','health':[],'misses':[],'doodle_success':True}
  clip=doodle_movie(app,Action(0,'Doodle: '+name),event)
  clip.start();clip.pause()
  node=app.render.find('**/battle-doodle')
  clip.setT(node.getPythonTag('trick_start')+1.5)
  for _ in range(3):app.position_nametags();app.graphicsEngine.renderFrame()
  if name=='Beg':app.win.saveScreenshot(str(Path('reports/doodle-beg.png').resolve()))
  assert not app.render.find('**/battle-doodle').isEmpty()
  clip.finish();app.clear_movie_props();assert app.render.find('**/battle-doodle').isEmpty()
 clip=doodle_movie(app,Action(0,'Doodle: Jump'),{'kind':'support','health':[],'misses':[],'doodle_success':False})
 clip.start();clip.pause();clip.setT(4);clip.finish();app.clear_movie_props()
 from support import REMOTES
 app.game.cogs[0].remote=REMOTES['Healing remote 1★'];app.sync_remote_visuals()
 assert not app.cog_actors[0].find('**/remote-antenna').isEmpty()
 clip=app.remote_movie({'kind':'remote','cog':0,'remote_kind':'Healing','remote_before':app.game.cogs[0].remote,'health':[],'misses':[]})
 clip.start();clip.pause();clip.setT(1.5)
 antenna=app.remote_visuals[0][1]
 assert antenna.getTightBounds(app.render)[1].z>4
 for _ in range(3):app.position_nametags();app.graphicsEngine.renderFrame()
 app.win.saveScreenshot(str(Path('reports/remote-antenna.png').resolve()))
 clip.finish();app.clear_movie_props();app.game.cogs[0].remote=None;app.sync_remote_visuals()
 assert app.cog_actors[0].find('**/remote-antenna').isEmpty()
 print('Reward UI and real Doodle movies passed: seven tricks, failure, setup skill points, alternate Unite caster.')
finally:app.destroy()
