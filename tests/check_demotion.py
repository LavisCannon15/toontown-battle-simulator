import sys,traceback
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from panda3d.core import loadPrcFileData
loadPrcFileData('','audio-library-name null')
from panda_battle import PandaBattle,Cog
from demotion_movie import reaction
app=PandaBattle(offscreen=True,timed=False,seed=1)
try:
 app.game.cogs=[Cog('Micromanager',5)];app.spawn_characters()
 r=reaction(app,0);r.start();r.pause();r.setT(2.2)
 frame=app.toon_actors[0]['torso'].getCurrentFrame('cringe');r.setT(4.5)
 assert app.toon_actors[0]['torso'].getCurrentFrame('cringe')==frame
 r.finish()
 for miss,lethal,cancel in [(False,False,False),(True,False,False),(False,True,False),(False,False,True)]:
  app.game.toons[0].hp=3 if lethal else 100;app.spawn_characters()
  app.display_toon_hp=[t.hp for t in app.game.toons];app.display_cog_hp=[c.hp for c in app.game.cogs]
  c=app.cog_movie(dict(kind='cog',cog=0,name='Demotion',targets=[0],misses=[0] if miss else [],health=[] if miss else [('toon',0,-5)],live=True));c.start();c.pause()
  assert len(app.movie_particles)==(1 if miss else 3)
  if not miss:
   assert app.movie_particles[1].getZ()==app.movie_particles[2].getZ()
   assert 1<app.movie_particles[1].getZ()<3
  for step in range(1,int((3 if cancel else c.getDuration())*100)+1):
   c.setT(step/100)
   if step==220:assert app.game.toons[0].hp==(3 if lethal else 100)
   if step==240:assert app.game.toons[0].hp==(0 if lethal else 100 if miss else 95)
  if cancel:c.pause()
  else:c.finish()
  for track in getattr(app,'live_departures',[]):track.pause() if cancel or lethal else track.finish()
  app.live_departures=[];app.clear_movie_props();assert not app.movie_particles
 Path('work/demotion-result.txt').write_text('PASS: frozen-pose hold, face effects, hit/miss, health timing, fatal hit and cancellation cleanup.')
except Exception:
 Path('work/demotion-result.txt').write_text(traceback.format_exc());raise
finally:app.destroy()
