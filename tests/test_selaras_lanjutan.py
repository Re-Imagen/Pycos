# -*- coding: utf-8 -*-
"""Tes lanjutan keselarasan ujaran: negasi klausa, morfologi, leksikon kustom,
dan kalibrasi terhadap korpus berlabel.

Catatan kejujuran: korpus `pycos/sumber_daya/korpus_contoh.jsonl` ditulis oleh
pengembang, bukan penilai manusia, dan sebagian leksikon disesuaikan setelah
melihat kesalahan di korpus itu. Tes terhadapnya hanya menjaga regresi; ia
bukan bukti akurasi pada data independen.
"""
from __future__ import annotations

import contextlib
import io
import json
import os
import sys
import tempfile
import unittest

AKAR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if AKAR not in sys.path:
    sys.path.insert(0, AKAR)

from pycos.__main__ import utama as cli  # noqa: E402
from pycos.bahasa.tutur import (  # noqa: E402
    JENDELA_NEGASI,
    LeksikonCiri,
    analisis_teks,
)
from pycos.inti.naluri import PERSONA_CONTOH, Keadaan  # noqa: E402
from pycos.refleksi.nurani import (  # noqa: E402
    ContohLabel,
    contoh_dari_dict,
    kappa_cohen,
    laporan_kalibrasi,
    muat_korpus,
    nilai_selaras,
    ukur_fitur,
    ukur_selaras,
)

KORPUS = os.path.join(AKAR, "pycos", "sumber_daya", "korpus_contoh.jsonl")


def _leksikon_kosong(**isi):
    dasar = {k: [] for k in ("positif", "negatif", "pelunak", "penguat",
                             "formal", "informal", "negasi")}
    dasar.update(isi)
    return dasar


class NegasiKlausaTest(unittest.TestCase):
    def test_jendela_tiga_token(self):
        self.assertEqual(3, JENDELA_NEGASI)
        self.assertEqual(-1.0, analisis_teks("tidak ada yang senang").polaritas())
        self.assertEqual(-1.0, analisis_teks("bukan hal yang bagus").polaritas())

    def test_negasi_berhenti_di_tanda_baca(self):
        self.assertEqual(1.0, analisis_teks("tidak tahu. aku senang").polaritas())
        self.assertEqual(1.0, analisis_teks("aku senang, tidak").polaritas())

    def test_negasi_di_luar_jendela_tidak_membalik(self):
        self.assertEqual(1.0, analisis_teks("tidak tahu kenapa aku senang").polaritas())

    def test_negasi_membalik_kata_negatif(self):
        self.assertEqual(1.0, analisis_teks("nggak sedih kok").polaritas())


class MorfologiTest(unittest.TestCase):
    def test_bentuk_turunan_terdeteksi(self):
        casting = {
            "menyenangkan sekali": 1.0,
            "penyayang sekali": 1.0,
            "kebahagiaannya": 1.0,
            "keberanian itu": 1.0,
            "tersakiti sekali": -1.0,
            "dikecewakan orang": -1.0,
            "mengecewakan kami": -1.0,
            "sedihnya sekali": -1.0,
        }
        for teks, harap in casting.items():
            with self.subTest(teks=teks):
                self.assertEqual(harap, analisis_teks(teks).polaritas())

    def test_kata_pendek_tidak_dipotong(self):
        # stem di bawah _MIN_STEM tidak boleh menimbulkan kecocokan palsu
        self.assertIsNone(analisis_teks("di sana").polaritas())

    def test_frasa_terima_kasih(self):
        self.assertEqual(1.0, analisis_teks("terima kasih banyak").polaritas())
        self.assertIsNone(analisis_teks("terima jaket itu").polaritas())


class LeksikonTest(unittest.TestCase):
    def test_roundtrip_dict(self):
        lx = LeksikonCiri.from_dict(_leksikon_kosong(positif=["cemerlang"]))
        self.assertEqual(["cemerlang"], lx.to_dict()["positif"])
        self.assertEqual(lx, LeksikonCiri.from_dict(lx.to_dict()))

    def test_kustom_mengganti_bawaan(self):
        lx = LeksikonCiri.from_dict(_leksikon_kosong(positif=["cemerlang"]))
        self.assertEqual(1.0, analisis_teks("cemerlang sekali", lx).polaritas())
        self.assertIsNone(analisis_teks("aku senang", lx).polaritas())

    def test_nilai_selaras_menerima_leksikon(self):
        lx = LeksikonCiri.from_dict(_leksikon_kosong(positif=["cemerlang"]))
        k = Keadaan(valensi=0.6)
        bawaan = nilai_selaras(PERSONA_CONTOH, k, "aku senang banget hari ini!")
        kustom = nilai_selaras(PERSONA_CONTOH, k, "aku senang banget hari ini!", lx)
        self.assertNotEqual(bawaan.dimensi, kustom.dimensi)
        self.assertEqual(nilai_selaras(PERSONA_CONTOH, k, "aku senang").to_dict(),
                         nilai_selaras(PERSONA_CONTOH, k, "aku senang", None).to_dict())

    def test_tolak_kategori_hilang(self):
        d = _leksikon_kosong()
        del d["negasi"]
        with self.assertRaises(ValueError):
            LeksikonCiri.from_dict(d)

    def test_tolak_kunci_tak_dikenal(self):
        with self.assertRaises(ValueError):
            LeksikonCiri.from_dict(dict(_leksikon_kosong(), ekstra=[]))

    def test_tolak_bukan_daftar(self):
        with self.assertRaises(ValueError):
            LeksikonCiri.from_dict(_leksikon_kosong(positif="senang"))

    def test_tolak_frasa_multi_kata(self):
        with self.assertRaises(ValueError) as konteks:
            LeksikonCiri.from_dict(_leksikon_kosong(negatif=["kurang ajar"]))
        self.assertIn("satu token", str(konteks.exception))

    def test_dari_berkas(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "lx.json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump(_leksikon_kosong(positif=["asyik"]), f)
            lx = LeksikonCiri.dari_berkas(path)
        self.assertEqual(1.0, analisis_teks("asyik sekali", lx).polaritas())


class MuatKorpusTest(unittest.TestCase):
    def _tulis(self, d, baris):
        path = os.path.join(d, "k.jsonl")
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(baris) + "\n")
        return path

    def test_korpus_contoh_valid(self):
        korpus = muat_korpus(KORPUS)
        self.assertGreaterEqual(len(korpus), 30)
        self.assertTrue(all(isinstance(c, ContohLabel) for c in korpus))

    def test_baris_kosong_dilewati(self):
        with tempfile.TemporaryDirectory() as d:
            path = self._tulis(d, ['{"teks": "aku senang"}', "", '{"teks": "sedih"}'])
            self.assertEqual(2, len(muat_korpus(path)))

    def test_galat_menyebut_nomor_baris(self):
        with tempfile.TemporaryDirectory() as d:
            path = self._tulis(d, ['{"teks": "ok"}', '{"teks": "x", "bogus": 1}'])
            with self.assertRaises(ValueError) as konteks:
                muat_korpus(path)
            self.assertIn("baris 2", str(konteks.exception))

    def test_json_rusak(self):
        with tempfile.TemporaryDirectory() as d:
            path = self._tulis(d, ["{teks:"])
            with self.assertRaises(ValueError):
                muat_korpus(path)

    def test_korpus_kosong(self):
        with tempfile.TemporaryDirectory() as d:
            path = self._tulis(d, [""])
            with self.assertRaises(ValueError):
                muat_korpus(path)

    def test_validasi_nilai_label(self):
        bad = [
            {"teks": "x", "polaritas": 2},
            {"teks": "x", "polaritas": True},
            {"teks": "x", "formalitas": "gaul"},
            {"teks": "x", "selaras": "ya"},
            {"teks": ""},
            {"polaritas": 1},
        ]
        for data in bad:
            with self.subTest(data=data):
                with self.assertRaises(ValueError):
                    contoh_dari_dict(data)

    def test_contoh_dengan_keadaan_dan_persona(self):
        c = contoh_dari_dict({"teks": "halo", "selaras": True,
                              "keadaan": {"valensi": 0.2},
                              "persona": {"nama": "Uji"}})
        self.assertEqual(0.2, c.keadaan.valensi)
        self.assertEqual("Uji", c.persona.nama)


class KappaTest(unittest.TestCase):
    def test_kappa_nilai_diketahui(self):
        pasangan = [(1, 1), (1, 1), (0, 0), (0, 1)]
        self.assertAlmostEqual(0.5, kappa_cohen(pasangan))

    def test_kappa_sempurna(self):
        self.assertAlmostEqual(1.0, kappa_cohen([(1, 1), (0, 0), (-1, -1)]))

    def test_kappa_satu_kelas(self):
        self.assertEqual(1.0, kappa_cohen([(1, 1), (1, 1)]))

    def test_kappa_kosong(self):
        self.assertIsNone(kappa_cohen([]))


class UkurFiturTest(unittest.TestCase):
    def test_cakupan_dan_akurasi(self):
        korpus = [
            ContohLabel("aku senang", polaritas=1),
            ContohLabel("aku tidak senang", polaritas=-1),
            ContohLabel("meja di sana", polaritas=1),     # tanpa bukti -> tak tercakup
        ]
        r = ukur_fitur(korpus)["polaritas"]
        self.assertEqual(3, r["label"])
        self.assertAlmostEqual(2 / 3, r["cakupan"], places=3)
        self.assertEqual(1.0, r["akurasi"])

    def test_formalitas_tanpa_label(self):
        r = ukur_fitur([ContohLabel("aku senang")])["formalitas"]
        self.assertEqual(0, r["label"])
        self.assertIsNone(r["akurasi"])

    def test_formalitas_salah_terukur(self):
        korpus = [ContohLabel("saya mohon izin", formalitas="santai")]
        r = ukur_fitur(korpus)["formalitas"]
        self.assertEqual(0.0, r["akurasi"])


class UkurSelarasTest(unittest.TestCase):
    def _korpus_sintetis(self):
        k_ya = Keadaan(valensi=0.6, gairah=0.7, ketidakpastian=0.2)
        ya = [ContohLabel("aku senang banget hari ini!", selaras=True, keadaan=k_ya)] * 4
        tidak = [ContohLabel("kamu sialan!", selaras=False,
                             keadaan=Keadaan(valensi=-0.5, gairah=0.8))] * 4
        return ya + tidak

    def test_kurang_dari_empat_label(self):
        r = ukur_selaras([ContohLabel("halo", selaras=True)])
        self.assertIn("keterangan", r)

    def test_pipeline_pada_data_sintetis(self):
        r = ukur_selaras(self._korpus_sintetis())
        self.assertEqual(1.0, r["akurasi_default"])
        self.assertEqual(0.75, r["ambang_default"])
        self.assertTrue(0.30 <= r["ambang_latih"] <= 0.95)
        self.assertIsNotNone(r["akurasi_uji"])

    def test_ambang_dipilih_dari_porsi_latih_saja(self):
        # Porsi latih berisi semua label benar; porsi uji dibalik sehingga akurasi
        # uji harus turun. Bila pencarian memakai seluruh data, hasilnya berbeda.
        benar = self._korpus_sintetis()[:4]
        balik = [ContohLabel(c.teks, selaras=not c.selaras, keadaan=c.keadaan)
                 for c in self._korpus_sintetis()[4:]]
        r = ukur_selaras(benar + balik, porsi_latih=0.5)
        self.assertEqual(1.0, r["akurasi_latih"])
        self.assertEqual(0.0, r["akurasi_uji"])

    def test_porsi_terlalu_kecil(self):
        r = ukur_selaras(self._korpus_sintetis()[:4], porsi_latih=0.9)
        self.assertIn("keterangan", r)


class KorpusContohRegresiTest(unittest.TestCase):
    """Penjaga regresi, bukan klaim akurasi pada data independen (lihat docstring)."""

    @classmethod
    def setUpClass(cls):
        cls.laporan = laporan_kalibrasi(muat_korpus(KORPUS))

    def test_polaritas_tidak_turun(self):
        self.assertGreaterEqual(self.laporan["fitur"]["polaritas"]["akurasi"], 0.95)
        self.assertEqual(1.0, self.laporan["fitur"]["polaritas"]["cakupan"])

    def test_formalitas_tidak_turun(self):
        self.assertGreaterEqual(self.laporan["fitur"]["formalitas"]["akurasi"], 0.95)

    def test_sarkasme_tetap_diakui_sebagai_batasan(self):
        # Sarkasme "hebat banget ..., bikin aku nangis" tidak tertangani; tes ini
        # mendokumentasikan kegagalan yang diketahui agar tidak diam-diam hilang.
        self.assertEqual(1.0, analisis_teks(
            "wah, hebat banget ya, bikin aku nangis.").polaritas())

    def test_laporan_berisi_peringatan_ukuran(self):
        self.assertIn("akurasi_uji", self.laporan["selaras"])


class CliKalibrasiTest(unittest.TestCase):
    def _jalankan(self, argv):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(io.StringIO()):
            kode = cli(argv)
        return kode, buf.getvalue()

    def test_kalibrasi_teks(self):
        kode, out = self._jalankan(["--kalibrasi", KORPUS])
        self.assertEqual(0, kode)
        self.assertIn("polaritas", out)
        self.assertIn("akurasi uji", out)

    def test_kalibrasi_json(self):
        kode, out = self._jalankan(["--kalibrasi", KORPUS, "--json"])
        self.assertEqual(0, kode)
        self.assertIn("fitur", json.loads(out))

    def test_korpus_rusak_kode_dua(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "r.jsonl")
            with open(path, "w", encoding="utf-8") as f:
                f.write('{"teks": "x", "polaritas": 9}\n')
            kode, _ = self._jalankan(["--kalibrasi", path])
        self.assertEqual(2, kode)

    def test_leksikon_kustom_di_cli(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "lx.json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump(_leksikon_kosong(positif=["cemerlang"]), f)
            kode, out = self._jalankan(["--teks", "cemerlang sekali", "--leksikon", path,
                                        "--valensi", "0.6", "--json"])
        self.assertIn(kode, (0, 1))
        self.assertIn("skor", json.loads(out))

    def test_leksikon_tidak_ada_kode_dua(self):
        kode, _ = self._jalankan(["--teks", "halo", "--leksikon", "/tidak/ada.json"])
        self.assertEqual(2, kode)


if __name__ == "__main__":
    unittest.main()
