import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from panda3d.core import loadPrcFileData
loadPrcFileData('','audio-library-name null')
from panda_battle import PandaBattle
from battle_engine import Action
from support import SOS
from sos_movies import arrival,remove
from sos_visuals import support_performance
app=PandaBattle(offscreen=True,timed=False)
try:
 real_sound=app.sound_clip;calls=[]
 def sound(name,*args,**kwargs):calls.append(name);return real_sound(name,*args,**kwargs)
 app.sound_clip=sound
 for name,data in SOS.items():
  if data[0] not in ('Toons Hit','Cogs Miss'):continue
  for count in (1,2,3,4):
   app.new_battle()
   for i,t in enumerate(app.game.toons):t.escaped=i>=count
   app.display_cog_hp=[c.hp if i<count else 0 for i,c in enumerate(app.game.cogs)]
   clip=arrival(app,Action(0,name));clip.start();clip.finish();calls.clear()
   guest=app.sos_guests[0];clip=support_performance(app,0,guest)
   assert calls.count('AA_heal_pixiedust.ogg')==1
   targets=(app.cog_nodes if data[0]=='Cogs Miss' else app.toon_nodes)[:count]
   drops=[e for e in app.movie_particles if e.getName()=='source-effect-pixieDrop']
   poofs=[e for e in app.movie_particles if e.getName()=='source-effect-pixiePoof']
   assert len(drops)==len(poofs)==count
   clip.start();clip.pause();clip.setT(2)
   assert {e.getParent() for e in drops}==set(targets)
   clip.setT(2.6)
   bubbles=[n for n,a in app.movie_props if n.getName()=='cog-speech-bubble']
   assert len(bubbles)==(count if data[0]=='Cogs Miss' else 0)
   assert all(not n.isHidden() for n in bubbles)
   clip.setT(3.5);assert {e.getParent() for e in poofs}==set(targets)
   clip.finish();assert all(n.isHidden() for n in bubbles)
   remove(app,0);app.clear_movie_props()
 print('All six accuracy SOS cards x 1–4 recipients: simultaneous drops/poofs, one cast sound, Cog dialogue and cleanup passed.')
finally:app.destroy()
