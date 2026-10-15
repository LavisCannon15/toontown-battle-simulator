"""Tutorial street assembled from the bundled TTR XML scene and storage table."""
import xml.etree.ElementTree as ET
from panda3d.core import TextNode,BitMask32
from game_resources import resource

def build_tutorial(app,parent):
    storage=ET.parse(resource('phase_3.5/dna/storage_tutorial.xml')).getroot()
    scene=ET.parse(resource('phase_3.5/dna/tutorial_street.xml')).getroot()
    library={};models={};textures={}
    for model in storage.findall('model'):
        for entry in model.findall('store_node'):
            library[entry.get('code')]=(model.get('path'),entry.get('node',entry.get('code')))
    for entry in storage.findall('store_texture'):
        textures[entry.get('code')]=app.loader.loadTexture(str(resource(entry.get('path'))))
    root=parent.attachNewNode('ttr-tutorial-street');root.setLightOff()
    def art(code,parent):
        path,node=library[code]
        if path not in models:models[path]=app.loader.loadModel(str(resource(path+'.bam')))
        source=models[path] if not node else models[path].find('**/'+node)
        if source.isEmpty():raise ValueError(f'Tutorial model missing {code}: {node}')
        result=source.copyTo(parent)
        for collision in result.findAllMatches('**/+CollisionNode'):collision.removeNode()
        return result
    def transform(node,element):
        for tag,axes,method in [('pos','xyz',node.setPos),('hpr','hpr',node.setHpr),('scale','xyz',node.setScale)]:
            value=element.find(tag)
            if value is not None:method(*(float(value.get(a,'1' if tag=='scale' else '0')) for a in axes))
        color=element.find('color')
        if color is not None:node.setColorScale(*(float(color.get(a,'1')) for a in 'rgba'))
    def populate(element,parent):
        tag=element.tag
        if tag in ('scene','group','visgroup'):
            for child in element:populate(child,parent)
        elif tag=='flat_building':
            building=parent.attachNewNode(element.get('id'));transform(building,element)
            width=float(element.get('width'));z=0
            for wall in element.findall('wall'):
                height=float(wall.get('height'));node=art(wall.get('code'),building)
                node.setScale(width,1,height);node.setZ(z);transform(node,wall)
                windows=wall.find('windows')
                if windows is not None:
                    count=int(windows.get('count'))
                    for i in range(count):
                        window=art(windows.get('code'),building);transform(window,windows)
                        window.setPos(width*(i+1)/(count+1),-.025,z+height*.55)
                cornice=wall.find('cornice')
                if cornice is not None:
                    trim=art(cornice.get('code'),building);transform(trim,cornice);trim.setScale(width,1,1);trim.setPos(0,-.03,z+height)
                z+=height
        elif tag in ('prop','street','landmark_building','anim_prop'):
            holder=parent.attachNewNode(element.get('name',element.get('id',tag)));transform(holder,element)
            node=art(element.get('code'),holder)
            if tag=='street':
                for tex in element.findall('texture'):
                    code=tex.text;part=code.split('_')[1]
                    for mesh in node.findAllMatches('**/*_'+part):mesh.setTexture(textures[code],1)
            door=element.find('door')
            if door is not None:
                anchor=node.find('**/*door_origin*')
                if not anchor.isEmpty():transform(art(door.get('code'),anchor),door)
            for sign in element.findall('sign'):
                board=art(sign.get('code'),holder);transform(board,sign)
                for baseline in sign.findall('baseline'):
                    group=board.attachNewNode('tutorial-sign-line');transform(group,baseline)
                    text=baseline.find('text')
                    if text is not None:
                        tn=TextNode('tutorial-sign-text');tn.setText(text.text);tn.setAlign(TextNode.ACenter);tn.setFont(app.font)
                        group.attachNewNode(tn)
                    graphic=baseline.find('graphic')
                    if graphic is not None:art(graphic.get('code'),group)
    populate(scene,root)
    # Keep battle/movie coordinates unchanged, centering the XML battle cell.
    # The tutorial road is at -0.5; place its surface at simulator Z=0.
    cell=scene.find('.//battle_cell');scale=.6
    root.setScale(scale);root.setH(90)
    root.setPos(float(cell.get('y'))*scale,-float(cell.get('x'))*scale,-float(cell.get('z'))*scale)
    root.setCollideMask(BitMask32.allOff())
    root.flattenStrong()
    sky=app.loader.loadModel(str(resource('phase_3.5/models/props/TT_sky.bam')))
    sky.reparentTo(parent);sky.setScale(1.5);sky.setZ(-20);sky.setLightOff();sky.setDepthWrite(False);sky.setBin('background',0)
    return root
