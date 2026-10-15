"""Draft-only battle setup, with dedicated editors instead of a combined form."""
import math
from direct.gui.DirectGui import DirectFrame,DirectButton,DGG
from panda3d.core import TextNode,TransparencyAttrib
from battle_engine import GAGS,TRACKS,COG_CATALOG,Cog,POUCH_SIZES,carry_limit
from support import REWARDS,DOODLES,SOS,UNITES,REMOTES
INK=(.14,.2,.3,1);GREEN=(.2,.53,.39,1)

def section(app,kind):
 app.flush_setup();app.setup_section=kind;app.setup_kind=kind;app.setup_page=0;app.draw_setup()

def reward_names(app):
 return list({'SOS':SOS,'Unites':UNITES,'Remotes':REMOTES,'Fires':{'Fire':None}}[getattr(app,'setup_reward_group','SOS')])

def reward_group(app,group):
 app.flush_setup();app.setup_reward_group=group;app.setup_page=0;app.draw_setup()

def preset(app,hard):
 app.flush_setup()
 names=['Flunky','Pencil Pusher','Yesman','Micromanager'] if not hard else ['Mr. Hollywood','Robber Baron','Big Wig','The Big Cheese']
 app.setup_draft['cogs']=[(n,COG_CATALOG[n]['rank']+(4 if hard else 0)) for n in names]
 app.setup_draft['version2']=[False]*4;app.setup_draft['skelecogs']=[False]*4;app.draw_setup()

def draw(app):
 if hasattr(app,'setup_body') and not app.setup_body.isEmpty():app.setup_body.destroy()
 app.setup_body=DirectFrame(parent=app.overlay,frameColor=(0,0,0,0));app.setup_entries=[];p=app.setup_body
 for i,tab in enumerate(['Cogs',*range(app.setup_draft['toon_count'])]):
  app.button(p,'Cog lineup' if tab=='Cogs' else app.setup_draft['toons'][tab].name[:16],-1.15+i*.57,.65,app.setup_switch,.54,args=[tab],color=(.50,.77,.74,1) if tab==app.setup_tab else (.85,.87,.84,1),size=.029)
 app.panel(p,(-1.49,1.49,-.72,.55),(.94,.95,.90,1))
 app.setup_error=app.label(p,'',-1.44,-.76,.025,(.72,.13,.1,1))
 app.setup_error['text_wordwrap']=112
 app.label(p,'Changes apply only when you start a new battle.',-1.43,-.84,.026)
 app.button(p,'Cancel',.48,-.83,app.close_modal,.42,size=.029)
 app.button(p,'Start battle',1.12,-.83,app.apply_setup,.68,GREEN,size=.035)
 if app.setup_tab=='Cogs':
  app.label(p,'Battle size',-1.40,.45,.037)
  app.label(p,'Toons',-.85,.45,.03);app.menu(p,[1,2,3,4],-.57,.44,.22,lambda v:app.setup_count('toon_count',v),app.setup_draft['toon_count'])
  app.label(p,'Cogs',-.17,.45,.03);app.menu(p,[1,2,3,4],.08,.44,.22,lambda v:app.setup_count('cog_count',v),app.setup_draft['cog_count'])
  for label,x in [('Department',-1.14),('Cog',-.49),('Level',.53),('Form',.94)]:app.label(p,label,x,.30,.025)
  for i,(name,level) in enumerate(app.setup_draft['cogs'][:app.setup_draft['cog_count']]):
   z=.16-i*.205;app.panel(p,(-1.43,1.43,z-.07,z+.075),(.84,.89,.87,1) if i%2==0 else (.89,.92,.89,1))
   app.label(p,str(i+1),-1.37,z,.034)
   dept=COG_CATALOG[name]['department'];app.menu(p,['Bossbot','Lawbot','Cashbot','Sellbot'],-1.14,z,.58,lambda v,j=i:app.setup_department(j,v),dept)
   app.menu(p,[n for n,d in COG_CATALOG.items() if d['department']==dept],-.49,z,.94,lambda v,j=i:app.setup_cog(j,v),name)
   rank=COG_CATALOG[name]['rank'];app.menu(p,list(range(rank,rank+5)),.53,z,.24,lambda v,j=i:app.setup_level(j,v),level)
   app.menu(p,['Regular','Skelecog','v2.0'],.94,z,.46,lambda v,j=i:app.setup_form(j,v),'v2.0' if app.setup_draft['version2'][i] else 'Skelecog' if app.setup_draft['skelecogs'][i] else 'Regular')
  app.label(p,'Skelecogs keep their base Cog attacks. v2.0 adds a second health layer.',-1.40,-.66,.026)
  return
 t=app.setup_draft['toons'][app.setup_tab];kind=getattr(app,'setup_section','profile')
 for i,(value,title) in enumerate([('profile','Toon details'),('gags','Gag pouch'),('rewards','Rewards'),('doodle','Doodle')]):
  app.button(p,title,-1.09+i*.72,.45,section,.66,args=[app,value],color=(.54,.79,.75,1) if kind==value else (.85,.88,.84,1),size=.03)
 if kind=='profile':
  app.label(p,'Your Toon',-1.35,.29,.04)
  app.label(p,'Name',-1.35,.15,.03);app.entry(p,t.name,-.86,.15,.90,lambda v:setattr(t,'name',v[:18]))
  app.label(p,'Animal',.32,.15,.03);app.menu(p,['cat','dog','bunny','mouse'],.81,.15,.50,lambda v:setattr(t,'animal',v),t.animal)
  app.label(p,'Current Laff',-1.35,-.015,.03);app.entry(p,t.hp,-.66,-.015,.30,lambda v:setattr(t,'hp',v))
  app.label(p,'Maximum Laff',.32,-.015,.03);app.entry(p,t.maximum,1.04,-.015,.28,lambda v:setattr(t,'maximum',v))
  app.label(p,'Gag training',-1.35,-.19,.04)
  app.label(p,'Missing track',-1.35,-.34,.03);app.menu(p,['None','Toon-Up','Trap','Lure','Sound','Drop'],-.62,-.34,.62,lambda v:app.setup_missing(t,v),t.missing_track)
  app.label(p,'Pouch size',.32,-.34,.03);app.menu(p,POUCH_SIZES,1.04,-.34,.28,lambda v:setattr(t,'pouch',int(v)),t.pouch)
  app.label(p,'Organic track',-1.35,-.49,.03);app.menu(p,['None',*TRACKS],-.62,-.49,.62,lambda v:setattr(t,'organic',v),t.organic)
  app.label(p,'Extra level 7',.32,-.49,.03);app.menu(p,['None',*TRACKS],1.04,-.49,.35,lambda v:setattr(t,'extra_seven',v),t.extra_seven)
  app.label(p,'Available tracks are fully trained. Toons do not have character levels.',-1.35,-.65,.026)
 elif kind=='gags':
  app.label(p,'Track / gag level',-1.38,.30,.025)
  app.setup_gag_hint=app.label(p,'Hover over a gag for its name and carry limit.',-1.38,-.585,.023)
  for level in range(1,8):app.label(p,str(level),-.77+(level-1)*.34,.30,.025,align=TextNode.ACenter)
  colors=[(.76,.64,.89,1),(.96,.83,.44,1),(.85,.57,.63,1),(.59,.74,.90,1),(.94,.70,.43,1),(.84,.58,.77,1),(.52,.81,.75,1)]
  for row,track in enumerate(TRACKS):
   z=.195-row*.119;app.panel(p,(-1.40,1.40,z-.052,z+.058),colors[row]);app.label(p,track,-1.35,z-.01,.027)
   for name,g in GAGS.items():
    if g.track!=track:continue
    x=-.77+(g.level-1)*.34
    icon=DirectFrame(parent=p,image=app.icons[name],image_scale=.035,pos=(x-.062,0,z),frameColor=(0,0,0,0));icon.setTransparency(TransparencyAttrib.MAlpha)
    entry=app.entry(p,t.stock.get(name,0),x-.012,z-.012,.125,lambda v,n=name:t.stock.__setitem__(n,v))
    hint=f'{name}: carry up to {carry_limit(g,t.extra_seven)}'
    entry.bind(DGG.ENTER,lambda event,text=hint:app.setup_gag_hint.__setitem__('text',text))
    if track==t.missing_track:entry['state']=DGG.DISABLED;icon.setColorScale(.4,.4,.4,1)
  app.setup_pouch_label=app.label(p,'',-1.38,-.65,.026)
  app.button(p,'Clear',.45,-.65,app.setup_fill,.40,args=[t,False],size=.026)
  app.button(p,'Balanced fill',1.08,-.65,app.setup_fill,.73,args=[t,True],size=.026)
  update_pouch(app)
 elif kind=='rewards':
  group=getattr(app,'setup_reward_group','SOS')
  for i,title in enumerate(['SOS','Unites','Remotes','Fires']):app.button(p,title,-1.12+i*.73,.29,reward_group,.63,args=[app,title],color=(.62,.78,.84,1) if title==group else (.85,.88,.84,1),size=.027)
  names=reward_names(app);pages=max(1,math.ceil(len(names)/8));app.setup_page%=pages
  for i,name in enumerate(names[app.setup_page*8:app.setup_page*8+8]):
   x=-1.36+(i%2)*1.45;z=.105-(i//2)*.16
   app.label(p,name.replace('SOS: ','').replace('Unite: ',''),x,z,.025)
   app.entry(p,t.rewards.get(name,0),x+1.0,z,.19,lambda v,n=name:t.rewards.__setitem__(n,v))
   app.label(p,'/200' if name=='Fire' else '/100',x+1.20,z,.021)
  app.button(p,'Previous',-.65,-.59,app.setup_next,.49,args=[-1],size=.026);app.label(p,f'Page {app.setup_page+1} of {pages}',0,-.60,.028,align=TextNode.ACenter);app.button(p,'Next',.65,-.59,app.setup_next,.49,args=[1],size=.026)
  app.label(p,'Unites stay separate from your gag choice during battle.',-1.36,-.68,.024)
 else:
  app.label(p,'Training points per trick',-1.35,.28,.031)
  app.button(p,'Happy' if t.doodle_happy else 'Negative mood',.91,.29,app.setup_toggle,.80,args=[t,'doodle_happy'],size=.027)
  for i,name in enumerate(DOODLES):
   t.doodle_skills.setdefault(name,10000 if t.doodle_trained else 0);z=.13-i*.10
   app.label(p,name.removeprefix('Doodle: '),-1.28,z,.028);app.entry(p,t.doodle_skills[name],-.38,z,.38,lambda v,n=name:t.doodle_skills.__setitem__(n,v));app.label(p,'/ 10,000',.09,z,.025)
  app.button(p,'Reset training',-.80,-.63,app.setup_doodle_fill,.77,args=[t,False],size=.027);app.button(p,'Max training',.32,-.63,app.setup_doodle_fill,.77,args=[t,True],size=.027)

def update_pouch(app):
 if app.modal!='setup' or app.setup_tab=='Cogs' or getattr(app,'setup_section','profile')!='gags':return
 try:
  values=[int(entry.get()) for entry,callback in app.setup_entries]
  toon=app.setup_draft['toons'][app.setup_tab]
  for (entry,callback),value,gag in zip(app.setup_entries,values,GAGS.values()):
   entry['frameColor']=(1,.76,.72,1) if not 0<=value<=carry_limit(gag,toon.extra_seven) else (1,1,1,1)
  count=sum(v for v,g in zip(values,GAGS.values()) if g.level<7)
  app.setup_pouch_label['text_fg']=(.72,.13,.1,1) if count>toon.pouch else INK
  # Entries are track-major, as is the GAGS catalog.
  app.setup_pouch_label['text']=f'Regular gags: {count} / {app.setup_draft["toons"][app.setup_tab].pouch}   (level 7 stored separately)'
 except ValueError:app.setup_pouch_label['text']='Enter whole numbers for gag quantities.'
