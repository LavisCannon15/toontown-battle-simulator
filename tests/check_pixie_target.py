import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from panda3d.core import loadPrcFileData,Vec3
loadPrcFileData('','audio-library-name null')
from panda_battle import PandaBattle
from battle_engine import Action
app=PandaBattle(offscreen=True,timed=False)
try:
 for caller in range(4):
  for target in range(4):
   if caller==target:continue
   origin=Vec3(app.toon_nodes[caller].getPos());heading=Vec3(app.toon_nodes[caller].getHpr())
   event=dict(kind='gags',track='Toon-Up',actions=[Action(caller,'Pixie Dust',target)],targets={caller:[target]},health=[],misses=[])
   clip=app.base_gag_movie(event);clip.start();clip.pause()
   for step in range(1,145):clip.setT(step/30)
   node=app.toon_nodes[caller];direction=app.toon_nodes[target].getPos(app.render)-node.getPos(app.render);direction.z=0;direction.normalize()
   throw_direction=node.getQuat(app.render).xform(Vec3(1,0,0));throw_direction.z=0;throw_direction.normalize()
   assert throw_direction.dot(direction)>.999,(caller,target,throw_direction,direction)
   for name in ('pixieDrop','pixiePoof'):
    effect=next(e for e in app.movie_particles if e.getName()=='source-effect-'+name)
    assert effect.getParent()==app.toon_nodes[target],(caller,target,name)
   clip.finish();assert (node.getPos()-origin).length()<.001 and (node.getHpr()-heading).length()<.001
   app.clear_movie_props()
 print('All 12 Pixie Dust caller/recipient pairs face correctly, use target drop/poof, and restore formation.')
finally:app.destroy()
