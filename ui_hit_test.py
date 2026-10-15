"""Coordinate-aware GUI blocking for world picking after resize/reposition."""
from panda3d.core import Point3

def contains(frame,from_node,point):
 if frame is None or frame.isEmpty() or frame.isHidden():return False
 local=frame.getRelativePoint(from_node,Point3(point))
 left,right,bottom,top=frame.getBounds()
 return left<=local.x<=right and bottom<=local.z<=top
