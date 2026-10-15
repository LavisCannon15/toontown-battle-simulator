"""TTR Throw Book reconstruction: head landing, jump miss, preserved prop size.
The classic source only dispatches doDefault for this attack. Release is retained
from our existing movie; flight/landing cues are not verified modern TTR constants.
"""
from panda3d.core import Vec3
from direct.interval.IntervalGlobal import Sequence,Parallel,Wait,Func,ActorInterval,LerpPosInterval,LerpScaleInterval
from cog_choreography import AUDIT
from classic_cog_movies import arc
from battle_movies import MOVIES

RELEASE=3.03
FLIGHT=1.2
IMPACT=RELEASE+FLIGHT

def movie(app,event):
 i=event['cog'];t=event['targets'][0];actor=app.cog_actors[i];root=app.cog_nodes[i];toon=app.toon_nodes[t];hit=t not in event['misses']
 recipe=next(p for p in AUDIT[app.game.cogs[i].name+'|Throw Book']['props'] if p['name']=='lawbook')
 book,_=app.movie_prop('lawbook',None);hand=actor.find('**/joint_Rhold')
 head=app.toon_actors[t]['torso'].find('**/def_head').getChild(0)
 def hold():
  book.reparentTo(hand);book.setPos(*recipe['pos']);book.setHpr(*recipe['hpr']);book.setScale(*recipe['scale']);book.show()
 def release():
  book.wrtReparentTo(app.render)
  # The model's broad X/Y cover lies flat; retain its world size at detachment.
  book.setHpr(toon,0,0,0)
 def destination():
  if hit:
   lo,hi=head.getTightBounds(app.render);contact=Vec3((lo.x+hi.x)/2,(lo.y+hi.y)/2,hi.z)
  else:contact=toon.getPos(app.render)+Vec3(0,-1.8,.04)
  lo,hi=book.getTightBounds(app.render);offset=Vec3((lo.x+hi.x)/2,(lo.y+hi.y)/2,lo.z)-book.getPos(app.render)
  return contact-offset
 path=Sequence(Wait(recipe.get('delay',.15)),Func(hold),Wait(RELEASE-recipe.get('delay',.15)),Func(release),arc(book,destination,FLIGHT))
 if hit:path.append(Func(book.wrtReparentTo,head))
 else:path.append(LerpPosInterval(book,.3,lambda:book.getPos()+Vec3(0,-.7,0)))
 path.append(Wait(.55));path.append(LerpScaleInterval(book,.2,.000001));path.append(Func(book.hide))
 anim=MOVIES['suits'][app.game.cogs[i].name]['attacks']['Throw Book'];native=actor.getDuration(anim);heading=Vec3(root.getHpr())
 def face():root.headsUp(toon);root.setH(root.getH()-actor.getH())
 effects=[path,app.health_movie(dict(event,reaction='conked',dodge='jump',dodge_at=IMPACT-.65),IMPACT)]
 for sound in MOVIES['cog_sounds'].get('throwbook',[]):effects.append(Sequence(Wait(RELEASE),app.sound_clip(sound)))
 duration=max(native,*[c.getDuration() for c in effects])
 effects.extend([Sequence(Func(face),ActorInterval(actor,anim),Wait(duration-native),Func(root.setHpr,heading),Func(app.restore_cog_pose,i)),app.attack_caption(i,'Throw Book',duration)])
 return Parallel(*effects)
