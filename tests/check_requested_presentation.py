"""Regression checks for resource panel, target slots and action choreography."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from panda_battle import PandaBattle
from battle_engine import Action
from panda3d.core import Vec3
app=PandaBattle(offscreen=True,timed=False)
try:
 assert app.target_marks(Action(0,'Cupcake',0))=='X---'
 assert app.target_marks(Action(0,'Cupcake',3))=='---X'
 assert app.target_marks(Action(0,'Bike Horn'))=='XXXX'
 assert app.target_marks(Action(0,'Feather',1))=='-X--'
 assert app.target_marks(Action(0,'Megaphone'))=='-XXX'
 assert app.target_marks(Action(0,'Pass'))==''
 app.game.cogs[1].hp=0
 assert app.target_marks(Action(0,'Cupcake',0))=='X--'
 app.game.cogs[1].hp=app.game.cogs[1].maximum
 app.display_toon_hp=[t.hp for t in app.game.toons];app.display_cog_hp=[c.hp for c in app.game.cogs]
 event={'kind':'gags','track':'Toon-Up','actions':[Action(0,'Feather',1)],'targets':{0:[1]},'health':[],'misses':[]}
 origin=Vec3(app.toon_nodes[0].getPos());clip=app.gag_movie(event);clip.start();clip.pause();clip.setT(1.1)
 assert app.toon_nodes[0].getPos().length()<.001
 assert app.toon_actors[0]['legs'].getNumFrames('run')>0
 clip.finish();assert (app.toon_nodes[0].getPos()-origin).length()<.001
 app.clear_movie_props()
 fire=app.fire_movie(Action(0,'Fire',0),{'health':[],'misses':[]})
 assert app.cog_nodes[0].find('**/fire-cannon').getH()==180
 fire.start();fire.pause();fire.setT(5.5);app.graphicsEngine.renderFrame();fire.finish();app.clear_movie_props()
 app.commit(Action(0,'Pass'));before=dict(app.selected);round_before=app.game.round
 app.use_unite('Unite: Toon-Up 20')
 assert app.selected==before and app.game.round==round_before
 assert app.unite_intervals and not app.render.find('**/unite-effect').isEmpty()
 app.unite_intervals[-1].finish();assert app.render.find('**/unite-effect').isEmpty()
 assert {'PASS','RUN','REWARDS'}<=app.reward_shortcuts.keys()
 print('Target markers, modern controls, Toon-Up travel, cannon heading and separate Unite effects passed.')
finally:app.destroy()
