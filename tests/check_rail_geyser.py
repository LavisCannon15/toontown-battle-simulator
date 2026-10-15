import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from panda3d.core import loadPrcFileData
loadPrcFileData('','audio-library-name null')
from panda_battle import PandaBattle
from battle_engine import Action
app=PandaBattle(offscreen=True,timed=False,seed=1)
def shot(name):
 app.position_nametags()
 for _ in range(3):app.graphicsEngine.renderFrame()
 app.win.saveScreenshot(str(Path('reports',name+'.png').resolve()))
def sample(clip,t,name):
 clip.start();clip.pause();clip.setT(t);shot(name)
try:
 app.display_toon_hp=[t.hp for t in app.game.toons];app.display_cog_hp=[c.hp for c in app.game.cogs]
 app.animating=True;app.make_hud()
 clip=app.attack_caption(0,'Finger Wag',3);sample(clip,1,'attack-title-revised')
 assert app.ui.find('**/cog-attack-name').node().getText()=='FINGER WAG!'
 clip.finish();app.clear_movie_props()
 for c in app.game.cogs:c.trap=('Railroad',200)
 event={'kind':'gags','track':'Trap','actions':[Action(0,'Railroad',None)],'targets':{0:[0,1,2,3]},'health':[],'misses':[]}
 clip=app.gag_movie(event);sample(clip,2.2,'railroad-placement');clip.finish();app.clear_movie_props()
 assert app.railroad_root is not None and not app.railroad_root.isEmpty()
 for c in app.game.cogs:c.trap=None
 event={'kind':'gags','track':'Lure','actions':[Action(0,'Hypno-goggles',None)],'targets':{0:[0,1,2,3]},'health':[('cog',i,-1) for i in range(4)],'misses':[]}
 clip=app.gag_movie(event);sample(clip,5.1,'railroad-train');clip.finish();app.clear_movie_props()
 assert app.railroad_root is None
 event={'kind':'gags','track':'Squirt','actions':[Action(0,'Geyser',None)],'targets':{0:[0,1,2,3]},'health':[('cog',i,-1) for i in range(4)],'misses':[]}
 clip=app.gag_movie(event);sample(clip,3.6,'geyser-eruption')
 assert all(n.getZ()>0 for n in app.cog_nodes)
 clip.finish();assert all(abs(n.getZ())<.001 for n in app.cog_nodes)
 app.clear_movie_props()
 app.animating=False;app.new_battle()
 assert app.railroad_root is None and not app.railroad_targets
 app.game.hit_rounds=99
 app.selected={0:Action(0,'Railroad',None),1:Action(1,'Hypno-goggles',None)}
 app.resolve()
 for _ in range(120):
  if app.animation:app.animation.finish()
  for c in getattr(app,'live_departures',[]):
   if c.isPlaying():c.finish()
  app.taskMgr.step()
  if not app.animating:break
 assert not app.animating and app.railroad_root is None
 print('Title, Railroad placement/trigger/removal, Geyser lift/return passed.')
finally:app.destroy()
