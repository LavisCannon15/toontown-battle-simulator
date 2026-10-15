"""Resource eye/muzzle state, including ToonHead's 0.125-second blink."""
import random
from time import monotonic

def set_face(head,expression='neutral',closed=False,variant='short'):
 meshes=list(head.findAllMatches('**/+GeomNode'))
 # Dog Actor head channels already animate the muzzle; static species need
 # explicit muzzle selection. Only use a variant when the resource supplies it.
 def detail(name):
  return next((tier for tier in ('high','medium','low') if tier in name),'')
 available={(detail(n.getName().lower()),'muzzle'+expression in n.getName().lower()) for n in meshes}

 for node in meshes:
  name=node.getName().lower()
  if 'eyes' not in name and 'muzzle' not in name:continue
  if ('long' if variant=='short' else 'short') in name:node.hide();continue
  muzzle=expression if (detail(name),True) in available else 'neutral'
  key=('eyes'+expression+('closed' if closed else 'open')) if 'eyes' in name else 'muzzle'+muzzle
  node.show() if key in name else node.hide()

class Face:
 def __init__(self,head):
  self.head=head;self.expression='neutral';self.closed=False
  self.random=random.Random();self.next=monotonic()+self.random.uniform(1,5)
 def set(self,expression):
  self.expression=expression;self.closed=False;set_face(self.head,expression)
 def tick(self,now):
  if now<self.next:return
  self.closed=not self.closed;set_face(self.head,self.expression,self.closed)
  r=self.random.random()
  self.next=now+(.125 if self.closed else .2 if r<.1 else 1+4*r)
