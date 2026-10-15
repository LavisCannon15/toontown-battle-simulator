import sys,traceback
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from panda3d.core import loadPrcFileData
loadPrcFileData('','audio-library-name null')
from panda_battle import PandaBattle,Cog
app=PandaBattle(offscreen=True,timed=False,seed=1)
try:
 for name,attack in [('Back Stabber','Guilt Trip'),('Downsizer','Sacked')]:
  for miss in (False,True):
   app.game.cogs=[Cog(name,7)];app.spawn_characters()
   for t in app.game.toons:t.hp=100
   app.display_toon_hp=[t.hp for t in app.game.toons];app.display_cog_hp=[c.hp for c in app.game.cogs]
   targets=[0,1,2,3] if attack=='Guilt Trip' else [0];misses=targets if miss else [3] if attack=='Guilt Trip' else []
   c=app.cog_movie(dict(kind='cog',cog=0,name=attack,targets=targets,misses=misses,health=[('toon',t,-5) for t in targets if t not in misses],live=True));c.start();c.pause()
   if attack=='Sacked':sack=next(n for n,a in app.movie_props if n.getName()=='battle-prop-sandbag')
   else:assert len(app.movie_particles)==3
   for step in range(1,int(c.getDuration()*100)+1):
    c.setT(step/100)
    if attack=='Sacked':
     if step==150:assert sack.getParent()==app.cog_actors[0].find('**/joint_Rhold')
     if step==320:assert sack.getParent()==app.render
     if step==400:
      assert sack.getParent()==(app.render if miss else app.toon_actors[0]['legs'].find('**/joint_hips'))
      if not miss:
       lo,hi=sack.getTightBounds(app.render);center=(lo+hi)*.5;pos=app.toon_nodes[0].getPos(app.render)
       assert abs(center.x-pos.x)<.05 and abs(center.y-pos.y)<.05
       assert 2<hi.z-lo.z<3.5 and lo.z>-.3,(lo,hi)
     if step==550 and not miss:assert app.game.toons[0].hp==100
    elif step==211:
     assert all(abs(e.getY()-15)<.01 for e in app.movie_particles[:2])
   c.finish()
   for t in targets:assert app.game.toons[t].hp==(100 if t in misses else 95)
   for r in getattr(app,'live_departures',[]):r.finish()
   app.live_departures=[];app.clear_movie_props();assert not app.movie_particles
 Path('work/guilt-sacked-result.txt').write_text('PASS: Guilt Trip mixed/all miss group health and moving bars; Sacked held/flight/wrap/miss states, delayed damage, cleanup.')
except Exception:
 Path('work/guilt-sacked-result.txt').write_text(traceback.format_exc());raise
finally:app.destroy()
