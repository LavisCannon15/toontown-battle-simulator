import sys,math
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from panda3d.core import loadPrcFileData,Point3
loadPrcFileData('','audio-library-name null')
from panda_battle import PandaBattle
from speech_balloon import build,update,WORLD_SCALE
app=PandaBattle(offscreen=True,timed=False,seed=1)
try:
 for phrase in ('Boo!', 'I believe your books do not balance. This will put you in debt.'):
  root=app.characters.attachNewNode('layout-test');root.setZ(5)
  content=build(app,root,phrase);layout=root.getPythonTag('speech-layout')
  assert layout['wordwrap']==10 and layout['hscale']>=.25
  middle=content.find('**/middle');top=content.find('**/top')
  assert abs(middle.getSz()-layout['height'])<.001
  assert abs(top.getZ()-(layout['height']+2))<.001
  for y in (-20,-40,-70):
   app.camera.setY(y);update(app,root)
   distance=app.cam.getRelativePoint(root,Point3(0)).y/WORLD_SCALE
   assert abs(content.getSx()-.56*math.sqrt(max(distance,.1)/50)*WORLD_SCALE)<.001
  root.removeNode()
 print('PASS: source wrapping, middle/top transforms, minimum width and camera-distance scale')
finally:app.destroy()
