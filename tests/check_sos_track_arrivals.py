import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from panda3d.core import loadPrcFileData
loadPrcFileData('','audio-library-name null')
from panda_battle import PandaBattle
from battle_engine import Action
import sos_movies
app=PandaBattle(offscreen=True,timed=False,seed=1)
real_arrival=sos_movies.arrival;arrivals=[]
def checked_arrival(app,action):
 current=[g['track'] for g in getattr(app,'sos_guests',{}).values()]
 track=sos_movies.SOS[action.gag][0]
 assert all(t==track for t in current),(track,current)
 arrivals.append(track)
 return real_arrival(app,action)
sos_movies.arrival=checked_arrival
try:
 for reverse in (False,True):
  app.new_battle();app.auto_resolve=False
  names=['SOS: Clerk Clara','SOS: Lil Oldman']
  if reverse:names.reverse()
  stock=[app.game.toons[i].rewards[n] for i,n in enumerate(names)]
  app.selected={i:Action(i,n) for i,n in enumerate(names)};arrivals.clear();app.resolve()
  for step in range(160):
   for clip in getattr(app,'live_departures',[]):
    if clip.isPlaying():clip.finish()
   if app.animation:app.animation.finish()
   app.taskMgr.step()
   if not app.animating:break
  assert not app.animating
  assert arrivals==['Trap','Lure'],arrivals
  assert not app.sos_guests
  assert not app.placed_traps
  assert all(app.game.toons[i].rewards[n]==stock[i]-1 for i,n in enumerate(names))
 # Early consumption must not create any guest; reset cannot leak a waiting NPC.
 app.new_battle();app.selected={0:Action(0,'SOS: Lil Oldman')}
 clip=sos_movies.support_movie(app,app.selected[0],dict(kind='support',health=[]))
 assert clip.getDuration()==0 and not app.sos_guests
 app.new_battle();assert not app.sos_guests
 print('Trap guest completes before Lure guest in either caller order; trap activation, single card consumption and reset passed.')
finally:sos_movies.arrival=real_arrival;app.destroy()
