# -*- coding: utf-8 -*-
"""Konstanta lintas lapisan; murni stdlib, tanpa bootstrap mesin."""
from __future__ import annotations
from typing import Tuple

__all__ = ["DRIVES"]

DRIVES: Tuple[str, ...] = (
    "energi", "keamanan", "keingintahuan", "penguasaan", "afiliasi", "koherensi",
)
