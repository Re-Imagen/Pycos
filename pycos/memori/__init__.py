# -*- coding: utf-8 -*-
"""pycos.memori — lapisan JEJAK: memori episodik dan prediksi hasil.

Berkas utama: :mod:`pycos.memori.jejak_prediksi`. Modul menyimpan episode
stimulus–aksi–hasil, mengambilnya kembali lewat cue, lalu menggabungkan
prior `Naluri`/`Nurani` dengan bukti lingkungan yang bobotnya dibatasi.
Integrasi dengan lapisan inti bersifat opsional dan duck-typed.
"""
from __future__ import annotations

from importlib import import_module
from typing import TYPE_CHECKING, Any, Dict, List

# Nama publik -> submodul tempat namanya didefinisikan.
_SUBMODUL: Dict[str, str] = {
    "JejakPrediksi": "jejak_prediksi",
}

__all__: List[str] = sorted(_SUBMODUL)

if TYPE_CHECKING:  # hanya untuk pemeriksa jenis, tidak dieksekusi
    from .jejak_prediksi import JejakPrediksi


def __getattr__(nama: str) -> Any:
    """Muat submodul hanya saat namanya pertama diakses (PEP 562)."""
    asal = _SUBMODUL.get(nama)
    if asal is None:
        raise AttributeError(
            "paket {!r} tidak punya atribut {!r}".format(__name__, nama))
    nilai = getattr(import_module("{}.{}".format(__name__, asal)), nama)
    globals()[nama] = nilai          # cache: resolusi sekali per proses
    return nilai


def __dir__() -> List[str]:
    return sorted(set(globals()) | set(_SUBMODUL))
