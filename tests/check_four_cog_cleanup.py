import sys,traceback
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from panda3d.core import loadPrcFileData,Vec3
loadPrcFileData('','audio-library-name null')
from panda_battle import PandaBattle,Cog
app=PandaBattle(offscreen=True,timed=False,seed=1)
try:
 for name,onset,impact in [('Spin',1.7,3.8),('Paradigm Shift',1.95,4.65),('Head Shrink',2.1,2.1)]:
  for fatal in (False,True):
   app.game.cogs=[Cog('Head Hunter' if name=='Head Shrink' else 'Spin Doctor',8)];app.spawn_characters()
   for t in app.game.toons:t.hp=100
   app.game.toons[0].hp=1 if fatal else 100
   app.display_toon_hp=[t.hp for t in app.game.toons];app.display_cog_hp=[c.hp for c in app.game.cogs]
   node=app.toon_nodes[0];pos=Vec3(node.getPos());heading=Vec3(node.getHpr());head=app.toon_actors[0]['torso'].find('**/def_head').getChild(0);scale=Vec3(head.getScale())
   targets=[0,1,2,3] if name=='Paradigm Shift' else [0]
   event=dict(kind='cog',cog=0,name=name,targets=targets,misses=[2] if len(targets)>1 else [],health=[('toon',t,-5) for t in targets if t!=2],live=True)
   c=app.cog_movie(event);c.start();c.pause()
   until=impact+.1 if fatal else 3.8
   for step in range(1,int(until*50)+1):
    at=step/50;c.setT(at)
    for n,r in enumerate(getattr(app,'live_departures',[])):
     # Freeze separately launched tracks at realistic elapsed time before impact.
     if at<impact and n==0:r.pause();r.setT(min(r.getDuration(),max(0,at-onset)))
   if fatal:
    assert app.game.toons[0].hp==0
    assert (node.getPos()-pos).length()<.001 and (node.getHpr()-heading).length()<.001
    assert (head.getScale()-scale).length()<.001
    if name=='Paradigm Shift':assert app.game.toons[1].hp==95 and app.game.toons[2].hp==100 and app.game.toons[3].hp==95
   c.pause()
   for r in getattr(app,'live_departures',[]):r.pause()
   app.live_departures=[];app.clear_movie_props()
   assert (node.getPos()-pos).length()<.001 and (node.getHpr()-heading).length()<.001
   assert (head.getScale()-scale).length()<.001
   assert not app.movie_props and not app.movie_particles
 app.game.cogs=[Cog('Money Bags',8)];app.spawn_characters()
 for misses in ([],[1,3],[0,1,2,3]):
  for t in app.game.toons:t.hp=100
  app.display_toon_hp=[100]*4;app.display_cog_hp=[app.game.cogs[0].hp]
  c=app.cog_movie(dict(kind='cog',cog=0,name='Money Talks',targets=[0,1,2,3],misses=misses,health=[('toon',t,-5) for t in range(4) if t not in misses],live=True));c.start();c.pause()
  wall=next(p for p,a in app.movie_props if p.getName()=='money-talks-wall')
  assert len(wall.getChildren())==15
  for step in range(1,int(c.getDuration()*50)+2):c.setT(min(step/50,c.getDuration()))
  c.finish()
  assert [t.hp for t in app.game.toons]==[100 if t in misses else 95 for t in range(4)]
  for r in getattr(app,'live_departures',[]):r.finish()
  app.live_departures=[];app.clear_movie_props()
 Path('work/four-cog-cleanup-result.txt').write_text('PASS: Spin, Paradigm Shift, Head Shrink fatal damage and mid-movie cancellation restore transforms; mixed group health remains independent; Money Talks full-team hit, mixed and all-miss wall/damage/cleanup.')
except Exception:
 Path('work/four-cog-cleanup-result.txt').write_text(traceback.format_exc());raise
finally:app.destroy()
