import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from panda3d.core import loadPrcFileData
loadPrcFileData('','audio-library-name null')
from panda_battle import PandaBattle
app=PandaBattle(offscreen=True,timed=False,seed=1)
try:
 app.game.toons=app.game.toons[:1];app.spawn_characters()
 for kind,track,index in [('gags','Throw',3),('gags','Lure',3),('cog',None,0)]:
  app.display_toon_hp=[100];app.display_cog_hp=[c.hp for c in app.game.cogs]
  event={'kind':kind,'track':track,'name':'Finger Wag','health':[],'misses':[index,index]}
  movie=app.health_movie(event,1);movie.start();movie.pause();movie.setT(1.5)
  parent=(app.toon_nodes if kind=='cog' else app.cog_nodes)[index]
  texts=[n for n,e in app.floating_effects if not n.isEmpty() and not n.isHidden() and n.getParent()==parent]
  assert len(texts)==1
  assert texts[0].node().getText()=='MISSED'
  assert texts[0].getZ()>(1.5 if kind=='cog' else 2)
  if track=='Lure':assert app.cog_actors[3].getCurrentAnim()=='idle'
  movie.finish();assert texts[0].isEmpty()
 assert app.game.toons[0].hp==100
 print('Cog/gag miss text rises and cleans up; duplicate suppression, Lure idle, and 1-Toon/4-Cog case passed.')
finally:app.destroy()
