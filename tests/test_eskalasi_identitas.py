# -*- coding: utf-8 -*-
"""Regresi H7 & H9 (ANALISIS_LINGUISTIK): eskalasi variasi bertingkat dan
batas identitas yang proporsional.

H7 — tingkat pertama meminta KANDIDAT BARU dari mesin tutur dengan larangan
pada struktur yang baru dipakai; pengakuan repetisi hanya langkah terakhir.

H9 — `batas_identitas` dinilai menurut isi klaim identitas dan kedekatannya
dengan identitas inti, bukan −0,80 tetap setiap ada klaim.
"""
from __future__ import annotations

import os
import sys
import unittest

AKAR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if AKAR not in sys.path:
    sys.path.insert(0, AKAR)

from pycos.inti import Naluri  # noqa: E402
from pycos.inti.ekstensi.pelindung import _pelindung_init  # noqa: E402


def _npc(watak: str = "paranoid") -> Naluri:
    n = Naluri(name="Sarah", rng_seed=71, params={"enable_pelindung": True})
    n.set_personality_preset(watak)
    n.enable_presentasi(semua=True)
    n.enable_kesadaran(semua=True)
    return n


class EskalasiVariasiTest(unittest.TestCase):
    """H7: variasi dari mesin tutur, bukan sinonim, sebelum pengakuan."""

    def test_tingkat_satu_memakai_kandidat_mesin_tutur(self):
        p = _pelindung_init(_npc().presentasi)
        p._pelindung_teks[:] = ["api itu kulihat"]
        p._pelindung_anggaran["leksikal"] = 0
        teks, act, info = p.eskalasi_variasi("api itu kulihat", "menjawab",
                                             "Player", "api")
        self.assertEqual(1, info.get("tingkat"))
        self.assertEqual("kandidat_baru_mesin_tutur", info.get("cara"))
        self.assertIn("larangan_bentuk", info)
        self.assertNotEqual("api itu kulihat", teks)
        self.assertIn("menjawab", ["menjawab", act])

    def test_isi_asal_tidak_hilang(self):
        p = _pelindung_init(_npc().presentasi)
        p._pelindung_teks[:] = ["api itu kulihat"]
        p._pelindung_anggaran["leksikal"] = 0
        teks, _, info = p.eskalasi_variasi("api itu kulihat", "menjawab",
                                           "Player", "api")
        if info.get("cara") == "kandidat_baru_mesin_tutur":
            self.assertIn("api", teks.lower(),
                          "variasi kehilangan isi asal: {}".format(teks))

    def test_pengakuan_repetisi_hanya_langkah_terakhir(self):
        p = _pelindung_init(_npc().presentasi)
        p._pelindung_anggaran = {k: 0 for k in p._pelindung_anggaran}
        p._pelindung_act_terakhir[:] = ["menjawab"] * 6
        p._pelindung_teks[:] = ["aku tidak tahu harus bilang apa"] * 4
        hasil, act, info = p.eskalasi_variasi(
            "aku tidak tahu harus bilang apa", "menjawab", "Player", "api")
        self.assertEqual("pengakuan_repetisi", info.get("cara"))
        self.assertTrue(info.get("langkah_terakhir"))
        self.assertTrue(hasil)

    def test_bentuk_terpakai_dicatat_terbatas(self):
        p = _pelindung_init(_npc().presentasi)
        for i in range(12):
            p.eskalasi_variasi("aku melihat api " * 1 + "itu" * (i % 3),
                               "menjawab", "Player", "api")
        self.assertLessEqual(len(p._pelindung_bentuk_terpakai), 8)


class BatasIdentitasProporsionalTest(unittest.TestCase):
    """H9: penolakan identitas sebanding kedekatan klaim dengan inti."""

    def setUp(self):
        from pycos.mandiri.organik import PenolakanTutur
        self.mekanisme = PenolakanTutur()

    def test_klaim_jauh_tidak_menekan_tutur(self):
        jauh, _ = self.mekanisme.kelayakan({"kedekatan_identitas": 0.1})
        dekat, _ = self.mekanisme.kelayakan({"kedekatan_identitas": 0.9})
        self.assertGreater(jauh, dekat)
        self.assertGreater(jauh, 0.8, "klaim jauh masih menekan tutur berat")
        self.assertLess(dekat, 0.3)

    def test_tanpa_klaim_tidak_ada_pinalti(self):
        skor, komp = self.mekanisme.kelayakan({"arousal": 0.1})
        self.assertNotIn("identitas", komp)
        self.assertGreater(skor, 0.9)

    def test_kunci_lama_tetap_dihormati(self):
        skor, komp = self.mekanisme.kelayakan({"batas_identitas": True})
        self.assertIn("identitas", komp)
        self.assertLess(skor, 0.4)

    def test_nilai_bukan_pinalti_tetap(self):
        _, komp_kecil = self.mekanisme.kelayakan({"kedekatan_identitas": 0.2})
        _, komp_besar = self.mekanisme.kelayakan({"kedekatan_identitas": 0.8})
        self.assertGreater(komp_kecil["identitas"], komp_besar["identitas"])
        self.assertNotEqual(-0.80, komp_besar["identitas"])

    def test_konteks_tubuh_membawa_kedekatan_dinamis(self):
        from pycos.inti.ekstensi.organik import _organik_konteks_tubuh
        n = _npc()
        n.tetapkan_identitas("aku penjaga yang tidak percaya siapa pun",
                             {"senang": "tolak"})
        p = n.presentasi
        p._recent_texts[:] = ["aku penjaga yang tidak percaya siapa pun"]
        konteks = _organik_konteks_tubuh(p)
        self.assertIn("kedekatan_identitas", konteks)
        self.assertGreaterEqual(konteks["kedekatan_identitas"], 0.0)
        self.assertLessEqual(konteks["kedekatan_identitas"], 1.0)
        self.assertNotIn("batas_identitas", konteks,
                         "penanda tetap sudah diganti kedekatan (H9)")


if __name__ == "__main__":
    unittest.main()
