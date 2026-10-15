"""Small live battle journal independent of the modal editor and battle timer."""
from direct.gui.DirectGui import DirectFrame,DirectScrolledFrame
from panda3d.core import TextNode

class BattleLog:
 def __init__(self,app):
  self.app=app;self.expanded=False;self.follow=True;self.signature=None;self.frame=None;self.build()
 def build(self):
  if self.frame:self.frame.destroy()
  app=self.app;self.bounds=(-1.12 if self.expanded else .13,1.70,-.64 if self.expanded else -.04,.80)
  l,r,b,t=self.bounds
  self.frame=DirectFrame(parent=app.ui,frameSize=self.bounds,frameColor=(.08,.17,.22,.98),sortOrder=100)
  app.label(self.frame,'Battle log',l+.06,t-.09,.04,(1,1,.93,1))
  app.button(self.frame,'Compact' if self.expanded else 'Expand',r-.44,t-.08,self.toggle,.42,size=.024)
  app.button(self.frame,'X',r-.105,t-.08,self.close,.15,size=.025)
  self.scroll=DirectScrolledFrame(parent=self.frame,frameSize=(l+.035,r-.035,b+.135,t-.15),canvasSize=(0,r-l-.13,-1,0),frameColor=(.96,.97,.92,1),scrollBarWidth=.038,autoHideScrollBars=True)
  self.scroll.horizontalScroll.hide();self.scroll.verticalScroll['scrollSize']=.06
  self.body=app.label(self.scroll.getCanvas(),' ',.035,-.06,.032,(.12,.19,.23,1));self.body['text_font']=app.body_font
  self.latest=app.button(self.frame,'Following latest' if self.follow else 'Latest',l+.34,b+.064,self.go_latest,.58,size=.024)
  self.count=app.label(self.frame,'',r-.07,b+.054,.023,(.85,.93,.90,1),TextNode.ARight)
  self.signature=None;self.refresh()
 def close(self):
  self.frame.destroy();self.frame=None;self.app.log_popup=None
 def toggle(self):self.expanded=not self.expanded;self.build()
 def go_latest(self):self.follow=True;self.scroll.verticalScroll['value']=1;self.latest['text']='Following latest'
 def contains_mouse(self):
  a=self.app
  if a.modal or not a.mouseWatcherNode.hasMouse():return False
  m=a.mouseWatcherNode.getMouse();scale=a.ui.getSx();x=m.x*a.getAspectRatio()/scale;z=m.y/scale;l,r,b,t=self.bounds
  return l<=x<=r and b<=z<=t
 def wheel(self,direction):
  if not self.contains_mouse():return
  self.follow=False;self.latest['text']='Latest';bar=self.scroll.verticalScroll;bar['value']=min(1,max(0,bar['value']+direction*.08))
 def refresh(self):
  if self.app.modal:self.frame.hide();return
  self.frame.show()
  # A dragged scrollbar disengages following without snapping back on each event.
  if self.signature is not None and self.follow and self.scroll.verticalScroll['value']<.98:
   self.follow=False;self.latest['text']='Latest'
  log=self.app.game.log;signature=(id(self.app.game),len(log),log[-1] if log else '')
  if signature==self.signature:return
  old=self.scroll.verticalScroll['value'];oldheight=-self.scroll['canvasSize'][2];newbattle=self.signature and signature[0]!=self.signature[0]
  if newbattle:self.follow=True
  l,r,b,t=self.bounds;viewheight=t-b-.285
  self.body['text']='\n'.join(log);self.body['text_scale']=.032
  self.body['text_wordwrap']=(r-l-.19)/.032
  height=max(viewheight,.10-self.body.component('text0').textNode.getBottom()*.032)
  self.scroll['canvasSize']=(0,r-l-.13,-height,0)
  position=old*max(0,oldheight-viewheight)/max(.001,height-viewheight)
  self.scroll.verticalScroll['value']=1 if self.follow else min(1,position)
  self.count['text']=f'{len(log)} entries';self.signature=signature
