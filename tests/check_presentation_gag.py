import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from panda3d.core import loadPrcFileData
loadPrcFileData('','audio-library-name null')
from panda_battle import PandaBattle
from battle_engine import Action
app=PandaBattle(offscreen=True,timed=False,seed=1)
try:
 app.display_toon_hp=[t.hp for t in app.game.toons];app.display_cog_hp=[c.hp for c in app.game.cogs]
 app.animating=True;app.make_hud()
 cues=[];original=app.sound_clip
 def sound(name,*args,**kwargs):cues.append(name);return original(name,*args,**kwargs)
 app.sound_clip=sound
 event={'kind':'gags','track':'Lure','actions':[Action(0,'Presentation',None)],'targets':{0:[0,1,2,3]},'health':[],'misses':[]}
 clip=app.gag_movie(event);clip.start();clip.pause();clip.setT(4)
 screen=app.render.find('**/battle-prop-slideshow')
 assert screen.getParent()==app.render and screen.getY()>app.toon_nodes[0].getY() and not screen.isHidden()
 assert 'TL_presentation.ogg' in cues and 'AA_drop_trigger_box.ogg' in cues and 'TL_hypnotize.ogg' not in cues
 app.position_nametags()
 for _ in range(3):app.graphicsEngine.renderFrame()
 app.win.saveScreenshot(str(Path('reports/presentation-screen.png').resolve()))
 clip.finish();assert screen.isHidden();app.clear_movie_props()
 app.animating=False;app.new_battle();app.game.hit_rounds=99
 app.selected={0:Action(0,'Railroad',None),1:Action(1,'Presentation',None)};app.resolve()
 for _ in range(160):
  for c in getattr(app,'live_departures',[]):
   if c.isPlaying():c.finish()
  if app.animation:app.animation.finish()
  app.taskMgr.step()
  if not app.animating:break
 assert not app.animating and app.railroad_root is None
 print('Presentation ground placement, screen reveal/removal and two timed source cues passed.')
finally:app.destroy()
