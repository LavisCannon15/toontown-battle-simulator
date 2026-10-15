"""Panda3D character assembly from pinned classic reference resources."""
from pathlib import Path
import json,math
from panda3d.core import (NodePath,GeomVertexData,GeomVertexFormat,GeomVertexWriter,GeomVertexReader,GeomTriangles,Geom,GeomNode,LineSegs,Filename,TransparencyAttrib,Point3,Thread)
from direct.actor.Actor import Actor
ROOT=Path(__file__).resolve().parent
from game_resources import TTR as SOURCE,resource
MODELS=json.loads((ROOT/'scene_models.json').read_text())
MOVIES=json.loads((ROOT/'assets/battle_movies.json').read_text())
COLORS=[(.28,.72,.92,1),(.96,.63,.23,1),(.75,.43,.87,1),(.32,.76,.56,1)]
# SuitDNA department palettes and Suit.generateSuit individual hand overrides.
COG_DEPARTMENT_HAND_COLORS={
 'Bossbot':(.95,.75,.75,1),'Lawbot':(.75,.75,.95,1),
 'Cashbot':(.65,.95,.85,1),'Sellbot':(.95,.75,.95,1),
}
COG_HAND_OVERRIDES={
 'Corporate Raider':(.85,.55,.55,1),'The Big Cheese':(.75,.95,.75,1),
 'Bloodsucker':(.95,.95,1,1),'Spin Doctor':(.5,.8,.75,1),
 'Legal Eagle':(.25,.25,.5,1),'Penny Pincher':(1,.5,.6,1),
 'Loan Shark':(.5,.85,.75,1),'Cold Caller':(.55,.65,1,1),
}

def path(name):return Filename.fromOsSpecific(str(resource(name)))

def expose_attachments(actor):
 for old,new in {'def_joint_attachFlower':'jnt_M_attachFlower_01','joint_hips':'jnt_M_attachPelvis_01','def_head':'def_M_head_01','joint_head':'def_M_head_01','joint_attachMeter':'jnt_M_attachMeter_01','joint_Rhold':'jnt_R_attachProp_01','joint_Lhold':'jnt_L_attachProp_01'}.items():
  if actor.find('**/'+old).isEmpty() and actor.getJoints(jointName=new):
   actor.exposeJoint(None,'modelRoot',new).setName(old)
 return actor

def remote_head_anchor(actor):
 # Sample the neutral skull before any props exist. Includes skinned robot
 # heads, whose geometry is not parented beneath the exposed head joint.
 points=[]
 for mesh in actor.findAllMatches('**/+GeomNode'):
  if mesh.isHidden():continue
  for geom in mesh.node().getGeoms():
   reader=GeomVertexReader(geom.getAnimatedVertexData(True,Thread.getCurrentThread()),'vertex')
   while not reader.isAtEnd():points.append(actor.getRelativePoint(mesh,reader.getData3f()))
 top=max(p.z for p in points)
 crown=[p for p in points if p.z>=top-.08]
 center=Point3(sum(p.x for p in crown)/len(crown),sum(p.y for p in crown)/len(crown),top)
 neck=actor.find('**/joint_head')
 return neck.getRelativePoint(actor,center) if not neck.isEmpty() else center

def color_head(head,color,animal):
 # ToonHead.generateToonColor: tint head skin and selected species' ears.
 # Muzzles, noses and mouth interiors keep their authored texture colors.
 for mesh in head.findAllMatches('**/+GeomNode'):
  name=mesh.getName().lower()
  skin=name.startswith('head') or '_head' in name
  ear=('ear' in name and animal in ('cat','rabbit','bunny','bear','mouse','pig'))
  if skin or ear:mesh.clearColorScale();mesh.setColor(*color)

def configure_head(head,variant='short'):
 for mesh in head.findAllMatches('**/+GeomNode'):
  name=mesh.getName().lower()
  hidden=('long' if variant=='short' else 'short') in name or 'lashes' in name or ('eyes' in name and 'neutralopen' not in name) or ('muzzle' in name and 'neutral' not in name)
  mesh.hide() if hidden else mesh.show()

def box(parent,pos,scale,color):
 data=GeomVertexData('box',GeomVertexFormat.getV3n3(),Geom.UHStatic)
 v=GeomVertexWriter(data,'vertex');n=GeomVertexWriter(data,'normal');tri=GeomTriangles(Geom.UHStatic)
 faces=[((0,0,1),[(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]),((0,0,-1),[(-1,1,-1),(1,1,-1),(1,-1,-1),(-1,-1,-1)]),((0,-1,0),[(-1,-1,-1),(1,-1,-1),(1,-1,1),(-1,-1,1)]),((0,1,0),[(1,1,-1),(-1,1,-1),(-1,1,1),(1,1,1)]),((1,0,0),[(1,-1,-1),(1,1,-1),(1,1,1),(1,-1,1)]),((-1,0,0),[(-1,1,-1),(-1,-1,-1),(-1,-1,1),(-1,1,1)])]
 for normal,points in faces:
  start=v.getWriteRow()
  for point in points:v.addData3(*point);n.addData3(*normal)
  tri.addVertices(start,start+1,start+2);tri.addVertices(start,start+2,start+3)
 geom=Geom(data);geom.addPrimitive(tri);node=GeomNode('box');node.addGeom(geom)
 obj=parent.attachNewNode(node);obj.setPos(*pos);obj.setScale(*scale);obj.setColor(*color);return obj

def ring(parent,radius,color,z=.025,thickness=3):
 lines=LineSegs();lines.setThickness(thickness);lines.setColor(*color)
 for i in range(65):
  a=2*math.pi*i/64;p=(radius*math.cos(a),radius*math.sin(a),z)
  if i:lines.drawTo(*p)
  else:lines.moveTo(*p)
 node=parent.attachNewNode(lines.create());node.setLightOff();return node

class CharacterArt:
 def __init__(self,base):
  self.base=base;self.heads={};self.actors=[]
  self.meter_model=base.loader.loadModel(path('phase_3.5/models/gui/matching_game_gui.bam'))
  self.glow_model=base.loader.loadModel(path('phase_3.5/models/props/glow.bam'))
  for body in 'ABC':
   phase='3.5' if body=='C' else '4'
   self.heads[body]=base.loader.loadModel(path(f'phase_{phase}/models/char/suit{body}-heads.bam'))
 def cog(self,cog,parent):
  spec=MODELS[cog.name];body=spec['body'];phase='3.5' if body=='C' else '4'
  if cog.skelecog:
   actor=Actor(path(f'phase_5/models/char/cog{body}_robot-zero.bam'),{'idle':path(f'phase_{phase}/models/char/suit{body}-neutral.bam')})
   expose_attachments(actor);actor.reparentTo(parent);actor.loop('idle');self.actors.append(actor)
   for node in actor.findAllMatches('**/pPlane*'):node.setTwoSided(True)
   dept=__import__('battle_engine').COG_CATALOG[cog.name]['department']
   tie=actor.find('**/tie')
   if not tie.isEmpty():tie.setTexture(self.base.loader.loadTexture(path('phase_5/maps/cog_robot_tie_'+{'Bossbot':'boss','Sellbot':'sales','Lawbot':'legal','Cashbot':'money'}[dept]+'.jpg')),1)
  else:
   actor=Actor(path(f'phase_3.5/models/char/suit{body}-mod.bam'),{'idle':path(f'phase_{phase}/models/char/suit{body}-neutral.bam')})
   expose_attachments(actor);actor.reparentTo(parent);actor.loop('idle');self.actors.append(actor)
   neck=actor.find('**/joint_head')
   for part in spec['heads']:
    node=next(model.find('**/'+part) for model in self.heads.values() if not model.find('**/'+part).isEmpty()).copyTo(neck)
    if spec['texture']:
     file=next(SOURCE.rglob(spec['texture']));node.setTexture(self.base.loader.loadTexture(Filename.fromOsSpecific(str(file))),1)
    if spec['tint']:node.setColorScale(*spec['tint'])
   dept={'Bossbot':'c','Cashbot':'m','Lawbot':'l','Sellbot':'s'}[__import__('battle_engine').COG_CATALOG[cog.name]['department']]
   for name,suffix in [('torso','blazer'),('arms','sleeve'),('legs','leg')]:
    mesh=actor.find('**/'+name)
    if not mesh.isEmpty():mesh.setTexture(self.base.loader.loadTexture(path(f'phase_3.5/maps/{dept}_{suffix}.jpg')),1)
   department=__import__('battle_engine').COG_CATALOG[cog.name]['department']
   hand_color=COG_HAND_OVERRIDES.get(cog.name,COG_DEPARTMENT_HAND_COLORS[department])
   for hands in actor.findAllMatches('**/hands'):
    hands.clearColorScale();hands.setColor(*hand_color)
    # The texture already shades the fingers. Scene ambient + sun washes
    # the pale SuitDNA colors out to white; preserve the resource palette.
    hands.setLightOff()
  actor.loadAnims({name:path(file) for name,file in MOVIES['suits'][cog.name]['anims'].items()})
  actor.loadAnims({'soak':path(f'phase_5/models/char/ttr_a_ene_cg{body.lower()}_soak.bam')})
  actor.loadAnims({'slip-forward':path(f'phase_4/models/char/ttr_a_ene_cg{body.lower()}_slip-forward.bam')})
  actor.loadAnims({'landing':path(f'ttr_a_ene_cg{body.lower()}_landing.bam')})
  actor.loadAnims({'reach':path(f'phase_5/models/char/ttr_a_ene_cg{body.lower()}_walknreach.bam')})
  actor.loadAnims({'flatten':path(f'phase_5/models/char/ttr_a_ene_cg{body.lower()}_drop.bam'),'slip-backward':path(f'phase_4/models/char/ttr_a_ene_cg{body.lower()}_slip-backward.bam')})
  actor.setPythonTag('skelecog',cog.skelecog)
  actor.loadAnims({name:path(f'ttr_a_ene_cg{body.lower()}_{name}.bam') for name in ('song-and-dance','speak','seizecontrol','controlidle')})
  actor.loadAnims({'victory':path(f'phase_4/models/char/suit{body}-victory.bam')})
  actor.pose('idle',0);actor.update(force=True);lo,hi=actor.getTightBounds()
  actor.setPythonTag('remote-head-anchor',remote_head_anchor(actor))
  actor.loop('idle');actor.setScale((2.5/4.14)*.62 if cog.name=='Micromanager' else (3.5+.06*cog.level)/(hi.z-lo.z));actor.setH(180)
  # Cache the neutral model height before props, glow and attack effects exist.
  actor.setPythonTag('nametag-height',actor.getTightBounds(parent)[1].z+.62)
  chest=actor.find('**/joint_attachMeter')
  if chest.isEmpty():raise ValueError('Cog has no chest meter joint: '+cog.name)
  meter=self.meter_model.find('**/minnieCircle').copyTo(chest);meter.setName('cog-health-light');meter.setScale(3);meter.setH(180);meter.setLightOff()
  glow=self.glow_model.copyTo(meter);glow.setScale(.28);glow.setPos(-.005,.01,.015);glow.setTransparency(TransparencyAttrib.MAlpha);glow.setLightOff()
  actor.setPythonTag('health-light',(meter,glow));self.update_health(actor,cog,0)
  return actor
 def update_health(self,actor,cog,now):
  if not actor.hasPythonTag('health-light'):return
  meter,glow=actor.getPythonTag('health-light');fraction=max(0,cog.hp/cog.maximum)
  condition=0 if fraction>.95 else 1 if fraction>.7 else 2 if fraction>.3 else 3 if fraction>.05 else 4
  colors=[(0,1,0,1),(1,1,0,1),(1,.5,0,1),(1,0,0,1),(.3,.3,.3,1)]
  glows=[(.25,1,.25,.5),(1,1,.25,.5),(1,.5,.25,.5),(1,.25,.25,.5),(.3,.3,.3,0)]
  if condition==4:condition=3 if now%(.35 if fraction==0 else .85)<(.25 if fraction==0 else .75) else 4
  meter.setColor(*colors[condition]);glow.setColor(*glows[condition]);meter.setPythonTag('health-condition',condition)
 def toon(self,toon,index,parent):
  actors={};color=COLORS[index]
  for part in ('legs','torso'):
   anims={'idle':path(f'phase_3/models/char/tt_a_chr_dgm_shorts_{part}_neutral.bam')}
   for anim in ('pie-throw','conked'):
    source=f'phase_3.5/models/char/tt_a_chr_dgm_shorts_{part}_{anim}.bam'
    anims[anim]=path(source)
   anims.update({name:path(f'phase_{phase}/models/char/tt_a_chr_dgm_shorts_{part}_{file}.bam') for name,phase,file in [('victory','3.5','victory-dance'),('lose','5','lose')]})
   anims.update({name:path(parts[part]) for name,parts in MOVIES['toon'].items() if part in parts})
   actor=Actor(path(f'phase_3/models/char/tt_a_chr_dgm_shorts_{part}_1000.bam'),anims)
   expose_attachments(actor);actor.loop('idle');self.actors.append(actor);actors[part]=actor
  legs=actors['legs'];torso=actors['torso'];legs.reparentTo(parent);torso.reparentTo(legs.find('**/joint_hips'))
  for actor in (legs,torso):
   for mesh in actor.findAllMatches('**/+GeomNode'):
    name=mesh.getName()
    if any(k in name for k in ('boots','shoes','skirt','naked')):mesh.hide()
    elif any(k in name for k in ('legs','feet','arms','neck')):mesh.clearColorScale();mesh.setColor(*color)
    elif 'shortsBot' in name:mesh.clearColorScale();mesh.setColor(.18,.34,.55,1)
    elif 'shorts' in name:mesh.clearColorScale();mesh.setColor(.95,.65,.3,1)
  if toon.animal=='dog':
   head=Actor(path('phase_3/models/char/tt_a_chr_dgm_shorts_head_1000.bam'),{'idle':path('phase_3/models/char/tt_a_chr_dgm_shorts_head_neutral.bam')})
   head.loadAnims({name:path(f'phase_{phase}/models/char/tt_a_chr_dgm_shorts_head_{file}.bam') for name,phase,file in [('victory','3.5','victory-dance'),('lose','5','lose')]})
   head.loadAnims({name:path(parts['head']) for name,parts in MOVIES['toon'].items() if 'head' in parts})
   head.loop('idle');self.actors.append(head);actors['head']=head
  else:
   species='rabbit' if toon.animal=='bunny' else toon.animal
   head=self.base.loader.loadModel(path(f'phase_3/models/char/{species}-heads-1000.bam'))
   for mesh in head.findAllMatches('**/+GeomNode'):
    name=mesh.getName()
    if 'long' in name or ('muzzle' in name and not name.endswith('neutral')):mesh.hide()
  configure_head(head)
  from toon_expression import Face
  legs.setPythonTag('face-controller',Face(head))
  head.reparentTo(torso.find('**/def_head'))
  color_head(head,color,toon.animal)
  # TTR body/head textures already carry their cartoon shading. The lab's
  # ambient + directional lights tint separately oriented skin meshes and
  # wash out gloves. Keep the resource palette consistent across the Toon.
  legs.setLightOff()
  legs.setScale(.62)
  for actor in actors.values():actor.pose('idle',0);actor.update(force=True)
  height=legs.getTightBounds(parent)[1].z
  legs.setPythonTag('nametag-height',height+.5*.62)
  # Avatar/Toon feeds the animated leg name-tag joint to Nametag3d.
  if legs.getJoints(jointName='jnt_M_nameTag_01'):
   joint=legs.exposeJoint(None,'modelRoot','jnt_M_nameTag_01');legs.update(force=True)
   legs.setPythonTag('nametag-joint',joint)
   legs.setPythonTag('nametag-neutral',joint.getPos(parent))
  for actor in actors.values():actor.loop('idle')
  return actors
 def clear(self):
  for actor in self.actors:actor.cleanup()
  self.actors=[]
