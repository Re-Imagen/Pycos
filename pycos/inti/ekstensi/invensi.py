"""Ekstensi invensi: definisi terpisah, patch dipasang oleh registri eksplisit."""
from __future__ import annotations

from typing import Any, Dict, List, Optional
from pycos.dukungan import diagnostik as _diag
from pycos.dukungan.patching import install_method, wrap_method

# >>> INVENSI-BLOCK-START (naluri) <<<
# Pelita STRUKTUR BARU (endogen). Semua layer Pycos menambah dimensi (drive,
# emosi, lapisan paralel, residu, bekas), tapi tak satu pun menghasilkan BENTUK
# baru — hipotesis/rencana/kategori/tujuan yang belum pernah ada. Gejala hanya
# mendekati kategori baru dari tekan LUAR. Invensi (organik) adalah mesin
# generatif dari DALAM; blok ini menyambungkannya ke state Naluri yang nyata:
# ia mengambil "digest" dari drives, emosi, graf asosiasi, keyakinan, disonansi
# kesadaran, kekosongan topologi, lubang luka & kontradiksi paralel, lalu
# mengkristalkan hipotesis baru menjadi KEYAKINAN NYATA di MesinKepercayaan,
# sementara tujuan/rencana/kategori baru disimpan bersama provenance di wadah
# Invensi (BUKAN disuntik ke Naluri.goals yang diturunkan-ulang dari drive
# setiap tick — rapuh). Mati bawaan (enable_invensi) demi kompatibilitas.


def _invensi_dari(obj):
    """Ambil mesin Invensi dari wadah Organik; pasang knob desainer sekali."""
    from pycos.inti.naluri import _organik_dari
    o = _organik_dari(obj, getattr(obj, "rng_seed", 0) or 0)
    if o is None:
        return None
    inv = getattr(o, "invensi", None)
    if inv is None:
        return None
    inv.set_knob(getattr(obj, "params", None) or {})
    return inv


def _invensi_aktif(self) -> bool:
    return bool(self.params.get("enable_invensi", False))


def _inv_teks(x) -> str:
    """Ekstrak teks episode dari entri memori (dict atau objek)."""
    if isinstance(x, dict):
        return str(x.get("ringkas") or x.get("isi") or x.get("teks") or "")
    return str(getattr(x, "ringkas", "") or getattr(x, "isi", "")
               or getattr(x, "teks", "") or "")


def _invensi_digest(self) -> Dict[str, Any]:
    """Digest data-polano dari state yang ADA (bebas mengintip isi internal)."""
    from pycos.inti.naluri import _kog_dari
    dg: Dict[str, Any] = {"drives": {}, "emosi": {}, "asosiasi": [],
                          "keyakinan": [], "dissonance": [], "kekosongan": [],
                          "lubang": [], "kontradiksi": [], "episode": [],
                          "konsep": [], "tujuan": []}
    try:
        dg["drives"] = {k: float(v) for k, v in (getattr(self, "levels", {}) or {}).items()}
    except Exception as _galat_diagnostik_221:
        _diag.catat('naluri._invensi_digest', "galat pada jalur fallback", galat=_galat_diagnostik_221, jalur=221)
        pass
    try:
        dg["emosi"] = {k: float(v) for k, v in (getattr(self, "emosi", {}) or {}).items()}
    except Exception as _galat_diagnostik_222:
        _diag.catat('naluri._invensi_digest', "galat pada jalur fallback", galat=_galat_diagnostik_222, jalur=222)
        pass
    # graf asosiasi + keyakinan (kognisi lanjut, lazim)
    try:
        kog = _kog_dari(self)
    except Exception as _galat_diagnostik_223:
        _diag.catat('naluri._invensi_digest', "galat pada jalur fallback", galat=_galat_diagnostik_223, jalur=223)
        kog = None
    if kog is not None:
        try:
            edge = dict(getattr(kog.graf, "edge", {}) or {})
            for (a, b), w in edge.items():
                dg["asosiasi"].append((a, b, float(w)))
            dg["konsep"] = list(dict.fromkeys([a for (a, _b) in edge.keys()]))
        except Exception as _galat_diagnostik_224:
            _diag.catat('naluri._invensi_digest', "galat pada jalur fallback", galat=_galat_diagnostik_224, jalur=224)
            pass
        try:
            dg["keyakinan"] = list((kog.kepercayaan.ringkas() or {}).keys())
        except Exception as _galat_diagnostik_225:
            _diag.catat('naluri._invensi_digest', "galat pada jalur fallback", galat=_galat_diagnostik_225, jalur=225)
            pass
    # kesadaran: disonansi + episode terbaru
    ks = getattr(self, "kesadaran", None)
    if ks is not None:
        try:
            dg["dissonance"] = list((getattr(ks, "dissonance", {}) or {}).keys())
        except Exception as _galat_diagnostik_226:
            _diag.catat('naluri._invensi_digest', "galat pada jalur fallback", galat=_galat_diagnostik_226, jalur=226)
            pass
        try:
            dg["episode"] = ([_inv_teks(x) for x in (getattr(ks, "core_memory", []) or [])][-6:]
                             + [_inv_teks(x) for x in (getattr(ks, "timeline", []) or [])][-6:])
        except Exception as _galat_diagnostik_227:
            _diag.catat('naluri._invensi_digest', "galat pada jalur fallback", galat=_galat_diagnostik_227, jalur=227)
            pass
    # organik: kekosongan slot, lubang luka, kontradiksi lapisan paralel
    o = getattr(self, "_organik", None)
    if o is not None:
        try:
            dg["kekosongan"] = list(o.topologi.kosong())
        except Exception as _galat_diagnostik_228:
            _diag.catat('naluri._invensi_digest', "galat pada jalur fallback", galat=_galat_diagnostik_228, jalur=228)
            pass
        try:
            dg["lubang"] = [{"ent": e, "domain": dom}
                            for e, doms in (o.luka.ringkas() or {}).items()
                            for dom in doms]
        except Exception as _galat_diagnostik_229:
            _diag.catat('naluri._invensi_digest', "galat pada jalur fallback", galat=_galat_diagnostik_229, jalur=229)
            pass
        try:
            dg["kontradiksi"] = list(o.paralel.bertentangan())[:3]
        except Exception as _galat_diagnostik_230:
            _diag.catat('naluri._invensi_digest', "galat pada jalur fallback", galat=_galat_diagnostik_230, jalur=230)
            pass
    # tujuan yang SUDAH ada (untuk dikonstruksi jadi rencana)
    try:
        dg["tujuan"] = [str(getattr(g, "statement", ""))
                        for g in (getattr(self, "goals", []) or [])][:4]
    except Exception as _galat_diagnostik_231:
        _diag.catat('naluri._invensi_digest', "galat pada jalur fallback", galat=_galat_diagnostik_231, jalur=231)
        pass
    return dg


def enable_invensi(self, aktif: bool = True) -> Dict[str, Any]:
    """Nyalakan/matikan pelita STRUKTUR BARU — mati bawaan."""
    self.params["enable_invensi"] = bool(aktif)
    return {"enable_invensi": bool(self.params.get("enable_invensi", False)),
            "operasi": ("negasi, abstraksi, analogi, pengisian, inventori, "
                        "konstruksi, pengelompokan")}


def lahirkan_struktur(self, tick: Optional[int] = None) -> Dict[str, Any]:
    """Lahirkan struktur baru dari state internal & kristalkanasi hipotesis.

    Hipotesis yang lahir (dan lolos saringan kebaruan/koherensi) dijadikan
    KEYAKINAN NYATA di MesinKepercayaan pada prior netral (0.5) — ia bisa
    dikonfirmasi/ditolak kemudian. Tujuan/rencana/kategori disimpan bersama
    provenance di wadah Invensi.
    """
    from pycos.inti.naluri import _kog_dari, _naluri_tick
    inv = _invensi_dari(self)
    if inv is None:
        return {"aktif": False}
    t = _naluri_tick(self) if tick is None else int(tick)
    dg = _invensi_digest(self)
    usul = inv.lahirkan(dg, t)
    kog = None
    try:
        kog = _kog_dari(self)
    except Exception as _galat_diagnostik_232:
        _diag.catat('naluri.lahirkan_struktur', "galat pada jalur fallback", galat=_galat_diagnostik_232, jalur=232)
        kog = None
    lahir = {"hipotesis": [], "rencana": [], "kategori": [], "tujuan": []}
    for s in usul:
        lahir[s["jenis"]].append(s["isi"])
        if s["jenis"] == "hipotesis" and kog is not None:
            try:
                kog.kepercayaan.tetapkan(s["isi"], 0.5)   # jadi keyakinan nyata
            except Exception as _galat_diagnostik_233:
                _diag.catat('naluri.lahirkan_struktur', "galat pada jalur fallback", galat=_galat_diagnostik_233, jalur=233)
                pass
    return {"aktif": True, "tick": t, "usul": len(usul), "lahir": lahir}


def kristalkan_invensi(self, tick: Optional[int] = None) -> List[Dict[str, Any]]:
    """Naikkan usul → kristal bila lolos ambang kebaruan & koherensi."""
    from pycos.inti.naluri import _naluri_tick
    inv = _invensi_dari(self)
    if inv is None:
        return []
    t = _naluri_tick(self) if tick is None else int(tick)
    return inv.kristal(t)


def invensi_state(self) -> Dict[str, Any]:
    """Keadaan pelita struktur baru (untuk inspeksi/HUD)."""
    inv = _invensi_dari(self)
    if inv is None:
        return {"aktif": False}
    st = inv.state()
    st["aktif"] = _invensi_aktif(self)
    return st




def _naluri_invensi_step(self):
    """Hook per-tick: lahirkan struktur baru secara berkala (ide muncul sendiri)."""
    from pycos.inti.naluri import _naluri_tick
    if not _invensi_aktif(self):
        return
    tunggu = int(getattr(self, "_invensi_tunggu", 0)) - 1
    if tunggu > 0:
        self._invensi_tunggu = tunggu
        return
    try:
        cadence = max(1, int((self.params or {}).get("invensi_cadence", 25)))
    except Exception as _galat_diagnostik_234:
        _diag.catat('naluri._naluri_invensi_step', "galat pada jalur fallback", galat=_galat_diagnostik_234, jalur=234)
        cadence = 25
    self._invensi_tunggu = cadence
    try:
        t = _naluri_tick(self)
        lahirkan_struktur(self, tick=t)
        inv = _invensi_dari(self)
        if inv is not None:
            inv.kristal(t)
            inv.gugur(t)
    except Exception as _galat_diagnostik_235:
        _diag.catat('naluri._naluri_invensi_step', "galat pada jalur fallback", galat=_galat_diagnostik_235, jalur=235)
        pass


def _invensi_tick(original, self, *a, **k):
    hasil = original(self, *a, **k)
    try:
        _naluri_invensi_step(self)
    except Exception as _galat_diagnostik_236:
        _diag.catat('naluri._invensi_tick', "galat pada jalur fallback", galat=_galat_diagnostik_236, jalur=236)
        pass
    return hasil


def _pasang_invensi_tick():
    from pycos.inti.naluri import Naluri
    return wrap_method(Naluri, "tick", _invensi_tick,
                      patch_id="naluri.invensi.tick")




# >>> INVENSI-BLOCK-END (naluri) <<<

def pasang(Naluri: type) -> None:
    """Pasang patch dengan urutan dan ID historis."""
    for _nama, _fn in (("enable_invensi", enable_invensi),
                       ("lahirkan_struktur", lahirkan_struktur),
                       ("kristalkan_invensi", kristalkan_invensi),
                       ("invensi_state", invensi_state)):
        install_method(Naluri, _nama, _fn,
                       patch_id="naluri.extension.Naluri." + _nama)

    _pasang_invensi_tick()

