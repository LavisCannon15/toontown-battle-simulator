"""Monotonic selection deadline; pause is a local sandbox convenience."""
from math import ceil
from time import monotonic

class RoundTimer:
    def __init__(self,seconds=30,clock=monotonic):
        self.seconds=seconds;self.clock=clock;self.paused=False;self.reset()
    def reset(self):
        self.saved=self.seconds;self.deadline=self.clock()+self.seconds
    @property
    def remaining(self):
        return max(0,ceil(self.saved if self.paused else self.deadline-self.clock()))
    def pause(self):
        if not self.paused:self.saved=max(0,self.deadline-self.clock());self.paused=True
    def resume(self):
        if self.paused:self.deadline=self.clock()+self.saved;self.paused=False
