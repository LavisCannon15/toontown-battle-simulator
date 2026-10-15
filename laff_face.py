"""Dynamic Laff faces assembled from the original laff_o_meter geometry."""
from direct.gui.DirectGui import DirectFrame,DirectLabel
from panda3d.core import TransparencyAttrib
from direct.interval.IntervalGlobal import Sequence,LerpScaleInterval

class LaffFace(DirectFrame):
 def __init__(self,parent,model,font,toon,color,pos,scale=.043):
  super().__init__(parent=parent,relief=None,frameColor=(0,0,0,0),pos=pos,scale=scale)
  self.setTransparency(TransparencyAttrib.MAlpha);self.color=color;self.hp=toon.hp;self.maximum=toon.maximum;self.pulse=None
  self.face=DirectFrame(parent=self,relief=None,image=model.find('**/'+toon.animal+'head'),image_color=color)
  self.parts={n:DirectFrame(parent=self,relief=None,image=model.find('**/'+n)) for n in ('frown','smile','eyes','open_smile')}
  self.teeth=[DirectFrame(parent=self.parts['open_smile'],relief=None,image=model.find('**/tooth_'+str(i))) for i in range(6,0,-1)]
  self.numbers=[DirectLabel(parent=self.parts['eyes'],relief=None,pos=(x,0,.051),text=str(value),text_font=font,text_scale=.4,text_fg=(0,0,0,1)) for x,value in [(-.398,toon.hp),(.442,toon.maximum)]]
  self.set_health(toon.hp,toon.maximum)
 def set_health(self,hp,maximum,animate=False):
  previous=self.hp;self.hp=hp;self.maximum=maximum
  for part in self.parts.values():part.hide()
  for tooth in self.teeth:tooth.hide()
  if hp<=0:
   self.parts['frown'].show();self.face['image_color']=(.5804,.8039,.3412,1)
  else:
   self.face['image_color']=self.color;self.parts['eyes'].show()
   if hp>=maximum:self.parts['smile'].show()
   else:
    self.parts['open_smile'].show()
    for i,tooth in enumerate(self.teeth):
     if hp>maximum*(0,.166666,.333333,.5,.666666,.833333)[i]:tooth.show()
  for label,value in zip(self.numbers,(hp,maximum)):label['text']=str(value)
  if animate and hp!=previous:
   if self.pulse:self.pulse.finish()
   scale=self.getScale();factor=.78 if hp<previous else 1.18
   self.pulse=Sequence(LerpScaleInterval(self,.15,scale*factor),LerpScaleInterval(self,.25,scale));self.pulse.start()
 def destroy(self):
  if self.pulse:self.pulse.pause()
  super().destroy()
