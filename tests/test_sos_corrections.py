import unittest
from battle_engine import Battle,Action,GAGS,Toon,Cog
from support import resolve_support,restock,SOS,SOS_STARS
class SOSCorrections(unittest.TestCase):
 def test_traps_skip_occupied_and_lured(self):
  b=Battle();b.cogs[0].trap=('TNT',180);b.cogs[1].lure=3
  resolve_support(b,Action(0,'SOS: Clerk Clara'),track='Trap')
  self.assertEqual(b.cogs[0].trap,('TNT',180));self.assertIsNone(b.cogs[1].trap);self.assertEqual(b.cogs[2].trap,('SOS: Clerk Clara',180))
 def test_restock_respects_unlocks(self):
  b=Battle();t=b.toons[0];t.track_levels['Throw']=1;t.stock={n:0 for n in GAGS}
  restock(b,'Throw',12)
  self.assertTrue(all(not q or GAGS[n].level==1 for n,q in t.stock.items()))
 def test_single_sos_single_stun(self):
  b=Battle();a=Action(0,'Whole Cream Pie',0);old=b.accuracy([a],[0],capped=False)
  resolve_support(b,Action(1,'SOS: Barbara Seville'),track='Sound')
  self.assertEqual(b.accuracy([a],[0],capped=False)-old,25)
 def test_status_recipients_and_toonup(self):
  b=Battle();a=Action(0,'Feather',1);old=b.accuracy([a],[1],capped=False)
  resolve_support(b,Action(0,'SOS: Sticky Lou'),early=True)
  self.assertEqual(b.accuracy([a],[1],capped=False)-old,75)
  b.toons[0]=Battle().toons[0]
  self.assertEqual(b.accuracy([a],[1],capped=False),old)
  resolve_support(b,Action(0,'SOS: Julius Wheezer'),early=True)
  self.assertGreater(b.cogs[0].accuracy_down,0)
  b.cogs[0]=Battle().cogs[0];self.assertEqual(b.cogs[0].accuracy_down,0)
 def test_all_stars(self):
  self.assertEqual(set(SOS),set(SOS_STARS));self.assertEqual(SOS_STARS['SOS: Professor Pete'],5)
