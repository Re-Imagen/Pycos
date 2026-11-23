# -*- coding: utf-8 -*-
"""Pycos — toolkit state kognitif untuk NPC dan agen simulasi.

Peta subpaket (satu lapis tanggung jawab per direktori):

    pycos.inti         — `Naluri`: enam drive, afek, atensi, presentasi, kawanan;
                         `Persona` dan `Keadaan` untuk profil & keadaan batin
    pycos.refleksi     — `Nurani`: refleksi, meta-plastisitas, dan penilai
                         keselarasan ujaran (`nilai_selaras`, `PelacakSelaras`)
    pycos.memori       — `JejakPrediksi`: memori episodik dan prediksi
    pycos.mandiri      — `Organik` + mekanisme kognitif lanjutan
    pycos.lingkungan   — dunia uji interaksi NPC (`Lingkungan`, `Peta`, objek)
    pycos.bahasa       — `TuturEngine` + penganalisis ujaran SA_SP + ciri
                         linguistik (`analisis_teks`)
    pycos.dukungan     — infrastruktur internal (patching, resolusi sumber daya)
    pycos.sumber_daya  — berkas data paket (`leksikon_pycos.json`)

Impor di sini malas (PEP 562): `import pycos` tidak menarik modul besar.
Nama publik di bawah dimuat saat pertama kali diakses, sehingga aplikasi host
boleh memakai `from pycos import Naluri` atau jalur eksplisit
`from pycos.inti import Naluri` — keduanya nama yang sama.

Istilah seperti kesadaran, emosi, dan memori menamai state simulasi
perangkat lunak, bukan klaim pengalaman subjektif atau model otak biologis.
"""
from __future__ import annotations

from typing import Any, Dict, List

__version__ = "0.1.0"

# Nama publik -> modul tempat nama itu didefinisikan.
_MODUL_NAMA: Dict[str, str] = {
    # pycos.inti
    "Naluri": "pycos.inti.naluri",
    "DRIVES": "pycos.inti.naluri",
    "Kesadaran": "pycos.inti.naluri",
    "Presentasi": "pycos.inti.naluri",
    "Ritual": "pycos.inti.naluri",
    "Goal": "pycos.inti.naluri",
    "Mood": "pycos.inti.naluri",
    "Reputasi": "pycos.inti.naluri",
    "KawananNPC": "pycos.inti.naluri",
    "buat_npc": "pycos.inti.naluri",
    # pycos.inti.persona — profil persona & keadaan batin ringkas
    "Persona": "pycos.inti.persona",
    "PERSONA_CONTOH": "pycos.inti.persona",
    "Keadaan": "pycos.inti.persona",
    # pycos.refleksi
    "Nurani": "pycos.refleksi.nurani",
    "CalibrationReport": "pycos.refleksi.nurani",
    "NURANI_DEFAULTS": "pycos.refleksi.nurani",
    # pycos.refleksi — penilaian keselarasan & kalibrasi (dulu pycos.selaras)
    "DimensiSkor": "pycos.refleksi.nurani",
    "Laporan": "pycos.refleksi.nurani",
    "PelacakSelaras": "pycos.refleksi.nurani",
    "nilai_selaras": "pycos.refleksi.nurani",
    # pycos.memori
    "JejakPrediksi": "pycos.memori.jejak_prediksi",
    # pycos.mandiri
    "Organik": "pycos.mandiri.organik",
    "KognisiLanjut": "pycos.mandiri.kognisi_lanjut",
    # pycos.lingkungan
    "Lingkungan": "pycos.lingkungan.dunia",
    "ObjekDunia": "pycos.lingkungan.dunia",
    "Peta": "pycos.lingkungan.dunia",
    # pycos.bahasa
    "TuturEngine": "pycos.bahasa.tutur",
    "GenContext": "pycos.bahasa.tutur",
    "SASPAnalyzer": "pycos.bahasa.tutur",
    "sa_sp": "pycos.bahasa.tutur",
    "sa_sp_literal": "pycos.bahasa.tutur",
    "sa_sp_pragmatik": "pycos.bahasa.tutur",
    # pycos.bahasa — ciri linguistik ujaran (dulu pycos.selaras.fitur)
    "FiturTutur": "pycos.bahasa.tutur",
    "analisis_teks": "pycos.bahasa.tutur",
    # pycos.dukungan
    "install_method": "pycos.dukungan.patching",
    "install_methods": "pycos.dukungan.patching",
    "optional_module": "pycos.dukungan.patching",
    "wrap_method": "pycos.dukungan.patching",
    "PatchConflictError": "pycos.dukungan.patching",
    "jalur_leksikon": "pycos.dukungan.sumber",
    "kandidat_leksikon": "pycos.dukungan.sumber",
    # Kontrak statis dan pemeriksaan operasi (tidak mengimpor lapisan pemilik).
    "DRIVE_KEYS": "pycos.kontrak",
    "LEVEL_TANPA_VERIFIKASI": "pycos.kontrak",
    "LEVEL_PRECONDITION": "pycos.kontrak",
    "LEVEL_OPERASI": "pycos.kontrak",
    "LEVEL_LINTAS_LAPIS": "pycos.kontrak",
    "JANJI": "pycos.kontrak",
    "KEBUTUHAN": "pycos.kontrak",
    "ContractViolationError": "pycos.kontrak",
    "kontrak_operasi": "pycos.kontrak",
    "verifikasi_startup": "pycos.kontrak",
    "check_operation": "pycos.kontrak",
    "verify_startup": "pycos.kontrak",
    "KEBIJAKAN_TOLAK": "pycos.kontrak",
    "KEBIJAKAN_CATAT": "pycos.kontrak",
    "KEBIJAKAN_ABAIKAN": "pycos.kontrak",
    # R5.4: API subpaket yang dipromosikan secara eksplisit; lihat docs/API_PUBLIK.md.
    "ARAH": "pycos.lingkungan.dunia",
    "Apersepsi": "pycos.mandiri.organik",
    "Arg": "pycos.bahasa.tutur",
    "Badan": "pycos.lingkungan.dunia",
    "BatasIdentitas": "pycos.mandiri.organik",
    "ContohLabel": "pycos.refleksi.nurani",
    "DetakInternal": "pycos.mandiri.organik",
    "EFEK_JENIS": "pycos.lingkungan.dunia",
    "EMOSI_NODE": "pycos.mandiri.kognisi_lanjut",
    "EversiTD": "pycos.mandiri.kognisi_lanjut",
    "Gejala": "pycos.mandiri.organik",
    "GejalaMurni": "pycos.mandiri.organik",
    "GrafAsosiasi": "pycos.mandiri.kognisi_lanjut",
    "Intrusi": "pycos.mandiri.organik",
    "Invensi": "pycos.mandiri.organik",
    "JENIS_DAPAT_DIAMBIL": "pycos.lingkungan.dunia",
    "KALIMAT_ADA_SESUATU": "pycos.mandiri.organik",
    "KALIMAT_TAK_BERNAMA": "pycos.mandiri.organik",
    "KOSONG": "pycos.mandiri.organik",
    "KategoriProto": "pycos.mandiri.organik",
    "L0": "pycos.bahasa.tutur",
    "L1": "pycos.bahasa.tutur",
    "L2": "pycos.bahasa.tutur",
    "L3": "pycos.bahasa.tutur",
    "LEGENDA_MEDAN": "pycos.lingkungan.dunia",
    "LEKSIKON_CIRI_BAWAAN": "pycos.bahasa.tutur",
    "LapisanParalel": "pycos.mandiri.organik",
    "Lattice": "pycos.bahasa.tutur",
    "Leksikon": "pycos.bahasa.tutur",
    "LeksikonCiri": "pycos.bahasa.tutur",
    "LukaDomain": "pycos.mandiri.organik",
    "MesinKepercayaan": "pycos.mandiri.kognisi_lanjut",
    "ModelKausal": "pycos.mandiri.organik",
    "NAMA_KORPUS": "pycos.dukungan.sumber",
    "NAMA_LEKSIKON": "pycos.dukungan.sumber",
    "Node": "pycos.bahasa.tutur",
    "Orkestrator": "pycos.bahasa.tutur",
    "PROPERTI_TERLARANG": "pycos.mandiri.organik",
    "PenolakanTutur": "pycos.mandiri.organik",
    "Perencana": "pycos.mandiri.organik",
    "ProsesOU": "pycos.mandiri.kognisi_lanjut",
    "Residu": "pycos.mandiri.organik",
    "SIMBOL_OBJEK": "pycos.lingkungan.dunia",
    "TAK_BERLAKU": "pycos.mandiri.organik",
    "TERISI": "pycos.mandiri.organik",
    "TopologiSlot": "pycos.mandiri.organik",
    "TubuhSumber": "pycos.mandiri.organik",
    "Tutur": "pycos.bahasa.tutur",
    "Vacancy": "pycos.mandiri.organik",
    "WaktuHeterogen": "pycos.mandiri.organik",
    "ada_sumber_daya": "pycos.dukungan.sumber",
    "akar_paket": "pycos.dukungan.sumber",
    "boltzmann_pilih": "pycos.mandiri.kognisi_lanjut",
    "inventaris": "pycos.dukungan.patching",
    "jalur_korpus": "pycos.dukungan.sumber",
    "kappa_cohen": "pycos.refleksi.nurani",
    "konteks_dari_presentasi": "pycos.bahasa.tutur",
    "laporan_kalibrasi": "pycos.refleksi.nurani",
    "muat_korpus": "pycos.refleksi.nurani",
    "peta_contoh": "pycos.lingkungan.dunia",
    "suhu_mental": "pycos.mandiri.kognisi_lanjut",
    "JejakLinguistik": "pycos.bahasa.teks",
    "Token": "pycos.bahasa.teks",
    "analisis_ujaran": "pycos.bahasa.teks",
    "cakupan_negasi": "pycos.bahasa.teks",
    "deteksi_bahasa": "pycos.bahasa.teks",
    "ekstrak_entitas": "pycos.bahasa.teks",
    "ekstrak_topik": "pycos.bahasa.teks",
    "jejak_pembentukan": "pycos.bahasa.teks",
    "jenis_kalimat": "pycos.bahasa.teks",
    "jenis_pertanyaan": "pycos.bahasa.teks",
    "kandidat_dasar": "pycos.bahasa.teks",
    "kemiripan": "pycos.bahasa.teks",
    "koreksi_ejaan": "pycos.bahasa.teks",
    "normalisasi_teks": "pycos.bahasa.teks",
    "normalisasi_token": "pycos.bahasa.teks",
    "pecah_kalimat": "pycos.bahasa.teks",
    "G1_KERAS": "pycos.bahasa.teks",
    "G1_LEMAK": "pycos.bahasa.teks",
    "VERBA_UMUM": "pycos.bahasa.teks",
    "periksa_gramatika": "pycos.bahasa.teks",
    "potong_batas_kata": "pycos.bahasa.teks",
    "stem": "pycos.bahasa.teks",
    "tindak_tutur_skor": "pycos.bahasa.teks",
    "tokenisasi": "pycos.bahasa.teks",
    "urai_subjek_predikat": "pycos.bahasa.teks",
    "token_dari": "pycos.bahasa.tutur",
    "ukur_fitur": "pycos.refleksi.nurani",
    "ukur_selaras": "pycos.refleksi.nurani",
    # View reflektif read-only atas wadah pengetahuan dan sikap.
    "STATUS_PENGETAHUAN": "pycos.refleksi.ketidaktahuan",
    "SIKAP_KETIDAKTAHUAN": "pycos.refleksi.ketidaktahuan",
    "batas_pengetahuan": "pycos.refleksi.ketidaktahuan",
    "sikap_ketidaktahuan": "pycos.refleksi.ketidaktahuan",
}

__all__: List[str] = ["__version__"] + sorted(_MODUL_NAMA)


def __getattr__(name: str) -> Any:
    """Selesaikan nama publik pada akses pertama, bukan pada `import pycos`."""
    modul = _MODUL_NAMA.get(name)
    if modul is None:
        raise AttributeError(
            "modul {!r} tidak punya atribut {!r}".format(__name__, name))
    import importlib

    nilai = getattr(importlib.import_module(modul), name)
    globals()[name] = nilai          # cache: resolusi hanya sekali per proses
    return nilai


def __dir__() -> List[str]:
    return sorted(set(globals()) | set(_MODUL_NAMA))
