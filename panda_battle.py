"""Toon Battle Lab: Panda3D desktop scene and battle controls."""
from pathlib import Path
from copy import deepcopy
import math,json,time,argparse,random
from auto_toons import choose_action as automatic_choice
from panda3d.core import (loadPrcFileData,TextNode,StaticTextFont,AmbientLight,DirectionalLight,Vec4,Vec3,CardMaker,TransparencyAttrib,CollisionNode,CollisionRay,CollisionSphere,CollisionTraverser,CollisionHandlerQueue,BitMask32,Filename,WindowProperties)
loadPrcFileData('','window-title Toon Battle Lab - Panda3D\nwin-size 1440 900\nsync-video true\nshow-frame-rate-meter false\ntextures-power-2 none\nnotify-level warning\nframebuffer-multisample 1\nmultisamples 4\naudio-library-name p3openal_audio\n')
from direct.showbase.ShowBase import ShowBase
from direct.gui.DirectGui import DirectFrame,DirectLabel,DirectButton,DirectOptionMenu,DirectEntry,DirectCheckButton,DirectScrolledFrame,DGG
from direct.interval.IntervalGlobal import Sequence,Parallel,Func,Wait,LerpPosInterval,LerpHprInterval,LerpColorScaleInterval,LerpColorInterval,LerpScaleInterval
from battle_engine import Battle,Action,GAGS,TRACKS,COG_CATALOG,Cog,POUCH_SIZES,carry_limit
from support import CATEGORIES,UNITES,REWARDS,REMOTES,DOODLES,describe,use_unite
from round_timer import RoundTimer
from scene_art import CharacterArt,box,ring,COLORS
from battle_hud import BattleHUD
from game_resources import resource
from rewards_ui import RewardsUI
from battle_movies import BattleMovies
from camera_controls import CameraControls
from safe_option_menu import RebuildSafeOptionMenu

ROOT=Path(__file__).resolve().parent
INK=(.14,.2,.3,1);CREAM=(.99,.96,.85,1);NAVY=(.09,.16,.24,1);BLUE=(.25,.49,.67,1);GREEN=(.2,.53,.39,1)
TRACK_COLORS=[(.69,.52,.83,1),(.93,.73,.27,1),(.82,.45,.46,1),(.46,.61,.84,1),(.88,.59,.32,1),(.77,.48,.68,1),(.43,.72,.71,1)]
ICON_STEMS={
'Toon-Up':('feather','megaphone','lipstick','bamboo_cane','pixiedust','juggling_cubes','ladder'),
'Trap':('bannana_peel','rake','marbles','quicksand_icon','trapdoor','tnt','traintracks'),
'Lure':('1dollarbill','small_magnet','5dollarbill','big_magnet','10dollarbill','hypno_goggles','screen'),
'Sound':('bikehorn','whistle','bugle','aoogah','elephant','fog_horn','opera_singer'),
'Throw':('cup_cake','fruit_pie_slice','cream_pie_slice','fruitpie','creampie','cake','wedding'),
'Squirt':('squirt_flower','glass_of_water','water_gun','seltzer_bottle','firehose','storm_cloud','geyser'),
'Drop':('flower_pot','sandbag','anvil','weight','safe_box','piano','ship')}

class PandaBattle(CameraControls,BattleMovies,RewardsUI,BattleHUD,ShowBase):
 def __init__(self,seed=None,offscreen=False,timed=True):
  super().__init__(windowType='offscreen' if offscreen else None)
  self.disableMouse();self.setBackgroundColor(.63,.79,.88,1)
  self.seed=seed;self.game=Battle(seed=seed);self.timer=RoundTimer();self.timed=timed;self.active=0;self.category='Throw';self.choice=None
  self.battle_setup=deepcopy((self.game.toons,self.game.cogs))
  self.selected={};self.modal=None;self.animating=False;self.animation=None;self.message='Choose a Toon, a gag, and a target. Enter resolves the team plan.';self.sounds_enabled=True
  self.auto_resolve=True
  self.auto_advance=True
  self.auto_modes=[False]*4;self.auto_due={};self.auto_rng=random.Random(seed)
  self.ui=self.aspect2d.attachNewNode('interface');self.overlay=None;self.setup_draft=None
  self.icons={n:self.loader.loadTexture(str(ROOT/'assets'/('inventory_'+ICON_STEMS[g.track][g.level-1]+'.png'))) for n,g in GAGS.items()}
  self.laff={}
  font=resource('phase_3/fonts/ImpressBT.ttf')
  self.font=self.loader.loadFont(str(font)) if font.exists() else self.loader.loadFont('cmr12')
  self.font.setPixelsPerUnit(120)
  self.body_font=self.loader.loadFont(str(resource('Humanist.ttf')));self.body_font.setPixelsPerUnit(80)
  self.load_battle_ui()
  self.damage_font=StaticTextFont(self.loader.loadModel(str(resource('phase_3/fonts/MickeyFontClassic.bam')),noCache=True).node())
  self.floating_effects=[]
  self.cues={}
  self.environment=self.render.attachNewNode('plaza');self.characters=self.render.attachNewNode('characters');self.art=CharacterArt(self)
  self.make_environment();self.spawn_characters();self.setup_picking();self.make_hud()
  self.accept('enter',self.resolve);self.accept('escape',self.escape_action);self.accept('mouse1',self.pick)
  self.accept('window-event',self.on_window_event);self.accept('u',self.open_unites)
  for i in range(4):self.accept(str(i+1),self.select_toon,[i])
  self.init_camera_controls()
  self.taskMgr.add(self.tick,'round-clock');self.timer.reset();self.resize(self.win)
 def label(self,parent,text,x,z,size=.032,color=INK,align=TextNode.ALeft,**kw):
  font=kw.pop('text_font',self.body_font if size<.037 or any(c in text for c in "━→★") else self.font)
  return DirectLabel(parent=parent,text=text,text_font=font,text_scale=size,text_fg=color,text_align=align,frameColor=(0,0,0,0),pos=(x,0,z),**kw)
 def button(self,parent,text,x,z,command,width=.24,color=(.83,.88,.87,1),args=None,size=.034):
  return DirectButton(parent=parent,text=text,text_font=self.body_font if size<.037 or any(c in text for c in "━→★") else self.font,text_scale=size,text_fg=INK,text_pos=(0,-.01),frameSize=(-width/2,width/2,-.038,.038),frameColor=color,relief=None,geom=[self.gui_models['inventory_gui'].find('**/'+n) for n in ('InventoryButtonUp','InventoryButtonDown','InventoryButtonRollover','InventoryButtonFlat')],geom_scale=(width/.1803922,1,.076/.1137254),geom_color=color,pos=(x,0,z),command=command,extraArgs=args or [],pressEffect=False,rolloverSound=None,clickSound=None)
 def panel(self,parent,bounds,color):return DirectFrame(parent=parent,frameSize=bounds,frameColor=color,relief=DGG.FLAT)
 def on_window_event(self,window):
  if window!=self.win:return
  # Preserve Panda's aspect2d, pixel2d, minimize and close-window handling.
  if hasattr(window,'getProperties'):ShowBase.windowEvent(self,window)
  self.resize(window)
 def resize(self,window):
  if not window or window!=self.win:return
  width,height=window.getXSize(),window.getYSize()
  if width<=0 or height<=0:return
  aspect=width/height
  self.adjustWindowAspectRatio(aspect)
  # Fit the entire authored interface, including the outer clock and tooltips.
  self.ui.setScale(min(1,(width-24)/height/1.80,(height-24)/height/1.02))
  self.camLens.setAspectRatio(aspect)
  self.camLens.setFilmOffset(0,(.5-getattr(self,'scene_center',.725))*self.camLens.getFilmSize().y)
 def make_environment(self):
  self.camNode.getDisplayRegion(0).setDimensions(0,1,0,1)
  self.camera.setPos(10,-39,24);self.camera.lookAt(0,.5,2.8);self.camLens.setFov(53)
  ambient=AmbientLight('daylight');ambient.setColor((.68,.69,.73,1));self.render.setLight(self.render.attachNewNode(ambient))
  sun=DirectionalLight('sun');sun.setColor((.85,.78,.64,1));sun_node=self.render.attachNewNode(sun);sun_node.setHpr(-35,-55,0);self.render.setLight(sun_node)
  box(self.environment,(0,0,-.3),(40,40,.25),(.45,.64,.47,1))
  box(self.environment,(0,0,-.04),(11,11,.08),(.71,.74,.72,1))
  for x in range(-10,11,2):
   box(self.environment,(x,0,.05),(.012,10,.01),(.61,.65,.65,1))
  for y in range(-10,11,2):box(self.environment,(0,y,.05),(10,.012,.01),(.61,.65,.65,1))
  ring(self.environment,8.5,(.94,.88,.64,1),.08,5)
  for i,x in enumerate((-15,-9,-3,3,9,15)):
   height=5+(i%3)*1.3;color=[(.73,.45,.42,1),(.55,.67,.8,1),(.76,.68,.43,1)][i%3]
   box(self.environment,(x,15,height/2),(2.7,2,height/2),color)
   roof=box(self.environment,(x,15,height+.25),(2.9,2.2,.3),(.3,.38,.48,1));roof.setR(-3 if i%2 else 3)
   for floor in range(1,int(height),2):
    for dx in (-1.3,1.3):
     box(self.environment,(x+dx,12.97,floor),(.55,.045,.65),(.88,.86,.61,1))
     box(self.environment,(x+dx,12.9,floor),(.03,.03,.65),(.32,.42,.5,1))
  for x in (-13,13):
   for y in (-7,4):
    box(self.environment,(x,y,1.3),(.2,.2,1.3),(.4,.3,.23,1))
    crown=box(self.environment,(x,y,3),(1.25,1.25,1.25),(.3,.57,.4,1));crown.setH(30);crown.setR(15)
 def spawn_characters(self):
  if getattr(self,'victory_sound',None):self.victory_sound.stop()
  self.victory_sound=None
  from trap_movies import clear
  clear(self)
  from sos_movies import remove
  for index in list(getattr(self,'sos_guests',{})):remove(self,index)
  root=getattr(self,'railroad_root',None)
  if root is not None and not root.isEmpty():root.removeNode()
  self.railroad_root=None;self.railroad_targets=set()
  self.clear_movie_props()
  for node,effect in getattr(self,'floating_effects',[]):effect.pause();node.removeNode()
  self.floating_effects=[]
  self.art.clear();self.remote_visuals={};self.characters.node().removeAllChildren();self.toon_nodes=[];self.cog_nodes=[];self.toon_actors=[];self.cog_actors=[];self.world_labels=[]
  for kind,team,y in [('toon',self.game.toons,-3.5),('cog',self.game.cogs,3.7)]:
   for i,fighter in enumerate(team):
    root=self.characters.attachNewNode(f'{kind}-{i}');root.setPos(4*(i-(len(team)-1)/2),y,0)
    if kind=='cog':actor=self.art.cog(fighter,root);self.cog_nodes.append(root);self.cog_actors.append(actor)
    else:actor=self.art.toon(fighter,i,root);self.toon_nodes.append(root);self.toon_actors.append(actor)
    collider=CollisionNode(f'{kind}-pick');collider.addSolid(CollisionSphere(0,0,1.8,1.3));collider.setIntoCollideMask(BitMask32.bit(1));np=root.attachNewNode(collider);np.setTag('kind',kind);np.setTag('index',str(i))
    ring(root,1.15,(.3,.38,.42,.6),.09,7)
  self.active_ring=ring(self.toon_nodes[self.active],1.35,(1,.88,.34,1),.12,5)
 def setup_picking(self):
  self.traverser=CollisionTraverser();self.queue=CollisionHandlerQueue();node=CollisionNode('mouse-ray');self.ray=CollisionRay();node.addSolid(self.ray);node.setFromCollideMask(BitMask32.bit(1));node.setIntoCollideMask(BitMask32.allOff());self.ray_node=self.camera.attachNewNode(node);self.traverser.addCollider(self.ray_node,self.queue)
 def world_character_at_mouse(self):
  if getattr(self,'log_popup',None) and self.log_popup.contains_mouse():return None
  if self.modal or self.animating or not self.mouseWatcherNode.hasMouse():return None
  mouse=self.mouseWatcherNode.getMouse()
  from panda3d.core import Point3
  ui_point=self.ui.getRelativePoint(self.render2d,Point3(mouse.x,0,mouse.y))
  # Hit-test in the same scaled coordinates as the extracted battle UI.
  if ui_point.z<.12 or ui_point.z>.72:return None
  from ui_hit_test import contains
  if self.choice and contains(getattr(self,'target_panel',None),self.ui,ui_point):return None
  region=self.mouseWatcherNode.getOverRegion()
  if region and region.getName().startswith('pg'):return None
  self.ray.setFromLens(self.camNode,mouse.x,mouse.y);self.traverser.traverse(self.characters)
  if not self.queue.getNumEntries():return None
  self.queue.sortEntries();node=self.queue.getEntry(0).getIntoNodePath()
  return node.getTag('kind'),int(node.getTag('index'))
 def pick(self):
  hit=self.world_character_at_mouse()
  if not hit:return
  kind,index=hit
  if kind=='toon':
   if self.choice in GAGS and GAGS[self.choice].track=='Toon-Up':self.choose_target(index)
   elif not self.choice:self.select_toon(index)
  else:self.choose_target(index)
 def action_description(self,name):
  if name=='Pass':return 'Pass this round.'
  if name not in GAGS:return describe(self.game,self.active,name)
  g=GAGS[name];power=f'{g.rounds} lure rounds' if g.track=='Lure' else f'{self.game.power(Action(self.active,name))} '+('Laff total' if g.track=='Toon-Up' else 'damage')
  return f'{name} | Gag level {g.level} | {power} | '+('Group action' if g.group else 'Choose a target below or click a character')
 def select_toon(self,index):
  if not 0<=index<len(self.game.toons):return
  if self.animating:return
  if not self.game.toons[index].alive:self.notice('That Toon went sad.');return
  self.active=index;self.choice=None
  self.active_ring.removeNode();self.active_ring=ring(self.toon_nodes[index],1.35,(1,.88,.34,1),.12,5);self.make_hud()
 def set_category(self,category):
  if self.animating:return
  self.category=category;self.choice=None;self.make_hud()
 def choose_action(self,name):
  if self.modal in ('rewards','fire'):self.close_modal()
  if self.auto_modes[self.active]:self.notice('Switch this Toon to Manual to choose its action.');return
  if self.animating or self.game.result:return
  self.choice=name
  try:
   targets=self.game.targets(self.active,name)
   if not targets:self.commit(Action(self.active,name))
   else:self.message=self.action_description(name)
  except ValueError as error:self.message=str(error)
  self.make_hud()
 def escape_action(self):
  if self.modal:self.close_modal()
  elif self.choice:self.cancel_choice()
  elif getattr(self,'log_popup',None):self.log_popup.close()
 def cancel_choice(self):
  if self.animating or self.modal or not self.choice:return
  self.choice=None
  previous=self.selected.get(self.active)
  self.message='Target selection cancelled. '+('Your confirmed choice remains: '+previous.gag+'.' if previous else 'Choose another gag whenever you are ready.')
  self.make_hud()
 def choose_target(self,index):
  if self.animating or self.modal or self.game.result:return
  if not self.choice:self.notice('Choose a gag or targeted reward first.');return
  self.commit(Action(self.active,self.choice,index));self.make_hud()
 def commit(self,action):
  try:self.game.validate(action)
  except ValueError as error:self.message=str(error);return
  self.selected[action.toon]=action;self.choice=None;self.message=f'{self.game.toons[action.toon].name}: {action.gag} selected.'
  if self.auto_advance:
   count=len(self.game.toons)
   for step in range(1,count):
    index=(action.toon+step)%count
    if self.game.toons[index].alive and not self.auto_modes[index] and index not in self.selected:
     self.active=index
     self.active_ring.removeNode();self.active_ring=ring(self.toon_nodes[index],1.35,(1,.88,.34,1),.12,5)
     break
 def toggle_auto_advance(self):
  self.auto_advance=not self.auto_advance
  self.make_hud()
 def notice(self,message):self.message=message;self.make_hud()
 def toggle_auto(self,index):
  if not 0<=index<len(self.game.toons) or self.animating or self.game.result:return
  self.auto_modes[index]=not self.auto_modes[index];self.selected.pop(index,None)
  if self.active==index:self.choice=None
  if self.auto_modes[index]:self.auto_due[index]=time.monotonic()+self.auto_rng.uniform(.8,2.8)
  else:self.auto_due.pop(index,None)
  self.notice(self.game.toons[index].name+(': Auto chooses regular gags independently.' if self.auto_modes[index] else ': Manual control enabled.'))
 def schedule_auto(self):
  self.auto_modes=(self.auto_modes+[False]*4)[:len(self.game.toons)]
  self.auto_due={i:time.monotonic()+self.auto_rng.uniform(.8,2.8) for i,on in enumerate(self.auto_modes) if on}
 def update_auto(self):
  if self.modal or self.animating or self.game.result:return
  changed=False
  for i,on in enumerate(self.auto_modes):
   if i<len(self.game.toons) and on and self.game.toons[i].alive and i not in self.selected and time.monotonic()>=self.auto_due.get(i,float('inf')):
    self.selected[i]=automatic_choice(self.game,i,self.auto_rng);changed=True
  if changed:self.make_hud()
 def toggle_sound(self):
  self.sounds_enabled=not self.sounds_enabled
  if getattr(self,'victory_sound',None):
   if self.sounds_enabled:self.victory_sound.play()
   else:self.victory_sound.stop()
  if not self.sounds_enabled:
   for sound in getattr(self,'movie_sounds',[]):sound.stop()
  self.make_hud()

 def toggle_auto_resolve(self):
  self.auto_resolve=not self.auto_resolve
  self.make_hud()
 def resolve_if_ready(self):
  if not self.auto_resolve or self.animating or self.modal or self.choice or self.game.result:return
  living=[i for i,t in enumerate(self.game.toons) if t.alive]
  if not living or any(i not in self.selected for i in living):return
  remote_targets=set()
  for i in living:
   action=self.selected[i]
   try:self.game.validate(action)
   except ValueError:return
   if action.gag in REMOTES:
    if action.target in remote_targets:return
    remote_targets.add(action.target)
  self.resolve()
 def toggle_timer(self):
  self.timed=not self.timed;self.timer.reset();self.make_hud()
 def tick(self,task):
  from time import monotonic
  now=monotonic()
  for parts in getattr(self,'toon_actors',[]):
   legs=parts['legs']
   if legs.hasPythonTag('face-controller'):legs.getPythonTag('face-controller').tick(now)
  if getattr(self,'log_popup',None):self.log_popup.refresh()
  if self.modal=='setup':__import__('setup_screen').update_pouch(self)
  self.update_auto()
  self.resolve_if_ready()
  if hasattr(self,'clock_label'):
   self.clock_label['text']='PAUSE' if self.timer.paused else str(self.timer.remaining)+'s' if self.timed and not self.game.result else 'DONE' if self.game.result else '--'
  if getattr(self,'modal_clock',None):self.modal_clock['text']=self.clock_label['text']
  if self.timed and not self.timer.paused and not self.animating and not self.game.result and self.timer.remaining==0:self.resolve(True)
  self.position_nametags()
  self.update_target_preview()
  now=time.monotonic()
  for i,(cog,actor) in enumerate(zip(self.game.cogs,self.cog_actors)):
   visual=__import__('types').SimpleNamespace(hp=self.display_cog_hp[i],maximum=cog.maximum) if self.animating and hasattr(self,'display_cog_hp') else cog
   self.art.update_health(actor,visual,now)
  for c,node in zip(self.game.cogs,self.cog_nodes):
   if not self.animating:node.setR(0)
  return task.cont
 def resolve(self,timed_out=False):
  if self.animating or self.modal=='setup' or self.game.result:return
  for i,enabled in enumerate(self.auto_modes):
   if i<len(self.game.toons) and enabled and self.game.toons[i].alive and i not in self.selected:self.selected[i]=automatic_choice(self.game,i,self.auto_rng)
  actions=[];remote_targets=set()
  try:
   for i,t in enumerate(self.game.toons):
    if not t.alive:continue
    action=self.selected.get(i,Action(i))
    try:
     self.game.validate(action)
     if action.gag in REMOTES:
      if action.target in remote_targets:raise ValueError('Choose different Cogs for simultaneous remotes.')
      remote_targets.add(action.target)
    except ValueError:
     if not timed_out:raise
     action=Action(i)
    actions.append(action)
   before_cogs=[c.hp for c in self.game.cogs];before_toons=[t.hp for t in self.game.toons]
   self.game.plans.clear()
   for a in actions:self.game.plan(a)
   self.round_events=self.game.resolve_events()
  except ValueError as error:self.notice(str(error));return
  self.display_toon_hp=list(before_toons);self.display_cog_hp=list(before_cogs)
  self.close_modal();self.animating=True;self.timer.pause();self.message='Resolving battle...';self.make_hud()
  self.play_next_event()
 def play_toon_animation(self,index,name,loop=False):
  legs=self.toon_actors[index]['legs']
  if legs.hasPythonTag('face-controller'):
   face=legs.getPythonTag('face-controller')
   expression='sad' if name=='lose' or not self.game.toons[index].alive else 'neutral'
   if face.expression!=expression:face.set(expression)
  for actor in self.toon_actors[index].values():
   if name in actor.getAnimNames():
    (actor.loop if loop else actor.play)(name)

 def float_text(self,parent,amount,height=3.0,start=True,text=None,bonus=0):
  # DistributedSuitBase.showHpText: combo=1 (yellow), knockback=2 (orange).
  color=(1,0,0,1) if text is not None else (1,1,0,1) if bonus==1 else (1,.5,0,1) if bonus==2 else (.9,0,0,1) if amount<0 else (0,.9,0,1)
  tn=TextNode('health-change');tn.setText(text if text is not None else f'{amount:+}');tn.setFont(self.damage_font);tn.setAlign(TextNode.ACenter);tn.setTextColor(*color)
  node=parent.attachNewNode(tn);node.setPos(0,0,height/2);node.setScale(.7 if text is not None else .72);node.setBillboardPointEye();node.setLightOff();node.setTransparency(TransparencyAttrib.MAlpha);node.setBin('fixed',100);node.setDepthTest(False);node.setDepthWrite(False);node.hide()
  effect=Sequence(Func(node.show),LerpPosInterval(node,1.0,(0,0,height+1.5),blendType='easeOut'),Wait(1.1 if text is not None else .85),LerpColorInterval(node,.1,(*color[:3],0),startColor=color),Func(node.removeNode))
  self.floating_effects=[(n,e) for n,e in self.floating_effects if not n.isEmpty()]
  self.floating_effects.append((node,effect))
  if start:effect.start()
  return effect
 def formation_positions(self):
  for team,nodes,y in [(self.game.toons,self.toon_nodes,-3.5),(self.game.cogs,self.cog_nodes,3.7)]:
   living=[i for i,fighter in enumerate(team) if fighter.alive]
   for slot,index in enumerate(living):yield nodes[index],Vec3(4*(slot-(len(living)-1)/2),2.2 if team is self.game.cogs and team[index].lure else y,0)
 def hide_defeated(self):
  for team,nodes in [(self.game.toons,self.toon_nodes),(self.game.cogs,self.cog_nodes)]:
   for fighter,node in zip(team,nodes):
    if not fighter.alive:
     node.hide()
     for collider in node.findAllMatches('**/+CollisionNode'):collider.node().setIntoCollideMask(BitMask32.allOff())
 def finish_round(self):
  self.animating=False
  self.hide_defeated()
  for node,pos in self.formation_positions():node.setPos(pos)
  if not any(t.alive for t in self.game.toons):
   for cog,actor in zip(self.game.cogs,self.cog_actors):
    if cog.alive:actor.loop('victory')
  self.sync_remote_visuals()
  for i,cog in enumerate(self.game.cogs):
   if cog.alive:self.restore_cog_pose(i)
  victory=not any(c.alive for c in self.game.cogs)
  if victory and any(t.alive for t in self.game.toons) and getattr(self,'victory_sound',None) is None:
   self.victory_sound=self.loader.loadSfx(str(resource('phase_3.5/audio/sfx/ENC_Win.ogg')))
   self.victory_sound.setLoop(True);self.victory_sound.setVolume(.65)
   if self.sounds_enabled:self.victory_sound.play()
  for i,toon in enumerate(self.game.toons):
   if toon.alive:self.play_toon_animation(i,'victory' if victory else 'idle',loop=True)
   else:self.toon_nodes[i].hide()
  for node,c in zip(self.cog_nodes,self.game.cogs):
   if not c.alive:node.hide()
  if self.auto_advance and not self.game.result:
   # Begin each new plan with the first living Toon needing manual input.
   self.active=next((i for i,t in enumerate(self.game.toons) if t.alive and not self.auto_modes[i]),
                    next((i for i,t in enumerate(self.game.toons) if t.alive),0))
   self.active_ring.reparentTo(self.toon_nodes[self.active])
  elif not self.game.toons[self.active].alive:
   self.active=next((i for i,t in enumerate(self.game.toons) if t.alive),0)
   self.active_ring.reparentTo(self.toon_nodes[self.active])
  self.selected.clear();self.choice=None;self.message=self.game.result or f'Round {self.game.round}: select the next team plan.'
  self.timer.reset();self.timer.pause() if self.game.result else self.timer.resume();self.schedule_auto();self.make_hud()
 def new_battle(self):
  # Cancel playback without finishing it: finishing would apply old impacts
  # and advance the old round against the replacement battle.
  if self.animation:self.animation.pause()
  self.animation=None
  for clip in getattr(self,'live_departures',[]):clip.pause()
  self.live_departures=[]
  events=getattr(self,'round_events',None)
  if events is not None and hasattr(events,'close'):events.close()
  self.round_events=iter(())
  self.animating=False
  self.close_modal();self.game=Battle(seed=self.seed)
  self.game.toons,self.game.cogs=deepcopy(self.battle_setup)
  self.selected.clear();self.choice=None;self.active=0;self.spawn_characters();self.timer.reset();self.timer.resume();self.schedule_auto();self.message='New battle. Select each Toon with the mouse or keys 1-4.';self.make_hud()
 def modal_frame(self,title,kind,pause=False):
  self.close_modal()
  self.modal=kind
  if pause:self.timer.pause()
  self.overlay=self.panel(self.ui,(-1.78,1.78,-1,1),(.035,.07,.12,.92));self.hud.hide()
  self.panel(self.overlay,(-1.6,1.6,-.9,.9),CREAM)
  self.label(self.overlay,title,-1.48,.79,.052)
  self.button(self.overlay,'Close',1.36,.80,self.close_modal,.25)
  self.modal_clock=self.label(self.overlay,'',.99,.79,.034,INK,TextNode.ACenter)
  return self.overlay
 def close_modal(self):
  was=self.modal
  if was=='rewards' and getattr(self,'reward_category',None)=='SOS cards' and hasattr(self,'reward_scroll'):
   if not hasattr(self,'reward_scroll_values'):self.reward_scroll_values={}
   self.reward_scroll_values[self.reward_filter]=self.reward_scroll.verticalScroll['value']
  preview=getattr(self,'reward_pet',None)
  if preview:
   preview.cleanup();self.reward_pet=None
  if self.overlay:self.overlay.destroy();self.overlay=None
  self.modal=None;self.modal_clock=None
  if hasattr(self,'hud'):self.hud.show()
  if was in ('rewards','fire') and hasattr(self,'content'):
   self.content.show();self.gag_grid.show();self.set_briefcase_open(False)
   panel=self.hud.find('**/ttr_t_gui_bat_battleMenu_base_card-art')
   if not panel.isEmpty():panel.show()
  if was in ('setup','notes'):self.timer.resume()
 def select_reward(self,name):
  if not self.reward_available(name):return
  self.close_modal();self.choose_action(name)
 def open_unites(self,caster=None):
  caster=self.active if caster is None else caster
  if not self.game.toons[caster].alive:
   caster=next((i for i,t in enumerate(self.game.toons) if t.alive),None)
  if caster is None:return
  self.unite_caster=caster
  parent=self.modal_frame(f'SpeedChat / Unites / {self.game.toons[caster].name}','unites')
  planned=self.selected.get(caster)
  for i,t in enumerate(self.game.toons):
   if t.alive:self.button(parent,t.name,-1.1+i*.72,.70,self.open_unites,.64,args=[i],size=.026)
  self.label(parent,'Use immediately. Your battle choice stays: '+(planned.gag if planned else 'not chosen yet'),-1.47,.61,.027)
  self.label(parent,f'Shared Toon-Up / Gag-Up cooldown: {self.game.toons[caster].unite_cooldown} rounds remaining.',-1.47,.56,.025)
  for i,name in enumerate(UNITES):
   self.button(parent,name.replace('Unite: ','')+f'  x{self.game.toons[caster].rewards[name]}',-.77+(i%2)*1.51,.46-(i//2)*.14,self.use_unite,1.4,args=[name],size=.028)
 def use_unite(self,name):
  before=[t.hp for t in self.game.toons]
  try:
   caster=getattr(self,'unite_caster',self.active) if self.modal=='unites' else self.active
   recipients=use_unite(self.game,caster,name)
   self.play_unite_effect(caster,name,recipients);self.close_modal();self.notice('Unite used. Your planned action remains available.')
   for i,(old,toon) in enumerate(zip(before,self.game.toons)):
    if toon.hp!=old:
     if hasattr(self,'display_toon_hp'):self.display_toon_hp[i]=toon.hp
     if hasattr(self,'status_hp_labels'):self.status_hp_labels[i]['text']=f'{toon.hp}/{toon.maximum}'
     self.float_text(self.toon_nodes[i],toon.hp-old)
     self.laff_faces[i].set_health(old,toon.maximum);self.laff_faces[i].set_health(toon.hp,toon.maximum,animate=True)
  except ValueError as error:self.close_modal();self.notice(str(error))
 def open_log(self):
  if getattr(self,'log_popup',None):self.log_popup.close()
  else:
   from battle_log import BattleLog
   self.log_popup=BattleLog(self)
 def scroll_log(self,direction):
  if getattr(self,'log_popup',None):self.log_popup.wheel(direction)
 def open_rules(self):
  parent=self.modal_frame('Mechanics and sources','rules');self.text_scroll(parent,(ROOT/'MECHANICS.md').read_text(),.028)
 def text_scroll(self,parent,text,size):
  import textwrap
  lines=[]
  for line in text.splitlines():lines+=textwrap.wrap(line,100 if size<.03 else 77) or ['']
  height=max(1.5,len(lines)*size*1.5)
  scroll=DirectScrolledFrame(parent=parent,frameSize=(-1.47,1.47,-.79,.67),canvasSize=(-1.43,1.4,-height,0),frameColor=(.93,.92,.85,1),scrollBarWidth=.035)
  body=self.label(scroll.getCanvas(),'\n'.join(lines),-1.38,-.05,size);body['text_font']=self.body_font
  scroll.verticalScroll['value']=1 if self.modal=='log' else 0
 def open_setup(self):
  if self.animating:return
  if self.modal=='setup':return
  defaults=Battle(seed=self.seed)
  self.setup_draft={'toons':deepcopy(self.game.toons)+deepcopy(defaults.toons[len(self.game.toons):]),'toon_count':len(self.game.toons),'cog_count':len(self.game.cogs),'cogs':[(c.name,c.level) for c in self.game.cogs]+[(c.name,c.level) for c in defaults.cogs[len(self.game.cogs):]],'version2':[c.version2 for c in self.game.cogs]+[False]*(4-len(self.game.cogs)),'skelecogs':[c.skelecog for c in self.game.cogs]+[False]*(4-len(self.game.cogs))}
  self.setup_tab='Cogs';self.setup_page=0;self.setup_kind='gags';self.setup_section='profile';self.setup_reward_group='SOS';self.modal_frame('Battle setup / clock paused','setup',True);self.draw_setup()
 def menu(self,parent,items,x,z,width,command=None,initial=None):
  return RebuildSafeOptionMenu(parent=parent,items=[str(v) for v in items],initialitem=[str(v) for v in items].index(str(initial)) if initial is not None and str(initial) in [str(v) for v in items] else 0,scale=.031,pos=(x,0,z),text_font=self.font,text_fg=INK,frameColor=(.84,.87,.86,1),highlightColor=(.5,.7,.7,1),command=command,popupMarker_pos=(width/.031-.6,0,0),frameSize=(0,width/.031,-.35,1.05),item_frameSize=(0,width/.031,-.35,1.05))
 def entry(self,parent,value,x,z,width,callback):
  return self._entry(parent,value,x,z,width,callback)
 def _entry(self,parent,value,x,z,width,callback):
  entry=DirectEntry(parent=parent,initialText=str(value),scale=.034,pos=(x,0,z),width=width/.034,text_font=self.font,frameColor=(1,1,1,1),text_fg=INK)
  entry['focusOutCommand']=lambda:callback(entry.get());self.setup_entries.append((entry,callback));return entry
 def flush_setup(self):
  for entry,callback in getattr(self,'setup_entries',[]):callback(entry.get())
 def setup_switch(self,tab):
  self.flush_setup();self.setup_tab=tab;self.setup_page=0;self.draw_setup()
 def draw_setup(self):
  from setup_screen import draw
  draw(self)
 def setup_doodle_fill(self,toon,trained):
  self.flush_setup();toon.doodle_trained=trained;toon.doodle_skills={n:10000 if trained else 0 for n in DOODLES};self.draw_setup()
 def setup_count(self,field,value):
  self.flush_setup();self.setup_draft[field]=int(value);self.draw_setup()
 def setup_form(self,index,value):
  self.setup_draft['skelecogs'][index]=value=='Skelecog';self.setup_draft['version2'][index]=value=='v2.0'
 def setup_department(self,index,dept):
  if dept=='None':self.setup_draft['cogs'][index]=('None',1)
  else:
   name=next(n for n,d in COG_CATALOG.items() if d['department']==dept);self.setup_draft['cogs'][index]=(name,COG_CATALOG[name]['rank'])
  self.draw_setup()
 def setup_cog(self,index,name):
  old,level=self.setup_draft['cogs'][index];rank=COG_CATALOG.get(name,{'rank':1})['rank'];self.setup_draft['cogs'][index]=(name,max(rank,min(rank+4,level)));self.draw_setup()
 def setup_level(self,index,level):name,_=self.setup_draft['cogs'][index];self.setup_draft['cogs'][index]=(name,int(level))
 def setup_missing(self,t,track):
  self.flush_setup();t.missing_track=track
  for n,g in GAGS.items():
   if g.track==track:t.stock[n]=0
  if t.organic==track:t.organic='None'
  if t.extra_seven==track:t.extra_seven='None'
  self.draw_setup()
 def setup_toggle(self,t,field):
  self.flush_setup();setattr(t,field,not getattr(t,field))
  if field=='doodle_trained':t.doodle_skills={}
  self.draw_setup()
 def setup_inventory(self,kind):
  from setup_screen import section
  section(self,kind)
 def setup_next(self,delta):
  self.flush_setup();size=len(__import__('setup_screen').reward_names(self) if self.setup_kind=='rewards' else GAGS if self.setup_kind=='gags' else DOODLES);self.setup_page=(self.setup_page+delta)%math.ceil(size/8);self.draw_setup()
 def setup_fill(self,t,fill):
  self.flush_setup()
  try:capacity=int(t.pouch)
  except ValueError:return
  t.stock={n:0 for n in GAGS}
  if fill:
   for level in range(7,0,-1):
    for n,g in GAGS.items():
     if g.level!=level or g.track==t.missing_track:continue
     count=carry_limit(g,t.extra_seven) if level>=5 else 2
     if level<7:count=min(count,capacity);capacity-=count
     t.stock[n]=count
  self.draw_setup()
 def apply_setup(self):
  self.flush_setup()
  try:
   toons=deepcopy(self.setup_draft['toons'][:self.setup_draft['toon_count']]);cogs=[Cog(n,lv,skelecog=self.setup_draft['skelecogs'][i],version2=self.setup_draft['version2'][i]) for i,(n,lv) in enumerate(self.setup_draft['cogs'][:self.setup_draft['cog_count']]) if n!='None']
   if not cogs:raise ValueError('Choose at least one Cog.')
   for t in toons:
    t.hp=int(t.hp);t.maximum=int(t.maximum)
    if not t.name.strip() or not 1<=t.hp<=t.maximum<=200:raise ValueError('Each Toon needs a name and 1 <= Laff <= max Laff <= 200.')
    if t.missing_track!='None' and t.missing_track in (t.organic,t.extra_seven):raise ValueError('Organic and extra level 7 tracks must be unlocked.')
    t.stock={n:int(v) for n,v in t.stock.items()};t.check_inventory(t.stock);t.rewards={n:int(v) for n,v in t.rewards.items()}
    if any(not 0<=v<=(200 if n=='Fire' else 100) for n,v in t.rewards.items()):raise ValueError('Reward limit: 200 fires, 100 of each other reward.')
    t.doodle_skills={n:int(v) for n,v in t.doodle_skills.items()}
    if any(n not in DOODLES or not 0<=v<=10000 for n,v in t.doodle_skills.items()):raise ValueError('Doodle skill points must be between 0 and 10000.')
    t.unite_cooldown=0;t.escaped=False;t.accuracy_up=0
   game=Battle(seed=self.seed);game.toons=toons;game.cogs=cogs
  except ValueError as error:self.setup_error['text']=str(error);return
  self.battle_setup=deepcopy((game.toons,game.cogs))
  self.game=game;self.close_modal();self.selected.clear();self.choice=None;self.active=0;self.timer.reset();self.spawn_characters();self.schedule_auto();self.notice('Custom battle started.')
 def destroy(self):
  from trap_movies import clear
  clear(self)
  for clip in getattr(self,'live_departures',[]):clip.pause()
  self.live_departures=[]
  self.clear_movie_props()
  for node,effect in getattr(self,'floating_effects',[]):effect.pause();node.removeNode()
  if getattr(self,'animation',None):self.animation.pause()
  if hasattr(self,'art'):self.art.clear()
  super().destroy()

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--seed',type=int);parser.add_argument('--untimed',action='store_true');args=parser.parse_args()
 PandaBattle(seed=args.seed,timed=not args.untimed).run()
if __name__=='__main__':main()
