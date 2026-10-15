"""Use pre-action status: successful new Lure has already updated engine state."""
def fresh_targets(event,targets):
 before=event.get('lure_before',[])
 return [i for i in targets if i>=len(before) or not before[i]]
