#!/usr/bin/env python3
"""Shortcut — delegates to the proper CLI module.

Prefer:  python -m wissenssystem.cli.inspect [options]
"""
import runpy
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))
runpy.run_module("wissenssystem.cli.inspect", run_name="__main__", alter_sys=True)
