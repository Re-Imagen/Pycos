# -*- coding: utf-8 -*-
"""pycos.inti — lapisan NALURI: motivasi, state inti, persona, dan kawanan NPC.

Berkas utama: :mod:`pycos.inti.naluri` (enam drive, afek, tujuan, atensi,
workspace, narasi diri, presentasi, reputasi, `KawananNPC`). Ekstensi dari
subpaket lain (refleksi, memori, mandiri, bahasa) menempel melalui
`pycos.dukungan.patching`, sehingga subpaket ini tetap termuat sendirian
tanpa lapisan opsional.

Impor nama publik dilakukan saat pertama diakses (`python -m
pycos.inti.naluri` karena itu tidak memuat modul dua kali).
"""
from __future__ import annotations

from importlib import import_module
from typing import TYPE_CHECKING, Any, Dict, List

# Nama publik -> submodul tempat namanya didefinisikan.
_SUBMODUL: Dict[str, str] = {
    "DRIVES": "naluri",
    "Goal": "naluri",
    "KawananNPC": "naluri",
    "Keadaan": "persona",
    "Kesadaran": "naluri",
    "Mood": "naluri",
    "Naluri": "naluri",
    "PERSONA_CONTOH": "persona",
    "Persona": "persona",
    "Presentasi": "naluri",
    "Reputasi": "naluri",
    "Ritual": "naluri",
    "buat_npc": "naluri",
}

__all__: List[str] = sorted(_SUBMODUL)

if TYPE_CHECKING:  # hanya untuk pemeriksa jenis, tidak dieksekusi
    from .naluri import (DRIVES, Goal, KawananNPC, Kesadaran, Mood, Naluri,
                         Presentasi, Reputasi, Ritual, buat_npc)
    from .persona import Keadaan, PERSONA_CONTOH, Persona


def __getattr__(nama: str) -> Any:
    """Muat submodul hanya saat namanya pertama diakses (PEP 562)."""
    asal = _SUBMODUL.get(nama)
    if asal is None:
        raise AttributeError(
            "paket {!r} tidak punya atribut {!r}".format(__name__, nama))
    nilai = getattr(import_module("{}.{}".format(__name__, asal)), nama)
    globals()[nama] = nilai          # cache: resolusi sekali per proses
    return nilai


def __dir__() -> List[str]:
    return sorted(set(globals()) | set(_SUBMODUL))
