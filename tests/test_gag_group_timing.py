"""Multi-performer regressions: single-gag smoke tests cannot catch batching bugs."""
import unittest
from unittest.mock import patch
from types import SimpleNamespace
from direct.interval.IntervalGlobal import Wait
from battle_engine import Action
import squirt_sequence,throw_sequence,drop_sequence,sound_sequence
class GroupTiming(unittest.TestCase):
 def test_regular_targeted_tracks(self):
  for module,gag,step in [(throw_sequence,'Cupcake',.5),(squirt_sequence,'Fire Hose',.5),(drop_sequence,'Grand Piano',.8)]:
   e=dict(actions=[Action(i,gag,0) for i in range(4)],targets={i:[0] for i in range(4)})
   result=module.schedule(e)
   if module is not squirt_sequence:result=result[0]
   self.assertEqual([round(t,2) for a,t in result],[round(i*step,2) for i in range(4)])
 def test_sound_same_level_together_mixed_separate(self):
  a=[Action(0,'Bike Horn'),Action(1,'Bike Horn'),Action(2,'Foghorn')]
  self.assertEqual([t for a,t in sound_sequence.schedule(a)],[0,0,2])
 def test_mixed_geyser_uses_scheduler_and_per_target_contact(self):
  events=[];health=[]
  def geyser(e):
   events.append(e);e['geyser_contacts']={0:3.2,1:3.6};return Wait(6)
  app=SimpleNamespace(geyser_movie=geyser,health_movie=lambda e,t:(health.append((e,t)) or Wait(t)))
  e=dict(actions=[Action(0,'Fire Hose',0),Action(1,'Geyser')],targets={0:[0],1:[0,1]},health=[('cog',0,-100),('cog',1,-90)],misses=[])
  with patch('audited_gags.squirt',return_value=(Wait(4),3)):
   movie=squirt_sequence.movie(app,e)
  self.assertEqual(movie.getDuration(),6.5)
  self.assertEqual([round(t,2) for e,t in health],[3.7,4.1])
  self.assertTrue(all(e['custom_cog_reaction'] for e,t in health))
  self.assertEqual([h for e,t in health for h in e['health']],e['health'])
  self.assertTrue(events[0]['scheduled_geyser'])
