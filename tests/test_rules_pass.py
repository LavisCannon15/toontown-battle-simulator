import unittest
from battle_engine import Battle,Action,Cog
from support import use_unite,resolve_support,doodle_stats,remote_tick,REMOTES
from combat_rules import capped_accuracy,cog_accuracy,doodle_values

class RulesPass(unittest.TestCase):
 def test_cap_is_explicit_and_cog_debuff_has_floor(self):
  self.assertEqual(capped_accuracy(220),95)
  self.assertEqual(cog_accuracy(50,True),5)
  self.assertEqual(cog_accuracy(95,True),20)
 def test_raw_formula_tracks_training_and_defense(self):
  b=Battle('Hard');a=Action(0,'Birthday Cake',0)
  self.assertEqual(b.accuracy([a],[0],capped=False),80)
  b.toons[0].track_levels['Throw']=6
  self.assertEqual(b.accuracy([a],[0],capped=False),70)
  b.cogs=[Cog('Flunky',5)];self.assertEqual(b.accuracy([a],[0],capped=False),110)
  b.cogs=[Cog('Flunky',12)];self.assertEqual(b.accuracy([a],[0],capped=False),70)
 def test_railroad_replaces_old_traps_but_simultaneous_traps_cancel(self):
  b=Battle('Hard');b.cog_phase=lambda:None;b.cogs[0].trap=('TNT',180)
  for i in range(4):b.plan(Action(i,'Railroad') if i==0 else Action(i))
  b.resolve();self.assertEqual(b.cogs[0].trap,('Railroad',200))
  b=Battle('Hard');b.cog_phase=lambda:None
  for i in range(4):b.plan(Action(i,'Railroad') if i==0 else Action(i,'Banana Peel',0) if i==1 else Action(i))
  b.resolve();self.assertIsNone(b.cogs[0].trap)
 def test_railroad_does_not_override_simultaneous_sos_trap(self):
  b=Battle('Hard');b.cog_phase=lambda:None
  for i in range(4):b.plan(Action(i,'Railroad') if i==0 else Action(i,'SOS: Clerk Clara') if i==1 else Action(i))
  b.resolve();self.assertTrue(all(c.trap is None for c in b.cogs))
 def test_doodle_fractional_accuracy_training_and_no_xp_on_failure(self):
  self.assertEqual(doodle_values(5000,0),(7,73.5))
  self.assertAlmostEqual(doodle_values(10000,6)[1],38.8)
  b=Battle();t=b.toons[0];t.doodle_trained=False;b.rng.random=lambda:0
  for member in b.toons:member.hp=10
  resolve_support(b,Action(0,'Doodle: Jump'),early=True)
  self.assertEqual(t.doodle_skills['Doodle: Jump'],5);self.assertEqual(t.hp,15)
  b.rng.random=lambda:.999;resolve_support(b,Action(0,'Doodle: Jump'),early=True)
  self.assertEqual(t.doodle_skills['Doodle: Jump'],5)
 def test_unites_reach_only_nearby_living_toons_and_keep_plans(self):
  b=Battle();b.toons[3].hp=0
  for t in b.toons[:3]:t.hp=10
  b.plan(Action(1,'Cupcake',0));plans=b.plans.copy()
  recipients=use_unite(b,1,'Unite: Toon-Up 20',[(0,0,0),(1,0,0),(40,0,0),(2,0,0)],radius=30)
  self.assertEqual(recipients,[0,1]);self.assertEqual([t.hp for t in b.toons],[30,30,10,0]);self.assertEqual(b.plans,plans)
  self.assertEqual(b.toons[1].unite_cooldown,3);self.assertEqual(b.toons[0].unite_cooldown,0)
 def test_remote_expiry_preserves_v2_state_and_does_not_attack(self):
  b=Battle('Hard');b.cogs=[Cog('The Big Cheese',12,version2=True)];c=b.cogs[0]
  c.remote=REMOTES['Healing remote 1★'];c.hp=1
  remote_tick(b,0);remote_tick(b,0)
  self.assertTrue(c.skelecog);self.assertEqual(c.hp,196);self.assertIsNone(c.remote)
if __name__=='__main__':unittest.main()
