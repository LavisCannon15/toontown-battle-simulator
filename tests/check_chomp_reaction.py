import sys,traceback
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from panda3d.core import loadPrcFileData
loadPrcFileData('','audio-library-name null')
from panda_battle import PandaBattle
from battle_engine import Cog
from chomp_reaction import reaction
app=PandaBattle(offscreen=True,timed=False,seed=1)
try:
 r=reaction(app,0);r.start();r.pause()
 for n in range(1,150):r.setT(n/100)
 for a in app.toon_actors[0].values():
  if 'spit' in a.getAnimNames():assert a.getAnimControl('spit').getFrame()>0
 r.finish()
 for fatal in (False,True):
  app.new_battle();app.game.cogs=[Cog('Loan Shark',11)];app.spawn_characters();app.make_hud()
  app.game.toons[0].hp=1 if fatal else 100
  app.display_toon_hp=[t.hp for t in app.game.toons];app.display_cog_hp=[c.hp for c in app.game.cogs]
  before=app.game.toons[0].hp
  event=dict(kind='cog',cog=0,name='Chomp',targets=[0],misses=[],health=[('toon',0,-min(10,before))],raw_toon_damage={0:10},live=True)
  clip=app.cog_movie(event);clip.start();clip.pause()
  for step in range(1,459):clip.setT(step/100)
  assert app.game.toons[0].hp==before
  assert app.live_departures,'Chomp reaction did not start before damage'
  react=app.live_departures[0];react.pause();react.setT(1.29);react.resume()
  assert react.isPlaying()
  clip.setT(4.61)
  assert app.game.toons[0].hp==max(0,before-10)
  if fatal:
   assert not react.isPlaying()
   app.taskMgr.step()
   app.live_departures[-1].setT(.01)
   assert app.toon_actors[0]['torso'].getCurrentAnim()=='lose'
  for c in app.live_departures:
   if c.isPlaying():c.finish()
  clip.finish();app.clear_movie_props()
  print('PASS Chomp', 'fatal' if fatal else 'nonfatal',flush=True)
 app.new_battle();assert not app.live_departures
 app.game.cogs=[Cog('Loan Shark',11)];app.spawn_characters();app.make_hud()
 app.display_toon_hp=[100]*4;app.display_cog_hp=[app.game.cogs[0].hp]
 miss=dict(kind='cog',cog=0,name='Chomp',targets=[0],misses=[0],health=[],live=True)
 clip=app.cog_movie(miss);clip.start();clip.pause()
 for step in range(1,int(clip.getDuration()*100)):clip.setT(step/100)
 assert app.game.toons[0].hp==100 and not app.live_departures
 clip.finish();app.clear_movie_props()
 print('PASS Chomp native spit segments, 4.6s HP timing, immediate sadness, and reset cleanup.',flush=True)
except Exception:traceback.print_exc();raise
finally:app.destroy()
