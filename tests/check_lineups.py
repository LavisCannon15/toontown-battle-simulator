"""All party/enemy counts, original skeleton models, and absent-slot input safety."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from panda3d.core import loadPrcFileData
loadPrcFileData('','audio-library-name null')
from panda_battle import PandaBattle
from battle_engine import Cog,COG_CATALOG
def finish(app):
 for _ in range(200):
  for clip in getattr(app,'live_departures',[]):
   if clip.isPlaying():clip.finish()
  if app.animation:app.animation.finish()
  app.taskMgr.step()
  if not app.animating:return
 raise AssertionError('Lineup playback stalled')
app=PandaBattle(seed=1,offscreen=True,timed=False)
for name,data in COG_CATALOG.items():
 node=app.render.attachNewNode('skeleton-test');actor=app.art.cog(Cog(name,data['rank'],skelecog=True),node)
 assert actor.getCurrentAnim()=='idle'
 assert actor.hasPythonTag('health-light') and not actor.find('**/tie').isEmpty()
 actor.cleanup();app.art.actors.remove(actor);node.removeNode()
for toons in range(1,5):
 for cogs in range(1,5):
  app.open_setup();app.setup_count('toon_count',toons);app.setup_count('cog_count',cogs)
  for t in app.setup_draft['toons']:t.hp=t.maximum
  app.setup_form(0,'Skelecog');app.apply_setup()
  assert app.modal is None,(toons,cogs)
  assert len(app.game.toons)==len(app.toon_nodes)==len(app.laff_faces)==len(app.auto_modes)==toons
  assert len(app.game.cogs)==len(app.cog_nodes)==len(app.nametags)==cogs
  assert app.game.cogs[0].skelecog
  assert abs(sum(n.getX() for n in app.toon_nodes))<.01
  assert abs(sum(n.getX() for n in app.cog_nodes))<.01
  if toons<4:
   app.select_toon(3);app.toggle_auto(3);assert app.active==0
  if toons==1:
   assert app.game.targets(0,'Feather')==[]
   from battle_engine import Action
   try:app.game.validate(Action(0,'Feather',0));raise AssertionError('Solo self-heal accepted')
   except ValueError:pass
  app.choose_action('Bike Horn');app.resolve()
  finish(app)
  assert app.game.round==2
# Reducing a party removes automated slots; expanding restores safe manual slots.
app.new_battle();app.toggle_auto(3);app.open_setup();app.setup_count('toon_count',1);app.apply_setup()
assert app.auto_modes==[False];app.update_auto()
app.open_setup();app.setup_count('toon_count',4);app.apply_setup();assert app.auto_modes==[False]*4
app.destroy()
print('Lineup checks passed: all 16 party/Cog counts, 32 Skelecog mappings, solo healing, centered models, and Auto slot resizing.')
