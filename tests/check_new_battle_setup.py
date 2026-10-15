import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from panda3d.core import loadPrcFileData
loadPrcFileData('','audio-library-name null')
from panda_battle import PandaBattle
app=PandaBattle(offscreen=True,timed=False,seed=1)
try:
 app.open_setup();app.flush_setup();app.setup_entries=[]
 app.setup_draft['toon_count']=2;app.setup_draft['cog_count']=2
 app.setup_draft['cogs'][:2]=[('Flunky',3),('Pencil Pusher',4)]
 app.setup_draft['version2'][:2]=[True,False]
 app.setup_draft['skelecogs'][:2]=[False,True]
 app.setup_draft['toons'][0].name='Custom Toon';app.setup_draft['toons'][0].hp=70
 app.apply_setup();assert app.modal is None
 stock=dict(app.game.toons[0].stock);rewards=dict(app.game.toons[0].rewards)
 app.game.toons[0].hp=0;app.game.toons[1].escaped=True
 app.game.toons[0].stock['Whole Cream Pie']=0
 app.game.toons[0].rewards['Fire']=0
 app.game.cogs[0].skelecog=True;app.game.cogs[0].hp=0
 app.new_battle()
 assert len(app.game.toons)==2 and len(app.game.cogs)==2
 assert [(c.name,c.level,c.version2,c.skelecog) for c in app.game.cogs]==[('Flunky',3,True,False),('Pencil Pusher',4,False,True)]
 assert all(c.hp==c.maximum and not c.lure and not c.trap and not c.remote for c in app.game.cogs)
 assert app.game.toons[0].name=='Custom Toon' and app.game.toons[0].hp==70
 assert not app.game.toons[1].escaped
 assert app.game.toons[0].stock==stock and app.game.toons[0].rewards==rewards
 app.open_setup();app.setup_draft['cogs'][0]=('Mr. Hollywood',8);app.close_modal()
 app.new_battle();assert app.game.cogs[0].name=='Flunky'
 print('New battle restores applied lineup, forms, team sizes and starting inventory/Laff; canceled setup is ignored.')
finally:app.destroy()
