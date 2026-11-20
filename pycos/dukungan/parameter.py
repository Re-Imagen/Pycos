# -*- coding: utf-8 -*-
"""Registry parameter Naluri; pemeriksaan ketat bersifat opt-in di 0.x.

Tipe dideklarasikan dari default runtime yang telah dirakit semua lapisan.
Rentang hanya ditetapkan untuk parameter dengan domain eksplisit di sini;
None berarti belum ada batas numerik spesifik, bukan jaminan semua nilai
berguna. Semua angka tetap harus finite. Tidak mengubah mapping input.
"""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Dict, Optional, Tuple

from pycos.kontrak import angka
from pycos.inti.naluri import DEFAULTS

_RENTANG = {
    "decay_per_tick": (0.0, None),
    "urgency_alpha": (0.0, 1.0),
    "calibration_alpha": (0.0, 1.0),
    "scale_alpha": (0.0, 1.0),
    "eligibility_lambda": (0.0, 1.0),
    "max_goals": (0.0, None),
    "context_capacity": (0.0, None),
}

# tanggal deklarasi, tipe, rentang inklusif opsional
PARAM_SPEC: Dict[str, Tuple[str, type, Optional[Tuple[Any, Any]]]] = {
    key: ("2026-11-08", type(value), _RENTANG.get(key))
    for key, value in DEFAULTS.items()
}


def periksa_params(params: Any) -> None:
    """Tolak kunci asing, tipe salah, angka non-finite, dan rentang terdaftar."""
    if params is None:
        return
    if not isinstance(params, Mapping):
        raise ValueError("params harus mapping")
    for key, value in params.items():
        label = "params[{!r}]".format(key)
        if key not in PARAM_SPEC:
            raise ValueError(label + " tidak dikenal")
        _, tipe, rentang = PARAM_SPEC[key]
        if tipe is float:
            angka(value, label)
        elif type(value) is not tipe:
            raise ValueError(label + " harus " + tipe.__name__)
        if tipe is int:
            angka(value, label)
        if rentang is not None:
            angka(value, label, *rentang)
