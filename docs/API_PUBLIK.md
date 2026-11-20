# Kebijakan API publik (R5.4)

## Aturan pemilihan

Root `pycos` menyediakan alias malas bagi nama yang dipublikasikan melalui
`__all__` tujuh subpaket: inti, refleksi, memori, mandiri, lingkungan, bahasa,
dan dukungan. Daftarnya **eksplisit** pada `_MODUL_NAMA` di `pycos/__init__.py`;
root tidak mengimpor subpaket untuk merakit registry pada runtime.

Dua pengecualian yang disengaja:

| Nama | Jalur yang dipertahankan | Alasan tidak di root |
|---|---|---|
| `demo` | `pycos.lingkungan.demo` | Entry point showcase, bukan primitif host; nama terlalu umum. |
| `sumber_daya` | `pycos.dukungan.sumber_daya` | Fungsi ini akan bertabrakan dengan modul data `pycos.sumber_daya`. |

API root yang sudah ada, termasuk kontrak dan view ketidaktahuan, dipertahankan.
Nama tidak dipromosikan hanya karena tidak berawalan underscore di implementasi:
`__all__` subpaket adalah batas seleksi, bukan seluruh isi modul.
Ekspor di root tidak mengubah dukungan serialization, thread safety, atau
status eksperimental algoritme. Nama yang belum diekspor tetap dapat diakses
melalui jalur implementasi, tetapi bukan otomatis API root.

## Hasil inventaris

Pada snapshot ini ada **66** nama publik subpaket yang belum diekspor root,
bukan persis 65 seperti estimasi rekomendasi. **64** dipromosikan dan **2**
dikecualikan seperti tabel di atas. Peningkatan sistem linguistik (tokenizer,
stemmer, negasi, pemeriksa gramatika, entitas/topik, jejak pembentukan)
menambahkan **22** nama publik dari `pycos.bahasa.teks` ke dua `__all__`;
semuanya dipromosikan root, sehingga total `pycos.__all__` menjadi **147**
nama (termasuk `__version__`). Angka ini inventaris bertahap, bukan batas
permanen.

Tambahan mencakup `EversiTD`, `Perencana`, `ModelKausal`, `GrafAsosiasi`, state
organik, data/komponen Tutur (`Arg`, `Node`, `L0`–`L3`, `Tutur`, `Leksikon`,
`Orkestrator`), utilitas fondasi teks (`tokenisasi`, `stem`, `periksa_gramatika`,
`cakupan_negasi`, `jenis_kalimat`, `tindak_tutur_skor`, `ekstrak_topik`,
`jejak_pembentukan`, …), utilitas kalibrasi, konstanta dunia, `Badan`,
`peta_contoh`, resolusi sumber daya dan `inventaris` patch. Tidak ada fungsi baru atau wrapper;
objek root identik dengan objek pemiliknya.

```python
from pycos import EversiTD, Perencana, ModelKausal, GrafAsosiasi
from pycos.mandiri import Perencana as PerencanaMandiri
assert Perencana is PerencanaMandiri
```

## Implikasi impor dan perubahan selanjutnya

- `import pycos` dan `dir(pycos)` hanya memuat root; akses atribut pertama
  memuat modul pemilik, lalu menyimpan objek pada globals root.
- `from pycos import *` sengaja memuat semua nama publik; bukan operasi malas
  atau janji startup murah. Pilih impor eksplisit untuk host produksi.
- Alias berbagi objek, termasuk konstanta mutable. Ekspor bukan salinan state;
  jangan memutasi konstanta bersama untuk konfigurasi per NPC.
- Tambahan `__all__` subpaket wajib diklasifikasikan: tambahkan alias root atau
  dokumentasikan pengecualian beserta tes. Jika dua subpaket menggunakan nama
  sama, identitas objek harus sama atau pilih jalur eksplisit, bukan menimpa
  alias root secara diam-diam.
- Nama modul subpaket/data tidak boleh ditimpa fungsi dengan nama sama.

`tests/test_api_publik.py` memeriksa klasifikasi **setiap** nama subpaket,
identitas alias, daftar unik, `dir`, cache, AttributeError, star import,
kelaziman impor root, dan benturan modul data dalam proses Python baru.
