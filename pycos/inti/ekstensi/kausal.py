"""Ekstensi kausal: definisi terpisah, patch dipasang oleh registri eksplisit."""
from __future__ import annotations

from typing import Any, Dict
from pycos.dukungan import diagnostik as _diag
from pycos.dukungan.patching import install_method, wrap_method

# >>> KAUSAL-BLOCK-START (naluri) <<<
# Poin 1: MODEL KAUSAL DUNIA. JEJAK menyimpan stimulus→aksi→hasil; predict()
# mengagregasinya jadi ANGKA (korelasi → vektor). Sistem bisa memprediksi,
# tak bisa MENJELASKAN. Blok ini menyambungkan ModelKausal ke
# JEJAK nyata: menambang episode jadi graf kausal (node+tepi berjenis), lalu
# mengekspos penjelasan "kenapa" (rantai sebab), counterfactual BERMEKANISME
# ("...karena Z"), blame (aksi vs kebetulan, diskon konfounder), dan jalur
# mekanisme. Mati bawaan.


def _kausal_dari(obj):
    from pycos.inti.naluri import _organik_dari
    o = _organik_dari(obj, getattr(obj, "rng_seed", 0) or 0)
    return getattr(o, "kausal", None) if o is not None else None


def _kausal_aktif(self) -> bool:
    return bool(self.params.get("enable_kausal", False))


def pelajari_kausal(self) -> Dict[str, Any]:
    """Tambang episode JEJAK yang BARU (inkremental by id) jadi tepi kausal."""
    mk = _kausal_dari(self)
    if mk is None:
        return {"aktif": False}
    jejak = getattr(self, "jejak", None)
    if jejak is None:
        return {"aktif": _kausal_aktif(self), "belajar": 0}
    try:
        eps = list(jejak.experiences)
    except Exception as _galat_diagnostik_237:
        _diag.catat('naluri.pelajari_kausal', "galat pada jalur fallback", galat=_galat_diagnostik_237, jalur=237)
        eps = []
    terakhir = int(getattr(self, "_kausal_terakhir", -1))
    baru = [e for e in eps if int(e.get("id", 0)) > terakhir]
    if baru:
        mk.pelajari(baru)
        self._kausal_terakhir = max(int(e.get("id", 0)) for e in baru)
    return {"aktif": _kausal_aktif(self), "belajar": len(baru), "ringkas": mk.ringkas()}


def jelaskan_kenapa(self, target, kedalaman: int = 4) -> Dict[str, Any]:
    """Rantai sebab yang diartikulasikan: 'X karena A karena S'."""
    mk = _kausal_dari(self)
    if mk is None:
        return {"aktif": False}
    pelajari_kausal(self)
    return mk.jelaskan(target, kedalaman)


def counterfactual_kausal(self, stimulus, aksi_alt) -> Dict[str, Any]:
    """'Kalau aku <aksi>, <Y> karena <Z>' — dengan mekanisme, atau jujur tak ada Z."""
    mk = _kausal_dari(self)
    if mk is None:
        return {"aktif": False}
    pelajari_kausal(self)
    return mk.counterfactual(stimulus, aksi_alt)


def blame_kausal(self, stimulus, aksi, hasil_label) -> Dict[str, Any]:
    """Atribusi kausal: 'karena aksiku' vs 'kebetulan situasi'."""
    mk = _kausal_dari(self)
    if mk is None:
        return {"aktif": False}
    pelajari_kausal(self)
    return mk.blame(stimulus, aksi, hasil_label)


def mekanisme_kausal(self, a, b) -> Dict[str, Any]:
    """Jalur kausal terpendek a→b: 'bagaimana X mengarah ke Y'."""
    mk = _kausal_dari(self)
    if mk is None:
        return {"aktif": False}
    pelajari_kausal(self)
    return mk.mekanisme(a, b)


def kausal_state(self) -> Dict[str, Any]:
    mk = _kausal_dari(self)
    if mk is None:
        return {"aktif": False}
    st = mk.state()
    st["aktif"] = _kausal_aktif(self)
    return st


def enable_kausal(self, aktif: bool = True) -> Dict[str, Any]:
    """Nyalakan/matikan model kausal — mati bawaan."""
    self.params["enable_kausal"] = bool(aktif)
    return {"enable_kausal": bool(self.params.get("enable_kausal", False)),
            "kemampuan": "jelaskan, counterfactual bermekanisme, blame aksi-vs-kebetulan"}




def _kausal_step(self):
    if not _kausal_aktif(self):
        return
    tunggu = int(getattr(self, "_kausal_tunggu", 0)) - 1
    if tunggu > 0:
        self._kausal_tunggu = tunggu
        return
    self._kausal_tunggu = max(1, int((self.params or {}).get("kausal_cadence", 8)))
    try:
        pelajari_kausal(self)
    except Exception as _galat_diagnostik_238:
        _diag.catat('naluri._kausal_step', "galat pada jalur fallback", galat=_galat_diagnostik_238, jalur=238)
        pass


def _kausal_tick(original, self, *a, **k):
    from pycos.inti.naluri import _kausal_step
    hasil = original(self, *a, **k)
    try:
        _kausal_step(self)
    except Exception as _galat_diagnostik_239:
        _diag.catat('naluri._kausal_tick', "galat pada jalur fallback", galat=_galat_diagnostik_239, jalur=239)
        pass
    return hasil


def _pasang_kausal_tick():
    from pycos.inti.naluri import Naluri
    return wrap_method(Naluri, "tick", _kausal_tick,
                      patch_id="naluri.kausal.tick")




# >>> KAUSAL-BLOCK-END (naluri) <<<

def pasang(Naluri: type) -> None:
    """Pasang patch dengan urutan dan ID historis."""
    for _nama, _fn in (("enable_kausal", enable_kausal),
                       ("pelajari_kausal", pelajari_kausal),
                       ("jelaskan_kenapa", jelaskan_kenapa),
                       ("counterfactual_kausal", counterfactual_kausal),
                       ("blame_kausal", blame_kausal),
                       ("mekanisme_kausal", mekanisme_kausal),
                       ("kausal_state", kausal_state)):
        install_method(Naluri, _nama, _fn,
                       patch_id="naluri.extension.Naluri." + _nama)

    _pasang_kausal_tick()

