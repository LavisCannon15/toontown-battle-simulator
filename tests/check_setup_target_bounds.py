"""Fresh setup removes battle buffs; target GUI uses its rendered hit area."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from panda3d.core import loadPrcFileData,Point3
loadPrcFileData('','audio-library-name null')
from panda_battle import PandaBattle
from ui_hit_test import contains
app=PandaBattle(offscreen=True,timed=False,seed=1)
try:
 app.game.toons[0].accuracy_up=5;app.game.toons[0].unite_cooldown=2
 app.open_setup();app.apply_setup()
 assert app.modal is None
 assert app.game.toons[0].accuracy_up==app.game.toons[0].unite_cooldown==0
 app.new_battle();assert app.game.toons[0].accuracy_up==0
 app.choose_action('Cupcake');panel=app.target_panel
 for scale,pos in [(1,(0,0,0)),(.8,(.1,0,-.1)),(1.2,(-.2,0,.15))]:
  panel.setScale(scale);panel.setPos(*pos)
  left,right,bottom,top=panel.getBounds()
  for point,want in [(Point3((left+right)/2,0,(bottom+top)/2),True),(Point3(left-.05,0,top+.05),False)]:
   world=app.ui.getRelativePoint(panel,point)
   assert contains(panel,app.ui,world)==want,(scale,pos,point)
 panel.hide();assert not contains(panel,app.ui,Point3(0,0,0))
 app.cancel_choice()
 print('Setup clears temporary buffs; target panel hit area follows position, scale and visibility.',flush=True)
finally:app.destroy()
