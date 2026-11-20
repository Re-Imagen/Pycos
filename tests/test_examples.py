# -*- coding: utf-8 -*-
"""Contoh publik harus berjalan sebagai modul dan menghasilkan state bermakna."""
from __future__ import annotations

import os
import json
from pathlib import Path
import subprocess
import sys
import unittest


AKAR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if AKAR not in sys.path:
    sys.path.insert(0, AKAR)
AKAR_PATH = Path(AKAR)


class ExamplesTests(unittest.TestCase):
    def jalankan(self, nama):
        proses = subprocess.run([sys.executable, "-m", "examples." + nama],
                                cwd=str(AKAR), capture_output=True, text=True,
                                encoding="utf-8", timeout=30, check=False)
        self.assertEqual(proses.returncode, 0, proses.stderr)
        self.assertEqual(proses.stderr, "")
        return json.loads(proses.stdout)

    def test_npc_dunia(self):
        hasil = self.jalankan("npc_dunia")
        self.assertLessEqual(len((AKAR_PATH / "examples/npc_dunia.py").read_text(
            encoding="utf-8").splitlines()), 40)
        self.assertEqual(hasil["tick_dunia"], 4)
        self.assertEqual(hasil["tick_npc"], 4)
        self.assertEqual([x["tick"] for x in hasil["langkah"]], [1, 2, 3, 4])
        for langkah in hasil["langkah"]:
            self.assertEqual(langkah["npc"], hasil["nama"])
            self.assertTrue(langkah["aksi"])
            x, y = langkah["posisi"]
            self.assertTrue(0 <= x < 5 and 0 <= y < 3)

    def test_dialog_hud(self):
        hasil = self.jalankan("dialog_hud")
        formal, akrab = hasil["dialog"]
        self.assertEqual([formal["register"], akrab["register"]], ["formal", "akrab"])
        self.assertTrue(formal["teks"])
        self.assertTrue(akrab["teks"])
        self.assertNotEqual(formal["teks"], akrab["teks"])
        self.assertTrue(hasil["hud"]["presentasi"]["aktif"])
        for dialog in hasil["dialog"]:
            self.assertIn(hasil["nama"], dialog["tag"])
            self.assertEqual(dialog["tag"], hasil["hud"]["tag_dialog"])

    def test_simpan_migrasi(self):
        hasil = self.jalankan("simpan_migrasi")
        self.assertEqual(hasil["format_asal"], "naluri/3")
        self.assertEqual(hasil["format_tujuan"], "naluri/4")
        self.assertTrue(hasil["save_ada"])
        self.assertTrue(hasil["state_pulih_sama"])
        for key in ("tick_asli", "tick_pulih", "tick_migrasi", "tick_subjektif"):
            self.assertEqual(hasil[key], 3)

    def test_kawanan_lod(self):
        hasil = self.jalankan("kawanan_lod")
        self.assertEqual(hasil["jumlah"], 100)
        self.assertEqual(hasil["lod"], dict.fromkeys(
            ("penuh", "ringan", "latar", "abstrak", "beku"), 20))
        self.assertEqual(len(hasil["kemajuan"]), 100)
        # Tick objektif tetap maju, termasuk NPC beku; LOD mengatur kerja internal.
        self.assertEqual(set(hasil["kemajuan"].values()), {3})

    def test_output_deterministik(self):
        for nama in ("npc_dunia", "dialog_hud", "simpan_migrasi", "kawanan_lod"):
            with self.subTest(nama=nama):
                self.assertEqual(self.jalankan(nama), self.jalankan(nama))
