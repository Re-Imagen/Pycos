# -*- coding: utf-8 -*-
"""Kontrak antarlapisan dan view reflektif ketidaktahuan yang murni."""
from __future__ import annotations

import copy
import os
import sys
import unittest
from types import SimpleNamespace

AKAR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if AKAR not in sys.path:
    sys.path.insert(0, AKAR)

from pycos.kontrak import (  # noqa: E402
    DRIVE_KEYS, JANJI, KEBIJAKAN_ABAIKAN, KEBIJAKAN_CATAT, KEBIJAKAN_TOLAK,
    KEBUTUHAN, ContractViolationError, check_operation, kontrak_operasi,
    verifikasi_startup, verify_startup,
)
from pycos.refleksi.ketidaktahuan import (  # noqa: E402
    SIKAP_KETIDAKTAHUAN, STATUS_PENGETAHUAN, batas_pengetahuan,
    sikap_ketidaktahuan,
)


class KontrakStatikDanOperasiTest(unittest.TestCase):
    def test_manifest_startup_dan_kebijakan_host(self):
        from pycos.inti import DRIVES

        self.assertEqual(DRIVE_KEYS, tuple(DRIVES))
        self.assertIsNone(verifikasi_startup(drives_aktual=DRIVES))
        self.assertIsNone(verify_startup(actual_drives=DRIVES))
        self.assertEqual({"reject", "log", "ignore"}, {
            KEBIJAKAN_TOLAK, KEBIJAKAN_CATAT, KEBIJAKAN_ABAIKAN})
        error = ContractViolationError({"apa": "contoh", "pelanggar": "A",
                                        "dirugikan": "B"})
        self.assertIn("contoh", str(error))

    def test_semua_pelanggaran_masuk_dilaporkan_dan_state_tetap(self):
        npc = SimpleNamespace(levels={})
        levels_before = copy.deepcopy(npc.levels)
        report = kontrak_operasi(
            "tick", "masuk", npc,
            {"events": "bukan iterable peristiwa", "action_cost": 1}, level=1)
        self.assertIsNotNone(report)
        self.assertEqual(3, len(report["pelanggaran"]))
        for issue in report["pelanggaran"]:
            self.assertTrue({"apa", "pelanggar", "dirugikan"}.issubset(issue))
        self.assertEqual(levels_before, npc.levels)

    def test_level_fase_postcondition_dan_tambah_npc(self):
        from pycos.inti import Naluri
        from pycos.lingkungan import Lingkungan

        world = Lingkungan.dari_ascii(["....."], seed=2)
        npc = Naluri(name="Ayu", rng_seed=2)
        args = {"npc": npc, "posisi": (1, 0), "nama": "Ayu"}
        self.assertIsNone(kontrak_operasi(
            "lingkungan.tambah_npc", "masuk", world, args, level=1))
        body = world.tambah_npc(npc, args["posisi"], nama=args["nama"])
        self.assertIsNone(kontrak_operasi(
            "lingkungan.tambah_npc", "keluar", world, args, body, level=2))

        step_args = {"nama": "Ayu"}
        self.assertIsNone(kontrak_operasi(
            "step", "masuk", world, step_args, level=1))
        result = world.langkah("Ayu")
        self.assertIsNone(kontrak_operasi(
            "step", "keluar", world, step_args, result, level=2))
        self.assertIsNone(kontrak_operasi(
            "step", "keluar", world, step_args, result, level=1),
            "Level 1 hanya menjalankan precondition")

    def test_tick_menerima_fase_masuk_keluar_dan_level_tiga(self):
        from pycos.inti import Naluri

        npc = Naluri(name="Rama", rng_seed=3)
        tick_before = npc.tick_count
        args = {"events": [], "action_cost": False,
                "tick_before": tick_before}
        self.assertIsNone(kontrak_operasi(
            "naluri.tick", "masuk", npc, args, level=3))
        npc.tick(events=args["events"], action_cost=args["action_cost"])
        self.assertIsNone(kontrak_operasi(
            "naluri.tick", "keluar", npc, args, hasil=None, level=3))

    def test_level_nol_tidak_memeriksa_dan_level_invalid_dilaporkan(self):
        self.assertIsNone(kontrak_operasi("tick", "masuk", object(), level=0))
        report = kontrak_operasi("tick", "masuk", object(), level=4)
        self.assertIn("integer 0..3", report["apa"])
        self.assertIsNone(check_operation(
            operation="tick", phase="entry",
            subject=SimpleNamespace(levels={d: 0.0 for d in DRIVE_KEYS}),
            arguments={"events": [], "action_cost": False}, level=1))

    def test_manifest_memuat_subsistem_keselarasan(self):
        for nama in ("Persona", "Keadaan", "PelacakSelaras"):
            self.assertIn(nama, JANJI)
        self.assertIn("PenilaiSelaras", KEBUTUHAN)
        self.assertIsNone(verifikasi_startup())

    def test_kontrak_operasi_nilai_selaras_dan_pelacak(self):
        from pycos.inti.persona import PERSONA_CONTOH, Keadaan
        from pycos.refleksi.nurani import PelacakSelaras, nilai_selaras

        keadaan = Keadaan(valensi=0.6)
        laporan = nilai_selaras(PERSONA_CONTOH, keadaan, "aku senang banget!")
        argumen = {"persona": PERSONA_CONTOH, "keadaan": keadaan,
                   "teks": "aku senang banget!"}
        self.assertIsNone(kontrak_operasi("nilai_selaras", "masuk", None,
                                          argumen, level=2))
        self.assertIsNone(kontrak_operasi("nilai_selaras", "keluar", None,
                                          {}, laporan, level=2))
        pelacak = PelacakSelaras()
        self.assertIsNone(kontrak_operasi("pelacak.catat", "masuk", pelacak,
                                          {"laporan": laporan}, level=2))
        pelacak.catat(laporan)
        self.assertIsNone(kontrak_operasi("pelacak.catat", "keluar", pelacak,
                                          {"laporan": laporan}, None, level=2))

    def test_kontrak_operasi_penilai_melaporkan_input_buruk(self):
        buruk = {"persona": SimpleNamespace(nama=None, sifat={}),
                 "keadaan": SimpleNamespace(valensi=float("nan"), gairah=2.0,
                                            ketidakpastian=0.3),
                 "teks": ""}
        report = kontrak_operasi("nilai_selaras", "masuk", None, buruk, level=2)
        self.assertIsNotNone(report)
        hasil_palsu = SimpleNamespace(status=None, skor=2.0,
                                      dimensi="bukan-sekuens")
        report = kontrak_operasi("nilai_selaras", "keluar", None, {},
                                 hasil_palsu, level=2)
        self.assertIsNotNone(report)
        report = kontrak_operasi("pelacak.catat", "masuk",
                                 SimpleNamespace(), {"laporan": object()},
                                 level=2)
        self.assertIsNotNone(report)


class BatasPengetahuanTest(unittest.TestCase):
    def test_npc_setengah_jadi_dan_di_luar_jangkauan_aman(self):
        npc = SimpleNamespace()
        result = batas_pengetahuan(npc, "api panas")
        self.assertEqual("tidak tahu", result["kesimpulan"])
        self.assertEqual(
            {"episodik", "afektif", "kausal", "sosial", "sadar"},
            set(result["wadah"]))
        self.assertEqual(set(STATUS_PENGETAHUAN), {
            "tahu", "merasa tahu", "tidak tahu", "tidak bisa tahu"})
        self.assertEqual(
            "tidak bisa tahu",
            batas_pengetahuan(npc, {
                "text": "rahasia yang dilindungi",
                "jangkauan": "di luar jangkauan",
            })["kesimpulan"],
        )
        focused = SimpleNamespace(kesadaran=SimpleNamespace(spotlight=[{
            "content": "api panas", "attention": 0.9,
        }]))
        focused_result = batas_pengetahuan(focused, "api panas")
        self.assertEqual("cukup", focused_result["wadah"]["sadar"]["status"])
        self.assertEqual("tidak tahu", focused_result["kesimpulan"],
                         "spotlight menandai atensi, bukan fakta/ingatan")

    def test_memori_episodik_dibaca_dari_indeks_tanpa_mutasi(self):
        from pycos.inti import Naluri
        from pycos.memori import JejakPrediksi

        npc = Naluri(name="Mira", rng_seed=4)
        memory = JejakPrediksi(naluri=npc)
        npc.attach_jejak(memory)
        memory.record_experience(
            "api menyentuh tangan", "menjauh dari api",
            {"impact": -0.8, "drive_deltas": {"keamanan": -0.8},
             "label": "kulit terbakar"}, sync_nurani=False)
        index_before = copy.deepcopy(memory._token_index)
        episodes_before = copy.deepcopy(memory._ep_by_id)
        calls_before = memory._retrieve_calls
        result = batas_pengetahuan(npc, "api menyentuh tangan")
        self.assertEqual("tahu", result["kesimpulan"])
        self.assertEqual("cukup", result["wadah"]["episodik"]["status"])
        self.assertEqual(index_before, memory._token_index)
        self.assertEqual(episodes_before, memory._ep_by_id)
        self.assertEqual(calls_before, memory._retrieve_calls)

    def test_afektif_saja_menjadi_merasa_tahu(self):
        from pycos.inti import Naluri

        npc = Naluri(name="Intuisi", rng_seed=5)
        npc.enable_nurani("affective_memory")
        npc.nurani.experience(
            "misteri berbahaya menyentuh tangan",
            {"keamanan": -0.9}, tick=1)
        signature_cache_before = dict(npc.nurani._sig_cache)
        result = batas_pengetahuan(
            npc, "misteri berbahaya menyentuh tangan")
        self.assertEqual("merasa tahu", result["kesimpulan"])
        self.assertEqual("cukup", result["wadah"]["afektif"]["status"])
        self.assertEqual(signature_cache_before, npc.nurani._sig_cache,
                         "view tidak boleh memanggil context_signature/cache")

    def test_wadah_sosial_dan_kausal_dibaca_lokal(self):
        from pycos.inti import Naluri
        from pycos.mandiri.organik import ModelKausal

        npc = Naluri(name="Sena", rng_seed=6)
        npc.nurani.observe_other_belief(
            "Ayu", "keamanan", -0.7, confidence=0.9, tick=1)
        social = batas_pengetahuan(npc, {
            "text": "keamanan", "pemegang": "Ayu", "drive": "keamanan"})
        self.assertEqual("cukup", social["wadah"]["sosial"]["status"])

        graph = ModelKausal()
        graph._tepi("a:menyentuh api", "h:tangan terbakar", 0.9)
        npc._organik = SimpleNamespace(kausal=graph)
        causal = batas_pengetahuan(npc, "tangan terbakar")
        self.assertEqual("cukup", causal["wadah"]["kausal"]["status"])
        self.assertIn("kausal", causal["wadah_kuat"])

    def test_sikap_memakai_watak_dan_konteks_tanpa_menyimpan(self):
        unknown = {"kesimpulan": "tidak tahu", "kekuatan_maks": 0.0}
        self.assertEqual("bertanya", sikap_ketidaktahuan(
            SimpleNamespace(levels={}, urgency={}, emosi={}, params={}),
            unknown, {"urgensi": 1.0}))
        self.assertEqual("malu", sikap_ketidaktahuan(
            SimpleNamespace(levels={}, urgency={}, emosi={}, params={}),
            unknown, {"publik": True, "watak": {"pemalu": 0.9}}))
        self.assertEqual("marah", sikap_ketidaktahuan(
            SimpleNamespace(levels={}, urgency={}, emosi={"marah": 0.9}, params={}),
            unknown))
        self.assertEqual("kekanak", sikap_ketidaktahuan(
            SimpleNamespace(stage="anak", levels={}, urgency={}, emosi={}, params={}),
            unknown))
        self.assertEqual("diam", sikap_ketidaktahuan(
            SimpleNamespace(levels={}, urgency={}, emosi={}, params={}),
            unknown, {"watak": {"pendiam": 0.9}}))
        self.assertEqual("tenang", sikap_ketidaktahuan(
            SimpleNamespace(levels={}, urgency={}, emosi={}, params={}), unknown))
        self.assertEqual("waspada", sikap_ketidaktahuan(
            SimpleNamespace(personality_name="paranoid", levels={}, urgency={},
                            emosi={}, params={}), unknown, {"publik": True}))
        self.assertEqual(
            set(SIKAP_KETIDAKTAHUAN),
            {"waspada", "malu", "marah", "kekanak", "tenang", "bertanya", "diam"},
        )


class IntegrasiKetidaktahuanTest(unittest.TestCase):
    def test_kesadaran_menambah_kandidat_sementara_dari_konteks_ada(self):
        from pycos.inti import Naluri

        npc = Naluri(name="Penasaran", rng_seed=7)
        npc.enable_kesadaran("global_workspace")
        npc.urgency["keingintahuan"] = 2.0
        npc.context_aktif = [{
            "stimulus": "misteri yang belum pernah dilihat",
            "salience": 0.8,
        }]
        workspace_before = copy.deepcopy(npc.kesadaran.workspace)
        candidates = npc.kesadaran._candidates()
        added = [x for x in candidates if x.get("kind") == "ketidaktahuan"]
        self.assertEqual(1, len(added))
        self.assertIn("misteri yang belum pernah dilihat", added[0]["content"])
        self.assertEqual(workspace_before, npc.kesadaran.workspace)

    def test_prior_presentasi_aditif_tidak_mengganti_himpunan_act(self):
        from pycos.inti import Naluri

        npc = Naluri(name="Bertanya", rng_seed=8)
        npc.urgency["keingintahuan"] = 2.5
        presentation = npc.presentasi
        baseline = presentation._skor_acts(None, None, False)
        shifted = presentation._skor_acts(None, "misteri baru", False)
        self.assertEqual(set(baseline), set(shifted))
        self.assertGreater(shifted["bertanya"], baseline["bertanya"])

    def test_sikap_bertanya_menaikkan_doubt_nurani_di_tick(self):
        from pycos.inti import Naluri

        npc = Naluri(name="Ragu", rng_seed=9)
        npc.enable_kesadaran("reality_monitoring")
        # NURANI metacognitive_doubt juga menghormati gate felt-consciousness.
        npc.params["enable_felt_consciousness"] = True
        # Hindari transisi auto-maturasi anak pada tick pertama.
        npc.tick_count = 2000
        npc.urgency["keingintahuan"] = 2.5
        npc.context_aktif = [{
            "stimulus": "misteri asing yang belum dikenal",
            "salience": 0.7,
        }]
        npc.nurani.doubt_level = 0.0
        npc.tick()
        self.assertGreater(npc.nurani.doubt_level, 0.0)


if __name__ == "__main__":
    unittest.main()
