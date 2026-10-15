import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from panda3d.core import loadPrcFileData
from direct.gui.DirectGui import DGG
loadPrcFileData('','audio-library-name null')
from panda_battle import PandaBattle
from battle_engine import Action
app=PandaBattle(offscreen=True,timed=False,seed=1)
try:
 for category,count in [('SOS cards',32),('Remotes',6),('Doodle',7)]:
  app.open_rewards(category)
  assert app.gag_grid.isHidden() and not app.content.isHidden()
  assert not app.reward_shortcuts['PASS'].isHidden()
  assert len(app.reward_buttons)==count
  if category=='Doodle':assert app.reward_pet is not None
  app.toggle_rewards();assert app.modal is None and not app.gag_grid.isHidden()
  assert getattr(app,'reward_pet',None) is None
 for c in app.game.cogs:c.lure=2
 app.open_rewards();assert app.reward_buttons['SOS: Lil Oldman']['state']==DGG.DISABLED
 app.select_reward('SOS: Lil Oldman');assert not app.selected and app.modal=='rewards'
 app.choose_action('Pass');assert app.modal is None and app.selected[0].gag=='Pass'
 assert app.target_marks(Action(0,'SOS: Flippy'))=='XXXX'
 app.game.cogs[1].hp=0
 assert app.target_marks(Action(0,'SOS: Julius Wheezer'))=='XXX'
 app.open_rewards('Doodle');app.new_battle();assert app.modal is None and app.reward_pet is None
 app.open_rewards();app.panel_run();assert app.game.toons[0].escaped and app.animating
 app.new_battle();app.open_notes();app.notes_entry.enterText('Save a lure for next round');app.save_notes()
 assert app.battle_notes=='Save a lure for next round' and not app.timer.paused
 app.gag_hover('Birthday Cake');app.gag_leave();assert app.detail_title['text']=='' and not app.notes_cover.isHidden()
 print('Panel shell, 45 reward choices, availability, Pass/Run, cleanup, target marks, notes and hover reset passed.')
finally:app.destroy()
