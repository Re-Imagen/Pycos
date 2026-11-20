# VALIDATION — bukti implementasi dan regresi Pycos

## Validasi terkini

**Diverifikasi ulang lokal:** 2026-10-17, Python **3.11.2**. Source acuan:
`95cba32` (merge R5.4–R5.5); pembaruan ini hanya mengubah README dan VALIDATION.
Tanggal/rentang baris pada arsip di bawah bukan tanggal verifikasi atau lokasi
source terbaru. Dokumen ini menilai implementasi/regresi, **bukan validasi
ilmiah, kualitas dialog manusia, atau jaminan produksi**.

### Ringkasan hasil yang diukur ulang

| Pemeriksaan | Hasil lokal |
| --- | --- |
| Suite `unittest` di bawah coverage | **508 tes lulus**, 70,749 detik; 20 berkas tes, termasuk **14 SST** |
| Health check paket | **11 cek lulus** |
| Strict mypy 1.15.0 | **18 berkas lulus**; cakupan bertahap pada `pyproject.toml`, bukan seluruh paket |
| Pyflakes 4.0.3 | Lulus untuk `pycos`, `tools`, `tests`, `examples`, kecuali `__init__.py` yang sengaja re-export |
| Compileall | Lulus pada empat direktori source tersebut |
| Audit AST `--check` | Lulus; indeks **82 berkas Python**, mengecualikan environment/build/vendor/non-source |
| Changelog gate terhadap `HEAD` | Lulus; tidak ada perubahan loader pada pembaruan dokumentasi ini |
| Checker leksikon impak | Lulus; 653 entri ID/382 EN, termasuk 622/379 kata tunggal |
| Coverage per-file | Gate lulus; hasil rinci di bawah |
| Benchmark tanpa tracing | Gate tick/predict lulus; hasil rinci di bawah |
| Inspector HTML | `node tools/periksa_inspector.cjs` lulus dengan DOM tiruan |

### Coverage baris

Diukur dengan coverage **7.6.12**, `--source=pycos,tools`. Coverage global
**73,4312%**, bukan klaim ≥80% seluruh paket atau branch coverage. Floor ≥80%
berlaku pada daftar target eksplisit `tools/periksa_gate.py` (kelompok dukungan,
kontrak, persona, Nurani, Tutur, konektor, serta tool gate).

| Berkas | Coverage baris |
| --- | ---: |
| `pycos/kontrak.py` | 93,18% |
| `pycos/refleksi/nurani.py` | 83,95% |
| `pycos/bahasa/tutur.py` | 84,25% |
| `pycos/konektor.py` | 98,89% |
| `tools/periksa_changelog.py` | 94,74% |

Eksekusi subprocess diuji secara fungsional, tetapi coverage-nya tidak
digabungkan ke laporan proses utama. Ketidakcakupan itu bukan alasan untuk
mengklaim cabang subprocess sudah diukur.

### Performa dan target yang masih terbuka

Pengukuran lokal `python -m pycos.dukungan.tolok --json` dilakukan **tanpa
tracing coverage**, pada mesin sesi ini; bukan jaminan lintas host.

| Fixture | Waktu per iterasi | Gate CI | Hasil |
| --- | ---: | ---: | --- |
| Tick Naluri | 0,1041 ms | <2 ms | Lulus |
| Predict 2.000 episode, budget 256 | 3,4068 ms | <5 ms | Lulus |

Target historis fase 2 predict ≤3 ms masih **belum terpenuhi** pada fixture
budget 256 ini. Target save ≤8 KB juga belum tercapai; profil kompak bukan
jaminan ukuran tersebut. Tidak dilakukan benchmark Godot atau throughput
adapter per-frame pada pembaruan ini.

### Bukti untuk fitur terkini

| Cakupan | Source/panduan saat ini | Bukti dan batas |
| --- | --- | --- |
| Mesin dan state inti R4.1 | [mesin](pycos/inti/mesin.py), [keadaan](pycos/inti/keadaan.py), [konfigurasi](pycos/inti/_konfigurasi.py), [fasad](pycos/inti/naluri.py) | `test_refaktor_inti`, `test_struktur_paket`, SST. Implementasi tidak lagi monolit di naluri.py. |
| Kelas pemilik dan ekstensi | [kesadaran](pycos/inti/kesadaran.py), [presentasi](pycos/inti/presentasi.py), [ritual](pycos/inti/ritual.py), [reputasi](pycos/inti/reputasi.py), [kawanan](pycos/inti/kawanan.py), [ekstensi](pycos/inti/ekstensi), [demo](pycos/inti/demo) | Integrasi, identitas kelas, patch dan jalur showcase diuji; impor lama dipertahankan. |
| Numerik dan runtime patch R4.2–R4.3 | [konstanta](pycos/dukungan/konstanta.py), [numerik](pycos/dukungan/numerik.py), [patching](pycos/dukungan/patching.py) | `test_konstanta_numerik`, `test_refaktor_inti`, SST. Metadata patch bukan bukti seluruh fitur aktif. |
| State, persistence, kontrak | [validasi state](pycos/dukungan/validasi_state.py), [persistensi](pycos/dukungan/persistensi.py), [kontrak](pycos/kontrak.py) | Round-trip dan input rusak pada `test_perbaikan_analisis`/`test_kontrak_negatif`; migrasi eksplisit dan checksum tetap berlaku. Bukan jaminan exact resume semua RNG. |
| Gate pengembangan R5.1/R5.3 | [gate kualitas](tools/periksa_gate.py), [gate changelog](tools/periksa_changelog.py), [kontribusi](CONTRIBUTING.md) | `test_gate_pengembangan`, `test_changelog`. Perubahan AST from_dict memerlukan catatan baru per path; helper tidak langsung dan kebenaran kompatibilitas tetap memerlukan review. |
| Contoh R5.2 | [empat contoh](examples/README.md) | Lima tes `test_examples`: exit code, JSON, state dan determinisme via subprocess. |
| API publik R5.4 | [kebijakan](docs/API_PUBLIK.md), [root](pycos/__init__.py) | Empat tes `test_api_publik`: 64 alias baru, total 125 ekspor; identitas, impor malas, cache, star import dan dua pengecualian. SST memetakan alias ke kelompok aktif, bukan instrumentasi tiap panggilan alias. |
| Adapter host R5.5 | [konektor](pycos/konektor.py), [kontrak host](docs/KONEKTOR_HOST.md) | Lima tes `test_konektor`: isolasi snapshot, keputusan sama dengan mesin, domain invalid, input/file/CLI subprocess. Host tetap pemilik lifecycle; pilihan dan HUD memakai snapshot awal. |
| Godot/HTML | [GDScript](examples/godot/pycos_host.gd), [HTML](examples/inspector.html) | Protokol CLI diuji; DOM tiruan menguji render dan input invalid. **Godot belum diuji dalam engine; browser visual belum diuji.** |
| Tutur, leksikon dan evaluasi R3 | [Tutur](pycos/bahasa/tutur.py), [Nurani](pycos/refleksi/nurani.py), [evaluasi](docs/IMPLEMENTASI_REKOMENDASI_FASE3_EVALUASI.md) | Tes runtime, fixture sintetis dan checker provenance; **evaluasi independen manusia nyata belum dilakukan**. |

### Status pengembangan dan CI

R0–R4 dan R5.1–R5.5 telah diimplementasikan pada cakupan panduan tiap fase;
R5.6 adapter LLM opsional dengan guardrail **belum diimplementasikan**.
Workflow [CI](.github/workflows/ci.yml) dikonfigurasi untuk Python 3.9–3.14,
quality gate, checker leksikon, audit, lint dan changelog pada PR. **Hasil CI
remote/matrix tidak diperiksa pada pembaruan ini**; hasil lokal Python 3.11.2
tidak membuktikan semua interpreter/OS lulus. Build wheel tidak diulang pada
pembaruan ini; hasil build lama tetap bukti historis saja.

### Reproduksi

Jalankan dari root checkout setelah memasang dependensi pengembangan:

```sh
python -m pip install -e '.[dev]'
python -m coverage run --source=pycos,tools -m unittest discover -q
python -m coverage json -o coverage.json
python tools/periksa_gate.py --coverage coverage.json
python -m mypy
python -m pyflakes $(find pycos tools tests examples -type f -name '*.py' ! -name '__init__.py' -print)
python -m compileall -q pycos tools tests examples
python tools/audit_python.py --check
python tools/periksa_changelog.py --base <commit-base-PR>
python -m pycos --periksa --json
python -m pycos.dukungan.leksikon --periksa
python -m pycos.dukungan.tolok --json > tolok.json
python tools/periksa_gate.py --tolok tolok.json
node tools/periksa_inspector.cjs  # opsional; bukan dependensi runtime Python
```

Audit memakai Python 3.11 agar rendering AST sama dengan CI. `<commit-base-PR>`
harus diganti base PR aktual; hasil terhadap HEAD saja tidak membuktikan gate
terhadap seluruh diff PR. Laporan coverage/tolok adalah artefak lokal, bukan
source yang perlu di-commit.

## Arsip validasi dan ledger historis

**Seluruh bagian di bawah adalah snapshot tahap terdahulu**, termasuk angka
tes, tanggal yang tercatat, status “belum dimulai”, dan rentang baris source.
Catatan tanggal arsip dipertahankan sebagaimana adanya, bukan diklaim sebagai
tanggal pengukuran ulang. Untuk status aktif gunakan [validasi terkini](#validasi-terkini).
Tautan baris pada ledger lama dapat menunjuk lokasi yang sudah berubah setelah
refaktor; gunakan tabel source saat ini di atas dan [indeks AST](docs/AUDIT_PYTHON_RINCI.md)
untuk mencari definisi terbaru. Arsip tidak mengesampingkan hasil terbaru.

**Tanggal audit:** 2026-10-18
**Cakupan:** source Python dan berkas tes pada checkout ini, beserta data
leksikon yang disertakan. Ini adalah audit implementasi dan regresi, bukan
klaim validasi ilmiah. Revisi yang diaudit mencakup perbaikan impor berkas
tes, round-trip `demo_npc`, penerusan sebab ujaran `PERINGATAN`, pencocokan
frasa multi-kata pada planner, injeksi waktu untuk recency, pemakaian nyata
`JejakPrediksi` dalam demo kognisi, penggantian nama subpaket
`pycos/primitif/` menjadi `pycos/mandiri/`, penambahan CI, penggabungan
subpaket `pycos/selaras/` ke `pycos/kontrak.py`, `pycos/bahasa/tutur.py`,
`pycos/inti/naluri.py`, `pycos/refleksi/nurani.py`, dan `pycos/__main__.py`
(diikuti penghapusan subpaket itu), serta putaran koherensi/orkestrasi
2026-10-18 (ekstraksi `pycos/inti/persona.py`, manifest kontrak untuk
subsistem keselarasan, cek `--periksa` 9 jalur, visibilitas kegagalan shim
via diagnostik, dan legenda penomoran konsep); temuan lama yang
tidak lagi berlaku diperbarui pada bagian "Catatan dan klaim yang belum terbukti".

### Cara membaca dokumen ini

Bukti dikelompokkan sebagai berikut:

- **Diuji** — assertion pada tes `unittest` bernama menjalankan perilaku yang
  dinyatakan pada fixture tersebut.
- **Diperiksa** — implementasi pada tautan berisi cabang, rumus, struktur data,
  atau API yang dijelaskan. Ini menunjukkan apa yang dilakukan program, bukan
  apakah desainnya berguna atau benar untuk semua aplikasi.
- **Smoke test** — impor atau contoh kecil dijalankan dan berhasil.
- **Belum terbukti** — repositori ini tidak memiliki tes, benchmark, data
  eksternal, atau evaluasi ilmiah yang membuktikan pernyataan tersebut. Hindari
  mengulanginya sebagai jaminan yang lebih kuat.

Source memiliki banyak komentar dan docstring metode yang berulang. Agar
ledger tetap terbaca tanpa menghilangkan subsistem, inventaris di bawah
mengelompokkan klaim berdasarkan kelas dan bagian source yang berurutan. Tautan
rentang source mencakup docstring modul/kelas/metode dan komentar inline pada
bagian tersebut. Komentar pemisah dan komentar yang hanya mengulang nama
variabel ikut terinventarisasi, tetapi bukan klaim perilaku tersendiri.

### Pembaruan fase 3 — evaluasi terpisah R3.3

[API dan batas bukti](docs/IMPLEMENTASI_REKOMENDASI_FASE3_EVALUASI.md):
jalur korpus eksternal terpisah, anotasi bool per identitas, pemeriksaan overlap
ID/teks, pemilihan ambang hanya dari pengembangan, kappa pasangan/cakupan,
konsensus non-seri dan abstention. Format laporan lama dipertahankan sebagai
metrik deskriptif internal. Tanpa bukti input yang cukup, nilai akurasi
terhadap konsensus tidak diterbitkan. Provenance tetap deklarasi belum diverifikasi.

**432 tes** lulus pada Python 3.11.2 (10 baru), termasuk 14 SST. Jalur SST baru
secara eksplisit memakai fixture sintetis, bukan data manusia pihak ketiga.
Sebelas cek kesehatan, compileall, Pyflakes 4.0.3, demo CLI, indeks AST 44 berkas,
dan diff check lulus. API/CLI telah diimplementasikan; **evaluasi independen
manusia nyata belum dilakukan**. Fase 4–5 dan target performa fase 2 yang masih
terbuka tidak dianggap selesai. Catatan berikut adalah snapshot sebelumnya.

### Pembaruan fase 3 — leksikon impak R3.2

[Data, aturan, dan kompatibilitas](docs/IMPLEMENTASI_REKOMENDASI_FASE3_LEKSIKON.md):
653 entri ID/382 EN, termasuk 622/379 kata tunggal. Checker CLI memeriksa
cakupan, vektor finite/nonzero, drive/rentang, checksum sumber, dan kesesuaian
provenance dengan vektor terkompilasi. Bobot lama tidak ditimpa.

**422 tes** lulus pada Python 3.11.2 (enam baru setelah R3.1), termasuk 14 SST
dengan impak dua bahasa pada NPC utama. Sebelas cek kesehatan, compileall,
Pyflakes 4.0.3, demo CLI, checker impak, indeks AST **44 berkas**, dan diff check
lulus. CI kini juga menjalankan checker impak; hosted workflow belum dijalankan
dari workspace ini. Cakupan/provenance bukan evaluasi gold sentiment. Snapshot
ringkas dengan ID bawaan versi sebelumnya membutuhkan ekspor penuh dari versi
lama; mismatch tidak ditafsirkan ulang diam-diam. R3.3 serta target performa
fase 2 tetap terbuka. Catatan berikut adalah snapshot putaran sebelumnya.

### Pembaruan fase 3 — variasi leksikal R3.1

[Implementasi dan batas bukti](docs/IMPLEMENTASI_REKOMENDASI_FASE3_TUTUR.md):
pool L2 hingga 12 lema kompatibel, penalti frekuensi riwayat, sampling seed,
dan urutan pengisian slot seed tanpa mengubah urutan linearisasi L3. Register
formal-only tidak lagi diterima pada konteks netral; rujukan/sebab tetap terikat.

**416 tes** lulus pada Python 3.11.2 (enam baru), termasuk 14 SST dengan engine
NPC utama aktif pada manifest variasi leksikal. Sebelas cek kesehatan,
compileall, Pyflakes 4.0.3, demo CLI, indeks AST 43 berkas, dan diff check lulus.
Pada fixture seed 7/20 permintaan identik: senang 11 teks unik, sedih 15.
Determinisme memerlukan riwayat awal dan urutan panggilan yang sama; hasil dapat
berbeda dari versi lama. Ini bukan evaluasi manusia atau bukti sinonimi mutlak
setiap entri. R3.2–R3.3 dan target performa fase 2 masih terbuka.
Catatan berikut adalah hasil putaran terdahulu.

### Pembaruan fase 2 — batas memori inti R2.5

[Implementasi dan ruang lingkup](docs/IMPLEMENTASI_REKOMENDASI_FASE2_BATAS_MEMORI.md):
registry BATAS untuk sembilan buffer/cache Naluri, audit memori_state, dan
penerapan eksplisit batasi_memori. Default lama dipertahankan; nol benar-benar
mengosongkan storage, dan batas lokal legacy tetap menjadi ceiling tambahan.

**410 tes** lulus pada Python 3.11.2 (9 baru setelah 401 tes R2.4), termasuk
14 SST dengan kebijakan host aktif pada NPC utama. Sebelas cek kesehatan,
compileall, Pyflakes 4.0.3, demo CLI, kesegaran indeks AST **43 berkas**, dan
git diff --check lulus. Audit menghitung entri, bukan byte/RAM total; kapasitas
lapisan lain belum dipusatkan seluruhnya. Menurunkan event_buffer/pred_pairs
memang dapat mengubah perilaku. Target 8 KB dan retrieval 256 kandidat <3 ms
masih terbuka. Catatan berikut adalah hasil putaran sebelumnya.

### Pembaruan fase 2 — kawanan lazy R2.4, 2026-11-08

[Implementasi dan kompatibilitas](docs/IMPLEMENTASI_REKOMENDASI_FASE2_KAWANAN.md):
dispatch prediksi opt-in sesudah seluruh tick, batch tanpa tick, seleksi LOD dan
radius pemain, serta laporan per-NPC. Ranking meneruskan jam NPC ke JEJAK,
termasuk engine tanpa backlink. Default tick_all tetap tanpa prediksi seperti
sebelumnya; tidak ada klaim waktu tick lama lebih cepat.

Pada Python 3.11.2, **401 tes** lulus (10 regresi baru), termasuk 14 SST yang
mengaktifkan jalur lazy pada subjek utama. Sebelas cek kesehatan, compileall,
Pyflakes 4.0.3, demo CLI, kesegaran indeks AST 42 berkas, dan git diff --check
lulus. R2.5 belum dikerjakan; target 8 KB/<3 ms yang masih terbuka tidak dianggap
terpenuhi oleh perubahan dispatch ini. Catatan berikut bersifat historis.

### Pembaruan fase 2 — retrieval R2.3, 2026-11-08

[Status dan batas bukti](docs/IMPLEMENTASI_REKOMENDASI_FASE2_RETRIEVAL.md):
batas similarity per retrieval, pruning usia awal, batas aksi ranking, dan
laporan pemotongan diimplementasikan secara opt-in. **391 tes** lulus pada
Python 3.11.2, termasuk 9 regresi retrieval baru dan 14 SST; 11 cek kesehatan,
compileall, Pyflakes, demo CLI, tolok JSON, kesegaran indeks AST 42 berkas,
dan `git diff --check` lulus.

Fixture 2.000 episode menghasilkan sekitar 4,18 ms/predict untuk batas 256,
dan 2,98 ms untuk batas 128. Target <3 ms pada batas 256 belum tercapai.
Budget membatasi evaluasi similarity, bukan seluruh operasi indeks/retensi
atau deadline wall-clock. Hasil terpotong adalah aproksimasi, bukan jaminan
kualitas setara pencarian penuh. R2.4–R2.5 dan target ukuran 8 KB tetap terbuka.
Bagian berikut mencatat putaran historis sebelumnya.

### Pembaruan fase 2 — putaran persistensi, 2026-11-08

[Status R2.1–R2.2](docs/IMPLEMENTASI_REKOMENDASI_FASE2.md): profil persistensi
konservatif dan referensi/diff bawaan diterapkan pada Naluri dan KawananNPC.
Pada Python 3.11.2, **382 tes** lulus (9 baru), termasuk pembanding load penuh
versus ringkas selama 200 tick per profil pada fixture lapisan aktif. SST
menjalankan kedua profil pada NPC utama; 14 tes SST dan 11 cek kesehatan lulus.
Compileall, Pyflakes 4.0.3, demo CLI, tolok JSON, kesegaran indeks AST 42 berkas,
dan `git diff --check` lulus.

Target 8 KB belum tercapai (fixture aktif: penuh 77.823 byte, simpan 64.623,
minimal 64.596). `pred_pairs` tidak dibuang karena memengaruhi kalibrasi.
Detail fixture, kehilangan log, encoding versi/referensi, dan batas pembuktian
resume ada pada dokumen status. R2.3–R2.5 belum dikerjakan; fase 2 belum
seluruhnya selesai. Bagian di bawah merupakan catatan putaran sebelumnya.

### Pembaruan fase 1 — 2026-11-08

[Implementasi R1.1–R1.4](docs/IMPLEMENTASI_REKOMENDASI_FASE1.md) menambahkan
validasi event, registry parameter opt-in, galat nama konsisten, dan kanal
diagnostik handler/wrapper. Kanal baru mengungkap pemanggilan helper tubuh yang
terputus; pemanggilan dan batas delta pasca-fisika diperbaiki dengan regresi.
Pada Python 3.11.2: **373 tes** lulus (19 baru, termasuk suite **14 SST**),
**11 cek** CLI lulus, compileall pycos/tests/tools, Pyflakes 4.0.3, demo CLI,
kesegaran indeks audit **42 berkas**, dan `git diff --check` lulus.

Diagnostik pada health_check/CLI bersifat global proses dan mencakup input
buruk yang sengaja dikirim probe; adanya catatan bukan otomatis gagal cek.
Domain parameter yang belum dideklarasikan tidak diberi rentang spekulatif.
Rincian kompatibilitas/ruang lingkup dijelaskan di dokumen fase 1. Fase 2–5
belum dinyatakan selesai; catatan fase 0 berikut adalah hasil historis.

### Pembaruan fase 0 — 2026-11-08

Implementasi dan bukti terbaru: [status rekomendasi](docs/IMPLEMENTASI_REKOMENDASI.md).
Pada Python 3.11.2: **354 tes** lulus (termasuk **14 SST**), **10 cek**
`--periksa` lulus; compileall untuk pycos/tests/tools, Pyflakes 4.0.3,
`--demo`, `audit_python.py --check`, dan `git diff --check` lulus.
Indeks AST terbaru memuat **41 berkas** source proyek, tidak termasuk direktori
lingkungan/dependensi/build yang dicantumkan oleh generator. Ini inventaris
struktur, bukan bukti analisis semantik baru atas seluruh source.

Tambahan 15 tes mencakup domain state/jam, format/migrasi termasuk rantai,
save gagal pada fsync/replace, checksum rusak/legacy, attach identitas,
deprecation positional flag, serta cakupan audit. Detail batas validasi,
kompatibilitas metadata, dan persistensi ada dalam dokumen status di atas.
Fase 1–5 belum dinyatakan selesai. Hasil audit dan smoke tambahan di bawah
adalah catatan putaran terdahulu, bukan seluruhnya dijalankan ulang putaran ini.

### Hasil verifikasi historis (sebelum fase 0)

Perintah historis dijalankan dari direktori repositori pada revisi saat itu:

```text
python -m compileall -q pycos tests                LULUS
python -m unittest discover -q                    339 tes — OK
python -m unittest discover -v                    339 tes — OK
python -m pyflakes $(find pycos tests -name '*.py' ! -name '__init__.py')
                                                     LULUS (Pyflakes 4.0.3)
python -m pycos --demo                            LULUS (keluar 0)
python -m pycos --periksa                         LULUS (9 cek, keluar 0)
python -m pycos.dukungan.tolok --json             LULUS (keluar 0)
Demo mandiri: python -m pycos.inti.naluri           LULUS (keluar 0)
Demo mandiri: pycos.refleksi.nurani                 LULUS (keluar 0)
Demo mandiri: pycos.memori.jejak_prediksi           LULUS (keluar 0)
Demo mandiri: pycos.mandiri.organik                 LULUS (keluar 0)
Demo mandiri: pycos.lingkungan.dunia                LULUS (keluar 0)
Contoh README: memori + Tutur + lingkungan          LULUS
Impor paket via PYTHONPATH, tanpa instalasi         LULUS
`python -m pycos` mencetak peta paket                LULUS
Eksekusi berkas langsung dari cwd lain               LULUS (4 modul)
Build wheel (`pip wheel .`) + impor dari wheel       LULUS
TuturEngine + leksikon paket                        LULUS (4.229 entri)
demo_kognisi(seed=7)                                 LULUS (JEJAK + setpoint NURANI)
git diff --check                                     LULUS
```

Pyflakes dijalankan pada seluruh `pycos/` dan `tests/` selain berkas
`__init__.py`, yang sengaja mengimpor ulang nama API di cabang `TYPE_CHECKING`
untuk dukungan tipe. Tidak ada warning di cakupan itu. Workflow CI ditambahkan
di `.github/workflows/ci.yml`; job GitHub-hosted belum dijalankan dari workspace
ini, sehingga hasil lokal di bawah bukan laporan eksekusi hosted workflow.

Struktur paket diperiksa dengan mengimpor `pycos.inti.naluri`,
`pycos.refleksi.nurani`, `pycos.memori.jejak_prediksi`,
`pycos.mandiri.organik`, `pycos.mandiri.kognisi_lanjut`,
`pycos.lingkungan.dunia`, dan `pycos.bahasa.tutur`; tes juga memeriksa enam
nama drive, round-trip state `Organik`, resolusi `jalur_leksikon()`, pemuatan
leksikon 4.229 entri dari dalam wheel, serta round-trip dunia `Lingkungan`.

Demo `python -m pycos.inti.naluri` kini **selesai dengan keluar 0**: assertion
round-trip `KawananNPC` pada `demo_npc()` yang dulu gagal sudah diperbaiki di
sumbernya (`Kesadaran.__init__` tidak lagi absen menuliskan kunci
`body_locus["ownership"]` yang ditulis ulang oleh `from_dict`). Perbaikan itu
adalah perubahan perilaku serialisasi, bukan sekadar pelonggaran assertion:
`KawananNPC.to_dict() == KawananNPC.from_dict(...).to_dict()` tetap diuji.

Smoke test README mencatat satu episode, mengambilnya kembali untuk forecast
aksi, menghasilkan `aku melihat api.` dari leksikon yang disertakan, dan
menjalankan dua NPC di `Lingkungan.dari_ascii(...)` selama 12 langkah tanpa
keluar dari rentang drive. Pemeriksaan dijalankan dengan Python 3.11.2 di
workspace ini; hasilnya tidak membuktikan kompatibilitas dengan semua versi
Python atau platform.

Suite tes kecil dibandingkan ukuran basis kode. Lulusnya 339 tes berarti
assertion tersebut lulus; **bukan** berarti setiap API atau kombinasi flag
memiliki cakupan baris/cabang. Rinciannya per berkas: 21 tes struktur paket dan
gaya berkas (`test_struktur_paket`), 17 tes sumber daya
(`test_sumber_daya`), 14 tes integrasi paket (`test_integrasi_paket`), 38 tes
perilaku kognitif terpilih (`test_struktur_kognitif`), 24 tes primitif mandiri
(`test_organik_lanjutan`), 16 tes kontrak (`test_kontrak_ketidaktahuan`),
61 tes lingkungan uji (`test_lingkungan`), 60 tes
perbaikan analisis (`test_perbaikan_analisis`), 32 tes
keselarasan ujaran (`test_selaras`), 42 tes lanjutan keselarasan
(`test_selaras_lanjutan`), dan 14 tes Systematic-Structured Test
(`test_sst` — 6 tes orkestra + 2 tes klasifikasi + 6 tes pengaman).

#### Batas jaminan SST dan pengamannya

Daftar kebutuhan prioritas berdasarkan audit SST, diimplementasikan dalam
urutan berikut:

1. **Integritas manifest — selesai.** Enam kelompok memori yang sebelumnya
   hanya ditandai kini wajib; label di luar manifest dan bukti kosong ditolak.
2. **Assertion perilaku — selesai.** Hapus kondisi selalu benar dan blok
   peta mati; aktifkan memori sosial sebelum interaksi dan uji relasi dikenal.
3. **Siklus hidup sumber daya — selesai.** `finally` membersihkan direktori
   sementara pada jalur sukses maupun exception tanpa menelan kegagalannya.
4. **Regresi pengaman — selesai.** Tambahkan enam tes negatif/siklus hidup.
5. **Dokumentasi dan validasi — selesai.** Perjelas batas cakupan; 339 tes,
   compileall, sembilan pemeriksaan kesehatan, dan Pyflakes 4.0.3 lulus.


Ledger menolak bukti kosong; orkestra menolak label tak terdaftar dan
memeriksa kesamaan persis fitur aktif dengan manifest. Enam tes
`SSTPengamanTest` menguji penolakan input ledger, salah label, fase yang
hilang, dan pembersihan direktori sementara saat sukses/gagal. Assertion
sosial memverifikasi relasi dikenal setelah pilar memori sosial diaktifkan;
assertion delta, emosi dominan, HUD, dan peta tidak lagi selalu benar.

Jaminan ini berlaku untuk **manifest 90 kelompok fitur**, bukan inventaris
lengkap seluruh metode implementasi. `CAKUPAN_API` menguji pemetaan nama
publik ke kelompok fitur; ia tidak merekam pemanggilan setiap nama atau
mengukur cakupan baris/cabang. AST demo hanya memantau titik masuk showcase.
NPC lain merupakan lawan interaksi; serialisasi juga membuat salinan untuk
verifikasi, sehingga “satu NPC” berarti satu subjek utama, bukan hanya satu
objek NPC yang pernah dibuat. Pengujian semua kombinasi flag dan seluruh
metode masih merupakan pekerjaan lanjutan.

#### Keselarasan ujaran (dahulu subpaket `pycos.selaras`)

Penilai keselarasan ujaran kini berada di modul yang sudah ada
(`Persona`/`Keadaan` di `pycos/inti/naluri.py`, ciri linguistik di
`pycos/bahasa/tutur.py`, penilai/pelacak/kalibrasi di `pycos/refleksi/nurani.py`);
CLI-nya menyatu di `python -m pycos`. Subpaket `pycos.selaras` telah dihapus.
Logika dan angka di bawah berlaku apa adanya. Lapisan yang lebih rendah tidak
mengimpor lapisan yang lebih tinggi; impor `pycos.inti`/`pycos.bahasa` dari
`nurani.py` dilakukan secara malas di dalam fungsi agar tidak memutus rantai
impor.

| Klaim | Bukti | Status |
| --- | --- | --- |
| 90 kelompok fitur yang tercantum dalam manifest SST dijalankan sistematis dan terstruktur untuk satu NPC utama — fitur wajib harus ditandai aktif beserta buktinya (`wajib - aktif == {}`), semua nama `pycos.__all__` terpetakan ke fitur aktif, dan satu-satunya pengecualian adalah titik masuk showcase `demo_*`/`*.demo` yang dikunci di `LUAR_CAKUPAN_SST` dan dipantau pemindaian AST | `SSTOrkestraTest.test_tidak_ada_fitur_tertinggal`, `test_setiap_fitur_punya_bukti`, `test_api_publik_tercakup_manifest`, `test_api_publik_benar_benar_aktif`, `test_fase_terlaksana_berurutan`, `test_laporan_menyebut_semua_fitur`, `SSTKlasifikasiTest` (`tests/test_sst.py`) | **Diuji** |
| Target valensi, gairah, dan keraguan adalah campuran keadaan batin dan sifat persona dengan bobot 0,5 | `PenilaiTest.test_target_campuran_persona_dan_keadaan` | **Diuji** |
| Ujaran yang memuat kata pantangan dibatasi ke skor 0,4 dan berstatus `melanggar_pantangan`; pencocokan per token, bukan substring | `PenilaiTest.test_pantangan_*` | **Diuji** |
| Register formal pada persona santai menurunkan skor register | `PenilaiTest.test_register_formal_*` | **Diuji** |
| Ciri tanpa bukti bernilai `None`, tidak dihitung nol; dimensi `None` tidak masuk rerata | `FiturTest.test_tanpa_bukti_*`, `PelacakTest.test_memori_terbatas_dan_dimensi_none_dilewati` | **Diuji** |
| Drift lintas giliran terdeteksi (menurun, meningkat, stabil, belum cukup) dengan memori terbatas | `PelacakTest` | **Diuji** |
| Input tidak sah (NaN, bool, string angka, kunci asing) ditolak | `PersonaTest`, `KeadaanTest`, `PelacakTest` | **Diuji** |
| Lapisan tidak melingkar: `pycos.refleksi` tidak mengimpor `pycos.inti`/`pycos.bahasa` pada tingkat modul; impor internal hanya sesuai manifest | `KepindahanRumahTest.test_refleksi_tidak_mengimpor_inti_atau_bahasa_di_tingkat_modul` (analisis AST) | **Diuji** |
| Negasi (tidak, tak, bukan, belum, jangan, tiada, nggak, ga) hingga tiga token sebelum kata sentimen dalam klausa yang sama membalik polaritas; batas tanda baca menghentikan jendela | `FiturTest.test_negasi_membalik_polaritas`, `NegasiKlausaTest` | **Diuji** untuk pola sederhana. Negasi yang lebih jauh dari tiga token atau melintasi klausa tidak dibalik. |
| Morfologi sederhana (klitik -nya/-lah/-ku, sufiks -kan/-an/-i, prefiks ber-/ter-/me-/di-/ke-/se-, dan pemulihan huruf awal nasal) mengenali bentuk turunan kata leksikon | `MorfologiTest` | **Diuji** untuk pola yang tercantum. Bukan lemmatizer penuh; bentuk tidak beraturan dapat terlewat. |
| Leksikon bawaan diperluas dan dapat diganti dengan berkas JSON (`LeksikonCiri.dari_berkas`, `--leksikon`); entri harus satu token, frasa ditolak dengan galat | `LeksikonTest`, `CliKalibrasiTest` | **Diuji.** Cakupan tetap terbatas: ribuan kata dan idiom tidak dicakup. |
| Sarkasme dan ironi tidak terdeteksi (contoh: "wah, hebat banget ya, bikin aku nangis" dinilai positif) | `KorpusContohRegresiTest.test_sarkasme_tetap_diakui_sebagai_batasan` (mendokumentasikan kegagalan) | **Batasan terbuka.** Tidak ada perbaikan yang diklaim. |
| Kalibrasi terhadap label: `--kalibrasi` menghitung cakupan, akurasi, dan kappa Cohen untuk polaritas dan formalitas, akurasi keselarasan, dan ambang latih/uji (70/30) | `UkurFiturTest`, `KappaTest`, `UkurSelarasTest`, `MuatKorpusTest` | **Diuji** pada data sintetis. Angka pada `korpus_contoh.jsonl` hanya indikatif: korpus itu dilabeli penulis, dan sebagian leksikon disesuaikan setelah melihat kesalahan pada korpus tersebut sehingga bukan uji independen. Korpus berlabel manusia diperlukan untuk klaim akurasi. |
| Skor dan ambang (0,75 / 0,5 / 0,4, bobot 0,5) adalah pilihan desain | Seksi penilai di `pycos/refleksi/nurani.py` | **Belum divalidasi** terhadap penilaian manusia. Korpus keselarasan contoh hanya 11 contoh berlabel, terlalu kecil untuk menyimpulkan ambang. `--kalibrasi` siap dipakai dengan korpus yang lebih besar. |

#### Perbaikan analisis dan fitur baru

Bagian ini mencatat bukti untuk perubahan dari analisis menyeluruh. Angka
pengukuran berasal dari mesin pengembangan sandbox dan **tidak** dijamin pada
mesin lain.

| Klaim | Bukti | Status |
| --- | --- | --- |
| Nilai non-finite dan kunci drive asing ditolak pada batas masuk; `initial_levels` juga wajib berada pada `[-1, 1]` | `NumerikTest`, `ValidasiBatasMasukNalurTest` | **Diuji** untuk `initial_levels`, `weights`, `delta`, dan `reward_for` sesuai kontrak masing-masing. |
| Kandidat `choose_action` tanpa `name` string non-kosong ditolak; kandidat dengan kunci `effects` dicatat ke diagnostik | `ValidasiBatasMasukNalurTest.test_choose_action_*` | **Diuji** |
| Seed NPC yang sama menghasilkan level identik | `PerilakuNalurTest.test_determinisme_dengan_seed_sama`, `python -m pycos --periksa` (cek `determinisme`) | **Diuji** untuk jalur `Naluri`. Konfabulasi di `JejakPrediksi`/`Nurani` memakai RNG lokal, tetapi determinisme penuh seluruh modul belum diuji. |
| `losses` dibatasi 256 entri | `PerilakuNalurTest.test_losses_dibatasi` | **Diuji** |
| Mimpi buruk tertunda dilaporkan lalu dikosongkan saat `wake()` | `PerilakuNalurTest.test_mimpi_tertunda_dikonsumsi_saat_bangun` | **Diuji** |
| `future_simulation` memanggil `rank_actions` dengan benar dan tidak menelan galat | `JejakPrediksiTest` | **Diuji** |
| `install_methods` tidak menandai fungsi bila batch ditolak | `PatchingTest.test_install_methods_batch_konflik_tidak_menandai_fungsi` | **Diuji** |
| `optional_module` hanya menelan `ImportError` bila modul targetnya absen | `PatchingTest.test_optional_module_*` | **Diuji** |
| Leksikon di-cache per proses (kunci: path absolut, mtime, ukuran); polisem menyimpan semua sense | `LeksikonDanCacheTest` | **Diuji**. Pengukuran sandbox: muat dingin sekitar 43–49 ms, muat hangat sekitar 0,02 ms (`tolok`). Sebelumnya setiap engine memuat ulang JSON 4,3 MB (sekitar 0,15 detik dan 17 MB per engine). |
| `dunia.py` tidak lagi memanggil `npc.tick` dua kali bila TypeError berasal dari dalam tick; reward yang gagal dicatat ke log NPC | `DuniaTest`, `IntegrasiNaluriTest.test_reward_gagal_dicatat_dan_dunia_tetap_berjalan` | **Diuji.** Jalur reward gagal menghasilkan reward netral, mencatat alasan ke log NPC, dan tidak menghentikan langkah dunia. |
| Pemeriksaan kesehatan untuk CI | `PeriksaTest`; `python -m pycos --periksa` | **Diuji** (kode keluar 0 dan 1) |
| Workflow GitHub Actions | `.github/workflows/ci.yml` | **Dikonfigurasi**, bukan dijalankan dari workspace ini: matrix Python 3.9–3.14 menjalankan `compileall`, unit test, dan pemeriksaan kesehatan; job terpisah menjalankan Pyflakes 4.0.3. |
| Cakupan Pyflakes | `python -m pyflakes $(find pycos tests -name '*.py' ! -name '__init__.py')` | **LULUS.** Berkas `__init__.py` dikecualikan karena re-export API publik di bawah `TYPE_CHECKING` tampak sebagai F401 untuk Pyflakes. |
| `SEBAB` dari frame L0 diteruskan ke kalimat L1 `PERINGATAN` | `TuturDanLeksikonTest.test_peringatan_memasukkan_sebab_dari_spotlight` | **Diuji.** Contoh peringatan kini memuat sebab eksplisit (`karena asap tebal`). |
| Demo kognisi menyambungkan `JejakPrediksi` dan menampilkan setpoint NURANI | `DemoKognisiTest.test_jejak_dan_setpoint_dipakai_dalam_demo` | **Diuji** dengan seed tetap; `JejakPrediksi` dipasang melalui `Naluri.attach_jejak()`, bukan hanya dibuat/diambil lalu diabaikan. |
| Tolok kinerja | `TolokTest`; `python -m pycos.dukungan.tolok` | **Diuji** sebagai fungsi dan CLI. **Angka** bersifat indikatif, bukan jaminan kinerja. |
| Recency node eksternal memakai jam dinding (`time.time()`) bila node tidak menyediakan `idle_seconds`; pemanggil dapat menginjeksi waktu `now` | `Naluri.salience` di `naluri.py` (L11309); `SalienceReproducibilityTest` | **Diuji.** Jalur fallback dapat direproduksi dengan `now` dan menolak waktu non-finite. Tanpa argumen itu, fallback tetap memakai jam dinding; node yang menyediakan `idle_seconds()` tetap diutamakan. |

Keterbatasan kode yang tersisa: `Naluri.tick()` dan `choose_action` masih
memiliki jalur klem numerik inline yang tidak dikonsolidasikan karena beberapa
memiliki batas berbeda (misalnya batas integer). Sebab `SEBAB` kini diteruskan
ke L1 dan dimasukkan dalam keluaran `PERINGATAN`; regresinya dijaga oleh
tes `TuturDanLeksikonTest.test_peringatan_memasukkan_sebab_dari_spotlight`.

#### Koherensi dan orkestrasi antar-berkas (2026-10-18)

Putaran ini memperbaiki seam lintas berkas yang ditemukan analisis menyeluruh
atas seluruh berkas Python (catatan analisisnya diringkas di PR #14),
tanpa mengubah perilaku kognitif.

| Klaim | Bukti | Status |
| --- | --- | --- |
| `Persona`/`Keadaan`/`PERSONA_CONTOH` berada di modul ringan `pycos.inti.persona` (impor 29 ms vs 53 ms `naluri`), dan nama lama tetap bisa diimpor dari `pycos.inti.naluri` dengan objek kelas yang identik | `KepindahanRumahTest.test_rumah_baru_sesuai_lapisan`, `test_re_export_kompatibel_di_naluri` | **Diuji** |
| Manifest `JANJI`/`KEBUTUHAN` memuat entri `Persona`, `Keadaan`, `PelacakSelaras` dan kebutuhan `PenilaiSelaras`; `verifikasi_startup()` tanpa pelanggaran | `KontrakStatikDanOperasiTest.test_manifest_memuat_subsistem_keselarasan` | **Diuji** |
| Kontrak operasi `nilai_selaras` dan `pelacak.catat` lulus level 2 pada objek nyata, dan melaporkan input buruk (persona tak bernama, keadaan NaN/luar rentang, skor di luar [0,1]) | `test_kontrak_operasi_nilai_selaras_dan_pelacak`, `test_kontrak_operasi_penilai_melaporkan_input_buruk` | **Diuji** |
| `--periksa` menjangkau seluruh subsistem (9 cek, termasuk `penilai`, `korpus`, `validasi_batas`) | `PeriksaTest`, `python -m pycos --periksa` | **Diuji** |
| Kegagalan impor lapisan opsional di naluri (NURANI/JEJAK/TUTUR) tercatat ke `dukungan.diagnostik`, bukan senyap | `ShimIntegrasiTest` (subprocess, modul diblokir) | **Diuji** |
| Tiga salinan daftar drive (`kontrak.DRIVE_KEYS`, `naluri.DRIVES`, `nurani.DEFAULT_DRIVES`) dijaga tetap identik | `KoherensiLintasModulTest.test_daftar_drive_tiga_salinan_sama` | **Diuji** |
| `jalur_korpus`/`NAMA_KORPUS` diuji seperti leksikon; korpus contoh terpasang | `test_sumber_daya.test_jalur_korpus_absolut_dan_korpus_ikut_terpasang` | **Diuji** |
| Penomoran "konsep 1–17" dalam source dipetakan di README ("Penomoran konsep dalam source") dari rujukan aktual; daftar desain aslinya tetap di luar repo | README; komentar `naluri.py` ("Ringkasan konsep 17 di folder analysis") | **Diperiksa** — pemetaan disusun dari pemakaian kode, bukan dari dokumen desain yang tidak disertakan. |

### Inventaris dokumentasi

Inventaris AST/tokenizer atas 26 berkas Python (19 di `pycos/`, 7 di `tests/`)
menemukan **822 docstring** modul, kelas, dan fungsi serta **2.717 token
komentar** Python. Metodenya: docstring dihitung lewat AST untuk
`Module`/`ClassDef`/`FunctionDef`/`AsyncFunctionDef`, komentar dihitung dari
token `COMMENT` `tokenize`. Token komentar mencakup deklarasi encoding,
pemisah, dan catatan implementasi, bukan hanya klaim. Nomor dihitung ulang pada
revisi ini; `__pycache__` dikecualikan. Rinciannya:

| Berkas | Docstring | Token komentar |
| --- | ---: | ---: |
| `pycos/inti/naluri.py` | 450 | 1.621 |
| `pycos/refleksi/nurani.py` | 94 | 359 |
| `pycos/memori/jejak_prediksi.py` | 53 | 98 |
| `pycos/mandiri/organik.py` | 91 | 292 |
| `pycos/mandiri/kognisi_lanjut.py` | 15 | 28 |
| `pycos/bahasa/tutur.py` | 24 | 132 |
| `pycos/lingkungan/dunia.py` | 39 | 83 |
| `pycos/dukungan/patching.py` | 7 | 4 |
| `pycos/dukungan/sumber.py` | 6 | 1 |
| 9 berkas `__init__.py` + `pycos/__main__.py` | 19 | 42 |
| `tests/` (7 berkas) | 24 | 57 |
| **Total** | **822** | **2.717** |

`pycos/sumber_daya/leksikon_pycos.json` adalah data JSON, bukan source Python; record `meta`
dibandingkan dengan entri yang diparse di bawah. `LICENSE` adalah teks lisensi
MIT, bukan pernyataan perilaku perangkat lunak.

### Ledger klaim dan bukti

#### Bentuk proyek dan dependensi

| Blok klaim source | Bukti | Temuan |
| --- | --- | --- |
| Ikhtisar dan katalog API modul `pycos/inti/naluri.py` ([L1–L250](pycos/inti/naluri.py#L1-L250)); deklarasi drive/default ([L301–L648](pycos/inti/naluri.py#L301-L648)) | `Naluri`, transisi state, dan metodenya ada di [L7695–L12473](pycos/inti/naluri.py#L7695-L12473). Kesadaran, presentasi, kepribadian, dan ekstensi opsional dijelaskan pada bagian terkait di bawah. | Enam nama drive dan implementasi API tersedia. Katalog API bersifat deskriptif; itu bukan jaminan setiap fitur aktif pada NPC default. |
| Helper drive/WATAK dan default kesadaran sebelum definisi kelasnya: [L651–L1129](pycos/inti/naluri.py#L651-L1129) | Resolver parameter per-drive, helper clipping, serta konfigurasi kesadaran/agensi berada di rentang tersebut. | **Diperiksa.** Nilai dan gate adalah pilihan konfigurasi; label fisiologi yang muncul di komentar bukan bukti biologis. |
| Klaim “hanya standard library” / tidak ada dependensi keras pada aplikasi host ([pycos/inti/naluri.py L1–L250](pycos/inti/naluri.py#L1-L250), [pycos/memori/jejak_prediksi.py L1–L42](pycos/memori/jejak_prediksi.py#L1-L42), [pycos/mandiri/organik.py L1–L68](pycos/mandiri/organik.py#L1-L68), [pycos/bahasa/tutur.py L1–L30](pycos/bahasa/tutur.py#L1-L30), [pycos/mandiri/kognisi_lanjut.py L1–L19](pycos/mandiri/kognisi_lanjut.py#L1-L19), [pycos/lingkungan/dunia.py L1–L60](pycos/lingkungan/dunia.py#L1-L60)) | Impor menggunakan standard library atau modul dalam checkout ini; `pycos/inti/naluri.py` memakai impor opsional dan akses duck-typed alih-alih mengimpor `samre.*` ([pycos/inti/naluri.py L251–L300](pycos/inti/naluri.py#L251-L300), [pycos/dukungan/patching.py L23–L39](pycos/dukungan/patching.py#L23-L39)). | **Diperiksa dan diuji dengan smoke test** pada Python 3.11.2. Tidak ada dependensi runtime pihak ketiga yang diimpor/dideklarasikan oleh modul ini. Ini tidak membuktikan kompatibilitas dengan semua lingkungan yang disebut dalam komentar. |
| `pycos/mandiri/kognisi_lanjut.py` dapat dimuat tanpa mengimpor modul inti ([L1–L12](pycos/mandiri/kognisi_lanjut.py#L1-L12)) | Modul hanya mengimpor `math`, `random`, dan helper typing ([L14–L18](pycos/mandiri/kognisi_lanjut.py#L14-L18)). | **Diperiksa.** Hook `Naluri` dipasang dari `pycos/inti/naluri.py`, bukan diimpor oleh `pycos/mandiri/kognisi_lanjut.py`. |
| Penamaan subpaket `pycos/mandiri/` (dulu `pycos/primitif/`) dan klaim bahwa dua modulnya berdiri sendiri: [pycos/mandiri/__init__.py L1–L14](pycos/mandiri/__init__.py#L1-L14) | `git mv` direktori; modul di dalamnya hanya mengimpor standard library, dan hook `Naluri` dipasang dari lapisan pemanggil lewat `optional_module("pycos.mandiri.*")` ([pycos/inti/naluri.py L15492](pycos/inti/naluri.py#L15492), [pycos/memori/jejak_prediksi.py L2390](pycos/memori/jejak_prediksi.py#L2390), [pycos/refleksi/nurani.py L3246](pycos/refleksi/nurani.py#L3246)). | **Diuji.** `SusunanBerkasTest` menjaga peta direktori, `JalurImporTest.test_lingkungan_tanpa_impor_lapisan_pycos_di_tingkat_atas` memastikan modul dunia tidak mengimpor lapisan Pycos di tingkat atas, dan `test_optional_module_menyelesaikan_nama_bertitik` memastikan nama baru resolve dan `optional_module("organik")` (nama flat lama) mengembalikan `None` tanpa melempar; impor datar ke nama lama dilarang di source maupun berkas tes. |
| Konsistensi gaya impor berkas tes: [tests/test_struktur_paket.py L203–L255](tests/test_struktur_paket.py#L203-L255) | `GayaBerkasTesTest` memeriksa AST setiap `tests/test_*.py`: tidak ada impor datar ke nama modul di dalam paket, tidak ada impor relatif, kepala berkas memakai deklarasi encoding, docstring modul, `from __future__ import annotations`, dan penambahan akar repo ke `sys.path`. | **Diuji.** Sebelum perbaikan, `test_organik_lanjutan.py` dan `test_struktur_kognitif.py` memakai `from naluri import ...` yang gagal di `python -m unittest discover`; kini seluruh berkas tes mengimpor lewat `pycos.*` dan suite berjalan utuh. |
| Kompatibilitas impor sebagai paket/mandiri ([pycos/dukungan/patching.py L1–L8](pycos/dukungan/patching.py#L1-L8); impor integrasi pada `pycos/inti/naluri.py`, `pycos/refleksi/nurani.py`, `pycos/memori/jejak_prediksi.py`) | Smoke test impor sebagai paket berhasil untuk modul terintegrasi yang disebut; implementasi resolver opsional ada di [pycos/dukungan/patching.py L23–L39](pycos/dukungan/patching.py#L23-L39). | **Diuji dengan smoke test** untuk modul-modul tersebut. Ini bukan pengujian menyeluruh semua kemungkinan kegagalan impor atau tata letak package host. |

#### `pycos/inti/naluri.py` — inti, kesadaran, presentasi, dan kawanan

| Bagian docstring/komentar | Bukti kode | Bukti regresi / batasan |
| --- | --- | --- |
| Enam level drive, event, tick/LOD, tujuan, penilaian aksi, reward, kalibrasi, tidur, serialisasi, dan diagnostik: [ikhtisar L1–L250](pycos/inti/naluri.py#L1-L250), [default L301–L648](pycos/inti/naluri.py#L301-L648), [`Naluri` L7695–L12473](pycos/inti/naluri.py#L7695-L12473) | `Naluri.__init__`, `tick`, `_physics`, metode aksi/reward, serta `to_dict` / `from_dict` berada di kelas terkait. Transisi fisika normal membatasi drive di [L8270](pycos/inti/naluri.py#L8270); `initial_levels` divalidasi dengan `float_hingga` dan pemeriksaan rentang eksplisit saat konstruksi di [L7716–L7720](pycos/inti/naluri.py#L7716-L7720). | **Diuji.** Nilai non-finite, boolean, dan nilai di luar `[-1, 1]` ditolak (`ValidasiBatasMasukNalurTest`); README menyatakan kontrak ini. |
| Bobot kepribadian, preset bernama, parameter WATAK, dan seeding backstory: [L338–L540](pycos/inti/naluri.py#L338-L540), [L322–L336](pycos/inti/naluri.py#L322-L336), [L10814–L11008](pycos/inti/naluri.py#L10814-L11008) | Tabel preset dan metode setter/seed ada pada bagian implementasi tersebut. | Perilaku preset terpilih **diuji** oleh `PelindungIlusiTest.test_watak_kegagalan_berbeda_tiap_preset` ([test_struktur_kognitif.py L298–L317](tests/test_struktur_kognitif.py#L298-L317)); seluruh katalog preset tidak diuji. |
| Kesadaran, spotlight/workspace, identitas naratif, monitoring realitas/sumber, kognisi sosial, agensi, tidur, nilai, dan state batin: [kelas `Kesadaran` L1130–L5161](pycos/inti/naluri.py#L1130-L5161) | Metode dan field state tersebut diimplementasikan di kelas ini; kelas dibuat dan diintegrasikan oleh `Naluri` di [L7695–L8001](pycos/inti/naluri.py#L7695-L8001). | Perilaku terpilih **diuji** oleh `LantaiKesadaranDanReportTest` ([test_struktur_kognitif.py L69–L104](tests/test_struktur_kognitif.py#L69-L104)), `AudisiDiriTest` ([L613–L701](tests/test_struktur_kognitif.py#L613-L701)), `StrategiSosialTest` ([L748–L810](tests/test_struktur_kognitif.py#L748-L810)), `EpistemicAndOpacityTest` ([L811–L830](tests/test_struktur_kognitif.py#L811-L830)), dan `SleepInsightAndFreeWillTest` ([L857–L932](tests/test_struktur_kognitif.py#L857-L932)). Sebagian besar metode kesadaran belum memiliki tes tersendiri. |
| Presentasi dinamis, dialog, kanal nonverbal, pergiliran bicara, kebocoran afektif, hesitasi, dan serialisasi state: [kelas `Presentasi` L5245–L7349](pycos/inti/naluri.py#L5245-L7349), ditambah integrasi presentasi [L17921–L19289](pycos/inti/naluri.py#L17921-L19289) | Metode bicara, mendengar, penyusunan adegan, kanal, dan state diimplementasikan pada bagian tersebut. | **Diuji untuk jalur terpilih** oleh `PelindungIlusiTest` ([test_struktur_kognitif.py L298–L431](tests/test_struktur_kognitif.py#L298-L431)), `PenahananSadarTest` ([L563–L612](tests/test_struktur_kognitif.py#L563-L612)), `AudisiDiriTest` ([L613–L701](tests/test_struktur_kognitif.py#L613-L701)), dan smoke test generasi README. Kualitas yang “natural” atau mirip manusia tidak dibuktikan secara objektif. |
| Ritual dan tujuan: [L7373–L7694](pycos/inti/naluri.py#L7373-L7694) | Implementasi `Ritual`, `Goal`, dan `Mood` serta konfigurasinya tersedia. | Detail API ritual terutama **diperiksa**. Pemilihan tujuan tanpa input drive memiliki assertion khusus di `SleepInsightAndFreeWillTest` ([test_struktur_kognitif.py L902–L931](tests/test_struktur_kognitif.py#L902-L931)). |
| Kawanan, reputasi, spatial hash, tick event-driven/layered, gosip, pembelajaran sosial, dan prediksi bersama: kelas `Reputasi` [L12475–L12700](pycos/inti/naluri.py#L12475-L12700), kelas `KawananNPC` [L12703–L14049](pycos/inti/naluri.py#L12703-L14049) | Nama API dan algoritma berada pada kelas-kelas tersebut. `_nearby` dan `_pairs_within` menggunakan indeks grid. | **Diperiksa, tidak di-benchmark.** Tes saat ini tidak membuktikan throughput kawanan berskala besar, mutu inferensi gosip, atau skalabilitas produksi. |
| Hook kognisi-lanjut: [L15040–L15382](pycos/inti/naluri.py#L15040-L15382) | Pembuatan `KognisiLanjut` secara opsional, wrapper tick, serialisasi state, dan pemasangan metode tersedia pada rentang tersebut. | Keamanan patch per-instance dan persistensi Bayes **diuji** oleh `SafeMethodPatchTest` ([test_organik_lanjutan.py L13–L56](tests/test_organik_lanjutan.py#L13-L56)). Tidak ada regresi numerik langsung untuk seluruh parameter TD, OU, atau graf. |
| Demo/fixture mandiri dan klaim keluaran demo: [L14055–L15039](pycos/inti/naluri.py#L14055-L15039), demo Organik [L15384–L15478](pycos/inti/naluri.py#L15384-L15478), demo Lingkungan [pycos/lingkungan/dunia.py L1460–L1494](pycos/lingkungan/dunia.py#L1460-L1494) | Fungsi demo membuat skenario, menjalankan metode, dan mengembalikan/mencetak hasil; demo `demo_npc()` berisi assertion round-trip `KawananNPC.to_dict()`/`from_dict` yang dulu gagal dan kini lulus. | **Diuji sebagai jalur eksekusi:** `JalurEksekusiTest` menjalankan lima modul demo (`python -m ...`) dan empat berkas secara langsung, semuanya keluar 0. Assertion demo tetap bukan pengganti tes unit, dan klaim demonstrasi introspeksi/fisiologi dibatasi oleh catatan ilmiah di bawah. |
| Integrasi state organik, pipeline gejala, invensi, penalaran kausal, planner, dan ujaran protektif: [L15479–L17920](pycos/inti/naluri.py#L15479-L17920), [L17921–L19289](pycos/inti/naluri.py#L17921-L19289) | Hook dan fungsi wrapper didefinisikan pada rentang tersebut serta memakai modul `organik` lokal bila tersedia. | **Tes integrasi terpilih** dicantumkan pada bagian `pycos/mandiri/organik.py`, serta di `GejalaMurniPipelineTest`, `TubuhTakDapatDitukarTest`, dan kelas-kelas tes presentasi. Seluruh permukaan hook tidak tercakup. |
| Batasan akselerasi native/GPU/dashboard: [pycos/inti/naluri.py L133–L135](pycos/inti/naluri.py#L133-L135) | Checkout ini berisi source Python dan data JSON saja; tidak ada ekstensi native, kode GPU, atau berkas dashboard web. | **Diperiksa untuk checkout ini.** Aplikasi host eksternal dapat menyediakan komponennya sendiri; temuan berlaku untuk repositori ini. |

#### `pycos/refleksi/nurani.py` — refleksi dan state adaptif

| Bagian docstring/komentar | Bukti kode | Bukti regresi / batasan |
| --- | --- | --- |
| Ikhtisar memori afektif, kalibrasi, setpoint/interosepsi, konflik/sirkadian/flow, memori sosial, persepsi, WATAK, dan backstory: [docstring modul L1–L105](pycos/refleksi/nurani.py#L1-L105) | Default berada di [L128–L336](pycos/refleksi/nurani.py#L128-L336); metode dan persistensi `Nurani` berada di [L374–L3221](pycos/refleksi/nurani.py#L374-L3221). | **Diperiksa.** Flag fitur milik `NURANI_DEFAULTS` bernilai false secara bawaan; perilaku saat ditempel juga bergantung pada gate dan konfigurasi `Naluri` pemilik. |
| Skema `CalibrationReport`: [L345–L368](pycos/refleksi/nurani.py#L345-L368); laporan dan hold-out di `Nurani`: [L374–L3221](pycos/refleksi/nurani.py#L374-L3221) | Field laporan, `to_dict`, pencatatan observasi, Brier/EMA, reliability, dan metode skala ada dalam implementasi. | **Diperiksa.** Suite menguji sebagian outcome confidence, ketidakpastian, kejutan, dan prior sosial, tetapi tidak memvalidasi mutu kalibrasi statistik pada suatu dataset. |
| Hook luka domain dan trust/graf: [L3238–L3418](pycos/refleksi/nurani.py#L3238-L3418) | Metode integrasi dan pemasangan wrapper tersedia pada rentang tersebut. | **Diperiksa.** Checkout ini tidak memiliki berkas khusus bernama `tests/test_nurani.py`; lihat catatan rujukan usang di bawah. |
| Impor mandiri / state JSON-safe: [modul L1–L105](pycos/refleksi/nurani.py#L1-L105), [serialisasi L2356–L2560](pycos/refleksi/nurani.py#L2356-L2560) | `Nurani` menerima kamus parameter opsional dan menserialisasi state bertingkat pada metode terkait. Modul hanya mengimpor standard library dan helper patch lokal. | **Smoke test** berhasil untuk `Pycos.nurani`; state NURANI juga dipakai pada beberapa kasus `test_struktur_kognitif.py`. Demo standalone tidak dijalankan sebagai bagian dari test suite. |
| Pemetaan ilmiah/fisiologis dalam komentar: [L267–L276](pycos/refleksi/nurani.py#L267-L276), [L1845–L1856](pycos/refleksi/nurani.py#L1845-L1856) | Komentar menyebut konsep dan makalah rujukan; variabel dan ambang perangkat lunak terkait ada di kode. | **Tidak dibuktikan secara ilmiah oleh repositori ini.** Sitasi dalam komentar adalah petunjuk bacaan, bukan validasi independen bahwa kode mereplikasi mekanisme otak. |

#### `pycos/memori/jejak_prediksi.py` — memori episodik, prediksi, dan integrasi

| Bagian docstring/komentar | Bukti kode | Bukti regresi / batasan |
| --- | --- | --- |
| Ikhtisar tujuan, bobot, API publik, retensi, dan persistensi: [docstring modul L1–L42](pycos/memori/jejak_prediksi.py#L1-L42), konstanta default [L68–L82](pycos/memori/jejak_prediksi.py#L68-L82) | Konstruktor dan metode utama `JejakPrediksi` berada di [L327–L2333](pycos/memori/jejak_prediksi.py#L327-L2333). Bobot defaultnya 0,75 / 0,15 / 0,10; kode konstruktor membatasi bobot lingkungan hingga 0,20. | **Diperiksa dan diuji dengan smoke test.** Bobot adalah nilai desain yang bisa dikonfigurasi, bukan bobot prediksi manusia hasil pengukuran. |
| Normalisasi outcome, similarity, alias cue, dan keluarga aksi: [L87–L327](pycos/memori/jejak_prediksi.py#L87-L327), [`_normalise_outcome` L222–L279](pycos/memori/jejak_prediksi.py#L222-L279) | Tokenisasi regex, tabel alias kecil, filter stopword, klasifikasi keluarga aksi, dan skema outcome ada di kode. | **Diperiksa.** Ini heuristik ringan, bukan NLP penuh atau model multibahasa; benchmark mutu retrieval skala luas tidak tersedia. |
| Indeks terbalik, cache, MinHash, mode coarse/exact, dan profiling: [L715–L807](pycos/memori/jejak_prediksi.py#L715-L807) | `_candidates` menggabungkan ID episode dari indeks token; `_minhash` dan `_minhash_sim` membuat signature; `performance_report` mengembalikan counter runtime. | **Diperiksa, tidak di-benchmark.** Keterangan O(k) versus O(n) adalah maksud struktural, bukan jaminan kompleksitas atau kecepatan tanpa syarat: `_candidates` kembali ke daftar episode bila indeks kosong dan benchmark performa tidak disertakan. |
| Konsolidasi, kematian/retensi memori, gate recall rewrite, prediksi, ranking, dan reinforcement: [L623–L715](pycos/memori/jejak_prediksi.py#L623-L715), [L808–L1258](pycos/memori/jejak_prediksi.py#L808-L1258), [L1259–L1756](pycos/memori/jejak_prediksi.py#L1259-L1756) | Kode memelihara nekropolis berbasis signature, menghapus/mengeviksi episode, mematikan reconstructive recall secara bawaan, membentuk forecast, meranking aksi, dan memperkuat berdasarkan outcome. | **Diuji secara selektif** oleh `NekropolisDanRecallTest` ([test_struktur_kognitif.py L14–L68](tests/test_struktur_kognitif.py#L14-L68)), `WaktuSubjektifTest` ([L432–L479](tests/test_struktur_kognitif.py#L432-L479)), dan smoke test memori README. Tes membedakan cue yang diketahui lalu mati dari cue yang belum pernah diketahui serta memeriksa gate rewrite; tes tidak mencakup semua kasus retensi/ranking. |
| Autobiografi, simulasi masa depan, emosi kontrafaktual, konfabulasi, pola aktor, dan hook Bayes: [L1758–L2333](pycos/memori/jejak_prediksi.py#L1758-L2333), [L2382–L2777](pycos/memori/jejak_prediksi.py#L2382-L2777) | Metode publik, wrapper waktu per episode, state pola, dan integrasi keyakinan opsional ada pada rentang tersebut. | Patching/persistensi Bayes **diuji** oleh `SafeMethodPatchTest`; klaim autobiografi dan pola lain terutama **diperiksa** pada suite saat ini. |

#### `pycos/mandiri/organik.py` — primitif state dan wadah

| Bagian docstring/komentar | Bukti kode | Bukti regresi / batasan |
| --- | --- | --- |
| Katalog dua belas primitif state dan klaim “tanpa impor internal Pycos”: [docstring modul L1–L68](pycos/mandiri/organik.py#L1-L68), ekspor [L79–L108](pycos/mandiri/organik.py#L79-L108) | Definisi primitif dan wadah `Organik` berada di [L121–L3139](pycos/mandiri/organik.py#L121-L3139). Impornya hanya dari standard library. | **Diperiksa.** Pernyataan tanpa impor internal berlaku untuk impor modul ini. Tidak setiap primitif memiliki tes regresi langsung. |
| Persistensi/residu tanpa decay dan efek ambang/plafon: [Residu L121–L329](pycos/mandiri/organik.py#L121-L329) | State aktif/arsip/tambalan, metode ambang/plafon, dan serializer ada di kelas tersebut. | **Diuji** oleh `ResiduTest` ([test_organik_lanjutan.py L58–L90](tests/test_organik_lanjutan.py#L58-L90)); tes yang sama juga memeriksa integrasi `Naluri`. |
| Intrusi, detak internal fraksional, dan vacancy: [Intrusi L335–L452](pycos/mandiri/organik.py#L335-L452), [DetakInternal L458–L568](pycos/mandiri/organik.py#L458-L568), [Vacancy L1461–L1521](pycos/mandiri/organik.py#L1461-L1521) | Sampling, akumulator fraksional, dan jam vacancy diimplementasikan pada kelas terkait. | **Diuji secara selektif** oleh `IntrusiTest` dan `DetakInternalTest` ([test_organik_lanjutan.py L91–L145](tests/test_organik_lanjutan.py#L91-L145)), serta `VacancyTest` ([test_struktur_kognitif.py L146–L178](tests/test_struktur_kognitif.py#L146-L178)). |
| Topologi kosong, luka domain, batas identitas, waktu heterogen per episode, penolakan tutur, dan apersepsi: [kelas terkait L574–L1256](pycos/mandiri/organik.py#L574-L1256) | Sentinel `None`, hasil domain yang dikecualikan, filter identitas, state waktu per episode, variasi penolakan, dan mode apersepsi direpresentasikan oleh kelas-kelas tersebut. | **Diuji secara selektif** oleh `TopologiSlotTest`, `LukaDomainTest`, `BatasIdentitasTest`, `WaktuHeterogenTest`, `PenolakanTuturTest`, dan `ApersepsiTest` (`test_organik_lanjutan.py`). Serialisasi juga diuji untuk slot dan waktu; katalog dan semua kombinasi state tetap belum tercakup. |
| Lapisan keyakinan paralel dan state tubuh: [L1262–L1458](pycos/mandiri/organik.py#L1262-L1458) | Penyimpanan lapisan dan metode integrator tubuh tersedia. | Kontradiksi paralel dan satu lokus tubuh **diuji secara selektif** oleh `KoherensiParalelTest` ([test_organik_lanjutan.py L146–L168](tests/test_organik_lanjutan.py#L146-L168)) serta `TubuhTakDapatDitukarTest` ([test_struktur_kognitif.py L480–L506](tests/test_struktur_kognitif.py#L480-L506)). |
| Gejala mentah, kategori proto, dan pipeline kategori: [L1560–L2069](pycos/mandiri/organik.py#L1560-L2069) | Implementasi melacak primitif gejala mentah, signature berulang, state proto, klaim kategori, pemudaran, dan residu. | **Diuji** oleh `GejalaMurniOrdeNolTest` ([test_organik_lanjutan.py L169–L236](tests/test_organik_lanjutan.py#L169-L236)) dan `GejalaMurniPipelineTest` ([test_struktur_kognitif.py L179–L297](tests/test_struktur_kognitif.py#L179-L297)). |
| Invensi, graf kausal, dan planner hierarkis: [L2124–L3042](pycos/mandiri/organik.py#L2124-L3042) | Scoring usulan, edge/penjelasan/kontrafaktual kausal, dan metode perencanaan tersedia pada kelas-kelas terkait. | **Diuji secara selektif** oleh `InvensiTest`, `ModelKausalTest`, dan `PerencanaOutcomeTokenTest` (`test_organik_lanjutan.py`): usulan, penjelasan/kontrafaktual/atribusi, round-trip graf, serta pencocokan hasil multi-kata dijalankan. Cakupan bukan verifikasi ilmiah atau uji semua kombinasi planner. |
| Agregasi wadah/serialisasi: [L3048–L3139](pycos/mandiri/organik.py#L3048-L3139) | `Organik.to_dict()` dan `from_dict()` menserialisasi/memulihkan state komponennya. | **Smoke test** berhasil saat impor package; round-trip gejala/residu juga dicakup tes pipeline gejala di atas. |

#### `pycos/mandiri/kognisi_lanjut.py` — lima mekanisme komputasional

| Bagian docstring/komentar | Bukti kode | Bukti regresi / batasan |
| --- | --- | --- |
| Ringkasan modul: [L1–L12](pycos/mandiri/kognisi_lanjut.py#L1-L12) | `EversiTD` dan rumus TD/eversi [L23–L137](pycos/mandiri/kognisi_lanjut.py#L23-L137); Softmax/temperatur [L143–L176](pycos/mandiri/kognisi_lanjut.py#L143-L176); trust log-odds [L191–L263](pycos/mandiri/kognisi_lanjut.py#L191-L263); graf asosiasi [L274–L402](pycos/mandiri/kognisi_lanjut.py#L274-L402); OU terbatas [L408–L456](pycos/mandiri/kognisi_lanjut.py#L408-L456); bundel [L462–L533](pycos/mandiri/kognisi_lanjut.py#L462-L533). | **Diperiksa.** Source mengimplementasikan persamaan dan transisi state yang dinamai. Suite saat ini tidak menguji secara independen setiap rumus dan rentang parameter. |
| Interpretasi evolusi parameter “permanen” / psikologis pada komentar kelas ([EversiTD L23–L137](pycos/mandiri/kognisi_lanjut.py#L23-L137), [ProsesOU L408–L456](pycos/mandiri/kognisi_lanjut.py#L408-L456)) | Nilai yang dipelajari disimpan pada objek dan memiliki metode serialisasi; nilai OU dibatasi oleh limit terkonfigurasinya. | “Permanen” berarti state objek dapat dipersistenkan, bukan penyimpanan yang tak dapat diubah atau klaim tentang kepribadian. Kesetaraan perilaku/neurosains tidak dibuktikan. |

#### `pycos/bahasa/tutur.py` dan `pycos/sumber_daya/leksikon_pycos.json` — generasi dan analisis

| Bagian docstring/komentar | Bukti kode/data | Bukti regresi / batasan |
| --- | --- | --- |
| Struktur leksikon dan tipe semantik: [Lattice/Leksikon/data L48–L260](pycos/bahasa/tutur.py#L48-L260) | Lattice memeriksa hubungan subtipe pada rantai induk; `Leksikon` mengindeks entri menurut lema/kelas/tipe; `Arg`, `Node`, `GenContext`, dan `Tutur` memuat struktur semantik serta hasil generasi. | **Diperiksa** dan dipakai smoke test dengan leksikon bundel. Ini tidak membuktikan mutu tata bahasa atau kelengkapan taksonomi semantik. |
| Ikhtisar empat tahap generasi dan perilaku tanpa leksikon: [pycos/bahasa/tutur.py L1–L30](pycos/bahasa/tutur.py#L1-L30), `L0` [L266–L514](pycos/bahasa/tutur.py#L266-L514), `L1` [L543–L656](pycos/bahasa/tutur.py#L543-L656), `L2` [L662–L818](pycos/bahasa/tutur.py#L662-L818), `L3` [L832–L1146](pycos/bahasa/tutur.py#L832-L1146), `Orkestrator` [L1152–L1236](pycos/bahasa/tutur.py#L1152-L1236), `TuturEngine` [L1522–L1572](pycos/bahasa/tutur.py#L1522-L1572) | Empat tahap dan facade engine diimplementasikan; tanpa leksikon `tersedia()` bernilai false dan `ucap()` mengembalikan `None`. | **Smoke test** berhasil dengan leksikon bundel dan contoh README. `SaSpTest` mencakup perilaku analyzer/presentation terpilih ([test_struktur_kognitif.py L702–L747](tests/test_struktur_kognitif.py#L702-L747)). |

| Redaksi “tidak hardcoded”: [pycos/bahasa/tutur.py L1–L10](pycos/bahasa/tutur.py#L1-L10) | L0 memiliki cabang tindak-tutur-ke-proposisi yang ditentukan di kode, sedangkan L1–L3 memakai frame berbasis data, pilihan leksikal, dan morfologi. | **Dikualifikasi:** keluaran tidak dipilih dari satu template balasan tetap, tetapi generator tidak sepenuhnya berbasis data atau terpelajar. README menjelaskan klaim yang lebih sempit dan akurat. |
| Analisis literal vs pragmatik kontekstual: [SASPAnalyzer L1242–L1516](pycos/bahasa/tutur.py#L1242-L1516), fungsi ringkas [L1575–L1591](pycos/bahasa/tutur.py#L1575-L1591) | Analyzer menyediakan jalur literal dan pragmatik terpisah; keluaran pragmatik memuat hipotesis serta bukti kontekstual. | **Diuji secara selektif** oleh `SaSpTest`; ini analyzer heuristik, bukan parser lengkap atau jaminan tentang maksud pembicara. |
| Jembatan state presentasi ke `GenContext`: [L1596–L1749](pycos/bahasa/tutur.py#L1596-L1749) | `konteks_dari_presentasi` membaca state/atribut `Presentasi` secara duck-typed, menggunakan nilai defensif/default bila field tidak tersedia, lalu membentuk konteks generasi. | **Diperiksa.** Tidak setiap kombinasi objek host eksternal diuji. |
| Jumlah entri dan metadata bahasa leksikon: [`pycos/sumber_daya/leksikon_pycos.json`](pycos/sumber_daya/leksikon_pycos.json) | Parse JSON menghasilkan 4.229 entri: 3.824 `id`, 405 `en`; record `meta` menyatakan jumlah yang sama. Smoke `TuturEngine.info()` juga melaporkan 4.229. | **Jumlah diverifikasi.** Kesamaan jumlah tidak membuktikan kebenaran leksikal, cakupan, atau kelancaran bahasa. |

#### `pycos/lingkungan/dunia.py` — lingkungan uji interaksi

| Blok klaim source | Bukti kode | Temuan / batasan |
| --- | --- | --- |
| Tujuan modul: dunia deterministik untuk menguji NPC (peta, objek, bahaya, cuaca, jam) dengan NPC dipanggil *duck-typed* dan memori opsional: [docstring L1–L59](pycos/lingkungan/dunia.py#L1-L59) | `Lingkungan.__init__` menyimpan peta, `random.Random(seed)`, jam, cuaca, objek, badan, dan antrean peristiwa ([L433–L453](pycos/lingkungan/dunia.py#L433-L453)); alur `langkah()` dijelaskan pada docstring kelas ([L415–L432](pycos/lingkungan/dunia.py#L415-L432)). | **Diperiksa dan diuji.** 61 tes `tests/test_lingkungan.py` menutup peta, gerak, objek, bahaya, cuaca, satiasi, interaksi, serialisasi, reward gagal, dan integrasi `Naluri`/`JejakPrediksi`. |
| Peta berpetak, medan berbiaya, dan validasi bentuk: kelas `Peta` [L207–L291](pycos/lingkungan/dunia.py#L207-L291) | `Peta.dari_ascii`, `bisa_dilewati`, `biaya`, dan `petak` mengimplementasikan kontrak; baris tidak seragam ditolak dengan `ValueError`. | **Diuji.** Peta uji kecil membuktikan dinding/air/batu terhalang, jalan lebih murah dari tanah, simbol tak dikenal dianggap tanah, dan `to_dict`/`from_dict` idempoten. |
| Objek dunia, efek per jenis, dan atribut kustom: `ObjekDunia` [L295–L345](pycos/lingkungan/dunia.py#L295-L345), tabel `EFEK_JENIS` [L129–L153](pycos/lingkungan/dunia.py#L129-L153) | Efek standar membaca tabel jenis; `atribut` dapat menimpa `delta`/`pesan`; `sekali_pakai` menentukan objek habis setelah dipakai. | **Diuji.** Makanan/air/obat sekali pakai, tempat aman dan penanda berulang; objek `bahaya`/`tempat_aman` tidak bisa masuk inventaris (`JENIS_DAPAT_DIAMBIL`). |
| Badan NPC dan pemisahan kognisi: `Badan` [L349–L411](pycos/lingkungan/dunia.py#L349-L411) | `Badan` hanya menyimpan posisi, inventaris, petak dikenal, perlindungan, satiasi, dan log; objek kognitif disimpan sebagai referensi `npc`/`jejak`. | **Diuji.** `SerialisasiTest` memastikan `to_dict()` tidak memuat `levels`/`params`, dan `from_dict(..., npcs=...)` menyambungkan kembali objek NPC yang sama. |
| Kontrak pemilihan aksi: kandidat berformat `Naluri.choose_action`, kebijakan defensif cadangan, dan satiasi yang juga terlihat di kandidat: [L614–L766](pycos/lingkungan/dunia.py#L614-L766) | `aksi_tersedia` menawarkan gerak/hampiri/dekati/ambil/pakai/menjauh/sapa/amati/istirahat/tunggu dengan `drive_effects`; `pilih_aksi` memakai `choose_action` bila ada, lalu jatuh ke `_pilih_defensif`; pengali satiasi diterapkan pada kandidat dan pada efek yang diterapkan. | **Diuji.** Stub tanpa `choose_action` tetap bertindak, pilihan NPC yang tidak valid jatuh ke jalur defensif, aksi yang diulang melemah, dan aksi lain pulih perlahan. Parameter `PENGURANGAN_ULANG`/`PEMULIHAN_ULANG`/`PLAFON_ULANG` adalah pilihan desain, bukan hasil pengukuran perilaku manusia. |
| Persepsi, peristiwa lingkungan, dan integrasi kognitif: `observasi` [L527–L598](pycos/lingkungan/dunia.py#L527-L598), `peristiwa_lingkungan` [L1103–L1130](pycos/lingkungan/dunia.py#L1103-L1130), `langkah` [L1157–L1279](pycos/lingkungan/dunia.py#L1157-L1279) | Persepsi menghasilkan daftar objek/NPC, paparan, dan ringkasan teks; peristiwa fase/cuaca/paparan diantre per NPC; `npc.tick(events=..., action_cost=True)`, `reward_for`, `predict`, dan `reinforce`/`record_experience` dipanggil secara defensif bila tersedia. | **Diuji untuk jalur terpilih.** Tidak ada pembuktian bahwa persepsi ini menyerupai penglihatan manusia, bahwa bobot efek/ambang bahaya realistis, atau bahwa perilaku NPC di dunia ini dapat digeneralisasi ke aplikasi host. |
| Serialisasi dunia dan pemisahan dari state kognitif: `to_dict`/`from_dict` [L1387–L1436](pycos/lingkungan/dunia.py#L1387-L1436) | Dunia menyimpan peta, objek, badan (posisi, inventaris, satiasi, riwayat 128 terakhir), cuaca, dan antrean; NPC disambungkan lewat argumen `npcs`/`jejak`. | **Diuji.** Round-trip idempoten untuk dunia dengan dan tanpa `JejakPrediksi`, termasuk antrean peristiwa; state kognitif tetap milik `Naluri.to_dict()` dan tidak disalin. |

#### `pycos/dukungan/patching.py` — integrasi berpagar

| Bagian docstring/komentar | Bukti kode | Bukti regresi / batasan |
| --- | --- | --- |
| Impor opsional, pemasangan hanya-tambah, batch atomik, idempotensi berbasis ID, dan pemeliharaan descriptor/wrapper: [modul L1–L8](pycos/dukungan/patching.py#L1-L8), [L23–L191](pycos/dukungan/patching.py#L23-L191) | `optional_module`, `install_method(s)`, `PatchConflictError`, dan `wrap_method` mengimplementasikan kontrak tersebut. | **Diuji secara selektif** oleh `SafeMethodPatchTest` ([test_organik_lanjutan.py L13–L56](tests/test_organik_lanjutan.py#L13-L56)): ID wrapper berulang tidak menumpuk, descriptor classmethod tetap bekerja, dan konflik batch tidak meninggalkan metode awal terpasang. Staticmethod, metaclass kustom, dan uji stres konkurensi tidak diuji terpisah. |

#### Docstring dan komentar dalam berkas tes

Komentar berikut menjelaskan skenario yang dicoba; bukti perilakunya adalah
assertion, bukan nama tes semata. Rentang baris diambil dari revisi ini.

| Bagian tes | Klaim yang diuji |
| --- | --- |
| [`test_struktur_paket.py`](tests/test_struktur_paket.py): `SusunanBerkasTest` [L64–L111](tests/test_struktur_paket.py#L64-L111), `JalurImporTest` [L114–L199](tests/test_struktur_paket.py#L114-L199), `GayaBerkasTesTest` [L203–L255](tests/test_struktur_paket.py#L203-L255), `ApiPublikTest` [L258–L338](tests/test_struktur_paket.py#L258-L338) | Susunan direktori dan himpunan berkas persis, larangan impor datar/relatif di source dan di berkas tes, keseragaman kepala berkas tes, resolusi nama bertitik opsional, serta fasad malas `from pycos import ...`. |
| [`test_sumber_daya.py`](tests/test_sumber_daya.py): `JalurSumberDayaTest` [L26–L74](tests/test_sumber_daya.py#L26-L74), `IsiLeksikonTest` [L77–L103](tests/test_sumber_daya.py#L77-L103), `TuturDanLeksikonTest` [L106–L158](tests/test_sumber_daya.py#L106-L158) | Jalur sumber daya absolut, kandidat terurut tanpa duplikat, jumlah dan pembagian bahasa leksikon, pemuatan leksikon oleh engine dan `Presentasi`, serta penerusan `SEBAB` pada ujaran `PERINGATAN`. |
| [`test_integrasi_paket.py`](tests/test_integrasi_paket.py): `MulaiCepatREADMETest` [L23–L50](tests/test_integrasi_paket.py#L23-L50), `HookOrganikTest` [L53–L91](tests/test_integrasi_paket.py#L53-L91), `KognisiLanjutTest` [L94–L113](tests/test_integrasi_paket.py#L94-L113), `RefleksiTest` [L116–L128](tests/test_integrasi_paket.py#L116-L128), `LingkunganTest` [L131–L147](tests/test_integrasi_paket.py#L131-L147), `JalurEksekusiTest` [L150–L192](tests/test_integrasi_paket.py#L150-L192) | Alur README, nama modul per lapisan, hook `mandiri` lewat `patching`, state Bayes round-trip, memori afektif, lingkungan yang menjalankan `Naluri`, serta eksekusi modul/berkas lewat jalur paket. |
| [`test_organik_lanjutan.py`](tests/test_organik_lanjutan.py): `SafeMethodPatchTest` [L27–L69](tests/test_organik_lanjutan.py#L27-L69), `ResiduTest` [L72–L102](tests/test_organik_lanjutan.py#L72-L102), `IntrusiTest` [L105–L119](tests/test_organik_lanjutan.py#L105-L119), `SelisihSelfTest` [L122–L137](tests/test_organik_lanjutan.py#L122-L137), `DetakInternalTest` [L140–L157](tests/test_organik_lanjutan.py#L140-L157), `KoherensiParalelTest` [L160–L180](tests/test_organik_lanjutan.py#L160-L180), `GejalaMurniOrdeNolTest` [L183–L248](tests/test_organik_lanjutan.py#L183-L248), dan primitif baru [L251–L398](tests/test_organik_lanjutan.py#L251-L398) | Keamanan patch dan persistensi Bayes per-instance; efek residu/tanpa decay; intrusi tanpa atensi biasa; deviasi diri; detak fraksional; konflik keyakinan paralel; properti gejala mentah, klaim, pemudaran, progresi kategori, serialisasi; serta regresi slot/luka/identitas/waktu/tutur/apersepsi/invensi/model kausal/planner. |
| [`test_struktur_kognitif.py`](tests/test_struktur_kognitif.py): memori [L26–L78](tests/test_struktur_kognitif.py#L26-L78), awareness/reportability [L81–L114](tests/test_struktur_kognitif.py#L81-L114), kejutan/kacamata sosial [L117–L155](tests/test_struktur_kognitif.py#L117-L155), vacancy [L158–L188](tests/test_struktur_kognitif.py#L158-L188), pipeline gejala [L191–L307](tests/test_struktur_kognitif.py#L191-L307) | Memori mati diketahui versus belum pernah diketahui dan rewrite saat recall; awareness/reportability; structural shock dan persistensi keyakinan sosial; perilaku vacancy; klaim gejala, pemudaran, penamaan, dan persistensi. |
| `test_struktur_kognitif.py`: presentasi/kepribadian [L310–L441](tests/test_struktur_kognitif.py#L310-L441), waktu subjektif/tubuh [L444–L516](tests/test_struktur_kognitif.py#L444-L516), kelelahan/penahanan/audisi diri [L519–L711](tests/test_struktur_kognitif.py#L519-L711) | Presentasi protektif terpilih, jeda/variasi, persistensi state, half-life subjektif, lokus tubuh, efek kelelahan, penahanan tutur kumulatif, dan konsekuensi audisi diri. |
| `test_struktur_kognitif.py`: bahasa/sosial/kognisi [L714–L942](tests/test_struktur_kognitif.py#L714-L942) | Analisis literal/pragmatik terpilih, strategi sosial, opasitas epistemik, perilaku estetis/bosan, insight tidur, round-trip JSON, dan pemilihan tujuan tanpa digerakkan vektor drive. |
| [`test_perbaikan_analisis.py`](tests/test_perbaikan_analisis.py#L309-L348): `SalienceReproducibilityTest`, `DemoKognisiTest` | Recency eksternal dapat diputar ulang dengan waktu injeksi; demo kognisi benar-benar memasang `JejakPrediksi` dan melaporkan setpoint NURANI. |
| [`test_lingkungan.py`](tests/test_lingkungan.py): `PetaTest` [L64–L108](tests/test_lingkungan.py#L64-L108), `ObjekDuniaTest` [L111–L133](tests/test_lingkungan.py#L111-L133), `PendaftaranTest` [L136–L170](tests/test_lingkungan.py#L136-L170), `GerakTest` [L173–L239](tests/test_lingkungan.py#L173-L239), `ObjekAksiTest` [L242–L324](tests/test_lingkungan.py#L242-L324), `BahayaDanCuacaTest` [L327–L396](tests/test_lingkungan.py#L327-L396), `SatiasiTest` [L399–L445](tests/test_lingkungan.py#L399-L445) | Peta dan medan, penolakan aksi terhalang, bonus eksplorasi, ambil/pakai objek, perlindungan yang melebur, paparan bahaya, fase jam, cuaca deterministik, dan satiasi aksi. |
| `test_lingkungan.py`: `InteraksiTest` [L448–L492](tests/test_lingkungan.py#L448-L492), `ObservasiTest` [L495–L526](tests/test_lingkungan.py#L495-L526), `SerialisasiTest` [L529–L573](tests/test_lingkungan.py#L529-L573), `IntegrasiNaluriTest` [L576–L662](tests/test_lingkungan.py#L576-L662), `JalurEksekusiTest` [L664–L681](tests/test_lingkungan.py#L664-L681), `KonstantaTest` [L683–L694](tests/test_lingkungan.py#L683-L694) | Antrean peristiwa antar-NPC, ringkasan persepsi, rendering ASCII, round-trip dunia tanpa state kognitif, jalannya `Naluri` + `JejakPrediksi` di dalam dunia, penanganan kegagalan reward, dan eksekusi demo lewat dua jalur. |

### Catatan dan klaim yang belum terbukti

1. **Rujukan historis yang tidak ada di checkout ini** (diperbaiki 2026-10-18:
   kini ditandai eksplisit sebagai berkas di luar repo, bukan perintah yang
   dapat direproduksi). `pycos/refleksi/nurani.py` menyebut `run.py` dan
   `analysis/RINGKASAN_NURANI.md`; tidak satu pun path itu ada di sini,
   sehingga perintah tes/laporan historis tersebut tidak dapat direproduksi.
   Sebaliknya, dua berkas tes yang dulu
   diragukan (`test_organik_lanjutan.py`, `test_struktur_kognitif.py`) **ada**
   pada checkout ini dan sejak perbaikan impor ikut dijalankan oleh
   `python -m unittest discover`; keduanya memakai jalur paket `pycos.*`, bukan
   impor datar. Suite aktif kini sepuluh berkas dan 301 tes (rincian di atas).
2. **Judul pilar tidak konsisten** (diperbaiki 2026-10-18: judul docstring
   kini "Enam pilar (A–F) dan Watak (W)" dengan catatan historis). Ikhtisar
   `pycos/refleksi/nurani.py` pernah menyebut “Empat pilar”,
   sementara label yang ada A–F dan WATAK ([pycos/refleksi/nurani.py](pycos/refleksi/nurani.py)).
   Implementasi memiliki flag pilar dasar serta ekstensi sosial/persepsi dan
   state terasa.
3. **Klaim gate default bersifat kondisional.** Flag fitur dalam default NURANI
   sendiri bernilai false ([pycos/refleksi/nurani.py L128–L336](pycos/refleksi/nurani.py#L128-L336)). Namun,
   di `Naluri` beberapa flag anak `enable_*` bernilai true sementara gate induk
   seperti `enable_kesadaran` dan `enable_presentasi` false; preset kepribadian
   juga dapat mengatur flag lain ([pycos/inti/naluri.py L338–L540](pycos/inti/naluri.py#L338-L540),
   [L541–L648](pycos/inti/naluri.py#L541-L648)). Jadi “mati secara bawaan” tidak berlaku
   secara literal untuk setiap parameter; periksa gate induk dan preset aktif.
4. **Analogi ilmiah bukan validasi ilmiah.** Komentar mengaitkan variabel
   dengan insula, ACC, PFC, DMN, Global Workspace, dan teori somatic-marker
   ([pycos/inti/naluri.py L11396–L11406](pycos/inti/naluri.py#L11396-L11406),
   [pycos/refleksi/nurani.py L267–L276](pycos/refleksi/nurani.py#L267-L276),
   [pycos/refleksi/nurani.py L1845–L1856](pycos/refleksi/nurani.py#L1845-L1856)). Kode dan tes unit tidak
   membuktikan bahwa mekanisme tersebut akurat secara biologis. Secara khusus,
   frasa “fisiologi nyata, bukan pseudo-science” dalam docstring demo
   ([pycos/inti/naluri.py L14284–L14293](pycos/inti/naluri.py#L14284-L14293)) lebih kuat daripada
   bukti yang tersedia di repositori ini. Anggap sebagai analogi desain.
5. **Pernyataan performa bukan hasil benchmark.** Indeks terbalik, MinHash,
   spatial hash, counter profiler, dan cabang LOD ada di source
   ([pycos/memori/jejak_prediksi.py L715–L807](pycos/memori/jejak_prediksi.py#L715-L807),
   [pycos/inti/naluri.py L12956–L13360](pycos/inti/naluri.py#L12956-L13360)); tidak ada dataset
   benchmark atau laporan performa yang dapat diulang. Label kompleksitas
   seperti O(k), perkiraan penghematan seperti “~90%”, dan klaim skalabilitas
   adalah ekspektasi desain sampai diukur pada beban kerja host tertentu.
6. **Kealamian, kognisi, dan kebenaran tidak dievaluasi eksternal.** Repositori
   tidak menyertakan evaluasi dialog oleh manusia, benchmark akurasi domain,
   suite uji NLP adversarial, atau perbandingan neurosains. Keluaran heuristik
   bisa keliru walaupun jalur kode dan tes unit berfungsi sesuai implementasi.
7. **Nama integrasi eksternal bukan dependensi bundel.** Nama seperti
   `samre.core.brain`, `samre.imagination.engine`, dan `SamanticGarden` muncul
   dalam komentar/deskripsi API ([pycos/inti/naluri.py L26–L29](pycos/inti/naluri.py#L26-L29),
   [L242–L249](pycos/inti/naluri.py#L242-L249)). Nama-nama itu adalah titik integrasi host
   duck-typed yang opsional; paket-paket tersebut tidak disertakan dalam
   checkout ini.
8. **“Permanen” berarti persistensi state/objek, bukan tidak dapat diubah.**
   Misalnya, nilai yang dipelajari `EversiTD` berada di objek dan dapat
   diserialisasi; kata itu tidak membuktikan pembelajaran jangka panjang yang
   tak dapat dibatalkan atau kepribadian stabil.
9. **Cakupan versi/platform terbatas.** Workflow `.github/workflows/ci.yml`
   mendeklarasikan matrix tes Python 3.9–3.14, tetapi job hosted belum
   dijalankan/dikonfirmasi dari workspace ini; validasi lokal dilakukan pada
   Python 3.11.2. Ini bukan bukti untuk Termux, semua sistem operasi, atau
   setiap lingkungan host.

10. **Lingkungan uji adalah simulasi berpetak, bukan validasi dunia nyata.**
   `pycos/lingkungan/dunia.py` menyediakan ruang, sumber daya, bahaya, cuaca,
   dan konsekuensi yang deterministik, tetapi tidak ada fisika kontinu,
   penglihatan, jaringan, atau pengukuran beban kerja: ambang paparan, bobot
   efek objek, kurva satiasi aksi, dan panjang langkah adalah pilihan desain.
   `render()` adalah ASCII untuk pemeriksaan manusia, dan `langkah_semua()`
   memanggil satu NPC per siklus — bukan game loop produksi maupun bukti
   skalabilitas untuk banyak NPC. Klaim “lingkungan nyata” pada docstring
   modul harus dibaca sebagai “dunia simulasi dengan konsekuensi eksplisit”,
   bukan kesetaraan dengan dunia fisik.

### Kesimpulan

Source, data, dan tes regresi yang disebut mendukung **mekanisme yang memang
diimplementasikan** serta contoh yang berhasil di-smoke-test di atas, termasuk
lingkungan uji `pycos.lingkungan` yang menjalankan `Naluri` sungguhan di dalam
dunia berpetak. Bukti itu tidak mendukung penafsiran metafora sebagai
kesadaran, neurosains sebagai implementasi tervalidasi, daftar API sebagai
cakupan tes penuh, komentar kompleksitas sebagai hasil performa, atau dunia uji
sebagai simulasi dunia fisik. Jika dokumentasi source menunjuk artefak yang
hilang atau memakai redaksi lebih kuat daripada bukti, celah tersebut dicatat di
sini alih-alih dianggap terbukti.

### Audit source menyeluruh (22 Oktober 2026)

Lihat [analisis semua 38 berkas](docs/AUDIT_PYTHON.md) dan
[lampiran callable/hash source](docs/AUDIT_PYTHON_RINCI.md). Dua belas regresi
baru di `test_perbaikan_analisis.py` mencakup `AuditPersonaTest`,
`AuditTrenTest`, `AuditSnapshotTest`, `AuditRollbackPatchTest`,
`AuditKognisiTest`, dan `AuditCliTest`. Baseline 315 tes menjadi **327 tes**.
Tes struktur mengganti `eval` dengan `ast.literal_eval` dan mengirim `[]`
secara eksplisit ke `utama` agar tidak mengonsumsi argumen runner tes.

Perbaikan terbukti: validasi string pantangan tidak terlewati; tren datar
pada ambang nol stabil dan ambang inf ditolak; snapshot diagnostik nested
terisolasi; rollback patch memulihkan metadata fungsi; clamp lokal netral
konsisten; konfigurasi dan kelanjutan pembelajaran EversiTD bertahan setelah
JSON roundtrip, termasuk kompatibilitas save lama; opsi CLI salah gagal
terlihat. Perubahan EversiTD **bukan** klaim resume state RNG seluruh NPC.

### Audit ulang seluruh Python (8 November 2026)

[Analisis per berkas terkini](docs/AUDIT_PYTHON_LANJUTAN.md) mencakup 39/39
berkas Python (38 awal + generator baru), tanpa pengecualian demo, private,
nested, init, atau tools. Baseline 327 tes menjadi **339 tes**. Dua belas tes
baru: `AuditGrafPersistensiTest`, `AuditPenyebaranTest`,
`AuditResumeKognisiTest`, `AuditGeneratorTest` (masing-masing tiga).

Bukti baru membandingkan **langkah berikutnya** setelah JSON roundtrip:
konfigurasi pembelajaran/peluruhan graf, pasangan nama yang mengandung `|`,
cache Gaussian RNG, dan konteks transisi TD milik wrapper Naluri. Save graf
baru memakai pasangan terstruktur; loader baru tetap membaca format lama,
tetapi save baru tidak dijanjikan terbaca oleh versi lama. Collision dalam
save lama yang sudah kehilangan informasi tidak direkonstruksi secara spekulatif.

`python3 tools/audit_python.py --check` memeriksa inventaris dan hash seluruh
source; CI menjalankannya pada Python 3.11. Tool mengagregasikan syntax error
semua berkas dan gagal, bukan melewati berkas rusak. Perintah compile/lint
kini juga mencakup `tools`; pengecualian lint re-export init bukan pengecualian
audit. Semua `__init__.py` tetap diindeks dan ekspornya diuji.

### Pembaruan fase 4 — R4.1 tahap pertama

**437 tes lulus**, termasuk 14 SST. Lima tes baru mengunci API publik Naluri,
identitas kelas lintas jalur/urutan impor, lazy facade, pickle historis, dan
kelanjutan RNG ritual. Sebelas cek kesehatan, compileall, demo CLI, Pyflakes
4.0.3 (non-init), audit AST 48 berkas dan diff check lulus.
Ritual/Reputasi/KawananNPC sudah dipisahkan; R4.1 belum selesai.
Lihat [rincian struktur dan sisa pekerjaan](docs/IMPLEMENTASI_REKOMENDASI_FASE4_STRUKTUR.md).

### Pembaruan fase 4 — R4.1 tahap kedua

**440 tes lulus**, termasuk 14 SST dan delapan tes refaktor. Kesadaran dan
Presentasi kini berada di modul pemilik; konfigurasi memakai referensi bersama.
Kontrak AST kedua kelas dibandingkan baseline sebelum pemindahan; hanya impor
backend lokal yang ditambahkan. Tes diagnostik mencakup semua modul hasil
pemisahan. Sebelas cek kesehatan, compileall, demo CLI, Pyflakes 4.0.3 non-init,
audit AST 51 berkas, dan diff check lulus. R4.1 masih terbuka untuk demo,
ekstensi, dan target semua berkas ≤5.000 baris.

### Pembaruan fase 4 — R4.1 tahap ketiga

**444 tes lulus**, termasuk 14 SST dan 12 tes refaktor. Seluruh showcase berhasil
dijalankan melalui `python -m pycos.inti.demo` dan jalur lama
`python -m pycos.inti.naluri`. Impor produksi tidak memuat subpaket demo.
Ekstensi pelindung dipasang eksplisit; patch ID/urutannya dibandingkan fixture
sebelum pemindahan dan diuji idempoten. Assertion demo watak yang salah arah
(telah dikonfirmasi juga gagal pada baseline sebelum refaktor) dikoreksi untuk
mengukur magnitudo perubahan setpoint. Algoritme NPC tidak berubah.
Sebelas cek kesehatan, compileall, Pyflakes 4.0.3 non-init, demo CLI penilai,
audit AST 56 berkas dan diff check lulus. R4.1 tetap belum selesai: ekstensi
lain dan target semua berkas ≤5.000 baris masih terbuka.

### Pembaruan fase 4 — R4.1 selesai secara struktural

**448 tes lulus**, termasuk 14 SST dan 16 tes refaktor. Mesin Naluri, Goal/Mood,
dan seluruh ekstensi telah dipisahkan. Facade 979 baris, mesin 4.815 baris;
setiap berkas Python inti ≤5.000 baris, dijaga tes rekursif. Identitas kelas,
API publik, pickle, AST kelas, patch ID/urutannya, idempotensi registri lengkap,
dan hook lintas ekstensi tetap diuji. Registri menolak nama asing sebelum impor.
Impor semua modul ekstensi sebelum facade tidak memasang patch.
Sebelas cek kesehatan, compileall, Pyflakes 4.0.3 non-init, demo CLI dan seluruh
showcase, audit AST 66 berkas dan diff check lulus secara lokal (Python 3.11).
R4.2/R4.3 belum dikerjakan; tidak ada klaim pencapaian target save/performa atau
hasil korpus manusia eksternal. Lihat dokumen struktur untuk rincian dan batas
kompatibilitas global internal.

### Pembaruan fase 4 — R4.2 inventaris patch

**455 tes lulus**, termasuk 14 SST. Tujuh regresi baru memeriksa snapshot patch,
jenis descriptor, urutan ID, referensi lemah, rollback, kecocokan fixture inti,
dan keluaran teks/JSON `--periksa`. Manifest SST `dukungan.inventaris_patch`
aktif tanpa menambah NPC. Inventaris tidak memuat mesin dan bukan verifikasi
integritas kode. Sebelas cek kesehatan, compileall, Pyflakes 4.0.3 non-init,
demo CLI, audit AST 66 berkas dan diff check lulus pada Python lokal 3.11.
R4.3 belum dikerjakan. Rincian:
[API inventaris dan batas bukti](docs/IMPLEMENTASI_REKOMENDASI_FASE4_PATCH.md).

### Pembaruan fase 4 — R4.3 konstanta dan penjepitan

**464 tes lulus**, termasuk 14 SST. Sembilan regresi baru memeriksa identitas
semua alias drive, literal duplikat, impor ringan, perbandingan helper netral,
varian tutur/persona/ketidaktahuan, inventaris definisi helper, dan tiga modul
mandiri yang diimpor tanpa paket. SST mengaktifkan `dukungan.konstanta`.
Sebelas cek kesehatan, compileall, Pyflakes 4.0.3 non-init, demo CLI, pemeriksaan
leksikon, audit AST 68 berkas dan diff check lulus pada Python lokal 3.11.
R4.1–R4.3 selesai pada cakupan terdokumentasi; fase 5 belum dimulai. Rincian:
[sumber drive dan kontrak numerik](docs/IMPLEMENTASI_REKOMENDASI_FASE4_KONSTANTA.md).

### Pembaruan fase 5 — R5.1 tahap awal

**469 tes lulus**, termasuk 14 SST dan lima tes baru untuk gate laporan.
Mypy 1.15.0 strict lulus pada 15 berkas dukungan/kontrak/persona. Coverage diukur
dengan coverage 7.6.12: gate ≥80% per berkas kelompok awal lulus; tool baru
98,73%; global pycos+tools 71,50%. Kontrak masih sekitar 59,8% sehingga belum
termasuk floor coverage 80%, meskipun termasuk strict typing.
Benchmark tanpa coverage: tick 0,1163 ms; predict fixture 2.000/256 4,5769 ms,
lulus anggaran R5.1 <2/<5 ms, bukan target fase 2 ≤3 ms. Wheel memuat py.typed.
Sebelas cek kesehatan, compileall, Pyflakes, indeks audit 70 berkas, dan diff
check lulus lokal. CI quality dikonfigurasi; belum ada klaim hasil remote.
R5.1 belum selesai: typing Nurani/Tutur dan perluasan gate masih terbuka.
[Rincian dan batas bukti](docs/IMPLEMENTASI_REKOMENDASI_FASE5_GATE.md).

### Pembaruan R5.1 — typing Nurani/Tutur

**477 tes lulus** (delapan baru), termasuk 14 SST. Mypy strict kini lulus pada
17 berkas termasuk Nurani/Tutur, tanpa ignore modul. Perbaikan narrowing juga
menangani `kerangka=None` pada modifier L3, dijaga regresi runtime. Coverage
Nurani 83,95% dan Tutur 84,25% sekarang digate ≥80% per berkas. Global masih
72,44%, kontrak 60,14%; tidak ada klaim keduanya telah mencapai 80%.
Benchmark tanpa tracing: tick 0,0893 ms dan predict 2.000/256 3,2380 ms;
gate R5.1 <2/<5 ms lulus, target fase 2 ≤3 ms tetap terbuka. Sebelas cek
kesehatan, compileall, Pyflakes, audit AST 71 berkas, dan diff check lulus lokal.
Cakupan typing rekomendasi sudah diperluas; coverage kontrak legacy masih
pekerjaan lanjutan. CI remote belum diverifikasi; R5.2 belum dimulai.

### Pembaruan R5.1 — kontrak masuk coverage gate

**487 tes lulus**, termasuk 14 SST dan sepuluh tes kontrak baru. Coverage kontrak
naik ke **93,18%** dan kini wajib ≥80% pada gate; Nurani 83,95%, Tutur 84,25%.
Seluruh kelompok strict 17 berkas dan tool gate dicakup floor per berkas.
Coverage global masih 73,29%; tidak ada klaim ≥80% seluruh paket atau seluruh
branch. Tes mencakup 11 operasi pre/post, valid/invalid state, forecast, linkage,
level/fase, alias, fault injection, dan manifest skema yang rusak.
Mypy strict, compileall, Pyflakes, 11 cek kesehatan, audit AST 72 berkas dan
diff check lulus lokal. Gate performa lulus: tick 0,1049 ms; predict 2.000/256
4,3269 ms. Cakupan rekomendasi R5.1 terpenuhi; CI remote belum diverifikasi.
R5.2 belum dimulai. Rincian ada pada dokumen implementasi fase 5.

### R5.2 — contoh runnable

492 tes lulus (64,655 detik), termasuk 14 SST dan 5 tes integrasi contoh.
Empat modul `examples/` dijalankan via subprocess; assertion memeriksa state
JSON serta determinisme, bukan hanya exit code. Mypy strict 17 berkas,
Pyflakes, compileall, health 11 cek, audit AST/check, dan coverage gate lulus.
Global coverage tetap 73,2880% (subprocess tidak digabungkan).
Gate performa: tick 0,0846 ms; predict 2000/256 3,2776 ms, lulus <2/<5 ms.
Rincian: `docs/IMPLEMENTASI_REKOMENDASI_FASE5_CONTOH.md`.

### R5.3 — changelog dan kontribusi

499 tes lulus (63,506 detik), termasuk 14 SST dan 7 tes gate changelog.
Tool diff AST `from_dict` mencapai coverage 94,74% dan masuk gate ≥80% per-file.
Global coverage 73,3244%. Mypy strict 17 berkas, lint, compileall, audit/check,
health 11 cek, diff check dan gate coverage/performa lulus. Tick 0,0821 ms;
predict 2000/256 3,4415 ms. Gate changelog berjalan pada CI PR terhadap base SHA;
remote CI belum dijalankan. Lihat `docs/IMPLEMENTASI_REKOMENDASI_FASE5_CHANGELOG.md`.

### R5.4 — ekspos API publik

503 tes lulus (71,836 detik), termasuk 14 SST dan 4 tes API publik baru.
64 alias root ditambah; seluruh ekspor subpaket diklasifikasikan, dua nama
sengaja tetap di subpaket. SST memetakan alias ke kelompok wajib aktif.
Root coverage 100% baris; global 73,3244%. Coverage gate, strict mypy 17 berkas,
lint, compileall, audit/check, changelog gate dan health 11 cek lulus.
Tick 0,0930 ms dan predict 2000/256 3,8211 ms lulus gate <2/<5 ms.
Remote CI belum dijalankan. Lihat `docs/IMPLEMENTASI_REKOMENDASI_FASE5_API.md`.

### R5.5 — adapter host

508 tes lulus (74,225 detik), termasuk 14 SST dan lima tes konektor.
Strict mypy 18 berkas lulus; konektor coverage 98,89% dan ditambahkan ke gate
≥80% per-file. Global 73,4312%. Lint/compile/audit/check/changelog gate dan
health 11 cek lulus. Tick 0,0925 ms; predict 2000/256 4,1737 ms, gate lulus.
Inspector smoke dengan DOM tiruan Node lulus; Godot belum diuji dalam engine,
browser visual serta CI remote belum diuji.
Rincian: `docs/IMPLEMENTASI_REKOMENDASI_FASE5_KONEKTOR.md`.
