# -*- coding: utf-8 -*-
"""pycos/dukungan/diagnostik.py — catatan kegagalan yang sebelumnya tersenyap.

Beberapa jalur Pycos memilih bertahan (mengembalikan nilai bawaan) alih-alih
melempar galat, karena itu perilaku yang disengaja untuk host. Masalahnya,
sebelum modul ini kegagalan semacam itu tidak meninggalkan jejak sama sekali:
`future_simulation` pernah diam-diam mengabaikan semua kandidat aksi, dan
engine tutur yang gagal dimuat hanya menyebabkan jalur template dipakai tanpa
pemberitahuan.

Modul ini menyediakan satu tempat pencatatan terbatas (ring buffer, aman
untuk banyak thread) yang dapat diperiksa host atau `python -m pycos --periksa`.
Pencatatan tidak pernah melempar galat dan tidak mengubah perilaku fungsi
yang mencatat.

Murni stdlib.
"""
from __future__ import annotations

from copy import deepcopy
import threading
import time
from collections import deque
from typing import Any, Deque, Dict

__all__ = ["catat", "laporan", "kosongkan", "KAPASITAS"]

KAPASITAS = 200

_LOCK = threading.Lock()
_CATATAN: Deque[Dict[str, Any]] = deque(maxlen=KAPASITAS)
_TOTAL: Dict[str, int] = {}


def catat(sumber: str, pesan: str, **detail: Any) -> None:
    """Catat satu kejadian tersenyap. Tidak pernah melempar galat."""
    try:
        entri: Dict[str, Any] = {"waktu": round(time.time(), 3), "sumber": str(sumber),
                 "pesan": str(pesan)[:300]}
        if detail:
            entri["detail"] = {str(k): str(v)[:120] for k, v in detail.items()}
        with _LOCK:
            _CATATAN.append(entri)
            _TOTAL[entri["sumber"]] = _TOTAL.get(entri["sumber"], 0) + 1
    except Exception:  # pencatatan tidak boleh menjatuhkan jalur utama
        return


def laporan() -> Dict[str, Any]:
    """Snapshot terisolasi; perubahan laporan tidak memutasi catatan internal."""
    with _LOCK:
        return {"total": sum(_TOTAL.values()),
                "per_sumber": dict(sorted(_TOTAL.items())),
                "terakhir": deepcopy(list(_CATATAN)),
                "kapasitas": KAPASITAS}


def kosongkan() -> None:
    with _LOCK:
        _CATATAN.clear()
        _TOTAL.clear()
