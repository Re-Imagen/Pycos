"""Mesin motivasi Naluri; patch dan ekspor publik dikelola facade naluri.

Modul implementasi ini bukan entry point konstruksi tanpa bootstrap; gunakan
pycos.inti.naluri atau facade paket untuk memperoleh kelas yang telah dipatch.
"""
from __future__ import annotations
import copy
import json
import math
import random
import re
import time
from typing import Any, Callable, Dict, Iterable, List, Mapping, Optional, Tuple, TYPE_CHECKING
from pycos.dukungan import diagnostik as _diag
from pycos.dukungan.batas_memori import batas as _batas_memori, pangkas as _pangkas_memori
from pycos.dukungan.numerik import float_hingga, jepit, jepit_01, jepit_drive
from pycos.inti.keadaan import Goal, Mood
from pycos.inti.kesadaran import Kesadaran
from pycos.inti.presentasi import PRESENTASI_DEFAULTS, Presentasi
from pycos.inti.ritual import Ritual

if TYPE_CHECKING:
    from pycos.inti.naluri import CalibrationReport

from pycos.inti._konfigurasi import (DEFAULTS, DRIVES, DRIVE_ATTENTION, DRIVE_NEUROMOD, EMOSI, EMOSI_ALIASES, EMOSI_HUD_THRESHOLD, EMOSI_LABELS, EMOSI_PERSEPSI, GOAL_TEMPLATES, HUD_DRIVE_INTENT, HUD_MOOD_LABELS, KESADARAN_DEFAULTS, LEXICON, LEXICON_PACKS, LOD_ALIASES, LOD_DIVISOR_FACTOR, LOD_MODES, PERSONALITIES, PERSONALITY_ALIASES, SLEEP_MODES, SLEEP_MODE_ALIASES, STAGE_WEIGHTS, TAG_LEXICON, _nilai_per_drive, _periksa_kunci_drive)

class Naluri:
    """Homeostat enam drive; jantung motivasi Samre."""

    def __init__(self,
                 weights: Optional[Dict[str, float]] = None,
                 initial_levels: Optional[Dict[str, float]] = None,
                 params: Optional[Dict[str, Any]] = None,
                 stage: str = "dewasa",
                 rng_seed: Optional[int] = None,
                 name: Optional[str] = None,
                 personality: Optional[str] = None,
                 lexicon: Optional[Dict[str, Dict[str, float]]] = None,
                 tag_lexicon: Optional[Dict[str, Dict[str, float]]] = None,
                 lod: Optional[str] = None,
                 validate_params: bool = False):
        """Bangun NPC; validate_params memeriksa input params secara opt-in."""
        from pycos.inti.naluri import Nurani
        if not isinstance(validate_params, bool):
            raise ValueError("validate_params harus bool")
        if validate_params:
            from pycos.dukungan.parameter import periksa_params
            periksa_params(params)
        # Identitas NPC (fix konteks: modul ini dipakai untuk satu/banyak NPC).
        self.name: str = "" if name is None else str(name)
        self.stage = stage if stage in STAGE_WEIGHTS else "dewasa"
        self.weights = dict(STAGE_WEIGHTS[self.stage])
        if weights:
            _periksa_kunci_drive(weights, "weights")
            self.weights.update({k: float_hingga(v, "weights[{}]".format(k))
                                 for k, v in weights.items()})

        # Level awal divalidasi di batas masuk: kunci salah ketik dulu diabaikan
        # diam-diam, nilai NaN/luar rentang dulu lolos dan merusak simulasi.
        self.levels: Dict[str, float] = {d: 0.0 for d in DRIVES}
        if initial_levels:
            _periksa_kunci_drive(initial_levels, "initial_levels")
            for k, v in initial_levels.items():
                nilai = float_hingga(v, "initial_levels[{}]".format(k))
                if not -1.0 <= nilai <= 1.0:
                    raise ValueError(
                        "initial_levels[{}] = {} di luar rentang [-1, 1]"
                        .format(k, nilai))
                self.levels[k] = nilai

        # WATAK: deep-copy — DEFAULTS memuat dict bersarang (per-drive);
        # tanpa copy, mutasi satu NPC akan membocor ke konstanta modul.
        self.params: Dict[str, Any] = copy.deepcopy(DEFAULTS)
        if params:
            self.params.update(copy.deepcopy(params))

        self.urgency: Dict[str, float] = {d: 0.0 for d in DRIVES}
        self.deficit_ticks: Dict[str, int] = {d: 0 for d in DRIVES}
        self.goals: List[Goal] = []
        self.tick_count: int = 0
        # Jam objektif tetap `tick_count`; jam pengalaman berintegrasi dengan
        # keadaan mental. JEJAK menyimpan cap subjektif ini per episode.
        self.subjective_tick_count: float = 0.0
        self._vacant: bool = False
        self.tick_history: List[Dict[str, Any]] = []
        # Working memory: stimulus yang lolos atensi, berumur pendek.
        self.context_aktif: List[Dict[str, Any]] = []
        self._context_repeat: Dict[str, Dict[str, Any]] = {}
        # Eligibility trace: beberapa aksi dapat menerima kredit tertunda.
        self._eligibility_traces: List[Dict[str, Any]] = []
        self._action_values: Dict[str, Dict[str, Any]] = {}
        self._last_credit_assignments: List[Dict[str, Any]] = []
        # Jejak perubahan drive eksplisit (dengan alasan) - terbatas.
        self.delta_log: List[Dict[str, Any]] = []
        self._DELTA_LOG_MAX: int = 512
        self.actions_taken: int = 0
        self.slept_count: int = 0
        self.total_sleep_seconds: float = 0.0
        self._last_sleep_tick: int = -10_000  # refraktori
        # Siklus sirkadian terakhir tempat tidur terjadwal terjadi (fix #4):
        # mencegah NPC tidur berulang kali pada malam yang sama.
        self._slept_cycle: int = -1

        # Kalibrator — EMA kesalahan prediksi Imagination (dengan lantai derau).
        self._calibration_ema: float = 0.0
        self._calibration_samples: int = 0
        self._unverified_predictions: int = 0
        self._prediction_log: List[Dict[str, Any]] = []
        # Pasangan (prediksi, realita) mentah untuk estimate_scale().
        self._pred_pairs: List[Tuple[float, float]] = []

        # Skala adaptif (penyetara utilitas simulasi → reward dunia).
        self._scale: float = float(self.params["scale_initial"])

        # RNG lokal (untuk mimpi/pemilihan template); stdlib saja.
        self._rng = random.Random(rng_seed)
        self.rng_seed = rng_seed
        # DETERMINISTIC REPLAY: log event + snapshot awal agar run bisa diputar
        # ulang persis (debugging). Diaktifkan lewat enable_replay().
        self._replay_enabled: bool = False
        self._event_log: List[Dict[str, Any]] = []
        self._replay_initial: Optional[Dict[str, Any]] = None

        # Lexicon — bisa di-extend via add_lexicon() atau diganti total via
        # set_lexicon()/argumen konstruktor (fix #5: bukan lagi konstanta
        # modul Indonesia-only; mapping apa pun bisa di-inject per NPC).
        self.lexicon = ({str(w).lower(): dict(v) for w, v in lexicon.items()}
                        if lexicon is not None
                        else {w: dict(v) for w, v in LEXICON.items()})
        self.tag_lexicon = ({str(t): dict(v) for t, v in tag_lexicon.items()}
                            if tag_lexicon is not None
                            else {t: dict(v) for t, v in TAG_LEXICON.items()})
        # Indeks lexicon ter-compile (trie + rank) + cache hasil; dibangun
        # malas dan diinvalidasi setiap lexicon berubah (fix #6).
        self._trie: Optional[Dict[str, Any]] = None
        self._lexicon_rank: Dict[str, int] = {}
        self._tags_lower: List[Tuple[str, Dict[str, float]]] = []
        self._impact_cache: Dict[str, Dict[str, float]] = {}
        self._lexicon_dirty: bool = True

        # LOD / throttling (fix #2): "penuh" = tick penuh tiap panggilan,
        # "latar" = fisika tick sekali per `lod_divisor` panggilan (kompensasi
        # langkah), "beku" = tidak ada pembaruan (event di-buffer).
        self.lod_mode: str = "penuh"
        self.lod_divisor: int = max(1, int(self.params.get("lod_divisor", 10)))
        self._lod_accum: int = 0
        self._event_buffer: List[Dict[str, Any]] = []
        self._last_memory_compaction: Dict[str, Any] = {}

        # Preset kepribadian bernama (fix #3).
        self.personality_name: Optional[str] = None
        self._personality_blend: float = 1.0
        # WATAK: kunci `params` yang pernah disetel preset/set_watak (agar
        # bisa dikembalikan ke default saat preset diganti) + penanda apakah
        # backstory ("lahir") sudah di-seed (tidak boleh diulang set_stage).
        self._watak_keys: List[str] = []
        self._lahir_diterapkan: bool = False
        # Label HUD per-instans (fix #5/#7): bisa diganti per bahasa/NPC.
        self.hud_intents: Dict[str, str] = dict(HUD_DRIVE_INTENT)
        self.hud_moods: Dict[str, str] = dict(HUD_MOOD_LABELS)
        self.hud_emosi: Dict[str, str] = dict(EMOSI_LABELS["id"])

        # ------------------------------------------------------------------
        # EMPATI — keadaan emosi diskret (mati bawaan via enable_emosi).
        # `emosi[e]` = intensitas [0..1]; `_emosi_val_prev` = valensi mentah
        # tick fisika sebelumnya untuk apresiasi Δ; `_emosi_log` = jejak
        # terbatas "mengapa emosi ini muncul" (untuk debug/narasi).
        # ------------------------------------------------------------------
        self.emosi: Dict[str, float] = {e: 0.0 for e in EMOSI}
        self._emosi_val_prev: Optional[float] = None
        self._emosi_keamanan_prev: Optional[float] = None
        self._emosi_ingin_prev: Optional[float] = None
        self._emosi_log: List[Dict[str, Any]] = []
        self._EMOSI_LOG_MAX: int = 64
        self._coping_focus: Optional[Dict[str, Any]] = None

        # SELF-MODEL BOLEH SALAH: bukan galat interoseptif NURANI, melainkan
        # jarak antara perilaku yang diprediksi diri dan perilaku yang sungguh
        # keluar lewat presentasi. Nilai harus berulang sebelum menggoyahkan
        # identitas naratif.
        self._selisih_self: float = 0.0
        self._selisih_self_beruntun: int = 0
        self._selisih_self_log: List[Dict[str, Any]] = []
        self._disorientasi_identitas: float = 0.0
        self._interupsi_internal: List[Dict[str, Any]] = []

        # ------------------------------------------------------------------
        # PERSEPSI — lapisan rekonstruksi antara dunia dan drive (mati
        # bawaan via enable_perception). `_persepsi_log` = jejak peristiwa
        # perseptual mencolok (alarm palsu, subliminal kuat, atenuasi atensi)
        # untuk narasi/debug; `_persepsi_stim` = akumulator besaran stimulus
        # per tick untuk pembaruan level adaptasi (Helson) di NURANI.
        # ------------------------------------------------------------------
        self._persepsi_log: List[Dict[str, Any]] = []
        self._PERSEPSI_LOG_MAX: int = 64
        self.persepsi_alarm_palsu: int = 0
        self._persepsi_stim: Dict[str, float] = {d: 0.0 for d in DRIVES}

        # ------------------------------------------------------------------
        # NURANI (konsep 17) - lapisan meta-plastisitas di atas naluri.
        # Ia tidak memegang kendali: membaca state, belajar, lalu menulis bias
        # halus (prior afektif, setpoint, gema interosepsi, bonus kompromi,
        # ambang malam). Setiap pemakaian dikunci satu flag `enable_*`, dan
        # semuanya mati bawaan. Objeknya memakai dict `self.params` yang sama,
        # sehingga perubahan flag lewat enable_nurani()/orkestra langsung
        # berlaku tanpa perlu membuat ulang lapisan ini.
        # ------------------------------------------------------------------
        self.nurani = (None if Nurani is None
                       else Nurani(drives=DRIVES, params=self.params,
                                   rng_seed=(None if rng_seed is None else
                                             (int(rng_seed) ^ 0x4E55) & 0x7FFFFFFF)))

        # KESADARAN: panggung kesadaran naratif di atas NURANI.
        # Master flag `enable_kesadaran` mati bawaan → perilaku lama persis
        # tidak berubah; saat aktif, tiap tick menjalankan kompetisi atensi,
        # ignition, monolog batin, agensi, interosepsi afektif, monitoring
        # realitas, kognisi sosial, pragmatik, bias, nilai, mortalitas, mimpi,
        # dan audisi-diri segera setelah tuturan.
        self.kesadaran = Kesadaran(self, self.params)

        # PRESENTASI (lapisan penyajian "Pycos"): menerjemahkan seluruh data
        # internal (drive, emosi, introspeksi, kesadaran, relasi, nilai,
        # mortalitas, mimpi) menjadi perilaku yang dapat diamati — dialog
        # natural, ekspresi, tatapan, postur, napas, gestur, prosodi, idle.
        # Master flag `enable_presentasi` mati bawaan → perilaku lama persis.
        # `self.jejak` (opsional) diisi lewat attach_jejak() agar memori
        # autobiografis JEJAK ikut dikisahkan dalam dialog.
        self.jejak: Any = None
        self.presentasi = Presentasi(self, self.params)

        # RITUAL (perilaku "utilitas nol"): kebiasaan/keanehan yang dipicu
        # kondisi spesifik, bukan defisit drive — membunuh kesan mesin.
        # Master flag `enable_ritual` mati bawaan.
        self.ritual = Ritual(self, self.params)

        # MEMOIZATION (fix kinerja): cache mood per-signature & prior afektif
        # dengan TTL tick, agar pemanggilan berulang (presentasi/kesadaran/
        # choose_action) tidak menghitung ulang.
        self._mood_cache: Optional[Tuple[Any, Any]] = None
        self._anticipate_cache: Dict[str, Tuple[int, Dict[str, float]]] = {}
        self._ANTICIPATE_TTL: int = 8

        # PROFILER bawaan (gated): akumulasi waktu per-seksi tanpa dependensi.
        self._profiling: bool = False
        self._profile: Dict[str, Dict[str, float]] = {}
        self._profile_ticks: int = 0
        # LIGHT/HEAVY split: saat True, lapisan berat (introspeksi/kesadaran/
        # presentasi/ritual) dilewati walau LOD penuh — untuk tick massal.
        self._force_light: bool = False

        # WATAK: preset diterapkan SETELAH NURANI ada — backstory ("lahir")
        # harus men-seed setpoint/memori afektif memakai clamp watak aktif.
        if personality:
            self.set_personality_preset(personality)
        # LOD diatur setelah NURANI + backstory tersedia, sehingga kompresi
        # otomatis aman dan dapat memangkas state awal bila diperlukan.
        if lod:
            self.set_lod(lod)


    # -------------------- tahap maturasi --------------------
    def set_stage(self, stage: str) -> None:
        if stage not in STAGE_WEIGHTS:
            raise ValueError(f"stage tidak dikenal: {stage}")
        self.stage = stage
        self.weights = dict(STAGE_WEIGHTS[stage])
        # Preset kepribadian bertahan melewati perubahan tahap (fix #3):
        # tanpa ini, maturasi otomatis akan menghapus bobot kustom NPC.
        # `terapkan_lahir=False`: backstory adalah kondisi KELAHIRAN — bila
        # diulang tiap maturasi (tick 400/1500), level/setpoint NPC akan
        # di-reset ke masa kecilnya. Watak (params) tetap diterapkan ulang.
        if self.personality_name:
            self.set_personality_preset(self.personality_name,
                                        blend=self._personality_blend,
                                        terapkan_lahir=False)

    def advance_stage_by_ticks(self) -> str:
        """Auto-pilih tahap berdasarkan tick_count (anak<400, remaja<1500, dewasa)."""
        t = self.tick_count
        if t < 400:
            stage = "anak"
        elif t < 1500:
            stage = "remaja"
        else:
            stage = "dewasa"
        if stage != self.stage:
            self.set_stage(stage)
        return stage

    def subjective_time_profile(self) -> Dict[str, Any]:
        """Laju waktu yang dialami, terpisah dari jam objektif.

        Arousal/ancaman meregangkan momen, duka membuatnya menetap, sedangkan
        kebosanan dan kegembiraan mengompresi pengalaman. `clock_rate` mengatur
        penuaan subjektif; `episode_scale` mengubah half-life struktural saat
        momen itu dikodekan. Keduanya sengaja bukan importance.
        """
        em = getattr(self, "emosi", {}) or {}
        levels = getattr(self, "levels", {}) or {}
        try:
            arousal = jepit_01(float(self.mood().arousal))
        except Exception as _galat_diagnostik_116:
            _diag.catat('naluri.Naluri.subjective_time_profile', "galat pada jalur fallback", galat=_galat_diagnostik_116, jalur=116)
            arousal = 0.0
        fear = jepit_01(float(em.get("takut", 0.0) or 0.0))
        anger = jepit_01(float(em.get("marah", 0.0) or 0.0))
        joy = jepit_01(float(em.get("senang", 0.0) or 0.0))
        sadness = jepit_01(float(em.get("sedih", 0.0) or 0.0))
        boredom = jepit_01(max(
            -float(levels.get("keingintahuan", 0.0) or 0.0),
            float(em.get("bosan", 0.0) or 0.0)))
        # Kehilangan/duka juga mempertahankan momen meski emosi sedih belum
        # dominan lagi; residu tetap bagian dari kondisi yang dialami tubuh.
        ks = getattr(self, "kesadaran", None)
        try:
            grief = max((float(x.get("intensity", 0.0) or 0.0)
                         for x in (getattr(ks, "grief", {}) or {}).values()),
                        default=0.0)
        except Exception as _galat_diagnostik_117:
            _diag.catat('naluri.Naluri.subjective_time_profile', "galat pada jalur fallback", galat=_galat_diagnostik_117, jalur=117)
            grief = 0.0
        sadness = max(sadness, min(1.0, grief))
        episode_scale = jepit(1.0 + 1.10 * arousal * (1.0 - 0.85 * joy)
            + 0.45 * fear + 0.35 * anger + 0.60 * sadness
            - 0.90 * boredom - 0.90 * joy, 0.20, 3.50)
        clock_rate = jepit(1.0 + 0.95 * boredom + 0.55 * joy
            - 0.45 * arousal - 0.35 * fear - 0.55 * sadness, 0.20, 2.80)
        if episode_scale >= 1.20:
            rasa = "memanjang"
        elif episode_scale <= 0.80:
            rasa = "melesat"
        else:
            rasa = "netral"
        return {"clock_rate": clock_rate,
                "episode_scale": episode_scale,
                "arousal": arousal, "takut": fear, "marah": anger,
                "senang": joy, "sedih": sadness, "bosan": boredom,
                "rasa": rasa}

    def subjective_time_state(self) -> Dict[str, Any]:
        return {"tick_objektif": int(self.tick_count),
                "tick_subjektif": round(float(self.subjective_tick_count), 4),
                **self.subjective_time_profile()}

    def _advance_subjective_time(self, steps: float = 1.0) -> float:
        profile = self.subjective_time_profile()
        dt = max(0.0, float(steps))
        self.subjective_tick_count = max(0.0,
            float(self.subjective_tick_count) + dt * profile["clock_rate"])
        return float(self.subjective_tick_count)

    # -------------------- waktu & peristiwa --------------------
    def tick(self, events: Optional[Iterable[Dict[str, Any]]] = None,
             action_cost: bool = False) -> None:
        """Kemajukan waktu satu tick (menghormati mode LOD).

        events: iterable dari {"drive": str, "delta": float, "reason": str}
        action_cost: True jika tick ini juga mengambil aksi (biaya energi tambahan).

        LOD (fix #2) — untuk NPC yang jauh dari pemain:
          * "penuh"  : fisika tick penuh tiap panggilan (perilaku lama).
          * "latar"  : jam (tick_count) tetap berjalan, tetapi fisika berat
                       (peluruhan, urgensi, goal, NURANI, history) hanya
                       dijalankan sekali per `lod_divisor` panggilan dengan
                       kompensasi `steps` (default 10x lebih hemat). Events
                       selama tick yang dilewati di-buffer lalu diterapkan
                       sekaligus, jadi tidak ada peristiwa yang hilang.
          * "beku"   : tidak ada pembaruan sama sekali; events tetap di-buffer
                       (maks 64) dan diterapkan lagi saat LOD naik.
        Naikkan LOD ke "penuh" saat pemain berinteraksi; `action_cost=True`
        pada mode "latar" juga memaksa tick penuh segera.
        """
        vacancy_aktif = getattr(self, "_vacancy_aktif", None)
        vacancy_lewat = getattr(self, "_vacancy_lewat", None)
        if callable(vacancy_aktif) and vacancy_aktif():
            # Vacancy menolak events dan action_cost alih-alih membuffer mereka.
            # Waktu tetap lewat, tetapi tak satu pun jalur pemrosesan/log hidup.
            self.tick_count += 1
            if callable(vacancy_lewat):
                vacancy_lewat(1.0)
            return
        if events is not None and self._replay_enabled:
            try:
                events = list(events)
            except TypeError:
                events = [events]
            self._event_log.append({
                "tick": self.tick_count + 1,
                "events": [dict(e) for e in events if isinstance(e, Mapping)],
                "action_cost": bool(action_cost)})
            _pangkas_memori(self._event_log, "replay_log")
        self.tick_count += 1
        self._advance_subjective_time(1.0)
        mode = self.lod_mode
        if mode == "beku":
            if events:
                self._buffer_events(events)
            return
        if mode in ("latar", "abstrak") and not action_cost:
            if events:
                self._buffer_events(events)
            self._lod_accum += 1
            # "abstrak" lebih hemat: divisor dikali LOD_DIVISOR_FACTOR.
            ambang = self.lod_divisor * LOD_DIVISOR_FACTOR.get(mode, 1)
            if self._lod_accum < ambang:
                return
            steps = self._lod_accum
            self._lod_accum = 0
            self._physics(steps=steps, events=None, action_cost=False)
            return
        # "penuh"/"ringan", atau latar/abstrak dengan aksi (interaksi responsif)
        if mode in ("latar", "abstrak"):
            self._lod_accum = 0
        if self._profiling:
            t0 = time.perf_counter()
            self._physics(steps=1, events=events, action_cost=action_cost)
            self._profile_add("Naluri._physics", time.perf_counter() - t0)
            self._profile_ticks += 1
        else:
            self._physics(steps=1, events=events, action_cost=action_cost)

    def _buffer_events(self, events: Iterable[Dict[str, Any]]) -> None:
        """Simpan events LOD yang dilewati, dibatasi BATAS[event_buffer]."""
        for ev in events:
            if isinstance(ev, dict):
                self._event_buffer.append(dict(ev))
        _pangkas_memori(self._event_buffer, "event_buffer")

    def _physics(self, steps: int = 1,
                 events: Optional[Iterable[Dict[str, Any]]] = None,
                 action_cost: bool = False) -> None:
        """Inti fisika tick; `steps` > 1 mengompensasi tick LOD yang dilewati
        (peluruhan eksponensial dipangkatkan, suku linear dikalikan)."""
        steps = max(1, int(steps))
        vacancy_aktif = getattr(self, "_vacancy_aktif", None)
        vacancy_lewat = getattr(self, "_vacancy_lewat", None)
        if callable(vacancy_aktif) and vacancy_aktif():
            if callable(vacancy_lewat):
                vacancy_lewat(float(steps))
            return
        # EMPATI: peluruhan emosi LOD-aware di awal; potret "keadaan sebelum"
        # diambil SETELAH advance_stage_by_ticks() (di bawah) agar apresiasi Δ
        # tidak tercemar pergantian bobot weights saat tahap maturasi berubah
        # (bug-fix debugging: dv palsu pada tick pertama & tick transisi tahap).
        emosi_aktif = bool(self.params.get("enable_emosi", False))
        fokus = self._coping_focus if self.params.get("enable_coping", False) else None
        decay_gain = (float(fokus.get("emotion_decay_multiplier", 1.0))
                      if fokus and int(fokus.get("remaining", 0)) > 0 else 1.0)
        if emosi_aktif:
            self._emosi_peluruh(steps, multiplier=decay_gain)
        self._advance_working_memory(steps)
        self._decay_eligibility_traces(steps)
        self._advance_coping_focus(steps)
        decay = self.params["decay_per_tick"]
        # peluruhan baseline menuju 0 (homeostatis ringan)
        factor = (1.0 - decay) ** steps
        for d in DRIVES:
            self.levels[d] *= factor
        # biaya energi komputasi
        self.levels["energi"] -= self.params["energi_cost_tick"] * steps
        if action_cost:
            self.levels["energi"] -= self.params["energi_cost_action"]
            self.actions_taken += 1
        else:
            # istirahat ringan memulihkan energi
            self.levels["energi"] += self.params["energi_recover_rest"] * steps

        # kebosanan menggerogoti keingintahuan (terutama saat aksi terasa repetitif)
        self.levels["keingintahuan"] -= (0.008 if action_cost else 0.003) * steps

        # isolasi ringan menggerus afiliasi
        self.levels["afiliasi"] -= 0.003 * steps

        # semua drive non-energi perlahan menurun jika tidak diurus (merasa lapar)
        for d in ("keamanan", "penguasaan", "koherensi"):
            self.levels[d] -= 0.002 * steps

        # terlalu nyaman di semua drive → keingintahuan turun pelan (homeostasis)
        if all(self.levels[d] > 0.15 for d in DRIVES):
            self.levels["keingintahuan"] -= 0.005 * steps

        # maturasi otomatis
        self.advance_stage_by_ticks()

        # EMPATI: potret keadaan SEBELUM peristiwa (bobot sudah final tick ini)
        if emosi_aktif:
            val_sebelum = self._valensi_mentah()
            keam_sebelum = max(0.0, -self.levels["keamanan"])
            ingin_sebelum = self.levels["keingintahuan"]

        # proses peristiwa: buffer LOD lebih dulu (kronologis), lalu events baru
        if self._event_buffer:
            buffered, self._event_buffer = self._event_buffer, []
            self.apply_events(buffered)
        if events:
            self.apply_events(events)

        # Jam internal bergerak dalam pecahan tick. Interupsi diproses SEKARANG,
        # bukan dimasukkan event buffer untuk tick berikutnya.
        interupsi_awal: List[Dict[str, Any]] = []
        checkpoint = getattr(self, "_detak_checkpoint", None)
        if callable(checkpoint):
            try:
                interupsi_awal = checkpoint(0.34 * steps, "pasca_event")
            except Exception as _galat_diagnostik_118:
                _diag.catat('naluri.Naluri._physics', "galat pada jalur fallback", galat=_galat_diagnostik_118, jalur=118)
                interupsi_awal = []
        # Mual yang jatuh tempo membuat fase reflektif fisika ini terlewati.
        lewati_introspeksi = any(x.get("proses") == "mual"
                                for x in interupsi_awal)

        # PERSEPSI (gated): alarm palsu endogen (criterion negatif + derau)
        # dan pembaruan level adaptasi saluran dari stimulus tick ini.
        if self._persepsi_aktif():
            self._persepsi_spontan(steps)
            if self.nurani is not None:
                self.nurani.update_adaptasi(self._persepsi_stim, tick=self.tick_count)
            self._persepsi_stim = {d: 0.0 for d in DRIVES}

        # INTROSPEKSI DIRI (gated): self-monitoring loop (insula + ACC + PFC)
        # Fisiologi: tiap tick, anterior insula memperkirakan keadaan tubuh (model_diri)
        # dengan derau, ACC memonitor konflik, PFC mengevaluasi confidence.
        # Ini adalah object-level vs meta-level (Nelson & Narens 1990).
        if (self._lod_heavy() and self._introspeksi_aktif()
                and not lewati_introspeksi):
            konflik_info = None
            if self.nurani.enabled("conflict_resolution") and len(self.goals) >= 2:
                try:
                    konflik_info = self.nurani.detect_conflict(self.goals, [])
                except Exception as _galat_diagnostik_119:
                    _diag.catat('naluri.Naluri._physics', "galat pada jalur fallback", galat=_galat_diagnostik_119, jalur=119)
                    konflik_info = None
            try:
                self.nurani.update_introspection(
                    levels=self.levels,
                    urgency=self.urgency,
                    valence=self.mood().valence,
                    arousal=self.mood().arousal,
                    tick=self.tick_count,
                    konflik=konflik_info,
                    rng=self._rng
                )
            except Exception as _galat_diagnostik_120:
                _diag.catat('naluri.Naluri._physics', "galat pada jalur fallback", galat=_galat_diagnostik_120, jalur=120)
                pass
            # NURANI pilar H: kesadaran terasa — bentuk sensasi tubuh yang
            # dapat dilaporkan, lalu monolog batin berjalan secara berkala.
            if self.nurani.felt_consciousness():
                try:
                    self.nurani.update_felt(self.levels, self.urgency,
                                            self.mood().arousal, self.tick_count)
                    if (self.nurani._felt("inner_speech")
                            and self.tick_count - self.nurani._last_inner_speech_tick
                            >= int(self.nurani._p("inner_speech_period"))):
                        konteks = ""
                        if self.context_aktif:
                            konteks = str(max(self.context_aktif,
                                              key=lambda c: float(c.get("salience", 0.0)))
                                          .get("stimulus", ""))
                        self.nurani.inner_speech(konteks, self.tick_count)
                        self.nurani._last_inner_speech_tick = self.tick_count
                except Exception as _galat_diagnostik_121:
                    _diag.catat('naluri.Naluri._physics', "galat pada jalur fallback", galat=_galat_diagnostik_121, jalur=121)
                    pass

        # update defisit_ticks (berapa tick berturut drive defisit) dan urgensi
        dp = self.params["deadline_pressure"]
        # NURANI pilar C: setpoint bergerak & matriks interosepsi belajar,
        # diperbarui SEBELUM urgensi agar perhitungan urgensi memakai hasilnya.
        nur = self.nurani
        if nur is not None:
            nur.update_setpoints(self.levels)
            nur.update_interoception({d: max(0.0, -self.levels[d]) for d in DRIVES},
                                     self.tick_count)
        plastis = nur is not None and nur.enabled("plastic_setpoints")
        gema = nur is not None and nur.enabled("interoception")
        # Defisit diukur terhadap nol (jalur lama) atau terhadap setpoint
        # plastis (NURANI pilar C): di lingkungan ber-energi rendah organisme
        # menggeser ekspektasinya, bukan panik setiap kali turun di bawah nol.
        deficits: Dict[str, float] = {
            d: (nur.relative_deficit(d, self.levels[d]) if plastis
                else max(0.0, -self.levels[d])) for d in DRIVES
        }
        for d in DRIVES:
            deficit = deficits[d]  # defisit = 0 saat surplus
            if deficit > 0.05:
                self.deficit_ticks[d] = self.deficit_ticks.get(d, 0) + steps
            else:
                self.deficit_ticks[d] = 0
            # Tekanan deadline: urgensi = defisit × bobot × (1 + deficit_ticks/200)
            # (dp = 0.005 = 1/200 sehingga multiplier di bawah persis
            #  1 + deficit_ticks/200 seperti yang diklaim komentar ini.)
            deadline_mult = 1.0 + dp * self.deficit_ticks[d]  # =1+deficit_ticks/200
            raw = deficit * self.weights[d] * deadline_mult
            if gema:
                # NURANI pilar C: "gema interoseptif" -- defisit drive lain
                # menambah urgensi drive ini lewat korelasi yang TERPELAJARI.
                raw += nur.interoceptive_echo(deficits, d)
            # WATAK: alpha urgensi boleh per-drive — paranoid bereaksi cepat
            # pada ancaman ({"keamanan": 0.5}), pengrajin lambat goyah
            # ({"penguasaan": 0.15}); skalar lama tetap berlaku apa adanya.
            alpha = _nilai_per_drive(self.params, "urgency_alpha", d, 0.25)
            self.urgency[d] = (1 - alpha) * self.urgency[d] + alpha * raw
            self.urgency[d] = jepit(self.urgency[d], 0.0, 2.5)

        interupsi_tengah: List[Dict[str, Any]] = []
        if callable(checkpoint):
            try:
                interupsi_tengah = checkpoint(0.33 * steps, "pasca_urgensi")
            except Exception as _galat_diagnostik_122:
                _diag.catat('naluri.Naluri._physics', "galat pada jalur fallback", galat=_galat_diagnostik_122, jalur=122)
                interupsi_tengah = []

        # Mual yang datang persis di sini melewati refresh goal: keputusan
        # motivasional lama tertahan satu putaran tanpa pernah memilihnya.
        lewati_goal = any(x.get("proses") == "mual"
                          for x in interupsi_tengah)
        if not lewati_goal:
            self._rebuild_goals()

        # penuaan goal
        for g in self.goals:
            g.age += 1

        # clip drive
        for d in DRIVES:
            self.levels[d] = jepit_drive(self.levels[d])

        interupsi_akhir: List[Dict[str, Any]] = []
        if callable(checkpoint):
            try:
                interupsi_akhir = checkpoint(0.33 * steps, "pra_presentasi")
            except Exception as _galat_diagnostik_123:
                _diag.catat('naluri.Naluri._physics', "galat pada jalur fallback", galat=_galat_diagnostik_123, jalur=123)
                interupsi_akhir = []
        lewati_penyajian = any(x.get("proses") == "mual"
                               for x in interupsi_akhir)

        # EMPATI: apresiasi — emosi lahir dari PERUBAHAN keadaan drive tick ini
        if emosi_aktif:
            self._emosi_apresiasi(val_sebelum, keam_sebelum, ingin_sebelum)

        # KESADARAN (gated): setelah seluruh modul memperbarui state, jalankan
        # satu putaran kesadaran — seleksi atensi, ignition/broadcast, monolog
        # batin, rasa agensi, interosepsi afektif, monitoring realitas,
        # mortalitas, dan kontinuitas mimpi.
        if (self._lod_heavy() and self._kesadaran_aktif()
                and not lewati_penyajian):
            try:
                self.kesadaran.step(steps)
            except Exception as _galat_diagnostik_124:
                _diag.catat('naluri.Naluri._physics', "galat pada jalur fallback", galat=_galat_diagnostik_124, jalur=124)
                pass

        # PRESENTASI (gated): perbarui denyut mikro ekspresi (napas, kedip,
        # fidget, mikro-ekspresi) agar perilaku terlihat hidup antar-tick.
        if (self._lod_heavy() and self._presentasi_aktif()
                and not lewati_penyajian):
            try:
                self.presentasi.tick(steps)
            except Exception as _galat_diagnostik_125:
                _diag.catat('naluri.Naluri._physics', "galat pada jalur fallback", galat=_galat_diagnostik_125, jalur=125)
                pass
        if self._lod_heavy() and self._ritual_aktif():
            try:
                self.ritual.tick(steps)
            except Exception as _galat_diagnostik_126:
                _diag.catat('naluri.Naluri._physics', "galat pada jalur fallback", galat=_galat_diagnostik_126, jalur=126)
                pass

        # catat history (ringkas)
        if self.tick_count % 5 == 0:
            self.tick_history.append({
                "t": self.tick_count,
                "levels": dict(self.levels),
                "urgency": dict(self.urgency),
                "cal": self._calibration_ema,
            })
            _pangkas_memori(self.tick_history, "tick_history")

    # -------------------- kompresi memori / LOD --------------------
    def _buffer_memori(self):
        return {
            "tick_history": (self.tick_history, None),
            "delta_log": (self.delta_log, self._DELTA_LOG_MAX),
            "pred_pairs": (self._pred_pairs, None),
            "prediction_log": (self._prediction_log, None),
            "event_buffer": (self._event_buffer, None),
            "emosi_log": (self._emosi_log, self._EMOSI_LOG_MAX),
            "persepsi_log": (self._persepsi_log, self._PERSEPSI_LOG_MAX),
            "impact_cache": (self._impact_cache, None),
            "replay_log": (self._event_log, None),
        }

    def memori_state(self) -> Dict[str, Any]:
        """Audit buffer inti tanpa serialisasi/pemangkasan; bukan RAM total."""
        from pycos.dukungan.batas_memori import BATAS
        buffers = {}
        for key, (items, lokal) in self._buffer_memori().items():
            cap = _batas_memori(key, lokal)
            buffers[key] = {"entries": len(items), "limit": cap,
                            "policy_limit": BATAS[key], "local_limit": lokal,
                            "over_limit": len(items) > cap}
        return {"scope": "buffer_inti_naluri", "buffers": buffers,
                "total_entries": sum(v["entries"] for v in buffers.values())}

    def batasi_memori(self) -> Dict[str, Any]:
        """Terapkan kebijakan baru sekarang; seluruh batas diperiksa dahulu."""
        self.memori_state()
        for key, (items, lokal) in self._buffer_memori().items():
            if isinstance(items, dict):
                cap = _batas_memori(key, lokal)
                for k in list(items)[:max(0, len(items) - cap)]:
                    del items[k]
            else:
                _pangkas_memori(items, key, lokal)
        return self.memori_state()

    def kompres_memori(self, level: Any = "latar") -> Dict[str, Any]:
        """Kompres history/log dan memori afektif dengan diagnostik terukur.

        Profil ``latar`` memenuhi batas operasional 50 tick-history, 20
        prediksi, dan 100 asosiasi afektif terpenting. ``beku`` lebih agresif
        (25/10/50); ``ringan`` tersedia untuk kompresi manual yang lebih lunak.
        Alias Inggris dan level numerik 1–3 diterima. ``penuh`` adalah no-op.
        Pemilihan asosiasi afektif deterministik: importance, jumlah bukti,
        recency, lalu signature sebagai tie-breaker.
        """
        raw = str(level).lower().strip()
        aliases = {
            "1": "ringan", "light": "ringan", "soft": "ringan",
            "2": "latar", "background": "latar", "low": "latar",
            "3": "beku", "frozen": "beku", "agresif": "beku",
            "full": "penuh", "high": "penuh",
            "abstract": "abstrak", "coarse": "abstrak",
        }
        mode = aliases.get(raw, raw)
        profiles = {
            "ringan": (200, 100, 500),
            "latar": (50, 20, 100),
            "abstrak": (35, 15, 75),
            "beku": (25, 10, 50),
            "penuh": None,
        }
        if mode not in profiles:
            raise ValueError("level kompresi harus 'ringan', 'latar', 'beku', atau 'penuh'")
        sebelum_history = len(self.tick_history)
        sebelum_prediksi = len(self._prediction_log)
        nur = getattr(self, "nurani", None)
        affective = getattr(nur, "_affective", {}) if nur is not None else {}
        sebelum_afektif = len(affective)
        cache = getattr(nur, "_sig_cache", {}) if nur is not None else {}
        sebelum_cache = len(cache)
        limits = profiles[mode]
        cutoff_importance = None
        if limits is not None:
            history_cap, prediction_cap, affective_cap = limits
            self.tick_history = self.tick_history[-history_cap:] if history_cap else []
            self._prediction_log = self._prediction_log[-prediction_cap:] if prediction_cap else []
            if nur is not None and len(nur._affective) > affective_cap:
                ranked = sorted(
                    nur._affective.items(),
                    key=lambda kv: (
                        max(float(kv[1].get("importance", 0.0)),
                            max((abs(float(v)) for v in
                                 (kv[1].get("deltas", {}) or {}).values()),
                                default=0.0)),
                        int(kv[1].get("n", 0)),
                        int(kv[1].get("last_t", 0)),
                        -int(kv[0]),
                    ),
                    reverse=True,
                )
                keep = {sig for sig, _slot in ranked[:affective_cap]}
                cutoff_importance = min((
                    max(float(slot.get("importance", 0.0)),
                        max((abs(float(v)) for v in
                             (slot.get("deltas", {}) or {}).values()), default=0.0))
                    for sig, slot in ranked[:affective_cap]
                ), default=0.0)
                # Pertahankan urutan insertion state di antara slot terpilih.
                nur._affective = {sig: slot for sig, slot in nur._affective.items()
                                  if sig in keep}
                if hasattr(nur, "_sig_cache"):
                    nur._sig_cache.clear()
        else:
            history_cap = prediction_cap = affective_cap = None
        sesudah_afektif = (len(nur._affective) if nur is not None else 0)
        hasil = {
            "level": mode,
            "applied": limits is not None,
            "before": {"tick_history": sebelum_history,
                       "prediction_log": sebelum_prediksi,
                       "affective": sebelum_afektif,
                       "signature_cache": sebelum_cache},
            "after": {"tick_history": len(self.tick_history),
                      "prediction_log": len(self._prediction_log),
                      "affective": sesudah_afektif,
                      "signature_cache": (len(nur._sig_cache)
                                           if nur is not None else 0)},
            "removed": {"tick_history": sebelum_history - len(self.tick_history),
                        "prediction_log": sebelum_prediksi - len(self._prediction_log),
                        "affective": sebelum_afektif - sesudah_afektif,
                        "signature_cache": sebelum_cache - (len(nur._sig_cache)
                                           if nur is not None else 0)},
            "limits": {"tick_history": history_cap,
                       "prediction_log": prediction_cap,
                       "affective": affective_cap},
            "affective_cutoff_importance": cutoff_importance,
        }
        self._last_memory_compaction = copy.deepcopy(hasil)
        return hasil

    # -------------------- LOD (fix #2) --------------------
    def set_lod(self, mode: str, divisor: Optional[int] = None) -> Dict[str, Any]:
        """Atur level-of-detail: "penuh" | "latar" | "beku" (alias Inggris ok).

        `divisor`: pada mode "latar", fisika tick dijalankan sekali per
        `divisor` panggilan (default dari params["lod_divisor"], umumnya 10).
        Saat LOD diturunkan dari "beku"/"latar", event yang di-buffer tetap
        diterapkan pada fisika tick berikutnya — tidak ada yang hilang.
        """
        key = LOD_ALIASES.get(str(mode).lower())
        if key is None:
            raise ValueError(f"mode LOD tidak dikenal: {mode!r} "
                             f"(pilihan: {', '.join(LOD_MODES)})")
        self.lod_mode = key
        if divisor is not None:
            self.lod_divisor = max(1, int(divisor))
        if key == "penuh":
            self._lod_accum = 0
        elif key == "ringan":
            self.kompres_memori("ringan")
        elif key in ("latar", "abstrak", "beku"):
            # NPC latar/abstrak/beku tidak boleh menumpuk jejak tanpa batas.
            self.kompres_memori(key)
        return self.lod_status()

    def _lod_heavy(self) -> bool:
        """True hanya pada LOD "penuh" dan bukan tick ringan: lapisan berat
        (introspeksi/kesadaran/presentasi/ritual) dilewati pada mode lain."""
        return self.lod_mode == "penuh" and not self._force_light

    def tick_light(self, events: Optional[Iterable[Dict[str, Any]]] = None,
                   action_cost: bool = False) -> None:
        """Tick ringan: fisika dasar tanpa lapisan berat (untuk semua NPC)."""
        prev = self._force_light
        self._force_light = True
        try:
            self.tick(events=events, action_cost=action_cost)
        finally:
            self._force_light = prev

    def heavy_computation(self) -> Dict[str, Any]:
        """Komputasi berat (introspeksi/kesadaran/presentasi) sekali jalan.

        Dipisahkan dari tick agar game loop dapat menjalankannya hanya untuk
        NPC dekat Player (lihat KawananNPC.tick_layered).
        """
        if self.lod_mode == "beku":
            return {}
        hasil: Dict[str, Any] = {}
        if self._introspeksi_aktif():
            try:
                self.nurani.update_introspection(
                    levels=self.levels, urgency=self.urgency,
                    valence=self.mood().valence, arousal=self.mood().arousal,
                    tick=self.tick_count, rng=self._rng)
                hasil["introspeksi"] = True
            except Exception as _galat_diagnostik_127:
                _diag.catat('naluri.Naluri.heavy_computation', "galat pada jalur fallback", galat=_galat_diagnostik_127, jalur=127)
                pass
        if self._kesadaran_aktif():
            try:
                self.kesadaran.step(1)
                hasil["kesadaran"] = True
            except Exception as _galat_diagnostik_128:
                _diag.catat('naluri.Naluri.heavy_computation', "galat pada jalur fallback", galat=_galat_diagnostik_128, jalur=128)
                pass
        if self._presentasi_aktif():
            try:
                self.presentasi.tick(1)
                hasil["presentasi"] = True
            except Exception as _galat_diagnostik_129:
                _diag.catat('naluri.Naluri.heavy_computation', "galat pada jalur fallback", galat=_galat_diagnostik_129, jalur=129)
                pass
        if self._ritual_aktif():
            try:
                self.ritual.tick(1)
                hasil["ritual"] = True
            except Exception as _galat_diagnostik_130:
                _diag.catat('naluri.Naluri.heavy_computation', "galat pada jalur fallback", galat=_galat_diagnostik_130, jalur=130)
                pass
        return hasil

    def lod_status(self) -> Dict[str, Any]:
        return {"mode": self.lod_mode, "divisor": self.lod_divisor,
                "akumulator": self._lod_accum,
                "event_dibuffer": len(self._event_buffer)}

    def apply_events(self, events: Iterable[Dict[str, Any]]) -> None:
        # Periksa seluruh batch sebelum persepsi atau perubahan state.
        try:
            evs = list(events)
        except TypeError as exc:
            raise ValueError("events harus iterable mapping") from exc
        dikenal = {"drive", "delta", "stimulus", "context", "text", "reason",
                   "salience", "source", "emosi", "intensitas", "tag", "jenis",
                   "kind", "content", "konten", "proses", "_dapat_dilaporkan"}
        for index, ev in enumerate(evs):
            label = "events[{}]".format(index)
            if not isinstance(ev, Mapping):
                raise ValueError(label + " harus mapping")
            masalah = []
            asing = [str(k) for k in ev if k not in dikenal]
            if asing:
                masalah.append("kunci tidak dikenal: " + ", ".join(sorted(asing)))
            if "drive" in ev and not isinstance(ev["drive"], str):
                raise ValueError(label + ".drive harus string")
            if "drive" in ev and ev["drive"] not in DRIVES:
                masalah.append("drive tidak dikenal: {!r}".format(ev["drive"]))
            if masalah:
                pesan = label + ": " + "; ".join(masalah)
                _diag.catat("Naluri.apply_events", pesan)
                if self.params.get("strict_events", False):
                    raise ValueError(pesan)
            float_hingga(ev.get("delta", 0.0), label + ".delta")
        # PERSEPSI (gated): stimulus dunia tidak masuk apa adanya — ia
        # direkonstruksi oleh saluran indera + atensi sebelum jadi delta.
        # Flag mati = daftar event dipakai apa adanya (jalur lama persis).
        if self._persepsi_aktif():
            evs = self._persepsi_batch(evs)
        context_seen = set()
        for ev in evs:
            context_text = ev.get("stimulus", ev.get("context", ev.get("text", ev.get("reason"))))
            if context_text:
                context_key = self._context_key(str(context_text))
                if context_key and context_key not in context_seen:
                    context_seen.add(context_key)
                    self.remember_context(str(context_text),
                                          salience=float(ev.get("salience", 1.0)),
                                          source=str(ev.get("source", "event")))
            d = ev.get("drive")
            delta = float_hingga(ev.get("delta", 0.0), "delta event")
            if context_text and d in DRIVES:
                key = self._context_key(str(context_text))
                item = next((c for c in self.context_aktif if c.get("key") == key), None)
                if item is not None:
                    item.setdefault("delta", {x: 0.0 for x in DRIVES})[d] = jepit_drive(delta)
            if d in self.levels:
                self.delta(d, delta, reason=str(ev.get("reason", "")))
            # EMPATI: event boleh membawa emosi langsung, mis.
            # {"emosi": "takut", "intensitas": 0.7, "reason": "jumpscare"}
            # (no-op selama enable_emosi mati; field drive boleh absen).
            if ev.get("emosi"):
                self.feel(ev["emosi"], float(ev.get("intensitas", 0.5)),
                          alasan=str(ev.get("reason", "")))
            # KESADARAN: peristiwa menjadi KANDIDAT isi kesadaran; hanya yang
            # memenangkan kompetisi atensi nanti yang disiarkan (ignition).
            if self._kesadaran_aktif():
                self.kesadaran.observe_event(ev)

    # -------------------- PERSEPSI (lapisan rekonstruksi) --------------------
    # Fisiologi & teori yang diimplementasikan (semua gated enable_perception):
    #   * Derau reseptor + Signal Detection Theory (Green & Swets): dv =
    #     |r|·d' + N(0, σ/d'); criterion per-drive (watak) → hipervigilan.
    #   * Weber-Fechner + adaptation-level (Helson): sensasi logaritmik
    #     terhadap level adaptasi saluran (NURANI pilar F).
    #   * Habituasi + pemulihan spontan (reflex physiology).
    #   * Atensi terbatas (Broadbent) dengan atenuasi (Treisman) dan
    #     penyempitan oleh arousal (Easterbrook).
    #   * Congruence mood/emosi (Bower, affective realism): EMOSI_PERSEPSI.
    #   * Pemrosesan prediktif (Helmholtz/Friston): blend bukti sensorik
    #     dengan prior afektif per reliabilitas (trust).
    #   * Alarm palsu (false alarm SDT): criterion negatif + derau → NPC
    #     "melihat" ancaman yang tidak ada (persepsi hantu).
    #   * Affordance (Gibson) + kesiapan perseptual (Bruner "New Look"):
    #     kebutuhan membuat kemungkinan aksi menonjol (choose_action opsional).
    #   * Perceptual learning: d' saluran diperbarui dari galat prediksi
    #     (observe_outcome → NURANI.belajar_persepsi).

    def _persepsi_aktif(self) -> bool:
        return bool(self.params.get("enable_perception", False))

    def _introspeksi_aktif(self) -> bool:
        return bool(self.params.get("enable_introspection", False) and self.nurani is not None and self.nurani.enabled("introspection"))

    def _kesadaran_aktif(self) -> bool:
        """True bila lapisan kesadaran menyala (master flag)."""
        return bool(self.params.get("enable_kesadaran", False)
                    and getattr(self, "kesadaran", None) is not None)

    def _presentasi_aktif(self) -> bool:
        """True bila lapisan presentasi (Pycos) menyala (master flag)."""
        return bool(self.params.get("enable_presentasi", False)
                    and getattr(self, "presentasi", None) is not None)

    def _ritual_aktif(self) -> bool:
        """True bila lapisan ritual (perilaku utilitas-nol) menyala."""
        return bool(self.params.get("enable_ritual", False)
                    and getattr(self, "ritual", None) is not None)

    def _persepsi_gain_emosi(self, drive: str) -> float:
        """Gain congruence: emosi aktif memperkuat saluran yang selaras."""
        if not self._emosi_aktif():
            return 1.0
        g = float(self.params.get("persepsi_emosi_gain", 0.6))
        if g <= 0.0:
            return 1.0
        tot = 0.0
        for e, peta in EMOSI_PERSEPSI.items():
            w = peta.get(drive, 0.0)
            if w:
                tot += self.emosi.get(e, 0.0) * w
        return 1.0 + g * tot

    def _persepsi_topdown(self, m: float, drive: str, reason: str) -> float:
        """Blend prediktif: persepsi = (1−w)·bukti + w·ekspektasi.

        w = persepsi_topdown × trust prior afektif (per-drive, dari WATAK
        cap). Tanpa slot/trust → bukti apa adanya. Ekspektasi = delta mentah
        slot (prior/trust) sehingga top-down bisa MENGISI sensasi yang lemah
        — "melihat yang ditakuti", inti persepsi prediktif.
        """
        nur = self.nurani
        w_base = float(self.params.get("persepsi_topdown", 0.35))
        if nur is None or not reason or w_base <= 0.0:
            return m
        prior, trust = nur.anticipate_detail(reason, hitung=False)
        t = float(trust.get(drive, 0.0))
        if t <= 1e-9:
            return m
        ekspektasi = float(prior.get(drive, 0.0)) / t
        w = min(0.95, w_base * t)
        return (1.0 - w) * m + w * ekspektasi

    def _catat_persepsi(self, jenis: str, drive: str, mentah: float,
                        persepsi: float, alasan: str = "") -> None:
        self._persepsi_log.append({
            "tick": self.tick_count, "jenis": jenis, "drive": drive,
            "mentah": round(float(mentah), 4),
            "persepsi": round(float(persepsi), 4),
            "alasan": str(alasan)[:40]})
        _pangkas_memori(self._persepsi_log, "persepsi_log", self._PERSEPSI_LOG_MAX)

    def _persepsi_batch(self, events: List[Dict[str, Any]]
                        ) -> List[Dict[str, Any]]:
        """Jalankan seluruh pipeline perseptual untuk satu batch event tick.

        Mengembalikan event BARU (tidak memutasi input) dengan "delta"
        tertransformasi dan metadata "_persepsi" (diabaikan konsumen lama).
        Event non-drive (emosi saja) lewat tanpa disaring — injeksi emosi
        eksplisit adalah 'jalan pintas subkortikal' (low road LeDoux).
        """
        nur = self.nurani
        hasil: List[Dict[str, Any]] = []
        calon: List[Tuple[float, int]] = []     # (skor atensi, indeks hasil)
        for ev in events:
            d = ev.get("drive")
            r = float(ev.get("delta", 0.0) or 0.0)
            alasan = str(ev.get("reason", "") or "")
            if d not in self.levels or abs(r) < 1e-12:
                hasil.append(ev)
                continue
            if nur is not None:
                dv, kat = nur.deteksi(d, r, self._rng)
                m = math.copysign(nur.kompres(d, dv), r)
                if kat == "subliminal":
                    m *= float(self.params.get("persepsi_subliminal", 0.25))
                m *= nur.habit_factor(d, alasan, self.tick_count)
            else:
                # Degradasi tanpa NURANI: tak ada state saluran — linear.
                m, kat = r, "sadar"
            m *= self._persepsi_gain_emosi(d)
            m = self._persepsi_topdown(m, d, alasan)
            ev2 = dict(ev)
            ev2["delta"] = m
            ev2["_persepsi"] = {"mentah": r, "kategori": kat, "atenuasi": False}
            hasil.append(ev2)
            # Prioritas atensi = besaran × relevansi kebutuhan (Posner:
            # urgensi drive adalah 'spotlight' internal).
            calon.append((abs(m) * (1.0 + self.urgency.get(d, 0.0)),
                          len(hasil) - 1))
        # --- atensi: kapasitas (Broadbent) + atenuasi (Treisman) +
        #     penyempitan arousal (Easterbrook) ---
        if calon:
            arousal = jepit_01(self.mood().arousal)
            kap = int(round(float(self.params.get("persepsi_atensi", 3))
                            - float(self.params.get("persepsi_arousal_fokus",
                                                    2.0)) * arousal))
            kap = max(1, kap)
            aten = float(self.params.get("persepsi_atenuasi", 0.35))
            calon.sort(key=lambda x: x[0], reverse=True)
            for rank, (_, idx) in enumerate(calon):
                if rank < kap:
                    continue
                info = hasil[idx]["_persepsi"]
                sebelum = float(hasil[idx]["delta"])
                hasil[idx]["delta"] = sebelum * aten
                info["atenuasi"] = True
                if abs(sebelum) >= 0.15:   # hanya yang mencolok dilogkan
                    self._catat_persepsi(
                        "teralihkan", str(hasil[idx].get("drive")),
                        info["mentah"], hasil[idx]["delta"],
                        str(hasil[idx].get("reason", "")))
            # akumulator adaptasi + log subliminal yang 'nyaris' terlihat
            for ev2 in hasil:
                info = ev2.get("_persepsi")
                d2 = ev2.get("drive")
                if info and d2 in self._persepsi_stim:
                    self._persepsi_stim[d2] += abs(float(ev2.get("delta", 0.0)))
                    if (info["kategori"] == "subliminal"
                            and abs(info["mentah"]) >= 0.05):
                        self._catat_persepsi(
                            "subliminal", str(d2), info["mentah"],
                            float(ev2["delta"]), str(ev2.get("reason", "")))
        return hasil

    def _persepsi_spontan(self, steps: int = 1) -> None:
        """Alarm palsu SDT: criterion negatif + derau endogen → persepsi hantu.

        Hanya saluran dengan `persepsi_kriterion` < 0 (watak hipervigilan)
        yang bisa memicu; probabilitas per tick ∝ kedalaman bias "ya",
        dikompensasi `steps` untuk LOD latar. Efek: delta negatif kecil +
        emosi takut + jejak log — paranoia yang muncul dari FISIOLOGI
        persepsi, bukan dari skrip.
        """
        nur = self.nurani
        rate = float(self.params.get("persepsi_alarm_rate", 0.06))
        maks = max(1e-3, float(self.params.get("persepsi_alarm_maks", 0.15)))
        ambang = float(nur._p("persepsi_ambang")) if nur is not None else 0.02
        noise = float(nur._p("persepsi_noise")) if nur is not None else 0.03
        for d in DRIVES:
            c = _nilai_per_drive(self.params, "persepsi_kriterion", d, 0.0)
            if c >= 0.0 or rate <= 0.0:
                continue
            p = min(0.25, rate * min(1.0, -c / 0.5))
            p = 1.0 - (1.0 - p) ** max(1, int(steps))
            if self._rng.random() >= p:
                continue
            sens = nur._sens(d) if nur is not None else 1.0
            besar = min(maks, ambang + sens * noise
                        * abs(self._rng.gauss(0.0, 1.0)))
            self.delta(d, -besar, reason="persepsi: alarm palsu (bayangan)")
            self.persepsi_alarm_palsu += 1
            if self._emosi_aktif():
                self.feel("takut", 0.2 + 0.6 * min(1.0, besar / maks),
                          "alarm palsu: seperti ada ancaman")
            self._catat_persepsi("alarm_palsu", d, 0.0, -besar, "bayangan")

    def persepsi(self, teks: str) -> Dict[str, Any]:
        """Apa yang NPC PERSEPSI dari sebuah deskripsi? (baca-saja, tanpa RNG)

        Pipeline deterministik untuk UI/dialog: lexicon (sudah termasuk prior
        afektif via impact_of) → kompresi Weber-Fechner/adaptasi → habituasi
        TANPA jejak → gain emosi → top-down. Tidak mengonsumsi RNG dan tidak
        memutasi state yang terserialisasi (counter `affective_hits` yang
        ikut naik lewat impact_of dipulihkan kembali; cache lexicon turunan
        tidak diserialisasi sehingga aman).
        """
        nur0 = self.nurani
        hits0 = nur0.affective_hits if nur0 is not None else 0
        imp = self.impact_of(teks)
        if nur0 is not None:
            nur0.affective_hits = hits0    # baca-saja: jangan hitung prior
        if not self._persepsi_aktif():
            return {"delta": dict(imp), "menonjol": None, "aktif": False}
        nur = self.nurani
        out: Dict[str, float] = {}
        for d in DRIVES:
            r = float(imp.get(d, 0.0))
            m = r
            if nur is not None:
                dv = abs(r) * nur._sens(d)          # tanpa derau (baca-saja)
                m = math.copysign(nur.kompres(d, dv), r)
                m *= nur.habit_factor(d, teks[:40], self.tick_count,
                                      mutate=False)
            m *= self._persepsi_gain_emosi(d)
            m = self._persepsi_topdown(m, d, teks)
            out[d] = m
        menonjol = max(DRIVES, key=lambda d: abs(out[d]))
        if abs(out[menonjol]) < 1e-6:
            menonjol = None
        return {"delta": out, "menonjol": menonjol, "aktif": True}

    def affordances(self, obj: Any) -> Dict[str, Any]:
        """Gibson + Bruner "New Look": apa yang lingkungan TAWARKAN sekarang?

        Kebutuhan (urgensi) membuat kemungkinan yang relevan menonjol —
        NPC lapar 'melihat' makanan di ruangan yang sama yang diabaikan
        NPC kenyang. obj: teks deskripsi (via impact_of) ATAU dict kandidat
        {drive_effects}. Mengembalikan {"salience": per-drive, "ancaman":
        per-drive, "menonjol": drive|None} — baca-saja.
        """
        if isinstance(obj, str):
            effects = self.impact_of(obj)
        elif isinstance(obj, dict):
            effects = obj.get("drive_effects") or {}
        else:
            effects = {}
        sal: Dict[str, float] = {}
        anc: Dict[str, float] = {}
        for d in DRIVES:
            e = float(effects.get(d, 0.0) or 0.0)
            bobot = 0.2 + self.urgency.get(d, 0.0)
            sal[d] = max(0.0, e) * bobot
            anc[d] = max(0.0, -e) * bobot
        gabungan = {d: sal[d] + anc[d] for d in DRIVES}
        menonjol = max(DRIVES, key=lambda d: gabungan[d])
        if gabungan[menonjol] < 1e-6:
            menonjol = None
        return {"salience": sal, "ancaman": anc, "menonjol": menonjol}

    def _salience_kandidat(self, effects: Mapping[str, Any]) -> float:
        """Salience afordansi untuk choose_action (bonus opsional)."""
        tot = 0.0
        for d in DRIVES:
            e = float((effects or {}).get(d, 0.0) or 0.0)
            tot += abs(e) * self.urgency.get(d, 0.0)
        return tot

    def persepsi_state(self) -> Dict[str, Any]:
        """Snapshot lapisan persepsi untuk HUD/status (JSON-safe)."""
        st: Dict[str, Any] = {
            "aktif": self._persepsi_aktif(),
            "alarm_palsu": self.persepsi_alarm_palsu,
            "log": len(self._persepsi_log),
            "terakhir": (dict(self._persepsi_log[-1])
                         if self._persepsi_log else None),
        }
        if self.nurani is not None:
            st["saluran"] = self.nurani.persepsi_ringkas()
        return st

    def delta(self, drive: str, amount: float, reason: str = "") -> None:
        """Perubahan drive eksplisit (untuk dipanggil dari luar).

        `reason` dicatat ke `delta_log` (terbatas) supaya jejak mengapa sebuah
        drive bergerak dapat ditelusuri -- skema event di `tick()` memang
        menyertakan field `reason`.
        """
        if drive in self.levels:
            jumlah = float_hingga(amount, "delta[{}]".format(drive))
            # Kontradiksi yang SUDAH disadari sebagai lapisan paralel bukan
            # kegagalan koherensi. Penurunan lain (kejutan, kacau, kalibrasi)
            # tetap berlaku; kontradiksi tak disadari juga tetap menghukum.
            alasan_low = str(reason).lower()
            if (drive == "koherensi" and jumlah < 0.0
                    and any(k in alasan_low for k in
                            ("kontradiksi", "disonansi", "dissonance", "contradiction"))):
                o = getattr(self, "_organik", None)
                if o is not None and o.paralel.tanpa_resolusi():
                    jumlah = 0.0
            self.levels[drive] += jumlah
            self.delta_log.append({
                "tick": self.tick_count, "drive": drive,
                "amount": round(jumlah, 4), "reason": reason,
                "kontradiksi_disadari": bool(
                    jumlah == 0.0 and float(amount) < 0.0),
            })
            _pangkas_memori(self.delta_log, "delta_log", self._DELTA_LOG_MAX)

    def deficit(self, drive: str) -> float:
        """Besar defisit (positif jika level di bawah 0)."""
        return max(0.0, -self.levels.get(drive, 0.0))

    # -------------------- mood --------------------
    def mood(self) -> Mood:
        # MEMOIZATION: mood murni dari (levels, urgency, emosi, weights, stage).
        # Signature murah ini membuat pemanggilan berulang dalam keadaan yang
        # sama (presentasi/kesadaran/choose_action) mengembalikan cache.
        _sig = (self.tick_count, self.stage,
                round(sum(self.levels.values()), 6),
                round(sum(self.urgency.values()), 6),
                round(sum(self.emosi.values()), 6))
        _cache = self._mood_cache
        if _cache is not None and _cache[0] == _sig:
            return _cache[1]
        # Valensi = rata-rata level TERBOBOT bobot drive kepribadian.
        wsum = sum(self.weights.values())
        valence = sum(self.levels[d] * self.weights[d] for d in DRIVES) / max(1e-6, wsum)
        # Arousal = rata-rata urgensi terbobot (tenang ↔ gelisah).
        arousal = min(1.0, sum(self.urgency[d] * self.weights[d] for d in DRIVES)
                           / (max(1e-6, wsum) * 0.9))
        # EMPATI (gated): emosi diskret mewarnai mood — senang mengangkat
        # valensi, takut/marah mengangkat arousal, dst. Mati = rumus lama utuh.
        if self.params.get("enable_emosi", False):
            e = self.emosi
            valence += (0.15 * (e["senang"] - e["sedih"])
                        - 0.10 * (e["takut"] + e["marah"]))
            arousal += (0.30 * max(e["takut"], e["marah"])
                        + 0.15 * max(e["senang"], e["penasaran"]))
        m = Mood(valence=jepit_drive(valence),
                 arousal=jepit_01(arousal))
        self._mood_cache = (_sig, m)
        return m

    # -------------------- goal stack --------------------
    def _rebuild_goals(self) -> None:
        threshold = self.params["goal_urgency_threshold"]
        # urut drive berdasarkan urgensi, turun
        ranked = sorted(DRIVES, key=lambda d: self.urgency[d], reverse=True)
        new_goals: List[Goal] = []
        existing = {g.drive: g for g in self.goals}
        for d in ranked:
            if self.urgency[d] < threshold and d not in existing:
                continue
            if d in existing:
                # Bug-fix: pernyataan goal stabil sejak terbentuk (sebelumnya
                # di-gulung ulang tiap tick sehingga narasi goal "berkedip"
                # acak; Ego/abstraksi mengutip statement ini).
                g = existing[d]
                g.urgency = self.urgency[d]
            else:
                templates = GOAL_TEMPLATES.get(d)
                tpl = self._rng.choice(templates)
                stmt = tpl.format(urg=self.urgency[d])
                g = Goal(drive=d, urgency=self.urgency[d],
                         statement=stmt, created_tick=self.tick_count)
            new_goals.append(g)
            if len(new_goals) >= int(self.params["max_goals"]):
                break
        self.goals = new_goals

    def _active_subgoal(self) -> Optional[Goal]:
        """Satu subgoal aktif teratas dari hierarki satu tingkat."""
        options = [(float(s.urgency), s)
                   for g in self.goals
                   for s in g.subgoals if not s.completed]
        return max(options, key=lambda x: x[0])[1] if options else None

    def set_subgoal(self,
                    parent_drive: str,
                    statement: str,
                    drive: Optional[str] = None,
                    urgency: Optional[float] = None) -> Dict[str, Any]:
        """Tetapkan/mutakhirkan satu subgoal opsional untuk goal induk."""
        if parent_drive not in DRIVES:
            raise ValueError(f"drive induk tidak dikenal: {parent_drive!r}")
        child_drive = drive or parent_drive
        if child_drive not in DRIVES:
            raise ValueError(f"drive subgoal tidak dikenal: {child_drive!r}")
        parent = next((g for g in self.goals if g.drive == parent_drive), None)
        if parent is None:
            templates = GOAL_TEMPLATES.get(parent_drive, ["{urg:.2f}"])
            parent = Goal(parent_drive, self.urgency.get(parent_drive, 0.0),
                          self._rng.choice(templates).format(
                              urg=self.urgency.get(parent_drive, 0.0)), self.tick_count)
            self.goals.append(parent)
            self.goals.sort(key=lambda g: g.urgency, reverse=True)
            self.goals = self.goals[:max(1, int(self.params.get("max_goals", 4)))]
            parent = next((g for g in self.goals if g.drive == parent_drive), parent)
        child_urgency = (parent.urgency if urgency is None
                         else jepit(float(urgency), 0.0, 2.5))
        child = Goal(drive=child_drive, urgency=child_urgency,
                     statement=str(statement)[:240], created_tick=self.tick_count)
        # Satu tingkat, satu subgoal aktif; tidak ada recursive nesting.
        parent.subgoals = [child]
        parent.completed = False
        return {"parent": parent.to_dict(), "active_subgoal": child.to_dict()}

    def complete_subgoal(self, parent_drive: Optional[str] = None) -> Dict[str, Any]:
        """Tandai subgoal selesai dan turunkan urgency goal induk."""
        parents = [g for g in self.goals if g.active_subgoal() is not None
                   and (parent_drive is None or g.drive == parent_drive)]
        if not parents:
            return {"completed": False, "reason": "tidak ada subgoal aktif"}
        parent = max(parents, key=lambda g: g.urgency)
        child = parent.active_subgoal()
        if child is None:
            return {"completed": False, "reason": "tidak ada subgoal aktif"}
        child.completed = True
        retain = jepit_01(float(self.params.get("subgoal_completion_decay", 0.75)))
        self.urgency[parent.drive] = max(0.0, self.urgency.get(parent.drive, 0.0) * retain)
        parent.urgency = self.urgency[parent.drive]
        return {"completed": True, "parent_drive": parent.drive,
                "subgoal": child.statement, "parent_urgency": parent.urgency}

    def goal_to_scenario(self) -> str:
        drive_urgency = 0.0
        if not self.goals:
            # fallback jika semua drive nyaman: eksplorasi ringan
            task = "Jelajahi jalur baru yang mungkin memberikan wawasan (tidak ada goal mendesak)"
        else:
            # pilih goal teratas, tapi 30% acak dari 2 teratas untuk variasi
            top = self.goals[0]
            if len(self.goals) > 1 and self._rng.random() < 0.3:
                top = self._rng.choice(self.goals[:2])
            active = top.active_subgoal()
            task = active.statement if active is not None else top.statement
            drive_urgency = float(active.urgency if active is not None else top.urgency)
        if self._kesadaran_aktif():
            try:
                own = self.kesadaran.free_will_current_goal()
                if own and float(own.get("prioritas", 0.0)) >= drive_urgency:
                    task = "Tujuan yang kupilih sendiri: " + str(own.get("tujuan", ""))
            except Exception as _galat_diagnostik_131:
                _diag.catat('naluri.Naluri.goal_to_scenario', "galat pada jalur fallback", galat=_galat_diagnostik_131, jalur=131)
                pass
        if self.context_aktif:
            context = max(self.context_aktif,
                          key=lambda c: float(c.get("salience", 0.0)))
            return f"{task} (mengingat konteks: {context.get('stimulus', '')[:72]})"
        return task

    # -------------------- lexicon / impact_of / scoring --------------------
    def add_lexicon(self, word: str, drive_deltas: Dict[str, float]) -> None:
        self.lexicon[word.lower()] = dict(drive_deltas)
        self._lexicon_dirty = True

    @staticmethod
    def _context_key(text: str) -> str:
        """Kunci kerja ringkas untuk menyatukan pengamatan berulang."""
        return " ".join(re.findall(r"[\w]+", str(text or "").lower()))[:120]

    @staticmethod
    def _context_similarity(a: str, b: str) -> float:
        """Jaccard sederhana; dipakai hanya untuk memori kerja kecil (<=5 slot)."""
        ta = set(re.findall(r"[\w]+", str(a or "").lower()))
        tb = set(re.findall(r"[\w]+", str(b or "").lower()))
        if not ta or not tb:
            return 0.0
        return len(ta & tb) / max(1, len(ta | tb))

    def remember_context(self,
                         stimulus: str,
                         salience: float = 1.0,
                         source: str = "observation",
                         outcome: Any = None,
                         action: Optional[str] = None,
                         tick: Optional[int] = None,
                         learn: bool = True) -> Dict[str, Any]:
        """Masukkan observasi ke working memory 3–5 slot yang cepat meluruh.

        Ground-truth `outcome` opsional; bila tersedia ia juga memperbarui
        memori afektif NURANI sehingga pengulangan bermakna menjadi intuisi.
        Pengamatan tanpa hasil nyata tidak diajarkan sebagai fakta.
        """
        text = str(stimulus or "").strip()
        key = self._context_key(text)
        if not key:
            return {"aktif": False, "alasan": "stimulus kosong"}
        now = self.tick_count if tick is None else int(tick)
        sal = jepit_01(float(salience))
        # Compute before inserting this item so its first observation does not
        # feed back onto itself through impact_of().
        delta = self.impact_of(text)
        repeat = self._context_repeat.get(key, {"count": 0, "last_t": now})
        repeat_count = int(repeat.get("count", 0)) + 1
        self._context_repeat[key] = {"count": repeat_count, "last_t": now,
                                     "text": text[:120]}
        found = next((c for c in self.context_aktif if c.get("key") == key), None)
        if found is None:
            found = next((c for c in self.context_aktif
                          if self._context_similarity(text, c.get("stimulus", "")) >= 0.82), None)
        if found is None:
            found = {"key": key, "stimulus": text[:160], "salience": sal,
                     "tick": now, "last_decay_tick": now, "age": 0, "delta": dict(delta),
                     "source": str(source)[:40], "repeat": repeat_count,
                     "action": str(action or "")[:80]}
            self.context_aktif.append(found)
        else:
            # Ulangi konteks memperkuat salience, tetapi dibatasi agar tidak
            # mengunci perhatian permanen; timestamp menyegarkan short-term memory.
            found["salience"] = min(1.0, max(float(found.get("salience", 0.0)) * 0.75, sal))
            found["tick"] = now
            found["last_decay_tick"] = now
            found["age"] = 0
            found["repeat"] = repeat_count
            found["source"] = str(source)[:40]
            if action:
                found["action"] = str(action)[:80]
            found["delta"] = {d: 0.65 * float((found.get("delta") or {}).get(d, 0.0))
                              + 0.35 * float(delta.get(d, 0.0)) for d in DRIVES}
        cap = max(3, min(5, int(self.params.get("context_capacity", 5))))
        if len(self.context_aktif) > cap:
            self.context_aktif.sort(key=lambda c: (float(c.get("salience", 0.0)),
                                                   int(c.get("tick", 0))), reverse=True)
            del self.context_aktif[cap:]

        learned = False
        if outcome is not None:
            raw_deltas = outcome.get("drive_deltas") if isinstance(outcome, Mapping) else None
            if isinstance(raw_deltas, Mapping) and any(abs(float(v or 0.0)) > 1e-9
                                                       for v in raw_deltas.values()):
                actual_deltas = {d: float(raw_deltas.get(d, 0.0) or 0.0) for d in DRIVES}
            else:
                projected = {"impact": float(outcome)} if isinstance(outcome, (int, float)) else outcome
                actual_deltas = self.project_outcome_to_drives(projected)
            # Ground-truth effect, bila ada, memperbaiki signature konteks aktif.
            found["delta"] = {d: jepit_drive(0.35 * float((found.get("delta") or {}).get(d, 0.0))
                + 0.65 * float(actual_deltas.get(d, 0.0))) for d in DRIVES}
            if learn and bool(self.params.get("context_auto_experience", True)):
                learned = self.experience(text, actual_deltas)
        # Hanya simpan ringkasan repetisi yang masih mungkin membantu; tidak
        # membiarkan konteks sekali-lihat tumbuh tanpa batas.
        if len(self._context_repeat) > 64:
            oldest = min(self._context_repeat, key=lambda k: int(self._context_repeat[k].get("last_t", 0)))
            self._context_repeat.pop(oldest, None)
        result = copy.deepcopy(found)
        result["aktif"] = True
        result["repeat_count"] = repeat_count
        result["learned"] = learned
        return result

    def clear_context(self) -> int:
        """Kosongkan working memory aktif; replay dan memori jangka panjang tetap."""
        n = len(self.context_aktif)
        self.context_aktif = []
        return n

    def _advance_working_memory(self, steps: int) -> None:
        """Decay konteks ber- half-life 5–10 tick; LOD memakai Δt aktual."""
        half_life = max(1.0, float(self.params.get("context_decay_ticks", 8)))
        minimum = max(0.0, float(self.params.get("context_min_salience", 0.025)))
        for item in self.context_aktif:
            last_decay = int(item.get("last_decay_tick", item.get("tick", self.tick_count)))
            elapsed = max(0, self.tick_count - last_decay)
            if elapsed == 0:
                elapsed = max(1, int(steps))
            factor = 0.5 ** (elapsed / half_life)
            item["age"] = int(item.get("age", 0)) + elapsed
            item["salience"] = float(item.get("salience", 0.0)) * factor
            item["last_decay_tick"] = self.tick_count
        self.context_aktif = [c for c in self.context_aktif
                              if float(c.get("salience", 0.0)) >= minimum]
        horizon = max(12, 3 * int(half_life))
        for key, item in list(self._context_repeat.items()):
            if self.tick_count - int(item.get("last_t", self.tick_count)) > horizon:
                self._context_repeat.pop(key, None)

    def _working_memory_impact(self, text: str,
                               deltas: Dict[str, float]) -> None:
        if not bool(self.params.get("context_bind_impact", True)) or not text:
            return
        gain = max(0.0, float(self.params.get("context_impact_gain", 0.18)))
        for item in self.context_aktif:
            similarity = self._context_similarity(text, item.get("stimulus", ""))
            if similarity < 0.20:
                continue
            weight = gain * similarity * float(item.get("salience", 0.0))
            for d in DRIVES:
                deltas[d] += weight * float((item.get("delta") or {}).get(d, 0.0))

    def _working_memory_action_bias(self, effects: Mapping[str, Any]) -> float:
        """Konteks ancaman aktif mendorong langkah protektif, bukan skor dunia."""
        danger = sum(float(c.get("salience", 0.0))
                     * max(0.0, -float((c.get("delta") or {}).get("keamanan", 0.0)))
                     for c in self.context_aktif)
        if danger <= 0.0:
            return 0.0
        security = float((effects or {}).get("keamanan", 0.0) or 0.0)
        return (float(self.params.get("context_action_bias", 0.24)) * danger
                * jepit_drive(security))

    def set_lexicon(self,
                    mapping: Optional[Dict[str, Dict[str, float]]] = None,
                    merge: bool = False) -> int:
        """Ganti (atau dengan merge=True, tambahkan) lexicon kata — fix #5.

        Lexicon bukan lagi konstanta modul Indonesia-only: mapping apa pun
        bisa di-inject per NPC (mis. lexicon Inggris untuk build internasional,
        atau lexicon domain khusus). `mapping=None` tanpa merge mengembalikan
        lexicon default bawaan (LEXICON). Mengembalikan jumlah entri aktif.
        """
        if mapping is None and not merge:
            self.lexicon = {w: dict(v) for w, v in LEXICON.items()}
        elif merge:
            for w, dv in (mapping or {}).items():
                self.lexicon[str(w).lower()] = dict(dv)
        else:
            self.lexicon = {str(w).lower(): dict(dv)
                            for w, dv in (mapping or {}).items()}
        self._lexicon_dirty = True
        return len(self.lexicon)

    def set_tag_lexicon(self,
                        mapping: Optional[Dict[str, Dict[str, float]]] = None,
                        merge: bool = False) -> int:
        """Ganti/tambah lexicon tag khusus (lihat set_lexicon)."""
        if mapping is None and not merge:
            self.tag_lexicon = {t: dict(v) for t, v in TAG_LEXICON.items()}
        elif merge:
            for t, dv in (mapping or {}).items():
                self.tag_lexicon[str(t)] = dict(dv)
        else:
            self.tag_lexicon = {str(t): dict(dv) for t, dv in (mapping or {}).items()}
        self._lexicon_dirty = True
        return len(self.tag_lexicon)

    def use_lexicon_pack(self, pack: str) -> int:
        """Pakai paket bahasa bawaan: "id" (default) atau "en" (contoh i18n)."""
        if pack not in LEXICON_PACKS:
            raise ValueError(f"paket lexicon tidak dikenal: {pack!r} "
                             f"(tersedia: {', '.join(sorted(LEXICON_PACKS))})")
        kata, tag = LEXICON_PACKS[pack]
        self.lexicon = {w: dict(v) for w, v in kata.items()}
        self.tag_lexicon = {t: dict(v) for t, v in tag.items()}
        self._lexicon_dirty = True
        return len(self.lexicon)

    def _compile_lexicon(self) -> None:
        """Pre-compile lexicon: trie karakter + urutan/rank kata (fix #6).

        Dibangun sekali dan dipakai ulang sampai lexicon berubah
        (`_lexicon_dirty`), menggantikan `sorted(..., key=len, reverse=True)`
        yang dihitung ulang pada SETIAP panggilan `impact_of()`.
        """
        # Indeks frasa leksikon sebagai rentang token ternormalisasi (D1):
        # "zaman dahulu" tidak lagi cocok dengan substring "aman".
        from pycos.bahasa.teks import normalisasi_token as _norm_tok

        root: Dict[str, Any] = {}
        entri_parts: Dict[tuple, List[str]] = {}
        for word in self.lexicon:
            w = str(word).lower().strip()
            if not w:
                continue
            parts = tuple(p for p in
                          (_norm_tok(pw) for pw in w.split())
                          if p)
            if not parts:
                continue
            node = root
            for ch in w:
                node = node.setdefault(ch, {})
            node[""] = w  # penanda ujung frasa (kompatibilitas)
            entri_parts.setdefault(parts, []).append(w)
        self._trie = root
        self._entri_parts = entri_parts
        # panjang maksimum frasa dalam leksikon (untuk pemindaian jendela)
        self._maks_frasa = max((len(p) for p in entri_parts), default=1)
        # Urutan lama: panjang menurun, seri -> urutan insersi (sorted stabil).
        order = sorted(self.lexicon.keys(), key=len, reverse=True)
        self._lexicon_rank = {w: i for i, w in enumerate(order)}
        self._tags_lower = [(str(t).lower(), dict(dv))
                            for t, dv in self.tag_lexicon.items()]
        self._tags_by_lower = {str(t).lower(): dict(dv)
                               for t, dv in self.tag_lexicon.items()}
        tag_parts: Dict[tuple, List[Tuple[str, Dict[str, float]]]] = {}
        for t, dv in self._tags_lower:
            parts = tuple(p for p in
                          (_norm_tok(pw) for pw in t.split())
                          if p)
            if parts:
                tag_parts.setdefault(parts, []).append((t, dv))
        self._tag_parts = tag_parts
        self._impact_cache = {}
        self._lexicon_dirty = False

    def _lexicon_occurrences(self, low: str) -> List[Tuple[str, int, int]]:
        """Semua kemunculan kata/frasa lexicon di `low` — satu lintasan trie,
        O(panjang teks × kedalaman frasa)."""
        occ: List[Tuple[str, int, int]] = []
        trie: Dict[str, Any] = self._trie or {}
        n = len(low)
        i = 0
        while i < n:
            node = trie.get(low[i])
            if node is None:
                i += 1
                continue
            j = i  # j = indeks karakter terakhir yang dikonsumsi
            while True:
                w = node.get("")
                if w is not None:
                    occ.append((w, i, j + 1))
                if j + 1 >= n:
                    break
                nxt = node.get(low[j + 1])
                if nxt is None:
                    break
                node = nxt
                j += 1
            i += 1
        return occ

    _PENGUAT_POS = frozenset({"kurang", "ringan", "agak", "sedikit", "jarang"})

    def _span_cocok(self, text: str
                    ) -> List[Tuple[str, int, int, bool, bool]]:
        """Rentang token leksikon/tag di `text`.

        Mengembalikan (nama_entri, awal, akhir, terbalik, diabaikan) per entri
        yang cocok, memakai tokenisasi bersama (A1–A2: "senaaang"→"senang",
        "gk"→"tidak") dan cakupan negasi bersama (D2). `terbalik` True bila
        mayoritas isi rentang berada dalam cakupan negasi — tandanya dibalik.
        `diabaikan` True bila diatur pengurang ("kurang X") atau retorika
        ("mana mungkin") — kontribusinya nol.
        """
        from pycos.bahasa.teks import cakupan_negasi, tokenisasi
        deltas_flags: List[Tuple[str, int, int, bool, bool]] = []
        toks = tokenisasi(text)
        if not toks:
            return []
        flags = cakupan_negasi(toks)
        # daftar kata sesuai urutan, dengan indeks klausa dan flag negasi
        kata: List[str] = []
        kata_flag: List[bool] = []
        kata_klausa: List[int] = []
        klausa = 0
        for t, f in zip(toks, flags):
            if t.jenis == "tanda_baca":
                klausa += 1
                continue
            if t.jenis != "kata":
                continue
            kata.append(t.bentuk)
            kata_flag.append(f)
            kata_klausa.append(klausa)
        n = len(kata)
        if n == 0:
            return []
        # pengurangan & retorika per klausa
        batas_kanan = [0] * n
        for i in range(n):
            j = i
            while j + 1 < n and kata_klausa[j + 1] == kata_klausa[j]:
                j += 1
            batas_kanan[i] = j + 1
        terdeteksi: List[Tuple[tuple, int]] = []
        # pemangkasan jendela: hanya mulai di kata, panjang <= maks_frasa
        for i in range(n):
            for L in range(self._maks_frasa, 0, -1):
                if i + L > n:
                    continue
                if kata_klausa[i] != kata_klausa[i + L - 1]:
                    continue
                jendela = tuple(kata[i:i + L])
                if jendela in self._entri_parts or jendela in self._tag_parts:
                    terdeteksi.append((jendela, i))
        # aturan lemah: jangan tumpang-tindih bagian dari rentang lebih panjang
        terdeteksi.sort(key=lambda kv: (-len(kv[0]), kv[1]))
        terpakai: List[Tuple[int, int]] = []
        for jendela, i in terdeteksi:
            L = len(jendela)
            if any(i < e and s < i + L for s, e in terpakai):
                continue
            isi_flag = kata_flag[i:i + L]
            terbalik = sum(isi_flag) > L / 2.0
            # pengurang: kata sebelum rentang dalam klausa yang sama & dekat
            lemah = False
            for j in range(max(0, i - 2), i):
                if kata_klausa[j] != kata_klausa[i]:
                    break
                if kata[j] in self._PENGUAT_POS:
                    lemah = True
                    break
            # retorika: "mana/masa mungkin" mendahului dalam klausa yang sama
            if not lemah:
                awal_k = i
                while awal_k > 0 and kata_klausa[awal_k - 1] == kata_klausa[i]:
                    awal_k -= 1
                for j in range(awal_k, i):
                    if kata[j] in ("mana", "masa") and j + 1 < n \
                            and kata[j + 1] == "mungkin":
                        lemah = True
                        break
            for nama in self._entri_parts.get(jendela, []):
                deltas_flags.append((nama, i, i + L, terbalik, lemah))
            for t, dv in self._tag_parts.get(jendela, []):
                deltas_flags.append(("tag::" + t, i, i + L, terbalik, lemah))
            terpakai.append((i, i + L))
        return deltas_flags

    def _base_impact(self, text: str) -> Dict[str, float]:
        """Dampak lexicon+tag+marker (SEBELUM prior NURANI & clip).

        D1: pencocokan berdasarkan token (A1/A2), bukan substring — "aman"
        tidak lagi cocok di dalam "dahulu"— dan cakupan negasi (D2) membalik
        tanda entri ("tidak aman" → keamanan −0,5; "bukan ancaman" → +0,6).
        Urutan terpanjang-dulu, entri yang sama maksimal satu kali,
        maksimum 5 hit (dipertahankan dari algoritma lama).
        """
        deltas = {d: 0.0 for d in DRIVES}
        cocok = self._span_cocok(text)
        if cocok:
            # pilih menurut rank lexicon lama (panjang menurun, lalu insersi),
            # entri yang sama sekali per kemunculan pertama
            per_entri: Dict[str, Tuple[int, int, bool, bool]] = {}
            for nama, i, e, terbalik, lemah in cocok:
                per_entri.setdefault(nama, (i, e, terbalik, lemah))
            dipilih = sorted(per_entri.items(),
                             key=lambda kv: self._lexicon_rank.get(
                                 kv[0].replace("tag::", "").lower(), 10 ** 9))
            hits = 0
            for nama, (i, e, terbalik, lemah) in dipilih:
                if hits >= 5:
                    break
                if lemah:
                    continue
                if nama.startswith("tag::"):
                    t_low = nama[5:].lower()
                    dv = dict(self._tags_by_lower.get(t_low) or {})
                    for k, v in dv.items():
                        if k in deltas:
                            deltas[k] += v * (-0.3 if terbalik else 0.3)
                    hits += 1
                    continue
                entri = self.lexicon.get(nama)
                if not entri:
                    continue
                tanda = -1.0 if terbalik else 1.0
                for k, v in entri.items():
                    if k in deltas:
                        deltas[k] += v * tanda
                hits += 1
        # deteksi sleeper/tanda waktu: t+N → ancaman laten
        if "[⌛" in text or "t+" in text:
            deltas["keamanan"] -= 0.05
            deltas["koherensi"] -= 0.02
        # probabilitas/keyakinan rendah → koherensi turun sedikit
        for marker in ("prob=0%", "prob=0.0", "tidak yakin", "ketidakpastian"):
            if marker in text:
                deltas["koherensi"] -= 0.05
        return deltas

    def impact_of(self, text: str) -> Dict[str, float]:
        """Hitung vektor perubahan drive dari sebuah deskripsi.

        Fix #6: lexicon di-pre-compile menjadi trie + rank (tidak ada lagi
        `sorted()` dan scan `in` per kata pada setiap panggilan), dan hasil
        lexicon di-cache LRU per teks — NPC yang berbicara tiap frame dengan
        kalimat berulang membayar O(1). Semantik penilaian identik dengan
        algoritma lama (longest-first, sekali per frasa, maksimum 5 hit).
        Prior afektif NURANI selalu dihitung segar (tidak di-cache) karena ia
        terus belajar.
        """
        if text is None:
            return {d: 0.0 for d in DRIVES}
        if self._lexicon_dirty or self._trie is None:
            self._compile_lexicon()
        cache_cap = _batas_memori("impact_cache")
        if len(self._impact_cache) > cache_cap:
            self._impact_cache.clear()
        base = self._impact_cache.get(text)
        if base is None:
            base = self._base_impact(text)
            if cache_cap:
                if len(self._impact_cache) >= cache_cap:
                    self._impact_cache.clear()
                self._impact_cache[text] = base
        deltas = dict(base)
        # NURANI pilar A: "rasa cepat sebelum pikiran lambat" -- pengalaman
        # masa lalu dengan kata kunci yang sama menjadi prior. anticipate()
        # mengembalikan nol selama pilarnya mati, jadi jalur lexicon murni
        # tidak pernah berubah; clip di bawah tetap menjaga rentang [-1, +1].
        if self.nurani is not None and text:
            prior = self.nurani.anticipate(text)
            for d in DRIVES:
                if prior[d]:
                    deltas[d] += prior[d]
            # Lexicon kata dinamis (diasosiasikan NURANI.experience) memberi
            # sinyal tambahan yang kecil; kontribusi ini di-gate pilar A dan
            # dibatasi gain agar lexicon statis + model internal tetap utama.
            word_prior = self.nurani.anticipate_words(str(text))
            for d in DRIVES:
                if word_prior[d]:
                    deltas[d] += word_prior[d]
        self._working_memory_impact(str(text), deltas)
        # clip supaya tidak meledak
        for d in DRIVES:
            deltas[d] = jepit_drive(deltas[d])
        return deltas

    def project_outcome_to_drives(self, outcome: Any) -> Dict[str, float]:
        """Proyeksikan outcome (SimulationOutcome/dict) ke vektor drive_deltas."""
        from pycos.inti.naluri import _get_attr
        desc = _get_attr(outcome, "description", "")
        impact = float(_get_attr(outcome, "impact_score",
                        _get_attr(outcome, "impact", 0.0)) or 0.0)
        deltas = self.impact_of(desc)
        # Impak numerik outcome dibagi merata ke drive yang bergerak searah
        if abs(impact) > 1e-6:
            total = sum(abs(v) for v in deltas.values())
            if total < 1e-6:
                # deskripsi tak dikenal → dorong penguasaan dan keamanan sesuai tanda impak
                if impact > 0:
                    deltas["penguasaan"] += 0.4 * impact
                    deltas["keamanan"] += 0.2 * impact
                else:
                    deltas["keamanan"] += 0.4 * impact
                    deltas["koherensi"] += 0.1 * impact
            else:
                # skala agar vektor lexicon bercampur dengan impak Gaussian
                scale = 0.5 + 0.5 * min(1.0, abs(impact))
                for d in list(deltas.keys()):
                    deltas[d] *= scale
        return deltas

    def utility(self, outcome: Any, scale: Optional[float] = None) -> float:
        """Skor utilitas outcome (SimulationOutcome atau dict) — terbobot drive defisit.

        Dirancang agar callable(object) cocok dengan kontrak scoring_func
        Imagination (weighted_score memanggil scoring_func(outcome)).
        Skala `scale` menyejajarkan skor dengan rentang reward dunia; bila
        None dipakai estimate_scale() adaptif.
        """
        from pycos.inti.naluri import _get_attr
        desc = _get_attr(outcome, "description", "")
        # SimulationOutcome menyimpan impak sebagai `impact_score`; `impact`
        # dibaca sebagai fallback agar utilitas() tetap kompatibel dengan
        # dictionary/objek lain.
        impact_val = _get_attr(outcome, "impact_score",
                               _get_attr(outcome, "impact", 0.0)) or 0.0
        prob = _get_attr(outcome, "probability", 1.0)
        delay = _get_attr(outcome, "delay_to_impact", 0) or 0
        perspective = _get_attr(outcome, "perspective", "self")

        deltas = self.impact_of(desc)
        discount = 1.0 / ((1.0 + 0.15) ** max(0, delay))
        # Kontribusi Gaussian mentah dikecilkan; arti (deltas lexicon) adalah
        # pembawa nilai sesungguhan. Ini mencegah cabang dengan impak acak besar
        # tapi tanpa makna mendominasi pruning.
        base = float(impact_val) * 0.15
        lex_score = sum(deltas[d] * self._drive_weight_for_utility(d) for d in DRIVES)
        raw = (base + lex_score) * float(prob) * discount
        if perspective and str(perspective) != "self":
            raw += 0.15 * self.weights["afiliasi"] * float(prob)
        # Skala adaptif memperkecil perkalian mentah agar utilitas tak meledak
        # saat cabang ROOT dengan 1 outcome (n=1) diberi bobot statistik penuh.
        s = float(scale) if scale is not None else self.estimate_scale()
        return math.tanh(raw) * s

    def _drive_weight_for_utility(self, d: str) -> float:
        """Drive yang sedang defisit berbobot lebih besar (goal-biased)."""
        deficit = self.deficit(d)
        urgency_mult = 1.0 + self.urgency.get(d, 0.0)
        return self.weights[d] * (1.0 + 0.8 * deficit) * urgency_mult

    def scoring_func(self, scale: Optional[float] = None) -> Callable[[Any], float]:
        """Kembalikan closure scoring_func untuk imagination.simulate(...)."""
        def _score(outcome: Any) -> float:
            return self.utility(outcome, scale=scale)
        return _score

    # -------------------- skala adaptif --------------------
    def estimate_scale(self) -> float:
        return max(self.params["scale_floor"],
                   min(self.params["scale_ceiling"], self._scale))

    def _update_scale(self) -> None:
        """Sesuaikan skala berdasarkan rata-rata rasio |realita/prediksi| atas
        pasangan terakhir (dimaksimkan supaya prediksi mendekati nol tak
        menyebabkan pembagian liar).

        NURANI pilar B: bila kalibrasi berlapis aktif, rasio mentah tidak lagi
        diterima apa adanya -- skala diusulkan dari bagian pasangan terlama lalu
        HANYA dipakai bila hold-out sisanya benar-benar membaik, sehingga drift
        tanpa perbaikan nyata tertolak (lihat scale_from_holdout di NURANI)."""
        nur = self.nurani
        if nur is not None and nur.enabled("layered_calibration"):
            self._scale = nur.scale_from_holdout(self._pred_pairs, self._scale)[0]
            return
        if len(self._pred_pairs) < 10:
            return
        recent = self._pred_pairs[-50:]
        # Hanya pakai pasangan di mana |pred| dan |real| di atas lantai untuk
        # menghindari ledakan rasio saat prediksi ~0.
        usable = [(abs(p), abs(r)) for p, r in recent if abs(p) > 0.05 and abs(r) > 0.05]
        if len(usable) < 5:
            return
        mean_pred = sum(p for p, _ in usable) / len(usable)
        mean_real = sum(r for _, r in usable) / len(usable)
        if mean_pred < 1e-9:
            return
        ratio = mean_real / mean_pred
        # update teredam (mirip EMA) agar tak melompat
        alpha = self.params["scale_alpha"]
        self._scale *= 1.0 + alpha * (ratio - 1.0)
        self._scale = max(self.params["scale_floor"],
                          min(self.params["scale_ceiling"], self._scale))

    # -------------------- kalibrasi --------------------
    def observe_outcome(self,
                        prediksi: Any,
                        realita: Any,
                        action_id: Optional[str] = None,
                        tick: Optional[int] = None) -> Dict[str, Any]:
        """Bandingkan prediksi dengan realita; update koherensi + EMA error + skala.

        prediksi : SimulationOutcome.to_dict() atau outcome dengan .impact/.probability
        realita  : dict dengan "reward" (float) atau "impact" (float) atau "success" (bool).
                   Bisa juga berisi "drive_deltas": {drive: delta}.

        Lantai derau: tolerance = 0.20 + calibration_error; hanya error DI ATAS
        tolerance yang dianggap "kejutan sejati" dan menghukum koherensi. Ini
        adil di dunia berderau — prediksi terbaik pun tak bisa nol error.
        """
        from pycos.inti.naluri import _get_attr
        pred_impact = float(_get_attr(prediksi, "impact_score",
                             _get_attr(prediksi, "impact", 0.0)) or 0.0)
        pred_prob = float(_get_attr(prediksi, "probability", 1.0) or 1.0)
        now = self.tick_count if tick is None else int(tick)
        epistemic = float(_get_attr(prediksi, "uncertainty_epistemic",
                          _get_attr(prediksi, "epistemic_uncertainty", 1.0)) or 0.0)
        aleatoric = float(_get_attr(prediksi, "uncertainty_aleatoric",
                          _get_attr(prediksi, "aleatoric_uncertainty", 0.0)) or 0.0)
        epistemic = jepit_01(epistemic)
        aleatoric = jepit_01(aleatoric)
        # nilai realita
        dd: Dict[str, float] = {}
        if isinstance(realita, dict):
            real_impact = float(realita.get("reward",
                                  realita.get("impact",
                                  1.0 if realita.get("success") else -1.0)))
            dd = realita.get("drive_deltas") or {}
        else:
            real_impact = float(realita)

        s = self.estimate_scale()
        desc = _get_attr(prediksi, "description", "")
        delay = _get_attr(prediksi, "delay_to_impact", 0) or 0
        perspective = _get_attr(prediksi, "perspective", "self")
        discount = 1.0 / ((1.0 + 0.15) ** max(0, delay))
        lex = self.impact_of(desc)
        lex_score = sum(lex[d] * self.weights[d] for d in DRIVES)
        raw_pred = (pred_impact * 0.15 + lex_score) * pred_prob * discount
        if perspective and str(perspective) != "self":
            raw_pred += 0.15 * self.weights["afiliasi"] * pred_prob
        # pred_scaled = skor dalam skala dunia (pakai tanh agar clipping stabil
        # dan utilitas tak meledak walau ada 1 outcome dengan impak ekstrem)
        # (Bug-fix kecil: `s = self.estimate_scale()` sempat dihitung dua kali.)
        pred_scaled = math.tanh(raw_pred) * s
        real_norm = jepit_drive(real_impact)
        # Error diukur pada skala ternormalisasi (−1..1) agar kalibrator adil
        # terhadap cabang dengan magnitude berbeda.
        pred_unit = jepit_drive(raw_pred)
        real_unit = jepit_drive(real_impact)
        abs_error = abs(pred_unit - real_unit)

        # lantai derau (tolerance) — hanya surplus yang dihukum
        tolerance = float(self.params["calibration_tolerance"]) + self._calibration_ema
        surprise = max(0.0, abs_error - tolerance)

        alpha = self.params["calibration_alpha"]
        if self._calibration_samples == 0:
            self._calibration_ema = abs_error
        else:
            self._calibration_ema = (1 - alpha) * self._calibration_ema + alpha * abs_error
        self._calibration_samples += 1
        self._unverified_predictions = max(0, self._unverified_predictions - 1)

        # simpan pasangan untuk skala adaptif (pakai raw_pred, bukan yang diskalakan)
        self._pred_pairs.append((raw_pred, real_impact))
        _pangkas_memori(self._pred_pairs, "pred_pairs")
        if self._calibration_samples % 10 == 0:
            self._update_scale()

        # Update koherensi berdasarkan surprise (kejutan)
        if surprise > 0:
            self.levels["koherensi"] -= self.params["calibration_penalty"] * surprise
            self.levels["keingintahuan"] += 0.02 * min(1.0, surprise * 2)
        else:
            self.levels["koherensi"] += self.params["calibration_reward"] * (1.0 - abs_error)

        # terapkan drive_deltas eksplisit dari realita DENGAN SATIATION:
        # hanya tambahkan sebesar perubahan level yang benar-benar efektif.
        for d, v in dd.items():
            if d in self.levels:
                before = self.levels[d]
                after = jepit_drive(before + float(v))
                self.levels[d] = after
        # Jika realita positif → penguasaan naik; jika negatif → turun (efektif setelah jepit)
        eff_rew = jepit_drive(real_impact)
        before_p = self.levels["penguasaan"]
        after_p = jepit_drive(before_p + 0.08 * eff_rew)
        self.levels["penguasaan"] = after_p

        # EMPATI (gated): reaksi emosional terhadap realita. Kejutan besar =
        # takut + penasaran; hasil positif = senang; hasil negatif = sedih,
        # dan marah bila penguasaan memang sedang defisit (frustrasi).
        if self.params.get("enable_emosi", False):
            if surprise > 0.0:
                g = float(self.params["emosi_reaksi_kejutan"])
                self._emosi_naikkan("takut", g * surprise * 0.6,
                                    "kejutan prediksi")
                self._emosi_naikkan("penasaran", g * surprise,
                                    "kejutan prediksi")
            gr = float(self.params["emosi_reaksi_reward"])
            if eff_rew > 0.05:
                self._emosi_naikkan("senang", gr * eff_rew,
                                    "hasil nyata positif")
            elif eff_rew < -0.05:
                self._emosi_naikkan("sedih", gr * (-eff_rew) * 0.7,
                                    "hasil nyata negatif")
                self._emosi_naikkan(
                    "marah",
                    gr * (-eff_rew) * 0.5 * min(1.0, 2.0 * self.deficit("penguasaan")),
                    "frustrasi (penguasaan defisit)")

        # ------------------------------------------------------------------
        # NURANI (konsep 17): satu observasi = tiga pelajaran.
        #   pilar A: pengalaman (deskripsi prediksi -> dampak drive NYATA)
        #            masuk memori afektif, hanya bila realita membawa
        #            drive_deltas eksplisit (tanpa ground truth tak ada yang
        #            bisa dipelajari);
        #   pilar B: rapor kalibrasi berlapis menerima pasangan skala-unit,
        #            (probabilitas, sukses), dan galat per drive.
        # Keduanya no-op selama pilarnya mati, jadi jalur lama tidak berubah.
        # ------------------------------------------------------------------
        nur = self.nurani
        uncertainty_report = None
        structural_shock = None
        if nur is not None:
            sukses = None
            if isinstance(realita, dict):
                sukses = realita.get("success")
            if sukses is None:
                sukses = real_impact > 0.0
            if dd:
                nur.experience(str(_get_attr(prediksi, "description", "") or ""),
                               dd, tick=now)
            galat_per_drive = {d: abs(float(lex.get(d, 0.0)) - float(dd.get(d, 0.0)))
                               for d in DRIVES}
            structural_shock = nur.structural_surprise(
                surprise, galat_per_drive, tick=now)
            nur.record_observation(
                pred_unit=pred_unit, real_unit=real_unit, prob=pred_prob,
                success=bool(sukses), per_drive=galat_per_drive)
            uncertainty_report = nur.record_uncertainty(epistemic, aleatoric, tick=now)
            # PERSEPSI (pilar F): "belajar melihat" — saluran yang galatnya
            # kecil terbukti andal → sensitivitas d' naik (dan sebaliknya).
            if nur.enabled("perception"):
                nur.belajar_persepsi(galat_per_drive)
            # INTROSPEKSI (pilar G): metakognisi — confidence memprediksi correctness
            # (Fleming & Dolan 2012). Benar bila error <= tolerance (lantai derau).
            if nur.enabled("introspection"):
                benar = abs_error <= tolerance
                try:
                    nur.update_introspection(
                        levels=self.levels,
                        urgency=self.urgency,
                        valence=self.mood().valence,
                        arousal=self.mood().arousal,
                        tick=self.tick_count,
                        prediksi_benar=bool(benar),
                        confidence_pred=float(pred_prob),
                        rng=self._rng
                    )
                except Exception as _galat_diagnostik_132:
                    _diag.catat('naluri.Naluri.observe_outcome', "galat pada jalur fallback", galat=_galat_diagnostik_132, jalur=132)
                    pass

        credit_report = self.assign_delayed_credit(realita, action_id=action_id, tick=now)
        self._prediction_log.append({
            "t": now,
            "pred": pred_scaled, "real": real_norm, "error": abs_error,
            "surprise": surprise, "scale": s,
        })
        _pangkas_memori(self._prediction_log, "prediction_log")

        for d in DRIVES:
            self.levels[d] = jepit_drive(self.levels[d])

        return {"error": abs_error, "surprise": surprise,
                "calibration_ema": self._calibration_ema,
                "coherence_level": self.levels["koherensi"],
                "scale": s,
                "uncertainty": uncertainty_report,
                "structural_shock": structural_shock,
                "delayed_credit": credit_report}

    def calibration_error(self) -> float:
        return self._calibration_ema

    # -------------------- tidur: kognitif (endogen) & terjadwal --------------------
    def _fase_lokal(self, tick: Optional[int] = None) -> str:
        """Fase sirkadian lokal — tetap tersedia tanpa NURANI (fix #4).

        Rumusnya identik dengan Nurani.circadian_phase: satu "hari" =
        `circadian_period` tick, dibagi empat fase pagi/siang/sore/malam.
        """
        period = max(4, int(self.params.get("circadian_period", 24)))
        t = self.tick_count if tick is None else int(tick)
        per_fase = period / 4.0
        return ("pagi", "siang", "sore", "malam")[min(3, int((t % period) / per_fase))]

    def _sleep_cycle(self) -> int:
        """Indeks siklus sirkadian saat ini (satu siklus = satu 'hari')."""
        period = max(4, int(self.params.get("circadian_period", 24)))
        return self.tick_count // period

    @property
    def sleep_mode(self) -> str:
        """Mode tidur aktif: "kognitif" | "terjadwal" | "gabung"."""
        mode = str(self.params.get("sleep_mode", "kognitif")).lower()
        return SLEEP_MODE_ALIASES.get(mode, "kognitif")

    def set_sleep_mode(self, mode: str) -> str:
        """Atur mode tidur (fix #4).

        "kognitif"  : tidur endogen lama — energi/koherensi/backlog prediksi;
                      cocok untuk konsolidasi model, tapi bisa muncul kapan saja.
        "terjadwal" : sirkadian murni — NPC hanya tidur pada fase target
                      (default "malam"), sekali per siklus; alasan selalu
                      terbaca pemain dan refraktori tidak menahannya.
        "gabung"    : terjadwal ATAU kognitif (kognitif tetap direfraktori).
        """
        key = SLEEP_MODE_ALIASES.get(str(mode).lower())
        if key is None:
            raise ValueError(f"mode tidur tidak dikenal: {mode!r} "
                             f"(pilihan: {', '.join(SLEEP_MODES)})")
        self.params["sleep_mode"] = key
        return key

    def _scheduled_sleep(self) -> Tuple[bool, str]:
        """Tidur terjadwal: hanya pada fase sirkadian target, sekali per siklus."""
        target = str(self.params.get("sleep_scheduled_phase", "malam")).lower()
        fase = self._fase_lokal()
        if fase == target and self._slept_cycle != self._sleep_cycle():
            return True, (f"tidur terjadwal (fase sirkadian '{fase}', "
                          f"siklus ke-{self._sleep_cycle()})")
        return False, ""

    def sleep_status(self) -> Dict[str, Any]:
        """Info tidur untuk UI/skenario (fix #4 & #7): terbaca, bukan debug."""
        perlu, alasan = self.should_sleep()
        period = max(4, int(self.params.get("circadian_period", 24)))
        target = str(self.params.get("sleep_scheduled_phase", "malam")).lower()
        # jam dalam siklus (0..24) agar desainer bisa menampilkan "22:30"
        jam = 24.0 * ((self.tick_count % period) / period)
        return {
            "mode": self.sleep_mode,
            "perlu_tidur": perlu,
            "alasan": alasan or ("tertidur sesuai jadwal" if self._slept_cycle
                                 == self._sleep_cycle() and self.slept_count
                                 else ""),
            "fase": self._fase_lokal(),
            "fase_tidur": target,
            "jam_sirkadian": round(jam, 2),
            "periode": period,
            "slept_count": self.slept_count,
            "refraktori_sisa": max(0, int(self.params["sleep_refractory_ticks"])
                                   - (self.tick_count - self._last_sleep_tick)),
        }

    def should_sleep(self) -> Tuple[bool, str]:
        mode = self.sleep_mode
        # Tidur terjadwal (fix #4): murni sirkadian, tidak bergantung keadaan
        # drive dan tidak ditahan refraktori — jadwal harus deterministik dan
        # terbaca pemain ("NPC ini tidur karena malam", bukan "menghilang").
        if mode in ("terjadwal", "gabung"):
            terjadwal = self._scheduled_sleep()
            if terjadwal[0]:
                return terjadwal
            if mode == "terjadwal":
                return False, ""
        # ---- jalur kognitif (endogen): perilaku lama, tetap direfraktori ----
        # Refraktori: jangan tidur lagi segera setelah bangun
        if self.tick_count - self._last_sleep_tick < self.params["sleep_refractory_ticks"]:
            return False, ""
        e = self.levels["energi"]
        c = self.levels["koherensi"]
        if e < self.params["sleep_energy_threshold"]:
            return True, f"energi menipis (energi={e:+.2f})"
        if c < self.params["sleep_coherence_threshold"]:
            return True, f"koherensi ambruk (koherensi={c:+.2f})"
        # backlog prediksi yang belum diverifikasi → tidur untuk konsolidasi
        if self._unverified_predictions >= self.params["sleep_backlog_threshold"]:
            return True, (f"backlog prediksi belum terverifikasi "
                          f"(n={self._unverified_predictions})")
        # kalibrasi buruk
        if self._calibration_samples > 10 and self._calibration_ema > 0.55:
            return True, f"akumulasi kesalahan prediksi (err={self._calibration_ema:.2f})"
        nur = self.nurani
        if nur is not None and nur.enabled("layered_calibration"):
            # NURANI pilar B: satu skalar EMA tidak bisa membedakan "aku salah
            # besar di tiga prediksi terakhir" (tidur SEKARANG) dari "aku salah
            # sedang terus-menerus" (belum perlu tidur) -- spike & Brier.
            spike = nur.recent_spike()
            if spike > 0.0:
                return True, f"kejutan besar pada prediksi terakhir (err={spike:.2f})"
            rep_kal = nur.calibration_report()
            if (rep_kal.n_samples > 10
                    and rep_kal.brier_ema > self.params["sleep_brier_threshold"]):
                return True, ("kalibrasi probabilitas buruk "
                              f"(brier_ema={rep_kal.brier_ema:.2f})")
        if nur is not None:
            # NURANI pilar D: ritme sirkadian membuat tidur PREVENTIF mungkin.
            # Fase malam tidak memaksa tidur -- ia hanya menaikkan ambang
            # energi (mempersempit selisihnya), dan refraktori di atas tetap
            # berlaku, jadi organisme tidak berpindah tempat tidur setiap tick.
            geser = nur.night_energy_shift(self.tick_count)
            ambang = self.params["sleep_energy_threshold"] + geser
            if geser > 0.0 and e < ambang:
                # should_sleep() adalah kueri: dipanggil beberapa kali per tick
                # (status, snapshot, orkestra) jadi tidak ada counter yang
                # boleh dinaikkan di sini -- hanya keputusan & alasannya.
                return True, (f"tidur preventif (fase malam, energi={e:+.2f}, "
                              f"ambang={ambang:+.2f})")
        return False, ""

    def note_prediction(self) -> None:
        """Tandai bahwa satu prediksi Imajinasi baru dihasilkan tapi belum
        diverifikasi oleh observe_outcome()."""
        self._unverified_predictions += 1

    def dream_policy(self) -> Dict[str, Any]:
        """Parameter mimpi sesuai keadaan drive.

        Prioritaskan drive yang sedang defisit (priority_drives), agar sistem
        *memimpikan apa yang dibutuhkannya*.
        """
        mood = self.mood()
        base_dreams = 3 if self.stage == "dewasa" else (4 if self.stage == "remaja" else 5)
        urgency_factor = 1.0 + 0.5 * max(self.urgency["koherensi"], self.urgency["keamanan"])
        num_dreams = max(2, min(8, int(round(base_dreams * urgency_factor))))
        replay_strength = 0.4 + 0.3 * mood.arousal
        persist = self.stage == "dewasa"
        priority_drives = [g.drive for g in self.goals]
        kebijakan = {
            "num_dreams": num_dreams,
            "steps_per_dream": 8,
            "replay_strength": jepit(replay_strength, 0.2, 0.9),
            "persist": persist,
            "scenario_hint": self.goal_to_scenario(),
            "priority_drives": priority_drives,
            "multi_perspective": self.weights["afiliasi"] >= 1.0
                                 or "afiliasi" in priority_drives,
            "enable_sleeper": self.deficit("keamanan") > 0.2,
            "counterfactual": self.deficit("koherensi") > 0.15,
        }
        # EMPATI (gated): mimpi memproses emosi dominan — NPC yang takut
        # "bermimpi buruk", yang penasaran "bermimpi menjelajah".
        if self._emosi_aktif():
            dom = self.emosi_dominan(ambang=0.0)
            kebijakan["emosi_dominan"] = ({"emosi": dom[0],
                                           "intensitas": round(dom[1], 3)}
                                          if dom else None)
        return kebijakan

    def post_sleep(self, report: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        self.slept_count += 1
        self._last_sleep_tick = self.tick_count
        # Tandai siklus sirkadian ini sudah dipakai tidur terjadwal, supaya
        # NPC tidak tidur berulang kali pada "malam" yang sama (fix #4).
        self._slept_cycle = self._sleep_cycle()
        self.levels["energi"] = min(1.0, self.levels["energi"] + self.params["sleep_energy_gain"])
        self.levels["koherensi"] = min(1.0, self.levels["koherensi"] + self.params["sleep_coherence_gain"])
        self.levels["keamanan"] = min(1.0, self.levels["keamanan"] + 0.1)
        # Tidur mengenyangkan penasaran sedikit (mimpi memberi "wawasan" baru)
        self.levels["keingintahuan"] = max(-1.0, self.levels["keingintahuan"] - 0.1)
        # Kurangi kalibrasi error (mimpi mengonsolidasikan model)
        self._calibration_ema *= 0.7
        self._unverified_predictions = 0
        for d in DRIVES:
            self.urgency[d] *= 0.6
        if report:
            self.total_sleep_seconds += float(report.get("duration", 0.0))
        # KESADARAN: mimpi diproses saat tidur, lalu bangun dengan inersia &
        # laporan mimpi — ada kehidupan mental saat pemain tidak melihat.
        mimpi = None
        bangun = None
        if self._kesadaran_aktif() and self.kesadaran.enabled("dream_continuity"):
            try:
                mimpi = self.kesadaran.dream(saat_tidur=True)
                bangun = self.kesadaran.wake()
            except Exception as _galat_diagnostik_133:
                _diag.catat('naluri.Naluri.post_sleep', "galat pada jalur fallback", galat=_galat_diagnostik_133, jalur=133)
                mimpi = None
                bangun = None
        # KONSOLIDASI MEMORI (tidur): JEJAK memadatkan episode remeh menjadi
        # ringkasan (memori semantik) — hemat memori tanpa kehilangan "jiwa".
        konsolidasi = None
        if getattr(self, "jejak", None) is not None:
            try:
                konsolidasi = self.jejak.consolidate_memory()
            except Exception as _galat_diagnostik_134:
                _diag.catat('naluri.Naluri.post_sleep', "galat pada jalur fallback", galat=_galat_diagnostik_134, jalur=134)
                konsolidasi = None
        return {"energi": self.levels["energi"], "koherensi": self.levels["koherensi"],
                "konsolidasi": konsolidasi,
                "slept_count": self.slept_count, "mimpi": mimpi,
                "bangun": bangun,
                "wawasan_tidur": (copy.deepcopy(self.kesadaran.last_sleep_insight)
                                  if self._kesadaran_aktif()
                                  and self.kesadaran.last_sleep_insight else None)}

    # -------------------- pilihan aksi & reward intrinsik --------------------
    def _effective_delta(self, drive: str, v: float) -> float:
        """Kembalikan perubahan level YANG BENAR-BENAR tercapai setelah jepit.
        Inilah utilitas marginal (satiation): drive kenyang (level≈+1) tak lagi
        menarik bonus; drive di dasar (level≈-1) tak lagi takut hukuman."""
        before = self.levels.get(drive, 0.0)
        after = jepit_drive(before + float(v))
        return after - before

    def record_action(self,
                      action: str,
                      drive_effects: Optional[Mapping[str, Any]] = None,
                      eligibility: float = 1.0,
                      context: Any = None,
                      tick: Optional[int] = None) -> List[Dict[str, Any]]:
        """Mulai eligibility trace per aksi/drive untuk outcome tertunda.

        Aksi berulang mengakumulasi jejak hingga 1.0; aksi yang berbeda tetap
        hidup bersama sehingga credit dapat dibagi mundur menurut λ^Δt.
        """
        name = str(action or "").strip()
        if not name:
            return []
        base = jepit_01(float(eligibility))
        now = self.tick_count if tick is None else int(tick)
        if drive_effects is None:
            weights = {d: base for d in DRIVES}
        else:
            weights = {d: base * min(1.0, abs(float(drive_effects.get(d, 0.0) or 0.0)))
                       for d in DRIVES
                       if abs(float(drive_effects.get(d, 0.0) or 0.0)) >= 1e-6}
        if not weights:
            # Aksi netral tetap dapat menerima reward scalar tertunda.
            weights = {d: base for d in DRIVES}
        result: List[Dict[str, Any]] = []
        context_text = str(context or "")[:120]
        for drive, amount in weights.items():
            trace = next((x for x in self._eligibility_traces
                          if x.get("action") == name and x.get("drive") == drive), None)
            if trace is None:
                trace = {"action": name, "drive": drive, "eligibility": amount,
                         "effect": float((drive_effects or {}).get(drive, 0.0) or 0.0),
                         "tick": now, "last_tick": now, "context": context_text}
                self._eligibility_traces.append(trace)
            else:
                trace["eligibility"] = min(1.0, float(trace.get("eligibility", 0.0)) + amount)
                trace["effect"] = float((drive_effects or {}).get(drive,
                                              trace.get("effect", 0.0)) or 0.0)
                trace["tick"] = now
                trace["last_tick"] = now
                if context_text:
                    trace["context"] = context_text
            result.append(dict(trace))
        cap = max(1, int(self.params.get("eligibility_max_traces", 64)))
        if len(self._eligibility_traces) > cap:
            self._eligibility_traces.sort(
                key=lambda x: float(x.get("eligibility", 0.0)) *
                (1.0 + 0.1 * min(1.0, abs(float(x.get("effect", 0.0))))), reverse=True)
            del self._eligibility_traces[cap:]
        return result

    def _decay_eligibility_traces(self, steps: int = 1) -> None:
        lam = jepit_01(float(self.params.get("eligibility_lambda", 0.88)))
        minimum = max(0.0, float(self.params.get("eligibility_min", 0.015)))
        horizon = max(1, int(self.params.get("eligibility_horizon", 160)))
        kept: List[Dict[str, Any]] = []
        for trace in self._eligibility_traces:
            last = int(trace.get("last_tick", trace.get("tick", self.tick_count)))
            delta_t = max(0, self.tick_count - last)
            if delta_t == 0:
                delta_t = max(1, int(steps))
            trace["eligibility"] = float(trace.get("eligibility", 0.0)) * (lam ** delta_t)
            trace["last_tick"] = self.tick_count
            if (self.tick_count - int(trace.get("tick", self.tick_count)) <= horizon
                    and float(trace["eligibility"]) >= minimum):
                kept.append(trace)
        self._eligibility_traces = kept

    def assign_delayed_credit(self,
                              outcome: Any,
                              action_id: Optional[str] = None,
                              alpha: Optional[float] = None,
                              tick: Optional[int] = None) -> Dict[str, Any]:
        """Sebarkan reward nyata ke jejak aksi/drive yang masih eligible.

        Jejak tiap drive dinormalisasi di antara aksi yang memenuhi syarat;
        nilai aksi (Q) dan nilai per-drive diperbarui secara proporsional.
        """
        now = self.tick_count if tick is None else int(tick)
        if isinstance(outcome, Mapping):
            raw_dd = outcome.get("drive_deltas")
            drive_targets = ({d: float(raw_dd.get(d, 0.0) or 0.0) for d in DRIVES}
                             if isinstance(raw_dd, Mapping)
                             else self.project_outcome_to_drives(outcome))
            explicit_scalar = outcome.get("reward", outcome.get("impact"))
            if explicit_scalar is None:
                success = outcome.get("success")
                if success is not None:
                    explicit_scalar = 1.0 if success else -1.0
                else:
                    weights = {d: abs(float(drive_targets.get(d, 0.0))) for d in DRIVES}
                    denom = sum(weights.values())
                    explicit_scalar = (sum(float(drive_targets.get(d, 0.0)) * weights[d]
                                           for d in DRIVES) / denom if denom > 0.0 else 0.0)
            scalar_target = jepit_drive(float(explicit_scalar))
        else:
            scalar_target = jepit_drive(float(outcome))
            drive_targets = self.project_outcome_to_drives({"impact": scalar_target})
        traces = [x for x in self._eligibility_traces
                  if float(x.get("eligibility", 0.0)) > 0.0
                  and (action_id is None or str(x.get("action")) == str(action_id))]
        if not traces:
            self._last_credit_assignments = []
            return {"assigned": 0, "action_id": action_id,
                    "drive_targets": drive_targets, "assignments": []}
        rate = (float(self.params.get("eligibility_learning_alpha", 0.20))
                if alpha is None else float(alpha))
        rate = jepit_01(rate)
        total_per_drive = {d: sum(float(x.get("eligibility", 0.0))
                                  for x in traces if x.get("drive") == d)
                           for d in DRIVES}
        by_action: Dict[str, Dict[str, Any]] = {}
        for trace in traces:
            name = str(trace.get("action", ""))
            drive = str(trace.get("drive", ""))
            elig = max(0.0, float(trace.get("eligibility", 0.0)))
            if not name or drive not in DRIVES or elig <= 0.0:
                continue
            item = by_action.setdefault(name, {"eligibility": 0.0,
                                               "drive_weights": {d: 0.0 for d in DRIVES}})
            item["eligibility"] += elig
            item["drive_weights"][drive] += elig
        total_action_weight = sum(x["eligibility"] for x in by_action.values()) or 1.0
        assignments: List[Dict[str, Any]] = []
        for name, item in by_action.items():
            share = item["eligibility"] / total_action_weight
            slot = self._action_values.setdefault(name, {
                "value": 0.0, "n": 0, "last_t": now,
                "drive_values": {d: 0.0 for d in DRIVES},
                "drive_n": {d: 0 for d in DRIVES},
            })
            old_value = float(slot.get("value", 0.0))
            slot["value"] = old_value + rate * share * (scalar_target - old_value)
            slot["n"] = int(slot.get("n", 0)) + 1
            slot["last_t"] = now
            per_drive_credit: Dict[str, float] = {}
            for d, weight in item["drive_weights"].items():
                if weight <= 0.0:
                    continue
                denom = total_per_drive.get(d, 0.0)
                portion = weight / denom if denom > 0 else 0.0
                target = jepit_drive(float(drive_targets.get(d, 0.0)))
                values = slot.setdefault("drive_values", {x: 0.0 for x in DRIVES})
                counts = slot.setdefault("drive_n", {x: 0 for x in DRIVES})
                old = float(values.get(d, 0.0))
                values[d] = old + rate * portion * (target - old)
                counts[d] = int(counts.get(d, 0)) + 1
                per_drive_credit[d] = round(rate * portion * target, 6)
            assignments.append({"action": name, "share": round(share, 4),
                                "q_value": round(float(slot["value"]), 4),
                                "drive_credit": per_drive_credit})
        self._last_credit_assignments = assignments[-32:]
        return {"assigned": len(assignments), "action_id": action_id,
                "drive_targets": drive_targets,
                "assignments": copy.deepcopy(self._last_credit_assignments)}

    def choose_action(self, candidates: List[Dict[str, Any]],
                      goal_bias: bool = True,
                      record_eligibility: bool = True) -> Dict[str, Any]:
        """Pilih aksi dengan utilitas tertinggi berdasarkan drive_deltas.

        candidates: list of dict {name, drive_effects: {drive: delta}, [prob], [cost]}
        Mengembalikan dict {action, score, candidate, ranked, ...}.

        Bila goal_bias=True, urgensi goal aktif melipatgandakan bobot drive
        yang sedang lapar (imp *= 1 + urgency(drive)). Memakai satiation:
        yang dihitung adalah perubahan level efektif setelah jepit.

        NURANI pilar D: bila dua goal berurgensi tinggi menghendaki hal yang
        berlawanan (satu kandidat menaikkan drive A sambil menurunkan B,
        kandidat lain sebaliknya), weighted-sum linear menghasilkan skor yang
        saling meniadakan dan keputusan menjadi flip-flop. Saat konflik
        terdeteksi, peringkat diganti: aksi yang menggerakkan KEDUA drive
        berlawanan ke arah positif (kompromi) didahulukan, lalu lexicographic
        urgency x bobot pada drive paling lapar, dengan weighted-sum lama
        sebagai pemecah seri. Tanpa flag enable_conflict_resolution jalur ini
        tidak tersentuh.
        """
        if not candidates:
            return {"action": None, "score": 0.0, "reason": "tidak ada kandidat"}
        for c in candidates:
            nama_c = c.get("name") if isinstance(c, Mapping) else None
            if not isinstance(nama_c, str) or not nama_c.strip():
                raise ValueError("kandidat aksi wajib berupa mapping dengan "
                                 "'name' string non-kosong; dapat {!r}".format(c))
            if "drive_effects" not in c:
                # Kunci lain (mis. 'effects') tidak dibaca: kandidat itu skornya 0.
                _diag.catat("Naluri.choose_action",
                            "kandidat tanpa 'drive_effects' dinilai 0",
                            aksi=nama_c)
        scored = []
        # EMPATI: prior sosial & bias emosi (keduanya gated; mati = jalur lama)
        sosial_aktif = (self.nurani is not None
                        and self.nurani.enabled("social_memory"))
        emosi_aktif = self._emosi_aktif()
        # PERSEPSI (Gibson): kebutuhan membuat kemungkinan aksi MENONJOL —
        # bonus salience opsional (persepsi_afordansi > 0), di luar goal_bias.
        afordansi_aktif = (self._persepsi_aktif()
                           and float(self.params.get("persepsi_afordansi",
                                                     0.0)) > 0.0)
        active_subgoal = self._active_subgoal()
        for c in candidates:
            effects = c.get("drive_effects", {}) or {}
            # Kandidat boleh menyebut "target": entitas sosial. Prior relasi
            # (valensi/kepercayaan) digeser ke efek drive SEBELUM satiation,
            # sehingga "mengobrol dengan teman" mengenyangkan afiliasi lebih
            # besar daripada "mengobrol dengan orang asing".
            if sosial_aktif and c.get("target") is not None:
                prior = self.nurani.social_prior(c.get("target"))
                if prior:
                    effects = dict(effects)
                    for d, pv in prior.items():
                        if d in self.levels:
                            effects[d] = float(effects.get(d, 0.0)) + pv
            prob = float(c.get("prob", 1.0))
            cost = float(c.get("cost", 0.0))
            s = 0.0
            # biaya energi dihitung dengan satiation juga: eff_cost adalah
            # perubahan level energi yang TERJADI (negatif saat cost>0) sehingga
            # menambah `s` memang MENGURANGI skor. (Bug-fix: sebelumnya ada
            # pembalikan tanda yang menjadikan aksi berbiaya malah diberi bonus.)
            eff_cost = self._effective_delta("energi", -cost * 0.5)
            for d in DRIVES:
                raw = float(effects.get(d, 0.0))
                eff = self._effective_delta(d, raw)
                w = self.weights[d]
                if goal_bias:
                    w *= (1.0 + self.urgency.get(d, 0.0))
                if active_subgoal is not None and d == active_subgoal.drive:
                    w *= (1.0 + float(self.params.get("subgoal_bias", 0.18))
                          * max(0.0, float(active_subgoal.urgency)))
                if emosi_aktif:
                    w *= self._emosi_weight_bias(d)
                s += eff * w * prob
            s += eff_cost * self.weights["energi"] * prob
            if afordansi_aktif:
                s += (float(self.params["persepsi_afordansi"])
                      * self._salience_kandidat(effects) * prob)
            s += self._working_memory_action_bias(effects)
            action_name = str(c.get("name", ""))
            learned_value = float((self._action_values.get(action_name) or {}).get("value", 0.0))
            s += float(self.params.get("eligibility_value_weight", 0.45)) * learned_value
            evaluated = c
            if self._kesadaran_aktif():
                try:
                    own_goal = self.kesadaran.free_will_action_bonus(c)
                    own_bonus = float(own_goal.get("bonus", 0.0))
                    if own_bonus > 0.0:
                        s += own_bonus
                        evaluated = dict(c)
                        evaluated["_free_will_bonus"] = own_bonus
                        evaluated["_free_will_goal_id"] = own_goal.get("goal_id")
                        evaluated["_free_will_goal"] = own_goal.get("tujuan")
                except Exception as _galat_diagnostik_135:
                    _diag.catat('naluri.Naluri.choose_action', "galat pada jalur fallback", galat=_galat_diagnostik_135, jalur=135)
                    pass
            scored.append((s, evaluated))
        # ---------------- NURANI pilar D: mediasi konflik antar-drive --------
        nur = self.nurani
        konflik = None
        if (nur is not None and nur.enabled("conflict_resolution")
                and len(self.goals) >= 2):
            konflik = nur.detect_conflict(self.goals, [c for _, c in scored])
        if konflik is not None and konflik.get("ada"):
            d1, d2 = konflik["drive"]
            dominan = (d1 if self.urgency.get(d1, 0.0) >= self.urgency.get(d2, 0.0)
                       else d2)
            w_dom = self.weights[dominan] * (1.0 + self.urgency.get(dominan, 0.0))
            ulang: List[Tuple[float, float, float, float, Dict[str, Any]]] = []
            for s, c in scored:
                effects = c.get("drive_effects", {}) or {}
                # probabilitas kandidat ikut menilai SEMUA suku kunci
                # lexicographic (efek maupun bonus kompromi): aksi "heroik"
                # yang nyaris tak mungkin terjadi tidak boleh menang hanya
                # karena efeknya besar -- kunci ini harus tetap berskala
                # nilai-harapan, sama seperti weighted-sum di jalur normal.
                prob_c = float(c.get("prob", 1.0))
                bonus = nur.compromise_bonus(effects, d1, d2) * prob_c
                lex = (self._effective_delta(dominan,
                                             float(effects.get(dominan, 0.0)))
                       * w_dom * prob_c + bonus)
                # Kunci utama: kandidat yang mendamaikan KEDUA drive
                # didahulukan. Tanpa itu bonus compromise_bonus x min(e1, e2)
                # tidak pernah cukup mengalahkan kandidat serakah, sehingga
                # keputusan tetap melukai drive lapar seperti weighted-sum
                # (angkanya di Ringkasan konsep 17 di folder analysis).
                own_bonus = float(c.get("_free_will_bonus", 0.0) or 0.0)
                # Setelah kewajiban mencari kompromi drive, tujuan yang dipilih
                # sendiri menjadi tie-breaker tersendiri sebelum utilitas drive.
                ulang.append((1.0 if bonus > 0.0 else 0.0,
                              own_bonus, lex, s, c))
            ulang.sort(key=lambda x: (x[0], x[1], x[2], x[3]), reverse=True)
            _, _, lex_best, best_score, best = ulang[0]
            nur.note_conflict(konflik, resolved=True, tick=self.tick_count)
            if record_eligibility and best.get("name"):
                trace_effects = dict(best.get("drive_effects", {}) or {})
                if float(best.get("cost", 0.0) or 0.0) > 0.0:
                    trace_effects["energi"] = trace_effects.get("energi", 0.0) - 0.5 * float(best["cost"])
                self.record_action(str(best.get("name")), trace_effects,
                                   context=self.context_aktif[0].get("stimulus", "")
                                   if self.context_aktif else "")
            return {
                "action": best.get("name"),
                "score": best_score,
                "candidate": best,
                # `ranked` tetap memakai weighted-sum agar dibandingkan dengan
                # jalur normal; kunci lexicographic dilaporkan terpisah.
                "ranked": [(round(float(s), 4), c.get("name"))
                           for _, _, _, s, c in ulang],
                "curiosity": self.deficit("keingintahuan"),
                "uncertainty": self._calibration_ema,
                "konflik": konflik,
                "skor_leksikografis": round(float(lex_best), 4),
            }
        scored.sort(key=lambda x: x[0], reverse=True)
        best_score, best = scored[0]
        if record_eligibility and best.get("name"):
            trace_effects = dict(best.get("drive_effects", {}) or {})
            if float(best.get("cost", 0.0) or 0.0) > 0.0:
                trace_effects["energi"] = trace_effects.get("energi", 0.0) - 0.5 * float(best["cost"])
            self.record_action(str(best.get("name")), trace_effects,
                               context=self.context_aktif[0].get("stimulus", "")
                               if self.context_aktif else "")
        return {
            "action": best.get("name"),
            "score": best_score,
            "candidate": best,
            "ranked": [(round(float(s), 4), c.get("name")) for s, c in scored],
            "curiosity": self.deficit("keingintahuan"),
            "uncertainty": self._calibration_ema,
        }

    def reward_for(self, deltas: Dict[str, float]) -> float:
        """Reward intrinsik dari perubahan drive — dipakai untuk memberi reward
        ke NeuralNode bandit di SamanticGarden tanpa reward eksternal.
        Memakai satiation agar drive kenyang tidak menghasilkan reward.

        NURANI pilar D: keadaan flow (valensi cukup tinggi, gairah tetap
        rendah) menambah bonus reward intrinsik -- organisme menghargai
        keadaan terserap. Bonus ini terkunci enable_flow_state sendiri karena
        menambah angka pada skor yang sebelumnya murni satiation.
        """
        # Kunci asing dan nilai non-finite ditolak, bukan dihitung sebagai 0 diam-diam.
        _periksa_kunci_drive(deltas, "reward_for")
        r = 0.0
        for d, dv in deltas.items():
            dv = float_hingga(dv, "reward_for[{}]".format(d))
            eff = self._effective_delta(d, dv)
            w = self.weights[d] * (1.0 + self.urgency.get(d, 0.0))
            r += eff * w
        nur = self.nurani
        if nur is not None:
            mood = self.mood()
            r += nur.flow_reward_bonus(mood.valence, mood.arousal)
        return r

    # -------------------- EMPATI: mesin emosi diskret --------------------
    def _emosi_aktif(self) -> bool:
        return bool(self.params.get("enable_emosi", False))

    def enable_emosi(self, aktif: bool = True) -> bool:
        """Nyalakan/matikan mesin emosi. Mematikan mengosongkan intensitas
        agar keadaan tidak 'bekas' saat dinyalakan lagi."""
        self.params["enable_emosi"] = bool(aktif)
        if not aktif:
            for e in EMOSI:
                self.emosi[e] = 0.0
            self._emosi_val_prev = None
            self._emosi_keamanan_prev = None
            self._emosi_ingin_prev = None
        return bool(self.params["enable_emosi"])

    def _valensi_mentah(self) -> float:
        """Valensi dari drive saja (tanpa campuran emosi) — untuk apresiasi."""
        wsum = sum(self.weights.values())
        return sum(self.levels[d] * self.weights[d] for d in DRIVES) / max(1e-6, wsum)

    def _emosi_naikkan(self, emosi: str, jumlah: float, alasan: str = "") -> float:
        """Tambah intensitas satu emosi (clip [0..1]) + jejak log terbatas."""
        e = EMOSI_ALIASES.get(str(emosi).lower())
        if e is None or jumlah <= 0.0:
            return self.emosi.get(e or "", 0.0)
        before = self.emosi[e]
        baru = jepit_01(before + float(jumlah))
        if alasan and baru - before > 1e-4:
            self._emosi_log.append({
                "t": self.tick_count, "emosi": e,
                "delta": round(baru - before, 4), "nilai": round(baru, 4),
                "alasan": str(alasan)[:60]})
            _pangkas_memori(self._emosi_log, "emosi_log", self._EMOSI_LOG_MAX)
        self.emosi[e] = baru
        return baru

    def _emosi_peluruh(self, steps: int = 1, multiplier: float = 1.0) -> None:
        """Peluruhan eksponensial; distraction dapat menaikkan decay sementara."""
        decay = jepit(float(self.params.get("emosi_decay", 0.03))
                               * max(1.0, float(multiplier)), 0.0, 0.95)
        sisa = (1.0 - decay) ** max(1, int(steps))
        ambang = float(self.params.get("emosi_ambang", 0.02))
        for e in EMOSI:
            v = self.emosi[e] * sisa
            self.emosi[e] = 0.0 if v < ambang else v

    def _emosi_apresiasi(self, val_sebelum: float, keam_sebelum: float,
                          ingin_sebelum: float) -> None:
        """Apresiasi: emosi lahir dari PERUBAHAN keadaan, bukan level absolut.

        Δvalensi+  → senang; Δvalensi− → sedih (atau marah bila ada frustrasi
        penguasaan/keamanan); Δdefisit keamanan+ → takut; Δkeingintahuan+ →
        penasaran (hal baru tersulut).
        """
        v_now = self._valensi_mentah()
        dv = v_now - val_sebelum
        gain = float(self.params["emosi_gain_valence"])
        if dv > 0.01:
            self._emosi_naikkan("senang", gain * dv, "keadaan membaik")
        elif dv < -0.01:
            frustrasi = (self.deficit("penguasaan") > 0.2
                         or self.deficit("keamanan") > 0.3)
            if frustrasi:
                self._emosi_naikkan("marah", gain * (-dv) * 0.7,
                                    "keadaan memburuk + frustrasi")
                self._emosi_naikkan("sedih", gain * (-dv) * 0.4,
                                    "keadaan memburuk")
            else:
                self._emosi_naikkan("sedih", gain * (-dv), "keadaan memburuk")
        keam_now = max(0.0, -self.levels["keamanan"])
        dk = keam_now - keam_sebelum
        if dk > 0.01:
            self._emosi_naikkan("takut",
                                float(self.params["emosi_gain_keamanan"]) * dk,
                                "defisit keamanan naik")
        di = self.levels["keingintahuan"] - ingin_sebelum
        if di > 0.01:
            self._emosi_naikkan("penasaran",
                                float(self.params["emosi_gain_keingintahuan"]) * di,
                                "keingintahuan tersulut")
        self._emosi_val_prev = v_now
        self._emosi_keamanan_prev = keam_now
        self._emosi_ingin_prev = self.levels["keingintahuan"]

    def feel(self, emosi: str, intensitas: float, alasan: str = "") -> float:
        """Suntik emosi eksplisit dari sistem game/dialog (gated enable_emosi).

        `intensitas` diskalakan `emosi_gain_event`; alias Inggris diterima
        (fear/anger/joy/sad/curious). Mengembalikan intensitas hasilnya.
        """
        if not self._emosi_aktif():
            return 0.0
        return self._emosi_naikkan(
            emosi, float(intensitas) * float(self.params["emosi_gain_event"]),
            alasan or "rangsangan eksternal")

    def emosi_state(self) -> Dict[str, float]:
        """Salinan intensitas seluruh emosi (dibulatkan, JSON-safe)."""
        return {e: round(self.emosi[e], 4) for e in EMOSI}

    def emosi_dominan(self, ambang: Optional[float] = None
                       ) -> Optional[Tuple[str, float]]:
        """(emosi, intensitas) terkuat di atas ambang; None bila netral/mati."""
        if not self._emosi_aktif():
            return None
        batas = EMOSI_HUD_THRESHOLD if ambang is None else float(ambang)
        e = max(EMOSI, key=lambda x: self.emosi[x])
        return (e, self.emosi[e]) if self.emosi[e] >= batas else None

    def enable_coping(self, aktif: bool = True) -> bool:
        """Nyalakan/matikan teknik coping; mati bawaan agar kompatibel."""
        self.params["enable_coping"] = bool(aktif)
        if not aktif:
            self._coping_focus = None
        return bool(self.params["enable_coping"])

    def _coping_gate(self) -> Tuple[bool, float, str]:
        if not bool(self.params.get("enable_coping", False)):
            return False, 0.0, "coping dinonaktifkan"
        if not self._emosi_aktif():
            return False, 0.0, "mesin emosi dinonaktifkan"
        readiness = (0.5 * (self.levels.get("energi", 0.0) + 1.0) / 2.0
                     + 0.5 * (self.levels.get("koherensi", 0.0) + 1.0) / 2.0)
        readiness = jepit_01(readiness)
        threshold = jepit_01(float(self.params.get("coping_gate_min", 0.14)))
        if readiness < threshold:
            return False, readiness, "kapasitas energi/koherensi terlalu rendah"
        return True, readiness, "siap"

    def _coping_reduce_emotion(self, emotion: str, amount: float, reason: str) -> float:
        before = float(self.emosi.get(emotion, 0.0))
        after = max(0.0, before - max(0.0, float(amount)))
        self.emosi[emotion] = after
        if before - after > 1e-5:
            self._emosi_log.append({"t": self.tick_count, "emosi": emotion,
                                    "delta": round(after - before, 4),
                                    "nilai": round(after, 4),
                                    "alasan": str(reason)[:60]})
            _pangkas_memori(self._emosi_log, "emosi_log", self._EMOSI_LOG_MAX)
        return before - after

    def reappraise(self,
                   emotion: Optional[str] = None,
                   interpretation: str = "",
                   strength: float = 0.5) -> Dict[str, Any]:
        """Reappraisal: turunkan emosi negatif lewat reinterpretasi, gated."""
        allowed, readiness, reason = self._coping_gate()
        if not allowed:
            return {"applied": False, "reason": reason, "readiness": round(readiness, 3)}
        key = EMOSI_ALIASES.get(str(emotion or "").lower()) if emotion else None
        if key is None:
            key = max(("takut", "marah", "sedih"), key=lambda e: self.emosi[e])
        if key not in ("takut", "marah", "sedih") or self.emosi[key] <= 0.0:
            return {"applied": False, "reason": "tidak ada emosi negatif untuk dinilai ulang",
                    "readiness": round(readiness, 3)}
        strength = jepit_01(float(strength))
        amount = self.emosi[key] * strength * float(self.params.get("coping_reappraise_gain", 0.35)) * readiness
        reduced = self._coping_reduce_emotion(key, amount, "reappraisal")
        self.delta("koherensi", 0.025 * reduced, reason="reappraisal: pemaknaan ulang")
        if interpretation:
            self._coping_focus = {"topic": str(interpretation)[:120], "remaining": 3,
                                  "emotion_decay_multiplier": 1.0}
        return {"applied": reduced > 0.0, "emotion": key,
                "reduced": round(reduced, 4), "remaining": round(self.emosi[key], 4),
                "readiness": round(readiness, 3), "interpretation": str(interpretation)[:120]}

    def suppress(self,
                 emotion: Optional[str] = None,
                 strength: float = 0.5) -> Dict[str, Any]:
        """Suppress: redam ekspresi emosi sementara dengan biaya koherensi."""
        allowed, readiness, reason = self._coping_gate()
        if not allowed:
            return {"applied": False, "reason": reason, "readiness": round(readiness, 3)}
        key = EMOSI_ALIASES.get(str(emotion or "").lower()) if emotion else None
        if key is None:
            key = max(EMOSI, key=lambda e: self.emosi[e])
        if self.emosi.get(key, 0.0) <= 0.0:
            return {"applied": False, "reason": "emosi target kosong",
                    "readiness": round(readiness, 3)}
        strength = jepit_01(float(strength))
        reduced = self._coping_reduce_emotion(key,
                    self.emosi[key] * strength * readiness, "suppression")
        cost = float(self.params.get("coping_suppression_cost", 0.08)) * reduced
        if cost > 0.0:
            self.delta("koherensi", -cost, reason="biaya suppression")
        return {"applied": reduced > 0.0, "emotion": key,
                "reduced": round(reduced, 4), "coherence_cost": round(cost, 4),
                "remaining": round(self.emosi[key], 4), "readiness": round(readiness, 3)}

    def distract(self,
                 topic: str,
                 duration: int = 6,
                 strength: float = 0.6) -> Dict[str, Any]:
        """Distraction: alihkan fokus dan percepat decay emosi selama beberapa tick."""
        allowed, readiness, reason = self._coping_gate()
        if not allowed:
            return {"applied": False, "reason": reason, "readiness": round(readiness, 3)}
        topic = str(topic or "").strip()
        if not topic:
            return {"applied": False, "reason": "topik fokus kosong",
                    "readiness": round(readiness, 3)}
        strength = jepit_01(float(strength))
        multiplier = 1.0 + (float(self.params.get("coping_distraction_decay", 2.5)) - 1.0) * strength * readiness
        self._coping_focus = {"topic": topic[:120],
                              "remaining": max(1, min(100, int(duration))),
                              "emotion_decay_multiplier": max(1.0, multiplier)}
        self.levels["keingintahuan"] = jepit_drive(self.levels["keingintahuan"] + float(self.params.get("coping_focus_gain", 0.15))
            * strength * readiness)
        return {"applied": True, "topic": topic[:120],
                "remaining": self._coping_focus["remaining"],
                "emotion_decay_multiplier": round(multiplier, 3),
                "readiness": round(readiness, 3)}

    def _advance_coping_focus(self, steps: int = 1) -> None:
        if not self._coping_focus:
            return
        self._coping_focus["remaining"] = int(self._coping_focus.get("remaining", 0)) - max(1, int(steps))
        if self._coping_focus["remaining"] <= 0:
            self._coping_focus = None

    def coping_state(self) -> Dict[str, Any]:
        return {"enabled": bool(self.params.get("enable_coping", False)),
                "focus": copy.deepcopy(self._coping_focus)}

    def _emosi_weight_bias(self, d: str) -> float:
        """Pengali keputusan dengan gerbang/plafon yang dapat diubah Residu.

        Residu tidak pernah ditambahkan pada bobot. Ia mengubah fungsi yang
        membaca emosi: nilai di bawah ambang hilang dari keputusan dan nilai
        di atas plafon dipotong sebelum rumus lama dijalankan.
        """
        mentah = self.emosi
        o = getattr(self, "_organik", None)
        residu = getattr(o, "residu", None) if o is not None else None
        dasar_ambang = float(self.params.get("emosi_ambang", 0.02))
        e: Dict[str, float] = {}
        for nama, nilai in mentah.items():
            ambang = (residu.ambang_dimodifikasi(nama, dasar_ambang)
                      if residu is not None else dasar_ambang)
            langit = (residu.langit_dimodifikasi(nama, 1.0)
                      if residu is not None else 1.0)
            e[nama] = 0.0 if float(nilai) < ambang else min(float(nilai), langit)
        if d == "keamanan":
            hasil = ((1.0 + 0.6 * e["takut"])
                     * (1.0 - 0.3 * e["marah"])
                     * (1.0 - 0.15 * e["penasaran"]))
        elif d == "penguasaan":
            hasil = 1.0 + 0.4 * e["marah"]
        elif d == "afiliasi":
            hasil = (1.0 + 0.25 * e["senang"]) * (1.0 + 0.3 * e["sedih"])
        elif d == "keingintahuan":
            hasil = 1.0 + 0.5 * e["penasaran"]
        elif d == "energi":
            hasil = max(0.2, 1.0 + 0.2 * e["takut"] - 0.2 * e["sedih"])
        else:
            hasil = 1.0
        if residu is not None:
            # Plafon drive membatasi ruang keputusan; bukan bias yang dijumlah.
            plafon = residu.langit_dimodifikasi(d, max(1.0, hasil))
            hasil = min(hasil, plafon)
        return max(0.0, hasil)

    def mode_npc(self, aktif: bool = True) -> Dict[str, Any]:
        """Satu sakelar 'mode NPC penuh' untuk desainer:
        tidur terjadwal + mesin emosi + memori sosial & sirkadian NURANI.
        `aktif=False` mengembalikan ke perilaku konservatif."""
        if self.nurani is not None:
            self.nurani.set_pillars(("social_memory", "circadian"), aktif=aktif)
        self.enable_emosi(aktif)
        self.set_sleep_mode("terjadwal" if aktif else "kognitif")
        return {"sleep_mode": self.sleep_mode,
                "emosi": self._emosi_aktif(),
                "social": (self.nurani is not None
                           and self.nurani.enabled("social_memory"))}

    # -------------------- EMPATI: relasi sosial (pilar E NURANI) --------------------
    def _relasi_netral(self, entitas: Any, nama: str = "") -> Dict[str, Any]:
        return {"id": str(entitas), "nama": nama, "valensi": 0.0,
                "kepercayaan": 0.0, "akrab": 0.0, "n": 0, "last_t": 0,
                "dikenal": False}

    def kenal(self, entitas: Any, nama: Optional[str] = None) -> Dict[str, Any]:
        """Daftarkan entitas (pemain / NPC lain / faksi) ke memori sosial.

        Netral bila NURANI tidak terpasang (mode berdiri sendiri) — pemanggil
        tidak perlu memeriksa apa pun.
        """
        if self.nurani is None:
            r = self._relasi_netral(entitas, nama or "")
            r["catatan"] = "NURANI tidak terpasang"
            return r
        return self.nurani.meet(entitas, nama=nama, tick=self.tick_count)

    def observe_other_belief(self,
                            other_id: Any,
                            drive: str,
                            value: float,
                            confidence: float = 0.35) -> Dict[str, Any]:
        """Tambahkan observasi perilaku ke sparse Theory of Mind NURANI."""
        if self.nurani is None:
            return {"other_id": str(other_id), "drive": drive,
                    "estimate": jepit_drive(float(value)),
                    "confidence": 0.0, "basis": "NURANI_unavailable", "n": 0}
        return self.nurani.observe_other_belief(other_id, drive, value,
                                                confidence=confidence,
                                                tick=self.tick_count)

    def estimate_other_belief(self, other_id: Any, drive: str) -> Dict[str, Any]:
        """Estimasi belief NPC lain dari observasi + prior false-consensus lemah."""
        if self.nurani is None:
            return {"other_id": str(other_id), "drive": drive, "estimate": 0.0,
                    "confidence": 0.0, "basis": "NURANI_unavailable", "n": 0}
        return self.nurani.estimate_other_belief(other_id, drive)

    def relasi(self, entitas: Any) -> Dict[str, Any]:
        """Snapshot relasi dengan satu entitas (netral bila tak dikenal)."""
        if self.nurani is None:
            return self._relasi_netral(entitas)
        return self.nurani.relationship(entitas)

    def label_relasi(self, entitas_atau_relasi: Any) -> str:
        """Label terbaca pemain: asing/netral/akrab/suka/percaya/curiga/benci."""
        r = (entitas_atau_relasi if isinstance(entitas_atau_relasi, dict)
             else self.relasi(entitas_atau_relasi))
        if not r.get("dikenal"):
            return "asing"
        v = float(r.get("valensi", 0.0))
        t = float(r.get("kepercayaan", 0.0))
        a = float(r.get("akrab", 0.0))
        if v <= -0.4:
            return "benci"
        if t <= -0.3:
            return "curiga"
        if t >= 0.5 and v >= 0.3:
            return "percaya"
        if v >= 0.4:
            return "suka"
        if a >= 0.6:
            return "akrab"
        return "netral"

    def catat_utang(self, entitas: Any, isi: str, bobot: float = 1.0,
                    jenis: str = "janji") -> Dict[str, Any]:
        """Catat utang emosional (janji/permintaan yang belum ditepati)."""
        if self.nurani is None:
            return {}
        return self.nurani.tambah_utang(entitas, isi, bobot=bobot, jenis=jenis,
                                        tick=self.tick_count)

    def bayar_utang(self, entitas: Any, isi: Optional[str] = None) -> int:
        """Tepati utang emosional; memulihkan sebagian prior sosial."""
        if self.nurani is None:
            return 0
        return self.nurani.bayar_utang(entitas, isi=isi, tick=self.tick_count)

    def utang(self, entitas: Any) -> Dict[str, Any]:
        """Berat utang emosional & status menarik diri (fitur 4)."""
        if self.nurani is None:
            return {"berat": 0.0, "menarik_diri": False, "daftar": []}
        return self.nurani.utang_state(entitas)

    def menarik_diri(self, entitas: Any) -> bool:
        """True bila NPC sudah menyerah percaya karena tumpukan utang."""
        return bool(self.nurani is not None and self.nurani.menarik_diri(entitas))

    def tandai_momen(self, teks: str, klaim: Optional[str] = None,
                     bobot: float = 1.0) -> Dict[str, Any]:
        """Tandai sebuah momen sebagai memori inti (pilar identitas).

        Core memory tidak pernah di-prune, sering muncul di kesadaran,
        mengikat klaim identitas, dan menaikkan cap kepercayaan untuk
        signature-nya — satu momen yang mengubah segalanya.
        """
        if self.kesadaran is None:
            return {}
        return self.kesadaran.tandai_core_memory(teks, klaim=klaim, bobot=bobot)

    def viskositas_relasi(self, entitas: Any) -> Dict[str, Any]:
        """Asimetri pemulihan kepercayaan (fitur 6): laporan + label.

        Membangun kepercayaan dari nol relatif cepat; memulihkannya setelah
        hancur sangat lambat (faktor pembagi besar) — Player merasakan
        'beratnya' memperbaiki hubungan yang ia rusak sendiri.
        """
        if self.nurani is None:
            return {"faktor": 1.0, "label": "normal", "kepercayaan": 0.0}
        r = self.relasi(entitas)
        faktor = 1.0
        getter = getattr(self.nurani, "trust_recovery_factor", None)
        if callable(getter):
            try:
                faktor = float(getter(entitas))
            except Exception as _galat_diagnostik_136:
                _diag.catat('naluri.Naluri.viskositas_relasi', "galat pada jalur fallback", galat=_galat_diagnostik_136, jalur=136)
                faktor = 1.0
        t = float(r.get("kepercayaan", 0.0))
        if r.get("hancur") or t < 0.0:
            label = "hancur" if faktor <= 0.2 else "rusak"
        elif t >= 0.5:
            label = "kokoh"
        else:
            label = "normal"
        return {"faktor": round(faktor, 4), "label": label,
                "kepercayaan": round(t, 4), "hancur": bool(r.get("hancur"))}

    def hancurkan_kepercayaan(self, entitas: Any, sebab: str = "") -> Dict[str, Any]:
        """Serangan/pengkhianatan: kepercayaan dihancurkan cepat & dalam.

        Setelah ini, pemulihan butuh interaksi positif jauh lebih banyak
        (lihat viskositas_relasi).
        """
        rel = None
        if self.nurani is not None:
            breaker = getattr(self.nurani, "break_trust", None)
            if callable(breaker):
                rel = breaker(entitas, severity=0.7, tick=self.tick_count,
                              nama=None)
        if rel is None:
            hasil = self.berinteraksi(entitas, muatan=-0.9,
                                      kepercayaan_delta=-0.9,
                                      alasan=sebab or "kepercayaan dihancurkan")
            rel = hasil.get("relasi")
        try:
            self.kesadaran.betray(entitas, sebab=sebab) if self.kesadaran else None
        except Exception as _galat_diagnostik_137:
            _diag.catat('naluri.Naluri.hancurkan_kepercayaan', "galat pada jalur fallback", galat=_galat_diagnostik_137, jalur=137)
            pass
        return {"relasi": rel, "label": self.label_relasi(rel),
                "viskositas": self.viskositas_relasi(entitas)}

    def berinteraksi(self, entitas: Any, muatan: float = 0.3,
                     kepercayaan_delta: float = 0.0,
                     nama: Optional[str] = None,
                     alasan: str = "") -> Dict[str, Any]:
        """Satu interaksi sosial penuh — titik masuk tunggal untuk dialog,
        perdagangan, pertengkaran, dsb.

        `muatan` = valensi emosional interaksi [-1..+1] (obrolan ringan +0.2,
        pertolongan +0.8, hinaan −0.6, pengkhianatan −1.0).

        Efek berlapis: (1) relasi diperbarui di memori sosial NURANI;
        (2) drive afiliasi/keamanan bergerak — DIMODULASI relasi: bersama
        entitas yang disukai & akrab lebih mengenyangkan afiliasi, entitas
        tepercaya menenangkan keamanan; (3) emosi bereaksi (gated);
        (4) semua tercatat di delta_log/emosi_log sehingga bisa diaudit.
        """
        if self.nurani is None:
            r = self._relasi_netral(entitas, nama or "")
        else:
            r = self.nurani.interact(entitas, muatan=muatan,
                                     kepercayaan_delta=kepercayaan_delta,
                                     tick=self.tick_count, nama=nama)
        gain = float(self.params.get("social_interaction_gain", 0.15))
        d_af = (gain * (0.5 + 0.5 * r["valensi"]) * (0.4 + 0.6 * r["akrab"])
                + gain * float(muatan))
        d_ke = 0.6 * gain * r["kepercayaan"]
        alasan = alasan or f"interaksi dengan {r.get('nama') or r['id']}"
        self.delta("afiliasi", d_af, reason=alasan)
        self.delta("keamanan", d_ke, reason=alasan)
        # Bug-fix (soak test): interaksi sosial bisa terjadi DI LUAR tick
        # fisika (mis. LOD "beku"/"latar"), di mana clip [-1,1] tidak berjalan
        # — clip eksplisit di sini agar level tak pernah keluar rentang.
        for d in ("afiliasi", "keamanan"):
            self.levels[d] = jepit_drive(self.levels[d])
        if self._emosi_aktif():
            g = float(self.params["emosi_gain_event"])
            if muatan > 0.05:
                self._emosi_naikkan("senang",
                                    min(1.0, float(muatan))
                                    * (0.5 + 0.5 * r["valensi"]) * g, alasan)
            elif muatan < -0.05:
                self._emosi_naikkan("sedih",
                                    min(1.0, -float(muatan)) * 0.7 * g, alasan)
                if r["kepercayaan"] < 0.0:
                    self._emosi_naikkan("marah",
                                        min(1.0, -float(muatan)) * 0.5 * g,
                                        alasan + " (relasi buruk)")
                if r["kepercayaan"] < -0.2:
                    self._emosi_naikkan("takut",
                                        min(1.0, -float(muatan)) * 0.3 * g,
                                        alasan + " (tak dipercaya)")
        return {"relasi": r, "label": self.label_relasi(r),
                "d_afiliasi": round(d_af, 4), "d_keamanan": round(d_ke, 4)}

    # -------------------- integrasi dengan modul lain --------------------
    def apply_to_brain(self, brain: Any) -> None:
        """Kirim sinyal neuromodulasi + atensi top-down ke Brain, bila API ada.

        Duck-typed: tidak meng-import samre.core.brain.
        """
        if brain is None:
            return
        # Hitung level neuromodulator dari defisit drive.
        # Setiap neuromodulator adalah rata-rata defisit drive yang terpetakan + baseline 0.
        nm: Dict[str, float] = {"dopamine": 0.0, "serotonin": 0.0,
                                "noradrenaline": 0.0, "acetylcholine": 0.0}
        contrib = {"dopamine": 0, "serotonin": 0, "noradrenaline": 0, "acetylcholine": 0}
        for d in DRIVES:
            deficit = self.deficit(d)
            mod = DRIVE_NEUROMOD.get(d)
            if mod:
                nm[mod] += deficit
                contrib[mod] += 1
        for k, v in list(nm.items()):
            if contrib[k] > 0:
                nm[k] = v / contrib[k]
        # reward pasca-berhasil menambah dopamine
        nm["dopamine"] = max(nm["dopamine"], self.levels["penguasaan"] * 0.5)
        # afiliasi surplus → serotonin tambahan
        nm["serotonin"] = max(nm["serotonin"], max(self.levels["afiliasi"], 0.0) * 0.6)

        setter = getattr(brain, "set_neuromodulator", None)
        if callable(setter):
            for name, value in nm.items():
                try:
                    setter(name, float(jepit_drive(value)))
                except Exception as _galat_diagnostik_138:
                    _diag.catat('naluri.Naluri.apply_to_brain', "galat pada jalur fallback", galat=_galat_diagnostik_138, jalur=138)
                    pass

        # learning rate multiplier dari mood
        mod = self.mood().modulation()
        lr_setter = getattr(brain, "set_learning_rate", None)
        if callable(lr_setter):
            try:
                base_lr = getattr(brain, "learning_rate", 0.01)
                lr_setter(base_lr * mod["learning_rate_mult"])
            except Exception as _galat_diagnostik_139:
                _diag.catat('naluri.Naluri.apply_to_brain', "galat pada jalur fallback", galat=_galat_diagnostik_139, jalur=139)
                pass

        # Atensi top-down: lepas dulu, lalu set region drive dominan.
        release = getattr(brain, "clear_attentional_bias", None)
        focus = getattr(brain, "set_attentional_bias", None)
        if callable(release):
            try:
                release()
            except Exception as _galat_diagnostik_140:
                _diag.catat('naluri.Naluri.apply_to_brain', "galat pada jalur fallback", galat=_galat_diagnostik_140, jalur=140)
                pass
        if callable(focus) and self.goals:
            dominant = self.goals[0].drive
            for region in DRIVE_ATTENTION.get(dominant, []):
                try:
                    focus(region, 0.6 + 0.4 * self.urgency[dominant])
                except Exception as _galat_diagnostik_141:
                    _diag.catat('naluri.Naluri.apply_to_brain', "galat pada jalur fallback", galat=_galat_diagnostik_141, jalur=141)
                    pass

    def memory_policy(self) -> Dict[str, Any]:
        """Override config untuk SamanticGarden sebelum konsolidasi."""
        mood = self.mood()
        # keingintahuan tinggi → mudah masuk (ingest threshold rendah)
        ingest_threshold = max(0.05, 0.25 - 0.2 * self.deficit("keingintahuan"))
        # murung (valence<0) → kristalisasi sulit (pilih yang benar-benar penting)
        crystallize_importance = max(0.4, 0.55 - 0.3 * mood.valence)
        # energi rendah → pruning agresif (memori ikut ekonomi energi)
        pruning_aggressiveness = 0.5 + 0.5 * self.deficit("energi")
        # sigma node (jika Garden mendukung) naik saat mood ceria
        node_sigma_mult = max(0.6, 1.0 + 0.3 * mood.valence)
        # replays diutamakan untuk drive yang sedang defisit
        priority_drives = [g.drive for g in self.goals]
        return {
            "ingest_threshold": ingest_threshold,
            "crystallize_importance": crystallize_importance,
            "episodic_decay_rate": 0.01 + 0.02 * self.deficit("energi"),
            "episodic_importance_decay": 0.005 + 0.01 * self.deficit("energi"),
            "consolidation_pruning_threshold": max(0.05, 0.2 - 0.1 * self.deficit("energi")),
            "pruning_aggressiveness": pruning_aggressiveness,
            "priority_drives": priority_drives,
            "replay_strength": 0.4 + 0.3 * mood.arousal,
            "node_sigma_mult": node_sigma_mult,
            "mood": {"valence": mood.valence, "arousal": mood.arousal},
        }

    def apply_memory_policy(self, garden: Any) -> None:
        """Terapkan kebijakan memori ke SamanticGarden: tulis config dan
        metadata['salience']/metadata['drive_context'] ke semua node.

        Duck-typed: tidak meng-import samre.memory.garden.
        """
        if garden is None:
            return
        policy = self.memory_policy()
        cfg = getattr(garden, "config", None)
        if isinstance(cfg, dict):
            for k, v in policy.items():
                if k in cfg and not isinstance(v, (dict, list)):
                    try:
                        cfg[k] = float(v)
                    except (TypeError, ValueError):
                        pass
        nodes = getattr(garden, "nodes", None)
        if isinstance(nodes, dict):
            for node in nodes.values():
                try:
                    meta = getattr(node, "metadata", None)
                    if not isinstance(meta, dict):
                        meta = {}
                        try:
                            node.metadata = meta
                        except Exception as _galat_diagnostik_142:
                            _diag.catat('naluri.Naluri.apply_memory_policy', "galat pada jalur fallback", galat=_galat_diagnostik_142, jalur=142)
                            meta = None
                    if meta is not None:
                        meta["salience"] = self.salience(node)
                        # tulis sigma node bila ada (opsional)
                        if hasattr(node, "sigma") and "node_sigma_mult" in policy:
                            try:
                                base = getattr(node, "_base_sigma", node.sigma)
                                node._base_sigma = base
                                node.sigma = float(base) * float(policy["node_sigma_mult"])
                            except Exception as _galat_diagnostik_143:
                                _diag.catat('naluri.Naluri.apply_memory_policy', "galat pada jalur fallback", galat=_galat_diagnostik_143, jalur=143)
                                pass
                except Exception as _galat_diagnostik_144:
                    _diag.catat('naluri.Naluri.apply_memory_policy', "galat pada jalur fallback", galat=_galat_diagnostik_144, jalur=144)
                    pass

    def set_personality(self, **drive_weights: float) -> None:
        """Atur kepribadian dengan mengubah bobot drive.

        Contoh: naluri.set_personality(afiliasi=0.1)  # 'psikopat'
                 naluri.set_personality(keamanan=2.0)  # 'paranoid'
                 naluri.set_personality(keingintahuan=2.0)  # 'petualang'

        Untuk penyetelan siap-tempel berbasis NAMA, lihat
        `set_personality_preset()` (fix #3) — katalognya `PERSONALITIES`.
        """
        for d, w in drive_weights.items():
            if d in self.weights:
                self.weights[d] = float(w)

    def set_personality_preset(self, name: Any, blend: float = 1.0,
                               terapkan_lahir: bool = True) -> Dict[str, float]:
        """Terapkan preset kepribadian bernama (fix #3, diperluas WATAK).

        name  : kunci PERSONALITIES ("penjaga", "sosiawan", ...), alias di
                PERSONALITY_ALIASES ("guard", "petualang", ...), ATAU dict
                langsung {"weights": {...}, "watak": {...}, "lahir": {...}}
                agar desainer bisa menempel penyetelan kustom tanpa mengubah
                modul (kunci lama "params" tetap diterima sebagai alias
                "watak").
        blend : 0..1 — 1.0 = bobot preset apa adanya; 0.5 = campur setengah
                dengan bobot dasar tahap maturasi (penyetelan dinamis).
        terapkan_lahir : seed kondisi awal (backstory). `set_stage()`
                memanggil dengan False agar maturasi tidak mereset NPC ke
                "masa kecilnya"; dari kode game biarkan True (default).

        Tiga lapis yang diterapkan:
          weights (kepribadian/arah) → self.weights (di-blend dengan tahap),
          watak (viskositas/filter)  → injeksi self.params — pintu yang dulu
              tidak pernah dipakai preset mana pun; nilai dict di-deep-copy
              agar konstanta modul tak pernah bocor antar-instans. Kunci
              watak preset sebelumnya yang tidak dipakai preset baru
              dikembalikan ke DEFAULTS (watak tergantikan utuh).
          lahir (backstory/kondisi awal) → seed_backstory().

        Preset bertahan melewati perubahan tahap otomatis (set_stage
        menerapkannya ulang), dan `personality_name` ikut terserialisasi.
        Mengembalikan bobot aktif final.
        """
        if isinstance(name, dict):
            preset = copy.deepcopy(name)
            key = str(preset.get("name", "kustom")).lower()
        else:
            key = str(name).lower()
            resolved = PERSONALITY_ALIASES.get(key, key)
            if resolved not in PERSONALITIES:
                raise ValueError(
                    f"preset kepribadian tidak dikenal: {name!r} "
                    f"(pilihan: {', '.join(sorted(PERSONALITIES))})")
            preset = PERSONALITIES[resolved]
            key = resolved
        blend = jepit_01(float(blend))
        base = STAGE_WEIGHTS[self.stage]
        for d, w in (preset.get("weights") or {}).items():
            if d in self.weights:
                b = float(base.get(d, self.weights[d]))
                self.weights[d] = b * (1.0 - blend) + float(w) * blend
        self.personality_name = key
        self._personality_blend = blend
        # --- WATAK: injeksi parameter (deep-copy; alias lama "params") ---
        watak = preset.get("watak")
        if watak is None:
            watak = preset.get("params")
        watak = copy.deepcopy(watak) if isinstance(watak, dict) else {}
        for k in self._watak_keys:
            if k not in watak:  # bersihkan sisa watak preset sebelumnya
                if k in DEFAULTS:
                    self.params[k] = copy.deepcopy(DEFAULTS[k])
                else:
                    self.params.pop(k, None)
        self.params.update(watak)
        self._watak_keys = sorted(watak.keys())
        # --- LAHIR: kondisi awal (sekali per kelahiran/penerapan eksplisit) ---
        if terapkan_lahir:
            self.seed_backstory(preset.get("lahir") or {})
        return dict(self.weights)

    def set_watak(self, **kv: Any) -> None:
        """Setel parameter watak individual, tanpa preset.

        Contoh:
            naluri.set_watak(setpoint_lr={"keamanan": 0.00001, "*": 0.0008},
                             social_consolidation=0.1,
                             urgency_alpha={"keamanan": 0.5})
        Nilai dict (per-drive) di-deep-copy. Perubahan langsung dipakai
        NURANI karena `params` adalah satu sumber kebenaran bersama.
        """
        for k, v in kv.items():
            self.params[k] = copy.deepcopy(v) if isinstance(v, dict) else v
            if k not in self._watak_keys:
                self._watak_keys.append(k)

    def watak_aktif(self) -> Dict[str, Any]:
        """Snapshot parameter watak yang pernah disetel (preset/set_watak)."""
        out: Dict[str, Any] = {}
        for k in self._watak_keys:
            if k in self.params:
                v = self.params[k]
                out[k] = copy.deepcopy(v) if isinstance(v, dict) else v
        return out

    def seed_backstory(self, lahir: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Terapkan kondisi awal (backstory) — "lahir" dari preset WATAK.

        Filter plastisitas hanya MEMPERTAHANKAN sifat; kondisi awal yang
        MENCIPTAKANNYA di tick 0. `lahir` mendukung kunci:
          "levels"    : {drive: float} — kondisi fisiologis awal (clip [-1,1])
          "setpoints" : {drive: float} — ekspektasi homeostatis awal; di-clip
                        oleh `setpoint_clamp` watak yang AKTIF (paranoid boleh
                        di-seed 0.55 karena clamp keamanannya 0.6)
          "memori"    : [{"teks", "deltas", "n"}] — memori afektif; prior
                        langsung aktif di tick 0 (bila pilar A nyala)
          "relasi"    : [{"nama"|"entitas", "valensi", "kepercayaan", "akrab",
                        "n"}] — orang yang "sudah dikenal sebelum game mulai"
          "emosi"     : {nama_emosi: intensitas} — hanya bila enable_emosi
        Semua aman (no-op) bila pilar terkait mati / NURANI tak tersedia —
        degradasi anggun tetap berlaku. Mengembalikan ringkasan terapan.
        """
        lahir = lahir or {}
        ringkas: Dict[str, Any] = {}
        # 1) level fisiologis awal
        lvl = lahir.get("levels") or {}
        dipakai = {}
        for d, v in lvl.items():
            if d in self.levels:
                self.levels[d] = jepit_drive(float(v))
                dipakai[d] = self.levels[d]
        if dipakai:
            ringkas["levels"] = dipakai
        nur = self.nurani
        if nur is not None:
            # 2) setpoint awal (di-clip clamp watak per-drive)
            sp = lahir.get("setpoints") or {}
            if sp:
                hasil = nur.seed_setpoints(sp)
                if hasil:
                    ringkas["setpoints"] = hasil
            # 3) memori afektif ("pernah terbakar sebelumnya")
            mem = lahir.get("memori") or []
            n_mem = 0
            for m in mem:
                if isinstance(m, dict) and m.get("teks"):
                    if nur.seed_affective(str(m["teks"]), m.get("deltas") or {},
                                          n=int(m.get("n", 5)),
                                          tick=self.tick_count):
                        n_mem += 1
            if n_mem:
                ringkas["memori"] = n_mem
            # 4) relasi lama
            rel = lahir.get("relasi") or []
            n_rel = 0
            for r in rel:
                if isinstance(r, dict):
                    ent = r.get("entitas", r.get("nama", ""))
                    if ent == "":
                        continue
                    nur.seed_relationship(
                        ent, valensi=float(r.get("valensi", 0.0)),
                        kepercayaan=float(r.get("kepercayaan", 0.0)),
                        akrab=float(r.get("akrab", 0.0)),
                        n=int(r.get("n", 1)),
                        nama=str(r.get("nama", ent)), tick=self.tick_count)
                    n_rel += 1
            if n_rel:
                ringkas["relasi"] = n_rel
        # 5) emosi awal (hanya bila mesin emosi aktif)
        emo = lahir.get("emosi") or {}
        if emo and self.params.get("enable_emosi"):
            dipakai_e = {}
            for e, v in emo.items():
                k = EMOSI_ALIASES.get(str(e).lower())
                if k is not None:
                    self.emosi[k] = jepit_01(float(v))
                    dipakai_e[k] = self.emosi[k]
            if dipakai_e:
                ringkas["emosi"] = dipakai_e
        if lahir:
            self._lahir_diterapkan = True
        return ringkas

    @staticmethod
    def personality_presets() -> Dict[str, Dict[str, Any]]:
        """Katalog preset untuk desainer: nama -> {label, desc, weights,
        watak, lahir} (deep-copy: aman dimutasi oleh tooling)."""
        return {k: {"label": v.get("label", k), "desc": v.get("desc", ""),
                    "weights": dict(v.get("weights") or {}),
                    "watak": copy.deepcopy(v.get("watak") or {}),
                    "lahir": copy.deepcopy(v.get("lahir") or {})}
                for k, v in PERSONALITIES.items()}

    def describe_personality(self) -> Dict[str, Any]:
        """Ringkasan kepribadian aktif (preset + bobot final + watak)."""
        preset = PERSONALITIES.get(self.personality_name or "")
        return {
            "preset": self.personality_name,
            "label": preset.get("label") if preset else "kustom",
            "desc": preset.get("desc") if preset else "",
            "blend": self._personality_blend,
            "weights": {d: round(self.weights[d], 3) for d in DRIVES},
            "tahap": self.stage,
            "watak": self.watak_aktif(),
            "lahir_diterapkan": self._lahir_diterapkan,
        }

    # -------------------- NNRE: Neuro-Divergent Pruning --------------------
    def neuromodulation_bias(self, brain: Any = None) -> Dict[str, Any]:
        """Terjemahkan level neuromodulator aktif (dari Brain atau dari defisit
        drive) menjadi parameter Imagination yang adaptif.

        Pilar A NNRE — Pemangkasan Simulasi Berbasis Neuromodulator:
            - ACh tinggi (penasaran/koherensi lapar)  → branch_factor naik,
              pruning longgar (eksplorasi kreatif).
            - NA tinggi (keamanan/energi defisit)     → pruning ketat
              (top-n kecil, statistical), fokus ke risiko.
            - DA tinggi (penguasaan surplus/goal penguasaan)
              → preference terhadap reward/impact positif (d lewat
              reward_bias yang dikirim ke scoring).
        Bisa dipakai dengan atau tanpa objek Brain (duck-typed).
        """
        # Ambil level neuromodulator dari brain jika tersedia, jika tidak
        # pakai defisit drive sebagai proksi (sudah cukup akurat karena
        # apply_to_brain() mengatur mereka dari defisit).
        nm_getter = getattr(brain, "get_neuromodulators", None) if brain is not None else None
        nm: Dict[str, float] = {}
        if callable(nm_getter):
            try:
                nm = nm_getter() or {}
            except Exception as _galat_diagnostik_145:
                _diag.catat('naluri.Naluri.neuromodulation_bias', "galat pada jalur fallback", galat=_galat_diagnostik_145, jalur=145)
                nm = {}
        # fallback proksi dari drive/goal
        ach = float(nm.get("acetylcholine",
                     0.5 * self.deficit("keingintahuan") + 0.5 * self.deficit("koherensi")))
        na = float(nm.get("noradrenaline",
                    0.6 * self.deficit("keamanan") + 0.3 * self.deficit("energi")))
        da = float(nm.get("dopamine",
                    max(self.levels.get("penguasaan", 0.0),
                        0.6 * self.urgency.get("penguasaan", 0.0))))
        se = float(nm.get("serotonin",
                    max(self.levels.get("afiliasi", 0.0),
                        0.5 * self.levels.get("koherensi", 0.0))))
        mood = self.mood()
        # base dari mood modulation (yang sudah ada)
        mod = mood.modulation()
        bf_base = 5
        bf = int(round(bf_base * mod["branch_factor_mult"]))
        pf = mod["pruning_aggressiveness"]
        # ACh → perlebar
        bf += int(round(2.0 * max(0.0, ach)))
        pf -= 0.2 * max(0.0, ach)
        # NA → persempit & fokus
        bf -= int(round(2.0 * max(0.0, na)))
        pf += 0.25 * max(0.0, na)
        bf = max(2, min(9, bf))
        pf = jepit(pf, 0.25, 0.95)
        # pruning method: statistical saat NA tinggi (agresif), top_n biasa,
        # atau 'top_n' dengan top_n kecil
        if na > 0.4:
            pruning_method = "statistical"
        elif ach > 0.4:
            pruning_method = "top_n"
        else:
            pruning_method = "top_n"
        top_n = max(3, int(round((bf + 2) * (1.1 - 0.5 * pf))))
        # reward_bias diteruskan ke scoring; DA+ → lebih memilih outcome positif
        reward_bias = 0.2 * max(0.0, da) - 0.1 * max(0.0, na)
        # lapisan simulasi: lebih dalam saat arousal tinggi
        max_layers_mult = mod["max_layers_mult"] * (1.0 + 0.3 * max(0.0, na))
        return {
            "branch_factor": bf,
            "pruning_method": pruning_method,
            "pruning_aggressiveness": pf,
            "pruning_threshold": max(0.25, pf),
            "top_n": top_n,
            "reward_bias": reward_bias,
            "max_layers_mult": max_layers_mult,
            "learning_rate_mult": mod["learning_rate_mult"],
            "sigma_mult": mod["sigma_mult"],
            "ach": ach, "na": na, "da": da, "se": se,
        }

    # -------------------- NNRE: Counterfactual Synaptic Rehearsal -----------
    def counterfactual_rehearsal(self, brain: Any, imagination_result: Any,
                                  strength: float = 0.4,
                                  steps: int = 2,
                                  max_outcomes: int = 3) -> Dict[str, Any]:
        """Latihan sinaptik imajinatif — jadikan simulasi kritis sebagai
        pengalaman *sebelum* aksi diambil.

        Pilar B NNRE: saat Imagination menemukan sleeper/counterfactual kritis
        (bom waktu atau cabang what-if yang sangat negatif), hasilnya
        dikonversi menjadi spike/potensial sintetis yang disuntikkan ke Brain
        (seolah-olah otak "berlatih menghadapi" skenario itu). Ini memberi
        Zero-Real-World-Harm Learning.
        """
        from pycos.inti.naluri import _get_attr
        if brain is None or imagination_result is None:
            return {"rehearsed": 0}
        # Ambil outcome kritis: sleeper negatif atau counterfactual buruk
        top = getattr(imagination_result, "top_outcomes", None)
        if isinstance(top, dict):
            top = [top]
        candidates = []
        if isinstance(top, list):
            for o in top:
                desc = str(_get_attr(o, "description", "") or "").lower()
                # Ambil impak dari atribut yang benar (`impact_score` pada
                # SimulationOutcome; `impact` sebagai fallback).
                impact = float(_get_attr(o, "impact_score",
                               _get_attr(o, "impact", 0.0)) or 0.0)
                delay = int(_get_attr(o, "delay_to_impact", 0) or 0)
                is_cf = ("counterfactual" in desc)
                is_sleeper = (delay >= 2 and impact < -0.2) or ("bom waktu" in desc)
                is_worst = impact < -0.4
                if is_cf or is_sleeper or is_worst:
                    prio = abs(impact) + (0.3 if is_sleeper else 0.0) + (0.2 if is_cf else 0.0)
                    candidates.append((prio, o))
        candidates.sort(key=lambda x: x[0], reverse=True)
        targets = candidates[:max_outcomes]
        rehearse_log = []
        # Dapatkan region yang akan diinjeksikan (region motor+region drive dominan)
        focus_regions: List[str] = []
        if self.goals:
            focus_regions = list(DRIVE_ATTENTION.get(self.goals[0].drive, []))
        # tambahkan beberapa region standar
        for extra in ("PremotorCortex", "Amygdala", "Hippocampus",
                      "CingulateGyrus", "CaudateNucleus", "ParietalAssociationCortex"):
            if extra in getattr(brain, "regions", {}) and extra not in focus_regions:
                focus_regions.append(extra)
        for prio, o in targets:
            impact = float(_get_attr(o, "impact_score",
                            _get_attr(o, "impact", 0.0)) or 0.0)
            desc = str(_get_attr(o, "description", "") or "")
            inj_mag = strength * prio * (1.0 if impact < 0 else 0.4)
            # set reward otak sesuai sign (negatif = waspada = takkan diulang)
            try:
                brain.set_reward(float(impact) * inj_mag * 0.5)
            except Exception as _galat_diagnostik_146:
                _diag.catat('naluri.Naluri.counterfactual_rehearsal', "galat pada jalur fallback", galat=_galat_diagnostik_146, jalur=146)
                pass
            for _step in range(steps):
                for rname in focus_regions:
                    try:
                        brain.inject_input(rname, inj_mag * jepit_drive(impact))
                    except Exception as _galat_diagnostik_147:
                        _diag.catat('naluri.Naluri.counterfactual_rehearsal', "galat pada jalur fallback", galat=_galat_diagnostik_147, jalur=147)
                        continue
                # DA pulse kecil untuk belajar dari outcome (jika buruk, DA turun)
                try:
                    if impact > 0:
                        brain.set_neuromodulator("dopamine",
                            min(1.0, 0.2 + 0.4 * impact * inj_mag))
                    else:
                        brain.set_neuromodulator("dopamine",
                            max(-1.0, -0.3 + 0.4 * impact * inj_mag))
                except Exception as _galat_diagnostik_148:
                    _diag.catat('naluri.Naluri.counterfactual_rehearsal', "galat pada jalur fallback", galat=_galat_diagnostik_148, jalur=148)
                    pass
                try:
                    brain.step()
                except Exception as _galat_diagnostik_149:
                    _diag.catat('naluri.Naluri.counterfactual_rehearsal', "galat pada jalur fallback", galat=_galat_diagnostik_149, jalur=149)
                    break
            rehearse_log.append({
                "description": desc[:80],
                "impact": impact,
                "injection": inj_mag,
            })
        # Juga jalankan homeostatic_update bila ada (ritme sirkadian mikro)
        try:
            for region in getattr(brain, "atomic_regions", []) or []:
                if hasattr(region, "homeostatic_update"):
                    region.homeostatic_update(rate_gain=0.02)
        except Exception as _galat_diagnostik_150:
            _diag.catat('naluri.Naluri.counterfactual_rehearsal', "galat pada jalur fallback", galat=_galat_diagnostik_150, jalur=150)
            pass
        return {"rehearsed": len(rehearse_log), "targets": rehearse_log}

    # -------------------- NNRE: Drive-Triggered Targeted Dreaming ----------
    def drive_targeted_scenario(self) -> Optional[Dict[str, Any]]:
        """Jika salah satu drive di ambang kritis, pesan satu skenario Imagination
        khusus beserta semantic vector bias (drive-focus) untuk NPV simulasi
        dan expectation calibration sebelum aksi diambil.

        Pilar C NNRE. Mengembalikan dict {scenario, drive, urgency, bias_vector,
        weight_counterfactual, weight_sleeper} atau None jika tak ada drive
        yang cukup lapar untuk memicu simulasi tambahan.
        """
        critical = None
        for g in self.goals:
            if g.urgency > 0.5 or (g.drive == "keamanan" and g.urgency > 0.35):
                critical = g
                break
        if critical is None:
            return None
        # buat semantic vector bias sederhana: one-hot bobot drive pada 6 slot
        # (vektor ini akan dipakai orchestrator untuk menggabungkan dengan
        #  state vector saat memanggil imagination.simulate).
        bias = [0.0] * len(DRIVES)
        idx = DRIVES.index(critical.drive)
        bias[idx] = 1.0
        hint = {
            "energi": "Cari aksi paling hemat energi tanpa mengorbankan tujuan lain",
            "keamanan": "Simulasikan ancaman laten dan bom waktu; rencanakan mitigasi",
            "keingintahuan": "Jelajahi paradoks dan perspektif alternatif; buat counterfactual",
            "penguasaan": "Ulangi aksi kompeten; cari penguatan positif dan jalur kemenangan",
            "afiliasi": "Cari hasil win-win dengan pihak lain; simulasikan perspektif mereka",
            "koherensi": "Kalibrasi prediksi; uji asumsi; konsolidasikan yang konsisten",
        }[critical.drive]
        return {
            "scenario": f"[FOKUS {critical.drive.upper()}] {hint} (urgensi {critical.urgency:.2f})",
            "drive": critical.drive,
            "urgency": critical.urgency,
            "bias_vector": bias,
            "counterfactual": critical.drive in ("keamanan", "keingintahuan", "koherensi"),
            "enable_sleeper": critical.drive in ("keamanan", "koherensi"),
            "multi_perspective": critical.drive in ("afiliasi", "keingintahuan"),
            "layers_hint": max(3, min(6, int(round(3 + 2 * critical.urgency)))),
        }

    # -------------------- NNRE: Resonant Sleep ----------------------------
    def resonant_recalibration(self,
                                imagination_history: Optional[List[Any]] = None,
                                strength: float = 0.5) -> Dict[str, Any]:
        """Rekalibrasi Naluri pada fase tidur menggunakan NPV / weighted_score
        hasil simulasi yang terjadi selama terjaga.

        - Rata-rata NPV simulasi → dorong koherensi
        - NPV buruk (negatif) pada sleeper → turunkan keamanan sedikit
        - Kalibrasi skala adaptif dirapatkan
        """
        from pycos.inti.naluri import _get_attr
        npv_sum = 0.0
        npv_n = 0
        worst_sleeper: Optional[float] = None
        if imagination_history:
            for item in imagination_history:
                if item is None:
                    continue
                ws = _get_attr(item, "weighted_score", None)
                if callable(ws):
                    try:
                        v = float(ws(self.scoring_func()))
                    except Exception as _galat_diagnostik_151:
                        _diag.catat('naluri.Naluri.resonant_recalibration', "galat pada jalur fallback", galat=_galat_diagnostik_151, jalur=151)
                        v = None
                else:
                    v = float(ws) if ws is not None else None
                if v is None:
                    v = float(_get_attr(item, "impact_score", 0.0) or 0.0) * \
                        float(_get_attr(item, "probability", 1.0) or 1.0)
                delay = int(_get_attr(item, "delay_to_impact", 0) or 0)
                npv_v = v / ((1.0 + 0.15) ** max(0, delay))
                npv_sum += npv_v
                npv_n += 1
                if delay >= 2 and npv_v < (worst_sleeper if worst_sleeper is not None else 0.0):
                    worst_sleeper = npv_v
        # dorong koherensi (rata-rata prediksi positif = validasi)
        if npv_n > 0:
            avg_npv = npv_sum / npv_n
            delta_koh = strength * 0.15 * jepit_drive(avg_npv)
            self.levels["koherensi"] = jepit_drive(self.levels["koherensi"] + delta_koh)
            if worst_sleeper is not None:
                self.levels["keamanan"] = max(-1.0,
                    self.levels["keamanan"] + strength * 0.1 * worst_sleeper)
        # paksa update skala
        self._update_scale()
        # reset backlog
        self._unverified_predictions = max(0, self._unverified_predictions - 3)
        return {"npv_n": npv_n,
                "avg_npv": (npv_sum / npv_n) if npv_n else 0.0,
                "worst_sleeper": worst_sleeper}

    def salience(self, node: Any, now: Optional[float] = None) -> float:
        """Penting × relevansi drive; `now` bisa dipasang untuk hasil reprodusibel."""
        from pycos.inti.naluri import _get_attr
        now = None if now is None else float_hingga(now, "now")
        try:
            importance = float(_get_attr(node, "importance", 0.5))
        except Exception as _galat_diagnostik_152:
            _diag.catat('naluri.Naluri.salience', "galat pada jalur fallback", galat=_galat_diagnostik_152, jalur=152)
            importance = 0.5
        metadata = _get_attr(node, "metadata", {}) or {}
        drive_ctx = metadata.get("drive_context", {}) if isinstance(metadata, dict) else {}
        relevance = 0.0
        for d in DRIVES:
            ctx = float(drive_ctx.get(d, 0.0))
            relevance += ctx * self.deficit(d) * self.weights[d]
        # sentuhan akses terakhir memberi bonus kecil.
        # Bug-fix: `last_accessed` adalah WAKTU DINDING (time.time), bukan
        # tick_count — sebelumnya `tick_count - last_accessed` menghasilkan
        # nilai raksasa negatif sehingga bonus recency tak pernah bekerja.
        try:
            idle = None
            idle_fn = getattr(node, "idle_seconds", None)
            if callable(idle_fn):
                try:
                    idle = max(0.0, float(idle_fn()))
                except Exception as _galat_diagnostik_153:
                    _diag.catat('naluri.Naluri.salience', "galat pada jalur fallback", galat=_galat_diagnostik_153, jalur=153)
                    idle = None
            if idle is None:
                last = _get_attr(node, "last_accessed", 0.0) or 0.0
                if last:
                    idle = max(0.0, (time.time() if now is None else now) - float(last))
            if idle is not None:
                recency = 1.0 / (1.0 + idle * 0.05)
                relevance += 0.1 * recency
            access_count = float(_get_attr(node, "access_count", 0.0))
            relevance += 0.01 * min(access_count, 20.0)
        except Exception as _galat_diagnostik_154:
            _diag.catat('naluri.Naluri.salience', "galat pada jalur fallback", galat=_galat_diagnostik_154, jalur=154)
            pass
        return jepit_drive(importance * (1.0 + relevance))

    # -------------------- NURANI (konsep 17: naluri reflektif) --------------------
    @property
    def setpoints(self) -> Dict[str, float]:
        """Salinan setpoint plastis per drive (pilar C); {} bila NURANI tak ada."""
        return dict(self.nurani.setpoints) if self.nurani is not None else {}

    def experience(self, text: str, drive_deltas: Dict[str, float]) -> bool:
        """Rekam satu pengalaman ke memori afektif (pilar A). True bila tercatat."""
        if self.nurani is None:
            return False
        return self.nurani.experience(text, drive_deltas, tick=self.tick_count)

    def warmup_from_log(self, replace: bool = True) -> int:
        """Replay log episode ringkas NURANI sesudah sesi dimuat."""
        if self.nurani is None:
            return 0
        return self.nurani.warmup_from_log(replace=replace)

    def anticipate(self, text: str) -> Dict[str, float]:
        """Prior afektif untuk sebuah deskripsi (pilar A); nol bila pilar mati.

        MEMOIZATION: hasil di-cache per teks dengan TTL tick, karena prior
        hanya berubah saat memori afektif belajar (bukan tiap tick).
        """
        if self.nurani is None:
            return {d: 0.0 for d in DRIVES}
        key = str(text)
        now = self.tick_count
        cached = self._anticipate_cache.get(key)
        if cached is not None and now - cached[0] <= self._ANTICIPATE_TTL:
            return dict(cached[1])
        val = self.nurani.anticipate(key)
        self._anticipate_cache[key] = (now, dict(val))
        if len(self._anticipate_cache) > 256:
            # buang entri tertua (TTL/least-recent)
            tertua = min(self._anticipate_cache, key=lambda k: self._anticipate_cache[k][0])
            self._anticipate_cache.pop(tertua, None)
        return val

    def forget_affective(self, max_age: Optional[int] = None) -> int:
        """Buang slot memori afektif yang lebih tua dari `max_age` tick.

        Usia diukur terhadap `tick_count` Naluri saat ini, jadi slot yang
        tidak pernah disentuh lagi akhirnya dibuang (mitigasi memori tumbuh).
        """
        if self.nurani is None:
            return 0
        return self.nurani.forget_affective(max_age, kini=self.tick_count)

    def calibration_report(self) -> Optional[CalibrationReport]:
        """Rapor kalibrasi berlapis: Brier, galat per drive, reliability bins."""
        if self.nurani is None:
            return None
        return self.nurani.calibration_report()

    def setpoint(self, drive: str) -> float:
        """Setpoint satu drive (pilar C); 0.0 = netral bila lapisan tak ada."""
        if self.nurani is None:
            return 0.0
        return float(self.nurani.setpoints.get(drive, 0.0))

    def interoception_matrix(self) -> List[List[float]]:
        """Matriks korelasi defisit antar-drive, urutan mengikuti DRIVES."""
        if self.nurani is None:
            return []
        return [list(baris) for baris in self.nurani.interoception]

    def circadian_phase(self) -> str:
        """Fase ritme internal saat ini: "pagi", "siang", "sore", atau "malam".

        Tanpa NURANI terpasang pun fase tetap dihitung lokal (fix #4), agar
        tidur terjadwal NPC tidak bergantung pada lapisan opsional.
        """
        if self.nurani is None:
            return self._fase_lokal()
        return self.nurani.circadian_phase(self.tick_count)

    def resolve_conflict(self, candidates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Diagnostik konflik antar goal aktif atas `candidates` (pilar D)."""
        if self.nurani is None:
            return {"ada": False, "drive": None, "urgensi": None,
                    "penjelasan": "NURANI tidak terpasang", "kandidat_didua": 0}
        return self.nurani.detect_conflict(self.goals, candidates)

    def flow_state(self) -> bool:
        """Keadaan flow saat ini: valensi di atas ambang, gairah di bawah ambang."""
        if self.nurani is None:
            return False
        mood = self.mood()
        return self.nurani.flow_state(mood.valence, mood.arousal)

    # -------------------- INTROSPEKSI DIRI (pilar G) --------------------
    # Fisiologi nyata:
    #   - Interosepsi sadar: anterior insula (Craig 2002) -> model_diri berderau
    #   - Metakognisi: PFC (Fleming 2012) -> confidence & meta-d'
    #   - Error monitoring: ACC (Botvinick 2001) -> error_monitor
    #   - Narasi diri: DMN/mPFC (Raichle 2001, Northoff 2006)
    def introspeksi(self) -> Dict[str, Any]:
        """Snapshot introspeksi diri: model diri, akurasi, meta-d', narasi.

        Mengembalikan {} bila pilar mati / NURANI tak ada (no-op aman).
        """
        if self.nurani is None:
            return {"aktif": False, "catatan": "NURANI tidak terpasang"}
        return self.nurani.introspeksi_state()

    def evaluasi_diri(self) -> Dict[str, Any]:
        """Evaluasi diri cepat: discrepansi, drive bermasalah, bias."""
        if self.nurani is None:
            return {"aktif": False}
        return self.nurani.evaluasi_diri()

    def meta_kognisi(self) -> Dict[str, Any]:
        """Laporan metakognitif: akurasi interoseptif, meta-d', Brier confidence."""
        if self.nurani is None:
            return {"aktif": False}
        return self.nurani.meta_kognisi_laporan()

    def refleksi_diri(self, paksa: bool = False) -> Dict[str, Any]:
        """Picu refleksi DMN-like (narasi diri). `paksa=True` abaikan period."""
        if self.nurani is None or not self.nurani.enabled("introspection"):
            return {"aktif": False}
        if paksa:
            return self.nurani.refleksi_diri(self.tick_count, self.levels, self.urgency,
                                             self.mood().valence, self.mood().arousal)
        # jika tidak paksa, kembalikan narasi terakhir bila ada
        if self.nurani.narasi_diri:
            return self.nurani.narasi_diri[-1]
        return self.nurani.refleksi_diri(self.tick_count, self.levels, self.urgency,
                                         self.mood().valence, self.mood().arousal)

    def sadar_diri(self) -> bool:
        """Apakah organisme sadar diri saat ini (Global Workspace Theory)?"""
        if self.nurani is None:
            return False
        return self.nurani.sadar_diri()

    def nilai_kepercayaan(self, drive: Optional[str] = None) -> float:
        """Kepercayaan diri (confidence) global atau per-drive."""
        if self.nurani is None or not self.nurani.enabled("introspection"):
            return 0.5
        if drive:
            return float(self.nurani.kepercayaan_diri.get(drive, 0.5))
        return float(self.nurani.kepercayaan_global)

    def meta_status(self) -> Dict[str, Any]:
        """Ringkasan seluruh lapisan NURANI (pilar aktif, memori, Brier, ritme)."""
        if self.nurani is None:
            return {"tersedia": False}
        st = self.nurani.meta_status()
        st["tersedia"] = True
        st["working_memory"] = {
            "slot_aktif": len(self.context_aktif),
            "kapasitas": max(3, min(5, int(self.params.get("context_capacity", 5)))),
            "half_life_ticks": float(self.params.get("context_decay_ticks", 8)),
        }
        st["temporal_credit"] = {
            "traces": len(self._eligibility_traces),
            "actions_learned": len(self._action_values),
            "last_assignments": copy.deepcopy(self._last_credit_assignments[-8:]),
        }
        st["coping"] = self.coping_state()
        return st

    def enable_kesadaran(self, *fitur: str, semua: bool = True) -> Dict[str, Any]:
        """Nyalakan (atau `semua=False`, matikan) lapisan kesadaran.

        Master flag `enable_kesadaran`; tanpa argumen tambahan seluruh
        sub-fitur ikut. Nama fitur: global_workspace, inner_speech,
        autobiography, agency, felt_state, reality_monitoring,
        attention_limits, second_person, pragmatics, fallibility, values,
        mortality, dream_continuity, self_audition. Mengembalikan keadaan akhir.
        """
        fitur_list = ("global_workspace", "inner_speech", "autobiography",
                      "agency", "felt_state", "reality_monitoring",
                      "attention_limits", "second_person", "pragmatics",
                      "fallibility", "values", "mortality", "dream_continuity",
                      "self_audition", "epistemic_emotions", "self_opacity",
                      "social_strategy", "play_aesthetics", "sa_sp",
                      "free_will")
        alias_fitur = {"audisi_diri": "self_audition",
                       "audisi-diri": "self_audition",
                       "self-audition": "self_audition"}
        pilih = (tuple(alias_fitur.get(str(f).strip().lower(), f) for f in fitur)
                 if fitur else fitur_list)
        for f in pilih:
            if "enable_" + str(f) not in KESADARAN_DEFAULTS:
                raise ValueError("fitur kesadaran tidak dikenal: {!r}".format(f))
        self.params["enable_kesadaran"] = bool(semua) if not fitur else True
        for f in pilih:
            key = "enable_" + str(f)
            if key in KESADARAN_DEFAULTS:
                self.params[key] = bool(semua)
        return {"enable_kesadaran": bool(self.params.get("enable_kesadaran", False)),
                **{f: bool(self.params.get("enable_" + f, False))
                   for f in fitur_list}}

    def enable_presentasi(self, *kanal: str, semua: bool = True) -> Dict[str, Any]:
        """Nyalakan (atau `semua=False`, matikan) lapisan PRESENTASI (Pycos).

        Master flag `enable_presentasi`; tanpa argumen, seluruh kanal ikut.
        Nama kanal: gestur, prosodi, tatapan, microexpression, idle.
        """
        self.params["enable_presentasi"] = bool(semua) if not kanal else True
        kanal_list = ("gestur", "prosodi", "tatapan", "microexpression", "idle")
        pilih = tuple(kanal) if kanal else kanal_list
        for k in pilih:
            key = "presentasi_" + str(k)
            if key in PRESENTASI_DEFAULTS:
                self.params[key] = bool(semua)
        return {"enable_presentasi": bool(self.params.get("enable_presentasi", False)),
                **{k: bool(self.params.get("presentasi_" + k, False))
                   for k in kanal_list}}

    def enable_replay(self, aktif: bool = True) -> Dict[str, Any]:
        """Aktifkan deterministic replay: snapshot awal + log event."""
        self._replay_enabled = bool(aktif)
        if aktif:
            self._event_log = []
            self._replay_initial = self.to_dict()
        return {"replay": self._replay_enabled,
                "events": len(self._event_log)}

    def export_replay(self) -> Dict[str, Any]:
        """Ekspor snapshot awal + log event untuk diputar ulang."""
        return {"format": "naluri-replay/1",
                "initial": copy.deepcopy(self._replay_initial),
                "events": [dict(x) for x in self._event_log]}

    @classmethod
    def replay(cls, data: Mapping[str, Any],
               until: Optional[int] = None) -> "Naluri":
        """Putar ulang run dari `export_replay()` secara deterministik."""
        init = (data or {}).get("initial")
        if not init:
            raise ValueError("data replay tanpa 'initial'")
        obj = cls.from_dict(init)
        log = list((data or {}).get("events") or [])
        for i, entri in enumerate(log):
            if until is not None and i >= int(until):
                break
            obj.tick(events=entri.get("events") or None,
                     action_cost=bool(entri.get("action_cost", False)))
        return obj

    def enable_profiling(self, aktif: bool = True) -> Dict[str, Any]:
        """Nyalakan profiler bawaan (akumulasi waktu per-seksi, stdlib saja)."""
        self._profiling = bool(aktif)
        if aktif:
            self._profile = {}
            self._profile_ticks = 0
        return {"profiling": self._profiling}

    def _profile_add(self, name: str, dt: float) -> None:
        slot = self._profile.get(name)
        if slot is None:
            slot = {"total": 0.0, "n": 0, "max": 0.0}
            self._profile[name] = slot
        slot["total"] += float(dt)
        slot["n"] += 1
        if dt > slot["max"]:
            slot["max"] = float(dt)

    def profile_report(self) -> Dict[str, Any]:
        """Laporan profiler: seksi tersibuk (mirip cProfile ringkas)."""
        total = sum(s["total"] for s in self._profile.values()) or 1e-9
        items = sorted(self._profile.items(), key=lambda kv: kv[1]["total"],
                       reverse=True)
        return {
            "profiling": self._profiling,
            "ticks": self._profile_ticks,
            "sections": [{"name": n, "total_ms": round(s["total"] * 1000, 3),
                          "avg_ms": round(s["total"] / max(1, s["n"]) * 1000, 4),
                          "max_ms": round(s["max"] * 1000, 3),
                          "pct": round(100 * s["total"] / total, 1)}
                         for n, s in items],
            "jejak": (self.jejak.performance_report()
                      if getattr(self, "jejak", None) is not None else None),
        }

    def enable_ritual(self, aktif: bool = True) -> Dict[str, Any]:
        """Nyalakan/matikan perilaku ritual (utilitas nol)."""
        self.params["enable_ritual"] = bool(aktif)
        return {"enable_ritual": bool(self.params.get("enable_ritual", False)),
                "arketipe": (self.ritual._archetype
                             if getattr(self, "ritual", None) else None)}

    def lakukan_ritual(self, ritual: Any = None,
                       konteks: str = "idle") -> Dict[str, Any]:
        """Jalankan satu ritual secara eksplisit (mis. untuk cutscene)."""
        if not self._ritual_aktif():
            return {}
        try:
            return self.ritual.perform(ritual, konteks=konteks)
        except Exception as _galat_diagnostik_155:
            _diag.catat('naluri.Naluri.lakukan_ritual', "galat pada jalur fallback", galat=_galat_diagnostik_155, jalur=155)
            return {}

    def attach_jejak(self, jejak: Any) -> Dict[str, Any]:
        """Sambungkan JEJAK agar presentasi dapat mengisahkan autobiografi.

        Dipanggil otomatis oleh JejakPrediksi(naluri=...) bila lapisan
        presentasi ada. `jejak` bertipe JejakPrediksi (duck-typed).
        """
        self.jejak = jejak
        if getattr(self, "presentasi", None) is not None:
            try:
                self.presentasi.set_jejak(jejak)
            except Exception as _galat_diagnostik_156:
                _diag.catat('naluri.Naluri.attach_jejak', "galat pada jalur fallback", galat=_galat_diagnostik_156, jalur=156)
                pass
        return {"jejak": jejak is not None,
                "presentasi": self._presentasi_aktif()}

    def observe_player(self, action: str, aktor: str = "Player",
                       meta: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
        """Catat tindakan Player agar JEJAK dapat mengenali POLA bermainnya.

        Meneruskan ke `jejak.observe_actor` (duck-typed). Pola yang kuat otomatis
        menulis identitas/batas di lapisan kesadaran (lihat efek meta-pattern).
        """
        jejak = getattr(self, "jejak", None)
        if jejak is None:
            return {"entry": None, "pola_baru": []}
        try:
            return jejak.observe_actor(aktor, action,
                                       tick=self.tick_count, meta=meta)
        except Exception as _galat_diagnostik_157:
            _diag.catat('naluri.Naluri.observe_player', "galat pada jalur fallback", galat=_galat_diagnostik_157, jalur=157)
            return {"entry": None, "pola_baru": []}

    def pattern_report(self, aktor: Optional[str] = None) -> Dict[str, Any]:
        """Pola kebiasaan aktor yang dikenali JEJAK (untuk dialog/HUD)."""
        jejak = getattr(self, "jejak", None)
        if jejak is None:
            return {"pola": [], "jumlah": 0}
        try:
            return jejak.pattern_report(aktor)
        except Exception as _galat_diagnostik_158:
            _diag.catat('naluri.Naluri.pattern_report', "galat pada jalur fallback", galat=_galat_diagnostik_158, jalur=158)
            return {"pola": [], "jumlah": 0}

    def enable_nurani(self, *pilar: str, semua: bool = True) -> Dict[str, bool]:
        """Nyalakan (atau dengan `semua=False`, matikan) pilar NURANI.

        Tanpa argumen: semua pilar. Nama pilar: affective_memory,
        layered_calibration, plastic_setpoints, interoception,
        conflict_resolution, circadian, flow_state. Mengembalikan keadaan
        akhir seluruh pilar.
        """
        if self.nurani is None:
            return {}
        return self.nurani.set_pillars(tuple(pilar) if pilar else None, aktif=semua)

    # -------------------- HUD / niat untuk UI (fix #7) --------------------
    def set_hud_labels(self,
                       intents: Optional[Dict[str, str]] = None,
                       moods: Optional[Dict[str, str]] = None,
                       emosi: Optional[Dict[str, str]] = None) -> None:
        """Inject label HUD per NPC/per bahasa (i18n ringan untuk fix #5).

        Contoh: naluri.set_hud_labels(intents={"afiliasi": "wants to chat"},
                                     emosi=EMOSI_LABELS["en"])
        """
        if intents:
            self.hud_intents.update({str(k): str(v) for k, v in intents.items()})
        if moods:
            self.hud_moods.update({str(k): str(v) for k, v in moods.items()})
        if emosi:
            self.hud_emosi.update({str(k): str(v) for k, v in emosi.items()})

    def mood_label(self) -> str:
        """Label mood satu kata dari kuadran valensi x arousal (untuk HUD)."""
        m = self.mood()
        if m.valence >= 0.0:
            key = "bersemangat" if m.arousal >= 0.5 else "tenang"
        else:
            key = "gelisah" if m.arousal >= 0.5 else "murung"
        return self.hud_moods.get(key, key)

    def intent(self) -> Dict[str, Any]:
        """Niat NPC untuk hover UI — ringkas dan terbaca pemain.

        Prioritas: tidur (terjadwal/kognitif) > goal teratas > santai.
        `teks` siap ditampilkan; `alasan` untuk tooltip; tanpa angka debug.
        """
        perlu, alasan = self.should_sleep()
        if perlu:
            teks = (self.hud_intents.get("tidur")
                    or "sedang mencari tempat untuk tidur")
            return {"jenis": "tidur", "drive": None, "urgensi": 0.0,
                    "teks": teks, "alasan": alasan}
        drive_goal = None
        if self.goals:
            g = self.goals[0]
            child = g.active_subgoal()
            task = child.statement if child is not None else g.statement
            drive_goal = {"jenis": "subgoal" if child is not None else "goal",
                          "drive": child.drive if child is not None else g.drive,
                          "urgensi": round(float(child.urgency if child is not None else g.urgency), 3),
                          "teks": task if child is not None else self.hud_intents.get(g.drive, task),
                          "alasan": task,
                          "parent_drive": g.drive if child is not None else None}
        own = self.kesadaran.free_will_current_goal() if self._kesadaran_aktif() else None
        if own and (drive_goal is None
                    or float(own.get("prioritas", 0.0)) >= float(drive_goal.get("urgensi", 0.0))):
            return {"jenis": "free_will_goal", "drive": None,
                    "urgensi": round(float(own.get("prioritas", 0.0)), 3),
                    "goal_id": own.get("id"), "dipilih_sendiri": True,
                    "teks": str(own.get("tujuan", "")),
                    "alasan": str(own.get("alasan", "")),
                    "basis": "tanpa_drive"}
        if drive_goal is not None:
            return drive_goal
        return {"jenis": "santai", "drive": None, "urgensi": 0.0,
                "teks": self.hud_intents.get("santai", "santai — tidak ada desakan"),
                "alasan": ""}

    def hud_state(self, relasi_dengan: Optional[Any] = None) -> Dict[str, Any]:
        """Status kompak untuk HUD (bukan status() yang untuk debug).

        Berisi: nama, label mood, niat terbaca, bar drive 0..1 (siap gambar),
        fase sirkadian, info tidur, dan — bila EMPATI aktif — emosi dominan +
        peta intensitas. `relasi_dengan`: id entitas (mis. pemain) untuk
        menyertakan ringkasan relasi berlabel ("percaya"/"curiga"/...).
        Semua nilai sudah dibulatkan & JSON-safe.
        """
        m = self.mood()
        niat = self.intent()
        dom = self.emosi_dominan()
        h = {
            "nama": self.name,
            "mood": self.mood_label(),
            "valence": round(m.valence, 3),
            "arousal": round(m.arousal, 3),
            "niat": niat["teks"],
            "niat_detail": niat,
            "drive_dominan": niat.get("drive"),
            "bars": {d: round((jepit_drive(self.levels[d]) + 1.0) / 2.0, 3)
                     for d in DRIVES},
            "tidur": niat["jenis"] == "tidur",
            "fase": self._fase_lokal(),
            "kepribadian": self.personality_name or "kustom",
            "tahap": self.stage,
            "lod": self.lod_mode,
            "emosi": {
                "dominan": (self.hud_emosi.get(dom[0], dom[0]) if dom
                            else self.hud_emosi.get("netral", "netral")),
                "intensitas": round(dom[1], 2) if dom else 0.0,
                "peta": {e: round(self.emosi[e], 2) for e in EMOSI},
            },
        }
        if relasi_dengan is not None:
            r = self.relasi(relasi_dengan)
            h["relasi"] = {"id": r["id"], "nama": r["nama"],
                           "label": self.label_relasi(r),
                           "valensi": round(r["valensi"], 2),
                           "kepercayaan": round(r["kepercayaan"], 2),
                           "akrab": round(r["akrab"], 2), "n": r["n"]}
        # PERSEPSI (gated): fokus atensi terakhir + jumlah alarm palsu —
        # bahan narasi "dia seperti melihat sesuatu".
        if self._persepsi_aktif():
            st = self.persepsi_state()
            h["persepsi"] = {"alarm_palsu": st["alarm_palsu"],
                             "terakhir": st["terakhir"]}
        # INTROSPEKSI (gated): akurasi interoseptif + meta-d' + sadar diri
        if self._introspeksi_aktif():
            ist = self.introspeksi()
            h["introspeksi"] = {
                "akurasi": ist.get("akurasi", 0.0),
                "kepercayaan": ist.get("kepercayaan_global", 0.0),
                "meta_d": ist.get("meta_d_global", 0.0),
                "sadar": self.sadar_diri(),
                "narasi": ist.get("narasi_terakhir", "")[:120]
            }
        # KESADARAN (gated): fokus sadar, monolog batin, rasa tubuh, agensi.
        if self._kesadaran_aktif():
            h["kesadaran"] = self.kesadaran.hud_state()
        # PRESENTASI (gated): ekspresi, tatapan, napas, postur, ujaran terakhir.
        if self._presentasi_aktif():
            h["presentasi"] = self.presentasi.hud_state(relasi_dengan)
            # UI/UX (konsep 6): indikator psikologis + tag dialog dinamis,
            # menggantikan "stat bar" mentah.
            h["indikator"] = self.presentasi.indikator_psikologis()
            h["tag_dialog"] = self.presentasi.tag_dialog()
        # RITUAL (gated): kebiasaan idiosyncratic terakhir + arketipe.
        if self._ritual_aktif():
            h["ritual"] = self.ritual.state()
        h["ringkasan"] = self.brief()
        return h

    def brief(self) -> str:
        """Satu baris untuk bubble/label: 'Rina — tenang; ingin mengobrol ...'.

        Bila EMPATI aktif dan ada emosi dominan, emosinya ikut disebut:
        'Rama — gelisah [takut 0.42]; sedang waspada ...'.
        Bila INTROSPEKSI aktif dan sadar diri, ditandai [introspeksi].
        """
        niat = self.intent()
        nama = (self.name + " — ") if self.name else ""
        dom = self.emosi_dominan()
        emosi_txt = ""
        if dom:
            label = self.hud_emosi.get(dom[0], dom[0])
            emosi_txt = f" [{label} {dom[1]:.2f}]"
        # PERSEPSI: alarm palsu baru = NPC bereaksi pada bayangan.
        if (self._persepsi_aktif() and self._persepsi_log
                and self._persepsi_log[-1]["jenis"] == "alarm_palsu"
                and self.tick_count - self._persepsi_log[-1]["tick"] <= 3):
            emosi_txt += " [seperti melihat sesuatu]"
        # INTROSPEKSI: sadar diri
        if self._introspeksi_aktif() and self.sadar_diri():
            emosi_txt += " [introspeksi]"
        if self._coping_focus and int(self._coping_focus.get("remaining", 0)) > 0:
            emosi_txt += f" [fokus: {self._coping_focus.get('topic', '')[:24]}]"
        # KESADARAN: monolog batin + tubuh yang dirasakan + rasa agensi.
        batin_txt = ""
        if self._kesadaran_aktif():
            ks = self.kesadaran.hud_state()
            if ks.get("monolog"):
                batin_txt = f' [{ks["monolog"][:60]}]'
            if ks.get("felt"):
                batin_txt += f' [{ks["felt"]}]'
            if ks.get("agensi", 1.0) < 0.35:
                batin_txt += " [bukan aku yang melakukannya]"
        # PRESENTASI: tag ekspresi/wajah singkat agar bubble terasa hidup.
        if self._presentasi_aktif():
            try:
                wajah = (self.presentasi.ekspresi() or {}).get("wajah", "")
                if wajah:
                    batin_txt += f" [{wajah}]"
            except Exception as _galat_diagnostik_159:
                _diag.catat('naluri.Naluri.brief', "galat pada jalur fallback", galat=_galat_diagnostik_159, jalur=159)
                pass
        narasi = f"{nama}{self.mood_label()}{emosi_txt}{batin_txt}; {niat['teks']}"
        if self.context_aktif:
            ctx = max(self.context_aktif, key=lambda c: float(c.get("salience", 0.0)))
            narasi += f"; masih mengingat {ctx.get('stimulus', '')[:48]}"
        return narasi

    # -------------------- telemetri kesehatan --------------------
    def health_check(self) -> Dict[str, Any]:
        """Diagnostik anomali dengan ambang eksplisit dan gate per pilar.

        Pilar mati menghasilkan status ``inactive`` (bukan alarm). Ambang:
        rasio penolakan skala >5, EMA kalibrasi >0.4 setelah >200 sampel,
        alarm persepsi palsu/tick >0.1, atau semua sensitivitas belajar
        berada pada rentang [1.9, 2.0].
        """
        nur = self.nurani
        calibration_on = bool(nur is not None and nur.enabled("layered_calibration"))
        perception_on = bool(nur is not None and nur.enabled("perception")
                             and self._persepsi_aktif())
        checks: Dict[str, Dict[str, Any]] = {}
        anomalies: List[Dict[str, Any]] = []

        accepted = int(nur.scale_accepted) if nur is not None else 0
        rejected = int(nur.scale_rejected) if nur is not None else 0
        if not calibration_on:
            checks["scale_stability"] = {
                "status": "inactive", "pillar": "layered_calibration",
                "accepted": accepted, "rejected": rejected,
                "ratio_rejected_accepted": None,
            }
        else:
            ratio = (rejected / accepted) if accepted else (float("inf") if rejected else 0.0)
            ratio_out: Any = "infinite" if math.isinf(ratio) else round(ratio, 4)
            scale_status = "insufficient_data" if accepted + rejected == 0 else "ok"
            if ratio > 5.0:
                scale_status = "anomaly"
                anomalies.append({
                    "code": "scale_unstable", "severity": "warning",
                    "message": "Skala adaptif lebih sering ditolak daripada diterima.",
                    "ratio_rejected_accepted": ratio_out,
                    "accepted": accepted, "rejected": rejected,
                })
            checks["scale_stability"] = {
                "status": scale_status, "pillar": "layered_calibration",
                "accepted": accepted, "rejected": rejected,
                "ratio_rejected_accepted": ratio_out,
                "threshold": "> 5",
            }

        samples = int(self._calibration_samples)
        ema = float(self._calibration_ema)
        if not calibration_on:
            checks["model_calibration"] = {
                "status": "inactive", "pillar": "layered_calibration",
                "samples": samples, "calibration_ema": round(ema, 4),
            }
        else:
            model_status = "insufficient_data" if samples <= 200 else "ok"
            if samples > 200 and ema > 0.4:
                model_status = "anomaly"
                anomalies.append({
                    "code": "poor_calibration", "severity": "critical",
                    "message": "Galat kalibrasi tetap tinggi setelah lebih dari 200 sampel.",
                    "calibration_ema": round(ema, 4), "samples": samples,
                })
            checks["model_calibration"] = {
                "status": model_status, "pillar": "layered_calibration",
                "samples": samples, "calibration_ema": round(ema, 4),
                "threshold": {"samples": "> 200", "ema": "> 0.4"},
            }

        false_alarms = int(self.persepsi_alarm_palsu)
        ticks = int(self.tick_count)
        false_alarm_rate = (false_alarms / ticks) if ticks > 0 else (
            float("inf") if false_alarms else 0.0)
        if not perception_on:
            checks["perception_false_alarms"] = {
                "status": "inactive", "pillar": "perception",
                "false_alarms": false_alarms, "ticks": ticks,
                "rate": None,
            }
            checks["perceptual_saturation"] = {
                "status": "inactive", "pillar": "perception",
                "sensitivities": (dict(nur.sensitivitas) if nur is not None else {}),
            }
        else:
            rate_out: Any = "infinite" if math.isinf(false_alarm_rate) else round(false_alarm_rate, 4)
            alarm_status = "insufficient_data" if ticks == 0 and false_alarms == 0 else "ok"
            if false_alarm_rate > 0.1:
                alarm_status = "anomaly"
                anomalies.append({
                    "code": "hypervigilance", "severity": "warning",
                    "message": "Frekuensi alarm persepsi palsu melebihi 0,1 per tick.",
                    "false_alarms": false_alarms, "ticks": ticks,
                    "rate": rate_out,
                })
            checks["perception_false_alarms"] = {
                "status": alarm_status, "pillar": "perception",
                "false_alarms": false_alarms, "ticks": ticks,
                "rate": rate_out, "threshold": "> 0.1",
            }
            sensitivities = {d: float(v) for d, v in nur.sensitivitas.items()}
            saturated = bool(sensitivities) and all(1.9 <= v <= 2.0
                                                   for v in sensitivities.values())
            saturation_status = "anomaly" if saturated else "ok"
            if saturated:
                anomalies.append({
                    "code": "perceptual_learning_saturated", "severity": "warning",
                    "message": "Semua sensitivitas perseptual telah mendekati batas atas belajar.",
                    "sensitivities": {d: round(v, 4) for d, v in sensitivities.items()},
                })
            checks["perceptual_saturation"] = {
                "status": saturation_status, "pillar": "perception",
                "sensitivities": {d: round(v, 4) for d, v in sensitivities.items()},
                "threshold": "all in [1.9, 2.0]",
            }

        levels = {"ok": 0, "warning": 1, "critical": 2}
        severity = max((str(a["severity"]) for a in anomalies),
                       key=lambda x: levels.get(x, 0), default="ok")
        return {
            "diagnostik": _diag.laporan(),
            "healthy": not anomalies,
            "severity": severity,
            "tick": ticks,
            "pillars": {
                "layered_calibration": calibration_on,
                "perception": perception_on,
            },
            "checks": checks,
            "anomalies": anomalies,
        }

    # -------------------- laporan --------------------
    def status(self) -> Dict[str, Any]:
        mood = self.mood()
        perlu_tidur, alasan_tidur = self.should_sleep()
        return {
            "name": self.name,
            "stage": self.stage,
            "personality": self.personality_name,
            "lod": self.lod_status(),
            "memory_compaction": copy.deepcopy(self._last_memory_compaction),
            "health": self.health_check(),
            "sleep_mode": self.sleep_mode,
            "weights": dict(self.weights),
            "levels": dict(self.levels),
            "urgency": dict(self.urgency),
            "deficit_ticks": dict(self.deficit_ticks),
            "mood": {"valence": mood.valence, "arousal": mood.arousal},
            "modulation": mood.modulation(),
            "goals": [g.to_dict() for g in self.goals],
            "working_memory": copy.deepcopy(self.context_aktif),
            "eligibility": {"active_traces": len(self._eligibility_traces),
                            "action_values": copy.deepcopy(self._action_values)},
            "coping": self.coping_state(),
            "calibration_error": self._calibration_ema,
            "calibration_samples": self._calibration_samples,
            "unverified_predictions": self._unverified_predictions,
            "utility_scale": self.estimate_scale(),
            "should_sleep": perlu_tidur,
            "sleep_reason": alasan_tidur,
            "slept_count": self.slept_count,
            "actions_taken": self.actions_taken,
            "tick": self.tick_count,
            # EMPATI: emosi selalu terlihat (nol semua selama flag mati) dan
            # jumlah slot relasi sosial (0 bila NURANI tak ada / pilar mati).
            "emosi": self.emosi_state(),
            "relasi_slot": (self.nurani.social_size
                            if self.nurani is not None else 0),
            # PERSEPSI: counter selalu terlihat; detail saluran hanya saat
            # pilar aktif (persepsi_state sudah memuat "aktif").
            "persepsi": self.persepsi_state(),
            # NURANI (konsep 17): meta-plastisitas selalu terlihat di status,
            # termasuk saat semua pilar mati (maka `tersedia`/`pillars` False).
            "nurani": self.meta_status(),
            "introspeksi": self.introspeksi() if self.nurani and self.nurani.enabled("introspection") else {"aktif": False},
            # KESADARAN: laporan terpadu seluruh sub-lapisan.
            "kesadaran": (self.kesadaran.report() if self._kesadaran_aktif()
                          else {"aktif": False}),
            # PRESENTASI (Pycos): snapshot kanal nonverbal + prosodi + riwayat.
            "presentasi": (self.presentasi.snapshot() if self._presentasi_aktif()
                           else {"aktif": False}),
            # RITUAL (utilitas nol): arketipe + riwayat kebiasaan.
            "ritual": (self.ritual.state() if self._ritual_aktif()
                       else {"aktif": False}),
        }

    # -------------------- serialisasi (fix #1) --------------------
    def to_dict(self, profil: str = "penuh") -> Dict[str, Any]:
        """Serialisasi penuh state Naluri ke struktur JSON-safe.

        Mencakup: drive/urgensi/goal, params & weights, kalibrator + pasangan
        prediksi (nested), log terbatas, tick_history, keadaan RNG (agar run
        yang di-load deterministik lanjut), lexicon instans (termasuk yang
        di-inject), LOD & buffer event, siklus tidur terjadwal, label HUD,
        dan state NURANI bersarang (memori afektif, interosepsi, kalibrasi).
        Params NURANI tidak diduplikasi — ia hidup di `params` (satu sumber).
        """
        st = self._rng.getstate()
        return {
            "format": "naluri/4",
            "name": self.name,
            "stage": self.stage,
            "personality": {"name": self.personality_name,
                            "blend": self._personality_blend,
                            "watak_keys": list(self._watak_keys),
                            "lahir": self._lahir_diterapkan},
            "weights": dict(self.weights),
            "levels": dict(self.levels),
            # WATAK: deep-copy — params bisa memuat dict per-drive bersarang.
            "params": copy.deepcopy(self.params),
            "urgency": dict(self.urgency),
            "deficit_ticks": dict(self.deficit_ticks),
            "goals": [g.to_dict() for g in self.goals],
            "tick_count": self.tick_count,
            "subjective_tick_count": float(self.subjective_tick_count),
            "tick_history": [dict(h) for h in self.tick_history],
            "delta_log": [dict(x) for x in self.delta_log],
            "delta_log_max": self._DELTA_LOG_MAX,
            "working_memory": {
                "active": copy.deepcopy(self.context_aktif),
                "repeat": copy.deepcopy(self._context_repeat),
            },
            "eligibility": {
                "traces": copy.deepcopy(self._eligibility_traces),
                "action_values": copy.deepcopy(self._action_values),
                "last_assignments": copy.deepcopy(self._last_credit_assignments),
            },
            "actions_taken": self.actions_taken,
            "slept_count": self.slept_count,
            "total_sleep_seconds": self.total_sleep_seconds,
            "last_sleep_tick": self._last_sleep_tick,
            "slept_cycle": self._slept_cycle,
            "calibration": {"ema": self._calibration_ema,
                            "samples": self._calibration_samples,
                            "unverified": self._unverified_predictions},
            "prediction_log": [dict(x) for x in self._prediction_log],
            "pred_pairs": [[float(p), float(r)] for p, r in self._pred_pairs],
            "scale": self._scale,
            "rng_state": [int(st[0]), [int(x) for x in st[1]], st[2]],
            "lexicon": {w: dict(dv) for w, dv in self.lexicon.items()},
            "tag_lexicon": {t: dict(dv) for t, dv in self.tag_lexicon.items()},
            "hud_labels": {"intents": dict(self.hud_intents),
                           "moods": dict(self.hud_moods)},
            "lod": {"mode": self.lod_mode, "divisor": self.lod_divisor,
                    "accum": self._lod_accum,
                    "buffer": [dict(e) for e in self._event_buffer]},
            # EMPATI: keadaan emosi + jejak log + label HUD emosi
            "emosi": dict(self.emosi),
            "emosi_log": [dict(x) for x in self._emosi_log],
            "emosi_log_max": self._EMOSI_LOG_MAX,
            "emosi_prev": {"valensi": self._emosi_val_prev,
                           "keamanan": self._emosi_keamanan_prev,
                           "ingin": self._emosi_ingin_prev},
            "hud_labels_emosi": dict(self.hud_emosi),
            "coping": {"focus": copy.deepcopy(self._coping_focus)},
            "selisih_self": {"nilai": float(self._selisih_self),
                              "beruntun": int(self._selisih_self_beruntun),
                              "disorientasi": float(self._disorientasi_identitas),
                              "log": [dict(x) for x in self._selisih_self_log],
                              "interupsi": [dict(x) for x in self._interupsi_internal]},
            # PERSEPSI: log + counter + akumulator stimulus tick berjalan
            # (state saluran d'/adaptasi/habituasi ikut di blok "nurani").
            "persepsi": {"log": [dict(x) for x in self._persepsi_log],
                         "log_max": self._PERSEPSI_LOG_MAX,
                         "alarm_palsu": self.persepsi_alarm_palsu,
                         "stim": dict(self._persepsi_stim)},
            "nurani": (self.nurani.to_dict(include_params=False)
                       if self.nurani is not None else None),
            # KESADARAN: seluruh state lapisan (save lama tanpa
            # blok ini tetap termuat — dari_dict membuat objek default).
            "kesadaran": (self.kesadaran.to_dict()
                          if getattr(self, "kesadaran", None) is not None
                          else None),
            # PRESENTASI (Pycos performance layer): state kanal nonverbal,
            # prosodi, riwayat ujaran (jejak eksternal TIDAK disimpan di sini).
            "presentasi": (self.presentasi.to_dict()
                           if getattr(self, "presentasi", None) is not None
                           else None),
            # RITUAL (perilaku utilitas-nol): riwayat & arketipe.
            "ritual": (self.ritual.to_dict()
                       if getattr(self, "ritual", None) is not None else None),
        }

    @classmethod
    def migrate(cls, data: Mapping[str, Any]) -> Dict[str, Any]:
        """Salinan snapshot tervalidasi dalam format naluri terbaru."""
        from pycos.dukungan.validasi_state import validasi_state
        return validasi_state(data, "Naluri")

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Naluri":
        """Bangun kembali Naluri dari hasil `to_dict()` (toleran field hilang)."""
        from pycos.inti.naluri import Nurani
        from pycos.dukungan.validasi_state import validasi_state
        data = validasi_state(data, "Naluri")
        data = data or {}
        obj = cls(stage=str(data.get("stage", "dewasa")),
                  params=data.get("params"),
                  name=data.get("name"))
        kep = data.get("personality") or {}
        obj.personality_name = kep.get("name")
        obj._personality_blend = float(kep.get("blend", 1.0))
        # WATAK: pulihkan jejak kunci watak + penanda backstory. Save lama
        # tanpa field ini tetap termuat; NPC bernama dianggap sudah "lahir"
        # agar tidak pernah di-seed ulang setelah load.
        obj._watak_keys = [str(k) for k in (kep.get("watak_keys") or [])]
        obj._lahir_diterapkan = bool(kep.get(
            "lahir", obj.personality_name is not None))
        for d in DRIVES:
            if d in (data.get("weights") or {}):
                obj.weights[d] = float(data["weights"][d])
            if d in (data.get("levels") or {}):
                obj.levels[d] = float(data["levels"][d])
            if d in (data.get("urgency") or {}):
                obj.urgency[d] = float(data["urgency"][d])
            if d in (data.get("deficit_ticks") or {}):
                obj.deficit_ticks[d] = int(data["deficit_ticks"][d])
        obj.goals = [Goal.from_dict(g) for g in (data.get("goals") or [])]
        obj.tick_count = int(data.get("tick_count", 0))
        # Save lama tidak membedakan jam; mulai dari jam objektif agar memori
        # yang dimuat tidak mengalami lompatan negatif pada _recency.
        obj.subjective_tick_count = max(0.0, float(data.get(
            "subjective_tick_count", obj.tick_count)))
        obj.tick_history = [dict(h) for h in (data.get("tick_history") or [])]
        obj.delta_log = [dict(x) for x in (data.get("delta_log") or [])]
        obj._DELTA_LOG_MAX = int(data.get("delta_log_max", 512))
        wm = data.get("working_memory") or {}
        obj.context_aktif = []
        for item in (wm.get("active") or []):
            if not isinstance(item, Mapping):
                continue
            dd = {d: jepit_drive(float((item.get("delta") or {}).get(d, 0.0)))
                  for d in DRIVES}
            obj.context_aktif.append({
                "key": str(item.get("key", obj._context_key(str(item.get("stimulus", ""))))),
                "stimulus": str(item.get("stimulus", ""))[:160],
                "salience": jepit_01(float(item.get("salience", 0.0))),
                "tick": int(item.get("tick", 0)),
                "last_decay_tick": int(item.get("last_decay_tick", item.get("tick", 0))),
                "age": max(0, int(item.get("age", 0))),
                "delta": dd, "source": str(item.get("source", ""))[:40],
                "repeat": max(1, int(item.get("repeat", 1))),
                "action": str(item.get("action", ""))[:80],
            })
        obj.context_aktif = obj.context_aktif[-5:]
        obj._context_repeat = {str(k): {"count": max(0, int(v.get("count", 0))),
                                       "last_t": int(v.get("last_t", 0)),
                                       "text": str(v.get("text", ""))[:120]}
                               for k, v in (wm.get("repeat") or {}).items()
                               if isinstance(v, Mapping)}
        el = data.get("eligibility") or {}
        obj._eligibility_traces = []
        for trace in (el.get("traces") or []):
            if not isinstance(trace, Mapping) or trace.get("drive") not in DRIVES:
                continue
            obj._eligibility_traces.append({
                "action": str(trace.get("action", ""))[:120],
                "drive": str(trace.get("drive")),
                "eligibility": jepit_01(float(trace.get("eligibility", 0.0))),
                "effect": jepit_drive(float(trace.get("effect", 0.0))),
                "tick": int(trace.get("tick", 0)), "last_tick": int(trace.get("last_tick", 0)),
                "context": str(trace.get("context", ""))[:120],
            })
        obj._eligibility_traces = obj._eligibility_traces[-max(1, int(obj.params.get("eligibility_max_traces", 64))):]
        obj._action_values = {}
        for name, value in (el.get("action_values") or {}).items():
            if not isinstance(value, Mapping):
                continue
            obj._action_values[str(name)] = {
                "value": jepit_drive(float(value.get("value", 0.0))),
                "n": max(0, int(value.get("n", 0))),
                "last_t": int(value.get("last_t", 0)),
                "drive_values": {d: jepit_drive(float((value.get("drive_values") or {}).get(d, 0.0)))
                                 for d in DRIVES},
                "drive_n": {d: max(0, int((value.get("drive_n") or {}).get(d, 0)))
                            for d in DRIVES},
            }
        obj._last_credit_assignments = [dict(x) for x in (el.get("last_assignments") or [])][-32:]
        obj.actions_taken = int(data.get("actions_taken", 0))
        obj.slept_count = int(data.get("slept_count", 0))
        obj.total_sleep_seconds = float(data.get("total_sleep_seconds", 0.0))
        obj._last_sleep_tick = int(data.get("last_sleep_tick", -10_000))
        obj._slept_cycle = int(data.get("slept_cycle", -1))
        kal = data.get("calibration") or {}
        obj._calibration_ema = float(kal.get("ema", 0.0))
        obj._calibration_samples = int(kal.get("samples", 0))
        obj._unverified_predictions = int(kal.get("unverified", 0))
        obj._prediction_log = [dict(x) for x in (data.get("prediction_log") or [])]
        obj._pred_pairs = [(float(p[0]), float(p[1]))
                           for p in (data.get("pred_pairs") or [])]
        obj._scale = float(data.get("scale", obj.params["scale_initial"]))
        # keadaan RNG: lanjutkan urutan acak persis dari titik simpan
        rs = data.get("rng_state")
        if rs and len(rs) == 3 and rs[1]:
            try:
                obj._rng.setstate((int(rs[0]), tuple(int(x) for x in rs[1]), rs[2]))
            except (ValueError, TypeError):
                pass
        if data.get("lexicon") is not None:
            obj.lexicon = {str(w): dict(dv) for w, dv in data["lexicon"].items()}
        if data.get("tag_lexicon") is not None:
            obj.tag_lexicon = {str(t): dict(dv)
                               for t, dv in data["tag_lexicon"].items()}
        obj._lexicon_dirty = True
        hud = data.get("hud_labels") or {}
        if hud.get("intents"):
            obj.hud_intents = {str(k): str(v) for k, v in hud["intents"].items()}
        if hud.get("moods"):
            obj.hud_moods = {str(k): str(v) for k, v in hud["moods"].items()}
        lod = data.get("lod") or {}
        obj.lod_mode = LOD_ALIASES.get(str(lod.get("mode", "penuh")).lower(), "penuh")
        obj.lod_divisor = max(1, int(lod.get("divisor", obj.lod_divisor)))
        obj._lod_accum = int(lod.get("accum", 0))
        obj._event_buffer = [dict(e) for e in (lod.get("buffer") or [])]
        # EMPATI: emosi + log + label (save lama "naluri/2" tanpa field ini
        # tetap termuat — default netral).
        for e, v in (data.get("emosi") or {}).items():
            key = EMOSI_ALIASES.get(str(e).lower())
            if key is not None:
                obj.emosi[key] = jepit_01(float(v))
        obj._emosi_log = [dict(x) for x in (data.get("emosi_log") or [])]
        obj._EMOSI_LOG_MAX = int(data.get("emosi_log_max", 64))
        ep = data.get("emosi_prev") or {}
        obj._emosi_val_prev = ep.get("valensi")
        obj._emosi_keamanan_prev = ep.get("keamanan")
        obj._emosi_ingin_prev = ep.get("ingin")
        if data.get("hud_labels_emosi"):
            obj.hud_emosi = {str(k): str(v)
                             for k, v in data["hud_labels_emosi"].items()}
        coping = data.get("coping") or {}
        focus = coping.get("focus")
        obj._coping_focus = (dict(focus) if isinstance(focus, Mapping) else None)
        if obj._coping_focus is not None:
            obj._coping_focus["topic"] = str(obj._coping_focus.get("topic", ""))[:120]
            obj._coping_focus["remaining"] = max(0, int(obj._coping_focus.get("remaining", 0)))
            obj._coping_focus["emotion_decay_multiplier"] = max(1.0, float(
                obj._coping_focus.get("emotion_decay_multiplier", 1.0)))
            if obj._coping_focus["remaining"] <= 0:
                obj._coping_focus = None
        ss = data.get("selisih_self") or {}
        obj._selisih_self = jepit_01(float(ss.get("nilai", 0.0)))
        obj._selisih_self_beruntun = max(0, int(ss.get("beruntun", 0)))
        obj._disorientasi_identitas = jepit_01(float(ss.get("disorientasi", 0.0)))
        obj._selisih_self_log = [dict(x) for x in (ss.get("log") or [])][-64:]
        obj._interupsi_internal = [dict(x) for x in (ss.get("interupsi") or [])][-64:]
        # PERSEPSI: save lama tanpa blok ini tetap termuat (default netral).
        ps = data.get("persepsi") or {}
        obj._persepsi_log = [dict(x) for x in (ps.get("log") or [])]
        obj._PERSEPSI_LOG_MAX = int(ps.get("log_max", 64))
        obj.persepsi_alarm_palsu = int(ps.get("alarm_palsu", 0))
        for d, v in (ps.get("stim") or {}).items():
            if d in obj._persepsi_stim:
                obj._persepsi_stim[d] = float(v)
        # NURANI: pulihkan state bersarang (memori afektif dsb.) dengan params
        # MILIK obj agar tetap satu sumber kebenaran seperti saat konstruksi.
        nur_data = data.get("nurani")
        if nur_data and Nurani is not None:
            obj.nurani = Nurani.from_dict(nur_data, params=obj.params)
        # KESADARAN: pulihkan state lapisan; save lama tanpa blok ini → default.
        pres_data = data.get("presentasi")
        if pres_data and getattr(obj, "presentasi", None) is not None:
            try:
                obj.presentasi.from_dict(pres_data)
            except Exception as _galat_diagnostik_160:
                _diag.catat('naluri.Naluri.from_dict', "galat pada jalur fallback", galat=_galat_diagnostik_160, jalur=160)
                pass
        rit_data = data.get("ritual")
        if rit_data and getattr(obj, "ritual", None) is not None:
            try:
                obj.ritual.from_dict(rit_data)
            except Exception as _galat_diagnostik_161:
                _diag.catat('naluri.Naluri.from_dict', "galat pada jalur fallback", galat=_galat_diagnostik_161, jalur=161)
                pass
        kes_data = data.get("kesadaran")
        if kes_data and getattr(obj, "kesadaran", None) is not None:
            try:
                obj.kesadaran.from_dict(kes_data)
            except Exception as _galat_diagnostik_162:
                _diag.catat('naluri.Naluri.from_dict', "galat pada jalur fallback", galat=_galat_diagnostik_162, jalur=162)
                pass
        if obj.lod_mode in ("latar", "beku"):
            obj.kompres_memori(obj.lod_mode)
        obj.batasi_memori()
        return obj

    def to_json(self, profil: str = "penuh", **json_kwargs: Any) -> str:
        """`to_dict()` sebagai string JSON (default: utf-8 terbaca)."""
        json_kwargs.setdefault("ensure_ascii", False)
        return json.dumps(self.to_dict(profil=profil), **json_kwargs)

    @classmethod
    def from_json(cls, s: str) -> "Naluri":
        return cls.from_dict(json.loads(s))

    def save(self, path: str, *, profil: str = "penuh") -> str:
        """Simpan state ke berkas JSON. Mengembalikan path."""
        from pycos.dukungan.persistensi import simpan_json
        return simpan_json(path, self.to_dict(profil=profil))

    @classmethod
    def load(cls, path: str) -> "Naluri":
        """Muat state dari berkas JSON hasil `save()`."""
        from pycos.dukungan.persistensi import muat_json
        return cls.from_dict(muat_json(path))

    # -------------------- demo (stdlib saja) --------------------
    @classmethod
    def demo(cls, ticks: int = 90, seed: int = 7) -> "Naluri":
        """Simulasi harian; implementasi showcase dimuat hanya saat dipanggil."""
        from pycos.inti.demo.skenario import _simulasi_harian
        return _simulasi_harian(cls, ticks=ticks, seed=seed)


Naluri.__module__ = "pycos.inti.naluri"
