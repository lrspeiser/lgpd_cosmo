# DO NOT USE THIS FILE. Kept only to preserve prior scaffolding for reference.
# See repository root `planck_plc.py` for the active adapter implementation.
#
# This file mirrors the earlier in-package scaffold and is intentionally not imported by
# any code. Retained to satisfy project policy about moving deprecated code to a clearly
# marked location instead of keeping duplicates.

import os
import logging

try:
    import clik  # Planck likelihood library
    _HAS_CLIK = True
except Exception:
    _HAS_CLIK = False

class PlanckPLCLike:
    """
    Deprecated scaffold. Use the root-level planck_plc.PlanckPLC instead.
    """
    def __init__(self, *args, **kwargs):
        raise RuntimeError(
            "Deprecated: Use the root-level planck_plc.PlanckPLC adapter instead."
        )
