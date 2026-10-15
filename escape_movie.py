"""Run escape using Toon.getTeleportOutTrack's portal and audio sequence."""
from direct.interval.IntervalGlobal import Sequence,Func
from sos_movies import teleport

def movie(app,index):
 guest={'actors':app.toon_actors[index],'props':[]}
 clip=teleport(app,guest)
 # Register the portal for cancellation/New battle as well as normal cleanup.
 portals=guest['props']
 for portal in portals:app.movie_props.append((portal,portal))
 def cleanup():
  for portal in portals:
   if not portal.isEmpty():portal.cleanup();portal.removeNode()
  app.movie_props[:]=[(node,actor) for node,actor in app.movie_props if all(node is not p for p in portals)]
 return Sequence(clip,Func(app.toon_nodes[index].hide),Func(cleanup))
