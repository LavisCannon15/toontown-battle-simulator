"""Open battle courtyard with bundled Toontown paving, grass and sky."""
import math
from panda3d.core import Geom,GeomNode,GeomVertexData,GeomVertexFormat,GeomVertexWriter,GeomTriangles,Texture
from game_resources import resource


def outline(x,y,r):
    points=[]
    for cx,cy,start in ((x-r,y-r,0),(-x+r,y-r,90),(-x+r,-y+r,180),(x-r,-y+r,270)):
        for step in range(13):
            angle=math.radians(start+step*90/12)
            points.append((cx+r*math.cos(angle),cy+r*math.sin(angle)))
    return points


def build_plaza(app,parent):
    def mesh(name,vertices,triangles,texture):
        data=GeomVertexData(name,GeomVertexFormat.getV3n3t2(),Geom.UHStatic)
        v=GeomVertexWriter(data,'vertex');n=GeomVertexWriter(data,'normal');uv=GeomVertexWriter(data,'texcoord')
        for x,y,z,u,w in vertices:v.addData3(x,y,z);n.addData3(0,0,1);uv.addData2(u,w)
        indices=GeomTriangles(Geom.UHStatic)
        for tri in triangles:indices.addVertices(*tri)
        geom=Geom(data);geom.addPrimitive(indices);node=GeomNode(name);node.addGeom(geom)
        result=parent.attachNewNode(node)
        tex=app.loader.loadTexture(str(resource('phase_3.5/maps/'+texture)))
        tex.setWrapU(Texture.WMRepeat);tex.setWrapV(Texture.WMRepeat)
        tex.setMinfilter(Texture.FTLinearMipmapLinear);tex.setMagfilter(Texture.FTLinear);tex.setAnisotropicDegree(8)
        result.setTexture(tex,1);result.setLightOff()
        return result
    def surface(name,points,z,texture,tile):
        verts=[(0,0,z,0,0)]+[(x,y,z,x/tile,y/tile) for x,y in points]
        return mesh(name,verts,[(0,i+1,(i+1)%len(points)+1) for i in range(len(points))],texture)
    def band(name,inner,outer,z1,z2,texture,tile):
        verts=[]
        for (x,y),(a,b) in zip(inner,outer):verts.extend(((x,y,z1,x/tile,y/tile),(a,b,z2,a/tile,b/tile)))
        count=len(inner);tris=[]
        for i in range(count):
            a=2*i;b=2*((i+1)%count);tris.extend(((a,a+1,b+1),(a,b+1,b)))
        return mesh(name,verts,tris,texture)
    surface('tt-grass-border',[(-300,-300),(300,-300),(300,300),(-300,300)],-.08,'grassTT.jpg',12)
    inner=outline(14,12,4);curb=outline(14.30,12.30,4.30);outer=outline(16.3,14.3,6.3)
    surface('tt-battle-paving',inner,0,'sidewalkbrown.jpg',5)
    band('tt-rounded-curb',inner,curb,0,.20,'curb_brown_even.jpg',2)
    band('tt-rounded-sidewalk',curb,outer,.20,.20,'sidewalk_4cont_brown.jpg',5)
    band('tt-sidewalk-edge',outer,outline(16.45,14.45,6.45),.20,-.08,'curb_brown_even.jpg',2)
    sky=app.loader.loadModel(str(resource('phase_3.5/models/props/TT_sky.bam')))
    sky.reparentTo(parent);sky.setName('tt-plaza-sky');sky.setScale(3);sky.setZ(-25)
    sky.setLightOff();sky.setDepthWrite(False);sky.setBin('background',0)
