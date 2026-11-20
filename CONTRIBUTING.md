# Berkontribusi pada Pycos

## Lingkungan dan batas desain

Gunakan Python ≥3.9; runtime hanya standard library. Dependensi pengembangan
bersifat opsional dan dipin pada `pyproject.toml`:

```sh
python -m venv .venv
. .venv/bin/activate
python -m pip install -e '.[dev]'
```

Pertahankan fasad impor malas, API publik, seed deterministik, dan flag
`enable_*` yang mati secara default. Jangan menyembunyikan regresi dengan
blanket ignore, mematikan tes SST, atau melonggarkan validasi persistence.

## Sebelum mengirim perubahan

```sh
python -m compileall -q pycos tests tools examples
python -m unittest discover -q
python -m pycos --periksa
python -m pycos.dukungan.leksikon --periksa
python -m mypy
python -m pyflakes $(find pycos tests tools examples -type f -name '*.py' ! -name '__init__.py' -print)
python tools/audit_python.py
python tools/audit_python.py --check
python -m coverage run --source=pycos,tools -m unittest discover -q
python -m coverage json -o coverage.json
python tools/periksa_gate.py --coverage coverage.json
python -m pycos.dukungan.tolok --json > tolok.json
python tools/periksa_gate.py --tolok tolok.json
```

Indeks AST digenerate dengan Python 3.11 agar render sama dengan CI; jangan
mengedit manual arsip audit historis. Laporan JSON benchmark/coverage bukan
source dan tidak perlu di-commit. Benchmark harus tanpa tracing coverage.
Mypy saat ini bertahap (18 berkas, termasuk konektor host), bukan klaim seluruh paket strict.
Coverage gate ≥80% berlaku pada daftar target `tools/periksa_gate.py`, bukan
rata-rata global. CI menguji Python 3.9–3.14; keberhasilan lokal satu interpreter
bukan bukti seluruh matrix lulus.

Tes baru mengikuti header encoding, docstring, future annotations dan bootstrap
root pada tes yang ada. Perubahan perilaku perlu tes positif dan negatif.
Gunakan direktori temporer untuk save; jangan menaruh dataset besar di Git.
Empat contoh dapat dijalankan dengan `python -m examples.<nama>`; baca
[examples/README.md](examples/README.md).

## Persistence dan changelog (wajib)

Setiap perubahan `from_dict` (termasuk tambah, hapus, atau pindah implementasi)
wajib menambahkan baris pada bagian **Unreleased** di `CHANGELOG.md`, dengan
format berikut untuk **setiap path Python yang terpengaruh**:

```text
- Kompatibilitas save: `pycos/lapisan/modul.py` — skema asal → tujuan;
  field/default yang berubah, migrasi atau penolakan yang disengaja, dampak save lama.
```

Jika tidak ada perubahan skema, tulis alasan kompatibilitas tetap terjaga.
Perubahan helper validasi, `to_dict`, profil save atau registry migrasi juga
wajib didokumentasikan meski gate otomatis hanya membandingkan AST `from_dict`.
Jangan menaikkan format tanpa migrasi eksplisit atau kebijakan penolakan jelas.
Tambahkan round-trip save/load, fixture lama/field hilang, dan input rusak.
Jangan mengedit berkas save ber-checksum untuk menyimulasikan versi lama tanpa
menghitung ulang checksum; gunakan snapshot di memori seperti contoh migrasi.

Periksa diff terhadap base PR yang sebenarnya, bukan selalu `HEAD~1`:

```sh
python tools/periksa_changelog.py --base <commit-base-PR>
```

Gate menuntut baris kompatibilitas **baru** pada Unreleased untuk setiap berkas
produksi yang AST `from_dict`-nya berubah. Baris lama tidak cukup. Gate tidak
memahami kebenaran klaim kompatibilitas: review manusia dan tes migrasi tetap
wajib. AST tidak mendeteksi perubahan helper tidak langsung.

## Pull request

Jelaskan tujuan, batas scope, dampak API/save, perintah validasi dan hasilnya.
Bedakan pengukuran lokal dari CI remote. Pakai heading Keep a Changelog
`Added`, `Changed`, `Deprecated`, `Removed`, `Fixed`, atau `Security` di Unreleased;
jangan membuat tanggal/versi rilis fiktif. Saat rilis, pindahkan catatan ke
versi/tanggal aktual dan buat Unreleased baru.

## Ekspor API publik

Ikuti [kebijakan ekspor](docs/API_PUBLIK.md): nama publik baru di `__all__`
subpaket harus mendapat alias root eksplisit atau pengecualian terdokumentasi.
Pertahankan impor malas dan identitas objek pemilik; jangan menimpa nama modul.
Perbarui pemetaan `CAKUPAN_API` SST ke kelompok fitur yang benar-benar aktif,
bukan sekadar menambah nama untuk meloloskan manifest.
