# -*- coding: utf-8 -*-
"""pycos/inti/persona.py — profil persona dan ringkasan keadaan batin.

Data murni untuk penilaian keselarasan ujaran: `Persona` (sifat, register,
kata pantangan) dan `Keadaan` (valensi, gairah, ketidakpastian). Keduanya
dahulu berada di `pycos.inti.naluri`; diekstraksi ke modul ringan ini agar
konsumen yang hanya butuh kelas data (CLI `python -m pycos --teks`, penilai
di `pycos.refleksi.nurani`) tidak memuat mesin `Naluri` yang besar.

Kelas yang sama tetap dapat diimpor dari `pycos.inti.naluri` (re-export
kompatibilitas), sehingga kode lama tidak putus.

Murni stdlib + validator batas `pycos.kontrak`; tidak mengimpor modul inti
lain, jadi aman dimuat dari lapisan mana pun tanpa lingkaran impor.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Mapping, Optional, Tuple

from pycos.kontrak import angka, hanya_kunci, teks_wajib
from pycos.dukungan.numerik import float_hingga, jepit

__all__ = [
    "Keadaan", "Persona", "PERSONA_CONTOH",
    "SIFAT_DIKENAL", "REGISTER_DIKENAL", "normalisasi_frasa",
]


# ---------------------------------------------------------------------------
# Keadaan batin ringkas & profil persona (dulu subsistem pycos.selaras)
# ---------------------------------------------------------------------------
def _jepit(x: float, lo: float, hi: float) -> float:
    """Jepit ke [lo, hi]; NaN dan inf ditolak agar tidak tersamar sebagai batas."""
    if isinstance(x, bool) or not isinstance(x, (int, float)):
        raise ValueError("nilai keadaan harus angka, dapat {!r}".format(x))
    v = float_hingga(x, "nilai keadaan")
    return jepit(v, lo, hi)


_KUNCI_KEADAAN = ("valensi", "gairah", "ketidakpastian")


@dataclass(frozen=True)
class Keadaan:
    """Ringkasan keadaan batin yang akan diselaraskan dengan ujaran.

    Tiga angka yang dapat dibaca dari sistem mana pun:

    * ``valensi``        — [-1, 1]: negatif (tidak enak) ... positif (enak);
    * ``gairah``         — [0, 1]: tenang ... bergairah;
    * ``ketidakpastian`` — [0, 1]: yakin ... ragu.

    `dari_mood` menerima objek apa pun yang punya atribut `valence` dan
    `arousal` (duck typing; mis. `Mood` di `pycos.inti.naluri`), sehingga host
    dapat memetakan keadaan dari sistem mana pun tanpa ketergantungan kode.
    """

    valensi: float = 0.0
    gairah: float = 0.5
    ketidakpastian: float = 0.3

    def __post_init__(self) -> None:
        object.__setattr__(self, "valensi", angka(self.valensi, "valensi", -1.0, 1.0))
        object.__setattr__(self, "gairah", angka(self.gairah, "gairah", 0.0, 1.0))
        object.__setattr__(self, "ketidakpastian",
                           angka(self.ketidakpastian, "ketidakpastian", 0.0, 1.0))

    @classmethod
    def dari_mood(cls, mood: Any, ketidakpastian: float = 0.3) -> "Keadaan":
        """Bentuk `Keadaan` dari objek ber-atribut `valence` dan `arousal`.

        Nilai dijepit ke rentang (arousal yang berada di [-1, 1] dipetakan ke
        [0, 1]). Atribut yang hilang melempar `AttributeError`, bukan dianggap 0.
        """
        valensi = _jepit(getattr(mood, "valence"), -1.0, 1.0)
        arousal = getattr(mood, "arousal")
        gairah = _jepit(arousal, 0.0, 1.0) if arousal >= 0 else _jepit(
            (float(arousal) + 1.0) / 2.0, 0.0, 1.0)
        return cls(valensi=valensi, gairah=gairah, ketidakpastian=ketidakpastian)

    def to_dict(self) -> Dict[str, float]:
        return {"valensi": self.valensi, "gairah": self.gairah,
                "ketidakpastian": self.ketidakpastian}

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "Keadaan":
        hanya_kunci(dict(data), _KUNCI_KEADAAN, "data keadaan")
        return cls(**dict(data))


SIFAT_DIKENAL: Tuple[str, ...] = ("ekspresif", "ragu", "hangat")
REGISTER_DIKENAL: Tuple[str, ...] = ("formal", "santai", "netral")
_KUNCI_PERSONA: Tuple[str, ...] = ("nama", "sifat", "register", "pantangan")


def normalisasi_frasa(frasa: str) -> str:
    """Huruf kecil dan spasi tunggal; dipakai untuk membandingkan frasa."""
    return " ".join(frasa.lower().split())


@dataclass(frozen=True)
class Persona:
    """Profil persona: sifat, register, dan kata pantangan.

    `Persona` adalah data murni. Sifat dinyatakan sebagai angka dalam [0, 1]:

    * ``hangat``    — 0 dingin ... 1 hangat (memengaruhi target valensi);
    * ``ekspresif`` — 0 datar ... 1 ekspresif (memengaruhi target gairah);
    * ``ragu``      — 0 yakin ... 1 ragu-ragu (memengaruhi target keraguan).

    Register: ``formal`` (saya/anda), ``santai`` (aku/kamu), atau ``netral``
    (register tidak dinilai). Kata pantangan adalah kata atau frasa yang tidak
    boleh muncul dalam tutur persona ini.
    """

    nama: str
    sifat: Mapping[str, float] = field(default_factory=dict)
    register: str = "netral"
    pantangan: Tuple[str, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "nama", teks_wajib(self.nama, "nama"))
        sifat: Dict[str, float] = {}
        for kunci, nilai in dict(self.sifat).items():
            if kunci not in SIFAT_DIKENAL:
                raise ValueError("sifat {!r} tidak dikenal; sifat sah: {}".format(
                    kunci, ", ".join(SIFAT_DIKENAL)))
            sifat[kunci] = angka(nilai, "sifat[{}]".format(kunci), 0.0, 1.0)
        object.__setattr__(self, "sifat", sifat)
        if self.register not in REGISTER_DIKENAL:
            raise ValueError("register {!r} tidak dikenal; pilihan: {}".format(
                self.register, ", ".join(REGISTER_DIKENAL)))
        if isinstance(self.pantangan, str):
            raise ValueError("pantangan harus daftar string, bukan satu string")
        daftar = tuple(normalisasi_frasa(teks_wajib(p, "pantangan"))
                       for p in self.pantangan)
        object.__setattr__(self, "pantangan", tuple(dict.fromkeys(daftar)))

    def sifat_of(self, kunci: str) -> Optional[float]:
        """Nilai sifat bila ditetapkan, selain itu None (tidak ada preferensi)."""
        return self.sifat.get(kunci)

    def to_dict(self) -> Dict[str, Any]:
        return {"nama": self.nama, "sifat": dict(self.sifat),
                "register": self.register, "pantangan": list(self.pantangan)}

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "Persona":
        hanya_kunci(dict(data), _KUNCI_PERSONA, "data persona")
        if "nama" not in data:
            raise ValueError("data persona wajib memuat 'nama'")
        return cls(nama=data["nama"], sifat=dict(data.get("sifat", {})),
                   register=data.get("register", "netral"),
                   pantangan=data.get("pantangan", ()))


PERSONA_CONTOH = Persona(
    nama="Rani",
    sifat={"hangat": 0.8, "ekspresif": 0.6, "ragu": 0.3},
    register="santai",
    pantangan=("sialan", "bodoh"),
)
