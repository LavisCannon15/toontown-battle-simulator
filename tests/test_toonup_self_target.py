"""A player's own Toon-Up must exclude them for every gag and party size."""
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from battle_engine import Battle,Action,GAGS

class ToonUpRecipients(unittest.TestCase):
 def test_every_gag_excludes_its_user(self):
  for name,gag in GAGS.items():
   if gag.track!='Toon-Up':continue
   for count in (2,3,4):
    for caster in range(count):
     with self.subTest(gag=name,count=count,caster=caster):
      b=Battle(seed=1);b.toons=b.toons[:count];b.roll=lambda _:True
      for t in b.toons:t.hp=1;t.stock[name]=1;t.missing_track='None'
      target=next(i for i in range(count) if i!=caster)
      a=Action(caster,name,None if gag.group else target)
      self.assertNotIn(caster,b.victims(a))
      for i in range(count):b.plan(a if i==caster else Action(i))
      stream=b.resolve_events()
      for event in stream:
       if event and event.get('track')=='Toon-Up':
        self.assertEqual(b.toons[caster].hp,1)
        self.assertTrue(any(t.hp>1 for i,t in enumerate(b.toons) if i!=caster))
        self.assertFalse(any(k=='toon' and i==caster and n>0 for k,i,n in event['health']))
        break
      stream.close()
 def test_solo_and_single_target_self_choices_are_rejected(self):
  for name,gag in GAGS.items():
   if gag.track!='Toon-Up':continue
   b=Battle();b.toons[0].stock[name]=1;b.toons[0].missing_track='None'
   if not gag.group:
    with self.assertRaises(ValueError):b.validate(Action(0,name,0))
   b.toons=b.toons[:1]
   with self.assertRaises(ValueError):b.validate(Action(0,name,0))

if __name__=='__main__':unittest.main()
