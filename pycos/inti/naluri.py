# -*- coding: utf-8 -*-
"""
NALURI — Modul Kehendak & Motivasi (pycos.inti.naluri)
======================================================
Otak berpikir. Taman mengingat. Imajinasi membayangkan. Dirigen memimpin.
Naluri memberi alasan untuk semuanya.

Profil `Persona` (sifat, register, kata pantangan) dan ringkasan `Keadaan`
batin (valensi, gairah, ketidakpastian) kini berada di `pycos.inti.persona`
(diekstraksi dari modul ini agar konsumen ringan tidak memuat mesin); nama
lama tetap tersedia di sini lewat re-export kompatibilitas.

Enam drive homeostatis (level ∈ [-1, +1]; defisit ↔ surplus):
    energi, keamanan, keingintahuan, penguasaan, afiliasi, koherensi.

API inti (semua stdlib — numpy/gymnasium/networkx TIDAK dibutuhkan):
    naluri.tick(events, cost)              — waktu berjalan, drive meluruh
    naluri.mood() -> Mood                  — valensi/arousal → dict modulasi (terbobot)
    naluri.scoring_func(scale=None)        — callable untuk Imagination (pruning/rank)
    naluri.observe_outcome(prediksi, realita) — kalibrator: rapor Imajinasi (dengan tolerance floor)
    naluri.calibration_error() -> float    — EMA kesalahan prediksi
    naluri.estimate_scale() -> float       — skala adaptif antara skor simulasi dan reward dunia
    naluri.should_sleep() -> (bool, reason) — dengan refraktori & backlog prediksi
    naluri.dream_policy() -> dict          — num_dreams, replay_strength, priority_drives
    naluri.post_sleep(report)              — pulihkan energi/koherensi, set refraktori
    naluri.goal_to_scenario() -> str       — skenario dari goal teratas
    naluri.goals -> list[Goal]             — tumpukan tujuan (max 4)
    naluri.choose_action(candidates, goal_bias=True) — keputusan goal-biased dengan satiation
    naluri.reward_for(deltas) -> float     — reward intrinsik (dengan satiation)
    naluri.project_outcome_to_drives(outcome) -> dict — konversi outcome ke drive_deltas
    naluri.apply_to_brain(brain)           — neuromodulasi & atensi drive-driven
    naluri.memory_policy() -> dict         — override config SamanticGarden
    naluri.apply_memory_policy(garden)     — tulis metadata["salience"] ke semua node Garden
    naluri.salience(node) -> float         — importance × relevansi drive
    naluri.status() -> dict
    naluri.health_check() -> dict          — diagnostik kesehatan + severity
    naluri.kompres_memori(level) -> dict   — kompresi log/memori menurut LOD
    naluri.utility(outcome) -> float       — skor utilitas outcome (berskala adaptif)
    naluri.impact_of(description) -> dict  — vektor drive dari teks deskripsi
    naluri.set_personality(weights)        — atur kepribadian (bobot drive kustom)

API NPC (save/load, LOD, preset, tidur terjadwal, lexicon injectable, HUD):
    naluri.to_dict() / Naluri.from_dict(d) — serialisasi penuh (JSON-safe)
    naluri.to_json() / Naluri.from_json(s) — bungkus json
    naluri.save(path) / Naluri.load(path)  — simpan/muat ke berkas
    naluri.set_lod(mode, divisor)          — "penuh" | "latar" | "beku" (throttling)
    naluri.set_personality_preset(nama)    — preset bernama (lihat PERSONALITIES)
    naluri.set_sleep_mode(mode)            — "kognitif" | "terjadwal" | "gabung"

API WATAK (tiga lapis kepribadian; semua aditif, aman tanpa NURANI):
    KEPRIBADIAN = "weights" (arah) · WATAK = "watak" (viskositas/filter
    plastisitas, di-inject ke params; boleh dict per-drive {"keamanan": x,
    "*": y}) · BACKSTORY = "lahir" (kondisi awal: level, setpoint, memori
    afektif, relasi, emosi — filter hanya MEMPERTAHANKAN sifat, kondisi
    awal yang menciptakannya di tick 0).
    naluri.set_personality_preset(nama, blend, terapkan_lahir)
    naluri.set_watak(**param)              — setel filter individual (tanpa preset)
    naluri.watak_aktif() -> dict           — snapshot filter yang pernah disetel
    naluri.seed_backstory(dict) -> dict    — seed kondisi awal kustom
    Naluri.personality_presets() -> dict   — katalog lengkap (weights+watak+lahir)
    naluri.describe_personality() -> dict  — kepribadian aktif + watak

API KESADARAN (berbagai lapisan kognitif; gated master `enable_kesadaran`, mati bawaan):
    naluri.enable_kesadaran(*fitur)          — nyalakan lapisan/konsep
    naluri.kesadaran.attend()                — kompetisi atensi → spotlight 1–3
    naluri.kesadaran.workspace_report()      — isi sadar + ignition terakhir
    naluri.kesadaran.inner_speech()          — monolog batin berjalan
    naluri.kesadaran.narrative_state()       — identitas naratif orang-pertama
    naluri.kesadaran.autobiographical_timeline/life_chapters/future_simulation
    naluri.kesadaran.act()/feedback()        — rasa agensi (aku vs terjadi padaku)
    naluri.kesadaran.felt_report()           — 'aku tidak enak badan' + emosi moral
    naluri.kesadaran.reality_check()/source_memory()/confabulate()
    naluri.kesadaran.inattentional_blindness()/attention_limits()
    naluri.kesadaran.joint_attention()/commit()/betray()/forgive()/gossip()
    naluri.kesadaran.dialogue_turn()/backchannel()/repair()
    naluri.kesadaran.audition_self()         — mendengar ujarannya dari luar diri
    naluri.kesadaran.hold_belief()/harden_belief()/misremember()
    naluri.kesadaran.set_value()/add_boundary()/refuse()
    naluri.kesadaran.face_death()/grieve()/mortality_state()
    naluri.kesadaran.dream()/dream_report()/wake()
    NURANI pilar H (expand konsep 2/5/6): update_felt, inner_speech,
    moral_emotion, somatic_mark, reality_monitoring, metacognitive_doubt,
    confabulation, narrate_identity, kesadaran_laporan.
    JEJAK diri autobiografis (konsep 3): autobiographical_timeline,
    life_chapters, future_simulation, counterfactual_emotions, confabulate,
    autobiography_state.

API PRESENTASI (lapisan penyajian dinamis "Pycos"; gated `enable_presentasi`):
    Menerjemahkan seluruh data internal (Naluri + NURANI + JEJAK) menjadi
    perilaku yang dapat diamati: dialog natural, ekspresi, tatapan, postur,
    napas, gestur, jarak, prosodi, perilaku idle, dan reaksi.
    naluri.enable_presentasi(*kanal)        — nyalakan lapisan/kanal
    naluri.attach_jejak(jejak)              — sambungkan memori autobiografis
    naluri.presentasi.ucap(kepada, topik)   — satu ujaran + nonverbal + prosodi
    naluri.presentasi.dengar(teks, dari)    — proses ujaran masuk (turn-taking)
    naluri.presentasi.balas(dari)           — balasan kontekstual
    naluri.presentasi.backchannel()         — umpan balik singkat
    naluri.presentasi.adegan(kepada, topik) — satu denyut perilaku lengkap
    naluri.presentasi.ekspresi()/tatapan()/postur()/napas()/gestur()/jarak()
    naluri.presentasi.prosodi()             — laju/tinggi/volume/tremor/jeda
    naluri.presentasi.perilaku_idle()       — perilaku saat tak berinteraksi
    naluri.presentasi.reaksi(event)         — peristiwa → reaksi terlihat
    naluri.presentasi.deskripsi()           — narasi pengamat siap baca
    naluri.presentasi.snapshot()/hud_state()— laporan JSON-safe

API FITUR LANJUTAN (semua gated, mati bawaan):
    META-PATTERN (JEJAK): jejak.observe_actor(aktor, aksi) / naluri.observe_player()
        → jejak.detect_patterns() / pattern_report() / is_pattern() — membaca
        KEBIASAAN Player ("hantu", "eksploitatif", "pengkhianat", ...) lalu
        menulis identitas/batas otonom.
    RITUAL (utilitas nol): naluri.enable_ritual() / naluri.ritual.maybe_trigger()
        / lakukan_ritual() — kebiasaan idiosyncratic yang terlihat tak sengaja.
    TEMPORAL: presentasi.lihat_player(present) / presentasi.proaktif() —
        menyapa saat Player diam lama atau kembali setelah absen.
    FALLIBILITY: presentasi.terima_bukti() / koreksi_ingatan() — berubah pikiran
        di tengah dialog & salah ingat detail namun yakin akan intinya.
    UI/UX: presentasi.indikator_psikologis() (Ketenangan/Fokus/Gairah/
        Keterhubungan) + presentasi.tag_dialog() ('[Rama - Waspada]').
    KAWANAN: kawanan.presentasi_all() / dialog(a,b) / adegan_all() / tag_all()
        / lihat_player_all() / proaktif_all().
    REPUTASI (fitur baru): kawanan.enable_reputasi() / catat_rumor() /
        reputasi(tentang) / terapkan_reputasi() — medan sosial bersama.

API KINERJA & SKALABILITAS (optimasi, stdlib saja):
    JEJAK: indeks terbalik token→episode (retrieve O(k) bukan O(n)), MinHash
        (set_retrieve_mode("coarse")), cache fitur, consolidate_memory()
        (konsolidasi saat tidur), performance_report(), selective persistence.
    NALURI: mood()/anticipate() ter-memo, LOD hierarkis 5 tingkat
        (penuh/ringan/latar/abstrak/beku), tick_light()/heavy_computation(),
        enable_profiling()/profile_report(), enable_replay()/export_replay()/
        Naluri.replay().
    KAWANAN: spatial hash (_nearby/_pairs_within), tick_batch(),
        tick_event_driven()/wake(), tick_layered(dekat=...), emotional_contagion(),
        social_learn()/teaching()/form_cultural_norms(), gossip_round()/
        shared_narrative(), share_prediction()/resolve_predictions()/
        prediction_leaderboard().
    KESADARAN: check_narrative_coherence() (merenung tiap 20 tick).
    CATATAN: akselerasi native (Cython/Rust), GPU, dan dashboard web TIDAK
    diimplementasikan di sini (butuh dependensi/berkas baru); state JSON sudah
    siap diekspor untuk profiler/dashboard eksternal.

API DINAMIKA SOSIAL & KEBENARAN (gosip, faksi, konfrontasi, peluruhan):
    KAWANAN.trust_weight(sumber)          — bobot kepercayaan penyebar gosip;
        catat_rumor(...) otomatis menghitungnya & menandai `alarm_palsu` bila
        sumber punya riwayat konfabulasi/penyangkalan atau tak dipercaya.
    KAWANAN.echo_chamber(target, ...)     — faksi organik (in-group menguatkan
        rasa takut, out-group = target jadi "monster"); faksi() untuk HUD.
    KAWANAN.konfrontasi(target, saksi, korban, bukti) — paksa terima_bukti() +
        koreksi_ingatan() secara real-time; tandai rumor terkonfirmasi.
    KAWANAN.decay_of_truth(window)        — gosip lama tanpa konfirmasi makin
        ekstrem lewat misremember()+confabulate() ("iblis yang memakan jiwa");
        konfirmasi_rumor()/peluruhan_kebenaran() untuk kontrol & HUD.
    KAWANAN.konsensus(tentang)            — social proof: 5 sumber berbeda
        dalam jendela singkat meng-override kredibilitas individu.
    NALURI.hancurkan_kepercayaan(ent)     — pengkhianatan mematahkan trust;
        viskositas_relasi(ent) menunjukkan pemulihan yang sangat diperlambat.
    KESADARAN.terima_bukti()/koreksi_ingatan()/tandai_alarm_palsu()/
        konfrontasi_state().

API MOMEN & INTERIOR (satu momen > rata-rata; kebocoran; hesitasi):
    NALURI.tandai_momen(teks, klaim=...) / KESADARAN.tandai_core_memory()
        — core memory: tak pernah di-prune, salience tinggi di `_candidates()`,
        mengikat klaim identitas, dan menaikkan `affective_trust_cap` khusus
        untuk signature-nya (memfilter interpretasi pengalaman baru).
        `core_memory_state()` untuk HUD.
    PRESENTASI.tell_katalog()   — tell lahir dari watak: drive dengan
        `setpoint_lr` terkecil (paling beku) bocor saat dilanggar & saat
        menyembunyikan sesuatu. Konsisten per-NPC, TIDAK pernah diumumkan;
        muncul sebagai `ekspresi()["kebocoran"]` (deskripsi fisik biasa).
    PRESENTASI hesitasi — `presentasi_hesitasi` (sakelar): saat ignition,
        konflik drive, atau perubahan relasi dalam 2–3 tick terakhir, act
        menjadi "menimbang" (jeda lebih panjang) lalu act berubah;
        `hesitation_state()`.
    NALURI.catat_utang()/bayar_utang()/utang(ent)/menarik_diri(ent) —
        utang emosional kumulatif; beratnya menekan `social_prior` secara
        proporsional; lewat ambang NPC menarik diri aktif. commit()/betray()
        menambah utang, forgive() membayarnya.
    LINGER (histeresis) — `presentasi_emosi_linger`/`_postur_linger`/
        `_tatapan_linger`: ekspresi punya momentum, bukan snapshot.

MESIN TUTUR GENERATIF (pycos.bahasa.tutur + pycos.sumber_daya):
    Ujaran tidak lagi dari template hardcoded. Arsitektur berlapis:
        L0 Rencana Konten  — tindak tutur → proposisi bertipe (biografi masuk
                             sebagai ARGUMEN; proposisi mengkerut bila bahan
                             tidak ada — penurunan anggun, bukan template).
        L1 Bentuk Semantik — kerangka subkategorisasi per predikat → slot.
        L2 Leksikon        — isi slot: hard filter (register/bahasa/lattice/
                             restriksi seleksional) + soft score (dot product
                             state×fitur kata) + freshness penalty.
        L3 Morfologi       — nasalisasi, voice (dipilih topik), afiks, partikel,
                             reduplikasi, linearisasi dengan pemindahan topik.
    Sumber daya: `pycos/sumber_daya/leksikon_pycos.json` (ribuan lema ID/EN,
    lattice tipe semantik, kerangka predikat, aturan morfologi).
    API: presentasi.set_leksikon(path) / presentasi.tutur_engine() /
         presentasi.ucap(...)["trace"] (aktifkan presentasi_trace).
    Sakelar: `presentasi_generatif` (otomatis mati bila leksikon absen → jalur
    lama tetap dipakai, backward-compatible).

API PERSEPSI (lapisan rekonstruksi dunia→drive; gated `enable_perception`):
    Dunia tidak masuk apa adanya: stimulus melewati derau reseptor + deteksi
    sinyal (criterion per-drive; negatif = hipervigilan → alarm palsu),
    kompresi Weber-Fechner terhadap level adaptasi, habituasi, atensi
    terbatas (menyempit oleh arousal), congruence emosi, dan blend top-down
    dengan prior afektif (pemrosesan prediktif).
    naluri.persepsi(teks) -> dict          — apa yang dipersepsi (baca-saja)
    naluri.affordances(teks|kandidat)      — apa yang menonjol sesuai kebutuhan
    naluri.persepsi_state() -> dict        — saluran, counter, jejak terakhir
    (event tick otomatis difilter apply_events saat pilar aktif)
    naluri.sleep_status() -> dict          — alasan tidur yang terbaca pemain
    naluri.set_lexicon(mapping, merge)     — inject/ubah lexicon (i18n)
    naluri.hud_state() / naluri.intent()   — ringkasan untuk HUD, bukan debug
    KawananNPC                             — manajer banyak NPC (LOD per jarak)

API EMPATI (lapisan emosi & relasi sosial; semuanya aditif, mati bawaan):
    naluri.enable_emosi(True)              — nyalakan mesin emosi diskret
    naluri.feel(emosi, intensitas)         — suntik emosi ("takut","marah",
                                             "senang","sedih","penasaran")
    naluri.emosi_state()/emosi_dominan()   — baca keadaan emosi
    naluri.mode_npc()                      — satu sakelar: tidur terjadwal +
                                             emosi + memori sosial + sirkadian
    naluri.kenal(entitas, nama)            — daftarkan pemain/NPC lain
    naluri.berinteraksi(entitas, muatan)   — satu interaksi sosial penuh:
                                             relasi + drive + emosi + log
    naluri.relasi(entitas)/label_relasi()  — keadaan relasi utk dialog/HUD
    naluri.choose_action(... target=entitas) — kandidat aksi boleh menyebut
                                             entitas; prior relasi mem-bias
                                             afiliasi/keamanan (pilar E NURANI)
    KawananNPC.interaksi(a, b, muatan)     — dua NPC saling berinteraksi
    KawananNPC.set_position(nama, pos)     — set koordinat 2D/3D untuk radius
    KawananNPC.broadcast(sumber, event, radius) — event ber-atenuasi jarak
    KawananNPC.biarkan_bersosialisasi()    — NPC kesepian berpasangan sendiri

API NURANI (konsep 17 — lapisan meta-plastisitas; semuanya aditif dan setiap
pilar mati secara bawaan, jadi perilaku lama utuh bila tidak dinyalakan):
    naluri.experience(teks, deltas)         — pilar A: rekam satu pengalaman
    naluri.anticipate(teks) -> dict         — pilar A: prior afektif sebelum lexicon
    naluri.forget_affective(max_age) -> int — pilar A: prune memori afektif manual
    naluri.calibration_report()             — pilar B: Brier + galat per drive + reliability
    naluri.setpoint(drive) -> float         — pilar C: setpoint plastis satu drive
    naluri.interoception_matrix() -> list   — pilar C: korelasi defisit antar-drive
    naluri.circadian_phase() -> str         — pilar D: pagi/siang/sore/malam
    naluri.resolve_conflict(candidates)     — pilar D: diagnostik konflik drive
    naluri.flow_state() -> bool             — pilar D: keadaan terserap
    naluri.meta_status() -> dict            — ringkasan seluruh lapisan NURANI
    naluri.enable_nurani(*pilar)            — nyalakan/matikan pilar

Catatan: modul ini didesain nol-dependensi agar aman di Termux; integrasi dengan
samre.core.brain / samre.imagination.engine / samre.memory.garden / samre.orchestrator bersifat
duck-typed (tidak perlu import langsung), sehingga modulnya tetap bisa
dipanggil sendiri. Demo: `python -m pycos.inti.naluri` dari akar repositori
atau `python3 pycos/inti/naluri.py` dari mana pun. Lapisan NURANI tinggal di
`pycos.refleksi.nurani`, satu paket ini; bila
lapisan opsional itu tidak dapat diimpor, `naluri.nurani` menjadi None dan
seluruh kait NURANI menjadi no-op.
"""
from __future__ import annotations

import copy as _copy
copy = _copy
import json as _json
json = _json
import math as _math
math = _math
import os
import random as _random
random = _random
import re as _re
re = _re
import time as _time
time = _time
import typing as _typing
Sequence = _typing.Sequence
import itertools as _itertools
islice = _itertools.islice
import dataclasses as _dataclasses
dataclass = _dataclasses.dataclass
asdict = _dataclasses.asdict
field = _dataclasses.field
from typing import Any, Dict, Optional
Callable = _typing.Callable
Iterable = _typing.Iterable
List = _typing.List
Mapping = _typing.Mapping
Tuple = _typing.Tuple

if not __package__:  # berkas dieksekusi langsung, bukan sebagai modul paket
    # `python3 pycos/inti/naluri.py` di dalam checkout: kenalkan direktori
    # induk paket ke sys.path supaya impor `pycos.*` tetap resolve tanpa
    # instalasi maupun PYTHONPATH manual.
    import os as _os
    import sys as _sys

    _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.dirname(
        _os.path.abspath(__file__)))))
    del _os, _sys

# Pengaman integrasi runtime + resolusi sumber daya — wajib, satu paket.
from pycos.dukungan import patching as _patching
install_method = _patching.install_method
install_methods = _patching.install_methods
optional_module = _patching.optional_module
wrap_method = _patching.wrap_method
from pycos.dukungan import sumber as _sumber
kandidat_leksikon = _sumber.kandidat_leksikon
from pycos.dukungan import diagnostik as _diag
from pycos.dukungan import batas_memori as _modul_batas
_batas_memori = _modul_batas.batas
_pangkas_memori = _modul_batas.pangkas
from pycos.dukungan import numerik as _numerik
float_hingga = _numerik.float_hingga
jepit = _numerik.jepit
jepit_01 = _numerik.jepit_01
jepit_drive = _numerik.jepit_drive

try:  # NURANI (konsep 17): refleksi dan meta-plastisitas
    from pycos.refleksi.nurani import (CalibrationReport, NURANI_DEFAULTS,
                                       Nurani)
except ImportError as galat:  # lapisan NURANI tidak ikut disalin: kait jadi no-op
    CalibrationReport, NURANI_DEFAULTS, Nurani = None, {}, None
    _diag.catat("naluri.shim.nurani",
                "lapisan NURANI tidak tersedia; kait menjadi no-op",
                galat=type(galat).__name__)

try:  # JEJAK opsional (duck-typed): meta-pattern & diri autobiografis
    from pycos.memori.jejak_prediksi import JejakPrediksi
except ImportError as galat:  # tanpa JEJAK: memori episodik mati
    JejakPrediksi = None
    _diag.catat("naluri.shim.jejak",
                "lapisan JEJAK tidak tersedia; memori episodik mati",
                galat=type(galat).__name__)

try:  # MESIN TUTUR generatif (L0–L3) + leksikon paket — opsional
    from pycos.bahasa.tutur import (TuturEngine, GenContext,
                                    konteks_dari_presentasi, SASPAnalyzer)
except ImportError as galat:  # tanpa mesin tutur → pakai jalur lama
    TuturEngine = GenContext = konteks_dari_presentasi = SASPAnalyzer = None
    _diag.catat("naluri.shim.tutur",
                "mesin tutur tidak tersedia; jalur template dipakai",
                galat=type(galat).__name__)


# ---------------------------------------------------------------------------
# Konstanta publik
# ---------------------------------------------------------------------------
# Batas memori daftar kehilangan (`losses`); sebelumnya tumbuh tanpa batas.
from pycos.inti import _konfigurasi

_MAKS_LOSSES = _konfigurasi._MAKS_LOSSES
DRIVES = _konfigurasi.DRIVES
STAGE_WEIGHTS = _konfigurasi.STAGE_WEIGHTS
PERSONALITIES = _konfigurasi.PERSONALITIES
PERSONALITY_ALIASES = _konfigurasi.PERSONALITY_ALIASES
DEFAULTS = _konfigurasi.DEFAULTS
_nilai_per_drive = _konfigurasi._nilai_per_drive
LEXICON = _konfigurasi.LEXICON
TAG_LEXICON = _konfigurasi.TAG_LEXICON
LEXICON_EN = _konfigurasi.LEXICON_EN
TAG_LEXICON_EN = _konfigurasi.TAG_LEXICON_EN
LEXICON_PACKS = _konfigurasi.LEXICON_PACKS
DRIVE_NEUROMOD = _konfigurasi.DRIVE_NEUROMOD
DRIVE_ATTENTION = _konfigurasi.DRIVE_ATTENTION
GOAL_TEMPLATES = _konfigurasi.GOAL_TEMPLATES
HUD_DRIVE_INTENT = _konfigurasi.HUD_DRIVE_INTENT
HUD_MOOD_LABELS = _konfigurasi.HUD_MOOD_LABELS
LOD_MODES = _konfigurasi.LOD_MODES
LOD_ALIASES = _konfigurasi.LOD_ALIASES
LOD_DIVISOR_FACTOR = _konfigurasi.LOD_DIVISOR_FACTOR
SLEEP_MODES = _konfigurasi.SLEEP_MODES
SLEEP_MODE_ALIASES = _konfigurasi.SLEEP_MODE_ALIASES
NPC_PARAMS = _konfigurasi.NPC_PARAMS
EMOSI = _konfigurasi.EMOSI
EMOSI_ALIASES = _konfigurasi.EMOSI_ALIASES
EMOSI_LABELS = _konfigurasi.EMOSI_LABELS
EMOSI_HUD_THRESHOLD = _konfigurasi.EMOSI_HUD_THRESHOLD
EMOSI_PERSEPSI = _konfigurasi.EMOSI_PERSEPSI
FELT_STATES = _konfigurasi.FELT_STATES
MORAL_EMOTIONS = _konfigurasi.MORAL_EMOTIONS
EPISTEMIC_EMOTIONS = _konfigurasi.EPISTEMIC_EMOTIONS
EPISTEMIC_ALIASES = _konfigurasi.EPISTEMIC_ALIASES
MORAL_ALIASES = _konfigurasi.MORAL_ALIASES
REALITY_SOURCES = _konfigurasi.REALITY_SOURCES
SELF_BIASES = _konfigurasi.SELF_BIASES
KESADARAN_DEFAULTS = _konfigurasi.KESADARAN_DEFAULTS
FREE_WILL_DEFAULTS = _konfigurasi.FREE_WILL_DEFAULTS
_periksa_kunci_drive = _konfigurasi._periksa_kunci_drive
_kclip = _konfigurasi._kclip
DEFAULTS.update(NURANI_DEFAULTS)
DEFAULTS.update(KESADARAN_DEFAULTS)
DEFAULTS.update(FREE_WILL_DEFAULTS)

from pycos.inti import kesadaran as _kesadaran
Kesadaran = _kesadaran.Kesadaran


# ---------------------------------------------------------------------------
# PRESENTASI — lapisan penyajian dinamis ("Pycos performance layer").
#
# Menerjemahkan kekayaan data internal (Naluri + NURANI + JEJAK, bersama-sama
# disebut "Pycos") menjadi perilaku yang DAPAT DIAMATI secara natural: dialog
# (tindak tutur, hedges, jeda, pronomina, referensi sejarah bersama), kanal
# nonverbal (ekspresi, tatapan, postur, napas, gestur, jarak, mikro-ekspresi),
# prosodi suara, perilaku idle, dan reaksi terhadap peristiwa. Lapisan ini
# membaca state, tidak memegang kendali; semua aksi tulis internal dibatasi
# pada pencatatan pragmatik (turn/backchannel) dan bersifat opsional.
#
# Gated oleh master `enable_presentasi` (mati bawaan) + flag kanal.
# ---------------------------------------------------------------------------
from pycos.inti.presentasi import PRESENTASI_DEFAULTS
DEFAULTS.update(PRESENTASI_DEFAULTS)

from pycos.inti import presentasi as _presentasi
Presentasi = _presentasi.Presentasi


# ---------------------------------------------------------------------------
# RITUAL — perilaku "utilitas nol" (idiosyncrasy).
#
# Makhluk sadar melakukan hal yang TIDAK menambah drive apa pun, tetapi
# memberi kenyamanan psikologis atau sekadar kebiasaan. Ritual dipicu oleh
# kondisi spesifik (watak + sedikit ketidaknyamanan), berpeluang rendah per
# tick, dan hanya muncul saat tidak ada interaksi langsung — sehingga Player
# menemukannya "secara tidak sengaja". Efeknya menyentuh afek/presentasi,
# bukan homeostatis: kesan mesin larut.
# ---------------------------------------------------------------------------
from pycos.inti import ritual as _ritual
RITUAL_DEFAULTS = _ritual.RITUAL_DEFAULTS
Ritual = _ritual.Ritual

DEFAULTS.update(RITUAL_DEFAULTS)

# ---------------------------------------------------------------------------
# Data classes
from pycos.inti import keadaan as _keadaan
Goal = _keadaan.Goal
Mood = _keadaan.Mood
# ---------------------------------------------------------------------------




# ---------------------------------------------------------------------------
# Keadaan batin ringkas & profil persona — rumahnya kini modul terpisah
# (pycos.inti.persona). Nama lama tetap tersedia lewat re-export kompatibilitas
# di sini sehingga `from pycos.inti.naluri import Persona` tidak putus.
# ---------------------------------------------------------------------------
from pycos.inti import persona as _persona

Keadaan = _persona.Keadaan
Persona = _persona.Persona
PERSONA_CONTOH = _persona.PERSONA_CONTOH
SIFAT_DIKENAL = _persona.SIFAT_DIKENAL
REGISTER_DIKENAL = _persona.REGISTER_DIKENAL
normalisasi_frasa = _persona.normalisasi_frasa


# ---------------------------------------------------------------------------
# Naluri (InstinctCore)
# ---------------------------------------------------------------------------
from pycos.inti.mesin import Naluri as Naluri


# ---------------------------------------------------------------------------
# NPC helpers — pemakaian untuk satu atau beberapa NPC
# ---------------------------------------------------------------------------
def buat_npc(nama: str,
             personality: Optional[str] = None,
             npc: bool = True,
             sosial: bool = False,
             **kwargs: Any) -> Naluri:
    """Factory instans NPC: nama + preset kepribadian + parameter ramah-NPC.

    `npc=True` menerapkan NPC_PARAMS (tidur terjadwal murni sirkadian) agar
    NPC tidak menghilang dari scene tanpa alasan yang terbaca pemain.
    `sosial=True` additionally menyalakan `mode_npc()`: mesin emosi +
    memori sosial NURANI + ritme sirkadian (EMPATI lengkap).
    kwargs lain diteruskan ke konstruktor Naluri (lexicon=, lod=, params=,
    stage=, rng_seed=, ...).

    Contoh:
        penjaga = buat_npc("Rama", personality="penjaga")
        turis   = buat_npc("Ana", personality="penjelajah", lod="latar")
        guide   = buat_npc("Bob", lexicon=LEXICON_EN, tag_lexicon=TAG_LEXICON_EN)
        teman   = buat_npc("Citra", personality="sosiawan", sosial=True)
    """
    params: Dict[str, Any] = dict(NPC_PARAMS) if npc else {}
    user_params = kwargs.pop("params", None)
    if user_params:
        params.update(user_params)
    n = Naluri(name=nama, personality=personality,
               params=params or None, **kwargs)
    if sosial:
        n.mode_npc(True)
    return n


# ---------------------------------------------------------------------------
# REPUTASI — fitur baru: medan sosial reputasi yang menyebar antar-NPC.
#
# Melengkapi kognisi orang-kedua (Kesadaran.gossip, second-person loop) dan
# meta-pattern JEJAK: apa yang SATU NPC amati/obrolkan tentang Player/NPC lain
# menjadi REPUTASI BERSAMA yang dapat dibaca semua NPC. Reputasi memengaruhi
# relasi, dialog, dan kesiapan menolong/menolak — kesadaran menjadi kolektif.
# ---------------------------------------------------------------------------
from pycos.inti import reputasi as _reputasi

REPUTASI_DEFAULTS = _reputasi.REPUTASI_DEFAULTS
REPUTASI_SUMBU = _reputasi.REPUTASI_SUMBU
Reputasi = _reputasi.Reputasi

DEFAULTS.update(REPUTASI_DEFAULTS)

from pycos.inti import kawanan as _kawanan
KawananNPC = _kawanan.KawananNPC


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _get_attr(obj: Any, name: str, default: Any = None) -> Any:
    """Ambil atribut dari objek (objek biasa, dict, atau punya .get)."""
    if obj is None:
        return default
    if isinstance(obj, dict):
        return obj.get(name, default)
    return getattr(obj, name, default)


# ---------------------------------------------------------------------------
# Demo NPC (fix #1-#7 sekaligus): preset, LOD, tidur terjadwal, HUD, save/load
# ---------------------------------------------------------------------------
def demo_npc(ticks: int = 72, seed: int = 21) -> Dict[str, Any]:
    """Demo multi-NPC: tiga NPC dengan preset berbeda, LOD per jarak pemain,
    tidur terjadwal (sirkadian murni), HUD terbaca, dan round-trip save/load."""
    from pycos.inti.demo.skenario import demo_npc as jalankan
    return jalankan(ticks=ticks, seed=seed)


# ---------------------------------------------------------------------------
# Demo EMPATI: emosi diskret + relasi sosial (pilar E) antar-NPC & "pemain"
# ---------------------------------------------------------------------------
def demo_empati(ticks: int = 48, seed: int = 31) -> Dict[str, Any]:
    """Demo lapisan EMPATI: dua NPC sosial, interaksi dengan 'pemain'
    (positif lalu penghinaan), event menakutkan, prior sosial di
    choose_action, dan round-trip save/load dengan relasi + emosi."""
    from pycos.inti.demo.skenario import demo_empati as jalankan
    return jalankan(ticks=ticks, seed=seed)


# ---------------------------------------------------------------------------
# Main: demo
# ---------------------------------------------------------------------------
def demo_watak(ticks_bukti: int = 120, ticks_tarik: int = 180,
               seed: int = 53) -> Dict[str, Any]:
    """Demo lapisan WATAK: paranoid vs penjelajah di dunia yang SAMA.

    Tiga klaim yang dibuktikan:
      1. VISKOSITAS — 120 tick "bukti dunia aman" menggeser setpoint
         keamanan penjelajah (lr 0.002) tetapi nyaris tidak menggeser
         milik paranoid (lr 1e-5): ia TIDAK BISA belajar aman.
      2. BACKSTORY — saat bukti ditarik, paranoid tetap defisit besar
         (ekspektasi 0.55 tak pernah turun), penjelajah sudah beradaptasi.
      3. COLD-START — NPC paranoid baru WASPADA DI TICK 1 (setpoint +
         emosi + prior afektif ter-seed "lahir"), bukan belajar dulu.
    """
    from pycos.inti.demo.skenario import demo_watak as jalankan
    return jalankan(ticks_bukti=ticks_bukti, ticks_tarik=ticks_tarik, seed=seed)


def demo_introspeksi(ticks: int = 120, seed: int = 89) -> Dict[str, Any]:
    """Demo pilar G INTROSPEKSI DIRI: fisiologi nyata, bukan pseudo-science.

    Tiga fenomena yang dibuktikan (semua terukur angka):
      1) Interosepsi berderau (insula - Craig 2002): model diri != actual,
         akurasi = Pearson(actual, perceived) < 1.0 karena noise, membaik
         dengan pembelajaran (lr).
      2) Metakognisi (PFC - Fleming 2012): confidence memprediksi correctness
         -> meta-d' > 0.5 (chance) bila sistem belajar, Brier confidence turun.
      3) Sadar diri (Global Workspace - Dehaene): discrepancy > ambang +
         confidence -> sadar_diri_ticks naik, narasi DMN terbentuk.
    """
    from pycos.inti.demo.skenario import demo_introspeksi as jalankan
    return jalankan(ticks=ticks, seed=seed)


def demo_kesadaran(ticks: int = 240, seed: int = 137) -> Dict[str, Any]:
    """Demo lapisan KESADARAN — dari reaksi tersebar ke arus sadar.

    1 global workspace + ignition · 2 monolog batin + identitas · 3 diri
    autobiografis + time travel · 4 rasa agensi · 5 interosepsi afektif +
    emosi moral · 6 monitoring realitas + keraguan · 7 keterbatasan atensi ·
    8 kognisi sosial orang-kedua · 9 pragmatik dialog · 10 kepincangan/bias ·
    11 nilai & batas · 12 mortalitas & duka · 13 mimpi & kontinuitas tidur ·
    14 audisi-diri: menerima suara sendiri sebagai input eksternal-sebagian.
    """
    from pycos.inti.demo.skenario import demo_kesadaran as jalankan
    return jalankan(ticks=ticks, seed=seed)


def demo_presentasi(ticks: int = 180, seed: int = 211) -> Dict[str, Any]:
    """Demo lapisan PRESENTASI (Pycos): data internal → perilaku teramati.

    Menunjukkan satu NPC yang sama menampilkan dialog + kanal nonverbal yang
    BERUBAH sesuai keadaan internal: ancaman (waspada), duka (mengenang),
    disonansi (rasionalisasi), nilai (menolak), keraguan (ragu), dan momen
    tenang (akrab). Semua dari state Pycos, bukan skrip.
    """
    from pycos.inti.demo.skenario import demo_presentasi as jalankan
    return jalankan(ticks=ticks, seed=seed)


def demo_fitur_lanjutan(ticks: int = 90, seed: int = 331) -> Dict[str, Any]:
    """Demo 8 fitur lanjutan: meta-pattern, ritual, temporal, fallibility,
    UI psikologis, presentasi kawanan, dan reputasi sosial."""
    from pycos.inti.demo.skenario import demo_fitur_lanjutan as jalankan
    return jalankan(ticks=ticks, seed=seed)


def demo_kinerja(seed: int = 7) -> Dict[str, Any]:
    """Demo optimasi: indeks terbalik, konsolidasi, LOD hierarkis, profiler,
    spatial hash, event-driven, replay deterministik."""
    from pycos.inti.demo.skenario import demo_kinerja as jalankan
    return jalankan(seed=seed)


def demo_sosial(seed: int = 11) -> Dict[str, Any]:
    """Demo 6 fitur sosial: trust weight, faksi, konfrontasi, decay of truth,
    social proof, dan asimetri pemulihan kepercayaan."""
    from pycos.inti.demo.skenario import demo_sosial as jalankan
    return jalankan(seed=seed)


def demo_momen(seed: int = 13) -> Dict[str, Any]:
    """Demo 5 tambahan: core memory, tells, diam bermakna, utang, linger."""
    from pycos.inti.demo.skenario import demo_momen as jalankan
    return jalankan(seed=seed)


def demo_tutur(seed: int = 21) -> Dict[str, Any]:
    """Demo MESIN TUTUR GENERATIF (L0–L3) + leksikon eksternal."""
    from pycos.inti.demo.skenario import demo_tutur as jalankan
    return jalankan(seed=seed)


def demo_kognisi(seed: int = 31) -> Dict[str, Any]:
    """Demo 5 mekanisme kognisi lanjut (pycos.mandiri.kognisi_lanjut)."""
    from pycos.inti.demo.skenario import demo_kognisi as jalankan
    return jalankan(seed=seed)


def demo_persepsi(ticks: int = 200, seed: int = 71) -> Dict[str, Any]:
    """Demo lapisan PERSEPSI: dunia tidak masuk apa adanya.

    Tujuh fenomena psikofisika/fisiologi, masing-masing dicetak dengan
    angka pembanding: (1) hukum Weber-Fechner + level adaptasi, (2) habituasi
    + pemulihan spontan, (3) alarm palsu hipervigilan (SDT), (4) congruence
    emosi + penyempitan atensi Easterbrook, (5) blend top-down prediktif
    (persepsi bisa BERBALIK tanda oleh ekspektasi), (6) affordance Gibson,
    (7) pembelajaran perseptual (d' naik oleh prediksi akurat).
    """
    from pycos.inti.demo.skenario import demo_persepsi as jalankan
    return jalankan(ticks=ticks, seed=seed)


# ===========================================================================
# INTEGRASI KOGNISI LANJUT — eversi/TD, drift Ornstein-Uhlenbeck,
# graf asosiasi Hebbian, dan pemilihan tindakan Boltzmann.
# Semua GATED OFF bawaan; aktifkan via enable_*(). pycos.mandiri.kognisi_lanjut
# ===========================================================================
from pycos.inti.ekstensi import pasang as _pasang_ekstensi
from pycos.inti.ekstensi import kognisi as _ekstensi_kognisi
_kog_disonansi = _ekstensi_kognisi._kog_disonansi
_kog_situasi = _ekstensi_kognisi._kog_situasi
_kog_aksi = _ekstensi_kognisi._kog_aksi
_kog_dari = _ekstensi_kognisi._kog_dari
_naluri_enable_eversi = _ekstensi_kognisi._naluri_enable_eversi
_naluri_enable_drift = _ekstensi_kognisi._naluri_enable_drift
_naluri_enable_asosiasi = _ekstensi_kognisi._naluri_enable_asosiasi
_naluri_eversi_param = _ekstensi_kognisi._naluri_eversi_param
_naluri_latent_drift = _ekstensi_kognisi._naluri_latent_drift
_naluri_asosiasi = _ekstensi_kognisi._naluri_asosiasi
_naluri_koaktifkan = _ekstensi_kognisi._naluri_koaktifkan
_naluri_aktifkan_konsep = _ekstensi_kognisi._naluri_aktifkan_konsep
_naluri_fobia = _ekstensi_kognisi._naluri_fobia
_naluri_kepercayaan = _ekstensi_kognisi._naluri_kepercayaan
_naluri_perbarui_kepercayaan = _ekstensi_kognisi._naluri_perbarui_kepercayaan
_naluri_kognisi_state = _ekstensi_kognisi._naluri_kognisi_state
_naluri_kog_step = _ekstensi_kognisi._naluri_kog_step
_kog_tick = _ekstensi_kognisi._kog_tick
_kog_to_dict = _ekstensi_kognisi._kog_to_dict
_kog_from_dict = _ekstensi_kognisi._kog_from_dict
_pres_enable_boltzmann = _ekstensi_kognisi._pres_enable_boltzmann
_pres_skor_acts = _ekstensi_kognisi._pres_skor_acts
_pres_pilih_act_boltzmann = _ekstensi_kognisi._pres_pilih_act_boltzmann
_pres_boltzmann_terakhir = _ekstensi_kognisi._pres_boltzmann_terakhir
_pilih_act_boltzmann = _ekstensi_kognisi._pilih_act_boltzmann
_pasang_boltzmann = _ekstensi_kognisi._pasang_boltzmann

_pasang_ekstensi(Naluri, nama="kognisi")



def demo_organik():
    """Demo STATE ORGANIK: lima perubahan SIFAT state (bukan penambahan angka).

    1. Kehilangan topologis — slot kosong, bukan bobot kecil.
    2. Luka yang mengecualikan domain — lubang, bukan skalar rendah.
    3. Identitas yang membatasi — emosi ditolak oleh state.
    4. Waktu yang tidak seragam — half-life per-episode yang dipelajari.
    5. Kegagalan dari dalam — kalimat terbentuk, tubuh menolak mengucapkannya.
    """
    from pycos.inti.demo.skenario import demo_organik as jalankan
    return jalankan()





from pycos.inti.ekstensi import organik as _ekstensi_organik
_organik_dari = _ekstensi_organik._organik_dari
_organik_bungkus_serialisasi = _ekstensi_organik._organik_bungkus_serialisasi
_naluri_organik = _ekstensi_organik._naluri_organik
_naluri_organik_ambil = _ekstensi_organik._naluri_organik_ambil
_naluri_organik_pasang = _ekstensi_organik._naluri_organik_pasang
_naluri_tick = _ekstensi_organik._naluri_tick
daftarkan_slot = _ekstensi_organik.daftarkan_slot
kosongkan_slot = _ekstensi_organik.kosongkan_slot
isi_ulang_slot = _ekstensi_organik.isi_ulang_slot
slot_terisi = _ekstensi_organik.slot_terisi
intensitas_topologis = _ekstensi_organik.intensitas_topologis
layak_cabang = _ekstensi_organik.layak_cabang
duka = _ekstensi_organik.duka
kehilangan_state = _ekstensi_organik.kehilangan_state
cabang_mustahil = _ekstensi_organik.cabang_mustahil
tetapkan_identitas = _ekstensi_organik.tetapkan_identitas
batas_identitas_state = _ekstensi_organik.batas_identitas_state
emosi_ditolak = _ekstensi_organik.emosi_ditolak
tandai_stimulus_bertentangan = _ekstensi_organik.tandai_stimulus_bertentangan
organik_state = _ekstensi_organik.organik_state
_organik_emosi_naikkan = _ekstensi_organik._organik_emosi_naikkan
_organik_future_simulation = _ekstensi_organik._organik_future_simulation
_presentasi_organik = _ekstensi_organik._presentasi_organik
_organik_konteks_tubuh = _ekstensi_organik._organik_konteks_tubuh
kelayakan_tutur = _ekstensi_organik.kelayakan_tutur
penolakan_state = _ekstensi_organik.penolakan_state
_organik_ucap = _ekstensi_organik._organik_ucap
_organik_felt_mentah = _ekstensi_organik._organik_felt_mentah
apersepsi_state = _ekstensi_organik.apersepsi_state
rasa_kabut = _ekstensi_organik.rasa_kabut
_organik_felt_report_jujur = _ekstensi_organik._organik_felt_report_jujur
pegang_dua = _ekstensi_organik.pegang_dua
pegang_keyakinan = _ekstensi_organik.pegang_keyakinan
keyakinan_paralel = _ekstensi_organik.keyakinan_paralel
pengaruh_paralel = _ekstensi_organik.pengaruh_paralel
tanpa_resolusi = _ekstensi_organik.tanpa_resolusi
bertindak_dari_lapisan = _ekstensi_organik.bertindak_dari_lapisan
_organik_tubuh_langkah = _ekstensi_organik._organik_tubuh_langkah
tubuh_state = _ekstensi_organik.tubuh_state
suntik_tubuh = _ekstensi_organik.suntik_tubuh
_organik_tick = _ekstensi_organik._organik_tick
_NAMA_STOP = _ekstensi_organik._NAMA_STOP
_nama_dari_teks = _ekstensi_organik._nama_dari_teks
auto_deteksi_slot = _ekstensi_organik.auto_deteksi_slot
_organik_hud_state = _ekstensi_organik._organik_hud_state
daftarkan_residu = _ekstensi_organik.daftarkan_residu
tambal_residu = _ekstensi_organik.tambal_residu
ambang_dimodifikasi = _ekstensi_organik.ambang_dimodifikasi
langit_dimodifikasi = _ekstensi_organik.langit_dimodifikasi
residu_state = _ekstensi_organik.residu_state
mulai_vacancy = _ekstensi_organik.mulai_vacancy
vacancy_state = _ekstensi_organik.vacancy_state
_vacancy_aktif = _ekstensi_organik._vacancy_aktif
_vacancy_lewat = _ekstensi_organik._vacancy_lewat
_kesadaran_intrusi_spontan = _ekstensi_organik._kesadaran_intrusi_spontan
paksa_intrusi = _ekstensi_organik.paksa_intrusi
intrusi_state = _ekstensi_organik.intrusi_state
_detak_context = _ekstensi_organik._detak_context
_catat_interupsi = _ekstensi_organik._catat_interupsi
_detak_checkpoint = _ekstensi_organik._detak_checkpoint
paksa_interupsi = _ekstensi_organik.paksa_interupsi
detak_internal_state = _ekstensi_organik.detak_internal_state
_catat_selisih_self = _ekstensi_organik._catat_selisih_self
selisih_self_state = _ekstensi_organik.selisih_self_state
interupsi_internal_state = _ekstensi_organik.interupsi_internal_state
_organik_lanjut_ucap = _ekstensi_organik._organik_lanjut_ucap
_organik_hold_belief = _ekstensi_organik._organik_hold_belief

_pasang_ekstensi(Naluri, nama="organik")






from pycos.inti.ekstensi import gejala as _ekstensi_gejala
_gejala_modul = _ekstensi_gejala._gejala_modul
_gejala_dari = _ekstensi_gejala._gejala_dari
_gejala_aktif = _ekstensi_gejala._gejala_aktif
gejala_rasakan = _ekstensi_gejala.gejala_rasakan
_gejala_aktifkan_kembali = _ekstensi_gejala._gejala_aktifkan_kembali
_gejala_konten = _ekstensi_gejala._gejala_konten
_gejala_klaim_drive = _ekstensi_gejala._gejala_klaim_drive
_gejala_klaim_emosi = _ekstensi_gejala._gejala_klaim_emosi
_gejala_klaim_memori = _ekstensi_gejala._gejala_klaim_memori
_gejala_klaim_tutur = _ekstensi_gejala._gejala_klaim_tutur
_gejala_nama_sementara = _ekstensi_gejala._gejala_nama_sementara
_gejala_pipeline = _ekstensi_gejala._gejala_pipeline
_gejala_terapkan = _ekstensi_gejala._gejala_terapkan
_gejala_klaim_identitas = _ekstensi_gejala._gejala_klaim_identitas
_gejala_ignite = _ekstensi_gejala._gejala_ignite
_gejala_proses_tertunda = _ekstensi_gejala._gejala_proses_tertunda
_gejala_tick = _ekstensi_gejala._gejala_tick
enable_gejala = _ekstensi_gejala.enable_gejala
gejala_state = _ekstensi_gejala.gejala_state
_gejala_hud_state = _ekstensi_gejala._gejala_hud_state

_pasang_ekstensi(Naluri, nama="gejala")

def demo_gejala() -> Dict[str, Any]:
    """Demo SISTEM I: gejala murni yang tak bisa diklaim → kategori baru."""
    from pycos.inti.demo.skenario import demo_gejala as jalankan
    return jalankan()




from pycos.inti.ekstensi import invensi as _ekstensi_invensi
_invensi_dari = _ekstensi_invensi._invensi_dari
_invensi_aktif = _ekstensi_invensi._invensi_aktif
_inv_teks = _ekstensi_invensi._inv_teks
_invensi_digest = _ekstensi_invensi._invensi_digest
enable_invensi = _ekstensi_invensi.enable_invensi
lahirkan_struktur = _ekstensi_invensi.lahirkan_struktur
kristalkan_invensi = _ekstensi_invensi.kristalkan_invensi
invensi_state = _ekstensi_invensi.invensi_state
_naluri_invensi_step = _ekstensi_invensi._naluri_invensi_step
_invensi_tick = _ekstensi_invensi._invensi_tick
_pasang_invensi_tick = _ekstensi_invensi._pasang_invensi_tick

_pasang_ekstensi(Naluri, nama="invensi")

def demo_invensi() -> Dict[str, Any]:
    """Demo pelita STRUKTUR BARU: hipotesis/rencana/kategori/tujuan endogen."""
    from pycos.inti.demo.skenario import demo_invensi as jalankan
    return jalankan()




from pycos.inti.ekstensi import kausal as _ekstensi_kausal
_kausal_dari = _ekstensi_kausal._kausal_dari
_kausal_aktif = _ekstensi_kausal._kausal_aktif
pelajari_kausal = _ekstensi_kausal.pelajari_kausal
jelaskan_kenapa = _ekstensi_kausal.jelaskan_kenapa
counterfactual_kausal = _ekstensi_kausal.counterfactual_kausal
blame_kausal = _ekstensi_kausal.blame_kausal
mekanisme_kausal = _ekstensi_kausal.mekanisme_kausal
kausal_state = _ekstensi_kausal.kausal_state
enable_kausal = _ekstensi_kausal.enable_kausal
_kausal_step = _ekstensi_kausal._kausal_step
_kausal_tick = _ekstensi_kausal._kausal_tick
_pasang_kausal_tick = _ekstensi_kausal._pasang_kausal_tick

_pasang_ekstensi(Naluri, nama="kausal")

def demo_kausal() -> Dict[str, Any]:
    """Demo poin 1: model kausal — menjelaskan kenapa, counterfactual, blame."""
    from pycos.inti.demo.skenario import demo_kausal as jalankan
    return jalankan()




from pycos.inti.ekstensi import perencana as _ekstensi_perencana
_perencana_dari = _ekstensi_perencana._perencana_dari
_perencana_aktif = _ekstensi_perencana._perencana_aktif
_fakta_sekarang = _ekstensi_perencana._fakta_sekarang
rencanakan = _ekstensi_perencana.rencanakan
rencana_state = _ekstensi_perencana.rencana_state
enable_perencana = _ekstensi_perencana.enable_perencana

_pasang_ekstensi(Naluri, nama="perencana")

def demo_perencana() -> Dict[str, Any]:
    """Demo poin 2: perencanaan multi-tingkat + meta-planning."""
    from pycos.inti.demo.skenario import demo_perencana as jalankan
    return jalankan()




from pycos.inti.ekstensi import pelindung as _ekstensi_pelindung

_PELINDUNG_WATAK = _ekstensi_pelindung._PELINDUNG_WATAK
_PELINDUNG_ALTERNATIF_ACT = _ekstensi_pelindung._PELINDUNG_ALTERNATIF_ACT
_PELINDUNG_UJIAN = _ekstensi_pelindung._PELINDUNG_UJIAN
_PELINDUNG_META_RE = _ekstensi_pelindung._PELINDUNG_META_RE
_PELINDUNG_META_KETAT_RE = _ekstensi_pelindung._PELINDUNG_META_KETAT_RE
_PELINDUNG_ANGKA_RE = _ekstensi_pelindung._PELINDUNG_ANGKA_RE
_pelindung_stabil = _ekstensi_pelindung._pelindung_stabil
_pelindung_kata = _ekstensi_pelindung._pelindung_kata
_pelindung_bentuk = _ekstensi_pelindung._pelindung_bentuk
_pelindung_jaccard = _ekstensi_pelindung._pelindung_jaccard
_pelindung_pilih_stabil = _ekstensi_pelindung._pelindung_pilih_stabil
_pelindung_dari = _ekstensi_pelindung._pelindung_dari
_pelindung_aktif = _ekstensi_pelindung._pelindung_aktif
_pelindung_init = _ekstensi_pelindung._pelindung_init
watak_kegagalan = _ekstensi_pelindung.watak_kegagalan
pidato_gagal = _ekstensi_pelindung.pidato_gagal
_pelindung_act_hint = _ekstensi_pelindung._pelindung_act_hint
_pelindung_reset_flag = _ekstensi_pelindung._pelindung_reset_flag
_BUFFER_MANUSIAWI = _ekstensi_pelindung._BUFFER_MANUSIAWI
buffer_manusiawi = _ekstensi_pelindung.buffer_manusiawi
tandai_lupa = _ekstensi_pelindung.tandai_lupa
tandai_kontradiksi = _ekstensi_pelindung.tandai_kontradiksi
tandai_tidak_paham = _ekstensi_pelindung.tandai_tidak_paham
_pelindung_buffer_jenis = _ekstensi_pelindung._pelindung_buffer_jenis
jeda_bermakna = _ekstensi_pelindung.jeda_bermakna
_pelindung_kebaruan_input = _ekstensi_pelindung._pelindung_kebaruan_input
eskalasi_variasi = _ekstensi_pelindung.eskalasi_variasi
_pengakuan_repetisi = _ekstensi_pelindung._pengakuan_repetisi
_ganti_kata = _ekstensi_pelindung._ganti_kata
_ganti_struktur = _ekstensi_pelindung._ganti_struktur
_pengakuan_istirahat = _ekstensi_pelindung._pengakuan_istirahat
saring_meta = _ekstensi_pelindung.saring_meta
_kuantor_angka = _ekstensi_pelindung._kuantor_angka
serap_adversarial = _ekstensi_pelindung.serap_adversarial
degradasi_state = _ekstensi_pelindung.degradasi_state
_pelindung_tanda_lelah = _ekstensi_pelindung._pelindung_tanda_lelah
keragaman_tanda = _ekstensi_pelindung.keragaman_tanda
dorong_geser = _ekstensi_pelindung.dorong_geser
keragaman_scene = _ekstensi_pelindung.keragaman_scene
MonitorIntegritas = _ekstensi_pelindung.MonitorIntegritas
_pelindung_pilih_act = _ekstensi_pelindung._pelindung_pilih_act
_pelindung_ucap = _ekstensi_pelindung._pelindung_ucap
_pelindung_entry = _ekstensi_pelindung._pelindung_entry
_penahanan_ucap = _ekstensi_pelindung._penahanan_ucap
_audisi_diri_ucap = _ekstensi_pelindung._audisi_diri_ucap
_pelindung_dengar = _ekstensi_pelindung._pelindung_dengar
monitor_integritas = _ekstensi_pelindung.monitor_integritas
enable_pelindung = _ekstensi_pelindung.enable_pelindung
pelindung_state = _ekstensi_pelindung.pelindung_state
_pelindung_to_dict = _ekstensi_pelindung._pelindung_to_dict
_pelindung_from_dict = _ekstensi_pelindung._pelindung_from_dict
monitor_scene = _ekstensi_pelindung.monitor_scene
keragaman = _ekstensi_pelindung.keragaman
_pelindung_tick_all = _ekstensi_pelindung._pelindung_tick_all

_pasang_ekstensi(Naluri, nama="pelindung")

def demo_pelindung() -> Dict[str, Any]:
    """Demo SISTEM II: sepuluh mekanisme pelindung ilusi."""
    from pycos.inti.demo.skenario import demo_pelindung as jalankan
    return jalankan()




# ---------------------------------------------------------------------
# View reflektif ketidaktahuan (pure read) — integrasi hanya di pemanggil.
# ---------------------------------------------------------------------
from pycos.inti.ekstensi import ketidaktahuan as _ekstensi_kt
_kt_view = _ekstensi_kt._kt_view
if _kt_view is not None:
    _kt_batas_pengetahuan = _ekstensi_kt._kt_batas_pengetahuan
    _kt_sikap_ketidaktahuan = _ekstensi_kt._kt_sikap_ketidaktahuan
    _kt_context_item = _ekstensi_kt._kt_context_item
    _kt_kesadaran_candidates = _ekstensi_kt._kt_kesadaran_candidates
    _kt_presentasi_skor = _ekstensi_kt._kt_presentasi_skor
    _kt_tick_doubt = _ekstensi_kt._kt_tick_doubt
_pasang_ekstensi(Naluri, nama="ketidaktahuan")

from pycos.inti.ekstensi import persistensi as _ekstensi_persistensi
_naluri_profil_snapshot = _ekstensi_persistensi._naluri_profil_snapshot
_pasang_ekstensi(Naluri, nama="persistensi")


if __name__ == "__main__":
    from pycos.inti.demo import jalankan
    jalankan()
