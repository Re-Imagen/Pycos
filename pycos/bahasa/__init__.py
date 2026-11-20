# -*- coding: utf-8 -*-
"""pycos.bahasa — mesin tutur generatif, penganalisis ujaran,
dan ciri linguistik dangkal.

Berkas utama: :mod:`pycos.bahasa.tutur`. `TuturEngine` menjalankan empat
tahap (L0 rencana konten → L1 bentuk semantik → L2 leksikon → L3 morfologi)
dengan sumber daya dari `pycos/sumber_daya/leksikon_pycos.json`, sedangkan
`SASPAnalyzer` memisahkan semantik literal dari hipotesis pragmatik.

Subpaket ini tidak mengimpor lapisan Pycos lain: konteks NPC masuk lewat
`konteks_dari_presentasi` secara duck-typed. Tanpa leksikon pada path yang
diminta, `TuturEngine.tersedia()` bernilai False dan pemanggil jatuh ke jalur
template lama.
"""
from __future__ import annotations

from importlib import import_module
from typing import TYPE_CHECKING, Any, Dict, List

# Nama publik -> submodul tempat namanya didefinisikan.
_SUBMODUL: Dict[str, str] = {
    "Arg": "tutur",
    "FiturTutur": "tutur",
    "GenContext": "tutur",
    "L0": "tutur",
    "L1": "tutur",
    "L2": "tutur",
    "L3": "tutur",
    "LEKSIKON_CIRI_BAWAAN": "tutur",
    "Lattice": "tutur",
    "Leksikon": "tutur",
    "LeksikonCiri": "tutur",
    "Node": "tutur",
    "Orkestrator": "tutur",
    "SASPAnalyzer": "tutur",
    "Tutur": "tutur",
    "TuturEngine": "tutur",
    "JejakLinguistik": "teks",
    "Token": "teks",
    "analisis_ujaran": "teks",
    "cakupan_negasi": "teks",
    "deteksi_bahasa": "teks",
    "ekstrak_entitas": "teks",
    "ekstrak_topik": "teks",
    "jejak_pembentukan": "teks",
    "jenis_kalimat": "teks",
    "jenis_pertanyaan": "teks",
    "kandidat_dasar": "teks",
    "kemiripan": "teks",
    "koreksi_ejaan": "teks",
    "normalisasi_teks": "teks",
    "normalisasi_token": "teks",
    "pecah_kalimat": "teks",
    "periksa_gramatika": "teks",
    "potong_batas_kata": "teks",
    "stem": "teks",
    "tindak_tutur_skor": "teks",
    "tokenisasi": "teks",
    "urai_subjek_predikat": "teks",
    "analisis_teks": "tutur",
    "konteks_dari_presentasi": "tutur",
    "sa_sp": "tutur",
    "sa_sp_literal": "tutur",
    "sa_sp_pragmatik": "tutur",
    "token_dari": "tutur",
}

__all__: List[str] = sorted(_SUBMODUL)

if TYPE_CHECKING:  # hanya untuk pemeriksa jenis, tidak dieksekusi
    from .tutur import (Arg, FiturTutur, GenContext, L0, L1, L2, L3,
                        LEKSIKON_CIRI_BAWAAN, Lattice, Leksikon, LeksikonCiri,
                        Node, Orkestrator, SASPAnalyzer, Tutur, TuturEngine,
                        analisis_teks, konteks_dari_presentasi, sa_sp,
                        sa_sp_literal, sa_sp_pragmatik, token_dari)
    from .teks import (Token, JejakLinguistik, analisis_ujaran,
                     deteksi_bahasa, cakupan_negasi, ekstrak_entitas,
                     ekstrak_topik, jenis_kalimat, jenis_pertanyaan,
                     jejak_pembentukan, kandidat_dasar, koreksi_ejaan,
                     kemiripan, normalisasi_teks, normalisasi_token,
                     pecah_kalimat, periksa_gramatika, potong_batas_kata,
                     stem, tindak_tutur_skor, tokenisasi,
                     urai_subjek_predikat)


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
