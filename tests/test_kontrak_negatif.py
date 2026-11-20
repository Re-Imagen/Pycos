# -*- coding: utf-8 -*-
"""Regresi kontrak publik: penolakan, postcondition, dan manifest rusak."""
from __future__ import annotations

from copy import deepcopy
import os
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch

AKAR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if AKAR not in sys.path:
    sys.path.insert(0, AKAR)

from pycos import kontrak as k  # noqa: E402


class KontrakNegatifTest(unittest.TestCase):
    def violation(self, report):
        self.assertIsInstance(report, dict)
        for leaf in report.get('pelanggaran', [report]):
            self.assertTrue(all(isinstance(leaf[name], str) and leaf[name]
                                for name in ['apa', 'pelanggar', 'dirugikan']))
        return report

    @staticmethod
    def npc(**overrides):
        values = dict(levels={d: 0. for d in k.DRIVE_KEYS}, tick_count=1)
        values.update(overrides)
        return SimpleNamespace(**values)

    def test_semua_operasi_menolak_pre_dan_post_tidak_sah(self):
        operations = ['lingkungan.tambah_npc', 'lingkungan.langkah', 'naluri.tick',
                      'naluri.choose_action', 'naluri.reward_for', 'jejak.record_experience',
                      'jejak.predict', 'jejak.reinforce', 'presentasi.ucap',
                      'penilai.nilai_selaras', 'pelacak.catat']
        for operation in operations:
            for phase in ['masuk', 'keluar']:
                with self.subTest(operation=operation, phase=phase):
                    self.violation(k.kontrak_operasi(operation, phase, hasil=object(), level=2))

    def test_level_alias_dan_validator_gagal_aman(self):
        for level in [-1, 4, True, '2']:
            self.violation(k.kontrak_operasi('tick', 'masuk', level=level))
        self.assertIsNone(k.check_operation('tick', 'exit', level=1))
        self.assertIsNone(k.check_operation('tidak ada', 'tidak ada', level=0))
        self.violation(k.check_operation('tidak ada', 'pre', level=2))
        self.violation(k.check_operation('tick', 'tidak ada', level=2))
        def rusak(*args):
            raise RuntimeError('validator rusak')
        original = k._OPERATION_CHECKS['naluri.tick']
        for checker in [rusak, lambda *args: {'apa': 'uji', 'pelanggar': 'uji', 'dirugikan': 'host'}]:
            with patch.dict(k._OPERATION_CHECKS, {'naluri.tick': {**original, 'masuk': (checker,)}}):
                self.violation(k.kontrak_operasi('tick', 'pre', level=2))
        with patch('pycos.kontrak._lintas_lapis', side_effect=RuntimeError('uji')):
            self.violation(k.kontrak_operasi('tick', 'pre', self.npc(), level=3))

    def test_tick_domain_counter_dan_generator_tidak_dikonsumsi(self):
        for value in [True, '0', float('nan'), float('inf'), 10 ** 400]:
            npc = self.npc(levels={**self.npc().levels, 'energi': value})
            self.violation(k.kontrak_operasi('tick', 'pre', npc,
                                            {'events': 'bukan event', 'action_cost': 1}, level=2))
        for tick in [True, '2', 7]:
            self.violation(k.kontrak_operasi('tick', 'post', self.npc(tick_count=tick),
                                            {'tick_before': 0}, hasil=1, level=2))
        self.violation(k.kontrak_operasi('tick', 'post', self.npc(levels={'energi': 2.}), level=2))
        visited = []
        def events():
            visited.append('dikonsumsi')
            yield {'drive': 'energi', 'delta': .1}
        stream = events()
        self.assertIsNone(k.kontrak_operasi('tick', 'pre', self.npc(), {'events': stream}, level=2))
        self.assertEqual([], visited)
        self.assertIsNone(k.kontrak_operasi('tick', 'post', self.npc(), {'tick_before': 0}, level=2))

    def test_lingkungan_resolusi_npc_dan_identitas_hasil(self):
        npc = self.npc()
        body = SimpleNamespace(npc=npc)
        env = SimpleNamespace(badan={'Rama': body})
        for args in [{'npc': npc}, {'args': [npc]}]:
            self.assertIsNone(k.kontrak_operasi('tambah_npc', 'pre', env, args, level=2))
            self.assertIsNone(k.kontrak_operasi('tambah_npc', 'post', env, args, body, level=2))
        for args in [{'nama': 'Rama'}, {'args': ['Rama']}, {}]:
            self.assertIsNone(k.kontrak_operasi('langkah', 'pre', env, args, level=2))
        self.violation(k.kontrak_operasi('langkah', 'pre', env, {'nama': 'hilang'}, level=2))
        self.violation(k.kontrak_operasi('tambah_npc', 'post', npc, {}, SimpleNamespace(npc=self.npc()), level=2))
        self.assertIsNone(k.kontrak_operasi('tambah_npc', 'post', npc, {}, body, level=2))
        self.violation(k.kontrak_operasi('langkah', 'post', env, hasil={}, level=2))
        self.assertIsNone(k.kontrak_operasi('langkah', 'post', env,
                         hasil=dict(aksi='diam', delta={}, posisi=(0, 0), npc='Rama', tick=1), level=2))

    def test_choose_reward_dan_record_batas_kecil(self):
        candidates = [{'name': 'diam'}]
        before = deepcopy(candidates)
        self.assertIsNone(k.kontrak_operasi('choose_action', 'post', argumen={'candidates': candidates},
                                          hasil={'action': 'diam'}, level=2))
        self.violation(k.kontrak_operasi('choose_action', 'post', argumen={'candidates': candidates},
                                       hasil={'action': 'di luar daftar'}, level=2))
        self.assertEqual(before, candidates)
        self.assertIsNone(k.kontrak_operasi('choose_action', 'post', argumen={'candidates': []}, hasil={}, level=2))
        self.assertIsNone(k.kontrak_operasi('choose_action', 'pre', argumen={'candidates': candidates}, level=2))
        for value in [None, {'energi': True}, {'energi': '0'}]:
            self.violation(k.kontrak_operasi('reward_for', 'pre', argumen={'deltas': value}, level=2))
        self.assertIsNone(k.kontrak_operasi('reward_for', 'pre', argumen={'deltas': {'energi': .1}}, level=2))
        for value in [True, float('nan'), float('inf'), 10 ** 400]:
            self.violation(k.kontrak_operasi('reward_for', 'post', hasil=value, level=2))
        self.assertIsNone(k.kontrak_operasi('reward_for', 'post', hasil=.2, level=2))
        self.assertIsNone(k.kontrak_operasi('record', 'pre', argumen={'stimulus': 'uji'}, level=2))
        self.assertIsNone(k.kontrak_operasi('record', 'post', hasil=1, level=2))

    def test_forecast_pre_post_dan_reinforce(self):
        good = {'forecast': {'drive_deltas': {d: 0. for d in k.DRIVE_KEYS}, 'impact': .1, 'confidence': .8}}
        self.assertIsNone(k.kontrak_operasi('predict', 'pre', argumen={'stimulus': 'uji'}, level=2))
        self.assertIsNone(k.kontrak_operasi('predict', 'post', hasil=good, level=2))
        bad_results = [{}, {'forecast': {}}, {'forecast': {'drive_deltas': {}}}]
        for value in [True, 'rusak', float('nan'), float('inf'), 10 ** 400, 2.]:
            bad = deepcopy(good)
            bad['forecast']['drive_deltas']['energi'] = value
            bad['forecast']['impact'] = value
            bad['forecast']['confidence'] = value
            bad_results.append(bad)
        for bad in bad_results:
            with self.subTest(bad=bad):
                self.violation(k.kontrak_operasi('predict', 'post', hasil=bad, level=2))
        self.assertIsNone(k.kontrak_operasi('reinforce', 'pre', argumen={'prediction': {'stimulus': 'uji'}}, level=2))
        self.violation(k.kontrak_operasi('reinforce', 'pre', argumen={'stimulus': 'uji', 'prediction': []}, level=2))
        for value in [True, 0, -1, '1']:
            self.violation(k.kontrak_operasi('reinforce', 'post', hasil={'episode_id': value}, level=2))
        for result in [{'id': 1}, {}]:
            self.assertIsNone(k.kontrak_operasi('reinforce', 'post', hasil=result, level=2))

    def test_ucap_penilai_dan_pelacak(self):
        self.assertIsNone(k.kontrak_operasi('ucap', 'pre', SimpleNamespace(), level=2))
        for result in [{}, {'act': 'diam'}]:
            self.assertIsNone(k.kontrak_operasi('ucap', 'post', hasil=result, level=2))
        self.violation(k.kontrak_operasi('ucap', 'post', hasil={'act': 1}, level=2))
        self.violation(k.kontrak_operasi('nilai_selaras', 'pre', argumen={
            'persona': {'nama': '', 'sifat': []}, 'keadaan': {}, 'teks': ''}, level=2))
        self.violation(k.kontrak_operasi('nilai_selaras', 'post', hasil={'status': '', 'skor': 2., 'dimensi': {}}, level=2))
        self.assertIsNone(k.kontrak_operasi('nilai_selaras', 'post', hasil={'status': 'tidak_dapat_dinilai', 'skor': None, 'dimensi': ()}, level=2))
        self.assertIsNone(k.kontrak_operasi('pelacak.catat', 'pre', {'kapasitas': 2}, {'laporan': {'status': 'selaras'}}, level=2))
        self.assertIsNone(k.kontrak_operasi('pelacak.catat', 'post', level=2))
        self.violation(k.kontrak_operasi('pelacak.catat', 'post', hasil=1, level=2))

    def test_lintas_lapis_mismatch_dan_alias_inggris(self):
        owner = self.npc(params={}, nurani=SimpleNamespace(drives=['energi'], params={}))
        owner.kesadaran = SimpleNamespace(naluri=self.npc())
        self.violation(k.check_operation(operation='tick', phase='pre', subject=owner, level=3))
        self.violation(k.check_operation(operasi='ucap', fase='pre', subjek=SimpleNamespace(naluri=owner), level=3))
        self.violation(k.check_operation('predict', 'pre', SimpleNamespace(naluri=owner), {'stimulus': 'uji'}, level=3))
        self.assertIsNone(k.verify_startup(actual_drives=k.DRIVE_KEYS))
        self.violation(k.verify_startup(actual_drives=['energi']))
        report = self.violation(k.kontrak_operasi('tick', 'pre', level=2))
        error = k.ContractViolationError(report)
        self.assertEqual(report, error.violation)
        self.assertIsNot(report, error.violation)

    def test_manifest_skema_field_dan_operasi_rusak(self):
        def manifest(field, requirement, operation=None, op_requirement=None):
            promises = {'P': {'fields': {'x': field}, 'operations': {'op': operation}}}
            needs = {'C': {'dependencies': {'P': {'fields': {'x': requirement},
                     'operations': {'op': op_requirement}}}}}
            return k.verifikasi_startup(promises, needs)
        good = {'shape': 'mapping', 'key_type': 'str', 'value_type': 'float', 'keys': ['x'], 'range': (-1., 1.)}
        need = {**good, 'value_type': 'number'}
        op = {'callable': True, 'phases': ['pre', 'post']}
        self.assertIsNone(manifest(good, need, op, {'callable': True, 'phases': ['pre']}))
        for field in [None, {}, {**good, 'shape': 'list'}, {**good, 'keys': None},
                      {**good, 'keys': []}, {**good, 'range': (0., .5)},
                      {**good, 'range': ('bad', 1)}, {**good, 'range': (float('nan'), 1)}]:
            self.violation(manifest(field, need, op, {}))
        self.violation(manifest(good, 'bad', op, {}))
        for broken in [None, {}, {'callable': False}, {'callable': True, 'phases': []}]:
            self.violation(manifest(good, need, broken, {'callable': True, 'phases': ['post']}))
        self.violation(manifest(good, need, op, 'bad'))
        self.assertIsNone(manifest(None, {'optional': True}, None, {'optional': True}))

    def test_manifest_dependency_hilang_dan_rusak(self):
        for promises, needs in [([], {}), ({}, []), ({}, {'C': {'dependencies': []}}),
                               ({}, {'C': {'dependencies': {'P': 'bad'}}}),
                               ({}, {'C': {'dependencies': {'P': {}}}})]:
            self.violation(k.verifikasi_startup(promises, needs))
        self.assertIsNone(k.verifikasi_startup({}, {'C': {'dependencies': {'P': {'optional': True}}}}))


if __name__ == '__main__':
    unittest.main()
