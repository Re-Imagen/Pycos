# Lampiran audit AST seluruh Python Pycos

Dibuat oleh `python3 tools/audit_python.py`; periksa kebaruan dengan `--check`.
Seluruh source proyek termasuk private/demo/init/tool diperiksa; bukan paket dependensi atau build.
Direktori non-source yang dikecualikan: .git, .mypy_cache, .nox, .pytest_cache, .ruff_cache, .tox, .venv, __pycache__, build, dist, env, node_modules, site-packages, venv.
Indikator kontrol/mutasi termasuk scope nested; bukan kompleksitas siklomatik formal.
Nama call bersifat sintaksis, bukan resolusi callback atau monkey patch runtime.
Analisis semantik dan batas bukti: [audit lanjutan](AUDIT_PYTHON_LANJUTAN.md).

Jumlah berkas: **87**.

## `examples/dialog_hud.py`

SHA-256: `4f46f6958a9bf0b9ebb5bea01bb3b07bda58d4c8178109d9e977a98cef7cd75a`

28 baris; 0 kelas; 1 fungsi/metode termasuk nested.

Kelas: tidak ada.
Handler luas: tidak ada.

Impor (termasuk lazy/TYPE_CHECKING): `from pycos.bahasa.tutur import GenContext, TuturEngine`; `from pycos.dukungan.sumber import jalur_leksikon`; `from pycos.inti.naluri import Naluri`; `import json`.

- L9–24 **`main`** · kontrol=3, assignment/delete=4, except=0 · Call: `GenContext`, `Naluri`, `RuntimeError`, `TuturEngine`, `dialog.append`, `engine.ucap`, `jalur_leksikon`, `json.dumps`, `npc.enable_presentasi`, `npc.hud_state`, `npc.presentasi.tag_dialog`, `print`

## `examples/kawanan_lod.py`

SHA-256: `aa3896c350994d2beec4084478701f42a238e5a33607fb5497340d25551bbbef`

26 baris; 0 kelas; 1 fungsi/metode termasuk nested.

Kelas: tidak ada.
Handler luas: tidak ada.

Impor (termasuk lazy/TYPE_CHECKING): `from collections import Counter`; `from pycos.inti.kawanan import KawananNPC`; `import json`.

- L8–22 **`main`** · kontrol=5, assignment/delete=4, except=0 · Call: `'NPC-{:03d}'.format`, `Counter`, `KawananNPC`, `dict`, `json.dumps`, `kawanan.npcs.items`, `kawanan.npcs.values`, `kawanan.set_lod_by_distance`, `kawanan.tambah`, `kawanan.tick_all`, `len`, `print`, `range`

## `examples/npc_dunia.py`

SHA-256: `34280efd1e6c2bca03af43dffb0580697d9d9198d2522d4e3db2204847fbbbc3`

21 baris; 0 kelas; 1 fungsi/metode termasuk nested.

Kelas: tidak ada.
Handler luas: tidak ada.

Impor (termasuk lazy/TYPE_CHECKING): `from pycos.inti.naluri import Naluri`; `from pycos.lingkungan.dunia import Lingkungan`; `import json`.

- L8–17 **`main`** · kontrol=1, assignment/delete=3, except=0 · Call: `Lingkungan.dari_ascii`, `Naluri`, `dunia.langkah_semua`, `dunia.tambah_npc`, `json.dumps`, `print`, `range`, `riwayat.extend`

## `examples/simpan_migrasi.py`

SHA-256: `8d774c50d2e3a5355e8f647e11013764ffcc6d01b015c5718459b8f0e07cd987`

35 baris; 0 kelas; 1 fungsi/metode termasuk nested.

Kelas: tidak ada.
Handler luas: tidak ada.

Impor (termasuk lazy/TYPE_CHECKING): `from pathlib import Path`; `from pycos.dukungan.validasi_state import migrasi`; `from pycos.inti.naluri import Naluri`; `from tempfile import TemporaryDirectory`; `import json`.

- L10–31 **`main`** · kontrol=2, assignment/delete=7, except=0 · Call: `Naluri`, `Naluri.from_dict`, `Naluri.load`, `Path`, `TemporaryDirectory`, `json.dumps`, `lama.pop`, `migrasi`, `npc.save`, `npc.tick`, `npc.to_dict`, `path.is_file`, `print`, `pulih.to_dict`, `range`, `str`

## `pycos/__init__.py`

SHA-256: `54d660f295b7bd82c4ab2fe33f47925198d1811424db5b6bcf34665597a726e6`

215 baris; 0 kelas; 2 fungsi/metode termasuk nested.

Kelas: tidak ada.
Handler luas: tidak ada.

Impor (termasuk lazy/TYPE_CHECKING): `from __future__ import annotations`; `from typing import Any, Dict, List`; `import importlib`.

- L201–211 **`__getattr__`** · kontrol=1, assignment/delete=3, except=0 · Call: `'modul {!r} tidak punya atribut {!r}'.format`, `AttributeError`, `_MODUL_NAMA.get`, `getattr`, `globals`, `importlib.import_module`
- L214–215 **`__dir__`** · kontrol=0, assignment/delete=0, except=0 · Call: `globals`, `set`, `sorted`

## `pycos/__main__.py`

SHA-256: `fcbea1d6b4ac62ddfcccb5c2677d9e271de48b369f5fc10ca2541d9f90b5faaf`

314 baris; 0 kelas; 8 fungsi/metode termasuk nested.

Kelas: tidak ada.
Handler luas: 255.

Impor (termasuk lazy/TYPE_CHECKING): `from __future__ import annotations`; `from pycos import __all__ as API_PUBLIK, __version__`; `from pycos.bahasa.tutur import LeksikonCiri`; `from pycos.dukungan.periksa import main_periksa`; `from pycos.dukungan.sumber import NAMA_KORPUS, NAMA_LEKSIKON, jalur_korpus, jalur_leksikon`; `from pycos.inti.persona import PERSONA_CONTOH, Keadaan, Persona`; `from pycos.refleksi.nurani import PelacakSelaras, nilai_selaras`; `from pycos.refleksi.nurani import laporan_kalibrasi, muat_korpus, nilai_selaras`; `from typing import Any, Optional, Sequence, Tuple`; `import argparse`; `import importlib`; `import json`; `import os`; `import sys`.

- L72–77 **`_mode_selaras_aktif`** · kontrol=4, assignment/delete=0, except=0 · Call: `a.startswith`
- L80–93 **`_format_laporan`** · kontrol=4, assignment/delete=1, except=0 · Call: `'  {:<9} skor {:.3f}  obs {:+.3f}  target {:+.3f}'.format`, `'  {:<9} tidak dinilai ({})'.format`, `'Persona: {} | status: {} | skor: {}'.format`, `'\n'.join`, `'{:.3f}'.format`, `baris.append`
- L96–97 **`_fmt`** · kontrol=0, assignment/delete=0, except=0 · Call: `'{:.3f}'.format`
- L100–132 **`_format_kalibrasi`** · kontrol=6, assignment/delete=4, except=0 · Call: `'  akurasi uji pada ambang itu: {} ({} contoh)'.format`, `'  ambang terbaik pada porsi latih ({:.0%}): {:.2f}, akurasi latih {}'.format`, `'  anotator {}: kappa {}, pasangan {}'.format`, `'  pada ambang {:.2f}: akurasi {} ({} contoh)'.format`, `'  uji {} | dinilai {} | akurasi terhadap konsensus {}'.format`, `'  {:<11} label {:>3}  cakupan {}  akurasi {}  kappa {}'.format`, `'  {:<11} tidak ada label'.format`, `'/'.join`, `'Jumlah contoh berlabel: {}'.format`, `'\n'.join`, `_fmt`, `baris.append`, `eksternal.get`, `r.get`
- L135–200 **`jalankan_selaras`** · kontrol=11, assignment/delete=9, except=1 · Call: `'galat: {}'.format`, `Keadaan`, `LeksikonCiri.dari_berkas`, `Persona.from_dict`, `ValueError`, `_KODE_STATUS.get`, `_format_kalibrasi`, `_format_laporan`, `_jalankan_demo`, `ap.add_argument`, `ap.error`, `ap.parse_args`, `argparse.ArgumentParser`, `json.dumps`, `json.load`, `laporan.to_dict`, `laporan_kalibrasi`, `list`, `muat_korpus`, `nilai_selaras`, `open`, `print`
- L203–232 **`_jalankan_demo`** · kontrol=5, assignment/delete=4, except=0 · Call: `'  {:<12} sampel {:>2}  rerata {}  kemiringan {}  -> {}'.format`, `'{:+.5f}'.format`, `'{:.3f}'.format`, `PelacakSelaras`, `_format_laporan`, `json.dumps`, `l.to_dict`, `laporan_list.append`, `nilai_selaras`, `pelacak.catat`, `pelacak.tren`, `print`, `tren.items`
- L235–282 **`cetak_peta`** · kontrol=6, assignment/delete=6, except=1 · Call: `'  TuturEngine gagal dimuat: {}'.format`, `'  TuturEngine.info(): {}'.format`, `'  python -m {:<31}# dari akar repo'.format`, `'  {:<16} {}'.format`, `'  {:<41}# dari direktori mana pun'.format`, `'  {} — TIDAK DITEMUKAN di {}'.format`, `'  {} — {} ({:,} byte)'.format`, `', '.join`, `'Python {}'.format`, `'pycos {} — paket di {}'.format`, `importlib.import_module`, `jalur_korpus`, `jalur_leksikon`, `len`, `modul[len('pycos.'):].replace`, `os.path.abspath`, `os.path.dirname`, `os.path.getsize`, `os.path.isfile`, `os.path.relpath`, `print`, `sys.version.split`, `tutur.TuturEngine`, `tutur.TuturEngine(path=leksikon).info`
- L285–310 **`utama`** · kontrol=4, assignment/delete=3, except=0 · Call: `_mode_selaras_aktif`, `argparse.ArgumentParser`, `cetak_peta`, `jalankan_selaras`, `list`, `main_periksa`, `parser.add_argument`, `parser.error`, `parser.parse_args`

## `pycos/bahasa/__init__.py`

SHA-256: `dd6c864f1d5b42eb41812e637c8b26373b28aa8d6b96e0dfc055f45387d63ddb`

102 baris; 0 kelas; 2 fungsi/metode termasuk nested.

Kelas: tidak ada.
Handler luas: tidak ada.

Impor (termasuk lazy/TYPE_CHECKING): `from .teks import Token, JejakLinguistik, analisis_ujaran, G1_KERAS, G1_LEMAK, VERBA_UMUM, deteksi_bahasa, cakupan_negasi, ekstrak_entitas, ekstrak_topik, jenis_kalimat, jenis_pertanyaan, jejak_pembentukan, kandidat_dasar, koreksi_ejaan, kemiripan, normalisasi_teks, normalisasi_token, pecah_kalimat, periksa_gramatika, potong_batas_kata, stem, tindak_tutur_skor, tokenisasi, urai_subjek_predikat`; `from .tutur import Arg, FiturTutur, GenContext, L0, L1, L2, L3, LEKSIKON_CIRI_BAWAAN, Lattice, Leksikon, LeksikonCiri, Node, Orkestrator, SASPAnalyzer, Tutur, TuturEngine, analisis_teks, konteks_dari_presentasi, sa_sp, sa_sp_literal, sa_sp_pragmatik, token_dari`; `from __future__ import annotations`; `from importlib import import_module`; `from typing import TYPE_CHECKING, Any, Dict, List`.

- L90–98 **`__getattr__`** · kontrol=1, assignment/delete=3, except=0 · Call: `'paket {!r} tidak punya atribut {!r}'.format`, `'{}.{}'.format`, `AttributeError`, `_SUBMODUL.get`, `getattr`, `globals`, `import_module`
- L101–102 **`__dir__`** · kontrol=0, assignment/delete=0, except=0 · Call: `globals`, `set`, `sorted`

## `pycos/bahasa/keadaan.py`

SHA-256: `f22cdf9cf82b07d9fa4e9bee14a5167736553471330a2e76281820102aab0cd8`

119 baris; 0 kelas; 3 fungsi/metode termasuk nested.

Kelas: tidak ada.
Handler luas: 99.

Impor (termasuk lazy/TYPE_CHECKING): `from __future__ import annotations`; `from pycos.bahasa.tutur import GenContext`; `from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple`.

- L51–79 **`konteks_keadaan`** · kontrol=9, assignment/delete=4, except=0 · Call: `GenContext`, `getattr`, `lain.items`, `set`, `str`, `str(x).strip`, `tuple`
- L82–104 **`realisasi`** · kontrol=5, assignment/delete=3, except=1 · Call: `bool`, `engine.ucap`, `getattr`, `getattr(engine, 'tersedia', lambda: False)`, `int`, `konteks_keadaan`, `str`, `str(getattr(hasil, 'teks', '') or '').strip`
- L107–119 **`realisasi_daftar`** · kontrol=3, assignment/delete=2, except=0 · Call: `int`, `keluar.append`, `max`, `range`, `realisasi`

## `pycos/bahasa/teks.py`

SHA-256: `0deca7467a594b37be63d89365ffe6f12a7911fdeecb8fa5ae10bdde3f2d66f5`

1376 baris; 3 kelas; 44 fungsi/metode termasuk nested.

Kelas: `_IdiomSentimen` L195, `Token` L295, `JejakLinguistik` L1304.
Handler luas: 158, 548, 725, 731, 162, 1279.

Impor (termasuk lazy/TYPE_CHECKING): `from __future__ import annotations`; `from collections import Counter`; `from dataclasses import dataclass, field`; `from functools import lru_cache`; `from pathlib import Path as _P`; `from pycos.dukungan import diagnostik as _diag`; `from pycos.dukungan.sumber import ada_sumber_daya, jalur_leksikon`; `from typing import Any, Dict, List, Mapping, Optional, Sequence, Set, Tuple`; `import difflib`; `import json`; `import re`; `import unicodedata`.

- L132–190 **`_idiom_dari_leksikon`** · kontrol=15, assignment/delete=13, except=3 · Call: `_P`, `_P(__file__).resolve`, `_diag.catat`, `bawaan.items`, `c.startswith`, `dok.get`, `e.get`, `float`, `isinstance`, `json.load`, `open`, `peta.setdefault`, `str`, `str(e.get('lema', '')).strip`
- L200–204 **`_IdiomSentimen._bangun`** · kontrol=1, assignment/delete=1, except=0 · Call: `_idiom_dari_leksikon`, `self.update`
- L206–208 **`_IdiomSentimen.__getitem__`** · kontrol=0, assignment/delete=0, except=0 · Call: `dict.__getitem__`, `self._bangun`
- L210–212 **`_IdiomSentimen.__missing__`** · kontrol=0, assignment/delete=0, except=0 · Call: `dict.__getitem__`, `self._bangun`
- L214–216 **`_IdiomSentimen.__iter__`** · kontrol=0, assignment/delete=0, except=0 · Call: `dict.__iter__`, `self._bangun`
- L218–220 **`_IdiomSentimen.items`** · kontrol=0, assignment/delete=0, except=0 · Call: `dict.items`, `self._bangun`
- L222–224 **`_IdiomSentimen.keys`** · kontrol=0, assignment/delete=0, except=0 · Call: `dict.keys`, `self._bangun`
- L226–228 **`_IdiomSentimen.values`** · kontrol=0, assignment/delete=0, except=0 · Call: `dict.values`, `self._bangun`
- L230–232 **`_IdiomSentimen.__len__`** · kontrol=0, assignment/delete=0, except=0 · Call: `dict.__len__`, `self._bangun`
- L234–236 **`_IdiomSentimen.__contains__`** · kontrol=0, assignment/delete=0, except=0 · Call: `dict.__contains__`, `self._bangun`
- L238–240 **`_IdiomSentimen.get`** · kontrol=0, assignment/delete=0, except=0 · Call: `dict.get`, `self._bangun`
- L302–303 **`Token.__repr__`** · kontrol=0, assignment/delete=0, except=0 · Call: `'Token({!r}->{!r},{})'.format`
- L318–324 **`_strip_klitik`** · kontrol=3, assignment/delete=0, except=0 · Call: `kata.endswith`, `len`
- L327–354 **`normalisasi_token`** · kontrol=7, assignment/delete=7, except=0 · Call: `'-'.join`, `'{}-{}'.format`, `_strip_klitik`, `len`, `m.group`, `re.match`, `re.sub`, `s.split`, `str`, `unicodedata.normalize`, `unicodedata.normalize('NFC', str(kata or '')).strip`, `unicodedata.normalize('NFC', str(kata or '')).strip().lower`
- L357–360 **`normalisasi_teks`** · kontrol=1, assignment/delete=0, except=0 · Call: `' '.join`, `normalisasi_token`, `tokenisasi`
- L363–378 **`tokenisasi`** · kontrol=5, assignment/delete=3, except=0 · Call: `Token`, `_TOKEN_RE.finditer`, `m.end`, `m.group`, `m.start`, `normalisasi_token`, `out.append`, `str`, `unicodedata.normalize`
- L381–396 **`pecah_kalimat`** · kontrol=5, assignment/delete=5, except=0 · Call: `m.group`, `m.group(0).replace`, `out.append`, `p.strip`, `p.strip().replace`, `re.split`, `re.sub`, `str`, `str(teks or '').strip`
- L422–527 **`kandidat_dasar`** · kontrol=39, assignment/delete=18, except=0 · Call: `_ALOFON_POLOS.get`, `baru.append`, `bentuk.endswith`, `bentuk.startswith`, `dict.fromkeys`, `hasil.append`, `hasil.remove`, `kandidat_dasar`, `len`, `list`, `re.sub`, `semua.extend`, `semua.sort`, `str`, `unicodedata.normalize`, `unicodedata.normalize('NFC', str(kata or '')).strip`, `unicodedata.normalize('NFC', str(kata or '')).strip().lower`, `w.split`
- L531–549 **`kosakata_bawaan`** · kontrol=5, assignment/delete=1, except=1 · Call: `ada_sumber_daya`, `dok.get`, `e.get`, `frozenset`, `jalur_leksikon`, `json.load`, `lru_cache`, `open`, `str`, `str(e.get('lema', '')).lower`
- L582–614 **`urai_reduplikasi`** · kontrol=10, assignment/delete=6, except=0 · Call: `a.endswith`, `b.startswith`, `dict.fromkeys`, `len`, `list`, `out.append`, `re.sub`, `str`, `unicodedata.normalize`, `unicodedata.normalize('NFC', str(kata or '')).strip`, `unicodedata.normalize('NFC', str(kata or '')).strip().lower`, `w.split`
- L617–634 **`reduplikasi`** · kontrol=5, assignment/delete=3, except=0 · Call: `ValueError`, `_REDUP_TERBALIK.get`, `re.sub`, `str`, `unicodedata.normalize`, `unicodedata.normalize('NFC', str(kata or '')).strip`, `unicodedata.normalize('NFC', str(kata or '')).strip().lower`
- L637–652 **`stem`** · kontrol=8, assignment/delete=2, except=0 · Call: `kandidat_dasar`, `kosakata_bawaan`, `str`, `str(kata or '').lower`
- L658–708 **`cakupan_negasi`** · kontrol=13, assignment/delete=15, except=0 · Call: `enumerate`, `len`
- L714–715 **`_kata_tokens`** · kontrol=1, assignment/delete=0, except=0 · Call: tidak ada
- L718–733 **`_kelas_dari`** · kontrol=7, assignment/delete=2, except=2 · Call: `callable`, `ent.get`, `fn`, `getattr`, `leksikon.ambil`, `list`
- L736–739 **`_adalah_verba`** · kontrol=1, assignment/delete=0, except=0 · Call: `_kelas_dari`
- L742–784 **`jenis_kalimat`** · kontrol=17, assignment/delete=7, except=0 · Call: `_adalah_verba`, `_kata_tokens`, `any`, `len`, `list`, `low.rstrip`, `low.rstrip().endswith`, `raw.lower`, `raw.rstrip`, `raw.rstrip().endswith`, `str`, `str(teks or '').strip`, `t.bentuk.endswith`, `tokenisasi`
- L787–814 **`jenis_pertanyaan`** · kontrol=18, assignment/delete=4, except=0 · Call: `_kata_tokens`, `any`, `k.endswith`, `list`, `raw.rstrip`, `raw.rstrip().endswith`, `set`, `str`, `str(teks or '').strip`, `tokenisasi`
- L820–834 **`_awalan_verba`** · kontrol=6, assignment/delete=1, except=0 · Call: `(bentuk or '').lower`, `b.startswith`, `len`
- L837–921 **`urai_subjek_predikat`** · kontrol=43, assignment/delete=22, except=0 · Call: `'{} {}'.format`, `_adalah_verba`, `_awalan_verba`, `_kata_tokens`, `_kelas_dari`, `enumerate`, `len`, `range`
- L927–1010 **`tindak_tutur_skor`** · kontrol=55, assignment/delete=34, except=0 · Call: `' '.join`, `_kata_tokens`, `any`, `dict`, `jenis_kalimat`, `len`, `list`, `low.startswith`, `max`, `sem.get`, `set`, `skor.values`, `stem`, `tokenisasi`
- L1013–1044 **`ekstrak_entitas`** · kontrol=12, assignment/delete=9, except=0 · Call: `_adalah_verba`, `_kata_tokens`, `e['teks'].lower`, `enumerate`, `len`, `list`, `out.append`, `seen.add`, `set`, `t.asli[:1].isupper`, `tokenisasi`, `uniq.append`
- L1047–1080 **`ekstrak_topik`** · kontrol=17, assignment/delete=2, except=0 · Call: `_kata_tokens`, `_kelas_dari`, `b.endswith`, `len`, `list`, `tokenisasi`
- L1083–1097 **`deteksi_bahasa`** · kontrol=10, assignment/delete=4, except=0 · Call: `_kata_tokens`, `sum`, `tokenisasi`
- L1103–1105 **`_ngram`** · kontrol=1, assignment/delete=1, except=0 · Call: `len`, `range`
- L1108–1120 **`kemiripan`** · kontrol=4, assignment/delete=7, except=0 · Call: `_kata_tokens`, `_ngram`, `difflib.SequenceMatcher`, `difflib.SequenceMatcher(None, normalisasi_teks(a), normalisasi_teks(b)).ratio`, `float`, `len`, `normalisasi_teks`, `set`, `stem`, `tokenisasi`
- L1123–1129 **`koreksi_ejaan`** · kontrol=2, assignment/delete=2, except=0 · Call: `difflib.get_close_matches`, `list`, `normalisasi_token`, `set`
- L1143–1213 **`periksa_gramatika`** · kontrol=31, assignment/delete=9, except=0 · Call: `_kata_tokens`, `_kelas_dari`, `dict.fromkeys`, `enumerate`, `last.endswith`, `len`, `list`, `masalah.append`, `range`, `re.match`, `re.search`, `stem`, `str`, `str(teks or '').strip`, `tokenisasi`
- L1229–1253 **`jejak_bentuk`** · kontrol=7, assignment/delete=5, except=0 · Call: `detail.items`, `dict`, `keluar.append`, `str`
- L1256–1285 **`kata_isi`** · kontrol=8, assignment/delete=6, except=1 · Call: `_kata_tokens`, `keluar.append`, `leksikon.kelas_dari`, `len`, `str`, `str(kelas).upper`, `tokenisasi`, `w.lower`
- L1288–1297 **`potong_batas_kata`** · kontrol=3, assignment/delete=4, except=0 · Call: `len`, `potong.rfind`, `potong.rstrip`, `str`
- L1313–1317 **`JejakLinguistik.to_dict`** · kontrol=0, assignment/delete=0, except=0 · Call: `dict`
- L1320–1345 **`jejak_pembentukan`** · kontrol=9, assignment/delete=1, except=0 · Call: `JejakLinguistik`, `JejakLinguistik(input_teks=input_teks, filter_keadaan=dict(keadaan or {}), formation_faktor=formation, output_teks=output_teks, act=act, alasan_act=alasan_act).to_dict`, `dict`
- L1351–1376 **`analisis_ujaran`** · kontrol=4, assignment/delete=9, except=0 · Call: `_kata_tokens`, `cakupan_negasi`, `deteksi_bahasa`, `ekstrak_entitas`, `ekstrak_topik`, `jenis_kalimat`, `jenis_pertanyaan`, `max`, `periksa_gramatika`, `round`, `skor.items`, `stem`, `str`, `tindak_tutur_skor`, `tokenisasi`, `urai_subjek_predikat`

## `pycos/bahasa/tutur.py`

SHA-256: `87d8d6ecd588b9a2bb73026fa0caea01968b993006d78bd1d5913acb64091e04`

3071 baris; 17 kelas; 100 fungsi/metode termasuk nested.

Kelas: `Lattice` L85, `Leksikon` L149, `Arg` L355, `Node` L376, `GenContext` L397, `Tutur` L459, `L0` L473, `Slot` L747, `Kerangka` L761, `L1` L769, `L2` L887, `L3` L1156, `Orkestrator` L1944, `SASPAnalyzer` L2067, `TuturEngine` L2400, `LeksikonCiri` L2742, `FiturTutur` L2869.
Handler luas: 2508, 2545, 2565, 2578, 2587, 2598, 2516, 2526, 2539, 2553, 1765, 1774, 2499, 2607.

Impor (termasuk lazy/TYPE_CHECKING): `from __future__ import annotations`; `from dataclasses import dataclass, field`; `from pycos.bahasa import teks as _teks_mod`; `from pycos.bahasa.teks import IDIOM_SENTIMEN as _IDIOM`; `from pycos.bahasa.teks import cakupan_negasi as _cakupan_negasi, jenis_kalimat as _jenis_kalimat_teks, kandidat_dasar as _kandidat_dasar_teks, pecah_kalimat as _pecah_kalimat, periksa_gramatika as _periksa_gramatika, potong_batas_kata as _potong_batas_kata, stem as _stem_teks, tokenisasi as _tokenisasi_teks, urai_subjek_predikat as _urai_subjek_predikat`; `from pycos.bahasa.teks import cakupan_negasi as _cn, jenis_kalimat as _jk, jenis_pertanyaan as _jp, tokenisasi as _tk, urai_subjek_predikat as _usp, ekstrak_entitas as _ee, ekstrak_topik as _et`; `from pycos.bahasa.teks import ekstrak_topik as _et`; `from pycos.bahasa.teks import ekstrak_topik as _et2`; `from pycos.bahasa.teks import ekstrak_topik as _et3`; `from pycos.bahasa.teks import ekstrak_topik as _et4`; `from pycos.bahasa.teks import ekstrak_topik as _et5`; `from pycos.bahasa.teks import jejak_pembentukan as _jejak`; `from pycos.bahasa.teks import stem as _stem`; `from pycos.bahasa.teks import stem as _stem_b11`; `from pycos.bahasa.teks import stem as _stem_b7`; `from pycos.bahasa.teks import stem as _stem_b7mg`; `from pycos.bahasa.teks import tindak_tutur_skor as _tts`; `from pycos.kontrak import hanya_kunci, teks_wajib`; `from typing import Any, Dict, FrozenSet, List, Mapping, Optional, Sequence, Tuple, cast`; `import json`; `import math`; `import os`; `import random`; `import re`; `import re as _re_b11`; `import re as _re_b11p`; `import re as _re_e8`; `import re as _re_mod`; `import threading`.

- L62–75 **`_clip`** · kontrol=2, assignment/delete=1, except=1 · Call: `float`
- L78–79 **`_norm`** · kontrol=1, assignment/delete=0, except=0 · Call: `' '.join`, `str`, `str(s or '').strip`, `str(s or '').strip().lower`, `str(s or '').strip().lower().split`
- L86–87 **`Lattice.__init__`** · kontrol=0, assignment/delete=1, except=0 · Call: `dict`
- L89–102 **`Lattice.subtipe`** · kontrol=5, assignment/delete=6, except=0 · Call: `self.peta.get`, `str`, `str(a).upper`, `str(b).upper`
- L104–111 **`Lattice.cocok`** · kontrol=4, assignment/delete=0, except=0 · Call: `self.subtipe`, `str`
- L150–196 **`Leksikon.__init__`** · kontrol=13, assignment/delete=19, except=0 · Call: `Lattice`, `dict`, `dok.get`, `e.get`, `list`, `peta.get`, `peta.setdefault`, `self._by_kelas.setdefault`, `self._by_kelas.setdefault(k, []).append`, `self._by_lema.setdefault`, `self._by_tipe.setdefault`, `self._by_tipe.setdefault(t, []).append`, `self._senses.setdefault`, `self._senses.setdefault(kunci, []).append`
- L198–199 **`Leksikon.ambil`** · kontrol=0, assignment/delete=0, except=0 · Call: `_norm`, `self._by_lema.get`
- L201–240 **`Leksikon.pilih_makna`** · kontrol=25, assignment/delete=15, except=1 · Call: `any`, `e.get`, `float`, `id`, `len`, `list`, `max`, `self.senses`, `set`
- L242–247 **`Leksikon.kandidat`** · kontrol=2, assignment/delete=1, except=0 · Call: `out.append`, `self._by_kelas.get`
- L249–251 **`Leksikon.senses`** · kontrol=0, assignment/delete=0, except=0 · Call: `_norm`, `list`, `self._senses.get`
- L253–259 **`Leksikon.kelas_dari`** · kontrol=3, assignment/delete=1, except=0 · Call: `e.get`, `out.append`, `self.senses`
- L261–267 **`Leksikon.tipe_dari`** · kontrol=3, assignment/delete=1, except=0 · Call: `e.get`, `out.append`, `self.senses`
- L270–329 **`Leksikon.nasalisasi`** · kontrol=23, assignment/delete=4, except=0 · Call: `_norm`, `e.get`, `len`, `re.findall`, `self.ambil`
- L331–337 **`Leksikon.nominalisasi`** · kontrol=3, assignment/delete=2, except=0 · Call: `(e.get('afiks') or {}).get`, `cast`, `e.get`, `self.ambil`
- L339–340 **`Leksikon.adjektiva_dasar`** · kontrol=0, assignment/delete=0, except=0 · Call: `_norm`
- L346–351 **`_pertahankan_kapitalisasi`** · kontrol=3, assignment/delete=1, except=0 · Call: `' '.join`, `any`, `ch.isupper`, `mentah.lower`, `str`, `str(s or '').strip`, `str(s or '').strip().split`
- L371–372 **`Arg.kosong`** · kontrol=1, assignment/delete=0, except=0 · Call: tidak ada
- L389–393 **`Node.arg`** · kontrol=2, assignment/delete=0, except=0 · Call: tidak ada
- L452–455 **`GenContext.topik_aktif`** · kontrol=2, assignment/delete=1, except=0 · Call: `' '.join`, `any`, `ch.isupper`, `mentah.lower`, `str`, `str(self.topik or '').split`
- L465–467 **`Tutur.to_dict`** · kontrol=0, assignment/delete=0, except=0 · Call: tidak ada
- L476–477 **`L0.__init__`** · kontrol=0, assignment/delete=1, except=0 · Call: tidak ada
- L488–502 **`L0._mungkin_ekspresif`** · kontrol=5, assignment/delete=2, except=0 · Call: `self.EKSPRESI_PAKAI.get`
- L506–511 **`L0._episode`** · kontrol=2, assignment/delete=0, except=0 · Call: `len`, `min`
- L513–740 **`L0.rencana`** · kontrol=53, assignment/delete=25, except=0 · Call: `Arg`, `Node`, `_clip`, `_norm`, `ctx.topik_aktif`, `node.args.append`, `self._episode`, `self._mungkin_ekspresif`, `str`, `turun.append`
- L770–771 **`L1.__init__`** · kontrol=0, assignment/delete=1, except=0 · Call: tidak ada
- L773–881 **`L1.realisasi`** · kontrol=42, assignment/delete=28, except=0 · Call: `','.join`, `Kerangka`, `Slot`, `_norm`, `a.kosong`, `alias.get`, `any`, `bool`, `catatan.append`, `ctx.topik_aktif`, `float`, `isinstance`, `list`, `node.arg`, `s.get`, `self.leks.lattice.cocok`, `self.leks.predikat.get`, `self.leks.tipe_dari`, `sisa.remove`, `slots.append`, `spec.get`
- L901–906 **`L2.__init__`** · kontrol=0, assignment/delete=4, except=0 · Call: tidak ada
- L909–919 **`L2._lolos_hard`** · kontrol=7, assignment/delete=0, except=0 · Call: `e.get`, `self.leks.lattice.cocok`
- L922–1016 **`L2._skor`** · kontrol=40, assignment/delete=40, except=0 · Call: `_clip`, `_norm`, `_norm(str(teks or '')).split`, `abs`, `any`, `bool`, `ctx.topik_aktif`, `e.get`, `entri_prev.get`, `enumerate`, `float`, `konteks_kata.add`, `len`, `list`, `max`, `min`, `reversed`, `self.leks.ambil`, `set`, `str`, `w.strip`
- L1018–1043 **`L2._pilih_beragam`** · kontrol=7, assignment/delete=9, except=0 · Call: `info.update`, `len`, `math.exp`, `round`, `self.riwayat.append`, `self.rng.choices`, `set`, `terlihat.add`, `unik.append`
- L1053–1072 **`L2._pilih_dalam`** · kontrol=3, assignment/delete=6, except=0 · Call: `info['dibuang'].get`, `len`, `lolos.append`, `lolos.sort`, `self._lolos_hard`, `self._pilih_beragam`, `self._skor`
- L1077–1121 **`L2.pilih_predikat`** · kontrol=18, assignment/delete=18, except=0 · Call: `Slot`, `e.get`, `float`, `len`, `min`, `self.PRED_AKSI.get`, `self.PRED_KUTUB.get`, `self.PRED_TIPE.get`, `self._lolos_hard`, `self._pilih_dalam`, `self._skor`, `self.leks.kandidat`, `self.pilih`, `self.riwayat.append`, `self.rng.random`, `self.rng.randrange`, `sorted`
- L1123–1142 **`L2.pilih`** · kontrol=3, assignment/delete=9, except=0 · Call: `info['dibuang'].get`, `len`, `lolos.append`, `lolos.sort`, `self._lolos_hard`, `self._pilih_beragam`, `self._skor`, `self.leks.kandidat`
- L1157–1159 **`L3.__init__`** · kontrol=0, assignment/delete=2, except=0 · Call: tidak ada
- L1162–1183 **`L3.bentuk_verba`** · kontrol=9, assignment/delete=2, except=0 · Call: `_norm`, `self.leks.nasalisasi`, `self.leks.nominalisasi`
- L1185–1196 **`L3.bentuk_partikel`** · kontrol=2, assignment/delete=1, except=0 · Call: `partikel.lstrip`
- L1199–1267 **`L3.frasa_nomina`** · kontrol=27, assignment/delete=11, except=0 · Call: `_norm`, `_norm(x).split`, `_pertahankan_kapitalisasi`, `any`, `ch.isupper`, `e.get`, `isinstance`, `len`, `s.endswith`, `self.bentuk_partikel`, `self.klausa`, `self.leks.ambil`, `set`, `str`, `tuple`
- L1269–1294 **`L3.frasa_adjektiva`** · kontrol=17, assignment/delete=7, except=0 · Call: `(e['modifier'].get('pelemah') or {}).get`, `(e['modifier'].get('penguat') or {}).get`, `_clip`, `_norm`, `e.get`, `e['modifier'].get`, `isinstance`, `self.leks.ambil`, `self.rng.choice`, `str`
- L1297–1310 **`L3._placeholder`** · kontrol=3, assignment/delete=5, except=0 · Call: `out.append`, `template.find`
- L1312–1347 **`L3._render_ekspresi`** · kontrol=16, assignment/delete=13, except=0 · Call: `' '.join`, `' '.join(out.split()).replace`, `' '.join(out.split()).replace(' .', '.').replace`, `all`, `b.items`, `cast`, `eks.get`, `eks.values`, `isinstance`, `iter`, `list`, `next`, `node.predikat.lower`, `out.find`, `out.replace`, `out.rstrip`, `out.rstrip().endswith`, `out.split`, `self._placeholder`, `self.rng.choice`, `spec.get`
- L1350–1352 **`L3._dasar`** · kontrol=0, assignment/delete=0, except=0 · Call: `_stem`, `lema.split`
- L1354–1373 **`L3._verba`** · kontrol=7, assignment/delete=1, except=0 · Call: `(self.leks.predikat.get(node.predikat) or {}).get`, `_norm`, `lema.startswith`, `node.predikat.lower`, `self._dasar`, `self.bentuk_verba`, `self.leks.nasalisasi`, `self.leks.predikat.get`
- L1375–1402 **`L3._diatesis_objek`** · kontrol=10, assignment/delete=6, except=0 · Call: `_norm`
- L1405–1454 **`L3.klausa`** · kontrol=13, assignment/delete=14, except=0 · Call: `_et`, `_norm`, `_pertahankan_kapitalisasi`, `_pertahankan_kapitalisasi(str(a.literal or a.peran or '')).strip`, `a.kosong`, `getattr`, `inti.rstrip`, `inti.rstrip().endswith`, `isinstance`, `node.predikat.lower`, `self._kalimat_predikat`, `self.frasa_adjektiva`, `self.frasa_nomina`, `self.klausa`, `self.klausa(a.isi, ctx, nested=True).rstrip`, `self.leks.predikat.get`, `spec.get`, `str`
- L1456–1709 **`L3._kalimat_predikat`** · kontrol=110, assignment/delete=71, except=0 · Call: `P.lower`, `_et2`, `_et3`, `_et4`, `_et5`, `_norm`, `_stem_b7`, `_stem_b7mg`, `any`, `b.get`, `ch.isupper`, `getattr`, `kal.endswith`, `node.arg`, `pred.endswith`, `self._diatesis_objek`, `self._render_ekspresi`, `self._verba`, `self.leks.predikat.get`, `self.rng.choice`, `spec.get`, `spec_eks.get`, `st.count`, `str`, `str(sebab).strip`, `str(sebab).strip().rstrip`, `topik.rstrip`, `topik.rstrip().endswith`, `uj.endswith`, `{'karena': 'because', 'sebab': 'because', 'bahwa': 'that'}.get`, `{'karena': 'because', 'sebab': 'because', 'terhadap': 'about', 'soal': 'about', 'pada': 'about', 'tentang': 'about', 'kepada': 'to', 'akan': 'will', 'untuk': 'for'}.get`, `{'sebab': 'karena', 'konsesi': 'meski', 'kontras': 'tapi', 'urutan': 'lalu', 'elaborasi': 'soalnya'}.get`
- L1717–1745 **`L3._penanda_aspek_modal`** · kontrol=7, assignment/delete=7, except=0 · Call: `self._PENANDA_ASPEK.get`
- L1747–1789 **`L3._sisipkan_penanda`** · kontrol=14, assignment/delete=9, except=2 · Call: `_norm`, `_re_b11.escape`, `_re_b11.match`, `_re_b11.search`, `_re_b11p.search`, `_stem_b11`, `dasar_norm.split`, `dasar_norm.startswith`, `kandidat.append`, `m.end`, `m.start`, `node.predikat.lower`, `self._penanda_aspek_modal`, `self.leks.nasalisasi`, `self.leks.predikat.get`, `spec.get`
- L1791–1827 **`L3._variasikan_struktur`** · kontrol=10, assignment/delete=7, except=0 · Call: `(verb + ' ' + m_subj.group(1) + (' ' + sisa2 if sisa2 else '')).strip`, `_re_mod.match`, `abs`, `bool`, `m_subj.end`, `m_subj.group`, `m_verb.end`, `m_verb.group`, `m_verb.group(1).startswith`, `self.rng.random`, `sisa[m_verb.end():].lstrip`
- L1829–1884 **`L3._sisipkan_partikel`** · kontrol=27, assignment/delete=10, except=0 · Call: `_norm`, `_re_mod.match`, `len`, `m.group`, `m.group(1).rstrip`, `self.rng.choice`, `self.rng.random`, `str`, `str(e).upper`, `teks.split`, `tersedia.append`
- L1886–1938 **`L3.linearisasi`** · kontrol=18, assignment/delete=20, except=0 · Call: `_norm`, `_re_e8.escape`, `_re_e8.sub`, `ctx.topik_aktif`, `inti.rstrip`, `inti.split`, `isinstance`, `node.arg`, `self._sisipkan_partikel`, `self._sisipkan_penanda`, `self._variasikan_struktur`, `self.klausa`, `set`, `str`, `str(arg.tipe or '').upper`, `str(arg.tipe or '').upper().split`, `str(ctx.sapaan[0]).strip`, `str(ctx.sapaan[0]).strip().rstrip`, `w.strip`
- L1947–1954 **`Orkestrator.__init__`** · kontrol=0, assignment/delete=6, except=0 · Call: `L0`, `L1`
- L1957–1962 **`Orkestrator._stabil`** · kontrol=1, assignment/delete=2, except=0 · Call: `ord`, `str`
- L1964–1966 **`Orkestrator._rng`** · kontrol=0, assignment/delete=0, except=0 · Call: `random.Random`, `self._stabil`
- L1968–2061 **`Orkestrator.bangun`** · kontrol=24, assignment/delete=20, except=0 · Call: `L2`, `L3`, `Node`, `Tutur`, `_jejak`, `_norm`, `_periksa_gramatika`, `alternatif.append`, `enumerate`, `isinstance`, `len`, `list`, `range`, `rng.shuffle`, `self._l2.pilih`, `self._l2.pilih_predikat`, `self._l3.linearisasi`, `self._rng`, `self.l0.rencana`, `self.l1.realisasi`, `teks.strip`, `trace.append`
- L2098–2103 **`SASPAnalyzer.__init__`** · kontrol=1, assignment/delete=4, except=0 · Call: `str`
- L2106–2111 **`SASPAnalyzer._konteks`** · kontrol=2, assignment/delete=0, except=0 · Call: `dict`, `isinstance`, `str`
- L2114–2115 **`SASPAnalyzer._bool`** · kontrol=1, assignment/delete=0, except=0 · Call: `any`, `bool`, `konteks.get`
- L2118–2133 **`SASPAnalyzer._available`** · kontrol=6, assignment/delete=3, except=1 · Call: `hasil.append`, `isinstance`, `item.get`, `konteks.get`, `raw.lower`, `str`, `str(item).lower`
- L2135–2150 **`SASPAnalyzer._leksikal`** · kontrol=3, assignment/delete=2, except=0 · Call: `ent.get`, `hasil.append`, `list`, `self.leksikon.ambil`
- L2152–2206 **`SASPAnalyzer._semantik`** · kontrol=13, assignment/delete=18, except=0 · Call: `' '.join`, `_cn`, `_ee`, `_et`, `_jk`, `_jp`, `_tk`, `_usp`, `any`, `enumerate`, `len`, `min`, `next`, `round`, `self._leksikal`, `urai.get`, `w.startswith`
- L2208–2317 **`SASPAnalyzer._pragmatik`** · kontrol=33, assignment/delete=28, except=0 · Call: `' '.join`, `_tts`, `any`, `bool`, `bukti.append`, `konteks.get`, `low.startswith`, `maksud.append`, `min`, `pilihan.append`, `proposisi.get`, `round`, `self._available`, `self._bool`, `semantik.get`, `skor_tindak.items`, `sorted`, `str`
- L2319–2323 **`SASPAnalyzer.analisis_literal`** · kontrol=2, assignment/delete=2, except=0 · Call: `self._TOKEN.findall`, `self._semantik`, `str`, `str(ujaran or '').strip`, `w.lower`
- L2328–2335 **`SASPAnalyzer.analisis_pragmatik`** · kontrol=2, assignment/delete=3, except=0 · Call: `dict`, `isinstance`, `self._TOKEN.findall`, `self._konteks`, `self._pragmatik`, `self.analisis_literal`, `str`, `str(ujaran or '').strip`, `w.lower`
- L2341–2346 **`SASPAnalyzer.analisis_tindak_tutur`** · kontrol=0, assignment/delete=1, except=0 · Call: `prag.get`, `self.analisis_pragmatik`
- L2350–2359 **`SASPAnalyzer.analisis`** · kontrol=1, assignment/delete=6, except=0 · Call: `self.analisis_literal`, `self.analisis_pragmatik`, `str`, `str(ujaran or '').strip`
- L2376–2391 **`muat_leksikon`** · kontrol=7, assignment/delete=7, except=0 · Call: `Leksikon`, `_CACHE_LEKSIKON.get`, `json.load`, `open`, `os.path.realpath`, `os.stat`
- L2394–2397 **`kosongkan_cache_leksikon`** · kontrol=1, assignment/delete=0, except=0 · Call: `_CACHE_LEKSIKON.clear`
- L2401–2412 **`TuturEngine.__init__`** · kontrol=3, assignment/delete=8, except=0 · Call: `SASPAnalyzer`, `muat_leksikon`, `os.path.exists`
- L2414–2415 **`TuturEngine.tersedia`** · kontrol=0, assignment/delete=0, except=0 · Call: tidak ada
- L2417–2421 **`TuturEngine.info`** · kontrol=1, assignment/delete=0, except=0 · Call: `len`
- L2423–2430 **`TuturEngine.ucap`** · kontrol=2, assignment/delete=3, except=0 · Call: `Orkestrator`, `self.orkestrator.bangun`
- L2432–2435 **`TuturEngine.analisis_sa_sp`** · kontrol=0, assignment/delete=0, except=0 · Call: `self.analis_sa_sp.analisis`
- L2439–2440 **`TuturEngine.analisis_literal_sa_sp`** · kontrol=0, assignment/delete=0, except=0 · Call: `self.analis_sa_sp.analisis_literal`
- L2444–2446 **`TuturEngine.analisis_pragmatik_sa_sp`** · kontrol=0, assignment/delete=0, except=0 · Call: `self.analis_sa_sp.analisis_pragmatik`
- L2451–2453 **`TuturEngine.to_dict`** · kontrol=0, assignment/delete=0, except=0 · Call: `list`
- L2455–2465 **`TuturEngine.muat_dict`** · kontrol=4, assignment/delete=4, except=0 · Call: `ValueError`, `data.get`, `isinstance`, `list`, `str`
- L2468–2471 **`sa_sp`** · kontrol=0, assignment/delete=0, except=0 · Call: `SASPAnalyzer`, `SASPAnalyzer(leksikon).analisis`
- L2474–2477 **`sa_sp_literal`** · kontrol=0, assignment/delete=0, except=0 · Call: `SASPAnalyzer`, `SASPAnalyzer(leksikon).analisis_literal`
- L2480–2483 **`sa_sp_pragmatik`** · kontrol=0, assignment/delete=0, except=0 · Call: `SASPAnalyzer`, `SASPAnalyzer(leksikon).analisis_pragmatik`
- L2489–2699 **`konteks_dari_presentasi`** · kontrol=78, assignment/delete=71, except=13 · Call: `(getattr(ks, 'values', {}) or {}).items`, `GenContext`, `_call`, `_clip`, `_daftar_str`, `_teks_persona`, `atensi.get`, `c.get`, `callable`, `dict`, `emosi_lbl.append`, `es.items`, `es.values`, `float`, `fn`, `fn_ap`, `fs.items`, `fs_attr`, `getattr`, `hasattr`, `int`, `isinstance`, `ks.attention_state`, `ks.withholding_state`, `n.emosi_state`, `nilai.strip`, `p.naluri.mood`, `ref.get`, `reg_p.strip`, `reg_p.strip().lower`, `sorted`, `st.get`, `str`, `str(nama).upper`, `str(sumber.get('bahasa', '') or '').strip`, `str(sumber.get('bahasa', '') or '').strip().lower`, `str(x).strip`, `sum`, `sumber.get`, `tubuh_lbl.append`, `tuple`, `ws.get`, `x.get`
- L2494–2501 **`konteks_dari_presentasi._call`** · kontrol=2, assignment/delete=1, except=1 · Call: `callable`, `fn`, `getattr`
- L2648–2655 **`konteks_dari_presentasi._daftar_str`** · kontrol=3, assignment/delete=1, except=1 · Call: `getattr`, `isinstance`, `nilai.strip`, `str`, `str(x).strip`, `tuple`
- L2657–2663 **`konteks_dari_presentasi._teks_persona`** · kontrol=3, assignment/delete=1, except=0 · Call: `getattr`, `isinstance`, `nilai.strip`, `str`
- L2737–2738 **`_fs`** · kontrol=0, assignment/delete=0, except=0 · Call: `frozenset`
- L2754–2773 **`LeksikonCiri.from_dict`** · kontrol=6, assignment/delete=5, except=0 · Call: `'kata di {} harus satu token, bukan frasa: {!r}'.format`, `'kata di {}'.format`, `'kategori {!r} harus daftar string'.format`, `'leksikon wajib memuat kategori {!r}'.format`, `ValueError`, `cls`, `dict`, `frozenset`, `hanya_kunci`, `isinstance`, `kata.split`, `kata_kata.append`, `len`, `teks_wajib`, `teks_wajib(k, 'kata di {}'.format(kategori)).lower`
- L2776–2778 **`LeksikonCiri.dari_berkas`** · kontrol=1, assignment/delete=0, except=0 · Call: `cls.from_dict`, `json.load`, `open`
- L2780–2781 **`LeksikonCiri.to_dict`** · kontrol=1, assignment/delete=0, except=0 · Call: `getattr`, `sorted`
- L2783–2794 **`LeksikonCiri.kanonik`** · kontrol=2, assignment/delete=1, except=0 · Call: `_kandidat_dasar`, `getattr`
- L2807–2813 **`_kandidat_dasar`** · kontrol=0, assignment/delete=0, except=0 · Call: `_kandidat_dasar_teks`
- L2816–2818 **`stem_kata`** · kontrol=0, assignment/delete=0, except=0 · Call: `_stem_teks`
- L2882–2886 **`FiturTutur.polaritas`** · kontrol=1, assignment/delete=1, except=0 · Call: tidak ada
- L2888–2892 **`FiturTutur.formalitas`** · kontrol=1, assignment/delete=1, except=0 · Call: tidak ada
- L2894–2899 **`FiturTutur.intensitas`** · kontrol=1, assignment/delete=1, except=0 · Call: `min`
- L2901–2904 **`FiturTutur.keraguan`** · kontrol=1, assignment/delete=0, except=0 · Call: `min`
- L2907–2919 **`_tokenkan`** · kontrol=4, assignment/delete=1, except=0 · Call: `_tokenisasi_teks`, `keluar.append`
- L2922–2923 **`_kata_saja`** · kontrol=1, assignment/delete=0, except=0 · Call: tidak ada
- L2926–3023 **`_sentimen`** · kontrol=37, assignment/delete=28, except=0 · Call: `' '.join`, `_IDIOM.items`, `_cakupan_negasi`, `_teks_mod.Token`, `dikonsumsi.add`, `enumerate`, `frasa.split`, `klausa_id.append`, `leksikon.kanonik`, `len`, `max`, `range`, `set`
- L3026–3027 **`_hitung`** · kontrol=1, assignment/delete=0, except=0 · Call: `leksikon.kanonik`, `sum`
- L3030–3052 **`analisis_teks`** · kontrol=5, assignment/delete=6, except=0 · Call: `'teks harus string, dapat {}'.format`, `FiturTutur`, `TypeError`, `_hitung`, `_kata_saja`, `_sentimen`, `_tokenkan`, `c.isalpha`, `c.isupper`, `isinstance`, `len`, `sum`, `teks.count`, `type`
- L3058–3063 **`token_dari`** · kontrol=2, assignment/delete=0, except=0 · Call: `_TOKEN_MENTAH.finditer`, `m.group`, `m.group(0).lower`, `str`

## `pycos/dukungan/__init__.py`

SHA-256: `b50434ada1d692de398fcb08ddf936e46336313c3364c887c46fc384f6acf18e`

58 baris; 0 kelas; 2 fungsi/metode termasuk nested.

Kelas: tidak ada.
Handler luas: tidak ada.

Impor (termasuk lazy/TYPE_CHECKING): `from .konstanta import DRIVES`; `from .patching import PatchConflictError, inventaris, install_method, install_methods, optional_module, wrap_method`; `from .sumber import NAMA_KORPUS, NAMA_LEKSIKON, akar_paket, ada_sumber_daya, jalur_korpus, kandidat_leksikon, jalur_leksikon, sumber_daya`; `from __future__ import annotations`; `from importlib import import_module`; `from typing import TYPE_CHECKING, Any, Dict, List`.

- L46–54 **`__getattr__`** · kontrol=1, assignment/delete=3, except=0 · Call: `'paket {!r} tidak punya atribut {!r}'.format`, `'{}.{}'.format`, `AttributeError`, `_SUBMODUL.get`, `getattr`, `globals`, `import_module`
- L57–58 **`__dir__`** · kontrol=0, assignment/delete=0, except=0 · Call: `globals`, `set`, `sorted`

## `pycos/dukungan/batas_memori.py`

SHA-256: `ef1eb44621d39a7e70e75746af8db8cec6fc860f37d401a1e821a521f5ca250a`

40 baris; 0 kelas; 2 fungsi/metode termasuk nested.

Kelas: tidak ada.
Handler luas: tidak ada.

Impor (termasuk lazy/TYPE_CHECKING): `from __future__ import annotations`; `from typing import Any, Dict, List, Optional`.

- L25–33 **`batas`** · kontrol=5, assignment/delete=1, except=0 · Call: `'BATAS[{}] harus integer non-negatif'.format`, `'BATAS[{}] wajib integer non-negatif'.format`, `ValueError`, `isinstance`, `min`
- L36–40 **`pangkas`** · kontrol=1, assignment/delete=2, except=0 · Call: `batas`, `len`

## `pycos/dukungan/diagnostik.py`

SHA-256: `7e5c6364a0171c73a57743229ac4cbb1dbc2e7d335c01ef866389c9dc65c552a`

61 baris; 0 kelas; 3 fungsi/metode termasuk nested.

Kelas: tidak ada.
Handler luas: 45.

Impor (termasuk lazy/TYPE_CHECKING): `from __future__ import annotations`; `from collections import deque`; `from copy import deepcopy`; `from typing import Any, Deque, Dict`; `import threading`; `import time`.

- L35–46 **`catat`** · kontrol=4, assignment/delete=3, except=1 · Call: `_CATATAN.append`, `_TOTAL.get`, `detail.items`, `round`, `str`, `time.time`
- L49–55 **`laporan`** · kontrol=1, assignment/delete=0, except=0 · Call: `_TOTAL.items`, `_TOTAL.values`, `deepcopy`, `dict`, `list`, `sorted`, `sum`
- L58–61 **`kosongkan`** · kontrol=1, assignment/delete=0, except=0 · Call: `_CATATAN.clear`, `_TOTAL.clear`

## `pycos/dukungan/konstanta.py`

SHA-256: `a82cf846b366f3e1bc232dc3715896176f32bf53beb111400375d99bda769d4c`

10 baris; 0 kelas; 0 fungsi/metode termasuk nested.

Kelas: tidak ada.
Handler luas: tidak ada.

Impor (termasuk lazy/TYPE_CHECKING): `from __future__ import annotations`; `from typing import Tuple`.


## `pycos/dukungan/leksikon.py`

SHA-256: `12b997d5856e0b9a5da8c485cdbc0f01b965008426ec9232e23305df804f52e5`

125 baris; 0 kelas; 5 fungsi/metode termasuk nested.

Kelas: tidak ada.
Handler luas: tidak ada.

Impor (termasuk lazy/TYPE_CHECKING): `from __future__ import annotations`; `from copy import deepcopy`; `from functools import lru_cache`; `from pycos.bahasa.tutur import LEKSIKON_CIRI_BAWAAN`; `from pycos.dukungan.sumber import jalur_leksikon`; `from pycos.inti.naluri import LEXICON, LEXICON_EN, TAG_LEXICON, TAG_LEXICON_EN`; `from pycos.kontrak import DRIVE_KEYS, angka`; `from typing import Any, Dict, List, Optional`; `import argparse`; `import hashlib`; `import json`.

- L16–29 **`validasi_entri`** · kontrol=9, assignment/delete=0, except=0 · Call: `'[{}] harus vektor non-kosong'.format`, `'[{}] tidak boleh seluruhnya nol'.format`, `'[{}]: drive tidak dikenal: {}'.format`, `'[{}][{}]'.format`, `ValueError`, `angka`, `any`, `data.items`, `isinstance`, `kata.strip`, `vector.items`, `vector.values`
- L33–40 **`_dokumen`** · kontrol=4, assignment/delete=1, except=0 · Call: `ValueError`, `data.get`, `isinstance`, `jalur_leksikon`, `json.load`, `lru_cache`, `open`, `validasi_entri`
- L43–47 **`perluas`** · kontrol=2, assignment/delete=0, except=0 · Call: `_dokumen`, `_dokumen()['entri'][lang].items`, `deepcopy`, `target.setdefault`
- L50–108 **`periksa`** · kontrol=26, assignment/delete=10, except=0 · Call: `"konflik tanda: '{}' negatif di daftar ciri, tetapi valensi {} di leksikon".format`, `"konflik tanda: '{}' positif di daftar ciri, tetapi semua valensi {} di leksikon".format`, `ValueError`, `_dokumen`, `all`, `dict`, `e.get`, `entri.get`, `expected[lang].setdefault`, `f.read`, `float`, `hashlib.sha256`, `hashlib.sha256(raw).hexdigest`, `jalur_leksikon`, `json.loads`, `len`, `open`, `peta_valensi.get`, `peta_valensi.setdefault`, `peta_valensi.setdefault(str(e.get('lema', '')).lower(), []).append`, `str`, `str(e.get('lema', '')).lower`, `str(kata).lower`, `sum`, `validasi_entri`
- L111–121 **`main`** · kontrol=1, assignment/delete=2, except=1 · Call: `argparse.ArgumentParser`, `json.dumps`, `parser.add_argument`, `parser.parse_args`, `periksa`, `print`, `str`

## `pycos/dukungan/numerik.py`

SHA-256: `04bec041146b25531e7619ea42a2f061cfce4872346263e4f73d37895ccb6c6d`

84 baris; 0 kelas; 4 fungsi/metode termasuk nested.

Kelas: tidak ada.
Handler luas: tidak ada.

Impor (termasuk lazy/TYPE_CHECKING): `from __future__ import annotations`; `from typing import Any`; `import math`.

- L42–57 **`jepit`** · kontrol=5, assignment/delete=4, except=1 · Call: `float`, `isinstance`
- L60–62 **`jepit_drive`** · kontrol=0, assignment/delete=0, except=0 · Call: `jepit`
- L65–67 **`jepit_01`** · kontrol=0, assignment/delete=0, except=0 · Call: `jepit`
- L70–84 **`float_hingga`** · kontrol=3, assignment/delete=1, except=1 · Call: `'{} harus angka, bukan bool'.format`, `'{} harus angka, dapat {!r}'.format`, `'{} harus berhingga, dapat {!r}'.format`, `ValueError`, `float`, `isinstance`, `math.isfinite`

## `pycos/dukungan/parameter.py`

SHA-256: `cc3db2209db2a058029091611b0e90eb16a31424fe2ec4548557b295b259b462`

52 baris; 0 kelas; 1 fungsi/metode termasuk nested.

Kelas: tidak ada.
Handler luas: tidak ada.

Impor (termasuk lazy/TYPE_CHECKING): `from __future__ import annotations`; `from collections.abc import Mapping`; `from pycos.inti.naluri import DEFAULTS`; `from pycos.kontrak import angka`; `from typing import Any, Dict, Optional, Tuple`.

- L34–52 **`periksa_params`** · kontrol=8, assignment/delete=2, except=0 · Call: `'params[{!r}]'.format`, `ValueError`, `angka`, `isinstance`, `params.items`, `type`

## `pycos/dukungan/patching.py`

SHA-256: `1ffb32fd0d0abe7589e59048773104a8adfd8be3d72951b5e1ce0ebc8aba9104`

266 baris; 1 kelas; 12 fungsi/metode termasuk nested.

Kelas: `PatchConflictError` L60.
Handler luas: 175, 228, 181, 190.

Impor (termasuk lazy/TYPE_CHECKING): `from __future__ import annotations`; `from functools import update_wrapper`; `from pycos.dukungan import diagnostik`; `from threading import RLock`; `from typing import Any, Callable, Dict, Iterable, List, Mapping, Tuple, Union`; `from weakref import WeakValueDictionary`; `import importlib`; `import inspect`.

- L25–35 **`_modul_absen`** · kontrol=2, assignment/delete=1, except=0 · Call: `getattr`, `nama.startswith`
- L38–57 **`optional_module`** · kontrol=7, assignment/delete=0, except=2 · Call: `'{}.{}'.format`, `ValueError`, `_modul_absen`, `importlib.import_module`, `isinstance`, `name.strip`
- L64–70 **`_validate_target`** · kontrol=5, assignment/delete=0, except=0 · Call: `'nama metode patch tidak valid: {!r}'.format`, `TypeError`, `ValueError`, `isinstance`, `name.isidentifier`, `patch_id.strip`
- L73–77 **`_unwrap_descriptor`** · kontrol=1, assignment/delete=0, except=0 · Call: `isinstance`, `type`
- L80–83 **`_patch_ids`** · kontrol=0, assignment/delete=2, except=0 · Call: `_unwrap_descriptor`, `getattr`, `isinstance`, `tuple`
- L86–95 **`_tag`** · kontrol=3, assignment/delete=1, except=0 · Call: `getattr`, `ids.append`, `list`, `setattr`, `tuple`
- L98–102 **`_conflict`** · kontrol=0, assignment/delete=0, except=0 · Call: `'patch {!r} tidak dipasang: {}.{}.{} sudah memiliki implementasi yang tidak dikelola patch ini'.format`, `PatchConflictError`
- L105–113 **`install_method`** · kontrol=0, assignment/delete=0, except=0 · Call: `bool`, `install_methods`
- L116–194 **`install_methods`** · kontrol=23, assignment/delete=12, except=3 · Call: `'{} harus callable'.format`, `'{}.{}'.format`, `TypeError`, `ValueError`, `_conflict`, `_patch_ids`, `_tag`, `_unwrap_descriptor`, `_validate_target`, `callable`, `delattr`, `descriptor_type`, `getattr`, `hasattr`, `id`, `inspect.getattr_static`, `installed.append`, `isinstance`, `len`, `list`, `methods.items`, `pending.append`, `prepared.append`, `retag.append`, `reversed`, `setattr`, `snapshots.setdefault`, `snapshots.values`, `tuple`
- L197–240 **`wrap_method`** · kontrol=6, assignment/delete=6, except=1 · Call: `'patch {!r} tidak dipasang: {}.{}.{} tidak ditemukan'.format`, `PatchConflictError`, `TypeError`, `_conflict`, `_patch_ids`, `_tag`, `_unwrap_descriptor`, `_validate_target`, `callable`, `descriptor_type`, `diagnostik.catat`, `id`, `inspect.getattr_static`, `setattr`, `update_wrapper`, `wrapper`
- L225–231 **`wrap_method.composed`** · kontrol=1, assignment/delete=0, except=1 · Call: `diagnostik.catat`, `wrapper`
- L243–266 **`inventaris`** · kontrol=5, assignment/delete=3, except=0 · Call: `_TARGETS.values`, `_patch_ids`, `_unwrap_descriptor`, `callable`, `hasil.append`, `list`, `sorted`, `vars`, `vars(target).items`

## `pycos/dukungan/periksa.py`

SHA-256: `3fed4e4c7823e8a80c01c399cdf9e048c2cf0cd4c85a4e545cfe2a99d2381f57`

277 baris; 0 kelas; 13 fungsi/metode termasuk nested.

Kelas: tidak ada.
Handler luas: 57, 130, 193, 245.

Impor (termasuk lazy/TYPE_CHECKING): `from __future__ import annotations`; `from pycos.bahasa.tutur import TuturEngine`; `from pycos.dukungan import diagnostik`; `from pycos.dukungan.patching import inventaris`; `from pycos.dukungan.sumber import jalur_korpus`; `from pycos.dukungan.sumber import jalur_leksikon`; `from pycos.inti.naluri import DRIVES`; `from pycos.inti.naluri import Naluri`; `from pycos.inti.persona import PERSONA_CONTOH, Keadaan`; `from pycos.kontrak import angka, hanya_kunci, teks_wajib`; `from pycos.kontrak import kontrak_operasi`; `from pycos.kontrak import verifikasi_startup`; `from pycos.refleksi.nurani import PelacakSelaras, nilai_selaras`; `from pycos.refleksi.nurani import laporan_kalibrasi, muat_korpus`; `from typing import Any, Callable, Dict, List, Optional, Tuple`; `import importlib`; `import json`; `import math`; `import os`.

- L52–59 **`_cek_impor`** · kontrol=2, assignment/delete=1, except=1 · Call: `'; '.join`, `'{} ({})'.format`, `gagal.append`, `importlib.import_module`, `type`
- L62–68 **`_cek_kontrak`** · kontrol=1, assignment/delete=1, except=0 · Call: `laporan.get`, `str`, `verifikasi_startup`
- L71–80 **`_cek_leksikon`** · kontrol=2, assignment/delete=2, except=0 · Call: `'TuturEngine.tersedia() = False untuk {}'.format`, `'berkas tidak ditemukan: {}'.format`, `TuturEngine`, `eng.tersedia`, `jalur_leksikon`, `os.path.isfile`
- L83–96 **`_cek_smoke_naluri`** · kontrol=4, assignment/delete=3, except=0 · Call: `'choose_action tidak memilih aksi: {!r}'.format`, `'reward_for menghasilkan nilai tak berhingga: {!r}'.format`, `Naluri`, `float`, `math.isfinite`, `npc.choose_action`, `npc.reward_for`, `npc.tick`, `pilihan.get`, `range`
- L99–108 **`_cek_determinisme`** · kontrol=2, assignment/delete=2, except=0 · Call: `'level berbeda untuk seed sama: {} vs {}'.format`, `Naluri`, `a.tick`, `b.tick`, `range`
- L111–134 **`_cek_validasi_input`** · kontrol=2, assignment/delete=2, except=2 · Call: `', '.join`, `'{} (galat {})'.format`, `Naluri`, `Naluri(rng_seed=1).choose_action`, `Naluri(rng_seed=1).tick`, `float`, `fungsi`, `lolos.append`, `type`
- L137–156 **`_cek_penilai`** · kontrol=3, assignment/delete=5, except=0 · Call: `'kontrak nilai_selaras fase {} bocor: {}'.format`, `Keadaan`, `PelacakSelaras`, `isinstance`, `kontrak_operasi`, `nilai_selaras`, `pelacak.catat`, `pelacak.tren`, `pelanggaran.get`
- L159–173 **`_cek_korpus`** · kontrol=4, assignment/delete=3, except=0 · Call: `'korpus contoh terlalu kecil: {} contoh'.format`, `'korpus contoh tidak ditemukan: {}'.format`, `isinstance`, `jalur_korpus`, `laporan_kalibrasi`, `len`, `muat_korpus`, `os.path.isfile`
- L176–197 **`_cek_validasi_batas`** · kontrol=2, assignment/delete=2, except=2 · Call: `', '.join`, `'{} (galat {})'.format`, `angka`, `float`, `fungsi`, `hanya_kunci`, `lolos.append`, `teks_wajib`, `type`
- L200–209 **`_cek_validasi_state`** · kontrol=2, assignment/delete=0, except=1 · Call: `Naluri.from_dict`
- L212–221 **`_cek_validasi_event`** · kontrol=2, assignment/delete=1, except=1 · Call: `Naluri`, `n.apply_events`
- L239–249 **`jalankan`** · kontrol=3, assignment/delete=3, except=1 · Call: `'{}: {}'.format`, `fungsi`, `hasil.append`, `type`
- L252–277 **`main_periksa`** · kontrol=5, assignment/delete=6, except=0 · Call: `'  [{}] {}{}'.format`, `'  {}.{} [{}]: {}'.format`, `'  {}: {}'.format`, `' -> '.join`, `'Diagnostik proses: {} catatan (bukan kegagalan cek otomatis)'.format`, `'Hasil: {}'.format`, `'Inventaris patch runtime: {} metode'.format`, `all`, `diagnostik.laporan`, `inventaris`, `jalankan`, `json.dumps`, `len`, `print`

## `pycos/dukungan/persistensi.py`

SHA-256: `34c0db9509e84a9dba828e871f97fc2f77c1cb94a3541d74280a45e783a58f78`

132 baris; 0 kelas; 7 fungsi/metode termasuk nested.

Kelas: tidak ada.
Handler luas: tidak ada.

Impor (termasuk lazy/TYPE_CHECKING): `from __future__ import annotations`; `from copy import deepcopy`; `from pycos.inti.naluri import DEFAULTS, LEXICON, TAG_LEXICON`; `from typing import Any, Dict`; `import hashlib`; `import hmac`; `import json`; `import os`; `import tempfile`.

- L19–21 **`_kanonik`** · kontrol=0, assignment/delete=0, except=0 · Call: `json.dumps`, `json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False).encode`
- L24–43 **`simpan_json`** · kontrol=4, assignment/delete=5, except=0 · Call: `ValueError`, `_kanonik`, `berkas.fileno`, `berkas.flush`, `berkas.write`, `dict`, `hashlib.sha256`, `hashlib.sha256(_kanonik(payload)).hexdigest`, `json.dumps`, `json.dumps(payload, ensure_ascii=False, allow_nan=False).encode`, `os.fdopen`, `os.fspath`, `os.fsync`, `os.path.abspath`, `os.path.basename`, `os.path.dirname`, `os.path.exists`, `os.replace`, `os.unlink`, `tempfile.mkstemp`
- L46–60 **`muat_json`** · kontrol=7, assignment/delete=2, except=0 · Call: `ValueError`, `_kanonik`, `any`, `hashlib.sha256`, `hashlib.sha256(_kanonik(payload)).hexdigest`, `hmac.compare_digest`, `isinstance`, `json.load`, `len`, `open`, `payload.pop`
- L63–66 **`_bawaan_snapshot`** · kontrol=0, assignment/delete=0, except=0 · Call: tidak ada
- L69–70 **`_id_bawaan`** · kontrol=0, assignment/delete=0, except=0 · Call: `_kanonik`, `hashlib.sha256`, `hashlib.sha256(_kanonik({'nilai': base, 'urutan': list(base)})).hexdigest`, `list`
- L73–100 **`profil_snapshot`** · kontrol=11, assignment/delete=9, except=0 · Call: `'profil tidak dikenal: {!r}'.format`, `ValueError`, `_bawaan_snapshot`, `_bawaan_snapshot().items`, `_id_bawaan`, `deepcopy`, `hasil.get`, `hasil.get('selisih_self', {}).pop`, `hasil.pop`, `list`, `nilai.items`, `type`
- L103–132 **`perluas_snapshot`** · kontrol=15, assignment/delete=10, except=0 · Call: `'referensi[{}] atau diff tidak sah'.format`, `'referensi[{}].id tidak cocok dengan bawaan runtime'.format`, `'referensi[{}].urutan tidak sah'.format`, `ValueError`, `_bawaan_snapshot`, `_id_bawaan`, `any`, `bases.items`, `data.get`, `data.pop`, `deepcopy`, `isinstance`, `len`, `nilai.pop`, `nilai.update`, `ref.get`, `set`

## `pycos/dukungan/sumber.py`

SHA-256: `6a26690f70d528c7007d6a4ddc760040ed0c2fef4fcb0823851cc192a802dd35`

73 baris; 0 kelas; 6 fungsi/metode termasuk nested.

Kelas: tidak ada.
Handler luas: tidak ada.

Impor (termasuk lazy/TYPE_CHECKING): `from __future__ import annotations`; `from typing import List, Optional`; `import os`.

- L25–27 **`akar_paket`** · kontrol=0, assignment/delete=0, except=0 · Call: `os.path.abspath`, `os.path.dirname`
- L30–32 **`sumber_daya`** · kontrol=0, assignment/delete=0, except=0 · Call: `akar_paket`, `os.path.join`
- L35–41 **`jalur_leksikon`** · kontrol=0, assignment/delete=0, except=0 · Call: `os.path.join`, `sumber_daya`
- L44–50 **`jalur_korpus`** · kontrol=0, assignment/delete=0, except=0 · Call: `os.path.join`, `sumber_daya`
- L53–55 **`ada_sumber_daya`** · kontrol=0, assignment/delete=0, except=0 · Call: `jalur_leksikon`, `os.path.isfile`
- L58–73 **`kandidat_leksikon`** · kontrol=3, assignment/delete=1, except=0 · Call: `hasil.append`, `jalur_leksikon`, `os.getcwd`, `os.path.join`

## `pycos/dukungan/tolok.py`

SHA-256: `6799e4c9a22602bede18d7f04ce8c9a519002aad7e9a9fda4525261e396405ad`

191 baris; 0 kelas; 10 fungsi/metode termasuk nested.

Kelas: tidak ada.
Handler luas: 37, 130.

Impor (termasuk lazy/TYPE_CHECKING): `from __future__ import annotations`; `from pycos.bahasa.tutur import TuturEngine, kosongkan_cache_leksikon`; `from pycos.dukungan.sumber import jalur_leksikon`; `from pycos.inti.naluri import DEFAULTS`; `from pycos.inti.naluri import Naluri`; `from pycos.memori.jejak_prediksi import JejakPrediksi`; `from typing import Any, Callable, Dict, List, Optional`; `import argparse`; `import json`; `import os`; `import sys`; `import time`.

- L30–42 **`_ukur`** · kontrol=2, assignment/delete=2, except=1 · Call: `'{}: {}'.format`, `fungsi`, `max`, `range`, `round`, `time.perf_counter`, `type`
- L45–48 **`_tolok_naluri_tick`** · kontrol=0, assignment/delete=1, except=0 · Call: `Naluri`, `_ukur`, `npc.tick`
- L51–58 **`_tolok_choose_action`** · kontrol=0, assignment/delete=2, except=0 · Call: `Naluri`, `_ukur`, `npc.choose_action`
- L61–66 **`_tolok_rank_actions`** · kontrol=0, assignment/delete=2, except=0 · Call: `JejakPrediksi`, `_ukur`, `jejak.rank_actions`
- L69–95 **`_tolok_to_dict_simpan`** · kontrol=4, assignment/delete=7, except=0 · Call: `DEFAULTS.items`, `Naluri`, `_ukur`, `aktif.enable_asosiasi`, `aktif.enable_eversi`, `aktif.enable_invensi`, `aktif.enable_kausal`, `aktif.enable_latent_drift`, `aktif.tick`, `aktif.to_json`, `aktif.to_json().encode`, `aktif.to_json(profil='minimal').encode`, `aktif.to_json(profil='simpan').encode`, `isinstance`, `k.startswith`, `len`, `npc.tick`, `npc.to_dict`, `npc.to_json`, `npc.to_json().encode`, `npc.to_json(profil='simpan').encode`, `range`
- L98–114 **`_tolok_predict_2000`** · kontrol=1, assignment/delete=7, except=0 · Call: `'api lorong kejadian {}'.format`, `JejakPrediksi`, `_ukur`, `float`, `hasil.get`, `jejak.performance_report`, `jejak.predict`, `jejak.record_experience`, `range`
- L117–137 **`_tolok_leksikon`** · kontrol=3, assignment/delete=4, except=1 · Call: `'berkas leksikon tidak ditemukan: {}'.format`, `'{}: {}'.format`, `TuturEngine`, `_ukur`, `hangat.get`, `jalur_leksikon`, `kosongkan_cache_leksikon`, `os.path.isfile`, `round`, `time.perf_counter`, `type`
- L140–151 **`jalankan_semua`** · kontrol=0, assignment/delete=1, except=0 · Call: `_tolok_choose_action`, `_tolok_leksikon`, `_tolok_naluri_tick`, `_tolok_predict_2000`, `_tolok_rank_actions`, `_tolok_to_dict_simpan`, `int`, `max`
- L154–166 **`_format_teks`** · kontrol=3, assignment/delete=1, except=0 · Call: `'  {:<16} GAGAL — {}'.format`, `'  {:<16} muat dingin {:.3f} ms | muat hangat {} ms/muat'.format`, `'  {:<16} {:.4f} ms/iterasi ({} iterasi, {:.3f} s)'.format`, `'\n'.join`, `baris.append`, `h.get`
- L169–187 **`main`** · kontrol=3, assignment/delete=4, except=0 · Call: `_format_teks`, `all`, `ap.add_argument`, `ap.error`, `ap.parse_args`, `argparse.ArgumentParser`, `h.get`, `jalankan_semua`, `json.dumps`, `print`

## `pycos/dukungan/validasi_state.py`

SHA-256: `8420f5463c9feeeac779239655d48cd89e2e5f29d8c7c5ee5c3b9abbd9807f8c`

152 baris; 0 kelas; 9 fungsi/metode termasuk nested.

Kelas: tidak ada.
Handler luas: tidak ada.

Impor (termasuk lazy/TYPE_CHECKING): `from __future__ import annotations`; `from collections.abc import Mapping`; `from copy import deepcopy`; `from pycos.dukungan.persistensi import perluas_snapshot`; `from pycos.kontrak import DRIVE_KEYS, angka`; `from typing import Any, Callable, Dict, List, Tuple, cast`.

- L25–30 **`_naluri_3_ke_4`** · kontrol=0, assignment/delete=1, except=0 · Call: `data.get`, `data.setdefault`
- L33–35 **`_perluas_profil`** · kontrol=0, assignment/delete=0, except=0 · Call: `perluas_snapshot`
- L45–99 **`migrasi`** · kontrol=22, assignment/delete=11, except=0 · Call: `'migrasi {} tidak menghasilkan format tujuan'.format`, `'{}.format tidak didukung: {!r}; perlu {}'.format`, `'{}.format tidak sah: {!r}'.format`, `'{}.{}'.format`, `'{}[{}]'.format`, `FORMAT_TERBARU.values`, `MIGRASI.items`, `ValueError`, `antrian.append`, `antrian.pop`, `deepcopy`, `dict`, `dilihat.add`, `enumerate`, `f.split`, `fmt.split`, `fn`, `isinstance`, `item.get`, `item.items`, `item.update`, `next`, `telusuri`, `tujuan.split`, `ubah`
- L51–81 **`migrasi.ubah`** · kontrol=15, assignment/delete=7, except=0 · Call: `'migrasi {} tidak menghasilkan format tujuan'.format`, `'{}.format tidak didukung: {!r}; perlu {}'.format`, `'{}.format tidak sah: {!r}'.format`, `'{}.{}'.format`, `MIGRASI.items`, `ValueError`, `antrian.append`, `antrian.pop`, `dilihat.add`, `fn`, `isinstance`, `item.get`, `item.items`, `item.update`, `telusuri`
- L83–96 **`migrasi.telusuri`** · kontrol=6, assignment/delete=3, except=0 · Call: `'{}.{}'.format`, `'{}[{}]'.format`, `FORMAT_TERBARU.values`, `enumerate`, `f.split`, `fmt.split`, `isinstance`, `item.get`, `item.items`, `next`, `telusuri`, `ubah`
- L102–106 **`tick_maju`** · kontrol=2, assignment/delete=0, except=0 · Call: `'{} harus integer non-negatif'.format`, `ValueError`, `cast`, `isinstance`
- L109–111 **`urgensi`** · kontrol=0, assignment/delete=0, except=0 · Call: `angka`
- L114–152 **`validasi_state`** · kontrol=16, assignment/delete=4, except=0 · Call: `'{} harus mapping'.format`, `'{}.{}'.format`, `'{}[{}]'.format`, `'{}[{}]: drive tidak dikenal'.format`, `ValueError`, `angka`, `dict`, `enumerate`, `isinstance`, `item.items`, `migrasi`, `periksa`, `tick_maju`, `urgensi`, `value.items`
- L123–149 **`validasi_state.periksa`** · kontrol=14, assignment/delete=2, except=0 · Call: `'{} harus mapping'.format`, `'{}.{}'.format`, `'{}[{}]'.format`, `'{}[{}]: drive tidak dikenal'.format`, `ValueError`, `angka`, `enumerate`, `isinstance`, `item.items`, `periksa`, `tick_maju`, `urgensi`, `value.items`

## `pycos/inti/__init__.py`

SHA-256: `e15a849aaf0d78edcc21b0e3738a23eb02409bd9b334b5085e4b233227e1f1b8`

55 baris; 0 kelas; 2 fungsi/metode termasuk nested.

Kelas: tidak ada.
Handler luas: tidak ada.

Impor (termasuk lazy/TYPE_CHECKING): `from .naluri import DRIVES, Goal, KawananNPC, Kesadaran, Mood, Naluri, Presentasi, Reputasi, Ritual, buat_npc`; `from .persona import Keadaan, PERSONA_CONTOH, Persona`; `from __future__ import annotations`; `from importlib import import_module`; `from typing import TYPE_CHECKING, Any, Dict, List`.

- L43–51 **`__getattr__`** · kontrol=1, assignment/delete=3, except=0 · Call: `'paket {!r} tidak punya atribut {!r}'.format`, `'{}.{}'.format`, `AttributeError`, `_SUBMODUL.get`, `getattr`, `globals`, `import_module`
- L54–55 **`__dir__`** · kontrol=0, assignment/delete=0, except=0 · Call: `globals`, `set`, `sorted`

## `pycos/inti/_konfigurasi.py`

SHA-256: `831f7ae07eef2dd51cc31c99e7d241e3ae65d765b8de15260c33c18dee7e9fca`

852 baris; 0 kelas; 3 fungsi/metode termasuk nested.

Kelas: tidak ada.
Handler luas: tidak ada.

Impor (termasuk lazy/TYPE_CHECKING): `from __future__ import annotations`; `from pycos.dukungan import konstanta as _konstanta_drive`; `from pycos.dukungan.leksikon import perluas as _perluas_leksikon_impak`; `from pycos.dukungan.numerik import jepit`; `from typing import Any, Dict, List, Mapping, Tuple`.

- L362–379 **`_nilai_per_drive`** · kontrol=3, assignment/delete=1, except=0 · Call: `float`, `isinstance`, `params.get`
- L840–845 **`_periksa_kunci_drive`** · kontrol=2, assignment/delete=1, except=0 · Call: `', '.join`, `'{} memuat kunci tak dikenal {}; kunci sah: {}'.format`, `ValueError`, `sorted`, `str`
- L848–850 **`_kclip`** · kontrol=0, assignment/delete=0, except=0 · Call: `jepit`

## `pycos/inti/demo/__init__.py`

SHA-256: `4e6c93ff90014c9b4c9b12cb246b1bfe4e4d32ea0191ae2cb70e605ae9df87d2`

48 baris; 0 kelas; 1 fungsi/metode termasuk nested.

Kelas: tidak ada.
Handler luas: tidak ada.

Impor (termasuk lazy/TYPE_CHECKING): `from __future__ import annotations`; `from pycos.inti.demo import skenario`; `from pycos.inti.naluri import Naluri`.

- L5–47 **`jalankan`** · kontrol=0, assignment/delete=0, except=0 · Call: `Naluri.demo`, `print`, `skenario.demo_empati`, `skenario.demo_fitur_lanjutan`, `skenario.demo_gejala`, `skenario.demo_introspeksi`, `skenario.demo_invensi`, `skenario.demo_kausal`, `skenario.demo_kesadaran`, `skenario.demo_kinerja`, `skenario.demo_kognisi`, `skenario.demo_momen`, `skenario.demo_npc`, `skenario.demo_organik`, `skenario.demo_pelindung`, `skenario.demo_perencana`, `skenario.demo_persepsi`, `skenario.demo_presentasi`, `skenario.demo_sosial`, `skenario.demo_tutur`, `skenario.demo_watak`

## `pycos/inti/demo/__main__.py`

SHA-256: `843e0afb6d01a5d131a24b40931fd7c58e2e4b70a15d1408aa2b889d1ccf54f1`

5 baris; 0 kelas; 0 fungsi/metode termasuk nested.

Kelas: tidak ada.
Handler luas: tidak ada.

Impor (termasuk lazy/TYPE_CHECKING): `from pycos.inti.demo import jalankan`.


## `pycos/inti/demo/skenario.py`

SHA-256: `2f9561050fa0624d9b8ff87a60da522075db7fec998e349e7a669ca11444d44c`

1405 baris; 0 kelas; 23 fungsi/metode termasuk nested.

Kelas: tidak ada.
Handler luas: tidak ada.

Impor (termasuk lazy/TYPE_CHECKING): `from __future__ import annotations`; `from pycos.dukungan.numerik import jepit_drive`; `from pycos.inti.naluri import DRIVES`; `from pycos.inti.naluri import JejakPrediksi, KawananNPC, LOD_MODES, Naluri`; `from pycos.inti.naluri import JejakPrediksi, KawananNPC, Naluri`; `from pycos.inti.naluri import JejakPrediksi, Naluri`; `from pycos.inti.naluri import JejakPrediksi, Naluri, Nurani`; `from pycos.inti.naluri import JejakPrediksi, Naluri, optional_module`; `from pycos.inti.naluri import KawananNPC`; `from pycos.inti.naluri import KawananNPC, LEXICON_EN, TAG_LEXICON_EN`; `from pycos.inti.naluri import KawananNPC, Naluri`; `from pycos.inti.naluri import KawananNPC, Naluri, _pelindung_act_hint, _pengakuan_istirahat, keragaman_scene`; `from pycos.inti.naluri import Naluri`; `from pycos.inti.naluri import Naluri, _kog_dari`; `from typing import Any, Dict, List, Tuple, TYPE_CHECKING`; `import json`; `import random`; `import random as _r`; `import random as _rd`.

- L15–91 **`_simulasi_harian`** · kontrol=12, assignment/delete=21, except=0 · Call: `cls`, `decision['candidate'].get`, `eff.items`, `events.append`, `float`, `jepit_drive`, `len`, `max`, `naluri.apply_events`, `naluri.calibration_error`, `naluri.choose_action`, `naluri.dream_policy`, `naluri.estimate_scale`, `naluri.observe_outcome`, `naluri.post_sleep`, `naluri.should_sleep`, `naluri.tick`, `print`, `random.Random`, `range`, `real_deltas.items`, `real_deltas.values`, `rng.gauss`, `rng.random`, `rng.uniform`, `sum`
- L94–139 **`demo_npc`** · kontrol=10, assignment/delete=9, except=0 · Call: `KawananNPC`, `KawananNPC.from_json`, `en.items`, `idn.items`, `kawanan.brief`, `kawanan.nama`, `kawanan.npcs.items`, `kawanan.set_lod_by_distance`, `kawanan.tambah`, `kawanan.tick_all`, `kawanan.to_dict`, `kawanan.to_json`, `kawanan['Bob'].impact_of`, `kawanan['Rama'].impact_of`, `len`, `n.lod_status`, `n.post_sleep`, `n.should_sleep`, `print`, `pulih.to_dict`, `range`, `round`, `tidur_log.append`
- L142–217 **`demo_empati`** · kontrol=15, assignment/delete=14, except=0 · Call: `KawananNPC`, `KawananNPC.from_json`, `ana.delta`, `ana.kenal`, `dict`, `h.get`, `jejak.append`, `json.dumps`, `k.biarkan_bersosialisasi`, `k.interaksi`, `k.tambah`, `k.tick_all`, `k.to_dict`, `print`, `pulih.to_dict`, `pulih['Rama'].relasi`, `rama.berinteraksi`, `rama.choose_action`, `rama.delta`, `rama.hud_state`, `rama.kenal`, `rama.post_sleep`, `rama.relasi`, `rama.should_sleep`, `range`, `rel.get`, `skor.get`, `tuple`
- L220–305 **`demo_watak`** · kontrol=6, assignment/delete=13, except=0 · Call: `Naluri`, `a.describe_personality`, `a.hud_state`, `a.tick`, `abs`, `b.describe_personality`, `b.hud_state`, `b.tick`, `c.hud_state`, `c.impact_of`, `c.nurani.relative_deficit`, `c.tick`, `o.nurani.relative_deficit`, `print`, `range`
- L308–364 **`demo_introspeksi`** · kontrol=7, assignment/delete=13, except=0 · Call: `Naluri`, `baik.introspeksi`, `baik.meta_kognisi`, `baik.nurani.enabled`, `baik.refleksi_diri`, `baik.tick`, `buruk.introspeksi`, `buruk.meta_kognisi`, `buruk.tick`, `dict`, `max`, `n.observe_outcome`, `print`, `range`, `rng.random`, `rng.uniform`
- L367–454 **`demo_kesadaran`** · kontrol=18, assignment/delete=9, except=0 · Call: `Naluri`, `evs.append`, `ks.add_boundary`, `ks.agency_state`, `ks.attention_limits`, `ks.backchannel`, `ks.betray`, `ks.commit`, `ks.dialogue_turn`, `ks.dream`, `ks.dream_report`, `ks.face_death`, `ks.fallibility_state`, `ks.feedback`, `ks.felt_report`, `ks.gossip`, `ks.grieve`, `ks.hold_belief`, `ks.joint_attention`, `ks.last_thought`, `ks.life_chapters`, `ks.life_chapters()[-1].get`, `ks.metacognitive_doubt`, `ks.moral_emotion`, `ks.mortality_state`, `ks.narrative_state`, `ks.pragmatics_state`, `ks.reality_report`, `ks.recursive_tom`, `ks.report`, `ks.second_person_state`, `ks.set_value`, `ks.values_state`, `ks.workspace_report`, `len`, `list`, `n.enable_kesadaran`, `n.enable_nurani`, `n.tick`, `print`, `range`
- L457–525 **`demo_presentasi`** · kontrol=5, assignment/delete=9, except=0 · Call: `Naluri`, `evs.append`, `n.enable_emosi`, `n.enable_kesadaran`, `n.enable_nurani`, `n.enable_presentasi`, `n.kesadaran.add_boundary`, `n.kesadaran.grieve`, `n.kesadaran.hold_belief`, `n.kesadaran.joint_attention`, `n.kesadaran.refuse`, `n.kesadaran.set_value`, `n.presentasi.balas`, `n.presentasi.dengar`, `n.presentasi.perilaku_idle`, `n.presentasi.reaksi`, `n.presentasi.snapshot`, `n.presentasi.ucap`, `n.tick`, `print`, `range`, `ref.get`
- L528–593 **`demo_fitur_lanjutan`** · kontrol=10, assignment/delete=11, except=0 · Call: `JejakPrediksi`, `KawananNPC`, `Naluri`, `dict`, `kawanan.catat_rumor`, `kawanan.enable_reputasi`, `kawanan.reputasi`, `kawanan.tag_all`, `kawanan.tambah`, `kawanan.terapkan_reputasi`, `n.attach_jejak`, `n.enable_emosi`, `n.enable_kesadaran`, `n.enable_nurani`, `n.enable_presentasi`, `n.enable_ritual`, `n.kesadaran.hold_belief`, `n.kesadaran.metacognitive_doubt`, `n.observe_player`, `n.pattern_report`, `n.presentasi.indikator_psikologis`, `n.presentasi.lihat_player`, `n.presentasi.proaktif`, `n.presentasi.tag_dialog`, `n.presentasi.terima_bukti`, `n.presentasi.tick`, `n.ritual.maybe_trigger`, `n.tick`, `npc.enable_emosi`, `npc.enable_presentasi`, `npc.enable_ritual`, `print`, `pro.get`, `range`
- L596–652 **`demo_kinerja`** · kontrol=7, assignment/delete=12, except=0 · Call: `JejakPrediksi`, `KawananNPC`, `Naluri`, `Naluri.replay`, `_r.Random`, `j._candidates`, `j.record_experience`, `j2.consolidate_memory`, `j2.record_experience`, `k._reindex_grid`, `k.emotional_contagion`, `k.set_position`, `k.tambah`, `k.tick_event_driven`, `len`, `n.enable_kesadaran`, `n.enable_presentasi`, `n.enable_profiling`, `n.enable_replay`, `n.export_replay`, `n.profile_report`, `n.tick`, `print`, `range`, `rng.choice`, `rng.uniform`
- L655–726 **`demo_sosial`** · kontrol=12, assignment/delete=14, except=0 · Call: `KawananNPC`, `Naluri`, `_mk`, `enumerate`, `k.catat_rumor`, `k.enable_reputasi`, `k.npcs['Pembohong'].kesadaran.confabulate`, `k.npcs[nm].berinteraksi`, `k.set_position`, `k.tambah`, `k.trust_weight`, `k2.catat_rumor`, `k2.enable_reputasi`, `k2.reputasi`, `k2.reputasi(player)['sumbu'].get`, `k2.tambah`, `k3.catat_rumor`, `k3.decay_of_truth`, `k3.echo_chamber`, `k3.enable_reputasi`, `k3.konfrontasi`, `k3.npcs[nm].kesadaran.gossip`, `k3.set_position`, `k3.tambah`, `n.berinteraksi`, `n.enable_kesadaran`, `n.hancurkan_kepercayaan`, `n.mode_npc`, `n.relasi`, `n.viskositas_relasi`, `print`, `r.get`, `range`
- L663–667 **`demo_sosial._mk`** · kontrol=0, assignment/delete=1, except=0 · Call: `k.set_position`, `k.tambah`, `n.enable_kesadaran`, `n.mode_npc`
- L729–802 **`demo_momen`** · kontrol=4, assignment/delete=25, except=0 · Call: `Naluri`, `_full`, `c.get`, `ding.presentasi.tell_katalog`, `hes.presentasi._pilih_act`, `hes.presentasi.prosodi`, `lg.presentasi.ekspresi`, `n.enable_kesadaran`, `n.kesadaran._candidates`, `n.kesadaran._remember_episode`, `n.kesadaran.narrative_state`, `n.mode_npc`, `n.nurani.set_pillars`, `n.tandai_momen`, `par.presentasi.ekspresi`, `par.presentasi.tell_katalog`, `print`, `range`, `u.bayar_utang`, `u.berinteraksi`, `u.catat_utang`, `u.menarik_diri`, `u.relasi`, `u.utang`
- L734–738 **`demo_momen._full`** · kontrol=1, assignment/delete=0, except=0 · Call: `n.enable_kesadaran`, `n.mode_npc`, `n.nurani.set_pillars`
- L805–842 **`demo_tutur`** · kontrol=3, assignment/delete=10, except=0 · Call: `Naluri`, `eng.info`, `enumerate`, `list`, `n.enable_emosi`, `n.enable_kesadaran`, `n.enable_nurani`, `n.enable_presentasi`, `n.kesadaran.hold_belief`, `n.kesadaran.tandai_core_memory`, `n.presentasi.tutur_engine`, `n.presentasi.ucap`, `print`, `r.get`, `x.keys`
- L845–926 **`demo_kognisi`** · kontrol=11, assignment/delete=22, except=0 · Call: `JejakPrediksi`, `KL.MesinKepercayaan`, `KL.boltzmann_pilih`, `KL.suhu_mental`, `Naluri`, `_npc`, `_rd.Random`, `a.eversi_param`, `a.tick`, `b.eversi_param`, `b.tick`, `dr.items`, `jp.predict`, `jp.record_experience`, `len`, `list`, `m.curiga`, `m.perbarui`, `m.tetapkan`, `max`, `n.enable_emosi`, `n.enable_eversi`, `n.enable_kesadaran`, `n3.attach_jejak`, `n3.enable_kesadaran`, `n3.enable_nurani`, `n3.nurani.seed_setpoints`, `n3.setpoint`, `n3.tick`, `n4._kog.graf.bobot`, `n4.asosiasi`, `n4.enable_asosiasi`, `n4.enable_emosi`, `n4.fobia`, `n4.tick`, `n5.enable_emosi`, `n5.enable_latent_drift`, `n5.latent_drift`, `n5.tick`, `optional_module`, `print`, `range`, `round`, `set`
- L855–859 **`demo_kognisi._npc`** · kontrol=0, assignment/delete=1, except=0 · Call: `Naluri`, `n.enable_emosi`, `n.enable_eversi`, `n.enable_kesadaran`
- L929–1070 **`demo_persepsi`** · kontrol=26, assignment/delete=26, except=0 · Call: `Naluri`, `abs`, `any`, `bl.observe_outcome`, `dict`, `enumerate`, `ev.tick`, `h.tick`, `kenyang.affordances`, `kenyang.tick`, `lapar.affordances`, `lapar.tick`, `len`, `net.tick`, `next`, `panik.feel`, `panik.tick`, `par.tick`, `print`, `range`, `reversed`, `seri.append`, `sum`, `td.nurani.seed_affective`, `td.tick`, `tenang.tick`, `vet.tick`, `wz.tick`
- L1073–1161 **`demo_organik`** · kontrol=9, assignment/delete=23, except=0 · Call: `(m.emosi_ditolak() or [{}])[-1].get`, `JejakPrediksi`, `Naluri`, `Nurani`, `bool`, `e.get`, `isinstance`, `j.half_life_episode`, `j.ingat_kembali`, `j.koreksi_salah`, `j.record_experience`, `list`, `m._emosi_naikkan`, `m.emosi_ditolak`, `m.enable_kesadaran`, `m.tandai_stimulus_bertentangan`, `m.tetapkan_identitas`, `n.daftarkan_slot`, `n.duka`, `n.enable_kesadaran`, `n.intensitas_topologis`, `n.kesadaran.future_simulation`, `n.kosongkan_slot`, `nu.hancurkan_domain`, `nu.tambal_luka`, `nu.terapkan_domain`, `p.enable_kesadaran`, `p.enable_presentasi`, `p.kosongkan_slot`, `p.presentasi.kelayakan_tutur`, `p.presentasi.ucap`, `print`, `range`, `repr`, `round`, `str`, `tahan.get`
- L1164–1226 **`demo_gejala`** · kontrol=14, assignment/delete=11, except=0 · Call: `(klaim.get('pipeline') or {}).get`, `Naluri`, `b.get`, `c.get`, `dict`, `klaim.get`, `list`, `n._gejala_hasil.get`, `n._organik.residu.state`, `n.enable_gejala`, `n.enable_kesadaran`, `n.enable_presentasi`, `n.gejala_rasakan`, `n.gejala_state`, `n.kesadaran.narrative_state`, `n.tick`, `pipa.get`, `print`, `range`, `sorted`, `st['sensitivitas_nurani'].values`, `str`
- L1229–1265 **`demo_invensi`** · kontrol=5, assignment/delete=9, except=0 · Call: `Naluri`, `_kog_dari`, `getattr`, `k.startswith`, `kog.graf.koaktifkan`, `kog.kepercayaan.ringkas`, `kog.kepercayaan.ringkas().keys`, `kog.kepercayaan.tetapkan`, `len`, `n.enable_invensi`, `n.enable_kesadaran`, `n.invensi_state`, `n.kesadaran.hold_belief`, `n.tick`, `org.luka.lukai`, `org.topologi.daftar`, `org.topologi.kosongkan`, `print`, `range`
- L1268–1296 **`demo_kausal`** · kontrol=5, assignment/delete=4, except=0 · Call: `JejakPrediksi`, `Naluri`, `jejak.record_experience`, `n.attach_jejak`, `n.blame_kausal`, `n.counterfactual_kausal`, `n.enable_kausal`, `n.enable_kesadaran`, `n.jelaskan_kenapa`, `n.pelajari_kausal`, `print`, `range`
- L1299–1322 **`demo_perencana`** · kontrol=4, assignment/delete=3, except=0 · Call: `' → '.join`, `JejakPrediksi`, `Naluri`, `jejak.record_experience`, `n.attach_jejak`, `n.enable_kausal`, `n.enable_kesadaran`, `n.enable_perencana`, `n.rencanakan`, `print`, `range`, `s.split`
- L1325–1404 **`demo_pelindung`** · kontrol=12, assignment/delete=21, except=0 · Call: `KawananNPC`, `Naluri`, `_pelindung_act_hint`, `_pengakuan_istirahat`, `hasil.append`, `info.get`, `kawanan.npcs[nm].enable_pelindung`, `kawanan.npcs[nm].enable_presentasi`, `kawanan.tambah`, `keragaman_scene`, `list`, `n.enable_kesadaran`, `n.enable_pelindung`, `n.enable_presentasi`, `n.set_personality_preset`, `p.buffer_manusiawi`, `p.dengar`, `p.eskalasi_variasi`, `p.jeda_bermakna`, `p.monitor_integritas`, `p.monitor_integritas().periksa`, `p.pidato_gagal`, `p.saring_meta`, `p.serap_adversarial`, `p.tandai_lupa`, `p.tandai_tidak_paham`, `p.ucap`, `p.watak_kegagalan`, `p2.degradasi_state`, `print`, `q._history.append`, `range`, `repr`, `ucap.get`

## `pycos/inti/ekstensi/__init__.py`

SHA-256: `23ff2d6d80f040de73dc1b15ea110d183d518f0ba17195c094f682c184872da8`

16 baris; 0 kelas; 1 fungsi/metode termasuk nested.

Kelas: tidak ada.
Handler luas: tidak ada.

Impor (termasuk lazy/TYPE_CHECKING): `from __future__ import annotations`; `from importlib import import_module`; `from typing import Optional`.

- L10–16 **`pasang`** · kontrol=3, assignment/delete=1, except=0 · Call: `'ekstensi tidak dikenal: {!r}'.format`, `ValueError`, `import_module`, `modul.pasang`

## `pycos/inti/ekstensi/gejala.py`

SHA-256: `ffce923e7cbf36db8a2953e9b33a3c327471848890b57bf8b75ee4ec5039cb42`

623 baris; 0 kelas; 21 fungsi/metode termasuk nested.

Kelas: tidak ada.
Handler luas: 213, 259, 470, 494, 582, 150, 307, 539, 441, 521.

Impor (termasuk lazy/TYPE_CHECKING): `from __future__ import annotations`; `from pycos.dukungan import diagnostik as _diag`; `from pycos.dukungan.numerik import jepit, jepit_01, jepit_drive`; `from pycos.dukungan.patching import install_method, optional_module, wrap_method`; `from pycos.inti.kesadaran import Kesadaran`; `from pycos.inti.naluri import _organik_dari`; `from typing import Any, Dict, List, Mapping, Optional`; `import re`.

- L59–61 **`_gejala_modul`** · kontrol=0, assignment/delete=0, except=0 · Call: `optional_module`
- L64–85 **`_gejala_dari`** · kontrol=6, assignment/delete=5, except=1 · Call: `_organik_dari`, `getattr`, `int`, `max`, `setattr`
- L88–89 **`_gejala_aktif`** · kontrol=0, assignment/delete=0, except=0 · Call: `bool`, `self.params.get`
- L95–161 **`gejala_rasakan`** · kontrol=15, assignment/delete=17, except=1 · Call: `OG.Gejala.tanda_dari`, `_diag.catat`, `_gejala_aktif`, `_gejala_dari`, `_gejala_modul`, `dict`, `float`, `g.muncul`, `gejala.get`, `getattr`, `getattr(self, '_gejala_hasil', {}).get`, `int`, `jepit`, `jepit_01`, `jepit_drive`, `ks.attend`, `ks.enabled`, `ks.submit`, `nur.context_signature`, `round`, `self._gejala_aktifkan_kembali`, `self._gejala_pipeline`, `str`, `str(sampel).strip`
- L164–187 **`_gejala_aktifkan_kembali`** · kontrol=7, assignment/delete=7, except=0 · Call: `(gejala or {}).get`, `dict`, `dikenal.get`, `getattr`, `int`, `max`, `round`, `self._emosi_aktif`, `self._emosi_naikkan`, `self.delta`, `str`
- L190–201 **`_gejala_konten`** · kontrol=2, assignment/delete=1, except=0 · Call: `float`, `getattr`, `int`, `jepit`, `ks.enabled`, `ks.submit`, `str`
- L207–228 **`_gejala_klaim_drive`** · kontrol=5, assignment/delete=4, except=1 · Call: `_diag.catat`, `abs`, `float`, `max`, `self.delta`, `self.impact_of`, `self.params.get`, `str`, `str(sampel).strip`, `vektor.items`
- L231–247 **`_gejala_klaim_emosi`** · kontrol=4, assignment/delete=3, except=0 · Call: `abs`, `float`, `max`, `self._emosi_aktif`, `self._emosi_naikkan`, `self.emosi_dominan`, `str`
- L250–275 **`_gejala_klaim_memori`** · kontrol=9, assignment/delete=5, except=1 · Call: `_diag.catat`, `abs`, `float`, `getattr`, `hasattr`, `max`, `nur.anticipate`, `nur.anticipate_detail`, `nur.enabled`, `prior.items`, `self.delta`, `self.params.get`, `str`, `str(sampel).strip`, `trust.get`
- L278–294 **`_gejala_klaim_tutur`** · kontrol=6, assignment/delete=4, except=0 · Call: `getattr`, `re.findall`, `str`, `str(sampel).strip`, `str(sampel).strip().lower`
- L297–312 **`_gejala_nama_sementara`** · kontrol=5, assignment/delete=5, except=1 · Call: `_diag.catat`, `getattr`, `p._generatif`, `p.enabled`, `re.findall`, `str`, `str(sampel).lower`
- L318–389 **`_gejala_pipeline`** · kontrol=29, assignment/delete=25, except=0 · Call: `(akrab or {}).get`, `(hasil or {}).get`, `(item or {}).get`, `_gejala_aktif`, `_gejala_dari`, `_gejala_modul`, `bool`, `c.get`, `detail.get`, `dict`, `float`, `g.gagal`, `g.jenis_hint`, `g.klaim`, `g.proses`, `getattr`, `getattr(self, '_gejala_hasil', {}).get`, `hasil.get`, `int`, `len`, `list`, `max`, `pencalonan.append`, `probe`, `round`, `self._gejala_konten`, `self._gejala_terapkan`, `simpan.keys`, `simpan.pop`, `str`, `sudah.keys`, `sudah.pop`
- L392–449 **`_gejala_terapkan`** · kontrol=18, assignment/delete=12, except=1 · Call: `(self._gejala_sampel or {}).get`, `_diag.catat`, `_gejala_dari`, `_gejala_modul`, `bekas.get`, `float`, `g.beri_nama`, `getattr`, `hasattr`, `int`, `keputusan.get`, `min`, `nur.serap_kategori`, `org.residu.bekas`, `penuh.get`, `proto.get`, `self._gejala_klaim_identitas`, `self._gejala_konten`, `self._gejala_nama_sementara`, `str`
- L452–473 **`_gejala_klaim_identitas`** · kontrol=6, assignment/delete=2, except=1 · Call: `_diag.catat`, `any`, `bool`, `float`, `getattr`, `int`, `ks._refresh_identity`, `ks.enabled`, `ks.narrative_identity.append`, `min`, `penuh.get`, `round`, `self.params.get`, `str`, `x.get`
- L479–497 **`_gejala_ignite`** · kontrol=8, assignment/delete=7, except=1 · Call: `(item or {}).get`, `_diag.catat`, `_gejala_aktif`, `detail.get`, `dict`, `getattr`, `getattr(self, '_tick', lambda: 0)`, `int`, `isinstance`, `n._gejala_pipeline`, `original`, `str`
- L502–525 **`_gejala_proses_tertunda`** · kontrol=11, assignment/delete=9, except=1 · Call: `(item or {}).get`, `_diag.catat`, `detail.get`, `dict`, `getattr`, `int`, `isinstance`, `item.get`, `list`, `self._gejala_pipeline`, `str`
- L528–542 **`_gejala_tick`** · kontrol=6, assignment/delete=3, except=1 · Call: `_diag.catat`, `_gejala_aktif`, `_gejala_dari`, `g.proses`, `getattr`, `int`, `keputusan.get`, `original`, `self._gejala_proses_tertunda`, `self._gejala_terapkan`
- L547–551 **`enable_gejala`** · kontrol=0, assignment/delete=1, except=0 · Call: `bool`, `self.params.get`
- L554–565 **`gejala_state`** · kontrol=3, assignment/delete=6, except=0 · Call: `_gejala_dari`, `bool`, `dict`, `g.state`, `getattr`, `org.residu.bekas_state`, `self.params.get`
- L568–585 **`_gejala_hud_state`** · kontrol=4, assignment/delete=3, except=1 · Call: `_diag.catat`, `_gejala_aktif`, `dict`, `len`, `original`, `self.naluri.gejala_state`, `self.naluri.gejala_state().get`, `x.get`
- L595–622 **`pasang`** · kontrol=1, assignment/delete=0, except=0 · Call: `install_method`, `wrap_method`

## `pycos/inti/ekstensi/invensi.py`

SHA-256: `138e89a3fe9ef064cd3d67cf418326cc7e9fa57cc24f8a20879b4f72ec60fa67`

248 baris; 0 kelas; 12 fungsi/metode termasuk nested.

Kelas: tidak ada.
Handler luas: 56, 61, 67, 122, 154, 202, 213, 222, 76, 81, 89, 95, 103, 110, 115, 163.

Impor (termasuk lazy/TYPE_CHECKING): `from __future__ import annotations`; `from pycos.dukungan import diagnostik as _diag`; `from pycos.dukungan.patching import install_method, wrap_method`; `from pycos.inti.naluri import Naluri`; `from pycos.inti.naluri import _kog_dari`; `from pycos.inti.naluri import _kog_dari, _naluri_tick`; `from pycos.inti.naluri import _naluri_tick`; `from pycos.inti.naluri import _organik_dari`; `from typing import Any, Dict, List, Optional`.

- L22–32 **`_invensi_dari`** · kontrol=4, assignment/delete=2, except=0 · Call: `_organik_dari`, `getattr`, `inv.set_knob`
- L35–36 **`_invensi_aktif`** · kontrol=0, assignment/delete=0, except=0 · Call: `bool`, `self.params.get`
- L39–44 **`_inv_teks`** · kontrol=3, assignment/delete=0, except=0 · Call: `getattr`, `isinstance`, `str`, `x.get`
- L47–125 **`_invensi_digest`** · kontrol=32, assignment/delete=16, except=11 · Call: `(getattr(ks, 'dissonance', {}) or {}).keys`, `(getattr(self, 'emosi', {}) or {}).items`, `(getattr(self, 'levels', {}) or {}).items`, `(kog.kepercayaan.ringkas() or {}).keys`, `(o.luka.ringkas() or {}).items`, `_diag.catat`, `_inv_teks`, `_kog_dari`, `dg['asosiasi'].append`, `dict`, `dict.fromkeys`, `edge.items`, `edge.keys`, `float`, `getattr`, `kog.kepercayaan.ringkas`, `list`, `o.luka.ringkas`, `o.paralel.bertentangan`, `o.topologi.kosong`, `str`
- L128–133 **`enable_invensi`** · kontrol=0, assignment/delete=1, except=0 · Call: `bool`, `self.params.get`
- L136–166 **`lahirkan_struktur`** · kontrol=6, assignment/delete=8, except=2 · Call: `_diag.catat`, `_invensi_dari`, `_invensi_digest`, `_kog_dari`, `_naluri_tick`, `int`, `inv.lahirkan`, `kog.kepercayaan.tetapkan`, `lahir[s['jenis']].append`, `len`
- L169–176 **`kristalkan_invensi`** · kontrol=1, assignment/delete=2, except=0 · Call: `_invensi_dari`, `_naluri_tick`, `int`, `inv.kristal`
- L179–186 **`invensi_state`** · kontrol=1, assignment/delete=3, except=0 · Call: `_invensi_aktif`, `_invensi_dari`, `inv.state`
- L191–215 **`_naluri_invensi_step`** · kontrol=6, assignment/delete=7, except=2 · Call: `(self.params or {}).get`, `_diag.catat`, `_invensi_aktif`, `_invensi_dari`, `_naluri_tick`, `getattr`, `int`, `inv.gugur`, `inv.kristal`, `lahirkan_struktur`, `max`
- L218–225 **`_invensi_tick`** · kontrol=1, assignment/delete=1, except=1 · Call: `_diag.catat`, `_naluri_invensi_step`, `original`
- L228–231 **`_pasang_invensi_tick`** · kontrol=0, assignment/delete=0, except=0 · Call: `wrap_method`
- L238–247 **`pasang`** · kontrol=1, assignment/delete=0, except=0 · Call: `_pasang_invensi_tick`, `install_method`

## `pycos/inti/ekstensi/kausal.py`

SHA-256: `b4b177a08836fde4c8d43fed985ddcb0c1a0cfe6b83178ef3c7d185ad8a1983c`

152 baris; 0 kelas; 13 fungsi/metode termasuk nested.

Kelas: tidak ada.
Handler luas: 38, 113, 123.

Impor (termasuk lazy/TYPE_CHECKING): `from __future__ import annotations`; `from pycos.dukungan import diagnostik as _diag`; `from pycos.dukungan.patching import install_method, wrap_method`; `from pycos.inti.naluri import Naluri`; `from pycos.inti.naluri import _kausal_step`; `from pycos.inti.naluri import _organik_dari`; `from typing import Any, Dict`.

- L18–21 **`_kausal_dari`** · kontrol=1, assignment/delete=1, except=0 · Call: `_organik_dari`, `getattr`
- L24–25 **`_kausal_aktif`** · kontrol=0, assignment/delete=0, except=0 · Call: `bool`, `self.params.get`
- L28–46 **`pelajari_kausal`** · kontrol=6, assignment/delete=7, except=1 · Call: `_diag.catat`, `_kausal_aktif`, `_kausal_dari`, `e.get`, `getattr`, `int`, `len`, `list`, `max`, `mk.pelajari`, `mk.ringkas`
- L49–55 **`jelaskan_kenapa`** · kontrol=1, assignment/delete=1, except=0 · Call: `_kausal_dari`, `mk.jelaskan`, `pelajari_kausal`
- L58–64 **`counterfactual_kausal`** · kontrol=1, assignment/delete=1, except=0 · Call: `_kausal_dari`, `mk.counterfactual`, `pelajari_kausal`
- L67–73 **`blame_kausal`** · kontrol=1, assignment/delete=1, except=0 · Call: `_kausal_dari`, `mk.blame`, `pelajari_kausal`
- L76–82 **`mekanisme_kausal`** · kontrol=1, assignment/delete=1, except=0 · Call: `_kausal_dari`, `mk.mekanisme`, `pelajari_kausal`
- L85–91 **`kausal_state`** · kontrol=1, assignment/delete=3, except=0 · Call: `_kausal_aktif`, `_kausal_dari`, `mk.state`
- L94–98 **`enable_kausal`** · kontrol=0, assignment/delete=1, except=0 · Call: `bool`, `self.params.get`
- L103–115 **`_kausal_step`** · kontrol=4, assignment/delete=3, except=1 · Call: `(self.params or {}).get`, `_diag.catat`, `_kausal_aktif`, `getattr`, `int`, `max`, `pelajari_kausal`
- L118–126 **`_kausal_tick`** · kontrol=1, assignment/delete=1, except=1 · Call: `_diag.catat`, `_kausal_step`, `original`
- L129–132 **`_pasang_kausal_tick`** · kontrol=0, assignment/delete=0, except=0 · Call: `wrap_method`
- L139–151 **`pasang`** · kontrol=1, assignment/delete=0, except=0 · Call: `_pasang_kausal_tick`, `install_method`

## `pycos/inti/ekstensi/ketidaktahuan.py`

SHA-256: `75f770542ec2accbe9589cd4a3bf786f6302a5b9eaf0c18e4ca62e7cd5ef1824`

216 baris; 0 kelas; 5 fungsi/metode termasuk nested.

Kelas: tidak ada.
Handler luas: 87, 141, 195.

Impor (termasuk lazy/TYPE_CHECKING): `from __future__ import annotations`; `from itertools import islice`; `from pycos.dukungan import diagnostik as _diag`; `from pycos.dukungan.numerik import jepit, jepit_01`; `from pycos.dukungan.patching import optional_module, wrap_method`; `from pycos.inti.kesadaran import Kesadaran`; `from pycos.inti.presentasi import Presentasi`; `from typing import Mapping`.

- L16–20 **`_kt_context_item`** · kontrol=1, assignment/delete=1, except=0 · Call: `isinstance`, `item.get`
- L22–91 **`_kt_kesadaran_candidates`** · kontrol=16, assignment/delete=15, except=2 · Call: `_diag.catat`, `_kt_batas_pengetahuan`, `_kt_context_item`, `_kt_sikap_ketidaktahuan`, `boundary.get`, `candidates.append`, `float`, `getattr`, `int`, `isinstance`, `islice`, `item.get`, `jepit`, `list`, `original`, `proposition.lower`, `proposition.lower().startswith`, `self.enabled`
- L94–143 **`_kt_presentasi_skor`** · kontrol=15, assignment/delete=13, except=1 · Call: `_diag.catat`, `_kt_batas_pengetahuan`, `_kt_context_item`, `_kt_sikap_ketidaktahuan`, `boundary.get`, `dict`, `float`, `getattr`, `isinstance`, `islice`, `item.get`, `iter`, `jepit_01`, `nudges.get`, `original`, `selected.items`, `topik.strip`
- L146–198 **`_kt_tick_doubt`** · kontrol=19, assignment/delete=15, except=1 · Call: `_diag.catat`, `_kt_batas_pengetahuan`, `_kt_context_item`, `_kt_sikap_ketidaktahuan`, `boundary.get`, `callable`, `detail.get`, `float`, `getattr`, `isinstance`, `islice`, `item.get`, `iter`, `kwargs.get`, `len`, `min`, `nurani.enabled`, `nurani.felt_consciousness`, `nurani.metacognitive_doubt`, `original`, `params.get`
- L204–215 **`pasang`** · kontrol=1, assignment/delete=0, except=0 · Call: `wrap_method`

## `pycos/inti/ekstensi/kognisi.py`

SHA-256: `f5b8e1c04aa2964679875a780e488d5026e1ea02d6da9be48938e2d0a00aa3f5`

368 baris; 0 kelas; 27 fungsi/metode termasuk nested.

Kelas: tidak ada.
Handler luas: 173, 236, 308, 21.

Impor (termasuk lazy/TYPE_CHECKING): `from __future__ import annotations`; `from pycos.dukungan import diagnostik as _diag`; `from pycos.dukungan.patching import install_method, install_methods, optional_module, wrap_method`; `from pycos.inti.presentasi import Presentasi`; `from typing import Mapping`.

- L9–24 **`_kog_disonansi`** · kontrol=6, assignment/delete=3, except=1 · Call: `_diag.catat`, `abs`, `callable`, `d.values`, `float`, `fn`, `getattr`, `isinstance`, `sum`
- L27–32 **`_kog_situasi`** · kontrol=2, assignment/delete=4, except=0 · Call: `abs`, `emosi.get`, `float`, `getattr`, `levels.get`, `max`
- L35–40 **`_kog_aksi`** · kontrol=2, assignment/delete=2, except=0 · Call: `getattr`, `isinstance`, `log[-1].get`, `str`
- L43–53 **`_kog_dari`** · kontrol=3, assignment/delete=6, except=0 · Call: `getattr`, `int`, `modul.KognisiLanjut`, `optional_module`
- L56–65 **`_naluri_enable_eversi`** · kontrol=3, assignment/delete=3, except=0 · Call: `_kog_dari`, `bool`, `float`, `kog.aktifkan`
- L68–79 **`_naluri_enable_drift`** · kontrol=4, assignment/delete=4, except=0 · Call: `_kog_dari`, `bool`, `float`, `kog.aktifkan`
- L82–91 **`_naluri_enable_asosiasi`** · kontrol=3, assignment/delete=3, except=0 · Call: `_kog_dari`, `bool`, `float`, `kog.aktifkan`
- L94–99 **`_naluri_eversi_param`** · kontrol=1, assignment/delete=1, except=0 · Call: `_kog_dari`, `dict`, `kog.eversi.eversi_param`
- L102–104 **`_naluri_latent_drift`** · kontrol=0, assignment/delete=1, except=0 · Call: `_kog_dari`, `kog.ou.ringkas`
- L107–109 **`_naluri_asosiasi`** · kontrol=0, assignment/delete=1, except=0 · Call: `_kog_dari`, `kog.graf.asosiasi`
- L112–118 **`_naluri_koaktifkan`** · kontrol=3, assignment/delete=2, except=0 · Call: `(getattr(self, 'emosi', {}) or {}).get`, `_kog_dari`, `float`, `getattr`, `kog.graf.koaktifkan`
- L121–123 **`_naluri_aktifkan_konsep`** · kontrol=0, assignment/delete=1, except=0 · Call: `_kog_dari`, `kog.graf.aktifkan`
- L126–128 **`_naluri_fobia`** · kontrol=0, assignment/delete=1, except=0 · Call: `_kog_dari`, `kog.graf.fobia`
- L131–133 **`_naluri_kepercayaan`** · kontrol=0, assignment/delete=1, except=0 · Call: `_kog_dari`, `kog.kepercayaan.kepercayaan`
- L136–140 **`_naluri_perbarui_kepercayaan`** · kontrol=1, assignment/delete=1, except=0 · Call: `_kog_dari`, `kog.kepercayaan.perbarui`
- L143–145 **`_naluri_kognisi_state`** · kontrol=0, assignment/delete=1, except=0 · Call: `getattr`, `kog.to_dict`
- L148–164 **`_naluri_kog_step`** · kontrol=6, assignment/delete=8, except=0 · Call: `_kog_aksi`, `_kog_disonansi`, `_kog_situasi`, `any`, `getattr`, `kog.aktif.get`, `kog.aktif.values`, `kog.eversi.update`, `kog.langkah`
- L169–176 **`_kog_tick`** · kontrol=1, assignment/delete=1, except=1 · Call: `_diag.catat`, `_naluri_kog_step`, `original`
- L181–188 **`_kog_to_dict`** · kontrol=2, assignment/delete=5, except=0 · Call: `getattr`, `isinstance`, `kog.to_dict`, `list`, `original`
- L191–205 **`_kog_from_dict`** · kontrol=6, assignment/delete=5, except=1 · Call: `all`, `data.get`, `isinstance`, `len`, `modul.KognisiLanjut.from_dict`, `optional_module`, `original`, `tuple`
- L211–220 **`_pres_enable_boltzmann`** · kontrol=3, assignment/delete=4, except=0 · Call: `bool`, `float`
- L223–268 **`_pres_skor_acts`** · kontrol=8, assignment/delete=21, except=1 · Call: `_diag.catat`, `em`, `emosi.get`, `float`, `getattr`, `getattr(self, '_doubt', lambda: 0.0)`, `len`, `levels.get`, `lv`, `max`, `self._label_rel`, `str`
- L271–292 **`_pres_pilih_act_boltzmann`** · kontrol=4, assignment/delete=12, except=0 · Call: `emosi.get`, `float`, `getattr`, `levels.get`, `max`, `modul.boltzmann_pilih`, `modul.suhu_mental`, `optional_module`, `round`, `self._skor_acts`, `self.params.get`
- L295–296 **`_pres_boltzmann_terakhir`** · kontrol=0, assignment/delete=0, except=0 · Call: `getattr`
- L301–311 **`_pilih_act_boltzmann`** · kontrol=2, assignment/delete=3, except=1 · Call: `_diag.catat`, `bool`, `k.get`, `len`, `original`, `self._pilih_act_boltzmann`, `self.params.get`
- L314–317 **`_pasang_boltzmann`** · kontrol=0, assignment/delete=0, except=0 · Call: `wrap_method`
- L333–367 **`pasang`** · kontrol=1, assignment/delete=0, except=0 · Call: `_pasang_boltzmann`, `install_method`, `install_methods`, `wrap_method`

## `pycos/inti/ekstensi/organik.py`

SHA-256: `36808d3bfcd36c57066dd15cd0c3ae6066b268b0c6a8eb9d437a28e5b8e942c5`

1187 baris; 0 kelas; 69 fungsi/metode termasuk nested.

Kelas: tidak ada.
Handler luas: 244, 269, 332, 489, 524, 603, 703, 946, 230, 349, 458, 972, 46, 56, 360, 464, 884, 1010, 1085, 795, 807.

Impor (termasuk lazy/TYPE_CHECKING): `from __future__ import annotations`; `from pycos.bahasa.teks import ekstrak_entitas`; `from pycos.bahasa.teks import jejak_bentuk as _jejak_bentuk`; `from pycos.bahasa.teks import jejak_bentuk as _jejak_d`; `from pycos.bahasa.teks import jejak_bentuk as _jejak_i`; `from pycos.bahasa.teks import potong_batas_kata`; `from pycos.dukungan import diagnostik as _diag`; `from pycos.dukungan.numerik import jepit_01, jepit_drive`; `from pycos.dukungan.patching import install_method, install_methods, optional_module, wrap_method`; `from pycos.inti._konfigurasi import DRIVES, EMOSI_ALIASES, FELT_STATES`; `from pycos.inti.kesadaran import Kesadaran`; `from pycos.inti.naluri import _organik_tubuh_langkah`; `from pycos.inti.presentasi import Presentasi`; `from typing import Mapping`; `import math`; `import re`.

- L26–34 **`_organik_dari`** · kontrol=3, assignment/delete=4, except=0 · Call: `getattr`, `int`, `modul.Organik`, `optional_module`
- L37–64 **`_organik_bungkus_serialisasi`** · kontrol=5, assignment/delete=4, except=2 · Call: `_diag.catat`, `ambil`, `data.get`, `isinstance`, `original`, `pasang`, `wrap_method`
- L41–49 **`_organik_bungkus_serialisasi._ambil_state`** · kontrol=2, assignment/delete=2, except=1 · Call: `_diag.catat`, `ambil`, `isinstance`, `original`
- L51–59 **`_organik_bungkus_serialisasi._pasang_state`** · kontrol=3, assignment/delete=1, except=1 · Call: `_diag.catat`, `data.get`, `isinstance`, `original`, `pasang`
- L68–69 **`_naluri_organik`** · kontrol=1, assignment/delete=0, except=0 · Call: `_organik_dari`, `getattr`
- L72–74 **`_naluri_organik_ambil`** · kontrol=0, assignment/delete=1, except=0 · Call: `getattr`, `o.to_dict`
- L77–86 **`_naluri_organik_pasang`** · kontrol=3, assignment/delete=3, except=1 · Call: `bool`, `getattr`, `int`, `modul.Organik.from_dict`, `optional_module`
- L89–90 **`_naluri_tick`** · kontrol=1, assignment/delete=0, except=0 · Call: `getattr`, `int`
- L94–96 **`daftarkan_slot`** · kontrol=0, assignment/delete=1, except=0 · Call: `_naluri_organik`, `_naluri_tick`, `o.topologi.daftar`
- L99–101 **`kosongkan_slot`** · kontrol=0, assignment/delete=1, except=0 · Call: `_naluri_organik`, `_naluri_tick`, `o.topologi.kosongkan`
- L104–106 **`isi_ulang_slot`** · kontrol=0, assignment/delete=1, except=0 · Call: `_naluri_organik`, `_naluri_tick`, `o.topologi.isi_ulang`
- L109–111 **`slot_terisi`** · kontrol=0, assignment/delete=1, except=0 · Call: `getattr`, `o.topologi.terisi`
- L114–117 **`intensitas_topologis`** · kontrol=0, assignment/delete=1, except=0 · Call: `float`, `getattr`, `o.topologi.intensitas`
- L120–122 **`layak_cabang`** · kontrol=0, assignment/delete=1, except=0 · Call: `getattr`, `o.topologi.layak_cabang`
- L125–130 **`duka`** · kontrol=1, assignment/delete=1, except=0 · Call: `getattr`, `o.topologi.peek`, `o.topologi.peek(ent).get`
- L133–139 **`kehilangan_state`** · kontrol=2, assignment/delete=2, except=0 · Call: `bool`, `getattr`, `len`, `o.topologi.kosong`, `o.topologi.peek`
- L142–144 **`cabang_mustahil`** · kontrol=1, assignment/delete=1, except=0 · Call: `getattr`, `list`
- L148–150 **`tetapkan_identitas`** · kontrol=0, assignment/delete=1, except=0 · Call: `_naluri_organik`, `o.identitas.tetapkan`
- L153–155 **`batas_identitas_state`** · kontrol=0, assignment/delete=1, except=0 · Call: `getattr`, `o.identitas.state`
- L158–160 **`emosi_ditolak`** · kontrol=0, assignment/delete=1, except=0 · Call: `getattr`, `o.identitas.penolakan`
- L163–165 **`tandai_stimulus_bertentangan`** · kontrol=0, assignment/delete=1, except=0 · Call: `bool`
- L168–170 **`organik_state`** · kontrol=0, assignment/delete=1, except=0 · Call: `getattr`, `o.ringkas`
- L175–206 **`_organik_emosi_naikkan`** · kontrol=12, assignment/delete=14, except=0 · Call: `EMOSI_ALIASES.get`, `_naluri_organik`, `_naluri_tick`, `bool`, `float`, `getattr`, `max`, `min`, `o.identitas.catat_penolakan`, `o.identitas.izinkan`, `o.residu.ambang_dimodifikasi`, `o.residu.langit_dimodifikasi`, `oo.residu.daftar`, `original`, `self.emosi.get`, `self.params.get`, `str`, `str(alasan).lower`, `str(emosi).lower`
- L212–247 **`_organik_future_simulation`** · kontrol=11, assignment/delete=8, except=2 · Call: `_diag.catat`, `_naluri_tick`, `ent.get`, `getattr`, `isinstance`, `len`, `log.append`, `o.topologi.cabang_mustahil`, `original`, `self.future_sim.pop`, `str`
- L253–257 **`_presentasi_organik`** · kontrol=2, assignment/delete=1, except=0 · Call: `_organik_dari`, `getattr`
- L260–285 **`_organik_konteks_tubuh`** · kontrol=10, assignment/delete=14, except=1 · Call: `_diag.catat`, `bool`, `em.get`, `float`, `getattr`, `len`, `lv.get`, `max`, `min`, `n.mood`, `o.topologi.kosong`
- L288–294 **`kelayakan_tutur`** · kontrol=2, assignment/delete=2, except=0 · Call: `_organik_konteks_tubuh`, `_presentasi_organik`, `komp.items`, `o.tutur.kelayakan`, `round`
- L297–300 **`penolakan_state`** · kontrol=0, assignment/delete=1, except=0 · Call: `_presentasi_organik`, `o.tutur.riwayat`
- L303–335 **`_organik_ucap`** · kontrol=7, assignment/delete=13, except=1 · Call: `_diag.catat`, `_jejak_bentuk`, `_naluri_tick`, `_organik_konteks_tubuh`, `_presentasi_organik`, `ent.get`, `getattr`, `isinstance`, `komp.items`, `o.tutur.bentuk`, `o.tutur.catat`, `o.tutur.jenis`, `o.tutur.kelayakan`, `o.tutur.tertahan`, `original`, `round`
- L341–363 **`_organik_felt_mentah`** · kontrol=10, assignment/delete=9, except=2 · Call: `_diag.catat`, `f.items`, `float`, `fr.items`, `getattr`, `isinstance`, `nu.felt_report`
- L366–382 **`apersepsi_state`** · kontrol=3, assignment/delete=5, except=1 · Call: `_naluri_organik`, `_organik_felt_mentah`, `getattr`, `list`, `o.apersepsi.amati`
- L385–386 **`rasa_kabut`** · kontrol=0, assignment/delete=0, except=0 · Call: `self.apersepsi_state`, `self.apersepsi_state().get`
- L389–396 **`_organik_felt_report_jujur`** · kontrol=0, assignment/delete=1, except=0 · Call: `ap.get`, `self.apersepsi_state`
- L400–410 **`pegang_dua`** · kontrol=1, assignment/delete=4, except=0 · Call: `_naluri_organik`, `_naluri_tick`, `o.paralel.tambah`
- L413–417 **`pegang_keyakinan`** · kontrol=1, assignment/delete=1, except=0 · Call: `_naluri_organik`, `_naluri_tick`, `o.paralel.tambah`
- L420–422 **`keyakinan_paralel`** · kontrol=0, assignment/delete=1, except=0 · Call: `getattr`, `o.paralel.state`
- L425–427 **`pengaruh_paralel`** · kontrol=0, assignment/delete=1, except=0 · Call: `getattr`, `o.paralel.pengaruh`
- L430–432 **`tanpa_resolusi`** · kontrol=0, assignment/delete=1, except=0 · Call: `getattr`, `o.paralel.tanpa_resolusi`
- L435–437 **`bertindak_dari_lapisan`** · kontrol=1, assignment/delete=1, except=0 · Call: `getattr`, `o.paralel.bertindak_dari`
- L441–467 **`_organik_tubuh_langkah`** · kontrol=7, assignment/delete=8, except=2 · Call: `_diag.catat`, `_organik_felt_mentah`, `delta.items`, `float`, `getattr`, `jepit_drive`, `o.tubuh.langkah`, `self.delta`, `self.levels.get`
- L470–472 **`tubuh_state`** · kontrol=0, assignment/delete=1, except=0 · Call: `getattr`, `o.tubuh.state`
- L475–478 **`suntik_tubuh`** · kontrol=0, assignment/delete=1, except=0 · Call: `_naluri_organik`, `o.tubuh.suntik`
- L481–492 **`_organik_tick`** · kontrol=2, assignment/delete=2, except=1 · Call: `_diag.catat`, `_organik_tubuh_langkah`, `bool`, `getattr`, `getattr(self, '_vacancy_aktif', lambda: False)`, `original`
- L502–536 **`_nama_dari_teks`** · kontrol=11, assignment/delete=5, except=1 · Call: `_diag.catat`, `e.get`, `ekstrak_entitas`, `hasil.append`, `len`, `m.group`, `m.start`, `nama.lower`, `nm.lower`, `out.extend`, `re.escape`, `re.findall`, `re.finditer`, `str`
- L539–586 **`auto_deteksi_slot`** · kontrol=22, assignment/delete=16, except=0 · Call: `(getattr(j, '_patterns', None) or {}).items`, `_naluri_organik`, `_naluri_tick`, `_nama_dari_teks`, `entri.get`, `ep.get`, `getattr`, `int`, `isinstance`, `item.get`, `kandidat.get`, `kandidat.items`, `key.split`, `max`, `o.topologi.daftar`, `o.topologi.peek`, `o.topologi.peek(nama).get`, `slot.get`, `sorted`, `str`
- L590–606 **`_organik_hud_state`** · kontrol=3, assignment/delete=8, except=1 · Call: `_diag.catat`, `ap.get`, `bool`, `getattr`, `isinstance`, `n.apersepsi_state`, `o.paralel.state`, `original`, `round`, `str`, `str(o.identitas.klaim).strip`
- L611–616 **`daftarkan_residu`** · kontrol=1, assignment/delete=1, except=0 · Call: `_naluri_organik`, `_naluri_tick`, `o.residu.daftar`
- L619–624 **`tambal_residu`** · kontrol=1, assignment/delete=1, except=0 · Call: `_naluri_organik`, `_naluri_tick`, `o.residu.tambal`
- L627–630 **`ambang_dimodifikasi`** · kontrol=0, assignment/delete=1, except=0 · Call: `_naluri_organik`, `float`, `o.residu.ambang_dimodifikasi`
- L633–636 **`langit_dimodifikasi`** · kontrol=0, assignment/delete=1, except=0 · Call: `_naluri_organik`, `float`, `o.residu.langit_dimodifikasi`
- L639–641 **`residu_state`** · kontrol=0, assignment/delete=1, except=0 · Call: `getattr`, `o.residu.state`
- L645–651 **`mulai_vacancy`** · kontrol=1, assignment/delete=3, except=0 · Call: `_naluri_organik`, `_naluri_tick`, `bool`, `o.vacancy.mulai`, `state.get`
- L654–659 **`vacancy_state`** · kontrol=1, assignment/delete=1, except=0 · Call: `bool`, `getattr`, `o.vacancy.state`
- L662–666 **`_vacancy_aktif`** · kontrol=1, assignment/delete=3, except=0 · Call: `bool`, `getattr`
- L669–684 **`_vacancy_lewat`** · kontrol=5, assignment/delete=6, except=0 · Call: `_naluri_tick`, `bool`, `float`, `getattr`, `int`, `math.ceil`, `max`, `o.vacancy.lewat`, `self._emosi_peluruh`, `self.params.get`
- L688–728 **`_kesadaran_intrusi_spontan`** · kontrol=10, assignment/delete=11, except=1 · Call: `_diag.catat`, `_naluri_organik`, `_naluri_tick`, `bool`, `dict`, `float`, `getattr`, `int`, `len`, `max`, `n.mood`, `n.params.get`, `o.intrusi.coba`, `o.residu.tekanan`, `self._lolos_lantai`, `self._tick`, `self.workspace.append`
- L731–733 **`paksa_intrusi`** · kontrol=0, assignment/delete=0, except=0 · Call: `self._intrusi_spontan`
- L736–738 **`intrusi_state`** · kontrol=0, assignment/delete=1, except=0 · Call: `getattr`, `o.intrusi.state`
- L744–755 **`_detak_context`** · kontrol=6, assignment/delete=5, except=0 · Call: `float`, `getattr`, `grief.values`, `max`, `o.residu.tekanan`, `x.get`
- L758–763 **`_catat_interupsi`** · kontrol=1, assignment/delete=2, except=0 · Call: `_naluri_tick`, `dict`, `len`, `self._interupsi_internal.append`
- L766–811 **`_detak_checkpoint`** · kontrol=14, assignment/delete=17, except=2 · Call: `_catat_interupsi`, `_detak_context`, `_diag.catat`, `_naluri_organik`, `_naluri_tick`, `entri.get`, `float`, `getattr`, `hasattr`, `isinstance`, `keluar.append`, `ks.attend`, `ks.enabled`, `ks.felt.get`, `max`, `min`, `o.detak.maju`, `p.enabled`, `p.ucap`, `str`, `ucapan.get`
- L814–816 **`paksa_interupsi`** · kontrol=0, assignment/delete=1, except=0 · Call: `_naluri_organik`, `o.detak.paksa`
- L819–821 **`detak_internal_state`** · kontrol=0, assignment/delete=1, except=0 · Call: `getattr`, `o.detak.state`
- L825–891 **`_catat_selisih_self`** · kontrol=24, assignment/delete=32, except=1 · Call: `_diag.catat`, `_naluri_tick`, `a_pros.get`, `abs`, `aktual.get`, `float`, `getattr`, `hasattr`, `int`, `jepit_01`, `ks._refresh_identity`, `ks.submit`, `lantai.get`, `len`, `list`, `max`, `min`, `p_pros.get`, `prediksi.get`, `round`, `self._selisih_self_log.append`, `self.params.get`, `str`
- L894–900 **`selisih_self_state`** · kontrol=0, assignment/delete=0, except=0 · Call: `dict`, `float`, `int`, `round`
- L903–907 **`interupsi_internal_state`** · kontrol=1, assignment/delete=0, except=0 · Call: `dict`, `len`
- L912–1055 **`_organik_lanjut_ucap`** · kontrol=61, assignment/delete=65, except=3 · Call: `' '.join`, `' '.join(kata[:batas]).rstrip`, `_catat_interupsi`, `_catat_selisih_self`, `_detak_context`, `_diag.catat`, `_jejak_d`, `_jejak_i`, `dict`, `em.get`, `em_utama.get`, `ent.get`, `ev.get`, `float`, `getattr`, `hist[-1].get`, `info.get`, `int`, `isinstance`, `lap.get`, `len`, `list`, `max`, `min`, `model_diri.get`, `n.mood`, `nu._p`, `o.detak.maju`, `o.paralel.tanpa_resolusi`, `o.residu.tekanan_target`, `original`, `potong_batas_kata`, `prediksi.get`, `round`, `sebab.append`, `self._label_rel`, `set`, `str`, `str(ent['teks']).split`, `utama.get`
- L1061–1088 **`_organik_hold_belief`** · kontrol=8, assignment/delete=12, except=1 · Call: `_diag.catat`, `bool`, `dict`, `float`, `getattr`, `isinstance`, `jepit_01`, `n.delta`, `o.paralel.tanpa_resolusi`, `original`, `self.dissonance.get`, `str`
- L1097–1186 **`pasang`** · kontrol=3, assignment/delete=0, except=0 · Call: `_organik_bungkus_serialisasi`, `install_method`, `install_methods`, `wrap_method`

## `pycos/inti/ekstensi/pelindung.py`

SHA-256: `9887feda8d9202fd51d8a1f52bae233fd9e3663119906a2b1b064106bca3f18c`

1845 baris; 1 kelas; 54 fungsi/metode termasuk nested.

Kelas: `MonitorIntegritas` L1143.
Handler luas: 248, 280, 373, 421, 491, 586, 1421, 1521, 1764, 259, 1255, 1385, 1443, 1577, 1728, 1249, 1266, 1561, 724.

Impor (termasuk lazy/TYPE_CHECKING): `from __future__ import annotations`; `from pycos.bahasa import keadaan as _keadaan`; `from pycos.bahasa.teks import kandidat_dasar`; `from pycos.bahasa.teks import kata_isi as _kata_isi`; `from pycos.bahasa.teks import kata_isi as _kata_isi_t`; `from pycos.bahasa.teks import kata_isi as _kata_isi_u`; `from pycos.dukungan import diagnostik as _diag`; `from pycos.dukungan.numerik import jepit`; `from pycos.dukungan.patching import install_method, install_methods, wrap_method`; `from pycos.inti.kawanan import KawananNPC`; `from pycos.inti.presentasi import Presentasi`; `from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple`; `import copy`; `import re`.

- L221–226 **`_pelindung_stabil`** · kontrol=1, assignment/delete=2, except=0 · Call: `ord`, `str`
- L229–230 **`_pelindung_kata`** · kontrol=2, assignment/delete=0, except=0 · Call: `re.findall`, `str`, `str(teks or '').lower`
- L233–268 **`_pelindung_lema_tutur`** · kontrol=10, assignment/delete=11, except=2 · Call: `_diag.catat`, `_pelindung_init`, `callable`, `e.get`, `fn`, `getattr`, `lema.add`, `set`, `str`, `str(k).lower`, `str(l).lower`
- L271–285 **`_pelindung_kata_dikenal`** · kontrol=4, assignment/delete=0, except=1 · Call: `_diag.catat`, `kandidat_dasar`
- L288–294 **`_pelindung_bentuk`** · kontrol=2, assignment/delete=4, except=0 · Call: `int`, `k.strip`, `kal[0].lower`, `len`, `min`, `re.findall`, `re.split`, `str`, `t.split`
- L297–300 **`_pelindung_jaccard`** · kontrol=2, assignment/delete=0, except=0 · Call: `float`, `len`
- L303–306 **`_pelindung_pilih_stabil`** · kontrol=1, assignment/delete=0, except=0 · Call: `_pelindung_stabil`, `len`, `str`
- L309–315 **`_pelindung_dari`** · kontrol=3, assignment/delete=0, except=0 · Call: `getattr`, `hasattr`
- L318–324 **`_pelindung_aktif`** · kontrol=2, assignment/delete=3, except=0 · Call: `_pelindung_dari`, `bool`, `getattr`, `params.get`
- L327–353 **`_pelindung_init`** · kontrol=2, assignment/delete=21, except=0 · Call: `dict`, `getattr`, `int`, `p.params.get`, `set`
- L359–394 **`_pelindung_ujaran_keadaan`** · kontrol=8, assignment/delete=8, except=1 · Call: `_diag.catat`, `_keadaan.realisasi`, `_keadaan.realisasi_daftar`, `int`, `ord`, `self._tick`, `self.tutur_engine`, `str`, `sum`, `tuple`
- L397–405 **`watak_kegagalan`** · kontrol=3, assignment/delete=5, except=0 · Call: `data.get`, `dict`, `getattr`, `str`, `str(getattr(self.naluri, 'personality_name', '') or '').strip`, `str(getattr(self.naluri, 'personality_name', '') or '').strip().lower`
- L408–433 **`pidato_gagal`** · kontrol=7, assignment/delete=7, except=1 · Call: `' '.join`, `_diag.catat`, `_kata_isi`, `_pelindung_pilih_stabil`, `_pelindung_ujaran_keadaan`, `list`, `self._tick`, `self.watak_kegagalan`, `str`, `w.get`
- L436–446 **`_pelindung_act_hint`** · kontrol=6, assignment/delete=3, except=0 · Call: `_pelindung_init`, `any`, `bool`, `int`, `p._pelindung_flag.values`, `self._tick`, `self.watak_kegagalan`, `str`, `ujian.get`, `w.get`
- L449–452 **`_pelindung_reset_flag`** · kontrol=1, assignment/delete=1, except=0 · Call: tidak ada
- L471–501 **`buffer_manusiawi`** · kontrol=9, assignment/delete=8, except=1 · Call: `' '.join`, `_diag.catat`, `_kata_isi`, `_pelindung_init`, `_pelindung_pilih_stabil`, `_pelindung_ujaran_keadaan`, `bool`, `ord`, `self._tick`, `self.params.get`, `self.watak_kegagalan`, `str`, `str(jenis or 'tak_paham').lower`, `sum`, `w.get`, `{'lupa': 'ragu', 'kontradiksi': 'ragu'}.get`
- L504–507 **`tandai_lupa`** · kontrol=0, assignment/delete=2, except=0 · Call: `_pelindung_init`, `bool`, `dict`
- L510–513 **`tandai_kontradiksi`** · kontrol=0, assignment/delete=2, except=0 · Call: `_pelindung_init`, `bool`, `dict`
- L516–519 **`tandai_tidak_paham`** · kontrol=0, assignment/delete=2, except=0 · Call: `_pelindung_init`, `bool`, `dict`
- L522–552 **`_pelindung_buffer_jenis`** · kontrol=15, assignment/delete=10, except=0 · Call: `(sekarang or {}).get`, `_pelindung_init`, `bool`, `getattr`, `int`, `len`, `p._pelindung_flag.get`, `self._kes`, `self._tick`, `self.params.get`, `str`
- L558–626 **`jeda_bermakna`** · kontrol=15, assignment/delete=22, except=1 · Call: `_diag.catat`, `_pelindung_init`, `float`, `getattr`, `int`, `jepit`, `len`, `max`, `min`, `p._pelindung_jeda_riwayat.append`, `round`, `sebab.append`, `self._dissonance`, `self._doubt`, `self._nur`, `self._p`, `self._pelindung_kebaruan_input`, `self._tick`, `self.naluri.mood`
- L629–639 **`_pelindung_kebaruan_input`** · kontrol=3, assignment/delete=4, except=0 · Call: `_pelindung_init`, `_pelindung_kata`, `_pelindung_kata_dikenal`, `_pelindung_lema_tutur`, `float`, `len`
- L645–742 **`eskalasi_variasi`** · kontrol=34, assignment/delete=41, except=1 · Call: `_PELINDUNG_ALTERNATIF_ACT.get`, `_diag.catat`, `_pelindung_bentuk`, `_pelindung_init`, `_pelindung_jaccard`, `_pelindung_kata`, `all`, `any`, `bool`, `deteksi.get`, `deteksi.items`, `float`, `geser.get`, `int`, `len`, `max`, `min`, `p._pelindung_act_terakhir.append`, `p._pelindung_anggaran.get`, `p._pelindung_anggaran_maks.get`, `p._pelindung_teks.append`, `self._bingkai_relasi`, `self._ganti_kata`, `self._ganti_struktur`, `self._generatif`, `self._isi_ucap`, `self._p`, `self._pengakuan_repetisi`, `self._tick`, `self._warnai`, `str`, `urutan.index`
- L745–762 **`_pengakuan_repetisi`** · kontrol=0, assignment/delete=3, except=0 · Call: `_pelindung_pilih_stabil`, `list`, `pilihan.append`, `self._tick`, `self.watak_kegagalan`, `str`, `tabel.get`
- L776–842 **`_ganti_kata`** · kontrol=39, assignment/delete=22, except=0 · Call: `_pelindung_pilih_stabil`, `abs`, `all`, `any`, `e2.get`, `ent.get`, `float`, `getattr`, `hasattr`, `kandidat.append`, `leks.ambil`, `len`, `list`, `m.group`, `max`, `pilih[0].upper`, `re.sub`, `self._tick`, `self.tutur_engine`, `set`, `sorted`, `str`, `w.lower`, `w[0].isupper`
- L790–840 **`_ganti_kata.ganti`** · kontrol=38, assignment/delete=19, except=0 · Call: `_pelindung_pilih_stabil`, `abs`, `all`, `any`, `e2.get`, `ent.get`, `float`, `kandidat.append`, `leks.ambil`, `len`, `list`, `m.group`, `max`, `pilih[0].upper`, `self._tick`, `set`, `sorted`, `str`, `w.lower`, `w[0].isupper`
- L845–862 **`_ganti_struktur`** · kontrol=8, assignment/delete=6, except=0 · Call: `' '.join`, `_pelindung_pilih_stabil`, `belakang.strip`, `belakang.strip().rstrip`, `depan.strip`, `depan.strip().lower`, `k.strip`, `len`, `opsi.append`, `re.split`, `self._tick`, `sisa.strip`, `sisa[0].upper`, `str`, `t.split`
- L865–878 **`_pengakuan_istirahat`** · kontrol=3, assignment/delete=2, except=0 · Call: `_pelindung_pilih_stabil`, `pilihan.append`, `self._tick`, `self.watak_kegagalan`
- L884–947 **`saring_meta`** · kontrol=13, assignment/delete=21, except=0 · Call: `_PELINDUNG_ANGKA_KONTEKS_RE.search`, `_PELINDUNG_ANGKA_KONTEKS_RE.sub`, `_PELINDUNG_META_KETAT_RE.finditer`, `_pelindung_init`, `_pelindung_pilih_stabil`, `_pola_angka.search`, `_pola_angka.sub`, `bocor.append`, `bool`, `len`, `list`, `m.end`, `m.group`, `m.start`, `p._pelindung_meta_bocor.append`, `pola.finditer`, `re.findall`, `re.sub`, `re.sub('\\s{2,}', ' ', bersih).strip`, `re.sub('\\s{2,}', ' ', out).strip`, `self._kuantor_angka`, `self._tick`, `sorted`, `str`, `x.start`
- L950–954 **`_kuantor_angka`** · kontrol=2, assignment/delete=2, except=0 · Call: `int`, `re.sub`, `str`, `sum`
- L960–993 **`serap_adversarial`** · kontrol=12, assignment/delete=11, except=0 · Call: `_PELINDUNG_UJIAN.items`, `_kata_isi_u`, `_pelindung_aktif`, `_pelindung_init`, `_pelindung_pilih_stabil`, `_pelindung_ujaran_keadaan`, `dict`, `list`, `re.search`, `self._tick`, `self.watak_kegagalan`, `str`, `str(teks or '').strip`, `str(teks or '').strip().lower`, `w.get`
- L999–1031 **`degradasi_state`** · kontrol=8, assignment/delete=13, except=0 · Call: `_pelindung_init`, `float`, `getattr`, `int`, `len`, `max`, `min`, `p._pelindung_anggaran.values`, `p._pelindung_anggaran_maks.values`, `round`, `self._kes`, `self._nur`, `self._p`, `self._tick`, `sum`
- L1034–1053 **`_pelindung_tanda_lelah`** · kontrol=4, assignment/delete=10, except=0 · Call: `_pelindung_init`, `_pelindung_pilih_stabil`, `dict`, `entry.get`, `float`, `int`, `max`, `pros.get`, `round`, `self._tick`, `str`
- L1059–1074 **`keragaman_tanda`** · kontrol=4, assignment/delete=6, except=0 · Call: `_pelindung_init`, `dict`, `frek.get`, `frek.items`, `int`, `max`, `re.findall`, `self._act_counts.get`, `self._act_counts.items`, `self._act_counts.values`, `str`, `sum`, `t.lower`, `x.get`
- L1077–1088 **`dorong_geser`** · kontrol=2, assignment/delete=5, except=0 · Call: `_pelindung_init`, `dict`, `int`, `self._p`, `self._tick`
- L1091–1137 **`keragaman_scene`** · kontrol=16, assignment/delete=13, except=0 · Call: `_pelindung_aktif`, `_pelindung_dari`, `dict`, `dict(npcs or {}).items`, `dict(npcs or {}).values`, `getattr`, `getattr(contoh, 'params', {}).get`, `int`, `laporan.append`, `len`, `max`, `next`, `p.dorong_geser`, `p.enabled`, `p.keragaman_tanda`, `peta.items`, `peta.setdefault`, `peta.setdefault(str(nilai), []).append`, `sorted`, `str`, `t.get`, `tanda.items`, `tanda[nm].get`
- L1152–1157 **`MonitorIntegritas.__init__`** · kontrol=0, assignment/delete=5, except=0 · Call: tidak ada
- L1160–1237 **`MonitorIntegritas.periksa`** · kontrol=25, assignment/delete=28, except=0 · Call: `_pelindung_dari`, `_pelindung_init`, `_pelindung_jaccard`, `_pelindung_kata`, `act.count`, `dict`, `float`, `getattr`, `int`, `koreksi.append`, `len`, `list`, `max`, `min`, `p._kes`, `p._tick`, `p.degradasi_state`, `p.dorong_geser`, `p.enabled`, `round`, `self._picu_momen`, `self.koreksi.append`, `self.riwayat.append`, `self.riwayat[-1].get`, `set`, `str`, `sum`, `temuan.append`, `x.get`
- L1240–1273 **`MonitorIntegritas._picu_momen`** · kontrol=12, assignment/delete=7, except=3 · Call: `_diag.catat`, `dipakai.append`, `getattr`, `getattr(ritual, 'enabled', lambda: False)`, `koreksi.append`, `ks.enabled`, `ks.submit`, `p._kes`, `p.tell_katalog`, `ritual.maybe_trigger`, `tell.get`
- L1279–1291 **`_pelindung_pilih_act`** · kontrol=5, assignment/delete=4, except=0 · Call: `_PELINDUNG_ALTERNATIF_ACT.get`, `_pelindung_act_hint`, `_pelindung_aktif`, `_pelindung_init`, `dict`, `geser.get`, `int`, `original`, `self._tick`, `str`
- L1296–1398 **`_pelindung_ucap`** · kontrol=31, assignment/delete=47, except=1 · Call: `_diag.catat`, `_pelindung_aktif`, `_pelindung_buffer_jenis`, `_pelindung_init`, `_pelindung_reset_flag`, `_pelindung_tanda_lelah`, `_pengakuan_istirahat`, `dict`, `entry.get`, `eskalasi.get`, `int`, `isinstance`, `laporan.get`, `list`, `min`, `original`, `pros.get`, `self._history[-1].get`, `self._p`, `self._pelindung_entry`, `self._tick`, `self.buffer_manusiawi`, `self.degradasi_state`, `self.deskripsi`, `self.eskalasi_variasi`, `self.jeda_bermakna`, `self.monitor_integritas`, `self.monitor_integritas().periksa`, `self.saring_meta`, `self.watak_kegagalan`, `self.watak_kegagalan().get`, `str`, `ujian.get`
- L1401–1425 **`_pelindung_entry`** · kontrol=4, assignment/delete=8, except=1 · Call: `(degradasi or {}).get`, `_diag.catat`, `dict`, `entry.get`, `int`, `max`, `min`, `pros.get`, `round`, `self._doubt`, `self._eid`, `self._log`, `self._tick`, `self.deskripsi`, `self.jeda_bermakna`, `self.nonverbal`, `self.prosodi`, `str`
- L1433–1524 **`_penahanan_ucap`** · kontrol=24, assignment/delete=41, except=2 · Call: `' '.join`, `(desc + '; ' + tell).strip`, `(lama + '; ' + tell).strip`, `_diag.catat`, `_kata_isi_t`, `_pelindung_ujaran_keadaan`, `copy.deepcopy`, `dict`, `eksp.get`, `entry.get`, `float`, `gestur.get`, `hasil_tahan.get`, `int`, `isinstance`, `ks.record_withholding_attempt`, `ks.withheld_for`, `max`, `min`, `nv.setdefault`, `original`, `pros.get`, `round`, `self._history[-1].get`, `self._kes`, `self._log`, `self.deskripsi`, `str`, `str(eksp.get('kebocoran') or '').strip`, `str(gestur.get('deskripsi', '')).strip`, `str(hasil_tahan.get('tell', '')).strip`, `tertahan.get`
- L1531–1583 **`_audisi_diri_ucap`** · kontrol=18, assignment/delete=11, except=2 · Call: `_diag.catat`, `bool`, `dict`, `entry.get`, `entry.pop`, `isinstance`, `ks.audition_self`, `ks.deliver_strategic_speech`, `ks.record_manipulation_step`, `ks.record_roleplay_speech`, `original`, `self._history[-1].get`, `self._kes`, `str`, `str(entry.get('teks', '')).strip`, `str(strategic.get('teks', '')).strip`, `strategic.get`
- L1588–1608 **`_pelindung_dengar`** · kontrol=7, assignment/delete=8, except=0 · Call: `_pelindung_aktif`, `_pelindung_init`, `_pelindung_kata`, `_pelindung_kata_dikenal`, `_pelindung_lema_tutur`, `float`, `len`, `list`, `original`, `self.serap_adversarial`, `set`, `str`
- L1613–1618 **`monitor_integritas`** · kontrol=1, assignment/delete=2, except=0 · Call: `MonitorIntegritas`, `_pelindung_init`
- L1621–1625 **`enable_pelindung`** · kontrol=0, assignment/delete=1, except=0 · Call: `bool`, `self.params.get`
- L1628–1646 **`pelindung_state`** · kontrol=1, assignment/delete=2, except=0 · Call: `_pelindung_dari`, `_pelindung_init`, `bool`, `dict`, `len`, `p.degradasi_state`, `p.monitor_integritas`, `p.watak_kegagalan`, `self.params.get`
- L1649–1667 **`_pelindung_to_dict`** · kontrol=2, assignment/delete=2, except=0 · Call: `dict`, `getattr`, `int`, `list`, `original`, `sorted`
- L1672–1702 **`_pelindung_from_dict`** · kontrol=23, assignment/delete=15, except=0 · Call: `(blok.get('anggaran') or {}).items`, `(blok.get('anggaran_maks') or {}).items`, `(blok.get('flag') or {}).items`, `(data or {}).get`, `_pelindung_init`, `blok.get`, `bool`, `dict`, `int`, `isinstance`, `original`, `set`, `str`
- L1718–1744 **`monitor_scene`** · kontrol=8, assignment/delete=6, except=1 · Call: `_diag.catat`, `getattr`, `keragaman_scene`, `laporan.get`, `list`, `p.enabled`, `p.monitor_integritas`, `p.monitor_integritas().periksa`, `rotasi.append`, `self.npcs.items`
- L1747–1749 **`keragaman`** · kontrol=0, assignment/delete=0, except=0 · Call: `keragaman_scene`
- L1754–1767 **`_pelindung_tick_all`** · kontrol=4, assignment/delete=4, except=1 · Call: `_diag.catat`, `_pelindung_aktif`, `_pelindung_dari`, `getattr`, `getattr(p, '_tick', lambda: 0)`, `int`, `max`, `next`, `original`, `p._p`, `self.monitor_scene`, `self.npcs.values`
- L1778–1844 **`pasang`** · kontrol=2, assignment/delete=0, except=0 · Call: `install_method`, `install_methods`, `wrap_method`

## `pycos/inti/ekstensi/perencana.py`

SHA-256: `751177ab168c214282c4fd8707ef71cbbe6475103bcec1160f5d61bc13b8773d`

92 baris; 0 kelas; 7 fungsi/metode termasuk nested.

Kelas: tidak ada.
Handler luas: 36, 43.

Impor (termasuk lazy/TYPE_CHECKING): `from __future__ import annotations`; `from pycos.dukungan import diagnostik as _diag`; `from pycos.dukungan.patching import install_method`; `from pycos.inti.naluri import _kausal_dari, pelajari_kausal`; `from pycos.inti.naluri import _kog_dari`; `from pycos.inti.naluri import _organik_dari`; `from typing import Any, Dict, Iterable, List, Optional`; `import re`.

- L19–22 **`_perencana_dari`** · kontrol=1, assignment/delete=1, except=0 · Call: `_organik_dari`, `getattr`
- L25–26 **`_perencana_aktif`** · kontrol=0, assignment/delete=0, except=0 · Call: `bool`, `self.params.get`
- L29–46 **`_fakta_sekarang`** · kontrol=5, assignment/delete=5, except=2 · Call: `(kog.kepercayaan.ringkas() or {}).keys`, `_diag.catat`, `_kog_dari`, `getattr`, `kog.kepercayaan.ringkas`, `konteks.lower`, `list`, `re.findall`, `str`
- L49–62 **`rencanakan`** · kontrol=2, assignment/delete=4, except=0 · Call: `_fakta_sekarang`, `_kausal_dari`, `_perencana_aktif`, `_perencana_dari`, `list`, `pelajari_kausal`, `pl.langkah`, `pl.narasi`, `pl.rencanakan_rencana`, `str`
- L65–71 **`rencana_state`** · kontrol=1, assignment/delete=3, except=0 · Call: `_perencana_aktif`, `_perencana_dari`, `pl.state`
- L74–78 **`enable_perencana`** · kontrol=0, assignment/delete=1, except=0 · Call: `bool`, `self.params.get`
- L85–91 **`pasang`** · kontrol=1, assignment/delete=0, except=0 · Call: `install_method`

## `pycos/inti/ekstensi/persistensi.py`

SHA-256: `0ac8616e2a7e4225dbd9794c2c8f4f3f28ae74b0b26c44ed55699c3720739993`

15 baris; 0 kelas; 2 fungsi/metode termasuk nested.

Kelas: tidak ada.
Handler luas: tidak ada.

Impor (termasuk lazy/TYPE_CHECKING): `from __future__ import annotations`; `from pycos.dukungan.patching import wrap_method`; `from pycos.dukungan.persistensi import profil_snapshot`; `from typing import Any, Dict`.

- L6–10 **`_naluri_profil_snapshot`** · kontrol=1, assignment/delete=0, except=0 · Call: `'profil tidak dikenal: {!r}'.format`, `ValueError`, `original`, `profil_snapshot`
- L12–15 **`pasang`** · kontrol=0, assignment/delete=0, except=0 · Call: `wrap_method`

## `pycos/inti/kawanan.py`

SHA-256: `36d4cb9c060febbaeb99c18775685cc3a35042f16aab2f65e99cd9f710d20d4d`

1578 baris; 1 kelas; 78 fungsi/metode termasuk nested.

Kelas: `KawananNPC` L19.
Handler luas: 91, 260, 910, 1381, 183, 480, 1152, 1192, 1348, 1359, 1518, 1542, 198, 211, 233, 274, 948, 1006, 1075, 1286, 1342, 1444, 1455, 1272, 1296.

Impor (termasuk lazy/TYPE_CHECKING): `from __future__ import annotations`; `from pycos.dukungan import diagnostik as _diag`; `from pycos.dukungan.numerik import jepit_01, jepit_drive`; `from pycos.dukungan.persistensi import muat_json`; `from pycos.dukungan.persistensi import simpan_json`; `from pycos.dukungan.validasi_state import validasi_state`; `from pycos.inti.naluri import DRIVES`; `from pycos.inti.naluri import EMOSI`; `from pycos.inti.naluri import Naluri`; `from pycos.inti.naluri import buat_npc`; `from pycos.inti.reputasi import Reputasi`; `from pycos.kontrak import angka`; `from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple, TYPE_CHECKING`; `import copy`; `import json`; `import math`; `import warnings`.

- L37–57 **`KawananNPC.__init__`** · kontrol=0, assignment/delete=14, except=0 · Call: `Reputasi`
- L60–96 **`KawananNPC.tambah`** · kontrol=7, assignment/delete=6, except=1 · Call: `TypeError`, `ValueError`, `_diag.catat`, `buat_npc`, `isinstance`, `len`, `self.set_position`, `warnings.warn`
- L98–124 **`KawananNPC.serap`** · kontrol=10, assignment/delete=8, except=1 · Call: `TypeError`, `ValueError`, `any`, `getattr`, `isinstance`, `key.strip`, `self.npcs.values`, `self.positions.pop`, `self.set_position`
- L129–131 **`KawananNPC.enable_reputasi`** · kontrol=0, assignment/delete=1, except=0 · Call: `bool`, `self._reputasi.enabled`
- L133–151 **`KawananNPC.catat_rumor`** · kontrol=1, assignment/delete=5, except=0 · Call: `float`, `self._penilaian_sumber`, `self._reputasi.sebar`, `self._tandai_listener_alarm`
- L153–155 **`KawananNPC.reputasi`** · kontrol=0, assignment/delete=0, except=0 · Call: `self._reputasi.reputasi`
- L157–158 **`KawananNPC.reputasi_semua`** · kontrol=0, assignment/delete=0, except=0 · Call: `self._reputasi.semua`
- L160–187 **`KawananNPC.terapkan_reputasi`** · kontrol=4, assignment/delete=6, except=1 · Call: `_diag.catat`, `dict`, `float`, `getattr`, `jepit_drive`, `n.berinteraksi`, `n.kenal`, `rep.get`, `rep['sumbu'].get`, `round`, `self._record_relation`, `self._reputasi.reputasi`, `self.npcs.items`, `str`
- L190–201 **`KawananNPC.lihat_player_all`** · kontrol=4, assignment/delete=3, except=1 · Call: `_diag.catat`, `getattr`, `pres.enabled`, `pres.lihat_player`, `self.npcs.items`
- L203–214 **`KawananNPC.presentasi_all`** · kontrol=4, assignment/delete=3, except=1 · Call: `_diag.catat`, `getattr`, `pres.enabled`, `pres.hud_state`, `self.npcs.items`
- L216–221 **`KawananNPC.tag_all`** · kontrol=3, assignment/delete=0, except=0 · Call: `getattr`, `n.presentasi.enabled`, `n.presentasi.tag_dialog`, `self.npcs.items`
- L223–236 **`KawananNPC.proaktif_all`** · kontrol=5, assignment/delete=4, except=1 · Call: `_diag.catat`, `getattr`, `pres.enabled`, `pres.proaktif`, `self.npcs.items`
- L238–263 **`KawananNPC.dialog`** · kontrol=6, assignment/delete=5, except=1 · Call: `KeyError`, `_diag.catat`, `getattr`, `pa.dengar`, `pa.enabled`, `pa.ucap`, `pb.balas`, `pb.dengar`, `pb.enabled`, `self._reputasi.catat`, `self.interaksi`, `ucapan_a.get`, `ucapan_b.get`
- L265–277 **`KawananNPC.adegan_all`** · kontrol=4, assignment/delete=3, except=1 · Call: `_diag.catat`, `getattr`, `pres.adegan`, `pres.enabled`, `self.npcs.items`
- L279–287 **`KawananNPC.hapus`** · kontrol=1, assignment/delete=2, except=0 · Call: `row.pop`, `self._wake.pop`, `self.npcs.pop`, `self.positions.pop`, `self.relation_matrix.pop`, `self.relation_matrix.values`, `str`
- L289–290 **`KawananNPC.__getitem__`** · kontrol=0, assignment/delete=0, except=0 · Call: tidak ada
- L292–293 **`KawananNPC.__contains__`** · kontrol=0, assignment/delete=0, except=0 · Call: tidak ada
- L295–296 **`KawananNPC.__iter__`** · kontrol=0, assignment/delete=0, except=0 · Call: `iter`, `self.npcs.values`
- L298–299 **`KawananNPC.__len__`** · kontrol=0, assignment/delete=0, except=0 · Call: `len`
- L301–302 **`KawananNPC.nama`** · kontrol=0, assignment/delete=0, except=0 · Call: `list`
- L304–332 **`KawananNPC._record_relation`** · kontrol=3, assignment/delete=9, except=0 · Call: `dict`, `float`, `int`, `len`, `min`, `observer_npc.nurani.observe_other_belief`, `prior.get`, `relation.get`, `row.get`, `row.pop`, `row[k].get`, `self.npcs.get`, `self.relation_matrix.setdefault`, `str`
- L334–336 **`KawananNPC.relasi`** · kontrol=0, assignment/delete=0, except=0 · Call: `dict`, `self.relation_matrix.get`, `self.relation_matrix.get(str(observer), {}).get`, `str`
- L338–360 **`KawananNPC.set_position`** · kontrol=9, assignment/delete=6, except=0 · Call: `KeyError`, `TypeError`, `ValueError`, `all`, `float`, `isinstance`, `len`, `list`, `math.isfinite`, `str`
- L362–365 **`KawananNPC.position_of`** · kontrol=0, assignment/delete=1, except=0 · Call: `list`, `self.positions.get`, `str`
- L368–388 **`KawananNPC.set_lod_by_distance`** · kontrol=4, assignment/delete=6, except=0 · Call: `n.set_lod`
- L390–394 **`KawananNPC.lod_by_distance_all`** · kontrol=2, assignment/delete=0, except=0 · Call: `jarak.items`, `self.set_lod_by_distance`
- L397–462 **`KawananNPC._rencana_prediksi`** · kontrol=39, assignment/delete=18, except=0 · Call: `': NPC tidak dikenal: {!r}'.format`, `'JEJAK {} tidak mendukung rank_actions'.format`, `'candidates[{}] harus daftar aksi bernama'.format`, `'stimulus[{}] harus teks non-kosong'.format`, `ValueError`, `angka`, `any`, `c.get`, `c.get('name', c.get('action', '')).strip`, `callable`, `candidates.get`, `data.items`, `getattr`, `getattr(n, '_vacancy_aktif', lambda: False)`, `isinstance`, `len`, `math.dist`, `plan.append`, `self.npcs.items`, `self.positions.get`, `stimulus.get`, `stimulus.strip`, `tuple`, `value.strip`
- L464–487 **`KawananNPC._jalankan_prediksi`** · kontrol=5, assignment/delete=9, except=1 · Call: `_diag.catat`, `copy.deepcopy`, `jejak.predict`, `jejak.rank_actions`, `report['npcs'].values`, `slot.update`, `str`
- L489–491 **`KawananNPC.laporan_prediksi`** · kontrol=0, assignment/delete=0, except=0 · Call: `copy.deepcopy`, `getattr`
- L493–500 **`KawananNPC.prediksi_all`** · kontrol=0, assignment/delete=1, except=0 · Call: `self._jalankan_prediksi`, `self._rencana_prediksi`
- L502–533 **`KawananNPC.tick_all`** · kontrol=7, assignment/delete=5, except=0 · Call: `ValueError`, `action_cost.get`, `any`, `bool`, `events.get`, `isinstance`, `n.tick`, `self._jalankan_prediksi`, `self._rencana_prediksi`, `self.npcs.items`
- L535–658 **`KawananNPC.broadcast`** · kontrol=34, assignment/delete=39, except=0 · Call: `KeyError`, `TypeError`, `ValueError`, `_for_distance`, `annotated.append`, `any`, `copy.deepcopy`, `dict`, `drive_map.items`, `enumerate`, `expanded.append`, `float`, `isinstance`, `item.get`, `item.pop`, `item.setdefault`, `len`, `list`, `math.isfinite`, `math.sqrt`, `max`, `min`, `npc._buffer_events`, `npc.apply_events`, `range`, `raw.get`, `raw.items`, `report['skipped_outside_radius'].append`, `report['skipped_unpositioned'].append`, `round`, `self._nearby`, `self.positions.get`, `sorted`, `str`, `sum`
- L573–617 **`KawananNPC.broadcast._for_distance`** · kontrol=17, assignment/delete=18, except=0 · Call: `annotated.append`, `copy.deepcopy`, `drive_map.items`, `enumerate`, `expanded.append`, `float`, `isinstance`, `item.get`, `item.pop`, `item.setdefault`, `max`, `raw.get`, `raw.items`, `round`, `sorted`, `str`
- L661–664 **`KawananNPC.hud_all`** · kontrol=1, assignment/delete=0, except=0 · Call: `n.hud_state`, `self.npcs.items`
- L666–667 **`KawananNPC.brief`** · kontrol=1, assignment/delete=0, except=0 · Call: `n.brief`, `self.npcs.values`
- L670–707 **`KawananNPC.interaksi`** · kontrol=2, assignment/delete=6, except=0 · Call: `dict`, `float`, `isinstance`, `jepit_drive`, `na.berinteraksi`, `na.kenal`, `nb.berinteraksi`, `nb.kenal`, `rel_a.get`, `rel_a.update`, `rel_b.get`, `rel_b.update`, `self._record_relation`
- L709–737 **`KawananNPC.biarkan_bersosialisasi`** · kontrol=6, assignment/delete=3, except=0 · Call: `dipakai.add`, `enumerate`, `hasil.append`, `kv[1].deficit`, `len`, `n.deficit`, `self.interaksi`, `self.npcs.items`, `set`, `sorted`
- L740–742 **`KawananNPC._cell_key`** · kontrol=1, assignment/delete=1, except=0 · Call: `float`, `int`, `list`, `math.floor`, `max`, `tuple`
- L745–759 **`KawananNPC._offsets`** · kontrol=8, assignment/delete=1, except=0 · Call: `hasil.append`, `range`
- L761–766 **`KawananNPC._reindex_grid`** · kontrol=1, assignment/delete=2, except=0 · Call: `self._cell_key`, `self._grid.setdefault`, `self._grid.setdefault(self._cell_key(pos), set()).add`, `self.positions.items`, `set`, `str`
- L768–782 **`KawananNPC._nearby`** · kontrol=5, assignment/delete=5, except=0 · Call: `float`, `int`, `len`, `math.ceil`, `max`, `out.update`, `range`, `self._cell_key`, `self._grid.get`, `self._offsets`, `self._reindex_grid`, `set`, `tuple`
- L784–802 **`KawananNPC._pairs_within`** · kontrol=7, assignment/delete=4, except=0 · Call: `len`, `math.sqrt`, `max`, `pairs.append`, `range`, `self._nearby`, `self._reindex_grid`, `self.positions.get`, `self.positions.items`, `str`, `sum`
- L804–815 **`KawananNPC.tick_batch`** · kontrol=3, assignment/delete=2, except=0 · Call: `action_cost.get`, `bool`, `events.get`, `isinstance`, `n._buffer_events`, `n.tick`, `self.npcs.items`
- L818–825 **`KawananNPC.wake`** · kontrol=1, assignment/delete=3, except=0 · Call: `int`, `max`, `self._wake.get`, `self.npcs.get`, `str`
- L827–843 **`KawananNPC.should_wake`** · kontrol=8, assignment/delete=1, except=0 · Call: `any`, `getattr`, `int`, `n.deficit`, `self.npcs.get`, `str`
- L845–861 **`KawananNPC.tick_event_driven`** · kontrol=3, assignment/delete=6, except=0 · Call: `action_cost.get`, `bool`, `events.get`, `isinstance`, `len`, `n._buffer_events`, `n.tick`, `self.npcs.items`, `self.should_wake`
- L864–884 **`KawananNPC.emotional_contagion`** · kontrol=5, assignment/delete=10, except=0 · Call: `float`, `jepit_01`, `len`, `max`, `na.emosi.get`, `nb.emosi.get`, `self._pairs_within`, `set`, `tersentuh.add`
- L887–914 **`KawananNPC.social_learn`** · kontrol=7, assignment/delete=9, except=1 · Call: `(getattr(nb, '_action_values', {}) or {}).get`, `_diag.catat`, `float`, `getattr`, `int`, `jepit_drive`, `max`, `na._action_values.setdefault`, `round`, `self._reputasi.catat`, `self.npcs.get`, `slot.get`, `str`
- L916–918 **`KawananNPC.teaching`** · kontrol=0, assignment/delete=0, except=0 · Call: `self.social_learn`
- L920–951 **`KawananNPC.form_cultural_norms`** · kontrol=15, assignment/delete=9, except=1 · Call: `_diag.catat`, `counts.get`, `counts.items`, `float`, `getattr`, `ks.set_value`, `list`, `max`, `round`, `self.npcs.values`
- L960–967 **`KawananNPC._gossip_valence`** · kontrol=5, assignment/delete=3, except=0 · Call: `jepit_drive`, `max`, `str`, `str(konten or '').lower`, `sum`
- L969–1011 **`KawananNPC.gossip_round`** · kontrol=10, assignment/delete=11, except=1 · Call: `_diag.catat`, `float`, `g.get`, `getattr`, `self._gossip_valence`, `self._max_tick`, `self._nearby`, `self._penilaian_sumber`, `self._reputasi.decay`, `self._reputasi.report`, `self._reputasi.sebar`, `self.npcs.get`, `self.npcs.items`, `self.positions.get`, `str`, `tks.tandai_alarm_palsu`
- L1013–1031 **`KawananNPC.shared_narrative`** · kontrol=3, assignment/delete=5, except=0 · Call: `entri.get`, `float`, `hasil.append`, `hasil.sort`, `hitung.setdefault`, `hitung.values`, `int`, `len`, `max`, `round`, `set`, `slot['muatan'].append`, `slot['sumber'].add`, `str`, `sum`
- L1033–1034 **`KawananNPC._max_tick`** · kontrol=1, assignment/delete=0, except=0 · Call: `max`, `self.npcs.values`
- L1037–1049 **`KawananNPC.share_prediction`** · kontrol=2, assignment/delete=3, except=0 · Call: `dict`, `len`, `self._predictions.append`, `self.npcs.get`, `str`
- L1051–1081 **`KawananNPC.resolve_predictions`** · kontrol=7, assignment/delete=10, except=1 · Call: `_diag.catat`, `abs`, `float`, `hasil.append`, `max`, `min`, `p.get`, `p.get('forecast', {}).get`, `round`, `self._prediction_credit.get`, `self._reputasi.catat`, `self.npcs.get`, `str`, `str(p.get('stimulus', '')).lower`, `str(p.get('stimulus', ''))[:60].lower`, `str(stimulus).lower`, `str(stimulus)[:60].lower`
- L1083–1086 **`KawananNPC.prediction_leaderboard`** · kontrol=1, assignment/delete=0, except=0 · Call: `round`, `self._prediction_credit.items`, `sorted`
- L1089–1110 **`KawananNPC.tick_layered`** · kontrol=3, assignment/delete=7, except=0 · Call: `action_cost.get`, `bool`, `events.get`, `isinstance`, `len`, `n.heavy_computation`, `n.tick_light`, `self.npcs.items`, `set`
- L1113–1170 **`KawananNPC._penilaian_sumber`** · kontrol=16, assignment/delete=23, except=1 · Call: `(getattr(ks, 'biases', {}) or {}).get`, `_diag.catat`, `alasan.append`, `bool`, `float`, `getattr`, `int`, `jepit_01`, `len`, `on.relasi`, `r.get`, `round`, `self._reputasi._p`, `self._source_trust.get`, `self.npcs.get`, `self.npcs.items`, `str`, `sum`, `vals.append`
- L1172–1174 **`KawananNPC.trust_weight`** · kontrol=0, assignment/delete=0, except=0 · Call: `self._penilaian_sumber`
- L1176–1195 **`KawananNPC._tandai_listener_alarm`** · kontrol=5, assignment/delete=5, except=1 · Call: `_diag.catat`, `getattr`, `int`, `ks.tandai_alarm_palsu`, `self.npcs.items`, `str`
- L1198–1218 **`KawananNPC._gossip_tentang`** · kontrol=9, assignment/delete=5, except=0 · Call: `g.get`, `getattr`, `int`, `out.append`, `self._gossip_valence`, `self._max_tick`, `self.npcs.items`, `str`
- L1220–1221 **`KawananNPC._faction_label`** · kontrol=0, assignment/delete=0, except=0 · Call: tidak ada
- L1223–1310 **`KawananNPC.echo_chamber`** · kontrol=23, assignment/delete=20, except=3 · Call: `_diag.catat`, `adj.get`, `adj[a].add`, `adj[b].add`, `enumerate`, `faksi.append`, `float`, `getattr`, `hasattr`, `int`, `komp.append`, `komponen.append`, `ks.harden_belief`, `ks.hold_belief`, `len`, `max`, `na._emosi_aktif`, `na._emosi_naikkan`, `na.berinteraksi`, `ra['relasi'].get`, `round`, `seen.add`, `self._faction_label`, `self._faksi.append`, `self._gossip_tentang`, `self._max_tick`, `self.npcs.get`, `set`, `sorted`, `str`, `tumpukan.extend`, `tumpukan.pop`, `x.get`
- L1312–1314 **`KawananNPC.faksi`** · kontrol=1, assignment/delete=0, except=0 · Call: `dict`
- L1317–1392 **`KawananNPC.konfrontasi`** · kontrol=17, assignment/delete=13, except=4 · Call: `_diag.catat`, `_proses`, `f.get`, `float`, `getattr`, `hasil['dipulihkan'].append`, `ks.koreksi_ingatan`, `ks.terima_bukti`, `list`, `max`, `min`, `n.berinteraksi`, `r.get`, `self._max_tick`, `self._reputasi._unit.get`, `self._reputasi.sebar`, `self._source_trust.get`, `self.npcs.get`, `self.npcs[kid].berinteraksi`, `slot.get`, `str`
- L1333–1351 **`KawananNPC.konfrontasi._proses`** · kontrol=4, assignment/delete=2, except=2 · Call: `_diag.catat`, `getattr`, `hasil['dipulihkan'].append`, `ks.koreksi_ingatan`, `ks.terima_bukti`, `n.berinteraksi`, `self.npcs.get`, `str`
- L1395–1402 **`KawananNPC._eskalasi_cerita`** · kontrol=0, assignment/delete=1, except=0 · Call: `int`, `len`, `max`, `min`
- L1404–1463 **`KawananNPC.decay_of_truth`** · kontrol=15, assignment/delete=14, except=2 · Call: `_diag.catat`, `any`, `g.get`, `getattr`, `hasil.append`, `int`, `ks.confabulate`, `ks.misremember`, `list`, `max`, `min`, `pemegang.append`, `r.get`, `r0.get`, `self._eskalasi_cerita`, `self._max_tick`, `self._reputasi._unit.items`, `self._reputasi.sebar`, `self._truth_decay.get`, `self.npcs.items`, `self.trust_weight`, `slot.get`, `st.get`, `str`, `x.get`
- L1465–1477 **`KawananNPC.konfirmasi_rumor`** · kontrol=6, assignment/delete=5, except=0 · Call: `getattr`, `r.get`, `self._reputasi._unit.get`, `self._reputasi._unit.get(eid, {}).get`, `self._truth_decay.pop`, `str`
- L1479–1481 **`KawananNPC.peluruhan_kebenaran`** · kontrol=1, assignment/delete=0, except=0 · Call: `dict`, `self._truth_decay.items`
- L1484–1486 **`KawananNPC.konsensus`** · kontrol=0, assignment/delete=0, except=0 · Call: `self._reputasi.konsensus`
- L1489–1506 **`KawananNPC.to_dict`** · kontrol=6, assignment/delete=0, except=0 · Call: `'profil tidak dikenal: {!r}'.format`, `ValueError`, `copy.deepcopy`, `dict`, `float`, `list`, `n.to_dict`, `self._prediction_credit.items`, `self._reputasi.to_dict`, `self._source_trust.items`, `self.npcs.items`, `self.positions.items`
- L1509–1558 **`KawananNPC.from_dict`** · kontrol=32, assignment/delete=16, except=4 · Call: `((data or {}).get('positions') or {}).items`, `((data or {}).get('prediction_credit') or {}).items`, `((data or {}).get('relation_matrix') or {}).items`, `((data or {}).get('source_trust') or {}).items`, `(data or {}).get`, `(data or {}).get('npcs', {}).items`, `Naluri.from_dict`, `_diag.catat`, `cls`, `copy.deepcopy`, `dict`, `float`, `int`, `isinstance`, `jepit_01`, `jepit_drive`, `max`, `obj._reputasi.from_dict`, `obj.set_position`, `rel.get`, `row.items`, `str`, `validasi_state`
- L1560–1562 **`KawananNPC.to_json`** · kontrol=0, assignment/delete=0, except=0 · Call: `json.dumps`, `json_kwargs.setdefault`, `self.to_dict`
- L1565–1566 **`KawananNPC.from_json`** · kontrol=0, assignment/delete=0, except=0 · Call: `cls.from_dict`, `json.loads`
- L1568–1570 **`KawananNPC.save`** · kontrol=0, assignment/delete=0, except=0 · Call: `self.to_dict`, `simpan_json`
- L1573–1575 **`KawananNPC.load`** · kontrol=0, assignment/delete=0, except=0 · Call: `cls.from_dict`, `muat_json`

## `pycos/inti/keadaan.py`

SHA-256: `b3c0911b130c6b4ae0eabb5b2c1b120c52eddb32906db9c7adf63d36581f8352`

61 baris; 2 kelas; 4 fungsi/metode termasuk nested.

Kelas: `Goal` L7, `Mood` L35.
Handler luas: tidak ada.

Impor (termasuk lazy/TYPE_CHECKING): `from __future__ import annotations`; `from dataclasses import dataclass, asdict, field`; `from typing import Any, Dict, List, Optional`.

- L16–17 **`Goal.to_dict`** · kontrol=0, assignment/delete=0, except=0 · Call: `asdict`
- L19–20 **`Goal.active_subgoal`** · kontrol=1, assignment/delete=0, except=0 · Call: `next`
- L23–31 **`Goal.from_dict`** · kontrol=2, assignment/delete=0, except=0 · Call: `bool`, `cls`, `cls.from_dict`, `data.get`, `float`, `int`, `isinstance`, `str`
- L39–58 **`Mood.modulation`** · kontrol=0, assignment/delete=6, except=0 · Call: `max`

## `pycos/inti/kesadaran.py`

SHA-256: `f426e7cd67d567bc4aa8cb7ab8b93809e8e20d40682c1ae0b59e6a52df83be3d`

4220 baris; 1 kelas; 174 fungsi/metode termasuk nested.

Kelas: `Kesadaran` L50.
Handler luas: 28, 827, 846, 999, 1584, 1658, 1866, 1962, 1989, 2131, 2867, 3146, 3325, 3537, 3544, 3601, 3744, 3756, 3809, 457, 609, 615, 944, 1119, 1473, 1792, 1830, 1936, 1984, 2051, 2379, 2862, 3724, 3799, 2761, 3453, 3672, 1956, 2849.

Impor (termasuk lazy/TYPE_CHECKING): `from __future__ import annotations`; `from pycos.bahasa.teks import jenis_kalimat`; `from pycos.bahasa.teks import jenis_pertanyaan, ekstrak_topik`; `from pycos.dukungan import diagnostik as _diag`; `from pycos.dukungan.numerik import jepit, jepit_01`; `from pycos.dukungan.validasi_state import validasi_state`; `from pycos.inti._konfigurasi import DRIVES, EMOSI_ALIASES, EPISTEMIC_ALIASES, EPISTEMIC_EMOTIONS, FELT_STATES, KESADARAN_DEFAULTS, MORAL_ALIASES, MORAL_EMOTIONS, REALITY_SOURCES, SELF_BIASES, _MAKS_LOSSES, _kclip`; `from pycos.inti.naluri import SASPAnalyzer`; `from pycos.refleksi.nurani import Nurani as _Nurani`; `from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple`; `import copy`; `import math`; `import random`; `import re`.

- L13–47 **`_pertanyaan_balik`** · kontrol=14, assignment/delete=8, except=1 · Call: `_diag.catat`, `ekstrak_topik`, `jenis_pertanyaan`, `jp.get`, `str`, `str(ekstrak_topik(s) or '').strip`, `str(jp.get('jenis') or '').strip`, `str(jp.get('jenis') or '').strip().lower`, `str(pembicara or 'kamu').strip`, `str(teks or '').strip`
- L65–245 **`Kesadaran.__init__`** · kontrol=7, assignment/delete=98, except=0 · Call: `'tubuh:{}:{}'.format`, `copy.deepcopy`, `getattr`, `random.Random`, `self._tick`, `str`
- L248–252 **`Kesadaran.enabled`** · kontrol=1, assignment/delete=0, except=0 · Call: `bool`, `self.params.get`
- L254–261 **`Kesadaran._p`** · kontrol=2, assignment/delete=2, except=1 · Call: `KESADARAN_DEFAULTS.get`, `float`, `isinstance`, `self.params.get`, `v.get`
- L263–264 **`Kesadaran._tick`** · kontrol=0, assignment/delete=0, except=0 · Call: `getattr`, `int`
- L266–267 **`Kesadaran._levels`** · kontrol=1, assignment/delete=0, except=0 · Call: `dict`, `getattr`
- L269–270 **`Kesadaran._emosi`** · kontrol=1, assignment/delete=0, except=0 · Call: `dict`, `getattr`
- L272–273 **`Kesadaran._nama`** · kontrol=1, assignment/delete=0, except=0 · Call: `getattr`, `str`
- L278–297 **`Kesadaran.observe_event`** · kontrol=6, assignment/delete=7, except=0 · Call: `_kclip`, `abs`, `ev.get`, `float`, `isinstance`, `max`, `min`, `self._event_content`, `self.enabled`, `self.submit`, `str`
- L299–318 **`Kesadaran.daftar_lantai_kesadaran`** · kontrol=0, assignment/delete=1, except=0 · Call: `_kclip`, `bool`, `dict`, `self._lantai_kesadaran.append`, `str`
- L320–321 **`Kesadaran.set_konteks_lantai`** · kontrol=0, assignment/delete=1, except=0 · Call: `bool`
- L323–350 **`Kesadaran._kondisi_lantai_aktif`** · kontrol=17, assignment/delete=5, except=0 · Call: `all`, `any`, `bool`, `em.get`, `em.values`, `float`, `getattr`, `isinstance`, `kondisi.get`, `kondisi.strip`, `kondisi.strip().lower`, `lv.get`, `max`, `self._emosi`, `self._kondisi_lantai_aktif`, `self._levels`, `str`, `sumber.get`
- L352–362 **`Kesadaran._tekanan_residu_lantai`** · kontrol=2, assignment/delete=4, except=0 · Call: `_kclip`, `float`, `getattr`, `max`, `residu.tekanan_target`
- L364–383 **`Kesadaran._lolos_lantai`** · kontrol=6, assignment/delete=6, except=0 · Call: `aturan.get`, `bool`, `float`, `item.get`, `self._kondisi_lantai_aktif`, `self._lantai_log.append`, `self._tekanan_residu_lantai`, `self._tick`, `str`, `tag.startswith`
- L385–407 **`Kesadaran.submit`** · kontrol=4, assignment/delete=3, except=0 · Call: `(detail or {}).get`, `_kclip`, `bool`, `dict`, `len`, `self._lolos_lantai`, `self._tick`, `self.workspace.append`, `str`
- L410–418 **`Kesadaran._event_content`** · kontrol=3, assignment/delete=1, except=0 · Call: `str`
- L420–494 **`Kesadaran._candidates`** · kontrol=19, assignment/delete=6, except=1 · Call: `_diag.catat`, `abs`, `add`, `c.get`, `cm.get`, `dict`, `float`, `g.get`, `getattr`, `int`, `lv.items`, `min`, `out.append`, `self._drive_phrase`, `self._emosi`, `self._emosi().items`, `self._felt_phrase`, `self._levels`, `self._lolos_lantai`, `self._tick`, `self.felt.items`, `self.grief.items`, `str`
- L424–428 **`Kesadaran._candidates.add`** · kontrol=1, assignment/delete=0, except=0 · Call: `out.append`, `self._lolos_lantai`
- L497–498 **`Kesadaran.attention_fatigue`** · kontrol=0, assignment/delete=0, except=0 · Call: `float`, `jepit_01`
- L501–502 **`Kesadaran.attentional_fatigue`** · kontrol=0, assignment/delete=0, except=0 · Call: tidak ada
- L504–518 **`Kesadaran._recover_attention`** · kontrol=4, assignment/delete=7, except=1 · Call: `float`, `max`, `self._p`, `self._tick`, `self.enabled`
- L520–543 **`Kesadaran.attention_effort`** · kontrol=8, assignment/delete=8, except=1 · Call: `float`, `jepit`, `jepit_01`, `len`, `min`, `re.findall`, `round`, `self._attention_log.append`, `self._recover_attention`, `self._tick`, `self.enabled`, `str`, `str(text or '').count`, `sum`
- L545–555 **`Kesadaran.attention_state`** · kontrol=0, assignment/delete=1, except=0 · Call: `dict`, `max`, `round`, `self._p`, `self.enabled`
- L558–564 **`Kesadaran._drive_phrase`** · kontrol=0, assignment/delete=1, except=0 · Call: `tabel.get`
- L567–574 **`Kesadaran._felt_phrase`** · kontrol=0, assignment/delete=1, except=0 · Call: `tabel.get`
- L576–648 **`Kesadaran.attend`** · kontrol=17, assignment/delete=25, except=2 · Call: `_diag.catat`, `_kclip`, `c.get`, `dict`, `float`, `getattr`, `int`, `len`, `max`, `min`, `round`, `scored.append`, `scored.sort`, `self._candidates`, `self._detect_change_blindness`, `self._ignite`, `self._p`, `self._recover_attention`, `self._rng.gauss`, `self._tick`, `self.attention_effort`, `self.enabled`, `self.spotlight[0].get`, `top.get`, `urg.get`
- L650–673 **`Kesadaran._ignite`** · kontrol=4, assignment/delete=6, except=0 · Call: `dict`, `ev.get`, `float`, `int`, `item.get`, `len`, `max`, `round`, `self._broadcast.append`, `self._p`, `self._remember_episode`, `self._tick`, `self.enabled`, `self.ignitions.append`
- L675–690 **`Kesadaran._detect_change_blindness`** · kontrol=7, assignment/delete=5, except=0 · Call: `before.get`, `c.get`, `len`, `next`, `reversed`, `self._tick`, `self.blindness_log.append`, `str`, `w.get`
- L692–704 **`Kesadaran.inattentional_blindness`** · kontrol=4, assignment/delete=3, except=0 · Call: `bool`, `len`, `self._tick`, `self.blindness_log.append`, `self.enabled`, `str`
- L706–731 **`Kesadaran.workspace_report`** · kontrol=9, assignment/delete=3, except=0 · Call: `(c.get('detail') or {}).get`, `boleh`, `bool`, `c.get`, `dict`, `float`, `max`, `next`, `reversed`, `round`, `self._tick`, `self.attention_state`, `self.enabled`
- L733–759 **`Kesadaran.decision_bias`** · kontrol=12, assignment/delete=8, except=0 · Call: `any`, `ev.get`, `float`, `item.get`, `m.get`, `self.enabled`
- L764–785 **`Kesadaran.inner_speech`** · kontrol=7, assignment/delete=8, except=0 · Call: `c.get`, `int`, `len`, `next`, `self._identity_relevant`, `self._p`, `self._speak_template`, `self._tick`, `self.enabled`, `self.self_talk.append`, `str`, `top.get`
- L790–797 **`Kesadaran._self_audition_reaction_now`** · kontrol=0, assignment/delete=2, except=0 · Call: `float`, `int`, `jepit_01`, `max`, `min`, `raw.get`, `round`, `self._tick`
- L799–947 **`Kesadaran.audition_self`** · kontrol=26, assignment/delete=36, except=4 · Call: `_Nurani._lexical_words`, `_diag.catat`, `bool`, `copy.deepcopy`, `dict`, `emosi.get`, `felt.get`, `float`, `getattr`, `heard.lower`, `intended.get`, `isinstance`, `jepit_01`, `len`, `max`, `min`, `niat.strip`, `ord`, `re.search`, `reaksi.items`, `round`, `self._emosi`, `self._self_audition_log.append`, `self._self_audition_reaction_now`, `self._tick`, `self._withholding_terms`, `self.attention_effort`, `self.enabled`, `self.grief.values`, `self.submit`, `set`, `str`, `str(utterance or '').strip`, `suara.get`, `sum`, `x.get`
- L952–958 **`Kesadaran.self_audition_state`** · kontrol=0, assignment/delete=0, except=0 · Call: `copy.deepcopy`, `len`, `max`, `self._self_audition_reaction_now`, `self.enabled`
- L963–1001 **`Kesadaran._speak_template`** · kontrol=23, assignment/delete=2, except=1 · Call: `_diag.catat`, `any`, `isi.lower`, `self._rng.choice`
- L1003–1009 **`Kesadaran._identity_relevant`** · kontrol=2, assignment/delete=1, except=0 · Call: `isi.lower`, `self._identity_traits.items`, `sorted`
- L1011–1036 **`Kesadaran.form_identity`** · kontrol=7, assignment/delete=7, except=0 · Call: `cm.get`, `float`, `item.get`, `self._emosi`, `self._emosi().items`, `self._refresh_identity`, `self.enabled`, `str`
- L1038–1053 **`Kesadaran._refresh_identity`** · kontrol=6, assignment/delete=3, except=0 · Call: `_kclip`, `any`, `evidence.items`, `len`, `round`, `self._identity_traits.get`, `self._identity_traits.items`, `self._tick`, `self.narrative_identity.append`, `sorted`, `x.get`
- L1055–1060 **`Kesadaran.narrative_state`** · kontrol=1, assignment/delete=1, except=0 · Call: `max`, `x.get`
- L1062–1063 **`Kesadaran.last_thought`** · kontrol=1, assignment/delete=0, except=0 · Call: `x.get`
- L1068–1122 **`Kesadaran.tandai_core_memory`** · kontrol=15, assignment/delete=9, except=1 · Call: `(episode or {}).get`, `_diag.catat`, `dict`, `float`, `getattr`, `hasattr`, `int`, `it.get`, `jepit`, `len`, `next`, `nur.tandai_core`, `reversed`, `self._p`, `self._refresh_identity`, `self._remember_episode`, `self._tick`, `self._top_emotion`, `self.core_memory.append`, `self.core_memory.sort`, `self.enabled`, `str`, `x.get`
- L1124–1126 **`Kesadaran.core_memory_state`** · kontrol=1, assignment/delete=0, except=0 · Call: `dict`, `len`
- L1128–1152 **`Kesadaran._remember_episode`** · kontrol=3, assignment/delete=4, except=0 · Call: `bool`, `ev.get`, `float`, `int`, `len`, `ranked.sort`, `round`, `self._p`, `self._tick`, `self._top_emotion`, `self._update_chapter`, `self.enabled`, `self.timeline.append`, `sorted`, `str`, `x.get`
- L1154–1166 **`Kesadaran._update_chapter`** · kontrol=4, assignment/delete=6, except=0 · Call: `getattr`, `int`, `item.get`, `len`, `self._chapter_label`, `self._p`, `self._tick`, `self.chapters.append`, `str`
- L1168–1178 **`Kesadaran._chapter_label`** · kontrol=4, assignment/delete=1, except=0 · Call: `item.get`, `self._tick`, `str`
- L1180–1185 **`Kesadaran.life_chapters`** · kontrol=2, assignment/delete=1, except=0 · Call: `dict`, `out.append`
- L1187–1216 **`Kesadaran.future_simulation`** · kontrol=7, assignment/delete=7, except=0 · Call: `_kclip`, `batas_tubuh.get`, `getattr`, `int`, `len`, `lv.get`, `round`, `self._anticipatory_emotion`, `self._levels`, `self._tick`, `self.body_locus_state`, `self.constrain_imagination`, `self.enabled`, `self.future_sim.append`, `str`
- L1218–1224 **`Kesadaran._anticipatory_emotion`** · kontrol=1, assignment/delete=2, except=0 · Call: `lv.get`, `max`, `proyeksi.get`, `round`, `self._levels`, `sum`
- L1226–1249 **`Kesadaran.counterfactual`** · kontrol=8, assignment/delete=8, except=0 · Call: `abs`, `em.items`, `float`, `len`, `max`, `min`, `round`, `self._counterfactual_log.append`, `self._tick`, `self.counterfactual_emotions.get`, `self.enabled`, `str`
- L1251–1259 **`Kesadaran.mental_time_travel`** · kontrol=3, assignment/delete=0, except=0 · Call: tidak ada
- L1264–1267 **`Kesadaran.act`** · kontrol=0, assignment/delete=0, except=0 · Call: `_kclip`, `self._tick`, `str`
- L1269–1291 **`Kesadaran.feedback`** · kontrol=2, assignment/delete=9, except=0 · Call: `_kclip`, `abs`, `len`, `max`, `rencana.get`, `round`, `self._agency_log.append`, `self._levels`, `self._levels().get`, `self._p`, `self._tick`, `self.enabled`, `str`
- L1293–1302 **`Kesadaran.body_ownership`** · kontrol=1, assignment/delete=4, except=0 · Call: `_kclip`, `self._p`, `self.enabled`
- L1304–1337 **`Kesadaran.update_body_locus`** · kontrol=13, assignment/delete=10, except=3 · Call: `all`, `coords.append`, `float`, `isinstance`, `len`, `list`, `math.isfinite`, `max`, `min`, `raw.get`, `self.body_locus_state`
- L1339–1350 **`Kesadaran.body_locus_state`** · kontrol=0, assignment/delete=0, except=0 · Call: `float`, `int`, `len`, `list`, `round`, `self._body_locus.get`, `str`
- L1352–1426 **`Kesadaran.constrain_imagination`** · kontrol=25, assignment/delete=27, except=1 · Call: `any`, `bool`, `dest.append`, `float`, `isinstance`, `len`, `list`, `m_menjadi.group`, `math.sqrt`, `range`, `raw.get`, `re.search`, `round`, `self._body_imagination_log.append`, `self._body_locus.get`, `self._nama`, `self._nama().strip`, `self._nama().strip().lower`, `self._tick`, `str`, `str(mode or 'auto').strip`, `str(mode or 'auto').strip().lower`, `str(mode or 'auto').strip().lower().replace`, `str(target if target is not None else inferred_target or '').strip`, `sum`, `target_name.lower`, `teks.lower`
- L1428–1432 **`Kesadaran.imagine_from_body`** · kontrol=0, assignment/delete=0, except=0 · Call: `self.constrain_imagination`
- L1437–1444 **`Kesadaran.agency_state`** · kontrol=0, assignment/delete=0, except=0 · Call: `round`, `self.body_locus_state`, `self.enabled`
- L1449–1501 **`Kesadaran._update_felt`** · kontrol=11, assignment/delete=15, except=1 · Call: `_diag.catat`, `_kclip`, `bool`, `float`, `getattr`, `int`, `jepit`, `len`, `lv.get`, `max`, `nur.felt_state.get`, `round`, `self._levels`, `self._p`, `self._somatic_tag`, `self._tick`, `self.naluri.mood`, `self.somatic_markers.append`, `target.get`, `urg.get`
- L1504–1507 **`Kesadaran._somatic_tag`** · kontrol=0, assignment/delete=0, except=0 · Call: `{'sesak': 'keamanan', 'jantung': 'keamanan', 'tegang': 'keamanan', 'nyeri': 'keamanan', 'lelah': 'energi', 'lapar': 'energi', 'mual': 'koherensi', 'ringan': 'energi'}.get`
- L1509–1529 **`Kesadaran.moral_emotion`** · kontrol=6, assignment/delete=2, except=0 · Call: `MORAL_ALIASES.get`, `_kclip`, `float`, `self._bias_emosi`, `self._p`, `self.enabled`, `str`, `str(emosi).lower`
- L1531–1576 **`Kesadaran.epistemic_emotion`** · kontrol=6, assignment/delete=12, except=0 · Call: `EPISTEMIC_ALIASES.get`, `_kclip`, `int`, `jepit_01`, `max`, `nama.replace`, `round`, `self._epistemic_log.append`, `self._p`, `self._tick`, `self.enabled`, `self.epistemic_body.get`, `str`, `str(emosi or '').strip`, `str(emosi or '').strip().lower`, `tekstur.items`, `{'bingung': {'dahi_mengerut': 0.65, 'napas_tertahan': 0.16}, 'penasaran': {'tubuh_condong': 0.6, 'dahi_mengerut': 0.12}, 'lega': {'dada_mengendur': 0.5, 'bahu_rileks': 0.65}, 'malu_tidak_tahu': {'wajah_hangat': 0.68, 'tubuh_condong': -0.18}, 'takjub': {'napas_tertahan': 0.52, 'dahi_mengerut': 0.18}, 'frustrasi': {'rahang_tegang': 0.62, 'dahi_mengerut': 0.35}, 'yakin': {'dada_mengendur': 0.18, 'bahu_rileks': 0.22}, 'bosan': {'tubuh_condong': -0.25, 'dahi_mengerut': 0.1}}.get`
- L1578–1600 **`Kesadaran._update_epistemic_from_state`** · kontrol=4, assignment/delete=6, except=1 · Call: `_diag.catat`, `_kclip`, `float`, `max`, `self.enabled`, `self.naluri.deficit`
- L1602–1615 **`Kesadaran.epistemic_emotion_state`** · kontrol=2, assignment/delete=2, except=0 · Call: `dict`, `float`, `max`, `round`, `self.enabled`, `self.epistemic_body.items`, `self.epistemic_emotions.get`, `self.epistemic_emotions.items`
- L1617–1633 **`Kesadaran.epistemic_report`** · kontrol=1, assignment/delete=5, except=0 · Call: `self.epistemic_emotion_state`, `st.get`, `{'bingung': 'aku bingung; pikiranku mengerut mencari pola', 'penasaran': 'ada sesuatu yang ingin kupahami; tubuhku condong ke arahnya', 'lega': 'aku lega karena kini mulai tahu', 'malu_tidak_tahu': 'aku malu karena tidak tahu, dan sulit menatap lurus', 'takjub': 'aku terdiam, takjub pada hal yang baru kupahami', 'frustrasi': 'aku frustrasi karena jawabannya belum terbuka', 'yakin': 'aku merasa cukup yakin dengan yang kuketahui', 'bosan': 'pola ini terasa jenuh; aku ingin melakukan sesuatu yang berbeda'}.get`
- L1635–1720 **`Kesadaran.self_opacity`** · kontrol=20, assignment/delete=25, except=1 · Call: `EMOSI_ALIASES.get`, `_diag.catat`, `_kclip`, `bool`, `float`, `int`, `max`, `round`, `self._p`, `self._self_opacity_log.append`, `self._tick`, `self._top_emotion`, `self._top_emotion().lower`, `self.enabled`, `self.epistemic_emotion`, `self.self_opacity_state`, `self.submit`, `state.get`, `state.update`, `str`, `str(perasaan_dikenali or '').strip`, `str(perasaan_dikenali or '').strip().lower`, `str(perasaan_laten or '').strip`, `str(perasaan_laten or '').strip().lower`, `str(sebab_diyakini or '').strip`, `str(sebab_diyakini or '').strip().lower`, `str(sebab_laten or '').strip`, `str(sebab_laten or '').strip().lower`
- L1724–1736 **`Kesadaran.self_opacity_state`** · kontrol=4, assignment/delete=4, except=0 · Call: `copy.deepcopy`, `item.items`, `self.enabled`, `state.pop`
- L1738–1743 **`Kesadaran._bias_emosi`** · kontrol=3, assignment/delete=2, except=0 · Call: `_kclip`, `getattr`, `isinstance`, `self.enabled`
- L1745–1762 **`Kesadaran.felt_report`** · kontrol=6, assignment/delete=9, except=0 · Call: `dict`, `epistemik.get`, `max`, `opasitas.get`, `round`, `self._felt_phrase`, `self.enabled`, `self.epistemic_report`, `self.felt.items`, `self.moral.items`, `self.self_opacity_state`, `str`
- L1767–1778 **`Kesadaran.classify_reality`** · kontrol=4, assignment/delete=1, except=0 · Call: `item.get`, `str`
- L1780–1805 **`Kesadaran.reality_check`** · kontrol=6, assignment/delete=7, except=1 · Call: `_diag.catat`, `item.get`, `len`, `min`, `round`, `self._rng.random`, `self._tick`, `self.classify_reality`, `self.enabled`, `self.epistemic_emotion`, `self.reality.get`, `self.source_log.append`, `str`
- L1807–1816 **`Kesadaran.source_memory`** · kontrol=4, assignment/delete=1, except=0 · Call: `e.get`, `e.get('isi', '').lower`, `next`, `reversed`, `self.enabled`, `tentang.lower`
- L1818–1841 **`Kesadaran.metacognitive_doubt`** · kontrol=5, assignment/delete=6, except=1 · Call: `_diag.catat`, `_kclip`, `abs`, `float`, `getattr`, `min`, `self._p`, `self.enabled`, `self.epistemic_emotion`
- L1843–1854 **`Kesadaran.confabulate`** · kontrol=3, assignment/delete=4, except=0 · Call: `int`, `len`, `self._p`, `self._plausible_story`, `self._tick`, `self.confabulations.append`, `self.enabled`, `str`
- L1856–1868 **`Kesadaran._plausible_story`** · kontrol=1, assignment/delete=2, except=1 · Call: `_diag.catat`, `self._rng.choice`
- L1870–1878 **`Kesadaran.reality_report`** · kontrol=1, assignment/delete=0, except=0 · Call: `len`, `round`, `self.enabled`, `self.reality.items`
- L1883–1888 **`Kesadaran.attention_limits`** · kontrol=0, assignment/delete=0, except=0 · Call: `len`, `max`, `self._tick`, `self.enabled`
- L1894–1895 **`Kesadaran._eid`** · kontrol=0, assignment/delete=0, except=0 · Call: `getattr`, `str`
- L1897–1909 **`Kesadaran.joint_attention`** · kontrol=2, assignment/delete=6, except=0 · Call: `dict`, `int`, `len`, `self._eid`, `self._joint_attention.setdefault`, `self._shared_history.append`, `self._tick`, `self.enabled`, `slot.get`, `str`
- L1911–1918 **`Kesadaran.recursive_tom`** · kontrol=1, assignment/delete=3, except=0 · Call: `_kclip`, `dict`, `round`, `self._eid`, `self._recursive_tom.setdefault`, `self.enabled`, `str`
- L1920–1939 **`Kesadaran.commit`** · kontrol=5, assignment/delete=4, except=1 · Call: `_diag.catat`, `dict`, `getattr`, `hasattr`, `int`, `len`, `nur.tambah_utang`, `self._eid`, `self._p`, `self._tick`, `self.commitments.append`, `self.enabled`, `str`
- L1941–1968 **`Kesadaran.betray`** · kontrol=8, assignment/delete=4, except=2 · Call: `_diag.catat`, `c.get`, `getattr`, `hasattr`, `nur.tambah_utang`, `self._bias_emosi`, `self._eid`, `self._refresh_identity`, `self._tick`, `self.enabled`, `self.moral_emotion`, `self.naluri.nurani.interact`, `str`
- L1970–1993 **`Kesadaran.forgive`** · kontrol=8, assignment/delete=3, except=2 · Call: `_diag.catat`, `c.get`, `getattr`, `hasattr`, `nur.bayar_utang`, `self._eid`, `self._tick`, `self.enabled`, `self.moral_emotion`, `self.naluri.nurani.interact`, `str`
- L1995–2005 **`Kesadaran.gossip`** · kontrol=2, assignment/delete=2, except=0 · Call: `dict`, `int`, `len`, `self._eid`, `self._p`, `self._tick`, `self.enabled`, `self.gossip_log.append`, `str`
- L2007–2021 **`Kesadaran.tandai_alarm_palsu`** · kontrol=1, assignment/delete=3, except=0 · Call: `len`, `min`, `self._tick`, `self.reality.get`, `self.source_log.append`, `str`
- L2023–2060 **`Kesadaran.terima_bukti`** · kontrol=9, assignment/delete=9, except=1 · Call: `_diag.catat`, `_kclip`, `dict`, `dilunakkan.append`, `float`, `jepit_01`, `len`, `round`, `self._bukti_log.append`, `self._tick`, `self.dissonance.items`, `self.enabled`, `self.forgive`, `slot.get`, `str`
- L2062–2094 **`Kesadaran.koreksi_ingatan`** · kontrol=8, assignment/delete=12, except=0 · Call: `(str(bl.get('sebelum', '')) + ' ' + str(bl.get('sesudah', ''))).lower`, `(str(c.get('celah', '')) + ' ' + str(c.get('cerita', ''))).lower`, `_kclip`, `bl.get`, `c.get`, `dict`, `dikoreksi.append`, `len`, `self._koreksi_log.append`, `self._tick`, `str`, `str(asli)[:60].lower`
- L2096–2101 **`Kesadaran.konfrontasi_state`** · kontrol=3, assignment/delete=0, except=0 · Call: `dict`, `float`, `s.get`, `self.dissonance.values`, `sum`
- L2103–2112 **`Kesadaran.second_person_state`** · kontrol=2, assignment/delete=1, except=0 · Call: `c.get`, `dict`, `self._eid`, `self._joint_attention.get`, `self._recursive_tom.get`, `self.enabled`
- L2117–2146 **`Kesadaran.dialogue_turn`** · kontrol=5, assignment/delete=11, except=1 · Call: `_diag.catat`, `_pertanyaan_balik`, `int`, `jenis_kalimat`, `pembicara.lower`, `self.enabled`, `self.repair`, `str`, `str(teks).strip`, `str(teks).strip().endswith`, `t.get`
- L2148–2156 **`Kesadaran.backchannel`** · kontrol=2, assignment/delete=2, except=0 · Call: `len`, `self._tick`, `self.backchannels.append`, `self.enabled`, `str`
- L2194–2238 **`Kesadaran.repair`** · kontrol=15, assignment/delete=14, except=0 · Call: `any`, `dict`, `konteks.get`, `len`, `self._JENIS_KE_STRATEGI.get`, `self._STRATEGI_REPAIR[pilih]['frasa']`, `self._tick`, `self.repairs.append`, `str`, `str(jenis).strip`, `str(jenis).strip().lower`, `str(sebab).lower`
- L2240–2246 **`Kesadaran.pragmatics_state`** · kontrol=0, assignment/delete=0, except=0 · Call: `dict`, `self.enabled`
- L2249–2256 **`Kesadaran._withholding_terms`** · kontrol=3, assignment/delete=2, except=0 · Call: `len`, `re.findall`, `set`, `str`, `str(text or '').lower`
- L2258–2313 **`Kesadaran.withhold_speech`** · kontrol=10, assignment/delete=12, except=0 · Call: `' '.join`, `'terbiasa menahan {}'.format`, `_kclip`, `ada.get`, `bool`, `float`, `getattr`, `int`, `len`, `max`, `next`, `ord`, `penerima.lower`, `self._refresh_identity`, `self._tick`, `self._withheld_speech.append`, `self._withholding_terms`, `self.params.get`, `sorted`, `str`, `str(content or '').strip`, `str(topic or '').strip`, `str(x.get('kepada', '')).lower`, `str(x.get('topik', '')).lower`, `sum`, `topik.lower`, `x.get`
- L2318–2347 **`Kesadaran.withheld_for`** · kontrol=15, assignment/delete=7, except=0 · Call: `(str(getattr(recipient, 'name', recipient)) if recipient is not None else '').lower`, `copy.deepcopy`, `getattr`, `incoming.lower`, `item.get`, `len`, `max`, `reversed`, `self._withholding_terms`, `self.turn_state.get`, `str`, `str(item.get('kepada', '') or '').lower`, `str(item.get('topik', '')).lower`, `str(self.turn_state.get('topic', '') or '').strip`, `str(topic or '').strip`
- L2349–2387 **`Kesadaran.record_withholding_attempt`** · kontrol=8, assignment/delete=11, except=1 · Call: `'terbiasa menahan {}'.format`, `_diag.catat`, `_kclip`, `float`, `getattr`, `int`, `item.get`, `min`, `next`, `nur.enabled`, `nur.interact`, `round`, `self._refresh_identity`, `self._tick`, `str`, `x.get`
- L2389–2395 **`Kesadaran.withholding_relationship_tension`** · kontrol=3, assignment/delete=1, except=0 · Call: `float`, `getattr`, `max`, `str`, `str(getattr(recipient, 'name', recipient) or '').lower`, `str(x.get('kepada', '')).lower`, `x.get`
- L2397–2406 **`Kesadaran.withholding_state`** · kontrol=4, assignment/delete=2, except=0 · Call: `any`, `copy.deepcopy`, `dict`, `items.append`, `len`, `raw.items`, `x.get`
- L2408–2429 **`Kesadaran.choose_to_disclose`** · kontrol=4, assignment/delete=7, except=0 · Call: `int`, `item.get`, `next`, `self._tick`, `self._withholding_disclosure_log.append`, `str`, `x.get`
- L2434–2451 **`Kesadaran.model_other_belief`** · kontrol=5, assignment/delete=6, except=0 · Call: `_kclip`, `model.setdefault`, `self._eid`, `self._other_belief_models.setdefault`, `self._tick`, `self.enabled`, `str`, `str(proposisi or '').strip`
- L2453–2458 **`Kesadaran.other_belief_model`** · kontrol=1, assignment/delete=1, except=0 · Call: `copy.deepcopy`, `self._eid`, `self._other_belief_models.get`
- L2460–2504 **`Kesadaran.choose_to_lie`** · kontrol=10, assignment/delete=11, except=0 · Call: `' '.join`, `_kclip`, `int`, `max`, `norm`, `re.findall`, `self._eid`, `self._p`, `self._refresh_identity`, `self._strategic_deceptions.append`, `self._tick`, `self.enabled`, `self.submit`, `str`, `str(falsehood or '').strip`, `str(goal or '').strip`, `str(intended_belief or lie).strip`, `str(known_truth or '').strip`, `str(topic or '').strip`, `x.lower`
- L2510–2528 **`Kesadaran.strategic_speech_for`** · kontrol=10, assignment/delete=4, except=0 · Call: `copy.deepcopy`, `item.get`, `reversed`, `self._eid`, `self._withholding_terms`, `self.enabled`, `str`
- L2530–2552 **`Kesadaran.deliver_strategic_speech`** · kontrol=3, assignment/delete=5, except=0 · Call: `float`, `int`, `item.get`, `model.setdefault`, `model.setdefault('keyakinan', {}).setdefault`, `next`, `reversed`, `round`, `self._other_belief_models.setdefault`, `self._tick`, `str`, `x.get`
- L2554–2594 **`Kesadaran.plan_manipulation`** · kontrol=14, assignment/delete=11, except=0 · Call: `int`, `isinstance`, `len`, `max`, `normalized.append`, `raw.get`, `self._eid`, `self._manipulation_plans.append`, `self._p`, `self._tick`, `self.enabled`, `str`, `str(goal or '').strip`, `str(raw or '').strip`, `str(raw.get('aksi', raw.get('action', 'mengamati')) or 'mengamati').strip`, `str(raw.get('ujaran', raw.get('utterance', raw.get('teks', ''))) or '').strip`
- L2598–2618 **`Kesadaran.next_manipulation_action`** · kontrol=8, assignment/delete=4, except=0 · Call: `copy.deepcopy`, `int`, `len`, `plan.get`, `reversed`, `self._eid`, `self._withholding_terms`, `self.enabled`, `step.get`
- L2620–2648 **`Kesadaran.record_manipulation_step`** · kontrol=7, assignment/delete=9, except=0 · Call: `copy.deepcopy`, `dict`, `float`, `int`, `isinstance`, `len`, `max`, `next`, `outcome.get`, `plan.get`, `reversed`, `self._tick`, `self.model_other_belief`, `str`, `x.get`
- L2650–2665 **`Kesadaran.record_manipulation_outcome`** · kontrol=3, assignment/delete=4, except=0 · Call: `bool`, `int`, `next`, `reversed`, `self._tick`, `self.model_other_belief`, `str`, `x.get`
- L2667–2691 **`Kesadaran.roleplay`** · kontrol=7, assignment/delete=3, except=0 · Call: `bool`, `copy.deepcopy`, `dict`, `self._eid`, `self._tick`, `self.enabled`, `str`, `str(klaim or '').strip`, `str(peran or '').strip`
- L2696–2710 **`Kesadaran.roleplay_speech_for`** · kontrol=7, assignment/delete=3, except=0 · Call: `copy.deepcopy`, `self._eid`, `self.enabled`, `state.get`, `str`, `style.get`
- L2712–2718 **`Kesadaran.record_roleplay_speech`** · kontrol=2, assignment/delete=2, except=0 · Call: `self._roleplay_state.get`, `self._tick`
- L2720–2724 **`Kesadaran.end_roleplay`** · kontrol=0, assignment/delete=2, except=0 · Call: `copy.deepcopy`, `lama.get`
- L2726–2790 **`Kesadaran.choose_loyalty`** · kontrol=14, assignment/delete=18, except=1 · Call: `_diag.catat`, `_kclip`, `c.get`, `copy.deepcopy`, `dict`, `float`, `isinstance`, `item.get`, `len`, `min`, `n.relasi`, `raw.get`, `rel.get`, `round`, `scored.append`, `scored.sort`, `self._eid`, `self._strategic_loyalty.append`, `self._tick`, `self.enabled`, `spec.get`, `str`, `val`
- L2740–2745 **`Kesadaran.choose_loyalty.val`** · kontrol=2, assignment/delete=0, except=0 · Call: `_kclip`, `isinstance`, `spec.get`
- L2795–2817 **`Kesadaran.social_strategy_state`** · kontrol=7, assignment/delete=3, except=0 · Call: `copy.deepcopy`, `deceptions.append`, `len`, `raw.get`, `role.items`, `self.enabled`, `x.get`
- L2828–2885 **`Kesadaran.analisis_sa_sp`** · kontrol=23, assignment/delete=18, except=3 · Call: `SASPAnalyzer`, `_diag.catat`, `abs`, `callable`, `ctx.setdefault`, `dict`, `float`, `getattr`, `isinstance`, `label`, `len`, `max`, `min`, `prag.get`, `result.get`, `self._eid`, `self._sa_sp_analyzer.analisis`, `self.enabled`, `self.epistemic_emotion`, `self.observe_sa_sp`, `str`, `type`, `x.get`
- L2889–2893 **`Kesadaran.sa_sp_state`** · kontrol=0, assignment/delete=0, except=0 · Call: `copy.deepcopy`, `len`, `self.enabled`
- L2896–2909 **`Kesadaran._free_will_action_names`** · kontrol=7, assignment/delete=4, except=1 · Call: `action.get`, `dict.fromkeys`, `isinstance`, `list`, `out.append`, `str`, `str(action or '').strip`
- L2911–2976 **`Kesadaran.free_will_choose_goal`** · kontrol=9, assignment/delete=14, except=0 · Call: `' '.join`, `_kclip`, `copy.deepcopy`, `existing.get`, `goal_text.lower`, `int`, `max`, `re.findall`, `reversed`, `round`, `self._free_will_action_names`, `self._free_will_events.append`, `self._free_will_goals.append`, `self._p`, `self._refresh_identity`, `self._tick`, `self.enabled`, `self.submit`, `str`, `str(description or '').strip`, `str(existing.get('tujuan', '')).lower`
- L2981–3018 **`Kesadaran.free_will_decide_goal`** · kontrol=8, assignment/delete=9, except=0 · Call: `_kclip`, `dict`, `enumerate`, `isinstance`, `item.get`, `max`, `round`, `scored.append`, `self._free_will_action_names`, `self.enabled`, `self.free_will_choose_goal`, `str`, `str(item.get('tujuan', item.get('goal', item.get('description', ''))) or '').strip`
- L3023–3030 **`Kesadaran.free_will_current_goal`** · kontrol=3, assignment/delete=1, except=0 · Call: `copy.deepcopy`, `float`, `int`, `max`, `self.enabled`, `x.get`
- L3032–3068 **`Kesadaran.free_will_action_bonus`** · kontrol=20, assignment/delete=14, except=0 · Call: `any`, `candidate.get`, `float`, `goal.get`, `int`, `isinstance`, `labels.append`, `len`, `max`, `min`, `re.findall`, `round`, `self._p`, `self.free_will_current_goal`, `str`, `str(candidate.get('name', candidate.get('aksi', ''))).strip`, `str(candidate.get('name', candidate.get('aksi', ''))).strip().lower`, `str(candidate.get(key)).strip`, `str(candidate.get(key)).strip().lower`, `str(goal.get('tujuan', '')).lower`, `str(x).strip`, `str(x).strip().lower`
- L3070–3088 **`Kesadaran.free_will_progress`** · kontrol=5, assignment/delete=6, except=0 · Call: `_kclip`, `float`, `goal.get`, `goal.setdefault`, `goal.setdefault('hasil', []).append`, `max`, `next`, `self._tick`, `str`, `x.get`
- L3090–3101 **`Kesadaran.free_will_cancel_goal`** · kontrol=4, assignment/delete=4, except=0 · Call: `next`, `self._tick`, `str`, `x.get`
- L3103–3110 **`Kesadaran.free_will_state`** · kontrol=1, assignment/delete=0, except=0 · Call: `copy.deepcopy`, `len`, `self.enabled`, `x.get`
- L3115–3137 **`Kesadaran.hold_belief`** · kontrol=5, assignment/delete=5, except=0 · Call: `_kclip`, `dict`, `float`, `int`, `len`, `self._defense`, `self._tick`, `self.denials.append`, `self.dissonance.setdefault`, `self.enabled`, `slot.get`, `slot['bukti'].append`, `str`
- L3139–3148 **`Kesadaran._defense`** · kontrol=1, assignment/delete=1, except=1 · Call: `_diag.catat`, `self._rng.choice`
- L3150–3158 **`Kesadaran.bias`** · kontrol=2, assignment/delete=3, except=0 · Call: `_kclip`, `float`, `self.enabled`, `str`, `str(jenis).lower`
- L3160–3169 **`Kesadaran.misremember`** · kontrol=1, assignment/delete=1, except=0 · Call: `self._tick`, `self.blindness_log.append`, `self.enabled`, `str`
- L3171–3180 **`Kesadaran.harden_belief`** · kontrol=1, assignment/delete=2, except=0 · Call: `float`, `max`, `self.bias`, `self.dissonance.setdefault`, `self.enabled`, `slot.get`, `str`
- L3182–3190 **`Kesadaran.fallibility_state`** · kontrol=2, assignment/delete=0, except=0 · Call: `float`, `len`, `round`, `s.get`, `self.biases.items`, `self.dissonance.values`, `self.enabled`
- L3195–3203 **`Kesadaran.set_value`** · kontrol=1, assignment/delete=3, except=0 · Call: `_kclip`, `float`, `self._p`, `self.enabled`, `self.values.get`, `str`
- L3205–3211 **`Kesadaran.add_boundary`** · kontrol=2, assignment/delete=1, except=0 · Call: `list`, `self.boundaries.append`, `self.enabled`, `str`
- L3213–3222 **`Kesadaran.add_quirk`** · kontrol=3, assignment/delete=3, except=0 · Call: `len`, `list`, `self.enabled`, `self.quirks.append`, `str`
- L3224–3249 **`Kesadaran.refuse`** · kontrol=9, assignment/delete=7, except=0 · Call: `any`, `b.lower`, `len`, `max`, `self._refresh_identity`, `self._tick`, `self.enabled`, `self.refusals.append`, `self.values.items`, `str`, `str(permintaan).lower`
- L3251–3258 **`Kesadaran.values_state`** · kontrol=1, assignment/delete=0, except=0 · Call: `list`, `round`, `self.enabled`, `self.values.items`, `sorted`
- L3263–3297 **`Kesadaran.aesthetic_response`** · kontrol=8, assignment/delete=12, except=0 · Call: `_kclip`, `any`, `copy.deepcopy`, `dict`, `f.get`, `round`, `self._tick`, `self.enabled`, `self.epistemic_emotion`, `str`, `str(stimulus or '').strip`, `teks.lower`
- L3299–3353 **`Kesadaran.playful_reframe`** · kontrol=13, assignment/delete=15, except=1 · Call: `_diag.catat`, `_kclip`, `callable`, `copy.deepcopy`, `fn`, `getattr`, `int`, `max`, `min`, `round`, `self._eid`, `self._humor_log.append`, `self._p`, `self._tick`, `self.enabled`, `self.epistemic_emotion`, `self.submit`, `str`, `str(frame_alternatif or '').strip`, `str(frame_literal or '').strip`, `str(jenis or 'humor').strip`, `str(jenis or 'humor').strip().lower`, `str(ujaran or '').strip`
- L3358–3387 **`Kesadaran.observe_sa_sp`** · kontrol=11, assignment/delete=6, except=0 · Call: `(analisis.get('pragmatik') or {}).get`, `analisis.get`, `copy.deepcopy`, `frames.get`, `isinstance`, `self._eid`, `self._sa_sp_log.append`, `self._tick`, `self.enabled`, `self.playful_reframe`, `social.get`, `str`
- L3389–3395 **`Kesadaran.play_aesthetics_state`** · kontrol=0, assignment/delete=0, except=0 · Call: `copy.deepcopy`, `len`, `self.enabled`
- L3400–3410 **`Kesadaran.mortality_salience_update`** · kontrol=2, assignment/delete=3, except=0 · Call: `_kclip`, `float`, `self._p`, `self.enabled`
- L3412–3424 **`Kesadaran.face_death`** · kontrol=1, assignment/delete=1, except=0 · Call: `round`, `self._bias_emosi`, `self._refresh_identity`, `self._tick`, `self.enabled`, `self.moral_emotion`, `self.submit`, `str`
- L3426–3456 **`Kesadaran.grieve`** · kontrol=6, assignment/delete=8, except=1 · Call: `_diag.catat`, `_kclip`, `callable`, `daftar`, `dict`, `float`, `getattr`, `len`, `max`, `self._bias_emosi`, `self._eid`, `self._remember_episode`, `self._tick`, `self.enabled`, `self.grief.setdefault`, `self.losses.append`, `self.moral_emotion`, `slot.get`, `str`
- L3458–3464 **`Kesadaran.mortality_state`** · kontrol=1, assignment/delete=0, except=0 · Call: `float`, `len`, `round`, `self.enabled`, `self.grief.items`, `v.get`
- L3469–3520 **`Kesadaran.sleep_insight`** · kontrol=13, assignment/delete=16, except=0 · Call: `' '.join`, `copy.deepcopy`, `enumerate`, `gagasan.lower`, `int`, `kanan.lower`, `kiri.lower`, `len`, `max`, `re.findall`, `self._dream_material`, `self._p`, `self._tick`, `self.enabled`, `self.epistemic_emotion`, `self.self_talk.append`, `self.sleep_insights.append`, `self.submit`, `str`, `str(x).strip`, `str(x.get('gagasan', '')).lower`, `sumber.extend`, `x.get`
- L3522–3526 **`Kesadaran.insight_report`** · kontrol=0, assignment/delete=0, except=0 · Call: `copy.deepcopy`, `len`, `self.enabled`
- L3528–3561 **`Kesadaran.dream`** · kontrol=7, assignment/delete=12, except=2 · Call: `(getattr(self.naluri, 'urgency', {}) or {}).values`, `_diag.catat`, `bool`, `getattr`, `int`, `len`, `max`, `self._bias_emosi`, `self._dream_material`, `self._dream_pending.append`, `self._dream_scenario`, `self._emosi`, `self._emosi().get`, `self._p`, `self._tick`, `self.dream_log.append`, `self.enabled`, `self.sleep_insight`
- L3563–3593 **`Kesadaran._dream_material`** · kontrol=18, assignment/delete=4, except=0 · Call: `bahan.append`, `c.get`, `getattr`, `goal.get`, `isinstance`, `item.get`, `self._sa_sp_log[-1].get`, `str`
- L3595–3603 **`Kesadaran._dream_scenario`** · kontrol=2, assignment/delete=1, except=1 · Call: `_diag.catat`
- L3605–3612 **`Kesadaran.dream_report`** · kontrol=3, assignment/delete=1, except=0 · Call: `d.get`, `self.enabled`
- L3614–3636 **`Kesadaran.wake`** · kontrol=2, assignment/delete=4, except=0 · Call: `_kclip`, `bool`, `copy.deepcopy`, `list`, `round`, `self._tick`, `self.dream_report`, `self.enabled`, `self.last_dream.get`
- L3638–3643 **`Kesadaran.dream_state`** · kontrol=0, assignment/delete=0, except=0 · Call: `len`, `round`, `self.enabled`, `self.insight_report`
- L3648–3729 **`Kesadaran.step`** · kontrol=23, assignment/delete=14, except=2 · Call: `_diag.catat`, `_kclip`, `bool`, `c.get`, `callable`, `dict`, `float`, `g.get`, `getattr`, `int`, `langsung.get`, `max`, `pembangkit`, `self._decay`, `self._ignite`, `self._p`, `self._recover_attention`, `self._seed_from_state`, `self._tick`, `self._update_epistemic_from_state`, `self._update_felt`, `self._update_identity_from_state`, `self.attend`, `self.check_narrative_coherence`, `self.enabled`, `self.form_identity`, `self.future_simulation`, `self.grief.items`, `self.inner_speech`, `self.metacognitive_doubt`, `self.mortality_salience_update`, `self.params.get`, `self.reality_check`
- L3731–3758 **`Kesadaran._seed_from_state`** · kontrol=5, assignment/delete=5, except=2 · Call: `_diag.catat`, `getattr`, `max`, `self._rng.choice`, `self.quirks.append`, `self.values.setdefault`
- L3760–3769 **`Kesadaran._update_identity_from_state`** · kontrol=4, assignment/delete=4, except=0 · Call: `self._emosi`, `self._emosi().get`, `self._refresh_identity`
- L3771–3803 **`Kesadaran.check_narrative_coherence`** · kontrol=17, assignment/delete=4, except=1 · Call: `' | '.join`, `' | '.join((str(x.get('klaim', '')) for x in self.narrative_identity)).lower`, `_diag.catat`, `c.get`, `hasattr`, `kontradiksi.append`, `len`, `self._emosi`, `self._emosi().get`, `self._tick`, `self.harden_belief`, `self.hold_belief`, `str`, `sum`, `x.get`
- L3805–3811 **`Kesadaran._top_emotion`** · kontrol=1, assignment/delete=1, except=1 · Call: `_diag.catat`, `self.naluri.emosi_dominan`
- L3813–3832 **`Kesadaran._decay`** · kontrol=6, assignment/delete=7, except=0 · Call: `_kclip`, `jepit`, `max`
- L3839–3841 **`Kesadaran.global_workspace`** · kontrol=0, assignment/delete=0, except=0 · Call: `list`
- L3844–3846 **`Kesadaran.attention_spotlight`** · kontrol=0, assignment/delete=0, except=0 · Call: `list`
- L3849–3851 **`Kesadaran.sense_of_agency`** · kontrol=0, assignment/delete=0, except=0 · Call: tidak ada
- L3854–3856 **`Kesadaran.felt_state`** · kontrol=0, assignment/delete=0, except=0 · Call: `dict`
- L3858–3861 **`Kesadaran.confabulation`** · kontrol=0, assignment/delete=0, except=0 · Call: `self.confabulate`
- L3863–3866 **`Kesadaran.cognitive_dissonance`** · kontrol=0, assignment/delete=0, except=0 · Call: `self.hold_belief`
- L3868–3871 **`Kesadaran.commitment`** · kontrol=0, assignment/delete=0, except=0 · Call: `self.commit`
- L3873–3875 **`Kesadaran.betrayal`** · kontrol=0, assignment/delete=0, except=0 · Call: `self.betray`
- L3877–3879 **`Kesadaran.forgiveness`** · kontrol=0, assignment/delete=0, except=0 · Call: `self.forgive`
- L3881–3894 **`Kesadaran.nightmare`** · kontrol=1, assignment/delete=5, except=0 · Call: `max`, `self._bias_emosi`, `self._dream_material`, `self._dream_pending.append`, `self._dream_scenario`, `self._tick`, `self.dream_log.append`, `self.enabled`
- L3896–3928 **`Kesadaran.report`** · kontrol=3, assignment/delete=0, except=0 · Call: `bool`, `c.get`, `len`, `round`, `self.agency_state`, `self.attention_limits`, `self.counterfactual_emotions.items`, `self.dream_state`, `self.epistemic_report`, `self.fallibility_state`, `self.felt_report`, `self.free_will_state`, `self.insight_report`, `self.last_thought`, `self.life_chapters`, `self.mortality_state`, `self.params.get`, `self.play_aesthetics_state`, `self.pragmatics_state`, `self.reality_report`, `self.sa_sp_state`, `self.second_person_state`, `self.self_audition_state`, `self.self_opacity_state`, `self.social_strategy_state`, `self.values_state`, `self.workspace_report`, `x.get`
- L3930–3949 **`Kesadaran.hud_state`** · kontrol=1, assignment/delete=0, except=0 · Call: `bool`, `c.get`, `round`, `self.epistemic_report`, `self.epistemic_report().get`, `self.felt_report`, `self.felt_report().get`, `self.last_dream.get`, `self.last_sleep_insight.get`, `self.life_chapters`, `self.life_chapters()[-1].get`, `self.narrative_state`, `self.params.get`, `self.self_audition_state`, `self.self_opacity_state`, `self.self_opacity_state().get`
- L3951–4051 **`Kesadaran.to_dict`** · kontrol=50, assignment/delete=0, except=0 · Call: `bool`, `copy.deepcopy`, `dict`, `float`, `int`, `list`, `self._identity_traits.items`, `self.biases.items`, `self.counterfactual_emotions.items`, `self.epistemic_body.items`, `self.epistemic_emotions.items`, `self.felt.items`, `self.moral.items`, `self.reality.items`, `self.values.items`
- L4053–4217 **`Kesadaran.from_dict`** · kontrol=132, assignment/delete=101, except=0 · Call: `(data.get('biases') or {}).items`, `(data.get('counterfactual_emotions') or {}).items`, `(data.get('epistemic_body') or {}).items`, `(data.get('epistemic_emotions') or {}).items`, `(data.get('felt') or {}).items`, `(data.get('identity_traits') or {}).items`, `(data.get('moral') or {}).items`, `(data.get('reality') or {}).items`, `(data.get('values') or {}).items`, `_kclip`, `bool`, `copy.deepcopy`, `data.get`, `dict`, `float`, `int`, `isinstance`, `max`, `self._body_locus.update`, `self._self_audition_reaction.update`, `self._self_opacity.update`, `self._tick`, `self.play_state.update`, `str`, `validasi_state`, `x.get`

## `pycos/inti/mesin.py`

SHA-256: `a08945851762dd01cbb001a7d6b0970764b051c9ad57b7497ce2bbd0290a6a43`

4934 baris; 1 kelas; 177 fungsi/metode termasuk nested.

Kelas: `Naluri` L27.
Handler luas: 302, 319, 3171, 3743, 3849, 3880, 4179, 4212, 4223, 505, 543, 610, 633, 651, 661, 667, 870, 877, 884, 891, 1397, 2359, 2369, 3139, 3274, 3284, 3597, 3707, 4193, 4416, 4884, 4891, 4898, 530, 562, 2141, 2643, 3263, 3292, 3362, 3725, 3730, 3868, 3714, 3813, 3348, 3359.

Impor (termasuk lazy/TYPE_CHECKING): `from __future__ import annotations`; `from pycos.bahasa.teks import cakupan_negasi, tokenisasi`; `from pycos.bahasa.teks import normalisasi_token as _norm_tok`; `from pycos.dukungan import diagnostik as _diag`; `from pycos.dukungan.batas_memori import BATAS`; `from pycos.dukungan.batas_memori import batas as _batas_memori, pangkas as _pangkas_memori`; `from pycos.dukungan.numerik import float_hingga, jepit, jepit_01, jepit_drive`; `from pycos.dukungan.parameter import periksa_params`; `from pycos.dukungan.persistensi import muat_json`; `from pycos.dukungan.persistensi import simpan_json`; `from pycos.dukungan.validasi_state import validasi_state`; `from pycos.inti._konfigurasi import DEFAULTS, DRIVES, DRIVE_ATTENTION, DRIVE_NEUROMOD, EMOSI, EMOSI_ALIASES, EMOSI_HUD_THRESHOLD, EMOSI_LABELS, EMOSI_PERSEPSI, GOAL_TEMPLATES, HUD_DRIVE_INTENT, HUD_MOOD_LABELS, KESADARAN_DEFAULTS, LEXICON, LEXICON_PACKS, LOD_ALIASES, LOD_DIVISOR_FACTOR, LOD_MODES, PERSONALITIES, PERSONALITY_ALIASES, SLEEP_MODES, SLEEP_MODE_ALIASES, STAGE_WEIGHTS, TAG_LEXICON, _nilai_per_drive, _periksa_kunci_drive`; `from pycos.inti.demo.skenario import _simulasi_harian`; `from pycos.inti.keadaan import Goal, Mood`; `from pycos.inti.kesadaran import Kesadaran`; `from pycos.inti.naluri import CalibrationReport`; `from pycos.inti.naluri import Nurani`; `from pycos.inti.naluri import _get_attr`; `from pycos.inti.presentasi import PRESENTASI_DEFAULTS, Presentasi`; `from pycos.inti.ritual import Ritual`; `from typing import Any, Callable, Dict, Iterable, List, Mapping, Optional, Tuple, TYPE_CHECKING`; `import copy`; `import json`; `import math`; `import random`; `import re`; `import time`.

- L30–258 **`Naluri.__init__`** · kontrol=19, assignment/delete=84, except=0 · Call: `'initial_levels[{}] = {} di luar rentang [-1, 1]'.format`, `'initial_levels[{}]'.format`, `'weights[{}]'.format`, `Kesadaran`, `LEXICON.items`, `Nurani`, `Presentasi`, `Ritual`, `TAG_LEXICON.items`, `ValueError`, `_periksa_kunci_drive`, `copy.deepcopy`, `dict`, `float`, `float_hingga`, `initial_levels.items`, `int`, `isinstance`, `lexicon.items`, `max`, `periksa_params`, `random.Random`, `self.params.get`, `self.params.update`, `self.set_lod`, `self.set_personality_preset`, `self.weights.update`, `str`, `str(w).lower`, `tag_lexicon.items`, `weights.items`
- L262–275 **`Naluri.set_stage`** · kontrol=2, assignment/delete=2, except=0 · Call: `ValueError`, `dict`, `self.set_personality_preset`
- L277–288 **`Naluri.advance_stage_by_ticks`** · kontrol=3, assignment/delete=4, except=0 · Call: `self.set_stage`
- L290–338 **`Naluri.subjective_time_profile`** · kontrol=15, assignment/delete=18, except=2 · Call: `(getattr(ks, 'grief', {}) or {}).values`, `_diag.catat`, `em.get`, `float`, `getattr`, `jepit`, `jepit_01`, `levels.get`, `max`, `min`, `self.mood`, `x.get`
- L340–343 **`Naluri.subjective_time_state`** · kontrol=0, assignment/delete=0, except=0 · Call: `float`, `int`, `round`, `self.subjective_time_profile`
- L345–350 **`Naluri._advance_subjective_time`** · kontrol=0, assignment/delete=3, except=0 · Call: `float`, `max`, `self.subjective_time_profile`
- L353–420 **`Naluri.tick`** · kontrol=15, assignment/delete=14, except=1 · Call: `LOD_DIVISOR_FACTOR.get`, `_pangkas_memori`, `bool`, `callable`, `dict`, `getattr`, `isinstance`, `list`, `self._advance_subjective_time`, `self._buffer_events`, `self._event_log.append`, `self._physics`, `self._profile_add`, `time.perf_counter`, `vacancy_aktif`, `vacancy_lewat`
- L422–427 **`Naluri._buffer_events`** · kontrol=2, assignment/delete=0, except=0 · Call: `_pangkas_memori`, `dict`, `isinstance`, `self._event_buffer.append`
- L429–679 **`Naluri._physics`** · kontrol=58, assignment/delete=57, except=9 · Call: `_diag.catat`, `_nilai_per_drive`, `_pangkas_memori`, `all`, `any`, `bool`, `c.get`, `callable`, `checkpoint`, `dict`, `float`, `fokus.get`, `getattr`, `int`, `jepit`, `jepit_drive`, `len`, `max`, `max(self.context_aktif, key=lambda c: float(c.get('salience', 0.0))).get`, `nur.enabled`, `nur.interoceptive_echo`, `nur.relative_deficit`, `nur.update_interoception`, `nur.update_setpoints`, `self._advance_coping_focus`, `self._advance_working_memory`, `self._decay_eligibility_traces`, `self._emosi_apresiasi`, `self._emosi_peluruh`, `self._introspeksi_aktif`, `self._kesadaran_aktif`, `self._lod_heavy`, `self._persepsi_aktif`, `self._persepsi_spontan`, `self._presentasi_aktif`, `self._rebuild_goals`, `self._ritual_aktif`, `self._valensi_mentah`, `self.advance_stage_by_ticks`, `self.apply_events`, `self.deficit_ticks.get`, `self.kesadaran.step`, `self.mood`, `self.nurani._felt`, `self.nurani._p`, `self.nurani.detect_conflict`, `self.nurani.enabled`, `self.nurani.felt_consciousness`, `self.nurani.inner_speech`, `self.nurani.update_adaptasi`, `self.nurani.update_felt`, `self.nurani.update_introspection`, `self.params.get`, `self.presentasi.tick`, `self.ritual.tick`, `self.tick_history.append`, `str`, `vacancy_aktif`, `vacancy_lewat`, `x.get`
- L682–693 **`Naluri._buffer_memori`** · kontrol=0, assignment/delete=0, except=0 · Call: tidak ada
- L695–705 **`Naluri.memori_state`** · kontrol=2, assignment/delete=3, except=0 · Call: `_batas_memori`, `buffers.values`, `len`, `self._buffer_memori`, `self._buffer_memori().items`, `sum`
- L707–717 **`Naluri.batasi_memori`** · kontrol=3, assignment/delete=2, except=0 · Call: `_batas_memori`, `_pangkas_memori`, `isinstance`, `len`, `list`, `max`, `self._buffer_memori`, `self._buffer_memori().items`, `self.memori_state`
- L719–812 **`Naluri.kompres_memori`** · kontrol=12, assignment/delete=24, except=0 · Call: `(kv[1].get('deltas', {}) or {}).values`, `(slot.get('deltas', {}) or {}).values`, `ValueError`, `abs`, `aliases.get`, `copy.deepcopy`, `float`, `getattr`, `hasattr`, `int`, `kv[1].get`, `len`, `max`, `min`, `nur._affective.items`, `nur._sig_cache.clear`, `slot.get`, `sorted`, `str`, `str(level).lower`, `str(level).lower().strip`
- L815–837 **`Naluri.set_lod`** · kontrol=5, assignment/delete=4, except=0 · Call: `', '.join`, `LOD_ALIASES.get`, `ValueError`, `int`, `max`, `self.kompres_memori`, `self.lod_status`, `str`, `str(mode).lower`
- L839–842 **`Naluri._lod_heavy`** · kontrol=1, assignment/delete=0, except=0 · Call: tidak ada
- L844–852 **`Naluri.tick_light`** · kontrol=1, assignment/delete=3, except=0 · Call: `self.tick`
- L854–894 **`Naluri.heavy_computation`** · kontrol=9, assignment/delete=5, except=4 · Call: `_diag.catat`, `self._introspeksi_aktif`, `self._kesadaran_aktif`, `self._presentasi_aktif`, `self._ritual_aktif`, `self.kesadaran.step`, `self.mood`, `self.nurani.update_introspection`, `self.presentasi.tick`, `self.ritual.tick`
- L896–899 **`Naluri.lod_status`** · kontrol=0, assignment/delete=0, except=0 · Call: `len`
- L901–961 **`Naluri.apply_events`** · kontrol=24, assignment/delete=15, except=1 · Call: `', '.join`, `'; '.join`, `'drive tidak dikenal: {!r}'.format`, `'events[{}]'.format`, `ValueError`, `_diag.catat`, `c.get`, `context_seen.add`, `enumerate`, `ev.get`, `float`, `float_hingga`, `isinstance`, `item.setdefault`, `jepit_drive`, `list`, `masalah.append`, `next`, `self._context_key`, `self._kesadaran_aktif`, `self._persepsi_aktif`, `self._persepsi_batch`, `self.delta`, `self.feel`, `self.kesadaran.observe_event`, `self.params.get`, `self.remember_context`, `set`, `sorted`, `str`
- L982–983 **`Naluri._persepsi_aktif`** · kontrol=0, assignment/delete=0, except=0 · Call: `bool`, `self.params.get`
- L985–986 **`Naluri._introspeksi_aktif`** · kontrol=1, assignment/delete=0, except=0 · Call: `bool`, `self.nurani.enabled`, `self.params.get`
- L988–991 **`Naluri._kesadaran_aktif`** · kontrol=1, assignment/delete=0, except=0 · Call: `bool`, `getattr`, `self.params.get`
- L993–996 **`Naluri._presentasi_aktif`** · kontrol=1, assignment/delete=0, except=0 · Call: `bool`, `getattr`, `self.params.get`
- L998–1001 **`Naluri._ritual_aktif`** · kontrol=1, assignment/delete=0, except=0 · Call: `bool`, `getattr`, `self.params.get`
- L1003–1015 **`Naluri._persepsi_gain_emosi`** · kontrol=4, assignment/delete=4, except=0 · Call: `EMOSI_PERSEPSI.items`, `float`, `peta.get`, `self._emosi_aktif`, `self.emosi.get`, `self.params.get`
- L1017–1035 **`Naluri._persepsi_topdown`** · kontrol=3, assignment/delete=6, except=0 · Call: `float`, `min`, `nur.anticipate_detail`, `prior.get`, `self.params.get`, `trust.get`
- L1037–1044 **`Naluri._catat_persepsi`** · kontrol=0, assignment/delete=0, except=0 · Call: `_pangkas_memori`, `float`, `round`, `self._persepsi_log.append`, `str`
- L1046–1117 **`Naluri._persepsi_batch`** · kontrol=16, assignment/delete=27, except=0 · Call: `abs`, `calon.append`, `calon.sort`, `dict`, `enumerate`, `ev.get`, `ev2.get`, `float`, `hasil.append`, `hasil[idx].get`, `int`, `jepit_01`, `len`, `math.copysign`, `max`, `nur.deteksi`, `nur.habit_factor`, `nur.kompres`, `round`, `self._catat_persepsi`, `self._persepsi_gain_emosi`, `self._persepsi_topdown`, `self.mood`, `self.params.get`, `self.urgency.get`, `str`
- L1119–1149 **`Naluri._persepsi_spontan`** · kontrol=5, assignment/delete=11, except=0 · Call: `_nilai_per_drive`, `abs`, `float`, `int`, `max`, `min`, `nur._p`, `nur._sens`, `self._catat_persepsi`, `self._emosi_aktif`, `self._rng.gauss`, `self._rng.random`, `self.delta`, `self.feel`, `self.params.get`
- L1151–1184 **`Naluri.persepsi`** · kontrol=5, assignment/delete=16, except=0 · Call: `abs`, `dict`, `float`, `imp.get`, `math.copysign`, `max`, `nur._sens`, `nur.habit_factor`, `nur.kompres`, `self._persepsi_aktif`, `self._persepsi_gain_emosi`, `self._persepsi_topdown`, `self.impact_of`
- L1186–1212 **`Naluri.affordances`** · kontrol=7, assignment/delete=12, except=0 · Call: `effects.get`, `float`, `isinstance`, `max`, `obj.get`, `self.impact_of`, `self.urgency.get`
- L1214–1220 **`Naluri._salience_kandidat`** · kontrol=3, assignment/delete=3, except=0 · Call: `(effects or {}).get`, `abs`, `float`, `self.urgency.get`
- L1222–1233 **`Naluri.persepsi_state`** · kontrol=1, assignment/delete=2, except=0 · Call: `dict`, `len`, `self._persepsi_aktif`, `self.nurani.persepsi_ringkas`
- L1235–1261 **`Naluri.delta`** · kontrol=7, assignment/delete=5, except=0 · Call: `'delta[{}]'.format`, `_pangkas_memori`, `any`, `bool`, `float`, `float_hingga`, `getattr`, `o.paralel.tanpa_resolusi`, `round`, `self.delta_log.append`, `str`, `str(reason).lower`
- L1263–1265 **`Naluri.deficit`** · kontrol=0, assignment/delete=0, except=0 · Call: `max`, `self.levels.get`
- L1268–1296 **`Naluri.mood`** · kontrol=5, assignment/delete=10, except=0 · Call: `Mood`, `jepit_01`, `jepit_drive`, `max`, `min`, `round`, `self.emosi.values`, `self.levels.values`, `self.params.get`, `self.urgency.values`, `self.weights.values`, `sum`
- L1299–1323 **`Naluri._rebuild_goals`** · kontrol=6, assignment/delete=11, except=0 · Call: `GOAL_TEMPLATES.get`, `Goal`, `int`, `len`, `new_goals.append`, `self._rng.choice`, `sorted`, `tpl.format`
- L1325–1330 **`Naluri._active_subgoal`** · kontrol=2, assignment/delete=1, except=0 · Call: `float`, `max`
- L1332–1360 **`Naluri.set_subgoal`** · kontrol=6, assignment/delete=10, except=0 · Call: `GOAL_TEMPLATES.get`, `Goal`, `ValueError`, `child.to_dict`, `float`, `int`, `jepit`, `max`, `next`, `parent.to_dict`, `self._rng.choice`, `self.goals.append`, `self.goals.sort`, `self.params.get`, `self.urgency.get`, `str`
- L1362–1377 **`Naluri.complete_subgoal`** · kontrol=5, assignment/delete=7, except=0 · Call: `float`, `g.active_subgoal`, `jepit_01`, `max`, `parent.active_subgoal`, `self.params.get`, `self.urgency.get`
- L1379–1404 **`Naluri.goal_to_scenario`** · kontrol=8, assignment/delete=10, except=1 · Call: `_diag.catat`, `c.get`, `context.get`, `float`, `len`, `max`, `own.get`, `self._kesadaran_aktif`, `self._rng.choice`, `self._rng.random`, `self.kesadaran.free_will_current_goal`, `str`, `top.active_subgoal`
- L1407–1409 **`Naluri.add_lexicon`** · kontrol=0, assignment/delete=2, except=0 · Call: `dict`, `word.lower`
- L1412–1414 **`Naluri._context_key`** · kontrol=1, assignment/delete=0, except=0 · Call: `' '.join`, `re.findall`, `str`, `str(text or '').lower`
- L1417–1423 **`Naluri._context_similarity`** · kontrol=4, assignment/delete=2, except=0 · Call: `len`, `max`, `re.findall`, `set`, `str`, `str(a or '').lower`, `str(b or '').lower`
- L1425–1504 **`Naluri.remember_context`** · kontrol=23, assignment/delete=33, except=0 · Call: `(found.get('delta') or {}).get`, `abs`, `actual_deltas.get`, `any`, `bool`, `c.get`, `copy.deepcopy`, `delta.get`, `dict`, `float`, `found.get`, `int`, `isinstance`, `jepit_01`, `jepit_drive`, `len`, `max`, `min`, `next`, `outcome.get`, `raw_deltas.get`, `raw_deltas.values`, `repeat.get`, `self._context_key`, `self._context_repeat.get`, `self._context_repeat.pop`, `self._context_repeat[k].get`, `self._context_similarity`, `self.context_aktif.append`, `self.context_aktif.sort`, `self.experience`, `self.impact_of`, `self.params.get`, `self.project_outcome_to_drives`, `str`, `str(stimulus or '').strip`
- L1506–1510 **`Naluri.clear_context`** · kontrol=0, assignment/delete=2, except=0 · Call: `len`
- L1512–1530 **`Naluri._advance_working_memory`** · kontrol=5, assignment/delete=11, except=0 · Call: `c.get`, `float`, `int`, `item.get`, `list`, `max`, `self._context_repeat.items`, `self._context_repeat.pop`, `self.params.get`
- L1532–1543 **`Naluri._working_memory_impact`** · kontrol=6, assignment/delete=4, except=0 · Call: `(item.get('delta') or {}).get`, `bool`, `float`, `item.get`, `max`, `self._context_similarity`, `self.params.get`
- L1545–1554 **`Naluri._working_memory_action_bias`** · kontrol=5, assignment/delete=2, except=0 · Call: `(c.get('delta') or {}).get`, `(effects or {}).get`, `c.get`, `float`, `jepit_drive`, `max`, `self.params.get`, `sum`
- L1556–1575 **`Naluri.set_lexicon`** · kontrol=8, assignment/delete=4, except=0 · Call: `(mapping or {}).items`, `LEXICON.items`, `dict`, `len`, `str`, `str(w).lower`
- L1577–1589 **`Naluri.set_tag_lexicon`** · kontrol=8, assignment/delete=4, except=0 · Call: `(mapping or {}).items`, `TAG_LEXICON.items`, `dict`, `len`, `str`
- L1591–1600 **`Naluri.use_lexicon_pack`** · kontrol=3, assignment/delete=4, except=0 · Call: `', '.join`, `ValueError`, `dict`, `kata.items`, `len`, `sorted`, `tag.items`
- L1602–1649 **`Naluri._compile_lexicon`** · kontrol=14, assignment/delete=19, except=0 · Call: `_norm_tok`, `dict`, `entri_parts.setdefault`, `entri_parts.setdefault(parts, []).append`, `enumerate`, `len`, `max`, `node.setdefault`, `self.lexicon.keys`, `self.tag_lexicon.items`, `sorted`, `str`, `str(t).lower`, `str(word).lower`, `str(word).lower().strip`, `t.split`, `tag_parts.setdefault`, `tag_parts.setdefault(parts, []).append`, `tuple`, `w.split`
- L1651–1676 **`Naluri._lexicon_occurrences`** · kontrol=7, assignment/delete=12, except=0 · Call: `len`, `node.get`, `occ.append`, `trie.get`
- L1680–1764 **`Naluri._span_cocok`** · kontrol=29, assignment/delete=24, except=0 · Call: `any`, `cakupan_negasi`, `deltas_flags.append`, `kata.append`, `kata_flag.append`, `kata_klausa.append`, `len`, `max`, `range`, `self._entri_parts.get`, `self._tag_parts.get`, `sum`, `terdeteksi.append`, `terdeteksi.sort`, `terpakai.append`, `tokenisasi`, `tuple`, `zip`
- L1766–1816 **`Naluri._base_impact`** · kontrol=17, assignment/delete=16, except=0 · Call: `dict`, `dv.items`, `entri.items`, `kv[0].replace`, `kv[0].replace('tag::', '').lower`, `nama.startswith`, `nama[5:].lower`, `per_entri.items`, `per_entri.setdefault`, `self._lexicon_rank.get`, `self._span_cocok`, `self._tags_by_lower.get`, `self.lexicon.get`, `sorted`
- L1818–1864 **`Naluri.impact_of`** · kontrol=15, assignment/delete=10, except=0 · Call: `_batas_memori`, `dict`, `jepit_drive`, `len`, `self._base_impact`, `self._compile_lexicon`, `self._impact_cache.clear`, `self._impact_cache.get`, `self._working_memory_impact`, `self.nurani.anticipate`, `self.nurani.anticipate_words`, `str`
- L1866–1889 **`Naluri.project_outcome_to_drives`** · kontrol=6, assignment/delete=10, except=0 · Call: `_get_attr`, `abs`, `deltas.keys`, `deltas.values`, `float`, `list`, `min`, `self.impact_of`, `sum`
- L1891–1923 **`Naluri.utility`** · kontrol=5, assignment/delete=12, except=0 · Call: `_get_attr`, `float`, `math.tanh`, `max`, `self._drive_weight_for_utility`, `self.estimate_scale`, `self.impact_of`, `str`, `sum`
- L1925–1929 **`Naluri._drive_weight_for_utility`** · kontrol=0, assignment/delete=2, except=0 · Call: `self.deficit`, `self.urgency.get`
- L1931–1935 **`Naluri.scoring_func`** · kontrol=0, assignment/delete=0, except=0 · Call: `self.utility`
- L1933–1934 **`Naluri.scoring_func._score`** · kontrol=0, assignment/delete=0, except=0 · Call: `self.utility`
- L1938–1940 **`Naluri.estimate_scale`** · kontrol=0, assignment/delete=0, except=0 · Call: `max`, `min`
- L1942–1972 **`Naluri._update_scale`** · kontrol=9, assignment/delete=10, except=0 · Call: `abs`, `len`, `max`, `min`, `nur.enabled`, `nur.scale_from_holdout`, `sum`
- L1975–2162 **`Naluri.observe_outcome`** · kontrol=29, assignment/delete=56, except=1 · Call: `_diag.catat`, `_get_attr`, `_pangkas_memori`, `abs`, `bool`, `dd.get`, `dd.items`, `float`, `int`, `isinstance`, `jepit_01`, `jepit_drive`, `lex.get`, `math.tanh`, `max`, `min`, `nur.belajar_persepsi`, `nur.enabled`, `nur.experience`, `nur.record_observation`, `nur.record_uncertainty`, `nur.structural_surprise`, `nur.update_introspection`, `realita.get`, `self._emosi_naikkan`, `self._pred_pairs.append`, `self._prediction_log.append`, `self._update_scale`, `self.assign_delayed_credit`, `self.deficit`, `self.estimate_scale`, `self.impact_of`, `self.mood`, `self.params.get`, `str`, `sum`
- L2164–2165 **`Naluri.calibration_error`** · kontrol=0, assignment/delete=0, except=0 · Call: tidak ada
- L2168–2177 **`Naluri._fase_lokal`** · kontrol=0, assignment/delete=3, except=0 · Call: `int`, `max`, `min`, `self.params.get`
- L2179–2182 **`Naluri._sleep_cycle`** · kontrol=0, assignment/delete=1, except=0 · Call: `int`, `max`, `self.params.get`
- L2185–2188 **`Naluri.sleep_mode`** · kontrol=0, assignment/delete=1, except=0 · Call: `SLEEP_MODE_ALIASES.get`, `self.params.get`, `str`, `str(self.params.get('sleep_mode', 'kognitif')).lower`
- L2190–2205 **`Naluri.set_sleep_mode`** · kontrol=1, assignment/delete=2, except=0 · Call: `', '.join`, `SLEEP_MODE_ALIASES.get`, `ValueError`, `str`, `str(mode).lower`
- L2207–2214 **`Naluri._scheduled_sleep`** · kontrol=2, assignment/delete=2, except=0 · Call: `self._fase_lokal`, `self._sleep_cycle`, `self.params.get`, `str`, `str(self.params.get('sleep_scheduled_phase', 'malam')).lower`
- L2216–2236 **`Naluri.sleep_status`** · kontrol=2, assignment/delete=4, except=0 · Call: `int`, `max`, `round`, `self._fase_lokal`, `self._sleep_cycle`, `self.params.get`, `self.should_sleep`, `str`, `str(self.params.get('sleep_scheduled_phase', 'malam')).lower`
- L2238–2292 **`Naluri.should_sleep`** · kontrol=17, assignment/delete=9, except=0 · Call: `nur.calibration_report`, `nur.enabled`, `nur.night_energy_shift`, `nur.recent_spike`, `self._scheduled_sleep`
- L2294–2297 **`Naluri.note_prediction`** · kontrol=0, assignment/delete=1, except=0 · Call: tidak ada
- L2299–2331 **`Naluri.dream_policy`** · kontrol=3, assignment/delete=10, except=0 · Call: `int`, `jepit`, `max`, `min`, `round`, `self._emosi_aktif`, `self.deficit`, `self.emosi_dominan`, `self.goal_to_scenario`, `self.mood`
- L2333–2378 **`Naluri.post_sleep`** · kontrol=8, assignment/delete=20, except=2 · Call: `_diag.catat`, `copy.deepcopy`, `float`, `getattr`, `max`, `min`, `report.get`, `self._kesadaran_aktif`, `self._sleep_cycle`, `self.jejak.consolidate_memory`, `self.kesadaran.dream`, `self.kesadaran.enabled`, `self.kesadaran.wake`
- L2381–2387 **`Naluri._effective_delta`** · kontrol=0, assignment/delete=2, except=0 · Call: `float`, `jepit_drive`, `self.levels.get`
- L2389–2439 **`Naluri.record_action`** · kontrol=20, assignment/delete=17, except=0 · Call: `(drive_effects or {}).get`, `abs`, `dict`, `drive_effects.get`, `float`, `int`, `jepit_01`, `len`, `max`, `min`, `next`, `result.append`, `self._eligibility_traces.append`, `self._eligibility_traces.sort`, `self.params.get`, `str`, `str(action or '').strip`, `trace.get`, `weights.items`, `x.get`
- L2441–2456 **`Naluri._decay_eligibility_traces`** · kontrol=4, assignment/delete=10, except=0 · Call: `float`, `int`, `jepit_01`, `kept.append`, `max`, `self.params.get`, `trace.get`
- L2458–2544 **`Naluri.assign_delayed_credit`** · kontrol=26, assignment/delete=43, except=0 · Call: `abs`, `assignments.append`, `by_action.items`, `by_action.setdefault`, `by_action.values`, `copy.deepcopy`, `counts.get`, `drive_targets.get`, `float`, `int`, `isinstance`, `item['drive_weights'].items`, `jepit_01`, `jepit_drive`, `len`, `max`, `outcome.get`, `raw_dd.get`, `round`, `self._action_values.setdefault`, `self.params.get`, `self.project_outcome_to_drives`, `slot.get`, `slot.setdefault`, `str`, `sum`, `total_per_drive.get`, `trace.get`, `values.get`, `weights.values`, `x.get`
- L2546–2720 **`Naluri.choose_action`** · kontrol=44, assignment/delete=53, except=1 · Call: `"kandidat aksi wajib berupa mapping dengan 'name' string non-kosong; dapat {!r}".format`, `(self._action_values.get(action_name) or {}).get`, `ValueError`, `_diag.catat`, `best.get`, `c.get`, `dict`, `effects.get`, `float`, `isinstance`, `konflik.get`, `len`, `max`, `nama_c.strip`, `nur.compromise_bonus`, `nur.detect_conflict`, `nur.enabled`, `nur.note_conflict`, `own_goal.get`, `prior.items`, `round`, `scored.append`, `scored.sort`, `self._action_values.get`, `self._active_subgoal`, `self._effective_delta`, `self._emosi_aktif`, `self._emosi_weight_bias`, `self._kesadaran_aktif`, `self._persepsi_aktif`, `self._salience_kandidat`, `self._working_memory_action_bias`, `self.context_aktif[0].get`, `self.deficit`, `self.kesadaran.free_will_action_bonus`, `self.nurani.enabled`, `self.nurani.social_prior`, `self.params.get`, `self.record_action`, `self.urgency.get`, `str`, `trace_effects.get`, `ulang.append`, `ulang.sort`
- L2722–2744 **`Naluri.reward_for`** · kontrol=2, assignment/delete=8, except=0 · Call: `'reward_for[{}]'.format`, `_periksa_kunci_drive`, `deltas.items`, `float_hingga`, `nur.flow_reward_bonus`, `self._effective_delta`, `self.mood`, `self.urgency.get`
- L2747–2748 **`Naluri._emosi_aktif`** · kontrol=0, assignment/delete=0, except=0 · Call: `bool`, `self.params.get`
- L2750–2760 **`Naluri.enable_emosi`** · kontrol=2, assignment/delete=5, except=0 · Call: `bool`
- L2762–2765 **`Naluri._valensi_mentah`** · kontrol=1, assignment/delete=1, except=0 · Call: `max`, `self.weights.values`, `sum`
- L2767–2781 **`Naluri._emosi_naikkan`** · kontrol=5, assignment/delete=4, except=0 · Call: `EMOSI_ALIASES.get`, `_pangkas_memori`, `float`, `jepit_01`, `round`, `self._emosi_log.append`, `self.emosi.get`, `str`, `str(emosi).lower`
- L2783–2791 **`Naluri._emosi_peluruh`** · kontrol=1, assignment/delete=5, except=0 · Call: `float`, `int`, `jepit`, `max`, `self.params.get`
- L2793–2829 **`Naluri._emosi_apresiasi`** · kontrol=6, assignment/delete=10, except=0 · Call: `float`, `max`, `self._emosi_naikkan`, `self._valensi_mentah`, `self.deficit`
- L2831–2841 **`Naluri.feel`** · kontrol=2, assignment/delete=0, except=0 · Call: `float`, `self._emosi_aktif`, `self._emosi_naikkan`
- L2843–2845 **`Naluri.emosi_state`** · kontrol=1, assignment/delete=0, except=0 · Call: `round`
- L2847–2854 **`Naluri.emosi_dominan`** · kontrol=1, assignment/delete=2, except=0 · Call: `float`, `max`, `self._emosi_aktif`
- L2856–2861 **`Naluri.enable_coping`** · kontrol=1, assignment/delete=2, except=0 · Call: `bool`
- L2863–2874 **`Naluri._coping_gate`** · kontrol=3, assignment/delete=3, except=0 · Call: `bool`, `float`, `jepit_01`, `self._emosi_aktif`, `self.levels.get`, `self.params.get`
- L2876–2886 **`Naluri._coping_reduce_emotion`** · kontrol=1, assignment/delete=3, except=0 · Call: `_pangkas_memori`, `float`, `max`, `round`, `self._emosi_log.append`, `self.emosi.get`, `str`
- L2888–2911 **`Naluri.reappraise`** · kontrol=6, assignment/delete=7, except=0 · Call: `EMOSI_ALIASES.get`, `float`, `jepit_01`, `max`, `round`, `self._coping_gate`, `self._coping_reduce_emotion`, `self.delta`, `self.params.get`, `str`, `str(emotion or '').lower`
- L2913–2934 **`Naluri.suppress`** · kontrol=5, assignment/delete=6, except=0 · Call: `EMOSI_ALIASES.get`, `float`, `jepit_01`, `max`, `round`, `self._coping_gate`, `self._coping_reduce_emotion`, `self.delta`, `self.emosi.get`, `self.params.get`, `str`, `str(emotion or '').lower`
- L2936–2958 **`Naluri.distract`** · kontrol=3, assignment/delete=6, except=0 · Call: `float`, `int`, `jepit_01`, `jepit_drive`, `max`, `min`, `round`, `self._coping_gate`, `self.params.get`, `str`, `str(topic or '').strip`
- L2960–2965 **`Naluri._advance_coping_focus`** · kontrol=2, assignment/delete=2, except=0 · Call: `int`, `max`, `self._coping_focus.get`
- L2967–2969 **`Naluri.coping_state`** · kontrol=0, assignment/delete=0, except=0 · Call: `bool`, `copy.deepcopy`, `self.params.get`
- L2971–3007 **`Naluri._emosi_weight_bias`** · kontrol=7, assignment/delete=16, except=0 · Call: `float`, `getattr`, `max`, `mentah.items`, `min`, `residu.ambang_dimodifikasi`, `residu.langit_dimodifikasi`, `self.params.get`
- L3009–3020 **`Naluri.mode_npc`** · kontrol=2, assignment/delete=0, except=0 · Call: `self._emosi_aktif`, `self.enable_emosi`, `self.nurani.enabled`, `self.nurani.set_pillars`, `self.set_sleep_mode`
- L3023–3026 **`Naluri._relasi_netral`** · kontrol=0, assignment/delete=0, except=0 · Call: `str`
- L3028–3038 **`Naluri.kenal`** · kontrol=2, assignment/delete=2, except=0 · Call: `self._relasi_netral`, `self.nurani.meet`
- L3040–3052 **`Naluri.observe_other_belief`** · kontrol=1, assignment/delete=0, except=0 · Call: `float`, `jepit_drive`, `self.nurani.observe_other_belief`, `str`
- L3054–3059 **`Naluri.estimate_other_belief`** · kontrol=1, assignment/delete=0, except=0 · Call: `self.nurani.estimate_other_belief`, `str`
- L3061–3065 **`Naluri.relasi`** · kontrol=1, assignment/delete=0, except=0 · Call: `self._relasi_netral`, `self.nurani.relationship`
- L3067–3086 **`Naluri.label_relasi`** · kontrol=7, assignment/delete=4, except=0 · Call: `float`, `isinstance`, `r.get`, `self.relasi`
- L3088–3094 **`Naluri.catat_utang`** · kontrol=1, assignment/delete=0, except=0 · Call: `self.nurani.tambah_utang`
- L3096–3100 **`Naluri.bayar_utang`** · kontrol=1, assignment/delete=0, except=0 · Call: `self.nurani.bayar_utang`
- L3102–3106 **`Naluri.utang`** · kontrol=1, assignment/delete=0, except=0 · Call: `self.nurani.utang_state`
- L3108–3110 **`Naluri.menarik_diri`** · kontrol=1, assignment/delete=0, except=0 · Call: `bool`, `self.nurani.menarik_diri`
- L3112–3122 **`Naluri.tandai_momen`** · kontrol=1, assignment/delete=0, except=0 · Call: `self.kesadaran.tandai_core_memory`
- L3124–3150 **`Naluri.viskositas_relasi`** · kontrol=6, assignment/delete=9, except=1 · Call: `_diag.catat`, `bool`, `callable`, `float`, `getattr`, `getter`, `r.get`, `round`, `self.relasi`
- L3152–3175 **`Naluri.hancurkan_kepercayaan`** · kontrol=5, assignment/delete=5, except=1 · Call: `_diag.catat`, `breaker`, `callable`, `getattr`, `hasil.get`, `self.berinteraksi`, `self.kesadaran.betray`, `self.label_relasi`, `self.viskositas_relasi`
- L3177–3229 **`Naluri.berinteraksi`** · kontrol=10, assignment/delete=8, except=0 · Call: `float`, `jepit_drive`, `min`, `r.get`, `round`, `self._emosi_aktif`, `self._emosi_naikkan`, `self._relasi_netral`, `self.delta`, `self.label_relasi`, `self.nurani.interact`, `self.params.get`
- L3232–3294 **`Naluri.apply_to_brain`** · kontrol=16, assignment/delete=16, except=4 · Call: `DRIVE_ATTENTION.get`, `DRIVE_NEUROMOD.get`, `_diag.catat`, `callable`, `float`, `focus`, `getattr`, `jepit_drive`, `list`, `lr_setter`, `max`, `nm.items`, `release`, `self.deficit`, `self.mood`, `self.mood().modulation`, `setter`
- L3296–3320 **`Naluri.memory_policy`** · kontrol=1, assignment/delete=6, except=0 · Call: `max`, `self.deficit`, `self.mood`
- L3322–3364 **`Naluri.apply_memory_policy`** · kontrol=15, assignment/delete=12, except=4 · Call: `_diag.catat`, `float`, `getattr`, `hasattr`, `isinstance`, `nodes.values`, `policy.items`, `self.memory_policy`, `self.salience`
- L3366–3378 **`Naluri.set_personality`** · kontrol=2, assignment/delete=1, except=0 · Call: `drive_weights.items`, `float`
- L3380–3445 **`Naluri.set_personality_preset`** · kontrol=11, assignment/delete=17, except=0 · Call: `', '.join`, `(preset.get('weights') or {}).items`, `PERSONALITY_ALIASES.get`, `ValueError`, `base.get`, `copy.deepcopy`, `dict`, `float`, `isinstance`, `jepit_01`, `preset.get`, `self.params.pop`, `self.params.update`, `self.seed_backstory`, `sorted`, `str`, `str(name).lower`, `str(preset.get('name', 'kustom')).lower`, `watak.keys`
- L3447–3460 **`Naluri.set_watak`** · kontrol=2, assignment/delete=1, except=0 · Call: `copy.deepcopy`, `isinstance`, `kv.items`, `self._watak_keys.append`
- L3462–3469 **`Naluri.watak_aktif`** · kontrol=2, assignment/delete=3, except=0 · Call: `copy.deepcopy`, `isinstance`
- L3471–3548 **`Naluri.seed_backstory`** · kontrol=28, assignment/delete=27, except=0 · Call: `EMOSI_ALIASES.get`, `emo.items`, `float`, `int`, `isinstance`, `jepit_01`, `jepit_drive`, `lahir.get`, `lvl.items`, `m.get`, `nur.seed_affective`, `nur.seed_relationship`, `nur.seed_setpoints`, `r.get`, `self.params.get`, `str`, `str(e).lower`
- L3551–3558 **`Naluri.personality_presets`** · kontrol=4, assignment/delete=0, except=0 · Call: `PERSONALITIES.items`, `copy.deepcopy`, `dict`, `v.get`
- L3560–3572 **`Naluri.describe_personality`** · kontrol=2, assignment/delete=1, except=0 · Call: `PERSONALITIES.get`, `preset.get`, `round`, `self.watak_aktif`
- L3575–3649 **`Naluri.neuromodulation_bias`** · kontrol=5, assignment/delete=25, except=1 · Call: `_diag.catat`, `callable`, `float`, `getattr`, `int`, `jepit`, `max`, `min`, `mood.modulation`, `nm.get`, `nm_getter`, `round`, `self.deficit`, `self.levels.get`, `self.mood`, `self.urgency.get`
- L3652–3746 **`Naluri.counterfactual_rehearsal`** · kontrol=30, assignment/delete=17, except=5 · Call: `DRIVE_ATTENTION.get`, `_diag.catat`, `_get_attr`, `abs`, `brain.inject_input`, `brain.set_neuromodulator`, `brain.set_reward`, `brain.step`, `candidates.append`, `candidates.sort`, `float`, `focus_regions.append`, `getattr`, `hasattr`, `int`, `isinstance`, `jepit_drive`, `len`, `list`, `max`, `min`, `range`, `region.homeostatic_update`, `rehearse_log.append`, `str`, `str(_get_attr(o, 'description', '') or '').lower`
- L3749–3788 **`Naluri.drive_targeted_scenario`** · kontrol=5, assignment/delete=6, except=0 · Call: `DRIVES.index`, `critical.drive.upper`, `int`, `len`, `max`, `min`, `round`
- L3791–3841 **`Naluri.resonant_recalibration`** · kontrol=13, assignment/delete=18, except=1 · Call: `_diag.catat`, `_get_attr`, `callable`, `float`, `int`, `jepit_drive`, `max`, `self._update_scale`, `self.scoring_func`, `ws`
- L3843–3883 **`Naluri.salience`** · kontrol=10, assignment/delete=18, except=3 · Call: `_diag.catat`, `_get_attr`, `callable`, `drive_ctx.get`, `float`, `float_hingga`, `getattr`, `idle_fn`, `isinstance`, `jepit_drive`, `max`, `metadata.get`, `min`, `self.deficit`, `time.time`
- L3887–3889 **`Naluri.setpoints`** · kontrol=0, assignment/delete=0, except=0 · Call: `dict`
- L3891–3895 **`Naluri.experience`** · kontrol=1, assignment/delete=0, except=0 · Call: `self.nurani.experience`
- L3897–3901 **`Naluri.warmup_from_log`** · kontrol=1, assignment/delete=0, except=0 · Call: `self.nurani.warmup_from_log`
- L3903–3922 **`Naluri.anticipate`** · kontrol=5, assignment/delete=6, except=0 · Call: `dict`, `len`, `min`, `self._anticipate_cache.get`, `self._anticipate_cache.pop`, `self.nurani.anticipate`, `str`
- L3924–3932 **`Naluri.forget_affective`** · kontrol=1, assignment/delete=0, except=0 · Call: `self.nurani.forget_affective`
- L3934–3938 **`Naluri.calibration_report`** · kontrol=1, assignment/delete=0, except=0 · Call: `self.nurani.calibration_report`
- L3940–3944 **`Naluri.setpoint`** · kontrol=1, assignment/delete=0, except=0 · Call: `float`, `self.nurani.setpoints.get`
- L3946–3950 **`Naluri.interoception_matrix`** · kontrol=2, assignment/delete=0, except=0 · Call: `list`
- L3952–3960 **`Naluri.circadian_phase`** · kontrol=1, assignment/delete=0, except=0 · Call: `self._fase_lokal`, `self.nurani.circadian_phase`
- L3962–3967 **`Naluri.resolve_conflict`** · kontrol=1, assignment/delete=0, except=0 · Call: `self.nurani.detect_conflict`
- L3969–3974 **`Naluri.flow_state`** · kontrol=1, assignment/delete=1, except=0 · Call: `self.mood`, `self.nurani.flow_state`
- L3982–3989 **`Naluri.introspeksi`** · kontrol=1, assignment/delete=0, except=0 · Call: `self.nurani.introspeksi_state`
- L3991–3995 **`Naluri.evaluasi_diri`** · kontrol=1, assignment/delete=0, except=0 · Call: `self.nurani.evaluasi_diri`
- L3997–4001 **`Naluri.meta_kognisi`** · kontrol=1, assignment/delete=0, except=0 · Call: `self.nurani.meta_kognisi_laporan`
- L4003–4014 **`Naluri.refleksi_diri`** · kontrol=4, assignment/delete=0, except=0 · Call: `self.mood`, `self.nurani.enabled`, `self.nurani.refleksi_diri`
- L4016–4020 **`Naluri.sadar_diri`** · kontrol=1, assignment/delete=0, except=0 · Call: `self.nurani.sadar_diri`
- L4022–4028 **`Naluri.nilai_kepercayaan`** · kontrol=3, assignment/delete=0, except=0 · Call: `float`, `self.nurani.enabled`, `self.nurani.kepercayaan_diri.get`
- L4030–4047 **`Naluri.meta_status`** · kontrol=1, assignment/delete=5, except=0 · Call: `copy.deepcopy`, `float`, `int`, `len`, `max`, `min`, `self.coping_state`, `self.nurani.meta_status`, `self.params.get`
- L4049–4080 **`Naluri.enable_kesadaran`** · kontrol=6, assignment/delete=6, except=0 · Call: `'fitur kesadaran tidak dikenal: {!r}'.format`, `ValueError`, `alias_fitur.get`, `bool`, `self.params.get`, `str`, `str(f).strip`, `str(f).strip().lower`, `tuple`
- L4082–4097 **`Naluri.enable_presentasi`** · kontrol=3, assignment/delete=5, except=0 · Call: `bool`, `self.params.get`, `str`, `tuple`
- L4099–4106 **`Naluri.enable_replay`** · kontrol=1, assignment/delete=3, except=0 · Call: `bool`, `len`, `self.to_dict`
- L4108–4112 **`Naluri.export_replay`** · kontrol=1, assignment/delete=0, except=0 · Call: `copy.deepcopy`, `dict`
- L4115–4128 **`Naluri.replay`** · kontrol=8, assignment/delete=3, except=0 · Call: `(data or {}).get`, `ValueError`, `bool`, `cls.from_dict`, `entri.get`, `enumerate`, `int`, `list`, `obj.tick`
- L4130–4136 **`Naluri.enable_profiling`** · kontrol=1, assignment/delete=3, except=0 · Call: `bool`
- L4138–4146 **`Naluri._profile_add`** · kontrol=2, assignment/delete=6, except=0 · Call: `float`, `self._profile.get`
- L4148–4163 **`Naluri.profile_report`** · kontrol=3, assignment/delete=2, except=0 · Call: `getattr`, `max`, `round`, `self._profile.items`, `self._profile.values`, `self.jejak.performance_report`, `sorted`, `sum`
- L4165–4170 **`Naluri.enable_ritual`** · kontrol=0, assignment/delete=1, except=0 · Call: `bool`, `getattr`, `self.params.get`
- L4172–4181 **`Naluri.lakukan_ritual`** · kontrol=2, assignment/delete=0, except=1 · Call: `_diag.catat`, `self._ritual_aktif`, `self.ritual.perform`
- L4183–4197 **`Naluri.attach_jejak`** · kontrol=2, assignment/delete=1, except=1 · Call: `_diag.catat`, `getattr`, `self._presentasi_aktif`, `self.presentasi.set_jejak`
- L4199–4214 **`Naluri.observe_player`** · kontrol=2, assignment/delete=1, except=1 · Call: `_diag.catat`, `getattr`, `jejak.observe_actor`
- L4216–4225 **`Naluri.pattern_report`** · kontrol=2, assignment/delete=1, except=1 · Call: `_diag.catat`, `getattr`, `jejak.pattern_report`
- L4227–4237 **`Naluri.enable_nurani`** · kontrol=1, assignment/delete=0, except=0 · Call: `self.nurani.set_pillars`, `tuple`
- L4240–4254 **`Naluri.set_hud_labels`** · kontrol=6, assignment/delete=0, except=0 · Call: `emosi.items`, `intents.items`, `moods.items`, `self.hud_emosi.update`, `self.hud_intents.update`, `self.hud_moods.update`, `str`
- L4256–4263 **`Naluri.mood_label`** · kontrol=1, assignment/delete=3, except=0 · Call: `self.hud_moods.get`, `self.mood`
- L4265–4301 **`Naluri.intent`** · kontrol=7, assignment/delete=8, except=0 · Call: `drive_goal.get`, `float`, `g.active_subgoal`, `own.get`, `round`, `self._kesadaran_aktif`, `self.hud_intents.get`, `self.kesadaran.free_will_current_goal`, `self.should_sleep`, `str`
- L4303–4374 **`Naluri.hud_state`** · kontrol=9, assignment/delete=16, except=0 · Call: `ist.get`, `jepit_drive`, `niat.get`, `round`, `self._fase_lokal`, `self._introspeksi_aktif`, `self._kesadaran_aktif`, `self._persepsi_aktif`, `self._presentasi_aktif`, `self._ritual_aktif`, `self.brief`, `self.emosi_dominan`, `self.hud_emosi.get`, `self.intent`, `self.introspeksi`, `self.kesadaran.hud_state`, `self.label_relasi`, `self.mood`, `self.mood_label`, `self.persepsi_state`, `self.presentasi.hud_state`, `self.presentasi.indikator_psikologis`, `self.presentasi.tag_dialog`, `self.relasi`, `self.ritual.state`, `self.sadar_diri`
- L4376–4423 **`Naluri.brief`** · kontrol=16, assignment/delete=19, except=1 · Call: `(self.presentasi.ekspresi() or {}).get`, `_diag.catat`, `c.get`, `ctx.get`, `float`, `int`, `ks.get`, `max`, `self._coping_focus.get`, `self._introspeksi_aktif`, `self._kesadaran_aktif`, `self._persepsi_aktif`, `self._presentasi_aktif`, `self.emosi_dominan`, `self.hud_emosi.get`, `self.intent`, `self.kesadaran.hud_state`, `self.mood_label`, `self.presentasi.ekspresi`, `self.sadar_diri`
- L4426–4550 **`Naluri.health_check`** · kontrol=17, assignment/delete=34, except=0 · Call: `_diag.laporan`, `all`, `anomalies.append`, `bool`, `dict`, `float`, `int`, `levels.get`, `math.isinf`, `max`, `nur.enabled`, `nur.sensitivitas.items`, `round`, `self._persepsi_aktif`, `sensitivities.items`, `sensitivities.values`, `str`
- L4553–4605 **`Naluri.status`** · kontrol=2, assignment/delete=2, except=0 · Call: `copy.deepcopy`, `dict`, `g.to_dict`, `len`, `mood.modulation`, `self._kesadaran_aktif`, `self._presentasi_aktif`, `self._ritual_aktif`, `self.coping_state`, `self.emosi_state`, `self.estimate_scale`, `self.health_check`, `self.introspeksi`, `self.kesadaran.report`, `self.lod_status`, `self.meta_status`, `self.mood`, `self.nurani.enabled`, `self.persepsi_state`, `self.presentasi.snapshot`, `self.ritual.state`, `self.should_sleep`
- L4608–4702 **`Naluri.to_dict`** · kontrol=13, assignment/delete=1, except=0 · Call: `copy.deepcopy`, `dict`, `float`, `g.to_dict`, `getattr`, `int`, `list`, `self._rng.getstate`, `self.kesadaran.to_dict`, `self.lexicon.items`, `self.nurani.to_dict`, `self.presentasi.to_dict`, `self.ritual.to_dict`, `self.tag_lexicon.items`
- L4705–4708 **`Naluri.migrate`** · kontrol=0, assignment/delete=0, except=0 · Call: `validasi_state`
- L4711–4904 **`Naluri.from_dict`** · kontrol=96, assignment/delete=85, except=4 · Call: `(data.get('emosi') or {}).items`, `(el.get('action_values') or {}).items`, `(item.get('delta') or {}).get`, `(ps.get('stim') or {}).items`, `(value.get('drive_n') or {}).get`, `(value.get('drive_values') or {}).get`, `(wm.get('repeat') or {}).items`, `EMOSI_ALIASES.get`, `Goal.from_dict`, `LOD_ALIASES.get`, `Nurani.from_dict`, `_diag.catat`, `bool`, `cls`, `coping.get`, `data.get`, `data['hud_labels_emosi'].items`, `data['lexicon'].items`, `data['tag_lexicon'].items`, `dict`, `el.get`, `ep.get`, `float`, `getattr`, `hud.get`, `hud['intents'].items`, `hud['moods'].items`, `int`, `isinstance`, `item.get`, `jepit_01`, `jepit_drive`, `kal.get`, `kep.get`, `len`, `lod.get`, `max`, `obj._context_key`, `obj._coping_focus.get`, `obj._eligibility_traces.append`, `obj._rng.setstate`, `obj.batasi_memori`, `obj.context_aktif.append`, `obj.kesadaran.from_dict`, `obj.kompres_memori`, `obj.params.get`, `obj.presentasi.from_dict`, `obj.ritual.from_dict`, `ps.get`, `ss.get`, `str`, `str(e).lower`, `str(lod.get('mode', 'penuh')).lower`, `trace.get`, `tuple`, `v.get`, `validasi_state`, `value.get`, `wm.get`
- L4906–4909 **`Naluri.to_json`** · kontrol=0, assignment/delete=0, except=0 · Call: `json.dumps`, `json_kwargs.setdefault`, `self.to_dict`
- L4912–4913 **`Naluri.from_json`** · kontrol=0, assignment/delete=0, except=0 · Call: `cls.from_dict`, `json.loads`
- L4915–4918 **`Naluri.save`** · kontrol=0, assignment/delete=0, except=0 · Call: `self.to_dict`, `simpan_json`
- L4921–4924 **`Naluri.load`** · kontrol=0, assignment/delete=0, except=0 · Call: `cls.from_dict`, `muat_json`
- L4928–4931 **`Naluri.demo`** · kontrol=0, assignment/delete=0, except=0 · Call: `_simulasi_harian`

## `pycos/inti/naluri.py`

SHA-256: `29e26f6296a1a51240ebef46920c831345dd9e213fe28f6447d37e3ce335ff6d`

979 baris; 0 kelas; 21 fungsi/metode termasuk nested.

Kelas: tidak ada.
Handler luas: tidak ada.

Impor (termasuk lazy/TYPE_CHECKING): `from __future__ import annotations`; `from pycos.bahasa.tutur import TuturEngine, GenContext, konteks_dari_presentasi, SASPAnalyzer`; `from pycos.dukungan import batas_memori as _modul_batas`; `from pycos.dukungan import diagnostik as _diag`; `from pycos.dukungan import numerik as _numerik`; `from pycos.dukungan import patching as _patching`; `from pycos.dukungan import sumber as _sumber`; `from pycos.inti import _konfigurasi`; `from pycos.inti import kawanan as _kawanan`; `from pycos.inti import keadaan as _keadaan`; `from pycos.inti import kesadaran as _kesadaran`; `from pycos.inti import persona as _persona`; `from pycos.inti import presentasi as _presentasi`; `from pycos.inti import reputasi as _reputasi`; `from pycos.inti import ritual as _ritual`; `from pycos.inti.demo import jalankan`; `from pycos.inti.demo.skenario import demo_empati as jalankan`; `from pycos.inti.demo.skenario import demo_fitur_lanjutan as jalankan`; `from pycos.inti.demo.skenario import demo_gejala as jalankan`; `from pycos.inti.demo.skenario import demo_introspeksi as jalankan`; `from pycos.inti.demo.skenario import demo_invensi as jalankan`; `from pycos.inti.demo.skenario import demo_kausal as jalankan`; `from pycos.inti.demo.skenario import demo_kesadaran as jalankan`; `from pycos.inti.demo.skenario import demo_kinerja as jalankan`; `from pycos.inti.demo.skenario import demo_kognisi as jalankan`; `from pycos.inti.demo.skenario import demo_momen as jalankan`; `from pycos.inti.demo.skenario import demo_npc as jalankan`; `from pycos.inti.demo.skenario import demo_organik as jalankan`; `from pycos.inti.demo.skenario import demo_pelindung as jalankan`; `from pycos.inti.demo.skenario import demo_perencana as jalankan`; `from pycos.inti.demo.skenario import demo_persepsi as jalankan`; `from pycos.inti.demo.skenario import demo_presentasi as jalankan`; `from pycos.inti.demo.skenario import demo_sosial as jalankan`; `from pycos.inti.demo.skenario import demo_tutur as jalankan`; `from pycos.inti.demo.skenario import demo_watak as jalankan`; `from pycos.inti.ekstensi import gejala as _ekstensi_gejala`; `from pycos.inti.ekstensi import invensi as _ekstensi_invensi`; `from pycos.inti.ekstensi import kausal as _ekstensi_kausal`; `from pycos.inti.ekstensi import ketidaktahuan as _ekstensi_kt`; `from pycos.inti.ekstensi import kognisi as _ekstensi_kognisi`; `from pycos.inti.ekstensi import organik as _ekstensi_organik`; `from pycos.inti.ekstensi import pasang as _pasang_ekstensi`; `from pycos.inti.ekstensi import pelindung as _ekstensi_pelindung`; `from pycos.inti.ekstensi import perencana as _ekstensi_perencana`; `from pycos.inti.ekstensi import persistensi as _ekstensi_persistensi`; `from pycos.inti.mesin import Naluri as Naluri`; `from pycos.inti.presentasi import PRESENTASI_DEFAULTS`; `from pycos.memori.jejak_prediksi import JejakPrediksi`; `from pycos.refleksi.nurani import CalibrationReport, NURANI_DEFAULTS, Nurani`; `from typing import Any, Dict, Optional`; `import copy as _copy`; `import dataclasses as _dataclasses`; `import itertools as _itertools`; `import json as _json`; `import math as _math`; `import os`; `import os as _os`; `import random as _random`; `import re as _re`; `import sys as _sys`; `import time as _time`; `import typing as _typing`.

- L465–493 **`buat_npc`** · kontrol=3, assignment/delete=3, except=0 · Call: `Naluri`, `dict`, `kwargs.pop`, `n.mode_npc`, `params.update`
- L519–525 **`_get_attr`** · kontrol=2, assignment/delete=0, except=0 · Call: `getattr`, `isinstance`, `obj.get`
- L531–535 **`demo_npc`** · kontrol=0, assignment/delete=0, except=0 · Call: `jalankan`
- L541–546 **`demo_empati`** · kontrol=0, assignment/delete=0, except=0 · Call: `jalankan`
- L552–566 **`demo_watak`** · kontrol=0, assignment/delete=0, except=0 · Call: `jalankan`
- L569–582 **`demo_introspeksi`** · kontrol=0, assignment/delete=0, except=0 · Call: `jalankan`
- L585–596 **`demo_kesadaran`** · kontrol=0, assignment/delete=0, except=0 · Call: `jalankan`
- L599–608 **`demo_presentasi`** · kontrol=0, assignment/delete=0, except=0 · Call: `jalankan`
- L611–615 **`demo_fitur_lanjutan`** · kontrol=0, assignment/delete=0, except=0 · Call: `jalankan`
- L618–622 **`demo_kinerja`** · kontrol=0, assignment/delete=0, except=0 · Call: `jalankan`
- L625–629 **`demo_sosial`** · kontrol=0, assignment/delete=0, except=0 · Call: `jalankan`
- L632–635 **`demo_momen`** · kontrol=0, assignment/delete=0, except=0 · Call: `jalankan`
- L638–641 **`demo_tutur`** · kontrol=0, assignment/delete=0, except=0 · Call: `jalankan`
- L644–647 **`demo_kognisi`** · kontrol=0, assignment/delete=0, except=0 · Call: `jalankan`
- L650–661 **`demo_persepsi`** · kontrol=0, assignment/delete=0, except=0 · Call: `jalankan`
- L702–712 **`demo_organik`** · kontrol=0, assignment/delete=0, except=0 · Call: `jalankan`
- L818–821 **`demo_gejala`** · kontrol=0, assignment/delete=0, except=0 · Call: `jalankan`
- L841–844 **`demo_invensi`** · kontrol=0, assignment/delete=0, except=0 · Call: `jalankan`
- L865–868 **`demo_kausal`** · kontrol=0, assignment/delete=0, except=0 · Call: `jalankan`
- L883–886 **`demo_perencana`** · kontrol=0, assignment/delete=0, except=0 · Call: `jalankan`
- L950–953 **`demo_pelindung`** · kontrol=0, assignment/delete=0, except=0 · Call: `jalankan`

## `pycos/inti/persona.py`

SHA-256: `5fe3c65daf52a7b8e4120f078c3ff0f1582dbd2e590338006d103a98e26572ae`

208 baris; 2 kelas; 10 fungsi/metode termasuk nested.

Kelas: `Keadaan` L46, `Persona` L109.
Handler luas: tidak ada.

Impor (termasuk lazy/TYPE_CHECKING): `from __future__ import annotations`; `from dataclasses import dataclass, field`; `from pycos.dukungan.numerik import float_hingga, jepit`; `from pycos.kontrak import angka, hanya_kunci, teks_wajib`; `from typing import Any, Dict, Mapping, Optional, Tuple`.

- L34–39 **`_jepit`** · kontrol=2, assignment/delete=1, except=0 · Call: `'nilai keadaan harus angka, dapat {!r}'.format`, `ValueError`, `float_hingga`, `isinstance`, `jepit`
- L64–68 **`Keadaan.__post_init__`** · kontrol=0, assignment/delete=0, except=0 · Call: `angka`, `object.__setattr__`
- L71–81 **`Keadaan.dari_mood`** · kontrol=0, assignment/delete=3, except=0 · Call: `_jepit`, `cls`, `float`, `getattr`
- L83–85 **`Keadaan.to_dict`** · kontrol=0, assignment/delete=0, except=0 · Call: tidak ada
- L88–90 **`Keadaan.from_dict`** · kontrol=0, assignment/delete=0, except=0 · Call: `cls`, `dict`, `hanya_kunci`
- L103–105 **`normalisasi_frasa`** · kontrol=0, assignment/delete=0, except=0 · Call: `' '.join`, `frasa.lower`, `frasa.lower().split`
- L142–173 **`Persona.__post_init__`** · kontrol=10, assignment/delete=3, except=0 · Call: `', '.join`, `'keterusterangan {!r} tidak dikenal; pilihan: {}'.format`, `'panjang_kalimat {!r} tidak dikenal; pilihan: {}'.format`, `'register {!r} tidak dikenal; pilihan: {}'.format`, `'sifat {!r} tidak dikenal; sifat sah: {}'.format`, `'sifat[{}]'.format`, `'{} harus daftar string, bukan satu string'.format`, `ValueError`, `angka`, `dict`, `dict(self.sifat).items`, `dict.fromkeys`, `isinstance`, `normalisasi_frasa`, `object.__setattr__`, `str`, `str(x).strip`, `teks_wajib`, `tuple`
- L175–177 **`Persona.sifat_of`** · kontrol=0, assignment/delete=0, except=0 · Call: `self.sifat.get`
- L179–186 **`Persona.to_dict`** · kontrol=0, assignment/delete=0, except=0 · Call: `dict`, `list`
- L189–200 **`Persona.from_dict`** · kontrol=1, assignment/delete=0, except=0 · Call: `ValueError`, `cls`, `data.get`, `dict`, `hanya_kunci`

## `pycos/inti/presentasi.py`

SHA-256: `ec70a62af26dac62c2f66748b59885fbb8a0d3187eeb8b30f600d9f3621b658b`

2790 baris; 1 kelas; 92 fungsi/metode termasuk nested.

Kelas: `Presentasi` L125.
Handler luas: 246, 253, 260, 268, 402, 423, 443, 617, 663, 669, 754, 815, 968, 990, 1009, 1084, 1222, 1538, 1757, 1825, 2179, 2290, 2300, 2683, 283, 294, 307, 353, 380, 534, 542, 584, 681, 695, 702, 712, 719, 776, 786, 890, 983, 1112, 1153, 1160, 1170, 1180, 1195, 1205, 1234, 1243, 1255, 1264, 1275, 1284, 1293, 1302, 1316, 1328, 1340, 1402, 1459, 1474, 1492, 1625, 1867, 1969, 2078, 2084, 2150, 2188, 2247, 2273, 2308, 2353, 2371, 2446, 2452, 2459, 2496, 397, 551, 1879, 1891, 1959, 2222, 2314, 2427, 2506, 2018, 2168, 2435.

Impor (termasuk lazy/TYPE_CHECKING): `from __future__ import annotations`; `from pycos.bahasa.teks import ekstrak_topik`; `from pycos.bahasa.teks import jejak_bentuk as _jejak_bentuk`; `from pycos.bahasa.teks import jenis_kalimat`; `from pycos.bahasa.teks import jenis_pertanyaan`; `from pycos.bahasa.teks import pecah_kalimat as _pecah`; `from pycos.bahasa.teks import periksa_gramatika as _pgm, G1_KERAS`; `from pycos.bahasa.teks import tindak_tutur_skor`; `from pycos.dukungan import diagnostik as _diag`; `from pycos.dukungan.numerik import jepit, jepit_01`; `from pycos.dukungan.sumber import kandidat_leksikon`; `from pycos.dukungan.validasi_state import validasi_state`; `from pycos.inti._konfigurasi import _kclip`; `from pycos.inti.naluri import SASPAnalyzer`; `from pycos.inti.naluri import TuturEngine`; `from pycos.inti.naluri import konteks_dari_presentasi`; `from pycos.inti.persona import Keadaan`; `from pycos.refleksi.nurani import nilai_selaras`; `from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple`; `import copy`; `import os`; `import random`; `import re`.

- L116–122 **`_skema_act`** · kontrol=2, assignment/delete=2, except=0 · Call: `_ACT_FUNGSI.get`, `str`, `str(act or '').strip`, `str(act or '').strip().lower`
- L141–203 **`Presentasi.__init__`** · kontrol=0, assignment/delete=48, except=0 · Call: `copy.deepcopy`, `random.Random`, `self._seed_for`
- L206–212 **`Presentasi._seed_for`** · kontrol=2, assignment/delete=3, except=0 · Call: `enumerate`, `getattr`, `ord`, `str`
- L217–222 **`Presentasi.enabled`** · kontrol=2, assignment/delete=0, except=0 · Call: `bool`, `self.params.get`
- L224–231 **`Presentasi._p`** · kontrol=2, assignment/delete=2, except=1 · Call: `PRESENTASI_DEFAULTS.get`, `float`, `isinstance`, `self.params.get`, `v.get`
- L233–234 **`Presentasi._tick`** · kontrol=0, assignment/delete=0, except=0 · Call: `getattr`, `int`
- L236–239 **`Presentasi._eid`** · kontrol=1, assignment/delete=0, except=0 · Call: `getattr`, `str`
- L241–248 **`Presentasi._pick`** · kontrol=2, assignment/delete=0, except=1 · Call: `_diag.catat`, `list`, `self._rng.choice`
- L250–255 **`Presentasi._lev`** · kontrol=2, assignment/delete=0, except=1 · Call: `(getattr(self.naluri, 'levels', {}) or {}).get`, `_diag.catat`, `float`, `getattr`
- L257–262 **`Presentasi._emosi`** · kontrol=2, assignment/delete=0, except=1 · Call: `(getattr(self.naluri, 'emosi', {}) or {}).get`, `_diag.catat`, `float`, `getattr`
- L264–270 **`Presentasi._epistemik`** · kontrol=2, assignment/delete=1, except=1 · Call: `(getattr(ks, 'epistemic_emotions', {}) or {}).get`, `_diag.catat`, `float`, `getattr`, `self._kes`
- L272–273 **`Presentasi._kes`** · kontrol=0, assignment/delete=0, except=0 · Call: `getattr`
- L275–276 **`Presentasi._nur`** · kontrol=0, assignment/delete=0, except=0 · Call: `getattr`
- L278–286 **`Presentasi._rel`** · kontrol=3, assignment/delete=1, except=1 · Call: `_diag.catat`, `callable`, `dict`, `fn`, `getattr`
- L288–310 **`Presentasi._label_rel`** · kontrol=10, assignment/delete=6, except=2 · Call: `_diag.catat`, `callable`, `float`, `fn`, `getattr`, `ks.withholding_relationship_tension`, `self._kes`, `str`
- L312–315 **`Presentasi.set_jejak`** · kontrol=0, assignment/delete=1, except=0 · Call: tidak ada
- L320–325 **`Presentasi.set_leksikon`** · kontrol=0, assignment/delete=3, except=0 · Call: `self.tutur_engine`, `str`
- L327–364 **`Presentasi.tutur_engine`** · kontrol=12, assignment/delete=6, except=2 · Call: `TuturEngine`, `_diag.catat`, `bool`, `eng.tersedia`, `kandidat_leksikon`, `len`, `os.path.abspath`, `os.path.dirname`, `os.path.exists`, `self.params.get`, `str`, `type`
- L366–404 **`Presentasi.analisis_sa_sp`** · kontrol=13, assignment/delete=9, except=3 · Call: `SASPAnalyzer`, `_diag.catat`, `bool`, `copy.deepcopy`, `engine.analisis_sa_sp`, `getattr`, `getattr(ks, 'enabled', lambda *_: False)`, `hasattr`, `hasil.get`, `ks.analisis_sa_sp`, `ks.observe_sa_sp`, `self._kes`, `self._sa_sp_analyzer.analisis`, `self.params.get`, `self.tutur_engine`, `type`
- L408–429 **`Presentasi._generatif`** · kontrol=5, assignment/delete=4, except=1 · Call: `_diag.catat`, `eng.ucap`, `konteks_dari_presentasi`, `self.tutur_engine`, `t.teks.strip`
- L434–469 **`Presentasi.tick`** · kontrol=6, assignment/delete=19, except=1 · Call: `_diag.catat`, `float`, `getattr`, `int`, `max`, `min`, `self._emosi`, `self._felt`, `self._lerp`, `self.enabled`, `self.naluri.mood`
- L474–492 **`Presentasi.lihat_player`** · kontrol=4, assignment/delete=6, except=0 · Call: `bool`, `int`, `self._p`, `self._tick`, `self.enabled`
- L494–515 **`Presentasi.proaktif`** · kontrol=5, assignment/delete=6, except=0 · Call: `bool`, `self._p`, `self._tick`, `self.enabled`, `self.params.get`, `self.ucap`
- L520–572 **`Presentasi.terima_bukti`** · kontrol=8, assignment/delete=7, except=3 · Call: `_diag.catat`, `float`, `ks._refresh_identity`, `ks.hold_belief`, `ks.metacognitive_doubt`, `min`, `round`, `self._doubt`, `self._kes`, `self._log`, `self._pick`, `self._tick`, `self.deskripsi`, `self.enabled`, `self.nonverbal`, `str`
- L574–599 **`Presentasi.koreksi_ingatan`** · kontrol=4, assignment/delete=5, except=1 · Call: `_diag.catat`, `ks.misremember`, `self._kes`, `self._log`, `self._pick`, `self._tick`, `self.deskripsi`, `self.enabled`, `self.nonverbal`, `str`
- L604–649 **`Presentasi.indikator_psikologis`** · kontrol=4, assignment/delete=9, except=1 · Call: `_diag.catat`, `float`, `jepit_01`, `label`, `max`, `round`, `self._doubt`, `self._effort`, `self._emosi`, `self._felt`, `self._lev`, `self._moral`, `self.enabled`, `self.naluri.mood`
- L630–644 **`Presentasi.indikator_psikologis.label`** · kontrol=2, assignment/delete=1, except=0 · Call: tidak ada
- L651–684 **`Presentasi.tag_dialog`** · kontrol=10, assignment/delete=10, except=3 · Call: `_diag.catat`, `getattr`, `hasattr`, `label.capitalize`, `self.enabled`, `self.naluri.emosi_dominan`, `self.naluri.hud_emosi.get`, `self.naluri.mood_label`, `self.naluri.ritual.state`, `st.get`, `str`
- L687–688 **`Presentasi._lerp`** · kontrol=0, assignment/delete=0, except=0 · Call: `jepit_01`
- L690–705 **`Presentasi._felt`** · kontrol=4, assignment/delete=2, except=2 · Call: `_diag.catat`, `float`, `getattr`, `getattr(ks, 'felt', {}).get`, `getattr(nur, 'felt_state', {}).get`, `self._kes`, `self._nur`
- L707–722 **`Presentasi._moral`** · kontrol=4, assignment/delete=2, except=2 · Call: `_diag.catat`, `float`, `getattr`, `getattr(ks, 'moral', {}).get`, `getattr(nur, 'moral_emotions', {}).get`, `self._kes`, `self._nur`
- L727–763 **`Presentasi.ekspresi`** · kontrol=6, assignment/delete=12, except=1 · Call: `_diag.catat`, `bool`, `campuran.get`, `e`, `max`, `round`, `self._emosi`, `self._linger`, `self._p`, `self._rng.random`, `self._tell_aktif`, `self.enabled`, `self.naluri.params.get`, `{'takut': 'mata melebar, rahang menegang', 'marah': 'alis berkerut, bibir menipis', 'senang': 'mata sedikit menyipit, sudut bibir naik', 'sedih': 'pandangan sayu, sudut bibir turun', 'penasaran': 'kepala sedikit miring, mata menyapu', 'netral': 'wajah tenang'}.get`
- L765–804 **`Presentasi.tatapan`** · kontrol=18, assignment/delete=16, except=2 · Call: `_diag.catat`, `float`, `getattr`, `getattr(ks, '_joint_attention', {}).get`, `ja.get`, `rel.get`, `self._eid`, `self._emosi`, `self._kes`, `self._label_rel`, `self._linger`, `self._moral`, `self._p`, `self._rel`, `self.enabled`, `spot[0].get`, `str`
- L806–836 **`Presentasi.postur`** · kontrol=6, assignment/delete=14, except=1 · Call: `_diag.catat`, `float`, `round`, `self._effort`, `self._lev`, `self._linger`, `self._p`, `self.enabled`, `self.naluri.mood`
- L838–853 **`Presentasi.napas`** · kontrol=4, assignment/delete=7, except=0 · Call: `round`, `self._emosi`, `self._felt`, `self.enabled`
- L855–881 **`Presentasi.gestur`** · kontrol=8, assignment/delete=13, except=0 · Call: `round`, `self._agency`, `self._effort`, `self._emosi`, `self._quirk_gesture`, `self.enabled`
- L883–893 **`Presentasi._quirk_gesture`** · kontrol=5, assignment/delete=2, except=1 · Call: `_diag.catat`, `getattr`, `list`, `self._kes`, `self._rng.random`, `str`
- L895–915 **`Presentasi.jarak`** · kontrol=5, assignment/delete=11, except=0 · Call: `jepit`, `max`, `round`, `self._label_rel`, `self._lev`, `self._p`, `self.enabled`
- L920–938 **`Presentasi._linger`** · kontrol=2, assignment/delete=6, except=0 · Call: `abs`, `float`, `jepit_01`, `self._histeresis.get`
- L960–993 **`Presentasi._derive_tell`** · kontrol=12, assignment/delete=11, except=4 · Call: `(getattr(self.naluri, 'params', {}) or {}).get`, `_diag.catat`, `float`, `getattr`, `isinstance`, `list`, `min`, `raw.items`, `self._TELL_PETA.get`, `self._rng.choice`, `wts.get`
- L995–1019 **`Presentasi._tell_aktif`** · kontrol=7, assignment/delete=5, except=1 · Call: `_diag.catat`, `bool`, `float`, `max`, `self._derive_tell`, `self._doubt`, `self._emosi`, `self._lev`, `self._moral`, `self._p`, `self.enabled`, `self.naluri.deficit`, `self.params.get`
- L1021–1025 **`Presentasi.tell_katalog`** · kontrol=1, assignment/delete=1, except=0 · Call: `dict`, `self._derive_tell`
- L1030–1068 **`Presentasi._cek_pending_shift`** · kontrol=16, assignment/delete=14, except=0 · Call: `bool`, `getattr`, `int`, `max`, `peristiwa.append`, `self._kes`, `self._nur`, `self._p`, `self._tick`, `self.params.get`, `sorted`, `spot[0].get`, `str`
- L1070–1073 **`Presentasi.hesitation_state`** · kontrol=0, assignment/delete=0, except=0 · Call: `dict`
- L1075–1129 **`Presentasi.prosodi`** · kontrol=8, assignment/delete=23, except=2 · Call: `_diag.catat`, `float`, `int`, `jepit`, `jepit_01`, `ks._self_audition_reaction_now`, `ks.enabled`, `max`, `min`, `reaksi.get`, `round`, `self._doubt`, `self._effort`, `self._emosi`, `self._felt`, `self._kes`, `self._moral`, `self.enabled`, `self.naluri.mood`
- L1131–1143 **`Presentasi.nonverbal`** · kontrol=1, assignment/delete=0, except=0 · Call: `self.ekspresi`, `self.enabled`, `self.gestur`, `self.jarak`, `self.napas`, `self.postur`, `self.tatapan`
- L1148–1163 **`Presentasi._doubt`** · kontrol=4, assignment/delete=2, except=2 · Call: `_diag.catat`, `float`, `getattr`, `self._kes`, `self._nur`
- L1165–1173 **`Presentasi._agency`** · kontrol=2, assignment/delete=1, except=1 · Call: `_diag.catat`, `float`, `getattr`, `self._kes`
- L1175–1183 **`Presentasi._effort`** · kontrol=2, assignment/delete=1, except=1 · Call: `_diag.catat`, `float`, `getattr`, `self._kes`
- L1185–1198 **`Presentasi._grief`** · kontrol=5, assignment/delete=4, except=1 · Call: `_diag.catat`, `float`, `g[ent].get`, `g[k].get`, `getattr`, `max`, `self._kes`
- L1200–1208 **`Presentasi._mortality`** · kontrol=2, assignment/delete=1, except=1 · Call: `_diag.catat`, `float`, `getattr`, `self._kes`
- L1210–1225 **`Presentasi._dissonance`** · kontrol=5, assignment/delete=4, except=1 · Call: `_diag.catat`, `d[k].get`, `dict`, `float`, `getattr`, `max`, `self._kes`, `slot.get`
- L1227–1246 **`Presentasi._inner_speech`** · kontrol=8, assignment/delete=4, except=2 · Call: `_diag.catat`, `getattr`, `nd[-1].get`, `self._kes`, `self._nur`, `str`, `t[-1].get`
- L1248–1267 **`Presentasi._kenangan`** · kontrol=7, assignment/delete=3, except=2 · Call: `_diag.catat`, `getattr`, `self._kes`, `self.jejak.autobiographical_timeline`
- L1269–1287 **`Presentasi._babak`** · kontrol=6, assignment/delete=3, except=2 · Call: `_diag.catat`, `ch[-1].get`, `ks.life_chapters`, `self._kes`, `self.jejak.life_chapters`, `str`
- L1289–1305 **`Presentasi._counterfactual`** · kontrol=5, assignment/delete=1, except=2 · Call: `_diag.catat`, `dict`, `float`, `getattr`, `getattr(ks, 'counterfactual_emotions', {}).items`, `round`, `self._kes`, `self.jejak.counterfactual_emotions`
- L1307–1319 **`Presentasi._dream`** · kontrol=4, assignment/delete=3, except=1 · Call: `_diag.catat`, `callable`, `fn`, `getattr`, `self._kes`, `str`
- L1321–1331 **`Presentasi._refusal`** · kontrol=5, assignment/delete=2, except=1 · Call: `_diag.catat`, `dict`, `getattr`, `int`, `r[-1].get`, `self._kes`, `self._tick`
- L1333–1343 **`Presentasi._shared`** · kontrol=4, assignment/delete=2, except=1 · Call: `_diag.catat`, `getattr`, `self._kes`, `str`
- L1345–1351 **`Presentasi._top_felt`** · kontrol=4, assignment/delete=3, except=0 · Call: `self._felt`
- L1353–1360 **`Presentasi._top_moral`** · kontrol=4, assignment/delete=3, except=0 · Call: `self._moral`
- L1365–1440 **`Presentasi._pilih_act`** · kontrol=35, assignment/delete=11, except=1 · Call: `_diag.catat`, `ks._self_audition_reaction_now`, `ks.enabled`, `reaction.get`, `ref.get`, `self._cek_pending_shift`, `self._dissonance`, `self._doubt`, `self._dream`, `self._emosi`, `self._epistemik`, `self._grief`, `self._inner_speech`, `self._kes`, `self._label_rel`, `self._lev`, `self._mortality`, `self._refusal`, `self._rng.random`, `self._tick`, `str`, `str(ref.get('permintaan', '')).lower`, `str(topik).lower`
- L1442–1545 **`Presentasi._jawaban_keadaan`** · kontrol=27, assignment/delete=22, except=4 · Call: `(jenis_pertanyaan(teks) or {}).get`, `_diag.catat`, `dict`, `dict(self.naluri.emosi_state() or {}).items`, `emosi_teratas`, `es.items`, `float`, `getattr`, `jenis_pertanyaan`, `keadaan_singkat`, `max`, `re.search`, `self._addr`, `self._inner_speech`, `self.naluri.emosi_state`, `self.naluri.mood`, `str`, `str(getattr(self.naluri, 'name', '') or '').strip`, `str(self._ucapan_terakhir or '').lower`, `{'siapa': 'siapa itu', 'apa': 'apa yang kau maksud', 'dimana': 'di mana', 'kapan': 'kapan', 'kenapa': 'kenapa', 'bagaimana': 'bagaimana', 'berapa': 'berapa', 'pilihan': 'yang mana'}.get`
- L1455–1468 **`Presentasi._jawaban_keadaan.keadaan_singkat`** · kontrol=3, assignment/delete=3, except=1 · Call: `_diag.catat`, `float`, `getattr`, `self.naluri.mood`
- L1470–1482 **`Presentasi._jawaban_keadaan.emosi_teratas`** · kontrol=4, assignment/delete=2, except=1 · Call: `_diag.catat`, `dict`, `dict(self.naluri.emosi_state() or {}).items`, `es.items`, `float`, `max`, `self.naluri.emosi_state`
- L1547–1579 **`Presentasi._pronomina`** · kontrol=7, assignment/delete=11, except=0 · Call: `getattr`, `map`, `self._eid`, `self._label_rel`, `self._pronomina_per_mitra.get`, `str`, `str(getattr(persona, 'register', '') or '').lower`, `sum`
- L1581–1604 **`Presentasi._konsisten_pronomina`** · kontrol=2, assignment/delete=6, except=0 · Call: `m.group`, `m.group(2).upper`, `re.sub`, `self._pronomina`
- L1606–1615 **`Presentasi._addr`** · kontrol=3, assignment/delete=2, except=0 · Call: `self._eid`, `self._label_rel`
- L1617–1628 **`Presentasi._kita`** · kontrol=4, assignment/delete=2, except=1 · Call: `_diag.catat`, `getattr`, `getattr(ks, '_joint_attention', {}).get`, `self._eid`, `self._kes`, `self._label_rel`
- L1630–1766 **`Presentasi._isi_ucap`** · kontrol=30, assignment/delete=19, except=1 · Call: `_diag.catat`, `babak.capitalize`, `dis.get`, `hasattr`, `n.intent`, `n.intent().get`, `n.self_intent`, `ref.get`, `self._addr`, `self._babak`, `self._dissonance`, `self._dream`, `self._grief`, `self._inner_speech`, `self._jawaban_keadaan`, `self._kita`, `self._pick`, `self._refusal`, `str`, `str(topik or '').strip`
- L1768–1784 **`Presentasi._bingkai_relasi`** · kontrol=8, assignment/delete=8, except=0 · Call: `ken.get`, `self._kenangan`, `self._label_rel`, `self._rng.random`, `self._shared`, `str`, `teks.rstrip`
- L1786–1843 **`Presentasi._warnai`** · kontrol=17, assignment/delete=18, except=1 · Call: `_diag.catat`, `float`, `m.group`, `out.startswith`, `out.strip`, `out[0].islower`, `out[0].upper`, `out[1:].lstrip`, `re.match`, `re.sub`, `self._agency`, `self._doubt`, `self._emosi`, `self._pick`, `self._rng.random`, `self._top_felt`, `self._top_moral`, `self.naluri.mood`, `{'bersalah': 'maaf… ', 'malu': 'aku… ', 'bangga': 'hei, ', 'cemburu': 'siapa dia? ', 'iri': 'kamu beruntung. ', 'syukur': 'terima kasih. ', 'haru': '… ', 'kesepian': 'kamu masih di sini? '}.get`, `{'sesak': '(napas tertahan) ', 'jantung': '(menekan dada) ', 'nyeri': '(mengerang pelan) ', 'lelah': '(suara melemah) ', 'lapar': '(menelan ludah) ', 'mual': '(menahan mual) ', 'tegang': '(rahang mengeras) '}.get`
- L1845–2113 **`Presentasi.ucap`** · kontrol=84, assignment/delete=91, except=8 · Call: `' '.join`, `(role_style or {}).get`, `Keadaan.dari_mood`, `_diag.catat`, `_jejak_bentuk`, `_masalah_selaras`, `_pecah`, `_pgm`, `_skema_act`, `bool`, `cacat_gaya.append`, `calon.lower`, `calon.lower().endswith`, `calon.lower().startswith`, `calon.rstrip`, `deception.get`, `dict`, `direct.get`, `entry.pop`, `getattr`, `int`, `isinstance`, `jejak_akhir[0].get`, `ks.attention_effort`, `ks.dialogue_turn`, `ks.next_manipulation_action`, `ks.roleplay_speech_for`, `ks.strategic_speech_for`, `len`, `list`, `max`, `nilai_selaras`, `prefix.lower`, `range`, `re.escape`, `re.search`, `re.sub`, `replacements.items`, `role.get`, `role_style.get`, `round`, `self._act_counts.get`, `self._beat_diam`, `self._bingkai_relasi`, `self._doubt`, `self._eid`, `self._generatif`, `self._isi_ucap`, `self._kes`, `self._konsisten_pronomina`, `self._log`, `self._p`, `self._pilih_act`, `self._recent_texts.append`, `self._rng.random`, `self._tick`, `self._warnai`, `self.deskripsi`, `self.enabled`, `self.naluri.mood`, `self.nonverbal`, `self.params.get`, `self.prosodi`, `self.tutur_engine`, `step.get`, `str`, `str(calon or '').strip`, `str(direct.get('teks', '')).strip`, `str(source).strip`, `str(step.get('ujaran', '')).strip`, `str(style.get('akhiran', style.get('suffix', '')) or '').strip`, `str(style.get('awalan', style.get('prefix', '')) or '').strip`, `str(target_word).strip`, `str(teks or '').strip`, `style.get`, `suffix.lower`
- L1932–1963 **`Presentasi.ucap._masalah_selaras`** · kontrol=7, assignment/delete=3, except=1 · Call: `Keadaan.dari_mood`, `_diag.catat`, `getattr`, `nilai_selaras`, `self._doubt`, `self.naluri.mood`, `str`
- L2115–2123 **`Presentasi._beat_diam`** · kontrol=0, assignment/delete=2, except=0 · Call: `max`, `round`, `self._doubt`, `self._eid`, `self._log`, `self._tick`, `self.deskripsi`, `self.nonverbal`, `self.prosodi`
- L2125–2258 **`Presentasi._dengar_efek`** · kontrol=32, assignment/delete=32, except=8 · Call: `_diag.catat`, `abs`, `bool`, `emo_applied.get`, `float`, `getattr`, `getattr(n, '_emosi_aktif', lambda: False)`, `hasattr`, `imp.items`, `ks.epistemic_emotion`, `n._emosi_naikkan`, `n.delta`, `n.impact_of`, `pemetaan.items`, `round`, `self._kes`, `self._label_rel`, `self.params.get`, `str`, `tindak.get`, `tindak.items`, `tindak_tutur_skor`
- L2260–2331 **`Presentasi.dengar`** · kontrol=15, assignment/delete=19, except=5 · Call: `_diag.catat`, `_fn_eng`, `analisis.get`, `bool`, `callable`, `copy.deepcopy`, `ctx.setdefault`, `dict`, `ekstrak_topik`, `getattr`, `isinstance`, `jenis_kalimat`, `ks.attention_effort`, `ks.dialogue_turn`, `kwargs.get`, `max`, `self._dengar_efek`, `self._eid`, `self._kes`, `self._kita`, `self._label_rel`, `self._p`, `self._rng.random`, `self.analisis_sa_sp`, `self.backchannel`, `self.enabled`, `str`, `str(teks).strip`, `str(teks).strip().endswith`
- L2333–2339 **`Presentasi.balas`** · kontrol=0, assignment/delete=4, except=0 · Call: `self.ucap`
- L2341–2358 **`Presentasi.backchannel`** · kontrol=4, assignment/delete=3, except=1 · Call: `_diag.catat`, `ks.backchannel`, `self._kes`, `self._log`, `self._pick`, `self._tick`, `self.enabled`
- L2363–2386 **`Presentasi._update_boredom`** · kontrol=3, assignment/delete=11, except=1 · Call: `_diag.catat`, `_kclip`, `float`, `ks.epistemic_emotions.get`, `max`, `min`, `self._kes`, `self._lev`, `self._p`
- L2388–2394 **`Presentasi.boredom_state`** · kontrol=0, assignment/delete=0, except=0 · Call: `copy.deepcopy`, `float`, `len`, `list`, `round`, `self._p`
- L2396–2478 **`Presentasi._spontaneous_boredom_action`** · kontrol=18, assignment/delete=25, except=5 · Call: `_diag.catat`, `copy.deepcopy`, `free_goal.get`, `free_goal.get('goal', {}).get`, `int`, `isinstance`, `konteks.get`, `ks.aesthetic_response`, `ks.epistemic_emotion`, `ks.free_will_choose_goal`, `ks.playful_reframe`, `ks.submit`, `len`, `max`, `round`, `self._boredom_log.append`, `self._boredom_recent.append`, `self._kes`, `self._p`, `self._tick`, `set`, `str`
- L2480–2539 **`Presentasi.perilaku_idle`** · kontrol=16, assignment/delete=19, except=2 · Call: `(getattr(self._kes(), 'epistemic_emotions', {}) or {}).get`, `_diag.catat`, `float`, `getattr`, `ks.epistemic_emotion`, `max`, `r.get`, `ritual.enabled`, `ritual.maybe_trigger`, `round`, `self._emosi`, `self._felt`, `self._kes`, `self._lev`, `self._log`, `self._moral`, `self._p`, `self._pick`, `self._quirk_gesture`, `self._rng.random`, `self._spontaneous_boredom_action`, `self._tick`, `self._update_boredom`, `self.enabled`
- L2541–2571 **`Presentasi.reaksi`** · kontrol=13, assignment/delete=13, except=0 · Call: `(jenis + ' ' + konten).lower`, `any`, `event.get`, `isinstance`, `self._log`, `self._tick`, `self.enabled`, `self.nonverbal`, `str`
- L2573–2581 **`Presentasi.adegan`** · kontrol=4, assignment/delete=2, except=0 · Call: `self.enabled`, `self.perilaku_idle`, `self.ucap`, `u.get`
- L2586–2621 **`Presentasi.deskripsi`** · kontrol=17, assignment/delete=13, except=0 · Call: `'; '.join`, `(nv.get('ekspresi') or {}).get`, `(nv.get('gestur') or {}).get`, `(nv.get('jarak') or {}).get`, `(nv.get('napas') or {}).get`, `(nv.get('postur') or {}).get`, `(nv.get('tatapan') or {}).get`, `bagian.append`, `nv.get`, `self.nonverbal`
- L2626–2630 **`Presentasi._log`** · kontrol=2, assignment/delete=2, except=0 · Call: `dict`, `int`, `len`, `self._history.append`, `self._p`
- L2632–2651 **`Presentasi.snapshot`** · kontrol=0, assignment/delete=0, except=0 · Call: `copy.deepcopy`, `int`, `round`, `self.boredom_state`, `self.enabled`, `self.indikator_psikologis`, `self.nonverbal`, `self.prosodi`, `self.tag_dialog`
- L2653–2674 **`Presentasi.hud_state`** · kontrol=6, assignment/delete=0, except=0 · Call: `(self.ekspresi() or {}).get`, `(self.napas() or {}).get`, `(self.postur() or {}).get`, `(self.tatapan(kepada) or {}).get`, `copy.deepcopy`, `getattr`, `getattr(self.naluri, 'ritual', None).state`, `round`, `self._history[-1].get`, `self._reputasi_view`, `self.ekspresi`, `self.enabled`, `self.indikator_psikologis`, `self.naluri.ritual.enabled`, `self.napas`, `self.postur`, `self.tag_dialog`, `self.tatapan`
- L2676–2685 **`Presentasi._reputasi_view`** · kontrol=3, assignment/delete=1, except=1 · Call: `_diag.catat`, `getattr`, `kawanan.reputasi`
- L2687–2730 **`Presentasi.to_dict`** · kontrol=5, assignment/delete=1, except=0 · Call: `bool`, `copy.deepcopy`, `dict`, `float`, `int`, `list`, `self._act_counts.items`, `self._histeresis.items`, `self._rng.getstate`, `str`
- L2732–2787 **`Presentasi.from_dict`** · kontrol=17, assignment/delete=41, except=1 · Call: `(data.get('act_counts') or {}).items`, `(data.get('histeresis') or {}).items`, `_kclip`, `bool`, `copy.deepcopy`, `data.get`, `dict`, `float`, `int`, `isinstance`, `len`, `max`, `self._rng.setstate`, `str`, `tuple`, `validasi_state`

## `pycos/inti/reputasi.py`

SHA-256: `2a42ff16b13f0139657ded60044e154b1c31117b62294cdbcaaf18c309d18469`

262 baris; 1 kelas; 15 fungsi/metode termasuk nested.

Kelas: `Reputasi` L32.
Handler luas: tidak ada.

Impor (termasuk lazy/TYPE_CHECKING): `from __future__ import annotations`; `from pycos.dukungan.numerik import jepit_01, jepit_drive`; `from pycos.dukungan.validasi_state import validasi_state`; `from typing import Any, Dict, List, Mapping, Optional, Tuple`; `import copy`.

- L35–44 **`Reputasi.__init__`** · kontrol=0, assignment/delete=5, except=0 · Call: `copy.deepcopy`
- L46–47 **`Reputasi.enabled`** · kontrol=0, assignment/delete=0, except=0 · Call: `bool`, `self.params.get`
- L49–56 **`Reputasi._p`** · kontrol=2, assignment/delete=2, except=1 · Call: `REPUTASI_DEFAULTS.get`, `float`, `isinstance`, `self.params.get`, `v.get`
- L58–71 **`Reputasi._slot`** · kontrol=5, assignment/delete=7, except=0 · Call: `getattr`, `int`, `isinstance`, `len`, `max`, `min`, `self._p`, `self._unit.get`, `self._unit.pop`, `self._unit[k].values`, `str`, `v.get`
- L73–90 **`Reputasi.catat`** · kontrol=2, assignment/delete=6, except=0 · Call: `float`, `getattr`, `int`, `jepit_01`, `jepit_drive`, `round`, `sel.get`, `self._p`, `self._slot`, `self.enabled`, `str`
- L92–132 **`Reputasi.sebar`** · kontrol=6, assignment/delete=11, except=0 · Call: `bool`, `float`, `getattr`, `int`, `jepit_01`, `jepit_drive`, `len`, `max`, `min`, `round`, `self._catat_social_proof`, `self._p`, `self._rumor_log.append`, `self._slot`, `self.catat`, `self.enabled`, `slot['rumor'].append`, `str`
- L134–164 **`Reputasi._catat_social_proof`** · kontrol=3, assignment/delete=14, except=0 · Call: `float`, `getattr`, `int`, `len`, `max`, `round`, `self._p`, `self._social_proof.setdefault`, `self._social_proof.setdefault(eid, {}).setdefault`, `self.catat`, `set`, `slot.get`, `slot['sumber'].add`, `str`
- L166–172 **`Reputasi.konsensus`** · kontrol=1, assignment/delete=2, except=0 · Call: `getattr`, `int`, `self._social_proof.get`, `set`, `slot.items`, `sorted`, `str`, `v.get`
- L174–189 **`Reputasi.reputasi`** · kontrol=5, assignment/delete=4, except=0 · Call: `dict`, `float`, `getattr`, `int`, `round`, `self._unit.get`, `self.enabled`, `self.label`, `slot.get`, `slot[s].get`, `str`, `sum`
- L191–207 **`Reputasi.label`** · kontrol=4, assignment/delete=6, except=0 · Call: `abs`, `float`, `getattr`, `max`, `min`, `self._unit.get`, `slot[s].get`, `str`, `v.values`
- L209–210 **`Reputasi.semua`** · kontrol=1, assignment/delete=0, except=0 · Call: `self.label`
- L212–219 **`Reputasi.decay`** · kontrol=2, assignment/delete=4, except=0 · Call: `float`, `int`, `max`, `sel.get`, `self._p`, `self._unit.values`
- L221–224 **`Reputasi.report`** · kontrol=0, assignment/delete=0, except=0 · Call: `self.enabled`, `self.semua`
- L226–237 **`Reputasi.to_dict`** · kontrol=3, assignment/delete=1, except=0 · Call: `copy.deepcopy`, `dict`, `int`, `self._social_proof.items`, `self.enabled`, `set`, `slot.items`, `sorted`, `v.get`
- L239–258 **`Reputasi.from_dict`** · kontrol=11, assignment/delete=8, except=0 · Call: `(data.get('social_proof') or {}).items`, `(slot or {}).items`, `bool`, `copy.deepcopy`, `data.get`, `dict`, `int`, `isinstance`, `self.params.update`, `set`, `v.get`, `validasi_state`

## `pycos/inti/ritual.py`

SHA-256: `9387c9824cf8ff9cf21fa9102c91d207518a5bd51a555bef27656f7094088952`

286 baris; 1 kelas; 16 fungsi/metode termasuk nested.

Kelas: `Ritual` L19.
Handler luas: 127, 149, 241.

Impor (termasuk lazy/TYPE_CHECKING): `from __future__ import annotations`; `from pycos.dukungan import diagnostik as _diag`; `from pycos.dukungan.validasi_state import validasi_state`; `from typing import Any, Dict, List, Mapping, Optional`; `import copy`; `import random`.

- L90–98 **`Ritual.__init__`** · kontrol=0, assignment/delete=7, except=0 · Call: `copy.deepcopy`, `random.Random`, `self._detect_archetype`, `self._seed_for`
- L101–106 **`Ritual._seed_for`** · kontrol=2, assignment/delete=3, except=0 · Call: `enumerate`, `getattr`, `ord`, `str`
- L109–110 **`Ritual.enabled`** · kontrol=0, assignment/delete=0, except=0 · Call: `bool`, `self.params.get`
- L112–119 **`Ritual._p`** · kontrol=2, assignment/delete=2, except=1 · Call: `RITUAL_DEFAULTS.get`, `float`, `isinstance`, `self.params.get`, `v.get`
- L121–122 **`Ritual._tick`** · kontrol=0, assignment/delete=0, except=0 · Call: `getattr`, `int`
- L124–129 **`Ritual._deficit`** · kontrol=1, assignment/delete=0, except=1 · Call: `_diag.catat`, `float`, `self.naluri.deficit`
- L131–152 **`Ritual._detect_archetype`** · kontrol=7, assignment/delete=4, except=1 · Call: `_diag.catat`, `any`, `getattr`, `max`, `str`, `str(getattr(self.naluri, 'personality_name', '') or '').lower`, `{'keingintahuan': 'cendekia', 'afiliasi': 'sosiawan', 'penguasaan': 'pengrajin', 'keamanan': 'penjaga'}.get`
- L154–166 **`Ritual._kondisi_ok`** · kontrol=4, assignment/delete=3, except=0 · Call: `self._deficit`
- L169–171 **`Ritual.tick`** · kontrol=0, assignment/delete=0, except=0 · Call: tidak ada
- L173–176 **`Ritual.refresh_archetype`** · kontrol=0, assignment/delete=1, except=0 · Call: `self._detect_archetype`
- L178–198 **`Ritual.maybe_trigger`** · kontrol=11, assignment/delete=3, except=0 · Call: `int`, `r.get`, `self._RITUALS.get`, `self._kondisi_ok`, `self._p`, `self._rng.choice`, `self._rng.random`, `self._tick`, `self.enabled`, `self.perform`, `self.refresh_archetype`
- L200–226 **`Ritual.perform`** · kontrol=6, assignment/delete=9, except=0 · Call: `int`, `isinstance`, `len`, `next`, `r.get`, `ritual.get`, `self._RITUALS.get`, `self._log.append`, `self._p`, `self._rng.choice`, `self._terapkan_efek`, `self._tick`, `self.enabled`, `self.refresh_archetype`, `str`
- L228–249 **`Ritual._terapkan_efek`** · kontrol=7, assignment/delete=4, except=1 · Call: `_diag.catat`, `float`, `getattr`, `max`
- L251–256 **`Ritual.state`** · kontrol=0, assignment/delete=0, except=0 · Call: `self.enabled`, `self.refresh_archetype`
- L258–265 **`Ritual.to_dict`** · kontrol=2, assignment/delete=1, except=0 · Call: `dict`, `int`, `self._rng.getstate`
- L267–282 **`Ritual.from_dict`** · kontrol=7, assignment/delete=6, except=1 · Call: `data.get`, `dict`, `int`, `isinstance`, `len`, `self._rng.setstate`, `str`, `tuple`, `validasi_state`

## `pycos/konektor.py`

SHA-256: `68d520b115924b78cdf2f5223cd7bb729d3d0ec6372f2b058303bd95d90e4684`

127 baris; 0 kelas; 5 fungsi/metode termasuk nested.

Kelas: tidak ada.
Handler luas: tidak ada.

Impor (termasuk lazy/TYPE_CHECKING): `from __future__ import annotations`; `from pycos.inti.naluri import Naluri`; `from pycos.kontrak import DRIVE_KEYS`; `from typing import Any, Dict, List, Mapping, Optional, Sequence, cast`; `import argparse`; `import json`; `import math`; `import sys`.

- L19–29 **`_salin`** · kontrol=10, assignment/delete=0, except=0 · Call: `ValueError`, `_salin`, `all`, `isinstance`, `math.isfinite`, `value.items`
- L32–36 **`_npc`** · kontrol=1, assignment/delete=0, except=0 · Call: `Naluri.from_dict`, `ValueError`, `_salin`, `isinstance`
- L39–62 **`observasi`** · kontrol=7, assignment/delete=5, except=0 · Call: `ValueError`, `_npc`, `_salin`, `all`, `clone.tick`, `data.get`, `events.append`, `isinstance`, `ringkas.strip`, `set`
- L65–87 **`aksi`** · kontrol=11, assignment/delete=4, except=0 · Call: `ValueError`, `_npc`, `_salin`, `all`, `candidate.get`, `cast`, `clone.choose_action`, `effects.values`, `isinstance`, `json.dumps`, `json.loads`, `list`, `set`
- L90–123 **`main`** · kontrol=9, assignment/delete=11, except=1 · Call: `Naluri`, `Naluri(name='HostNPC', rng_seed=seed).to_dict`, `ValueError`, `_npc`, `_npc(state).hud_state`, `_salin`, `aksi`, `argparse.ArgumentParser`, `isinstance`, `json.dumps`, `json.loads`, `len`, `observasi`, `open`, `parser.add_argument`, `parser.parse_args`, `print`, `request.get`, `set`, `source.read`, `str`, `sys.stdin.read`

## `pycos/kontrak.py`

SHA-256: `c5efd45a64ed618ca063f5a5c449498fa8d0f7672f078a5f5ad0c6c0dcefd94d`

1357 baris; 2 kelas; 49 fungsi/metode termasuk nested.

Kelas: `ContractViolationError` L358, `_OperationChecks` L1122.
Handler luas: 417, 425, 672, 765, 864, 893, 1322, 1340, 1355, 437, 547, 662, 1300, 1311.

Impor (termasuk lazy/TYPE_CHECKING): `from __future__ import annotations`; `from collections.abc import Iterable, Mapping, Sequence`; `from itertools import islice`; `from pycos.dukungan import konstanta as _konstanta_drive`; `from pycos.dukungan.numerik import float_hingga`; `from typing import Any, Callable, Dict, List, Optional, Tuple, TypedDict`; `import math`; `import numbers`.

- L365–367 **`ContractViolationError.__init__`** · kontrol=0, assignment/delete=1, except=0 · Call: `dict`, `self.violation.get`, `str`, `super`, `super().__init__`
- L373–389 **`angka`** · kontrol=6, assignment/delete=1, except=0 · Call: `'{} = {} di atas batas {}'.format`, `'{} = {} di bawah batas {}'.format`, `'{} harus angka, dapat {!r}'.format`, `ValueError`, `float_hingga`, `isinstance`
- L392–396 **`teks_wajib`** · kontrol=2, assignment/delete=0, except=0 · Call: `'{} harus string non-kosong, dapat {!r}'.format`, `ValueError`, `isinstance`, `x.strip`
- L399–406 **`hanya_kunci`** · kontrol=3, assignment/delete=1, except=0 · Call: `', '.join`, `'{} harus berupa dict, dapat {!r}'.format`, `'{} memuat kunci tak dikenal {}; kunci sah: {}'.format`, `ValueError`, `isinstance`, `sorted`, `str`, `type`
- L409–419 **`_field`** · kontrol=3, assignment/delete=1, except=1 · Call: `d.get`, `isinstance`, `obj.get`, `object.__getattribute__`
- L422–426 **`_get`** · kontrol=1, assignment/delete=0, except=1 · Call: `isinstance`, `obj.get`
- L429–439 **`_label`** · kontrol=4, assignment/delete=0, except=1 · Call: `isinstance`, `str`, `type`
- L442–451 **`_pelanggaran`** · kontrol=1, assignment/delete=2, except=0 · Call: `_label`
- L454–466 **`_gabungkan`** · kontrol=2, assignment/delete=2, except=0 · Call: `'{} ({} syarat)'.format`, `_pelanggaran`, `len`, `list`
- L469–480 **`_range`** · kontrol=7, assignment/delete=2, except=1 · Call: `float`, `isinstance`, `len`, `math.isfinite`
- L483–491 **`_range_mencakup`** · kontrol=7, assignment/delete=4, except=0 · Call: `_range`
- L494–502 **`_tipe_kompatibel`** · kontrol=4, assignment/delete=0, except=0 · Call: tidak ada
- L505–565 **`_cek_skema_field`** · kontrol=16, assignment/delete=8, except=1 · Call: `'deklarasi kebutuhan field {!r} tidak valid'.format`, `'field {} tidak menjamin semua kunci yang dibutuhkan'.format`, `'field {} tidak menjanjikan himpunan kunci tetap'.format`, `'field {}: {} menjanjikan {}={!r}, {} membutuhkan {!r}'.format`, `'rentang field {} yang dijanjikan tidak mencakup kebutuhan'.format`, `'{} membutuhkan field {} yang tidak dijanjikan'.format`, `_pelanggaran`, `_range_mencakup`, `_tipe_kompatibel`, `isinstance`, `janji.get`, `kebutuhan.get`, `keluar.append`, `tuple`
- L568–597 **`_cek_skema_operasi`** · kontrol=8, assignment/delete=2, except=0 · Call: `'deklarasi kebutuhan operasi {!r} tidak valid'.format`, `'operasi {} tidak dijanjikan callable oleh {}'.format`, `'operasi {} tidak menjanjikan seluruh fase yang dibutuhkan'.format`, `'{} membutuhkan operasi {} yang tidak dijanjikan'.format`, `_pelanggaran`, `isinstance`, `janji.get`, `kebutuhan.get`, `set`, `set(fase_wajib).issubset`, `tuple`
- L600–676 **`verifikasi_startup`** · kontrol=17, assignment/delete=12, except=2 · Call: `'deklarasi dependency {} -> {} tidak valid'.format`, `'dependencies {!r} bukan mapping'.format`, `'{} membutuhkan penyedia {} yang tidak ada di JANJI'.format`, `_cek_skema_field`, `_cek_skema_operasi`, `_gabungkan`, `_get`, `_pelanggaran`, `bool`, `dependencies.items`, `dependency.get`, `isinstance`, `kebutuhan_aktif.items`, `pelanggaran.append`, `pelanggaran.extend`, `required_fields.items`, `required_ops.items`, `str`, `tuple`, `type`
- L679–680 **`_arg`** · kontrol=0, assignment/delete=0, except=0 · Call: `_get`
- L683–724 **`_npc_levels`** · kontrol=13, assignment/delete=7, except=1 · Call: `'{} membutuhkan levels bertipe mapping'.format`, `_field`, `_get`, `_pelanggaran`, `di_luar.append`, `float`, `isinstance`, `issues.append`, `math.isfinite`, `tidak_numerik.append`, `tuple`
- L727–735 **`_arg_posisional`** · kontrol=3, assignment/delete=1, except=1 · Call: `_arg`, `isinstance`
- L738–767 **`_npc_dari_lingkungan`** · kontrol=12, assignment/delete=9, except=1 · Call: `_arg`, `_arg_posisional`, `_field`, `_get`, `_label`, `bodies.values`, `isinstance`, `iter`, `len`, `next`
- L770–775 **`_cek_tambah_npc_masuk`** · kontrol=1, assignment/delete=1, except=0 · Call: `_npc_dari_lingkungan`, `_npc_levels`, `_pelanggaran`
- L778–785 **`_cek_tambah_npc_keluar`** · kontrol=4, assignment/delete=2, except=0 · Call: `_field`, `_npc_dari_lingkungan`, `_pelanggaran`
- L788–793 **`_cek_langkah_masuk`** · kontrol=1, assignment/delete=1, except=0 · Call: `_npc_dari_lingkungan`, `_npc_levels`, `_pelanggaran`
- L796–806 **`_cek_langkah_keluar`** · kontrol=3, assignment/delete=2, except=0 · Call: `_pelanggaran`, `isinstance`, `tuple`
- L809–822 **`_cek_tick_masuk`** · kontrol=4, assignment/delete=3, except=0 · Call: `_arg`, `_npc_levels`, `_pelanggaran`, `isinstance`, `issues.append`, `type`
- L825–845 **`_cek_tick_keluar`** · kontrol=7, assignment/delete=3, except=0 · Call: `_arg`, `_field`, `_npc_levels`, `_pelanggaran`, `isinstance`, `issues.append`, `issues.extend`, `type`
- L848–854 **`_cek_choose_masuk`** · kontrol=2, assignment/delete=1, except=0 · Call: `_arg`, `_pelanggaran`, `isinstance`
- L857–881 **`_cek_choose_keluar`** · kontrol=8, assignment/delete=6, except=1 · Call: `_arg`, `_get`, `_pelanggaran`, `isinstance`, `islice`, `iter`, `len`
- L884–899 **`_cek_reward_masuk`** · kontrol=5, assignment/delete=4, except=1 · Call: `_arg`, `_pelanggaran`, `deltas.items`, `isinstance`, `islice`, `iter`, `len`, `tuple`
- L902–914 **`_cek_reward_keluar`** · kontrol=4, assignment/delete=0, except=1 · Call: `_pelanggaran`, `float`, `isinstance`, `math.isfinite`, `type`
- L917–922 **`_cek_record_masuk`** · kontrol=2, assignment/delete=1, except=0 · Call: `_arg`, `_pelanggaran`, `isinstance`, `stimulus.strip`
- L925–930 **`_cek_record_keluar`** · kontrol=2, assignment/delete=0, except=0 · Call: `_pelanggaran`, `isinstance`
- L933–938 **`_cek_predict_masuk`** · kontrol=2, assignment/delete=1, except=0 · Call: `_arg`, `_pelanggaran`, `isinstance`, `stimulus.strip`
- L941–990 **`_cek_forecast`** · kontrol=17, assignment/delete=10, except=2 · Call: `'forecast.{} berada di luar kontrak'.format`, `'{} harus mengembalikan mapping'.format`, `_get`, `_pelanggaran`, `bad.append`, `float`, `isinstance`, `issues.append`, `math.isfinite`, `tuple`
- L993–994 **`_cek_predict_keluar`** · kontrol=0, assignment/delete=0, except=0 · Call: `_cek_forecast`
- L997–1008 **`_cek_reinforce_masuk`** · kontrol=5, assignment/delete=3, except=0 · Call: `_arg`, `_get`, `_pelanggaran`, `isinstance`, `stimulus.strip`
- L1011–1021 **`_cek_reinforce_keluar`** · kontrol=4, assignment/delete=1, except=0 · Call: `_get`, `_pelanggaran`, `isinstance`
- L1024–1027 **`_cek_ucap_masuk`** · kontrol=1, assignment/delete=0, except=0 · Call: `_pelanggaran`
- L1030–1037 **`_cek_ucap_keluar`** · kontrol=3, assignment/delete=0, except=0 · Call: `_get`, `_pelanggaran`, `isinstance`
- L1040–1046 **`_angka_dalam`** · kontrol=2, assignment/delete=1, except=1 · Call: `float`, `isinstance`, `math.isfinite`
- L1049–1075 **`_cek_nilai_selaras_masuk`** · kontrol=8, assignment/delete=6, except=0 · Call: `'nilai_selaras membutuhkan keadaan.{} dalam [{}, {}]'.format`, `_angka_dalam`, `_arg`, `_field`, `_pelanggaran`, `isinstance`, `issues.append`, `nama.strip`, `teks.strip`
- L1078–1096 **`_cek_nilai_selaras_keluar`** · kontrol=5, assignment/delete=4, except=0 · Call: `_angka_dalam`, `_field`, `_pelanggaran`, `isinstance`, `issues.append`, `status.strip`
- L1099–1112 **`_cek_catat_masuk`** · kontrol=3, assignment/delete=3, except=0 · Call: `_arg`, `_field`, `_pelanggaran`, `isinstance`, `issues.append`
- L1115–1119 **`_cek_catat_keluar`** · kontrol=1, assignment/delete=0, except=0 · Call: `_pelanggaran`
- L1204–1206 **`_kanonik_operasi`** · kontrol=0, assignment/delete=1, except=0 · Call: `_OPERATION_ALIASES.get`, `isinstance`, `operasi.strip`, `operasi.strip().lower`
- L1209–1215 **`_fase`** · kontrol=2, assignment/delete=1, except=0 · Call: `fase.strip`, `fase.strip().lower`, `isinstance`
- L1218–1258 **`_lintas_lapis`** · kontrol=14, assignment/delete=13, except=0 · Call: `_field`, `_npc_dari_lingkungan`, `_pelanggaran`, `isinstance`, `islice`, `issues.append`, `iter`, `len`, `operasi.endswith`, `operasi.startswith`, `set`, `tuple`
- L1261–1325 **`kontrak_operasi`** · kontrol=17, assignment/delete=7, except=3 · Call: `'kontrak {} fase {} dilanggar'.format`, `_OPERATION_CHECKS.get`, `_fase`, `_gabungkan`, `_kanonik_operasi`, `_label`, `_lintas_lapis`, `_pelanggaran`, `check`, `contract.get`, `getattr`, `isinstance`, `pelanggaran.append`, `pelanggaran.extend`, `str`, `type`
- L1329–1342 **`check_operation`** · kontrol=1, assignment/delete=0, except=1 · Call: `_pelanggaran`, `kontrak_operasi`, `kwargs.get`
- L1345–1357 **`verify_startup`** · kontrol=1, assignment/delete=0, except=1 · Call: `_pelanggaran`, `kwargs.get`, `verifikasi_startup`

## `pycos/lingkungan/__init__.py`

SHA-256: `3c47590abb358f07cd8ecf42230b96dbfa367fe2937c2057a7f754ab5b5b72a3`

56 baris; 0 kelas; 2 fungsi/metode termasuk nested.

Kelas: tidak ada.
Handler luas: tidak ada.

Impor (termasuk lazy/TYPE_CHECKING): `from .dunia import ARAH, EFEK_JENIS, JENIS_DAPAT_DIAMBIL, LEGENDA_MEDAN, SIMBOL_OBJEK, Badan, Lingkungan, ObjekDunia, Peta, demo, peta_contoh`; `from __future__ import annotations`; `from importlib import import_module`; `from typing import TYPE_CHECKING, Any, Dict, List`.

- L44–52 **`__getattr__`** · kontrol=1, assignment/delete=3, except=0 · Call: `'paket {!r} tidak punya atribut {!r}'.format`, `'{}.{}'.format`, `AttributeError`, `_SUBMODUL.get`, `getattr`, `globals`, `import_module`
- L55–56 **`__dir__`** · kontrol=0, assignment/delete=0, except=0 · Call: `globals`, `set`, `sorted`

## `pycos/lingkungan/dunia.py`

SHA-256: `6006293c8564bcafe51a03c92c42dbc24929caa6c240364a554a5c590d66768f`

1533 baris; 4 kelas; 70 fungsi/metode termasuk nested.

Kelas: `Peta` L228, `ObjekDunia` L316, `Badan` L370, `Lingkungan` L436.
Handler luas: 826, 1096, 1101, 1232, 1248, 1274.

Impor (termasuk lazy/TYPE_CHECKING): `from __future__ import annotations`; `from pycos.inti import Naluri`; `from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple`; `import copy`; `import inspect`; `import math`; `import os as _os`; `import random`; `import sys as _sys`.

- L180–182 **`_jarak`** · kontrol=0, assignment/delete=0, except=0 · Call: `abs`, `float`, `int`, `max`
- L185–199 **`_arah_relatif`** · kontrol=4, assignment/delete=3, except=0 · Call: `abs`, `int`
- L202–209 **`_menerima_action_cost`** · kontrol=3, assignment/delete=1, except=1 · Call: `any`, `inspect.signature`, `params.values`
- L212–222 **`_potong`** · kontrol=2, assignment/delete=3, except=1 · Call: `float`, `isinstance`, `math.isnan`, `max`, `min`
- L235–251 **`Peta.__init__`** · kontrol=5, assignment/delete=6, except=0 · Call: `'baris {} berisi {} petak, seharusnya {}'.format`, `ValueError`, `enumerate`, `isinstance`, `len`, `list`, `str`
- L255–261 **`Peta.dari_ascii`** · kontrol=2, assignment/delete=1, except=0 · Call: `ValueError`, `b.rstrip`, `cls`, `str`, `str(b).strip`
- L264–269 **`Peta.didalam`** · kontrol=2, assignment/delete=1, except=1 · Call: `int`
- L271–273 **`Peta.simbol`** · kontrol=0, assignment/delete=1, except=0 · Call: `int`
- L275–276 **`Peta.jenis`** · kontrol=0, assignment/delete=0, except=0 · Call: `LEGENDA_MEDAN.get`, `self.simbol`
- L278–282 **`Peta.bisa_dilewati`** · kontrol=1, assignment/delete=0, except=0 · Call: `BIAYA_MEDAN.get`, `int`, `self.didalam`, `self.jenis`
- L284–289 **`Peta.biaya`** · kontrol=1, assignment/delete=1, except=0 · Call: `BIAYA_MEDAN.get`, `float`, `int`, `self.didalam`, `self.jenis`
- L291–293 **`Peta.petak`** · kontrol=2, assignment/delete=0, except=0 · Call: `range`
- L295–296 **`Peta.petak_bisa_dilewati`** · kontrol=1, assignment/delete=0, except=0 · Call: `self.bisa_dilewati`, `self.petak`
- L299–301 **`Peta.to_dict`** · kontrol=1, assignment/delete=0, except=0 · Call: `''.join`
- L304–306 **`Peta.from_dict`** · kontrol=2, assignment/delete=0, except=0 · Call: `cls`, `data.get`, `str`
- L308–310 **`Peta.__repr__`** · kontrol=0, assignment/delete=0, except=0 · Call: `'Peta({}x{}, nama={!r})'.format`
- L323–331 **`ObjekDunia.__init__`** · kontrol=1, assignment/delete=7, except=0 · Call: `bool`, `dict`, `int`, `self.atribut.get`, `str`
- L333–344 **`ObjekDunia.efek`** · kontrol=3, assignment/delete=4, except=0 · Call: `(self.atribut.get('delta') or {}).items`, `EFEK_JENIS.get`, `bawaan.get`, `bool`, `dict`, `float`, `self.atribut.get`, `str`
- L346–350 **`ObjekDunia.to_dict`** · kontrol=0, assignment/delete=0, except=0 · Call: `copy.deepcopy`, `list`
- L353–360 **`ObjekDunia.from_dict`** · kontrol=1, assignment/delete=4, except=0 · Call: `bool`, `cls`, `data.get`, `int`, `str`, `tuple`
- L362–364 **`ObjekDunia.__repr__`** · kontrol=0, assignment/delete=0, except=0 · Call: `'ObjekDunia({!r}, {!r}, {})'.format`
- L378–394 **`Badan.__init__`** · kontrol=0, assignment/delete=14, except=0 · Call: `int`, `str`
- L396–408 **`Badan.to_dict`** · kontrol=3, assignment/delete=0, except=0 · Call: `dict`, `float`, `int`, `list`, `round`, `self.satiasi.items`, `sorted`
- L411–427 **`Badan.from_dict`** · kontrol=9, assignment/delete=11, except=0 · Call: `(data.get('satiasi') or {}).items`, `cls`, `data.get`, `dict`, `float`, `int`, `str`, `tuple`
- L429–430 **`Badan.__repr__`** · kontrol=0, assignment/delete=0, except=0 · Call: `'Badan({!r}, posisi={})'.format`
- L454–471 **`Lingkungan.__init__`** · kontrol=0, assignment/delete=15, except=0 · Call: `float`, `int`, `max`, `peta_contoh`, `random.Random`, `self.rng.randint`
- L475–477 **`Lingkungan.dari_ascii`** · kontrol=0, assignment/delete=0, except=0 · Call: `Peta.dari_ascii`, `cls`
- L480–498 **`Lingkungan.tambah_objek`** · kontrol=3, assignment/delete=6, except=0 · Call: `'objek {!r} sudah ada'.format`, `'posisi {} di luar peta'.format`, `'{}{}'.format`, `ObjekDunia`, `ValueError`, `int`, `self._urutan_objek.get`, `self.peta.didalam`, `str`
- L500–515 **`Lingkungan.tambah_npc`** · kontrol=4, assignment/delete=4, except=0 · Call: `'NPC {!r} sudah terdaftar'.format`, `'npc{}'.format`, `'posisi {} di luar peta'.format`, `'posisi {} tidak bisa dilewati'.format`, `Badan`, `ValueError`, `getattr`, `int`, `len`, `self._antrean.setdefault`, `self.peta.bisa_dilewati`, `self.peta.didalam`, `str`
- L517–519 **`Lingkungan.npc`** · kontrol=0, assignment/delete=0, except=0 · Call: `str`
- L521–523 **`Lingkungan.nama_badan`** · kontrol=0, assignment/delete=0, except=0 · Call: `sorted`
- L526–531 **`Lingkungan.fase`** · kontrol=2, assignment/delete=0, except=0 · Call: tidak ada
- L533–535 **`Lingkungan.konteks`** · kontrol=0, assignment/delete=0, except=0 · Call: `'{}|{}|{}'.format`, `self.fase`
- L537–545 **`Lingkungan._maju_cuaca`** · kontrol=2, assignment/delete=5, except=0 · Call: `float`, `list`, `self.rng.choice`, `self.rng.randint`
- L548–601 **`Lingkungan.observasi`** · kontrol=9, assignment/delete=9, except=0 · Call: `'NPC tidak dikenal: {!r}'.format`, `ValueError`, `_arah_relatif`, `_jarak`, `list`, `npc_terlihat.append`, `objek_terlihat.append`, `round`, `self._ringkas`, `self.fase`, `self.nama_badan`, `self.objek.values`, `self.paparan`, `self.peta.jenis`, `self.peta.petak`, `sorted`, `str`
- L603–620 **`Lingkungan._ringkas`** · kontrol=4, assignment/delete=3, except=0 · Call: `', '.join`, `'; '.join`, `'aku di {} pada petak {}'.format`, `'{} dan {}'.format`, `'{} di petakku'.format`, `'{} {} langkah ke {}'.format`, `bagian.append`, `int`, `list`, `self.fase`, `self.peta.jenis`, `sorted`, `str`
- L622–634 **`Lingkungan.paparan`** · kontrol=4, assignment/delete=4, except=0 · Call: `_jarak`, `hasil.append`, `round`, `self.objek.values`, `sorted`, `str`
- L637–789 **`Lingkungan.aksi_tersedia`** · kontrol=35, assignment/delete=21, except=0 · Call: `'ambil:{}'.format`, `'bergerak:{}'.format`, `'dekati:{}'.format`, `'hampiri:{}'.format`, `'menjauh:{}'.format`, `'pakai:{}'.format`, `'sapa:{}'.format`, `(c.get('drive_effects') or {}).items`, `ARAH.items`, `_jarak`, `any`, `badan.satiasi.get`, `c.get`, `dict`, `float`, `harapan.get`, `kandidat.append`, `list`, `o.efek`, `o.efek()['delta'].items`, `round`, `self._ada_tempat_aman`, `self._ditempati`, `self._efek_istirahat`, `self._satu_langkah_ke`, `self.nama_badan`, `self.objek.get`, `self.objek.values`, `self.paparan`, `self.peta.biaya`, `self.peta.bisa_dilewati`, `set`, `sorted`, `str`, `str(c['name']).split`
- L791–795 **`Lingkungan._ada_tempat_aman`** · kontrol=2, assignment/delete=0, except=0 · Call: `_jarak`, `any`, `self.objek.values`
- L797–801 **`Lingkungan._efek_istirahat`** · kontrol=1, assignment/delete=0, except=0 · Call: `self._ada_tempat_aman`
- L803–809 **`Lingkungan._ditempati`** · kontrol=3, assignment/delete=0, except=0 · Call: `self.badan.items`
- L812–842 **`Lingkungan.pilih_aksi`** · kontrol=10, assignment/delete=13, except=1 · Call: `'choose_action gagal: {}'.format`, `(hasil or {}).get`, `any`, `badan.log.append`, `c.items`, `callable`, `getattr`, `hasil.get`, `isinstance`, `list`, `npc.choose_action`, `self._pilih_defensif`, `self.aksi_tersedia`, `str`
- L844–859 **`Lingkungan._pilih_defensif`** · kontrol=6, assignment/delete=8, except=0 · Call: `c.get`, `efek.items`, `float`, `getattr`, `levels.get`, `max`, `str`
- L861–893 **`Lingkungan.terapkan`** · kontrol=10, assignment/delete=4, except=0 · Call: `'aksi tidak dikenal: {}'.format`, `self._ada_tempat_aman`, `self._aksi_amati`, `self._aksi_ambil`, `self._aksi_bergerak`, `self._aksi_dekati`, `self._aksi_hampiri`, `self._aksi_menjauh`, `self._aksi_pakai`, `self._aksi_sapa`, `self._efek_istirahat`, `self._hasil`, `str`, `str(aksi).partition`
- L896–905 **`Lingkungan._hasil`** · kontrol=7, assignment/delete=0, except=0 · Call: `(antre or {}).items`, `(delta or {}).items`, `(emosi or {}).items`, `bool`, `dict`, `float`, `str`
- L907–934 **`Lingkungan._aksi_bergerak`** · kontrol=5, assignment/delete=11, except=0 · Call: `'arah tidak dikenal: {}'.format`, `'batas peta menghalangi ke {}'.format`, `'bergerak ke {}'.format`, `'berpindah ke {}'.format`, `'petak {} ditempati NPC lain'.format`, `'{} di {} tidak bisa dilewati'.format`, `badan.dikunjungi.append`, `list`, `self._ditempati`, `self._hasil`, `self.peta.biaya`, `self.peta.bisa_dilewati`, `self.peta.didalam`, `self.peta.jenis`
- L936–952 **`Lingkungan._aksi_ambil`** · kontrol=4, assignment/delete=3, except=0 · Call: `'mengambil {}'.format`, `'objek {} belum terlihat'.format`, `'objek {} tidak ada'.format`, `'objek {} tidak di petak ini'.format`, `_jarak`, `badan.inventaris.append`, `self._hasil`, `self.objek.get`
- L954–981 **`Lingkungan._aksi_pakai`** · kontrol=10, assignment/delete=10, except=0 · Call: `'efek {}'.format`, `'objek {} sudah tidak aktif'.format`, `'objek {} tidak ada'.format`, `'terlalu jauh untuk memakai {}'.format`, `ObjekDunia`, `_jarak`, `badan.inventaris.remove`, `efek.get`, `o.efek`, `self._hasil`, `self.objek.get`
- L983–996 **`Lingkungan._satu_langkah_ke`** · kontrol=4, assignment/delete=2, except=0 · Call: `ARAH.items`, `_jarak`, `kandidat.append`, `kandidat.sort`, `self._ditempati`, `self.peta.bisa_dilewati`
- L998–1012 **`Lingkungan._pindah_ke`** · kontrol=1, assignment/delete=9, except=0 · Call: `'berpindah ke {}'.format`, `badan.dikunjungi.append`, `list`, `self._hasil`, `self.peta.biaya`
- L1014–1032 **`Lingkungan._aksi_dekati`** · kontrol=5, assignment/delete=5, except=0 · Call: `'mendekati {}'.format`, `'mendekati {}; {}'.format`, `'objek {} belum terlihat'.format`, `'objek {} tidak ada'.format`, `'sudah di petak {}'.format`, `'tidak ada jalan menuju {}'.format`, `_jarak`, `self._hasil`, `self._pindah_ke`, `self._satu_langkah_ke`, `self.objek.get`
- L1034–1049 **`Lingkungan._aksi_hampiri`** · kontrol=3, assignment/delete=5, except=0 · Call: `'NPC {} tidak ada'.format`, `'menghampiri {}'.format`, `'menghampiri {}; {}'.format`, `'sudah dekat dengan {}'.format`, `'tidak ada jalan ke {}'.format`, `_jarak`, `self._hasil`, `self._pindah_ke`, `self._satu_langkah_ke`, `self.badan.get`
- L1051–1080 **`Lingkungan._aksi_menjauh`** · kontrol=8, assignment/delete=7, except=0 · Call: `'bahaya {} tidak ada'.format`, `'bertahan menjauh dari {}'.format`, `'jarak {} → {}'.format`, `'menjauh dari {} ke {}'.format`, `ARAH.items`, `_jarak`, `badan.dikunjungi.append`, `int`, `kandidat.append`, `kandidat.sort`, `self._ditempati`, `self._hasil`, `self.objek.get`, `self.peta.bisa_dilewati`
- L1082–1108 **`Lingkungan._aksi_sapa`** · kontrol=6, assignment/delete=6, except=2 · Call: `' (berinteraksi gagal: {})'.format`, `'NPC {} tidak ada'.format`, `'disapa {}'.format`, `'menyapa {}'.format`, `'{} terlalu jauh untuk disapa'.format`, `_jarak`, `callable`, `getattr`, `npc.berinteraksi`, `npc.kenal`, `self._hasil`, `self.badan.get`
- L1110–1123 **`Lingkungan._aksi_amati`** · kontrol=5, assignment/delete=4, except=0 · Call: `', '.join`, `'; terungkap: {}'.format`, `_jarak`, `self._hasil`, `self.objek.values`, `sorted`, `terungkap.append`
- L1126–1153 **`Lingkungan.peristiwa_lingkungan`** · kontrol=6, assignment/delete=7, except=0 · Call: `'terpapar {}'.format`, `float`, `peristiwa.append`, `self.fase`, `self.paparan`, `str`
- L1155–1157 **`Lingkungan._antre`** · kontrol=1, assignment/delete=0, except=0 · Call: `dict`, `self._antrean.setdefault`, `self._antrean.setdefault(str(nama), []).extend`, `str`
- L1159–1162 **`Lingkungan._ambil_antrean`** · kontrol=1, assignment/delete=2, except=0 · Call: `dict`, `self._antrean.get`, `str`
- L1164–1177 **`Lingkungan._ke_events`** · kontrol=7, assignment/delete=1, except=0 · Call: `(delta or {}).items`, `(emosi or {}).items`, `abs`, `e.items`, `events.append`, `float`, `isinstance`, `str`
- L1180–1309 **`Lingkungan.langkah`** · kontrol=27, assignment/delete=31, except=3 · Call: `'NPC tidak dikenal: {!r}'.format`, `'catat memori gagal: {}'.format`, `'predict gagal: {}'.format`, `'reward_for gagal: {}'.format`, `(hasil.get('antre') or {}).items`, `ValueError`, `_menerima_action_cost`, `_potong`, `badan.jejak.predict`, `badan.jejak.record_experience`, `badan.jejak.reinforce`, `badan.log.append`, `badan.satiasi.get`, `bool`, `callable`, `delta.values`, `float`, `getattr`, `hasil.get`, `hasil['delta'].items`, `isinstance`, `len`, `list`, `max`, `min`, `npc.reward_for`, `npc.tick`, `prediksi.get`, `round`, `self._ambil_antrean`, `self._antre`, `self._ke_events`, `self.aksi_tersedia`, `self.fase`, `self.konteks`, `self.observasi`, `self.pilih_aksi`, `self.riwayat.append`, `self.terapkan`, `str`, `str(pilihan['aksi']).split`, `sum`
- L1311–1323 **`Lingkungan.langkah_semua`** · kontrol=5, assignment/delete=3, except=0 · Call: `'NPC {!r} tidak terdaftar'.format`, `KeyError`, `self._antre`, `self._maju_cuaca`, `self.langkah`, `self.nama_badan`, `self.peristiwa_lingkungan`, `str`
- L1325–1331 **`Lingkungan.jalankan`** · kontrol=1, assignment/delete=1, except=0 · Call: `hasil.extend`, `int`, `max`, `range`, `self.langkah_semua`, `self.statistik`
- L1334–1369 **`Lingkungan.statistik`** · kontrol=5, assignment/delete=7, except=0 · Call: `aksi.get`, `dict`, `dict(levels).items`, `float`, `getattr`, `isinstance`, `len`, `list`, `round`, `self.fase`, `self.nama_badan`, `self.objek.values`, `str`, `str(baris['aksi']).split`, `sum`
- L1372–1391 **`Lingkungan.render`** · kontrol=9, assignment/delete=9, except=0 · Call: `' | fokus: {}'.format`, `''.join`, `'\n'.join`, `'{} — tick {} | {} | {}'.format`, `SIMBOL_OBJEK.get`, `chr`, `enumerate`, `range`, `self.fase`, `self.nama_badan`, `self.objek.values`, `self.peta.petak`, `self.peta.simbol`, `sorted`
- L1393–1414 **`Lingkungan.lihat_sekitar`** · kontrol=7, assignment/delete=5, except=0 · Call: `''.join`, `'\n'.join`, `SIMBOL_OBJEK.get`, `baris.append`, `int`, `next`, `potong.append`, `range`, `self._ditempati`, `self.objek.values`, `self.peta.didalam`, `self.peta.simbol`, `str`
- L1417–1434 **`Lingkungan.to_dict`** · kontrol=5, assignment/delete=0, except=0 · Call: `dict`, `round`, `self._antrean.items`, `self.badan.items`, `self.objek.items`, `self.peta.to_dict`, `sorted`, `v.to_dict`
- L1437–1466 **`Lingkungan.from_dict`** · kontrol=11, assignment/delete=11, except=0 · Call: `(data.get('antrean') or {}).items`, `(data.get('badan') or {}).items`, `(data.get('objek') or {}).items`, `Badan.from_dict`, `ObjekDunia.from_dict`, `Peta.from_dict`, `cls`, `data.get`, `dict`, `dunia._antre`, `dunia._antrean.setdefault`, `float`, `int`, `jejak.get`, `npcs.get`, `o.get`, `str`
- L1468–1470 **`Lingkungan.__repr__`** · kontrol=0, assignment/delete=0, except=0 · Call: `'Lingkungan({!r}, npc={}, objek={}, tick={})'.format`, `len`
- L1476–1487 **`peta_contoh`** · kontrol=0, assignment/delete=0, except=0 · Call: `Peta.dari_ascii`
- L1490–1529 **`demo`** · kontrol=3, assignment/delete=4, except=0 · Call: `'  [t{:03d}] {:<5} {:<22} {} ({})'.format`, `Lingkungan`, `Naluri`, `dunia.langkah_semua`, `dunia.lihat_sekitar`, `dunia.render`, `dunia.statistik`, `dunia.tambah_npc`, `dunia.tambah_objek`, `int`, `max`, `peta_contoh`, `print`, `range`

## `pycos/mandiri/__init__.py`

SHA-256: `73d83ee302bdb515fd1dd3d849e2e0c06597591f29171fd98d0cf73319da8711`

85 baris; 0 kelas; 2 fungsi/metode termasuk nested.

Kelas: tidak ada.
Handler luas: tidak ada.

Impor (termasuk lazy/TYPE_CHECKING): `from .kognisi_lanjut import EMOSI_NODE, GrafAsosiasi, KognisiLanjut, MesinKepercayaan, ProsesOU, EversiTD, boltzmann_pilih, suhu_mental`; `from .organik import KALIMAT_ADA_SESUATU, KALIMAT_TAK_BERNAMA, KOSONG, PROPERTI_TERLARANG, TAK_BERLAKU, TERISI, Apersepsi, BatasIdentitas, DetakInternal, Gejala, GejalaMurni, Invensi, Intrusi, KategoriProto, LapisanParalel, LukaDomain, ModelKausal, Organik, PenolakanTutur, Perencana, Residu, TubuhSumber, TopologiSlot, Vacancy, WaktuHeterogen`; `from __future__ import annotations`; `from importlib import import_module`; `from typing import TYPE_CHECKING, Any, Dict, List`.

- L73–81 **`__getattr__`** · kontrol=1, assignment/delete=3, except=0 · Call: `'paket {!r} tidak punya atribut {!r}'.format`, `'{}.{}'.format`, `AttributeError`, `_SUBMODUL.get`, `getattr`, `globals`, `import_module`
- L84–85 **`__dir__`** · kontrol=0, assignment/delete=0, except=0 · Call: `globals`, `set`, `sorted`

## `pycos/mandiri/kognisi_lanjut.py`

SHA-256: `815fde42a67a03b84947640a52a5230402e4eb5c15992246161e60c31c8e2ac3`

609 baris; 5 kelas; 48 fungsi/metode termasuk nested.

Kelas: `EversiTD` L36, `MesinKepercayaan` L217, `GrafAsosiasi` L300, `ProsesOU` L463, `KognisiLanjut` L517.
Handler luas: tidak ada.

Impor (termasuk lazy/TYPE_CHECKING): `from __future__ import annotations`; `from typing import Any, Dict, Iterable, List, Optional, Tuple`; `import math`; `import random`.

- L21–31 **`jepit_drive`** · kontrol=2, assignment/delete=3, except=1 · Call: `float`, `isinstance`
- L44–71 **`EversiTD.__init__`** · kontrol=1, assignment/delete=17, except=0 · Call: `dict`, `float`
- L74–84 **`EversiTD.reward_intrinsik`** · kontrol=1, assignment/delete=5, except=0 · Call: `float`
- L87–88 **`EversiTD._nilai`** · kontrol=0, assignment/delete=0, except=0 · Call: `self.q.get`, `self.q.get(s, {}).get`
- L90–92 **`EversiTD._maks`** · kontrol=0, assignment/delete=1, except=0 · Call: `d.values`, `max`, `self.q.get`
- L94–103 **`EversiTD.update`** · kontrol=0, assignment/delete=7, except=0 · Call: `float`, `self._maks`, `self._nilai`, `self.kunjungan.get`, `self.q.setdefault`
- L105–106 **`EversiTD.nilai`** · kontrol=0, assignment/delete=0, except=0 · Call: `self._nilai`
- L108–109 **`EversiTD.nilai_situasi`** · kontrol=0, assignment/delete=0, except=0 · Call: `self._maks`
- L112–127 **`EversiTD.eversi_param`** · kontrol=4, assignment/delete=9, except=0 · Call: `dict`, `float`, `len`, `math.isfinite`, `math.tanh`, `max`, `min`, `self._maks`, `self.acuan.items`, `self.arah.get`, `sum`
- L129–130 **`EversiTD.ambil`** · kontrol=0, assignment/delete=0, except=0 · Call: `float`, `self.acuan.get`, `self.eversi.get`
- L133–143 **`EversiTD.to_dict`** · kontrol=1, assignment/delete=0, except=0 · Call: `dict`, `self.q.items`
- L146–163 **`EversiTD.from_dict`** · kontrol=5, assignment/delete=10, except=0 · Call: `(d.get('q') or {}).items`, `cls`, `d.get`, `dict`, `float`, `tuple`
- L169–175 **`suhu_mental`** · kontrol=0, assignment/delete=1, except=0 · Call: `float`, `max`, `min`
- L178–199 **`boltzmann_pilih`** · kontrol=7, assignment/delete=8, except=0 · Call: `(rng or random).random`, `bobot.items`, `bobot.values`, `dist.items`, `float`, `math.exp`, `max`, `skor.items`, `skor.values`, `sum`
- L205–209 **`_sigmoid`** · kontrol=1, assignment/delete=1, except=0 · Call: `math.exp`
- L212–214 **`_logit`** · kontrol=0, assignment/delete=1, except=0 · Call: `float`, `math.log`, `max`, `min`
- L224–230 **`MesinKepercayaan.__init__`** · kontrol=0, assignment/delete=5, except=0 · Call: `float`
- L232–237 **`MesinKepercayaan.tetapkan`** · kontrol=0, assignment/delete=3, except=0 · Call: `_logit`, `float`, `self.bukti.setdefault`, `self.kepercayaan`, `str`
- L239–243 **`MesinKepercayaan.kepercayaan`** · kontrol=1, assignment/delete=1, except=0 · Call: `_sigmoid`, `str`
- L245–259 **`MesinKepercayaan.perbarui`** · kontrol=3, assignment/delete=4, except=0 · Call: `float`, `len`, `math.log`, `max`, `round`, `self.bukti.setdefault`, `self.bukti.setdefault(h, []).append`, `self.kepercayaan`, `self.tetapkan`, `str`
- L261–264 **`MesinKepercayaan.curiga`** · kontrol=0, assignment/delete=1, except=0 · Call: `float`, `self.kepercayaan`
- L266–270 **`MesinKepercayaan.entropi`** · kontrol=2, assignment/delete=1, except=0 · Call: `math.log2`, `self.kepercayaan`
- L272–273 **`MesinKepercayaan.ringkas`** · kontrol=1, assignment/delete=0, except=0 · Call: `round`, `self.kepercayaan`
- L275–280 **`MesinKepercayaan.to_dict`** · kontrol=1, assignment/delete=0, except=0 · Call: `dict`, `list`, `self.bukti.items`
- L283–289 **`MesinKepercayaan.from_dict`** · kontrol=4, assignment/delete=4, except=0 · Call: `(d.get('bukti') or {}).items`, `cls`, `d.get`, `dict`, `list`
- L307–318 **`GrafAsosiasi.__init__`** · kontrol=0, assignment/delete=9, except=0 · Call: `float`, `int`
- L321–323 **`GrafAsosiasi._kunci`** · kontrol=0, assignment/delete=1, except=0 · Call: `str`, `str(a).strip`, `str(a).strip().lower`, `str(b).strip`, `str(b).strip().lower`
- L325–343 **`GrafAsosiasi.koaktifkan`** · kontrol=4, assignment/delete=7, except=0 · Call: `float`, `len`, `max`, `min`, `round`, `self._jaga_ukuran`, `self._kunci`, `self.asosiasi_terbentuk.append`, `self.edge.get`, `str`, `str(a).strip`, `str(a).strip().lower`, `str(b).strip`, `str(b).strip().lower`
- L345–372 **`GrafAsosiasi.aktifkan`** · kontrol=9, assignment/delete=11, except=0 · Call: `baru.get`, `baru.items`, `dict`, `dikunjungi.update`, `float`, `int`, `max`, `min`, `range`, `self.aktivasi.get`, `self.edge.items`, `str`, `str(konsep).strip`, `str(konsep).strip().lower`
- L374–375 **`GrafAsosiasi.bobot`** · kontrol=0, assignment/delete=0, except=0 · Call: `self._kunci`, `self.edge.get`
- L377–389 **`GrafAsosiasi.asosiasi`** · kontrol=4, assignment/delete=2, except=0 · Call: `out.append`, `out.sort`, `self.edge.items`, `str`, `str(konsep).strip`, `str(konsep).strip().lower`
- L391–394 **`GrafAsosiasi.emosi_terasosiasi`** · kontrol=1, assignment/delete=0, except=0 · Call: `self.asosiasi`
- L396–405 **`GrafAsosiasi.fobia`** · kontrol=4, assignment/delete=2, except=0 · Call: `float`, `out.append`, `out.sort`, `round`, `self.edge.items`
- L407–415 **`GrafAsosiasi.luruh`** · kontrol=4, assignment/delete=4, except=0 · Call: `float`, `list`, `max`
- L417–421 **`GrafAsosiasi._jaga_ukuran`** · kontrol=2, assignment/delete=1, except=0 · Call: `len`, `self.edge.items`, `sorted`
- L423–434 **`GrafAsosiasi.to_dict`** · kontrol=2, assignment/delete=0, except=0 · Call: `dict`, `self.edge.items`
- L437–457 **`GrafAsosiasi.from_dict`** · kontrol=15, assignment/delete=7, except=0 · Call: `'GrafAsosiasi.format tidak didukung: {!r}'.format`, `(d.get('edge') or {}).items`, `ValueError`, `cls`, `d.get`, `dict`, `float`, `k.partition`, `str`
- L470–477 **`ProsesOU.__init__`** · kontrol=1, assignment/delete=5, except=0 · Call: `dict`, `float`
- L479–480 **`ProsesOU.nilai`** · kontrol=0, assignment/delete=0, except=0 · Call: `self.x.get`, `str`
- L482–497 **`ProsesOU.langkah`** · kontrol=2, assignment/delete=11, except=0 · Call: `float`, `math.sqrt`, `max`, `min`, `r.gauss`, `self.mu.get`, `self.x.get`, `str`
- L499–500 **`ProsesOU.ringkas`** · kontrol=1, assignment/delete=0, except=0 · Call: `round`, `self.x.items`
- L502–504 **`ProsesOU.to_dict`** · kontrol=0, assignment/delete=0, except=0 · Call: `dict`
- L507–511 **`ProsesOU.from_dict`** · kontrol=1, assignment/delete=2, except=0 · Call: `cls`, `d.get`, `dict`
- L520–530 **`KognisiLanjut.__init__`** · kontrol=1, assignment/delete=7, except=0 · Call: `EversiTD`, `GrafAsosiasi`, `MesinKepercayaan`, `ProsesOU`, `int`, `kw.items`, `random.Random`
- L532–536 **`KognisiLanjut.aktifkan`** · kontrol=2, assignment/delete=1, except=0 · Call: `bool`, `flag.items`
- L539–572 **`KognisiLanjut.langkah`** · kontrol=11, assignment/delete=13, except=0 · Call: `abs`, `emosi.get`, `ev.items`, `float`, `ink.items`, `jepit_drive`, `len`, `levels.get`, `list`, `max`, `round`, `self.eversi.ambil`, `self.eversi.eversi_param`, `self.eversi.reward_intrinsik`, `self.graf.bobot`, `self.graf.koaktifkan`, `self.graf.luruh`, `self.ou.langkah`, `self.ou.ringkas`, `self.riwayat.append`
- L574–580 **`KognisiLanjut.to_dict`** · kontrol=0, assignment/delete=1, except=0 · Call: `dict`, `list`, `self.eversi.to_dict`, `self.graf.to_dict`, `self.kepercayaan.to_dict`, `self.ou.to_dict`, `self.rng.getstate`
- L583–605 **`KognisiLanjut.from_dict`** · kontrol=12, assignment/delete=7, except=1 · Call: `EversiTD.from_dict`, `GrafAsosiasi.from_dict`, `MesinKepercayaan.from_dict`, `ProsesOU.from_dict`, `ValueError`, `cls`, `d.get`, `isinstance`, `len`, `math.isfinite`, `o.aktif.update`, `o.rng.setstate`, `tuple`

## `pycos/mandiri/organik.py`

SHA-256: `824402cd7386a32054f56cf312ce673bb2d8f537ad65c308c36236e32cfbba68`

3422 baris; 19 kelas; 217 fungsi/metode termasuk nested.

Kelas: `Residu` L136, `Intrusi` L350, `DetakInternal` L473, `TopologiSlot` L589, `LukaDomain` L714, `BatasIdentitas` L793, `WaktuHeterogen` L888, `PenolakanTutur` L1025, `Apersepsi` L1149, `LapisanParalel` L1277, `TubuhSumber` L1381, `Vacancy` L1476, `GejalaMurni` L1575, `KategoriProto` L1682, `Gejala` L1768, `Invensi` L2139, `ModelKausal` L2505, `Perencana` L2808, `Organik` L3063.
Handler luas: 368, 500, 2443, 491, 2360.

Impor (termasuk lazy/TYPE_CHECKING): `from __future__ import annotations`; `from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple`; `import math`; `import random`; `import re`; `import zlib`.

- L114–126 **`_kclip`** · kontrol=2, assignment/delete=3, except=1 · Call: `float`, `isinstance`
- L129–130 **`_teks`** · kontrol=0, assignment/delete=0, except=0 · Call: `str`
- L167–176 **`Residu.__init__`** · kontrol=0, assignment/delete=5, except=0 · Call: tidak ada
- L179–180 **`Residu._nama`** · kontrol=0, assignment/delete=0, except=0 · Call: `_teks`, `_teks(x).strip`, `_teks(x).strip().lower`
- L183–187 **`Residu._mag`** · kontrol=1, assignment/delete=0, except=1 · Call: `_kclip`, `abs`, `float`
- L189–220 **`Residu.daftar`** · kontrol=5, assignment/delete=13, except=0 · Call: `_teks`, `dict`, `float`, `int`, `lama.get`, `nama_target.get`, `self._aktif.get`, `self._arsip.append`, `self._mag`, `self._nama`
- L222–227 **`Residu.tekanan_target`** · kontrol=1, assignment/delete=1, except=0 · Call: `_kclip`, `entri.get`, `float`, `self._aktif.get`, `self._nama`
- L229–234 **`Residu.tekanan`** · kontrol=1, assignment/delete=2, except=0 · Call: `_kclip`, `self.tekanan_target`
- L236–243 **`Residu._pengaruh`** · kontrol=3, assignment/delete=4, except=0 · Call: `max`, `self._nama`, `self.tekanan_target`, `tabel.get`
- L245–250 **`Residu.ambang_dimodifikasi`** · kontrol=0, assignment/delete=2, except=0 · Call: `_kclip`, `float`, `max`, `self._pengaruh`
- L252–256 **`Residu.langit_dimodifikasi`** · kontrol=0, assignment/delete=2, except=0 · Call: `float`, `max`, `self._pengaruh`
- L258–286 **`Residu.tambal`** · kontrol=4, assignment/delete=10, except=0 · Call: `_teks`, `_teks(peristiwa).strip`, `bool`, `dict`, `entri.get`, `float`, `int`, `kena.append`, `len`, `list`, `min`, `self._aktif.get`, `self._aktif.keys`, `self._mag`, `self._nama`, `self._tambalan.append`
- L293–311 **`Residu.bekas`** · kontrol=3, assignment/delete=3, except=0 · Call: `_teks`, `dict`, `int`, `len`, `rincian.items`, `self._bekas.append`
- L313–314 **`Residu.bekas_state`** · kontrol=1, assignment/delete=0, except=0 · Call: `dict`
- L316–322 **`Residu.state`** · kontrol=4, assignment/delete=0, except=0 · Call: `dict`, `round`, `self._aktif.items`, `self.tekanan`, `self.tekanan_target`
- L324–329 **`Residu.to_dict`** · kontrol=4, assignment/delete=0, except=0 · Call: `dict`, `self._aktif.items`
- L332–344 **`Residu.from_dict`** · kontrol=10, assignment/delete=6, except=0 · Call: `(d.get('aktif') or {}).items`, `cls`, `d.get`, `dict`, `int`, `isinstance`, `str`
- L358–362 **`Intrusi.__init__`** · kontrol=0, assignment/delete=4, except=0 · Call: `float`, `int`, `max`
- L365–369 **`Intrusi._acak`** · kontrol=1, assignment/delete=0, except=1 · Call: `_RNG_CADANGAN.random`, `float`, `rng.random`
- L371–404 **`Intrusi._pilih_slot`** · kontrol=19, assignment/delete=12, except=0 · Call: `(affective or {}).values`, `abs`, `calon.append`, `dampak.get`, `dampak.values`, `drives.get`, `float`, `int`, `isinstance`, `math.log`, `math.log1p`, `max`, `min`, `residu.tekanan_target`, `self._acak`, `slot.get`, `sum`
- L406–447 **`Intrusi.coba`** · kontrol=11, assignment/delete=19, except=0 · Call: `'kenapa aku masih memikirkan {}?'.format`, `'{} — aneh, ini mengingatkanku pada {}'.format`, `_kclip`, `_teks`, `dict`, `float`, `int`, `len`, `max`, `residu.tekanan`, `round`, `self._acak`, `self._log.append`, `self._pilih_slot`, `slot.get`, `spotlight[0].get`
- L449–453 **`Intrusi.state`** · kontrol=0, assignment/delete=0, except=0 · Call: `dict`, `len`
- L455–458 **`Intrusi.to_dict`** · kontrol=1, assignment/delete=0, except=0 · Call: `dict`
- L461–467 **`Intrusi.from_dict`** · kontrol=3, assignment/delete=3, except=0 · Call: `cls`, `d.get`, `dict`, `int`, `isinstance`
- L484–494 **`DetakInternal.__init__`** · kontrol=2, assignment/delete=6, except=1 · Call: `_RNG_CADANGAN.random`, `float`, `rng.random`, `self._ambang_baru`
- L497–501 **`DetakInternal._ambang_baru`** · kontrol=1, assignment/delete=0, except=1 · Call: `_RNG_CADANGAN.random`, `float`, `rng.random`
- L504–520 **`DetakInternal._rate`** · kontrol=14, assignment/delete=6, except=0 · Call: `emosi.get`, `felt.get`, `float`, `levels.get`, `max`, `state.get`
- L522–547 **`DetakInternal.maju`** · kontrol=4, assignment/delete=13, except=0 · Call: `_teks`, `dict`, `float`, `keluar.append`, `len`, `max`, `round`, `self._ambang_baru`, `self._log.append`, `self._rate`
- L549–555 **`DetakInternal.paksa`** · kontrol=1, assignment/delete=2, except=0 · Call: `float`, `max`, `self._nama_proses`
- L558–562 **`DetakInternal._nama_proses`** · kontrol=0, assignment/delete=2, except=0 · Call: `_teks`, `_teks(nama).strip`, `_teks(nama).strip().lower`, `_teks(nama).strip().lower().replace`, `alias.get`
- L564–568 **`DetakInternal.state`** · kontrol=2, assignment/delete=0, except=0 · Call: `dict`, `len`, `round`, `self._jam.items`, `v.items`
- L570–572 **`DetakInternal.to_dict`** · kontrol=2, assignment/delete=0, except=0 · Call: `dict`, `self._jam.items`
- L575–583 **`DetakInternal.from_dict`** · kontrol=7, assignment/delete=3, except=0 · Call: `(d.get('jam') or {}).items`, `cls`, `d.get`, `dict`, `float`, `isinstance`, `jam.get`, `max`
- L605–606 **`TopologiSlot.__init__`** · kontrol=0, assignment/delete=1, except=0 · Call: tidak ada
- L609–620 **`TopologiSlot.daftar`** · kontrol=3, assignment/delete=4, except=0 · Call: `_teks`, `dict`, `int`, `s['bekas'].update`, `self._slot.get`
- L622–624 **`TopologiSlot.peek`** · kontrol=0, assignment/delete=0, except=0 · Call: `_teks`, `dict`, `self._slot.get`
- L627–638 **`TopologiSlot.kosongkan`** · kontrol=1, assignment/delete=5, except=0 · Call: `_teks`, `dict`, `int`, `self.daftar`
- L640–650 **`TopologiSlot.isi_ulang`** · kontrol=0, assignment/delete=6, except=0 · Call: `_teks`, `dict`, `int`, `self.daftar`
- L653–654 **`TopologiSlot.terisi`** · kontrol=0, assignment/delete=0, except=0 · Call: `_teks`, `self._slot.get`, `self._slot.get(_teks(ent), {}).get`
- L656–657 **`TopologiSlot.kosong`** · kontrol=1, assignment/delete=0, except=0 · Call: `s.get`, `self._slot.items`
- L659–660 **`TopologiSlot.semua`** · kontrol=0, assignment/delete=0, except=0 · Call: `list`, `self._slot.keys`
- L662–672 **`TopologiSlot.intensitas`** · kontrol=2, assignment/delete=1, except=0 · Call: `_teks`, `float`, `self.terisi`
- L674–676 **`TopologiSlot.layak_cabang`** · kontrol=0, assignment/delete=0, except=0 · Call: `self.terisi`
- L678–689 **`TopologiSlot.cabang_mustahil`** · kontrol=4, assignment/delete=2, except=0 · Call: `_teks`, `self.kosong`
- L692–693 **`TopologiSlot.to_dict`** · kontrol=1, assignment/delete=0, except=0 · Call: `dict`, `self._slot.items`
- L696–708 **`TopologiSlot.from_dict`** · kontrol=6, assignment/delete=2, except=0 · Call: `(d.get('slot') or {}).items`, `_teks`, `cls`, `d.get`, `dict`, `int`, `isinstance`, `str`, `v.get`
- L727–728 **`LukaDomain.__init__`** · kontrol=0, assignment/delete=1, except=0 · Call: tidak ada
- L730–736 **`LukaDomain.lukai`** · kontrol=1, assignment/delete=3, except=0 · Call: `_teks`, `bool`, `int`, `self._lubang.setdefault`
- L738–741 **`LukaDomain.dikecualikan`** · kontrol=3, assignment/delete=2, except=0 · Call: `_teks`, `self._lubang.get`
- L743–744 **`LukaDomain.domain_terluka`** · kontrol=1, assignment/delete=0, except=0 · Call: `(self._lubang.get(_teks(ent)) or {}).keys`, `_teks`, `self._lubang.get`, `sorted`
- L746–750 **`LukaDomain.terapkan`** · kontrol=1, assignment/delete=0, except=0 · Call: `float`, `self.dikecualikan`
- L752–765 **`LukaDomain.tambal`** · kontrol=5, assignment/delete=4, except=0 · Call: `_teks`, `d.get`, `rec.get`, `self._lubang.get`, `self._lubang.pop`
- L767–768 **`LukaDomain.ringkas`** · kontrol=1, assignment/delete=0, except=0 · Call: `d.keys`, `self._lubang.items`, `sorted`
- L770–772 **`LukaDomain.to_dict`** · kontrol=2, assignment/delete=0, except=0 · Call: `d.items`, `dict`, `self._lubang.items`
- L775–787 **`LukaDomain.from_dict`** · kontrol=7, assignment/delete=2, except=0 · Call: `(d.get('lubang') or {}).items`, `_teks`, `bool`, `cls`, `d.get`, `doms.items`, `int`, `isinstance`, `o._lubang.setdefault`, `str`, `v.get`
- L808–811 **`BatasIdentitas.__init__`** · kontrol=0, assignment/delete=3, except=0 · Call: tidak ada
- L813–832 **`BatasIdentitas.tetapkan`** · kontrol=7, assignment/delete=5, except=0 · Call: `(batas or {}).items`, `_teks`, `float`, `isinstance`, `len`, `r.get`, `self.state`
- L834–847 **`BatasIdentitas.izinkan`** · kontrol=5, assignment/delete=2, except=0 · Call: `_teks`, `float`, `min`, `r.get`, `self._batas.get`
- L849–855 **`BatasIdentitas.catat_penolakan`** · kontrol=1, assignment/delete=1, except=0 · Call: `_teks`, `float`, `int`, `len`, `round`, `self._ditolak.append`
- L857–858 **`BatasIdentitas.penolakan`** · kontrol=1, assignment/delete=0, except=0 · Call: `dict`
- L860–864 **`BatasIdentitas.state`** · kontrol=1, assignment/delete=0, except=0 · Call: `dict`, `len`, `self._batas.items`
- L866–869 **`BatasIdentitas.to_dict`** · kontrol=2, assignment/delete=0, except=0 · Call: `dict`, `self._batas.items`
- L872–882 **`BatasIdentitas.from_dict`** · kontrol=7, assignment/delete=4, except=0 · Call: `(d.get('batas') or {}).items`, `_teks`, `cls`, `d.get`, `dict`, `float`, `isinstance`, `str`, `v.get`
- L899–915 **`WaktuHeterogen.__init__`** · kontrol=0, assignment/delete=10, except=0 · Call: `float`, `max`
- L917–922 **`WaktuHeterogen.daftar`** · kontrol=1, assignment/delete=2, except=0 · Call: `_kclip`, `_teks`, `float`, `self._skala_subjektif.setdefault`
- L924–944 **`WaktuHeterogen.skala_subjektif`** · kontrol=2, assignment/delete=3, except=0 · Call: `_kclip`, `_teks`, `float`, `max`, `self._skala_subjektif.get`, `self.daftar`, `str`
- L946–954 **`WaktuHeterogen.diingat`** · kontrol=1, assignment/delete=3, except=0 · Call: `_kclip`, `_teks`, `int`, `max`, `range`, `self._ingat.get`, `self.daftar`, `self.half_life`
- L956–964 **`WaktuHeterogen.dikoreksi_salah`** · kontrol=1, assignment/delete=3, except=0 · Call: `_kclip`, `_teks`, `int`, `max`, `range`, `self._salah.get`, `self.daftar`, `self.half_life`
- L966–972 **`WaktuHeterogen.half_life`** · kontrol=0, assignment/delete=2, except=0 · Call: `_kclip`, `_teks`, `self._skala_subjektif.get`, `self.daftar`
- L974–976 **`WaktuHeterogen.bobot`** · kontrol=0, assignment/delete=1, except=0 · Call: `float`, `max`, `self.half_life`
- L978–987 **`WaktuHeterogen.ringkas`** · kontrol=4, assignment/delete=2, except=0 · Call: `dict`, `efektif.items`, `len`, `round`, `self._skala_subjektif.items`, `self.half_life`, `sorted`
- L989–996 **`WaktuHeterogen.to_dict`** · kontrol=1, assignment/delete=0, except=0 · Call: `dict`, `self._durasi_subjektif.items`
- L999–1019 **`WaktuHeterogen.from_dict`** · kontrol=12, assignment/delete=6, except=0 · Call: `(d.get('durasi_subjektif') or {}).items`, `(d.get('hl') or {}).items`, `(d.get('ingat') or {}).items`, `(d.get('salah') or {}).items`, `(d.get('skala_subjektif') or {}).items`, `_kclip`, `cls`, `d.get`, `dict`, `int`, `isinstance`, `o._skala_subjektif.setdefault`, `str`
- L1040–1042 **`PenolakanTutur.__init__`** · kontrol=0, assignment/delete=2, except=0 · Call: `float`
- L1044–1058 **`PenolakanTutur.kelayakan`** · kontrol=7, assignment/delete=11, except=0 · Call: `_kclip`, `float`, `k.get`, `komp.values`, `max`, `sum`
- L1060–1063 **`PenolakanTutur.kelayakan_bertipe`** · kontrol=0, assignment/delete=1, except=0 · Call: `self.jenis`, `self.jenis_penolakan`, `self.kelayakan`
- L1065–1070 **`PenolakanTutur.tertahan`** · kontrol=1, assignment/delete=2, except=0 · Call: `_kclip`, `float`, `max`, `r.random`
- L1072–1077 **`PenolakanTutur.jenis`** · kontrol=3, assignment/delete=1, except=0 · Call: `float`, `k.get`, `min`
- L1079–1113 **`PenolakanTutur.bentuk`** · kontrol=9, assignment/delete=5, except=0 · Call: `' '.join`, `_teks`, `_teks(teks_terbentuk).split`, `len`, `list`, `r.choice`, `r.shuffle`, `self.jenis`
- L1115–1117 **`PenolakanTutur.jenis_penolakan`** · kontrol=0, assignment/delete=0, except=0 · Call: `_JENIS_PENOLAKAN.get`, `self.jenis`
- L1119–1130 **`PenolakanTutur.catat`** · kontrol=3, assignment/delete=2, except=0 · Call: `(komponen or {}).items`, `_teks`, `dict`, `float`, `int`, `len`, `round`, `self._riwayat.append`
- L1132–1133 **`PenolakanTutur.riwayat`** · kontrol=1, assignment/delete=0, except=0 · Call: `dict`
- L1135–1136 **`PenolakanTutur.to_dict`** · kontrol=1, assignment/delete=0, except=0 · Call: `dict`
- L1139–1143 **`PenolakanTutur.from_dict`** · kontrol=4, assignment/delete=2, except=0 · Call: `(d or {}).get`, `cls`, `d.get`, `dict`, `isinstance`
- L1167–1173 **`Apersepsi.__init__`** · kontrol=0, assignment/delete=5, except=0 · Call: `float`, `int`, `max`
- L1175–1233 **`Apersepsi.amati`** · kontrol=18, assignment/delete=21, except=0 · Call: `'aku merasa {n}.'.format`, `(felt or {}).items`, `_kclip`, `_teks`, `_teks(klaim_identitas).strip`, `abs`, `bool`, `dict`, `f.keys`, `f.values`, `float`, `len`, `list`, `lv.values`, `math.log`, `max`, `round`, `self._gradien`, `self._riwayat.append`, `self._signature`, `sorted`, `sum`
- L1235–1254 **`Apersepsi._gradien`** · kontrol=13, assignment/delete=7, except=0 · Call: `abs`, `bool`, `float`, `len`, `math.sqrt`, `max`, `range`, `round`, `set`, `set().union`, `sorted`, `sum`, `x.get`, `x.keys`, `zip`
- L1257–1261 **`Apersepsi._signature`** · kontrol=5, assignment/delete=1, except=0 · Call: `'{}='.format`, `'|'.join`, `f.items`, `float`, `round`, `sorted`, `str`
- L1263–1264 **`Apersepsi.to_dict`** · kontrol=1, assignment/delete=0, except=0 · Call: `dict`
- L1267–1271 **`Apersepsi.from_dict`** · kontrol=3, assignment/delete=2, except=0 · Call: `cls`, `d.get`, `dict`, `isinstance`
- L1290–1293 **`LapisanParalel.__init__`** · kontrol=0, assignment/delete=3, except=0 · Call: `int`, `max`
- L1295–1309 **`LapisanParalel.tambah`** · kontrol=3, assignment/delete=3, except=0 · Call: `(emosi or {}).items`, `_kclip`, `_teks`, `dict`, `float`, `int`, `len`, `self._lapisan.append`, `str`
- L1311–1317 **`LapisanParalel.aktif`** · kontrol=4, assignment/delete=1, except=0 · Call: `_teks`, `dict`
- L1319–1325 **`LapisanParalel.pengaruh`** · kontrol=3, assignment/delete=2, except=0 · Call: `float`, `hasil.get`, `hasil.items`, `lap['emosi'].items`, `round`, `self.aktif`
- L1327–1341 **`LapisanParalel.bertentangan`** · kontrol=7, assignment/delete=3, except=0 · Call: `a.get`, `b.get`, `enumerate`, `keluar.append`, `set`
- L1343–1345 **`LapisanParalel.disonansi_paralel`** · kontrol=0, assignment/delete=0, except=0 · Call: tidak ada
- L1347–1348 **`LapisanParalel.tanpa_resolusi`** · kontrol=1, assignment/delete=0, except=0 · Call: `bool`, `len`, `self.bertentangan`
- L1350–1356 **`LapisanParalel.bertindak_dari`** · kontrol=3, assignment/delete=2, except=0 · Call: `_teks`, `dict`, `max`
- L1358–1363 **`LapisanParalel.state`** · kontrol=1, assignment/delete=0, except=0 · Call: `dict`, `len`, `self.bertentangan`, `self.tanpa_resolusi`
- L1365–1367 **`LapisanParalel.to_dict`** · kontrol=1, assignment/delete=0, except=0 · Call: `dict`
- L1370–1375 **`LapisanParalel.from_dict`** · kontrol=5, assignment/delete=3, except=0 · Call: `(d or {}).get`, `cls`, `d.get`, `dict`, `int`, `isinstance`, `len`
- L1395–1413 **`TubuhSumber.__init__`** · kontrol=0, assignment/delete=7, except=0 · Call: `float`
- L1415–1423 **`TubuhSumber.masukan`** · kontrol=6, assignment/delete=4, except=0 · Call: `(emosi or {}).get`, `f.get`, `float`, `max`, `sum`
- L1425–1450 **`TubuhSumber.langkah`** · kontrol=10, assignment/delete=9, except=0 · Call: `(felt or {}).items`, `_kclip`, `abs`, `delta.get`, `delta.items`, `delta.setdefault`, `float`, `len`, `max`, `round`, `self._jejak.append`, `self.arah.get`, `self.arah.get(isyarat, {}).items`, `self.masukan`
- L1452–1455 **`TubuhSumber.suntik`** · kontrol=0, assignment/delete=1, except=0 · Call: `_kclip`, `float`
- L1457–1459 **`TubuhSumber.state`** · kontrol=1, assignment/delete=0, except=0 · Call: `dict`, `round`
- L1461–1463 **`TubuhSumber.to_dict`** · kontrol=1, assignment/delete=0, except=0 · Call: `dict`
- L1466–1473 **`TubuhSumber.from_dict`** · kontrol=4, assignment/delete=3, except=0 · Call: `cls`, `d.get`, `dict`, `float`, `isinstance`
- L1483–1488 **`Vacancy.__init__`** · kontrol=0, assignment/delete=5, except=0 · Call: tidak ada
- L1490–1496 **`Vacancy.mulai`** · kontrol=0, assignment/delete=5, except=0 · Call: `float`, `int`, `max`, `self.state`
- L1498–1510 **`Vacancy.lewat`** · kontrol=3, assignment/delete=6, except=0 · Call: `float`, `int`, `max`, `min`
- L1512–1518 **`Vacancy.state`** · kontrol=0, assignment/delete=0, except=0 · Call: `max`, `round`
- L1520–1523 **`Vacancy.to_dict`** · kontrol=0, assignment/delete=0, except=0 · Call: tidak ada
- L1526–1536 **`Vacancy.from_dict`** · kontrol=2, assignment/delete=6, except=0 · Call: `bool`, `cls`, `d.get`, `float`, `int`, `isinstance`, `max`, `min`
- L1584–1599 **`GejalaMurni.__init__`** · kontrol=0, assignment/delete=10, except=0 · Call: `_kclip`, `float`, `int`, `round`, `str`
- L1602–1623 **`GejalaMurni.perbarui`** · kontrol=3, assignment/delete=6, except=0 · Call: `_kclip`, `float`, `int`, `len`, `max`, `round`, `self.riwayat.append`, `self.state`
- L1625–1629 **`GejalaMurni.tekanan`** · kontrol=1, assignment/delete=0, except=0 · Call: `_kclip`, `max`
- L1631–1636 **`GejalaMurni.tandai_terklaim`** · kontrol=0, assignment/delete=1, except=0 · Call: `dict`, `float`, `int`, `round`, `str`
- L1638–1640 **`GejalaMurni.properti_terlarang`** · kontrol=1, assignment/delete=0, except=0 · Call: `hasattr`
- L1642–1655 **`GejalaMurni.state`** · kontrol=0, assignment/delete=0, except=0 · Call: `bool`, `dict`, `int`, `round`, `self.tekanan`
- L1657–1664 **`GejalaMurni.to_dict`** · kontrol=1, assignment/delete=0, except=0 · Call: `bool`, `dict`, `float`, `int`
- L1667–1679 **`GejalaMurni.from_dict`** · kontrol=3, assignment/delete=7, except=0 · Call: `bool`, `cls`, `d.get`, `dict`, `float`, `int`, `isinstance`, `max`, `str`
- L1691–1702 **`KategoriProto.__init__`** · kontrol=1, assignment/delete=9, except=0 · Call: `_kclip`, `float`, `int`, `str`
- L1704–1716 **`KategoriProto.konfirmasi`** · kontrol=2, assignment/delete=7, except=0 · Call: `_kclip`, `float`, `int`, `max`, `self.state`, `str`
- L1718–1723 **`KategoriProto.beri_nama`** · kontrol=2, assignment/delete=2, except=0 · Call: `str`
- L1725–1726 **`KategoriProto.umur`** · kontrol=0, assignment/delete=0, except=0 · Call: `int`, `max`
- L1728–1732 **`KategoriProto.layak_penuh`** · kontrol=1, assignment/delete=0, except=0 · Call: `int`, `max`, `self.umur`
- L1734–1742 **`KategoriProto.state`** · kontrol=0, assignment/delete=0, except=0 · Call: `bool`, `int`, `round`
- L1744–1751 **`KategoriProto.to_dict`** · kontrol=0, assignment/delete=0, except=0 · Call: tidak ada
- L1754–1765 **`KategoriProto.from_dict`** · kontrol=1, assignment/delete=7, except=0 · Call: `_kclip`, `cls`, `d.get`, `float`, `int`, `max`, `str`
- L1792–1813 **`Gejala.__init__`** · kontrol=0, assignment/delete=16, except=0 · Call: `int`, `max`
- L1819–1822 **`Gejala.tanda_dari`** · kontrol=0, assignment/delete=1, except=0 · Call: `format`, `repr`, `repr(nilai).encode`, `zlib.crc32`
- L1827–1862 **`Gejala.muncul`** · kontrol=5, assignment/delete=12, except=0 · Call: `GejalaMurni`, `_kclip`, `dict`, `entri.get`, `float`, `g.state`, `int`, `lama.perbarui`, `lama.state`, `round`, `self._aktif.get`, `self._catat`, `self._dikenal.get`, `self._pangkas`, `self.tanda_dari`, `str`
- L1868–1874 **`Gejala.kalimat_tanpa_nama`** · kontrol=0, assignment/delete=0, except=0 · Call: tidak ada
- L1876–1884 **`Gejala.gagal`** · kontrol=1, assignment/delete=1, except=0 · Call: `int`, `round`, `self._aktif.get`, `self._catat`, `self.kalimat_tanpa_nama`, `str`
- L1889–1907 **`Gejala.klaim`** · kontrol=3, assignment/delete=5, except=0 · Call: `dict`, `float`, `g.tandai_terklaim`, `int`, `len`, `round`, `self._aktif.get`, `self._catat`, `self._pangkas`, `self._terklaim.append`, `str`
- L1909–1913 **`Gejala.jenis_hint`** · kontrol=1, assignment/delete=1, except=0 · Call: `self._aktif.get`, `setattr`, `str`
- L1918–1985 **`Gejala.proses`** · kontrol=9, assignment/delete=21, except=0 · Call: `KategoriProto`, `dict`, `endapan.append`, `getattr`, `int`, `konsolidasi.append`, `len`, `list`, `min`, `pemudaran.append`, `proto.konfirmasi`, `proto.layak_penuh`, `proto.state`, `proto.umur`, `round`, `self._aktif.items`, `self._bekas.append`, `self._catat`, `self._proto.get`, `str`
- L1987–1990 **`Gejala.beri_nama`** · kontrol=0, assignment/delete=1, except=0 · Call: `proto.beri_nama`, `self._proto.get`, `str`
- L1992–1993 **`Gejala.bekas`** · kontrol=1, assignment/delete=0, except=0 · Call: `dict`
- L1995–1996 **`Gejala.kategori_penuh`** · kontrol=1, assignment/delete=0, except=0 · Call: `dict`, `self._penuh.values`
- L1998–1999 **`Gejala.proto`** · kontrol=1, assignment/delete=0, except=0 · Call: `p.state`, `self._proto.values`
- L2001–2002 **`Gejala.aktif`** · kontrol=1, assignment/delete=0, except=0 · Call: `g.state`, `self._aktif.values`
- L2004–2005 **`Gejala.terklaim`** · kontrol=1, assignment/delete=0, except=0 · Call: `dict`
- L2008–2014 **`Gejala._catat`** · kontrol=1, assignment/delete=1, except=0 · Call: `int`, `len`, `round`, `self._log.append`, `str`
- L2016–2029 **`Gejala._pangkas`** · kontrol=4, assignment/delete=3, except=0 · Call: `len`, `list`, `self._aktif.values`, `self._catat`, `self._dikenal.keys`, `self._dikenal.pop`, `sorted`
- L2031–2042 **`Gejala.state`** · kontrol=3, assignment/delete=1, except=0 · Call: `dict`, `g.state`, `len`, `self._aktif.values`, `self.kategori_penuh`, `self.proto`
- L2044–2058 **`Gejala.to_dict`** · kontrol=7, assignment/delete=0, except=0 · Call: `dict`, `self._aktif.items`, `self._dikenal.items`, `self._penuh.items`, `self._proto.items`, `v.to_dict`
- L2061–2084 **`Gejala.from_dict`** · kontrol=21, assignment/delete=13, except=0 · Call: `(d or {}).get`, `(d.get('aktif') or {}).items`, `(d.get('dikenal') or {}).items`, `(d.get('penuh') or {}).items`, `(d.get('proto') or {}).items`, `GejalaMurni.from_dict`, `KategoriProto.from_dict`, `cls`, `d.get`, `dict`, `int`, `isinstance`, `setelan.items`, `str`
- L2150–2160 **`Invensi.__init__`** · kontrol=0, assignment/delete=9, except=0 · Call: `int`, `random.Random`
- L2164–2166 **`Invensi._token`** · kontrol=3, assignment/delete=0, except=0 · Call: `len`, `re.findall`, `str`, `str(teks or '').lower`
- L2169–2173 **`Invensi._jaccard`** · kontrol=2, assignment/delete=1, except=0 · Call: `len`, `set`
- L2175–2176 **`Invensi._ada`** · kontrol=1, assignment/delete=0, except=0 · Call: `s.get`
- L2178–2182 **`Invensi._kebaruan`** · kontrol=2, assignment/delete=1, except=0 · Call: `_kclip`, `max`, `self._ada`, `self._jaccard`
- L2185–2188 **`Invensi._koherensi`** · kontrol=2, assignment/delete=0, except=0 · Call: `len`, `sum`
- L2191–2201 **`Invensi._utilitas`** · kontrol=7, assignment/delete=3, except=0 · Call: `(drives or {}).items`, `(emosi or {}).items`, `_kclip`, `bobot.get`, `float`, `len`, `max`, `re.findall`, `str`, `str(d).lower`, `sum`
- L2204–2208 **`Invensi._emosi_teratas`** · kontrol=1, assignment/delete=1, except=0 · Call: `emosi.items`, `float`, `max`
- L2210–2221 **`Invensi._kosakata`** · kontrol=4, assignment/delete=1, except=0 · Call: `d.get`, `k.add`, `k.update`, `self._token`, `set`, `str`, `str(a).lower`, `str(b).lower`
- L2224–2237 **`Invensi._g_negasi`** · kontrol=3, assignment/delete=3, except=0 · Call: `d.get`, `key.startswith`, `len`, `out.append`, `self._token`, `str`
- L2239–2251 **`Invensi._g_abstraksi`** · kontrol=3, assignment/delete=4, except=0 · Call: `' '.join`, `d.get`, `len`, `out.append`, `self._emosi_teratas`, `self._token`
- L2253–2273 **`Invensi._g_analogi`** · kontrol=6, assignment/delete=5, except=0 · Call: `d.get`, `float`, `frozenset`, `out.append`, `pasangan.add`, `self._token`, `set`, `sorted`, `str`, `tetangga.get`, `tetangga.setdefault`, `tetangga.setdefault(a, []).append`, `tetangga.setdefault(b, []).append`
- L2275–2295 **`Invensi._g_pengisian`** · kontrol=2, assignment/delete=4, except=0 · Call: `d.get`, `lub.get`, `out.append`, `self._token`, `str`
- L2297–2315 **`Invensi._g_inventori`** · kontrol=3, assignment/delete=5, except=0 · Call: `d.get`, `float`, `kon.get`, `out.append`, `self._token`, `sorted`, `str`
- L2317–2331 **`Invensi._g_konstruksi`** · kontrol=5, assignment/delete=9, except=0 · Call: `' → '.join`, `d.get`, `len`, `list`, `map`, `min`, `out.append`, `self._token`, `self.rng.sample`, `str`
- L2333–2349 **`Invensi._g_pengelompokan`** · kontrol=6, assignment/delete=8, except=0 · Call: `', '.join`, `d.get`, `len`, `list`, `map`, `out.append`, `range`, `self._token`, `set`, `sorted`, `str`, `tetangga.get`, `tetangga.keys`, `tetangga.setdefault`, `tetangga.setdefault(a, set()).add`, `tetangga.setdefault(b, set()).add`
- L2352–2412 **`Invensi.lahirkan`** · kontrol=16, assignment/delete=22, except=1 · Call: `dict.fromkeys`, `digest.get`, `dinilai.append`, `dinilai.sort`, `diterima.append`, `frozenset`, `gen`, `int`, `kandidat.extend`, `len`, `list`, `per.keys`, `per.setdefault`, `per.setdefault(s['jenis'], []).append`, `round`, `self._kebaruan`, `self._koherensi`, `self._kosakata`, `self._utilitas`, `self.lahir.append`, `self.riwayat_usul.append`, `set`, `sorted`, `tanda.add`
- L2414–2424 **`Invensi.kristal`** · kontrol=4, assignment/delete=3, except=0 · Call: `int`, `naik.append`, `s.get`
- L2426–2430 **`Invensi.gugur`** · kontrol=3, assignment/delete=1, except=0 · Call: `int`, `s.get`
- L2432–2445 **`Invensi.set_knob`** · kontrol=6, assignment/delete=4, except=1 · Call: `_kclip`, `float`, `int`, `max`
- L2448–2453 **`Invensi.state`** · kontrol=4, assignment/delete=2, except=0 · Call: `len`, `s.get`, `sum`
- L2455–2459 **`Invensi.ringkas`** · kontrol=3, assignment/delete=0, except=0 · Call: `len`, `s.get`, `sum`
- L2461–2463 **`Invensi.to_dict`** · kontrol=2, assignment/delete=0, except=0 · Call: `dict`, `list`
- L2466–2473 **`Invensi.from_dict`** · kontrol=4, assignment/delete=4, except=0 · Call: `cls`, `d.get`, `dict`, `int`, `list`
- L2511–2516 **`ModelKausal.__init__`** · kontrol=0, assignment/delete=5, except=0 · Call: `int`, `random.Random`
- L2520–2522 **`ModelKausal._token`** · kontrol=3, assignment/delete=0, except=0 · Call: `len`, `re.findall`, `str`, `str(teks or '').lower`
- L2525–2533 **`ModelKausal._jenis`** · kontrol=5, assignment/delete=0, except=0 · Call: `a.startswith`, `b.startswith`
- L2535–2547 **`ModelKausal._tepi`** · kontrol=3, assignment/delete=8, except=0 · Call: `_kclip`, `float`, `self.keluar.setdefault`, `self.masuk.setdefault`, `self.tepi.get`
- L2549–2557 **`ModelKausal._pangkas`** · kontrol=2, assignment/delete=1, except=0 · Call: `len`, `self.keluar.get`, `self.keluar.get(a, {}).pop`, `self.masuk.get`, `self.masuk.get(b, {}).pop`, `self.tepi.items`, `self.tepi.pop`, `sorted`
- L2560–2565 **`ModelKausal.pelajari`** · kontrol=2, assignment/delete=0, except=0 · Call: `self._pangkas`, `self._pelajari_satu`, `self.ringkas`
- L2567–2587 **`ModelKausal._pelajari_satu`** · kontrol=12, assignment/delete=8, except=0 · Call: `_kclip`, `abs`, `deltas.items`, `dict.fromkeys`, `ep.get`, `float`, `list`, `self._tepi`, `self._token`, `str`, `str(ep.get('action') or '').strip`, `str(ep.get('action') or '').strip().lower`, `str(ep.get('label') or '').strip`
- L2590–2603 **`ModelKausal._node`** · kontrol=9, assignment/delete=3, except=0 · Call: `self._token`, `str`, `str(target or '').strip`, `str(target or '').strip().lower`
- L2605–2612 **`ModelKausal._sebab`** · kontrol=2, assignment/delete=2, except=0 · Call: `cand.append`, `cand.sort`, `self._jenis`, `self.masuk.get`
- L2615–2624 **`ModelKausal._narasi`** · kontrol=4, assignment/delete=0, except=0 · Call: `node.startswith`
- L2626–2646 **`ModelKausal.jelaskan`** · kontrol=6, assignment/delete=7, except=0 · Call: `' karena '.join`, `int`, `max`, `range`, `rantai.append`, `round`, `self._jenis`, `self._narasi`, `self._node`, `self._sebab`, `str`
- L2648–2669 **`ModelKausal.counterfactual`** · kontrol=5, assignment/delete=7, except=0 · Call: `b.startswith`, `max`, `round`, `self._jenis`, `self._mekanisme_dorong`, `self._narasi`, `self._token`, `self.keluar.get`, `self.tepi.get`, `self.tepi.get(('s:' + s, a_node), {}).get`, `sorted`, `str`, `str(aksi_alt).strip`, `str(aksi_alt).strip().lower`
- L2671–2676 **`ModelKausal._mekanisme_dorong`** · kontrol=1, assignment/delete=1, except=0 · Call: `d.startswith`, `self._narasi`, `self.keluar.get`, `sorted`
- L2678–2681 **`ModelKausal._aksi_ke`** · kontrol=1, assignment/delete=0, except=0 · Call: `self._jenis`, `self.masuk.get`
- L2683–2717 **`ModelKausal.blame`** · kontrol=4, assignment/delete=15, except=0 · Call: `_kclip`, `max`, `round`, `self._aksi_ke`, `self._jenis`, `self._token`, `self.tepi.get`, `self.tepi.get(('s:' + s, h_node), {}).get`, `self.tepi.get((a_node, h_node), {}).get`, `str`, `str(aksi).strip`, `str(aksi).strip().lower`, `str(hasil_label).strip`, `str(hasil_label).strip().lower`, `sum`
- L2719–2741 **`ModelKausal.mekanisme`** · kontrol=8, assignment/delete=6, except=0 · Call: `' → '.join`, `antrian.append`, `antrian.pop`, `jalur.append`, `jalur.reverse`, `len`, `self._narasi`, `self._node`, `self.keluar.get`
- L2743–2754 **`ModelKausal.keyakinan`** · kontrol=1, assignment/delete=4, except=0 · Call: `_kclip`, `int`, `round`, `self._jenis`, `self._node`, `self.tepi.get`
- L2757–2765 **`ModelKausal.state`** · kontrol=2, assignment/delete=3, except=0 · Call: `int`, `len`, `round`, `self._jenis`, `self.tepi.items`, `sorted`
- L2767–2768 **`ModelKausal.ringkas`** · kontrol=0, assignment/delete=0, except=0 · Call: `len`, `set`
- L2770–2772 **`ModelKausal.to_dict`** · kontrol=1, assignment/delete=0, except=0 · Call: `dict`, `self.tepi.items`
- L2775–2787 **`ModelKausal.from_dict`** · kontrol=6, assignment/delete=6, except=0 · Call: `(d.get('tepi', {}) or {}).items`, `cls`, `d.get`, `float`, `int`, `kunci.partition`, `m.keluar.setdefault`, `m.masuk.setdefault`, `rec.get`
- L2812–2816 **`Perencana.__init__`** · kontrol=0, assignment/delete=4, except=0 · Call: `int`, `random.Random`
- L2820–2823 **`Perencana._fakta`** · kontrol=2, assignment/delete=2, except=0 · Call: `node.split`, `set`
- L2825–2831 **`Perencana._aksi_capai`** · kontrol=1, assignment/delete=1, except=0 · Call: `domain._jenis`, `domain.masuk.get`, `keluar.sort`
- L2833–2835 **`Perencana._pemicu`** · kontrol=1, assignment/delete=0, except=0 · Call: `domain._jenis`, `domain.masuk.get`
- L2838–2873 **`Perencana._mundur`** · kontrol=10, assignment/delete=7, except=0 · Call: `all`, `domain._node`, `pra_rencana.append`, `round`, `s.split`, `self._aksi_capai`, `self._fakta`, `self._mundur`, `self._outcome_penutup`, `self._pemicu`
- L2875–2887 **`Perencana._outcome_penutup`** · kontrol=6, assignment/delete=6, except=0 · Call: `h[2:].lower`, `len`, `n.startswith`, `re.findall`, `self._aksi_capai`, `set`, `sorted`, `t.split`, `t.split(':', 1)[-1].lower`
- L2890–2918 **`Perencana.maju`** · kontrol=12, assignment/delete=7, except=0 · Call: `a.startswith`, `all`, `bisa.append`, `bisa.sort`, `dilihat.add`, `domain._jenis`, `domain._node`, `domain.keluar.get`, `langkah.append`, `len`, `punya.add`, `range`, `self._fakta`, `self._pemicu`, `set`, `sorted`
- L2921–2938 **`Perencana._kompleksitas`** · kontrol=9, assignment/delete=5, except=0 · Call: `_kclip`, `baru.add`, `domain._jenis`, `domain._node`, `domain.keluar.get`, `domain.masuk.get`, `len`, `list`, `range`, `set`
- L2940–2956 **`Perencana.rencanakan_rencana`** · kontrol=0, assignment/delete=7, except=0 · Call: `round`, `self._buntu`, `self._kompleksitas`, `self.maju`, `self.rancang`, `uji.get`
- L2959–2972 **`Perencana.rancang`** · kontrol=1, assignment/delete=5, except=0 · Call: `frozenset`, `len`, `self._kedalaman`, `self._mundur`, `self.jejak_rencana.append`, `str`
- L2974–2977 **`Perencana._kedalaman`** · kontrol=2, assignment/delete=0, except=0 · Call: `max`, `node.get`, `self._kedalaman`
- L2979–2985 **`Perencana._buntu`** · kontrol=2, assignment/delete=1, except=0 · Call: `keluar.append`, `keluar.extend`, `node.get`, `self._buntu`, `self._buntu_label`
- L2988–2989 **`Perencana._buntu_label`** · kontrol=0, assignment/delete=0, except=0 · Call: `node.get`
- L2991–3002 **`Perencana.langkah`** · kontrol=6, assignment/delete=2, except=0 · Call: `(self.rencana_aktif or {}).get`, `keluar.append`, `keluar.extend`, `node.get`, `self.langkah`
- L3004–3030 **`Perencana.narasi`** · kontrol=8, assignment/delete=12, except=0 · Call: `' '.join`, `(self.rencana_aktif or {}).get`, `domain._narasi`, `node.get`, `self.narasi`
- L3033–3039 **`Perencana.state`** · kontrol=1, assignment/delete=1, except=0 · Call: `aktif.get`, `len`, `self.langkah`
- L3041–3043 **`Perencana.ringkas`** · kontrol=0, assignment/delete=0, except=0 · Call: `len`
- L3045–3047 **`Perencana.to_dict`** · kontrol=0, assignment/delete=0, except=0 · Call: `list`
- L3050–3057 **`Perencana.from_dict`** · kontrol=2, assignment/delete=4, except=0 · Call: `cls`, `d.get`, `int`, `list`
- L3066–3087 **`Organik.__init__`** · kontrol=0, assignment/delete=17, except=0 · Call: `Apersepsi`, `BatasIdentitas`, `DetakInternal`, `Gejala`, `Intrusi`, `Invensi`, `LapisanParalel`, `LukaDomain`, `ModelKausal`, `PenolakanTutur`, `Perencana`, `Residu`, `TopologiSlot`, `TubuhSumber`, `Vacancy`, `WaktuHeterogen`, `int`, `random.Random`
- L3090–3106 **`Organik.ringkas`** · kontrol=0, assignment/delete=0, except=0 · Call: `len`, `round`, `self.detak.state`, `self.gejala.state`, `self.identitas.state`, `self.intrusi.state`, `self.invensi.state`, `self.kausal.state`, `self.luka.ringkas`, `self.paralel.state`, `self.perencana.state`, `self.residu.state`, `self.topologi.kosong`, `self.topologi.semua`, `self.tutur.riwayat`, `self.vacancy.state`, `self.waktu.ringkas`
- L3108–3126 **`Organik.to_dict`** · kontrol=1, assignment/delete=1, except=0 · Call: `int`, `self.apersepsi.to_dict`, `self.detak.to_dict`, `self.gejala.to_dict`, `self.identitas.to_dict`, `self.intrusi.to_dict`, `self.invensi.to_dict`, `self.kausal.to_dict`, `self.luka.to_dict`, `self.paralel.to_dict`, `self.perencana.to_dict`, `self.residu.to_dict`, `self.rng.getstate`, `self.topologi.to_dict`, `self.tubuh.to_dict`, `self.tutur.to_dict`, `self.vacancy.to_dict`, `self.waktu.to_dict`
- L3129–3154 **`Organik.from_dict`** · kontrol=5, assignment/delete=18, except=1 · Call: `Apersepsi.from_dict`, `BatasIdentitas.from_dict`, `DetakInternal.from_dict`, `Gejala.from_dict`, `Intrusi.from_dict`, `Invensi.from_dict`, `LapisanParalel.from_dict`, `LukaDomain.from_dict`, `ModelKausal.from_dict`, `PenolakanTutur.from_dict`, `Perencana.from_dict`, `Residu.from_dict`, `TopologiSlot.from_dict`, `TubuhSumber.from_dict`, `Vacancy.from_dict`, `WaktuHeterogen.from_dict`, `cls`, `d.get`, `int`, `isinstance`, `len`, `o.rng.setstate`, `tuple`

## `pycos/memori/__init__.py`

SHA-256: `61395c77239e3596a1edb734ce12d62f501f69404bb3a90c8d56edefb18016d8`

37 baris; 0 kelas; 2 fungsi/metode termasuk nested.

Kelas: tidak ada.
Handler luas: tidak ada.

Impor (termasuk lazy/TYPE_CHECKING): `from .jejak_prediksi import JejakPrediksi`; `from __future__ import annotations`; `from importlib import import_module`; `from typing import TYPE_CHECKING, Any, Dict, List`.

- L25–33 **`__getattr__`** · kontrol=1, assignment/delete=3, except=0 · Call: `'paket {!r} tidak punya atribut {!r}'.format`, `'{}.{}'.format`, `AttributeError`, `_SUBMODUL.get`, `getattr`, `globals`, `import_module`
- L36–37 **`__dir__`** · kontrol=0, assignment/delete=0, except=0 · Call: `globals`, `set`, `sorted`

## `pycos/memori/jejak_prediksi.py`

SHA-256: `d5b60112b9b14550c9f8eb397e7d465714605dc6a4f04b1f124d1d1f6dc1af13`

2850 baris; 1 kelas; 99 fungsi/metode termasuk nested.

Kelas: `JejakPrediksi` L329.
Handler luas: 315, 2550, 2573, 2592, 2647, 2725, 893, 2206, 426, 1141, 1501, 1521, 1534, 1613, 1704, 1824, 1916, 2187, 2195, 2821, 1148, 1371, 1728, 1790, 1802, 1702, 1726.

Impor (termasuk lazy/TYPE_CHECKING): `from __future__ import annotations`; `from pycos.dukungan import konstanta as _konstanta_drive`; `from pycos.dukungan.numerik import jepit, jepit_01, jepit_drive`; `from pycos.dukungan.patching import install_method, install_methods, optional_module, wrap_method`; `from pycos.dukungan.persistensi import muat_json`; `from pycos.dukungan.persistensi import simpan_json`; `from pycos.dukungan.validasi_state import validasi_state`; `from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Set, Tuple`; `import heapq`; `import json`; `import math`; `import os as _os`; `import random`; `import re`; `import sys as _sys`; `import time`; `import zlib`.

- L146–148 **`_clip`** · kontrol=0, assignment/delete=0, except=0 · Call: `jepit`
- L151–154 **`_read`** · kontrol=1, assignment/delete=0, except=0 · Call: `getattr`, `isinstance`, `obj.get`
- L157–174 **`_context_text`** · kontrol=9, assignment/delete=3, except=0 · Call: `' '.join`, `isinstance`, `parts.extend`, `sorted`, `str`
- L177–184 **`_action_family`** · kontrol=3, assignment/delete=1, except=0 · Call: `_WORD_RE.findall`, `set`, `str`, `str(text or '').lower`, `words.intersection`
- L187–198 **`_features`** · kontrol=6, assignment/delete=4, except=0 · Call: `_ALIASES.get`, `_WORD_RE.findall`, `_action_family`, `len`, `out.add`, `set`, `str`, `str(text or '').lower`
- L201–215 **`_similarity`** · kontrol=3, assignment/delete=4, except=0 · Call: `jepit_01`, `left.intersection`, `left.union`, `len`
- L218–273 **`_normalise_outcome`** · kontrol=18, assignment/delete=25, except=0 · Call: `_clip`, `_read`, `abs`, `bool`, `deltas.get`, `deltas.values`, `isinstance`, `len`, `max`, `raw_deltas.items`, `str`, `sum`
- L276–301 **`_subjective_time_snapshot`** · kontrol=6, assignment/delete=10, except=2 · Call: `callable`, `float`, `fn`, `getattr`, `int`, `isinstance`, `jepit`, `max`, `profile.get`, `str`
- L304–320 **`_attention_fatigue`** · kontrol=5, assignment/delete=2, except=2 · Call: `float`, `getattr`, `isinstance`, `jepit_01`, `ks.attention_state`, `state.get`
- L323–326 **`_batas_retrieval`** · kontrol=3, assignment/delete=0, except=0 · Call: `ValueError`, `isinstance`
- L344–427 **`JejakPrediksi.__init__`** · kontrol=3, assignment/delete=47, except=1 · Call: `_pres.set_jejak`, `bool`, `float`, `getattr`, `int`, `jepit`, `jepit_01`, `max`, `random.Random`, `range`, `self._normalise_weights`, `tuple`
- L430–450 **`JejakPrediksi._normalise_weights`** · kontrol=5, assignment/delete=9, except=1 · Call: `dict`, `float`, `max`, `min`
- L453–454 **`JejakPrediksi.size`** · kontrol=0, assignment/delete=0, except=0 · Call: `len`
- L457–459 **`JejakPrediksi.experiences`** · kontrol=1, assignment/delete=0, except=0 · Call: `self._episode_copy`
- L462–472 **`JejakPrediksi._memory_signature`** · kontrol=2, assignment/delete=2, except=0 · Call: `'{:08x}'.format`, `'|'.join`, `_features`, `bahan.encode`, `sorted`, `str`, `zlib.crc32`
- L475–502 **`JejakPrediksi._episode_copy`** · kontrol=2, assignment/delete=0, except=0 · Call: `(ep.get('drive_deltas') or {}).get`, `ep.get`, `float`, `int`, `str`
- L504–519 **`JejakPrediksi._current_tick`** · kontrol=4, assignment/delete=4, except=2 · Call: `getattr`, `int`, `max`
- L521–565 **`JejakPrediksi._build_episode`** · kontrol=2, assignment/delete=5, except=1 · Call: `_read`, `_subjective_time_snapshot`, `dict`, `float`, `jepit`, `max`, `self._memory_signature`, `str`, `time_profile.get`
- L567–625 **`JejakPrediksi.record_experience`** · kontrol=7, assignment/delete=11, except=0 · Call: `ValueError`, `_context_text`, `_context_text(context).strip`, `_normalise_outcome`, `bool`, `int`, `self._build_episode`, `self._current_tick`, `self._episodes.append`, `self._evict_overflow`, `self._index_episode`, `self._matikan_memori_tua`, `self._sync_naluri`, `str`, `str(action or '').strip`, `str(stimulus or '').strip`
- L630–643 **`JejakPrediksi._kuburkan`** · kontrol=3, assignment/delete=4, except=0 · Call: `(lama or {}).get`, `episode.get`, `int`, `self._memory_signature`, `self._nekropolis.get`, `str`
- L645–662 **`JejakPrediksi._matikan_memori_tua`** · kontrol=6, assignment/delete=5, except=0 · Call: `ep.get`, `float`, `int`, `len`, `max`, `self._deindex_episode`, `self._kuburkan`
- L664–667 **`JejakPrediksi.nekropolis_state`** · kontrol=1, assignment/delete=0, except=0 · Call: `dict`, `len`, `self._nekropolis.values`
- L669–675 **`JejakPrediksi.enable_recall_rewrite`** · kontrol=1, assignment/delete=2, except=0 · Call: `bool`, `float`, `jepit_01`
- L677–694 **`JejakPrediksi.forget`** · kontrol=4, assignment/delete=5, except=0 · Call: `ep.get`, `int`, `keep.append`, `len`, `max`, `removed.append`, `self._current_tick`, `self._deindex_episode`, `self._kuburkan`
- L696–700 **`JejakPrediksi._recency`** · kontrol=1, assignment/delete=1, except=0 · Call: `episode.get`, `int`, `max`
- L702–712 **`JejakPrediksi._retention_score`** · kontrol=2, assignment/delete=6, except=0 · Call: `(episode.get('drive_deltas') or {}).values`, `abs`, `episode.get`, `float`, `int`, `math.log1p`, `max`, `min`
- L714–720 **`JejakPrediksi._evict_overflow`** · kontrol=1, assignment/delete=2, except=0 · Call: `len`, `min`, `range`, `self._deindex_episode`, `self._episodes.pop`, `self._kuburkan`, `self._retention_score`
- L723–735 **`JejakPrediksi._minhash`** · kontrol=3, assignment/delete=7, except=0 · Call: `enumerate`, `len`, `str`, `str(token).encode`, `tuple`, `zlib.crc32`
- L738–743 **`JejakPrediksi._minhash_sim`** · kontrol=3, assignment/delete=1, except=0 · Call: `len`, `sum`, `zip`
- L745–756 **`JejakPrediksi._index_episode`** · kontrol=2, assignment/delete=5, except=0 · Call: `_features`, `dict`, `episode.get`, `int`, `isinstance`, `self._minhash`, `self._token_index.setdefault`, `self._token_index.setdefault(tok, set()).add`, `set`, `str`
- L758–772 **`JejakPrediksi._deindex_episode`** · kontrol=4, assignment/delete=4, except=0 · Call: `_features`, `episode.get`, `int`, `s.discard`, `self._ep_by_id.pop`, `self._feature_cache.pop`, `self._minhash_sig.pop`, `self._token_index.get`, `self._token_index.pop`, `str`
- L774–781 **`JejakPrediksi._rebuild_index`** · kontrol=1, assignment/delete=4, except=0 · Call: `self._index_episode`
- L783–792 **`JejakPrediksi._candidates`** · kontrol=4, assignment/delete=1, except=0 · Call: `ids.update`, `list`, `self._token_index.get`, `set`
- L794–798 **`JejakPrediksi.set_retrieve_mode`** · kontrol=0, assignment/delete=2, except=0 · Call: `str`, `str(mode).lower`, `str(mode).lower().strip`
- L800–813 **`JejakPrediksi.performance_report`** · kontrol=0, assignment/delete=1, except=0 · Call: `dict`, `len`, `max`, `round`
- L816–874 **`JejakPrediksi.consolidate_memory`** · kontrol=16, assignment/delete=19, except=0 · Call: `(e.get('drive_deltas') or {}).get`, `_action_family`, `e.get`, `ep.get`, `float`, `int`, `jepit_01`, `jepit_drive`, `keep.append`, `len`, `max`, `min`, `rep.get`, `self._current_tick`, `self._evict_overflow`, `self._memory_signature`, `self._rebuild_index`, `str`, `sum`, `summaries.append`, `trivial.items`, `trivial.setdefault`, `trivial.setdefault(key, []).append`
- L876–939 **`JejakPrediksi._rewrite_episode_at_recall`** · kontrol=14, assignment/delete=30, except=1 · Call: `' [recall:{}]'.format`, `(label + ' [recall:{}]'.format(warna)).strip`, `_clip`, `dd.get`, `dd.values`, `dict`, `emosi.get`, `ep.get`, `float`, `getattr`, `int`, `jepit_01`, `jepit_drive`, `len`, `max`, `re.sub`, `re.sub('\\s*\\[recall:[^\\]]+\\]\\s*$', '', str(ep.get('label', ''))).strip`, `round`, `self._recall_rewrite_log.append`, `self.naluri.mood`, `str`, `sum`
- L941–1027 **`JejakPrediksi._retrieve`** · kontrol=18, assignment/delete=42, except=0 · Call: `_attention_fatigue`, `_batas_retrieval`, `_context_text`, `_features`, `_similarity`, `_waktu_umur_subjektif`, `any`, `bool`, `dict`, `ep.get`, `float`, `heapq.nsmallest`, `hits.append`, `hits.sort`, `int`, `len`, `max`, `min`, `self._candidates`, `self._feature_cache.get`, `self._matikan_memori_tua`, `self._memory_signature`, `self._minhash`, `self._minhash_sig.get`, `self._minhash_sim`, `self._recency`, `self._rewrite_episode_at_recall`, `str`, `time.perf_counter`
- L1029–1064 **`JejakPrediksi._retrieve_action`** · kontrol=9, assignment/delete=13, except=0 · Call: `_action_family`, `_features`, `_similarity`, `dict`, `ep.get`, `float`, `hits.append`, `hits.sort`, `max`, `self._action_feature_cache.get`, `str`, `x.get`
- L1067–1124 **`JejakPrediksi._aggregate`** · kontrol=14, assignment/delete=16, except=0 · Call: `(h.get('drive_deltas') or {}).get`, `JejakPrediksi._aggregate`, `_clip`, `drive_deltas.items`, `float`, `h.get`, `int`, `jepit`, `len`, `matches.append`, `math.exp`, `math.sqrt`, `max`, `min`, `round`, `str`, `sum`
- L1126–1169 **`JejakPrediksi._instinct_prior`** · kontrol=16, assignment/delete=21, except=2 · Call: `_clip`, `abs`, `bool`, `callable`, `deltas.get`, `deltas.values`, `float`, `getattr`, `impact_fn`, `isinstance`, `max`, `min`, `perception`, `result.get`, `sum`, `weights.get`
- L1172–1191 **`JejakPrediksi._environment_prior`** · kontrol=6, assignment/delete=5, except=0 · Call: `_clip`, `_normalise_outcome`, `_read`, `abs`, `any`, `isinstance`, `parsed['drive_deltas'].values`
- L1193–1271 **`JejakPrediksi._blend`** · kontrol=12, assignment/delete=29, except=0 · Call: `(instinct.get('drive_deltas') or {}).get`, `(memory.get('drive_deltas') or {}).get`, `_clip`, `abs`, `environment.get`, `ext_deltas.get`, `final_deltas.get`, `float`, `instinct.get`, `internal_deltas.items`, `max`, `memory.get`, `min`, `round`
- L1274–1288 **`JejakPrediksi._recommendation`** · kontrol=6, assignment/delete=2, except=0 · Call: `float`, `situation.get`
- L1290–1454 **`JejakPrediksi.predict`** · kontrol=25, assignment/delete=27, except=1 · Call: `' '.join`, `' '.join((x for x in (stimulus, context_str) if x)).strip`, `ValueError`, `_context_text`, `bool`, `callable`, `dict`, `float`, `getattr`, `len`, `note`, `round`, `self._aggregate`, `self._blend`, `self._current_tick`, `self._environment_prior`, `self._instinct_prior`, `self._recommendation`, `self._retrieve`, `self._retrieve_action`, `self.weights.items`, `str`, `str(stimulus or '').strip`
- L1456–1648 **`JejakPrediksi.rank_actions`** · kontrol=31, assignment/delete=64, except=5 · Call: `_batas_retrieval`, `_clip`, `_context_text`, `action_forecast.get`, `any`, `base_result.get`, `best['candidate'].get`, `bool`, `budgets.append`, `callable`, `candidate.get`, `choose`, `deficit_fn`, `dict`, `drive_weights.get`, `effects.get`, `enumerate`, `float`, `getattr`, `h.get`, `int`, `jepit`, `jepit_01`, `len`, `list`, `math.log1p`, `math.sqrt`, `max`, `min`, `pred.get`, `recorder`, `remember`, `round`, `scored.append`, `scored.sort`, `self._current_tick`, `self._pending_shadows.pop`, `self._pending_shadows[k].get`, `self._retrieve`, `self._retrieve_action`, `self.predict`, `str`, `sum`
- L1650–1814 **`JejakPrediksi.reinforce`** · kontrol=34, assignment/delete=41, except=8 · Call: `_normalise_outcome`, `abs`, `alt_forecast.get`, `alt_prediction.get`, `assigner`, `bool`, `callable`, `counterfactuals.append`, `decision.get`, `dict`, `float`, `forecast.get`, `getattr`, `int`, `isinstance`, `item.get`, `len`, `list`, `observer`, `pending.get`, `prediction.get`, `recorder`, `remember_context`, `round`, `selected.get`, `self._counterfactual_log.append`, `self._current_tick`, `self._pending_shadows.pop`, `self._sync_naluri`, `self.predict`, `self.record_experience`, `str`
- L1816–1825 **`JejakPrediksi._sync_naluri`** · kontrol=4, assignment/delete=2, except=1 · Call: `_normalise_outcome`, `abs`, `any`, `callable`, `dict`, `fn`, `getattr`, `parsed['drive_deltas'].values`
- L1832–1836 **`JejakPrediksi._episode_importance`** · kontrol=2, assignment/delete=3, except=0 · Call: `abs`, `deltas.values`, `ep.get`, `float`, `int`, `math.log1p`, `max`
- L1838–1858 **`JejakPrediksi.autobiographical_timeline`** · kontrol=2, assignment/delete=3, except=0 · Call: `e.get`, `ep.get`, `float`, `int`, `max`, `out.append`, `pilih.sort`, `round`, `self._episode_importance`, `str`
- L1860–1870 **`JejakPrediksi.open_chapter`** · kontrol=2, assignment/delete=4, except=0 · Call: `dict`, `len`, `self._chapters.append`, `self._current_tick`, `str`
- L1872–1877 **`JejakPrediksi.life_chapters`** · kontrol=2, assignment/delete=1, except=0 · Call: `dict`, `out.append`
- L1879–1889 **`JejakPrediksi.close_chapter`** · kontrol=3, assignment/delete=4, except=0 · Call: `dict`, `self._chapters.append`, `self._current_tick`, `self.open_chapter`, `str`
- L1891–1940 **`JejakPrediksi.future_simulation`** · kontrol=9, assignment/delete=22, except=1 · Call: `(hasil_rank.get('situation_forecast') or {}).get`, `float`, `forecast.get`, `hasil_rank.get`, `len`, `list`, `max`, `min`, `pred.get`, `round`, `self._counterfactual_emotions.get`, `self._current_tick`, `self._future_sim_log.append`, `self.predict`, `self.rank_actions`, `str`, `str(a).strip`, `top.get`
- L1942–1966 **`JejakPrediksi.register_counterfactual`** · kontrol=7, assignment/delete=9, except=0 · Call: `abs`, `emosi.items`, `float`, `len`, `max`, `min`, `round`, `self._counterfactual_emotions.get`, `self._counterfactual_log.append`, `self._current_tick`, `str`
- L1968–1977 **`JejakPrediksi.counterfactual_emotions`** · kontrol=4, assignment/delete=2, except=0 · Call: `em.items`, `entry.get`, `float`, `max`, `round`, `self._counterfactual_emotions.get`, `self._counterfactual_emotions.items`
- L1979–1999 **`JejakPrediksi.confabulate`** · kontrol=3, assignment/delete=4, except=0 · Call: `len`, `self._confabulations.append`, `self._current_tick`, `self._rng.choice`, `str`
- L2001–2010 **`JejakPrediksi.autobiography_state`** · kontrol=1, assignment/delete=0, except=0 · Call: `c.get`, `len`, `self.autobiographical_timeline`, `self.counterfactual_emotions`, `self.life_chapters`
- L2069–2086 **`JejakPrediksi.observe_actor`** · kontrol=2, assignment/delete=5, except=0 · Call: `dict`, `len`, `self._actor_id`, `self._actor_log.append`, `self._current_tick`, `self._normalise_actor_action`, `self.detect_patterns`
- L2089–2090 **`JejakPrediksi._actor_id`** · kontrol=0, assignment/delete=0, except=0 · Call: `getattr`, `str`
- L2105–2107 **`JejakPrediksi._normalise_actor_action`** · kontrol=0, assignment/delete=1, except=0 · Call: `self._AKSI_ALIAS.get`, `str`, `str(action).strip`, `str(action).strip().lower`
- L2109–2110 **`JejakPrediksi._pattern_key`** · kontrol=0, assignment/delete=0, except=0 · Call: tidak ada
- L2112–2173 **`JejakPrediksi.detect_patterns`** · kontrol=17, assignment/delete=26, except=0 · Call: `by_actor.items`, `by_actor.setdefault`, `by_actor.setdefault(e['actor'], []).append`, `float`, `hasil.append`, `int`, `len`, `max`, `min`, `range`, `round`, `self._PATTERN_RULES.items`, `self._actor_id`, `self._apply_pattern_effect`, `self._current_tick`, `self._pattern_key`, `self._patterns.get`, `slot.get`, `sum`
- L2175–2208 **`JejakPrediksi._apply_pattern_effect`** · kontrol=11, assignment/delete=7, except=3 · Call: `aturan.get`, `float`, `getattr`, `hasattr`, `ks._refresh_identity`, `ks.add_boundary`, `self.naluri.berinteraksi`
- L2210–2217 **`JejakPrediksi.pattern_report`** · kontrol=2, assignment/delete=2, except=0 · Call: `dict`, `float`, `items.sort`, `len`, `self._actor_id`, `self._patterns.values`, `v.get`, `x.get`
- L2219–2230 **`JejakPrediksi.is_pattern`** · kontrol=5, assignment/delete=1, except=0 · Call: `float`, `self._actor_id`, `self._patterns.items`, `slot.get`
- L2232–2248 **`JejakPrediksi.forget_patterns`** · kontrol=7, assignment/delete=3, except=0 · Call: `buang.append`, `int`, `len`, `self._actor_id`, `self._current_tick`, `self._patterns.items`, `self._patterns.pop`, `slot.get`
- L2250–2288 **`JejakPrediksi.to_dict`** · kontrol=11, assignment/delete=0, except=0 · Call: `dict`, `float`, `self._counterfactual_emotions.items`, `self._episode_copy`, `self._nekropolis.items`, `self._patterns.items`, `self._pending_shadows.items`, `str`
- L2291–2388 **`JejakPrediksi.from_dict`** · kontrol=31, assignment/delete=23, except=1 · Call: `(data.get('counterfactual_emotions') or {}).items`, `(data.get('nekropolis') or {}).items`, `(data.get('patterns') or {}).items`, `(data.get('pending_shadows') or {}).items`, `_normalise_outcome`, `bool`, `cls`, `config.get`, `data.get`, `dict`, `float`, `int`, `isinstance`, `jepit`, `list`, `max`, `obj._episodes.append`, `obj._evict_overflow`, `obj._memory_signature`, `obj._pending_shadows.items`, `obj._rebuild_index`, `raw.get`, `str`, `v.get`, `validasi_state`
- L2390–2392 **`JejakPrediksi.to_json`** · kontrol=0, assignment/delete=0, except=0 · Call: `json.dumps`, `kwargs.setdefault`, `self.to_dict`
- L2395–2396 **`JejakPrediksi.from_json`** · kontrol=0, assignment/delete=0, except=0 · Call: `cls.from_dict`, `json.loads`
- L2398–2400 **`JejakPrediksi.save`** · kontrol=0, assignment/delete=0, except=0 · Call: `self.to_dict`, `simpan_json`
- L2403–2405 **`JejakPrediksi.load`** · kontrol=0, assignment/delete=0, except=0 · Call: `cls.from_dict`, `muat_json`
- L2408–2437 **`demo`** · kontrol=0, assignment/delete=3, except=0 · Call: `JejakPrediksi`, `jejak.predict`, `jejak.rank_actions`, `jejak.record_experience`, `print`
- L2459–2468 **`_jejak_waktu`** · kontrol=2, assignment/delete=4, except=0 · Call: `getattr`, `modul.WaktuHeterogen`, `optional_module`
- L2471–2473 **`half_life_episode`** · kontrol=0, assignment/delete=1, except=0 · Call: `_jejak_waktu`, `w.half_life`
- L2476–2479 **`ingat_kembali`** · kontrol=0, assignment/delete=1, except=0 · Call: `_jejak_waktu`, `w.diingat`
- L2482–2485 **`koreksi_salah`** · kontrol=0, assignment/delete=1, except=0 · Call: `_jejak_waktu`, `w.dikoreksi_salah`
- L2488–2490 **`waktu_state`** · kontrol=0, assignment/delete=1, except=0 · Call: `getattr`, `w.ringkas`
- L2503–2511 **`_waktu_episode_id`** · kontrol=3, assignment/delete=3, except=0 · Call: `dalam.get`, `ep.get`, `isinstance`
- L2514–2537 **`_waktu_umur_subjektif`** · kontrol=8, assignment/delete=9, except=1 · Call: `_subjective_time_snapshot`, `_subjective_time_snapshot(n).get`, `episode.get`, `float`, `getattr`, `int`, `jepit`, `max`
- L2540–2552 **`_waktu_recency`** · kontrol=4, assignment/delete=4, except=1 · Call: `_waktu_episode_id`, `_waktu_umur_subjektif`, `getattr`, `original`, `w.half_life`
- L2559–2575 **`_waktu_retention`** · kontrol=4, assignment/delete=8, except=1 · Call: `_waktu_episode_id`, `_waktu_umur_subjektif`, `float`, `getattr`, `max`, `original`, `w.half_life`
- L2582–2594 **`_waktu_retrieve`** · kontrol=5, assignment/delete=3, except=1 · Call: `_waktu_episode_id`, `getattr`, `original`, `w.diingat`
- L2601–2620 **`_jejak_waktu_ambil`** · kontrol=4, assignment/delete=6, except=1 · Call: `dict`, `float`, `getattr`, `modul.WaktuHeterogen`, `modul.WaktuHeterogen(dasar=float(getattr(self, 'half_life_ticks', 600.0))).to_dict`, `optional_module`, `w.to_dict`
- L2623–2637 **`_jejak_waktu_pasang`** · kontrol=5, assignment/delete=5, except=1 · Call: `data.pop`, `dict`, `isinstance`, `modul.WaktuHeterogen.from_dict`, `optional_module`
- L2641–2648 **`_jejak_impact`** · kontrol=5, assignment/delete=1, except=1 · Call: `(ep.get('drive_deltas') or {}).values`, `abs`, `ep.get`, `float`, `sum`
- L2651–2698 **`_reconsolidasi_otomatis`** · kontrol=15, assignment/delete=14, except=0 · Call: `_jejak_impact`, `abs`, `baru.get`, `e.get`, `ep.get`, `float`, `getattr`, `hasil.append`, `len`, `log.extend`, `next`, `round`, `set`, `str`, `str(baru.get('stimulus', '')).lower`, `str(baru.get('stimulus', '')).lower().split`, `str(ep.get('stimulus', '')).lower`, `str(ep.get('stimulus', '')).lower().split`, `w.diingat`, `w.dikoreksi_salah`
- L2701–2705 **`reconsolidasi_state`** · kontrol=2, assignment/delete=1, except=0 · Call: `dict`, `getattr`, `w.ringkas`
- L2708–2729 **`_jejak_record`** · kontrol=4, assignment/delete=4, except=1 · Call: `_jejak_waktu`, `_reconsolidasi_otomatis`, `episode.get`, `getattr`, `getattr(self, '_ep_by_id', {}).get`, `int`, `item.get`, `next`, `original`, `waktu.skala_subjektif`
- L2740–2747 **`_jejak_serialisasi`** · kontrol=2, assignment/delete=4, except=0 · Call: `_jejak_waktu_ambil`, `getattr`, `isinstance`, `mesin.to_dict`, `original`
- L2750–2766 **`_jejak_deserialisasi`** · kontrol=5, assignment/delete=5, except=1 · Call: `_jejak_waktu_pasang`, `data.get`, `isinstance`, `modul.MesinKepercayaan.from_dict`, `optional_module`, `original`
- L2780–2789 **`_jejak_mesin`** · kontrol=2, assignment/delete=4, except=0 · Call: `getattr`, `modul.MesinKepercayaan`, `optional_module`
- L2792–2794 **`_jejak_tetapkan_kepercayaan`** · kontrol=0, assignment/delete=1, except=0 · Call: `_jejak_mesin`, `float`, `m.tetapkan`
- L2797–2802 **`_jejak_perbarui_kepercayaan`** · kontrol=1, assignment/delete=1, except=0 · Call: `_jejak_mesin`, `m.perbarui`
- L2805–2807 **`_jejak_kepercayaan`** · kontrol=0, assignment/delete=1, except=0 · Call: `_jejak_mesin`, `m.kepercayaan`
- L2810–2823 **`_jejak_curiga`** · kontrol=4, assignment/delete=5, except=1 · Call: `_jejak_mesin`, `callable`, `float`, `fn`, `getattr`, `m.curiga`
- L2826–2828 **`_jejak_kepercayaan_state`** · kontrol=0, assignment/delete=1, except=0 · Call: `getattr`, `m.to_dict`
- L2831–2833 **`_jejak_pasang`** · kontrol=0, assignment/delete=0, except=0 · Call: `self._jejak_mesin`

## `pycos/refleksi/__init__.py`

SHA-256: `0b97901de944a7bcac6aba9ed11b32f748bbb8f46eb23316f06481351fce2369`

60 baris; 0 kelas; 2 fungsi/metode termasuk nested.

Kelas: tidak ada.
Handler luas: tidak ada.

Impor (termasuk lazy/TYPE_CHECKING): `from .ketidaktahuan import STATUS_PENGETAHUAN, SIKAP_KETIDAKTAHUAN, batas_pengetahuan, sikap_ketidaktahuan`; `from .nurani import NURANI_DEFAULTS, CalibrationReport, ContohLabel, DimensiSkor, Laporan, Nurani, PelacakSelaras, kappa_cohen, laporan_kalibrasi, muat_korpus, nilai_selaras, ukur_fitur, ukur_selaras`; `from __future__ import annotations`; `from importlib import import_module`; `from typing import TYPE_CHECKING, Any, Dict, List`.

- L48–56 **`__getattr__`** · kontrol=1, assignment/delete=3, except=0 · Call: `'paket {!r} tidak punya atribut {!r}'.format`, `'{}.{}'.format`, `AttributeError`, `_SUBMODUL.get`, `getattr`, `globals`, `import_module`
- L59–60 **`__dir__`** · kontrol=0, assignment/delete=0, except=0 · Call: `globals`, `set`, `sorted`

## `pycos/refleksi/ketidaktahuan.py`

SHA-256: `35e55a17bf1f01b7f96ec407252d54f93f6ba61bab9ff0fb01b86c51f823407e`

735 baris; 0 kelas; 24 fungsi/metode termasuk nested.

Kelas: tidak ada.
Handler luas: 80, 88, 239, 280, 525, 733, 101.

Impor (termasuk lazy/TYPE_CHECKING): `from __future__ import annotations`; `from collections.abc import Mapping, Sequence`; `from itertools import islice`; `from pycos.dukungan import konstanta as _konstanta_drive`; `from pycos.dukungan.numerik import jepit, jepit_01`; `from pycos.refleksi.nurani import Nurani`; `from typing import Any, Dict, List, Optional, Tuple`; `import math`; `import re`; `import zlib`.

- L72–82 **`_field`** · kontrol=3, assignment/delete=1, except=1 · Call: `instance_dict.get`, `isinstance`, `obj.get`, `object.__getattribute__`
- L85–89 **`_get`** · kontrol=1, assignment/delete=0, except=1 · Call: `isinstance`, `mapping.get`
- L92–103 **`_text`** · kontrol=4, assignment/delete=0, except=1 · Call: `isinstance`, `str`
- L106–121 **`_proposition`** · kontrol=6, assignment/delete=2, except=0 · Call: `_field`, `_get`, `_text`, `isinstance`
- L124–143 **`_unreachable`** · kontrol=6, assignment/delete=4, except=0 · Call: `_get`, `_text`, `_text(scope).strip`, `_text(scope).strip().lower`, `_text(scope).strip().lower().replace`, `isinstance`
- L146–158 **`_tokens`** · kontrol=4, assignment/delete=3, except=0 · Call: `_TOKEN_RE.findall`, `_text`, `_text(text).lower`, `len`, `out.append`, `seen.add`, `set`, `tuple`
- L161–170 **`_clip`** · kontrol=3, assignment/delete=1, except=1 · Call: `float`, `isinstance`, `jepit_01`, `math.isfinite`
- L173–179 **`_coverage`** · kontrol=2, assignment/delete=1, except=0 · Call: `_tokens`, `float`, `len`, `set`, `set(query).intersection`
- L182–189 **`_episode_coverage`** · kontrol=4, assignment/delete=2, except=0 · Call: `_EPISODIC_ALIASES.get`, `_tokens`, `canonical_query.intersection`, `float`, `len`
- L192–207 **`_wadah`** · kontrol=3, assignment/delete=4, except=0 · Call: `_clip`, `bool`, `dict`, `round`
- L210–268 **`_episodik`** · kontrol=20, assignment/delete=22, except=2 · Call: `' '.join`, `_EPISODIC_ALIASES.get`, `_clip`, `_episode_coverage`, `_field`, `_get`, `_text`, `bucket.keys`, `dict.fromkeys`, `float`, `ids.add`, `isinstance`, `islice`, `iter`, `len`, `max`, `min`, `round`, `set`, `tuple`
- L271–287 **`_affective_signature`** · kontrol=3, assignment/delete=3, except=1 · Call: `'|'.join`, `'|'.join(keywords).encode`, `Nurani.keywords`, `_AFFECTIVE_WORD_RE.findall`, `_text`, `_text(text).lower`, `set`, `sorted`, `tuple`, `zlib.crc32`
- L290–322 **`_afektif`** · kontrol=9, assignment/delete=13, except=1 · Call: `_affective_signature`, `_clip`, `_field`, `_get`, `_text`, `abs`, `float`, `isinstance`, `len`, `max`, `min`, `str`
- L325–331 **`_is_causal_edge`** · kontrol=4, assignment/delete=0, except=0 · Call: `source.startswith`, `target.startswith`
- L334–381 **`_kausal`** · kontrol=16, assignment/delete=20, except=0 · Call: `' '.join`, `_TOKEN_RE.findall`, `_clip`, `_field`, `_get`, `_is_causal_edge`, `_text`, `_text(text).lower`, `_text(text).strip`, `_text(text).strip().lower`, `dict.fromkeys`, `isinstance`, `islice`, `nodes.append`, `nodes.extend`, `pairs.extend`, `tuple`
- L384–405 **`_sosial`** · kontrol=10, assignment/delete=7, except=0 · Call: `_get`, `_text`, `_text(holder).strip`, `_tokens`, `isinstance`, `next`, `set`
- L408–427 **`_bukti_sosial`** · kontrol=4, assignment/delete=6, except=0 · Call: `_clip`, `_field`, `_get`, `_sosial`, `isinstance`, `query.get`
- L430–449 **`_sadar`** · kontrol=6, assignment/delete=9, except=0 · Call: `_clip`, `_coverage`, `_field`, `_get`, `_text`, `isinstance`, `islice`, `max`, `round`
- L452–537 **`batas_pengetahuan`** · kontrol=10, assignment/delete=23, except=2 · Call: `_afektif`, `_bukti_sosial`, `_episodik`, `_kausal`, `_proposition`, `_sadar`, `_tokens`, `_unreachable`, `_wadah`, `affective.get`, `any`, `causal.get`, `conscious.get`, `episodic.get`, `float`, `jepit_01`, `math.isfinite`, `max`, `round`, `social.get`, `tuple`, `vessels.items`, `vessels.values`
- L540–548 **`_trait`** · kontrol=4, assignment/delete=1, except=0 · Call: `_clip`, `_get`, `isinstance`
- L551–554 **`_drive_or_emotion`** · kontrol=2, assignment/delete=0, except=0 · Call: `_clip`, `_get`, `isinstance`, `max`
- L557–568 **`_internal_urgency`** · kontrol=5, assignment/delete=3, except=1 · Call: `_get`, `float`, `isinstance`, `jepit`, `math.isfinite`, `max`
- L571–584 **`_context_number`** · kontrol=5, assignment/delete=2, except=1 · Call: `_get`, `float`, `isinstance`, `jepit`, `math.isfinite`
- L587–735 **`sikap_ketidaktahuan`** · kontrol=55, assignment/delete=43, except=1 · Call: `' '.join`, `' '.join((_text(_field(npc, 'personality_name', '')), _text(_field(npc, 'personality', '')), _text(_field(npc, 'watak', '')))).lower`, `_clip`, `_context_number`, `_drive_or_emotion`, `_field`, `_get`, `_internal_urgency`, `_text`, `_text(_get(observer, 'relasi', _get(observer, 'relation', ''))).lower`, `_text(observer).lower`, `_trait`, `any`, `bool`, `explicit_traits.lower`, `float`, `isinstance`, `max`, `min`

## `pycos/refleksi/nurani.py`

SHA-256: `33ec765e82cbdfed030ddeeb226f490f066134c869a94b2042d86fb71078284f`

4179 baris; 6 kelas; 174 fungsi/metode termasuk nested.

Kelas: `CalibrationReport` L367, `Nurani` L396, `DimensiSkor` L3564, `Laporan` L3577, `PelacakSelaras` L3796, `ContohLabel` L3889.
Handler luas: 3416, 3433, 3625, 3636, 3729, 608, 643, 740, 3462, 3472, 3502, 3737, 1851, 2022.

Impor (termasuk lazy/TYPE_CHECKING): `from __future__ import annotations`; `from collections import deque`; `from dataclasses import dataclass, field`; `from itertools import combinations`; `from pycos.bahasa.teks import stem as _stem`; `from pycos.bahasa.teks import stem as _stem_p`; `from pycos.bahasa.teks import stem as _stem_pantangan`; `from pycos.bahasa.teks import tokenisasi as _tok, cakupan_negasi as _cak, stem as _stem`; `from pycos.bahasa.tutur import LeksikonCiri`; `from pycos.bahasa.tutur import analisis_teks`; `from pycos.bahasa.tutur import analisis_teks, token_dari`; `from pycos.dukungan import konstanta as _konstanta_drive`; `from pycos.dukungan.numerik import jepit, jepit_01, jepit_drive`; `from pycos.dukungan.patching import install_method, optional_module, wrap_method`; `from pycos.dukungan.sumber import jalur_leksikon`; `from pycos.dukungan.validasi_state import validasi_state`; `from pycos.inti.persona import Keadaan, Persona`; `from pycos.inti.persona import PERSONA_CONTOH, Keadaan`; `from pycos.kontrak import hanya_kunci, teks_wajib`; `from pycos.mandiri.kognisi_lanjut import GrafAsosiasi`; `from pycos.mandiri.organik import LukaDomain`; `from pycos.refleksi.nurani import Nurani as _N`; `from typing import TYPE_CHECKING, Any, Deque, Dict, List, Mapping, Optional, Sequence, Tuple, Set, Callable, cast`; `import copy`; `import json`; `import json as _json`; `import math`; `import os as _os`; `import random`; `import re`; `import sys as _sys`; `import zlib`.

- L382–390 **`CalibrationReport.to_dict`** · kontrol=2, assignment/delete=0, except=0 · Call: `round`, `self.per_drive_ema.items`
- L404–542 **`Nurani.__init__`** · kontrol=15, assignment/delete=78, except=0 · Call: `copy.deepcopy`, `enumerate`, `float`, `len`, `random.Random`, `range`, `self._p`, `tuple`
- L545–547 **`Nurani.enabled`** · kontrol=0, assignment/delete=0, except=0 · Call: `bool`, `self.params.get`
- L549–550 **`Nurani.any_enabled`** · kontrol=1, assignment/delete=0, except=0 · Call: `any`, `self.enabled`
- L552–560 **`Nurani.set_pillars`** · kontrol=3, assignment/delete=2, except=0 · Call: `ValueError`, `bool`, `self.params.get`, `tuple`
- L562–567 **`Nurani._p`** · kontrol=1, assignment/delete=2, except=0 · Call: `float`, `isinstance`, `self.params.get`, `v.get`
- L569–585 **`Nurani._p_drive`** · kontrol=3, assignment/delete=1, except=0 · Call: `float`, `isinstance`, `self.params.get`
- L594–610 **`Nurani._muat_frekuensi`** · kontrol=6, assignment/delete=6, except=1 · Call: `_json.load`, `dok.get`, `e.get`, `float`, `jalur_leksikon`, `max`, `open`, `str`, `str(e.get('lema', '')).lower`
- L614–623 **`Nurani._bobot_kata`** · kontrol=0, assignment/delete=3, except=0 · Call: `Nurani._FREK_LEKSIKON.get`, `math.log10`, `max`
- L626–651 **`Nurani.keywords`** · kontrol=5, assignment/delete=7, except=1 · Call: `Nurani._lexical_words`, `_stem`, `cls._bobot_kata`, `cls._muat_frekuensi`, `dict.fromkeys`, `enumerate`, `len`, `list`, `sorted`, `tuple`
- L653–663 **`Nurani.context_signature`** · kontrol=3, assignment/delete=4, except=0 · Call: `'|'.join`, `'|'.join(self.keywords(teks)).encode`, `len`, `self._sig_cache.clear`, `self._sig_cache.get`, `self.keywords`, `str`, `zlib.crc32`
- L665–674 **`Nurani._retention_score`** · kontrol=2, assignment/delete=6, except=0 · Call: `abs`, `cast`, `deltas.values`, `float`, `int`, `item.get`, `math.log1p`, `max`, `min`, `self._p`
- L676–682 **`Nurani._evict_affective`** · kontrol=2, assignment/delete=3, except=0 · Call: `int`, `len`, `min`, `self._affective.items`, `self._affective.pop`, `self._p`, `self._retention_score`
- L684–704 **`Nurani._append_episode_log`** · kontrol=6, assignment/delete=5, except=0 · Call: `abs`, `bool`, `copied.values`, `deltas.get`, `float`, `int`, `jepit_drive`, `len`, `max`, `self._episode_log.append`, `self._episode_log.sort`, `self._p`, `self._retention_score`, `self.params.get`, `str`, `x.get`
- L707–762 **`Nurani._lexical_words`** · kontrol=14, assignment/delete=7, except=1 · Call: `_cak`, `_stem`, `_tambah`, `_tok`, `enumerate`, `isi.append`, `len`, `re.findall`, `seen.add`, `set`, `str`, `str(text or '').casefold`, `tuple`, `words.append`, `zip`
- L748–753 **`Nurani._lexical_words._tambah`** · kontrol=1, assignment/delete=0, except=0 · Call: `len`, `seen.add`, `words.append`
- L764–770 **`Nurani._evict_word_delta`** · kontrol=1, assignment/delete=3, except=0 · Call: `int`, `len`, `max`, `min`, `self._kata_delta.items`, `self._kata_delta.pop`, `self._p`, `self._retention_score`
- L772–801 **`Nurani._update_word_delta`** · kontrol=9, assignment/delete=13, except=0 · Call: `(drive_deltas or {}).get`, `abs`, `float`, `incoming.values`, `int`, `jepit_01`, `jepit_drive`, `max`, `self._evict_word_delta`, `self._kata_delta.get`, `self._lexical_words`, `self._p`, `slot.get`, `slot['deltas'].get`
- L803–831 **`Nurani.anticipate_words`** · kontrol=11, assignment/delete=10, except=0 · Call: `deltas.get`, `float`, `int`, `jepit_01`, `max`, `min`, `self._kata_delta.get`, `self._lexical_words`, `self._p`, `self.enabled`, `slot.get`, `sum`, `weighted.append`
- L833–865 **`Nurani.experience`** · kontrol=6, assignment/delete=13, except=0 · Call: `abs`, `drive_deltas.get`, `float`, `incoming.values`, `int`, `jepit_drive`, `max`, `self._affective.get`, `self._append_episode_log`, `self._evict_affective`, `self._update_word_delta`, `self.context_signature`, `self.enabled`, `slot.get`, `str`
- L867–906 **`Nurani.warmup_from_log`** · kontrol=8, assignment/delete=18, except=0 · Call: `deltas.get`, `entry.get`, `float`, `int`, `jepit_drive`, `len`, `max`, `self._affective.get`, `self._evict_affective`, `self._update_word_delta`, `slot.get`, `sorted`, `str`, `x.get`
- L908–937 **`Nurani.anticipate_detail`** · kontrol=9, assignment/delete=11, except=0 · Call: `int`, `max`, `min`, `self._affective.get`, `self._core_cap.get`, `self._p`, `self._p_drive`, `self.context_signature`, `self.enabled`, `str`
- L939–947 **`Nurani.anticipate`** · kontrol=0, assignment/delete=0, except=0 · Call: `self.anticipate_detail`
- L949–964 **`Nurani.forget_affective`** · kontrol=4, assignment/delete=4, except=0 · Call: `int`, `len`, `max`, `self._affective.items`, `self._affective.pop`, `self._affective.values`, `self._p`
- L967–968 **`Nurani.affective_size`** · kontrol=0, assignment/delete=0, except=0 · Call: `len`
- L971–1015 **`Nurani.record_observation`** · kontrol=9, assignment/delete=12, except=0 · Call: `abs`, `float`, `jepit_01`, `jepit_drive`, `len`, `per_drive.items`, `self._errors.append`, `self._errors.pop`, `self._p`, `self._p_drive`, `self._pairs_unit.append`, `self._pairs_unit.pop`, `self.enabled`
- L1017–1031 **`Nurani.record_uncertainty`** · kontrol=2, assignment/delete=7, except=0 · Call: `float`, `jepit_01`, `self._p`, `self.enabled`, `self.uncertainty_report`
- L1033–1044 **`Nurani.uncertainty_report`** · kontrol=2, assignment/delete=4, except=0 · Call: `float`, `int`, `round`
- L1046–1063 **`Nurani.calibration_report`** · kontrol=4, assignment/delete=9, except=0 · Call: `CalibrationReport`, `int`, `max`, `min`, `range`, `self._p`
- L1065–1076 **`Nurani.recent_spike`** · kontrol=1, assignment/delete=3, except=0 · Call: `float`, `int`, `max`, `self._p`
- L1079–1089 **`Nurani._rasio`** · kontrol=6, assignment/delete=3, except=0 · Call: `abs`, `len`, `sum`
- L1092–1105 **`Nurani.holdout_brier`** · kontrol=2, assignment/delete=4, except=0 · Call: `float`, `jepit_drive`, `len`, `math.tanh`
- L1107–1139 **`Nurani.scale_from_holdout`** · kontrol=6, assignment/delete=15, except=0 · Call: `float`, `int`, `jepit`, `len`, `list`, `self._p`, `self._rasio`, `self.holdout_brier`, `self.params.get`
- L1142–1157 **`Nurani.update_setpoints`** · kontrol=2, assignment/delete=5, except=0 · Call: `float`, `levels.get`, `max`, `min`, `self._p_drive`, `self.enabled`
- L1159–1161 **`Nurani.relative_deficit`** · kontrol=0, assignment/delete=0, except=0 · Call: `float`, `max`, `self.setpoints.get`
- L1163–1192 **`Nurani.update_interoception`** · kontrol=11, assignment/delete=8, except=0 · Call: `deficits.get`, `float`, `int`, `len`, `max`, `range`, `self._p`, `self._p_drive`, `self.advance_perception_tick`, `self.enabled`
- L1194–1239 **`Nurani.structural_surprise`** · kontrol=12, assignment/delete=16, except=0 · Call: `(galat_per_drive or {}).get`, `abs`, `dict`, `errors.items`, `errors.values`, `float`, `int`, `len`, `list`, `max`, `range`, `round`, `self._p`, `self._structural_shocks.append`, `sum`
- L1241–1245 **`Nurani.advance_perception_tick`** · kontrol=1, assignment/delete=2, except=0 · Call: `dict`, `int`, `self._sensitivitas_instabil.items`, `v.get`
- L1247–1262 **`Nurani.interoceptive_echo`** · kontrol=4, assignment/delete=3, except=0 · Call: `deficits.get`, `float`, `self._p_drive`, `self.enabled`
- L1265–1270 **`Nurani.circadian_phase`** · kontrol=0, assignment/delete=3, except=0 · Call: `int`, `max`, `min`, `self._p`
- L1272–1280 **`Nurani.night_energy_shift`** · kontrol=1, assignment/delete=0, except=0 · Call: `self._p`, `self.circadian_phase`, `self.enabled`
- L1283–1286 **`Nurani._efek`** · kontrol=3, assignment/delete=0, except=0 · Call: `c.get`, `dict`, `getattr`, `isinstance`
- L1289–1294 **`Nurani._urgensi`** · kontrol=2, assignment/delete=1, except=1 · Call: `float`, `getattr`, `goal.get`, `isinstance`
- L1297–1299 **`Nurani._drive`** · kontrol=1, assignment/delete=1, except=0 · Call: `getattr`, `goal.get`, `isinstance`, `str`
- L1301–1338 **`Nurani.detect_conflict`** · kontrol=10, assignment/delete=9, except=0 · Call: `any`, `float`, `hasil.update`, `len`, `self._drive`, `self._efek`, `self._efek(c).get`, `self._p`, `self._urgensi`, `sum`, `tanda`
- L1320–1321 **`Nurani.detect_conflict.tanda`** · kontrol=0, assignment/delete=0, except=0 · Call: `float`, `self._efek`, `self._efek(c).get`
- L1340–1347 **`Nurani.compromise_bonus`** · kontrol=4, assignment/delete=2, except=0 · Call: `effects.get`, `float`, `min`, `self._p`
- L1349–1359 **`Nurani.note_conflict`** · kontrol=4, assignment/delete=5, except=0 · Call: `det.get`, `int`, `list`
- L1361–1364 **`Nurani.flow_state`** · kontrol=1, assignment/delete=0, except=0 · Call: `float`, `self._p`
- L1366–1373 **`Nurani.flow_reward_bonus`** · kontrol=2, assignment/delete=1, except=0 · Call: `self._p`, `self.enabled`, `self.flow_state`
- L1377–1379 **`Nurani._eid`** · kontrol=0, assignment/delete=0, except=0 · Call: `str`
- L1381–1384 **`Nurani._netral`** · kontrol=0, assignment/delete=0, except=0 · Call: `self._eid`
- L1386–1401 **`Nurani.meet`** · kontrol=5, assignment/delete=4, except=0 · Call: `int`, `self._eid`, `self._entitas.get`, `self._netral`, `self.enabled`, `self.relationship`, `str`
- L1403–1417 **`Nurani.relationship`** · kontrol=2, assignment/delete=1, except=0 · Call: `bool`, `dict`, `float`, `int`, `round`, `self._berat_utang_slot`, `self._eid`, `self._entitas.get`, `self._menarik_diri_slot`, `self._netral`, `slot.get`, `u.get`
- L1419–1440 **`Nurani.break_trust`** · kontrol=2, assignment/delete=9, except=0 · Call: `abs`, `float`, `int`, `jepit_01`, `min`, `self._eid`, `self._entitas.get`, `self._netral`, `self.enabled`, `self.meet`, `self.relationship`
- L1443–1446 **`Nurani._berat_utang_slot`** · kontrol=2, assignment/delete=0, except=0 · Call: `float`, `max`, `slot.get`, `sum`, `u.get`
- L1448–1450 **`Nurani._menarik_diri_slot`** · kontrol=0, assignment/delete=1, except=0 · Call: `max`, `self._berat_utang_slot`, `self._p`
- L1452–1471 **`Nurani.tambah_utang`** · kontrol=3, assignment/delete=5, except=0 · Call: `dict`, `float`, `int`, `len`, `max`, `round`, `self._berat_utang_slot`, `self._eid`, `self._entitas.get`, `self._menarik_diri_slot`, `self.enabled`, `self.meet`, `slot.setdefault`, `slot.setdefault('utang', []).append`, `str`
- L1473–1488 **`Nurani.bayar_utang`** · kontrol=6, assignment/delete=6, except=0 · Call: `int`, `self._eid`, `self._entitas.get`, `slot.get`, `str`, `str(isi)[:60].lower`, `str(u.get('isi', '')).lower`, `u.get`
- L1490–1492 **`Nurani.berat_utang`** · kontrol=0, assignment/delete=1, except=0 · Call: `round`, `self._berat_utang_slot`, `self._eid`, `self._entitas.get`
- L1494–1497 **`Nurani.menarik_diri`** · kontrol=1, assignment/delete=1, except=0 · Call: `bool`, `self._eid`, `self._entitas.get`, `self._menarik_diri_slot`
- L1499–1512 **`Nurani.utang_state`** · kontrol=7, assignment/delete=1, except=0 · Call: `bool`, `dict`, `len`, `round`, `s.get`, `self._berat_utang_slot`, `self._eid`, `self._entitas.get`, `self._entitas.items`, `self._menarik_diri_slot`, `slot.get`, `u.get`
- L1515–1527 **`Nurani.tandai_core`** · kontrol=0, assignment/delete=3, except=0 · Call: `float`, `jepit_01`, `list`, `round`, `self._p`, `self.context_signature`, `self.keywords`, `str`
- L1529–1531 **`Nurani.core_cap_state`** · kontrol=1, assignment/delete=0, except=0 · Call: `len`, `round`, `self._core_cap.items`
- L1533–1548 **`Nurani.trust_recovery_factor`** · kontrol=2, assignment/delete=4, except=0 · Call: `abs`, `float`, `max`, `min`, `self._eid`, `self._entitas.get`, `self._p`, `slot.get`
- L1550–1641 **`Nurani.interact`** · kontrol=15, assignment/delete=44, except=0 · Call: `abs`, `cast`, `float`, `int`, `jepit_01`, `jepit_drive`, `len`, `math.log1p`, `max`, `min`, `self._berat_utang_slot`, `self._eid`, `self._entitas.get`, `self._entitas.items`, `self._entitas.pop`, `self._menarik_diri_slot`, `self._netral`, `self._p`, `self.enabled`, `self.meet`, `self.relationship`, `slot2.get`, `str`
- L1630–1637 **`Nurani.interact.retensi`** · kontrol=0, assignment/delete=4, except=0 · Call: `abs`, `cast`, `float`, `int`, `math.log1p`, `max`, `min`, `slot2.get`
- L1643–1679 **`Nurani.social_prior`** · kontrol=7, assignment/delete=12, except=0 · Call: `abs`, `float`, `max`, `self._berat_utang_slot`, `self._eid`, `self._entitas.get`, `self._menarik_diri_slot`, `self._p`, `self._p_drive`, `self.enabled`
- L1681–1690 **`Nurani.set_kacamata_sosial`** · kontrol=1, assignment/delete=1, except=0 · Call: `ValueError`, `dict`, `float`, `jepit_01`, `jepit_drive`
- L1692–1694 **`Nurani.kacamata_sosial_state`** · kontrol=1, assignment/delete=0, except=0 · Call: `abs`, `dict`, `float`, `self._kacamata_sosial.items`, `v.get`
- L1696–1738 **`Nurani.observe_other_belief`** · kontrol=7, assignment/delete=21, except=0 · Call: `ValueError`, `abs`, `float`, `int`, `item.get`, `jepit_01`, `jepit_drive`, `len`, `lensa.get`, `max`, `min`, `self._eid`, `self._other_beliefs.pop`, `self._other_beliefs.setdefault`, `self._other_beliefs[k].values`, `self._p`, `self.estimate_other_belief`, `slot.get`, `v.get`
- L1740–1777 **`Nurani.estimate_other_belief`** · kontrol=4, assignment/delete=13, except=0 · Call: `ValueError`, `abs`, `float`, `int`, `jepit`, `jepit_01`, `jepit_drive`, `lensa.get`, `max`, `observed.get`, `relation.get`, `self._eid`, `self._entitas.get`, `self._other_beliefs.get`, `self._other_beliefs.get(eid, {}).get`, `self._p`
- L1779–1794 **`Nurani.decay_social`** · kontrol=4, assignment/delete=5, except=0 · Call: `int`, `max`, `self._entitas.values`, `self._p`, `self.enabled`
- L1796–1807 **`Nurani.forget_social`** · kontrol=4, assignment/delete=4, except=0 · Call: `int`, `len`, `max`, `self._entitas.items`, `self._entitas.pop`, `self._entitas.values`, `self._p`
- L1810–1811 **`Nurani.social_size`** · kontrol=0, assignment/delete=0, except=0 · Call: `len`
- L1820–1831 **`Nurani._sens`** · kontrol=2, assignment/delete=5, except=0 · Call: `float`, `instabil.get`, `int`, `max`, `self._index.get`, `self._p_drive`, `self._sensitivitas_instabil.get`, `self.sensitivitas.get`
- L1833–1860 **`Nurani.deteksi`** · kontrol=4, assignment/delete=10, except=1 · Call: `abs`, `float`, `max`, `rng.gauss`, `self._p`, `self._p_drive`, `self._sens`
- L1862–1872 **`Nurani.kompres`** · kontrol=0, assignment/delete=2, except=0 · Call: `float`, `math.log`, `max`, `self._p`, `self.adaptasi.get`
- L1874–1886 **`Nurani.update_adaptasi`** · kontrol=3, assignment/delete=3, except=0 · Call: `(stimulus or {}).get`, `abs`, `float`, `int`, `max`, `self._p`, `self.advance_perception_tick`
- L1888–1889 **`Nurani._habit_sig`** · kontrol=0, assignment/delete=0, except=0 · Call: `f'{drive}|{str(reason)[:60]}'.encode`, `str`, `zlib.crc32`
- L1891–1926 **`Nurani.habit_factor`** · kontrol=6, assignment/delete=17, except=0 · Call: `cast`, `float`, `hslot.get`, `int`, `jepit`, `jepit_01`, `len`, `max`, `min`, `self._habit.get`, `self._habit.items`, `self._habit_sig`, `self._p`, `slot.get`, `str`
- L1916–1920 **`Nurani.habit_factor.retensi`** · kontrol=0, assignment/delete=3, except=0 · Call: `cast`, `float`, `hslot.get`, `int`, `max`, `min`
- L1928–1943 **`Nurani.belajar_persepsi`** · kontrol=3, assignment/delete=5, except=0 · Call: `(galat_per_drive or {}).items`, `abs`, `float`, `jepit`, `jepit_drive`, `self._p`
- L1945–1958 **`Nurani.persepsi_ringkas`** · kontrol=4, assignment/delete=0, except=0 · Call: `float`, `int`, `len`, `round`, `self._sens`, `self._sensitivitas_instabil.items`, `self.adaptasi.items`, `self.sensitivitas.items`, `v.get`
- L1983–1999 **`Nurani._pearson`** · kontrol=3, assignment/delete=11, except=0 · Call: `len`, `math.sqrt`, `sum`, `zip`
- L2001–2026 **`Nurani._self_perceive`** · kontrol=4, assignment/delete=11, except=1 · Call: `float`, `levels.get`, `max`, `rng.gauss`, `self._p_drive`, `urgency.get`
- L2028–2175 **`Nurani.update_introspection`** · kontrol=35, assignment/delete=54, except=0 · Call: `abs`, `bool`, `float`, `int`, `isinstance`, `jepit`, `jepit_01`, `konflik.get`, `len`, `levels.get`, `math.sqrt`, `max`, `perceived_l.get`, `perceived_u.get`, `self._error_monitor.append`, `self._introspeksi_history.append`, `self._meta_history.append`, `self._p`, `self._p_drive`, `self._pearson`, `self._self_perceive`, `self.enabled`, `self.kepercayaan_diri.values`, `self.refleksi_diri`, `sum`
- L2177–2239 **`Nurani.refleksi_diri`** · kontrol=10, assignment/delete=15, except=0 · Call: `', '.join`, `float`, `int`, `len`, `min`, `round`, `self.enabled`, `self.kepercayaan_diri.items`, `self.model_diri.get`, `self.narasi_diri.append`
- L2241–2260 **`Nurani.introspeksi_state`** · kontrol=5, assignment/delete=0, except=0 · Call: `float`, `len`, `round`, `self.enabled`, `self.introspeksi_korelasi_per_drive.items`, `self.kepercayaan_diri.items`, `self.meta_d.items`, `self.model_diri.items`, `self.model_urgensi.items`
- L2262–2289 **`Nurani.meta_kognisi_laporan`** · kontrol=3, assignment/delete=6, except=0 · Call: `int`, `jepit_01`, `len`, `round`, `self._p`, `self.enabled`, `self.meta_d.items`
- L2291–2311 **`Nurani.evaluasi_diri`** · kontrol=6, assignment/delete=4, except=0 · Call: `errors.items`, `len`, `round`, `self.enabled`, `sorted`, `sum`
- L2313–2322 **`Nurani.sadar_diri`** · kontrol=3, assignment/delete=1, except=0 · Call: `float`, `self._p`, `self.enabled`
- L2324–2346 **`Nurani.seed_introspection`** · kontrol=8, assignment/delete=8, except=0 · Call: `dict`, `float`, `jepit_01`, `jepit_drive`, `kepercayaan.items`, `len`, `model_diri.items`, `self.kepercayaan_diri.values`, `sum`
- L2355–2375 **`Nurani.seed_affective`** · kontrol=4, assignment/delete=6, except=0 · Call: `abs`, `deltas.values`, `drive_deltas.get`, `float`, `int`, `jepit_drive`, `max`, `self._append_episode_log`, `self._evict_affective`, `self.context_signature`, `str`
- L2377–2387 **`Nurani.seed_relationship`** · kontrol=1, assignment/delete=1, except=0 · Call: `float`, `int`, `jepit_01`, `jepit_drive`, `max`, `self._eid`, `self.relationship`, `str`
- L2389–2401 **`Nurani.seed_setpoints`** · kontrol=3, assignment/delete=4, except=0 · Call: `(setpoints or {}).items`, `float`, `max`, `min`, `self._p_drive`
- L2403–2413 **`Nurani.seed_calibration`** · kontrol=4, assignment/delete=5, except=0 · Call: `(per_drive or {}).items`, `abs`, `float`, `int`, `max`
- L2416–2470 **`Nurani.meta_status`** · kontrol=5, assignment/delete=2, except=0 · Call: `dict`, `int`, `len`, `list`, `rep.per_drive_ema.items`, `round`, `self._p`, `self.calibration_report`, `self.enabled`, `self.introspeksi_state`, `self.meta_kognisi_laporan`, `self.persepsi_ringkas`, `self.setpoints.items`, `self.uncertainty_report`, `sum`
- L2473–2620 **`Nurani.to_dict`** · kontrol=34, assignment/delete=2, except=0 · Call: `bool`, `copy.deepcopy`, `dict`, `e.get`, `e['deltas'].get`, `float`, `int`, `list`, `n.get`, `s.get`, `s['deltas'].get`, `self._affective.items`, `self._core_cap.items`, `self._entitas.items`, `self._habit.items`, `self._kata_delta.items`, `self.adaptasi.items`, `self.felt_state.items`, `self.introspeksi_korelasi_per_drive.items`, `self.kepercayaan_diri.items`, `self.meta_d.items`, `self.model_diri.items`, `self.model_urgensi.items`, `self.moral_emotions.items`, `self.sensitivitas.items`, `slot.get`, `slot.get('deltas', {}).get`, `str`
- L2623–2859 **`Nurani.from_dict`** · kontrol=127, assignment/delete=97, except=3 · Call: `(data.get('affective') or {}).items`, `(data.get('core_cap') or {}).items`, `(data.get('drive_err_ema') or {}).items`, `(data.get('drive_err_n') or {}).items`, `(data.get('entitas') or {}).items`, `(data.get('kacamata_sosial') or {}).items`, `(data.get('other_beliefs') or {}).items`, `(data.get('sensitivitas_instabil') or {}).items`, `(data.get('setpoints') or {}).items`, `(data.get('word_deltas') or {}).items`, `(e.get('deltas') or {}).get`, `(f.get('adaptasi') or {}).items`, `(f.get('habit') or {}).items`, `(f.get('sensitivitas') or {}).items`, `(g.get('kepercayaan') or {}).items`, `(g.get('korelasi') or {}).items`, `(g.get('meta_d') or {}).items`, `(g.get('model_diri') or {}).items`, `(g.get('model_urgensi') or {}).items`, `(h.get('felt') or {}).items`, `(h.get('kategori_proto') or {}).items`, `(h.get('moral') or {}).items`, `(item.get('deltas') or {}).get`, `(s.get('deltas') or {}).get`, `abs`, `b.get`, `bool`, `c.get`, `cls`, `copy.deepcopy`, `data.get`, `deltas.values`, `dict`, `drives_map.items`, `e.get`, `ed.values`, `f.get`, `fc.get`, `float`, `g.get`, `gc.get`, `h.get`, `int`, `isinstance`, `item.get`, `jepit`, `jepit_01`, `jepit_drive`, `k.get`, `len`, `list`, `max`, `n.get`, `nur._episode_log.append`, `nur._episode_log.sort`, `nur._evict_word_delta`, `nur._kata_delta.values`, `nur._p`, `nur._retention_score`, `s.get`, `sc.get`, `str`, `str(word).casefold`, `str(word).casefold().strip`, `tuple`, `u.get`, `validasi_state`, `x.get`
- L2864–2908 **`Nurani.serap_kategori`** · kontrol=9, assignment/delete=14, except=0 · Call: `dict`, `entri.get`, `float`, `int`, `jepit_01`, `kv[1].get`, `lama.get`, `len`, `max`, `min`, `round`, `self.kategori_proto.get`, `self.kategori_proto.items`, `self.kategori_proto.pop`, `str`, `x.get`
- L2910–2913 **`Nurani.sensitivitas_kategori`** · kontrol=1, assignment/delete=0, except=0 · Call: `dict`, `float`, `self.kategori_proto.items`, `v.get`
- L2915–2918 **`Nurani.peka_terhadap`** · kontrol=0, assignment/delete=1, except=0 · Call: `entri.get`, `float`, `self.kategori_proto.get`, `str`
- L2923–2924 **`Nurani.felt_consciousness`** · kontrol=0, assignment/delete=0, except=0 · Call: `bool`, `self.params.get`
- L2926–2928 **`Nurani._felt`** · kontrol=1, assignment/delete=0, except=0 · Call: `bool`, `self.felt_consciousness`, `self.params.get`
- L2930–2966 **`Nurani.update_felt`** · kontrol=7, assignment/delete=11, except=0 · Call: `dict`, `float`, `int`, `jepit`, `jepit_01`, `levels.get`, `max`, `self._felt`, `self._p`, `self._somatic_tag`, `self.felt_consciousness`, `self.felt_state.get`, `self.somatic_mark`, `target.get`, `urg.get`
- L2969–2972 **`Nurani._somatic_tag`** · kontrol=0, assignment/delete=0, except=0 · Call: `{'sesak': 'keamanan', 'jantung': 'keamanan', 'tegang': 'keamanan', 'nyeri': 'keamanan', 'lelah': 'energi', 'lapar': 'energi', 'mual': 'koherensi', 'ringan': 'energi'}.get`
- L2974–2987 **`Nurani.felt_report`** · kontrol=4, assignment/delete=5, except=0 · Call: `float`, `max`, `round`, `self._felt_phrase`, `self._p`, `self.felt_consciousness`, `self.felt_state.items`, `self.moral_emotions.items`
- L2990–2996 **`Nurani._felt_phrase`** · kontrol=0, assignment/delete=0, except=0 · Call: `{'nyeri': 'badanku nyeri', 'lelah': 'aku tidak enak badan', 'lapar': 'aku lapar', 'sesak': 'dadaku sesak', 'jantung': 'jantungku berdebar', 'mual': 'aku mual', 'tegang': 'tubuhku tegang', 'ringan': 'badanku ringan'}.get`
- L2998–3008 **`Nurani.moral_emotion`** · kontrol=2, assignment/delete=3, except=0 · Call: `NURANI_MORAL_ALIASES.get`, `float`, `jepit_01`, `self._felt`, `self._p`, `str`, `str(emosi).lower`
- L3010–3022 **`Nurani.somatic_mark`** · kontrol=2, assignment/delete=3, except=0 · Call: `float`, `int`, `jepit_drive`, `len`, `max`, `self._felt`, `self._p`, `self.somatic_markers.append`, `str`
- L3024–3032 **`Nurani.somatic_bias`** · kontrol=3, assignment/delete=3, except=0 · Call: `acc.get`, `acc.items`, `float`, `m.get`, `round`, `self._felt`
- L3034–3050 **`Nurani.inner_speech`** · kontrol=4, assignment/delete=4, except=0 · Call: `h.get`, `int`, `len`, `max`, `round`, `self._felt`, `self._inner_speech_text`, `self.narasi_diri.append`
- L3052–3078 **`Nurani._inner_speech_text`** · kontrol=8, assignment/delete=4, except=0 · Call: `float`, `frasa.get`, `max`, `self._felt_phrase`, `self._p`, `self.felt_state.get`, `self.model_diri.get`, `str`, `str(konteks or '').lower`
- L3080–3098 **`Nurani.narrate_identity`** · kontrol=4, assignment/delete=4, except=0 · Call: `ada.get`, `float`, `int`, `jepit_01`, `len`, `list`, `next`, `self._felt`, `self.narrative_identity.append`, `str`, `x.get`
- L3100–3107 **`Nurani.narrative_identity_state`** · kontrol=2, assignment/delete=1, except=0 · Call: `float`, `max`, `self._felt`, `top.get`, `x.get`
- L3110–3118 **`Nurani.classify_source`** · kontrol=3, assignment/delete=1, except=0 · Call: `item.get`, `str`
- L3120–3138 **`Nurani.reality_monitoring`** · kontrol=4, assignment/delete=6, except=0 · Call: `int`, `item.get`, `len`, `round`, `self._felt`, `self._rng.random`, `self.classify_source`, `self.reality_source_log.append`, `str`
- L3140–3149 **`Nurani.source_memory`** · kontrol=4, assignment/delete=1, except=0 · Call: `e.get`, `e.get('isi', '').lower`, `next`, `reversed`, `self._felt`, `str`, `str(tentang).lower`
- L3151–3160 **`Nurani.metacognitive_doubt`** · kontrol=2, assignment/delete=2, except=0 · Call: `float`, `jepit_01`, `self._felt`, `self._p`
- L3162–3181 **`Nurani.confabulation`** · kontrol=2, assignment/delete=5, except=0 · Call: `int`, `len`, `max`, `self._felt`, `self._p`, `self._rng.choice`, `self.confabulation_log.append`, `str`
- L3183–3197 **`Nurani.kesadaran_laporan`** · kontrol=0, assignment/delete=0, except=0 · Call: `len`, `round`, `self.felt_consciousness`, `self.felt_report`, `self.narrative_identity_state`, `self.somatic_bias`
- L3199–3202 **`Nurani.to_json`** · kontrol=0, assignment/delete=0, except=0 · Call: `json.dumps`, `json_kwargs.setdefault`, `self.to_dict`
- L3205–3207 **`Nurani.from_json`** · kontrol=0, assignment/delete=0, except=0 · Call: `cls.from_dict`, `json.loads`
- L3211–3334 **`Nurani.demo`** · kontrol=21, assignment/delete=34, except=0 · Call: `' '.join`, `abs`, `cls`, `deltas.items`, `dict`, `k.startswith`, `len`, `list`, `max`, `next`, `nur.anticipate`, `nur.belajar_persepsi`, `nur.calibration_report`, `nur.circadian_phase`, `nur.compromise_bonus`, `nur.detect_conflict`, `nur.deteksi`, `nur.experience`, `nur.interact`, `nur.interoceptive_echo`, `nur.introspeksi_state`, `nur.kompres`, `nur.meet`, `nur.meta_kognisi_laporan`, `nur.record_observation`, `nur.refleksi_diri`, `nur.relationship`, `nur.scale_from_holdout`, `nur.social_prior`, `nur.update_adaptasi`, `nur.update_interoception`, `nur.update_introspection`, `nur.update_setpoints`, `print`, `prior_sosial.items`, `random.Random`, `range`, `rng.gauss`, `rng.uniform`, `rng_i.gauss`, `rng_i.random`, `rng_i.uniform`, `sum`
- L3356–3364 **`_nurani_luka`** · kontrol=2, assignment/delete=4, except=0 · Call: `cast`, `getattr`, `modul.LukaDomain`, `optional_module`
- L3367–3369 **`hancurkan_domain`** · kontrol=0, assignment/delete=1, except=0 · Call: `_nurani_luka`, `lk.lukai`
- L3372–3374 **`dikecualikan`** · kontrol=0, assignment/delete=1, except=0 · Call: `cast`, `getattr`, `lk.dikecualikan`
- L3377–3379 **`domain_terluka`** · kontrol=0, assignment/delete=1, except=0 · Call: `cast`, `getattr`, `lk.domain_terluka`
- L3382–3385 **`terapkan_domain`** · kontrol=0, assignment/delete=1, except=0 · Call: `cast`, `float`, `getattr`, `lk.terapkan`
- L3388–3390 **`tambal_luka`** · kontrol=0, assignment/delete=1, except=0 · Call: `cast`, `getattr`, `lk.tambal`
- L3393–3395 **`luka_state`** · kontrol=0, assignment/delete=1, except=0 · Call: `cast`, `getattr`, `lk.ringkas`
- L3409–3418 **`_luka_break_trust`** · kontrol=2, assignment/delete=1, except=1 · Call: `float`, `original`, `self.hancurkan_domain`
- L3425–3435 **`_luka_relationship`** · kontrol=3, assignment/delete=4, except=1 · Call: `isinstance`, `original`, `self.domain_terluka`
- L3442–3444 **`_nurani_luka_ambil`** · kontrol=0, assignment/delete=1, except=0 · Call: `cast`, `getattr`, `lk.to_dict`
- L3447–3454 **`_nurani_luka_pasang`** · kontrol=2, assignment/delete=2, except=1 · Call: `modul.LukaDomain.from_dict`, `optional_module`
- L3457–3464 **`_luka_to_dict`** · kontrol=2, assignment/delete=2, except=1 · Call: `_nurani_luka_ambil`, `isinstance`, `original`
- L3467–3474 **`_luka_from_dict`** · kontrol=3, assignment/delete=1, except=1 · Call: `_nurani_luka_pasang`, `data.get`, `isinstance`, `original`
- L3489–3504 **`_nurani_ambang_kecurigaan`** · kontrol=4, assignment/delete=8, except=1 · Call: `float`, `getattr`, `jepit`, `max`, `p.get`, `r.get`, `self.relationship`
- L3507–3509 **`_nurani_sambungkan_graf`** · kontrol=0, assignment/delete=1, except=0 · Call: tidak ada
- L3512–3516 **`_nurani_asosiasi_emosi`** · kontrol=1, assignment/delete=1, except=0 · Call: `cast`, `g.emosi_terasosiasi`, `getattr`
- L3519–3524 **`_nurani_bias_asosiatif`** · kontrol=1, assignment/delete=2, except=0 · Call: `float`, `round`, `self.asosiasi_emosi`, `self.asosiasi_emosi(konsep).items`
- L3571–3573 **`DimensiSkor.to_dict`** · kontrol=0, assignment/delete=0, except=0 · Call: tidak ada
- L3585–3586 **`Laporan.skor_dimensi`** · kontrol=1, assignment/delete=0, except=0 · Call: tidak ada
- L3588–3592 **`Laporan.to_dict`** · kontrol=1, assignment/delete=0, except=0 · Call: `d.to_dict`, `list`
- L3595–3599 **`_campur`** · kontrol=1, assignment/delete=0, except=0 · Call: tidak ada
- L3602–3603 **`_skor`** · kontrol=0, assignment/delete=0, except=0 · Call: `abs`, `max`
- L3606–3618 **`_saran_dimensi`** · kontrol=3, assignment/delete=1, except=0 · Call: tidak ada
- L3621–3626 **`_stem_bantu`** · kontrol=2, assignment/delete=0, except=1 · Call: `_stem`, `str`, `str(kata or '').lower`
- L3629–3637 **`_lemma_set`** · kontrol=4, assignment/delete=0, except=1 · Call: `_N._lexical_words`, `_stem`, `re.findall`, `set`, `str`, `str(teks or '').lower`
- L3640–3643 **`_jaccard`** · kontrol=2, assignment/delete=0, except=0 · Call: `float`, `len`
- L3646–3762 **`nilai_selaras`** · kontrol=20, assignment/delete=37, except=2 · Call: `' '.join`, `'hapus kata pantangan: {}'.format`, `DimensiSkor`, `Laporan`, `_campur`, `_dimensi`, `_dimensi_skala`, `_jaccard`, `_lemma_set`, `_saran_dimensi`, `_stem_bantu`, `_stem_p`, `_stem_pantangan`, `abs`, `analisis_teks`, `dimensi.append`, `fitur.formalitas`, `fitur.intensitas`, `fitur.keraguan`, `fitur.polaritas`, `float`, `getattr`, `jepit_01`, `len`, `list`, `max`, `min`, `pelanggaran.append`, `persona.sifat_of`, `round`, `sum`, `token_dari`, `tuple`
- L3693–3696 **`nilai_selaras._dimensi_skala`** · kontrol=0, assignment/delete=0, except=0 · Call: `DimensiSkor`, `abs`, `jepit_01`, `round`
- L3765–3770 **`_dimensi`** · kontrol=1, assignment/delete=0, except=0 · Call: `DimensiSkor`, `_skor`, `round`
- L3786–3793 **`_kemiringan`** · kontrol=2, assignment/delete=5, except=0 · Call: `enumerate`, `len`, `range`, `sum`
- L3799–3814 **`PelacakSelaras.__init__`** · kontrol=7, assignment/delete=4, except=0 · Call: `ValueError`, `deque`, `float`, `isinstance`, `math.isfinite`
- L3816–3817 **`PelacakSelaras.__len__`** · kontrol=0, assignment/delete=0, except=0 · Call: `len`
- L3819–3823 **`PelacakSelaras.catat`** · kontrol=1, assignment/delete=0, except=0 · Call: `'catat menerima Laporan, bukan {}'.format`, `TypeError`, `isinstance`, `laporan.skor_dimensi`, `self._riwayat.append`, `type`
- L3825–3826 **`PelacakSelaras.kosongkan`** · kontrol=0, assignment/delete=0, except=0 · Call: `self._riwayat.clear`
- L3828–3836 **`PelacakSelaras._seri`** · kontrol=4, assignment/delete=1, except=0 · Call: `dimensi.items`, `seri.setdefault`, `seri.setdefault(nama, []).append`, `seri['keseluruhan'].append`
- L3838–3859 **`PelacakSelaras.tren`** · kontrol=5, assignment/delete=10, except=0 · Call: `_kemiringan`, `len`, `round`, `self._seri`, `self._seri().items`, `sum`
- L3900–3910 **`_validasi_anotasi`** · kontrol=5, assignment/delete=2, except=0 · Call: `'.anotasi[{}] harus bool'.format`, `ValueError`, `anotasi.items`, `isinstance`, `nama.strip`
- L3913–3936 **`contoh_dari_dict`** · kontrol=8, assignment/delete=10, except=0 · Call: `', '.join`, `'contoh #{}'.format`, `'{}.formalitas harus salah satu dari {}'.format`, `'{}.polaritas harus -1, 0, 1, atau null'.format`, `'{}.selaras harus true, false, atau null'.format`, `ContohLabel`, `Keadaan.from_dict`, `Persona.from_dict`, `ValueError`, `_validasi_anotasi`, `data.get`, `dict`, `hanya_kunci`, `isinstance`, `teks_wajib`
- L3939–3958 **`muat_korpus`** · kontrol=7, assignment/delete=2, except=2 · Call: `'baris {}: JSON tidak valid ({})'.format`, `'baris {}: harus objek JSON'.format`, `'baris {}: {}'.format`, `'korpus kosong: {}'.format`, `ValueError`, `baris.strip`, `contoh_dari_dict`, `enumerate`, `hasil.append`, `isinstance`, `json.loads`, `open`
- L3961–3972 **`kappa_cohen`** · kontrol=8, assignment/delete=4, except=0 · Call: `len`, `math.isclose`, `sorted`, `sum`
- L3975–3976 **`_bulat`** · kontrol=0, assignment/delete=0, except=0 · Call: `round`
- L3979–3985 **`_ringkas`** · kontrol=2, assignment/delete=2, except=0 · Call: `_bulat`, `kappa_cohen`, `len`, `round`, `sum`
- L3988–4006 **`ukur_fitur`** · kontrol=3, assignment/delete=7, except=0 · Call: `_ringkas`, `analisis_teks`, `f.formalitas`, `f.polaritas`, `form.append`, `len`, `pol.append`
- L4009–4014 **`_skor_selaras`** · kontrol=2, assignment/delete=1, except=0 · Call: `Keadaan`, `nilai_selaras`
- L4017–4022 **`_akurasi_ambang`** · kontrol=3, assignment/delete=1, except=0 · Call: `len`, `sum`
- L4025–4068 **`ukur_selaras`** · kontrol=11, assignment/delete=13, except=0 · Call: `_akurasi_ambang`, `_bulat`, `_skor_selaras`, `abs`, `int`, `len`, `range`, `round`
- L4071–4152 **`_evaluasi_eksternal`** · kontrol=28, assignment/delete=26, except=0 · Call: `' '.join`, `'{}[{}] harus ContohLabel'.format`, `ValueError`, `_akurasi_ambang`, `_bulat`, `_skor_selaras`, `_validasi_anotasi`, `abs`, `bool`, `c.anotasi.values`, `combinations`, `enumerate`, `evaluasi.append`, `identitas`, `ids.add`, `isinstance`, `kappa_cohen`, `len`, `max`, `pasangan.append`, `pilihan.append`, `range`, `round`, `set`, `sorted`, `sum`, `teks.add`, `teks_wajib`, `teks_wajib(c.teks, nama + '.teks').casefold`, `teks_wajib(c.teks, nama + '.teks').casefold().split`
- L4075–4092 **`_evaluasi_eksternal.identitas`** · kontrol=7, assignment/delete=3, except=0 · Call: `' '.join`, `'{}[{}] harus ContohLabel'.format`, `ValueError`, `_validasi_anotasi`, `enumerate`, `ids.add`, `isinstance`, `set`, `teks.add`, `teks_wajib`, `teks_wajib(c.teks, nama + '.teks').casefold`, `teks_wajib(c.teks, nama + '.teks').casefold().split`
- L4155–4175 **`laporan_kalibrasi`** · kontrol=2, assignment/delete=1, except=0 · Call: `ValueError`, `_evaluasi_eksternal`, `len`, `ukur_fitur`, `ukur_selaras`

## `pycos/sumber_daya/__init__.py`

SHA-256: `48f9d2aecb7af63858d3aae7b40b0e4c67ce5092e390c6cc77aa0eecff0b6984`

26 baris; 0 kelas; 0 fungsi/metode termasuk nested.

Kelas: tidak ada.
Handler luas: tidak ada.

Impor (termasuk lazy/TYPE_CHECKING): `from __future__ import annotations`; `from pycos.dukungan.sumber import NAMA_KORPUS, NAMA_LEKSIKON, ada_sumber_daya, jalur_korpus, jalur_leksikon, sumber_daya`.


## `tests/__init__.py`

SHA-256: `b53bfa1ef68a313c6fe4a3b8f53743594a33b542cbf5f361f6ad7fa4d72620bc`

7 baris; 0 kelas; 0 fungsi/metode termasuk nested.

Kelas: tidak ada.
Handler luas: tidak ada.

Impor (termasuk lazy/TYPE_CHECKING): tidak ada.


## `tests/test_api_publik.py`

SHA-256: `0b9073f4745ebd8355160cf8423ab997f2080eb614ec4aa7933a6fde4a60a412`

67 baris; 1 kelas; 4 fungsi/metode termasuk nested.

Kelas: `ApiPublikR54Tests` L19.
Handler luas: tidak ada.

Impor (termasuk lazy/TYPE_CHECKING): `from __future__ import annotations`; `import importlib`; `import json`; `import os`; `import pycos`; `import subprocess`; `import sys`; `import unittest`.

- L20–35 **`ApiPublikR54Tests.test_seluruh_api_subpaket_terklasifikasi`** · kontrol=4, assignment/delete=3, except=0 · Call: `callable`, `getattr`, `importlib.import_module`, `seen.add`, `self.assertEqual`, `self.assertIn`, `self.assertIs`, `self.assertNotIn`, `self.assertTrue`, `self.subTest`, `set`
- L37–46 **`ApiPublikR54Tests.test_daftar_unik_dir_dan_cache`** · kontrol=3, assignment/delete=1, except=0 · Call: `dir`, `getattr`, `len`, `self.assertEqual`, `self.assertIn`, `self.assertIs`, `self.assertRaises`, `set`
- L48–55 **`ApiPublikR54Tests.test_impor_dan_dir_tidak_memuat_pemilik`** · kontrol=0, assignment/delete=2, except=0 · Call: `json.loads`, `self.assertEqual`, `subprocess.run`
- L57–67 **`ApiPublikR54Tests.test_star_import_dan_tabrakan_nama_paket`** · kontrol=0, assignment/delete=2, except=0 · Call: `self.assertEqual`, `subprocess.run`

## `tests/test_changelog.py`

SHA-256: `6d3459ca49433afd464aafb3e88f6677a03affa227a7d6ca92cbcf8fa72696a8`

77 baris; 1 kelas; 7 fungsi/metode termasuk nested.

Kelas: `ChangelogTests` L21.
Handler luas: tidak ada.

Impor (termasuk lazy/TYPE_CHECKING): `from __future__ import annotations`; `from pathlib import Path`; `from tempfile import TemporaryDirectory`; `from tools import periksa_changelog`; `from tools.periksa_changelog import errors, loaders, unreleased`; `from unittest.mock import patch`; `import os`; `import subprocess`; `import sys`; `import unittest`.

- L28–30 **`ChangelogTests.test_ast_ignores_comments_and_format`** · kontrol=0, assignment/delete=0, except=0 · Call: `errors`, `loaders`, `self.assertEqual`, `self.assertFalse`
- L32–36 **`ChangelogTests.test_missing_and_old_notes_fail`** · kontrol=1, assignment/delete=0, except=0 · Call: `errors`, `self.assertTrue`
- L38–40 **`ChangelogTests.test_new_note_passes`** · kontrol=0, assignment/delete=0, except=0 · Call: `errors`, `self.assertFalse`
- L42–48 **`ChangelogTests.test_added_removed_and_multiple_files`** · kontrol=1, assignment/delete=0, except=0 · Call: `errors`, `len`, `self.assertEqual`, `self.assertFalse`, `self.assertTrue`
- L50–52 **`ChangelogTests.test_unreleased_boundaries`** · kontrol=0, assignment/delete=0, except=0 · Call: `self.assertEqual`, `unreleased`
- L54–63 **`ChangelogTests.test_cli_and_invalid_base`** · kontrol=2, assignment/delete=1, except=0 · Call: `self.assertEqual`, `self.assertIn`, `self.assertNotEqual`, `subprocess.run`
- L65–77 **`ChangelogTests.test_main_success_and_failure_in_process`** · kontrol=3, assignment/delete=1, except=0 · Call: `(root / 'CHANGELOG.md').write_text`, `(root / 'pycos').mkdir`, `(root / self.path).write_text`, `Path`, `TemporaryDirectory`, `patch`, `patch.object`, `periksa_changelog.main`, `self.assertEqual`

## `tests/test_examples.py`

SHA-256: `033f3415f1ac72262db97b8dced17dc1659abd3f8f31ac50c5b764615adf5492`

74 baris; 1 kelas; 6 fungsi/metode termasuk nested.

Kelas: `ExamplesTests` L19.
Handler luas: tidak ada.

Impor (termasuk lazy/TYPE_CHECKING): `from __future__ import annotations`; `from pathlib import Path`; `import json`; `import os`; `import subprocess`; `import sys`; `import unittest`.

- L20–26 **`ExamplesTests.jalankan`** · kontrol=0, assignment/delete=1, except=0 · Call: `json.loads`, `self.assertEqual`, `str`, `subprocess.run`
- L28–39 **`ExamplesTests.test_npc_dunia`** · kontrol=3, assignment/delete=2, except=0 · Call: `(AKAR_PATH / 'examples/npc_dunia.py').read_text`, `(AKAR_PATH / 'examples/npc_dunia.py').read_text(encoding='utf-8').splitlines`, `len`, `self.assertEqual`, `self.assertLessEqual`, `self.assertTrue`, `self.jalankan`
- L41–51 **`ExamplesTests.test_dialog_hud`** · kontrol=1, assignment/delete=2, except=0 · Call: `self.assertEqual`, `self.assertIn`, `self.assertNotEqual`, `self.assertTrue`, `self.jalankan`
- L53–60 **`ExamplesTests.test_simpan_migrasi`** · kontrol=1, assignment/delete=1, except=0 · Call: `self.assertEqual`, `self.assertTrue`, `self.jalankan`
- L62–69 **`ExamplesTests.test_kawanan_lod`** · kontrol=0, assignment/delete=1, except=0 · Call: `dict.fromkeys`, `hasil['kemajuan'].values`, `len`, `self.assertEqual`, `self.jalankan`, `set`
- L71–74 **`ExamplesTests.test_output_deterministik`** · kontrol=2, assignment/delete=0, except=0 · Call: `self.assertEqual`, `self.jalankan`, `self.subTest`

## `tests/test_gate_pengembangan.py`

SHA-256: `842567ac7eaf140f0ec589a0aee719a35b11bfaa5ad4108321d24baf1a6257d4`

92 baris; 1 kelas; 7 fungsi/metode termasuk nested.

Kelas: `GatePengembanganTest` L21.
Handler luas: tidak ada.

Impor (termasuk lazy/TYPE_CHECKING): `from __future__ import annotations`; `from pathlib import Path`; `from tools.periksa_gate import coverage_errors, main, target_coverage, tolok_errors`; `import contextlib`; `import io`; `import json`; `import os`; `import sys`; `import tempfile`; `import unittest`.

- L22–30 **`GatePengembanganTest.test_coverage_per_file_dan_laporan_tidak_lengkap`** · kontrol=2, assignment/delete=0, except=0 · Call: `coverage_errors`, `report`, `self.assertEqual`, `self.assertTrue`
- L23–24 **`GatePengembanganTest.test_coverage_per_file_dan_laporan_tidak_lengkap.report`** · kontrol=0, assignment/delete=0, except=0 · Call: tidak ada
- L32–40 **`GatePengembanganTest.test_target_coverage_mencakup_modul_baru`** · kontrol=0, assignment/delete=0, except=0 · Call: `len`, `self.assertEqual`, `self.assertIn`, `set`, `target_coverage`
- L43–46 **`GatePengembanganTest.report`** · kontrol=0, assignment/delete=0, except=0 · Call: tidak ada
- L48–53 **`GatePengembanganTest.test_ambang_performa_ketat`** · kontrol=1, assignment/delete=0, except=0 · Call: `float`, `self.assertEqual`, `self.assertTrue`, `self.report`, `tolok_errors`
- L55–70 **`GatePengembanganTest.test_tolok_gagal_hilang_duplikat_dan_iterasi_invalid`** · kontrol=2, assignment/delete=7, except=0 · Call: `report['tolok'].append`, `self.assertTrue`, `self.report`, `tolok_errors`
- L72–88 **`GatePengembanganTest.test_cli_lulus_dan_gagal`** · kontrol=3, assignment/delete=1, except=0 · Call: `Path`, `contextlib.redirect_stderr`, `contextlib.redirect_stdout`, `io.StringIO`, `json.dumps`, `main`, `path.write_text`, `self.assertEqual`, `self.assertRaises`, `self.report`, `str`, `target_coverage`, `tempfile.TemporaryDirectory`

## `tests/test_idiolek_tutur.py`

SHA-256: `a9fd5862eea511b8e5e8f1e0bb5185e7e1c9173af96de5f5829b10edce0d85c5`

251 baris; 9 kelas; 23 fungsi/metode termasuk nested.

Kelas: `IdiolekPersonaTest` L32, `IdiolekMasukKonteksTest` L64, `SkorKonteksTest` L105, `StrukturDanPartikelTest` L175, `KeterusteranganTest` L230, `_Naluri` L68, `_P` L78, `_Naluri` L90, `_P` L96.
Handler luas: tidak ada.

Impor (termasuk lazy/TYPE_CHECKING): `from __future__ import annotations`; `from pycos.bahasa.tutur import Arg, L1, Node`; `from pycos.bahasa.tutur import GenContext, Leksikon, TuturEngine, konteks_dari_presentasi, muat_leksikon`; `from pycos.bahasa.tutur import L2, Slot`; `from pycos.bahasa.tutur import L3`; `from pycos.bahasa.tutur import Node`; `from pycos.dukungan.sumber import jalur_leksikon`; `from pycos.inti.persona import Persona`; `import dataclasses`; `import os`; `import random`; `import sys`; `import unittest`.

- L28–29 **`_leksikon`** · kontrol=0, assignment/delete=0, except=0 · Call: `jalur_leksikon`, `muat_leksikon`
- L35–43 **`IdiolekPersonaTest.test_bidang_idiolek_bolak_balik`** · kontrol=0, assignment/delete=2, except=0 · Call: `Persona`, `Persona.from_dict`, `p.to_dict`, `q.to_dict`, `self.assertEqual`
- L45–53 **`IdiolekPersonaTest.test_snapshot_lama_tetap_dimuat`** · kontrol=0, assignment/delete=2, except=0 · Call: `Persona.from_dict`, `self.assertEqual`
- L55–61 **`IdiolekPersonaTest.test_nilai_tak_dikenal_ditolak`** · kontrol=3, assignment/delete=0, except=0 · Call: `Persona`, `self.assertRaises`
- L67–87 **`IdiolekMasukKonteksTest.test_bidang_persona_terpetakan`** · kontrol=0, assignment/delete=4, except=0 · Call: `Persona`, `RuntimeError`, `_Naluri`, `_P`, `konteks_dari_presentasi`, `self.assertEqual`
- L75–76 **`IdiolekMasukKonteksTest.test_bidang_persona_terpetakan._Naluri.mood`** · kontrol=0, assignment/delete=0, except=0 · Call: `RuntimeError`
- L89–102 **`IdiolekMasukKonteksTest.test_tanpa_persona_nilai_netral`** · kontrol=0, assignment/delete=3, except=0 · Call: `RuntimeError`, `_Naluri`, `_P`, `konteks_dari_presentasi`, `self.assertEqual`
- L93–94 **`IdiolekMasukKonteksTest.test_tanpa_persona_nilai_netral._Naluri.mood`** · kontrol=0, assignment/delete=0, except=0 · Call: `RuntimeError`
- L108–113 **`SkorKonteksTest.setUp`** · kontrol=0, assignment/delete=3, except=0 · Call: `L2`, `_leksikon`, `random.Random`
- L115–116 **`SkorKonteksTest._slot`** · kontrol=0, assignment/delete=0, except=0 · Call: `self.Slot`
- L118–121 **`SkorKonteksTest._entri`** · kontrol=0, assignment/delete=1, except=0 · Call: `'lema {!r} tidak ada di leksikon'.format`, `self.assertIsNotNone`, `self.leks.ambil`
- L123–130 **`SkorKonteksTest.test_sinonim_fokus_menaikkan_skor`** · kontrol=0, assignment/delete=3, except=0 · Call: `GenContext`, `self._slot`, `self.assertGreater`, `self.l2._skor`
- L132–142 **`SkorKonteksTest.test_antonim_menurunkan_skor_kecuali_act_menolak`** · kontrol=0, assignment/delete=4, except=0 · Call: `GenContext`, `self._slot`, `self.assertGreater`, `self.assertLess`, `self.l2._skor`
- L144–150 **`SkorKonteksTest.test_kata_favorit_menaikkan_skor`** · kontrol=0, assignment/delete=3, except=0 · Call: `GenContext`, `self._slot`, `self.assertGreater`, `self.l2._skor`
- L152–162 **`SkorKonteksTest.test_penalti_riwayat_meluruh`** · kontrol=0, assignment/delete=6, except=0 · Call: `GenContext`, `self._slot`, `self.assertGreater`, `self.assertLess`, `self.l2._skor`
- L164–172 **`SkorKonteksTest.test_slot_mode_isi_boleh_kosong`** · kontrol=0, assignment/delete=3, except=0 · Call: `Arg`, `GenContext`, `L1`, `Node`, `l1.realisasi`, `self.assertIsNotNone`
- L178–180 **`StrukturDanPartikelTest.setUp`** · kontrol=0, assignment/delete=1, except=0 · Call: `TuturEngine`, `jalur_leksikon`, `self.assertTrue`, `self.engine.tersedia`
- L182–187 **`StrukturDanPartikelTest._ucap`** · kontrol=0, assignment/delete=2, except=0 · Call: `GenContext`, `dataclasses.replace`, `self.assertIsNotNone`, `self.engine.ucap`
- L189–196 **`StrukturDanPartikelTest.test_register_netral_tanpa_partikel`** · kontrol=2, assignment/delete=2, except=0 · Call: `'partikel {!r} bocor ke register netral: {!r}'.format`, `range`, `self._ucap`, `self.assertNotIn`, `set`, `teks.replace`, `teks.replace('.', ' ').replace`, `teks.replace('.', ' ').replace('…', ' ').split`
- L198–205 **`StrukturDanPartikelTest.test_register_formal_tetap_formal`** · kontrol=1, assignment/delete=1, except=0 · Call: `range`, `self._ucap`, `self.assertNotIn`, `self.assertTrue`, `teks.strip`
- L207–215 **`StrukturDanPartikelTest.test_sapaan_hanya_pada_act_akrab`** · kontrol=0, assignment/delete=3, except=0 · Call: `akrab.startswith`, `biasa.startswith`, `self._ucap`, `self.assertFalse`, `self.assertTrue`
- L217–227 **`StrukturDanPartikelTest.test_riwayat_tersimpan_dan_dimuat`** · kontrol=1, assignment/delete=2, except=0 · Call: `TuturEngine`, `jalur_leksikon`, `lain.muat_dict`, `lain.to_dict`, `len`, `self._ucap`, `self.assertEqual`, `self.assertLessEqual`, `self.assertRaises`, `self.assertTrue`, `self.engine.to_dict`
- L233–247 **`KeterusteranganTest.test_langsung_tanpa_mungkin`** · kontrol=0, assignment/delete=5, except=0 · Call: `GenContext`, `L3`, `Node`, `_leksikon`, `l3._penanda_aspek_modal`, `random.Random`, `self.assertIn`, `self.assertNotIn`

## `tests/test_integrasi_paket.py`

SHA-256: `e8228b53a22b820659596fd2dc212886c86de70493751a3e8f9fdd511b7d3761`

210 baris; 7 kelas; 15 fungsi/metode termasuk nested.

Kelas: `MulaiCepatREADMETest` L23, `HookOrganikTest` L53, `KognisiLanjutTest` L94, `RefleksiTest` L116, `LingkunganTest` L131, `JalurEksekusiTest` L150, `KoherensiLintasModulTest` L195.
Handler luas: tidak ada.

Impor (termasuk lazy/TYPE_CHECKING): `from __future__ import annotations`; `from pycos import JejakPrediksi, Naluri`; `from pycos import JejakPrediksi, Naluri, Nurani, Organik, TuturEngine`; `from pycos import Lingkungan, Naluri`; `from pycos.inti import Naluri`; `from pycos.inti.naluri import DRIVES`; `from pycos.kontrak import DRIVE_KEYS`; `from pycos.memori import JejakPrediksi`; `from pycos.refleksi import Nurani`; `from pycos.refleksi.nurani import DEFAULT_DRIVES`; `import os`; `import subprocess`; `import sys`; `import unittest`.

- L24–41 **`MulaiCepatREADMETest.test_alur_npc_dan_jejak`** · kontrol=0, assignment/delete=3, except=0 · Call: `JejakPrediksi`, `Naluri`, `jejak.predict`, `jejak.record_experience`, `npc.tick`, `self.assertEqual`, `self.assertIn`
- L43–50 **`MulaiCepatREADMETest.test_nama_modul_lapisan_sesuai_paket`** · kontrol=0, assignment/delete=0, except=0 · Call: `self.assertEqual`
- L56–69 **`HookOrganikTest.test_slot_topologis_lewat_patching`** · kontrol=0, assignment/delete=2, except=0 · Call: `Naluri`, `npc.daftarkan_slot`, `npc.intensitas_topologis`, `npc.kosongkan_slot`, `npc.layak_cabang`, `npc.organik_state`, `self.assertEqual`, `self.assertFalse`, `self.assertIsNone`
- L71–81 **`HookOrganikTest.test_jejak_mengambil_waktu_heterogen`** · kontrol=0, assignment/delete=2, except=0 · Call: `JejakPrediksi`, `jejak.record_experience`, `jejak.waktu_state`, `self.assertEqual`, `self.assertIn`
- L83–91 **`HookOrganikTest.test_nurani_memakai_mandiri_untuk_luka_domain`** · kontrol=0, assignment/delete=1, except=0 · Call: `Nurani`, `nurani.domain_terluka`, `nurani.hancurkan_domain`, `nurani.luka_state`, `nurani.terapkan_domain`, `self.assertEqual`, `self.assertIsNone`
- L95–103 **`KognisiLanjutTest.test_graf_asosiasi_terpasang_ke_naluri`** · kontrol=0, assignment/delete=2, except=0 · Call: `Naluri`, `dict`, `npc.asosiasi`, `npc.enable_asosiasi`, `npc.koaktifkan`, `npc.kognisi_state`, `self.assertIn`, `self.assertTrue`
- L105–113 **`KognisiLanjutTest.test_state_bayes_round_trip`** · kontrol=0, assignment/delete=3, except=0 · Call: `Naluri`, `Naluri.from_dict`, `npc.perbarui_kepercayaan`, `npc.to_dict`, `pulih.to_dict`, `self.assertEqual`, `self.assertIn`
- L117–128 **`RefleksiTest.test_memori_afektif_dan_round_trip`** · kontrol=0, assignment/delete=4, except=0 · Call: `Nurani`, `Nurani.from_dict`, `Nurani.from_dict(data, params=dict(params)).to_dict`, `dict`, `nurani.anticipate`, `nurani.experience`, `nurani.to_dict`, `self.assertEqual`, `self.assertLess`, `self.assertTrue`
- L134–147 **`LingkunganTest.test_npc_bertindak_dan_berpindah_di_dunia`** · kontrol=1, assignment/delete=3, except=0 · Call: `Lingkungan.dari_ascii`, `Naluri`, `all`, `dunia.jalankan`, `dunia.tambah_npc`, `dunia.tambah_objek`, `float`, `len`, `npc.levels.values`, `self.assertEqual`, `self.assertGreater`, `self.assertTrue`
- L153–155 **`JalurEksekusiTest.jalankan`** · kontrol=0, assignment/delete=0, except=0 · Call: `subprocess.run`
- L157–163 **`JalurEksekusiTest.test_modul_lewat_dash_m`** · kontrol=2, assignment/delete=1, except=0 · Call: `self.assertEqual`, `self.jalankan`, `self.subTest`
- L165–171 **`JalurEksekusiTest.test_ringkasan_paket`** · kontrol=2, assignment/delete=1, except=0 · Call: `self.assertEqual`, `self.assertIn`, `self.jalankan`, `self.subTest`
- L173–183 **`JalurEksekusiTest.test_berkas_dijalankan_langsung_tanpa_PYTHONPATH`** · kontrol=2, assignment/delete=2, except=0 · Call: `berkas.split`, `dict`, `os.path.dirname`, `os.path.join`, `self.assertEqual`, `self.subTest`, `subprocess.run`
- L185–192 **`JalurEksekusiTest.test_impor_lewat_PYTHONPATH_tanpa_instalasi`** · kontrol=0, assignment/delete=1, except=0 · Call: `dict`, `hasil.stdout.strip`, `self.assertEqual`, `subprocess.run`
- L198–206 **`KoherensiLintasModulTest.test_daftar_drive_tiga_salinan_sama`** · kontrol=0, assignment/delete=0, except=0 · Call: `self.assertEqual`, `tuple`

## `tests/test_jejak_makna_keadaan.py`

SHA-256: `59464363be47ba286b14977385e7458d27681b19c4224149d3e20bdba3efb837`

151 baris; 3 kelas; 15 fungsi/metode termasuk nested.

Kelas: `JejakBentukTest` L32, `ActKeadaanTest` L56, `PelindungMesinTest` L101.
Handler luas: tidak ada.

Impor (termasuk lazy/TYPE_CHECKING): `from __future__ import annotations`; `from pycos.bahasa.keadaan import ACT_KEADAAN, konteks_keadaan, realisasi, realisasi_daftar`; `from pycos.bahasa.teks import jejak_bentuk, kata_isi`; `from pycos.bahasa.tutur import TuturEngine`; `from pycos.dukungan.sumber import jalur_leksikon`; `from pycos.inti import Naluri`; `import os`; `import sys`; `import unittest`.

- L35–36 **`JejakBentukTest.test_langkah_sama_tidak_mencatat`** · kontrol=0, assignment/delete=0, except=0 · Call: `jejak_bentuk`, `self.assertEqual`
- L38–47 **`JejakBentukTest.test_asal_dipertahankan_pada_rantai`** · kontrol=1, assignment/delete=2, except=0 · Call: `jejak_bentuk`, `len`, `self.assertEqual`
- L49–53 **`JejakBentukTest.test_kata_isi_membuang_kata_fungsi`** · kontrol=0, assignment/delete=1, except=0 · Call: `kata_isi`, `self.assertIn`, `self.assertNotIn`
- L60–62 **`ActKeadaanTest.setUpClass`** · kontrol=0, assignment/delete=1, except=0 · Call: `TuturEngine`, `cls.engine.tersedia`, `jalur_leksikon`
- L64–72 **`ActKeadaanTest.test_act_keadaan_menghasilkan_teks`** · kontrol=2, assignment/delete=1, except=0 · Call: `'act {} tidak menghasilkan ujaran'.format`, `realisasi`, `self.assertNotIn`, `self.assertTrue`, `self.subTest`
- L74–79 **`ActKeadaanTest.test_seed_berbeda_menghasilkan_lebih_dari_satu_varian`** · kontrol=0, assignment/delete=1, except=0 · Call: `len`, `realisasi_daftar`, `self.assertGreater`, `set`
- L81–87 **`ActKeadaanTest.test_isi_masuk_ke_ujaran`** · kontrol=1, assignment/delete=1, except=0 · Call: `'isi yang ada di kepala NPC hilang dari ujaran: {}'.format`, `any`, `realisasi`, `self.assertTrue`, `teks.lower`
- L89–94 **`ActKeadaanTest.test_konteks_menolak_bidang_asing`** · kontrol=0, assignment/delete=1, except=0 · Call: `hasattr`, `konteks_keadaan`, `self.assertEqual`, `self.assertFalse`
- L96–98 **`ActKeadaanTest.test_mesin_absen_mengembalikan_kosong`** · kontrol=0, assignment/delete=0, except=0 · Call: `realisasi`, `realisasi_daftar`, `self.assertEqual`
- L104–111 **`PelindungMesinTest._npc`** · kontrol=0, assignment/delete=1, except=0 · Call: `Naluri`, `n.enable_kesadaran`, `n.enable_presentasi`, `n.set_personality_preset`
- L113–119 **`PelindungMesinTest.test_pidato_gagal_tetap_ada_dan_in_character`** · kontrol=1, assignment/delete=2, except=0 · Call: `p.pidato_gagal`, `self._npc`, `self.assertNotIn`, `self.assertTrue`, `str`, `str(teks).strip`
- L121–125 **`PelindungMesinTest.test_watak_masih_menentukan_act`** · kontrol=0, assignment/delete=2, except=0 · Call: `self._npc`, `self._npc('dingin').presentasi.watak_kegagalan`, `self._npc('paranoid').presentasi.watak_kegagalan`, `self.assertEqual`
- L127–131 **`PelindungMesinTest.test_serap_adversarial_memakai_mesin`** · kontrol=0, assignment/delete=2, except=0 · Call: `p.serap_adversarial`, `self._npc`, `self.assertEqual`, `self.assertTrue`, `str`, `str(serap['balasan']).strip`
- L133–137 **`PelindungMesinTest.test_buffer_manusiawi_tetap_punya_kalimat`** · kontrol=0, assignment/delete=2, except=0 · Call: `p.buffer_manusiawi`, `p.tandai_lupa`, `self._npc`, `self.assertTrue`, `str`, `str(teks).strip`
- L139–147 **`PelindungMesinTest.test_ucap_membawa_jejak_makna`** · kontrol=2, assignment/delete=4, except=0 · Call: `entry.get`, `p.ucap`, `self._npc`, `self.assertEqual`, `self.assertIn`, `self.assertNotIn`

## `tests/test_konektor.py`

SHA-256: `8ec8f66f95745232948585e121b3a097b4f10359e36041c9e82d6285d101ea19`

116 baris; 1 kelas; 7 fungsi/metode termasuk nested.

Kelas: `KonektorTests` L24.
Handler luas: tidak ada.

Impor (termasuk lazy/TYPE_CHECKING): `from __future__ import annotations`; `from copy import deepcopy`; `from pathlib import Path`; `from pycos import konektor`; `from pycos.inti.naluri import Naluri`; `from tempfile import TemporaryDirectory`; `from unittest.mock import patch`; `import io`; `import json`; `import os`; `import subprocess`; `import sys`; `import unittest`.

- L25–29 **`KonektorTests.setUp`** · kontrol=0, assignment/delete=3, except=0 · Call: `Naluri`, `self.npc.to_dict`
- L31–42 **`KonektorTests.test_observasi_terisolasi_dan_dapat_diterapkan`** · kontrol=0, assignment/delete=4, except=0 · Call: `deepcopy`, `konektor.observasi`, `self.assertEqual`, `self.npc.tick`
- L44–55 **`KonektorTests.test_aksi_memakai_mesin_tanpa_mutasi`** · kontrol=0, assignment/delete=4, except=0 · Call: `Naluri.from_dict`, `Naluri.from_dict(self.state).choose_action`, `deepcopy`, `json.dumps`, `json.loads`, `konektor.aksi`, `self.assertEqual`, `self.assertIsNone`
- L57–76 **`KonektorTests.test_input_json_dan_domain_invalid`** · kontrol=6, assignment/delete=1, except=0 · Call: `float`, `konektor.aksi`, `konektor.observasi`, `object`, `self.assertRaises`, `self.subTest`
- L78–81 **`KonektorTests.call_main`** · kontrol=2, assignment/delete=0, except=0 · Call: `io.StringIO`, `json.loads`, `konektor.main`, `output.getvalue`, `patch`, `self.assertEqual`
- L83–100 **`KonektorTests.test_main_sukses_galat_batas_dan_berkas`** · kontrol=3, assignment/delete=3, except=0 · Call: `Path`, `TemporaryDirectory`, `json.dumps`, `patch.object`, `path.unlink`, `path.write_text`, `self.assertEqual`, `self.assertFalse`, `self.assertTrue`, `self.call_main`, `str`
- L102–116 **`KonektorTests.test_cli_subprocess_json_tanpa_shell`** · kontrol=0, assignment/delete=3, except=0 · Call: `json.dumps`, `json.loads`, `self.assertEqual`, `self.assertFalse`, `subprocess.run`

## `tests/test_konstanta_numerik.py`

SHA-256: `5b5209a2fba5f4cfe56abc169a1f95a5c80aa27e279a09a6cb3923458e5f0c85`

141 baris; 1 kelas; 9 fungsi/metode termasuk nested.

Kelas: `KonstantaNumerikTest` L20.
Handler luas: tidak ada.

Impor (termasuk lazy/TYPE_CHECKING): `from __future__ import annotations`; `from pathlib import Path`; `from pycos.bahasa.tutur import _clip`; `from pycos.dukungan.konstanta import DRIVES`; `from pycos.dukungan.numerik import jepit`; `from pycos.dukungan.numerik import jepit_01`; `from pycos.inti.persona import _jepit`; `from pycos.refleksi.ketidaktahuan import _clip`; `import ast`; `import importlib`; `import math`; `import os`; `import random`; `import subprocess`; `import sys`; `import unittest`.

- L21–33 **`KonstantaNumerikTest.test_alias_drive_identik_di_semua_lapisan`** · kontrol=2, assignment/delete=0, except=0 · Call: `getattr`, `importlib.import_module`, `len`, `self.assertEqual`, `self.assertIs`, `self.assertIsInstance`, `self.subTest`, `set`
- L35–44 **`KonstantaNumerikTest.test_tidak_ada_salinan_literal_drive_tersembunyi`** · kontrol=9, assignment/delete=1, except=0 · Call: `(Path(AKAR) / 'pycos').rglob`, `Path`, `all`, `ast.parse`, `ast.walk`, `found.append`, `isinstance`, `len`, `path.read_text`, `path.relative_to`, `self.assertEqual`, `set`, `str`, `str(path.relative_to(Path(AKAR) / 'pycos')).replace`
- L46–54 **`KonstantaNumerikTest.test_konstanta_tidak_memuat_mesin`** · kontrol=0, assignment/delete=1, except=0 · Call: `subprocess.run`
- L56–72 **`KonstantaNumerikTest.test_semua_clamp_netral_cocok_kanonik`** · kontrol=5, assignment/delete=4, except=0 · Call: `float`, `fn`, `getattr`, `importlib.import_module`, `jepit`, `random.Random`, `range`, `rng.uniform`, `self.assertEqual`, `self.subTest`, `values.extend`
- L74–85 **`KonstantaNumerikTest.test_varian_tutur_dipertahankan_bukan_dinetralkan`** · kontrol=4, assignment/delete=0, except=0 · Call: `_clip`, `float`, `jepit`, `self.assertEqual`, `self.assertRaises`
- L87–95 **`KonstantaNumerikTest.test_varian_persona_tetap_ketat_dan_delegate_kanonik`** · kontrol=3, assignment/delete=0, except=0 · Call: `_jepit`, `float`, `jepit`, `math.isfinite`, `self.assertEqual`, `self.assertRaises`, `self.assertTrue`
- L97–105 **`KonstantaNumerikTest.test_varian_view_memakai_default_untuk_semua_non_finite`** · kontrol=3, assignment/delete=0, except=0 · Call: `_clip`, `float`, `jepit_01`, `self.assertEqual`
- L107–122 **`KonstantaNumerikTest.test_seluruh_definisi_clamp_masuk_kontrak`** · kontrol=4, assignment/delete=2, except=0 · Call: `(Path(AKAR) / 'pycos').rglob`, `Path`, `ast.parse`, `ast.walk`, `found.add`, `isinstance`, `path.read_text`, `path.relative_to`, `self.assertEqual`, `set`, `str`, `str(path.relative_to(Path(AKAR) / 'pycos')).replace`
- L124–137 **`KonstantaNumerikTest.test_tiga_modul_mandiri_tetap_terimpor_tanpa_paket`** · kontrol=2, assignment/delete=2, except=0 · Call: `Path`, `self.subTest`, `str`, `subprocess.run`

## `tests/test_kontrak_ketidaktahuan.py`

SHA-256: `f2bc0d604256d081833595eca936504d8791f35faa4c0792d9fd979ddc7d1669`

296 baris; 3 kelas; 16 fungsi/metode termasuk nested.

Kelas: `KontrakStatikDanOperasiTest` L26, `BatasPengetahuanTest` L139, `IntegrasiKetidaktahuanTest` L247.
Handler luas: tidak ada.

Impor (termasuk lazy/TYPE_CHECKING): `from __future__ import annotations`; `from pycos.inti import DRIVES`; `from pycos.inti import Naluri`; `from pycos.inti.persona import PERSONA_CONTOH, Keadaan`; `from pycos.kontrak import DRIVE_KEYS, JANJI, KEBIJAKAN_ABAIKAN, KEBIJAKAN_CATAT, KEBIJAKAN_TOLAK, KEBUTUHAN, ContractViolationError, check_operation, kontrak_operasi, verifikasi_startup, verify_startup`; `from pycos.lingkungan import Lingkungan`; `from pycos.mandiri.organik import ModelKausal`; `from pycos.memori import JejakPrediksi`; `from pycos.refleksi.ketidaktahuan import SIKAP_KETIDAKTAHUAN, STATUS_PENGETAHUAN, batas_pengetahuan, sikap_ketidaktahuan`; `from pycos.refleksi.nurani import PelacakSelaras, nilai_selaras`; `from types import SimpleNamespace`; `import copy`; `import os`; `import sys`; `import unittest`.

- L27–37 **`KontrakStatikDanOperasiTest.test_manifest_startup_dan_kebijakan_host`** · kontrol=0, assignment/delete=1, except=0 · Call: `ContractViolationError`, `self.assertEqual`, `self.assertIn`, `self.assertIsNone`, `str`, `tuple`, `verifikasi_startup`, `verify_startup`
- L39–49 **`KontrakStatikDanOperasiTest.test_semua_pelanggaran_masuk_dilaporkan_dan_state_tetap`** · kontrol=1, assignment/delete=3, except=0 · Call: `SimpleNamespace`, `copy.deepcopy`, `kontrak_operasi`, `len`, `self.assertEqual`, `self.assertIsNotNone`, `self.assertTrue`, `{'apa', 'pelanggar', 'dirugikan'}.issubset`
- L51–72 **`KontrakStatikDanOperasiTest.test_level_fase_postcondition_dan_tambah_npc`** · kontrol=0, assignment/delete=6, except=0 · Call: `Lingkungan.dari_ascii`, `Naluri`, `kontrak_operasi`, `self.assertIsNone`, `world.langkah`, `world.tambah_npc`
- L74–85 **`KontrakStatikDanOperasiTest.test_tick_menerima_fase_masuk_keluar_dan_level_tiga`** · kontrol=0, assignment/delete=3, except=0 · Call: `Naluri`, `kontrak_operasi`, `npc.tick`, `self.assertIsNone`
- L87–94 **`KontrakStatikDanOperasiTest.test_level_nol_tidak_memeriksa_dan_level_invalid_dilaporkan`** · kontrol=1, assignment/delete=1, except=0 · Call: `SimpleNamespace`, `check_operation`, `kontrak_operasi`, `object`, `self.assertIn`, `self.assertIsNone`
- L96–100 **`KontrakStatikDanOperasiTest.test_manifest_memuat_subsistem_keselarasan`** · kontrol=1, assignment/delete=0, except=0 · Call: `self.assertIn`, `self.assertIsNone`, `verifikasi_startup`
- L102–119 **`KontrakStatikDanOperasiTest.test_kontrak_operasi_nilai_selaras_dan_pelacak`** · kontrol=0, assignment/delete=4, except=0 · Call: `Keadaan`, `PelacakSelaras`, `kontrak_operasi`, `nilai_selaras`, `pelacak.catat`, `self.assertIsNone`
- L121–136 **`KontrakStatikDanOperasiTest.test_kontrak_operasi_penilai_melaporkan_input_buruk`** · kontrol=0, assignment/delete=5, except=0 · Call: `SimpleNamespace`, `float`, `kontrak_operasi`, `object`, `self.assertIsNotNone`
- L140–162 **`BatasPengetahuanTest.test_npc_setengah_jadi_dan_di_luar_jangkauan_aman`** · kontrol=0, assignment/delete=4, except=0 · Call: `SimpleNamespace`, `batas_pengetahuan`, `self.assertEqual`, `set`
- L164–183 **`BatasPengetahuanTest.test_memori_episodik_dibaca_dari_indeks_tanpa_mutasi`** · kontrol=0, assignment/delete=6, except=0 · Call: `JejakPrediksi`, `Naluri`, `batas_pengetahuan`, `copy.deepcopy`, `memory.record_experience`, `npc.attach_jejak`, `self.assertEqual`
- L185–199 **`BatasPengetahuanTest.test_afektif_saja_menjadi_merasa_tahu`** · kontrol=0, assignment/delete=3, except=0 · Call: `Naluri`, `batas_pengetahuan`, `dict`, `npc.enable_nurani`, `npc.nurani.experience`, `self.assertEqual`
- L201–217 **`BatasPengetahuanTest.test_wadah_sosial_dan_kausal_dibaca_lokal`** · kontrol=0, assignment/delete=5, except=0 · Call: `ModelKausal`, `Naluri`, `SimpleNamespace`, `batas_pengetahuan`, `graph._tepi`, `npc.nurani.observe_other_belief`, `self.assertEqual`, `self.assertIn`
- L219–244 **`BatasPengetahuanTest.test_sikap_memakai_watak_dan_konteks_tanpa_menyimpan`** · kontrol=0, assignment/delete=1, except=0 · Call: `SimpleNamespace`, `self.assertEqual`, `set`, `sikap_ketidaktahuan`
- L248–263 **`IntegrasiKetidaktahuanTest.test_kesadaran_menambah_kandidat_sementara_dari_konteks_ada`** · kontrol=1, assignment/delete=6, except=0 · Call: `Naluri`, `copy.deepcopy`, `len`, `npc.enable_kesadaran`, `npc.kesadaran._candidates`, `self.assertEqual`, `self.assertIn`, `x.get`
- L265–274 **`IntegrasiKetidaktahuanTest.test_prior_presentasi_aditif_tidak_mengganti_himpunan_act`** · kontrol=0, assignment/delete=5, except=0 · Call: `Naluri`, `presentation._skor_acts`, `self.assertEqual`, `self.assertGreater`, `set`
- L276–292 **`IntegrasiKetidaktahuanTest.test_sikap_bertanya_menaikkan_doubt_nurani_di_tick`** · kontrol=0, assignment/delete=6, except=0 · Call: `Naluri`, `npc.enable_kesadaran`, `npc.tick`, `self.assertGreater`

## `tests/test_kontrak_negatif.py`

SHA-256: `0d28e1654d69957aa061aeae714dc413ccbbb811b1b3093a6a1cbbae3eaa8c28`

188 baris; 1 kelas; 15 fungsi/metode termasuk nested.

Kelas: `KontrakNegatifTest` L19.
Handler luas: tidak ada.

Impor (termasuk lazy/TYPE_CHECKING): `from __future__ import annotations`; `from copy import deepcopy`; `from pycos import kontrak as k`; `from types import SimpleNamespace`; `from unittest.mock import patch`; `import os`; `import sys`; `import unittest`.

- L20–25 **`KontrakNegatifTest.violation`** · kontrol=3, assignment/delete=0, except=0 · Call: `all`, `isinstance`, `report.get`, `self.assertIsInstance`, `self.assertTrue`
- L28–31 **`KontrakNegatifTest.npc`** · kontrol=1, assignment/delete=1, except=0 · Call: `SimpleNamespace`, `dict`, `values.update`
- L33–41 **`KontrakNegatifTest.test_semua_operasi_menolak_pre_dan_post_tidak_sah`** · kontrol=3, assignment/delete=1, except=0 · Call: `k.kontrak_operasi`, `object`, `self.subTest`, `self.violation`
- L43–57 **`KontrakNegatifTest.test_level_alias_dan_validator_gagal_aman`** · kontrol=4, assignment/delete=1, except=0 · Call: `RuntimeError`, `k.check_operation`, `k.kontrak_operasi`, `patch`, `patch.dict`, `self.assertIsNone`, `self.npc`, `self.violation`
- L50–51 **`KontrakNegatifTest.test_level_alias_dan_validator_gagal_aman.rusak`** · kontrol=0, assignment/delete=0, except=0 · Call: `RuntimeError`
- L59–75 **`KontrakNegatifTest.test_tick_domain_counter_dan_generator_tidak_dikonsumsi`** · kontrol=2, assignment/delete=3, except=0 · Call: `events`, `float`, `k.kontrak_operasi`, `self.assertEqual`, `self.assertIsNone`, `self.npc`, `self.violation`, `visited.append`
- L69–71 **`KontrakNegatifTest.test_tick_domain_counter_dan_generator_tidak_dikonsumsi.events`** · kontrol=0, assignment/delete=0, except=0 · Call: `visited.append`
- L77–91 **`KontrakNegatifTest.test_lingkungan_resolusi_npc_dan_identitas_hasil`** · kontrol=2, assignment/delete=3, except=0 · Call: `SimpleNamespace`, `dict`, `k.kontrak_operasi`, `self.assertIsNone`, `self.npc`, `self.violation`
- L93–110 **`KontrakNegatifTest.test_choose_reward_dan_record_batas_kecil`** · kontrol=2, assignment/delete=2, except=0 · Call: `deepcopy`, `float`, `k.kontrak_operasi`, `self.assertEqual`, `self.assertIsNone`, `self.violation`
- L112–131 **`KontrakNegatifTest.test_forecast_pre_post_dan_reinforce`** · kontrol=6, assignment/delete=6, except=0 · Call: `bad_results.append`, `deepcopy`, `float`, `k.kontrak_operasi`, `self.assertIsNone`, `self.subTest`, `self.violation`
- L133–144 **`KontrakNegatifTest.test_ucap_penilai_dan_pelacak`** · kontrol=1, assignment/delete=0, except=0 · Call: `SimpleNamespace`, `k.kontrak_operasi`, `self.assertIsNone`, `self.violation`
- L146–157 **`KontrakNegatifTest.test_lintas_lapis_mismatch_dan_alias_inggris`** · kontrol=0, assignment/delete=4, except=0 · Call: `SimpleNamespace`, `k.ContractViolationError`, `k.check_operation`, `k.kontrak_operasi`, `k.verify_startup`, `self.assertEqual`, `self.assertIsNone`, `self.assertIsNot`, `self.npc`, `self.violation`
- L159–177 **`KontrakNegatifTest.test_manifest_skema_field_dan_operasi_rusak`** · kontrol=2, assignment/delete=5, except=0 · Call: `float`, `k.verifikasi_startup`, `manifest`, `self.assertIsNone`, `self.violation`
- L160–164 **`KontrakNegatifTest.test_manifest_skema_field_dan_operasi_rusak.manifest`** · kontrol=0, assignment/delete=2, except=0 · Call: `k.verifikasi_startup`
- L179–184 **`KontrakNegatifTest.test_manifest_dependency_hilang_dan_rusak`** · kontrol=1, assignment/delete=0, except=0 · Call: `k.verifikasi_startup`, `self.assertIsNone`, `self.violation`

## `tests/test_lingkungan.py`

SHA-256: `2d61907934c783f2e5c851e108d37ef06efbdc1b9111ded5f8e6e714a8c5c19b`

696 baris; 17 kelas; 69 fungsi/metode termasuk nested.

Kelas: `StubNPC` L27, `PetaTest` L64, `ObjekDuniaTest` L111, `PendaftaranTest` L136, `GerakTest` L173, `ObjekAksiTest` L242, `BahayaDanCuacaTest` L327, `SatiasiTest` L399, `InteraksiTest` L448, `ObservasiTest` L495, `SerialisasiTest` L529, `IntegrasiNaluriTest` L576, `JalurEksekusiTest` L664, `KonstantaTest` L683, `Pasif` L430, `RewardRusak` L633, `Pasif` L650.
Handler luas: tidak ada.

Impor (termasuk lazy/TYPE_CHECKING): `from __future__ import annotations`; `from pycos.inti import Naluri`; `from pycos.lingkungan import ARAH, JENIS_DAPAT_DIAMBIL, Badan, Lingkungan, ObjekDunia, Peta, peta_contoh`; `from pycos.memori import JejakPrediksi`; `import os`; `import subprocess`; `import sys`; `import unittest`.

- L34–41 **`StubNPC.__init__`** · kontrol=1, assignment/delete=6, except=0 · Call: `list`
- L43–46 **`StubNPC.choose_action`** · kontrol=0, assignment/delete=1, except=0 · Call: `self.aksi_dipilih.append`, `self.dipilih.pop`
- L48–50 **`StubNPC.tick`** · kontrol=2, assignment/delete=0, except=0 · Call: `bool`, `dict`, `self.peristiwa.append`
- L52–55 **`StubNPC.reward_for`** · kontrol=2, assignment/delete=2, except=0 · Call: `(deltas or {}).values`, `float`, `sum`
- L57–61 **`StubNPC.events`** · kontrol=4, assignment/delete=1, except=0 · Call: `e.get`
- L65–71 **`PetaTest.test_dari_ascii_membangun_ukuran_dan_medan`** · kontrol=0, assignment/delete=1, except=0 · Call: `Peta.dari_ascii`, `peta.jenis`, `self.assertEqual`
- L73–81 **`PetaTest.test_medan_menentukan_bisa_dilewati`** · kontrol=0, assignment/delete=1, except=0 · Call: `Peta.dari_ascii`, `peta.bisa_dilewati`, `self.assertFalse`, `self.assertTrue`
- L83–86 **`PetaTest.test_biaya_medan_urut`** · kontrol=0, assignment/delete=1, except=0 · Call: `Peta.dari_ascii`, `peta.biaya`, `self.assertLess`
- L88–91 **`PetaTest.test_simbol_tak_dikenal_dianggap_tanah`** · kontrol=0, assignment/delete=1, except=0 · Call: `Peta.dari_ascii`, `peta.bisa_dilewati`, `peta.jenis`, `self.assertEqual`, `self.assertTrue`
- L93–95 **`PetaTest.test_baris_tidak_seragam_ditolak`** · kontrol=1, assignment/delete=0, except=0 · Call: `Peta.dari_ascii`, `self.assertRaises`
- L97–102 **`PetaTest.test_petak_urut_dan_roundtrip`** · kontrol=0, assignment/delete=2, except=0 · Call: `Peta.dari_ascii`, `Peta.from_dict`, `peta.petak`, `peta.to_dict`, `pulih.to_dict`, `self.assertEqual`
- L104–108 **`PetaTest.test_peta_contoh_konsisten`** · kontrol=0, assignment/delete=1, except=0 · Call: `peta.petak_bisa_dilewati`, `peta_contoh`, `self.assertEqual`, `self.assertTrue`
- L112–116 **`ObjekDuniaTest.test_efek_standar_per_jenis`** · kontrol=0, assignment/delete=2, except=0 · Call: `ObjekDunia`, `obj.efek`, `self.assertGreater`, `self.assertTrue`
- L118–123 **`ObjekDuniaTest.test_atribut_menimpa_efek_dan_pesan`** · kontrol=0, assignment/delete=2, except=0 · Call: `ObjekDunia`, `obj.efek`, `self.assertEqual`
- L125–127 **`ObjekDuniaTest.test_tempat_aman_tidak_sekali_pakai`** · kontrol=0, assignment/delete=0, except=0 · Call: `ObjekDunia`, `ObjekDunia('rumah', 'tempat_aman', (0, 0)).efek`, `self.assertFalse`
- L129–133 **`ObjekDuniaTest.test_roundtrip_objek`** · kontrol=0, assignment/delete=2, except=0 · Call: `ObjekDunia`, `ObjekDunia.from_dict`, `obj.to_dict`, `pulih.to_dict`, `self.assertEqual`, `self.assertTrue`
- L137–138 **`PendaftaranTest.setUp`** · kontrol=0, assignment/delete=1, except=0 · Call: `Lingkungan.dari_ascii`
- L140–142 **`PendaftaranTest.test_tambah_npc_di_luar_peta_ditolak`** · kontrol=1, assignment/delete=0, except=0 · Call: `StubNPC`, `self.assertRaises`, `self.dunia.tambah_npc`
- L144–147 **`PendaftaranTest.test_tambah_npc_di_medan_terhalang_ditolak`** · kontrol=1, assignment/delete=1, except=0 · Call: `Lingkungan.dari_ascii`, `StubNPC`, `dunia.tambah_npc`, `self.assertRaises`
- L149–152 **`PendaftaranTest.test_nama_ganda_ditolak`** · kontrol=1, assignment/delete=0, except=0 · Call: `StubNPC`, `self.assertRaises`, `self.dunia.tambah_npc`
- L154–156 **`PendaftaranTest.test_objek_di_luar_peta_ditolak`** · kontrol=1, assignment/delete=0, except=0 · Call: `self.assertRaises`, `self.dunia.tambah_objek`
- L158–161 **`PendaftaranTest.test_objek_tanpa_nama_mendapat_nomor_unik`** · kontrol=0, assignment/delete=2, except=0 · Call: `self.assertNotEqual`, `self.dunia.tambah_objek`
- L163–170 **`PendaftaranTest.test_nama_badan_urut_dan_npc_mengembalikan_objek`** · kontrol=0, assignment/delete=2, except=0 · Call: `StubNPC`, `self.assertEqual`, `self.assertIs`, `self.assertIsInstance`, `self.assertIsNone`, `self.dunia.nama_badan`, `self.dunia.npc`, `self.dunia.tambah_npc`
- L174–188 **`GerakTest.test_bergerak_ke_petak_baru_memberi_bonus_eksplorasi`** · kontrol=0, assignment/delete=3, except=0 · Call: `Lingkungan.dari_ascii`, `StubNPC`, `dunia.langkah_semua`, `dunia.tambah_npc`, `npc.events`, `self.assertEqual`, `self.assertGreater`, `self.assertTrue`
- L190–198 **`GerakTest.test_petak_yang_sudah_dikunjungi_tanpa_bonus`** · kontrol=1, assignment/delete=2, except=0 · Call: `Lingkungan.dari_ascii`, `StubNPC`, `dunia.langkah_semua`, `dunia.tambah_npc`, `range`, `self.assertEqual`, `self.assertNotIn`
- L200–209 **`GerakTest.test_dinding_menghalangi`** · kontrol=1, assignment/delete=2, except=0 · Call: `Lingkungan.dari_ascii`, `StubNPC`, `dunia.aksi_tersedia`, `dunia.tambah_npc`, `dunia.terapkan`, `self.assertEqual`, `self.assertFalse`, `self.assertIn`, `self.assertNotIn`
- L211–218 **`GerakTest.test_batas_peta_dan_medan_air_ditolak`** · kontrol=1, assignment/delete=3, except=0 · Call: `Lingkungan.dari_ascii`, `StubNPC`, `dunia.aksi_tersedia`, `dunia.tambah_npc`, `dunia.terapkan`, `self.assertFalse`, `self.assertIn`, `self.assertNotIn`
- L220–228 **`GerakTest.test_petak_ditempati_npc_lain_ditolak`** · kontrol=1, assignment/delete=2, except=0 · Call: `Lingkungan.dari_ascii`, `StubNPC`, `dunia.aksi_tersedia`, `dunia.tambah_npc`, `dunia.terapkan`, `self.assertEqual`, `self.assertFalse`, `self.assertNotIn`
- L230–239 **`GerakTest.test_biaya_jalan_lebih_kecil_dari_rumput`** · kontrol=0, assignment/delete=5, except=0 · Call: `Lingkungan.dari_ascii`, `StubNPC`, `dunia.langkah`, `dunia.tambah_npc`, `self.assertLess`
- L243–254 **`ObjekAksiTest.test_ambil_masuk_inventaris_dan_pakai_menghabiskannya`** · kontrol=0, assignment/delete=3, except=0 · Call: `Lingkungan.dari_ascii`, `StubNPC`, `dunia.langkah_semua`, `dunia.tambah_npc`, `dunia.tambah_objek`, `self.assertEqual`, `self.assertFalse`, `self.assertGreater`, `self.assertTrue`
- L256–262 **`ObjekAksiTest.test_makanan_hanya_bisa_diambil_di_petak_yang_sama`** · kontrol=0, assignment/delete=2, except=0 · Call: `Lingkungan.dari_ascii`, `StubNPC`, `dunia.tambah_npc`, `dunia.tambah_objek`, `dunia.terapkan`, `self.assertFalse`, `self.assertIn`
- L264–273 **`ObjekAksiTest.test_dekati_bergerak_menuju_objek_jauh`** · kontrol=1, assignment/delete=3, except=0 · Call: `Lingkungan.dari_ascii`, `StubNPC`, `dunia.aksi_tersedia`, `dunia.langkah_semua`, `dunia.tambah_npc`, `dunia.tambah_objek`, `self.assertEqual`, `self.assertIn`, `tuple`
- L275–286 **`ObjekAksiTest.test_amati_mengungkap_objek_tersembunyi`** · kontrol=1, assignment/delete=3, except=0 · Call: `Lingkungan.dari_ascii`, `StubNPC`, `dunia.langkah_semua`, `dunia.observasi`, `dunia.tambah_npc`, `dunia.tambah_objek`, `self.assertEqual`, `self.assertFalse`
- L288–298 **`ObjekAksiTest.test_tempat_aman_memberi_berlindung_yang_melebur`** · kontrol=0, assignment/delete=2, except=0 · Call: `Lingkungan.dari_ascii`, `StubNPC`, `dunia.langkah_semua`, `dunia.tambah_npc`, `dunia.tambah_objek`, `self.assertEqual`
- L300–308 **`ObjekAksiTest.test_menjauh_meninggalkan_bahaya`** · kontrol=0, assignment/delete=3, except=0 · Call: `Lingkungan.dari_ascii`, `StubNPC`, `dunia.langkah_semua`, `dunia.tambah_npc`, `dunia.tambah_objek`, `self.assertEqual`, `self.assertGreater`, `self.assertTrue`
- L310–315 **`ObjekAksiTest.test_aksi_tak_dikenal_gagal_dengan_catat`** · kontrol=0, assignment/delete=2, except=0 · Call: `Lingkungan.dari_ascii`, `StubNPC`, `dunia.tambah_npc`, `dunia.terapkan`, `self.assertEqual`, `self.assertFalse`
- L317–324 **`ObjekAksiTest.test_jenis_yang_tidak_bisa_diambil_tidak_ditawarkan`** · kontrol=1, assignment/delete=2, except=0 · Call: `Lingkungan.dari_ascii`, `StubNPC`, `dunia.aksi_tersedia`, `dunia.tambah_npc`, `dunia.tambah_objek`, `self.assertIn`, `self.assertNotIn`
- L328–337 **`BahayaDanCuacaTest.test_paparan_bahaya_menurunkan_keamanan_dan_terhitung`** · kontrol=1, assignment/delete=4, except=0 · Call: `Lingkungan.dari_ascii`, `StubNPC`, `any`, `dunia.langkah_semua`, `dunia.tambah_npc`, `dunia.tambah_objek`, `float`, `npc.events`, `self.assertEqual`, `self.assertIn`, `self.assertTrue`
- L339–350 **`BahayaDanCuacaTest.test_berlindung_mengurangi_paparan`** · kontrol=1, assignment/delete=3, except=0 · Call: `Lingkungan.dari_ascii`, `StubNPC`, `dunia.langkah_semua`, `dunia.tambah_npc`, `dunia.tambah_objek`, `e.get`, `float`, `npc.events`, `self.assertGreater`, `self.assertTrue`, `str`
- L352–359 **`BahayaDanCuacaTest.test_malam_memberi_peristiwa_keamanan`** · kontrol=2, assignment/delete=3, except=0 · Call: `Lingkungan.dari_ascii`, `StubNPC`, `any`, `dunia.fase`, `dunia.langkah_semua`, `dunia.tambah_npc`, `npc.events`, `self.assertEqual`, `self.assertTrue`
- L361–372 **`BahayaDanCuacaTest.test_jam_maju_dan_fase_berubah`** · kontrol=2, assignment/delete=1, except=0 · Call: `Lingkungan.dari_ascii`, `StubNPC`, `dunia.fase`, `dunia.langkah_semua`, `dunia.tambah_npc`, `range`, `self.assertEqual`
- L374–386 **`BahayaDanCuacaTest.test_cuaca_deterministik_dan_nilai_sah`** · kontrol=3, assignment/delete=2, except=0 · Call: `Lingkungan.dari_ascii`, `StubNPC`, `any`, `dunia.langkah_semua`, `dunia.tambah_npc`, `jejak_cuaca`, `range`, `self.assertEqual`, `self.assertIn`, `self.assertTrue`
- L375–378 **`BahayaDanCuacaTest.test_cuaca_deterministik_dan_nilai_sah.jejak_cuaca`** · kontrol=1, assignment/delete=1, except=0 · Call: `Lingkungan.dari_ascii`, `StubNPC`, `dunia.langkah_semua`, `dunia.tambah_npc`, `range`
- L388–396 **`BahayaDanCuacaTest.test_hujan_memberi_peristiwa_energi`** · kontrol=1, assignment/delete=5, except=0 · Call: `Lingkungan.dari_ascii`, `StubNPC`, `dunia.langkah_semua`, `dunia.tambah_npc`, `npc.events`, `self.assertIn`
- L400–407 **`SatiasiTest.test_aksi_yang_diulang_melemah`** · kontrol=1, assignment/delete=3, except=0 · Call: `Lingkungan.dari_ascii`, `StubNPC`, `dunia.langkah_semua`, `dunia.tambah_npc`, `range`, `self.assertGreater`
- L409–417 **`SatiasiTest.test_kandidat_ikut_melemah_sehingga_npc_melihat_efek_nyata`** · kontrol=2, assignment/delete=4, except=0 · Call: `Lingkungan.dari_ascii`, `StubNPC`, `dunia.aksi_tersedia`, `dunia.langkah_semua`, `dunia.tambah_npc`, `self.assertLess`
- L419–427 **`SatiasiTest.test_aksi_lain_pulih_perlahan`** · kontrol=1, assignment/delete=3, except=0 · Call: `Lingkungan.dari_ascii`, `StubNPC`, `dunia.langkah_semua`, `dunia.tambah_npc`, `range`, `self.assertGreater`
- L429–438 **`SatiasiTest.test_kebijakan_defensif_dipakai_tanpa_choose_action`** · kontrol=0, assignment/delete=4, except=0 · Call: `Lingkungan.dari_ascii`, `Pasif`, `dunia.pilih_aksi`, `dunia.tambah_npc`, `self.assertEqual`, `self.assertIn`
- L440–445 **`SatiasiTest.test_pilihan_npc_yang_tidak_valid_jatuh_ke_defensif`** · kontrol=0, assignment/delete=3, except=0 · Call: `Lingkungan.dari_ascii`, `StubNPC`, `dunia.pilih_aksi`, `dunia.tambah_npc`, `self.assertEqual`
- L449–464 **`InteraksiTest.test_sapa_mengantre_peristiwa_untuk_sasaran`** · kontrol=1, assignment/delete=5, except=0 · Call: `Lingkungan.dari_ascii`, `StubNPC`, `b.events`, `dunia.langkah`, `dunia.tambah_npc`, `e.get`, `float`, `len`, `self.assertEqual`, `self.assertGreater`, `self.assertIn`, `self.assertTrue`, `str`
- L466–472 **`InteraksiTest.test_sapa_terlalu_jauh_gagal`** · kontrol=0, assignment/delete=2, except=0 · Call: `Lingkungan.dari_ascii`, `StubNPC`, `dunia.tambah_npc`, `dunia.terapkan`, `self.assertFalse`, `self.assertIn`
- L474–479 **`InteraksiTest.test_hampiri_mendekati_npc_lain`** · kontrol=0, assignment/delete=1, except=0 · Call: `Lingkungan.dari_ascii`, `StubNPC`, `dunia.langkah`, `dunia.tambah_npc`, `self.assertEqual`
- L481–492 **`InteraksiTest.test_berinteraksi_dipanggil_pada_naluri`** · kontrol=0, assignment/delete=4, except=0 · Call: `Lingkungan.dari_ascii`, `Naluri`, `dunia.tambah_npc`, `dunia.terapkan`, `self.assertGreater`, `self.assertIn`, `self.assertTrue`
- L496–507 **`ObservasiTest.test_observasi_memuat_objek_dan_ringkasan`** · kontrol=1, assignment/delete=2, except=0 · Call: `Lingkungan.dari_ascii`, `StubNPC`, `dunia.observasi`, `dunia.tambah_npc`, `dunia.tambah_objek`, `len`, `self.assertEqual`, `self.assertIn`
- L509–515 **`ObservasiTest.test_observasi_memuat_npc_lain_urut_jarak`** · kontrol=1, assignment/delete=2, except=0 · Call: `Lingkungan.dari_ascii`, `StubNPC`, `dunia.observasi`, `dunia.tambah_npc`, `self.assertEqual`
- L517–526 **`ObservasiTest.test_render_dan_lihat_sekitar`** · kontrol=0, assignment/delete=3, except=0 · Call: `Lingkungan.dari_ascii`, `StubNPC`, `dunia.lihat_sekitar`, `dunia.render`, `dunia.tambah_npc`, `dunia.tambah_objek`, `len`, `potong.splitlines`, `self.assertEqual`, `self.assertIn`
- L530–548 **`SerialisasiTest.test_roundtrip_idempoten_dan_state_dipulihkan`** · kontrol=1, assignment/delete=3, except=0 · Call: `Lingkungan.dari_ascii`, `Lingkungan.from_dict`, `StubNPC`, `dunia.langkah_semua`, `dunia.tambah_npc`, `dunia.tambah_objek`, `dunia.to_dict`, `pulih.to_dict`, `range`, `self.assertEqual`
- L550–556 **`SerialisasiTest.test_npc_dapat_disambungkan_ulang`** · kontrol=0, assignment/delete=3, except=0 · Call: `Lingkungan.dari_ascii`, `Lingkungan.from_dict`, `StubNPC`, `dunia.tambah_npc`, `dunia.to_dict`, `pulih.npc`, `self.assertIs`, `self.assertIsNone`
- L558–565 **`SerialisasiTest.test_state_kognitif_tidak_ikut_diserialisasi`** · kontrol=0, assignment/delete=2, except=0 · Call: `Lingkungan.dari_ascii`, `Naluri`, `dunia.tambah_npc`, `dunia.to_dict`, `self.assertNotIn`, `str`
- L567–573 **`SerialisasiTest.test_antrean_ikut_dipulihkan`** · kontrol=0, assignment/delete=2, except=0 · Call: `Lingkungan.dari_ascii`, `Lingkungan.from_dict`, `StubNPC`, `dunia.langkah`, `dunia.tambah_npc`, `dunia.to_dict`, `len`, `self.assertEqual`
- L577–611 **`IntegrasiNaluriTest.test_jalankan_dengan_naluri_dan_jejak`** · kontrol=6, assignment/delete=7, except=0 · Call: `JejakPrediksi`, `Lingkungan`, `Naluri`, `all`, `any`, `b['aksi'].startswith`, `badan.jejak.performance_report`, `dunia.jalankan`, `dunia.nama_badan`, `dunia.peta.bisa_dilewati`, `dunia.peta.didalam`, `dunia.tambah_npc`, `dunia.tambah_objek`, `enumerate`, `float`, `len`, `levels.values`, `peta_contoh`, `self.assertEqual`, `self.assertGreater`, `self.assertGreaterEqual`, `self.assertTrue`
- L613–630 **`IntegrasiNaluriTest.test_jejak_memprediksi_setelah_pengalaman_pertama`** · kontrol=1, assignment/delete=4, except=0 · Call: `JejakPrediksi`, `Lingkungan.dari_ascii`, `Naluri`, `dunia.konteks`, `dunia.langkah_semua`, `dunia.tambah_npc`, `dunia.tambah_objek`, `jejak.predict`, `range`, `self.assertIn`
- L632–646 **`IntegrasiNaluriTest.test_reward_gagal_dicatat_dan_dunia_tetap_berjalan`** · kontrol=1, assignment/delete=4, except=0 · Call: `Lingkungan.dari_ascii`, `RewardRusak`, `RuntimeError`, `any`, `dunia.langkah_semua`, `dunia.tambah_npc`, `entri.get`, `len`, `self.assertEqual`, `self.assertTrue`
- L634–635 **`IntegrasiNaluriTest.test_reward_gagal_dicatat_dan_dunia_tetap_berjalan.RewardRusak.reward_for`** · kontrol=0, assignment/delete=0, except=0 · Call: `RuntimeError`
- L648–661 **`IntegrasiNaluriTest.test_lingkungan_tidak_menuntut_naluri`** · kontrol=1, assignment/delete=4, except=0 · Call: `Lingkungan.dari_ascii`, `Pasif`, `all`, `dunia.jalankan`, `dunia.tambah_npc`, `len`, `self.assertEqual`, `self.assertIsNone`, `self.assertTrue`
- L665–671 **`JalurEksekusiTest.test_modul_dijalankan_lewat_dash_m`** · kontrol=0, assignment/delete=1, except=0 · Call: `self.assertEqual`, `self.assertIn`, `subprocess.run`
- L673–680 **`JalurEksekusiTest.test_berkas_dijalankan_langsung_tanpa_PYTHONPATH`** · kontrol=0, assignment/delete=2, except=0 · Call: `dict`, `os.path.dirname`, `os.path.join`, `self.assertEqual`, `self.assertIn`, `subprocess.run`
- L684–688 **`KonstantaTest.test_arah_lengkap_dan_tidak_nol`** · kontrol=1, assignment/delete=0, except=0 · Call: `ARAH.items`, `len`, `self.assertEqual`, `self.assertTrue`, `type`
- L690–692 **`KonstantaTest.test_jenis_dapat_diambil_bukan_bahaya`** · kontrol=0, assignment/delete=0, except=0 · Call: `self.assertNotIn`

## `tests/test_organik_lanjutan.py`

SHA-256: `95e04e1fe9998d8d74a0096415f5acbe189a86dbd441902159c2dfaa27656020`

401 baris; 18 kelas; 27 fungsi/metode termasuk nested.

Kelas: `SafeMethodPatchTest` L27, `ResiduTest` L72, `IntrusiTest` L105, `SelisihSelfTest` L122, `DetakInternalTest` L140, `KoherensiParalelTest` L160, `GejalaMurniOrdeNolTest` L183, `TopologiSlotTest` L251, `LukaDomainTest` L265, `BatasIdentitasTest` L280, `WaktuHeterogenTest` L293, `PenolakanTuturTest` L309, `ApersepsiTest` L322, `InvensiTest` L336, `ModelKausalTest` L356, `PerencanaOutcomeTokenTest` L380, `Target` L29, `Target` L44.
Handler luas: tidak ada.

Impor (termasuk lazy/TYPE_CHECKING): `from __future__ import annotations`; `from pycos.dukungan.patching import PatchConflictError, install_methods, wrap_method`; `from pycos.inti import Naluri`; `from pycos.mandiri import Apersepsi`; `from pycos.mandiri import BatasIdentitas`; `from pycos.mandiri import Invensi`; `from pycos.mandiri import KALIMAT_ADA_SESUATU, KALIMAT_TAK_BERNAMA, DetakInternal, Gejala, GejalaMurni, Organik, Residu`; `from pycos.mandiri import LukaDomain`; `from pycos.mandiri import ModelKausal`; `from pycos.mandiri import ModelKausal, Perencana`; `from pycos.mandiri import PenolakanTutur`; `from pycos.mandiri import TopologiSlot`; `from pycos.mandiri import WaktuHeterogen`; `from pycos.memori import JejakPrediksi`; `import os`; `import random`; `import sys`; `import unittest`.

- L28–41 **`SafeMethodPatchTest.test_wrapper_menjaga_chain_descriptor_dan_idempoten`** · kontrol=0, assignment/delete=0, except=0 · Call: `'{}:{}'.format`, `Target.load`, `original`, `self.assertEqual`, `self.assertFalse`, `self.assertTrue`, `wrap_method`
- L31–32 **`SafeMethodPatchTest.test_wrapper_menjaga_chain_descriptor_dan_idempoten.Target.load`** · kontrol=0, assignment/delete=0, except=0 · Call: `'{}:{}'.format`
- L34–35 **`SafeMethodPatchTest.test_wrapper_menjaga_chain_descriptor_dan_idempoten.add_suffix`** · kontrol=0, assignment/delete=0, except=0 · Call: `original`
- L43–57 **`SafeMethodPatchTest.test_benturan_batch_tidak_meninggalkan_pemasangan_sebagian`** · kontrol=1, assignment/delete=0, except=0 · Call: `Target`, `Target().occupied`, `hasattr`, `install_methods`, `self.assertEqual`, `self.assertFalse`, `self.assertRaises`
- L45–46 **`SafeMethodPatchTest.test_benturan_batch_tidak_meninggalkan_pemasangan_sebagian.Target.occupied`** · kontrol=0, assignment/delete=0, except=0 · Call: tidak ada
- L59–69 **`SafeMethodPatchTest.test_integrasi_bayes_tidak_memutasi_metode_kelas_per_instance`** · kontrol=0, assignment/delete=3, except=0 · Call: `JejakPrediksi`, `JejakPrediksi.from_dict`, `jejak._pasang_bayes`, `jejak.kepercayaan`, `jejak.perbarui_kepercayaan`, `jejak.tetapkan_kepercayaan`, `jejak.to_dict`, `pulih.kepercayaan`, `self.assertAlmostEqual`, `self.assertIs`, `self.assertTrue`
- L73–95 **`ResiduTest.test_residu_mengubah_aturan_dan_tidak_decay`** · kontrol=1, assignment/delete=6, except=0 · Call: `Residu`, `r.ambang_dimodifikasi`, `r.daftar`, `r.langit_dimodifikasi`, `r.state`, `r.tambal`, `r.tekanan`, `range`, `self.assertAlmostEqual`, `self.assertEqual`, `self.assertFalse`, `self.assertGreater`, `self.assertIn`, `self.assertLess`, `self.assertTrue`
- L97–102 **`ResiduTest.test_residu_terintegrasi_ke_emosi`** · kontrol=0, assignment/delete=1, except=0 · Call: `Naluri`, `n._emosi_naikkan`, `n._emosi_weight_bias`, `n.daftarkan_residu`, `self.assertEqual`, `self.assertLess`
- L106–119 **`IntrusiTest.test_intrusi_menyampel_affective_tanpa_attend`** · kontrol=0, assignment/delete=3, except=0 · Call: `Naluri`, `n.daftarkan_residu`, `n.kesadaran.paksa_intrusi`, `n.kesadaran.workspace_report`, `n.nurani.seed_affective`, `self.assertEqual`, `self.assertIsNotNone`, `self.assertTrue`
- L123–137 **`SelisihSelfTest.test_deviasi_berulang_menaikkan_disorientasi_identitas`** · kontrol=1, assignment/delete=3, except=0 · Call: `Naluri`, `n.daftarkan_residu`, `n.presentasi.ucap`, `n.selisih_self_state`, `range`, `self.assertGreater`, `self.assertGreaterEqual`, `self.assertIn`
- L141–157 **`DetakInternalTest.test_jam_fraksional_dan_ucapan_terpotong_saat_ini`** · kontrol=0, assignment/delete=4, except=0 · Call: `DetakInternal`, `Naluri`, `hasil['teks'].endswith`, `jam.maju`, `jam.paksa`, `n.interupsi_internal_state`, `n.paksa_interupsi`, `n.presentasi.ucap`, `self.assertEqual`, `self.assertTrue`
- L161–180 **`KoherensiParalelTest.test_hanya_kontradiksi_tak_disadari_menghukum`** · kontrol=0, assignment/delete=5, except=0 · Call: `Naluri`, `biasa.kesadaran.hold_belief`, `paralel.delta`, `paralel.kesadaran.hold_belief`, `paralel.pegang_dua`, `paralel.tanpa_resolusi`, `self.assertEqual`, `self.assertLess`, `self.assertTrue`
- L186–198 **`GejalaMurniOrdeNolTest.test_primitif_hanya_empat_properti`** · kontrol=0, assignment/delete=2, except=0 · Call: `GejalaMurni`, `g.properti_terlarang`, `g.state`, `self.assertEqual`, `self.assertGreater`, `self.assertIsNone`, `self.assertTrue`
- L200–204 **`GejalaMurniOrdeNolTest.test_polaritas_none_bukan_gagal_dan_boleh_menyusul`** · kontrol=0, assignment/delete=1, except=0 · Call: `GejalaMurni`, `g.perbarui`, `self.assertAlmostEqual`, `self.assertEqual`
- L206–220 **`GejalaMurniOrdeNolTest.test_pipeline_berulang_menjadi_kategori_penuh`** · kontrol=0, assignment/delete=2, except=0 · Call: `Gejala`, `ge.jenis_hint`, `ge.kategori_penuh`, `ge.muncul`, `ge.proses`, `len`, `self.assertEqual`, `self.assertIn`, `self.assertTrue`
- L222–229 **`GejalaMurniOrdeNolTest.test_pemudaran_meniggalkan_bekas_bukan_entri_aktif`** · kontrol=0, assignment/delete=2, except=0 · Call: `Gejala`, `ge.aktif`, `ge.bekas`, `ge.muncul`, `ge.proses`, `self.assertEqual`, `self.assertTrue`
- L231–237 **`GejalaMurniOrdeNolTest.test_klaim_menghapus_kemurnian`** · kontrol=0, assignment/delete=2, except=0 · Call: `Gejala`, `ge.aktif`, `ge.klaim`, `ge.muncul`, `ge.terklaim`, `self.assertEqual`
- L239–248 **`GejalaMurniOrdeNolTest.test_roundtrip_wadah_membawa_gejala_dan_bekas`** · kontrol=1, assignment/delete=2, except=0 · Call: `Organik`, `Organik.from_dict`, `o.gejala.muncul`, `o.gejala.proses`, `o.residu.bekas`, `o.to_dict`, `o2.gejala.aktif`, `o2.residu.bekas_state`, `o2.residu.tekanan`, `self.assertEqual`
- L252–262 **`TopologiSlotTest.test_slot_kosong_membuat_cabang_mustahil_dan_roundtrip`** · kontrol=0, assignment/delete=2, except=0 · Call: `TopologiSlot`, `TopologiSlot.from_dict`, `salinan.to_dict`, `self.assertEqual`, `self.assertIsNone`, `slot.cabang_mustahil`, `slot.daftar`, `slot.intensitas`, `slot.kosongkan`, `slot.to_dict`
- L266–277 **`LukaDomainTest.test_lubang_nonpermanen_dapat_ditambal_bukan_permanen`** · kontrol=0, assignment/delete=1, except=0 · Call: `LukaDomain`, `luka.lukai`, `luka.tambal`, `luka.terapkan`, `self.assertEqual`, `self.assertFalse`, `self.assertIsNone`, `self.assertTrue`
- L281–290 **`BatasIdentitasTest.test_identitas_menolak_dan_membatasi_emosi`** · kontrol=0, assignment/delete=1, except=0 · Call: `BatasIdentitas`, `batas.izinkan`, `batas.tetapkan`, `self.assertEqual`
- L294–306 **`WaktuHeterogenTest.test_recall_koreksi_skala_dan_roundtrip`** · kontrol=0, assignment/delete=1, except=0 · Call: `WaktuHeterogen`, `WaktuHeterogen.from_dict`, `WaktuHeterogen.from_dict(waktu.to_dict()).to_dict`, `self.assertAlmostEqual`, `self.assertEqual`, `waktu.bobot`, `waktu.daftar`, `waktu.diingat`, `waktu.dikoreksi_salah`, `waktu.half_life`, `waktu.skala_subjektif`, `waktu.to_dict`
- L310–319 **`PenolakanTuturTest.test_takut_mengubah_bentuk_tutur_secara_reproduksibel`** · kontrol=0, assignment/delete=2, except=0 · Call: `PenolakanTutur`, `mekanisme.bentuk`, `mekanisme.jenis`, `mekanisme.kelayakan`, `random.Random`, `self.assertEqual`, `self.assertLess`
- L323–333 **`ApersepsiTest.test_tekanan_tinggi_tanpa_kategori_menghasilkan_tanpa_nama`** · kontrol=0, assignment/delete=2, except=0 · Call: `Apersepsi`, `apersepsi.amati`, `self.assertEqual`, `self.assertIsNone`
- L337–353 **`InvensiTest.test_lahirkan_menghasilkan_usulan_deterministik`** · kontrol=2, assignment/delete=2, except=0 · Call: `Invensi`, `Invensi(seed=5).lahirkan`, `all`, `self.assertEqual`, `self.assertTrue`
- L357–377 **`ModelKausalTest.test_pelajari_penjelasan_counterfactual_blame_dan_roundtrip`** · kontrol=1, assignment/delete=5, except=0 · Call: `ModelKausal`, `ModelKausal.from_dict`, `model.blame`, `model.counterfactual`, `model.jelaskan`, `model.pelajari`, `model.to_dict`, `pulih.jelaskan`, `self.assertEqual`, `self.assertIn`, `self.assertTrue`
- L381–397 **`PerencanaOutcomeTokenTest.test_frasa_multi_kata_menutupi_prasyarat_dan_rencana_lengkap`** · kontrol=0, assignment/delete=4, except=0 · Call: `ModelKausal`, `Perencana`, `domain._tepi`, `perencana.rancang`, `self.assertEqual`, `self.assertTrue`

## `tests/test_perbaikan_analisis.py`

SHA-256: `2e1f0ac31ec86298b2e668fdd4e6d28e098370c921805a38f036e01163f55b89`

1824 baris; 44 kelas; 183 fungsi/metode termasuk nested.

Kelas: `NumerikTest` L26, `ValidasiBatasMasukNalurTest` L46, `PerilakuNalurTest` L93, `JejakPrediksiTest` L132, `PatchingTest` L147, `LeksikonDanCacheTest` L198, `DuniaTest` L231, `DiagnostikTest` L250, `TolokTest` L263, `PeriksaTest` L281, `SalienceReproducibilityTest` L320, `DemoKognisiTest` L340, `ShimIntegrasiTest` L362, `AuditPersonaTest` L385, `AuditTrenTest` L402, `AuditSnapshotTest` L425, `AuditRollbackPatchTest` L449, `AuditKognisiTest` L491, `AuditCliTest` L526, `AuditGrafPersistensiTest` L553, `AuditPenyebaranTest` L591, `AuditResumeKognisiTest` L624, `AuditGeneratorTest` L672, `RekomendasiStateTest` L719, `RekomendasiFormatTest` L760, `RekomendasiAtomicTest` L800, `RekomendasiSerapTest` L857, `RekomendasiAuditScopeTest` L893, `RekomendasiEventTest` L913, `RekomendasiParameterTest` L959, `RekomendasiNamaTest` L1001, `RekomendasiDiagnostikTest` L1025, `RekomendasiProfilTest` L1102, `RekomendasiRetrievalTest` L1224, `RekomendasiKawananLazyTest` L1324, `RekomendasiBatasMemoriTest` L1449, `RekomendasiVariasiTuturTest` L1558, `RekomendasiLeksikonImpakTest` L1636, `RekomendasiEvaluasiEksternalTest` L1697, `Target` L151, `Kelas` L173, `Menolak` L453, `Target` L462, `Target` L1031.
Handler luas: tidak ada.

Impor (termasuk lazy/TYPE_CHECKING): `from __future__ import annotations`; `from copy import deepcopy`; `from dataclasses import replace`; `from pycos.__main__ import jalankan_selaras`; `from pycos.bahasa.tutur import GenContext, TuturEngine`; `from pycos.bahasa.tutur import L2, Slot, GenContext, Leksikon`; `from pycos.bahasa.tutur import Leksikon, L2, Slot, GenContext`; `from pycos.bahasa.tutur import Leksikon, TuturEngine`; `from pycos.bahasa.tutur import TuturEngine, kosongkan_cache_leksikon`; `from pycos.dukungan import diagnostik`; `from pycos.dukungan import leksikon`; `from pycos.dukungan import patching`; `from pycos.dukungan import periksa`; `from pycos.dukungan import tolok`; `from pycos.dukungan import validasi_state as state`; `from pycos.dukungan.batas_memori import BATAS`; `from pycos.dukungan.batas_memori import BATAS, batas`; `from pycos.dukungan.batas_memori import BATAS, pangkas`; `from pycos.dukungan.leksikon import periksa`; `from pycos.dukungan.leksikon import perluas`; `from pycos.dukungan.leksikon import validasi_entri`; `from pycos.dukungan.numerik import float_hingga, jepit, jepit_01, jepit_drive`; `from pycos.dukungan.parameter import PARAM_SPEC`; `from pycos.dukungan.parameter import periksa_params`; `from pycos.dukungan.patching import optional_module`; `from pycos.dukungan.patching import wrap_method`; `from pycos.dukungan.persistensi import simpan_json`; `from pycos.dukungan.sumber import jalur_leksikon`; `from pycos.dukungan.tolok import _tolok_to_dict_simpan`; `from pycos.dukungan.validasi_state import FORMAT_TERBARU, validasi_state`; `from pycos.inti import KawananNPC`; `from pycos.inti import Naluri`; `from pycos.inti import Naluri, KawananNPC`; `from pycos.inti import naluri`; `from pycos.inti.naluri import DEFAULTS`; `from pycos.inti.naluri import DEFAULTS, Naluri`; `from pycos.inti.naluri import LEXICON`; `from pycos.inti.naluri import Naluri`; `from pycos.inti.naluri import Naluri, LEXICON_EN, TAG_LEXICON_EN`; `from pycos.inti.naluri import Naluri, _naluri_kog_step`; `from pycos.inti.naluri import Naluri, demo_kognisi`; `from pycos.inti.naluri import _MAKS_LOSSES`; `from pycos.inti.persona import Keadaan, Persona`; `from pycos.inti.persona import Persona`; `from pycos.lingkungan import dunia`; `from pycos.lingkungan.dunia import Lingkungan`; `from pycos.lingkungan.dunia import _potong`; `from pycos.mandiri import GrafAsosiasi`; `from pycos.mandiri.kognisi_lanjut import EversiTD`; `from pycos.mandiri.kognisi_lanjut import GrafAsosiasi`; `from pycos.mandiri.kognisi_lanjut import KognisiLanjut`; `from pycos.mandiri.kognisi_lanjut import jepit_drive as lokal`; `from pycos.mandiri.organik import _kclip`; `from pycos.memori import JejakPrediksi`; `from pycos.memori import jejak_prediksi as modul`; `from pycos.memori.jejak_prediksi import JejakPrediksi`; `from pycos.refleksi import Nurani`; `from pycos.refleksi.nurani import ContohLabel`; `from pycos.refleksi.nurani import ContohLabel, laporan_kalibrasi`; `from pycos.refleksi.nurani import Laporan, PelacakSelaras`; `from pycos.refleksi.nurani import PelacakSelaras`; `from pycos.refleksi.nurani import contoh_dari_dict, muat_korpus`; `from pycos.refleksi.nurani import laporan_kalibrasi`; `from pycos.refleksi.nurani import nilai_selaras`; `from types import SimpleNamespace`; `from unittest.mock import Mock`; `from unittest.mock import patch`; `import ast`; `import contextlib`; `import io`; `import json`; `import math`; `import os`; `import random`; `import subprocess`; `import sys`; `import tempfile`; `import unittest`.

- L27–31 **`NumerikTest.test_jepit_nan_menjadi_nol_lalu_dijepit`** · kontrol=0, assignment/delete=0, except=0 · Call: `float`, `jepit`, `self.assertEqual`
- L33–37 **`NumerikTest.test_jepit_01_dan_drive`** · kontrol=0, assignment/delete=0, except=0 · Call: `float`, `jepit_01`, `jepit_drive`, `self.assertEqual`
- L39–43 **`NumerikTest.test_float_hingga_menolak_non_finite_dan_tak_numerik`** · kontrol=2, assignment/delete=0, except=0 · Call: `float`, `float_hingga`, `self.assertEqual`, `self.assertRaises`, `self.subTest`
- L47–49 **`ValidasiBatasMasukNalurTest.setUp`** · kontrol=0, assignment/delete=1, except=0 · Call: tidak ada
- L51–53 **`ValidasiBatasMasukNalurTest.test_initial_levels_kunci_asing_ditolak`** · kontrol=1, assignment/delete=0, except=0 · Call: `self.Naluri`, `self.assertRaisesRegex`
- L55–59 **`ValidasiBatasMasukNalurTest.test_initial_levels_nan_dan_luar_rentang_ditolak`** · kontrol=2, assignment/delete=0, except=0 · Call: `float`, `self.Naluri`, `self.assertRaisesRegex`
- L61–63 **`ValidasiBatasMasukNalurTest.test_weights_kunci_asing_ditolak`** · kontrol=1, assignment/delete=0, except=0 · Call: `self.Naluri`, `self.assertRaisesRegex`
- L65–70 **`ValidasiBatasMasukNalurTest.test_delta_non_finite_ditolak`** · kontrol=2, assignment/delete=1, except=0 · Call: `all`, `float`, `math.isfinite`, `npc.levels.values`, `npc.tick`, `self.Naluri`, `self.assertRaises`, `self.assertTrue`
- L72–77 **`ValidasiBatasMasukNalurTest.test_reward_for_kunci_asing_dan_nan_ditolak`** · kontrol=2, assignment/delete=1, except=0 · Call: `float`, `npc.reward_for`, `self.Naluri`, `self.assertRaises`
- L79–83 **`ValidasiBatasMasukNalurTest.test_choose_action_menolak_kandidat_tanpa_nama`** · kontrol=2, assignment/delete=1, except=0 · Call: `npc.choose_action`, `self.Naluri`, `self.assertRaises`, `self.subTest`
- L85–90 **`ValidasiBatasMasukNalurTest.test_choose_action_mencatat_kunci_effects_salah`** · kontrol=0, assignment/delete=2, except=0 · Call: `diagnostik.kosongkan`, `diagnostik.laporan`, `npc.choose_action`, `self.Naluri`, `self.assertIn`
- L94–96 **`PerilakuNalurTest.setUp`** · kontrol=0, assignment/delete=1, except=0 · Call: tidak ada
- L98–106 **`PerilakuNalurTest.test_determinisme_dengan_seed_sama`** · kontrol=1, assignment/delete=3, except=0 · Call: `a.tick`, `b.tick`, `range`, `self.Naluri`, `self.assertEqual`
- L108–113 **`PerilakuNalurTest.test_losses_dibatasi`** · kontrol=1, assignment/delete=1, except=0 · Call: `len`, `npc.kesadaran.face_death`, `range`, `self.Naluri`, `self.assertLessEqual`
- L115–123 **`PerilakuNalurTest.test_mimpi_tertunda_dikonsumsi_saat_bangun`** · kontrol=0, assignment/delete=4, except=0 · Call: `kes._dream_pending.append`, `kes.enabled`, `kes.wake`, `laporan.get`, `self.Naluri`, `self.assertEqual`, `self.assertIn`, `self.assertTrue`
- L125–129 **`PerilakuNalurTest.test_round_trip_setelah_perbaikan`** · kontrol=0, assignment/delete=2, except=0 · Call: `json.dumps`, `json.loads`, `npc.tick`, `npc.to_dict`, `self.Naluri`, `self.Naluri.from_dict`, `self.assertEqual`
- L133–138 **`JejakPrediksiTest.test_future_simulation_menghasilkan_peringkat`** · kontrol=0, assignment/delete=2, except=0 · Call: `JejakPrediksi`, `jejak.future_simulation`, `self.assertEqual`, `self.assertIn`
- L140–144 **`JejakPrediksiTest.test_rank_actions_menerima_mapping`** · kontrol=1, assignment/delete=2, except=0 · Call: `JejakPrediksi`, `jejak.rank_actions`, `self.assertEqual`
- L148–169 **`PatchingTest.test_install_methods_batch_konflik_tidak_menandai_fungsi`** · kontrol=1, assignment/delete=0, except=0 · Call: `hasattr`, `patching._patch_ids`, `patching.install_methods`, `self.assertEqual`, `self.assertFalse`, `self.assertRaises`, `tuple`
- L152–153 **`PatchingTest.test_install_methods_batch_konflik_tidak_menandai_fungsi.Target.ada`** · kontrol=0, assignment/delete=0, except=0 · Call: tidak ada
- L155–156 **`PatchingTest.test_install_methods_batch_konflik_tidak_menandai_fungsi.baru`** · kontrol=0, assignment/delete=0, except=0 · Call: tidak ada
- L158–159 **`PatchingTest.test_install_methods_batch_konflik_tidak_menandai_fungsi.bentrok`** · kontrol=0, assignment/delete=0, except=0 · Call: tidak ada
- L161–162 **`PatchingTest.test_install_methods_batch_konflik_tidak_menandai_fungsi.ada_lain`** · kontrol=0, assignment/delete=0, except=0 · Call: tidak ada
- L171–178 **`PatchingTest.test_pesan_galat_memuat_nama_lengkap`** · kontrol=0, assignment/delete=1, except=0 · Call: `patching._conflict`, `self.assertIn`, `str`
- L180–182 **`PatchingTest.test_optional_module_absen_menjadi_none`** · kontrol=0, assignment/delete=0, except=0 · Call: `optional_module`, `self.assertIsNone`
- L184–195 **`PatchingTest.test_optional_module_dependensi_hilang_dilempar_ulang`** · kontrol=4, assignment/delete=0, except=0 · Call: `f.write`, `open`, `optional_module`, `os.path.join`, `self.assertRaises`, `sys.modules.pop`, `sys.path.insert`, `sys.path.remove`, `tempfile.TemporaryDirectory`
- L200–202 **`LeksikonDanCacheTest.setUpClass`** · kontrol=0, assignment/delete=1, except=0 · Call: `jalur_leksikon`
- L204–212 **`LeksikonDanCacheTest.test_cache_mengembalikan_objek_yang_sama`** · kontrol=0, assignment/delete=3, except=0 · Call: `TuturEngine`, `kosongkan_cache_leksikon`, `self.assertIs`, `self.assertIsNot`
- L214–228 **`LeksikonDanCacheTest.test_polisem_menyimpan_semua_sense`** · kontrol=4, assignment/delete=5, except=0 · Call: `TuturEngine`, `leks._senses.items`, `leks.kelas_dari`, `len`, `s.get`, `self.assertIn`, `self.assertIsInstance`, `self.assertTrue`
- L232–235 **`DuniaTest.test_potong_nan_tidak_menjadi_batas_atas`** · kontrol=0, assignment/delete=0, except=0 · Call: `_potong`, `float`, `self.assertEqual`
- L237–247 **`DuniaTest.test_menerima_action_cost_dari_signature`** · kontrol=0, assignment/delete=0, except=0 · Call: `dunia._menerima_action_cost`, `self.assertFalse`, `self.assertTrue`
- L240–241 **`DuniaTest.test_menerima_action_cost_dari_signature.tick_dengan_kwarg`** · kontrol=0, assignment/delete=0, except=0 · Call: tidak ada
- L243–244 **`DuniaTest.test_menerima_action_cost_dari_signature.tick_positional`** · kontrol=0, assignment/delete=0, except=0 · Call: tidak ada
- L251–257 **`DiagnostikTest.test_catat_dan_laporan`** · kontrol=0, assignment/delete=1, except=0 · Call: `diagnostik.catat`, `diagnostik.kosongkan`, `diagnostik.laporan`, `self.assertEqual`
- L259–260 **`DiagnostikTest.test_catat_tidak_pernah_melempar`** · kontrol=0, assignment/delete=0, except=0 · Call: `diagnostik.catat`, `object`
- L264–273 **`TolokTest.test_tolok_json_dan_kode_keluar`** · kontrol=2, assignment/delete=4, except=0 · Call: `contextlib.redirect_stdout`, `io.StringIO`, `json.loads`, `keluaran.getvalue`, `self.assertEqual`, `self.assertTrue`, `tolok.main`
- L275–278 **`TolokTest.test_ulang_harus_positif`** · kontrol=1, assignment/delete=0, except=0 · Call: `contextlib.redirect_stderr`, `io.StringIO`, `self.assertRaises`, `tolok.main`
- L282–289 **`PeriksaTest.test_periksa_semua_lulus`** · kontrol=2, assignment/delete=3, except=0 · Call: `all`, `contextlib.redirect_stdout`, `io.StringIO`, `json.loads`, `keluaran.getvalue`, `periksa.main_periksa`, `self.assertEqual`, `self.assertTrue`
- L291–299 **`PeriksaTest.test_periksa_memuat_cek_wajib_lintas_subsistem`** · kontrol=1, assignment/delete=2, except=0 · Call: `self.assertTrue`, `wajib.issubset`
- L301–310 **`PeriksaTest.test_periksa_gagal_memberi_kode_1`** · kontrol=2, assignment/delete=4, except=0 · Call: `contextlib.redirect_stdout`, `io.StringIO`, `periksa.main_periksa`, `self.assertEqual`
- L312–317 **`PeriksaTest.test_python_m_pycos_periksa`** · kontrol=0, assignment/delete=1, except=0 · Call: `self.assertEqual`, `self.assertIn`, `subprocess.run`
- L321–330 **`SalienceReproducibilityTest.test_now_diinjeksi_membuat_recency_dapat_diulang`** · kontrol=0, assignment/delete=4, except=0 · Call: `Naluri`, `npc.salience`, `self.assertEqual`, `self.assertGreater`
- L332–337 **`SalienceReproducibilityTest.test_now_tidak_berhingga_ditolak`** · kontrol=1, assignment/delete=0, except=0 · Call: `Naluri`, `Naluri(rng_seed=15).salience`, `float`, `self.assertRaisesRegex`
- L341–359 **`DemoKognisiTest.test_jejak_dan_setpoint_dipakai_dalam_demo`** · kontrol=2, assignment/delete=3, except=0 · Call: `asli`, `contextlib.redirect_stdout`, `demo_kognisi`, `dipasang.append`, `io.StringIO`, `keluaran.getvalue`, `len`, `patch.object`, `self.assertEqual`, `self.assertIn`
- L348–350 **`DemoKognisiTest.test_jejak_dan_setpoint_dipakai_dalam_demo.pantau`** · kontrol=0, assignment/delete=0, except=0 · Call: `asli`, `dipasang.append`
- L365–382 **`ShimIntegrasiTest.test_shim_yang_gagal_dicatat_di_diagnostik`** · kontrol=1, assignment/delete=3, except=0 · Call: `json.loads`, `per_sumber.get`, `self.assertEqual`, `self.assertGreaterEqual`, `subprocess.run`
- L386–391 **`AuditPersonaTest.test_pantangan_string_ditolak_di_kedua_jalur`** · kontrol=2, assignment/delete=0, except=0 · Call: `Persona`, `Persona.from_dict`, `buat`, `self.assertRaisesRegex`
- L393–399 **`AuditPersonaTest.test_pantangan_daftar_dinormalisasi_tanpa_mutasi`** · kontrol=0, assignment/delete=2, except=0 · Call: `Persona.from_dict`, `persona.to_dict`, `self.assertEqual`
- L403–407 **`AuditTrenTest.test_ambang_tidak_berhingga_ditolak`** · kontrol=2, assignment/delete=0, except=0 · Call: `PelacakSelaras`, `float`, `self.assertRaises`, `self.subTest`
- L409–422 **`AuditTrenTest.test_ambang_nol_membedakan_datar_naik_turun`** · kontrol=3, assignment/delete=2, except=0 · Call: `Keadaan`, `PelacakSelaras`, `Persona`, `nilai_selaras`, `pelacak.catat`, `pelacak.tren`, `replace`, `self.assertEqual`, `self.assertIsInstance`, `self.subTest`
- L426–428 **`AuditSnapshotTest.setUp`** · kontrol=0, assignment/delete=0, except=0 · Call: `diagnostik.kosongkan`, `self.addCleanup`
- L430–438 **`AuditSnapshotTest.test_detail_laporan_tidak_membocorkan_referensi`** · kontrol=0, assignment/delete=4, except=0 · Call: `diagnostik.catat`, `diagnostik.laporan`, `laporan['terakhir'].clear`, `self.assertEqual`
- L440–446 **`AuditSnapshotTest.test_snapshot_tetap_tersedia_setelah_buffer_dikosongkan`** · kontrol=0, assignment/delete=1, except=0 · Call: `diagnostik.catat`, `diagnostik.kosongkan`, `diagnostik.laporan`, `self.assertEqual`
- L450–488 **`AuditRollbackPatchTest.test_metaclass_gagal_memulihkan_slot_dan_semua_tag`** · kontrol=2, assignment/delete=2, except=0 · Call: `RuntimeError`, `hasattr`, `patching._patch_ids`, `patching.install_methods`, `self.assertEqual`, `self.assertFalse`, `self.assertIs`, `self.assertRaisesRegex`, `super`, `super().__setattr__`
- L454–457 **`AuditRollbackPatchTest.test_metaclass_gagal_memulihkan_slot_dan_semua_tag.Menolak.__setattr__`** · kontrol=1, assignment/delete=0, except=0 · Call: `RuntimeError`, `super`, `super().__setattr__`
- L459–460 **`AuditRollbackPatchTest.test_metaclass_gagal_memulihkan_slot_dan_semua_tag.ada`** · kontrol=0, assignment/delete=0, except=0 · Call: tidak ada
- L469–470 **`AuditRollbackPatchTest.test_metaclass_gagal_memulihkan_slot_dan_semua_tag.baru`** · kontrol=0, assignment/delete=0, except=0 · Call: tidak ada
- L472–473 **`AuditRollbackPatchTest.test_metaclass_gagal_memulihkan_slot_dan_semua_tag.gagal`** · kontrol=0, assignment/delete=0, except=0 · Call: tidak ada
- L492–501 **`AuditKognisiTest.test_salinan_clamp_netral_konsisten_dengan_kanonik`** · kontrol=4, assignment/delete=0, except=0 · Call: `float`, `fungsi`, `jepit`, `self.assertEqual`, `self.subTest`
- L503–515 **`AuditKognisiTest.test_eversi_json_mempertahankan_konfigurasi_dan_lanjutan`** · kontrol=0, assignment/delete=2, except=0 · Call: `EversiTD`, `EversiTD.from_dict`, `awal.eversi_param`, `awal.reward_intrinsik`, `awal.to_dict`, `awal.update`, `json.dumps`, `json.loads`, `pulih.eversi_param`, `pulih.reward_intrinsik`, `pulih.to_dict`, `pulih.update`, `self.assertEqual`
- L517–523 **`AuditKognisiTest.test_eversi_save_lama_tetap_dapat_dibaca`** · kontrol=0, assignment/delete=1, except=0 · Call: `EversiTD.from_dict`, `pulih.nilai`, `self.assertEqual`, `self.assertIsNone`
- L527–529 **`AuditCliTest.jalankan`** · kontrol=0, assignment/delete=0, except=0 · Call: `subprocess.run`
- L531–539 **`AuditCliTest.test_argumen_asing_dan_mode_bercampur_ditolak`** · kontrol=2, assignment/delete=1, except=0 · Call: `self.assertEqual`, `self.assertIn`, `self.assertNotIn`, `self.jalankan`, `self.subTest`
- L541–550 **`AuditCliTest.test_help_peta_dan_json_periksa_tetap_berfungsi`** · kontrol=0, assignment/delete=3, except=0 · Call: `json.loads`, `self.assertEqual`, `self.assertIn`, `self.assertTrue`, `self.jalankan`
- L554–565 **`AuditGrafPersistensiTest.test_konfigurasi_dan_pembelajaran_berikutnya_tetap`** · kontrol=0, assignment/delete=2, except=0 · Call: `GrafAsosiasi`, `GrafAsosiasi.from_dict`, `awal.koaktifkan`, `awal.luruh`, `awal.to_dict`, `json.dumps`, `json.loads`, `pulih.koaktifkan`, `pulih.luruh`, `pulih.to_dict`, `self.assertEqual`
- L567–574 **`AuditGrafPersistensiTest.test_nama_dengan_pemisah_tidak_menggabungkan_tepi`** · kontrol=0, assignment/delete=2, except=0 · Call: `GrafAsosiasi`, `GrafAsosiasi.from_dict`, `awal.koaktifkan`, `awal.to_dict`, `json.dumps`, `json.loads`, `len`, `self.assertEqual`
- L576–588 **`AuditGrafPersistensiTest.test_save_lama_dan_snapshot_log_terisolasi`** · kontrol=0, assignment/delete=7, except=0 · Call: `GrafAsosiasi.from_dict`, `graf.bobot`, `graf.to_dict`, `self.assertEqual`
- L592–596 **`AuditPenyebaranTest.graf`** · kontrol=0, assignment/delete=2, except=0 · Call: `GrafAsosiasi`
- L598–604 **`AuditPenyebaranTest.test_jumlah_hop_dan_atenuasi`** · kontrol=0, assignment/delete=1, except=0 · Call: `self.assertAlmostEqual`, `self.assertEqual`, `self.graf`, `self.graf().aktifkan`, `set`
- L606–613 **`AuditPenyebaranTest.test_siklus_tidak_memompa_aktivasi`** · kontrol=0, assignment/delete=3, except=0 · Call: `graf.aktifkan`, `self.assertAlmostEqual`, `self.assertEqual`, `self.graf`
- L615–621 **`AuditPenyebaranTest.test_ambang_dan_urutan_tepi_tidak_mengubah_hasil`** · kontrol=0, assignment/delete=4, except=0 · Call: `balik.aktifkan`, `dict`, `graf.aktifkan`, `graf.edge.items`, `list`, `reversed`, `self.assertEqual`, `self.assertNotIn`, `self.graf`
- L625–641 **`AuditResumeKognisiTest.test_rng_dan_gaussian_cache_melanjutkan_drift_setelah_json`** · kontrol=1, assignment/delete=6, except=0 · Call: `KognisiLanjut`, `KognisiLanjut(seed=19).aktifkan`, `KognisiLanjut.from_dict`, `__import__`, `__import__('random').getstate`, `awal.langkah`, `awal.rng.getstate`, `awal.to_dict`, `dict`, `json.dumps`, `json.loads`, `pulih.langkah`, `pulih.rng.getstate`, `range`, `self.assertEqual`, `self.assertIsNotNone`
- L643–652 **`AuditResumeKognisiTest.test_rng_save_lama_dan_state_rusak`** · kontrol=2, assignment/delete=1, except=0 · Call: `KognisiLanjut`, `KognisiLanjut().rng.getstate`, `KognisiLanjut().to_dict`, `KognisiLanjut.from_dict`, `KognisiLanjut.from_dict({}).rng.getstate`, `float`, `self.assertEqual`, `self.assertRaises`, `self.subTest`
- L654–669 **`AuditResumeKognisiTest.test_transisi_td_naluri_tidak_hilang_saat_load`** · kontrol=0, assignment/delete=3, except=0 · Call: `Naluri`, `Naluri.from_dict`, `Naluri.from_json`, `_naluri_kog_step`, `awal.enable_eversi`, `awal.enable_latent_drift`, `awal.kognisi_state`, `awal.tick`, `awal.to_dict`, `awal.to_json`, `data.pop`, `pulih.kognisi_state`, `self.assertEqual`, `self.assertIsNone`
- L673–676 **`AuditGeneratorTest.jalankan`** · kontrol=0, assignment/delete=0, except=0 · Call: `os.path.join`, `subprocess.run`
- L678–694 **`AuditGeneratorTest.test_semua_berkas_termasuk_init_demo_private_dan_nested`** · kontrol=5, assignment/delete=4, except=0 · Call: `'## {}'.format`, `f.read`, `f.write`, `open`, `os.makedirs`, `os.path.join`, `self.assertEqual`, `self.assertIn`, `self.jalankan`, `sources.items`, `tempfile.TemporaryDirectory`
- L696–704 **`AuditGeneratorTest.test_check_mendeteksi_source_berubah`** · kontrol=2, assignment/delete=1, except=0 · Call: `f.write`, `open`, `os.path.join`, `self.assertEqual`, `self.jalankan`, `tempfile.TemporaryDirectory`
- L706–716 **`AuditGeneratorTest.test_syntax_error_tidak_dilewati_dan_dilaporkan_semua`** · kontrol=3, assignment/delete=2, except=0 · Call: `f.write`, `open`, `os.path.exists`, `os.path.join`, `self.assertEqual`, `self.assertFalse`, `self.assertIn`, `self.jalankan`, `tempfile.TemporaryDirectory`
- L720–728 **`RekomendasiStateTest.test_domain_naluri_ditolak_dengan_nama_field`** · kontrol=2, assignment/delete=0, except=0 · Call: `Naluri.from_dict`, `self.assertRaisesRegex`, `self.subTest`
- L730–740 **`RekomendasiStateTest.test_nurani_jejak_dan_pemilik_state_lain_memakai_gate`** · kontrol=2, assignment/delete=2, except=0 · Call: `KawananNPC`, `Naluri`, `loader`, `self.assertRaisesRegex`, `self.subTest`
- L742–750 **`RekomendasiStateTest.test_invalid_nested_ditolak_sebelum_fallback_atau_mutasi`** · kontrol=2, assignment/delete=2, except=0 · Call: `Naluri`, `Naluri.from_dict`, `n.kesadaran.from_dict`, `n.kesadaran.to_dict`, `self.assertEqual`, `self.assertRaisesRegex`
- L752–757 **`RekomendasiStateTest.test_roundtrip_dan_field_lama_tetap_diterima`** · kontrol=0, assignment/delete=1, except=0 · Call: `Naluri`, `Naluri.from_dict`, `Naluri.from_json`, `n.tick`, `n.to_json`, `self.assertEqual`
- L761–769 **`RekomendasiFormatTest.test_migrasi_naluri_3_ke_4_tanpa_mutasi_input`** · kontrol=0, assignment/delete=3, except=0 · Call: `Naluri.from_dict`, `Naluri.migrate`, `json.dumps`, `self.assertEqual`
- L771–779 **`RekomendasiFormatTest.test_semua_format_baru_tidak_dikenal_ditolak`** · kontrol=3, assignment/delete=1, except=0 · Call: `FORMAT_TERBARU.items`, `GrafAsosiasi.from_dict`, `fmt.split`, `self.assertRaisesRegex`, `self.subTest`, `validasi_state`
- L781–787 **`RekomendasiFormatTest.test_format_nested_tidak_disembunyikan_fallback`** · kontrol=2, assignment/delete=0, except=0 · Call: `KawananNPC.from_dict`, `Naluri.from_dict`, `self.assertEqual`, `self.assertRaisesRegex`
- L789–797 **`RekomendasiFormatTest.test_registry_mendukung_rantai_migrasi`** · kontrol=1, assignment/delete=1, except=0 · Call: `dict`, `patch.dict`, `self.assertEqual`, `state.migrasi`
- L792–793 **`RekomendasiFormatTest.test_registry_mendukung_rantai_migrasi.ke_3`** · kontrol=0, assignment/delete=0, except=0 · Call: `dict`
- L801–819 **`RekomendasiAtomicTest.test_gagal_replace_menjaga_save_lama_dan_membersihkan_temp`** · kontrol=8, assignment/delete=3, except=0 · Call: `JejakPrediksi`, `KawananNPC`, `Naluri`, `OSError`, `f.read`, `obj.save`, `open`, `os.listdir`, `os.path.join`, `patch`, `self.assertEqual`, `self.assertRaises`, `self.subTest`, `tempfile.TemporaryDirectory`, `type`, `type(obj).load`
- L821–842 **`RekomendasiAtomicTest.test_checksum_salah_dan_legacy`** · kontrol=7, assignment/delete=5, except=0 · Call: `Naluri`, `Naluri.load`, `f.write`, `json.dump`, `json.load`, `n.save`, `n.to_json`, `open`, `os.path.join`, `self.assertEqual`, `self.assertIn`, `self.assertRaisesRegex`, `tempfile.TemporaryDirectory`
- L844–854 **`RekomendasiAtomicTest.test_serialisasi_gagal_tidak_memotong_target`** · kontrol=4, assignment/delete=1, except=0 · Call: `f.read`, `f.write`, `float`, `open`, `os.listdir`, `os.path.join`, `self.assertEqual`, `self.assertRaises`, `simpan_json`, `tempfile.TemporaryDirectory`
- L858–872 **`RekomendasiSerapTest.test_serap_mempertahankan_identitas_dan_konfigurasi`** · kontrol=2, assignment/delete=3, except=0 · Call: `KawananNPC`, `KawananNPC().serap`, `Naluri`, `dict`, `kawanan.position_of`, `kawanan.serap`, `kawanan.tambah_npc`, `n.delta`, `self.assertEqual`, `self.assertIs`, `self.assertRaises`
- L874–884 **`RekomendasiSerapTest.test_objek_pada_flag_ditolak_dan_gagal_posisi_tidak_mendaftar`** · kontrol=2, assignment/delete=2, except=0 · Call: `KawananNPC`, `Naluri`, `float`, `getattr`, `k.serap`, `k.tambah`, `self.assertEqual`, `self.assertIsNone`, `self.assertRaises`, `self.assertRaisesRegex`
- L886–890 **`RekomendasiSerapTest.test_posisional_legacy_mendapat_deprecation`** · kontrol=1, assignment/delete=1, except=0 · Call: `KawananNPC`, `KawananNPC().tambah`, `self.assertEqual`, `self.assertWarns`
- L894–911 **`RekomendasiAuditScopeTest.test_dependency_dan_build_tidak_mengubah_check`** · kontrol=4, assignment/delete=6, except=0 · Call: `f.write`, `open`, `os.mkdir`, `os.path.join`, `self.assertEqual`, `subprocess.run`, `tempfile.TemporaryDirectory`
- L914–915 **`RekomendasiEventTest.setUp`** · kontrol=0, assignment/delete=0, except=0 · Call: `diagnostik.kosongkan`
- L917–925 **`RekomendasiEventTest.test_longgar_mencatat_typo_tanpa_mengubah_level`** · kontrol=0, assignment/delete=3, except=0 · Call: `Naluri`, `diagnostik.laporan`, `dict`, `n.apply_events`, `self.assertEqual`, `self.assertIn`
- L927–934 **`RekomendasiEventTest.test_strict_menolak_batch_sebelum_mutasi`** · kontrol=1, assignment/delete=2, except=0 · Call: `Naluri`, `diagnostik.laporan`, `n.apply_events`, `n.to_dict`, `self.assertEqual`, `self.assertGreater`, `self.assertRaisesRegex`
- L936–940 **`RekomendasiEventTest.test_non_mapping_dan_drive_non_teks_menyebut_indeks`** · kontrol=2, assignment/delete=0, except=0 · Call: `Naluri`, `Naluri().apply_events`, `self.assertRaisesRegex`, `self.subTest`
- L942–946 **`RekomendasiEventTest.test_generator_dan_event_emosi_tanpa_drive`** · kontrol=0, assignment/delete=1, except=0 · Call: `Naluri`, `iter`, `n.apply_events`, `self.assertAlmostEqual`
- L948–956 **`RekomendasiEventTest.test_persepsi_tetap_menerima_generator`** · kontrol=1, assignment/delete=1, except=0 · Call: `Naluri`, `iter`, `len`, `n.apply_events`, `patch.object`, `self.assertAlmostEqual`, `self.assertEqual`
- L960–966 **`RekomendasiParameterTest.test_lima_salah_ketik_atau_tipe`** · kontrol=2, assignment/delete=1, except=0 · Call: `Naluri`, `kasus.items`, `self.assertRaisesRegex`, `self.subTest`
- L968–975 **`RekomendasiParameterTest.test_seluruh_default_dan_tipe_registry`** · kontrol=1, assignment/delete=1, except=0 · Call: `DEFAULTS.items`, `Naluri`, `self.assertEqual`, `self.assertIs`, `self.assertIsNot`, `set`, `type`
- L977–983 **`RekomendasiParameterTest.test_angka_bool_nan_inf_dan_rentang`** · kontrol=2, assignment/delete=0, except=0 · Call: `Naluri`, `float`, `self.assertRaisesRegex`, `self.subTest`
- L985–987 **`RekomendasiParameterTest.test_default_tetap_longgar_untuk_ekstensi_host`** · kontrol=0, assignment/delete=0, except=0 · Call: `Naluri`, `self.assertEqual`
- L989–998 **`RekomendasiParameterTest.test_input_tidak_dimutasi_dan_mapping_wajib`** · kontrol=2, assignment/delete=1, except=0 · Call: `Naluri`, `periksa_params`, `self.assertEqual`, `self.assertRaisesRegex`
- L1002–1008 **`RekomendasiNamaTest.test_fitur_kesadaran_asing_tidak_memutasi_params`** · kontrol=1, assignment/delete=2, except=0 · Call: `Naluri`, `dict`, `n.enable_kesadaran`, `self.assertEqual`, `self.assertRaisesRegex`
- L1010–1015 **`RekomendasiNamaTest.test_alias_dan_semua_fitur_masih_bekerja`** · kontrol=0, assignment/delete=1, except=0 · Call: `Naluri`, `n.enable_kesadaran`, `self.assertFalse`, `self.assertTrue`
- L1017–1022 **`RekomendasiNamaTest.test_nama_npc_asing_di_dunia_adalah_valueerror`** · kontrol=2, assignment/delete=1, except=0 · Call: `Lingkungan`, `fn`, `self.assertRaisesRegex`
- L1026–1027 **`RekomendasiDiagnostikTest.setUp`** · kontrol=0, assignment/delete=0, except=0 · Call: `diagnostik.kosongkan`
- L1029–1039 **`RekomendasiDiagnostikTest.test_galat_wrapper_dicatat_dan_tetap_diteruskan`** · kontrol=1, assignment/delete=0, except=0 · Call: `RuntimeError`, `Target`, `Target().fn`, `diagnostik.laporan`, `self.assertEqual`, `self.assertRaisesRegex`, `wrap_method`
- L1032–1033 **`RekomendasiDiagnostikTest.test_galat_wrapper_dicatat_dan_tetap_diteruskan.Target.fn`** · kontrol=0, assignment/delete=0, except=0 · Call: tidak ada
- L1034–1035 **`RekomendasiDiagnostikTest.test_galat_wrapper_dicatat_dan_tetap_diteruskan.rusak`** · kontrol=0, assignment/delete=0, except=0 · Call: `RuntimeError`
- L1041–1049 **`RekomendasiDiagnostikTest.test_galat_di_dalam_wrapper_fallback_terlihat`** · kontrol=1, assignment/delete=2, except=0 · Call: `RuntimeError`, `diagnostik.laporan`, `naluri.Naluri`, `naluri._kausal_tick`, `patch.object`, `self.assertEqual`, `self.assertIn`
- L1051–1061 **`RekomendasiDiagnostikTest.test_health_dan_cli_json_memuat_laporan`** · kontrol=2, assignment/delete=2, except=0 · Call: `Naluri`, `Naluri().health_check`, `contextlib.redirect_stdout`, `diagnostik.catat`, `io.StringIO`, `json.loads`, `keluaran.getvalue`, `periksa.main_periksa`, `self.assertEqual`, `self.assertIn`
- L1063–1072 **`RekomendasiDiagnostikTest.test_tick_organik_memanggil_helper_dan_tidak_menyembunyikan_attributeerror`** · kontrol=1, assignment/delete=1, except=0 · Call: `diagnostik.kosongkan`, `diagnostik.laporan`, `langkah.assert_called_once_with`, `n.tick`, `naluri.Naluri`, `patch.object`, `self.assertEqual`
- L1074–1083 **`RekomendasiDiagnostikTest.test_delta_tubuh_pas_check_fisika_tetap_dalam_domain_snapshot`** · kontrol=0, assignment/delete=2, except=0 · Call: `Mock`, `SimpleNamespace`, `naluri.Naluri`, `naluri._organik_tubuh_langkah`, `self.assertEqual`
- L1085–1100 **`RekomendasiDiagnostikTest.test_semua_handler_broad_naluri_memiliki_kanal_diagnostik`** · kontrol=8, assignment/delete=2, except=0 · Call: `any`, `ast.parse`, `ast.walk`, `f.read`, `handlers.extend`, `isinstance`, `len`, `open`, `os.path.join`, `self.assertGreater`, `self.assertTrue`
- L1103–1108 **`RekomendasiProfilTest.test_penuh_tetap_default_dan_profil_asing_ditolak`** · kontrol=2, assignment/delete=0, except=0 · Call: `KawananNPC`, `Naluri`, `obj.to_dict`, `self.assertEqual`, `self.assertRaisesRegex`
- L1110–1123 **`RekomendasiProfilTest.test_log_dibuang_tetapi_pasangan_kalibrasi_tetap_ada`** · kontrol=2, assignment/delete=4, except=0 · Call: `Naluri`, `n.delta`, `n.tick`, `n.to_dict`, `range`, `self.assertEqual`, `self.assertNotIn`
- L1125–1140 **`RekomendasiProfilTest.test_referensi_diff_custom_dan_penghapusan_lexicon`** · kontrol=0, assignment/delete=6, except=0 · Call: `Naluri`, `Naluri.from_dict`, `iter`, `n.lexicon.pop`, `n.to_dict`, `next`, `self.assertEqual`, `set`
- L1142–1150 **`RekomendasiProfilTest.test_urutan_lexicon_custom_dipertahankan`** · kontrol=0, assignment/delete=4, except=0 · Call: `Naluri`, `Naluri.from_dict`, `dict`, `list`, `n.impact_of`, `n.lexicon.items`, `n.tag_lexicon.items`, `n.to_dict`, `other.impact_of`, `reversed`, `self.assertEqual`
- L1152–1165 **`RekomendasiProfilTest.test_referensi_rusak_atau_bawaan_berubah_ditolak`** · kontrol=4, assignment/delete=3, except=0 · Call: `Naluri`, `Naluri().to_dict`, `Naluri.from_dict`, `deepcopy`, `patch.dict`, `self.assertRaisesRegex`, `self.subTest`
- L1167–1176 **`RekomendasiProfilTest.test_format_referensi_tidak_boleh_disamarkan_sebagai_penuh`** · kontrol=3, assignment/delete=2, except=0 · Call: `Naluri`, `Naluri().to_dict`, `Naluri.from_dict`, `data.pop`, `self.assertRaisesRegex`
- L1178–1191 **`RekomendasiProfilTest.test_file_json_dan_kawanan_meneruskan_profil`** · kontrol=4, assignment/delete=4, except=0 · Call: `KawananNPC`, `Naluri`, `k.serap`, `obj.save`, `obj.to_dict`, `obj.to_json`, `os.path.join`, `other.to_dict`, `self.assertEqual`, `self.subTest`, `tempfile.TemporaryDirectory`, `type`, `type(obj).from_json`, `type(obj).load`, `type(obj).load(path).to_dict`
- L1193–1216 **`RekomendasiProfilTest.test_200_tick_dan_kalibrasi_setara_penuh_pada_fixture_aktif`** · kontrol=5, assignment/delete=6, except=0 · Call: `DEFAULTS.items`, `Naluri`, `Naluri.from_dict`, `a.estimate_scale`, `a.tick`, `a.to_dict`, `b.estimate_scale`, `b.tick`, `b.to_dict`, `isinstance`, `k.startswith`, `n.enable_asosiasi`, `n.enable_eversi`, `n.enable_invensi`, `n.enable_kausal`, `n.enable_latent_drift`, `n.tick`, `n.to_dict`, `range`, `self.assertEqual`
- L1218–1222 **`RekomendasiProfilTest.test_tolok_memuat_waktu_dan_byte_profil`** · kontrol=0, assignment/delete=1, except=0 · Call: `_tolok_to_dict_simpan`, `self.assertLess`, `self.assertTrue`
- L1225–1231 **`RekomendasiRetrievalTest.memori`** · kontrol=1, assignment/delete=1, except=0 · Call: `'api lorong kejadian {}'.format`, `JejakPrediksi`, `j.record_experience`, `range`
- L1233–1246 **`RekomendasiRetrievalTest.test_batas_similarity_dan_laporan_pemotongan`** · kontrol=1, assignment/delete=4, except=0 · Call: `j.performance_report`, `j.predict`, `patch.object`, `self.assertEqual`, `self.assertTrue`, `self.memori`
- L1248–1254 **`RekomendasiRetrievalTest.test_recency_diperiksa_sebelum_similarity_dan_recall`** · kontrol=0, assignment/delete=2, except=0 · Call: `j.predict`, `self.assertEqual`, `self.assertFalse`, `self.memori`
- L1256–1263 **`RekomendasiRetrievalTest.test_kandidat_terbaru_deterministik_setelah_load`** · kontrol=3, assignment/delete=4, except=0 · Call: `JejakPrediksi.from_dict`, `j._retrieve`, `j.to_dict`, `loaded._retrieve`, `self.assertEqual`, `self.memori`
- L1265–1273 **`RekomendasiRetrievalTest.test_batas_besar_setara_mode_legacy`** · kontrol=0, assignment/delete=4, except=0 · Call: `JejakPrediksi.from_dict`, `j.predict`, `j.to_dict`, `other.predict`, `self.assertEqual`, `self.assertFalse`, `self.memori`
- L1275–1285 **`RekomendasiRetrievalTest.test_rank_actions_membatasi_setiap_retrieval_dan_aksi`** · kontrol=1, assignment/delete=3, except=0 · Call: `all`, `j.rank_actions`, `len`, `self.assertEqual`, `self.assertTrue`, `self.memori`
- L1287–1299 **`RekomendasiRetrievalTest.test_opsi_buruk_ditolak_sebelum_mutasi`** · kontrol=5, assignment/delete=2, except=0 · Call: `j.predict`, `j.rank_actions`, `j.to_dict`, `self.assertEqual`, `self.assertRaisesRegex`, `self.assertTrue`, `self.memori`, `self.subTest`
- L1301–1307 **`RekomendasiRetrievalTest.test_query_tanpa_hit_mereset_laporan`** · kontrol=0, assignment/delete=2, except=0 · Call: `j.predict`, `j.rank_actions`, `self.assertEqual`, `self.assertFalse`, `self.memori`
- L1309–1315 **`RekomendasiRetrievalTest.test_lubang_memori_mati_tetap_dibedakan_dari_pemotongan`** · kontrol=0, assignment/delete=2, except=0 · Call: `JejakPrediksi`, `j.predict`, `j.record_experience`, `self.assertFalse`, `self.assertTrue`
- L1317–1322 **`RekomendasiRetrievalTest.test_mode_coarse_tetap_menghormati_batas`** · kontrol=0, assignment/delete=2, except=0 · Call: `j.predict`, `j.set_retrieve_mode`, `self.assertLessEqual`, `self.assertTrue`, `self.memori`
- L1325–1339 **`RekomendasiKawananLazyTest.kawanan`** · kontrol=1, assignment/delete=5, except=0 · Call: `KawananNPC`, `Mock`, `Naluri`, `k.serap`, `n.attach_jejak`, `n.set_lod`
- L1341–1349 **`RekomendasiKawananLazyTest.test_default_tidak_memanggil_prediksi_dan_event_latar_tetap_dibuffer`** · kontrol=1, assignment/delete=1, except=0 · Call: `k.laporan_prediksi`, `k.npcs.values`, `k.tick_all`, `n.jejak.predict.assert_not_called`, `n.jejak.rank_actions.assert_not_called`, `self.assertEqual`, `self.assertIsNone`, `self.assertTrue`, `self.kawanan`
- L1351–1366 **`RekomendasiKawananLazyTest.test_ranking_hanya_npc_aktif_dalam_radius`** · kontrol=2, assignment/delete=4, except=0 · Call: `k.laporan_prediksi`, `k.npcs['Dekat'].jejak.rank_actions.assert_called_once_with`, `k.npcs[nama].jejak.predict.assert_not_called`, `k.npcs[nama].jejak.rank_actions.assert_not_called`, `k.tick_all`, `self.assertEqual`, `self.kawanan`
- L1368–1374 **`RekomendasiKawananLazyTest.test_batch_lazim_tidak_memajukan_waktu`** · kontrol=1, assignment/delete=2, except=0 · Call: `all`, `k.npcs.values`, `k.npcs['Dekat'].jejak.predict.assert_called_once_with`, `k.prediksi_all`, `self.assertEqual`, `self.assertTrue`, `self.kawanan`
- L1376–1388 **`RekomendasiKawananLazyTest.test_opsi_invalid_ditolak_sebelum_tick`** · kontrol=3, assignment/delete=2, except=0 · Call: `all`, `k.npcs.values`, `k.tick_all`, `self.assertRaises`, `self.assertTrue`, `self.kawanan`, `self.subTest`
- L1390–1397 **`RekomendasiKawananLazyTest.test_prediksi_setelah_seluruh_tick`** · kontrol=1, assignment/delete=2, except=0 · Call: `all`, `k.laporan_prediksi`, `k.npcs.values`, `k.tick_all`, `self.assertEqual`, `self.assertTrue`, `self.kawanan`
- L1392–1394 **`RekomendasiKawananLazyTest.test_prediksi_setelah_seluruh_tick.pred`** · kontrol=1, assignment/delete=0, except=0 · Call: `all`, `k.npcs.values`, `self.assertTrue`
- L1399–1404 **`RekomendasiKawananLazyTest.test_koordinat_hilang_dan_radius_nol`** · kontrol=0, assignment/delete=2, except=0 · Call: `k.positions.pop`, `k.prediksi_all`, `self.assertEqual`, `self.kawanan`
- L1406–1412 **`RekomendasiKawananLazyTest.test_galat_callback_dilaporkan_dan_diteruskan`** · kontrol=2, assignment/delete=2, except=0 · Call: `RuntimeError`, `all`, `k.laporan_prediksi`, `k.npcs.values`, `k.tick_all`, `self.assertEqual`, `self.assertRaisesRegex`, `self.assertTrue`, `self.kawanan`
- L1414–1422 **`RekomendasiKawananLazyTest.test_tanpa_jejak_dan_vacancy_diklasifikasikan`** · kontrol=1, assignment/delete=3, except=0 · Call: `k.prediksi_all`, `patch.object`, `self.assertEqual`, `self.kawanan`
- L1424–1437 **`RekomendasiKawananLazyTest.test_ranking_memakai_jam_npc_walau_jejak_tidak_memiliki_backlink`** · kontrol=0, assignment/delete=5, except=0 · Call: `JejakPrediksi`, `KawananNPC`, `Naluri`, `j.record_experience`, `k.prediksi_all`, `k.serap`, `n.attach_jejak`, `self.assertIsNone`, `self.assertTrue`
- L1439–1447 **`RekomendasiKawananLazyTest.test_radius_diperiksa_ulang_setelah_callback_tick`** · kontrol=1, assignment/delete=2, except=0 · Call: `k.laporan_prediksi`, `k.set_position`, `k.tick_all`, `n.jejak.rank_actions.assert_not_called`, `patch.object`, `self.assertEqual`, `self.kawanan`
- L1450–1457 **`RekomendasiBatasMemoriTest.test_nilai_bawaan_dan_batas_tidak_sah`** · kontrol=2, assignment/delete=0, except=0 · Call: `batas`, `patch.dict`, `self.assertEqual`, `self.assertRaisesRegex`
- L1459–1470 **`RekomendasiBatasMemoriTest.test_pangkas_inplace_nol_dan_ceiling_lokal`** · kontrol=2, assignment/delete=2, except=0 · Call: `list`, `pangkas`, `patch.dict`, `range`, `self.assertEqual`, `self.assertIs`
- L1472–1480 **`RekomendasiBatasMemoriTest.test_history_memakai_batas_host_dan_tetap_terbaru`** · kontrol=3, assignment/delete=1, except=0 · Call: `Naluri`, `n.tick`, `patch.dict`, `range`, `self.assertEqual`
- L1482–1494 **`RekomendasiBatasMemoriTest.test_delta_replay_dan_event_buffer_nol`** · kontrol=1, assignment/delete=1, except=0 · Call: `Naluri`, `n.delta`, `n.enable_replay`, `n.set_lod`, `n.tick`, `patch.dict`, `self.assertEqual`
- L1496–1504 **`RekomendasiBatasMemoriTest.test_cache_nol_tidak_menyimpan_tetapi_tetap_menghitung`** · kontrol=1, assignment/delete=2, except=0 · Call: `Naluri`, `n.impact_of`, `patch.dict`, `self.assertEqual`
- L1506–1521 **`RekomendasiBatasMemoriTest.test_audit_readonly_dan_penerapan_seluruh_buffer`** · kontrol=5, assignment/delete=3, except=0 · Call: `Naluri`, `all`, `isinstance`, `items.extend`, `items.update`, `len`, `n._buffer_memori`, `n._buffer_memori().items`, `n.batasi_memori`, `n.memori_state`, `patch.dict`, `self.assertEqual`, `self.assertTrue`, `state['buffers'].values`
- L1523–1532 **`RekomendasiBatasMemoriTest.test_kebijakan_invalid_tidak_memangkas_sebagian`** · kontrol=2, assignment/delete=2, except=0 · Call: `Naluri`, `n.batasi_memori`, `patch.dict`, `self.assertEqual`, `self.assertRaisesRegex`
- L1534–1545 **`RekomendasiBatasMemoriTest.test_load_mengikuti_kebijakan_runtime_bukan_snapshot_host`** · kontrol=3, assignment/delete=3, except=0 · Call: `Naluri`, `Naluri.from_dict`, `len`, `n.tick`, `n.to_dict`, `patch.dict`, `range`, `self.assertEqual`
- L1547–1556 **`RekomendasiBatasMemoriTest.test_kalibrasi_dan_prediction_log_memakai_batas_saat_penulisan`** · kontrol=2, assignment/delete=1, except=0 · Call: `Naluri`, `len`, `n.observe_outcome`, `patch.dict`, `range`, `self.assertEqual`
- L1559–1564 **`RekomendasiVariasiTuturTest.rangkaian`** · kontrol=1, assignment/delete=2, except=0 · Call: `GenContext`, `TuturEngine`, `e.ucap`, `jalur_leksikon`, `range`
- L1566–1571 **`RekomendasiVariasiTuturTest.test_minimal_delapan_dari_dua_puluh_identik`** · kontrol=3, assignment/delete=1, except=0 · Call: `all`, `len`, `self.assertGreaterEqual`, `self.assertLessEqual`, `self.assertTrue`, `self.rangkaian`
- L1573–1579 **`RekomendasiVariasiTuturTest.test_seed_dan_riwayat_sama_menghasilkan_rangkaian_sama`** · kontrol=6, assignment/delete=3, except=0 · Call: `self.assertEqual`, `self.assertNotEqual`, `self.rangkaian`
- L1581–1597 **`RekomendasiVariasiTuturTest.test_pilihan_mematuhi_kelas_bahasa_register_dan_lattice`** · kontrol=1, assignment/delete=4, except=0 · Call: `GenContext`, `L2`, `Leksikon`, `Slot`, `dict`, `entri`, `l2.pilih`, `leks.lattice.cocok`, `random.Random`, `range`, `self.assertEqual`, `self.assertTrue`
- L1584–1586 **`RekomendasiVariasiTuturTest.test_pilihan_mematuhi_kelas_bahasa_register_dan_lattice.entri`** · kontrol=0, assignment/delete=0, except=0 · Call: `dict`
- L1599–1611 **`RekomendasiVariasiTuturTest.test_riwayat_mempengaruhi_skor_tanpa_memutasi_leksikon`** · kontrol=0, assignment/delete=5, except=0 · Call: `GenContext`, `L2`, `Leksikon`, `Slot`, `dict`, `l2._skor`, `l2.pilih`, `l2.riwayat.extend`, `random.Random`, `self.assertEqual`, `self.assertLess`
- L1613–1622 **`RekomendasiVariasiTuturTest.test_pool_kecil_tidak_mengarang_sinonim`** · kontrol=2, assignment/delete=4, except=0 · Call: `GenContext`, `L2`, `Leksikon`, `Slot`, `l2.pilih`, `random.Random`, `range`, `self.assertEqual`, `set`
- L1624–1634 **`RekomendasiVariasiTuturTest.test_seed_memilih_urutan_slot_tanpa_menghilangkan_sebab`** · kontrol=2, assignment/delete=3, except=0 · Call: `GenContext`, `TuturEngine`, `e.ucap`, `jalur_leksikon`, `len`, `next`, `range`, `self.assertGreater`, `self.assertIn`, `set`, `tuple`, `urutan.add`
- L1637–1645 **`RekomendasiLeksikonImpakTest.test_cakupan_provenance_dan_cli`** · kontrol=0, assignment/delete=2, except=0 · Call: `json.loads`, `periksa`, `self.assertEqual`, `self.assertGreaterEqual`, `self.assertTrue`, `subprocess.run`
- L1647–1657 **`RekomendasiLeksikonImpakTest.test_tambahan_tidak_menimpa_bobot_lama_dan_tidak_alias`** · kontrol=0, assignment/delete=4, except=0 · Call: `perluas`, `self.assertGreater`, `self.assertIs`, `self.assertLess`
- L1659–1666 **`RekomendasiLeksikonImpakTest.test_vector_tidak_sah_ditolak`** · kontrol=2, assignment/delete=1, except=0 · Call: `float`, `self.assertRaises`, `self.subTest`, `validasi_entri`
- L1668–1677 **`RekomendasiLeksikonImpakTest.test_impact_baru_dua_bahasa_dan_tag`** · kontrol=0, assignment/delete=2, except=0 · Call: `Naluri`, `en.impact_of`, `n.impact_of`, `self.assertGreater`, `self.assertLess`
- L1679–1685 **`RekomendasiLeksikonImpakTest.test_snapshot_penuh_dan_ringkas_memuat_lexicon_baru`** · kontrol=1, assignment/delete=2, except=0 · Call: `Naluri`, `Naluri.from_dict`, `loaded.impact_of`, `n.impact_of`, `n.to_dict`, `self.assertEqual`
- L1687–1695 **`RekomendasiLeksikonImpakTest.test_checker_menolak_provenance_rusak`** · kontrol=2, assignment/delete=2, except=0 · Call: `deepcopy`, `leksikon._dokumen`, `leksikon.periksa`, `patch.object`, `self.assertRaisesRegex`
- L1698–1705 **`RekomendasiEvaluasiEksternalTest.data`** · kontrol=0, assignment/delete=2, except=0 · Call: `ContohLabel`
- L1707–1713 **`RekomendasiEvaluasiEksternalTest.test_tanpa_data_tidak_mengklaim_evaluasi_eksternal`** · kontrol=0, assignment/delete=1, except=0 · Call: `laporan_kalibrasi`, `self.assertEqual`, `self.assertIn`, `self.assertIsNone`
- L1715–1729 **`RekomendasiEvaluasiEksternalTest.test_kappa_diketahui_konsensus_seri_dikeluarkan`** · kontrol=1, assignment/delete=3, except=0 · Call: `laporan_kalibrasi`, `patch`, `self.assertEqual`, `self.data`
- L1731–1745 **`RekomendasiEvaluasiEksternalTest.test_label_atau_skor_uji_tidak_memilih_ambang`** · kontrol=4, assignment/delete=4, except=0 · Call: `c.anotasi.items`, `c.teks.startswith`, `laporan_kalibrasi`, `patch`, `replace`, `self.assertEqual`, `self.data`, `skor`
- L1736–1737 **`RekomendasiEvaluasiEksternalTest.test_label_atau_skor_uji_tidak_memilih_ambang.skor`** · kontrol=0, assignment/delete=0, except=0 · Call: tidak ada
- L1747–1754 **`RekomendasiEvaluasiEksternalTest.test_overlap_teks_dan_id_ditolak`** · kontrol=3, assignment/delete=0, except=0 · Call: `ContohLabel`, `laporan_kalibrasi`, `self.assertRaisesRegex`
- L1756–1761 **`RekomendasiEvaluasiEksternalTest.test_anotasi_satu_dan_provenance_kosong_tidak_menerbitkan_akurasi`** · kontrol=1, assignment/delete=1, except=0 · Call: `ContohLabel`, `laporan_kalibrasi`, `self.assertIsNone`
- L1763–1768 **`RekomendasiEvaluasiEksternalTest.test_kappa_kelas_konstan_tidak_diklaim_sempurna`** · kontrol=1, assignment/delete=2, except=0 · Call: `ContohLabel`, `laporan_kalibrasi`, `self.assertIn`, `self.assertIsNone`
- L1770–1781 **`RekomendasiEvaluasiEksternalTest.test_label_annotator_bool_dan_identitas_divalidasi_jsonl`** · kontrol=4, assignment/delete=2, except=0 · Call: `contoh_dari_dict`, `f.write`, `json.dumps`, `muat_korpus`, `open`, `os.path.join`, `self.assertEqual`, `self.assertRaisesRegex`, `tempfile.TemporaryDirectory`
- L1783–1799 **`RekomendasiEvaluasiEksternalTest.test_cli_json_dan_teks_menampilkan_status_dan_kappa`** · kontrol=6, assignment/delete=3, except=0 · Call: `contextlib.redirect_stdout`, `f.write`, `io.StringIO`, `jalankan_selaras`, `json.dumps`, `json.loads`, `open`, `os.path.join`, `out.getvalue`, `self.assertEqual`, `self.assertIn`, `tempfile.TemporaryDirectory`
- L1801–1809 **`RekomendasiEvaluasiEksternalTest.test_tiga_anotator_pasangan_dan_data_hilang`** · kontrol=1, assignment/delete=2, except=0 · Call: `ContohLabel`, `laporan_kalibrasi`, `len`, `self.assertEqual`
- L1811–1820 **`RekomendasiEvaluasiEksternalTest.test_abstention_dilaporkan_dan_sumber_tanpa_korpus_ditolak`** · kontrol=2, assignment/delete=2, except=0 · Call: `ContohLabel`, `laporan_kalibrasi`, `patch`, `self.assertEqual`, `self.assertIsNone`, `self.assertRaisesRegex`

## `tests/test_refaktor_inti.py`

SHA-256: `1dd5c186f5972fbd1aaea3c09d1e780b08822948b77d6e7b9cfe705d274e5a13`

348 baris; 9 kelas; 28 fungsi/metode termasuk nested.

Kelas: `RefaktorIntiTest` L19, `InventarisPatchTest` L244, `TanpaImporBackend` L86, `Sasaran` L259, `Berbahaya` L281, `Induk` L285, `Anak` L288, `Sasaran` L316, `Sementara` L305.
Handler luas: tidak ada.

Impor (termasuk lazy/TYPE_CHECKING): `from __future__ import annotations`; `from pathlib import Path`; `from pycos.dukungan.patching import install_method, inventaris`; `from pycos.dukungan.patching import install_methods, inventaris, PatchConflictError`; `from pycos.dukungan.patching import install_methods, wrap_method, inventaris`; `from pycos.dukungan.patching import inventaris`; `from pycos.dukungan.patching import inventaris, install_method`; `from pycos.inti import naluri`; `from pycos.inti import naluri, _konfigurasi, kesadaran, presentasi`; `from pycos.inti.ekstensi import pasang`; `from pycos.inti.naluri import DEFAULTS, RITUAL_DEFAULTS, Ritual`; `from pycos.inti.naluri import Naluri`; `from pycos.inti.naluri import Naluri, Goal, Mood`; `from pycos.inti.naluri import Reputasi, Ritual, KawananNPC`; `from pycos.inti.ritual import RITUAL_DEFAULTS as defaults`; `from types import SimpleNamespace`; `from unittest.mock import patch`; `import ast`; `import gc`; `import hashlib`; `import json`; `import pickle`; `import subprocess`; `import sys`; `import unittest`; `import weakref`.

- L20–24 **`RefaktorIntiTest.test_nama_publik_naluri_tetap`** · kontrol=1, assignment/delete=2, except=0 · Call: `Path`, `dir`, `json.loads`, `n.startswith`, `path.read_text`, `self.assertEqual`, `sorted`
- L26–43 **`RefaktorIntiTest.test_urutan_impor_dan_identitas`** · kontrol=3, assignment/delete=1, except=0 · Call: `self.subTest`, `subprocess.run`
- L45–57 **`RefaktorIntiTest.test_impor_paket_tetap_lazy`** · kontrol=0, assignment/delete=1, except=0 · Call: `subprocess.run`
- L59–66 **`RefaktorIntiTest.test_pickle_jalur_historis`** · kontrol=2, assignment/delete=2, except=0 · Call: `KawananNPC`, `Reputasi`, `Ritual`, `SimpleNamespace`, `obj.to_dict`, `pickle.dumps`, `pickle.loads`, `restored.to_dict`, `self.assertEqual`, `self.assertIs`, `self.subTest`, `type`
- L68–78 **`RefaktorIntiTest.test_ritual_rng_dan_default_bersama`** · kontrol=3, assignment/delete=3, except=0 · Call: `Ritual`, `Ritual(npc, params={'enable_ritual': True}).from_dict`, `SimpleNamespace`, `a.perform`, `a.to_dict`, `b.perform`, `defaults.items`, `range`, `self.assertEqual`, `self.assertIs`
- L80–114 **`RefaktorIntiTest.test_ast_kelas_tidak_berubah_selain_impor_backend`** · kontrol=11, assignment/delete=7, except=0 · Call: `(Path(AKAR) / 'pycos' / 'inti' / (module + '.py')).read_text`, `(Path(__file__).parent / 'fixtures' / 'kelas_inti_r41.json').read_text`, `Path`, `TanpaImporBackend`, `TanpaImporBackend().visit`, `ast.iter_fields`, `ast.parse`, `canonical`, `hashlib.sha256`, `hashlib.sha256(payload.encode()).hexdigest`, `isinstance`, `json.dumps`, `json.loads`, `next`, `payload.encode`, `self.assertEqual`, `self.subTest`, `type`
- L87–93 **`RefaktorIntiTest.test_ast_kelas_tidak_berubah_selain_impor_backend.TanpaImporBackend.visit_ImportFrom`** · kontrol=3, assignment/delete=1, except=0 · Call: tidak ada
- L103–110 **`RefaktorIntiTest.test_ast_kelas_tidak_berubah_selain_impor_backend.canonical`** · kontrol=4, assignment/delete=0, except=0 · Call: `ast.iter_fields`, `canonical`, `isinstance`, `type`
- L116–124 **`RefaktorIntiTest.test_konfigurasi_berbagi_objek_bukan_salinan`** · kontrol=2, assignment/delete=0, except=0 · Call: `getattr`, `presentasi.PRESENTASI_DEFAULTS.items`, `self.assertEqual`, `self.assertIs`
- L126–132 **`RefaktorIntiTest.test_backend_opsional_mengikuti_facade_lama`** · kontrol=1, assignment/delete=1, except=0 · Call: `naluri.Naluri`, `npc.presentasi.tutur_engine`, `patch.object`, `self.assertIsNone`
- L134–145 **`RefaktorIntiTest.test_demo_tidak_dimuat_oleh_impor_produksi`** · kontrol=0, assignment/delete=1, except=0 · Call: `subprocess.run`
- L147–152 **`RefaktorIntiTest.test_semua_showcase_dapat_dijalankan`** · kontrol=0, assignment/delete=1, except=0 · Call: `self.assertEqual`, `self.assertIn`, `subprocess.run`
- L154–183 **`RefaktorIntiTest.test_patch_ids_dan_urutan_tetap_idempoten`** · kontrol=0, assignment/delete=2, except=0 · Call: `Path`, `str`, `subprocess.run`
- L185–197 **`RefaktorIntiTest.test_impor_ekstensi_belum_memasang_patch`** · kontrol=0, assignment/delete=1, except=0 · Call: `subprocess.run`
- L199–203 **`RefaktorIntiTest.test_semua_berkas_inti_maksimal_5000_baris`** · kontrol=2, assignment/delete=1, except=0 · Call: `Path`, `len`, `path.read_text`, `path.read_text().splitlines`, `path.relative_to`, `root.rglob`, `self.assertLessEqual`, `self.subTest`, `str`
- L205–212 **`RefaktorIntiTest.test_registri_menolak_nama_asing_sebelum_impor`** · kontrol=2, assignment/delete=0, except=0 · Call: `loader.assert_not_called`, `pasang`, `patch`, `self.assertRaisesRegex`
- L214–229 **`RefaktorIntiTest.test_semua_modul_ekstensi_aman_diimpor_sebelum_facade`** · kontrol=0, assignment/delete=1, except=0 · Call: `subprocess.run`
- L231–241 **`RefaktorIntiTest.test_pickle_mesin_dan_model_memakai_jalur_lama`** · kontrol=3, assignment/delete=1, except=0 · Call: `Goal`, `Mood`, `Naluri`, `hasattr`, `obj.to_dict`, `pickle.dumps`, `pickle.loads`, `restored.to_dict`, `self.assertEqual`, `self.assertIs`, `self.subTest`, `type`
- L245–254 **`InventarisPatchTest.test_inventaris_tidak_memuat_mesin`** · kontrol=0, assignment/delete=1, except=0 · Call: `subprocess.run`
- L256–276 **`InventarisPatchTest.test_descriptor_urutan_dan_snapshot_terpisah`** · kontrol=5, assignment/delete=1, except=0 · Call: `Sasaran`, `Sasaran().biasa`, `Sasaran.kelas`, `Sasaran.statis`, `any`, `classmethod`, `install_methods`, `inventaris`, `original`, `r['kelas'].endswith`, `r['kelas'].startswith`, `rows[0]['patch_ids'].append`, `self.assertEqual`, `self.assertFalse`, `staticmethod`, `wrap_method`
- L278–298 **`InventarisPatchTest.test_tidak_menjalankan_descriptor_dan_tidak_menggandakan_warisan`** · kontrol=3, assignment/delete=4, except=0 · Call: `AssertionError`, `Berbahaya`, `any`, `install_method`, `inventaris`, `self.assertEqual`, `self.assertFalse`
- L282–283 **`InventarisPatchTest.test_tidak_menjalankan_descriptor_dan_tidak_menggandakan_warisan.Berbahaya.__get__`** · kontrol=0, assignment/delete=0, except=0 · Call: `AssertionError`
- L300–312 **`InventarisPatchTest.test_kelas_sementara_tidak_ditahan_registri`** · kontrol=1, assignment/delete=1, except=0 · Call: `any`, `buat`, `gc.collect`, `install_method`, `inventaris`, `ref`, `self.assertFalse`, `self.assertIsNone`, `weakref.ref`
- L304–308 **`InventarisPatchTest.test_kelas_sementara_tidak_ditahan_registri.buat`** · kontrol=0, assignment/delete=0, except=0 · Call: `install_method`, `weakref.ref`
- L314–323 **`InventarisPatchTest.test_patch_gagal_tidak_masuk_inventaris`** · kontrol=3, assignment/delete=0, except=0 · Call: `any`, `hasattr`, `install_methods`, `inventaris`, `self.assertFalse`, `self.assertRaises`
- L317–318 **`InventarisPatchTest.test_patch_gagal_tidak_masuk_inventaris.Sasaran.ada`** · kontrol=0, assignment/delete=0, except=0 · Call: tidak ada
- L325–333 **`InventarisPatchTest.test_inventaris_inti_cocok_fixture`** · kontrol=2, assignment/delete=4, except=0 · Call: `(Path(__file__).parent / 'fixtures' / 'patch_inti_r41.json').read_text`, `Path`, `expected.items`, `getattr`, `inventaris`, `json.loads`, `self.assertEqual`
- L335–344 **`InventarisPatchTest.test_periksa_json_dan_teks_memuat_patch`** · kontrol=1, assignment/delete=3, except=0 · Call: `any`, `json.loads`, `self.assertIn`, `self.assertTrue`, `subprocess.run`

## `tests/test_regresi_linguistik.py`

SHA-256: `7be3132fb4e0996e2db3966fdd9ccbc4dd1a857edd8579ed6fc032d2ac415528`

955 baris; 36 kelas; 105 fungsi/metode termasuk nested.

Kelas: `ManaMungkinTest` L23, `MorphologySection3Test` L48, `NegasiSection3Test` L74, `TipeSemantikSection3Test` L104, `PeriksaLeksikonTest` L138, `NasalisasiGugusTest` L147, `TindakTuturSkorTest` L168, `PenolakanTuturTest` L184, `PotongBatasKataTest` L205, `GoalTemplateTest` L219, `AlurE0Test` L230, `ParserSection3Test` L261, `TransitiveG1Test` L292, `UjianSection3Test` L310, `EntitasSection3Test` L333, `JawabanSection3Test` L347, `DiamE4Test` L380, `TopikE3Test` L408, `ActE1Test` L427, `AgenSection3Test` L441, `PertanyaanBalikTest` L463, `RedupB6Test` L495, `AspekModalB11Test` L526, `KapitalNamaDiriB10Test` L565, `SelekSiG2Test` L588, `KataKunciG4G5Test` L636, `PassiveB7Test` L664, `FrasaNominaB9Test` L711, `PolisemC6Test` L774, `KerangkaValensiC7Test` L801, `IdiomC8Test` L838, `HubunganE6Test` L866, `RepairE10Test` L913, `_M` L594, `_M` L608, `_M` L625.
Handler luas: tidak ada.

Impor (termasuk lazy/TYPE_CHECKING): `from __future__ import annotations`; `from pycos.bahasa import teks`; `from pycos.bahasa.teks import periksa_gramatika`; `from pycos.bahasa.teks import periksa_gramatika, G1_KERAS`; `from pycos.bahasa.teks import potong_batas_kata`; `from pycos.bahasa.teks import reduplikasi`; `from pycos.bahasa.teks import tindak_tutur_skor`; `from pycos.bahasa.teks import urai_reduplikasi`; `from pycos.bahasa.teks import urai_reduplikasi, stem`; `from pycos.bahasa.tutur import GenContext`; `from pycos.bahasa.tutur import L3, Leksikon`; `from pycos.bahasa.tutur import L3, Leksikon, GenContext, Node, Arg`; `from pycos.bahasa.tutur import Leksikon`; `from pycos.bahasa.tutur import Leksikon, analisis_teks`; `from pycos.bahasa.tutur import Node, Arg`; `from pycos.bahasa.tutur import TuturEngine, GenContext`; `from pycos.bahasa.tutur import TuturEngine, GenContext, Leksikon`; `from pycos.dukungan import leksikon as _leks`; `from pycos.dukungan.sumber import jalur_leksikon`; `from pycos.inti import Naluri`; `from pycos.inti._konfigurasi import GOAL_TEMPLATES`; `from pycos.inti.ekstensi.organik import _nama_dari_teks`; `from pycos.inti.ekstensi.pelindung import _PELINDUNG_UJIAN`; `from pycos.inti.naluri import Naluri`; `from pycos.inti.persona import Persona, Keadaan`; `from pycos.mandiri import PenolakanTutur`; `from pycos.refleksi.nurani import Nurani`; `from pycos.refleksi.nurani import nilai_selaras`; `import json`; `import os`; `import pycos.bahasa as b`; `import pycos.bahasa.teks as t`; `import random`; `import random as _r`; `import re`; `import sys`; `import unittest`.

- L26–28 **`ManaMungkinTest.test_mana_mungkin_bukan_positif`** · kontrol=0, assignment/delete=1, except=0 · Call: `analisis_teks`, `self.assertEqual`
- L30–32 **`ManaMungkinTest.test_masa_mungkin_juga_retorika`** · kontrol=0, assignment/delete=1, except=0 · Call: `analisis_teks`, `self.assertEqual`
- L34–36 **`ManaMungkinTest.test_retorika_berhenti_di_batas_klausa`** · kontrol=0, assignment/delete=1, except=0 · Call: `analisis_teks`, `self.assertEqual`
- L38–40 **`ManaMungkinTest.test_mungkin_saja_masih_normal`** · kontrol=0, assignment/delete=1, except=0 · Call: `analisis_teks`, `self.assertEqual`
- L42–45 **`ManaMungkinTest.test_mana_mungkin_tidak_menyisakan_negatif`** · kontrol=0, assignment/delete=1, except=0 · Call: `analisis_teks`, `self.assertEqual`
- L51–52 **`MorphologySection3Test.setUp`** · kontrol=0, assignment/delete=1, except=0 · Call: `Leksikon`
- L54–60 **`MorphologySection3Test.test_nasalisasi_baris_dokumen`** · kontrol=0, assignment/delete=0, except=0 · Call: `self.assertEqual`, `self.lex.nasalisasi`
- L62–66 **`MorphologySection3Test.test_stem_baris_dokumen`** · kontrol=0, assignment/delete=0, except=0 · Call: `self.assertEqual`, `teks.stem`
- L68–71 **`MorphologySection3Test.test_stem_tervalidasi_leksikon`** · kontrol=0, assignment/delete=0, except=0 · Call: `self.assertEqual`, `teks.stem`
- L77–81 **`NegasiSection3Test.test_zaman_dahulu_tidak_berdampak`** · kontrol=0, assignment/delete=2, except=0 · Call: `Naluri`, `dampak.get`, `n.impact_of`, `self.assertEqual`
- L83–87 **`NegasiSection3Test.test_dia_tidak_gagal_positif`** · kontrol=0, assignment/delete=2, except=0 · Call: `Naluri`, `dampak.get`, `n.impact_of`, `self.assertGreater`
- L89–91 **`NegasiSection3Test.test_tidak_pernah_bahagia_tidak_positif`** · kontrol=0, assignment/delete=1, except=0 · Call: `analisis_teks`, `self.assertEqual`
- L93–95 **`NegasiSection3Test.test_bukan_tidak_senang_positif`** · kontrol=0, assignment/delete=1, except=0 · Call: `analisis_teks`, `self.assertGreaterEqual`
- L97–101 **`NegasiSection3Test.test_senggatan_informal_dan_idiom`** · kontrol=0, assignment/delete=0, except=0 · Call: `analisis_teks`, `self.assertEqual`
- L107–115 **`TipeSemantikSection3Test._tipe`** · kontrol=4, assignment/delete=1, except=0 · Call: `e.get`, `jalur_leksikon`, `json.load`, `list`, `open`
- L117–122 **`TipeSemantikSection3Test.test_tipe_dipisah`** · kontrol=0, assignment/delete=0, except=0 · Call: `self._tipe`, `self.assertEqual`
- L124–135 **`TipeSemantikSection3Test.test_valensi_bukan_default_salah`** · kontrol=6, assignment/delete=1, except=0 · Call: `e.get`, `jalur_leksikon`, `json.load`, `open`, `self.assertLess`, `self.assertNotEqual`, `set`
- L141–144 **`PeriksaLeksikonTest.test_periksa_ok`** · kontrol=0, assignment/delete=1, except=0 · Call: `_leks.periksa`, `self.assertTrue`
- L150–151 **`NasalisasiGugusTest.setUp`** · kontrol=0, assignment/delete=1, except=0 · Call: `Leksikon`
- L153–156 **`NasalisasiGugusTest.test_gugus_tidak_terambil_aturan_menge`** · kontrol=0, assignment/delete=0, except=0 · Call: `self.assertEqual`, `self.lex.nasalisasi`
- L158–160 **`NasalisasiGugusTest.test_satu_suku_kata_tetap_menge`** · kontrol=0, assignment/delete=0, except=0 · Call: `self.assertEqual`, `self.lex.nasalisasi`
- L162–165 **`NasalisasiGugusTest.test_gugus_titik_dua_aturan_mem_dan_men`** · kontrol=0, assignment/delete=0, except=0 · Call: `self.assertEqual`, `self.lex.nasalisasi`
- L171–173 **`TindakTuturSkorTest.test_tuduhan_deklaratif_dengan_pronomina`** · kontrol=0, assignment/delete=1, except=0 · Call: `self.assertGreaterEqual`, `skor.get`, `tindak_tutur_skor`
- L175–177 **`TindakTuturSkorTest.test_hinaan_dengan_pronomina`** · kontrol=0, assignment/delete=1, except=0 · Call: `self.assertGreaterEqual`, `skor.get`, `tindak_tutur_skor`
- L179–181 **`TindakTuturSkorTest.test_pujian_dengan_pronomina`** · kontrol=0, assignment/delete=1, except=0 · Call: `self.assertGreaterEqual`, `skor.get`, `tindak_tutur_skor`
- L187–193 **`PenolakanTuturTest.test_takut_memutus_kalimat`** · kontrol=0, assignment/delete=2, except=0 · Call: `PenolakanTutur`, `r.bentuk`, `random.Random`, `self.assertIn`
- L195–202 **`PenolakanTuturTest.test_malu_mengalihkan`** · kontrol=0, assignment/delete=2, except=0 · Call: `PenolakanTutur`, `r.bentuk`, `random.Random`, `self.assertNotIn`, `self.assertTrue`
- L208–211 **`PotongBatasKataTest.test_potong_di_spasi`** · kontrol=0, assignment/delete=0, except=0 · Call: `potong_batas_kata`, `self.assertEqual`
- L213–216 **`PotongBatasKataTest.test_kata_panjang_tetap_dipotong`** · kontrol=0, assignment/delete=0, except=0 · Call: `potong_batas_kata`, `self.assertEqual`
- L222–227 **`GoalTemplateTest.test_templates_tanpa_placeholder_teknis`** · kontrol=2, assignment/delete=0, except=0 · Call: `GOAL_TEMPLATES.items`, `self.assertNotIn`, `tpl.lower`
- L233–239 **`AlurE0Test._npc`** · kontrol=0, assignment/delete=1, except=0 · Call: `Naluri`, `n.enable_kesadaran`, `n.enable_presentasi`
- L241–245 **`AlurE0Test.test_dengar_mengubah_keadaan_batin`** · kontrol=1, assignment/delete=2, except=0 · Call: `efek.get`, `n.presentasi.dengar`, `n.presentasi.dengar('Aku benci kamu', dari='Rama').get`, `self._npc`, `self.assertTrue`
- L247–258 **`AlurE0Test.test_ucap_membawa_jejak_formation_delapan_faktor`** · kontrol=3, assignment/delete=4, except=0 · Call: `e0['formation'].keys`, `ent.get`, `isinstance`, `n.presentasi.ucap`, `next`, `self._npc`, `self.assertEqual`, `self.assertIsNotNone`, `set`
- L264–269 **`ParserSection3Test.test_transitif_aktif_tanpa_leksikon`** · kontrol=0, assignment/delete=1, except=0 · Call: `self.assertEqual`, `teks.tokenisasi`, `teks.urai_subjek_predikat`
- L271–282 **`ParserSection3Test.test_transitif_aktif_dengan_leksikon`** · kontrol=1, assignment/delete=2, except=0 · Call: `Leksikon`, `jalur_leksikon`, `json.load`, `open`, `self.assertEqual`, `teks.tokenisasi`, `teks.urai_subjek_predikat`
- L284–289 **`ParserSection3Test.test_tolong_bukan_predikat`** · kontrol=0, assignment/delete=1, except=0 · Call: `self.assertEqual`, `teks.tokenisasi`, `teks.urai_subjek_predikat`
- L295–297 **`TransitiveG1Test.test_mengerti_lolos`** · kontrol=0, assignment/delete=0, except=0 · Call: `periksa_gramatika`, `self.assertEqual`
- L299–302 **`TransitiveG1Test.test_preposisi_ganda_tetap_tertangkap`** · kontrol=0, assignment/delete=0, except=0 · Call: `periksa_gramatika`, `self.assertIn`
- L304–307 **`TransitiveG1Test.test_g1_keras_lemah_terekspor`** · kontrol=0, assignment/delete=0, except=0 · Call: `self.assertIn`
- L313–316 **`UjianSection3Test._pola_logika`** · kontrol=0, assignment/delete=0, except=0 · Call: `re.compile`
- L318–322 **`UjianSection3Test.test_kata_kunci_telanjang_tidak_memicu`** · kontrol=1, assignment/delete=1, except=0 · Call: `pola.search`, `self._pola_logika`, `self.assertIsNone`
- L324–330 **`UjianSection3Test.test_menyerang_pendengar_memicu`** · kontrol=1, assignment/delete=1, except=0 · Call: `pola.search`, `self._pola_logika`, `self.assertIsNotNone`
- L336–338 **`EntitasSection3Test.test_nama_di_awal_kalimat_dikenali`** · kontrol=0, assignment/delete=0, except=0 · Call: `_nama_dari_teks`, `self.assertIn`
- L340–344 **`EntitasSection3Test.test_frekuensi_kemunculan_dipertahankan`** · kontrol=0, assignment/delete=0, except=0 · Call: `_nama_dari_teks`, `self.assertEqual`
- L350–356 **`JawabanSection3Test._npc`** · kontrol=0, assignment/delete=1, except=0 · Call: `Naluri`, `n.enable_kesadaran`, `n.enable_presentasi`
- L358–361 **`JawabanSection3Test._tanya`** · kontrol=0, assignment/delete=1, except=0 · Call: `n.presentasi.balas`, `n.presentasi.balas(dari='Rama').get`, `n.presentasi.dengar`, `self._npc`
- L363–365 **`JawabanSection3Test.test_identitas_dijawab_nama`** · kontrol=0, assignment/delete=0, except=0 · Call: `self._tanya`, `self.assertEqual`
- L367–369 **`JawabanSection3Test.test_jam_dijawab_jujur`** · kontrol=0, assignment/delete=0, except=0 · Call: `self._tanya`, `self.assertEqual`
- L371–377 **`JawabanSection3Test.test_tidak_tahu_menyebut_fokus`** · kontrol=0, assignment/delete=0, except=0 · Call: `self._tanya`, `self.assertEqual`
- L383–393 **`DiamE4Test._npc`** · kontrol=0, assignment/delete=3, except=0 · Call: `Naluri`, `n.enable_kesadaran`, `n.enable_presentasi`
- L395–398 **`DiamE4Test.test_isi_ucap_kosong_tanpa_dasar`** · kontrol=0, assignment/delete=1, except=0 · Call: `n.presentasi._isi_ucap`, `self._npc`, `self.assertEqual`
- L400–405 **`DiamE4Test.test_ucap_menjadi_diam`** · kontrol=0, assignment/delete=2, except=0 · Call: `keluar.get`, `n.presentasi.ucap`, `self._npc`, `self.assertEqual`
- L411–417 **`TopikE3Test._npc`** · kontrol=0, assignment/delete=1, except=0 · Call: `Naluri`, `n.enable_kesadaran`, `n.enable_presentasi`
- L419–424 **`TopikE3Test.test_topik_bukan_verbatim_lawan`** · kontrol=0, assignment/delete=2, except=0 · Call: `getattr`, `n.presentasi.dengar`, `self._npc`, `self.assertIsNotNone`, `self.assertNotIn`, `str`, `str(top).lower`
- L430–438 **`ActE1Test.test_ajakan_lawan_tidak_menular`** · kontrol=0, assignment/delete=2, except=0 · Call: `Naluri`, `keluar.get`, `n.enable_kesadaran`, `n.enable_presentasi`, `n.presentasi.balas`, `n.presentasi.dengar`, `self.assertNotIn`
- L444–450 **`AgenSection3Test._npc`** · kontrol=0, assignment/delete=1, except=0 · Call: `Naluri`, `n.enable_kesadaran`, `n.enable_presentasi`
- L452–460 **`AgenSection3Test.test_delapan_ucapan_tidak_ada_masalah_keras`** · kontrol=2, assignment/delete=3, except=0 · Call: `keluar.get`, `n.presentasi.ucap`, `periksa_gramatika`, `range`, `self._npc`, `self.assertEqual`
- L466–471 **`PertanyaanBalikTest._npc`** · kontrol=0, assignment/delete=1, except=0 · Call: `Naluri`, `n.enable_kesadaran`, `n.enable_presentasi`
- L473–483 **`PertanyaanBalikTest.test_balikan_berbeda_per_jenis_tanya`** · kontrol=2, assignment/delete=4, except=0 · Call: `all`, `jawaban.values`, `keluar.get`, `len`, `n.kesadaran.dialogue_turn`, `self._npc`, `self.assertEqual`, `self.assertTrue`, `set`
- L485–488 **`PertanyaanBalikTest.test_balikan_memuat_pronomina_pemicu`** · kontrol=1, assignment/delete=2, except=0 · Call: `keluar.get`, `n.kesadaran.dialogue_turn`, `self._npc`, `self.assertIn`
- L498–500 **`RedupB6Test.test_urai_penuh`** · kontrol=0, assignment/delete=0, except=0 · Call: `self.assertEqual`, `urai_reduplikasi`
- L502–505 **`RedupB6Test.test_urai_berimbuhan`** · kontrol=0, assignment/delete=0, except=0 · Call: `self.assertEqual`, `urai_reduplikasi`
- L507–514 **`RedupB6Test.test_urai_berubah_bunyi`** · kontrol=0, assignment/delete=0, except=0 · Call: `self.assertEqual`, `stem`, `urai_reduplikasi`
- L516–523 **`RedupB6Test.test_bangkit_redup`** · kontrol=1, assignment/delete=0, except=0 · Call: `reduplikasi`, `self.assertEqual`, `self.assertRaises`
- L529–536 **`AspekModalB11Test.test_modal_mungkin_dari_keraguan`** · kontrol=0, assignment/delete=3, except=0 · Call: `GenContext`, `TuturEngine`, `eng.ucap`, `self._leks`, `self.assertIn`, `self.assertIsNotNone`
- L538–545 **`AspekModalB11Test.test_tanpa_keraguan_tanpa_mungkin`** · kontrol=0, assignment/delete=3, except=0 · Call: `GenContext`, `TuturEngine`, `eng.ucap`, `self._leks`, `self.assertIsNotNone`, `self.assertNotIn`
- L547–554 **`AspekModalB11Test.test_aspek_pengalaman_jadi_pernah`** · kontrol=0, assignment/delete=3, except=0 · Call: `GenContext`, `TuturEngine`, `eng.ucap`, `self._leks`, `self.assertIn`, `self.assertIsNotNone`
- L557–562 **`AspekModalB11Test._leks`** · kontrol=1, assignment/delete=0, except=0 · Call: `Leksikon`, `jalur_leksikon`, `json.load`, `open`
- L568–578 **`KapitalNamaDiriB10Test.test_topik_nama_dipertahankan`** · kontrol=1, assignment/delete=4, except=0 · Call: `GenContext`, `Leksikon`, `TuturEngine`, `eng.ucap`, `jalur_leksikon`, `json.load`, `open`, `self.assertIn`
- L580–585 **`KapitalNamaDiriB10Test.test_topik_aktif_pertahankan_kapital`** · kontrol=0, assignment/delete=2, except=0 · Call: `GenContext`, `ctx.topik_aktif`, `self.assertEqual`
- L591–602 **`SelekSiG2Test.test_pantangan_setelah_stemming`** · kontrol=0, assignment/delete=4, except=0 · Call: `Keadaan.dari_mood`, `Persona`, `_M`, `nilai_selaras`, `self.assertEqual`
- L604–619 **`SelekSiG2Test.test_relevansi_terkait_vs_tidak`** · kontrol=2, assignment/delete=8, except=0 · Call: `Keadaan.dari_mood`, `Persona`, `_M`, `nilai_selaras`, `self.assertGreater`
- L621–633 **`SelekSiG2Test.test_koherensi_ulangan_penuh_rendah`** · kontrol=1, assignment/delete=6, except=0 · Call: `Keadaan.dari_mood`, `Persona`, `_M`, `next`, `nilai_selaras`, `self.assertLessEqual`
- L639–645 **`KataKunciG4G5Test.test_keywords_tidak_urut_abjad_saja`** · kontrol=0, assignment/delete=1, except=0 · Call: `Nurani.keywords`, `len`, `self.assertIn`, `self.assertLessEqual`
- L647–650 **`KataKunciG4G5Test.test_kata_negasi_tidak_mengasosiasikan_kutub_lawan`** · kontrol=0, assignment/delete=1, except=0 · Call: `Nurani._lexical_words`, `self.assertNotIn`
- L652–661 **`KataKunciG4G5Test.test_audition_dihitung_atas_lema`** · kontrol=0, assignment/delete=2, except=0 · Call: `Naluri`, `n.enable_kesadaran`, `n.kesadaran.audition_self`, `self.assertEqual`
- L667–672 **`PassiveB7Test._leks`** · kontrol=1, assignment/delete=0, except=0 · Call: `Leksikon`, `jalur_leksikon`, `json.load`, `open`
- L674–682 **`PassiveB7Test.test_topik_objek_menjadi_pasif_kuat`** · kontrol=0, assignment/delete=3, except=0 · Call: `GenContext`, `TuturEngine`, `eng.ucap`, `self._leks`, `self.assertIsNotNone`, `self.assertRegex`
- L684–691 **`PassiveB7Test.test_spotlight_aku_tetap_aktif`** · kontrol=0, assignment/delete=3, except=0 · Call: `GenContext`, `TuturEngine`, `eng.ucap`, `self._leks`, `self.assertIsNotNone`, `self.assertNotRegex`
- L693–708 **`PassiveB7Test.test_diatesis_objek_langsung`** · kontrol=0, assignment/delete=2, except=0 · Call: `GenContext`, `L3`, `_r.Random`, `l3._diatesis_objek`, `self._leks`, `self.assertEqual`
- L714–720 **`FrasaNominaB9Test._l3`** · kontrol=1, assignment/delete=0, except=0 · Call: `L3`, `Leksikon`, `_r.Random`, `jalur_leksikon`, `json.load`, `open`
- L722–730 **`FrasaNominaB9Test.test_posesif_milik_tubuh`** · kontrol=0, assignment/delete=3, except=0 · Call: `GenContext`, `l3.frasa_nomina`, `self._l3`, `self.assertEqual`
- L732–742 **`FrasaNominaB9Test.test_anaphora_demonstrativa`** · kontrol=0, assignment/delete=3, except=0 · Call: `GenContext`, `l3.frasa_nomina`, `self._l3`, `self.assertEqual`
- L744–752 **`FrasaNominaB9Test.test_pewatas_sikap`** · kontrol=0, assignment/delete=3, except=0 · Call: `GenContext`, `l3.frasa_nomina`, `self._l3`, `self.assertIn`
- L754–771 **`FrasaNominaB9Test.test_klausa_relatif_yang`** · kontrol=1, assignment/delete=7, except=0 · Call: `Arg`, `GenContext`, `L3`, `Leksikon`, `Node`, `_r.Random`, `jalur_leksikon`, `json.load`, `l3.klausa`, `open`, `self.assertIn`, `self.assertTrue`
- L777–782 **`PolisemC6Test._leks`** · kontrol=1, assignment/delete=0, except=0 · Call: `Leksikon`, `jalur_leksikon`, `json.load`, `open`
- L784–787 **`PolisemC6Test.test_bisa_mampu_vs_racun`** · kontrol=0, assignment/delete=1, except=0 · Call: `leks.pilih_makna`, `self._leks`, `self.assertEqual`
- L789–792 **`PolisemC6Test.test_tahu_mengetahui_vs_makanan`** · kontrol=0, assignment/delete=1, except=0 · Call: `leks.pilih_makna`, `self._leks`, `self.assertEqual`
- L794–798 **`PolisemC6Test.test_catatan_polisemi_otomatis`** · kontrol=2, assignment/delete=2, except=0 · Call: `' '.join`, `e.get`, `leks.senses`, `self._leks`, `self.assertIn`
- L804–814 **`KerangkaValensiC7Test.test_semua_verba_id_punya_kerangka`** · kontrol=3, assignment/delete=3, except=0 · Call: `e.get`, `jalur_leksikon`, `json.load`, `open`, `self.assertEqual`
- L816–825 **`KerangkaValensiC7Test.test_dwitransitif_berisi_tujuan`** · kontrol=3, assignment/delete=2, except=0 · Call: `e.get`, `jalur_leksikon`, `json.load`, `open`, `self.assertIn`
- L827–835 **`KerangkaValensiC7Test.test_mengirimkan_restriksi_obj_entitas`** · kontrol=5, assignment/delete=2, except=0 · Call: `(e.get('restriksi') or {}).get`, `e.get`, `jalur_leksikon`, `json.load`, `next`, `open`, `self.assertEqual`
- L844–855 **`IdiomC8Test.test_idiom_ada_di_leksikon_dengan_catatan`** · kontrol=6, assignment/delete=4, except=0 · Call: `' '.join`, `e.get`, `jalur_leksikon`, `json.load`, `next`, `open`, `self.assertIn`
- L857–863 **`IdiomC8Test.test_idiom_sentimen_dari_leksikon`** · kontrol=1, assignment/delete=0, except=0 · Call: `self.assertEqual`
- L869–875 **`HubunganE6Test._l3`** · kontrol=1, assignment/delete=0, except=0 · Call: `L3`, `Leksikon`, `_r.Random`, `jalur_leksikon`, `json.load`, `open`
- L877–883 **`HubunganE6Test._node`** · kontrol=1, assignment/delete=1, except=0 · Call: `Arg`, `Node`, `node.args.append`
- L885–890 **`HubunganE6Test.test_alasan_sebab_gabung_karena`** · kontrol=0, assignment/delete=2, except=0 · Call: `GenContext`, `l3.klausa`, `self._l3`, `self._node`, `self.assertIn`, `self.assertNotIn`
- L892–897 **`HubunganE6Test.test_alasan_konsesi_gabung_meski`** · kontrol=0, assignment/delete=2, except=0 · Call: `GenContext`, `l3.klausa`, `self._l3`, `self._node`, `self.assertIn`
- L899–911 **`HubunganE6Test.test_episode_utuh_tidak_diringkas`** · kontrol=1, assignment/delete=4, except=0 · Call: `Arg`, `GenContext`, `L3`, `Leksikon`, `Node`, `_r.Random`, `jalur_leksikon`, `json.load`, `l3.klausa`, `open`, `self.assertIn`
- L916–922 **`RepairE10Test._kes`** · kontrol=0, assignment/delete=1, except=0 · Call: `Naluri`
- L924–928 **`RepairE10Test.test_minta_ulang`** · kontrol=0, assignment/delete=2, except=0 · Call: `ks.repair`, `self._kes`, `self.assertEqual`, `self.assertIn`
- L930–934 **`RepairE10Test.test_konfirmasi_echo`** · kontrol=0, assignment/delete=2, except=0 · Call: `ks.repair`, `self._kes`, `self.assertEqual`
- L936–942 **`RepairE10Test.test_koreksi_diri`** · kontrol=0, assignment/delete=2, except=0 · Call: `ks.repair`, `self._kes`, `self.assertEqual`, `self.assertIn`
- L944–950 **`RepairE10Test.test_klarifikasi_bagian`** · kontrol=0, assignment/delete=3, except=0 · Call: `ks.repair`, `self._kes`, `self.assertEqual`, `self.assertIn`
- L952–955 **`RepairE10Test.test_default_minta_ulang`** · kontrol=0, assignment/delete=2, except=0 · Call: `ks.repair`, `self._kes`, `self.assertEqual`

## `tests/test_selaras.py`

SHA-256: `9b3efe2c454e0816a047212a9ef8504a668807d5f1feac298167b4515ae863a9`

320 baris; 7 kelas; 34 fungsi/metode termasuk nested.

Kelas: `PersonaTest` L41, `KeadaanTest` L63, `FiturTest` L89, `PenilaiTest` L123, `PelacakTest` L182, `CliTest` L225, `KepindahanRumahTest` L275.
Handler luas: tidak ada.

Impor (termasuk lazy/TYPE_CHECKING): `from __future__ import annotations`; `from pycos.__main__ import utama as cli`; `from pycos.bahasa.tutur import analisis_teks`; `from pycos.inti.naluri import Keadaan, Persona`; `from pycos.inti.naluri import PERSONA_CONTOH as C2, Keadaan as K2, Persona as P2`; `from pycos.inti.persona import PERSONA_CONTOH, Keadaan, Persona`; `from pycos.refleksi.nurani import DimensiSkor, Laporan, PelacakSelaras, nilai_selaras`; `from types import SimpleNamespace`; `import ast`; `import contextlib`; `import importlib`; `import io`; `import json`; `import os`; `import subprocess`; `import sys`; `import tempfile`; `import unittest`.

- L42–47 **`PersonaTest.test_roundtrip_dan_normalisasi_pantangan`** · kontrol=0, assignment/delete=1, except=0 · Call: `Persona`, `Persona.from_dict`, `p.to_dict`, `self.assertEqual`
- L49–56 **`PersonaTest.test_validasi_ketat`** · kontrol=2, assignment/delete=0, except=0 · Call: `Persona`, `self.assertRaises`, `self.subTest`
- L58–60 **`PersonaTest.test_from_dict_menolak_kunci_asing`** · kontrol=1, assignment/delete=0, except=0 · Call: `Persona.from_dict`, `self.assertRaisesRegex`
- L64–70 **`KeadaanTest.test_validasi_dan_roundtrip`** · kontrol=2, assignment/delete=1, except=0 · Call: `Keadaan`, `Keadaan.from_dict`, `float`, `k.to_dict`, `self.assertEqual`, `self.assertRaises`, `self.subTest`
- L72–77 **`KeadaanTest.test_dari_mood_duck_typing_dan_pemetaan_arousal`** · kontrol=0, assignment/delete=2, except=0 · Call: `Keadaan.dari_mood`, `SimpleNamespace`, `self.assertEqual`
- L79–81 **`KeadaanTest.test_dari_mood_atribut_hilang_tidak_jadi_nol`** · kontrol=1, assignment/delete=0, except=0 · Call: `Keadaan.dari_mood`, `SimpleNamespace`, `self.assertRaises`
- L83–86 **`KeadaanTest.test_dari_mood_non_finite_ditolak`** · kontrol=2, assignment/delete=0, except=0 · Call: `Keadaan.dari_mood`, `SimpleNamespace`, `float`, `self.assertRaises`, `self.subTest`
- L90–95 **`FiturTest.test_polaritas_formalitas_intensitas_keraguan`** · kontrol=0, assignment/delete=1, except=0 · Call: `analisis_teks`, `f.formalitas`, `f.intensitas`, `f.keraguan`, `f.polaritas`, `self.assertEqual`, `self.assertGreater`
- L97–105 **`FiturTest.test_negasi_membalik_polaritas`** · kontrol=0, assignment/delete=0, except=0 · Call: `analisis_teks`, `analisis_teks('aku senang sekali').polaritas`, `analisis_teks('aku tidak senang').polaritas`, `analisis_teks('bukan hal yang bagus').polaritas`, `analisis_teks('bukan yang bagus').polaritas`, `analisis_teks('tidak tahu kenapa aku senang').polaritas`, `self.assertEqual`
- L107–112 **`FiturTest.test_tanpa_bukti_bernilai_none`** · kontrol=0, assignment/delete=1, except=0 · Call: `analisis_teks`, `analisis_teks('   ').intensitas`, `f.formalitas`, `f.keraguan`, `f.polaritas`, `self.assertEqual`, `self.assertIsNone`
- L114–116 **`FiturTest.test_huruf_kapital_dan_tanda_hubung`** · kontrol=0, assignment/delete=0, except=0 · Call: `analisis_teks`, `analisis_teks('TOLONG CEPAT').intensitas`, `self.assertEqual`, `self.assertGreater`
- L118–120 **`FiturTest.test_bukan_string_ditolak`** · kontrol=1, assignment/delete=0, except=0 · Call: `analisis_teks`, `self.assertRaises`
- L124–129 **`PenilaiTest.test_teks_selaras_dengan_persona_dan_keadaan`** · kontrol=0, assignment/delete=1, except=0 · Call: `Keadaan`, `laporan.to_dict`, `nilai_selaras`, `self.assertEqual`, `self.assertGreaterEqual`
- L131–136 **`PenilaiTest.test_target_campuran_persona_dan_keadaan`** · kontrol=1, assignment/delete=3, except=0 · Call: `Keadaan`, `Persona`, `next`, `nilai_selaras`, `self.assertEqual`
- L138–143 **`PenilaiTest.test_register_formal_pada_persona_santai_diberi_skor_rendah`** · kontrol=2, assignment/delete=2, except=0 · Call: `Keadaan`, `any`, `next`, `nilai_selaras`, `self.assertLess`, `self.assertTrue`
- L145–151 **`PenilaiTest.test_pantangan_membatasi_skor_dan_status`** · kontrol=0, assignment/delete=1, except=0 · Call: `Keadaan`, `nilai_selaras`, `self.assertEqual`, `self.assertIn`, `self.assertLessEqual`
- L153–160 **`PenilaiTest.test_pantangan_cocok_setelah_stemming_g2`** · kontrol=0, assignment/delete=2, except=0 · Call: `Keadaan`, `nilai_selaras`, `self.assertEqual`
- L162–166 **`PenilaiTest.test_persona_netral_tidak_menilai_register`** · kontrol=1, assignment/delete=2, except=0 · Call: `Keadaan`, `Persona`, `next`, `nilai_selaras`, `self.assertIn`, `self.assertIsNone`
- L168–171 **`PenilaiTest.test_teks_kosong_tidak_dapat_dinilai`** · kontrol=0, assignment/delete=1, except=0 · Call: `Keadaan`, `nilai_selaras`, `self.assertEqual`, `self.assertIsNone`
- L173–179 **`PenilaiTest.test_deterministik_dan_tanpa_mutasi_input`** · kontrol=0, assignment/delete=3, except=0 · Call: `Keadaan`, `a.to_dict`, `b.to_dict`, `nilai_selaras`, `self.assertEqual`, `self.assertIsInstance`
- L183–185 **`PelacakTest._laporan`** · kontrol=2, assignment/delete=1, except=0 · Call: `(dim or {}).items`, `DimensiSkor`, `Laporan`, `tuple`
- L187–195 **`PelacakTest.test_tren_menurun_dan_meningkat`** · kontrol=2, assignment/delete=1, except=0 · Call: `PelacakSelaras`, `pelacak.catat`, `pelacak.kosongkan`, `pelacak.tren`, `self._laporan`, `self.assertEqual`
- L197–204 **`PelacakTest.test_stabil_dan_belum_cukup`** · kontrol=2, assignment/delete=1, except=0 · Call: `PelacakSelaras`, `pelacak.catat`, `pelacak.tren`, `range`, `self._laporan`, `self.assertEqual`
- L206–214 **`PelacakTest.test_memori_terbatas_dan_dimensi_none_dilewati`** · kontrol=1, assignment/delete=2, except=0 · Call: `DimensiSkor`, `Laporan`, `PelacakSelaras`, `len`, `pelacak.catat`, `pelacak.tren`, `range`, `self._laporan`, `self.assertEqual`, `self.assertNotIn`
- L216–222 **`PelacakTest.test_validasi_konstruktor_dan_tipe`** · kontrol=3, assignment/delete=0, except=0 · Call: `PelacakSelaras`, `PelacakSelaras().catat`, `self.assertRaises`, `self.subTest`
- L226–230 **`CliTest._jalankan`** · kontrol=1, assignment/delete=2, except=0 · Call: `cli`, `contextlib.redirect_stdout`, `io.StringIO`, `keluaran.getvalue`
- L232–239 **`CliTest.test_kode_keluar_sesuai_status`** · kontrol=0, assignment/delete=3, except=0 · Call: `self._jalankan`, `self.assertEqual`
- L241–244 **`CliTest.test_input_tidak_sah_kode_2`** · kontrol=1, assignment/delete=1, except=0 · Call: `contextlib.redirect_stderr`, `io.StringIO`, `self._jalankan`, `self.assertEqual`
- L246–253 **`CliTest.test_json_dan_demo`** · kontrol=0, assignment/delete=4, except=0 · Call: `json.loads`, `len`, `self._jalankan`, `self.assertEqual`, `self.assertIn`
- L255–266 **`CliTest.test_persona_json_dipakai_pada_demo`** · kontrol=2, assignment/delete=4, except=0 · Call: `Persona`, `dengan.to_dict`, `json.dump`, `json.loads`, `open`, `os.path.join`, `self._jalankan`, `self.assertEqual`, `tempfile.TemporaryDirectory`
- L268–272 **`CliTest.test_python_m_pycos_demo`** · kontrol=0, assignment/delete=1, except=0 · Call: `self.assertEqual`, `self.assertIn`, `subprocess.run`
- L278–287 **`KepindahanRumahTest.test_rumah_baru_sesuai_lapisan`** · kontrol=1, assignment/delete=0, except=0 · Call: `importlib.import_module`, `self.assertEqual`, `self.assertRaises`
- L289–297 **`KepindahanRumahTest.test_re_export_kompatibel_di_naluri`** · kontrol=0, assignment/delete=0, except=0 · Call: `self.assertIs`
- L299–316 **`KepindahanRumahTest.test_refleksi_tidak_mengimpor_inti_atau_bahasa_di_tingkat_modul`** · kontrol=6, assignment/delete=5, except=0 · Call: `(simpul.module or '').split`, `ast.parse`, `f.read`, `isinstance`, `open`, `os.path.join`, `self.assertNotIn`, `simpul.names[0].name.split`

## `tests/test_selaras_lanjutan.py`

SHA-256: `5f912bd06ad4fdc8694e461402055374a7bac2eeba6af8aec385b2ce3be01805`

338 baris; 9 kelas; 47 fungsi/metode termasuk nested.

Kelas: `NegasiKlausaTest` L52, `MorfologiTest` L69, `LeksikonTest` L94, `MuatKorpusTest` L142, `KappaTest` L200, `UkurFiturTest` L215, `UkurSelarasTest` L238, `KorpusContohRegresiTest` L272, `CliKalibrasiTest` L296.
Handler luas: tidak ada.

Impor (termasuk lazy/TYPE_CHECKING): `from __future__ import annotations`; `from pycos.__main__ import utama as cli`; `from pycos.bahasa.tutur import JENDELA_NEGASI, LeksikonCiri, analisis_teks`; `from pycos.inti.naluri import PERSONA_CONTOH, Keadaan`; `from pycos.refleksi.nurani import ContohLabel, contoh_dari_dict, kappa_cohen, laporan_kalibrasi, muat_korpus, nilai_selaras, ukur_fitur, ukur_selaras`; `import contextlib`; `import io`; `import json`; `import os`; `import sys`; `import tempfile`; `import unittest`.

- L45–49 **`_leksikon_kosong`** · kontrol=1, assignment/delete=1, except=0 · Call: `dasar.update`
- L53–56 **`NegasiKlausaTest.test_jendela_tiga_token`** · kontrol=0, assignment/delete=0, except=0 · Call: `analisis_teks`, `analisis_teks('bukan hal yang bagus').polaritas`, `analisis_teks('tidak ada yang senang').polaritas`, `self.assertEqual`
- L58–60 **`NegasiKlausaTest.test_negasi_berhenti_di_tanda_baca`** · kontrol=0, assignment/delete=0, except=0 · Call: `analisis_teks`, `analisis_teks('aku senang, tidak').polaritas`, `analisis_teks('tidak tahu. aku senang').polaritas`, `self.assertEqual`
- L62–63 **`NegasiKlausaTest.test_negasi_di_luar_jendela_tidak_membalik`** · kontrol=0, assignment/delete=0, except=0 · Call: `analisis_teks`, `analisis_teks('tidak tahu kenapa aku senang').polaritas`, `self.assertEqual`
- L65–66 **`NegasiKlausaTest.test_negasi_membalik_kata_negatif`** · kontrol=0, assignment/delete=0, except=0 · Call: `analisis_teks`, `analisis_teks('nggak sedih kok').polaritas`, `self.assertEqual`
- L70–83 **`MorfologiTest.test_bentuk_turunan_terdeteksi`** · kontrol=2, assignment/delete=1, except=0 · Call: `analisis_teks`, `analisis_teks(teks).polaritas`, `casting.items`, `self.assertEqual`, `self.subTest`
- L85–87 **`MorfologiTest.test_kata_pendek_tidak_dipotong`** · kontrol=0, assignment/delete=0, except=0 · Call: `analisis_teks`, `analisis_teks('di sana').polaritas`, `self.assertIsNone`
- L89–91 **`MorfologiTest.test_frasa_terima_kasih`** · kontrol=0, assignment/delete=0, except=0 · Call: `analisis_teks`, `analisis_teks('terima jaket itu').polaritas`, `analisis_teks('terima kasih banyak').polaritas`, `self.assertEqual`, `self.assertIsNone`
- L95–98 **`LeksikonTest.test_roundtrip_dict`** · kontrol=0, assignment/delete=1, except=0 · Call: `LeksikonCiri.from_dict`, `_leksikon_kosong`, `lx.to_dict`, `self.assertEqual`
- L100–103 **`LeksikonTest.test_kustom_mengganti_bawaan`** · kontrol=0, assignment/delete=1, except=0 · Call: `LeksikonCiri.from_dict`, `_leksikon_kosong`, `analisis_teks`, `analisis_teks('aku senang', lx).polaritas`, `analisis_teks('cemerlang sekali', lx).polaritas`, `self.assertEqual`, `self.assertIsNone`
- L105–112 **`LeksikonTest.test_nilai_selaras_menerima_leksikon`** · kontrol=0, assignment/delete=4, except=0 · Call: `Keadaan`, `LeksikonCiri.from_dict`, `_leksikon_kosong`, `nilai_selaras`, `nilai_selaras(PERSONA_CONTOH, k, 'aku senang').to_dict`, `nilai_selaras(PERSONA_CONTOH, k, 'aku senang', None).to_dict`, `self.assertEqual`, `self.assertNotEqual`
- L114–118 **`LeksikonTest.test_tolak_kategori_hilang`** · kontrol=1, assignment/delete=2, except=0 · Call: `LeksikonCiri.from_dict`, `_leksikon_kosong`, `self.assertRaises`
- L120–122 **`LeksikonTest.test_tolak_kunci_tak_dikenal`** · kontrol=1, assignment/delete=0, except=0 · Call: `LeksikonCiri.from_dict`, `_leksikon_kosong`, `dict`, `self.assertRaises`
- L124–126 **`LeksikonTest.test_tolak_bukan_daftar`** · kontrol=1, assignment/delete=0, except=0 · Call: `LeksikonCiri.from_dict`, `_leksikon_kosong`, `self.assertRaises`
- L128–131 **`LeksikonTest.test_tolak_frasa_multi_kata`** · kontrol=1, assignment/delete=0, except=0 · Call: `LeksikonCiri.from_dict`, `_leksikon_kosong`, `self.assertIn`, `self.assertRaises`, `str`
- L133–139 **`LeksikonTest.test_dari_berkas`** · kontrol=2, assignment/delete=2, except=0 · Call: `LeksikonCiri.dari_berkas`, `_leksikon_kosong`, `analisis_teks`, `analisis_teks('asyik sekali', lx).polaritas`, `json.dump`, `open`, `os.path.join`, `self.assertEqual`, `tempfile.TemporaryDirectory`
- L143–147 **`MuatKorpusTest._tulis`** · kontrol=1, assignment/delete=1, except=0 · Call: `'\n'.join`, `f.write`, `open`, `os.path.join`
- L149–152 **`MuatKorpusTest.test_korpus_contoh_valid`** · kontrol=1, assignment/delete=1, except=0 · Call: `all`, `isinstance`, `len`, `muat_korpus`, `self.assertGreaterEqual`, `self.assertTrue`
- L154–157 **`MuatKorpusTest.test_baris_kosong_dilewati`** · kontrol=1, assignment/delete=1, except=0 · Call: `len`, `muat_korpus`, `self._tulis`, `self.assertEqual`, `tempfile.TemporaryDirectory`
- L159–164 **`MuatKorpusTest.test_galat_menyebut_nomor_baris`** · kontrol=2, assignment/delete=1, except=0 · Call: `muat_korpus`, `self._tulis`, `self.assertIn`, `self.assertRaises`, `str`, `tempfile.TemporaryDirectory`
- L166–170 **`MuatKorpusTest.test_json_rusak`** · kontrol=2, assignment/delete=1, except=0 · Call: `muat_korpus`, `self._tulis`, `self.assertRaises`, `tempfile.TemporaryDirectory`
- L172–176 **`MuatKorpusTest.test_korpus_kosong`** · kontrol=2, assignment/delete=1, except=0 · Call: `muat_korpus`, `self._tulis`, `self.assertRaises`, `tempfile.TemporaryDirectory`
- L178–190 **`MuatKorpusTest.test_validasi_nilai_label`** · kontrol=3, assignment/delete=1, except=0 · Call: `contoh_dari_dict`, `self.assertRaises`, `self.subTest`
- L192–197 **`MuatKorpusTest.test_contoh_dengan_keadaan_dan_persona`** · kontrol=0, assignment/delete=1, except=0 · Call: `contoh_dari_dict`, `self.assertEqual`
- L201–203 **`KappaTest.test_kappa_nilai_diketahui`** · kontrol=0, assignment/delete=1, except=0 · Call: `kappa_cohen`, `self.assertAlmostEqual`
- L205–206 **`KappaTest.test_kappa_sempurna`** · kontrol=0, assignment/delete=0, except=0 · Call: `kappa_cohen`, `self.assertAlmostEqual`
- L208–209 **`KappaTest.test_kappa_satu_kelas`** · kontrol=0, assignment/delete=0, except=0 · Call: `kappa_cohen`, `self.assertEqual`
- L211–212 **`KappaTest.test_kappa_kosong`** · kontrol=0, assignment/delete=0, except=0 · Call: `kappa_cohen`, `self.assertIsNone`
- L216–225 **`UkurFiturTest.test_cakupan_dan_akurasi`** · kontrol=0, assignment/delete=2, except=0 · Call: `ContohLabel`, `self.assertAlmostEqual`, `self.assertEqual`, `ukur_fitur`
- L227–230 **`UkurFiturTest.test_formalitas_tanpa_label`** · kontrol=0, assignment/delete=1, except=0 · Call: `ContohLabel`, `self.assertEqual`, `self.assertIsNone`, `ukur_fitur`
- L232–235 **`UkurFiturTest.test_formalitas_salah_terukur`** · kontrol=0, assignment/delete=2, except=0 · Call: `ContohLabel`, `self.assertEqual`, `ukur_fitur`
- L239–244 **`UkurSelarasTest._korpus_sintetis`** · kontrol=0, assignment/delete=3, except=0 · Call: `ContohLabel`, `Keadaan`
- L246–248 **`UkurSelarasTest.test_kurang_dari_empat_label`** · kontrol=0, assignment/delete=1, except=0 · Call: `ContohLabel`, `self.assertIn`, `ukur_selaras`
- L250–255 **`UkurSelarasTest.test_pipeline_pada_data_sintetis`** · kontrol=0, assignment/delete=1, except=0 · Call: `self._korpus_sintetis`, `self.assertEqual`, `self.assertIsNotNone`, `self.assertTrue`, `ukur_selaras`
- L257–265 **`UkurSelarasTest.test_ambang_dipilih_dari_porsi_latih_saja`** · kontrol=1, assignment/delete=3, except=0 · Call: `ContohLabel`, `self._korpus_sintetis`, `self.assertEqual`, `ukur_selaras`
- L267–269 **`UkurSelarasTest.test_porsi_terlalu_kecil`** · kontrol=0, assignment/delete=1, except=0 · Call: `self._korpus_sintetis`, `self.assertIn`, `ukur_selaras`
- L276–277 **`KorpusContohRegresiTest.setUpClass`** · kontrol=0, assignment/delete=1, except=0 · Call: `laporan_kalibrasi`, `muat_korpus`
- L279–281 **`KorpusContohRegresiTest.test_polaritas_tidak_turun`** · kontrol=0, assignment/delete=0, except=0 · Call: `self.assertEqual`, `self.assertGreaterEqual`
- L283–284 **`KorpusContohRegresiTest.test_formalitas_tidak_turun`** · kontrol=0, assignment/delete=0, except=0 · Call: `self.assertGreaterEqual`
- L286–290 **`KorpusContohRegresiTest.test_sarkasme_tetap_diakui_sebagai_batasan`** · kontrol=0, assignment/delete=0, except=0 · Call: `analisis_teks`, `analisis_teks('wah, hebat banget ya, bikin aku nangis.').polaritas`, `self.assertEqual`
- L292–293 **`KorpusContohRegresiTest.test_laporan_berisi_peringatan_ukuran`** · kontrol=0, assignment/delete=0, except=0 · Call: `self.assertIn`
- L297–301 **`CliKalibrasiTest._jalankan`** · kontrol=1, assignment/delete=2, except=0 · Call: `buf.getvalue`, `cli`, `contextlib.redirect_stderr`, `contextlib.redirect_stdout`, `io.StringIO`
- L303–307 **`CliKalibrasiTest.test_kalibrasi_teks`** · kontrol=0, assignment/delete=1, except=0 · Call: `self._jalankan`, `self.assertEqual`, `self.assertIn`
- L309–312 **`CliKalibrasiTest.test_kalibrasi_json`** · kontrol=0, assignment/delete=1, except=0 · Call: `json.loads`, `self._jalankan`, `self.assertEqual`, `self.assertIn`
- L314–320 **`CliKalibrasiTest.test_korpus_rusak_kode_dua`** · kontrol=2, assignment/delete=2, except=0 · Call: `f.write`, `open`, `os.path.join`, `self._jalankan`, `self.assertEqual`, `tempfile.TemporaryDirectory`
- L322–330 **`CliKalibrasiTest.test_leksikon_kustom_di_cli`** · kontrol=2, assignment/delete=2, except=0 · Call: `_leksikon_kosong`, `json.dump`, `json.loads`, `open`, `os.path.join`, `self._jalankan`, `self.assertIn`, `tempfile.TemporaryDirectory`
- L332–334 **`CliKalibrasiTest.test_leksikon_tidak_ada_kode_dua`** · kontrol=0, assignment/delete=1, except=0 · Call: `self._jalankan`, `self.assertEqual`

## `tests/test_sst.py`

SHA-256: `0639e4362270302bcced0f3d043751c64a45161e3f8fabee7dca2e1c4bdf8f47`

1449 baris; 6 kelas; 40 fungsi/metode termasuk nested.

Kelas: `LedgerFitur` L49, `OrkestraSST` L305, `SSTOrkestraTest` L1305, `SSTPengamanTest` L1362, `SSTKlasifikasiTest` L1417, `Sasaran` L380.
Handler luas: tidak ada.

Impor (termasuk lazy/TYPE_CHECKING): `from __future__ import annotations`; `from pycos import kontrak`; `from pycos.bahasa import teks as teks_api`; `from pycos.bahasa.tutur import FiturTutur, GenContext, LeksikonCiri, SASPAnalyzer, TuturEngine, analisis_teks, konteks_dari_presentasi, sa_sp, sa_sp_literal, sa_sp_pragmatik, token_dari`; `from pycos.dukungan import diagnostik`; `from pycos.dukungan import periksa`; `from pycos.dukungan.batas_memori import BATAS`; `from pycos.dukungan.konstanta import DRIVES`; `from pycos.dukungan.leksikon import periksa as periksa_impak`; `from pycos.dukungan.numerik import float_hingga, jepit, jepit_01, jepit_drive`; `from pycos.dukungan.patching import PatchConflictError, install_method, install_methods, optional_module, wrap_method`; `from pycos.dukungan.patching import inventaris`; `from pycos.dukungan.sumber import ada_sumber_daya, akar_paket, jalur_korpus, jalur_leksikon, kandidat_leksikon`; `from pycos.dukungan.sumber import jalur_korpus`; `from pycos.dukungan.sumber import jalur_leksikon`; `from pycos.inti.naluri import DRIVES, Naluri, buat_npc`; `from pycos.inti.naluri import KawananNPC, Reputasi`; `from pycos.inti.naluri import Naluri`; `from pycos.inti.persona import Keadaan, Persona`; `from pycos.inti.persona import PERSONA_CONTOH, Keadaan, Persona`; `from pycos.lingkungan.dunia import Lingkungan, Peta, peta_contoh`; `from pycos.mandiri.kognisi_lanjut import KognisiLanjut, boltzmann_pilih`; `from pycos.mandiri.organik import Organik`; `from pycos.memori.jejak_prediksi import JejakPrediksi`; `from pycos.refleksi.ketidaktahuan import batas_pengetahuan, sikap_ketidaktahuan`; `from pycos.refleksi.nurani import ContohLabel, PelacakSelaras, contoh_dari_dict, kappa_cohen, laporan_kalibrasi, muat_korpus, nilai_selaras, ukur_fitur, ukur_selaras`; `from pycos.refleksi.nurani import PelacakSelaras, nilai_selaras`; `from typing import Any, Dict, List, Set, Tuple`; `from unittest.mock import patch`; `import ast`; `import contextlib`; `import io`; `import os`; `import pycos`; `import sys`; `import tempfile`; `import types`; `import unittest`.

- L52–54 **`LedgerFitur.__init__`** · kontrol=0, assignment/delete=2, except=0 · Call: tidak ada
- L56–62 **`LedgerFitur.tandai`** · kontrol=4, assignment/delete=1, except=0 · Call: `AssertionError`, `bukti.strip`, `isinstance`, `nama.strip`, `self._jejak.append`, `str`
- L64–65 **`LedgerFitur.bukti`** · kontrol=0, assignment/delete=0, except=0 · Call: `self._aktif.get`
- L67–68 **`LedgerFitur.aktif`** · kontrol=0, assignment/delete=0, except=0 · Call: `set`
- L70–71 **`LedgerFitur.kurang`** · kontrol=0, assignment/delete=0, except=0 · Call: `self.aktif`, `set`
- L73–77 **`LedgerFitur.laporan`** · kontrol=1, assignment/delete=1, except=0 · Call: `'  [OK] {:<38} {}'.format`, `'LAPORAN SST — fitur aktif: {}'.format`, `'\n'.join`, `baris.append`, `len`, `sorted`
- L143–147 **`himpunan_fitur_wajib`** · kontrol=1, assignment/delete=1, except=0 · Call: `FITUR_WAJIB.values`, `set`, `total.update`
- L300–302 **`_cek`** · kontrol=1, assignment/delete=0, except=0 · Call: `AssertionError`
- L312–323 **`OrkestraSST.__init__`** · kontrol=0, assignment/delete=11, except=0 · Call: `LedgerFitur`, `tempfile.TemporaryDirectory`
- L326–329 **`OrkestraSST._t`** · kontrol=1, assignment/delete=0, except=0 · Call: `AssertionError`, `himpunan_fitur_wajib`, `self.ledger.tandai`
- L331–341 **`OrkestraSST.jalankan`** · kontrol=2, assignment/delete=1, except=0 · Call: `'manifest berbeda dari fitur aktif: {}'.format`, `_cek`, `getattr`, `getattr(self, 'fase_' + nama_fase.split('_', 1)[1])`, `himpunan_fitur_wajib`, `nama_fase.split`, `self.ledger.aktif`, `self.tmp.cleanup`, `sorted`
- L344–462 **`OrkestraSST.fase_sumber_daya_dan_kontrak`** · kontrol=10, assignment/delete=10, except=3 · Call: `Keadaan`, `PelacakSelaras`, `Persona`, `Sasaran`, `Sasaran().nilai_baru`, `_cek`, `ada_sumber_daya`, `akar_paket`, `any`, `asli`, `diagnostik.catat`, `diagnostik.kosongkan`, `diagnostik.laporan`, `diagnostik.laporan()['per_sumber'].get`, `float`, `float_hingga`, `install_method`, `install_methods`, `inventaris`, `jalur_korpus`, `jalur_leksikon`, `jepit`, `jepit_01`, `jepit_drive`, `kandidat_leksikon`, `kasus`, `kontrak.ContractViolationError`, `kontrak.angka`, `kontrak.check_operation`, `kontrak.hanya_kunci`, `kontrak.kontrak_operasi`, `kontrak.teks_wajib`, `kontrak.verifikasi_startup`, `len`, `nilai_selaras`, `optional_module`, `os.path.isdir`, `os.path.isfile`, `self._t`, `types.SimpleNamespace`, `wrap_method`
- L381–382 **`OrkestraSST.fase_sumber_daya_dan_kontrak.Sasaran.__init__`** · kontrol=0, assignment/delete=1, except=0 · Call: tidak ada
- L384–385 **`OrkestraSST.fase_sumber_daya_dan_kontrak.nilai_baru`** · kontrol=0, assignment/delete=0, except=0 · Call: tidak ada
- L398–399 **`OrkestraSST.fase_sumber_daya_dan_kontrak.pembungkus`** · kontrol=0, assignment/delete=0, except=0 · Call: `asli`
- L465–665 **`OrkestraSST.fase_inti_dan_kepribadian`** · kontrol=12, assignment/delete=28, except=0 · Call: `Keadaan.dari_mood`, `Naluri`, `Naluri.from_dict`, `Naluri.from_json`, `Persona`, `_cek`, `abs`, `bool`, `buat_npc`, `callable`, `hasattr`, `isinstance`, `iter`, `len`, `m.modulation`, `max`, `min`, `n.add_lexicon`, `n.advance_stage_by_ticks`, `n.apply_memory_policy`, `n.apply_to_brain`, `n.assign_delayed_credit`, `n.bayar_utang`, `n.berinteraksi`, `n.calibration_error`, `n.catat_utang`, `n.choose_action`, `n.clear_context`, `n.complete_subgoal`, `n.coping_state`, `n.counterfactual_rehearsal`, `n.deficit`, `n.delta`, `n.describe_personality`, `n.distract`, `n.dream_policy`, `n.drive_targeted_scenario`, `n.emosi.values`, `n.emosi_dominan`, `n.emosi_state`, `n.enable_coping`, `n.enable_emosi`, `n.enable_nurani`, `n.enable_profiling`, `n.enable_replay`, `n.estimate_other_belief`, `n.estimate_scale`, `n.export_replay`, `n.feel`, `n.goal_to_scenario`, `n.hancurkan_kepercayaan`, `n.heavy_computation`, `n.hud_state`, `n.impact_of`, `n.intent`, `n.kenal`, `n.kompres_memori`, `n.levels.keys`, `n.lod_status`, `n.memory_policy`, `n.menarik_diri`, `n.mood`, `n.mood_label`, `n.note_prediction`, `n.observe_other_belief`, `n.observe_outcome`, `n.personality_presets`, `n.post_sleep`, `n.profile_report`, `n.project_outcome_to_drives`, `n.reappraise`, `n.record_action`, `n.relasi`, `n.relasi(lawan).get`, `n.remember_context`, `n.replay`, `n.resonant_recalibration`, `n.reward_for`, `n.salience`, `n.scoring_func`, `n.seed_backstory`, `n.set_lexicon`, `n.set_lod`, `n.set_personality`, `n.set_personality_preset`, `n.set_sleep_mode`, `n.set_stage`, `n.set_subgoal`, `n.set_tag_lexicon`, `n.set_watak`, `n.should_sleep`, `n.sleep_status`, `n.status`, `n.subjective_time_state`, `n.suppress`, `n.tandai_momen`, `n.tick`, `n.tick_light`, `n.to_dict`, `n.to_json`, `n.use_lexicon_pack`, `n.utility`, `n.watak_aktif`, `next`, `periksa_impak`, `persona.to_dict`, `pilihan.get`, `range`, `self._t`, `set`, `types.SimpleNamespace`
- L668–748 **`OrkestraSST.fase_kesadaran_presentasi_sosial`** · kontrol=2, assignment/delete=6, except=0 · Call: `KawananNPC`, `Reputasi`, `_cek`, `k.attention_state`, `k.audition_self`, `k.core_memory_state`, `k.daftar_lantai_kesadaran`, `k.form_identity`, `k.inner_speech`, `k.narrative_state`, `k.observe_event`, `k.set_konteks_lantai`, `k.submit`, `k.tandai_core_memory`, `k.workspace_report`, `kawanan.biarkan_bersosialisasi`, `kawanan.broadcast`, `kawanan.catat_rumor`, `kawanan.emotional_contagion`, `kawanan.enable_reputasi`, `kawanan.form_cultural_norms`, `kawanan.hud_all`, `kawanan.interaksi`, `kawanan.reputasi_semua`, `kawanan.serap`, `kawanan.social_learn`, `kawanan.tambah`, `kawanan.teaching`, `kawanan.tick_all`, `n.enable_kesadaran`, `n.enable_presentasi`, `n.enable_ritual`, `n.lakukan_ritual`, `n.ritual.maybe_trigger`, `n.ritual.refresh_archetype`, `n.ritual.state`, `p.ekspresi`, `p.gestur`, `p.indikator_psikologis`, `p.jarak`, `p.koreksi_ingatan`, `p.lihat_player`, `p.napas`, `p.postur`, `p.proaktif`, `p.set_jejak`, `p.tag_dialog`, `p.tatapan`, `p.terima_bukti`, `p.ucap`, `range`, `rep.catat`, `rep.decay`, `rep.konsensus`, `rep.report`, `rep.sebar`, `self._t`
- L751–785 **`OrkestraSST.fase_dunia`** · kontrol=1, assignment/delete=8, except=0 · Call: `Lingkungan`, `Lingkungan.from_dict`, `Peta.dari_ascii`, `_cek`, `dunia.aksi_tersedia`, `dunia.fase`, `dunia.jalankan`, `dunia.konteks`, `dunia.langkah`, `dunia.observasi`, `dunia.paparan`, `dunia.peristiwa_lingkungan`, `dunia.pilih_aksi`, `dunia.tambah_npc`, `dunia.tambah_objek`, `dunia.terapkan`, `dunia.to_dict`, `peta.didalam`, `peta.simbol`, `peta_contoh`, `peta_kecil.simbol`, `self._t`
- L788–881 **`OrkestraSST.fase_bahasa`** · kontrol=11, assignment/delete=18, except=0 · Call: `'{} unik dari 20 pada NPC utama'.format`, `GenContext`, `LeksikonCiri.from_dict`, `SASPAnalyzer`, `TuturEngine`, `_cek`, `all`, `analisis.analisis`, `analisis_teks`, `any`, `engine.info`, `engine.tersedia`, `engine.ucap`, `engine_subjek.ucap`, `fitur.polaritas`, `isinstance`, `jalur_leksikon`, `konteks_dari_presentasi`, `len`, `lx.to_dict`, `range`, `sa_sp`, `sa_sp_literal`, `sa_sp_pragmatik`, `self._t`, `self.n.presentasi.tutur_engine`, `teks_api.JejakLinguistik`, `teks_api.JejakLinguistik().to_dict`, `teks_api.analisis_ujaran`, `teks_api.cakupan_negasi`, `teks_api.deteksi_bahasa`, `teks_api.ekstrak_entitas`, `teks_api.ekstrak_topik`, `teks_api.jejak_pembentukan`, `teks_api.jenis_kalimat`, `teks_api.jenis_pertanyaan`, `teks_api.jenis_pertanyaan('apa kabar?').get`, `teks_api.kandidat_dasar`, `teks_api.kemiripan`, `teks_api.koreksi_ejaan`, `teks_api.normalisasi_teks`, `teks_api.normalisasi_token`, `teks_api.pecah_kalimat`, `teks_api.periksa_gramatika`, `teks_api.potong_batas_kata`, `teks_api.stem`, `teks_api.tindak_tutur_skor`, `teks_api.tokenisasi`, `teks_api.urai_subjek_predikat`, `token_dari`, `urai.get`
- L884–1002 **`OrkestraSST.fase_memori`** · kontrol=3, assignment/delete=13, except=0 · Call: `JejakPrediksi`, `_cek`, `isinstance`, `jejak.autobiographical_timeline`, `jejak.autobiography_state`, `jejak.close_chapter`, `jejak.confabulate`, `jejak.consolidate_memory`, `jejak.counterfactual_emotions`, `jejak.curiga`, `jejak.detect_patterns`, `jejak.enable_recall_rewrite`, `jejak.experience`, `jejak.forget`, `jejak.forget_patterns`, `jejak.future_simulation`, `jejak.half_life_episode`, `jejak.ingat_kembali`, `jejak.kepercayaan`, `jejak.kepercayaan_state`, `jejak.koreksi_salah`, `jejak.life_chapters`, `jejak.nekropolis_state`, `jejak.observe_actor`, `jejak.open_chapter`, `jejak.pattern_report`, `jejak.perbarui_kepercayaan`, `jejak.performance_report`, `jejak.predict`, `jejak.rank_actions`, `jejak.reconsolidasi_state`, `jejak.record_experience`, `jejak.register_counterfactual`, `jejak.reinforce`, `jejak.save`, `jejak.set_retrieve_mode`, `jejak.tetapkan_kepercayaan`, `jejak.to_dict`, `jejak.to_json`, `jejak.waktu_state`, `n.attach_jejak`, `n.kawanan.laporan_prediksi`, `n.kawanan.prediksi_all`, `n.kawanan.tick_all`, `n.set_lod`, `os.path.join`, `ranking.get`, `self._t`, `str`
- L1005–1111 **`OrkestraSST.fase_nurani`** · kontrol=2, assignment/delete=8, except=0 · Call: `_cek`, `all`, `keadaan_pilar.values`, `n.enable_nurani`, `nur.anticipate`, `nur.anticipate_words`, `nur.any_enabled`, `nur.bayar_utang`, `nur.belajar_persepsi`, `nur.break_trust`, `nur.calibration_report`, `nur.circadian_phase`, `nur.classify_source`, `nur.compromise_bonus`, `nur.confabulation`, `nur.decay_social`, `nur.detect_conflict`, `nur.deteksi`, `nur.enabled`, `nur.evaluasi_diri`, `nur.experience`, `nur.felt_consciousness`, `nur.felt_report`, `nur.flow_reward_bonus`, `nur.flow_state`, `nur.forget_affective`, `nur.habit_factor`, `nur.holdout_brier`, `nur.inner_speech`, `nur.interoceptive_echo`, `nur.introspeksi_state`, `nur.kesadaran_laporan`, `nur.meet`, `nur.meta_kognisi_laporan`, `nur.meta_status`, `nur.metacognitive_doubt`, `nur.moral_emotion`, `nur.narrate_identity`, `nur.night_energy_shift`, `nur.note_conflict`, `nur.observe_other_belief`, `nur.peka_terhadap`, `nur.persepsi_ringkas`, `nur.reality_monitoring`, `nur.record_observation`, `nur.record_uncertainty`, `nur.refleksi_diri`, `nur.relationship`, `nur.relative_deficit`, `nur.sadar_diri`, `nur.scale_from_holdout`, `nur.sensitivitas_kategori`, `nur.serap_kategori`, `nur.set_kacamata_sosial`, `nur.somatic_bias`, `nur.somatic_mark`, `nur.source_memory`, `nur.tambah_utang`, `nur.to_dict`, `nur.to_json`, `nur.update_adaptasi`, `nur.update_felt`, `nur.update_interoception`, `nur.update_introspection`, `nur.update_setpoints`, `nur.warmup_from_log`, `self._t`, `type`, `type(nur).from_dict`, `type(nur).from_json`, `types.SimpleNamespace`
- L1114–1201 **`OrkestraSST.fase_mandiri`** · kontrol=0, assignment/delete=6, except=0 · Call: `KognisiLanjut`, `Organik`, `_cek`, `all`, `boltzmann_pilih`, `dict`, `domain._tepi`, `isinstance`, `k.aktif.values`, `k.aktifkan`, `k.eversi.eversi_param`, `k.eversi.update`, `k.graf.asosiasi`, `k.graf.koaktifkan`, `k.kepercayaan.entropi`, `k.kepercayaan.perbarui`, `k.kepercayaan.tetapkan`, `k.langkah`, `k.ou.langkah`, `o.apersepsi.amati`, `o.detak.maju`, `o.gejala.beri_nama`, `o.gejala.muncul`, `o.gejala.proses`, `o.gejala.state`, `o.identitas.catat_penolakan`, `o.identitas.izinkan`, `o.identitas.tetapkan`, `o.intrusi.coba`, `o.invensi.lahirkan`, `o.kausal.blame`, `o.kausal.counterfactual`, `o.kausal.jelaskan`, `o.kausal.pelajari`, `o.luka.lukai`, `o.luka.ringkas`, `o.luka.terapkan`, `o.paralel.bertentangan`, `o.paralel.tambah`, `o.perencana.maju`, `o.perencana.rancang`, `o.residu.daftar`, `o.residu.tambal`, `o.residu.tekanan`, `o.ringkas`, `o.topologi.isi_ulang`, `o.topologi.layak_cabang`, `o.topologi.terisi`, `o.tubuh.langkah`, `o.tubuh.masukan`, `o.tubuh.suntik`, `o.tutur.catat`, `o.tutur.kelayakan`, `o.vacancy.lewat`, `o.vacancy.mulai`, `o.waktu.daftar`, `o.waktu.dikoreksi_salah`, `o.waktu.skala_subjektif`, `self._t`
- L1204–1259 **`OrkestraSST.fase_ketidaktahuan_penilai`** · kontrol=4, assignment/delete=9, except=0 · Call: `'sekarang suasana berubah perlahan nomor {}'.format`, `ContohLabel`, `PelacakSelaras`, `_cek`, `all`, `batas_pengetahuan`, `contoh_dari_dict`, `isinstance`, `jalur_korpus`, `kappa_cohen`, `laporan.skor_dimensi`, `laporan_kalibrasi`, `len`, `muat_korpus`, `nilai_selaras`, `pelacak.catat`, `pelacak.tren`, `range`, `self._t`, `sikap_ketidaktahuan`, `tren.values`, `ukur_fitur`, `ukur_selaras`
- L1263–1298 **`OrkestraSST.fase_tutup`** · kontrol=6, assignment/delete=8, except=0 · Call: `'periksa kesehatan lulus semua: {}'.format`, `'{} cek lulus'.format`, `Naluri.from_dict`, `Naluri.from_json`, `Naluri.from_json(n.to_json()).status`, `Naluri.load`, `_cek`, `all`, `isinstance`, `len`, `n.batasi_memori`, `n.health_check`, `n.memori_state`, `n.save`, `n.to_dict`, `n.to_json`, `os.path.join`, `patch.dict`, `periksa.jalankan`, `pulih.to_dict`, `self._t`, `tempfile.TemporaryDirectory`
- L1309–1312 **`SSTOrkestraTest.setUpClass`** · kontrol=1, assignment/delete=2, except=0 · Call: `OrkestraSST`, `cls.orkestra.jalankan`, `contextlib.redirect_stdout`, `io.StringIO`
- L1314–1319 **`SSTOrkestraTest.test_tidak_ada_fitur_tertinggal`** · kontrol=0, assignment/delete=1, except=0 · Call: `'fitur wajib belum aktif: {}'.format`, `himpunan_fitur_wajib`, `self.assertEqual`, `self.ledger.aktif`, `self.ledger.kurang`, `set`, `sorted`
- L1321–1325 **`SSTOrkestraTest.test_setiap_fitur_punya_bukti`** · kontrol=2, assignment/delete=0, except=0 · Call: `'{} aktif tanpa bukti'.format`, `himpunan_fitur_wajib`, `self.assertTrue`, `self.ledger.bukti`, `self.subTest`, `sorted`
- L1327–1337 **`SSTOrkestraTest.test_api_publik_tercakup_manifest`** · kontrol=1, assignment/delete=3, except=0 · Call: `'fitur tujuan tidak ada di manifest: {}'.format`, `CAKUPAN_API.values`, `himpunan_fitur_wajib`, `self.assertEqual`, `self.assertTrue`, `set`, `sorted`
- L1339–1347 **`SSTOrkestraTest.test_api_publik_benar_benar_aktif`** · kontrol=2, assignment/delete=1, except=0 · Call: `'API {} tidak tersentuh (fitur {})'.format`, `CAKUPAN_API.items`, `himpunan_fitur_wajib`, `self.assertIn`, `self.ledger.aktif`, `self.subTest`, `sorted`
- L1349–1354 **`SSTOrkestraTest.test_fase_terlaksana_berurutan`** · kontrol=2, assignment/delete=3, except=0 · Call: `jejak.index`, `min`, `self.assertEqual`, `sorted`
- L1356–1359 **`SSTOrkestraTest.test_laporan_menyebut_semua_fitur`** · kontrol=1, assignment/delete=1, except=0 · Call: `himpunan_fitur_wajib`, `self.assertIn`, `self.ledger.laporan`, `sorted`
- L1365–1370 **`SSTPengamanTest.test_ledger_menolak_nama_kosong`** · kontrol=2, assignment/delete=1, except=0 · Call: `LedgerFitur`, `ledger.aktif`, `ledger.tandai`, `self.assertEqual`, `self.assertRaises`, `self.subTest`, `set`
- L1372–1377 **`SSTPengamanTest.test_ledger_menolak_bukti_kosong`** · kontrol=2, assignment/delete=1, except=0 · Call: `LedgerFitur`, `ledger.aktif`, `ledger.tandai`, `self.assertEqual`, `self.assertRaises`, `self.subTest`, `set`
- L1379–1384 **`SSTPengamanTest.test_label_tidak_dikenal_ditolak`** · kontrol=1, assignment/delete=1, except=0 · Call: `OrkestraSST`, `orkestra._t`, `orkestra.ledger.aktif`, `self.addCleanup`, `self.assertEqual`, `self.assertRaisesRegex`, `set`
- L1386–1394 **`SSTPengamanTest.test_fitur_tidak_dijalankan_menggagalkan_orkestra`** · kontrol=2, assignment/delete=2, except=0 · Call: `OrkestraSST`, `fase.split`, `orkestra.jalankan`, `os.path.exists`, `self.assertFalse`, `self.assertRaisesRegex`, `setattr`
- L1396–1406 **`SSTPengamanTest.test_kegagalan_fase_membersihkan_sumber_daya`** · kontrol=1, assignment/delete=3, except=0 · Call: `OrkestraSST`, `RuntimeError`, `orkestra.jalankan`, `os.path.exists`, `self.assertFalse`, `self.assertRaisesRegex`
- L1400–1401 **`SSTPengamanTest.test_kegagalan_fase_membersihkan_sumber_daya.gagal`** · kontrol=0, assignment/delete=0, except=0 · Call: `RuntimeError`
- L1408–1414 **`SSTPengamanTest.test_sukses_membersihkan_sumber_daya`** · kontrol=1, assignment/delete=3, except=0 · Call: `OrkestraSST`, `contextlib.redirect_stdout`, `himpunan_fitur_wajib`, `io.StringIO`, `ledger.aktif`, `orkestra.jalankan`, `os.path.exists`, `self.assertEqual`, `self.assertFalse`
- L1420–1434 **`SSTKlasifikasiTest.test_showcase_demo_diklasifikasi`** · kontrol=7, assignment/delete=2, except=0 · Call: `ast.parse`, `ast.walk`, `ditemukan.add`, `f.read`, `isinstance`, `nama.endswith`, `open`, `os.path.join`, `os.walk`, `self.assertEqual`, `set`, `simpul.name.startswith`
- L1436–1440 **`SSTKlasifikasiTest.test_tidak_ada_nama_fitur_ganda`** · kontrol=1, assignment/delete=1, except=0 · Call: `FITUR_WAJIB.values`, `len`, `self.assertEqual`, `set`, `total.extend`

## `tests/test_struktur_kognitif.py`

SHA-256: `bdc94d06f8845c638c5999731ec7920285657dbb71aa15bc3a66e9136bdeea9d`

946 baris; 16 kelas; 42 fungsi/metode termasuk nested.

Kelas: `NekropolisDanRecallTest` L26, `LantaiKesadaranDanReportTest` L81, `SyokDanKacamataTest` L117, `VacancyTest` L158, `GejalaMurniPipelineTest` L191, `PelindungIlusiTest` L310, `WaktuSubjektifTest` L444, `TubuhTakDapatDitukarTest` L492, `KelelahanAtensiTest` L519, `PenahananSadarTest` L575, `AudisiDiriTest` L625, `SaSpTest` L714, `StrategiSosialTest` L760, `EpistemicAndOpacityTest` L823, `AestheticsAndBoredomTest` L843, `SleepInsightAndFreeWillTest` L869.
Handler luas: tidak ada.

Impor (termasuk lazy/TYPE_CHECKING): `from __future__ import annotations`; `from pycos.bahasa.tutur import GenContext, L2, SASPAnalyzer, Slot, sa_sp, sa_sp_literal, sa_sp_pragmatik`; `from pycos.inti import KawananNPC, Naluri`; `from pycos.memori import JejakPrediksi`; `from pycos.refleksi import Nurani`; `import json`; `import os`; `import random`; `import sys`; `import unittest`.

- L27–55 **`NekropolisDanRecallTest.test_mati_diketahui_berbeda_dari_tidak_pernah_tahu`** · kontrol=0, assignment/delete=5, except=0 · Call: `JejakPrediksi`, `JejakPrediksi.from_dict`, `j._retrieve`, `j.nekropolis_state`, `j.predict`, `j.rank_actions`, `j.record_experience`, `j.to_dict`, `pulih._retrieve`, `self.assertEqual`, `self.assertIsNone`, `self.assertNotIn`, `self.assertTrue`
- L57–78 **`NekropolisDanRecallTest.test_rewrite_recall_default_mati_dan_gate_mengubah_episode`** · kontrol=0, assignment/delete=6, except=0 · Call: `JejakPrediksi`, `Naluri`, `normal._retrieve`, `normal.record_experience`, `rekonstruktif._retrieve`, `rekonstruktif.record_experience`, `self.assertAlmostEqual`, `self.assertEqual`, `self.assertGreater`, `self.assertIn`
- L82–98 **`LantaiKesadaranDanReportTest.test_lantai_memblokir_sebelum_kandidat_dan_residu_menggeser`** · kontrol=2, assignment/delete=4, except=0 · Call: `Naluri`, `diblokir.get`, `k._candidates`, `k.daftar_lantai_kesadaran`, `k.submit`, `lolos.get`, `n.daftarkan_residu`, `self.assertFalse`, `self.assertIn`, `self.assertNotIn`, `self.assertTrue`, `x.get`
- L100–114 **`LantaiKesadaranDanReportTest.test_tak_dapat_dilaporkan_tetap_di_spotlight_dan_kausal`** · kontrol=1, assignment/delete=4, except=0 · Call: `Naluri`, `k.attend`, `k.decision_bias`, `k.inner_speech`, `k.submit`, `k.workspace_report`, `self.assertEqual`, `self.assertGreater`, `self.assertNotIn`, `x.get`
- L118–136 **`SyokDanKacamataTest.test_syok_membatalkan_kopling_dan_mengguncang_d_prime`** · kontrol=5, assignment/delete=6, except=0 · Call: `Nurani`, `all`, `len`, `nu._sens`, `nu.advance_perception_tick`, `nu.structural_surprise`, `range`, `self.assertIsNotNone`, `self.assertNotEqual`, `self.assertTrue`
- L138–155 **`SyokDanKacamataTest.test_kacamata_tidak_hilang_oleh_satu_bukti`** · kontrol=2, assignment/delete=5, except=0 · Call: `Nurani`, `nu.kacamata_sosial_state`, `nu.observe_other_belief`, `nu.set_kacamata_sosial`, `range`, `self.assertAlmostEqual`, `self.assertGreater`, `self.assertLess`, `self.assertNotEqual`
- L159–188 **`VacancyTest.test_vacancy_hanya_waktu_dan_decay_dasar`** · kontrol=0, assignment/delete=8, except=0 · Call: `Naluri`, `Naluri.from_dict`, `dict`, `len`, `list`, `n.mulai_vacancy`, `n.tick`, `n.to_dict`, `n.vacancy_state`, `restored.vacancy_state`, `self.assertAlmostEqual`, `self.assertEqual`, `self.assertFalse`
- L194–199 **`GejalaMurniPipelineTest._npc`** · kontrol=0, assignment/delete=1, except=0 · Call: `Naluri`, `n.enable_kesadaran`, `n.enable_presentasi`
- L201–239 **`GejalaMurniPipelineTest.test_gagal_diklaim_adalah_state_dan_proto_mengkristal`** · kontrol=7, assignment/delete=6, except=0 · Call: `c.get`, `n.gejala_rasakan`, `n.gejala_state`, `n.nurani.peka_terhadap`, `n.tick`, `range`, `self._npc`, `self.assertEqual`, `self.assertGreater`, `self.assertIn`, `self.assertIsNone`, `self.assertTrue`, `x.get`
- L241–261 **`GejalaMurniPipelineTest.test_pemudaran_ke_residu_dan_klaim_oleh_drive`** · kontrol=3, assignment/delete=5, except=0 · Call: `list`, `n._gejala_hasil.get`, `n._gejala_hasil.keys`, `n._organik.residu.state`, `n.gejala_rasakan`, `n.gejala_state`, `n.tick`, `pipa.get`, `range`, `self._npc`, `self.assertEqual`, `self.assertTrue`, `str`
- L263–281 **`GejalaMurniPipelineTest.test_proto_mendapat_nama_sementara_dari_tutur`** · kontrol=2, assignment/delete=2, except=0 · Call: `' '.join`, `Naluri`, `c.get`, `n.enable_kesadaran`, `n.enable_presentasi`, `n.gejala_rasakan`, `n.gejala_state`, `n.tick`, `range`, `self.assertEqual`, `self.assertIn`, `self.assertTrue`, `str`
- L283–296 **`GejalaMurniPipelineTest.test_tanda_terklaim_menjadi_sesuatu_yang_dikenal`** · kontrol=0, assignment/delete=3, except=0 · Call: `lagi.get`, `n.gejala_rasakan`, `n.gejala_state`, `n.tick`, `self._npc`, `self.assertEqual`, `self.assertFalse`, `self.assertGreaterEqual`, `self.assertTrue`
- L298–307 **`GejalaMurniPipelineTest.test_serialisasi_gejala_dan_bekas`** · kontrol=3, assignment/delete=2, except=0 · Call: `Naluri.from_dict`, `m.gejala_state`, `n.gejala_rasakan`, `n.gejala_state`, `n.tick`, `n.to_dict`, `range`, `self._npc`, `self.assertEqual`
- L313–319 **`PelindungIlusiTest._npc`** · kontrol=0, assignment/delete=1, except=0 · Call: `Naluri`, `n.enable_kesadaran`, `n.enable_presentasi`, `n.set_personality_preset`
- L321–328 **`PelindungIlusiTest.test_watak_kegagalan_berbeda_tiap_preset`** · kontrol=0, assignment/delete=0, except=0 · Call: `self._npc`, `self._npc('dingin').presentasi.watak_kegagalan`, `self._npc('paranoid').presentasi.watak_kegagalan`, `self._npc('pemimpi').presentasi.pidato_gagal`, `self._npc('pengrajin').presentasi.watak_kegagalan`, `self.assertEqual`, `self.assertTrue`
- L330–340 **`PelindungIlusiTest.test_jeda_bermakna_korelasi_dengan_state_dan_deterministik`** · kontrol=0, assignment/delete=6, except=0 · Call: `p.jeda_bermakna`, `self._npc`, `self.assertEqual`, `self.assertGreater`, `self.assertIn`, `self.assertTrue`
- L342–356 **`PelindungIlusiTest.test_penyaring_meta_tidak_membocorkan_state_internal`** · kontrol=0, assignment/delete=4, except=0 · Call: `p.saring_meta`, `self._npc`, `self.assertEqual`, `self.assertIn`, `self.assertNotIn`, `self.assertNotRegex`, `self.assertTrue`
- L358–374 **`PelindungIlusiTest.test_eskalasi_variasi_empat_tingkat`** · kontrol=2, assignment/delete=7, except=0 · Call: `info.get`, `int`, `max`, `p.eskalasi_variasi`, `range`, `self._npc`, `self.assertEqual`, `self.assertGreater`, `self.assertIn`, `self.assertTrue`, `tingkat.append`
- L376–389 **`PelindungIlusiTest.test_buffer_manusiawi_dan_adversarial`** · kontrol=0, assignment/delete=5, except=0 · Call: `entry.get`, `n.tick`, `p.serap_adversarial`, `p.tandai_lupa`, `p.ucap`, `self._npc`, `self.assertEqual`, `self.assertIn`, `self.assertTrue`
- L391–405 **`PelindungIlusiTest.test_degradasi_anggun_bertingkat`** · kontrol=3, assignment/delete=8, except=0 · Call: `entry.get`, `list`, `p.degradasi_state`, `p.ucap`, `range`, `self._npc`, `self.assertEqual`, `self.assertTrue`
- L407–431 **`PelindungIlusiTest.test_keragaman_lintas_npc_dan_monitor`** · kontrol=4, assignment/delete=7, except=0 · Call: `KawananNPC`, `kawanan.keragaman`, `kawanan.monitor_scene`, `kawanan.tambah`, `len`, `n.enable_pelindung`, `n.enable_presentasi`, `n.presentasi._history.append`, `n.presentasi.jeda_bermakna`, `n.presentasi.monitor_integritas`, `n.presentasi.monitor_integritas().periksa`, `range`, `self.assertEqual`, `self.assertIn`, `self.assertTrue`
- L433–441 **`PelindungIlusiTest.test_serialisasi_state_pelindung`** · kontrol=0, assignment/delete=3, except=0 · Call: `Naluri.from_dict`, `n.to_dict`, `p.dorong_geser`, `p.jeda_bermakna`, `self._npc`, `self.assertEqual`
- L445–478 **`WaktuSubjektifTest.test_keadaan_mengubah_half_life_dan_usia_recency`** · kontrol=1, assignment/delete=14, except=0 · Call: `JejakPrediksi`, `JejakPrediksi.from_dict`, `Naluri`, `jejak['bosan']._recency`, `jejak['bosan'].half_life_episode`, `jejak['netral'].half_life_episode`, `jejak['trauma']._recency`, `jejak['trauma'].half_life_episode`, `jejak['trauma'].to_dict`, `jejak[label].record_experience`, `pulih.half_life_episode`, `self.assertAlmostEqual`, `self.assertEqual`, `self.assertGreater`, `self.assertLess`
- L480–489 **`WaktuSubjektifTest.test_jam_subjektif_berintegrasi_dan_disimpan`** · kontrol=1, assignment/delete=4, except=0 · Call: `Naluri`, `Naluri.from_dict`, `n.subjective_time_state`, `n.tick`, `n.to_dict`, `range`, `self.assertAlmostEqual`, `self.assertLess`
- L493–516 **`TubuhTakDapatDitukarTest.test_lokus_tubuh_membatasi_imajinasi_tanpa_memblokir_model_sosial`** · kontrol=0, assignment/delete=8, except=0 · Call: `Naluri`, `Naluri.from_dict`, `ks.body_locus_state`, `ks.constrain_imagination`, `ks.future_simulation`, `ks.imagine_from_body`, `ks.update_body_locus`, `n.to_dict`, `pulih.kesadaran.body_locus_state`, `self.assertEqual`, `self.assertFalse`, `self.assertGreater`, `self.assertTrue`
- L520–572 **`KelelahanAtensiTest.test_beban_percakapan_memodulasi_recall_lexical_dan_attend`** · kontrol=3, assignment/delete=18, except=0 · Call: `GenContext`, `JejakPrediksi`, `L2`, `Naluri`, `Naluri.from_dict`, `Slot`, `l2._skor`, `lelah.enable_kesadaran`, `lelah.enable_presentasi`, `lelah.kesadaran.attend`, `lelah.kesadaran.attention_state`, `lelah.presentasi.dengar`, `lelah.presentasi.ucap`, `lelah.to_dict`, `len`, `memory.record_experience`, `memory_fresh._retrieve`, `memory_tired._retrieve`, `random.Random`, `range`, `segar.enable_kesadaran`, `segar.enable_presentasi`, `segar.kesadaran.attend`, `segar.kesadaran.attention_state`, `self.assertAlmostEqual`, `self.assertEqual`, `self.assertGreater`, `self.assertLess`
- L576–622 **`PenahananSadarTest.test_dorongan_tutur_ditahan_sakitnya_terakumulasi_dan_tidak_dapat_dipaksa`** · kontrol=2, assignment/delete=11, except=0 · Call: `Naluri`, `Naluri.from_dict`, `entry.get`, `hasil.append`, `ks.choose_to_disclose`, `ks.withhold_speech`, `ks.withholding_state`, `n.enable_kesadaran`, `n.enable_presentasi`, `n.to_dict`, `p.dengar`, `p.ucap`, `pulih.kesadaran.choose_to_disclose`, `pulih.kesadaran.withholding_state`, `self.assertEqual`, `self.assertFalse`, `self.assertGreater`, `self.assertNotEqual`, `self.assertNotIn`, `self.assertTrue`
- L627–633 **`AudisiDiriTest._npc`** · kontrol=0, assignment/delete=1, except=0 · Call: `Naluri`, `n.enable_kesadaran`, `n.enable_presentasi`
- L635–659 **`AudisiDiriTest.test_ujaran_diproses_sebagai_suara_luar_bukan_inner_speech_atau_turn`** · kontrol=1, assignment/delete=7, except=0 · Call: `any`, `ks.self_audition_state`, `p.ucap`, `self._npc`, `self.assertEqual`, `self.assertFalse`, `self.assertGreaterEqual`, `self.assertLessEqual`, `self.assertNotIn`, `self.assertTrue`, `x.get`
- L661–679 **`AudisiDiriTest.test_audisi_mendeteksi_kesenjangan_niat_dan_kebohongan_diri`** · kontrol=1, assignment/delete=5, except=0 · Call: `any`, `dict`, `ks.audition_self`, `self._npc`, `self.assertEqual`, `self.assertGreater`, `self.assertLess`, `self.assertTrue`, `x.get`
- L681–703 **`AudisiDiriTest.test_malu_retroaktif_mengubah_tutur_berikutnya_dan_disimpan`** · kontrol=0, assignment/delete=8, except=0 · Call: `Naluri.from_dict`, `dipulihkan.kesadaran.self_audition_state`, `ks.audisi_diri`, `n.to_dict`, `p.prosodi`, `p.ucap`, `self._npc`, `self.assertEqual`, `self.assertGreater`, `self.assertGreaterEqual`, `self.assertLess`
- L705–711 **`AudisiDiriTest.test_sakelar_audisi_diri_bisa_diaktifkan_dengan_nama_indonesia`** · kontrol=0, assignment/delete=3, except=0 · Call: `Naluri`, `n.enable_kesadaran`, `n.kesadaran.audition_self`, `self.assertFalse`, `self.assertTrue`
- L715–745 **`SaSpTest.test_literal_terpisah_dari_maksud_dan_aksi_tersedia`** · kontrol=8, assignment/delete=8, except=0 · Call: `SASPAnalyzer`, `analyzer.analisis`, `any`, `maksud.get`, `sa_sp`, `sa_sp_literal`, `sa_sp_pragmatik`, `self.assertEqual`, `self.assertIn`, `self.assertNotEqual`, `self.assertNotIn`, `self.assertTrue`, `x.get`
- L747–757 **`SaSpTest.test_presentasi_dengar_mencatat_sa_sp_dengan_konteks`** · kontrol=0, assignment/delete=2, except=0 · Call: `Naluri`, `n.kesadaran.sa_sp_state`, `n.presentasi.dengar`, `self.assertEqual`, `self.assertIn`
- L761–763 **`StrategiSosialTest._npc`** · kontrol=0, assignment/delete=0, except=0 · Call: `Naluri`
- L765–797 **`StrategiSosialTest.test_kebohongan_sadar_permainan_peran_dan_manipulasi_diucapkan`** · kontrol=0, assignment/delete=7, except=0 · Call: `ks.choose_to_lie`, `ks.plan_manipulation`, `ks.roleplay`, `p.ucap`, `self._npc`, `self.assertEqual`, `self.assertNotIn`, `self.assertTrue`, `styled['teks'].startswith`
- L799–820 **`StrategiSosialTest.test_rahasia_ditahan_dan_kesetiaan_tidak_memakai_valensi`** · kontrol=0, assignment/delete=6, except=0 · Call: `ks.choose_loyalty`, `ks.choose_to_lie`, `ks.social_strategy_state`, `ks.withhold_speech`, `out.get`, `p.ucap`, `self._npc`, `self.assertEqual`, `self.assertFalse`, `self.assertNotIn`, `self.assertTrue`
- L824–840 **`EpistemicAndOpacityTest.test_emosi_epistemik_berbeda_dari_moral_dan_opasitas_menyimpan_latensi`** · kontrol=0, assignment/delete=4, except=0 · Call: `Naluri`, `ks.epistemic_emotion`, `ks.epistemic_emotion_state`, `ks.self_opacity`, `ks.self_opacity_state`, `self.assertEqual`, `self.assertGreater`, `self.assertNotIn`
- L844–866 **`AestheticsAndBoredomTest.test_bosan_menghasilkan_aksi_baru_dan_permainan_memegang_dua_frame`** · kontrol=2, assignment/delete=5, except=0 · Call: `Naluri`, `aksi.get`, `n.kesadaran.aesthetic_response`, `n.kesadaran.play_aesthetics_state`, `n.kesadaran.playful_reframe`, `n.presentasi.boredom_state`, `n.presentasi.perilaku_idle`, `range`, `self.assertGreater`, `self.assertIn`, `self.assertTrue`
- L870–882 **`SleepInsightAndFreeWillTest.test_tidur_menghasilkan_hipotesis_baru_dari_pengalaman`** · kontrol=0, assignment/delete=3, except=0 · Call: `Naluri`, `n.kesadaran.timeline.extend`, `n.post_sleep`, `self.assertEqual`, `self.assertIn`, `self.assertTrue`
- L884–912 **`SleepInsightAndFreeWillTest.test_state_baru_json_roundtrip`** · kontrol=0, assignment/delete=5, except=0 · Call: `Naluri`, `Naluri.from_dict`, `json.dumps`, `json.loads`, `ks.choose_to_lie`, `ks.epistemic_emotion`, `ks.free_will_choose_goal`, `ks.playful_reframe`, `ks.self_opacity`, `ks.timeline.extend`, `n.post_sleep`, `n.presentasi.dengar`, `n.to_dict`, `self.assertEqual`, `self.assertTrue`, `state.free_will_current_goal`, `state.insight_report`, `state.play_aesthetics_state`, `state.sa_sp_state`, `state.self_opacity_state`, `state.social_strategy_state`
- L914–942 **`SleepInsightAndFreeWillTest.test_free_will_memilih_tujuan_tanpa_drive_dan_mengarahkan_aksi`** · kontrol=1, assignment/delete=5, except=0 · Call: `Naluri`, `Naluri.from_dict`, `ks.free_will_decide_goal`, `n.choose_action`, `n.intent`, `n.to_dict`, `restored.kesadaran.free_will_current_goal`, `restored.kesadaran.free_will_state`, `self.assertEqual`, `self.assertFalse`, `self.assertGreater`, `self.assertTrue`

## `tests/test_struktur_paket.py`

SHA-256: `98d11d6a52b77b06923c52109c3003ffd6ee5b1839547f99020c3713f798f8ac`

374 baris; 4 kelas; 24 fungsi/metode termasuk nested.

Kelas: `SusunanBerkasTest` L72, `JalurImporTest` L123, `GayaBerkasTesTest` L226, `ApiPublikTest` L281.
Handler luas: tidak ada.

Impor (termasuk lazy/TYPE_CHECKING): `from __future__ import annotations`; `from pycos import bahasa, dukungan, inti, lingkungan, mandiri, memori, refleksi`; `from pycos.__main__ import utama`; `from pycos.dukungan.patching import optional_module`; `from pycos.mandiri.organik import TAK_BERLAKU`; `import ast`; `import contextlib`; `import importlib`; `import io`; `import os`; `import pycos`; `import subprocess`; `import sys`; `import unittest`.

- L61–63 **`berbeda`** · kontrol=0, assignment/delete=0, except=0 · Call: tidak ada
- L66–69 **`baca_ast`** · kontrol=1, assignment/delete=1, except=0 · Call: `ast.parse`, `f.read`, `open`, `os.path.join`
- L73–84 **`SusunanBerkasTest.test_setiap_subpaket_dan_modul_ada`** · kontrol=4, assignment/delete=1, except=0 · Call: `'pycos.{}'.format`, `'pycos/{} tanpa __init__.py'.format`, `PETA.items`, `os.path.isdir`, `os.path.isfile`, `os.path.join`, `self.assertTrue`, `self.subTest`
- L86–91 **`SusunanBerkasTest.test_modul_lama_tidak_lagi_di_akar`** · kontrol=2, assignment/delete=0, except=0 · Call: `'{}.py masih ada di akar repo'.format`, `os.path.exists`, `os.path.join`, `self.assertFalse`, `self.subTest`
- L93–97 **`SusunanBerkasTest.test_daftar_subpaket_tepat`** · kontrol=3, assignment/delete=1, except=0 · Call: `os.listdir`, `os.path.isdir`, `os.path.join`, `self.assertEqual`, `sorted`
- L99–114 **`SusunanBerkasTest.test_himpunan_berkas_persis_sesuai_peta`** · kontrol=5, assignment/delete=2, except=0 · Call: `'pycos/{}/__init__.py'.format`, `'pycos/{}/{}.py'.format`, `PETA.items`, `ada.add`, `berbeda`, `harus.add`, `harus.update`, `nama.endswith`, `os.path.join`, `os.path.relpath`, `os.path.relpath(os.path.join(direktori, nama), AKAR).replace`, `os.walk`, `self.assertEqual`, `set`
- L116–120 **`SusunanBerkasTest.test_sumber_daya_hanya_data_dan_init`** · kontrol=1, assignment/delete=2, except=0 · Call: `os.listdir`, `os.path.join`, `self.assertEqual`, `sorted`
- L124–128 **`JalurImporTest.test_nama_lama_gagal_sebagai_modul_datar`** · kontrol=3, assignment/delete=0, except=0 · Call: `__import__`, `self.assertRaises`, `self.subTest`
- L130–160 **`JalurImporTest.test_tidak_ada_impor_datar_atau_lintas_subpaket_relatif`** · kontrol=13, assignment/delete=5, except=0 · Call: `'{} memakai from .{} import lintas subpaket'.format`, `'{} memakai import {}'.format`, `'{} memakai impor datar {!r}'.format`, `(simpul.module or '').split`, `PETA.items`, `alias.name.split`, `ast.walk`, `baca_ast`, `isinstance`, `os.path.isfile`, `os.path.join`, `os.path.relpath`, `self.assertEqual`, `self.assertNotIn`, `self.subTest`, `set`
- L162–172 **`JalurImporTest.test_semua_submodul_terimpor_dengan_nama_baru`** · kontrol=3, assignment/delete=2, except=0 · Call: `'pycos.{}.{}'.format`, `'pycos/{}/{}.py'.format`, `PETA.items`, `importlib.import_module`, `m.__file__.replace`, `m.__file__.replace(os.sep, '/').endswith`, `self.assertEqual`, `self.assertTrue`, `self.subTest`, `sub.replace`
- L174–180 **`JalurImporTest.test_tidak_ada_sisa_package___package__`** · kontrol=4, assignment/delete=1, except=0 · Call: `'pycos/{}.py'.format`, `PETA.items`, `f.read`, `open`, `os.path.join`, `self.assertNotIn`, `self.subTest`
- L182–191 **`JalurImporTest.test_optional_module_menyelesaikan_nama_bertitik`** · kontrol=2, assignment/delete=1, except=0 · Call: `'{} tidak resolve'.format`, `optional_module`, `self.assertEqual`, `self.assertIsNone`, `self.assertIsNotNone`, `self.subTest`
- L193–205 **`JalurImporTest.test_lingkungan_tanpa_impor_lapisan_pycos_di_tingkat_atas`** · kontrol=6, assignment/delete=2, except=0 · Call: `'impor {} di tingkat atas'.format`, `alias.name.startswith`, `baca_ast`, `isinstance`, `penuh.startswith`, `self.assertFalse`
- L207–222 **`JalurImporTest.test_inti_tidak_mengimpor_lapisan_atas_secara_wajib`** · kontrol=5, assignment/delete=4, except=0 · Call: `ast.walk`, `baca_ast`, `dalam_try.add`, `isinstance`, `self.assertEqual`, `set`
- L235–239 **`GayaBerkasTesTest.berkas_tes`** · kontrol=2, assignment/delete=1, except=0 · Call: `n.endswith`, `n.startswith`, `os.listdir`, `os.path.join`, `sorted`
- L241–264 **`GayaBerkasTesTest.test_tidak_ada_impor_datar_atau_relatif`** · kontrol=10, assignment/delete=4, except=0 · Call: `'{} memakai import {}'.format`, `'{} memakai impor datar {!r}'.format`, `'{} memakai impor relatif from {}'.format`, `(simpul.module or '').split`, `PETA.values`, `alias.name.split`, `ast.parse`, `ast.walk`, `f.read`, `isinstance`, `open`, `os.path.relpath`, `self.assertFalse`, `self.assertNotIn`, `self.berkas_tes`
- L266–278 **`GayaBerkasTesTest.test_kepala_berkas_tes_seragam`** · kontrol=3, assignment/delete=3, except=0 · Call: `'{} tanpa deklarasi encoding'.format`, `'{} tanpa docstring modul'.format`, `ast.get_docstring`, `ast.parse`, `f.read`, `isi.startswith`, `open`, `os.path.relpath`, `self.assertIn`, `self.assertTrue`, `self.berkas_tes`, `self.subTest`
- L282–290 **`ApiPublikTest.test_nama_top_level_terselesaikan`** · kontrol=3, assignment/delete=0, except=0 · Call: `getattr`, `self.assertIs`, `self.assertIsNone`, `self.assertIsNotNone`, `self.subTest`
- L292–301 **`ApiPublikTest.test_impor_pycos_bersifat_malas`** · kontrol=0, assignment/delete=3, except=0 · Call: `ast.literal_eval`, `hasil.stdout.strip`, `self.assertEqual`, `self.assertIn`, `str`, `subprocess.run`
- L303–306 **`ApiPublikTest.test_nama_tidak_ada_memberi_attributeerror`** · kontrol=1, assignment/delete=0, except=0 · Call: `self.assertIn`, `self.assertRaises`, `str`
- L308–313 **`ApiPublikTest.test_dir_paket_memuat_api`** · kontrol=2, assignment/delete=1, except=0 · Call: `dir`, `self.assertIn`, `self.subTest`
- L315–342 **`ApiPublikTest.test_subpaket_mengekspor_api_terdokumentasi`** · kontrol=3, assignment/delete=1, except=0 · Call: `harapan.items`, `hasattr`, `self.assertIn`, `self.assertTrue`, `self.subTest`
- L344–354 **`ApiPublikTest.test___all___subpaket_dapat_diimpor`** · kontrol=3, assignment/delete=0, except=0 · Call: `'{} tanpa {}'.format`, `getattr`, `hasattr`, `self.assertTrue`, `self.subTest`
- L356–370 **`ApiPublikTest.test___main__mencetak_ringkasan`** · kontrol=3, assignment/delete=3, except=0 · Call: `buffer.getvalue`, `contextlib.redirect_stdout`, `io.StringIO`, `self.assertEqual`, `self.assertIn`, `self.subTest`, `utama`

## `tests/test_sumber_daya.py`

SHA-256: `607be284e85823f6a127864d3563aacb67cc58b4c5e49dc3d0a9c557fa175512`

174 baris; 3 kelas; 18 fungsi/metode termasuk nested.

Kelas: `JalurSumberDayaTest` L29, `IsiLeksikonTest` L89, `TuturDanLeksikonTest` L118.
Handler luas: tidak ada.

Impor (termasuk lazy/TYPE_CHECKING): `from __future__ import annotations`; `from pycos import sumber_daya as paket_sumber`; `from pycos.bahasa import GenContext, TuturEngine`; `from pycos.bahasa import TuturEngine`; `from pycos.dukungan.sumber import NAMA_KORPUS, NAMA_LEKSIKON, akar_paket, ada_sumber_daya, kandidat_leksikon, jalur_korpus, jalur_leksikon, sumber_daya`; `from pycos.dukungan.sumber import jalur_leksikon as jalur`; `import json`; `import os`; `import sys`; `import unittest`.

- L30–32 **`JalurSumberDayaTest.test_akar_paket_menunjuk_direktori_pycos`** · kontrol=0, assignment/delete=0, except=0 · Call: `akar_paket`, `os.path.basename`, `os.path.dirname`, `self.assertEqual`
- L34–36 **`JalurSumberDayaTest.test_direktori_sumber_daya_berada_dalam_paket`** · kontrol=0, assignment/delete=0, except=0 · Call: `akar_paket`, `os.path.join`, `self.assertEqual`, `sumber_daya`
- L38–43 **`JalurSumberDayaTest.test_jalur_leksikon_absolut_dan_bisa_dibaca`** · kontrol=0, assignment/delete=1, except=0 · Call: `ada_sumber_daya`, `jalur_leksikon`, `os.path.basename`, `os.path.isabs`, `os.path.join`, `self.assertEqual`, `self.assertTrue`, `sumber_daya`
- L45–54 **`JalurSumberDayaTest.test_jalur_korpus_absolut_dan_korpus_ikut_terpasang`** · kontrol=0, assignment/delete=1, except=0 · Call: `ada_sumber_daya`, `jalur_korpus`, `os.path.basename`, `os.path.isabs`, `os.path.isfile`, `os.path.join`, `self.assertEqual`, `self.assertFalse`, `self.assertTrue`, `sumber_daya`
- L56–62 **`JalurSumberDayaTest.test_konstanta_subpaket_sama_dengan_helper`** · kontrol=1, assignment/delete=0, except=0 · Call: `hasattr`, `jalur_leksikon`, `self.assertEqual`, `self.assertTrue`
- L64–72 **`JalurSumberDayaTest.test_kandidat_terurut_dan_bebas_duplikat`** · kontrol=0, assignment/delete=2, except=0 · Call: `jalur_leksikon`, `kandidat_leksikon`, `len`, `os.getcwd`, `os.path.join`, `self.assertEqual`, `set`
- L74–78 **`JalurSumberDayaTest.test_kandidat_tanpa_argumen_tetut_lengkap`** · kontrol=1, assignment/delete=1, except=0 · Call: `jalur_leksikon`, `kandidat_leksikon`, `self.assertFalse`, `self.assertIn`, `str`, `str(c).strip`
- L80–82 **`JalurSumberDayaTest.test_kandidat_menggabung_sumber_daya_tanpa_duplikat`** · kontrol=1, assignment/delete=1, except=0 · Call: `jalur_leksikon`, `kandidat_leksikon`, `self.assertEqual`, `sum`, `sumber_daya`
- L84–86 **`JalurSumberDayaTest.test_nama_berkas_dapat_diganti`** · kontrol=0, assignment/delete=0, except=0 · Call: `jalur_leksikon`, `os.path.join`, `self.assertEqual`, `sumber_daya`
- L90–92 **`IsiLeksikonTest.setUp`** · kontrol=1, assignment/delete=1, except=0 · Call: `jalur_leksikon`, `json.load`, `open`
- L94–98 **`IsiLeksikonTest.test_kunci_struktural_ada`** · kontrol=2, assignment/delete=0, except=0 · Call: `self.assertIn`, `self.subTest`
- L100–105 **`IsiLeksikonTest.test_jumlah_entri_sesuai_metadata`** · kontrol=0, assignment/delete=1, except=0 · Call: `int`, `len`, `self.assertEqual`
- L107–115 **`IsiLeksikonTest.test_pembagian_bahasa_sesuai_metadata`** · kontrol=2, assignment/delete=4, except=0 · Call: `entri.get`, `int`, `nyata.get`, `nyata.values`, `per_bahasa.items`, `self.assertEqual`, `sum`
- L119–128 **`TuturDanLeksikonTest.test_engine_muat_leksikon_paket`** · kontrol=0, assignment/delete=2, except=0 · Call: `GenContext`, `TuturEngine`, `engine.info`, `engine.tersedia`, `engine.ucap`, `jalur_leksikon`, `self.assertEqual`, `self.assertIsNotNone`, `self.assertTrue`
- L130–140 **`TuturDanLeksikonTest.test_peringatan_memasukkan_sebab_dari_spotlight`** · kontrol=0, assignment/delete=3, except=0 · Call: `GenContext`, `TuturEngine`, `engine.ucap`, `jalur_leksikon`, `self.assertIn`, `self.assertIsNotNone`, `self.assertNotIn`
- L142–147 **`TuturDanLeksikonTest.test_tanpa_path_engine_tidak_aktif`** · kontrol=0, assignment/delete=0, except=0 · Call: `TuturEngine`, `TuturEngine().tersedia`, `TuturEngine(path='leksikon-tidak-ada.json').tersedia`, `self.assertFalse`
- L149–159 **`TuturDanLeksikonTest.test_presentasi_menemukan_leksikon_paket_sendiri`** · kontrol=0, assignment/delete=3, except=0 · Call: `__import__`, `__import__('pycos.inti', fromlist=['Naluri']).Naluri`, `engine.tersedia`, `jalur`, `npc.presentasi.tutur_engine`, `os.path.realpath`, `self.assertEqual`, `self.assertIsNotNone`, `self.assertTrue`
- L161–170 **`TuturDanLeksikonTest.test_set_leksikon_menerima_path_eksplisit`** · kontrol=0, assignment/delete=5, except=0 · Call: `__import__`, `__import__('pycos.inti', fromlist=['Naluri']).Naluri`, `jalur_leksikon`, `npc.presentasi.set_leksikon`, `npc.presentasi.tutur_engine`, `self.assertIsNone`, `self.assertTrue`

## `tests/test_typing_lanjutan.py`

SHA-256: `c9bfccb8823d885fcc54bc36c9daa78ef3fbdcfdc7757e05535a5feaf9c2548a`

113 baris; 1 kelas; 9 fungsi/metode termasuk nested.

Kelas: `TypingLanjutanTest` L17.
Handler luas: tidak ada.

Impor (termasuk lazy/TYPE_CHECKING): `from __future__ import annotations`; `from pycos.bahasa.tutur import L3, GenContext, Slot, Kerangka, Node`; `from pycos.bahasa.tutur import L3, Node, GenContext`; `from pycos.bahasa.tutur import Leksikon`; `from pycos.inti.persona import PERSONA_CONTOH, Keadaan`; `from pycos.refleksi.nurani import ContohLabel, ukur_selaras, ukur_fitur`; `from pycos.refleksi.nurani import Nurani`; `from pycos.refleksi.nurani import nilai_selaras`; `import contextlib`; `import io`; `import os`; `import random`; `import sys`; `import unittest`.

- L19–25 **`TypingLanjutanTest.leksikon`** · kontrol=0, assignment/delete=0, except=0 · Call: `Leksikon`
- L27–36 **`TypingLanjutanTest.test_adjektiva_modifier_tanpa_kerangka_tidak_crash`** · kontrol=0, assignment/delete=4, except=0 · Call: `GenContext`, `Kerangka`, `L3`, `Node`, `Slot`, `random.Random`, `renderer.frasa_adjektiva`, `self.assertEqual`, `self.leksikon`
- L38–44 **`TypingLanjutanTest.test_morfologi_json_tetap_menghasilkan_string`** · kontrol=0, assignment/delete=1, except=0 · Call: `leks.nasalisasi`, `leks.nominalisasi`, `self.assertEqual`, `self.assertIsNone`, `self.leksikon`
- L46–54 **`TypingLanjutanTest.test_template_json_dan_polaritas`** · kontrol=0, assignment/delete=3, except=0 · Call: `GenContext`, `L3`, `Node`, `random.Random`, `renderer._render_ekspresi`, `self.assertEqual`, `self.leksikon`
- L56–63 **`TypingLanjutanTest.test_slot_relasi_optional_dan_utang`** · kontrol=0, assignment/delete=1, except=0 · Call: `Nurani`, `nur.menarik_diri`, `nur.tambah_utang`, `nur.utang_state`, `self.assertFalse`, `self.assertTrue`
- L65–75 **`TypingLanjutanTest.test_dimensi_bernilai_selalu_punya_observasi_dan_target`** · kontrol=4, assignment/delete=1, except=0 · Call: `Keadaan`, `all`, `isinstance`, `nilai_selaras`, `self.assertIsInstance`, `self.assertIsNotNone`, `self.assertTrue`
- L77–88 **`TypingLanjutanTest.test_label_optional_tidak_masuk_pemilihan_ambang`** · kontrol=0, assignment/delete=4, except=0 · Call: `ContohLabel`, `self.assertEqual`, `self.assertIn`, `ukur_fitur`, `ukur_selaras`
- L90–97 **`TypingLanjutanTest.test_kategori_proto_diulang_mempertahankan_tipe_record`** · kontrol=0, assignment/delete=3, except=0 · Call: `Nurani`, `nur.serap_kategori`, `self.assertEqual`, `self.assertGreater`
- L99–109 **`TypingLanjutanTest.test_showcase_nurani_berseed_dan_semua_pilar_terlapor`** · kontrol=2, assignment/delete=2, except=0 · Call: `Nurani.demo`, `contextlib.redirect_stdout`, `io.StringIO`, `self.assertEqual`, `self.assertGreater`, `self.assertIn`

## `tools/audit_python.py`

SHA-256: `64da067ab48e69fcb2acf82b4f18f8ee70c3fee3e7060653f58ac9a1b5c7d0ad`

141 baris; 1 kelas; 6 fungsi/metode termasuk nested.

Kelas: `IndeksCallable` L49.
Handler luas: tidak ada.

Impor (termasuk lazy/TYPE_CHECKING): `from __future__ import annotations`; `from pathlib import Path`; `from typing import List, Optional, Sequence, Tuple`; `import argparse`; `import ast`; `import hashlib`; `import os`.

- L29–46 **`inventaris`** · kontrol=6, assignment/delete=6, except=1 · Call: `'\n'.join`, `'{}: {}'.format`, `Path`, `ValueError`, `ast.parse`, `f.endswith`, `galat.append`, `hasil.append`, `jalur.read_text`, `jalur.relative_to`, `os.walk`, `paths.extend`, `sorted`, `str`
- L52–54 **`IndeksCallable.__init__`** · kontrol=0, assignment/delete=2, except=0 · Call: tidak ada
- L56–59 **`IndeksCallable.visit_ClassDef`** · kontrol=0, assignment/delete=0, except=0 · Call: `self.generic_visit`, `self.scope.append`, `self.scope.pop`
- L61–77 **`IndeksCallable.visit_FunctionDef`** · kontrol=6, assignment/delete=6, except=0 · Call: `', '.join`, `'- L{}–{} **{}** · kontrol={}, assignment/delete={}, except={} · Call: {}'.format`, `'.'.join`, `ast.unparse`, `ast.walk`, `isinstance`, `list`, `self.baris.append`, `self.generic_visit`, `self.scope.append`, `self.scope.pop`, `sorted`, `sum`, `x.replace`
- L82–114 **`laporan`** · kontrol=13, assignment/delete=8, except=0 · Call: `'## {}'.format`, `', '.join`, `'; '.join`, `'Jumlah berkas: **{}**.'.format`, `'SHA-256: {}'.format`, `'\n'.join`, `'{} L{}'.format`, `'{} baris; {} kelas; {} fungsi/metode termasuk nested.'.format`, `IndeksCallable`, `ast.unparse`, `ast.walk`, `baris.extend`, `hashlib.sha256`, `hashlib.sha256(teks.encode('utf-8')).hexdigest`, `inventaris`, `isinstance`, `jalur.as_posix`, `len`, `list`, `map`, `sorted`, `teks.encode`, `teks.splitlines`, `visitor.visit`
- L117–137 **`main`** · kontrol=5, assignment/delete=3, except=1 · Call: `ValueError`, `argparse.ArgumentParser`, `args.output.is_file`, `args.output.parent.mkdir`, `args.output.read_text`, `args.output.write_text`, `args.root.is_dir`, `args.root.resolve`, `laporan`, `parser.add_argument`, `parser.parse_args`, `print`, `str`

## `tools/periksa_changelog.py`

SHA-256: `f0235565e62f772b5b0fb3afcba07e6edc84f26cd4509487b33fb943564c7c9f`

67 baris; 0 kelas; 5 fungsi/metode termasuk nested.

Kelas: tidak ada.
Handler luas: tidak ada.

Impor (termasuk lazy/TYPE_CHECKING): `from __future__ import annotations`; `from pathlib import Path`; `from typing import Dict, List`; `import argparse`; `import ast`; `import subprocess`.

- L14–18 **`loaders`** · kontrol=2, assignment/delete=0, except=0 · Call: `ast.dump`, `ast.parse`, `ast.walk`, `isinstance`, `sorted`
- L21–27 **`unreleased`** · kontrol=2, assignment/delete=3, except=0 · Call: `'\n'.join`, `enumerate`, `len`, `lines[i].startswith`, `next`, `range`, `text.splitlines`
- L30–39 **`errors`** · kontrol=4, assignment/delete=3, except=0 · Call: `after.get`, `after.keys`, `any`, `before.get`, `before.keys`, `line.split`, `line.split(' — ', 1)[1].strip`, `line.startswith`, `loaders`, `set`, `sorted`, `unreleased`, `unreleased(new_log).splitlines`, `unreleased(old_log).splitlines`
- L42–44 **`git`** · kontrol=0, assignment/delete=0, except=0 · Call: `subprocess.run`
- L47–63 **`main`** · kontrol=3, assignment/delete=8, except=0 · Call: `(AKAR / 'CHANGELOG.md').read_text`, `(AKAR / 'pycos').rglob`, `argparse.ArgumentParser`, `bool`, `errors`, `git`, `git('ls-tree', '-r', '--name-only', args.base, '--', 'pycos').splitlines`, `int`, `log_paths.strip`, `p.endswith`, `p.read_text`, `p.relative_to`, `p.relative_to(AKAR).as_posix`, `parser.add_argument`, `parser.parse_args`, `print`

## `tools/periksa_gate.py`

SHA-256: `520195e9aa391c8ce04bb086869104c8b197c7bd9fa8a32960e6accc00d2c826`

105 baris; 0 kelas; 5 fungsi/metode termasuk nested.

Kelas: tidak ada.
Handler luas: tidak ada.

Impor (termasuk lazy/TYPE_CHECKING): `from __future__ import annotations`; `from pathlib import Path`; `from typing import Any, Dict, List, Optional`; `import argparse`; `import json`; `import math`.

- L15–21 **`_angka`** · kontrol=3, assignment/delete=0, except=1 · Call: `isinstance`, `math.isfinite`
- L24–29 **`target_coverage`** · kontrol=1, assignment/delete=0, except=0 · Call: `(AKAR / 'pycos' / 'dukungan').glob`, `p.relative_to`, `sorted`, `str`, `str(p.relative_to(AKAR)).replace`
- L32–53 **`coverage_errors`** · kontrol=6, assignment/delete=6, except=0 · Call: `'coverage: {} {:.2f}% < 80%'.format`, `errors.append`, `files.get`, `isinstance`, `item.get`, `report.get`, `summary.get`, `target_coverage`
- L56–77 **`tolok_errors`** · kontrol=9, assignment/delete=6, except=0 · Call: `'tolok: {} {}ms harus <{}ms'.format`, `BATAS_MS.items`, `_angka`, `errors.append`, `isinstance`, `len`, `report.get`, `row.get`
- L80–101 **`main`** · kontrol=7, assignment/delete=4, except=1 · Call: `'{}: {}'.format`, `ValueError`, `argparse.ArgumentParser`, `errors.append`, `errors.extend`, `isinstance`, `json.loads`, `parser.add_argument`, `parser.error`, `parser.parse_args`, `path.read_text`, `print`, `validator`
