"""Ekstensi kognisi: definisi terpisah, patch dipasang oleh registri eksplisit."""
from __future__ import annotations

from typing import Mapping
from pycos.dukungan import diagnostik as _diag
from pycos.dukungan.patching import install_method, install_methods, optional_module, wrap_method
from pycos.inti.presentasi import Presentasi

def _kog_disonansi(obj):
    ks = getattr(obj, "kesadaran", None)
    if ks is None:
        return 0.0
    d = getattr(ks, "dissonance", None)
    if isinstance(d, dict):
        return float(sum(abs(float(v)) for v in d.values()))
    for nama in ("_dissonansi", "_dissonance", "dissonansi"):
        fn = getattr(obj, nama, None)
        if callable(fn):
            try:
                return float(fn())
            except Exception as _galat_diagnostik_187:
                _diag.catat('naluri._kog_disonansi', "galat pada jalur fallback", galat=_galat_diagnostik_187, jalur=187)
                pass
    return 0.0


def _kog_situasi(obj):
    levels = getattr(obj, "levels", {}) or {}
    emosi = getattr(obj, "emosi", {}) or {}
    drv = max(levels, key=lambda k: abs(float(levels.get(k, 0.0)))) if levels else "-"
    emo = max(emosi, key=lambda k: abs(float(emosi.get(k, 0.0)))) if emosi else "-"
    return "%s|%s" % (drv, emo)


def _kog_aksi(obj):
    p = getattr(obj, "presentasi", None)
    log = getattr(p, "_log", None) if p is not None else None
    if isinstance(log, list) and log:
        return str(log[-1].get("act", "diam"))
    return str(getattr(obj, "act_terakhir", "diam"))


def _kog_dari(obj):
    kog = getattr(obj, "_kog", None)
    if kog is None:
        modul = optional_module("pycos.mandiri.kognisi_lanjut")
        if modul is None:
            return None
        seed = int(getattr(obj, "rng_seed", 0) or 0)
        kog = modul.KognisiLanjut(seed=seed)
        obj._kog = kog
        obj._kog_prev = None
    return kog


def _naluri_enable_eversi(self, aktif=True, alpha=None, gamma=None):
    kog = _kog_dari(self)
    if kog is None:
        return False
    kog.aktifkan(eversi=bool(aktif))
    if alpha is not None:
        kog.eversi.alpha = float(alpha)
    if gamma is not None:
        kog.eversi.gamma = float(gamma)
    return bool(aktif)


def _naluri_enable_drift(self, aktif=True, theta=None, sigma=None, batas=None):
    kog = _kog_dari(self)
    if kog is None:
        return False
    kog.aktifkan(drift=bool(aktif))
    if theta is not None:
        kog.ou.theta = float(theta)
    if sigma is not None:
        kog.ou.sigma = float(sigma)
    if batas is not None:
        kog.ou.batas = float(batas)
    return bool(aktif)


def _naluri_enable_asosiasi(self, aktif=True, laju=None, ambang=None):
    kog = _kog_dari(self)
    if kog is None:
        return False
    kog.aktifkan(asosiasi=bool(aktif))
    if laju is not None:
        kog.graf.laju_hebb = float(laju)
    if ambang is not None:
        kog.graf.ambang_fobia = float(ambang)
    return bool(aktif)


def _naluri_eversi_param(self):
    kog = _kog_dari(self)
    if kog is None:
        return {}
    kog.eversi.eversi_param()
    return dict(kog.eversi.eversi)


def _naluri_latent_drift(self):
    kog = _kog_dari(self)
    return kog.ou.ringkas() if kog else {}


def _naluri_asosiasi(self, konsep, top=5):
    kog = _kog_dari(self)
    return kog.graf.asosiasi(konsep, top) if kog else []


def _naluri_koaktifkan(self, a, b, gain=1.0, takut=None):
    kog = _kog_dari(self)
    if kog is None:
        return 0.0
    if takut is None:
        takut = float((getattr(self, "emosi", {}) or {}).get("takut", 0.0))
    return kog.graf.koaktifkan(a, b, gain, takut)


def _naluri_aktifkan_konsep(self, konsep, energi=1.0, sebar=1):
    kog = _kog_dari(self)
    return kog.graf.aktifkan(konsep, energi, sebar) if kog else {}


def _naluri_fobia(self, minimum=None):
    kog = _kog_dari(self)
    return kog.graf.fobia(minimum) if kog else []


def _naluri_kepercayaan(self, hipotesis):
    kog = _kog_dari(self)
    return kog.kepercayaan.kepercayaan(hipotesis) if kog else 0.5


def _naluri_perbarui_kepercayaan(self, hipotesis, lr, bobot=1.0, label=""):
    kog = _kog_dari(self)
    if kog is None:
        return 0.5
    return kog.kepercayaan.perbarui(hipotesis, lr, bobot, label)


def _naluri_kognisi_state(self):
    kog = getattr(self, "_kog", None)
    return kog.to_dict() if kog is not None else {}


def _naluri_kog_step(self):
    kog = getattr(self, "_kog", None)
    if kog is None or not any(kog.aktif.values()):
        return
    levels = getattr(self, "levels", None)
    emosi = getattr(self, "emosi", None)
    if levels is None or emosi is None:
        return
    kog.langkah(levels, emosi, _kog_disonansi(self), dt=1.0)
    if kog.aktif.get("eversi"):
        s = _kog_situasi(self)
        a = _kog_aksi(self)
        r = kog.eversi.reward_terakhir
        prev = getattr(self, "_kog_prev", None)
        if prev:
            kog.eversi.update(prev[0], prev[1], r, s)
        self._kog_prev = (s, a)




def _kog_tick(original, self, *a, **k):
    hasil = original(self, *a, **k)
    try:
        _naluri_kog_step(self)
    except Exception as _galat_diagnostik_188:
        _diag.catat('naluri._kog_tick', "galat pada jalur fallback", galat=_galat_diagnostik_188, jalur=188)
        pass
    return hasil




def _kog_to_dict(original, self, *a, **k):
    data = original(self, *a, **k)
    kog = getattr(self, "_kog", None)
    if isinstance(data, dict) and kog is not None:
        data["kognisi_lanjut"] = kog.to_dict()
        prev = getattr(self, "_kog_prev", None)
        data["kognisi_prev"] = list(prev) if prev is not None else None
    return data


def _kog_from_dict(original, cls, data, *a, **k):
    hasil = original(cls, data, *a, **k)
    if isinstance(data, Mapping) and data.get("kognisi_lanjut"):
        modul = optional_module("pycos.mandiri.kognisi_lanjut")
        if modul is not None:
            try:
                hasil._kog = modul.KognisiLanjut.from_dict(
                    data["kognisi_lanjut"])
                prev = data.get("kognisi_prev")
                hasil._kog_prev = (tuple(prev) if isinstance(prev, (list, tuple))
                                   and len(prev) == 2
                                   and all(isinstance(x, str) for x in prev) else None)
            except (AttributeError, TypeError, ValueError):
                pass
    return hasil




# ------------------------- Presentasi: Boltzmann ---------------------------
def _pres_enable_boltzmann(self, aktif=True, dasar=None, gain_arousal=None,
                           gain_lelahan=None):
    self.params["presentasi_boltzmann"] = bool(aktif)
    if dasar is not None:
        self.params["presentasi_tau_dasar"] = float(dasar)
    if gain_arousal is not None:
        self.params["presentasi_tau_arousal"] = float(gain_arousal)
    if gain_lelahan is not None:
        self.params["presentasi_tau_lelahan"] = float(gain_lelahan)
    return bool(aktif)


def _pres_skor_acts(self, kepada=None, topik=None, masuk=False):
    """Skor tiap tindak tutur dari keadaan internal (bukan if-else)."""
    n = self.naluri
    levels = getattr(n, "levels", {}) or {}
    emosi = getattr(n, "emosi", {}) or {}
    lv = lambda d: float(levels.get(d, 0.0))
    em = lambda e: float(emosi.get(e, 0.0))
    takut = max(0.0, em("takut")) + max(0.0, -lv("keamanan"))
    sedih = max(0.0, em("sedih"))
    marah = max(0.0, em("marah"))
    senang = max(0.0, em("senang"))
    try:
        label = str(self._label_rel(kepada)) if kepada is not None else "netral"
    except Exception as _galat_diagnostik_189:
        _diag.catat('naluri._pres_skor_acts', "galat pada jalur fallback", galat=_galat_diagnostik_189, jalur=189)
        label = "netral"
    dekat = 1.0 if label in ("akrab", "suka", "percaya") else 0.0
    jauhi = 1.0 if label in ("curiga", "benci", "takut") else 0.0
    doubt = float(getattr(self, "_doubt", lambda: 0.0)() or 0.0)
    agency = float(getattr(n, "agency", 0.5) or 0.5)
    spotlight = getattr(getattr(n, "kesadaran", None), "spotlight", None) or []
    kesadaran = getattr(n, "kesadaran", None)
    dissonance = len(getattr(kesadaran, "dissonance", {}) or {})
    grief = len(getattr(kesadaran, "grief", {}) or {})
    lelah = max(0.0, -lv("istirahat")) + max(0.0, -lv("energi"))
    skor = {
        "ragu": 0.9 * doubt + 0.6 * takut,
        "waspada": 0.8 * takut + 0.7 * jauhi,
        "menantang": 0.9 * marah + 0.5 * jauhi,
        "menegur": 0.6 * marah + 0.5 * doubt,
        "menolak": 0.5 * jauhi + 0.4 * doubt + 0.3 * marah,
        "mengenang": 0.8 * sedih + 0.6 * (1.0 if grief else 0.0),
        "eksistensial": 0.7 * sedih + 0.4 * doubt,
        "mimpi": 0.7 * lelah + 0.3 * (1.0 - agency),
        "rasionalisasi": 0.8 * (1.0 if dissonance else 0.0) + 0.4 * doubt,
        "peringatan": 0.7 * takut + 0.6 * dekat,
        "akrab": 0.9 * senang + 0.8 * dekat,
        "menjawab": 0.9 * (1.0 if masuk else 0.0) + 0.2,
        "mengamati": 0.8 * (1.0 if spotlight else 0.0),
        "bertanya": 0.5 * doubt + 0.5 * (1.0 if masuk else 0.0),
        "menyapa_proaktif": 0.6 * dekat + 0.4 * senang,
        "kembali": 0.5 * dekat + 0.4 * senang,
        "menyatakan": 0.25 + 0.3 * (1.0 - doubt),
        "menimbang": 0.5 * doubt + 0.3 * lelah,
    }
    return skor


def _pres_pilih_act_boltzmann(self, kepada=None, topik=None, masuk=False):
    modul = optional_module("pycos.mandiri.kognisi_lanjut")
    if modul is None:
        skor = self._skor_acts(kepada, topik, masuk)
        return max(skor, key=skor.get) if skor else "menyatakan"
    n = self.naluri
    emosi = getattr(n, "emosi", {}) or {}
    levels = getattr(n, "levels", {}) or {}
    takut = max(0.0, float(emosi.get("takut", 0.0)))
    lelah = max(0.0, -float(levels.get("istirahat", 0.0))) + \
        max(0.0, -float(levels.get("energi", 0.0)))
    tau = modul.suhu_mental(
        takut, lelah,
        dasar=float(self.params.get("presentasi_tau_dasar", 0.15)),
        gain_arousal=float(self.params.get("presentasi_tau_arousal", 1.4)),
        gain_lelahan=float(self.params.get("presentasi_tau_lelahan", 1.1)))
    skor = self._skor_acts(kepada, topik, masuk)
    rng = getattr(n, "rng", None) or getattr(n, "_rng", None)
    act, dist = modul.boltzmann_pilih(skor, tau, rng)
    self._boltzmann_terakhir = {"tau": round(tau, 4), "distribusi": dist,
                                "skor": skor, "act": act}
    return act


def _pres_boltzmann_terakhir(self):
    return getattr(self, "_boltzmann_terakhir", {})




def _pilih_act_boltzmann(original, self, *a, **k):
    if bool(self.params.get("presentasi_boltzmann", False)):
        try:
            kepada = a[0] if len(a) > 0 else k.get("kepada")
            topik = a[1] if len(a) > 1 else k.get("topik")
            masuk = a[2] if len(a) > 2 else k.get("masuk", False)
            return self._pilih_act_boltzmann(kepada, topik, masuk)
        except Exception as _galat_diagnostik_190:
            _diag.catat('naluri._pilih_act_boltzmann', "galat pada jalur fallback", galat=_galat_diagnostik_190, jalur=190)
            pass
    return original(self, *a, **k)


def _pasang_boltzmann():
    """Kompatibilitas untuk pemanggil lama; pemasangan kini idempoten."""
    return wrap_method(Presentasi, "_pilih_act", _pilih_act_boltzmann,
                      patch_id="naluri.boltzmann.choice")















def pasang(Naluri: type) -> None:
    """Pasang patch dengan urutan dan ID historis."""
    for _nama, _fn in (("enable_eversi", _naluri_enable_eversi),
                       ("enable_latent_drift", _naluri_enable_drift),
                       ("enable_asosiasi", _naluri_enable_asosiasi),
                       ("eversi_param", _naluri_eversi_param),
                       ("latent_drift", _naluri_latent_drift),
                       ("asosiasi", _naluri_asosiasi),
                       ("koaktifkan", _naluri_koaktifkan),
                       ("aktifkan_konsep", _naluri_aktifkan_konsep),
                       ("fobia", _naluri_fobia),
                       ("kepercayaan", _naluri_kepercayaan),
                       ("perbarui_kepercayaan", _naluri_perbarui_kepercayaan),
                       ("kognisi_state", _naluri_kognisi_state)):
        install_method(Naluri, _nama, _fn,
                       patch_id="naluri.extension.Naluri." + _nama)

    wrap_method(Naluri, "tick", _kog_tick, patch_id="naluri.kognisi.tick")

    wrap_method(Naluri, "to_dict", _kog_to_dict,
                patch_id="naluri.kognisi.serialisasi")

    wrap_method(Naluri, "from_dict", _kog_from_dict,
                patch_id="naluri.kognisi.deserialisasi")

    install_methods(
        Presentasi,
        (("enable_boltzmann", _pres_enable_boltzmann),
         ("_skor_acts", _pres_skor_acts),
         ("_pilih_act_boltzmann", _pres_pilih_act_boltzmann),
         ("boltzmann_terakhir", _pres_boltzmann_terakhir)),
        patch_id="naluri.boltzmann.api",
    )

    _pasang_boltzmann()

