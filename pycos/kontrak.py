# -*- coding: utf-8 -*-
"""Kontrak arsitektur Pycos: janji, kebutuhan, dan boundary operasi.

Berkas ini sengaja berada di luar modul yang dikontrak. Deklarasi ``JANJI``
dan ``KEBUTUHAN`` adalah data statis; pemeriksaan kontrak tidak menyimpan
hasil, tidak mengubah objek yang diperiksa, dan tidak memutuskan kebijakan
host. Tiap pelanggaran memuat ``apa``, ``pelanggar``, dan ``dirugikan``.

Level verifikasi:

* 0: tidak menjalankan pemeriksaan;
* 1: precondition operasi (keberadaan field dan tipe kasar);
* 2: precondition + postcondition operasi;
* 3: level 2 + pemeriksaan kecil lintas-lapisan.

``kontrak_operasi`` dan ``verifikasi_startup`` mengembalikan ``None`` bila
lolos, atau satu dict pelanggaran. Bila banyak syarat gagal, seluruh
pelanggaran daun dikumpulkan di ``dict['pelanggaran']``. Fungsi-fungsi ini
hanya melaporkan; host boleh menolak, mencatat, atau mengabaikan hasilnya.

Modul ini juga memuat **pemeriksaan argumen batas** (:func:`angka`,
:func:`teks_wajib`, :func:`hanya_kunci`) untuk parameter publik yang wajib
ditolak di tempatnya bila tidak sah. Berbeda dengan validator kontrak di
atas, ketiganya melempar ``ValueError`` bernama argumen: bool ditolak sebagai
angka, string angka ditolak, dan nilai non-finite ditolak. Aturan angka
berhingga disatukan lewat ``pycos.dukungan.numerik.float_hingga``.
"""
from __future__ import annotations

import math
import numbers
from collections.abc import Iterable, Mapping, Sequence
from itertools import islice
from typing import Any, Callable, Dict, List, Optional, Tuple, TypedDict

from pycos.dukungan.numerik import float_hingga

__all__ = [
    "DRIVE_KEYS", "JANJI", "KEBUTUHAN", "LEVEL_TANPA_VERIFIKASI",
    "LEVEL_PRECONDITION", "LEVEL_OPERASI", "LEVEL_LINTAS_LAPIS",
    "KEBIJAKAN_TOLAK", "KEBIJAKAN_CATAT", "KEBIJAKAN_ABAIKAN",
    "ContractViolationError", "kontrak_operasi", "verifikasi_startup",
    "check_operation", "verify_startup",
    "angka", "teks_wajib", "hanya_kunci",
]

# Alias kanonik lintas lapisan; verifikasi runtime Level 1+ tetap
# memeriksa kunci sebenarnya pada tiap NPC.
from pycos.dukungan import konstanta as _konstanta_drive
DRIVE_KEYS = _konstanta_drive.DRIVES

LEVEL_TANPA_VERIFIKASI = 0
LEVEL_PRECONDITION = 1
LEVEL_OPERASI = 2
LEVEL_LINTAS_LAPIS = 3

KEBIJAKAN_TOLAK = "reject"
KEBIJAKAN_CATAT = "log"
KEBIJAKAN_ABAIKAN = "ignore"

# Skema field sengaja sederhana: shape, tipe kunci/nilai, kunci yang
# dijamin, dan rentang nilai bila relevan. Tidak ada validator yang berjalan
# otomatis di dalam modul pemilik field.
JANJI: Dict[str, Dict[str, Any]] = {
    "Naluri": {
        "fields": {
            "name": {"shape": "str", "when": "setelah konstruksi"},
            "levels": {
                "shape": "mapping", "key_type": "str",
                "value_type": "float", "keys": DRIVE_KEYS,
                "range": (-1.0, 1.0), "when": "setelah konstruksi",
            },
            "tick_count": {"shape": "int", "range": (0.0, None)},
            "nurani": {"shape": "optional-object"},
            "kesadaran": {"shape": "object"},
        },
        "operations": {
            "tick": {"callable": True, "returns": "None",
                     "phases": ("masuk", "keluar")},
            "choose_action": {"callable": True, "returns": "mapping",
                              "phases": ("masuk", "keluar")},
            "reward_for": {"callable": True, "returns": "float",
                           "phases": ("masuk", "keluar")},
        },
    },
    "Nurani": {
        "fields": {
            "drives": {"shape": "sequence[str]", "keys": DRIVE_KEYS},
            "_affective": {"shape": "mapping", "key_type": "int",
                            "value_type": "mapping"},
            "_other_beliefs": {"shape": "mapping", "key_type": "str",
                                "value_type": "mapping"},
            "doubt_level": {"shape": "float", "range": (0.0, 1.0)},
        },
        "operations": {
            "experience": {"callable": True, "returns": "bool"},
            "metacognitive_doubt": {"callable": True, "returns": "float"},
        },
    },
    "JejakPrediksi": {
        "fields": {
            "naluri": {"shape": "optional-object"},
            "_episodes": {"shape": "sequence[mapping]"},
            "_token_index": {"shape": "mapping", "value_type": "set[int]"},
            "_ep_by_id": {"shape": "mapping", "value_type": "mapping"},
        },
        "operations": {
            "record_experience": {"callable": True, "returns": "int",
                                  "phases": ("masuk", "keluar")},
            "predict": {"callable": True, "returns": "mapping",
                        "phases": ("masuk", "keluar")},
            "reinforce": {"callable": True, "returns": "mapping",
                          "phases": ("masuk", "keluar")},
        },
    },
    "ModelKausal": {
        "fields": {
            "tepi": {"shape": "mapping", "key_type": "tuple[str,str]",
                     "value_type": "mapping"},
            "masuk": {"shape": "mapping", "value_type": "mapping"},
            "keluar": {"shape": "mapping", "value_type": "mapping"},
        },
    },
    "Kesadaran": {
        "fields": {
            "naluri": {"shape": "object"},
            "spotlight": {"shape": "sequence[mapping]", "max_items": 3},
        },
    },
    "Presentasi": {
        "fields": {"naluri": {"shape": "object"}},
        "operations": {
            "ucap": {"callable": True, "returns": "mapping",
                     "phases": ("masuk", "keluar")},
        },
    },
    "Lingkungan": {
        "fields": {"badan": {"shape": "mapping"}},
        "operations": {
            "langkah": {"callable": True, "returns": "mapping",
                        "phases": ("masuk", "keluar")},
        },
    },
    "Ketidaktahuan": {
        "fields": {},
        "operations": {
            "batas_pengetahuan": {"callable": True, "returns": "mapping",
                                  "pure": True},
            "sikap_ketidaktahuan": {"callable": True, "returns": "str",
                                    "pure": True},
        },
    },
    "Persona": {
        "fields": {
            "nama": {"shape": "str", "when": "setelah konstruksi"},
            "sifat": {"shape": "mapping", "key_type": "str", "value_type": "float",
                      "range": (0.0, 1.0), "when": "setelah konstruksi"},
            "register": {"shape": "str", "when": "setelah konstruksi"},
            "pantangan": {"shape": "sequence[str]", "when": "setelah konstruksi"},
        },
        "operations": {
            "sifat_of": {"callable": True, "returns": "optional-float",
                         "pure": True},
            "to_dict": {"callable": True, "returns": "mapping", "pure": True},
        },
    },
    "Keadaan": {
        "fields": {
            "valensi": {"shape": "float", "range": (-1.0, 1.0),
                        "when": "setelah konstruksi"},
            "gairah": {"shape": "float", "range": (0.0, 1.0),
                       "when": "setelah konstruksi"},
            "ketidakpastian": {"shape": "float", "range": (0.0, 1.0),
                               "when": "setelah konstruksi"},
        },
        "operations": {
            "to_dict": {"callable": True, "returns": "mapping", "pure": True},
            "from_dict": {"callable": True, "returns": "object", "pure": True},
        },
    },
    "PelacakSelaras": {
        "fields": {
            "kapasitas": {"shape": "int", "range": (2.0, None),
                          "when": "setelah konstruksi"},
            "min_sampel": {"shape": "int", "range": (2.0, None),
                           "when": "setelah konstruksi"},
            "ambang_tren": {"shape": "float", "range": (0.0, None),
                            "when": "setelah konstruksi"},
        },
        "operations": {
            "catat": {"callable": True, "returns": "None",
                      "phases": ("masuk", "keluar")},
            "tren": {"callable": True, "returns": "mapping", "pure": True},
            "kosongkan": {"callable": True, "returns": "None"},
        },
    },
}

# Kebutuhan menyatakan apa yang benar-benar dipakai konsumen. `optional=True`
# berarti integrasi boleh tidak dipasang; jika penyedia ada, janji field dan
# operasinya tetap harus kompatibel.
KEBUTUHAN: Dict[str, Dict[str, Any]] = {
    "Lingkungan": {
        "dependencies": {
            "Naluri": {
                "optional": False,
                "fields": {
                    "levels": {
                        "shape": "mapping", "key_type": "str",
                        "value_type": "float", "keys": DRIVE_KEYS,
                        "range": (-1.0, 1.0),
                    },
                },
                "operations": {
                    "choose_action": {"callable": True, "optional": True},
                    "tick": {"callable": True, "optional": True},
                    "reward_for": {"callable": True, "optional": True},
                },
            },
            "JejakPrediksi": {
                "optional": True,
                "operations": {
                    "predict": {"callable": True, "optional": True},
                    "record_experience": {"callable": True, "optional": True},
                    "reinforce": {"callable": True, "optional": True},
                },
            },
        },
    },
    "Naluri": {
        "dependencies": {
            "Nurani": {
                "optional": True,
                "fields": {
                    "_affective": {"shape": "mapping", "key_type": "int",
                                    "value_type": "mapping"},
                    "_other_beliefs": {"shape": "mapping", "key_type": "str",
                                        "value_type": "mapping"},
                    "doubt_level": {"shape": "float", "range": (0.0, 1.0)},
                },
                "operations": {
                    "experience": {"callable": True, "optional": True},
                    "metacognitive_doubt": {"callable": True, "optional": True},
                },
            },
            "JejakPrediksi": {
                "optional": True,
                "operations": {
                    "record_experience": {"callable": True, "optional": True},
                    "predict": {"callable": True, "optional": True},
                },
            },
            "ModelKausal": {
                "optional": True,
                "fields": {"tepi": {"shape": "mapping", "value_type": "mapping"}},
            },
        },
    },
    "Presentasi": {
        "dependencies": {
            "Ketidaktahuan": {
                "optional": True,
                "operations": {
                    "batas_pengetahuan": {"callable": True},
                    "sikap_ketidaktahuan": {"callable": True},
                },
            },
        },
    },
    "Kesadaran": {
        "dependencies": {
            "Ketidaktahuan": {
                "optional": True,
                "operations": {
                    "batas_pengetahuan": {"callable": True},
                    "sikap_ketidaktahuan": {"callable": True},
                },
            },
        },
    },
    "Perencana": {
        "dependencies": {
            "Ketidaktahuan": {
                "optional": True,
                "operations": {
                    "batas_pengetahuan": {"callable": True},
                    "sikap_ketidaktahuan": {"callable": True},
                },
            },
            "ModelKausal": {
                "optional": True,
                "fields": {"tepi": {"shape": "mapping", "value_type": "mapping"}},
            },
        },
    },
    "Ketidaktahuan": {
        "dependencies": {
            "JejakPrediksi": {
                "optional": True,
                "fields": {
                    "_token_index": {"shape": "mapping", "value_type": "set[int]"},
                    "_ep_by_id": {"shape": "mapping", "value_type": "mapping"},
                },
            },
            "Nurani": {
                "optional": True,
                "fields": {
                    "_affective": {"shape": "mapping", "key_type": "int",
                                    "value_type": "mapping"},
                    "_other_beliefs": {"shape": "mapping", "key_type": "str",
                                        "value_type": "mapping"},
                },
            },
            "ModelKausal": {
                "optional": True,
                "fields": {"tepi": {"shape": "mapping", "value_type": "mapping"}},
            },
            "Kesadaran": {
                "optional": True,
                "fields": {"spotlight": {"shape": "sequence[mapping]"}},
            },
        },
    },
    "PenilaiSelaras": {
        "dependencies": {
            "Persona": {
                "optional": False,
                "fields": {
                    "nama": {"shape": "str"},
                    "sifat": {"shape": "mapping", "key_type": "str",
                              "value_type": "float", "range": (0.0, 1.0)},
                },
                "operations": {
                    "sifat_of": {"callable": True, "optional": True},
                },
            },
            "Keadaan": {
                "optional": False,
                "fields": {
                    "valensi": {"shape": "float", "range": (-1.0, 1.0)},
                    "gairah": {"shape": "float", "range": (0.0, 1.0)},
                    "ketidakpastian": {"shape": "float", "range": (0.0, 1.0)},
                },
            },
            "PelacakSelaras": {
                "optional": True,
                "operations": {
                    "catat": {"callable": True, "optional": True,
                              "phases": ("masuk", "keluar")},
                    "tren": {"callable": True, "optional": True},
                },
            },
        },
    },
}


class ContractViolationError(Exception):
    """Pengecualian kebijakan host untuk mode ``reject``.

    Validator tidak pernah mengangkat kelas ini. Host yang memilih kebijakan
    ``reject`` boleh mengangkatnya setelah menerima laporan pelanggaran.
    """

    def __init__(self, violation: Mapping[str, Any]):
        self.violation = dict(violation)
        super().__init__(str(self.violation.get("apa", "kontrak dilanggar")))


# ---------------------------------------------------------------------------
# Pemeriksaan argumen batas (dulu di pycos.selaras.validasi)
# ---------------------------------------------------------------------------
def angka(x: object, nama: str, lo: Optional[float] = None,
          hi: Optional[float] = None) -> float:
    """Pastikan ``x`` adalah bilangan real berhingga dalam ``[lo, hi]`` bila ada.

    Aturan sengaja ketat: ``bool`` ditolak sebagai angka, string angka
    ditolak, dan nilai non-finite ditolak (pesan disatukan lewat
    :func:`pycos.dukungan.numerik.float_hingga`). Nilai yang tidak sah
    menghasilkan ``ValueError`` dengan nama argumen, bukan diubah diam-diam.
    """
    if isinstance(x, bool) or not isinstance(x, numbers.Real):
        raise ValueError("{} harus angka, dapat {!r}".format(nama, x))
    v = float_hingga(x, nama)
    if lo is not None and v < lo:
        raise ValueError("{} = {} di bawah batas {}".format(nama, v, lo))
    if hi is not None and v > hi:
        raise ValueError("{} = {} di atas batas {}".format(nama, v, hi))
    return v


def teks_wajib(x: object, nama: str) -> str:
    """Pastikan ``x`` string yang tidak kosong setelah dipangkas spasi."""
    if not isinstance(x, str) or not x.strip():
        raise ValueError("{} harus string non-kosong, dapat {!r}".format(nama, x))
    return x.strip()


def hanya_kunci(data: object, sah: Tuple[str, ...], nama: str) -> None:
    """Tolak mapping yang memuat kunci di luar ``sah``."""
    if not isinstance(data, dict):
        raise ValueError("{} harus berupa dict, dapat {!r}".format(nama, type(data).__name__))
    asing = sorted(str(k) for k in data if k not in sah)
    if asing:
        raise ValueError("{} memuat kunci tak dikenal {}; kunci sah: {}".format(
            nama, asing, ", ".join(sah)))


def _field(obj: Any, nama: str, default: Any = None) -> Any:
    """Baca field tanpa memanggil properti/fungsi modul yang sedang diperiksa."""
    try:
        if isinstance(obj, Mapping):
            return obj.get(nama, default)
        d = object.__getattribute__(obj, "__dict__")
        if isinstance(d, dict):
            return d.get(nama, default)
    except Exception:
        pass
    return default


def _get(obj: Any, key: Any, default: Any = None) -> Any:
    try:
        return obj.get(key, default) if isinstance(obj, Mapping) else default
    except Exception:
        return default


def _label(value: Any, default: str = "objek") -> str:
    if isinstance(value, str):
        return value
    if value is None:
        return default
    if isinstance(value, (int, float, bool)):
        try:
            return str(value)
        except Exception:
            pass
    return type(value).__name__


def _pelanggaran(apa: str, pelanggar: str, dirugikan: str,
                 **detail: Any) -> Dict[str, Any]:
    hasil: Dict[str, Any] = {
        "apa": _label(apa, "pelanggaran"),
        "pelanggar": _label(pelanggar),
        "dirugikan": _label(dirugikan),
    }
    if detail:
        hasil["detail"] = detail
    return hasil


def _gabungkan(pelanggaran: List[Dict[str, Any]],
               pelanggar: str, dirugikan: str,
               ringkasan: str) -> Optional[Dict[str, Any]]:
    if not pelanggaran:
        return None
    if len(pelanggaran) == 1:
        return pelanggaran[0]
    report = _pelanggaran(
        "{} ({} syarat)".format(ringkasan, len(pelanggaran)),
        pelanggar, dirugikan,
    )
    report["pelanggaran"] = list(pelanggaran)
    return report


def _range(value: Any) -> Optional[Tuple[Optional[float], Optional[float]]]:
    try:
        if not isinstance(value, (tuple, list)) or len(value) != 2:
            return None
        lo = None if value[0] is None else float(value[0])
        hi = None if value[1] is None else float(value[1])
        if (lo is not None and not math.isfinite(lo)) or (
                hi is not None and not math.isfinite(hi)):
            return None
        return lo, hi
    except (TypeError, ValueError, OverflowError):
        return None


def _range_mencakup(penyedia: Any, kebutuhan: Any) -> bool:
    p = _range(penyedia)
    k = _range(kebutuhan)
    if p is None or k is None:
        return False
    p_lo, p_hi = p
    k_lo, k_hi = k
    return ((p_lo is None or (k_lo is not None and p_lo <= k_lo))
            and (p_hi is None or (k_hi is not None and p_hi >= k_hi)))


def _tipe_kompatibel(penyedia: Any, kebutuhan: Any) -> bool:
    if kebutuhan in (None, "any"):
        return True
    if penyedia == kebutuhan:
        return True
    # `number` pada sisi konsumen menerima kontrak int/float yang lebih sempit.
    if kebutuhan == "number" and penyedia in ("int", "float", "number"):
        return True
    return False


def _cek_skema_field(nama_penyedia: str, nama_konsumen: str,
                     field: str, janji: Any, kebutuhan: Any,
                     optional: bool = False) -> List[Dict[str, Any]]:
    keluar: List[Dict[str, Any]] = []
    if not isinstance(janji, Mapping):
        if not optional:
            keluar.append(_pelanggaran(
                "{} membutuhkan field {} yang tidak dijanjikan".format(
                    nama_konsumen, field),
                nama_penyedia, nama_konsumen, field=field,
            ))
        return keluar
    if not isinstance(kebutuhan, Mapping):
        return [_pelanggaran("deklarasi kebutuhan field {!r} tidak valid".format(field),
                             nama_konsumen, nama_penyedia, field=field)]

    for kunci in ("shape", "key_type", "value_type"):
        required = kebutuhan.get(kunci)
        provided = janji.get(kunci)
        if required is None:
            continue
        if provided is None or (kunci == "shape" and provided != required) or (
                kunci != "shape" and not _tipe_kompatibel(provided, required)):
            keluar.append(_pelanggaran(
                "field {}: {} menjanjikan {}={!r}, {} membutuhkan {!r}".format(
                    field, nama_penyedia, kunci, provided, nama_konsumen, required),
                nama_penyedia, nama_konsumen, field=field, aspek=kunci,
                dijanjikan=provided, dibutuhkan=required,
            ))

    kunci_wajib = kebutuhan.get("keys")
    if kunci_wajib is not None:
        kunci_dijamin = janji.get("keys")
        if not isinstance(kunci_dijamin, (tuple, list, set, frozenset)):
            keluar.append(_pelanggaran(
                "field {} tidak menjanjikan himpunan kunci tetap".format(field),
                nama_penyedia, nama_konsumen, field=field,
                kunci_dibutuhkan=tuple(kunci_wajib),
            ))
        else:
            try:
                hilang = tuple(k for k in kunci_wajib if k not in kunci_dijamin)
            except Exception:
                hilang = tuple(kunci_wajib)
            if hilang:
                keluar.append(_pelanggaran(
                    "field {} tidak menjamin semua kunci yang dibutuhkan".format(field),
                    nama_penyedia, nama_konsumen, field=field,
                    kunci_hilang=hilang,
                ))

    range_wajib = kebutuhan.get("range")
    if range_wajib is not None and not _range_mencakup(janji.get("range"),
                                                      range_wajib):
        keluar.append(_pelanggaran(
            "rentang field {} yang dijanjikan tidak mencakup kebutuhan".format(field),
            nama_penyedia, nama_konsumen, field=field,
            rentang_dijanjikan=janji.get("range"),
            rentang_dibutuhkan=range_wajib,
        ))
    return keluar


def _cek_skema_operasi(nama_penyedia: str, nama_konsumen: str,
                       operasi: str, janji: Any, kebutuhan: Any,
                       optional: bool = False) -> List[Dict[str, Any]]:
    if not isinstance(janji, Mapping):
        if optional:
            return []
        return [_pelanggaran(
            "{} membutuhkan operasi {} yang tidak dijanjikan".format(
                nama_konsumen, operasi),
            nama_penyedia, nama_konsumen, operasi=operasi,
        )]
    if not isinstance(kebutuhan, Mapping):
        return [_pelanggaran("deklarasi kebutuhan operasi {!r} tidak valid".format(operasi),
                             nama_konsumen, nama_penyedia, operasi=operasi)]
    if kebutuhan.get("callable", False) and not janji.get("callable", False):
        return [_pelanggaran(
            "operasi {} tidak dijanjikan callable oleh {}".format(operasi,
                                                                    nama_penyedia),
            nama_penyedia, nama_konsumen, operasi=operasi,
        )]
    fase_wajib = kebutuhan.get("phases")
    fase_dijamin = janji.get("phases")
    if fase_wajib and (not isinstance(fase_dijamin, (tuple, list, set, frozenset))
                       or not set(fase_wajib).issubset(set(fase_dijamin))):
        return [_pelanggaran(
            "operasi {} tidak menjanjikan seluruh fase yang dibutuhkan".format(operasi),
            nama_penyedia, nama_konsumen, operasi=operasi,
            fase_dibutuhkan=tuple(fase_wajib),
        )]
    return []


def verifikasi_startup(janji: Any = None, kebutuhan: Any = None,
                       drives_aktual: Any = None) -> Optional[Dict[str, Any]]:
    """Cocokkan seluruh deklarasi janji/kebutuhan sekali pada startup.

    ``drives_aktual`` opsional agar host yang telah memuat lapisan inti dapat
    membandingkan manifest statis dengan konstanta kode tanpa memaksa kontrak
    mengimpor modul atau menimbulkan siklus dependensi.
    """
    try:
        janji_aktif = JANJI if janji is None else janji
        kebutuhan_aktif = KEBUTUHAN if kebutuhan is None else kebutuhan
        if not isinstance(janji_aktif, Mapping) or not isinstance(kebutuhan_aktif, Mapping):
            return _pelanggaran("manifest JANJI/KEBUTUHAN bukan mapping",
                                "kontrak", "host", tahap="startup")
        pelanggaran: List[Dict[str, Any]] = []
        for konsumen, data_kebutuhan in kebutuhan_aktif.items():
            dependencies = _get(data_kebutuhan, "dependencies", {})
            if not isinstance(dependencies, Mapping):
                pelanggaran.append(_pelanggaran(
                    "dependencies {!r} bukan mapping".format(konsumen),
                    str(konsumen), "kontrak", tahap="startup",
                ))
                continue
            for penyedia, dependency in dependencies.items():
                if not isinstance(dependency, Mapping):
                    pelanggaran.append(_pelanggaran(
                        "deklarasi dependency {} -> {} tidak valid".format(
                            konsumen, penyedia),
                        str(konsumen), str(penyedia), tahap="startup",
                    ))
                    continue
                optional_dependency = bool(dependency.get("optional", False))
                provider = _get(janji_aktif, penyedia)
                if not isinstance(provider, Mapping):
                    if not optional_dependency:
                        pelanggaran.append(_pelanggaran(
                            "{} membutuhkan penyedia {} yang tidak ada di JANJI".format(
                                konsumen, penyedia),
                            str(penyedia), str(konsumen), tahap="startup",
                        ))
                    continue
                promised_fields = _get(provider, "fields", {})
                required_fields = dependency.get("fields", {})
                if isinstance(required_fields, Mapping):
                    for field, spec in required_fields.items():
                        pelanggaran.extend(_cek_skema_field(
                            str(penyedia), str(konsumen), str(field),
                            _get(promised_fields, field), spec,
                            optional=bool(_get(spec, "optional", False)),
                        ))
                promised_ops = _get(provider, "operations", {})
                required_ops = dependency.get("operations", {})
                if isinstance(required_ops, Mapping):
                    for operation, spec in required_ops.items():
                        pelanggaran.extend(_cek_skema_operasi(
                            str(penyedia), str(konsumen), str(operation),
                            _get(promised_ops, operation), spec,
                            optional=bool(_get(spec, "optional", False)),
                        ))
        if drives_aktual is not None:
            try:
                aktual = tuple(str(x) for x in drives_aktual)
            except Exception:
                aktual = ()
            if aktual != DRIVE_KEYS:
                pelanggaran.append(_pelanggaran(
                    "DRIVES aktual tidak sama dengan manifest kontrak",
                    "Naluri", "Lingkungan/Nurani/JejakPrediksi",
                    dijanjikan=DRIVE_KEYS, aktual=aktual,
                ))
        return _gabungkan(pelanggaran, "manifest JANJI/KEBUTUHAN",
                          "modul yang bergantung", "konflik kontrak startup")
    except Exception as galat:
        # Bahkan manifest yang rusak harus menghasilkan laporan, bukan throw.
        return _pelanggaran("pemeriksaan manifest gagal secara aman",
                            "kontrak", "host",
                            jenis_galat=type(galat).__name__)


def _arg(argumen: Any, nama: str, default: Any = None) -> Any:
    return _get(argumen, nama, default)


def _npc_levels(subjek: Any, operasi: str, dirugikan: str,
                periksa_rentang: bool = False) -> List[Dict[str, Any]]:
    """Pemeriksaan lokal enam kunci; tidak menelusuri struktur besar."""
    issues: List[Dict[str, Any]] = []
    levels = _field(subjek, "levels")
    if not isinstance(levels, Mapping):
        return [_pelanggaran(
            "{} membutuhkan levels bertipe mapping".format(operasi),
            "NPC", dirugikan, field="levels",
        )]
    hilang = tuple(d for d in DRIVE_KEYS if d not in levels)
    if hilang:
        issues.append(_pelanggaran(
            "levels tidak memiliki semua kunci DRIVES", "NPC", dirugikan,
            field="levels", kunci_hilang=hilang,
        ))
    tidak_numerik: List[str] = []
    di_luar: List[str] = []
    for drive in DRIVE_KEYS:
        if drive not in levels:
            continue
        value = _get(levels, drive)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            tidak_numerik.append(drive)
            continue
        try:
            number = float(value)
            if not math.isfinite(number) or (periksa_rentang and not -1.0 <= number <= 1.0):
                di_luar.append(drive)
        except (TypeError, ValueError, OverflowError):
            tidak_numerik.append(drive)
    if tidak_numerik:
        issues.append(_pelanggaran(
            "levels harus berisi nilai numerik untuk setiap drive", "NPC", dirugikan,
            field="levels", kunci_tidak_numerik=tuple(tidak_numerik),
        ))
    if di_luar:
        issues.append(_pelanggaran(
            "levels berada di luar rentang [-1, 1]", "NPC", dirugikan,
            field="levels", kunci_di_luar_rentang=tuple(di_luar),
        ))
    return issues


def _arg_posisional(argumen: Any, index: int) -> Any:
    positional = (_arg(argumen, "args") if isinstance(argumen, Mapping)
                  else argumen)
    if isinstance(positional, Sequence) and not isinstance(positional, (str, bytes)):
        try:
            return positional[index]
        except (IndexError, TypeError):
            return None
    return None


def _npc_dari_lingkungan(subjek: Any, argumen: Any,
                         operasi: str) -> Any:
    """Ambil NPC target dari argumen atau badan lingkungan, tanpa menyapu."""
    direct = _arg(argumen, "npc")
    if direct is None and operasi == "tambah_npc":
        direct = _arg_posisional(argumen, 0)
    if direct is not None:
        return direct
    bodies = _field(subjek, "badan")
    if not isinstance(bodies, Mapping):
        return subjek if _field(subjek, "levels") is not None else None
    name = _arg(argumen, "nama", _arg(argumen, "name"))
    if name is None and operasi == "langkah":
        name = _arg_posisional(argumen, 0)
    if name is None and operasi == "tambah_npc":
        # Host boleh memberi badan hasil operasi tambah sebagai subjek;
        # jangan menebak di antara beberapa NPC yang sudah terdaftar.
        name = None
    if name is not None:
        body = _get(bodies, name)
        if body is None:
            body = _get(bodies, _label(name))
        return _field(body, "npc")
    try:
        if len(bodies) == 1:
            body = next(iter(bodies.values()))
            return _field(body, "npc")
    except Exception:
        pass
    return None


def _cek_tambah_npc_masuk(subjek: Any, argumen: Any) -> List[Dict[str, Any]]:
    npc = _npc_dari_lingkungan(subjek, argumen, "tambah_npc")
    if npc is None:
        return [_pelanggaran("NPC tidak diberikan", "Lingkungan", "host",
                             operasi="tambah_npc")]
    return _npc_levels(npc, "Lingkungan.tambah_npc", "Lingkungan")


def _cek_tambah_npc_keluar(subjek: Any, argumen: Any, hasil: Any) -> List[Dict[str, Any]]:
    npc = _npc_dari_lingkungan(subjek, argumen, "tambah_npc")
    if npc is None and _field(subjek, "levels") is not None:
        npc = subjek
    if hasil is None or npc is None or _field(hasil, "npc") is not npc:
        return [_pelanggaran("Badan hasil tidak menautkan NPC yang didaftarkan",
                             "Lingkungan", "pemanggil.tambah_npc")]
    return []


def _cek_langkah_masuk(subjek: Any, argumen: Any) -> List[Dict[str, Any]]:
    npc = _npc_dari_lingkungan(subjek, argumen, "langkah")
    if npc is None:
        return [_pelanggaran("NPC untuk satu langkah tidak tersedia",
                             "Lingkungan", "host.langkah")]
    return _npc_levels(npc, "Lingkungan.langkah", "Lingkungan")


def _cek_langkah_keluar(subjek: Any, argumen: Any, hasil: Any) -> List[Dict[str, Any]]:
    if not isinstance(hasil, Mapping):
        return [_pelanggaran("hasil langkah harus berupa mapping",
                             "Lingkungan", "pemanggil.langkah")]
    wajib = ("aksi", "delta", "posisi", "npc", "tick")
    hilang = tuple(x for x in wajib if x not in hasil)
    if hilang:
        return [_pelanggaran("hasil langkah tidak memenuhi bentuk yang dijanjikan",
                             "Lingkungan", "pemanggil.langkah",
                             field_hilang=hilang)]
    return []


def _cek_tick_masuk(subjek: Any, argumen: Any) -> List[Dict[str, Any]]:
    issues = _npc_levels(subjek, "Naluri.tick", "pemanggil.tick")
    events = _arg(argumen, "events")
    if events is not None and (isinstance(events, (str, bytes)) or
                               not isinstance(events, Iterable)):
        issues.append(_pelanggaran("events harus iterable atau None",
                                   "pemanggil.tick", "Naluri",
                                   tipe=type(events).__name__))
    cost = _arg(argumen, "action_cost", False)
    if not isinstance(cost, bool):
        issues.append(_pelanggaran("action_cost harus bool",
                                   "pemanggil.tick", "Naluri",
                                   tipe=type(cost).__name__))
    return issues


def _cek_tick_keluar(subjek: Any, argumen: Any, hasil: Any) -> List[Dict[str, Any]]:
    issues: List[Dict[str, Any]] = []
    if hasil is not None:
        issues.append(_pelanggaran("Naluri.tick menjanjikan return None",
                                   "Naluri", "pemanggil.tick",
                                   tipe=type(hasil).__name__))
    tick_after = _field(subjek, "tick_count")
    tick_before = _arg(argumen, "tick_before")
    if tick_after is not None:
        if isinstance(tick_after, bool) or not isinstance(tick_after, int):
            issues.append(_pelanggaran("tick_count harus int setelah tick",
                                       "Naluri", "pemanggil.tick",
                                       nilai=type(tick_after).__name__))
        elif isinstance(tick_before, int) and not isinstance(tick_before, bool):
            if tick_after != tick_before + 1:
                issues.append(_pelanggaran("tick_count harus maju tepat satu",
                                           "Naluri", "pemanggil.tick",
                                           sebelum=tick_before, sesudah=tick_after))
    issues.extend(_npc_levels(subjek, "Naluri.tick", "pemanggil.tick",
                              periksa_rentang=True))
    return issues


def _cek_choose_masuk(subjek: Any, argumen: Any) -> List[Dict[str, Any]]:
    candidates = _arg(argumen, "candidates")
    if (not isinstance(candidates, Sequence) or
            isinstance(candidates, (str, bytes))):
        return [_pelanggaran("candidates harus sequence", "pemanggil.choose_action",
                             "Naluri.choose_action")]
    return []


def _cek_choose_keluar(subjek: Any, argumen: Any, hasil: Any) -> List[Dict[str, Any]]:
    candidates = _arg(argumen, "candidates", ())
    if not isinstance(hasil, Mapping):
        return [_pelanggaran("choose_action harus mengembalikan mapping",
                             "Naluri.choose_action", "Lingkungan")]
    try:
        jumlah = len(candidates)
    except Exception:
        jumlah = 0
    if jumlah:
        action = _get(hasil, "action")
        # Keanggotaan diperiksa pada daftar kecil saja; kontrak tidak mengaudit
        # populasi kandidat besar dan tidak membangun salinan kandidatnya.
        if jumlah <= 128:
            cocok = False
            for candidate in islice(iter(candidates), 128):
                if isinstance(candidate, Mapping) and _get(candidate, "name") == action:
                    cocok = True
                    break
            if not cocok:
                return [_pelanggaran(
                    "aksi hasil choose_action harus berasal dari kandidat",
                    "Naluri.choose_action", "Lingkungan",
                    aksi=action, jumlah_kandidat=jumlah)]
    return []


def _cek_reward_masuk(subjek: Any, argumen: Any) -> List[Dict[str, Any]]:
    deltas = _arg(argumen, "deltas")
    if not isinstance(deltas, Mapping):
        return [_pelanggaran("deltas harus mapping drive -> angka",
                             "pemanggil.reward_for", "Naluri.reward_for")]
    try:
        sample = islice(iter(deltas.items()), len(DRIVE_KEYS) + 4)
        bad = tuple(k for k, v in sample
                    if isinstance(v, bool) or not isinstance(v, (int, float)))
    except Exception:
        bad = ("<mapping tidak dapat dibaca>",)
    if bad:
        return [_pelanggaran("deltas berisi nilai non-numerik",
                             "pemanggil.reward_for", "Naluri.reward_for",
                             kunci=bad)]
    return []


def _cek_reward_keluar(subjek: Any, argumen: Any, hasil: Any) -> List[Dict[str, Any]]:
    if isinstance(hasil, bool) or not isinstance(hasil, (int, float)):
        return [_pelanggaran("reward_for harus mengembalikan angka",
                             "Naluri.reward_for", "pemanggil.reward_for",
                             tipe=type(hasil).__name__)]
    try:
        if not math.isfinite(float(hasil)):
            return [_pelanggaran("reward_for harus finite", "Naluri.reward_for",
                                 "pemanggil.reward_for")]
    except (TypeError, ValueError, OverflowError):
        return [_pelanggaran("reward_for harus finite", "Naluri.reward_for",
                             "pemanggil.reward_for")]
    return []


def _cek_record_masuk(subjek: Any, argumen: Any) -> List[Dict[str, Any]]:
    stimulus = _arg(argumen, "stimulus")
    if not isinstance(stimulus, str) or not stimulus.strip():
        return [_pelanggaran("stimulus record_experience wajib string non-kosong",
                             "pemanggil.record_experience", "JejakPrediksi")]
    return []


def _cek_record_keluar(subjek: Any, argumen: Any, hasil: Any) -> List[Dict[str, Any]]:
    if isinstance(hasil, bool) or not isinstance(hasil, int) or hasil <= 0:
        return [_pelanggaran("record_experience harus mengembalikan id episode positif",
                             "JejakPrediksi.record_experience", "pemanggil.record_experience",
                             hasil=hasil)]
    return []


def _cek_predict_masuk(subjek: Any, argumen: Any) -> List[Dict[str, Any]]:
    stimulus = _arg(argumen, "stimulus")
    if not isinstance(stimulus, str) or not stimulus.strip():
        return [_pelanggaran("stimulus predict wajib string non-kosong",
                             "pemanggil.predict", "JejakPrediksi")]
    return []


def _cek_forecast(hasil: Any, operasi: str) -> List[Dict[str, Any]]:
    if not isinstance(hasil, Mapping):
        return [_pelanggaran("{} harus mengembalikan mapping".format(operasi),
                             "JejakPrediksi." + operasi, "pemanggil." + operasi)]
    forecast = _get(hasil, "forecast")
    if not isinstance(forecast, Mapping):
        return [_pelanggaran("hasil predict tidak memiliki forecast mapping",
                             "JejakPrediksi.predict", "pemanggil.predict",
                             field="forecast")]
    issues: List[Dict[str, Any]] = []
    deltas = _get(forecast, "drive_deltas")
    if not isinstance(deltas, Mapping):
        issues.append(_pelanggaran("forecast.drive_deltas harus mapping",
                                   "JejakPrediksi.predict", "pemanggil.predict"))
    else:
        missing = tuple(d for d in DRIVE_KEYS if d not in deltas)
        if missing:
            issues.append(_pelanggaran("forecast tidak menjamin semua drive",
                                       "JejakPrediksi.predict", "pemanggil.predict",
                                       kunci_hilang=missing))
        bad: List[str] = []
        for drive in DRIVE_KEYS:
            if drive not in deltas:
                continue
            value = _get(deltas, drive)
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                bad.append(drive)
                continue
            try:
                number = float(value)
                if not math.isfinite(number) or not -1.0 <= number <= 1.0:
                    bad.append(drive)
            except (TypeError, ValueError, OverflowError):
                bad.append(drive)
        if bad:
            issues.append(_pelanggaran("forecast.drive_deltas harus finite di [-1, 1]",
                                       "JejakPrediksi.predict", "pemanggil.predict",
                                       kunci_tidak_valid=tuple(bad)))
    for name in ("impact", "confidence"):
        value = _get(forecast, name)
        lo, hi = (-1.0, 1.0) if name == "impact" else (0.0, 1.0)
        try:
            number = float(value)
            if isinstance(value, bool) or not math.isfinite(number) or not lo <= number <= hi:
                raise ValueError
        except (TypeError, ValueError, OverflowError):
            issues.append(_pelanggaran("forecast.{} berada di luar kontrak".format(name),
                                       "JejakPrediksi.predict", "pemanggil.predict",
                                       field=name, rentang=(lo, hi)))
    return issues


def _cek_predict_keluar(subjek: Any, argumen: Any, hasil: Any) -> List[Dict[str, Any]]:
    return _cek_forecast(hasil, "predict")


def _cek_reinforce_masuk(subjek: Any, argumen: Any) -> List[Dict[str, Any]]:
    prediction = _arg(argumen, "prediction")
    stimulus = _arg(argumen, "stimulus")
    if not stimulus and isinstance(prediction, Mapping):
        stimulus = _get(prediction, "stimulus")
    if not isinstance(stimulus, str) or not stimulus.strip():
        return [_pelanggaran("reinforce membutuhkan stimulus dari argumen/prediksi",
                             "pemanggil.reinforce", "JejakPrediksi")]
    if not isinstance(prediction, Mapping):
        return [_pelanggaran("prediction reinforce harus mapping",
                             "pemanggil.reinforce", "JejakPrediksi")]
    return []


def _cek_reinforce_keluar(subjek: Any, argumen: Any, hasil: Any) -> List[Dict[str, Any]]:
    if not isinstance(hasil, Mapping):
        return [_pelanggaran("reinforce harus mengembalikan mapping",
                             "JejakPrediksi.reinforce", "pemanggil.reinforce")]
    episode_id = _get(hasil, "episode_id", _get(hasil, "id"))
    if episode_id is not None and (isinstance(episode_id, bool) or
                                   not isinstance(episode_id, int) or episode_id <= 0):
        return [_pelanggaran("reinforce mengembalikan episode_id tidak valid",
                             "JejakPrediksi.reinforce", "pemanggil.reinforce",
                             episode_id=episode_id)]
    return []


def _cek_ucap_masuk(subjek: Any, argumen: Any) -> List[Dict[str, Any]]:
    if subjek is None:
        return [_pelanggaran("Presentasi tidak tersedia", "pemanggil.ucap", "Presentasi")]
    return []


def _cek_ucap_keluar(subjek: Any, argumen: Any, hasil: Any) -> List[Dict[str, Any]]:
    if not isinstance(hasil, Mapping):
        return [_pelanggaran("Presentasi.ucap harus mengembalikan mapping",
                             "Presentasi.ucap", "pemanggil.ucap")]
    if hasil and not isinstance(_get(hasil, "act"), str):
        return [_pelanggaran("hasil ucap aktif harus menyebut act string",
                             "Presentasi.ucap", "pemanggil.ucap")]
    return []


def _angka_dalam(value: Any, lo: float, hi: float) -> bool:
    try:
        number = float(value)
        return (not isinstance(value, bool) and math.isfinite(number)
                and lo <= number <= hi)
    except (TypeError, ValueError, OverflowError):
        return False


def _cek_nilai_selaras_masuk(subjek: Any, argumen: Any) -> List[Dict[str, Any]]:
    issues: List[Dict[str, Any]] = []
    persona = _arg(argumen, "persona")
    keadaan = _arg(argumen, "keadaan")
    teks = _arg(argumen, "teks")
    nama = _field(persona, "nama")
    if not isinstance(nama, str) or not nama.strip():
        issues.append(_pelanggaran(
            "nilai_selaras membutuhkan persona bernama",
            "pemanggil.nilai_selaras", "penilai", field="persona.nama"))
    sifat = _field(persona, "sifat")
    if sifat is not None and not isinstance(sifat, Mapping):
        issues.append(_pelanggaran(
            "persona.sifat harus mapping", "pemanggil.nilai_selaras", "penilai",
            field="persona.sifat"))
    for field, lo, hi in (("valensi", -1.0, 1.0), ("gairah", 0.0, 1.0),
                          ("ketidakpastian", 0.0, 1.0)):
        if not _angka_dalam(_field(keadaan, field), lo, hi):
            issues.append(_pelanggaran(
                "nilai_selaras membutuhkan keadaan.{} dalam [{}, {}]".format(
                    field, lo, hi),
                "pemanggil.nilai_selaras", "penilai", field="keadaan." + field))
    if not isinstance(teks, str) or not teks.strip():
        issues.append(_pelanggaran(
            "nilai_selaras membutuhkan teks string non-kosong",
            "pemanggil.nilai_selaras", "penilai", field="teks"))
    return issues


def _cek_nilai_selaras_keluar(subjek: Any, argumen: Any,
                              hasil: Any) -> List[Dict[str, Any]]:
    issues: List[Dict[str, Any]] = []
    status = _field(hasil, "status")
    if not isinstance(status, str) or not status.strip():
        issues.append(_pelanggaran(
            "hasil nilai_selaras harus memuat status string",
            "penilai.nilai_selaras", "pemanggil.nilai_selaras", field="status"))
    skor = _field(hasil, "skor")
    if skor is not None and not _angka_dalam(skor, 0.0, 1.0):
        issues.append(_pelanggaran(
            "skor hasil nilai_selaras harus None atau angka dalam [0, 1]",
            "penilai.nilai_selaras", "pemanggil.nilai_selaras", field="skor"))
    dimensi = _field(hasil, "dimensi")
    if not isinstance(dimensi, (tuple, list)):
        issues.append(_pelanggaran(
            "dimensi hasil nilai_selaras harus sekuens",
            "penilai.nilai_selaras", "pemanggil.nilai_selaras", field="dimensi"))
    return issues


def _cek_catat_masuk(subjek: Any, argumen: Any) -> List[Dict[str, Any]]:
    issues: List[Dict[str, Any]] = []
    laporan = _arg(argumen, "laporan")
    if not isinstance(_field(laporan, "status"), str):
        issues.append(_pelanggaran(
            "pelacak.catat membutuhkan laporan berstatus",
            "pemanggil.catat", "PelacakSelaras", field="laporan"))
    kapasitas = _field(subjek, "kapasitas")
    if (isinstance(kapasitas, bool) or not isinstance(kapasitas, int)
            or kapasitas < 2):
        issues.append(_pelanggaran(
            "pelacak membutuhkan kapasitas integer >= 2",
            "PelacakSelaras", "pemanggil.catat", field="kapasitas"))
    return issues


def _cek_catat_keluar(subjek: Any, argumen: Any, hasil: Any) -> List[Dict[str, Any]]:
    if hasil is not None:
        return [_pelanggaran("pelacak.catat tidak mengembalikan nilai",
                             "PelacakSelaras", "pemanggil.catat")]
    return []


class _OperationChecks(TypedDict):
    masuk: Tuple[Callable[..., Any], ...]
    keluar: Tuple[Callable[..., Any], ...]
    violator: str
    injured: str


_OPERATION_CHECKS: Dict[str, _OperationChecks] = {
    "lingkungan.tambah_npc": {
        "masuk": (_cek_tambah_npc_masuk,),
        "keluar": (_cek_tambah_npc_keluar,),
        "violator": "Lingkungan", "injured": "host",
    },
    "lingkungan.langkah": {
        "masuk": (_cek_langkah_masuk,),
        "keluar": (_cek_langkah_keluar,),
        "violator": "Lingkungan", "injured": "host.langkah",
    },
    "naluri.tick": {
        "masuk": (_cek_tick_masuk,),
        "keluar": (_cek_tick_keluar,),
        "violator": "Naluri", "injured": "pemanggil.tick",
    },
    "naluri.choose_action": {
        "masuk": (_cek_choose_masuk,),
        "keluar": (_cek_choose_keluar,),
        "violator": "Naluri", "injured": "Lingkungan",
    },
    "naluri.reward_for": {
        "masuk": (_cek_reward_masuk,),
        "keluar": (_cek_reward_keluar,),
        "violator": "Naluri", "injured": "pemanggil.reward_for",
    },
    "jejak.record_experience": {
        "masuk": (_cek_record_masuk,),
        "keluar": (_cek_record_keluar,),
        "violator": "JejakPrediksi", "injured": "pemanggil.record_experience",
    },
    "jejak.predict": {
        "masuk": (_cek_predict_masuk,),
        "keluar": (_cek_predict_keluar,),
        "violator": "JejakPrediksi", "injured": "pemanggil.predict",
    },
    "jejak.reinforce": {
        "masuk": (_cek_reinforce_masuk,),
        "keluar": (_cek_reinforce_keluar,),
        "violator": "JejakPrediksi", "injured": "pemanggil.reinforce",
    },
    "presentasi.ucap": {
        "masuk": (_cek_ucap_masuk,),
        "keluar": (_cek_ucap_keluar,),
        "violator": "Presentasi", "injured": "pemanggil.ucap",
    },
    "penilai.nilai_selaras": {
        "masuk": (_cek_nilai_selaras_masuk,),
        "keluar": (_cek_nilai_selaras_keluar,),
        "violator": "pemanggil.nilai_selaras", "injured": "penilai",
    },
    "pelacak.catat": {
        "masuk": (_cek_catat_masuk,),
        "keluar": (_cek_catat_keluar,),
        "violator": "PelacakSelaras", "injured": "pemanggil.catat",
    },
}

_OPERATION_ALIASES = {
    "step": "lingkungan.langkah",
    "langkah": "lingkungan.langkah",
    "environment.step": "lingkungan.langkah",
    "tambah_npc": "lingkungan.tambah_npc",
    "tick": "naluri.tick",
    "record": "jejak.record_experience",
    "record_experience": "jejak.record_experience",
    "predict": "jejak.predict",
    "reinforce": "jejak.reinforce",
    "choose_action": "naluri.choose_action",
    "reward_for": "naluri.reward_for",
    "ucap": "presentasi.ucap",
    "nilai_selaras": "penilai.nilai_selaras",
}


def _kanonik_operasi(operasi: Any) -> str:
    text = operasi.strip().lower() if isinstance(operasi, str) else ""
    return _OPERATION_ALIASES.get(text, text)


def _fase(fase: Any) -> Optional[str]:
    text = fase.strip().lower() if isinstance(fase, str) else ""
    if text in ("masuk", "pre", "precondition", "input", "entry", "enter"):
        return "masuk"
    if text in ("keluar", "post", "postcondition", "output", "exit", "leave"):
        return "keluar"
    return None


def _lintas_lapis(subjek: Any, operasi: str,
                   argumen: Any = None) -> List[Dict[str, Any]]:
    """Invariant lintas-lapis O(1) / enam drive, bukan audit state global."""
    issues: List[Dict[str, Any]] = []
    owner = subjek
    if operasi.startswith("lingkungan."):
        action = "langkah" if operasi.endswith("langkah") else "tambah_npc"
        owner = _npc_dari_lingkungan(subjek, argumen, action)
    elif operasi.startswith(("presentasi.", "kesadaran.")):
        owner = _field(subjek, "naluri")
    elif operasi.startswith("jejak."):
        owner = _field(subjek, "naluri")
    if owner is None:
        return issues
    nur = _field(owner, "nurani")
    if nur is not None:
        drives = _field(nur, "drives")
        if isinstance(drives, Sequence) and not isinstance(drives, (str, bytes)):
            observed = tuple(islice(iter(drives), len(DRIVE_KEYS) + 1))
            if len(observed) != len(DRIVE_KEYS) or set(observed) != set(DRIVE_KEYS):
                issues.append(_pelanggaran(
                    "Naluri dan Nurani tidak sepakat pada himpunan DRIVES",
                    "Nurani", "Naluri", drives_nurani=observed,
                    drives_manifest=DRIVE_KEYS,
                ))
        params = _field(owner, "params")
        params_nur = _field(nur, "params")
        if params is not None and params_nur is not None and params is not params_nur:
            issues.append(_pelanggaran(
                "Naluri dan Nurani tidak berbagi objek params yang dijanjikan",
                "Naluri/Nurani", "integrasi refleksi",
            ))
    ks = _field(owner, "kesadaran")
    if ks is not None:
        owner_ks = _field(ks, "naluri")
        if owner_ks is not None and owner_ks is not owner:
            issues.append(_pelanggaran(
                "Kesadaran tertaut ke Naluri yang berbeda",
                "Kesadaran", "Naluri",
            ))
    return issues


def kontrak_operasi(operasi: Any, fase: Any, subjek: Any = None,
                    argumen: Any = None, hasil: Any = None,
                    level: int = 0) -> Optional[Dict[str, Any]]:
    """Jalankan kontrak operasi untuk fase masuk atau keluar.

    Pemeriksaan Level 1 menjalankan semua precondition murah, Level 2 juga
    postcondition, dan Level 3 menambah invariant lintas-lapis kecil. Satu
    kegagalan tidak menghentikan pemeriksaan lain; hasil agregat memuat semua
    pelanggaran daun. Fungsi ini tidak mengubah argumen, subjek, atau hasil.
    """
    try:
        if isinstance(level, bool) or not isinstance(level, int) or not 0 <= level <= 3:
            return _pelanggaran("level kontrak harus integer 0..3",
                                "host", "kontrak", level=level)
        if level == 0:
            return None
        name = _kanonik_operasi(operasi)
        phase = _fase(fase)
        contract = _OPERATION_CHECKS.get(name)
        if phase is None:
            return _pelanggaran("fase kontrak harus masuk atau keluar",
                                name or "host", "kontrak", fase=fase)
        if contract is None:
            return _pelanggaran("operasi tidak memiliki deklarasi kontrak",
                                name or "host", "kontrak", operasi=operasi)
        # Level 1 sengaja hanya precondition; postcondition baru aktif pada 2.
        if phase == "keluar" and level < 2:
            return None
        checks = contract["masuk"] if phase == "masuk" else contract["keluar"]
        pelanggaran: List[Dict[str, Any]] = []
        args = {} if argumen is None else argumen
        for check in checks:
            try:
                ditemukan = check(subjek, args) if phase == "masuk" else check(
                    subjek, args, hasil)
                if isinstance(ditemukan, list):
                    pelanggaran.extend(x for x in ditemukan if isinstance(x, dict))
                elif isinstance(ditemukan, dict):
                    pelanggaran.append(ditemukan)
            except Exception as galat:
                pelanggaran.append(_pelanggaran(
                    "validator operasi gagal secara aman",
                    str(contract.get("violator", name)),
                    str(contract.get("injured", "host")),
                    validator=getattr(check, "__name__", "validator"),
                    jenis_galat=type(galat).__name__,
                ))
        if level >= 3:
            try:
                pelanggaran.extend(_lintas_lapis(subjek, name, argumen))
            except Exception as galat:
                pelanggaran.append(_pelanggaran(
                    "pemeriksaan lintas-lapis gagal secara aman",
                    str(contract.get("violator", name)),
                    str(contract.get("injured", "host")),
                    jenis_galat=type(galat).__name__,
                ))
        return _gabungkan(pelanggaran,
                          str(contract.get("violator", name)),
                          str(contract.get("injured", "host")),
                          "kontrak {} fase {} dilanggar".format(name, phase))
    except Exception as galat:
        return _pelanggaran("pemeriksaan operasi gagal secara aman",
                            _label(operasi, "host"), "host",
                            jenis_galat=type(galat).__name__)


# Alias Inggris kecil untuk host yang API-nya memakai nama bahasa Inggris.
def check_operation(operation: Any = None, phase: Any = None,
                    subject: Any = None, arguments: Any = None,
                    result: Any = None, level: int = 0,
                    **kwargs: Any) -> Optional[Dict[str, Any]]:
    """Pembungkus nama-argumen Inggris untuk :func:`kontrak_operasi`."""
    try:
        return kontrak_operasi(
            kwargs.get("operasi", operation), kwargs.get("fase", phase),
            kwargs.get("subjek", subject), kwargs.get("argumen", arguments),
            kwargs.get("hasil", result), kwargs.get("level", level),
        )
    except Exception:
        return _pelanggaran("pemeriksaan operasi gagal secara aman",
                            "kontrak", "host")


def verify_startup(promises: Any = None, requirements: Any = None,
                   actual_drives: Any = None,
                   **kwargs: Any) -> Optional[Dict[str, Any]]:
    """Pembungkus nama-argumen Inggris untuk :func:`verifikasi_startup`."""
    try:
        return verifikasi_startup(
            kwargs.get("janji", promises),
            kwargs.get("kebutuhan", requirements),
            kwargs.get("drives_aktual", actual_drives),
        )
    except Exception:
        return _pelanggaran("pemeriksaan manifest gagal secara aman",
                            "kontrak", "host")
