import sys,traceback
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from panda3d.core import loadPrcFileData
loadPrcFileData('','audio-library-name null')
from panda_battle import PandaBattle
from battle_engine import Action
from sos_movies import arrival,remove
from sos_visuals import gag_performance
app=PandaBattle(offscreen=True,timed=False,seed=1)
try:
 app.display_cog_hp=[c.hp for c in app.game.cogs]
 c=arrival(app,Action(0,'SOS: Lil Oldman'));c.start();c.finish()
 guest=app.sos_guests[0];c=gag_performance(app,0,guest)
 assert guest['impact']==1.6
 assert any(n.getName()=='battle-prop-hypno-goggles' for n,a in app.movie_props)
 assert 'Actor-hypnotize' in str(c)
 c.start();c.pause();c.setT(1)
 goggles=next(n for n,a in app.movie_props if n.getName()=='battle-prop-hypno-goggles')
 assert not goggles.isHidden()
 assert goggles.getParent()==guest['actors']['torso'].find('**/joint_Lhold')
 c.finish();remove(app,0);app.clear_movie_props()
 app.new_battle();app.selected={0:Action(0,'SOS: Lil Oldman')};app.resolve()
 for _ in range(160):
  for c in getattr(app,'live_departures',[]):
   if c.isPlaying():c.finish()
  if app.animation:app.animation.finish()
  app.taskMgr.step()
  if not app.animating:break
 assert not app.animating and not app.sos_guests
 assert all(a.getCurrentAnim()=='idle' for a in app.cog_actors),str([(c.lure,getattr(c,'lure_pose',None),a.getCurrentAnim()) for c,a in zip(app.game.cogs,app.cog_actors)])
 for cog in app.game.cogs: cog.lure_pose='hypnotized'
 for i in range(len(app.game.cogs)):app.restore_cog_pose(i)
 assert all(a.getCurrentAnim()=='idle' for a in app.cog_actors)
 assert all(c.lure>0 for c in app.game.cogs)
 app.finish_round()
 assert all(a.getCurrentAnim()=='idle' for a in app.cog_actors)
 Path('work/oldman-pose-result.txt').write_text('PASS: Lil Oldman reaction completes; stale Hypno pose cannot loop; lure status persists.')
except Exception:
 Path('work/oldman-pose-result.txt').write_text(traceback.format_exc());raise
finally:app.destroy()
