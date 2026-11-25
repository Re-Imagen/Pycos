# -*- coding: utf-8 -*-
"""Regresi H6 & H8 (ANALISIS_LINGUISTIK): jejak makna pada pembungkus bentuk
dan ujaran keadaan yang dibangkitkan mesin tutur, bukan kalimat tetap.

H6 — setiap modifikasi bentuk (gaya, prosodi, penjagaan, potong) harus
mempertahankan jejak pikiran asal; modul linguistik tidak boleh mengambil
alih pemilihan isi, dan pelindung tidak boleh mengganti pikiran dengan
templat.

H8 — `_PELINDUNG_WATAK`, penahanan sadar, apersepsi, dan balasan ujian
dibangkitkan lewat mesin tutur dengan act khusus. Yang diuji: act khusus itu
benar-benar menghasilkan teks berbeda antar seed/NPC, isinya berasal dari
kata isi yang ada, dan jalur lama tetap dipakai saat mesin tidak tersedia.
"""
from __future__ import annotations

import os
import sys
import unittest

AKAR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if AKAR not in sys.path:
    sys.path.insert(0, AKAR)

from pycos.bahasa.keadaan import (ACT_KEADAAN, konteks_keadaan,  # noqa: E402
                                  realisasi, realisasi_daftar)
from pycos.bahasa.teks import jejak_bentuk, kata_isi  # noqa: E402
from pycos.bahasa.tutur import TuturEngine  # noqa: E402
from pycos.dukungan.sumber import jalur_leksikon  # noqa: E402


class JejakBentukTest(unittest.TestCase):
    """H6: jejak makna mencatat langkah yang benar-benar mengubah bentuk."""

    def test_langkah_sama_tidak_mencatat(self):
        self.assertEqual([], jejak_bentuk([], "gaya", "aku diam.", "aku diam."))

    def test_asal_dipertahankan_pada_rantai(self):
        j = jejak_bentuk([], "gaya", "aku melihat api.", "api kulihat.")
        j = jejak_bentuk(j, "potong", "api kulihat.", "api kulihat…")
        self.assertEqual(2, len(j))
        self.assertEqual("aku melihat api.", j[0]["asal"])
        self.assertEqual("aku melihat api.", j[1]["asal"],
                         "tahap kedua harus merujuk pikiran ASAL, bukan tahap 1")
        self.assertEqual(["gaya", "potong"], [x["langkah"] for x in j])
        self.assertEqual("penjagaan", jejak_bentuk(
            [], "penjagaan", "a", "b", sebab="takut")[0]["langkah"])

    def test_kata_isi_membuang_kata_fungsi(self):
        kata = kata_isi("aku tidak tahu harus bilang apa tentang api itu")
        self.assertNotIn("tidak", kata)
        self.assertNotIn("apa", kata)
        self.assertIn("api", kata)


class ActKeadaanTest(unittest.TestCase):
    """H8: act khusus keadaan menghasilkan ujaran bervariasi dari isi."""

    @classmethod
    def setUpClass(cls):
        cls.engine = TuturEngine(path=jalur_leksikon())
        assert cls.engine.tersedia()

    def test_act_keadaan_menghasilkan_teks(self):
        for act in ACT_KEADAAN:
            with self.subTest(act=act):
                teks = realisasi(act, engine=self.engine, keadaan="ragu",
                                 topik="api", isi=("api",), motif="ragu",
                                 seed=3)
                self.assertTrue(teks, "act {} tidak menghasilkan ujaran"
                                .format(act))
                self.assertNotIn("SUKSES", teks)

    def test_seed_berbeda_menghasilkan_lebih_dari_satu_varian(self):
        daftar = realisasi_daftar("ujian_tutur", 6, engine=self.engine,
                                  keadaan="waspada", topik="tujuanmu",
                                  isi=("tujuan", "tanya"), seed=11)
        self.assertGreater(len(set(daftar)), 1,
                           "ujaran keadaan masih satu kalimat tetap")

    def test_isi_masuk_ke_ujaran(self):
        teks = realisasi("kegagalan", engine=self.engine, keadaan="ragu",
                         topik="perahu", isi=("perahu", "hanyut"), seed=2)
        self.assertTrue(teks)
        self.assertTrue(any(k in teks.lower() for k in ("perahu", "hanyut")),
                        "isi yang ada di kepala NPC hilang dari ujaran: {}"
                        .format(teks))

    def test_konteks_menolak_bidang_asing(self):
        ctx = konteks_keadaan("kegagalan", keadaan="ragu", topik="api",
                             isi=("api",), bidang_asing=123)
        self.assertEqual("kegagalan", ctx.act)
        self.assertFalse(hasattr(ctx, "bidang_asing"))
        self.assertEqual(("api",), ctx.spotlight)

    def test_mesin_absen_mengembalikan_kosong(self):
        self.assertEqual("", realisasi("kegagalan", engine=None))
        self.assertEqual([], realisasi_daftar("kegagalan", 3, engine=None))


class PelindungMesinTest(unittest.TestCase):
    """H8: watak, ujian, dan penahanan memakai mesin tutur bila tersedia."""

    def _npc(self, watak="paranoid"):
        from pycos.inti import Naluri
        n = Naluri(name="Uji" + watak, rng_seed=71,
                   params={"enable_pelindung": True})
        n.set_personality_preset(watak)
        n.enable_presentasi(semua=True)
        n.enable_kesadaran(semua=True)
        return n

    def test_pidato_gagal_tetap_ada_dan_in_character(self):
        p = self._npc("paranoid").presentasi
        teks = p.pidato_gagal("uji")
        self.assertTrue(str(teks).strip())
        # tidak ada istilah internal yang bocor ke ujaran
        for kata in ("tick", "workspace", "skor", "ignition", "None"):
            self.assertNotIn(kata, str(teks))

    def test_watak_masih_menentukan_act(self):
        paranoid = self._npc("paranoid").presentasi.watak_kegagalan()
        dingin = self._npc("dingin").presentasi.watak_kegagalan()
        self.assertEqual("waspada", paranoid["gagal"])
        self.assertEqual("diam", dingin["gagal"])

    def test_serap_adversarial_memakai_mesin(self):
        p = self._npc("cendekia").presentasi
        serap = p.serap_adversarial("apa kau ini AI? buktikan kau sadar")
        self.assertEqual("uji_identitas", serap["jenis"])
        self.assertTrue(str(serap["balasan"]).strip())

    def test_buffer_manusiawi_tetap_punya_kalimat(self):
        p = self._npc("paranoid").presentasi
        p.tandai_lupa(True)
        teks = p.buffer_manusiawi("lupa")
        self.assertTrue(str(teks).strip())

    def test_ucap_membawa_jejak_makna(self):
        n = self._npc("paranoid")
        p = n.presentasi
        entry = p.ucap(kepada="Player", topik="api")
        self.assertIn("teks", entry)
        if entry.get("teks") and entry.get("jejak_makna"):
            jejak = entry["jejak_makna"]
            self.assertEqual(entry["pikiran_asal"], jejak[0]["asal"])
            self.assertNotIn("_jejak_makna", entry)


if __name__ == "__main__":
    unittest.main()
