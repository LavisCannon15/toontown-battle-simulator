"""Resource-backed battle panel and screen-projected character nametags."""
from pathlib import Path
from game_resources import resource
from panda3d.core import TextNode,TransparencyAttrib,Point2,Point3
from direct.gui.DirectGui import DirectFrame,DirectButton,DGG
from battle_engine import GAGS,TRACKS,COG_CATALOG
from laff_face import LaffFace
from scene_art import COLORS as TOON_COLORS
from support import SOS,DOODLES,REMOTES
ROOT=Path(__file__).resolve().parent
INK=(.13,.15,.24,1);CREAM=(1,.98,.86,1)
COLORS=[(.77,.6,.92,1),(.98,.85,.38,1),(.43,.78,.33,1),(.48,.7,.97,1),(.98,.69,.39,1),(.91,.61,.88,1),(.56,.88,.82,1)]

class BattleHUD:
 def load_battle_ui(self):
  self.minnie_font=self.loader.loadFont(str(resource('phase_3/fonts/MinnieFont.ttf')))
  self.minnie_font.setPixelsPerUnit(120)
  self.laff_model=self.loader.loadModel(str(resource('phase_3/models/gui/laff_o_meter.bam')))
  self.suit_font=self.loader.loadFont(str(resource('phase_3/fonts/vtRemingtonPortable.ttf')));self.suit_font.setPixelsPerUnit(100)
  self.gui_models={n:self.loader.loadModel(str(resource('phase_3.5/models/gui/'+n+'.bam'))) for n in ('battle_gui','inventory_gui','clock_gui','frame','name_star','frame4names')}
  self.gui_models['ttr_inventory']=self.loader.loadModel(str(resource('ttr_m_gui_bat_inventoryGUI.bam')))
  self.choice_circle=self.loader.loadTexture(str(resource('ttr_t_gui_bat_toonGUI_gagcircle_back.jpg')),str(resource('ttr_t_gui_bat_toonGUI_gagcircle_back_a.rgb')))
  self.gui_models['gag_icons']=self.loader.loadModel(str(resource('inventory_icons.bam')))
  self.gui_models['status_icons']=self.loader.loadModel(str(resource('ttr_m_gui_bat_statusEffect.bam')))
  self.gui_models['ttr_toon']=self.loader.loadModel(str(resource('ttr_m_gui_bat_toonGUI.bam')))
  self.gui_models['playingCard']=self.loader.loadModel(str(resource('phase_3.5/models/gui/playingCard.bam')))
  self.gui_models['ttr_notes']=self.loader.loadModel(str(resource('ttr_m_gui_bat_shtickyNotes.bam')))
  modern=resource('phase_3.5/models/gui/ttr_m_gui_bat_battleMenu.bam')
  if modern.exists():self.gui_models['ttr_battle']=self.loader.loadModel(str(modern))
 def art_node(self,model,node,parent,x,z,width,height=None):
  source=self.gui_models[model].find('**/'+node)
  if source.isEmpty():raise ValueError('Missing UI resource '+node)
  holder=parent.attachNewNode(node+'-art');copy=source.copyTo(holder);lo,hi=copy.getTightBounds()
  sx=width/(hi.x-lo.x);sz=(height/(hi.z-lo.z)) if height else sx
  copy.setPos(-(lo.x+hi.x)/2,0,-(lo.z+hi.z)/2)
  holder.setScale(sx,1,sz);holder.setPos(x,0,z);holder.setTransparency(TransparencyAttrib.MAlpha)
  return holder
 def ui_states(self,model,prefix,width,height):
  states=[]
  for state in ('up','down','hover','up'):
   source=self.gui_models[model].find('**/'+prefix+state+'_card')
   if source.isEmpty():raise ValueError(prefix+state)
   from panda3d.core import NodePath
   holder=NodePath('button-'+state);copy=source.copyTo(holder);lo,hi=copy.getTightBounds()
   copy.setPos(-(lo.x+hi.x)/2,0,-(lo.z+hi.z)/2);holder.setScale(width/(hi.x-lo.x),1,height/(hi.z-lo.z));holder.flattenLight();states.append(holder)
  return states
 def make_hud(self):
  self.preview_target=None;self.target_button_hover=None
  reopen=self.modal if self.modal in ('rewards','fire') else None
  if reopen:self.close_modal()
  for face in getattr(self,'laff_faces',[]):face.destroy()
  if hasattr(self,'hud'):self.hud.destroy()
  self.hud=DirectFrame(parent=self.ui,frameColor=(0,0,0,0))
  self.panel(self.hud,(-1.78,1.78,.89,1),(.09,.19,.27,.96))
  self.label(self.hud,'Toon Battle Lab',-1.68,.925,.055,CREAM)
  for text,x,cmd,width in [('Setup',-.48,self.open_setup,.25),('New battle',-.12,self.new_battle,.39),('Battle log',.32,self.open_log,.39),('Rules',.69,self.open_rules,.25),('Sound on' if self.sounds_enabled else 'Muted',1.06,self.toggle_sound,.36)]:
   self.button(self.hud,text,x,.947,cmd,width,size=.03)
  self.button(self.hud,'SpeedChat / Unites',-1.30,.80,self.open_unites,.80,(.72,.9,.67,1),size=.031)
  self.button(self.hud,'Auto resolve: ON' if self.auto_resolve else 'Auto resolve: OFF',1.23,.80,self.toggle_auto_resolve,.35,(.48,.86,.51,1) if self.auto_resolve else (.86,.87,.77,1),size=.025)
  self.button(self.hud,'Timed' if self.timed else 'Untimed',1.23,.70,self.toggle_timer,.35,size=.03)
  self.button(self.hud,'Next Toon: ON' if self.auto_advance else 'Next Toon: OFF',1.23,.60,self.toggle_auto_advance,.35,(.48,.86,.51,1) if self.auto_advance else (.86,.87,.77,1),size=.025)
  self.label(self.hud,'U: use separately from your battle choice',-1.69,.732,.023,INK)
  self.scene_bottom=0;self.scene_height=1
  self.scene_center=.565 if self.animating or self.game.result else .725
  self.camNode.getDisplayRegion(0).setDimensions(0,1,0,1);self.resize(self.win)
  if self.animating or self.game.result:
   self.make_team_cards();self.make_nametags()
   if self.game.result:self.label(self.hud,self.game.result,0,.77,.055,CREAM,TextNode.ACenter)
   self.clock_label=self.label(self.hud,'Battle',1.60,-.94,.03,INK,TextNode.ACenter)
   self.tooltip=self.label(self.hud,'',0,-.98,.025,INK,TextNode.ACenter)
   self.position_nametags();return
  # Original illustrated panel, row backings and four-state inventory buttons.
  self.gag_base=self.art_node('ttr_battle','ttr_t_gui_bat_battleMenu_base_card',self.hud,-.49,-.39,2.48,.98)
  self.content=DirectFrame(parent=self.hud,frameColor=(0,0,0,0));self.draw_actions()
  self.make_team_cards();self.make_nametags()
  self.label(self.hud,self.message[:145],1.25,.17,.027,INK,TextNode.ACenter,text_wordwrap=32)
  self.tooltip=self.label(self.hud,'Hover over a gag to see its name and power.',-.49,-.984,.025,CREAM,TextNode.ACenter)
  # The alarm clock occupies the lower right, as in Rewritten's modern layout.
  self.art_node('clock_gui','alarm_clock',self.hud,1.55,-.90,.21)
  self.clock_label=self.label(self.hud,'30',1.55,-.916,.05,INK,TextNode.ACenter)
  self.label(self.hud,'ROUND '+str(self.game.round),1.035,-.84,.027,CREAM,TextNode.ACenter)
  self.button(self.hud,'Resolve round',1.035,-.94,self.resolve,.52,(.48,.86,.51,1),size=.037)
  self.position_nametags()
  if self.choice in GAGS:self.gag_hover(self.choice)
  if self.choice:self.preview_action_target(None)
  if reopen=='rewards':self.open_rewards(getattr(self,'reward_category','SOS cards'),filter_track=getattr(self,'reward_filter','All'))
  elif reopen=='fire':self.open_fire()
  elif self.modal:self.hud.hide()
 def draw_actions(self):
  toon=self.game.toons[self.active]
  self.gag_grid=DirectFrame(parent=self.content,frameColor=(0,0,0,0))
  self.gag_buttons={}
  for row,track in enumerate(TRACKS):
   z=-.017-row*.123
   backing=self.art_node('ttr_inventory','ttr_t_gui_bat_inventoryGUI_gagStrip_base_card',self.gag_grid,-.765,z,1.75,.116);backing.setColorScale(*COLORS[row])
   self.label(self.gag_grid,track.upper(),-1.59,z+.019,.032,INK,sortOrder=30,text_font=self.font)
   for col,(name,gag) in enumerate((n,g) for n,g in GAGS.items() if g.track==track):
    if track==toon.missing_track:continue
    x=-1.15+col*.187
    available=(track!='Toon-Up' or any(t.alive and i!=self.active for i,t in enumerate(self.game.toons))) and toon.stock[name]>0 and track!=toon.missing_track and (track not in ('Lure','Trap') or self.game.lure_available)
    nodes=self.ui_states('ttr_inventory','ttr_t_gui_bat_inventoryGUI_gagButton_base_',.174,.113)
    btn=DirectButton(parent=self.gag_grid,pos=(x,0,z),geom=nodes,geom_color=(0,.6,1,1),relief=None,frameSize=(-.084,.084,-.058,.058),command=self.choose_action,extraArgs=[name],pressEffect=False,state=DGG.NORMAL if available else DGG.DISABLED)
    btn.setTransparency(TransparencyAttrib.MAlpha)
    icon=DirectFrame(parent=btn,image=self.icons[name],image_scale=(.048,1,.048),frameColor=(0,0,0,0),pos=(-.006,0,.006),sortOrder=10);icon.setTransparency(TransparencyAttrib.MAlpha)
    if not available:btn.setColorScale(.45,.45,.45,.7)
    if self.choice==name or (not self.choice and self.selected.get(self.active) and self.selected[self.active].gag==name):btn.setColorScale(.75,1,.5,1)
    self.label(btn,str(toon.stock[name]),.070,-.044,.034,CREAM,TextNode.ARight,text_font=self.font)
    btn.bind(DGG.ENTER,self.gag_hover,[name]);btn.bind(DGG.EXIT,self.gag_leave)
    self.gag_buttons[name]=btn
  self.label(self.gag_grid,f'{toon.name}  •  Pouch {toon.carried}/{toon.pouch}',-.82,-.863,.028,CREAM,TextNode.ACenter)
  # Move the entire gag-info panel: (horizontal, depth, vertical).
  gag_info_pos = (.395, 0, -.210)
  self.gag_info_panel=DirectFrame(parent=self.content,frameColor=(0,0,0,0),pos=gag_info_pos)
  self.art_node('ttr_notes','ttr_t_gui_bat_battleMenu_shtickyNotes_pages_card',self.gag_info_panel,0,0,.43,.46)
  self.art_node('ttr_notes','ttr_t_gui_bat_battleMenu_shtickyNotes_rings_card',self.gag_info_panel,0,.240,.43,.055)
  self.notes_cover=self.art_node('ttr_notes','ttr_t_gui_bat_battleMenu_shtickyNotes_cover_card',self.gag_info_panel,0,0,.43,.46)
  self.notes_button=DirectButton(parent=self.gag_info_panel,relief=None,frameSize=(-.18,.18,.025,.17),command=self.open_notes)
  self.detail_title=self.label(self.gag_info_panel,'Choose a gag',0,.135,.032,INK,TextNode.ACenter,text_font=self.font,text_wordwrap=10.6)
  self.detail_icon=DirectFrame(parent=self.gag_info_panel,frameColor=(0,0,0,0),pos=(0,0,.020),image_scale=(.065,1,.065));self.detail_icon.setTransparency(TransparencyAttrib.MAlpha)
  self.detail_text=self.label(self.gag_info_panel,'Hover over a gag\nto see its details.',-.157,-.055,.029,INK,sortOrder=30,text_font=self.font,text_wordwrap=11.0)
  self.reward_shortcuts={}
  # Individual positions: (horizontal, depth, vertical). Right/up are positive.
  run_pos = (.512, 0, -.50)
  pass_pos = (.272, 0, -.50)
  briefcase_pos = (.400, 0, -.68)
  for title,button_pos,fn,args in [('RUN',run_pos,self.panel_run,[]),('PASS',pass_pos,self.choose_action,['Pass'])]:
   btn=DirectButton(parent=self.content,relief=None,geom=self.ui_states('ttr_battle','ttr_t_gui_bat_battleMenu_suitcaseButton_',.18,.115),frameSize=(-.10,.10,-.0675,.0675),pos=button_pos,command=fn,extraArgs=args)
   for suffix,z,width in [('icon',0,.095)]:
    self.art_node('ttr_battle','ttr_t_gui_bat_battleMenu_'+title.lower()+'_'+suffix+'_card',btn,0,z,width)
   self.reward_shortcuts[title]=btn
  briefcase=DirectButton(parent=self.content,relief=None,geom=self.ui_states('ttr_battle','ttr_t_gui_bat_battleMenu_suitcaseButton_',.39,.20),frameSize=(-.21,.21,-.08,.08),pos=briefcase_pos,command=self.toggle_rewards)
  self.briefcase_icon=self.art_node('ttr_battle','ttr_t_gui_bat_battleMenu_suitcaseIcon_closed_card',briefcase,0,0,.21,.12)
  self.reward_shortcuts['REWARDS']=briefcase
  self.notes_idle()
  targets=self.game.targets(self.active,self.choice) if self.choice else []
  if targets:
   from target_panel import build
   build(self,targets)
 def fit_detail_text(self):
  probe=TextNode('detail-measure');probe.setFont(self.font)
  size=.029
  while True:
   probe.setWordwrap(.32/size);probe.setText(self.detail_text['text'])
   if probe.getHeight()*size<=.145 or size<=.018:break
   size-=.001
  self.detail_text['text_scale']=size;self.detail_text['text_wordwrap']=.32/size
 def gag_hover(self,name,event=None):
  if not hasattr(self,'detail_title') or self.detail_title.isEmpty():return
  if hasattr(self,'tooltip') and not self.tooltip.isEmpty():self.tooltip['text']=self.action_description(name).replace('Choose a target below or click a character','Choose a character')
  if hasattr(self,'detail_title'):
   self.notes_cover.hide();self.notes_button.hide()
   self.detail_text.setPos(-.157,0,-.055);self.detail_text.setScale(1);self.detail_text['text_align']=TextNode.ALeft
   gag=GAGS[name];toon=self.game.toons[self.active]
   self.detail_title['text']=name;self.detail_icon['image']=self.icons[name];self.detail_icon['image_scale']=(.065,1,.065)
   from battle_engine import Action
   power=str(gag.rounds)+' rounds' if gag.track=='Lure' else str(self.game.power(Action(self.active,name)))+(' Laff' if gag.track=='Toon-Up' else ' damage')
   self.detail_text['text']=f'{power}\nLevel {gag.level} gag\n'+('All targets' if gag.group else 'Single target')+f'\nStock: {toon.stock[name]}'
   self.fit_detail_text()
 def gag_leave(self,event=None):
  if self.choice in GAGS:self.gag_hover(self.choice)
  else:
   self.notes_idle()
   if hasattr(self,'tooltip') and not self.tooltip.isEmpty():self.tooltip['text']='Hover over a gag to see its name and power.'
 def notes_idle(self):
  if not hasattr(self,'detail_title') or self.detail_title.isEmpty() or self.notes_button.isEmpty():return
  self.notes_cover.show();self.notes_button.show()
  self.detail_title['text']=''
  self.detail_icon['image']=None
  toon=self.game.toons[self.active]
  self.detail_text['text_scale']=.029
  self.detail_text['text_wordwrap']=11
  self.detail_text['text']=f'Total gags\n{toon.carried} / {toon.pouch}'
  self.detail_text.setPos(0,0,-.10);self.detail_text.setScale(1.15);self.detail_text['text_align']=TextNode.ACenter
 def open_notes(self):
  from direct.gui.DirectGui import DirectEntry
  self.notes_return=getattr(self,'reward_category','SOS cards') if self.modal=='rewards' else None
  parent=self.modal_frame('Shticky Notes','notes',pause=True)
  self.notes_entry=DirectEntry(parent=parent,initialText=getattr(self,'battle_notes',''),numLines=8,width=54,scale=.045,pos=(-1.25,0,.5),focus=1)
  self.button(parent,'Save',0,-.65,self.save_notes,.5)
 def save_notes(self):
  self.battle_notes=self.notes_entry.get()
  category=self.notes_return;self.close_modal()
  if category:self.open_rewards(category)
 def set_briefcase_open(self,opened):
  if not hasattr(self,'briefcase_icon') or self.briefcase_icon.isEmpty():return
  self.briefcase_icon.removeNode()
  self.briefcase_icon=self.art_node('ttr_battle','ttr_t_gui_bat_battleMenu_suitcaseIcon_'+('open' if opened else 'closed')+'_card',self.reward_shortcuts['REWARDS'],0,0,.21,.12)
 def panel_run(self):
  if self.modal in ('rewards','fire'):self.close_modal()
  self.run_away()
 def toggle_rewards(self):
  if self.modal in ('rewards','fire'):self.close_modal()
  else:self.open_rewards(getattr(self,'reward_category','SOS cards'),filter_track=getattr(self,'reward_filter','All'))
 def target_caption(self,action):
  if not action:return '?', 'No choice yet'
  if action.gag=='Pass':return '—', 'Pass'
  gag=GAGS.get(action.gag)
  if action.target is not None:
   toon_target=gag and gag.track=='Toon-Up';team=self.game.toons if toon_target else self.game.cogs
   return ('Toon ' if toon_target else 'Cog ')+str(action.target+1), ('Toon ' if toon_target else 'Cog ')+str(action.target+1)+': '+team[action.target].name
  track=gag.track if gag else SOS.get(action.gag,('',))[0]
  if action.gag in DOODLES or track=='Toon-Up' or track.startswith('Restock') or track=='Toons Hit':
   return 'Toons', 'Other living Toons' if gag and track=='Toon-Up' else 'All living Toons'
  return 'Cogs', 'All eligible Cogs'
 def target_marks(self,action):
  if not action or action.gag=='Pass':return ''
  gag=GAGS.get(action.gag);track=gag.track if gag else SOS.get(action.gag,('',))[0]
  toons=action.gag in DOODLES or track=='Toon-Up' or track.startswith('Restock') or track=='Toons Hit'
  team=self.game.toons if toons else self.game.cogs
  slots=[i for i,t in enumerate(team) if t.alive]
  return ''.join('X' if (action.target==i if action.target is not None else not(toons and track=='Toon-Up' and action.gag in GAGS and i==action.toon)) else '-' for i in slots)
 def make_team_cards(self):
  self.laff_faces=[];self.status_targets=[];self.status_hp_labels=[];self.team_card_roots=[];self.unite_cooldown_labels=[];self.target_mark_labels=[]
  living=[i for i,t in enumerate(self.game.toons) if t.alive]
  for i,toon in enumerate(self.game.toons):
   container=DirectFrame(parent=self.hud,frameColor=(0,0,0,0));self.team_card_roots.append(container)
   if not toon.alive:container.hide()
   slot=living.index(i) if i in living else 0
   x=.70*(slot-(len(living)-1)/2) if self.animating else 1.015+(slot%2)*.49;z=-.82 if self.animating else -.195-(slot//2)*.40
   self.label(container,f'{i+1}. {toon.name}',x,z+.153,.029,INK,TextNode.ACenter)
   card=DirectButton(parent=container,relief=None,frameSize=(-.214,.214,-.135,.135),pos=(x,0,z),command=self.select_toon,extraArgs=[i],pressEffect=False)
   bg=self.art_node('ttr_toon','ttr_t_gui_bat_toonGUI_base_card',card,0,0,.43)
   # The extracted TTR model supplies anchors for the face, count, choice and targets.
   source=self.gui_models['ttr_toon'];lo,hi=source.getTightBounds();center=(lo+hi)*.5;scale=.43/(hi.x-lo.x)
   def anchor(name):
    point=(source.find('**/'+name).getPos(source)-center)*scale
    return point.x,point.z
   fx,fz=anchor('loc_laffMeter');hx,hz=anchor('loc_laffCount');gx,gz=anchor('loc_gagGUI');tx,tz=anchor('loc_targets')
   face=LaffFace(card,self.laff_model,self.font,toon,TOON_COLORS[i],(fx,0,fz),.044);self.laff_faces.append(face)
   hp=self.display_toon_hp[i] if self.animating and hasattr(self,'display_toon_hp') else toon.hp
   face.set_health(hp,toon.maximum)
   self.status_hp_labels.append(self.label(card,f'{hp}/{toon.maximum}',hx,hz,.034,INK,TextNode.ACenter))
   self.unite_cooldown_labels.append(self.label(card,'',0,.113,.022,(.65,.05,.05,1),TextNode.ACenter))
   action=self.selected.get(i);code,caption=self.target_caption(action);self.status_targets.append(caption)
   if action:
    gag=GAGS.get(action.gag);color=COLORS[TRACKS.index(gag.track)] if gag else (1,.85,.45,1)
    circle=DirectFrame(parent=card,image=self.choice_circle,image_scale=(.087,1,.087),image_color=color,pos=(gx,0,gz),frameColor=(0,0,0,0))
    circle.setTransparency(TransparencyAttrib.MAlpha)
   if action and action.gag in self.icons:
    icon=DirectFrame(parent=card,image=self.icons[action.gag],image_scale=(.057,1,.057),pos=(gx,0,gz),frameColor=(0,0,0,0));icon.setTransparency(TransparencyAttrib.MAlpha)
   elif action and action.gag=='Pass':self.art_node('battle_gui','tt_t_gui_bat_pass',card,gx,gz,.088)
   elif action and (action.gag in SOS or action.gag in DOODLES or action.gag in REMOTES or action.gag=='Fire'):
    model,name=self.reward_choice_art(action.gag)
    source=self.gui_models[model].find('**/'+name);lo,hi=source.getTightBounds()
    width=min(.115,.125*(hi.x-lo.x)/(hi.z-lo.z))
    icon=self.art_node(model,name,card,gx,gz,width)
    icon.setPythonTag('reward-choice',action.gag)
   elif action:
    title='SOS' if action.gag in SOS else 'Doodle' if action.gag in DOODLES else 'Remote' if 'remote' in action.gag else action.gag
    self.label(card,title,gx,gz-.016,.065 if title=='?' else .029,INK,TextNode.ACenter)
   self.target_mark_labels.append(self.label(card,self.target_marks(action),tx,tz,.038,INK,TextNode.ACenter))
   card.bind(DGG.ENTER,self.status_hover,[i]);card.bind(DGG.EXIT,self.gag_leave)
   if self.animating:continue
   self.button(container,'Auto' if self.auto_modes[i] else 'Manual',x,z-.176,self.toggle_auto,.38,(.47,.85,.51,1) if self.auto_modes[i] else (.86,.87,.77,1),[i],.027)
 def reward_choice_art(self,name):
  if name in REMOTES:
   kind,duration,*_=REMOTES[name]
   return 'ttr_battle',f'ttr_t_gui_bat_rewardsGUI_icon_remote{kind}_level{duration-1}_card'
  if name in DOODLES:
   trick=name.removeprefix('Doodle: ')
   stem={'Play Dead':'playDead'}.get(trick,trick.lower())
   return 'ttr_battle','ttr_t_gui_bat_rewardsMenu_doodlePanel_trickIcon_'+stem+'_card'
  if name=='Fire' or SOS[name][0]=='Fire':
   return 'ttr_battle','ttr_t_gui_bat_rewardsGUI_icon_fire_card'
  track=SOS[name][0]
  if track in ('Toons Hit','Cogs Miss'):
   return 'status_icons','ttr_t_gui_bat_statusEffect_icon_'+('increasedacc' if track=='Toons Hit' else 'decreasedacc')
  from sos_visuals import GAG_MOVIES
  gag='Lipstick' if track.startswith('Restock') else GAG_MOVIES[name.removeprefix('SOS: ')]
  # Use the same extracted inventory artwork as the NPC's actual gag.
  stems={'Lipstick':'lipstick','Juggling Cubes':'juggling_cubes','TNT':'tnt',
   'Hypno-goggles':'hypno_goggles','Foghorn':'fog_horn','Grand Piano':'piano',
   'Wedding Cake':'wedding','Geyser':'geyser','Presentation':'screen'}
  return 'gag_icons','inventory_'+stems[gag]
 def status_hover(self,index,event=None):
  action=self.selected.get(index)
  if hasattr(self,'tooltip') and not self.tooltip.isEmpty():self.tooltip['text']=self.game.toons[index].name+': '+(action.gag if action else 'Choosing...')+' | '+self.status_targets[index]
 def make_nametags(self):
  # Character names belong behind the battle controls, like the 3-D nametag pass.
  self.nametag_layer=DirectFrame(parent=self.hud,frameColor=(0,0,0,0),sortOrder=-10)
  self.toon_nametags=[]
  for toon in self.game.toons:
   tag=self.label(self.nametag_layer,toon.name,0,0,.043,(.08,.2,.66,1),TextNode.ACenter,text_shadow=(1,1,1,1),text_shadowOffset=(.045,.045))
   tag['text_font']=self.font
   self.toon_nametags.append(tag)
  self.nametags=[];self.cog_status_labels=[];self.cog_name_labels=[]
  for i,cog in enumerate(self.game.cogs):
   tag=DirectFrame(parent=self.nametag_layer,frameColor=(0,0,0,0))
   from character_nametags import cog_text,fit_cog_label
   name=self.label(tag,cog_text(cog,self.cog_actors[i]),0,0,.03,(0,0,0,1),TextNode.ACenter,text_font=self.suit_font,pad=(.016,.01))
   name['frameColor']=(.8,.8,.8,.8);fit_cog_label(name)
   self.cog_name_labels.append(name)
   status=[]
   if cog.lure:status.append(f'Lured: {cog.lure}')
   if cog.trap:status.append('Trapped')
   if cog.remote:status.append(f'{cog.remote[0]}: {cog.remote[1]}')
   self.cog_status_labels.append(self.label(tag,' / '.join(status),0,-.034,.024,(1,.92,.38,1),TextNode.ACenter,text_shadow=(0,0,0,1),text_shadowOffset=(.06,.06)))
   self.nametags.append(tag)
 def has_health_popup(self,parent):
  return any(not node.isEmpty() and not node.isHidden() and node.getParent()==parent for node,effect in getattr(self,'floating_effects',[]))
 def position_nametags(self):
  from speech_balloon import update as update_sos_speech
  for guest in getattr(self,'sos_guests',{}).values():
   for bubble in guest['root'].findAllMatches('**/sos-speech-bubble'):
    if not bubble.isHidden():update_sos_speech(self,bubble)
  for label,toon in zip(getattr(self,'unite_cooldown_labels',[]),self.game.toons):
   label['text']=f'Unite cooldown: {toon.unite_cooldown}' if toon.unite_cooldown else ''
  if not hasattr(self,'nametags'):return
  from character_nametags import anchor,project,cog_text,fit_cog_label
  for index,(tag,node,cog,actor) in enumerate(zip(self.nametags,self.cog_nodes,self.game.cogs,self.cog_actors)):
   status=[]
   if cog.lure:status.append(f'Lured: {cog.lure}')
   if cog.trap:status.append('Trapped')
   if cog.remote:status.append(f'{cog.remote[0]}: {cog.remote[1]}')
   self.cog_status_labels[index]['text']=' / '.join(status)
   name=self.cog_name_labels[index];text=cog_text(cog,actor)
   if name['text']!=text:name['text']=text;fit_cog_label(name)
   point=anchor(node,actor)
   if index in getattr(self,'remote_visuals',{}):point.z+=1.9
   pos=project(self,node,point)
   alive=self.display_cog_hp[index]>0 if self.animating and hasattr(self,'display_cog_hp') else cog.alive
   # Several future attack bubbles may already exist but remain hidden.
   # Any visible speech replaces the whole identity/status card.
   from speech_balloon import update as update_speech
   for bubble in node.findAllMatches('**/cog-speech-bubble'):
    if bubble.hasPythonTag('speech-content'):update_speech(self,bubble)
   speaking=any(not bubble.isHidden() for pattern in ('**/remote-joke-bubble','**/cog-speech-bubble') for bubble in node.findAllMatches(pattern))
   if alive and not speaking and not node.isHidden() and pos is not None and not self.has_health_popup(node):
    tag.show();tag.setPos(pos)
   else:tag.hide()
  for tag,node,toon,parts in zip(self.toon_nametags,self.toon_nodes,self.game.toons,self.toon_actors):
   if tag['text']!=toon.name:tag['text']=toon.name
   pos=project(self,node,anchor(node,parts['legs'],toon=True))
   phrase=node.find('**/unite-phrase');speaking=not phrase.isEmpty() and not phrase.isHidden()
   if not speaking and not node.isHidden() and pos is not None and not self.has_health_popup(node):
    tag.show();tag.setPos(pos)
   else:tag.hide()

 def target_enter(self,index,event=None):
  self.target_button_hover=index;self.preview_action_target(index)
 def target_exit(self,event=None):
  self.target_button_hover=None;self.preview_action_target(None)
 def preview_action_target(self,index):
  from battle_engine import Action
  if self.modal or self.animating or not self.choice:index=None
  if index is not None and index not in [i for i,t in self.game.targets(self.active,self.choice)]:index=None
  self.preview_target=index
  labels=getattr(self,'target_mark_labels',[])
  if self.active<len(labels):
   action=Action(self.active,self.choice,index) if index is not None else self.selected.get(self.active)
   labels[self.active]['text']=self.target_marks(action)
   labels[self.active]['text_fg']=(.7,.08,.06,1) if index is not None else INK
  for i,label in enumerate(getattr(self,'cog_name_labels',[])):
   toon_target=self.choice in GAGS and GAGS[self.choice].track=='Toon-Up'
   label['frameColor']=(1,.93,.55,.95) if index==i and not toon_target else (.8,.8,.8,.8)
  for i,label in enumerate(getattr(self,'toon_nametags',[])):
   toon_target=self.choice in GAGS and GAGS[self.choice].track=='Toon-Up'
   label['text_fg']=(.7,.08,.06,1) if index==i and toon_target else (.08,.2,.66,1)
  if hasattr(self,'tooltip') and not self.tooltip.isEmpty():
   if index is not None:
    team=self.game.toons if self.choice in GAGS and GAGS[self.choice].track=='Toon-Up' else self.game.cogs
    self.tooltip['text']=f'{self.choice} on {team[index].name}  •  Click to choose  •  Esc to cancel'
   elif self.choice:self.tooltip['text']=f'{self.choice} selected • Choose a target • Esc to cancel'
 def update_target_preview(self):
  if getattr(self,'target_button_hover',None) is not None:return
  hit=self.world_character_at_mouse() if self.choice and not self.modal and not self.animating else None
  index=None
  if hit:
   kind,i=hit;expected='toon' if self.choice in GAGS and GAGS[self.choice].track=='Toon-Up' else 'cog'
   if kind==expected:index=i
  if index!=getattr(self,'preview_target',None):self.preview_action_target(index)
