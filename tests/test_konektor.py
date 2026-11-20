# -*- coding: utf-8 -*-
"""Adapter snapshot host: isolasi, kesetaraan keputusan, dan protokol CLI."""
from __future__ import annotations

from copy import deepcopy
import io
import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

AKAR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if AKAR not in sys.path:
    sys.path.insert(0, AKAR)

from pycos import konektor
from pycos.inti.naluri import Naluri


class KonektorTests(unittest.TestCase):
    def setUp(self):
        self.npc = Naluri(name='Rama', rng_seed=7)
        self.state = self.npc.to_dict()
        self.candidates = [{'name': 'istirahat', 'drive_effects': {'energi': .2}},
                           {'name': 'amati', 'drive_effects': {'keingintahuan': .1}}]

    def test_observasi_terisolasi_dan_dapat_diterapkan(self):
        world = {'ringkas': 'api terlihat', 'events': [{'drive': 'energi', 'delta': -.1}]}
        before = deepcopy((self.state, world))
        events = konektor.observasi(self.state, world)
        self.assertEqual((self.state, world), before)
        self.assertEqual(events[-1]['stimulus'], 'api terlihat')
        self.assertEqual(konektor.observasi(self.state, world), events)
        self.npc.tick(events=events)
        self.assertEqual(self.npc.tick_count, 1)
        events[0]['delta'] = 100
        self.assertEqual(world['events'][0]['delta'], -.1)
        self.assertEqual(konektor.observasi(self.state, {}), [])

    def test_aksi_memakai_mesin_tanpa_mutasi(self):
        before = deepcopy((self.state, self.candidates))
        result = konektor.aksi(self.state, self.candidates)
        expected = Naluri.from_dict(self.state).choose_action(
            deepcopy(self.candidates), record_eligibility=False)
        self.assertEqual(result, json.loads(json.dumps(expected)))
        self.assertEqual(result['action'], 'istirahat')
        self.assertEqual(konektor.aksi(self.state, self.candidates), result)
        self.assertEqual(before, (self.state, self.candidates))
        self.assertIsNone(konektor.aksi(self.state, [])['action'])
        result['candidate']['name'] = 'ubah'
        self.assertEqual(self.candidates[0]['name'], 'istirahat')

    def test_input_json_dan_domain_invalid(self):
        worlds = [[], {'unknown': 1}, {'ringkas': 1}, {'events': {}},
                  {'events': [None]}, {'events': [{'drive': 'asing', 'delta': .1}]},
                  {'events': [{'delta': float('nan')}]}, {1: 'key'},
                  {'events': [{'delta': object()}]}]
        for world in worlds:
            with self.subTest(world=world), self.assertRaises((ValueError, TypeError)):
                konektor.observasi(self.state, world)
        for state in [None, [], {'format': 'naluri/999'}]:
            with self.subTest(state=state), self.assertRaises(ValueError):
                konektor.aksi(state, [])
        for candidate in [{}, [None], [{'name': ''}],
                          [{'name': 'x', 'drive_effects': []}],
                          [{'name': 'x', 'drive_effects': {'unknown': 1}}],
                          [{'name': 'x', 'drive_effects': {'energi': True}}],
                          [{'name': 'x', 'prob': 2}], [{'name': 'x', 'cost': -1}],
                          [{'name': 'x', 'cost': float('inf')}],
                          [{'name': 'x', 'prob': '1'}]]:
            with self.subTest(candidate=candidate), self.assertRaises(ValueError):
                konektor.aksi(self.state, candidate)

    def call_main(self, request, expected=0, args=None):
        with patch('sys.stdin', io.StringIO(request)), patch('sys.stdout', new_callable=io.StringIO) as output:
            self.assertEqual(konektor.main(args or ['--json']), expected)
            return json.loads(output.getvalue())

    def test_main_sukses_galat_batas_dan_berkas(self):
        request = json.dumps({'npc': self.state, 'kandidat': self.candidates})
        result = self.call_main(request)
        self.assertTrue(result['ok'])
        self.assertEqual(result['hud']['nama'], 'Rama')
        self.assertEqual(result['pilihan']['action'], 'istirahat')
        self.assertEqual(self.call_main('{}')['hud']['nama'], 'HostNPC')
        for raw in ['{', '[]', '{"unknown":1}', '{"seed":true}',
                    '{"seed":NaN}', '{"kandidat":[null]}']:
            self.assertFalse(self.call_main(raw, 2)['ok'])
        with patch.object(konektor, 'BATAS_INPUT', 5):
            self.assertFalse(self.call_main('123456', 2)['ok'])
        with TemporaryDirectory() as folder:
            path = Path(folder) / 'request.json'
            path.write_text(request, encoding='utf-8')
            self.assertEqual(self.call_main('', args=['--json', '--input', str(path)]), result)
            path.unlink()
            self.assertFalse(self.call_main('', 2, ['--json', '--input', str(path)])['ok'])

    def test_cli_subprocess_json_tanpa_shell(self):
        request = {'dunia': {'ringkas': '"; $(perintah) <script> & bahasa Indonesia'},
                   'kandidat': self.candidates}
        result = subprocess.run([sys.executable, '-m', 'pycos.konektor', '--json'],
                                cwd=AKAR, input=json.dumps(request), capture_output=True,
                                text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, '')
        self.assertEqual(json.loads(result.stdout)['events'][0]['stimulus'],
                         request['dunia']['ringkas'])
        invalid = subprocess.run([sys.executable, '-m', 'pycos.konektor', '--json'],
                                 cwd=AKAR, input='bad', capture_output=True,
                                 text=True, timeout=30)
        self.assertEqual(invalid.returncode, 2)
        self.assertFalse(json.loads(invalid.stdout)['ok'])
