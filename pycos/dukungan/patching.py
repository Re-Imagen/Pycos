"""pycos/dukungan/patching.py — utilitas batas integrasi runtime Pycos.

Impor opsional memakai nama modul bertitik penuh (mis.
"pycos.mandiri.organik") sehingga seragam di seluruh subpaket. Metode baru
hanya boleh ditambahkan ke slot kosong, sementara perubahan pada metode lama
dipasang sebagai wrapper yang menjaga implementasi sebelumnya. Setiap
pemasangan ber-ID supaya aman dipanggil lebih dari sekali.
"""
from __future__ import annotations

import importlib
import inspect
from functools import update_wrapper
from threading import RLock
from weakref import WeakValueDictionary
from typing import Any, Callable, Dict, Iterable, List, Mapping, Tuple, Union


_PATCH_IDS = "__pycos_patch_ids__"
_MISSING = object()
_LOCK = RLock()
_TARGETS: WeakValueDictionary[int, type] = WeakValueDictionary()


def _modul_absen(galat: ImportError, nama: str) -> bool:
    """True bila galat impor berarti *nama* itu sendiri tidak ada.

    Galat karena dependensi di dalam modul yang ada (mis. ``numpy`` absen
    untuk ``pycos.x``) bukan keabsenan modul: ia harus tetap terlihat, bukan
    ditelan lalu fitur diam-diam mati.
    """
    hilang = getattr(galat, "name", None)
    if not hilang:
        return False
    return nama == hilang or nama.startswith(hilang + ".")


def optional_module(name: str, package: str = "") -> Any:
    """Impor modul opsional: relatif ke ``package``, lalu sebagai nama mutlak.

    Mengembalikan ``None`` hanya bila modul itu sendiri tidak ada. Bila modul
    ada tetapi gagal diimpor karena dependensinya, galat dilempar ulang.
    """
    if not isinstance(name, str) or not name.strip():
        raise ValueError("nama modul opsional wajib berupa string non-kosong")
    if package:
        try:
            return importlib.import_module("." + name, package=package)
        except ImportError as galat:
            if not _modul_absen(galat, "{}.{}".format(package, name)):
                raise
    try:
        return importlib.import_module(name)
    except ImportError as galat:
        if not _modul_absen(galat, name):
            raise
        return None


class PatchConflictError(RuntimeError):
    """Dilempar bila ekstensi akan menimpa metode yang tidak diharapkan."""


def _validate_target(target: type, name: str, patch_id: str) -> None:
    if not isinstance(target, type):
        raise TypeError("target patch harus berupa kelas")
    if not isinstance(name, str) or not name.isidentifier():
        raise ValueError("nama metode patch tidak valid: {!r}".format(name))
    if not isinstance(patch_id, str) or not patch_id.strip():
        raise ValueError("patch_id wajib berupa string non-kosong")


def _unwrap_descriptor(descriptor: Any) -> Tuple[Any, Any]:
    """Kembalikan fungsi dan jenis descriptor tanpa melakukan binding."""
    if isinstance(descriptor, (classmethod, staticmethod)):
        return descriptor.__func__, type(descriptor)
    return descriptor, None


def _patch_ids(descriptor: Any) -> Tuple[str, ...]:
    function, _ = _unwrap_descriptor(descriptor)
    ids = getattr(function, _PATCH_IDS, ())
    return tuple(ids) if isinstance(ids, (tuple, list, set, frozenset)) else ()


def _tag(function: Callable[..., Any], patch_id: str,
         inherited_ids: Iterable[str] = ()) -> Callable[..., Any]:
    ids = list(inherited_ids)
    for existing in getattr(function, _PATCH_IDS, ()):
        if existing not in ids:
            ids.append(existing)
    if patch_id not in ids:
        ids.append(patch_id)
    setattr(function, _PATCH_IDS, tuple(ids))
    return function


def _conflict(target: type, name: str, patch_id: str) -> PatchConflictError:
    return PatchConflictError(
        "patch {!r} tidak dipasang: {}.{}.{} sudah memiliki implementasi "
        "yang tidak dikelola patch ini".format(
            patch_id, target.__module__, target.__qualname__, name))


def install_method(target: type, name: str, method: Callable[..., Any], *,
                   patch_id: str) -> bool:
    """Tambahkan metode hanya jika slot belum terpakai.

    Mengembalikan ``True`` bila metode baru dipasang dan ``False`` bila patch
    yang sama sudah terpasang. Benturan tidak pernah menimpa metode lama;
    ``PatchConflictError`` memberi tahu integrator tentang konflik tersebut.
    """
    return bool(install_methods(target, ((name, method),), patch_id=patch_id))


def install_methods(target: type,
                    methods: Union[Mapping[str, Any], Iterable[Tuple[str, Any]]],
                    *, patch_id: str) -> Tuple[str, ...]:
    """Pasang sekumpulan metode secara atomik dan idempoten.

    ID individual dibentuk dari ``patch_id`` dan nama metode. Semua benturan
    diperiksa sebelum satu pun perubahan dilakukan, sehingga batch tidak
    meninggalkan kelas dalam keadaan terpasang sebagian.
    """
    _validate_target(target, "_", patch_id)
    pairs = list(methods.items() if isinstance(methods, Mapping) else methods)
    if len({name for name, _ in pairs}) != len(pairs):
        raise ValueError("nama metode duplikat dalam satu batch patch")

    with _LOCK:
        # Fase 1 — validasi murni: tidak ada objek yang dimutasi di sini, sehingga
        # batch yang ditolak (benturan atau TypeError di tengah) tidak
        # meninggalkan fungsi ber-tag yang sebagian.
        pending = []
        retag = []
        for name, method in pairs:
            _validate_target(target, name, patch_id)
            if not callable(method) and not isinstance(method, (classmethod, staticmethod)):
                raise TypeError("{} harus callable".format(name))
            current = inspect.getattr_static(target, name, _MISSING)
            method_id = "{}.{}".format(patch_id, name)
            if current is not _MISSING:
                if method_id in _patch_ids(current):
                    continue
                if current is method:
                    function, _ = _unwrap_descriptor(current)
                    retag.append((function, method_id))
                    continue
                raise _conflict(target, name, method_id)
            pending.append((name, method, method_id))

        prepared = []
        for name, method, method_id in pending:
            function, descriptor_type = _unwrap_descriptor(method)
            if not callable(function):
                raise TypeError("{} harus callable".format(name))
            descriptor = (descriptor_type(function) if descriptor_type else function)
            prepared.append((name, method_id, function, descriptor))

        # Fase 2 — simpan metadata sebelum tagging maupun pemasangan.
        # Fungsi dapat dipakai di lebih dari satu slot, jadi snapshot per objek.
        snapshots: Dict[int, Tuple[Any, Any]] = {}
        for function, _mid in retag + [(fn, mid) for _n, mid, fn, _d in prepared]:
            snapshots.setdefault(id(function),
                                 (function, getattr(function, _PATCH_IDS, _MISSING)))
        installed = []
        try:
            for function, method_id in retag:
                _tag(function, method_id)
            for _name, method_id, function, _descriptor in prepared:
                _tag(function, method_id)
            for name, _mid, _fn, descriptor in prepared:
                setattr(target, name, descriptor)
                installed.append(name)
        except Exception:
            # Pulihkan slot dan metadata, termasuk fungsi yang di-retag tetapi
            # sudah ada pada kelas sebelum batch dimulai.
            for name in reversed(installed):
                try:
                    delattr(target, name)
                except Exception:
                    pass
            for function, ids in snapshots.values():
                try:
                    if ids is _MISSING:
                        if hasattr(function, _PATCH_IDS):
                            delattr(function, _PATCH_IDS)
                    else:
                        setattr(function, _PATCH_IDS, ids)
                except Exception:
                    pass
            raise
        _TARGETS[id(target)] = target
        return tuple(installed)


def wrap_method(target: type, name: str, wrapper: Callable[..., Any], *,
                patch_id: str) -> bool:
    """Bungkus metode yang sudah ada tanpa kehilangan implementasi lamanya.

    ``wrapper`` menerima fungsi asli sebagai argumen pertama, lalu seluruh
    argumen metode normal. Contoh: ``def log(original, self, *args, **kwargs)``.
    Descriptor ``classmethod`` dan ``staticmethod`` dipertahankan. Wrapper
    dengan ID sama tidak akan ditumpuk ulang, termasuk bila ia berada di tengah
    rantai wrapper.
    """
    _validate_target(target, name, patch_id)
    if not callable(wrapper):
        raise TypeError("wrapper harus callable")

    with _LOCK:
        current = inspect.getattr_static(target, name, _MISSING)
        if current is _MISSING:
            raise PatchConflictError(
                "patch {!r} tidak dipasang: {}.{}.{} tidak ditemukan".format(
                    patch_id, target.__module__, target.__qualname__, name))
        original, descriptor_type = _unwrap_descriptor(current)
        if not callable(original):
            raise _conflict(target, name, patch_id)
        current_ids = _patch_ids(current)
        if patch_id in current_ids:
            _TARGETS[id(target)] = target
            return False

        def composed(*args: Any, **kwargs: Any) -> Any:
            try:
                return wrapper(original, *args, **kwargs)
            except Exception as exc:
                from pycos.dukungan import diagnostik
                diagnostik.catat(patch_id, "galat wrapper; diteruskan ke pemanggil", galat=exc)
                raise

        # update_wrapper dipakai secara eksplisit agar introspeksi nama dan
        # dokumentasi tetap menunjuk ke implementasi yang sedang dibungkus.
        update_wrapper(composed, original)
        _tag(composed, patch_id, current_ids)
        descriptor = descriptor_type(composed) if descriptor_type else composed
        setattr(target, name, descriptor)
        _TARGETS[id(target)] = target
        return True


def inventaris() -> List[Dict[str, Any]]:
    """Snapshot metode ber-ID pada kelas hidup yang dikelola utilitas ini.

    Tidak memuat mesin atau menjalankan descriptor. Hanya slot milik kelas
    tercatat (bukan salinan metode warisan) dilaporkan; urutan patch_ids adalah
    urutan pemasangan. Ini metadata runtime, bukan verifikasi integritas kode.
    Metode yang dihapus/diganti tanpa metadata tidak lagi muncul. Referensi
    kelas lemah tidak memperpanjang umur kelas plugin sementara.
    """
    hasil = []
    with _LOCK:
        for target in list(_TARGETS.values()):
            for nama, descriptor in sorted(vars(target).items()):
                function, jenis = _unwrap_descriptor(descriptor)
                if not callable(function):
                    continue
                ids = _patch_ids(descriptor)
                if not ids:
                    continue
                hasil.append({"kelas": target.__module__ + "." + target.__qualname__,
                              "metode": nama,
                              "jenis": (jenis.__name__ if jenis else "method"),
                              "patch_ids": list(ids)})
    return sorted(hasil, key=lambda baris: (baris["kelas"], baris["metode"]))
