"""Behavioral regression tests with fixed outcomes and complete battle runs."""
import random
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from battle_engine import Action, Battle, GAGS, cog_health


class Rules(unittest.TestCase):
    def battle(self, difficulty='Hard'):
        b=Battle(difficulty,seed=7)
        b.roll=lambda chance: chance>0
        b.cog_phase=lambda:None
        return b

    def resolve(self,b,*actions):
        for i in range(4):
            if b.toons[i].alive:
                b.plan(next((a for a in actions if a.toon==i),Action(i)))
        b.resolve()

    def test_level_12_health_is_196(self):
        self.assertEqual([cog_health(i) for i in (1,8,10,11,12)],[6,90,132,156,196])

    def test_planning_is_free_and_replaceable(self):
        b=self.battle(); before=b.toons[0].stock.copy()
        b.plan(Action(0,'Birthday Cake',0)); b.plan(Action(0,'Cupcake',1))
        self.assertEqual(b.toons[0].stock,before)
        self.assertEqual(b.cogs[0].hp,196)
        self.assertEqual(b.plans[0].gag,'Cupcake')

    def test_incomplete_round_is_rejected(self):
        b=self.battle(); b.plan(Action(0,'Birthday Cake',0))
        with self.assertRaises(ValueError): b.resolve()
        self.assertEqual(b.toons[0].stock['Birthday Cake'],3)

    def test_trap_then_lure_even_when_toon_order_is_reversed(self):
        b=self.battle()
        self.resolve(b,Action(0,'$10 Bill',0),Action(3,'TNT',0))
        self.assertEqual(b.cogs[0].hp,16)
        self.assertEqual(b.cogs[0].lure,0)
        self.assertIsNone(b.cogs[0].trap)

    def test_trap_persists_when_lure_misses(self):
        b=self.battle(); b.roll=lambda chance:False
        self.resolve(b,Action(0,'TNT',0),Action(1,'$10 Bill',0))
        self.assertEqual(b.cogs[0].hp,196)
        self.assertEqual(b.cogs[0].trap,('TNT',180))

    def test_multiple_traps_cancel(self):
        b=self.battle()
        self.resolve(b,Action(0,'TNT',0),Action(1,'Banana Peel',0),Action(2,'$10 Bill',0))
        self.assertEqual(b.cogs[0].hp,196)
        self.assertIsNone(b.cogs[0].trap)
        self.assertEqual(b.cogs[0].lure,4)

    def test_trap_cannot_be_placed_on_lured_cog(self):
        b=self.battle(); b.cogs[0].lure=4
        with self.assertRaises(ValueError): b.plan(Action(0,'TNT',0))

    def test_lure_and_combo_are_additive(self):
        b=self.battle()
        self.resolve(b,Action(0,'$10 Bill',0),Action(1,'Whole Cream Pie',0),Action(2,'Whole Cream Pie',0))
        self.assertEqual(b.cogs[0].hp,60)  # 196 - (80 + 16 + 40)

    def test_combo_rounds_up(self):
        b=self.battle()
        self.resolve(b,Action(0,'Cupcake',0),Action(1,'Cupcake',0))
        self.assertEqual(b.cogs[0].hp,181)  # 12 + ceil(2.4)

    def test_one_fog_three_trunks_hits_all_for_136(self):
        b=self.battle()
        self.resolve(b,Action(0,'Foghorn'),*(Action(i,'Elephant Trunk') for i in (1,2,3)))
        self.assertEqual([c.hp for c in b.cogs],[60]*4)

    def test_three_fog_one_trunk_defeats_level12(self):
        b=self.battle()
        self.resolve(b,Action(0,'Elephant Trunk'),*(Action(i,'Foghorn') for i in (1,2,3)))
        self.assertEqual([c.hp for c in b.cogs],[0]*4)
        self.assertIn('Victory',b.result)

    def test_sound_wakes_before_throw(self):
        b=self.battle(); b.cogs[0].lure=4
        self.resolve(b,Action(0,'Birthday Cake',0),Action(1,'Bike Horn'))
        self.assertEqual(b.cogs[0].hp,92)  # 4 + 100, no lure bonus

    def test_drop_misses_lured_but_hits_after_sound(self):
        b=self.battle(); b.cogs[0].lure=4
        self.resolve(b,Action(0,'Grand Piano',0))
        self.assertEqual(b.cogs[0].hp,196)
        self.resolve(b,Action(0,'Grand Piano',0),Action(1,'Bike Horn'))
        self.assertEqual(b.cogs[0].hp,22)

    def test_lured_throw_guaranteed(self):
        b=self.battle(); b.cogs[0].lure=4
        self.assertEqual(b.accuracy([Action(0,'Birthday Cake',0)],[0]),100)

    def test_maxed_accuracy_accounts_for_defense_and_stun(self):
        b=self.battle(); a=Action(0,'Grand Piano',0)
        self.assertEqual(b.accuracy([a],[0]),55)
        b.hits=[('Squirt',{0},False,25)]
        self.assertEqual(b.accuracy([a],[0]),80)
        b.hits=[('Trap',{0},False,50)]
        self.assertEqual(b.accuracy([a],[0]),95)

    def test_passive_trap_accuracy_and_double_lure(self):
        b=self.battle(); a=Action(0,'Hypno-goggles')
        self.assertEqual(b.accuracy([a],[0,1,2,3]),80)
        b.cogs[0].trap=('TNT',180)
        self.assertEqual(b.accuracy([a],[0,1,2,3]),90)
        b.cogs[1].trap=('TNT',180)
        self.assertEqual(b.accuracy([a],[0,1,2,3]),95)
        b.cogs[0].trap=b.cogs[1].trap=None
        self.assertEqual(b.accuracy([a,Action(1,'Hypno-goggles')],[0,1,2,3]),95)

    def test_group_sound_has_one_shared_roll(self):
        b=self.battle(); calls=[]
        b.roll=lambda chance: calls.append(chance) or False
        self.resolve(b,Action(0,'Foghorn'),Action(1,'Foghorn'))
        self.assertEqual(len(calls),1)
        self.assertEqual([c.hp for c in b.cogs],[196]*4)

    def test_toon_up_cannot_heal_self(self):
        b=self.battle()
        with self.assertRaises(ValueError): b.plan(Action(0,'Pixie Dust',0))

    def test_group_toon_up_excludes_caster(self):
        b=self.battle()
        for t in b.toons:t.hp=10
        self.resolve(b,Action(0,'Juggling Cubes'))
        self.assertEqual([t.hp for t in b.toons],[10,45,45,45])

    def test_weak_heal_and_health_cap(self):
        b=self.battle(); b.roll=lambda chance:False; b.toons[1].hp=50
        self.resolve(b,Action(0,'Pixie Dust',1))
        self.assertEqual(b.toons[1].hp,62)
        b.roll=lambda chance:True
        self.resolve(b,Action(0,'Pixie Dust',1))
        self.assertEqual(b.toons[1].hp,100)

    def test_organic_rounding(self):
        b=self.battle(); b.toons[0].organic='Drop'
        self.assertEqual(b.power(Action(0,'Grand Piano',0)),196)
        b.toons[0].organic='Squirt'
        self.assertEqual(b.power(Action(0,'Storm Cloud',0)),92)
        b.toons[0].organic='Toon-Up'
        self.assertEqual(b.power(Action(0,'Juggling Cubes')),126)

    def test_lure_duration_and_no_refresh(self):
        b=Battle('Hard',seed=9); b.roll=lambda chance:True
        self.resolve(b,Action(0,'Hypno-goggles'))
        self.assertEqual([c.lure for c in b.cogs],[3]*4)
        before=(b.round,b.toons[0].stock.copy(),[c.lure for c in b.cogs])
        with self.assertRaises(ValueError):self.resolve(b,Action(0,'Hypno-goggles'))
        self.assertEqual((b.round,b.toons[0].stock,[c.lure for c in b.cogs]),before)
        self.resolve(b)
        self.assertEqual([c.lure for c in b.cogs],[2]*4)
        self.resolve(b); self.resolve(b)
        self.assertEqual([t.hp for t in b.toons],[100]*4)
        self.resolve(b)
        self.assertTrue(any(t.hp<100 for t in b.toons))

    def test_empty_stock_rejected_without_mutation(self):
        b=self.battle(); b.toons[0].stock['Foghorn']=0
        with self.assertRaises(ValueError): b.plan(Action(0,'Foghorn'))
        self.assertFalse(b.plans)

    def test_sad_toons_cannot_act_or_be_healed(self):
        b=self.battle(); b.toons[0].hp=0
        with self.assertRaises(ValueError): b.plan(Action(0))
        with self.assertRaises(ValueError): b.plan(Action(1,'Pixie Dust',0))
        self.resolve(b)
        self.assertEqual(b.round,2)

    def test_same_seed_replays_identically(self):
        a,b=Battle(seed=42),Battle(seed=42)
        for game in (a,b):
            self.resolve(game,*(Action(i,'Whole Cream Pie',i) for i in range(4)))
        self.assertEqual(a.log,b.log)

    def test_300_complete_battles_and_invariants(self):
        outcomes=set()
        for difficulty in ('Easy','Normal','Hard'):
            for seed in range(100):
                b=Battle(difficulty,seed)
                for turn in range(150):
                    if b.result:break
                    live=[j for j,c in enumerate(b.cogs) if c.alive]
                    for i,t in enumerate(b.toons):
                        if not t.alive:continue
                        # Include intentionally passive teams to exercise losses.
                        name=next((n for n in ('Foghorn','Birthday Cake','Storm Cloud','Grand Piano') if t.stock[n]),'Pass') if seed%2 else 'Pass'
                        target=None if name=='Pass' or GAGS[name].group else live[i%len(live)]
                        b.plan(Action(i,name,target))
                    b.resolve()
                    self.assertTrue(all(0<=x.hp<=x.maximum for x in [*b.cogs,*b.toons]))
                    self.assertTrue(all(n>=0 for t in b.toons for n in t.stock.values()))
                self.assertIsNotNone(b.result,(difficulty,seed))
                outcomes.add(b.result.split('!')[0])
        self.assertEqual(len(outcomes),2)


if __name__=='__main__':unittest.main(verbosity=2)
