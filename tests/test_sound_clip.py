"""Audio excerpts must seek before playing and preserve their requested duration."""
import unittest
from types import SimpleNamespace
from battle_movies import BattleMovies

class Sound:
 def __init__(self):self.calls=[]
 def length(self):return 4.5
 def setVolume(self,value):self.calls.append(('volume',value))
 def setTime(self,value):self.calls.append(('seek',value))
 def play(self):self.calls.append(('play',))
 def stop(self):self.calls.append(('stop',))

class SoundClipTests(unittest.TestCase):
 def app(self,enabled=True):
  sound=Sound()
  return SimpleNamespace(loader=SimpleNamespace(loadSfx=lambda path:sound),sounds_enabled=enabled),sound
 def test_death_excerpt_seeks_and_stops_at_requested_duration(self):
  app,sound=self.app()
  clip=BattleMovies.sound_clip(app,'Cog_Death.ogg',1.2,start_time=1.5,volume=.2)
  clip.setT(.01)
  self.assertEqual(sound.calls,[('volume',.2),('seek',1.5),('play',)])
  self.assertEqual(clip.getDuration(),1.2)
  clip.finish();self.assertEqual(sound.calls[-1],('stop',))
  self.assertEqual(app.movie_sounds,[sound])
 def test_excerpt_without_duration_uses_remaining_audio(self):
  app,sound=self.app()
  clip=BattleMovies.sound_clip(app,'Cog_Death.ogg',start_time=1.5)
  self.assertEqual(clip.getDuration(),3)
 def test_muted_cue_does_not_seek_or_play(self):
  app,sound=self.app(False)
  clip=BattleMovies.sound_clip(app,'Cog_Death.ogg',1.2,start_time=1.5,volume=.2)
  clip.setT(.01);clip.finish()
  self.assertEqual(sound.calls,[('stop',)])
if __name__=='__main__':unittest.main()
