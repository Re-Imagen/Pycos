"""Ekstensi perencana: definisi terpisah, patch dipasang oleh registri eksplisit."""
from __future__ import annotations

import re
from typing import Any, Dict, Iterable, List, Optional
from pycos.dukungan import diagnostik as _diag
from pycos.dukungan.patching import install_method

# >>> PERENCANA-BLOCK-START (naluri) <<<
# Poin 2: PERENCANAAN MULTI-TINGKAT. Goal.subgoals hanya satu tingkat; tak ada
# means-end, forward/backward chaining, dekomposisi rekursif, meta-planning.
# Perencana (organik.py) memakai ModelKausal sebagai MODEL DOMAIN: backward
# chaining (goal→aksi→precond→subgoal→...), forward chaining dari fakta, dan
# meta-planning (memutuskan strategi & anggaran kedalaman, sadar sedang
# merencanakan). Blok ini menyambungkannya ke JEJAK nyata via graf kausal.
# Mati bawaan; perencanaan on-demand (operasi penalaran, bukan periodik).


def _perencana_dari(obj):
    from pycos.inti.naluri import _organik_dari
    o = _organik_dari(obj, getattr(obj, "rng_seed", 0) or 0)
    return getattr(o, "perencana", None) if o is not None else None


def _perencana_aktif(self) -> bool:
    return bool(self.params.get("enable_perencana", False))


def _fakta_sekarang(self) -> List[str]:
    """Fakta kasar sekarang: token situasi terkini + label hasil yang dikenal."""
    from pycos.inti.naluri import _kog_dari
    fakta: List[str] = []
    try:
        konteks = str(getattr(getattr(self, "presentasi", None), "konteks", "") or "")
        fakta += re.findall(r"[a-z0-9]{3,}", konteks.lower())
    except Exception as _galat_diagnostik_240:
        _diag.catat('naluri._fakta_sekarang', "galat pada jalur fallback", galat=_galat_diagnostik_240, jalur=240)
        pass
    try:
        kog = _kog_dari(self)
        if kog is not None:
            fakta += list((kog.kepercayaan.ringkas() or {}).keys())
    except Exception as _galat_diagnostik_241:
        _diag.catat('naluri._fakta_sekarang', "galat pada jalur fallback", galat=_galat_diagnostik_241, jalur=241)
        pass
    return fakta


def rencanakan(self, tujuan, fakta: Optional[Iterable[str]] = None) -> Dict[str, Any]:
    """Rencanakan `tujuan` multi-tingkat memakai graf kausal sebagai domain."""
    from pycos.inti.naluri import _kausal_dari, pelajari_kausal
    pl = _perencana_dari(self)
    mk = _kausal_dari(self)
    if pl is None or mk is None:
        return {"aktif": False}
    pelajari_kausal(self)                       # pastikan graf kausal terbaru
    fk = list(fakta) if fakta is not None else _fakta_sekarang(self)
    hasil = pl.rencanakan_rencana(tujuan, mk, fk)
    return {"aktif": _perencana_aktif(self), "tujuan": str(tujuan),
            "meta": hasil["meta"], "pohon": hasil["pohon"],
            "langkah": pl.langkah(hasil["pohon"]["akar"]),
            "narasi": pl.narasi(hasil["pohon"]["akar"], mk)}


def rencana_state(self) -> Dict[str, Any]:
    pl = _perencana_dari(self)
    if pl is None:
        return {"aktif": False}
    st = pl.state()
    st["aktif"] = _perencana_aktif(self)
    return st


def enable_perencana(self, aktif: bool = True) -> Dict[str, Any]:
    """Nyalakan/matikan perencana multi-tingkat — mati bawaan."""
    self.params["enable_perencana"] = bool(aktif)
    return {"enable_perencana": bool(self.params.get("enable_perencana", False)),
            "kemampuan": "means-end, backward/forward chaining, dekomposisi, meta-planning"}




# >>> PERENCANA-BLOCK-END (naluri) <<<

def pasang(Naluri: type) -> None:
    """Pasang patch dengan urutan dan ID historis."""
    for _nama, _fn in (("enable_perencana", enable_perencana),
                       ("rencanakan", rencanakan),
                       ("rencana_state", rencana_state)):
        install_method(Naluri, _nama, _fn,
                       patch_id="naluri.extension.Naluri." + _nama)

