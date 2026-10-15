"""MovieSuitAttacks.doChomp's spliced cringe/spit reaction, using TTR clips."""
from direct.interval.IntervalGlobal import Sequence,Parallel,Wait,Func,ActorInterval

REACTION_AT=3.2
DAMAGE_AT=4.6
STAGES=(('cringe',.01,.7,1.2),('spit',.01,2.95,1.47),
        ('spit',.01,4.42,.07),('spit',.08,4.49,-.07),
        ('spit',.08,4.42,.07),('spit',.08,4.49,-.07),
        ('spit',.08,4.42,.07),('spit',.08,4.49,-.07),
        ('spit',.01,4.42,None))

def reaction(app,index):
 track=Sequence()
 for name,delay,start,length in STAGES:
  args={} if length is None else {'endTime':start+length} if length<0 else {'duration':length}
  track.append(Wait(delay))
  track.append(Parallel(*(ActorInterval(a,name,startTime=start,**args)
                         for a in app.toon_actors[index].values() if name in a.getAnimNames())))
 def idle():
  if app.game.toons[index].alive:app.play_toon_animation(index,'idle',True)
 track.append(Func(idle))
 return track

def schedule(app,event):
 # Separate intervals can be stopped immediately by live_health on a fatal hit.
 tracks={};clips=[]
 for index in event['targets']:
  if index in event.get('misses',[]):continue
  track=reaction(app,index);tracks[index]=[track]
  def start(index=index,track=track):
   if app.game.toons[index].alive:
    app.live_departures=getattr(app,'live_departures',[])+[track];track.start()
  clips.append(Sequence(Wait(REACTION_AT),Func(start),Wait(track.getDuration())))
 event.update(custom_toon_reaction=True,custom_toon_tracks_by_index=tracks)
 return clips
