import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from panda3d.core import loadPrcFileData
loadPrcFileData('','audio-library-name null')
from panda_battle import PandaBattle
from battle_engine import Action
app=PandaBattle(offscreen=True,timed=False,seed=1)
try:
 app.selected={i:Action(i) for i in range(3)};app.resolve_if_ready();assert not app.animating
 app.selected[3]=Action(3)
 app.toggle_auto_resolve();app.resolve_if_ready();assert not app.animating
 app.toggle_auto_resolve();app.modal='rewards';app.resolve_if_ready();assert not app.animating
 app.modal=None;app.choice='Whole Cream Pie';app.resolve_if_ready();assert not app.animating
 app.choice=None;app.resolve_if_ready();assert app.animating
 clip=app.animation;app.resolve_if_ready();assert app.animation is clip
 app.new_battle();app.game.toons[3].escaped=True
 app.selected={i:Action(i) for i in range(3)};app.resolve_if_ready();assert app.animating
 app.new_battle();app.selected={i:Action(i,'Damage remote 1★',0) for i in range(4)}
 app.resolve_if_ready();assert not app.animating
 print('Auto resolve waits for committed living-Toon choices, honors toggle/modals, rejects duplicate remotes, and starts once.')
finally:app.destroy()
