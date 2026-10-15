"""Reference-derived attack timings and attachments; unresolved choreography is reported."""
import json,re
from pathlib import Path
from panda3d.core import Vec3,Vec4
from direct.interval.IntervalGlobal import Sequence,Parallel,Func,Wait,ActorInterval,LerpPosInterval,LerpScaleInterval
from battle_movies import MOVIES
ROOT=Path(__file__).resolve().parent
AUDIT=json.loads((ROOT/'assets/cog_attack_audit.json').read_text())
PARTICLES=json.loads((ROOT/'assets/cog_particle_map.json').read_text())
THROWN={'lawbook','clip-on-tie','pink-slip','sandbag','can','half-windsor','baseball','power-tie','newspaper','teeth','shredder-paper','bounced-check'}

def time_value(value,duration,fallback):
 if isinstance(value,dict):return max(0,value['offset']+value['duration']*duration)
 return value if isinstance(value,(int,float)) else fallback

def prop_movie(app,event,recipe,duration,impact,throw=False):
 index=event['cog'];actor=app.cog_actors[index];name=recipe['name'];prop,animated=app.movie_prop(name,None)
 parent=actor if recipe.get('parent')=='suit' else actor.find('**/joint_'+('Lhold' if recipe.get('parent')=='left' else 'Rhold'))
 if parent.isEmpty():parent=actor
 pos=recipe.get('pos') or [0,0,0];hpr=recipe.get('hpr') or [0,0,0];scale=recipe.get('scale') or [1,1,1];delay=max(0,recipe.get('delay') or 0)
 def attach():prop.reparentTo(parent);prop.setPos(*pos);prop.setHpr(*hpr);prop.setScale(*scale);prop.show()
 # Pick Pocket borrows the dollar model, not its fishing/lure animation.
 # MovieSuitAttacks.doPickPocket uses getPropTrack with anim=0.
 if event['name']=='Pick Pocket' and name=='1dollar':
  return prop,Sequence(Wait(delay),Func(attach),
   LerpScaleInterval(prop,.5,Vec3(*scale),startScale=Vec3(.01)),
   Wait(.55),LerpScaleInterval(prop,.5,.001),Func(prop.hide))
 path=[Wait(delay),Func(attach)]
 if throw and event['targets']:
  target=event['targets'][0];dest=app.toon_nodes[target].getPos()+Vec3(1.8 if target in event['misses'] else 0,0,2)
  path.extend([Wait(max(0,impact-.4-delay)),Func(prop.wrtReparentTo,app.render),LerpPosInterval(prop,.4,dest),Wait(.3)])
 else:path.append(Wait(max(.3,duration-delay)))
 path.extend([LerpScaleInterval(prop,.2,.001),Func(prop.hide)])
 return prop,Parallel(Sequence(*path),Sequence(Wait(delay),ActorInterval(animated,'prop')) if animated else Wait(0))

def movie(app,event):
 index=event['cog'];name=event['name'];actor=app.cog_actors[index];cog=app.game.cogs[index]
 recipe=AUDIT[cog.name+'|'+name];key=re.sub('[^a-z0-9]','',name.lower());anim=MOVIES['suits'][cog.name]['attacks'][name]
 native=actor.getDuration(anim);old=MOVIES.get('attack_timing',{}).get(key,{})
 impact=time_value(recipe.get('impact'),native,old.get('impact',native*.62))
 dodge_at=time_value(recipe.get('dodge_at'),native,old.get('dodge_at',max(0,impact-.5)))
 reaction=recipe.get('reaction') or old.get('reaction','conked')
 dodge=recipe.get('dodge') or old.get('dodge',MOVIES['dodges'].get(key,'sidestep-left'))
 if dodge=='sidestep':dodge='sidestep-left'
 if not any(reaction in a.getAnimNames() for a in app.toon_actors[0].values()):reaction='conked'
 duration=max(native,impact+1.2,dodge_at+1.5)
 event=dict(event,reaction=reaction,dodge=dodge,dodge_at=dodge_at)
 origin=Vec3(app.cog_nodes[index].getHpr())
 # Source single-target movies face their chosen Toon and restore formation heading.
 def face_target():
  app.cog_nodes[index].headsUp(app.toon_nodes[event['targets'][0]])
  app.cog_nodes[index].setH(app.cog_nodes[index].getH()-actor.getH())
 face=Func(face_target) if len(event['targets'])==1 else Wait(0)
 reactions=[];health_at=impact
 if name=='Chomp':
  from chomp_reaction import schedule,DAMAGE_AT
  reactions=schedule(app,event);health_at=DAMAGE_AT
 clips=[Sequence(face,ActorInterval(actor,anim),Wait(max(0,duration-native)),Func(app.cog_nodes[index].setHpr,origin),Func(app.restore_cog_pose,index)),app.attack_caption(index,name,duration),app.health_movie(event,health_at),*reactions]
 sounds=recipe.get('sounds') or [{'file':s,'delay':.5+i*.55} for i,s in enumerate(MOVIES['cog_sounds'].get(key,[]))]
 if name=='Pick Pocket' and not any(t not in event['misses'] for t in event['targets']):sounds=[]
 for sound in sounds:
  clips.append(Sequence(Wait(max(0,sound.get('delay') or 0)),app.sound_clip(sound['file'])))
 props={p['name']:p for p in recipe.get('props',[])}
 if name in ('Hang Up','Pound Key'):
  # Receiver changes hands during the phone gesture.
  props={'phone':dict(name='phone',parent='left',pos=[.23,.17,-.11],hpr=[5.939,2.763,-177.591],scale=[1]*3,delay=.3),'receiver':dict(name='receiver',parent='right',pos=[-.45,.48,-.62],hpr=[-87.47,-18.21,7.82],scale=[1]*3,delay=1.54)}
 if name=='Fountain Pen':props['pen']=dict(name='pen',parent='right',scale=[1.5]*3,delay=.01)
 # Clouds belong above their caster/target, never in a hand.
 cloud_attack=name in ('Brain Storm','Freeze Assets','Liquidate')
 held={}
 for prop in MOVIES['attack_props'].get(key,[]):
  if name=='Pick Pocket' and not any(t not in event['misses'] for t in event['targets']):continue
  if cloud_attack and prop in ('stormcloud','quicksand'):continue
  if prop=='redtape-tube' or (name=='Glower Power' and prop=='dagger'):continue
  record=props.get(prop,dict(name=prop,parent='left' if prop in ('pad','sharpener','calculator','watercooler') else 'right',scale=[1]*3))
  thrown=prop in THROWN and (anim in ('throw-paper','throw-object') or name in ('Clip on Tie','Half Windsor','Power Tie','Market Crash','Bite','Chomp','Eviction Notice','Restraining Order'))
  held[prop],clip=prop_movie(app,event,record,duration,impact,thrown);clips.append(clip)
 if name=='Glower Power':
  for target in event['targets']:
   for side in (-1,1):
    for n in range(3):
     knife,a=app.movie_prop('dagger',None);knife.reparentTo(actor);knife.setPos(side*.4,3.8,4.1);knife.setScale(.4)
     dest=app.toon_nodes[target].getPos()+Vec3(1.8 if target in event['misses'] else 0,0,2)
     clips.append(Sequence(Wait(1.1+n*.11),Func(knife.show),Func(knife.wrtReparentTo,app.render),LerpPosInterval(knife,.3,dest),Func(knife.hide)))
 if name in ('Fountain Pen','Watercooler'):
  from audited_gags import stream
  prop=held['pen' if name=='Fountain Pen' else 'watercooler']
  tip=prop.find('**/joint_toSpray');tip=prop if tip.isEmpty() else tip
  for target in event['targets']:
   dest=app.toon_nodes[target].getPos()+Vec3(1.8 if target in event['misses'] else 0,0,2)
   clips.append(stream(app,lambda n=tip:n.getPos(app.render),lambda p=dest:p,max(0,impact-.2),.10 if name=='Fountain Pen' else .3,.2,color=(0,0,0,1) if name=='Fountain Pen' else (.75,.75,1,.8)))
 if cloud_attack:
  cloud,a=app.movie_prop('stormcloud',None);cloud.setPos(app.cog_nodes[index].getPos()+Vec3(0,0,4.3));cloud.setScale(.9)
  clips.append(Sequence(Func(cloud.show),app.prop_clip(a,duration),Func(cloud.hide)))
  from audited_gags import stream
  for target in event['targets']:
   end=app.toon_nodes[target].getPos()+Vec3(1.8 if target in event['misses'] else 0,0,2)
   clips.append(stream(app,lambda n=cloud:n.getPos(),lambda p=end:p,max(0,impact-.3),.15,.7))
   if name=='Liquidate' and target not in event['misses']:clips.append(Sequence(Wait(impact-.5),app.positioned_prop('quicksand',end-Vec3(0,0,1.95),3,1.5)))
 for item in recipe.get('particles',[]):
  stem=PARTICLES.get(item['effect'])
  if not stem:continue
  owners=[actor] if item['parent']=='suit' else [app.toon_nodes[i] for i in event['targets'] if i not in event['misses']] if item['parent']=='target' else []
  for owner in owners:
   effect=app.source_particle(stem,index)
   if owner is not actor:effect.setScale(effect.getScale()*.62);effect.setPos(effect.getPos()*.62)
   if item.get('texture'):
    art=app.loader.loadModel(str(__import__('game_resources').resource('phase_3.5/models/props/suit-particles.bam')))
    app.movie_props.append((art,None));sprite=art.find('**/'+item['texture'])
    for system in effect.getParticlesList():
     system.renderer.setFromNode(sprite)
     if item.get('color'):system.renderer.setColor(Vec4(*item['color']))
   if name=='Finger Wag':effect.setPos(.167,1.8,5 if 'suitB' in MOVIES['suits'][cog.name]['anims'][anim] else 4.1)
   clips.append(Sequence(Wait(time_value(item['delay'],native,0)),Func(effect.start,owner),Wait(time_value(item['duration'],native,1)),Func(effect.softStop),Wait(1),Func(effect.disable)))
 return Parallel(*clips)
