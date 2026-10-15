import sys,traceback
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from panda3d.core import loadPrcFileData,Vec3,Point3
loadPrcFileData('','audio-library-name null')
from panda_battle import PandaBattle,Cog
from character_nametags import anchor,project
app=PandaBattle(offscreen=True,timed=False,seed=1)
try:
 app.game.cogs=[Cog('Micromanager',4),Cog('Ambulance Chaser',8),Cog('Corporate Raider',11),Cog('Big Wig',12,skelecog=True)]
 app.spawn_characters();app.make_hud();app.position_nametags()
 for label in app.cog_name_labels:
  bounds=label['frameSize'] or label.bounds
  text=label.component('text0');frame=text.textNode.getFrameActual();size=label['text_scale'][0]
  assert bounds[0]<=frame[0]*size+.001 and bounds[1]>=frame[1]*size-.001 and bounds[2]<=frame[2]*size+.001 and bounds[3]>=frame[3]*size-.001,(bounds,frame,size)
 assert app.cog_name_labels[3]['text']=='Skelecog\nLawbot\nLevel 12'
 assert anchor(app.cog_nodes[0],app.cog_actors[0]).z<3
 assert anchor(app.cog_nodes[2],app.cog_actors[2]).z>4
 for i,(node,parts) in enumerate(zip(app.toon_nodes,app.toon_actors)):
  legs=parts['legs'];base=anchor(node,legs,True);joint=legs.getPythonTag('nametag-joint')
  assert not joint.isEmpty()
  legs.pose('jump',18);legs.update(force=True)
  expected=Point3(0,0,legs.getPythonTag('nametag-height'))+joint.getPos(node)-legs.getPythonTag('nametag-neutral')
  assert (anchor(node,legs,True)-expected).length()<.001
  legs.pose('idle',0);legs.update(force=True)
 # Dynamic data refresh and background resizing, without rebuilding the HUD.
 app.game.toons[0].name='Professor Longname McFluffypaws';app.game.cogs[1].level=13;app.position_nametags()
 assert app.toon_nametags[0]['text']==app.game.toons[0].name
 assert app.cog_name_labels[1]['text'].endswith('Level 13')
 app.cog_actors[2].setPythonTag('skelecog',True);app.position_nametags()
 assert app.cog_name_labels[2]['text'].startswith('Skelecog')
 # A hidden speech node must not suppress the name forever.
 phrase=app.toon_nodes[0].attachNewNode('unite-phrase');phrase.hide();app.position_nametags()
 assert not app.toon_nametags[0].isHidden()
 phrase.show();app.position_nametags();assert app.toon_nametags[0].isHidden();phrase.removeNode()
 # The projection remains identical on screen when HUD scale changes.
 for factor in (.7,1,1.2):
  app.ui.setScale(factor)
  node=app.toon_nodes[1];p=anchor(node,app.toon_actors[1]['legs'],True);position=project(app,node,p)
  assert position is not None
  screen=app.render2d.getRelativePoint(app.hud,position)
  from panda3d.core import Point2
  expected=Point2();app.camLens.project(app.cam.getRelativePoint(node,p),expected)
  assert abs(screen.x-expected.x)<.001 and abs(screen.z-expected.y)<.001
 app.ui.setScale(.9);app.position_nametags()
 app.toon_nodes[1].hide();app.position_nametags();assert app.toon_nametags[1].isHidden();app.toon_nodes[1].show()
 app.cog_actors[2].setPythonTag('skelecog',False);app.position_nametags()
 for _ in range(3):app.graphicsEngine.renderFrame()
 app.win.saveScreenshot('work/nametag-audit.png')
 Path('work/nametag-result.txt').write_text('PASS: font-backed auto-sized frames, Skelecog/level/name refresh, model heights, Toon joint anchoring, hidden speech visibility, HUD-scale projection and removed-character hiding.')
except Exception:
 Path('work/nametag-result.txt').write_text(traceback.format_exc());raise
finally:app.destroy()
