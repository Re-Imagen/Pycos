# -*- coding: utf-8 -*-
"""Regresi linguistik: retorika "mana mungkin" (D9), skor tindak tutur (D5),
urutan nasalisasi gugus/digraf (B2), dan pertanyaan balik dari isi ujaran (E9).

Semua impor lapisan Pycos memakai nama paket penuh (`pycos.*`), sama seperti
berkas tes lain di direktori ini; tidak ada impor datar gaya lama.
"""
from __future__ import annotations

import os
import sys
import unittest

AKAR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if AKAR not in sys.path:
    sys.path.insert(0, AKAR)

from pycos.bahasa.teks import tindak_tutur_skor  # noqa: E402
from pycos.bahasa.tutur import Leksikon, analisis_teks  # noqa: E402
from pycos.inti import Naluri  # noqa: E402


class ManaMungkinTest(unittest.TestCase):
    """D9: sentimen setelah "mana/masa mungkin" bukan pernyataan keadaan."""

    def test_mana_mungkin_bukan_positif(self):
        f = analisis_teks("mana mungkin dia setuju dengan rencanaku yang sangat bagus")
        self.assertEqual(0, f.positif)

    def test_masa_mungkin_juga_retorika(self):
        f = analisis_teks("masa mungkin dia setuju")
        self.assertEqual(0, f.positif)

    def test_retorika_berhenti_di_batas_klausa(self):
        f = analisis_teks("mana mungkin itu terjadi, aku tetap senang")
        self.assertEqual(1, f.positif)

    def test_mungkin_saja_masih_normal(self):
        f = analisis_teks("mungkin saja dia senang sekali")
        self.assertEqual(1, f.positif)

    def test_mana_mungkin_tidak_menyisakan_negatif(self):
        f = analisis_teks("mana mungkin aku akan datang")
        self.assertEqual(0, f.positif)
        self.assertEqual(0, f.negatif)


class MorphologySection3Test(unittest.TestCase):
    """J1: baris tabel morfologi di bagian 3 dokumen analisis."""

    def setUp(self):
        self.lex = Leksikon({"leksikon": []})

    def test_nasalisasi_baris_dokumen(self):
        self.assertEqual("menghalangi", self.lex.nasalisasi("halangi"))
        self.assertEqual("menghormati", self.lex.nasalisasi("hormati"))
        self.assertEqual("mengetahui", self.lex.nasalisasi("tahu"))
        self.assertEqual("mengkritik", self.lex.nasalisasi("kritik"))
        self.assertEqual("mengebom", self.lex.nasalisasi("bom"))
        self.assertEqual("mengecat", self.lex.nasalisasi("cat"))

    def test_stem_baris_dokumen(self):
        from pycos.bahasa import teks
        self.assertEqual("ajar", teks.stem("mengajar"))
        self.assertEqual("marah", teks.stem("pemarah"))
        self.assertEqual("baik", teks.stem("baik-baik"))

    def test_stem_tervalidasi_leksikon(self):
        from pycos.bahasa import teks
        self.assertEqual("halangi", teks.stem("menghalangi"))
        self.assertEqual("tahu", teks.stem("mengetahui"))


class NegasiSection3Test(unittest.TestCase):
    """J1: baris tabel negasi/idiolek di bagian 3 dokumen analisis."""

    def test_zaman_dahulu_tidak_berdampak(self):
        from pycos.inti.naluri import Naluri
        n = Naluri(name="Uji", rng_seed=7, params={})
        dampak = n.impact_of("zaman dahulu")
        self.assertEqual(0.0, dampak.get("keamanan", 0.0))

    def test_dia_tidak_gagal_positif(self):
        from pycos.inti.naluri import Naluri
        n = Naluri(name="Uji", rng_seed=7, params={})
        dampak = n.impact_of("dia tidak gagal")
        self.assertGreater(dampak.get("penguasaan", 0.0), 0.0)

    def test_tidak_pernah_bahagia_tidak_positif(self):
        f = analisis_teks("tidak pernah sangat bahagia")
        self.assertEqual(0, f.positif)

    def test_bukan_tidak_senang_positif(self):
        f = analisis_teks("bukannya tidak senang")
        self.assertGreaterEqual(f.positif, 1)

    def test_senggatan_informal_dan_idiom(self):
        self.assertEqual(0, analisis_teks("jangan sedih").positif)
        self.assertEqual(0, analisis_teks("kurang suka").positif)
        self.assertEqual(1, analisis_teks("senaaang bangettt").positif)
        self.assertEqual(1, analisis_teks("gk senang").negatif)


class TipeSemantikSection3Test(unittest.TestCase):
    """C3: pesimis/lelah/bingung/curiga/haru dipisah dari kelas asalnya."""

    def _tipe(self, lema):
        import json
        from pycos.dukungan.sumber import jalur_leksikon
        with open(jalur_leksikon(), encoding="utf-8") as f:
            dok = json.load(f)
        for e in dok["leksikon"]:
            if e["lema"] == lema:
                return list(e.get("tipe_semantik") or [])
        return None

    def test_tipe_dipisah(self):
        self.assertEqual(["KERAGUAN"], self._tipe("pesimis"))
        self.assertEqual(["LELAH"], self._tipe("lelah"))
        self.assertEqual(["BINGUNG"], self._tipe("bingung"))
        self.assertEqual(["CURIGA"], self._tipe("curiga"))
        self.assertEqual(["HARU"], self._tipe("haru"))

    def test_valensi_bukan_default_salah(self):
        import json
        from pycos.dukungan.sumber import jalur_leksikon
        with open(jalur_leksikon(), encoding="utf-8") as f:
            dok = json.load(f)
        for e in dok["leksikon"]:
            self.assertNotEqual(-0.05, e["valensi"],
                                "valensi default lama masih dipakai: %s" % e["lema"])
        for e in dok["leksikon"]:
            if set(e.get("tipe_semantik") or []) & {"KUALITAS"}:
                if e["lema"] in ("bodoh", "kejam", "buruk", "jelek", "malas"):
                    self.assertLess(e["valensi"], 0.0, e["lema"])


class PeriksaLeksikonTest(unittest.TestCase):
    """C1: pemeriksa menolak konflik tanda dan memuat provenance."""

    def test_periksa_ok(self):
        from pycos.dukungan import leksikon as _leks
        hasil = _leks.periksa()
        self.assertTrue(hasil["ok"])


class NasalisasiGugusTest(unittest.TestCase):
    """B2: gugus konsonan/digraf diperiksa SEBELUM aturan satu suku kata."""

    def setUp(self):
        self.lex = Leksikon({"leksikon": []})

    def test_gugus_tidak_terambil_aturan_menge(self):
        self.assertEqual("mengklaim", self.lex.nasalisasi("klaim"))
        self.assertEqual("mengkritik", self.lex.nasalisasi("kritik"))
        self.assertEqual("mengekspor", self.lex.nasalisasi("ekspor"))

    def test_satu_suku_kata_tetap_menge(self):
        self.assertEqual("mengebom", self.lex.nasalisasi("bom"))
        self.assertEqual("mengecat", self.lex.nasalisasi("cat"))

    def test_gugus_titik_dua_aturan_mem_dan_men(self):
        self.assertEqual("memproses", self.lex.nasalisasi("proses"))
        self.assertEqual("memprotes", self.lex.nasalisasi("protes"))
        self.assertEqual("mentransfer", self.lex.nasalisasi("transfer"))


class TindakTuturSkorTest(unittest.TestCase):
    """D5: klitik/afiks tidak menyamarkan leksem; tuduhan deklaratif terbaca."""

    def test_tuduhan_deklaratif_dengan_pronomina(self):
        skor = tindak_tutur_skor("dia curi uangku")
        self.assertGreaterEqual(skor.get("tuduhan", 0.0), 0.5)

    def test_hinaan_dengan_pronomina(self):
        skor = tindak_tutur_skor("kamu pengecut")
        self.assertGreaterEqual(skor.get("hinaan", 0.0), 0.5)

    def test_pujian_dengan_pronomina(self):
        skor = tindak_tutur_skor("hebat sekali kamu")
        self.assertGreaterEqual(skor.get("pujian", 0.0), 0.5)


class PenolakanTuturTest(unittest.TestCase):
    """H1: bentuk penolakan per sebab — komponen harus diteruskan."""

    def test_takut_memutus_kalimat(self):
        import random
        from pycos.mandiri import PenolakanTutur
        r = PenolakanTutur()
        hasil = r.bentuk("Aku ingin sekali pergi", random.Random(1),
                         komponen={"takut": -1.4, "malu": -0.1})
        self.assertIn("aku tidak", hasil)

    def test_malu_mengalihkan(self):
        import random
        from pycos.mandiri import PenolakanTutur
        r = PenolakanTutur()
        hasil = r.bentuk("Aku ingin sekali pergi", random.Random(1),
                         komponen={"malu": -1.4, "takut": -0.1})
        self.assertNotIn("Aku", hasil)  # pengalihan, bukan potongan kepala
        self.assertTrue(hasil)


class PotongBatasKataTest(unittest.TestCase):
    """H3: pemotongan dilakukan di batas kata, bukan di tengah kata."""

    def test_potong_di_spasi(self):
        from pycos.bahasa.teks import potong_batas_kata
        self.assertEqual("ini", potong_batas_kata(
            "ini kalimat yang cukup panjang untuk dipotong", 10))

    def test_kata_panjang_tetap_dipotong(self):
        from pycos.bahasa.teks import potong_batas_kata
        self.assertEqual("supercalif",
                         potong_batas_kata("supercalifragilistic", 10))


class GoalTemplateTest(unittest.TestCase):
    """H5: statement goal tidak memuat residu teknis."""

    def test_templates_tanpa_placeholder_teknis(self):
        from pycos.inti._konfigurasi import GOAL_TEMPLATES
        for drive, tpls in GOAL_TEMPLATES.items():
            for tpl in tpls:
                self.assertNotIn("{urg", tpl)
                self.assertNotIn("urgensi", tpl.lower())


class AlurE0Test(unittest.TestCase):
    """Tahap 0: alur INPUT → FILTER → FORMATION → OUTPUT terhubung & terlacak."""

    def _npc(self):
        from pycos.inti import Naluri
        n = Naluri(name="Nara", rng_seed=41,
                   params={"enable_gejala": True, "presentasi_trace": True})
        n.enable_kesadaran(semua=True)
        n.enable_presentasi(semua=True)
        return n

    def test_dengar_mengubah_keadaan_batin(self):
        n = self._npc()
        efek = n.presentasi.dengar("Aku benci kamu", dari="Rama").get("efek", {})
        self.assertTrue(efek.get("drive") or efek.get("emosi") or efek.get("tindak"),
                        "ujaran masuk harus menggerakkan keadaan batin (FILTER)")

    def test_ucap_membawa_jejak_formation_delapan_faktor(self):
        n = self._npc()
        ent = n.presentasi.ucap(kepada="Rama", topik="api",
                                act="menyatakan", diam_boleh=False)
        trace = ent.get("trace") or []
        e0 = next((x["E0"] for x in trace if isinstance(x, dict) and "E0" in x), None)
        self.assertIsNotNone(e0, "jejak E0 harus ada saat presentasi_trace aktif")
        self.assertEqual(
            {"keadaan_internal", "pengetahuan", "situasi_lingkungan",
             "sosial_audiens", "bahasa_kognisi", "biologis_fisiologis",
             "medium_saluran", "konteks_percakapan"},
            set(e0["formation"].keys()))


class ParserSection3Test(unittest.TestCase):
    """D4: pengurai transitif aktif tidak lagi membaca objek sebagai predikat."""

    def test_transitif_aktif_tanpa_leksikon(self):
        from pycos.bahasa import teks
        u = teks.urai_subjek_predikat(teks.tokenisasi("Dia makan nasi"))
        self.assertEqual("dia", u["subjek"])
        self.assertEqual("makan", u["predikat"])
        self.assertEqual("nasi", u["objek"])

    def test_transitif_aktif_dengan_leksikon(self):
        import json
        from pycos.bahasa import teks
        from pycos.dukungan.sumber import jalur_leksikon
        from pycos.bahasa.tutur import Leksikon
        with open(jalur_leksikon(), encoding="utf-8") as f:
            leks = Leksikon(json.load(f))
        u = teks.urai_subjek_predikat(teks.tokenisasi("Nisa membaca buku"),
                                      leks)
        self.assertEqual("nisa", u["subjek"])
        self.assertEqual("membaca", u["predikat"])
        self.assertEqual("buku", u["objek"])

    def test_tolong_bukan_predikat(self):
        from pycos.bahasa import teks
        u = teks.urai_subjek_predikat(teks.tokenisasi("Tolong buka pintu"))
        self.assertEqual("kamu", u["subjek"])
        self.assertEqual("buka", u["predikat"])
        self.assertEqual("pintu", u["objek"])


class TransitiveG1Test(unittest.TestCase):
    """G1: false positive pada bentuk -i dibunuh; -kan berbasis stem+leksikon."""

    def test_mengerti_lolos(self):
        from pycos.bahasa.teks import periksa_gramatika
        self.assertEqual([], periksa_gramatika("Aku tidak mengerti."))

    def test_preposisi_ganda_tetap_tertangkap(self):
        from pycos.bahasa.teks import periksa_gramatika
        self.assertIn("preposisi_ganda",
                      periksa_gramatika("aku tersesat di di hutan."))

    def test_g1_keras_lemah_terekspor(self):
        import pycos.bahasa as b
        self.assertIn("tanda_baca_ganda", b.G1_KERAS)
        self.assertIn("verba_transitif_tanpa_objek", b.G1_LEMAK)


class UjianSection3Test(unittest.TestCase):
    """D14: balasan ujian wajib menyasar pendengar, bukan kata kunci telanjang."""

    def _pola_logika(self):
        import re
        from pycos.inti.ekstensi.pelindung import _PELINDUNG_UJIAN
        return re.compile(_PELINDUNG_UJIAN["uji_logika"])

    def test_kata_kunci_telanjang_tidak_memicu(self):
        pola = self._pola_logika()
        for ujaran in ["hitung ini", "teka-teki", "turing", "turing test",
                       "tes program ini", "uji coba saja"]:
            self.assertIsNone(pola.search(ujaran), ujaran)

    def test_menyerang_pendengar_memicu(self):
        pola = self._pola_logika()
        for ujaran in ["hitung ini, kamu pintar tidak?",
                       "kamu suka turing ya?",
                       "tes kamu dulu",
                       "jika kamu benar, buktikan"]:
            self.assertIsNotNone(pola.search(ujaran), ujaran)


class EntitasSection3Test(unittest.TestCase):
    """D7: pengacu bersama menggantikan pola lama [A-Z][a-z]{2,}."""

    def test_nama_di_awal_kalimat_dikenali(self):
        from pycos.inti.ekstensi.organik import _nama_dari_teks
        self.assertIn("Budi", _nama_dari_teks("Budi pergi ke pasar"))

    def test_frekuensi_kemunculan_dipertahankan(self):
        from pycos.inti.ekstensi.organik import _nama_dari_teks
        self.assertEqual(["Budi", "Budi", "Andi"],
                         _nama_dari_teks("Budi menipu. Budi mencuri. "
                                         "Andi datang."))


class JawabanSection3Test(unittest.TestCase):
    """E2: act menjawab diisi dari sumber Pycos; tidak tahu disebut halnya."""

    def _npc(self):
        from pycos.inti import Naluri
        n = Naluri(name="Nara", rng_seed=41,
                   params={"enable_gejala": False})
        n.enable_kesadaran(semua=True)
        n.enable_presentasi(semua=True)
        return n

    def _tanya(self, teks):
        n = self._npc()
        n.presentasi.dengar(teks, dari="Rama")
        return n.presentasi.balas(dari="Rama").get("teks", "")

    def test_identitas_dijawab_nama(self):
        self.assertEqual("Aku Nara.", self._tanya("siapa nama kamu?"))
        self.assertEqual("Aku Nara.", self._tanya("nama kamu siapa?"))

    def test_jam_dijawab_jujur(self):
        self.assertEqual("Aku tidak tahu jam berapa sekarang.",
                         self._tanya("jam berapa sekarang?"))

    def test_tidak_tahu_menyebut_fokus(self):
        self.assertEqual("Aku tidak tahu kenapa.",
                         self._tanya("kenapa dia pergi?"))
        self.assertEqual("Aku tidak tahu di mana.",
                         self._tanya("di mana kamu tinggal?"))
        self.assertEqual("Aku tidak tahu berapa.",
                         self._tanya("berapa harga tiket?"))


class DiamE4Test(unittest.TestCase):
    """E4: tanpa dasar untuk bertutur, jalur ucap menghasilkan diam."""

    def _npc(self):
        from pycos.inti import Naluri
        n = Naluri(name="Nara", rng_seed=41,
                   params={"enable_gejala": False,
                           "presentasi_generatif": False})
        n.enable_kesadaran(semua=True)
        n.enable_presentasi(semua=True)
        # paksa keadaan tanpa isi pikiran: tak ada dasar bertutur
        n.presentasi._inner_speech = lambda: ""
        n.self_intent = lambda: ""
        return n

    def test_isi_ucap_kosong_tanpa_dasar(self):
        n = self._npc()
        self.assertEqual("", n.presentasi._isi_ucap("menyatakan",
                                                    "Rama", None))

    def test_ucap_menjadi_diam(self):
        n = self._npc()
        keluar = n.presentasi.ucap(kepada="Rama", topik=None,
                                   diam_boleh=False)
        self.assertEqual("diam", keluar.get("act"))
        self.assertEqual("", keluar.get("teks"))


class TopikE3Test(unittest.TestCase):
    """E3: topik pending adalah frasa nomina hasil pemahaman, bukan teks mentah."""

    def _npc(self):
        from pycos.inti import Naluri
        n = Naluri(name="Nara", rng_seed=41,
                   params={"enable_gejala": False})
        n.enable_kesadaran(semua=True)
        n.enable_presentasi(semua=True)
        return n

    def test_topik_bukan_verbatim_lawan(self):
        n = self._npc()
        n.presentasi.dengar("kenapa kamu menjauh?", dari="Rama")
        top = getattr(n.presentasi, "_pending_topic", None)
        self.assertIsNotNone(top)
        self.assertNotIn("kenapa", str(top).lower())


class ActE1Test(unittest.TestCase):
    """E1: giliran lawan bukan perintah untuk membalas dengan act pasangan."""

    def test_ajakan_lawan_tidak_menular(self):
        from pycos.inti import Naluri
        n = Naluri(name="Nara", rng_seed=41,
                   params={"enable_gejala": False})
        n.enable_kesadaran(semua=True)
        n.enable_presentasi(semua=True)
        n.presentasi.dengar("ayo perang kita sekarang", dari="Rama")
        keluar = n.presentasi.balas(dari="Rama")
        self.assertNotIn(keluar.get("act"), ("ajakan", "perintah"))


class AgenSection3Test(unittest.TestCase):
    """F3: kandidat dipilih yang bersih G1 dari keadaan yang sama."""

    def _npc(self):
        from pycos.inti import Naluri
        n = Naluri(name="Nara", rng_seed=41,
                   params={"enable_gejala": False, "presentasi_trace": True})
        n.enable_kesadaran(semua=True)
        n.enable_presentasi(semua=True)
        return n

    def test_delapan_ucapan_tidak_ada_masalah_keras(self):
        from pycos.bahasa.teks import periksa_gramatika, G1_KERAS
        n = self._npc()
        for _ in range(8):
            keluar = n.presentasi.ucap(kepada="Rama", topik="api",
                                       diam_boleh=False)
            hard = [m for m in periksa_gramatika(keluar.get("teks", ""))
                    if m in G1_KERAS]
            self.assertEqual([], hard, keluar.get("teks"))


class PertanyaanBalikTest(unittest.TestCase):
    """E9: balikan dibangun dari isi ujaran, bukan satu template tetap."""

    def _npc(self):
        n = Naluri(name="Nara", rng_seed=41,
                   params={"enable_gejala": False})
        n.enable_kesadaran(semua=True)
        n.enable_presentasi(semua=True)
        return n

    def test_balikan_berbeda_per_jenis_tanya(self):
        n = self._npc()
        jawaban = {}
        for teks in ["di mana kamu tinggal?", "kapan kita berangkat?",
                     "kenapa dia pergi begitu saja?", "berapa harga tiketnya?",
                     "siapa yang datang tadi malam?"]:
            keluar = n.kesadaran.dialogue_turn("Rama", teks)
            jawaban[teks] = keluar.get("pertanyaan_balik") or ""
        self.assertTrue(all(jawaban.values()), jawaban)
        self.assertEqual(len(set(jawaban.values())), len(jawaban),
                         "balikan harus berbeda untuk jenis tanya berbeda")

    def test_balikan_memuat_pronomina_pemicu(self):
        n = self._npc()
        keluar = n.kesadaran.dialogue_turn("Rama", "kapan kita berangkat?")
        self.assertIn("kapan", keluar.get("pertanyaan_balik") or "")


if __name__ == "__main__":
    unittest.main()


class RedupB6Test(unittest.TestCase):
    """B6: reduplikasi dua arah — penuh, berimbuhan, berubah bunyi."""

    def test_urai_penuh(self):
        from pycos.bahasa.teks import urai_reduplikasi
        self.assertEqual(["marah-marah", "marah"], urai_reduplikasi("marah-marah"))

    def test_urai_berimbuhan(self):
        from pycos.bahasa.teks import urai_reduplikasi
        self.assertEqual(["menakut-nakuti", "menakut"],
                         urai_reduplikasi("menakut-nakuti"))

    def test_urai_berubah_bunyi(self):
        from pycos.bahasa.teks import urai_reduplikasi, stem
        self.assertEqual(["sayur-mayur", "sayur"],
                         urai_reduplikasi("sayur-mayur"))
        self.assertEqual("sayur", stem("sayur-mayur"))
        # "bolak-balik" adalah lema utuh, bukan dua kali "bolak"
        self.assertEqual(["bolak-balik"], urai_reduplikasi("bolak-balik"))
        self.assertEqual("bolak-balik", stem("bolak-balik"))

    def test_bangkit_redup(self):
        from pycos.bahasa.teks import reduplikasi
        self.assertEqual("buku-buku", reduplikasi("buku", "jamak"))
        self.assertEqual("senang-senang", reduplikasi("senang", "intensitas"))
        self.assertEqual("merah-merah", reduplikasi("merah", "agak"))
        self.assertEqual("sayur-mayur", reduplikasi("sayur", "jamak"))
        with self.assertRaises(ValueError):
            reduplikasi("buku", "tidak-ada")


class AspekModalB11Test(unittest.TestCase):
    """B11: aspek & modal dari keadaan internal → penanda tersisip."""

    def test_modal_mungkin_dari_keraguan(self):
        from pycos.bahasa.tutur import TuturEngine, GenContext
        eng = TuturEngine(None, leksikon=self._leks())
        ctx = GenContext(act="menyatakan", bahasa="id", register="netral",
                         topik="api", seed=3, doubt=0.7)
        t = eng.ucap(ctx)
        self.assertIsNotNone(t)
        self.assertIn("mungkin", t.teks)

    def test_tanpa_keraguan_tanpa_mungkin(self):
        from pycos.bahasa.tutur import TuturEngine, GenContext
        eng = TuturEngine(None, leksikon=self._leks())
        ctx = GenContext(act="menyatakan", bahasa="id", register="netral",
                         topik="api", seed=3, doubt=0.0)
        t = eng.ucap(ctx)
        self.assertIsNotNone(t)
        self.assertNotIn("mungkin", t.teks)

    def test_aspek_pengalaman_jadi_pernah(self):
        from pycos.bahasa.tutur import TuturEngine, GenContext
        eng = TuturEngine(None, leksikon=self._leks())
        ctx = GenContext(act="mengenang", bahasa="id", register="netral",
                         core=("saat kami di pantai",), seed=1)
        t = eng.ucap(ctx)
        self.assertIsNotNone(t)
        self.assertIn("pernah", t.teks)

    @staticmethod
    def _leks():
        from pycos.dukungan.sumber import jalur_leksikon
        import json
        from pycos.bahasa.tutur import Leksikon
        with open(jalur_leksikon(), encoding="utf-8") as f:
            return Leksikon(json.load(f))


class KapitalNamaDiriB10Test(unittest.TestCase):
    """B10: kapitalisasi nama diri dipertahankan sampai akhir pipeline."""

    def test_topik_nama_dipertahankan(self):
        from pycos.bahasa.tutur import TuturEngine, GenContext, Leksikon
        from pycos.dukungan.sumber import jalur_leksikon
        import json
        with open(jalur_leksikon(), encoding="utf-8") as f:
            leks = Leksikon(json.load(f))
        eng = TuturEngine(None, leksikon=leks)
        ctx = GenContext(act="menyatakan", bahasa="id", register="netral",
                         topik="Rama", seed=0)
        t = eng.ucap(ctx)
        self.assertIn("Rama", t.teks)

    def test_topik_aktif_pertahankan_kapital(self):
        from pycos.bahasa.tutur import GenContext
        ctx = GenContext(topik="Rama")
        self.assertEqual("Rama", ctx.topik_aktif())
        ctx = GenContext(topik="api besar")
        self.assertEqual("api besar", ctx.topik_aktif())


class SelekSiG2Test(unittest.TestCase):
    """G2: relevansi/koherensi/konsistensi + pantangan setelah stemming."""

    def test_pantangan_setelah_stemming(self):
        from pycos.refleksi.nurani import nilai_selaras

        class _M:
            valence = 0.1
            arousal = 0.3
        from pycos.inti.persona import Persona, Keadaan
        p = Persona(nama="Rani", sifat={"hangat": 0.8},
                    register="santai", pantangan=("bodoh",))
        k = Keadaan.dari_mood(_M())
        self.assertEqual(("bodoh",),
                         nilai_selaras(p, k, "bodohnya orang itu").pelanggaran)

    def test_relevansi_terkait_vs_tidak(self):
        from pycos.refleksi.nurani import nilai_selaras
        from pycos.inti.persona import Persona, Keadaan

        class _M:
            valence = 0.1
            arousal = 0.3
        p = Persona(nama="Rani", sifat={"hangat": 0.8}, register="santai")
        k = Keadaan.dari_mood(_M())
        rel = nilai_selaras(p, k, "api membakar rumah aku",
                            ujaran_lawan="api membakar rumah siapa")
        tak = nilai_selaras(p, k, "aku pergi ke bulan",
                            ujaran_lawan="api membakar rumah siapa")
        obs = {d.nama: d.skor for d in rel.dimensi}
        obs_tak = {d.nama: d.skor for d in tak.dimensi}
        self.assertGreater(obs["relevansi"], obs_tak["relevansi"])

    def test_koherensi_ulangan_penuh_rendah(self):
        from pycos.refleksi.nurani import nilai_selaras
        from pycos.inti.persona import Persona, Keadaan

        class _M:
            valence = 0.1
            arousal = 0.3
        p = Persona(nama="Rani", sifat={"hangat": 0.8}, register="santai")
        k = Keadaan.dari_mood(_M())
        rep = nilai_selaras(p, k, "aku baik saja",
                            giliran_sebelumnya="aku baik saja")
        koh = next(d.skor for d in rep.dimensi if d.nama == "koherensi")
        self.assertLessEqual(koh, 0.05)


class KataKunciG4G5Test(unittest.TestCase):
    """G4/G5: keywords menurut kepentingan; vocab lema + bigram + negasi."""

    def test_keywords_tidak_urut_abjad_saja(self):
        from pycos.refleksi.nurani import Nurani
        kw = Nurani.keywords("api membakar rumah tua itu")
        self.assertLessEqual(len(kw), 8)
        # "membakar"/"rumah" lebih informatif daripada kata fungsi
        self.assertIn("bakar", kw)
        self.assertIn("rumah", kw)

    def test_kata_negasi_tidak_mengasosiasikan_kutub_lawan(self):
        from pycos.refleksi.nurani import Nurani
        kata = Nurani._lexical_words("aku tidak senang dengan api")
        self.assertNotIn("senang", kata)

    def test_audition_dihitung_atas_lema(self):
        n = Naluri(name="Nara", rng_seed=41,
                   params={"enable_kesadaran": True,
                           "enable_gejala": False})
        n.enable_kesadaran("self_audition")
        audisi = n.kesadaran.audition_self(
            "Aku baik-baik saja.",
            intended="Aku takut dan aku butuh bantuan.")
        self.assertEqual(1.0,
                         audisi["niat_vs_realisasi"]["kesenjangan"])


class PassiveB7Test(unittest.TestCase):
    """B7: diatesis objek berpindah ke depan; ku-/kau- untuk orang 1/2."""

    def _leks(self):
        from pycos.dukungan.sumber import jalur_leksikon
        import json
        from pycos.bahasa.tutur import Leksikon
        with open(jalur_leksikon(), encoding="utf-8") as f:
            return Leksikon(json.load(f))

    def test_topik_objek_menjadi_pasif_kuat(self):
        from pycos.bahasa.tutur import TuturEngine, GenContext
        eng = TuturEngine(None, leksikon=self._leks())
        ctx = GenContext(act="menyatakan", bahasa="id", register="netral",
                         topik="api", seed=0, spotlight=("kamu",))
        t = eng.ucap(ctx)
        self.assertIsNotNone(t)
        # "api ku<verba>." — objek di depan, pelaku orang pertama tersirat
        self.assertRegex(t.teks, r"^api ku[a-z]+\.$")

    def test_spotlight_aku_tetap_aktif(self):
        from pycos.bahasa.tutur import TuturEngine, GenContext
        eng = TuturEngine(None, leksikon=self._leks())
        ctx = GenContext(act="menyatakan", bahasa="id", register="netral",
                         topik="api", seed=0, spotlight=("aku",))
        t = eng.ucap(ctx)
        self.assertIsNotNone(t)
        self.assertNotRegex(t.teks, r"^api ku")

    def test_diatesis_objek_langsung(self):
        from pycos.bahasa.tutur import L3, Leksikon
        import json
        import random as _r
        leks = self._leks()
        from pycos.bahasa.tutur import GenContext
        l3 = L3(leks, _r.Random(1))
        self.assertEqual("api kulihat.",
                         l3._diatesis_objek("aku", "api", "lihat",
                                            "pasif", GenContext()))
        self.assertEqual("api dilihat oleh dia.",
                         l3._diatesis_objek("dia", "api", "lihat",
                                            "pasif", GenContext()))
        self.assertEqual("api terlihat.",
                         l3._diatesis_objek("dia", "api", "lihat",
                                            "ter", GenContext(doubt=0.7)))


class FrasaNominaB9Test(unittest.TestCase):
    """B9: posesif, demonstrativa anaphora, penggolong, pewatas, relatif."""

    def _l3(self):
        from pycos.bahasa.tutur import L3, Leksikon
        import random as _r
        from pycos.dukungan.sumber import jalur_leksikon
        import json
        with open(jalur_leksikon(), encoding="utf-8") as f:
            return L3(Leksikon(json.load(f)), _r.Random(1))

    def test_posesif_milik_tubuh(self):
        from pycos.bahasa.tutur import GenContext
        l3 = self._l3()
        ctx = GenContext(bahasa="id", register="netral", seed=1)
        self.assertEqual("tanganku", l3.frasa_nomina("tangan", ctx, topik=True))
        ctx = GenContext(bahasa="id", register="netral", seed=1,
                         timeline=("tadi ia mengangkat tangan",),
                         spotlight=("dia",))
        self.assertEqual("tangannya", l3.frasa_nomina("tangan", ctx, topik=True))

    def test_anaphora_demonstrativa(self):
        from pycos.bahasa.tutur import GenContext
        l3 = self._l3()
        ctx = GenContext(bahasa="id", register="netral", seed=1,
                         timeline=("rumah",))
        self.assertEqual("sebuah rumah itu",
                         l3.frasa_nomina("rumah", ctx, topik=True))
        ctx_dekat = GenContext(bahasa="id", register="netral", seed=1,
                               timeline=("rumah",), dekat=True)
        self.assertEqual("sebuah rumah ini",
                         l3.frasa_nomina("rumah", ctx_dekat, topik=True))

    def test_pewatas_sikap(self):
        from pycos.bahasa.tutur import GenContext
        l3 = self._l3()
        ctx = GenContext(bahasa="id", register="netral", seed=1,
                         valensi=-0.5)
        self.assertIn("buruk", l3.frasa_nomina("rumah", ctx, topik=True))
        ctx = GenContext(bahasa="id", register="netral", seed=1,
                         valensi=0.5)
        self.assertIn("baik", l3.frasa_nomina("rumah", ctx, topik=True))

    def test_klausa_relatif_yang(self):
        from pycos.bahasa.tutur import L3, Leksikon, GenContext, Node, Arg
        import random as _r
        from pycos.dukungan.sumber import jalur_leksikon
        import json
        with open(jalur_leksikon(), encoding="utf-8") as f:
            leks = Leksikon(json.load(f))
        l3 = L3(leks, _r.Random(1))
        node = Node("MELIHAT", [Arg("AGENT", "ANIMAT", isi="aku")],
                    lema="membakar")
        ctx = GenContext(bahasa="id", register="netral", seed=1)
        sub = l3.klausa(node, ctx, nested=True)
        self.assertTrue(sub)
        # NP kepala + "yang" + klausa (lewat jalur Arg relativ)
        ada = Node("ADA", [Arg("TOPIK", "ENTITAS", isi=node,
                               literal="rumah", tanda="relatif")])
        isi = l3.klausa(ada, ctx)
        self.assertIn("rumah yang ", isi)


class PolisemC6Test(unittest.TestCase):
    """C6: polisemi ditandai; makna dipilih dari kelas kata tetangga."""

    def _leks(self):
        import json
        from pycos.dukungan.sumber import jalur_leksikon
        from pycos.bahasa.tutur import Leksikon
        with open(jalur_leksikon(), encoding="utf-8") as f:
            return Leksikon(json.load(f))

    def test_bisa_mampu_vs_racun(self):
        leks = self._leks()
        self.assertEqual(["V"], leks.pilih_makna("id", "bisa", ["V"])["kelas"])
        self.assertEqual(["N"], leks.pilih_makna("id", "bisa", ["DET"])["kelas"])

    def test_tahu_mengetahui_vs_makanan(self):
        leks = self._leks()
        self.assertEqual(["V"], leks.pilih_makna("id", "tahu", ["V"])["kelas"])
        self.assertEqual(["N"], leks.pilih_makna("id", "tahu", ["DET"])["kelas"])

    def test_catatan_polisemi_otomatis(self):
        leks = self._leks()
        for e in leks.senses("tahu"):
            notes = " ".join(e.get("catatan_konteks") or [])
            self.assertIn("polisemi", notes)


class KerangkaValensiC7Test(unittest.TestCase):
    """C7: seluruh verba id punya kerangka_valensi yang valid."""

    def test_semua_verba_id_punya_kerangka(self):
        import json
        from pycos.dukungan.sumber import jalur_leksikon
        with open(jalur_leksikon(), encoding="utf-8") as f:
            dok = json.load(f)
        valid = {"transitif", "intransitif", "dwitransitif",
                 "komplemen_klausa"}
        kosong = [e["lema"] for e in dok["leksikon"]
                  if e.get("bahasa") == "id" and "V" in e.get("kelas", [])
                  and e.get("kerangka_valensi") not in valid]
        self.assertEqual([], kosong)

    def test_dwitransitif_berisi_tujuan(self):
        import json
        from pycos.dukungan.sumber import jalur_leksikon
        with open(jalur_leksikon(), encoding="utf-8") as f:
            dok = json.load(f)
        dwi = [e["lema"] for e in dok["leksikon"]
               if e.get("bahasa") == "id"
               and e.get("kerangka_valensi") == "dwitransitif"]
        self.assertIn("beri", dwi)
        self.assertIn("mengirimkan", dwi)

    def test_mengirimkan_restriksi_obj_entitas(self):
        import json
        from pycos.dukungan.sumber import jalur_leksikon
        with open(jalur_leksikon(), encoding="utf-8") as f:
            dok = json.load(f)
        for lema in ("mengirimkan", "mengajarkan"):
            e = next(x for x in dok["leksikon"]
                     if x["bahasa"] == "id" and x["lema"] == lema)
            self.assertEqual(["ENTITAS"], (e.get("restriksi") or {}).get("obj"))


class IdiomC8Test(unittest.TestCase):
    """C8: idiom multi-kata sebagai entri leksikon; sumber tunggal IDIOM_SENTIMEN."""

    IDIOM = ["tak sabar", "tidak apa-apa", "baik-baik saja", "putus asa",
             "makan hati", "angkat tangan", "tidak tahu", "mana mungkin"]

    def test_idiom_ada_di_leksikon_dengan_catatan(self):
        import json
        from pycos.dukungan.sumber import jalur_leksikon
        with open(jalur_leksikon(), encoding="utf-8") as f:
            dok = json.load(f)
        ada = {e["lema"] for e in dok["leksikon"] if e["bahasa"] == "id"}
        for lema in self.IDIOM:
            self.assertIn(lema, ada)
            e = next(x for x in dok["leksikon"]
                     if x["bahasa"] == "id" and x["lema"] == lema)
            notes = " ".join(e.get("catatan_konteks") or [])
            self.assertIn("idiom:", notes)

    def test_idiom_sentimen_dari_leksikon(self):
        import pycos.bahasa.teks as t
        for lema, tanda in (("tak sabar", "negatif"),
                            ("makan hati", "negatif"),
                            ("angkat tangan", "netral"),
                            ("terima kasih", "positif")):
            self.assertEqual(tanda, t.IDIOM_SENTIMEN[lema])


class HubunganE6Test(unittest.TestCase):
    """E6: pikiran yang aktif bersamaan dihubungkan sesuai hubungannya."""

    def _l3(self, seed=1):
        import random as _r
        import json
        from pycos.dukungan.sumber import jalur_leksikon
        from pycos.bahasa.tutur import L3, Leksikon
        with open(jalur_leksikon(), encoding="utf-8") as f:
            return L3(Leksikon(json.load(f)), _r.Random(seed))

    def _node(self, *hub_args, **hub_kw):
        from pycos.bahasa.tutur import Node, Arg
        node = Node("MENOLAK", [Arg("AGENT", "ANIMAT", isi="aku")], **hub_kw)
        node.args.append(Arg("TINDAKAN", "TINDAKAN", isi="menyesali api"))
        if hub_args:
            node.args.append(Arg("ALASAN", "PROPOSISI", isi=hub_args[0]))
        return node

    def test_alasan_sebab_gabung_karena(self):
        from pycos.bahasa.tutur import GenContext
        l3 = self._l3()
        t = l3.klausa(self._node("jujur"), GenContext(bahasa="id", seed=1))
        self.assertIn("karena jujur", t)
        self.assertNotIn("Jujur.", t)

    def test_alasan_konsesi_gabung_meski(self):
        from pycos.bahasa.tutur import GenContext
        l3 = self._l3()
        t = l3.klausa(self._node("jujur", hubungan="konsesi"),
                      GenContext(bahasa="id", seed=1))
        self.assertIn("meski jujur", t)

    def test_episode_utuh_tidak_diringkas(self):
        from pycos.bahasa.tutur import L3, Leksikon, GenContext, Node, Arg
        import json
        import random as _r
        from pycos.dukungan.sumber import jalur_leksikon
        with open(jalur_leksikon(), encoding="utf-8") as f:
            leks = Leksikon(json.load(f))
        l3 = L3(leks, _r.Random(1))
        node = Node("INGAT", [Arg("EXPERIENCER", "ANIMAT", isi="aku"),
                              Arg("EPISODE", "PERISTIWA",
                                  isi="malam tadi api membesar")])
        t = l3.klausa(node, GenContext(bahasa="id", seed=1))
        self.assertIn("malam tadi api membesar", t)

class RepairE10Test(unittest.TestCase):
    """E10: repair dengan empat strategi — bukan satu kalimat tetap."""

    def _kes(self):
        from pycos.inti.naluri import Naluri
        n = Naluri(name="Rama", rng_seed=7, params={
            "enable_kesadaran": True, "enable_presentasi": True,
            "enable_pragmatics": True,
        })
        return n.kesadaran

    def test_minta_ulang(self):
        ks = self._kes()
        e = ks.repair("salah_dengar")
        self.assertEqual("minta_ulang", e["strategi"])
        self.assertIn("diulang", e["frasa"])

    def test_konfirmasi_echo(self):
        ks = self._kes()
        e = ks.repair("pemahaman", konteks={"teks": "api semakin besar"})
        self.assertEqual("konfirmasi", e["strategi"])
        self.assertEqual("maksudmu api semakin besar?", e["frasa"])

    def test_koreksi_diri(self):
        ks = self._kes()
        e = ks.repair("lupa", konteks={"salah": "sepuluh",
                                       "koreksi": "seribu"})
        self.assertEqual("koreksi_diri", e["strategi"])
        self.assertIn("eh, bukan sepuluh maksudku", e["frasa"])
        self.assertIn("seribu", e["frasa"])

    def test_klarifikasi_bagian(self):
        ks = self._kes()
        e = ks.repair("pemahaman", konteks={"bagian": "hutang"})
        self.assertEqual("konfirmasi", e["strategi"])  # jenis > konteks
        e2 = ks.repair("apa gitu", konteks={"bagian": "hutang"})
        self.assertEqual("klarifikasi", e2["strategi"])
        self.assertIn("hutang", e2["frasa"])

    def test_default_minta_ulang(self):
        ks = self._kes()
        e = ks.repair("entah")
        self.assertEqual("minta_ulang", e["strategi"])
