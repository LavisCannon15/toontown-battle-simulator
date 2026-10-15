"""Independent battle model. Public TTR rules with explicit limits in MECHANICS.md."""
from __future__ import annotations
from dataclasses import dataclass, field
from math import ceil
import random
from combat_rules import capped_accuracy, cog_accuracy
import json
from pathlib import Path
COG_CATALOG = json.loads((Path(__file__).parent / "cogs.json").read_text())

TRACKS = ('Toon-Up', 'Trap', 'Lure', 'Sound', 'Throw', 'Squirt', 'Drop')

@dataclass(frozen=True)
class Gag:
    name: str
    track: str
    level: int
    power: int
    accuracy: int
    group: bool = False
    rounds: int = 0

# Fully trained gag values, including the seven level 7 group gags.
_DATA = {
    'Toon-Up': [('Feather',10),('Megaphone',18),('Lipstick',30),('Bamboo Cane',45),('Pixie Dust',60),('Juggling Cubes',105)],
    'Trap': [('Banana Peel',12),('Rake',20),('Marbles',35),('Quicksand',50),('Trapdoor',85),('TNT',180)],
    'Lure': [('$1 Bill',0),('Small Magnet',0),('$5 Bill',0),('Big Magnet',0),('$10 Bill',0),('Hypno-goggles',0)],
    'Sound': [('Bike Horn',4),('Whistle',7),('Bugle',11),('Aoogah',16),('Elephant Trunk',21),('Foghorn',50)],
    'Throw': [('Cupcake',6),('Fruit Pie Slice',10),('Cream Pie Slice',17),('Whole Fruit Pie',27),('Whole Cream Pie',40),('Birthday Cake',100)],
    'Squirt': [('Squirting Flower',4),('Glass of Water',8),('Squirt Gun',12),('Seltzer Bottle',21),('Fire Hose',30),('Storm Cloud',80)],
    'Drop': [('Flower Pot',10),('Sandbag',18),('Anvil',30),('Big Weight',45),('Safe',70),('Grand Piano',170)],
}
for track, row in zip(TRACKS, [('High Dive',210),('Railroad',200),('Presentation',0),('Opera Singer',90),('Wedding Cake',120),('Geyser',105),('Toontanic',180)]):
    _DATA[track].append(row)
GAGS = {}
for track, rows in _DATA.items():
    for level, (name, power) in enumerate(rows, 1):
        accuracy = {'Toon-Up':70,'Trap':100,'Sound':95,'Throw':75,'Squirt':95,'Drop':50}.get(track)
        if name == 'High Dive':accuracy=95
        if track == 'Lure':
            accuracy = (60,55,70,65,80,75,90)[level-1]
        group = level == 7 or track == 'Sound' or track in ('Toon-Up','Lure') and level % 2 == 0
        GAGS[name] = Gag(name,track,level,power,accuracy,group,
                         (2,2,3,3,4,4,8)[level-1] if track == 'Lure' else 0)

DEFAULT_COGS = ('Mr. Hollywood','Robber Baron','Big Wig','The Big Cheese')
DEFENSE = {1:2,2:5,3:10,4:15,5:20,6:25,7:30,8:35,9:40,10:45,11:50,12:55}
SCENARIOS = {'Easy': (8,8), 'Normal': (8,9,10,11), 'Hard': (12,12,12,12)}


def cog_health(level):
    if not 1 <= level <= 12:
        raise ValueError('Supported Cog levels are 1–12.')
    return (level+1)*(level+2) + (14 if level >= 12 else 0)


POUCH_SIZES = (20,25,30,35,40,50,60,70,80)

def inventory():
    return {name: (1 if g.level==7 else (1,1,1,2,3,2 if g.track=='Sound' else 3)[g.level-1])
            for name,g in GAGS.items()}

def carry_limit(gag, extra='None'):
    if gag.level == 7:
        return 2 if gag.track == extra else 1
    return ((20,15,15,10,5,2) if gag.track=='Sound' else (30,25,20,15,7,3))[gag.level-1]


@dataclass
class Toon:
    name: str
    hp: int = 100
    maximum: int = 100
    stock: dict = field(default_factory=inventory)
    organic: str = 'None'
    animal: str = 'cat'
    pouch: int = 80
    missing_track: str = 'None'
    extra_seven: str = 'None'
    rewards: dict = field(default_factory=dict)
    unite_cooldown: int = 0
    doodle_trained: bool = True
    doodle_happy: bool = True
    doodle_skills: dict = field(default_factory=dict)
    track_levels: dict = field(default_factory=dict)
    escaped: bool = False
    accuracy_up: int = 0

    @property
    def carried(self):
        return sum(v for n,v in self.stock.items() if GAGS[n].level<7)

    def check_inventory(self, stock):
        if self.pouch not in POUCH_SIZES:
            raise ValueError('Choose a listed gag pouch size.')
        for n,g in GAGS.items():
            value=stock.get(n,0)
            if type(value) is not int or not 0<=value<=carry_limit(g,self.extra_seven):
                raise ValueError(f'{n}: carry limit {carry_limit(g,self.extra_seven)}.')
            if g.track==self.missing_track and value:
                raise ValueError(f'{g.track} is not unlocked for this Toon.')
        if sum(v for n,v in stock.items() if GAGS[n].level<7)>self.pouch:
            raise ValueError('The regular gag pouch is over capacity.')


    @property
    def alive(self):
        return self.hp > 0 and not self.escaped


@dataclass
class Cog:
    name: str
    level: int
    hp: int = field(init=False)
    maximum: int = field(init=False)
    lure: int = 0
    accuracy_down: int = 0
    remote: tuple | None = None
    trap: tuple[str,int] | None = None
    skelecog: bool = False
    version2: bool = False

    def __post_init__(self):
        if self.name not in COG_CATALOG:
            raise ValueError('Choose one of the 32 standard Cogs.')
        self.hp = self.maximum = cog_health(self.level)

    @property
    def alive(self):
        return self.hp > 0


@dataclass(frozen=True)
class Action:
    toon: int
    gag: str = 'Pass'
    target: int | None = None


class Battle:
    def __init__(self, difficulty='Normal', seed=None, organic='None'):
        if difficulty not in SCENARIOS or organic not in ('None', *TRACKS):
            raise ValueError('Invalid battle setup.')
        self.rng = random.Random(seed)
        self.toons = [Toon(n, organic=organic) for n in ('You', 'Buddy', 'Flippy', 'Bubbles')]
        self.cogs = [Cog(name,lv) for name,lv in zip(DEFAULT_COGS, SCENARIOS[difficulty])]
        from support import REWARDS
        for i,t in enumerate(self.toons):
            t.animal=('cat','dog','bunny','mouse')[i]
            t.rewards={n:2 for n in REWARDS}
        self.hit_rounds = self.miss_rounds = 0
        self.round = 1
        self.plans: dict[int,Action] = {}
        self.log = ['Plan one action per living Toon, then resolve the round.',
                    'Sandbox loadout: all seven tracks. Setup can select a normal six-track build.',
                    'Accuracy uses the documented legacy 95% cap; see Mechanics for current TTR limits.']
        self.hits = []
        self.health_events = []
        self.movie_events = []
        self._movie_event = None

    @property
    def result(self):
        if not any(c.alive for c in self.cogs):
            return 'Victory! All Cogs defeated.'
        if not any(t.alive for t in self.toons):
            if any(t.escaped for t in self.toons):return 'Cogs win! The Toons left the battle.'
            return 'Cogs win! All Toons went sad.'
        return None

    @property
    def ready(self):
        return not self.result and all(i in self.plans for i,t in enumerate(self.toons) if t.alive)

    @property
    def lure_available(self):
        return any(c.alive and not c.lure for c in self.cogs)

    def targets(self, toon, name):
        if name == 'Pass':
            return []
        if name not in GAGS:
            from support import support_targets
            return support_targets(self,toon,name)
        gag = GAGS[name]
        if gag.group:
            return []
        fighters = self.toons if gag.track == 'Toon-Up' else self.cogs
        return [(i,t) for i,t in enumerate(fighters) if t.alive and (gag.track != 'Toon-Up' or i != toon) and (gag.track not in ('Lure','Trap') or not t.lure)]

    def validate(self, action):
        if self.result:
            raise ValueError('Start a new battle first.')
        if not 0 <= action.toon < len(self.toons) or not self.toons[action.toon].alive:
            raise ValueError('Choose a living Toon.')
        if action.gag == 'Pass':
            return
        if action.gag not in GAGS:
            from support import validate_support
            return validate_support(self,action)
        toon, gag = self.toons[action.toon], GAGS[action.gag]
        if gag.track=='Lure' and not self.lure_available:
            raise ValueError('All living Cogs are already lured. Choose another action; no round or gag was spent.')
        if gag.track=='Trap' and not self.lure_available:
            raise ValueError('Trap cannot be used: all living Cogs are already lured. No round or gag was spent.')
        if gag.track==toon.missing_track:
            raise ValueError('That track is not unlocked.')
        if toon.stock[action.gag] <= 0:
            raise ValueError('That gag is out of stock for this Toon.')
        if gag.track == 'Toon-Up' and not any(t.alive and i != action.toon for i,t in enumerate(self.toons)):
            raise ValueError('Toon-Up requires another living Toon; it cannot heal yourself.')
        if gag.track == 'Trap' and not gag.group and action.target is not None and 0 <= action.target < len(self.cogs) and self.cogs[action.target].lure:
            raise ValueError('Trap cannot be placed on an already lured Cog.')
        if not gag.group and action.target not in [i for i,_ in self.targets(action.toon,action.gag)]:
            raise ValueError('Choose a valid target. Toon-Up cannot heal yourself.')

    def plan(self, action):
        self.validate(action)
        self.plans[action.toon] = action

    def power(self, action):
        g = GAGS[action.gag]
        if self.toons[action.toon].organic != g.track or g.track == 'Lure':
            return g.power
        percent = {'Toon-Up':20,'Squirt':15,'Drop':15}.get(g.track,10)
        return g.power + ceil(g.power*percent/100)

    def victims(self, action):
        g = GAGS[action.gag]
        if g.track == 'Toon-Up':
            return [i for i,t in enumerate(self.toons) if t.alive and i != action.toon and (g.group or i == action.target)]
        return [i for i,c in enumerate(self.cogs) if c.alive and (g.group or i == action.target)]

    def accuracy(self, actions, targets, *, capped=True):
        """Percent, including shared-track accuracy; no RNG or state changes."""
        gags = [GAGS[a.gag] for a in actions]
        track, group = gags[0].track, gags[0].group
        if track == 'Trap':
            return 100
        if getattr(self,'sos_track',None)==track and track!='Toon-Up':
            return 100
        if track not in ('Toon-Up','Lure') and targets and all(self.cogs[i].remote for i in targets):
            return 100
        if track == 'Toon-Up':
            raw=max(g.accuracy+(self.toons[a.toon].track_levels.get(g.track,7)-1)*5 for a,g in zip(actions,gags))
            raw += 75 if any(self.toons[a.toon].accuracy_up if getattr(self,'hit_scoped',False) else self.hit_rounds for a in actions) else 0
            return capped_accuracy(raw) if capped else raw
        if not targets:
            return 0
        if track == 'Drop' and all(self.cogs[i].lure for i in targets):
            return 0
        if track in ('Throw','Squirt','Sound') and all(self.cogs[i].lure for i in targets):
            return 100
        base = max(min(95,g.accuracy + (10 if track=='Lure' and self.toons[a.toon].organic=='Lure' else 0))
                   for a,g in zip(actions,gags))
        defense = max((12 if self.cogs[i].level==4 else 15) if COG_CATALOG[self.cogs[i].name]['rank']==1 and self.cogs[i].level in (4,5) else DEFENSE[self.cogs[i].level] for i in targets)
        bonus = 75 if any(self.toons[a.toon].accuracy_up if getattr(self,'hit_scoped',False) else self.hit_rounds for a in actions) else 0
        if track == 'Lure':
            tiers = sorted((min(3,(g.level+1)//2) for g in gags),reverse=True)
            bonus += sum(max(10,20-5*(tiers[0]-tier)) for tier in tiers[1:])
            traps = sum(self.cogs[i].trap is not None for i in targets)
            bonus += 10 + 5*(traps-1) if traps else 0
        else:
            matched = [h for h in self.hits if h[0] != track and (group or h[2] or set(targets)&h[1])]
            bonus += sum(h[3] for h in matched if h[0]!='Trap')
            bonus += 50 if any(h[0]=='Trap' for h in matched) else 0
            if track == 'Sound' or (track in ('Throw','Squirt') and any(g.level==7 for g in gags)):
                bonus += 100*sum(bool(self.cogs[i].lure or self.cogs[i].remote) for i in targets)/len(targets)
        experience=max((self.toons[a.toon].track_levels.get(track,7)-1)*10 for a in actions)
        raw=base+experience-defense+bonus
        return capped_accuracy(raw) if capped else raw

    def roll(self, chance):
        return self.rng.randrange(100) < chance

    def resolve(self):
        """Synchronous adapter for headless use; GUI consumes resolve_events()."""
        start=len(self.log)
        for event in self.resolve_events():pass
        return self.log[start:]

    def finish_event(self):
        if self._movie_event is None:return None
        event=self._movie_event
        event['lure_after']=[c.lure for c in self.cogs]
        self._movie_event=None
        return event

    def resolve_events(self):
        if not self.ready:
            raise ValueError('Choose an action for every living Toon.')
        actions = [self.plans[i] for i,t in enumerate(self.toons) if t.alive]
        # Validate the whole round before mutating inventory or health.
        for a in actions:
            self.validate(a)
        from support import REMOTES
        remote_targets=[a.target for a in actions if a.gag in REMOTES]
        if len(remote_targets)!=len(set(remote_targets)):
            raise ValueError('Choose different Cogs for simultaneous remotes.')
        start = len(self.log)
        self.log.append(f'━━ Round {self.round} ━━')
        self.hits = []
        self.health_events = []
        self.movie_events = []
        self._movie_event = None
        from support import resolve_support
        special=[a for a in actions if a.gag!='Pass' and a.gag not in GAGS]
        remote_actions=[a for a in special if a.gag in REMOTES]
        remotes_started=False
        for a in special:
            if a.gag in REMOTES:
                if remotes_started:
                    continue
                remotes_started=True
                batch=remote_actions
            else:
                batch=[a]
            self.begin_movie_event('support',actions=batch)
            for action in batch:
                resolve_support(self,action,early=True)
            yield self.finish_event()
        actions=[a for a in actions if a not in special]
        for track in TRACKS:
            prior_traps=[c.trap for c in self.cogs]
            selected = [a for a in actions if a.gag!='Pass' and GAGS[a.gag].track==track]
            self.begin_movie_event('gags',track=track,actions=selected,targets={a.toon:self.victims(a) for a in selected})
            self.sos_track=track if any(__import__('support').SOS.get(a.gag,(None,))[0]==track for a in special) else None
            for a in special:
                if __import__('support').SOS.get(a.gag,(None,))[0]!=track:continue
                start_health=len(self._movie_event['health'])
                before_lure=[c.lure for c in self.cogs]
                before_trap=[c.trap for c in self.cogs]
                before_alive=[c.alive for c in self.cogs]
                resolve_support(self,a,track=track)
                self._movie_event.setdefault('support_events',{})[a.toon]=dict(
                    kind='gags',track=track,action=a,actions=[],misses=[],
                    health=self._movie_event['health'][start_health:],
                    lure_before=before_lure,lure_after=[c.lure for c in self.cogs],
                    trap_before=before_trap,cogs_alive_before=before_alive)
            regular_start=len(self._movie_event['health'])
            self._movie_event['regular_lure_before']=[c.lure for c in self.cogs]
            self._movie_event['regular_trap_before']=[c.trap for c in self.cogs]
            selected = [a for a in actions if a.gag!='Pass' and GAGS[a.gag].track==track]
            selected=[a for a in selected if self.victims(a)]
            self._movie_event['actions']=selected
            self._movie_event['targets']={a.toon:self.victims(a) for a in selected}
            for a in selected:self.toons[a.toon].stock[a.gag]-=1
            if not selected:
                self._movie_event['regular_health']=[]
                yield self.finish_event()
                continue
            self.log.append(f'[{track}]')
            if track=='Toon-Up':
                for a in selected:
                    health_start=len(self._movie_event['health'])
                    targets = self.victims(a)
                    if not targets:
                        continue
                    hit = self.roll(self.accuracy([a],targets))
                    total = self.power(a) if hit else ceil(self.power(a)*.2)
                    # Divide the total, preserving its remainder in Toon order.
                    share, remainder = divmod(total,len(targets))
                    for index,i in enumerate(targets):
                        t = self.toons[i]
                        amount = min(t.maximum-t.hp,share+(index<remainder))
                        t.hp += amount
                        if amount:self.record_health(('toon',i,amount))
                        self.log.append(f'{self.toons[a.toon].name} → {t.name}: +{amount} Laff ({a.gag}{" — weak heal" if not hit else ""}).')
                    self._movie_event.setdefault('health_by_action',{})[a.toon]=self._movie_event['health'][health_start:]
            elif track=='Trap':
                buckets = {}
                for a in selected:
                    for target in self.victims(a):
                        if not self.cogs[target].lure:
                            buckets.setdefault(target,[]).append(a)
                for target, group in buckets.items():
                    cog = self.cogs[target]
                    if cog.trap and cog.trap==prior_traps[target] and prior_traps[target] is not None and len(selected)==1 and group[0].gag=='Railroad' and not any(__import__('support').SOS.get(a.gag,(None,))[0]=='Trap' for a in special):
                        cog.trap=('Railroad',self.power(group[0]))
                        self.log.append(f'{cog.name}: Railroad replaces the previous trap.')
                    elif cog.trap or len(group)>1:
                        cog.trap = None
                        self.log.append(f'{cog.name}: traps collide and cancel!')
                    else:
                        a = group[0]
                        cog.trap = (a.gag,self.power(a))
                        self.log.append(f'{cog.name}: {a.gag} placed ({self.power(a)} damage when lured).')
            else:
                buckets = {}
                track_hits = {}
                for a in selected:
                    g = GAGS[a.gag]
                    if track=='Lure':
                        buckets.setdefault(('all' if g.group else a.target),[]).append(a)
                    else:
                        for target in self.victims(a):
                            buckets.setdefault(target,[]).append(a)
                rolls={}
                for bucket,group in buckets.items():
                    targets = self.victims(group[0]) if track=='Lure' else [bucket]
                    if not targets:
                        self.log.append('Target already defeated; committed gags are spent.')
                        continue
                    g = GAGS[group[0].gag]
                    roll_targets=sorted({j for a in group for j in self.victims(a)})
                    chance = self.accuracy(group,roll_targets)
                    signature=tuple(group)
                    if signature not in rolls: rolls[signature]=self.roll(chance)
                    hit = rolls[signature]
                    names = ' + '.join(a.gag for a in group)
                    self.log.append(f'{names}: {chance:g}% chance — {"HIT" if hit else "MISS"}.')
                    if not hit:
                        self._movie_event['misses'].extend(targets)
                        continue
                    if track == 'Lure':
                        for i in targets:
                            cog = self.cogs[i]
                            if cog.lure:
                                self.log.append(f'{cog.name} is already lured; duration is not extended.')
                            elif cog.trap:
                                name,damage = cog.trap
                                cog.trap = None
                                self.damage(i,damage,f'{name} triggered')
                                self.hits.append(('Trap',{i},False,50))
                            else:
                                cog.lure = max(GAGS[a.gag].rounds for a in group)
                                self.log.append(f'{cog.name}: lured for {cog.lure} Cog phases.')
                    else:
                        successful = set()
                        for i in targets:
                            cog = self.cogs[i]
                            if track=='Drop' and cog.lure:
                                self._movie_event['misses'].append(i)
                                self.log.append(f'{cog.name}: Drop misses while lured.')
                                continue
                            base = sum(self.power(a) for a in group)
                            combo = ceil(base*.2) if len(group)>1 else 0
                            knockback = ceil(base*.5) if cog.lure and track in ('Throw','Squirt') else 0
                            self._movie_event.setdefault('damage_components',{})[i]={'base':base,'combo':combo,'knockback':knockback}
                            self._movie_event.setdefault('damage_by_action',{}).setdefault(i,{}).update({a.toon:self.power(a) for a in group})
                            self.damage(i,base+combo+knockback,f'{base} base + {combo} combo + {knockback} lure')
                            cog.lure = 0
                            successful.add(i)
                        if successful:
                            for a in group: track_hits.setdefault(a,set()).update(successful)
                self.hits.extend((track,targets,GAGS[a.gag].group,25) for a,targets in track_hits.items())
            self._movie_event['regular_health']=self._movie_event['health'][regular_start:]
            yield self.finish_event()
        for a in actions:
            if a.gag=='Pass':
                self.log.append(f'{self.toons[a.toon].name} passes.')
        if not self.result:
            if getattr(self.cog_phase,'__func__',None) is Battle.cog_phase:
                yield from self.cog_events()
            else:self.cog_phase()
        self.sos_track=None
        for t in self.toons:t.accuracy_up=max(0,t.accuracy_up-1)
        for c in self.cogs:c.accuracy_down=max(0,c.accuracy_down-1)
        self.hit_rounds=max(0,self.hit_rounds-1)
        self.miss_rounds=max(0,self.miss_rounds-1)
        for t in self.toons: t.unite_cooldown=max(0,t.unite_cooldown-1)
        self.plans.clear()
        if self.result:
            self.log.append(self.result)
        else:
            self.round += 1
        if self._movie_event is not None:self._movie_event['lure_after']=[c.lure for c in self.cogs]
        self._movie_event = None
        return self.log[start:]

    def begin_movie_event(self,kind,**details):
        if self._movie_event is not None:self._movie_event['lure_after']=[c.lure for c in self.cogs]
        self._movie_event=dict(kind=kind,health=[],misses=[],trap_before=[c.trap for c in self.cogs],lure_before=[c.lure for c in self.cogs],**details)
        self.movie_events.append(self._movie_event)

    def record_health(self,event):
        self.health_events.append(event)
        if self._movie_event is not None:self._movie_event['health'].append(event)

    def damage(self,index,amount,reason,bypass_layers=False):
        cog = self.cogs[index]
        previous=cog.hp
        cog.hp = max(0,cog.hp-amount)
        if previous!=cog.hp:self.record_health(('cog',index,cog.hp-previous))
        self.log.append(f'{cog.name}: −{amount} HP ({reason}).' + (' SUIT LAYER DESTROYED!' if not cog.alive and cog.version2 and not cog.skelecog and not bypass_layers else ' DEFEATED!' if not cog.alive else ''))
        if not cog.alive:
            cog.lure, cog.trap = 0,None
            if cog.version2 and not cog.skelecog and not bypass_layers:
                cog.skelecog=True;cog.hp=cog.maximum
                if self._movie_event is not None:self._movie_event.setdefault('layer_changes',[]).append(index)
                self.log.append(f'{cog.name}: suit destroyed; Skelecog layer has {cog.hp} HP.')

    def cog_phase(self):
        for event in self.cog_events():pass

    def cog_events(self):
        self.log.append('[Cogs]')
        for cog_index,cog in enumerate(self.cogs):
            living = [i for i,t in enumerate(self.toons) if t.alive]
            if not cog.alive or not living:
                continue
            if cog.remote:
                from support import remote_tick
                self.begin_movie_event('remote',cog=cog_index,actions=[])
                remote_tick(self,cog_index)
                yield self.finish_event()
                continue
            if cog.lure:
                self.begin_movie_event('lured',cog=cog_index,actions=[])
                cog.lure -= 1
                self.log.append(f'{cog.name} skips its attack (lured; {cog.lure} phases left).')
                yield self.finish_event()
                continue
            data=COG_CATALOG[cog.name]
            relative=max(0,min(4,cog.level-data['rank']))
            attacks=data['attacks']
            attack=self.rng.choices(attacks,weights=[a['weight'][relative] for a in attacks])[0]
            name,group,damages=attack['name'],attack['group'],attack['damage']
            targets = living if group else [self.rng.choice(living)]
            self.begin_movie_event('cog',cog=cog_index,name=name,targets=targets[:])
            for toon_index in targets:
                t=self.toons[toon_index]
                if self.roll(cog_accuracy(attack['accuracy'][relative],(cog.accuracy_down if getattr(self,'miss_scoped',False) else self.miss_rounds)>0)):
                    damage = damages[relative]
                    self._movie_event.setdefault('raw_toon_damage',{})[toon_index]=damage
                    previous=t.hp
                    t.hp = max(0,t.hp-damage)
                    if previous!=t.hp:self.record_health(('toon',toon_index,t.hp-previous))
                    self.log.append(f'{cog.name} uses {name} → {t.name}: −{damage} Laff.' + (' SAD!' if not t.alive else ''))
                else:
                    self._movie_event['misses'].append(toon_index)
                    self.log.append(f'{cog.name} uses {name} → {t.name}: dodged!')

            yield self.finish_event()
