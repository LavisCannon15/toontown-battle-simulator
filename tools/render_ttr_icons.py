from pathlib import Path
import sys
from panda3d.core import loadPrcFileData,Filename,NodePath,OrthographicLens,PNMImage,AmbientLight,DirectionalLight,Vec4,TransparencyAttrib
from direct.showbase.ShowBase import ShowBase
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'assets/ttr'; OUT=ROOT/'assets'; OUT.mkdir(exist_ok=True)
loadPrcFileData('', 'model-cache-models false\nmodel-cache-textures false\nwindow-type offscreen\nwin-size 256 256\naudio-library-name null\nframebuffer-alpha true\nbackground-color 0 0 0 0\nnotify-level warning\n')
from panda3d.core import getModelPath
getModelPath().prependDirectory(Filename.fromOsSpecific(str(SOURCE)))
base=ShowBase(windowType='offscreen')
base.setBackgroundColor(0,0,0,0)
base.cam.node().setLens(OrthographicLens())
base.cam.node().getLens().setFilmSize(2,2)
base.cam.setPos(0,-10,0);base.cam.lookAt(0,0,0)

def save(node,name,size=80,flat=True):
    wrapper=base.render.attachNewNode('asset')
    obj=node.copyTo(wrapper)
    obj.setState(node.getNetState())
    obj.setTransparency(TransparencyAttrib.MAlpha)
    if flat:
        obj.setLightOff()
        obj.setDepthTest(False)
        obj.setDepthWrite(False)
        obj.setTwoSided(True)
    else:
        obj.setH(180)
        ambient=AmbientLight('ambient');ambient.setColor((.8,.8,.8,1))
        wrapper.setLight(wrapper.attachNewNode(ambient))
        light=DirectionalLight('key');light.setColor((.5,.5,.5,1))
        ln=wrapper.attachNewNode(light);ln.setHpr(-30,-30,0);wrapper.setLight(ln)
    lo,hi=obj.getTightBounds(wrapper)
    center=(lo+hi)*.5
    scale=1.75/max(hi.x-lo.x,hi.z-lo.z)
    obj.setPos(-center)
    wrapper.setScale(scale)
    for _ in range(3):base.graphicsEngine.renderFrame()
    pnm=PNMImage();base.win.getScreenshot(pnm)
    scaled=PNMImage(size,size,4);scaled.quickFilterFrom(pnm)
    scaled.write(Filename.fromOsSpecific(str(OUT/(name+'.png'))))
    wrapper.removeNode()

inventory=base.loader.loadModel(Filename.fromOsSpecific(str(SOURCE/'phase_3.5/models/gui/inventory_icons.bam')))
for node in inventory.findAllMatches('**/+GeomNode'):
    save(node,node.name,64)
print('Rendered gag icons:',len(list(OUT.glob('inventory*.png'))))
base.destroy()
