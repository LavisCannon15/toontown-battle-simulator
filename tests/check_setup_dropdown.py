"""Exercise the dropdown's actual selection handler, not setup callbacks alone."""
import sys,traceback
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from panda3d.core import loadPrcFileData
loadPrcFileData('','audio-library-name null')
from panda_battle import PandaBattle
app=PandaBattle(offscreen=True,timed=False,seed=1)
menus=[];original=app.menu

def record(*args,**kwargs):
 menu=original(*args,**kwargs);menus.append(menu);return menu
app.menu=record

def select(items_contains,value):
 menu=next(m for m in menus if not m.isEmpty() and items_contains in m['items'])
 menu.popupMenu.show();menu.cancelFrame.show();menu.highlightedIndex=menu['items'].index(value)
 menu.selectHighlightedIndex()

try:
 app.open_setup()
 select('Mr. Hollywood','Cold Caller')
 assert app.setup_draft['cogs'][0][0]=='Cold Caller'
 select('Sellbot','Bossbot')
 assert app.setup_draft['cogs'][0][0]=='Flunky'
 select('Micromanager','Micromanager')
 assert app.setup_draft['cogs'][0][0]=='Micromanager'
 # Count menus share options; explicitly target each freshly rebuilt row.
 for field,offset in [('toon_count',0),('cog_count',1)]:
  choices=[m for m in menus if not m.isEmpty() and m['items']==['1','2','3','4']]
  menu=choices[offset];menu.popupMenu.show();menu.cancelFrame.show();menu.highlightedIndex=1;menu.selectHighlightedIndex()
  assert app.setup_draft[field]==2
 select('Skelecog','Skelecog')
 app.apply_setup();assert len(app.game.toons)==len(app.game.cogs)==2
 assert app.game.cogs[0].name=='Micromanager'
 app.open_setup();select('Micromanager','Yesman');app.close_modal()
 assert app.game.cogs[0].name=='Micromanager'
 for _ in range(3):app.taskMgr.step()
 Path('work/setup-dropdown-result.txt').write_text('PASS: real dropdown selection for Cog, department, Toon/Cog counts and form; apply, reopen, cancel and event loop.')
except Exception:
 Path('work/setup-dropdown-result.txt').write_text(traceback.format_exc());raise
finally:app.destroy()
