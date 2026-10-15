"""Classic TownBattleSOSPanel frame and NPCFriendCard resources.
The shared category navigation extends the classic panel for TTR rewards.
"""
import json
from pathlib import Path
from game_resources import resource
from scene_art import configure_head,color_head
from direct.gui.DirectGui import DirectFrame,DirectButton,DirectOptionMenu,DirectScrolledFrame,DGG
from panda3d.core import TextNode,TransparencyAttrib
from support import CATEGORIES,SOS,SOS_STARS,REMOTES,DOODLES,describe
from battle_engine import GAGS,Action,COG_CATALOG

class RewardsUI:
 def open_fire(self):
  if self.animating or self.game.result or not self.game.toons[self.active].alive or self.auto_modes[self.active]:return
  self.close_modal();self.modal='fire';self.gag_grid.hide();self.set_briefcase_open(True)
  gui=self.gui_models['battle_gui']
  self.overlay=DirectFrame(parent=self.ui,relief=None,image=gui.find('**/BtlPick_TAB'),image_color=(1,.2,.2,1),scale=1.3,pos=(-.75,0,-.42))
  DirectFrame(parent=self.overlay,relief=None,image=gui.find('**/ToonBtl_Status_BG'),image_color=(.5,.9,.5,1),pos=(.611,0,0))
  count=self.game.toons[self.active].rewards.get('Fire',0)
  DirectFrame(parent=self.overlay,relief=None,image=gui.find('**/PckMn_Select_Tab'),image_color=(1,1,0,1),image_scale=(1,1,2),pos=(-.013,0,.013))
  self.label(self.overlay,f'Fire a Cog!\n{count} pink slips',-.013,.032,.035,(0,0,.4,1),TextNode.ACenter)
  self.label(self.overlay,f'{self.game.toons[self.active].name}\n{self.game.toons[self.active].hp}/{self.game.toons[self.active].maximum}',.611,.025,.028,(0,0,.3,1),TextNode.ACenter)
  self.fire_buttons={};targets=[(i,c) for i,c in enumerate(self.game.cogs) if c.alive]
  for slot,(index,cog) in enumerate(targets):
   nodes=[gui.find('**/'+n) for n in ('PckMn_Arrow_Up','PckMn_Arrow_Dn','PckMn_Arrow_Rlvr')]
   btn=DirectButton(parent=self.overlay,relief=None,image=nodes,pos=(.4*(slot-(len(targets)-1)/2),0,.2),text=f'{"Skelecog" if cog.skelecog else cog.name}',text_scale=.024,text_pos=(0,.075),text_fg=(1,1,1,1),command=self.fire_target,extraArgs=[index],state=DGG.NORMAL if count else DGG.DISABLED)
   self.fire_buttons[index]=btn
  DirectButton(parent=self.overlay,relief=None,image=tuple(gui.find('**/'+n) for n in ('PckMn_BackBtn','PckMn_BackBtn_Dn','PckMn_BackBtn_Rlvr')),pos=(-.647,0,.006),scale=1.05,text='Back',text_scale=.05,text_pos=(.01,-.012),text_fg=(0,0,.8,1),command=self.close_modal)
  self.modal_clock=self.label(self.overlay,'',.61,-.09,.025,(0,0,.4,1),TextNode.ACenter)
 def open_sos(self,page=0,filter_track='All'):
  return self.open_rewards('SOS cards',page,filter_track)
 def fire_target(self,index):
  action=Action(self.active,'Fire',index)
  try:self.game.validate(action)
  except ValueError as error:self.close_modal();self.notice(str(error));return
  self.close_modal();self.commit(action);self.make_hud()
 def reward_portrait(self,parent,name):
  root=Path(__file__).resolve().parent
  if not hasattr(self,'sos_portraits'):self.sos_portraits=json.loads((root/'assets/sos_portraits.json').read_text())
  info=self.sos_portraits.get(name)
  if not info:return False
  holder=parent.attachNewNode('npc-portrait');holder.setDepthTest(True);holder.setDepthWrite(True);head=self.loader.loadModel(str(resource(info['model'])));head.reparentTo(holder)
  variant='long' if info['dna'][1]=='l' else 'short'
  animal={'d':'dog','c':'cat','r':'rabbit','m':'mouse','p':'pig','b':'bear','h':'horse','f':'duck'}.get(info['dna'][0],'dog')
  color_head(head,info['color'],animal)
  configure_head(head,variant)
  for mesh in head.findAllMatches('**/+GeomNode'):
   if mesh.getName().lower().endswith(('low','medium')):mesh.hide()
  head.setH(180);head.setLightOff();lo,hi=head.getTightBounds();size=max(hi.x-lo.x,hi.z-lo.z);head.setPos(-(lo.x+hi.x)/2,0,-(lo.z+hi.z)/2)
  holder.setScale(.22/size);holder.setPos(0,-.05,.005);return True
 def reward_available(self,name):
  try:
   targets=self.game.targets(self.active,name)
   if targets:
    for i,_ in targets:
     try:self.game.validate(Action(self.active,name,i));return True
     except ValueError:pass
    return False
   self.game.validate(Action(self.active,name));return True
  except ValueError:return False
 def open_rewards(self,category='SOS cards',page=0,filter_track='All'):
  if category=='Fire':return self.open_fire()
  if self.animating or self.game.result or not self.game.toons[self.active].alive or self.auto_modes[self.active]:return
  self.close_modal();self.modal='rewards';self.gag_grid.hide();self.set_briefcase_open(True)
  self.overlay=DirectFrame(parent=self.content,frameColor=(0,0,0,0),pos=(-.765,0,-.37),scale=.54)
  self.art_node('ttr_battle','ttr_t_gui_bat_rewardsMenu_base_noRed_card',self.overlay,0,0,3.36,1.70)
  self.art_node('ttr_battle','ttr_t_gui_bat_rewardsMenu_panel_base_card',self.overlay,.25,0,2.75,1.65)
  self.art_node('ttr_battle','ttr_t_gui_bat_rewardsMenu_'+{'SOS cards':'SOSPanel','Remotes':'remotePanel','Doodle':'doodlePanel'}[category]+'_indent_card',self.overlay,.25,0,2.60,1.51)
  self.reward_category=category;self.reward_page=0;self.reward_filter=filter_track;self.reward_buttons={}
  for i,tab in enumerate(('SOS cards','Fire','Remotes','Doodle')):
   button=DirectButton(parent=self.overlay,relief=None,frameSize=(-.22,.22,-.19,.19),pos=(-1.40,0,.56-i*.38),command=self.open_rewards,extraArgs=[tab])
   self.art_node('ttr_battle','ttr_t_gui_bat_rewardsMenu_tabButton_'+('down' if tab==category else 'up')+'_card',button,0,0,.43,.37)
   icon={'SOS cards':'sos_cardFront','Fire':'fire','Remotes':'remote_body','Doodle':'doodle'}[tab]
   self.art_node('ttr_battle','ttr_t_gui_bat_rewardsGUI_icon_'+icon+'_card',button,0,0,.24,.27)
   if tab=='Fire':self.label(button,str(self.game.toons[self.active].rewards.get('Fire',0)),.12,-.14,.09,(1,1,1,1),TextNode.ACenter)
  if category=='SOS cards':self.draw_sos_cards(filter_track)
  elif category=='Remotes':self.draw_remote_choices()
  else:self.draw_doodle_choices()
 def bind_reward(self,button,name):
  if not self.reward_available(name):button['state']=DGG.DISABLED
  button.bind(DGG.ENTER,self.reward_hover,[name]);button.bind(DGG.EXIT,self.reward_hover,[''])
  self.reward_buttons[name]=button
 def draw_sos_cards(self,filter_track):
  filters=['All']+list(dict.fromkeys(v[0] for v in SOS.values()))
  if filter_track not in filters:filter_track='All'
  self.reward_filter_menu=DirectOptionMenu(parent=self.overlay,items=filters,initialitem=filters.index(filter_track),scale=.047,pos=(.81,0,.63),command=lambda value:self.open_rewards('SOS cards',filter_track=value))
  names=[n for n in SOS if filter_track=='All' or SOS[n][0]==filter_track]
  rows=(len(names)+3)//4
  self.reward_scroll=DirectScrolledFrame(parent=self.overlay,frameSize=(-1.02,1.47,-.70,.49),canvasSize=(-1.02,1.40,-max(1.18,rows*.59),0),pos=(0,0,0),frameColor=(0,0,0,0),scrollBarWidth=.045,autoHideScrollBars=True)
  self.reward_scroll.verticalScroll['thumb_frameColor']=(1,.86,.05,1)
  self.reward_scroll.verticalScroll['value']=getattr(self,'reward_scroll_values',{}).get(filter_track,0)
  for i,name in enumerate(names):
   x=-.73+(i%4)*.60;z=-.29-(i//4)*.59
   card=DirectFrame(parent=self.reward_scroll.getCanvas(),relief=None,frameColor=(1,1,1,1),frameSize=(-.28,.28,-.28,.28),pos=(x,0,z))
   # Native NPC card front, with its own call control rather than remote artwork.
   self.art_node('playingCard','card_front',card,0,0,.56,.56)
   kind=SOS[name][0]
   self.label(card,kind.upper(),0,.215,.050,(.13,.25,.4,1),TextNode.ACenter,text_font=self.minnie_font,text_wordwrap=10.5)
   self.label(card,name[5:],0,.16,.050,(.12,.17,.27,1),TextNode.ACenter,text_font=self.font,text_wordwrap=10.5)
   self.reward_portrait(card,name)
   available=self.reward_available(name);count=self.game.toons[self.active].rewards.get(name,0)
   self.label(card,f'{count} Remaining' if available else 'Unavailable',0,-.145,.045,(.12,.17,.27,1),TextNode.ACenter,text_font=self.font,text_wordwrap=10.5)
   button=DirectButton(parent=card,text='CALL',text_scale=.032,text_pos=(0,-.01),geom=tuple(self.gui_models['inventory_gui'].find('**/'+n) for n in ('InventoryButtonUp','InventoryButtonDown','InventoryButtonRollover','InventoryButtonFlat')),geom_scale=(.9,1,.60),geom_color=(1,.3,.3,1),frameColor=(0,0,0,0),frameSize=(-.08,.08,-.035,.035),pos=(-.17,0,-.22),relief=None,command=self.select_reward,extraArgs=[name])
   self.bind_reward(button,name)
   for star in range(SOS_STARS[name]):self.art_node('name_star','name_star',card,-.03+star*.048,-.22,.04).setColorScale(.5,.25,.25,1)
 def draw_remote_choices(self):
  for row,kind in enumerate(('Damage','Healing')):
   self.art_node('ttr_battle','ttr_t_gui_bat_rewardsMenu_remotePanel_'+kind.lower()+'Remote_title_card',self.overlay,-.34,.43-row*.61,1.30,.13)
   for col,name in enumerate(n for n in REMOTES if REMOTES[n][0]==kind):
    button=DirectButton(parent=self.overlay,relief=None,geom=self.ui_states('ttr_battle','ttr_t_gui_bat_rewardsMenu_remotePanel_button_',.36,.45),geom_color=(.1,.68,1,1),frameSize=(-.18,.18,-.225,.225),pos=(-.72+col*.46,0,.12-row*.61),command=self.select_reward,extraArgs=[name])
    stars=REMOTES[name][1]-1
    self.art_node('ttr_battle',f'ttr_t_gui_bat_rewardsGUI_icon_remote{kind}_level{stars}_card',button,0,.015,.24,.29)
    for star in range(stars):self.art_node('name_star','name_star',button,(star-(stars-1)/2)*.064,.177,.06).setColorScale(1,.8,.08,1)
    self.label(button,str(self.game.toons[self.active].rewards.get(name,0)),.115,-.175,.07,(1,1,1,1),TextNode.ACenter)
    if not self.reward_available(name):button.setColorScale(.45,.45,.45,1)
    self.bind_reward(button,name)
 def draw_doodle_choices(self):
  from pet_movies import create_doodle
  holder,pet=create_doodle(self);self.movie_props.remove((holder,pet));self.reward_pet=pet
  holder.reparentTo(self.overlay);holder.setPos(-.57,-.1,-.50);holder.setH(180);holder.setScale(.58);holder.setLightOff();holder.show();pet.loop('neutral')
  colors=[(.7,.43,.83,1),(.66,.7,.32,1),(.4,.7,.34,1),(.48,.46,.75,1),(.8,.53,.34,1),(.8,.4,.7,1),(.3,.7,.73,1)]
  for i,name in enumerate(DOODLES):
   button=DirectButton(parent=self.overlay,relief=None,frameSize=(-.46,.46,-.08,.08),pos=(.61,0,.46-i*.17),command=self.select_reward,extraArgs=[name])
   self.art_node('ttr_battle','ttr_t_gui_bat_rewardsMenu_doodlePanel_trickStrip_base_card',button,0,0,.90,.16).setColorScale(*colors[i])
   trick={'Play Dead':'playDead','Rollover':'rollover','Backflip':'backflip'}.get(name[8:],name[8:].lower())
   self.art_node('ttr_battle','ttr_t_gui_bat_rewardsMenu_doodlePanel_trickIcon_'+trick+'_card',button,-.34,0,.12,.12)
   self.label(button,name[8:]+'!',.09,-.018,.065,(1,1,1,1),TextNode.ACenter)
   self.bind_reward(button,name)
 def reward_hover(self,name,event=None):
  if not name:self.notes_idle();return
  self.notes_cover.hide();self.notes_button.hide()
  self.detail_text.setPos(-.157,0,-.055);self.detail_text.setScale(1)
  self.detail_title['text']=name.replace('SOS: ','').replace('Doodle: ','')
  self.detail_text['text_align']=TextNode.ALeft
  self.detail_text['text']=describe(self.game,self.active,name)
  self.fit_detail_text()
