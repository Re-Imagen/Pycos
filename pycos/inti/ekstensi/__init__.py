"""Registri eksplisit ekstensi inti; tidak memakai discovery atau exec."""
from __future__ import annotations

from importlib import import_module
from typing import Optional

URUTAN = ("kognisi", "organik", "gejala", "invensi", "kausal", "perencana", "pelindung", "ketidaktahuan", "persistensi")


def pasang(Naluri: type, *, nama: Optional[str] = None) -> None:
    """Pasang semua atau satu tahap eksplisit; facade menjaga urutan bootstrap."""
    if nama is not None and nama not in URUTAN:
        raise ValueError("ekstensi tidak dikenal: {!r}".format(nama))
    for tahap in URUTAN if nama is None else (nama,):
        modul = import_module("pycos.inti.ekstensi." + tahap)
        modul.pasang(Naluri)
