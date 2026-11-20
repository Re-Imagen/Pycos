# -*- coding: utf-8 -*-
"""Gate R5.1 diuji memakai waktu sintetis, bukan timing unit test yang flaky."""
from __future__ import annotations

import contextlib
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest

AKAR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if AKAR not in sys.path:
    sys.path.insert(0, AKAR)

from tools.periksa_gate import coverage_errors, main, target_coverage, tolok_errors  # noqa: E402


class GatePengembanganTest(unittest.TestCase):
    def test_coverage_per_file_dan_laporan_tidak_lengkap(self):
        def report(covered, total):
            return {'files': {'x': {'summary': {'covered_lines': covered, 'num_statements': total}}}}
        self.assertEqual([], coverage_errors(report(8, 10), ['x']))
        self.assertTrue(coverage_errors(report(7, 10), ['x']))
        for covered, total in [(True, 10), (10, 0), (-1, 10), (11, 10), (1, '10')]:
            self.assertTrue(coverage_errors(report(covered, total), ['x']))
        for bad in [{}, {'files': []}, {'files': {}}, {'files': {'x': {}}}]:
            self.assertTrue(coverage_errors(bad, ['x']))

    def test_target_coverage_mencakup_modul_baru(self):
        self.assertIn('pycos/dukungan/konstanta.py', target_coverage())
        self.assertIn('tools/periksa_gate.py', target_coverage())
        self.assertIn('pycos/kontrak.py', target_coverage())
        self.assertIn('pycos/konektor.py', target_coverage())
        self.assertIn('pycos/inti/persona.py', target_coverage())
        self.assertIn('pycos/refleksi/nurani.py', target_coverage())
        self.assertIn('pycos/bahasa/tutur.py', target_coverage())
        self.assertEqual(len(target_coverage()), len(set(target_coverage())))

    @staticmethod
    def report(tick=.1, predict=4.):
        return {'ok': True, 'tolok': [
            {'nama': 'naluri_tick', 'ok': True, 'iterasi': 200, 'per_iterasi_ms': tick},
            {'nama': 'predict_2000_terbatas', 'ok': True, 'iterasi': 100, 'per_iterasi_ms': predict}]}

    def test_ambang_performa_ketat(self):
        self.assertEqual([], tolok_errors(self.report()))
        self.assertTrue(tolok_errors(self.report(tick=2.)))
        self.assertTrue(tolok_errors(self.report(predict=5.)))
        for value in [True, None, float('nan'), float('inf'), 10 ** 400, -1, '0.1']:
            self.assertTrue(tolok_errors(self.report(tick=value)))

    def test_tolok_gagal_hilang_duplikat_dan_iterasi_invalid(self):
        for bad in [{}, {'ok': True, 'tolok': {}}, {'ok': True, 'tolok': []}]:
            self.assertTrue(tolok_errors(bad))
        report = self.report()
        report['ok'] = False
        self.assertTrue(tolok_errors(report))
        report = self.report()
        report['tolok'].append(report['tolok'][0])
        self.assertTrue(tolok_errors(report))
        for iterations in [0, True, '1']:
            report = self.report()
            report['tolok'][0]['iterasi'] = iterations
            self.assertTrue(tolok_errors(report))
        report = self.report()
        report['tolok'][0]['ok'] = False
        self.assertTrue(tolok_errors(report))

    def test_cli_lulus_dan_gagal(self):
        with tempfile.TemporaryDirectory() as folder, contextlib.redirect_stdout(io.StringIO()):
            path = Path(folder) / 'tolok.json'
            path.write_text(json.dumps(self.report()))
            self.assertEqual(0, main(['--tolok', str(path)]))
            path.write_text(json.dumps(self.report(predict=5.)))
            self.assertEqual(1, main(['--tolok', str(path)]))
            path.write_text('rusak')
            self.assertEqual(1, main(['--tolok', str(path)]))
            path.write_text('[]')
            self.assertEqual(1, main(['--tolok', str(path)]))
            self.assertEqual(1, main(['--coverage', str(path) + '.hilang']))
            path.write_text(json.dumps({'files': {p: {'summary': {'covered_lines': 8,
                           'num_statements': 10}} for p in target_coverage()}}))
            self.assertEqual(0, main(['--coverage', str(path)]))
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            main([])


if __name__ == '__main__':
    unittest.main()
