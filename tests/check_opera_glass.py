import sys,traceback
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from panda3d.core import loadPrcFileData
from direct.interval.IntervalGlobal import Sequence,Func
loadPrcFileData('','audio-library-name null')
from panda_battle import PandaBattle
from battle_engine import Action
from battle_movies import MOVIES,SOURCE
app=PandaBattle(offscreen=True,timed=False,seed=1)
try:
 name='AA_sound_Opera_Singer_Cog_Glass.ogg'
 assert (SOURCE/MOVIES['audio'][name]).read_bytes()[:4]==b'OggS'
 for count,misses in [(1,[]),(4,[]),(2,[1,3]),(1,[0,1,2,3])]:
  app.spawn_characters();app.display_cog_hp=[c.hp for c in app.game.cogs];sounds=[];health=[];now=[0]
  original_sound=app.sound_clip;original_health=app.live_health
  def sound(file,duration=None):
   clip=original_sound(file,duration)
   return Sequence(Func(lambda:sounds.append(now[0])),clip) if file==name else clip
  app.sound_clip=sound;app.live_health=lambda e,k,i,n:health.append((i,now[0]))
  event=dict(kind='gags',track='Sound',actions=[Action(t,'Opera Singer') for t in range(count)],targets={t:[0,1,2,3] for t in range(count)},misses=misses,health=[('cog',i,-1) for i in range(4) if i not in misses],live=True)
  rng=app.game.rng.getstate();c=app.gag_movie(event);c.start();c.pause()
  for step in range(1,int(c.getDuration()*100)+2):now[0]=min(step/100,c.getDuration());c.setT(now[0])
  assert len(sounds)==4-len(misses),(count,misses,sounds)
  assert sorted(sounds)==sorted(t for i,t in health)
  assert all(4.8<=t<=5.8 for t in sounds),sounds
  assert app.game.rng.getstate()==rng
  c.finish();app.clear_movie_props();app.sound_clip=original_sound;app.live_health=original_health
 Path('work/opera-glass-result.txt').write_text('PASS: bundled Ogg registered; one cue per hit Cog, multiple singers deduplicated, no glass on misses, health/audio synchronized, combat RNG unchanged, cleanup.')
except Exception:
 Path('work/opera-glass-result.txt').write_text(traceback.format_exc());raise
finally:app.destroy()
