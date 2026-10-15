import unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from battle_engine import *
from support import *

class Expansion(unittest.TestCase):
 def game(self):
  b=Battle('Hard',seed=6);b.cog_phase=lambda:None;b.roll=lambda chance:chance>0
  return b
 def turn(self,b,*chosen):
  for i in range(4):b.plan(next((a for a in chosen if a.toon==i),Action(i)))
  b.resolve()
 def test_all_32_catalogs_have_rank_tables(self):
  self.assertEqual(len(COG_CATALOG),32)
  for name,data in COG_CATALOG.items():
   for lv in range(data['rank'],data['rank']+5):
    b=Battle(seed=1);b.cogs=[Cog(name,lv)];b.cog_phase()
    self.assertTrue(all(0<=t.hp<=100 for t in b.toons))
   self.assertTrue(all(len(a['damage'])==5 for a in data['attacks']))
 def test_new_ttr_group_attacks(self):
  for name,attack in [('Micromanager','Close the Loop'),('Corporate Raider','Hostile Takeover'),('Money Bags','Money Talks')]:
   self.assertTrue(next(a for a in COG_CATALOG[name]['attacks'] if a['name']==attack)['group'])
 def test_real_carry_limits(self):
  self.assertEqual(carry_limit(GAGS['TNT']),3);self.assertEqual(carry_limit(GAGS['Foghorn']),2)
  self.assertEqual(carry_limit(GAGS['Elephant Trunk']),5)
  t=Toon('Tester');t.stock['TNT']=4
  with self.assertRaises(ValueError):t.check_inventory(t.stock)
 def test_pouch_overflow_and_separate_sevens(self):
  t=Toon('Tester');t.pouch=20
  with self.assertRaises(ValueError):t.check_inventory(t.stock)
  t.stock={n:0 for n in GAGS};t.stock['Cupcake']=20;t.stock['Wedding Cake']=1;t.check_inventory(t.stock)
  self.assertEqual(t.carried,20)
 def test_extra_seven_only_one_chosen_track(self):
  t=Toon('Tester');t.extra_seven='Throw';t.stock['Wedding Cake']=2;t.check_inventory(t.stock)
  t.stock['Geyser']=2
  with self.assertRaises(ValueError):t.check_inventory(t.stock)
 def test_missing_track_not_usable(self):
  b=self.game();b.toons[0].missing_track='Trap'
  with self.assertRaises(ValueError):b.plan(Action(0,'TNT',0))
 def test_all_seven_level_sevens_group(self):
  self.assertEqual(len(GAGS),49);self.assertTrue(all(g.group for g in GAGS.values() if g.level==7))
 def test_railroad_places_all_and_lure_activates(self):
  b=self.game();self.turn(b,Action(0,'Railroad'),Action(1,'Presentation'))
  self.assertTrue(all(not c.alive for c in b.cogs));self.assertEqual(b.toons[0].stock['Railroad'],0)
 def test_level_seven_combo_only_on_shared_target(self):
  b=self.game();self.turn(b,Action(0,'Wedding Cake'),Action(1,'Cupcake',0))
  self.assertEqual(b.cogs[0].hp,44);self.assertEqual(b.cogs[1].hp,76)
 def test_group_attack_stun_not_multiplied_by_cogs(self):
  b=self.game();self.turn(b,Action(0,'Bike Horn'))
  self.assertEqual(sum(h[3] for h in b.hits),25)
 def test_high_dive_heals_other_toons(self):
  b=self.game()
  for t in b.toons:t.hp=10
  self.turn(b,Action(0,'High Dive'));self.assertEqual([t.hp for t in b.toons],[10,80,80,80])
 def test_fire_consumed_once(self):
  b=self.game();self.turn(b,Action(0,'Fire',0))
  self.assertFalse(b.cogs[0].alive);self.assertEqual(b.toons[0].rewards['Fire'],1)
 def test_invalid_reward_does_not_spend_gag(self):
  b=self.game();b.plan(Action(0,'Fire',0));b.toons[0].rewards['Fire']=0
  for i in range(1,4):b.plan(Action(i,'Cupcake',1))
  with self.assertRaises(ValueError):b.resolve()
  self.assertEqual(b.toons[1].stock['Cupcake'],1)
 def test_duplicate_remote_rejected_atomically(self):
  b=self.game()
  with self.assertRaises(ValueError):self.turn(b,Action(0,'Damage remote 1★',0),Action(1,'Healing remote 1★',0))
  self.assertEqual(b.toons[0].rewards['Damage remote 1★'],2)
 def test_remote_damage_and_expiration(self):
  b=self.game();self.turn(b,Action(0,'Damage remote 1★',0));remote_tick(b,0)
  self.assertEqual([c.hp for c in b.cogs],[196,151,151,151]);remote_tick(b,0)
  self.assertEqual([c.hp for c in b.cogs],[151,106,106,106]);self.assertIsNone(b.cogs[0].remote)
 def test_healing_remote_heals_including_caster(self):
  b=self.game()
  for t in b.toons:t.hp=10
  self.turn(b,Action(0,'Healing remote 3★',0));remote_tick(b,0)
  self.assertEqual([t.hp for t in b.toons],[35]*4)
 def test_remote_replaces_cog_attack(self):
  b=Battle(seed=1);b.cogs=[Cog('Mr. Hollywood',12)];b.cogs[0].remote=REMOTES['Healing remote 1★'];b.cog_phase()
  self.assertEqual([t.hp for t in b.toons],[100]*4)
 def test_sos_healing_includes_caster(self):
  b=self.game()
  for t in b.toons:t.hp=10
  self.turn(b,Action(0,'SOS: Flippy'));self.assertEqual([t.hp for t in b.toons],[55]*4)
 def test_sos_drop_misses_lured(self):
  b=self.game();b.cogs[0].lure=4;self.turn(b,Action(0,'SOS: Barnacle Bessie'))
  self.assertEqual(b.cogs[0].hp,196);self.assertEqual(b.cogs[1].hp,26)
 def test_sos_lure_activates_trap(self):
  b=self.game();self.turn(b,Action(0,'TNT',0),Action(1,'SOS: Lil Oldman'))
  self.assertEqual(b.cogs[0].hp,16);self.assertEqual(b.cogs[1].lure,6)
 def test_sos_duration(self):
  b=self.game();self.turn(b,Action(0,'SOS: Soggy Bottom'));self.assertEqual(b.hit_rounds,2)
  self.turn(b);self.turn(b);self.assertEqual(b.hit_rounds,0)
 def test_unite_does_not_spend_turn_and_cooldown(self):
  b=self.game();b.toons[0].hp=10;b.plan(Action(0,'Cupcake',0));use_unite(b,0,'Unite: Toon-Up 80')
  self.assertEqual(b.toons[0].hp,90);self.assertIn(0,b.plans)
  with self.assertRaises(ValueError):use_unite(b,0,'Unite: Gag-Up All')
  for _ in range(3):self.turn(b)
  self.assertEqual(b.toons[0].unite_cooldown,0)
 def test_restock_respects_pouch_tracks_and_sevens(self):
  b=self.game();t=b.toons[0];t.stock={n:0 for n in GAGS};t.missing_track='Drop';t.pouch=20
  restock(b,'All',45);self.assertEqual(t.carried,20);t.check_inventory(t.stock)
  self.assertEqual(t.stock['Wedding Cake'],0);self.assertEqual(t.stock['Grand Piano'],0)
 def test_doodle_success_and_failure(self):
  b=self.game()
  for t in b.toons:t.hp=10
  b.rng.random=lambda:0.0
  self.turn(b,Action(0,'Doodle: Speak'));self.assertEqual([t.hp for t in b.toons],[32]*4)
  b.rng.random=lambda:.999;self.turn(b,Action(0,'Doodle: Speak'));self.assertEqual([t.hp for t in b.toons],[32]*4)
 def test_sound_reenables_lure_next_round(self):
  b=self.game();self.turn(b,Action(0,'Hypno-goggles'))
  self.assertFalse(b.lure_available)
  for i in range(4):
   with self.assertRaises(ValueError):b.plan(Action(i,'Hypno-goggles'))
   with self.assertRaises(ValueError):b.plan(Action(i,'SOS: Lil Oldman'))
  self.turn(b,Action(0,'Bike Horn'))
  self.assertTrue(b.lure_available);self.assertTrue(all(c.lure==0 for c in b.cogs))
  b.plan(Action(0,'Hypno-goggles'))
 def test_single_lure_excludes_lured_targets(self):
  b=self.game();b.cogs[0].lure=3
  self.assertNotIn(0,[i for i,c in b.targets(0,'$10 Bill')])
  with self.assertRaises(ValueError):b.plan(Action(0,'$10 Bill',0))
  b.plan(Action(0,'Hypno-goggles'))
 def test_dead_cogs_do_not_enable_lure(self):
  b=self.game();b.cogs[0].hp=0
  for c in b.cogs[1:]:c.lure=3
  self.assertFalse(b.lure_available)
 def test_stale_lure_plan_rejected_without_round_changes(self):
  b=self.game()
  for i in range(4):b.plan(Action(i,'Hypno-goggles'))
  for c in b.cogs:c.lure=3
  before=(b.round,[t.stock.copy() for t in b.toons],b.log.copy())
  with self.assertRaises(ValueError):b.resolve()
  self.assertEqual((b.round,[t.stock for t in b.toons],b.log),before)
 def test_every_reward_can_resolve(self):
  for name in (*SOS,*REMOTES,*DOODLES,'Fire'):
   b=self.game();self.turn(b,Action(0,name,0 if name in REMOTES or name=='Fire' else None))
   self.assertTrue(all(0<=c.hp<=c.maximum for c in b.cogs),name)

if __name__=='__main__':unittest.main()
