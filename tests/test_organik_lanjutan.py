# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
"""Uji regresi untuk residu, intrusi, selisih-diri, detak, dan koherensi.

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

from pycos.dukungan.patching import (PatchConflictError, install_methods,  # noqa: E402
                                     wrap_method)
from pycos.inti import Naluri  # noqa: E402
from pycos.mandiri import (KALIMAT_ADA_SESUATU, KALIMAT_TAK_BERNAMA,  # noqa: E402
                           DetakInternal, Gejala, GejalaMurni, Organik,
                           Residu)
from pycos.memori import JejakPrediksi  # noqa: E402


class SafeMethodPatchTest(unittest.TestCase):
    def test_wrapper_menjaga_chain_descriptor_dan_idempoten(self):
        class Target:
            @classmethod
            def load(cls, value):
                return "{}:{}".format(cls.__name__, value)

        def add_suffix(original, cls, value):
            return original(cls, value) + "!"

        self.assertTrue(wrap_method(
            Target, "load", add_suffix, patch_id="test.safe.load"))
        self.assertFalse(wrap_method(
            Target, "load", add_suffix, patch_id="test.safe.load"))
        self.assertEqual(Target.load("state"), "Target:state!")

    def test_benturan_batch_tidak_meninggalkan_pemasangan_sebagian(self):
        class Target:
            def occupied(self):
                return "original"

        with self.assertRaises(PatchConflictError):
            install_methods(
                Target,
                (("new_api", lambda self: "new"),
                 ("occupied", lambda self: "replacement")),
                patch_id="test.safe.batch",
            )

        self.assertFalse(hasattr(Target, "new_api"))
        self.assertEqual(Target().occupied(), "original")

    def test_integrasi_bayes_tidak_memutasi_metode_kelas_per_instance(self):
        jejak = JejakPrediksi()
        metode = JejakPrediksi.record_experience
        self.assertTrue(jejak._pasang_bayes())
        self.assertIs(JejakPrediksi.record_experience, metode)

        jejak.tetapkan_kepercayaan("pintu aman", 0.8)
        jejak.perbarui_kepercayaan("pintu aman", 0.5, label="bukti baru")
        pulih = JejakPrediksi.from_dict(jejak.to_dict())
        self.assertAlmostEqual(pulih.kepercayaan("pintu aman"),
                               jejak.kepercayaan("pintu aman"))


class ResiduTest(unittest.TestCase):
    def test_residu_mengubah_aturan_dan_tidak_decay(self):
        r = Residu()
        awal = r.daftar("kehilangan", "duka", 0.8, tick=1)
        self.assertTrue(awal["aktif"])
        self.assertGreater(r.ambang_dimodifikasi("senang", 0.02), 0.02)
        self.assertLess(r.langit_dimodifikasi("afiliasi", 1.0), 1.0)

        # Tidak ada langkah waktu/decay; pembacaan berulang identik.
        tekanan = r.tekanan()
        for _ in range(100):
            self.assertEqual(r.tekanan(), tekanan)

        lemah = r.daftar("kenangan lain", "duka", 0.4, tick=99)
        self.assertFalse(lemah["aktif"])
        self.assertEqual(r.tekanan(), tekanan)
        kuat = r.daftar("kehilangan kedua", "duka", 0.9, tick=100)
        self.assertTrue(kuat["aktif"])
        self.assertAlmostEqual(r.tekanan(), 0.9)

        patch = r.tambal("ritual perpisahan", "duka", 0.5, tick=101)
        self.assertTrue(patch["ditambal"])
        self.assertAlmostEqual(r.tekanan(), 0.45)
        self.assertIn("duka", r.state()["aktif"])  # ditambal, bukan dihapus

    def test_residu_terintegrasi_ke_emosi(self):
        n = Naluri(params={"enable_emosi": True})
        n.daftarkan_residu("kehilangan", "duka", 0.8)
        # Ambang senang naik: rangsangan kecil tak lagi mengaktifkannya.
        self.assertEqual(n._emosi_naikkan("senang", 0.2, "kabar baik kecil"), 0.0)
        self.assertLess(n._emosi_weight_bias("afiliasi"), 1.0)


class IntrusiTest(unittest.TestCase):
    def test_intrusi_menyampel_affective_tanpa_attend(self):
        n = Naluri(rng_seed=3, params={
            "enable_kesadaran": True,
            "enable_affective_memory": True,
        })
        n.daftarkan_residu("kehilangan rumah", "duka", 0.9)
        n.nurani.seed_affective(
            "bau hujan di rumah lama", {"afiliasi": -0.8, "koherensi": -0.4}, n=8)
        item = n.kesadaran.paksa_intrusi()
        self.assertIsNotNone(item)
        self.assertEqual(item["source"], "tanpa_sebab")
        self.assertTrue(item["datang_tanpa_sebab"])
        laporan = n.kesadaran.workspace_report()
        self.assertEqual(laporan["intrusi"][-1]["label"], "datang tanpa sebab")


class SelisihSelfTest(unittest.TestCase):
    def test_deviasi_berulang_menaikkan_disorientasi_identitas(self):
        n = Naluri(name="Rama", rng_seed=4, params={
            "enable_presentasi": True,
            "enable_kesadaran": True,
            "enable_emosi": True,
        })
        n.daftarkan_residu("kehilangan", "duka", 0.95)
        for _ in range(2):
            hasil = n.presentasi.ucap(
                kepada="Ayu", topik="hari ini", act="akrab", diam_boleh=False)
            self.assertIn("residu_duka", hasil["deviasi_self"])
        state = n.selisih_self_state()
        self.assertGreaterEqual(state["beruntun"], 2)
        self.assertGreater(state["disorientasi_identitas"], 0.0)
        self.assertGreater(n.kesadaran.doubt, 0.0)


class DetakInternalTest(unittest.TestCase):
    def test_jam_fraksional_dan_ucapan_terpotong_saat_ini(self):
        jam = DetakInternal()
        self.assertTrue(jam.paksa("mual"))
        ev = jam.maju(0.01, {"levels": {}, "felt": {}, "emosi": {}})
        self.assertEqual(ev[0]["proses"], "mual")

        n = Naluri(name="Rama", params={
            "enable_presentasi": True,
            "enable_kesadaran": True,
        })
        n.paksa_interupsi("mual")
        hasil = n.presentasi.ucap(
            kepada="Ayu", topik="cerita yang cukup panjang untuk dipotong",
            act="menyatakan", diam_boleh=False)
        self.assertEqual(hasil["terpotong_internal"], "mual")
        self.assertTrue(hasil["teks"].endswith("—"))
        self.assertEqual(n.interupsi_internal_state()["jumlah"], 1)


class KoherensiParalelTest(unittest.TestCase):
    def test_hanya_kontradiksi_tak_disadari_menghukum(self):
        params = {"enable_kesadaran": True, "enable_fallibility": True}
        biasa = Naluri(params=params)
        biasa.kesadaran.hold_belief("aku mencintainya", "aku membencinya")
        self.assertLess(biasa.levels["koherensi"], 0.0)

        paralel = Naluri(params=params)
        paralel.pegang_dua(
            "aku mencintainya", "aku membencinya",
            emosi_a={"afiliasi": 0.8}, emosi_b={"afiliasi": -0.8})
        sebelum = paralel.levels["koherensi"]
        hasil = paralel.kesadaran.hold_belief(
            "aku mencintainya", "aku membencinya")
        self.assertTrue(paralel.tanpa_resolusi())
        self.assertTrue(hasil["tanpa_resolusi"])
        self.assertEqual(hasil["tension"], 0.0)
        self.assertEqual(paralel.levels["koherensi"], sebelum)

        paralel.delta("koherensi", -0.4, reason="disonansi keyakinan")
        self.assertEqual(paralel.levels["koherensi"], sebelum)


class GejalaMurniOrdeNolTest(unittest.TestCase):
    """Orde nol: primitif minimal, tanpa properti terlarang."""

    def test_primitif_hanya_empat_properti(self):
        g = GejalaMurni(0.7, None, signature="t", tick=0)
        st = g.state()
        self.assertEqual(st["intensitas"], 0.7)
        self.assertIsNone(st["polaritas"], "arah boleh tak terdefinisi")
        self.assertTrue(st["tanpa_tipe"])
        self.assertTrue(st["menuntut"])
        self.assertGreater(st["tekanan"], 0.0, "menuntut = tak bisa diabaikan")
        # durasi/isi/sebab/tujuan secara eksplisit tidak dimiliki
        self.assertEqual(st["tidak_dimiliki"],
                         {"durasi": None, "isi": None, "sebab": None,
                          "tujuan": None})
        self.assertEqual(g.properti_terlarang(), [])

    def test_polaritas_none_bukan_gagal_dan_boleh_menyusul(self):
        g = GejalaMurni(0.5, None)
        g.perbarui(0.6, -0.4, tick=3)
        self.assertAlmostEqual(g.polaritas, -0.4)
        self.assertEqual(g.ulangan, 2)

    def test_pipeline_berulang_menjadi_kategori_penuh(self):
        ge = Gejala(ambang_ulang=2, proto_min_ulang=3, proto_min_umur=5,
                    memudar_ticks=3)
        ge.muncul(0.7, None, tanda="t", tick=0)
        ge.jenis_hint("t", "emosi")
        ge.proses(tick=1)
        ge.muncul(0.8, -0.3, tanda="t", tick=2)
        ge.muncul(0.6, None, tanda="t", tick=3)
        self.assertTrue(ge.proses(tick=4)["endapan"])
        self.assertEqual(ge.kategori_penuh(), [], "belum bertahan lama")
        ge.proses(tick=6)
        penuh = ge.kategori_penuh()
        self.assertEqual(len(penuh), 1)
        self.assertEqual(penuh[0]["jenis"], "emosi")
        self.assertIn("tidak bisa kujelaskan", penuh[0]["klaim_identitas"])

    def test_pemudaran_meniggalkan_bekas_bukan_entri_aktif(self):
        ge = Gejala(memudar_ticks=2)
        ge.muncul(0.5, None, tanda="sekilas", tick=0)
        keputusan = ge.proses(tick=5)
        self.assertTrue(keputusan["pemudaran"])
        self.assertEqual(ge.aktif(), [])
        self.assertEqual(ge.bekas()[-1]["catatan"], KALIMAT_ADA_SESUATU)
        self.assertEqual(ge.bekas()[-1]["signature"], "sekilas")

    def test_klaim_menghapus_kemurnian(self):
        ge = Gejala()
        ge.muncul(0.9, 0.4, tanda="kenal", tick=0)
        hasil = ge.klaim("kenal", "drive", "keamanan", kuat=0.8, tick=1)
        self.assertEqual(hasil["jenis"], "drive")
        self.assertEqual(ge.aktif(), [], "gejala terklaim tidak lagi baru")
        self.assertEqual(ge.terklaim()[-1]["kategori"], "keamanan")

    def test_roundtrip_wadah_membawa_gejala_dan_bekas(self):
        o = Organik(seed=5)
        o.gejala.muncul(0.6, None, tanda="t", tick=1)
        o.gejala.proses(tick=2)
        o.residu.bekas("gejala", KALIMAT_TAK_BERNAMA, tick=2, signature="t")
        o2 = Organik.from_dict(o.to_dict(), seed=5)
        self.assertEqual([g["signature"] for g in o2.gejala.aktif()], ["t"])
        self.assertEqual(o2.residu.bekas_state()[-1]["signature"], "t")
        self.assertEqual(o2.residu.tekanan(), 0.0,
                         "bekas bukan entri aktif")


class TopologiSlotTest(unittest.TestCase):
    def test_slot_kosong_membuat_cabang_mustahil_dan_roundtrip(self):
        from pycos.mandiri import TopologiSlot

        slot = TopologiSlot()
        slot.daftar("Ayu", {"relasi": "teman"}, tick=1)
        slot.kosongkan("Ayu", alasan="pindah", tick=2)

        self.assertIsNone(slot.intensitas("Ayu", skalar=0.8))
        self.assertEqual(["Ayu"], slot.cabang_mustahil("bertemu Ayu"))
        salinan = TopologiSlot.from_dict(slot.to_dict())
        self.assertEqual(slot.to_dict(), salinan.to_dict())


class LukaDomainTest(unittest.TestCase):
    def test_lubang_nonpermanen_dapat_ditambal_bukan_permanen(self):
        from pycos.mandiri import LukaDomain

        luka = LukaDomain()
        luka.lukai("Ayu", "uang", "hutang", tick=1, permanen=False)
        self.assertIsNone(luka.terapkan("Ayu", "uang", 0.8))
        self.assertTrue(luka.tambal("Ayu", "uang"))
        self.assertEqual(0.8, luka.terapkan("Ayu", "uang", 0.8))

        luka.lukai("Ayu", "kepercayaan", "pengkhianatan", tick=2)
        self.assertFalse(luka.tambal("Ayu", "kepercayaan"))
        self.assertIsNone(luka.terapkan("Ayu", "kepercayaan", 1.0))


class BatasIdentitasTest(unittest.TestCase):
    def test_identitas_menolak_dan_membatasi_emosi(self):
        from pycos.mandiri import BatasIdentitas

        batas = BatasIdentitas()
        batas.tetapkan("aku tidak menyakiti", {
            "marah": "tolak", "sedih": ("langit", 0.2)})
        self.assertEqual((False, 0.0, "aku tidak menyakiti"),
                         batas.izinkan("marah", 0.9))
        self.assertEqual((True, 0.2, "aku tidak menyakiti"),
                         batas.izinkan("sedih", 0.9))


class WaktuHeterogenTest(unittest.TestCase):
    def test_recall_koreksi_skala_dan_roundtrip(self):
        from pycos.mandiri import WaktuHeterogen

        waktu = WaktuHeterogen(dasar=100.0, min_=10.0, maks=500.0)
        self.assertEqual(100.0, waktu.daftar("episode"))
        self.assertEqual(135.0, waktu.diingat("episode"))
        self.assertEqual(94.5, waktu.dikoreksi_salah("episode"))
        self.assertEqual(0.5, waktu.skala_subjektif(
            "episode", 0.5, durasi_objektif=2.0, durasi_subjektif=1.0))
        self.assertEqual(47.25, waktu.half_life("episode"))
        self.assertAlmostEqual(0.5, waktu.bobot("episode", 47.25))
        self.assertEqual(waktu.to_dict(),
                         WaktuHeterogen.from_dict(waktu.to_dict()).to_dict())


class PenolakanTuturTest(unittest.TestCase):
    def test_takut_mengubah_bentuk_tutur_secara_reproduksibel(self):
        import random
        from pycos.mandiri import PenolakanTutur

        mekanisme = PenolakanTutur()
        skor, komponen = mekanisme.kelayakan({"takut": 1.0})
        self.assertLess(skor, mekanisme.ambang)
        self.assertEqual("takut", mekanisme.jenis(komponen))
        self.assertEqual("Aku… aku tidak—", mekanisme.bentuk(
            "Aku tahu jawabannya", random.Random(0), komponen))


class ApersepsiTest(unittest.TestCase):
    def test_tekanan_tinggi_tanpa_kategori_menghasilkan_tanpa_nama(self):
        from pycos.mandiri import Apersepsi

        apersepsi = Apersepsi()
        hasil = apersepsi.amati(
            {"aneh": 0.5, "asing": 0.4}, {"keamanan": 0.9},
            dikenal=["sedih"])
        self.assertEqual("tanpa_nama", hasil["modus"])
        self.assertIsNone(hasil["nama"])
        self.assertEqual("ada sesuatu di dalam diriku yang belum punya nama.",
                         hasil["kalimat"])


class InvensiTest(unittest.TestCase):
    def test_lahirkan_menghasilkan_usulan_deterministik(self):
        from pycos.mandiri import Invensi

        digest = {
            "keyakinan": ["aku takut api", "pintu tidak aman"],
            "episode": ["asap memenuhi lorong", "aku berlari keluar"],
            "asosiasi": [("asap", "bahaya", 0.8), ("api", "bahaya", 0.9)],
            "konsep": ["asap", "bahaya", "api"],
            "tujuan": ["keluar dari api"],
            "drives": {"keamanan": 0.9}, "emosi": {"takut": 0.9},
        }
        hasil = Invensi(seed=5).lahirkan(digest, tick=7)

        self.assertTrue(hasil)
        self.assertEqual(hasil, Invensi(seed=5).lahirkan(digest, tick=7))
        self.assertTrue(all(s["status"] == "usul" and s["tick"] == 7
                            for s in hasil))


class ModelKausalTest(unittest.TestCase):
    def test_pelajari_penjelasan_counterfactual_blame_dan_roundtrip(self):
        from pycos.mandiri import ModelKausal

        model = ModelKausal(seed=9)
        model.pelajari([{
            "stimulus": "lorong berasap", "action": "menyalakan kipas",
            "impact": 0.9, "drive_deltas": {"keamanan": -0.6},
            "label": "asap hilang",
        }])
        penjelasan = model.jelaskan("asap hilang")
        kontrafaktual = model.counterfactual(
            "lorong berasap", "menyalakan kipas")
        atribusi = model.blame(
            "lorong berasap", "menyalakan kipas", "asap hilang")

        self.assertIn("a:menyalakan kipas", [x["node"]
                                               for x in penjelasan["rantai"]])
        self.assertTrue(kontrafaktual["mekanisme"])
        self.assertEqual("aksi", atribusi["sebab"])
        pulih = ModelKausal.from_dict(model.to_dict(), seed=9)
        self.assertEqual(penjelasan, pulih.jelaskan("asap hilang"))


class PerencanaOutcomeTokenTest(unittest.TestCase):
    def test_frasa_multi_kata_menutupi_prasyarat_dan_rencana_lengkap(self):
        from pycos.mandiri import ModelKausal, Perencana

        domain = ModelKausal()
        domain._tepi("s:kunci ditemukan", "a:buka pintu", 0.8)
        domain._tepi("a:buka pintu", "h:pintu terbuka", 0.9)
        domain._tepi("s:pintu terkunci", "a:ambil kunci", 0.8)
        domain._tepi("a:ambil kunci", "h:kunci ditemukan", 0.9)

        perencana = Perencana(seed=3)
        pohon = perencana.rancang(
            "pintu terbuka", domain, ["s:pintu terkunci"])

        self.assertTrue(pohon["lengkap"], pohon["akar"])
        pra = pohon["akar"]["pra"][0]
        self.assertEqual("h:kunci ditemukan", pra["via"])
        self.assertEqual("a:ambil kunci", pra["pra"][0]["aksi"])


if __name__ == "__main__":
    unittest.main()
