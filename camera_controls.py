"""Mouse orbit/pan/zoom independent of battle state and GUI scrolling."""
import math
from panda3d.core import Vec3

class CameraControls:
 def init_camera_controls(self):
  self.camera_drag=None;self.reset_camera()
  self.accept('mouse3',self.start_camera_drag,['orbit'])
  self.accept('mouse3-up',self.stop_camera_drag)
  self.accept('mouse2',self.start_camera_drag,['pan'])
  self.accept('mouse2-up',self.stop_camera_drag)
  self.accept('home',self.reset_camera)
  self.accept('wheel_up',self.camera_wheel,[-1])
  self.accept('wheel_down',self.camera_wheel,[1])
  self.taskMgr.add(self.update_camera_drag,'battle-camera-controls')
 def reset_camera(self):
  self.camera_drag=None;self.camera_focus=Vec3(0,.5,2.8)
  delta=Vec3(10,-39,24)-self.camera_focus
  self.camera_distance=delta.length()
  self.camera_yaw=math.atan2(delta.x,-delta.y)
  self.camera_pitch=math.asin(delta.z/self.camera_distance)
  self.apply_camera()
 def apply_camera(self):
  d=self.camera_distance;p=self.camera_pitch;y=self.camera_yaw
  self.camera.setPos(self.camera_focus+Vec3(d*math.cos(p)*math.sin(y),-d*math.cos(p)*math.cos(y),d*math.sin(p)))
  self.camera.lookAt(self.camera_focus)
 def camera_pointer_allowed(self):
  if self.modal or not self.mouseWatcherNode.hasMouse():return False
  if getattr(self,'log_popup',None) and self.log_popup.contains_mouse():return False
  mouse=self.mouseWatcherNode.getMouse();z=mouse.y/self.ui.getSx()
  if z>.72 or z<(.0 if not self.animating and not self.game.result else -.62):return False
  region=self.mouseWatcherNode.getOverRegion()
  return not region or not region.getName().startswith('pg')
 def start_camera_drag(self,mode):
  if not self.camera_pointer_allowed():return
  m=self.mouseWatcherNode.getMouse();self.camera_drag=(mode,m.x,m.y)
 def stop_camera_drag(self):self.camera_drag=None
 def camera_wheel(self,direction):
  if getattr(self,'log_popup',None) and self.log_popup.contains_mouse():self.scroll_log(direction);return
  if self.modal=='rewards' and getattr(self,'reward_category',None)=='SOS cards':
   bar=self.reward_scroll.verticalScroll;bar['value']=max(0,min(1,bar['value']+direction*.08));return
  if not self.camera_pointer_allowed():return
  self.zoom_camera(direction)
 def zoom_camera(self,direction):
  self.camera_distance=max(8,min(100,self.camera_distance*math.exp(direction*.10)));self.apply_camera()
 def orbit_camera(self,dx,dy):
  self.camera_yaw-=dx*3
  self.camera_pitch=max(math.radians(8),min(math.radians(80),self.camera_pitch+dy*2))
  self.apply_camera()
 def pan_camera(self,dx,dy):
  right=self.camera.getQuat(self.render).getRight();forward=Vec3(math.sin(self.camera_yaw),-math.cos(self.camera_yaw),0)
  self.camera_focus+=(-right*dx+forward*dy)*self.camera_distance*.6
  self.camera_focus.x=max(-25,min(25,self.camera_focus.x));self.camera_focus.y=max(-25,min(25,self.camera_focus.y))
  self.apply_camera()
 def update_camera_drag(self,task):
  if self.camera_drag:
   if self.modal or not self.mouseWatcherNode.hasMouse():self.stop_camera_drag()
   else:
    mode,x,y=self.camera_drag;m=self.mouseWatcherNode.getMouse()
    (self.orbit_camera if mode=='orbit' else self.pan_camera)(m.x-x,m.y-y)
    self.camera_drag=(mode,m.x,m.y)
  return task.cont
