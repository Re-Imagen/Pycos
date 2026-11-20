# -*- coding: utf-8 -*-
"""Kontrak R4.3: satu sumber drive dan semua varian penjepitan terklasifikasi."""
from __future__ import annotations

import ast
import importlib
import math
import os
from pathlib import Path
import random
import subprocess
import sys
import unittest

AKAR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if AKAR not in sys.path:
    sys.path.insert(0, AKAR)


class KonstantaNumerikTest(unittest.TestCase):
    def test_alias_drive_identik_di_semua_lapisan(self):
        from pycos.dukungan.konstanta import DRIVES
        for module, name in [('pycos.dukungan', 'DRIVES'),
                             ('pycos.kontrak', 'DRIVE_KEYS'),
                             ('pycos.inti._konfigurasi', 'DRIVES'),
                             ('pycos.inti.naluri', 'DRIVES'),
                             ('pycos.memori.jejak_prediksi', 'DRIVES'),
                             ('pycos.refleksi.nurani', 'DEFAULT_DRIVES'),
                             ('pycos.refleksi.ketidaktahuan', '_DRIVES')]:
            with self.subTest(module=module):
                self.assertIs(DRIVES, getattr(importlib.import_module(module), name))
        self.assertIsInstance(DRIVES, tuple)
        self.assertEqual(6, len(set(DRIVES)))

    def test_tidak_ada_salinan_literal_drive_tersembunyi(self):
        from pycos.dukungan.konstanta import DRIVES
        found = []
        for path in (Path(AKAR) / 'pycos').rglob('*.py'):
            for node in ast.walk(ast.parse(path.read_text(encoding='utf-8'))):
                if isinstance(node, (ast.Tuple, ast.List, ast.Set)) and len(node.elts) == 6:
                    if all(isinstance(x, ast.Constant) and isinstance(x.value, str) for x in node.elts):
                        if {x.value for x in node.elts} == set(DRIVES):
                            found.append(str(path.relative_to(Path(AKAR) / 'pycos')).replace(os.sep, '/'))
        self.assertEqual(['dukungan/konstanta.py'], found)

    def test_konstanta_tidak_memuat_mesin(self):
        code = """
import sys
from pycos.dukungan import DRIVES
assert len(DRIVES) == 6
assert 'pycos.inti.naluri' not in sys.modules
assert 'pycos.kontrak' not in sys.modules
"""
        subprocess.run([sys.executable, '-c', code], check=True, capture_output=True, text=True)

    def test_semua_clamp_netral_cocok_kanonik(self):
        from pycos.dukungan.numerik import jepit
        functions = [('pycos.inti._konfigurasi', '_kclip'),
                     ('pycos.memori.jejak_prediksi', '_clip'),
                     ('pycos.mandiri.organik', '_kclip'),
                     ('pycos.mandiri.kognisi_lanjut', 'jepit_drive'),
                     ('pycos.lingkungan.dunia', '_potong')]
        values = [True, False, None, 'rusak', '.4', float('nan'), float('inf'),
                  -float('inf'), 10 ** 400, -10 ** 400, -.0, .3]
        rng = random.Random(43)
        values.extend(rng.uniform(-100, 100) for _ in range(250))
        for module, name in functions:
            fn = getattr(importlib.import_module(module), name)
            for lo, hi in [(-1., 1.), (.2, .9), (-4., -2.), (0., 0.)]:
                for value in values:
                    with self.subTest(module=module, value=value, lo=lo, hi=hi):
                        self.assertEqual(jepit(value, lo, hi), fn(value, lo, hi))

    def test_varian_tutur_dipertahankan_bukan_dinetralkan(self):
        from pycos.bahasa.tutur import _clip
        from pycos.dukungan.numerik import jepit
        for lo, hi in [(-1., 1.), (.2, .9), (-4., -2.)]:
            for value in [None, 'rusak', float('nan')]:
                self.assertEqual(lo, _clip(value, lo, hi))
            for value in [-10., -.3, .4, 2., '0.3', float('inf'), -float('inf')]:
                self.assertEqual(jepit(value, lo, hi), _clip(value, lo, hi))
        self.assertEqual(1., _clip(True))
        self.assertEqual(0., _clip(False))
        with self.assertRaises(OverflowError):
            _clip(10 ** 400)

    def test_varian_persona_tetap_ketat_dan_delegate_kanonik(self):
        from pycos.inti.persona import _jepit
        from pycos.dukungan.numerik import jepit
        for value in [True, False, None, '0.3', float('nan'), float('inf'), -float('inf')]:
            with self.assertRaises(ValueError):
                _jepit(value, -1., 1.)
        for value in [-10., -.3, -.0, .8, 10.]:
            self.assertEqual(jepit(value, -.4, .6), _jepit(value, -.4, .6))
        self.assertTrue(math.isfinite(_jepit(.2, -1., 1.)))

    def test_varian_view_memakai_default_untuk_semua_non_finite(self):
        from pycos.refleksi.ketidaktahuan import _clip
        from pycos.dukungan.numerik import jepit_01
        for default in [0., .3, 1.]:
            for value in [True, False, None, 'rusak', float('nan'), float('inf'),
                          -float('inf'), 10 ** 400]:
                self.assertEqual(default, _clip(value, default=default))
        for value in [-10, -.3, .4, 3., '0.3']:
            self.assertEqual(jepit_01(value), _clip(value))

    def test_seluruh_definisi_clamp_masuk_kontrak(self):
        names = {'jepit', 'jepit_drive', 'jepit_01', '_kclip', '_clip', '_potong', '_jepit'}
        found = set()
        for path in (Path(AKAR) / 'pycos').rglob('*.py'):
            for node in ast.walk(ast.parse(path.read_text(encoding='utf-8'))):
                if isinstance(node, ast.FunctionDef) and node.name in names:
                    found.add((str(path.relative_to(Path(AKAR) / 'pycos')).replace(os.sep, '/'), node.name))
        self.assertEqual({('dukungan/numerik.py', 'jepit'),
                          ('dukungan/numerik.py', 'jepit_drive'),
                          ('dukungan/numerik.py', 'jepit_01'),
                          ('inti/_konfigurasi.py', '_kclip'), ('inti/persona.py', '_jepit'),
                          ('memori/jejak_prediksi.py', '_clip'),
                          ('mandiri/organik.py', '_kclip'),
                          ('mandiri/kognisi_lanjut.py', 'jepit_drive'),
                          ('lingkungan/dunia.py', '_potong'), ('bahasa/tutur.py', '_clip'),
                          ('refleksi/ketidaktahuan.py', '_clip')}, found)

    def test_tiga_modul_mandiri_tetap_terimpor_tanpa_paket(self):
        for rel in ['mandiri/organik.py', 'mandiri/kognisi_lanjut.py', 'lingkungan/dunia.py']:
            path = str(Path(AKAR) / 'pycos' / rel)
            code = f"""
import importlib.util, sys
spec = importlib.util.spec_from_file_location('modul_mandiri', {path!r})
m = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = m
spec.loader.exec_module(m)
assert not any(name == 'pycos' or name.startswith('pycos.') for name in sys.modules)
"""
            with self.subTest(module=rel):
                subprocess.run([sys.executable, '-I', '-c', code], check=True,
                               capture_output=True, text=True)


if __name__ == '__main__':
    unittest.main()
