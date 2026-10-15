import sys,traceback,random
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from panda3d.core import loadPrcFileData,Vec3
loadPrcFileData('','audio-library-name null')
from panda_battle import PandaBattle,Cog
app=PandaBattle(offscreen=True,timed=False,seed=1)
try:
 for name,attack in [('Number Cruncher','Crunch'),('Downsizer','Downsize')]:
  for miss,cancel,lethal in [(False,False,False),(True,False,False),(False,True,False),(False,False,True)]:
   app.game.cogs=[Cog(name,7)];app.spawn_characters();app.game.toons[0].hp=3 if lethal else 100;app.presentation_rng=random.Random(123)
   app.display_toon_hp=[t.hp for t in app.game.toons];app.display_cog_hp=[c.hp for c in app.game.cogs]
   initial=Vec3(app.toon_nodes[0].getScale());rng=app.game.rng.getstate()
   c=app.cog_movie(dict(kind='cog',cog=0,name=attack,targets=[0],misses=[0] if miss else [],health=[] if miss else [('toon',0,-5)],live=True));c.start();c.pause()
   assert app.game.rng.getstate()==rng
   numbers=[n for n,a in app.movie_props if n.getName()=='crunch-held-number']
   if attack=='Crunch':assert 5<=len(numbers)<=9 and len(app.movie_particles)==len(numbers)+1
   for step in range(1,int((4.5 if cancel else c.getDuration())*100)+1):
    c.setT(step/100)
    if attack=='Crunch' and step==160:
     assert all(not n.isHidden() and n.getParent()==app.cog_actors[0].find('**/joint_Rhold') for n in numbers)
    if attack=='Downsize' and step==430 and not lethal:
     assert abs(app.toon_nodes[0].getSx()-(1 if miss else .4))<.001
   if cancel:c.pause()
   else:c.finish();assert app.game.toons[0].hp==(0 if lethal else 100 if miss else 95)
   for r in getattr(app,'live_departures',[]):r.pause() if cancel or lethal else r.finish()
   app.live_departures=[];app.clear_movie_props()
   if not lethal:assert (app.toon_nodes[0].getScale()-initial).length()<.001
   assert not app.movie_particles
 Path('work/crunch-downsize-result.txt').write_text('PASS: hit/miss, fatal/cancel, held numbers and effect counts, combat RNG isolation, Downsize scale and restoration, live damage and cleanup.')
except Exception:
 Path('work/crunch-downsize-result.txt').write_text(traceback.format_exc());raise
finally:app.destroy()
