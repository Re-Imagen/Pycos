"""View ketidaktahuan: pemasangan eksplisit setelah ekstensi pelindung."""
from __future__ import annotations
from itertools import islice
from typing import Mapping
from pycos.dukungan import diagnostik as _diag
from pycos.dukungan.numerik import jepit, jepit_01
from pycos.dukungan.patching import optional_module, wrap_method
from pycos.inti.kesadaran import Kesadaran
from pycos.inti.presentasi import Presentasi

_kt_view = optional_module("pycos.refleksi.ketidaktahuan")
if _kt_view is not None:
    _kt_batas_pengetahuan = _kt_view.batas_pengetahuan
    _kt_sikap_ketidaktahuan = _kt_view.sikap_ketidaktahuan

    def _kt_context_item(item):
        if not isinstance(item, Mapping):
            return ""
        text = item.get("content", item.get("teks", ""))
        return text[:120] if isinstance(text, str) else ""

    def _kt_kesadaran_candidates(original, self, *args, **kwargs):
        candidates = original(self, *args, **kwargs)
        try:
            if (not isinstance(candidates, list)
                    or not self.enabled("global_workspace")
                    or not candidates):
                return candidates
            npc = getattr(self, "naluri", None)
            if npc is None:
                return candidates
            kuat = {"waspada", "malu", "marah", "kekanak", "bertanya"}
            # Hanya 12 kandidat yang sudah tersedia dibaca, dengan stimulus
            # persepsi/working-memory lebih dahulu daripada goal generik.
            # View tidak meminta retrieval baru dan kandidat tambahan tidak
            # disimpan ke workspace/state Kesadaran sebelum kompetisi berjalan.
            available = list(islice(candidates, 12))
            preferred = [item for item in available
                         if isinstance(item, Mapping)
                         and (item.get("kind") in ("event", "wm")
                              or item.get("source") == "persepsi")]
            fallback = [item for item in available
                        if isinstance(item, Mapping)
                        and item not in preferred]
            for item in (preferred[:4] + fallback[:4]):
                if item.get("kind") == "ketidaktahuan":
                    continue
                proposition = _kt_context_item(item)
                if not proposition or proposition.lower().startswith("aku tidak tahu"):
                    continue
                boundary = _kt_batas_pengetahuan(npc, proposition)
                if boundary.get("kesimpulan") == "tahu":
                    continue
                attitude = _kt_sikap_ketidaktahuan(
                    npc, boundary, {"publik": False})
                if attitude not in kuat:
                    continue
                try:
                    certainty = float(boundary.get("kekuatan_maks", 0.0))
                except (TypeError, ValueError):
                    certainty = 0.0
                salience = jepit(0.42 + 0.16 * certainty, 0.38, 0.62)
                conclusion = boundary.get("kesimpulan")
                prefix = ("aku merasa tahu, tapi belum punya landasan: "
                          if conclusion == "merasa tahu" else
                          "aku tidak bisa tahu " if conclusion == "tidak bisa tahu" else
                          "aku tidak tahu ")
                tag = ("keamanan" if attitude == "waspada" else
                       "afiliasi" if attitude == "malu" else
                       "koherensi" if attitude == "marah" else
                       "keingintahuan")
                candidates.append({
                    "content": prefix + proposition[:96],
                    "salience": salience,
                    "tag": tag,
                    "source": "refleksi_ketidaktahuan",
                    "kind": "ketidaktahuan",
                    "tick": int(getattr(npc, "tick_count", 0)),
                    "detail": {
                        "proposisi": proposition[:120],
                        "kesimpulan": boundary.get("kesimpulan"),
                        "sikap": attitude,
                        "kekuatan": boundary.get("kekuatan_maks", 0.0),
                    },
                })
                break
        except Exception as _galat_diagnostik_255:
            # Integrasi opsional tidak boleh mengganggu seleksi atensi lama.
            _diag.catat('naluri._kt_kesadaran_candidates', "galat pada jalur fallback", galat=_galat_diagnostik_255, jalur=255)
            return candidates
        return candidates


    def _kt_presentasi_skor(original, self, kepada=None, topik=None, masuk=False,
                            *args, **kwargs):
        scores = original(self, kepada, topik, masuk, *args, **kwargs)
        if not isinstance(scores, Mapping):
            return scores
        try:
            npc = getattr(self, "naluri", None)
            if npc is None:
                return scores
            proposition = topik.strip()[:160] if isinstance(topik, str) else ""
            if not proposition:
                kesadaran = getattr(npc, "kesadaran", None)
                spotlight = getattr(kesadaran, "spotlight", ()) or ()
                for item in islice(iter(spotlight), 3):
                    if (isinstance(item, Mapping)
                            and item.get("kind") != "ketidaktahuan"):
                        proposition = _kt_context_item(item)
                        if proposition:
                            break
            if not proposition:
                return scores
            boundary = _kt_batas_pengetahuan(npc, proposition)
            if boundary.get("kesimpulan") == "tahu":
                return scores
            attitude = _kt_sikap_ketidaktahuan(
                npc, boundary,
                {"publik": kepada is not None,
                 "pengamat": kepada} if kepada is not None else {"publik": False})
            # Prior kecil bersifat aditif: act dan skema skor Presentasi tetap
            # milik Presentasi; Boltzmann (bila diaktifkan host) hanya menerima
            # distribusi yang sedikit bergeser.
            prior = 0.06 + 0.08 * jepit_01(float(boundary.get("kekuatan_maks", 0.0) or 0.0))
            nudges = {
                "bertanya": {"bertanya": 1.0, "mengamati": 0.25},
                "waspada": {"waspada": 1.0, "peringatan": 0.60},
                "malu": {"ragu": 0.85, "menimbang": 0.45},
                "marah": {"menegur": 0.80, "menantang": 0.75},
                "kekanak": {"bertanya": 0.80, "menyapa_proaktif": 0.30},
            }
            selected = nudges.get(attitude)
            if not selected:
                return scores
            adjusted = dict(scores)
            for act, multiplier in selected.items():
                if act in adjusted:
                    adjusted[act] = float(adjusted[act]) + prior * multiplier
            return adjusted
        except Exception as _galat_diagnostik_256:
            _diag.catat('naluri._kt_presentasi_skor', "galat pada jalur fallback", galat=_galat_diagnostik_256, jalur=256)
            return scores


    def _kt_tick_doubt(original, self, *args, **kwargs):
        result = original(self, *args, **kwargs)
        try:
            params = getattr(self, "params", {})
            if (not isinstance(params, Mapping)
                    or not params.get("enable_kesadaran", False)
                    or not params.get("enable_global_workspace", True)
                    or getattr(self, "_vacant", False)):
                return result
            mode = getattr(self, "lod_mode", "penuh")
            action_cost = kwargs.get("action_cost")
            if action_cost is None and len(args) > 1:
                action_cost = args[1]
            if mode == "beku" or (mode in ("latar", "abstrak")
                                   and not action_cost
                                   and getattr(self, "_lod_accum", 0) > 0):
                return result
            nurani = getattr(self, "nurani", None)
            kesadaran = getattr(self, "kesadaran", None)
            if (nurani is None or kesadaran is None
                    or not callable(getattr(nurani, "metacognitive_doubt", None))
                    or not callable(getattr(nurani, "enabled", None))
                    or not nurani.enabled("reality_monitoring")
                    or not callable(getattr(nurani, "felt_consciousness", None))
                    or not nurani.felt_consciousness()):
                return result
            spotlight = getattr(kesadaran, "spotlight", ()) or ()
            for item in islice(iter(spotlight), 3):
                if not isinstance(item, Mapping):
                    continue
                detail = item.get("detail", {})
                if item.get("kind") == "ketidaktahuan" and isinstance(detail, Mapping):
                    boundary = {"kesimpulan": detail.get("kesimpulan"),
                                "kekuatan_maks": detail.get("kekuatan", 0.0)}
                    attitude = detail.get("sikap")
                else:
                    proposition = _kt_context_item(item)
                    if not proposition:
                        continue
                    boundary = _kt_batas_pengetahuan(self, proposition)
                    attitude = _kt_sikap_ketidaktahuan(
                        self, boundary, {"publik": False})
                if (boundary.get("kesimpulan") != "tahu"
                        and attitude in ("bertanya", "waspada")):
                    current = float(getattr(nurani, "doubt_level", 0.0) or 0.0)
                    # Efek memakai jalur NURANI yang sudah ada dan tetap tunduk
                    # pada gate reality_monitoring; sikap tenang tidak menulis.
                    nurani.metacognitive_doubt(min(1.0, current + 0.20))
                    break
        except Exception as _galat_diagnostik_257:
            _diag.catat('naluri._kt_tick_doubt', "galat pada jalur fallback", galat=_galat_diagnostik_257, jalur=257)
            pass
        return result





def pasang(Naluri: type) -> None:
    """Pertahankan ketidakhadiran lapisan opsional tanpa memasang wrapper."""
    if _kt_view is None:
        return
    wrap_method(Kesadaran, "_candidates", _kt_kesadaran_candidates,
                patch_id="naluri.ketidaktahuan.kandidat_sementara")

    wrap_method(Presentasi, "_skor_acts", _kt_presentasi_skor,
                patch_id="naluri.ketidaktahuan.prior_presentasi")

    wrap_method(Naluri, "tick", _kt_tick_doubt,
                patch_id="naluri.ketidaktahuan.doubt_nurani")

