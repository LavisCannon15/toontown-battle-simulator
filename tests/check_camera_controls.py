import sys,math
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from panda3d.core import loadPrcFileData,Vec3,Point2,Point3
loadPrcFileData('','audio-library-name null')
from panda_battle import PandaBattle
app=PandaBattle(offscreen=True,timed=False,seed=1)
try:
 original=Vec3(app.camera.getPos());hp=[t.hp for t in app.game.toons];rng=app.game.rng.getstate()
 app.orbit_camera(.3,.2);assert (app.camera.getPos()-original).length()>1
 app.pan_camera(.1,.1);assert (app.camera_focus-Vec3(0,.5,2.8)).length()>1
 for _ in range(100):app.zoom_camera(-1)
 assert app.camera_distance==8
 for _ in range(100):app.zoom_camera(1)
 assert app.camera_distance==100
 app.orbit_camera(10,100);assert app.camera_pitch<=math.radians(80)
 app.reset_camera();assert (app.camera.getPos()-original).length()<.0001
 assert hp==[t.hp for t in app.game.toons] and rng==app.game.rng.getstate()
 for dx in (-.3,.3):
  app.orbit_camera(dx,.05);app.position_nametags()
  p=Point2();assert app.camLens.project(app.camera.getRelativePoint(app.render,app.camera_focus),p)
  near=Point3();far=Point3();assert app.camLens.extrude(p,near,far)
  direction=(far-near).normalized();focus=app.camera.getRelativePoint(app.render,app.camera_focus)
  assert (focus-near).cross(direction).length()<.001
 app.open_rewards();distance=app.camera_distance;app.camera_wheel(1);assert app.camera_distance==distance
 app.close_modal();app.reset_camera()
 print('Orbit, pan, zoom limits, reset, battle-state isolation, projection and menu scrolling passed.')
finally:app.destroy()
