"""Offscreen integration for reward navigation and original ending animations."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from panda3d.core import loadPrcFileData
loadPrcFileData('','audio-library-name null')
from panda_battle import PandaBattle
from battle_engine import Action
from support import CATEGORIES
app=PandaBattle(seed=1,offscreen=True,timed=False)
try:
 initial=app.game.toons[0].rewards.copy();app.selected[0]=Action(0,'Cupcake',0)
 for category in CATEGORIES:
  app.open_rewards(category)
  assert app.modal==('fire' if category=='Fire' else 'rewards')
  if category!='Fire':
   assert app.reward_buttons
   for name in app.reward_buttons:app.reward_hover(name)
 app.open_rewards('SOS cards',3);assert len(app.reward_buttons)==8
 app.open_rewards('SOS cards',0,'Lure');assert len(app.reward_buttons)==3
 app.close_modal();assert app.selected[0].gag=='Cupcake' and app.game.toons[0].rewards==initial
 app.open_rewards('Fire');assert set(app.fire_buttons)=={0,1,2,3}
 app.close_modal();assert app.selected[0].gag=='Cupcake'
 app.open_fire();app.fire_target(1);assert app.selected[0]==Action(0,'Fire',1) and app.modal is None
 assert app.game.toons[0].rewards==initial
 for actors in app.toon_actors:
  for part,actor in actors.items():
   assert actor.getNumFrames('victory')>1 and actor.getNumFrames('lose')>1,(part,actor.getAnimNames())
 before=[t.hp for t in app.game.toons];app.game.toons[0].hp=0;app.animating=True
 app.animate_round([], [c.hp for c in app.game.cogs],before)
 app.animation.pause();app.animation.setT(app.animation.getDuration()-.1)
 assert app.toon_nodes[0].isHidden()
 app.animation.finish();assert app.active==1 and not app.animating
 for cog in app.game.cogs:cog.hp=0
 app.finish_round()
 assert all(node.isHidden() for node in app.cog_nodes)
 for actors,toon in zip(app.toon_actors,app.game.toons):
  if toon.alive:assert all(a.getCurrentAnim()=='victory' for a in actors.values())
 app.new_battle();assert all(not n.isHidden() and n.getSx()==1 for n in app.toon_nodes)
 print('Rewards navigation, filters, selection/cancel, original victory/lose clips, sad exit, active Toon handover, and reset passed.')
finally:app.destroy()
