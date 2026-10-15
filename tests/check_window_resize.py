import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from panda3d.core import loadPrcFileData,Point3,WindowProperties
loadPrcFileData('','audio-library-name null')
from panda_battle import PandaBattle
app=PandaBattle(offscreen=False,timed=False,seed=1)
out=Path('reports/window-resize');out.mkdir(exist_ok=True)
try:
 for w,h in [(1440,900),(1817,993),(1280,1024),(1920,1080),(2560,1080),(640,480),(1440,900)]:
  print('Request resize',w,h,flush=True)
  requested=(w,h);props=WindowProperties();props.setSize(w,h);app.win.requestProperties(props)
  import time
  for _ in range(8):app.taskMgr.step();app.graphicsEngine.renderFrame();time.sleep(.03)
  w,h=app.win.getXSize(),app.win.getYSize()
  assert abs(app.aspect2d.getSx()-1/(w/h))<1e-5,(w,h,app.aspect2d.getScale())
  for x,z in [(-1.78,1),(1.78,1),(-1.78,-1.01),(1.78,-1.01)]:
   p=app.render2d.getRelativePoint(app.ui,Point3(x,0,z))
   assert -1<=p.x<=1 and -1<=p.z<=1,(w,h,p)
  for battle in (False,True):
   app.animating=battle;app.make_hud()
   assert abs(app.camLens.getAspectRatio()-(w/h)/app.scene_height)<1e-4
   app.position_nametags()
   if requested==(1817,993):
    for _ in range(3):app.graphicsEngine.renderFrame()
    app.win.saveScreenshot(str((out/('maximized-battle.png' if battle else 'maximized-planning.png')).resolve()))
  app.animating=False
 print('Resize transitions passed: original, maximized, 5:4, 16:9, ultrawide, small window, restore; interface corners and battle lens fit.')
finally:app.destroy()
