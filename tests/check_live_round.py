"""Real-model checks of impact-time health, emergency Unites, and v2 transitions."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from panda3d.core import loadPrcFileData
loadPrcFileData('','audio-library-name null\nwin-size 1200 800')
from panda_battle import PandaBattle
from battle_engine import Action,Cog
from battle_movies import MOVIES

def finish(app):
 for _ in range(150):
  for clip in getattr(app,'live_departures',[]):
   if clip.isPlaying():clip.finish()
  if app.animation:app.animation.finish()
  app.taskMgr.step()
  if not app.animating:return
 raise AssertionError('Playback stalled')

app=PandaBattle(seed=2,offscreen=True,timed=False)
app.game.cogs=[Cog('Mr. Hollywood',12)]
app.game.toons=app.game.toons[:1];app.game.toons[0].hp=1
app.spawn_characters();app.make_hud();app.game.roll=lambda chance:True
app.resolve()
assert app.animating and app.game.toons[0].hp==1,'Damage applied before its animation'
app.open_unites();assert app.modal=='unites'
app.use_unite('Unite: Toon-Up 80');assert app.game.toons[0].hp==81
finish(app)
assert app.game.toons[0].alive and app.game.round==2
assert app.display_toon_hp[0]==app.game.toons[0].hp
# A fatal impact immediately starts the sad animation before later events.
app.game.toons[0].hp=1;app.display_toon_hp[0]=1
app.live_health({'kind':'cog','cog':0,'name':'Power Trip','raw_toon_damage':{0:30}},'toon',0,-1)
assert not app.game.toons[0].alive
app.taskMgr.step()
assert app.toon_actors[0]['torso'].getCurrentAnim()=='lose'
for clip in app.live_departures:clip.finish()
app.live_departures=[]
app.game.toons[0].hp=100;app.game.cogs=[Cog('The Big Cheese',12,version2=True)]
app.spawn_characters();app.make_hud()
app.game.cogs[0].hp=1
app.game.toons[0].stock['Cupcake']=1
app.selected={0:Action(0,'Cupcake',0)};app.resolve();finish(app)
assert app.game.cogs[0].skelecog and app.game.cogs[0].hp==196
assert app.cog_actors[0].getPythonTag('skelecog')
assert not app.cog_nodes[0].isHidden()
# Loaded attack-specific clips must bind to the extracted skeletons.
for name in ('slip-forward','slip-backward','struggle'):
 for actor in app.toon_actors[0].values():
  assert actor.getNumFrames(name)>1,name
assert MOVIES['attack_timing']['powertrip']=={'impact':1.8,'reaction':'slip-forward','dodge_at':1.29,'dodge':'jump'}
for name in ('song-and-dance','speak'):
 assert app.cog_actors[0].getNumFrames(name)>1,name
# Held projectiles inherit the animated character's scale, and keep that world scale at release.
clip=app.projectile(0,0,'fruitpie',launch=2,flight=.3)
clip.start();clip.pause();clip.setT(.5)
prop=app.render.find('**/battle-prop-fruitpie')
hand=app.toon_actors[0]['torso'].find('**/joint_Rhold')
assert (prop.getScale(app.render)-hand.getScale(app.render)).length()<.001
scale=prop.getScale(app.render);clip.setT(2.1)
assert (prop.getScale(app.render)-scale).length()<.001
clip.finish();app.clear_movie_props()
app.destroy()
print('Live round passed: impact-time HP, emergency Unite, immediate sadness, v2 transformation and reaction rigs.')
