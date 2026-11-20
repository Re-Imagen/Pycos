# -*- coding: utf-8 -*-
"""Penulisan JSON atomik dan checksum integritas (bukan autentikasi).

Berkas lama tanpa checksum tetap terbaca. Temp file unik berada pada direktori
sama sehingga os.replace tidak melintasi filesystem. Sebelum replace gagal,
berkas target lama tidak disentuh. Snapshot in-memory/from_json tidak wajib
membawa checksum; verifikasi dilakukan pada API load berkas.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import tempfile
from typing import Any, Dict


def _kanonik(data: Dict[str, Any]) -> bytes:
    return json.dumps(data, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def simpan_json(path: Any, data: Dict[str, Any]) -> Any:
    """Flush + fsync + replace; selalu hapus temp yang belum dipasang."""
    payload = dict(data)
    if "_sha256" in payload:
        raise ValueError("_sha256 adalah field persistensi yang dicadangkan")
    payload["_sha256"] = hashlib.sha256(_kanonik(payload)).hexdigest()
    isi = json.dumps(payload, ensure_ascii=False, allow_nan=False).encode("utf-8")
    tujuan = os.path.abspath(os.fspath(path))
    fd, sementara = tempfile.mkstemp(prefix="." + os.path.basename(tujuan) + ".",
                                     suffix=".tmp", dir=os.path.dirname(tujuan))
    try:
        with os.fdopen(fd, "wb") as berkas:
            berkas.write(isi)
            berkas.flush()
            os.fsync(berkas.fileno())
        os.replace(sementara, tujuan)
    finally:
        if os.path.exists(sementara):
            os.unlink(sementara)
    return path


def muat_json(path: Any) -> Dict[str, Any]:
    """Baca JSON legacy atau verifikasi checksum snapshot baru."""
    with open(path, "r", encoding="utf-8") as berkas:
        payload = json.load(berkas)
    if not isinstance(payload, dict):
        raise ValueError("state berkas harus mapping JSON")
    if "_sha256" in payload:
        checksum = payload.pop("_sha256")
        if (not isinstance(checksum, str) or len(checksum) != 64
                or any(c not in "0123456789abcdef" for c in checksum)):
            raise ValueError("checksum _sha256 tidak sah")
        if not hmac.compare_digest(
                checksum, hashlib.sha256(_kanonik(payload)).hexdigest()):
            raise ValueError("checksum _sha256 tidak cocok; state berkas rusak")
    return payload


def _bawaan_snapshot() -> Dict[str, Any]:
    # Lazy: helper persistensi tetap dapat diimpor tanpa memuat mesin inti.
    from pycos.inti.naluri import DEFAULTS, LEXICON, TAG_LEXICON
    return {"params": DEFAULTS, "lexicon": LEXICON, "tag_lexicon": TAG_LEXICON}


def _id_bawaan(base: Dict[str, Any]) -> str:
    return hashlib.sha256(_kanonik({"nilai": base, "urutan": list(base)})).hexdigest()


def profil_snapshot(data: Dict[str, Any], profil: str = "penuh") -> Dict[str, Any]:
    """Profil konservatif; jangan buang pasangan kalibrasi atau memori perilaku."""
    from copy import deepcopy
    if profil not in ("penuh", "simpan", "minimal"):
        raise ValueError("profil tidak dikenal: {!r}".format(profil))
    if profil == "penuh":
        return data
    hasil = deepcopy(data)
    for key in ("tick_history", "delta_log", "prediction_log"):
        hasil.pop(key, None)
    if profil == "minimal":
        hasil.pop("emosi_log", None)
        hasil.get("selisih_self", {}).pop("log", None)
    referensi = {}
    for key, base in _bawaan_snapshot().items():
        nilai = hasil[key]
        referensi[key] = {
            "id": _id_bawaan(base),
            "hapus": [k for k in base if k not in nilai],
        }
        hasil[key] = {k: v for k, v in nilai.items()
                      if k not in base or type(v) is not type(base[k]) or v != base[k]}
        urutan = [k for k in base if k in nilai] + [k for k in nilai if k not in base]
        if urutan != list(nilai):
            referensi[key]["urutan"] = list(nilai)
    hasil["referensi"] = referensi
    hasil["format"] = "naluri/4-" + profil
    return hasil


def perluas_snapshot(data: Dict[str, Any]) -> Dict[str, Any]:
    """Migrasi encoding referensi ke snapshot penuh; pemanggil menyediakan salinan."""
    from copy import deepcopy
    referensi = data.get("referensi")
    bases = _bawaan_snapshot()
    if not isinstance(referensi, dict) or set(referensi) != set(bases):
        raise ValueError("referensi snapshot tidak lengkap")
    for key, base in bases.items():
        ref = referensi[key]
        if not isinstance(ref, dict) or ref.get("id") != _id_bawaan(base):
            raise ValueError("referensi[{}].id tidak cocok dengan bawaan runtime".format(key))
        hapus = ref.get("hapus")
        diff = data.get(key)
        if (not isinstance(hapus, list) or any(not isinstance(k, str) or k not in base for k in hapus)
                or not isinstance(diff, dict)):
            raise ValueError("referensi[{}] atau diff tidak sah".format(key))
        nilai = deepcopy(base)
        for k in hapus:
            nilai.pop(k, None)
        nilai.update(diff)
        if "urutan" in ref:
            urutan = ref["urutan"]
            if (not isinstance(urutan, list) or any(not isinstance(k, str) for k in urutan)
                    or len(urutan) != len(nilai) or set(urutan) != set(nilai)):
                raise ValueError("referensi[{}].urutan tidak sah".format(key))
            nilai = {k: nilai[k] for k in urutan}
        data[key] = nilai
    data.pop("referensi")
    data["format"] = "naluri/4"
    return data
