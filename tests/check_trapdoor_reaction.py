import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from panda3d.core import loadPrcFileData,Vec3
loadPrcFileData('','audio-library-name null\nwin-size 1440 900')
from panda_battle import PandaBattle
from battle_engine import Action,Cog
from trap_movies import sync,trapdoor_reaction,return_to_formation,clear
from direct.interval.IntervalGlobal import Sequence
app=PandaBattle(offscreen=True,timed=False)
try:
 app.game.cogs=[Cog('Mr. Hollywood',8),Cog('Pencil Pusher',3),Cog('Flunky',1)];app.spawn_characters()
 for c in app.game.cogs:c.trap=('Trapdoor',10)
 sync(app);app.animating=True;app.make_hud()
 for i in range(3):
  prop=app.placed_traps[i][0];lo,hi=prop.getTightBounds(app.render)
  assert lo.z>.06,(i,lo)
  assert hi.x-lo.x>.6
 for _ in range(3):app.graphicsEngine.renderFrame()
 app.win.saveScreenshot(str(Path('work/trapdoor-reaction/placed.png').resolve()))
 for i in range(3):
  prop=app.placed_traps[i][0];node=app.cog_nodes[i];origin=Vec3(node.getPos())
  node.setY(prop.getY());app.display_cog_hp=[c.hp for c in app.game.cogs];before=app.display_cog_hp[i]
  event=dict(kind='gags',track='Lure',health=[('cog',i,-1)],misses=[])
  clip=Sequence(trapdoor_reaction(app,event,i,prop,origin),return_to_formation(app,i,origin))
  clip.start();clip.pause()
  for step in range(1,145):
   t=step/30;clip.setT(t)
   if abs(t-1)<.001:assert prop.getColor().x==0
   if abs(t-2.8)<.001:assert node.isHidden()
   if abs(t-3.6)<.001:assert app.display_cog_hp[i]==before-1
   if abs(t-4.3)<.001:assert not node.isHidden() and node.getZ()>0
   if abs(t-4.6)<.001:assert abs(node.getZ()-origin.z)<.001
  clip.finish();assert (node.getPos()-origin).length()<.001 and not node.isHidden()
 app.clear_movie_props();clear(app)
 # Interruption while underground must not leave a hidden Cog in the next battle.
 app.new_battle();app.game.cogs[0].trap=('Trapdoor',10);sync(app)
 prop=app.placed_traps[0][0];node=app.cog_nodes[0];origin=Vec3(node.getPos())
 app.display_cog_hp=[c.hp for c in app.game.cogs]
 app.animation=trapdoor_reaction(app,dict(kind='gags',track='Lure',health=[],misses=[]),0,prop,origin)
 app.animating=True;app.animation.start();app.animation.pause();app.animation.setT(2.8)
 app.new_battle();assert all(not n.isHidden() and abs(n.getZ())<.001 for n in app.cog_nodes)
 print('Trapdoor visible above floor; A/B/C wind-up, fall, hidden interval, landing, single damage, return and New battle reset passed.')
finally:app.destroy()
