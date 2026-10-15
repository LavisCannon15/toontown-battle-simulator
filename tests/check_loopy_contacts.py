"""Loopy's health changes follow each bundled Geyser launch, not a shared time."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from panda3d.core import loadPrcFileData
loadPrcFileData('','audio-library-name null')
from direct.interval.IntervalGlobal import Wait
from panda_battle import PandaBattle
from battle_engine import Action
from sos_movies import arrival,wrap_track
app=PandaBattle(offscreen=True,timed=False,seed=1)
try:
 class Delays:
  def __init__(self):self.values=iter((0,.2,.5,.9))
  def random(self):return next(self.values)
 app.presentation_rng=Delays()
 app.display_toon_hp=[100]*4;app.display_cog_hp=[196]*4
 for cog in app.game.cogs:cog.hp=cog.maximum=196
 arrive=arrival(app,Action(0,'SOS: Loopy Loopenloop'));arrive.start();arrive.finish()
 own=dict(kind='gags',track='Squirt',actions=[],health=[('cog',i,-115) for i in range(4)],misses=[],lure_before=[0]*4,trap_before=[None]*4)
 event=dict(own,support_events={0:own},regular_health=[])
 clip=wrap_track(app,event,Wait(0));clip.start();clip.pause()
 for step in range(1,301):clip.setT(step/100)
 assert app.display_cog_hp==[81,196,196,196],app.display_cog_hp
 for step in range(301,351):clip.setT(step/100)
 assert app.display_cog_hp==[81,81,81,196],app.display_cog_hp
 clip.finish();assert app.display_cog_hp==[81]*4
 app.clear_movie_props();assert not app.sos_guests
 print('Loopy applies each Cog damage at its Geyser eruption; no early group damage or duplicate HP.',flush=True)
finally:app.destroy()
