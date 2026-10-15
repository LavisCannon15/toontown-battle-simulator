"""Option menu whose selection callback may replace its containing panel."""
from direct.gui.DirectGui import DirectOptionMenu


class RebuildSafeOptionMenu(DirectOptionMenu):
 def __init__(self,parent=None,**kwargs):
  super().__init__(parent,**kwargs)
  self.initialiseoptions(RebuildSafeOptionMenu)

 def selectHighlightedIndex(self,event=None):
  index=self.highlightedIndex
  if index is None:return
  # DirectOptionMenu normally calls set() before hiding. set() invokes the
  # callback, which may destroy this widget while rebuilding the setup panel.
  # Finish all popup work first and never access the widget after set().
  self.hidePopupMenu()
  self.set(index)
