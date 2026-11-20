# -*- coding: utf-8 -*-
"""Kebijakan ekspor root: identitas, resolusi malas, dan pengecualian eksplisit."""
from __future__ import annotations

import importlib
import json
import os
import subprocess
import sys
import unittest

AKAR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if AKAR not in sys.path:
    sys.path.insert(0, AKAR)

import pycos


class ApiPublikR54Tests(unittest.TestCase):
    def test_seluruh_api_subpaket_terklasifikasi(self):
        excluded = {('lingkungan', 'demo'), ('dukungan', 'sumber_daya')}
        seen = set()
        for layer in ('inti', 'refleksi', 'memori', 'mandiri', 'lingkungan',
                      'bahasa', 'dukungan'):
            package = importlib.import_module('pycos.' + layer)
            for name in package.__all__:
                with self.subTest(layer=layer, name=name):
                    if (layer, name) in excluded:
                        self.assertNotIn(name, pycos.__all__)
                        self.assertTrue(callable(getattr(package, name)))
                        seen.add((layer, name))
                    else:
                        self.assertIn(name, pycos.__all__)
                        self.assertIs(getattr(pycos, name), getattr(package, name))
        self.assertEqual(seen, excluded)

    def test_daftar_unik_dir_dan_cache(self):
        self.assertEqual(len(pycos.__all__), len(set(pycos.__all__)))
        for name in pycos.__all__:
            self.assertIn(name, dir(pycos))
            value = getattr(pycos, name)
            self.assertIs(value, pycos.__dict__[name])
        for name in ('EversiTD', 'Perencana', 'ModelKausal', 'GrafAsosiasi'):
            self.assertIn(name, pycos.__all__)
        with self.assertRaises(AttributeError):
            getattr(pycos, 'TidakAdaR54')

    def test_impor_dan_dir_tidak_memuat_pemilik(self):
        code = ('import sys, json, pycos; dir(pycos); '
                'print(json.dumps(sorted(m for m in sys.modules '
                'if m == "pycos" or m.startswith("pycos."))))')
        result = subprocess.run([sys.executable, '-c', code], cwd=AKAR,
                                capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), ['pycos'])

    def test_star_import_dan_tabrakan_nama_paket(self):
        # Jalur modul data tetap modul, bukan fungsi sumber_daya dukungan.
        code = ('import types, pycos; from pycos import *; '
                'import pycos.sumber_daya; '
                'assert isinstance(pycos.sumber_daya, types.ModuleType); '
                'assert all(n in globals() for n in pycos.__all__); '
                'from pycos import Perencana; '
                'from pycos.mandiri import Perencana as P; assert P is Perencana')
        result = subprocess.run([sys.executable, '-c', code], cwd=AKAR,
                                capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
