"""Resource panel anchors, manual advance, trap sounds and single Lure approach."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from panda3d.core import loadPrcFileData,Vec3
loadPrcFileData('','audio-library-name null\nwin-size 1440 900')
from panda_battle import PandaBattle
from battle_engine import Action,GAGS
from trap_movies import sync,clear,trap_position
app=PandaBattle(offscreen=True,timed=False,seed=1)
try:
 app.auto_resolve=False
 assert len(app.hud.findAllMatches('**/ttr_t_gui_bat_toonGUI_base_card-art'))==4
 assert app.hud.find('**/ToonBtl_Status_BG-art').isEmpty()
 app.choose_action('Cupcake');assert app.active==0
 app.cancel_choice();assert app.active==0
 app.choose_action('Cupcake');app.choose_target(0);assert app.active==1 and app.selected[0].target==0
 app.auto_modes[2]=True
 app.choose_action('Pass');assert app.active==3
 app.choose_action('Pass');assert app.active==3
 app.toggle_auto_advance();app.select_toon(0);app.choose_action('Pass');assert app.active==0
 app.toggle_auto_advance();app.selected.clear();app.game.toons[1].escaped=True
 app.choose_action('Pass');assert app.active==3
 app.new_battle();app.auto_modes=[False]*4;app.select_toon(0)
 app.choose_action('Cupcake');app.choose_target(0)
 for _ in range(3):app.graphicsEngine.renderFrame()
 app.win.saveScreenshot(str(Path('work/trap-panel-2026-09-20/panels.png').resolve()))
 sounds=[];real_sound=app.sound_clip
 def sound(name,*a,**kw):sounds.append(name);return real_sound(name,*a,**kw)
 app.sound_clip=sound
 for name in ('Banana Peel','Rake','Marbles','Quicksand','Trapdoor','TNT'):
  app.new_battle();app.auto_resolve=False
  g=GAGS[name];app.game.cogs[0].trap=(name,10);sounds.clear()
  event=dict(kind='gags',track='Trap',actions=[Action(0,name,0)],targets={0:[0]},health=[],misses=[])
  clip=app.base_gag_movie(event);clip.start();clip.pause()
  for step in range(1,int(clip.getDuration()*30)+1):clip.setT(step/30)
  clip.finish()
  assert 0 in app.placed_traps,name
  assert (app.placed_traps[0][0].getPos()-trap_position(app,0,g.level)).length()<.001,name
  expected={'Banana Peel':'TL_banana.ogg','Rake':'TL_rake_throw_only.ogg','Marbles':'TL_marbles.ogg','Quicksand':'TL_quicksand.ogg','Trapdoor':'TL_trap_door.ogg','TNT':'TL_dynamite.ogg'}[name]
  assert expected in sounds and 'AA_pie_throw_only.ogg' not in sounds,(name,sounds)
  app.clear_movie_props()
  for lure in ('Small Magnet','Hypno-goggles','Presentation','$1 Bill'):
   if lure not in GAGS:continue
   app.cog_nodes[0].setPos(-3.6,3.7,0);app.game.cogs[0].trap=(name,10);sync(app)
   before=app.game.cogs[0].hp;app.display_cog_hp=[c.hp for c in app.game.cogs];app.display_toon_hp=[t.hp for t in app.game.toons]
   app.game.cogs[0].trap=None;app.game.cogs[0].lure=0
   event=dict(kind='gags',track='Lure',actions=[Action(0,lure,0)],targets={0:[0]},health=[('cog',0,-10)],misses=[],trap_before=[(name,10),None,None,None],lure_before=[0]*4)
   clip=app.base_gag_movie(event);clip.start();clip.pause()
   advanced=False
   for step in range(1,int(clip.getDuration()*30)+1):
    clip.setT(step/30)
    # There is no separate forward walk after the Lure; the only walk is recovery.
    if app.cog_nodes[0].getY()<3.6:advanced=True
    if app.cog_actors[0].getCurrentAnim()=='walk':assert app.display_cog_hp[0]<before,(name,lure,'walk before damage')
   clip.finish();assert advanced,(name,lure)
   assert abs(app.cog_nodes[0].getY()-3.7)<.001,(name,lure)
   assert app.display_cog_hp[0]==before-10,(name,lure)
   assert not app.placed_traps
   app.clear_movie_props()
 print('TTR panel, advance toggle, six Trap sounds/positions and 24 Trap/Lure combinations passed.')
finally:app.destroy()
