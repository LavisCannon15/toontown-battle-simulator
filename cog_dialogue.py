"""Classic attack taunts with bundled chatbox and Suit voice families."""
import json,random,re
from pathlib import Path
from panda3d.core import TextNode,Vec3
from direct.interval.IntervalGlobal import Sequence,Parallel,Func,Wait
from game_resources import resource
TAUNTS=json.loads((Path(__file__).parent/'assets/cog_attack_taunts.json').read_text())
def movie(app,event,duration):
 index=event['cog'];actor=app.cog_actors[index]
 key=re.sub('[^a-z]','',event['name'].lower())
 choices=next((v for k,v in TAUNTS.items() if re.sub('[^a-z]','',k.lower())==key and v),['Take that!','Take a memo on this!'])
 if not hasattr(app,'presentation_rng'):app.presentation_rng=random.Random()
 phrase=app.presentation_rng.choice(choices)
 return speech(app,index,phrase,min(duration,4))

def speech(app,index,phrase,duration,voice_enabled=True):
 actor=app.cog_actors[index]
 root=app.cog_nodes[index].attachNewNode('cog-speech-bubble');root.setZ(actor.getPythonTag('nametag-height'))
 root.setBillboardPointEye();root.setLightOff();root.hide();app.movie_props.append((root,None))
 from speech_balloon import build
 build(app,root,phrase)
 # Suit.loadDialog maps exclamations to statement and questions to question.
 voice='question' if '?' in phrase else 'statement' if '!' in phrase or len(phrase)>20 else 'murmur' if len(phrase)>10 else 'grunt'
 prefix='Skel_COG_VO_' if actor.getPythonTag('skelecog') else 'COG_VO_'
 def show():
  root.show();app.position_nametags()
 def hide():
  root.hide();app.position_nametags()
 return Parallel(Sequence(Func(show),Wait(duration),Func(hide)),app.sound_clip(prefix+voice+'.ogg') if voice_enabled else Wait(0))


def remote_joke(app,event,impact,duration):
 """Observed setup/punchline/replies; text is isolated pending TTR transcription."""
 index=event['cog']
 data=json.loads((Path(__file__).parent/'assets/remote_joke_dialogue.json').read_text())
 if not hasattr(app,'presentation_rng'):app.presentation_rng=random.Random()
 setup,punchline=app.presentation_rng.choice(data['jokes'])
 split=impact/2
 clips=[Sequence(speech(app,index,setup,split,False),
                 speech(app,index,punchline,duration-split,False))]
 # Use this event's recipients, not end-of-round alive state: a Cog can
 # still speak here even if a later attack defeats it.
 targets=list(dict.fromkeys(i for side,i,delta in event.get('health',[])
                           if side=='cog' and i!=index and delta<0))
 for slot,target in enumerate(targets):
  clips.append(Sequence(Wait(impact),speech(app,target,
               data['responses'][slot%len(data['responses'])],duration-impact,False)))
 return Parallel(*clips)
