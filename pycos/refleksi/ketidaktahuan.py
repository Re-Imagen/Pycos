# -*- coding: utf-8 -*-
"""View reflektif atas batas pengetahuan NPC (read-only, tanpa state baru).

``batas_pengetahuan(npc, proposisi)`` membaca lima wadah yang telah ada:
Jejak episodik, memori afektif Nurani, tepi kausal, model keyakinan sosial,
dan spotlight Kesadaran. Ia tidak menilai kebenaran atau kecukupan untuk tugas.

``sikap_ketidaktahuan(npc, batas, konteks=None)`` menghitung sikap saat ini
dari bentuk ketidaktahuan, watak yang sudah ada, dan konteks pemanggil. Hasil
sikap tidak pernah ditulis kembali ke NPC. Keduanya dapat dipanggil terhadap
NPC yang baru lahir atau objek yang hanya memiliki sebagian lapisan.
"""
from __future__ import annotations

import math
import re
import zlib
from collections.abc import Mapping, Sequence
from itertools import islice
from typing import Any, Dict, List, Optional, Tuple

from pycos.dukungan.numerik import jepit, jepit_01

__all__ = [
    "STATUS_PENGETAHUAN", "SIKAP_KETIDAKTAHUAN",
    "batas_pengetahuan", "sikap_ketidaktahuan",
]

STATUS_PENGETAHUAN: Tuple[str, ...] = (
    "tahu", "merasa tahu", "tidak tahu", "tidak bisa tahu",
)
SIKAP_KETIDAKTAHUAN: Tuple[str, ...] = (
    "waspada", "malu", "marah", "kekanak", "tenang", "bertanya", "diam",
)

from pycos.dukungan import konstanta as _konstanta_drive
_DRIVES = _konstanta_drive.DRIVES
_TOKEN_RE = re.compile(r"[a-z0-9]+", re.IGNORECASE)
_AFFECTIVE_WORD_RE = re.compile(r"[a-z]{4,}")
_STOP_WORDS = frozenset((
    "yang", "dan", "atau", "di", "ke", "dari", "dengan", "untuk", "pada",
    "dalam", "itu", "ini", "saat", "ketika", "oleh", "karena", "sebuah",
    "ada", "pernah", "aku", "saya", "tahu", "merasa", "mengetahui",
    "menyadari", "bisa", "akan", "lebih",
    "the", "and", "or", "at", "to", "from", "with", "for", "in", "on",
    "when", "while", "after", "before", "this", "that", "there", "was", "were",
    "is", "are", "it", "its", "a", "an", "of", "by", "as",
))
_EPISODIC_ALIASES = {
    "fire": "api", "fires": "api", "flame": "api", "flames": "api",
    "bonfire": "api", "bara": "api", "kebakaran": "api",
    "burn": "bakar", "burns": "bakar", "burned": "bakar",
    "burning": "bakar", "membakar": "bakar", "terbakar": "bakar",
    "dibakar": "bakar", "heat": "panas", "hot": "panas",
    "smoke": "asap", "danger": "bahaya", "dangerous": "bahaya",
    "berbahaya": "bahaya", "threat": "ancaman", "risk": "risiko",
    "risky": "risiko", "berisiko": "risiko", "unsafe": "tidakaman",
    "safe": "aman", "approach": "paparan", "approaching": "paparan",
    "mendekat": "paparan", "mendekati": "paparan", "dekat": "paparan",
    "touch": "paparan", "touching": "paparan", "sentuh": "paparan",
    "menyentuh": "paparan", "pegang": "paparan", "memegang": "paparan",
    "handle": "paparan", "grab": "paparan", "avoid": "hindar",
    "avoiding": "hindar", "hindari": "hindar", "menghindari": "hindar",
    "menghindar": "hindar", "menjauh": "hindar", "menjauhi": "hindar",
    "mundur": "hindar", "retreat": "hindar", "flee": "hindar",
    "observe": "amati", "observing": "amati", "inspect": "amati",
    "watch": "amati", "mengamati": "amati", "periksa": "amati",
    "melihat": "lihat",
}


def _field(obj: Any, name: str, default: Any = None) -> Any:
    """Baca atribut instance langsung, tanpa memanggil method/property."""
    try:
        if isinstance(obj, Mapping):
            return obj.get(name, default)
        instance_dict = object.__getattribute__(obj, "__dict__")
        if isinstance(instance_dict, dict):
            return instance_dict.get(name, default)
    except Exception:
        pass
    return default


def _get(mapping: Any, key: Any, default: Any = None) -> Any:
    try:
        return mapping.get(key, default) if isinstance(mapping, Mapping) else default
    except Exception:
        return default


def _text(value: Any) -> str:
    # Hindari __str__ pada objek asing: implementasi pengguna dapat punya efek.
    if isinstance(value, str):
        return value[:512]
    if value is None:
        return ""
    if isinstance(value, (int, float, bool)):
        try:
            return str(value)[:512]
        except Exception:
            return ""
    return ""


def _proposition(proposisi: Any) -> Tuple[str, Any]:
    if isinstance(proposisi, str):
        return proposisi[:512], proposisi
    if isinstance(proposisi, Mapping):
        for key in ("teks", "text", "content", "proposition", "proposisi",
                    "claim", "statement", "isi"):
            value = _get(proposisi, key)
            if value is not None:
                return _text(value), proposisi
        return "", proposisi
    # Dataclass/record sederhana diterima melalui __dict__, tanpa memanggil API.
    for key in ("teks", "text", "content", "proposition", "proposisi", "claim"):
        value = _field(proposisi, key)
        if value is not None:
            return _text(value), proposisi
    return "", proposisi


def _unreachable(proposisi: Any) -> bool:
    """Jangkauan adalah input eksplisit dari host, bukan fakta yang ditebak."""
    if not isinstance(proposisi, Mapping):
        return False
    for key in ("out_of_reach", "unreachable", "tidak_terjangkau"):
        value = _get(proposisi, key)
        if value is True:
            return True
    for key in ("reachable", "dapat_diketahui", "terjangkau"):
        value = _get(proposisi, key)
        if value is False:
            return True
    scope = _get(proposisi, "jangkauan")
    if scope is False:
        return True
    text = _text(scope).strip().lower().replace(" ", "_")
    return text in {
        "di_luar", "luar", "di_luar_jangkauan", "tidak_terjangkau",
        "tak_terjangkau", "mustahil_diketahui", "tidak_bisa_diketahui",
    }


def _tokens(text: Any, maksimum: int = 24) -> Tuple[str, ...]:
    raw = _text(text).lower()
    out: List[str] = []
    seen = set()
    # Teks dipotong sebelum regex; jumlah kata dan ukuran traversal selalu kecil.
    for token in _TOKEN_RE.findall(raw)[:64]:
        if token in _STOP_WORDS or token in seen or len(token) < 2:
            continue
        seen.add(token)
        out.append(token)
        if len(out) >= maksimum:
            break
    return tuple(out)


def _clip(value: Any, default: float = 0.0) -> float:
    try:
        if isinstance(value, bool):
            return default
        result = float(value)
        if not math.isfinite(result):
            return default
        return jepit_01(result)
    except (TypeError, ValueError, OverflowError):
        return default


def _coverage(query: Tuple[str, ...], evidence_text: Any) -> float:
    if not query:
        return 0.0
    tokens = set(_tokens(evidence_text, maksimum=48))
    if not tokens:
        return 0.0
    return len(set(query).intersection(tokens)) / float(len(set(query)))


def _episode_coverage(query: Tuple[str, ...], evidence_text: Any) -> float:
    """Cakupan dengan alias yang sama seperti indeks token Jejak."""
    canonical_query = {_EPISODIC_ALIASES.get(token, token) for token in query}
    evidence = {_EPISODIC_ALIASES.get(token, token)
                for token in _tokens(evidence_text, maksimum=48)}
    if not canonical_query or not evidence:
        return 0.0
    return len(canonical_query.intersection(evidence)) / float(len(canonical_query))


def _wadah(ada: bool = False, kekuatan: float = 0.0,
           bukti: Optional[Mapping[str, Any]] = None,
           ambang: float = 0.25) -> Dict[str, Any]:
    score = _clip(kekuatan)
    if not ada:
        status = "tidak_ada"
    elif score >= ambang:
        status = "cukup"
    else:
        status = "lemah"
    return {
        "status": status,
        "ada": bool(ada),
        "kekuatan": round(score, 4),
        "bukti": dict(bukti or {}),
    }


def _episodik(npc: Any, query: Tuple[str, ...]) -> Dict[str, Any]:
    """Cari kandidat melalui indeks Jejak, bukan scan seluruh episode."""
    memory = _field(npc, "jejak")
    if memory is None:
        presentasi = _field(npc, "presentasi")
        memory = _field(presentasi, "jejak")
    if memory is None or not query:
        return {"ada": False, "kekuatan": 0.0, "bukti": {}}
    index = _field(memory, "_token_index")
    episode_by_id = _field(memory, "_ep_by_id")
    if not isinstance(index, Mapping) or not isinstance(episode_by_id, Mapping):
        return {"ada": False, "kekuatan": 0.0, "bukti": {}}

    ids = set()
    index_query = tuple(dict.fromkeys(
        _EPISODIC_ALIASES.get(token, token) for token in query))
    try:
        for token in index_query:
            bucket = _get(index, token, ())
            if isinstance(bucket, Mapping):
                bucket = bucket.keys()
            if not isinstance(bucket, Sequence) and not isinstance(bucket, (set, frozenset)):
                continue
            for episode_id in islice(iter(bucket), 48):
                ids.add(episode_id)
                if len(ids) >= 96:
                    break
            if len(ids) >= 96:
                break
    except Exception:
        return {"ada": False, "kekuatan": 0.0, "bukti": {}}

    best = 0.0
    best_evidence: Dict[str, Any] = {}
    for episode_id in ids:
        episode = _get(episode_by_id, episode_id)
        if not isinstance(episode, Mapping):
            continue
        text = " ".join(_text(_get(episode, key, ""))[:180]
                         for key in ("stimulus", "context", "action", "label"))
        coverage = _episode_coverage(query, text)
        minimum_coverage = 0.60 if len(set(query)) > 1 else 0.50
        if coverage < minimum_coverage:
            continue
        importance = _clip(_get(episode, "importance", 1.0), default=0.5)
        count = _get(episode, "count", 1)
        try:
            repetition = min(1.0, max(0.0, float(count)) / 3.0)
        except (TypeError, ValueError, OverflowError):
            repetition = 0.0
        score = coverage * (0.70 + 0.30 * importance) * (0.90 + 0.10 * repetition)
        if score > best:
            best = score
            best_evidence = {
                "episode_id": episode_id,
                "coverage": round(coverage, 4),
                "stimulus": _text(_get(episode, "stimulus", ""))[:80],
            }
    return {"ada": best > 0.0, "kekuatan": best, "bukti": best_evidence}


def _affective_signature(text: Any) -> Optional[int]:
    # Identik dengan Nurani.keywords/context_signature, tetapi dihitung lokal:
    # context_signature mengisi cache dan karena itu tidak boleh dipanggil.
    # Nurani.keywords adalah fungsi murni atas isi teks (tanpa menyentuh
    # _sig_cache); signature = crc32 atas lema tergabung persis seperti
    # context_signature, sehingga slot tersimpan selalu cocok.
    try:
        from pycos.refleksi.nurani import Nurani
        keywords = Nurani.keywords(_text(text))
    except Exception:
        words = set(_AFFECTIVE_WORD_RE.findall(_text(text).lower()))
        if not words:
            return None
        keywords = tuple(sorted(words)[:8])
    if not keywords:
        return None
    return zlib.crc32("|".join(keywords).encode("utf-8")) & 0xFFFFFFFF


def _afektif(npc: Any, text: str) -> Dict[str, Any]:
    nurani = _field(npc, "nurani")
    affective = _field(nurani, "_affective")
    signature = _affective_signature(text)
    if not isinstance(affective, Mapping) or signature is None:
        return {"ada": False, "kekuatan": 0.0, "bukti": {}}
    slot = _get(affective, signature)
    if slot is None:
        slot = _get(affective, str(signature))
    if not isinstance(slot, Mapping):
        return {"ada": False, "kekuatan": 0.0, "bukti": {}}
    sample = _text(_get(slot, "sample", ""))
    # Nurani memang menyimpan cuplikan maksimum 60 karakter; cuplikan penuh
    # tidak cukup untuk membuktikan bahwa signature konteksnya berbeda.
    if sample and len(sample) < 60 and _affective_signature(sample) != signature:
        return {"ada": False, "kekuatan": 0.0, "bukti": {}}

    deltas = _get(slot, "deltas", {})
    impact = 0.0
    if isinstance(deltas, Mapping):
        for drive in _DRIVES:
            impact = max(impact, _clip(abs(_get(deltas, drive, 0.0))))
    impact = max(impact, _clip(_get(slot, "importance", 0.0)))
    try:
        samples = min(1.0, max(0.0, float(_get(slot, "n", 0))) / 3.0)
    except (TypeError, ValueError, OverflowError):
        samples = 0.0
    score = 0.70 * impact + 0.30 * samples
    return {
        "ada": True,
        "kekuatan": score,
        "bukti": {"signature": signature, "sample": sample[:64]},
    }


def _is_causal_edge(source: str, target: str) -> float:
    # Korelasi situasi→hasil tidak dihitung sebagai penjelasan sebab.
    if source.startswith("a:") and target.startswith(("h:", "d:")):
        return 1.0
    if source.startswith("s:") and target.startswith("a:"):
        return 0.85
    return 0.0


def _kausal(npc: Any, text: str, query: Tuple[str, ...]) -> Dict[str, Any]:
    organic = _field(npc, "_organik")
    model = _field(organic, "kausal") if organic is not None else None
    if model is None:
        model = _field(npc, "kausal")
    edges = _field(model, "tepi")
    incoming = _field(model, "masuk")
    outgoing = _field(model, "keluar")
    if not isinstance(edges, Mapping) or not query:
        return {"ada": False, "kekuatan": 0.0, "bukti": {}}

    normalized = " ".join(_TOKEN_RE.findall(_text(text).lower())[:24])
    nodes: List[str] = []
    supplied = _text(text).strip().lower()
    if supplied[:2] in ("s:", "a:", "h:", "d:"):
        nodes.append(supplied[:120])
    for prefix in ("s:", "a:", "h:", "d:"):
        if normalized:
            nodes.append(prefix + normalized[:96])
    for token in query[:12]:
        nodes.extend(("s:" + token, "a:" + token, "h:" + token, "d:" + token))
    unique_nodes = tuple(dict.fromkeys(nodes))[:52]

    best = 0.0
    best_evidence: Dict[str, Any] = {}
    for node in unique_nodes:
        incoming_nodes = _get(incoming, node, {})
        outgoing_nodes = _get(outgoing, node, {})
        pairs: List[Tuple[str, str]] = []
        if isinstance(incoming_nodes, Mapping):
            pairs.extend((_text(source), node) for source in islice(incoming_nodes, 12))
        if isinstance(outgoing_nodes, Mapping):
            pairs.extend((node, _text(target)) for target in islice(outgoing_nodes, 12))
        for source, target in pairs:
            causal_weight = _is_causal_edge(source, target)
            if causal_weight <= 0.0:
                continue
            edge = _get(edges, (source, target))
            if not isinstance(edge, Mapping):
                continue
            weight = _clip(_get(edge, "kuat", 0.0)) * causal_weight
            if weight > best:
                best = weight
                best_evidence = {
                    "sebab": source[:96], "akibat": target[:96],
                    "jenis": "mekanisme" if causal_weight == 1.0 else "pemicu",
                }
    return {"ada": best > 0.0, "kekuatan": best, "bukti": best_evidence}


def _sosial(proposisi: Any, text: str) -> Dict[str, Any]:
    if not isinstance(proposisi, Mapping):
        return {"ada": False, "kekuatan": 0.0, "bukti": {}}
    holder = None
    for key in ("pemegang", "holder", "orang", "entitas", "other", "other_id"):
        holder = _get(proposisi, key)
        if _text(holder).strip():
            break
        holder = None
    drive = None
    for key in ("drive", "drive_key", "keyakinan_drive"):
        candidate = _get(proposisi, key)
        if isinstance(candidate, str) and candidate in _DRIVES:
            drive = candidate
            break
    if drive is None:
        drive = next((d for d in _DRIVES if d in set(_tokens(text, maksimum=32))), None)
    if holder is None or drive is None:
        return {"ada": False, "kekuatan": 0.0, "bukti": {}}
    # NPC diberikan terpisah ke fungsi ini setelah slot Nurani dibaca oleh
    # pemanggil; metadata di bawah diisi oleh batas_pengetahuan.
    return {"ada": True, "holder": _text(holder), "drive": drive}


def _bukti_sosial(npc: Any, proposisi: Any, text: str) -> Dict[str, Any]:
    query = _sosial(proposisi, text)
    if not query.get("ada"):
        return {"ada": False, "kekuatan": 0.0, "bukti": {}}
    nurani = _field(npc, "nurani")
    beliefs = _field(nurani, "_other_beliefs")
    if not isinstance(beliefs, Mapping):
        return {"ada": False, "kekuatan": 0.0, "bukti": {}}
    holder_map = _get(beliefs, query["holder"])
    if not isinstance(holder_map, Mapping):
        return {"ada": False, "kekuatan": 0.0, "bukti": {}}
    slot = _get(holder_map, query["drive"])
    if not isinstance(slot, Mapping):
        return {"ada": False, "kekuatan": 0.0, "bukti": {}}
    confidence = _clip(_get(slot, "confidence", 0.0))
    return {
        "ada": True,
        "kekuatan": confidence,
        "bukti": {"pemegang": query["holder"], "drive": query["drive"]},
    }


def _sadar(npc: Any, query: Tuple[str, ...]) -> Dict[str, Any]:
    kesadaran = _field(npc, "kesadaran")
    spotlight = _field(kesadaran, "spotlight")
    if not isinstance(spotlight, Sequence) or isinstance(spotlight, (str, bytes)):
        return {"ada": False, "kekuatan": 0.0, "bukti": {}}
    best = 0.0
    best_evidence: Dict[str, Any] = {}
    for item in islice(spotlight, 3):
        if not isinstance(item, Mapping):
            continue
        content = _text(_get(item, "content", _get(item, "teks", "")))
        coverage = _coverage(query, content)
        if coverage < 0.50:
            continue
        strength = max(_clip(_get(item, "attention", 0.0)),
                       _clip(_get(item, "salience", 0.0))) * coverage
        if strength > best:
            best = strength
            best_evidence = {"content": content[:80], "coverage": round(coverage, 4)}
    return {"ada": best > 0.0, "kekuatan": best, "bukti": best_evidence}


def batas_pengetahuan(npc: Any, proposisi: Any,
                      ambang_kekuatan: float = 0.25) -> Dict[str, Any]:
    """Laporkan di mana proposisi hadir dan bentuk batas pengetahuan NPC.

    Proposisi boleh berupa string atau mapping. Mapping juga dapat menyertakan
    ``jangkauan='di_luar_jangkauan'`` (atau ``reachable=False``) dari host, dan
    metadata sosial ``pemegang``/``drive``. Tanpa penanda jangkauan eksplisit,
    fungsi tidak menebak bahwa sesuatu mustahil diketahui.

    Ambang ini hanya ambang kekuatan epistemik view, bukan ukuran apakah
    pengetahuan cukup untuk tujuan aplikasi. Pengembalian tidak menyimpan apa
    pun ke NPC; Jejak episodik dicari melalui indeks terbalik yang sudah ada
    (maksimal 96 kandidat), sementara spotlight dibatasi tiga item.
    """
    try:
        try:
            threshold = float(ambang_kekuatan)
            if not math.isfinite(threshold):
                threshold = 0.25
            threshold = jepit_01(threshold)
        except (TypeError, ValueError, OverflowError):
            threshold = 0.25
        text, source = _proposition(proposisi)
        query = _tokens(text)

        episodic = _episodik(npc, query)
        affective = _afektif(npc, text)
        causal = _kausal(npc, text, query)
        social = _bukti_sosial(npc, source, text)
        conscious = _sadar(npc, query)

        vessels = {
            "episodik": _wadah(episodic.get("ada", False),
                               episodic.get("kekuatan", 0.0),
                               episodic.get("bukti"), threshold),
            "afektif": _wadah(affective.get("ada", False),
                              affective.get("kekuatan", 0.0),
                              affective.get("bukti"), threshold),
            "kausal": _wadah(causal.get("ada", False),
                             causal.get("kekuatan", 0.0),
                             causal.get("bukti"), threshold),
            "sosial": _wadah(social.get("ada", False),
                             social.get("kekuatan", 0.0),
                             social.get("bukti"), threshold),
            "sadar": _wadah(conscious.get("ada", False),
                            conscious.get("kekuatan", 0.0),
                            conscious.get("bukti"), threshold),
        }
        enough = tuple(name for name, value in vessels.items()
                       if value["status"] == "cukup")
        grounded = any(vessels[name]["status"] == "cukup"
                       for name in ("episodik", "kausal", "sosial"))
        max_strength = max((v["kekuatan"] for v in vessels.values()), default=0.0)
        if _unreachable(source):
            conclusion = "tidak bisa tahu"
        elif grounded:
            conclusion = "tahu"
        elif vessels["afektif"]["status"] == "cukup":
            # Rasa yakin afektif tanpa episode/kausal/sosial bukan landasan
            # eksternal. Spotlight saja menandai atensi, bukan pengetahuan.
            conclusion = "merasa tahu"
        else:
            conclusion = "tidak tahu"
        return {
            "proposisi": text,
            "wadah": vessels,
            "kesimpulan": conclusion,
            "status": conclusion,
            "dalam_jangkauan": not _unreachable(source),
            "kekuatan_maks": round(max_strength, 4),
            "ambang_kekuatan": round(threshold, 4),
            "wadah_kuat": enough,
        }
    except Exception:
        # Objek setengah jadi atau wadah rusak tetap dapat ditanyakan.
        empty = {name: _wadah() for name in
                 ("episodik", "afektif", "kausal", "sosial", "sadar")}
        text, source = _proposition(proposisi)
        unreachable = _unreachable(source)
        conclusion = "tidak bisa tahu" if unreachable else "tidak tahu"
        return {
            "proposisi": text, "wadah": empty, "kesimpulan": conclusion,
            "status": conclusion, "dalam_jangkauan": not unreachable,
            "kekuatan_maks": 0.0, "ambang_kekuatan": 0.25,
            "wadah_kuat": (),
        }


def _trait(explicit: Any, names: Tuple[str, ...], default: float = 0.0) -> float:
    if isinstance(explicit, Mapping):
        for name in names:
            value = _get(explicit, name)
            if value is not None:
                if isinstance(value, bool):
                    return 1.0 if value else 0.0
                return _clip(value, default=default)
    return default


def _drive_or_emotion(mapping: Any, names: Tuple[str, ...]) -> float:
    if not isinstance(mapping, Mapping):
        return 0.0
    return max((_clip(_get(mapping, key, 0.0)) for key in names), default=0.0)


def _internal_urgency(mapping: Any) -> float:
    if not isinstance(mapping, Mapping):
        return 0.0
    maximum = 0.0
    for drive in _DRIVES:
        try:
            value = float(_get(mapping, drive, 0.0) or 0.0)
            if math.isfinite(value):
                maximum = max(maximum, jepit(value, 0.0, 2.5))
        except (TypeError, ValueError, OverflowError):
            continue
    return maximum / 2.5


def _context_number(context: Any, names: Tuple[str, ...]) -> Optional[float]:
    if not isinstance(context, Mapping):
        return None
    for name in names:
        value = _get(context, name)
        if value is None:
            continue
        try:
            number = float(value)
            if math.isfinite(number):
                return jepit(number, 0.0, 2.5)
        except (TypeError, ValueError, OverflowError):
            continue
    return None


def sikap_ketidaktahuan(npc: Any, batas: Any,
                        konteks: Optional[Mapping[str, Any]] = None) -> str:
    """Hitung satu sikap saat ini: waspada/malu/marah/kekanak/tenang/
    bertanya/diam.

    ``konteks`` boleh memberi ``publik``, ``urgensi`` (0..1 atau 0..2.5),
    ``pengamat``, dan ``watak``/``traits`` tanpa menyimpannya ke NPC. Watak
    bawaan dibaca dari kepribadian, emosi, drive, dan parameter yang sudah ada.
    Urutan prioritas sengaja eksplisit agar pengguna dapat menguji respons
    tanpa memanggil method yang mengubah state.
    """
    try:
        context = konteks if isinstance(konteks, Mapping) else {}
        conclusion = _get(batas, "kesimpulan", _get(batas, "status", "tidak tahu"))
        if conclusion not in STATUS_PENGETAHUAN:
            conclusion = "tidak tahu"

        personality = " ".join((
            _text(_field(npc, "personality_name", "")),
            _text(_field(npc, "personality", "")),
            _text(_field(npc, "watak", "")),
        )).lower()
        explicit_traits = _get(context, "watak", _get(context, "traits", {}))
        if isinstance(explicit_traits, str):
            personality += " " + explicit_traits.lower()
            explicit_traits = {}
        elif not isinstance(explicit_traits, Mapping):
            explicit_traits = {}

        paranoid = _trait(explicit_traits, ("paranoid", "paranoid_level"),
                          0.75 if any(x in personality for x in
                                      ("paranoid", "curiga", "waspada")) else
                          0.55 if "penjaga" in personality else 0.0)
        curiosity_trait = _trait(
            explicit_traits, ("penasaran", "curious", "curiosity"),
            0.80 if "penjelajah" in personality else
            0.65 if "cendekia" in personality else 0.0)
        shy = _trait(explicit_traits, ("pemalu", "shy", "malu"),
                     0.65 if any(x in personality for x in ("pemalu", "pendiam")) else 0.0)
        angry_trait = _trait(explicit_traits, ("pemarah", "anger_prone"),
                             0.55 if any(x in personality for x in
                                         ("pemarah", "agresif")) else 0.0)
        child_trait = _trait(explicit_traits, ("kekanak", "childlike"),
                             0.75 if _field(npc, "stage") == "anak" or
                             any(x in personality for x in ("kekanak", "child")) else 0.0)
        calm_trait = _trait(explicit_traits, ("tenang", "calm"),
                            0.70 if any(x in personality for x in ("tenang", "seimbang")) else
                            0.55 if "cendekia" in personality else 0.0)
        silent_trait = _trait(explicit_traits, ("pendiam", "silent", "diam"),
                              0.70 if any(x in personality for x in
                                          ("pendiam", "introvert")) else 0.0)

        emotions = _field(npc, "emosi")
        levels = _field(npc, "levels")
        urgency_state = _field(npc, "urgency")
        kesadaran = _field(npc, "kesadaran")
        epistemic = _field(kesadaran, "epistemic_emotions")
        moral = _field(kesadaran, "moral")
        params = _field(npc, "params")

        fear = max(_drive_or_emotion(emotions, ("takut", "fear")),
                   _clip(-float(_get(levels, "keamanan", 0.0) or 0.0) * 0.60)
                   if isinstance(levels, Mapping) else 0.0)
        anger = max(angry_trait,
                    _drive_or_emotion(emotions, ("marah", "anger")))
        shame = max(shy,
                    _drive_or_emotion(epistemic, ("malu_tidak_tahu", "malu")),
                    _drive_or_emotion(moral, ("malu", "shame")))
        curiosity = max(
            curiosity_trait,
            _drive_or_emotion(emotions, ("penasaran", "curiosity")),
            _drive_or_emotion(epistemic, ("penasaran", "curiosity")),
            _clip(-float(_get(levels, "keingintahuan", 0.0) or 0.0) * 0.60)
            if isinstance(levels, Mapping) else 0.0,
        )
        explicit_urgency = _context_number(context, ("urgensi", "urgency"))
        if explicit_urgency is None:
            explicit_urgency = _internal_urgency(urgency_state)
        urgency = explicit_urgency / 2.5 if explicit_urgency > 1.0 else explicit_urgency
        curiosity = max(curiosity, min(1.0, urgency * 0.55))

        observer = _get(context, "pengamat", _get(context, "observer"))
        public_value = _get(context, "publik", _get(context, "public"))
        is_public = bool(observer is not None) if public_value is None else bool(public_value)
        trusted = False
        relation = ""
        if isinstance(observer, Mapping):
            trusted = bool(_get(observer, "tepercaya", _get(observer, "trusted", False)))
            relation = _text(_get(observer, "relasi", _get(observer, "relation", ""))).lower()
        elif observer is not None:
            relation = _text(observer).lower()
        if trusted or relation in ("percaya", "akrab", "teman", "trusted", "friend"):
            is_public = False if public_value is None else is_public
        public_pressure = 1.0 if is_public else 0.0
        if is_public and not trusted:
            shame = max(shame, shy * 0.75)

        if conclusion == "tahu":
            if anger >= 0.72:
                return "marah"
            return "tenang"
        if conclusion == "tidak bisa tahu":
            if is_public and paranoid >= 0.55:
                return "waspada"
            if anger >= 0.62:
                return "marah"
            if curiosity >= 0.62 and urgency >= 0.35:
                return "bertanya"
            if calm_trait >= 0.45 or (fear < 0.35 and not is_public):
                return "tenang"
            return "waspada"
        if conclusion == "merasa tahu":
            if is_public and paranoid >= 0.55:
                return "waspada"
            if anger >= 0.62:
                return "marah"
            if is_public and shame >= 0.45:
                return "malu"
            doubt = max(_clip(_field(_field(npc, "nurani"), "doubt_level", 0.0)),
                        _clip(_field(kesadaran, "doubt", 0.0)))
            if doubt >= 0.55 or curiosity >= 0.70:
                return "bertanya"
            return "tenang"

        # Tidak tahu: publik + paranoid memberi ancaman sosial yang lebih kuat;
        # di ruang privat, paranoia saja tidak memaksa reaksi ancaman.
        if is_public and paranoid >= 0.55:
            return "waspada"
        if anger >= 0.58:
            return "marah"
        if is_public and (shame >= 0.38 or shy >= 0.55):
            return "malu"
        if child_trait >= 0.55:
            return "kekanak"
        if curiosity * 0.55 + urgency * 0.45 >= 0.42:
            return "bertanya"
        silence_probability = _clip(_get(params, "presentasi_bisukan", 0.0))
        if silent_trait >= 0.60 or silence_probability >= 0.70:
            return "diam"
        if fear >= 0.55 or (paranoid >= 0.65 and urgency >= 0.45):
            return "waspada"
        if calm_trait >= 0.45 or fear < 0.35:
            return "tenang"
        if public_pressure:
            return "malu"
        return "waspada"
    except Exception:
        # Terima objek setengah jadi, tapi tetap jaga himpunan hasil kontrak.
        return "tenang"
