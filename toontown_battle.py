#!/usr/bin/env python3
"""Launch the Panda3D game, using the local runtime when needed."""
from pathlib import Path
import importlib.util
import os
import sys
ROOT=Path(__file__).resolve().parent
if importlib.util.find_spec('panda3d') is None:
    runtime=ROOT/'.venv/bin/python'
    if runtime.exists():
        os.execv(str(runtime),[str(runtime),str(Path(__file__).resolve()),*sys.argv[1:]])
    raise SystemExit('Install requirements.txt in a Python virtual environment, then launch again.')
from panda_battle import main
if __name__=='__main__':main()
