"""Exercise every combat Unite, independent particles, tint and battle invariants."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from panda3d.core import loadPrcFileData,Vec4
loadPrcFileData('','audio-library-name null')
from panda_battle import PandaBattle
from battle_engine import Action
from support import UNITES
app=PandaBattle(offscreen=True,timed=False,seed=8)
out=Path('reports/unite-audit');out.mkdir(exist_ok=True)
try:
 for name in UNITES:
  app.new_battle();app.animating=True;app.make_hud()
  app.selected={0:Action(0,'Cupcake',0)}
  app.game.toons[0].hp=10;app.game.toons[1].escaped=True
  plans=app.selected.copy();state=app.game.rng.getstate();round_before=app.game.round
  scales=[Vec4(a['legs'].getColorScale()) for a in app.toon_actors]
  app.unite_caster=0;app.modal='unites';app.use_unite(name)
  assert app.selected==plans and app.game.round==round_before
  assert app.game.rng.getstate()==state
  assert app.game.toons[0].unite_cooldown==3 and app.game.toons[1].unite_cooldown==0
  root=app.render.find('**/unite-effect');assert not root.isEmpty()
  particle=root.getPythonTag('unite-particle');icons=root.getPythonTag('unite-icons')
  if 'Gag-Up' in name:
   assert len(icons)==6 and all(level<=6 for track,level in icons)
   if name.endswith(' All'):assert len({track for track,level in icons})==6
   else:assert all(track==name.removeprefix('Unite: Gag-Up ') for track,level in icons)
  effect=app.unite_intervals[-1];effect.pause();effect.setT(.5);particle.accelerate(.15)
  for pulse in app.unite_tints.values():pulse.pause();pulse.setT(.5)
  app.position_nametags()
  assert app.toon_actors[1]['legs'].getColorScale()==scales[1]
  app.clear_movie_props(include_unites=False);assert not root.isEmpty()
  if name in ('Unite: Toon-Up 20','Unite: Gag-Up All'):
   for _ in range(3):app.graphicsEngine.renderFrame()
   app.win.saveScreenshot(str((out/('heal.png' if 'Toon-Up 20' in name else 'restock.png')).resolve()))
  effect.finish();assert app.render.find('**/unite-effect').isEmpty()
  assert all(a['legs'].getColorScale().almostEqual(color) for a,color in zip(app.toon_actors,scales))
  app.animating=False
 # Two casters may activate independently; interrupted tint must still restore.
 app.new_battle();app.play_unite_effect(0,'Unite: Toon-Up 20',[0,1]);first=app.unite_intervals[-1]
 first.pause();first.setT(.4)
 app.play_unite_effect(1,'Unite: Gag-Up All',[0,1]);second=app.unite_intervals[-1]
 first.finish();second.finish()
 assert app.toon_actors[0]['legs'].getColorScale().almostEqual(Vec4(1))
 app.new_battle();assert app.render.find('**/unite-effect').isEmpty()
 print('13 combat Unites passed: resources, recipients, independent lifecycle, unchanged actions/round/RNG, tint restoration and overlap.')
finally:app.destroy()
