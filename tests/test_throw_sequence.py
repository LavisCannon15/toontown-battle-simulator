import unittest
from unittest.mock import patch
from types import SimpleNamespace
from direct.interval.IntervalGlobal import Wait
from battle_engine import Action
from throw_sequence import schedule,movie

class ThrowTiming(unittest.TestCase):
 def event(self,actions,targets):
  return dict(track='Throw',actions=actions,targets=targets,health=[],misses=[])
 def test_same_target_stagger(self):
  actions=[Action(i,'Cupcake',0) for i in range(4)]
  ordered,wide=schedule(self.event(actions,{i:[0] for i in range(4)}))
  self.assertEqual([t for a,t in ordered],[0,.5,1,1.5]);self.assertFalse(wide)
 def test_target_groups_and_stable_order(self):
  actions=[Action(0,'Cupcake',0),Action(1,'Birthday Cake',1),Action(2,'Whole Cream Pie',0)]
  ordered,_=schedule(self.event(actions,{0:[0],1:[1],2:[0]}))
  self.assertEqual([(a.toon,t) for a,t in ordered],[(1,0),(0,1),(2,1.5)])
 def test_group_phase_and_health_once(self):
  actions=[Action(0,'Cupcake',0),Action(1,'Wedding Cake'),Action(2,'Wedding Cake')]
  event=self.event(actions,{0:[0],1:[0,1],2:[0,1]});event['health']=[('cog',0,-100),('cog',1,-120)]
  calls=[]
  app=SimpleNamespace(health_movie=lambda e,t:(calls.append((e,t)) or Wait(t)))
  with patch('audited_gags.throw',return_value=(Wait(4.2),3)):
   result=movie(app,event)
  self.assertAlmostEqual(result.getDuration(),8.4)
  self.assertEqual([h for e,t in calls for h in e['health']],event['health'])
  self.assertTrue(all(abs(t-7.2)<.001 for e,t in calls))
 def test_miss_dodge_tracks_target_start(self):
  event=self.event([Action(0,'Cupcake',0),Action(1,'Cupcake',1)],{0:[0],1:[1]});event['misses']=[1]
  calls=[];app=SimpleNamespace(health_movie=lambda e,t:(calls.append((e,t)) or Wait(t)))
  with patch('audited_gags.throw',return_value=(Wait(4.2),3)):movie(app,event)
  self.assertEqual(calls[0][0]['dodge_at'],3.45);self.assertEqual(calls[0][1],4)
