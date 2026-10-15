import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from panda3d.core import loadPrcFileData,Vec3
loadPrcFileData('','audio-library-name null\nwin-size 960 600')
from panda_battle import PandaBattle
from battle_engine import GAGS,Action
from trap_movies import clear,sync
app=PandaBattle(offscreen=True,timed=False,seed=1)
out=Path('reports/gag-audit');out.mkdir(exist_ok=True)
def finish():
 for _ in range(200):
  for c in getattr(app,'live_departures',[]):
   if c.isPlaying():c.finish()
  if app.animation:app.animation.finish()
  app.taskMgr.step()
  if not app.animating:return
 raise AssertionError('Stalled battle')
try:
 app.animating=True;app.make_hud();rows=[]
 for name,g in GAGS.items():
  origins=[Vec3(n.getPos()) for n in app.toon_nodes]
  for miss in (False,True):
   app.display_toon_hp=[50]*4;app.display_cog_hp=[196]*4
   for c in app.game.cogs:c.trap=None;c.lure=0
   clear(app);app.sync_railroad()
   targets=([1,2,3] if g.group else [1]) if g.track=='Toon-Up' else ([0,1,2,3] if g.group else [0])
   if g.track=='Trap':
    for i in targets:app.game.cogs[i].trap=(name,100)
   event={'kind':'gags','track':g.track,'actions':[Action(0,name,targets[0])],'targets':{0:targets},'health':[],'misses':targets if miss else []}
   clip=app.gag_movie(event);clip.start();clip.pause()
   t={'Toon-Up':5.2,'Trap':2.8,'Lure':3,'Sound':2.55,'Throw':2.85,'Squirt':3,'Drop':4.6}[g.track]
   if name=='High Dive':t=6.5
   if name=='Presentation':t=4
   sample=min(t,clip.getDuration()-.01)
   # Advance across attachment/scale boundaries as actual playback does.
   for step in range(1,int(sample*30)+1):clip.setT(step/30)
   clip.setT(sample)
   for effect in app.movie_particles:effect.accelerate(.25)
   if not miss:
    app.position_nametags()
    for _ in range(3):app.graphicsEngine.renderFrame()
    app.win.saveScreenshot(str((out/(g.track+'-'+str(g.level)+'.png')).resolve()))
   clip.finish();app.clear_movie_props();clear(app);app.sync_railroad()
   assert all((n.getPos()-v).length()<.01 for n,v in zip(app.toon_nodes,origins)),name
  rows.append({'gag':name,'track':g.track,'level':g.level,'hit_and_miss_playback':'passed'})
 # Persistent traps and activation: actual events, not hand-written movie-only fixtures.
 app.animating=False
 for name,g in GAGS.items():
  if g.track!='Trap':continue
  app.new_battle();app.game.hit_rounds=99
  app.selected={0:Action(0,name,0)};app.resolve();finish()
  assert (app.railroad_root is not None) if g.level==7 else (0 in app.placed_traps),name
  app.selected={1:Action(1,'Presentation',None)};app.resolve();finish()
  assert not app.placed_traps and app.railroad_root is None,name
 (out/'coverage.json').write_text(json.dumps(rows,indent=2))
 print('49 gag hit/miss sequences, transform restoration, seven persistent Trap/Lure live rounds passed.')
finally:app.destroy()
