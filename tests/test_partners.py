"""Trap selection regressions and independent practice-partner decisions."""
import unittest,random
from copy import deepcopy
from battle_engine import Battle,Action,GAGS
from auto_toons import choose_action

class TrapRules(unittest.TestCase):
 def test_all_lured_rejects_every_trap_without_mutation(self):
  b=Battle(seed=1)
  for c in b.cogs:c.lure=3
  stock=deepcopy(b.toons[0].stock);round_number=b.round
  for name,g in GAGS.items():
   if g.track=='Trap':
    with self.assertRaisesRegex(ValueError,'already lured'):b.plan(Action(0,name,None if g.group else 0))
  self.assertEqual(stock,b.toons[0].stock);self.assertEqual(round_number,b.round);self.assertFalse(b.plans)
 def test_single_trap_targets_exclude_lured(self):
  b=Battle(seed=1);b.cogs[0].lure=3
  self.assertNotIn(0,[i for i,_ in b.targets(0,'TNT')]);b.validate(Action(0,'TNT',1))
 def test_mixed_railroad_only_places_on_unlured(self):
  b=Battle(seed=1);b.cogs[0].lure=3
  for i in range(4):b.plan(Action(i,'Railroad') if i==0 else Action(i))
  b.resolve();self.assertIsNone(b.cogs[0].trap);self.assertTrue(all(c.trap for c in b.cogs[1:]))
 def test_stale_plan_fails_atomically(self):
  b=Battle(seed=1)
  for i in range(4):b.plan(Action(i,'Railroad') if i==0 else Action(i))
  for c in b.cogs:c.lure=3
  stock=deepcopy(b.toons[0].stock)
  with self.assertRaises(ValueError):b.resolve()
  self.assertEqual(stock,b.toons[0].stock);self.assertEqual(b.round,1)
 def test_trap_and_lure_same_round_remains_legal(self):
  b=Battle(seed=1);b.roll=lambda chance:True
  for i in range(4):b.plan(Action(0,'Banana Peel',0) if i==0 else Action(1,'Hypno-goggles') if i==1 else Action(i))
  b.resolve();self.assertIsNone(b.cogs[0].trap);self.assertLess(b.cogs[0].hp,b.cogs[0].maximum)
 def test_sos_trap_cannot_bypass_all_lured(self):
  b=Battle(seed=1)
  for c in b.cogs:c.lure=2
  with self.assertRaisesRegex(ValueError,'lured'):b.validate(Action(0,'SOS: Clerk Clara'))

class AutoPartners(unittest.TestCase):
 def test_choices_legal_and_conserve_rare_supplies(self):
  for seed in range(30):
   b=Battle(seed=seed)
   for c in b.cogs:c.lure=2 if seed%2 else 0
   b.toons[0].hp=20
   original=deepcopy(b.toons);engine_rng=b.rng.getstate()
   for i in range(1,4):
    a=choose_action(b,i,random.Random(seed));b.validate(a)
    self.assertTrue(a.gag=='Pass' or a.gag in GAGS and GAGS[a.gag].level<7)
   self.assertEqual(original,b.toons);self.assertEqual(engine_rng,b.rng.getstate())
 def test_no_regular_stock_passes(self):
  b=Battle(seed=1)
  for n,g in GAGS.items():
   if g.level<7:b.toons[1].stock[n]=0
  self.assertEqual(choose_action(b,1,random.Random(1)).gag,'Pass')
 def test_does_not_peek_at_pending_actions(self):
  b=Battle(seed=1);a=choose_action(b,1,random.Random(4))
  b.plan(Action(0,'Hypno-goggles'))
  self.assertEqual(a,choose_action(b,1,random.Random(4)))

class HealthEvents(unittest.TestCase):
 def test_healing_and_damage_are_separate_events(self):
  b=Battle(seed=1);b.cogs=b.cogs[:1];b.toons[1].hp=30
  b.roll=lambda chance:True;b.rng.choice=lambda choices:choices[1]
  for i in range(4):b.plan(Action(0,'Feather',1) if i==0 else Action(i))
  b.resolve();changes=[amount for kind,index,amount in b.health_events if kind=='toon' and index==1]
  self.assertTrue(any(n>0 for n in changes));self.assertTrue(any(n<0 for n in changes))
  self.assertEqual(sum(changes),b.toons[1].hp-30)
 def test_unite_records_actual_healing(self):
  from support import use_unite
  b=Battle(seed=1);b.toons[0].hp=95
  use_unite(b,0,'Unite: Toon-Up 20')
  self.assertEqual(b.health_events,[('toon',0,5)])
