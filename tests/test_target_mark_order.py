import unittest
from types import SimpleNamespace
from battle_hud import BattleHUD
from battle_engine import Battle,Action
class TargetOrder(unittest.TestCase):
 def test_visible_formation_order(self):
  app=SimpleNamespace(game=Battle())
  for count in range(1,5):
   for i,c in enumerate(app.game.cogs):c.hp=c.maximum if i<count else 0
   for target in range(count):
    self.assertEqual(BattleHUD.target_marks(app,Action(0,'Cupcake',target)),''.join('X' if i==target else '-' for i in range(count)))
 def test_removed_middle_and_toon_targets(self):
  app=SimpleNamespace(game=Battle());app.game.cogs[1].hp=0
  self.assertEqual(BattleHUD.target_marks(app,Action(0,'Cupcake',2)),'-X-')
  self.assertEqual(BattleHUD.target_marks(app,Action(0,'Bike Horn')),'XXX')
  self.assertEqual(BattleHUD.target_marks(app,Action(0,'Feather',1)),'-X--')
  self.assertEqual(BattleHUD.target_marks(app,Action(0,'Megaphone')),'-XXX')
  self.assertEqual(BattleHUD.target_marks(app,Action(0,'Pass')),'')
if __name__=='__main__':unittest.main()
