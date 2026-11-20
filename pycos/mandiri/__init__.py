# -*- coding: utf-8 -*-
"""pycos.mandiri — primitif state dan mekanisme kognitif tambahan.

Dua modul yang berdiri sendiri (tidak mengimpor lapisan Pycos lain):

* :mod:`pycos.mandiri.organik` — sifat state (slot kosong, luka domain,
  batas identitas, waktu heterogen, penolakan tutur, apersepsi, lapisan
  paralel, tubuh, residu, intrusi, detak fraksional, vacancy, gejala,
  invensi, model kausal, perencana) dalam wadah `Organik`;
* :mod:`pycos.mandiri.kognisi_lanjut` — lima mekanisme komputasional
  (`EversiTD`, Boltzmann, `MesinKepercayaan`, `GrafAsosiasi`, `ProsesOU`).

Hook ke `Naluri`/`Nurani`/`JejakPrediksi` dipasang dari lapisan pemanggil,
bukan dari sini, sehingga kedua modul aman disalin atau dipakai terpisah.
"""
from __future__ import annotations

from importlib import import_module
from typing import TYPE_CHECKING, Any, Dict, List

# Nama publik -> submodul tempat namanya didefinisikan.
_SUBMODUL: Dict[str, str] = {
    "Apersepsi": "organik",
    "BatasIdentitas": "organik",
    "DetakInternal": "organik",
    "EMOSI_NODE": "kognisi_lanjut",
    "EversiTD": "kognisi_lanjut",
    "Gejala": "organik",
    "GejalaMurni": "organik",
    "GrafAsosiasi": "kognisi_lanjut",
    "Intrusi": "organik",
    "Invensi": "organik",
    "KALIMAT_ADA_SESUATU": "organik",
    "KALIMAT_TAK_BERNAMA": "organik",
    "KOSONG": "organik",
    "KategoriProto": "organik",
    "KognisiLanjut": "kognisi_lanjut",
    "LapisanParalel": "organik",
    "LukaDomain": "organik",
    "MesinKepercayaan": "kognisi_lanjut",
    "ModelKausal": "organik",
    "Organik": "organik",
    "PROPERTI_TERLARANG": "organik",
    "PenolakanTutur": "organik",
    "Perencana": "organik",
    "ProsesOU": "kognisi_lanjut",
    "Residu": "organik",
    "TAK_BERLAKU": "organik",
    "TERISI": "organik",
    "TopologiSlot": "organik",
    "TubuhSumber": "organik",
    "Vacancy": "organik",
    "WaktuHeterogen": "organik",
    "boltzmann_pilih": "kognisi_lanjut",
    "suhu_mental": "kognisi_lanjut",
}

__all__: List[str] = sorted(_SUBMODUL)

if TYPE_CHECKING:  # hanya untuk pemeriksa jenis, tidak dieksekusi
    from .kognisi_lanjut import (EMOSI_NODE, GrafAsosiasi, KognisiLanjut,
                                 MesinKepercayaan, ProsesOU, EversiTD,
                                 boltzmann_pilih, suhu_mental)
    from .organik import (KALIMAT_ADA_SESUATU, KALIMAT_TAK_BERNAMA, KOSONG,
                          PROPERTI_TERLARANG, TAK_BERLAKU, TERISI, Apersepsi,
                          BatasIdentitas, DetakInternal, Gejala, GejalaMurni,
                          Invensi, Intrusi, KategoriProto, LapisanParalel,
                          LukaDomain, ModelKausal, Organik, PenolakanTutur,
                          Perencana, Residu, TubuhSumber, TopologiSlot, Vacancy,
                          WaktuHeterogen)


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
