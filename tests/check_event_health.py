"""Compare live mixed-reward playback to independent headless resolution."""
import sys
from copy import deepcopy
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from panda3d.core import loadPrcFileData
loadPrcFileData('','audio-library-name null')
from panda_battle import PandaBattle
from battle_engine import Action

def finish(app):
 for _ in range(350):
  for clip in getattr(app,'live_departures',[]):
   if clip.isPlaying():clip.finish()
  if app.animation:app.animation.finish()
  app.taskMgr.step()
  if not app.animating:return
 raise AssertionError('Round playback stalled')

cases=[
 ('Rocky + Throw',[(0,'SOS: Rocky'),(1,'Cupcake',0)]),
 ('Loopy + Squirt',[(0,'SOS: Loopy Loopenloop'),(1,'Squirting Flower',0)]),
 ('Flippy + two healers',[(0,'SOS: Flippy'),(1,'Feather',2),(2,'Feather',3)]),
 ('Bessie + Drop',[(0,'SOS: Barnacle Bessie'),(1,'Flower Pot',0)]),
 ('Lil Oldman + Lure',[(0,'SOS: Lil Oldman'),(1,'Big Magnet')]),
 ('Two SOS healers',[(0,'SOS: Flippy'),(1,'SOS: Daffy Don'),(2,'Feather',0)]),
 ('Two SOS sound + gag',[(0,'SOS: Barbara Seville'),(1,'SOS: Sid Sonata'),(2,'Bike Horn')]),
 ('Two SOS Drop',[(0,'SOS: Clumsy Ned'),(1,'SOS: Franz Neckvein'),(2,'Flower Pot',0)]),
 ('Two SOS Throw',[(0,'SOS: Rocky'),(1,'SOS: Rocky'),(2,'Cupcake',0)]),
 ('SOS Lure triggers Trap',[(0,'TNT',0),(1,'SOS: Lil Oldman')]),
 ('SOS Lure triggers Railroad',[(0,'Railroad'),(1,'SOS: Lil Oldman')]),
]
app=PandaBattle(offscreen=True,timed=False,seed=1)
try:
 for label,choices in cases:
  app.new_battle();app.auto_resolve=False
  app.game.roll=lambda chance:chance>0;app.game.cog_phase=lambda:None
  for t in app.game.toons:t.hp=10
  for c in app.game.cogs:c.hp=c.maximum=196
  actions={i:Action(i) for i in range(4)}
  actions.update({a[0]:Action(*a) for a in choices})
  expected=deepcopy(app.game)
  for a in actions.values():expected.plan(a)
  expected.resolve()
  app.selected=actions;app.resolve();finish(app)
  for attr,display in [('toons',app.display_toon_hp),('cogs',app.display_cog_hp)]:
   health=[v.hp for v in getattr(expected,attr)]
   assert health==[v.hp for v in getattr(app.game,attr)],(label,attr,'engine',health)
   assert health==display,(label,attr,'display',health,display)
  assert [c.lure for c in expected.cogs]==[c.lure for c in app.game.cogs],label
  assert [c.trap for c in expected.cogs]==[c.trap for c in app.game.cogs],label
  assert not app.movie_particles and not app.movie_props,label
  assert not app.sos_guests,label
  print('PASS:',label,flush=True)
 print(f'Mixed SOS/gag playback matches headless health, statuses, and cleanup in all {len(cases)} cases.',flush=True)
finally:app.destroy()
