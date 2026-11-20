# -*- coding: utf-8 -*-
"""pycos/dukungan/numerik.py — aturan kanonik penjepitan angka Pycos.

Masalah yang diperbaiki modul ini: idiom ``max(lo, min(hi, x))`` yang tersebar
di puluhan lokasi mengubah ``NaN`` menjadi ``hi`` secara diam-diam, karena
setiap perbandingan dengan NaN bernilai ``False``. Akibatnya level drive yang
rusak (mis. dari delta NaN) berubah menjadi surplus maksimum ``+1.0`` tanpa
jejak apa pun.

Aturan tunggal di sini:

* nilai yang tidak dapat dibaca sebagai bilangan real, atau NaN, dijepit ke
  titik netral ``0.0`` (lalu dijepit ke rentang yang diminta);
* ``+inf``/``-inf`` dijepit ke batas rentang seperti biasa;
* ``bool`` diperlakukan sebagai non-numerik.

Peta pemakaian aturan ini:

* delegasi langsung — ``pycos.inti.naluri._kclip`` dan
  ``pycos.memori.jejak_prediksi._clip`` hanyalah alias tipis ke :func:`jepit`;
* salinan yang disengaja (agar modul dapat disalin/dipakai sendirian, kontrak
  yang dijaga tes) — ``pycos.mandiri.organik._kclip``,
  ``pycos.mandiri.kognisi_lanjut.jepit_drive``, dan
  ``pycos.lingkungan.dunia._potong`` (aturan sama) serta
  ``pycos.bahasa.tutur._clip`` (varian: NaN/tak-numerik menjadi ``lo``, karena
  perannya nilai-pengganti, bukan netral);
* varian ketat — ``persona._jepit`` memvalidasi angka berhingga lebih dulu,
  lalu mendelegasikan penjepitan; ``ketidaktahuan._clip`` memakai default
  pemanggil untuk input rusak/non-finite, lalu ``jepit_01`` untuk angka valid.
  Seluruh helper tersebut dicakup tes R4.3.

Murni stdlib; tidak mengimpor modul Pycos lain.
"""
from __future__ import annotations

import math
from typing import Any

__all__ = ["jepit", "jepit_drive", "jepit_01", "float_hingga"]


def jepit(x: Any, lo: float = -1.0, hi: float = 1.0) -> float:
    """Jepit ``x`` ke ``[lo, hi]``; NaN atau tak-numerik menjadi ``0.0``."""
    if isinstance(x, bool):
        v = 0.0
    else:
        try:
            v = float(x)
        except (TypeError, ValueError, OverflowError):
            v = 0.0
    if v != v:  # NaN: netral, bukan batas atas
        v = 0.0
    if v < lo:
        return float(lo)
    if v > hi:
        return float(hi)
    return v


def jepit_drive(x: Any) -> float:
    """Jepit ke rentang nominal drive ``[-1, 1]``."""
    return jepit(x, -1.0, 1.0)


def jepit_01(x: Any) -> float:
    """Jepit ke rentang probabilitas/keyakinan ``[0, 1]``."""
    return jepit(x, 0.0, 1.0)


def float_hingga(x: Any, nama: str) -> float:
    """Konversi ketat ke float berhingga; galat jelas bila tidak bisa.

    Dipakai di batas masuk (delta event, level awal) agar nilai rusak ditolak
    di tempatnya, bukan diam-diam menjadi angka lain di tengah simulasi.
    """
    if isinstance(x, bool):
        raise ValueError("{} harus angka, bukan bool".format(nama))
    try:
        v = float(x)
    except (TypeError, ValueError, OverflowError):
        raise ValueError("{} harus angka, dapat {!r}".format(nama, x)) from None
    if not math.isfinite(v):
        raise ValueError("{} harus berhingga, dapat {!r}".format(nama, x))
    return v
