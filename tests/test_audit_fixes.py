import unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from battle_engine import Battle,Action,Cog,GAGS
from support import use_unite
class AuditFixes(unittest.TestCase):
 def test_group_seven_gets_mixed_lure_bonus(self):
  b=Battle('Hard');a=Action(0,'Wedding Cake');self.assertEqual(b.accuracy([a],[0,1,2,3]),80)
  b.cogs[0].lure=2;self.assertEqual(b.accuracy([a],[0,1,2,3]),95)
  b.cogs[0].lure=0;b.cogs[0].remote=('Healing',2,45,15);self.assertEqual(b.accuracy([a],[0,1,2,3]),95)
 def test_v2_layers_stop_overflow_and_fire_removes_both(self):
  b=Battle('Hard');b.cogs=[Cog('The Big Cheese',12,version2=True)];b.damage(0,500,'test')
  self.assertTrue(b.cogs[0].skelecog);self.assertEqual(b.cogs[0].hp,196)
  b.damage(0,196,'test');self.assertFalse(b.cogs[0].alive)
  b.cogs=[Cog('The Big Cheese',12,version2=True)];b.damage(0,196,'Fire',bypass_layers=True);self.assertFalse(b.cogs[0].alive)
 def test_generator_can_receive_unite_between_cog_attacks(self):
  b=Battle('Hard');b.roll=lambda chance:True
  for t in b.toons:t.hp=60
  for i in range(4):b.plan(Action(i))
  gen=b.resolve_events()
  first=next(e for e in gen if e['kind']=='cog');hp=[t.hp for t in b.toons]
  use_unite(b,0,'Unite: Toon-Up 20');self.assertTrue(all(t.hp>=h for t,h in zip(b.toons,hp)))
  for e in gen:pass
  self.assertEqual(b.round,2)
 def test_unperformed_gag_not_consumed(self):
  b=Battle('Hard')
  for i in range(4):b.plan(Action(i,'Grand Piano',0) if i==0 else Action(i,'Fire',0) if i==1 else Action(i))
  stock=b.toons[0].stock['Grand Piano'];b.resolve();self.assertEqual(b.toons[0].stock['Grand Piano'],stock)
if __name__=='__main__':unittest.main()
