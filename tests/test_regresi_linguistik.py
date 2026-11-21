# -*- coding: utf-8 -*-
"""Regresi linguistik: retorika "mana mungkin" (D9), skor tindak tutur (D5),
urutan nasalisasi gugus/digraf (B2), dan pertanyaan balik dari isi ujaran (E9).

Semua impor lapisan Pycos memakai nama paket penuh (`pycos.*`), sama seperti
berkas tes lain di direktori ini; tidak ada impor datar gaya lama.
"""
from __future__ import annotations

import os
import sys
import unittest

AKAR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if AKAR not in sys.path:
    sys.path.insert(0, AKAR)

from pycos.bahasa.teks import tindak_tutur_skor  # noqa: E402
from pycos.bahasa.tutur import Leksikon, analisis_teks  # noqa: E402
from pycos.inti import Naluri  # noqa: E402


class ManaMungkinTest(unittest.TestCase):
    """D9: sentimen setelah "mana/masa mungkin" bukan pernyataan keadaan."""

    def test_mana_mungkin_bukan_positif(self):
        f = analisis_teks("mana mungkin dia setuju dengan rencanaku yang sangat bagus")
        self.assertEqual(0, f.positif)

    def test_masa_mungkin_juga_retorika(self):
        f = analisis_teks("masa mungkin dia setuju")
        self.assertEqual(0, f.positif)

    def test_retorika_berhenti_di_batas_klausa(self):
        f = analisis_teks("mana mungkin itu terjadi, aku tetap senang")
        self.assertEqual(1, f.positif)

    def test_mungkin_saja_masih_normal(self):
        f = analisis_teks("mungkin saja dia senang sekali")
        self.assertEqual(1, f.positif)

    def test_mana_mungkin_tidak_menyisakan_negatif(self):
        f = analisis_teks("mana mungkin aku akan datang")
        self.assertEqual(0, f.positif)
        self.assertEqual(0, f.negatif)


class NasalisasiGugusTest(unittest.TestCase):
    """B2: gugus konsonan/digraf diperiksa SEBELUM aturan satu suku kata."""

    def setUp(self):
        self.lex = Leksikon({"leksikon": []})

    def test_gugus_tidak_terambil_aturan_menge(self):
        self.assertEqual("mengklaim", self.lex.nasalisasi("klaim"))
        self.assertEqual("mengkritik", self.lex.nasalisasi("kritik"))
        self.assertEqual("mengekspor", self.lex.nasalisasi("ekspor"))

    def test_satu_suku_kata_tetap_menge(self):
        self.assertEqual("mengebom", self.lex.nasalisasi("bom"))
        self.assertEqual("mengecat", self.lex.nasalisasi("cat"))

    def test_gugus_titik_dua_aturan_mem_dan_men(self):
        self.assertEqual("memproses", self.lex.nasalisasi("proses"))
        self.assertEqual("memprotes", self.lex.nasalisasi("protes"))
        self.assertEqual("mentransfer", self.lex.nasalisasi("transfer"))


class TindakTuturSkorTest(unittest.TestCase):
    """D5: klitik/afiks tidak menyamarkan leksem; tuduhan deklaratif terbaca."""

    def test_tuduhan_deklaratif_dengan_pronomina(self):
        skor = tindak_tutur_skor("dia curi uangku")
        self.assertGreaterEqual(skor.get("tuduhan", 0.0), 0.5)

    def test_hinaan_dengan_pronomina(self):
        skor = tindak_tutur_skor("kamu pengecut")
        self.assertGreaterEqual(skor.get("hinaan", 0.0), 0.5)

    def test_pujian_dengan_pronomina(self):
        skor = tindak_tutur_skor("hebat sekali kamu")
        self.assertGreaterEqual(skor.get("pujian", 0.0), 0.5)


class PertanyaanBalikTest(unittest.TestCase):
    """E9: balikan dibangun dari isi ujaran, bukan satu template tetap."""

    def _npc(self):
        n = Naluri(name="Nara", rng_seed=41,
                   params={"enable_gejala": False})
        n.enable_kesadaran(semua=True)
        n.enable_presentasi(semua=True)
        return n

    def test_balikan_berbeda_per_jenis_tanya(self):
        n = self._npc()
        jawaban = {}
        for teks in ["di mana kamu tinggal?", "kapan kita berangkat?",
                     "kenapa dia pergi begitu saja?", "berapa harga tiketnya?",
                     "siapa yang datang tadi malam?"]:
            keluar = n.kesadaran.dialogue_turn("Rama", teks)
            jawaban[teks] = keluar.get("pertanyaan_balik") or ""
        self.assertTrue(all(jawaban.values()), jawaban)
        self.assertEqual(len(set(jawaban.values())), len(jawaban),
                         "balikan harus berbeda untuk jenis tanya berbeda")

    def test_balikan_memuat_pronomina_pemicu(self):
        n = self._npc()
        keluar = n.kesadaran.dialogue_turn("Rama", "kapan kita berangkat?")
        self.assertIn("kapan", keluar.get("pertanyaan_balik") or "")


if __name__ == "__main__":
    unittest.main()
