import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from panda3d.core import loadPrcFileData
loadPrcFileData('','audio-library-name null')
from direct.interval.IntervalGlobal import Sequence,Func,Wait
from panda_battle import PandaBattle
from battle_engine import Action
app=PandaBattle(offscreen=True,timed=False)
try:
 for count in (1,4):
  app.new_battle();calls=[];now=[0]
  def sound(name,duration=None,**kw):
   return Sequence(Func(lambda:calls.append((now[0],'start',name))),Wait(duration or 1),Func(lambda:calls.append((now[0],'stop',name))))
  app.sound_clip=sound
  for i in range(count):app.game.cogs[i].trap=('Trapdoor',10)
  event=dict(kind='gags',track='Trap',actions=[Action(i,'Trapdoor',i) for i in range(count)],targets={i:[i] for i in range(count)},health=[],misses=[])
  clip=app.base_gag_movie(event);clip.start();clip.pause()
  for step in range(1,int(clip.getDuration()*100)+1):now[0]=step/100;clip.setT(now[0])
  clip.finish()
  starts=[(t,n) for t,k,n in calls if k=='start'];assert len(starts)==2,starts
  button_end=next(t for t,k,n in calls if k=='stop' and n=='AA_drop_trigger_box.ogg')
  trap_start=next(t for t,k,n in calls if k=='start' and n=='TL_trap_door.ogg')
  assert trap_start-button_end>=.29,calls
  app.clear_movie_props()
 print('Single and four-Toon Trapdoor placement: one button, one opening sound, no overlap, .3-second gap.')
finally:app.destroy()
