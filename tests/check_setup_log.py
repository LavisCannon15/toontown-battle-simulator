import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from panda3d.core import loadPrcFileData
loadPrcFileData('','audio-library-name null')
from panda_battle import PandaBattle
from battle_engine import Action
app=PandaBattle(offscreen=True,timed=False,seed=1)
out=Path('reports/setup-log');out.mkdir(exist_ok=True)
def shot(name):
 for _ in range(3):app.graphicsEngine.renderFrame()
 app.win.saveScreenshot(str((out/(name+'.png')).resolve()))
try:
 original=app.game;app.open_setup();assert app.timer.paused;shot('lineup')
 app.setup_count('toon_count',2);app.setup_count('cog_count',1)
 app.setup_switch(0);app.setup_entries[0][0].enterText('New Toon');app.setup_inventory('gags')
 assert app.setup_draft['toons'][0].name=='New Toon';assert len(app.setup_entries)==49
 shot('gags')
 app.setup_inventory('rewards');shot('rewards')
 app.setup_inventory('doodle');shot('doodle')
 app.setup_switch(1);__import__('setup_screen').section(app,'profile');shot('toon')
 app.close_modal();assert app.game is original and app.game.toons[0].name!='New Toon'
 app.open_setup();app.setup_count('toon_count',2);app.setup_count('cog_count',1)
 app.setup_switch(0);app.setup_entries[0][0].enterText('New Toon')
 app.setup_draft['toons'][0].escaped=True;app.apply_setup()
 assert app.modal is None and len(app.game.toons)==2 and len(app.game.cogs)==1
 assert app.game.toons[0].name=='New Toon' and not app.game.toons[0].escaped
 app.open_log();popup=app.log_popup;assert app.modal is None and not app.hud.isHidden()
 for i in range(80):app.game.log.append(f'Round {i+1}: Cog attack hits a Toon for 12 Laff. A long line wraps safely inside the journal.')
 popup.refresh();shot('log')
 popup.follow=False;popup.scroll.verticalScroll['value']=.25
 before=-popup.scroll['canvasSize'][2];app.game.log.append('Another live event');popup.refresh()
 assert 0<popup.scroll.verticalScroll['value']<=.25 and -popup.scroll['canvasSize'][2]>=before
 popup.go_latest();assert popup.follow and popup.scroll.verticalScroll['value']==1
 popup.toggle();shot('log-expanded');popup.toggle()
 app.new_battle();popup.refresh();assert popup.follow and popup.count['text']==f'{len(app.game.log)} entries'
 app.open_setup();popup.refresh();assert popup.frame.isHidden();app.close_modal();popup.refresh();assert not popup.frame.isHidden()
 app.escape_action();assert app.log_popup is None
 print('Setup draft/cancel/apply, lineup sizes, 49-gag grid, all editor sections, live log, scroll retention, expand, reset and close passed.')
finally:app.destroy()
