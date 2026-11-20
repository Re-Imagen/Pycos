"""Profil snapshot: wrapper terakhir serialisasi inti."""
from __future__ import annotations
from typing import Any, Dict
from pycos.dukungan.patching import wrap_method

def _naluri_profil_snapshot(original, self, profil: str = "penuh") -> Dict[str, Any]:
    from pycos.dukungan.persistensi import profil_snapshot
    if profil not in ("penuh", "simpan", "minimal"):
        raise ValueError("profil tidak dikenal: {!r}".format(profil))
    return profil_snapshot(original(self), profil)

def pasang(Naluri: type) -> None:
    """Pasang profil snapshot setelah semua ekstensi serialisasi lainnya."""
    wrap_method(Naluri, "to_dict", _naluri_profil_snapshot,
                patch_id="naluri.persistensi.profil")
