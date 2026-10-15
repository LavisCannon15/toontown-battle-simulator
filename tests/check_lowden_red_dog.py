import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from panda3d.core import loadPrcFileData
loadPrcFileData('','audio-library-name null')
from panda_battle import PandaBattle
from battle_engine import Action
from lowden_movie import movie
app=PandaBattle(offscreen=True,timed=False,seed=1)
try:
 app.animating=True;app.display_toon_hp=[t.hp for t in app.game.toons];app.display_cog_hp=[c.hp for c in app.game.cogs];app.make_hud()
 event={'kind':'support','health':[('cog',i,-c.hp) for i,c in enumerate(app.game.cogs)],'misses':[]}
 clip=movie(app,Action(0,'SOS: Lord Lowden Clear'),event)
 assert not any(n.getName()=='battle-prop-receiver' for n,a in app.movie_props)
 cannons=[n for n,a in app.movie_props if n.getName()=='fire-cannon']
 assert len(cannons)==4 and all(abs(n.getH())<.001 for n in cannons)
 guest=app.sos_guests[0]
 assert set(guest['actors'])=={'suit'}
 clip.start();clip.pause();clip.setT(1.0)
 assert guest['root'].getZ()>0,'Lowden must descend from above'
 blades=[n for n,a in app.movie_props if n.getName()=='lowden-flight-propeller']
 assert len(blades)==2 and not blades[0].isHidden()
 clip.setT(5.6)
 assert abs(guest['root'].getZ())<.001 and blades[0].isHidden()
 assert all(hp>0 for hp in app.display_cog_hp),'Cannons must wait until after the slip throw'
 slip=next(n for n,a in app.movie_props if n.getName()=='battle-prop-pink-slip')
 assert not slip.isHidden()
 assert slip.getParent().getName()=='joint_Rhold'
 assert guest['actors']['suit'].getAnimControl('command').getFrame()>0
 head=guest['head']
 colored=[n for n in head.findAllMatches('**/+GeomNode') if n.hasColor() and n.getColor().x>n.getColor().y*2]
 assert colored,'Dog forehead must be red'
 assert all(not n.hasColor() for n in head.findAllMatches('**/+GeomNode') if any(word in n.getName().lower() for word in ('muzzle','ears','nose','eyes')))
 suit=guest['actors']['suit']
 assert 'm_blazer' in suit.find('**/torso').getTexture().getFilename().getBasename()
 app.camera.setPos(-8,-13,8);app.camera.lookAt(guest['root'].getPos()+__import__('panda3d.core',fromlist=['Vec3']).Vec3(0,0,2))
 for _ in range(3):app.graphicsEngine.renderFrame()
 app.win.saveScreenshot(str(Path('reports/lowden-red-dog.png').resolve()))
 clip.setT(7.5)
 for i,suit in enumerate(app.cog_actors):
  assert abs(abs(suit.getH(app.cog_nodes[i]))-180)<.01,'Cog facing must survive cannon rotation'
 clip.setT(clip.getDuration()-.5)
 assert guest['root'].getZ()>0 and not blades[1].isHidden(),'Takeoff must ascend with propeller'
 clip.finish();assert not app.sos_guests
 app.clear_movie_props()
 assert all(hp==0 for hp in app.display_cog_hp)
 print('Lowden uses a red dog head with original muzzle/ears and Cashbot suit, fires all four Cogs, and cleans up.')
finally:app.destroy()
