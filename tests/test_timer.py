import unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from round_timer import RoundTimer
class TimerTests(unittest.TestCase):
 def setUp(self):
  self.now=10.;self.timer=RoundTimer(clock=lambda:self.now)
 def test_thirty_second_deadline(self):
  self.assertEqual(self.timer.remaining,30);self.now+=29.5;self.assertEqual(self.timer.remaining,1)
  self.now+=.5;self.assertEqual(self.timer.remaining,0)
 def test_pause_preserves_remaining_time(self):
  self.now+=10;self.timer.pause();self.now+=100;self.assertEqual(self.timer.remaining,20)
  self.timer.resume();self.now+=5;self.assertEqual(self.timer.remaining,15)
 def test_restart_while_paused(self):
  self.now+=29;self.timer.pause();self.timer.reset();self.now+=90;self.timer.resume();self.assertEqual(self.timer.remaining,30)
 def test_reset_uses_new_deadline(self):
  self.now+=20;self.timer.reset();self.assertEqual(self.timer.remaining,30)
