"""Battle rewards. Current public values; edge-case assumptions in MECHANICS.md."""
SOS={}
for track,names,values in [
 ('Toon-Up',['Madam Chuckle','Daffy Don','Flippy'],[60,120,180]),
 ('Trap',['Clerk Will','Clerk Penny','Clerk Clara'],[60,120,180]),
 ('Lure',['Stinky Ned','Nancy Gas','Lil Oldman'],[4,5,6]),
 ('Sound',['Barbara Seville','Sid Sonata','Moe Zart'],[35,55,75]),
 ('Drop',['Clumsy Ned','Franz Neckvein','Barnacle Bessie'],[60,100,170]),
 ('Toons Hit',['Soggy Bottom','Soggy Nell','Sticky Lou'],[3,4,5]),
 ('Cogs Miss',['Flim Flam','Mr. Freeze','Julius Wheezer'],[3,4,5])]:
 for name,value in zip(names,values):SOS['SOS: '+name]=(track,value)
TRACKS=('Toon-Up','Trap','Lure','Sound','Throw','Squirt','Drop')
for track,name in zip(TRACKS,['Professor Guffaw','Clerk Ray','Doctor Drift','Melody Wavers','Baker Bridget','Sofie Squirt','Shelly Seaweed']):
 SOS['SOS: '+name]=('Restock '+track,12)
SOS.update({'SOS: Professor Pete':('Restock All',45),'SOS: Rocky':('Throw',132),'SOS: Loopy Loopenloop':('Squirt',115),'SOS: Lord Lowden Clear':('Fire',0)})
REMOTES={f'{kind} remote {stars}★':(kind,stars+1,(45,90,150)[stars-1],(30+15*stars if kind=='Damage' else 10+5*stars)) for kind in ('Damage','Healing') for stars in (1,2,3)}
DOODLES={f'Doodle: {name}':(heal,positive,negative,low) for name,heal,positive,negative,low in [('Jump',10,97,60,50),('Beg',12,87,54,45),('Play Dead',14,78,48,40),('Rollover',16,68,42,35),('Backflip',18,58,36,30),('Dance',20,49,30,25),('Speak',22,39,24,20)]}
UNITES={**{f'Unite: Toon-Up {n}':('Toon-Up',n) for n in (20,35,50,65,80)},**{f'Unite: Gag-Up {track}':(track,30 if track=='All' else 7) for track in (*TRACKS,'All')}}
REWARDS={**SOS,**REMOTES,'Fire':('Fire',1),**UNITES}
CATEGORIES={'SOS cards':list(SOS),'Remotes':list(REMOTES),'Fire':['Fire'],'Doodle':list(DOODLES)}

def support_targets(game,toon,name):
 if name in REMOTES or name=='Fire':return [(i,c) for i,c in enumerate(game.cogs) if c.alive]
 if name in SOS or name in DOODLES:return []
 raise ValueError('Choose a listed battle action.')

def validate_support(game,a):
 if a.gag not in (*SOS,*REMOTES,*DOODLES,'Fire'):raise ValueError('Choose a battle action.')
 if SOS.get(a.gag,(None,))[0]=='Lure' and not game.lure_available:raise ValueError('All living Cogs are already lured. Choose another action.')
 if SOS.get(a.gag,(None,))[0]=='Trap' and not game.lure_available:raise ValueError('Trap cannot be used on already lured Cogs.')
 if a.gag not in DOODLES and game.toons[a.toon].rewards.get(a.gag,0)<=0:raise ValueError('This reward is out of stock.')
 if a.gag in REMOTES or a.gag=='Fire':
  if a.target not in [i for i,c in enumerate(game.cogs) if c.alive]:raise ValueError('Select a living Cog.')
  if a.gag in REMOTES and game.cogs[a.target].remote:raise ValueError('This simulator does not replace active remotes; choose another Cog.')

def heal(game,total,reason,split=False,recipients=None):
 living=[t for i,t in enumerate(game.toons) if t.alive and (recipients is None or i in recipients)]
 if not living:return
 amount,remainder=divmod(total,len(living)) if split else (total,0)
 for i,t in enumerate(living):
  n=min(t.maximum-t.hp,amount+(i<remainder));t.hp+=n
  if n:game.record_health(('toon',next(j for j,member in enumerate(game.toons) if member is t),n))
  game.log.append(f'{reason} → {t.name}: +{n} Laff.')

def restock(game,track,count,recipients=None):
 from battle_engine import GAGS,carry_limit
 for i,t in enumerate(game.toons):
  if not t.alive or (recipients is not None and i not in recipients):continue
  remaining=count
  for n,g in sorted(GAGS.items(),key=lambda item:-item[1].level):
   if g.level==7 or g.level>t.track_levels.get(g.track,7) or g.track==t.missing_track or track not in ('All',g.track):continue
   add=max(0,min(remaining,carry_limit(g)-t.stock[n],t.pouch-t.carried))
   t.stock[n]+=add;remaining-=add
  game.log.append(f'{t.name}: restocked {count-remaining} regular gags ({track}).')

def use_unite(game,index,name,positions=None,radius=None):
 if game.result or not 0<=index<len(game.toons) or not game.toons[index].alive:raise ValueError('Choose a living Toon in an active battle.')
 t=game.toons[index]
 if name not in UNITES:raise ValueError('Choose a listed unite.')
 if t.unite_cooldown:raise ValueError(f'Unites ready in {t.unite_cooldown} rounds for {t.name}.')
 if t.rewards.get(name,0)<=0:raise ValueError('This unite is out of stock.')
 recipients=None
 if positions is not None:
  from math import dist
  if len(positions)!=len(game.toons):raise ValueError('Unite positions must cover every Toon.')
  if radius is None or radius<=0:raise ValueError('Supply an explicit positive radius for spatial test cases; the current TTR radius is unverified.')
  recipients={i for i,pos in enumerate(positions) if i==index or dist(positions[index],pos)<radius}
 t.rewards[name]-=1;t.unite_cooldown=3
 kind,value=UNITES[name]
 if kind=='Toon-Up' and name.startswith('Unite: Toon-Up'):heal(game,value,name,recipients=recipients)
 else:restock(game,kind,value,recipients=recipients)
 game.log.append(f'{t.name} uses {name}. Their gag action remains available.')
 return [i for i,member in enumerate(game.toons) if member.alive and (recipients is None or i in recipients)]

def resolve_support(game,a,early=False,track=None):
 name=a.gag
 if early:
  if name not in DOODLES:game.toons[a.toon].rewards[name]-=1
  if name=='Fire':game.damage(a.target,game.cogs[a.target].hp,'Pink slip',bypass_layers=True)
  elif name in REMOTES:
   if game.cogs[a.target].alive:
    game.cogs[a.target].remote=REMOTES[name];game.cogs[a.target].lure=0
    game.log.append(f'{game.cogs[a.target].name}: {name} attached.')
  elif name in DOODLES:
   t=game.toons[a.toon]
   power,chance=doodle_stats(t,name)
   # Pet probabilities are continuous, unlike the gag engine's integer roll.
   success=game.rng.random()*100<chance
   if game._movie_event is not None:game._movie_event['doodle_success']=success
   if success:
    points=t.doodle_skills.get(name,10000 if t.doodle_trained else 0)
    t.doodle_skills[name]=min(10000,points+5)
    heal(game,power,name)
    game.log.append(f'{name}: {t.doodle_skills[name]}/10000 training points.')
   else:game.log.append(f'{name}: failed ({chance:g}% success chance).')
  elif name in SOS:
   kind,value=SOS[name]
   if kind=='Toons Hit':
    game.hit_scoped=True
    for t in game.toons:
     if t.alive:t.accuracy_up=max(t.accuracy_up,value)
    game.hit_rounds=max((t.accuracy_up for t in game.toons),default=0)
   elif kind=='Cogs Miss':
    game.miss_scoped=True
    for c in game.cogs:
     if c.alive:c.accuracy_down=max(c.accuracy_down,value)
    game.miss_rounds=max((c.accuracy_down for c in game.cogs),default=0)
   elif kind.startswith('Restock '):restock(game,kind[8:],value)
   elif kind=='Fire':
    for i,c in enumerate(game.cogs):
     if c.alive:game.damage(i,c.hp,name,bypass_layers=True)
  return
 if name not in SOS:return
 kind,value=SOS[name]
 if kind!=track:return
 game.log.append(name)
 if kind=='Toon-Up':heal(game,value,name,True);return
 hit_targets=set()
 for i,c in enumerate(game.cogs):
  if not c.alive:continue
  if kind=='Trap':
   if not c.lure and not c.trap:c.trap=(name,value)
  elif kind=='Lure':
   if c.trap:
    trap,power=c.trap;c.trap=None;game.damage(i,power,trap+' triggered');game.hits.append(('Trap',{i},False,50))
   elif not c.lure:c.lure=value
  elif kind=='Drop' and c.lure:game.log.append(f'{c.name}: SOS Drop misses while lured.')
  else:
   from math import ceil
   game.damage(i,value+(ceil(value*.5) if c.lure and kind in ('Throw','Squirt') else 0),name)
   c.lure=0
   hit_targets.add(i)
 if hit_targets:game.hits.append((kind,hit_targets,True,25))

def remote_tick(game,index):
 c=game.cogs[index];kind,rounds,expiry,power=c.remote
 if game._movie_event is not None:
  game._movie_event['remote_kind']=kind;game._movie_event['remote_before']=c.remote
 if kind=='Healing':heal(game,power,f'{c.name} healing remote')
 else:
  for j,other in enumerate(game.cogs):
   if j!=index and other.alive:
    game.damage(j,power,f'{c.name} damage remote');other.lure=0
 rounds-=1
 c.remote=(kind,rounds,expiry,power) if rounds else None
 if not rounds:game.damage(index,expiry,'Remote expired')
 else:game.log.append(f'{c.name}: remote has {rounds} rounds remaining.')

def describe(game,index,name):
 if name in REMOTES:
  kind,rounds,expiry,power=REMOTES[name]
  info=f'{rounds} rounds · {power} '+('damage to other Cogs' if kind=='Damage' else 'Laff per Toon')+f' · {expiry} expiry damage'
 elif name in SOS:
  kind,value=SOS[name]
  if kind=='Fire':info='Dismiss all living Cogs, including v2 layers'
  elif kind=='Toon-Up':info=f'{value} total Laff split among living Toons, including you'
  elif kind.startswith('Restock'):info=f'Up to {value} unlocked regular gags per Toon · {kind}'
  elif kind in ('Toons Hit','Cogs Miss'):info=f'{kind}: 75 percentage points · {value} rounds · current recipients'
  elif kind=='Lure':info=f'Lure eligible Cogs · {value} rounds'
  elif kind=='Trap':info=f'{value} damage when lured · only empty, unlured trap slots'
  else:info=f'{value} damage per eligible Cog · {kind}'
 elif name in DOODLES:
  t=game.toons[index];power,chance=doodle_stats(t,name)
  return f'{power} Laff per Toon · {chance:g}% success · {t.doodle_skills.get(name,10000 if t.doodle_trained else 0)}/10000 XP'
 else:info='Dismiss one Cog immediately'
 return info+f' · {game.toons[index].rewards.get(name,0)} left'

def doodle_stats(toon,name):
 from combat_rules import doodle_values
 return doodle_values(toon.doodle_skills.get(name,10000 if toon.doodle_trained else 0),list(DOODLES).index(name),toon.doodle_happy)

SOS_STARS={name:(3+list(SOS).index(name)%3 if list(SOS).index(name)<21 else 5 if name in ("SOS: Professor Pete","SOS: Rocky","SOS: Loopy Loopenloop","SOS: Lord Lowden Clear") else 3) for name in SOS}
