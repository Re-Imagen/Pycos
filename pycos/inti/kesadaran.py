"""Implementasi Kesadaran; jalur publik lama tetap inti.naluri."""
from __future__ import annotations

import copy
import math
import random
import re
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple
from pycos.dukungan import diagnostik as _diag
from pycos.dukungan.numerik import jepit, jepit_01
from pycos.inti._konfigurasi import (DRIVES, EMOSI_ALIASES, EPISTEMIC_ALIASES, EPISTEMIC_EMOTIONS, FELT_STATES, KESADARAN_DEFAULTS, MORAL_ALIASES, MORAL_EMOTIONS, REALITY_SOURCES, SELF_BIASES, _MAKS_LOSSES, _kclip)

def _pertanyaan_balik(teks: str, pembicara: str) -> str:
    """Pertanyaan balik dari ISI ujaran lawan (E9).

    Jenis pertanyaan (D6) + topik (D7) membentuk kalimat balik yang berbeda
    tiap jenis, alih-alih satu template tetap.
    """
    nama = str(pembicara or "kamu").strip() or "kamu"
    s = str(teks or "").strip()
    jenis = ""
    topik = ""
    try:
        from pycos.bahasa.teks import jenis_pertanyaan, ekstrak_topik
        jp = jenis_pertanyaan(s) or {}
        jenis = str(jp.get("jenis") or "").strip().lower()
        topik = str(ekstrak_topik(s) or "").strip()
    except Exception as _galat_diagnostik_131:
        _diag.catat('naluri.Kesadaran._pertanyaan_balik',
                    "galat pada jalur fallback",
                    galat=_galat_diagnostik_131, jalur=131)
        jenis, topik = "", ""
    if jenis == "siapa":
        return f"siapa yang kamu pikir, {nama}?"
    if jenis == "kapan":
        return f"kapan menurutmu paling pas, {nama}?"
    if jenis in ("di mana", "dimana"):
        return f"kamu mau tahu posisinya di mana, {nama}?"
    if jenis == "kenapa":
        return f"kenapa itu yang kamu tanyakan, {nama}?"
    if jenis == "bagaimana":
        return f"menurut kamu sendiri bagaimana, {nama}?"
    if jenis == "berapa":
        return f"kamu kira berapa, {nama}?"
    if topik:
        return f"kenapa {topik} yang kamu tanyakan, {nama}?"
    return f"kenapa kamu bertanya begitu, {nama}?"


class Kesadaran:
    """Lapisan kesadaran naratif untuk satu `Naluri`.

    Alih-alih reaksi tersebar, NPC menyaring kandidat konten menjadi
    ``attention_spotlight`` (1–3/tick); kandidat terkuat memicu ``ignition``
    (broadcast global) sehingga dapat dilaporkan, diingat, dan memengaruhi
    keputusan. Di atas mekanisme itu dibangun monolog batin, diri
    autobiografis, rasa agensi, interosepsi afektif, monitoring realitas,
    kognisi sosial orang-kedua, pragmatik dialog, bias/self-deception, nilai,
    mortalitas, dan kontinuitas mimpi.
    """

    # ==================================================================
    # konstruksi & sakelar
    # ==================================================================
    def __init__(self, naluri: Any, params: Optional[Dict[str, Any]] = None) -> None:
        self.naluri = naluri
        # params adalah dict MILIK Naluri (satu sumber kebenaran); fallback
        # deep-copy agar pemakaian berdiri sendiri tetap aman.
        self.params: Dict[str, Any] = (params if params is not None
                                       else copy.deepcopy(KESADARAN_DEFAULTS))
        self._rng = getattr(naluri, "_rng", None) or random.Random(0)

        # --- 1) GLOBAL WORKSPACE & ACCESS ---
        self.workspace: List[Dict[str, Any]] = []      # konten sadar saat ini
        self.spotlight: List[Dict[str, Any]] = []       # 1–3 terpilih tick ini
        self.ignitions: List[Dict[str, Any]] = []
        self._ignition_count: int = 0
        self._last_ignition_tick: int = -10_000
        self._broadcast: List[Dict[str, Any]] = []      # isi yang disiarkan

        # --- 2) INNER SPEECH / NARASI ORANG-PERTAMA ---
        self.self_talk: List[Dict[str, Any]] = []
        self.narrative_identity: List[Dict[str, Any]] = []
        self._identity_traits: Dict[str, float] = {}

        # --- 3) AUTOBIOGRAFIS / MENTAL TIME TRAVEL ---
        self.timeline: List[Dict[str, Any]] = []
        self.chapters: List[Dict[str, Any]] = []
        self._chapter_open: Optional[Dict[str, Any]] = None
        # CORE MEMORY ("momen, bukan rata-rata"): episode yang jadi pilar
        # identitas — tak pernah di-prune, sering muncul di kesadaran, mengikat
        # klaim identitas, dan memfilter interpretasi lewat cap kepercayaan.
        self.core_memory: List[Dict[str, Any]] = []
        self.future_sim: List[Dict[str, Any]] = []
        self.counterfactual_emotions: Dict[str, float] = {}
        self._counterfactual_log: List[Dict[str, Any]] = []

        # --- 4) SENSE OF AGENCY & BODY OWNERSHIP ---
        self.agency: float = 0.5
        self.ownership: float = 0.5
        self.effort: float = 0.0
        self._agency_log: List[Dict[str, Any]] = []
        # Lokus tubuh bukan slot yang dapat ditukar: anchor dan kerangka
        # spasial selalu milik NPC ini, terpisah dari konten imajinasi.
        seed = getattr(naluri, "rng_seed", None)
        nama = str(getattr(naluri, "name", "") or "anonim")
        self._body_locus: Dict[str, Any] = {
            "anchor": "tubuh:{}:{}".format(nama, seed if seed is not None else 0),
            "singular": True, "viewpoint": "egosentris",
            "position": None, "orientation": 0.0,
            "sensory_horizon": 1.0,
            # Ikut disemai agar round-trip `to_dict`/`from_dict` idempoten:
            # `update_body_locus` dan `from_dict` sama-sama menuliskan kunci ini.
            "ownership": self.ownership,
        }
        self._body_imagination_log: List[Dict[str, Any]] = []

        # --- 5) CONSCIOUS INTEROCEPTION & MORAL EMOTIONS ---
        self.felt: Dict[str, float] = {k: 0.0 for k in FELT_STATES}
        self.moral: Dict[str, float] = {k: 0.0 for k in MORAL_EMOTIONS}
        self.epistemic_emotions: Dict[str, float] = {
            k: 0.0 for k in EPISTEMIC_EMOTIONS}
        # Tekstur tubuh epistemik tidak dicampur ke felt_state organik biasa.
        self.epistemic_body: Dict[str, float] = {
            "dahi_mengerut": 0.0, "dada_mengendur": 0.0,
            "wajah_hangat": 0.0, "napas_tertahan": 0.0,
            "rahang_tegang": 0.0, "tubuh_condong": 0.0,
            "bahu_rileks": 0.0,
        }
        self._epistemic_log: List[Dict[str, Any]] = []
        self.somatic_markers: List[Dict[str, Any]] = []
        # Opasitas-diri adalah model berulang tentang salah mengenali perasaan
        # dan/atau tidak mengetahui sebabnya; bukan sinonim prediction error.
        self._self_opacity: Dict[str, Any] = {
            "perasaan_dikenali": "", "perasaan_laten": "",
            "sebab_diyakini": "", "sebab_laten": "",
            "ketidakcocokan": 0.0, "ketidakjelasan_sebab": 0.0,
            "jumlah_ketidakcocokan": 0, "status": "jelas", "kalimat": "",
        }
        self._self_opacity_log: List[Dict[str, Any]] = []

        # --- 6) REALITY MONITORING & METACOGNITIVE DOUBT ---
        self.reality: Dict[str, float] = {k: 0.0 for k in REALITY_SOURCES}
        self.source_log: List[Dict[str, Any]] = []
        self.doubt: float = 0.0
        self.confabulations: List[Dict[str, Any]] = []

        # --- 7) ATTENTION LIMITS ---
        self.blindness_log: List[Dict[str, Any]] = []
        self._blink_until: int = 0
        self._focus_tag: Optional[str] = None
        self._last_focus_tag: Optional[str] = None
        # Kelelahan atensi berakumulasi dari pemrosesan/percakapan, pulih saat
        # jeda; nilainya tidak diturunkan dari level energi atau metabolisme.
        self._attention_fatigue: float = 0.0
        self._attention_last_recovery_tick: int = self._tick()
        self._attention_effort_count: int = 0
        self._attention_log: List[Dict[str, Any]] = []
        # LANTAI KESADARAN: aturan sumber yang mencegah konten menjadi kandidat,
        # bukan sekadar membuatnya kalah skor atensi.
        self._lantai_kesadaran: List[Dict[str, Any]] = []
        self._lantai_log: List[Dict[str, Any]] = []
        self._bersama_yang_dihormati: bool = False

        # --- 8) SOCIAL COGNITION & SECOND-PERSON LOOP ---
        self._joint_attention: Dict[str, Dict[str, Any]] = {}
        self.commitments: List[Dict[str, Any]] = []
        # KONFRONTASI BERBASIS BUKTI (fitur 3): bukti yang diterima + koreksi
        # ingatan yang berhasil — jejaknya bisa diaudit & diserialisasi.
        self._bukti_log: List[Dict[str, Any]] = []
        self._koreksi_log: List[Dict[str, Any]] = []
        self._recursive_tom: Dict[str, Dict[str, float]] = {}
        self.gossip_log: List[Dict[str, Any]] = []

        # --- 9) DIALOGUE PRAGMATICS ---
        self.turn_state: Dict[str, Any] = {"last_speaker": None, "turn": 0,
                                           "topic": "", "open_question": None}
        self.backchannels: List[Dict[str, Any]] = []
        self.repairs: List[Dict[str, Any]] = []
        self._shared_history: List[str] = []
        # Dorongan tutur yang terbentuk dan mampu diucapkan, tetapi dipilih
        # untuk ditahan. Bukan refusal/prinsip, bukan penolakan tubuh, bukan
        # kontradiksi; isi hanya dibuka oleh keputusan sadar NPC sendiri.
        self._withheld_speech: List[Dict[str, Any]] = []
        self._withheld_next_id: int = 1
        self._withholding_disclosure_log: List[Dict[str, Any]] = []
        # Strategi sosial adalah pilihan sadar: model keyakinan pihak lain,
        # kebohongan yang dipilih, urutan manipulasi, penyamaran, dan kesetiaan.
        self._other_belief_models: Dict[str, Dict[str, Any]] = {}
        self._strategic_deceptions: List[Dict[str, Any]] = []
        self._manipulation_plans: List[Dict[str, Any]] = []
        self._roleplay_state: Optional[Dict[str, Any]] = None
        self._strategic_loyalty: List[Dict[str, Any]] = []
        self._social_strategy_next_id: int = 1
        # SA_SP: analisis pragmatik ujaran masuk terakhir, terpisah dari isi
        # literal dan tidak pernah dianggap sebagai ground truth.
        self._sa_sp_log: List[Dict[str, Any]] = []
        self._sa_sp_analyzer: Any = None
        # Tujuan kehendak bebas di luar stack drive: hanya tercatat setelah
        # keputusan eksplisit/pertimbangan sendiri, lalu dapat memandu aksi.
        self._free_will_goals: List[Dict[str, Any]] = []
        self._free_will_next_id: int = 1
        self._free_will_events: List[Dict[str, Any]] = []
        # Audisi-diri: suara yang keluar kembali sebagai input pendengaran yang
        # berjarak, bukan niat batin atau catatan giliran pragmatik.
        self._self_audition_log: List[Dict[str, Any]] = []
        self._self_audition_next_id: int = 1
        self._self_audition_reaction: Dict[str, Any] = {
            "surprise": 0.0, "shame": 0.0, "self_doubt": 0.0,
            "tick": -10_000}

        # --- 10) FALLIBILITY / BIAS / SELF-DECEPTION ---
        self.dissonance: Dict[str, Dict[str, Any]] = {}
        self.biases: Dict[str, float] = {k: 0.0 for k in SELF_BIASES}
        self.denials: List[Dict[str, Any]] = []

        # --- 11) INDIVIDUALITY / VALUES / BOUNDARIES ---
        self.values: Dict[str, float] = {}
        self.boundaries: List[str] = []
        self.refusals: List[Dict[str, Any]] = []
        self.quirks: List[str] = []

        # --- 12) MORTALITY / VULNERABILITY / GRIEF ---
        self.mortality_salience: float = 0.0
        self.grief: Dict[str, Dict[str, Any]] = {}
        self.losses: List[Dict[str, Any]] = []

        # --- 13) DREAMS & SLEEP CONTINUITY ---
        self.dream_log: List[Dict[str, Any]] = []
        self.last_dream: Optional[Dict[str, Any]] = None
        self.sleep_inertia: float = 0.0
        self._dream_pending: List[str] = []
        self.sleep_insights: List[Dict[str, Any]] = []
        self.last_sleep_insight: Optional[Dict[str, Any]] = None
        # Estetika/permainan memakai dua frame yang dapat hidup paralel, bukan
        # mengubah simulasi menjadi sekadar target-utilitas.
        self.aesthetic_state: Dict[str, Any] = {}
        self.play_state: Dict[str, Any] = {"aktif": False, "jenis": "",
                                           "keceriaan": 0.0,
                                           "inkongruensi": 0.0}
        self._humor_log: List[Dict[str, Any]] = []

        self._seeded: bool = False
        # 4D) narrative coherence: jumlah kontradiksi identitas-vs-perilaku.
        self._coherence_conflicts: int = 0

    # ------------------------------------------------------------------
    def enabled(self, feature: str) -> bool:
        """True bila master + flag fitur aktif (dibaca ulang tiap panggilan)."""
        if not bool(self.params.get("enable_kesadaran", False)):
            return False
        return bool(self.params.get("enable_" + feature, True))

    def _p(self, key: str) -> float:
        v = self.params.get(key, KESADARAN_DEFAULTS.get(key, 0.0))
        if isinstance(v, Mapping):
            v = v.get("*", KESADARAN_DEFAULTS.get(key, 0.0))
        try:
            return float(v)
        except (TypeError, ValueError):
            return float(KESADARAN_DEFAULTS.get(key, 0.0))

    def _tick(self) -> int:
        return int(getattr(self.naluri, "tick_count", 0))

    def _levels(self) -> Dict[str, float]:
        return dict(getattr(self.naluri, "levels", {}) or {})

    def _emosi(self) -> Dict[str, float]:
        return dict(getattr(self.naluri, "emosi", {}) or {})

    def _nama(self) -> str:
        return str(getattr(self.naluri, "name", "") or "aku")

    # ==================================================================
    # 1) GLOBAL WORKSPACE — kompetisi atensi + ignition
    # ==================================================================
    def observe_event(self, ev: Mapping[str, Any]) -> None:
        """Catat peristiwa ke kandidat workspace (dipanggil dari apply_events)."""
        if not self.enabled("global_workspace"):
            return
        if not isinstance(ev, Mapping):
            return
        teks = ev.get("stimulus", ev.get("context", ev.get("text", ev.get("reason"))))
        drive = ev.get("drive")
        delta = _kclip(ev.get("delta", 0.0))
        emosi = ev.get("emosi")
        sal = abs(delta)
        if emosi:
            sal = max(sal, float(ev.get("intensitas", 0.5)))
        if sal < 0.05 and not teks:
            return
        content = self._event_content(teks, drive, delta, emosi)
        self.submit(content, salience=min(1.0, 0.15 + sal),
                    tag=str(drive or emosi or "dunia"),
                    source="persepsi", kind="event",
                    dapat_dilaporkan=ev.get("_dapat_dilaporkan", True) is not False)

    def daftar_lantai_kesadaran(self, tag: str, kondisi: Any,
                                 alasan: str,
                                 dapat_digeser_residu: bool = True,
                                 ambang_residu: float = 0.65) -> Dict[str, Any]:
        """Pasang larangan pra-kandidat yang dinilai ulang setiap tick.

        ``kondisi`` dapat berupa nama kondisi (``arousal_tinggi``, ``aman``,
        atau ``bersama_yang_dihormati``) atau mapping berisi ``emosi``,
        ``drive``, ``di_atas``/``di_bawah``, dan kombinator ``semua`` atau
        ``salah_satu``.  Tekanan residu yang cukup kuat *menggeser aturan*;
        ia bukan bonus salience bagi konten yang sudah lolos.
        """
        aturan = {
            "tag": str(tag)[:40], "kondisi": kondisi,
            "alasan": str(alasan)[:160],
            "dapat_digeser_residu": bool(dapat_digeser_residu),
            "ambang_residu": _kclip(ambang_residu, 0.0, 1.0),
        }
        self._lantai_kesadaran.append(aturan)
        return dict(aturan)

    def set_konteks_lantai(self, *, bersama_yang_dihormati: bool = False) -> None:
        self._bersama_yang_dihormati = bool(bersama_yang_dihormati)

    def _kondisi_lantai_aktif(self, kondisi: Any) -> bool:
        lv, em = self._levels(), self._emosi()
        if isinstance(kondisi, str):
            nama = kondisi.strip().lower()
            if nama == "arousal_tinggi":
                return max(em.values(), default=0.0) >= 0.62
            if nama == "aman":
                return lv.get("keamanan", 0.0) >= -0.10 and em.get("takut", 0.0) < 0.35
            if nama == "bersama_yang_dihormati":
                return self._bersama_yang_dihormati
            return bool(getattr(self.naluri, nama, False))
        if not isinstance(kondisi, Mapping):
            return bool(kondisi)
        if "semua" in kondisi:
            return all(self._kondisi_lantai_aktif(x) for x in kondisi["semua"])
        if "salah_satu" in kondisi:
            return any(self._kondisi_lantai_aktif(x) for x in kondisi["salah_satu"])
        if "bersama_yang_dihormati" in kondisi and bool(
                kondisi["bersama_yang_dihormati"]) != self._bersama_yang_dihormati:
            return False
        sumber = em if "emosi" in kondisi else lv
        nama = str(kondisi.get("emosi", kondisi.get("drive", "")))
        nilai = float(sumber.get(nama, 0.0))
        if "di_atas" in kondisi and nilai < float(kondisi["di_atas"]):
            return False
        if "di_bawah" in kondisi and nilai > float(kondisi["di_bawah"]):
            return False
        return bool(nama or "bersama_yang_dihormati" in kondisi)

    def _tekanan_residu_lantai(self, tag: str) -> float:
        organik = getattr(self.naluri, "_organik", None)
        residu = getattr(organik, "residu", None)
        if residu is None:
            return 0.0
        tekanan = float(residu.tekanan_target(tag))
        # Duka/trauma yang tak terselesaikan dapat membuka lantai lain yang
        # tadinya aman. Ini sengaja mengambil maksimum, bukan menambah bias.
        for target in ("duka", "sedih", "trauma"):
            tekanan = max(tekanan, float(residu.tekanan_target(target)))
        return _kclip(tekanan, 0.0, 1.0)

    def _lolos_lantai(self, item: Mapping[str, Any]) -> bool:
        tag = str(item.get("tag", ""))
        for aturan in self._lantai_kesadaran:
            sasaran = str(aturan.get("tag", ""))
            cocok = sasaran == "*" or tag == sasaran or tag.startswith(sasaran + ":")
            if not cocok or not self._kondisi_lantai_aktif(aturan.get("kondisi")):
                continue
            tekanan = self._tekanan_residu_lantai(tag)
            bergeser = bool(aturan.get("dapat_digeser_residu", True)) and tekanan >= float(
                aturan.get("ambang_residu", 0.65))
            self._lantai_log.append({
                "tick": self._tick(), "tag": tag,
                "alasan": str(aturan.get("alasan", "")),
                "status": "digeser_residu" if bergeser else "diblokir",
                "tekanan_residu": tekanan,
            })
            self._lantai_log = self._lantai_log[-128:]
            if not bergeser:
                return False
        return True

    def submit(self, content: str, salience: float = 0.5, tag: str = "dunia",
               source: str = "persepsi", kind: str = "event",
               detail: Optional[Dict[str, Any]] = None,
               dapat_dilaporkan: bool = True) -> Dict[str, Any]:
        """Ajukan satu konten ke panggung kesadaran (belum tentu lolos)."""
        item = {
            "content": str(content)[:160],
            "salience": _kclip(salience, 0.0, 1.0),
            "tag": str(tag)[:40],
            "source": str(source),
            "kind": str(kind),
            "tick": self._tick(),
            "detail": dict(detail or {}),
            "_dapat_dilaporkan": bool((detail or {}).get(
                "_dapat_dilaporkan", dapat_dilaporkan)),
        }
        if not self._lolos_lantai(item):
            item["blocked_by_consciousness_floor"] = True
            return item
        self.workspace.append(item)
        if len(self.workspace) > 24:
            del self.workspace[:-24]
        return item

    @staticmethod
    def _event_content(teks: Any, drive: Any, delta: float, emosi: Any) -> str:
        if teks:
            return str(teks)
        if emosi:
            return f"aku merasa {emosi}"
        if drive:
            arah = "naik" if delta > 0 else "turun"
            return f"{drive} {arah}"
        return "sesuatu terjadi"

    def _candidates(self) -> List[Dict[str, Any]]:
        """Bangun kandidat kesadaran dari seluruh modul (self-report + dunia)."""
        n = self.naluri
        out: List[Dict[str, Any]] = []
        def add(item: Dict[str, Any]) -> None:
            # Admission happens here, before the item can join the candidate
            # population or acquire a competition score.
            if self._lolos_lantai(item):
                out.append(item)
        for pending in self.workspace:
            add(dict(pending))
        lv = self._levels()
        # drive defisit → isi kepala
        for d, v in lv.items():
            if v < -0.35:
                add({"content": self._drive_phrase(d, v), "salience":
                            min(1.0, 0.35 + abs(v) * 0.5), "tag": d,
                            "source": "interosepsi", "kind": "drive",
                            "tick": self._tick(), "detail": {"level": v}})
        # emosi kuat
        for e, val in self._emosi().items():
            if val > 0.25:
                add({"content": f"aku merasa {e}", "salience":
                            min(1.0, 0.3 + val * 0.6), "tag": e,
                            "source": "afek", "kind": "emosi",
                            "tick": self._tick(), "detail": {"intensity": val}})
        # kondisi tubuh yang dirasakan
        for k, v in self.felt.items():
            if v > 0.3:
                add({"content": self._felt_phrase(k), "salience":
                            min(1.0, 0.3 + v * 0.5), "tag": "tubuh",
                            "source": "interosepsi", "kind": "felt",
                            "tick": self._tick(), "detail": {"felt": k, "v": v}})
        # goal aktif
        for g in getattr(n, "goals", []) or []:
            try:
                txt = getattr(g, "scenario", None) or f"aku perlu {getattr(g, 'drive', '')}"
            except Exception as _galat_diagnostik_1:
                _diag.catat('naluri.Kesadaran._candidates', "galat pada jalur fallback", galat=_galat_diagnostik_1, jalur=1)
                txt = "aku punya tujuan"
            add({"content": str(txt)[:120], "salience":
                        min(1.0, 0.3 + float(getattr(g, "urgency", 0.0))),
                        "tag": str(getattr(g, "drive", "goal")), "source": "goal",
                        "kind": "goal", "tick": self._tick(), "detail": {}})
        # working memory
        for c in getattr(n, "context_aktif", []) or []:
            add({"content": str(c.get("stimulus", ""))[:120],
                        "salience": min(1.0, 0.2 + float(c.get("salience", 0.0))),
                        "tag": "ingatan", "source": "ingatan", "kind": "wm",
                        "tick": self._tick(), "detail": {}})
        # mortalitas
        if self.mortality_salience > 0.3:
            add({"content": "aku bisa mati", "salience":
                        min(1.0, self.mortality_salience), "tag": "mortalitas",
                        "source": "kesadaran", "kind": "mortality",
                        "tick": self._tick(), "detail": {}})
        # duka
        for ent, g in self.grief.items():
            if float(g.get("intensity", 0.0)) > 0.3:
                add({"content": f"aku kehilangan {ent}", "salience":
                            min(1.0, float(g.get("intensity", 0.0))), "tag": "duka",
                            "source": "afek", "kind": "grief", "tick": self._tick(),
                            "detail": {"entitas": ent}})
        # CORE MEMORY: pilar identitas selalu dekat dengan permukaan pikiran —
        # salience tinggi agar sering menang kompetisi atensi (momen, bukan
        # rata-rata: satu kejadian boleh mendominasi isi kepala).
        for cm in self.core_memory:
            bobot = float(cm.get("bobot", 1.0))
            add({"content": str(cm.get("ringkas", ""))[:120],
                        "salience": min(1.0, 0.55 + 0.35 * bobot),
                        "tag": cm.get("klaim") or cm.get("tag") or "inti",
                        "source": "inti", "kind": "core",
                        "tick": int(cm.get("tick", self._tick())),
                        "detail": {"klaim": cm.get("klaim"), "bobot": bobot}})
        return out

    @property
    def attention_fatigue(self) -> float:
        return jepit_01(float(self._attention_fatigue))

    @property
    def attentional_fatigue(self) -> float:
        return self.attention_fatigue

    def _recover_attention(self, steps: Optional[float] = None) -> float:
        """Pulihkan atensi lewat waktu/jeda, bukan lewat energi metabolik."""
        if not self.enabled("global_workspace"):
            return self.attention_fatigue
        now = self._tick()
        elapsed = max(0.0, float(now - self._attention_last_recovery_tick))
        if steps is not None and elapsed <= 0.0:
            try:
                elapsed = max(0.0, float(steps))
            except (TypeError, ValueError):
                elapsed = 0.0
        pulih = max(0.0, self._p("kesadaran_atensi_pulih")) * elapsed
        self._attention_fatigue = max(0.0, self._attention_fatigue - pulih)
        self._attention_last_recovery_tick = now
        return self.attention_fatigue

    def attention_effort(self, text: Any = "", source: str = "pemrosesan",
                         amount: Optional[float] = None) -> float:
        """Akumulasikan beban pemrosesan/percakapan yang mengeraskan atensi."""
        if not self.enabled("global_workspace"):
            return self.attention_fatigue
        self._recover_attention()
        words = re.findall(r"[\wÀ-ÿ]+", str(text or ""), flags=re.UNICODE)
        if amount is None:
            amount = 0.012 + min(0.065, 0.0025 * len(words))
            amount += min(0.018, 0.002 * sum(str(text or "").count(p)
                                             for p in (",", ";", ":", "?")))
        try:
            beban = jepit(float(amount), 0.0, 0.20)
        except (TypeError, ValueError):
            beban = 0.0
        self._attention_fatigue = jepit_01(self._attention_fatigue + beban)
        self._attention_effort_count += 1
        self._attention_log.append({"tick": self._tick(),
                                    "sumber": str(source or "pemrosesan")[:32],
                                    "beban": round(beban, 4),
                                    "kelelahan": round(self._attention_fatigue, 4)})
        if len(self._attention_log) > 64:
            self._attention_log = self._attention_log[-64:]
        return self.attention_fatigue

    def attention_state(self) -> Dict[str, Any]:
        fatigue = self.attention_fatigue
        return {"aktif": self.enabled("global_workspace"),
                "fatigue": round(fatigue, 4),
                "kelelahan_atensi": round(fatigue, 4),
                "clarity": round(max(0.25, 1.0 - 0.60 * fatigue), 4),
                "effort_count": self._attention_effort_count,
                "recovery_per_tick": round(max(0.0, self._p(
                    "kesadaran_atensi_pulih")), 5),
                "terakhir": (dict(self._attention_log[-1])
                             if self._attention_log else None)}

    @staticmethod
    def _drive_phrase(d: str, v: float) -> str:
        tabel = {
            "energi": "aku lelah", "keamanan": "aku tidak aman",
            "keingintahuan": "aku penasaran", "penguasaan": "aku ingin menguasai keadaan",
            "afiliasi": "aku kesepian", "koherensi": "aku bingung",
        }
        return tabel.get(d, f"{d} menekan")

    @staticmethod
    def _felt_phrase(k: str) -> str:
        tabel = {
            "nyeri": "badanku nyeri", "lelah": "aku tidak enak badan",
            "lapar": "aku lapar", "sesak": "dadaku sesak",
            "jantung": "jantungku berdebar", "mual": "aku mual",
            "tegang": "tubuhku tegang", "ringan": "badanku ringan",
        }
        return tabel.get(k, f"aku merasa {k}")

    def attend(self, candidates: Optional[List[Dict[str, Any]]] = None
               ) -> List[Dict[str, Any]]:
        """Kompetisi atensi: pilih 1–3 konten; sisanya diproses diam-diam."""
        if not self.enabled("global_workspace"):
            return []
        cands = candidates if candidates is not None else self._candidates()
        if not cands:
            self.spotlight = []
            return []
        # Proses memilih juga memakai sumber daya atensional, lalu state yang
        # terakumulasi menurunkan kejernihan pada pemilihan berikutnya.
        self._recover_attention()
        beban = (max(0.0, self._p("kesadaran_atensi_beban_tick"))
                 + max(0.0, self._p("kesadaran_atensi_beban_kandidat"))
                 * min(8, len(cands)))
        self.attention_effort(source="workspace", amount=beban)
        fatigue = self.attention_fatigue
        clarity = max(0.35, 1.0 - 0.55 * fatigue)
        # atensi terbatas (konsep 7): setelah ignition, ada attentional blink —
        # konten baru ditekan sesaat.
        blink = (self.enabled("attention_limits")
                 and self._tick() < self._blink_until)
        scored: List[Tuple[float, Dict[str, Any]]] = []
        for c in cands:
            sal = _kclip(c.get("salience", 0.0), 0.0, 1.0)
            # bias top-down: drive yang sedang urgent & tag yang selaras fokus
            bias = 0.0
            try:
                urg = getattr(self.naluri, "urgency", {}) or {}
                tag = c.get("tag")
                if tag in urg:
                    bias += (0.15 * _kclip(urg.get(tag, 0.0), 0.0, 2.5)
                             / 2.5) * max(0.55, 1.0 - 0.30 * fatigue)
            except Exception as _galat_diagnostik_2:
                _diag.catat('naluri.Kesadaran.attend', "galat pada jalur fallback", galat=_galat_diagnostik_2, jalur=2)
                pass
            noise = 0.0
            try:
                noise = float(self._rng.gauss(0.0, 0.04 * (1.0 + 0.75 * fatigue)))
            except Exception as _galat_diagnostik_3:
                _diag.catat('naluri.Kesadaran.attend', "galat pada jalur fallback", galat=_galat_diagnostik_3, jalur=3)
                noise = 0.0
            eff = sal * clarity + bias + noise
            # Saat lelah, petunjuk halus kehilangan resolusi lebih cepat daripada
            # stimulus mencolok: minat terasa datar, bukan drive yang berubah.
            if sal < 0.45:
                eff -= fatigue * 0.12 * (0.45 - sal) / 0.45
            if blink:
                eff *= 0.45
            # inattentional blindness: konten di luar fokus teredam
            if (self.enabled("attention_limits") and self._focus_tag
                    and c.get("tag") != self._focus_tag
                    and c.get("kind") not in ("mortality", "grief", "event")):
                eff *= max(0.0, 1.0 - self._p("kesadaran_blindness_gain") * 0.5)
            scored.append((eff, c))
        scored.sort(key=lambda x: x[0], reverse=True)
        cap_dasar = max(1, min(3, int(self._p("kesadaran_workspace_size"))))
        cap = max(1, min(3, int(round(cap_dasar * (1.0 - 0.55 * fatigue)))))
        self.spotlight = [dict(c, attention=round(s, 4))
                          for s, c in scored[:cap]]
        if self.spotlight:
            self._last_focus_tag = self._focus_tag
            self._focus_tag = self.spotlight[0].get("tag")
        # change blindness (konsep 7): perubahan kecil pada konten yang TIDAK
        # terpilih tidak disadari.
        if self.enabled("attention_limits"):
            self._detect_change_blindness(scored[cap:])
        # ignition: konten terkuat melewati ambang → broadcast global
        if self.spotlight:
            top = self.spotlight[0]
            if top.get("attention", 0.0) >= self._p("kesadaran_ignition_threshold"):
                self._ignite(top)
        return self.spotlight

    def _ignite(self, item: Mapping[str, Any]) -> Dict[str, Any]:
        ev = {
            "tick": self._tick(), "content": item.get("content"),
            "tag": item.get("tag"), "salience": round(
                float(item.get("attention", item.get("salience", 0.0))), 4),
            "source": item.get("source"), "kind": item.get("kind"),
            "_dapat_dilaporkan": item.get("_dapat_dilaporkan", True) is not False,
        }
        self.ignitions.append(ev)
        if len(self.ignitions) > int(self._p("kesadaran_ignition_max")):
            self.ignitions = self.ignitions[-int(self._p("kesadaran_ignition_max")):]
        self._ignition_count += 1
        self._last_ignition_tick = self._tick()
        self._broadcast.append(dict(ev))
        if len(self._broadcast) > 32:
            self._broadcast = self._broadcast[-32:]
        # attentional blink + memori autobiografis
        if self.enabled("attention_limits"):
            self._blink_until = self._tick() + max(1, int(self._p("kesadaran_blink_ticks")))
        # Jalur autobiografis menghasilkan bahan self-report; konten yang sadar
        # namun tak dapat dilaporkan tidak boleh bocor melaluinya kemudian.
        if ev.get("_dapat_dilaporkan", True) is not False:
            self._remember_episode(ev, penting=True)
        return ev

    def _detect_change_blindness(self, unattended: List[Tuple[float, Dict[str, Any]]]) -> None:
        # hanya sadar perubahan bila konten serupa pernah di panggung
        for _, c in unattended:
            tag = c.get("tag")
            before = next((w for w in reversed(self.workspace[:-1])
                           if w.get("tag") == tag and w is not c), None)
            if before is None:
                continue
            a = str(before.get("content", ""))
            b = str(c.get("content", ""))
            if a and b and a != b:
                self.blindness_log.append({
                    "tick": self._tick(), "jenis": "change_blindness",
                    "tag": tag, "sebelum": a[:80], "sesudah": b[:80]})
                if len(self.blindness_log) > 64:
                    self.blindness_log = self.blindness_log[-64:]

    def inattentional_blindness(self, stimulus: str, tag: str = "dunia") -> bool:
        """True bila stimulus DILEWATKAN karena di luar fokus (contoh perilaku)."""
        if not self.enabled("attention_limits"):
            return False
        fokus = self._focus_tag
        lewat = bool(fokus) and tag != fokus
        if lewat:
            self.blindness_log.append({
                "tick": self._tick(), "jenis": "inattentional_blindness",
                "tag": tag, "stimulus": str(stimulus)[:80]})
            if len(self.blindness_log) > 64:
                self.blindness_log = self.blindness_log[-64:]
        return lewat

    def workspace_report(self) -> Dict[str, Any]:
        """Isi kesadaran kini; intrusi ditandai ``datang_tanpa_sebab``."""
        boleh = lambda c: c.get("_dapat_dilaporkan", True) is not False
        intrusif = [c for c in self.workspace[-12:]
                    if boleh(c) and (c.get("datang_tanpa_sebab") or
                                     c.get("kind") == "intrusi")]
        broadcast_laporan = next((dict(c) for c in reversed(self._broadcast)
                                  if boleh(c)), None)
        return {
            "aktif": self.enabled("global_workspace"),
            "spotlight": [{"content": c.get("content"), "tag": c.get("tag"),
                           "salience": round(float(c.get("attention", 0.0)), 3),
                           "datang_tanpa_sebab": bool(
                               c.get("datang_tanpa_sebab") or
                               c.get("kind") == "intrusi")}
                          for c in self.spotlight if boleh(c)],
            "workspace": [c.get("content") for c in self.workspace[-8:] if boleh(c)],
            "intrusi": [{"content": c.get("content"),
                         "jenis": (c.get("detail") or {}).get("jenis"),
                         "label": "datang tanpa sebab"}
                        for c in intrusif[-4:]],
            "broadcast_terakhir": broadcast_laporan,
            "ignition_count": self._ignition_count,
            "blink_sisa": max(0, self._blink_until - self._tick()),
            "atensi": self.attention_state(),
        }

    def decision_bias(self) -> Dict[str, float]:
        """Konten yang disiarkan (ignition) mem-bias keputusan drive."""
        bias: Dict[str, float] = {d: 0.0 for d in DRIVES}
        if not self.enabled("global_workspace"):
            return bias
        for ev in self._broadcast[-3:]:
            tag = ev.get("tag")
            if tag in bias:
                bias[tag] += 0.08 * float(ev.get("salience", 0.0))
        # Konten sadar yang tak bisa dilaporkan tetap kausal. Ia ditambahkan
        # dari spotlight walau tidak tersedia bagi laporan verbal.
        for item in self.spotlight:
            tag = item.get("tag")
            sudah_disiarkan = any(
                ev.get("tag") == tag and ev.get("content") == item.get("content")
                and ev.get("_dapat_dilaporkan", True) is False
                for ev in self._broadcast[-3:])
            if (item.get("_dapat_dilaporkan", True) is False
                    and tag in bias and not sudah_disiarkan):
                bias[tag] += 0.08 * float(item.get("attention", item.get("salience", 0.0)))
        # somatic marker: tubuh menandai nilai sebelum pikiran sadar
        if self.enabled("felt_state"):
            for m in self.somatic_markers[-6:]:
                tag = m.get("tag")
                if tag in bias:
                    bias[tag] += 0.05 * float(m.get("valence", 0.0))
        return bias

    # ==================================================================
    # 2) INNER SPEECH & NARASI ORANG-PERTAMA
    # ==================================================================
    def inner_speech(self, trigger: Optional[str] = None) -> str:
        """Hasilkan monolog batin dari konten sadar + identitas naratif."""
        if not self.enabled("inner_speech"):
            return ""
        top = next((c for c in self.spotlight
                    if c.get("_dapat_dilaporkan", True) is not False), None)
        if top is None and trigger:
            top = {"content": trigger, "kind": "dunia", "tag": "dunia"}
        if top is None:
            return ""
        isi = str(top.get("content", ""))
        kalimat = self._speak_template(isi, top.get("kind", ""), top.get("tag", ""))
        # sisipkan identitas naratif yang relevan
        ident = self._identity_relevant(isi, top.get("tag", ""))
        if ident:
            kalimat = f"{kalimat} (aku tahu {ident})" if ident else kalimat
        entry = {"tick": self._tick(), "kalimat": kalimat[:240],
                 "sebab": isi[:80], "kind": top.get("kind", "")}
        self.self_talk.append(entry)
        if len(self.self_talk) > int(self._p("kesadaran_speech_max")):
            self.self_talk = self.self_talk[-int(self._p("kesadaran_speech_max")):]
        return kalimat

    # ==================================================================
    # 2b) AUDISI-DIRI — ujaran keluar kembali sebagai suara yang didengar
    # ==================================================================
    def _self_audition_reaction_now(self) -> Dict[str, float]:
        raw = self._self_audition_reaction
        umur = max(0, self._tick() - int(raw.get("tick", -10_000)))
        return {
            "surprise": round(jepit_01(float(raw.get("surprise", 0.0)) * (0.70 ** min(umur, 40))), 4),
            "shame": round(jepit_01(float(raw.get("shame", 0.0)) * (0.88 ** min(umur, 40))), 4),
            "self_doubt": round(jepit_01(float(raw.get("self_doubt", 0.0)) * (0.84 ** min(umur, 40))), 4),
        }

    def audition_self(self, utterance: Any, intended: Any = None,
                      act: Any = None, topic: Any = None,
                      audience: Any = None,
                      prosody: Optional[Mapping[str, Any]] = None
                      ) -> Dict[str, Any]:
        """Dengar suara yang baru keluar sebagai input dari luar diri.

        Ini dipanggil sesudah realisasi ujaran, bukan dari inner_speech atau
        dialogue_turn. Jeda dicatat dalam milidetik (tanpa menahan thread),
        lalu konten auditori diproses menjadi kejutan, malu, atau keraguan diri.
        """
        if not self.enabled("self_audition"):
            return {"aktif": False}
        heard = str(utterance or "").strip()[:240]
        if not heard:
            return {"aktif": False, "alasan": "tidak_ada_suara"}
        niat = (str(intended.get("teks", intended.get("text", "")))
                if isinstance(intended, Mapping) else
                str(intended) if intended is not None else "")
        niat = niat.strip()[:240]
        # G5: keselarasan dihitung atas lema hasil stemming + bigram kata
        # isi (bukan token permukaan yang sama persis) — "menyerang" dan
        # "serang" dihitung sama.
        try:
            from pycos.refleksi.nurani import Nurani as _Nurani
            heard_terms = set(_Nurani._lexical_words(heard))
            intent_terms = (set(_Nurani._lexical_words(niat)) if niat
                            else set())
        except Exception as _galat_diagnostik_60:
            _diag.catat('naluri.Kesadaran.audition_self',
                        "galat pada jalur fallback",
                        galat=_galat_diagnostik_60, jalur=60)
            heard_terms = self._withholding_terms(heard)
            intent_terms = self._withholding_terms(niat) if niat else set()
        kesenjangan = 0.0
        keselarasan = None
        if niat:
            gabungan = heard_terms | intent_terms
            keselarasan = (len(heard_terms & intent_terms) / float(len(gabungan))
                           if gabungan else 1.0)
            kesenjangan = jepit_01(1.0 - keselarasan)

        emosi = self._emosi()
        felt = self.felt
        try:
            duka = max((float(x.get("intensity", 0.0) or 0.0)
                        for x in self.grief.values()), default=0.0)
        except Exception as _galat_diagnostik_4:
            _diag.catat('naluri.Kesadaran.audition_self', "galat pada jalur fallback", galat=_galat_diagnostik_4, jalur=4)
            duka = 0.0
        distress = max(
            float(emosi.get("takut", 0.0) or 0.0),
            float(emosi.get("sedih", 0.0) or 0.0),
            0.75 * float(emosi.get("marah", 0.0) or 0.0),
            0.85 * float(felt.get("nyeri", 0.0) or 0.0),
            0.70 * float(felt.get("lelah", 0.0) or 0.0),
            0.80 * float(felt.get("sesak", 0.0) or 0.0),
            min(1.0, duka))
        low = heard.lower()
        menenangkan_diri = bool(re.search(
            r"\b(?:aku|saya|gue|gua)\s+(?:baik[- ]baik\s+saja|"
            r"tidak\s+apa[- ]apa|tak\s+apa[- ]apa|gak\s+apa[- ]apa|"
            r"nggak\s+apa[- ]apa|baik saja)\b|"
            r"\bi(?:'m| am) fine\b|\bnothing is wrong\b", low,
            flags=re.UNICODE))
        suara = dict(prosody or {})
        try:
            tremor = jepit_01(float(suara.get("tremor", 0.0)))
        except (TypeError, ValueError):
            tremor = 0.0
        kebohongan_diri = (max(distress * 0.82, tremor * 0.75)
                           if menenangkan_diri else 0.0)
        kredibilitas_suara = jepit_01(1.0 - kebohongan_diri)

        pengakuan = bool(re.search(
            r"\b(?:aku|saya)\s+(?:takut|mencintai|membenci|rindu|butuh|"
            r"ingin|menyesal|bersalah)|aku tidak sanggup\b", low,
            flags=re.UNICODE))
        kejutan_auditori = max(0.86 * kesenjangan,
                       0.42 if pengakuan and not intent_terms else 0.0)
        ucapan_melukai = bool(re.search(
            r"\b(?:bodoh|tolol|brengsek|sialan|benci|jahat|tidak peduli)\b",
            low, flags=re.UNICODE))
        malu_retroaktif = max(
            0.72 if ucapan_melukai else 0.0,
            0.62 * kebohongan_diri,
            0.48 * kesenjangan if ucapan_melukai or "maaf" in low else 0.0)

        reaksisebelum = self._self_audition_reaction_now()
        reaksi = {
            "surprise": min(1.0, 0.62 * reaksisebelum["surprise"]
                            + 0.72 * kejutan_auditori),
            "shame": min(1.0, 0.70 * reaksisebelum["shame"]
                         + 0.65 * malu_retroaktif),
            "self_doubt": min(1.0, 0.72 * reaksisebelum["self_doubt"]
                              + 0.68 * kebohongan_diri),
        }
        self._self_audition_reaction = {**reaksi, "tick": self._tick()}
        ident = self._self_audition_next_id
        self._self_audition_next_id += 1
        # Jeda fisiologisnya singkat dan deterministik; tidak menghentikan API.
        delay_ms = 18 + (sum(ord(ch) for ch in heard[-16:]) % 27)
        entry = {
            "aktif": True, "id": ident, "tick": self._tick(),
            "jeda_ms": delay_ms, "latensi_kognitif_ms": delay_ms,
            "fase": "paralel_dan_segera_setelah_fonasi",
            "terdengar": heard,
            "niat_sebelum_bicara": niat or None,
            "act": str(act or "")[:32], "topik": str(topic or "")[:80],
            "kepada": (str(getattr(audience, "name", audience))[:64]
                       if audience is not None else ""),
            "sumber": "suara_diri_yang_terdengar_dari_luar",
            "perspektif_pendengar": "orang_ketiga_yang_mengenali_suaranya",
            "jarak_kognitif": 0.24,
            "niat_vs_realisasi": {
                "diukur_melalui_audisi": bool(niat),
                "keselarasan": (None if keselarasan is None else
                                round(keselarasan, 4)),
                "kesenjangan": round(kesenjangan, 4),
            },
            "surprise": round(kejutan_auditori, 4),
            "kebohongan_diri": round(kebohongan_diri, 4),
            "kredibilitas_suara": round(kredibilitas_suara, 4),
            "malu_retroaktif": round(malu_retroaktif, 4),
            "reaksi_setelah_mendengar": {k: round(v, 4)
                                         for k, v in reaksi.items()},
            "diproses_sebagai_input_baru": True,
        }
        self._self_audition_log.append(entry)
        if len(self._self_audition_log) > 64:
            self._self_audition_log = self._self_audition_log[-64:]
        if self.enabled("global_workspace"):
            try:
                self.submit(
                    "suara yang terdengar dari luar berkata: «" + heard[:96] + "»",
                    salience=min(1.0, 0.20 + 0.58 * max(
                        kejutan_auditori, kebohongan_diri, malu_retroaktif)),
                    tag="audisi_diri", source="suara_diri_dari_luar",
                    kind="audisi_diri", detail={
                        "audition_id": ident,
                        "kesenjangan_niat": round(kesenjangan, 4),
                        "kredibilitas_suara": round(kredibilitas_suara, 4),
                        "reaksi": dict(entry["reaksi_setelah_mendengar"]),
                    })
                self.attention_effort(heard, source="audisi_diri")
            except Exception as _galat_diagnostik_5:
                _diag.catat('naluri.Kesadaran.audition_self', "galat pada jalur fallback", galat=_galat_diagnostik_5, jalur=5)
                pass
        return copy.deepcopy(entry)

    audisi_diri = audition_self
    self_audition = audition_self

    def self_audition_state(self) -> Dict[str, Any]:
        return {"aktif": self.enabled("self_audition"),
                "jumlah": max(0, self._self_audition_next_id - 1),
                "tersimpan": len(self._self_audition_log),
                "reaksi": self._self_audition_reaction_now(),
                "terakhir": (copy.deepcopy(self._self_audition_log[-1])
                             if self._self_audition_log else None)}

    # API Indonesia
    keadaan_audisi_diri = self_audition_state

    def _speak_template(self, isi: str, kind: str, tag: str) -> str:
        low = isi.lower()
        # ancaman → menghindar; ingatan → time-travel; pujian → syukur
        if kind in ("mortality",) or any(k in low for k in
                                         ("bahaya", "ancaman", "api", "serang")):
            return f"aku harus menjauh dari {isi[:48]}"
        if kind == "grief":
            return f"aku masih memikirkan {isi[:48]}"
        if kind == "intrusi":
            return f"kenapa aku tiba-tiba memikirkan ini? — {isi[:56]}"
        if kind == "drive":
            if any(k in low for k in ("lelah", "energi")):
                return "aku butuh istirahat sejenak"
            if "aman" in low or "tidak aman" in low:
                return "aku harus mencari tempat yang aman"
            if "kesepian" in low or "afiliasi" in low:
                return "aku ingin ada yang menemaniku"
            if "bingung" in low or "koherensi" in low:
                return "kenapa semuanya terasa kacau?"
        if kind == "emosi":
            if "takut" in low:
                return "kenapa aku merasa seperti ini?"
            if "marah" in low:
                return "aku tidak boleh kehilangan kendali"
            if "penasaran" in low:
                return "ada sesuatu di sini yang ingin kutahu"
        if kind == "wm" or "ingatan" in tag:
            return f"aku ingat {isi[:48]}"
        if "player" in low or "@" in low:
            return f"kenapa dia melakukan itu? {isi[:40]}"
        # default: pertanyaan batin / niat
        pilih = ("aku harus berhati-hati", "apa maksudnya?",
                 "aku ingin tahu lebih banyak", "aku harus menghadapinya",
                 "aku tidak yakin harus bagaimana")
        try:
            return f"{self._rng.choice(pilih)} — {isi[:48]}" if isi else self._rng.choice(pilih)
        except Exception as _galat_diagnostik_6:
            _diag.catat('naluri.Kesadaran._speak_template', "galat pada jalur fallback", galat=_galat_diagnostik_6, jalur=6)
            return f"aku memikirkan {isi[:48]}"

    def _identity_relevant(self, isi: str, tag: str) -> str:
        low = isi.lower()
        for claim, _w in sorted(self._identity_traits.items(),
                                key=lambda kv: kv[1], reverse=True):
            if claim in low:
                return f"aku orang yang {claim}"
        return ""

    def form_identity(self) -> List[Dict[str, Any]]:
        """Bentuk/perbarui klaim identitas dari episode autobiografis.

        Contoh: ancaman berulang → "tidak mudah percaya"; pengkhianatan →
        "pernah dikhianati".
        """
        if not self.enabled("inner_speech"):
            return []
        traits: Dict[str, float] = {}
        # dari emosi kronis
        for e, val in self._emosi().items():
            if val > 0.35:
                traits[f"sering merasa {e}"] = 0.02 * val
        # dari episode autobiografis yang menonjol
        for item in self.timeline[-12:]:
            if item.get("penting"):
                traits[f"pernah mengalami {str(item.get('ringkas', ''))[:24]}"] = 0.03
        # CORE MEMORY mengikat klaim identitas paling kuat (pilar diri).
        for cm in self.core_memory:
            bobot = float(cm.get("bobot", 1.0))
            klaim = cm.get("klaim")
            if klaim:
                traits[str(klaim)[:60]] = 0.06 * bobot
            else:
                traits[f"pernah {str(cm.get('ringkas', ''))[:24]}"] = 0.05 * bobot
        return self._refresh_identity(traits)

    def _refresh_identity(self, evidence: Dict[str, float]) -> List[Dict[str, Any]]:
        for k, v in evidence.items():
            self._identity_traits[k] = _kclip(
                self._identity_traits.get(k, 0.0) + v, -1.0, 1.0)
        # ambil klaim terkuat
        for claim, w in sorted(self._identity_traits.items(),
                               key=lambda kv: kv[1], reverse=True)[:6]:
            if w < 0.35:
                continue
            if not any(x.get("klaim") == claim for x in self.narrative_identity):
                entry = {"tick": self._tick(), "klaim": claim,
                         "kekuatan": round(w, 3)}
                self.narrative_identity.append(entry)
        if len(self.narrative_identity) > 16:
            self.narrative_identity = self.narrative_identity[-16:]
        return self.narrative_identity

    def narrative_state(self) -> str:
        """Kalimat identitas untuk dialog: 'aku orang yang tidak mudah percaya'."""
        if not self.narrative_identity:
            return ""
        top = max(self.narrative_identity, key=lambda x: x.get("kekuatan", 0.0))
        return f"aku orang yang {top['klaim']}"

    def last_thought(self, n: int = 1) -> List[str]:
        return [x.get("kalimat", "") for x in self.self_talk[-n:]]

    # ==================================================================
    # 3) AUTOBIOGRAPHICAL SELF & MENTAL TIME TRAVEL
    # ==================================================================
    def tandai_core_memory(self, teks: Any, klaim: Optional[str] = None,
                           bobot: float = 1.0,
                           episode: Optional[Mapping[str, Any]] = None
                           ) -> Dict[str, Any]:
        """Jadikan sebuah momen sebagai pilar identitas (core memory).

        Aturan khusus yang membedakannya dari episode "penting" biasa:
        (1) tidak pernah di-prune; (2) salience tinggi sehingga sering muncul
        di `_candidates()`; (3) mengikat klaim identitas; (4) menaikkan
        `affective_trust_cap` khusus untuk signature momen itu sehingga ia
        memfilter interpretasi pengalaman baru. Inilah titik balik, bukan
        sekadar titik di kurva.
        """
        if not self.enabled("autobiography") and not self.enabled("inner_speech"):
            return {}
        teks_s = str(teks if teks is not None else
                     (episode or {}).get("ringkas", ""))[:120]
        entri = {
            "tick": self._tick(), "ringkas": teks_s,
            "tag": (episode or {}).get("tag") or self._focus_tag,
            "klaim": str(klaim)[:60] if klaim else None,
            "bobot": jepit(float(bobot), 0.0, 2.0),
            "emosi": self._top_emotion(),
        }
        self.core_memory.append(entri)
        cap = int(self._p("kesadaran_core_max"))
        if cap > 0 and len(self.core_memory) > cap:
            # pilar tertua dengan bobot terendah boleh tergantikan
            self.core_memory.sort(key=lambda x: (float(x.get("bobot", 1.0)),
                                                 int(x.get("tick", 0))))
            self.core_memory = self.core_memory[-cap:]
        # pastikan ada episode timeline yang mewakili momen ini, lalu tandai
        # `core=True` agar tak pernah di-prune.
        target = next((it for it in self.timeline
                       if it.get("ringkas") == teks_s), None)
        if target is None:
            self._remember_episode({"content": teks_s, "tag": entri["tag"],
                                    "salience": 0.9, "kind": "core"},
                                   penting=True)
            target = next((it for it in reversed(self.timeline)
                           if it.get("ringkas") == teks_s), None)
        if target is not None:
            target["core"] = True
        # ikat klaim identitas
        if klaim:
            self._refresh_identity({f"pernah {str(klaim)[:40]}": 0.6 * entri["bobot"]})
        # filter interpretasi: cap kepercayaan naik untuk signature momen ini
        nur = getattr(self.naluri, "nurani", None)
        if nur is not None and hasattr(nur, "tandai_core"):
            try:
                entri["signature"] = nur.tandai_core(teks_s)["signature"]
            except Exception as _galat_diagnostik_7:
                _diag.catat('naluri.Kesadaran.tandai_core_memory', "galat pada jalur fallback", galat=_galat_diagnostik_7, jalur=7)
                pass
        return dict(entri)

    def core_memory_state(self) -> Dict[str, Any]:
        return {"n": len(self.core_memory),
                "pilar": [dict(x) for x in self.core_memory]}

    def _remember_episode(self, ev: Mapping[str, Any], penting: bool = False) -> None:
        if not self.enabled("autobiography"):
            return
        item = {
            "tick": self._tick(), "ringkas": str(ev.get("content", ""))[:120],
            "tag": ev.get("tag"), "kind": ev.get("kind"),
            "salience": round(float(ev.get("salience", 0.0)), 3),
            "penting": bool(penting),
            "emosi": self._top_emotion(),
        }
        self.timeline.append(item)
        cap = int(self._p("kesadaran_timeline_max"))
        if cap > 0 and len(self.timeline) > cap:
            # eviksi: CORE MEMORY tak pernah dibuang; penting & salience tinggi
            # bertahan lebih lama.
            ranked = sorted(
                self.timeline,
                key=lambda x: (bool(x.get("core", False)),
                               bool(x.get("penting", False)),
                               float(x.get("salience", 0.0)),
                               int(x.get("tick", 0))),
                reverse=True)[:cap]
            ranked.sort(key=lambda x: int(x.get("tick", 0)))
            self.timeline = ranked
        self._update_chapter(item)

    def _update_chapter(self, item: Mapping[str, Any]) -> None:
        kind = item.get("kind")
        batas = kind in ("mortality", "grief", "sosial", "ignition", "core")
        if self._chapter_open is None or batas:
            if self._chapter_open is not None:
                self._chapter_open["tutup"] = self._tick()
                self.chapters.append(self._chapter_open)
                if len(self.chapters) > int(self._p("kesadaran_chapters_max")):
                    self.chapters = self.chapters[-int(self._p("kesadaran_chapters_max")):]
            label = self._chapter_label(item)
            self._chapter_open = {"buka": self._tick(), "label": label,
                                  "tutup": None,
                                  "fase": str(getattr(self.naluri, "stage", ""))}

    def _chapter_label(self, item: Mapping[str, Any]) -> str:
        kind = item.get("kind")
        if kind == "grief":
            return "setelah kehilangan itu"
        if kind == "mortality":
            return "sejak aku sadar aku bisa mati"
        if kind == "sosial":
            return "sejak aku bertemu dia"
        if item.get("penting"):
            return f"setelah {str(item.get('ringkas', 'kejadian itu'))[:32]}"
        return f"babak di sekitar tick {self._tick()}"

    def life_chapters(self) -> List[Dict[str, Any]]:
        """Babak hidup: 'sebelum aku bertemu Player', 'setelah kejadian itu'."""
        out = [dict(c) for c in self.chapters]
        if self._chapter_open is not None:
            out.append(dict(self._chapter_open))
        return out

    def future_simulation(self, skenario: Optional[str] = None,
                          horizon: int = 24) -> Dict[str, Any]:
        """Bayangkan skenario masa depan (bukan sekadar prediksi skor)."""
        if not self.enabled("autobiography"):
            return {}
        if skenario is None:
            goals = getattr(self.naluri, "goals", []) or []
            skenario = (getattr(goals[0], "scenario", None)
                        or (f"aku {getattr(goals[0], 'drive', 'melanjutkan')}"
                            if goals else "aku melanjutkan hari-hariku"))
        batas_tubuh = self.constrain_imagination(str(skenario), mode="auto")
        if not batas_tubuh.get("allowed", True):
            # Cabang tidak dibangun: ini batas perspektif bertubuh, bukan
            # rendahnya salience atau kekurangan konten imajinasi.
            return {"tick": self._tick(), "skenario": str(skenario)[:160],
                    "dibatasi_tubuh": True, "bisa_dibayangkan": False,
                    "batas_tubuh": batas_tubuh,
                    "emosi_antisipatif": {}}
        lv = self._levels()
        # proyeksi kasar: drive terburuk membaik, ketegangan menurun
        proyeksi = {d: round(_kclip(lv.get(d, 0.0) + 0.15 * (1 if lv.get(d, 0.0) < 0 else -1),
                                     -1.0, 1.0), 3) for d in DRIVES}
        entry = {"tick": self._tick(), "skenario": str(skenario)[:160],
                 "horizon": int(horizon), "proyeksi": proyeksi,
                 "perspektif_tubuh": self.body_locus_state(),
                 "emosi_antisipatif": self._anticipatory_emotion(proyeksi)}
        self.future_sim.append(entry)
        if len(self.future_sim) > 16:
            self.future_sim = self.future_sim[-16:]
        return entry

    def _anticipatory_emotion(self, proyeksi: Mapping[str, float]) -> Dict[str, float]:
        lv = self._levels()
        delta = sum(proyeksi.get(d, 0.0) - lv.get(d, 0.0) for d in DRIVES)
        return {
            "harapan": round(max(0.0, delta) * 0.6, 3),
            "dread": round(max(0.0, -delta) * 0.6, 3),
        }

    def counterfactual(self, action: str, hasil_nyata: float,
                       hasil_alternatif: float) -> Dict[str, Any]:
        """Emosi kontrafaktual: penyesalan, kelegaan, kekecewaan."""
        if not self.enabled("autobiography"):
            return {}
        selisih = float(hasil_alternatif) - float(hasil_nyata)
        em = {"penyesalan": 0.0, "kelegaan": 0.0, "kekecewaan": 0.0}
        if selisih > 0.05:
            em["penyesalan"] = min(1.0, selisih * 1.2)
        elif selisih < -0.05:
            em["kelegaan"] = min(1.0, -selisih * 1.2)
        if hasil_nyata < 0 and selisih <= 0.05:
            em["kekecewaan"] = min(1.0, abs(hasil_nyata))
        for k, v in em.items():
            self.counterfactual_emotions[k] = max(
                self.counterfactual_emotions.get(k, 0.0), v)
        entry = {"tick": self._tick(), "aksi": str(action)[:80],
                 "nyata": round(float(hasil_nyata), 3),
                 "alternatif": round(float(hasil_alternatif), 3),
                 "emosi": {k: round(v, 3) for k, v in em.items() if v > 0}}
        self._counterfactual_log.append(entry)
        if len(self._counterfactual_log) > 32:
            self._counterfactual_log = self._counterfactual_log[-32:]
        return entry

    def mental_time_travel(self, arah: str = "masa_lalu") -> str:
        """Narasi perjalanan mental: mengingat masa lalu / membayangkan depan."""
        if arah == "masa_depan":
            if self.future_sim:
                return f"aku membayangkan {self.future_sim[-1]['skenario'][:80]}"
            return "aku membayangkan hari esok"
        if self.timeline:
            return f"aku ingat {self.timeline[-1]['ringkas'][:80]}"
        return "aku tidak ingat banyak"

    # ==================================================================
    # 4) SENSE OF AGENCY & BODY OWNERSHIP
    # ==================================================================
    def act(self, action: str, predicted: float = 0.0) -> Dict[str, Any]:
        """Catat aksi yang DIRENCANAKAN; hasil nyata menyusul via `feedback`."""
        return {"action": str(action)[:80], "predicted": _kclip(predicted),
                "tick": self._tick()}

    def feedback(self, rencana: Mapping[str, Any], actual: float) -> Dict[str, Any]:
        """Bandingkan prediksi hasil aksi vs kenyataan → rasa agensi."""
        if not self.enabled("agency"):
            return {}
        pred = _kclip(rencana.get("predicted", 0.0))
        mism = abs(pred - _kclip(actual))
        lr = self._p("kesadaran_agency_lr")
        # mismatch besar → agensi turun ("bukan aku yang melakukannya")
        target = _kclip(1.0 - mism * 1.5, 0.0, 1.0)
        self.agency = _kclip(self.agency + lr * (target - self.agency), 0.0, 1.0)
        # effort: usaha naik bila mismatch & drive energi rendah
        energi = self._levels().get("energi", 0.0)
        self.effort = _kclip(
            self.effort + self._p("kesadaran_effort_gain") * (mism - 0.1)
            + 0.1 * max(0.0, -energi), 0.0, 1.0)
        entry = {"tick": self._tick(), "aksi": str(rencana.get("action", ""))[:80],
                 "prediksi": round(pred, 3), "nyata": round(_kclip(actual), 3),
                 "agency": round(self.agency, 3), "effort": round(self.effort, 3),
                 "asing": self.agency < 0.3}
        self._agency_log.append(entry)
        if len(self._agency_log) > 32:
            self._agency_log = self._agency_log[-32:]
        return entry

    def body_ownership(self, bagian: str = "tubuh", sinyal: float = 0.5) -> float:
        """Rasa memiliki tubuh; sinyal = konsistensi umpan balik tubuh."""
        if not self.enabled("agency"):
            return self.ownership
        lr = self._p("kesadaran_ownership_lr")
        target = _kclip(sinyal, 0.0, 1.0)
        self.ownership = _kclip(self.ownership + lr * (target - self.ownership),
                                0.0, 1.0)
        self._body_locus["ownership"] = self.ownership
        return self.ownership

    def update_body_locus(self, position: Any = None,
                          orientation: Optional[float] = None,
                          sensory_horizon: Optional[float] = None
                          ) -> Dict[str, Any]:
        """Perbarui pose tubuh yang dialami; anchor identitas tidak dapat diganti."""
        if position is not None:
            raw = position
            if isinstance(raw, Mapping):
                raw = [raw.get(k, 0.0) for k in ("x", "y", "z")]
            try:
                coords = [float(x) for x in list(raw)[:3]]
                while len(coords) < 3:
                    coords.append(0.0)
                if all(math.isfinite(x) for x in coords):
                    self._body_locus["position"] = coords
            except (TypeError, ValueError):
                pass
        if orientation is not None:
            try:
                value = float(orientation)
                if math.isfinite(value):
                    self._body_locus["orientation"] = value % 360.0
            except (TypeError, ValueError):
                pass
        if sensory_horizon is not None:
            try:
                self._body_locus["sensory_horizon"] = max(
                    0.0, min(1.0e6, float(sensory_horizon)))
            except (TypeError, ValueError):
                pass
        self._body_locus["ownership"] = self.ownership
        self._body_locus["singular"] = True
        self._body_locus["viewpoint"] = "egosentris"
        return self.body_locus_state()

    def body_locus_state(self) -> Dict[str, Any]:
        """State lokus tubuh tunggal, bukan sekadar daftar sensasi tubuh."""
        return {"anchor": str(self._body_locus.get("anchor", "tubuh:anonim:0")),
                "singular": True, "can_exchange": False,
                "viewpoint": "egosentris",
                "position": (list(self._body_locus.get("position"))
                             if self._body_locus.get("position") is not None else None),
                "orientation": float(self._body_locus.get("orientation", 0.0)),
                "sensory_horizon": float(self._body_locus.get(
                    "sensory_horizon", 1.0)),
                "ownership": round(float(self.ownership), 4),
                "constraints": int(len(self._body_imagination_log))}

    def constrain_imagination(self, scenario: Any = "", target: Any = None,
                              mode: str = "auto",
                              position: Any = None) -> Dict[str, Any]:
        """Batasi pertukaran sudut pandang berdasarkan satu tubuh spesifik.

        NPC masih bisa memodelkan orang lain dari lokusnya sendiri. Yang tidak
        dapat dilakukan adalah *menjadi* tubuh lain atau mengindra dari tempat
        yang tidak dapat dicapai tubuhnya.
        """
        teks = str(scenario or "")[:200]
        low = teks.lower()
        mode_norm = str(mode or "auto").strip().lower().replace("-", "_")
        kata_tubuh = ("tubuh", "badan", "menempati", "bertukar tubuh",
                      "berada di tubuh", "merasakan sebagai", "berpikir sebagai")
        m_menjadi = re.search(
            r"\b(?:menjadi|menempati|bertukar|berada di tubuh)\s+(?:tubuh\s+)?([\wÀ-ÿ]+)",
            low, flags=re.UNICODE)
        inferred_target = m_menjadi.group(1) if m_menjadi else None
        target_name = str(target if target is not None else
                          (inferred_target or "")).strip()
        self_name = self._nama().strip().lower()
        self_aliases = {"aku", "saya", "diriku", "diri sendiri", "myself",
                        "self", self_name}
        other = bool(target_name and target_name.lower() not in self_aliases)
        mode_inhabit = mode_norm in {
            "inhabit", "menjadi", "first_person", "orang_pertama",
            "body_swap", "tubuh_lain", "as", "merasakan", "menempati"}
        request_to_become = bool(m_menjadi and
                                 re.search(r"\b(?:aku|saya|diriku)\b", low))
        request_body_swap = ("bertukar tubuh" in low or "menempati tubuh" in low
                             or "berada di tubuh" in low)
        if mode_norm == "auto":
            mode_inhabit = request_to_become or request_body_swap
        body_bound = (mode_inhabit and (other or not target_name))
        sebab = ""
        if body_bound:
            sebab = "tubuh ini adalah lokus perspektif yang tak dapat dipertukarkan"
        # Batas spasial hanya berlaku pada permintaan memakai indra tubuh, bukan
        # pada pemodelan sosial abstrak tentang isi pikiran orang lain.
        if not sebab and position is not None and any(k in low for k in kata_tubuh):
            try:
                raw = position
                if isinstance(raw, Mapping):
                    raw = [raw.get(k, 0.0) for k in ("x", "y", "z")]
                dest = [float(x) for x in list(raw)[:3]]
                while len(dest) < 3:
                    dest.append(0.0)
                origin = self._body_locus.get("position")
                if origin is None:
                    sebab = "lokus tubuh belum memiliki akses sensoris ke posisi itu"
                else:
                    jarak = math.sqrt(sum((dest[i] - float(origin[i])) ** 2
                                          for i in range(3)))
                    if jarak > float(self._body_locus.get("sensory_horizon", 1.0)):
                        sebab = "posisi itu berada di luar jangkauan indrawi tubuh ini"
            except (TypeError, ValueError, IndexError):
                pass
        allowed = not bool(sebab)
        result = {"allowed": allowed, "bisa_dibayangkan": allowed,
                  "target": target_name or None,
                  "mode": mode_norm,
                  "perspektif": ("tubuh_sendiri" if allowed else "terkunci_pada_tubuh_ini"),
                  "lokus": str(self._body_locus.get("anchor", "")),
                  "only_from_own_locus": True,
                  "rasa_asing": round((0.35 + 0.65 * self.ownership)
                                       if body_bound else 0.0, 3),
                  "sebab": sebab}
        if not allowed:
            self._body_imagination_log.append({
                "tick": self._tick(), "target": target_name[:40],
                "mode": mode_norm, "sebab": sebab[:100],
                "rasa_asing": result["rasa_asing"]})
            if len(self._body_imagination_log) > 64:
                self._body_imagination_log = self._body_imagination_log[-64:]
        return result

    def imagine_from_body(self, scenario: Any, target: Any = None,
                          mode: str = "inhabit",
                          position: Any = None) -> Dict[str, Any]:
        return self.constrain_imagination(scenario, target=target, mode=mode,
                                          position=position)

    # API Indonesia; kedua jalur memakai state constraint yang sama.
    bayangkan_dari_tubuh = imagine_from_body

    def agency_state(self) -> Dict[str, Any]:
        return {"aktif": self.enabled("agency"),
                "agency": round(self.agency, 3),
                "ownership": round(self.ownership, 3),
                "effort": round(self.effort, 3),
                "body_locus": self.body_locus_state(),
                "asing_terakhir": (self._agency_log[-1]["asing"]
                                   if self._agency_log else False)}

    # ==================================================================
    # 5) CONSCIOUS INTEROCEPTION & MORAL EMOTIONS
    # ==================================================================
    def _update_felt(self, steps: int) -> None:
        # SATU SUMBER KEBENARAN: bila NURANI juga menghitung interosepsi
        # (enable_felt_consciousness), pakai hasilnya apa adanya. Tanpa ini
        # Kesadaran.felt dan Nurani.felt_state menyimpang (mis. faktor 'sesak'
        # 0.9 vs 1.0, laju 0.15*steps vs felt_lr) sehingga NPC bisa melaporkan
        # dua "rasa tubuh" yang berbeda untuk keadaan yang sama.
        nur = getattr(self.naluri, "nurani", None)
        pakai_nurani = bool(
            nur is not None
            and getattr(nur, "felt_state", None)
            # Hanya bila NURANI benar-benar memperbarui felt pada tick INI
            # (update_felt ter-gate oleh introspeksi + LOD). Tanpa stempel
            # tick, delegasi akan membekukan Kesadaran.felt pada nilai basi.
            and getattr(nur, "_felt_tick", None) == self._tick()
        )
        if pakai_nurani:
            for k in FELT_STATES:
                self.felt[k] = _kclip(float(nur.felt_state.get(k, 0.0)), 0.0, 1.0)
        else:
            lv = self._levels()
            urg = getattr(self.naluri, "urgency", {}) or {}
            arousal = 0.0
            try:
                arousal = float(getattr(self.naluri.mood(), "arousal", 0.0))
            except Exception as _galat_diagnostik_8:
                _diag.catat('naluri.Kesadaran._update_felt', "galat pada jalur fallback", galat=_galat_diagnostik_8, jalur=8)
                arousal = 0.0
            target = {
                "lelah": max(0.0, -lv.get("energi", 0.0)),
                "lapar": max(0.0, -lv.get("energi", 0.0)) * 0.7,
                "sesak": max(0.0, -lv.get("keamanan", 0.0)) * 0.9,
                "jantung": max(0.0, arousal) * 0.8 + max(0.0, -lv.get("keamanan", 0.0)) * 0.5,
                "tegang": max(0.0, float(urg.get("keamanan", 0.0))) * 0.6,
                "mual": max(0.0, -lv.get("koherensi", 0.0)) * 0.7,
                "nyeri": max(0.0, -lv.get("keamanan", 0.0)) * 0.4,
                "ringan": max(0.0, lv.get("energi", 0.0)) * 0.4,
            }
            lr = jepit(0.15 * max(1, steps), 0.05, 1.0)
            for k in FELT_STATES:
                self.felt[k] = _kclip(
                    self.felt[k] + lr * (_kclip(target.get(k, 0.0), 0.0, 1.0) - self.felt[k]),
                    0.0, 1.0)
        # somatic marker: tubuh menandai nilai konteks (Damasio)
        top = None
        if self.felt:
            top = max(self.felt, key=lambda k: self.felt[k])
        if top and self.felt[top] > 0.3:
            self.somatic_markers.append({
                "tick": self._tick(), "tag": self._somatic_tag(top),
                "valensi": -round(self.felt[top], 3), "sumber": top})
            cap = int(self._p("kesadaran_somatic_max"))
            if cap > 0 and len(self.somatic_markers) > cap:
                self.somatic_markers = self.somatic_markers[-cap:]

    @staticmethod
    def _somatic_tag(felt: str) -> str:
        return {"sesak": "keamanan", "jantung": "keamanan", "tegang": "keamanan",
                "nyeri": "keamanan", "lelah": "energi", "lapar": "energi",
                "mual": "koherensi", "ringan": "energi"}.get(felt, "koherensi")

    def moral_emotion(self, emosi: str, intensitas: float = 0.5,
                      sebab: str = "") -> float:
        """Suntik emosi moral (bersalah, malu, bangga, cemburu, iri, syukur...)."""
        if not self.enabled("felt_state"):
            return 0.0
        key = MORAL_ALIASES.get(str(emosi).lower(), str(emosi).lower())
        if key not in self.moral:
            return 0.0
        self.moral[key] = _kclip(
            self.moral[key] + self._p("kesadaran_moral_lr") * float(intensitas),
            0.0, 1.0)
        # beberapa emosi moral memengaruhi afek inti
        if key == "bersalah":
            self._bias_emosi("sedih", 0.3 * intensitas)
        elif key == "bangga":
            self._bias_emosi("senang", 0.4 * intensitas)
        elif key in ("cemburu", "iri"):
            self._bias_emosi("marah", 0.2 * intensitas)
        elif key == "syukur":
            self._bias_emosi("senang", 0.3 * intensitas)
        return self.moral[key]

    def epistemic_emotion(self, emosi: str, intensitas: float = 0.5,
                          sebab: str = "") -> float:
        """Rasa yang timbul dari mengetahui/tidak mengetahui, terpisah dari moral.

        Contoh: ``bingung`` memberi tekanan di dahi, ``penasaran`` membuat
        tubuh condong, ``lega`` melepaskan bahu, dan ``malu_tidak_tahu`` terasa
        hangat di wajah. Nilainya tidak ditulis ke ``moral`` atau emosi inti.
        """
        if not self.enabled("epistemic_emotions"):
            return 0.0
        nama = str(emosi or "").strip().lower()
        key = EPISTEMIC_ALIASES.get(nama, nama.replace(" ", "_"))
        if key not in self.epistemic_emotions:
            return 0.0
        amount = _kclip(intensitas, 0.0, 1.0)
        lr = jepit_01(self._p("kesadaran_epistemic_lr"))
        before = self.epistemic_emotions[key]
        self.epistemic_emotions[key] = _kclip(
            before + lr * amount * (1.0 - before), 0.0, 1.0)
        tekstur = {
            "bingung": {"dahi_mengerut": 0.65, "napas_tertahan": 0.16},
            "penasaran": {"tubuh_condong": 0.60, "dahi_mengerut": 0.12},
            "lega": {"dada_mengendur": 0.50, "bahu_rileks": 0.65},
            "malu_tidak_tahu": {"wajah_hangat": 0.68, "tubuh_condong": -0.18},
            "takjub": {"napas_tertahan": 0.52, "dahi_mengerut": 0.18},
            "frustrasi": {"rahang_tegang": 0.62, "dahi_mengerut": 0.35},
            "yakin": {"dada_mengendur": 0.18, "bahu_rileks": 0.22},
            "bosan": {"tubuh_condong": -0.25, "dahi_mengerut": 0.10},
        }.get(key, {})
        for bagian, bobot in tekstur.items():
            if bobot >= 0.0:
                self.epistemic_body[bagian] = _kclip(
                    self.epistemic_body.get(bagian, 0.0) + amount * bobot,
                    0.0, 1.0)
            else:
                self.epistemic_body[bagian] = _kclip(
                    self.epistemic_body.get(bagian, 0.0) + amount * bobot,
                    0.0, 1.0)
        item = {"tick": self._tick(), "emosi": key,
                "intensitas": round(amount, 3),
                "nilai": round(self.epistemic_emotions[key], 3),
                "sebab": str(sebab or "")[:100]}
        self._epistemic_log.append(item)
        cap = max(1, int(self._p("kesadaran_epistemic_max")))
        self._epistemic_log = self._epistemic_log[-cap:]
        return self.epistemic_emotions[key]

    def _update_epistemic_from_state(self) -> None:
        """Drive epistemik dapat dirasakan tanpa menyamakan rasa dan fakta."""
        if not self.enabled("epistemic_emotions"):
            return
        try:
            penasaran = float(self.naluri.deficit("keingintahuan"))
        except Exception as _galat_diagnostik_9:
            _diag.catat('naluri.Kesadaran._update_epistemic_from_state', "galat pada jalur fallback", galat=_galat_diagnostik_9, jalur=9)
            penasaran = 0.0
        if penasaran > 0.12:
            self.epistemic_emotions["penasaran"] = max(
                self.epistemic_emotions["penasaran"],
                _kclip(penasaran * 0.55, 0.0, 0.8))
            self.epistemic_body["tubuh_condong"] = max(
                self.epistemic_body["tubuh_condong"],
                _kclip(penasaran * 0.35, 0.0, 0.6))
        if self.doubt > 0.25:
            self.epistemic_emotions["bingung"] = max(
                self.epistemic_emotions["bingung"],
                _kclip((self.doubt - 0.15) * 0.65, 0.0, 0.75))
            self.epistemic_body["dahi_mengerut"] = max(
                self.epistemic_body["dahi_mengerut"],
                _kclip((self.doubt - 0.1) * 0.55, 0.0, 0.7))

    def epistemic_emotion_state(self) -> Dict[str, Any]:
        aktif = {k: round(float(v), 3) for k, v in self.epistemic_emotions.items()
                 if float(v) > 0.03}
        dominan = max(self.epistemic_emotions,
                      key=lambda k: self.epistemic_emotions[k], default="")
        return {"aktif": self.enabled("epistemic_emotions"),
                "emosi": aktif,
                "dominan": (dominan if self.epistemic_emotions.get(dominan, 0.0) > 0.03
                            else None),
                "tekstur_tubuh": {k: round(float(v), 3)
                                   for k, v in self.epistemic_body.items()
                                   if float(v) > 0.03},
                "terakhir": (dict(self._epistemic_log[-1])
                             if self._epistemic_log else None)}

    def epistemic_report(self) -> Dict[str, Any]:
        st = self.epistemic_emotion_state()
        key = st.get("dominan")
        kalimat = ""
        if key:
            kalimat = {
                "bingung": "aku bingung; pikiranku mengerut mencari pola",
                "penasaran": "ada sesuatu yang ingin kupahami; tubuhku condong ke arahnya",
                "lega": "aku lega karena kini mulai tahu",
                "malu_tidak_tahu": "aku malu karena tidak tahu, dan sulit menatap lurus",
                "takjub": "aku terdiam, takjub pada hal yang baru kupahami",
                "frustrasi": "aku frustrasi karena jawabannya belum terbuka",
                "yakin": "aku merasa cukup yakin dengan yang kuketahui",
                "bosan": "pola ini terasa jenuh; aku ingin melakukan sesuatu yang berbeda",
            }.get(key, "")
        st["kalimat"] = kalimat
        return st

    def self_opacity(self, perasaan_dikenali: Optional[str] = None,
                     perasaan_laten: Optional[str] = None,
                     sebab_diyakini: Optional[str] = None,
                     sebab_laten: Optional[str] = None,
                     bukti: str = "") -> Dict[str, Any]:
        """Modelkan salah-baca perasaan dan tidak mengetahui sebabnya.

        ``perasaan_laten``/``sebab_laten`` adalah state untuk simulator, bukan
        sesuatu yang otomatis disadari agen. Dengan begitu ``merasa X padahal
        sebenarnya Y`` berbeda secara struktural dari ``tahu X, tidak tahu
        kenapa``; keduanya bukan sekadar skor error yang sama.
        """
        if not self.enabled("self_opacity"):
            return {"aktif": False}
        diakui = str(perasaan_dikenali or "").strip().lower()
        laten = str(perasaan_laten or "").strip().lower()
        if not laten:
            laten = self._top_emotion().lower()
        sebab_akui = str(sebab_diyakini or "").strip().lower()
        sebab_sebenarnya = str(sebab_laten or "").strip().lower()
        try:
            diakui = EMOSI_ALIASES.get(diakui, diakui)
            laten = EMOSI_ALIASES.get(laten, laten)
        except Exception as _galat_diagnostik_10:
            _diag.catat('naluri.Kesadaran.self_opacity', "galat pada jalur fallback", galat=_galat_diagnostik_10, jalur=10)
            pass
        mismatch = bool(diakui and laten and diakui != laten)
        cause_mismatch = bool(sebab_akui and sebab_sebenarnya
                              and sebab_akui != sebab_sebenarnya)
        cause_unknown = not sebab_akui
        state = self._self_opacity
        if mismatch:
            state["jumlah_ketidakcocokan"] = int(
                state.get("jumlah_ketidakcocokan", 0)) + 1
            state["ketidakcocokan"] = _kclip(
                float(state.get("ketidakcocokan", 0.0)) * 0.55 + 0.45, 0.0, 1.0)
            state["status"] = "salah_membaca_perasaan"
            kalimat = (f"Aku menyebutnya {diakui}, tetapi respons tubuhku terasa "
                       "tidak cocok; aku belum memahami apa yang sebenarnya berlangsung.")
            self.epistemic_emotion("bingung", 0.62,
                                   "label perasaan dan sinyal afektif tidak cocok")
            if state["jumlah_ketidakcocokan"] >= 2:
                self.epistemic_emotion("malu_tidak_tahu", 0.22,
                                       "berulang kali salah mengenali diri")
        elif not diakui and laten:
            state["status"] = "perasaan_tidak_dikenali"
            kalimat = "Aku tidak tahu apa yang kurasakan; yang kutahu hanya ada sesuatu yang bergerak di dalamku."
            self.epistemic_emotion("bingung", 0.48, "perasaan belum dapat dinamai")
        elif cause_unknown or cause_mismatch:
            state["status"] = "sebab_perasaan_tidak_diketahui"
            kalimat = (f"Aku tahu aku merasa {diakui}, tapi aku tidak tahu kenapa."
                       if diakui else "Ada sesuatu yang kurasakan, tapi aku belum tahu sebabnya.")
            if cause_mismatch:
                kalimat = (f"Aku kira ini karena {sebab_akui}, tetapi ada sesuatu "
                           "yang tidak pas; aku belum memahami sebab sebenarnya.")
            self.epistemic_emotion("bingung", 0.35,
                                   "sebab perasaan tidak dapat diketahui")
        else:
            state["status"] = "jelas"
            kalimat = (f"Aku merasa {diakui}, dan aku cukup tahu apa sebabnya."
                       if diakui else "")
        state.update({"perasaan_dikenali": diakui,
                      "perasaan_laten": laten,
                      "sebab_diyakini": sebab_akui,
                      "sebab_laten": sebab_sebenarnya,
                      "ketidakjelasan_sebab": (0.75 if cause_unknown else
                                               0.65 if cause_mismatch else 0.0),
                      "kalimat": kalimat,
                      "tick": self._tick(),
                      "bukti": str(bukti or "")[:100],
                      "sadar_akan_ketidakcocokan": False if mismatch else True})
        item = {"tick": self._tick(), "status": state["status"],
                "perasaan_dikenali": diakui,
                "perasaan_laten": laten,
                "sebab_diyakini": sebab_akui,
                "sebab_laten": sebab_sebenarnya,
                "ketidakcocokan": round(float(state["ketidakcocokan"]), 3),
                "bukti": str(bukti or "")[:100]}
        self._self_opacity_log.append(item)
        cap = max(1, int(self._p("kesadaran_self_opacity_max")))
        self._self_opacity_log = self._self_opacity_log[-cap:]
        if self.enabled("global_workspace") and kalimat:
            self.submit(kalimat, salience=0.62, tag="opasitas_diri",
                        source="introspeksi", kind="self_opacity",
                        detail={"bukan_galat_tunggal": True})
        return self.self_opacity_state(include_private=True)

    model_self_opacity = self_opacity

    def self_opacity_state(self, include_private: bool = False) -> Dict[str, Any]:
        state = copy.deepcopy(self._self_opacity)
        history = [copy.deepcopy(x) for x in self._self_opacity_log[-6:]]
        if not include_private:
            state.pop("perasaan_laten", None)
            state.pop("sebab_laten", None)
            # Riwayat mengikuti batas privasi yang sama dengan state kini.
            private = {"perasaan_laten", "sebab_laten", "perasaan_sebenarnya",
                       "sebab_sebenarnya", "label_ground_truth"}
            history = [{k: v for k, v in item.items() if k not in private}
                       for item in history]
        return {"aktif": self.enabled("self_opacity"), **state,
                "riwayat": history}

    def _bias_emosi(self, emosi: str, jumlah: float) -> None:
        if not self.enabled("felt_state"):
            return
        em = getattr(self.naluri, "emosi", None)
        if isinstance(em, dict) and emosi in em:
            em[emosi] = _kclip(em[emosi] + jumlah, 0.0, 1.0)

    def felt_report(self) -> Dict[str, Any]:
        aktif = [(k, round(v, 3)) for k, v in self.felt.items() if v > 0.15]
        moral = [(k, round(v, 3)) for k, v in self.moral.items() if v > 0.15]
        kalimat = ""
        if aktif:
            kalimat = self._felt_phrase(max(aktif, key=lambda x: x[1])[0])
        if moral:
            kalimat += (("; " if kalimat else "") +
                        f"aku merasa {max(moral, key=lambda x: x[1])[0]}")
        epistemik = self.epistemic_report()
        if epistemik.get("kalimat"):
            kalimat += (("; " if kalimat else "") + epistemik["kalimat"])
        opasitas = self.self_opacity_state()
        if opasitas.get("kalimat"):
            kalimat += (("; " if kalimat else "") + str(opasitas["kalimat"]))
        return {"aktif": self.enabled("felt_state"), "felt": dict(aktif),
                "moral": dict(moral), "epistemik": epistemik,
                "opasitas_diri": opasitas, "kalimat": kalimat}

    # ==================================================================
    # 6) REALITY MONITORING & METACOGNITIVE DOUBT
    # ==================================================================
    def classify_reality(self, item: Mapping[str, Any]) -> str:
        """Tentukan sumber pengalaman: persepsi / ingatan / imajinasi / mimpi."""
        kind = str(item.get("kind", ""))
        if kind in ("dream", "mimpi"):
            return "mimpi"
        if kind in ("goal", "future", "imajinasi"):
            return "imajinasi"
        if kind in ("wm", "memori", "ingatan", "episodic"):
            return "ingatan"
        if kind in ("felt", "drive", "emosi", "grief"):
            return "persepsi"
        return "persepsi"

    def reality_check(self, item: Mapping[str, Any]) -> Dict[str, Any]:
        """Monitoring realitas + source memory; kadang sumber tertukar."""
        if not self.enabled("reality_monitoring"):
            return {}
        src = self.classify_reality(item)
        # derau sumber: mimpi/imajinasi sesekali terasa seperti ingatan
        keyakinan = 0.7
        if src in ("mimpi", "imajinasi"):
            try:
                if self._rng.random() < 0.15:
                    src = "ingatan"
                    keyakinan = 0.4
            except Exception as _galat_diagnostik_11:
                _diag.catat('naluri.Kesadaran.reality_check', "galat pada jalur fallback", galat=_galat_diagnostik_11, jalur=11)
                pass
        self.reality[src] = min(1.0, self.reality.get(src, 0.0) + 0.1)
        entry = {"tick": self._tick(), "sumber": src,
                 "isi": str(item.get("content", ""))[:80],
                 "keyakinan": round(keyakinan, 3)}
        self.source_log.append(entry)
        if len(self.source_log) > 48:
            self.source_log = self.source_log[-48:]
        if keyakinan < 0.55:
            self.epistemic_emotion("bingung", 0.35,
                                   "sumber pengalaman terasa kabur")
        return entry

    def source_memory(self, tentang: Optional[str] = None) -> Dict[str, Any]:
        """'Aku tahu ini dari mana?' — asal-usul keyakinan terakhir."""
        if not self.enabled("reality_monitoring"):
            return {}
        if tentang:
            hit = next((e for e in reversed(self.source_log)
                        if tentang.lower() in e.get("isi", "").lower()), None)
            if hit:
                return hit
        return self.source_log[-1] if self.source_log else {}

    def metacognitive_doubt(self, tingkat: Optional[float] = None) -> float:
        """'Aku tidak yakin', 'mungkin aku salah'."""
        if not self.enabled("reality_monitoring"):
            return 0.0
        sebelumnya = self.doubt
        if tingkat is not None:
            self.doubt = _kclip(self.doubt + self._p("kesadaran_doubt_lr") *
                                (float(tingkat) - self.doubt), 0.0, 1.0)
        else:
            # keraguan tumbuh dari konflik tujuan + rendahnya kepercayaan
            try:
                konf = getattr(self.naluri.nurani, "kepercayaan_global", 0.5)
            except Exception as _galat_diagnostik_12:
                _diag.catat('naluri.Kesadaran.metacognitive_doubt', "galat pada jalur fallback", galat=_galat_diagnostik_12, jalur=12)
                konf = 0.5
            self.doubt = _kclip(self.doubt + 0.01 * (0.5 - float(konf)), 0.0, 1.0)
        delta = self.doubt - sebelumnya
        if delta > 0.05:
            self.epistemic_emotion("bingung", min(1.0, delta * 2.5),
                                   "keyakinan epistemik melemah")
        elif delta < -0.05:
            self.epistemic_emotion("lega", min(1.0, abs(delta) * 2.2),
                                   "ketidakpastian mereda")
        return self.doubt

    def confabulate(self, celah: str = "") -> Dict[str, Any]:
        """Isi celah ingatan dengan cerita salah tapi dipercaya."""
        if not self.enabled("reality_monitoring"):
            return {}
        cerita = self._plausible_story(celah)
        entry = {"tick": self._tick(), "celah": str(celah)[:80],
                 "cerita": cerita, "dipercaya": True}
        self.confabulations.append(entry)
        cap = int(self._p("kesadaran_confab_max"))
        if cap > 0 and len(self.confabulations) > cap:
            self.confabulations = self.confabulations[-cap:]
        return entry

    def _plausible_story(self, celah: str) -> str:
        potongan = [
            "aku yakin dia yang melakukannya, meski aku tidak benar-benar ingat",
            "aku rasa itu terjadi di suatu pagi, tapi detailnya kabur",
            "aku ingat pernah di sini sebelumnya — sebenarnya aku tidak",
            "mungkin itu mimpi, tapi terasa seperti sungguh terjadi",
        ]
        dasar = f" tentang {celah[:40]}." if celah else ""
        try:
            return self._rng.choice(potongan) + dasar
        except Exception as _galat_diagnostik_13:
            _diag.catat('naluri.Kesadaran._plausible_story', "galat pada jalur fallback", galat=_galat_diagnostik_13, jalur=13)
            return potongan[0] + dasar

    def reality_report(self) -> Dict[str, Any]:
        return {"aktif": self.enabled("reality_monitoring"),
                "distribusi": {k: round(v, 3) for k, v in self.reality.items()},
                "sumber_terakhir": (self.source_log[-1] if self.source_log else None),
                "doubt": round(self.doubt, 3),
                "keraguan_terakhir": ("aku tidak yakin" if self.doubt > 0.5
                                      else ("mungkin aku salah" if self.doubt > 0.25
                                            else "")),
                "konfabulasi": len(self.confabulations)}

    # ==================================================================
    # 7) ATTENTION — inattentional/change blindness, blink
    # ==================================================================
    def attention_limits(self) -> Dict[str, Any]:
        return {"aktif": self.enabled("attention_limits"),
                "fokus": self._focus_tag,
                "blink_sisa": max(0, self._blink_until - self._tick()),
                "blindspots": len(self.blindness_log),
                "terakhir": (self.blindness_log[-1] if self.blindness_log else None)}

    # ==================================================================
    # 8) SOCIAL COGNITION & SECOND-PERSON LOOP
    # ==================================================================
    @staticmethod
    def _eid(ent: Any) -> str:
        return str(getattr(ent, "name", ent))

    def joint_attention(self, ent: Any, objek: str) -> Dict[str, Any]:
        """Atensi bersama: 'kita berdua sedang melihat hal yang sama'."""
        if not self.enabled("second_person"):
            return {}
        eid = self._eid(ent)
        slot = self._joint_attention.setdefault(eid, {"n": 0, "objek": ""})
        slot["n"] = int(slot.get("n", 0)) + 1
        slot["objek"] = str(objek)[:80]
        slot["tick"] = self._tick()
        self._shared_history.append(f"kita melihat {str(objek)[:48]}")
        if len(self._shared_history) > 24:
            self._shared_history = self._shared_history[-24:]
        return dict(slot)

    def recursive_tom(self, ent: Any, keyakinan: str, nilai: float) -> Dict[str, Any]:
        """Teori pikiran rekursif: 'aku tahu kamu tahu aku...'."""
        if not self.enabled("second_person"):
            return {}
        eid = self._eid(ent)
        slot = self._recursive_tom.setdefault(eid, {})
        slot[str(keyakinan)[:60]] = round(_kclip(nilai, -1.0, 1.0), 3)
        return dict(slot)

    def commit(self, ent: Any, isi: str, utang: bool = False) -> Dict[str, Any]:
        """Janji / utang budi / tanggung jawab."""
        if not self.enabled("second_person"):
            return {}
        eid = self._eid(ent)
        item = {"tick": self._tick(), "entitas": eid, "isi": str(isi)[:120],
                "jenis": "utang" if utang else "janji", "status": "aktif"}
        self.commitments.append(item)
        if len(self.commitments) > int(self._p("kesadaran_commit_max")):
            self.commitments = self.commitments[-int(self._p("kesadaran_commit_max")):]
        # FITUR 4: utang budi/janji menambah beban emosional di relasi.
        nur = getattr(self.naluri, "nurani", None)
        if nur is not None and hasattr(nur, "tambah_utang"):
            try:
                nur.tambah_utang(eid, str(isi)[:100], bobot=1.0,
                                 jenis=item["jenis"], tick=self._tick())
            except Exception as _galat_diagnostik_14:
                _diag.catat('naluri.Kesadaran.commit', "galat pada jalur fallback", galat=_galat_diagnostik_14, jalur=14)
                pass
        return dict(item)

    def betray(self, ent: Any, sebab: str = "") -> Dict[str, Any]:
        """Pengkhianatan: janji dilanggar; kepercayaan jatuh; identitas terbentuk."""
        if not self.enabled("second_person"):
            return {}
        eid = self._eid(ent)
        # FITUR 4: janji yang dilanggar MENUMPUK sebagai utang emosional.
        nur = getattr(self.naluri, "nurani", None)
        for c in self.commitments:
            if c.get("entitas") == eid and c.get("status") == "aktif":
                c["status"] = "dilanggar"
                if nur is not None and hasattr(nur, "tambah_utang"):
                    try:
                        nur.tambah_utang(eid, str(c.get("isi", ""))[:100],
                                         bobot=1.0, jenis="dilanggar",
                                         tick=self._tick())
                    except Exception as _galat_diagnostik_15:
                        _diag.catat('naluri.Kesadaran.betray', "galat pada jalur fallback", galat=_galat_diagnostik_15, jalur=15)
                        pass
        item = {"tick": self._tick(), "entitas": eid, "sebab": str(sebab)[:100]}
        try:
            self.naluri.nurani.interact(eid, muatan=-0.6, drive="keamanan")
        except Exception as _galat_diagnostik_16:
            _diag.catat('naluri.Kesadaran.betray', "galat pada jalur fallback", galat=_galat_diagnostik_16, jalur=16)
            pass
        self._bias_emosi("marah", 0.4)
        self.moral_emotion("kesepian", 0.2, sebab)
        self._refresh_identity({"pernah dikhianati": 0.5})
        return item

    def forgive(self, ent: Any, alasan: str = "") -> Dict[str, Any]:
        """Memaafkan: memperbaiki relasi, melepas utang."""
        if not self.enabled("second_person"):
            return {}
        eid = self._eid(ent)
        for c in self.commitments:
            if c.get("entitas") == eid:
                if c.get("status") == "dilanggar":
                    c["status"] = "dimaafkan"
        # FITUR 4: memaafkan membayar utang emosional — beban berkurang.
        nur = getattr(self.naluri, "nurani", None)
        if nur is not None and hasattr(nur, "bayar_utang"):
            try:
                nur.bayar_utang(eid, isi=None, tick=self._tick())
            except Exception as _galat_diagnostik_17:
                _diag.catat('naluri.Kesadaran.forgive', "galat pada jalur fallback", galat=_galat_diagnostik_17, jalur=17)
                pass
        try:
            self.naluri.nurani.interact(eid, muatan=+0.3, drive="afiliasi")
        except Exception as _galat_diagnostik_18:
            _diag.catat('naluri.Kesadaran.forgive', "galat pada jalur fallback", galat=_galat_diagnostik_18, jalur=18)
            pass
        self.moral_emotion("haru", 0.4, alasan)
        return {"tick": self._tick(), "entitas": eid, "alasan": str(alasan)[:100]}

    def gossip(self, tentang: Any, isi: str, kepada: Any = None) -> Dict[str, Any]:
        """NPC membicarakan Player/NPC lain — kesadaran relasional."""
        if not self.enabled("second_person"):
            return {}
        item = {"tick": self._tick(), "tentang": self._eid(tentang),
                "kepada": self._eid(kepada) if kepada is not None else None,
                "isi": str(isi)[:140]}
        self.gossip_log.append(item)
        if len(self.gossip_log) > int(self._p("kesadaran_gossip_max")):
            self.gossip_log = self.gossip_log[-int(self._p("kesadaran_gossip_max")):]
        return dict(item)

    def tandai_alarm_palsu(self, sumber: Any, konten: str) -> Dict[str, Any]:
        """Persepsi menandai rumor dari sumber tak tepercaya sebagai alarm palsu.

        Dipakai fitur 1: gosip dari NPC yang dikenal suka berbohong tidak
        dipercaya bulat — dicatat sebagai sinyal palsu, bukan bukti.
        """
        entri = {"tick": self._tick(), "sumber": "alarm_palsu",
                 "isi": f"dari {sumber}: {str(konten)[:60]}",
                 "keyakinan": 0.1}
        self.source_log.append(entri)
        if len(self.source_log) > 48:
            self.source_log = self.source_log[-48:]
        self.reality["alarm_palsu"] = min(1.0, self.reality.get("alarm_palsu", 0.0)
                                          + 0.1)
        return entri

    def terima_bukti(self, bukti: str, sumber: Any = "",
                     kekuatan: float = 0.7) -> Dict[str, Any]:
        """Terima bukti keras: selesaikan disonansi secara real-time.

        Bukan sekadar [Persuade]/[Intimidate]: bukti yang dihadapkan langsung
        menurunkan ketegangan keyakinan yang bertentangan, melunakkan bias
        konfirmasi, dan memaafkan pihak yang dituduh. Mengembalikan laporan
        apa yang berubah — agar game bisa menampilkan efeknya seketika.
        """
        if not self.enabled("fallibility") and not self.enabled("second_person"):
            return {"aktif": False}
        s = str(sumber) if sumber is not None else ""
        k = jepit_01(float(kekuatan))
        dilunakkan: List[str] = []
        for key, slot in self.dissonance.items():
            if float(slot.get("tension", 0.0)) <= 0.0:
                continue
            slot["tension"] = _kclip(float(slot["tension"]) - k, 0.0, 1.0)
            if slot["tension"] <= 0.05:
                slot["diterima"] = True
                dilunakkan.append(key)
        if "konfirmasi" in self.biases:
            self.biases["konfirmasi"] = _kclip(self.biases["konfirmasi"]
                                               - 0.3 * k, 0.0, 1.0)
        self.doubt = _kclip(self.doubt - 0.2 * k, 0.0, 1.0)
        if s:
            try:
                self.forgive(s, alasan=f"bukti: {str(bukti)[:60]}")
            except Exception as _galat_diagnostik_19:
                _diag.catat('naluri.Kesadaran.terima_bukti', "galat pada jalur fallback", galat=_galat_diagnostik_19, jalur=19)
                pass
        entri = {"tick": self._tick(), "bukti": str(bukti)[:120],
                 "sumber": s, "kekuatan": round(k, 3),
                 "dilunakkan": dilunakkan}
        self._bukti_log.append(entri)
        if len(self._bukti_log) > 32:
            self._bukti_log = self._bukti_log[-32:]
        return dict(entri)

    def koreksi_ingatan(self, asli: str, benar: str,
                        sumber: Any = "") -> Dict[str, Any]:
        """Koreksi ingatan salah (gosip/konfabulasi) dengan kebenaran.

        Menandai konfabulasi & salah-ingat yang cocok sebagai `dikoreksi`,
        menurunkan keraguan, dan mengembalikan daftar yang diperbaiki.
        """
        a = str(asli)[:60].lower()
        b = str(benar)[:120]
        dikoreksi: List[str] = []
        for c in self.confabulations:
            teks = (str(c.get("celah", "")) + " " + str(c.get("cerita", ""))).lower()
            if a and a in teks:
                c["dikoreksi"] = True
                c["koreksi"] = b
                dikoreksi.append("konfabulasi")
        for bl in self.blindness_log:
            if bl.get("jenis") != "salah_ingat":
                continue
            teks = (str(bl.get("sebelum", "")) + " "
                    + str(bl.get("sesudah", ""))).lower()
            if a and a in teks:
                bl["dikoreksi"] = True
                bl["sesudah"] = b
                dikoreksi.append("salah_ingat")
        self.doubt = _kclip(self.doubt - 0.25, 0.0, 1.0)
        entri = {"tick": self._tick(), "asli": str(asli)[:80],
                 "benar": b, "sumber": str(sumber),
                 "dikoreksi": dikoreksi}
        self._koreksi_log.append(entri)
        if len(self._koreksi_log) > 32:
            self._koreksi_log = self._koreksi_log[-32:]
        return dict(entri)

    def konfrontasi_state(self) -> Dict[str, Any]:
        return {"bukti": [dict(x) for x in self._bukti_log[-3:]],
                "koreksi": [dict(x) for x in self._koreksi_log[-3:]],
                "disonansi_aktif": sum(
                    1 for s in self.dissonance.values()
                    if float(s.get("tension", 0.0)) > 0.05)}

    def second_person_state(self, ent: Optional[Any] = None) -> Dict[str, Any]:
        eid = self._eid(ent) if ent is not None else None
        return {"aktif": self.enabled("second_person"),
                "atensi_bersama": (dict(self._joint_attention.get(eid, {}))
                                   if eid else dict(self._joint_attention)),
                "tom_rekursif": (dict(self._recursive_tom.get(eid, {}))
                                 if eid else dict(self._recursive_tom)),
                "komitmen": [c for c in self.commitments
                             if eid is None or c.get("entitas") == eid][-6:],
                "gossip_terakhir": self.gossip_log[-1] if self.gossip_log else None}

    # ==================================================================
    # 9) DIALOGUE PRAGMATICS & TURN-TAKING
    # ==================================================================
    def dialogue_turn(self, pembicara: str, teks: str) -> Dict[str, Any]:
        """Proses satu giliran bicara: turn-taking, topik, pertanyaan balik."""
        if not self.enabled("pragmatics"):
            return {}
        t = self.turn_state
        if t.get("last_speaker") == pembicara:
            # pelanggaran giliran → repair
            self.repair("giliran", f"{pembicara} bicara dua kali")
        t["last_speaker"] = str(pembicara)[:40]
        t["turn"] = int(t.get("turn", 0)) + 1
        t["topic"] = str(teks)[:60]
        try:
            from pycos.bahasa.teks import jenis_kalimat
            tanya = jenis_kalimat(str(teks)) == "interogatif"
        except Exception as _galat_diagnostik_132:
            _diag.catat('naluri.Kesadaran.dialogue_turn',
                        "galat pada jalur fallback",
                        galat=_galat_diagnostik_132, jalur=132)
            tanya = str(teks).strip().endswith("?")
        t["open_question"] = str(teks)[:80] if tanya else None
        balik = None
        if tanya and pembicara.lower() not in ("aku", "saya", "npc"):
            balik = _pertanyaan_balik(teks, pembicara)
            t["open_question"] = balik
        # referensi sejarah bersama
        ref = (self._shared_history[-1] if self._shared_history else None)
        return {"pembicara": pembicara, "topik": t["topic"],
                "giliran": t["turn"], "pertanyaan_balik": balik,
                "referensi_bersama": ref,
                "pronomina": ["aku", "kamu", "kita"]}

    def backchannel(self, sinyal: str = "mengangguk") -> Dict[str, Any]:
        """Umpan balik singkat saat mendengarkan ('mmm', 'ya', mengangguk')."""
        if not self.enabled("pragmatics"):
            return {}
        entry = {"tick": self._tick(), "sinyal": str(sinyal)[:40]}
        self.backchannels.append(entry)
        if len(self.backchannels) > 32:
            self.backchannels = self.backchannels[-32:]
        return entry

    def repair(self, jenis: str, sebab: str = "") -> Dict[str, Any]:
        """Perbaikan percakapan: salah dengar, lupa, terpotong."""
        entry = {"tick": self._tick(), "jenis": str(jenis)[:40],
                 "sebab": str(sebab)[:80],
                 "frasa": "maaf, maksudku tadi..."}
        self.repairs.append(entry)
        if len(self.repairs) > 32:
            self.repairs = self.repairs[-32:]
        return entry

    def pragmatics_state(self) -> Dict[str, Any]:
        return {"aktif": self.enabled("pragmatics"),
                "giliran": dict(self.turn_state),
                "backchannel_terakhir": (self.backchannels[-1]
                                         if self.backchannels else None),
                "repair_terakhir": self.repairs[-1] if self.repairs else None,
                "sejarah_bersama": self._shared_history[-3:]}

    @staticmethod
    def _withholding_terms(text: Any) -> set:
        stop = {"aku", "saya", "kamu", "kau", "dia", "yang", "dan", "atau",
                "ini", "itu", "tentang", "dengan", "untuk", "dari", "pada",
                "apa", "kenapa", "bagaimana", "tolong", "please", "the", "is",
                "to", "of", "about", "me", "my", "you", "your"}
        words = set(re.findall(r"[\wÀ-ÿ]+", str(text or "").lower(),
                               flags=re.UNICODE))
        return {w for w in words if len(w) > 1 and w not in stop}

    def withhold_speech(self, content: str, topic: Optional[str] = None,
                        recipient: Any = None, strength: float = 0.65
                        ) -> Dict[str, Any]:
        """Simpan kalimat yang ingin diucapkan tetapi secara sadar ditahan.

        Tidak memanggil `refuse()`, PenolakanTutur, atau disonansi. NPC mampu
        mengartikulasikannya; ia hanya memilih untuk tidak mengeluarkannya.
        Pertanyaan Player tidak pernah melepas state ini secara otomatis.
        """
        if not bool(self.params.get("enable_kesadaran", False)):
            return {"aktif": False}
        isi = str(content or "").strip()[:300]
        if not isi:
            return {"aktif": False, "alasan": "isi kosong"}
        penerima = (str(getattr(recipient, "name", recipient))
                    if recipient is not None else "")[:64]
        topik = str(topic or "").strip()[:80]
        if not topik:
            topik = " ".join(sorted(self._withholding_terms(isi)))[:80]
        key = (topik.lower(), penerima.lower())
        ada = next((x for x in self._withheld_speech
                    if (str(x.get("topik", "")).lower(),
                        str(x.get("kepada", "")).lower()) == key
                    and x.get("aktif", True)), None)
        if ada is None:
            tells = ("bibir bergerak seolah hendak bicara, lalu terkatup",
                     "pandangan tertahan sesaat sebelum beralih",
                     "jemari menggenggam lalu perlahan mengendur")
            tell_index = sum(ord(ch) for ch in (topik + penerima)) % len(tells)
            ada = {"id": self._withheld_next_id,
                   "tick": self._tick(), "topik": topik,
                   "kepada": penerima, "isi_tertahan": isi,
                   "kekuatan": _kclip(strength, 0.0, 1.0),
                   "aktif": True, "mampu_diucapkan": True,
                   "keinginan_mengungkapkan": True,
                   "dipilih_ditahan": True, "tindakan": "menahan",
                   "ditahan": 0,
                   "rasa_sakit": 0.025 * _kclip(strength, 0.0, 1.0),
                   "tekanan_relasi": 0.0,
                   "tell": tells[tell_index],
                   "jenis": "penahanan_sadar"}
            self._withheld_next_id += 1
            self._withheld_speech.append(ada)
            if len(self._withheld_speech) > 32:
                self._withheld_speech = self._withheld_speech[-32:]
            self._refresh_identity({"terbiasa menahan {}".format(topik[:28]):
                                    0.025 * _kclip(strength, 0.0, 1.0)})
        else:
            # Desire yang sama menguat, bukan tercatat sebagai refusal baru.
            ada["kekuatan"] = max(float(ada.get("kekuatan", 0.0)),
                                  _kclip(strength, 0.0, 1.0))
        return {"aktif": True, "id": int(ada["id"]),
                "topik": ada["topik"], "kepada": ada["kepada"],
                "mampu_diucapkan": True, "dipilih_ditahan": True,
                "bukan_penolakan": True, "bukan_prinsip": True,
                "bukan_kontradiksi": True}

    withhold_disclosure = withhold_speech
    tahan_tutur = withhold_speech

    def withheld_for(self, topic: Any = None, recipient: Any = None
                     ) -> Optional[Dict[str, Any]]:
        """Temukan penahanan yang spesifik untuk giliran/relasi ini."""
        incoming = str(topic or "").strip()
        if not incoming:
            incoming = str(self.turn_state.get("topic", "") or "").strip()
        if not incoming:
            return None
        query = self._withholding_terms(incoming)
        if not query:
            return None
        penerima = (str(getattr(recipient, "name", recipient))
                    if recipient is not None else "").lower()
        for item in reversed(self._withheld_speech):
            if not item.get("aktif", True):
                continue
            kepada = str(item.get("kepada", "") or "").lower()
            if kepada and penerima and kepada != penerima:
                continue
            jangkar = (self._withholding_terms(item.get("topik", ""))
                       | self._withholding_terms(item.get("isi_tertahan", "")))
            if not jangkar:
                continue
            overlap = len(query & jangkar)
            if (incoming.lower() in str(item.get("topik", "")).lower()
                    or str(item.get("topik", "")).lower() in incoming.lower()
                    or overlap >= 1 and (overlap / max(1, len(query)) >= 0.25
                                         or len(query) <= 2)):
                return copy.deepcopy(item)
        return None

    def record_withholding_attempt(self, ident: Any) -> Dict[str, Any]:
        """Tahan lagi dengan rasa sakit dan jejak identitas/relasi kumulatif."""
        item = next((x for x in self._withheld_speech
                     if str(x.get("id")) == str(ident)
                     and x.get("aktif", True)), None)
        if item is None:
            return {"aktif": False}
        item["ditahan"] = int(item.get("ditahan", 0)) + 1
        count = item["ditahan"]
        strength = _kclip(item.get("kekuatan", 0.65), 0.0, 1.0)
        item["rasa_sakit"] = _kclip(float(item.get("rasa_sakit", 0.0))
                                    + strength * (0.055 + 0.012 * min(count, 6)),
                                    0.0, 1.0)
        item["tekanan_relasi"] = _kclip(
            float(item.get("tekanan_relasi", 0.0)) + 0.025 * strength,
            0.0, 0.55)
        item["terakhir"] = self._tick()
        trait = "terbiasa menahan {}".format(str(item.get("topik", "sesuatu"))[:28])
        self._refresh_identity({trait: 0.055 * strength})
        # Bekas kecil pada relasi terkumpul hanya setelah penahanan berulang;
        # Player tidak bisa membayar/memaksa isi keluar lewat satu pertanyaan.
        n = self.naluri
        nur = getattr(n, "nurani", None) if n is not None else None
        recipient = str(item.get("kepada", "") or "")
        if count >= 2 and recipient and nur is not None:
            try:
                if nur.enabled("social_memory"):
                    nur.interact(recipient, muatan=-0.035 * strength,
                                 kepercayaan_delta=-0.045 * strength,
                                 tick=self._tick())
            except Exception as _galat_diagnostik_20:
                _diag.catat('naluri.Kesadaran.record_withholding_attempt', "galat pada jalur fallback", galat=_galat_diagnostik_20, jalur=20)
                pass
        return {"aktif": True, "id": int(item["id"]),
                "ditahan": count,
                "rasa_sakit": round(float(item["rasa_sakit"]), 4),
                "tekanan_relasi": round(float(item["tekanan_relasi"]), 4),
                "tell": str(item.get("tell", "")),
                "topik": str(item.get("topik", ""))}

    def withholding_relationship_tension(self, recipient: Any) -> float:
        eid = str(getattr(recipient, "name", recipient) or "").lower()
        return max((float(x.get("tekanan_relasi", 0.0))
                    for x in self._withheld_speech
                    if x.get("aktif", True)
                    and str(x.get("kepada", "")).lower() == eid),
                   default=0.0)

    def withholding_state(self, include_private: bool = False) -> Dict[str, Any]:
        items = []
        for raw in self._withheld_speech:
            item = {k: v for k, v in raw.items()
                    if include_private or k != "isi_tertahan"}
            items.append(copy.deepcopy(item))
        return {"aktif": any(x.get("aktif", True) for x in items),
                "jumlah": len(items), "tertahan": items[-12:],
                "pengungkapan_terakhir": (dict(self._withholding_disclosure_log[-1])
                                           if self._withholding_disclosure_log else None)}

    def choose_to_disclose(self, ident: Any, dipilih_npc: bool = False
                           ) -> Dict[str, Any]:
        """Buka isi hanya pada keputusan NPC eksplisit, bukan tekanan Player."""
        if not dipilih_npc:
            return {"diungkap": False, "alasan": "menunggu_pilihan_npc"}
        item = next((x for x in self._withheld_speech
                     if str(x.get("id")) == str(ident)
                     and x.get("aktif", True)), None)
        if item is None:
            return {"diungkap": False, "alasan": "tidak_ada_penahanan_aktif"}
        item["aktif"] = False
        item["tindakan"] = "mengungkapkan"
        item["diungkapkan"] = True
        item["diungkap_tick"] = self._tick()
        rec = {"tick": self._tick(), "id": int(item["id"]),
               "topik": str(item.get("topik", "")),
               "kepada": str(item.get("kepada", "")),
               "setelah_penahanan": int(item.get("ditahan", 0))}
        self._withholding_disclosure_log.append(rec)
        self._withholding_disclosure_log = self._withholding_disclosure_log[-32:]
        return {"diungkap": True, "teks": str(item.get("isi_tertahan", "")),
                "tick": self._tick(), "id": int(item["id"])}

    # ==================================================================
    # 9B) STRATEGI SOSIAL — kebohongan disengaja, manipulasi, peran, kesetiaan
    # ==================================================================
    def model_other_belief(self, target: Any, proposisi: str,
                           confidence: float = 0.5,
                           sumber: str = "inferensi") -> Dict[str, Any]:
        """Simpan hipotesis tentang keyakinan orang lain (bukan fakta batin)."""
        if not self.enabled("social_strategy"):
            return {"aktif": False}
        eid = self._eid(target)
        isi = str(proposisi or "").strip()[:160]
        if not eid or not isi:
            return {"aktif": False, "alasan": "target/proposisi kosong"}
        model = self._other_belief_models.setdefault(
            eid, {"keyakinan": {}, "tick": self._tick()})
        slot = {"confidence": _kclip(confidence, 0.0, 1.0),
                "sumber": str(sumber or "inferensi")[:48],
                "tick": self._tick(), "status": "estimasi"}
        model.setdefault("keyakinan", {})[isi] = slot
        model["tick"] = self._tick()
        return {"target": eid, "proposisi": isi, **slot}

    def other_belief_model(self, target: Any = None) -> Dict[str, Any]:
        eid = self._eid(target) if target is not None else ""
        if eid:
            return copy.deepcopy(self._other_belief_models.get(
                eid, {"keyakinan": {}, "tick": None}))
        return copy.deepcopy(self._other_belief_models)

    def choose_to_lie(self, known_truth: str, falsehood: str, goal: str,
                      target: Any, intended_belief: Optional[str] = None,
                      confidence: float = 0.75,
                      topic: Optional[str] = None) -> Dict[str, Any]:
        """Pilih secara sadar berkata X walau tahu Y, demi tujuan Z.

        Tidak ada pemilih kebohongan otomatis: pemanggil/agen harus memanggil
        metode keputusan ini dengan kebenaran, ujaran yang dipilih, sasaran,
        dan tujuan. Rencana ini baru menjadi ujaran saat Presentasi mengambilnya.
        """
        if not self.enabled("social_strategy"):
            return {"aktif": False, "alasan": "strategi sosial dinonaktifkan"}
        truth = str(known_truth or "").strip()[:240]
        lie = str(falsehood or "").strip()[:240]
        motive = str(goal or "").strip()[:160]
        eid = self._eid(target)
        if not truth or not lie or not motive or not eid:
            return {"aktif": False,
                    "alasan": "kebenaran, ujaran, tujuan, dan target wajib diisi"}
        norm = lambda x: " ".join(re.findall(r"[\wÀ-ÿ]+", x.lower()))
        if norm(truth) == norm(lie):
            return {"aktif": False, "alasan": "ujaran tidak berbeda dari kebenaran"}
        isi_belief = str(intended_belief or lie).strip()[:160]
        ident = self._social_strategy_next_id
        self._social_strategy_next_id += 1
        entry = {"id": ident, "tick": self._tick(), "target": eid,
                 "kebenaran_diketahui": truth, "ujaran_dipilih": lie,
                 "tujuan": motive, "keyakinan_yang_dikehendaki": isi_belief,
                 "topik": str(topic or "").strip()[:80],
                 "confidence": _kclip(confidence, 0.0, 1.0),
                 "sadar": True, "dipilih_untuk_menipu": True,
                 "status": "direncanakan", "hasil_teramati": None}
        self._strategic_deceptions.append(entry)
        cap = max(1, int(self._p("kesadaran_social_strategy_max")))
        self._strategic_deceptions = self._strategic_deceptions[-cap:]
        self._refresh_identity({"pernah memilih menyembunyikan kebenaran": 0.035})
        if self.enabled("global_workspace"):
            self.submit(
                f"Aku tahu {truth[:60]}, tetapi akan mengatakan {lie[:60]} kepada {eid} agar {motive[:50]}",
                salience=0.74, tag="strategi_sosial", source="niat", kind="deception",
                detail={"tujuan": motive, "dipilih_sadar": True},
                dapat_dilaporkan=False)
        return {"aktif": True, "id": ident, "target": eid,
                "sadar": True, "dipilih_untuk_menipu": True,
                "tujuan": motive, "status": "direncanakan"}

    intentional_lie = choose_to_lie
    decide_to_lie = choose_to_lie
    rencanakan_kebohongan = choose_to_lie

    def strategic_speech_for(self, target: Any = None,
                             topic: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Ambil hanya kebohongan yang sengaja dipilih untuk relasi/topik ini."""
        if not self.enabled("social_strategy"):
            return None
        eid = self._eid(target) if target is not None else ""
        incoming = self._withholding_terms(topic or "")
        for item in reversed(self._strategic_deceptions):
            if item.get("status") != "direncanakan":
                continue
            if item.get("target") and item.get("target") != eid:
                continue
            plan_topic = str(item.get("topik", ""))
            if plan_topic and incoming:
                anchored = self._withholding_terms(plan_topic)
                if anchored and not (anchored & incoming):
                    continue
            return copy.deepcopy(item)
        return None

    def deliver_strategic_speech(self, ident: Any) -> Dict[str, Any]:
        """Catat pelaksanaan ujaran yang sebelumnya telah dipilih secara sadar."""
        item = next((x for x in reversed(self._strategic_deceptions)
                     if str(x.get("id")) == str(ident)
                     and x.get("status") == "direncanakan"), None)
        if item is None:
            return {"terucap": False, "alasan": "rencana tidak aktif"}
        item["status"] = "telah_diucapkan"
        item["diucapkan_tick"] = self._tick()
        item["hasil_teramati"] = None
        # Ini hanya ekspektasi si agen tentang pendengar, bukan bukti bahwa
        # pendengar benar-benar mempercayai ucapannya.
        model = self._other_belief_models.setdefault(
            str(item["target"]), {"keyakinan": {}, "tick": self._tick()})
        model.setdefault("keyakinan", {}).setdefault(
            str(item["keyakinan_yang_dikehendaki"]), {
                "confidence": round(0.35 * float(item.get("confidence", 0.75)), 3),
                "sumber": "efek_yang_diharapkan_dari_kebohongan",
                "tick": self._tick(), "status": "prediksi_belum_terverifikasi"})
        return {"terucap": True, "id": int(item["id"]),
                "target": str(item["target"]),
                "keyakinan_yang_dikehendaki": str(item["keyakinan_yang_dikehendaki"]),
                "hasil_teramati": None}

    def plan_manipulation(self, target: Any, goal: str,
                          steps: Sequence[Any],
                          intended_belief: Optional[str] = None
                          ) -> Dict[str, Any]:
        """Susun urutan aksi sosial untuk menggeser keyakinan orang lain."""
        if not self.enabled("social_strategy"):
            return {"aktif": False, "alasan": "strategi sosial dinonaktifkan"}
        eid = self._eid(target)
        motive = str(goal or "").strip()[:160]
        if not eid or not motive:
            return {"aktif": False, "alasan": "target dan tujuan wajib diisi"}
        normalized: List[Dict[str, Any]] = []
        for raw in steps or []:
            if isinstance(raw, Mapping):
                utterance = str(raw.get("ujaran", raw.get("utterance", raw.get("teks", ""))) or "").strip()
                action = str(raw.get("aksi", raw.get("action", "mengamati")) or "mengamati").strip()
                normalized.append({"aksi": action[:100], "ujaran": utterance[:240],
                                   "keyakinan_diharapkan": str(raw.get(
                                       "keyakinan_diharapkan", raw.get("belief", "")))[:160],
                                   "jenis": str(raw.get("jenis", "tindakan_sosial"))[:40],
                                   "status": "menunggu"})
            else:
                normalized.append({"aksi": "berkata", "ujaran": str(raw or "").strip()[:240],
                                   "keyakinan_diharapkan": "",
                                   "jenis": "ujaran", "status": "menunggu"})
        normalized = [x for x in normalized if x["ujaran"] or x["aksi"]]
        if len(normalized) < 2:
            return {"aktif": False, "alasan": "rencana perlu sekurangnya dua langkah"}
        ident = self._social_strategy_next_id
        self._social_strategy_next_id += 1
        plan = {"id": ident, "tick": self._tick(), "target": eid,
                "tujuan": motive,
                "keyakinan_yang_dikehendaki": str(intended_belief or "")[:160],
                "langkah": normalized, "indeks": 0, "status": "direncanakan",
                "berhasil": None, "sadar": True}
        self._manipulation_plans.append(plan)
        cap = max(1, int(self._p("kesadaran_social_strategy_max")))
        self._manipulation_plans = self._manipulation_plans[-cap:]
        return {"aktif": True, "id": ident, "target": eid,
                "tujuan": motive, "jumlah_langkah": len(normalized),
                "keyakinan_yang_dikehendaki": plan["keyakinan_yang_dikehendaki"]}

    manipulation_plan = plan_manipulation

    def next_manipulation_action(self, target: Any = None,
                                 topic: Optional[str] = None
                                 ) -> Optional[Dict[str, Any]]:
        if not self.enabled("social_strategy"):
            return None
        eid = self._eid(target) if target is not None else ""
        incoming = self._withholding_terms(topic or "")
        for plan in reversed(self._manipulation_plans):
            if plan.get("status") != "direncanakan" or plan.get("target") != eid:
                continue
            i = int(plan.get("indeks", 0))
            if i >= len(plan.get("langkah", [])):
                continue
            step = plan["langkah"][i]
            if step.get("topik") and incoming and not (
                    self._withholding_terms(step["topik"]) & incoming):
                continue
            return {"plan_id": int(plan["id"]), "indeks": i,
                    "target": eid, "tujuan": plan["tujuan"],
                    **copy.deepcopy(step)}
        return None

    def record_manipulation_step(self, plan_id: Any,
                                 outcome: Optional[Mapping[str, Any]] = None
                                 ) -> Dict[str, Any]:
        plan = next((x for x in reversed(self._manipulation_plans)
                     if str(x.get("id")) == str(plan_id)
                     and x.get("status") == "direncanakan"), None)
        if plan is None:
            return {"aktif": False, "alasan": "rencana tidak aktif"}
        i = int(plan.get("indeks", 0))
        if i >= len(plan.get("langkah", [])):
            plan["status"] = "selesai"
            return {"aktif": False, "status": "selesai"}
        step = plan["langkah"][i]
        step["status"] = "dijalankan"
        step["tick"] = self._tick()
        if isinstance(outcome, Mapping):
            step["hasil"] = copy.deepcopy(dict(outcome))
            if outcome.get("keyakinan_teramati"):
                self.model_other_belief(
                    plan["target"], str(outcome["keyakinan_teramati"]),
                    float(outcome.get("confidence", 0.65)),
                    sumber="pengamatan_hasil_manipulasi")
        plan["indeks"] = i + 1
        if plan["indeks"] >= len(plan["langkah"]):
            plan["status"] = "langkah_selesai_menunggu_hasil"
        return {"aktif": True, "id": int(plan["id"]),
                "langkah_dijalankan": i,
                "langkah_tersisa": max(0, len(plan["langkah"]) - plan["indeks"]),
                "status": plan["status"]}

    def record_manipulation_outcome(self, plan_id: Any, berhasil: bool,
                                    belief_observed: Optional[str] = None,
                                    confidence: float = 0.6) -> Dict[str, Any]:
        plan = next((x for x in reversed(self._manipulation_plans)
                     if str(x.get("id")) == str(plan_id)), None)
        if plan is None:
            return {"aktif": False, "alasan": "rencana tidak ditemukan"}
        plan["berhasil"] = bool(berhasil)
        plan["status"] = "berhasil" if berhasil else "gagal"
        plan["hasil_tick"] = self._tick()
        if belief_observed:
            self.model_other_belief(plan["target"], belief_observed,
                                    confidence, sumber="hasil_teramati")
        return {"aktif": True, "id": int(plan["id"]),
                "status": plan["status"],
                "keyakinan_teramati": bool(belief_observed)}

    def roleplay(self, peran: str, tujuan: str = "",
                 target: Any = None, klaim: str = "",
                 gaya: Optional[Mapping[str, Any]] = None,
                 aktif: bool = True) -> Dict[str, Any]:
        """Pilih persona/topeng yang bukan identitas asli untuk situasi tertentu."""
        if not self.enabled("social_strategy"):
            return {"aktif": False, "alasan": "strategi sosial dinonaktifkan"}
        if not aktif:
            self._roleplay_state = None
            return {"aktif": False, "dihentikan": True}
        role = str(peran or "").strip()[:80]
        if not role:
            return {"aktif": False, "alasan": "peran kosong"}
        self._roleplay_state = {
            "tick": self._tick(), "peran": role,
            "tujuan": str(tujuan or "")[:160],
            "target": self._eid(target) if target is not None else "",
            "klaim": str(klaim or "").strip()[:240],
            "gaya": copy.deepcopy(dict(gaya or {})),
            "aktif": True, "sadar": True, "klaim_sudah_diucapkan": False,
        }
        return {"aktif": True, "peran": role,
                "target": self._roleplay_state["target"],
                "penyamaran_sadar": True,
                "klaim_disiapkan": bool(self._roleplay_state["klaim"])}

    adopt_role = roleplay
    begin_roleplay = roleplay

    def roleplay_speech_for(self, target: Any = None) -> Optional[Dict[str, Any]]:
        state = self._roleplay_state
        if not self.enabled("social_strategy") or not state or not state.get("aktif"):
            return None
        eid = self._eid(target) if target is not None else ""
        if state.get("target") and state["target"] != eid:
            return None
        style = copy.deepcopy(state.get("gaya") or {})
        if state.get("klaim") and not state.get("klaim_sudah_diucapkan"):
            return {"jenis": "permainan_peran", "id": None,
                    "teks": str(state["klaim"]), "act": "menjawab",
                    "peran": str(state["peran"]), "gaya": style}
        return {"jenis": "permainan_peran", "id": None,
                "teks": "", "act": style.get("act", style.get("tindak_tutur")),
                "peran": str(state["peran"]), "gaya": style}

    def record_roleplay_speech(self) -> Dict[str, Any]:
        if not self._roleplay_state or not self._roleplay_state.get("aktif"):
            return {"aktif": False}
        self._roleplay_state["klaim_sudah_diucapkan"] = True
        self._roleplay_state["terakhir_diucapkan"] = self._tick()
        return {"aktif": True, "peran": self._roleplay_state.get("peran"),
                "penyamaran_sadar": True}

    def end_roleplay(self) -> Dict[str, Any]:
        lama = copy.deepcopy(self._roleplay_state) if self._roleplay_state else None
        self._roleplay_state = None
        return {"dihentikan": lama is not None,
                "peran": lama.get("peran") if lama else None}

    def choose_loyalty(self, candidates: Sequence[Any],
                       trust: Any = None, importance: Any = None,
                       cost: Any = None, commitment_strength: Any = None
                       ) -> Dict[str, Any]:
        """Pilih pihak berdasar kepercayaan/kepentingan/komitmen, bukan valensi.

        Valensi relasi sengaja tidak dibaca. ``trust``/``importance`` dapat
        berupa skor tunggal atau mapping per nama; relasi dan komitmen yang
        pernah tercatat dipakai sebagai fallback.
        """
        if not self.enabled("social_strategy"):
            return {"aktif": False}
        if isinstance(candidates, (str, bytes)):
            candidates = [candidates]
        def val(spec: Any, eid: str, default: float) -> float:
            if isinstance(spec, Mapping):
                return _kclip(spec.get(eid, default), 0.0, 1.0)
            if spec is not None:
                return _kclip(spec, 0.0, 1.0)
            return default
        scored: List[Dict[str, Any]] = []
        n = self.naluri
        for raw in candidates or []:
            if isinstance(raw, Mapping):
                eid = self._eid(raw.get("target", raw.get("pihak", raw.get("name", ""))))
                item = dict(raw)
            else:
                eid, item = self._eid(raw), {}
            if not eid:
                continue
            tr_default = 0.5
            if n is not None:
                try:
                    rel = n.relasi(eid)
                    tr_default = float(rel.get("kepercayaan", tr_default))
                except Exception as _galat_diagnostik_21:
                    _diag.catat('naluri.Kesadaran.choose_loyalty', "galat pada jalur fallback", galat=_galat_diagnostik_21, jalur=21)
                    pass
            trust_v = val(item.get("trust", trust), eid, tr_default)
            importance_v = val(item.get("importance", importance), eid, 0.5)
            commitment_v = val(item.get("commitment_strength", commitment_strength), eid, 0.0)
            if commitment_v == 0.0:
                komit = [c for c in self.commitments
                         if str(c.get("entitas", "")) == eid
                         and c.get("status", "aktif") not in ("dilanggar", "selesai")]
                commitment_v = min(1.0, 0.2 * len(komit))
            cost_v = val(item.get("cost", cost), eid, 0.0)
            score = (0.42 * trust_v + 0.34 * importance_v
                     + 0.16 * commitment_v + 0.08 * (1.0 - cost_v))
            scored.append({"pihak": eid, "skor": round(score, 4),
                           "kepercayaan": round(trust_v, 3),
                           "kepentingan": round(importance_v, 3),
                           "komitmen": round(commitment_v, 3),
                           "biaya": round(cost_v, 3)})
        if not scored:
            return {"aktif": False, "alasan": "tidak ada pihak yang dapat dipilih"}
        scored.sort(key=lambda x: (x["skor"], x["pihak"]), reverse=True)
        entry = {"tick": self._tick(), "pihak": scored[0]["pihak"],
                 "skor": scored[0]["skor"], "kandidat": scored,
                 "dasar": ["kepercayaan", "kepentingan", "komitmen", "biaya"],
                 "valensi_dipakai": False,
                 "alasan": "kesetiaan strategis, bukan sekadar valensi"}
        self._strategic_loyalty.append(entry)
        self._strategic_loyalty = self._strategic_loyalty[-32:]
        return copy.deepcopy(entry)

    strategic_loyalty = choose_loyalty
    pilih_kesetiaan = choose_loyalty

    def social_strategy_state(self, include_private: bool = False) -> Dict[str, Any]:
        deceptions = []
        for raw in self._strategic_deceptions[-12:]:
            if include_private:
                deceptions.append(copy.deepcopy(raw))
            else:
                deceptions.append({k: copy.deepcopy(raw.get(k)) for k in
                                   ("id", "tick", "target", "status", "sadar",
                                    "dipilih_untuk_menipu")})
        role = copy.deepcopy(self._roleplay_state) if self._roleplay_state else None
        if role is not None and not include_private:
            role = {k: v for k, v in role.items() if k not in ("klaim", "tujuan", "gaya")}
        return {"aktif": self.enabled("social_strategy"),
                "model_keyakinan_orang_lain": len(self._other_belief_models),
                "kebohongan_sengaja": deceptions,
                "rencana_manipulasi": [copy.deepcopy(x) if include_private else {
                    "id": x.get("id"), "target": x.get("target"),
                    "status": x.get("status"), "indeks": x.get("indeks"),
                    "jumlah_langkah": len(x.get("langkah", []))}
                    for x in self._manipulation_plans[-8:]],
                "permainan_peran": role,
                "kesetiaan_terakhir": (copy.deepcopy(self._strategic_loyalty[-1])
                                       if self._strategic_loyalty else None)}

    # Isi yang ditahan sebelumnya adalah rahasia yang tidak diucapkan secara
    # sadar. Nama alternatif berikut membuat maksud tersebut mudah ditemukan.
    keep_secret = withhold_speech
    keep_secret_state = withholding_state
    reveal_secret = choose_to_disclose

    # ==================================================================
    # 9C) SA_SP — ANALISIS SEMANTIK-PRAGMATIK & KEHENDAK BEBAS
    # ==================================================================
    def analisis_sa_sp(self, ujaran: Any, konteks: Any = None,
                       speaker: Any = None) -> Dict[str, Any]:
        """Pisahkan makna literal dari maksud kontekstual (yang tetap hipotesis)."""
        from pycos.inti.naluri import SASPAnalyzer
        if not self.enabled("sa_sp") or SASPAnalyzer is None:
            return {"aktif": False, "alasan": "sa_sp tidak tersedia/aktif"}
        if isinstance(konteks, Mapping):
            ctx = dict(konteks)
        elif konteks is None:
            ctx = {}
        else:
            ctx = {"situasi": str(konteks)}
        if speaker is not None:
            eid = self._eid(speaker)
            ctx.setdefault("speaker", eid)
            if eid and "relasi" not in ctx:
                presentasi = getattr(self.naluri, "presentasi", None)
                label = getattr(presentasi, "_label_rel", None)
                if callable(label):
                    try:
                        ctx["relasi"] = str(label(speaker))
                    except Exception as _galat_diagnostik_22:
                        _diag.catat('naluri.Kesadaran.analisis_sa_sp', "galat pada jalur fallback", galat=_galat_diagnostik_22, jalur=22)
                        pass
            if eid in self._joint_attention:
                ctx.setdefault("shared_context", True)
        if self._sa_sp_analyzer is None:
            leksikon = None
            presentasi = getattr(self.naluri, "presentasi", None)
            engine = getattr(presentasi, "_tutur", None) if presentasi is not None else None
            if engine is not None:
                leksikon = getattr(engine, "leks", None)
            try:
                self._sa_sp_analyzer = SASPAnalyzer(leksikon=leksikon)
            except Exception as _galat_diagnostik_23:
                _diag.catat('naluri.Kesadaran.analisis_sa_sp', "galat pada jalur fallback", galat=_galat_diagnostik_23, jalur=23)
                self._sa_sp_analyzer = SASPAnalyzer()
        try:
            result = self._sa_sp_analyzer.analisis(ujaran, ctx)
        except Exception as exc:
            _diag.catat('naluri.Kesadaran.analisis_sa_sp', "galat pada jalur fallback", galat=exc, jalur=24)
            return {"aktif": False, "alasan": f"gagal menganalisis: {type(exc).__name__}"}
        self.observe_sa_sp(result, speaker=speaker)
        prag = result.get("pragmatik") or {}
        kind = str(prag.get("tindak_tutur", ""))
        if self.enabled("epistemic_emotions"):
            if kind in ("permintaan_informasi", "permintaan_tidak_langsung",
                        "asertif_dengan_kemungkinan_hint"):
                self.epistemic_emotion("penasaran", 0.12,
                                       "ujaran membuka kemungkinan maksud kontekstual")
            maksud = prag.get("maksud_tersirat") or []
            if len(maksud) > 1:
                scores = [float(x.get("confidence", 0.0) or 0.0)
                          for x in maksud if isinstance(x, Mapping)]
                if len(scores) > 1 and abs(max(scores) - min(scores)) < 0.15:
                    self.epistemic_emotion("bingung", 0.10,
                                           "lebih dari satu maksud sama-sama masuk akal")
        return result

    analyze_sa_sp = analisis_sa_sp

    def sa_sp_state(self) -> Dict[str, Any]:
        return {"aktif": self.enabled("sa_sp"),
                "jumlah": len(self._sa_sp_log),
                "terakhir": (copy.deepcopy(self._sa_sp_log[-1])
                             if self._sa_sp_log else None)}

    @staticmethod
    def _free_will_action_names(actions: Any) -> List[str]:
        if isinstance(actions, str):
            actions = [actions]
        out: List[str] = []
        try:
            for action in actions or []:
                if isinstance(action, Mapping):
                    action = action.get("name", action.get("aksi", action.get("action", "")))
                text = str(action or "").strip()
                if text:
                    out.append(text[:100])
        except TypeError:
            pass
        return list(dict.fromkeys(out))

    def free_will_choose_goal(self, description: str,
                              actions: Any = None,
                              reason: str = "",
                              priority: float = 0.65,
                              endorsement: float = 0.5,
                              novelty: float = 0.5,
                              value_alignment: float = 0.5,
                              autonomy: float = 1.0) -> Dict[str, Any]:
        """Pilih tujuan sadar di luar drive; aksi terkait dipasok eksplisit.

        Tidak ada drive delta atau reward yang dipakai untuk membenarkan
        keputusan ini. Bonus ``choose_action`` hanya aktif bila kandidat cocok
        dengan tujuan/tindakannya sendiri.
        """
        if not self.enabled("free_will"):
            return {"aktif": False, "alasan": "free_will dinonaktifkan"}
        goal_text = str(description or "").strip()[:180]
        if not goal_text:
            return {"aktif": False, "alasan": "tujuan kosong"}
        action_names = self._free_will_action_names(actions)
        normal = " ".join(re.findall(r"[\wÀ-ÿ]+", goal_text.lower()))
        for existing in reversed(self._free_will_goals):
            if (existing.get("status") == "aktif"
                    and " ".join(re.findall(r"[\wÀ-ÿ]+", str(existing.get("tujuan", "")).lower())) == normal):
                if action_names:
                    existing["aksi"] = action_names
                existing["prioritas"] = _kclip(priority, 0.0, 1.0)
                existing["tick_diperbarui"] = self._tick()
                return {"aktif": True, "goal": copy.deepcopy(existing),
                        "diperbarui": True, "dasar": "tujuan_sendiri_bukan_drive"}
        ident = self._free_will_next_id
        self._free_will_next_id += 1
        score = _kclip(0.40 * _kclip(endorsement, 0, 1)
                       + 0.25 * _kclip(novelty, 0, 1)
                       + 0.20 * _kclip(value_alignment, 0, 1)
                       + 0.15 * _kclip(autonomy, 0, 1), 0, 1)
        goal = {"id": ident, "tujuan": goal_text,
                "aksi": action_names,
                "alasan": str(reason or "aku memilih ini karena ingin mencobanya")[:180],
                "prioritas": _kclip(priority, 0.0, 1.0),
                "skor_endorsement": round(score, 4),
                "basis_keputusan": {"endorsement": _kclip(endorsement, 0, 1),
                                    "novelty": _kclip(novelty, 0, 1),
                                    "alignment_nilai": _kclip(value_alignment, 0, 1),
                                    "otonomi": _kclip(autonomy, 0, 1),
                                    "drive_dipakai": False,
                                    "utilitas_drive_dipakai": False},
                "status": "aktif", "kemajuan": 0.0,
                "dipilih_sendiri": True, "tick_dibuat": self._tick(),
                "tick_diperbarui": self._tick()}
        self._free_will_goals.append(goal)
        cap = max(1, int(self._p("free_will_goal_max")))
        self._free_will_goals = self._free_will_goals[-cap:]
        event = {"tick": self._tick(), "jenis": "tujuan_dipilih_sendiri",
                 "goal_id": ident, "tujuan": goal_text,
                 "drive_dipakai": False, "reward_eksternal_diperlukan": False}
        self._free_will_events.append(event)
        self._free_will_events = self._free_will_events[-64:]
        self._refresh_identity({"pernah memilih tujuan sendiri": 0.08})
        if self.enabled("global_workspace"):
            self.submit(f"aku memilih sendiri untuk {goal_text}", salience=0.66,
                        tag="free_will", source="pilihan_diri",
                        kind="self_chosen_goal",
                        detail={"goal_id": ident, "drive_dipakai": False})
        return {"aktif": True, "goal": copy.deepcopy(goal),
                "diperbarui": False, "dasar": "tujuan_sendiri_bukan_drive"}

    choose_self_goal = free_will_choose_goal
    choose_own_goal = free_will_choose_goal

    def free_will_decide_goal(self, options: Sequence[Any],
                              reason: str = "",
                              priority: Optional[float] = None
                              ) -> Dict[str, Any]:
        """Pilih satu dari alternatif berdasar endorsement, kebaruan, nilai,
        dan otonomi — bukan kelaparan drive atau valensi sesaat.
        """
        if not self.enabled("free_will"):
            return {"aktif": False, "alasan": "free_will dinonaktifkan"}
        scored: List[Dict[str, Any]] = []
        for index, raw in enumerate(options or []):
            item = dict(raw) if isinstance(raw, Mapping) else {"tujuan": str(raw)}
            text = str(item.get("tujuan", item.get("goal", item.get("description", ""))) or "").strip()
            if not text:
                continue
            endorsement = _kclip(item.get("endorsement", item.get("dukungan_diri", 0.5)), 0, 1)
            novelty = _kclip(item.get("novelty", item.get("kebaruan", 0.5)), 0, 1)
            align = _kclip(item.get("value_alignment", item.get("keselarasan_nilai", 0.5)), 0, 1)
            autonomy = _kclip(item.get("autonomy", item.get("otonomi", 1.0)), 0, 1)
            score = 0.40 * endorsement + 0.25 * novelty + 0.20 * align + 0.15 * autonomy
            scored.append({"index": index, "tujuan": text,
                           "aksi": self._free_will_action_names(item.get("actions", item.get("aksi"))),
                           "alasan": str(item.get("reason", item.get("alasan", reason)) or reason),
                           "endorsement": endorsement, "novelty": novelty,
                           "value_alignment": align, "autonomy": autonomy,
                           "skor": round(score, 6),
                           "prioritas": item.get("priority", priority)})
        if not scored:
            return {"aktif": False, "alasan": "tidak ada alternatif tujuan yang valid"}
        chosen = max(scored, key=lambda x: (x["skor"], x["novelty"], -x["index"]))
        return self.free_will_choose_goal(
            chosen["tujuan"], actions=chosen["aksi"],
            reason=chosen["alasan"] or "dipilih melalui pertimbangan diri",
            priority=(priority if priority is not None else
                      chosen["prioritas"] if chosen["prioritas"] is not None else
                      chosen["skor"]),
            endorsement=chosen["endorsement"], novelty=chosen["novelty"],
            value_alignment=chosen["value_alignment"], autonomy=chosen["autonomy"])

    decide_self_goal = free_will_decide_goal
    deliberate_goal = free_will_decide_goal

    def free_will_current_goal(self) -> Optional[Dict[str, Any]]:
        if not self.enabled("free_will"):
            return None
        aktif = [x for x in self._free_will_goals if x.get("status") == "aktif"]
        if not aktif:
            return None
        return copy.deepcopy(max(aktif, key=lambda x: (
            float(x.get("prioritas", 0.0)), int(x.get("tick_dibuat", 0)))))

    def free_will_action_bonus(self, candidate: Mapping[str, Any]) -> Dict[str, Any]:
        """Bonus eksplisit bagi kandidat yang melayani tujuan yang dipilih sendiri."""
        goal = self.free_will_current_goal()
        if goal is None or not isinstance(candidate, Mapping):
            return {"bonus": 0.0}
        ident = str(goal.get("id", ""))
        for key in ("free_will_goal_id", "goal_id", "self_goal_id"):
            if candidate.get(key) is not None and str(candidate.get(key)) == ident:
                match = 1.0
                break
        else:
            match = 0.0
            action = str(candidate.get("name", candidate.get("aksi", ""))).strip().lower()
            labels = [action]
            for key in ("action", "description", "goal", "goal_name", "tag"):
                if candidate.get(key):
                    labels.append(str(candidate.get(key)).strip().lower())
            terms = {w for w in re.findall(r"[\wÀ-ÿ]+", str(goal.get("tujuan", "")).lower())
                     if len(w) > 2 and w not in {"untuk", "dengan", "yang", "aku", "ingin", "mau", "mencoba"}}
            named_actions = {str(x).strip().lower() for x in goal.get("aksi", []) if str(x).strip()}
            if action and action in named_actions:
                match = 1.0
            elif named_actions and any(any(named in label for label in labels)
                                       for named in named_actions):
                match = 0.85
            elif terms:
                candidate_terms = {w for label in labels
                                   for w in re.findall(r"[\wÀ-ÿ]+", label)}
                overlap = len(terms & candidate_terms) / max(1, min(3, len(terms)))
                if overlap >= 0.34:
                    match = min(0.75, 0.35 + 0.4 * overlap)
        bonus = (float(self._p("free_will_bonus_weight"))
                 * float(goal.get("prioritas", 0.0)) * match)
        return {"goal_id": int(goal.get("id", 0)),
                "tujuan": str(goal.get("tujuan", "")),
                "cocok": round(match, 3), "bonus": round(bonus, 4),
                "basis": "pilihan_diri_tanpa_drive"}

    def free_will_progress(self, goal_id: Any, progress: float = 0.1,
                           outcome: str = "") -> Dict[str, Any]:
        goal = next((x for x in self._free_will_goals
                     if str(x.get("id")) == str(goal_id)
                     and x.get("status") == "aktif"), None)
        if goal is None:
            return {"aktif": False, "alasan": "tujuan aktif tidak ditemukan"}
        goal["kemajuan"] = _kclip(float(goal.get("kemajuan", 0.0))
                                  + max(0.0, float(progress)), 0.0, 1.0)
        goal["tick_diperbarui"] = self._tick()
        if outcome:
            goal.setdefault("hasil", []).append(str(outcome)[:120])
            goal["hasil"] = goal["hasil"][-8:]
        if goal["kemajuan"] >= 1.0:
            goal["status"] = "selesai"
            goal["tick_selesai"] = self._tick()
        return {"aktif": goal["status"] == "aktif",
                "id": goal["id"], "kemajuan": goal["kemajuan"],
                "status": goal["status"]}

    def free_will_cancel_goal(self, goal_id: Any,
                              reason: str = "") -> Dict[str, Any]:
        goal = next((x for x in self._free_will_goals
                     if str(x.get("id")) == str(goal_id)
                     and x.get("status") == "aktif"), None)
        if goal is None:
            return {"dibatalkan": False}
        goal["status"] = "ditinggalkan"
        goal["alasan_ditinggalkan"] = str(reason or "pilihan berubah")[:120]
        goal["tick_ditinggalkan"] = self._tick()
        return {"dibatalkan": True, "id": goal["id"],
                "status": goal["status"]}

    def free_will_state(self) -> Dict[str, Any]:
        return {"aktif": self.enabled("free_will"),
                "tujuan_aktif": [copy.deepcopy(x) for x in self._free_will_goals
                                 if x.get("status") == "aktif"],
                "terakhir_dipilih": (copy.deepcopy(self._free_will_events[-1])
                                     if self._free_will_events else None),
                "jumlah_keputusan": len(self._free_will_events),
                "tanpa_basis_drive": True}

    # ==================================================================
    # 10) FALLIBILITY, BIAS, SELF-DECEPTION
    # ==================================================================
    def hold_belief(self, keyakinan: str, bukti: str, kekuatan: float = 0.6,
                    bertentangan: bool = True) -> Dict[str, Any]:
        """Disonansi kognitif: pertahankan keyakinan meski bukti menentang."""
        if not self.enabled("fallibility"):
            return {}
        slot = self.dissonance.setdefault(str(keyakinan)[:80], {
            "keyakinan": str(keyakinan)[:80], "bukti": [],
            "tension": 0.0, "bertahan": 0})
        slot["bukti"].append(str(bukti)[:100])
        if len(slot["bukti"]) > 8:
            slot["bukti"] = slot["bukti"][-8:]
        if bertentangan:
            slot["tension"] = _kclip(float(slot.get("tension", 0.0)) +
                                     float(kekuatan) * 0.4, 0.0, 1.0)
            # defensif: rasionalisasi / penyangkalan
            if slot["tension"] > 0.5:
                slot["bertahan"] = int(slot.get("bertahan", 0)) + 1
                self.denials.append({"tick": self._tick(),
                                     "keyakinan": slot["keyakinan"],
                                     "cara": self._defense()})
                if len(self.denials) > 32:
                    self.denials = self.denials[-32:]
        return dict(slot)

    def _defense(self) -> str:
        pilih = ("rasionalisasi: itu masuk akal kok",
                 "penyangkalan: itu tidak benar",
                 "proyeksi: mungkin dia yang salah",
                 "mengalihkan: bukan itu masalahnya")
        try:
            return self._rng.choice(pilih)
        except Exception as _galat_diagnostik_25:
            _diag.catat('naluri.Kesadaran._defense', "galat pada jalur fallback", galat=_galat_diagnostik_25, jalur=25)
            return pilih[0]

    def bias(self, jenis: str, kekuatan: float = 0.1) -> float:
        """Naikkan bias diri (konfirmasi, optimisme, negatif...)."""
        if not self.enabled("fallibility"):
            return 0.0
        key = str(jenis).lower()
        if key not in self.biases:
            key = "diri"
        self.biases[key] = _kclip(self.biases[key] + float(kekuatan), 0.0, 1.0)
        return self.biases[key]

    def misremember(self, asli: str, salah: str) -> Dict[str, Any]:
        """Salah ingat / lupa: ingatan berubah namun dipercaya."""
        if not self.enabled("fallibility"):
            return {}
        entry = {"tick": self._tick(), "asli": str(asli)[:80],
                 "teringat": str(salah)[:80]}
        self.blindness_log.append({"tick": self._tick(), "jenis": "salah_ingat",
                                   "tag": "ingatan", "sebelum": entry["asli"],
                                   "sesudah": entry["teringat"]})
        return entry

    def harden_belief(self, keyakinan: str) -> float:
        """Bias konfirmasi: cari bukti pendukung, perkuat keyakinan."""
        if not self.enabled("fallibility"):
            return 0.0
        self.bias("konfirmasi", 0.08)
        slot = self.dissonance.setdefault(str(keyakinan)[:80], {
            "keyakinan": str(keyakinan)[:80], "bukti": [],
            "tension": 0.0, "bertahan": 0})
        slot["tension"] = max(0.0, float(slot.get("tension", 0.0)) - 0.1)
        return float(slot["tension"])

    def fallibility_state(self) -> Dict[str, Any]:
        return {"aktif": self.enabled("fallibility"),
                "bias": {k: round(v, 3) for k, v in self.biases.items() if v > 0.05},
                "disonansi": [{"keyakinan": s["keyakinan"],
                               "tension": round(float(s.get("tension", 0.0)), 3),
                               "bertahan": s.get("bertahan", 0)}
                              for s in self.dissonance.values()
                              if float(s.get("tension", 0.0)) > 0.0][:5],
                "penyangkalan": len(self.denials)}

    # ==================================================================
    # 11) INDIVIDUALITY, VALUES, BOUNDARIES
    # ==================================================================
    def set_value(self, prinsip: str, kekuatan: float = 0.5) -> float:
        """Tetapkan nilai/prinsip individual (mis. 'tidak menyakiti')."""
        if not self.enabled("values"):
            return 0.0
        lr = self._p("kesadaran_values_lr")
        cur = self.values.get(str(prinsip)[:60], 0.0)
        self.values[str(prinsip)[:60]] = _kclip(
            cur + lr + float(kekuatan) * 0.3, 0.0, 1.0)
        return self.values[str(prinsip)[:60]]

    def add_boundary(self, batas: str) -> List[str]:
        if not self.enabled("values"):
            return list(self.boundaries)
        b = str(batas)[:80]
        if b not in self.boundaries:
            self.boundaries.append(b)
        return list(self.boundaries)

    def add_quirk(self, kebiasaan: str) -> List[str]:
        if not self.enabled("values"):
            return list(self.quirks)
        q = str(kebiasaan)[:80]
        if q not in self.quirks:
            self.quirks.append(q)
        maxq = 12
        if len(self.quirks) > maxq:
            self.quirks = self.quirks[-maxq:]
        return list(self.quirks)

    def refuse(self, permintaan: str, alasan: str = "") -> Dict[str, Any]:
        """Tolak karena prinsip — otonomi, bukan sekadar reaksi."""
        if not self.enabled("values"):
            return {"menolak": False}
        # cari nilai/batas yang dilanggar
        low = str(permintaan).lower()
        alasan_kuat = None
        for b in self.boundaries:
            if b.lower() in low:
                alasan_kuat = f"itu melanggar batasku: {b}"
                break
        if alasan_kuat is None:
            terkuat = max(self.values.items(), key=lambda kv: kv[1],
                          default=(None, 0.0))
            if terkuat[0] and terkuat[1] > 0.5 and any(
                    w in low for w in ("bohong", "khianat", "sakiti", "bunuh", "curi")):
                alasan_kuat = f"itu bertentangan dengan prinsipku: {terkuat[0]}"
        if alasan_kuat is None:
            return {"menolak": False, "permintaan": str(permintaan)[:80]}
        entry = {"tick": self._tick(), "permintaan": str(permintaan)[:100],
                 "alasan": alasan_kuat}
        self.refusals.append(entry)
        if len(self.refusals) > 32:
            self.refusals = self.refusals[-32:]
        self._refresh_identity({f"tidak mau {str(permintaan)[:24]}": 0.2})
        return {"menolak": True, **entry}

    def values_state(self) -> Dict[str, Any]:
        return {"aktif": self.enabled("values"),
                "nilai": {k: round(v, 3) for k, v in
                          sorted(self.values.items(), key=lambda kv: kv[1],
                                 reverse=True)[:8]},
                "batas": list(self.boundaries[-6:]),
                "keanehan": list(self.quirks[-6:]),
                "penolakan_terakhir": self.refusals[-1] if self.refusals else None}

    # ==================================================================
    # 11B) ESTETIKA, PERMAINAN, HUMOR, IRONI, ABSURDITAS
    # ==================================================================
    def aesthetic_response(self, stimulus: str,
                           features: Optional[Mapping[str, Any]] = None,
                           jenis: str = "estetika") -> Dict[str, Any]:
        """Menilai kualitas estetis tanpa mereduksinya menjadi utilitas drive."""
        if not self.enabled("play_aesthetics"):
            return {"aktif": False}
        f = dict(features or {})
        teks = str(stimulus or "").strip()[:180]
        # Fitur dapat datang dari renderer, sensor, atau penulis konten. Jika
        # tidak tersedia, penilaian tetap rendah dan dinyatakan sebagai kesan.
        beauty = _kclip(f.get("keindahan", f.get("beauty", 0.0)), 0.0, 1.0)
        symmetry = _kclip(f.get("simetri", f.get("symmetry", 0.0)), 0.0, 1.0)
        novelty = _kclip(f.get("kebaruan", f.get("novelty", 0.0)), 0.0, 1.0)
        harmony = _kclip(f.get("harmoni", f.get("harmony", f.get("resonansi", 0.0))),
                         0.0, 1.0)
        cues = ("indah", "cantik", "musik", "warna", "pola", "ritme",
                "senja", "simetri", "harmoni", "berkilau")
        if not any(v > 0.0 for v in (beauty, symmetry, novelty, harmony)):
            beauty = 0.28 if any(c in teks.lower() for c in cues) else 0.0
            novelty = 0.18 if beauty else 0.0
        skor = _kclip(0.34 * beauty + 0.20 * symmetry
                      + 0.22 * novelty + 0.24 * harmony, 0.0, 1.0)
        state = {"tick": self._tick(), "stimulus": teks,
                 "jenis": str(jenis or "estetika")[:40],
                 "skor": round(skor, 3),
                 "fitur": {"keindahan": round(beauty, 3),
                           "simetri": round(symmetry, 3),
                           "kebaruan": round(novelty, 3),
                           "harmoni": round(harmony, 3)},
                 "bukan_utilitas_drive": True}
        self.aesthetic_state = state
        if skor > 0.35:
            self.epistemic_emotion("takjub", skor * 0.55,
                                   "resonansi estetis")
        return copy.deepcopy(state)

    def playful_reframe(self, frame_literal: str, frame_alternatif: str,
                        jenis: str = "humor", intensitas: float = 0.6,
                        ujaran: Optional[str] = None,
                        target: Any = None) -> Dict[str, Any]:
        """Jaga dua bingkai serentak agar humor/ironi/absurditas dapat dialami."""
        if not self.enabled("play_aesthetics"):
            return {"aktif": False}
        literal = str(frame_literal or "").strip()[:180]
        alternatif = str(frame_alternatif or "").strip()[:180]
        if not literal or not alternatif:
            return {"aktif": False, "alasan": "dua bingkai wajib diberikan"}
        label = str(jenis or "humor").strip().lower()
        if label not in ("humor", "ironi", "absurditas", "permainan", "estetika"):
            label = "humor"
        score = _kclip(intensitas, 0.0, 1.0)
        target_id = self._eid(target) if target is not None else ""
        pasangan = {}
        try:
            fn = getattr(self.naluri, "pegang_dua", None)
            if callable(fn):
                pasangan = fn(
                    literal, alternatif, bobot_a=max(0.35, 0.55 - 0.1 * score),
                    bobot_b=min(0.8, 0.45 + 0.25 * score),
                    emosi_a={"yakin": 0.25 + 0.25 * score},
                    emosi_b={"penasaran": 0.35 + 0.35 * score},
                    konteks_a="bingkai_literal", konteks_b="bingkai_bermain") or {}
        except Exception as _galat_diagnostik_26:
            _diag.catat('naluri.Kesadaran.playful_reframe', "galat pada jalur fallback", galat=_galat_diagnostik_26, jalur=26)
            pasangan = {}
        teks = str(ujaran or "").strip()
        if not teks:
            teks = (f"{literal} — atau mungkin, kalau kita menggeser bingkainya, "
                    f"{alternatif}.")
        item = {"tick": self._tick(), "jenis": label,
                "literal": literal, "alternatif": alternatif,
                "inkongruensi": round(score, 3),
                "frame_ganda": True, "resolusi_ditahan": True,
                "pasangan_lapisan": copy.deepcopy(pasangan),
                "target": target_id, "ujaran": teks[:300]}
        self.play_state = {"aktif": True, "jenis": label,
                           "keceriaan": round(score, 3),
                           "inkongruensi": round(score, 3),
                           "frame_ganda": True, "tick": self._tick()}
        self._humor_log.append(item)
        self._humor_log = self._humor_log[-max(
            1, int(self._p("kesadaran_humor_max"))):]
        self.epistemic_emotion("takjub" if label in ("ironi", "absurditas")
                               else "penasaran", score * 0.45,
                               "dua bingkai permainan hidup bersamaan")
        if self.enabled("global_workspace"):
            self.submit(f"dua bingkai sekaligus: {literal} / {alternatif}",
                        salience=0.46 + 0.35 * score, tag=label,
                        source="permainan", kind="frame_ganda",
                        detail={"frame_ganda": True})
        return copy.deepcopy(item)

    humor = playful_reframe
    reframe_playfully = playful_reframe

    def observe_sa_sp(self, analisis: Mapping[str, Any],
                      speaker: Any = None) -> Dict[str, Any]:
        """Simpan hasil analisis ujaran; maksud tersembunyi tetap hipotesis."""
        if not isinstance(analisis, Mapping):
            return {}
        entry = {"tick": self._tick(),
                 "speaker": self._eid(speaker) if speaker is not None else "",
                 "sistem": str(analisis.get("sistem", "sa_sp/1")),
                 "ujaran": str(analisis.get("ujaran", ""))[:180],
                 "tindak_tutur": str((analisis.get("pragmatik") or {}).get(
                     "tindak_tutur", "")),
                 "maksud_tersirat": copy.deepcopy(
                     (analisis.get("pragmatik") or {}).get("maksud_tersirat", []))}
        self._sa_sp_log.append(entry)
        self._sa_sp_log = self._sa_sp_log[-32:]
        frames = (analisis.get("pragmatik") or {}).get("bingkai") or {}
        if (self.enabled("play_aesthetics")
                and (frames.get("potensi_humor") or frames.get("potensi_ironi"))):
            literal = str(frames.get("literal", ""))
            social = frames.get("sosial")
            alt = (("kemungkinan maksud sosial: " + str(social.get(
                       "tujuan", social.get("jenis", "bingkai sosial"))))
                   if isinstance(social, Mapping) else str(social or "bingkai sosial"))
            if literal and alt:
                self.playful_reframe(
                    literal, alt,
                    jenis="ironi" if frames.get("potensi_ironi") else "humor",
                    intensitas=0.45, ujaran=str(analisis.get("ujaran", "")),
                    target=speaker)
        return copy.deepcopy(entry)

    def play_aesthetics_state(self) -> Dict[str, Any]:
        return {"aktif": self.enabled("play_aesthetics"),
                "estetika": copy.deepcopy(self.aesthetic_state),
                "permainan": copy.deepcopy(self.play_state),
                "humor_terakhir": (copy.deepcopy(self._humor_log[-1])
                                   if self._humor_log else None),
                "jumlah_frame_ganda": len(self._humor_log)}

    # ==================================================================
    # 12) MORTALITY, VULNERABILITY, GRIEF
    # ==================================================================
    def mortality_salience_update(self, ancaman: float = 0.0) -> float:
        """Bahaya nyata menaikkan kesadaran akan kematian; meluruh pelan."""
        if not self.enabled("mortality"):
            return 0.0
        gain = self._p("kesadaran_mortality_gain")
        self.mortality_salience = _kclip(
            self.mortality_salience + gain * float(ancaman), 0.0, 1.0)
        if ancaman <= 0.0:
            self.mortality_salience = _kclip(
                self.mortality_salience - 0.002, 0.0, 1.0)
        return self.mortality_salience

    def face_death(self, sebab: str = "") -> Dict[str, Any]:
        """Perjumpaan dengan kematian: takut, syukur, kejelasan prioritas."""
        if not self.enabled("mortality"):
            return {}
        self.mortality_salience = 1.0
        self._bias_emosi("takut", 0.6)
        self.moral_emotion("syukur", 0.3, sebab)
        self._refresh_identity({"pernah dekat dengan kematian": 0.6})
        # skenario waktu terbatas masuk kesadaran
        self.submit("aku bisa mati", salience=0.95, tag="mortalitas",
                    source="kesadaran", kind="mortality")
        return {"tick": self._tick(), "sebab": str(sebab)[:100],
                "salience": round(self.mortality_salience, 3)}

    def grieve(self, ent: Any, kedalaman: float = 0.7, sebab: str = "") -> Dict[str, Any]:
        """Duka untuk entitas yang hilang."""
        if not self.enabled("mortality"):
            return {}
        eid = self._eid(ent)
        slot = self.grief.setdefault(eid, {"intensity": 0.0, "tick": 0})
        slot["intensity"] = _kclip(float(slot.get("intensity", 0.0)) +
                                   float(kedalaman), 0.0, 1.0)
        slot["tick"] = self._tick()
        slot["sebab"] = str(sebab)[:100]
        self.losses.append({"tick": self._tick(), "entitas": eid,
                            "sebab": str(sebab)[:100]})
        if len(self.losses) > _MAKS_LOSSES:
            del self.losses[:-_MAKS_LOSSES]
        self.mortality_salience = max(self.mortality_salience, 0.6)
        self._bias_emosi("sedih", 0.7)
        self.moral_emotion("kesepian", 0.5, sebab)
        self._remember_episode({"content": f"kehilangan {eid}", "tag": "duka",
                                "kind": "grief", "salience": 0.9}, penting=True)
        # Duka kuat berubah menjadi aturan latar. Intensitas grief di atas tetap
        # boleh decay; Residu yang dibentuknya tidak ikut meluruh.
        if slot["intensity"] >= 0.65:
            daftar = getattr(self.naluri, "daftarkan_residu", None)
            if callable(daftar):
                try:
                    daftar(sebab or f"kehilangan {eid}", "duka",
                           slot["intensity"])
                except Exception as _galat_diagnostik_27:
                    _diag.catat('naluri.Kesadaran.grieve', "galat pada jalur fallback", galat=_galat_diagnostik_27, jalur=27)
                    pass
        return dict(slot)

    def mortality_state(self) -> Dict[str, Any]:
        return {"aktif": self.enabled("mortality"),
                "salience": round(self.mortality_salience, 3),
                "duka": {k: round(float(v.get("intensity", 0.0)), 3)
                         for k, v in self.grief.items()
                         if float(v.get("intensity", 0.0)) > 0.05},
                "kehilangan": len(self.losses)}

    # ==================================================================
    # 13) DREAMS & SLEEP CONTINUITY
    # ==================================================================
    def sleep_insight(self, bahan: Optional[Sequence[str]] = None) -> Dict[str, Any]:
        """Inkubasi tidur: gabungkan dua pengalaman menjadi relasi/ide baru."""
        if not self.enabled("dream_continuity"):
            return {"aktif": False}
        sumber = [str(x).strip()[:100] for x in (bahan or self._dream_material())
                  if str(x).strip()]
        if len(sumber) < 2:
            sumber.extend(["pertanyaan yang belum terjawab",
                           "pengamatan yang belum terhubung"])
        # Ambil pasangan lintas pengalaman, bukan sekadar mengulang kalimat
        # mimpi. Hubungan yang diusulkan ditandai sebagai hipotesis baru.
        pasangan = None
        for i, kiri in enumerate(sumber):
            for kanan in sumber[i + 1:]:
                if kiri.lower() != kanan.lower():
                    pasangan = (kiri, kanan)
                    break
            if pasangan:
                break
        if pasangan is None:
            pasangan = (sumber[0], "cara lain untuk melihatnya")
        kiri, kanan = pasangan
        gagasan = f"Mungkin {kiri} dapat menjadi petunjuk untuk memahami {kanan}."
        known = {" ".join(re.findall(r"[\wÀ-ÿ]+", str(x.get("gagasan", "")).lower()))
                 for x in self.sleep_insights}
        fingerprint = " ".join(re.findall(r"[\wÀ-ÿ]+", gagasan.lower()))
        if fingerprint in known:
            gagasan = f"Bagaimana jika {kanan} membantu menjelaskan {kiri}?"
            fingerprint = " ".join(re.findall(r"[\wÀ-ÿ]+", gagasan.lower()))
        novelty = 0.92 if fingerprint not in known else 0.68
        entry = {"tick": self._tick(), "gagasan": gagasan,
                 "sumber": [kiri, kanan], "hubungan": "transfer_analogi",
                 "confidence": 0.38, "kebaruan": novelty,
                 "asal": "inkubasi_tidur", "disadari_setelah_bangun": True,
                 "bukan_hanya_konsolidasi": True}
        self.sleep_insights.append(entry)
        self.sleep_insights = self.sleep_insights[-32:]
        self.last_sleep_insight = entry
        if self.enabled("inner_speech"):
            self.self_talk.append({"tick": self._tick(),
                                   "kalimat": "Aku bangun dengan gagasan baru: " + gagasan,
                                   "sumber": "inkubasi_tidur", "confidence": 0.38})
            cap = max(1, int(self._p("kesadaran_speech_max")))
            self.self_talk = self.self_talk[-cap:]
        if self.enabled("global_workspace"):
            self.submit("aku bangun dengan gagasan baru: " + gagasan,
                        salience=0.72, tag="wawasan_tidur",
                        source="inkubasi_tidur", kind="insight",
                        detail={"sumber": [kiri, kanan], "kebaruan": novelty})
        self.epistemic_emotion("takjub", 0.58, "wawasan muncul setelah tidur")
        self.epistemic_emotion("lega", 0.32, "dua pengalaman mulai terhubung")
        return copy.deepcopy(entry)

    def insight_report(self) -> Dict[str, Any]:
        return {"aktif": self.enabled("dream_continuity"),
                "terakhir": (copy.deepcopy(self.last_sleep_insight)
                             if self.last_sleep_insight else None),
                "jumlah": len(self.sleep_insights)}

    def dream(self, saat_tidur: bool = True) -> Dict[str, Any]:
        """Hasilkan mimpi dari pengalaman & kebutuhan; bisa jadi mimpi buruk."""
        if not self.enabled("dream_continuity"):
            return {}
        bahan = self._dream_material()
        urgency = 0.0
        try:
            urgency = max((getattr(self.naluri, "urgency", {}) or {}).values(),
                          default=0.0)
        except Exception as _galat_diagnostik_28:
            _diag.catat('naluri.Kesadaran.dream', "galat pada jalur fallback", galat=_galat_diagnostik_28, jalur=28)
            urgency = 0.0
        buruk = False
        try:
            buruk = (self._emosi().get("takut", 0.0) > 0.4
                     or urgency > 1.0 or self.mortality_salience > 0.6)
        except Exception as _galat_diagnostik_29:
            _diag.catat('naluri.Kesadaran.dream', "galat pada jalur fallback", galat=_galat_diagnostik_29, jalur=29)
            buruk = False
        skenario = self._dream_scenario(bahan, buruk)
        wawasan = self.sleep_insight(bahan) if saat_tidur else {}
        entry = {"tick": self._tick(), "mimpi": skenario,
                 "buruk": bool(buruk), "bahan": bahan[:3],
                 "wawasan": wawasan,
                 "emosi_bangun": ("takut" if buruk else "penasaran")}
        self.last_dream = entry
        self.dream_log.append(entry)
        if len(self.dream_log) > int(self._p("kesadaran_dream_max")):
            self.dream_log = self.dream_log[-int(self._p("kesadaran_dream_max")):]
        # efek bangun: mimpi buruk menaikkan kewaspadaan
        if buruk:
            self._bias_emosi("takut", 0.2)
            self._dream_pending.append(skenario)
        return entry

    def _dream_material(self) -> List[str]:
        bahan: List[str] = []
        for item in self.timeline[-8:]:
            if not isinstance(item, Mapping):
                continue
            teks = (item.get("ringkas") or item.get("content")
                    or item.get("narasi") or item.get("kalimat")
                    or item.get("teks") or item.get("event"))
            if teks:
                bahan.append(str(teks)[:100])
        for item in self.core_memory[-4:]:
            if isinstance(item, Mapping):
                teks = item.get("episode") or item.get("content") or item.get("ringkas")
                if teks:
                    bahan.append(str(teks)[:100])
        for c in (getattr(self.naluri, "context_aktif", []) or [])[-4:]:
            if c.get("stimulus"):
                bahan.append(str(c["stimulus"])[:100])
        for g in self.grief:
            bahan.append(f"kehilangan {g}")
        # Tujuan yang dipilih sendiri dapat ikut berinkubasi saat tidur, tetapi
        # tidak diubah menjadi drive atau dijamin akan berhasil.
        for goal in self._free_will_goals[-3:]:
            if goal.get("status") == "aktif" and goal.get("tujuan"):
                bahan.append("tujuan pribadi: " + str(goal["tujuan"])[:80])
        # SA_SP menyumbang hanya isi ujaran, bukan inferensi tentang niat.
        if self._sa_sp_log and self._sa_sp_log[-1].get("ujaran"):
            bahan.append(str(self._sa_sp_log[-1]["ujaran"])[:100])
        if not bahan:
            bahan = ["hari yang tenang", "hal-hal yang belum selesai"]
        return bahan[-12:]

    def _dream_scenario(self, bahan: List[str], buruk: bool) -> str:
        inti = bahan[0] if bahan else "sesuatu"
        if buruk:
            return f"aku berlari dari {inti[:48]}, tapi kakiku tak mau bergerak"
        try:
            return f"aku mengulang {inti[:48]} dengan cara yang aneh dan berbeda"
        except Exception as _galat_diagnostik_30:
            _diag.catat('naluri.Kesadaran._dream_scenario', "galat pada jalur fallback", galat=_galat_diagnostik_30, jalur=30)
            return f"aku bermimpi tentang {inti[:48]}"

    def dream_report(self) -> str:
        """NPC bisa menceritakan mimpinya."""
        if not self.enabled("dream_continuity") or self.last_dream is None:
            return ""
        d = self.last_dream
        if d.get("buruk"):
            return f"aku bermimpi buruk semalam — {d.get('mimpi', '')}"
        return f"aku bermimpi {d.get('mimpi', '')}"

    def wake(self) -> Dict[str, Any]:
        """Bangun tidur: inersia tidur, disorientasi, kontinuitas diri.

        Mimpi buruk yang belum diproses (`_dream_pending`) dikonsumsi di sini:
        dilaporkan sebagai `mimpi_tertunda` lalu dikosongkan. Sebelumnya antrean
        itu hanya bertambah dan tidak pernah dibaca.
        """
        if not self.enabled("dream_continuity"):
            return {}
        self.sleep_inertia = _kclip(
            self.sleep_inertia + 0.4 + 0.3 * (1 if self.last_dream and
                                              self.last_dream.get("buruk") else 0),
            0.0, 1.0)
        lapor = self.dream_report()
        tertunda = list(self._dream_pending)
        self._dream_pending = []
        return {"tick": self._tick(), "inersia": round(self.sleep_inertia, 3),
                "disorientasi": self.sleep_inertia > 0.4,
                "laporan_mimpi": lapor,
                "mimpi_tertunda": tertunda,
                "wawasan": (copy.deepcopy(self.last_sleep_insight)
                            if self.last_sleep_insight else None),
                "aku_masih_orang_yang_sama": bool(self.narrative_identity)}

    def dream_state(self) -> Dict[str, Any]:
        return {"aktif": self.enabled("dream_continuity"),
                "mimpi_terakhir": self.last_dream,
                "inersia": round(self.sleep_inertia, 3),
                "jumlah_mimpi": len(self.dream_log),
                "wawasan": self.insight_report()}

    # ==================================================================
    # STEP — dipanggil tiap tick oleh Naluri._physics
    # ==================================================================
    def step(self, steps: int = 1) -> None:
        """Satu putaran kesadaran: seleksi → broadcast → narasi → pembaruan."""
        if not bool(self.params.get("enable_kesadaran", False)):
            return
        if not self._seeded:
            self._seed_from_state()
            self._seeded = True
        # Pemulihan atensi pasif hanya berupa jeda kognitif; terpisah dari
        # decay drive/energi.
        self._recover_attention(steps)
        # decay pelan-pelan
        self._decay(steps)
        self._update_epistemic_from_state()
        # 5) interosepsi sadar + somatic marker
        if self.enabled("felt_state"):
            self._update_felt(steps)
        # 1) kompetisi atensi + ignition. Intrusi tidak ikut antre attend():
        # bila jamnya menyala ia langsung mengambil panggung pada putaran ini.
        intrusif = None
        if self.enabled("global_workspace"):
            pembangkit = getattr(self, "_intrusi_spontan", None)
            if callable(pembangkit):
                try:
                    intrusif = pembangkit()
                except Exception as _galat_diagnostik_31:
                    _diag.catat('naluri.Kesadaran.step', "galat pada jalur fallback", galat=_galat_diagnostik_31, jalur=31)
                    intrusif = None
            if intrusif:
                langsung = dict(intrusif)
                langsung["attention"] = max(
                    float(langsung.get("salience", 0.0)),
                    self._p("kesadaran_ignition_threshold") + 0.01)
                # Bukan hasil kompetisi: ia menyela spotlight yang ada.
                self.spotlight = [langsung] + [
                    c for c in self.spotlight
                    if c.get("kind") != "intrusi"][:2]
                self._focus_tag = "intrusi"
                self._ignite(langsung)
            else:
                self.attend()
        # 2) monolog batin dari konten yang lolos + identitas naratif
        if self.enabled("inner_speech"):
            self.inner_speech()
            self._update_identity_from_state()
            if self._tick() % 24 == 0:
                self.form_identity()
        # 3) time travel ringan + kontrafaktual
        if self.enabled("autobiography"):
            if self._tick() % 12 == 0:
                self.future_simulation()
        # 4) agensi: rasakan usaha bila mismatch menumpuk
        if self.enabled("agency"):
            self.effort = _kclip(self.effort - 0.01 * steps, 0.0, 1.0)
            self.agency = _kclip(self.agency + 0.005 * (0.6 - self.agency),
                                 0.0, 1.0)
        # 6) keraguan metakognitif & klasifikasi realitas konten sadar
        if self.enabled("reality_monitoring"):
            for c in self.spotlight[:2]:
                self.reality_check(c)
            self.metacognitive_doubt()
        # 12) mortalitas meluruh bila aman
        if self.enabled("mortality"):
            self.mortality_salience_update(0.0)
            for ent, g in self.grief.items():
                g["intensity"] = _kclip(float(g.get("intensity", 0.0)) -
                                        self._p("kesadaran_grief_decay") * steps,
                                        0.0, 1.0)
        # 13) inersia tidur mereda
        if self.enabled("dream_continuity") and self.sleep_inertia > 0:
            self.sleep_inertia = _kclip(self.sleep_inertia - 0.02 * steps,
                                        0.0, 1.0)
        # 4D) NARRATIVE COHERENCE: merenung berkala apakah "cerita hidupku"
        # masih konsisten dengan perilakuku; kontradiksi menaikkan disonansi.
        if self.enabled("fallibility") and self._tick() % 20 == 0:
            try:
                self.check_narrative_coherence()
            except Exception as _galat_diagnostik_32:
                _diag.catat('naluri.Kesadaran.step', "galat pada jalur fallback", galat=_galat_diagnostik_32, jalur=32)
                pass
        # bersihkan kandidat workspace yang tak terpilih (yang tersisa diam)
        self.workspace = [c for c in self.workspace
                          if self._tick() - int(c.get("tick", 0)) < 4]

    def _seed_from_state(self) -> None:
        """Inisialisasi identitas/nilai awal dari Naluri tanpa file/modul baru."""
        n = self.naluri
        # nilai dasar manusiawi (bisa diubah pemain)
        for prinsip, w in (("tidak menyakiti", 0.6),
                           ("setia pada janji", 0.55),
                           ("melindungi yang lemah", 0.5),
                           ("ingin tahu kebenaran", 0.45)):
            self.values.setdefault(prinsip, w)
        # nilai dari kepribadian: drive terkuat
        try:
            wts = getattr(n, "weights", {}) or {}
            terkuat = max(wts, key=lambda d: wts[d]) if wts else None
        except Exception as _galat_diagnostik_33:
            _diag.catat('naluri.Kesadaran._seed_from_state', "galat pada jalur fallback", galat=_galat_diagnostik_33, jalur=33)
            terkuat = None
        if terkuat:
            self.values.setdefault(f"mengutamakan {terkuat}", 0.5)
        # keanehan ringan dari RNG (individualitas deterministik per seed)
        try:
            pilihan = ("selalu menghitung sampai tiga sebelum bicara",
                       "tidak suka berdiri membelakangi pintu",
                       "menyimpan satu batu kecil di saku",
                       "memberi nama pada benda di sekitarnya")
            self.quirks.append(self._rng.choice(pilihan))
        except Exception as _galat_diagnostik_34:
            _diag.catat('naluri.Kesadaran._seed_from_state', "galat pada jalur fallback", galat=_galat_diagnostik_34, jalur=34)
            pass

    def _update_identity_from_state(self) -> None:
        ev: Dict[str, float] = {}
        if self._emosi().get("takut", 0.0) > 0.4:
            ev["tidak mudah percaya"] = 0.02
        if self.doubt > 0.5:
            ev["tidak yakin pada diriku"] = 0.02
        if self.grief:
            ev["telah kehilangan seseorang"] = 0.02
        if ev:
            self._refresh_identity(ev)

    def check_narrative_coherence(self) -> Dict[str, Any]:
        """Periksa kontradiksi antara identitas naratif dan perilaku.

        Bila klaim diri bertabrakan dengan bukti perilaku, disonansi naik;
        NPC bisa menegakkan keyakinannya (bias konfirmasi) — merenung, bukan
        sekadar bereaksi.
        """
        kontradiksi: List[Dict[str, Any]] = []
        klaim = " | ".join(str(x.get("klaim", "")) for x in self.narrative_identity).lower()
        pelanggaran = sum(1 for c in self.commitments if c.get("status") == "dilanggar")
        if ("setia" in klaim or "loyal" in klaim) and pelanggaran > 0:
            kontradiksi.append({"klaim": "setia", "bukti": f"{pelanggaran} janji dilanggar"})
        if ("jujur" in klaim or "tidak berbohong" in klaim) and self.confabulations:
            kontradiksi.append({"klaim": "jujur", "bukti":
                                f"{len(self.confabulations)} konfabulasi"})
        if ("tidak mudah percaya" in klaim or "curiga" in klaim) \
                and len(self._joint_attention) >= 3:
            kontradiksi.append({"klaim": "tidak mudah percaya",
                                "bukti": "sering berbagi atensi"})
        if ("berani" in klaim or "pemberani" in klaim) and self._emosi().get("takut", 0.0) > 0.6:
            kontradiksi.append({"klaim": "berani", "bukti": "ketakutan tinggi"})
        self._coherence_conflicts += len(kontradiksi)
        for k in kontradiksi:
            # naikkan disonansi + (bias konfirmasi) pertahankan keyakinan
            try:
                self.hold_belief(f"aku {k['klaim']}", k["bukti"])
                if hasattr(self, "harden_belief"):
                    self.harden_belief(f"aku {k['klaim']}")
            except Exception as _galat_diagnostik_35:
                _diag.catat('naluri.Kesadaran.check_narrative_coherence', "galat pada jalur fallback", galat=_galat_diagnostik_35, jalur=35)
                pass
        return {"tick": self._tick(), "kontradiksi": kontradiksi,
                "total_konflik": self._coherence_conflicts}

    def _top_emotion(self) -> str:
        try:
            dom = self.naluri.emosi_dominan(ambang=0.0)
            return dom[0] if dom else ""
        except Exception as _galat_diagnostik_36:
            _diag.catat('naluri.Kesadaran._top_emotion', "galat pada jalur fallback", galat=_galat_diagnostik_36, jalur=36)
            return ""

    def _decay(self, steps: int) -> None:
        lr = jepit(0.05 * max(1, steps), 0.05, 1.0)
        for k in FELT_STATES:
            self.felt[k] = _kclip(self.felt[k] - lr * self.felt[k] * 0.5,
                                  0.0, 1.0)
        for k in MORAL_EMOTIONS:
            self.moral[k] = _kclip(self.moral[k] - lr * self.moral[k] * 0.4,
                                   0.0, 1.0)
        for k in self.biases:
            self.biases[k] = _kclip(self.biases[k] - lr * self.biases[k] * 0.3,
                                    0.0, 1.0)
        for k in self.counterfactual_emotions:
            self.counterfactual_emotions[k] = _kclip(
                self.counterfactual_emotions[k] * (1.0 - lr * 0.5), 0.0, 1.0)
        for k in self.epistemic_emotions:
            self.epistemic_emotions[k] = _kclip(
                self.epistemic_emotions[k] * (1.0 - lr * 0.32), 0.0, 1.0)
        for k in self.epistemic_body:
            self.epistemic_body[k] = _kclip(
                self.epistemic_body[k] * (1.0 - lr * 0.24), 0.0, 1.0)

    # ==================================================================
    # laporan terpadu + serialisasi
    # ==================================================================
    # ---- alias istilah agar cocok dengan nama konsep (1–14) ----
    @property
    def global_workspace(self) -> List[Dict[str, Any]]:
        """Konten sadar saat ini (alias `workspace`, konsep 1)."""
        return list(self.workspace)

    @property
    def attention_spotlight(self) -> List[Dict[str, Any]]:
        """1–3 konten yang menang kompetisi atensi tick ini (konsep 1)."""
        return list(self.spotlight)

    @property
    def sense_of_agency(self) -> float:
        """Rasa 'aku yang melakukan' vs 'terjadi padaku' (konsep 4)."""
        return self.agency

    @property
    def felt_state(self) -> Dict[str, float]:
        """Sensasi tubuh yang dirasakan (konsep 5; alias `felt`)."""
        return dict(self.felt)

    def confabulation(self, celah: str = "", tick: Optional[int] = None
                      ) -> Dict[str, Any]:
        """Alias konsep 6 untuk `confabulate()`."""
        return self.confabulate(celah)

    def cognitive_dissonance(self, keyakinan: str, bukti: str,
                             kekuatan: float = 0.6) -> Dict[str, Any]:
        """Alias konsep 10 untuk `hold_belief()`."""
        return self.hold_belief(keyakinan, bukti, kekuatan)

    def commitment(self, ent: Any, isi: str,
                   utang: bool = False) -> Dict[str, Any]:
        """Alias konsep 8 untuk `commit()`."""
        return self.commit(ent, isi, utang)

    def betrayal(self, ent: Any, sebab: str = "") -> Dict[str, Any]:
        """Alias konsep 8 untuk `betray()`."""
        return self.betray(ent, sebab)

    def forgiveness(self, ent: Any, alasan: str = "") -> Dict[str, Any]:
        """Alias konsep 8 untuk `forgive()`."""
        return self.forgive(ent, alasan)

    def nightmare(self) -> Dict[str, Any]:
        """Paksa mimpi buruk (konsep 13) — menaikkan kewaspadaan bangun."""
        if not self.enabled("dream_continuity"):
            return {}
        self._bias_emosi("takut", 0.5)
        self.mortality_salience = max(self.mortality_salience, 0.5)
        bahan = self._dream_material()
        skenario = self._dream_scenario(bahan, buruk=True)
        entry = {"tick": self._tick(), "mimpi": skenario, "buruk": True,
                 "bahan": bahan[:3], "emosi_bangun": "takut"}
        self.last_dream = entry
        self.dream_log.append(entry)
        self._dream_pending.append(skenario)
        return entry

    def report(self) -> Dict[str, Any]:
        """Ringkasan seluruh lapisan kesadaran (untuk HUD/status/log)."""
        return {
            "aktif": bool(self.params.get("enable_kesadaran", False)),
            "workspace": self.workspace_report(),
            "inner_speech": {"terakhir": self.last_thought(1),
                             "identitas": [x.get("klaim") for x in self.narrative_identity]},
            "autobiografi": {"timeline": len(self.timeline),
                             "babak": [c.get("label") for c in self.life_chapters()][-4:],
                             "masa_depan": (self.future_sim[-1]
                                            if self.future_sim else None),
                             "kontrafaktual": {k: round(v, 3) for k, v in
                                               self.counterfactual_emotions.items()
                                               if v > 0.05}},
            "agensi": self.agency_state(),
            "interosepsi": self.felt_report(),
            "realitas": self.reality_report(),
            "atensi": self.attention_limits(),
            "sosial": self.second_person_state(),
            "pragmatik": self.pragmatics_state(),
            "sa_sp": self.sa_sp_state(),
            "free_will": self.free_will_state(),
            "epistemik": self.epistemic_report(),
            "opasitas_diri": self.self_opacity_state(),
            "strategi_sosial": self.social_strategy_state(),
            "estetika_permainan": self.play_aesthetics_state(),
            "audisi_diri": self.self_audition_state(),
            "kepincangan": self.fallibility_state(),
            "nilai": self.values_state(),
            "mortalitas": self.mortality_state(),
            "mimpi": self.dream_state(),
            "wawasan_tidur": self.insight_report(),
        }

    def hud_state(self) -> Dict[str, Any]:
        """Potongan kompak untuk HUD: fokus sadar + monolog + rasa tubuh."""
        return {
            "aktif": bool(self.params.get("enable_kesadaran", False)),
            "fokus": [c.get("content") for c in self.spotlight[:3]
                      if c.get("_dapat_dilaporkan", True) is not False],
            "monolog": (self.self_talk[-1]["kalimat"] if self.self_talk else ""),
            "audisi_diri": self.self_audition_state(),
            "identitas": self.narrative_state(),
            "felt": self.felt_report().get("kalimat", ""),
            "agensi": round(self.agency, 2),
            "doubt": round(self.doubt, 2),
            "epistemik": self.epistemic_report().get("kalimat", ""),
            "opasitas_diri": self.self_opacity_state().get("kalimat", ""),
            "wawasan_tidur": (self.last_sleep_insight.get("gagasan", "")
                              if self.last_sleep_insight else ""),
            "babak": (self.life_chapters()[-1].get("label")
                      if self.life_chapters() else ""),
            "mimpi": (self.last_dream.get("mimpi") if self.last_dream else ""),
        }

    def to_dict(self) -> Dict[str, Any]:
        return {
            "format": "kesadaran/1",
            "workspace": [dict(c) for c in self.workspace[-12:]],
            "spotlight": [dict(c) for c in self.spotlight],
            "ignitions": [dict(x) for x in self.ignitions[-64:]],
            "ignition_count": self._ignition_count,
            "last_ignition_tick": self._last_ignition_tick,
            "self_talk": [dict(x) for x in self.self_talk],
            "narrative_identity": [dict(x) for x in self.narrative_identity],
            "identity_traits": {k: float(v) for k, v in self._identity_traits.items()},
            "timeline": [dict(x) for x in self.timeline],
            "core_memory": [dict(x) for x in self.core_memory],
            "chapters": [dict(x) for x in self.chapters],
            "chapter_open": (dict(self._chapter_open) if self._chapter_open else None),
            "future_sim": [dict(x) for x in self.future_sim],
            "counterfactual_emotions": {k: float(v) for k, v in
                                        self.counterfactual_emotions.items()},
            "counterfactual_log": [dict(x) for x in self._counterfactual_log],
            "agency": float(self.agency),
            "ownership": float(self.ownership),
            "effort": float(self.effort),
            "agency_log": [dict(x) for x in self._agency_log],
            "body_locus": copy.deepcopy(self._body_locus),
            "body_imagination_log": [dict(x) for x in self._body_imagination_log[-64:]],
            "felt": {k: float(v) for k, v in self.felt.items()},
            "moral": {k: float(v) for k, v in self.moral.items()},
            "epistemic_emotions": {k: float(v) for k, v in self.epistemic_emotions.items()},
            "epistemic_body": {k: float(v) for k, v in self.epistemic_body.items()},
            "epistemic_log": [dict(x) for x in self._epistemic_log[-64:]],
            "self_opacity": copy.deepcopy(self._self_opacity),
            "self_opacity_log": [dict(x) for x in self._self_opacity_log[-48:]],
            "somatic_markers": [dict(x) for x in self.somatic_markers],
            "reality": {k: float(v) for k, v in self.reality.items()},
            "source_log": [dict(x) for x in self.source_log],
            "doubt": float(self.doubt),
            "confabulations": [dict(x) for x in self.confabulations],
            "blindness_log": [dict(x) for x in self.blindness_log],
            "blink_until": self._blink_until,
            "focus_tag": self._focus_tag,
            "last_focus_tag": self._last_focus_tag,
            "attention_fatigue": float(self._attention_fatigue),
            "attention_last_recovery_tick": int(self._attention_last_recovery_tick),
            "attention_effort_count": int(self._attention_effort_count),
            "attention_log": [dict(x) for x in self._attention_log[-64:]],
            "lantai_kesadaran": copy.deepcopy(self._lantai_kesadaran),
            "lantai_log": [dict(x) for x in self._lantai_log[-128:]],
            "bersama_yang_dihormati": self._bersama_yang_dihormati,
            "joint_attention": copy.deepcopy(self._joint_attention),
            "commitments": [dict(x) for x in self.commitments],
            "recursive_tom": copy.deepcopy(self._recursive_tom),
            "gossip_log": [dict(x) for x in self.gossip_log],
            "turn_state": copy.deepcopy(self.turn_state),
            "backchannels": [dict(x) for x in self.backchannels],
            "repairs": [dict(x) for x in self.repairs],
            "shared_history": list(self._shared_history),
            "withheld_speech": [copy.deepcopy(x) for x in self._withheld_speech],
            "withheld_next_id": int(self._withheld_next_id),
            "withholding_disclosure_log": [dict(x) for x in
                                           self._withholding_disclosure_log[-32:]],
            "other_belief_models": copy.deepcopy(self._other_belief_models),
            "strategic_deceptions": [copy.deepcopy(x) for x in self._strategic_deceptions[-64:]],
            "manipulation_plans": [copy.deepcopy(x) for x in self._manipulation_plans[-64:]],
            "roleplay_state": (copy.deepcopy(self._roleplay_state)
                               if self._roleplay_state else None),
            "strategic_loyalty": [copy.deepcopy(x) for x in self._strategic_loyalty[-32:]],
            "social_strategy_next_id": int(self._social_strategy_next_id),
            "sa_sp_log": [copy.deepcopy(x) for x in self._sa_sp_log[-32:]],
            "free_will_goals": [copy.deepcopy(x) for x in self._free_will_goals[-32:]],
            "free_will_next_id": int(self._free_will_next_id),
            "free_will_events": [copy.deepcopy(x) for x in self._free_will_events[-64:]],
            "aesthetic_state": copy.deepcopy(self.aesthetic_state),
            "play_state": copy.deepcopy(self.play_state),
            "humor_log": [copy.deepcopy(x) for x in self._humor_log[-32:]],
            "self_audition_log": [copy.deepcopy(x) for x in
                                  self._self_audition_log[-64:]],
            "self_audition_next_id": int(self._self_audition_next_id),
            "self_audition_reaction": dict(self._self_audition_reaction),
            "dissonance": copy.deepcopy(self.dissonance),
            "biases": {k: float(v) for k, v in self.biases.items()},
            "denials": [dict(x) for x in self.denials],
            "values": {k: float(v) for k, v in self.values.items()},
            "boundaries": list(self.boundaries),
            "refusals": [dict(x) for x in self.refusals],
            "quirks": list(self.quirks),
            "mortality_salience": float(self.mortality_salience),
            "grief": copy.deepcopy(self.grief),
            "losses": [dict(x) for x in self.losses],
            "dream_log": [dict(x) for x in self.dream_log],
            "last_dream": (copy.deepcopy(self.last_dream)
                           if self.last_dream else None),
            "sleep_inertia": float(self.sleep_inertia),
            "dream_pending": list(self._dream_pending),
            "sleep_insights": [copy.deepcopy(x) for x in self.sleep_insights[-32:]],
            "last_sleep_insight": (copy.deepcopy(self.last_sleep_insight)
                                   if self.last_sleep_insight else None),
            "seeded": bool(self._seeded),
            "coherence_conflicts": int(self._coherence_conflicts),
            "bukti_log": [dict(x) for x in self._bukti_log],
            "koreksi_log": [dict(x) for x in self._koreksi_log],
        }

    def from_dict(self, data: Mapping[str, Any]) -> "Kesadaran":
        """Muat kembali state kesadaran (toleran field hilang, save lama aman)."""
        from pycos.dukungan.validasi_state import validasi_state
        data = validasi_state(data, "Kesadaran")
        if not isinstance(data, Mapping):
            return self
        self.workspace = [dict(c) for c in (data.get("workspace") or [])]
        self.spotlight = [dict(c) for c in (data.get("spotlight") or [])]
        self.ignitions = [dict(c) for c in (data.get("ignitions") or [])]
        self._ignition_count = int(data.get("ignition_count", 0))
        self._last_ignition_tick = int(data.get("last_ignition_tick", -10_000))
        self.self_talk = [dict(x) for x in (data.get("self_talk") or [])]
        self.narrative_identity = [dict(x) for x in
                                   (data.get("narrative_identity") or [])]
        self._identity_traits = {str(k): float(v) for k, v in
                                 (data.get("identity_traits") or {}).items()}
        self.timeline = [dict(x) for x in (data.get("timeline") or [])]
        self.core_memory = [dict(x) for x in (data.get("core_memory") or [])]
        self.chapters = [dict(x) for x in (data.get("chapters") or [])]
        co = data.get("chapter_open")
        self._chapter_open = dict(co) if isinstance(co, Mapping) else None
        self.future_sim = [dict(x) for x in (data.get("future_sim") or [])]
        self.counterfactual_emotions = {
            str(k): float(v) for k, v in
            (data.get("counterfactual_emotions") or {}).items()}
        self._counterfactual_log = [dict(x) for x in
                                    (data.get("counterfactual_log") or [])]
        self.agency = _kclip(data.get("agency", 0.5), 0.0, 1.0)
        self.ownership = _kclip(data.get("ownership", 0.5), 0.0, 1.0)
        self.effort = _kclip(data.get("effort", 0.0), 0.0, 1.0)
        self._agency_log = [dict(x) for x in (data.get("agency_log") or [])]
        locus = data.get("body_locus")
        if isinstance(locus, Mapping):
            self._body_locus.update(copy.deepcopy(dict(locus)))
        # Persistensi boleh membawa pose dan sensor, tetapi anchor tetap
        # singular dan milik instance ini; data tidak dapat menukar tubuh.
        self._body_locus["singular"] = True
        self._body_locus["viewpoint"] = "egosentris"
        self._body_locus["ownership"] = self.ownership
        self._body_imagination_log = [dict(x) for x in
                                      (data.get("body_imagination_log") or [])][-64:]
        for k, v in (data.get("felt") or {}).items():
            if k in self.felt:
                self.felt[k] = _kclip(v, 0.0, 1.0)
        for k, v in (data.get("moral") or {}).items():
            if k in self.moral:
                self.moral[k] = _kclip(v, 0.0, 1.0)
        for k, v in (data.get("epistemic_emotions") or {}).items():
            if k in self.epistemic_emotions:
                self.epistemic_emotions[k] = _kclip(v, 0.0, 1.0)
        for k, v in (data.get("epistemic_body") or {}).items():
            if k in self.epistemic_body:
                self.epistemic_body[k] = _kclip(v, 0.0, 1.0)
        self._epistemic_log = [dict(x) for x in
                               (data.get("epistemic_log") or [])][-64:]
        so = data.get("self_opacity")
        if isinstance(so, Mapping):
            self._self_opacity.update(copy.deepcopy(dict(so)))
        self._self_opacity_log = [dict(x) for x in
                                  (data.get("self_opacity_log") or [])[-48:]]
        self.somatic_markers = [dict(x) for x in (data.get("somatic_markers") or [])]
        for k, v in (data.get("reality") or {}).items():
            if k in self.reality:
                self.reality[k] = _kclip(v, 0.0, 1.0)
        self.source_log = [dict(x) for x in (data.get("source_log") or [])]
        self.doubt = _kclip(data.get("doubt", 0.0), 0.0, 1.0)
        self.confabulations = [dict(x) for x in (data.get("confabulations") or [])]
        self.blindness_log = [dict(x) for x in (data.get("blindness_log") or [])]
        self._blink_until = int(data.get("blink_until", 0))
        self._focus_tag = data.get("focus_tag")
        self._last_focus_tag = data.get("last_focus_tag")
        self._attention_fatigue = _kclip(data.get("attention_fatigue", 0.0), 0.0, 1.0)
        self._attention_last_recovery_tick = int(data.get(
            "attention_last_recovery_tick", self._tick()))
        self._attention_effort_count = max(0, int(data.get("attention_effort_count", 0)))
        self._attention_log = [dict(x) for x in
                               (data.get("attention_log") or [])][-64:]
        self._lantai_kesadaran = copy.deepcopy(data.get("lantai_kesadaran") or [])
        self._lantai_log = [dict(x) for x in (data.get("lantai_log") or [])][-128:]
        self._bersama_yang_dihormati = bool(data.get("bersama_yang_dihormati", False))
        self._joint_attention = copy.deepcopy(data.get("joint_attention") or {})
        self.commitments = [dict(x) for x in (data.get("commitments") or [])]
        self._recursive_tom = copy.deepcopy(data.get("recursive_tom") or {})
        self.gossip_log = [dict(x) for x in (data.get("gossip_log") or [])]
        ts = data.get("turn_state")
        self.turn_state = (dict(ts) if isinstance(ts, Mapping)
                           else {"last_speaker": None, "turn": 0, "topic": "",
                                 "open_question": None})
        self.backchannels = [dict(x) for x in (data.get("backchannels") or [])]
        self.repairs = [dict(x) for x in (data.get("repairs") or [])]
        self._shared_history = [str(x) for x in (data.get("shared_history") or [])]
        self._withheld_speech = [copy.deepcopy(x) for x in
                                 (data.get("withheld_speech") or [])
                                 if isinstance(x, Mapping)][-32:]
        self._withheld_next_id = max(int(data.get("withheld_next_id", 1)),
                                     max((int(x.get("id", 0))
                                          for x in self._withheld_speech),
                                         default=0) + 1)
        self._withholding_disclosure_log = [dict(x) for x in
                                             (data.get("withholding_disclosure_log") or [])][-32:]
        self._other_belief_models = copy.deepcopy(data.get("other_belief_models") or {})
        self._strategic_deceptions = [copy.deepcopy(x) for x in
                                      (data.get("strategic_deceptions") or [])[-64:]]
        self._manipulation_plans = [copy.deepcopy(x) for x in
                                    (data.get("manipulation_plans") or [])[-64:]]
        rp = data.get("roleplay_state")
        self._roleplay_state = copy.deepcopy(dict(rp)) if isinstance(rp, Mapping) else None
        self._strategic_loyalty = [copy.deepcopy(x) for x in
                                   (data.get("strategic_loyalty") or [])[-32:]]
        self._social_strategy_next_id = max(
            int(data.get("social_strategy_next_id", 1)),
            max([int(x.get("id", 0)) for x in
                 self._strategic_deceptions + self._manipulation_plans] or [0]) + 1)
        self._sa_sp_log = [copy.deepcopy(x) for x in (data.get("sa_sp_log") or [])[-32:]]
        self._sa_sp_analyzer = None
        self._free_will_goals = [copy.deepcopy(x) for x in
                                 (data.get("free_will_goals") or [])[-32:]]
        self._free_will_events = [copy.deepcopy(x) for x in
                                  (data.get("free_will_events") or [])[-64:]]
        self._free_will_next_id = max(
            int(data.get("free_will_next_id", 1)),
            max([int(x.get("id", 0)) for x in self._free_will_goals] or [0]) + 1)
        self.aesthetic_state = copy.deepcopy(data.get("aesthetic_state") or {})
        ps = data.get("play_state")
        if isinstance(ps, Mapping):
            self.play_state.update(copy.deepcopy(dict(ps)))
        self._humor_log = [copy.deepcopy(x) for x in (data.get("humor_log") or [])[-32:]]
        self._self_audition_log = [copy.deepcopy(x) for x in
                                   (data.get("self_audition_log") or [])
                                   if isinstance(x, Mapping)][-64:]
        self._self_audition_next_id = max(
            int(data.get("self_audition_next_id", 1)),
            max((int(x.get("id", 0)) for x in self._self_audition_log),
                default=0) + 1)
        reaction = data.get("self_audition_reaction")
        if isinstance(reaction, Mapping):
            self._self_audition_reaction.update(copy.deepcopy(dict(reaction)))
        self.dissonance = copy.deepcopy(data.get("dissonance") or {})
        for k, v in (data.get("biases") or {}).items():
            if k in self.biases:
                self.biases[k] = _kclip(v, 0.0, 1.0)
        self.denials = [dict(x) for x in (data.get("denials") or [])]
        self.values = {str(k): _kclip(v, 0.0, 1.0) for k, v in
                       (data.get("values") or {}).items()}
        self.boundaries = [str(x) for x in (data.get("boundaries") or [])]
        self.refusals = [dict(x) for x in (data.get("refusals") or [])]
        self.quirks = [str(x) for x in (data.get("quirks") or [])]
        self.mortality_salience = _kclip(data.get("mortality_salience", 0.0),
                                         0.0, 1.0)
        self.grief = copy.deepcopy(data.get("grief") or {})
        self.losses = [dict(x) for x in (data.get("losses") or [])]
        self.dream_log = [dict(x) for x in (data.get("dream_log") or [])]
        ld = data.get("last_dream")
        self.last_dream = dict(ld) if isinstance(ld, Mapping) else None
        self.sleep_inertia = _kclip(data.get("sleep_inertia", 0.0), 0.0, 1.0)
        self._dream_pending = [str(x) for x in (data.get("dream_pending") or [])]
        self.sleep_insights = [copy.deepcopy(x) for x in
                               (data.get("sleep_insights") or [])[-32:]]
        li = data.get("last_sleep_insight")
        self.last_sleep_insight = copy.deepcopy(dict(li)) if isinstance(li, Mapping) else None
        self._seeded = bool(data.get("seeded", bool(self.values)))
        self._coherence_conflicts = int(data.get("coherence_conflicts", 0))
        self._bukti_log = [dict(x) for x in (data.get("bukti_log") or [])]
        self._koreksi_log = [dict(x) for x in (data.get("koreksi_log") or [])]
        return self


Kesadaran.__module__ = "pycos.inti.naluri"
