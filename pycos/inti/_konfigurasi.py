"""Konfigurasi dan utilitas inti bersama, tanpa impor mesin atau patch.

Objek mutable diekspor ulang oleh naluri, bukan disalin. Parameter lapisan
opsional tetap digabung oleh facade setelah konfigurasi dasar dimuat.
"""
from __future__ import annotations
from typing import Any, Dict, List, Mapping, Tuple
from pycos.dukungan.numerik import jepit

_MAKS_LOSSES = 256

from pycos.dukungan import konstanta as _konstanta_drive
DRIVES = _konstanta_drive.DRIVES

# Bobot drive per tahap maturasi (kurikulum perkembangan).
STAGE_WEIGHTS: Dict[str, Dict[str, float]] = {
    "anak":    {"energi": 1.0, "keamanan": 1.0, "keingintahuan": 1.6,
                "penguasaan": 0.6, "afiliasi": 1.0, "koherensi": 0.9},
    "remaja":  {"energi": 1.0, "keamanan": 1.0, "keingintahuan": 1.2,
                "penguasaan": 1.0, "afiliasi": 1.1, "koherensi": 1.1},
    "dewasa":  {"energi": 1.1, "keamanan": 1.2, "keingintahuan": 0.8,
                "penguasaan": 1.3, "afiliasi": 1.0, "koherensi": 1.4},
}

# Preset kepribadian bernama (fix #3): konstanta siap-tempel untuk desainer.
# Setiap preset: {"label", "desc", "weights" (bobot drive absolut), "params"?}.
# Dipakai lewat `Naluri(personality="penjaga")` atau
# `naluri.set_personality_preset("penjaga", blend=0.5)` (blend 0..1 =
# pencampuran dengan bobot dasar tahap, untuk penyetelan yang lebih dinamis).
#
# ---------------------------------------------------------------------------
# WATAK — tiga lapis kepribadian (setiap preset memuat ketiganya):
#
#   1. "weights" = KEPRIBADIAN (arah): drive mana yang paling dikejar.
#   2. "watak"   = VISKOSITAS (filter plastisitas): parameter `params` yang
#      di-inject preset — seberapa CEPAT pengalaman boleh mengoreksi arah
#      itu. Boleh per-drive: {"keamanan": 1e-5, "*": 8e-4} berarti hampir
#      beku untuk keamanan, normal untuk drive lain. "Paranoid" yang sejati
#      BUKAN keamanan berbobot 2.0, melainkan ketidakmampuan belajar bahwa
#      dunia ternyata aman.
#   3. "lahir"   = BACKSTORY (kondisi awal): level, setpoint, memori afektif,
#      relasi, dan emosi awal. Filter hanya MEMPERTAHANKAN sifat — ia tidak
#      menciptakannya di tick 0; kondisi awal yang menciptakannya.
#
# Preset lama yang hanya memuat "weights" tetap sah; kunci "params" lama
# diterima sebagai alias "watak".
# ---------------------------------------------------------------------------
PERSONALITIES: Dict[str, Dict[str, Any]] = {
    "seimbang": {
        "label": "Seimbang", "desc": "Semua drive berbobot sama; netral.",
        "weights": {d: 1.0 for d in DRIVES},
        # Tanpa watak & backstory: kanvas kosong.
    },
    "penjaga": {
        "label": "Penjaga", "desc": "Waspada dan teratur; keamanan & koherensi tinggi.",
        "weights": {"keamanan": 1.6, "koherensi": 1.2, "energi": 1.1,
                    "keingintahuan": 0.8},
        "watak": {
            "enable_plastic_setpoints": True,
            "enable_social_memory": True,
            # Urgensi keamanan bereaksi cepat (alpha besar), keyakinan aman
            # direvisi lambat (lr kecil): waspada yang terbentuk, bukan panik.
            "urgency_alpha": {"keamanan": 0.45, "*": 0.25},
            "setpoint_lr": {"keamanan": 0.0002, "*": 0.0008},
            "social_trust_lr": 0.15,
            "social_consolidation": 0.05,
        },
        "lahir": {
            "setpoints": {"keamanan": 0.1},  # sedikit di atas netral: siaga
        },
    },
    "penjelajah": {
        "label": "Penjelajah", "desc": "Berani dan penasaran; keamanan rendah.",
        "weights": {"keingintahuan": 1.6, "energi": 1.1, "penguasaan": 1.1,
                    "keamanan": 0.8},
        "watak": {
            "enable_affective_memory": True,
            "enable_plastic_setpoints": True,  # tanpa ini setpoint_lr mati
            "affective_min_samples": 1,      # satu pengalaman cukup jadi intuisi
            "affective_trust_cap": {"keingintahuan": 0.9, "*": 0.7},
            "setpoint_lr": 0.002,            # cepat beradaptasi pada dunia baru
            "urgency_alpha": {"keingintahuan": 0.4, "*": 0.25},
            "social_valensi_lr": 0.6,        # kesan sosial terbentuk cepat
            # PERSEPSI: peka hal baru (d' keingintahuan tinggi), lambat bosan
            # (habituasi rendah), atensi lebar — dunia penuh yang terlihat.
            "enable_perception": True,
            "persepsi_sensitivitas": {"keingintahuan": 1.3, "*": 1.0},
            "persepsi_habit_lr": 0.1,
            "persepsi_atensi": 4,
        },
        "lahir": {
            "levels": {"keingintahuan": 0.25},
        },
    },
    "cendekia": {
        "label": "Cendekia", "desc": "Sistematis; koherensi & keingintahuan tinggi.",
        "weights": {"keingintahuan": 1.3, "koherensi": 1.6, "penguasaan": 1.2,
                    "energi": 0.9},
        "watak": {
            "enable_affective_memory": True,
            "enable_layered_calibration": True,
            "enable_plastic_setpoints": True,
            "affective_min_samples": 4,      # bukti dulu, baru intuisi
            "affective_trust_cap": 0.85,
            "calibration_report_alpha": 0.4, # rapor diri cepat direvisi data
            "scale_alpha": 0.2,
            "setpoint_lr": {"koherensi": 0.0015, "*": 0.0008},
        },
        "lahir": {
            "setpoints": {"koherensi": 0.15},  # terbiasa dunia yang tertata
        },
    },
    "pengrajin": {
        "label": "Pengrajin", "desc": "Tekun; penguasaan tinggi.",
        "weights": {"penguasaan": 1.6, "koherensi": 1.1, "keingintahuan": 0.8},
        "watak": {
            "enable_plastic_setpoints": True,
            "setpoint_lr": {"penguasaan": 0.0001, "*": 0.0008},
            "setpoint_clamp": {"penguasaan": 0.6, "*": 0.4},
            "urgency_alpha": {"penguasaan": 0.15, "*": 0.25},  # tekun, tak lekas goyah
        },
        "lahir": {
            "setpoints": {"penguasaan": 0.35},  # standar keahlian diri tinggi
            "levels": {"penguasaan": 0.2},      # bertahun-tahun latihan
        },
    },
    "sosiawan": {
        "label": "Sosiawan", "desc": "Ramah; afiliasi tinggi.",
        "weights": {"afiliasi": 1.6, "keingintahuan": 1.0, "keamanan": 0.9},
        "watak": {
            "enable_social_memory": True,
            "enable_affective_memory": True,
            "social_valensi_lr": 0.8,        # cepat menyukai/menilai orang
            "social_trust_lr": 0.5,
            "social_familiarity_lr": 0.35,
            "social_consolidation": 0.0,     # setiap orang dianggap baru
            "affective_min_samples": 1,
        },
        "lahir": {
            "levels": {"afiliasi": 0.3},     # tumbuh di tengah keramaian
        },
    },
    "paranoid": {
        "label": "Paranoid", "desc": "Serba curiga; TIDAK BISA belajar bahwa dunia aman.",
        "weights": {"keamanan": 2.0, "koherensi": 1.0, "afiliasi": 0.7,
                    "keingintahuan": 0.9},
        "watak": {
            "enable_plastic_setpoints": True,
            "enable_affective_memory": True,
            "enable_social_memory": True,
            "enable_emosi": True,
            # Inti watak paranoid: setpoint keamanan nyaris beku (lr 1e-5) —
            # bukti keamanan sebanyak apa pun tidak menggeser ekspektasinya —
            # dengan clamp LEBAR sehingga keyakinannya boleh ekstrem.
            "setpoint_lr": {"keamanan": 0.00001, "*": 0.0005},
            "setpoint_clamp": {"keamanan": 0.6, "*": 0.4},
            # Masa lalu mendominasi persepsi ancaman (cap 0.95 vs default 0.7).
            "affective_trust_cap": {"keamanan": 0.95, "*": 0.7},
            "affective_min_samples": 1,
            # Kepercayaan pada orang lambat naik, kesan buruk cepat menempel,
            # dan relasi lama makin sukar digoyang (konsolidasi tinggi).
            "social_trust_lr": 0.1,
            "social_valensi_lr": 0.6,
            "social_consolidation": 0.12,
            "urgency_alpha": {"keamanan": 0.5, "*": 0.25},
            "interoception_echo": {"keamanan": 0.3, "*": 0.15},
            # PERSEPSI: hipervigilansi (SDT) — criterion ancaman negatif
            # sehingga derau endogen pun bisa lolos sebagai "bayangan"
            # (alarm palsu), saluran lebih berderau, dan persepsi didominasi
            # ekspektasi: ia MELIHAT apa yang ditakutinya.
            "enable_perception": True,
            "persepsi_kriterion": {"keamanan": -0.35, "*": 0.0},
            "persepsi_noise": 0.05,
            "persepsi_topdown": 0.6,
            "persepsi_emosi_gain": 0.9,
        },
        "lahir": {
            "setpoints": {"keamanan": 0.55},  # yakin dunia berbahaya
            "memori": [{  # luka lama: aktif sebagai prior sejak tick 0
                "teks": "dikhianati teman dipercaya ancaman bahaya",
                "deltas": {"keamanan": -0.6, "afiliasi": -0.3}, "n": 6}],
            "emosi": {"takut": 0.25},
        },
    },
    "dingin": {
        "label": "Dingin", "desc": "Afeksi nyaris nol (setara set_personality(afiliasi=0.1)).",
        "weights": {"afiliasi": 0.1, "penguasaan": 1.3, "keamanan": 1.2},
        "watak": {
            "enable_social_memory": True,
            "enable_plastic_setpoints": True,
            "setpoint_lr": {"afiliasi": 0.00002, "*": 0.0008},
            "affective_trust_cap": {"afiliasi": 0.1, "*": 0.7},
            # Orang lain nyaris tak bisa menggeser perasaannya; yang tersisa
            # hanya kalkulasi aman/tidak-aman (prior keamanan tetap jalan).
            "social_valensi_lr": 0.1,
            "social_familiarity_lr": 0.05,
            "social_trust_lr": 0.4,
            "social_prior_weight": {"keamanan": 0.25, "afiliasi": 0.05, "*": 0.25},
            # PERSEPSI: afek tumpul (blunting) — saluran sosial kurang peka
            # dan emosi hampir tak mewarnai apa yang dilihat.
            "enable_perception": True,
            "persepsi_sensitivitas": {"afiliasi": 0.5, "*": 1.0},
            "persepsi_emosi_gain": 0.1,
        },
        "lahir": {
            "setpoints": {"afiliasi": -0.3},  # tidak pernah butuh orang lain
        },
    },
    "pemimpi": {
        "label": "Pemimpi", "desc": "Melamun; keingintahuan & afiliasi tinggi, energi rendah.",
        "weights": {"keingintahuan": 1.4, "afiliasi": 1.2, "energi": 0.9,
                    "koherensi": 0.8},
        "watak": {
            "enable_affective_memory": True,
            "enable_plastic_setpoints": True,
            "enable_emosi": True,
            "affective_trust_cap": 0.9,      # hidup dari perasaan & ingatan
            "affective_min_samples": 1,
            "urgency_alpha": 0.12,           # semua urgensi melambat: melamun
            "setpoint_lr": 0.0015,
            "emosi_gain_valence": 1.6,       # hatinya mudah tersentuh
            # PERSEPSI: hidup di dalam kepala — ekspektasi mendominasi sensasi
            # (top-down 0.8), dunia luar mudah memudar (ambang tinggi) dan
            # yang tak terfokus nyaris hilang (atenuasi 0.2): melamun.
            "enable_perception": True,
            "persepsi_topdown": 0.8,
            "persepsi_ambang": 0.06,
            "persepsi_atenuasi": 0.2,
        },
        "lahir": {
            "levels": {"keingintahuan": 0.15},
            "emosi": {"penasaran": 0.2},
        },
    },
}

# Alias agar preset bisa dirujuk dengan nama bebas-form yang sudah dikenal
# (mis. dari data desainer lama): kunci alias -> nama preset kanonik.
PERSONALITY_ALIASES: Dict[str, str] = {
    "netral": "seimbang", "default": "seimbang", "balanced": "seimbang",
    "guard": "penjaga", "penjaga_keamanan": "penjaga",
    "explorer": "penjelajah", "petualang": "penjelajah", "adventurer": "penjelajah",
    "scholar": "cendekia", "ilmuwan": "cendekia",
    "artisan": "pengrajin", "pekerja": "pengrajin", "craftsman": "pengrajin",
    "social": "sosiawan", "socialite": "sosiawan", "ramah": "sosiawan",
    "psychopath": "dingin", "psikopat": "dingin",
    "dreamer": "pemimpi",
}

# Ambang dan parameter fisiologis (defaults yang terdokumen).
DEFAULTS: Dict[str, Any] = {
    "strict_events": False,         # kunci/drive asing dicatat; True juga menolak
    "decay_per_tick": 0.005,        # peluruhan drive baseline menuju 0
    "energi_cost_tick": 0.006,      # biaya komputasi per tick (energi turun)
    "energi_cost_action": 0.03,     # biaya tambahan saat aksi diambil
    "energi_recover_rest": 0.015,   # pemulihan energi saat tidak beraksi
    "urgency_alpha": 0.25,          # smoothing urgensi
    "deadline_pressure": 0.005,     # koefisien akumulasi "bunga" defisit
    "calibration_alpha": 0.25,      # EMA kesalahan prediksi
    "calibration_tolerance": 0.20,  # lantai derau (dunia berderau; kesalahan kecil tidak dihukum)
    "calibration_penalty": 0.55,    # penurunan koherensi per satuan error DI ATAS tolerance
    "calibration_reward": 0.03,     # kenaikan koherensi saat prediksi akurat
    "scale_alpha": 0.10,            # laju pembelajaran skala adaptif
    "scale_initial": 1.0,           # tebakan awal skala utilitas vs reward dunia
    "scale_floor": 0.1,             # lantai skala
    "scale_ceiling": 20.0,          # plafon skala (skor utilitas berada di [-1,1]
                                    #   setelah tanh; plafon dijaga rendah agar
                                    #   pruning/RiskAssessment tak meledak)
    "sleep_energy_threshold": -0.20,
    "sleep_coherence_threshold": -0.20,
    "sleep_backlog_threshold": 6,   # jumlah prediksi-tak-terverifikasi yang memicu tidur
    "sleep_refractory_ticks": 25,   # tak tidur lagi secepat ini sesudah bangun
    "sleep_energy_gain": 0.45,
    "sleep_coherence_gain": 0.30,
    "goal_urgency_threshold": 0.12,
    "max_goals": 4,
    # --- memori kerja: konteks yang masih aktif sesudah persepsi ---
    "context_capacity": 5,
    "context_decay_ticks": 8,
    "context_min_salience": 0.025,
    "context_bind_impact": True,
    "context_impact_gain": 0.18,
    "context_action_bias": 0.24,
    "context_repeat_threshold": 2,
    "context_auto_experience": True,
    # --- tujuan hierarkis (opsional satu tingkat subgoal) ---
    "subgoal_bias": 0.18,
    "subgoal_completion_decay": 0.75,
    # --- temporal credit / eligibility trace ---
    "eligibility_lambda": 0.88,
    "eligibility_min": 0.015,
    "eligibility_max_traces": 64,
    "eligibility_learning_alpha": 0.20,
    "eligibility_value_weight": 0.45,
    "eligibility_horizon": 160,
    # --- mode tidur NPC (fix #4): "kognitif" = perilaku lama (endogen, untuk
    # konsolidasi model); "terjadwal" = sirkadian murni (NPC tidur hanya pada
    # fase malam, sekali per siklus, refraktori tidak berlaku); "gabung" =
    # terjadwal ATAU kognitif. Default lama dipertahankan agar kompatibel.
    "sleep_mode": "kognitif",
    "sleep_scheduled_phase": "malam",  # fase sirkadian untuk tidur terjadwal
    "circadian_period": 24,            # fallback lokal bila NURANI tak terpasang
    # --- LOD (fix #2): pada mode "latar", fisika tick dijalankan sekali per
    # `lod_divisor` panggilan dengan kompensasi langkah (10x lebih hemat).
    "lod_divisor": 10,
    # --- EMPATI: mesin emosi diskret (mati bawaan = kompatibel mundur) ---
    "enable_emosi": False,
    "enable_coping": False,         # reappraisal/suppression/distraction gated
    "coping_reappraise_gain": 0.35,
    "coping_suppression_cost": 0.08,
    "coping_distraction_decay": 2.5,
    "coping_focus_gain": 0.15,
    "coping_gate_min": 0.14,
    "emosi_decay": 0.03,            # proporsi peluruhan emosi per tick
    "emosi_gain_valence": 1.2,      # apresiasi: Δvalensi mentah -> senang/sedih
    "emosi_gain_keamanan": 1.0,     # apresiasi: Δdefisit keamanan -> takut
    "emosi_gain_keingintahuan": 0.8,  # apresiasi: Δkeingintahuan -> penasaran
    "emosi_gain_event": 0.6,        # skala suntikan feel()/event "emosi"
    "emosi_reaksi_kejutan": 0.5,    # observe_outcome: surprise -> takut/penasaran
    "emosi_reaksi_reward": 0.4,     # observe_outcome: reward -> senang/sedih
    "emosi_ambang": 0.02,           # di bawah ini dibulatkan ke 0 (lantai derau)
    "social_interaction_gain": 0.15,  # besar efek drive per interaksi sosial
    # --- PERSEPSI: mesin sisi Naluri (psikofisika saluran hidup di NURANI) ---
    # Semua hanya berlaku saat enable_perception nyala; mati = jalur lama utuh.
    "persepsi_atensi": 3,           # kapasitas atensi (Broadbent): stimulus/tick
    "persepsi_atenuasi": 0.35,      # atenuasi tak-terfokus (Treisman; bukan nol)
    "persepsi_arousal_fokus": 2.0,  # Easterbrook: arousal tinggi mempersempit
                                    #   atensi (kapasitas −= fokus·arousal;
                                    #   panik penuh → fokus satu saluran)
    "persepsi_topdown": 0.35,       # bobot ekspektasi (prior afektif) vs sensasi
                                    #   (pemrosesan prediktif: persepsi =
                                    #   kombinasi bukti + prior per reliabilitas)
    "persepsi_emosi_gain": 0.6,     # gain congruence EMOSI_PERSEPSI
    "persepsi_alarm_rate": 0.06,    # laju alarm palsu/tick (criterion negatif)
    "persepsi_alarm_maks": 0.15,    # plafon besaran delta hantu
    "persepsi_afordansi": 0.0,      # bonus salience Gibson di choose_action
                                    #   (0 = mati meski pilar nyala)
    # --- INTROSPEKSI DIRI (fisiologi nyata, duplikat untuk mode standalone) ---
    # Jika NURANI terpasang, nilai dari NURANI_DEFAULTS yang dipakai; ini fallback
    # agar demo mandiri punya default yang sama.
    "enable_introspection": False,
    "introspeksi_noise": 0.08,
    "introspeksi_bias": 0.0,
    "introspeksi_lr": 0.06,
    "introspeksi_meta_lr": 0.04,
    "introspeksi_window": 64,
    "introspeksi_ambang_sadar": 0.18,
    "introspeksi_refleksi_period": 24,
    "introspeksi_max_memori": 256,
    "introspeksi_kepercayaan_awal": 0.5,
    "introspeksi_meta_d_floor": 0.0,
    "introspeksi_meta_d_ceiling": 2.5,
}

# NURANI (konsep 17): parameter lapisan meta-plastisitas -- sakelar enam pilar
# (semua False = kompatibel mundur) plus laju/jepit setpoint, periode sirkadian,
# dan kapasitas memori afektif. Satu sumber kebenaran: kamarnya sendiri di
# pycos.refleksi.nurani, di-unpack ke sini agar `params` Naluri satu dict.



def _nilai_per_drive(params: Dict[str, Any], key: str, drive: str,
                     fallback: float) -> float:
    """Baca parameter WATAK: skalar global ATAU dict per-drive.

    Format dict: {"keamanan": 0.5, "*": 0.25} — "*" adalah fallback untuk
    drive yang tidak disebut; tanpa "*", fallback ke `fallback`. Dipakai
    untuk parameter yang dikonsumsi langsung Naluri (mis. urgency_alpha);
    parameter NURANI punya resolver sendiri (Nurani._p_drive) dengan semantik
    identik.
    """
    v = params.get(key, fallback)
    if isinstance(v, dict):
        if drive in v:
            return float(v[drive])
        if "*" in v:
            return float(v["*"])
        return float(fallback)
    return float(v)

# Lexicon Indonesia (campur dengan bahasa Inggris) untuk menilai dampak deskripsi
# terhadap enam drive. Bentuk: kata -> {drive: delta}
# Kosakata diambil dari frasa yang biasa muncul di deskripsi Imagination
# (lihat samre/imagination/engine.py: _generate_description / _expand_parent)
# agar scoring tidak butuh model bahasa.
LEXICON: Dict[str, Dict[str, float]] = {
    # --- Energi ---
    "hemat":          {"energi": +0.3, "keamanan": +0.05},
    "efisien":        {"energi": +0.3},
    "lelah":          {"energi": -0.4},
    "hemat energi":   {"energi": +0.5},
    "istirahat":      {"energi": +0.4, "keamanan": +0.1},
    "tidur":          {"energi": +0.4},
    # --- Keamanan ---
    "aman":           {"keamanan": +0.5},
    "risiko":         {"keamanan": -0.4},
    "bahaya":         {"keamanan": -0.6, "keingintahuan": +0.1},
    "ancaman":        {"keamanan": -0.6},
    "buruk":          {"keamanan": -0.3, "penguasaan": -0.2},
    "gagal":          {"keamanan": -0.2, "penguasaan": -0.5},
    "celaka":         {"keamanan": -0.7},
    "bom waktu":      {"keamanan": -0.6, "koherensi": -0.1},
    "terlambat":      {"keamanan": -0.25},
    "stabil":         {"keamanan": +0.4, "koherensi": +0.2},
    "mitigasi":       {"keamanan": +0.4},
    "waspada":        {"keamanan": +0.3},
    "hati-hati":      {"keamanan": +0.4},
    # --- Keingintahuan ---
    "baru":           {"keingintahuan": +0.3, "energi": -0.05},
    "mengejutkan":    {"keingintahuan": +0.5, "koherensi": -0.15},
    "paradoks":       {"keingintahuan": +0.6, "koherensi": -0.2},
    "wawasan":        {"keingintahuan": +0.4, "koherensi": +0.2},
    "aneh":           {"keingintahuan": +0.3},
    "misteri":        {"keingintahuan": +0.4},
    "belajar":        {"keingintahuan": +0.3, "penguasaan": +0.2},
    "mengeksplorasi": {"keingintahuan": +0.4},
    "ditemukan":      {"keingintahuan": +0.2, "penguasaan": +0.2},
    "familiar":       {"keingintahuan": -0.3},
    "bosan":          {"keingintahuan": -0.4},
    # --- Penguasaan ---
    "berhasil":       {"penguasaan": +0.5, "keamanan": +0.1},
    "sukses":         {"penguasaan": +0.6, "afiliasi": +0.05},
    "kuasai":         {"penguasaan": +0.5},
    "mahir":          {"penguasaan": +0.4},
    "menang":         {"penguasaan": +0.5, "afiliasi": -0.1},
    "kalah":          {"penguasaan": -0.5, "keamanan": -0.2},
    "sulit":          {"penguasaan": -0.1, "keingintahuan": +0.1},
    "membiasakan":    {"penguasaan": +0.2},
    "kompeten":       {"penguasaan": +0.5},
    # --- Afiliasi ---
    "kerja sama":     {"afiliasi": +0.6, "penguasaan": +0.1},
    "bersama":        {"afiliasi": +0.4},
    "win-win":        {"afiliasi": +0.7, "penguasaan": +0.2},
    "dipercaya":      {"afiliasi": +0.5, "keamanan": +0.2},
    "ditolak":        {"afiliasi": -0.5, "keamanan": -0.2},
    "sendirian":      {"afiliasi": -0.4},
    "musuh":          {"afiliasi": -0.5, "keamanan": -0.3},
    "teman":          {"afiliasi": +0.4},
    "perspektif":     {"afiliasi": +0.2, "keingintahuan": +0.1},
    "pihak lain":     {"afiliasi": +0.25},
    # --- Koherensi ---
    "terduga":        {"koherensi": +0.3, "keingintahuan": -0.1},
    "terbukti":       {"koherensi": +0.4, "penguasaan": +0.2},
    "terprediksi":    {"koherensi": +0.3},
    "terjawab":       {"koherensi": +0.3, "keingintahuan": -0.1},
    "meleset":        {"koherensi": -0.5, "keingintahuan": +0.2},
    "kacau":          {"koherensi": -0.4, "keamanan": -0.2},
    "acak":           {"koherensi": -0.3},
    "konsisten":      {"koherensi": +0.4},
    "counterfactual": {"koherensi": -0.1, "keingintahuan": +0.2},
    "terkalibrasi":   {"koherensi": +0.5},
}

# Pola tambahan untuk tag khusus Imagination yang tidak memakai kata umum.
TAG_LEXICON: Dict[str, Dict[str, float]] = {
    "PERSPEKTIF PIHAK LAIN": {"afiliasi": +0.20, "keingintahuan": +0.10},
    "COUNTERFACTUAL":        {"koherensi": -0.10, "keingintahuan": +0.25},
    "BOM WAKTU":             {"keamanan": -0.45, "koherensi": -0.10},
}

# Fix #5: contoh paket lexicon Inggris (bukti bahwa lexicon dapat di-inject,
# bukan konstanta Indonesia-only). Terjemahan 1:1 dari LEXICON di atas dengan
# bobot yang sama, sehingga perilaku scoring identik lintas bahasa.
LEXICON_EN: Dict[str, Dict[str, float]] = {
    # --- energi ---
    "frugal":         {"energi": +0.3, "keamanan": +0.05},
    "efficient":      {"energi": +0.3},
    "tired":          {"energi": -0.4},
    "energy saving":  {"energi": +0.5},
    "rest":           {"energi": +0.4, "keamanan": +0.1},
    "sleep":          {"energi": +0.4},
    # --- keamanan ---
    "safe":           {"keamanan": +0.5},
    "risk":           {"keamanan": -0.4},
    "danger":         {"keamanan": -0.6, "keingintahuan": +0.1},
    "threat":         {"keamanan": -0.6},
    "bad":            {"keamanan": -0.3, "penguasaan": -0.2},
    "fail":           {"keamanan": -0.2, "penguasaan": -0.5},
    "accident":       {"keamanan": -0.7},
    "time bomb":      {"keamanan": -0.6, "koherensi": -0.1},
    "late":           {"keamanan": -0.25},
    "stable":         {"keamanan": +0.4, "koherensi": +0.2},
    "mitigation":     {"keamanan": +0.4},
    "vigilant":       {"keamanan": +0.3},
    "careful":        {"keamanan": +0.4},
    # --- keingintahuan ---
    "new":            {"keingintahuan": +0.3, "energi": -0.05},
    "surprising":     {"keingintahuan": +0.5, "koherensi": -0.15},
    "paradox":        {"keingintahuan": +0.6, "koherensi": -0.2},
    "insight":        {"keingintahuan": +0.4, "koherensi": +0.2},
    "strange":        {"keingintahuan": +0.3},
    "mystery":        {"keingintahuan": +0.4},
    "learn":          {"keingintahuan": +0.3, "penguasaan": +0.2},
    "explore":        {"keingintahuan": +0.4},
    "discovered":     {"keingintahuan": +0.2, "penguasaan": +0.2},
    "familiar":       {"keingintahuan": -0.3},
    "bored":          {"keingintahuan": -0.4},
    # --- penguasaan ---
    "succeeded":      {"penguasaan": +0.5, "keamanan": +0.1},
    "success":        {"penguasaan": +0.6, "afiliasi": +0.05},
    "master":         {"penguasaan": +0.5},
    "skilled":        {"penguasaan": +0.4},
    "win":            {"penguasaan": +0.5, "afiliasi": -0.1},
    "lose":           {"penguasaan": -0.5, "keamanan": -0.2},
    "difficult":      {"penguasaan": -0.1, "keingintahuan": +0.1},
    "habituate":      {"penguasaan": +0.2},
    "competent":      {"penguasaan": +0.5},
    # --- afiliasi ---
    "cooperation":    {"afiliasi": +0.6, "penguasaan": +0.1},
    "together":       {"afiliasi": +0.4},
    "win-win":        {"afiliasi": +0.7, "penguasaan": +0.2},
    "trusted":        {"afiliasi": +0.5, "keamanan": +0.2},
    "rejected":       {"afiliasi": -0.5, "keamanan": -0.2},
    "alone":          {"afiliasi": -0.4},
    "enemy":          {"afiliasi": -0.5, "keamanan": -0.3},
    "friend":         {"afiliasi": +0.4},
    "perspective":    {"afiliasi": +0.2, "keingintahuan": +0.1},
    "other party":    {"afiliasi": +0.25},
    # --- koherensi ---
    "expected":       {"koherensi": +0.3, "keingintahuan": -0.1},
    "proven":         {"koherensi": +0.4, "penguasaan": +0.2},
    "predicted":      {"koherensi": +0.3},
    "answered":       {"koherensi": +0.3, "keingintahuan": -0.1},
    "missed":         {"koherensi": -0.5, "keingintahuan": +0.2},
    "chaotic":        {"koherensi": -0.4, "keamanan": -0.2},
    "random":         {"koherensi": -0.3},
    "consistent":     {"koherensi": +0.4},
    "counterfactual": {"koherensi": -0.1, "keingintahuan": +0.2},
    "calibrated":     {"koherensi": +0.5},
}

TAG_LEXICON_EN: Dict[str, Dict[str, float]] = {
    "OTHER PARTY PERSPECTIVE": {"afiliasi": +0.20, "keingintahuan": +0.10},
    "COUNTERFACTUAL":          {"koherensi": -0.10, "keingintahuan": +0.25},
    "TIME BOMB":               {"keamanan": -0.45, "koherensi": -0.10},
}

# Suplemen terkompilasi: bobot lama selalu menang atas aturan tambahan.
from pycos.dukungan.leksikon import perluas as _perluas_leksikon_impak
_perluas_leksikon_impak(LEXICON, LEXICON_EN)
TAG_LEXICON.update({"BUTUH ISTIRAHAT": {"energi": -0.25},
                    "ANCAMAN LANGSUNG": {"keamanan": -0.4},
                    "DUKUNGAN SOSIAL": {"afiliasi": 0.3}})
TAG_LEXICON_EN.update({"NEEDS REST": {"energi": -0.25},
                       "DIRECT THREAT": {"keamanan": -0.4},
                       "SOCIAL SUPPORT": {"afiliasi": 0.3}})

# Registri paket bahasa: nama -> (lexicon kata, lexicon tag).
# Pakai `naluri.use_lexicon_pack("en")` atau inject mapping sendiri via
# konstruktor / `set_lexicon()`.
LEXICON_PACKS: Dict[str, Tuple[Dict[str, Dict[str, float]],
                               Dict[str, Dict[str, float]]]] = {
    "id": (LEXICON, TAG_LEXICON),
    "en": (LEXICON_EN, TAG_LEXICON_EN),
}

# Pemetaan drive dominan → (neuromodulator yang dinaikkan, region atensi).
# Dipakai apply_to_brain() bila brain memiliki API set_neuromodulator / set_attentional_bias.
DRIVE_NEUROMOD: Dict[str, str] = {
    "energi":         "noradrenaline",
    "keamanan":       "noradrenaline",
    "keingintahuan":  "acetylcholine",
    "penguasaan":     "dopamine",
    "afiliasi":       "serotonin",
    "koherensi":      "acetylcholine",
}

DRIVE_ATTENTION: Dict[str, List[str]] = {
    "energi":         [],
    "keamanan":       ["InferiorColliculus", "Amygdala"],
    "keingintahuan":  ["VisualAssociationCortex", "Hippocampus"],
    "penguasaan":     ["PremotorCortex", "CaudateNucleus"],
    "afiliasi":       ["Insula", "CingulateGyrus"],
    "koherensi":      ["Hippocampus", "ParietalAssociationCortex"],
}

# Goal templates per drive (dipakai goal_to_scenario()).
GOAL_TEMPLATES: Dict[str, List[str]] = {
    "energi": [
        "Cari jalan efisien: kurangi biaya komputasi dan hemat energi",
        "Prioritaskan aksi rendah biaya untuk memulihkan energi",
    ],
    "keamanan": [
        "Kurangi risiko: identifikasi ancaman laten dan skenario terburuk",
        "Mitigasi bahaya yang terdeteksi, siapkan rute cadangan",
    ],
    "keingintahuan": [
        "Jelajahi jalur aneh dan paradoks: cari wawasan baru",
        "Eksploitasi sudut pandang yang belum dicoba untuk memahami situasi",
    ],
    "penguasaan": [
        "Raih kompetensi: ulangi aksi yang pernah berhasil dan kuasai domain",
        "Wujudkan kemenangan kecil untuk membangun kepercayaan diri",
    ],
    "afiliasi": [
        "Cari outcome win-win: dampak positif pada pihak lain dan sistem sendiri",
        "Bangun kepercayaan dengan memperhatikan perspektif pihak lain",
    ],
    "koherensi": [
        "Kalibrasi model: uji prediksi dan konsolidasikan yang terbukti benar",
        "Bersihkan kacau dan konsistensi dalam representasi memori",
    ],
}

# Label niat per drive untuk HUD (fix #7): kalimat pendek yang terbaca pemain,
# bukan format debug. `intent()`/`hud_state()` memakainya.
HUD_DRIVE_INTENT: Dict[str, str] = {
    "energi":         "ingin beristirahat / menghemat tenaga",
    "keamanan":       "sedang waspada / mencari tempat aman",
    "keingintahuan":  "ingin menjelajah / mencari hal baru",
    "penguasaan":     "ingin berlatih / menuntaskan pekerjaan",
    "afiliasi":       "ingin mengobrol / mencari teman",
    "koherensi":      "sedang merenung / menata pikiran",
    "tidur":          "sedang mencari tempat untuk tidur",
    "santai":         "santai — tidak ada desakan",
}

# Label mood kuadran valensi x arousal untuk HUD.
HUD_MOOD_LABELS: Dict[str, str] = {
    "tenang":      "tenang",
    "bersemangat": "bersemangat",
    "murung":      "murung",
    "gelisah":     "gelisah",
}

# Nama mode LOD yang sah + alias (fix #2).
# Nama mode LOD hierarkis (5 tingkat, dari paling kaya ke paling hemat).
LOD_MODES: Tuple[str, ...] = ("penuh", "ringan", "latar", "abstrak", "beku")
LOD_ALIASES: Dict[str, str] = {
    "penuh": "penuh", "full": "penuh", "high": "penuh",
    "ringan": "ringan", "light": "ringan", "medium": "ringan",
    "latar": "latar", "background": "latar", "low": "latar",
    "abstrak": "abstrak", "abstract": "abstrak", "coarse": "abstrak",
    "beku": "beku", "frozen": "beku", "off": "beku",
}
# Bobot kelipatan divisor per mode (makin jauh makin hemat).
LOD_DIVISOR_FACTOR: Dict[str, int] = {
    "penuh": 1, "ringan": 1, "latar": 1, "abstrak": 4, "beku": 1,
}

# Mode tidur yang sah + alias (fix #4).
SLEEP_MODES: Tuple[str, ...] = ("kognitif", "terjadwal", "gabung")
SLEEP_MODE_ALIASES: Dict[str, str] = {
    "kognitif": "kognitif", "cognitive": "kognitif", "endogen": "kognitif",
    "terjadwal": "terjadwal", "scheduled": "terjadwal", "sirkadian": "terjadwal",
    "gabung": "gabung", "both": "gabung", "hybrid": "gabung",
}

# Preset parameter siap-tempel untuk NPC (fix #4): tidur mengikuti jadwal
# sirkadian sehingga NPC tidak "menghilang" dari scene tanpa alasan terbaca.
# Pakai: Naluri(params=dict(NPC_PARAMS)) atau KawananNPC.tambah(..., npc=True).
NPC_PARAMS: Dict[str, Any] = {
    "sleep_mode": "terjadwal",
}

# ---------------------------------------------------------------------------
# EMPATI — emosi diskret & relasi sosial
# ---------------------------------------------------------------------------
# Lima emosi diskret. Masing-masing: intensitas [0..1] dengan peluruhan sendiri,
# lahir dari APREKASI (perubahan keadaan drive) dan peristiwa eksplisit, lalu
# membalik memodulasi kognisi (mood, bobot keputusan, mimpi) — loop yang sama
# seperti drive, tapi pada lapisan afektif.
EMOSI: Tuple[str, ...] = ("takut", "marah", "senang", "sedih", "penasaran")

# Alias internasional agar desainer bisa menyuntik emosi dengan nama Inggris.
EMOSI_ALIASES: Dict[str, str] = {
    "takut": "takut", "fear": "takut", "afraid": "takut", "scared": "takut",
    "marah": "marah", "anger": "marah", "angry": "marah", "mad": "marah",
    "senang": "senang", "joy": "senang", "happy": "senang", "gembira": "senang",
    "sedih": "sedih", "sad": "sedih", "sadness": "sedih", "duka": "sedih",
    "penasaran": "penasaran", "curious": "penasaran", "curiosity": "penasaran",
    "interest": "penasaran", "tertarik": "penasaran",
}

# Label emosi untuk HUD per bahasa (inject via set_hud_labels(emosi=...)).
EMOSI_LABELS: Dict[str, Dict[str, str]] = {
    "id": {"takut": "takut", "marah": "marah", "senang": "senang",
           "sedih": "sedih", "penasaran": "penasaran", "netral": "netral"},
    "en": {"takut": "afraid", "marah": "angry", "senang": "happy",
           "sedih": "sad", "penasaran": "curious", "netral": "neutral"},
}

# Ambang intensitas agar emosi ditampilkan di HUD/brief (di bawah = netral).
EMOSI_HUD_THRESHOLD: float = 0.15

# ---------------------------------------------------------------------------
# PERSEPSI — congruence mood/emosi (Bower; "affective realism"): emosi yang
# aktif menaikkan gain saluran drive yang SELARAS sehingga stimulus congruent
# dipersepsi lebih kuat. Takut → waspada ancaman (kanal keamanan membesar);
# penasaran → dunia penuh hal menarik untuk dipelajari; sedih → kehilangan
# dan kelelahan lebih terasa. Gain = 1 + persepsi_emosi_gain · Σ emosi·tabel.
# ---------------------------------------------------------------------------
EMOSI_PERSEPSI: Dict[str, Dict[str, float]] = {
    "takut":     {"keamanan": 0.8},
    "marah":     {"keamanan": 0.3, "penguasaan": 0.3},
    "senang":    {"afiliasi": 0.4, "keingintahuan": 0.3, "penguasaan": 0.2},
    "sedih":     {"afiliasi": 0.4, "energi": 0.3},
    "penasaran": {"keingintahuan": 0.8},
}


# ---------------------------------------------------------------------------
# KESADARAN — lapisan kesadaran naratif: global workspace, monolog
# batin, diri autobiografis, agensi, interosepsi afektif, monitoring realitas,
# keterbatasan atensi, kognisi sosial, pragmatik dialog, kepincangan/bias,
# nilai & batas, mortalitas & duka, mimpi & kontinuitas tidur, dan audisi-diri).
#
# Semua fitur dikunci `enable_kesadaran` (master) + flag per-konsep, sehingga
# perilaku lama persis tak berubah saat lapisan ini mati. Objek ini MEMBACA
# state Naluri secara duck-typed (levels, emosi, goals, context_aktif, mood)
# dan menulis state-nya sendiri; Naluri memanggil `step()` tiap tick dan
# `observe_event()` tiap peristiwa.
# ---------------------------------------------------------------------------
FELT_STATES: Tuple[str, ...] = (
    "nyeri", "lelah", "lapar", "sesak", "jantung", "mual", "tegang", "ringan",
)
MORAL_EMOTIONS: Tuple[str, ...] = (
    "bersalah", "malu", "bangga", "cemburu", "iri", "syukur", "haru", "kesepian",
)
# Lapisan epistemik terpisah dari moral: emosi karena mengetahui, belum tahu,
# atau menyadari bahwa model pengetahuan sendiri mungkin keliru.
EPISTEMIC_EMOTIONS: Tuple[str, ...] = (
    "bingung", "penasaran", "lega", "malu_tidak_tahu", "takjub",
    "frustrasi", "yakin", "bosan",
)
EPISTEMIC_ALIASES: Dict[str, str] = {
    "bingung": "bingung", "confused": "bingung", "confusion": "bingung",
    "penasaran": "penasaran", "curious": "penasaran", "curiosity": "penasaran",
    "lega": "lega", "relief": "lega", "relieved": "lega",
    "malu_tidak_tahu": "malu_tidak_tahu", "malu karena tidak tahu": "malu_tidak_tahu",
    "epistemic_shame": "malu_tidak_tahu", "embarrassed_not_knowing": "malu_tidak_tahu",
    "takjub": "takjub", "wonder": "takjub", "awe": "takjub",
    "frustrasi": "frustrasi", "frustration": "frustrasi",
    "yakin": "yakin", "certainty": "yakin", "confidence": "yakin",
    "bosan": "bosan", "bored": "bosan", "boredom": "bosan",
}
MORAL_ALIASES: Dict[str, str] = {
    "bersalah": "bersalah", "guilty": "bersalah", "guilt": "bersalah",
    "malu": "malu", "shame": "malu", "ashamed": "malu",
    "bangga": "bangga", "proud": "bangga", "pride": "bangga",
    "cemburu": "cemburu", "jealous": "cemburu", "jealousy": "cemburu",
    "iri": "iri", "envy": "iri", "envious": "iri",
    "syukur": "syukur", "gratitude": "syukur", "grateful": "syukur",
    "haru": "haru", "moved": "haru", "touched": "haru",
    "kesepian": "kesepian", "lonely": "kesepian", "loneliness": "kesepian",
}
REALITY_SOURCES: Tuple[str, ...] = ("persepsi", "ingatan", "imajinasi", "mimpi")
SELF_BIASES: Tuple[str, ...] = (
    "konfirmasi", "diri", "optimisme", "sosial", "negatif",
)

KESADARAN_DEFAULTS: Dict[str, Any] = {
    # master + sakelar per-konsep (semua tetap aman saat master mati)
    "enable_kesadaran": False,
    "enable_global_workspace": True,
    "enable_inner_speech": True,
    "enable_autobiography": True,
    "enable_agency": True,
    "enable_felt_state": True,
    "enable_reality_monitoring": True,
    "enable_attention_limits": True,
    "enable_second_person": True,
    "enable_pragmatics": True,
    "enable_fallibility": True,
    "enable_values": True,
    "enable_mortality": True,
    "enable_dream_continuity": True,
    "enable_self_audition": True,
    "enable_epistemic_emotions": True,
    "enable_self_opacity": True,
    "enable_social_strategy": True,
    "enable_play_aesthetics": True,
    "enable_sa_sp": True,
    "enable_free_will": True,
    # parameter lapisan
    "kesadaran_workspace_size": 3,          # puncak atensi 1..3 konten/tick
    "kesadaran_ignition_threshold": 0.62,   # ambang broadcast global
    "kesadaran_ignition_max": 64,
    "kesadaran_speech_max": 64,
    "kesadaran_timeline_max": 128,
    "kesadaran_core_max": 5,        # pilar identitas (core memory) yang disimpan
    "kesadaran_chapters_max": 32,
    "kesadaran_agency_lr": 0.18,
    "kesadaran_ownership_lr": 0.12,
    "kesadaran_effort_gain": 0.55,
    "kesadaran_blink_ticks": 4,
    "kesadaran_blindness_gain": 0.55,
    # Akumulator atensional: tidak mengambil biaya dari energi metabolik.
    "kesadaran_atensi_pulih": 0.0035,
    "kesadaran_atensi_beban_tick": 0.001,
    "kesadaran_atensi_beban_kandidat": 0.0008,
    "kesadaran_doubt_lr": 0.10,
    "kesadaran_confab_max": 48,
    "kesadaran_moral_lr": 0.25,
    "kesadaran_epistemic_lr": 0.28,
    "kesadaran_epistemic_max": 64,
    "kesadaran_self_opacity_max": 48,
    "kesadaran_social_strategy_max": 64,
    "kesadaran_humor_max": 32,
    "kesadaran_somatic_max": 64,
    "kesadaran_values_lr": 0.06,
    "kesadaran_commit_max": 48,
    "kesadaran_gossip_max": 48,
    "kesadaran_grief_decay": 0.004,
    "kesadaran_mortality_gain": 0.45,
    "kesadaran_dream_max": 64,
    # Pikiran spontan: periodenya hanya membuka kesempatan; peluang aktual
    # tetap residu × arousal, sehingga tanpa tekanan tidak ada intrusi.
    "intrusi_periode": 7,
    "intrusi_gain": 1.15,
    # Selisih perilaku-vs-self model harus berulang sebelum menjadi
    # disorientasi identitas (bukan sekadar satu prediction error).
    "selisih_self_ambang": 0.18,
    "selisih_self_ulang": 2,
    # ORDE NOL (SISTEM I): gejala murni — penampakan tanpa kategori, bahan
    # mentah dari mana kategori baru bisa mengkristal. Mati bawaan.
    "enable_gejala": False,
    "gejala_ambang_ulang": 3,        # kemunculan sebelum menendap jadi proto
    "gejala_proto_min_ulang": 4,     # bukti minimum sebelum proto jadi penuh
    "gejala_proto_min_umur": 40,     # proto harus BERTAHAN selama ini (tick)
    "gejala_memudar_ticks": 12,      # tak berulang selama ini → memudar
    "gejala_klaim_ambang": 0.14,     # kuat minimum agar modul boleh mengklaim
    "gejala_max_aktif": 24,
}

# Tujuan yang dipilih sendiri berada di luar daftar drive; bonusnya hanya
# berlaku saat goal tersebut dicantumkan eksplisit oleh pemanggil.
FREE_WILL_DEFAULTS: Dict[str, Any] = {
    "enable_free_will": True,
    "free_will_goal_max": 12,
    "free_will_bonus_weight": 0.75,
}

# Satu sumber kebenaran: parameter lapisan dilebur ke dict params Naluri
# (setelah DEFAULTS dirakit), sehingga flag/ambang hidup berdampingan.




def _periksa_kunci_drive(mapping: Mapping[str, Any], nama: str) -> None:
    """Tolak kunci yang bukan salah satu dari enam DRIVES (bukan diabaikan)."""
    asing = sorted(str(k) for k in mapping if k not in DRIVES)
    if asing:
        raise ValueError("{} memuat kunci tak dikenal {}; kunci sah: {}".format(
            nama, asing, ", ".join(DRIVES)))


def _kclip(x: Any, low: float = -1.0, high: float = 1.0) -> float:
    """Jepit nilai ke [low, high]; NaN/None → 0 (aturan ada di dukungan.numerik)."""
    return jepit(x, low, high)


