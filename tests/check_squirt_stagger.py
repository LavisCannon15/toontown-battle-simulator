import sys,traceback
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from panda3d.core import loadPrcFileData
loadPrcFileData('','audio-library-name null')
from panda_battle import PandaBattle
from battle_engine import Action
from squirt_sequence import schedule
app=PandaBattle(offscreen=True,timed=False,seed=1)
try:
 for targets,expected in [([0,0,0,0],[0,.5,1,1.5]),([0,1,2,3],[0,1,2,3]),([0,0,1,2],[0,1,2,2.5])]:
  for miss in (False,True):
   app.spawn_characters();app.display_cog_hp=[c.hp for c in app.game.cogs]
   actions=[Action(i,'Fire Hose',t) for i,t in enumerate(targets)]
   event=dict(kind='gags',track='Squirt',actions=actions,targets={i:[t] for i,t in enumerate(targets)},health=[] if miss else [('cog',t,-10) for t in sorted(set(targets))],misses=sorted(set(targets)) if miss else [],live=True)
   ordered=schedule(event);assert [d for a,d in ordered]==expected,(ordered,expected)
   health=[];original=app.live_health
   app.live_health=lambda e,k,i,n:health.append((k,i,n))
   clip=app.gag_movie(event);clip.start();clip.pause()
   hoses=[p for p,a in app.movie_props if p.getName()=='battle-prop-firehose'];assert len(hoses)==4,len(hoses)
   first_seen={}
   for step in range(1,int(clip.getDuration()*100)+2):
    at=min(step/100,clip.getDuration());clip.setT(at)
    for i,p in enumerate(hoses):
     if not p.isHidden() and i not in first_seen:first_seen[i]=at
   assert len(first_seen)==4,first_seen
   observed=[first_seen[i] for i in range(4)]
   assert all(abs((observed[i]-observed[0])-(expected[i]-expected[0]))<.03 for i in range(4)),(observed,expected)
   assert len(health)==(0 if miss else len(set(targets))),health
   assert all(n==-10 for k,i,n in health)
   clip.finish();app.clear_movie_props();app.live_health=original
   assert all(p.isEmpty() for p in hoses)
 # Mixed normal Squirt gags retain ordering inside each target group.
 actions=[Action(0,'Squirting Flower',0),Action(1,'Fire Hose',0),Action(2,'Storm Cloud',1)]
 event=dict(actions=actions,targets={0:[0],1:[0],2:[1]})
 assert [(a.toon,d) for a,d in schedule(event)]==[(2,0),(0,1),(1,1.5)]
 Path('work/squirt-stagger-result.txt').write_text('PASS: four real Fire Hoses stagger on same, separate and mixed target groups; hit/miss; props start at source offsets; aggregate damage occurs once; cleanup; mixed Squirt scheduling.')
except Exception:
 Path('work/squirt-stagger-result.txt').write_text(traceback.format_exc());raise
finally:app.destroy()
