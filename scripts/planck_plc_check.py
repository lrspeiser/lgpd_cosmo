#!/usr/bin/env python3
"""
Sanity check for Planck PLC (clik) integration.

This script verifies that:
- clik can be imported from the current Python environment
- CLIK_PATH exists and is a directory

It does NOT evaluate a real likelihood yet. That requires local paths to
specific likelihood components and mapping C_ell arrays into the clik API.

See: docs/PLANCK_PLC_SETUP.md
"""
import os
import sys

ok = True
try:
    import clik  # type: ignore
    print("clik import: OK (", clik.__file__, ")")
except Exception as e:
    print("clik import: FAILED:", repr(e))
    ok = False

clik_path = os.environ.get("CLIK_PATH")
if clik_path and os.path.isdir(clik_path):
    print("CLIK_PATH:", clik_path)
else:
    print("CLIK_PATH not set or not a directory.")
    ok = False

sys.exit(0 if ok else 1)
