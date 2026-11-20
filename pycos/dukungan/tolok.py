# -*- coding: utf-8 -*-
"""Tolok kinerja ringan: `python -m pycos.dukungan.tolok [--json] [--ulang N]`.

Mengukur enam jalur yang paling sering dipanggil saat Pycos dipakai sebagai
pustaka simulasi:

* ``naluri_tick``     — ms per ``Naluri.tick()`` (fisika drive + proses inti).
* ``choose_action``   — ms per pemilihan aksi dengan tiga kandidat.
* ``rank_actions``    — ms per peringkingan aksi di ``JejakPrediksi``.
* ``predict_2000_terbatas`` — predict dengan 2.000 episode, batas 256 kandidat.
* ``to_dict_simpan`` — snapshot ringkas dan ukuran JSON penuh/simpan.
* ``leksikon``        — muat leksikon dingin (cache kosong) vs hangat (cache terisi).

Tujuannya membandingkan angka antar-perubahan dan antar-mesin, bukan menjadi
jaminan kinerja. Keluaran teks untuk manusia; `--json` untuk CI atau arsip.
Kode keluar 0 bila semua tolok selesai, 1 bila ada yang melempar galat.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from typing import Any, Callable, Dict, List, Optional

__all__ = ["jalankan_semua", "main"]


def _ukur(nama: str, iterasi: int, fungsi: Callable[[], Any]) -> Dict[str, Any]:
    """Jalankan `fungsi` `iterasi` kali dan kembalikan ringkasan waktunya."""
    try:
        t0 = time.perf_counter()
        for _ in range(iterasi):
            fungsi()
        total = time.perf_counter() - t0
    except Exception as galat:  # laporkan per tolok; jangan batalkan semuanya
        return {"nama": nama, "ok": False,
                "galat": "{}: {}".format(type(galat).__name__, galat)}
    return {"nama": nama, "ok": True, "iterasi": iterasi,
            "total_s": round(total, 6),
            "per_iterasi_ms": round(1000.0 * total / max(1, iterasi), 4)}


def _tolok_naluri_tick(ulang: int) -> Dict[str, Any]:
    from pycos.inti.naluri import Naluri
    npc = Naluri(rng_seed=7, name="tolok")
    return _ukur("naluri_tick", 200 * ulang, lambda: npc.tick(events=None))


def _tolok_choose_action(ulang: int) -> Dict[str, Any]:
    from pycos.inti.naluri import Naluri
    npc = Naluri(rng_seed=8, name="tolok-aksi")
    kandidat = [{"name": "makan", "drive_effects": {"energi": 0.6}},
                {"name": "tidur", "drive_effects": {"energi": 0.2}},
                {"name": "diam", "drive_effects": {}}]
    return _ukur("choose_action", 300 * ulang,
                 lambda: npc.choose_action(kandidat))


def _tolok_rank_actions(ulang: int) -> Dict[str, Any]:
    from pycos.memori.jejak_prediksi import JejakPrediksi
    jejak = JejakPrediksi(rng_seed=9)
    kandidat = [{"name": "makan"}, {"name": "tidur"}, {"name": "diam"}]
    return _ukur("rank_actions", 100 * ulang,
                 lambda: jejak.rank_actions("lapar", kandidat))


def _tolok_to_dict_simpan(ulang: int) -> Dict[str, Any]:
    from pycos.inti.naluri import Naluri
    npc = Naluri(rng_seed=7, name="tolok-simpan")
    for _ in range(50):
        npc.tick()
    hasil = _ukur("to_dict_simpan", 50 * ulang,
                  lambda: npc.to_dict(profil="simpan"))
    hasil["byte_penuh"] = len(npc.to_json().encode("utf-8"))
    hasil["byte_simpan"] = len(npc.to_json(profil="simpan").encode("utf-8"))
    from pycos.inti.naluri import DEFAULTS
    params = {k: True for k, v in DEFAULTS.items()
              if k.startswith("enable_") and isinstance(v, bool)}
    aktif: Any = Naluri(params=params, rng_seed=7, name="tolok-lapisan")
    aktif.enable_eversi()
    aktif.enable_latent_drift()
    aktif.enable_asosiasi()
    aktif.enable_kausal()
    aktif.enable_invensi()
    for _ in range(10):
        aktif.tick()
    hasil["fixture_lapisan_aktif"] = {
        "flag_enable": len(params), "tick": 10,
        "byte_penuh": len(aktif.to_json().encode("utf-8")),
        "byte_simpan": len(aktif.to_json(profil="simpan").encode("utf-8")),
        "byte_minimal": len(aktif.to_json(profil="minimal").encode("utf-8")),
    }
    return hasil


def _tolok_predict_2000(ulang: int) -> Dict[str, Any]:
    from pycos.memori.jejak_prediksi import JejakPrediksi
    jejak = JejakPrediksi(capacity=2000, half_life_ticks=0,
                         memory_retention_half_life=0, rng_seed=7)
    for i in range(2000):
        jejak.record_experience("api lorong kejadian {}".format(i), "lari",
                                {"impact": -.2}, tick=i, sync_nurani=False)
    hasil = _ukur("predict_2000_terbatas", 30 * ulang,
                  lambda: jejak.predict("api lorong", tick=2000, max_candidates=256))
    hasil["episodes"] = jejak.size
    hasil["budget"] = jejak.performance_report()["last_budget"]
    hasil["target_ms"] = 3.0
    hasil["target_tercapai"] = hasil.get("per_iterasi_ms", float("inf")) < 3.0
    hasil["alternatif_128"] = _ukur(
        "predict_2000_batas128", 30 * ulang,
        lambda: jejak.predict("api lorong", tick=2000, max_candidates=128))
    return hasil


def _tolok_leksikon(ulang: int, jalur: Optional[str]) -> Dict[str, Any]:
    from pycos.bahasa.tutur import TuturEngine, kosongkan_cache_leksikon
    from pycos.dukungan.sumber import jalur_leksikon
    path = jalur or jalur_leksikon()
    if not os.path.isfile(path):
        return {"nama": "leksikon", "ok": False,
                "galat": "berkas leksikon tidak ditemukan: {}".format(path)}
    try:
        kosongkan_cache_leksikon()
        t0 = time.perf_counter()
        TuturEngine(path)
        dingin = time.perf_counter() - t0
        hangat = _ukur("leksikon_hangat", 20 * ulang, lambda: TuturEngine(path))
    except Exception as galat:
        return {"nama": "leksikon", "ok": False,
                "galat": "{}: {}".format(type(galat).__name__, galat)}
    return {"nama": "leksikon", "ok": hangat["ok"],
            "muat_dingin_ms": round(1000.0 * dingin, 3),
            "muat_hangat_per_ms": hangat.get("per_iterasi_ms"),
            "galat": hangat.get("galat"),
            "iterasi": hangat.get("iterasi")}


def jalankan_semua(ulang: int = 1, jalur_leksikon_opsional: Optional[str] = None
                   ) -> List[Dict[str, Any]]:
    """Jalankan semua tolok dan kembalikan daftar hasil (satu dict per tolok)."""
    ulang = max(1, int(ulang))
    return [
        _tolok_naluri_tick(ulang),
        _tolok_choose_action(ulang),
        _tolok_rank_actions(ulang),
        _tolok_to_dict_simpan(ulang),
        _tolok_predict_2000(ulang),
        _tolok_leksikon(ulang, jalur_leksikon_opsional),
    ]


def _format_teks(hasil: List[Dict[str, Any]]) -> str:
    baris = ["Tolok kinerja Pycos (waktu per iterasi, lebih kecil lebih baik)"]
    for h in hasil:
        if not h.get("ok"):
            baris.append("  {:<16} GAGAL — {}".format(h["nama"], h.get("galat")))
        elif h["nama"] == "leksikon":
            baris.append("  {:<16} muat dingin {:.3f} ms | muat hangat {} ms/muat"
                         .format(h["nama"], h["muat_dingin_ms"],
                                 h["muat_hangat_per_ms"]))
        else:
            baris.append("  {:<16} {:.4f} ms/iterasi ({} iterasi, {:.3f} s)".format(
                h["nama"], h["per_iterasi_ms"], h["iterasi"], h["total_s"]))
    return "\n".join(baris)


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(prog="python -m pycos.dukungan.tolok",
                                 description="Tolok kinerja ringan Pycos.")
    ap.add_argument("--json", action="store_true", help="keluaran JSON")
    ap.add_argument("--ulang", type=int, default=1,
                    help="pengali jumlah iterasi (default 1)")
    ap.add_argument("--leksikon", default=None,
                    help="jalur leksikon kustom (default: sumber daya bawaan)")
    args = ap.parse_args(argv)
    if args.ulang < 1:
        ap.error("--ulang harus >= 1")
    hasil = jalankan_semua(args.ulang, args.leksikon)
    semua_ok = all(h.get("ok") for h in hasil)
    if args.json:
        print(json.dumps({"ok": semua_ok, "tolok": hasil}, ensure_ascii=False,
                         indent=2))
    else:
        print(_format_teks(hasil))
    return 0 if semua_ok else 1


if __name__ == "__main__":
    sys.exit(main())
