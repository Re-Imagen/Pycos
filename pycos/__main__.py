# -*- coding: utf-8 -*-
"""Ringkasan paket: jalankan `python -m pycos` dari direktori repositori.

Menampilkan versi, susunan subpaket, dan status sumber daya. Berguna untuk
memeriksa bahwa penataan berkas dan jalur impor konsisten pada instalasi
tertentu (checkout, `PYTHONPATH`, atau wheel).

Mode lain:

* `python -m pycos --periksa [--json]` — pemeriksaan kesehatan untuk CI,
  keluar dengan kode 0 (semua lulus) atau 1 (ada yang gagal).
* Penilaian keselarasan ujaran (dulu CLI `pycos.selaras`):

      python -m pycos --teks "aku senang banget!" --valensi 0.6 [--json]
      python -m pycos --persona-json persona.json --teks "..."
      python -m pycos --demo [--json]
      python -m pycos --teks "..." --leksikon leksikon.json
      python -m pycos --kalibrasi korpus.jsonl [--json]

  Kode keluar mode penilaian: 0 bila selaras; 1 bila sebagian, tidak selaras,
  atau melanggar pantangan; 2 bila tidak dapat dinilai atau argumen tidak sah.
"""
from __future__ import annotations

import importlib
import os
import sys
from typing import Any, Optional, Sequence, Tuple

from pycos import __all__ as API_PUBLIK, __version__
from pycos.dukungan.sumber import (NAMA_KORPUS, NAMA_LEKSIKON, jalur_korpus,
                                   jalur_leksikon)

SUBPAKET: Tuple[Tuple[str, str], ...] = (
    ("pycos.inti", "naluri (drive, kesadaran, presentasi, kawanan), persona"),
    ("pycos.refleksi", "nurani (refleksi + penilai keselarasan), ketidaktahuan"),
    ("pycos.memori", "jejak_prediksi"),
    ("pycos.mandiri", "organik, kognisi_lanjut"),
    ("pycos.bahasa", "tutur (mesin tutur + ciri linguistik)"),
    ("pycos.lingkungan", "dunia"),
    ("pycos.dukungan", "konstanta, patching, sumber, numerik, diagnostik, periksa, tolok, validasi_state, persistensi, parameter, batas_memori, leksikon"),
)

# Modul yang punya blok `if __name__ == "__main__"` (uji-diri atau demo).
DEMO_MANDIRI: Tuple[str, ...] = (
    "pycos.inti.naluri",
    "pycos.refleksi.nurani",
    "pycos.memori.jejak_prediksi",
    "pycos.mandiri.organik",
    "pycos.lingkungan.dunia",
)

# Flag yang mengalihkan ke mode penilaian keselarasan (bukan peta paket).
_MODE_SELARAS: Tuple[str, ...] = (
    "--teks", "--persona-json", "--valensi", "--gairah", "--ketidakpastian",
    "--leksikon", "--kalibrasi", "--korpus-pihak-ketiga", "--sumber-evaluasi", "--demo",
)

_KODE_STATUS = {"selaras": 0, "sebagian": 1, "tidak_selaras": 1,
                "melanggar_pantangan": 1, "tidak_dapat_dinilai": 2}

DEMO_SKENARIO: Tuple[str, ...] = (
    "aku senang banget hari ini! kamu hebat sekali!",
    "aku senang sekali, makasih ya!",
    "hmm mungkin aku sedikit lelah, sepertinya tidak bagus juga.",
    "saya mohon maaf, saya tidak dapat hadir hari ini.",
    "saya berkenan menerima undangan anda, terima kasih.",
    "saya mohon izin untuk pamit, silakan lanjutkan acara.",
)


def _mode_selaras_aktif(argv: Sequence[str]) -> bool:
    for a in argv:
        for flag in _MODE_SELARAS:
            if a == flag or a.startswith(flag + "="):
                return True
    return False


def _format_laporan(laporan: Any) -> str:
    baris = ["Persona: {} | status: {} | skor: {}".format(
        laporan.persona, laporan.status,
        "-" if laporan.skor is None else "{:.3f}".format(laporan.skor))]
    for d in laporan.dimensi:
        if d.skor is None:
            baris.append("  {:<9} tidak dinilai ({})".format(
                d.nama, d.catatan or "-"))
        else:
            baris.append("  {:<9} skor {:.3f}  obs {:+.3f}  target {:+.3f}".format(
                d.nama, d.skor, d.observasi, d.target))
    for s in laporan.saran:
        baris.append("  saran: " + s)
    return "\n".join(baris)


def _fmt(x: Any) -> str:
    return "-" if x is None else "{:.3f}".format(x)


def _format_kalibrasi(r: dict) -> str:
    baris = ["Jumlah contoh berlabel: {}".format(r["jumlah_contoh"]), "Fitur (prediksi vs label internal):"]
    for nama in ("polaritas", "formalitas"):
        f = r["fitur"][nama]
        if f["label"] == 0:
            baris.append("  {:<11} tidak ada label".format(nama))
            continue
        baris.append("  {:<11} label {:>3}  cakupan {}  akurasi {}  kappa {}".format(
            nama, f["label"], _fmt(f["cakupan"]), _fmt(f["akurasi"]), _fmt(f["kappa"])))
    s = r["selaras"]
    baris.append("Keselarasan:")
    if "keterangan" in s:
        baris.append("  " + s["keterangan"])
    else:
        baris.append("  pada ambang {:.2f}: akurasi {} ({} contoh)".format(
            s["ambang_default"], _fmt(s["akurasi_default"]), s["dinilai_default"]))
        baris.append("  ambang terbaik pada porsi latih ({:.0%}): {:.2f}, akurasi latih {}".format(
            s["porsi_latih"], s["ambang_latih"], _fmt(s["akurasi_latih"])))
        baris.append("  akurasi uji pada ambang itu: {} ({} contoh)".format(
            _fmt(s["akurasi_uji"]), s["dinilai_uji"]))
        if s["dinilai_uji"] < 30:
            baris.append("  peringatan: contoh uji kurang dari 30; angka ini belum stabil")
    eksternal = r.get("evaluasi_pihak_ketiga", {})
    baris.append("Evaluasi pihak ketiga: " + eksternal.get("status", "belum_tersedia"))
    if "jumlah_uji" in eksternal:
        baris.append("  uji {} | dinilai {} | akurasi terhadap konsensus {}".format(
            eksternal["jumlah_uji"], eksternal["dinilai"],
            _fmt(eksternal["akurasi_terhadap_konsensus"])))
        for pair in eksternal["antar_anotator"]:
            baris.append("  anotator {}: kappa {}, pasangan {}".format(
                "/".join(pair["anotator"]), _fmt(pair["kappa"]), pair["jumlah_pasangan"]))
    baris.append("  " + eksternal.get("peringatan", ""))
    return "\n".join(baris)


def jalankan_selaras(argv: Optional[Sequence[str]] = None) -> int:
    """Mode penilaian keselarasan ujaran (dulu `python -m pycos.selaras`)."""
    import argparse

    from pycos.bahasa.tutur import LeksikonCiri
    from pycos.inti.persona import PERSONA_CONTOH, Keadaan, Persona
    from pycos.refleksi.nurani import (laporan_kalibrasi, muat_korpus,
                                       nilai_selaras)

    ap = argparse.ArgumentParser(
        prog="python -m pycos", allow_abbrev=False,
        description="Nilai keselarasan persona, keadaan, dan ujaran "
                    "(atau cetak peta paket tanpa argumen).")
    ap.add_argument("--teks", help="ujaran yang akan dinilai")
    ap.add_argument("--persona-json", metavar="BERKAS",
                    help="profil persona dalam JSON (default: persona contoh)")
    ap.add_argument("--valensi", type=float, default=0.0, help="[-1, 1]")
    ap.add_argument("--gairah", type=float, default=0.5, help="[0, 1]")
    ap.add_argument("--ketidakpastian", type=float, default=0.3, help="[0, 1]")
    ap.add_argument("--leksikon", metavar="BERKAS",
                    help="leksikon ciri JSON kustom (default: leksikon ciri bawaan)")
    ap.add_argument("--kalibrasi", metavar="KORPUS",
                    help="ukur fitur dan keselarasan terhadap korpus JSONL berlabel")
    ap.add_argument("--korpus-pihak-ketiga", metavar="UJI_JSONL",
                    help="korpus held-out dengan id/anotasi; membutuhkan --kalibrasi")
    ap.add_argument("--sumber-evaluasi", metavar="SUMBER",
                    help="deklarasi provenance korpus pihak ketiga, belum diverifikasi")
    ap.add_argument("--demo", action="store_true", help="jalankan skenario drift")
    ap.add_argument("--json", action="store_true", help="keluaran JSON")
    args = ap.parse_args(list(argv) if argv is not None else None)
    try:
        leksikon = LeksikonCiri.dari_berkas(args.leksikon) if args.leksikon else None
        if (args.korpus_pihak_ketiga or args.sumber_evaluasi) and not args.kalibrasi:
            raise ValueError("evaluasi eksternal membutuhkan --kalibrasi sebagai data pengembangan")
        if args.kalibrasi:
            uji = muat_korpus(args.korpus_pihak_ketiga) if args.korpus_pihak_ketiga else None
            r = laporan_kalibrasi(muat_korpus(args.kalibrasi), leksikon,
                                  korpus_pihak_ketiga=uji, sumber_pihak_ketiga=args.sumber_evaluasi)
            if args.json:
                import json
                print(json.dumps(r, ensure_ascii=False, indent=2))
            else:
                print(_format_kalibrasi(r))
            return 0
        if args.persona_json:
            import json
            with open(args.persona_json, "r", encoding="utf-8") as f:
                persona = Persona.from_dict(json.load(f))
        else:
            persona = PERSONA_CONTOH
        keadaan = Keadaan(valensi=args.valensi, gairah=args.gairah,
                          ketidakpastian=args.ketidakpastian)
        if args.demo:
            return _jalankan_demo(persona, keadaan, args.json, leksikon)
        if args.teks is None:
            ap.error("--teks wajib kecuali --demo atau --kalibrasi")
        laporan = nilai_selaras(persona, keadaan, args.teks, leksikon)
    except (ValueError, TypeError, OSError) as galat:
        print("galat: {}".format(galat), file=sys.stderr)
        return 2
    if args.json:
        import json
        print(json.dumps(laporan.to_dict(), ensure_ascii=False, indent=2))
    else:
        print(_format_laporan(laporan))
    return _KODE_STATUS.get(laporan.status, 2)


def _jalankan_demo(persona: Any, keadaan: Any, as_json: bool,
                   leksikon: Optional[Any]) -> int:
    import json

    from pycos.refleksi.nurani import PelacakSelaras, nilai_selaras

    pelacak = PelacakSelaras(kapasitas=20, min_sampel=5, ambang_tren=0.02)
    laporan_list = []
    for teks in DEMO_SKENARIO:
        laporan = nilai_selaras(persona, keadaan, teks, leksikon)
        pelacak.catat(laporan)
        laporan_list.append((teks, laporan))
    tren = pelacak.tren()
    if as_json:
        print(json.dumps({
            "persona": persona.nama,
            "giliran": [{"teks": t, "laporan": l.to_dict()} for t, l in laporan_list],
            "tren": tren}, ensure_ascii=False, indent=2))
    else:
        for teks, laporan in laporan_list:
            print("> " + teks)
            print(_format_laporan(laporan))
        print("\nTren lintas giliran:")
        for nama, t in tren.items():
            print("  {:<12} sampel {:>2}  rerata {}  kemiringan {}  -> {}".format(
                nama, t["sampel"],
                "-" if t["rerata"] is None else "{:.3f}".format(t["rerata"]),
                "-" if t["kemiringan"] is None else "{:+.5f}".format(t["kemiringan"]),
                t["status"]))
    return 0


def cetak_peta() -> int:
    """Cetak peta paket dan status sumber daya; mengembalikan 0."""
    akar = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print("pycos {} — paket di {}".format(__version__, akar))
    print("Python {}".format(sys.version.split()[0]))
    print()
    print("Subpaket:")
    for nama, isi in SUBPAKET:
        print("  {:<16} {}".format(nama, isi))
    print()
    print("Sumber daya:")
    leksikon = jalur_leksikon()
    if os.path.isfile(leksikon):
        print("  {} — {} ({:,} byte)".format(
            NAMA_LEKSIKON, os.path.relpath(leksikon, akar),
            os.path.getsize(leksikon)))
        try:
            tutur = importlib.import_module("pycos.bahasa.tutur")
            info = tutur.TuturEngine(path=leksikon).info()
            print("  TuturEngine.info(): {}".format(info))
        except Exception as galat:  # pragma: no cover - diagnostik saja
            print("  TuturEngine gagal dimuat: {}".format(galat))
    else:
        print("  {} — TIDAK DITEMUKAN di {}".format(NAMA_LEKSIKON, leksikon))
    korpus = jalur_korpus()
    if os.path.isfile(korpus):
        print("  {} — {} ({:,} byte)".format(
            NAMA_KORPUS, os.path.relpath(korpus, akar),
            os.path.getsize(korpus)))
    else:
        print("  {} — TIDAK DITEMUKAN di {}".format(NAMA_KORPUS, korpus))
    print()
    print("Demo mandiri (modul yang memiliki blok `__main__`):")
    for modul in DEMO_MANDIRI:
        print("  python -m {:<31}# dari akar repo".format(modul))
        berkas = "pycos/" + modul[len("pycos."):].replace(".", "/") + ".py"
        print("  {:<41}# dari direktori mana pun".format("python3 " + berkas))
    print()
    print("Showcase inti terpisah: python -m pycos.inti.demo")
    print()
    print("Penilaian keselarasan (dulu `python -m pycos.selaras`):")
    print('  python -m pycos --teks "..." [--valensi V] [--gairah G] [--json]')
    print("  python -m pycos --demo [--json]")
    print("  python -m pycos --kalibrasi " + NAMA_KORPUS + " [--json]")
    print()
    print("Nama publik `from pycos import <nama>`:")
    print("  " + ", ".join(n for n in API_PUBLIK if n != "__version__"))
    return 0


def utama(argv: Optional[Sequence[str]] = None) -> int:
    """Cetak peta paket; atau jalankan `--periksa` / penilaian keselarasan.

    Mengembalikan 0 untuk peta paket; 0/1 untuk `--periksa`; 0/1/2 untuk mode
    penilaian keselarasan.
    """
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--periksa" not in argv and _mode_selaras_aktif(argv):
        return jalankan_selaras(argv)
    import argparse

    parser = argparse.ArgumentParser(
        prog="python -m pycos", allow_abbrev=False,
        description="Peta paket dan pemeriksaan kesehatan Pycos.",
        epilog='Penilaian: --teks "..." [--json]; demo: --demo; '
               'kalibrasi: --kalibrasi KORPUS. Gunakan --teks "..." --help '
               'untuk opsi penilaian lengkap.')
    parser.add_argument("--periksa", action="store_true", help="periksa kesehatan paket")
    parser.add_argument("--json", action="store_true", help="laporan --periksa sebagai JSON")
    args = parser.parse_args(argv)
    if args.periksa:
        from pycos.dukungan.periksa import main_periksa
        return main_periksa(as_json=args.json)
    if args.json:
        parser.error("--json membutuhkan --periksa atau mode penilaian")
    return cetak_peta()


if __name__ == "__main__":
    raise SystemExit(utama(sys.argv[1:]))
