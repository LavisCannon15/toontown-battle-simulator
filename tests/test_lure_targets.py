import unittest
from lure_targets import fresh_targets
class LureTargets(unittest.TestCase):
 def test_group_lure_only_reacts_on_fresh_cog(self):
  self.assertEqual(fresh_targets({'lure_before':[3,2,1,0]},[0,1,2,3]),[3])
 def test_pre_action_status_survives_updated_engine_state(self):
  self.assertEqual(fresh_targets({'lure_before':[0,2],'lure_after':[3,1]},[0,1]),[0])
 def test_older_events_keep_targets(self):
  self.assertEqual(fresh_targets({},[0,1]),[0,1])
