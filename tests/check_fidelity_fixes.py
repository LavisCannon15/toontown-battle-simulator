import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from panda3d.core import loadPrcFileData
loadPrcFileData('','audio-library-name null')
from panda_battle import PandaBattle
from battle_engine import Action
from battle_movies import MOVIES
app=PandaBattle(seed=1,offscreen=True,timed=False)
try:
 assert set(app.reward_shortcuts)=={'FIRE','PASS','RUN','SOS'}
 assert MOVIES['dodges']['powertrip']=='jump'
 assert MOVIES['dodges']['teeoff']=='duck'
 assert len(MOVIES['attack_props']['hangup'])>=2
 app.selected={0:Action(0,'Fire',0)};app.resolve();app.animation.pause()
 assert not app.cog_nodes[0].find('**/fire-cannon').isEmpty()
 assert app.cog_nodes[0].find('**/cog-breakup').isEmpty(),'Fire must not explode a Cog'
 app.animation.setT(5.2)
 for _ in range(3):app.graphicsEngine.renderFrame()
 app.win.saveScreenshot('/home/laviscannon/Documents/Codex/2026-09-08/can/outputs/fire-cannon.png')
 app.animation.finish();assert app.cog_nodes[0].isHidden()
 app.new_battle();before=[t.hp for t in app.game.toons];before[0]=1;app.game.toons[0].hp=0;app.game.toons[1].hp-=5
 app.game.movie_events=[{'kind':'cog','cog':0,'name':'Power Trip','targets':[0],'health':[('toon',0,-1)],'misses':[]},{'kind':'cog','cog':1,'name':next(iter(MOVIES['suits'][app.game.cogs[1].name]['attacks'])),'targets':[1],'health':[('toon',1,-5)],'misses':[]}]
 app.game.health_events=[('toon',0,-1),('toon',1,-5)];app.animating=True;app.display_toon_hp=before;app.display_cog_hp=[c.hp for c in app.game.cogs];app.make_hud();app.animate_round([],app.display_cog_hp,before);app.animation.pause()
 first=app.animation[0].getDuration();app.animation.setT(first+.01)
 assert app.toon_nodes[0].isHidden(),'Sad Toon must leave before the next attack'
 assert app.display_toon_hp[1]==before[1],'Next attack damage must not be shown early'
 app.animation.finish();app.new_battle();hp=app.game.toons[0].hp;round_number=app.game.round
 app.run_away();app.animation.finish()
 assert app.game.toons[0].escaped and app.game.toons[0].hp==hp and app.game.round==round_number
 assert app.toon_nodes[0].isHidden() and app.active==1
 print('Cannon Fire, source dodge mapping, multiple Cog props, immediate sad exit, screenshot buttons, and Run passed.')
finally:app.destroy()
