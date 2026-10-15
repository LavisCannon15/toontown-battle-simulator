import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from battle_engine import Battle,Action
from support import REMOTES
b=Battle(seed=1)
actions=[Action(0,'Damage remote 1★',0),Action(1,'Healing remote 2★',1),Action(2),Action(3)]
for a in actions:b.plan(a)
events=b.resolve_events();event=next(events)
assert event['kind']=='support' and event['actions']==actions[:2]
assert b.cogs[0].remote==REMOTES[actions[0].gag] and b.cogs[1].remote==REMOTES[actions[1].gag]
assert all(b.toons[a.toon].rewards[a.gag]==1 for a in actions[:2])
events.close()
from panda3d.core import loadPrcFileData
loadPrcFileData('','audio-library-name null')
from panda_battle import PandaBattle
app=PandaBattle(offscreen=True,timed=False,seed=1)
try:
 app.selected={a.toon:a for a in actions};app.resolve()
 clip=app.animation;clip.pause();clip.setT(1.2)
 for i in (0,1):
  assert app.toon_actors[i]['torso'].getAnimControl('remoteAttack').getFrame()>0
  assert app.cog_actors[i].getAnimControl('seizecontrol').getFrame()>0
 assert len(app.movie_sounds)==2  # Toon remote and Cog takeover are separate cues.
 app.new_battle();assert not clip.isPlaying() and not app.movie_props
 print('Two distinct remote targets share one event; both Toon/Cog animations run together, with separate Toon/Cog sounds and safe interruption.')
finally:app.destroy()
