# -*- coding: utf-8 -*-
"""Regresi F4–F7 (ANALISIS_LINGUISTIK): skor leksikal kontekstual, variasi
struktur & partikel wacana, serta idiolek persona yang mengalir dari `Persona`
ke `GenContext` lewat `konteks_dari_presentasi`.

Yang dijaga di sini adalah sifat, bukan string tertentu: sinonim fokus dan
kolokasi menaikkan skor, antonim menurunkannya (kecuali act yang memang
menolak/menantang/menegur), penalti riwayat meluruh, partikel tidak pernah
muncul pada register formal/netral, dan snapshot persona lama tetap dimuat.
"""
from __future__ import annotations

import dataclasses
import os
import sys
import unittest

AKAR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if AKAR not in sys.path:
    sys.path.insert(0, AKAR)

from pycos.bahasa.tutur import (GenContext, Leksikon, TuturEngine,  # noqa: E402
                                konteks_dari_presentasi, muat_leksikon)
from pycos.dukungan.sumber import jalur_leksikon  # noqa: E402
from pycos.inti.persona import Persona  # noqa: E402


def _leksikon() -> Leksikon:
    return muat_leksikon(jalur_leksikon())


class IdiolekPersonaTest(unittest.TestCase):
    """F7: lima bidang idiolek pada Persona bertahan pada simpan/muat."""

    def test_bidang_idiolek_bolak_balik(self):
        p = Persona(nama="Rani", register="santai",
                    kata_favorit=("dingin", "api"), panjang_kalimat="pendek",
                    partikel=("dong",), sapaan=("Kak",),
                    keterusterangan="langsung")
        q = Persona.from_dict(p.to_dict())
        self.assertEqual(p.to_dict(), q.to_dict())
        self.assertEqual(("dingin", "api"), q.kata_favorit)
        self.assertEqual("langsung", q.keterusterangan)

    def test_snapshot_lama_tetap_dimuat(self):
        lama = {"nama": "Bima", "sifat": {"hangat": 0.5},
                "register": "formal", "pantangan": []}
        p = Persona.from_dict(lama)
        self.assertEqual((), p.kata_favorit)
        self.assertEqual("netral", p.panjang_kalimat)
        self.assertEqual("netral", p.keterusterangan)
        self.assertEqual((), p.partikel)
        self.assertEqual((), p.sapaan)

    def test_nilai_tak_dikenal_ditolak(self):
        with self.assertRaises(ValueError):
            Persona(nama="X", panjang_kalimat="panjang sekali")
        with self.assertRaises(ValueError):
            Persona(nama="X", keterusterangan="kasar")
        with self.assertRaises(ValueError):
            Persona(nama="X", kata_favorit="api")   # string tunggal


class IdiolekMasukKonteksTest(unittest.TestCase):
    """F7: `konteks_dari_presentasi` memetakan Persona → GenContext."""

    def test_bidang_persona_terpetakan(self):
        class _Naluri:
            tick_count = 3
            persona = Persona(nama="Rani", register="santai",
                              kata_favorit=("dingin",), partikel=("dong",),
                              sapaan=("Kak",), panjang_kalimat="pendek",
                              keterusterangan="lunak")

            def mood(self):
                raise RuntimeError("tanpa mood")

        class _P:
            naluri = _Naluri()

        ctx = konteks_dari_presentasi(_P(), act="menyatakan", topik="api")
        self.assertEqual("akrab", ctx.register)
        self.assertEqual(("dingin",), ctx.kata_favorit)
        self.assertEqual(("dong",), ctx.partikel_persona)
        self.assertEqual(("Kak",), ctx.sapaan)
        self.assertEqual("pendek", ctx.panjang_kalimat)
        self.assertEqual("lunak", ctx.keterusterangan)

    def test_tanpa_persona_nilai_netral(self):
        class _Naluri:
            tick_count = 1

            def mood(self):
                raise RuntimeError("tanpa mood")

        class _P:
            naluri = _Naluri()

        ctx = konteks_dari_presentasi(_P(), act="menyatakan")
        self.assertEqual((), ctx.kata_favorit)
        self.assertEqual("netral", ctx.panjang_kalimat)
        self.assertEqual("netral", ctx.keterusterangan)


class SkorKonteksTest(unittest.TestCase):
    """F4: sinonim, kolokasi, antonim, favorit, dan peluruhan riwayat."""

    def setUp(self):
        self.leks = _leksikon()
        from pycos.bahasa.tutur import L2, Slot
        import random
        self.L2, self.Slot = L2, Slot
        self.l2 = L2(self.leks, random.Random(7), [])

    def _slot(self) -> "object":
        return self.Slot("OBJEK", "N", "ENTITAS", True, 0.5, 0.5, False)

    def _entri(self, lema: str) -> dict:
        entri = self.leks.ambil("id", lema)
        self.assertIsNotNone(entri, "lema {!r} tidak ada di leksikon".format(lema))
        return entri

    def test_sinonim_fokus_menaikkan_skor(self):
        entri = {"lema": "nyala", "sinonim": ["api"], "bahasa": "id",
                 "register": ["netral"], "tipe_semantik": ["ENTITAS"],
                 "frekuensi": 0.5}
        tanpa = self.l2._skor(entri, self._slot(), GenContext())
        dengan = self.l2._skor(
            entri, self._slot(), GenContext(spotlight=("api",)))
        self.assertGreater(dengan, tanpa)

    def test_antonim_menurunkan_skor_kecuali_act_menolak(self):
        entri = {"lema": "dingin", "antonim": ["panas"], "bahasa": "id",
                 "register": ["netral"], "tipe_semantik": ["ENTITAS"],
                 "frekuensi": 0.5}
        acuan = self.l2._skor(entri, self._slot(), GenContext())
        ditolak = self.l2._skor(
            entri, self._slot(), GenContext(topik="panas"))
        self.assertLess(ditolak, acuan)
        menolak = self.l2._skor(
            entri, self._slot(), GenContext(topik="panas", act="menolak"))
        self.assertGreater(menolak, ditolak)

    def test_kata_favorit_menaikkan_skor(self):
        entri = {"lema": "dingin", "bahasa": "id", "register": ["netral"],
                 "tipe_semantik": ["ENTITAS"], "frekuensi": 0.5}
        tanpa = self.l2._skor(entri, self._slot(), GenContext())
        dengan = self.l2._skor(
            entri, self._slot(), GenContext(kata_favorit=("dingin",)))
        self.assertGreater(dengan, tanpa)

    def test_penalti_riwayat_meluruh(self):
        entri = {"lema": "dingin", "bahasa": "id", "register": ["netral"],
                 "tipe_semantik": ["ENTITAS"], "frekuensi": 0.5}
        segar = self.l2._skor(entri, self._slot(), GenContext())
        self.l2.riwayat[:] = ["dingin"]
        baru = self.l2._skor(entri, self._slot(), GenContext())
        self.l2.riwayat[:] = ["dingin"] + ["api"] * 5
        lama = self.l2._skor(entri, self._slot(), GenContext())
        self.assertLess(baru, segar)
        # pengulangan yang jauh lebih lama hukumannya lebih ringan
        self.assertGreater(lama, baru)

    def test_slot_mode_isi_boleh_kosong(self):
        from pycos.bahasa.tutur import Arg, L1, Node
        l1 = L1(self.leks)
        node = Node("MELIHAT", [
            Arg("EXPERIENCER", "ANIMAT", "aku"),
            Arg("OBJEK", "ENTITAS", None, mode="isi"),
        ])
        kerangka, catatan = l1.realisasi(node, GenContext())
        self.assertIsNotNone(kerangka, catatan)


class StrukturDanPartikelTest(unittest.TestCase):
    """F5/F6: variasi bentuk dan partikel menjaga register."""

    def setUp(self):
        self.engine = TuturEngine(path=jalur_leksikon())
        self.assertTrue(self.engine.tersedia())

    def _ucap(self, **kw):
        base = GenContext(act="menyatakan", topik="api",
                          register="netral", bahasa="id")
        ujaran = self.engine.ucap(dataclasses.replace(base, **kw))
        self.assertIsNotNone(ujaran)
        return ujaran

    def test_register_netral_tanpa_partikel(self):
        for seed in range(6):
            teks = self._ucap(seed=seed).teks
            for partikel in ("sih", "nih", "tuh", "dong", "kok", "deh", "kan"):
                kata = set(teks.replace(".", " ").replace("…", " ").split())
                self.assertNotIn(partikel, kata,
                                 "partikel {!r} bocor ke register netral: {!r}"
                                 .format(partikel, teks))

    def test_register_formal_tetap_formal(self):
        for seed in range(6):
            teks = self._ucap(seed=seed, register="formal",
                              emosi=("TAKUT",), arousal=0.9,
                              valensi=-0.8).teks
            self.assertTrue(teks.strip())
            self.assertNotIn(" nih", teks)
            self.assertNotIn(" tuh", teks)

    def test_sapaan_hanya_pada_act_akrab(self):
        sapa = ("Kak",)
        akrab = self._ucap(seed=0, act="kembali", register="akrab",
                           dekat=True, sapaan=sapa,
                           kata_favorit=("api",)).teks
        self.assertTrue(akrab.startswith("Kak, "), akrab)
        biasa = self._ucap(seed=0, act="menyatakan", register="akrab",
                           dekat=True, sapaan=sapa).teks
        self.assertFalse(biasa.startswith("Kak, "), biasa)

    def test_riwayat_tersimpan_dan_dimuat(self):
        self._ucap(seed=1)
        self._ucap(seed=2)
        data = self.engine.to_dict()
        self.assertTrue(data["riwayat"])
        self.assertLessEqual(len(data["riwayat"]), 32)
        lain = TuturEngine(path=jalur_leksikon())
        lain.muat_dict(data)
        self.assertEqual(data["riwayat"], lain.to_dict()["riwayat"])
        with self.assertRaises(ValueError):
            lain.muat_dict({"riwayat": "api"})   # bukan daftar


class KeterusteranganTest(unittest.TestCase):
    """F7/B11: 'mungkin' mengikuti keterusterangan persona."""

    def test_langsung_tanpa_mungkin(self):
        from pycos.bahasa.tutur import L3
        import random
        l3 = L3(_leksikon(), random.Random(3))
        from pycos.bahasa.tutur import Node
        node = Node("TAKUT")
        lunak = l3._penanda_aspek_modal(
            node, GenContext(doubt=0.5, keterusterangan="lunak"), None)
        netral = l3._penanda_aspek_modal(
            node, GenContext(doubt=0.5, keterusterangan="netral"), None)
        langsung = l3._penanda_aspek_modal(
            node, GenContext(doubt=0.9, keterusterangan="langsung"), None)
        self.assertIn("mungkin", lunak)
        self.assertNotIn("mungkin", netral)
        self.assertNotIn("mungkin", langsung)


if __name__ == "__main__":
    unittest.main()
