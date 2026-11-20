# -*- coding: utf-8 -*-
"""pycos.sumber_daya — berkas data yang ikut terpasang bersama paket.

Isi direktori ini hanyalah data: `leksikon_pycos.json` (lema ID/EN, kelas
gramatikal, lattice tipe semantik, kerangka predikat, dan aturan morfologi)
yang dimuat `pycos.bahasa.tutur`, serta `korpus_contoh.jsonl` (korpus contoh
berlabel untuk kalibrasi keselarasan; dilabeli penulis, bukan penilai
manusia). Nama-nama di bawah mengembalikan path
absolut supaya pemanggil tidak perlu menggabung-gabung string sendiri.

Berkas data disertakan dalam wheel melalui `package-data` pada
`pyproject.toml`; pada checkout, path yang sama menunjuk ke berkas di repo.
"""
from __future__ import annotations

from pycos.dukungan.sumber import (NAMA_KORPUS, NAMA_LEKSIKON, ada_sumber_daya,
                                   jalur_korpus, jalur_leksikon, sumber_daya)

LEKSIKON = jalur_leksikon()
"""Path leksikon bawaan paket (bisa tidak ada bila sumber daya dipindah)."""

KORPUS_CONTOH = jalur_korpus()
"""Path korpus contoh berlabel paket (JSON Lines, dilabeli penulis)."""

__all__ = ["KORPUS_CONTOH", "LEKSIKON", "NAMA_KORPUS", "NAMA_LEKSIKON",
           "ada_sumber_daya", "jalur_korpus", "jalur_leksikon", "sumber_daya"]
