# -*- coding: utf-8 -*-
"""Suplemen impak terkompilasi dan pemeriksa cakupan (heuristik, bukan sentimen gold)."""
from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from functools import lru_cache
from typing import Any, Dict, List, Optional

from pycos.dukungan.sumber import jalur_leksikon
from pycos.kontrak import DRIVE_KEYS, angka


def validasi_entri(data: Any, label: str) -> None:
    if not isinstance(data, dict):
        raise ValueError(label + " harus mapping")
    for kata, vector in data.items():
        if not isinstance(kata, str) or not kata.strip() or kata != kata.strip():
            raise ValueError(label + ": lema harus teks non-kosong tanpa spasi tepi")
        if not isinstance(vector, dict) or not vector:
            raise ValueError(label + "[{}] harus vektor non-kosong".format(kata))
        for drive, value in vector.items():
            if drive not in DRIVE_KEYS:
                raise ValueError(label + "[{}]: drive tidak dikenal: {}".format(kata, drive))
            angka(value, label + "[{}][{}]".format(kata, drive), -1, 1)
        if not any(vector.values()):
            raise ValueError(label + "[{}] tidak boleh seluruhnya nol".format(kata))


@lru_cache(maxsize=1)
def _dokumen() -> Dict[str, Any]:
    with open(jalur_leksikon("impak_tambahan.json"), encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict) or data.get("format") != "impak/1":
        raise ValueError("format suplemen impak tidak didukung")
    for lang in ("id", "en"):
        validasi_entri(data["entri"][lang], "suplemen." + lang)
    return data


def perluas(id_words: Dict[str, Any], en_words: Dict[str, Any]) -> None:
    """Tambahkan lema baru, tanpa menimpa satu pun bobot/lema legacy."""
    for lang, target in (("id", id_words), ("en", en_words)):
        for kata, vector in _dokumen()["entri"][lang].items():
            target.setdefault(kata, deepcopy(vector))


def periksa() -> Dict[str, Any]:
    from pycos.inti.naluri import LEXICON, LEXICON_EN, TAG_LEXICON, TAG_LEXICON_EN
    doc = _dokumen()
    with open(jalur_leksikon(), "rb") as f:
        raw = f.read()
    if hashlib.sha256(raw).hexdigest() != doc["sumber_sha256"]:
        raise ValueError("sumber leksikon berubah; suplemen impak perlu ditinjau/dibangun ulang")
    # Bangun ulang dari provenance agar entri terkompilasi tidak menjadi angka
    # cakupan yang tidak dapat ditelusuri.
    expected: Dict[str, Any] = {"id": {}, "en": {}}
    for group in doc["kelompok"]:
        vector = {group["drive"]: group["nilai"]}
        for lang in expected:
            for kata in group[lang]:
                expected[lang].setdefault(kata, dict(vector))
    for entri in json.loads(raw)["leksikon"]:
        lang = entri["bahasa"]
        if lang in expected:
            for tipe in entri.get("tipe_semantik", []):
                if tipe in doc["aturan_tipe"]:
                    expected[lang].setdefault(entri["lema"], dict(doc["aturan_tipe"][tipe]))
                    break
    if expected != doc["entri"]:
        raise ValueError("entri suplemen tidak sesuai provenance kelompok/aturan tipe")
    for label, words in (("id", LEXICON), ("en", LEXICON_EN),
                         ("tag_id", TAG_LEXICON), ("tag_en", TAG_LEXICON_EN)):
        validasi_entri(words, label)
    # C1: tolak konflik tanda antara leksikon utama dan daftar ciri.
    # LeksikonCiri positif/negatif tidak boleh berlawanan valensi lema
    # yang sama di leksikon utama.
    from pycos.bahasa.tutur import LEKSIKON_CIRI_BAWAAN
    # polisem-aware: kumpulkan SEMUA valensi per lema; konflik hanya bila
    # seluruh makna berlawanan dengan daftar ciri.
    peta_valensi: Dict[str, list] = {}
    for e in json.loads(raw)["leksikon"]:
        if e.get("bahasa") == "id":
            peta_valensi.setdefault(str(e.get("lema", "")).lower(),
                                    []).append(float(e.get("valensi", 0) or 0))
    for kata in LEKSIKON_CIRI_BAWAAN.positif:
        valensi = peta_valensi.get(str(kata).lower())
        if valensi is not None and all(v < 0 for v in valensi):
            raise ValueError(
                "konflik tanda: '{}' positif di daftar ciri, "
                "tetapi semua valensi {} di leksikon".format(kata, valensi))
    for kata in LEKSIKON_CIRI_BAWAAN.negatif:
        valensi = peta_valensi.get(str(kata).lower())
        if valensi is not None and all(v > 0 for v in valensi):
            raise ValueError(
                "konflik tanda: '{}' negatif di daftar ciri, "
                "tetapi valensi {} di leksikon".format(kata, valensi))
    id_single = sum(" " not in k for k in LEXICON)
    en_single = sum(" " not in k for k in LEXICON_EN)
    if id_single < 400 or en_single < 200:
        raise ValueError("cakupan impak di bawah target 400 ID / 200 EN")
    return {"ok": True, "id": len(LEXICON), "en": len(LEXICON_EN),
            "id_kata_tunggal": id_single, "en_kata_tunggal": en_single,
            "tag_id": len(TAG_LEXICON), "tag_en": len(TAG_LEXICON_EN),
            "suplemen_id": len(doc["entri"]["id"]), "suplemen_en": len(doc["entri"]["en"]),
            "metode": "heuristik kurasi kelompok dan tipe semantik; bukan validasi sentimen"}


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--periksa", action="store_true", required=True)
    parser.parse_args(argv)
    try:
        hasil = periksa()
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(json.dumps({"ok": False, "galat": str(exc)}, ensure_ascii=False))
        return 1
    print(json.dumps(hasil, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
