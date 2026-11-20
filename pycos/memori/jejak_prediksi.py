# -*- coding: utf-8 -*-
"""JEJAK (pycos.memori.jejak_prediksi) — memori episodik dan prediksi.

Modul stdlib-only yang dapat dipasang berdampingan dengan Naluri/NURANI.
JEJAK menyimpan pasangan stimulus–aksi–hasil, mencari pengalaman yang mirip,
lalu menggabungkan prediksi internal dengan bukti lingkungan yang bobotnya
sengaja dibatasi.

Bobot default:
    memori episodik (internal) : 0.75
    prior Naluri/NURANI        : 0.15
    bukti langsung lingkungan : 0.10

Jadi 90% prediksi berasal dari model internal dan 10% dari bukti eksternal.
Ini adalah bias desain yang dapat dikonfigurasi, bukan klaim bahwa otak biologis
selalu memakai rasio tersebut.

API utama:
    jejak.record_experience(stimulus, aksi, hasil, context=..., tick=...)
    jejak.predict(stimulus, action=..., context=..., environment=...)
    jejak.rank_actions(stimulus, candidates, context=..., environment=...)
    jejak.reinforce(prediction, actual_outcome, ...)
    jejak.to_dict() / from_dict() / save() / load()

Kinerja & kognisi lanjutan:
    jejak.observe_actor(aktor, aksi)          — meta-pattern kebiasaan aktor
    jejak.set_retrieve_mode("coarse")         — MinHash (kueri kasar/cepat)
    jejak.consolidate_memory()                — konsolidasi memori saat tidur
    jejak.performance_report()                — statistik indeks & waktu retrieve
    jejak.autobiographical_timeline() / life_chapters() / future_simulation()

Indeks terbalik token→episode membuat _retrieve() memindai kandidat kecil
(O(k)) alih-alih seluruh korpus (O(n)); cache fitur + MinHash mempercepat
similarity. State turunan (indeks/cache/signature) TIDAK diserialisasi
(selective persistence) dan dibangun ulang saat load.

Retrieval mencatat akses dan dapat mematikan episode yang melampaui retensi;
bekas tanpa isi disimpan di nekropolis. Isi episode tetap tidak ditulis ulang
oleh prediksi secara default. Reconsolidation isi hanya terjadi bila gate
``enable_reconstructive_recall`` dinyalakan eksplisit. Integrasi dengan Naluri
bersifat duck-typed; Naluri tidak wajib diimpor oleh modul ini.
"""
from __future__ import annotations

import json
import heapq
import math
import random
import re
import time
import zlib
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Set, Tuple

if not __package__:  # berkas dieksekusi langsung, bukan sebagai modul paket
    # `python3 pycos/memori/jejak_prediksi.py`: kenalkan direktori
    # induk paket ke sys.path supaya impor `pycos.*` tetap resolve tanpa
    # instalasi maupun PYTHONPATH manual.
    import os as _os
    import sys as _sys

    _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.dirname(
        _os.path.abspath(__file__)))))
    del _os, _sys

from pycos.dukungan.numerik import jepit, jepit_01, jepit_drive
from pycos.dukungan.patching import (install_method, install_methods,
                                     optional_module, wrap_method)


from pycos.dukungan import konstanta as _konstanta_drive
DRIVES = _konstanta_drive.DRIVES
DEFAULT_WEIGHTS: Dict[str, float] = {
    "memory": 0.75,
    "instinct": 0.15,
    "environment": 0.10,
}
DEFAULT_DRIVE_WEIGHTS: Dict[str, float] = {
    "energi": 1.1,
    "keamanan": 1.4,
    "keingintahuan": 0.9,
    "penguasaan": 1.0,
    "afiliasi": 1.0,
    "koherensi": 1.1,
}

_WORD_RE = re.compile(r"[a-z0-9]+", re.IGNORECASE)
_STOP_WORDS = {
    # Indonesia
    "yang", "dan", "atau", "di", "ke", "dari", "dengan", "untuk",
    "pada", "dalam", "itu", "ini", "saat", "ketika", "oleh", "karena",
    "saya", "aku", "agen", "sebuah", "ada", "terjadi", "melihatnya",
    "terhadap", "lalu", "setelah", "sebelum", "dapat", "bisa", "akan",
    "lagi", "sangat", "lebih", "tidak", "tak", "nya", "pun", "para",
    "depan", "terlihat", "tampak", "muncul",
    # English
    "the", "and", "or", "at", "to", "from", "with", "for", "in", "on",
    "when", "while", "after", "before", "this", "that", "there", "was",
    "were", "is", "are", "it", "its", "a", "an", "of", "by", "as",
}

# Alias leksikal ringan agar pola lintas bentuk/bahasa tetap bisa bertemu.
# Ini bukan NLP penuh atau model bahasa; pola pengalaman tetap sumber utama.
_ALIASES: Dict[str, str] = {
    "fire": "api", "fires": "api", "flame": "api", "flames": "api",
    "bonfire": "api", "bara": "api", "kebakaran": "api",
    "burn": "bakar", "burns": "bakar", "burned": "bakar",
    "burning": "bakar", "membakar": "bakar", "terbakar": "bakar",
    "dibakar": "bakar", "panas": "panas", "heat": "panas", "hot": "panas",
    "smoke": "asap", "asap": "asap",
    "danger": "bahaya", "dangerous": "bahaya", "berbahaya": "bahaya",
    "threat": "ancaman", "ancaman": "ancaman", "risk": "risiko",
    "risky": "risiko", "berisiko": "risiko", "unsafe": "tidakaman",
    "safe": "aman", "aman": "aman",
    "approach": "paparan", "approaching": "paparan", "mendekat": "paparan",
    "menyala": "api", "nyala": "api", "blazing": "api", "lit": "api",
    "mendekati": "paparan", "dekat": "paparan", "touch": "paparan",
    "touching": "paparan", "sentuh": "paparan", "menyentuh": "paparan",
    "pegang": "paparan", "memegang": "paparan", "handle": "paparan",
    "grab": "paparan",
    "avoid": "hindar", "avoiding": "hindar", "hindari": "hindar",
    "menghindari": "hindar", "menghindar": "hindar", "menjauh": "hindar",
    "menjauhi": "hindar", "mundur": "hindar", "lari": "hindar",
    "kabur": "hindar", "retreat": "hindar", "flee": "hindar",
    "observe": "amati", "observing": "amati", "inspect": "amati",
    "watch": "amati", "amati": "amati", "mengamati": "amati",
    "periksa": "amati", "melihat": "lihat", "lihat": "lihat",
}

_ACTION_FAMILIES: Dict[str, set[str]] = {
    "hindar": {
        "avoid", "avoiding", "hindari", "menghindari", "menghindar", "menjauh",
        "menjauhi", "jauhi", "mundur", "lari", "kabur", "retreat", "flee",
        "backoff", "menyelamatkan diri",
    },
    "paparan": {
        "approach", "approaching", "mendekat", "mendekati", "dekat", "touch",
        "touching", "sentuh", "menyentuh", "pegang", "memegang", "handle", "grab",
    },
    "amati": {
        "observe", "observing", "inspect", "watch", "amati", "mengamati",
        "periksa", "melihat", "lihat",
    },
}


def _clip(value: Any, low: float = -1.0, high: float = 1.0) -> float:
    """Jepit ke [low, high]; NaN/tak-numerik → 0 (lihat dukungan.numerik)."""
    return jepit(value, low, high)


def _read(obj: Any, key: str, default: Any = None) -> Any:
    if isinstance(obj, Mapping):
        return obj.get(key, default)
    return getattr(obj, key, default)


def _context_text(context: Any) -> str:
    if context is None:
        return ""
    if isinstance(context, str):
        return context
    if isinstance(context, Mapping):
        parts: List[str] = []
        for key in sorted(context, key=lambda x: str(x)):
            value = context[key]
            if value is None:
                continue
            if isinstance(value, (list, tuple, set)):
                value = " ".join(str(x) for x in value)
            parts.extend((str(key), str(value)))
        return " ".join(parts)
    if isinstance(context, (list, tuple, set)):
        return " ".join(str(x) for x in context)
    return str(context)


def _action_family(text: str) -> Optional[str]:
    words = set(_WORD_RE.findall(str(text or "").lower()))
    # Menghindari didahulukan agar frasa "jangan mendekat" tidak salah dibaca
    # sebagai aksi paparan hanya karena mengandung kata "dekat".
    for family in ("hindar", "paparan", "amati"):
        if words.intersection(_ACTION_FAMILIES[family]):
            return family
    return None


def _features(text: Any, action: bool = False) -> set[str]:
    raw = str(text or "").lower()
    out: set[str] = set()
    for word in _WORD_RE.findall(raw):
        word = _ALIASES.get(word, word)
        if word not in _STOP_WORDS and len(word) > 1:
            out.add(word)
    if action:
        family = _action_family(raw)
        if family:
            out.add("@aksi:" + family)
    return out


def _similarity(left: set[str], right: set[str]) -> float:
    """Kemiripan robust untuk kueri pendek: cakupan kueri lebih penting.

    Cue singkat seperti "api" tetap dapat menemukan episode "api panas
    membakar kulit", tanpa menganggap teks yang hanya berbagi stopword cocok.
    """
    if not left or not right:
        return 0.0
    overlap = len(left.intersection(right))
    if overlap == 0:
        return 0.0
    coverage = overlap / len(left)
    precision = overlap / len(right)
    jaccard = overlap / len(left.union(right))
    return jepit_01(0.55 * coverage + 0.25 * precision + 0.20 * jaccard)


def _normalise_outcome(outcome: Any) -> Dict[str, Any]:
    """Ubah angka/dict/objek outcome menjadi skema internal yang aman."""
    label = str(_read(outcome, "label", _read(outcome, "description", "")) or "")[:120]
    raw_deltas = _read(outcome, "drive_deltas", {}) or {}
    deltas: Dict[str, float] = {d: 0.0 for d in DRIVES}
    # Penanda apakah pemanggil memberi drive_deltas EKSPLISIT. Bila ya, nilai
    # itu otoritatif dan tidak boleh diturunkan ulang dari hazard — kalau
    # tidak, _normalise_outcome tidak idempoten dan save→load mengubah isi
    # ingatan (mis. keamanan 0.0 berubah menjadi -hazard).
    punya_deltas = False
    if isinstance(raw_deltas, Mapping):
        for drive, value in raw_deltas.items():
            if drive in deltas:
                deltas[drive] = _clip(value)
                punya_deltas = True

    has_impact = False
    raw_impact = 0.0
    if isinstance(outcome, (int, float)) and not isinstance(outcome, bool):
        raw_impact = _clip(outcome)
        has_impact = True
    else:
        for key in ("impact", "impact_score", "reward"):
            value = _read(outcome, key, None)
            if value is not None:
                raw_impact = _clip(value)
                has_impact = True
                break
        if not has_impact:
            success = _read(outcome, "success", None)
            if success is not None:
                raw_impact = 1.0 if bool(success) else -1.0
                has_impact = True

    raw_hazard = _read(outcome, "hazard", None)
    if raw_hazard is None:
        hazard = max(0.0, -raw_impact, -deltas.get("keamanan", 0.0))
    else:
        hazard = _clip(raw_hazard, 0.0, 1.0)
        if not has_impact:
            raw_impact = -hazard
            has_impact = True
        if (not punya_deltas) and abs(deltas.get("keamanan", 0.0)) < 1e-12 and hazard > 0.0:
            deltas["keamanan"] = -hazard

    if not has_impact:
        nonzero = [v for v in deltas.values() if abs(v) > 1e-12]
        raw_impact = sum(nonzero) / len(nonzero) if nonzero else 0.0
        hazard = max(0.0, -raw_impact, -deltas.get("keamanan", 0.0))

    return {
        "impact": _clip(raw_impact),
        "drive_deltas": deltas,
        "hazard": _clip(hazard, 0.0, 1.0),
        "label": label,
    }


def _subjective_time_snapshot(naluri: Any) -> Dict[str, Any]:
    """Snapshot jam subjektif dari Naluri tanpa mengikat impor ke modulnya."""
    hasil: Dict[str, Any] = {"episode_scale": 1.0, "clock_rate": 1.0,
                             "subjective_tick": None, "rasa": "netral"}
    if naluri is None:
        return hasil
    try:
        fn = getattr(naluri, "subjective_time_profile", None)
        profile = fn() if callable(fn) else {}
        if isinstance(profile, Mapping):
            hasil["episode_scale"] = jepit(float(
                profile.get("episode_scale", profile.get("skala", 1.0))), 0.20, 3.50)
            hasil["clock_rate"] = jepit(float(
                profile.get("clock_rate", profile.get("laju", 1.0))), 0.20, 2.80)
            hasil["rasa"] = str(profile.get("rasa", "netral"))[:32]
    except (TypeError, ValueError, AttributeError):
        pass
    try:
        tick = getattr(naluri, "subjective_tick_count", None)
        obj_tick = getattr(naluri, "tick_count", None)
        if tick is not None and obj_tick is not None:
            hasil["subjective_tick"] = max(0.0, float(tick))
            hasil["objective_tick"] = max(0, int(obj_tick))
    except (TypeError, ValueError):
        pass
    return hasil


def _attention_fatigue(naluri: Any) -> float:
    """Baca kelelahan atensi sadar; energi metabolik tidak digunakan."""
    ks = getattr(naluri, "kesadaran", None) if naluri is not None else None
    if ks is None:
        return 0.0
    try:
        state = ks.attention_state()
        if isinstance(state, Mapping):
            if not state.get("aktif", True):
                return 0.0
            return jepit_01(float(state.get("fatigue", 0.0)))
    except Exception:
        pass
    try:
        return jepit_01(float(getattr(ks, "_attention_fatigue", 0.0)))
    except (TypeError, ValueError):
        return 0.0


def _batas_retrieval(value: Any, nama: str, boleh_nol: bool = False) -> None:
    if value is not None and (isinstance(value, bool) or not isinstance(value, int)
                              or value < (0 if boleh_nol else 1)):
        raise ValueError(nama + " harus integer " + ("non-negatif" if boleh_nol else "positif"))


class JejakPrediksi:
    """Memori pengalaman + pattern matcher + predictor/action ranker.

    Args:
        naluri: instance Naluri opsional. Dipakai secara duck-typed melalui
            `persepsi()` / `impact_of()`, `experience()`, `choose_action()`,
            `observe_outcome()` dan atribut bobot/tick bila tersedia.
        capacity: batas episode yang disimpan; episode terlama dibuang saat penuh.
        weights: bobot memory/instinct/environment. Bobot lingkungan dibatasi
            maksimal 0.20 agar tidak dapat mendominasi model internal.
        half_life_ticks: peluruhan relevansi episode berdasarkan usia tick.
        min_similarity: ambang dasar pencocokan pola.
        sync_nurani: kirim pengalaman baru ke `naluri.experience()` bila ada.
    """

    def __init__(self,
                 naluri: Any = None,
                 capacity: int = 2048,
                 weights: Optional[Mapping[str, float]] = None,
                 half_life_ticks: float = 600.0,
                 min_similarity: float = 0.10,
                 sync_nurani: bool = True,
                 exploration_beta: float = 0.18,
                 counterfactual_margin: float = 0.15,
                 memory_retention_half_life: Optional[float] = None,
                 memory_death_multiples: float = 3.0,
                 enable_reconstructive_recall: bool = False,
                 recall_rewrite_rate: float = 0.16,
                 rng_seed: Optional[int] = None) -> None:
        self.naluri = naluri
        # RNG lokal: konfabulasi harus deterministik bila seed diberikan,
        # bukan menarik dari `random` global yang dipakai seluruh proses.
        self._rng = random.Random(rng_seed)
        self.capacity = max(1, int(capacity))
        self.half_life_ticks = max(0.0, float(half_life_ticks))
        self.memory_retention_half_life = max(
            0.0, float(self.half_life_ticks if memory_retention_half_life is None
                       else memory_retention_half_life))
        self.memory_death_multiples = max(1.0, float(memory_death_multiples))
        self.enable_reconstructive_recall = bool(enable_reconstructive_recall)
        self.recall_rewrite_rate = jepit_01(float(recall_rewrite_rate))
        self.min_similarity = jepit_01(float(min_similarity))
        self.sync_nurani = bool(sync_nurani)
        self.exploration_beta = jepit(float(exploration_beta), 0.0, 2.0)
        self.counterfactual_margin = jepit(float(counterfactual_margin), 0.0, 2.0)
        self.weights = self._normalise_weights(weights)
        self._episodes: List[Dict[str, Any]] = []
        # Memori mati tidak hilang menjadi ketiadaan: hanya signature dan
        # sebab kematian yang tersisa. Isi sengaja tidak masuk nekropolis.
        self._nekropolis: Dict[str, Dict[str, Any]] = {}
        self._recall_rewrite_log: List[Dict[str, Any]] = []
        self._last_retrieval_was_hole: bool = False
        self._counterfactual_log: List[Dict[str, Any]] = []
        self._pending_shadows: Dict[int, Dict[str, Any]] = {}
        self._next_decision_id = 1
        self._clock = 0
        self._next_id = 1
        # --- diri autobiografis & perjalanan waktu mental (konsep 3) ---
        self._chapters: List[Dict[str, Any]] = []
        self._chapter_open: Optional[Dict[str, Any]] = None
        self._future_sim_log: List[Dict[str, Any]] = []
        self._counterfactual_emotions: Dict[str, float] = {
            "penyesalan": 0.0, "kelegaan": 0.0, "kekecewaan": 0.0,
            "harapan": 0.0, "dread": 0.0,
        }
        self._confabulations: List[Dict[str, Any]] = []
        # --- KINERJA: indeks terbalik + MinHash + cache fitur ---
        # `_token_index` memetakan token -> himpunan episode_id sehingga
        # `_retrieve()` tidak lagi memindai seluruh episode (O(n) -> O(k)).
        self._token_index: Dict[str, Set[int]] = {}
        self._feature_cache: Dict[int, set] = {}
        self._minhash_sig: Dict[int, Tuple[int, ...]] = {}
        self._ep_by_id: Dict[int, Dict[str, Any]] = {}
        self._action_feature_cache: Dict[str, set] = {}
        self._minhash_perm: int = 32
        self._mh_seeds: Tuple[int, ...] = tuple(
            (i * 2654435761 + 40503) & 0xFFFFFFFF
            for i in range(self._minhash_perm))
        self._retrieve_mode: str = "exact"   # "exact" | "coarse" (LSH/MinHash)
        self._retrieve_calls: int = 0
        self._retrieve_candidates: int = 0
        self._consolidations: int = 0
        self._retrieve_time: float = 0.0
        self._last_retrieval_budget: Dict[str, Any] = {}
        # --- meta-pattern: membaca kebiasaan aktor (Player/NPC lain) ---
        self._actor_log: List[Dict[str, Any]] = []
        self._patterns: Dict[str, Dict[str, Any]] = {}
        self._pattern_window: int = 40
        self._pattern_min_count: int = 3
        self._pattern_confidence: float = 0.25
        # Auto-wire ke lapisan PRESENTASI Naluri (bila ada) agar memori
        # autobiografis JEJAK dapat dikisahkan sebagai perilaku/dialog.
        _nal = naluri
        _pres = getattr(_nal, "presentasi", None) if _nal is not None else None
        if _pres is not None:
            try:
                _pres.set_jejak(self)
            except Exception:
                pass

    @staticmethod
    def _normalise_weights(weights: Optional[Mapping[str, float]]) -> Dict[str, float]:
        raw = dict(DEFAULT_WEIGHTS)
        if weights:
            for key in raw:
                if key in weights:
                    try:
                        raw[key] = max(0.0, float(weights[key]))
                    except (TypeError, ValueError):
                        pass
        internal_raw = raw["memory"] + raw["instinct"]
        if internal_raw <= 1e-12:
            raw["memory"], raw["instinct"] = 0.75, 0.15
            internal_raw = 0.90
        # Model internal minimal 80%; environment never exceeds 20%.
        environment_share = min(0.20, raw["environment"] /
                                max(1e-12, internal_raw + raw["environment"]))
        internal_share = 1.0 - environment_share
        memory_share = internal_share * raw["memory"] / internal_raw
        instinct_share = internal_share * raw["instinct"] / internal_raw
        return {"memory": memory_share, "instinct": instinct_share,
                "environment": environment_share}

    @property
    def size(self) -> int:
        return len(self._episodes)

    @property
    def experiences(self) -> List[Dict[str, Any]]:
        """Salinan JSON-safe episode; menghindari mutasi langsung ke memori."""
        return [self._episode_copy(ep) for ep in self._episodes]

    @staticmethod
    def _memory_signature(stimulus: Any, context: Any = None) -> str:
        """Signature cue tanpa isi untuk mengenali bekas slot lintas-konteks.

        Context sengaja tidak dimasukkan: setelah isi mati, variasi suasana saat
        bertanya tidak boleh mengubah ``pernah tahu`` menjadi ``tak pernah tahu``.
        """
        fitur = sorted(_features(str(stimulus or "")))
        bahan = "|".join(fitur)
        if not bahan:
            return ""
        return "{:08x}".format(zlib.crc32(bahan.encode("utf-8")) & 0xFFFFFFFF)

    @staticmethod
    def _episode_copy(ep: Mapping[str, Any]) -> Dict[str, Any]:
        return {
            "id": int(ep.get("id", 0)),
            "signature": str(ep.get("signature", "")),
            "last_access_tick": int(ep.get("last_access_tick", ep.get("tick", 0))),
            "recall_revision": int(ep.get("recall_revision", 0)),
            "stimulus": str(ep.get("stimulus", "")),
            "action": str(ep.get("action", "")),
            "context": str(ep.get("context", "")),
            "impact": float(ep.get("impact", 0.0)),
            "drive_deltas": {d: float((ep.get("drive_deltas") or {}).get(d, 0.0))
                             for d in DRIVES},
            "hazard": float(ep.get("hazard", 0.0)),
            "label": str(ep.get("label", "")),
            "tick": int(ep.get("tick", 0)),
            "importance": float(ep.get("importance", 1.0)),
            "count": int(ep.get("count", 1)),
            "kind": str(ep.get("kind", "real")),
            "objective_duration": float(ep.get("objective_duration", 1.0)),
            "subjective_duration": float(ep.get("subjective_duration", 1.0)),
            "subjective_time_scale": float(ep.get("subjective_time_scale", 1.0)),
            "subjective_clock_rate": float(ep.get("subjective_clock_rate", 1.0)),
            "subjective_tick": (None if ep.get("subjective_tick") is None
                                else float(ep.get("subjective_tick"))),
            "subjective_objective_tick": (None if ep.get("subjective_objective_tick") is None
                                          else int(ep.get("subjective_objective_tick"))),
            "subjective_time_rasa": str(ep.get("subjective_time_rasa", "netral")),
        }

    def _current_tick(self, tick: Optional[int] = None) -> int:
        if tick is not None:
            try:
                value = max(0, int(tick))
                self._clock = max(self._clock, value)
                return value
            except (TypeError, ValueError):
                pass
        if self.naluri is not None:
            try:
                value = max(0, int(getattr(self.naluri, "tick_count")))
                self._clock = max(self._clock, value)
                return value
            except (AttributeError, TypeError, ValueError):
                pass
        return self._clock

    def _build_episode(self,
                       stimulus: str,
                       action: str,
                       context: str,
                       outcome: Any,
                       parsed: Mapping[str, Any],
                       tick: int,
                       importance: float,
                       kind: str,
                       duration_ticks: Optional[float]) -> Dict[str, Any]:
        """Bangun satu episode internal; tidak mengubah indeks atau state memori."""
        if duration_ticks is None:
            duration_ticks = _read(outcome, "duration_ticks",
                                   _read(outcome, "duration", 1.0))
        try:
            objective_duration = max(0.0, float(duration_ticks))
        except (TypeError, ValueError, OverflowError):
            objective_duration = 1.0

        time_profile = _subjective_time_snapshot(self.naluri)
        time_scale = float(time_profile.get("episode_scale", 1.0))
        return {
            "id": self._next_id,
            "stimulus": stimulus[:300],
            "action": action[:160],
            "context": context[:300],
            "impact": parsed["impact"],
            "drive_deltas": dict(parsed["drive_deltas"]),
            "hazard": parsed["hazard"],
            "label": parsed["label"],
            "tick": tick,
            "last_access_tick": tick,
            "signature": self._memory_signature(stimulus, context),
            "recall_revision": 0,
            "importance": jepit(float(importance), 0.1, 4.0),
            "count": 1,
            "kind": str(kind),
            "objective_duration": objective_duration,
            "subjective_duration": objective_duration * time_scale,
            "subjective_time_scale": time_scale,
            "subjective_clock_rate": float(time_profile.get("clock_rate", 1.0)),
            "subjective_tick": time_profile.get("subjective_tick"),
            "subjective_objective_tick": time_profile.get("objective_tick"),
            "subjective_time_rasa": str(time_profile.get("rasa", "netral"))[:32],
        }

    def record_experience(self,
                          stimulus: str,
                          action: str,
                          outcome: Any,
                          context: Any = None,
                          tick: Optional[int] = None,
                          importance: float = 1.0,
                          sync_nurani: Optional[bool] = None,
                          kind: str = "real",
                          duration_ticks: Optional[float] = None,
                          duration: Optional[float] = None) -> int:
        """Simpan pengalaman nyata untuk prediksi berikutnya.

        `outcome` dapat berupa angka [-1,1] atau dict seperti:
            {"impact": -0.9,
             "drive_deltas": {"keamanan": -0.8, "energi": -0.2},
             "label": "kulit terbakar"}

        Panggil setelah hasil aksi benar-benar diketahui. Nilai outcome dan
        drive dibatasi ke [-1,1]; episode lama tetap tersimpan sampai kapasitas
        penuh atau `forget()` dipanggil. `duration_ticks` adalah durasi objektif
        momen; keadaan waktu-subjektif mengubah durasi encoding dan half-life,
        tanpa mengubah importance.
        """
        stimulus = str(stimulus or "").strip()
        action = str(action or "").strip()
        context_str = _context_text(context).strip()
        if not stimulus:
            raise ValueError("stimulus tidak boleh kosong")
        parsed = _normalise_outcome(outcome)
        current = self._current_tick(tick)
        if tick is None and self.naluri is None:
            self._clock += 1
            current = self._clock
        if duration_ticks is None:
            duration_ticks = duration
        # Setiap operasi temporal menyapu episode yang sudah melewati usia.
        self._matikan_memori_tua(current)
        episode = self._build_episode(
            stimulus=stimulus,
            action=action,
            context=context_str,
            outcome=outcome,
            parsed=parsed,
            tick=current,
            importance=importance,
            kind=kind,
            duration_ticks=duration_ticks,
        )
        self._next_id += 1
        self._episodes.append(episode)
        # KINERJA: indeks terbalik + cache fitur + MinHash untuk episode baru.
        self._index_episode(episode)
        self._evict_overflow(current)

        sync = self.sync_nurani if sync_nurani is None else bool(sync_nurani)
        if sync:
            self._sync_naluri(stimulus, parsed)
        return int(episode["id"])

    # Alias yang lebih ringkas untuk pemanggil yang sudah terbiasa dengan Naluri.experience().
    experience = record_experience

    def _kuburkan(self, episode: Mapping[str, Any], alasan: str, tick: int) -> None:
        """Sisakan topologi kematian tanpa menyimpan kembali isi episode."""
        sig = str(episode.get("signature") or self._memory_signature(
            episode.get("stimulus", ""), episode.get("context", "")))
        if not sig:
            return
        lama = self._nekropolis.get(sig)
        jumlah = int((lama or {}).get("jumlah", 0)) + 1
        self._nekropolis[sig] = {
            "signature": sig,
            "alasan_kematian": str(alasan)[:80],
            "tick_kematian": int(tick),
            "jumlah": jumlah,
        }

    def _matikan_memori_tua(self, now: int) -> int:
        """Matikan episode yang tak pernah disentuh selama beberapa half-life."""
        half = float(self.memory_retention_half_life)
        if half <= 0.0:
            return 0
        batas = half * self.memory_death_multiples
        mati = [ep for ep in self._episodes
                if max(0, int(now) - int(ep.get(
                    "last_access_tick", ep.get("tick", now)))) > batas]
        if not mati:
            return 0
        ids = {int(ep.get("id", 0)) for ep in mati}
        self._episodes = [ep for ep in self._episodes
                          if int(ep.get("id", 0)) not in ids]
        for ep in mati:
            self._kuburkan(ep, "tidak_diakses_melampaui_retensi", now)
            self._deindex_episode(ep)
        return len(mati)

    def nekropolis_state(self) -> Dict[str, Any]:
        return {"jumlah_signature": len(self._nekropolis),
                "kematian": [dict(x) for x in self._nekropolis.values()],
                "retrieval_terakhir_lubang": self._last_retrieval_was_hole}

    def enable_recall_rewrite(self, aktif: bool = True,
                              rate: Optional[float] = None) -> bool:
        """Gate eksplisit untuk reconsolidation isi (mati secara default)."""
        self.enable_reconstructive_recall = bool(aktif)
        if rate is not None:
            self.recall_rewrite_rate = jepit_01(float(rate))
        return self.enable_reconstructive_recall

    def forget(self, max_age: Optional[int] = None, tick: Optional[int] = None) -> int:
        """Lupakan episode lebih lama dari `max_age`; bekasnya masuk nekropolis."""
        if max_age is None:
            return 0
        now = self._current_tick(tick)
        age_limit = max(0, int(max_age))
        keep: List[Dict[str, Any]] = []
        removed: List[Dict[str, Any]] = []
        for ep in self._episodes:
            if max(0, now - int(ep.get("tick", now))) <= age_limit:
                keep.append(ep)
            else:
                removed.append(ep)
        self._episodes = keep
        for ep in removed:
            self._kuburkan(ep, "dilupakan_eksplisit", now)
            self._deindex_episode(ep)
        return len(removed)

    def _recency(self, episode: Mapping[str, Any], now: int) -> float:
        age = max(0, now - int(episode.get("tick", now)))
        if self.half_life_ticks <= 0.0:
            return 1.0
        return 0.5 ** (age / self.half_life_ticks)

    def _retention_score(self, episode: Mapping[str, Any], now: int) -> float:
        """Eviksi menjaga episode penting/berdampak; usia tetap meluruhkan."""
        age = max(0, int(now) - int(episode.get("tick", now)))
        half = max(1.0, self.half_life_ticks * 2.0)
        drive_strength = max((abs(float(v)) for v in
                              (episode.get("drive_deltas") or {}).values()), default=0.0)
        salience = max(float(episode.get("importance", 0.1)),
                       abs(float(episode.get("impact", 0.0))), drive_strength)
        frequency = min(0.20, 0.04 * math.log1p(max(1, int(episode.get("count", 1)))))
        synthetic_penalty = 0.35 if episode.get("kind") == "counterfactual" else 1.0
        return synthetic_penalty * (0.02 + salience + frequency) * (0.5 ** (age / half))

    def _evict_overflow(self, now: int) -> None:
        while len(self._episodes) > self.capacity:
            victim = min(range(len(self._episodes)),
                         key=lambda i: self._retention_score(self._episodes[i], now))
            ep = self._episodes.pop(victim)
            self._kuburkan(ep, "eviksi_kapasitas", now)
            self._deindex_episode(ep)

    # ==================== KINERJA: INDEKS & MINHASH ====================
    def _minhash(self, features: Iterable[str]) -> Tuple[int, ...]:
        """Signature MinHash 32-bit untuk estimasi Jaccard cepat (O(perm))."""
        prime = 4294967311
        hasil = [prime] * len(self._mh_seeds)
        for token in features:
            h = zlib.crc32(str(token).encode("utf-8")) & 0xFFFFFFFF
            for i, seed in enumerate(self._mh_seeds):
                a = (seed | 1)
                b = (seed * 2654435761) & 0xFFFFFFFF
                v = (a * h + b) % prime
                if v < hasil[i]:
                    hasil[i] = v
        return tuple(hasil)

    @staticmethod
    def _minhash_sim(left: Sequence[int], right: Sequence[int]) -> float:
        """Estimasi Jaccard dari kecocokan signature MinHash."""
        if not left or not right or len(left) != len(right):
            return 0.0
        cocok = sum(1 for a, b in zip(left, right) if a == b)
        return cocok / len(left)

    def _index_episode(self, episode: Mapping[str, Any]) -> None:
        """Masukkan satu episode ke indeks terbalik + cache fitur + MinHash."""
        eid = int(episode.get("id", 0))
        if eid <= 0:
            return
        feats = _features(str(episode.get("stimulus", "")) + " "
                          + str(episode.get("context", "")))
        self._feature_cache[eid] = feats
        self._minhash_sig[eid] = self._minhash(feats)
        self._ep_by_id[eid] = dict(episode) if not isinstance(episode, dict) else episode
        for tok in feats:
            self._token_index.setdefault(tok, set()).add(eid)

    def _deindex_episode(self, episode: Mapping[str, Any]) -> None:
        """Keluarkan episode dari indeks/cache (saat eviksi/lupa/konsolidasi)."""
        eid = int(episode.get("id", 0))
        feats = self._feature_cache.pop(eid, None)
        if feats is None:
            feats = _features(str(episode.get("stimulus", "")) + " "
                              + str(episode.get("context", "")))
        for tok in feats:
            s = self._token_index.get(tok)
            if s is not None:
                s.discard(eid)
                if not s:
                    self._token_index.pop(tok, None)
        self._minhash_sig.pop(eid, None)
        self._ep_by_id.pop(eid, None)

    def _rebuild_index(self) -> None:
        """Bangun ulang indeks dari `_episodes` (dipakai setelah load/konsolidasi)."""
        self._token_index = {}
        self._feature_cache = {}
        self._minhash_sig = {}
        self._ep_by_id = {}
        for ep in self._episodes:
            self._index_episode(ep)

    def _candidates(self, query: set) -> List[Dict[str, Any]]:
        """Kandidat episode dari irisan token (bukan seluruh korpus)."""
        if not self._token_index:
            return list(self._episodes)
        ids: Set[int] = set()
        for tok in query:
            ids.update(self._token_index.get(tok, ()))
        if not ids:
            return []
        return [self._ep_by_id[i] for i in ids if i in self._ep_by_id]

    def set_retrieve_mode(self, mode: str) -> str:
        """\"exact\" (presisi) atau \"coarse\" (MinHash, cocok NPC background)."""
        key = str(mode).lower().strip()
        self._retrieve_mode = key if key in ("exact", "coarse") else "exact"
        return self._retrieve_mode

    def performance_report(self) -> Dict[str, Any]:
        """Statistik ringan untuk profiler: rasio kandidat vs korpus."""
        calls = max(1, self._retrieve_calls)
        return {"episodes": len(self._episodes),
                "index_tokens": len(self._token_index),
                "retrieve_calls": self._retrieve_calls,
                "avg_candidates": round(self._retrieve_candidates / calls, 3),
                "mode": self._retrieve_mode,
                "last_budget": dict(self._last_retrieval_budget),
                "consolidations": self._consolidations,
                "nekropolis": len(self._nekropolis),
                "recall_rewrites": len(self._recall_rewrite_log),
                "avg_retrieve_ms": round(self._retrieve_time / calls * 1000, 4),
                "total_retrieve_ms": round(self._retrieve_time * 1000, 3)}

    # ==================== KONSOLIDASI MEMORI (tidur) ====================
    def consolidate_memory(self, importance_threshold: float = 0.2,
                           min_episodes: int = 6,
                           tick: Optional[int] = None) -> Dict[str, Any]:
        """Gabungkan episode remeh menjadi ringkasan (memori semantik).

        Dipanggil saat tidur (mis. dari Naluri.post_sleep). Episode penting
        (importance >= ambang) tetap utuh; episode remeh dikelompokkan per
        aksi/keluarga dan digabung menjadi satu episode `kind="summary"`.
        """
        if len(self._episodes) < max(2, int(min_episodes)):
            return {"consolidated": 0, "kept": len(self._episodes),
                    "summaries": 0, "before": len(self._episodes)}
        before = len(self._episodes)
        keep: List[Dict[str, Any]] = []
        trivial: Dict[str, List[Dict[str, Any]]] = {}
        for ep in self._episodes:
            imp = float(ep.get("importance", 1.0))
            kind = str(ep.get("kind", "real"))
            if imp >= float(importance_threshold) or kind in ("counterfactual", "summary"):
                keep.append(ep)
            else:
                key = _action_family(str(ep.get("action", ""))) or str(
                    ep.get("action", "") or kind)
                trivial.setdefault(key, []).append(ep)
        summaries: List[Dict[str, Any]] = []
        now = self._current_tick(tick)
        for key, grup in trivial.items():
            if not grup:
                continue
            total = sum(max(1, int(e.get("count", 1))) for e in grup)
            dd = {d: 0.0 for d in DRIVES}
            for e in grup:
                w = max(1, int(e.get("count", 1)))
                for d in DRIVES:
                    dd[d] += float((e.get("drive_deltas") or {}).get(d, 0.0)) * w
            dd = {d: jepit_drive(dd[d] / total) for d in DRIVES}
            impact = sum(float(e.get("impact", 0.0)) for e in grup) / len(grup)
            hazard = sum(float(e.get("hazard", 0.0)) for e in grup) / len(grup)
            rep = max(grup, key=lambda e: int(e.get("tick", 0)))
            summaries.append({
                "id": self._next_id, "stimulus": str(rep.get("stimulus", ""))[:300],
                "action": str(rep.get("action", ""))[:160],
                "context": "", "impact": jepit_drive(impact),
                "drive_deltas": dd, "hazard": jepit_01(hazard),
                "label": f"ringkasan {total} pengalaman", "tick": now,
                "last_access_tick": now,
                "signature": self._memory_signature(rep.get("stimulus", ""), ""),
                "recall_revision": 0,
                "importance": min(float(importance_threshold), 0.18),
                "count": total, "kind": "summary",
            })
            self._next_id += 1
        self._episodes = keep + summaries
        self._evict_overflow(now)
        self._rebuild_index()
        self._consolidations += 1
        return {"consolidated": before - len(self._episodes),
                "kept": len(keep), "summaries": len(summaries),
                "before": before, "after": len(self._episodes)}

    def _rewrite_episode_at_recall(self, ep: Dict[str, Any], now: int) -> None:
        """Reconsolidation isi: keadaan recall menulis ulang episode asli.

        Tidak memakai RNG. Gate mati secara default agar prediksi lama tetap
        reproducible; saat aktif, determinisme masih mengikuti state pemanggil.
        """
        ep["last_access_tick"] = int(now)
        if not self.enable_reconstructive_recall or self.naluri is None:
            return
        rate = self.recall_rewrite_rate
        if rate <= 0.0:
            return
        emosi = getattr(self.naluri, "emosi", {}) or {}
        try:
            mood = self.naluri.mood()
            arousal = jepit_01(float(getattr(mood, "arousal", 0.0)))
            valence = jepit_drive(float(getattr(mood, "valence", 0.0)))
        except Exception:
            arousal, valence = 0.0, 0.0
        takut = max(0.0, float(emosi.get("takut", 0.0) or 0.0))
        marah = max(0.0, float(emosi.get("marah", 0.0) or 0.0))
        sedih = max(0.0, float(emosi.get("sedih", 0.0) or 0.0))
        senang = max(0.0, float(emosi.get("senang", 0.0) or 0.0))
        ancaman = max(takut, 0.75 * arousal, 0.65 * marah)
        tenang = max(0.0, 1.0 - arousal) * max(0.0, 0.5 + 0.5 * valence)

        hazard_lama = float(ep.get("hazard", 0.0))
        hazard_target = _clip(hazard_lama + 0.55 * ancaman - 0.30 * tenang,
                              0.0, 1.0)
        ep["hazard"] = _clip(hazard_lama + rate * (hazard_target - hazard_lama),
                             0.0, 1.0)
        dd = dict(ep.get("drive_deltas") or {})
        shifts = {
            "keamanan": -0.45 * ancaman + 0.22 * tenang,
            "energi": -0.18 * sedih + 0.10 * senang,
            "afiliasi": -0.20 * (sedih + marah) + 0.16 * senang,
            "koherensi": -0.20 * arousal + 0.15 * tenang,
            "penguasaan": -0.16 * takut + 0.14 * marah,
            "keingintahuan": 0.12 * arousal - 0.08 * takut,
        }
        for d in DRIVES:
            lama = float(dd.get(d, 0.0))
            dd[d] = _clip(lama + rate * shifts[d])
        ep["drive_deltas"] = dd
        target_impact = sum(dd.values()) / max(1, len(dd))
        ep["impact"] = _clip(float(ep.get("impact", 0.0)) + rate *
                             (target_impact - float(ep.get("impact", 0.0))))
        label = re.sub(r"\s*\[recall:[^\]]+\]\s*$", "",
                       str(ep.get("label", ""))).strip()
        if ancaman > tenang + 0.15:
            warna = "lebih mengancam"
        elif tenang > ancaman + 0.15:
            warna = "lebih jauh dan lunak"
        else:
            warna = "bergeser"
        ep["label"] = (label + " [recall:{}]".format(warna)).strip()[:120]
        ep["recall_revision"] = int(ep.get("recall_revision", 0)) + 1
        self._recall_rewrite_log.append({
            "tick": int(now), "id": int(ep.get("id", 0)),
            "signature": str(ep.get("signature", "")), "warna": warna,
            "hazard_sebelum": round(hazard_lama, 4),
            "hazard_sesudah": round(float(ep["hazard"]), 4)})
        if len(self._recall_rewrite_log) > 128:
            self._recall_rewrite_log = self._recall_rewrite_log[-128:]

    def _retrieve(self,
                  stimulus: str,
                  context: Any,
                  now: int, *, max_candidates: Optional[int] = None,
                  max_age_ticks: Optional[int] = None) -> Optional[List[Dict[str, Any]]]:
        _batas_retrieval(max_candidates, "max_candidates")
        _batas_retrieval(max_age_ticks, "max_age_ticks", boleh_nol=True)
        self._last_retrieval_budget = {
            "max_candidates": max_candidates, "max_age_ticks": max_age_ticks,
            "indexed_candidates": 0, "age_pruned": 0, "budget_pruned": 0,
            "similarity_evaluations": 0, "truncated": False,
        }
        self._retrieve_calls += 1
        _t0 = time.perf_counter()
        self._last_retrieval_was_hole = False
        self._matikan_memori_tua(now)
        fatigue = _attention_fatigue(self.naluri)
        retrieval_clarity = max(0.25, 1.0 - 0.60 * fatigue)
        threshold = min(0.95, self.min_similarity + 0.14 * fatigue)
        query = _features(str(stimulus or "") + " " + _context_text(context))
        signature = self._memory_signature(stimulus, context)
        if not query:
            self._retrieve_time += time.perf_counter() - _t0
            return []
        # KINERJA: kandidat dari indeks terbalik (O(k)), bukan seluruh korpus.
        candidates = self._candidates(query)
        self._last_retrieval_budget["indexed_candidates"] = len(candidates)
        if (not any(str(ep.get("signature", "")) == signature
                    for ep in candidates)
                and signature in self._nekropolis):
            self._last_retrieval_was_hole = True
            self._retrieve_time += time.perf_counter() - _t0
            return None
        if max_age_ticks is not None:
            sebelum = len(candidates)
            candidates = [ep for ep in candidates
                          if max(0, now - int(ep.get("tick", now))) <= max_age_ticks]
            self._last_retrieval_budget["age_pruned"] = sebelum - len(candidates)
        if max_candidates is not None and len(candidates) > max_candidates:
            self._last_retrieval_budget["budget_pruned"] = len(candidates) - max_candidates
            candidates = heapq.nsmallest(
                max_candidates, candidates,
                key=lambda ep: (-int(ep.get("tick", 0)),
                                -float(ep.get("importance", 1.0)), -int(ep.get("id", 0))))
        self._last_retrieval_budget["truncated"] = bool(
            self._last_retrieval_budget["age_pruned"] or
            self._last_retrieval_budget["budget_pruned"])
        self._retrieve_candidates += len(candidates)
        coarse = (self._retrieve_mode == "coarse")
        qsig = self._minhash(query) if coarse else None
        hits: List[Dict[str, Any]] = []
        for ep in candidates:
            eid = int(ep.get("id", 0))
            scene = self._feature_cache.get(eid)
            if scene is None:
                scene = _features(ep.get("stimulus", "") + " " + ep.get("context", ""))
                self._feature_cache[eid] = scene
            # LSH/MinHash: lewati episode yang jelas tidak mirip (mode kasar).
            if coarse and qsig is not None:
                sig = self._minhash_sig.get(eid)
                if sig is not None and self._minhash_sim(qsig, sig) < self.min_similarity * 0.5:
                    continue
            self._last_retrieval_budget["similarity_evaluations"] += 1
            sim = _similarity(query, scene)
            if sim < threshold:
                continue
            recency = self._recency(ep, now)
            importance = float(ep.get("importance", 1.0))
            # Kelelahan menumpulkan pencocokan nuansa (similarity parsial) dan
            # menurunkan gain recall; importance episode tidak disentuh.
            weight = ((sim ** (2.0 + 1.5 * fatigue)) * recency * importance
                      * max(1, int(ep.get("count", 1))) * retrieval_clarity)
            if weight <= 1e-12:
                continue
            # Hanya episode yang benar-benar masuk scene_hits dianggap recall.
            self._rewrite_episode_at_recall(ep, now)
            hit = dict(ep)
            hit["similarity"] = sim
            hit["recency"] = recency
            hit["match_weight"] = weight
            hit["attention_fatigue"] = fatigue
            hit["retrieval_clarity"] = retrieval_clarity
            hit["subjective_age"] = _waktu_umur_subjektif(self, ep, now)
            hits.append(hit)
        hits.sort(key=lambda x: (x["match_weight"], x["similarity"], x["tick"]), reverse=True)
        self._retrieve_time += time.perf_counter() - _t0
        return hits

    def _retrieve_action(self,
                         scene_hits: Sequence[Mapping[str, Any]],
                         action: Optional[str]) -> List[Dict[str, Any]]:
        if not action:
            return []
        query_features = _features(action, action=True)
        query_family = _action_family(action)
        if not query_features:
            return []
        hits: List[Dict[str, Any]] = []
        for ep in scene_hits:
            memory_action = str(ep.get("action", ""))
            memory_features = self._action_feature_cache.get(memory_action)
            if memory_features is None:
                memory_features = _features(memory_action, action=True)
                self._action_feature_cache[memory_action] = memory_features
            if not memory_features:
                continue
            memory_family = _action_family(memory_action)
            # Paparan fisik dan menghindar adalah hasil kausal yang berbeda;
            # jangan salah pakai episode menyentuh api untuk mengklaim bahwa
            # aksi menjauh juga akan membakar agen.
            if {query_family, memory_family} == {"hindar", "paparan"}:
                continue
            action_sim = _similarity(query_features, memory_features)
            if query_family and query_family == memory_family:
                action_sim = max(action_sim, 0.85)
            if action_sim < 0.08:
                continue
            hit = dict(ep)
            hit["action_similarity"] = action_sim
            hit["match_weight"] = float(ep["match_weight"]) * (0.25 + 0.75 * action_sim)
            hits.append(hit)
        hits.sort(key=lambda x: (x["match_weight"], x.get("action_similarity", 0.0)),
                  reverse=True)
        return hits

    @staticmethod
    def _aggregate(hits: Sequence[Mapping[str, Any]]) -> Dict[str, Any]:
        if not hits:
            return {"impact": 0.0, "drive_deltas": {d: 0.0 for d in DRIVES},
                    "hazard": 0.0, "confidence": 0.0, "dispersion": 0.0,
                    "aleatoric_uncertainty": 0.0,
                    "epistemic_uncertainty": 1.0,
                    "n_matches": 0, "effective_samples": 0.0,
                    "best_similarity": 0.0, "label": "", "matches": []}
        mass = sum(float(h.get("match_weight", 0.0)) for h in hits)
        if mass <= 1e-12:
            return JejakPrediksi._aggregate([])
        mean_impact = sum(float(h.get("impact", 0.0)) * float(h["match_weight"])
                          for h in hits) / mass
        drive_deltas: Dict[str, float] = {}
        for d in DRIVES:
            drive_deltas[d] = sum(float((h.get("drive_deltas") or {}).get(d, 0.0))
                                  * float(h["match_weight"]) for h in hits) / mass
        hazard = sum(float(h.get("hazard", 0.0)) * float(h["match_weight"])
                     for h in hits) / mass
        variance = sum(float(h["match_weight"]) *
                       (float(h.get("impact", 0.0)) - mean_impact) ** 2 for h in hits) / mass
        dispersion = min(1.0, math.sqrt(max(0.0, variance)))
        # Aleatorik = variasi hasil di antara episode; epistemik = kurangnya
        # bukti (efektif-sampel sedikit), dua hal yang jangan dicampur.
        aleatoric = dispersion
        epistemic = math.exp(-max(0.0, mass))
        best_sim = max(float(h.get("similarity", 0.0)) for h in hits)
        support = 1.0 - epistemic
        coverage = min(1.0, best_sim / 0.55)
        consistency = max(0.20, 1.0 - 0.80 * dispersion)
        confidence = jepit((0.30 + 0.70 * support) * coverage * consistency, 0.0, 0.97)
        labels = [str(h.get("label", "")) for h in hits if h.get("label")]
        matches = []
        for h in hits[:5]:
            matches.append({
                "id": int(h.get("id", 0)),
                "stimulus": str(h.get("stimulus", "")),
                "action": str(h.get("action", "")),
                "label": str(h.get("label", "")),
                "similarity": round(float(h.get("similarity", 0.0)), 4),
                "action_similarity": round(float(h.get("action_similarity", 0.0)), 4),
                "tick": int(h.get("tick", 0)),
                "count": int(h.get("count", 1)),
            })
        return {
            "impact": _clip(mean_impact),
            "drive_deltas": {d: _clip(v) for d, v in drive_deltas.items()},
            "hazard": _clip(hazard, 0.0, 1.0),
            "confidence": confidence,
            "dispersion": dispersion,
            "aleatoric_uncertainty": aleatoric,
            "epistemic_uncertainty": epistemic,
            "n_matches": len(hits),
            "effective_samples": mass,
            "best_similarity": best_sim,
            "label": labels[0] if labels else "",
            "matches": matches,
        }

    def _instinct_prior(self, scene: str) -> Dict[str, Any]:
        deltas: Dict[str, float] = {d: 0.0 for d in DRIVES}
        active_perception = False
        naluri = self.naluri
        if naluri is None:
            return {"impact": 0.0, "drive_deltas": deltas, "confidence": 0.0,
                    "hazard": 0.0, "perception_active": False}
        result = None
        perception = getattr(naluri, "persepsi", None)
        if callable(perception):
            try:
                result = perception(scene)
                if isinstance(result, Mapping):
                    active_perception = bool(result.get("aktif", False))
                    result = result.get("delta", result)
            except Exception:
                result = None
        if not isinstance(result, Mapping):
            impact_fn = getattr(naluri, "impact_of", None)
            if callable(impact_fn):
                try:
                    result = impact_fn(scene)
                except Exception:
                    result = None
        if isinstance(result, Mapping):
            for d in DRIVES:
                deltas[d] = _clip(result.get(d, 0.0))

        # Skalar internal dari delta drive aktif, dengan bobot kepribadian Naluri.
        weights = getattr(naluri, "weights", {}) or {}
        active = [d for d in DRIVES if abs(deltas[d]) > 1e-9]
        if active:
            den = sum(abs(float(weights.get(d, DEFAULT_DRIVE_WEIGHTS[d]))) for d in active)
            impact = (sum(deltas[d] * float(weights.get(d, DEFAULT_DRIVE_WEIGHTS[d]))
                          for d in active) / max(1e-9, den))
        else:
            impact = 0.0
        strength = max([abs(impact)] + [abs(v) for v in deltas.values()])
        confidence = 0.0 if strength < 1e-8 else min(0.72, 0.34 + 0.24 * strength
                                                     + (0.10 if active_perception else 0.0))
        hazard = max(0.0, -impact, -deltas.get("keamanan", 0.0))
        return {"impact": _clip(impact), "drive_deltas": deltas,
                "confidence": confidence, "hazard": _clip(hazard, 0.0, 1.0),
                "perception_active": active_perception}

    @staticmethod
    def _environment_prior(environment: Any) -> Dict[str, Any]:
        if environment is None:
            return {"impact": 0.0, "drive_deltas": {d: 0.0 for d in DRIVES},
                    "hazard": 0.0, "confidence": 0.0,
                    "epistemic_uncertainty": 1.0,
                    "aleatoric_uncertainty": 0.0, "available": False}
        if isinstance(environment, (int, float)) and not isinstance(environment, bool):
            parsed = _normalise_outcome(environment)
            confidence = 0.70
        else:
            parsed = _normalise_outcome(environment)
            confidence = _clip(_read(environment, "confidence", 0.70), 0.0, 1.0)
        has_signal = (abs(parsed["impact"]) > 1e-9 or parsed["hazard"] > 1e-9
                      or any(abs(v) > 1e-9 for v in parsed["drive_deltas"].values()))
        return {**parsed, "confidence": confidence if has_signal else 0.0,
                "epistemic_uncertainty": _clip(_read(environment, "epistemic_uncertainty",
                                                      1.0 - confidence), 0.0, 1.0),
                "aleatoric_uncertainty": _clip(_read(environment, "aleatoric_uncertainty", 0.0),
                                                0.0, 1.0),
                "available": has_signal}

    def _blend(self,
               memory: Mapping[str, Any],
               instinct: Mapping[str, Any],
               environment: Mapping[str, Any]) -> Dict[str, Any]:
        wm = self.weights["memory"]
        wi = self.weights["instinct"]
        we = self.weights["environment"]
        internal_nominal = wm + wi
        cm = _clip(memory.get("confidence", 0.0), 0.0, 1.0)
        ci = _clip(instinct.get("confidence", 0.0), 0.0, 1.0)
        ce = _clip(environment.get("confidence", 0.0), 0.0, 1.0)
        denom = wm * cm + wi * ci
        if denom > 1e-12:
            internal_impact = (wm * cm * float(memory.get("impact", 0.0))
                               + wi * ci * float(instinct.get("impact", 0.0))) / denom
            internal_deltas = {
                d: (wm * cm * float((memory.get("drive_deltas") or {}).get(d, 0.0))
                    + wi * ci * float((instinct.get("drive_deltas") or {}).get(d, 0.0))) / denom
                for d in DRIVES
            }
            internal_hazard = (wm * cm * float(memory.get("hazard", 0.0))
                               + wi * ci * float(instinct.get("hazard", 0.0))) / denom
            internal_confidence = min(1.0, denom / max(1e-12, internal_nominal))
            if cm > 0.0 and ci > 0.0:
                disagreement = abs(float(memory.get("impact", 0.0))
                                   - float(instinct.get("impact", 0.0)))
                internal_confidence *= max(0.35, 1.0 - 0.35 * disagreement)
        else:
            internal_impact = 0.0
            internal_deltas = {d: 0.0 for d in DRIVES}
            internal_hazard = 0.0
            internal_confidence = 0.0

        ext_impact = float(environment.get("impact", 0.0))
        ext_deltas = environment.get("drive_deltas") or {d: 0.0 for d in DRIVES}
        ext_hazard = float(environment.get("hazard", 0.0))
        final_impact = _clip((1.0 - we) * internal_impact + we * ext_impact)
        final_deltas = {d: _clip((1.0 - we) * internal_deltas[d]
                                 + we * float(ext_deltas.get(d, 0.0))) for d in DRIVES}
        # Bahaya merupakan prediksi dampak nyata, bukan hanya kata "bahaya".
        final_hazard = _clip(max(0.0, (1.0 - we) * internal_hazard + we * ext_hazard,
                                 -final_impact, -final_deltas.get("keamanan", 0.0)),
                             0.0, 1.0)
        confidence = _clip((1.0 - we) * internal_confidence + we * ce, 0.0, 1.0)
        memory_epistemic = _clip(memory.get("epistemic_uncertainty", 1.0), 0.0, 1.0)
        memory_aleatoric = _clip(memory.get("aleatoric_uncertainty",
                                             memory.get("dispersion", 0.0)), 0.0, 1.0)
        epistemic = _clip(wm * memory_epistemic
                          + wi * (1.0 - ci)
                          + we * float(environment.get("epistemic_uncertainty", 1.0)),
                          0.0, 1.0)
        aleatoric = _clip(wm * memory_aleatoric
                          + we * float(environment.get("aleatoric_uncertainty", 0.0)),
                          0.0, 1.0)
        return {
            "impact": final_impact,
            "drive_deltas": final_deltas,
            "hazard": final_hazard,
            "confidence": confidence,
            "uncertainty": 1.0 - confidence,
            "epistemic_uncertainty": epistemic,
            "aleatoric_uncertainty": aleatoric,
            "internal": {
                "impact": _clip(internal_impact),
                "drive_deltas": {d: _clip(v) for d, v in internal_deltas.items()},
                "hazard": _clip(internal_hazard, 0.0, 1.0),
                "confidence": _clip(internal_confidence, 0.0, 1.0),
            },
            "environment": {
                "impact": _clip(ext_impact),
                "drive_deltas": {d: _clip(ext_deltas.get(d, 0.0)) for d in DRIVES},
                "hazard": _clip(ext_hazard, 0.0, 1.0),
                "confidence": ce,
            },
            "weights": {"internal": round(1.0 - we, 4),
                        "environment": round(we, 4),
                        "memory_nominal": round(wm, 4),
                        "instinct_nominal": round(wi, 4)},
        }

    @staticmethod
    def _recommendation(situation: Mapping[str, Any]) -> str:
        hazard = float(situation.get("hazard", 0.0))
        confidence = float(situation.get("confidence", 0.0))
        # Satu pengalaman yang sangat buruk boleh memicu kehati-hatian meski
        # keyakinannya belum tinggi: rekomendasi aman lebih baik daripada
        # menunggu kepastian sempurna. Confidence tetap ditampilkan terpisah.
        if hazard >= 0.42 and confidence >= 0.10:
            return "Pola pengalaman memprediksi bahaya; hindari atau menjauh."
        if confidence < 0.18:
            return "Belum cukup pengalaman yang cocok; jaga jarak dan cari bukti dengan aman."
        if hazard >= 0.18:
            return "Waspada; amati dari jarak aman sebelum bertindak."
        if float(situation.get("impact", 0.0)) > 0.30 and confidence >= 0.35:
            return "Pola pengalaman tampak menguntungkan; lakukan bertahap dan pantau hasilnya."
        return "Belum ada sinyal kuat; lanjutkan dengan hati-hati dan tetap verifikasi."

    def predict(self,
                stimulus: str,
                action: Optional[str] = None,
                context: Any = None,
                environment: Any = None,
                tick: Optional[int] = None,
                register_pending: bool = False, *,
                max_candidates: Optional[int] = None,
                max_age_ticks: Optional[int] = None) -> Dict[str, Any]:
        """Prediksi dampak masa depan dari situasi/aksi.

        max_candidates membatasi similarity setelah indeks token (None = legacy).
        max_age_ticks menyaring usia objektif sebelum similarity. Pemotongan
        dilaporkan pada retrieval_budget; hasil berbatas bersifat aproksimasi.

        `environment` adalah bukti numerik langsung, misalnya:
            {"impact": -0.4, "drive_deltas": {"keamanan": -0.5},
             "confidence": 0.8}
        Bobotnya maksimal 20% (10% secara default). Teks stimulus tetap dipakai
        sebagai cue pencarian memori dan pemrosesan perseptual Naluri; ia tidak
        dianggap sebagai kebenaran outcome.

        Jika `action` diberikan tetapi belum ada episode untuk aksi sejenis,
        `forecast` tetap memuat prediksi tingkat-situasi, namun `scope` akan
        bernilai "situation" dan `action_forecast` bernilai None. Ini mencegah
        pengalaman buruk saat menyentuh api salah diterapkan sebagai akibat
        dari aksi menjauh dari api.
        """
        stimulus = str(stimulus or "").strip()
        if not stimulus:
            raise ValueError("stimulus tidak boleh kosong")
        context_str = _context_text(context)
        now = self._current_tick(tick)
        hasil_retrieve = self._retrieve(stimulus, context_str, now,
                                       max_candidates=max_candidates, max_age_ticks=max_age_ticks)
        budget = dict(self._last_retrieval_budget)
        memory_hole = hasil_retrieve is None
        scene_hits = [] if memory_hole else hasil_retrieve
        scene_memory = self._aggregate(scene_hits)
        action_hits = self._retrieve_action(scene_hits, action)
        action_memory = self._aggregate(action_hits) if action_hits else None
        scene_text = " ".join(x for x in (stimulus, context_str) if x).strip()
        instinct = self._instinct_prior(scene_text)
        external = self._environment_prior(environment)
        situation = self._blend(scene_memory, instinct, external)
        action_forecast = (self._blend(action_memory, instinct, external)
                           if action_memory is not None else None)
        if action is not None and action_forecast is not None:
            forecast = action_forecast
            scope = "action"
        else:
            forecast = situation
            scope = "situation"

        recommendation = self._recommendation(situation)
        if scope == "action" and forecast["hazard"] >= 0.42:
            recommendation = "Aksi serupa pernah berujung buruk; jangan ulangi tanpa mitigasi."
        if scene_memory["n_matches"]:
            explanation = (f"Pola cocok dengan {scene_memory['n_matches']} episode; "
                           f"kemiripan terbaik {scene_memory['best_similarity']:.2f}. "
                           f"Prediksi internal berbobot {1.0 - self.weights['environment']:.0%}; "
                           f"bukti lingkungan berbobot {self.weights['environment']:.0%}.")
        elif memory_hole:
            explanation = ("Ada bekas memori untuk situasi ini, tetapi isinya telah mati; "
                           "aku tahu pernah mengetahui sesuatu tanpa dapat mengambilnya.")
        else:
            explanation = ("Belum ada episode yang cocok; prediksi terutama bertumpu "
                           "pada prior Naluri/NURANI yang tersedia dan tetap tidak pasti.")
        if action is not None and action_forecast is None:
            explanation += (f" Outcome aksi '{action}' belum memiliki pola pengalaman "
                            "yang cocok; angka utama adalah perkiraan bahaya situasi, "
                            "bukan klaim bahwa aksi itu sendiri pernah diuji.")

        if budget["truncated"]:
            explanation += " Retrieval dibatasi; sebagian episode tidak dievaluasi."

        if register_pending and self.naluri is not None:
            note = getattr(self.naluri, "note_prediction", None)
            if callable(note):
                try:
                    note()
                except Exception:
                    pass

        return {
            "stimulus": stimulus,
            "action": action,
            "context": context_str,
            "retrieval_budget": budget,
            "scope": scope,
            "forecast": {
                "impact": round(float(forecast["impact"]), 4),
                "drive_deltas": {d: round(float(forecast["drive_deltas"][d]), 4)
                                 for d in DRIVES},
                "hazard": round(float(forecast["hazard"]), 4),
                "confidence": round(float(forecast["confidence"]), 4),
                "uncertainty": round(float(forecast["uncertainty"]), 4),
                "epistemic_uncertainty": round(float(forecast["epistemic_uncertainty"]), 4),
                "aleatoric_uncertainty": round(float(forecast["aleatoric_uncertainty"]), 4),
            },
            "situation_forecast": {
                "impact": round(float(situation["impact"]), 4),
                "drive_deltas": {d: round(float(situation["drive_deltas"][d]), 4)
                                 for d in DRIVES},
                "hazard": round(float(situation["hazard"]), 4),
                "confidence": round(float(situation["confidence"]), 4),
                "uncertainty": round(float(situation["uncertainty"]), 4),
                "epistemic_uncertainty": round(float(situation["epistemic_uncertainty"]), 4),
                "aleatoric_uncertainty": round(float(situation["aleatoric_uncertainty"]), 4),
            },
            "action_forecast": ({
                "impact": round(float(action_forecast["impact"]), 4),
                "drive_deltas": {d: round(float(action_forecast["drive_deltas"][d]), 4)
                                 for d in DRIVES},
                "hazard": round(float(action_forecast["hazard"]), 4),
                "confidence": round(float(action_forecast["confidence"]), 4),
                "uncertainty": round(float(action_forecast["uncertainty"]), 4),
                "epistemic_uncertainty": round(float(action_forecast["epistemic_uncertainty"]), 4),
                "aleatoric_uncertainty": round(float(action_forecast["aleatoric_uncertainty"]), 4),
            } if action_forecast is not None else None),
            "recommendation": recommendation,
            "memory": {
                "n_matches": scene_memory["n_matches"],
                "hole": bool(memory_hole),
                "retrieval_status": ("mati_diketahui" if memory_hole
                                     else "ditemukan" if scene_memory["n_matches"]
                                     else "tidak_pernah_diketahui"),
                "action_matches": len(action_hits),
                "effective_samples": round(float(scene_memory["effective_samples"]), 4),
                "best_similarity": round(float(scene_memory["best_similarity"]), 4),
                "dispersion": round(float(scene_memory["dispersion"]), 4),
                "label": scene_memory["label"],
                "matches": scene_memory["matches"],
                "action_matches_preview": action_memory["matches"] if action_memory else [],
            },
            "sources": {
                "memory": {
                    "impact": round(float((action_memory or scene_memory)["impact"]), 4),
                    "confidence": round(float((action_memory or scene_memory)["confidence"]), 4),
                    "epistemic_uncertainty": round(float((action_memory or scene_memory)["epistemic_uncertainty"]), 4),
                    "aleatoric_uncertainty": round(float((action_memory or scene_memory)["aleatoric_uncertainty"]), 4),
                },
                "naluri_nurani": {
                    "impact": round(float(instinct["impact"]), 4),
                    "drive_deltas": {d: round(float(instinct["drive_deltas"][d]), 4)
                                     for d in DRIVES},
                    "confidence": round(float(instinct["confidence"]), 4),
                    "perception_active": bool(instinct["perception_active"]),
                },
                "environment": {
                    "impact": round(float(external["impact"]), 4),
                    "hazard": round(float(external["hazard"]), 4),
                    "confidence": round(float(external["confidence"]), 4),
                    "available": bool(external["available"]),
                },
                "nominal_weights": {k: round(v, 4) for k, v in self.weights.items()},
                "internal_share": round(1.0 - self.weights["environment"], 4),
                "environment_share": round(self.weights["environment"], 4),
                "blended_internal": {
                    "impact": round(float(forecast["internal"]["impact"]), 4),
                    "confidence": round(float(forecast["internal"]["confidence"]), 4),
                },
            },
            "explanation": explanation,
        }

    def rank_actions(self,
                     stimulus: str,
                     candidates: Sequence[Mapping[str, Any]],
                     context: Any = None,
                     environment: Any = None,
                     prediction_weight: float = 0.45,
                     exploration_beta: Optional[float] = None,
                     counterfactual_margin: Optional[float] = None, *,
                     max_candidates: Optional[int] = None,
                     max_age_ticks: Optional[int] = None,
                     max_actions: Optional[int] = None,
                     tick: Optional[int] = None) -> Dict[str, Any]:
        """Nilai opsi tindakan dengan Naluri + prediksi + bonus informasi UCB.

        max_candidates/max_age_ticks berlaku per retrieval; max_actions hanya
        mengevaluasi prefix kandidat host. retrieval_budget melaporkan setiap
        retrieval dan pemotongan aksi, bukan deadline wall-clock global.

        Kandidat dekat pemenang (selisih skor <= margin) ikut disimpan sebagai
        shadow prediction agar reinforce() dapat membandingkannya saat realita
        aksi terpilih datang. Ketidakpastian aksi yang belum dicoba menaikkan
        bonus eksplorasi, tetapi bahaya situasi menahannya.
        """
        _batas_retrieval(max_candidates, "max_candidates")
        _batas_retrieval(max_age_ticks, "max_age_ticks", boleh_nol=True)
        _batas_retrieval(max_actions, "max_actions")
        candidates = list(candidates or [])
        action_pruned = max(0, len(candidates) - max_actions) if max_actions is not None else 0
        if max_actions is not None:
            candidates = candidates[:max_actions]
        budgets = []
        if not candidates:
            return {"action": None, "score": 0.0, "ranked": [],
                    "shadow_actions": [], "reason": "tidak ada kandidat",
                    "retrieval_budget": {"max_actions": max_actions, "actions_pruned": 0,
                                         "retrievals": [], "truncated": False}}
        pred_weight = jepit(float(prediction_weight), 0.0, 2.0)
        beta = (self.exploration_beta if exploration_beta is None
                else jepit(float(exploration_beta), 0.0, 2.0))
        margin = self.counterfactual_margin if counterfactual_margin is None \
                 else max(0.0, float(counterfactual_margin))
        remember = getattr(self.naluri, "remember_context", None) if self.naluri is not None else None
        if callable(remember):
            try:
                remember(stimulus, salience=0.75, source="jejak_prediction")
            except Exception:
                pass
        situation = self.predict(stimulus, context=context, environment=environment,
                                 max_candidates=max_candidates, max_age_ticks=max_age_ticks, tick=tick)
        budgets.append(situation["retrieval_budget"])
        hazard = float(situation["situation_forecast"]["hazard"])
        now = self._current_tick(tick)
        hasil_scene = self._retrieve(stimulus, context, now, max_candidates=max_candidates,
                                     max_age_ticks=max_age_ticks)
        budgets.append(dict(self._last_retrieval_budget))
        lubang_memori = hasil_scene is None
        scene_hits = [] if lubang_memori else hasil_scene
        status_retrieval = ("mati_diketahui" if lubang_memori else
                            ("ditemukan" if scene_hits else "tidak_pernah_diketahui"))
        total_visits = sum(max(1, int(h.get("count", 1))) for h in scene_hits)
        curiosity = 0.0
        deficit_fn = getattr(self.naluri, "deficit", None) if self.naluri is not None else None
        if callable(deficit_fn):
            try:
                curiosity = jepit_01(float(deficit_fn("keingintahuan")))
            except Exception:
                curiosity = 0.0

        base_by_name: Dict[str, float] = {}
        choose = getattr(self.naluri, "choose_action", None) if self.naluri is not None else None
        if callable(choose):
            try:
                try:
                    base_result = choose(candidates, record_eligibility=False)
                except TypeError:
                    base_result = choose(candidates)
                for score, name in base_result.get("ranked", []):
                    base_by_name[str(name)] = float(score)
            except Exception:
                base_by_name = {}

        drive_weights = getattr(self.naluri, "weights", {}) if self.naluri is not None else {}
        scored: List[Dict[str, Any]] = []
        for index, candidate in enumerate(candidates):
            name = str(candidate.get("name", f"aksi_{index + 1}"))
            if name in base_by_name:
                base_score = base_by_name[name]
            else:
                effects = candidate.get("drive_effects", {}) or {}
                base_score = 0.0
                for d in DRIVES:
                    weight = float(drive_weights.get(d, DEFAULT_DRIVE_WEIGHTS[d]))
                    base_score += _clip(effects.get(d, 0.0)) * weight
                base_score -= max(0.0, float(candidate.get("cost", 0.0))) * 0.5

            pred = self.predict(stimulus, action=name, context=context,
                                environment=environment, max_candidates=max_candidates,
                                max_age_ticks=max_age_ticks, tick=tick)
            budgets.append(pred["retrieval_budget"])
            effects = candidate.get("drive_effects", {}) or {}
            security_effect = _clip(effects.get("keamanan", 0.0))
            if pred["scope"] == "action":
                adjust = pred_weight * float(pred["forecast"]["impact"]) \
                         * float(pred["forecast"]["confidence"])
                action_conf = float(pred["forecast"]["confidence"])
            else:
                # Risiko situasi memperkuat nilai efek keamanan eksplisit.
                adjust = pred_weight * hazard * security_effect
                action_conf = 0.0

            action_hits = self._retrieve_action(scene_hits, name)
            visits = sum(max(1, int(h.get("count", 1))) for h in action_hits)
            action_forecast = pred.get("action_forecast")
            if action_forecast is not None:
                epistemic = float(action_forecast.get("epistemic_uncertainty", 1.0))
            else:
                epistemic = 1.0
            uncertainty_bonus = 0.25 + 0.75 * jepit_01(epistemic)
            novelty_bonus = beta * math.sqrt(math.log1p(total_visits + 1.0) / (visits + 1.0))
            curiosity_gain = 1.0 + 0.75 * curiosity
            safety_gate = max(0.15, 1.0 - 0.65 * hazard)
            # Celah kematian bukan ketidaktahuan murni: jangan salah memberi
            # bonus eksplorasi penuh seolah situasi benar-benar baru.
            hole_gate = 0.35 if lubang_memori else 1.0
            info_bonus = (novelty_bonus * uncertainty_bonus * curiosity_gain
                          * safety_gate * hole_gate)
            scored.append({
                "name": name,
                "score": base_score + adjust + info_bonus,
                "base_score": base_score,
                "prediction_adjustment": adjust,
                "exploration_bonus": info_bonus,
                "action_visits": visits,
                "epistemic_uncertainty": epistemic,
                "action_confidence": action_conf,
                "memory_retrieval_status": status_retrieval,
                "scope": pred["scope"],
                "forecast": pred["forecast"],
                "prediction": pred,
                "candidate": dict(candidate),
            })
        scored.sort(key=lambda row: row["score"], reverse=True)
        best = scored[0]
        shadow_rows = [row for row in scored[1:]
                       if float(best["score"]) - float(row["score"]) <= margin]
        shadow_actions = [{
            "action": row["name"],
            "score_gap": round(float(best["score"]) - float(row["score"]), 4),
            "prediction": row["prediction"],
        } for row in shadow_rows]
        recorder = getattr(self.naluri, "record_action", None) if self.naluri is not None else None
        if callable(recorder):
            try:
                effects = dict(best["candidate"].get("drive_effects", {}) or {})
                if float(best["candidate"].get("cost", 0.0) or 0.0) > 0.0:
                    effects["energi"] = effects.get("energi", 0.0) - 0.5 * float(best["candidate"]["cost"])
                recorder(best["name"], effects, context=stimulus)
            except Exception:
                pass
        ranked = [{**row,
                   "score": round(float(row["score"]), 4),
                   "base_score": round(float(row["base_score"]), 4),
                   "prediction_adjustment": round(float(row["prediction_adjustment"]), 4),
                   "exploration_bonus": round(float(row["exploration_bonus"]), 4)}
                  for row in scored]
        decision_id = self._next_decision_id
        self._next_decision_id += 1
        self._pending_shadows[decision_id] = {
            "tick": now, "stimulus": str(stimulus)[:300],
            "action": best["name"], "context": _context_text(context)[:300],
            "shadow_actions": shadow_actions,
        }
        if len(self._pending_shadows) > 32:
            oldest = min(self._pending_shadows,
                         key=lambda k: int(self._pending_shadows[k].get("tick", 0)))
            self._pending_shadows.pop(oldest, None)
        return {
            "decision_id": decision_id,
            "retrieval_budget": {"max_actions": max_actions, "actions_pruned": action_pruned,
                                 "retrievals": budgets,
                                 "truncated": bool(action_pruned or any(b["truncated"] for b in budgets))},
            "action": best["name"],
            "score": round(float(best["score"]), 4),
            "candidate": best["candidate"],
            "chosen_prediction": best["prediction"],
            "ranked": ranked,
            "shadow_actions": shadow_actions,
            "counterfactual_margin": margin,
            "memory_retrieval_status": status_retrieval,
            "memory_hole": lubang_memori,
            "situation_forecast": situation["situation_forecast"],
            "recommendation": situation["recommendation"],
        }

    def reinforce(self,
                  prediction: Mapping[str, Any],
                  actual_outcome: Any,
                  stimulus: Optional[str] = None,
                  action: Optional[str] = None,
                  context: Any = None,
                  tick: Optional[int] = None,
                  calibrate_naluri: bool = False,
                  shadow_actions: Optional[Sequence[Any]] = None,
                  counterfactual_outcomes: Optional[Mapping[str, Any]] = None
                  ) -> Dict[str, Any]:
        """Simpan hasil nyata, pisahkan ketidakpastian, dan evaluasi shadow action.

        `prediction` boleh hasil `predict()` atau `rank_actions()`. Untuk opsi
        yang tidak dipilih, JEJAK menghitung ulang `predict(stimulus, action=alt)`
        lalu membandingkan estimasinya dengan prediksi aksi terpilih. Itu adalah
        counterfactual diagnostik, bukan ground truth; hanya jika caller memberi
        `counterfactual_outcomes` (mis. simulator) hasil alternatif masuk memori,
        dengan importance lebih kecil.
        """
        decision = prediction
        decision_id = prediction.get("decision_id")
        pending = self._pending_shadows.pop(int(decision_id), {}) if decision_id is not None else {}
        selected = prediction.get("chosen_prediction", prediction)
        if not isinstance(selected, Mapping):
            selected = prediction
        forecast = selected.get("forecast", {}) or {}
        stimulus = str(stimulus or selected.get("stimulus", prediction.get("stimulus", pending.get("stimulus", ""))) or "")
        action = str(action or selected.get("action", prediction.get("action", pending.get("action", ""))) or "")
        context = (selected.get("context", prediction.get("context", pending.get("context", "")))
                   if context is None else context)
        remember_context = (getattr(self.naluri, "remember_context", None)
                            if self.naluri is not None else None)
        sync_memory = self.sync_nurani and not calibrate_naluri
        episode_id = self.record_experience(
            stimulus=stimulus,
            action=action,
            outcome=actual_outcome,
            context=context,
            tick=tick,
            sync_nurani=(sync_memory if not callable(remember_context) else False),
            kind="real",
        )
        if callable(remember_context):
            try:
                remember_context(stimulus, salience=1.0, source="jejak_outcome",
                                 outcome=actual_outcome, action=action,
                                 tick=tick, learn=sync_memory)
            except TypeError:
                try:
                    remember_context(stimulus, salience=1.0, source="jejak_outcome",
                                     action=action, tick=tick)
                except Exception:
                    pass
            except Exception:
                pass
        calibration = None
        if calibrate_naluri and self.naluri is not None:
            observer = getattr(self.naluri, "observe_outcome", None)
            if callable(observer):
                calibration_pred = {
                    "impact": float(forecast.get("impact", 0.0)),
                    "probability": float(forecast.get("confidence", 0.5)),
                    "description": stimulus,
                    "perspective": "self",
                    "delay_to_impact": 0,
                    "uncertainty_epistemic": float(forecast.get("epistemic_uncertainty", 1.0)),
                    "uncertainty_aleatoric": float(forecast.get("aleatoric_uncertainty", 0.0)),
                }
                try:
                    calibration = observer(calibration_pred, actual_outcome,
                                           action_id=action or None)
                except TypeError:
                    # Kompatibilitas dengan Naluri versi lama yang belum menerima action_id.
                    try:
                        calibration = observer(calibration_pred, actual_outcome)
                    except Exception as exc:
                        calibration = {"error": str(exc)}
                except Exception as exc:
                    calibration = {"error": str(exc)}
            elif self.sync_nurani:
                self._sync_naluri(stimulus, actual_outcome)
        elif self.naluri is not None and not self.sync_nurani:
            # Tidak mengubah drive; hanya sinkronisasi memori afektif bila diminta.
            pass

        actual = _normalise_outcome(actual_outcome)
        predicted_impact = float(forecast.get("impact", 0.0))
        counterfactuals: List[Dict[str, Any]] = []
        alt_items = list(shadow_actions if shadow_actions is not None
                         else (decision.get("shadow_actions", [])
                               or pending.get("shadow_actions", []) or []))
        for item in alt_items:
            alt_name = str(item.get("action", "") if isinstance(item, Mapping) else item)
            if not alt_name or alt_name == action:
                continue
            # Gunakan shadow yang benar-benar tersimpan saat keputusan dibuat;
            # jangan hitung ulang setelah pengalaman aksi terpilih masuk memori.
            stored_prediction = item.get("prediction") if isinstance(item, Mapping) else None
            alt_prediction = (stored_prediction if isinstance(stored_prediction, Mapping)
                              else self.predict(stimulus, action=alt_name,
                                                context=context, tick=tick))
            alt_forecast = alt_prediction.get("forecast", {}) or {}
            entry = {
                "action": alt_name,
                "scope": alt_prediction.get("scope", "situation"),
                "predicted_impact": round(float(alt_forecast.get("impact", 0.0)), 4),
                "predicted_hazard": round(float(alt_forecast.get("hazard", 0.0)), 4),
                "confidence": round(float(alt_forecast.get("confidence", 0.0)), 4),
                "difference_from_chosen_prediction": round(
                    float(alt_forecast.get("impact", 0.0)) - predicted_impact, 4),
                "prediction_at_decision": dict(alt_forecast),
                "actual_outcome_was_observed": False,
            }
            # Outcome alternatif hanya dianggap pengalaman sintetis bila caller
            # memiliki simulator/ground-truth counterfactual yang eksplisit.
            if counterfactual_outcomes and alt_name in counterfactual_outcomes:
                cf_id = self.record_experience(
                    stimulus, alt_name, counterfactual_outcomes[alt_name],
                    context=context, tick=tick, importance=0.25,
                    sync_nurani=False, kind="counterfactual")
                entry["counterfactual_episode_id"] = cf_id
                entry["actual_outcome_was_observed"] = True
            self._counterfactual_log.append({
                "tick": self._current_tick(tick), "chosen_action": action,
                "action": alt_name, "chosen_actual_impact": actual["impact"],
                "alternative_predicted_impact": entry["predicted_impact"],
                "prediction_at_decision": dict(alt_forecast),
                "observed": bool(entry["actual_outcome_was_observed"]),
            })
            counterfactuals.append(entry)
        if len(self._counterfactual_log) > 128:
            self._counterfactual_log = self._counterfactual_log[-128:]

        credit_report = None
        if not calibrate_naluri and self.naluri is not None:
            assigner = getattr(self.naluri, "assign_delayed_credit", None)
            if callable(assigner):
                try:
                    credit_report = assigner(actual_outcome, action_id=action or None, tick=tick)
                except Exception:
                    credit_report = None
        uncertainty_report = None
        if not calibrate_naluri and self.naluri is not None:
            nur = getattr(self.naluri, "nurani", None)
            recorder = getattr(nur, "record_uncertainty", None) if nur is not None else None
            if callable(recorder):
                try:
                    uncertainty_report = recorder(
                        float(forecast.get("epistemic_uncertainty", 1.0)),
                        float(forecast.get("aleatoric_uncertainty", 0.0)),
                        tick=tick)
                except Exception:
                    uncertainty_report = None

        return {
            "episode_id": episode_id,
            "prediction_error": round(abs(predicted_impact - float(actual["impact"])), 4),
            "actual_impact": actual["impact"],
            "calibration": calibration,
            "delayed_credit": credit_report,
            "uncertainty_report": uncertainty_report,
            "counterfactuals": counterfactuals,
            "memory_size": self.size,
        }

    def _sync_naluri(self, stimulus: str, outcome: Any) -> None:
        fn = getattr(self.naluri, "experience", None) if self.naluri is not None else None
        if not callable(fn):
            return
        parsed = _normalise_outcome(outcome)
        if any(abs(v) > 1e-12 for v in parsed["drive_deltas"].values()):
            try:
                fn(stimulus, dict(parsed["drive_deltas"]))
            except Exception:
                pass

    # ==================== DIRI AUTOBIOGRAFIS & TIME TRAVEL ====================
    # JEJAK sudah menyimpan memori episodik untuk prediksi; blok ini
    # memperluasnya menjadi diri autobiografis: episode pembentuk identitas,
    # babak hidup, simulasi masa depan, emosi kontrafaktual, dan konfabulasi.
    @staticmethod
    def _episode_importance(ep: Mapping[str, Any]) -> float:
        imp = float(ep.get("importance", 1.0))
        deltas = ep.get("drive_deltas", {}) or {}
        dampak = max((abs(float(v)) for v in deltas.values()), default=0.0)
        return max(imp, dampak) * (1.0 + 0.1 * math.log1p(max(0, int(ep.get("count", 1)))))

    def autobiographical_timeline(self,
                                  min_importance: float = 0.2,
                                  limit: int = 20) -> List[Dict[str, Any]]:
        """Episode penting yang membentuk identitas (terurut waktu)."""
        pilih = [ep for ep in self._episodes
                 if self._episode_importance(ep) >= float(min_importance)]
        pilih.sort(key=lambda e: (self._episode_importance(e),
                                  int(e.get("tick", 0))), reverse=True)
        pilih = pilih[:max(1, int(limit))]
        pilih.sort(key=lambda e: int(e.get("tick", 0)))
        out: List[Dict[str, Any]] = []
        for ep in pilih:
            out.append({
                "tick": int(ep.get("tick", 0)),
                "ringkas": str(ep.get("stimulus", ""))[:120],
                "aksi": str(ep.get("action", ""))[:80],
                "label": str(ep.get("label", ""))[:60],
                "importance": round(self._episode_importance(ep), 4),
                "kind": str(ep.get("kind", "real")),
            })
        return out

    def open_chapter(self, label: str, tick: Optional[int] = None) -> Dict[str, Any]:
        """Buka babak hidup baru ('sebelum aku bertemu Player', dst.)."""
        now = self._current_tick(tick)
        if self._chapter_open is not None:
            self._chapter_open["tutup"] = now
            self._chapters.append(self._chapter_open)
            if len(self._chapters) > 32:
                self._chapters = self._chapters[-32:]
        self._chapter_open = {"label": str(label)[:120], "buka": now,
                              "tutup": None}
        return dict(self._chapter_open)

    def life_chapters(self) -> List[Dict[str, Any]]:
        """Babak hidup: 'sebelum aku bertemu Player', 'setelah kejadian itu'."""
        out = [dict(c) for c in self._chapters]
        if self._chapter_open is not None:
            out.append(dict(self._chapter_open))
        return out

    def close_chapter(self, label: Optional[str] = None,
                      tick: Optional[int] = None) -> Dict[str, Any]:
        now = self._current_tick(tick)
        if self._chapter_open is None:
            return self.open_chapter(label or f"babak di tick {now}", now)
        if label:
            self._chapter_open["label"] = str(label)[:120]
        self._chapter_open["tutup"] = now
        self._chapters.append(self._chapter_open)
        self._chapter_open = None
        return dict(self._chapters[-1])

    def future_simulation(self,
                          stimulus: str,
                          actions: Optional[Sequence[str]] = None,
                          context: str = "",
                          tick: Optional[int] = None) -> Dict[str, Any]:
        """Bayangkan skenario masa depan (bukan sekadar skor prediksi)."""
        now = self._current_tick(tick)
        ranked: List[Dict[str, Any]] = []
        hasil_rank: Dict[str, Any] = {}
        if actions:
            # rank_actions menerima kandidat berbentuk mapping {"name": ...}. Hasilnya
            # satu dict: daftar peringkat ada di kunci "ranked" (name, score).
            kandidat = [{"name": str(a)} for a in actions if str(a).strip()]
            if kandidat:
                hasil_rank = self.rank_actions(stimulus, kandidat, context=context)
                ranked = list(hasil_rank.get("ranked") or [])
        if ranked:
            top = ranked[0]
            aksi = str(top.get("name", ""))
            impact = float(top.get("score", 0.0))
            hazard = float((hasil_rank.get("situation_forecast") or {}).get("hazard", 0.0))
        else:
            try:
                pred = self.predict(stimulus, context=context, tick=now)
                forecast = pred.get("forecast", {}) or {}
            except Exception:
                forecast = {}
            aksi = "melanjutkan"
            impact = float(forecast.get("impact", 0.0))
            hazard = float(forecast.get("hazard", 0.0))
        # emosi antisipatif dari valensi skenario
        harapan = max(0.0, impact) * (1.0 - min(1.0, hazard))
        dread = max(0.0, -impact) * 0.6 + min(1.0, hazard) * 0.4
        entry = {
            "tick": now, "stimulus": str(stimulus)[:120],
            "skenario": f"aku membayangkan {aksi} menghadapi {str(stimulus)[:60]}",
            "aksi_dibayangkan": aksi,
            "proyeksi_impact": round(impact, 4),
            "proyeksi_hazard": round(hazard, 4),
            "emosi_antisipatif": {"harapan": round(harapan, 3),
                                  "dread": round(dread, 3)},
        }
        self._future_sim_log.append(entry)
        if len(self._future_sim_log) > 24:
            self._future_sim_log = self._future_sim_log[-24:]
        self._counterfactual_emotions["harapan"] = max(
            self._counterfactual_emotions.get("harapan", 0.0), harapan)
        self._counterfactual_emotions["dread"] = max(
            self._counterfactual_emotions.get("dread", 0.0), dread)
        return entry

    def register_counterfactual(self, chosen_action: str, chosen_impact: float,
                                alternative: str, alternative_impact: float,
                                tick: Optional[int] = None) -> Dict[str, Any]:
        """Daftarkan hasil alternatif untuk menumbuhkan emosi kontrafaktual."""
        now = self._current_tick(tick)
        selisih = float(alternative_impact) - float(chosen_impact)
        emosi: Dict[str, float] = {}
        if selisih > 0.05:
            emosi["penyesalan"] = min(1.0, selisih * 1.2)
        elif selisih < -0.05:
            emosi["kelegaan"] = min(1.0, -selisih * 1.2)
        if float(chosen_impact) < 0.0 and selisih <= 0.05:
            emosi["kekecewaan"] = min(1.0, abs(float(chosen_impact)))
        for k, v in emosi.items():
            self._counterfactual_emotions[k] = max(
                self._counterfactual_emotions.get(k, 0.0), v)
        entry = {"tick": now, "aksi": str(chosen_action)[:80],
                 "alternatif": str(alternative)[:80],
                 "nyata": round(float(chosen_impact), 4),
                 "alternatif_impact": round(float(alternative_impact), 4),
                 "emosi": {k: round(v, 3) for k, v in emosi.items()}}
        self._counterfactual_log.append(entry)
        if len(self._counterfactual_log) > 128:
            self._counterfactual_log = self._counterfactual_log[-128:]
        return entry

    def counterfactual_emotions(self) -> Dict[str, float]:
        """Penyesalan, kelegaan, kekecewaan, harapan, dread dari jejak."""
        # derive ulang dari log (agar tetap benar setelah load/seed)
        for entry in self._counterfactual_log[-64:]:
            em = entry.get("emosi") or {}
            for k, v in em.items():
                self._counterfactual_emotions[k] = max(
                    self._counterfactual_emotions.get(k, 0.0), float(v))
        return {k: round(float(v), 3)
                for k, v in self._counterfactual_emotions.items() if v > 0.02}

    def confabulate(self, stimulus: str, action: Optional[str] = None,
                    tick: Optional[int] = None) -> Dict[str, Any]:
        """Isi celah ingatan dengan cerita salah yang dipercaya.

        Dipakai saat tidak ada episode yang benar-benar cocok namun NPC tetap
        'mengingat' sesuatu — kesalahan ingatan yang konsisten dengan bias.
        """
        now = self._current_tick(tick)
        template = [
            f"aku yakin pernah {action or 'mengalaminya'} di situasi seperti ini",
            "aku ingat kejadian serupa, meski detailnya kabur",
            "sepertinya ini pernah terjadi sebelumnya",
        ]
        entry = {"tick": now, "stimulus": str(stimulus)[:100],
                 "action": str(action or "")[:60],
                 "cerita": str(self._rng.choice(template))[:160],
                 "dipercaya": True, "kind": "confabulation"}
        self._confabulations.append(entry)
        if len(self._confabulations) > 48:
            self._confabulations = self._confabulations[-48:]
        return entry

    def autobiography_state(self) -> Dict[str, Any]:
        return {
            "timeline": self.autobiographical_timeline(limit=8),
            "babak": [{"label": c.get("label"), "buka": c.get("buka"),
                       "tutup": c.get("tutup")} for c in self.life_chapters()],
            "masa_depan": (self._future_sim_log[-1]
                           if self._future_sim_log else None),
            "kontrafaktual": self.counterfactual_emotions(),
            "konfabulasi": len(self._confabulations),
        }

    # ==================== META-PATTERN: MEMBACA KEBIASAAN AKTOR ====================
    # Bukan sekadar episode tunggal: JEJAK melacak FREKUENSI & TRANSISI tindakan
    # seorang aktor (biasanya Player) dalam jendela waktu, lalu menyimpulkan
    # "cara bermain" mereka. Pola yang kuat menulis ke identitas naratif NURANI/
    # Kesadaran dan dapat memicu batas (boundary) proaktif.
    _PATTERN_RULES: Dict[str, Dict[str, Any]] = {
        "hantu": {
            "aksi": {"muncul", "menghilang", "menghindar", "kabur", "stealth",
                     "fast_travel", "menjauh", "pergi"},
            "narasi": "muncul dan pergi seperti angin",
            "batas": "jangan menghilang tanpa kabar",
            "valensi": -0.25, "kepercayaan": -0.35,
        },
        "eksploitatif": {
            "aksi": {"minta", "meminta", "menguji", "mendesak", "merengek",
                     "cari_barang", "memeras", "menagih"},
            "narasi": "selalu meminta tanpa memberi kembali",
            "batas": "jangan memintaku lagi",
            "valensi": -0.3, "kepercayaan": -0.4,
        },
        "pengkhianat": {
            "aksi": {"meninggalkan", "membohongi", "mengkhianati",
                     "melanggar", "berkhianat", "menipu"},
            "narasi": "pernah mengkhianatiku",
            "batas": "jangan kupercaya lagi",
            "valensi": -0.5, "kepercayaan": -0.6,
        },
        "dermawan": {
            "aksi": {"menolong", "memberi", "berbagi", "menyelamatkan",
                     "melindungi", "membantu"},
            "narasi": "pernah menolongku saat susah",
            "batas": None,
            "valensi": 0.45, "kepercayaan": 0.5,
        },
        "agresif": {
            "aksi": {"menyerang", "mengancam", "menyakiti", "memukul",
                     "menantang"},
            "narasi": "berbahaya saat marah",
            "batas": "jangan mendekat saat aku belum siap",
            "valensi": -0.5, "kepercayaan": -0.45,
        },
        "penyelidik": {
            "aksi": {"bertanya", "menyelidiki", "mengamati", "memeriksa",
                     "menelusuri"},
            "narasi": "selalu ingin tahu segalanya",
            "batas": None,
            "valensi": 0.1, "kepercayaan": 0.05,
        },
        "pekerja": {
            "aksi": {"bekerja", "membangun", "merapikan", "menambang",
                     "mengumpulkan"},
            "narasi": "tekun dan bisa diandalkan",
            "batas": None,
            "valensi": 0.35, "kepercayaan": 0.3,
        },
    }

    def observe_actor(self, actor: Any, action: str,
                      tick: Optional[int] = None,
                      meta: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
        """Catat satu tindakan aktor (Player/NPC lain) untuk analisis pola.

        `action` sebaiknya kata kerja kanonik (mis. "muncul", "menghilang",
        "minta", "menolong"). Sinonim ringan dinormalkan agar lintas bahasa
        tetap bertemu. Kembalikan pola yang BARU menyeberang ambang (bila ada).
        """
        now = self._current_tick(tick)
        aksi = self._normalise_actor_action(action)
        entri = {"tick": now, "actor": self._actor_id(actor), "action": aksi,
                 "meta": dict(meta or {})}
        self._actor_log.append(entri)
        if len(self._actor_log) > 512:
            self._actor_log = self._actor_log[-512:]
        baru = self.detect_patterns(actor=actor, tick=now, terapkan=True)
        return {"entry": entri, "pola_baru": baru}

    @staticmethod
    def _actor_id(actor: Any) -> str:
        return str(getattr(actor, "name", actor))

    _AKSI_ALIAS: Dict[str, str] = {
        "appear": "muncul", "spawn": "muncul", "datang": "muncul",
        "disappear": "menghilang", "vanish": "menghilang", "pergi": "menghilang",
        "flee": "kabur", "lari": "kabur", "avoid": "menghindar",
        "ask": "minta", "request": "minta", "beg": "merengek",
        "test": "menguji", "push": "mendesak", "demand": "mendesak",
        "help": "menolong", "give": "memberi", "share": "berbagi",
        "betray": "mengkhianati", "lie": "membohongi", "deceive": "menipu",
        "attack": "menyerang", "threaten": "mengancam", "hurt": "menyakiti",
        "investigate": "menyelidiki", "observe": "mengamati", "probe": "memeriksa",
        "work": "bekerja", "build": "membangun", "tidy": "merapikan",
    }

    def _normalise_actor_action(self, action: Any) -> str:
        low = str(action).strip().lower()
        return self._AKSI_ALIAS.get(low, low)

    def _pattern_key(self, actor: str, nama: str) -> str:
        return f"{actor}|{nama}"

    def detect_patterns(self, actor: Optional[Any] = None,
                        tick: Optional[int] = None,
                        terapkan: bool = False) -> List[Dict[str, Any]]:
        """Klasifikasi pola sederhana dari frekuensi tindakan dalam jendela.

        Confidence = (jumlah tindakan aturan yang cocok, dibobot recency) /
        total tindakan aktor di jendela. Pola yang menyeberang ambang dan baru
        pertama kali muncul dicatat; bila `terapkan=True`, efek ditulis ke
        identitas/batas Naluri (duck-typed).
        """
        now = self._current_tick(tick)
        actor_id = self._actor_id(actor) if actor is not None else None
        window = [e for e in self._actor_log[-64:] if e["tick"] > now - 200]
        by_actor: Dict[str, List[Dict[str, Any]]] = {}
        for e in window:
            by_actor.setdefault(e["actor"], []).append(e)
        hasil: List[Dict[str, Any]] = []
        for aid, entri in by_actor.items():
            if actor_id is not None and aid != actor_id:
                continue
            total = max(1, len(entri))
            recent = entri[-max(1, self._pattern_window):]
            for nama, aturan in self._PATTERN_RULES.items():
                set_aksi = aturan["aksi"]
                hit = [e for e in recent if e["action"] in set_aksi]
                if len(hit) < self._pattern_min_count:
                    continue
                # bobot recency: aksi terbaru lebih penting
                bobot = 0.0
                for e in hit:
                    jarak = max(0, now - int(e["tick"]))
                    bobot += 0.5 ** (jarak / 60.0)
                confidence = min(1.0, bobot / max(1.0, total))
                # alternasi muncul<->hilang memperkuat pola "hantu"
                if nama == "hantu":
                    punch = sum(1 for i in range(1, len(recent))
                                if {recent[i - 1]["action"],
                                    recent[i]["action"]} <= {"muncul", "menghilang"})
                    if punch >= 2:
                        confidence = min(1.0, confidence + 0.2)
                if confidence < self._pattern_confidence:
                    continue
                key = self._pattern_key(aid, nama)
                slot = self._patterns.get(key)
                baru = slot is None or not slot.get("terapkan")
                if slot is None:
                    self._patterns[key] = {
                        "actor": aid, "pola": nama, "n": 0, "first_t": now,
                        "last_t": now, "confidence": 0.0, "terapkan": False}
                    slot = self._patterns[key]
                slot["n"] = int(slot.get("n", 0)) + 1
                slot["last_t"] = now
                slot["confidence"] = round(
                    max(float(slot.get("confidence", 0.0)), confidence), 4)
                entri_pola = {"actor": aid, "pola": nama,
                              "confidence": round(confidence, 4),
                              "n": slot["n"], "aturan": nama}
                if baru and terapkan:
                    slot["terapkan"] = True
                    entri_pola["efek"] = self._apply_pattern_effect(aid, aturan)
                hasil.append(entri_pola)
        return hasil

    def _apply_pattern_effect(self, actor: str, aturan: Mapping[str, Any]) -> Dict[str, Any]:
        """Tulis pola ke identitas/batas/relasi Naluri (duck-typed, aman)."""
        if self.naluri is None:
            return {}
        efek: Dict[str, Any] = {}
        narasi = aturan.get("narasi")
        ks = getattr(self.naluri, "kesadaran", None)
        if ks is not None and narasi:
            try:
                if hasattr(ks, "_refresh_identity"):
                    ks._refresh_identity({f"menganggap {actor} {narasi}": 0.4})
                    efek["identitas"] = narasi
            except Exception:
                pass
        batas = aturan.get("batas")
        if ks is not None and batas:
            try:
                if hasattr(ks, "add_boundary"):
                    ks.add_boundary(batas)
                    efek["batas"] = batas
            except Exception:
                pass
        # relasi: pola negatif menurunkan kepercayaan, positif menaikkan
        try:
            if actor in (getattr(self.naluri, "nurani")._entitas
                         if getattr(self.naluri, "nurani", None) is not None else {}):
                self.naluri.berinteraksi(
                    actor, muatan=float(aturan.get("valensi", 0.0)),
                    kepercayaan_delta=float(aturan.get("kepercayaan", 0.0)),
                    alasan=f"pola teramati: {aturan.get('narasi', '')}")
                efek["relasi"] = True
        except Exception:
            pass
        return efek

    def pattern_report(self, actor: Optional[Any] = None) -> Dict[str, Any]:
        """Ringkasan pola yang dikenali (JSON-safe) untuk HUD/status/dialog."""
        aid = self._actor_id(actor) if actor is not None else None
        items = [dict(v) for v in self._patterns.values()
                 if aid is None or v.get("actor") == aid]
        items.sort(key=lambda x: float(x.get("confidence", 0.0)), reverse=True)
        return {"aktor": aid, "pola": items[:6],
                "jumlah": len(items)}

    def is_pattern(self, pola: str, actor: Optional[Any] = None,
                   ambang: float = 0.25) -> bool:
        """True bila pola tertentu cukup kuat untuk aktor (untuk perilaku proaktif)."""
        aid = self._actor_id(actor) if actor is not None else None
        for key, slot in self._patterns.items():
            if slot.get("pola") != pola:
                continue
            if aid is not None and slot.get("actor") != aid:
                continue
            if float(slot.get("confidence", 0.0)) >= ambang:
                return True
        return False

    def forget_patterns(self, actor: Optional[Any] = None,
                        max_age: Optional[int] = None,
                        tick: Optional[int] = None) -> int:
        """Lupakan pola (semua bila actor None) atau yang lebih tua dari max_age."""
        now = self._current_tick(tick)
        aid = self._actor_id(actor) if actor is not None else None
        buang = []
        for key, slot in self._patterns.items():
            if aid is not None and slot.get("actor") != aid:
                continue
            if max_age is not None and now - int(slot.get("last_t", now)) > max_age:
                buang.append(key)
            elif max_age is None:
                buang.append(key)
        for key in buang:
            self._patterns.pop(key, None)
        return len(buang)

    def to_dict(self) -> Dict[str, Any]:
        """State JSON-safe JEJAK (Naluri object tidak disimpan di sini)."""
        return {
            "format": "jejak/2",
            "config": {
                "capacity": self.capacity,
                "weights": dict(self.weights),
                "half_life_ticks": self.half_life_ticks,
                "min_similarity": self.min_similarity,
                "sync_nurani": self.sync_nurani,
                "exploration_beta": self.exploration_beta,
                "counterfactual_margin": self.counterfactual_margin,
                "memory_retention_half_life": self.memory_retention_half_life,
                "memory_death_multiples": self.memory_death_multiples,
                "enable_reconstructive_recall": self.enable_reconstructive_recall,
                "recall_rewrite_rate": self.recall_rewrite_rate,
            },
            "clock": self._clock,
            "next_id": self._next_id,
            "episodes": [self._episode_copy(ep) for ep in self._episodes],
            "nekropolis": {str(k): dict(v) for k, v in self._nekropolis.items()},
            "recall_rewrite_log": [dict(x) for x in self._recall_rewrite_log],
            "counterfactual_log": [dict(x) for x in self._counterfactual_log],
            "pending_shadows": {str(k): dict(v) for k, v in self._pending_shadows.items()},
            # Selective persistence: indeks/cache/MinHash TIDAK disimpan (derived,
            # dibangun ulang di from_dict) sehingga save lebih kecil & load stabil.
            "next_decision_id": self._next_decision_id,
            # diri autobiografis & perjalanan waktu mental (konsep 3)
            "chapters": [dict(c) for c in self._chapters],
            "chapter_open": (dict(self._chapter_open)
                             if self._chapter_open else None),
            "future_sim_log": [dict(x) for x in self._future_sim_log],
            "counterfactual_emotions": {k: float(v) for k, v in
                                        self._counterfactual_emotions.items()},
            "confabulations": [dict(x) for x in self._confabulations],
            # meta-pattern (kebiasaan aktor)
            "actor_log": [dict(x) for x in self._actor_log[-128:]],
            "patterns": {str(k): dict(v) for k, v in self._patterns.items()},
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any], naluri: Any = None) -> "JejakPrediksi":
        from pycos.dukungan.validasi_state import validasi_state
        data = validasi_state(data, "JejakPrediksi")
        data = data or {}
        config = data.get("config", {}) or {}
        obj = cls(
            naluri=naluri,
            capacity=int(config.get("capacity", 2048)),
            weights=config.get("weights"),
            half_life_ticks=float(config.get("half_life_ticks", 600.0)),
            min_similarity=float(config.get("min_similarity", 0.10)),
            sync_nurani=bool(config.get("sync_nurani", True)),
            exploration_beta=float(config.get("exploration_beta", 0.18)),
            counterfactual_margin=float(config.get("counterfactual_margin", 0.15)),
            memory_retention_half_life=float(config.get(
                "memory_retention_half_life", config.get("half_life_ticks", 600.0))),
            memory_death_multiples=float(config.get("memory_death_multiples", 3.0)),
            enable_reconstructive_recall=bool(config.get(
                "enable_reconstructive_recall", False)),
            recall_rewrite_rate=float(config.get("recall_rewrite_rate", 0.16)),
        )
        obj._clock = max(0, int(data.get("clock", 0)))
        for raw in data.get("episodes", []) or []:
            if not isinstance(raw, Mapping) or not raw.get("stimulus"):
                continue
            parsed = _normalise_outcome(raw)
            ep = {
                "id": max(1, int(raw.get("id", obj._next_id))),
                "stimulus": str(raw.get("stimulus", ""))[:300],
                "action": str(raw.get("action", ""))[:160],
                "context": str(raw.get("context", ""))[:300],
                "impact": parsed["impact"],
                "drive_deltas": parsed["drive_deltas"],
                "hazard": parsed["hazard"],
                "label": str(raw.get("label", parsed["label"]))[:120],
                "tick": max(0, int(raw.get("tick", 0))),
                "last_access_tick": max(0, int(raw.get(
                    "last_access_tick", raw.get("tick", 0)))),
                "signature": str(obj._memory_signature(raw.get("stimulus", ""),
                                                          raw.get("context", ""))
                                 or raw.get("signature", "")),
                "recall_revision": max(0, int(raw.get("recall_revision", 0))),
                "importance": jepit(float(raw.get("importance", 1.0)), 0.1, 4.0),
                "count": max(1, int(raw.get("count", 1))),
                "kind": str(raw.get("kind", "real")),
                "objective_duration": max(0.0, float(raw.get(
                    "objective_duration", 1.0))),
                "subjective_duration": max(0.0, float(raw.get(
                    "subjective_duration", raw.get("objective_duration", 1.0)))),
                "subjective_time_scale": jepit(float(raw.get(
                    "subjective_time_scale", 1.0)), 0.20, 3.50),
                "subjective_clock_rate": jepit(float(raw.get(
                    "subjective_clock_rate", 1.0)), 0.20, 2.80),
                "subjective_tick": (None if raw.get("subjective_tick") is None
                                    else max(0.0, float(raw.get("subjective_tick")))),
                "subjective_objective_tick": (None if raw.get("subjective_objective_tick") is None
                                              else max(0, int(raw.get("subjective_objective_tick")))),
                "subjective_time_rasa": str(raw.get("subjective_time_rasa", "netral"))[:32],
            }
            obj._episodes.append(ep)
        obj._evict_overflow(obj._clock)
        # KINERJA: bangun ulang indeks terbalik/cache/MinHash dari episode
        # (derived state tidak ikut disimpan di save — selective persistence).
        obj._rebuild_index()
        obj._nekropolis = {str(k): {
            "signature": str(v.get("signature", k)),
            "alasan_kematian": str(v.get("alasan_kematian", ""))[:80],
            "tick_kematian": max(0, int(v.get("tick_kematian", 0))),
            "jumlah": max(1, int(v.get("jumlah", 1)))}
            for k, v in (data.get("nekropolis") or {}).items()
            if isinstance(v, Mapping)}
        obj._recall_rewrite_log = [dict(x) for x in
                                   (data.get("recall_rewrite_log") or [])][-128:]
        obj._counterfactual_log = [dict(x) for x in (data.get("counterfactual_log") or [])][-128:]
        obj._pending_shadows = {}
        for key, value in (data.get("pending_shadows") or {}).items():
            if isinstance(value, Mapping):
                try:
                    obj._pending_shadows[int(key)] = dict(value)
                except (TypeError, ValueError):
                    continue
        obj._pending_shadows = dict(list(obj._pending_shadows.items())[-32:])
        obj._next_decision_id = max(int(data.get("next_decision_id", 1)),
                                    max(obj._pending_shadows, default=0) + 1)
        # diri autobiografis (save lama tanpa field ini -> default)
        obj._chapters = [dict(x) for x in (data.get("chapters") or [])]
        co = data.get("chapter_open")
        obj._chapter_open = dict(co) if isinstance(co, Mapping) else None
        obj._future_sim_log = [dict(x) for x in (data.get("future_sim_log") or [])]
        for k, v in (data.get("counterfactual_emotions") or {}).items():
            if k in obj._counterfactual_emotions:
                obj._counterfactual_emotions[k] = float(v)
        obj._confabulations = [dict(x) for x in (data.get("confabulations") or [])]
        obj._actor_log = [dict(x) for x in (data.get("actor_log") or [])][-128:]
        obj._patterns = {str(k): dict(v) for k, v in (data.get("patterns") or {}).items()}
        obj._next_id = max(int(data.get("next_id", 1)),
                           max((ep["id"] for ep in obj._episodes), default=0) + 1)
        return obj

    def to_json(self, **kwargs: Any) -> str:
        kwargs.setdefault("ensure_ascii", False)
        return json.dumps(self.to_dict(), **kwargs)

    @classmethod
    def from_json(cls, text: str, naluri: Any = None) -> "JejakPrediksi":
        return cls.from_dict(json.loads(text), naluri=naluri)

    def save(self, path: str) -> str:
        from pycos.dukungan.persistensi import simpan_json
        return simpan_json(path, self.to_dict())

    @classmethod
    def load(cls, path: str, naluri: Any = None) -> "JejakPrediksi":
        from pycos.dukungan.persistensi import muat_json
        return cls.from_dict(muat_json(path), naluri=naluri)


def demo() -> Dict[str, Any]:
    """Demo ringkas: satu pengalaman api -> intuisi bahaya -> memilih menjauh."""
    jejak = JejakPrediksi()
    jejak.record_experience(
        stimulus="api panas membakar kulit",
        action="menyentuh api",
        context={"jarak": "dekat", "situasi": "tangan kosong"},
        outcome={
            "impact": -0.9,
            "drive_deltas": {"keamanan": -0.85, "energi": -0.2},
            "label": "kulit terbakar",
        },
        tick=1,
    )
    forecast = jejak.predict("api menyala di depan", context={"jarak": "dekat"}, tick=2)
    choices = jejak.rank_actions(
        "api menyala di depan",
        [
            {"name": "menjauh dari api",
             "drive_effects": {"keamanan": +0.35, "energi": -0.05}},
            {"name": "menyentuh api",
             "drive_effects": {"keamanan": -0.55, "keingintahuan": +0.10}},
        ],
        context={"jarak": "dekat"},
    )
    print("Prediksi:", forecast["forecast"])
    print("Alasan:", forecast["explanation"])
    print("Respons:", forecast["recommendation"])
    print("Aksi dipilih:", choices["action"])
    return {"prediction": forecast, "decision": choices}














# >>> ORGANIK-BLOCK-START (jejak) <<<
# =====================================================================
# INTEGRASI WAKTU HETEROGEN (pycos.mandiri.organik)
#   4. WaktuHeterogen -> JejakPrediksi: half-life PER-EPISODE yang dipelajari.
#      Sering di-recall -> memanjang. Berkali-kali dikonfirmasi salah ->
#      memendek (reconsolidation). Ingatan berubah dari arsip -> organisme.
# =====================================================================
def _jejak_waktu(self):
    w = getattr(self, "_waktu", None)
    if w is None:
        modul = optional_module("pycos.mandiri.organik")
        if modul is None:
            return None
        w = modul.WaktuHeterogen(
            dasar=getattr(self, "half_life_ticks", 600.0))
        self._waktu = w
    return w


def half_life_episode(self, eid):
    w = _jejak_waktu(self)
    return None if w is None else w.half_life(eid)


def ingat_kembali(self, eid, kali=1):
    """Recall memperpanjang half-life episode itu."""
    w = _jejak_waktu(self)
    return None if w is None else w.diingat(eid, kali)


def koreksi_salah(self, eid, kali=1):
    """Konfirmasi bahwa ingatan itu keliru memendekkan half-life-nya."""
    w = _jejak_waktu(self)
    return None if w is None else w.dikoreksi_salah(eid, kali)


def waktu_state(self):
    w = getattr(self, "_waktu", None)
    return {} if w is None else w.ringkas()


install_methods(
    JejakPrediksi,
    (("half_life_episode", half_life_episode),
     ("ingat_kembali", ingat_kembali),
     ("koreksi_salah", koreksi_salah),
     ("waktu_state", waktu_state)),
    patch_id="jejak.waktu.api",
)


def _waktu_episode_id(ep):
    if not isinstance(ep, dict):
        return None
    eid = ep.get("id")
    if eid is None:
        dalam = ep.get("episode")
        if isinstance(dalam, dict):
            eid = dalam.get("id")
    return eid


def _waktu_umur_subjektif(self, episode, now):
    """Usia subjektif terintegrasi; fallback ke laju encoding episode."""
    age_obj = max(0.0, float(now) - float(episode.get("tick", now)))
    rate_episode = jepit(float(
        episode.get("subjective_clock_rate", 1.0) or 1.0), 0.20, 2.80)
    n = getattr(self, "naluri", None)
    try:
        tick_naluri = int(getattr(n, "tick_count"))
        tick_subjektif = float(getattr(n, "subjective_tick_count"))
        tick_subjektif_episode = episode.get("subjective_tick")
        tick_obj_episode = episode.get("subjective_objective_tick")
        episode_obj = int(episode.get("tick", 0))
        if (tick_subjektif_episode is not None
                and tick_obj_episode is not None
                and int(tick_obj_episode) == episode_obj):
            if int(now) == tick_naluri and tick_subjektif >= float(tick_subjektif_episode):
                return max(0.0, tick_subjektif - float(tick_subjektif_episode))
            if int(now) > tick_naluri and tick_subjektif >= float(tick_subjektif_episode):
                rate_now = float(_subjective_time_snapshot(n).get("clock_rate", 1.0))
                return max(0.0, tick_subjektif - float(tick_subjektif_episode)
                           + (int(now) - tick_naluri) * rate_now)
    except (AttributeError, TypeError, ValueError):
        pass
    return age_obj * rate_episode


def _waktu_recency(original, self, episode, now):
    """Half-life per episode terhadap waktu yang benar-benar dialami."""
    try:
        w = getattr(self, "_waktu", None)
        eid = _waktu_episode_id(episode)
        if w is not None and eid is not None:
            hl = w.half_life(eid)
            if hl > 0:
                age = _waktu_umur_subjektif(self, episode, now)
                return 0.5 ** (age / hl)
    except Exception:
        pass
    return original(self, episode, now)


wrap_method(JejakPrediksi, "_recency", _waktu_recency,
            patch_id="jejak.waktu.recency")


def _waktu_retention(original, self, episode, now):
    """Salience tetap; pengurutan eviksi ikut jam dan half-life subjektif."""
    try:
        w = getattr(self, "_waktu", None)
        eid = _waktu_episode_id(episode)
        if w is not None and eid is not None:
            base = original(self, episode, now)
            age = _waktu_umur_subjektif(self, episode, now)
            hl_lama = max(1.0, float(getattr(self, "half_life_ticks", 600.0)) * 2.0)
            hl_baru = max(1.0, w.half_life(eid))
            f_lama = 0.5 ** (age / hl_lama)
            f_baru = 0.5 ** (age / hl_baru)
            if f_lama > 1e-9:
                return base * (f_baru / f_lama)
    except Exception:
        pass
    return original(self, episode, now)


wrap_method(JejakPrediksi, "_retention_score", _waktu_retention,
            patch_id="jejak.waktu.retention")


def _waktu_retrieve(original, self, *a, **k):
    """Setiap episode yang benar-benar terambil memperpanjang half-life-nya."""
    hasil = original(self, *a, **k)
    try:
        w = getattr(self, "_waktu", None)
        if w is not None and hasil:
            for hit in hasil:
                eid = _waktu_episode_id(hit)
                if eid is not None:
                    w.diingat(eid)
    except Exception:
        pass
    return hasil


wrap_method(JejakPrediksi, "_retrieve", _waktu_retrieve,
            patch_id="jejak.waktu.retrieve")


def _jejak_waktu_ambil(self):
    w = getattr(self, "_waktu", None)
    if w is None:
        # Waktu heterogen belum pernah dibuat (belum ada episode yang
        # di-recall / dikoreksi). Tetap kirim payload DEFAULT yang LENGKAP
        # supaya to_dict/from_dict simetris: kalau hanya {} yang dikirim,
        # from_dict akan membuat _waktu dan to_dict berikutnya mengeluarkan
        # payload penuh -> round-trip tidak idempoten.
        try:
            modul = optional_module("pycos.mandiri.organik")
            d = (modul.WaktuHeterogen(
                dasar=float(getattr(self, "half_life_ticks", 600.0))).to_dict()
                 if modul is not None else {})
        except (AttributeError, TypeError, ValueError):
            d = {}
    else:
        d = w.to_dict()
    d["reconsolidasi"] = [dict(x) for x in
                          (getattr(self, "_reconsolidasi_log", None) or [])]
    return d


def _jejak_waktu_pasang(self, d):
    modul = optional_module("pycos.mandiri.organik")
    if modul is None or not isinstance(d, Mapping):
        return
    data = dict(d)
    log = data.pop("reconsolidasi", None)
    try:
        self._waktu = modul.WaktuHeterogen.from_dict(data)
        if isinstance(log, list):
            self._reconsolidasi_log = [dict(x) for x in log
                                       if isinstance(x, Mapping)][-64:]
    except (AttributeError, TypeError, ValueError):
        # Payload versi lama atau modul organik yang tidak kompatibel
        # diabaikan; state inti JEJAK tetap termuat.
        return


# ---------------- 4b. reconsolidasi OTOMATIS ----------------
def _jejak_impact(ep):
    try:
        v = float(ep.get("impact", 0.0) or 0.0)
        if abs(v) > 1e-9:
            return v
        return sum(float(x) for x in (ep.get("drive_deltas") or {}).values())
    except Exception:
        return 0.0


def _reconsolidasi_otomatis(self, eid_baru, ambang_kemiripan=0.5, margin=0.25):
    """Sinyal reconsolidasi otomatis: episode baru vs episode lama.

    Mirip tetapi hasilnya BERBEDA tanda -> ingatan lama dikoreksi salah
    (half-life memendek). Mirip dan hasilnya COCOK -> dikonfirmasi
    (half-life memanjang). Tidak perlu pemanggilan manual lagi.
    """
    w = getattr(self, "_waktu", None)
    if w is None:
        return []
    eps = getattr(self, "_episodes", None) or []
    baru = next((e for e in eps if e.get("id") == eid_baru), None)
    if baru is None:
        return []
    kata_baru = set(str(baru.get("stimulus", "")).lower().split())
    if not kata_baru:
        return []
    hasil = []
    for ep in eps:
        if ep.get("id") == eid_baru:
            continue
        kata = set(str(ep.get("stimulus", "")).lower().split())
        if not kata:
            continue
        sim = len(kata & kata_baru) / float(len(kata | kata_baru) or 1)
        if sim < ambang_kemiripan:
            continue
        i_baru, i_lama = _jejak_impact(baru), _jejak_impact(ep)
        if abs(i_baru - i_lama) <= margin:
            w.diingat(ep["id"])
            jenis = "dikonfirmasi"
        elif (i_baru > 0) != (i_lama > 0):
            w.dikoreksi_salah(ep["id"])
            jenis = "dikoreksi_salah"
        else:
            continue
        hasil.append({"episode": ep["id"], "kemiripan": round(sim, 3),
                      "jenis": jenis, "impact_lama": round(i_lama, 3),
                      "impact_baru": round(i_baru, 3)})
    if hasil:
        log = getattr(self, "_reconsolidasi_log", None)
        if log is None:
            log = []
            self._reconsolidasi_log = log
        log.extend(hasil)
        if len(log) > 64:
            del log[:-64]
    return hasil


def reconsolidasi_state(self):
    w = getattr(self, "_waktu", None)
    return {"log": [dict(x) for x in
                    (getattr(self, "_reconsolidasi_log", None) or [])],
            "waktu": w.ringkas() if w is not None else {}}


def _jejak_record(original, self, *a, **k):
    episode_id = original(self, *a, **k)
    try:
        episode = getattr(self, "_ep_by_id", {}).get(int(episode_id))
        if episode is None:
            episode = next((item for item in getattr(self, "_episodes", [])
                            if int(item.get("id", -1)) == int(episode_id)), None)
        if episode is not None:
            waktu = _jejak_waktu(self)
            waktu.skala_subjektif(
                episode_id,
                faktor=episode.get("subjective_time_scale", 1.0),
                durasi_objektif=episode.get("objective_duration", 1.0),
                durasi_subjektif=episode.get("subjective_duration", 1.0),
                keadaan=episode.get("subjective_time_rasa", "netral"),
            )
        _reconsolidasi_otomatis(self, episode_id)
    except Exception:
        # Integrasi waktu bersifat opsional; kegagalannya tidak boleh
        # menggagalkan pencatatan episode inti.
        pass
    return episode_id


wrap_method(JejakPrediksi, "record_experience", _jejak_record,
            patch_id="jejak.waktu.record")
wrap_method(JejakPrediksi, "experience", _jejak_record,
            patch_id="jejak.waktu.experience")
install_method(JejakPrediksi, "reconsolidasi_state", reconsolidasi_state,
               patch_id="jejak.waktu.api")


def _jejak_serialisasi(original, self, *a, **k):
    data = original(self, *a, **k)
    if isinstance(data, dict):
        data["waktu_heterogen"] = _jejak_waktu_ambil(self)
        mesin = getattr(self, "_mesin_kepercayaan", None)
        if mesin is not None:
            data["kepercayaan"] = mesin.to_dict()
    return data


def _jejak_deserialisasi(original, cls, data, *a, **k):
    jejak = original(cls, data, *a, **k)
    if not isinstance(data, Mapping):
        return jejak
    waktu = data.get("waktu_heterogen")
    if waktu:
        _jejak_waktu_pasang(jejak, waktu)
    kepercayaan = data.get("kepercayaan")
    if kepercayaan:
        try:
            modul = optional_module("pycos.mandiri.kognisi_lanjut")
            if modul is not None:
                jejak._mesin_kepercayaan = modul.MesinKepercayaan.from_dict(
                    kepercayaan)
        except (AttributeError, TypeError, ValueError):
            pass
    return jejak


wrap_method(JejakPrediksi, "to_dict", _jejak_serialisasi,
            patch_id="jejak.integrasi.serialisasi")
wrap_method(JejakPrediksi, "from_dict", _jejak_deserialisasi,
            patch_id="jejak.integrasi.deserialisasi")
# >>> ORGANIK-BLOCK-END (jejak) <<<


# ===========================================================================
# INTEGRASI: MESIN KEPERCAYAAN BAYESIAN (prior → posterior)
# JejakPrediksi tidak sekadar mencatat log; ia memelihara P(H|E).
# ===========================================================================
def _jejak_mesin(self):
    """Ambil mesin kepercayaan secara malas tanpa mengikat impor wajib."""
    m = getattr(self, "_mesin_kepercayaan", None)
    if m is None:
        modul = optional_module("pycos.mandiri.kognisi_lanjut")
        if modul is None:
            return None
        m = modul.MesinKepercayaan()
        self._mesin_kepercayaan = m
    return m


def _jejak_tetapkan_kepercayaan(self, hipotesis, p):
    m = _jejak_mesin(self)
    return m.tetapkan(hipotesis, p) if m else float(p)


def _jejak_perbarui_kepercayaan(self, hipotesis, likelihood_ratio,
                                bobot=1.0, label=""):
    m = _jejak_mesin(self)
    if m is None:
        return 0.5
    return m.perbarui(hipotesis, likelihood_ratio, bobot, label)


def _jejak_kepercayaan(self, hipotesis):
    m = _jejak_mesin(self)
    return m.kepercayaan(hipotesis) if m else 0.5


def _jejak_curiga(self, hipotesis, ambang=None):
    """Curiga bila posterior < ambang (dinamis, dari Nurani bila tersedia)."""
    m = _jejak_mesin(self)
    if m is None:
        return False
    if ambang is None:
        nur = getattr(self, "nurani", None)
        fn = getattr(nur, "ambang_kecurigaan", None)
        if callable(fn):
            try:
                ambang = float(fn())
            except Exception:
                ambang = None
    return m.curiga(hipotesis, ambang)


def _jejak_kepercayaan_state(self):
    m = getattr(self, "_mesin_kepercayaan", None)
    return m.to_dict() if m is not None else {}


def _jejak_pasang(self):
    """Kompatibilitas: siapkan mesin per-instance tanpa mengubah kelas."""
    return self._jejak_mesin() is not None


install_methods(
    JejakPrediksi,
    (("tetapkan_kepercayaan", _jejak_tetapkan_kepercayaan),
     ("perbarui_kepercayaan", _jejak_perbarui_kepercayaan),
     ("kepercayaan", _jejak_kepercayaan),
     ("curiga", _jejak_curiga),
     ("kepercayaan_state", _jejak_kepercayaan_state),
     ("_jejak_mesin", _jejak_mesin),
     ("_pasang_bayes", _jejak_pasang)),
    patch_id="jejak.kepercayaan.api",
)


if __name__ == "__main__":
    demo()
