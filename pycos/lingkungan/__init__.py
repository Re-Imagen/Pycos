# -*- coding: utf-8 -*-
"""pycos.lingkungan — lingkungan uji untuk interaksi NPC.

Berkas utama: :mod:`pycos.lingkungan.dunia`. Subpaket ini menyediakan dunia
berpetak yang deterministik: medan yang bisa/tidak bisa dilewati, objek yang
bisa diambil dan dipakai, bahaya yang memapar, cuaca, siklus jam, serta NPC
lain yang bisa disapa. Lingkungan memanggil API NPC secara *duck-typed*
(`choose_action`, `tick`, `reward_for`, `levels`), sehingga dunia dapat diuji
dengan stub maupun dengan `pycos.inti.naluri.Naluri` sungguhan; memori
opsional `JejakPrediksi` dapat ditautkan per badan NPC.

Subpaket ini tidak mengimpor lapisan Pycos lain pada tingkat atas, jadi aman
dipakai sendirian: `python -m pycos.lingkungan.dunia` atau
`python3 pycos/lingkungan/dunia.py` menjalankan demo di dalamnya.
"""
from __future__ import annotations

from importlib import import_module
from typing import TYPE_CHECKING, Any, Dict, List

# Nama publik -> submodul tempat namanya didefinisikan.
_SUBMODUL: Dict[str, str] = {
    "ARAH": "dunia",
    "Badan": "dunia",
    "EFEK_JENIS": "dunia",
    "JENIS_DAPAT_DIAMBIL": "dunia",
    "LEGENDA_MEDAN": "dunia",
    "Lingkungan": "dunia",
    "ObjekDunia": "dunia",
    "Peta": "dunia",
    "SIMBOL_OBJEK": "dunia",
    "demo": "dunia",
    "peta_contoh": "dunia",
}

__all__: List[str] = sorted(_SUBMODUL)

if TYPE_CHECKING:  # hanya untuk pemeriksa jenis, tidak dieksekusi
    from .dunia import (ARAH, EFEK_JENIS, JENIS_DAPAT_DIAMBIL, LEGENDA_MEDAN,
                        SIMBOL_OBJEK, Badan, Lingkungan, ObjekDunia, Peta,
                        demo, peta_contoh)


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
