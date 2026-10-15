"""Every catalog attack, hit/miss, real models, effects and restoration."""
import sys,json,re
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from panda3d.core import loadPrcFileData,Vec3
loadPrcFileData('','audio-library-name null')
from panda_battle import PandaBattle
from battle_engine import Cog,COG_CATALOG
from battle_movies import MOVIES
from cog_choreography import AUDIT,time_value
app=PandaBattle(offscreen=True,timed=False,seed=1)
out=Path('reports/cog-attack-audit');out.mkdir(exist_ok=True);seen=set();rows=[]
try:
 app.animating=True
 for cogname,spec in MOVIES['suits'].items():
  rank=COG_CATALOG[cogname]['rank'];app.game.cogs=[Cog(cogname,rank+4)];app.spawn_characters();app.make_hud()
  for name,anim in spec['attacks'].items():
   group=next(a['group'] for a in COG_CATALOG[cogname]['attacks'] if a['name']==name);targets=list(range(4)) if group else [0]
   for miss in (False,True):
    app.display_toon_hp=[100]*4;app.display_cog_hp=[app.game.cogs[0].hp]
    origins=[Vec3(n.getPos()) for n in app.toon_nodes];heading=Vec3(app.cog_nodes[0].getHpr())
    event=dict(kind='cog',cog=0,name=name,targets=targets,health=[] if miss else [('toon',i,-1) for i in targets],misses=targets if miss else [])
    clip=app.cog_movie(event);clip.start();clip.pause()
    source=AUDIT[cogname+'|'+name];impact=time_value(source.get('impact'),app.cog_actors[0].getDuration(anim),2.5)
    sample=min(max(.5,impact-.1),clip.getDuration()-.01)
    for step in range(1,int(sample*24)+1):
     clip.setT(step/24)
     for effect in app.movie_particles:
      if effect.isEnabled():effect.accelerate(1/24)
    clip.setT(sample)

    if not miss and name not in seen:
     app.position_nametags()
     for _ in range(2):app.graphicsEngine.renderFrame()
     app.win.saveScreenshot(str((out/(re.sub('[^a-z0-9]','',name.lower())+'.png')).resolve()));seen.add(name)
    clip.finish();app.clear_movie_props()
    assert app.cog_nodes[0].getHpr().almostEqual(heading),name
    assert all(n.getPos().almostEqual(pos) for n,pos in zip(app.toon_nodes,origins)),name
    assert app.cog_actors[0].getCurrentAnim()=='idle',name
   rows.append(dict(cog=cogname,attack=name,hit_miss='passed',classic_source=source['source_function']))
 (out/'coverage.json').write_text(json.dumps(rows,indent=2))
 print(f'{len(rows)} Cog/attack pairs, {len(seen)} distinct attacks, hit/miss effects and transform/idle restoration passed.')
finally:app.destroy()
