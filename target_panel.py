"""Extracted battle_gui target picker; reference TownBattleChooseAvatarPanel."""
from direct.gui.DirectGui import DirectFrame,DirectButton,DGG
from panda3d.core import TransparencyAttrib
from battle_engine import GAGS

def build(app,targets):
 app.content.hide();app.gag_base.hide()
 gui=app.gui_models['battle_gui']
 toon=app.choice in GAGS and GAGS[app.choice].track=='Toon-Up'
 panel=DirectFrame(parent=app.hud,relief=None,image=gui.find('**/BtlPick_TAB'),image_color=(1,.2,.2,1),pos=(0,0,0),scale=1.0)
 app.target_panel=panel;app.target_buttons={}
 panel.setTransparency(TransparencyAttrib.MAlpha)
 DirectFrame(parent=panel,relief=None,image=gui.find('**/PckMn_Select_Tab'),image_color=(1,1,0,1),text='WHICH TOON?' if toon else 'WHICH COG?',text_font=app.font,text_fg=(0,0,0,1),text_pos=(0,-.025),text_scale=.08,pos=(-.013,0,.013))
 DirectButton(parent=panel,relief=None,image=tuple(gui.find('**/'+n) for n in ('PckMn_BackBtn','PckMn_BackBtn_Dn','PckMn_BackBtn_Rlvr')),pos=(-.647,0,.006),scale=1.05,text='BACK',text_font=app.font,text_scale=.05,text_pos=(.01,-.012),text_fg=(0,0,.8,1),command=app.cancel_choice)
 team=app.game.toons if toon else app.game.cogs
 slots=[i for i,t in enumerate(team) if t.alive]
 # This simulator's formation indices run left to right, opposite classic slots.
 for index,target in targets:
  k=slots.index(index);x=(k-(len(slots)-1)/2)*.4
  btn=DirectButton(parent=panel,relief=None,image=tuple(gui.find('**/'+n) for n in ('PckMn_Arrow_Up','PckMn_Arrow_Dn','PckMn_Arrow_Rlvr')),pos=(x,0,-.2 if toon else .2),scale=(1,1,-1 if toon else 1),command=app.choose_target,extraArgs=[index],pressEffect=False)
  btn.bind(DGG.ENTER,app.target_enter,[index]);btn.bind(DGG.EXIT,app.target_exit)
  app.target_buttons[index]=btn
 app.art_node('battle_gui','ToonBtl_Status_IconSEL',panel,.611,0,.17,.17).setColorScale(1,.4,.8,1)
 if app.choice in app.icons:
  icon=DirectFrame(parent=panel,relief=None,image=app.icons[app.choice],image_scale=.055,pos=(.611,0,0));icon.setTransparency(TransparencyAttrib.MAlpha)
