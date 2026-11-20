"""Ritual: implementasi terpisah; diekspor ulang oleh inti.naluri."""
from __future__ import annotations

import copy
import random
from typing import Any, Dict, List, Mapping, Optional
from pycos.dukungan import diagnostik as _diag

RITUAL_DEFAULTS: Dict[str, Any] = {
    "enable_ritual": False,
    "ritual_probabilitas": 0.05,   # peluang per tick saat idle
    "ritual_cooldown": 10,         # tick minimum antar ritual
    "ritual_log_max": 32,
}

# Satu sumber kebenaran: parameter ritual dilebur ke dict params Naluri.


class Ritual:
    """Kumpulan kebiasaan tak-berguna yang membuat NPC terasa hidup.

    Arketipe dideteksi dari `personality_name` (bila ada) atau bobot drive
    dominan. Tiap arketipe punya beberapa ritual dengan kondisi pemicu ringan;
    `maybe_trigger()` memilih satu secara probabilistik hanya saat idle.
    """

    _RITUALS: Dict[str, List[Dict[str, Any]]] = {
        "cendekia": [
            {"nama": "merapikan_benda",
             "kondisi": "koherensi_sedikit",
             "deskripsi": "merapikan benda-benda di sekitarnya, menyusunnya sejajar",
             "efek": {"arousal": -0.05, "koherensi_rasa": 0.05}},
            {"nama": "membaca_ulang",
             "kondisi": "selalu",
             "deskripsi": "membuka catatan lama dan membacanya ulang, mengangguk sendiri",
             "efek": {"arousal": -0.03}},
        ],
        "sosiawan": [
            {"nama": "bersiul",
             "kondisi": "sepi",
             "deskripsi": "bersiul pelan, lalu bergumam pada dirinya sendiri",
             "efek": {"afiliasi_rasa": 0.06}},
            {"nama": "menyapa_bayangan",
             "kondisi": "sepi",
             "deskripsi": "menyapa seseorang yang kebetulan lewat, lalu tersenyum kecil",
             "efek": {"afiliasi_rasa": 0.05}},
        ],
        "pengrajin": [
            {"nama": "mengasah_alat",
             "kondisi": "aman",
             "deskripsi": "mengasah alatnya dengan gerakan yang sudah hafal di luar kepala",
             "efek": {"arousal": -0.04, "penguasaan_rasa": 0.05}},
            {"nama": "memutar_benda",
             "kondisi": "selalu",
             "deskripsi": "memutar sebuah benda kecil di sela jarinya, menimbang-nimbang",
             "efek": {"arousal": -0.03}},
        ],
        "penjaga": [
            {"nama": "memeriksa_tepi",
             "kondisi": "aman",
             "deskripsi": "berjalan menyusuri tepi ruangan, memastikan tak ada yang berubah",
             "efek": {"keamanan_rasa": 0.05}},
            {"nama": "menghitung_pintu",
             "kondisi": "selalu",
             "deskripsi": "menghitung pintu dan jendela dengan pandangan, tanpa sadar",
             "efek": {"arousal": -0.03}},
        ],
        "penjelajah": [
            {"nama": "menggambar_peta",
             "kondisi": "penasaran",
             "deskripsi": "menggambar arah di tanah dengan ujung sepatu, menandai titik",
             "efek": {"keingintahuan_rasa": 0.05}},
            {"nama": "menghafal_arah",
             "kondisi": "selalu",
             "deskripsi": "menutup mata sejenak, menghafal arah mata angin",
             "efek": {"arousal": -0.03}},
        ],
        "umum": [
            {"nama": "menepuk_pakaian",
             "kondisi": "selalu",
             "deskripsi": "menepuk pakaian yang sebenarnya tidak berdebu",
             "efek": {"arousal": -0.02}},
            {"nama": "memandang_jauh",
             "kondisi": "selalu",
             "deskripsi": "memandang jauh ke satu arah, seolah ada sesuatu di sana",
             "efek": {"arousal": -0.02}},
        ],
    }

    def __init__(self, naluri: Any, params: Optional[Dict[str, Any]] = None) -> None:
        self.naluri = naluri
        self.params: Dict[str, Any] = (params if params is not None
                                       else copy.deepcopy(RITUAL_DEFAULTS))
        self._rng = random.Random(self._seed_for(naluri) ^ 0x5EED)
        self._last_tick: int = -10_000
        self._log: List[Dict[str, Any]] = []
        self._archetype: str = self._detect_archetype()
        self._jumlah: int = 0

    @staticmethod
    def _seed_for(naluri: Any) -> int:
        nama = str(getattr(naluri, "name", "") or "")
        seed = 104729
        for i, ch in enumerate(nama):
            seed = (seed * 137 + ord(ch) * (i + 3)) & 0x7FFFFFFF
        return seed

    # ------------------------------------------------------------------
    def enabled(self) -> bool:
        return bool(self.params.get("enable_ritual", False))

    def _p(self, key: str) -> float:
        v = self.params.get(key, RITUAL_DEFAULTS.get(key, 0.0))
        if isinstance(v, Mapping):
            v = v.get("*", RITUAL_DEFAULTS.get(key, 0.0))
        try:
            return float(v)
        except (TypeError, ValueError):
            return float(RITUAL_DEFAULTS.get(key, 0.0))

    def _tick(self) -> int:
        return int(getattr(self.naluri, "tick_count", 0))

    def _deficit(self, drive: str) -> float:
        try:
            return float(self.naluri.deficit(drive))
        except Exception as _galat_diagnostik_113:
            _diag.catat('naluri.Ritual._deficit', "galat pada jalur fallback", galat=_galat_diagnostik_113, jalur=113)
            return 0.0

    def _detect_archetype(self) -> str:
        nama = str(getattr(self.naluri, "personality_name", "") or "").lower()
        peta = (
            (("cendekia", "sarjana", "ilmuwan", "bijak", "scholar"), "cendekia"),
            (("sosiawan", "sosial", "ramah", "periang", "social"), "sosiawan"),
            (("pengrajin", "tukang", "seniman", "artisan"), "pengrajin"),
            (("penjaga", "prajurit", "guard", "satpam", "knight"), "penjaga"),
            (("penjelajah", "petualang", "explorer", "pengembara"), "penjelajah"),
        )
        for kunci, ark in peta:
            if any(k in nama for k in kunci):
                return ark
        try:
            w = getattr(self.naluri, "weights", {}) or {}
            if w:
                dom = max(w, key=lambda d: w[d])
                return {"keingintahuan": "cendekia", "afiliasi": "sosiawan",
                        "penguasaan": "pengrajin", "keamanan": "penjaga"}.get(dom, "umum")
        except Exception as _galat_diagnostik_114:
            _diag.catat('naluri.Ritual._detect_archetype', "galat pada jalur fallback", galat=_galat_diagnostik_114, jalur=114)
            pass
        return "umum"

    def _kondisi_ok(self, kondisi: str) -> bool:
        koherensi = self._deficit("koherensi")
        afiliasi = self._deficit("afiliasi")
        keamanan = self._deficit("keamanan")
        if kondisi == "koherensi_sedikit":
            return 0.0 < koherensi < 0.4
        if kondisi == "sepi":
            return afiliasi > 0.05
        if kondisi == "aman":
            return keamanan < 0.25
        if kondisi == "penasaran":
            return self._deficit("keingintahuan") > 0.1
        return True  # "selalu"

    # ------------------------------------------------------------------
    def tick(self, steps: int = 1) -> None:
        """Tidak memicu sendiri; hanya menjaga denyut (kompatibel)."""
        return

    def refresh_archetype(self) -> str:
        """Hitung ulang arketipe (personality/preset bisa berubah setelah init)."""
        self._archetype = self._detect_archetype()
        return self._archetype

    def maybe_trigger(self, konteks: str = "idle",
                      paksa: bool = False) -> Optional[Dict[str, Any]]:
        """Peluang rendah memicu satu ritual bila kondisi & cooldown terpenuhi."""
        if not self.enabled():
            return None
        self.refresh_archetype()
        if konteks != "idle" and not paksa:
            return None
        now = self._tick()
        if not paksa and now - self._last_tick < int(self._p("ritual_cooldown")):
            return None
        if not paksa and self._rng.random() > self._p("ritual_probabilitas"):
            return None
        kandidat = [r for r in self._RITUALS.get(self._archetype, [])
                    if self._kondisi_ok(r.get("kondisi", "selalu"))]
        if not kandidat:
            kandidat = [r for r in self._RITUALS["umum"]
                        if self._kondisi_ok(r.get("kondisi", "selalu"))]
        if not kandidat:
            return None
        return self.perform(self._rng.choice(kandidat), konteks=konteks)

    def perform(self, ritual: Any = None,
                konteks: str = "idle") -> Dict[str, Any]:
        """Jalankan ritual; efek hanya afektif/presentasi, bukan drive."""
        if not self.enabled():
            return {}
        self.refresh_archetype()
        if ritual is None:
            ritual = self._rng.choice(self._RITUALS.get(self._archetype,
                                                        self._RITUALS["umum"]))
        if isinstance(ritual, str):
            ritual = next((r for r in self._RITUALS.get(self._archetype, [])
                           if r.get("nama") == ritual), {"nama": ritual,
                                                         "deskripsi": ritual,
                                                         "efek": {}})
        now = self._tick()
        efek = self._terapkan_efek(ritual.get("efek", {}))
        entri = {"tick": now, "arketipe": self._archetype,
                 "ritual": ritual.get("nama", ""),
                 "deskripsi": str(ritual.get("deskripsi", ""))[:140],
                 "konteks": konteks, "efek": efek}
        self._log.append(entri)
        cap = int(self._p("ritual_log_max"))
        if cap > 0 and len(self._log) > cap:
            self._log = self._log[-cap:]
        self._last_tick = now
        self._jumlah += 1
        return entri

    def _terapkan_efek(self, efek: Mapping[str, Any]) -> Dict[str, Any]:
        """Efek psikologis ringan: menenangkan/menyamankan — TANPA menambah drive."""
        hasil: Dict[str, Any] = {}
        if not efek:
            return hasil
        # turunkan arousal (menenangkan diri) lewat emosi, bukan drive
        if "arousal" in efek:
            try:
                for e in ("takut", "marah"):
                    if e in getattr(self.naluri, "emosi", {}):
                        self.naluri.emosi[e] = max(
                            0.0, self.naluri.emosi[e] + float(efek["arousal"]))
                hasil["arousal"] = float(efek["arousal"])
            except Exception as _galat_diagnostik_115:
                _diag.catat('naluri.Ritual._terapkan_efek', "galat pada jalur fallback", galat=_galat_diagnostik_115, jalur=115)
                pass
        # rasa-rasa (affect, bukan level drive)
        for k in ("koherensi_rasa", "afiliasi_rasa", "penguasaan_rasa",
                  "keamanan_rasa", "keingintahuan_rasa"):
            if k in efek:
                hasil[k] = float(efek[k])
        return hasil

    def state(self) -> Dict[str, Any]:
        self.refresh_archetype()
        return {"aktif": self.enabled(), "arketipe": self._archetype,
                "jumlah": self._jumlah,
                "terakhir": self._log[-1] if self._log else None,
                "riwayat": self._log[-5:]}

    def to_dict(self) -> Dict[str, Any]:
        st = self._rng.getstate()
        return {"format": "ritual/1",
                "last_tick": self._last_tick,
                "log": [dict(x) for x in self._log],
                "archetype": self._archetype,
                "jumlah": self._jumlah,
                "rng_state": [int(st[0]), [int(x) for x in st[1]], st[2]]}

    def from_dict(self, data: Mapping[str, Any]) -> "Ritual":
        from pycos.dukungan.validasi_state import validasi_state
        data = validasi_state(data, "Ritual")
        if not isinstance(data, Mapping):
            return self
        self._last_tick = int(data.get("last_tick", -10_000))
        self._log = [dict(x) for x in (data.get("log") or [])]
        self._archetype = str(data.get("archetype", self._archetype))
        self._jumlah = int(data.get("jumlah", 0))
        rs = data.get("rng_state")
        if rs and len(rs) == 3 and rs[1]:
            try:
                self._rng.setstate((int(rs[0]), tuple(int(x) for x in rs[1]), rs[2]))
            except (ValueError, TypeError):
                pass
        return self


# Jalur kelas historis untuk kompatibilitas pickle.
Ritual.__module__ = "pycos.inti.naluri"
