"""Reputasi: implementasi terpisah; diekspor ulang oleh inti.naluri."""
from __future__ import annotations

import copy
from typing import Any, Dict, List, Mapping, Optional, Tuple
from pycos.dukungan.numerik import jepit_01, jepit_drive

REPUTASI_DEFAULTS: Dict[str, Any] = {
    "enable_reputasi": False,
    "reputasi_lr": 0.35,            # laju pembaruan sumbu
    "reputasi_half_life": 2000.0,   # peluruhan (tick)
    "reputasi_max_entitas": 64,
    "reputasi_rumor_log_max": 64,
    # --- Fitur 1: bobot kepercayaan gosip (trust weight) ---
    "reputasi_kredibilitas_min": 0.35,  # di bawah ini sumber dianggap
                                     #   tidak kredibel → rumor ditandai
                                     #   alarm_palsu (diabaikan/didiskon)
    "reputasi_liar_confab_max": 3,  # riwayat konfabulasi yang menandai "pembohong"
    "reputasi_bobot_alarm": 0.15,   # bobot efektif sumber alarm_palsu
    # --- Fitur 5: social proof multiplier (konsensus) ---
    "reputasi_social_proof_n": 5,   # jumlah SUMBER BERBEDA dalam jendela →
                                     #   konsensus meng-override kredibilitas
    "reputasi_social_proof_window": 120,  # jendela tick untuk hitung konsensus
    "reputasi_social_proof_mult": 1.8,    # pengali saat konsensus tercapai
}

REPUTASI_SUMBU: Tuple[str, ...] = (
    "kepercayaan", "bahaya", "kedermawanan", "keanehan", "keterampilan",
)


class Reputasi:
    """Reputasi bersama satu scene/kawanan tentang entitas (Player/NPC)."""

    def __init__(self, params: Optional[Dict[str, Any]] = None) -> None:
        self.params: Dict[str, Any] = (params if params is not None
                                       else copy.deepcopy(REPUTASI_DEFAULTS))
        # tentang -> {sumbu: {nilai, n, last_t}, "rumor": [...]}
        self._unit: Dict[str, Dict[str, Any]] = {}
        self._rumor_log: List[Dict[str, Any]] = []
        # Fitur 5: konsensus sosial per (entitas, sumbu) dalam jendela waktu.
        #   {eid: {sumbu: {"sumber": set(), "t0": tick, "n": int}}}
        self._social_proof: Dict[str, Dict[str, Dict[str, Any]]] = {}
        self.social_proof_events: int = 0

    def enabled(self) -> bool:
        return bool(self.params.get("enable_reputasi", False))

    def _p(self, key: str) -> float:
        v = self.params.get(key, REPUTASI_DEFAULTS.get(key, 0.0))
        if isinstance(v, Mapping):
            v = v.get("*", REPUTASI_DEFAULTS.get(key, 0.0))
        try:
            return float(v)
        except (TypeError, ValueError):
            return float(REPUTASI_DEFAULTS.get(key, 0.0))

    def _slot(self, tentang: Any) -> Dict[str, Any]:
        eid = str(getattr(tentang, "name", tentang))
        slot = self._unit.get(eid)
        if slot is None:
            slot = {s: {"nilai": 0.0, "n": 0, "last_t": 0} for s in REPUTASI_SUMBU}
            slot["rumor"] = []
            self._unit[eid] = slot
            cap = int(self._p("reputasi_max_entitas"))
            if cap > 0 and len(self._unit) > cap:
                tertua = min(self._unit, key=lambda k: max(
                    int(v.get("last_t", 0)) for v in self._unit[k].values()
                    if isinstance(v, Mapping)) if self._unit[k] else 0)
                self._unit.pop(tertua, None)
        return slot

    def catat(self, tentang: Any, sumbu: str, nilai: float,
              bobot: float = 1.0, sumber: str = "",
              tick: int = 0) -> Dict[str, Any]:
        """Catat satu pengamatan tentang entitas pada satu sumbu reputasi."""
        if not self.enabled():
            return {}
        if sumbu not in REPUTASI_SUMBU:
            return {}
        slot = self._slot(tentang)
        sel = slot[sumbu]
        lr = jepit_01(self._p("reputasi_lr") * float(bobot))
        sel["nilai"] = jepit_drive(float(sel.get("nilai", 0.0))
                                     + lr * (float(nilai) - float(sel.get("nilai", 0.0))))
        sel["n"] = int(sel.get("n", 0)) + 1
        sel["last_t"] = int(tick)
        return {"entitas": str(getattr(tentang, "name", tentang)),
                "sumbu": sumbu, "nilai": round(sel["nilai"], 4),
                "n": sel["n"]}

    def sebar(self, sumber: Any, tentang: Any, konten: str,
              muatan: float = 0.0, tick: int = 0,
              kredibilitas: float = 0.6,
              alarm_palsu: bool = False) -> Dict[str, Any]:
        """Sebarkan rumor: konten + muatan memengaruhi beberapa sumbu sekaligus.

        `kredibilitas` = bobot kepercayaan sumber (fitur 1). Sumber tidak
        kredibel (`alarm_palsu`) didiskon ke `reputasi_bobot_alarm`, lalu
        fitur 5 menghitung konsensus: bila cukup banyak SUMBER BERBEDA
        menyebar hal serupa dalam jendela singkat, kredibilitas individu
        di-override (desas-desus menjadi "fakta").
        """
        if not self.enabled():
            return {}
        m = jepit_drive(float(muatan))
        sid = str(getattr(sumber, "name", sumber))
        kred = jepit_01(float(kredibilitas))
        if alarm_palsu:
            kred = min(kred, self._p("reputasi_bobot_alarm"))
        # muatan positif → percaya & dermawan naik; negatif → bahaya naik.
        self.catat(tentang, "kepercayaan", m, bobot=kred, sumber=sid, tick=tick)
        self.catat(tentang, "bahaya", max(0.0, -m), bobot=kred, sumber=sid, tick=tick)
        self.catat(tentang, "kedermawanan", max(0.0, m), bobot=kred, sumber=sid, tick=tick)
        entri = {"tick": int(tick), "sumber": sid,
                 "tentang": str(getattr(tentang, "name", tentang)),
                 "konten": str(konten)[:140], "muatan": round(m, 3),
                 "kredibilitas": round(kred, 3),
                 "alarm_palsu": bool(alarm_palsu)}
        # Fitur 5: catat sumber berbeda & mungkin picu penguatan konsensus.
        sp = self._catat_social_proof(tentang, m, sid, tick)
        if sp:
            entri["konsensus"] = sp
        self._rumor_log.append(entri)
        cap = int(self._p("reputasi_rumor_log_max"))
        if cap > 0 and len(self._rumor_log) > cap:
            self._rumor_log = self._rumor_log[-cap:]
        slot = self._slot(tentang)
        slot["rumor"].append(entri)
        if len(slot["rumor"]) > 8:
            slot["rumor"] = slot["rumor"][-8:]
        return entri

    def _catat_social_proof(self, tentang: Any, muatan: float, sumber: str,
                            tick: int) -> Optional[Dict[str, Any]]:
        """Fitur 5: kumpulkan sumber berbeda; bila ambang terlampaui,
        perkuat sumbu (konsensus meng-override kredibilitas individu)."""
        n_butuh = int(self._p("reputasi_social_proof_n"))
        if n_butuh <= 0:
            return None
        jendela = max(1.0, self._p("reputasi_social_proof_window"))
        eid = str(getattr(tentang, "name", tentang))
        sumbu = "bahaya" if float(muatan) < 0.0 else "kepercayaan"
        slot = self._social_proof.setdefault(eid, {}).setdefault(
            sumbu, {"sumber": set(), "t0": int(tick), "n": 0})
        if int(tick) - int(slot.get("t0", tick)) > jendela:
            slot = self._social_proof[eid][sumbu] = {"sumber": set(),
                                                     "t0": int(tick), "n": 0}
        slot["sumber"].add(str(sumber))
        slot["n"] = len(slot["sumber"])
        if slot["n"] < n_butuh:
            return None
        # Konsensus tercapai: dorong sumbu dengan penguatan override.
        mult = max(1.0, self._p("reputasi_social_proof_mult"))
        arah = max(0.0, -float(muatan)) if sumbu == "bahaya" else float(muatan)
        self.catat(tentang, sumbu, arah, bobot=mult, sumber="konsensus",
                   tick=tick)
        self.social_proof_events += 1
        hasil = {"sumbu": sumbu, "n_sumber": slot["n"],
                 "mult": round(mult, 2)}
        slot["sumber"] = set()  # reset agar tidak berulang tiap rumor
        slot["t0"] = int(tick)
        slot["n"] = 0
        return hasil

    def konsensus(self, tentang: Any) -> Dict[str, Any]:
        """Status konsensus sosial entitas (untuk HUD)."""
        eid = str(getattr(tentang, "name", tentang))
        slot = self._social_proof.get(eid, {})
        return {s: {"n_sumber": int(v.get("n", 0)),
                    "sumber": sorted(v.get("sumber", set())),
                    "t0": int(v.get("t0", 0))} for s, v in slot.items()}

    def reputasi(self, tentang: Any) -> Dict[str, Any]:
        """Baca reputasi agregat entitas (JSON-safe) + label + rumor terakhir."""
        if not self.enabled():
            return {"aktif": False}
        eid = str(getattr(tentang, "name", tentang))
        slot = self._unit.get(eid)
        if not slot:
            return {"aktif": True, "entitas": eid, "dikenal": False,
                    "label": "tidak dikenal", "sumbu": {}, "n": 0,
                    "rumor": []}
        sumbu = {s: round(float(slot[s].get("nilai", 0.0)), 3)
                 for s in REPUTASI_SUMBU}
        n = sum(int(slot[s].get("n", 0)) for s in REPUTASI_SUMBU)
        return {"aktif": True, "entitas": eid, "dikenal": n > 0,
                "label": self.label(tentang), "sumbu": sumbu, "n": n,
                "rumor": [dict(x) for x in slot.get("rumor", [])][-3:]}

    def label(self, tentang: Any) -> str:
        """Label reputasi dominan: dipercaya / berbahaya / dermawan / aneh / cakap."""
        eid = str(getattr(tentang, "name", tentang))
        slot = self._unit.get(eid)
        if not slot:
            return "tidak dikenal"
        v = {s: float(slot[s].get("nilai", 0.0)) for s in REPUTASI_SUMBU}
        if max(v.values()) < 0.12 and min(v.values()) > -0.12:
            return "netral"
        dom = max(v, key=lambda s: abs(v[s]))
        peta = {"kepercayaan": ("dipercaya", "tidak dipercaya"),
                "bahaya": ("ditakuti", "aman"),
                "kedermawanan": ("dermawan", "pelit"),
                "keanehan": ("aneh", "biasa"),
                "keterampilan": ("cakap", "canggung")}
        tinggi, rendah = peta[dom]
        return tinggi if v[dom] >= 0 else rendah

    def semua(self) -> Dict[str, str]:
        return {eid: self.label(eid) for eid in self._unit}

    def decay(self, tick: int = 0) -> None:
        """Reputasi memudar perlahan bila tak ada rumor baru."""
        half = max(1.0, self._p("reputasi_half_life"))
        for slot in self._unit.values():
            for s in REPUTASI_SUMBU:
                sel = slot[s]
                age = max(0, int(tick) - int(sel.get("last_t", 0)))
                sel["nilai"] = float(sel.get("nilai", 0.0)) * (0.5 ** (age / half))

    def report(self) -> Dict[str, Any]:
        return {"aktif": self.enabled(),
                "entitas": self.semua(),
                "rumor_terakhir": (self._rumor_log[-1] if self._rumor_log else None)}

    def to_dict(self) -> Dict[str, Any]:
        sp = {eid: {s: {"sumber": sorted(v.get("sumber", set())),
                        "t0": int(v.get("t0", 0)), "n": int(v.get("n", 0))}
                    for s, v in slot.items()}
              for eid, slot in self._social_proof.items()}
        return {"format": "reputasi/2",
                "enable": self.enabled(),
                "params": copy.deepcopy(self.params),
                "unit": copy.deepcopy(self._unit),
                "rumor_log": [dict(x) for x in self._rumor_log],
                "social_proof": sp,
                "social_proof_events": int(self.social_proof_events)}

    def from_dict(self, data: Mapping[str, Any]) -> "Reputasi":
        from pycos.dukungan.validasi_state import validasi_state
        data = validasi_state(data, "Reputasi")
        if not isinstance(data, Mapping):
            return self
        if isinstance(data.get("params"), Mapping):
            self.params.update(copy.deepcopy(dict(data["params"])))
        if "enable" in data:
            self.params["enable_reputasi"] = bool(data.get("enable"))
        self._unit = copy.deepcopy(data.get("unit") or {})
        self._rumor_log = [dict(x) for x in (data.get("rumor_log") or [])]
        self._social_proof = {}
        for eid, slot in (data.get("social_proof") or {}).items():
            self._social_proof[eid] = {}
            for s, v in (slot or {}).items():
                self._social_proof[eid][s] = {
                    "sumber": set(v.get("sumber") or []),
                    "t0": int(v.get("t0", 0)), "n": int(v.get("n", 0))}
        self.social_proof_events = int(data.get("social_proof_events", 0))
        return self


# Jalur kelas historis untuk kompatibilitas pickle.
Reputasi.__module__ = "pycos.inti.naluri"
