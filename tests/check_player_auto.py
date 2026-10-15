import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from panda3d.core import loadPrcFileData
loadPrcFileData('','audio-library-name null')
from panda_battle import PandaBattle
app=PandaBattle(offscreen=True,timed=False,seed=1)
try:
 assert not app.auto_modes[0]
 app.toggle_auto(0);assert app.auto_modes[0]
 app.auto_due[0]=0;app.update_auto()
 assert 0 in app.selected
 app.game.validate(app.selected[0])
 first=app.selected[0];app.update_auto();assert app.selected[0]==first
 app.toggle_auto(0);assert not app.auto_modes[0] and 0 not in app.selected
 app.choose_action('Whole Cream Pie');app.choose_target(0)
 assert app.selected[0].gag=='Whole Cream Pie'
 app.toggle_auto(0);app.new_battle()
 assert app.auto_modes[0] and 0 not in app.selected
 app.auto_due[0]=0;app.update_auto();assert 0 in app.selected
 app.game.validate(app.selected[0])
 print('Player Auto chooses a valid action, returns to Manual, and persists into a new battle.')
finally:app.destroy()
