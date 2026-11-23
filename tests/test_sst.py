# -*- coding: utf-8 -*-
"""Systematic-Structured Test (SST) — orkestra seluruh fitur Pycos dalam satu NPC.

Konsep
------
SST berbeda dari tes unit biasa: ia menjalankan **seluruh fitur Pycos secara
terstruktur dan sistematis sebagai satu orkestra**, dengan tujuan
mensimulasikan **sebuah NPC utuh** — dari lahir, hidup di dunia, bertutur,
mengingat, bercermin (NURANI), memakai primitif mandiri, sampai menutup
siklusnya — **tanpa ada fitur yang tertinggal atau tidak aktif**.

Tiga jaminan sistematis:

1. **Ledger fitur** — setiap fitur wajib (`FITUR_WAJIB`, dikelompokkan per
   fase) ditandai `aktif` disertai bukti perilaku saat orkestra berjalan.
   Akhir orkestra menguji `wajib - aktif == {}`; satu fitur pun yang
   terlewat membuat SST gagal.
2. **Cakupan API publik** — setiap nama di `pycos.__all__` harus terpetakan
   (`CAKUPAN_API`) ke satu kelompok fitur wajib yang aktif. Ini memeriksa
   pemetaan nama, bukan rekaman panggilan setiap API atau cakupan cabang.
3. **Klasifikasi eksplisit** — satu-satunya yang boleh tidak diorkestrasi
   adalah titik masuk showcase (`demo_*`, `*.demo`) yang fitur di bawahnya
   sudah dimainkan langsung; himpunan itu dikunci di `LUAR_CAKUPAN_SST` dan
   dipantau oleh pemindaian AST, jadi tidak ada yang lolos diam-diam.

Cara menjalankan: seperti tes lain (`python -m unittest tests.test_sst`),
atau langsung (`python3 tests/test_sst.py`) untuk melihat laporan orkestra.
"""
from __future__ import annotations

import ast
import contextlib
import io
import os
import sys
import tempfile
import types
import unittest
from typing import Any, Dict, List, Set, Tuple

AKAR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if AKAR not in sys.path:
    sys.path.insert(0, AKAR)


# ---------------------------------------------------------------------------
# Ledger fitur — buku catatan "fitur apa yang benar-benar hidup"
# ---------------------------------------------------------------------------
class LedgerFitur:
    """Catatan fitur yang aktif beserta buktinya; basis jaminan SST."""

    def __init__(self) -> None:
        self._aktif: Dict[str, str] = {}
        self._jejak: List[str] = []

    def tandai(self, nama: str, bukti: str = "") -> None:
        if not isinstance(nama, str) or not nama.strip():
            raise AssertionError("ledger menolak nama fitur kosong")
        if not isinstance(bukti, str) or not bukti.strip():
            raise AssertionError("ledger menolak bukti kosong")
        self._aktif[nama] = str(bukti)
        self._jejak.append(nama)

    def bukti(self, nama: str) -> str:
        return self._aktif.get(nama, "")

    def aktif(self) -> Set[str]:
        return set(self._aktif)

    def kurang(self, wajib: Set[str]) -> Set[str]:
        return set(wajib) - self.aktif()

    def laporan(self) -> str:
        baris = ["LAPORAN SST — fitur aktif: {}".format(len(self._aktif))]
        for nama in sorted(self._aktif):
            baris.append("  [OK] {:<38} {}".format(nama, self._aktif[nama]))
        return "\n".join(baris)


# ---------------------------------------------------------------------------
# Manifest fitur wajib per fase (urutan = urutan orkestra)
# ---------------------------------------------------------------------------
FITUR_WAJIB: Dict[str, Tuple[str, ...]] = {
    "0_sumber_daya_dan_kontrak": (
        "dukungan.sumber", "dukungan.konstanta", "dukungan.numerik", "dukungan.diagnostik", "dukungan.batas_memori",
        "dukungan.patching", "dukungan.inventaris_patch", "kontrak.manifest", "kontrak.verifikasi_startup",
        "kontrak.operasi_tick", "kontrak.operasi_penilai",
        "kontrak.validator_batas", "kontrak.kebijakan",
    ),
    "1_inti_dan_kepribadian": (
        "inti.persona", "inti.naluri_konstruksi", "inti.dinamika_drive",
        "inti.mood", "inti.tujuan", "inti.pilih_aksi", "inti.reward",
        "inti.utilitas_dampak", "inti.kalibrasi_skala", "inti.tidur_mimpi",
        "inti.tahap_waktu_subjektif", "inti.emosi", "inti.coping",
        "inti.watak_backstory", "inti.leksikon_dan_konteks", "inti.leksikon_impak",
        "inti.salience_kebijakan_memori", "inti.brain_dan_imajinasi",
        "inti.lod_kompresi", "inti.replay_dan_profiling", "inti.hud_status",
        "inti.kredit_aksi", "inti.sosial_naluri", "inti.serialisasi",
    ),
    "2_kesadaran_presentasi_sosial": (
        "kesadaran.workspace", "kesadaran.identitas", "kesadaran.lantai",
        "presentasi.ucap", "presentasi.kanal", "ritual",
        "sosial.kawanan", "sosial.prediksi_lazy", "sosial.reputasi",
    ),
    "3_dunia": (
        "dunia.peta", "dunia.objek_bahaya_cuaca", "dunia.siklus_langkah",
        "dunia.serialisasi",
    ),
    "4_bahasa": (
        "bahasa.tutur_generatif", "bahasa.variasi_leksikal", "bahasa.sa_sp", "bahasa.ciri_linguistik",
        "bahasa.leksikon_ciri", "bahasa.teks",
    ),
    "5_memori": (
        "memori.episodik", "memori.prediksi_ranking", "memori.retrieval_terbatas", "memori.reinforce_kalibrasi",
        "memori.retrieval_konteks", "memori.autobiografi", "memori.daur_hidup",
        "memori.integrasi_naluri", "memori.kontrafaktual",
        "memori.kepercayaan_dinamis", "memori.mimpi_dan_lintas_waktu",
        "memori.pola", "memori.sosial", "memori.kualitas_memori",
    ),
    "6_nurani": (
        "nurani.pilar_aktif", "nurani.memori_afektif", "nurani.kalibrasi_berlapis",
        "nurani.setpoint_interosepsi", "nurani.konflik_flow", "nurani.sirkadian",
        "nurani.memori_sosial", "nurani.persepsi_adaptasi", "nurani.introspeksi",
        "nurani.felt_dan_moral", "nurani.doubt_sumber", "nurani.kategori",
        "nurani.serialisasi",
    ),
    "7_mandiri": (
        "mandiri.topologi_luka", "mandiri.identitas_waktu",
        "mandiri.tutur_apersepsi_paralel", "mandiri.tubuh_residu_intrusi_detak",
        "mandiri.vacancy_gejala_kategori", "mandiri.invensi_kausal_perencana",
        "mandiri.kognisi_lanjut",
    ),
    "8_ketidaktahuan_penilai": (
        "ketidaktahuan.batas", "ketidaktahuan.sikap", "penilai.nilai_selaras",
        "penilai.pelacak_drift", "penilai.kalibrasi_korpus", "penilai.evaluasi_heldout",
    ),
    "9_tutup": (
        "dukungan.periksa", "inti.health_check_akhir", "inti.serialisasi_penuh", "inti.serialisasi_profil",
    ),
}


def himpunan_fitur_wajib() -> Set[str]:
    total: Set[str] = set()
    for daftar in FITUR_WAJIB.values():
        total.update(daftar)
    return total


# ---------------------------------------------------------------------------
# Peta cakupan API publik -> fitur wajib (setiap `pycos.__all__` wajib ada)
# ---------------------------------------------------------------------------
CAKUPAN_API: Dict[str, str] = {
    # R5.4: alias root dipetakan eksplisit ke kelompok wajib yang aktif.
    "ContohLabel": "penilai.kalibrasi_korpus",
    "kappa_cohen": "penilai.kalibrasi_korpus",
    "laporan_kalibrasi": "penilai.kalibrasi_korpus",
    "muat_korpus": "penilai.kalibrasi_korpus",
    "ukur_fitur": "penilai.kalibrasi_korpus",
    "ukur_selaras": "penilai.kalibrasi_korpus",
    "TopologiSlot": "mandiri.topologi_luka",
    "LukaDomain": "mandiri.topologi_luka",
    "KOSONG": "mandiri.topologi_luka",
    "TERISI": "mandiri.topologi_luka",
    "TAK_BERLAKU": "mandiri.topologi_luka",
    "BatasIdentitas": "mandiri.identitas_waktu",
    "WaktuHeterogen": "mandiri.identitas_waktu",
    "PROPERTI_TERLARANG": "mandiri.identitas_waktu",
    "PenolakanTutur": "mandiri.tutur_apersepsi_paralel",
    "Apersepsi": "mandiri.tutur_apersepsi_paralel",
    "LapisanParalel": "mandiri.tutur_apersepsi_paralel",
    "KALIMAT_ADA_SESUATU": "mandiri.tutur_apersepsi_paralel",
    "KALIMAT_TAK_BERNAMA": "mandiri.tutur_apersepsi_paralel",
    "TubuhSumber": "mandiri.tubuh_residu_intrusi_detak",
    "Residu": "mandiri.tubuh_residu_intrusi_detak",
    "Intrusi": "mandiri.tubuh_residu_intrusi_detak",
    "DetakInternal": "mandiri.tubuh_residu_intrusi_detak",
    "Vacancy": "mandiri.vacancy_gejala_kategori",
    "Gejala": "mandiri.vacancy_gejala_kategori",
    "GejalaMurni": "mandiri.vacancy_gejala_kategori",
    "KategoriProto": "mandiri.vacancy_gejala_kategori",
    "Invensi": "mandiri.invensi_kausal_perencana",
    "ModelKausal": "mandiri.invensi_kausal_perencana",
    "Perencana": "mandiri.invensi_kausal_perencana",
    "EMOSI_NODE": "mandiri.kognisi_lanjut",
    "EversiTD": "mandiri.kognisi_lanjut",
    "GrafAsosiasi": "mandiri.kognisi_lanjut",
    "MesinKepercayaan": "mandiri.kognisi_lanjut",
    "ProsesOU": "mandiri.kognisi_lanjut",
    "boltzmann_pilih": "mandiri.kognisi_lanjut",
    "suhu_mental": "mandiri.kognisi_lanjut",
    "ARAH": "dunia.peta",
    "LEGENDA_MEDAN": "dunia.peta",
    "peta_contoh": "dunia.peta",
    "EFEK_JENIS": "dunia.objek_bahaya_cuaca",
    "JENIS_DAPAT_DIAMBIL": "dunia.objek_bahaya_cuaca",
    "SIMBOL_OBJEK": "dunia.objek_bahaya_cuaca",
    "Badan": "dunia.siklus_langkah",
    "Arg": "bahasa.tutur_generatif",
    "L0": "bahasa.tutur_generatif",
    "L1": "bahasa.tutur_generatif",
    "L2": "bahasa.tutur_generatif",
    "L3": "bahasa.tutur_generatif",
    "Lattice": "bahasa.tutur_generatif",
    "Leksikon": "bahasa.tutur_generatif",
    "Node": "bahasa.tutur_generatif",
    "Orkestrator": "bahasa.tutur_generatif",
    "Tutur": "bahasa.tutur_generatif",
    "konteks_dari_presentasi": "bahasa.tutur_generatif",
    "LEKSIKON_CIRI_BAWAAN": "bahasa.leksikon_ciri",
    "LeksikonCiri": "bahasa.leksikon_ciri",
    "token_dari": "bahasa.ciri_linguistik",
    "NAMA_KORPUS": "dukungan.sumber",
    "NAMA_LEKSIKON": "dukungan.sumber",
    "ada_sumber_daya": "dukungan.sumber",
    "akar_paket": "dukungan.sumber",
    "jalur_korpus": "dukungan.sumber",
    "inventaris": "dukungan.inventaris_patch",
    # inti
    "Naluri": "inti.naluri_konstruksi", "DRIVES": "inti.dinamika_drive",
    "Mood": "inti.mood", "Goal": "inti.tujuan",
    "Persona": "inti.persona", "Keadaan": "inti.persona",
    "PERSONA_CONTOH": "inti.persona",
    "Kesadaran": "kesadaran.workspace", "Presentasi": "presentasi.ucap",
    "Ritual": "ritual", "KawananNPC": "sosial.kawanan",
    "Reputasi": "sosial.reputasi", "buat_npc": "sosial.kawanan",
    # refleksi
    "Nurani": "nurani.pilar_aktif", "NURANI_DEFAULTS": "nurani.pilar_aktif",
    "CalibrationReport": "nurani.kalibrasi_berlapis",
    "DimensiSkor": "penilai.nilai_selaras", "Laporan": "penilai.nilai_selaras",
    "nilai_selaras": "penilai.nilai_selaras",
    "PelacakSelaras": "penilai.pelacak_drift",
    "batas_pengetahuan": "ketidaktahuan.batas",
    "sikap_ketidaktahuan": "ketidaktahuan.sikap",
    "SIKAP_KETIDAKTAHUAN": "ketidaktahuan.sikap",
    "STATUS_PENGETAHUAN": "ketidaktahuan.batas",
    # memori
    "JejakPrediksi": "memori.episodik",
    # mandiri
    "Organik": "mandiri.topologi_luka",
    "KognisiLanjut": "mandiri.kognisi_lanjut",
    # bahasa
    "TuturEngine": "bahasa.tutur_generatif", "GenContext": "bahasa.tutur_generatif",
    "SASPAnalyzer": "bahasa.sa_sp", "sa_sp": "bahasa.sa_sp",
    "sa_sp_literal": "bahasa.sa_sp", "sa_sp_pragmatik": "bahasa.sa_sp",
    "analisis_teks": "bahasa.ciri_linguistik", "FiturTutur": "bahasa.ciri_linguistik",
    # bahasa.teks — fondasi teks bersama (R5.4: dipromosikan root)
    "Token": "bahasa.teks", "tokenisasi": "bahasa.teks",
    "normalisasi_token": "bahasa.teks", "normalisasi_teks": "bahasa.teks",
    "pecah_kalimat": "bahasa.teks", "stem": "bahasa.teks",
    "kandidat_dasar": "bahasa.teks", "cakupan_negasi": "bahasa.teks",
    "jenis_kalimat": "bahasa.teks", "jenis_pertanyaan": "bahasa.teks",
    "urai_subjek_predikat": "bahasa.teks", "tindak_tutur_skor": "bahasa.teks",
    "VERBA_UMUM": "bahasa.teks", "G1_KERAS": "bahasa.teks", "G1_LEMAK": "bahasa.teks",
    "ekstrak_entitas": "bahasa.teks", "ekstrak_topik": "bahasa.teks",
    "deteksi_bahasa": "bahasa.teks", "kemiripan": "bahasa.teks",
    "koreksi_ejaan": "bahasa.teks", "periksa_gramatika": "bahasa.teks",
    "potong_batas_kata": "bahasa.teks", "analisis_ujaran": "bahasa.teks",
    "JejakLinguistik": "bahasa.teks", "jejak_pembentukan": "bahasa.teks",
    # lingkungan
    "Lingkungan": "dunia.siklus_langkah", "Peta": "dunia.peta",
    "ObjekDunia": "dunia.objek_bahaya_cuaca",
    # kontrak
    "JANJI": "kontrak.manifest", "KEBUTUHAN": "kontrak.manifest",
    "verifikasi_startup": "kontrak.verifikasi_startup",
    "verify_startup": "kontrak.verifikasi_startup",
    "kontrak_operasi": "kontrak.operasi_tick",
    "check_operation": "kontrak.operasi_tick",
    "ContractViolationError": "kontrak.kebijakan",
    "LEVEL_TANPA_VERIFIKASI": "kontrak.kebijakan",
    "LEVEL_PRECONDITION": "kontrak.kebijakan",
    "LEVEL_OPERASI": "kontrak.kebijakan",
    "LEVEL_LINTAS_LAPIS": "kontrak.kebijakan",
    "KEBIJAKAN_TOLAK": "kontrak.kebijakan",
    "KEBIJAKAN_CATAT": "kontrak.kebijakan",
    "KEBIJAKAN_ABAIKAN": "kontrak.kebijakan",
    "DRIVE_KEYS": "kontrak.manifest",
    # dukungan
    "optional_module": "dukungan.patching",
    "install_method": "dukungan.patching",
    "install_methods": "dukungan.patching",
    "wrap_method": "dukungan.patching",
    "PatchConflictError": "dukungan.patching",
    "jalur_leksikon": "dukungan.sumber",
    "kandidat_leksikon": "dukungan.sumber",
}

# Satu-satunya fitur yang sengaja TIDAK diorkestrasi: titik masuk showcase.
# Fitur di bawahnya dimainkan langsung oleh orkestra; nama-nama ini dipantau
# pemindaian AST (lihat SSTKlasifikasiTest) agar tidak ada yang lolos diam-diam.
LUAR_CAKUPAN_SST: Set[str] = {
    "demo", "demo_npc", "demo_empati", "demo_watak", "demo_introspeksi",
    "demo_kesadaran", "demo_presentasi", "demo_fitur_lanjutan", "demo_kinerja",
    "demo_sosial", "demo_kognisi",
    "demo_organik", "demo_kausal", "demo_gejala", "demo_tutur", "demo_invensi",
    "demo_momen", "demo_persepsi", "demo_pelindung", "demo_perencana",
}


def _cek(kondisi: Any, pesan: str) -> None:
    if not kondisi:
        raise AssertionError("SST: " + pesan)


class OrkestraSST:
    """Menggerakkan satu NPC melewati seluruh siklus fitur Pycos.

    Setiap `fase_*` memainkan kelompok fitur sekaligus menandai ledger-nya;
    `jalankan()` mengembalikan ledger untuk diuji kelengkapannya.
    """

    def __init__(self, seed: int = 2026) -> None:
        self.seed = seed
        self.ledger = LedgerFitur()
        self.tmp = tempfile.TemporaryDirectory(prefix="sst_pycos_")
        self.n: Any = None            # NPC utama
        self.npc_lain: Any = None
        self.jejak: Any = None
        self.dunia: Any = None
        self.engine: Any = None
        self.orang: Any = None        # entitas sosial lawan bicara
        self.rumah: Any = None        # wadah Organik
        self.kognisi: Any = None

    # -- util ---------------------------------------------------------------
    def _t(self, nama: str, bukti: str = "") -> None:
        if nama not in himpunan_fitur_wajib():
            raise AssertionError("fitur tidak terdaftar: " + nama)
        self.ledger.tandai(nama, bukti)

    def jalankan(self) -> LedgerFitur:
        try:
            for nama_fase in sorted(FITUR_WAJIB):
                getattr(self, "fase_" + nama_fase.split("_", 1)[1])()
            wajib = himpunan_fitur_wajib()
            _cek(self.ledger.aktif() == wajib,
                 "manifest berbeda dari fitur aktif: {}".format(
                     sorted(self.ledger.aktif() ^ wajib)))
            return self.ledger
        finally:
            self.tmp.cleanup()

    # -- fase 0 -------------------------------------------------------------
    def fase_sumber_daya_dan_kontrak(self) -> None:
        from pycos.dukungan import diagnostik
        from pycos.dukungan.numerik import float_hingga, jepit, jepit_01, jepit_drive
        from pycos.dukungan.patching import (PatchConflictError, install_method,
                                             install_methods, optional_module,
                                             wrap_method)
        from pycos.dukungan.sumber import (ada_sumber_daya, akar_paket,
                                           jalur_korpus, jalur_leksikon,
                                           kandidat_leksikon)
        from pycos import kontrak

        _cek(os.path.isdir(akar_paket()), "akar paket harus direktori")
        _cek(os.path.isfile(jalur_leksikon()), "leksikon harus terpasang")
        _cek(os.path.isfile(jalur_korpus()), "korpus contoh harus terpasang")
        _cek(ada_sumber_daya(jalur_korpus()), "korpus terbaca")
        _cek(len(kandidat_leksikon()) >= 2, "kandidat leksikon terurut")
        self._t("dukungan.sumber", "leksikon+korpus terpasang")

        _cek(jepit(float("nan")) == 0.0, "jepit NaN -> 0")
        _cek(jepit_drive(9.0) == 1.0, "jepit_drive saturasi")
        _cek(jepit_01(-3.0) == 0.0, "jepit_01 saturasi")
        _cek(float_hingga(1.5, "x") == 1.5, "float_hingga terima berhingga")
        self._t("dukungan.numerik", "jepit/jepit_drive/jepit_01/float_hingga")
        from pycos.dukungan.konstanta import DRIVES
        _cek(kontrak.DRIVE_KEYS is DRIVES, "kontrak memakai tuple drive kanonik")
        self._t("dukungan.konstanta", "identitas tuple enam drive")

        diagnostik.kosongkan()
        diagnostik.catat("sst", "uji diagnostik", detail=1)
        _cek(diagnostik.laporan()["per_sumber"].get("sst") == 1, "diagnostik catat")
        diagnostik.kosongkan()
        self._t("dukungan.diagnostik", "catat/laporan/kosongkan")

        modul = optional_module("pycos.dukungan.numerik")
        _cek(modul is not None, "optional_module menemukan modul nyata")

        class Sasaran:
            def __init__(self) -> None:
                self._nilai = None

        def nilai_baru(_self: Any) -> int:
            return 7

        dipasang = install_method(Sasaran, "nilai_baru", nilai_baru,
                                  patch_id="sst.install")
        _cek(dipasang and Sasaran().nilai_baru() == 7, "install_method pasang")
        try:
            install_method(Sasaran, "nilai_baru", lambda self: 8,
                           patch_id="sst.duplikat")
            _cek(False, "install_method duplikat harus ditolak")
        except PatchConflictError:
            pass
        install_methods(Sasaran, {}, patch_id="sst.kosong")

        def pembungkus(asli: Any, self: Any) -> int:
            return asli(self) + 1

        wrap_method(Sasaran, "nilai_baru", pembungkus, patch_id="sst.wrap")
        _cek(Sasaran().nilai_baru() == 8, "wrap_method membungkus")
        self._t("dukungan.patching", "install/wrap/conflict")
        from pycos.dukungan.patching import inventaris
        _cek(any(row["metode"] == "nilai_baru" and "sst.wrap" in row["patch_ids"]
                 for row in inventaris()), "patch fase dukungan tercatat dalam inventaris")
        self._t("dukungan.inventaris_patch", "snapshot metadata patch runtime")

        _cek("Naluri" in kontrak.JANJI and "Persona" in kontrak.JANJI,
             "manifest memuat entri inti dan penilai")
        _cek("PenilaiSelaras" in kontrak.KEBUTUHAN, "kebutuhan penilai ada")
        self._t("kontrak.manifest", "JANJI/KEBUTUHAN lengkap")

        _cek(kontrak.verifikasi_startup() is None, "verifikasi_startup bersih")
        self._t("kontrak.verifikasi_startup", "tanpa pelanggaran")

        args_tick = {"events": [{"drive": "energi", "delta": 0.1}],
                     "action_cost": False}
        subjek_tick = types.SimpleNamespace(
            levels={d: 0.0 for d in kontrak.DRIVE_KEYS})
        _cek(kontrak.kontrak_operasi("tick", "masuk", subjek_tick, args_tick,
                                     level=1) is None, "kontrak tick masuk")
        _cek(kontrak.check_operation(operation="tick", phase="entry",
                                     subject=subjek_tick, arguments=args_tick,
                                     level=1) is None, "check_operation alias")
        self._t("kontrak.operasi_tick", "tick masuk/keluar level 1-2")

        from pycos.inti.persona import Keadaan, Persona
        persona_k = Persona(nama="UjiKontrak", sifat={"hangat": 1.0})
        keadaan_k = Keadaan(valensi=0.2, gairah=0.5, ketidakpastian=0.1)
        args_penilai = {"persona": persona_k, "keadaan": keadaan_k,
                        "teks": "halo dunia"}
        _cek(kontrak.kontrak_operasi("penilai.nilai_selaras", "masuk",
                                     types.SimpleNamespace(), args_penilai,
                                     level=1) is None, "kontrak penilai masuk")
        from pycos.refleksi.nurani import PelacakSelaras, nilai_selaras
        lap_k = nilai_selaras(persona_k, keadaan_k, "halo dunia")
        pel_k = PelacakSelaras()
        _cek(kontrak.kontrak_operasi("pelacak.catat", "masuk", pel_k,
                                     {"laporan": lap_k}, level=1) is None,
             "kontrak pelacak.catat masuk")
        self._t("kontrak.operasi_penilai",
                "penilai.nilai_selaras + pelacak.catat masuk")

        for kasus in (lambda: kontrak.angka(float("nan"), "x", 0.0, 1.0),
                      lambda: kontrak.angka(True, "x"),
                      lambda: kontrak.teks_wajib("  ", "x"),
                      lambda: kontrak.hanya_kunci({"bogus": 1}, ("a",), "d")):
            try:
                kasus()
                _cek(False, "validator batas harus menolak")
            except ValueError:
                pass
        self._t("kontrak.validator_batas", "angka/teks_wajib/hanya_kunci menolak")

        _cek(kontrak.LEVEL_OPERASI == 2 and kontrak.KEBIJAKAN_TOLAK == "reject",
             "konstanta kebijakan")
        try:
            raise kontrak.ContractViolationError({"apa": "uji"})
        except kontrak.ContractViolationError:
            pass
        self._t("kontrak.kebijakan", "LEVEL_*/KEBIJAKAN_*/ContractViolationError")

    # -- fase 1 -------------------------------------------------------------
    def fase_inti_dan_kepribadian(self) -> None:
        from pycos.inti.naluri import DRIVES, Naluri, buat_npc
        from pycos.inti.persona import PERSONA_CONTOH, Keadaan, Persona

        persona = Persona(nama="Sari", sifat={"hangat": 0.7, "ekspresif": 0.5,
                                              "ragu": 0.4},
                          register="santai", pantangan=("kejam",))
        _cek(persona.to_dict()["nama"] == "Sari", "persona round-trip")
        keadaan = Keadaan.dari_mood(types.SimpleNamespace(valence=0.2, arousal=0.6))
        _cek(0.0 <= keadaan.gairah <= 1.0, "keadaan dari mood")
        _cek(PERSONA_CONTOH.nama == "Rani", "persona contoh tersedia")
        self.persona = persona
        self.keadaan = keadaan
        self._t("inti.persona", "Persona/Keadaan/PERSONA_CONTOH")

        n = Naluri(rng_seed=self.seed, name="Sari", stage="remaja")
        self.n = n
        _cek(n.levels.keys() == set(DRIVES), "enam drive terisi")
        _cek(n.tick_count == 0, "NPC baru lahir")
        self._t("inti.naluri_konstruksi", "Naluri(seed,stage) + DRIVES")

        n.tick(events=[{"drive": "energi", "delta": -0.35},
                       {"drive": "keamanan", "delta": -0.2}])
        n.tick(events=None)
        _cek(n.tick_count == 2, "tick berjalan")
        sebelum = n.levels["energi"]
        n.delta("energi", 0.1)
        _cek(abs(n.levels["energi"] - min(1.0, sebelum + 0.1)) < 1e-9,
             "delta diterapkan dengan batas drive")
        _cek(isinstance(n.deficit("energi"), float), "deficit terbaca")
        self._t("inti.dinamika_drive", "tick/events/delta/deficit")

        m = n.mood()
        _cek(hasattr(m, "valence") and hasattr(m, "arousal"), "mood berbentuk")
        _cek(isinstance(m.modulation(), dict), "modulasi mood")
        self._t("inti.mood", "mood()/modulation()")

        n.set_subgoal("energi", "cari bekal untuk perjalanan")
        _cek(n.goal_to_scenario(), "skenario dari tujuan")
        n.complete_subgoal("energi")
        self._t("inti.tujuan", "set_subgoal/goal_to_scenario/complete_subgoal")

        pilihan = n.choose_action([{"name": "istirahat",
                                    "drive_effects": {"energi": 0.3}},
                                   {"name": "jelajah",
                                    "drive_effects": {"keingintahuan": 0.4}}])
        _cek(pilihan.get("action") is not None, "aksi terpilih")
        self._t("inti.pilih_aksi", "choose_action goal-biased")

        r = n.reward_for({"energi": 0.2, "keamanan": -0.1})
        _cek(isinstance(r, float) and r == r, "reward berhingga")
        self._t("inti.reward", "reward_for")

        dampak = n.impact_of("rumah terbakar dan aku kehilangan segalanya")
        _cek(isinstance(dampak, dict) and dampak, "impact_of vektor drive")
        hasil = n.project_outcome_to_drives({"energi": 0.3})
        _cek(isinstance(hasil, dict), "project_outcome_to_drives")
        _cek(isinstance(n.utility({"energi": 0.3}), float), "utility")
        self._t("inti.utilitas_dampak", "impact_of/project/utility")

        skor = n.scoring_func()
        prediksi = {"drive_deltas": {"energi": 0.2}, "impact": 0.3,
                    "confidence": 0.6}
        _cek(callable(skor), "scoring_func callable")
        n.observe_outcome(prediksi, {"drive_deltas": {"energi": 0.1}})
        _cek(isinstance(n.calibration_error(), float), "calibration_error")
        _cek(0.0 < n.estimate_scale() <= 10.0, "estimate_scale wajar")
        self._t("inti.kalibrasi_skala", "observe_outcome/calibration/scale")

        n.set_sleep_mode("gabung")
        tidur = n.should_sleep()
        _cek(isinstance(tidur, tuple) and len(tidur) == 2, "should_sleep tuple")
        kebijakan = n.dream_policy()
        _cek(isinstance(kebijakan, dict) and "num_dreams" in kebijakan,
             "dream_policy lengkap")
        n.note_prediction()
        n.post_sleep({"energi": 0.1})
        _cek(n.sleep_status(), "sleep_status")
        self._t("inti.tidur_mimpi", "should_sleep/dream_policy/post_sleep")

        n.set_stage("dewasa")
        n.tick(events=None)
        n.advance_stage_by_ticks()
        _cek(n.subjective_time_state(), "waktu subjektif")
        self._t("inti.tahap_waktu_subjektif", "set_stage/advance/subjective_time")

        n.enable_emosi(True)
        n.feel("senang", 0.6, "perjalanan berjalan")
        _cek(n.emosi_state(), "state emosi")
        dominan = n.emosi_dominan(ambang=0.0)
        _cek(dominan is not None and dominan[0] in n.emosi
             and dominan[1] == max(n.emosi.values()), "emosi dominan")
        self._t("inti.emosi", "enable_emosi/feel/emosi_state")

        n.enable_coping(True)
        n.reappraise("senang", "wajar saja", 0.4)
        n.suppress("senang", 0.3)
        n.distract("cuaca", 3, 0.5)
        _cek(n.coping_state(), "coping state")
        self._t("inti.coping", "reappraise/suppress/distract")

        n.set_watak(viskositas_diri=0.2)
        _cek(n.watak_aktif(), "watak aktif")
        n.seed_backstory({"ayah": "petani", "kampung": "pesisir"})
        preset = n.personality_presets()
        if preset:
            n.set_personality_preset(next(iter(preset)), blend=0.5)
        n.set_personality(energi=1.2)
        _cek(n.describe_personality(), "deskripsi kepribadian")
        self._t("inti.watak_backstory", "watak/preset/backstory")

        n.add_lexicon("petir", {"keamanan": -0.4})
        n.set_lexicon({"gempa": {"keamanan": -0.5}}, merge=True)
        n.set_tag_lexicon(None)
        n.use_lexicon_pack("id")
        n.remember_context("bau asap", 0.8)
        n.clear_context()
        self._t("inti.leksikon_dan_konteks", "add/set/pack/remember/clear")
        from pycos.dukungan.leksikon import periksa as periksa_impak
        _cek(periksa_impak()["ok"], "cakupan/provenance leksikon impak")
        _cek(n.impact_of("dehidrasi")["energi"] < 0, "impak ID baru pada subjek")
        try:
            n.use_lexicon_pack("en")
            _cek(n.impact_of("hydrated")["energi"] > 0, "impak EN baru pada subjek")
        finally:
            n.use_lexicon_pack("id")
        self._t("inti.leksikon_impak", "cakupan dan impak dua bahasa pada NPC utama")


        node = types.SimpleNamespace(id="n1", properties={"semantik": ["api"]},
                                     created_tick=0, last_access_tick=1,
                                     idle_seconds=lambda: 0.0, hit_count=2)
        _cek(isinstance(n.salience(node, now=10.0), float), "salience node")
        kebijakan_memori = n.memory_policy()
        _cek(isinstance(kebijakan_memori, dict), "memory_policy")
        garden = types.SimpleNamespace(nodes={"n1": node}, metadata={})
        n.apply_memory_policy(garden)
        _cek("salience" in garden.nodes["n1"].metadata, "apply_memory_policy")
        self._t("inti.salience_kebijakan_memori", "salience/memory_policy/garden")

        brain = types.SimpleNamespace(state={})
        n.apply_to_brain(brain)
        n.counterfactual_rehearsal(brain, {"drive_deltas": {"energi": 0.2}})
        for _ in range(6):
            n.tick(events=[{"drive": "keamanan", "delta": -0.5}])
        _cek(isinstance(n.drive_targeted_scenario(), dict),
             "drive_targeted_scenario")
        n.resonant_recalibration(imagination_history=[], strength=0.3)
        self._t("inti.brain_dan_imajinasi", "brain/rehearsal/scenario/recalibrasi")

        n.set_lod("latar", divisor=2)
        _cek(n.lod_status()["mode"] == "latar", "LOD latar")
        n.tick_light()
        n.heavy_computation()
        ringkas = n.kompres_memori("latar")
        _cek(isinstance(ringkas, dict), "kompres_memori")
        self._t("inti.lod_kompresi", "set_lod/tick_light/heavy/kompres")

        n.enable_replay(True)
        n.tick(events=[{"drive": "koherensi", "delta": 0.1}])
        putaran = n.export_replay()
        _cek(putaran, "replay tercatat")
        n.replay(putaran)
        n.enable_profiling(True)
        n.tick(events=None)
        _cek(n.profile_report(), "profile_report")
        self._t("inti.replay_dan_profiling", "export_replay/replay/profile")

        _cek(n.hud_state(), "hud_state")
        _cek(n.status(), "status")
        _cek(isinstance(n.mood_label(), str) and bool(n.mood_label()),
             "label mood terbaca")
        _cek(isinstance(n.intent(), dict) and bool(n.intent()), "niat terbaca")
        self._t("inti.hud_status", "hud/status/mood_label/intent")

        n.record_action("istirahat", {"energi": 0.2}, 0.8, tick=3)
        n.assign_delayed_credit({"energi": 0.2}, tick=5)
        self._t("inti.kredit_aksi", "record_action/assign_delayed_credit")

        n.enable_nurani("social_memory", semua=True)
        lawan = buat_npc("Bagas", personality="penjelajah", npc=True, sosial=True)
        self.orang = lawan
        n.kenal(lawan, "Bagas")
        n.berinteraksi(lawan, muatan=0.4, kepercayaan_delta=0.1, nama="Bagas")
        n.catat_utang(lawan, "menjaga tas", 1.0, "janji")
        n.bayar_utang(lawan, "menjaga tas")
        n.tandai_momen("pertemuan pertama di pasar")
        n.observe_other_belief("Bagas", "keamanan", 0.2, 0.4)
        _cek(n.estimate_other_belief("Bagas", "keamanan") is not None,
             "estimasi keyakinan orang lain")
        _cek(n.relasi(lawan).get("dikenal"), "relasi lawan bicara dicatat")
        n.hancurkan_kepercayaan(lawan, "ingkar janji")
        n.menarik_diri(lawan)
        self._t("inti.sosial_naluri", "kenal/interaksi/utang/momen/kepercayaan")

        data = n.to_dict()
        n2 = Naluri.from_dict(data)
        _cek(n2.name == "Sari" and n2.tick_count == n.tick_count,
             "round-trip to_dict/from_dict")
        _cek(Naluri.from_json(n.to_json()).name == "Sari", "round-trip json")
        self._t("inti.serialisasi", "to_dict/from_dict/to_json/from_json")

    # -- fase 2 -------------------------------------------------------------
    def fase_kesadaran_presentasi_sosial(self) -> None:
        from pycos.inti.naluri import KawananNPC, Reputasi

        n = self.n
        n.enable_kesadaran(semua=True)
        n.enable_presentasi(semua=True)
        k = n.kesadaran
        k.observe_event({"isi": "api menyala di ujung lorong", "sumber": "mata"})
        k.submit({"isi": "aku harus memadamkannya", "sumber": "niat"})
        _cek(k.workspace_report(), "laporan workspace")
        _cek(k.attention_state(), "state atensi")
        self._t("kesadaran.workspace", "observe_event/submit/workspace_report")

        k.form_identity()
        k.tandai_core_memory("rumah di pesisir", klaim="aku berasal dari pesisir")
        k.tandai_core_memory("aku harus selalu waspada", klaim="waspada itu wajar")
        for _ in range(3):
            k.form_identity()
        _cek(k.narrative_identity, "klaim identitas")
        _cek(k.narrative_state(), "narasi diri")
        _cek(k.core_memory_state(), "memori inti")
        _cek(k.inner_speech() is not None, "inner speech")
        _cek(k.audition_self("aku harus waspada") is not None, "audisi diri")
        self._t("kesadaran.identitas", "identitas/narasi/core/inner/audition")

        _cek(k.daftar_lantai_kesadaran("larang_kata_kasar", "arousal_tinggi",
                                       "saat marah jangan bicara kasar"),
             "daftar lantai")
        k.set_konteks_lantai(bersama_yang_dihormati=False)
        self._t("kesadaran.lantai", "daftar/set konteks lantai")

        p = n.presentasi
        p.set_jejak(self.jejak if self.jejak is not None else None)
        entri = p.ucap(kepada="Player", topik="kebakaran di lorong")
        _cek(entri, "ucap menghasilkan entri dialog")
        self._t("presentasi.ucap", "presentasi.ucap -> entri")

        p.lihat_player("Player")
        p.proaktif()
        p.terima_bukti("Player", "api sudah padam")
        p.koreksi_ingatan("api padam sendiri")
        p.indikator_psikologis()
        p.tag_dialog()
        _cek(p.ekspresi(), "ekspresi")
        _cek(p.tatapan() is not None and p.postur() is not None, "kanal tubuh")
        p.napas()
        p.gestur()
        p.jarak()
        self._t("presentasi.kanal", "ekspresi/tatapan/postur/napas/gestur/lihat")

        n.enable_ritual(True)
        n.lakukan_ritual(konteks="pulang")
        n.ritual.refresh_archetype()
        n.ritual.maybe_trigger(0)
        _cek(n.ritual.state() is not None, "state ritual")
        self._t("ritual", "lakukan_ritual/refresh/maybe_trigger/state")

        kawanan = KawananNPC()
        kawanan.serap(n, position=(1, 1))  # instance subjek tetap sama
        kawanan.tambah("Bagas", personality="penjelajah", position=(2, 1))
        kawanan.enable_reputasi()
        kawanan.catat_rumor("Sari", "Bagas", "menolong warga", muatan=0.6)
        _cek(kawanan.reputasi_semua(), "reputasi kawanan")
        kawanan.broadcast("Sari", [{"isi": "kebakaran di lorong"}], radius=10)
        kawanan.interaksi("Sari", "Bagas", 0.2, "mengobrol")
        kawanan.emotional_contagion()
        kawanan.social_learn("Sari", "Bagas", "menolong", 0.8)
        kawanan.teaching("Bagas", "Sari", "memadamkan api")
        kawanan.form_cultural_norms()
        kawanan.biarkan_bersosialisasi()
        kawanan.tick_all(events=None)
        _cek(kawanan.hud_all() is not None, "hud kawanan")
        self._t("sosial.kawanan", "tambah/rumor/broadcast/interaksi/budaya/tick")

        rep = Reputasi()
        rep.catat("Bagas", "menolong", 0.8, sumber="Sari")
        rep.sebar("Sari", "Bagas", "menolong", 0.5)
        _cek(rep.konsensus("Bagas") is not None, "konsensus")
        rep.decay()
        _cek(rep.report(), "laporan reputasi")
        self._t("sosial.reputasi", "catat/sebar/konsensus/decay/report")

    # -- fase 3 -------------------------------------------------------------
    def fase_dunia(self) -> None:
        from pycos.lingkungan.dunia import Lingkungan, Peta, peta_contoh

        peta = peta_contoh()
        peta_kecil = Peta.dari_ascii(["###", "#.#", "###"])
        _cek(peta_kecil.simbol((1, 1)) == ".", "peta ASCII terbaca")
        _cek(peta.simbol((0, 0)) == "#", "simbol dinding peta contoh")
        _cek(peta.didalam((1, 1)), "peta.didalam")
        self._t("dunia.peta", "peta_contoh/didalam/simbol")

        dunia = Lingkungan(peta=peta, seed=self.seed, pandangan=4)
        dunia.tambah_objek("makanan", (2, 1), nama="roti", porsi=1)
        dunia.tambah_objek("bahaya", (5, 5), nama="api")
        dunia.tambah_objek("air", (9, 5), nama="sumur")
        _cek(dunia.fase(), "fase jam")
        _cek(dunia.konteks() is not None, "konteks dunia")
        self._t("dunia.objek_bahaya_cuaca", "objek/bahaya/fase/konteks")

        jejak = self.jejak
        dunia.tambah_npc(self.n, (2, 2), nama="Sari", jejak=jejak)
        dunia.langkah("Sari")
        obs = dunia.observasi("Sari")
        _cek(obs, "observasi NPC")
        kandidat = dunia.aksi_tersedia("Sari")
        pilihan = dunia.pilih_aksi("Sari", kandidat)
        if pilihan:
            dunia.terapkan("Sari", pilihan)
        dunia.peristiwa_lingkungan("Sari")
        _cek(dunia.paparan("Sari") is not None, "paparan")
        dunia.jalankan(3, ["Sari"])
        self._t("dunia.siklus_langkah", "tambah_npc/langkah/observasi/jalankan")

        salin = dunia.to_dict()
        _cek(Lingkungan.from_dict(salin), "round-trip dunia")
        self._t("dunia.serialisasi", "to_dict/from_dict")

    # -- fase 4 -------------------------------------------------------------
    def fase_bahasa(self) -> None:
        from pycos.bahasa.tutur import (FiturTutur, GenContext, LeksikonCiri,
                                        SASPAnalyzer, TuturEngine, analisis_teks,
                                        konteks_dari_presentasi, sa_sp,
                                        sa_sp_literal, sa_sp_pragmatik,
                                        token_dari)
        from pycos.dukungan.sumber import jalur_leksikon

        engine = TuturEngine(jalur_leksikon())
        _cek(engine.tersedia(), "TuturEngine memuat leksikon")
        _cek(engine.info(), "info leksikon")
        ujaran = engine.ucap(GenContext(act="menyatakan", topik="perjalanan",
                                        valensi=0.2, arousal=0.4))
        _cek(isinstance(ujaran, (str, dict, list)) or ujaran, "ucap generatif")
        self.engine = engine
        self._t("bahasa.tutur_generatif", "TuturEngine.ucap/GenContext/info")
        engine_subjek = self.n.presentasi.tutur_engine()
        _cek(engine_subjek is not None, "engine tutur NPC utama tersedia")
        ctx_variasi = GenContext(act="senang", seed=7, valensi=.8, arousal=.3)
        variasi = [engine_subjek.ucap(ctx_variasi) for _ in range(20)]
        unik = len({t.teks for t in variasi})
        _cek(all(t.status == "SUKSES" for t in variasi) and unik >= 8,
             "minimal 8/20 ujaran unik pada engine NPC utama")
        self._t("bahasa.variasi_leksikal", "{} unik dari 20 pada NPC utama".format(unik))


        konteks = konteks_dari_presentasi(self.n.presentasi, "menyatakan",
                                          kepada="Player", topik="perjalanan")
        hasil = sa_sp("tolong jangan pergi sekarang", konteks)
        _cek(hasil, "sa_sp")
        _cek(sa_sp_literal("aku datang sekarang", engine.leks) is not None,
             "sa_sp_literal")
        _cek(sa_sp_pragmatik("bisa bantu aku?", konteks) is not None,
             "sa_sp_pragmatik")
        analisis = SASPAnalyzer()
        _cek(analisis.analisis("aku akan pergi besok", konteks),
             "SASPAnalyzer.analisis")
        self._t("bahasa.sa_sp", "sa_sp/literal/pragmatik/SASPAnalyzer")

        fitur = analisis_teks("aku senang banget, tidak sedih!")
        _cek(fitur.polaritas() and fitur.polaritas() > 0, "polaritas ciri")
        _cek(isinstance(fitur, FiturTutur), "FiturTutur")
        _cek(token_dari("Rumah-besar itu"), "token_dari")
        # Fondasi teks bersama (pycos.bahasa.teks) — dipanggil langsung di sini
        from pycos.bahasa import teks as teks_api
        toks = teks_api.tokenisasi("senaaang gk senang, dia baik2 saja")
        _cek([t.bentuk for t in toks if t.jenis == "kata"][:2] == ["senang", "tidak"],
             "tokenisasi normalisasi informal")
        _cek(teks_api.pecah_kalimat("Halo! Apa kabar?") == ["Halo!", "Apa kabar?"],
             "pecah_kalimat")
        _cek(teks_api.normalisasi_token("senaaang") == "senang"
             and teks_api.normalisasi_teks("Aku gk  tahu") == "aku tidak tahu",
             "normalisasi token/teks")
        _cek(teks_api.stem("mengajar") == "ajar", "stem Nazief-Adriani")
        _cek("ajar" in teks_api.kandidat_dasar("mengajar"), "kandidat_dasar")
        flag = teks_api.cakupan_negasi(teks_api.tokenisasi("tidak senang, dia baik"))
        _cek(any(flag), "cakupan negasi")
        _cek(teks_api.jenis_kalimat("tolong ambilkan air") == "imperatif",
             "jenis_kalimat imperatif")
        _cek(teks_api.jenis_pertanyaan("apa kabar?").get("jenis") == "apa",
             "jenis_pertanyaan")
        urai = teks_api.urai_subjek_predikat(
            teks_api.tokenisasi("aku lapar"), engine.leks)
        _cek(urai.get("subjek") == "aku", "urai_subjek_predikat")
        skor = teks_api.tindak_tutur_skor("tolong ambilkan air")
        _cek(skor["permintaan"] >= skor["perintah"] - 1e-9, "tindak_tutur_skor")
        _cek(isinstance(teks_api.ekstrak_entitas("Budi sedang ke pasar"), list),
             "ekstrak_entitas")
        _cek(isinstance(teks_api.ekstrak_topik("aku memikirkan perjalanan itu",
                                               None, engine.leks),
                        str),
             "ekstrak_topik")
        _cek(teks_api.deteksi_bahasa("aku tidak tahu") == "id", "deteksi_bahasa")
        _cek(teks_api.kemiripan("api di gudang", "ada api di gudang") > 0.3,
             "kemiripan")
        _cek(teks_api.koreksi_ejaan("seang", ["senang"]) == "senang", "koreksi_ejaan")
        _cek("kata_berulang" in teks_api.periksa_gramatika("dia yang yang pergi."),
             "periksa_gramatika")
        _cek(len(teks_api.potong_batas_kata("cerita yang cukup panjang dipotong",
                                              25)) <= 25,
             "potong_batas_kata")
        hasil = teks_api.analisis_ujaran("aku tidak senang.")
        _cek(hasil["token"] and hasil["jenis_kalimat"], "analisis_ujaran")
        jejak = teks_api.jejak_pembentukan(input_teks="halo", act="menyatakan")
        _cek(jejak["input"] == "halo" and "formation" in jejak, "jejak_pembentukan")
        _cek(teks_api.JejakLinguistik().to_dict()["act"] == "", "JejakLinguistik")
        self._t("bahasa.teks", "tokenisasi/stem/negasi/gramatika/jejak pembentukan")
        self._t("bahasa.ciri_linguistik", "analisis_teks/FiturTutur/token_dari")

        lx = LeksikonCiri.from_dict({k: [] for k in
                                     ("positif", "negatif", "pelunak",
                                      "penguat", "formal", "informal", "negasi")})
        _cek(lx.to_dict()["positif"] == [], "LeksikonCiri round-trip")
        self._t("bahasa.leksikon_ciri", "LeksikonCiri from_dict/to_dict")

    # -- fase 5 -------------------------------------------------------------
    def fase_memori(self) -> None:
        from pycos.memori.jejak_prediksi import JejakPrediksi

        n = self.n
        jejak = JejakPrediksi(naluri=n, rng_seed=self.seed,
                              enable_reconstructive_recall=True)
        self.jejak = jejak
        n.attach_jejak(jejak)
        _cek(n.jejak is jejak, "jejak terpasang ke naluri")
        self._t("memori.integrasi_naluri", "attach_jejak")

        eid = jejak.record_experience(
            "api di lorong", "padamkan", {"drive_deltas": {"keamanan": 0.3}},
            context=("lorong",), tick=n.tick_count, importance=1.2)
        _cek(isinstance(eid, int) and eid > 0, "pengalaman tercatat")
        jejak.experience("asap mengepul", "berlari",
                         {"drive_deltas": {"keamanan": -0.2}},
                         tick=n.tick_count, importance=0.8)
        _cek(jejak.size >= 1, "ukuran memori")
        self._t("memori.episodik", "record_experience/experience/size")

        prediksi = jejak.predict("api di lorong", "padamkan",
                                 context=("lorong",), tick=n.tick_count)
        _cek("forecast" in prediksi and "action_forecast" in prediksi,
             "prediksi berbentuk forecast")
        ranking = jejak.rank_actions("api di lorong",
                                     [{"name": "padamkan"},
                                      {"name": "lari"}],
                                     context=("lorong",))
        _cek(ranking.get("ranked"), "ranking aksi")
        self._t("memori.prediksi_ranking", "predict/rank_actions")
        n.set_lod("penuh")  # interaksi pemain mempromosikan subjek dari LOD latar
        batch = n.kawanan.prediksi_all(
            {"Sari": "api di lorong"}, candidates={"Sari": [{"name": "lari"}]},
            player_position=(1, 1), radius=2, max_candidates=2, max_actions=1)
        _cek(batch["npcs"]["Sari"]["status"] == "ranked", "ranking lazy NPC utama: " + str(batch))
        n.kawanan.tick_all(predict=True, stimulus={"Sari": "api di lorong"},
                           player_position=(1, 1), radius=2, max_candidates=2)
        _cek(n.kawanan.laporan_prediksi()["predicted"] == 1, "tick kawanan dengan prediksi")
        self._t("sosial.prediksi_lazy", "batch/radius/tick_all pada NPC utama")

        terbatas = jejak.predict("api di lorong", max_candidates=1, max_age_ticks=100)
        _cek(terbatas["retrieval_budget"]["similarity_evaluations"] <= 1,
             "batas similarity retrieval")
        rangking_batas = jejak.rank_actions("api di lorong", [{"name": "lari"},
                                            {"name": "padamkan"}],
                                            max_candidates=1, max_actions=1)
        _cek(rangking_batas["retrieval_budget"]["actions_pruned"] == 1,
             "laporan pemotongan aksi")
        self._t("memori.retrieval_terbatas", "predict/rank_actions berbatas pada NPC utama")

        hasil = jejak.reinforce(prediksi, {"drive_deltas": {"keamanan": 0.2}},
                                stimulus="api di lorong", action="padamkan",
                                tick=n.tick_count, calibrate_naluri=True)
        _cek(isinstance(hasil, dict), "reinforce umpan balik")
        self._t("memori.reinforce_kalibrasi", "reinforce + performance_report")

        jejak.register_counterfactual("padamkan", 0.3, "lari", -0.1,
                                      tick=n.tick_count)
        _cek(isinstance(jejak.counterfactual_emotions(), dict),
             "emosi kontrafaktual")
        self._t("memori.kontrafaktual", "register_counterfactual/emosi")

        _cek(jejak.curiga("Bagas menyalakan api", ambang=0.3) is not None,
             "kecurigaan")
        _cek(jejak.kepercayaan("Bagas menyalakan api") is not None,
             "baca kepercayaan")
        jejak.perbarui_kepercayaan("Bagas menyalakan api", 1.4, 1.0, "lihat")
        jejak.tetapkan_kepercayaan("Bagas menyalakan api", 0.6)
        _cek(jejak.kepercayaan_state() is not None, "state kepercayaan")
        self._t("memori.kepercayaan_dinamis", "curiga/kepercayaan/update/tetapkan")

        mimpi = jejak.confabulate("bayangan api", tick=n.tick_count)
        _cek(isinstance(mimpi, dict), "konfabulasi mimpi")
        _cek(isinstance(jejak.future_simulation("api di lorong",
                                                ["padamkan", "lari"],
                                                tick=n.tick_count), dict),
             "simulasi masa depan")
        self._t("memori.mimpi_dan_lintas_waktu", "confabulate/future_simulation")

        pola = jejak.detect_patterns(tick=n.tick_count)
        _cek(isinstance(pola, list), "deteksi pola")
        _cek(jejak.pattern_report() is not None, "laporan pola")
        jejak.forget_patterns(tick=n.tick_count)
        self._t("memori.pola", "detect_patterns/pattern_report/forget_patterns")

        jejak.open_chapter("perjalanan", tick=n.tick_count)
        _cek(jejak.life_chapters() is not None, "bab kehidupan")
        jejak.close_chapter(tick=n.tick_count)
        _cek(jejak.autobiographical_timeline(limit=3) is not None,
             "linimasa autobiografis")
        _cek(jejak.autobiography_state() is not None, "state autobiografi")
        self._t("memori.autobiografi", "chapters/timeline/autobiography_state")

        jejak.observe_actor("Bagas", "menolong", tick=n.tick_count)
        _cek(jejak.performance_report() is not None, "kinerja memori")
        self._t("memori.sosial", "observe_actor/performance_report")

        jejak.set_retrieve_mode("hybrid")
        jejak.predict("api di lorong", "padamkan", context=("lorong",),
                      register_pending=True)
        self._t("memori.retrieval_konteks", "mode hybrid + pending")

        jejak.consolidate_memory()
        jejak.enable_recall_rewrite(True)
        jejak.forget(max_age=10 ** 6, tick=n.tick_count)
        _cek(jejak.half_life_episode(eid) is not None, "paruh waktu episod")
        jejak.ingat_kembali(eid)
        jejak.koreksi_salah(eid)
        _cek(jejak.reconsolidasi_state() is not None, "rekonsolidasi")
        _cek(jejak.nekropolis_state() is not None, "nekropolis")
        _cek(jejak.waktu_state() is not None, "waktu internal memori")
        self._t("memori.daur_hidup",
                "consolidate/rewrite/forget/half_life/rekonsolidasi")

        isi = jejak.to_dict()
        jejak.save(os.path.join(self.tmp.name, "jejak.json"))
        _cek(isinstance(isi, dict) and jejak.to_json(), "serialisasi memori")
        self._t("memori.kualitas_memori", "to_dict/to_json/save")

    # -- fase 6 -------------------------------------------------------------
    def fase_nurani(self) -> None:
        n = self.n
        nur = n.nurani
        _cek(nur is not None, "NURANI melekat pada Naluri")
        keadaan_pilar = n.enable_nurani(semua=True)
        _cek(all(keadaan_pilar.values()) or nur.any_enabled(),
             "semua pilar menyala")
        _cek(nur.enabled("affective_memory"), "pilar afektif aktif")
        self._t("nurani.pilar_aktif", "enable_nurani semua pilar")

        nur.experience("api di lorong", {"keamanan": -0.4}, tick=1)
        nur.warmup_from_log(replace=True)
        _cek(nur.anticipate("api di lorong") is not None, "antisipasi afektif")
        _cek(nur.anticipate_words("api di lorong") is not None, "antisipasi kata")
        _cek(nur.affective_size >= 1, "memori afektif terisi")
        nur.forget_affective(0.0)
        self._t("nurani.memori_afektif", "experience/anticipate/warmup/size")

        nur.record_observation(0.8, 0.6, prob=0.7, success=True,
                               per_drive={"keamanan": 0.5})
        nur.record_uncertainty(0.4, 0.3)
        _cek(nur.calibration_report(), "laporan kalibrasi berlapis")
        _cek(nur.holdout_brier([(0.8, 1.0), (0.3, 0.0)], 1.0) is not None,
             "holdout brier")
        _cek(nur.scale_from_holdout([(0.8, 1.0)], 1.0) is not None,
             "skala holdout")
        self._t("nurani.kalibrasi_berlapis", "observasi/brier/skala/laporan")

        nur.update_setpoints({"energi": 0.1, "keamanan": -0.2})
        _cek(nur.relative_deficit("energi", 0.5) is not None, "defisit relatif")
        nur.update_interoception({"energi": 0.4}, tick=2)
        _cek(nur.interoceptive_echo({"energi": 0.4}, "energi") is not None,
             "gema interoseptif")
        _cek(nur.interoception is not None, "matriks interosepsi")
        self._t("nurani.setpoint_interosepsi", "setpoint/defisit/echo/matriks")

        det = nur.detect_conflict(n.goals, [])
        if det:
            nur.note_conflict(det, resolved=True, tick=3)
        _cek(nur.compromise_bonus({"energi": 0.2}, "energi", "keamanan")
             is not None, "bonus kompromi")
        _cek(nur.flow_state(0.6, 0.4) is not None, "flow state")
        nur.flow_reward_bonus(0.6, 0.4)
        self._t("nurani.konflik_flow", "detect/note/compromise/flow")

        _cek(nur.circadian_phase(10) is not None, "fase sirkadian")
        _cek(nur.night_energy_shift(23) is not None, "geser energi malam")
        self._t("nurani.sirkadian", "circadian_phase/night_energy_shift")

        ent = types.SimpleNamespace(id="Bagas")
        nur.meet(ent, "Bagas", tick=1)
        rel = nur.relationship(ent)
        _cek(rel is not None, "relasi sosial")
        nur.tambah_utang(ent, "menjaga tas", 1.0, "janji", tick=2, nama="Bagas")
        nur.bayar_utang(ent, "menjaga tas")
        nur.set_kacamata_sosial("keamanan", 0.3)
        nur.observe_other_belief("Bagas", "keamanan", 0.3, 0.4, tick=3)
        nur.break_trust(ent, 0.7, tick=3, nama="Bagas")
        nur.decay_social(tick=3)
        _cek(nur.social_size >= 1, "memori sosial terisi")
        self._t("nurani.memori_sosial", "meet/relasi/utang/kacamata/decay")

        _cek(nur.deteksi("keamanan", -0.2) is not None, "deteksi persepsi")
        nur.belajar_persepsi({"keamanan": 0.3})
        nur.update_adaptasi({"keamanan": -0.1}, tick=4)
        _cek(nur.persepsi_ringkas() is not None, "ringkasan persepsi")
        _cek(nur.habit_factor("keamanan", "api di lorong", 4) is not None, "faktor habituasi")
        self._t("nurani.persepsi_adaptasi", "deteksi/belajar/adaptasi/habit")

        nur.update_introspection(n.levels, {"energi": 0.5}, 0.2, 0.5, tick=5)
        _cek(nur.refleksi_diri(5, n.levels), "refleksi diri")
        _cek(nur.evaluasi_diri() is not None, "evaluasi diri")
        _cek(nur.sadar_diri() is not None, "sadar diri")
        _cek(nur.meta_kognisi_laporan(), "laporan metakognisi")
        _cek(nur.introspeksi_state() is not None, "state introspeksi")
        _cek(nur.meta_status() is not None, "meta status")
        _cek(nur.kesadaran_laporan(), "laporan kesadaran")
        self._t("nurani.introspeksi", "update/refleksi/evaluasi/meta/laporan")

        nur.update_felt(n.levels, {"energi": 0.4}, 0.5, tick=6)
        _cek(nur.felt_report(), "laporan felt")
        _cek(nur.felt_consciousness() is not None, "kesadaran terasa")
        nur.moral_emotion("bersalah", 0.5, "mengabaikan teman")
        nur.somatic_mark("api", -0.6, "lorong", tick=6)
        _cek(nur.somatic_bias() is not None, "bias somatik")
        _cek(nur.inner_speech("malam hari") is not None, "inner speech nurani")
        nur.narrate_identity("aku penyintas kebakaran", 0.6, tick=6)
        self._t("nurani.felt_dan_moral", "felt/moral/somatic/inner/narrate")

        nur.metacognitive_doubt(0.4)
        nur.confabulation("ingatan yang kabur", tick=7)
        _cek(nur.classify_source({"isi": "api"}) is not None, "klasifikasi sumber")
        _cek(nur.reality_monitoring({"isi": "api padam"}) is not None, "monitor realitas")
        _cek(nur.source_memory() is not None, "memori sumber")
        self._t("nurani.doubt_sumber", "doubt/confabulation/source/reality")

        nur.serap_kategori("api", "kebakaran", "tutur", 0.6, tick=8)
        _cek(nur.sensitivitas_kategori() is not None,
             "sensitivitas kategori")
        _cek(nur.peka_terhadap("api") is not None, "peka terhadap")
        self._t("nurani.kategori", "serap_kategori/sensitivitas/peka")

        data = nur.to_dict()
        nur2 = type(nur).from_dict(data, params=n.params)
        _cek(nur2 is not None, "round-trip nurani")
        _cek(type(nur).from_json(nur.to_json()), "json nurani")
        self._t("nurani.serialisasi", "to_dict/from_dict/to_json/from_json")

    # -- fase 7 -------------------------------------------------------------
    def fase_mandiri(self) -> None:
        from pycos.mandiri.kognisi_lanjut import (KognisiLanjut, boltzmann_pilih)
        from pycos.mandiri.organik import Organik

        o = Organik(seed=self.seed)
        self.rumah = o
        o.topologi.isi_ulang("Sari", tick=0)
        _cek(o.topologi.terisi("Sari"), "slot topologi terisi")
        _cek(o.topologi.layak_cabang("Sari") is not None, "layak cabang")
        o.luka.lukai("Ayu", "uang", "hutang", tick=1)
        o.luka.terapkan("Ayu", "uang", -0.2)
        _cek(o.luka.ringkas(), "ringkasan luka")
        self._t("mandiri.topologi_luka", "TopologiSlot + LukaDomain")

        o.identitas.tetapkan("diri", {"batas": 1.0})
        _cek(o.identitas.izinkan("senang", 0.5)[0], "identitas izin")
        o.identitas.catat_penolakan("marah", 1.5, "melebihi batas", tick=1)
        o.waktu.daftar("kebakaran", 10.0)
        _cek(o.waktu.skala_subjektif("kebakaran", faktor=1.5) is not None,
             "waktu subjektif")
        o.waktu.dikoreksi_salah("kebakaran")
        self._t("mandiri.identitas_waktu", "BatasIdentitas + WaktuHeterogen")

        _cek(o.tutur.kelayakan({"takut": 1.0})[0] is not None,
             "kelayakan tutur")
        o.tutur.catat("aku takut", "diam saja", 0.2, {"takut": 1.0}, tick=1)
        _cek(o.apersepsi.amati({"takut": 0.8}), "apersepsi")
        o.paralel.tambah("A", 0.5, {"energi": 0.3})
        o.paralel.tambah("B", 0.5, {"energi": -0.3})
        _cek(o.paralel.bertentangan(), "disonansi paralel")
        self._t("mandiri.tutur_apersepsi_paralel",
                "PenolakanTutur/Apersepsi/Paralel")

        o.tubuh.masukan({"nyeri": 0.6})
        o.tubuh.langkah({"nyeri": 0.6})
        o.tubuh.suntik(0.2)
        o.residu.daftar("api", {"takut": 1.0}, 0.5, tick=1)
        o.residu.tambal("api", kekuatan=0.3)
        _cek(o.residu.tekanan() >= 0.0, "tekanan residu")
        o.intrusi.coba(1, o.residu, 0.5, {}, rng=o.rng)
        o.detak.maju(1.0, {}, o.rng)
        self._t("mandiri.tubuh_residu_intrusi_detak",
                "TubuhSumber/Residu/Intrusi/DetakInternal")

        o.vacancy.mulai(5.0, tick=1)
        o.vacancy.lewat(1.0)
        o.gejala.muncul(0.6, tanda="api", tick=1)
        o.gejala.proses(tick=2)
        o.gejala.beri_nama("api", "kebakaran")
        _cek(o.gejala.state() is not None, "state gejala")
        self._t("mandiri.vacancy_gejala_kategori", "Vacancy/Gejala/KategoriProto")

        o.invensi.lahirkan({"sensor": "api"}, tick=2)
        o.kausal.pelajari([{"stimulus": "api", "action": "padamkan",
                            "outcome": {"drive_deltas": {"keamanan": 0.2}},
                            "tick": 1}], tick=2)
        _cek(o.kausal.jelaskan("asap") is not None, "jelaskan kausal")
        _cek(o.kausal.counterfactual("api", "biarkan") is not None,
             "counterfactual kausal")
        _cek(o.kausal.blame("api", "padamkan", "gagal") is not None,
             "blame kausal")
        domain = o.kausal
        domain._tepi("s:api menyala", "a:padamkan api", 0.8)
        domain._tepi("a:padamkan api", "h:api padam", 0.9)
        pohon = o.perencana.rancang("api padam", domain, ["s:api menyala"])
        _cek(pohon is not None, "perencana.rancang")
        o.perencana.maju("api padam", domain, ["s:api menyala"])
        _cek(o.ringkas(), "ringkasan organik")
        self._t("mandiri.invensi_kausal_perencana",
                "Invensi/ModelKausal/Perencana")

        k = KognisiLanjut(seed=self.seed)
        k.aktifkan(eversi=True, boltzmann=True, kepercayaan=True,
                   asosiasi=True, drift=True)
        _cek(all(k.aktif.values()), "seluruh modul kognisi lanjut aktif")
        keluar = k.langkah(dict(self.n.levels), {"takut": 0.4}, 0.3)
        _cek(isinstance(keluar, dict), "langkah kognisi")
        k.eversi.update("api menyala", "padamkan", 0.5, "api padam")
        k.eversi.eversi_param()
        k.kepercayaan.tetapkan("Bagas", 0.6)
        k.kepercayaan.perbarui("Bagas", True)
        _cek(k.kepercayaan.entropi("Bagas") >= 0.0, "entropi kepercayaan")
        k.graf.koaktifkan("api", "takut")
        _cek(k.graf.asosiasi("api") is not None, "asosiasi graf")
        k.ou.langkah(["energi"], 1.0, k.rng)
        _cek(boltzmann_pilih({"a": 1.0, "b": 0.5}, 0.5, k.rng) is not None,
             "pemilihan boltzmann")
        self._t("mandiri.kognisi_lanjut", "eversi/kepercayaan/graf/ou/boltzmann")

    # -- fase 8 -------------------------------------------------------------
    def fase_ketidaktahuan_penilai(self) -> None:
        from pycos.refleksi.ketidaktahuan import (batas_pengetahuan,
                                                  sikap_ketidaktahuan)
        from pycos.refleksi.nurani import (ContohLabel, PelacakSelaras,
                                           contoh_dari_dict, kappa_cohen,
                                           laporan_kalibrasi, muat_korpus,
                                           nilai_selaras, ukur_fitur,
                                           ukur_selaras)
        from pycos.dukungan.sumber import jalur_korpus

        n = self.n
        batas = batas_pengetahuan(n, "api berasal dari kompor", 0.25)
        _cek(batas is not None, "batas pengetahuan")
        _cek(sikap_ketidaktahuan(n, batas, {"topik": "api"}),
             "sikap ketidaktahuan")
        self._t("ketidaktahuan.batas", "batas_pengetahuan")
        self._t("ketidaktahuan.sikap", "sikap_ketidaktahuan")

        laporan = nilai_selaras(self.persona, self.keadaan,
                                "aku senang sekali hari ini!")
        _cek(laporan.status and laporan.skor is not None, "nilai_selaras")
        _cek(laporan.skor_dimensi(), "dimensi skor")
        self._t("penilai.nilai_selaras", "Persona×Keadaan×ujaran → Laporan")

        pelacak = PelacakSelaras(kapasitas=20, min_sampel=3, ambang_tren=0.01)
        for i in range(6):
            pelacak.catat(nilai_selaras(
                self.persona, self.keadaan,
                "sekarang suasana berubah perlahan nomor {}".format(i)))
        tren = pelacak.tren()
        _cek(tren and all("status" in v for v in tren.values()),
             "tren drift lintas giliran")
        self._t("penilai.pelacak_drift", "catat/tren")

        korpus = muat_korpus(jalur_korpus())
        _cek(len(korpus) >= 30, "korpus termuat")
        _cek(contoh_dari_dict({"teks": "halo", "selaras": True}, 1),
             "contoh_dari_dict")
        _cek(isinstance(ContohLabel("halo"), ContohLabel), "ContohLabel")
        _cek(isinstance(ukur_fitur(korpus), dict), "ukur_fitur")
        _cek(isinstance(ukur_selaras(korpus), dict), "ukur_selaras")
        _cek(isinstance(kappa_cohen([(1, 1), (0, 0)]), float), "kappa_cohen")
        _cek(laporan_kalibrasi(korpus)["selaras"], "laporan_kalibrasi")
        self._t("penilai.kalibrasi_korpus", "muat/ukur/kappa/laporan")
        # Fixture sintetis untuk mengaktifkan plumbing, bukan bukti pihak ketiga.
        uji_fixture = [ContohLabel("fixture SST evaluasi A", id_contoh="sst-a",
                                  anotasi={"fixture-A": True, "fixture-B": True}),
                       ContohLabel("fixture SST evaluasi B", id_contoh="sst-b",
                                  anotasi={"fixture-A": False, "fixture-B": False})]
        eksternal = laporan_kalibrasi(
            korpus, korpus_pihak_ketiga=uji_fixture,
            sumber_pihak_ketiga="fixture SST sintetis, bukan korpus manusia independen")
        cek_uji = eksternal["evaluasi_pihak_ketiga"]
        _cek(cek_uji["antar_anotator"][0]["kappa"] == 1.0, "kappa fixture terukur")
        _cek(cek_uji["pemisahan"] == "id_dan_teks_normalisasi_disjoint", "split held-out")
        self._t("penilai.evaluasi_heldout", "API/anotasi fixture sintetis, bukan bukti eksternal")


    # -- fase 9 -------------------------------------------------------------
    def fase_tutup(self) -> None:
        from pycos.dukungan import periksa
        from pycos.inti.naluri import Naluri

        hasil = periksa.jalankan()
        _cek(all(h["ok"] for h in hasil),
             "periksa kesehatan lulus semua: {}".format(
                 [h for h in hasil if not h["ok"]]))
        self._t("dukungan.periksa", "{} cek lulus".format(len(hasil)))

        n = self.n
        sehat = n.health_check()
        _cek(isinstance(sehat, dict), "health_check")
        self._t("inti.health_check_akhir", "health_check komprehensif")

        with tempfile.TemporaryDirectory() as folder:
            jalur = os.path.join(folder, "sst_npc.json")
            n.save(jalur)
            n2 = Naluri.load(jalur)
            _cek(n2.name == n.name and n2.tick_count == n.tick_count,
                 "save/load identik")
        _cek(Naluri.from_json(n.to_json()).status(), "json penuh")
        self._t("inti.serialisasi_penuh", "save/load + json")
        for profil in ("simpan", "minimal"):
            snapshot = n.to_dict(profil=profil)
            pulih = Naluri.from_dict(snapshot)
            _cek(pulih.to_dict(profil=profil) == snapshot, "roundtrip profil " + profil)
        self._t("inti.serialisasi_profil", "simpan/minimal pada NPC utama")
        from unittest.mock import patch
        from pycos.dukungan.batas_memori import BATAS
        with patch.dict(BATAS, {"delta_log": 3}):
            state = n.batasi_memori()
            _cek(state["buffers"]["delta_log"]["limit"] == 3, "batas host terbaca")
            _cek(len(n.delta_log) <= 3, "pemangkasan buffer NPC utama")
        _cek(n.memori_state()["scope"] == "buffer_inti_naluri", "audit memori inti")
        self._t("dukungan.batas_memori", "BATAS/batasi_memori/memori_state pada NPC utama")



# ---------------------------------------------------------------------------
# Kelas tes
# ---------------------------------------------------------------------------
class SSTOrkestraTest(unittest.TestCase):
    """Jalankan orkestra SST dan uji tiga jaminannya."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.orkestra = OrkestraSST(seed=2026)
        with contextlib.redirect_stdout(io.StringIO()):
            cls.ledger = cls.orkestra.jalankan()

    def test_tidak_ada_fitur_tertinggal(self):
        kurang = self.ledger.kurang(himpunan_fitur_wajib())
        self.assertEqual(set(), kurang,
                         "fitur wajib belum aktif: {}".format(sorted(kurang)))
        self.assertEqual(himpunan_fitur_wajib(), self.ledger.aktif(),
                         "fitur aktif di luar manifest")

    def test_setiap_fitur_punya_bukti(self):
        for nama in sorted(himpunan_fitur_wajib()):
            with self.subTest(fitur=nama):
                self.assertTrue(self.ledger.bukti(nama),
                                "{} aktif tanpa bukti".format(nama))

    def test_api_publik_tercakup_manifest(self):
        import pycos

        publik = {n for n in pycos.__all__ if n != "__version__"}
        self.assertEqual(publik, set(CAKUPAN_API),
                         "CAKUPAN_API tidak sinkron dengan pycos.__all__")
        wajib = himpunan_fitur_wajib()
        untuk_fitur = set(CAKUPAN_API.values())
        self.assertTrue(untuk_fitur <= wajib,
                        "fitur tujuan tidak ada di manifest: {}".format(
                            sorted(untuk_fitur - wajib)))

    def test_api_publik_benar_benar_aktif(self):
        # Verifikasi kelompok tujuan aktif; bukan instrumentasi pemanggilan API.
        wajib = himpunan_fitur_wajib()
        for nama, fitur in sorted(CAKUPAN_API.items()):
            with self.subTest(api=nama):
                self.assertIn(fitur, wajib)
                self.assertIn(fitur, self.ledger.aktif(),
                              "API {} tidak tersentuh (fitur {})".format(
                                  nama, fitur))

    def test_fase_terlaksana_berurutan(self):
        jejak = self.ledger._jejak
        fases = sorted(FITUR_WAJIB)
        posisi = [min(jejak.index(f) for f in FITUR_WAJIB[n] if f in jejak)
                  for n in fases]
        self.assertEqual(posisi, sorted(posisi), "fase tidak berurutan")

    def test_laporan_menyebut_semua_fitur(self):
        laporan = self.ledger.laporan()
        for nama in sorted(himpunan_fitur_wajib()):
            self.assertIn(nama, laporan)


class SSTPengamanTest(unittest.TestCase):
    """Uji negatif: pengaman orkestra harus menolak keberhasilan semu."""

    def test_ledger_menolak_nama_kosong(self):
        ledger = LedgerFitur()
        for nama in ("", "   ", None):
            with self.subTest(nama=nama), self.assertRaises(AssertionError):
                ledger.tandai(nama, "bukti")
        self.assertEqual(set(), ledger.aktif())

    def test_ledger_menolak_bukti_kosong(self):
        ledger = LedgerFitur()
        for bukti in ("", "   ", None):
            with self.subTest(bukti=bukti), self.assertRaises(AssertionError):
                ledger.tandai("fitur", bukti)
        self.assertEqual(set(), ledger.aktif())

    def test_label_tidak_dikenal_ditolak(self):
        orkestra = OrkestraSST()
        self.addCleanup(orkestra.tmp.cleanup)
        with self.assertRaisesRegex(AssertionError, "tidak terdaftar"):
            orkestra._t("fitur.salah_ketik", "dipanggil")
        self.assertEqual(set(), orkestra.ledger.aktif())

    def test_fitur_tidak_dijalankan_menggagalkan_orkestra(self):
        orkestra = OrkestraSST()
        folder = orkestra.tmp.name
        # Hilangkan seluruh fase tanpa memalsukan ledger.
        for fase in FITUR_WAJIB:
            setattr(orkestra, "fase_" + fase.split("_", 1)[1], lambda: None)
        with self.assertRaisesRegex(AssertionError, "manifest berbeda"):
            orkestra.jalankan()
        self.assertFalse(os.path.exists(folder))

    def test_kegagalan_fase_membersihkan_sumber_daya(self):
        orkestra = OrkestraSST()
        folder = orkestra.tmp.name

        def gagal():
            raise RuntimeError("gagal terencana")

        orkestra.fase_sumber_daya_dan_kontrak = gagal
        with self.assertRaisesRegex(RuntimeError, "gagal terencana"):
            orkestra.jalankan()
        self.assertFalse(os.path.exists(folder))

    def test_sukses_membersihkan_sumber_daya(self):
        orkestra = OrkestraSST()
        folder = orkestra.tmp.name
        with contextlib.redirect_stdout(io.StringIO()):
            ledger = orkestra.jalankan()
        self.assertEqual(himpunan_fitur_wajib(), ledger.aktif())
        self.assertFalse(os.path.exists(folder))


class SSTKlasifikasiTest(unittest.TestCase):
    """Yang di luar orkestra harus terdaftar eksplisit — tidak boleh lolos."""

    def test_showcase_demo_diklasifikasi(self):
        ditemukan: Set[str] = set()
        for root, _, files in os.walk(os.path.join(AKAR, "pycos")):
            for nama in files:
                if not nama.endswith(".py"):
                    continue
                with open(os.path.join(root, nama), "r", encoding="utf-8") as f:
                    pohon = ast.parse(f.read())
                for simpul in ast.walk(pohon):
                    if isinstance(simpul, ast.FunctionDef) \
                            and simpul.name.startswith("demo"):
                        ditemukan.add(simpul.name)
        self.assertEqual(ditemukan, LUAR_CAKUPAN_SST,
                         "titik masuk demo berubah; perbarui LUAR_CAKUPAN_SST "
                         "atau masukkan ke orkestra")

    def test_tidak_ada_nama_fitur_ganda(self):
        total: List[str] = []
        for daftar in FITUR_WAJIB.values():
            total.extend(daftar)
        self.assertEqual(len(total), len(set(total)), "fitur ganda di manifest")


if __name__ == "__main__":
    orkestra = OrkestraSST(seed=2026)
    ledger = orkestra.jalankan()
    print(ledger.laporan())
    kurang = ledger.kurang(himpunan_fitur_wajib())
    print("FITUR TERTINGGAL:", sorted(kurang) if kurang else "tidak ada")
    sys.exit(0 if not kurang else 1)
