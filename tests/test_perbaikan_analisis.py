# -*- coding: utf-8 -*-
"""Tes regresi untuk hasil analisis menyeluruh: validasi batas masuk, NaN,
determinisme, batas memori, patching atomik, cache leksikon, dan fitur baru
(tolok, `--periksa`, diagnostik).
"""
from __future__ import annotations

import contextlib
import io
import json
import math
import os
import subprocess
import sys
import tempfile
import unittest

AKAR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if AKAR not in sys.path:
    sys.path.insert(0, AKAR)

from pycos.dukungan import diagnostik  # noqa: E402
from pycos.dukungan.numerik import float_hingga, jepit, jepit_01, jepit_drive  # noqa: E402


class NumerikTest(unittest.TestCase):
    def test_jepit_nan_menjadi_nol_lalu_dijepit(self):
        self.assertEqual(0.0, jepit(float("nan"), -1.0, 1.0))
        self.assertEqual(0.2, jepit(float("nan"), 0.2, 0.9))  # 0 dijepit ke lo
        self.assertEqual(1.0, jepit(7.0, -1.0, 1.0))
        self.assertEqual(-1.0, jepit(-7.0, -1.0, 1.0))

    def test_jepit_01_dan_drive(self):
        self.assertEqual(1.0, jepit_01(3.0))
        self.assertEqual(0.0, jepit_01(-3.0))
        self.assertEqual(0.0, jepit_drive(float("nan")))
        self.assertEqual(-1.0, jepit_drive(-5))

    def test_float_hingga_menolak_non_finite_dan_tak_numerik(self):
        self.assertEqual(0.5, float_hingga("0.5", "x"))
        for buruk in (float("nan"), float("inf"), "abc", None):
            with self.subTest(nilai=buruk), self.assertRaises((ValueError, TypeError)):
                float_hingga(buruk, "x")


class ValidasiBatasMasukNalurTest(unittest.TestCase):
    def setUp(self):
        from pycos.inti.naluri import Naluri
        self.Naluri = Naluri

    def test_initial_levels_kunci_asing_ditolak(self):
        with self.assertRaisesRegex(ValueError, "tak dikenal"):
            self.Naluri(rng_seed=1, initial_levels={"energy": 0.1})

    def test_initial_levels_nan_dan_luar_rentang_ditolak(self):
        with self.assertRaisesRegex(ValueError, "berhingga"):
            self.Naluri(rng_seed=1, initial_levels={"keamanan": float("nan")})
        with self.assertRaisesRegex(ValueError, "rentang"):
            self.Naluri(rng_seed=1, initial_levels={"keamanan": 5.0})

    def test_weights_kunci_asing_ditolak(self):
        with self.assertRaisesRegex(ValueError, "tak dikenal"):
            self.Naluri(rng_seed=1, weights={"energy": 1.0})

    def test_delta_non_finite_ditolak(self):
        npc = self.Naluri(rng_seed=2)
        with self.assertRaises(ValueError):
            npc.tick(events=[{"drive": "energi", "delta": float("nan")}])
        # Level tidak boleh berubah diam-diam menjadi 1.0 akibat NaN.
        self.assertTrue(all(math.isfinite(v) for v in npc.levels.values()))

    def test_reward_for_kunci_asing_dan_nan_ditolak(self):
        npc = self.Naluri(rng_seed=3)
        with self.assertRaises(ValueError):
            npc.reward_for({"tidakada": 1.0})
        with self.assertRaises(ValueError):
            npc.reward_for({"energi": float("nan")})

    def test_choose_action_menolak_kandidat_tanpa_nama(self):
        npc = self.Naluri(rng_seed=4)
        for buruk in ({"name": None}, {"name": "   "}, {"drive_effects": {}}):
            with self.subTest(kandidat=buruk), self.assertRaises(ValueError):
                npc.choose_action([buruk])

    def test_choose_action_mencatat_kunci_effects_salah(self):
        diagnostik.kosongkan()
        npc = self.Naluri(rng_seed=5)
        npc.choose_action([{"name": "makan", "effects": {"energi": 1.0}}])
        laporan = diagnostik.laporan()
        self.assertIn("Naluri.choose_action", laporan["per_sumber"])


class PerilakuNalurTest(unittest.TestCase):
    def setUp(self):
        from pycos.inti.naluri import Naluri
        self.Naluri = Naluri

    def test_determinisme_dengan_seed_sama(self):
        a = self.Naluri(rng_seed=42, name="a")
        b = self.Naluri(rng_seed=42, name="b")
        for k in range(40):
            ev = [{"drive": "keamanan", "delta": -0.03, "reason": "ancaman"}] if k % 7 == 0 else None
            a.tick(events=ev)
            b.tick(events=ev)
        self.assertEqual(a.levels, b.levels)
        self.assertEqual(a.tick_count, b.tick_count)

    def test_losses_dibatasi(self):
        from pycos.inti.naluri import _MAKS_LOSSES
        npc = self.Naluri(rng_seed=6)
        for _ in range(_MAKS_LOSSES + 50):
            npc.kesadaran.face_death("uji")
        self.assertLessEqual(len(npc.kesadaran.losses), _MAKS_LOSSES)

    def test_mimpi_tertunda_dikonsumsi_saat_bangun(self):
        npc = self.Naluri(rng_seed=7)
        kes = npc.kesadaran
        kes.params["enable_kesadaran"] = True  # master kesadaran harus aktif
        self.assertTrue(kes.enabled("dream_continuity"))
        kes._dream_pending.append({"uji": True})
        laporan = kes.wake()
        self.assertIn({"uji": True}, laporan.get("mimpi_tertunda", []))
        self.assertEqual([], kes._dream_pending)

    def test_round_trip_setelah_perbaikan(self):
        npc = self.Naluri(rng_seed=8, initial_levels={"keamanan": -0.3})
        npc.tick(events=[{"drive": "keamanan", "delta": -0.02, "reason": "x"}])
        data = json.loads(json.dumps(npc.to_dict()))
        self.assertEqual(npc.levels, self.Naluri.from_dict(data).levels)


class JejakPrediksiTest(unittest.TestCase):
    def test_future_simulation_menghasilkan_peringkat(self):
        from pycos.memori.jejak_prediksi import JejakPrediksi
        jejak = JejakPrediksi(rng_seed=11)
        hasil = jejak.future_simulation("lapar", ["makan", "tidur"], tick=3)
        self.assertIn(hasil["aksi_dibayangkan"], {"makan", "tidur"})
        self.assertEqual(3, hasil["tick"])

    def test_rank_actions_menerima_mapping(self):
        from pycos.memori.jejak_prediksi import JejakPrediksi
        jejak = JejakPrediksi(rng_seed=12)
        hasil = jejak.rank_actions("lapar", [{"name": "makan"}, {"name": "tidur"}])
        self.assertEqual({"makan", "tidur"}, {r["name"] for r in hasil["ranked"]})


class PatchingTest(unittest.TestCase):
    def test_install_methods_batch_konflik_tidak_menandai_fungsi(self):
        from pycos.dukungan import patching

        class Target:
            def ada(self):
                return 1

        def baru(self):
            return 2

        def bentrok(self):  # nama 'ada' sudah dimiliki implementasi lain
            return 3

        def ada_lain(self):
            return 4

        with self.assertRaises(patching.PatchConflictError):
            patching.install_methods(Target, {"baru": baru, "ada": bentrok},
                                     patch_id="uji-atomik")
        self.assertFalse(hasattr(Target, "baru"))
        # Fungsi yang belum terpasang tidak boleh ikut ber-tag oleh batch yang gagal.
        self.assertEqual((), tuple(patching._patch_ids(baru)))

    def test_pesan_galat_memuat_nama_lengkap(self):
        from pycos.dukungan import patching
        class Kelas:
            pass

        galat = patching._conflict(Kelas, "metode", "pid")
        self.assertIn("metode", str(galat))
        self.assertIn("pid", str(galat))

    def test_optional_module_absen_menjadi_none(self):
        from pycos.dukungan.patching import optional_module
        self.assertIsNone(optional_module("modul_tidak_ada_sama_sekali_xyz"))

    def test_optional_module_dependensi_hilang_dilempar_ulang(self):
        from pycos.dukungan.patching import optional_module
        with tempfile.TemporaryDirectory() as tmp:
            with open(os.path.join(tmp, "uji_dep_modul.py"), "w", encoding="utf-8") as f:
                f.write("import dependensi_hilang_xyz\n")
            sys.path.insert(0, tmp)
            try:
                with self.assertRaises(ImportError):
                    optional_module("uji_dep_modul")
            finally:
                sys.path.remove(tmp)
                sys.modules.pop("uji_dep_modul", None)


class LeksikonDanCacheTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from pycos.dukungan.sumber import jalur_leksikon
        cls.path = jalur_leksikon()

    def test_cache_mengembalikan_objek_yang_sama(self):
        from pycos.bahasa.tutur import TuturEngine, kosongkan_cache_leksikon
        kosongkan_cache_leksikon()
        a = TuturEngine(self.path)
        b = TuturEngine(self.path)
        self.assertIs(a.leks, b.leks)
        kosongkan_cache_leksikon()
        c = TuturEngine(self.path)
        self.assertIsNot(a.leks, c.leks)

    def test_polisem_menyimpan_semua_sense(self):
        from pycos.bahasa.tutur import Leksikon, TuturEngine
        eng = TuturEngine(self.path)
        leks = eng.leks
        self.assertIsInstance(leks, Leksikon)
        ditemukan = False
        for (bahasa, lema), senses in leks._senses.items():
            if len(senses) > 1:
                kelas_gabungan = leks.kelas_dari(lema, bahasa)
                for s in senses:
                    for k in s.get("kelas", []):
                        self.assertIn(k, kelas_gabungan)
                ditemukan = True
                break
        self.assertTrue(ditemukan, "leksikon seharusnya memuat lema polisem")


class DuniaTest(unittest.TestCase):
    def test_potong_nan_tidak_menjadi_batas_atas(self):
        from pycos.lingkungan.dunia import _potong
        self.assertEqual(0.0, _potong(float("nan"), -1.0, 1.0))
        self.assertEqual(1.0, _potong(9.0, -1.0, 1.0))

    def test_menerima_action_cost_dari_signature(self):
        from pycos.lingkungan import dunia

        def tick_dengan_kwarg(events=None, action_cost=False):
            return None

        def tick_positional(events=None):
            return None

        self.assertTrue(dunia._menerima_action_cost(tick_dengan_kwarg))
        self.assertFalse(dunia._menerima_action_cost(tick_positional))


class DiagnostikTest(unittest.TestCase):
    def test_catat_dan_laporan(self):
        diagnostik.kosongkan()
        diagnostik.catat("uji", "pesan", kunci="nilai")
        laporan = diagnostik.laporan()
        self.assertEqual(1, laporan["total"])
        self.assertEqual({"uji": 1}, laporan["per_sumber"])
        self.assertEqual("uji", laporan["terakhir"][-1]["sumber"])

    def test_catat_tidak_pernah_melempar(self):
        diagnostik.catat("uji", object())  # objek tak biasa tetap aman


class TolokTest(unittest.TestCase):
    def test_tolok_json_dan_kode_keluar(self):
        from pycos.dukungan import tolok
        keluaran = io.StringIO()
        with contextlib.redirect_stdout(keluaran):
            kode = tolok.main(["--json"])
        data = json.loads(keluaran.getvalue())
        self.assertEqual(0, kode)
        self.assertTrue(data["ok"])
        nama = {t["nama"] for t in data["tolok"]}
        self.assertTrue({"naluri_tick", "choose_action", "rank_actions", "leksikon"} <= nama)

    def test_ulang_harus_positif(self):
        from pycos.dukungan import tolok
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            tolok.main(["--ulang", "0"])


class PeriksaTest(unittest.TestCase):
    def test_periksa_semua_lulus(self):
        from pycos.dukungan import periksa
        keluaran = io.StringIO()
        with contextlib.redirect_stdout(keluaran):
            kode = periksa.main_periksa(as_json=True)
        data = json.loads(keluaran.getvalue())
        self.assertEqual(0, kode, data)
        self.assertTrue(all(c["ok"] for c in data["cek"]), data)

    def test_periksa_memuat_cek_wajib_lintas_subsistem(self):
        # Cakupan --periksa harus menjangkau seluruh subsistem: inti, kontrak,
        # sumber daya, penilai keselarasan, korpus, dan validator batas.
        from pycos.dukungan import periksa

        nama = {n for n, _ in periksa.CEK}
        wajib = {"impor", "kontrak", "leksikon", "smoke_naluri", "determinisme",
                 "validasi_input", "penilai", "korpus", "validasi_batas"}
        self.assertTrue(wajib.issubset(nama), wajib - nama)

    def test_periksa_gagal_memberi_kode_1(self):
        from pycos.dukungan import periksa
        asli = periksa.CEK
        try:
            periksa.CEK = (("palsu", lambda: "sengaja gagal"),)
            with contextlib.redirect_stdout(io.StringIO()):
                kode = periksa.main_periksa(as_json=False)
        finally:
            periksa.CEK = asli
        self.assertEqual(1, kode)

    def test_python_m_pycos_periksa(self):
        import subprocess
        hasil = subprocess.run([sys.executable, "-m", "pycos", "--periksa"],
                               cwd=AKAR, capture_output=True, text=True, timeout=300)
        self.assertEqual(0, hasil.returncode, hasil.stdout + hasil.stderr[-1500:])
        self.assertIn("semua lulus", hasil.stdout)


class SalienceReproducibilityTest(unittest.TestCase):
    def test_now_diinjeksi_membuat_recency_dapat_diulang(self):
        from pycos.inti.naluri import Naluri

        npc = Naluri(rng_seed=14)
        node = {"importance": 0.5, "metadata": {}, "last_accessed": 100.0}
        baru = npc.salience(node, now=100.0)
        lama = npc.salience(node, now=120.0)

        self.assertEqual(baru, npc.salience(node, now=100.0))
        self.assertGreater(baru, lama)

    def test_now_tidak_berhingga_ditolak(self):
        from pycos.inti.naluri import Naluri

        with self.assertRaisesRegex(ValueError, "berhingga"):
            Naluri(rng_seed=15).salience(
                {"last_accessed": 100.0}, now=float("nan"))


class DemoKognisiTest(unittest.TestCase):
    def test_jejak_dan_setpoint_dipakai_dalam_demo(self):
        from unittest.mock import patch
        from pycos.inti.naluri import Naluri, demo_kognisi

        asli = Naluri.attach_jejak
        dipasang = []

        def pantau(naluri, jejak):
            dipasang.append(jejak)
            return asli(naluri, jejak)

        keluaran = io.StringIO()
        with patch.object(Naluri, "attach_jejak", pantau):
            with contextlib.redirect_stdout(keluaran):
                demo_kognisi(seed=7)

        self.assertEqual(1, len(dipasang))
        self.assertIn("F3 JEJAK:", keluaran.getvalue())
        self.assertIn("setpoint keamanan=", keluaran.getvalue())


class ShimIntegrasiTest(unittest.TestCase):
    """Kegagalan impor lapisan opsional wajib tercatat, bukan senyap."""

    def test_shim_yang_gagal_dicatat_di_diagnostik(self):
        skrip = (
            "import sys\n"
            "sys.modules['pycos.refleksi.nurani'] = None\n"
            "sys.modules['pycos.memori.jejak_prediksi'] = None\n"
            "sys.modules['pycos.bahasa.tutur'] = None\n"
            "import pycos.inti.naluri\n"
            "from pycos.dukungan import diagnostik\n"
            "import json\n"
            "print(json.dumps(diagnostik.laporan()['per_sumber']))\n"
        )
        hasil = subprocess.run([sys.executable, "-c", skrip], cwd=AKAR,
                               capture_output=True, text=True)
        self.assertEqual(0, hasil.returncode, hasil.stderr[-2000:])
        per_sumber = json.loads(hasil.stdout)
        for sumber in ("naluri.shim.nurani", "naluri.shim.jejak",
                       "naluri.shim.tutur"):
            self.assertGreaterEqual(per_sumber.get(sumber, 0), 1, per_sumber)


class AuditPersonaTest(unittest.TestCase):
    def test_pantangan_string_ditolak_di_kedua_jalur(self):
        from pycos.inti.persona import Persona
        for buat in (lambda: Persona("uji", pantangan="bodoh"),
                     lambda: Persona.from_dict({"nama": "uji", "pantangan": "bodoh"})):
            with self.assertRaisesRegex(ValueError, "bukan satu string"):
                buat()

    def test_pantangan_daftar_dinormalisasi_tanpa_mutasi(self):
        from pycos.inti.persona import Persona
        data = {"nama": "uji", "pantangan": ["  BODOH  ", "bodoh", "kejam"]}
        persona = Persona.from_dict(data)
        self.assertEqual(("bodoh", "kejam"), persona.pantangan)
        self.assertEqual(["  BODOH  ", "bodoh", "kejam"], data["pantangan"])
        self.assertEqual(persona, Persona.from_dict(persona.to_dict()))


class AuditTrenTest(unittest.TestCase):
    def test_ambang_tidak_berhingga_ditolak(self):
        from pycos.refleksi.nurani import PelacakSelaras
        for nilai in (float("nan"), float("inf"), -float("inf")):
            with self.subTest(nilai=nilai), self.assertRaises(ValueError):
                PelacakSelaras(ambang_tren=nilai)

    def test_ambang_nol_membedakan_datar_naik_turun(self):
        from pycos.refleksi.nurani import Laporan, PelacakSelaras
        from dataclasses import replace
        from pycos.inti.persona import Keadaan, Persona
        from pycos.refleksi.nurani import nilai_selaras
        dasar = nilai_selaras(Persona("uji"), Keadaan(), "aku senang!")
        self.assertIsInstance(dasar, Laporan)
        for skor, status in (((.5, .5), "stabil"), ((.2, .8), "meningkat"),
                             ((.8, .2), "menurun")):
            with self.subTest(status=status):
                pelacak = PelacakSelaras(min_sampel=2, ambang_tren=0)
                for x in skor:
                    pelacak.catat(replace(dasar, skor=x))
                self.assertEqual(status, pelacak.tren()["keseluruhan"]["status"])


class AuditSnapshotTest(unittest.TestCase):
    def setUp(self):
        diagnostik.kosongkan()
        self.addCleanup(diagnostik.kosongkan)

    def test_detail_laporan_tidak_membocorkan_referensi(self):
        diagnostik.catat("audit", "pesan", alasan="asli")
        laporan = diagnostik.laporan()
        laporan["terakhir"][0]["detail"]["alasan"] = "rusak"
        laporan["per_sumber"]["audit"] = 999
        laporan["terakhir"].clear()
        baru = diagnostik.laporan()
        self.assertEqual("asli", baru["terakhir"][0]["detail"]["alasan"])
        self.assertEqual(1, baru["per_sumber"]["audit"])

    def test_snapshot_tetap_tersedia_setelah_buffer_dikosongkan(self):
        diagnostik.catat("audit", "pesan", alasan="asli")
        laporan = diagnostik.laporan()
        diagnostik.kosongkan()
        self.assertEqual(1, laporan["total"])
        self.assertEqual("asli", laporan["terakhir"][0]["detail"]["alasan"])
        self.assertEqual(0, diagnostik.laporan()["total"])


class AuditRollbackPatchTest(unittest.TestCase):
    def test_metaclass_gagal_memulihkan_slot_dan_semua_tag(self):
        from pycos.dukungan import patching

        class Menolak(type):
            def __setattr__(cls, nama, nilai):
                if nama == "gagal":
                    raise RuntimeError("ditolak metaclass")
                super().__setattr__(nama, nilai)

        def ada(self):
            return 1

        class Target(metaclass=Menolak):
            pass

        Target.ada = ada
        patching.install_methods(Target, {"ada": ada}, patch_id="awal")
        tag_awal = patching._patch_ids(ada)

        def baru(self):
            return 2

        def gagal(self):
            return 3

        with self.assertRaisesRegex(RuntimeError, "ditolak metaclass"):
            patching.install_methods(Target, {"ada": ada, "baru": baru,
                                              "gagal": gagal}, patch_id="audit")
        self.assertIs(Target.ada, ada)
        self.assertFalse(hasattr(Target, "baru"))
        self.assertFalse(hasattr(Target, "gagal"))
        self.assertEqual(tag_awal, patching._patch_ids(ada))
        self.assertFalse(hasattr(baru, "__pycos_patch_ids__"))
        self.assertFalse(hasattr(gagal, "__pycos_patch_ids__"))
        # Metadata gagal tidak boleh menghalangi percobaan yang valid.
        self.assertEqual(("baru",), patching.install_methods(
            Target, {"baru": baru}, patch_id="audit"))
        self.assertEqual((), patching.install_methods(
            Target, {"baru": baru}, patch_id="audit"))


class AuditKognisiTest(unittest.TestCase):
    def test_salinan_clamp_netral_konsisten_dengan_kanonik(self):
        from pycos.mandiri.organik import _kclip
        from pycos.mandiri.kognisi_lanjut import jepit_drive as lokal
        from pycos.lingkungan.dunia import _potong
        for nilai in (True, False, None, "rusak", "0.4", float("nan"),
                      float("inf"), -float("inf"), 10 ** 400, -.3):
            for lo, hi in ((-1., 1.), (.2, .9)):
                for fungsi in (_kclip, lokal, _potong):
                    with self.subTest(fungsi=fungsi.__name__, nilai=nilai, lo=lo):
                        self.assertEqual(jepit(nilai, lo, hi), fungsi(nilai, lo, hi))

    def test_eversi_json_mempertahankan_konfigurasi_dan_lanjutan(self):
        from pycos.mandiri.kognisi_lanjut import EversiTD
        awal = EversiTD(alpha=.2, gamma=.7, laju_eversi=.1, batas_eversi=.2,
                        disonansi_bobot=2, cemas_bobot=3)
        awal.reward_intrinsik(.8, .7)
        awal.update("bahaya", "lari", .5, "aman")
        awal.eversi_param()
        pulih = EversiTD.from_dict(json.loads(json.dumps(awal.to_dict())))
        self.assertEqual(awal.to_dict(), pulih.to_dict())
        self.assertEqual(awal.reward_intrinsik(.4, .2), pulih.reward_intrinsik(.4, .2))
        self.assertEqual(awal.update("aman", "diam", .3, "aman"),
                         pulih.update("aman", "diam", .3, "aman"))
        self.assertEqual(awal.eversi_param(), pulih.eversi_param())

    def test_eversi_save_lama_tetap_dapat_dibaca(self):
        from pycos.mandiri.kognisi_lanjut import EversiTD
        pulih = EversiTD.from_dict({"alpha": .2, "q": {"s": {"a": .3}}})
        self.assertEqual(.35, pulih.laju_eversi)
        self.assertEqual(1., pulih.cemas_bobot)
        self.assertEqual(.3, pulih.nilai("s", "a"))
        self.assertIsNone(pulih.prev)


class AuditCliTest(unittest.TestCase):
    def jalankan(self, *args):
        return subprocess.run([sys.executable, "-m", "pycos", *args], cwd=AKAR,
                              capture_output=True, text=True, timeout=60)

    def test_argumen_asing_dan_mode_bercampur_ditolak(self):
        for args in (("--salah-ketik",), ("--periksa", "--salah-ketik"),
                     ("--periksa", "--teks", "halo"), ("--json",),
                     ("--teks", "halo", "--val", "0.4")):
            with self.subTest(args=args):
                hasil = self.jalankan(*args)
                self.assertEqual(2, hasil.returncode, hasil.stdout + hasil.stderr)
                self.assertIn("error:", hasil.stderr)
                self.assertNotIn("semua lulus", hasil.stdout)

    def test_help_peta_dan_json_periksa_tetap_berfungsi(self):
        bantuan = self.jalankan("--help")
        self.assertEqual(0, bantuan.returncode, bantuan.stderr)
        self.assertIn("--periksa", bantuan.stdout)
        peta = self.jalankan()
        self.assertEqual(0, peta.returncode, peta.stderr)
        self.assertIn("Subpaket:", peta.stdout)
        periksa = self.jalankan("--periksa", "--json")
        self.assertEqual(0, periksa.returncode, periksa.stderr)
        self.assertTrue(json.loads(periksa.stdout)["ok"])


class AuditGrafPersistensiTest(unittest.TestCase):
    def test_konfigurasi_dan_pembelajaran_berikutnya_tetap(self):
        from pycos.mandiri.kognisi_lanjut import GrafAsosiasi
        awal = GrafAsosiasi(laju_hebb=.3, laju_luruh=.02, ambang_fobia=.4,
                            bobot_maks=.9, maks_node=7, maks_tepi=9)
        awal.koaktifkan("api", "takut")
        pulih = GrafAsosiasi.from_dict(json.loads(json.dumps(awal.to_dict())))
        self.assertEqual(awal.to_dict(), pulih.to_dict())
        self.assertEqual(awal.koaktifkan("api", "takut"),
                         pulih.koaktifkan("api", "takut"))
        awal.luruh(.5)
        pulih.luruh(.5)
        self.assertEqual(awal.to_dict(), pulih.to_dict())

    def test_nama_dengan_pemisah_tidak_menggabungkan_tepi(self):
        from pycos.mandiri.kognisi_lanjut import GrafAsosiasi
        awal = GrafAsosiasi()
        awal.koaktifkan("a|b", "c", gain=.5)
        awal.koaktifkan("a", "b|c", gain=1.)
        pulih = GrafAsosiasi.from_dict(json.loads(json.dumps(awal.to_dict())))
        self.assertEqual(2, len(pulih.edge))
        self.assertEqual(awal.edge, pulih.edge)

    def test_save_lama_dan_snapshot_log_terisolasi(self):
        from pycos.mandiri.kognisi_lanjut import GrafAsosiasi
        graf = GrafAsosiasi.from_dict({"edge": {"api|takut": .6}})
        self.assertEqual(.6, graf.bobot("api", "takut"))
        self.assertEqual(.18, graf.laju_hebb)
        graf.asosiasi_terbentuk = [{"a": "api", "b": "takut", "bobot": .6}]
        data = graf.to_dict()
        data["asosiasi_terbentuk"][0]["a"] = "rusak"
        self.assertEqual("api", graf.asosiasi_terbentuk[0]["a"])
        data = graf.to_dict()
        pulih = GrafAsosiasi.from_dict(data)
        data["asosiasi_terbentuk"][0]["a"] = "rusak"
        self.assertEqual("api", pulih.asosiasi_terbentuk[0]["a"])


class AuditPenyebaranTest(unittest.TestCase):
    def graf(self):
        from pycos.mandiri.kognisi_lanjut import GrafAsosiasi
        graf = GrafAsosiasi()
        graf.edge = {("a", "b"): 1., ("b", "c"): 1., ("c", "d"): 1.}
        return graf

    def test_jumlah_hop_dan_atenuasi(self):
        self.assertEqual({"a": 1.}, self.graf().aktifkan("a", sebar=0))
        self.assertEqual({"a": 1., "b": .8}, self.graf().aktifkan("a", sebar=1))
        hasil = self.graf().aktifkan("a", sebar=2)
        self.assertEqual({"a", "b", "c"}, set(hasil))
        self.assertAlmostEqual(.64, hasil["c"])
        self.assertAlmostEqual(.8, hasil["b"])

    def test_siklus_tidak_memompa_aktivasi(self):
        graf = self.graf()
        graf.edge[("a", "c")] = 1.
        hasil = graf.aktifkan("a", energi=.5, sebar=100)
        self.assertEqual(.5, hasil["a"])
        self.assertEqual(.4, hasil["b"])
        self.assertEqual(.4, hasil["c"])
        self.assertAlmostEqual(.32, hasil["d"])

    def test_ambang_dan_urutan_tepi_tidak_mengubah_hasil(self):
        graf = self.graf()
        graf.edge[("a", "lemah")] = .01
        balik = self.graf()
        balik.edge = dict(reversed(list(graf.edge.items())))
        self.assertEqual(graf.aktifkan("a", sebar=3), balik.aktifkan("a", sebar=3))
        self.assertNotIn("lemah", graf.aktivasi)


class AuditResumeKognisiTest(unittest.TestCase):
    def test_rng_dan_gaussian_cache_melanjutkan_drift_setelah_json(self):
        from pycos.mandiri.kognisi_lanjut import KognisiLanjut
        awal = KognisiLanjut(seed=19).aktifkan(drift=True, asosiasi=True, eversi=True)
        levels = {"energi": -.2}
        emosi = {"takut": .3}
        awal.langkah(levels, emosi, .2)
        self.assertIsNotNone(awal.rng.getstate()[2])  # pasangan gauss tersisa
        global_rng = __import__("random").getstate()
        pulih = KognisiLanjut.from_dict(json.loads(json.dumps(awal.to_dict())))
        self.assertEqual(global_rng, __import__("random").getstate())
        levels_b, emosi_b = dict(levels), dict(emosi)
        for _ in range(10):
            self.assertEqual(awal.langkah(levels, emosi, .1),
                             pulih.langkah(levels_b, emosi_b, .1))
            self.assertEqual(levels, levels_b)
            self.assertEqual(emosi, emosi_b)
        self.assertEqual(awal.rng.getstate(), pulih.rng.getstate())

    def test_rng_save_lama_dan_state_rusak(self):
        from pycos.mandiri.kognisi_lanjut import KognisiLanjut
        self.assertEqual(KognisiLanjut().rng.getstate(),
                         KognisiLanjut.from_dict({}).rng.getstate())
        valid = KognisiLanjut().to_dict()["rng_state"]
        for state in (None, [], [3, None, None], [3, [], None],
                      [valid[0], valid[1], "rusak"],
                      [valid[0], valid[1], float("nan")]):
            with self.subTest(state=state), self.assertRaises(ValueError):
                KognisiLanjut.from_dict({"rng_state": state})

    def test_transisi_td_naluri_tidak_hilang_saat_load(self):
        from pycos.inti.naluri import Naluri, _naluri_kog_step
        awal = Naluri(rng_seed=37)
        awal.enable_eversi()
        awal.enable_latent_drift()
        awal.tick()
        pulih = Naluri.from_json(awal.to_json())
        self.assertEqual(awal._kog_prev, pulih._kog_prev)
        # Isolasi langkah kognisi dari RNG subsistem NPC lain.
        _naluri_kog_step(awal)
        _naluri_kog_step(pulih)
        self.assertEqual(awal.kognisi_state(), pulih.kognisi_state())
        self.assertEqual(awal.levels, pulih.levels)
        data = awal.to_dict()
        data.pop("kognisi_prev")
        self.assertIsNone(Naluri.from_dict(data)._kog_prev)


class AuditGeneratorTest(unittest.TestCase):
    def jalankan(self, root, output, *args):
        return subprocess.run([sys.executable, os.path.join(AKAR, "tools/audit_python.py"),
                               "--root", root, "--output", output, *args],
                              capture_output=True, text=True, timeout=60)

    def test_semua_berkas_termasuk_init_demo_private_dan_nested(self):
        with tempfile.TemporaryDirectory() as root:
            os.makedirs(os.path.join(root, "nested"))
            sources = {"__init__.py": "", "demo.py": "def demo(): pass",
                       "nested/private.py": "def _luar():\n def dalam(): pass\n"}
            for nama, isi in sources.items():
                with open(os.path.join(root, nama), "w", encoding="utf-8") as f:
                    f.write(isi)
            output = os.path.join(root, "audit.md")
            hasil = self.jalankan(root, output)
            self.assertEqual(0, hasil.returncode, hasil.stdout + hasil.stderr)
            with open(output, encoding="utf-8") as f:
                teks = f.read()
            for nama in sources:
                self.assertIn("## `{}`".format(nama), teks)
            self.assertIn("_luar.dalam", teks)
            self.assertEqual(0, self.jalankan(root, output, "--check").returncode)

    def test_check_mendeteksi_source_berubah(self):
        with tempfile.TemporaryDirectory() as root:
            output = os.path.join(root, "audit.md")
            self.assertEqual(0, self.jalankan(root, output).returncode)
            with open(os.path.join(root, "baru.py"), "w", encoding="utf-8") as f:
                f.write("x = 1\n")
            self.assertEqual(1, self.jalankan(root, output, "--check").returncode)
            self.assertEqual(0, self.jalankan(root, output).returncode)
            self.assertEqual(0, self.jalankan(root, output, "--check").returncode)

    def test_syntax_error_tidak_dilewati_dan_dilaporkan_semua(self):
        with tempfile.TemporaryDirectory() as root:
            for nama in ("rusak_a.py", "rusak_b.py"):
                with open(os.path.join(root, nama), "w", encoding="utf-8") as f:
                    f.write("def !")
            output = os.path.join(root, "audit.md")
            hasil = self.jalankan(root, output)
            self.assertEqual(1, hasil.returncode)
            self.assertIn("rusak_a.py", hasil.stdout)
            self.assertIn("rusak_b.py", hasil.stdout)
            self.assertFalse(os.path.exists(output))


class RekomendasiStateTest(unittest.TestCase):
    def test_domain_naluri_ditolak_dengan_nama_field(self):
        from pycos.inti import Naluri
        for field, value in (("levels", {"energi": 99.}),
                             ("urgency", {"energi": 1e9}),
                             ("tick_count", -1), ("tick_count", True),
                             ("subjective_tick_count", -1.),
                             ("levels", {"asing": .2})):
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, field):
                Naluri.from_dict({field: value})

    def test_nurani_jejak_dan_pemilik_state_lain_memakai_gate(self):
        from pycos.inti import Naluri, KawananNPC
        from pycos.refleksi import Nurani
        from pycos.memori import JejakPrediksi
        n = Naluri(rng_seed=1)
        loaders = (Nurani.from_dict, JejakPrediksi.from_dict, KawananNPC.from_dict,
                   n.kesadaran.from_dict, n.presentasi.from_dict, n.ritual.from_dict,
                   KawananNPC()._reputasi.from_dict)
        for loader in loaders:
            with self.subTest(loader=loader), self.assertRaisesRegex(ValueError, "clock"):
                loader({"clock": -1})

    def test_invalid_nested_ditolak_sebelum_fallback_atau_mutasi(self):
        from pycos.inti import Naluri
        n = Naluri(rng_seed=2)
        before = n.kesadaran.to_dict()
        with self.assertRaisesRegex(ValueError, "tick_count"):
            n.kesadaran.from_dict({"timeline": [{"tick_count": -1}]})
        self.assertEqual(before, n.kesadaran.to_dict())
        with self.assertRaisesRegex(ValueError, "levels"):
            Naluri.from_dict({"nurani": {"levels": {"energi": 99}}})

    def test_roundtrip_dan_field_lama_tetap_diterima(self):
        from pycos.inti import Naluri
        n = Naluri(rng_seed=3)
        n.tick()
        self.assertEqual(n.levels, Naluri.from_json(n.to_json()).levels)
        self.assertEqual(0, Naluri.from_dict({}).tick_count)


class RekomendasiFormatTest(unittest.TestCase):
    def test_migrasi_naluri_3_ke_4_tanpa_mutasi_input(self):
        from pycos.inti import Naluri
        data = {"format": "naluri/3", "tick_count": 7, "levels": {"energi": .2}}
        before = json.dumps(data)
        hasil = Naluri.migrate(data)
        self.assertEqual("naluri/4", hasil["format"])
        self.assertEqual(7, hasil["subjective_tick_count"])
        self.assertEqual(before, json.dumps(data))
        self.assertEqual(.2, Naluri.from_dict(data).levels["energi"])

    def test_semua_format_baru_tidak_dikenal_ditolak(self):
        from pycos.dukungan.validasi_state import FORMAT_TERBARU, validasi_state
        from pycos.mandiri import GrafAsosiasi
        for nama, fmt in FORMAT_TERBARU.items():
            buruk = fmt.split("/")[0] + "/999"
            with self.subTest(nama=nama), self.assertRaisesRegex(ValueError, "format"):
                validasi_state({"format": buruk}, nama)
        with self.assertRaisesRegex(ValueError, "format"):
            GrafAsosiasi.from_dict({"format": "graf_asosiasi/999"})

    def test_format_nested_tidak_disembunyikan_fallback(self):
        from pycos.inti import Naluri, KawananNPC
        with self.assertRaisesRegex(ValueError, "nurani/999"):
            Naluri.from_dict({"nurani": {"format": "nurani/999"}})
        with self.assertRaisesRegex(ValueError, "naluri/999"):
            KawananNPC.from_dict({"npcs": {"uji": {"format": "naluri/999"}}})
        self.assertEqual("kawanan/5", KawananNPC.format_versi)

    def test_registry_mendukung_rantai_migrasi(self):
        from unittest.mock import patch
        from pycos.dukungan import validasi_state as state
        def ke_3(data):
            return dict(data, format="naluri/3")
        with patch.dict(state.MIGRASI, {("naluri/2", "naluri/3"): ke_3}):
            hasil = state.migrasi({"format": "naluri/2", "tick_count": 9}, "naluri/4")
        self.assertEqual("naluri/4", hasil["format"])
        self.assertEqual(9, hasil["subjective_tick_count"])


class RekomendasiAtomicTest(unittest.TestCase):
    def test_gagal_replace_menjaga_save_lama_dan_membersihkan_temp(self):
        from unittest.mock import patch
        from pycos.inti import Naluri, KawananNPC
        from pycos.memori import JejakPrediksi
        kasus = [(obj, tahap) for obj in (Naluri(rng_seed=1), KawananNPC(), JejakPrediksi())
                 for tahap in ("replace", "fsync")]
        for obj, tahap in kasus:
            with self.subTest(obj=type(obj).__name__, tahap=tahap), tempfile.TemporaryDirectory() as tmp:
                path = os.path.join(tmp, "save.json")
                obj.save(path)
                with open(path, "rb") as f:
                    sebelum = f.read()
                with patch("pycos.dukungan.persistensi.os." + tahap, side_effect=OSError("putus")):
                    with self.assertRaises(OSError):
                        obj.save(path)
                with open(path, "rb") as f:
                    self.assertEqual(sebelum, f.read())
                self.assertEqual(["save.json"], os.listdir(tmp))
                type(obj).load(path)

    def test_checksum_salah_dan_legacy(self):
        from pycos.inti import Naluri
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "save.json")
            n = Naluri(name="uji", rng_seed=3)
            n.save(path)
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            self.assertIn("_sha256", data)
            data["name"] = "rusak"
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f)
            with self.assertRaisesRegex(ValueError, "checksum"):
                Naluri.load(path)
            data["_sha256"] = "å" * 64
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f)
            with self.assertRaisesRegex(ValueError, "checksum"):
                Naluri.load(path)
            with open(path, "w", encoding="utf-8") as f:
                f.write(n.to_json())
            self.assertEqual("uji", Naluri.load(path).name)

    def test_serialisasi_gagal_tidak_memotong_target(self):
        from pycos.dukungan.persistensi import simpan_json
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "save.json")
            with open(path, "w", encoding="utf-8") as f:
                f.write("lama")
            with self.assertRaises(ValueError):
                simpan_json(path, {"nilai": float("nan")})
            with open(path, encoding="utf-8") as f:
                self.assertEqual("lama", f.read())
            self.assertEqual(["save.json"], os.listdir(tmp))


class RekomendasiSerapTest(unittest.TestCase):
    def test_serap_mempertahankan_identitas_dan_konfigurasi(self):
        from pycos.inti import Naluri, KawananNPC
        n = Naluri(name="Sari", rng_seed=5)
        n.delta("energi", -.3)
        sebelum = dict(n.levels)
        kawanan = KawananNPC()
        self.assertIs(n, kawanan.serap(n, position=(1, 2)))
        self.assertIs(n, kawanan.npcs["Sari"])
        self.assertIs(kawanan, n.kawanan)
        self.assertEqual(sebelum, n.levels)
        self.assertEqual([1., 2.], kawanan.position_of("Sari"))
        with self.assertRaises(ValueError):
            kawanan.tambah_npc(n)
        with self.assertRaises(ValueError):
            KawananNPC().serap(n)

    def test_objek_pada_flag_ditolak_dan_gagal_posisi_tidak_mendaftar(self):
        from pycos.inti import Naluri, KawananNPC
        n = Naluri(name="Sari")
        k = KawananNPC()
        with self.assertRaisesRegex(TypeError, "serap"):
            k.tambah("uji", npc=n)
        with self.assertRaises(ValueError):
            k.serap(n, position=(float("nan"), 1))
        self.assertEqual({}, k.npcs)
        self.assertEqual({}, k.positions)
        self.assertIsNone(getattr(n, "kawanan", None))

    def test_posisional_legacy_mendapat_deprecation(self):
        from pycos.inti import KawananNPC
        with self.assertWarns(DeprecationWarning):
            n = KawananNPC().tambah("lama", None, True)
        self.assertEqual("lama", n.name)


class RekomendasiAuditScopeTest(unittest.TestCase):
    def test_dependency_dan_build_tidak_mengubah_check(self):
        tool = os.path.join(AKAR, "tools/audit_python.py")
        with tempfile.TemporaryDirectory() as root:
            output = os.path.join(root, "audit.md")
            args = [sys.executable, tool, "--root", root, "--output", output]
            awal = subprocess.run(args, capture_output=True, text=True)
            self.assertEqual(0, awal.returncode, awal.stdout + awal.stderr)
            for folder in (".venv", "build", "node_modules", "site-packages"):
                os.mkdir(os.path.join(root, folder))
                with open(os.path.join(root, folder, "rusak.py"), "w", encoding="utf-8") as f:
                    f.write("def !")
            hasil = subprocess.run(args + ["--check"], capture_output=True, text=True)
            self.assertEqual(0, hasil.returncode, hasil.stdout + hasil.stderr)
            # Source proyek biasa tetap terpantau, bukan hanya file tracked git.
            with open(os.path.join(root, "source_baru.py"), "w", encoding="utf-8") as f:
                f.write("x = 1")
            hasil = subprocess.run(args + ["--check"], capture_output=True, text=True)
            self.assertEqual(1, hasil.returncode)

class RekomendasiEventTest(unittest.TestCase):
    def setUp(self):
        diagnostik.kosongkan()

    def test_longgar_mencatat_typo_tanpa_mengubah_level(self):
        from pycos.inti import Naluri
        n = Naluri(rng_seed=1)
        awal = dict(n.levels)
        n.apply_events([{"drive": "energii", "delta": .2, "dleta": .1}])
        self.assertEqual(awal, n.levels)
        laporan = diagnostik.laporan()
        self.assertIn("energii", laporan["terakhir"][-1]["pesan"])
        self.assertIn("dleta", laporan["terakhir"][-1]["pesan"])

    def test_strict_menolak_batch_sebelum_mutasi(self):
        from pycos.inti import Naluri
        n = Naluri(params={"strict_events": True})
        awal = n.to_dict()
        with self.assertRaisesRegex(ValueError, r"events\[1\]"):
            n.apply_events([{"drive": "energi", "delta": .2}, {"dleta": .2}])
        self.assertEqual(awal, n.to_dict())
        self.assertGreater(diagnostik.laporan()["total"], 0)

    def test_non_mapping_dan_drive_non_teks_menyebut_indeks(self):
        from pycos.inti import Naluri
        for buruk in (None, 2, "event", {"drive": []}):
            with self.subTest(buruk=buruk), self.assertRaisesRegex(ValueError, r"events\[0\]"):
                Naluri().apply_events([buruk])

    def test_generator_dan_event_emosi_tanpa_drive(self):
        from pycos.inti import Naluri
        n = Naluri(params={"strict_events": True})
        n.apply_events(iter([{"drive": "energi", "delta": .2}, {"emosi": "takut"}]))
        self.assertAlmostEqual(.2, n.levels["energi"])

    def test_persepsi_tetap_menerima_generator(self):
        from unittest.mock import patch
        from pycos.inti import Naluri
        n = Naluri()
        with patch.object(n, "_persepsi_aktif", return_value=True), \
                patch.object(n, "_persepsi_batch", side_effect=lambda evs: evs) as batch:
            n.apply_events(iter([{"drive": "energi", "delta": .2}]))
        self.assertEqual(1, len(batch.call_args[0][0]))
        self.assertAlmostEqual(.2, n.levels["energi"])


class RekomendasiParameterTest(unittest.TestCase):
    def test_lima_salah_ketik_atau_tipe(self):
        from pycos.inti import Naluri
        kasus = {"enable_emosi_typo": True, "decay_per_tick": "x",
                 "urgency_alpha": "0.3", "max_goal": 4, "strict_events": "yes"}
        for key, val in kasus.items():
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, key):
                Naluri(params={key: val}, validate_params=True)

    def test_seluruh_default_dan_tipe_registry(self):
        from pycos.inti.naluri import DEFAULTS, Naluri
        from pycos.dukungan.parameter import PARAM_SPEC
        self.assertEqual(set(DEFAULTS), set(PARAM_SPEC))
        for key, val in DEFAULTS.items():
            self.assertIs(type(val), PARAM_SPEC[key][1])
        n = Naluri(params=DEFAULTS, validate_params=True)
        self.assertIsNot(n.params, DEFAULTS)

    def test_angka_bool_nan_inf_dan_rentang(self):
        from pycos.inti import Naluri
        for key, val in (("urgency_alpha", True), ("urgency_alpha", 2),
                         ("decay_per_tick", float("nan")), ("decay_per_tick", float("inf")),
                         ("max_goals", 2.5), ("enable_emosi", 1)):
            with self.subTest(key=key, val=val), self.assertRaisesRegex(ValueError, key):
                Naluri(params={key: val}, validate_params=True)

    def test_default_tetap_longgar_untuk_ekstensi_host(self):
        from pycos.inti import Naluri
        self.assertEqual(1, Naluri(params={"host_extension": 1}).params["host_extension"])

    def test_input_tidak_dimutasi_dan_mapping_wajib(self):
        from pycos.dukungan.parameter import periksa_params
        from pycos.inti import Naluri
        data = {"urgency_alpha": .3}
        periksa_params(data)
        Naluri(params=data, validate_params=True)
        self.assertEqual({"urgency_alpha": .3}, data)
        for buruk in ([], False, "params"):
            with self.assertRaisesRegex(ValueError, "params"):
                Naluri(params=buruk, validate_params=True)


class RekomendasiNamaTest(unittest.TestCase):
    def test_fitur_kesadaran_asing_tidak_memutasi_params(self):
        from pycos.inti import Naluri
        n = Naluri()
        awal = dict(n.params)
        with self.assertRaisesRegex(ValueError, "typo"):
            n.enable_kesadaran("inner_speech", "typo")
        self.assertEqual(awal, n.params)

    def test_alias_dan_semua_fitur_masih_bekerja(self):
        from pycos.inti import Naluri
        n = Naluri()
        self.assertTrue(n.enable_kesadaran("audisi_diri")["self_audition"])
        self.assertTrue(n.enable_kesadaran()["global_workspace"])
        self.assertFalse(n.enable_kesadaran(semua=False)["enable_kesadaran"])

    def test_nama_npc_asing_di_dunia_adalah_valueerror(self):
        from pycos.lingkungan.dunia import Lingkungan
        dunia = Lingkungan()
        for fn in (dunia.observasi, dunia.langkah):
            with self.assertRaisesRegex(ValueError, "Hilang"):
                fn("Hilang")


class RekomendasiDiagnostikTest(unittest.TestCase):
    def setUp(self):
        diagnostik.kosongkan()

    def test_galat_wrapper_dicatat_dan_tetap_diteruskan(self):
        from pycos.dukungan.patching import wrap_method
        class Target:
            def fn(self):
                return 1
        def rusak(original, self):
            raise RuntimeError("uji wrapper")
        wrap_method(Target, "fn", rusak, patch_id="uji.wrapper")
        with self.assertRaisesRegex(RuntimeError, "uji wrapper"):
            Target().fn()
        self.assertEqual(1, diagnostik.laporan()["per_sumber"]["uji.wrapper"])

    def test_galat_di_dalam_wrapper_fallback_terlihat(self):
        from unittest.mock import patch
        from pycos.inti import naluri
        n = naluri.Naluri()
        with patch.object(naluri, "_kausal_step", side_effect=RuntimeError("uji internal")):
            self.assertEqual("hasil", naluri._kausal_tick(lambda *a, **k: "hasil", n))
        entri = diagnostik.laporan()["terakhir"][-1]
        self.assertEqual("naluri._kausal_tick", entri["sumber"])
        self.assertIn("uji internal", entri["detail"]["galat"])

    def test_health_dan_cli_json_memuat_laporan(self):
        from pycos.inti import Naluri
        from pycos.dukungan import periksa
        diagnostik.catat("uji.host", "masalah host")
        self.assertIn("uji.host", Naluri().health_check()["diagnostik"]["per_sumber"])
        keluaran = io.StringIO()
        with contextlib.redirect_stdout(keluaran):
            self.assertEqual(0, periksa.main_periksa(as_json=True))
        laporan = json.loads(keluaran.getvalue())
        self.assertIn("uji.host", laporan["diagnostik"]["per_sumber"])
        self.assertIn("validasi_event", {c["cek"] for c in laporan["cek"]})

    def test_tick_organik_memanggil_helper_dan_tidak_menyembunyikan_attributeerror(self):
        from unittest.mock import patch
        from pycos.inti import naluri
        n = naluri.Naluri(rng_seed=1)
        diagnostik.kosongkan()
        n.tick()
        self.assertEqual(0, diagnostik.laporan()["total"])
        with patch.object(naluri, "_organik_tubuh_langkah", return_value={}) as langkah:
            n.tick()
        langkah.assert_called_once_with(n)

    def test_delta_tubuh_pas_check_fisika_tetap_dalam_domain_snapshot(self):
        from types import SimpleNamespace
        from unittest.mock import Mock
        from pycos.inti import naluri
        n = naluri.Naluri(initial_levels={"keamanan": -1.0})
        n._organik = SimpleNamespace(tubuh=SimpleNamespace(
            langkah=Mock(return_value={"keamanan": -.03})))
        naluri._organik_tubuh_langkah(n)
        self.assertEqual(-1.0, n.levels["keamanan"])
        self.assertEqual(0.0, n.delta_log[-1]["amount"])

    def test_semua_handler_broad_naluri_memiliki_kanal_diagnostik(self):
        import ast
        # Kontrak diagnostik juga mencakup kelas yang dipindahkan (R4.1).
        handlers = []
        for module in ("naluri", "mesin", "kesadaran", "presentasi", "ritual", "reputasi", "kawanan", "ekstensi/pelindung", "ekstensi/kognisi", "ekstensi/organik",
                       "ekstensi/gejala", "ekstensi/invensi", "ekstensi/kausal", "ekstensi/perencana", "ekstensi/ketidaktahuan"):
            with open(os.path.join(AKAR, "pycos/inti", module + ".py"), encoding="utf-8") as f:
                root = ast.parse(f.read())
            handlers.extend(n for n in ast.walk(root) if isinstance(n, ast.ExceptHandler)
                            and isinstance(n.type, ast.Name) and n.type.id == "Exception")
        self.assertGreater(len(handlers), 200)
        for handler in handlers:
            self.assertTrue(any(isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                                and isinstance(n.func.value, ast.Name)
                                and n.func.value.id == "_diag" and n.func.attr == "catat"
                                for stmt in handler.body for n in ast.walk(stmt)), handler.lineno)

class RekomendasiProfilTest(unittest.TestCase):
    def test_penuh_tetap_default_dan_profil_asing_ditolak(self):
        from pycos.inti import Naluri, KawananNPC
        for obj in (Naluri(rng_seed=7), KawananNPC()):
            self.assertEqual(obj.to_dict(), obj.to_dict(profil="penuh"))
            with self.assertRaisesRegex(ValueError, "profil"):
                obj.to_dict(profil="typo")

    def test_log_dibuang_tetapi_pasangan_kalibrasi_tetap_ada(self):
        from pycos.inti import Naluri
        n = Naluri(rng_seed=2)
        n._pred_pairs = [(.2, .5)] * 20
        for _ in range(10):
            n.tick()
        n.delta("energi", .1)
        penuh = n.to_dict()
        simpan = n.to_dict(profil="simpan")
        for key in ("tick_history", "delta_log", "prediction_log"):
            self.assertNotIn(key, simpan)
        self.assertEqual(penuh["pred_pairs"], simpan["pred_pairs"])
        self.assertEqual(penuh, n.to_dict())
        self.assertNotIn("emosi_log", n.to_dict(profil="minimal"))

    def test_referensi_diff_custom_dan_penghapusan_lexicon(self):
        from pycos.inti import Naluri
        from pycos.inti.naluri import LEXICON
        n = Naluri(params={"urgency_alpha": .4, "host": {"nested": 3}}, rng_seed=1)
        n.lexicon.pop(next(iter(LEXICON)))
        n.lexicon["baru"] = {"energi": .3}
        n.tag_lexicon["custom"] = {"afiliasi": .2}
        data = n.to_dict(profil="simpan")
        self.assertEqual({"urgency_alpha", "host"}, set(data["params"]))
        loaded = Naluri.from_dict(data)
        self.assertEqual(n.lexicon, loaded.lexicon)
        self.assertEqual(n.tag_lexicon, loaded.tag_lexicon)
        self.assertEqual(n.params, loaded.params)
        self.assertEqual("naluri/4-simpan", data["format"])
        loaded.params["host"]["nested"] = 5
        self.assertEqual(3, n.params["host"]["nested"])

    def test_urutan_lexicon_custom_dipertahankan(self):
        from pycos.inti import Naluri
        n = Naluri(rng_seed=2)
        n.lexicon = dict(reversed(list(n.lexicon.items())))
        n.tag_lexicon = dict(reversed(list(n.tag_lexicon.items())))
        other = Naluri.from_dict(n.to_dict(profil="simpan"))
        self.assertEqual(list(n.lexicon), list(other.lexicon))
        self.assertEqual(list(n.tag_lexicon), list(other.tag_lexicon))
        self.assertEqual(n.impact_of("makan tidur teman aman"), other.impact_of("makan tidur teman aman"))

    def test_referensi_rusak_atau_bawaan_berubah_ditolak(self):
        from copy import deepcopy
        from unittest.mock import patch
        from pycos.inti import Naluri
        from pycos.inti.naluri import DEFAULTS
        data = Naluri().to_dict(profil="simpan")
        for perubahan in ("id", "hapus", "urutan"):
            buruk = deepcopy(data)
            buruk["referensi"]["lexicon"][perubahan] = ["tidak-ada"]
            with self.subTest(perubahan=perubahan), self.assertRaisesRegex(ValueError, "referensi"):
                Naluri.from_dict(buruk)
        with patch.dict(DEFAULTS, {"decay_per_tick": .9}):
            with self.assertRaisesRegex(ValueError, "referensi"):
                Naluri.from_dict(data)

    def test_format_referensi_tidak_boleh_disamarkan_sebagai_penuh(self):
        from pycos.inti import Naluri
        for fmt in ("naluri/4", None):
            data = Naluri().to_dict(profil="simpan")
            if fmt is None:
                data.pop("format")
            else:
                data["format"] = fmt
            with self.assertRaisesRegex(ValueError, "format"):
                Naluri.from_dict(data)

    def test_file_json_dan_kawanan_meneruskan_profil(self):
        from pycos.inti import Naluri, KawananNPC
        k = KawananNPC()
        k.serap(Naluri(name="Sari", rng_seed=8), position=(1, 2))
        for obj in (k.npcs["Sari"], k):
            for profil in ("simpan", "minimal"):
                with self.subTest(owner=type(obj).__name__, profil=profil):
                    data = obj.to_dict(profil=profil)
                    other = type(obj).from_json(obj.to_json(profil=profil))
                    self.assertEqual(data, other.to_dict(profil=profil))
                    with tempfile.TemporaryDirectory() as tmp:
                        path = os.path.join(tmp, "snapshot.json")
                        obj.save(path, profil=profil)
                        self.assertEqual(data, type(obj).load(path).to_dict(profil=profil))

    def test_200_tick_dan_kalibrasi_setara_penuh_pada_fixture_aktif(self):
        from pycos.inti import Naluri
        from pycos.inti.naluri import DEFAULTS
        params = {k: True for k, v in DEFAULTS.items()
                  if k.startswith("enable_") and isinstance(v, bool)}
        n = Naluri(params=params, rng_seed=7, name="Sari")
        n.enable_eversi()
        n.enable_latent_drift()
        n.enable_asosiasi()
        n.enable_kausal()
        n.enable_invensi()
        n._pred_pairs = [(.2, .5), (.3, .1)] * 10
        for _ in range(10):
            n.tick()
        for profil in ("simpan", "minimal"):
            a = Naluri.from_dict(n.to_dict())
            b = Naluri.from_dict(n.to_dict(profil=profil))
            for tick in range(200):
                events = [{"drive": "energi", "delta": .02}]
                a.tick(events=events)
                b.tick(events=events)
                # Akses skala benar-benar menggunakan pasangan kalibrasi.
                self.assertEqual(a.estimate_scale(), b.estimate_scale(), (profil, tick))
                self.assertEqual(a.to_dict(profil=profil), b.to_dict(profil=profil), (profil, tick))

    def test_tolok_memuat_waktu_dan_byte_profil(self):
        from pycos.dukungan.tolok import _tolok_to_dict_simpan
        hasil = _tolok_to_dict_simpan(1)
        self.assertTrue(hasil["ok"])
        self.assertLess(hasil["byte_simpan"], hasil["byte_penuh"])

class RekomendasiRetrievalTest(unittest.TestCase):
    def memori(self, jumlah=30):
        from pycos.memori import JejakPrediksi
        j = JejakPrediksi(half_life_ticks=0, memory_retention_half_life=0, rng_seed=4)
        for i in range(jumlah):
            j.record_experience("api lorong kejadian {}".format(i), "lari",
                                {"impact": -.2}, tick=i, sync_nurani=False)
        return j

    def test_batas_similarity_dan_laporan_pemotongan(self):
        from unittest.mock import patch
        from pycos.memori import jejak_prediksi as modul
        j = self.memori()
        with patch.object(modul, "_similarity", wraps=modul._similarity) as sim:
            p = j.predict("api lorong", max_candidates=5)
        b = p["retrieval_budget"]
        self.assertEqual(30, b["indexed_candidates"])
        self.assertEqual(25, b["budget_pruned"])
        self.assertEqual(5, b["similarity_evaluations"])
        self.assertTrue(b["truncated"])
        self.assertEqual(5, sim.call_count)
        p["retrieval_budget"]["truncated"] = False
        self.assertTrue(j.performance_report()["last_budget"]["truncated"])

    def test_recency_diperiksa_sebelum_similarity_dan_recall(self):
        j = self.memori()
        p = j.predict("api lorong", tick=30, max_age_ticks=2)
        self.assertEqual(28, p["retrieval_budget"]["age_pruned"])
        self.assertEqual(2, p["retrieval_budget"]["similarity_evaluations"])
        self.assertEqual(0, j._episodes[0]["last_access_tick"])
        self.assertFalse(p["memory"]["hole"])

    def test_kandidat_terbaru_deterministik_setelah_load(self):
        from pycos.memori import JejakPrediksi
        j = self.memori()
        a = j._retrieve("api lorong", None, 30, max_candidates=3)
        self.assertEqual({28, 29, 30}, {ep["id"] for ep in a})
        loaded = JejakPrediksi.from_dict(j.to_dict())
        b = loaded._retrieve("api lorong", None, 30, max_candidates=3)
        self.assertEqual([ep["id"] for ep in a], [ep["id"] for ep in b])

    def test_batas_besar_setara_mode_legacy(self):
        from pycos.memori import JejakPrediksi
        j = self.memori()
        other = JejakPrediksi.from_dict(j.to_dict())
        a = j.predict("api lorong")
        b = other.predict("api lorong", max_candidates=100)
        self.assertEqual(a["forecast"], b["forecast"])
        self.assertEqual(a["memory"], b["memory"])
        self.assertFalse(a["retrieval_budget"]["truncated"])

    def test_rank_actions_membatasi_setiap_retrieval_dan_aksi(self):
        j = self.memori()
        hasil = j.rank_actions("api lorong", [{"name": "lari"}, {"name": "diam"},
                                             {"name": "padamkan"}],
                               max_candidates=4, max_actions=2)
        budget = hasil["retrieval_budget"]
        self.assertEqual(1, budget["actions_pruned"])
        self.assertEqual(2, len(hasil["ranked"]))
        self.assertEqual(4, len(budget["retrievals"]))
        self.assertTrue(all(b["similarity_evaluations"] <= 4 for b in budget["retrievals"]))
        self.assertTrue(budget["truncated"])

    def test_opsi_buruk_ditolak_sebelum_mutasi(self):
        j = self.memori(2)
        for nama in ("max_candidates", "max_age_ticks", "max_actions"):
            for val in (True, -1, 1.5, "5"):
                awal = j.to_dict()
                with self.subTest(nama=nama, val=val), self.assertRaisesRegex(ValueError, nama):
                    j.rank_actions("api", [], **{nama: val})
                self.assertEqual(awal, j.to_dict())
        with self.assertRaisesRegex(ValueError, "max_candidates"):
            j.predict("api", max_candidates=0)
        with self.assertRaisesRegex(ValueError, "max_actions"):
            j.rank_actions("api", [], max_actions=0)
        self.assertTrue(j.predict("api", max_age_ticks=0)["retrieval_budget"]["truncated"])

    def test_query_tanpa_hit_mereset_laporan(self):
        j = self.memori()
        j.predict("api lorong", max_candidates=2)
        p = j.predict("zzzunrelated", max_candidates=2)
        self.assertEqual(0, p["retrieval_budget"]["similarity_evaluations"])
        self.assertFalse(p["retrieval_budget"]["truncated"])
        self.assertFalse(j.rank_actions("api", [], max_actions=2)["retrieval_budget"]["truncated"])

    def test_lubang_memori_mati_tetap_dibedakan_dari_pemotongan(self):
        from pycos.memori import JejakPrediksi
        j = JejakPrediksi(memory_retention_half_life=1, rng_seed=1)
        j.record_experience("api lorong", "lari", {"impact": -.2}, tick=0)
        p = j.predict("api lorong", tick=10, max_candidates=1, max_age_ticks=0)
        self.assertTrue(p["memory"]["hole"])
        self.assertFalse(p["retrieval_budget"]["truncated"])

    def test_mode_coarse_tetap_menghormati_batas(self):
        j = self.memori()
        j.set_retrieve_mode("coarse")
        p = j.predict("api lorong", max_candidates=3)
        self.assertLessEqual(p["retrieval_budget"]["similarity_evaluations"], 3)
        self.assertTrue(p["retrieval_budget"]["truncated"])

class RekomendasiKawananLazyTest(unittest.TestCase):
    def kawanan(self):
        from unittest.mock import Mock
        from pycos.inti import Naluri, KawananNPC
        k = KawananNPC()
        for nama, pos, lod in (("Dekat", (0, 0), "penuh"), ("Jauh", (20, 0), "penuh"),
                               ("Latar", (1, 0), "latar"), ("Abstrak", (1, 0), "abstrak"),
                               ("Beku", (1, 0), "beku")):
            n = Naluri(name=nama, rng_seed=1)
            k.serap(n, position=pos)
            n.set_lod(lod)
            j = Mock()
            j.predict.return_value = {"forecast": {}}
            j.rank_actions.return_value = {"action": "diam"}
            n.attach_jejak(j)
        return k

    def test_default_tidak_memanggil_prediksi_dan_event_latar_tetap_dibuffer(self):
        k = self.kawanan()
        self.assertIsNone(k.tick_all(events={"Latar": [{"drive": "energi", "delta": .1}]}))
        for n in k.npcs.values():
            n.jejak.predict.assert_not_called()
            n.jejak.rank_actions.assert_not_called()
        self.assertEqual(1, k.npcs["Latar"].tick_count)
        self.assertTrue(k.npcs["Latar"]._event_buffer)
        self.assertEqual("disabled", k.laporan_prediksi()["npcs"]["Dekat"]["reason"])

    def test_ranking_hanya_npc_aktif_dalam_radius(self):
        k = self.kawanan()
        actions = {nama: [{"name": "diam"}] for nama in k.npcs}
        k.tick_all(predict=True, stimulus="lorong", candidates=actions,
                   player_position=(0, 0), radius=2, max_candidates=12, max_actions=1)
        k.npcs["Dekat"].jejak.rank_actions.assert_called_once_with(
            "lorong", [{"name": "diam"}], max_candidates=12, max_actions=1, tick=1)
        for nama in ("Jauh", "Latar", "Abstrak", "Beku"):
            k.npcs[nama].jejak.predict.assert_not_called()
            k.npcs[nama].jejak.rank_actions.assert_not_called()
        r = k.laporan_prediksi()
        self.assertEqual(1, r["ranked"])
        self.assertEqual("outside_radius", r["npcs"]["Jauh"]["reason"])
        self.assertEqual("lod_abstrak", r["npcs"]["Abstrak"]["reason"])
        r["ranked"] = 999
        self.assertEqual(1, k.laporan_prediksi()["ranked"])

    def test_batch_lazim_tidak_memajukan_waktu(self):
        k = self.kawanan()
        r = k.prediksi_all({"Dekat": "api"})
        self.assertEqual(1, r["predicted"])
        self.assertEqual("missing_stimulus", r["npcs"]["Jauh"]["reason"])
        self.assertTrue(all(n.tick_count == 0 for n in k.npcs.values()))
        k.npcs["Dekat"].jejak.predict.assert_called_once_with("api", tick=0, max_candidates=256)

    def test_opsi_invalid_ditolak_sebelum_tick(self):
        k = self.kawanan()
        kasus = [{"predict": 1}, {"predict": True},
                 {"predict": True, "stimulus": "x", "candidates": {}},
                 {"predict": True, "stimulus": "x", "radius": 2},
                 {"predict": True, "stimulus": "x", "radius": -1, "player_position": (0, 0)},
                 {"predict": True, "stimulus": {"Typo": "api"}},
                 {"predict": True, "stimulus": "x", "max_candidates": True},
                 {"stimulus": "x"}]
        for args in kasus:
            with self.subTest(args=args), self.assertRaises(ValueError):
                k.tick_all(**args)
        self.assertTrue(all(n.tick_count == 0 for n in k.npcs.values()))

    def test_prediksi_setelah_seluruh_tick(self):
        k = self.kawanan()
        def pred(*args, **kw):
            self.assertTrue(all(n.tick_count == 1 for n in k.npcs.values()))
            return {}
        k.npcs["Dekat"].jejak.predict.side_effect = pred
        k.tick_all(predict=True, stimulus={"Dekat": "api"})
        self.assertEqual(1, k.laporan_prediksi()["predicted"])

    def test_koordinat_hilang_dan_radius_nol(self):
        k = self.kawanan()
        k.positions.pop("Jauh")
        r = k.prediksi_all("api", player_position=(0, 0, 0), radius=0)
        self.assertEqual(1, r["predicted"])
        self.assertEqual("unpositioned", r["npcs"]["Jauh"]["reason"])

    def test_galat_callback_dilaporkan_dan_diteruskan(self):
        k = self.kawanan()
        k.npcs["Dekat"].jejak.predict.side_effect = RuntimeError("putus")
        with self.assertRaisesRegex(RuntimeError, "putus"):
            k.tick_all(predict=True, stimulus="api")
        self.assertEqual("error", k.laporan_prediksi()["npcs"]["Dekat"]["status"])
        self.assertTrue(all(n.tick_count == 1 for n in k.npcs.values()))

    def test_tanpa_jejak_dan_vacancy_diklasifikasikan(self):
        from unittest.mock import patch
        k = self.kawanan()
        del k.npcs["Jauh"].jejak
        with patch.object(k.npcs["Dekat"], "_vacancy_aktif", return_value=True):
            r = k.prediksi_all("api")
        self.assertEqual("vacancy", r["npcs"]["Dekat"]["reason"])
        self.assertEqual("no_jejak", r["npcs"]["Jauh"]["reason"])
        self.assertEqual(0, r["predicted"])

    def test_ranking_memakai_jam_npc_walau_jejak_tidak_memiliki_backlink(self):
        from pycos.inti import Naluri, KawananNPC
        from pycos.memori import JejakPrediksi
        n = Naluri(name="Sari", rng_seed=1)
        j = JejakPrediksi(memory_retention_half_life=1, rng_seed=1)
        j.record_experience("api lorong", "lari", {"impact": -.2}, tick=0)
        n.attach_jejak(j)
        n.tick_count = 10
        k = KawananNPC()
        k.serap(n, position=(0, 0))
        report = k.prediksi_all("api lorong", candidates={"Sari": [{"name": "lari"}]},
                               player_position=(0, 0), radius=1)
        self.assertTrue(report["npcs"]["Sari"]["result"]["memory_hole"])
        self.assertIsNone(j.naluri)

    def test_radius_diperiksa_ulang_setelah_callback_tick(self):
        from unittest.mock import patch
        k = self.kawanan()
        n = k.npcs["Dekat"]
        with patch.object(n, "tick", side_effect=lambda **kw: k.set_position("Dekat", (100, 0))):
            k.tick_all(predict=True, stimulus="api", candidates={"Dekat": [{"name": "diam"}]},
                       player_position=(0, 0), radius=2)
        n.jejak.rank_actions.assert_not_called()
        self.assertEqual("outside_radius", k.laporan_prediksi()["npcs"]["Dekat"]["reason"])

class RekomendasiBatasMemoriTest(unittest.TestCase):
    def test_nilai_bawaan_dan_batas_tidak_sah(self):
        from unittest.mock import patch
        from pycos.dukungan.batas_memori import BATAS, batas
        self.assertEqual(600, BATAS["tick_history"])
        self.assertEqual(512, BATAS["delta_log"])
        for bad in (True, -1, 1.2, "4", None):
            with patch.dict(BATAS, {"tick_history": bad}), self.assertRaisesRegex(ValueError, "tick_history"):
                batas("tick_history")

    def test_pangkas_inplace_nol_dan_ceiling_lokal(self):
        from unittest.mock import patch
        from pycos.dukungan.batas_memori import BATAS, pangkas
        items = list(range(5))
        alias = items
        with patch.dict(BATAS, {"delta_log": 4}):
            pangkas(items, "delta_log", 2)
        self.assertIs(alias, items)
        self.assertEqual([3, 4], items)
        with patch.dict(BATAS, {"delta_log": 0}):
            pangkas(items, "delta_log")
        self.assertEqual([], items)

    def test_history_memakai_batas_host_dan_tetap_terbaru(self):
        from unittest.mock import patch
        from pycos.dukungan.batas_memori import BATAS
        from pycos.inti import Naluri
        n = Naluri(rng_seed=1)
        with patch.dict(BATAS, {"tick_history": 2}):
            for _ in range(30):
                n.tick()
        self.assertEqual([25, 30], [h["t"] for h in n.tick_history])

    def test_delta_replay_dan_event_buffer_nol(self):
        from unittest.mock import patch
        from pycos.dukungan.batas_memori import BATAS
        from pycos.inti import Naluri
        n = Naluri(rng_seed=1)
        n.enable_replay()
        with patch.dict(BATAS, {"delta_log": 0, "event_buffer": 0, "replay_log": 0}):
            n.delta("energi", .1)
            n.set_lod("latar")
            n.tick(events=[{"drive": "energi", "delta": .1}])
        self.assertEqual([], n.delta_log)
        self.assertEqual([], n._event_buffer)
        self.assertEqual([], n._event_log)

    def test_cache_nol_tidak_menyimpan_tetapi_tetap_menghitung(self):
        from unittest.mock import patch
        from pycos.dukungan.batas_memori import BATAS
        from pycos.inti import Naluri
        n = Naluri(rng_seed=1)
        hasil = n.impact_of("makan")
        with patch.dict(BATAS, {"impact_cache": 0}):
            self.assertEqual(hasil, n.impact_of("makan"))
            self.assertEqual({}, n._impact_cache)

    def test_audit_readonly_dan_penerapan_seluruh_buffer(self):
        from unittest.mock import patch
        from pycos.dukungan.batas_memori import BATAS
        from pycos.inti import Naluri
        n = Naluri(rng_seed=1)
        for key, (items, _) in n._buffer_memori().items():
            if isinstance(items, dict):
                items.update({"a": {}, "b": {}})
            else:
                items.extend([{}, {}])
        with patch.dict(BATAS, {k: 0 for k in BATAS}):
            state = n.memori_state()
            self.assertTrue(all(v["over_limit"] for v in state["buffers"].values()))
            state["buffers"]["delta_log"]["entries"] = 999
            self.assertEqual(2, len(n.delta_log))
            self.assertEqual(0, n.batasi_memori()["total_entries"])

    def test_kebijakan_invalid_tidak_memangkas_sebagian(self):
        from unittest.mock import patch
        from pycos.dukungan.batas_memori import BATAS
        from pycos.inti import Naluri
        n = Naluri(rng_seed=1)
        n.tick_history = [{"t": 1}]
        with patch.dict(BATAS, {"tick_history": 0, "impact_cache": -1}):
            with self.assertRaisesRegex(ValueError, "impact_cache"):
                n.batasi_memori()
        self.assertEqual([{"t": 1}], n.tick_history)

    def test_load_mengikuti_kebijakan_runtime_bukan_snapshot_host(self):
        from unittest.mock import patch
        from pycos.dukungan.batas_memori import BATAS
        from pycos.inti import Naluri
        n = Naluri(rng_seed=1)
        for _ in range(20):
            n.tick()
        data = n.to_dict()
        with patch.dict(BATAS, {"tick_history": 1}):
            other = Naluri.from_dict(data)
        self.assertEqual(4, len(data["tick_history"]))
        self.assertEqual([20], [h["t"] for h in other.tick_history])

    def test_kalibrasi_dan_prediction_log_memakai_batas_saat_penulisan(self):
        from unittest.mock import patch
        from pycos.dukungan.batas_memori import BATAS
        from pycos.inti import Naluri
        n = Naluri(rng_seed=1)
        with patch.dict(BATAS, {"pred_pairs": 1, "prediction_log": 1}):
            for _ in range(3):
                n.observe_outcome({"impact": .2, "probability": .5}, {"impact": .1})
        self.assertEqual(1, len(n._pred_pairs))
        self.assertEqual(1, len(n._prediction_log))

class RekomendasiVariasiTuturTest(unittest.TestCase):
    def rangkaian(self, seed=7, act="senang"):
        from pycos.bahasa.tutur import GenContext, TuturEngine
        from pycos.dukungan.sumber import jalur_leksikon
        e = TuturEngine(jalur_leksikon())
        ctx = GenContext(act=act, seed=seed, valensi=.8, arousal=.3)
        return e, [e.ucap(ctx) for _ in range(20)]

    def test_minimal_delapan_dari_dua_puluh_identik(self):
        for act in ("senang", "sedih"):
            e, hasil = self.rangkaian(act=act)
            self.assertTrue(all(t.status == "SUKSES" for t in hasil))
            self.assertGreaterEqual(len({t.teks for t in hasil}), 8, act)
            self.assertLessEqual(len(e.riwayat), 32)

    def test_seed_dan_riwayat_sama_menghasilkan_rangkaian_sama(self):
        _, a = self.rangkaian(seed=7)
        _, b = self.rangkaian(seed=7)
        self.assertEqual([t.teks for t in a], [t.teks for t in b])
        self.assertEqual([t.trace for t in a], [t.trace for t in b])
        _, c = self.rangkaian(seed=31)
        self.assertNotEqual([t.teks for t in a], [t.teks for t in c])

    def test_pilihan_mematuhi_kelas_bahasa_register_dan_lattice(self):
        import random
        from pycos.bahasa.tutur import Leksikon, L2, Slot, GenContext
        def entri(lema, **kw):
            return dict({"lema": lema, "bahasa": "id", "kelas": ["ADJ"],
                         "register": ["netral"], "tipe_semantik": ["SUKA"]}, **kw)
        leks = Leksikon({"lattice": {"SUKA": "SENANG"}, "leksikon": [
            entri("suka"), entri("english", bahasa="en"),
            entri("nomina", kelas=["N"]), entri("formal", register=["formal"]),
            entri("takut", tipe_semantik=["TAKUT"])]})
        # Assert the actual lattice direction used by the fixture.
        self.assertTrue(leks.lattice.cocok(["SUKA"], "SENANG"))
        l2 = L2(leks, random.Random(1), [])
        slot = Slot("PREDIKAT", "ADJ", "SENANG", False, .6, .5, True)
        for _ in range(20):
            pilihan, _ = l2.pilih(slot, GenContext())
            self.assertEqual("suka", pilihan["lema"])

    def test_riwayat_mempengaruhi_skor_tanpa_memutasi_leksikon(self):
        import random
        from pycos.bahasa.tutur import L2, Slot, GenContext, Leksikon
        entri = {"lema": "senang", "bahasa": "id", "kelas": ["ADJ"],
                 "register": ["netral"], "tipe_semantik": ["SENANG"]}
        l2 = L2(Leksikon({"leksikon": [entri]}), random.Random(1), [])
        slot = Slot("PREDIKAT", "ADJ", "SENANG", False, .6, .5, True)
        awal = dict(entri)
        segar = l2._skor(entri, slot, GenContext())
        l2.riwayat.extend(["senang"] * 10)
        self.assertLess(l2._skor(entri, slot, GenContext()), segar)
        l2.pilih(slot, GenContext())
        self.assertEqual(awal, entri)

    def test_pool_kecil_tidak_mengarang_sinonim(self):
        import random
        from pycos.bahasa.tutur import Leksikon, L2, Slot, GenContext
        leks = Leksikon({"leksikon": [{"lema": w, "bahasa": "id", "kelas": ["ADJ"],
                    "register": ["netral"], "tipe_semantik": ["SENANG"]}
                    for w in ("senang", "gembira")]})
        l2 = L2(leks, random.Random(7), [])
        slot = Slot("PREDIKAT", "ADJ", "SENANG", False, .6, .5, True)
        pilihan = [l2.pilih(slot, GenContext())[0]["lema"] for _ in range(20)]
        self.assertEqual({"senang", "gembira"}, set(pilihan))

    def test_seed_memilih_urutan_slot_tanpa_menghilangkan_sebab(self):
        from pycos.bahasa.tutur import GenContext, TuturEngine
        from pycos.dukungan.sumber import jalur_leksikon
        urutan = set()
        for seed in range(10):
            e = TuturEngine(jalur_leksikon())
            t = e.ucap(GenContext(act="peringatan", topik="hutan",
                                 spotlight=("asap tebal",), seed=seed))
            self.assertIn("karena asap tebal", t.teks)
            urutan.add(tuple(next(x["L2-urutan"] for x in t.trace if "L2-urutan" in x)))
        self.assertGreater(len(urutan), 1)

class RekomendasiLeksikonImpakTest(unittest.TestCase):
    def test_cakupan_provenance_dan_cli(self):
        from pycos.dukungan.leksikon import periksa
        hasil = periksa()
        self.assertGreaterEqual(hasil["id"], 400)
        self.assertGreaterEqual(hasil["en"], 200)
        cli = subprocess.run([sys.executable, "-m", "pycos.dukungan.leksikon", "--periksa"],
                             cwd=AKAR, capture_output=True, text=True, timeout=30)
        self.assertEqual(0, cli.returncode, cli.stderr)
        self.assertTrue(json.loads(cli.stdout)["ok"])

    def test_tambahan_tidak_menimpa_bobot_lama_dan_tidak_alias(self):
        from pycos.dukungan.leksikon import perluas
        sentinel = {"energi": .123}
        id_words, en_words = {"dehidrasi": sentinel}, {}
        perluas(id_words, en_words)
        self.assertIs(sentinel, id_words["dehidrasi"])
        id_words["keracunan"]["keamanan"] = .99
        a, b = {}, {}
        perluas(a, b)
        self.assertLess(a["keracunan"]["keamanan"], 0)
        self.assertGreater(b["hydrated"]["energi"], 0)

    def test_vector_tidak_sah_ditolak(self):
        from pycos.dukungan.leksikon import validasi_entri
        kasus = [{"": {"energi": .2}}, {"x": {}}, {"x": {"typo": .2}},
                 {"x": {"energi": True}}, {"x": {"energi": float("nan")}},
                 {"x": {"energi": 5}}, {"x": {"energi": 0}}]
        for data in kasus:
            with self.subTest(data=data), self.assertRaises(ValueError):
                validasi_entri(data, "uji")

    def test_impact_baru_dua_bahasa_dan_tag(self):
        from pycos.inti.naluri import Naluri, LEXICON_EN, TAG_LEXICON_EN
        n = Naluri(rng_seed=1)
        self.assertLess(n.impact_of("dehidrasi")["energi"], 0)
        self.assertLess(n.impact_of("keracunan")["keamanan"], 0)
        self.assertGreater(n.impact_of("DUKUNGAN SOSIAL")["afiliasi"], 0)
        en = Naluri(lexicon=LEXICON_EN, tag_lexicon=TAG_LEXICON_EN, rng_seed=1)
        self.assertGreater(en.impact_of("hydrated")["energi"], 0)
        self.assertLess(en.impact_of("ostracized")["afiliasi"], 0)
        self.assertLess(en.impact_of("DIRECT THREAT")["keamanan"], 0)

    def test_snapshot_penuh_dan_ringkas_memuat_lexicon_baru(self):
        from pycos.inti import Naluri
        n = Naluri(rng_seed=1)
        for profil in ("penuh", "simpan"):
            loaded = Naluri.from_dict(n.to_dict(profil=profil))
            self.assertEqual(n.lexicon, loaded.lexicon)
            self.assertEqual(n.impact_of("dehidrasi"), loaded.impact_of("dehidrasi"))

    def test_checker_menolak_provenance_rusak(self):
        from copy import deepcopy
        from unittest.mock import patch
        from pycos.dukungan import leksikon
        data = deepcopy(leksikon._dokumen())
        data["entri"]["id"]["dehidrasi"] = {"energi": -.123}
        with patch.object(leksikon, "_dokumen", return_value=data):
            with self.assertRaisesRegex(ValueError, "provenance"):
                leksikon.periksa()

class RekomendasiEvaluasiEksternalTest(unittest.TestCase):
    def data(self):
        from pycos.refleksi.nurani import ContohLabel
        dev = [ContohLabel("dev rendah", selaras=False), ContohLabel("dev tinggi", selaras=True)]
        uji = [ContohLabel("uji a", anotasi={"A": True, "B": True}),
               ContohLabel("uji b", anotasi={"A": True, "B": False}),
               ContohLabel("uji c", anotasi={"A": False, "B": False}),
               ContohLabel("uji d", anotasi={"A": False, "B": False})]
        return dev, uji

    def test_tanpa_data_tidak_mengklaim_evaluasi_eksternal(self):
        from pycos.refleksi.nurani import laporan_kalibrasi
        r = laporan_kalibrasi([])
        self.assertIn("fitur", r)
        self.assertIn("selaras", r)
        self.assertEqual("belum_tersedia", r["evaluasi_pihak_ketiga"]["status"])
        self.assertIsNone(r["evaluasi_pihak_ketiga"]["akurasi_terhadap_konsensus"])

    def test_kappa_diketahui_konsensus_seri_dikeluarkan(self):
        from unittest.mock import patch
        from pycos.refleksi.nurani import laporan_kalibrasi
        dev, uji = self.data()
        scores = {"dev rendah": .1, "dev tinggi": .9, "uji a": .9,
                  "uji b": .6, "uji c": .1, "uji d": .1}
        with patch("pycos.refleksi.nurani._skor_selaras", side_effect=lambda c, lex: scores[c.teks]):
            r = laporan_kalibrasi(dev, korpus_pihak_ketiga=uji,
                                   sumber_pihak_ketiga="fixture unit sintetis")["evaluasi_pihak_ketiga"]
        self.assertEqual(.5, r["antar_anotator"][0]["kappa"])
        self.assertEqual(4, r["antar_anotator"][0]["jumlah_pasangan"])
        self.assertEqual(1, r["konsensus_seri"])
        self.assertEqual(3, r["dinilai"])
        self.assertEqual(1.0, r["akurasi_terhadap_konsensus"])
        self.assertEqual(.75, r["cakupan_konsensus"])

    def test_label_atau_skor_uji_tidak_memilih_ambang(self):
        from dataclasses import replace
        from unittest.mock import patch
        from pycos.refleksi.nurani import laporan_kalibrasi
        dev, uji = self.data()
        def skor(c, lex):
            return .1 if c.teks == "dev rendah" else .9
        with patch("pycos.refleksi.nurani._skor_selaras", side_effect=skor):
            a = laporan_kalibrasi(dev, korpus_pihak_ketiga=uji, sumber_pihak_ketiga="fixture")
            baru = [replace(c, anotasi={k: not v for k, v in c.anotasi.items()}) for c in uji]
            with patch("pycos.refleksi.nurani._skor_selaras",
                       side_effect=lambda c, lex: skor(c, lex) if c.teks.startswith("dev ") else .05):
                b = laporan_kalibrasi(dev, korpus_pihak_ketiga=baru, sumber_pihak_ketiga="fixture")
        self.assertEqual(a["evaluasi_pihak_ketiga"]["ambang"], b["evaluasi_pihak_ketiga"]["ambang"])
        self.assertEqual("dipilih_hanya_dari_pengembangan", a["evaluasi_pihak_ketiga"]["metode_ambang"])

    def test_overlap_teks_dan_id_ditolak(self):
        from pycos.refleksi.nurani import ContohLabel, laporan_kalibrasi
        for dev, uji in (([ContohLabel(" TEKS  sama ")], [ContohLabel("teks sama")]),
                         ([ContohLabel("satu", id_contoh="id1")], [ContohLabel("dua", id_contoh="id1")])):
            with self.assertRaisesRegex(ValueError, "tumpang tindih"):
                laporan_kalibrasi(dev, korpus_pihak_ketiga=uji)
        with self.assertRaisesRegex(ValueError, "duplikat"):
            laporan_kalibrasi([], korpus_pihak_ketiga=[ContohLabel("x"), ContohLabel("X")])

    def test_anotasi_satu_dan_provenance_kosong_tidak_menerbitkan_akurasi(self):
        from pycos.refleksi.nurani import ContohLabel, laporan_kalibrasi
        for source, label_anotator in ((None, {"A": True, "B": True}), ("fixture", {"A": True})):
            r = laporan_kalibrasi([], korpus_pihak_ketiga=[ContohLabel("contoh", anotasi=label_anotator)],
                                  sumber_pihak_ketiga=source)["evaluasi_pihak_ketiga"]
            self.assertIsNone(r["akurasi_terhadap_konsensus"])

    def test_kappa_kelas_konstan_tidak_diklaim_sempurna(self):
        from pycos.refleksi.nurani import ContohLabel, laporan_kalibrasi
        data = [ContohLabel(t, anotasi={"A": True, "B": True}) for t in ("x", "y")]
        r = laporan_kalibrasi([], korpus_pihak_ketiga=data)["evaluasi_pihak_ketiga"]
        self.assertIsNone(r["antar_anotator"][0]["kappa"])
        self.assertIn("tidak terdefinisi", r["antar_anotator"][0]["keterangan"])

    def test_label_annotator_bool_dan_identitas_divalidasi_jsonl(self):
        from pycos.refleksi.nurani import contoh_dari_dict, muat_korpus
        for anotasi in ({"A": 1}, {"": True}, {" A": False}, []):
            with self.assertRaisesRegex(ValueError, "anotasi"):
                contoh_dari_dict({"teks": "x", "anotasi": anotasi})
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "uji.jsonl")
            with open(path, "w", encoding="utf-8") as f:
                f.write(json.dumps({"id": "uji1", "teks": "uji", "anotasi": {"A": True, "B": False}}))
            hasil = muat_korpus(path)
            self.assertEqual("uji1", hasil[0].id_contoh)
            self.assertEqual({"A": True, "B": False}, hasil[0].anotasi)

    def test_cli_json_dan_teks_menampilkan_status_dan_kappa(self):
        from pycos.__main__ import jalankan_selaras
        with tempfile.TemporaryDirectory() as tmp:
            dev, uji = os.path.join(tmp, "dev.jsonl"), os.path.join(tmp, "uji.jsonl")
            with open(dev, "w", encoding="utf-8") as f:
                f.write(json.dumps({"teks": "contoh dev", "selaras": True}))
            with open(uji, "w", encoding="utf-8") as f:
                f.write(json.dumps({"teks": "contoh uji A", "anotasi": {"A": True, "B": True}}) + "\n")
                f.write(json.dumps({"teks": "contoh uji B", "anotasi": {"A": False, "B": False}}))
            args = ["--kalibrasi", dev, "--korpus-pihak-ketiga", uji, "--sumber-evaluasi", "fixture sintetis"]
            for extra in (["--json"], []):
                out = io.StringIO()
                with contextlib.redirect_stdout(out):
                    self.assertEqual(0, jalankan_selaras(args + extra))
                self.assertIn("kappa", out.getvalue())
                if extra:
                    self.assertEqual(2, json.loads(out.getvalue())["evaluasi_pihak_ketiga"]["jumlah_anotator"])

    def test_tiga_anotator_pasangan_dan_data_hilang(self):
        from pycos.refleksi.nurani import ContohLabel, laporan_kalibrasi
        data = [ContohLabel("a", anotasi={"A": True, "B": True, "C": False}),
                ContohLabel("b", anotasi={"A": False, "B": False}), ContohLabel("c")]
        r = laporan_kalibrasi([], korpus_pihak_ketiga=data, sumber_pihak_ketiga="fixture")["evaluasi_pihak_ketiga"]
        self.assertEqual(3, len(r["antar_anotator"]))
        self.assertEqual(1, r["kurang_dua_anotator"])
        self.assertEqual(2, r["jumlah_konsensus"])
        self.assertEqual([2, 1, 1], [p["jumlah_pasangan"] for p in r["antar_anotator"]])

    def test_abstention_dilaporkan_dan_sumber_tanpa_korpus_ditolak(self):
        from unittest.mock import patch
        from pycos.refleksi.nurani import ContohLabel, laporan_kalibrasi
        data = [ContohLabel("uji", anotasi={"A": True, "B": True})]
        with patch("pycos.refleksi.nurani._skor_selaras", return_value=None):
            r = laporan_kalibrasi([], korpus_pihak_ketiga=data, sumber_pihak_ketiga="fixture")["evaluasi_pihak_ketiga"]
        self.assertEqual(0, r["dinilai"])
        self.assertIsNone(r["akurasi_terhadap_konsensus"])
        with self.assertRaisesRegex(ValueError, "membutuhkan"):
            laporan_kalibrasi([], sumber_pihak_ketiga="tanpa data")


if __name__ == "__main__":
    unittest.main()
