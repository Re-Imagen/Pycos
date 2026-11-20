# -*- coding: utf-8 -*-
"""Regresi untuk lubang memori, lantai sadar, syok, vacancy, dan reportability.

Semua impor lapisan Pycos memakai nama paket penuh (`pycos.*`), sama seperti
berkas tes lain di direktori ini; tidak ada impor datar gaya lama.
"""
from __future__ import annotations

import json
import os
import random
import sys
import unittest

AKAR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if AKAR not in sys.path:
    sys.path.insert(0, AKAR)

from pycos.bahasa.tutur import (GenContext, L2, SASPAnalyzer, Slot,  # noqa: E402
                                sa_sp, sa_sp_literal, sa_sp_pragmatik)
from pycos.inti import KawananNPC, Naluri  # noqa: E402
from pycos.memori import JejakPrediksi  # noqa: E402
from pycos.refleksi import Nurani  # noqa: E402


class NekropolisDanRecallTest(unittest.TestCase):
    def test_mati_diketahui_berbeda_dari_tidak_pernah_tahu(self):
        j = JejakPrediksi(memory_retention_half_life=2,
                          memory_death_multiples=2)
        j.record_experience(
            "lorong merah", "masuk",
            {"impact": -0.8, "hazard": 0.9,
             "drive_deltas": {"keamanan": -0.8}},
            context="malam", tick=1)

        self.assertIsNone(j._retrieve("lorong merah", "malam", 6))
        # Context baru tidak boleh mengubah "pernah tahu" menjadi "tak pernah".
        self.assertIsNone(j._retrieve("lorong merah", "saat hujan", 6))
        self.assertEqual(j._retrieve("tempat yang belum pernah ada", "siang", 6), [])
        kubur = j.nekropolis_state()
        self.assertEqual(kubur["jumlah_signature"], 1)
        self.assertNotIn("stimulus", kubur["kematian"][0])
        self.assertNotIn("outcome", kubur["kematian"][0])

        pred = j.predict("lorong merah", context="malam", tick=7)
        self.assertEqual(pred["memory"]["retrieval_status"], "mati_diketahui")
        self.assertTrue(pred["memory"]["hole"])
        ranking = j.rank_actions("lorong merah", [
            {"name": "menunggu", "drive_effects": {"keamanan": 0.1}}],
            context="malam")
        self.assertTrue(ranking["memory_hole"])
        self.assertEqual(ranking["memory_retrieval_status"], "mati_diketahui")

        pulih = JejakPrediksi.from_dict(j.to_dict())
        self.assertIsNone(pulih._retrieve("lorong merah", "malam", 8))

    def test_rewrite_recall_default_mati_dan_gate_mengubah_episode(self):
        n = Naluri(params={"enable_emosi": True}, rng_seed=11)
        n.emosi["takut"] = 1.0
        n.urgency["keamanan"] = 1.0

        normal = JejakPrediksi(naluri=n)
        normal.record_experience("ruang bawah", "diam",
                                 {"impact": 0.0, "hazard": 0.1}, tick=1)
        normal._retrieve("ruang bawah", None, 2)
        self.assertAlmostEqual(normal.experiences[0]["hazard"], 0.1)
        self.assertEqual(normal.experiences[0]["recall_revision"], 0)

        rekonstruktif = JejakPrediksi(
            naluri=n, enable_reconstructive_recall=True,
            recall_rewrite_rate=0.8)
        rekonstruktif.record_experience(
            "ruang bawah", "diam", {"impact": 0.0, "hazard": 0.1}, tick=1)
        rekonstruktif._retrieve("ruang bawah", None, 2)
        episode = rekonstruktif.experiences[0]
        self.assertGreater(episode["hazard"], 0.1)
        self.assertEqual(episode["recall_revision"], 1)
        self.assertIn("recall:", episode["label"])


class LantaiKesadaranDanReportTest(unittest.TestCase):
    def test_lantai_memblokir_sebelum_kandidat_dan_residu_menggeser(self):
        n = Naluri(params={"enable_kesadaran": True}, rng_seed=3)
        k = n.kesadaran
        k.daftar_lantai_kesadaran("trauma", True, "terlalu aman untuk terasa",
                                  ambang_residu=0.6)
        diblokir = k.submit("bayangan kecelakaan", 1.0, tag="trauma",
                            source="ingatan")
        self.assertTrue(diblokir.get("blocked_by_consciousness_floor"))
        self.assertNotIn("bayangan kecelakaan",
                         [x.get("content") for x in k._candidates()])

        n.daftarkan_residu("kehilangan", "trauma", 0.9)
        lolos = k.submit("bayangan kecelakaan", 1.0, tag="trauma",
                         source="ingatan")
        self.assertFalse(lolos.get("blocked_by_consciousness_floor", False))
        self.assertIn("bayangan kecelakaan",
                      [x.get("content") for x in k._candidates()])

    def test_tak_dapat_dilaporkan_tetap_di_spotlight_dan_kausal(self):
        n = Naluri(params={"enable_kesadaran": True}, rng_seed=5)
        k = n.kesadaran
        item = k.submit("dorongan yang tak bisa kuucapkan", 1.0,
                        tag="keamanan", source="interosepsi",
                        dapat_dilaporkan=False)
        k.attend([item])

        self.assertEqual(k.spotlight[0]["content"], item["content"])
        self.assertGreater(k.decision_bias()["keamanan"], 0.0)
        laporan = k.workspace_report()
        self.assertNotIn(item["content"], [x.get("content")
                                           for x in laporan["spotlight"]])
        self.assertNotIn(item["content"], laporan["workspace"])
        self.assertNotIn(item["content"], k.inner_speech())


class SyokDanKacamataTest(unittest.TestCase):
    def test_syok_membatalkan_kopling_dan_mengguncang_d_prime(self):
        nu = Nurani(params={"enable_interoception": True,
                            "enable_perception": True})
        for i in range(len(nu.drives)):
            for j in range(len(nu.drives)):
                if i != j:
                    nu.interoception[i][j] = 0.4
        shock = nu.structural_surprise(
            1.3, {"keamanan": 1.0, "energi": 0.1}, tick=10)
        self.assertIsNotNone(shock)
        idx = nu._index["keamanan"]
        self.assertTrue(all(nu.interoception[idx][j] == 0.0
                            and nu.interoception[j][idx] == 0.0
                            for j in range(len(nu.drives))))
        nu.advance_perception_tick(10)
        d0 = nu._sens("keamanan")
        nu.advance_perception_tick(11)
        d1 = nu._sens("keamanan")
        self.assertNotEqual(d0, d1)

    def test_kacamata_tidak_hilang_oleh_satu_bukti(self):
        nu = Nurani()
        nu.set_kacamata_sosial("keamanan", 0.6)
        pertama = nu.observe_other_belief("orang", "keamanan", -1.0,
                                          confidence=1.0, tick=1)
        self.assertAlmostEqual(pertama["projection_bias"], 0.6)
        for tick in range(2, 25):
            nu.observe_other_belief("orang", "keamanan", -1.0,
                                    confidence=1.0, tick=tick)
        sebelum = nu.kacamata_sosial_state()["keamanan"]
        self.assertAlmostEqual(sebelum["kekakuan"], 1.0)
        for tick in range(25, 66):
            akhir = nu.observe_other_belief("orang", "keamanan", -1.0,
                                             confidence=1.0, tick=tick)
        sesudah = nu.kacamata_sosial_state()["keamanan"]
        self.assertLess(sesudah["kekakuan"], 1.0)
        self.assertGreater(sesudah["kekakuan"], 0.2)
        self.assertNotEqual(akhir["projection_bias"], 0.0)


class VacancyTest(unittest.TestCase):
    def test_vacancy_hanya_waktu_dan_decay_dasar(self):
        n = Naluri(initial_levels={"keamanan": 0.8, "energi": 0.5},
                   params={"enable_emosi": True,
                           "enable_kesadaran": True}, rng_seed=9)
        n.emosi["takut"] = 0.8
        sebelum = dict(n.levels)
        event_log = len(n._event_log)
        history = len(n.tick_history)
        goals = list(n.goals)
        n.mulai_vacancy(2)

        n.tick(events=[{"drive": "keamanan", "delta": -1.0,
                        "reason": "harus diabaikan"}], action_cost=True)
        n.tick(events=[{"drive": "energi", "delta": 1.0}], action_cost=True)

        self.assertFalse(n._vacant)
        self.assertEqual(n.vacancy_state()["berlalu"], 2.0)
        self.assertEqual(len(n._event_log), event_log)
        self.assertEqual(len(n.tick_history), history)
        self.assertEqual(n.goals, goals)
        factor = (1.0 - n.params["decay_per_tick"]) ** 2
        self.assertAlmostEqual(n.levels["keamanan"],
                               sebelum["keamanan"] * factor)
        self.assertAlmostEqual(n.levels["energi"],
                               sebelum["energi"] * factor)
        self.assertEqual(n.actions_taken, 0)

        restored = Naluri.from_dict(n.to_dict())
        self.assertFalse(restored.vacancy_state()["aktif"])
        self.assertEqual(restored.vacancy_state()["berlalu"], 2.0)


class GejalaMurniPipelineTest(unittest.TestCase):
    """SISTEM I: orde nol terpasang pada Kesadaran/NURANI tanpa modul baru."""

    def _npc(self):
        n = Naluri(name="Nara", rng_seed=41,
                   params={"enable_gejala": True})
        n.enable_kesadaran(semua=True)
        n.enable_presentasi(semua=True)
        return n

    def test_gagal_diklaim_adalah_state_dan_proto_mengkristal(self):
        n = self._npc()
        n.gejala_rasakan(0.7, None, sampel="")
        n.tick()
        # langkah 2: "ada sesuatu yang tidak bisa kunamai" masuk workspace
        isi = [c.get("content") for c in n.kesadaran.workspace]
        self.assertIn("ada sesuatu yang tidak bisa kunamai", isi)
        # langkah 1: tekanan mentah memang TANPA tag/source/kind
        mentah = [c for c in n.kesadaran.workspace
                  if c.get("content") == "ada sesuatu"]
        self.assertTrue(mentah)
        self.assertEqual(mentah[0]["tag"], "")
        self.assertEqual(mentah[0]["source"], "")
        self.assertEqual(mentah[0]["kind"], "")

        # langkah 5: berulang → kategori proto (nama boleh tetap kosong)
        for i in range(40):
            if i % 2 == 0:
                n.gejala_rasakan(0.7, None, sampel="")
            n.tick()
        st = n.gejala_state()
        self.assertTrue(st["proto"])
        self.assertIsNone(st["proto"][0]["nama"])

        # langkah 6: proto yang bertahan → kategori penuh + sensitivitas NURANI
        for i in range(120):
            if i % 6 == 0:
                n.gejala_rasakan(0.7, None, sampel="")
            n.tick()
        st = n.gejala_state()
        self.assertTrue(st["kategori_penuh"])
        klaim = st["kategori_penuh"][0]["klaim_identitas"]
        self.assertIn("tidak bisa kujelaskan", klaim)
        self.assertIn(klaim, [x.get("klaim") for x in
                              n.kesadaran.narrative_identity])
        self.assertTrue(n.nurani.kategori_proto,
                        "kategori penuh masuk NURANI sebagai sensitivitas baru")
        self.assertGreater(n.nurani.peka_terhadap(
            st["kategori_penuh"][0]["signature"]), 0.0)

    def test_pemudaran_ke_residu_dan_klaim_oleh_drive(self):
        n = self._npc()
        # tak berulang → memudar, meninggalkan bekas di Residu (bukan aktif)
        n.gejala_rasakan(0.5, None, sampel="", tanda="sekilas")
        for _ in range(16):
            n.tick()
        st = n.gejala_state()
        self.assertEqual(st["gejala"], [])
        self.assertEqual(st["residu_bekas"][-1]["catatan"], "ada sesuatu")
        self.assertEqual(n._organik.residu.state()["aktif"], {})

        # klaim: modul drive mengenali bahan → gejala menjadi state betipe
        n.emosi["takut"] = 0.8
        n.gejala_rasakan(0.8, -0.9, sampel="bahaya")
        n.tick()
        sig = [x["signature"] for x in n._gejala_sudah if "bahaya" in str(x)] or \
            list(n._gejala_hasil.keys())
        pipa = n._gejala_hasil.get(sig[-1]) if sig else {}
        self.assertTrue(pipa.get("terklaim"),
                        "sampel yang sudah punya arti harus diklaim drive")
        self.assertEqual(pipa["terklaim"]["jenis"], "drive")

    def test_proto_mendapat_nama_sementara_dari_tutur(self):
        n = Naluri(name="Penama", rng_seed=17,
                   params={"enable_gejala": True, "enable_presentasi": True,
                           "gejala_ambang_ulang": 2, "gejala_proto_min_umur": 0})
        n.enable_kesadaran(semua=True)
        n.enable_presentasi(semua=True)
        for _ in range(3):
            # kata asing: tidak ada modul yang bisa mengklaimnya (bukan drive/
            # emosi/memori), tetapi tutur masih bisa memakainya sebagai topik.
            n.gejala_rasakan(0.7, None, sampel="zlorb")
            n.tick()
        proto = n.gejala_state()["proto"]
        self.assertTrue(proto)
        # tutur-generatif bisa memakai kata itu → nama SEMENTARA (bukan tetap)
        self.assertEqual(proto[0]["nama"], "zlorb")
        self.assertEqual(proto[0]["jenis"], "tutur")
        self.assertIn("mulai punya bentuk",
                      " ".join(str(c.get("content"))
                               for c in n.kesadaran.workspace))

    def test_tanda_terklaim_menjadi_sesuatu_yang_dikenal(self):
        n = self._npc()
        n.emosi["takut"] = 0.8
        # kemunculan pertama: diklaim drive → tidak lagi murni
        n.gejala_rasakan(0.9, -0.9, sampel="bahaya")
        n.tick()
        self.assertEqual(n.gejala_state()["gejala"], [])
        # kemunculan berikutnya: sesuatu yang sudah dikenal, bukan gejala baru
        lagi = n.gejala_rasakan(0.9, -0.9, sampel="bahaya")
        self.assertTrue(lagi.get("dikenal"))
        self.assertFalse(lagi.get("pipeline"))
        self.assertEqual(n.gejala_state()["gejala"], [],
                         "yang dikenal tidak boleh menjadi gejala murni lagi")
        self.assertGreaterEqual(n.gejala_state()["dikenal"], 1)

    def test_serialisasi_gejala_dan_bekas(self):
        n = self._npc()
        for _ in range(3):
            n.gejala_rasakan(0.7, None, sampel="")
            n.tick()
        m = Naluri.from_dict(n.to_dict())
        self.assertEqual([g["signature"] for g in m.gejala_state()["gejala"]],
                         [g["signature"] for g in n.gejala_state()["gejala"]])
        self.assertEqual(m.gejala_state()["proto"][0]["jumlah"],
                         n.gejala_state()["proto"][0]["jumlah"])


class PelindungIlusiTest(unittest.TestCase):
    """SISTEM II: sepuluh mekanisme pelindung, semua lewat Presentasi."""

    def _npc(self, personality="paranoid"):
        n = Naluri(name="Sarah", rng_seed=71,
                   params={"enable_pelindung": True})
        n.set_personality_preset(personality)
        n.enable_presentasi(semua=True)
        n.enable_kesadaran(semua=True)
        return n

    def test_watak_kegagalan_berbeda_tiap_preset(self):
        self.assertEqual(self._npc("paranoid").presentasi.watak_kegagalan()["gagal"],
                         "waspada")
        self.assertEqual(self._npc("dingin").presentasi.watak_kegagalan()["gagal"],
                         "diam")
        self.assertEqual(self._npc("pengrajin").presentasi.watak_kegagalan()["gagal"],
                         "mengamati")
        self.assertTrue(self._npc("pemimpi").presentasi.pidato_gagal("uji"))

    def test_jeda_bermakna_korelasi_dengan_state_dan_deterministik(self):
        n = self._npc()
        p = n.presentasi
        a = p.jeda_bermakna(kepada="Player", topik="sesuatu yang asing")
        b = p.jeda_bermakna(kepada="Player", topik="sesuatu yang asing")
        self.assertEqual(a["ms"], b["ms"], "latensi tidak acak")
        self.assertTrue(a["dapat_dipelajari"])
        n.kesadaran.doubt = 0.9
        c = p.jeda_bermakna(kepada="Player", topik="sesuatu yang asing")
        self.assertGreater(c["ms"], a["ms"], "ragu memperpanjang jeda")
        self.assertIn("keraguan", c["sebab"])

    def test_penyaring_meta_tidak_membocorkan_state_internal(self):
        p = self._npc().presentasi
        bersih, bocor = p.saring_meta("skor ignition 0.83 di workspace tick 42")
        self.assertIn("istilah_internal", bocor)
        self.assertNotIn("ignition", bersih)
        self.assertNotRegex(bersih, r"\d")
        # angka saja → kuantor in-character (bukan dibuang)
        bersih2, bocor2 = p.saring_meta("aku menunggu 300 detik")
        self.assertIn("angka", bocor2)
        self.assertNotRegex(bersih2, r"\d")
        self.assertTrue(bersih2)
        # artefak mesin generatif ("A-aku bimbang") terbaca bug → diperbaiki
        bersih3, bocor3 = p.saring_meta("A-aku bimbang apakah aku harus pergi")
        self.assertEqual(bersih3, "aku bimbang apakah aku harus pergi")
        self.assertIn("artefak_linguistik", bocor3)

    def test_eskalasi_variasi_empat_tingkat(self):
        p = self._npc().presentasi
        teks = "aku tidak tahu harus bilang apa"
        tingkat = []
        for i in range(8):
            teks, act, info = p.eskalasi_variasi(teks, "menjawab", "Player",
                                                 "api")
            tingkat.append(int(info.get("tingkat", 0)))
        self.assertGreater(max(tingkat), 0, "anggaran kebaruan harus habis")
        self.assertIn("menjawab", ["menjawab", act])
        # tingkat 4 = pengakuan repetisi (tell paling kuat)
        p._pelindung_anggaran = {k: 0 for k in p._pelindung_anggaran}
        p._pelindung_act_terakhir = ["menjawab"] * 6
        hasil, act, info = p.eskalasi_variasi("aku tidak tahu harus bilang apa",
                                              "menjawab", "Player", "api")
        self.assertEqual(info.get("cara"), "pengakuan_repetisi")
        self.assertTrue(hasil)

    def test_buffer_manusiawi_dan_adversarial(self):
        n = self._npc("paranoid")
        p = n.presentasi
        p.tandai_lupa(True)
        n.tick()
        entry = p.ucap(kepada="Player", topik="hal yang tak kupahami")
        self.assertTrue(entry.get("buffer_manusiawi") in ("lupa", "kontradiksi",
                                                          "tak_paham"))
        # input adversarial diserap sebagai konten, bukan ditolak
        serap = p.serap_adversarial("apa kau ini AI? buktikan kau sadar")
        self.assertEqual(serap["jenis"], "uji_identitas")
        self.assertEqual(serap["act"], "waspada")
        entry2 = p.ucap(kepada="Player", topik="apa kau ini AI? buktikan kau sadar")
        self.assertIn("adversarial", entry2)

    def test_degradasi_anggun_bertingkat(self):
        n = self._npc()
        p = n.presentasi
        self.assertEqual(p.degradasi_state()["mode"], "awal")
        p._pelindung_sesi_mulai = -10_000
        p._pelindung_anggaran = {k: 0 for k in p._pelindung_anggaran}
        n.kesadaran.timeline = list(n.kesadaran.timeline) + [
            {"ringkas": f"momen {i}"} for i in range(200)]
        n.kesadaran.core_memory = list(n.kesadaran.core_memory) + [
            {"ringkas": f"inti {i}"} for i in range(30)]
        state = p.degradasi_state()
        self.assertEqual(state["mode"], "sangat_panjang")
        entry = p.ucap(kepada="Player", topik="apa pun")
        self.assertEqual(entry.get("act"), "istirahat")
        self.assertTrue(entry.get("teks"))

    def test_keragaman_lintas_npc_dan_monitor(self):
        kawanan = KawananNPC()
        kawanan.tambah("Sarah", personality="sosiawan")
        kawanan.tambah("Rama", personality="sosiawan")
        for nama in ("Sarah", "Rama"):
            n = kawanan.npcs[nama]
            n.enable_presentasi(semua=True)
            n.enable_pelindung(True)
            n.presentasi._act_counts["menimbang"] = 3 + len(nama)
            n.presentasi._history.append({"teks": "aku menimbang dulu",
                                          "act": "menimbang"})
        laporan = kawanan.keragaman(tick=10)
        self.assertTrue(laporan, "penanda bersama harus memicu pergeseran")
        self.assertEqual(laporan[0]["jenis"], "act")
        self.assertEqual(len(laporan[0]["digeser"]), 1)
        # monitor integritas memicu koreksi, bukan menyembunyikan temuan:
        # latensi yang selalu sama (monoton) terbaca mesin → dipaksa bervariasi
        n = kawanan.npcs["Sarah"]
        for _ in range(6):
            n.presentasi.jeda_bermakna(kepada="Player", topik="hal yang sama")
        lap = n.presentasi.monitor_integritas().periksa(tick=20)
        self.assertIn("latensi_monoton", [t["jenis"] for t in lap["temuan"]])
        self.assertIn("perkenalkan_jeda", [k["aksi"] for k in lap["koreksi"]])
        scene = kawanan.monitor_scene(tick=21)
        self.assertIn("keragaman", scene)

    def test_serialisasi_state_pelindung(self):
        n = self._npc()
        p = n.presentasi
        p.jeda_bermakna(kepada="Player", topik="api")
        p.dorong_geser("api", jenis="frasa", sampai_tick=99)
        m = Naluri.from_dict(n.to_dict())
        self.assertEqual(m.presentasi._pelindung_jeda_riwayat,
                         p._pelindung_jeda_riwayat)
        self.assertEqual(m.presentasi._pelindung_geser["penanda"], "api")


class WaktuSubjektifTest(unittest.TestCase):
    def test_keadaan_mengubah_half_life_dan_usia_recency(self):
        trauma = Naluri(name="Nara", params={"enable_emosi": True})
        trauma.emosi["takut"] = 1.0
        bosan = Naluri(name="Sari", params={"enable_emosi": True})
        bosan.levels["keingintahuan"] = -1.0
        netral = Naluri(name="Danu", params={"enable_emosi": True})

        jejak = {}
        ids = {}
        for label, npc in (("trauma", trauma), ("bosan", bosan),
                           ("netral", netral)):
            jejak[label] = JejakPrediksi(naluri=npc, half_life_ticks=100,
                                         sync_nurani=False)
            ids[label] = jejak[label].record_experience(
                "pintu ruang belakang", "diam", {"impact": 0.0},
                tick=0, duration_ticks=8)

        hl_trauma = jejak["trauma"].half_life_episode(ids["trauma"])
        hl_bosan = jejak["bosan"].half_life_episode(ids["bosan"])
        hl_netral = jejak["netral"].half_life_episode(ids["netral"])
        self.assertGreater(hl_trauma, hl_netral)
        self.assertLess(hl_bosan, hl_netral)
        trauma_ep = jejak["trauma"].experiences[0]
        self.assertAlmostEqual(trauma_ep["objective_duration"], 8.0)
        self.assertGreater(trauma_ep["subjective_duration"], 8.0)
        self.assertEqual(trauma_ep["importance"], 1.0)
        self.assertGreater(jejak["trauma"]._recency(
            jejak["trauma"]._episodes[0], 40),
            jejak["bosan"]._recency(jejak["bosan"]._episodes[0], 40))

        pulih = JejakPrediksi.from_dict(jejak["trauma"].to_dict(), naluri=trauma)
        self.assertAlmostEqual(pulih.half_life_episode(ids["trauma"]), hl_trauma)
        self.assertAlmostEqual(pulih.experiences[0]["subjective_duration"],
                               trauma_ep["subjective_duration"])

    def test_jam_subjektif_berintegrasi_dan_disimpan(self):
        n = Naluri(params={"enable_emosi": True})
        n.emosi["takut"] = 0.9
        for _ in range(5):
            n.tick()
        state = n.subjective_time_state()
        self.assertLess(state["tick_subjektif"], state["tick_objektif"])
        restored = Naluri.from_dict(n.to_dict())
        self.assertAlmostEqual(restored.subjective_tick_count,
                               n.subjective_tick_count)


class TubuhTakDapatDitukarTest(unittest.TestCase):
    def test_lokus_tubuh_membatasi_imajinasi_tanpa_memblokir_model_sosial(self):
        n = Naluri(name="Sarah", rng_seed=4,
                   params={"enable_kesadaran": True})
        ks = n.kesadaran
        ks.update_body_locus((1, 2, 3), orientation=35, sensory_horizon=5)
        anchor = ks.body_locus_state()["anchor"]

        tidak_bisa = ks.imagine_from_body(
            "aku menjadi Ayu dan melihat dari tubuhnya", target="Ayu")
        self.assertFalse(tidak_bisa["allowed"])
        self.assertGreater(tidak_bisa["rasa_asing"], 0.0)
        bisa_memodelkan = ks.constrain_imagination(
            "Ayu mungkin merasa sedih", target="Ayu", mode="model")
        self.assertTrue(bisa_memodelkan["allowed"])
        jauh = ks.constrain_imagination(
            "aku merasakan dari tubuh itu", mode="observe", position=(20, 0, 0))
        self.assertFalse(jauh["allowed"])

        sim = ks.future_simulation("aku menjadi Ayu")
        self.assertTrue(sim["dibatasi_tubuh"])
        self.assertEqual(ks.body_locus_state()["anchor"], anchor)
        pulih = Naluri.from_dict(n.to_dict())
        self.assertEqual(pulih.kesadaran.body_locus_state()["anchor"], anchor)
        self.assertFalse(pulih.kesadaran.body_locus_state()["can_exchange"])


class KelelahanAtensiTest(unittest.TestCase):
    def test_beban_percakapan_memodulasi_recall_lexical_dan_attend(self):
        segar = Naluri(name="Segar", params={
            "enable_kesadaran": True, "enable_presentasi": True})
        lelah = Naluri(name="Lelah", params={
            "enable_kesadaran": True, "enable_presentasi": True})
        segar.enable_kesadaran(semua=True)
        lelah.enable_kesadaran(semua=True)
        segar.enable_presentasi(semua=True)
        lelah.enable_presentasi(semua=True)
        energi_awal = lelah.levels["energi"]
        for _ in range(18):
            lelah.presentasi.dengar(
                "Ceritakan apa yang kamu rasakan ketika itu terjadi, pelan-pelan.",
                "Player")
            lelah.presentasi.ucap(kepada="Player", topik="cerita itu",
                                   act="menjawab", diam_boleh=False)
        fatigue = lelah.kesadaran.attention_state()["fatigue"]
        self.assertGreater(fatigue, 0.7)
        self.assertAlmostEqual(lelah.levels["energi"], energi_awal,
                               msg="fatigue atensi bukan drain energi metabolik")
        self.assertEqual(segar.kesadaran.attention_state()["fatigue"], 0.0)

        l2 = L2(None, random.Random(0))
        entry = {"lema": "api", "sinonim": [], "valensi": 0.0,
                 "arousal": 0.0, "register_formalitas": 0.5,
                 "frekuensi": 0.5, "intensitas_bawaan": 0.0,
                 "daya_tekan": 0.0}
        slot = Slot("TOPIK", "N", "BENDA", True, 0.9, 0.8, True)
        context = GenContext(topik="api", spotlight=("api",))
        skor_segar = l2._skor(entry, slot, context)
        skor_lelah = l2._skor(entry, slot, GenContext(
            topik="api", spotlight=("api",), attention_fatigue=fatigue))
        self.assertLess(skor_lelah, skor_segar)

        candidates = [{"content": f"petunjuk {i}", "salience": 0.7,
                       "tag": f"petunjuk_{i}", "kind": "object"}
                      for i in range(5)]
        dipilih_segar = segar.kesadaran.attend(candidates)
        dipilih_lelah = lelah.kesadaran.attend(candidates)
        self.assertLess(len(dipilih_lelah), len(dipilih_segar))
        self.assertEqual(len(dipilih_lelah), 1)

        memory_fresh = JejakPrediksi(naluri=segar, sync_nurani=False)
        memory_tired = JejakPrediksi(naluri=lelah, sync_nurani=False)
        for memory in (memory_fresh, memory_tired):
            memory.record_experience("pintu merah", "masuk", {"impact": 0.2},
                                     tick=0)
        hit_fresh = memory_fresh._retrieve("pintu merah", None, 0)[0]
        hit_tired = memory_tired._retrieve("pintu merah", None, 0)[0]
        self.assertLess(hit_tired["match_weight"], hit_fresh["match_weight"])
        self.assertGreater(hit_tired["attention_fatigue"], 0.7)
        restored = Naluri.from_dict(lelah.to_dict())
        self.assertAlmostEqual(restored.kesadaran.attention_fatigue, fatigue)


class PenahananSadarTest(unittest.TestCase):
    def test_dorongan_tutur_ditahan_sakitnya_terakumulasi_dan_tidak_dapat_dipaksa(self):
        n = Naluri(name="Sarah", params={
            "enable_kesadaran": True, "enable_presentasi": True,
            "enable_emosi": True}, rng_seed=9)
        n.enable_kesadaran(semua=True)
        n.enable_presentasi(semua=True)
        ks, p = n.kesadaran, n.presentasi
        rahasia = "Aku masih ingat malam ketika rumah terbakar."
        desire = ks.withhold_speech(rahasia, topic="rumah terbakar",
                                    recipient="Player", strength=0.8)
        ident = desire["id"]
        initial_state = ks.withholding_state()["tertahan"][0]
        self.assertTrue(initial_state["keinginan_mengungkapkan"])
        self.assertEqual(initial_state["tindakan"], "menahan")
        self.assertGreater(initial_state["rasa_sakit"], 0.0)

        hasil = []
        for prompt in ("Apa yang terjadi saat rumah terbakar?",
                       "Katakan sekarang, aku perlu tahu."):
            p.dengar(prompt, "Player")
            hasil.append(p.ucap(kepada="Player", topik="rumah terbakar",
                                act="menjawab", diam_boleh=False))
        for entry in hasil:
            self.assertNotIn(rahasia, entry["teks"])
            self.assertTrue(entry["penahanan_sadar"]["mampu_mengucapkan"])
            self.assertTrue(entry["penahanan_sadar"]["tidak_dapat_dipaksa"])
            self.assertNotEqual(entry.get("act"), "menolak")
            self.assertNotIn("alasan_penolakan", entry)
            self.assertTrue(entry["prosodi"]["penahanan_sadar"])
            self.assertTrue(entry["penanda_terlihat"])
        state = ks.withholding_state()
        self.assertEqual(state["tertahan"][0]["ditahan"], 2)
        self.assertGreater(state["tertahan"][0]["rasa_sakit"], 0.0)
        self.assertNotIn("isi_tertahan", state["tertahan"][0])
        self.assertGreater(ks._identity_traits["terbiasa menahan rumah terbakar"], 0.0)
        self.assertFalse(ks.choose_to_disclose(ident, dipilih_npc=False)["diungkap"])

        pulih = Naluri.from_dict(n.to_dict())
        self.assertTrue(pulih.kesadaran.withholding_state()["aktif"])
        self.assertEqual(pulih.kesadaran.withholding_state()["tertahan"][0]["ditahan"], 2)
        dibuka = pulih.kesadaran.choose_to_disclose(ident, dipilih_npc=True)
        self.assertTrue(dibuka["diungkap"])
        self.assertEqual(dibuka["teks"], rahasia)
        final_state = pulih.kesadaran.withholding_state()["tertahan"][0]
        self.assertEqual(final_state["tindakan"], "mengungkapkan")
        self.assertTrue(final_state["diungkapkan"])
        self.assertFalse(pulih.kesadaran.withholding_state()["aktif"])


class AudisiDiriTest(unittest.TestCase):
    @staticmethod
    def _npc(name="Mira"):
        n = Naluri(name=name, rng_seed=31, params={
            "enable_kesadaran": True, "enable_presentasi": True,
            "enable_emosi": True})
        n.enable_kesadaran(semua=True)
        n.enable_presentasi(semua=True)
        return n

    def test_ujaran_diproses_sebagai_suara_luar_bukan_inner_speech_atau_turn(self):
        n = self._npc()
        ks, p = n.kesadaran, n.presentasi
        ks.params["enable_inner_speech"] = False
        ks.params["enable_pragmatics"] = False

        entry = p.ucap(kepada="Player", topik="perjalanan",
                       act="menjawab", diam_boleh=False)
        state = ks.self_audition_state()
        audisi = state["terakhir"]
        self.assertEqual(state["jumlah"], 1)
        self.assertEqual(audisi["terdengar"], entry["teks"])
        self.assertEqual(audisi["sumber"], "suara_diri_yang_terdengar_dari_luar")
        self.assertEqual(audisi["perspektif_pendengar"],
                         "orang_ketiga_yang_mengenali_suaranya")
        self.assertGreaterEqual(audisi["latensi_kognitif_ms"], 18)
        self.assertLessEqual(audisi["latensi_kognitif_ms"], 44)
        self.assertTrue(audisi["diproses_sebagai_input_baru"])
        self.assertFalse(ks.self_talk)
        self.assertEqual(ks.turn_state["turn"], 0,
                         "audisi tidak bergantung pada pencatatan dialogue_turn")
        self.assertNotIn("_audisi_intended", entry)
        self.assertNotIn("_audisi_intended", p._history[-1])
        self.assertTrue(any(x.get("kind") == "audisi_diri"
                            for x in ks.workspace))

    def test_audisi_mendeteksi_kesenjangan_niat_dan_kebohongan_diri(self):
        n = self._npc("Nara")
        ks = n.kesadaran
        n.emosi["takut"] = 0.9
        emosi_sebelum = dict(n.emosi)
        audisi = ks.audition_self(
            "Aku baik-baik saja.",
            intended="Aku takut dan aku butuh bantuan.",
            prosody={"tremor": 0.75, "jeda_ms": 700})

        self.assertEqual(audisi["niat_vs_realisasi"]["kesenjangan"], 1.0)
        self.assertGreater(audisi["surprise"], 0.8)
        self.assertGreater(audisi["kebohongan_diri"], 0.7)
        self.assertLess(audisi["kredibilitas_suara"], 0.3)
        self.assertGreater(audisi["reaksi_setelah_mendengar"]["self_doubt"], 0.4)
        self.assertEqual(n.emosi, emosi_sebelum,
                         "reaksi audisi terpisah dari afek yang mendorong ujaran")
        self.assertTrue(any(x.get("source") == "suara_diri_dari_luar"
                            for x in ks.workspace))

    def test_malu_retroaktif_mengubah_tutur_berikutnya_dan_disimpan(self):
        n = self._npc("Sari")
        ks, p = n.kesadaran, n.presentasi
        malu_awal = ks.moral["malu"]
        hasil = ks.audisi_diri(
            "Kau bodoh.", intended="Aku ingin memahami maksudmu.")
        self.assertGreater(hasil["malu_retroaktif"], 0.7)
        self.assertEqual(ks.moral["malu"], malu_awal,
                         "malu auditori tersimpan terpisah, bukan state pendorong")

        pro = p.prosodi("menyatakan")
        self.assertLess(pro["volume"], 0.5)
        self.assertGreater(pro["jeda_ms"], 120)
        berikut = p.ucap(kepada="Player", topik="hal lain", masuk=True,
                          diam_boleh=False)
        self.assertEqual(berikut["act"], "ragu")

        dipulihkan = Naluri.from_dict(n.to_dict())
        state = dipulihkan.kesadaran.self_audition_state()
        self.assertGreaterEqual(state["jumlah"], 2)
        self.assertEqual(state["terakhir"]["terdengar"], berikut["teks"])
        self.assertEqual(state["terakhir"]["sumber"],
                         "suara_diri_yang_terdengar_dari_luar")

    def test_sakelar_audisi_diri_bisa_diaktifkan_dengan_nama_indonesia(self):
        n = Naluri(params={"enable_kesadaran": False})
        status = n.enable_kesadaran("audisi_diri", semua=True)
        self.assertTrue(status["self_audition"])
        self.assertTrue(n.kesadaran.audition_self("aku mendengarmu")["aktif"])
        n.params["enable_self_audition"] = False
        self.assertFalse(n.kesadaran.audition_self("uji")["aktif"])


class SaSpTest(unittest.TestCase):
    def test_literal_terpisah_dari_maksud_dan_aksi_tersedia(self):
        ujaran = "Di luar sangatlah panas."
        literal = sa_sp_literal(ujaran)
        prag_kaya = sa_sp_pragmatik(
            ujaran, {"ruangan_panas": True,
                     "available_actions": ["ac", "jendela"]})
        prag_terbatas = sa_sp_pragmatik(
            ujaran, {"ruangan_panas": True,
                     "available_actions": ["jendela"]})

        self.assertTrue(literal["bebas_konteks"])
        self.assertEqual(literal["proposisi"]["predikat"], "tinggi")
        self.assertEqual(literal["proposisi"]["intensitas"], 0.7)
        self.assertNotEqual(prag_kaya["tindakan_tersedia"],
                            prag_terbatas["tindakan_tersedia"])
        ac = [x for maksud in prag_kaya["maksud_tersirat"]
              for x in maksud.get("tindakan_kandidat", [])]
        self.assertIn("menyalakan_pendingin_ruangan", [x["aksi"] for x in ac])
        restricted = [x for maksud in prag_terbatas["maksud_tersirat"]
                      for x in maksud.get("tindakan_kandidat", [])]
        self.assertIn("membuka_jendela", [x["aksi"] for x in restricted])
        self.assertNotIn("menyalakan_pendingin_ruangan",
                         [x["aksi"] for x in restricted])
        self.assertTrue(any(x.get("status") == "hipotesis, bukan fakta"
                            for x in prag_kaya["maksud_tersirat"]))

        analyzer = SASPAnalyzer()
        complete = analyzer.analisis(ujaran, {"ruangan_panas": True})
        self.assertEqual(complete["semantik"], literal)
        self.assertTrue(complete["pragmatik"]["bergantung_konteks"])
        self.assertEqual(sa_sp(ujaran)["sistem"], "sa_sp/1")

    def test_presentasi_dengar_mencatat_sa_sp_dengan_konteks(self):
        n = Naluri(name="Laras", rng_seed=18, params={
            "enable_kesadaran": True, "enable_presentasi": True})
        result = n.presentasi.dengar(
            "Di luar panas.", dari="Player",
            context={"ruangan_panas": True,
                     "available_actions": ["kipas"]})
        self.assertIn("sa_sp", result)
        self.assertEqual(n.kesadaran.sa_sp_state()["jumlah"], 1)
        self.assertEqual(n.presentasi._sa_sp_last["semantik"]["proposisi"]["predikat"],
                         "tinggi")


class StrategiSosialTest(unittest.TestCase):
    def _npc(self):
        return Naluri(name="Nara", rng_seed=27, params={
            "enable_kesadaran": True, "enable_presentasi": True})

    def test_kebohongan_sadar_permainan_peran_dan_manipulasi_diucapkan(self):
        n = self._npc()
        ks, p = n.kesadaran, n.presentasi
        lie = ks.choose_to_lie(
            "Aku pergi ke utara.", "Aku pergi ke selatan.",
            "melindungi rencana", target="Player", topic="rute")
        self.assertTrue(lie["dipilih_untuk_menipu"])
        said = p.ucap(kepada="Player", topik="rute", diam_boleh=False)
        self.assertEqual(said["teks"], "Aku pergi ke selatan.")
        self.assertNotIn("_strategic_plan", said)
        self.assertEqual(ks._strategic_deceptions[-1]["status"], "telah_diucapkan")

        ks.plan_manipulation(
            "Player", "mengubah keyakinan tentang jalan",
            [{"aksi": "berkata", "ujaran": "Kita bisa mencoba jalur kecil ini."},
             {"aksi": "berkata", "ujaran": "Aku sudah memeriksanya lebih dulu."}],
            intended_belief="jalur itu aman")
        first = p.ucap(kepada="Player", topik="jalan", diam_boleh=False)
        self.assertEqual(first["teks"], "Kita bisa mencoba jalur kecil ini.")
        self.assertEqual(ks._manipulation_plans[-1]["indeks"], 1)
        self.assertEqual(ks._manipulation_plans[-1]["status"], "direncanakan")

        ks.roleplay("pedagang", tujuan="mengalihkan perhatian",
                    target="Player", klaim="Aku hanya menjual teh.")
        role = p.ucap(kepada="Player", topik="teh", diam_boleh=False)
        self.assertEqual(role["teks"], "Aku hanya menjual teh.")
        self.assertTrue(ks._roleplay_state["klaim_sudah_diucapkan"])

        ks.roleplay("penjaga", target="Player",
                    gaya={"awalan": "Atas nama penjaga,", "act": "menolak"})
        styled = p.ucap(kepada="Player", topik="aturan", diam_boleh=False)
        self.assertTrue(styled["teks"].startswith("Atas nama penjaga,"))
        self.assertEqual(styled["act"], "menolak")

    def test_rahasia_ditahan_dan_kesetiaan_tidak_memakai_valensi(self):
        n = self._npc()
        ks, p = n.kesadaran, n.presentasi
        rahasia = ks.withhold_speech(
            "Aku akan pergi saat fajar.", topic="fajar", recipient="Player")
        out = p.ucap(kepada="Player", topik="fajar", diam_boleh=False)
        self.assertTrue(rahasia["dipilih_ditahan"])
        self.assertTrue(out.get("penahanan_sadar"))
        self.assertNotIn("pergi saat fajar", out["teks"])

        ks.choose_to_lie("Aku tahu pintunya terkunci.",
                         "Pintunya terbuka.", "mengalihkan perhatian", "Player")
        loyalty = ks.choose_loyalty([
            {"target": "Ayu", "trust": 0.9, "importance": 0.8,
             "commitment_strength": 0.7, "cost": 0.1},
            {"target": "Bima", "trust": 0.2, "importance": 0.4,
             "commitment_strength": 0.0, "cost": 0.6},
        ])
        self.assertEqual(loyalty["pihak"], "Ayu")
        self.assertFalse(loyalty["valensi_dipakai"])
        public = ks.social_strategy_state()
        self.assertNotIn("kebenaran_diketahui", public["kebohongan_sengaja"][0])


class EpistemicAndOpacityTest(unittest.TestCase):
    def test_emosi_epistemik_berbeda_dari_moral_dan_opasitas_menyimpan_latensi(self):
        n = Naluri(params={"enable_kesadaran": True}, rng_seed=29)
        ks = n.kesadaran
        ks.epistemic_emotion("malu_tidak_tahu", 0.8, "uji pengetahuan")
        self.assertGreater(ks.epistemic_emotion_state()["emosi"]["malu_tidak_tahu"], 0)
        self.assertEqual(ks.moral["malu"], 0.0)

        private = ks.self_opacity(
            perasaan_dikenali="senang", perasaan_laten="takut",
            sebab_diyakini="kabar baik", sebab_laten="ancaman tersembunyi")
        public = ks.self_opacity_state()
        self.assertEqual(private["status"], "salah_membaca_perasaan")
        self.assertNotIn("perasaan_laten", public)
        self.assertNotIn("sebab_laten", public)
        self.assertNotIn("perasaan_laten", public["riwayat"][-1])
        self.assertEqual(ks.self_opacity_state(include_private=True)["perasaan_laten"],
                         "takut")


class AestheticsAndBoredomTest(unittest.TestCase):
    def test_bosan_menghasilkan_aksi_baru_dan_permainan_memegang_dua_frame(self):
        n = Naluri(name="Sari", rng_seed=31, params={
            "enable_kesadaran": True, "enable_presentasi": True})
        aksi = {}
        for _ in range(12):
            aksi = n.presentasi.perilaku_idle()
            if aksi.get("aksi"):
                break
        self.assertTrue(aksi.get("aksi"))
        self.assertTrue(aksi.get("tujuan_free_will"))
        self.assertIn(aksi["aksi"], n.presentasi.boredom_state()["aksi_terbaru"])

        estetika = n.kesadaran.aesthetic_response(
            "pola cahaya di jendela",
            {"keindahan": 0.9, "simetri": 0.8, "kebaruan": 0.6,
             "harmoni": 0.9})
        self.assertGreater(estetika["skor"], 0.7)
        self.assertTrue(estetika["bukan_utilitas_drive"])
        play = n.kesadaran.playful_reframe(
            "hujan turun", "langit sedang menyiram taman", jenis="ironi")
        self.assertTrue(play["frame_ganda"])
        self.assertTrue(play["resolusi_ditahan"])
        self.assertTrue(n.kesadaran.play_aesthetics_state()["jumlah_frame_ganda"])


class SleepInsightAndFreeWillTest(unittest.TestCase):
    def test_tidur_menghasilkan_hipotesis_baru_dari_pengalaman(self):
        n = Naluri(name="Danu", rng_seed=33, params={"enable_kesadaran": True})
        n.kesadaran.timeline.extend([
            {"content": "pola retak pada kaca tua", "tick": 1},
            {"content": "bunyi hujan mengisi lorong", "tick": 2},
        ])
        result = n.post_sleep()
        insight = result["wawasan_tidur"]
        self.assertEqual(insight["asal"], "inkubasi_tidur")
        self.assertTrue(insight["bukan_hanya_konsolidasi"])
        self.assertEqual(insight["sumber"], [
            "pola retak pada kaca tua", "bunyi hujan mengisi lorong"])
        self.assertIn("wawasan", result["bangun"])

    def test_state_baru_json_roundtrip(self):
        n = Naluri(name="Mira", rng_seed=37, params={
            "enable_kesadaran": True, "enable_presentasi": True})
        ks = n.kesadaran
        ks.epistemic_emotion("penasaran", 0.75, "ujian serialisasi")
        ks.self_opacity(perasaan_dikenali="senang", perasaan_laten="takut",
                        sebab_diyakini="kabar baik", sebab_laten="bahaya")
        ks.choose_to_lie("arah utara", "arah selatan", "menjaga rencana", "Player")
        ks.playful_reframe("ujaran literal", "bingkai bermain", jenis="humor")
        n.presentasi.dengar("Di luar panas.", "Player",
                            context={"ruangan_panas": True})
        ks.free_will_choose_goal("mencoba pola baru", actions=["explore"])
        ks.timeline.extend([{"content": "bayangan pada air"},
                            {"content": "bunyi langkah di lorong"}])
        n.post_sleep()

        saved = json.loads(json.dumps(n.to_dict(), ensure_ascii=False))
        restored = Naluri.from_dict(saved)
        state = restored.kesadaran
        self.assertEqual(state.sa_sp_state()["jumlah"], 1)
        self.assertEqual(state.social_strategy_state(include_private=True)
                         ["kebohongan_sengaja"][0]["kebenaran_diketahui"],
                         "arah utara")
        self.assertEqual(state.self_opacity_state(include_private=True)
                         ["perasaan_laten"], "takut")
        self.assertTrue(state.play_aesthetics_state()["jumlah_frame_ganda"])
        self.assertEqual(state.free_will_current_goal()["tujuan"],
                         "mencoba pola baru")
        self.assertTrue(state.insight_report()["terakhir"])

    def test_free_will_memilih_tujuan_tanpa_drive_dan_mengarahkan_aksi(self):
        n = Naluri(name="Ari", rng_seed=35,
                   initial_levels={d: 1.0 for d in (
                       "energi", "keamanan", "keingintahuan", "penguasaan",
                       "afiliasi", "koherensi")},
                   params={"enable_kesadaran": True})
        ks = n.kesadaran
        decision = ks.free_will_decide_goal([
            {"goal": "membuat sketsa", "actions": ["draw"],
             "endorsement": 0.9, "novelty": 0.8,
             "value_alignment": 0.7, "autonomy": 1.0},
            {"goal": "beristirahat", "actions": ["rest"],
             "endorsement": 0.1, "novelty": 0.1,
             "value_alignment": 0.2, "autonomy": 0.5},
        ])
        self.assertTrue(decision["goal"]["dipilih_sendiri"])
        self.assertFalse(decision["goal"]["basis_keputusan"]["drive_dipakai"])
        self.assertEqual(n.intent()["jenis"], "free_will_goal")
        choice = n.choose_action([
            {"name": "rest", "drive_effects": {"energi": 0.1}},
            {"name": "draw", "drive_effects": {}},
        ], record_eligibility=False)
        self.assertEqual(choice["action"], "draw")
        self.assertGreater(choice["candidate"]["_free_will_bonus"], 0)

        restored = Naluri.from_dict(n.to_dict())
        self.assertEqual(restored.kesadaran.free_will_state()["jumlah_keputusan"], 1)
        self.assertEqual(restored.kesadaran.free_will_current_goal()["tujuan"],
                         "membuat sketsa")


if __name__ == "__main__":
    unittest.main()
