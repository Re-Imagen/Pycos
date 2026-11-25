# -*- coding: utf-8 -*-
"""J2 (ANALISIS_LINGUISTIK): tes SIFAT generator tutur.

Untuk semua act × register × banyak seed, keluaran mesin tutur harus:

* tidak kosong;
* lolos G1 (tidak ada masalah gramatika berat);
* tidak memuat istilah internal (tick, skor, arousal, json, …);
* punya lebih dari satu varian untuk keadaan yang sama.

Tes ini tidak mengunci kalimat tertentu — ia menjaga sifat yang harus tetap
benar setelah perubahan leksikon, morfologi, atau orkestrasi.
"""
from __future__ import annotations

import os
import sys
import unittest

AKAR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if AKAR not in sys.path:
    sys.path.insert(0, AKAR)

from pycos.bahasa.teks import G1_KERAS, periksa_gramatika  # noqa: E402
from pycos.bahasa.tutur import GenContext, TuturEngine  # noqa: E402
from pycos.dukungan.sumber import jalur_leksikon  # noqa: E402
from pycos.inti.presentasi import _ACT_FUNGSI  # noqa: E402

REGISTER = ("netral", "akrab", "formal")

#: Istilah yang tidak pernah boleh muncul sebagai kata dalam dialog.
ISTILAH_INTERNAL = frozenset({
    "tick", "skor", "score", "ignition", "workspace", "arousal", "valensi",
    "valence", "spotlight", "residu", "koherensi", "neuron", "param",
    "params", "json", "none", "true", "false", "sukses", "trace", "buffer",
    "antrean", "state", "engine", "leksikon", "predikat",
})


def _konteks(act: str, register: str, seed: int) -> GenContext:
    """Konteks kaya: biografi, emosi, nilai, batas, memori — bukan topik saja."""
    return GenContext(
        act=act, register=register, seed=seed, topik="api", dekat=True,
        core=("api membakar rumah",), timeline=("aku lari dari api",),
        inner="api itu panas", niat="api itu panas", spotlight=("api",),
        emosi=("TAKUT",), valensi=-0.5, arousal=0.6, doubt=0.4,
        mortality=0.3, values=("kejujuran",), boundaries=("aku tidak menyakiti",),
        grief=("ibu",), kepada="Player",
    )


class SifatGeneratorTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = TuturEngine(path=jalur_leksikon())
        assert cls.engine.tersedia()
        cls.act = sorted(_ACT_FUNGSI)

    def test_tidak_kosong_untuk_semua_act_dan_register(self):
        for act in self.act:
            for register in REGISTER:
                for seed in range(3):
                    with self.subTest(act=act, register=register, seed=seed):
                        ujaran = self.engine.ucap(
                            _konteks(act, register, seed))
                        self.assertIsNotNone(ujaran)
                        self.assertTrue(ujaran.teks.strip(),
                                        "act {} di {} menghasilkan diam"
                                        .format(act, register))

    def test_lolos_g1_untuk_semua_act_dan_register(self):
        for act in self.act:
            for register in REGISTER:
                for seed in range(3):
                    teks = self.engine.ucap(
                        _konteks(act, register, seed)).teks
                    masalah = [m for m in periksa_gramatika(teks, self.engine.leks)
                               if m in G1_KERAS]
                    with self.subTest(act=act, register=register, seed=seed,
                                      teks=teks):
                        self.assertEqual([], masalah,
                                         "{} ({}): {}".format(act, register, masalah))

    def test_tanpa_istilah_internal(self):
        for act in self.act:
            for register in REGISTER:
                for seed in range(3):
                    teks = self.engine.ucap(
                        _konteks(act, register, seed)).teks.lower()
                    kata = set(teks.replace(".", " ").replace(",", " ")
                               .replace("?", " ").replace("!", " ").split())
                    bocor = kata & ISTILAH_INTERNAL
                    with self.subTest(act=act, register=register, seed=seed,
                                      teks=teks):
                        self.assertEqual(set(), bocor,
                                         "istilah internal bocor: {}"
                                         .format(sorted(bocor)))

    def test_lebih_dari_satu_varian_per_act(self):
        jumlah_rendah = {}
        for act in self.act:
            keluaran = set()
            for register in REGISTER:
                for seed in range(6):
                    keluaran.add(self.engine.ucap(
                        _konteks(act, register, seed)).teks)
            if len(keluaran) < 2:
                jumlah_rendah[act] = sorted(keluaran)
        self.assertEqual({}, jumlah_rendah,
                         "act dengan satu varian saja: {}".format(jumlah_rendah))


if __name__ == "__main__":
    unittest.main()
