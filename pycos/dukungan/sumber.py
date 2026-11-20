# -*- coding: utf-8 -*-
"""sumber.py — resolusi sumber daya yang dibundel bersama paket Pycos.

Berkas data (leksikon tutur) tinggal di `pycos/sumber_daya/`. Aplikasi host
tidak perlu menebak di mana checkout atau wheel terpasang: helper di sini
mengembalikan path absolut berbasis `__file__` paket, dan menyusun daftar
kandidat yang dipakai lapisan integrasi (mis. `Presentasi.tutur_engine`).

Murni stdlib, tanpa impor modul Pycos lain, sehingga dapat dipakai dari
subpaket mana pun tanpa menambah dependensi.
"""
from __future__ import annotations

import os
from typing import List, Optional

__all__ = ["NAMA_LEKSIKON", "NAMA_KORPUS", "akar_paket", "sumber_daya",
           "jalur_leksikon", "kandidat_leksikon", "ada_sumber_daya",
           "jalur_korpus"]

NAMA_LEKSIKON = "leksikon_pycos.json"
NAMA_KORPUS = "korpus_contoh.jsonl"


def akar_paket() -> str:
    """Direktori paket `pycos` (induk seluruh subpaket)."""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def sumber_daya() -> str:
    """Direktori `pycos/sumber_daya` tempat berkas data paket disimpan."""
    return os.path.join(akar_paket(), "sumber_daya")


def jalur_leksikon(nama: str = NAMA_LEKSIKON) -> str:
    """Path leksikon bawaan dalam paket.

    Path dapat menunjuk ke berkas yang tidak ada (mis. sumber daya dipasang
    terpisah); periksa dengan :func:`ada_sumber_daya` sebelum memakainya.
    """
    return os.path.join(sumber_daya(), nama)


def jalur_korpus(nama: str = NAMA_KORPUS) -> str:
    """Path korpus contoh berlabel bawaan dalam paket (JSON Lines).

    Korpus ini dilabeli penulis, bukan penilai manusia; dipakai untuk demo dan
    regresi `laporan_kalibrasi`, bukan sebagai bukti akurasi.
    """
    return os.path.join(sumber_daya(), nama)


def ada_sumber_daya(jalur: Optional[str] = None) -> bool:
    """True bila berkas sumber daya tersedia dan terbaca sebagai berkas biasa."""
    return os.path.isfile(jalur if jalur is not None else jalur_leksikon())


def kandidat_leksikon(ekplisit: Optional[str] = None,
                      sekitar: Optional[str] = None) -> List[str]:
    """Kandidat path leksikon, terurut dari yang paling spesifik.

    Urutan: ``ekplisit`` (path yang diminta pemanggil) → ``sekitar`` (berkas
    di samping modul pemanggil, jalur lawas saat data diletakkan bersama
    source) → sumber daya paket → direktori kerja saat ini. Duplikat dibuang.
    """
    hasil: List[str] = []
    for calon in (ekplisit,
                  os.path.join(sekitar, NAMA_LEKSIKON) if sekitar else None,
                  jalur_leksikon(),
                  os.path.join(os.getcwd(), NAMA_LEKSIKON)):
        if calon and calon not in hasil:
            hasil.append(calon)
    return hasil
