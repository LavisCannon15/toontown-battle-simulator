"""Local practice partners: varied legal choices, separate from combat randomness."""
from battle_engine import Action,GAGS

def choose_action(game,index,rng):
 """Choose without looking at other Toons' pending plans; conserve rare supplies."""
 if not game.toons[index].alive or game.result:return Action(index)
 candidates=[];weights=[]
 for name,gag in GAGS.items():
  if gag.level==7:continue
  targets=game.targets(index,name)
  for target in ([None] if gag.group else [i for i,_ in targets]):
   action=Action(index,name,target)
   try:game.validate(action)
   except ValueError:continue
   weight={'Toon-Up':1,'Trap':1,'Lure':2,'Sound':3,'Throw':5,'Squirt':5,'Drop':2}[gag.track]
   if gag.track=='Toon-Up':
    injured=[t for i,t in enumerate(game.toons) if i!=index and t.alive and t.hp<t.maximum*.7 and (gag.group or i==target)]
    if not injured:continue
    weight=25
   elif gag.track=='Trap' and target is not None and game.cogs[target].trap:continue
   elif gag.track=='Drop' and target is not None and game.cogs[target].lure:continue
   elif gag.track in ('Throw','Squirt') and target is not None and game.cogs[target].lure:weight=12
   candidates.append(action);weights.append(weight)
 return rng.choices(candidates,weights=weights,k=1)[0] if candidates else Action(index)
