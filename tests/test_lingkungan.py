# -*- coding: utf-8 -*-
"""Tes lingkungan uji: peta, gerak, objek, bahaya, cuaca, dan interaksi NPC.

Lingkungan diuji dengan dua jenis NPC: stub kecil yang deterministik dan
merekam peristiwa `tick`, serta `Naluri` sungguhan untuk jalur integrasi.
Fokusnya adalah kontrak dunia: aksi yang sah diterapkan, aksi yang terhalang
ditolak dengan alasan, efek drive sampai ke NPC lewat `tick(events=...)`,
satiasi mencegah pengulangan tanpa batas, dan state dunia dapat diserialisasi
tanpa menyalin state kognitif NPC.
"""
from __future__ import annotations

import os
import subprocess
import sys
import unittest

AKAR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if AKAR not in sys.path:
    sys.path.insert(0, AKAR)

from pycos.lingkungan import (ARAH, JENIS_DAPAT_DIAMBIL,  # noqa: E402
                              Badan, Lingkungan, ObjekDunia, Peta,
                              peta_contoh)


class StubNPC:
    """NPC minimal untuk menguji kontrak lingkungan tanpa lapisan kognitif.

    `aksi` adalah daftar nama aksi yang dipakai berurutan; bila habis, stub
    memilih kandidat pertama. Semua peristiwa `tick` direkam apa adanya.
    """

    def __init__(self, nama="Stub", aksi=None):
        self.name = nama
        self.levels = {"energi": -0.2, "keamanan": 0.0, "keingintahuan": -0.1,
                       "penguasaan": 0.0, "afiliasi": 0.0, "koherensi": 0.0}
        self.dipilih = list(aksi or [])
        self.aksi_dipilih = []
        self.peristiwa = []
        self.total_reward = 0.0

    def choose_action(self, kandidat):
        nama = self.dipilih.pop(0) if self.dipilih else kandidat[0]["name"]
        self.aksi_dipilih.append(nama)
        return {"action": nama, "score": 1.0}

    def tick(self, events=None, action_cost=False):
        self.peristiwa.append({"events": [dict(e) for e in (events or [])],
                               "action_cost": bool(action_cost)})

    def reward_for(self, deltas):
        nilai = sum(float(v) for v in (deltas or {}).values())
        self.total_reward += nilai
        return nilai

    def events(self, drive=None):
        keluar = [e for rekam in self.peristiwa for e in rekam["events"]]
        if drive is None:
            return keluar
        return [e for e in keluar if e.get("drive") == drive]


class PetaTest(unittest.TestCase):
    def test_dari_ascii_membangun_ukuran_dan_medan(self):
        peta = Peta.dari_ascii(["###", "#.#", "###"], nama="kamar")
        self.assertEqual(3, peta.lebar)
        self.assertEqual(3, peta.tinggi)
        self.assertEqual("kamar", peta.nama)
        self.assertEqual("dinding", peta.jenis((0, 0)))
        self.assertEqual("tanah", peta.jenis((1, 1)))

    def test_medan_menentukan_bisa_dilewati(self):
        peta = Peta.dari_ascii(["#.~^", ":,.."])
        self.assertFalse(peta.bisa_dilewati((0, 0)))   # dinding
        self.assertTrue(peta.bisa_dilewati((1, 0)))    # tanah
        self.assertFalse(peta.bisa_dilewati((2, 0)))   # air
        self.assertFalse(peta.bisa_dilewati((3, 0)))   # batu
        self.assertTrue(peta.bisa_dilewati((0, 1)))    # jalan
        self.assertTrue(peta.bisa_dilewati((1, 1)))    # rumput
        self.assertFalse(peta.bisa_dilewati((4, 0)), "di luar peta")

    def test_biaya_medan_urut(self):
        peta = Peta.dari_ascii([":,."])
        self.assertLess(peta.biaya((0, 0)), peta.biaya((2, 0)))
        self.assertLess(peta.biaya((2, 0)), peta.biaya((1, 0)))

    def test_simbol_tak_dikenal_dianggap_tanah(self):
        peta = Peta.dari_ascii(["?"])
        self.assertEqual("tanah", peta.jenis((0, 0)))
        self.assertTrue(peta.bisa_dilewati((0, 0)))

    def test_baris_tidak_seragam_ditolak(self):
        with self.assertRaises(ValueError):
            Peta.dari_ascii(["###", "##"])

    def test_petak_urut_dan_roundtrip(self):
        peta = Peta.dari_ascii(["#.", ".#"], nama="x")
        self.assertEqual([(0, 0), (1, 0), (0, 1), (1, 1)], peta.petak())
        pulih = Peta.from_dict(peta.to_dict())
        self.assertEqual(peta.to_dict(), pulih.to_dict())
        self.assertEqual(peta.nama, pulih.nama)

    def test_peta_contoh_konsisten(self):
        peta = peta_contoh()
        self.assertEqual(12, peta.lebar)
        self.assertEqual(8, peta.tinggi)
        self.assertTrue(peta.petak_bisa_dilewati())


class ObjekDuniaTest(unittest.TestCase):
    def test_efek_standar_per_jenis(self):
        obj = ObjekDunia("apel", "makanan", (0, 0))
        efek = obj.efek()
        self.assertGreater(efek["delta"]["energi"], 0.0)
        self.assertTrue(efek["sekali_pakai"])

    def test_atribut_menimpa_efek_dan_pesan(self):
        obj = ObjekDunia("jamu", "obat", (0, 0),
                         {"delta": {"keamanan": 0.1}, "pesan": "menenggak jamu"})
        efek = obj.efek()
        self.assertEqual(0.1, efek["delta"]["keamanan"])
        self.assertEqual("menenggak jamu", efek["pesan"])

    def test_tempat_aman_tidak_sekali_pakai(self):
        self.assertFalse(ObjekDunia("rumah", "tempat_aman", (0, 0)
                                    ).efek()["sekali_pakai"])

    def test_roundtrip_objek(self):
        obj = ObjekDunia("papan", "penanda", (1, 2), {"tersembunyi": True})
        pulih = ObjekDunia.from_dict(obj.to_dict())
        self.assertTrue(pulih.tersembunyi)
        self.assertEqual(obj.to_dict(), pulih.to_dict())


class PendaftaranTest(unittest.TestCase):
    def setUp(self):
        self.dunia = Lingkungan.dari_ascii([".....", "....."], seed=1)

    def test_tambah_npc_di_luar_peta_ditolak(self):
        with self.assertRaises(ValueError):
            self.dunia.tambah_npc(StubNPC("X"), (9, 9))

    def test_tambah_npc_di_medan_terhalang_ditolak(self):
        dunia = Lingkungan.dari_ascii(["#.."], seed=1)
        with self.assertRaises(ValueError):
            dunia.tambah_npc(StubNPC("X"), (0, 0))

    def test_nama_ganda_ditolak(self):
        self.dunia.tambah_npc(StubNPC("A"), (0, 0))
        with self.assertRaises(ValueError):
            self.dunia.tambah_npc(StubNPC("A"), (1, 0))

    def test_objek_di_luar_peta_ditolak(self):
        with self.assertRaises(ValueError):
            self.dunia.tambah_objek("makanan", (5, 0))

    def test_objek_tanpa_nama_mendapat_nomor_unik(self):
        a = self.dunia.tambah_objek("makanan", (1, 0))
        b = self.dunia.tambah_objek("makanan", (2, 0))
        self.assertNotEqual(a.nama, b.nama)

    def test_nama_badan_urut_dan_npc_mengembalikan_objek(self):
        npc_a, npc_b = StubNPC("B"), StubNPC("A")
        badan_a = self.dunia.tambah_npc(npc_a, (0, 0))
        self.dunia.tambah_npc(npc_b, (1, 0))
        self.assertIsInstance(badan_a, Badan)
        self.assertEqual(["A", "B"], self.dunia.nama_badan())
        self.assertIs(npc_b, self.dunia.npc("A"))
        self.assertIsNone(badan_a.jejak)


class GerakTest(unittest.TestCase):
    def test_bergerak_ke_petak_baru_memberi_bonus_eksplorasi(self):
        dunia = Lingkungan.dari_ascii(["....."], seed=1)
        npc = StubNPC("A", aksi=["bergerak:timur"])
        dunia.tambah_npc(npc, (0, 0))
        baris = dunia.langkah_semua()[0]
        self.assertTrue(baris["berhasil"])
        self.assertEqual((1, 0), dunia.badan["A"].posisi)
        self.assertGreater(baris["delta"]["keingintahuan"], 0.0)
        self.assertGreater(baris["delta"]["penguasaan"], 0.0)
        self.assertEqual(1, dunia.badan["A"].jarak_tempuh)
        # efek sampai ke NPC lewat tick(events=..., action_cost=True)
        self.assertTrue(npc.peristiwa[-1]["action_cost"])
        self.assertTrue(npc.events("keingintahuan"))
        self.assertEqual([(0, 0), (1, 0)], dunia.badan["A"].dikunjungi,
                         "posisi awal ikut tercatat sebagai petak dikenal")

    def test_petak_yang_sudah_dikunjungi_tanpa_bonus(self):
        dunia = Lingkungan.dari_ascii(["....."], seed=1)
        npc = StubNPC("A", aksi=["bergerak:timur", "bergerak:barat",
                                 "bergerak:timur"])
        dunia.tambah_npc(npc, (0, 0))
        for _ in range(3):
            dunia.langkah_semua()
        self.assertEqual((1, 0), dunia.badan["A"].posisi)
        self.assertNotIn("keingintahuan", dunia.riwayat[-1]["delta"])

    def test_dinding_menghalangi(self):
        dunia = Lingkungan.dari_ascii(["#.."], seed=1)
        dunia.tambah_npc(StubNPC("A"), (1, 0))
        baris = dunia.terapkan("A", "bergerak:barat")
        self.assertFalse(baris["berhasil"])
        self.assertEqual((1, 0), dunia.badan["A"].posisi)
        self.assertIn("terhalang", baris["catatan"])
        self.assertNotIn("bergerak:barat",
                         {c["name"] for c in dunia.aksi_tersedia("A")},
                         "arah terhalang tidak boleh ditawarkan")

    def test_batas_peta_dan_medan_air_ditolak(self):
        dunia = Lingkungan.dari_ascii(["..~"], seed=1)
        dunia.tambah_npc(StubNPC("A"), (1, 0))
        baris = dunia.terapkan("A", "bergerak:timur")
        self.assertFalse(baris["berhasil"])
        self.assertIn("tidak bisa dilewati", baris["pesan"])
        nama_kandidat = {c["name"] for c in dunia.aksi_tersedia("A")}
        self.assertNotIn("bergerak:timur", nama_kandidat)

    def test_petak_ditempati_npc_lain_ditolak(self):
        dunia = Lingkungan.dari_ascii(["....."], seed=1)
        dunia.tambah_npc(StubNPC("A"), (0, 0))
        dunia.tambah_npc(StubNPC("B"), (1, 0))
        baris = dunia.terapkan("A", "bergerak:timur")
        self.assertFalse(baris["berhasil"])
        self.assertEqual((0, 0), dunia.badan["A"].posisi)
        self.assertNotIn("bergerak:timur",
                         {c["name"] for c in dunia.aksi_tersedia("A")})

    def test_biaya_jalan_lebih_kecil_dari_rumput(self):
        dunia = Lingkungan.dari_ascii([":,."], seed=1)
        jalan = StubNPC("J", aksi=["bergerak:timur"])
        rumput = StubNPC("R", aksi=["bergerak:barat"])
        dunia.tambah_npc(jalan, (0, 0))
        dunia.tambah_npc(rumput, (2, 0))
        h_jalan = dunia.langkah("J")
        h_rumput = dunia.langkah("R")
        self.assertLess(h_jalan["delta"]["energi"],
                        h_rumput["delta"]["energi"])


class ObjekAksiTest(unittest.TestCase):
    def test_ambil_masuk_inventaris_dan_pakai_menghabiskannya(self):
        dunia = Lingkungan.dari_ascii(["....."], seed=1)
        dunia.tambah_objek("makanan", (0, 0), nama="roti")
        npc = StubNPC("A", aksi=["ambil:roti", "pakai:roti"])
        dunia.tambah_npc(npc, (0, 0))
        dunia.langkah_semua()
        self.assertEqual(["roti"], dunia.badan["A"].inventaris)
        self.assertFalse(dunia.objek["roti"].aktif, "sekali pakai harus habis")
        baris = dunia.langkah_semua()[0]
        self.assertTrue(baris["berhasil"])
        self.assertEqual([], dunia.badan["A"].inventaris)
        self.assertGreater(baris["delta"]["energi"], 0.0)

    def test_makanan_hanya_bisa_diambil_di_petak_yang_sama(self):
        dunia = Lingkungan.dari_ascii(["....."], seed=1)
        dunia.tambah_objek("makanan", (2, 0), nama="roti")
        dunia.tambah_npc(StubNPC("A"), (0, 0))
        baris = dunia.terapkan("A", "ambil:roti")
        self.assertFalse(baris["berhasil"])
        self.assertIn("tidak di petak ini", baris["pesan"])

    def test_dekati_bergerak_menuju_objek_jauh(self):
        dunia = Lingkungan.dari_ascii(["......"], seed=1)
        dunia.tambah_objek("air", (4, 0), nama="sumur")
        npc = StubNPC("A", aksi=["dekati:sumur", "dekati:sumur"])
        dunia.tambah_npc(npc, (0, 0))
        dunia.langkah_semua()
        self.assertEqual((1, 0), dunia.badan["A"].posisi)
        kandidat = {c["name"]: c for c in dunia.aksi_tersedia("A")}
        self.assertIn("dekati:sumur", kandidat)
        self.assertEqual((2, 0), tuple(kandidat["dekati:sumur"]["meta"]["tujuan"]))

    def test_amati_mengungkap_objek_tersembunyi(self):
        dunia = Lingkungan.dari_ascii(["....."], seed=1)
        dunia.tambah_objek("penanda", (2, 0), nama="papan",
                           tersembunyi=True)
        npc = StubNPC("A", aksi=["amati"])
        dunia.tambah_npc(npc, (0, 0))
        sebelum = dunia.observasi("A")
        self.assertEqual([], sebelum["objek"])
        dunia.langkah_semua()
        self.assertFalse(dunia.objek["papan"].tersembunyi)
        self.assertEqual(["papan"], [o["nama"]
                                     for o in dunia.observasi("A")["objek"]])

    def test_tempat_aman_memberi_berlindung_yang_melebur(self):
        dunia = Lingkungan.dari_ascii(["....."], seed=1)
        dunia.tambah_objek("tempat_aman", (1, 0), nama="rumah")
        npc = StubNPC("A", aksi=["pakai:rumah", "tunggu", "tunggu"])
        dunia.tambah_npc(npc, (0, 0))
        dunia.langkah_semua()
        self.assertEqual(2.0, dunia.badan["A"].berlindung)
        dunia.langkah_semua()
        self.assertEqual(1.0, dunia.badan["A"].berlindung)
        dunia.langkah_semua()
        self.assertEqual(0.0, dunia.badan["A"].berlindung)

    def test_menjauh_meninggalkan_bahaya(self):
        dunia = Lingkungan.dari_ascii(["....."], seed=1)
        dunia.tambah_objek("bahaya", (2, 0), nama="api")
        npc = StubNPC("A", aksi=["menjauh:api"])
        dunia.tambah_npc(npc, (1, 0))
        baris = dunia.langkah_semua()[0]
        self.assertTrue(baris["berhasil"])
        self.assertEqual((0, 0), dunia.badan["A"].posisi)
        self.assertGreater(baris["delta"]["keamanan"], 0.0)

    def test_aksi_tak_dikenal_gagal_dengan_catat(self):
        dunia = Lingkungan.dari_ascii(["....."], seed=1)
        dunia.tambah_npc(StubNPC("A"), (0, 0))
        hasil = dunia.terapkan("A", "terbang")
        self.assertFalse(hasil["berhasil"])
        self.assertEqual({}, hasil["delta"])

    def test_jenis_yang_tidak_bisa_diambil_tidak_ditawarkan(self):
        dunia = Lingkungan.dari_ascii(["....."], seed=1)
        dunia.tambah_objek("bahaya", (0, 0), nama="api")
        dunia.tambah_npc(StubNPC("A"), (0, 0))
        nama_aksi = {c["name"] for c in dunia.aksi_tersedia("A")}
        self.assertNotIn("ambil:api", nama_aksi)
        self.assertIn("pakai:api", nama_aksi)
        self.assertNotIn("api", JENIS_DAPAT_DIAMBIL)


class BahayaDanCuacaTest(unittest.TestCase):
    def test_paparan_bahaya_menurunkan_keamanan_dan_terhitung(self):
        dunia = Lingkungan.dari_ascii(["....."], seed=1)
        dunia.tambah_objek("bahaya", (1, 0), nama="api")
        npc = StubNPC("A", aksi=["tunggu"])
        dunia.tambah_npc(npc, (0, 0))
        baris = dunia.langkah_semua()[0]
        self.assertEqual(1, dunia.badan["A"].terpapar)
        self.assertIn("api", baris["paparan"])
        keamanan = npc.events("keamanan")
        self.assertTrue(any(float(e["delta"]) < 0.0 for e in keamanan))

    def test_berlindung_mengurangi_paparan(self):
        dunia = Lingkungan.dari_ascii(["......"], seed=1)
        dunia.tambah_objek("bahaya", (1, 0), nama="api")
        dunia.tambah_objek("tempat_aman", (0, 0), nama="rumah")
        npc = StubNPC("A", aksi=["pakai:rumah", "tunggu"])
        dunia.tambah_npc(npc, (0, 0))
        dunia.langkah_semua()
        dunia.langkah_semua()
        delta = [float(e["delta"]) for e in npc.events("keamanan")
                 if "terpapar" in str(e.get("reason", ""))]
        self.assertTrue(delta)
        self.assertGreater(delta[-1], -0.18, "paparan saat berlindung lebih kecil")

    def test_malam_memberi_peristiwa_keamanan(self):
        dunia = Lingkungan.dari_ascii(["....."], seed=1, mulai_jam=23.0)
        npc = StubNPC("A", aksi=["tunggu"])
        dunia.tambah_npc(npc, (0, 0))
        dunia.langkah_semua()
        self.assertEqual("malam", dunia.fase())
        alasan = [e["reason"] for e in npc.events("keamanan")]
        self.assertTrue(any("malam" in a for a in alasan))

    def test_jam_maju_dan_fase_berubah(self):
        dunia = Lingkungan.dari_ascii(["....."], seed=1, mulai_jam=8.0)
        dunia.tambah_npc(StubNPC("A"), (0, 0))
        self.assertEqual("pagi", dunia.fase())
        for _ in range(3):
            dunia.langkah_semua()
        self.assertEqual(11.0, dunia.jam)
        self.assertEqual("siang", dunia.fase())
        for _ in range(6):
            dunia.langkah_semua()
        self.assertEqual(17.0, dunia.jam)
        self.assertEqual("senja", dunia.fase())

    def test_cuaca_deterministik_dan_nilai_sah(self):
        def jejak_cuaca(seed):
            dunia = Lingkungan.dari_ascii(["....."], seed=seed)
            dunia.tambah_npc(StubNPC("A"), (0, 0))
            return [dunia.langkah_semua()[0]["cuaca"] for _ in range(30)]

        urutan = jejak_cuaca(5)
        self.assertEqual(urutan, jejak_cuaca(5))
        for cuaca in urutan:
            self.assertIn(cuaca, ("cerah", "berawan", "kabut", "hujan"))
        self.assertEqual("cerah", urutan[0], "cuaca awal selalu cerah")
        self.assertTrue(any(c in urutan for c in ("berawan", "kabut", "hujan")),
                        "cuaca tidak pernah berganti selama 30 langkah")

    def test_hujan_memberi_peristiwa_energi(self):
        dunia = Lingkungan.dari_ascii(["....."], seed=5)
        npc = StubNPC("A")
        dunia.tambah_npc(npc, (0, 0))
        dunia.cuaca = "hujan"
        dunia.cuaca_sisa = 99.0
        dunia.langkah_semua()
        alasan = [e["reason"] for e in npc.events("energi")]
        self.assertIn("hujan", alasan)


class SatiasiTest(unittest.TestCase):
    def test_aksi_yang_diulang_melemah(self):
        dunia = Lingkungan.dari_ascii(["....."], seed=1)
        npc = StubNPC("A", aksi=["istirahat", "istirahat", "istirahat"])
        dunia.tambah_npc(npc, (0, 0))
        delta = [dunia.langkah_semua()[0]["delta"]["energi"] for _ in range(3)]
        self.assertGreater(delta[0], delta[1])
        self.assertGreater(delta[1], delta[2])
        self.assertGreater(delta[0], 0.0)

    def test_kandidat_ikut_melemah_sehingga_npc_melihat_efek_nyata(self):
        dunia = Lingkungan.dari_ascii(["....."], seed=1)
        npc = StubNPC("A", aksi=["istirahat", "istirahat"])
        dunia.tambah_npc(npc, (0, 0))
        awal = {c["name"]: c for c in dunia.aksi_tersedia("A")}
        dunia.langkah_semua()
        setelah = {c["name"]: c for c in dunia.aksi_tersedia("A")}
        self.assertLess(setelah["istirahat"]["drive_effects"]["energi"],
                        awal["istirahat"]["drive_effects"]["energi"])

    def test_aksi_lain_pulih_perlahan(self):
        dunia = Lingkungan.dari_ascii(["....."], seed=1)
        npc = StubNPC("A", aksi=["istirahat", "tunggu", "tunggu"])
        dunia.tambah_npc(npc, (0, 0))
        dunia.langkah_semua()
        melemah = dunia.badan["A"].satiasi["istirahat"]
        for _ in range(2):
            dunia.langkah_semua()
        self.assertGreater(dunia.badan["A"].satiasi["istirahat"], melemah)

    def test_kebijakan_defensif_dipakai_tanpa_choose_action(self):
        class Pasif:
            name = "P"
            levels = {"energi": -0.9}

        dunia = Lingkungan.dari_ascii(["....."], seed=1)
        dunia.tambah_npc(Pasif(), (0, 0))
        hasil = dunia.pilih_aksi("P")
        self.assertEqual("defensif", hasil["sumber"])
        self.assertIn(hasil["aksi"], hasil["kandidat"])

    def test_pilihan_npc_yang_tidak_valid_jatuh_ke_defensif(self):
        npc = StubNPC("A", aksi=["aksi-yang-tidak-ada"])
        dunia = Lingkungan.dari_ascii(["....."], seed=1)
        dunia.tambah_npc(npc, (0, 0))
        hasil = dunia.pilih_aksi("A")
        self.assertEqual("defensif", hasil["sumber"])


class InteraksiTest(unittest.TestCase):
    def test_sapa_mengantre_peristiwa_untuk_sasaran(self):
        dunia = Lingkungan.dari_ascii(["....."], seed=1)
        a = StubNPC("A", aksi=["sapa:B"])
        b = StubNPC("B", aksi=["tunggu"])
        dunia.tambah_npc(a, (0, 0))
        dunia.tambah_npc(b, (1, 0))
        pertama = dunia.langkah("A")
        self.assertTrue(pertama["berhasil"])
        self.assertIn("sapa:B", a.aksi_dipilih)
        self.assertEqual([], b.events("afiliasi"), "belum diantre ke B")
        # B menerima antrean itu pada langkahnya sendiri
        dunia.langkah("B")
        disapa = [e for e in b.events("afiliasi")
                  if "disapa" in str(e.get("reason", ""))]
        self.assertEqual(1, len(disapa))
        self.assertGreater(float(disapa[0]["delta"]), 0.0)

    def test_sapa_terlalu_jauh_gagal(self):
        dunia = Lingkungan.dari_ascii(["....."], seed=1)
        dunia.tambah_npc(StubNPC("A"), (0, 0))
        dunia.tambah_npc(StubNPC("B"), (4, 0))
        hasil = dunia.terapkan("A", "sapa:B")
        self.assertFalse(hasil["berhasil"])
        self.assertIn("terlalu jauh", hasil["pesan"])

    def test_hampiri_mendekati_npc_lain(self):
        dunia = Lingkungan.dari_ascii(["......"], seed=1)
        dunia.tambah_npc(StubNPC("A", aksi=["hampiri:B"]), (0, 0))
        dunia.tambah_npc(StubNPC("B"), (4, 0))
        dunia.langkah("A")
        self.assertEqual((1, 0), dunia.badan["A"].posisi)

    def test_berinteraksi_dipanggil_pada_naluri(self):
        from pycos.inti import Naluri

        dunia = Lingkungan.dari_ascii(["....."], seed=1)
        a = Naluri(name="A", rng_seed=1)
        b = Naluri(name="B", rng_seed=2)
        dunia.tambah_npc(a, (0, 0), nama="A")
        dunia.tambah_npc(b, (1, 0), nama="B")
        hasil = dunia.terapkan("A", "sapa:B")
        self.assertTrue(hasil["berhasil"])
        self.assertIn("berinteraksi", hasil["catatan"])
        self.assertGreater(a.levels["afiliasi"], 0.0)


class ObservasiTest(unittest.TestCase):
    def test_observasi_memuat_objek_dan_ringkasan(self):
        dunia = Lingkungan.dari_ascii(["......"], seed=1, pandangan=3)
        dunia.tambah_objek("bahaya", (2, 0), nama="api")
        dunia.tambah_objek("penanda", (5, 0), nama="jauh")
        dunia.tambah_npc(StubNPC("A"), (0, 0))
        pengamatan = dunia.observasi("A")
        self.assertEqual(["api"], [o["nama"] for o in pengamatan["objek"]])
        self.assertEqual(2.0, pengamatan["objek"][0]["jarak"])
        self.assertEqual("timur", pengamatan["objek"][0]["arah"])
        self.assertIn("api", pengamatan["ringkas"])
        self.assertIn("aku di", pengamatan["ringkas"])
        self.assertEqual(1, len(pengamatan["paparan"]))

    def test_observasi_memuat_npc_lain_urut_jarak(self):
        dunia = Lingkungan.dari_ascii(["......"], seed=1)
        dunia.tambah_npc(StubNPC("A"), (0, 0))
        dunia.tambah_npc(StubNPC("Dekat"), (1, 0))
        dunia.tambah_npc(StubNPC("Jauh"), (3, 0))
        nama = [n["nama"] for n in dunia.observasi("A")["npc"]]
        self.assertEqual(["Dekat", "Jauh"], nama)

    def test_render_dan_lihat_sekitar(self):
        dunia = Lingkungan.dari_ascii([".....", "..#.."], seed=1)
        dunia.tambah_objek("makanan", (1, 0), nama="roti")
        dunia.tambah_npc(StubNPC("A"), (0, 0))
        gambar = dunia.render(nama="A")
        self.assertIn("@", gambar)
        self.assertIn("m", gambar, "simbol makanan harus muncul")
        potong = dunia.lihat_sekitar("A", radius=1)
        self.assertIn("@", potong)
        self.assertEqual(3, len(potong.splitlines()))


class SerialisasiTest(unittest.TestCase):
    def test_roundtrip_idempoten_dan_state_dipulihkan(self):
        dunia = Lingkungan.dari_ascii(["......", "....#."], seed=3)
        dunia.tambah_objek("makanan", (1, 0), nama="roti")
        dunia.tambah_objek("bahaya", (4, 1), nama="api")
        dunia.tambah_npc(StubNPC("A", aksi=["ambil:roti", "pakai:roti",
                                            "bergerak:timur"]), (0, 0))
        dunia.tambah_npc(StubNPC("B"), (2, 0))
        for _ in range(3):
            dunia.langkah_semua()
        data = dunia.to_dict()
        pulih = Lingkungan.from_dict(data)
        self.assertEqual(data, pulih.to_dict(), "round-trip tidak idempoten")
        self.assertEqual(dunia.badan["A"].posisi, pulih.badan["A"].posisi)
        self.assertEqual(dunia.badan["A"].inventaris,
                         pulih.badan["A"].inventaris)
        self.assertEqual(dunia.badan["A"].satiasi, pulih.badan["A"].satiasi)
        self.assertEqual(dunia.objek["roti"].aktif, pulih.objek["roti"].aktif)
        self.assertEqual(dunia.tick, pulih.tick)
        self.assertEqual(dunia.cuaca, pulih.cuaca)

    def test_npc_dapat_disambungkan_ulang(self):
        dunia = Lingkungan.dari_ascii(["....."], seed=1)
        npc = StubNPC("A")
        dunia.tambah_npc(npc, (0, 0))
        pulih = Lingkungan.from_dict(dunia.to_dict(), npcs={"A": npc})
        self.assertIs(npc, pulih.npc("A"))
        self.assertIsNone(Lingkungan.from_dict(dunia.to_dict()).badan["A"].npc)

    def test_state_kognitif_tidak_ikut_diserialisasi(self):
        from pycos.inti import Naluri

        dunia = Lingkungan.dari_ascii(["....."], seed=1)
        dunia.tambah_npc(Naluri(name="A", rng_seed=1), (0, 0), nama="A")
        data = dunia.to_dict()
        self.assertNotIn("levels", str(data["badan"]["A"]))
        self.assertNotIn("params", str(data["badan"]["A"]))

    def test_antrean_ikut_dipulihkan(self):
        dunia = Lingkungan.dari_ascii(["....."], seed=1)
        dunia.tambah_npc(StubNPC("A", aksi=["sapa:B"]), (0, 0))
        dunia.tambah_npc(StubNPC("B"), (1, 0))
        dunia.langkah("A")
        pulih = Lingkungan.from_dict(dunia.to_dict())
        self.assertEqual(1, len(pulih._antrean["B"]))


class IntegrasiNaluriTest(unittest.TestCase):
    def test_jalankan_dengan_naluri_dan_jejak(self):
        from pycos.inti import Naluri
        from pycos.memori import JejakPrediksi

        dunia = Lingkungan(peta=peta_contoh(), seed=7, pandangan=4)
        dunia.tambah_objek("makanan", (2, 1), nama="roti")
        dunia.tambah_objek("bahaya", (5, 5), nama="api")
        dunia.tambah_objek("tempat_aman", (2, 2), nama="rumah")
        for i, nama in enumerate(("Rama", "Ana")):
            npc = Naluri(name=nama, rng_seed=7 + i,
                         initial_levels={"energi": -0.5,
                                         "keingintahuan": -0.3})
            jejak = JejakPrediksi(naluri=npc, memory_retention_half_life=8)
            dunia.tambah_npc(npc, (1 + i, 1), nama=nama, jejak=jejak)
        hasil = dunia.jalankan(langkah=24)
        self.assertEqual(48, len(hasil["riwayat"]))
        self.assertEqual(48, hasil["statistik"]["langkah_riwayat"])
        for nama in dunia.nama_badan():
            badan = dunia.badan[nama]
            levels = badan.npc.levels
            self.assertTrue(all(-1.0 <= float(v) <= 1.0
                                for v in levels.values()), levels)
            x, y = badan.posisi
            self.assertTrue(dunia.peta.didalam((x, y)))
            self.assertTrue(dunia.peta.bisa_dilewati((x, y)))
            self.assertGreaterEqual(badan.langkah, 1)
            self.assertGreater(
                badan.jejak.performance_report()["episodes"], 0,
                "pengalaman tidak tercatat di JejakPrediksi")
        self.assertTrue(any(b["sumber_pilihan"] == "npc"
                            for b in hasil["riwayat"]))
        self.assertTrue(any(b["aksi"].startswith("bergerak")
                            or b["aksi"].startswith("dekati")
                            for b in hasil["riwayat"]),
                        "NPC tidak pernah bergerak di lingkungan")

    def test_jejak_memprediksi_setelah_pengalaman_pertama(self):
        from pycos.inti import Naluri
        from pycos.memori import JejakPrediksi

        dunia = Lingkungan.dari_ascii(["......"], seed=2)
        dunia.tambah_objek("bahaya", (1, 0), nama="api")
        npc = Naluri(name="A", rng_seed=2,
                     initial_levels={"keamanan": -0.6})
        jejak = JejakPrediksi(naluri=npc)
        dunia.tambah_npc(npc, (0, 0), nama="A", jejak=jejak)
        for _ in range(4):
            dunia.langkah_semua()
        prediksi = jejak.predict(dunia.riwayat[-1]["ringkas"],
                                 action=dunia.riwayat[-1]["aksi"],
                                 context=dunia.konteks(), tick=dunia.tick)
        self.assertIn(prediksi["memory"]["retrieval_status"],
                      ("ditemukan", "mati_diketahui"))
        self.assertIn("forecast", prediksi)

    def test_reward_gagal_dicatat_dan_dunia_tetap_berjalan(self):
        class RewardRusak(StubNPC):
            def reward_for(self, deltas):
                raise RuntimeError("reward tidak tersedia")

        dunia = Lingkungan.dari_ascii(["....."], seed=3)
        npc = RewardRusak("Gagal", aksi=["tunggu"])
        badan = dunia.tambah_npc(npc, (2, 0))

        hasil = dunia.langkah_semua()[0]

        self.assertEqual(0.0, hasil["reward"])
        self.assertTrue(any("reward_for gagal: reward tidak tersedia" in
                            entri.get("catatan", "") for entri in badan.log))
        self.assertEqual(1, len(dunia.riwayat))

    def test_lingkungan_tidak_menuntut_naluri(self):
        """Semua API kognitif bersifat opsional: stub pasif pun jalan."""
        class Pasif:
            name = "P"

        dunia = Lingkungan.dari_ascii(["....."], seed=1)
        dunia.tambah_npc(Pasif(), (0, 0))
        hasil = dunia.jalankan(langkah=5)
        self.assertEqual(5, len(hasil["riwayat"]))
        ringkas = hasil["statistik"]["per_npc"]["P"]
        self.assertEqual(5, ringkas["langkah"])
        self.assertIsNone(ringkas["levels"], "stub tanpa levels tidak diarangka")
        self.assertTrue(all(b["sumber_pilihan"] == "defensif"
                            for b in hasil["riwayat"]))


class JalurEksekusiTest(unittest.TestCase):
    def test_modul_dijalankan_lewat_dash_m(self):
        hasil = subprocess.run(
            [sys.executable, "-m", "pycos.lingkungan.dunia"], cwd=AKAR,
            capture_output=True, text=True)
        self.assertEqual(0, hasil.returncode, hasil.stderr[-2000:])
        self.assertIn("Demo LINGKUNGAN", hasil.stdout)
        self.assertIn("Statistik:", hasil.stdout)

    def test_berkas_dijalankan_langsung_tanpa_PYTHONPATH(self):
        jalur = os.path.join(AKAR, "pycos", "lingkungan", "dunia.py")
        hasil = subprocess.run(
            [sys.executable, jalur], cwd=os.path.dirname(jalur),
            env=dict(os.environ, PYTHONPATH=""),
            capture_output=True, text=True)
        self.assertEqual(0, hasil.returncode, hasil.stderr[-2000:])
        self.assertIn("Statistik:", hasil.stdout)


class KonstantaTest(unittest.TestCase):
    def test_arah_lengkap_dan_tidak_nol(self):
        self.assertEqual(8, len(ARAH))
        for nama, (dx, dy) in ARAH.items():
            self.assertEqual(str, type(nama))
            self.assertTrue((dx, dy) != (0, 0))

    def test_jenis_dapat_diambil_bukan_bahaya(self):
        self.assertNotIn("bahaya", JENIS_DAPAT_DIAMBIL)
        self.assertNotIn("tempat_aman", JENIS_DAPAT_DIAMBIL)


if __name__ == "__main__":
    unittest.main()
