import unittest
from battle_engine import Battle,Action,GAGS,carry_limit
from support import UNITES,use_unite

class UniteAudit(unittest.TestCase):
 def test_all_heals_are_per_recipient_capped_and_no_revival(self):
  for name,(kind,value) in UNITES.items():
   if not name.startswith('Unite: Toon-Up'):continue
   b=Battle();b.toons[0].hp=1;b.toons[1].hp=b.toons[1].maximum-1;b.toons[2].hp=0;b.toons[3].escaped=True
   before=b.toons[0].rewards[name];b.plan(Action(0,'Cupcake',0));plans=b.plans.copy()
   self.assertEqual(use_unite(b,0,name),[0,1]);self.assertEqual(b.toons[0].hp,1+value)
   self.assertEqual(b.toons[1].hp,b.toons[1].maximum);self.assertEqual(b.toons[2].hp,0)
   self.assertEqual(b.plans,plans);self.assertEqual(b.round,1);self.assertEqual(b.toons[0].rewards[name],before-1)
 def test_all_restock_types_caps_and_unavailable_track(self):
  for name,(track,count) in UNITES.items():
   if not name.startswith('Unite: Gag-Up'):continue
   b=Battle()
   for t in b.toons:t.stock={g:0 for g in GAGS}
   t=b.toons[0];use_unite(b,0,name)
   expected=0 if track==t.missing_track else count
   self.assertEqual(t.carried,expected,name)
   self.assertTrue(all(n==0 or (GAGS[g].level<7 and GAGS[g].track!=t.missing_track and track in ('All',GAGS[g].track) and n<=carry_limit(GAGS[g])) for g,n in t.stock.items()))
 def test_shared_lock_stock_validation_and_other_caster(self):
  b=Battle();use_unite(b,0,'Unite: Toon-Up 20');stock=b.toons[0].rewards.copy()
  with self.assertRaises(ValueError):use_unite(b,0,'Unite: Gag-Up All')
  self.assertEqual(stock,b.toons[0].rewards)
  use_unite(b,1,'Unite: Gag-Up All');self.assertEqual(b.toons[1].unite_cooldown,3)
  b.toons[2].rewards['Unite: Toon-Up 20']=0
  with self.assertRaises(ValueError):use_unite(b,2,'Unite: Toon-Up 20')
  self.assertEqual(b.toons[2].unite_cooldown,0)
if __name__=='__main__':unittest.main()
