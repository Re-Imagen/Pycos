# -*- coding: utf-8 -*-
"""pycos.dukungan — infrastruktur internal yang dipakai lintas lapisan.

Bukan API perilaku kognitif: berisi penjaga batas integrasi runtime
(:mod:`pycos.dukungan.patching`: `optional_module`, `install_method(s)`,
`wrap_method`, `PatchConflictError`) dan resolusi berkas data paket
(:mod:`pycos.dukungan.sumber`: `jalur_leksikon`, `kandidat_leksikon`).
Kedua modul murni stdlib dan tidak mengimpor subpaket perilaku, sehingga
selalu dapat dimuat lebih dulu.
"""
from __future__ import annotations

from importlib import import_module
from typing import TYPE_CHECKING, Any, Dict, List

# Nama publik -> submodul tempat namanya didefinisikan.
_SUBMODUL: Dict[str, str] = {
    "DRIVES": "konstanta",
    "NAMA_KORPUS": "sumber",
    "NAMA_LEKSIKON": "sumber",
    "PatchConflictError": "patching",
    "ada_sumber_daya": "sumber",
    "akar_paket": "sumber",
    "inventaris": "patching",
    "install_method": "patching",
    "install_methods": "patching",
    "jalur_korpus": "sumber",
    "jalur_leksikon": "sumber",
    "kandidat_leksikon": "sumber",
    "optional_module": "patching",
    "sumber_daya": "sumber",
    "wrap_method": "patching",
}

__all__: List[str] = sorted(_SUBMODUL)

if TYPE_CHECKING:  # hanya untuk pemeriksa jenis, tidak dieksekusi
    from .konstanta import DRIVES
    from .patching import (PatchConflictError, inventaris, install_method, install_methods,
                           optional_module, wrap_method)
    from .sumber import (NAMA_KORPUS, NAMA_LEKSIKON, akar_paket, ada_sumber_daya,
                         jalur_korpus, kandidat_leksikon, jalur_leksikon,
                         sumber_daya)


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
