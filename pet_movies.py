"""Bundled TTR Doodle rig and PetTricks animation sequences."""
from panda3d.core import Vec3,Texture
from direct.actor.Actor import Actor
from direct.interval.IntervalGlobal import Sequence,Parallel,Func,Wait,ActorInterval,ProjectileInterval
from game_resources import SOURCE

TRICKS={'Jump':['jump'],'Beg':['toBeg','beg','fromBeg'],'Play Dead':['playDead','fromPlayDead'],
        'Rollover':['rollover'],'Backflip':['backflip'],'Dance':['dance'],'Speak':['speak']}
ANIMS={'neutral':('4','neutral'),'sad':('4','neutral_sad'),'reappear':('5','reappear'),
       'toDig':('5','intoDig'),'dig':('5','dig'),'disappear':('5','disappear'),'jump':('5','jump'),'toBeg':('5','intoBeg'),
       'beg':('5','beg'),'fromBeg':('5','begOut'),'playDead':('5','playdead'),
       'fromPlayDead':('5','deadend'),'rollover':('5','rollover'),'backflip':('5','backflip'),
       'dance':('5','heal'),'speak':('5','speak')}
SOUNDS={'Jump':'jump.ogg','Beg':'beg.ogg','Play Dead':'play_dead.ogg','Rollover':'rollover.ogg',
        'Backflip':'backflip.ogg','Dance':'heal_dance.ogg','Speak':'speak_v1.ogg'}

def create_doodle(app):
    holder=app.render.attachNewNode('battle-doodle');holder.setPos(0,-.5,0);holder.setH(180)
    pet=Actor(str(SOURCE/'phase_4/models/char/TT_pets-mod.bam'),
              {n:str(SOURCE/f'phase_{phase}/models/char/TT_pets-{file}.bam') for n,(phase,file) in ANIMS.items()})
    pet.reparentTo(holder);pet.setScale(.62)
    for part in ('feathers','horns','antennae','catEars','rabbitEars','clownNose','ovalNose','pigNose','catTail','longTail','birdTail'):
        node=pet.find('**/'+part)
        if not node.isEmpty():node.hide()
    # PetDNA orange; use one body/appendage color rather than tinting the
    # extracted model's pre-colored green palette a second time.
    color=(.992188,.480469,.167969,1)
    for part in ('body','leftFoot','rightFoot','dogEars','bunnyTail','dogNose'):
        node=pet.find('**/'+part)
        if not node.isEmpty():
            node.setColor(*color,1)
            if part in ('dogEars','bunnyTail','dogNose'):
                # PetDNA assigns no pattern texture to these appendages.
                # TTR's bundled atlas contains the export's original color.
                node.setTextureOff(1)
    for part,file in [('body','BeanbodyTummy6.jpg'),('leftFoot','BeanFoot6.jpg'),('rightFoot','BeanFoot6.jpg')]:
        node=pet.find('**/'+part)
        if not node.isEmpty():
            texture=app.loader.loadTexture(str(SOURCE/f'phase_4/maps/{file}'))
            texture.setMinfilter(Texture.FTLinear);texture.setMagfilter(Texture.FTLinear)
            node.setTexture(texture,1)
    eyes=pet.find('**/eyeWhites')
    texture=app.loader.loadTexture(str(SOURCE/'phase_4/maps/BeanEyeBoys2.jpg'),str(SOURCE/'phase_4/maps/BeanEyeBoys2_a.rgb'))
    texture.setMinfilter(Texture.FTLinear);texture.setMagfilter(Texture.FTLinear)
    eyes.setTexture(texture,1)
    for part in ('eyeWhites','rightHighlight','leftHighlight'):
        node=pet.find('**/'+part)
        if not node.isEmpty():node.setColor(1,1,1,1,1);node.setTwoSided(True)
    for part in ('rightPupil','leftPupil','rightBrow','leftBrow'):
        node=pet.find('**/'+part)
        if not node.isEmpty():node.setColor(.08,.06,.03,1);node.setTwoSided(True)
    holder.hide();app.movie_props.append((holder,pet))
    return holder,pet

def doodle_movie(app,action,event):
    holder,pet=create_doodle(app);trick=action.gag.removeprefix('Doodle: ')
    success=event.get('doodle_success',True)
    if success:
        performance=Sequence(*(ActorInterval(pet,n) for n in TRICKS[trick]))
        if trick=='Rollover':performance.append(ActorInterval(pet,'rollover',playRate=-1))
        if trick=='Jump':
            performance=Parallel(performance,Sequence(Wait(.36),ProjectileInterval(holder,startPos=holder.getPos(),endPos=holder.getPos(),duration=1,gravityMult=.31)))
        performance=Parallel(performance,app.sound_clip(SOUNDS[trick]))
    else:
        tn=__import__('panda3d.core',fromlist=['TextNode']).TextNode('doodle-failure');tn.setText('?');tn.setFont(app.font)
        mark=holder.attachNewNode(tn);mark.setZ(1.7);mark.setScale(.65);mark.setBillboardPointEye();mark.hide()
        performance=Sequence(Func(mark.show),Parallel(ActorInterval(pet,'sad'),Wait(1)),Func(mark.hide))
    hole=Actor(str(SOURCE/'phase_3.5/models/props/portal-mod.bam'),{'hole':str(SOURCE/'phase_3.5/models/props/portal-chan.bam')})
    hole.reparentTo(pet);hole.setScale(.75);hole.setPos(0,-1,.01);hole.setBin('fixed',0);hole.setDepthWrite(False);hole.hide()
    app.movie_props.append((hole,hole))
    def opening():return ActorInterval(hole,'hole',startFrame=81,endFrame=71)
    def closing():return ActorInterval(hole,'hole',startFrame=71,endFrame=81)
    arrival=Sequence(Wait(1),Parallel(app.sound_clip('teleport_reappear.ogg'),Sequence(Func(holder.show),Func(pet.pose,'reappear',0),Func(hole.show),opening(),ActorInterval(pet,'reappear'),closing(),Func(hole.hide))))
    departure=Sequence(Wait(1),Parallel(app.sound_clip('teleport_disappear.ogg'),Sequence(ActorInterval(pet,'toDig'),Parallel(ActorInterval(pet,'dig'),Sequence(Func(hole.show),opening())),ActorInterval(pet,'disappear'),closing(),Func(hole.hide))),Func(holder.hide))
    holder.setPythonTag('trick_start',2.4+arrival.getDuration())
    return Sequence(app.toon_clip(action.toon,'callPet',2.4),arrival,performance,Parallel(Wait(2),app.health_movie(event,0)),departure)
