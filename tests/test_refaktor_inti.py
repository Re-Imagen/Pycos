# -*- coding: utf-8 -*-
"""Kontrak kompatibilitas pemecahan bertahap inti (R4.1)."""
from __future__ import annotations

import json
from pathlib import Path
import pickle
import subprocess
import sys
from types import SimpleNamespace
import unittest


AKAR = str(Path(__file__).resolve().parent.parent)
if AKAR not in sys.path:
    sys.path.insert(0, AKAR)


class RefaktorIntiTest(unittest.TestCase):
    def test_nama_publik_naluri_tetap(self):
        from pycos.inti.naluri import Naluri
        path = Path(__file__).parent / 'fixtures' / 'naluri_public_r41.json'
        expected = json.loads(path.read_text())
        self.assertEqual(expected, sorted(n for n in dir(Naluri) if not n.startswith('_')))

    def test_urutan_impor_dan_identitas(self):
        for module, name in [('ritual', 'Ritual'), ('reputasi', 'Reputasi'),
                             ('kawanan', 'KawananNPC'), ('kesadaran', 'Kesadaran'),
                             ('presentasi', 'Presentasi'), ('mesin', 'Naluri'),
                             ('keadaan', 'Goal'), ('keadaan', 'Mood')]:
            for first in [module, 'naluri']:
                with self.subTest(module=module, first=first):
                    code = f'''
import importlib
importlib.import_module('pycos.inti.{first}')
a = importlib.import_module('pycos.inti.{module}')
b = importlib.import_module('pycos.inti.naluri')
import pycos.inti as facade
assert a.{name} is b.{name} is facade.{name}
assert a.{name}.__module__ == 'pycos.inti.naluri'
'''
                    subprocess.run([sys.executable, '-c', code], check=True,
                                   capture_output=True, text=True)

    def test_impor_paket_tetap_lazy(self):
        code = '''
import sys
import pycos
import pycos.inti
assert 'pycos.inti.naluri' not in sys.modules
assert 'pycos.inti.ritual' not in sys.modules
assert 'pycos.inti.kawanan' not in sys.modules
assert 'pycos.inti.kesadaran' not in sys.modules
assert 'pycos.inti.presentasi' not in sys.modules
'''
        subprocess.run([sys.executable, '-c', code], check=True,
                       capture_output=True, text=True)

    def test_pickle_jalur_historis(self):
        from pycos.inti.naluri import Reputasi, Ritual, KawananNPC
        npc = SimpleNamespace(name='Rama', weights={}, emosi={}, tick_count=0)
        for obj in [Reputasi(), Ritual(npc), KawananNPC()]:
            with self.subTest(cls=type(obj).__name__):
                restored = pickle.loads(pickle.dumps(obj))
                self.assertIs(type(restored), type(obj))
                self.assertEqual(restored.to_dict(), obj.to_dict())

    def test_ritual_rng_dan_default_bersama(self):
        from pycos.inti.naluri import DEFAULTS, RITUAL_DEFAULTS, Ritual
        from pycos.inti.ritual import RITUAL_DEFAULTS as defaults
        self.assertIs(defaults, RITUAL_DEFAULTS)
        for key, value in defaults.items():
            self.assertEqual(DEFAULTS[key], value)
        npc = SimpleNamespace(name='Rama', weights={}, emosi={}, tick_count=0)
        a = Ritual(npc, params={'enable_ritual': True})
        b = Ritual(npc, params={'enable_ritual': True}).from_dict(a.to_dict())
        self.assertEqual([a.perform() for _ in range(10)],
                         [b.perform() for _ in range(10)])

    def test_ast_kelas_tidak_berubah_selain_impor_backend(self):
        import ast
        import hashlib
        expected = json.loads((Path(__file__).parent / 'fixtures' /
                               'kelas_inti_r41.json').read_text())

        class TanpaImporBackend(ast.NodeTransformer):
            def visit_ImportFrom(self, node):
                if node.module == 'pycos.inti.naluri':
                    self_names = {alias.name for alias in node.names}
                    if self_names <= {'SASPAnalyzer', 'TuturEngine', 'konteks_dari_presentasi',
                                      'Nurani', 'CalibrationReport', '_get_attr'}:
                        return None
                return node

        for module, cls in [('kesadaran', 'Kesadaran'), ('presentasi', 'Presentasi'),
                            ('mesin', 'Naluri')]:
            with self.subTest(cls=cls):
                root = ast.parse((Path(AKAR) / 'pycos' / 'inti' / (module + '.py')).read_text())
                node = next(n for n in root.body if isinstance(n, ast.ClassDef) and n.name == cls)
                normalized = TanpaImporBackend().visit(node)
                # ast.dump adds fields across Python releases (e.g. type_params).
                # Canonicalize only the schema used by these non-generic classes.
                def canonical(value):
                    if isinstance(value, ast.AST):
                        return [type(value).__name__, [[key, canonical(item)]
                                for key, item in ast.iter_fields(value)
                                if key != 'type_params']]
                    if isinstance(value, list):
                        return [canonical(item) for item in value]
                    return value

                payload = json.dumps(canonical(normalized), ensure_ascii=True, separators=(',', ':'))
                digest = hashlib.sha256(payload.encode()).hexdigest()
                self.assertEqual(expected[cls], digest)

    def test_konfigurasi_berbagi_objek_bukan_salinan(self):
        from pycos.inti import naluri, _konfigurasi, kesadaran, presentasi
        for name in ['DEFAULTS', 'DRIVES', 'LEXICON', 'LEXICON_PACKS',
                     'KESADARAN_DEFAULTS', 'FREE_WILL_DEFAULTS']:
            self.assertIs(getattr(naluri, name), getattr(_konfigurasi, name))
        self.assertIs(kesadaran.KESADARAN_DEFAULTS, naluri.KESADARAN_DEFAULTS)
        self.assertIs(presentasi.PRESENTASI_DEFAULTS, naluri.PRESENTASI_DEFAULTS)
        for key, value in presentasi.PRESENTASI_DEFAULTS.items():
            self.assertEqual(naluri.DEFAULTS[key], value)

    def test_backend_opsional_mengikuti_facade_lama(self):
        from unittest.mock import patch
        from pycos.inti import naluri
        npc = naluri.Naluri(name='Uji', params={'enable_presentasi': True})
        # Fallback tidak mengunci salinan backend saat modul baru diimpor.
        with patch.object(naluri, 'TuturEngine', None):
            self.assertIsNone(npc.presentasi.tutur_engine())

    def test_demo_tidak_dimuat_oleh_impor_produksi(self):
        code = """
import sys
from pycos.inti.naluri import Naluri, demo_kognisi
assert callable(demo_kognisi)
assert 'pycos.inti.demo' not in sys.modules
assert 'pycos.inti.demo.skenario' not in sys.modules
Naluri(rng_seed=7).tick()
assert 'pycos.inti.demo.skenario' not in sys.modules
"""
        subprocess.run([sys.executable, '-c', code], check=True,
                       capture_output=True, text=True)

    def test_semua_showcase_dapat_dijalankan(self):
        result = subprocess.run([sys.executable, '-m', 'pycos.inti.demo'],
                                cwd=AKAR, capture_output=True, text=True, timeout=60)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn('STATUS AKHIR', result.stdout)
        self.assertIn('setpoint keamanan=', result.stdout)

    def test_patch_ids_dan_urutan_tetap_idempoten(self):
        fixture = str(Path(__file__).parent / 'fixtures' / 'patch_inti_r41.json')
        code = f"""
import inspect, json
from pycos.inti import naluri
from pycos.inti.ekstensi import pasang, URUTAN
assert URUTAN == ('kognisi', 'organik', 'gejala', 'invensi', 'kausal', 'perencana', 'pelindung', 'ketidaktahuan', 'persistensi')
def snapshot():
    out = {{}}
    for name in ('Naluri', 'Kesadaran', 'Presentasi', 'KawananNPC'):
        cls = getattr(naluri, name)
        out[name] = {{}}
        for key in dir(cls):
            raw = inspect.getattr_static(cls, key)
            fn = raw.__func__ if isinstance(raw, (classmethod, staticmethod)) else raw
            ids = getattr(fn, '__pycos_patch_ids__', ())
            if ids:
                out[name][key] = list(ids)
    return out
with open({fixture!r}) as f:
    expected = json.load(f)
assert snapshot() == expected
original = naluri.Presentasi.ucap
pasang(naluri.Naluri)
pasang(naluri.Naluri)
assert naluri.Presentasi.ucap is original
assert snapshot() == expected
"""
        subprocess.run([sys.executable, '-c', code], check=True,
                       capture_output=True, text=True)

    def test_impor_ekstensi_belum_memasang_patch(self):
        code = """
import sys
from pycos.inti.ekstensi import pelindung
from pycos.inti.presentasi import Presentasi
assert 'pycos.inti.naluri' not in sys.modules
assert not getattr(Presentasi.ucap, '__pycos_patch_ids__', ())
from pycos.inti import naluri
assert naluri.MonitorIntegritas is pelindung.MonitorIntegritas
assert 'naluri.pelindung.ucap' in Presentasi.ucap.__pycos_patch_ids__
"""
        subprocess.run([sys.executable, '-c', code], check=True,
                       capture_output=True, text=True)

    def test_semua_berkas_inti_maksimal_5000_baris(self):
        root = Path(AKAR) / 'pycos' / 'inti'
        for path in root.rglob('*.py'):
            with self.subTest(path=str(path.relative_to(root))):
                self.assertLessEqual(len(path.read_text().splitlines()), 5000)

    def test_registri_menolak_nama_asing_sebelum_impor(self):
        from unittest.mock import patch
        from pycos.inti.ekstensi import pasang
        from pycos.inti.naluri import Naluri
        with patch('pycos.inti.ekstensi.import_module') as loader:
            with self.assertRaisesRegex(ValueError, 'tidak dikenal'):
                pasang(Naluri, nama='tidak-ada')
            loader.assert_not_called()

    def test_semua_modul_ekstensi_aman_diimpor_sebelum_facade(self):
        code = """
import sys
from importlib import import_module
from pycos.inti.ekstensi import URUTAN
for name in URUTAN:
    module = import_module('pycos.inti.ekstensi.' + name)
    assert callable(module.pasang)
assert 'pycos.inti.naluri' not in sys.modules
from pycos.inti.presentasi import Presentasi
assert not getattr(Presentasi.ucap, '__pycos_patch_ids__', ())
from pycos.inti.naluri import Naluri
assert Naluri(rng_seed=7).tick_count == 0
"""
        subprocess.run([sys.executable, '-c', code], check=True,
                       capture_output=True, text=True)

    def test_pickle_mesin_dan_model_memakai_jalur_lama(self):
        from pycos.inti.naluri import Naluri, Goal, Mood
        for obj in [Naluri(rng_seed=7), Goal('energi', .2, 'istirahat', 0), Mood(.1, .2)]:
            with self.subTest(cls=type(obj).__name__):
                restored = pickle.loads(pickle.dumps(obj))
                self.assertIs(type(restored), type(obj))
                self.assertEqual(type(obj).__module__, 'pycos.inti.naluri')
                if hasattr(obj, 'to_dict'):
                    self.assertEqual(restored.to_dict(), obj.to_dict())
                else:
                    self.assertEqual(restored, obj)


class InventarisPatchTest(unittest.TestCase):
    def test_inventaris_tidak_memuat_mesin(self):
        code = """
import sys
from pycos.dukungan import inventaris
assert inventaris() == []
assert 'pycos.inti.naluri' not in sys.modules
assert 'pycos.inti.mesin' not in sys.modules
"""
        subprocess.run([sys.executable, '-c', code], check=True,
                       capture_output=True, text=True)

    def test_descriptor_urutan_dan_snapshot_terpisah(self):
        from pycos.dukungan.patching import install_methods, wrap_method, inventaris

        class Sasaran:
            pass

        install_methods(Sasaran, {'biasa': lambda self: 1,
                                 'kelas': classmethod(lambda cls: cls.__name__),
                                 'statis': staticmethod(lambda: 3)}, patch_id='uji.inventaris')
        wrap_method(Sasaran, 'biasa', lambda original, self: original(self) + 1,
                    patch_id='uji.wrap')
        rows = [r for r in inventaris() if r['kelas'].endswith('.Sasaran')
                and r['kelas'].startswith(__name__ + '.InventarisPatchTest.')]
        self.assertEqual(['biasa', 'kelas', 'statis'], [r['metode'] for r in rows])
        self.assertEqual(['method', 'classmethod', 'staticmethod'], [r['jenis'] for r in rows])
        self.assertEqual(['uji.inventaris.biasa', 'uji.wrap'], rows[0]['patch_ids'])
        rows[0]['patch_ids'].append('bukan-patch')
        self.assertFalse(any('bukan-patch' in r['patch_ids'] for r in inventaris()))
        self.assertEqual(2, Sasaran().biasa())
        self.assertEqual('Sasaran', Sasaran.kelas())
        self.assertEqual(3, Sasaran.statis())

    def test_tidak_menjalankan_descriptor_dan_tidak_menggandakan_warisan(self):
        from pycos.dukungan.patching import inventaris, install_method

        class Berbahaya:
            def __get__(self, obj, cls):
                raise AssertionError('descriptor tidak boleh dieksekusi')

        class Induk:
            bahaya = Berbahaya()

        class Anak(Induk):
            pass

        install_method(Induk, 'metode', lambda self: 1, patch_id='uji.induk')
        install_method(Anak, 'lain', lambda self: 2, patch_id='uji.anak')
        rows = inventaris()
        anak = __name__ + '.' + Anak.__qualname__
        self.assertEqual(['lain'], [r['metode'] for r in rows if r['kelas'] == anak])
        Induk.metode = lambda self: 0
        self.assertFalse(any(r['kelas'] == __name__ + '.' + Induk.__qualname__
                             and r['metode'] == 'metode' for r in inventaris()))

    def test_kelas_sementara_tidak_ditahan_registri(self):
        import gc
        import weakref
        from pycos.dukungan.patching import install_method, inventaris
        def buat():
            class Sementara:
                pass
            install_method(Sementara, 'm', lambda self: 1, patch_id='uji.sementara')
            return weakref.ref(Sementara), Sementara.__module__ + '.' + Sementara.__qualname__
        ref, nama = buat()
        gc.collect()
        self.assertIsNone(ref())
        self.assertFalse(any(r['kelas'] == nama for r in inventaris()))

    def test_patch_gagal_tidak_masuk_inventaris(self):
        from pycos.dukungan.patching import install_methods, inventaris, PatchConflictError
        class Sasaran:
            def ada(self):
                return 1
        with self.assertRaises(PatchConflictError):
            install_methods(Sasaran, [('baru', lambda self: 2), ('ada', lambda self: 3)],
                            patch_id='uji.gagal')
        self.assertFalse(any('uji.gagal' in mid for r in inventaris() for mid in r['patch_ids']))
        self.assertFalse(hasattr(Sasaran, 'baru'))

    def test_inventaris_inti_cocok_fixture(self):
        from pycos.inti import naluri
        from pycos.dukungan.patching import inventaris
        expected = json.loads((Path(__file__).parent / 'fixtures' / 'patch_inti_r41.json').read_text())
        rows = inventaris()
        for cls, methods in expected.items():
            name = getattr(naluri, cls).__module__ + '.' + cls
            actual = {r['metode']: r['patch_ids'] for r in rows if r['kelas'] == name}
            self.assertEqual(methods, actual)

    def test_periksa_json_dan_teks_memuat_patch(self):
        result = subprocess.run([sys.executable, '-m', 'pycos', '--periksa', '--json'],
                                cwd=AKAR, check=True, capture_output=True, text=True)
        report = json.loads(result.stdout)
        self.assertTrue(report['ok'])
        self.assertTrue(any('naluri.kognisi.tick' in r['patch_ids'] for r in report['patch']))
        result = subprocess.run([sys.executable, '-m', 'pycos', '--periksa'],
                                cwd=AKAR, check=True, capture_output=True, text=True)
        self.assertIn('Inventaris patch runtime:', result.stdout)
        self.assertIn('naluri.persistensi.profil', result.stdout)


if __name__ == '__main__':
    unittest.main()
