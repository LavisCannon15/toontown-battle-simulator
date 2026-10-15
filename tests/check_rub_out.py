import sys,traceback
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from panda3d.core import loadPrcFileData,ColorScaleAttrib,TransparencyAttrib
loadPrcFileData('','audio-library-name null')
from panda_battle import PandaBattle,Cog
app=PandaBattle(offscreen=True,timed=False,seed=1)
try:
 for miss,cancel,lethal in [(False,False,False),(True,False,False),(False,True,False),(False,False,True)]:
  app.game.cogs=[Cog('Pencil Pusher',5)];app.spawn_characters();app.game.toons[0].hp=3 if lethal else 100
  meshes=list(app.toon_nodes[0].findAllMatches('**/+GeomNode'));colors={m:m.getAttrib(ColorScaleAttrib) for m in meshes};transparency={m:m.getAttrib(TransparencyAttrib) for m in meshes};faded=[]
  app.display_toon_hp=[t.hp for t in app.game.toons];app.display_cog_hp=[c.hp for c in app.game.cogs]
  e=dict(kind='cog',cog=0,name='Rub Out',targets=[0],misses=[0] if miss else [],health=[] if miss else [('toon',0,-5)],live=True)
  c=app.cog_movie(e);c.start();c.pause()
  props={n.getName():n for n,a in app.movie_props}
  assert len(app.movie_particles)==(0 if miss else 3)
  if not miss:
   heights=[p.getZ() for p in app.movie_particles];assert heights[0]>heights[1]>heights[2],heights
  for step in range(1,int((3 if cancel else c.getDuration())*50)+1):
   c.setT(step/50)
   if step==80:
    assert props['battle-prop-pencil'].getParent()==app.cog_actors[0].find('**/joint_Rhold')
    assert props['battle-prop-pad'].getParent()==app.cog_actors[0].find('**/joint_Lhold')
   if step in (125,155,185) and not miss and not lethal:
    faded.append(sum(m.getColorScale().w<.01 for m in meshes))
   if step==150 and not miss and not lethal:assert any(m.getAttrib(ColorScaleAttrib)!=colors[m] for m in meshes)
  if not miss and not lethal and not cancel:assert 0<faded[0]<faded[1]<faded[2],faded
  if cancel:c.pause()
  else:c.finish();assert app.game.toons[0].hp==(0 if lethal else 100 if miss else 95)
  for r in getattr(app,'live_departures',[]):r.pause()
  app.live_departures=[];app.clear_movie_props()
  assert all(m.isEmpty() or m.getAttrib(ColorScaleAttrib)==colors[m] for m in meshes)
  assert all(m.isEmpty() or m.getAttrib(TransparencyAttrib)==transparency[m] for m in meshes)
  assert not app.movie_particles
 Path('work/rub-out-result.txt').write_text('PASS: hit/miss, eraser particle heights, hand attachments, live damage, lethal hit, color restore and cancellation cleanup.')
except Exception:
 Path('work/rub-out-result.txt').write_text(traceback.format_exc());raise
finally:app.destroy()
