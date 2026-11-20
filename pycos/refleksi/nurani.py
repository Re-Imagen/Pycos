# -*- coding: utf-8 -*-
"""
NURANI — Naluri Reflektif (lapisan meta-plastisitas untuk InstinctCore)
=======================================================================

Konsep 17. `pycos.inti.naluri` adalah organisme reaktif yang matang: enam
drive, mood, kalibrasi EMA, skala adaptif, kebijakan tidur/mimpi, dan pilar
NNRE. (Penomoran konsep mengikuti daftar desain proyek yang tidak disertakan
di repo; pemetaan angka → fitur ada di README bagian "Penomoran konsep dalam
source".) Kelemahannya struktural dan disebut sendiri oleh diagnosanya: hampir
semua lapisannya STATIS. Lexicon tidak belajar dari pengalaman, setpoint tidak
pernah bergerak, kalibrasi hanya satu angka, dan konflik antar-drive tidak
perlu diselesaikan — hanya dijumlahkan berbobot lalu saling meniadakan.

NURANI menambahkan satu lapisan meta-plastisitas di atas arsitektur yang sudah
ada, TANPA membongkar API publik `Naluri`: Naluri tidak hanya memiliki insting
— ia belajar tentang instingnya sendiri.

Tesis: setiap lapisan Naluri (persepsi, kalibrasi, setpoint, keputusan) harus
plastis dan saling menginformasikan.

Catatan penyatuan: seksi penilai/pelacak/kalibrasi di bagian bawah modul ini
adalah penilai keselarasan ujaran (Persona × Keadaan × ciri tutur) yang dahulu
berada di subpaket `pycos.selaras`, kini dilebur ke sini. Impor `pycos.inti`
dan `pycos.bahasa` dilakukan secara malas di dalam fungsi agar rantai impor
tetap satu arah (naluri boleh memuat NURANI tanpa lingkaran).

Enam pilar (A–F) dan Watak (W)
------------------------------
Catatan historis: ikhtisar ini pernah berjudul "Empat pilar" saat baru A–D
yang ada; E, F, dan W menyusul, jadi jumlah pada judul lama tidak lagi akurat.
A. **Memori Afektif (Nurani)** — "rasa cepat sebelum pikiran lambat".
   Setiap deskripsi yang pernah dialami disimpan sebagai signature ringan ->
   running-mean dampak drive; `anticipate()` mengubahnya menjadi prior yang
   di-blend ke hasil lexicon di `impact_of()`. Kata yang belum ada di lexicon
   akhirnya punya arti setelah beberapa pengalaman.
B. **Kalibrasi Berlapis (Cermin)** — "nurani sebagai alat ukur yang jujur".
   `Brier` probabilitas + EMA galat per drive + bin reliability menggantikan
   satu skalar `_calibration_ema` yang mencampur semua tipe kesalahan; update
   skala adaptif lewat validasi hold-out sehingga rasio mentah yang merusak
   prediksi ditolak (`scale_ditolak` mencatatnya).
C. **Setpoint Plastis & Interosepsi (Tubuh)** — "tubuh yang belajar tentang
   kebutuhannya sendiri". Urgensi dihitung relatif terhadap setpoint yang
   bergerak (habituasi homeostatis), dan matriks korelasi antar-drive memberi
   "gema interoseptif": kelelahan kronis merembet ke koherensi/penguasaan
   secara terpelajar, bukan hardcoded.
D. **Resolusi Konflik & Ritme (Irama)** — "ketika dua hati berbeda pendapat,
   didamaikan, bukan dijumlahkan". Deteksi konflik antar goal berurgensi
   tinggi, bonus untuk aksi kompromi, ritme sirkadian untuk tidur preventif,
   dan keadaan flow yang dihargai sebagai reward intrinsik.
E. **Memori Sosial (Empati)** — "hati yang mengingat orang, bukan hanya rasa".
   Setiap ENTITAS (pemain, NPC lain) punya slot relasi: valensi (suka/tidak),
   kepercayaan, keakraban, jumlah interaksi. `social_prior()` menerjemahkan
   relasi menjadi bias drive (afiliasi/keamanan) saat memutuskan aksi yang
   melibatkan entitas itu; keakraban & valensi meluruh perlahan (lupa sosial).
   Mati secara bawaan seperti pilar lain (`enable_social_memory`).

F. **Persepsi (Panca Indera)** — "dunia tidak masuk apa adanya; ia
   direkonstruksi". Stimulus drive (event) melewati saluran fisiologis
   sebelum menjadi delta: derau reseptor + deteksi sinyal (criterion per
   drive; negatif = hipervigilan → alarm palsu), kompresi Weber-Fechner
   terhadap level adaptasi (Helson), habituasi per-stimulus dengan pemulihan
   spontan, dan pembelajaran perseptual (sensitivitas d' naik/turun dari
   galat prediksi per drive). Atensi (kapasitas terbatas) dan pencampuran
   top-down (prior afektif) dijalankan di sisi Naluri. Mati bawaan
   (`enable_perception`).

W. **Watak (viskositas per-drive & backstory)** — bukan pilar baru, melainkan
   generalisasi parameter semua pilar: setiap parameter plastisitas ber-sumbu
   drive (`setpoint_lr`, `setpoint_clamp`, `interoception_lr`,
   `interoception_echo`, `affective_trust_cap`, `calibration_report_alpha`,
   `social_prior_weight`) menerima skalar ATAU dict per-drive —
   `{"keamanan": 1e-5, "*": 8e-4}` ("*" = fallback; tanpa "*", NURANI_DEFAULTS).
   Resolver: `_p_drive(key, drive)`. `social_consolidation` menambah viskositas
   per-ENTITAS pada laju sosial (lr efektif = lr / (1 + c*n); 0 = perilaku lama).
   `social_trust_recovery_penalty` menambah ASIMETRI: bila kepercayaan sudah
   negatif (rusak), interaksi positif untuk memulihkannya dibagi
   (1 + penalty * keparahan) — menghancurkan cepat, memulihkan mahal.
   `break_trust()` mematahkan kepercayaan secara langkah (pengkhianatan).
   `trust_recovery_factor(ent)` melaporkan pengali pemulihan efektif.
   UTANG EMOSIONAL (`tambah_utang`/`bayar_utang`/`berat_utang`/`menarik_diri`):
   janji yang belum ditepati menumpuk; beratnya menekan `social_prior` dan
   interaksi positif secara proporsional, dan lewat `social_utang_ambang`
   NPC menarik diri ("aku tidak mau lagi percaya"). CORE MEMORY CAP:
   `tandai_core(text)` menaikkan cap kepercayaan khusus untuk signature itu,
   sehingga satu momen bisa mendominasi rata-rata masa lalu.
   Metode `seed_affective` / `seed_relationship` / `seed_setpoints` /
   `seed_calibration` menuntaskan cold-start: filter hanya MEMPERTAHANKAN
   sifat — kondisi awal (backstory "lahir") yang menciptakannya di tick 0.

Prinsip pemasangan
------------------
* Semua pilar MATI secara bawaan (`enable_*` di `DEFAULTS` -> nol perubahan
  perilaku, kompatibel mundur). `Naluri` tetap identik dengan sebelumnya bila
  tidak ada flag yang dinyalakan.
* Serialisasi (untuk save/load NPC): `Nurani.to_dict()` / `Nurani.from_dict()`
  menangani state bersarang (kunci int `_affective` -> string agar JSON-safe,
  matriks interosepsi, pasangan unit kalibrasi). Saat menempel pada Naluri,
  `params` TIDAK diduplikasi — Naluri pemilik satu-satunya dan
  `from_dict(data, params=naluri.params)` menjaga binding dict bersama itu.
* Modul ini nol-dependensi (stdlib saja) dan TIDAK meng-import `pycos.inti`;
  objek `Naluri` yang masuk selalu lewat argumen (duck-typed), sehingga
  `python -m pycos.refleksi.nurani` (atau `python3 pycos/refleksi/nurani.py`)
  tetap bisa jalan sendiri sebagai demo.
* Konstanta `DEFAULT_DRIVES` di bawah adalah salinan `DRIVES` di
  `pycos.inti.naluri`; tidak ada impor bolak-balik. Sinkronnya kini dijaga
  tes `KoherensiLintasModulTest.test_daftar_drive_tiga_salinan_sama`
  (bersama `DRIVE_KEYS` di `pycos.kontrak`).
* Angka A/B tiap pilar dan daftar penyimpangan dari konsep tulisannya pernah
  dicatat di `run.py --section nurani` dan `analysis/RINGKASAN_NURANI.md` —
  keduanya berkas historis di luar repositori ini, tidak ikut disertakan.
* Catatan penyimpangan dari konsep asli (disengaja, supaya bisa diuji ulang):
  signature memakai `zlib.crc32` alih-alih `hash()` bawaan Python yang
  ter-salt per-proses (`PYTHONHASHSEED`), agar memori afektif deterministik
  dan bisa dibandingkan antar-run; dan `enable_flow_state` ditambahkan sebagai
  flag tersendiri karena bonus reward tidak boleh mengubah skor lama secara
  diam-diam.
"""
from __future__ import annotations

import copy
import json
import math
import random
import re
import zlib
from collections import deque
from dataclasses import dataclass, field
from typing import (TYPE_CHECKING, Any, Deque, Dict, List, Mapping, Optional,
                    Sequence, Tuple, Set, Callable, cast)

if TYPE_CHECKING:  # hanya untuk anotasi; runtime memakai duck-typing/impor malas
    from pycos.mandiri.organik import LukaDomain
    from pycos.mandiri.kognisi_lanjut import GrafAsosiasi
    from pycos.bahasa.tutur import LeksikonCiri
    from pycos.inti.persona import Keadaan, Persona

if not __package__:  # berkas dieksekusi langsung, bukan sebagai modul paket
    # `python3 pycos/refleksi/nurani.py` di dalam checkout: kenalkan direktori
    # induk paket ke sys.path supaya impor `pycos.*` tetap resolve tanpa
    # instalasi maupun PYTHONPATH manual.
    import os as _os
    import sys as _sys

    _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.dirname(
        _os.path.abspath(__file__)))))
    del _os, _sys

from pycos.dukungan.numerik import jepit, jepit_01, jepit_drive
from pycos.dukungan.patching import (install_method, optional_module,
                                     wrap_method)
from pycos.kontrak import hanya_kunci, teks_wajib

# ---------------------------------------------------------------------------
# Konstanta
# ---------------------------------------------------------------------------
# Enam drive homeostatis; harus sama dengan DRIVES pycos.inti.naluri.
from pycos.dukungan import konstanta as _konstanta_drive
DEFAULT_DRIVES = _konstanta_drive.DRIVES

# Nama pilar (dipakai sebagai sufiks kunci `enable_<pilar>` dan `pillar`).
PILLARS: Tuple[str, ...] = (
    "affective_memory", "layered_calibration", "plastic_setpoints",
    "interoception", "conflict_resolution", "circadian", "flow_state",
    "social_memory", "perception", "introspection",
)

# Parameter NURANI. Di-unpack ke DEFAULTS inti agar ada satu sumber
# kebenaran; `Nurani` membaca dict milik Naluri (lihat __init__).
NURANI_DEFAULTS: Dict[str, Any] = {
    # --- sakelar pilar (semua mati secara bawaan = kompatibel mundur) ---
    "enable_affective_memory": False,
    "enable_layered_calibration": False,
    "enable_plastic_setpoints": False,
    "enable_interoception": False,
    "enable_conflict_resolution": False,
    "enable_circadian": False,
    "enable_flow_state": False,
    "enable_social_memory": False,
    # --- pilar A: memori afektif ---
    "affective_max": 2000,          # kapasitas slot (LRU)
    "affective_min_samples": 2,     # pengalaman ke-n sebelum prior dipakai
    "affective_trust_cap": 0.7,     # bobot maksimum prior terhadap lexicon
                                    #   (WATAK: boleh dict per-drive, mis.
                                    #    {"keamanan": 0.95, "*": 0.7})
    "affective_trust_saturate": 10,  # n sampel di atasnya kepercayaan jenuh
    "affective_max_age": 400,       # usia (tick) untuk pruning manual
    "enable_episode_log": True,     # replay ringkas lintas sesi (hanya pilar A aktif)
    "episode_log_max": 50,          # replay selektif; pertahankan pengalaman bermakna
    "memory_retention_half_life": 1200.0,  # eviksi meluruh, bukan LRU murni
    "word_delta_alpha": 0.08,        # laju kecil asosiasi kata → perubahan drive
    "word_delta_gain": 0.25,         # kontribusi lexicon kata dibatasi agar tetap minor
    "word_delta_min_samples": 2,     # bukti minimum sebelum kata memengaruhi intuisi
    "word_delta_saturate": 5,        # kepercayaan kata jenuh bertahap
    "word_delta_max": 4096,          # batas memori lexicon dinamis
    # --- pilar B: kalibrasi berlapis + skala tervalidasi ---
    "reliability_bins": 10,
    "calibration_report_alpha": 0.25,  # WATAK: boleh dict per-drive (EMA galat)
    "scale_holdout_fraction": 0.8,
    "scale_holdout_min_pairs": 40,
    "scale_holdout_window": 200,
    "scale_holdout_min_gain": 0.0,  # perbaikan minimum agar update diterima
    "sleep_brier_threshold": 0.3,
    "sleep_spike_error": 0.6,       # satu kejutan besar -> tidur sekarang
    "sleep_spike_window": 3,
    "uncertainty_alpha": 0.20,      # EMA epistemik/aleatorik terpisah
    # --- pilar C: setpoint plastis + interosepsi ---
    "setpoint_lr": 0.0008,          # WATAK: boleh dict per-drive — inilah
                                    #   "viskositas" utama: seberapa cepat
                                    #   ekspektasi drive direvisi pengalaman
    "setpoint_clamp": 0.4,          # WATAK: boleh dict per-drive (rentang keyakinan)
    "interoception_period": 20,     # frekuensi pembaruan matriks (tick)
    "interoception_lr": 0.02,       # WATAK: boleh dict per-drive TARGET (kolom)
    "interoception_gate": 0.1,      # deficit minimum drive sumber
    "interoception_echo": 0.15,     # pengali gema saat menghitung urgensi
                                    #   WATAK: boleh dict per-drive penerima
    "interoception_decay_period": 100,
    "interoception_decay": 0.02,    # lupa 2% per 100 tick menuju nol
    # --- pilar D: konflik, ritme, flow ---
    "circadian_period": 24,
    "circadian_night_shift": 0.3,   # ambang energi malam naik (preventif)
    "conflict_urgency_gate": 0.3,
    "conflict_sign_eps": 0.05,
    "compromise_bonus": 0.3,
    "flow_valence_min": 0.3,
    "flow_arousal_max": 0.4,
    "flow_reward_bonus": 0.05,
    # --- pilar E: memori sosial (EMPATI) ---
    "social_max": 64,                # kapasitas entitas (LRU by last_t)
    "social_valensi_lr": 0.5,        # laju perubahan valensi per muatan
    "social_trust_lr": 0.3,          # laju perubahan kepercayaan (lebih lambat)
    "social_familiarity_lr": 0.2,    # keakraban naik per interaksi (menuju 1)
    "social_consolidation": 0.0,     # WATAK: konsolidasi per-ENTITAS — lr efektif
                                     #   dibagi (1 + c*n): kesan pertama mudah
                                     #   berubah, relasi lama sukar digoyang
                                     #   (0.0 = perilaku lama)
    "social_trust_recovery_penalty": 10.0,  # ASIMETRI: bila kepercayaan sudah
                                     #   negatif (rusak), setiap interaksi
                                     #   positif untuk MEMULIHKAN dibagi
                                     #   (1 + penalty * keparahan). Menghancurkan
                                     #   mudah & cepat; memperbaiki mahal.
    "social_trust_crash_threshold": -0.3,   # di bawah ini relasi dianggap
                                     #   "hancur": pemulihan paling lambat
    "social_trust_recovery_cap": 0.0,  # batas atas pemulihan per interaksi
                                     #   dari kondisi hancur (0 = tanpa batas)
    # FITUR 4: utang emosional (janji/permintaan yang belum ditepati).
    "social_utang_ambang": 3.0,     # total bobot utang → NPC menarik diri
    "social_utang_prior_penalty": 0.22,  # tiap 1.0 bobot utang mengurangi
                                     #   social_prior secara proporsional
    "social_utang_withdraw_mult": 0.15,  # pengali interaksi positif saat
                                     #   sudah menarik diri (hampir tak percaya)
    # FITUR 1: core memory menaikkan cap kepercayaan untuk signature itu.
    "core_memory_cap": 0.95,         # cap default signature memori inti
    "core_memory_max": 5,            # jumlah pilar identitas yang disimpan
    "social_decay_period": 200,      # periode peluruhan lupa-sosial (tick)
    "social_decay": 0.03,            # besar peluruhan per periode
    "social_max_age": 2000,          # usia default untuk forget_social()
    "social_prior_weight": 0.25,     # bobot prior relasi -> bias drive
                                     #   WATAK: boleh dict per-drive
    "tom_belief_lr": 0.35,           # laju update model keyakinan pihak lain
    "tom_similarity_prior": 0.25,   # false-consensus prior saat bukti tipis
    "tom_max_entities": 64,          # slot sparse theory-of-mind per agen
    "tom_glasses_relax_after": 24,   # bukti lawan sebelum ini belum melonggarkan
    "tom_glasses_relax_examples": 40,# pelonggaran baru nyata setelah puluhan contoh
    # --- pilar F: persepsi (panca indera + psikofisika) ---
    "enable_perception": False,
    "persepsi_noise": 0.03,          # σ derau reseptor (fisiologi: noise saraf)
    "persepsi_ambang": 0.02,         # ambang mutlak kesadaran (absolute threshold)
    "persepsi_kriterion": 0.0,       # kriteria SDT per-drive (WATAK: dict);
                                     #   negatif = hipervigilan/bias "ya" ->
                                     #   stimulus lemah lolos + alarm palsu
    "persepsi_sensitivitas": 1.0,    # pengali d' dasar (WATAK: dict per-drive);
                                     #   dikalikan sensitivitas TERPELAJARI [0.5,2]
    "persepsi_weber": 0.5,           # k kompresi Weber-Fechner (saturasi log)
    "persepsi_adaptasi_lr": 0.03,    # laju level adaptasi (Helson) per tick
    "persepsi_habit_lr": 0.20,       # habituasi: faktor (1-lr)^n per pengulangan
    "persepsi_habit_lantai": 0.15,   # lantai habituasi (tak pernah nol total)
    "persepsi_habit_pulih": 0.04,    # pemulihan spontan per tick absen
    "persepsi_habit_window": 60,     # tick tanpa stimulus = hitungan direset
    "persepsi_habit_max": 256,       # kapasitas slot habituasi (LRU)
    "persepsi_belajar_lr": 0.05,     # laju pembelajaran perseptual (d')
    "persepsi_subliminal": 0.25,     # residu stimulus bawah sadar (bukan nol)
    # Surprise struktural membatalkan kopling lama dan mengguncang d', bukan
    # memperbarui model yang baru saja terbukti salah secara inkremental.
    "structural_surprise_multiplier": 2.0,
    "structural_shock_ticks": 12,
    # --- pilar G: introspeksi diri (metakognisi + interosepsi sadar) ---
    # Fisiologi nyata:
    #   * Interosepsi sadar = anterior insula (Craig 2002, Critchley 2004)
    #     mengintegrasi sinyal tubuh -> model diri dengan derau & bias.
    #   * Monitoring konflik/error = ACC (Botvinick 2001, Yeung 2004 ERN)
    #   * Evaluasi metakognitif = rostrolateral PFC / vmPFC (Fleming & Dolan 2012,
    #     Fleming 2017) -> confidence & meta-d'
    #   * Narasi diri = DMN / mPFC / precuneus (Raichle 2001, Northoff 2006)
    #   * Global Workspace (Dehaene) = ambang sadar untuk akses laporan diri
    # Teori: Nelson & Narens 1990 (object-level vs meta-level), Seth 2013
    #   interoceptive predictive coding (self-model = prediksi interoseptif),
    #   Damasio 1994 somatic marker (tubuh menandai nilai).
    "enable_introspection": False,
    "introspeksi_noise": 0.08,           # σ derau interoseptif (Craig: noise saraf)
                                         # WATAK: boleh dict per-drive
    "introspeksi_bias": 0.0,             # bias sistematis (mis. -0.1 = selalu merasa kurang aman)
                                         # WATAK: boleh dict per-drive
    "introspeksi_lr": 0.06,              # laju update model diri (plastisitas insula)
                                         # WATAK: boleh dict per-drive
    "introspeksi_meta_lr": 0.04,         # laju update kepercayaan diri (PFC)
                                         # WATAK: boleh dict per-drive
    "introspeksi_window": 64,            # jendela untuk korelasi & meta-d'
    "introspeksi_ambang_sadar": 0.18,    # ambang discrepansi -> sadar (Global Workspace)
    "introspeksi_refleksi_period": 24,   # periode refleksi DMN (tick)
    "introspeksi_max_memori": 256,       # kapasitas memori episodik diri
    "introspeksi_kepercayaan_awal": 0.5, # kepercayaan awal per saluran
    "introspeksi_meta_d_floor": 0.0,
    "introspeksi_meta_d_ceiling": 2.5,
}

# ---------------------------------------------------------------------------
# KESADARAN TERASA — perluasan pilar G NURANI (konsep 2, 5, 6).
# Pilar introspeksi sudah memodelkan tubuh (model_diri) dan metakognisi, tetapi
# belum "merasakan". Blok ini menambahkan: monolog batin berjalan + identitas
# naratif, interosepsi yang bisa dilaporkan (felt_state), emosi moral, somatic
# marker (Damasio), monitoring realitas/source memory, keraguan metakognitif,
# dan konfabulasi. Semua aditif & kompatibel mundur.
# ---------------------------------------------------------------------------
NURANI_FELT_STATES: Tuple[str, ...] = (
    "nyeri", "lelah", "lapar", "sesak", "jantung", "mual", "tegang", "ringan",
)
NURANI_MORAL_EMOTIONS: Tuple[str, ...] = (
    "bersalah", "malu", "bangga", "cemburu", "iri", "syukur", "haru", "kesepian",
)
NURANI_MORAL_ALIASES: Dict[str, str] = {
    "bersalah": "bersalah", "guilty": "bersalah", "guilt": "bersalah",
    "malu": "malu", "shame": "malu", "ashamed": "malu",
    "bangga": "bangga", "proud": "bangga", "pride": "bangga",
    "cemburu": "cemburu", "jealous": "cemburu", "jealousy": "cemburu",
    "iri": "iri", "envy": "iri", "envious": "iri",
    "syukur": "syukur", "gratitude": "syukur", "grateful": "syukur",
    "haru": "haru", "moved": "haru", "touched": "haru",
    "kesepian": "kesepian", "lonely": "kesepian", "loneliness": "kesepian",
}
NURANI_REALITY_SOURCES: Tuple[str, ...] = (
    "persepsi", "ingatan", "imajinasi", "mimpi",
)
NURANI_DEFAULTS.update({
    # master sub-lapisan kesadaran terasa + sakelar per-fitur
    "enable_felt_consciousness": False,
    "enable_inner_speech": False,
    "enable_moral_emotions": False,
    "enable_somatic_markers": False,
    "enable_reality_monitoring": False,
    "felt_lr": 0.15,               # laju pembentukan sensasi tubuh
    "felt_threshold": 0.15,        # ambang lapor ("aku tidak enak badan")
    "inner_speech_period": 6,      # tick antar monolog batin berjalan
    "moral_lr": 0.25,              # laju emosi moral
    "somatic_max": 64,             # kapasitas somatic marker
    "doubt_lr": 0.10,              # laju keraguan metakognitif
    "confab_max": 48,              # kapasitas log konfabulasi
})

# ---------------- KESADARAN TERASA: method NURANI ----------------
# Blok method disisipkan ke kelas Nurani oleh skrip penyisip.

FASE: Tuple[str, str, str, str] = ("pagi", "siang", "sore", "malam")


@dataclass
class CalibrationReport:
    """Rapor kalibrasi berlapis (pilar B).

    brier         rata-rata (prob - sukses)^2 di seluruh sampel
    brier_ema     EMA brier (peka terhadap kondisi terkini)
    per_drive_ema EMA galat per drive -> "aku selalu salah soal afiliasi"
    reliability   daftar (rata-rata prediksi, rata-rata realita, n) per bin
    n_samples     banyak observasi yang tercatat
    """
    brier: float
    brier_ema: float
    per_drive_ema: Dict[str, float] = field(default_factory=dict)
    reliability: List[Tuple[float, float, int]] = field(default_factory=list)
    n_samples: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "brier": round(self.brier, 4),
            "brier_ema": round(self.brier_ema, 4),
            "per_drive_ema": {k: round(v, 4) for k, v in self.per_drive_ema.items()},
            "reliability": [(round(p, 3), round(r, 3), n)
                            for p, r, n in self.reliability],
            "n_samples": self.n_samples,
        }


# ---------------------------------------------------------------------------
# Nurani
# ---------------------------------------------------------------------------
class Nurani:
    """Lapisan meta-plastisitas di atas `Naluri` (empat pilar NURANI).

    Objek ini TIDAK memegang kendali: ia membaca state Naluri, belajar darinya,
    dan menulis bias halus (prior, setpoint, gema interoseptif, bonus kompromi,
    ambang malam) yang pemakaiannya diputuskan oleh `Naluri` per pilar.
    """

    def __init__(self,
                 drives: Sequence[str] = DEFAULT_DRIVES,
                 params: Optional[Dict[str, Any]] = None,
                 rng_seed: Optional[int] = None) -> None:
        self.drives: Tuple[str, ...] = tuple(drives)
        # RNG lokal untuk derau sumber/konfabulasi: deterministik bila seed
        # diberikan (Naluri menurunkannya dari rng_seed NPC).
        self._rng = random.Random(rng_seed)
        self._index: Dict[str, int] = {d: i for i, d in enumerate(self.drives)}
        # params adalah dict MILIK Naluri (bisa None untuk pemakaian berdiri
        # sendiri): dibaca setiap saat supaya perubahan flag langsung berlaku.
        # WATAK: deep-copy fallback — NURANI_DEFAULTS/params bisa memuat dict
        # per-drive bersarang; salinan dangkal akan berbagi referensi.
        self.params: Dict[str, Any] = (params if params is not None
                                       else copy.deepcopy(NURANI_DEFAULTS))

        # --- pilar A: memori afektif ---
        self._affective: Dict[int, Dict[str, Any]] = {}
        self._sig_cache: Dict[str, int] = {}
        self.affective_hits: int = 0        # kali prior benar-benar dipakai
        self.experience_count: int = 0      # banyak pengalaman terekam
        self.affective_evicted: int = 0     # korban eviksi berbobot
        self.affective_forgotten: int = 0   # korban forget_affective()
        self._episode_log: List[Dict[str, Any]] = []  # replay ringkas lintas sesi
        # Lexicon dinamis per kata; terpisah dari signature frasa agar kata
        # yang baru dapat dipelajari dari contoh dengan laju kecil.
        self._kata_delta: Dict[str, Dict[str, Any]] = {}
        self.kata_delta_evicted: int = 0

        # --- pilar B: kalibrasi berlapis ---
        self._brier_sum: float = 0.0
        self._brier_ema: float = 0.0
        self._brier_n: int = 0
        self._drive_err_ema: Dict[str, float] = {d: 0.0 for d in self.drives}
        self._drive_err_n: Dict[str, int] = {d: 0 for d in self.drives}
        self._errors: List[float] = []                       # galat mentah terkini
        self._pairs_unit: List[Tuple[float, float]] = []     # (pred, real) di [0,1]
        self.scale_accepted: int = 0
        self.scale_rejected: int = 0
        self.last_holdout: Tuple[float, float] = (0.0, 0.0)
        self._epistemic_ema: float = 1.0
        self._aleatoric_ema: float = 0.0
        self._uncertainty_n: int = 0

        # --- pilar C: setpoint plastis + interosepsi ---
        self.setpoints: Dict[str, float] = {d: 0.0 for d in self.drives}
        n = len(self.drives)
        self.interoception: List[List[float]] = [[0.0] * n for _ in range(n)]
        self._structural_shocks: List[Dict[str, Any]] = []
        self._sensitivitas_instabil: Dict[str, Dict[str, Any]] = {}
        self._perception_tick: int = 0

        # --- pilar D: konflik, ritme, flow ---
        self.conflict_ticks: int = 0
        self.conflict_resolved: int = 0
        self.conflict_drives: List[str] = []
        self.flow_ticks: int = 0

        # --- pilar E: memori sosial (EMPATI) ---
        # kunci = str(entitas) agar JSON-safe; nilai = slot relasi.
        self._entitas: Dict[str, Dict[str, Any]] = {}
        # FITUR 1: cap kepercayaan naik khusus untuk signature memori inti
        #   {signature(str): cap}. "Momen" menindih rata-rata masa lalu.
        self._core_cap: Dict[str, float] = {}
        # Stempel waktu untuk DETEKSI HESITASI (diam yang bermakna).
        self._last_conflict_tick: int = -10_000
        self._last_social_tick: int = -10_000
        self.social_interactions: int = 0   # total interaksi tercatat
        self.social_evicted: int = 0        # korban LRU
        self.social_forgotten: int = 0      # korban forget_social()
        # Model pihak lain yang sparse: entitas -> drive -> estimate/confidence.
        self._other_beliefs: Dict[str, Dict[str, Dict[str, Any]]] = {}
        # Bias lensa proyeksi lintas-entitas. Ini bukan proposisi eksplisit dan
        # tidak dicampur sebagai noise; kekakuannya hanya longgar oleh banyak
        # bukti yang konsisten berlawanan arah.
        self._kacamata_sosial: Dict[str, Dict[str, Any]] = {
            d: {"bias": 0.0, "kekakuan": 1.0, "bukti_lawan": 0,
                "observasi": 0} for d in self.drives}

        # --- pilar F: persepsi (psikofisika saluran drive) ---
        # sensitivitas d' TERPELAJARI per saluran [0.5..2.0] (perceptual
        # learning); adaptasi = level adaptasi Helson per saluran; _habit =
        # slot habituasi per (drive, alasan) dengan pemulihan spontan malas.
        self.sensitivitas: Dict[str, float] = {d: 1.0 for d in self.drives}
        self.adaptasi: Dict[str, float] = {d: 0.0 for d in self.drives}
        self._habit: Dict[int, Dict[str, Any]] = {}
        self.persepsi_sadar: int = 0        # stimulus lolos ambang
        self.persepsi_subliminal: int = 0   # stimulus di bawah ambang
        self.persepsi_evicted: int = 0      # korban LRU habituasi

        # --- pilar G: introspeksi diri (fisiologi nyata) ---
        # model_diri = self-model (Seth 2013: prediksi interoseptif)
        # kepercayaan_diri = metacognitive confidence (Fleming & Dolan)
        # meta_d = metacognitive sensitivity meta-d' (Maniscalco & Lau 2012)
        # _introspeksi_history = episodik diri (DMN / autobiographical)
        # _error_monitor = ACC conflict/error signal (Botvinick 2001)
        self.model_diri: Dict[str, float] = {d: 0.0 for d in self.drives}
        self.model_urgensi: Dict[str, float] = {d: 0.0 for d in self.drives}
        self.kepercayaan_diri: Dict[str, float] = {
            d: float(self._p("introspeksi_kepercayaan_awal")) for d in self.drives}
        self.kepercayaan_global: float = float(self._p("introspeksi_kepercayaan_awal"))
        self._introspeksi_history: List[Dict[str, Any]] = []  # {tick, drive, actual, perceived, model, error, conf}
        self._meta_history: List[Dict[str, Any]] = []  # {tick, confidence, benar, error}
        self.meta_d: Dict[str, float] = {d: 0.5 for d in self.drives}
        self.meta_d_global: float = 0.5
        self.introspeksi_akurasi: float = 0.0       # Pearson r actual vs perceived
        self.introspeksi_bias_estimasi: float = 0.0 # mean(perceived-actual)
        self.introspeksi_korelasi_per_drive: Dict[str, float] = {d: 0.0 for d in self.drives}
        self.refleksi_count: int = 0
        self._terakhir_refleksi: int = -10000
        self.narasi_diri: List[Dict[str, Any]] = []  # autobiographical self-model
        self._error_monitor: List[Dict[str, Any]] = []  # ACC-like error log
        self.sadar_diri_ticks: int = 0
        self._introspeksi_discrepancy: float = 0.0

        # --- pilar H: kesadaran terasa (perluasan G, konsep 2/5/6) ---
        # felt_state = sensasi tubuh yang dapat dilaporkan; moral_emotions =
        # emosi moral (bersalah/malu/bangga/...); somatic_markers = tubuh
        # menandai nilai; narrative_identity = klaim "aku orang yang...";
        # reality_source_log + doubt_level + confabulation_log = monitoring
        # realitas, keraguan metakognitif, dan pengisian celah ingatan.
        self.felt_state: Dict[str, float] = {k: 0.0 for k in NURANI_FELT_STATES}
        # stempel tick terakhir update_felt benar-benar dijalankan — dipakai
        # Kesadaran untuk tahu apakah felt_state segar (satu sumber kebenaran).
        self._felt_tick: int = -1
        self.moral_emotions: Dict[str, float] = {k: 0.0
                                                 for k in NURANI_MORAL_EMOTIONS}
        self.somatic_markers: List[Dict[str, Any]] = []
        self.narrative_identity: List[Dict[str, Any]] = []
        self.reality_source_log: List[Dict[str, Any]] = []
        self.doubt_level: float = 0.0
        self.confabulation_log: List[Dict[str, Any]] = []
        self._last_inner_speech_tick: int = -10000
        # ORDE NOL — kategori proto yang terkonsolidasi menjadi SENSITIVITAS
        # BARU. Ini bukan drive/emosi baru (DRIVES & EMOSI tetap utuh, agar
        # tidak ada invariant lama yang dilanggar): ia kanal pengamatan di
        # atas keduanya, sehingga NPC peka pada pola yang dulu tak bernama.
        # `{signature: {nama, jenis, kekuatan, jumlah, tick_lahir, klaim}}`.
        self.kategori_proto: Dict[str, Dict[str, Any]] = {}

    # ==================== sakelar & util ====================
    def enabled(self, pillar: str) -> bool:
        """True bila `enable_<pillar>` aktif (flag dibaca ulang tiap panggilan)."""
        return bool(self.params.get("enable_" + pillar, False))

    def any_enabled(self) -> bool:
        return any(self.enabled(p) for p in PILLARS)

    def set_pillars(self, pillars: Optional[Sequence[str]] = None,
                    aktif: bool = True) -> Dict[str, bool]:
        """Nyalakan/matikan pilar; `pillars=None` = semua pilar."""
        pilih = tuple(pillars) if pillars else PILLARS
        for p in pilih:
            if p not in PILLARS:
                raise ValueError(f"pilar NURANI tidak dikenal: {p}")
            self.params["enable_" + p] = bool(aktif)
        return {p: bool(self.params.get("enable_" + p, False)) for p in PILLARS}

    def _p(self, key: str) -> float:
        v = self.params.get(key, NURANI_DEFAULTS[key])
        if isinstance(v, Mapping):
            # parameter per-drive dibaca sebagai skalar: pakai fallback "*"
            v = v.get("*", NURANI_DEFAULTS[key])
        return float(v)

    def _p_drive(self, key: str, drive: str) -> float:
        """Resolusi parameter WATAK: skalar (global) ATAU dict per-drive.

        Format dict: {"keamanan": 0.00001, "*": 0.0008} — kunci "*" adalah
        fallback untuk drive yang tidak disebut; tanpa "*", fallback ke nilai
        NURANI_DEFAULTS. Inilah infrastruktur "viskositas per-drive": laju
        belajar tiap drive bisa berbeda sehingga kepribadian tidak lagi hanya
        'arah' (weights) tetapi juga 'seberapa cepat arah itu bisa dikoreksi'.
        """
        v = self.params.get(key, NURANI_DEFAULTS[key])
        if isinstance(v, Mapping):
            if drive in v:
                return float(v[drive])
            if "*" in v:
                return float(v["*"])
            return float(NURANI_DEFAULTS[key])
        return float(v)

    # ==================== PILAR A — memori afektif ====================
    @staticmethod
    def keywords(text: str) -> Tuple[str, ...]:
        """<=8 kata kunci unik (kata huruf kecil, panjang min 4 = stopword
        pendek terbuang) dari sebuah deskripsi, terurut agar stabil."""
        if not text:
            return ()
        kata = {w for w in re.findall(r"[a-z]{4,}", str(text).lower())}
        return tuple(sorted(kata)[:8])

    def context_signature(self, text: str) -> int:
        """Signature 32-bit sebuah deskripsi (crc32, deterministik antar-proses)."""
        teks = str(text or "")
        sig = self._sig_cache.get(teks)
        if sig is not None:
            return sig
        h = zlib.crc32("|".join(self.keywords(teks)).encode("utf-8")) & 0xFFFFFFFF
        if len(self._sig_cache) > 4096:
            self._sig_cache.clear()
        self._sig_cache[teks] = h
        return h

    def _retention_score(self, item: Mapping[str, Any], kini: int,
                         tick_key: str = "last_t") -> float:
        """Skor retensi: dampak/importance bermakna tahan lebih lama daripada LRU."""
        age = max(0, int(kini) - int(item.get(tick_key, 0)))
        half = max(1.0, self._p("memory_retention_half_life"))
        deltas = item.get("deltas", {}) or {}
        impact = max((abs(float(v)) for v in deltas.values()), default=0.0)
        importance = max(float(item.get("importance", 0.0)), impact)
        count_bonus = min(0.10, 0.02 * math.log1p(max(0, int(item.get("n", 0)))))
        return cast(float, (0.02 + importance + count_bonus) * (0.5 ** (age / half)))

    def _evict_affective(self, kini: int) -> None:
        cap = int(self._p("affective_max"))
        while cap > 0 and len(self._affective) > cap:
            victim = min(self._affective.items(),
                         key=lambda kv: self._retention_score(kv[1], kini))
            self._affective.pop(victim[0], None)
            self.affective_evicted += 1

    def _append_episode_log(self, sig: int, tick: int,
                            deltas: Mapping[str, float], sample: str,
                            count: int = 1) -> None:
        if not bool(self.params.get("enable_episode_log", True)):
            return
        cap = max(0, int(self._p("episode_log_max")))
        if cap <= 0:
            return
        copied = {d: jepit_drive(float(deltas.get(d, 0.0)))
                  for d in self.drives}
        importance = max((abs(v) for v in copied.values()), default=0.0)
        self._episode_log.append({
            "sig": int(sig), "tick": int(tick), "deltas": copied,
            "impact": importance, "importance": importance,
            "sample": str(sample)[:60], "n": max(1, int(count)),
        })
        kini = max([int(tick)] + [int(x.get("tick", tick)) for x in self._episode_log])
        if len(self._episode_log) > cap:
            self._episode_log.sort(
                key=lambda x: self._retention_score(x, kini, "tick"), reverse=True)
            del self._episode_log[cap:]

    @staticmethod
    def _lexical_words(text: str) -> Tuple[str, ...]:
        """Token kata Unicode yang stabil untuk pembelajaran asosiasi kecil."""
        stop = {
            "yang", "dan", "atau", "untuk", "dari", "pada", "dengan", "ini", "itu",
            "akan", "telah", "dalam", "karena", "agar", "oleh", "saat", "jika",
            "the", "and", "or", "for", "from", "with", "this", "that", "was",
            "were", "are", "you", "your", "have", "has", "had", "into", "over",
        }
        seen = set()
        words: List[str] = []
        for word in re.findall(r"[^\W\d_]{3,}", str(text or "").casefold(), flags=re.UNICODE):
            if word in stop or word in seen:
                continue
            seen.add(word)
            words.append(word)
            if len(words) >= 32:
                break
        return tuple(words)

    def _evict_word_delta(self, kini: int) -> None:
        cap = max(0, int(self._p("word_delta_max")))
        while len(self._kata_delta) > cap:
            victim = min(self._kata_delta.items(),
                         key=lambda kv: (self._retention_score(kv[1], kini), kv[0]))
            self._kata_delta.pop(victim[0], None)
            self.kata_delta_evicted += 1

    def _update_word_delta(self, text: str, drive_deltas: Mapping[str, float],
                           tick: int, samples: int = 1) -> None:
        """Perbarui asosiasi tiap kata dengan EMA ber-alpha kecil."""
        words = self._lexical_words(text)
        if not words:
            return
        alpha = jepit_01(self._p("word_delta_alpha"))
        if alpha <= 0.0:
            return
        samples = max(1, int(samples))
        # Setara dengan menerapkan EMA `samples` kali; berguna saat replay
        # menyimpan beberapa pengamatan yang telah digabung menjadi satu baris.
        a = 1.0 - (1.0 - alpha) ** samples
        incoming = {d: jepit_drive(float((drive_deltas or {}).get(d, 0.0)))
                    for d in self.drives}
        importance = max((abs(v) for v in incoming.values()), default=0.0)
        for word in words:
            slot = self._kata_delta.get(word)
            if slot is None:
                slot = self._kata_delta[word] = {
                    "deltas": {d: 0.0 for d in self.drives}, "n": 0,
                    "last_t": int(tick), "importance": 0.0,
                }
            for d in self.drives:
                old = float(slot["deltas"].get(d, 0.0))
                slot["deltas"][d] = old + a * (incoming[d] - old)
            slot["n"] = int(slot.get("n", 0)) + samples
            slot["last_t"] = int(tick)
            slot["importance"] = max(float(slot.get("importance", 0.0)), importance)
        self._evict_word_delta(int(tick))

    def anticipate_words(self, text: str) -> Dict[str, float]:
        """Kontribusi lexicon dinamis kata→drive; nol bila pilar A mati.

        Kata-kata yang cocok digabungkan sebagai rata-rata berbobot bukti,
        lalu diperkecil oleh `word_delta_gain` agar tetap menjadi pengaruh
        minoritas di samping lexicon statis dan model internal lainnya.
        """
        prior = {d: 0.0 for d in self.drives}
        if not self.enabled("affective_memory") or not text:
            return prior
        minimum = max(1, int(self._p("word_delta_min_samples")))
        saturate = max(1.0, self._p("word_delta_saturate"))
        weighted: List[Tuple[Dict[str, float], float]] = []
        for word in self._lexical_words(text):
            slot = self._kata_delta.get(word)
            if not slot or int(slot.get("n", 0)) < minimum:
                continue
            weight = min(1.0, int(slot.get("n", 0)) / saturate)
            if weight > 0.0:
                weighted.append((slot.get("deltas", {}), weight))
        if not weighted:
            return prior
        total_weight = sum(weight for _deltas, weight in weighted)
        gain = jepit_01(self._p("word_delta_gain"))
        for d in self.drives:
            mean = sum(float(deltas.get(d, 0.0)) * weight
                       for deltas, weight in weighted) / total_weight
            prior[d] = gain * mean
        return prior

    def experience(self, text: str, drive_deltas: Mapping[str, float],
                   tick: int = 0) -> bool:
        """Rekam pengalaman: signature dan kata -> running-mean dampak drive.

        Selain running mean, simpan replay ringkas (signature, waktu, dampak)
        agar pola penting dapat dikonsolidasikan kembali lintas sesi.
        """
        if not self.enabled("affective_memory") or not text:
            return False
        sig = self.context_signature(text)
        tick = int(tick)
        slot = self._affective.get(sig)
        if slot is None:
            slot = self._affective[sig] = {
                "deltas": {d: 0.0 for d in self.drives},
                "n": 0, "last_t": tick, "sample": str(text)[:60],
                "importance": 0.0,
            }
        a = 1.0 / (1.0 + slot["n"])          # running mean
        incoming = {}
        for d in self.drives:
            v = jepit_drive(float(drive_deltas.get(d, 0.0))) if drive_deltas else 0.0
            incoming[d] = v
            slot["deltas"][d] += a * (v - slot["deltas"][d])
        slot["n"] += 1
        slot["last_t"] = tick
        slot["importance"] = max(float(slot.get("importance", 0.0)),
                                 max((abs(v) for v in incoming.values()), default=0.0))
        self.experience_count += 1
        self._update_word_delta(str(text), incoming, tick=tick)
        self._append_episode_log(sig, tick, incoming, str(text), count=1)
        self._evict_affective(tick)
        return True

    def warmup_from_log(self, replace: bool = True) -> int:
        """Konsolidasikan ulang replay ringkas menjadi memori afektif.

        `replace=True` membangun ulang slot dari log tersimpan; False menggabungkan
        ke slot aktif. Mengembalikan jumlah entri replay yang diproses.
        """
        if not self._episode_log:
            return 0
        if replace:
            self._affective = {}
            self._kata_delta = {}
            self.kata_delta_evicted = 0
        total_n = 0
        for entry in sorted(self._episode_log, key=lambda x: int(x.get("tick", 0))):
            sig = int(entry.get("sig", 0))
            n = max(1, int(entry.get("n", 1)))
            deltas = entry.get("deltas", {}) or {}
            slot = self._affective.get(sig)
            if slot is None:
                slot = self._affective[sig] = {
                    "deltas": {d: 0.0 for d in self.drives}, "n": 0,
                    "last_t": int(entry.get("tick", 0)),
                    "sample": str(entry.get("sample", ""))[:60],
                    "importance": float(entry.get("importance", entry.get("impact", 0.0))),
                }
            old_n = int(slot.get("n", 0))
            denom = max(1, old_n + n)
            for d in self.drives:
                v = jepit_drive(float(deltas.get(d, 0.0)))
                slot["deltas"][d] += (n / denom) * (v - slot["deltas"][d])
            slot["n"] = old_n + n
            slot["last_t"] = max(int(slot.get("last_t", 0)), int(entry.get("tick", 0)))
            slot["importance"] = max(float(slot.get("importance", 0.0)),
                                     float(entry.get("importance", entry.get("impact", 0.0))))
            self._update_word_delta(str(entry.get("sample", "")), deltas,
                                    tick=int(entry.get("tick", 0)), samples=n)
            total_n += n
        kini = max(int(x.get("tick", 0)) for x in self._episode_log)
        self._evict_affective(kini)
        return len(self._episode_log)

    def anticipate_detail(self, text: str, hitung: bool = True
                          ) -> Tuple[Dict[str, float], Dict[str, float]]:
        """(prior tertimbang kepercayaan, kepercayaan per drive).

        Kepercayaan per drive dibutuhkan PERSEPSI pilar F: blend top-down
        (pemrosesan prediktif) menimbang ekspektasi terhadap bukti sensorik
        menurut reliabilitasnya. prior[d] = trust[d] × delta slot[d].
        `hitung=False` untuk pembacaan tanpa jejak (counter hits tak naik) —
        dipakai API baca-saja `Naluri.persepsi(teks)`.
        """
        prior = {d: 0.0 for d in self.drives}
        trust = {d: 0.0 for d in self.drives}
        if not self.enabled("affective_memory") or not text:
            return prior, trust
        slot = self._affective.get(self.context_signature(text))
        if not slot or slot["n"] < int(self._p("affective_min_samples")):
            return prior, trust
        saturasi = max(1.0, self._p("affective_trust_saturate"))
        # FITUR 1: momen inti menaikkan cap kepercayaan untuk signature-nya.
        core_cap = self._core_cap.get(str(self.context_signature(text)), 0.0)
        for d in self.drives:
            cap = self._p_drive("affective_trust_cap", d)
            if core_cap > 0.0:
                cap = max(cap, core_cap)
            t = min(1.0, slot["n"] / saturasi) * cap
            trust[d] = t
            prior[d] = t * slot["deltas"][d]
        if hitung:
            self.affective_hits += 1
        return prior, trust

    def anticipate(self, text: str) -> Dict[str, float]:
        """Intuisi afektif: prior dampak drive dari pengalaman serupa.

        Kepercayaan naik dengan jumlah sampel dan jenuh di ~10, lalu dibatasi
        `affective_trust_cap` agar tidak pernah menindih lexicon. Cap boleh
        per-drive (WATAK): mis. paranoid {"keamanan": 0.95} — masa lalu
        mendominasi persepsi ancaman, sementara drive lain tetap 0.7.
        """
        return self.anticipate_detail(text)[0]

    def forget_affective(self, max_age: Optional[int] = None,
                         kini: Optional[int] = None) -> int:
        """Prune manual: buang slot yang usianya lewat `max_age` tick.

        Mengembalikan jumlah slot yang dibuang. `max_age=None` memakai
        `affective_max_age` dari params; `kini=None` memakai waktu terakhir
        yang diketahui (tick pemanggil lewat Naluri, atau slot termuda).
        """
        batas = int(self._p("affective_max_age")) if max_age is None else int(max_age)
        if kini is None:
            kini = max((s["last_t"] for s in self._affective.values()), default=0)
        buang = [sig for sig, s in self._affective.items() if kini - s["last_t"] > batas]
        for sig in buang:
            self._affective.pop(sig, None)
        self.affective_forgotten += len(buang)
        return len(buang)

    @property
    def affective_size(self) -> int:
        return len(self._affective)

    # ==================== PILAR B — kalibrasi berlapis ====================
    def record_observation(self, pred_unit: float, real_unit: float,
                           prob: Optional[float] = None,
                           success: Optional[bool] = None,
                           per_drive: Optional[Mapping[str, float]] = None
                           ) -> bool:
        """Catat satu hasil prediksi vs realita untuk rapor kalibrasi.

        pred_unit/real_unit  : prediksi & realita pada skala [-1, +1]
        prob / success       : pasangan (probabilitas, tercapai-tidaknya) untuk Brier
        per_drive            : |galat| per drive (prediksi lexicon vs drive_deltas nyata)
        """
        if not self.enabled("layered_calibration"):
            return False
        alpha = self._p("calibration_report_alpha")
        p01 = 0.5 * (jepit_drive(pred_unit) + 1.0)
        r01 = 0.5 * (jepit_drive(real_unit) + 1.0)
        self._pairs_unit.append((p01, r01))
        if len(self._pairs_unit) > 500:
            self._pairs_unit.pop(0)
        self._errors.append(abs(p01 - r01))
        if len(self._errors) > 64:
            self._errors.pop(0)

        if prob is not None and success is not None:
            b = (jepit_01(float(prob)) - (1.0 if success else 0.0)) ** 2
            self._brier_sum += b
            self._brier_ema = (b if self._brier_n == 0
                               else (1 - alpha) * self._brier_ema + alpha * b)
            self._brier_n += 1
        if per_drive:
            for d, e in per_drive.items():
                if d not in self._drive_err_ema:
                    continue
                e = abs(float(e))
                # WATAK: alpha boleh per-drive — seberapa cepat "rapor diri"
                # per drive direvisi (cendekia cepat, paranoid lambat untuk
                # keamanan).
                alpha_d = self._p_drive("calibration_report_alpha", d)
                if self._drive_err_n[d] == 0:
                    self._drive_err_ema[d] = e
                else:
                    self._drive_err_ema[d] = ((1 - alpha_d) * self._drive_err_ema[d]
                                              + alpha_d * e)
                self._drive_err_n[d] += 1
        return True

    def record_uncertainty(self, epistemic: float, aleatoric: float,
                           tick: Optional[int] = None) -> Dict[str, float]:
        """Terima dua sumber ketidakpastian terpisah (hanya pilar B aktif)."""
        if not self.enabled("layered_calibration"):
            return self.uncertainty_report()
        ep = jepit_01(float(epistemic))
        al = jepit_01(float(aleatoric))
        alpha = jepit_01(self._p("uncertainty_alpha"))
        if self._uncertainty_n == 0:
            self._epistemic_ema, self._aleatoric_ema = ep, al
        else:
            self._epistemic_ema = (1.0 - alpha) * self._epistemic_ema + alpha * ep
            self._aleatoric_ema = (1.0 - alpha) * self._aleatoric_ema + alpha * al
        self._uncertainty_n += 1
        return self.uncertainty_report()

    def uncertainty_report(self) -> Dict[str, Any]:
        """Pisahkan kurang-data dari dunia yang memang berubah-ubah."""
        ep, al = self._epistemic_ema, self._aleatoric_ema
        if ep > al + 0.10:
            policy = "gather_information"
        elif al > ep + 0.10:
            policy = "accept_aleatoric_noise"
        else:
            policy = "balanced"
        return {"epistemic": round(float(ep), 4),
                "aleatoric": round(float(al), 4),
                "n": int(self._uncertainty_n), "policy": policy}

    def calibration_report(self) -> CalibrationReport:
        """Rapor kalibrasi: Brier, EMA galat per drive, dan bin reliability."""
        brier = (self._brier_sum / self._brier_n) if self._brier_n else 0.0
        bins = max(1, int(self._p("reliability_bins")))
        tumpuk: List[List[float]] = [[0.0, 0.0, 0.0] for _ in range(bins)]
        for p01, r01 in self._pairs_unit:
            i = min(bins - 1, int(p01 * bins))
            tumpuk[i][0] += p01
            tumpuk[i][1] += r01
            tumpuk[i][2] += 1.0
        reliability = [(t[0] / t[2], t[1] / t[2], int(t[2]))
                       for t in tumpuk if t[2] > 0]
        per_drive = {d: self._drive_err_ema[d] for d in self.drives
                     if self._drive_err_n[d] > 0}
        return CalibrationReport(brier=brier, brier_ema=self._brier_ema,
                                 per_drive_ema=per_drive,
                                 reliability=reliability,
                                 n_samples=self._brier_n)

    def recent_spike(self, ambang: Optional[float] = None) -> float:
        """Galat maksimum pada jendela observasi terakhir (0 bila tak ada).

        Membedakan "salah besar beberapa kali terakhir" (spike -> tidur) dari
        "salah sedang terus-menerus" (EMA tinggi, tapi tanpa spike).
        """
        batas = self._p("sleep_spike_error") if ambang is None else float(ambang)
        jendela = max(1, int(self._p("sleep_spike_window")))
        if not self._errors:
            return 0.0
        puncak = max(self._errors[-jendela:])
        return puncak if puncak > batas else 0.0

    @staticmethod
    def _rasio(pairs: Sequence[Tuple[float, float]]) -> Optional[float]:
        """Rasio rata-rata |realita| / |prediksi| (lantai 0.05 anti-ledakan)."""
        pakai = [(abs(p), abs(r)) for p, r in pairs
                 if abs(p) > 0.05 and abs(r) > 0.05]
        if len(pakai) < 5:
            return None
        mean_pred = sum(p for p, _ in pakai) / len(pakai)
        mean_real = sum(r for _, r in pakai) / len(pakai)
        if mean_pred < 1e-9:
            return None
        return mean_real / mean_pred

    @staticmethod
    def holdout_brier(pairs: Sequence[Tuple[float, float]], scale: float) -> float:
        """Kesalahan kuadratik rata-rata (gaya Brier, di [0, 1]) pada hold-out.

        Prediksi diskala lalu dinormalisasi ke [0, 1] bersama realita; makin
        kecil berarti skala itu makin jujur.
        """
        if not pairs:
            return 0.0
        tot = 0.0
        for p, r in pairs:
            p01 = 0.5 * (math.tanh(float(p) * float(scale)) + 1.0)
            r01 = 0.5 * (jepit_drive(float(r)) + 1.0)
            tot += (p01 - r01) ** 2
        return tot / len(pairs)

    def scale_from_holdout(self, pairs: Sequence[Tuple[float, float]],
                           current_scale: float) -> Tuple[float, bool, float, float]:
        """Usulkan skala baru dari 80% pertama, terima hanya bila 20% sisanya membaik.

        Mengembalikan (skala_akhir, diterima, brier_sebelum, brier_sesudah).
        Update yang tidak lolos validasi DITOLAK — ini penangkal drift yang
        tidak membawa perbaikan nyata pada rasio mentah lama.
        """
        minimum = int(self._p("scale_holdout_min_pairs"))
        if len(pairs) < minimum:
            return current_scale, False, 0.0, 0.0
        jendela = int(self._p("scale_holdout_window"))
        recent = list(pairs[-jendela:]) if jendela > 0 else list(pairs)
        split = int(len(recent) * jepit(self._p("scale_holdout_fraction"), 0.5, 0.99))
        latih, hold = recent[:split], recent[split:]
        if not hold or not latih:
            return current_scale, False, 0.0, 0.0
        rasio = self._rasio(latih)
        if rasio is None:
            return current_scale, False, 0.0, 0.0
        floor = float(self.params.get("scale_floor", 0.1))
        ceiling = float(self.params.get("scale_ceiling", 20.0))
        usul = jepit(current_scale * rasio, floor, ceiling)
        sebelum = self.holdout_brier(hold, current_scale)
        sesudah = self.holdout_brier(hold, usul)
        diterima = (sesudah < sebelum - self._p("scale_holdout_min_gain")
                    and usul != current_scale)
        self.last_holdout = (sebelum, sesudah)
        if diterima:
            self.scale_accepted += 1
            return usul, True, sebelum, sesudah
        self.scale_rejected += 1
        return current_scale, False, sebelum, sesudah

    # ==================== PILAR C — setpoint & interosepsi ====================
    def update_setpoints(self, levels: Mapping[str, float]) -> None:
        """Setpoint mengejar rata-rata level historis (habituasi homeostatis).

        WATAK per-drive: `setpoint_lr` dan `setpoint_clamp` boleh dict
        {drive: nilai}. Di sinilah "paranoid" yang sesungguhnya hidup —
        lr keamanan ~0 berarti ekspektasi amannya TIDAK PERNAH direvisi oleh
        pengalaman aman; clamp lebar berarti keyakinannya boleh ekstrem.
        """
        if not self.enabled("plastic_setpoints"):
            return
        for d in self.drives:
            lr = self._p_drive("setpoint_lr", d)
            clamp = self._p_drive("setpoint_clamp", d)
            level = float(levels.get(d, 0.0))
            baru = self.setpoints[d] + lr * (level - self.setpoints[d])
            self.setpoints[d] = max(-clamp, min(clamp, baru))

    def relative_deficit(self, drive: str, level: float) -> float:
        """Defisit dihitung terhadap setpoint, bukan terhadap nol."""
        return max(0.0, self.setpoints.get(drive, 0.0) - float(level))

    def update_interoception(self, deficits: Mapping[str, float], tick: int) -> None:
        """Belajar korelasi defisit: 'kalika energiku turun, koherensiku ikut?'"""
        if not self.enabled("interoception"):
            return
        self.advance_perception_tick(int(tick))
        if int(tick) % max(1, int(self._p("interoception_period"))) != 0:
            return
        gate = self._p("interoception_gate")
        for di in self.drives:
            if float(deficits.get(di, 0.0)) <= gate:
                continue
            if di in self._sensitivitas_instabil:
                continue
            i = self._index[di]
            for dj in self.drives:
                if di == dj or dj in self._sensitivitas_instabil:
                    continue
                j = self._index[dj]
                # WATAK: lr per-drive TARGET (kolom) — seberapa cepat drive dj
                # "belajar" beresonansi dengan defisit drive lain.
                lr = self._p_drive("interoception_lr", dj)
                self.interoception[i][j] += lr * (float(deficits.get(dj, 0.0))
                                                  - self.interoception[i][j])
        # regularisasi anti-loop: lupakan sebagian menuju nol secara berkala
        period = max(1, int(self._p("interoception_decay_period")))
        if int(tick) % period == 0:
            sisa = 1.0 - self._p("interoception_decay")
            for baris in self.interoception:
                for k in range(len(baris)):
                    baris[k] *= sisa

    def structural_surprise(self, surprise: float,
                            galat_per_drive: Mapping[str, float],
                            tick: int = 0) -> Optional[Dict[str, Any]]:
        """Batalkan hipotesis interoseptif saat model salah secara struktural.

        Baris dan kolom kanal paling terkait dinolkan sekaligus. Itu adalah
        invalidasi model, bukan langkah gradient. d' kanal tersebut kemudian
        berosilasi deterministik selama beberapa tick sebelum stabil lagi.
        """
        threshold = (self._p("sleep_spike_error")
                     * self._p("structural_surprise_multiplier"))
        if float(surprise) <= threshold:
            return None
        errors = {d: abs(float((galat_per_drive or {}).get(d, 0.0)))
                  for d in self.drives}
        puncak = max(errors.values(), default=0.0)
        if puncak <= 1e-12:
            kanal = [max(self.drives, key=lambda d: sum(
                abs(self.interoception[self._index[d]][j])
                + abs(self.interoception[j][self._index[d]])
                for j in range(len(self.drives))))]
        else:
            kanal = [d for d, e in errors.items() if e >= max(0.25, puncak * 0.75)]
            if not kanal:
                kanal = [max(errors, key=lambda drive: errors[drive])]
        dibatalkan = 0
        sampai = int(tick) + max(2, int(self._p("structural_shock_ticks")))
        for drive in kanal:
            i = self._index[drive]
            for j in range(len(self.drives)):
                if self.interoception[i][j] != 0.0:
                    dibatalkan += 1
                if self.interoception[j][i] != 0.0 and j != i:
                    dibatalkan += 1
                self.interoception[i][j] = 0.0
                self.interoception[j][i] = 0.0
            self._sensitivitas_instabil[drive] = {
                "mulai": int(tick), "sampai": sampai,
                "shock": float(surprise)}
        entri = {"tick": int(tick), "surprise": round(float(surprise), 6),
                 "ambang": round(threshold, 6), "kanal": list(kanal),
                 "kopling_dibatalkan": dibatalkan,
                 "tidak_stabil_sampai": sampai}
        self._structural_shocks.append(entri)
        self._structural_shocks = self._structural_shocks[-64:]
        return dict(entri)

    def advance_perception_tick(self, tick: int) -> None:
        self._perception_tick = int(tick)
        self._sensitivitas_instabil = {
            d: dict(v) for d, v in self._sensitivitas_instabil.items()
            if int(v.get("sampai", -1)) >= self._perception_tick}

    def interoceptive_echo(self, deficits: Mapping[str, float], drive: str) -> float:
        """Gema antar-drive untuk menambah urgensi (0.0 bila pilar mati).

        WATAK: `interoception_echo` boleh per-drive penerima — mis. paranoid
        {"keamanan": 0.3}: kecemasan drive lain lebih keras bergema ke rasa
        tidak amannya.
        """
        if not self.enabled("interoception") or drive not in self._index:
            return 0.0
        j = self._index[drive]
        tot = 0.0
        for di in self.drives:
            if di == drive:
                continue
            tot += self.interoception[self._index[di]][j] * float(deficits.get(di, 0.0))
        return self._p_drive("interoception_echo", drive) * tot

    # ==================== PILAR D — konflik, ritme, flow ====================
    def circadian_phase(self, tick: int) -> str:
        """Fase sirkadian: satu 'hari' = `circadian_period` tick."""
        period = max(4, int(self._p("circadian_period")))
        p = int(tick) % period
        per_fase = period / 4.0
        return FASE[min(3, int(p / per_fase))]

    def night_energy_shift(self, tick: int) -> float:
        """Besar NAIKNYA ambang energi pada fase malam (0.0 di fase lain).

        Malam tidak memaksa tidur — hanya mempersempit ambang, sehingga tidur
        menjadi preventif (ritmis) dan tetap menghormati refraktori.
        """
        if not self.enabled("circadian"):
            return 0.0
        return self._p("circadian_night_shift") if self.circadian_phase(tick) == "malam" else 0.0

    @staticmethod
    def _efek(c: Any) -> Dict[str, float]:
        if isinstance(c, dict):
            return dict(c.get("drive_effects", {}) or {})
        return dict(getattr(c, "drive_effects", {}) or {})

    @staticmethod
    def _urgensi(goal: Any) -> float:
        u = goal.get("urgency") if isinstance(goal, dict) else getattr(goal, "urgency", 0.0)
        try:
            return float(u or 0.0)
        except (TypeError, ValueError):
            return 0.0

    @staticmethod
    def _drive(goal: Any) -> str:
        d = goal.get("drive") if isinstance(goal, dict) else getattr(goal, "drive", "")
        return str(d or "")

    def detect_conflict(self, goals: Sequence[Any],
                        candidates: Sequence[Any]) -> Dict[str, Any]:
        """Konflik = dua goal berurgensi tinggi YANG EFFECT-nya berlawanan tanda.

        Mengembalikan dict diagnostik {ada, drive, urgensi, penjelasan,
        kandidat_didua} — dipakai `choose_action()` untuk memutuskan apakah
        weighted-sum linear harus diganti lexicographic + bonus kompromi.
        """
        hasil: Dict[str, Any] = {"ada": False, "drive": None, "urgensi": None,
                                 "penjelasan": "tidak ada konflik",
                                 "kandidat_didua": 0}
        aktif = [g for g in goals if self._urgensi(g) > self._p("conflict_urgency_gate")]
        if len(aktif) < 2:
            hasil["penjelasan"] = (f"goal berurgensi tinggi hanya {len(aktif)}"
                                   f" (perlu 2, gerbang {self._p('conflict_urgency_gate'):.2f})")
            return hasil
        d1, d2 = self._drive(aktif[0]), self._drive(aktif[1])
        eps = self._p("conflict_sign_eps")

        def tanda(g: Any, c: Any) -> float:
            return float(self._efek(c).get(g, 0.0))

        plus = any(tanda(d1, c) > eps and tanda(d2, c) < -eps for c in candidates)
        minus = any(tanda(d1, c) < -eps and tanda(d2, c) > eps for c in candidates)
        both = sum(1 for c in candidates
                   if tanda(d1, c) > eps and tanda(d2, c) > eps)
        if not (plus and minus):
            hasil["penjelasan"] = f"drive {d1} vs {d2} tinggi, tapi kandidat tidak berlawanan tanda"
            return hasil
        hasil.update({
            "ada": True, "drive": (d1, d2),
            "urgensi": (self._urgensi(aktif[0]), self._urgensi(aktif[1])),
            "kandidat_didua": both,
            "penjelasan": (f"{d1} (urg {self._urgensi(aktif[0]):.2f}) vs "
                           f"{d2} (urg {self._urgensi(aktif[1]):.2f}) saling "
                           f"meniadakan pada weighted-sum"),
        })
        return hasil

    def compromise_bonus(self, effects: Mapping[str, float],
                         d1: str, d2: str) -> float:
        """Bonus untuk aksi yang menggerakkan KEDUA drive konflik ke arah positif."""
        e1 = float(effects.get(d1, 0.0) or 0.0)
        e2 = float(effects.get(d2, 0.0) or 0.0)
        if e1 > 0.0 and e2 > 0.0:
            return self._p("compromise_bonus") * min(e1, e2)
        return 0.0

    def note_conflict(self, det: Mapping[str, Any], resolved: bool,
                      tick: int = 0) -> None:
        """Catat bahwa satu keputusan melewati jalur resolusi konflik."""
        if det.get("ada"):
            self.conflict_ticks += 1
            self._last_conflict_tick = int(tick)
            dr = det.get("drive")
            if dr and list(dr) != self.conflict_drives:
                self.conflict_drives = list(dr)
            if resolved:
                self.conflict_resolved += 1

    def flow_state(self, valence: float, arousal: float) -> bool:
        """Keadaan terserap: valensi positif cukup tinggi, gairah tetap rendah."""
        return (float(valence) > self._p("flow_valence_min")
                and float(arousal) < self._p("flow_arousal_max"))

    def flow_reward_bonus(self, valence: float, arousal: float) -> float:
        """Reward intrinsik tambahan saat flow (0.0 bila pilar mati)."""
        if not self.enabled("flow_state"):
            return 0.0
        if self.flow_state(valence, arousal):
            self.flow_ticks += 1
            return self._p("flow_reward_bonus")
        return 0.0

    # ==================== PILAR E — memori sosial (EMPATI) ====================
    @staticmethod
    def _eid(ent: Any) -> str:
        """ID entitas yang stabil & JSON-safe (pemain, NPC lain, faksi...)."""
        return str(ent)

    def _netral(self, ent: Any) -> Dict[str, Any]:
        return {"id": self._eid(ent), "nama": "", "valensi": 0.0,
                "kepercayaan": 0.0, "akrab": 0.0, "n": 0, "last_t": 0,
                "dikenal": False, "utang": []}

    def meet(self, ent: Any, nama: Optional[str] = None, tick: int = 0) -> Dict[str, Any]:
        """Daftar/kenal satu entitas. Mengembalikan snapshot relasinya.

        No-op netral bila pilar E mati — pemanggil tidak perlu mengecek flag.
        """
        if not self.enabled("social_memory"):
            return self._netral(ent)
        eid = self._eid(ent)
        slot = self._entitas.get(eid)
        if slot is None:
            slot = self._entitas[eid] = {
                "nama": str(nama or ""), "valensi": 0.0, "kepercayaan": 0.0,
                "akrab": 0.0, "n": 0, "last_t": int(tick), "utang": []}
        elif nama and not slot["nama"]:
            slot["nama"] = str(nama)
        return self.relationship(ent)

    def relationship(self, ent: Any) -> Dict[str, Any]:
        """Snapshot relasi satu entitas (netral & dikenal=False bila tak ada)."""
        slot = self._entitas.get(self._eid(ent))
        if slot is None:
            return self._netral(ent)
        return {"id": self._eid(ent), "nama": slot["nama"],
                "valensi": float(slot["valensi"]),
                "kepercayaan": float(slot["kepercayaan"]),
                "akrab": float(slot["akrab"]), "n": int(slot["n"]),
                "last_t": int(slot["last_t"]), "dikenal": True,
                "hancur": bool(slot.get("hancur", False)),
                "berat_utang": round(self._berat_utang_slot(slot), 3),
                "utang_belum_selesai": [dict(u) for u in slot.get("utang", [])
                                        if not u.get("dibayar")],
                "menarik_diri": self._menarik_diri_slot(slot)}

    def break_trust(self, ent: Any, severity: float = 0.7, tick: int = 0,
                    nama: Optional[str] = None) -> Dict[str, Any]:
        """Hancurkan kepercayaan secara LANGKAH (bukan inkremental).

        Pengkhianatan/serangan mematahkan kepercayaan sekaligus, tidak
        menggerusnya perlahan. Setelah ini `social_trust_recovery_penalty`
        membuat pemulihannya sangat lambat — asimetri yang dirasakan Player.
        """
        if not self.enabled("social_memory"):
            return self._netral(ent)
        eid = self._eid(ent)
        slot = self._entitas.get(eid)
        if slot is None:
            self.meet(ent, nama=nama, tick=tick)
            slot = self._entitas[eid]
        sev = jepit_01(abs(float(severity)))
        slot["kepercayaan"] = -sev
        slot["valensi"] = min(float(slot["valensi"]), -sev)
        slot["hancur"] = True
        slot["n"] = int(slot["n"]) + 1
        slot["last_t"] = int(tick)
        return self.relationship(ent)

    # ==================== FITUR 4: UTANG EMOSIONAL ====================
    def _berat_utang_slot(self, slot: Mapping[str, Any]) -> float:
        return sum(max(0.0, float(u.get("bobot", 1.0)))
                   for u in (slot.get("utang") or [])
                   if not u.get("dibayar"))

    def _menarik_diri_slot(self, slot: Mapping[str, Any]) -> bool:
        ambang = max(1e-6, self._p("social_utang_ambang"))
        return self._berat_utang_slot(slot) >= ambang

    def tambah_utang(self, ent: Any, isi: str, bobot: float = 1.0,
                     jenis: str = "janji", tick: int = 0,
                     nama: Optional[str] = None) -> Dict[str, Any]:
        """Catat utang emosional: janji/permintaan/kepercayaan yang belum ditepati."""
        if not self.enabled("social_memory"):
            return {}
        eid = self._eid(ent)
        slot = self._entitas.get(eid)
        if slot is None:
            self.meet(ent, nama=nama, tick=tick)
            slot = self._entitas[eid]
        item = {"tick": int(tick), "jenis": str(jenis)[:24],
                "isi": str(isi)[:100], "bobot": round(max(0.0, float(bobot)), 3),
                "dibayar": False}
        slot.setdefault("utang", []).append(item)
        if len(slot["utang"]) > 32:
            slot["utang"] = slot["utang"][-32:]
        return {"entitas": eid, "utang": dict(item),
                "berat": round(self._berat_utang_slot(slot), 3),
                "menarik_diri": self._menarik_diri_slot(slot)}

    def bayar_utang(self, ent: Any, isi: Optional[str] = None,
                    tick: int = 0) -> int:
        """Tepati utang (semua bila `isi=None`); kembalikan jumlah yang dibayar."""
        slot = self._entitas.get(self._eid(ent))
        if not slot:
            return 0
        n = 0
        for u in slot.get("utang", []):
            if u.get("dibayar"):
                continue
            if isi is None or str(isi)[:60].lower() in str(u.get("isi", "")).lower():
                u["dibayar"] = True
                u["dibayar_tick"] = int(tick)
                n += 1
        slot["utang"] = [u for u in slot.get("utang", []) if not u.get("dibayar")]
        return n

    def berat_utang(self, ent: Any) -> float:
        slot = self._entitas.get(self._eid(ent))
        return round(self._berat_utang_slot(slot), 3) if slot else 0.0

    def menarik_diri(self, ent: Any) -> bool:
        """True bila beban utang melewati ambang: "aku tidak mau lagi percaya"."""
        slot = self._entitas.get(self._eid(ent))
        return slot is not None and bool(slot) and self._menarik_diri_slot(slot)

    def utang_state(self, ent: Optional[Any] = None) -> Dict[str, Any]:
        if ent is not None:
            slot = self._entitas.get(self._eid(ent))
            return {"entitas": self._eid(ent),
                    "berat": round(self._berat_utang_slot(slot), 3) if slot else 0.0,
                    "menarik_diri": slot is not None and bool(slot) and self._menarik_diri_slot(slot),
                    "daftar": [dict(u) for u in (slot.get("utang") or [])
                               if not u.get("dibayar")] if slot else []}
        return {eid: {"berat": round(self._berat_utang_slot(s), 3),
                      "menarik_diri": self._menarik_diri_slot(s),
                      "n": len([u for u in (s.get("utang") or [])
                                if not u.get("dibayar")])}
                for eid, s in self._entitas.items()
                if self._berat_utang_slot(s) > 0.0}

    # ==================== FITUR 1: CORE MEMORY CAP ====================
    def tandai_core(self, text: str, cap: Optional[float] = None) -> Dict[str, Any]:
        """Naikkan cap kepercayaan khusus untuk signature sebuah momen inti.

        Ini yang membuat satu momen bisa MENDOMINASI rata-rata: interpretasi
        pengalaman baru yang mirip momen itu ditimbang dengan kepercayaan
        tinggi (cap naik), sehingga NPC "membaca" dunia lewat luka lamanya.
        """
        sig = self.context_signature(text)
        cap_val = (self._p("core_memory_cap") if cap is None
                   else jepit_01(float(cap)))
        self._core_cap[str(sig)] = cap_val
        return {"signature": str(sig), "cap": round(cap_val, 3),
                "kata": list(self.keywords(text))}

    def core_cap_state(self) -> Dict[str, Any]:
        return {"n": len(self._core_cap),
                "signature": {k: round(v, 3) for k, v in self._core_cap.items()}}

    def trust_recovery_factor(self, ent: Any) -> float:
        """Pengali efektif pemulihan kepercayaan entitas (1.0 = normal).

        < 1.0 berarti pemulihan diperlambat (asimetri): makin rusak
        kepercayaan, makin kecil nilainya. Untuk HUD/dialog.
        """
        slot = self._entitas.get(self._eid(ent))
        if not slot:
            return 1.0
        trust_now = float(slot.get("kepercayaan", 0.0))
        if trust_now >= 0.0:
            return 1.0
        ambang = max(1e-6, abs(self._p("social_trust_crash_threshold")))
        keparahan = min(1.0, abs(trust_now) / ambang)
        return 1.0 / (1.0 + max(0.0, self._p(
            "social_trust_recovery_penalty")) * keparahan)

    def interact(self, ent: Any, muatan: float = 0.0,
                 kepercayaan_delta: float = 0.0, tick: int = 0,
                 nama: Optional[str] = None) -> Dict[str, Any]:
        """Catat satu interaksi sosial; kembalikan relasi sesudahnya.

        `muatan`  : valensi emosional interaksi, kira-kira [-1, +1]
                    (obrolan hangat +, dihina/pengalaman buruk −).
        `kepercayaan_delta` : perubahan kepercayaan (menepati janji +,
                    berkhianat −). Kepercayaan bergerak LEBIH LAMBAT dari
                    valensi (social_trust_lr < social_valensi_lr) — seperti
                    kepercayaan nyata: cepat goyah, lambat pulih bila
                    desainer memberi muatan asimetris.
        Pembaruan memakai soft-clamp (langkah menyusut dekat ±1) + clamp keras,
        dan keakraban naik asimtotik menuju 1 per interaksi.
        """
        if not self.enabled("social_memory"):
            return self._netral(ent)
        eid = self._eid(ent)
        slot = self._entitas.get(eid)
        if slot is None:
            self.meet(ent, nama=nama, tick=tick)
            slot = self._entitas[eid]
        elif nama and not slot["nama"]:
            slot["nama"] = str(nama)
        lv = self._p("social_valensi_lr")
        lt = self._p("social_trust_lr")
        lf = self._p("social_familiarity_lr")
        # WATAK: konsolidasi per-ENTITAS — plastisitas efektif menyusut
        # seiring jumlah interaksi (lr / (1 + c*n)). Inilah jawaban "satu
        # angka untuk semua orang": viskositas relasi menjadi properti yang
        # TUMBUH per entitas. c=0 (default) = perilaku lama persis.
        # FITUR 4: utang emosional mengurangi kekuatan interaksi positif.
        # Semakin banyak janji yang belum ditepati, semakin NPC "menahan diri".
        berat = self._berat_utang_slot(slot)
        if float(muatan) > 0.0:
            penalti = 1.0 / (1.0 + max(0.0, self._p(
                "social_utang_prior_penalty")) * berat)
            if self._menarik_diri_slot(slot):
                penalti *= max(0.0, self._p("social_utang_withdraw_mult"))
            muatan = float(muatan) * penalti
        if float(kepercayaan_delta) > 0.0:
            penalti_t = 1.0 / (1.0 + max(0.0, self._p(
                "social_utang_prior_penalty")) * berat)
            if self._menarik_diri_slot(slot):
                penalti_t *= max(0.0, self._p("social_utang_withdraw_mult"))
            kepercayaan_delta = float(kepercayaan_delta) * penalti_t
        konsol = max(0.0, self._p("social_consolidation"))
        if konsol > 0.0:
            faktor = 1.0 / (1.0 + konsol * int(slot["n"]))
            lv *= faktor
            lt *= faktor
        # ASIMETRI PEMULIHAN (viskositas relasi): kepercayaan yang sudah rusak
        # (negatif) dipulihkan jauh lebih lambat daripada kehancurannya.
        lt_repair = lt
        trust_now = float(slot["kepercayaan"])
        if float(kepercayaan_delta) > 0.0 and trust_now < 0.0:
            ambang = max(1e-6, abs(self._p("social_trust_crash_threshold")))
            keparahan = min(1.0, abs(trust_now) / ambang)
            lt_repair = lt / (1.0 + max(0.0, self._p(
                "social_trust_recovery_penalty")) * keparahan)
            batas = self._p("social_trust_recovery_cap")
            if batas > 0.0:
                lt_repair = min(lt_repair, batas)
            slot["hancur"] = True
        elif trust_now >= 0.0:
            slot["hancur"] = False
        v = float(slot["valensi"]) + lv * float(muatan) * (1.0 - abs(slot["valensi"]))
        t = (float(slot["kepercayaan"]) + lt_repair * float(kepercayaan_delta)
             * (1.0 - abs(slot["kepercayaan"])))
        slot["valensi"] = jepit_drive(v)
        slot["kepercayaan"] = jepit_drive(t)
        slot["akrab"] = jepit_01(slot["akrab"] + (1.0 - slot["akrab"]) * lf)
        slot["n"] += 1
        slot["last_t"] = int(tick)
        self._last_social_tick = int(tick)
        self.social_interactions += 1
        # LRU: buang entitas paling lama tak disentuh bila kapasitas penuh
        cap = int(self._p("social_max"))
        if cap > 0 and len(self._entitas) > cap:
            half = max(1.0, self._p("memory_retention_half_life"))
            def retensi(kv: Tuple[str, Dict[str, Any]]) -> float:
                slot2 = kv[1]
                age = max(0, int(tick) - int(slot2.get("last_t", 0)))
                relasi = (abs(float(slot2.get("valensi", 0.0)))
                          + abs(float(slot2.get("kepercayaan", 0.0)))
                          + 0.25 * float(slot2.get("akrab", 0.0)))
                frekuensi = min(0.10, 0.02 * math.log1p(int(slot2.get("n", 0))))
                return cast(float, (0.03 + relasi + frekuensi) * (0.5 ** (age / half)))
            lama = min(self._entitas.items(), key=retensi)
            self._entitas.pop(lama[0], None)
            self.social_evicted += 1
        return self.relationship(ent)

    def social_prior(self, ent: Any) -> Dict[str, float]:
        """Bias drive dari relasi: {afiliasi: ±, keamanan: ±} ({} bila netral).

        Dipakai `choose_action()` untuk kandidat ber-`target`: berinteraksi
        dengan entitas yang disukai & akrab terasa lebih mengenyangkan
        afiliasi; entitas tepercaya menenangkan keamanan; yang tidak
        tepercaya menggerusnya.
        """
        if not self.enabled("social_memory"):
            return {}
        slot = self._entitas.get(self._eid(ent))
        if not slot or slot["n"] < 1:
            return {}
        # WATAK: bobot prior boleh per-drive — mis. "dingin"
        # {"afiliasi": 0.05, "keamanan": 0.25}: relasi hanya dipakai untuk
        # kalkulasi aman/tidak-aman, bukan untuk kehangatan sosial.
        afiliasi = (self._p_drive("social_prior_weight", "afiliasi")
                    * float(slot["valensi"]) * (0.4 + 0.6 * float(slot["akrab"])))
        keamanan = (0.8 * self._p_drive("social_prior_weight", "keamanan")
                    * float(slot["kepercayaan"]))
        # FITUR 4: utang emosional menekan prior secara PROPORSIONAL — bukan
        # hanya lewat valensi. Pada ambang, NPC menarik diri secara aktif.
        berat = self._berat_utang_slot(slot)
        if berat > 0.0:
            redam = 1.0 / (1.0 + max(0.0, self._p(
                "social_utang_prior_penalty")) * berat)
            afiliasi *= redam
            keamanan *= redam
        if self._menarik_diri_slot(slot):
            afiliasi = -abs(afiliasi) - 0.15
            keamanan = -abs(keamanan) - 0.1
        prior: Dict[str, float] = {}
        if abs(afiliasi) > 1e-6:
            prior["afiliasi"] = afiliasi
        if abs(keamanan) > 1e-6:
            prior["keamanan"] = keamanan
        return prior

    def set_kacamata_sosial(self, drive: str, bias: float,
                             kekakuan: float = 1.0) -> Dict[str, Any]:
        """Tetapkan lensa proyeksi laten untuk satu drive ToM."""
        if drive not in self.drives:
            raise ValueError(f"drive tidak dikenal: {drive!r}")
        self._kacamata_sosial[drive] = {
            "bias": jepit_drive(float(bias)),
            "kekakuan": jepit_01(float(kekakuan)),
            "bukti_lawan": 0, "observasi": 0}
        return dict(self._kacamata_sosial[drive])

    def kacamata_sosial_state(self) -> Dict[str, Dict[str, Any]]:
        return {d: dict(v) for d, v in self._kacamata_sosial.items()
                if abs(float(v.get("bias", 0.0))) > 1e-12}

    def observe_other_belief(self, other_id: Any, drive: str, value: float,
                            confidence: float = 0.35, tick: int = 0
                            ) -> Dict[str, Any]:
        """Simpan petunjuk tentang keyakinan pihak lain (model ToM sederhana).

        Nilai yang masuk adalah inferensi dari perilaku/reaksi sosial, bukan
        akses langsung ke pikiran NPC lain. Update confidence-weighted agar
        satu sinyal ambigu tidak menghapus observasi berulang.
        """
        if drive not in self.drives:
            raise ValueError(f"drive tidak dikenal: {drive!r}")
        eid = self._eid(other_id)
        slot = self._other_beliefs.setdefault(eid, {})
        item = slot.get(drive)
        obs = jepit_drive(float(value))
        conf = jepit_01(float(confidence))
        lensa = self._kacamata_sosial[drive]
        lensa["observasi"] = int(lensa.get("observasi", 0)) + 1
        bias_lensa = float(lensa.get("bias", 0.0))
        if abs(bias_lensa) > 1e-12 and bias_lensa * obs < -0.02 and conf >= 0.20:
            lensa["bukti_lawan"] = int(lensa.get("bukti_lawan", 0)) + 1
            sesudah = int(self._p("tom_glasses_relax_after"))
            if lensa["bukti_lawan"] > sesudah:
                horizon = max(1.0, self._p("tom_glasses_relax_examples"))
                lensa["kekakuan"] = max(0.0, float(lensa.get("kekakuan", 1.0))
                                                * (1.0 - conf / horizon))
        lr = jepit_01(self._p("tom_belief_lr")) * max(0.1, conf)
        if item is None:
            item = {"value": obs, "confidence": conf, "n": 1,
                    "last_t": int(tick)}
            slot[drive] = item
        else:
            item["value"] = jepit_drive(float(item.get("value", 0.0)) + lr * (obs - float(item.get("value", 0.0))))
            item["confidence"] = jepit_01(float(item.get("confidence", 0.0)) + 0.25 * conf *
                (1.0 - float(item.get("confidence", 0.0))))
            item["n"] = int(item.get("n", 0)) + 1
            item["last_t"] = int(tick)
        limit = max(1, int(self._p("tom_max_entities")))
        if len(self._other_beliefs) > limit:
            oldest = min(self._other_beliefs, key=lambda k: max(
                (int(v.get("last_t", 0)) for v in self._other_beliefs[k].values()), default=0))
            self._other_beliefs.pop(oldest, None)
        return self.estimate_other_belief(other_id, drive)

    def estimate_other_belief(self, other_id: Any, drive: str) -> Dict[str, Any]:
        """Estimasi keyakinan pihak lain dengan prior false-consensus yang lemah.

        Jika bukti langsung minim, hubungan ego (keakraban/kepercayaan/valensi)
        memberi prior kesamaan kecil; observasi perilaku mendapat bobot utama.
        """
        if drive not in self.drives:
            raise ValueError(f"drive tidak dikenal: {drive!r}")
        eid = self._eid(other_id)
        observed = self._other_beliefs.get(eid, {}).get(drive)
        relation = self._entitas.get(eid, {})
        if drive == "afiliasi":
            proxy = float(relation.get("valensi", 0.0))
        elif drive == "keamanan":
            proxy = float(relation.get("kepercayaan", 0.0))
        else:
            proxy = float(relation.get("valensi", 0.0)) * 0.5
        prior_weight = jepit(self._p("tom_similarity_prior"), 0.0, 0.5)
        prior = jepit_drive(proxy * prior_weight)
        lensa = self._kacamata_sosial[drive]
        proyeksi = (float(lensa.get("bias", 0.0))
                    * float(lensa.get("kekakuan", 1.0)))
        if observed is None:
            value = prior + proyeksi
            return {"other_id": eid, "drive": drive,
                    "estimate": jepit_drive(value),
                    "confidence": max(0.10 if relation else 0.0,
                                      0.15 * abs(proyeksi)),
                    "basis": "projected_through_social_glasses",
                    "n": 0, "projection_bias": proyeksi}
        conf = jepit_01(float(observed.get("confidence", 0.0)))
        value = (conf * float(observed.get("value", 0.0))
                 + (1.0 - conf) * prior + proyeksi)
        return {"other_id": eid, "drive": drive,
                "estimate": jepit_drive(value),
                "confidence": conf, "basis": "observed_through_social_glasses",
                "n": int(observed.get("n", 0)),
                "projection_bias": proyeksi}

    def decay_social(self, tick: int) -> None:
        """Lupa sosial berkala: akrab/valensi/kepercayaan meluruh ke netral.

        Dipanggil dari Naluri._physics; digate `social_decay_period` sendiri
        sehingga aman dipanggil tiap tick (dan LOD-agnostic).
        """
        if not self.enabled("social_memory") or not self._entitas:
            return
        period = max(1, int(self._p("social_decay_period")))
        if int(tick) % period != 0:
            return
        sisa = 1.0 - self._p("social_decay")
        for slot in self._entitas.values():
            slot["akrab"] *= sisa
            slot["valensi"] *= (1.0 - 0.5 * self._p("social_decay"))
            slot["kepercayaan"] *= (1.0 - 0.5 * self._p("social_decay"))

    def forget_social(self, max_age: Optional[int] = None,
                      kini: Optional[int] = None) -> int:
        """Prune manual entitas yang sudah lama tidak berinteraksi."""
        batas = int(self._p("social_max_age")) if max_age is None else int(max_age)
        if kini is None:
            kini = max((s["last_t"] for s in self._entitas.values()), default=0)
        buang = [eid for eid, s in self._entitas.items()
                 if kini - s["last_t"] > batas]
        for eid in buang:
            self._entitas.pop(eid, None)
        self.social_forgotten += len(buang)
        return len(buang)

    @property
    def social_size(self) -> int:
        return len(self._entitas)

    # ==================== PILAR F — persepsi (psikofisika) ====================
    # Dunia tidak masuk apa adanya. Setiap stimulus drive melewati saluran:
    #   deteksi (SDT: derau + criterion) -> kompresi (Weber-Fechner terhadap
    #   level adaptasi) -> habituasi (pengulangan) -> [di Naluri: gain emosi,
    #   prior top-down, seleksi atensi]. Semua metode di bawah no-op aman
    #   saat pilar mati; pemanggil (Naluri) yang mengecek `enabled`.

    def _sens(self, drive: str) -> float:
        """d' efektif = sensitivitas TERPELAJARI × pengali WATAK per-drive."""
        belajar = float(self.sensitivitas.get(drive, 1.0))
        instabil = self._sensitivitas_instabil.get(drive)
        guncang = 1.0
        if instabil and self._perception_tick <= int(instabil.get("sampai", -1)):
            # Tiga fase d' yang berganti per tick; bukan noise RNG dan tetap
            # reproducible saat save/load.
            fase = (self._perception_tick + self._index.get(drive, 0)) % 3
            guncang = (0.70, 1.18, 0.88)[fase]
        return max(0.05, belajar * guncang
                   * self._p_drive("persepsi_sensitivitas", drive))

    def deteksi(self, drive: str, mentah: float,
                rng: Optional[Any] = None) -> Tuple[float, str]:
        """Deteksi sinyal (Green & Swets): (kekuatan bukti dv, kategori).

        dv = |mentah|·d' + derau(0, σ/d') — stimulus lemah bisa TERLEWAT
        (subliminal) dan derau bisa lolos sebagai sensasi (di sisi Naluri:
        alarm palsu). Criterion negatif (watak hipervigilan) menurunkan
        ambang efektif: lebih banyak "ya" — lebih peka sekaligus lebih rawan
        salah. kategori: "sadar" | "subliminal".
        """
        if drive not in self.sensitivitas:
            return abs(float(mentah)), "sadar"
        sens = self._sens(drive)
        sigma = max(1e-4, self._p("persepsi_noise") / sens)
        bising = 0.0
        if rng is not None:
            try:
                bising = float(rng.gauss(0.0, sigma))
            except Exception:
                bising = 0.0
        dv = abs(float(mentah)) * sens + bising
        c = self._p_drive("persepsi_kriterion", drive)
        ambang_eff = max(0.005, self._p("persepsi_ambang") + c)
        if dv >= ambang_eff:
            self.persepsi_sadar += 1
            return max(0.0, dv), "sadar"
        self.persepsi_subliminal += 1
        return max(0.0, dv), "subliminal"

    def kompres(self, drive: str, dv: float) -> float:
        """Weber-Fechner + level adaptasi (Helson): besaran terpersepsi.

        m = ln(1 + k·dv / (1 + adaptasi)) / k  ≈ dv untuk dv kecil (linear),
        tersaturasi logaritmik untuk dv besar (hukum hasil berkurang), dan
        MENYUSUT saat saluran teradaptasi: penghuni medan perang tak lagi
        terkesiap oleh letusan yang dulu membuatnya melompat.
        """
        k = max(1e-3, self._p("persepsi_weber"))
        adapt = max(0.0, float(self.adaptasi.get(drive, 0.0)))
        return math.log(1.0 + k * max(0.0, float(dv)) / (1.0 + adapt)) / k

    def update_adaptasi(self, stimulus: Mapping[str, float],
                        tick: Optional[int] = None) -> None:
        """Level adaptasi mengejar rata-rata besaran stimulus per saluran.

        Dipanggil sekali per tick fisika dengan {drive: Σ|m| yang dipersepsi
        tick itu}. Tanpa stimulus, adaptasi meluruh ke 0 (pemulihan gelap).
        """
        if tick is not None:
            self.advance_perception_tick(int(tick))
        lr = self._p("persepsi_adaptasi_lr")
        for d in self.adaptasi:
            s = abs(float((stimulus or {}).get(d, 0.0)))
            self.adaptasi[d] = max(0.0, self.adaptasi[d] + lr * (s - self.adaptasi[d]))

    def _habit_sig(self, drive: str, reason: str) -> int:
        return zlib.crc32(f"{drive}|{str(reason)[:60]}".encode("utf-8")) & 0x7FFFFFFF

    def habit_factor(self, drive: str, reason: str, tick: int,
                     mutate: bool = True) -> float:
        """Faktor habituasi (1−lr)^n dengan pemulihan SPONTAN malas.

        Stimulus identik yang diulang memudar (habituasi refleks); setelah
        absen, hitungan pulih perlahan (spontaneous recovery) — dan di luar
        `habit_window` dianggap benar-benar baru. `mutate=False` untuk
        pembacaan tanpa jejak (mis. API `persepsi(teks)` untuk UI).
        """
        if not reason:
            return 1.0
        lr = jepit(self._p("persepsi_habit_lr"), 0.0, 0.95)
        lantai = jepit_01(self._p("persepsi_habit_lantai"))
        pulih = jepit_01(self._p("persepsi_habit_pulih"))
        window = max(1, int(self._p("persepsi_habit_window")))
        sig = self._habit_sig(drive, reason)
        slot = self._habit.get(sig)
        n = 0.0
        if slot is not None:
            jeda = max(0, int(tick) - int(slot.get("last_t", 0)))
            if jeda <= window:
                n = float(slot.get("n", 0.0)) * ((1.0 - pulih) ** jeda)
        if mutate:
            if slot is None and len(self._habit) >= int(self._p("persepsi_habit_max")):
                half = max(1.0, float(window) * 2.0)
                def retensi(kv: Tuple[int, Dict[str, Any]]) -> float:
                    hslot = kv[1]
                    age = max(0, int(tick) - int(hslot.get("last_t", 0)))
                    frekuensi = min(1.0, float(hslot.get("n", 0.0)) / 5.0)
                    return cast(float, (0.05 + frekuensi) * (0.5 ** (age / half)))
                tua = min(self._habit.items(), key=retensi)
                del self._habit[tua[0]]
                self.persepsi_evicted += 1
            self._habit[sig] = {"n": n + 1.0, "last_t": int(tick),
                                "drive": drive, "sample": str(reason)[:40]}
        return cast(float, max(lantai, (1.0 - lr) ** n))

    def belajar_persepsi(self, galat_per_drive: Mapping[str, float]) -> None:
        """Pembelajaran perseptual: d' naik bila prediksi saluran akurat.

        Sinyal = |galat| per drive dari observe_outcome (lexicon vs realita):
        galat kecil → saluran terbukti andal → sensitivitas menuju 2.0;
        galat ≥ 0.5 → saluran tak andal → menuju 0.5. Inilah "belajar
        melihat", bukan "belajar menilai".
        """
        lr = self._p("persepsi_belajar_lr")
        for d, e in (galat_per_drive or {}).items():
            if d not in self.sensitivitas:
                continue
            e = abs(float(e))
            arah = jepit_drive(1.0 - e / 0.5)
            baru = self.sensitivitas[d] + lr * arah
            self.sensitivitas[d] = jepit(baru, 0.5, 2.0)

    def persepsi_ringkas(self) -> Dict[str, Any]:
        """Snapshot saluran untuk HUD/status (JSON-safe, terbulatkan)."""
        return {
            "sensitivitas": {d: round(float(v), 3)
                             for d, v in self.sensitivitas.items()},
            "d_efektif": {d: round(self._sens(d), 3) for d in self.drives},
            "tidak_stabil": {d: int(v.get("sampai", -1))
                              for d, v in self._sensitivitas_instabil.items()},
            "adaptasi": {d: round(float(v), 3)
                         for d, v in self.adaptasi.items()},
            "sadar": self.persepsi_sadar,
            "subliminal": self.persepsi_subliminal,
            "habit_slot": len(self._habit),
        }

    # ==================== PILAR G — introspeksi diri ====================
    # Fisiologi nyata & teori:
    #   Craig AD (2002) How do you feel? Interoception. Nat Rev Neurosci.
    #   Critchley HD et al (2004) Neural systems supporting interoceptive awareness. Nat Neurosci.
    #   Seth AK (2013) Interoceptive inference, emotion, and the embodied self. Trends Cogn Sci.
    #   Botvinick MM et al (2001) Conflict monitoring and cognitive control. Psychol Rev. (ACC)
    #   Yeung N et al (2004) ERN/Ne. (error-related negativity)
    #   Nelson & Narens (1990) Metamemory framework (object vs meta level)
    #   Fleming & Dolan (2012) The neural basis of metacognitive ability. Phil Trans R Soc.
    #   Maniscalco & Lau (2012) meta-d' measure of metacognitive sensitivity.
    #   Northoff et al (2006) Self-referential processing in cortical midline structures.
    #   Raichle et al (2001) Default Mode Network.
    #   Dehaene & Changeux (2011) Global Workspace Theory (ambang sadar)
    #   Damasio (1994) Somatic marker hypothesis.
    #
    # Implementasi:
    #   - _self_perceive: interosepsi berderau (anterior insula) -> perceived levels
    #   - update_introspection: EMA model diri + update confidence (PFC) + Pearson akurasi
    #   - meta: type-2 ROC proxy meta-d' = (mean conf correct - mean conf incorrect)/pooled SD
    #   - refleksi: DMN-like autobiographical integration -> narasi diri
    #   - sadar_diri: Global Workspace - discrepancy > ambang + confidence > ambang

    @staticmethod
    def _pearson(xs: Sequence[float], ys: Sequence[float]) -> float:
        """Korelasi Pearson, 0 bila varians nol / n<3 (real, bukan pseudo)."""
        if len(xs) < 3 or len(xs) != len(ys):
            return 0.0
        mx = sum(xs) / len(xs)
        my = sum(ys) / len(ys)
        num = 0.0
        den_x = 0.0
        den_y = 0.0
        for x, y in zip(xs, ys):
            dx = x - mx
            dy = y - my
            num += dx * dy
            den_x += dx * dx
            den_y += dy * dy
        den = math.sqrt(den_x * den_y)
        return num / den if den > 1e-12 else 0.0

    def _self_perceive(self, levels: Mapping[str, float],
                       urgency: Mapping[str, float],
                       rng: Optional[Any] = None
                       ) -> Tuple[Dict[str, float], Dict[str, float]]:
        """Interosepsi berderau: actual + bias + N(0,σ) -> perceived.

        Fisiologi: anterior insula mengintegrasi sinyal tubuh dengan derau
        (Craig 2002). σ = introspeksi_noise per-drive (WATAK: paranoid bisa
        punya noise tinggi untuk keamanan -> interosepsi buruk).
        """
        perceived_l: Dict[str, float] = {}
        perceived_u: Dict[str, float] = {}
        for d in self.drives:
            sigma = max(0.0, self._p_drive("introspeksi_noise", d))
            bias = self._p_drive("introspeksi_bias", d)
            n = 0.0
            nu = 0.0
            if rng is not None and sigma > 1e-9:
                try:
                    n = float(rng.gauss(0.0, sigma))
                    nu = float(rng.gauss(0.0, sigma * 0.5))
                except Exception:
                    n = 0.0
            perceived_l[d] = float(levels.get(d, 0.0)) + bias + n
            perceived_u[d] = float(urgency.get(d, 0.0)) + bias * 0.5 + nu
        return perceived_l, perceived_u

    def update_introspection(self,
                             levels: Mapping[str, float],
                             urgency: Mapping[str, float],
                             valence: float = 0.0,
                             arousal: float = 0.0,
                             tick: int = 0,
                             konflik: Optional[Any] = None,
                             prediksi_benar: Optional[bool] = None,
                             confidence_pred: Optional[float] = None,
                             rng: Optional[Any] = None) -> Dict[str, Any]:
        """Update model diri (insula) + kepercayaan (PFC) + akurasi + meta-d'.

        Dipanggil dari Naluri._physics tiap tick (self-monitoring) dan dari
        observe_outcome saat ada outcome prediksi (metacognitive update).

        - levels/urgency: keadaan aktual (object-level, Nelson & Narens)
        - valence/arousal: mood untuk konteks DMN
        - konflik: dict dari detect_conflict (ACC conflict signal)
        - prediksi_benar: bool apakah prediksi terakhir benar (untuk meta-d')
        - confidence_pred: confidence prediksi (0..1) untuk type-2
        """
        if not self.enabled("introspection"):
            return {}
        # 1) Persepsi interoseptif berderau
        perceived_l, perceived_u = self._self_perceive(levels, urgency, rng)

        # 2) Update model diri via EMA (Seth 2013: self-model = prediksi interoseptif)
        max_mem = int(self._p("introspeksi_max_memori"))
        window = int(self._p("introspeksi_window"))
        disc_total = 0.0
        for d in self.drives:
            lr = jepit_01(self._p_drive("introspeksi_lr", d))
            meta_lr = jepit_01(self._p_drive("introspeksi_meta_lr", d))
            actual = float(levels.get(d, 0.0))
            perc = float(perceived_l.get(d, 0.0))
            # EMA model
            self.model_diri[d] += lr * (perc - self.model_diri[d])
            self.model_urgensi[d] += lr * (float(perceived_u.get(d, 0.0)) - self.model_urgensi[d])
            # error untuk confidence: seberapa jauh model dari actual
            err = abs(actual - self.model_diri[d])
            disc_total += err
            # confidence update: target = 1 - clamp(err*1.5, 0..1) (PFC learning)
            target_conf = jepit_01(1.0 - err * 1.5)
            self.kepercayaan_diri[d] += meta_lr * (target_conf - self.kepercayaan_diri[d])
            self.kepercayaan_diri[d] = jepit_01(self.kepercayaan_diri[d])

            # simpan history per-drive untuk korelasi
            self._introspeksi_history.append({
                "tick": int(tick), "drive": d,
                "actual": actual, "perceived": perc,
                "model": float(self.model_diri[d]), "error": err,
                "conf": float(self.kepercayaan_diri[d]),
                "valence": float(valence), "arousal": float(arousal)
            })

        # batasi memori (LRU by tick)
        if max_mem > 0 and len(self._introspeksi_history) > max_mem:
            # simpan terbaru max_mem
            self._introspeksi_history = self._introspeksi_history[-max_mem:]

        self._introspeksi_discrepancy = disc_total / max(1, len(self.drives))
        self.kepercayaan_global = sum(self.kepercayaan_diri.values()) / max(1, len(self.drives))

        # 3) Hitung akurasi interoseptif = Pearson(actual, perceived) per drive
        #    (Critchley: interoceptive accuracy = korelasi)
        bias_sum = 0.0
        acc_sum = 0.0
        n_drive = 0
        for d in self.drives:
            hist_d = [h for h in self._introspeksi_history[-window:] if h["drive"] == d]
            if len(hist_d) >= 3:
                xs = [h["actual"] for h in hist_d]
                ys = [h["perceived"] for h in hist_d]
                r = self._pearson(xs, ys)
                self.introspeksi_korelasi_per_drive[d] = r
                acc_sum += r
                bias_sum += sum((h["perceived"] - h["actual"]) for h in hist_d) / len(hist_d)
                n_drive += 1
        if n_drive > 0:
            self.introspeksi_akurasi = acc_sum / n_drive
            self.introspeksi_bias_estimasi = bias_sum / n_drive
        else:
            self.introspeksi_akurasi = 0.0

        # 4) Metakognisi: meta-d' proxy (Maniscalco & Lau 2012)
        if prediksi_benar is not None and confidence_pred is not None:
            self._meta_history.append({
                "tick": int(tick), "confidence": jepit_01(float(confidence_pred)),
                "benar": bool(prediksi_benar),
                "error": 0.0 if prediksi_benar else 1.0
            })
            if len(self._meta_history) > max_mem:
                self._meta_history = self._meta_history[-max_mem:]

            # hitung meta-d' global: (mean conf correct - mean conf incorrect)/pooled SD
            correct = [h["confidence"] for h in self._meta_history[-window:] if h["benar"]]
            incorrect = [h["confidence"] for h in self._meta_history[-window:] if not h["benar"]]
            if correct and incorrect:
                mc = sum(correct) / len(correct)
                mi = sum(incorrect) / len(incorrect)
                # pooled SD
                var_c = sum((c - mc) ** 2 for c in correct) / max(1, len(correct))
                var_i = sum((c - mi) ** 2 for c in incorrect) / max(1, len(incorrect))
                pooled = math.sqrt((var_c + var_i) / 2.0) if (var_c + var_i) > 1e-9 else 1.0
                md = (mc - mi) / pooled if pooled > 1e-9 else (mc - mi)
                # clamp
                floor = float(self._p("introspeksi_meta_d_floor"))
                ceil = float(self._p("introspeksi_meta_d_ceiling"))
                self.meta_d_global = jepit(md + 0.5, floor, ceil)  # shift agar 0.5=chance
                # per-drive meta_d = -corr(conf, error) (confidence harus turun saat error naik)
                for d in self.drives:
                    hd = [h for h in self._introspeksi_history[-window:] if h["drive"] == d]
                    if len(hd) >= 5:
                        confs = [h["conf"] for h in hd]
                        errs = [h["error"] for h in hd]
                        # meta sensitivity = -corr(conf, err): tinggi = baik
                        r = self._pearson(confs, errs)
                        # ubah jadi meta-d proxy: 0.5 + (-r)/2 * scale
                        self.meta_d[d] = jepit(0.5 + (-r) * 0.8, floor, ceil)

        # 5) Error monitoring (ACC - Botvinick): log konflik & surprise
        if konflik is not None and isinstance(konflik, dict) and konflik.get("ada"):
            self._error_monitor.append({
                "tick": int(tick), "jenis": "konflik",
                "drive": konflik.get("drive"), "urgensi": konflik.get("urgensi"),
                "discrepancy": self._introspeksi_discrepancy
            })
            if len(self._error_monitor) > 128:
                self._error_monitor = self._error_monitor[-128:]

        # 6) Cek sadar diri (Global Workspace - Dehaene)
        ambang = float(self._p("introspeksi_ambang_sadar"))
        sadar = (self._introspeksi_discrepancy > ambang and self.kepercayaan_global > 0.3) or \
                (self.introspeksi_akurasi > 0.6 and self.kepercayaan_global > 0.5)
        if sadar:
            self.sadar_diri_ticks += 1

        # 7) Refleksi periodik (DMN)
        period = int(self._p("introspeksi_refleksi_period"))
        if int(tick) - self._terakhir_refleksi >= period and (sadar or period <= 1):
            self.refleksi_diri(tick, levels, urgency, valence, arousal)

        return {
            "discrepancy": self._introspeksi_discrepancy,
            "akurasi": self.introspeksi_akurasi,
            "kepercayaan": self.kepercayaan_global,
            "sadar": sadar
        }

    def refleksi_diri(self, tick: int,
                      levels: Optional[Mapping[str, float]] = None,
                      urgency: Optional[Mapping[str, float]] = None,
                      valence: float = 0.0,
                      arousal: float = 0.0) -> Dict[str, Any]:
        """DMN-like self-reflection: integrasi autobiografi -> narasi diri.

        Menghasilkan insight tentang pola kronis, bias, dan kepercayaan.
        Dipanggil otomatis tiap introspeksi_refleksi_period tick, atau manual.
        """
        if not self.enabled("introspection"):
            return {}
        if levels is None:
            levels = self.model_diri
        if urgency is None:
            urgency = self.model_urgensi

        # deteksi pola kronis: drive dengan model < -0.3 persisten
        kronis = [d for d in self.drives if float(self.model_diri.get(d, 0.0)) < -0.25]
        # bias: perceived > actual -> overestimasi, < -> underestimasi
        bias_desc = "netral"
        if self.introspeksi_bias_estimasi > 0.12:
            bias_desc = "cenderung melebih-lebihkan keadaan (overestimasi)"
        elif self.introspeksi_bias_estimasi < -0.12:
            bias_desc = "cenderung meremehkan keadaan (underestimasi)"

        # kepercayaan terendah
        if self.kepercayaan_diri:
            drive_rendah = min(self.drives, key=lambda d: self.kepercayaan_diri[d])
            conf_rendah = self.kepercayaan_diri[drive_rendah]
        else:
            drive_rendah = self.drives[0]
            conf_rendah = 0.5

        # narasi
        narasi = (
            f"Pada tick {tick}, saya merasa " + 
            ", ".join(f"{d} {self.model_diri[d]:+.2f}" for d in self.drives[:3]) +
            f"; valensi {valence:+.2f} arousal {arousal:.2f}. " +
            (f"Pola kronis: {', '.join(kronis)} defisit. " if kronis else "Tidak ada pola kronis berat. ") +
            f"Bias interoseptif: {bias_desc} ({self.introspeksi_bias_estimasi:+.3f}). " +
            f"Kepercayaan terendah pada {drive_rendah} ({conf_rendah:.2f}). " +
            f"Akurasi interoseptif r={self.introspeksi_akurasi:.2f}, meta-d'={self.meta_d_global:.2f}."
        )

        entry = {
            "tick": int(tick),
            "narasi": narasi,
            "kronis": kronis,
            "bias": bias_desc,
            "bias_nilai": round(self.introspeksi_bias_estimasi, 4),
            "akurasi": round(self.introspeksi_akurasi, 4),
            "meta_d": round(self.meta_d_global, 4),
            "kepercayaan": {d: round(v, 3) for d, v in self.kepercayaan_diri.items()},
            "discrepancy": round(self._introspeksi_discrepancy, 4),
            "sadar": self.sadar_diri_ticks > 0
        }
        self.narasi_diri.append(entry)
        if len(self.narasi_diri) > 64:
            self.narasi_diri = self.narasi_diri[-64:]
        self.refleksi_count += 1
        self._terakhir_refleksi = int(tick)
        return entry

    def introspeksi_state(self) -> Dict[str, Any]:
        """Snapshot introspeksi untuk HUD/status (JSON-safe)."""
        return {
            "aktif": self.enabled("introspection"),
            "model_diri": {d: round(float(v), 4) for d, v in self.model_diri.items()},
            "model_urgensi": {d: round(float(v), 4) for d, v in self.model_urgensi.items()},
            "kepercayaan": {d: round(float(v), 4) for d, v in self.kepercayaan_diri.items()},
            "kepercayaan_global": round(float(self.kepercayaan_global), 4),
            "akurasi": round(float(self.introspeksi_akurasi), 4),
            "bias": round(float(self.introspeksi_bias_estimasi), 4),
            "korelasi_per_drive": {d: round(float(v), 4) for d, v in self.introspeksi_korelasi_per_drive.items()},
            "meta_d": {d: round(float(v), 4) for d, v in self.meta_d.items()},
            "meta_d_global": round(float(self.meta_d_global), 4),
            "discrepancy": round(float(self._introspeksi_discrepancy), 4),
            "sadar_diri_ticks": self.sadar_diri_ticks,
            "refleksi_count": self.refleksi_count,
            "narasi_terakhir": self.narasi_diri[-1]["narasi"][:200] if self.narasi_diri else "",
            "history_len": len(self._introspeksi_history),
            "meta_len": len(self._meta_history),
        }

    def meta_kognisi_laporan(self) -> Dict[str, Any]:
        """Laporan metakognitif: akurasi, bias, meta-d', kalibrasi confidence.

        Berdasarkan Fleming & Dolan 2012: confidence harus memprediksi correctness.
        """
        if not self.enabled("introspection"):
            return {"aktif": False}
        # Brier confidence: (conf - (1-error_norm))^2
        brier = 0.0
        n = 0
        for h in self._introspeksi_history[-int(self._p("introspeksi_window")):]:
            target = jepit_01(1.0 - h["error"] * 1.5)
            brier += (h["conf"] - target) ** 2
            n += 1
        brier = brier / n if n else 0.0
        return {
            "aktif": True,
            "akurasi_interoseptif": round(self.introspeksi_akurasi, 4),
            "bias": round(self.introspeksi_bias_estimasi, 4),
            "kepercayaan_global": round(self.kepercayaan_global, 4),
            "meta_d_global": round(self.meta_d_global, 4),
            "meta_d_per_drive": {d: round(v, 4) for d, v in self.meta_d.items()},
            "brier_confidence": round(brier, 4),
            "discrepancy": round(self._introspeksi_discrepancy, 4),
            "sadar_diri": self.sadar_diri_ticks,
            "n_history": len(self._introspeksi_history),
            "n_meta": len(self._meta_history),
        }

    def evaluasi_diri(self) -> Dict[str, Any]:
        """Evaluasi diri cepat: discrepansi, drive bermasalah, insight."""
        if not self.enabled("introspection"):
            return {"aktif": False}
        # drive dengan error terbesar
        errors = {}
        for d in self.drives:
            hd = [h for h in self._introspeksi_history[-10:] if h["drive"] == d]
            if hd:
                errors[d] = sum(h["error"] for h in hd) / len(hd)
        bermasalah = sorted(errors.items(), key=lambda x: x[1], reverse=True)[:2]
        return {
            "aktif": True,
            "discrepancy": round(self._introspeksi_discrepancy, 4),
            "akurasi": round(self.introspeksi_akurasi, 4),
            "kepercayaan": round(self.kepercayaan_global, 4),
            "bermasalah": [(d, round(e, 4)) for d, e in bermasalah],
            "bias": round(self.introspeksi_bias_estimasi, 4),
            "meta_d": round(self.meta_d_global, 4),
            "sadar": self.sadar_diri_ticks > 0,
        }

    def sadar_diri(self) -> bool:
        """Apakah organisme saat ini sadar diri (Global Workspace Theory)?

        True bila discrepancy > ambang dan kepercayaan cukup, atau akurasi tinggi.
        """
        if not self.enabled("introspection"):
            return False
        ambang = float(self._p("introspeksi_ambang_sadar"))
        return (self._introspeksi_discrepancy > ambang and self.kepercayaan_global > 0.3) or \
               (self.introspeksi_akurasi > 0.6)

    def seed_introspection(self,
                           model_diri: Optional[Mapping[str, float]] = None,
                           kepercayaan: Optional[Mapping[str, float]] = None,
                           akurasi: Optional[float] = None) -> Dict[str, Any]:
        """Seed kondisi awal introspeksi (backstory 'lahir')."""
        hasil: Dict[str, Any] = {}
        if model_diri:
            for d, v in model_diri.items():
                if d in self.model_diri:
                    self.model_diri[d] = jepit_drive(float(v))
            hasil["model"] = dict(self.model_diri)
        if kepercayaan:
            for d, v in kepercayaan.items():
                if d in self.kepercayaan_diri:
                    self.kepercayaan_diri[d] = jepit_01(float(v))
            if self.kepercayaan_diri:
                self.kepercayaan_global = (sum(self.kepercayaan_diri.values())
                                           / len(self.kepercayaan_diri))
            hasil["kepercayaan"] = dict(self.kepercayaan_diri)
        if akurasi is not None:
            self.introspeksi_akurasi = jepit_drive(float(akurasi))
            hasil["akurasi"] = self.introspeksi_akurasi
        return hasil


    # --------- seeding backstory (solusi cold-start) ---------
    # Filter plastisitas (watak) TIDAK menciptakan sifat di tick 0 — ia hanya
    # MEMPERTAHANKAN-nya saat pengalaman mencoba mengubahnya. Karena itu
    # kondisi awal harus di-seed langsung: apa yang akan dihasilkan filter
    # lambat andaikan ia sudah berjalan bertahun-tahun sebelum game dimulai.

    def seed_affective(self, text: str, drive_deltas: Mapping[str, float],
                       n: int = 5, tick: int = 0) -> bool:
        """Seed satu slot memori afektif ("pernah terbakar sebelumnya").

        Prior langsung aktif di tick 0 (bila pilar A nyala) tanpa menunggu
        pengalaman nyata. `n` = jumlah sampel seolah-olah sudah dialami.
        """
        if not text:
            return False
        n = max(1, int(n))
        sig = self.context_signature(text)
        deltas = {d: jepit_drive(float(drive_deltas.get(d, 0.0) or 0.0))
                  for d in self.drives}
        importance = max((abs(v) for v in deltas.values()), default=0.0)
        self._affective[sig] = {"deltas": deltas, "n": n,
                                "last_t": int(tick), "sample": str(text)[:60],
                                "importance": importance}
        self.experience_count += n
        self._append_episode_log(sig, int(tick), deltas, str(text), count=n)
        self._evict_affective(int(tick))
        return True

    def seed_relationship(self, ent: Any, valensi: float = 0.0,
                          kepercayaan: float = 0.0, akrab: float = 0.0,
                          n: int = 1, nama: str = "", tick: int = 0) -> Dict[str, Any]:
        """Seed relasi dengan entitas yang 'sudah dikenal sebelum game mulai'."""
        self._entitas[self._eid(ent)] = {
            "nama": str(nama or ""),
            "valensi": jepit_drive(float(valensi)),
            "kepercayaan": jepit_drive(float(kepercayaan)),
            "akrab": jepit_01(float(akrab)),
            "n": max(0, int(n)), "last_t": int(tick)}
        return self.relationship(ent)

    def seed_setpoints(self, setpoints: Mapping[str, float]) -> Dict[str, float]:
        """Seed setpoint plastis (dieksekusi saat kelahiran Naluri).

        Nilai di-clip ke `setpoint_clamp` per-drive yang berlaku — watak
        menentukan seberapa ekstrem keyakinan awal boleh di-seed.
        """
        hasil: Dict[str, float] = {}
        for d, v in (setpoints or {}).items():
            if d in self.setpoints:
                clamp = self._p_drive("setpoint_clamp", d)
                self.setpoints[d] = max(-clamp, min(clamp, float(v)))
                hasil[d] = self.setpoints[d]
        return hasil

    def seed_calibration(self, per_drive: Optional[Mapping[str, float]] = None,
                         brier_ema: Optional[float] = None, n: int = 10) -> None:
        """Seed jejak rapor kalibrasi ("selalu salah soal keamanan")."""
        n = max(1, int(n))
        for d, e in (per_drive or {}).items():
            if d in self._drive_err_ema:
                self._drive_err_ema[d] = abs(float(e))
                self._drive_err_n[d] = n
        if brier_ema is not None:
            self._brier_ema = max(0.0, float(brier_ema))
            self._brier_n = max(self._brier_n, n)

    # ==================== laporan gabungan ====================
    def meta_status(self) -> Dict[str, Any]:
        """Ringkasan seluruh lapisan NURANI (dipakai Naluri.status & orkestra)."""
        rep = self.calibration_report()
        aset = sum(sum(r) for r in self.interoception)
        return {
            "pillars": {p: self.enabled(p) for p in PILLARS},
            "affective_memory": {
                "slot": self.affective_size,
                "pengalaman": self.experience_count,
                "prior_dipakai": self.affective_hits,
                "terbuang_lru": self.affective_evicted,
                "dilupakan": self.affective_forgotten,
                "replay_log": len(self._episode_log),
                "replay_kapasitas": int(self._p("episode_log_max")),
                "kapasitas": int(self._p("affective_max")),
                "lexicon_kata": len(self._kata_delta),
                "lexicon_kata_terbuang": self.kata_delta_evicted,
                "lexicon_kata_kapasitas": int(self._p("word_delta_max")),
            },
            "kalibrasi": {
                "brier": round(rep.brier, 4),
                "brier_ema": round(rep.brier_ema, 4),
                "n_samples": rep.n_samples,
                "per_drive_ema": {k: round(v, 4)
                                  for k, v in rep.per_drive_ema.items()},
                "bin_reliability": len(rep.reliability),
                "skala_diterima": self.scale_accepted,
                "skala_ditolak": self.scale_rejected,
                "holdout": [round(x, 4) for x in self.last_holdout],
                "ketidakpastian": self.uncertainty_report(),
            },
            "theory_of_mind": {"entitas": len(self._other_beliefs)},
            "setpoint": {d: round(v, 4) for d, v in self.setpoints.items()},
            "interosepsi": {"jumlah_aset": round(aset, 4),
                            "pengali_gema": round(self._p("interoception_echo"), 3)},
            "konflik": {"tick_konflik": self.conflict_ticks,
                        "resolusi": self.conflict_resolved,
                        "drive_terlibat": list(self.conflict_drives)},
            "ritme": {"periode": int(self._p("circadian_period")),
                      "geser_malam": round(self._p("circadian_night_shift"), 3),
                      "berlaku": self.enabled("circadian")},
            "flow": {"tick_flow": self.flow_ticks,
                     "bonus": round(self._p("flow_reward_bonus"), 3)},
            "relasi": {"slot": self.social_size,
                       "interaksi": self.social_interactions,
                       "terbuang_lru": self.social_evicted,
                       "dilupakan": self.social_forgotten,
                       "kapasitas": int(self._p("social_max")),
                       "berlaku": self.enabled("social_memory")},
            "persepsi": dict(self.persepsi_ringkas(),
                             berlaku=self.enabled("perception")),
            "introspeksi": dict(self.introspeksi_state(),
                                laporan=self.meta_kognisi_laporan(),
                                berlaku=self.enabled("introspection")),
        }

    # ==================== serialisasi (fix #1) ====================
    def to_dict(self, include_params: bool = False) -> Dict[str, Any]:
        """Serialisasi state NURANI ke struktur JSON-safe.

        Nested state ditangani eksplisit:
          * `_affective`  : kunci signature int -> string (JSON tidak punya
                           kunci int), nilai slot disalin apa adanya.
          * `interoception`: matriks list-of-list disalin per baris.
          * `_pairs_unit` : tuple -> list.
        `include_params=True` hanya untuk pemakaian BERDIRI SENDIRI; saat
        NURANI menempel pada Naluri, params adalah dict milik Naluri dan
        sudah ikut terserialisasi di sana (satu sumber kebenaran).
        Cache signature (`_sig_cache`) sengaja TIDAK disimpan — ia turunan.
        """
        data: Dict[str, Any] = {
            "format": "nurani/2",
            "drives": list(self.drives),
            "affective": {
                str(sig): {"deltas": {d: float(s["deltas"].get(d, 0.0))
                                      for d in self.drives},
                           "n": int(s["n"]), "last_t": int(s["last_t"]),
                           "sample": str(s.get("sample", "")),
                           "importance": float(s.get("importance", 0.0))}
                for sig, s in self._affective.items()},
            "episode_log": [
                {"sig": int(e["sig"]), "tick": int(e["tick"]),
                 "deltas": {d: float(e["deltas"].get(d, 0.0)) for d in self.drives},
                 "impact": float(e.get("impact", 0.0)),
                 "importance": float(e.get("importance", 0.0)),
                 "sample": str(e.get("sample", ""))[:60],
                 "n": int(e.get("n", 1))}
                for e in self._episode_log],
            "word_deltas": {
                word: {"deltas": {d: float(slot.get("deltas", {}).get(d, 0.0))
                                   for d in self.drives},
                       "n": int(slot.get("n", 0)),
                       "last_t": int(slot.get("last_t", 0)),
                       "importance": float(slot.get("importance", 0.0))}
                for word, slot in self._kata_delta.items()},
            "word_delta_evicted": self.kata_delta_evicted,
            "uncertainty": {"epistemic_ema": self._epistemic_ema,
                            "aleatoric_ema": self._aleatoric_ema,
                            "n": self._uncertainty_n},
            "other_beliefs": copy.deepcopy(self._other_beliefs),
            "kacamata_sosial": copy.deepcopy(self._kacamata_sosial),
            "counters": {"affective_hits": self.affective_hits,
                         "experience_count": self.experience_count,
                         "affective_evicted": self.affective_evicted,
                         "affective_forgotten": self.affective_forgotten,
                         "scale_accepted": self.scale_accepted,
                         "scale_rejected": self.scale_rejected},
            "brier": {"sum": self._brier_sum, "ema": self._brier_ema,
                      "n": self._brier_n},
            "drive_err_ema": dict(self._drive_err_ema),
            "drive_err_n": dict(self._drive_err_n),
            "errors": list(self._errors),
            "pairs_unit": [[float(p), float(r)] for p, r in self._pairs_unit],
            "last_holdout": [float(x) for x in self.last_holdout],
            "setpoints": dict(self.setpoints),
            "interoception": [[float(x) for x in baris]
                              for baris in self.interoception],
            "structural_shocks": [dict(x) for x in self._structural_shocks],
            "sensitivitas_instabil": copy.deepcopy(self._sensitivitas_instabil),
            "perception_tick": self._perception_tick,
            "conflict": {"ticks": self.conflict_ticks,
                         "resolved": self.conflict_resolved,
                         "drives": list(self.conflict_drives)},
            "flow_ticks": self.flow_ticks,
            # pilar E: entitas sudah ber-kunci string (JSON-safe apa adanya)
            "entitas": {eid: {"nama": s["nama"],
                              "valensi": float(s["valensi"]),
                              "kepercayaan": float(s["kepercayaan"]),
                              "akrab": float(s["akrab"]),
                              "n": int(s["n"]), "last_t": int(s["last_t"]),
                              "hancur": bool(s.get("hancur", False)),
                              "utang": [dict(u) for u in (s.get("utang") or [])]}
                        for eid, s in self._entitas.items()},
            "core_cap": {k: float(v) for k, v in self._core_cap.items()},
            "social_counters": {"interactions": self.social_interactions,
                                "evicted": self.social_evicted,
                                "forgotten": self.social_forgotten},
            # pilar F: saluran persepsi (sensitivitas belajar, adaptasi,
            # habituasi — kunci crc32 int -> string agar JSON-safe).
            "perception": {
                "sensitivitas": {d: float(v)
                                 for d, v in self.sensitivitas.items()},
                "adaptasi": {d: float(v) for d, v in self.adaptasi.items()},
                "habit": {str(sig): {"n": float(s.get("n", 0.0)),
                                     "last_t": int(s.get("last_t", 0)),
                                     "drive": str(s.get("drive", "")),
                                     "sample": str(s.get("sample", ""))}
                          for sig, s in self._habit.items()},
                "counters": {"sadar": self.persepsi_sadar,
                             "subliminal": self.persepsi_subliminal,
                             "evicted": self.persepsi_evicted},
            },
            # pilar G: introspeksi diri (interosepsi sadar + metakognisi)
            "introspection": {
                "model_diri": {d: float(v) for d, v in self.model_diri.items()},
                "model_urgensi": {d: float(v) for d, v in self.model_urgensi.items()},
                "kepercayaan": {d: float(v) for d, v in self.kepercayaan_diri.items()},
                "kepercayaan_global": float(self.kepercayaan_global),
                "meta_d": {d: float(v) for d, v in self.meta_d.items()},
                "meta_d_global": float(self.meta_d_global),
                "akurasi": float(self.introspeksi_akurasi),
                "bias": float(self.introspeksi_bias_estimasi),
                "korelasi": {d: float(v) for d, v in self.introspeksi_korelasi_per_drive.items()},
                "discrepancy": float(self._introspeksi_discrepancy),
                "history": [
                    {"tick": int(h["tick"]), "drive": str(h["drive"]),
                     "actual": float(h["actual"]), "perceived": float(h["perceived"]),
                     "model": float(h["model"]), "error": float(h["error"]),
                     "conf": float(h["conf"])}
                    for h in self._introspeksi_history[-128:]
                ],
                "meta_history": [
                    {"tick": int(h["tick"]), "confidence": float(h["confidence"]),
                     "benar": bool(h["benar"])} for h in self._meta_history[-128:]
                ],
                "narasi": [
                    {"tick": int(n["tick"]), "narasi": str(n["narasi"])[:400],
                     "kronis": list(n.get("kronis", [])), "bias": str(n.get("bias", "")),
                     "akurasi": float(n.get("akurasi", 0.0)), "meta_d": float(n.get("meta_d", 0.0))}
                    for n in self.narasi_diri[-16:]
                ],
                "error_monitor": [
                    {"tick": int(e["tick"]), "jenis": str(e["jenis"]), "drive": e.get("drive")}
                    for e in self._error_monitor[-32:]
                ],
                "counters": {"refleksi": self.refleksi_count, "sadar": self.sadar_diri_ticks,
                             "terakhir_refleksi": self._terakhir_refleksi},
            },
            # pilar H: kesadaran terasa (monolog, rasa tubuh, moral, keraguan)
            "kesadaran_terasa": {
                "felt": {k: float(v) for k, v in self.felt_state.items()},
                "moral": {k: float(v) for k, v in self.moral_emotions.items()},
                "somatic": [dict(x) for x in self.somatic_markers[-64:]],
                "narrative_identity": [dict(x) for x in self.narrative_identity[-16:]],
                "reality_log": [dict(x) for x in self.reality_source_log[-48:]],
                "doubt": float(self.doubt_level),
                "confab": [dict(x) for x in self.confabulation_log[-48:]],
                "last_inner_speech_tick": int(self._last_inner_speech_tick),
                # ORDE NOL: kanal kepekaan yang lahir dari kategori proto.
                "kategori_proto": copy.deepcopy(self.kategori_proto),
            },
        }
        if include_params:
            data["params"] = copy.deepcopy(self.params)
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any],
                  params: Optional[Dict[str, Any]] = None) -> "Nurani":
        """Bangun kembali Nurani dari `to_dict()`.

        `params`: dict params MILIK Naluri agar berbagi-dict tetap berlaku
        setelah load; None = pakai params tersimpan (mode berdiri sendiri)
        atau NURANI_DEFAULTS.
        """
        from pycos.dukungan.validasi_state import validasi_state
        data = validasi_state(data, "Nurani")
        data = data or {}
        drives = tuple(data.get("drives") or DEFAULT_DRIVES)
        if params is None:
            params = copy.deepcopy(data.get("params") or NURANI_DEFAULTS)
        nur = cls(drives=drives, params=params)
        # pilar A: kunci signature dikembalikan ke int
        for sig, s in (data.get("affective") or {}).items():
            deltas = {d: float((s.get("deltas") or {}).get(d, 0.0))
                      for d in drives}
            nur._affective[int(sig)] = {
                "deltas": deltas, "n": int(s.get("n", 0)),
                "last_t": int(s.get("last_t", 0)),
                "sample": str(s.get("sample", ""))[:60],
                "importance": float(s.get("importance", max((abs(v) for v in deltas.values()), default=0.0)))}
        nur._episode_log = []
        for e in (data.get("episode_log") or []):
            try:
                ed = {d: float((e.get("deltas") or {}).get(d, 0.0)) for d in drives}
                nur._episode_log.append({
                    "sig": int(e.get("sig", 0)), "tick": int(e.get("tick", 0)),
                    "deltas": ed,
                    "impact": float(e.get("impact", max((abs(v) for v in ed.values()), default=0.0))),
                    "importance": float(e.get("importance", max((abs(v) for v in ed.values()), default=0.0))),
                    "sample": str(e.get("sample", ""))[:60],
                    "n": max(1, int(e.get("n", 1))),
                })
            except (TypeError, ValueError):
                continue
        episode_cap = max(0, int(nur._p("episode_log_max")))
        if len(nur._episode_log) > episode_cap:
            if episode_cap == 0:
                nur._episode_log = []
            else:
                now = max((int(x.get("tick", 0)) for x in nur._episode_log), default=0)
                nur._episode_log.sort(
                    key=lambda x: nur._retention_score(x, now, "tick"), reverse=True)
                nur._episode_log = nur._episode_log[:episode_cap]
        nur._kata_delta = {}
        for word, item in (data.get("word_deltas") or {}).items():
            if not isinstance(item, Mapping):
                continue
            key = str(word).casefold().strip()
            if not key:
                continue
            try:
                deltas = {d: jepit_drive(float((item.get("deltas") or {}).get(d, 0.0)))
                          for d in drives}
                nur._kata_delta[key] = {
                    "deltas": deltas, "n": max(0, int(item.get("n", 0))),
                    "last_t": int(item.get("last_t", 0)),
                    "importance": max(0.0, float(item.get("importance",
                        max((abs(v) for v in deltas.values()), default=0.0)))),
                }
            except (TypeError, ValueError):
                continue
        nur.kata_delta_evicted = max(0, int(data.get("word_delta_evicted", 0)))
        nur._evict_word_delta(max((int(s.get("last_t", 0))
                                   for s in nur._kata_delta.values()), default=0))
        c = data.get("counters") or {}
        nur.affective_hits = int(c.get("affective_hits", 0))
        nur.experience_count = int(c.get("experience_count", 0))
        nur.affective_evicted = int(c.get("affective_evicted", 0))
        nur.affective_forgotten = int(c.get("affective_forgotten", 0))
        nur.scale_accepted = int(c.get("scale_accepted", 0))
        nur.scale_rejected = int(c.get("scale_rejected", 0))
        u = data.get("uncertainty") or {}
        nur._epistemic_ema = jepit_01(float(u.get("epistemic_ema", 1.0)))
        nur._aleatoric_ema = jepit_01(float(u.get("aleatoric_ema", 0.0)))
        nur._uncertainty_n = max(0, int(u.get("n", 0)))
        nur._other_beliefs = {}
        for eid, drives_map in (data.get("other_beliefs") or {}).items():
            if not isinstance(drives_map, Mapping):
                continue
            nur._other_beliefs[str(eid)] = {}
            for d, item in drives_map.items():
                if d in drives and isinstance(item, Mapping):
                    nur._other_beliefs[str(eid)][d] = {
                        "value": jepit_drive(float(item.get("value", 0.0))),
                        "confidence": jepit_01(float(item.get("confidence", 0.0))),
                        "n": max(0, int(item.get("n", 0))),
                        "last_t": max(0, int(item.get("last_t", 0))),
                    }
        for d, item in (data.get("kacamata_sosial") or {}).items():
            if d in nur._kacamata_sosial and isinstance(item, Mapping):
                nur._kacamata_sosial[d] = {
                    "bias": jepit_drive(float(item.get("bias", 0.0))),
                    "kekakuan": jepit_01(float(item.get("kekakuan", 1.0))),
                    "bukti_lawan": max(0, int(item.get("bukti_lawan", 0))),
                    "observasi": max(0, int(item.get("observasi", 0))),
                }
        # pilar B
        b = data.get("brier") or {}
        nur._brier_sum = float(b.get("sum", 0.0))
        nur._brier_ema = float(b.get("ema", 0.0))
        nur._brier_n = int(b.get("n", 0))
        for d, v in (data.get("drive_err_ema") or {}).items():
            if d in nur._drive_err_ema:
                nur._drive_err_ema[d] = float(v)
        for d, v in (data.get("drive_err_n") or {}).items():
            if d in nur._drive_err_n:
                nur._drive_err_n[d] = int(v)
        nur._errors = [float(x) for x in (data.get("errors") or [])]
        nur._pairs_unit = [(float(p[0]), float(p[1]))
                           for p in (data.get("pairs_unit") or [])]
        lh = data.get("last_holdout") or (0.0, 0.0)
        nur.last_holdout = (float(lh[0]), float(lh[1]))
        # pilar C
        for d, v in (data.get("setpoints") or {}).items():
            if d in nur.setpoints:
                nur.setpoints[d] = float(v)
        m = data.get("interoception")
        if m and len(m) == len(drives):
            nur.interoception = [[float(x) for x in baris[:len(drives)]]
                                 for baris in m]
        nur._structural_shocks = [dict(x) for x in
                                  (data.get("structural_shocks") or [])][-64:]
        nur._sensitivitas_instabil = {str(d): dict(v) for d, v in
                                      (data.get("sensitivitas_instabil") or {}).items()
                                      if d in drives and isinstance(v, Mapping)}
        nur._perception_tick = int(data.get("perception_tick", 0))
        # pilar D
        k = data.get("conflict") or {}
        nur.conflict_ticks = int(k.get("ticks", 0))
        nur.conflict_resolved = int(k.get("resolved", 0))
        nur.conflict_drives = [str(x) for x in (k.get("drives") or [])]
        nur.flow_ticks = int(data.get("flow_ticks", 0))
        # pilar E: memori sosial
        for eid, s in (data.get("entitas") or {}).items():
            nur._entitas[str(eid)] = {
                "nama": str(s.get("nama", "")),
                "valensi": jepit_drive(float(s.get("valensi", 0.0))),
                "kepercayaan": jepit_drive(float(s.get("kepercayaan", 0.0))),
                "akrab": jepit_01(float(s.get("akrab", 0.0))),
                "n": int(s.get("n", 0)), "last_t": int(s.get("last_t", 0)),
                "hancur": bool(s.get("hancur", False)),
                "utang": [dict(u) for u in (s.get("utang") or [])]}
        nur._core_cap = {str(k): float(v) for k, v in
                         (data.get("core_cap") or {}).items()}
        sc = data.get("social_counters") or {}
        nur.social_interactions = int(sc.get("interactions", 0))
        nur.social_evicted = int(sc.get("evicted", 0))
        nur.social_forgotten = int(sc.get("forgotten", 0))
        # pilar F: persepsi (save lama tanpa blok ini -> default netral)
        f = data.get("perception") or {}
        for d, v in (f.get("sensitivitas") or {}).items():
            if d in nur.sensitivitas:
                nur.sensitivitas[d] = jepit(float(v), 0.5, 2.0)
        for d, v in (f.get("adaptasi") or {}).items():
            if d in nur.adaptasi:
                nur.adaptasi[d] = max(0.0, float(v))
        for sig, s in (f.get("habit") or {}).items():
            try:
                nur._habit[int(sig)] = {
                    "n": float(s.get("n", 0.0)),
                    "last_t": int(s.get("last_t", 0)),
                    "drive": str(s.get("drive", "")),
                    "sample": str(s.get("sample", ""))}
            except (ValueError, TypeError):
                pass
        fc = f.get("counters") or {}
        nur.persepsi_sadar = int(fc.get("sadar", 0))
        nur.persepsi_subliminal = int(fc.get("subliminal", 0))
        nur.persepsi_evicted = int(fc.get("evicted", 0))
        # pilar G: introspeksi diri (save lama tanpa blok ini -> default netral)
        g = data.get("introspection") or {}
        for d, v in (g.get("model_diri") or {}).items():
            if d in nur.model_diri:
                nur.model_diri[d] = float(v)
        for d, v in (g.get("model_urgensi") or {}).items():
            if d in nur.model_urgensi:
                nur.model_urgensi[d] = float(v)
        for d, v in (g.get("kepercayaan") or {}).items():
            if d in nur.kepercayaan_diri:
                nur.kepercayaan_diri[d] = jepit_01(float(v))
        nur.kepercayaan_global = float(g.get("kepercayaan_global", nur.kepercayaan_global))
        for d, v in (g.get("meta_d") or {}).items():
            if d in nur.meta_d:
                nur.meta_d[d] = float(v)
        nur.meta_d_global = float(g.get("meta_d_global", 0.5))
        nur.introspeksi_akurasi = float(g.get("akurasi", 0.0))
        nur.introspeksi_bias_estimasi = float(g.get("bias", 0.0))
        for d, v in (g.get("korelasi") or {}).items():
            if d in nur.introspeksi_korelasi_per_drive:
                nur.introspeksi_korelasi_per_drive[d] = float(v)
        nur._introspeksi_discrepancy = float(g.get("discrepancy", 0.0))
        nur._introspeksi_history = [
            {"tick": int(h.get("tick", 0)), "drive": str(h.get("drive", "")),
             "actual": float(h.get("actual", 0.0)), "perceived": float(h.get("perceived", 0.0)),
             "model": float(h.get("model", 0.0)), "error": float(h.get("error", 0.0)),
             "conf": float(h.get("conf", 0.5))}
            for h in (g.get("history") or [])]
        nur._meta_history = [
            {"tick": int(h.get("tick", 0)), "confidence": float(h.get("confidence", 0.5)),
             "benar": bool(h.get("benar", False))}
            for h in (g.get("meta_history") or [])]
        nur.narasi_diri = [
            {"tick": int(n.get("tick", 0)), "narasi": str(n.get("narasi", "")),
             "kronis": list(n.get("kronis", [])), "bias": str(n.get("bias", "")),
             "akurasi": float(n.get("akurasi", 0.0)), "meta_d": float(n.get("meta_d", 0.0))}
            for n in (g.get("narasi") or [])]
        nur._error_monitor = [
            {"tick": int(e.get("tick", 0)), "jenis": str(e.get("jenis", "")), "drive": e.get("drive")}
            for e in (g.get("error_monitor") or [])]
        gc = g.get("counters") or {}
        nur.refleksi_count = int(gc.get("refleksi", 0))
        nur.sadar_diri_ticks = int(gc.get("sadar", 0))
        nur._terakhir_refleksi = int(gc.get("terakhir_refleksi", -10000))
        # pilar H: kesadaran terasa (save lama tanpa blok ini -> default)
        h = data.get("kesadaran_terasa") or {}
        for k, v in (h.get("felt") or {}).items():
            if k in nur.felt_state:
                nur.felt_state[k] = jepit_01(float(v))
        for k, v in (h.get("moral") or {}).items():
            if k in nur.moral_emotions:
                nur.moral_emotions[k] = jepit_01(float(v))
        nur.somatic_markers = [dict(x) for x in (h.get("somatic") or [])][-64:]
        nur.narrative_identity = [dict(x) for x in
                                  (h.get("narrative_identity") or [])][-16:]
        nur.reality_source_log = [dict(x) for x in
                                  (h.get("reality_log") or [])][-48:]
        nur.doubt_level = jepit_01(float(h.get("doubt", 0.0)))
        nur.confabulation_log = [dict(x) for x in (h.get("confab") or [])][-48:]
        nur._last_inner_speech_tick = int(h.get("last_inner_speech_tick", -10000))
        nur.kategori_proto = {
            str(k): dict(v) for k, v in (h.get("kategori_proto") or {}).items()
            if isinstance(v, Mapping)}
        return nur

    # ------------------------------------------------------------------
    # ORDE NOL: kategori yang belum pernah ada → sensitivitas baru NURANI
    # ------------------------------------------------------------------
    def serap_kategori(self, signature: Any, nama: Optional[str] = None,
                       jenis: str = "tutur", kekuatan: float = 0.5,
                       tick: Optional[int] = None,
                       klaim: Optional[str] = None) -> Dict[str, Any]:
        """Kategori proto yang TERKONSOLIDASI masuk sebagai sensitivitas baru.

        Sensitivitas ini tidak menyentuh ``sensitivitas`` per-drive (dimensi
        bawaan tetap ``drives``) dan tidak menambah emosi/drive baru: ia kanal
        tambahan. Kekuatan kanal bertambah menurut bukti berulang (logaritmik)
        dan dibatasi [0..1] — kategori baru menambah KEPEKAAN, bukan histeria.
        """
        sig = str(signature)
        if not sig:
            return {}
        k = jepit_01(float(kekuatan))
        kini = int(tick if tick is not None else max(
            [int(x.get("tick", 0)) for x in self.narrative_identity] + [0]))
        lama = self.kategori_proto.get(sig)
        if lama is None:
            entri: Dict[str, Any] = {"signature": sig, "nama": (str(nama)[:40] if nama else None),
                     "jenis": str(jenis or "tutur"),
                     "kekuatan": round(k, 4), "jumlah": 1,
                     "tick_lahir": kini, "tick_terakhir": kini,
                     "klaim": (str(klaim)[:80] if klaim else None)}
        else:
            entri = dict(lama)
            entri["jumlah"] = int(lama.get("jumlah", 1)) + 1
            # sqrt(n): bukti pertama paling mengubah kepekaan, bukti berikutnya
            # menambah sedikit — belajar, bukan terakumulasi tanpa batas.
            tambah = k / max(1.0, float(entri["jumlah"]) ** 1.5)
            entri["kekuatan"] = round(min(1.0, float(lama.get("kekuatan", 0.0))
                                          + tambah), 4)
            entri["tick_terakhir"] = kini
            if nama and not entri.get("nama"):
                entri["nama"] = str(nama)[:40]
            if klaim and not entri.get("klaim"):
                entri["klaim"] = str(klaim)[:80]
        self.kategori_proto[sig] = entri
        if len(self.kategori_proto) > 32:
            # buang yang paling lemah & paling lama tak muncul
            terlemah = min(self.kategori_proto.items(),
                           key=lambda kv: (float(kv[1].get("kekuatan", 0.0)),
                                           -int(kv[1].get("tick_terakhir", 0))))
            self.kategori_proto.pop(terlemah[0], None)
        return dict(entri)

    def sensitivitas_kategori(self, minimum: float = 0.0) -> Dict[str, Dict[str, Any]]:
        """Kanal kepekaan yang lahir dari kategori proto (bukan drive/emosi)."""
        return {k: dict(v) for k, v in self.kategori_proto.items()
                if float(v.get("kekuatan", 0.0)) >= float(minimum)}

    def peka_terhadap(self, signature: Any) -> float:
        """Kekuatan kepekaan terhadap sebuah kategori proto (0 bila belum ada)."""
        entri = self.kategori_proto.get(str(signature))
        return 0.0 if entri is None else float(entri.get("kekuatan", 0.0))

    # ==================== PILAR H — KESADARAN TERASA ====================
    # Perluasan pilar G: dari "model diri" menjadi pengalaman yang dapat
    # dilaporkan (monolog batin, rasa tubuh, emosi moral, keraguan, mimpi).
    def felt_consciousness(self) -> bool:
        return bool(self.params.get("enable_felt_consciousness", False))

    def _felt(self, key: str) -> bool:
        return (self.felt_consciousness()
                and bool(self.params.get("enable_" + key, False)))

    def update_felt(self,
                    levels: Mapping[str, float],
                    urgency: Optional[Mapping[str, float]] = None,
                    arousal: float = 0.0,
                    tick: Optional[int] = None) -> Dict[str, float]:
        """Bentuk sensasi tubuh yang DIRASAKAN dari keadaan drive + arousal."""
        if not self._felt("felt_consciousness") and not self.felt_consciousness():
            return {}
        urg = urgency or {}
        e = float(levels.get("energi", 0.0))
        k = float(levels.get("keamanan", 0.0))
        c = float(levels.get("koherensi", 0.0))
        target = {
            "lelah": max(0.0, -e),
            "lapar": 0.7 * max(0.0, -e),
            "sesak": max(0.0, -k),
            "jantung": 0.8 * max(0.0, arousal) + 0.5 * max(0.0, -k),
            "tegang": 0.6 * max(0.0, float(urg.get("keamanan", 0.0))),
            "mual": 0.7 * max(0.0, -c),
            "nyeri": 0.4 * max(0.0, -k),
            "ringan": 0.4 * max(0.0, e),
        }
        lr = jepit(float(self._p("felt_lr")), 0.05, 1.0)
        for name in NURANI_FELT_STATES:
            cur = float(self.felt_state.get(name, 0.0))
            tgt = jepit_01(target.get(name, 0.0))
            self.felt_state[name] = jepit_01(cur + lr * (tgt - cur))
        # somatic marker: sensasi kuat menandai nilai konteks (Damasio 1994)
        if self._felt("somatic_markers"):
            dominan = max(self.felt_state, key=lambda x: self.felt_state[x],
                          default=None)
            if dominan and self.felt_state[dominan] > 0.3:
                self.somatic_mark(self._somatic_tag(dominan),
                                  -self.felt_state[dominan],
                                  konteks=dominan, tick=tick)
        self._felt_tick = int(tick) if tick is not None else -1
        return dict(self.felt_state)

    @staticmethod
    def _somatic_tag(felt: str) -> str:
        return {"sesak": "keamanan", "jantung": "keamanan", "tegang": "keamanan",
                "nyeri": "keamanan", "lelah": "energi", "lapar": "energi",
                "mual": "koherensi", "ringan": "energi"}.get(felt, "koherensi")

    def felt_report(self) -> Dict[str, Any]:
        """'Aku tidak enak badan', 'aku merasa bersalah' — laporan rasa-dalam."""
        aktif = {k: round(v, 3) for k, v in self.felt_state.items()
                 if v >= float(self._p("felt_threshold"))}
        moral = {k: round(v, 3) for k, v in self.moral_emotions.items()
                 if v >= float(self._p("felt_threshold"))}
        kalimat = ""
        if aktif:
            kalimat = self._felt_phrase(max(aktif, key=lambda x: x[1]))
        if moral:
            kalimat += (("; " if kalimat else "") +
                        f"aku merasa {max(moral, key=lambda x: x[1])}")
        return {"aktif": self.felt_consciousness(), "felt": aktif,
                "moral": moral, "kalimat": kalimat}

    @staticmethod
    def _felt_phrase(name: str) -> str:
        return {
            "nyeri": "badanku nyeri", "lelah": "aku tidak enak badan",
            "lapar": "aku lapar", "sesak": "dadaku sesak",
            "jantung": "jantungku berdebar", "mual": "aku mual",
            "tegang": "tubuhku tegang", "ringan": "badanku ringan",
        }.get(name, f"aku merasa {name}")

    def moral_emotion(self, emosi: str, intensitas: float = 0.5,
                      sebab: str = "") -> float:
        """Suntik emosi moral (bersalah, malu, bangga, cemburu, iri, syukur...)."""
        if not self._felt("moral_emotions"):
            return 0.0
        key = NURANI_MORAL_ALIASES.get(str(emosi).lower(), str(emosi).lower())
        if key not in self.moral_emotions:
            return 0.0
        cur = float(self.moral_emotions[key])
        self.moral_emotions[key] = jepit_01(cur + float(self._p("moral_lr")) * float(intensitas))
        return self.moral_emotions[key]

    def somatic_mark(self, tag: str, valence: float, konteks: str = "",
                     tick: Optional[int] = None) -> Dict[str, Any]:
        """Tubuh menandai nilai sebelum pikiran sadar (somatic marker)."""
        if not self._felt("somatic_markers"):
            return {}
        entry = {"tick": int(tick) if tick is not None else 0,
                 "tag": str(tag)[:40], "valensi": jepit_drive(float(valence)),
                 "konteks": str(konteks)[:80]}
        self.somatic_markers.append(entry)
        cap = max(1, int(self._p("somatic_max")))
        if len(self.somatic_markers) > cap:
            self.somatic_markers = self.somatic_markers[-cap:]
        return entry

    def somatic_bias(self, top: int = 6) -> Dict[str, float]:
        """Nilai afektif bawah-sadar per tag (mem-bias keputusan)."""
        if not self._felt("somatic_markers"):
            return {}
        acc: Dict[str, float] = {}
        for m in self.somatic_markers[-top:]:
            tag = m.get("tag", "")
            acc[tag] = acc.get(tag, 0.0) + float(m.get("valensi", 0.0))
        return {k: round(v, 4) for k, v in acc.items()}

    def inner_speech(self, konteks: str = "", tick: Optional[int] = None) -> str:
        """Monolog batin berjalan (memperluas refleksi periodik narasi_diri)."""
        if not self._felt("inner_speech"):
            return ""
        t = int(tick) if tick is not None else (
            max((int(h.get("tick", 0)) for h in self._introspeksi_history),
                default=0))
        kalimat = self._inner_speech_text(konteks)
        if kalimat:
            entry = {"tick": t, "narasi": kalimat[:240], "kronis": [],
                     "bias": "", "akurasi": round(self.introspeksi_akurasi, 4),
                     "meta_d": round(self.meta_d_global, 4),
                     "jenis": "monolog_batin"}
            self.narasi_diri.append(entry)
            if len(self.narasi_diri) > 64:
                self.narasi_diri = self.narasi_diri[-64:]
        return kalimat

    def _inner_speech_text(self, konteks: str) -> str:
        low = str(konteks or "").lower()
        # tubuh yang tidak nyaman
        dominan = (max(self.felt_state, key=lambda x: self.felt_state[x])
                   if self.felt_state else None)
        if dominan and self.felt_state.get(dominan, 0.0) >= float(self._p("felt_threshold")):
            return self._felt_phrase(dominan)
        # kepercayaan diri rendah → keraguan
        if self.kepercayaan_global < 0.35:
            return "aku tidak yakin apakah aku benar"
        # drive kronis dari model diri
        kronis = [d for d in self.drives if float(self.model_diri.get(d, 0.0)) < -0.3]
        if kronis:
            frasa = {
                "energi": "aku harus beristirahat",
                "keamanan": "aku harus menjauh dari sini",
                "keingintahuan": "aku ingin tahu lebih banyak",
                "penguasaan": "aku harus bisa mengendalikan ini",
                "afiliasi": "aku ingin ada yang menemaniku",
                "koherensi": "kenapa semuanya terasa kacau?",
            }
            return frasa.get(kronis[0], f"aku merasa {kronis[0]} menekan")
        if low:
            return f"aku memikirkan {str(konteks)[:48]}"
        if self.kepercayaan_global > 0.7:
            return "aku tahu apa yang harus kulakukan"
        return ""

    def narrate_identity(self, klaim: str, kekuatan: float = 0.5,
                         tick: Optional[int] = None) -> List[Dict[str, Any]]:
        """Bentuk identitas naratif: 'aku orang yang tidak mudah percaya'."""
        if not self._felt("inner_speech"):
            return list(self.narrative_identity)
        claim = str(klaim)[:80]
        ada = next((x for x in self.narrative_identity
                    if x.get("klaim") == claim), None)
        if ada is not None:
            ada["kekuatan"] = jepit_01(float(ada.get("kekuatan", 0.0))
                                          + float(kekuatan) * 0.2)
        else:
            self.narrative_identity.append({
                "klaim": claim,
                "kekuatan": jepit_01(float(kekuatan)),
                "tick": int(tick) if tick is not None else 0})
        if len(self.narrative_identity) > 16:
            self.narrative_identity = self.narrative_identity[-16:]
        return list(self.narrative_identity)

    def narrative_identity_state(self) -> Dict[str, Any]:
        if not self.narrative_identity:
            return {"aktif": self._felt("inner_speech"), "kalimat": "",
                    "klaim": []}
        top = max(self.narrative_identity, key=lambda x: float(x.get("kekuatan", 0.0)))
        return {"aktif": self._felt("inner_speech"),
                "kalimat": f"aku orang yang {top.get('klaim')}",
                "klaim": [x.get("klaim") for x in self.narrative_identity]}

    # ---- monitoring realitas & keraguan metakognitif (konsep 6) ----
    def classify_source(self, item: Mapping[str, Any]) -> str:
        kind = str(item.get("kind", item.get("jenis", "")))
        if kind in ("mimpi", "dream"):
            return "mimpi"
        if kind in ("imajinasi", "goal", "future"):
            return "imajinasi"
        if kind in ("ingatan", "memori", "episodic", "wm"):
            return "ingatan"
        return "persepsi"

    def reality_monitoring(self, item: Mapping[str, Any],
                           tick: Optional[int] = None) -> Dict[str, Any]:
        """Bedakan persepsi / ingatan / imajinasi / mimpi + source memory."""
        if not self._felt("reality_monitoring"):
            return {}
        sumber = self.classify_source(item)
        keyakinan = 0.7
        # derau sumber: mimpi/imajinasi kadang terasa seperti ingatan nyata
        if sumber in ("mimpi", "imajinasi") and self._rng.random() < 0.15:
            sumber = "ingatan"
            keyakinan = 0.4
        entry = {"tick": int(tick) if tick is not None else 0,
                 "sumber": sumber, "isi": str(item.get("content",
                                                       item.get("teks", "")))[:80],
                 "keyakinan": round(keyakinan, 3)}
        self.reality_source_log.append(entry)
        if len(self.reality_source_log) > 48:
            self.reality_source_log = self.reality_source_log[-48:]
        return entry

    def source_memory(self, tentang: Optional[str] = None) -> Dict[str, Any]:
        if not self._felt("reality_monitoring"):
            return {}
        if tentang:
            hit = next((e for e in reversed(self.reality_source_log)
                        if str(tentang).lower() in e.get("isi", "").lower()),
                       None)
            if hit:
                return hit
        return self.reality_source_log[-1] if self.reality_source_log else {}

    def metacognitive_doubt(self, tingkat: Optional[float] = None) -> float:
        """'Aku tidak yakin', 'mungkin aku salah'."""
        if not self._felt("reality_monitoring"):
            return 0.0
        if tingkat is not None:
            self.doubt_level = jepit_01(self.doubt_level + float(self._p("doubt_lr"))
                * (float(tingkat) - self.doubt_level))
        else:
            self.doubt_level = jepit_01(self.doubt_level + 0.01 * (0.5 - self.kepercayaan_global))
        return self.doubt_level

    def confabulation(self, celah: str = "",
                      tick: Optional[int] = None) -> Dict[str, Any]:
        """Isi celah ingatan dengan cerita salah namun dipercaya."""
        if not self._felt("reality_monitoring"):
            return {}
        pilihan = [
            "aku yakin dialah yang melakukannya, meski aku tidak benar-benar ingat",
            "aku rasa itu terjadi pagi hari, tapi detailnya kabur",
            "aku ingat pernah ke sini — sebenarnya tidak",
            "mungkin itu mimpi, tapi terasa sungguh terjadi",
        ]
        dasar = f" tentang {str(celah)[:40]}." if celah else ""
        entry = {"tick": int(tick) if tick is not None else 0,
                 "celah": str(celah)[:80],
                 "cerita": self._rng.choice(pilihan) + dasar, "dipercaya": True}
        self.confabulation_log.append(entry)
        cap = max(1, int(self._p("confab_max")))
        if len(self.confabulation_log) > cap:
            self.confabulation_log = self.confabulation_log[-cap:]
        return entry

    def kesadaran_laporan(self) -> Dict[str, Any]:
        """Laporan terpadu pilar H untuk status/HUD."""
        return {
            "aktif": self.felt_consciousness(),
            "monolog_terakhir": (self.narasi_diri[-1]["narasi"]
                                 if self.narasi_diri else ""),
            "identitas": self.narrative_identity_state(),
            "terasa": self.felt_report(),
            "somatic_bias": self.somatic_bias(),
            "realitas": {
                "sumber_terakhir": (self.reality_source_log[-1]
                                    if self.reality_source_log else None),
                "doubt": round(self.doubt_level, 3),
                "konfabulasi": len(self.confabulation_log)},
        }

    def to_json(self, **json_kwargs: Any) -> str:
        import json
        json_kwargs.setdefault("ensure_ascii", False)
        return json.dumps(self.to_dict(include_params=True), **json_kwargs)

    @classmethod
    def from_json(cls, s: str) -> "Nurani":
        import json
        return cls.from_dict(json.loads(s))

    # ==================== demo berdiri sendiri (stdlib saja) ====================
    @classmethod
    def demo(cls, ticks: int = 120, seed: int = 11) -> Dict[str, Any]:
        """Demo empat pilar tanpa Naluri: nurani belajar dari dunia sintetis."""
        rng = random.Random(seed)
        params = dict(NURANI_DEFAULTS)
        for k in list(params):
            if k.startswith("enable_"):
                params[k] = True
        nur = cls(params=params)

        # --- pilar A: kata yang tidak ada di lexicon menjadi punya arti ---
        situasi = [
            ("saya tersesat di lorong gelap dan kehabisan bekal",
             {"keamanan": -0.5, "energi": -0.2}),
            ("saya menemukan pintu baru dan mencobanya segera",
             {"keingintahuan": +0.4, "penguasaan": +0.2}),
        ]
        for t in range(ticks):
            teks, deltas = situasi[t % len(situasi)]
            noisy = {d: v + rng.gauss(0, 0.02) for d, v in deltas.items()}
            nur.experience(teks, noisy, tick=t)
            nur.update_setpoints({d: rng.uniform(-0.8, 0.2) for d in nur.drives})
            nur.update_interoception({"energi": 0.4, "koherensi": 0.35,
                                      "keamanan": 0.2}, tick=t)
        # urutan kata berbeda tapi himpunan kata kunci sama -> signature sama,
        # jadi pengalaman masa lalu benar-benar terpakai untuk kalimat baru.
        prior = nur.anticipate("bekal kehabisan saya tersesat lorong gelap")
        echo = nur.interoceptive_echo({"energi": 0.4, "koherensi": 0.35,
                                       "keamanan": 0.2}, "koherensi")

        # --- pilar B: kalibrasi + gerbang hold-out ---
        pairs = [(rng.gauss(0.5, 0.3), rng.gauss(1.4, 0.3)) for _ in range(80)]
        for p, r in pairs:
            nur.record_observation(p, r, prob=0.7, success=r > 0,
                                   per_drive={"keamanan": abs(p - r)})
        skala, diterima, sebelum, sesudah = nur.scale_from_holdout(pairs, 1.0)

        # --- pilar D: konflik & kompromi ---
        goals = [{"drive": "keamanan", "urgency": 0.8},
                 {"drive": "keingintahuan", "urgency": 0.7}]
        cand: List[Dict[str, Any]] = [{"name": "nekat", "drive_effects": {"keamanan": -0.40, "keingintahuan": +0.50}},
                {"name": "menghindar", "drive_effects": {"keamanan": +0.45, "keingintahuan": -0.40}},
                {"name": "berani_hati_hati",
                 "drive_effects": {"keamanan": +0.15, "keingintahuan": +0.12}}]
        det = nur.detect_conflict(goals, cand)
        kompromi = next(c for c in cand if c["name"] == "berani_hati_hati")
        bonus = nur.compromise_bonus(kompromi["drive_effects"],
                                     "keamanan", "keingintahuan")

        # --- pilar E: memori sosial — relasi berevolusi lewat interaksi ---
        nur.meet("pemain", nama="Player", tick=0)
        for t in range(1, 6):
            nur.interact("pemain", muatan=+0.5, kepercayaan_delta=+0.4, tick=t)
        nur.interact("pemain", muatan=-0.9, kepercayaan_delta=-0.6, tick=6)
        rel = nur.relationship("pemain")
        prior_sosial = nur.social_prior("pemain")

        print("=== NURANI demo (konsep 17) ===")
        print(f"  prior afektif (kalimat setara)   : keamanan={prior['keamanan']:+.3f} "
              f"energi={prior['energi']:+.3f}")
        print(f"  gema interosepsi koherensi    : {echo:+.4f}")
        print("  setpoint drift                : "
              + " ".join(f"{d}={nur.setpoints[d]:+.3f}" for d in nur.drives))
        print(f"  brier={nur.calibration_report().brier:.3f} "
              f"skala {1.0:.2f}->{skala:.2f} "
              f"({'diterima' if diterima else 'ditolak'}, "
              f"hold-out {sebelum:.4f}->{sesudah:.4f})")
        print(f"  konflik: {det['ada']} - {det['penjelasan']}")
        print("  bonus kompromi: " + f"{bonus:+.4f}   satu hari sirkadian: "
              + " ".join(f"{t}:{nur.circadian_phase(t)}" for t in (2, 8, 14, 20)))
        print(f"  relasi 'pemain' (5x baik, 1x buruk): valensi={rel['valensi']:+.3f} "
              f"kepercayaan={rel['kepercayaan']:+.3f} akrab={rel['akrab']:.3f}")
        print("  prior sosial -> bias drive: "
              + " ".join(f"{k}={v:+.3f}" for k, v in prior_sosial.items()))

        # --- pilar F: persepsi — psikofisika saluran (tanpa Naluri) ---
        rng_p = random.Random(seed + 5)
        lemah = sum(1 for _ in range(200)
                    if nur.deteksi("keamanan", 0.005, rng_p)[1] == "sadar")
        kuat = sum(1 for _ in range(200)
                   if nur.deteksi("keamanan", 0.5, rng_p)[1] == "sadar")
        nur.params["persepsi_kriterion"] = {"keamanan": -0.5}
        hiper = sum(1 for _ in range(200)
                    if nur.deteksi("keamanan", 0.005, rng_p)[1] == "sadar")
        nur.params["persepsi_kriterion"] = 0.0
        m_pre = nur.kompres("keamanan", 0.4)
        for _ in range(150):
            nur.update_adaptasi({"keamanan": 0.5})
        m_post = nur.kompres("keamanan", 0.4)
        nur.belajar_persepsi({"keamanan": 0.0})
        print(f"  persepsi: stimulus lemah sadar {lemah}/200 vs kuat "
              f"{kuat}/200; hipervigilan (criterion −0.5) {hiper}/200")
        print(f"  Weber-Fechner: 0.4 → {m_pre:.3f}; setelah teradaptasi "
              f"{nur.adaptasi['keamanan']:.2f} → {m_post:.3f}; "
              f"d' belajar {nur.sensitivitas['keamanan']:.3f}")

        # --- pilar G: introspeksi diri (interosepsi sadar + metakognisi) ---
        # Simulasi 80 tick self-monitoring dengan derau, lalu evaluasi meta-d'
        rng_i = random.Random(seed + 9)
        for t in range(80):
            lvl = {d: rng_i.uniform(-0.6, 0.4) for d in nur.drives}
            urg = {d: max(0.0, -lvl[d]) for d in nur.drives}
            nur.update_introspection(lvl, urg, valence=rng_i.uniform(-0.4, 0.6),
                                     arousal=rng_i.uniform(0.1, 0.7), tick=t, rng=rng_i)
            # metakognisi: prediksi benar jika akurasi tinggi
            benar = rng_i.random() < (0.5 + 0.3 * nur.introspeksi_akurasi)
            conf = 0.5 + 0.4 * nur.kepercayaan_global + rng_i.gauss(0, 0.1)
            nur.update_introspection(lvl, urg, tick=t, prediksi_benar=benar,
                                     confidence_pred=conf, rng=rng_i)
        intro_state = nur.introspeksi_state()
        meta_lap = nur.meta_kognisi_laporan()
        refleksi = nur.refleksi_diri(80, {d: 0.0 for d in nur.drives}, {d: 0.0 for d in nur.drives})
        print(f"  introspeksi: akurasi interoseptif r={intro_state['akurasi']:.3f} "
              f"bias={intro_state['bias']:+.3f} kepercayaan={intro_state['kepercayaan_global']:.2f} "
              f"meta-d'={intro_state['meta_d_global']:.2f} sadar={intro_state['sadar_diri_ticks']}x")
        print(f"  meta-kognisi: Brier conf={meta_lap['brier_confidence']:.3f} "
              f"refleksi={nur.refleksi_count}x")
        print(f"  narasi diri: {refleksi['narasi'][:120]}...")
        return {"prior": prior, "gema": echo, "skala": skala,
                "diterima": diterima, "konflik": det["ada"], "bonus": bonus,
                "relasi": rel, "prior_sosial": prior_sosial,
                "persepsi": {"lemah_sadar": lemah, "kuat_sadar": kuat,
                             "hiper_sadar": hiper, "kompres": (m_pre, m_post),
                             "d_belajar": nur.sensitivitas["keamanan"]},
                "introspeksi": intro_state, "meta": meta_lap}














# >>> ORGANIK-BLOCK-START (nurani) <<<
# =====================================================================
# INTEGRASI LUKA DOMAIN (pycos.mandiri.organik)
#   2. LukaDomain -> Nurani: luka MENGECUALIKAN domain, bukan menurunkan angka.
#      break_trust() membuat lubang; bayar_utang() melunasi daftar tetapi
#      TIDAK menambal lubang. Skalar bisa pulih; lubang tetap lubang.
# =====================================================================
def _nurani_luka(self: Any) -> Optional["LukaDomain"]:
    lk = cast(Optional["LukaDomain"], getattr(self, "_luka", None))
    if lk is None:
        modul = optional_module("pycos.mandiri.organik")
        if modul is None:
            return None
        lk = modul.LukaDomain()
        self._luka = lk
    return cast(Optional["LukaDomain"], lk)


def hancurkan_domain(self: Any, ent: Any, domain: str = "*", alasan: str = "", tick: int = 0, permanen: bool = True) -> Optional[Dict[str, Any]]:
    lk = _nurani_luka(self)
    return None if lk is None else lk.lukai(ent, domain, alasan, tick, permanen)


def dikecualikan(self: Any, ent: Any, domain: str = "*") -> bool:
    lk = cast(Optional["LukaDomain"], getattr(self, "_luka", None))
    return False if lk is None else lk.dikecualikan(ent, domain)


def domain_terluka(self: Any, ent: Any) -> List[str]:
    lk = cast(Optional["LukaDomain"], getattr(self, "_luka", None))
    return [] if lk is None else lk.domain_terluka(ent)


def terapkan_domain(self: Any, ent: Any, domain: str, skalar: float) -> Optional[float]:
    """None bila domain adalah lubang. Skalar tidak berlaku di sana."""
    lk = cast(Optional["LukaDomain"], getattr(self, "_luka", None))
    return float(skalar) if lk is None else lk.terapkan(ent, domain, skalar)


def tambal_luka(self: Any, ent: Any, domain: str = "*") -> bool:
    lk = cast(Optional["LukaDomain"], getattr(self, "_luka", None))
    return False if lk is None else lk.tambal(ent, domain)


def luka_state(self: Any) -> Dict[str, List[str]]:
    lk = cast(Optional["LukaDomain"], getattr(self, "_luka", None))
    return {} if lk is None else lk.ringkas()


_fn: Callable[..., Any]
for _nama, _fn in (("hancurkan_domain", hancurkan_domain),
                   ("dikecualikan", dikecualikan),
                   ("domain_terluka", domain_terluka),
                   ("terapkan_domain", terapkan_domain),
                   ("tambal_luka", tambal_luka),
                   ("luka_state", luka_state)):
    install_method(Nurani, _nama, _fn,
                   patch_id="nurani.extension.Nurani." + _nama)


def _luka_break_trust(original: Callable[..., Any], self: Any, ent: Any, severity: float = 0.7, tick: int = 0, *a: Any, **k: Any) -> Any:
    """Kepercayaan hancur = LUBANG, bukan sekadar skalar rendah."""
    hasil = original(self, ent, severity, tick, *a, **k)
    try:
        if float(severity) >= 0.6:
            self.hancurkan_domain(ent, "*", alasan="kepercayaan hancur",
                                  tick=tick, permanen=True)
    except Exception:
        pass
    return hasil


wrap_method(Nurani, "break_trust", _luka_break_trust,
            patch_id="nurani.organik.break_trust")


def _luka_relationship(original: Callable[..., Any], self: Any, ent: Any) -> Any:
    d = original(self, ent)
    try:
        if isinstance(d, dict):
            dom = self.domain_terluka(ent)
            if dom:
                d["lubang"] = dom
                d["catatan_lubang"] = "domain ini tidak berlaku - bukan sekadar rendah"
    except Exception:
        pass
    return d


wrap_method(Nurani, "relationship", _luka_relationship,
            patch_id="nurani.organik.relationship")


def _nurani_luka_ambil(self: Any) -> Dict[str, Any]:
    lk = cast(Optional["LukaDomain"], getattr(self, "_luka", None))
    return lk.to_dict() if lk is not None else {}


def _nurani_luka_pasang(self: Any, d: Any) -> None:
    modul = optional_module("pycos.mandiri.organik")
    if modul is None:
        return
    try:
        self._luka = modul.LukaDomain.from_dict(d)
    except (AttributeError, TypeError, ValueError):
        pass


def _luka_to_dict(original: Callable[..., Any], self: Any, *a: Any, **k: Any) -> Any:
    data = original(self, *a, **k)
    if isinstance(data, dict):
        try:
            data["luka"] = _nurani_luka_ambil(self)
        except Exception:
            pass
    return data


def _luka_from_dict(original: Callable[..., Any], cls: Any, data: Any, *a: Any, **k: Any) -> Any:
    hasil = original(cls, data, *a, **k)
    if isinstance(data, Mapping) and data.get("luka"):
        try:
            _nurani_luka_pasang(hasil, data["luka"])
        except Exception:
            pass
    return hasil


wrap_method(Nurani, "to_dict", _luka_to_dict,
            patch_id="nurani.organik.serialisasi")
wrap_method(Nurani, "from_dict", _luka_from_dict,
            patch_id="nurani.organik.deserialisasi")
# >>> ORGANIK-BLOCK-END (nurani) <<<


# ===========================================================================
# INTEGRASI: AMBANG KECURIGAAN DINAMIS + KONSULTASI GRAF ASOSIASI
# Posterior kepercayaan (JejakPrediksi) dibandingkan dengan ambang yang
# berubah mengikuti relasi/viskositas — bukan konstanta.
# ===========================================================================
def _nurani_ambang_kecurigaan(self: Any, ent: Any = None, dasar: Optional[float] = None) -> float:
    p = getattr(self, "params", {}) or {}
    base = float(dasar if dasar is not None
                 else p.get("nurani_ambang_curiga", 0.35))
    koreksi = 0.0
    if ent is not None:
        try:
            r = self.relationship(ent)
            t = float(r.get("kepercayaan", 0.0))
            koreksi += -0.18 * max(0.0, t)
            koreksi += -0.12 * max(0.0, -t)
            if r.get("hancur"):
                koreksi += 0.25
        except Exception:
            pass
    return jepit(base + koreksi, 0.05, 0.9)


def _nurani_sambungkan_graf(self: Any, graf: Any) -> Any:
    self._graf_asosiasi = graf
    return self


def _nurani_asosiasi_emosi(self: Any, konsep: str, minimum: float = 0.08) -> Dict[str, float]:
    g = cast(Optional["GrafAsosiasi"], getattr(self, "_graf_asosiasi", None))
    if g is None:
        return {}
    return g.emosi_terasosiasi(konsep, minimum)


def _nurani_bias_asosiatif(self: Any, konsep: str, skala: float = 0.5) -> Dict[str, float]:
    """Sinyal afektif yang muncul dari asosiasi graf (embrio fobia)."""
    out = {}
    for node, w in self.asosiasi_emosi(konsep).items():
        out[node] = round(float(w) * float(skala), 4)
    return out


for _nama, _fn in (("ambang_kecurigaan", _nurani_ambang_kecurigaan),
                   ("sambungkan_graf", _nurani_sambungkan_graf),
                   ("asosiasi_emosi", _nurani_asosiasi_emosi),
                   ("bias_asosiatif", _nurani_bias_asosiatif)):
    install_method(Nurani, _nama, _fn,
                   patch_id="nurani.extension.Nurani." + _nama)


# ===========================================================================
# KESELARASAN UJARAN — PENILAI (dulu pycos.selaras.penilai)
# ===========================================================================
# Empat dimensi dinilai. Setiap dimensi punya **observasi** (ciri linguistik
# dari `pycos.bahasa.tutur.analisis_teks`) dan **target** (dari keadaan batin,
# dicampur sifat persona). Skor dimensi:
#
# * ``valensi``    : 1 − |obs − target| / 2, dengan obs, target di [−1, 1];
# * ``register``   : 1 − |obs − target| / 2, dengan target ±0,8 (formal/santai);
# * ``gairah``     : 1 − |obs − target|, dengan obs, target di [0, 1];
# * ``keraguan``   : 1 − |obs − target|, dengan obs, target di [0, 1].
#
# Campuran target: ``target = (1 − w)·keadaan + w·sifat`` dengan ``w = 0,5``.
# Bila persona tidak menetapkan sifat terkait, target murni dari keadaan batin.
#
# Aturan keras: bila ujaran memuat kata pantangan persona, skor dibatasi ke 0,4
# dan status menjadi ``melanggar_pantangan``. Dimensi tanpa observasi tidak
# ikut dirata-rata; bila tidak ada dimensi yang dapat dinilai, skor ``None``.
#
# Ambang (0,75 / 0,5 / 0,4, bobot 0,5) adalah pilihan desain yang belum
# divalidasi terhadap penilaian manusia (lihat VALIDATION.md).
BOBOT_SIFAT = 0.5
AMBANG_SELARAS = 0.75
AMBANG_SEBAGIAN = 0.5
PLAFON_PANTANGAN = 0.4
TARGET_REGISTER = {"formal": 0.8, "santai": -0.8}


@dataclass(frozen=True)
class DimensiSkor:
    nama: str
    observasi: Optional[float]
    target: Optional[float]
    skor: Optional[float]
    catatan: str

    def to_dict(self) -> Dict[str, Any]:
        return {"nama": self.nama, "observasi": self.observasi,
                "target": self.target, "skor": self.skor, "catatan": self.catatan}


@dataclass(frozen=True)
class Laporan:
    persona: str
    dimensi: Tuple[DimensiSkor, ...]
    pelanggaran: Tuple[str, ...]
    skor: Optional[float]
    status: str
    saran: Tuple[str, ...]

    def skor_dimensi(self) -> Dict[str, Optional[float]]:
        return {d.nama: d.skor for d in self.dimensi}

    def to_dict(self) -> Dict[str, Any]:
        return {"persona": self.persona,
                "dimensi": [d.to_dict() for d in self.dimensi],
                "pelanggaran": list(self.pelanggaran), "skor": self.skor,
                "status": self.status, "saran": list(self.saran)}


def _campur(dasar: float, sifat: Optional[float]) -> float:
    """Campur target keadaan dengan sifat persona (sifat sudah dipetakan)."""
    if sifat is None:
        return dasar
    return (1.0 - BOBOT_SIFAT) * dasar + BOBOT_SIFAT * sifat


def _skor(obs: float, target: float, rentang: float) -> float:
    return max(0.0, 1.0 - abs(obs - target) / rentang)


def _saran_dimensi(nama: str, obs: float, target: float) -> str:
    kurang = obs < target
    if nama == "valensi":
        return ("tambahkan nuansa positif dan kurangi kata negatif"
                if kurang else "kurangi nuansa positif; sesuaikan dengan keadaan")
    if nama == "register":
        return ("gunakan register lebih formal (saya, anda, mohon)"
                if kurang else "gunakan register lebih santai (aku, kamu)")
    if nama == "gairah":
        return ("tambahkan penekanan secukupnya (tanda seru, kata penguat)"
                if kurang else "kurangi tanda seru dan kata penguat")
    return ("tambahkan ungkapan ragu (mungkin, sepertinya)"
            if kurang else "kurangi ungkapan ragu dan nyatakan lebih tegas")


def nilai_selaras(persona: "Persona", keadaan: "Keadaan", teks: str,
                  leksikon: Optional["LeksikonCiri"] = None) -> Laporan:
    """Nilai `teks` terhadap `persona` dan `keadaan`. Tidak pernah mengubah input.

    `persona` dan `keadaan` duck-typed (cukup atribut `nama`/`sifat_of`/
    `register`/`pantangan` dan `valensi`/`gairah`/`ketidakpastian`). `leksikon`
    opsional; bila None, leksikon ciri bawaan `pycos.bahasa.tutur` dipakai.
    """
    from pycos.bahasa.tutur import analisis_teks, token_dari

    fitur = analisis_teks(teks, leksikon)
    dimensi = []

    obs = fitur.polaritas()
    hangat = persona.sifat_of("hangat")
    tgt = _campur(keadaan.valensi, None if hangat is None else 2.0 * hangat - 1.0)
    dimensi.append(_dimensi("valensi", obs, tgt, 2.0,
                            "tidak ada kata sentimen" if obs is None else ""))

    if persona.register == "netral":
        dimensi.append(DimensiSkor("register", None, None, None,
                                   "persona netral: register tidak dinilai"))
    else:
        obs = fitur.formalitas()
        tgt = TARGET_REGISTER[persona.register]
        dimensi.append(_dimensi("register", obs, tgt, 2.0,
                                "tidak ada kata register" if obs is None else ""))

    obs = fitur.intensitas()
    tgt = _campur(keadaan.gairah, persona.sifat_of("ekspresif"))
    dimensi.append(_dimensi("gairah", obs, tgt, 1.0,
                            "ujaran kosong" if obs is None else ""))

    obs = fitur.keraguan()
    tgt = _campur(keadaan.ketidakpastian, persona.sifat_of("ragu"))
    dimensi.append(_dimensi("keraguan", obs, tgt, 1.0,
                            "ujaran kosong" if obs is None else ""))

    hasil_dimensi = tuple(dimensi)
    token = " " + " ".join(token_dari(teks)) + " "
    pelanggaran = tuple(p for p in persona.pantangan
                        if " " + " ".join(token_dari(p)) + " " in token)

    nilai = [d.skor for d in dimensi if d.skor is not None]
    skor = round(sum(nilai) / len(nilai), 3) if nilai else None
    if pelanggaran:
        skor = PLAFON_PANTANGAN if skor is None else min(skor, PLAFON_PANTANGAN)
        status = "melanggar_pantangan"
    elif skor is None:
        status = "tidak_dapat_dinilai"
    elif skor >= AMBANG_SELARAS:
        status = "selaras"
    elif skor >= AMBANG_SEBAGIAN:
        status = "sebagian"
    else:
        status = "tidak_selaras"

    saran = [_saran_dimensi(d.nama, d.observasi, d.target) for d in dimensi
             if d.skor is not None and d.skor < AMBANG_SELARAS
             and d.observasi is not None and d.target is not None]
    saran += ["hapus kata pantangan: {}".format(p) for p in pelanggaran]
    return Laporan(persona=persona.nama, dimensi=hasil_dimensi, pelanggaran=pelanggaran,
                   skor=skor, status=status, saran=tuple(saran))


def _dimensi(nama: str, obs: Optional[float], tgt: float, rentang: float,
             catatan_kosong: str) -> DimensiSkor:
    if obs is None:
        return DimensiSkor(nama, None, round(tgt, 3), None, catatan_kosong)
    return DimensiSkor(nama, round(obs, 3), round(tgt, 3),
                       round(_skor(obs, tgt, rentang), 3), "")


# ===========================================================================
# KESELARASAN UJARAN — PELACAK DRIFT (dulu pycos.selaras.pelacak)
# ===========================================================================
# `PelacakSelaras` menyimpan skor `Laporan` terakhir dalam jendela berukuran
# tetap (memori terbatas). Untuk setiap seri (skor keseluruhan dan tiap
# dimensi) ia menghitung kemiringan regresi linear atas urutan skor:
#
# * ``menurun``    — kemiringan ≤ −ambang: ujaran makin menjauh dari persona;
# * ``meningkat``  — kemiringan ≥ +ambang;
# * ``stabil``     — di antara keduanya;
# * ``belum_cukup``— jumlah sampel di bawah `min_sampel`.
#
# Skor dimensi yang `None` (tidak dapat dinilai) dilewati, bukan dianggap nol.
def _kemiringan(nilai: Sequence[float]) -> float:
    """Kemiringan kuadrat-terkecil terhadap indeks 0..n-1."""
    n = len(nilai)
    rerata_x = (n - 1) / 2.0
    rerata_y = sum(nilai) / n
    pembilang = sum((i - rerata_x) * (y - rerata_y) for i, y in enumerate(nilai))
    penyebut = sum((i - rerata_x) ** 2 for i in range(n))
    return pembilang / penyebut if penyebut else 0.0


class PelacakSelaras:
    """Pelacak drift persona lintas giliran dengan memori jendela tetap."""

    def __init__(self, kapasitas: int = 60, min_sampel: int = 5,
                 ambang_tren: float = 0.01) -> None:
        if isinstance(kapasitas, bool) or not isinstance(kapasitas, int) or kapasitas < 2:
            raise ValueError("kapasitas harus bilangan bulat >= 2")
        if isinstance(min_sampel, bool) or not isinstance(min_sampel, int) or min_sampel < 2:
            raise ValueError("min_sampel harus bilangan bulat >= 2")
        if min_sampel > kapasitas:
            raise ValueError("min_sampel tidak boleh melebihi kapasitas")
        if isinstance(ambang_tren, bool) or not isinstance(ambang_tren, (int, float)) \
                or not math.isfinite(ambang_tren) or not ambang_tren >= 0:
            raise ValueError("ambang_tren harus angka berhingga >= 0")
        self.kapasitas = kapasitas
        self.min_sampel = min_sampel
        self.ambang_tren = float(ambang_tren)
        self._riwayat: Deque[Tuple[Optional[float], Dict[str, Optional[float]]]] = \
            deque(maxlen=kapasitas)

    def __len__(self) -> int:
        return len(self._riwayat)

    def catat(self, laporan: Laporan) -> None:
        if not isinstance(laporan, Laporan):
            raise TypeError("catat menerima Laporan, bukan {}".format(
                type(laporan).__name__))
        self._riwayat.append((laporan.skor, laporan.skor_dimensi()))

    def kosongkan(self) -> None:
        self._riwayat.clear()

    def _seri(self) -> Dict[str, List[float]]:
        seri: Dict[str, List[float]] = {"keseluruhan": []}
        for skor, dimensi in self._riwayat:
            if skor is not None:
                seri["keseluruhan"].append(skor)
            for nama, nilai in dimensi.items():
                if nilai is not None:
                    seri.setdefault(nama, []).append(nilai)
        return seri

    def tren(self) -> Dict[str, Dict[str, Any]]:
        """Ringkasan per seri: jumlah sampel, rerata, kemiringan, dan status."""
        hasil: Dict[str, Dict[str, Any]] = {}
        for nama, nilai in self._seri().items():
            n = len(nilai)
            if n < self.min_sampel:
                status, miring = "belum_cukup", None
            else:
                miring = _kemiringan(nilai)
                if miring == 0.0:
                    status = "stabil"
                elif miring <= -self.ambang_tren:
                    status = "menurun"
                elif miring >= self.ambang_tren:
                    status = "meningkat"
                else:
                    status = "stabil"
                miring = round(miring, 5)
            hasil[nama] = {"sampel": n,
                           "rerata": round(sum(nilai) / n, 3) if n else None,
                           "kemiringan": miring, "status": status}
        return hasil


# ===========================================================================
# KALIBRASI KORPUS BERLABEL (dulu pycos.selaras.kalibrasi)
# ===========================================================================
# Korpus berformat JSON Lines; setiap baris satu contoh. Hanya `teks` yang
# wajib:
#
#     {"teks": "aku senang!", "polaritas": 1, "formalitas": "santai",
#      "selaras": true, "keadaan": {"valensi": 0.6, "gairah": 0.7}}
#
# * ``polaritas``  — -1, 0, atau 1 (label untuk ciri polaritas);
# * ``formalitas`` — "formal", "santai", atau "netral";
# * ``selaras``    — true/false untuk penilaian keseluruhan. Bila ada, ``persona``
#   (dict) dan ``keadaan`` (dict) dipakai; tanpa keduanya, default
#   ``PERSONA_CONTOH`` dan ``Keadaan()``.
#
# Ukuran: akurasi + kappa Cohen (dengan cakupan) untuk polaritas/formalitas;
# akurasi biner keselarasan pada ambang tertentu; pencarian ambang dengan
# pemisahan latih/uji 70/30 (ambang yang dipilih dan diuji pada data yang sama
# tidak dilaporkan sebagai akurasi).
#
# Mengukur kesesuaian dengan label yang diberikan. Ia tidak membuktikan bahwa
# label itu benar; kualitas label adalah tanggung jawab pemberi label.
KUNCI_KORPUS = ("teks", "polaritas", "formalitas", "selaras", "persona", "keadaan", "id", "anotasi")
_FORMALITAS = ("formal", "santai", "netral")


@dataclass(frozen=True)
class ContohLabel:
    teks: str
    polaritas: Optional[int] = None
    formalitas: Optional[str] = None
    selaras: Optional[bool] = None
    persona: Optional["Persona"] = None
    keadaan: Optional["Keadaan"] = None
    id_contoh: Optional[str] = None
    anotasi: Mapping[str, bool] = field(default_factory=dict)


def _validasi_anotasi(anotasi: Any, lokasi: str) -> Dict[str, bool]:
    if not isinstance(anotasi, Mapping):
        raise ValueError(lokasi + ".anotasi harus mapping anotator ke bool")
    hasil = {}
    for nama, label in anotasi.items():
        if not isinstance(nama, str) or not nama.strip() or nama != nama.strip():
            raise ValueError(lokasi + ".anotasi: identitas anotator tidak sah")
        if not isinstance(label, bool):
            raise ValueError(lokasi + ".anotasi[{}] harus bool".format(nama))
        hasil[nama] = label
    return hasil


def contoh_dari_dict(data: Mapping[str, Any], nomor: int = 0) -> ContohLabel:
    from pycos.inti.persona import Keadaan, Persona

    lokasi = "contoh #{}".format(nomor)
    hanya_kunci(dict(data), KUNCI_KORPUS, lokasi)
    teks = teks_wajib(data.get("teks"), lokasi + ".teks")
    pol = data.get("polaritas")
    if pol is not None and (isinstance(pol, bool) or pol not in (-1, 0, 1)):
        raise ValueError("{}.polaritas harus -1, 0, 1, atau null".format(lokasi))
    form = data.get("formalitas")
    if form is not None and form not in _FORMALITAS:
        raise ValueError("{}.formalitas harus salah satu dari {}".format(
            lokasi, ", ".join(_FORMALITAS)))
    sel = data.get("selaras")
    if sel is not None and not isinstance(sel, bool):
        raise ValueError("{}.selaras harus true, false, atau null".format(lokasi))
    persona = Persona.from_dict(data["persona"]) if data.get("persona") is not None else None
    keadaan = Keadaan.from_dict(data["keadaan"]) if data.get("keadaan") is not None else None
    identitas = data.get("id")
    if identitas is not None:
        identitas = teks_wajib(identitas, lokasi + ".id")
    anotasi = _validasi_anotasi(data.get("anotasi", {}), lokasi)
    return ContohLabel(teks=teks, polaritas=pol, formalitas=form, selaras=sel,
                       persona=persona, keadaan=keadaan, id_contoh=identitas, anotasi=anotasi)


def muat_korpus(path: str) -> List[ContohLabel]:
    """Baca korpus JSONL. Baris kosong dilewati; galat menyebut nomor baris."""
    hasil: List[ContohLabel] = []
    with open(path, "r", encoding="utf-8") as f:
        for nomor, baris in enumerate(f, start=1):
            if not baris.strip():
                continue
            try:
                data = json.loads(baris)
            except json.JSONDecodeError as galat:
                raise ValueError("baris {}: JSON tidak valid ({})".format(nomor, galat))
            if not isinstance(data, dict):
                raise ValueError("baris {}: harus objek JSON".format(nomor))
            try:
                hasil.append(contoh_dari_dict(data, nomor))
            except ValueError as galat:
                raise ValueError("baris {}: {}".format(nomor, galat))
    if not hasil:
        raise ValueError("korpus kosong: {}".format(path))
    return hasil


def kappa_cohen(pasangan: Sequence[Tuple[Any, Any]]) -> Optional[float]:
    """Kappa Cohen untuk pasangan (label, prediksi). None bila tidak terdefinisi."""
    n = len(pasangan)
    if n == 0:
        return None
    label = sorted({a for a, _ in pasangan} | {b for _, b in pasangan}, key=str)
    po = sum(1 for a, b in pasangan if a == b) / n
    pe = sum((sum(1 for a, _ in pasangan if a == k) / n)
             * (sum(1 for _, b in pasangan if b == k) / n) for k in label)
    if math.isclose(pe, 1.0):
        return 1.0 if math.isclose(po, 1.0) else 0.0
    return (po - pe) / (1.0 - pe)


def _bulat(x: Optional[float]) -> Optional[float]:
    return None if x is None else round(x, 3)


def _ringkas(pasangan: List[Tuple[Any, Any]], total: int) -> Dict[str, Any]:
    dinilai = [(a, b) for a, b in pasangan if b is not None]
    benar = sum(1 for a, b in dinilai if a == b)
    return {"label": total,
            "cakupan": round(len(dinilai) / total, 3) if total else None,
            "akurasi": round(benar / len(dinilai), 3) if dinilai else None,
            "kappa": None if not dinilai else _bulat(kappa_cohen(dinilai))}


def ukur_fitur(korpus: Sequence[ContohLabel],
               leksikon: Optional["LeksikonCiri"] = None) -> Dict[str, Any]:
    """Akurasi dan kappa ciri polaritas dan formalitas terhadap label."""
    from pycos.bahasa.tutur import analisis_teks

    pol: List[Tuple[Any, Any]] = []
    form: List[Tuple[Any, Any]] = []
    for c in korpus:
        f = analisis_teks(c.teks, leksikon)
        if c.polaritas is not None:
            p = f.polaritas()
            pred = None if p is None else (1 if p > 0 else -1 if p < 0 else 0)
            pol.append((c.polaritas, pred))
        if c.formalitas is not None:
            r = f.formalitas()
            pred_form = None if r is None else ("formal" if r > 0 else "santai" if r < 0 else "netral")
            form.append((c.formalitas, pred_form))
    return {"polaritas": _ringkas(pol, len(pol)),
            "formalitas": _ringkas(form, len(form))}


def _skor_selaras(c: ContohLabel, leksikon: Optional["LeksikonCiri"]) -> Optional[float]:
    from pycos.inti.persona import PERSONA_CONTOH, Keadaan

    laporan = nilai_selaras(c.persona or PERSONA_CONTOH, c.keadaan or Keadaan(),
                            c.teks, leksikon)
    return laporan.skor


def _akurasi_ambang(data: List[Tuple[Optional[float], bool]],
                    ambang: float) -> Tuple[Optional[float], int]:
    dinilai = [(s >= ambang, y) for s, y in data if s is not None]
    if not dinilai:
        return None, 0
    return sum(1 for p, y in dinilai if p == y) / len(dinilai), len(dinilai)


def ukur_selaras(korpus: Sequence[ContohLabel],
                 leksikon: Optional["LeksikonCiri"] = None,
                 ambang: float = AMBANG_SELARAS,
                 porsi_latih: float = 0.7) -> Dict[str, Any]:
    """Akurasi keselarasan pada ambang default, dan pencarian ambang latih/uji."""
    berlabel = [c for c in korpus if c.selaras is not None]
    if len(berlabel) < 4:
        return {"label": len(berlabel), "keterangan": "butuh minimal 4 contoh berlabel"}
    data = [(_skor_selaras(c, leksikon), c.selaras) for c in berlabel
            if c.selaras is not None]
    akurasi_default, n_default = _akurasi_ambang(data, ambang)

    batas = int(len(data) * porsi_latih)
    latih, uji = data[:batas], data[batas:]
    if len(latih) < 2 or len(uji) < 2:
        return {"label": len(berlabel), "ambang_default": ambang,
                "akurasi_default": _bulat(akurasi_default),
                "keterangan": "porsi latih/uji terlalu kecil untuk pencarian ambang"}
    kisi = [round(0.30 + 0.05 * i, 2) for i in range(14)]          # 0.30 … 0.95
    terbaik = None
    for t in kisi:
        acc, _ = _akurasi_ambang(latih, t)
        if acc is None:
            continue
        # seri: pilih yang paling dekat dengan ambang default
        kunci = (acc, -abs(t - ambang))
        if terbaik is None or kunci > terbaik[0]:
            terbaik = (kunci, t)
    if terbaik is None:
        return {"label": len(berlabel), "keterangan": "tidak ada skor dapat dinilai"}
    ambang_latih = terbaik[1]
    akurasi_latih, _ = _akurasi_ambang(latih, ambang_latih)
    akurasi_uji, n_uji = _akurasi_ambang(uji, ambang_latih)
    return {
        "label": len(berlabel),
        "dinilai_default": n_default,
        "ambang_default": ambang,
        "akurasi_default": _bulat(akurasi_default),
        "ambang_latih": ambang_latih,
        "akurasi_latih": _bulat(akurasi_latih),
        "akurasi_uji": _bulat(akurasi_uji),
        "dinilai_uji": n_uji,
        "porsi_latih": porsi_latih,
    }


def _evaluasi_eksternal(latih: Sequence[ContohLabel], uji: Sequence[ContohLabel],
                        leksikon: Optional["LeksikonCiri"], sumber: Optional[str]) -> Dict[str, Any]:
    from itertools import combinations

    def identitas(rows: Sequence[ContohLabel], nama: str) -> Tuple[Set[str], Set[str]]:
        ids, teks = set(), set()
        for i, c in enumerate(rows):
            if not isinstance(c, ContohLabel):
                raise ValueError("{}[{}] harus ContohLabel".format(nama, i))
            t = " ".join(teks_wajib(c.teks, nama + ".teks").casefold().split())
            if c.id_contoh is not None:
                key = teks_wajib(c.id_contoh, nama + ".id")
                if key in ids:
                    raise ValueError(nama + ": id contoh duplikat: " + key)
                ids.add(key)
            if t in teks:
                raise ValueError(nama + ": teks contoh duplikat")
            teks.add(t)
            _validasi_anotasi(c.anotasi, nama)
            if c.selaras is not None and not isinstance(c.selaras, bool):
                raise ValueError(nama + ".selaras harus bool atau None")
        return ids, teks

    ids_latih, teks_latih = identitas(latih, "pengembangan")
    ids_uji, teks_uji = identitas(uji, "uji")
    if ids_latih & ids_uji or teks_latih & teks_uji:
        raise ValueError("korpus pengembangan/uji tumpang tindih (id atau teks)")
    if sumber is not None:
        sumber = teks_wajib(sumber, "sumber_pihak_ketiga")
    nama = sorted({a for c in uji for a in c.anotasi})
    pasangan = []
    for kiri, kanan in combinations(nama, 2):
        labels = [(c.anotasi[kiri], c.anotasi[kanan]) for c in uji
                  if kiri in c.anotasi and kanan in c.anotasi]
        # Konvensi kappa legacy satu kelas = 1 tidak dipakai untuk bukti
        # antar-anotator: peluang kesepakatan 1 berarti tak terdefinisi.
        degenerate = bool(labels) and len({a for pair in labels for a in pair}) == 1
        kappa = kappa_cohen(labels) if len(labels) >= 2 and not degenerate else None
        pasangan.append({"anotator": [kiri, kanan], "jumlah_pasangan": len(labels),
                         "kappa": _bulat(kappa),
                         "keterangan": ("butuh minimal 2 pasangan" if len(labels) < 2 else
                                        "kelas konstan; kappa tidak terdefinisi" if degenerate else None)})
    data_latih = [(_skor_selaras(c, leksikon), c.selaras) for c in latih
                  if c.selaras is not None]
    ambang = AMBANG_SELARAS
    metode = "default"
    if sum(score is not None for score, _ in data_latih) >= 2:
        pilihan = []
        for t in (round(.30 + .05 * i, 2) for i in range(14)):
            acc, _ = _akurasi_ambang(data_latih, t)
            pilihan.append((acc, -abs(t - AMBANG_SELARAS), t))
        ambang = max(pilihan)[2]
        metode = "dipilih_hanya_dari_pengembangan"
    evaluasi = []
    kurang = seri = 0
    for c in uji:
        if len(c.anotasi) < 2:
            kurang += 1
            continue
        ya = sum(c.anotasi.values())
        if ya * 2 == len(c.anotasi):
            seri += 1
            continue
        evaluasi.append((c, ya * 2 > len(c.anotasi)))
    # Tanpa provenance yang dinyatakan, jangan menerbitkan angka berlabel
    # akurasi eksternal. Sumber dan identitas tetap belum terverifikasi oleh kode.
    scores = [(_skor_selaras(c, leksikon), label) for c, label in evaluasi] if sumber else []
    acc, dinilai = _akurasi_ambang(scores, ambang)
    status = ("korpus_kosong" if not uji else "provenance_belum_dinyatakan" if not sumber else
              "anotasi_konsensus_tidak_cukup" if not evaluasi else
              "tidak_ada_skor_dapat_dinilai" if not dinilai else "diukur_terhadap_konsensus")
    return {"status": status, "sumber": sumber,
            "provenance": "deklarasi_pemanggil_belum_diverifikasi",
            "jumlah_pengembangan": len(latih), "jumlah_uji": len(uji),
            "pemisahan": "id_dan_teks_normalisasi_disjoint",
            "jumlah_anotator": len(nama), "antar_anotator": pasangan,
            "kurang_dua_anotator": kurang, "konsensus_seri": seri,
            "jumlah_konsensus": len(evaluasi), "dinilai": dinilai,
            "cakupan_konsensus": _bulat(dinilai / len(uji)) if uji else None,
            "ambang": ambang, "metode_ambang": metode,
            "akurasi_terhadap_konsensus": _bulat(acc), "ukuran_kecil": dinilai < 30,
            "peringatan": "Bukan bukti label manusia independen; ukuran kecil dan bias sumber tetap perlu ditinjau."}


def laporan_kalibrasi(korpus: Sequence[ContohLabel],
                      leksikon: Optional["LeksikonCiri"] = None, *,
                      korpus_pihak_ketiga: Optional[Sequence[ContohLabel]] = None,
                      sumber_pihak_ketiga: Optional[str] = None) -> Dict[str, Any]:
    """Laporan lama deskriptif, dengan evaluasi held-out eksternal opt-in.

    Anotasi eksternal bool per identitas pada ContohLabel.anotasi. Akurasi
    memerlukan >=2 anotator per contoh dan konsensus non-seri, serta deklarasi
    sumber; kode tidak memverifikasi apakah identitas benar-benar manusia.
    """
    if korpus_pihak_ketiga is None and sumber_pihak_ketiga is not None:
        raise ValueError("sumber_pihak_ketiga membutuhkan korpus_pihak_ketiga")
    eksternal = ({"status": "belum_tersedia", "akurasi_terhadap_konsensus": None,
                  "antar_anotator": [], "peringatan": "Tidak ada bukti evaluasi pihak ketiga."}
                 if korpus_pihak_ketiga is None else
                 _evaluasi_eksternal(korpus, korpus_pihak_ketiga, leksikon, sumber_pihak_ketiga))
    return {"jumlah_contoh": len(korpus),
            "fitur": ukur_fitur(korpus, leksikon),
            "selaras": ukur_selaras(korpus, leksikon),
            "evaluasi_pihak_ketiga": eksternal,
            "batas_bukti": "Metrik internal adalah kesesuaian terhadap label yang diberikan, bukan validasi ilmiah."}


if __name__ == "__main__":
    Nurani.demo()
