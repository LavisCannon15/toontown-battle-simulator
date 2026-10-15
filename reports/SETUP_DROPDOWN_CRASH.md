# Setup dropdown crash

The launch log showed DirectOptionMenu.selectHighlightedIndex calling hidePopupMenu after its selection callback destroyed the widget. Cog/department/count callbacks synchronously rebuild setup_body, deleting the active dropdown. Panda3D then raises !is_empty() and exits the event loop.

Reproduced the same failure before the fix using tests/check_setup_dropdown.py and the actual selectHighlightedIndex handler (not just calling setup_cog directly). Added RebuildSafeOptionMenu: dismiss popup before invoking selection, with no widget access after the callback. PandaBattle.menu now uses it. Panda3D dependency files are unchanged.

Regression passes: Cog change, department change, another Cog change, Toon/Cog count changes, form selection, applying the setup, reopening and cancelling, and subsequent event-loop steps. Draft/apply behavior is retained.
