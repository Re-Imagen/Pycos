# -*- coding: utf-8 -*-
"""Regresi runtime untuk narrowing tipe Nurani dan Tutur (R5.1)."""
from __future__ import annotations

import os
import io
import contextlib
import random
import sys
import unittest

AKAR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if AKAR not in sys.path:
    sys.path.insert(0, AKAR)


class TypingLanjutanTest(unittest.TestCase):
    @staticmethod
    def leksikon():
        from pycos.bahasa.tutur import Leksikon
        return Leksikon({'leksikon': [
            {'lema': 'tenang', 'bahasa': 'id', 'kelas': ['ADJ'],
             'modifier': {'pelemah': {'kiri': ['agak']}, 'penguat': {'kiri': ['sangat']}}},
            {'lema': 'ajar', 'bahasa': 'id', 'afiks': {'ver_kaus': 'mengajarkan', 'nom': 'pengajaran'}},
            {'lema': 'ikut', 'bahasa': 'id', 'afiks': {'ver_kaus': 'mengikuti'}}]})

    def test_adjektiva_modifier_tanpa_kerangka_tidak_crash(self):
        from pycos.bahasa.tutur import L3, GenContext, Slot, Kerangka, Node
        renderer = L3(self.leksikon(), random.Random(7))
        slot = Slot('sifat', 'ADJ', 'KUALITAS', False, 0., 0., True)
        ctx = GenContext(arousal=.1)
        self.assertEqual('tenang', renderer.frasa_adjektiva('tenang', ctx, slot=slot))
        frame = Kerangka(Node('TENANG', intensitas=.2), [slot], [])
        self.assertEqual('agak tenang', renderer.frasa_adjektiva('tenang', ctx, slot, frame))
        self.assertEqual('sangat tenang', renderer.frasa_adjektiva(
            'tenang', GenContext(arousal=.9), slot=slot))

    def test_morfologi_json_tetap_menghasilkan_string(self):
        leks = self.leksikon()
        self.assertEqual('mengajar', leks.nasalisasi('ajar'))
        self.assertEqual('mengikut', leks.nasalisasi('ikut'))
        self.assertEqual('memukul', leks.nasalisasi('pukul'))
        self.assertEqual('pengajaran', leks.nominalisasi('ajar'))
        self.assertIsNone(leks.nominalisasi('tidak-ada'))

    def test_template_json_dan_polaritas(self):
        from pycos.bahasa.tutur import L3, Node, GenContext
        renderer = L3(self.leksikon(), random.Random(7))
        node = Node('TENANG', modus='tanya')
        self.assertEqual('aku tenang?', renderer._render_ekspresi(
            node, {'ekspresi': ['aku {sifat}.']}, {'sifat': 'tenang'}, GenContext()))
        node.polaritas = '-'
        self.assertEqual('aku tidak tenang.', renderer._render_ekspresi(
            node, {'lema': 'tenang', 'ekspresi': ['aku tenang.']}, {}, GenContext()))

    def test_slot_relasi_optional_dan_utang(self):
        from pycos.refleksi.nurani import Nurani
        nur = Nurani(params={'enable_social_memory': True}, rng_seed=7)
        self.assertFalse(nur.menarik_diri('asing'))
        self.assertFalse(nur.utang_state('asing')['menarik_diri'])
        nur.tambah_utang('teman', 'janji', bobot=100.)
        self.assertTrue(nur.menarik_diri('teman'))
        self.assertTrue(nur.utang_state('teman')['menarik_diri'])

    def test_dimensi_bernilai_selalu_punya_observasi_dan_target(self):
        from pycos.inti.persona import PERSONA_CONTOH, Keadaan
        from pycos.refleksi.nurani import nilai_selaras
        for teks in ['', 'aku senang banget!', 'mungkin saya sedih', 'saya mohon bantuan']:
            result = nilai_selaras(PERSONA_CONTOH, Keadaan(), teks)
            self.assertIsInstance(result.dimensi, tuple)
            for dimensi in result.dimensi:
                if dimensi.skor is not None:
                    self.assertIsNotNone(dimensi.observasi)
                    self.assertIsNotNone(dimensi.target)
            self.assertTrue(all(isinstance(s, str) for s in result.saran))

    def test_label_optional_tidak_masuk_pemilihan_ambang(self):
        from pycos.refleksi.nurani import ContohLabel, ukur_selaras, ukur_fitur
        corpus = [ContohLabel('aku senang', selaras=True),
                  ContohLabel('saya sedih', selaras=False),
                  ContohLabel('mungkin bahagia', selaras=True),
                  ContohLabel('aku marah', selaras=False)]
        expected = ukur_selaras(corpus)
        self.assertEqual(expected, ukur_selaras(corpus + [ContohLabel('tanpa label')]))
        labels = [ContohLabel('aku senang', polaritas=1, formalitas='santai')]
        report = ukur_fitur(labels)
        self.assertIn('polaritas', report)
        self.assertIn('formalitas', report)

    def test_kategori_proto_diulang_mempertahankan_tipe_record(self):
        from pycos.refleksi.nurani import Nurani
        nur = Nurani(rng_seed=7)
        first = nur.serap_kategori('uji', kekuatan=.3, tick=0)
        second = nur.serap_kategori('uji', nama='kategori', kekuatan=.3, tick=1)
        self.assertEqual(2, second['jumlah'])
        self.assertGreater(second['kekuatan'], first['kekuatan'])
        self.assertEqual('kategori', second['nama'])

    def test_showcase_nurani_berseed_dan_semua_pilar_terlapor(self):
        from pycos.refleksi.nurani import Nurani
        with contextlib.redirect_stdout(io.StringIO()):
            first = Nurani.demo(seed=11)
            second = Nurani.demo(seed=11)
        self.assertEqual(first, second)
        for key in ['prior', 'gema', 'skala', 'konflik', 'bonus', 'relasi',
                    'prior_sosial', 'persepsi', 'introspeksi', 'meta']:
            self.assertIn(key, first)
        self.assertGreater(first['bonus'], 0)
        self.assertIn('brier_confidence', first['meta'])


if __name__ == '__main__':
    unittest.main()
