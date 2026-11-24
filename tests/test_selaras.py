# -*- coding: utf-8 -*-
"""Tes subsistem keselarasan ujaran: persona, keadaan, fitur linguistik, penilai,
pelacak drift, dan CLI.

Sejak penyatuan subsistem Selaras, programnya berada di lapisan yang sesuai:
`Persona`/`Keadaan` di `pycos.inti.naluri`, ciri linguistik di
`pycos.bahasa.tutur`, penilai/pelacak/kalibrasi di `pycos.refleksi.nurani`,
dan CLI di `python -m pycos`."""
from __future__ import annotations

import ast
import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from types import SimpleNamespace

AKAR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if AKAR not in sys.path:
    sys.path.insert(0, AKAR)

from pycos.__main__ import utama as cli  # noqa: E402
from pycos.bahasa.tutur import analisis_teks  # noqa: E402
from pycos.inti.naluri import Keadaan, Persona  # noqa: E402
from pycos.refleksi.nurani import (  # noqa: E402
    DimensiSkor,
    Laporan,
    PelacakSelaras,
    nilai_selaras,
)

SANTAI_HANGAT = Persona(nama="Rani", sifat={"hangat": 0.8, "ekspresif": 0.6, "ragu": 0.3},
                        register="santai", pantangan=("sialan", "bodoh"))
SELARAS_CONTOH = "aku senang banget hari ini! kamu hebat sekali!"


class PersonaTest(unittest.TestCase):
    def test_roundtrip_dan_normalisasi_pantangan(self):
        p = Persona(nama="  Rani ", sifat={"hangat": 1}, register="santai",
                    pantangan=(" Sialan  Tahu ", "sialan tahu"))
        self.assertEqual("Rani", p.nama)
        self.assertEqual(("sialan tahu",), p.pantangan)  # dedup dan huruf kecil
        self.assertEqual(p, Persona.from_dict(p.to_dict()))

    def test_validasi_ketat(self):
        for kwargs in ({"nama": ""}, {"nama": "A", "sifat": {"lucu": 0.5}},
                       {"nama": "A", "sifat": {"hangat": 1.5}},
                       {"nama": "A", "sifat": {"hangat": True}},
                       {"nama": "A", "register": "kasar"},
                       {"nama": "A", "pantangan": "satu-string"}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                Persona(**kwargs)

    def test_from_dict_menolak_kunci_asing(self):
        with self.assertRaisesRegex(ValueError, "tak dikenal"):
            Persona.from_dict({"nama": "A", "warna": "biru"})


class KeadaanTest(unittest.TestCase):
    def test_validasi_dan_roundtrip(self):
        k = Keadaan(valensi=-0.4, gairah=0.9, ketidakpastian=0.1)
        self.assertEqual(k, Keadaan.from_dict(k.to_dict()))
        for kwargs in ({"valensi": float("nan")}, {"gairah": True},
                       {"ketidakpastian": "0.2"}, {"valensi": 2}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                Keadaan(**kwargs)

    def test_dari_mood_duck_typing_dan_pemetaan_arousal(self):
        k = Keadaan.dari_mood(SimpleNamespace(valence=-2.0, arousal=-0.5))
        self.assertEqual(-1.0, k.valensi)      # dijepit
        self.assertEqual(0.25, k.gairah)       # arousal [-1,1] -> [0,1]
        k2 = Keadaan.dari_mood(SimpleNamespace(valence=0.4, arousal=0.9))
        self.assertEqual(0.9, k2.gairah)

    def test_dari_mood_atribut_hilang_tidak_jadi_nol(self):
        with self.assertRaises(AttributeError):
            Keadaan.dari_mood(SimpleNamespace(valence=0.1))

    def test_dari_mood_non_finite_ditolak(self):
        for nilai in (float("nan"), float("inf"), float("-inf")):
            with self.subTest(nilai=nilai), self.assertRaises(ValueError):
                Keadaan.dari_mood(SimpleNamespace(valence=0.1, arousal=nilai))


class FiturTest(unittest.TestCase):
    def test_polaritas_formalitas_intensitas_keraguan(self):
        f = analisis_teks("Saya senang sekali, mohon maaf! Mungkin benar-benar bagus.")
        self.assertEqual(1.0, f.polaritas())            # senang, bagus; tanpa negatif
        self.assertEqual(1.0, f.formalitas())           # saya, mohon
        self.assertGreater(f.intensitas(), 0.5)         # seru + penguat
        self.assertGreater(f.keraguan(), 0.0)           # mungkin

    def test_negasi_membalik_polaritas(self):
        self.assertEqual(-1.0, analisis_teks("aku tidak senang").polaritas())
        self.assertEqual(-1.0, analisis_teks("bukan yang bagus").polaritas())
        self.assertEqual(1.0, analisis_teks("aku senang sekali").polaritas())
        # jendela negasi tiga token berbatas klausa: "bukan hal yang bagus" dibalik
        # (sebelumnya jendela dua token gagal menangkapnya)
        self.assertEqual(-1.0, analisis_teks("bukan hal yang bagus").polaritas())
        # negasi di luar jendela tidak membalik polaritas
        self.assertEqual(1.0, analisis_teks("tidak tahu kenapa aku senang").polaritas())

    def test_tanpa_bukti_bernilai_none(self):
        f = analisis_teks("Meja itu di sana.")
        self.assertIsNone(f.polaritas())
        self.assertIsNone(f.formalitas())
        self.assertEqual(0.0, f.keraguan())             # token ada, tanpa pelunak
        self.assertIsNone(analisis_teks("   ").intensitas())

    def test_huruf_kapital_dan_tanda_hubung(self):
        self.assertGreater(analisis_teks("TOLONG CEPAT").intensitas(), 0.4)
        self.assertEqual(1, analisis_teks("benar-benar").penguat)

    def test_bukan_string_ditolak(self):
        with self.assertRaises(TypeError):
            analisis_teks(None)


class PenilaiTest(unittest.TestCase):
    def test_teks_selaras_dengan_persona_dan_keadaan(self):
        laporan = nilai_selaras(SANTAI_HANGAT, Keadaan(valensi=0.6, gairah=0.6),
                                SELARAS_CONTOH)
        self.assertEqual("selaras", laporan.status, laporan.to_dict())
        self.assertGreaterEqual(laporan.skor, 0.75)
        self.assertEqual((), laporan.pelanggaran)

    def test_target_campuran_persona_dan_keadaan(self):
        # hangat=1.0 -> sifat valensi 1.0; keadaan 0.0; bobot 0.5 -> target 0.5
        p = Persona(nama="P", sifat={"hangat": 1.0})
        laporan = nilai_selaras(p, Keadaan(valensi=0.0), "aku senang")
        valensi = next(d for d in laporan.dimensi if d.nama == "valensi")
        self.assertEqual(0.5, valensi.target)

    def test_register_formal_pada_persona_santai_diberi_skor_rendah(self):
        laporan = nilai_selaras(SANTAI_HANGAT, Keadaan(),
                                "saya mohon izin, anda silakan lanjut.")
        register = next(d for d in laporan.dimensi if d.nama == "register")
        self.assertLess(register.skor, 0.3)
        self.assertTrue(any("lebih santai" in s for s in laporan.saran))

    def test_pantangan_membatasi_skor_dan_status(self):
        laporan = nilai_selaras(SANTAI_HANGAT, Keadaan(valensi=0.6),
                                "kamu itu sialan, aku senang!")
        self.assertEqual(("sialan",), laporan.pelanggaran)
        self.assertEqual("melanggar_pantangan", laporan.status)
        self.assertLessEqual(laporan.skor, 0.4)
        self.assertIn("hapus kata pantangan: sialan", laporan.saran)

    def test_pantangan_cocok_setelah_stemming_g2(self):
        # G2 (Tahap 3): pantangan dicocokkan setelah stemming, sehingga
        # infleksi/klitik yang berbagi lema tetap tertangkap — "bodohnya"
        # adalah "bodoh". Token yang berbeda lemas tetap tidak cocok.
        laporan = nilai_selaras(SANTAI_HANGAT, Keadaan(), "bodohnya orang itu")
        self.assertEqual(("bodoh",), laporan.pelanggaran)
        laporan = nilai_selaras(SANTAI_HANGAT, Keadaan(), "bodoamat orang itu")
        self.assertEqual((), laporan.pelanggaran)

    def test_persona_netral_tidak_menilai_register(self):
        laporan = nilai_selaras(Persona(nama="N"), Keadaan(), "saya mohon maaf")
        register = next(d for d in laporan.dimensi if d.nama == "register")
        self.assertIsNone(register.skor)
        self.assertIn("netral", register.catatan)

    def test_teks_kosong_tidak_dapat_dinilai(self):
        laporan = nilai_selaras(SANTAI_HANGAT, Keadaan(), "  ?? ")
        self.assertEqual("tidak_dapat_dinilai", laporan.status)
        self.assertIsNone(laporan.skor)

    def test_deterministik_dan_tanpa_mutasi_input(self):
        k = Keadaan(valensi=0.2, gairah=0.4)
        a = nilai_selaras(SANTAI_HANGAT, k, "hmm mungkin aku lelah")
        b = nilai_selaras(SANTAI_HANGAT, k, "hmm mungkin aku lelah")
        self.assertEqual(a.to_dict(), b.to_dict())
        self.assertEqual(0.2, k.valensi)
        self.assertIsInstance(a, Laporan)


class PelacakTest(unittest.TestCase):
    def _laporan(self, skor, dim=None):
        dims = tuple(DimensiSkor(n, 0.0, 0.0, v, "") for n, v in (dim or {}).items())
        return Laporan("P", dims, (), skor, "sebagian", ())

    def test_tren_menurun_dan_meningkat(self):
        pelacak = PelacakSelaras(kapasitas=10, min_sampel=5, ambang_tren=0.01)
        for skor in (0.9, 0.8, 0.7, 0.6, 0.5, 0.4):
            pelacak.catat(self._laporan(skor))
        self.assertEqual("menurun", pelacak.tren()["keseluruhan"]["status"])
        pelacak.kosongkan()
        for skor in (0.4, 0.5, 0.6, 0.7, 0.8):
            pelacak.catat(self._laporan(skor))
        self.assertEqual("meningkat", pelacak.tren()["keseluruhan"]["status"])

    def test_stabil_dan_belum_cukup(self):
        pelacak = PelacakSelaras(kapasitas=10, min_sampel=5)
        for _ in range(3):
            pelacak.catat(self._laporan(0.7))
        self.assertEqual("belum_cukup", pelacak.tren()["keseluruhan"]["status"])
        for _ in range(3):
            pelacak.catat(self._laporan(0.7))
        self.assertEqual("stabil", pelacak.tren()["keseluruhan"]["status"])

    def test_memori_terbatas_dan_dimensi_none_dilewati(self):
        pelacak = PelacakSelaras(kapasitas=6, min_sampel=2)
        for i in range(20):
            pelacak.catat(self._laporan(0.5, {"gairah": 0.5}))
        self.assertEqual(6, len(pelacak))
        laporan = Laporan("P", (DimensiSkor("register", None, None, None, ""),),
                          (), None, "tidak_dapat_dinilai", ())
        pelacak.catat(laporan)
        self.assertNotIn("register", pelacak.tren())  # tidak ada nol palsu

    def test_validasi_konstruktor_dan_tipe(self):
        for kwargs in ({"kapasitas": 1}, {"min_sampel": 1},
                       {"kapasitas": 4, "min_sampel": 9}, {"ambang_tren": -1}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                PelacakSelaras(**kwargs)
        with self.assertRaises(TypeError):
            PelacakSelaras().catat({"skor": 1})


class CliTest(unittest.TestCase):
    def _jalankan(self, argv):
        keluaran = io.StringIO()
        with contextlib.redirect_stdout(keluaran):
            kode = cli(argv)
        return kode, keluaran.getvalue()

    def test_kode_keluar_sesuai_status(self):
        kode, _ = self._jalankan(["--teks", SELARAS_CONTOH, "--valensi", "0.6",
                                  "--gairah", "0.6"])
        self.assertEqual(0, kode)
        kode, _ = self._jalankan(["--teks", "kamu sialan!"])
        self.assertEqual(1, kode)
        kode, _ = self._jalankan(["--teks", "   ?? "])
        self.assertEqual(2, kode)

    def test_input_tidak_sah_kode_2(self):
        with contextlib.redirect_stderr(io.StringIO()):
            kode, _ = self._jalankan(["--teks", "halo", "--valensi", "3"])
        self.assertEqual(2, kode)

    def test_json_dan_demo(self):
        _, keluaran = self._jalankan(["--teks", "halo kak", "--json"])
        data = json.loads(keluaran)
        self.assertIn("dimensi", data)
        _, keluaran = self._jalankan(["--demo", "--json"])
        demo = json.loads(keluaran)
        self.assertEqual(6, len(demo["giliran"]))
        self.assertIn("keseluruhan", demo["tren"])

    def test_persona_json_dipakai_pada_demo(self):
        # bug lama: --persona-json diabaikan pada mode --demo
        dengan = Persona(nama="Uji", register="santai",
                         pantangan=("senang",))
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "persona.json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump(dengan.to_dict(), f)
            _, keluaran = self._jalankan(
                ["--demo", "--json", "--persona-json", path])
        demo = json.loads(keluaran)
        self.assertEqual("Uji", demo["persona"])

    def test_python_m_pycos_demo(self):
        hasil = subprocess.run([sys.executable, "-m", "pycos", "--demo"],
                               cwd=AKAR, capture_output=True, text=True, timeout=120)
        self.assertEqual(0, hasil.returncode, hasil.stderr[-1500:])
        self.assertIn("Tren lintas giliran", hasil.stdout)


class KepindahanRumahTest(unittest.TestCase):
    """Paket `pycos.selaras` sudah dihapus; programnya berada di rumah baru."""

    def test_rumah_baru_sesuai_lapisan(self):
        import importlib

        self.assertEqual("pycos.inti.persona", Persona.__module__)
        self.assertEqual("pycos.inti.persona", Keadaan.__module__)
        self.assertEqual("pycos.refleksi.nurani", nilai_selaras.__module__)
        self.assertEqual("pycos.refleksi.nurani", PelacakSelaras.__module__)
        self.assertEqual("pycos.bahasa.tutur", analisis_teks.__module__)
        with self.assertRaises(ImportError):
            importlib.import_module("pycos.selaras")

    def test_re_export_kompatibel_di_naluri(self):
        """Nama lama tetap bisa diimpor dari naluri, kelasnya identik."""
        from pycos.inti.naluri import (PERSONA_CONTOH as C2, Keadaan as K2,
                                       Persona as P2)
        from pycos.inti.persona import PERSONA_CONTOH, Keadaan, Persona

        self.assertIs(Persona, P2)
        self.assertIs(Keadaan, K2)
        self.assertIs(PERSONA_CONTOH, C2)

    def test_refleksi_tidak_mengimpor_inti_atau_bahasa_di_tingkat_modul(self):
        """Impor Persona/Keadaan/analisis_teks di nurani wajib di dalam fungsi
        (malas) agar pycos.refleksi tetap bebas lapisan inti/bahasa."""
        jalur = os.path.join(AKAR, "pycos", "refleksi", "nurani.py")
        with open(jalur, "r", encoding="utf-8") as f:
            pohon = ast.parse(f.read(), filename=jalur)
        for simpul in pohon.body:          # hanya tingkat atas modul
            nama = None
            if isinstance(simpul, ast.ImportFrom):
                nama = (simpul.module or "").split(".")[0]
            elif isinstance(simpul, ast.Import):
                nama = simpul.names[0].name.split(".")[0]
            if nama:
                self.assertNotIn(simpul.module if isinstance(simpul, ast.ImportFrom)
                                 else simpul.names[0].name,
                                 ("pycos.inti", "pycos.inti.naluri",
                                  "pycos.inti.persona",
                                  "pycos.bahasa", "pycos.bahasa.tutur"))


if __name__ == "__main__":
    unittest.main()
