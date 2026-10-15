"""Port of libotp ChatBalloon::generate and Nametag3d distance sizing.
Reference: work/libotp-reference/src/nametag (classic, not modern TTR source).
"""
import math
from panda3d.core import TextNode,Mat4,Point3
from game_resources import resource
WORLD_SCALE=.62

def build(app,parent,phrase,font=None):
 text=TextNode('cog-speech-text');text.setFont(font if font is not None else app.suit_font)
 text.setWordwrap(10);text.setAlign(TextNode.ALeft);text.setText(phrase);text.setTextColor(0,0,0,1)
 hscale=max(text.getWidth()/9,.25)
 xoffset=1.0
 if text.getWidth()/9<.25:text.setAlign(TextNode.ACenter);xoffset+=4.5
 rows=max(text.getNumRows(),1);height=rows*text.getLineHeight()
 content=parent.attachNewNode('speech-content')
 bubble=app.loader.loadModel(str(resource('phase_3/models/props/chatbox.bam')));bubble.reparentTo(content)
 middle=bubble.find('**/middle');top=bubble.find('**/top')
 middle.setMat(Mat4.scaleMat(1,1,height)*middle.getMat())
 top.setMat(Mat4.translateMat(0,0,height-1)*top.getMat())
 bubble.setScale(hscale,1,1)
 label=content.attachNewNode(text);label.setPos(xoffset*hscale,-.02,2+(rows-1)*text.getLineHeight()+.2)
 # Native bubbles grow from the tail at the avatar's name anchor.
 parent.setPythonTag('speech-content',content)
 parent.setPythonTag('speech-layout',{'wordwrap':10,'hscale':hscale,'rows':rows,'height':height})
 update(app,parent)
 return content

def update(app,root):
 content=root.getPythonTag('speech-content')
 distance=app.cam.getRelativePoint(root,Point3(0,0,0)).y/WORLD_SCALE
 content.setScale(.56*math.sqrt(max(distance,.1)/50)*WORLD_SCALE)
