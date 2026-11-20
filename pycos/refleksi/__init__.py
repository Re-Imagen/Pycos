# -*- coding: utf-8 -*-
"""pycos.refleksi — lapisan NURANI: refleksi, meta-plastisitas,
dan penilai keselarasan ujaran.

Berkas utama: :mod:`pycos.refleksi.nurani` (memori afektif, kalibrasi
berlapis, setpoint bergerak, interosepsi, persepsi, konflik/flow, relasi
sosial, dan state introspeksi). Subpaket ini tidak mengimpor `pycos.inti`:
objek `Naluri` selalu masuk lewat argumen (duck-typed), dan subpaket
`pycos.mandiri` dimuat opsional.
"""
from __future__ import annotations

from importlib import import_module
from typing import TYPE_CHECKING, Any, Dict, List

# Nama publik -> submodul tempat namanya didefinisikan.
_SUBMODUL: Dict[str, str] = {
    "CalibrationReport": "nurani",
    "ContohLabel": "nurani",
    "DimensiSkor": "nurani",
    "Laporan": "nurani",
    "NURANI_DEFAULTS": "nurani",
    "Nurani": "nurani",
    "PelacakSelaras": "nurani",
    "STATUS_PENGETAHUAN": "ketidaktahuan",
    "SIKAP_KETIDAKTAHUAN": "ketidaktahuan",
    "batas_pengetahuan": "ketidaktahuan",
    "kappa_cohen": "nurani",
    "laporan_kalibrasi": "nurani",
    "muat_korpus": "nurani",
    "nilai_selaras": "nurani",
    "sikap_ketidaktahuan": "ketidaktahuan",
    "ukur_fitur": "nurani",
    "ukur_selaras": "nurani",
}

__all__: List[str] = sorted(_SUBMODUL)

if TYPE_CHECKING:  # hanya untuk pemeriksa jenis, tidak dieksekusi
    from .ketidaktahuan import (STATUS_PENGETAHUAN, SIKAP_KETIDAKTAHUAN,
                                batas_pengetahuan, sikap_ketidaktahuan)
    from .nurani import (NURANI_DEFAULTS, CalibrationReport, ContohLabel,
                         DimensiSkor, Laporan, Nurani, PelacakSelaras,
                         kappa_cohen, laporan_kalibrasi, muat_korpus,
                         nilai_selaras, ukur_fitur, ukur_selaras)


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
