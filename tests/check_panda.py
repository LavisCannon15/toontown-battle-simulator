"""Headless Panda3D integration checks using real models and DirectGUI controls."""
from pathlib import Path
import sys,time
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from panda3d.core import loadPrcFileData
loadPrcFileData('','audio-library-name null\nwin-size 1440 900')
from panda_battle import PandaBattle
from battle_engine import Action,GAGS,COG_CATALOG,Cog
from support import CATEGORIES

def finish(app):
 for _ in range(100):
  for clip in getattr(app,'live_departures',[]):
   if clip.isPlaying():clip.finish()
  if app.animation:app.animation.finish()
  for _ in range(2):app.taskMgr.step()
  if not app.animating:return
 raise AssertionError('Battle playback did not complete')

app=PandaBattle(seed=1,offscreen=True,timed=False)
app.auto_advance=False  # This legacy scenario explicitly drives each Toon.
assert 'tkinter' not in sys.modules
assert len(app.icons)==49 and len(app.cog_nodes)==4
# Original static sign font retains glyph textures; the effect rises then fades.
from panda3d.core import NodePath
fx=app.float_text(app.toon_nodes[0],20,height=3,start=False)
node=app.floating_effects[-1][0]
assert node.node().getText()=='+20'
assert len(NodePath(node.node().generate()).findAllTextures())>0
fx.start();fx.pause();fx.setT(1.0);assert abs(node.getZ()-4.5)<.01
fx.setT(1.9);assert .4<node.getColor().w<.6
fx.finish();assert node.isEmpty()

assert len(app.gag_buttons)==49 and len(app.nametags)==4
app.gag_hover('Wedding Cake');assert 'Wedding Cake' in app.tooltip['text']
app.gag_leave()
# Nametags track scene movement rather than staying in fixed HUD slots.
app.position_nametags();before_tag=app.nametags[0].getX()
app.cog_nodes[0].setX(app.cog_nodes[0].getX()+1);app.position_nametags()
assert app.nametags[0].getX()!=before_tag
app.cog_nodes[0].setX(app.cog_nodes[0].getX()-1)
assert all(a.getCurrentAnim()=='idle' for a in app.cog_actors)
assert len(app.laff_faces)==4
face=app.laff_faces[0]
for hp,teeth in [(84,6),(70,5),(51,4),(34,3),(17,2),(1,1)]:
 face.set_health(hp,100);assert sum(not t.isHidden() for t in face.teeth)==teeth
face.set_health(100,100);assert not face.parts['smile'].isHidden() and face.parts['open_smile'].isHidden()
face.set_health(0,100);assert not face.parts['frown'].isHidden() and face.parts['eyes'].isHidden()
face.set_health(100,100)
assert len(app.hud.findAllMatches('**/ttr_t_gui_bat_toonGUI_base_card-art'))==4
# Each partner switches independently. Auto delays choices, keeps stock, and can be cancelled.
stock_before=app.game.toons[1].stock.copy()
app.toggle_auto(1);assert app.auto_modes[1] and 1 not in app.selected
app.auto_due[1]=0;app.update_auto();assert 1 in app.selected
app.game.validate(app.selected[1]);assert app.game.toons[1].stock==stock_before
app.toggle_auto(1);assert not app.auto_modes[1] and 1 not in app.selected
app.select_toon(1);app.choose_action('Cupcake');app.choose_target(2)
assert app.status_targets[1]=='Cog 3: '+app.game.cogs[2].name
app.selected.clear();app.select_toon(0)
# Enter fills pending Auto choices, preserves the user's choice, and leaves manual partners passing.
app.toggle_auto(1);app.choose_action('Cupcake');app.choose_target(0)
partner_stock=sum(app.game.toons[1].stock.values());manual_stock=app.game.toons[2].stock.copy()
app.resolve();finish(app);assert app.game.round==2
assert sum(app.game.toons[1].stock.values())==partner_stock-1
assert app.game.toons[2].stock==manual_stock
finish(app);assert 1 in app.auto_due
app.new_battle();app.toggle_auto(1)

# Original chest mesh is attached to the animated suit joint, with classic thresholds.
actor=app.cog_actors[0];cog=app.game.cogs[0];saved_hp=cog.hp
meter,glow=actor.getPythonTag('health-light')
assert meter.getParent().getName()=='joint_attachMeter'
for fraction,condition in [(1,0),(.9,1),(.5,2),(.2,3)]:
 cog.hp=cog.maximum*fraction;app.art.update_health(actor,cog,0)
 assert meter.getPythonTag('health-condition')==condition
cog.hp=cog.maximum*.02
app.art.update_health(actor,cog,.1);assert meter.getPythonTag('health-condition')==3
app.art.update_health(actor,cog,.8);assert meter.getPythonTag('health-condition')==4
cog.hp=saved_hp;app.art.update_health(actor,cog,0)
assert not app.hud.find('**/ttr_t_gui_bat_battleMenu_base_card-art').isEmpty()
app.gag_hover('Wedding Cake');assert app.detail_icon['image'] is not None
assert 'damage' in app.detail_text['text']
assert app.detail_icon.component('image0').getSx()<.1

# All 32 real Cog models assemble, including texture variants and multipart heads.
for name,data in COG_CATALOG.items():
 node=app.render.attachNewNode('test-cog');actor=app.art.cog(Cog(name,data['rank']),node)
 assert actor.getTightBounds()[1].z>0,name
 assert actor.hasPythonTag('health-light'),name
 actor.cleanup();app.art.actors.remove(actor);node.removeNode()
# Select through the same callbacks used by buttons.
app.game.roll=lambda chance:chance>0
app.select_toon(0);app.set_category('Lure');app.choose_action('Hypno-goggles');assert app.selected[0].gag=='Hypno-goggles'
app.resolve();assert app.animating;finish(app)
assert not app.game.lure_available
trap_stock=app.game.toons[0].stock.copy();trap_round=app.game.round
for name,g in GAGS.items():
 if g.track=='Trap':
  app.choose_action(name);assert 0 not in app.selected
assert app.game.toons[0].stock==trap_stock and app.game.round==trap_round

from direct.gui.DirectGui import DGG
assert all(app.gag_buttons[n]['state']==DGG.DISABLED for n,g in GAGS.items() if g.track in ('Lure','Trap'))
before=(app.game.round,app.game.toons[0].stock.copy())
app.choose_action('Hypno-goggles');assert 0 not in app.selected
assert 'already lured' in app.message
assert (app.game.round,app.game.toons[0].stock)==before
app.set_category('Sound');app.choose_action('Bike Horn');app.resolve();finish(app)
assert app.game.lure_available
# Targeted gag, no inventory spending before resolution.
app.choose_action('Cupcake');app.choose_target(2);assert app.selected[0].target==2
# Every support menu builds; pending single-target rewards can be targeted.
for category in CATEGORIES:
 app.open_rewards(category);assert app.modal==('fire' if category=='Fire' else 'rewards');app.close_modal()
app.select_reward('Damage remote 1★');app.choose_target(0);assert app.selected[0].gag=='Damage remote 1★'
planned_before=dict(app.selected);choice_before=app.choice;round_before=app.game.round;gags_before=app.game.toons[0].stock.copy()
app.open_unites();app.use_unite('Unite: Toon-Up 20');assert app.game.toons[0].unite_cooldown==3
assert app.selected==planned_before and app.choice==choice_before
assert app.game.round==round_before and app.game.toons[0].stock==gags_before
# Setup lazy pages retain edits and apply atomically.
start=time.perf_counter();app.open_setup();duration=time.perf_counter()-start
assert app.timer.paused
app.setup_department(0,'Bossbot');app.setup_cog(0,'Flunky');app.setup_level(0,'1')
app.setup_switch(0)
name_entry=app.setup_entries[0][0];name_entry.enterText('Panda Toon')
app.setup_next(1);assert app.setup_draft['toons'][0].name=='Panda Toon'
app.setup_entries[7][0].enterText('4')
app.apply_setup();assert app.modal=='setup' and 'limit' in app.setup_error['text']
app.setup_entries[7][0].enterText('3');app.apply_setup()
assert app.modal is None and not app.timer.paused
assert app.game.toons[0].name=='Panda Toon' and app.game.cogs[0].name=='Flunky'
# Timeout without choices passes, rather than firing default gags.
stock=app.game.toons[0].stock.copy();app.resolve(True);finish(app)
assert app.game.round==2 and app.game.toons[0].stock==stock
# Full inventory and sources are visible in Panda3D, with no Tk dependency.
app.open_log();app.close_modal();app.open_rules();app.close_modal()
for _ in range(3):app.taskMgr.step();app.graphicsEngine.renderFrame()
app.auto_advance=False  # This legacy scenario explicitly drives each Toon.
assert 'tkinter' not in sys.modules
app.destroy()
print(f'Panda3D integration passed: 32 Cog models, 49 gag images, selection, Lure/Sound, rewards, setup validation, timer, log. Setup opened in {duration:.3f}s.')
