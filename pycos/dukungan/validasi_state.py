# -*- coding: utf-8 -*-
"""Gerbang state tersimpan: validasi tanpa memperbaiki data rusak diam-diam.

Nilai waktu sentinel (mis. last_ignition_tick=-10000) tetap sah; jam utama
harus non-negatif. Field opsional lama boleh hilang, tetapi field yang hadir
harus mengikuti domainnya. Tidak mengimpor kelas pemilik state.
"""
from __future__ import annotations

from copy import deepcopy
from collections.abc import Mapping
from typing import Any, Callable, Dict, List, Tuple, cast

from pycos.kontrak import DRIVE_KEYS, angka


FORMAT_TERBARU = {
    "Naluri": "naluri/4", "KawananNPC": "kawanan/5", "Nurani": "nurani/2",
    "JejakPrediksi": "jejak/2", "Kesadaran": "kesadaran/1",
    "Presentasi": "presentasi/1", "Ritual": "ritual/1", "Reputasi": "reputasi/2",
    "GrafAsosiasi": "graf_asosiasi/2",
}


def _naluri_3_ke_4(data: Dict[str, Any]) -> Dict[str, Any]:
    # v3 belum memisahkan jam subjektif; gunakan jam objektif sebagai titik
    # awal. Field lain yang kompatibel dipertahankan, bukan dibuang.
    data.setdefault("subjective_tick_count", data.get("tick_count", 0))
    data["format"] = "naluri/4"
    return data


def _perluas_profil(data: Dict[str, Any]) -> Dict[str, Any]:
    from pycos.dukungan.persistensi import perluas_snapshot
    return perluas_snapshot(data)


MIGRASI = {
    ("naluri/3", "naluri/4"): _naluri_3_ke_4,
    ("naluri/4-simpan", "naluri/4"): _perluas_profil,
    ("naluri/4-minimal", "naluri/4"): _perluas_profil,
}


def migrasi(data: Any, tujuan: str) -> Dict[str, Any]:
    """Migrasi salinan input; tanpa format adalah snapshot legacy parsial."""
    if not isinstance(data, Mapping):
        raise ValueError("state harus mapping")
    hasil = deepcopy(dict(data))

    def ubah(item: Any, target: str, path: str) -> None:
        asal = item.get("format")
        if (target == "naluri/4" and "referensi" in item
                and asal not in ("naluri/4-simpan", "naluri/4-minimal")):
            raise ValueError(path + ".format tidak sesuai encoding referensi")
        if asal is None and "format" not in item:
            item["format"] = target
        elif not isinstance(asal, str):
            raise ValueError("{}.format tidak sah: {!r}".format(path, asal))
        elif asal != target:
            antrian: List[Tuple[str, List[Tuple[str, Callable[..., Any]]]]] = [(asal, [])]
            dilihat = {asal}
            rute = None
            while antrian:
                versi, langkah = antrian.pop(0)
                if versi == target:
                    rute = langkah
                    break
                for (dari, ke), fn in MIGRASI.items():
                    if dari == versi and ke not in dilihat:
                        dilihat.add(ke)
                        antrian.append((ke, langkah + [(ke, fn)]))
            if rute is None:
                raise ValueError("{}.format tidak didukung: {!r}; perlu {}".format(
                    path, asal, target))
            for versi, fn in rute:
                item.update(fn(item))
                if item.get("format") != versi:
                    raise ValueError("migrasi {} tidak menghasilkan format tujuan".format(versi))
        for key, value in item.items():
            telusuri(value, "{}.{}".format(path, key))

    def telusuri(item: Any, path: str) -> None:
        if isinstance(item, dict):
            fmt = item.get("format")
            keluarga = fmt.split("/")[0] if isinstance(fmt, str) else None
            target = next((f for f in FORMAT_TERBARU.values()
                           if f.split("/")[0] == keluarga), None)
            if target:
                ubah(item, target, path)
            else:
                for key, value in item.items():
                    telusuri(value, "{}.{}".format(path, key))
        elif isinstance(item, (list, tuple)):
            for index, value in enumerate(item):
                telusuri(value, "{}[{}]".format(path, index))

    ubah(hasil, tujuan, tujuan.split("/")[0])
    return hasil


def tick_maju(x: Any, nama: str) -> int:
    """Jam/counter diskret non-negatif; bool dan pecahan ditolak."""
    if isinstance(x, bool) or not isinstance(x, int) or x < 0:
        raise ValueError("{} harus integer non-negatif".format(nama))
    return cast(int, x)


def urgensi(x: Any, nama: str) -> float:
    """Domain urgensi drive yang sama dengan hasil fisika Naluri."""
    return angka(x, nama, 0.0, 2.5)


def validasi_state(data: Any, nama: str) -> Dict[str, Any]:
    """Periksa seluruh tree sebelum loader dapat memutasi objek atau fallback."""
    if data is None:
        data = {}  # kompatibilitas pemanggil lama
    if not isinstance(data, Mapping):
        raise ValueError("{} harus mapping".format(nama))

    data = migrasi(data, FORMAT_TERBARU[nama])

    def periksa(item: Any, path: str) -> None:
        if isinstance(item, Mapping):
            for key, value in item.items():
                field = "{}.{}".format(path, key)
                if key == "urgency" and not isinstance(value, Mapping) and path != nama:
                    angka(value, field, 0.0)
                elif key in ("levels", "urgency"):
                    if not isinstance(value, Mapping):
                        raise ValueError("{} harus mapping".format(field))
                    for drive, number in value.items():
                        if drive not in DRIVE_KEYS:
                            raise ValueError("{}[{}]: drive tidak dikenal".format(field, drive))
                        label = "{}[{}]".format(field, drive)
                        if key == "levels":
                            angka(number, label, -1.0, 1.0)
                        else:
                            urgensi(number, label)
                elif key in ("tick_count", "clock"):
                    tick_maju(value, field)
                elif key == "subjective_tick_count":
                    angka(value, field, 0.0)
                periksa(value, field)
        elif isinstance(item, (list, tuple)):
            for index, value in enumerate(item):
                periksa(value, "{}[{}]".format(path, index))
        elif isinstance(item, float):
            angka(item, path)  # NaN/inf di snapshot bukan state sah

    periksa(data, nama)
    return dict(data)
