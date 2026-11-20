# -*- coding: utf-8 -*-
"""pycos/mandiri/kognisi_lanjut.py — lima mekanisme kognitif Pycos.

Murni stdlib. Tidak mengimpor lapisan inti (dipasang dari luar oleh
`pycos.inti`, `pycos.refleksi`, atau `pycos.memori`), aman dari siklus.

Isi:
  1. EversiTD          — reward intrinsik + TD(0) + eversi parameter permanen
  2. boltzmann_pilih   — pemilihan tindakan Softmax/Boltzmann + suhu mental
  3. MesinKepercayaan  — pembaruan Bayesian (log-odds) + ambang curiga dinamis
  4. GrafAsosiasi      — graf berbobot + Hebbian ("fire together, wire together")
  5. ProsesOU          — latent drift Ornstein-Uhlenbeck (derau terikat)
"""
from __future__ import annotations

import math
import random
from typing import Any, Dict, Iterable, List, Optional, Tuple


def jepit_drive(x: Any, lo: float = -1.0, hi: float = 1.0) -> float:
    """Jepit ke [lo, hi]; NaN/tak-numerik menjadi 0 (salinan aturan
    `pycos.dukungan.numerik.jepit`, dipertahankan lokal agar modul ini tetap
    dapat disalin sendirian)."""
    try:
        v = 0.0 if isinstance(x, bool) else float(x)
    except (TypeError, ValueError, OverflowError):
        v = 0.0
    if v != v:
        v = 0.0
    return lo if v < lo else hi if v > hi else v

# ===========================================================================
# 1. EVERSI PARAMETER VIA TEMPORAL DIFFERENCE
# ===========================================================================
class EversiTD:
    """Reward intrinsik R = -ΔDisonansi - ΔKecemasan; TD(0) atas (situasi,aksi).

    Nilai Q yang terbentuk dipakai untuk menggeser parameter NPC secara
    PERMANEN (eversi): NPC dengan pengalaman berbeda berakhir dengan parameter
    berbeda meski kodenya sama.
    """

    def __init__(self, alpha: float = 0.15, gamma: float = 0.9,
                 laju_eversi: float = 0.35, batas_eversi: float = 0.35,
                 disonansi_bobot: float = 1.0, cemas_bobot: float = 1.0,
                 acuan: Optional[Dict[str, float]] = None) -> None:
        self.alpha = float(alpha)
        self.gamma = float(gamma)
        self.laju_eversi = float(laju_eversi)
        self.batas_eversi = float(batas_eversi)
        self.disonansi_bobot = float(disonansi_bobot)
        self.cemas_bobot = float(cemas_bobot)
        self.q: Dict[str, Dict[str, float]] = {}
        self.kunjungan: Dict[str, int] = {}
        self.prev: Optional[Tuple[str, str]] = None
        self.disonansi_lalu: Optional[float] = None
        self.cemas_lalu: Optional[float] = None
        self.delta_terakhir: float = 0.0
        self.reward_terakhir: float = 0.0
        self.jejak: List[Dict[str, Any]] = []
        self.acuan: Dict[str, float] = dict(acuan or {
            "redaman_emosi": 0.985, "viskositas_emosi": 0.10,
            "bobot_impresi": 1.0, "redaman_drive": 0.99})
        # arah eversi: +1 = naik bila homeostasis membaik; -1 = turun
        # (laju redaman TURUN artinya emosi bertahan lebih lama)
        self.arah: Dict[str, float] = {"redaman_emosi": -1.0,
                                       "redaman_drive": -1.0,
                                       "viskositas_emosi": 1.0,
                                       "bobot_impresi": 1.0}
        self.eversi: Dict[str, float] = dict(self.acuan)

    # -- reward intrinsik -------------------------------------------------
    def reward_intrinsik(self, disonansi: float, kecemasan: float) -> float:
        """R = -ΔDisonansi - ΔKecemasan (homeostasis membaik ⇒ R > 0)."""
        d, k = float(disonansi), float(kecemasan)
        if self.disonansi_lalu is None:
            r = 0.0
        else:
            r = -(self.disonansi_bobot * (d - self.disonansi_lalu)
                  + self.cemas_bobot * (k - self.cemas_lalu))
        self.disonansi_lalu, self.cemas_lalu = d, k
        self.reward_terakhir = r
        return r

    # -- TD(0) ------------------------------------------------------------
    def _nilai(self, s: str, a: str) -> float:
        return self.q.get(s, {}).get(a, 0.0)

    def _maks(self, s: str) -> float:
        d = self.q.get(s)
        return max(d.values()) if d else 0.0

    def update(self, situasi: str, aksi: str, reward: float,
               situasi_baru: str) -> float:
        lama = self._nilai(situasi, aksi)
        target = float(reward) + self.gamma * self._maks(situasi_baru)
        delta = target - lama
        self.q.setdefault(situasi, {})[aksi] = lama + self.alpha * delta
        self.kunjungan[situasi] = self.kunjungan.get(situasi, 0) + 1
        self.delta_terakhir = delta
        self.prev = (situasi_baru, aksi)
        return delta

    def nilai(self, situasi: str, aksi: str) -> float:
        return self._nilai(situasi, aksi)

    def nilai_situasi(self, situasi: str) -> float:
        return self._maks(situasi)

    # -- eversi parameter -------------------------------------------------
    def eversi_param(self) -> Dict[str, float]:
        """Petakan Q agregat → parameter permanen (bounded, halus)."""
        if not self.q:
            return dict(self.eversi)
        rata = sum(self._maks(s) for s in self.q) / max(1, len(self.q))
        sinyal = math.tanh(rata * 1.5)
        for nama, dasar in self.acuan.items():
            arah = float(self.arah.get(nama, 1.0))
            skala = 1.0 + arah * self.laju_eversi * sinyal
            lo = dasar * (1.0 - self.batas_eversi)
            hi = dasar * (1.0 + self.batas_eversi)
            nilai = dasar * skala
            if not math.isfinite(nilai):  # NaN/inf dari arah tak valid: kembali ke acuan
                nilai = dasar
            self.eversi[nama] = max(lo, min(hi, nilai))
        return dict(self.eversi)

    def ambil(self, nama: str) -> float:
        return float(self.eversi.get(nama, self.acuan.get(nama, 1.0)))

    # -- serialisasi ------------------------------------------------------
    def to_dict(self) -> Dict[str, Any]:
        return {"alpha": self.alpha, "gamma": self.gamma,
                "laju_eversi": self.laju_eversi, "batas_eversi": self.batas_eversi,
                "disonansi_bobot": self.disonansi_bobot, "cemas_bobot": self.cemas_bobot,
                "delta_terakhir": self.delta_terakhir,
                "reward_terakhir": self.reward_terakhir, "prev": self.prev,
                "q": {s: dict(a) for s, a in self.q.items()},
                "kunjungan": dict(self.kunjungan),
                "disonansi_lalu": self.disonansi_lalu,
                "cemas_lalu": self.cemas_lalu, "acuan": dict(self.acuan),
                "arah": dict(self.arah), "eversi": dict(self.eversi)}

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "EversiTD":
        o = cls(alpha=d.get("alpha", 0.15), gamma=d.get("gamma", 0.9),
                laju_eversi=d.get("laju_eversi", 0.35),
                batas_eversi=d.get("batas_eversi", 0.35),
                disonansi_bobot=d.get("disonansi_bobot", 1.0),
                cemas_bobot=d.get("cemas_bobot", 1.0), acuan=d.get("acuan"))
        o.delta_terakhir = float(d.get("delta_terakhir", 0.0))
        o.reward_terakhir = float(d.get("reward_terakhir", 0.0))
        o.prev = tuple(d["prev"]) if d.get("prev") is not None else None
        o.q = {s: dict(a) for s, a in (d.get("q") or {}).items()}
        o.kunjungan = dict(d.get("kunjungan") or {})
        o.disonansi_lalu = d.get("disonansi_lalu")
        o.cemas_lalu = d.get("cemas_lalu")
        if d.get("arah"):
            o.arah = dict(d["arah"])
        if d.get("eversi"):
            o.eversi = dict(d["eversi"])
        return o


# ===========================================================================
# 2. TRANSISI PROBABILISTIK: SOFTMAX / BOLTZMANN
# ===========================================================================
def suhu_mental(arousal: float, kelelahan: float = 0.0, dasar: float = 0.15,
                gain_arousal: float = 1.4, gain_lelahan: float = 1.1,
                minimum: float = 0.05, maksimum: float = 3.0) -> float:
    """τ: tenang ⇒ rendah (rasional); panik/lelah ⇒ tinggi (stokastik)."""
    t = (float(dasar) + gain_arousal * max(0.0, float(arousal))
         + gain_lelahan * max(0.0, float(kelelahan)))
    return max(float(minimum), min(float(maksimum), t))


def boltzmann_pilih(skor: Dict[str, float], tau: float,
                    rng: Optional[random.Random] = None,
                    ) -> Tuple[str, Dict[str, float]]:
    """Ambil sampel tindakan dari distribusi Softmax(skor/τ).

    τ→0 ⇒ argmax (deterministik); τ besar ⇒ makin acak. Kembalikan
    (aksi_terpilih, distribusi).
    """
    if not skor:
        return "", {}
    tau = max(1e-6, float(tau))
    mx = max(skor.values())
    bobot = {a: math.exp((float(v) - mx) / tau) for a, v in skor.items()}
    total = sum(bobot.values()) or 1.0
    dist = {a: b / total for a, b in bobot.items()}
    r = (rng or random).random()
    akum = 0.0
    for a, p in dist.items():
        akum += p
        if r <= akum:
            return a, dist
    return max(dist, key=lambda k: dist[k]), dist


# ===========================================================================
# 3. BAYESIAN UPDATING (MESIN KEPERCAYAAN)
# ===========================================================================
def _sigmoid(x: float) -> float:
    if x >= 0:
        return 1.0 / (1.0 + math.exp(-x))
    e = math.exp(x)
    return e / (1.0 + e)


def _logit(p: float) -> float:
    p = max(1e-6, min(1.0 - 1e-6, float(p)))
    return math.log(p / (1.0 - p))


class MesinKepercayaan:
    """Kepercayaan sebagai log-odds; bukti menggeser posterior P(H|E).

    P(H)=0.8 lalu bukti "berbohong" (likelihood-ratio < 1) menurunkan
    kepercayaan bertahap. Di bawah ambang dinamis → curiga.
    """

    def __init__(self, prior_bawaan: float = 0.5,
                 ambang_bawaan: float = 0.35) -> None:
        self.prior_bawaan = float(prior_bawaan)
        self.ambang_bawaan = float(ambang_bawaan)
        self.log_odds: Dict[str, float] = {}
        self.bukti: Dict[str, List[Dict[str, Any]]] = {}
        self._awal: Dict[str, float] = {}

    def tetapkan(self, hipotesis: str, p: float) -> float:
        h = str(hipotesis)
        self.log_odds[h] = _logit(p)
        self._awal[h] = float(p)
        self.bukti.setdefault(h, [])
        return self.kepercayaan(h)

    def kepercayaan(self, hipotesis: str) -> float:
        h = str(hipotesis)
        if h not in self.log_odds:
            return self.prior_bawaan
        return _sigmoid(self.log_odds[h])

    def perbarui(self, hipotesis: str, likelihood_ratio: float,
                 bobot: float = 1.0, label: str = "") -> float:
        """P(H|E) ∝ P(E|H)/P(E|¬H) · P(H). LR>1 memperkuat, LR<1 melemahkan."""
        h = str(hipotesis)
        if h not in self.log_odds:
            self.tetapkan(h, self.prior_bawaan)
        lr = max(1e-4, float(likelihood_ratio))
        self.log_odds[h] += float(bobot) * math.log(lr)
        self.bukti.setdefault(h, []).append(
            {"label": label or "bukti", "lr": round(lr, 3),
             "bobot": round(float(bobot), 3),
             "posterior": round(self.kepercayaan(h), 4)})
        if len(self.bukti[h]) > 60:
            del self.bukti[h][:-60]
        return self.kepercayaan(h)

    def curiga(self, hipotesis: str,
               ambang: Optional[float] = None) -> bool:
        a = self.ambang_bawaan if ambang is None else float(ambang)
        return self.kepercayaan(hipotesis) < a

    def entropi(self, hipotesis: str) -> float:
        p = self.kepercayaan(hipotesis)
        if p <= 0.0 or p >= 1.0:
            return 0.0
        return -(p * math.log2(p) + (1 - p) * math.log2(1 - p))

    def ringkas(self) -> Dict[str, float]:
        return {h: round(self.kepercayaan(h), 4) for h in self.log_odds}

    def to_dict(self) -> Dict[str, Any]:
        return {"prior_bawaan": self.prior_bawaan,
                "ambang_bawaan": self.ambang_bawaan,
                "log_odds": dict(self.log_odds),
                "awal": dict(self._awal),
                "bukti": {h: list(v) for h, v in self.bukti.items()}}

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "MesinKepercayaan":
        o = cls(prior_bawaan=d.get("prior_bawaan", 0.5),
                ambang_bawaan=d.get("ambang_bawaan", 0.35))
        o.log_odds = dict(d.get("log_odds") or {})
        o._awal = dict(d.get("awal") or {})
        o.bukti = {h: list(v) for h, v in (d.get("bukti") or {}).items()}
        return o


# ===========================================================================
# 4. GRAF ASOSIASI & HEBBIAN
# ===========================================================================
EMOSI_NODE = {"takut", "senang", "sedih", "marah", "malu", "cinta", "benci",
              "terkejut", "jijik", "harap", "kesepian", "tenang", "cemas",
              "rindu", "bangga", "bersalah"}


class GrafAsosiasi:
    """Graf berbobot konsep↔konsep. Fire together, wire together.

    Tepi menguat saat dua konsep aktif bersamaan (terutama saat takut tinggi),
    lalu meluruh. Di atas ambang → asosiasi otomatis (embrio fobia/trauma).
    """

    def __init__(self, laju_hebb: float = 0.18, laju_luruh: float = 0.006,
                 ambang_fobia: float = 0.55, bobot_maks: float = 1.0,
                 maks_node: int = 400, maks_tepi: int = 1200) -> None:
        self.laju_hebb = float(laju_hebb)
        self.laju_luruh = float(laju_luruh)
        self.ambang_fobia = float(ambang_fobia)
        self.bobot_maks = float(bobot_maks)
        self.maks_node = int(maks_node)
        self.maks_tepi = int(maks_tepi)
        self.edge: Dict[Tuple[str, str], float] = {}
        self.aktivasi: Dict[str, float] = {}
        self.asosiasi_terbentuk: List[Dict[str, Any]] = []

    @staticmethod
    def _kunci(a: str, b: str) -> Tuple[str, str]:
        a, b = str(a).strip().lower(), str(b).strip().lower()
        return (a, b) if a <= b else (b, a)

    def koaktifkan(self, a: str, b: str, gain: float = 1.0,
                   takut: float = 0.0) -> float:
        """Perkuat tepi a–b (Hebbian). `takut` menaikkan laju penguatan."""
        a, b = str(a).strip().lower(), str(b).strip().lower()
        if not a or not b or a == b:
            return 0.0
        k = self._kunci(a, b)
        lama = self.edge.get(k, 0.0)
        naik = self.laju_hebb * gain * (1.0 + 1.5 * max(0.0, float(takut)))
        baru = min(self.bobot_maks, lama + naik * (1.0 - lama))
        self.edge[k] = baru
        if lama < self.ambang_fobia <= baru:
            self.asosiasi_terbentuk.append(
                {"a": k[0], "b": k[1], "bobot": round(baru, 3),
                 "takut": round(float(takut), 3)})
            if len(self.asosiasi_terbentuk) > 40:
                del self.asosiasi_terbentuk[:-40]
        self._jaga_ukuran()
        return baru

    def aktifkan(self, konsep: str, energi: float = 1.0, sebar: int = 1,
                 minimum: float = 0.05) -> Dict[str, float]:
        """Rambatkan hingga ``sebar`` hop, sekali per node per panggilan."""
        c = str(konsep).strip().lower()
        if not c:
            return {}
        self.aktivasi[c] = min(1.0, self.aktivasi.get(c, 0.0) + float(energi))
        frontier = {c: self.aktivasi[c]}
        dikunjungi = {c}
        for _ in range(max(0, int(sebar))):
            baru: Dict[str, float] = {}
            for (a, b), w in self.edge.items():
                for sumber, target in ((a, b), (b, a)):
                    if sumber in frontier and target not in dikunjungi:
                        nilai = w * frontier[sumber]
                        baru[target] = max(baru.get(target, 0.0), nilai)
            frontier = {}
            for n, v in baru.items():
                if v > minimum:
                    tambahan = v * 0.8
                    self.aktivasi[n] = min(1.0, self.aktivasi.get(n, 0.0) + tambahan)
                    frontier[n] = tambahan
            # Per panggilan, node dikunjungi sekali. Siklus tidak memompa
            # energi kembali ke sumber, dan sebar adalah batas jarak hop.
            dikunjungi.update(frontier)
            if not frontier:
                break
        return dict(self.aktivasi)

    def bobot(self, a: str, b: str) -> float:
        return self.edge.get(self._kunci(a, b), 0.0)

    def asosiasi(self, konsep: str, top: int = 5,
                 minimum: float = 0.02) -> List[Tuple[str, float]]:
        c = str(konsep).strip().lower()
        out: List[Tuple[str, float]] = []
        for (a, b), w in self.edge.items():
            if w < minimum:
                continue
            if a == c:
                out.append((b, w))
            elif b == c:
                out.append((a, w))
        out.sort(key=lambda kv: kv[1], reverse=True)
        return out[:top]

    def emosi_terasosiasi(self, konsep: str,
                          minimum: float = 0.08) -> Dict[str, float]:
        return {n: w for n, w in self.asosiasi(konsep, top=12, minimum=minimum)
                if n in EMOSI_NODE}

    def fobia(self, minimum: Optional[float] = None) -> List[Dict[str, Any]]:
        amb = self.ambang_fobia if minimum is None else float(minimum)
        out = []
        for (a, b), w in self.edge.items():
            if w < amb:
                continue
            if a in EMOSI_NODE or b in EMOSI_NODE:
                out.append({"a": a, "b": b, "bobot": round(w, 3)})
        out.sort(key=lambda d: d["bobot"], reverse=True)
        return out

    def luruh(self, dt: float = 1.0) -> None:
        for k in list(self.edge):
            self.edge[k] *= max(0.0, 1.0 - self.laju_luruh * float(dt))
            if self.edge[k] < 1e-4:
                del self.edge[k]
        for n in list(self.aktivasi):
            self.aktivasi[n] *= max(0.0, 1.0 - 0.25 * float(dt))
            if self.aktivasi[n] < 1e-4:
                del self.aktivasi[n]

    def _jaga_ukuran(self) -> None:
        if len(self.edge) > self.maks_tepi:
            for k, _ in sorted(self.edge.items(), key=lambda kv: kv[1])[
                    :len(self.edge) - self.maks_tepi]:
                del self.edge[k]

    def to_dict(self) -> Dict[str, Any]:
        # Tuple node tidak dapat menjadi kunci JSON. Rekaman terstruktur tidak
        # ambigu ketika nama konsep sendiri memuat pemisah format lama "|".
        return {"format": "graf_asosiasi/2",
                "config": {"laju_hebb": self.laju_hebb,
                           "laju_luruh": self.laju_luruh,
                           "ambang_fobia": self.ambang_fobia,
                           "bobot_maks": self.bobot_maks,
                           "maks_node": self.maks_node, "maks_tepi": self.maks_tepi},
                "edges": [[a, b, v] for (a, b), v in self.edge.items()],
                "aktivasi": dict(self.aktivasi),
                "asosiasi_terbentuk": [dict(x) for x in self.asosiasi_terbentuk]}

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "GrafAsosiasi":
        if "format" in d and d["format"] != "graf_asosiasi/2":
            raise ValueError("GrafAsosiasi.format tidak didukung: {!r}".format(d["format"]))
        config = d.get("config") or {}
        o = cls(**{k: config[k] for k in (
            "laju_hebb", "laju_luruh", "ambang_fobia", "bobot_maks",
            "maks_node", "maks_tepi") if k in config})
        if "edges" in d:
            for a, b, v in d["edges"]:
                if a and b:
                    o.edge[(str(a), str(b))] = float(v)
        else:
            # Save lama: pertahankan pembacaan pemisah lama; informasi yang
            # sudah hilang akibat collision pada save lama tidak dapat ditebak.
            for k, v in (d.get("edge") or {}).items():
                a, _, b = k.partition("|")
                if a and b:
                    o.edge[(a, b)] = float(v)
        o.aktivasi = dict(d.get("aktivasi") or {})
        o.asosiasi_terbentuk = [dict(x) for x in (d.get("asosiasi_terbentuk") or [])]
        return o


# ===========================================================================
# 5. LATENT DRIFT — PROSES ORNSTEIN-UHLENBECK
# ===========================================================================
class ProsesOU:
    """x_t+1 = x_t + θ(μ − x_t)dt + σ√dt·N(0,1), terikat [−batas, +batas].

    μ = kecenderungan watak (mis. cemas). Menyuntikkan derau terikat ke nilai
    drive agar status internal "bernafas" — mood swing tanpa if-else baru.
    """

    def __init__(self, theta: float = 0.08, sigma: float = 0.018,
                 batas: float = 0.12, mu: Optional[Dict[str, float]] = None,
                 ) -> None:
        self.theta = float(theta)
        self.sigma = float(sigma)
        self.batas = float(batas)
        self.mu: Dict[str, float] = dict(mu or {})
        self.x: Dict[str, float] = {}

    def nilai(self, drive: str) -> float:
        return self.x.get(str(drive), 0.0)

    def langkah(self, drive: Iterable[str], dt: float = 1.0,
                rng: Optional[random.Random] = None) -> Dict[str, float]:
        """Kembalikan INKREMEN per drive (untuk ditambahkan ke level)."""
        r = rng or random
        dt = max(1e-6, float(dt))
        akar = math.sqrt(dt)
        ink: Dict[str, float] = {}
        for d in drive:
            d = str(d)
            x = self.x.get(d, 0.0)
            mu = float(self.mu.get(d, 0.0))
            x = x + self.theta * (mu - x) * dt + self.sigma * akar * r.gauss(0.0, 1.0)
            x = max(-self.batas, min(self.batas, x))
            self.x[d] = x
            ink[d] = x
        return ink

    def ringkas(self) -> Dict[str, float]:
        return {d: round(v, 4) for d, v in self.x.items()}

    def to_dict(self) -> Dict[str, Any]:
        return {"theta": self.theta, "sigma": self.sigma, "batas": self.batas,
                "mu": dict(self.mu), "x": dict(self.x)}

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "ProsesOU":
        o = cls(theta=d.get("theta", 0.08), sigma=d.get("sigma", 0.018),
                batas=d.get("batas", 0.12), mu=d.get("mu"))
        o.x = dict(d.get("x") or {})
        return o


# ===========================================================================
# WADAH: menyatukan kelimanya untuk satu langkah
# ===========================================================================
class KognisiLanjut:
    """Bundel lima mekanisme + satu langkah terpadu `langkah()`."""

    def __init__(self, seed: int = 0, **kw: Any) -> None:
        self.rng = random.Random(int(seed) * 2654435761 & 0x7FFFFFFF)
        self.eversi = EversiTD(**{k: v for k, v in kw.items()
                                  if k in ("alpha", "gamma", "laju_eversi",
                                           "batas_eversi")})
        self.kepercayaan = MesinKepercayaan()
        self.graf = GrafAsosiasi()
        self.ou = ProsesOU()
        self.aktif = {"eversi": False, "boltzmann": False,
                      "kepercayaan": False, "asosiasi": False, "drift": False}
        self.riwayat: List[Dict[str, Any]] = []

    def aktifkan(self, **flag: bool) -> "KognisiLanjut":
        for k, v in flag.items():
            if k in self.aktif:
                self.aktif[k] = bool(v)
        return self

    # -- langkah per-tick -------------------------------------------------
    def langkah(self, levels: Dict[str, float], emosi: Dict[str, float],
                disonansi: float, dt: float = 1.0) -> Dict[str, Any]:
        """Terapkan drift + asosiasi + eversi/TD untuk satu tick."""
        out: Dict[str, Any] = {}
        if self.aktif["drift"] and levels:
            ink = self.ou.langkah(list(levels), dt, self.rng)
            for d, v in ink.items():
                levels[d] = jepit_drive(float(levels.get(d, 0.0)) + v)
            out["drift"] = self.ou.ringkas()
        if self.aktif["asosiasi"]:
            # Fire together, wire together: bahaya & takut menguat saat takut tinggi
            f = max(0.0, float(emosi.get("takut", 0.0)))
            if f > 0.15:
                for d in ("keamanan", "bahaya"):
                    if d in levels:
                        self.graf.koaktifkan("bahaya", "takut",
                                             gain=abs(float(levels[d])), takut=f)
            self.graf.luruh(dt)
            out["asosiasi"] = {"bahaya-takut": round(
                self.graf.bobot("bahaya", "takut"), 4)}
        if self.aktif["eversi"]:
            cemas = float(emosi.get("takut", 0.0)) + max(
                0.0, -float(levels.get("keamanan", 0.0)))
            r = self.eversi.reward_intrinsik(disonansi, cemas)
            ev = self.eversi.eversi_param()
            out["reward"] = round(r, 5)
            out["eversi"] = {k: round(v, 5) for k, v in ev.items()}
            # terapkan redaman emosi/drive yang dipelajari
            for e in list(emosi):
                emosi[e] = float(emosi[e]) * self.eversi.ambil("redaman_emosi")
        self.riwayat.append(out)
        if len(self.riwayat) > 40:
            del self.riwayat[:-40]
        return out

    def to_dict(self) -> Dict[str, Any]:
        state = self.rng.getstate()
        return {"rng_state": [state[0], list(state[1]), state[2]],
                "eversi": self.eversi.to_dict(),
                "kepercayaan": self.kepercayaan.to_dict(),
                "graf": self.graf.to_dict(), "ou": self.ou.to_dict(),
                "aktif": dict(self.aktif)}

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "KognisiLanjut":
        o = cls()
        if "rng_state" in d:
            # JSON mengubah tuple menjadi list. setstate memvalidasi struktur
            # generator; save baru rusak ditolak, bukan diam-diam di-reseed.
            state = d["rng_state"]
            if not isinstance(state, (list, tuple)) or len(state) != 3:
                raise ValueError("rng_state harus memiliki tiga komponen")
            try:
                cache = state[2]
                if cache is not None and (isinstance(cache, bool)
                                          or not isinstance(cache, (int, float))
                                          or not math.isfinite(cache)):
                    raise ValueError("cache Gaussian tidak valid")
                o.rng.setstate((state[0], tuple(state[1]), cache))
            except (TypeError, ValueError, OverflowError) as galat:
                raise ValueError("rng_state tidak valid") from galat
        o.eversi = EversiTD.from_dict(d.get("eversi") or {})
        o.kepercayaan = MesinKepercayaan.from_dict(d.get("kepercayaan") or {})
        o.graf = GrafAsosiasi.from_dict(d.get("graf") or {})
        o.ou = ProsesOU.from_dict(d.get("ou") or {})
        o.aktif.update(d.get("aktif") or {})
        return o


__all__ = ["EversiTD", "boltzmann_pilih", "suhu_mental", "MesinKepercayaan",
           "GrafAsosiasi", "ProsesOU", "KognisiLanjut", "EMOSI_NODE"]
