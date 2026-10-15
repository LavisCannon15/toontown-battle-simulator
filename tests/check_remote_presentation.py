import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from panda3d.core import loadPrcFileData
loadPrcFileData('','audio-library-name null')
from panda_battle import PandaBattle
from support import REMOTES
app=PandaBattle(offscreen=True,timed=False,seed=1)
try:
 app.display_toon_hp=[t.hp for t in app.game.toons];app.display_cog_hp=[c.hp for c in app.game.cogs]
 remote=REMOTES['Damage remote 1★'];app.game.cogs[0].remote=remote;app.game.cogs[0].lure=3
 app.sync_remote_visuals();app.restore_cog_pose(0)
 assert app.cog_actors[0].getCurrentAnim()=='controlidle'
 antenna=app.remote_visuals[0][1];assert not antenna.isHidden()
 clip=app.cog_clip(0,'hypnotized',1);clip.start();clip.finish()
 assert app.cog_actors[0].getCurrentAnim()=='controlidle' and not antenna.isHidden()
 app.animating=True;app.make_hud()
 event={'kind':'remote','cog':0,'remote_kind':'Damage','remote_before':remote,'health':[('cog',1,-45)],'misses':[]}
 clip=app.remote_movie(event);clip.start();clip.pause();clip.setT(1.4)
 bubble=app.render.find('**/remote-joke-bubble');assert not bubble.isEmpty() and not bubble.isHidden()
 assert not app.cog_nodes[0].find('**/cog-speech-bubble').isEmpty()
 for tick in range(35,81):clip.setT(tick/24)
 replies=app.cog_nodes[1].findAllMatches('**/cog-speech-bubble')
 assert any(not node.isHidden() for node in replies), 'Recipient reply must appear after punchline'
 assert app.cog_nodes[2].find('**/cog-speech-bubble').isEmpty(), 'Nonrecipient must not reply'
 app.position_nametags()
 for _ in range(3):app.graphicsEngine.renderFrame()
 app.win.saveScreenshot(str(Path('reports/remote-joke-bubble.png').resolve()))
 clip.finish();app.clear_movie_props();assert app.render.find('**/remote-joke-bubble').isEmpty()
 assert app.render.find('**/cog-speech-bubble').isEmpty()
 assert not antenna.isHidden()
 app.finish_round();assert app.cog_actors[0].getCurrentAnim()=='controlidle'
 app.game.cogs[0].remote=None;app.sync_remote_visuals();app.restore_cog_pose(0)
 assert 0 not in app.remote_visuals and app.cog_actors[0].getCurrentAnim()=='idle'
 print('Remote joke bubble, Lure/remote pose priority, persistent antenna, cleanup and expiry passed.')
finally:app.destroy()
