# -*- coding: utf-8 -*-
"""Tes integrasi lintas subpaket melalui jalur impor baru.

Fokusnya bukan rumus masing-masing lapisan, melainkan bahwa sambungan antarmodul
masih tersambung setelah penataan ulang: hook yang dipasang
`pycos.dukungan.patching`, modul opsional yang diselesaikan dengan nama
bertitik (`pycos.mandiri.organik`, `pycos.mandiri.kognisi_lanjut`), dan
alur pemakaian yang dijanjikan README, termasuk lingkungan uji
`pycos.lingkungan.dunia` yang memanggil NPC secara duck-typed.
"""
from __future__ import annotations

import os
import subprocess
import sys
import unittest

AKAR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if AKAR not in sys.path:
    sys.path.insert(0, AKAR)


class MulaiCepatREADMETest(unittest.TestCase):
    def test_alur_npc_dan_jejak(self):
        from pycos import JejakPrediksi, Naluri

        npc = Naluri(name="Ayu", rng_seed=7)
        npc.tick(events=[{"drive": "keamanan", "delta": -0.2,
                          "reason": "mendengar suara di lorong"}])
        jejak = JejakPrediksi(naluri=npc)
        jejak.record_experience(
            "lorong berasap", "masuk",
            {"impact": -0.7, "drive_deltas": {"keamanan": -0.6},
             "label": "sesak"},
            context="malam", tick=1)
        hasil = jejak.predict("lorong berasap", action="masuk",
                              context="malam", tick=2)
        self.assertIn("forecast", hasil)
        self.assertEqual("ditemukan", hasil["memory"]["retrieval_status"])
        self.assertEqual(1, hasil["memory"]["n_matches"])
        self.assertIn(hasil["scope"], ("situasi", "action"))

    def test_nama_modul_lapisan_sesuai_paket(self):
        from pycos import JejakPrediksi, Naluri, Nurani, Organik, TuturEngine

        self.assertEqual("pycos.inti.naluri", Naluri.__module__)
        self.assertEqual("pycos.refleksi.nurani", Nurani.__module__)
        self.assertEqual("pycos.memori.jejak_prediksi", JejakPrediksi.__module__)
        self.assertEqual("pycos.mandiri.organik", Organik.__module__)
        self.assertEqual("pycos.bahasa.tutur", TuturEngine.__module__)


class HookOrganikTest(unittest.TestCase):
    """`Naluri` dan `Nurani` memasang hook LukaDomain/TopologiSlot dari `mandiri`."""

    def test_slot_topologis_lewat_patching(self):
        from pycos.inti import Naluri

        npc = Naluri(name="Bob", rng_seed=11)
        self.assertEqual({}, npc.organik_state())
        npc.daftarkan_slot("Ayu", {"peran": "sahabat"})
        ringkas = npc.organik_state()
        self.assertEqual(1, ringkas["slot_total"])
        self.assertEqual([], ringkas["slot_kosong"])
        npc.kosongkan_slot("Ayu", alasan="meninggal")
        self.assertEqual(["Ayu"], npc.organik_state()["slot_kosong"])
        self.assertIsNone(npc.intensitas_topologis("Ayu", 0.03),
                          "slot kosong harus None, bukan skalar kecil")
        self.assertFalse(npc.layak_cabang("Ayu"))

    def test_jejak_mengambil_waktu_heterogen(self):
        from pycos.memori import JejakPrediksi

        jejak = JejakPrediksi()
        jejak.record_experience("lorong", "masuk",
                                {"impact": -0.5,
                                 "drive_deltas": {"keamanan": -0.5}},
                                tick=1)
        state = jejak.waktu_state()          # dipasang hanya bila organik tersedia
        self.assertEqual(1, state["n"])
        self.assertIn("dasar", state)

    def test_nurani_memakai_mandiri_untuk_luka_domain(self):
        from pycos.refleksi import Nurani

        nurani = Nurani(params={"enable_affective_memory": True})
        nurani.hancurkan_domain("Budi", "uang", alasan="menipu", tick=1)
        self.assertIsNone(nurani.terapkan_domain("Budi", "uang", 0.9))
        self.assertEqual(0.9, nurani.terapkan_domain("Budi", "kesehatan", 0.9))
        self.assertEqual(["uang"], nurani.domain_terluka("Budi"))
        self.assertEqual({"Budi": ["uang"]}, nurani.luka_state())


class KognisiLanjutTest(unittest.TestCase):
    def test_graf_asosiasi_terpasang_ke_naluri(self):
        from pycos.inti import Naluri

        npc = Naluri(name="Rama", rng_seed=7)
        self.assertTrue(npc.enable_asosiasi(aktif=True))
        self.assertTrue(npc.koaktifkan("hujan", "sedih", 1.0) > 0)
        asosiasi = dict(npc.asosiasi("hujan"))
        self.assertIn("sedih", asosiasi)
        self.assertTrue(npc.kognisi_state()["aktif"]["asosiasi"])

    def test_state_bayes_round_trip(self):
        from pycos.inti import Naluri

        npc = Naluri(name="Ana", rng_seed=9)
        npc.perbarui_kepercayaan("lorong aman", 0.2, label="sepi")
        state = npc.to_dict()
        self.assertIn("kognisi_lanjut", state)
        pulih = Naluri.from_dict(state)
        self.assertEqual(state["kognisi_lanjut"], pulih.to_dict()["kognisi_lanjut"])


class RefleksiTest(unittest.TestCase):
    def test_memori_afektif_dan_round_trip(self):
        from pycos.refleksi import Nurani

        params = {"enable_affective_memory": True, "affective_min_samples": 1}
        nurani = Nurani(params=params)
        self.assertTrue(nurani.experience("lorong", {"keamanan": -0.4},
                                          tick=1))
        prior = nurani.anticipate("lorong")
        self.assertLess(prior["keamanan"], 0.0)
        data = nurani.to_dict()
        self.assertEqual(data, Nurani.from_dict(data, params=dict(params)
                                                ).to_dict())


class LingkunganTest(unittest.TestCase):
    """`Lingkungan` memakai `Naluri` yang sama dengan fasad paket."""

    def test_npc_bertindak_dan_berpindah_di_dunia(self):
        from pycos import Lingkungan, Naluri

        dunia = Lingkungan.dari_ascii(["......"], seed=4)
        dunia.tambah_objek("makanan", (3, 0), nama="roti")
        npc = Naluri(name="Ayu", rng_seed=4,
                     initial_levels={"energi": -0.6,
                                     "keingintahuan": -0.2})
        dunia.tambah_npc(npc, (0, 0))
        hasil = dunia.jalankan(langkah=12)
        self.assertEqual(12, len(hasil["riwayat"]))
        self.assertGreater(dunia.badan["Ayu"].langkah, 0)
        self.assertTrue(all(-1.0 <= float(v) <= 1.0
                            for v in npc.levels.values()))


class JalurEksekusiTest(unittest.TestCase):
    """Baik `python -m pycos.<sub>.<modul>` maupun eksekusi berkas harus lulus."""

    def jalankan(self, args, cwd=AKAR):
        return subprocess.run([sys.executable] + args, cwd=cwd,
                              capture_output=True, text=True)

    def test_modul_lewat_dash_m(self):
        for modul in ("pycos.mandiri.organik", "pycos.refleksi.nurani",
                      "pycos.memori.jejak_prediksi",
                      "pycos.lingkungan.dunia"):
            with self.subTest(modul=modul):
                hasil = self.jalankan(["-m", modul])
                self.assertEqual(0, hasil.returncode, hasil.stderr[-2000:])

    def test_ringkasan_paket(self):
        hasil = self.jalankan(["-m", "pycos"])
        self.assertEqual(0, hasil.returncode, hasil.stderr[-2000:])
        for penanda in ("Subpaket:", "pycos.inti", "pycos.bahasa",
                        "leksikon_pycos.json", "python -m pycos.inti.naluri"):
            with self.subTest(penanda=penanda):
                self.assertIn(penanda, hasil.stdout)

    def test_berkas_dijalankan_langsung_tanpa_PYTHONPATH(self):
        """Shim `if not __package__` menjaga mode lawas `python3 <berkas>.py`."""
        for berkas in ("refleksi/nurani.py", "memori/jejak_prediksi.py",
                       "mandiri/organik.py", "lingkungan/dunia.py"):
            with self.subTest(berkas=berkas):
                jalur = os.path.join(AKAR, "pycos", *berkas.split("/"))
                hasil = subprocess.run(
                    [sys.executable, jalur], cwd=os.path.dirname(jalur),
                    env=dict(os.environ, PYTHONPATH=""),
                    capture_output=True, text=True)
                self.assertEqual(0, hasil.returncode, hasil.stderr[-2000:])

    def test_impor_lewat_PYTHONPATH_tanpa_instalasi(self):
        hasil = subprocess.run(
            [sys.executable, "-c",
             "from pycos.inti import Naluri; print(Naluri.__module__)"],
            cwd="/tmp", env=dict(os.environ, PYTHONPATH=AKAR),
            capture_output=True, text=True)
        self.assertEqual(0, hasil.returncode, hasil.stderr[-2000:])
        self.assertEqual("pycos.inti.naluri", hasil.stdout.strip())


class KoherensiLintasModulTest(unittest.TestCase):
    """Penjaga salinan konstanta yang wajib sinkron antar-berkas."""

    def test_daftar_drive_tiga_salinan_sama(self):
        # kontrak.DRIVE_KEYS (kanonik manifest), naluri.DRIVES (mesin), dan
        # nurani.DEFAULT_DRIVES (lapisan refleksi) harus identik.
        from pycos.inti.naluri import DRIVES
        from pycos.kontrak import DRIVE_KEYS
        from pycos.refleksi.nurani import DEFAULT_DRIVES

        self.assertEqual(tuple(DRIVE_KEYS), tuple(DRIVES))
        self.assertEqual(tuple(DRIVE_KEYS), tuple(DEFAULT_DRIVES))


if __name__ == "__main__":
    unittest.main()
