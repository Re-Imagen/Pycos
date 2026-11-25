# -*- coding: utf-8 -*-
"""Tes penataan paket: susunan direktori, keberadaan `__init__.py`, jalur impor.

Struktur yang dijaga:

    pycos/__init__.py     — API publik malas (PEP 562)
    pycos/__main__.py     — ringkasan paket + penilaian keselarasan: `python -m pycos`
    pycos/kontrak.py      — kontrak antarlapisan + pemeriksaan argumen batas
    pycos/dukungan/       — patching.py, sumber.py, numerik.py, diagnostik.py,
                            tolok.py, periksa.py
    pycos/inti/           — naluri.py (mesin), persona.py (Persona & Keadaan)
    pycos/refleksi/       — nurani.py (termasuk penilai/pelacak/kalibrasi
                            keselarasan), ketidaktahuan.py
    pycos/memori/         — jejak_prediksi.py
    pycos/mandiri/       — organik.py, kognisi_lanjut.py
    pycos/bahasa/         — tutur.py (mesin tutur L0–L3), teks.py (fondasi
                            teks bersama: tokenizer, morfologi, negasi, G1),
                            keadaan.py (ujaran keadaan H8: kegagalan,
                            penahanan, apersepsi, ujian)
    pycos/lingkungan/     — dunia.py
    pycos/sumber_daya/    — leksikon_pycos.json, korpus_contoh.jsonl

Tes ini tidak menguji perilaku kognitif; ia memastikan tidak ada modul yang
tertinggal di luar paket, tidak ada gaya impor lama yang lolos, dan setiap
nama yang dijanjikan `__all__` benar-benar dapat diimpor.
"""
from __future__ import annotations

import ast
import os
import subprocess
import sys
import unittest

AKAR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if AKAR not in sys.path:
    sys.path.insert(0, AKAR)

import pycos  # noqa: E402

PAKET = os.path.join(AKAR, "pycos")

# Subpaket -> modul di dalamnya (tanpa ekstensi .py).
PETA = {
    "dukungan": ["konstanta", "patching", "sumber", "numerik", "diagnostik", "tolok", "periksa", "validasi_state", "persistensi", "parameter", "batas_memori", "leksikon"],
    "inti": ["naluri", "persona", "ritual", "reputasi", "kawanan", "_konfigurasi", "kesadaran", "presentasi", "keadaan", "mesin"],
    "inti/ekstensi": ["kognisi", "organik", "gejala", "invensi", "kausal", "perencana", "pelindung", "ketidaktahuan", "persistensi"],
    "inti/demo": ["skenario", "__main__"],
    "refleksi": ["nurani", "ketidaktahuan"],
    "memori": ["jejak_prediksi"],
    "mandiri": ["organik", "kognisi_lanjut"],
    "bahasa": ["tutur", "teks", "keadaan"],
    "lingkungan": ["dunia"],
}

# Nama modul saat masih satu direktori; tidak boleh ada lagi di akar repo.
NAMA_LAMA = ("naluri", "nurani", "jejak_prediksi", "organik",
             "kognisi_lanjut", "tutur", "patching")


def berbeda(harus, ada):
    """Selisih dua himpunan jalur, digabung agar pesan gagal informatif."""
    return (harus - ada) | (ada - harus)


def baca_ast(sub, nama):
    jalur = os.path.join(PAKET, sub, nama + ".py")
    with open(jalur, "r", encoding="utf-8") as f:
        return jalur, ast.parse(f.read(), filename=jalur)


class SusunanBerkasTest(unittest.TestCase):
    def test_setiap_subpaket_dan_modul_ada(self):
        for sub, modul in PETA.items():
            direktori = os.path.join(PAKET, sub)
            with self.subTest(subpaket=sub):
                self.assertTrue(os.path.isdir(direktori))
                self.assertTrue(
                    os.path.isfile(os.path.join(direktori, "__init__.py")),
                    "pycos/{} tanpa __init__.py".format(sub))
            for nama in modul:
                with self.subTest(modul="pycos.{}".format(nama)):
                    self.assertTrue(
                        os.path.isfile(os.path.join(direktori, nama + ".py")))

    def test_modul_lama_tidak_lagi_di_akar(self):
        for nama in NAMA_LAMA:
            with self.subTest(modul=nama):
                self.assertFalse(
                    os.path.exists(os.path.join(AKAR, nama + ".py")),
                    "{}.py masih ada di akar repo".format(nama))

    def test_daftar_subpaket_tepat(self):
        ada = sorted(
            nama for nama in os.listdir(PAKET)
            if os.path.isdir(os.path.join(PAKET, nama)) and nama != "__pycache__")
        self.assertEqual(sorted([n for n in PETA if "/" not in n] + ["sumber_daya"]), ada)

    def test_himpunan_berkas_persis_sesuai_peta(self):
        """Tidak ada .py tambahan di luar peta, dan tidak ada yang hilang."""
        harus = {"pycos/__init__.py", "pycos/__main__.py", "pycos/kontrak.py", "pycos/konektor.py"}
        for sub, modul in PETA.items():
            harus.add("pycos/{}/__init__.py".format(sub))
            harus.update("pycos/{}/{}.py".format(sub, nama) for nama in modul)
        harus.add("pycos/sumber_daya/__init__.py")

        ada = set()
        for direktori, _, nama_berkas in os.walk(PAKET):
            for nama in nama_berkas:
                if nama.endswith(".py"):
                    ada.add(os.path.relpath(os.path.join(direktori, nama), AKAR)
                            .replace(os.sep, "/"))
        self.assertEqual(berbeda(harus, ada), set(),
                         "struktur berkas menyimpang dari peta")

    def test_sumber_daya_hanya_data_dan_init(self):
        direktori = os.path.join(PAKET, "sumber_daya")
        isi = sorted(n for n in os.listdir(direktori) if n != "__pycache__")
        self.assertEqual(["__init__.py", "impak_tambahan.json", "korpus_contoh.jsonl",
                          "leksikon_pycos.json"], isi)


class JalurImporTest(unittest.TestCase):
    def test_nama_lama_gagal_sebagai_modul_datar(self):
        for nama in NAMA_LAMA:
            with self.subTest(modul=nama):
                with self.assertRaises(ImportError):
                    __import__(nama)

    def test_tidak_ada_impor_datar_atau_lintas_subpaket_relatif(self):
        """Impor datar ke modul lama dilarang; impor relatif hanya intra-paket."""
        milik = {nama: sub for sub, modul in PETA.items() for nama in modul}
        for sub, modul in PETA.items():
            for nama in modul + ["__init__"]:
                jalur_p = os.path.join(PAKET, sub, nama + ".py")
                if not os.path.isfile(jalur_p):
                    continue
                jalur, pohon = baca_ast(sub, nama)
                label = os.path.relpath(jalur, AKAR)
                with self.subTest(berkas=label):
                    for simpul in ast.walk(pohon):
                        if isinstance(simpul, ast.ImportFrom):
                            asal = (simpul.module or "").split(".")[0]
                            if simpul.level:      # `from .x import ...`
                                if asal in milik:
                                    self.assertEqual(
                                        sub, milik[asal],
                                        "{} memakai `from .{} import` lintas "
                                        "subpaket".format(label, asal))
                            else:                 # `from x import ...`
                                self.assertNotIn(
                                    asal, set(NAMA_LAMA),
                                    "{} memakai impor datar {!r}".format(
                                        label, simpul.module))
                        elif isinstance(simpul, ast.Import):
                            for alias in simpul.names:
                                self.assertNotIn(
                                    alias.name.split(".")[0], set(NAMA_LAMA),
                                    "{} memakai `import {}`".format(
                                        label, alias.name))

    def test_semua_submodul_terimpor_dengan_nama_baru(self):
        import importlib

        for sub, modul in PETA.items():
            for nama in modul:
                penuh = "pycos.{}.{}".format(sub.replace("/", "."), nama)
                with self.subTest(modul=penuh):
                    m = importlib.import_module(penuh)
                    self.assertEqual(penuh, m.__name__)
                    self.assertTrue(m.__file__.replace(os.sep, "/").endswith(
                        "pycos/{}/{}.py".format(sub, nama)))

    def test_tidak_ada_sisa_package___package__(self):
        for sub, modul in PETA.items():
            for nama in modul:
                jalur = os.path.join(PAKET, sub, nama + ".py")
                with self.subTest(berkas="pycos/{}.py".format(nama)):
                    with open(jalur, "r", encoding="utf-8") as f:
                        self.assertNotIn("package=__package__", f.read())

    def test_optional_module_menyelesaikan_nama_bertitik(self):
        from pycos.dukungan.patching import optional_module

        for nama in ("pycos.mandiri.organik", "pycos.mandiri.kognisi_lanjut"):
            with self.subTest(modul=nama):
                m = optional_module(nama)
                self.assertIsNotNone(m, "{} tidak resolve".format(nama))
                self.assertEqual(nama, m.__name__)
        # nama lama harus gagal dengan tenang (None), bukan melempar
        self.assertIsNone(optional_module("organik"))

    def test_lingkungan_tanpa_impor_lapisan_pycos_di_tingkat_atas(self):
        """`pycos.lingkungan.dunia` harus bisa disalin/dipakai sendirian."""
        jalur, pohon = baca_ast("lingkungan", "dunia")
        for simpul in pohon.body:          # hanya tingkat atas modul
            if isinstance(simpul, ast.ImportFrom):
                penuh = "pycos." + (simpul.module or "") if simpul.level \
                    else (simpul.module or "")
                self.assertFalse(penuh.startswith("pycos"),
                                 "impor {} di tingkat atas".format(penuh))
            elif isinstance(simpul, ast.Import):
                for alias in simpul.names:
                    self.assertFalse(alias.name.startswith("pycos"),
                                     "impor {} di tingkat atas".format(alias.name))

    def test_inti_tidak_mengimpor_lapisan_atas_secara_wajib(self):
        """Impor refleksi/memori/bahasa di `naluri` harus berada dalam try/except."""
        jalur, pohon = baca_ast("inti", "naluri")
        opsional = {"pycos.refleksi.nurani", "pycos.memori.jejak_prediksi",
                    "pycos.bahasa.tutur"}
        dalam_try = set()
        for simpul in ast.walk(pohon):
            if isinstance(simpul, ast.Try):
                for anak in ast.walk(simpul):
                    if isinstance(anak, ast.ImportFrom):
                        penuh = "pycos." + anak.module if anak.level else anak.module
                        if penuh in opsional:
                            dalam_try.add(penuh)
        self.assertEqual(opsional, dalam_try,
                         "lapisan opsional wajib ada di dalam try/except "
                         "agar `pycos.inti` tetap muat tanpa mereka")



class GayaBerkasTesTest(unittest.TestCase):
    """Direktori `tests` harus konsisten dengan source: impor paket penuh.

    Berkas tes pernah memakai impor datar (`from naluri import ...`) yang
    hanya bekerja bila direktori modul ada di `sys.path`; impor seperti itu
    gagal di `python -m unittest discover` dan berbeda dari berkas tes lain.
    Kelas ini menjaga agar gaya lama tidak kembali.
    """

    def berkas_tes(self):
        direktori = os.path.join(AKAR, "tests")
        return sorted(os.path.join(direktori, n)
                      for n in os.listdir(direktori)
                      if n.startswith("test_") and n.endswith(".py"))

    def test_tidak_ada_impor_datar_atau_relatif(self):
        """Impor datar ke nama modul di dalam paket (mis. `from naluri import`)
        dan impor relatif tidak boleh ada di berkas tes."""
        milik = {nama for modul in PETA.values() for nama in modul}
        for jalur in self.berkas_tes():
            with open(jalur, "r", encoding="utf-8") as f:
                pohon = ast.parse(f.read(), filename=jalur)
            label = os.path.relpath(jalur, AKAR)
            for simpul in ast.walk(pohon):
                if isinstance(simpul, ast.Import):
                    for alias in simpul.names:
                        self.assertNotIn(
                            alias.name.split(".")[0], milik,
                            "{} memakai `import {}`".format(label, alias.name))
                elif isinstance(simpul, ast.ImportFrom):
                    self.assertFalse(
                        simpul.level,
                        "{} memakai impor relatif `from {}`".format(
                            label, "." * simpul.level + (simpul.module or "")))
                    asal = (simpul.module or "").split(".")[0]
                    self.assertNotIn(
                        asal, milik,
                        "{} memakai impor datar {!r}".format(
                            label, simpul.module))

    def test_kepala_berkas_tes_seragam(self):
        for jalur in self.berkas_tes():
            with open(jalur, "r", encoding="utf-8") as f:
                isi = f.read()
            label = os.path.relpath(jalur, AKAR)
            with self.subTest(berkas=label):
                self.assertTrue(isi.startswith("# -*- coding: utf-8 -*-"),
                                "{} tanpa deklarasi encoding".format(label))
                pohon = ast.parse(isi, filename=jalur)
                self.assertTrue(ast.get_docstring(pohon),
                                "{} tanpa docstring modul".format(label))
                self.assertIn("from __future__ import annotations", isi)
                self.assertIn("if AKAR not in sys.path", isi)


class ApiPublikTest(unittest.TestCase):
    def test_nama_top_level_terselesaikan(self):
        for nama in pycos.__all__:
            with self.subTest(nama=nama):
                if nama == "TAK_BERLAKU":
                    from pycos.mandiri.organik import TAK_BERLAKU
                    self.assertIsNone(TAK_BERLAKU)
                    self.assertIs(getattr(pycos, nama), TAK_BERLAKU)
                else:
                    self.assertIsNotNone(getattr(pycos, nama))

    def test_impor_pycos_bersifat_malas(self):
        kode = ("import sys; import pycos; "
                "print(sorted(m for m in sys.modules if m.startswith('pycos')))")
        hasil = subprocess.run([sys.executable, "-c", kode], cwd=AKAR,
                               capture_output=True, text=True)
        self.assertEqual(0, hasil.returncode, hasil.stderr)
        termuat = ast.literal_eval(hasil.stdout.strip())
        self.assertEqual(["pycos"], termuat,
                         "`import pycos` menarik modul besar; API harus malas")
        self.assertIn("pycos.inti.naluri", str(pycos.Naluri.__module__))

    def test_nama_tidak_ada_memberi_attributeerror(self):
        with self.assertRaises(AttributeError) as ctx:
            pycos.TidakAdaBegini
        self.assertIn("TidakAdaBegini", str(ctx.exception))

    def test_dir_paket_memuat_api(self):
        d = dir(pycos)
        for nama in ("Naluri", "Nurani", "JejakPrediksi", "Organik",
                     "TuturEngine", "__version__"):
            with self.subTest(nama=nama):
                self.assertIn(nama, d)

    def test_subpaket_mengekspor_api_terdokumentasi(self):
        from pycos import (bahasa, dukungan, inti, lingkungan, mandiri,
                           memori, refleksi)

        harapan = {
            inti: ["Naluri", "Kesadaran", "Presentasi", "KawananNPC",
                   "Reputasi", "DRIVES", "buat_npc",
                   "Persona", "Keadaan", "PERSONA_CONTOH"],
            refleksi: ["Nurani", "CalibrationReport", "NURANI_DEFAULTS",
                       "DimensiSkor", "Laporan", "PelacakSelaras",
                       "nilai_selaras", "muat_korpus", "laporan_kalibrasi"],
            memori: ["JejakPrediksi"],
            mandiri: ["Organik", "KognisiLanjut", "TopologiSlot",
                      "ModelKausal", "Perencana", "EversiTD", "ProsesOU"],
            lingkungan: ["ARAH", "Badan", "Lingkungan", "ObjekDunia", "Peta",
                         "demo", "peta_contoh"],
            bahasa: ["TuturEngine", "GenContext", "SASPAnalyzer", "sa_sp",
                     "konteks_dari_presentasi",
                     "FiturTutur", "LeksikonCiri", "analisis_teks", "token_dari"],
            dukungan: ["optional_module", "install_method", "install_methods",
                       "wrap_method", "PatchConflictError", "jalur_leksikon",
                       "kandidat_leksikon", "jalur_korpus"],
        }
        for paket, nama in harapan.items():
            for atribut in nama:
                with self.subTest(paket=paket.__name__, atribut=atribut):
                    self.assertTrue(hasattr(paket, atribut))
                    self.assertIn(atribut, paket.__all__)

    def test___all___subpaket_dapat_diimpor(self):
        from pycos import (bahasa, dukungan, inti, lingkungan, mandiri,
                           memori, refleksi)

        for paket in (inti, refleksi, memori, mandiri, bahasa, lingkungan,
                      dukungan):
            with self.subTest(paket=paket.__name__):
                self.assertTrue(getattr(paket, "__all__", None))
                for nama in paket.__all__:
                    self.assertTrue(hasattr(paket, nama),
                                    "{} tanpa {}".format(paket.__name__, nama))

    def test___main__mencetak_ringkasan(self):
        import contextlib
        import io

        from pycos.__main__ import utama

        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            kode = utama([])
        keluaran = buffer.getvalue()
        self.assertEqual(0, kode)
        for penanda in ("pycos ", "Subpaket:", "pycos.inti", "pycos.bahasa",
                        "leksikon_pycos.json", "python -m pycos.inti.naluri"):
            with self.subTest(penanda=penanda):
                self.assertIn(penanda, keluaran)


if __name__ == "__main__":
    unittest.main()
