import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from panda3d.core import loadPrcFileData,Vec3
loadPrcFileData('','audio-library-name null')
from panda_battle import PandaBattle
from battle_engine import Action,GAGS
app=PandaBattle(offscreen=True,timed=False,seed=1)
try:
 count=0
 for name,gag in GAGS.items():
  if gag.track=='Toon-Up':continue
  for miss in (False,True):
   targets=[0,1,2,3] if gag.group else [3]
   event={'kind':'gags','track':gag.track,'actions':[Action(0,name,None if gag.group else 3)],'targets':{0:targets},'health':[],'misses':targets if miss else []}
   node=app.toon_nodes[0];original=Vec3(node.getHpr())
   movie=app.gag_movie(event);movie.start();movie.pause();movie.setT(.1)
   target=sum((app.cog_nodes[i].getPos() for i in targets),Vec3(0,0,0))/len(targets)
   direction=target-node.getPos();direction.z=0;direction.normalize()
   assert node.getQuat().getForward().dot(direction)>.999,(name,node.getH())
   movie.finish();assert (node.getHpr()-original).length()<.001,name
   app.clear_movie_props();count+=1
 print(count,'hit/miss gag movies face single/group targets and restore the original heading.')
finally:app.destroy()
