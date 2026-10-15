import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from panda3d.core import loadPrcFileData
loadPrcFileData('','audio-library-name null')
from panda_battle import PandaBattle
from battle_engine import Action
app=PandaBattle(offscreen=True,timed=False,seed=1)
def finish():
 for _ in range(120):
  for c in getattr(app,'live_departures',[]):
   if c.isPlaying():c.finish()
  if app.animation:app.animation.finish()
  app.taskMgr.step()
  if not app.animating:return
 raise AssertionError('Stalled')
def shot(name):
 app.position_nametags()
 for _ in range(3):app.graphicsEngine.renderFrame()
 app.win.saveScreenshot(str(Path('reports',name+'.png').resolve()))
try:
 for name in ('RUN','PASS'):assert app.reward_shortcuts[name]['geom'] is not None
 shot('fixed-run-pass')
 selected=app.selected.copy();app.open_rewards();assert not app.hud.isHidden() and app.content.isHidden()
 shot('in-place-rewards');app.close_modal();assert not app.content.isHidden() and app.selected==selected
 # Lure misses must not launch Cog dodge intervals.
 event={'kind':'gags','track':'Lure','health':[],'misses':[0,1]}
 clip=app.health_movie(event,2);assert clip.getDuration()==0
 clip=app.hand_prop(3,'golf-club',3,cog=True);clip.start();clip.pause();clip.setT(1)
 prop=app.render.find('**/battle-prop-golf-club');assert prop.getParent().getName()=='joint_Lhold'
 assert abs(prop.getH()-63.097)<.01
 clip.finish();app.clear_movie_props()
 cap=app.attack_caption(0,'Tee Off',3);cap.start();cap.pause();cap.setT(1)
 node=app.ui.find('**/cog-attack-name');assert not node.isEmpty() and node.getX()==0 and node.getZ()>.7
 cap.finish();app.clear_movie_props()
 app.animating=True;app.make_hud()
 clip=app.cog_movie({'kind':'cog','cog':3,'name':'Tee Off','targets':[0],'health':[],'misses':[]})
 clip.start();clip.pause();clip.setT(3);shot('tee-off-grip');clip.finish();app.clear_movie_props();app.animating=False;app.make_hud()
 # Each departure preserves round and surviving choices; final departure ends combat.
 app.selected[1]=Action(1,'Cupcake',0);round_before=app.game.round
 for i in range(4):
  app.select_toon(i);app.run_away();finish()
  assert app.game.round==round_before
  assert app.team_card_roots[i].isHidden()
  if i==0:assert app.selected[1].gag=='Cupcake'
 assert 'Cogs win' in app.game.result
 assert all(a.getCurrentAnim()=='victory' for a in app.cog_actors)
 assert app.hud.find('**/ttr_t_gui_bat_battleMenu_base_card-art').isEmpty()
 app.resolve();assert app.game.round==round_before
 shot('all-toons-ran-cogs-win')
 # Receiver reaction uses the extracted seizure/control animation.
 app.new_battle();app.selected={0:Action(0,'Healing remote 1★',0)};app.resolve()
 app.animation.pause();app.animation.setT(.8+app.cog_actors[0].getDuration('seizecontrol')*.5)
 assert app.cog_actors[0].getCurrentFrame('seizecontrol')>0
 shot('remote-receiver-control');finish()
 for toon in app.game.toons:toon.hp=0
 app.finish_round()
 assert 'Cogs win' in app.game.result and all(n.isHidden() for n in app.team_card_roots)
 assert all(a.getCurrentAnim()=='victory' for a in app.cog_actors)
 print('Run/no-round, disappearing cards, Cog victory, Lure miss, golf-club grip, caption, rewards overlay, and remote receiver checks passed.')
finally:app.destroy()
