import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from panda3d.core import loadPrcFileData
loadPrcFileData('','audio-library-name null')
from panda_battle import PandaBattle
from battle_engine import Action
app=PandaBattle(offscreen=True,timed=False,seed=1)
try:
 for gag in ('Small Magnet','Big Magnet'):
  app.new_battle();app.game.roll=lambda _:True
  app.selected={0:Action(0,gag)};app.resolve()
  checked=False
  for _ in range(160):
   if app.game.movie_events and app.game.movie_events[-1].get('track')=='Lure' and not checked:
    timeline=str(app.animation)
    assert 'Actor-landing' in timeline
    assert 'Actor-hypnotized' not in timeline,timeline
    checked=True
   for clip in getattr(app,'live_departures',[]):
    if clip.isPlaying():clip.finish()
   if app.animation:app.animation.finish()
   app.taskMgr.step()
   if not app.animating:break
  assert checked and not app.animating
  assert all(c.lure_pose=='idle' for c in app.game.cogs)
  assert all(a.getCurrentAnim()=='idle' for a in app.cog_actors)
 print('Full live rounds: both magnets have landing reaction, no queued Hypno transition, neutral end pose.')
finally:app.destroy()
