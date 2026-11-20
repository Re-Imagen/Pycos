"""Manajemen kawanan NPC, dipisahkan dari facade naluri.

Impor balik ke facade berada di metode pemakai untuk menghindari siklus impor;
modul ini dapat diimpor sebelum maupun sesudah inti.naluri.
"""
from __future__ import annotations

import copy
import json
import math
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple, TYPE_CHECKING
from pycos.dukungan import diagnostik as _diag
from pycos.dukungan.numerik import jepit_01, jepit_drive
from pycos.inti.reputasi import Reputasi

if TYPE_CHECKING:
    from pycos.inti.naluri import Naluri

class KawananNPC:
    """Manajer banyak NPC dalam satu scene (fix konteks).

    Menyatukan: LOD per jarak pemain (fix #2), tick massal, HUD massal
    (fix #7), dan save/load seluruh kawanan ke satu berkas JSON (fix #1).

        kawanan = KawananNPC()
        kawanan.tambah("Rama", personality="penjaga")
        kawanan.tambah("Ana", personality="sosiawan")
        kawanan.set_lod_by_distance("Ana", jarak=42.0)   # -> "beku"
        kawanan.tick_all(events={"Rama": [{"drive": "keamanan", "delta": -0.2,
                                           "reason": "ledakan"}]})
        for baris in kawanan.brief(): print(baris)
        kawanan.save("save/kawanan.json")
    """
    format_versi = "kawanan/5"


    def __init__(self) -> None:
        from pycos.inti.naluri import Naluri
        self.npcs: Dict[str, Naluri] = {}
        # Posisi dunia per NPC (koordinat 2D/3D) untuk jangkauan broadcast.
        self.positions: Dict[str, List[float]] = {}
        # Matriks sparse berarah: observer -> entitas lain -> relasi teramati.
        self.relation_matrix: Dict[str, Dict[str, Dict[str, Any]]] = {}
        # REPUTASI (fitur baru): medan sosial bersama tentang Player/NPC lain.
        self._reputasi = Reputasi()
        # --- SKALABILITAS: spatial hash, event-driven, norma, pasar prediksi ---
        self._grid: Dict[Tuple[int, ...], set] = {}
        self._cell_size: float = 10.0
        self._grid_dirty: bool = True
        self._wake: Dict[str, int] = {}
        self.norms: Dict[str, Dict[str, Any]] = {}
        self._predictions: List[Dict[str, Any]] = []
        self._prediction_credit: Dict[str, float] = {}
        # FITUR 1/2/4: kredibilitas penyebar, faksi terbentuk, peluruhan kebenaran.
        self._source_trust: Dict[str, float] = {}
        self._faksi: List[Dict[str, Any]] = []
        self._truth_decay: Dict[str, Dict[str, Any]] = {}

    # ---------- koleksi ----------
    def tambah(self, nama: str,
               personality: Optional[str] = None,
               *legacy: Any,
               npc: bool = True,
               position: Optional[Any] = None,
               **kwargs: Any) -> Naluri:
        """Buat NPC baru; npc adalah flag NPC_PARAMS, bukan instance.

        Argumen posisi lama untuk npc/position dipertahankan satu siklus
        deprecation. Gunakan serap(existing) untuk menautkan instance host.
        """
        from pycos.inti.naluri import buat_npc
        if legacy:
            import warnings
            if len(legacy) > 2:
                raise TypeError("tambah menerima maksimal dua argumen posisi legacy")
            warnings.warn("npc/position pada tambah harus keyword; gunakan serap untuk instance",
                          DeprecationWarning, stacklevel=2)
            npc = legacy[0]
            if len(legacy) == 2:
                position = legacy[1]
        if not isinstance(npc, bool):
            raise TypeError("npc harus bool (NPC_PARAMS); gunakan serap(npc) untuk instance")
        if nama in self.npcs:
            raise ValueError(f"NPC sudah ada: {nama!r}")
        n = buat_npc(nama, personality=personality, npc=npc, **kwargs)
        self.npcs[nama] = n
        self._grid_dirty = True
        # Tautkan balik agar presentasi/ritual bisa membaca reputasi kawanan.
        try:
            n.kawanan = self
        except Exception as _galat_diagnostik_163:
            _diag.catat('naluri.KawananNPC.tambah', "galat pada jalur fallback", galat=_galat_diagnostik_163, jalur=163)
            pass
        if position is not None:
            self.set_position(nama, position)
        return n

    def serap(self, npc: Naluri, nama: Optional[str] = None,
              position: Optional[Any] = None) -> Naluri:
        """Tautkan NPC yang sama, tanpa membangun ulang params/personality."""
        from pycos.inti.naluri import Naluri
        if not isinstance(npc, Naluri):
            raise TypeError("serap membutuhkan instance Naluri")
        key = npc.name if nama is None else nama
        if not isinstance(key, str) or not key.strip():
            raise ValueError("nama NPC harus string non-kosong")
        if key in self.npcs or any(n is npc for n in self.npcs.values()):
            raise ValueError("NPC atau nama sudah ada dalam kawanan")
        pemilik = getattr(npc, "kawanan", None)
        if pemilik is not None and pemilik is not self:
            raise ValueError("NPC masih terdaftar dalam kawanan lain")
        dirty = self._grid_dirty
        self.npcs[key] = npc
        try:
            if position is not None:
                self.set_position(key, position)
        except (TypeError, ValueError):
            del self.npcs[key]
            self.positions.pop(key, None)
            self._grid_dirty = dirty
            raise
        npc.kawanan = self
        self._grid_dirty = True
        return npc

    tambah_npc = serap

    # ---------- REPUTASI SOSIAL (fitur baru, konsep 8) ----------
    def enable_reputasi(self, aktif: bool = True) -> Dict[str, Any]:
        self._reputasi.params["enable_reputasi"] = bool(aktif)
        return {"enable_reputasi": self._reputasi.enabled()}

    def catat_rumor(self, sumber: Any, tentang: Any, konten: str,
                    muatan: float = 0.0, tick: int = 0,
                    kredibilitas: Optional[float] = None) -> Dict[str, Any]:
        """Satu rumor masuk ke medan reputasi bersama.

        Fitur 1: bila `kredibilitas` tidak diberikan, bobot kepercayaan sumber
        dihitung otomatis (`trust_weight`). Sumber tak kredibel ditandai
        `alarm_palsu` dan persepsi NPC lain menolaknya.
        """
        pen = self._penilaian_sumber(sumber)
        kred = pen["kredibilitas"] if kredibilitas is None else float(kredibilitas)
        entri = self._reputasi.sebar(sumber, tentang, konten, muatan, tick=tick,
                                     kredibilitas=kred,
                                     alarm_palsu=pen["alarm_palsu"])
        if pen["alarm_palsu"]:
            entri["alarm_palsu"] = True
            entri["alasan_alarm"] = pen["alasan"]
            self._tandai_listener_alarm(sumber, konten)
        return entri

    def reputasi(self, tentang: Any) -> Dict[str, Any]:
        """Reputasi bersama tentang entitas (dibaca semua NPC)."""
        return self._reputasi.reputasi(tentang)

    def reputasi_semua(self) -> Dict[str, str]:
        return self._reputasi.semua()

    def terapkan_reputasi(self, tentang: Any, kekuatan: float = 0.5) -> Dict[str, Any]:
        """Reputasi bersama mengendap menjadi relasi tiap NPC (ToM).

        Muatan = sumbu kepercayaan; setiap NPC memperbarui kesannya terhadap
        `tentang` tanpa harus berinteraksi langsung — kesadaran jadi kolektif.
        """
        rep = self._reputasi.reputasi(tentang)
        if not rep.get("dikenal"):
            return {}
        eid = str(getattr(tentang, "name", tentang))
        muatan = jepit_drive(float(rep["sumbu"].get("kepercayaan", 0.0))
                               - float(rep["sumbu"].get("bahaya", 0.0)))
        hasil: Dict[str, Any] = {}
        for nama, n in self.npcs.items():
            if nama == eid:
                continue
            try:
                n.kenal(eid, nama=eid)
                r = n.berinteraksi(eid, muatan=muatan * float(kekuatan),
                                   kepercayaan_delta=muatan * float(kekuatan),
                                   alasan="reputasi yang kudengar")
                self._record_relation(nama, eid, dict(r["relasi"]))
                hasil[nama] = r["label"]
            except Exception as _galat_diagnostik_164:
                _diag.catat('naluri.KawananNPC.terapkan_reputasi', "galat pada jalur fallback", galat=_galat_diagnostik_164, jalur=164)
                continue
        return {"tentang": eid, "label": rep.get("label"),
                "muatan": round(muatan, 3), "relasi": hasil}

    # ---------- PRESENTASI TERINTEGRASI (konsep 7) ----------
    def lihat_player_all(self, present: bool = True) -> Dict[str, Any]:
        """Beri tahu semua NPC bahwa Player hadir/absen (kesadaran temporal)."""
        hasil: Dict[str, Any] = {}
        for nama, n in self.npcs.items():
            pres = getattr(n, "presentasi", None)
            if pres is not None and pres.enabled():
                try:
                    hasil[nama] = pres.lihat_player(present)
                except Exception as _galat_diagnostik_165:
                    _diag.catat('naluri.KawananNPC.lihat_player_all', "galat pada jalur fallback", galat=_galat_diagnostik_165, jalur=165)
                    continue
        return hasil

    def presentasi_all(self, kepada: Any = None) -> Dict[str, Dict[str, Any]]:
        """HUD presentasi seluruh NPC (ekspresi, tatapan, tag, indikator)."""
        hasil: Dict[str, Dict[str, Any]] = {}
        for nama, n in self.npcs.items():
            pres = getattr(n, "presentasi", None)
            if pres is not None and pres.enabled():
                try:
                    hasil[nama] = pres.hud_state(kepada)
                except Exception as _galat_diagnostik_166:
                    _diag.catat('naluri.KawananNPC.presentasi_all', "galat pada jalur fallback", galat=_galat_diagnostik_166, jalur=166)
                    continue
        return hasil

    def tag_all(self) -> Dict[str, str]:
        """Tag dialog dinamis seluruh NPC: '[Rama - Waspada]'."""
        return {nama: (n.presentasi.tag_dialog()
                       if getattr(n, "presentasi", None) is not None
                       and n.presentasi.enabled() else (n.name or nama))
                for nama, n in self.npcs.items()}

    def proaktif_all(self, kepada: Any = None) -> Dict[str, Dict[str, Any]]:
        """Dialog proaktif NPC (Player diam lama / kembali setelah absen)."""
        hasil: Dict[str, Dict[str, Any]] = {}
        for nama, n in self.npcs.items():
            pres = getattr(n, "presentasi", None)
            if pres is not None and pres.enabled():
                try:
                    u = pres.proaktif(kepada)
                    if u:
                        hasil[nama] = u
                except Exception as _galat_diagnostik_167:
                    _diag.catat('naluri.KawananNPC.proaktif_all', "galat pada jalur fallback", galat=_galat_diagnostik_167, jalur=167)
                    continue
        return hasil

    def dialog(self, a: str, b: str, topik: Optional[str] = None) -> Dict[str, Any]:
        """Percakapan dua NPC lewat lapisan PRESENTASI (turn-taking + ToM).

        A berbicara (ucap), B mendengar (dengar) lalu membalas (balas);
        keduanya memperbarui pragmatik kesadaran masing-masing.
        """
        if a not in self.npcs or b not in self.npcs:
            raise KeyError(f"NPC tidak ditemukan: {a!r}/{b!r}")
        na, nb = self.npcs[a], self.npcs[b]
        pa = getattr(na, "presentasi", None)
        pb = getattr(nb, "presentasi", None)
        if pa is None or pb is None or not (pa.enabled() and pb.enabled()):
            # fallback: interaksi sosial lama
            return {"fallback": True, **self.interaksi(a, b)}
        ucapan_a = pa.ucap(kepada=b, topik=topik)
        pb.dengar(ucapan_a.get("teks", ""), a)
        ucapan_b = pb.balas(a)
        pa.dengar(ucapan_b.get("teks", ""), b)
        # reputasi: percakapan memindahkan kesan ringan
        try:
            self._reputasi.catat(b, "keanehan", 0.0, bobot=0.1,
                                sumber=a, tick=na.tick_count)
        except Exception as _galat_diagnostik_168:
            _diag.catat('naluri.KawananNPC.dialog', "galat pada jalur fallback", galat=_galat_diagnostik_168, jalur=168)
            pass
        return {"a": a, "b": b, "ucapan_a": ucapan_a, "ucapan_b": ucapan_b}

    def adegan_all(self, kepada: Any = None,
                   topik: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
        """Satu denyut perilaku (dialog + nonverbal) tiap NPC."""
        hasil: Dict[str, Dict[str, Any]] = {}
        for nama, n in self.npcs.items():
            pres = getattr(n, "presentasi", None)
            if pres is not None and pres.enabled():
                try:
                    hasil[nama] = pres.adegan(kepada=kepada, topik=topik)
                except Exception as _galat_diagnostik_169:
                    _diag.catat('naluri.KawananNPC.adegan_all', "galat pada jalur fallback", galat=_galat_diagnostik_169, jalur=169)
                    continue
        return hasil

    def hapus(self, nama: str) -> Optional[Naluri]:
        removed = self.npcs.pop(nama, None)
        self.positions.pop(str(nama), None)
        self._grid_dirty = True
        self._wake.pop(str(nama), None)
        self.relation_matrix.pop(str(nama), None)
        for row in self.relation_matrix.values():
            row.pop(str(nama), None)
        return removed

    def __getitem__(self, nama: str) -> Naluri:
        return self.npcs[nama]

    def __contains__(self, nama: object) -> bool:
        return nama in self.npcs

    def __iter__(self):
        return iter(self.npcs.values())

    def __len__(self) -> int:
        return len(self.npcs)

    def nama(self) -> List[str]:
        return list(self.npcs)

    def _record_relation(self, observer: str, other: str,
                         relation: Mapping[str, Any]) -> Dict[str, Any]:
        """Catat satu edge sparse observer→other dan perbarui ToM observer."""
        row = self.relation_matrix.setdefault(str(observer), {})
        prior = row.get(str(other), {"valensi": 0.0, "kepercayaan": 0.0,
                                     "akrab": 0.0, "n": 0, "last_t": 0})
        n = int(prior.get("n", 0))
        lr = 1.0 / (n + 1.0)
        item = {"valensi": float(prior.get("valensi", 0.0)) + lr *
                            (float(relation.get("valensi", 0.0)) - float(prior.get("valensi", 0.0))),
                "kepercayaan": float(prior.get("kepercayaan", 0.0)) + lr *
                            (float(relation.get("kepercayaan", 0.0)) - float(prior.get("kepercayaan", 0.0))),
                "akrab": float(prior.get("akrab", 0.0)) + lr *
                         (float(relation.get("akrab", 0.0)) - float(prior.get("akrab", 0.0))),
                "n": n + 1, "last_t": int(relation.get("last_t", 0))}
        row[str(other)] = item
        if len(row) > 128:
            oldest = min(row, key=lambda k: int(row[k].get("last_t", 0)))
            row.pop(oldest, None)
        observer_npc = self.npcs.get(str(observer))
        if observer_npc is not None and observer_npc.nurani is not None:
            confidence = min(0.9, 0.25 + 0.08 * min(5, item["n"]))
            observer_npc.nurani.observe_other_belief(
                str(other), "afiliasi", item["valensi"], confidence=confidence,
                tick=observer_npc.tick_count)
            observer_npc.nurani.observe_other_belief(
                str(other), "keamanan", item["kepercayaan"], confidence=confidence,
                tick=observer_npc.tick_count)
        return dict(item)

    def relasi(self, observer: str, other: str) -> Dict[str, Any]:
        """Baca edge sparse observer→other; kosong bila belum pernah diamati."""
        return dict(self.relation_matrix.get(str(observer), {}).get(str(other), {}))

    def set_position(self, nama: str, position: Any) -> List[float]:
        """Simpan koordinat NPC sebagai tuple/list 2D atau 3D.

        Terima sequence ``(x, y[, z])`` atau mapping dengan kunci ``x, y[, z]``.
        Broadcast tidak menebak posisi NPC yang belum ditempatkan.
        """
        if nama not in self.npcs:
            raise KeyError(f"NPC tidak ditemukan: {nama!r}")
        if isinstance(position, Mapping):
            keys = [k for k in ("x", "y", "z") if k in position]
            values = [position[k] for k in keys]
        elif isinstance(position, (list, tuple)):
            values = list(position)
        else:
            raise TypeError("position harus berupa sequence (x,y[,z]) atau mapping x/y/z")
        if len(values) not in (2, 3):
            raise ValueError("posisi harus memiliki tepat 2 atau 3 koordinat")
        coords = [float(v) for v in values]
        if not all(math.isfinite(v) for v in coords):
            raise ValueError("koordinat posisi harus finite")
        self.positions[str(nama)] = coords
        self._grid_dirty = True
        return list(coords)

    def position_of(self, nama: str) -> Optional[List[float]]:
        """Salinan koordinat NPC; None bila belum diposisikan."""
        pos = self.positions.get(str(nama))
        return list(pos) if pos is not None else None

    # ---------- LOD per jarak (fix #2) ----------
    def set_lod_by_distance(self, nama: str, jarak: float,
                            dekat: float = 10.0, jauh: float = 30.0,
                            divisor: Optional[int] = None) -> Dict[str, Any]:
        """Petakan jarak pemain → LOD hierarkis (5 tingkat).

        <=dekat "penuh"; <=1.5x "ringan"; <=jauh "latar"; <=2x jauh
        "abstrak"; >2x jauh "beku". NPC jauh tetap "hidup" secara emosional
        (valensi/arousal global) tanpa beban introspeksi/presentasi.
        """
        n = self.npcs[nama]
        if jarak <= dekat:
            mode = "penuh"
        elif jarak <= dekat * 1.5:
            mode = "ringan"
        elif jarak <= jauh:
            mode = "latar"
        elif jarak <= jauh * 2.0:
            mode = "abstrak"
        else:
            mode = "beku"
        return n.set_lod(mode, divisor)

    def lod_by_distance_all(self, jarak: Dict[str, float],
                            dekat: float = 10.0, jauh: float = 30.0) -> None:
        for nama, j in jarak.items():
            if nama in self.npcs:
                self.set_lod_by_distance(nama, j, dekat, jauh)

    # ---------- tick massal ----------
    def _rencana_prediksi(self, stimulus: Any, candidates: Any,
                          player_position: Any, radius: Optional[float],
                          max_candidates: Optional[int], max_actions: Optional[int]):
        """Validasi dan klasifikasikan batch sebelum tick/callback host."""
        for key, value in (("max_candidates", max_candidates), ("max_actions", max_actions)):
            if value is not None and (isinstance(value, bool) or not isinstance(value, int) or value < 1):
                raise ValueError(key + " harus integer positif")
        if not isinstance(stimulus, (str, Mapping)):
            raise ValueError("stimulus harus teks atau mapping nama NPC ke teks")
        if isinstance(stimulus, str) and not stimulus.strip():
            raise ValueError("stimulus tidak boleh kosong")
        for data, label in ((stimulus, "stimulus"), (candidates, "candidates")):
            if isinstance(data, Mapping):
                for nama, value in data.items():
                    if nama not in self.npcs:
                        raise ValueError(label + ": NPC tidak dikenal: {!r}".format(nama))
                    if label == "stimulus" and (not isinstance(value, str) or not value.strip()):
                        raise ValueError("stimulus[{}] harus teks non-kosong".format(nama))
                    if label == "candidates":
                        if not isinstance(value, (list, tuple)) or any(
                                not isinstance(c, Mapping) or not isinstance(c.get("name", c.get("action")), str)
                                or not c.get("name", c.get("action", "")).strip() for c in value):
                            raise ValueError("candidates[{}] harus daftar aksi bernama".format(nama))
        if candidates is not None and not isinstance(candidates, Mapping):
            raise ValueError("candidates harus mapping nama NPC ke daftar aksi")
        if (player_position is None) != (radius is None):
            raise ValueError("player_position dan radius harus diberikan bersama")
        if candidates is not None and radius is None:
            raise ValueError("ranking membutuhkan player_position dan radius")
        posisi = None
        if radius is not None:
            from pycos.kontrak import angka
            radius = angka(radius, "radius", 0.0)
            if not isinstance(player_position, (tuple, list)) or len(player_position) not in (2, 3):
                raise ValueError("player_position harus sequence 2D/3D")
            posisi = [angka(x, "player_position") for x in player_position]
        plan = []
        report: Dict[str, Any] = {"predicted": 0, "ranked": 0, "npcs": {}}
        for nama, n in self.npcs.items():
            reason = None
            jejak = getattr(n, "jejak", None)
            cue = stimulus.get(nama) if isinstance(stimulus, Mapping) else stimulus
            if n.lod_mode not in ("penuh", "ringan"):
                reason = "lod_" + n.lod_mode
            elif getattr(n, "_vacancy_aktif", lambda: False)():
                reason = "vacancy"
            elif not callable(getattr(jejak, "predict", None)):
                reason = "no_jejak"
            elif cue is None:
                reason = "missing_stimulus"
            elif posisi is not None:
                pos = self.positions.get(nama)
                if pos is None:
                    reason = "unpositioned"
                else:
                    jarak = math.dist(tuple(pos) + (0.0,) * (3 - len(pos)),
                                      tuple(posisi) + (0.0,) * (3 - len(posisi)))
                    if jarak > radius:
                        reason = "outside_radius"
            actions = candidates.get(nama) if candidates is not None else None
            if reason is None and actions and not callable(getattr(jejak, "rank_actions", None)):
                raise ValueError("JEJAK {} tidak mendukung rank_actions".format(nama))
            report["npcs"][nama] = {"status": "skipped" if reason else "planned", "reason": reason}
            if reason is None:
                plan.append((nama, jejak, cue, actions))
        return plan, report

    def _jalankan_prediksi(self, plan: Any, report: Dict[str, Any],
                           max_candidates: Optional[int], max_actions: Optional[int]) -> Dict[str, Any]:
        self._last_prediction_report = report
        for nama, jejak, cue, actions in plan:
            try:
                if actions:
                    hasil = jejak.rank_actions(cue, actions, max_candidates=max_candidates,
                                               max_actions=max_actions, tick=self.npcs[nama].tick_count)
                    report["ranked"] += 1
                    status = "ranked"
                else:
                    hasil = jejak.predict(cue, tick=self.npcs[nama].tick_count,
                                          max_candidates=max_candidates)
                    report["predicted"] += 1
                    status = "predicted"
                report["npcs"][nama] = {"status": status, "result": hasil}
            except Exception as exc:
                report["npcs"][nama] = {"status": "error", "error": str(exc)}
                for slot in report["npcs"].values():
                    if slot["status"] == "planned":
                        slot.update(status="skipped", reason="batch_aborted")
                _diag.catat("KawananNPC.prediksi_all", "galat prediksi diteruskan", npc=nama, galat=exc)
                raise
        return copy.deepcopy(report)

    def laporan_prediksi(self) -> Dict[str, Any]:
        """Snapshot batch terakhir, termasuk NPC yang dilewati; tidak dipersistensi."""
        return copy.deepcopy(getattr(self, "_last_prediction_report", {}))

    def prediksi_all(self, stimulus: Any, *, candidates: Any = None,
                     player_position: Any = None, radius: Optional[float] = None,
                     max_candidates: Optional[int] = 256,
                     max_actions: Optional[int] = 8) -> Dict[str, Any]:
        """Batch lazy tanpa memajukan tick; ranking hanya dalam radius pemain."""
        plan, report = self._rencana_prediksi(stimulus, candidates, player_position, radius,
                                              max_candidates, max_actions)
        return self._jalankan_prediksi(plan, report, max_candidates, max_actions)

    def tick_all(self, events: Optional[Any] = None,
                 action_cost: Optional[Any] = None, *, predict: bool = False,
                 stimulus: Any = None, candidates: Any = None,
                 player_position: Any = None, radius: Optional[float] = None,
                 max_candidates: Optional[int] = 256,
                 max_actions: Optional[int] = 8) -> None:
        """Tick semua NPC; prediksi opsional setelah seluruh tick selesai.

        Default predict=False mempertahankan perilaku lama. Prediksi melewati
        LOD latar/abstrak/beku dan vacancy. Ranking wajib memiliki radius pemain.
        Pemilihan aksi tidak otomatis menerapkan aksi ke dunia.
        """
        if not isinstance(predict, bool):
            raise ValueError("predict harus bool")
        plan, report = [], {"predicted": 0, "ranked": 0,
                            "npcs": {nama: {"status": "skipped", "reason": "disabled"}
                                     for nama in self.npcs}}
        if predict:
            plan, report = self._rencana_prediksi(stimulus, candidates, player_position, radius,
                                                  max_candidates, max_actions)
        elif any(x is not None for x in (stimulus, candidates, player_position, radius)):
            raise ValueError("opsi prediksi membutuhkan predict=True")
        for nama, n in self.npcs.items():
            ev = events.get(nama) if isinstance(events, dict) else events
            ac = (action_cost.get(nama, False)
                  if isinstance(action_cost, dict) else bool(action_cost))
            n.tick(events=ev, action_cost=ac)
        if predict:
            # Posisi/LOD boleh berubah melalui callback tick host.
            plan, report = self._rencana_prediksi(stimulus, candidates, player_position, radius,
                                                  max_candidates, max_actions)
        self._jalankan_prediksi(plan, report, max_candidates, max_actions)

    def broadcast(self, sumber: str, event: Any, radius: float) -> Dict[str, Any]:
        """Sebarkan event ke NPC berkoordinat di dalam radius.

        Posisi disetel dengan ``set_position(nama, (x,y[,z]))`` dan ikut
        serialisasi kawanan. Atenuasi linear: ``max(0, 1 - jarak/radius)``;
        pada radius nol hanya NPC di koordinat sumber yang menerima kekuatan
        penuh. NPC ``beku`` menyimpan event ber-atenuasi ke buffer dan belum
        mengubah drive sampai LOD dinaikkan. Sumber tidak menerima salinannya.
        """
        from pycos.inti.naluri import DRIVES
        source = str(sumber)
        if source not in self.npcs:
            raise KeyError(f"NPC sumber tidak ditemukan: {source!r}")
        r = float(radius)
        if not math.isfinite(r) or r < 0.0:
            raise ValueError("radius harus bilangan finite non-negatif")
        source_pos = self.positions.get(source)
        report: Dict[str, Any] = {
            "source": source, "radius": r, "delivered": 0,
            "processed": 0, "buffered": 0,
            "skipped_outside_radius": [], "skipped_unpositioned": [],
            "recipients": {},
        }
        if source_pos is None:
            report["reason"] = "source_position_missing"
            return report
        if isinstance(event, Mapping):
            raw_events = [copy.deepcopy(dict(event))]
        elif isinstance(event, Iterable) and not isinstance(event, (str, bytes)):
            event_seq = list(event)
            if any(not isinstance(e, Mapping) for e in event_seq):
                raise TypeError("setiap event harus berupa mapping")
            raw_events = [copy.deepcopy(dict(e)) for e in event_seq]
            if not raw_events:
                raise ValueError("event iterable harus memuat setidaknya satu mapping")
        else:
            raise TypeError("event harus berupa mapping atau iterable mapping")

        def _for_distance(distance: float) -> Tuple[float, List[Dict[str, Any]]]:
            factor = (1.0 if distance <= 1e-12 else 0.0) if r == 0.0 else max(0.0, 1.0 - distance / r)
            expanded: List[Dict[str, Any]] = []
            for raw in raw_events:
                if isinstance(raw.get("drive_deltas"), Mapping):
                    drive_map = raw.get("drive_deltas") or {}
                    base = {k: copy.deepcopy(v) for k, v in raw.items()
                            if k not in ("drive_deltas", "drive", "delta")}
                    valid = [(str(d), float(v)) for d, v in sorted(drive_map.items(), key=lambda kv: str(kv[0]))
                             if d in DRIVES]
                    if not valid and raw.get("emosi"):
                        valid = [("", 0.0)]
                    for index, (drive, amount) in enumerate(valid):
                        item = copy.deepcopy(base)
                        if drive:
                            item["drive"] = drive
                            item["delta"] = amount * factor
                        if index > 0:
                            item.pop("emosi", None)
                            item.pop("intensitas", None)
                        if item.get("emosi"):
                            item["intensitas"] = float(item.get("intensitas", 0.5)) * factor
                        if "salience" in item:
                            item["salience"] = float(item["salience"]) * factor
                        expanded.append(item)
                else:
                    item = copy.deepcopy(raw)
                    if "delta" in item:
                        item["delta"] = float(item["delta"]) * factor
                    if item.get("emosi"):
                        item["intensitas"] = float(item.get("intensitas", 0.5)) * factor
                    if "salience" in item:
                        item["salience"] = float(item["salience"]) * factor
                    expanded.append(item)
            annotated: List[Dict[str, Any]] = []
            for item in expanded:
                item.setdefault("source", f"broadcast:{source}")
                if "salience" not in item:
                    item["salience"] = factor
                item["broadcast"] = {
                    "source": source, "distance": round(distance, 6),
                    "radius": r, "attenuation": round(factor, 6),
                }
                annotated.append(item)
            return factor, annotated

        # SPATIAL HASH: hanya NPC di cell sekitar yang diuji (bukan semua).
        for nama in sorted(self._nearby(source_pos, r)):
            if nama == source:
                continue
            target_pos = self.positions.get(nama)
            if target_pos is None:
                report["skipped_unpositioned"].append(nama)
                continue
            ndim = max(len(source_pos), len(target_pos))
            distance = math.sqrt(sum(
                ((source_pos[i] if i < len(source_pos) else 0.0)
                 - (target_pos[i] if i < len(target_pos) else 0.0)) ** 2
                for i in range(ndim)))
            if distance > r:
                report["skipped_outside_radius"].append({
                    "name": nama, "distance": round(distance, 6)})
                continue
            factor, received = _for_distance(distance)
            npc = self.npcs[nama]
            if npc.lod_mode == "beku":
                npc._buffer_events(received)
                status = "buffered"
                count = min(len(received), 64)
                report["buffered"] += 1
            else:
                npc.apply_events(received)
                status = "processed"
                count = len(received)
                report["processed"] += 1
            report["delivered"] += 1
            report["recipients"][nama] = {
                "distance": round(distance, 6),
                "attenuation": round(factor, 6),
                "status": status,
                "events": count,
                "dropped_events": (max(0, len(received) - count)
                                   if status == "buffered" else 0),
                "buffer_size": len(npc._event_buffer),
            }
        return report

    # ---------- HUD massal (fix #7) ----------
    def hud_all(self, relasi_dengan: Optional[Any] = None
                 ) -> Dict[str, Dict[str, Any]]:
        return {nama: n.hud_state(relasi_dengan=relasi_dengan)
                for nama, n in self.npcs.items()}

    def brief(self) -> List[str]:
        return [n.brief() for n in self.npcs.values()]

    # ---------- interaksi antar-NPC (EMPATI) ----------
    def interaksi(self, a: str, b: str,
                  muatan: Any = 0.2,
                  alasan: str = "mengobrol") -> Dict[str, Any]:
        """Dua NPC saling berinteraksi; KEDUA sisi tercatat.

        `muatan` boleh skalar (sama untuk kedua arah) atau tuple (a→b, b→a)
        untuk interaksi asimetris (A menghina B: (-0.8 dari sisi B, ...)).
        Konvensi: muatan[0] = valensi yang DIRASAKAN a, muatan[1] = yang
        dirasakan b. Mengembalikan ringkasan relasi kedua sisi.
        """
        na, nb = self.npcs[a], self.npcs[b]
        m_ab, m_ba = (muatan if isinstance(muatan, (tuple, list))
                      else (muatan, muatan))
        na.kenal(b, nama=b)
        nb.kenal(a, nama=a)
        ra = na.berinteraksi(b, muatan=float(m_ab),
                             kepercayaan_delta=float(m_ab) * 0.5,
                             alasan=f"{alasan} dengan {b}")
        rb = nb.berinteraksi(a, muatan=float(m_ba),
                             kepercayaan_delta=float(m_ba) * 0.5,
                             alasan=f"{alasan} dengan {a}")
        # Relasi milik pihak lain adalah petunjuk ToM (bukan akses ke pikiran).
        # Jika social_memory dimatikan, gunakan muatan interaksi yang tampak
        # sebagai observasi lemah alih-alih mengunci matriks ke nilai netral.
        rel_b = dict(rb["relasi"])
        rel_a = dict(ra["relasi"])
        if not rel_b.get("dikenal"):
            rel_b.update({"valensi": jepit_drive(float(m_ba)),
                          "kepercayaan": jepit_drive(float(m_ba) * 0.5),
                          "akrab": 0.0, "last_t": nb.tick_count})
        if not rel_a.get("dikenal"):
            rel_a.update({"valensi": jepit_drive(float(m_ab)),
                          "kepercayaan": jepit_drive(float(m_ab) * 0.5),
                          "akrab": 0.0, "last_t": na.tick_count})
        self._record_relation(a, b, rel_b)
        self._record_relation(b, a, rel_a)
        return {a: {"label": ra["label"], "relasi": ra["relasi"]},
                b: {"label": rb["label"], "relasi": rb["relasi"]}}

    def biarkan_bersosialisasi(self, muatan: float = 0.25,
                                maks_pasangan: int = 3,
                                ambang_defisit: float = 0.1
                                ) -> List[Dict[str, Any]]:
        """NPC yang 'kesepian' (defisit afiliasi di atas ambang) dipasangkan
        dan mengobrol — perilaku sosial emergent yang murah untuk scene.

        Pasangan dibentuk dari yang PALING kesepian; butuh minimal dua NPC
        di atas ambang. Mengembalikan daftar ringkasan `interaksi()`.
        """
        item = sorted(((nm, n) for nm, n in self.npcs.items()
                       if n.deficit("afiliasi") > ambang_defisit),
                      key=lambda kv: -kv[1].deficit("afiliasi"))
        hasil: List[Dict[str, Any]] = []
        dipakai = set()
        for i, (nm_a, _a) in enumerate(item):
            if len(hasil) >= maks_pasangan:
                break
            if nm_a in dipakai:
                continue
            for nm_b, _b in item[i + 1:]:
                if nm_b in dipakai:
                    continue
                dipakai.add(nm_a)
                dipakai.add(nm_b)
                hasil.append(self.interaksi(nm_a, nm_b, muatan=muatan,
                                            alasan="obrolan spontan"))
                break
        return hasil

    # ==================== SKALABILITAS: SPATIAL HASH & BATCH ====================
    def _cell_key(self, pos: Sequence[float]) -> Tuple[int, ...]:
        cs = max(1e-6, float(self._cell_size))
        return tuple(int(math.floor(float(c) / cs)) for c in list(pos)[:3])

    @staticmethod
    def _offsets(dim: int, rng: int) -> List[Tuple[int, ...]]:
        hasil: List[Tuple[int, ...]] = []
        if dim <= 1:
            for a in range(-rng, rng + 1):
                hasil.append((a,))
        elif dim == 2:
            for a in range(-rng, rng + 1):
                for b in range(-rng, rng + 1):
                    hasil.append((a, b))
        else:
            for a in range(-rng, rng + 1):
                for b in range(-rng, rng + 1):
                    for c in range(-rng, rng + 1):
                        hasil.append((a, b, c))
        return hasil

    def _reindex_grid(self) -> None:
        """Bangun ulang spatial hash dari posisi NPC."""
        self._grid = {}
        for nama, pos in self.positions.items():
            self._grid.setdefault(self._cell_key(pos), set()).add(str(nama))
        self._grid_dirty = False

    def _nearby(self, pos: Optional[Sequence[float]], radius: float) -> set:
        """Kandidat NPC di cell sekitar (spatial hash) + yang belum diposisikan."""
        if pos is None:
            return set(self.npcs)
        if self._grid_dirty:
            self._reindex_grid()
        cs = max(1e-6, float(self._cell_size))
        rng = int(math.ceil(max(0.0, float(radius)) / cs))
        base = self._cell_key(pos)
        out: set = set()
        for off in self._offsets(len(base), rng):
            key = tuple(base[i] + off[i] for i in range(len(base)))
            out.update(self._grid.get(key, ()))
        out.update(n for n in self.npcs if n not in self.positions)
        return out

    def _pairs_within(self, radius: float) -> List[Tuple[str, str, float]]:
        """Pasangan NPC bertetangga (untuk contagion/obrolan) via grid."""
        if self._grid_dirty:
            self._reindex_grid()
        pairs: List[Tuple[str, str, float]] = []
        for nama, pos in self.positions.items():
            for other in self._nearby(pos, radius):
                if str(other) <= str(nama):
                    continue
                op = self.positions.get(str(other))
                if op is None:
                    continue
                ndim = max(len(pos), len(op))
                dist = math.sqrt(sum(
                    ((pos[i] if i < len(pos) else 0.0)
                     - (op[i] if i < len(op) else 0.0)) ** 2 for i in range(ndim)))
                if dist <= radius:
                    pairs.append((str(nama), str(other), dist))
        return pairs

    def tick_batch(self, events: Optional[Any] = None,
                   action_cost: Optional[Any] = None) -> None:
        """Tick massal: NPC \"beku\" hanya buffer (tanpa function-call berat)."""
        for nama, n in self.npcs.items():
            ev = events.get(nama) if isinstance(events, dict) else events
            if n.lod_mode == "beku":
                if ev:
                    n._buffer_events(ev)
                continue
            ac = (action_cost.get(nama, False)
                  if isinstance(action_cost, dict) else bool(action_cost))
            n.tick(events=ev, action_cost=ac)

    # ==================== EVENT-DRIVEN ARCHITECTURE ====================
    def wake(self, nama: str, ticks: int = 10) -> int:
        """Jadwalkan NPC untuk \"bangun\" (diproses) selama `ticks` berikutnya."""
        n = self.npcs.get(str(nama))
        if n is None:
            return 0
        sampai = n.tick_count + max(0, int(ticks))
        self._wake[str(nama)] = max(self._wake.get(str(nama), 0), sampai)
        return sampai

    def should_wake(self, nama: str, events: Optional[Any] = None) -> bool:
        """Apakah NPC perlu diproses tick ini (event-driven)."""
        from pycos.inti.naluri import DRIVES
        n = self.npcs.get(str(nama))
        if n is None:
            return False
        if events:
            return True
        if n.lod_mode in ("penuh", "ringan"):
            return True
        if str(nama) in self._wake and n.tick_count <= self._wake[str(nama)]:
            return True
        if any(n.deficit(d) > 0.5 for d in DRIVES):
            return True
        if int(getattr(n, "_unverified_predictions", 0)) > 0:
            return True
        return False

    def tick_event_driven(self, events: Optional[Any] = None,
                          action_cost: Optional[Any] = None) -> Dict[str, int]:
        """Hanya NPC yang \"bangun\" di-tick; sisanya buffer event (hemat ~90%)."""
        diproses = 0
        dibuffer = 0
        for nama, n in self.npcs.items():
            ev = events.get(nama) if isinstance(events, dict) else events
            if self.should_wake(nama, ev):
                ac = (action_cost.get(nama, False)
                      if isinstance(action_cost, dict) else bool(action_cost))
                n.tick(events=ev, action_cost=ac)
                diproses += 1
            elif ev:
                n._buffer_events(ev)
                dibuffer += 1
        return {"processed": diproses, "buffered": dibuffer,
                "total": len(self.npcs)}

    # ==================== KONTAGI EMOSI (4B) ====================
    def emotional_contagion(self, radius: float = 8.0,
                            strength: float = 0.12) -> Dict[str, int]:
        """Emosi menyebar antar NPC berdekatan (scene terasa hidup)."""
        from pycos.inti.naluri import EMOSI
        pairs = self._pairs_within(radius)
        tersentuh: set = set()
        for a, b, dist in pairs:
            na, nb = self.npcs[a], self.npcs[b]
            factor = max(0.0, 1.0 - dist / max(1e-6, radius)) * float(strength)
            if factor <= 0.0:
                continue
            snap_a = {e: float(na.emosi.get(e, 0.0)) for e in EMOSI}
            snap_b = {e: float(nb.emosi.get(e, 0.0)) for e in EMOSI}
            for e in EMOSI:
                da = (snap_b[e] - snap_a[e]) * factor
                db = (snap_a[e] - snap_b[e]) * factor
                na.emosi[e] = jepit_01(snap_a[e] + da)
                nb.emosi[e] = jepit_01(snap_b[e] + db)
            tersentuh.add(a)
            tersentuh.add(b)
        return {"pairs": len(pairs), "touched": len(tersentuh)}

    # ==================== SOCIAL LEARNING (4A) ====================
    def social_learn(self, pengamat: str, model: str, aksi: str,
                     nilai: Optional[float] = None) -> Dict[str, Any]:
        """Observational learning: pengamat meniru nilai aksi model."""
        from pycos.inti.naluri import DRIVES
        na = self.npcs.get(str(pengamat))
        nb = self.npcs.get(str(model))
        if na is None or nb is None:
            return {}
        if nilai is None:
            slot = (getattr(nb, "_action_values", {}) or {}).get(str(aksi), {})
            nilai = float(slot.get("value", 0.0))
        slot = (na._action_values.setdefault(str(aksi), {
            "value": 0.0, "n": 0, "last_t": na.tick_count,
            "drive_values": {d: 0.0 for d in DRIVES},
            "drive_n": {d: 0 for d in DRIVES}}))
        lr = 0.2
        slot["value"] = jepit_drive(float(slot.get("value", 0.0))
                                       + lr * (float(nilai) - float(slot.get("value", 0.0))))
        slot["n"] = int(slot.get("n", 0)) + 1
        slot["last_t"] = na.tick_count
        try:
            self._reputasi.catat(model, "keterampilan", max(0.0, float(nilai)),
                                 bobot=0.3, sumber=str(pengamat), tick=na.tick_count)
        except Exception as _galat_diagnostik_170:
            _diag.catat('naluri.KawananNPC.social_learn', "galat pada jalur fallback", galat=_galat_diagnostik_170, jalur=170)
            pass
        return {"pengamat": str(pengamat), "model": str(model), "aksi": str(aksi),
                "nilai": round(float(slot["value"]), 4)}

    def teaching(self, guru: str, murid: str, aksi: str) -> Dict[str, Any]:
        """Alias eksplisit untuk transfer pengetahuan (guru → murid)."""
        return self.social_learn(murid, guru, aksi)

    def form_cultural_norms(self, ambang: float = 0.5) -> Dict[str, Any]:
        """Norma bersama dari nilai/batas yang dianut mayoritas NPC."""
        counts: Dict[str, int] = {}
        total = 0
        for n in self.npcs.values():
            ks = getattr(n, "kesadaran", None)
            if ks is None:
                continue
            total += 1
            for v in list(getattr(ks, "values", {}) or {}):
                counts[v] = counts.get(v, 0) + 1
            for bnd in list(getattr(ks, "boundaries", []) or []):
                counts[bnd] = counts.get(bnd, 0) + 1
        norms = {k: {"dukungan": round(c / max(1, total), 3), "n": c}
                 for k, c in counts.items() if c / max(1, total) >= float(ambang)}
        self.norms = norms
        # endapkan norma lemah ke NPC yang belum menganutnya
        for n in self.npcs.values():
            ks = getattr(n, "kesadaran", None)
            if ks is None:
                continue
            for k in norms:
                if k in (getattr(ks, "values", {}) or {}):
                    continue
                if k in (getattr(ks, "boundaries", []) or []):
                    continue
                try:
                    ks.set_value(k, 0.2)
                except Exception as _galat_diagnostik_171:
                    _diag.catat('naluri.KawananNPC.form_cultural_norms', "galat pada jalur fallback", galat=_galat_diagnostik_171, jalur=171)
                    pass
        return norms

    # ==================== MEMORI KOLEKTIF & GOSSIP (4C) ====================
    _KATA_NEGATIF = ("menipu", "bohong", "khianat", "jahat", "menyakiti",
                     "mencuri", "berbahaya", "kejam", "meninggalkan", "pergi")
    _KATA_POSITIF = ("menolong", "baik", "memberi", "menyelamatkan",
                     "jujur", "setia", "ramah", "peduli", "melindungi")

    @classmethod
    def _gossip_valence(cls, konten: str) -> float:
        """Sentimen ringan dari isi gossip (bukan NLP penuh) → muatan reputasi."""
        low = str(konten or "").lower()
        neg = sum(1 for w in cls._KATA_NEGATIF if w in low)
        pos = sum(1 for w in cls._KATA_POSITIF if w in low)
        if neg == 0 and pos == 0:
            return 0.0
        return jepit_drive((pos - neg) / max(1, pos + neg))

    def gossip_round(self, radius: float = 12.0,
                     muatan: Optional[float] = None,
                     decay: bool = True) -> Dict[str, Any]:
        """NPC menyebarkan gossip terakhir ke tetangga → reputasi bersama.

        `muatan=None` (default) menurunkan muatan dari sentimen isi gossip,
        sehingga rumor negatif benar-benar menurunkan reputasi.
        """
        tersebar = 0
        for nama, n in self.npcs.items():
            ks = getattr(n, "kesadaran", None)
            if ks is None:
                continue
            log = getattr(ks, "gossip_log", []) or []
            if not log:
                continue
            g = log[-1]
            isi = g.get("isi", "")
            m = (self._gossip_valence(isi) if muatan is None
                 else float(muatan))
            # Fitur 1: bobot kepercayaan penyebar (bukan kredibilitas tetap).
            pen = self._penilaian_sumber(nama)
            pos = self.positions.get(nama)
            for tetangga in self._nearby(pos, radius):
                if str(tetangga) == str(nama):
                    continue
                try:
                    self._reputasi.sebar(nama, g.get("tentang", "?"),
                                         isi, muatan=m, tick=n.tick_count,
                                         kredibilitas=pen["kredibilitas"],
                                         alarm_palsu=pen["alarm_palsu"])
                    tersebar += 1
                    if pen["alarm_palsu"]:
                        tn = self.npcs.get(str(tetangga))
                        tks = getattr(tn, "kesadaran", None) if tn else None
                        if tks is not None:
                            tks.tandai_alarm_palsu(nama, isi)
                except Exception as _galat_diagnostik_172:
                    _diag.catat('naluri.KawananNPC.gossip_round', "galat pada jalur fallback", galat=_galat_diagnostik_172, jalur=172)
                    continue
        if decay:
            self._reputasi.decay(self._max_tick())
        return {"tersebar": tersebar, "reputasi": self._reputasi.report()}

    def shared_narrative(self, min_sumber: int = 2) -> List[Dict[str, Any]]:
        """Cerita yang dipercaya banyak NPC → \"sejarah resmi\" kawanan."""
        hitung: Dict[str, Dict[str, Any]] = {}
        for entri in self._reputasi._rumor_log:
            kunci = f"{entri.get('tentang')}|{str(entri.get('konten'))[:48]}"
            slot = hitung.setdefault(kunci, {"tentang": entri.get("tentang"),
                                             "konten": entri.get("konten"),
                                             "sumber": set(), "muatan": []})
            slot["sumber"].add(entri.get("sumber"))
            slot["muatan"].append(float(entri.get("muatan", 0.0)))
        hasil = []
        for slot in hitung.values():
            if len(slot["sumber"]) >= int(min_sumber):
                muatan = sum(slot["muatan"]) / max(1, len(slot["muatan"]))
                hasil.append({"tentang": slot["tentang"], "konten": slot["konten"],
                              "n_sumber": len(slot["sumber"]),
                              "muatan": round(muatan, 3)})
        hasil.sort(key=lambda x: x["n_sumber"], reverse=True)
        return hasil

    def _max_tick(self) -> int:
        return max((n.tick_count for n in self.npcs.values()), default=0)

    # ==================== PASAR PREDIKSI ANTAR-NPC (4E) ====================
    def share_prediction(self, nama: str, stimulus: str,
                         forecast: Mapping[str, Any]) -> Dict[str, Any]:
        """NPC membagikan prediksi masa depan (untuk dinilai saat terbukti)."""
        n = self.npcs.get(str(nama))
        if n is None:
            return {}
        entri = {"tick": n.tick_count, "nama": str(nama),
                 "stimulus": str(stimulus)[:120],
                 "forecast": dict(forecast), "resolved": False}
        self._predictions.append(entri)
        if len(self._predictions) > 256:
            self._predictions = self._predictions[-256:]
        return dict(entri)

    def resolve_predictions(self, stimulus: str, actual_impact: float,
                            tolerance: float = 0.3) -> List[Dict[str, Any]]:
        """Bandingkan prediksi dengan realita; yang akurat dapat bonus koherensi."""
        hasil: List[Dict[str, Any]] = []
        for p in self._predictions:
            if p.get("resolved"):
                continue
            if str(p.get("stimulus", ""))[:60].lower() not in str(stimulus).lower() \
                    and str(stimulus)[:60].lower() not in str(p.get("stimulus", "")).lower():
                continue
            pred = float(p.get("forecast", {}).get("impact", 0.0))
            err = abs(pred - float(actual_impact))
            akurasi = max(0.0, 1.0 - err / max(1e-6, float(tolerance)))
            p["resolved"] = True
            p["akurasi"] = round(akurasi, 3)
            nama = str(p.get("nama"))
            self._prediction_credit[nama] = (
                self._prediction_credit.get(nama, 0.5) * 0.7 + akurasi * 0.3)
            n = self.npcs.get(nama)
            if n is not None and akurasi > 0.7:
                n.levels["koherensi"] = min(1.0, n.levels["koherensi"] + 0.05)
                try:
                    self._reputasi.catat(nama, "keterampilan", akurasi,
                                         bobot=0.4, tick=n.tick_count)
                except Exception as _galat_diagnostik_173:
                    _diag.catat('naluri.KawananNPC.resolve_predictions', "galat pada jalur fallback", galat=_galat_diagnostik_173, jalur=173)
                    pass
            hasil.append({"nama": nama, "akurasi": round(akurasi, 3),
                          "prediksi": round(pred, 3),
                          "nyata": round(float(actual_impact), 3)})
        return hasil

    def prediction_leaderboard(self) -> List[Dict[str, Any]]:
        return sorted(({"nama": k, "kredit": round(v, 3)}
                       for k, v in self._prediction_credit.items()),
                      key=lambda x: x["kredit"], reverse=True)

    # ==================== LIGHT/HEAVY SPLIT (6A) ====================
    def tick_layered(self, events: Optional[Any] = None,
                     action_cost: Optional[Any] = None,
                     dekat: Optional[Any] = None) -> Dict[str, int]:
        """Pisahkan tick RINGAN (semua NPC) dari komputasi BERAT (NPC dekat).

        `dekat`: nama/iterable NPC yang dekat Player. Tick ringan dijalankan
        untuk semua; komputasi berat hanya untuk `dekat` (atau LOD \"penuh\").
        """
        ringan = 0
        berat = 0
        dekat_set = (set(dekat) if isinstance(dekat, (list, tuple, set))
                     else ({dekat} if isinstance(dekat, str) else None))
        for nama, n in self.npcs.items():
            ev = events.get(nama) if isinstance(events, dict) else events
            ac = (action_cost.get(nama, False)
                  if isinstance(action_cost, dict) else bool(action_cost))
            n.tick_light(events=ev, action_cost=ac)
            ringan += 1
            if dekat_set is None or nama in dekat_set or n.lod_mode == "penuh":
                n.heavy_computation()
                berat += 1
        return {"light": ringan, "heavy": berat, "total": len(self.npcs)}

    # ============ FITUR 1: BOBOT KEPERCAYAAN GOSIP (RUMOR TRUST WEIGHT) ============
    def _penilaian_sumber(self, sumber: Any) -> Dict[str, Any]:
        """Nilai kredibilitas seorang penyebar gosip (fitur 1).

        Menggabungkan tiga sinyal: (a) riwayat konfabulasi/penyangkalan &
        bias konfirmasi (\"suka berbohong\"), (b) kepercayaan komunitas rata-rata
        terhadapnya (mata rantai sosial), (c) kredibilitas yang sudah dipelajari
        (EMA, naik bila koreksinya terbukti). Bila di bawah ambang, rumor
        ditandai `alarm_palsu` dan didiskon.
        """
        sid = str(getattr(sumber, "name", sumber))
        alasan: List[str] = []
        kred = 0.6
        n = self.npcs.get(sid)
        confab = denials = 0
        bias_konf = 0.0
        if n is not None:
            ks = getattr(n, "kesadaran", None)
            if ks is not None:
                confab = len(getattr(ks, "confabulations", []) or [])
                denials = len(getattr(ks, "denials", []) or [])
                bias_konf = float((getattr(ks, "biases", {}) or {}).get(
                    "konfirmasi", 0.0))
        maks = int(self._reputasi._p("reputasi_liar_confab_max"))
        if maks > 0 and confab >= maks:
            kred -= 0.30
            alasan.append(f"riwayat konfabulasi ({confab})")
        if maks > 0 and denials >= maks:
            kred -= 0.15
            alasan.append(f"penyangkalan berulang ({denials})")
        if bias_konf > 0.4:
            kred -= 0.10
            alasan.append("bias konfirmasi tinggi")
        # (b) kepercayaan komunitas rata-rata terhadap sumber
        vals: List[float] = []
        for lain, on in self.npcs.items():
            if lain == sid:
                continue
            try:
                r = on.relasi(sid)
            except Exception as _galat_diagnostik_174:
                _diag.catat('naluri.KawananNPC._penilaian_sumber', "galat pada jalur fallback", galat=_galat_diagnostik_174, jalur=174)
                continue
            if r.get("dikenal"):
                vals.append(float(r.get("kepercayaan", 0.0)))
        if vals:
            komunitas = 0.5 + 0.5 * (sum(vals) / len(vals))
            kred = 0.55 * kred + 0.45 * komunitas
            if komunitas < 0.3:
                alasan.append("komunitas tak memercayainya")
        # (c) kredibilitas terpelajar (EMA)
        dipelajari = float(self._source_trust.get(sid, 0.6))
        kred = 0.7 * kred + 0.3 * dipelajari
        kred = jepit_01(kred)
        self._source_trust[sid] = round(
            0.8 * dipelajari + 0.2 * kred, 4)
        alarm = kred < float(self._reputasi._p("reputasi_kredibilitas_min"))
        return {"sumber": sid, "kredibilitas": round(kred, 3),
                "alarm_palsu": bool(alarm), "alasan": alasan}

    def trust_weight(self, sumber: Any) -> float:
        """Bobot kepercayaan sumber (fitur 1) — dipakai saat menyebar gosip."""
        return self._penilaian_sumber(sumber)["kredibilitas"]

    def _tandai_listener_alarm(self, sumber: Any, konten: str) -> int:
        """Persepsi semua NPC lain menandai rumor tak kredibel sebagai alarm palsu."""
        sid = str(getattr(sumber, "name", sumber))
        n_alarm = 0
        for nama, n in self.npcs.items():
            if nama == sid:
                continue
            ks = getattr(n, "kesadaran", None)
            if ks is None:
                continue
            try:
                ks.tandai_alarm_palsu(sid, konten)
                if n.nurani is not None:
                    n.nurani.persepsi_alarm_palsu = int(
                        getattr(n.nurani, "persepsi_alarm_palsu", 0)) + 1
                n_alarm += 1
            except Exception as _galat_diagnostik_175:
                _diag.catat('naluri.KawananNPC._tandai_listener_alarm', "galat pada jalur fallback", galat=_galat_diagnostik_175, jalur=175)
                continue
        return n_alarm

    # ============ FITUR 2: ECHO CHAMBER & FAKSI ============
    def _gossip_tentang(self, target: Any, window: int = 200,
                        negatif_saja: bool = True) -> List[Dict[str, Any]]:
        """Kumpulkan gosip tentang target dari seluruh NPC dalam jendela tick."""
        eid = str(getattr(target, "name", target))
        now = self._max_tick()
        out: List[Dict[str, Any]] = []
        for nama, n in self.npcs.items():
            ks = getattr(n, "kesadaran", None)
            if ks is None:
                continue
            for g in (getattr(ks, "gossip_log", []) or []):
                if str(g.get("tentang")) != eid:
                    continue
                if window is not None and now - int(g.get("tick", 0)) > int(window):
                    continue
                val = self._gossip_valence(g.get("isi", ""))
                if negatif_saja and val >= 0.0:
                    continue
                out.append({"sumber": str(nama), "isi": g.get("isi", ""),
                            "tick": int(g.get("tick", 0)), "valensi": val})
        return out

    def _faction_label(self, anggota: List[str], target: str) -> str:
        return f"sekutu anti-{target}"

    def echo_chamber(self, target: Any, window: int = 200,
                     min_anggota: int = 3) -> Dict[str, Any]:
        """Faksi organik: NPC yang terus berbagi gosip negatif saling menguatkan.

        In-group: afiliasi & kepercayaan antar-anggota naik. Out-group: target
        menjadi \"monster\" — rasa takut naik, keyakinan dikeraskan. Tidak ada
        faksi yang dikodekan manual; ia muncul dari pola gosip.
        """
        eid = str(getattr(target, "name", target))
        entri = self._gossip_tentang(target, window=window)
        pembicara = sorted({e["sumber"] for e in entri})
        # graf: dua NPC terhubung bila sama-sama membicarakan target negatif
        adj: Dict[str, set] = {s: set() for s in pembicara}
        for i, a in enumerate(pembicara):
            for b in pembicara[i + 1:]:
                adj[a].add(b)
                adj[b].add(a)
        # komponen terhubung
        komponen: List[List[str]] = []
        seen: set = set()
        for s in pembicara:
            if s in seen:
                continue
            tumpukan = [s]
            komp: List[str] = []
            while tumpukan:
                x = tumpukan.pop()
                if x in seen:
                    continue
                seen.add(x)
                komp.append(x)
                tumpukan.extend(adj.get(x, set()) - seen)
            if len(komp) >= int(min_anggota):
                komponen.append(sorted(komp))
        faksi: List[Dict[str, Any]] = []
        for komp in komponen:
            kohesi = 0.0
            n_pasang = 0
            for i, a in enumerate(komp):
                na = self.npcs.get(a)
                if na is None:
                    continue
                for b in komp[i + 1:]:
                    try:
                        ra = na.berinteraksi(
                            b, muatan=0.3, kepercayaan_delta=0.2,
                            alasan="faksi: saling menguatkan rasa takut")
                        kohesi += float(ra["relasi"].get("kepercayaan", 0.0))
                        n_pasang += 1
                    except Exception as _galat_diagnostik_176:
                        _diag.catat('naluri.KawananNPC.echo_chamber', "galat pada jalur fallback", galat=_galat_diagnostik_176, jalur=176)
                        continue
            # out-group: target jadi musuh bersama
            for a in komp:
                na = self.npcs.get(a)
                if na is None:
                    continue
                try:
                    na.berinteraksi(eid, muatan=-0.5, kepercayaan_delta=-0.4,
                                    alasan="faksi: musuh bersama")
                    if na._emosi_aktif():
                        na._emosi_naikkan("takut", 0.15, "faksi anti-target")
                        na._emosi_naikkan("marah", 0.10, "faksi anti-target")
                except Exception as _galat_diagnostik_177:
                    _diag.catat('naluri.KawananNPC.echo_chamber', "galat pada jalur fallback", galat=_galat_diagnostik_177, jalur=177)
                    pass
                ks = getattr(na, "kesadaran", None)
                if ks is not None:
                    try:
                        ks.hold_belief(f"{eid} berbahaya",
                                       "faksi menguatkan rasa takut")
                        if hasattr(ks, "harden_belief"):
                            ks.harden_belief(f"{eid} berbahaya")
                    except Exception as _galat_diagnostik_178:
                        _diag.catat('naluri.KawananNPC.echo_chamber', "galat pada jalur fallback", galat=_galat_diagnostik_178, jalur=178)
                        pass
            faksi.append({"anggota": komp, "ukuran": len(komp),
                          "kohesi": round(kohesi / max(1, n_pasang), 3),
                          "out_group": eid,
                          "label": self._faction_label(komp, eid)})
        now = self._max_tick()
        for f in faksi:
            self._faksi = [x for x in self._faksi
                           if x.get("anggota") != f["anggota"]]
            self._faksi.append({"anggota": f["anggota"], "target": eid,
                                "kohesi": f["kohesi"], "tick": now})
        return {"target": eid, "n_gosip_negatif": len(entri),
                "pembicara": pembicara, "faksi": faksi}

    def faksi(self) -> List[Dict[str, Any]]:
        """Daftar faksi yang terbentuk (untuk HUD/dialog)."""
        return [dict(x) for x in self._faksi]

    # ============ FITUR 3: KONFRONTASI BERBASIS BUKTI ============
    def konfrontasi(self, target: Any, saksi: Any, korban: Any, bukti: str,
                    kekuatan: float = 0.8, sebar_ke_faksi: bool = True
                    ) -> Dict[str, Any]:
        """Player membawa saksi ke korban; paksa bukti diterima secara real-time.

        Bukan [Persuade]/[Intimidate]: `terima_bukti()` + `koreksi_ingatan()`
        dijalankan pada korban dan seluruh faksi yang termakan gosip, rumor
        ditandai terkonfirmasi (menghentikan peluruhan kebenaran), dan reputasi
        target dipulihkan sebagian. Mengembalikan jejak perubahan.
        """
        eid = str(getattr(target, "name", target))
        sid = str(getattr(saksi, "name", saksi))
        kid = str(getattr(korban, "name", korban))
        hasil: Dict[str, Any] = {"target": eid, "saksi": sid, "korban": kid,
                                 "dipulihkan": []}

        def _proses(nama: str, kuat: float) -> None:
            n = self.npcs.get(nama)
            if n is None:
                return
            ks = getattr(n, "kesadaran", None)
            if ks is not None:
                try:
                    ks.terima_bukti(bukti, sumber=sid, kekuatan=kuat)
                    ks.koreksi_ingatan(str(bukti)[:40], str(bukti), sumber=sid)
                except Exception as _galat_diagnostik_179:
                    _diag.catat('naluri.KawananNPC.konfrontasi._proses', "galat pada jalur fallback", galat=_galat_diagnostik_179, jalur=179)
                    pass
            try:
                n.berinteraksi(eid, muatan=0.3, kepercayaan_delta=0.25,
                               alasan="bukti membersihkan nama")
            except Exception as _galat_diagnostik_180:
                _diag.catat('naluri.KawananNPC.konfrontasi._proses', "galat pada jalur fallback", galat=_galat_diagnostik_180, jalur=180)
                pass
            hasil["dipulihkan"].append(nama)

        _proses(kid, float(kekuatan))
        if self.npcs.get(kid) is not None:
            try:
                self.npcs[kid].berinteraksi(saksi, muatan=0.4,
                                            kepercayaan_delta=0.3,
                                            alasan="bukti disodorkan")
            except Exception as _galat_diagnostik_181:
                _diag.catat('naluri.KawananNPC.konfrontasi', "galat pada jalur fallback", galat=_galat_diagnostik_181, jalur=181)
                pass
        # saksi sebagai penyampai bukti: kredibilitasnya naik
        self._source_trust[sid] = min(
            1.0, float(self._source_trust.get(sid, 0.6)) + 0.15)
        # tandai semua rumor tentang target sebagai TERKONFIRMASI (hentikan decay)
        slot = self._reputasi._unit.get(eid, {})
        n_konfirm = 0
        for r in (slot.get("rumor") or []):
            if not r.get("dikonfirmasi"):
                r["dikonfirmasi"] = True
                n_konfirm += 1
        for r in self._reputasi._rumor_log:
            if str(r.get("tentang")) == eid:
                r["dikonfirmasi"] = True
        hasil["rumor_terkonfirmasi"] = n_konfirm
        # reputasi target dipulihkan (bukti kuat, sumber kredibel)
        try:
            self._reputasi.sebar(saksi, target, f"bukti: {str(bukti)[:60]}",
                                 muatan=0.8, tick=self._max_tick(),
                                 kredibilitas=0.9)
        except Exception as _galat_diagnostik_182:
            _diag.catat('naluri.KawananNPC.konfrontasi', "galat pada jalur fallback", galat=_galat_diagnostik_182, jalur=182)
            pass
        # sebar koreksi ke faksi/echo chamber terkait
        if sebar_ke_faksi:
            for f in list(self._faksi):
                if f.get("target") != eid:
                    continue
                for a in f["anggota"]:
                    if a != kid:
                        _proses(a, max(0.2, float(kekuatan) * 0.6))
        return hasil

    # ============ FITUR 4: DECAY OF TRUTH (PELURUHAN KEBENARAN) ============
    def _eskalasi_cerita(self, eid: str, tahap: int) -> str:
        tahapan = [
            f"{eid} melakukan kesalahan kecil",
            f"{eid} menyerang warga tanpa alasan",
            f"{eid} bukan manusia — dia iblis",
            f"{eid} adalah iblis yang memakan jiwa",
        ]
        return tahapan[max(0, min(len(tahapan) - 1, int(tahap)))]

    def decay_of_truth(self, window: int = 90,
                       maks_tahap: Optional[int] = None) -> List[Dict[str, Any]]:
        """Gosip lama yang tak dikonfirmasi makin ekstrem (fitur 4).

        Tiap kelipatan `window` tick tanpa konfirmasi, isi gosip dinaikkan satu
        tingkat dan pemegangnya mengalami `misremember()` + `confabulate()` —
        desas-desus berubah menjadi takhayul (\"iblis yang memakan jiwa\").
        """
        now = self._max_tick()
        hasil: List[Dict[str, Any]] = []
        for eid, slot in list(self._reputasi._unit.items()):
            aktif = [r for r in (slot.get("rumor") or [])
                     if not r.get("dikonfirmasi")]
            if not aktif:
                continue
            r0 = min(aktif, key=lambda x: int(x.get("tick", 0)))
            umur = now - int(r0.get("tick", 0))
            tahap = umur // max(1, int(window))
            if maks_tahap is not None:
                tahap = min(tahap, int(maks_tahap))
            if tahap <= 0:
                continue
            st = self._truth_decay.get(eid, {"tahap": 0})
            if int(st.get("tahap", 0)) >= tahap:
                continue
            cerita_baru = self._eskalasi_cerita(eid, tahap)
            lama = str(r0.get("konten", ""))
            # pemegang gosip salah-ingat & mengonfabulasi cerita baru
            pemegang: List[str] = []
            for nama, n in self.npcs.items():
                ks = getattr(n, "kesadaran", None)
                if ks is None:
                    continue
                ada = any(str(g.get("tentang")) == eid
                          for g in (getattr(ks, "gossip_log", []) or []))
                if not ada:
                    continue
                try:
                    ks.misremember(lama, cerita_baru)
                    ks.confabulate(cerita_baru)
                except Exception as _galat_diagnostik_183:
                    _diag.catat('naluri.KawananNPC.decay_of_truth', "galat pada jalur fallback", galat=_galat_diagnostik_183, jalur=183)
                    pass
                pemegang.append(nama)
            # sebar versi yang memburuk (kredibilitas kini dari kepercayaan
            # kolektif: cerita yang \"diketahui semua orang\" terasa benar)
            for nama in pemegang:
                try:
                    self._reputasi.sebar(
                        nama, eid, cerita_baru, muatan=-0.8, tick=now,
                        kredibilitas=max(0.4, self.trust_weight(nama)))
                except Exception as _galat_diagnostik_184:
                    _diag.catat('naluri.KawananNPC.decay_of_truth', "galat pada jalur fallback", galat=_galat_diagnostik_184, jalur=184)
                    continue
            self._truth_decay[eid] = {"tahap": tahap, "tick": now,
                                      "konten": cerita_baru}
            hasil.append({"target": eid, "umur": umur, "tahap": tahap,
                          "lama": lama[:60], "baru": cerita_baru,
                          "pemegang": pemegang})
        return hasil

    def konfirmasi_rumor(self, target: Any) -> int:
        """Tandai semua rumor tentang target terkonfirmasi (hentikan peluruhan)."""
        eid = str(getattr(target, "name", target))
        n = 0
        for r in self._reputasi._rumor_log:
            if str(r.get("tentang")) == eid and not r.get("dikonfirmasi"):
                r["dikonfirmasi"] = True
                n += 1
        for r in (self._reputasi._unit.get(eid, {}).get("rumor") or []):
            if not r.get("dikonfirmasi"):
                r["dikonfirmasi"] = True
        self._truth_decay.pop(eid, None)
        return n

    def peluruhan_kebenaran(self) -> Dict[str, Any]:
        """Ringkasan tahap peluruhan kebenaran per target (HUD)."""
        return {eid: dict(v) for eid, v in self._truth_decay.items()}

    # ============ FITUR 5: SOCIAL PROOF MULTIPLIER (HUD) ============
    def konsensus(self, tentang: Any) -> Dict[str, Any]:
        """Status konsensus sosial (fitur 5) — desas-desus menjadi \"fakta\"."""
        return self._reputasi.konsensus(tentang)

    # ---------- serialisasi (fix #1) ----------
    def to_dict(self, profil: str = "penuh") -> Dict[str, Any]:
        if profil not in ("penuh", "simpan", "minimal"):
            raise ValueError("profil tidak dikenal: {!r}".format(profil))
        # Selective persistence: `_grid`/`_wake` (derived) TIDAK disimpan.
        return {"format": "kawanan/5",
                "npcs": {nama: n.to_dict(profil=profil) for nama, n in self.npcs.items()},
                "positions": {nama: list(pos) for nama, pos in self.positions.items()},
                "relation_matrix": copy.deepcopy(self.relation_matrix),
                "reputasi": self._reputasi.to_dict(),
                "norms": copy.deepcopy(self.norms),
                "predictions": [dict(x) for x in self._predictions],
                "prediction_credit": {k: float(v) for k, v in
                                      self._prediction_credit.items()},
                "cell_size": float(self._cell_size),
                "source_trust": {k: float(v) for k, v in
                                 self._source_trust.items()},
                "faksi": copy.deepcopy(self._faksi),
                "truth_decay": copy.deepcopy(self._truth_decay)}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "KawananNPC":
        from pycos.inti.naluri import Naluri
        from pycos.dukungan.validasi_state import validasi_state
        data = validasi_state(data, "KawananNPC")
        obj = cls()
        for nama, nd in (data or {}).get("npcs", {}).items():
            n = Naluri.from_dict(nd)
            try:
                n.kawanan = obj
            except Exception as _galat_diagnostik_185:
                _diag.catat('naluri.KawananNPC.from_dict', "galat pada jalur fallback", galat=_galat_diagnostik_185, jalur=185)
                pass
            obj.npcs[str(nama)] = n
        for nama, pos in ((data or {}).get("positions") or {}).items():
            try:
                obj.set_position(str(nama), pos)
            except (KeyError, TypeError, ValueError):
                continue
        for observer, row in ((data or {}).get("relation_matrix") or {}).items():
            if not isinstance(row, Mapping):
                continue
            obj.relation_matrix[str(observer)] = {
                str(other): {"valensi": jepit_drive(float(rel.get("valensi", 0.0))),
                             "kepercayaan": jepit_drive(float(rel.get("kepercayaan", 0.0))),
                             "akrab": jepit_01(float(rel.get("akrab", 0.0))),
                             "n": max(0, int(rel.get("n", 0))),
                             "last_t": max(0, int(rel.get("last_t", 0)))}
                for other, rel in row.items() if isinstance(rel, Mapping)
            }
        rep_data = (data or {}).get("reputasi")
        if rep_data:
            try:
                obj._reputasi.from_dict(rep_data)
            except Exception as _galat_diagnostik_186:
                _diag.catat('naluri.KawananNPC.from_dict', "galat pada jalur fallback", galat=_galat_diagnostik_186, jalur=186)
                pass
        obj.norms = copy.deepcopy((data or {}).get("norms") or {})
        obj._predictions = [dict(x) for x in ((data or {}).get("predictions") or [])]
        obj._prediction_credit = {str(k): float(v) for k, v in
                                  ((data or {}).get("prediction_credit") or {}).items()}
        try:
            obj._cell_size = float((data or {}).get("cell_size", 10.0))
        except (TypeError, ValueError):
            obj._cell_size = 10.0
        obj._source_trust = {str(k): float(v) for k, v in
                             ((data or {}).get("source_trust") or {}).items()}
        obj._faksi = copy.deepcopy((data or {}).get("faksi") or [])
        obj._truth_decay = copy.deepcopy((data or {}).get("truth_decay") or {})
        obj._grid_dirty = True
        return obj

    def to_json(self, profil: str = "penuh", **json_kwargs: Any) -> str:
        json_kwargs.setdefault("ensure_ascii", False)
        return json.dumps(self.to_dict(profil=profil), **json_kwargs)

    @classmethod
    def from_json(cls, s: str) -> "KawananNPC":
        return cls.from_dict(json.loads(s))

    def save(self, path: str, *, profil: str = "penuh") -> str:
        from pycos.dukungan.persistensi import simpan_json
        return simpan_json(path, self.to_dict(profil=profil))

    @classmethod
    def load(cls, path: str) -> "KawananNPC":
        from pycos.dukungan.persistensi import muat_json
        return cls.from_dict(muat_json(path))


KawananNPC.__module__ = "pycos.inti.naluri"
