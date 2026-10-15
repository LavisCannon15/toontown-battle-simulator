import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from panda3d.core import loadPrcFileData
loadPrcFileData('','audio-library-name null')
from panda_battle import PandaBattle
from battle_engine import Action
app=PandaBattle(offscreen=True,timed=False,seed=1)
try:
 app.auto_modes=[False]*4
 app.selected[0]=Action(0,'Cupcake',1)
 app.choose_action('Cupcake')
 assert app.choice=='Cupcake'
 app.preview_action_target(0)
 assert app.target_mark_labels[0]['text']=='X---'
 assert app.selected[0].target==1
 assert app.game.cogs[0].name in app.tooltip['text']
 for _ in range(3):app.graphicsEngine.renderFrame()
 app.win.saveScreenshot('reports/target-preview.png')
 app.preview_action_target(None)
 assert app.target_mark_labels[0]['text']=='-X--'
 app.cancel_choice()
 assert app.choice is None and app.selected[0].target==1
 app.choose_action('Cupcake');app.choose_target(2)
 assert app.selected[0].target==2 and app.choice is None
 assert app.active==1  # Confirmation advanced to the next manual Toon.
 app.select_toon(0)
 app.choose_action('Feather');app.preview_action_target(1)
 assert app.target_mark_labels[0]['text']=='-X--'
 app.preview_action_target(0)
 assert app.preview_target is None
 print('Target previews, committed-choice preservation, cancel, confirm and Toon-Up eligibility passed.',flush=True)
finally:app.destroy()
