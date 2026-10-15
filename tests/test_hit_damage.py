import unittest
from hit_damage import schedule
class HitDamageTests(unittest.TestCase):
 def event(self,total=136):
  return dict(health=[('cog',0,-total)],damage_by_action={0:{0:40,1:40}},damage_components={0:dict(base=80,knockback=40,combo=16)})
 def test_hits_and_bonuses_have_separate_contacts(self):
  rows=schedule(self.event(),0,[(3.5,1),(3,0)])
  self.assertEqual([(r[0],r[1],r[3]) for r in rows],[(3,40,0),(3.5,40,0),(4.25,40,2),(5,16,1)])
  self.assertEqual(sum(r[2] for r in rows),136)
 def test_overkill_never_applies_total_twice(self):
  rows=schedule(self.event(45),0,[(3,0),(3.5,1)])
  self.assertEqual([r[2] for r in rows],[40,5,0,0])
 def test_old_events_keep_compatible_fallback(self):
  self.assertIsNone(schedule({'health':[]},0,[]))
