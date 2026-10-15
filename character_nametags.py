"""Reference heights/joints adapted to the simulator's projected HUD labels.
Avatar: height + .5; Suit: height + 1.0 (both converted to .62 scene scale).
Toon supplies its leg name-tag joint; Suit.getNametagJoints returns no joints.
"""
from panda3d.core import Point2,Point3
from battle_engine import COG_CATALOG

def cog_text(cog,actor):
 skeleton=actor.getPythonTag('skelecog') if actor.hasPythonTag('skelecog') else cog.skelecog
 # DistributedSuitBase.setSkeleRevives + TTLocalizer.SkeleRevivePostFix.
 # Use the displayed layer: the engine can resolve revival before playback.
 suffix=' v2.0' if cog.version2 and not skeleton else ''
 return f'{"Skelecog" if skeleton else cog.name}\n{COG_CATALOG[cog.name]["department"]}\nLevel {cog.level}{suffix}'

def anchor(node,actor,toon=False):
 height=actor.getPythonTag('nametag-height')
 point=Point3(0,0,height)
 if toon and actor.hasPythonTag('nametag-joint'):
  joint=actor.getPythonTag('nametag-joint')
  if not joint.isEmpty():point+=joint.getPos(node)-actor.getPythonTag('nametag-neutral')
 return point

def project(app,node,point):
 """Use the active display region and scene graph, not a guessed UI scale."""
 projected=Point2();camera_point=app.cam.getRelativePoint(node,point)
 if not app.camLens.project(camera_point,projected):return None
 if abs(projected.x)>1 or abs(projected.y)>1:return None
 region=app.camNode.getDisplayRegion(0)
 x=region.getLeft()+(projected.x+1)*.5*(region.getRight()-region.getLeft())
 y=region.getBottom()+(projected.y+1)*.5*(region.getTop()-region.getBottom())
 return app.hud.getRelativePoint(app.render2d,Point3(x*2-1,0,y*2-1))

def fit_cog_label(label):
 label.resetFrameSize()
 # Keep the lower edge of the complete three-line card above the anchor.
 label.setZ(-label.getBounds()[2])
