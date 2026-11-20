# -*- coding: utf-8 -*-
"""Batas buffer inti Naluri, dalam jumlah entri (bukan byte/RAM total).

Host boleh mengubah BATAS sebelum simulasi atau di antara tick. Perubahan
process-global tidak dipersistensi dan tidak thread-safe terhadap mutasi host.
Batas lokal legacy tetap merupakan ceiling tambahan. Nol berarti kosong.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

BATAS: Dict[str, int] = {
    "tick_history": 600,
    "delta_log": 512,
    "pred_pairs": 300,
    "prediction_log": 500,
    "event_buffer": 64,
    "emosi_log": 64,
    "persepsi_log": 64,
    "impact_cache": 512,
    "replay_log": 20000,
}


def batas(nama: str, lokal: Optional[int] = None) -> int:
    """Baca batas tervalidasi; tidak mengonversi bool/string/pecahan."""
    nilai = BATAS[nama]
    for label, v in ((nama, nilai), (nama + ".lokal", lokal)):
        if v is not None and (isinstance(v, bool) or not isinstance(v, int) or v < 0):
            raise ValueError("BATAS[{}] harus integer non-negatif".format(label))
    if nilai is None:
        raise ValueError("BATAS[{}] wajib integer non-negatif".format(nama))
    return nilai if lokal is None else min(nilai, lokal)


def pangkas(items: List[Any], nama: str, lokal: Optional[int] = None) -> None:
    """Pertahankan entri terbaru in-place, termasuk ketika batas nol."""
    cap = batas(nama, lokal)
    if len(items) > cap:
        del items[:len(items) - cap]
