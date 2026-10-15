import sys,traceback
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from panda3d.core import loadPrcFileData,Vec3
loadPrcFileData('', 'audio-library-name null')
from panda_battle import PandaBattle,Cog
from battle_movies import MOVIES
app=PandaBattle(offscreen=True,timed=False,seed=1)
try:
 count=0
 for cog,data in MOVIES['suits'].items():
  for attack in set(data['attacks']) & {'Bounce Check','Write Off','Liquidate','Red Tape'}:
   app.game.cogs=[Cog(cog,5)];app.spawn_characters()
   for miss in (False,True):
    e=dict(kind='cog',cog=0,name=attack,targets=[0],misses=[0] if miss else [],health=[])
    clip=app.cog_movie(e);clip.start();clip.pause()
    props={n.getName():n for n,a in app.movie_props}
    for t in (.5,1.5,2.5,3.1,3.6,4,4.6):
     clip.setT(t)
     if attack=='Write Off' and t==3.1:
      assert not props['write-off-checkmark'].isHidden()
     if attack=='Red Tape' and t==3.6:
      assert ('battle-prop-redtape-tube' in props)==(not miss)
      if not miss:assert not props['battle-prop-redtape-tube'].isHidden()
     if attack=='Liquidate' and t==3.1:
      cloud=props['battle-prop-stormcloud'];assert cloud.getParent()==app.render
      assert (cloud.getPos()-app.toon_nodes[0].getPos()-Vec3(0,0,3.86)).length()<.01
      assert len(app.movie_particles)==3
     if attack=='Bounce Check' and t==4:
      check=props['battle-prop-bounced-check'];assert check.getParent()==app.render
    clip.finish()
    for n,a in app.movie_props:assert n.isHidden(),n.getName()
    app.clear_movie_props();assert not app.movie_particles
    count+=1
 Path('work/classic-cog-result.txt').write_text(f'PASS: {count} real-asset hit/miss sequences, all Cog variants; checkmark, tape wrap, cloud travel/rain, bounce flight and cleanup.')
except Exception:
 Path('work/classic-cog-result.txt').write_text(traceback.format_exc());raise
finally:app.destroy()
