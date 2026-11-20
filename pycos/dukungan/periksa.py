# -*- coding: utf-8 -*-
"""Pemeriksaan kesehatan untuk CI: `python -m pycos --periksa [--json]`.

Menjalankan rangkaian cek berurutan dan memberi kode keluar 0 bila semua lolos,
1 bila ada yang gagal. Setiap cek berdiri sendiri: kegagalan satu cek tidak
menghentikan cek lain, sehingga laporan memuat gambaran lengkap.

Cek yang dijalankan:

1. ``impor``          — semua modul inti dapat diimpor.
2. ``kontrak``        — `verifikasi_startup(drives_aktual=...)` tanpa pelanggaran.
3. ``leksikon``       — berkas leksikon ada, dapat dimuat, dan `tersedia()`.
4. ``smoke_naluri``   — NPC dibuat, 5 tick berjalan, `choose_action` memilih aksi,
   `reward_for` menghasilkan angka berhingga.
5. ``determinisme``   — dua NPC dengan seed sama menghasilkan keadaan identik
   setelah 20 tick (menjaga kontrak `rng_seed`).
6. ``validasi_input`` — input buruk (NaN, kunci asing, kandidat tanpa nama)
   benar-benar ditolak, bukan diterima diam-diam.
7. ``penilai``        — pipeline keselarasan ujaran (Persona × Keadaan × teks)
   menghasilkan `Laporan` yang lolos kontrak operasi `nilai_selaras`, dan
   `PelacakSelaras` menerima laporan itu.
8. ``korpus``         — korpus contoh dapat dimuat dan `laporan_kalibrasi`
   mengembalikan laporan lengkap (fitur + keselarasan).
9. ``validasi_batas`` — validator argumen batas `pycos.kontrak` (`angka`,
   `teks_wajib`, `hanya_kunci`) menolak nilai tak sah, bukan menerima diam-diam.
10. ``validasi_state`` — deserialisasi menolak level, urgensi, dan jam tidak sah.
11. ``validasi_event`` — event salah tipe, kunci, atau drive ditolak.
"""
from __future__ import annotations

import importlib
import json
import math
import os
from typing import Any, Callable, Dict, List, Optional, Tuple

__all__ = ["jalankan", "main_periksa"]

MODUL_INTI: Tuple[str, ...] = (
    "pycos.inti.naluri",
    "pycos.refleksi.nurani",
    "pycos.refleksi.ketidaktahuan",
    "pycos.memori.jejak_prediksi",
    "pycos.mandiri.organik",
    "pycos.mandiri.kognisi_lanjut",
    "pycos.bahasa.tutur",
    "pycos.lingkungan.dunia",
    "pycos.kontrak",
)


def _cek_impor() -> Optional[str]:
    gagal = []
    for nama in MODUL_INTI:
        try:
            importlib.import_module(nama)
        except Exception as galat:
            gagal.append("{} ({})".format(nama, type(galat).__name__))
    return "; ".join(gagal) if gagal else None


def _cek_kontrak() -> Optional[str]:
    from pycos.inti.naluri import DRIVES
    from pycos.kontrak import verifikasi_startup
    laporan = verifikasi_startup(drives_aktual=DRIVES)
    if laporan is None:
        return None
    return str(laporan.get("apa", laporan))


def _cek_leksikon() -> Optional[str]:
    from pycos.bahasa.tutur import TuturEngine
    from pycos.dukungan.sumber import jalur_leksikon
    path = jalur_leksikon()
    if not os.path.isfile(path):
        return "berkas tidak ditemukan: {}".format(path)
    eng = TuturEngine(path)
    if not eng.tersedia():
        return "TuturEngine.tersedia() = False untuk {}".format(path)
    return None


def _cek_smoke_naluri() -> Optional[str]:
    from pycos.inti.naluri import Naluri
    npc = Naluri(rng_seed=101, name="periksa")
    for _ in range(5):
        npc.tick(events=None)
    pilihan = npc.choose_action([{"name": "makan",
                                  "drive_effects": {"energi": 0.5}},
                                 {"name": "diam", "drive_effects": {}}])
    if not pilihan or pilihan.get("action") is None:
        return "choose_action tidak memilih aksi: {!r}".format(pilihan)
    r = npc.reward_for({"energi": 0.1})
    if not math.isfinite(float(r)):
        return "reward_for menghasilkan nilai tak berhingga: {!r}".format(r)
    return None


def _cek_determinisme() -> Optional[str]:
    from pycos.inti.naluri import Naluri
    a = Naluri(rng_seed=202, name="det-a")
    b = Naluri(rng_seed=202, name="det-b")
    for _ in range(20):
        a.tick(events=None)
        b.tick(events=None)
    if a.levels != b.levels:
        return "level berbeda untuk seed sama: {} vs {}".format(a.levels, b.levels)
    return None


def _cek_validasi_input() -> Optional[str]:
    from pycos.inti.naluri import Naluri
    yang_harus_ditolak: List[Tuple[str, Callable[[], Any]]] = [
        ("initial_levels NaN",
         lambda: Naluri(rng_seed=1, initial_levels={"keamanan": float("nan")})),
        ("initial_levels kunci asing",
         lambda: Naluri(rng_seed=1, initial_levels={"energy": 0.1})),
        ("delta NaN",
         lambda: Naluri(rng_seed=1).tick(
             events=[{"drive": "energi", "delta": float("nan")}])),
        ("kandidat tanpa nama",
         lambda: Naluri(rng_seed=1).choose_action([{"name": None}])),
    ]
    lolos = []
    for nama, fungsi in yang_harus_ditolak:
        try:
            fungsi()
        except (ValueError, TypeError):
            continue
        except Exception as galat:  # jenis galat tak terduga juga gagal
            lolos.append("{} (galat {})".format(nama, type(galat).__name__))
            continue
        lolos.append(nama)
    return ("input buruk diterima: " + ", ".join(lolos)) if lolos else None


def _cek_penilai() -> Optional[str]:
    from pycos.inti.persona import PERSONA_CONTOH, Keadaan
    from pycos.kontrak import kontrak_operasi
    from pycos.refleksi.nurani import PelacakSelaras, nilai_selaras

    keadaan = Keadaan(valensi=0.6, gairah=0.7, ketidakpastian=0.2)
    argumen: Dict[str, Any] = {"persona": PERSONA_CONTOH, "keadaan": keadaan,
               "teks": "aku senang banget hari ini!"}
    laporan = nilai_selaras(argumen["persona"], keadaan, argumen["teks"])
    for fase, args, hasil in (("masuk", argumen, None), ("keluar", {}, laporan)):
        pelanggaran = kontrak_operasi("nilai_selaras", fase, None, args, hasil,
                                      level=2)
        if pelanggaran is not None:
            return "kontrak nilai_selaras fase {} bocor: {}".format(
                fase, pelanggaran.get("apa"))
    pelacak = PelacakSelaras()
    pelacak.catat(laporan)
    if not isinstance(pelacak.tren(), dict):
        return "PelacakSelaras.tren() bukan mapping"
    return None


def _cek_korpus() -> Optional[str]:
    from pycos.dukungan.sumber import jalur_korpus
    from pycos.refleksi.nurani import laporan_kalibrasi, muat_korpus

    path = jalur_korpus()
    if not os.path.isfile(path):
        return "korpus contoh tidak ditemukan: {}".format(path)
    korpus = muat_korpus(path)
    if len(korpus) < 30:
        return "korpus contoh terlalu kecil: {} contoh".format(len(korpus))
    laporan = laporan_kalibrasi(korpus)
    if not isinstance(laporan, dict) or "fitur" not in laporan \
            or "selaras" not in laporan:
        return "laporan_kalibrasi tanpa kunci 'fitur'/'selaras'"
    return None


def _cek_validasi_batas() -> Optional[str]:
    from pycos.kontrak import angka, hanya_kunci, teks_wajib

    yang_harus_ditolak: List[Tuple[str, Callable[[], Any]]] = [
        ("angka NaN", lambda: angka(float("nan"), "x", 0.0, 1.0)),
        ("angka bool", lambda: angka(True, "x", 0.0, 1.0)),
        ("angka string", lambda: angka("0.5", "x", 0.0, 1.0)),
        ("angka di luar rentang", lambda: angka(2.0, "x", 0.0, 1.0)),
        ("teks kosong", lambda: teks_wajib("   ", "x")),
        ("kunci asing", lambda: hanya_kunci({"a": 1, "bogus": 2}, ("a",), "data")),
    ]
    lolos = []
    for nama, fungsi in yang_harus_ditolak:
        try:
            fungsi()
        except (ValueError, TypeError):
            continue
        except Exception as galat:  # jenis galat tak terduga juga gagal
            lolos.append("{} (galat {})".format(nama, type(galat).__name__))
            continue
        lolos.append(nama)
    return ("input batas diterima: " + ", ".join(lolos)) if lolos else None


def _cek_validasi_state() -> Optional[str]:
    from pycos.inti.naluri import Naluri
    for field, value in (("levels", {"energi": 99.0}),
                         ("urgency", {"energi": 1e9}), ("tick_count", -1)):
        try:
            Naluri.from_dict({field: value})
        except ValueError:
            continue
        return "state tidak sah diterima: " + field
    return None


def _cek_validasi_event() -> Optional[str]:
    from pycos.inti.naluri import Naluri
    n: Any = Naluri(params={"strict_events": True}, rng_seed=0)
    for events in ([{"drive": "energii"}], [None], [{"dleta": 1}]):
        try:
            n.apply_events(events)
        except ValueError:
            continue
        return "event tidak sah diterima"
    return None


CEK: Tuple[Tuple[str, Callable[[], Optional[str]]], ...] = (
    ("impor", _cek_impor),
    ("kontrak", _cek_kontrak),
    ("leksikon", _cek_leksikon),
    ("smoke_naluri", _cek_smoke_naluri),
    ("determinisme", _cek_determinisme),
    ("validasi_input", _cek_validasi_input),
    ("penilai", _cek_penilai),
    ("korpus", _cek_korpus),
    ("validasi_batas", _cek_validasi_batas),
    ("validasi_state", _cek_validasi_state),
    ("validasi_event", _cek_validasi_event),
)


def jalankan() -> List[Dict[str, Any]]:
    """Jalankan semua cek. Galat tak tertangkap menjadi status `GAGAL`."""
    hasil = []
    for nama, fungsi in CEK:
        try:
            masalah = fungsi()
        except Exception as galat:
            masalah = "{}: {}".format(type(galat).__name__, galat)
        hasil.append({"cek": nama, "ok": masalah is None,
                      "detail": masalah or ""})
    return hasil


def main_periksa(as_json: bool = False) -> int:
    hasil = jalankan()
    semua_ok = all(h["ok"] for h in hasil)
    from pycos.dukungan import diagnostik
    lap = diagnostik.laporan()
    from pycos.dukungan.patching import inventaris
    patches = inventaris()
    if as_json:
        print(json.dumps({"ok": semua_ok, "cek": hasil, "diagnostik": lap, "patch": patches}, ensure_ascii=False,
                         indent=2))
    else:
        print("Pemeriksaan kesehatan Pycos")
        for h in hasil:
            status = "LULUS" if h["ok"] else "GAGAL"
            extra = "" if h["ok"] else "  — " + h["detail"]
            print("  [{}] {}{}".format(status, h["cek"], extra))
        print("Inventaris patch runtime: {} metode".format(len(patches)))
        for baris in patches:
            print("  {}.{} [{}]: {}".format(
                baris["kelas"], baris["metode"], baris["jenis"],
                " -> ".join(baris["patch_ids"])))
        print("Diagnostik proses: {} catatan (bukan kegagalan cek otomatis)".format(lap["total"]))
        for entri in lap["terakhir"][-5:]:
            print("  {}: {}".format(entri["sumber"], entri["pesan"]))
        print("Hasil: {}".format("semua lulus" if semua_ok else "ada yang gagal"))
    return 0 if semua_ok else 1
