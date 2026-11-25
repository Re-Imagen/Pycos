# -*- coding: utf-8 -*-
"""pycos/bahasa/keadaan.py — ujaran keadaan yang DIBANGKITKAN, bukan templat.

H8 (ANALISIS_LINGUISTIK): tabel watak pelindung (`_PELINDUNG_WATAK`), kalimat
penahanan sadar, kalimat apersepsi, dan balasan ujian sebelumnya berupa 3–5
kalimat tetap per kasus. Akibatnya dua NPC dengan keadaan berbeda dapat
mengucapkan kalimat yang sama persis, dan kalimatnya tidak pernah memakai isi
yang benar-benar ada di kepala NPC.

Modul ini tidak menggantikan pemilihan isi: ia hanya menyediakan *act khusus*
(`kegagalan`, `penahanan`, `apersepsi`, `ujian_tutur`) yang diteruskan ke
mesin tutur yang sama (L0–L3). Bila mesin tutur tidak tersedia, `realisasi`
mengembalikan string kosong dan pemanggil memakai jalur lamanya.

Murni stdlib; mengimpor :mod:`pycos.bahasa.tutur` hanya saat dipanggil agar
`import pycos` tetap malas.
"""
from __future__ import annotations

from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

__all__ = [
    "ACT_KEADAAN", "KOSAKATA_KEADAAN", "GAGAL",
    "konteks_keadaan", "realisasi", "realisasi_daftar",
]

#: Act khusus keadaan. Semuanya di luar `_ACT_FUNGSI` Presentasi: aktor di
#: sini bukan percakapan biasa, melainkan keadaan internal yang menekan tutur.
ACT_KEADAAN: Tuple[str, ...] = ("kegagalan", "penahanan", "apersepsi",
                                "ujian_tutur")

#: Keadaan → (act, mode gramatikal). ``ragu`` meminta proposisi, ``diam``
#: berarti "tidak ada yang perlu dikatakan" (dibiarkan ke pemanggil).
KOSAKATA_KEADAAN: Dict[str, Tuple[str, str]] = {
    "ragu": ("ragu", "proposisi"),
    "diam": ("menyatakan", "sunyi"),
    "waspada": ("waspada", "kecurigaan"),
    "bertanya": ("bertanya", "pertanyaan"),
    "mengamati": ("mengamati", "pengamatan"),
    "menyatakan": ("menyatakan", "pernyataan"),
    "menolak": ("menolak", "penolakan"),
    "akrab": ("akrab", "keakraban"),
    "menantang": ("menantang", "tantangan"),
    "mengenang": ("mengenang", "ingatan"),
}

#: Nama watak untuk jejak; bukan daftar kalimat.
GAGAL = "gagal"


def konteks_keadaan(act: str, keadaan: str = "", topik: str = "",
                    isi: Sequence[str] = (), motif: str = "",
                    **lain: Any) -> Any:
    """Bangun ``GenContext`` untuk act keadaan (duck-typed, tanpa impor keras).

    ``isi`` adalah kata/isi yang benar-benar ada di kepala NPC (lihat
    :func:`pycos.bahasa.teks.kata_isi`); ia masuk sebagai ``spotlight`` dan
    ``inner`` sehingga mesin tutur memilih lema dari isi itu, bukan dari
    templat. Nilai tambahan (mis. ``doubt``, ``valensi``) diteruskan apa
    adanya bila bidangnya dikenal `GenContext`.
    """
    from pycos.bahasa.tutur import GenContext

    kata = [str(x).strip() for x in (isi or ()) if str(x).strip()][:3]
    bidang = {
        "act": str(act or "menyatakan"),
        "register": "netral",
        "topik": str(topik or (kata[0] if kata else "")),
        "spotlight": tuple(kata),
        "inner": str(motif or ""),
        "niat": str(motif or ""),
        "emosi": tuple(),
        "doubt": 0.6 if keadaan == "ragu" else 0.3,
    }
    dikenal = set(getattr(GenContext, "__dataclass_fields__", {}) or {})
    for k, v in lain.items():
        if k in dikenal:
            bidang[k] = v
    return GenContext(**bidang)


def realisasi(act: str, engine: Any = None, keadaan: str = "",
              topik: str = "", isi: Sequence[str] = (), motif: str = "",
              seed: int = 0, **lain: Any) -> str:
    """Satu ujaran keadaan dari mesin tutur; "" bila mesin tidak tersedia.

    Pemanggil (pelindung/organik) yang memutuskan KAPAN gagal; modul ini
    tidak mengambil alih pemilihan tujuan. Bila mesin menyerah, hasil kosong
    dikembalikan dan pemanggil jatuh ke jalur lamanya.
    """
    if engine is None:
        return ""
    try:
        if not bool(getattr(engine, "tersedia", lambda: False)()):
            return ""
        ctx = konteks_keadaan(act, keadaan=keadaan, topik=topik, isi=isi,
                              motif=motif, seed=int(seed), **lain)
        hasil = engine.ucap(ctx)
    except Exception:                     # mesin tutur tidak wajib ada
        return ""
    teks = str(getattr(hasil, "teks", "") or "").strip() if hasil else ""
    if not teks:
        return ""
    return teks


def realisasi_daftar(act: str, jumlah: int, engine: Any = None,
                     keadaan: str = "", topik: str = "",
                     isi: Sequence[str] = (), motif: str = "",
                     seed: int = 0, **lain: Any) -> List[str]:
    """Beberapa kandidat berbeda (seed bergeser) untuk satu act keadaan."""
    keluar: List[str] = []
    for i in range(max(0, int(jumlah))):
        teks = realisasi(act, engine=engine, keadaan=keadaan, topik=topik,
                         isi=isi, motif=motif, seed=int(seed) + 7919 * i,
                         **lain)
        if teks and teks not in keluar:
            keluar.append(teks)
    return keluar
