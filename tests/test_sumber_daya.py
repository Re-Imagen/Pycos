# -*- coding: utf-8 -*-
"""Tes resolusi sumber daya paket: `pycos/sumber_daya/leksikon_pycos.json`
dan `pycos/sumber_daya/korpus_contoh.jsonl`.

Berkas data ikut pindah ke dalam paket bersama helper jalurnya di
`pycos/dukungan/sumber.py`. Yang dijaga di sini: path paket selalu absolut dan
menunjuk ke berkas yang sama di checkout mana pun, kandidat pencarian leksikon
tetap terurut, korpus contoh ikut terpasang untuk `--kalibrasi`, dan lapisan
tutur (`pycos.bahasa.tutur`) serta jembatan `Presentasi` tetap menemukan
leksikon tanpa path manual.
"""
from __future__ import annotations

import json
import os
import sys
import unittest

AKAR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if AKAR not in sys.path:
    sys.path.insert(0, AKAR)

from pycos.dukungan.sumber import (NAMA_KORPUS, NAMA_LEKSIKON,  # noqa: E402
                                   akar_paket, ada_sumber_daya,
                                   kandidat_leksikon, jalur_korpus,
                                   jalur_leksikon, sumber_daya)


class JalurSumberDayaTest(unittest.TestCase):
    def test_akar_paket_menunjuk_direktori_pycos(self):
        self.assertEqual("pycos", os.path.basename(akar_paket()))
        self.assertEqual(AKAR, os.path.dirname(akar_paket()))

    def test_direktori_sumber_daya_berada_dalam_paket(self):
        self.assertEqual(os.path.join(akar_paket(), "sumber_daya"),
                         sumber_daya())

    def test_jalur_leksikon_absolut_dan_bisa_dibaca(self):
        jalur = jalur_leksikon()
        self.assertTrue(os.path.isabs(jalur))
        self.assertEqual(NAMA_LEKSIKON, os.path.basename(jalur))
        self.assertEqual(os.path.join(sumber_daya(), NAMA_LEKSIKON), jalur)
        self.assertTrue(ada_sumber_daya(), "leksikon tidak ditemukan di paket")

    def test_jalur_korpus_absolut_dan_korpus_ikut_terpasang(self):
        jalur = jalur_korpus()
        self.assertTrue(os.path.isabs(jalur))
        self.assertEqual(NAMA_KORPUS, os.path.basename(jalur))
        self.assertEqual(os.path.join(sumber_daya(), NAMA_KORPUS), jalur)
        self.assertTrue(os.path.isfile(jalur),
                        "korpus contoh tidak ditemukan di paket")
        self.assertTrue(ada_sumber_daya(jalur))
        self.assertTrue(ada_sumber_daya(jalur))
        self.assertFalse(ada_sumber_daya(os.path.join(AKAR, "tidak-ada.json")))

    def test_konstanta_subpaket_sama_dengan_helper(self):
        from pycos import sumber_daya as paket_sumber

        self.assertEqual(jalur_leksikon(), paket_sumber.LEKSIKON)
        self.assertEqual(NAMA_LEKSIKON, paket_sumber.NAMA_LEKSIKON)
        for nama in paket_sumber.__all__:
            self.assertTrue(hasattr(paket_sumber, nama))

    def test_kandidat_terurut_dan_bebas_duplikat(self):
        jalur = jalur_leksikon()
        k = kandidat_leksikon(ekplisit="/opt/aksara.json", sekitar="/srv")
        self.assertEqual("/opt/aksara.json", k[0],
                         "path eksplisit harus paling depan")
        self.assertEqual(os.path.join("/srv", NAMA_LEKSIKON), k[1])
        self.assertEqual(jalur, k[2], "sumber daya paket harus sebelum cwd")
        self.assertEqual(os.path.join(os.getcwd(), NAMA_LEKSIKON), k[-1])
        self.assertEqual(len(k), len(set(k)), "kandidat duplikat")

    def test_kandidat_tanpa_argumen_tetut_lengkap(self):
        k = kandidat_leksikon()
        self.assertIn(jalur_leksikon(), k)
        self.assertFalse([c for c in k if not str(c).strip()],
                         "kandidat kosong tidak boleh ikut terkirim")

    def test_kandidat_menggabung_sumber_daya_tanpa_duplikat(self):
        k = kandidat_leksikon(sekitar=sumber_daya())
        self.assertEqual(1, sum(1 for c in k if c == jalur_leksikon()))

    def test_nama_berkas_dapat_diganti(self):
        self.assertEqual(os.path.join(sumber_daya(), "kustom.json"),
                         jalur_leksikon("kustom.json"))


class IsiLeksikonTest(unittest.TestCase):
    def setUp(self):
        with open(jalur_leksikon(), "r", encoding="utf-8") as f:
            self.data = json.load(f)

    def test_kunci_struktural_ada(self):
        for kunci in ("meta", "lattice", "morfologi", "predikat", "fungsi",
                      "leksikon"):
            with self.subTest(kunci=kunci):
                self.assertIn(kunci, self.data)

    def test_jumlah_entri_sesuai_metadata(self):
        meta = self.data["meta"]
        self.assertEqual(len(self.data["leksikon"]),
                         int(meta["jumlah_lema"]),
                         "meta.jumlah_lema berbeda dari isi leksikon")
        self.assertEqual(4262, len(self.data["leksikon"]))

    def test_pembagian_bahasa_sesuai_metadata(self):
        meta = self.data["meta"]
        per_bahasa = meta["per_bahasa"]
        nyata = {}
        for entri in self.data["leksikon"]:
            nyata[entri.get("bahasa", "?")] = nyata.get(
                entri.get("bahasa", "?"), 0) + 1
        self.assertEqual({k: int(v) for k, v in per_bahasa.items()}, nyata)
        self.assertEqual(4262, sum(nyata.values()))


class TuturDanLeksikonTest(unittest.TestCase):
    def test_engine_muat_leksikon_paket(self):
        from pycos.bahasa import GenContext, TuturEngine

        engine = TuturEngine(path=jalur_leksikon())
        self.assertTrue(engine.tersedia())
        self.assertEqual(4262, engine.info()["jumlah_lema"])
        ujaran = engine.ucap(GenContext(act="menyatakan", topik="api",
                                        niat="aku melihat api", seed=2))
        self.assertIsNotNone(ujaran)
        self.assertEqual("aku melihat api.", ujaran.teks)

    def test_peringatan_memasukkan_sebab_dari_spotlight(self):
        from pycos.bahasa import GenContext, TuturEngine

        engine = TuturEngine(path=jalur_leksikon())
        ujaran = engine.ucap(GenContext(
            act="peringatan", topik="hutan", spotlight=("asap tebal",), seed=17))
        self.assertIsNotNone(ujaran)
        self.assertIn("karena asap tebal", ujaran.teks)
        tanpa_sebab = engine.ucap(GenContext(
            act="peringatan", topik="hutan", seed=17))
        self.assertNotIn("karena ", tanpa_sebab.teks)

    def test_tanpa_path_engine_tidak_aktif(self):
        """Perilaku lama dipertahankan: engine tidak memuat sendiri secara diam-diam."""
        from pycos.bahasa import TuturEngine

        self.assertFalse(TuturEngine().tersedia())
        self.assertFalse(TuturEngine(path="leksikon-tidak-ada.json").tersedia())

    def test_presentasi_menemukan_leksikon_paket_sendiri(self):
        from pycos.dukungan.sumber import jalur_leksikon as jalur

        npc = __import__("pycos.inti", fromlist=["Naluri"]).Naluri(
            name="Ayu", rng_seed=7)
        npc.params["enable_presentasi"] = True
        engine = npc.presentasi.tutur_engine()
        self.assertIsNotNone(engine, "leksikon paket tidak ditemukan otomatis")
        self.assertTrue(engine.tersedia())
        self.assertEqual(os.path.realpath(jalur()),
                         os.path.realpath(engine.path))

    def test_set_leksikon_menerima_path_eksplisit(self):
        npc = __import__("pycos.inti", fromlist=["Naluri"]).Naluri(
            name="Bil", rng_seed=3)
        npc.params["enable_presentasi"] = True
        self.assertTrue(npc.presentasi.set_leksikon(jalur_leksikon()))
        npc.params["presentasi_generatif"] = False
        npc.presentasi._tutur = None
        npc.presentasi._tutur_dimuat = False
        self.assertIsNone(npc.presentasi.tutur_engine(),
                          "sakelar presentasi_generatif harus mematikan jalur generatif")


if __name__ == "__main__":
    unittest.main()
