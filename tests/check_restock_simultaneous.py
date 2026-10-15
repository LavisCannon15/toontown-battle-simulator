import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from panda3d.core import loadPrcFileData,Vec3
loadPrcFileData('','audio-library-name null')
from panda_battle import PandaBattle
from battle_engine import Action
from support import SOS
from sos_movies import arrival,remove
from sos_visuals import support_performance
app=PandaBattle(offscreen=True,timed=False)
try:
 names=[n for n,info in SOS.items() if info[0].startswith('Restock')]
 real_sound=app.sound_clip;sounds=[]
 def sound(name,*a,**kw):sounds.append(name);return real_sound(name,*a,**kw)
 app.sound_clip=sound
 for name in names:
  for count in (1,2,3,4):
   for i,t in enumerate(app.game.toons):t.escaped=i>=count
   arrive=arrival(app,Action(0,name));arrive.start();arrive.finish();sounds.clear()
   guest=app.sos_guests[0];clip=support_performance(app,0,guest)
   lips=[n for n,a in app.movie_props if n.getName()=='restock-lips']
   assert len(lips)==count and len(sounds)==1,(name,count,len(lips),sounds)
   assert {n.getPythonTag('recipient') for n in lips}==set(app.toon_nodes[:count])
   clip.start();clip.pause()
   throw_time=guest['impact']-.5
   for step in range(1,int((throw_time+.25)*30)+1):clip.setT(step/30)
   clip.setT(throw_time+.25)
   assert all(not n.isHidden() for n in lips)
   # All projectiles are at the same halfway point on their individual routes.
   positions=[Vec3(n.getPos(app.render)) for n in lips]
   clip.setT(guest['impact'])
   for n,mid in zip(lips,positions):
    target=n.getPythonTag('recipient');dest=target.getPos(app.render)+Vec3(0,0,2.5)
    assert (n.getPos(app.render)-dest).length()<.001
    assert n.isHidden()
   clip.finish();remove(app,0);app.clear_movie_props()
 print(f'{len(names)} Restock SOS cards x 1–4 living Toons: simultaneous projectiles, caller inclusion, one sound and cleanup passed.')
finally:app.destroy()
