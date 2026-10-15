import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from panda3d.core import loadPrcFileData
loadPrcFileData('','audio-library-name null')
from panda_battle import PandaBattle
app=PandaBattle(offscreen=True,timed=True,seed=1)
try:
 for when in (.2, 2.0):
  app.resolve()
  # Passing all Toons advances directly into the first Cog attack.
  assert app.animating
  # Complete empty planning-track events before exercising a real attack.
  for _ in range(30):
   if app.animation.getDuration()>2:break
   app.animation.finish()
  old_game=app.game;old_clip=app.animation
  old_clip.setT(min(when,old_clip.getDuration()*.5))
  assert app.animation is old_clip
  app.new_battle()
  assert app.game is not old_game and app.game.round==1
  assert not app.animating and app.animation is None and not old_clip.isPlaying()
  assert not app.timer.paused and not app.selected
  assert not app.movie_props and not app.movie_particles and not app.live_departures
  hp=[t.hp for t in app.game.toons]
  for _ in range(20):app.taskMgr.step()
  assert [t.hp for t in app.game.toons]==hp and app.game.round==1
  assert all(a.getCurrentAnim()=='idle' for a in app.cog_actors)
 print('New battle interrupts Cog wind-up/impact playback and resets the timer without old callbacks.')
finally:app.destroy()
