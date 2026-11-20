# -*- coding: utf-8 -*-
"""Gate R5.3: catatan lama tidak membenarkan perubahan loader baru."""
from __future__ import annotations

import os
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import subprocess
import sys
import unittest

AKAR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if AKAR not in sys.path:
    sys.path.insert(0, AKAR)

from tools import periksa_changelog
from tools.periksa_changelog import errors, loaders, unreleased


class ChangelogTests(unittest.TestCase):
    path = 'pycos/test.py'
    old = 'class A:\n def from_dict(self):\n  return 1\n'
    new = 'class A:\n def from_dict(self):\n  return 2\n'
    header = '## [Unreleased]\n'
    note = '- Kompatibilitas save: `pycos/test.py` — tidak berubah; validasi diperketat'

    def test_ast_ignores_comments_and_format(self):
        self.assertEqual(loaders(self.old), loaders(self.old + '# komentar\n'))
        self.assertFalse(errors({self.path: self.old}, {self.path: self.old}, '', ''))

    def test_missing_and_old_notes_fail(self):
        for old, new in [('', ''), (self.header + self.note, self.header + self.note),
                         ('', self.header + '## [0.1.0]\n' + self.note),
                         ('', self.header + '- Kompatibilitas save: `pycos/test.py` — ')]:
            self.assertTrue(errors({self.path: self.old}, {self.path: self.new}, old, new))

    def test_new_note_passes(self):
        self.assertFalse(errors({self.path: self.old}, {self.path: self.new},
                                self.header, self.header + self.note))

    def test_added_removed_and_multiple_files(self):
        for before, after in [({}, {self.path: self.new}),
                              ({self.path: self.old}, {})]:
            self.assertTrue(errors(before, after, '', self.header))
            self.assertFalse(errors(before, after, '', self.header + self.note))
        self.assertEqual(len(errors({}, {self.path: self.new, 'pycos/b.py': self.new},
                                    '', self.header + self.note)), 1)

    def test_unreleased_boundaries(self):
        self.assertEqual(unreleased('absent'), '')
        self.assertEqual(unreleased(self.header + 'text\n## [0.1]\nold'), 'text')

    def test_cli_and_invalid_base(self):
        for base, expected in [('HEAD', 0), ('refs/heads/does-not-exist-r53', 1)]:
            result = subprocess.run([sys.executable, 'tools/periksa_changelog.py',
                                     '--base', base], cwd=AKAR, capture_output=True,
                                    text=True, timeout=30)
            if expected:
                self.assertNotEqual(result.returncode, 0)
            else:
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn('LULUS', result.stdout)

    def test_main_success_and_failure_in_process(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'pycos').mkdir()
            (root / self.path).write_text(self.new, encoding='utf-8')
            for note, expected in [(self.note, 0), ('', 1)]:
                (root / 'CHANGELOG.md').write_text(self.header + note, encoding='utf-8')
                with patch.object(periksa_changelog, 'AKAR', root), \
                        patch.object(sys, 'argv', ['gate', '--base', 'HEAD']), \
                        patch.object(periksa_changelog, 'git', side_effect=[
                            'sha', self.path, self.old, 'CHANGELOG.md', self.header]), \
                        patch('builtins.print'):
                    self.assertEqual(periksa_changelog.main(), expected)
