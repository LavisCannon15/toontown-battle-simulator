import unittest
from copy import deepcopy
from battle_engine import Battle,Action

class EventAttribution(unittest.TestCase):
 def resolve(self,b,actions):
  b.roll=lambda chance:chance>0;b.cog_phase=lambda:None
  for i in range(len(b.toons)):b.plan(actions.get(i,Action(i)))
  b.resolve()
 def test_sos_and_regular_damage_have_separate_health(self):
  b=Battle('Hard');self.resolve(b,{0:Action(0,'SOS: Rocky'),1:Action(1,'Cupcake',0)})
  event=next(e for e in b.movie_events if e.get('track')=='Throw')
  self.assertEqual(event['regular_health'],[('cog',0,-6)])
  self.assertEqual(event['support_events'][0]['health'],[('cog',i,-132) for i in range(4)])
  self.assertEqual(b.cogs[0].hp,58)
 def test_sos_heal_survives_two_regular_healers(self):
  b=Battle('Hard')
  for t in b.toons:t.hp=10
  self.resolve(b,{0:Action(0,'SOS: Flippy'),1:Action(1,'Feather',2),2:Action(2,'Feather',3)})
  e=next(e for e in b.movie_events if e.get('track')=='Toon-Up')
  self.assertEqual(sum(n for k,i,n in e['support_events'][0]['health']),180)
  self.assertEqual(sum(n for k,i,n in e['regular_health']),20)
  self.assertEqual([t.hp for t in b.toons],[55,55,65,65])
 def test_lure_state_recorded_before_each_sos_and_regular(self):
  b=Battle('Hard');b.cogs[0].lure=2
  self.resolve(b,{0:Action(0,'SOS: Lil Oldman'),1:Action(1,'Big Magnet')})
  e=next(e for e in b.movie_events if e.get('track')=='Lure')
  self.assertEqual(e['support_events'][0]['lure_before'],[2,0,0,0])
  self.assertTrue(all(e['regular_lure_before']))
 def test_identical_toons_keep_separate_cog_target_indices(self):
  b=Battle('Hard');b.toons=[deepcopy(b.toons[0]) for _ in range(4)]
  b.rng.choices=lambda options,weights:[next(a for a in options if a['group'])]
  b.roll=lambda chance:False
  event=next(b.cog_events())
  self.assertEqual(event['targets'],[0,1,2,3]);self.assertEqual(event['misses'],[0,1,2,3])
