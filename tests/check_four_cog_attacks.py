"""Real extracted assets: all attacks, hit/miss, transforms and cancellation."""
import sys,traceback
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from panda3d.core import loadPrcFileData,Vec3
loadPrcFileData('','audio-library-name null')
from panda_battle import PandaBattle,Cog
from battle_movies import MOVIES
app=PandaBattle(offscreen=True,timed=False,seed=1)
try:
 checked=[];bounds={}
 from detailed_cog_props import ATTACKS as props
 from detailed_cog_motion import ATTACKS as motion
 shared='--shared' in sys.argv
 cogs=[c for c,s in MOVIES['suits'].items() if any(a in props|motion for a in s['attacks'])] if shared else ('Two-Face','Money Bags','Spin Doctor','Head Hunter')
 for cog in cogs:
  app.game.cogs=[Cog(cog,8)];app.spawn_characters()
  for name in MOVIES['suits'][cog]['attacks']:
   if shared and name not in props|motion:continue
   for miss in (False,True):
    app.clear_movie_props();app.game.toons[0].hp=100
    app.display_toon_hp=[t.hp for t in app.game.toons];app.display_cog_hp=[c.hp for c in app.game.cogs]
    before=(Vec3(app.toon_nodes[0].getPos()),Vec3(app.toon_nodes[0].getHpr()))
    c=app.cog_movie(dict(kind='cog',cog=0,name=name,targets=[0],misses=[0] if miss else [],health=[] if miss else [('toon',0,-5)],live=True));c.start();c.pause()
    onset={'Spin':1.7,'Paradigm Shift':1.95,'Quake':1.8,'Head Shrink':2.1}.get(name,0)
    if miss:onset={'Spin':.91,'Paradigm Shift':.95,'Quake':1.1,'Head Shrink':1.4}.get(name,0)
    for step in range(1,int(c.getDuration()*50)+2):
     time=min(step/50,c.getDuration());c.setT(time)
     for r in getattr(app,'live_departures',[]):
      if name in ('Spin','Paradigm Shift','Quake','Head Shrink'):r.pause();r.setT(min(r.getDuration(),max(0,time-onset)))
     for a in app.cog_actors:a.update(force=True)
     for p,a in app.movie_props:
      if p.isEmpty() or p.isHidden() or not p.getName().startswith('attack-'):continue
      b=p.getTightBounds(app.render)
      if b:bounds[cog+'|'+p.getName()]=max(bounds.get(cog+'|'+p.getName(),0),(b[1]-b[0]).length())
     if name=='Hang Up' and abs(time-2)<.001:
      receiver=next(p for p,a in app.movie_props if p.getName()=='attack-receiver');assert receiver.getParent()==app.cog_actors[0].find('**/joint_Rhold')
     if not miss and name=='Spin' and abs(time-4)<.001:assert abs(app.toon_nodes[0].getH())>30
     if not miss and name=='Paradigm Shift' and abs(time-3.3)<.001:assert app.toon_nodes[0].getZ()>before[0].z+1
     if not miss and name=='Head Shrink' and abs(time-4.2)<.001:assert app.toon_actors[0]['torso'].find('**/def_head').getChild(0).getScale().x<.7
    c.finish()
    for r in getattr(app,'live_departures',[]):r.finish()
    app.live_departures=[];app.clear_movie_props()
    assert app.game.toons[0].hp==(100 if miss else 95),(cog,name,app.game.toons[0].hp)
    assert (app.toon_nodes[0].getPos()-before[0]).length()<.01,(name,'position')
    assert (app.toon_nodes[0].getHpr()-before[1]).length()<.01,(name,'heading')
    checked.append((cog,name,miss))
 Path('work/shared-cog-result.txt' if shared else 'work/four-cog-result.txt').write_text('PASS '+str(len(checked))+' hit/miss movies\n'+str(bounds))
except Exception:
 Path('work/four-cog-result.txt').write_text(traceback.format_exc());raise
finally:app.destroy()
