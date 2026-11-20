# Pycos

Pycos adalah toolkit Python berbasis sumber untuk membangun NPC dan agen
simulasi yang memiliki state. Modul-modulnya memodelkan motivasi, afek,
memori, atensi, refleksi, interaksi sosial, perencanaan, dan dialog sebagai
state serta aturan eksplisit yang dapat diperiksa dan dipanggil aplikasi host.

Istilah di dalam implementasi—seperti *kesadaran*, *emosi*, *agensi*,
*memori*, dan *kehendak bebas*—menamai state dan perilaku simulasi perangkat
lunak. Istilah itu **bukan** klaim bahwa program ini sadar, memiliki perasaan
manusia, atau merupakan model otak biologis yang tervalidasi. Prediksi dan
dialog adalah keluaran heuristik, bukan fakta atau jaminan.

README ini merupakan peta terpadu untuk pengguna. Docstring dan komentar di
source Python tetap ada; [`VALIDATION.md`](VALIDATION.md) memetakan klaim
perilaku di dalamnya ke bukti yang tersedia.

## Status terkini

Snapshot source `95cba32` (setelah R5.5), diverifikasi ulang lokal pada
**2026-10-17**, Python **3.11.2**: **508 tes lulus**, termasuk **14 SST**;
health check **11 cek**, mypy strict **18 berkas**, dan seluruh gate lokal lulus.
Coverage global **73,43%**, bukan klaim ≥80% seluruh paket. CI dikonfigurasi
untuk Python 3.9–3.14; hasil remote tidak diverifikasi pada pembaruan ini.
[Rincian hasil dan batas bukti](VALIDATION.md#validasi-terkini).

R0–R4 serta R5.1–R5.5 sudah diimplementasikan pada cakupan terdokumentasi.
R5.6 (adapter LLM opsional dengan guardrail) **belum diimplementasikan**.

## Isi repositori

Source runtime berada di paket `pycos/`; tool pengembangan, tes, dan contoh
berada di `tools/`, `tests/`, dan `examples/`. Peta berikut diringkas; indeks
source lengkap tersedia di [lampiran AST](docs/AUDIT_PYTHON_RINCI.md). Setiap
subpaket mengekspor API utamanya melalui `__init__.py`.

```text
Pycos/
├── pycos/                       # paket Python (namespace tunggal: `pycos`)
│   ├── __init__.py              # API publik malas — `from pycos import Naluri`
│   ├── __main__.py              # peta paket + penilaian keselarasan; `--periksa` untuk CI
│   ├── kontrak.py               # kontrak antarlapisan (JANJI/KEBUTUHAN) + validasi argumen
│   ├── konektor.py              # adapter snapshot host + CLI JSON
│   ├── py.typed                 # penanda distribusi bertipe
│   ├── inti/
│   │   ├── __init__.py
│   │   ├── naluri.py            # fasad kompatibilitas & registri integrasi
│   │   ├── mesin.py             # implementasi mesin Naluri
│   │   ├── keadaan.py           # implementasi state/serialisasi mesin
│   │   ├── _konfigurasi.py      # parameter dan konfigurasi inti
│   │   ├── persona.py           # Persona & Keadaan (data ringan)
│   │   ├── kesadaran.py, presentasi.py, ritual.py, reputasi.py, kawanan.py
│   │   ├── ekstensi/            # integrasi opsional dan persistence
│   │   └── demo/                # showcase; python -m pycos.inti.demo
│   ├── refleksi/
│   │   ├── __init__.py
│   │   ├── nurani.py            # NURANI: meta-plastisitas, introspeksi, penilai keselarasan
│   │   └── ketidaktahuan.py     # view reflektif ketidaktahuan (tanpa state)
│   ├── memori/
│   │   ├── __init__.py
│   │   └── jejak_prediksi.py    # JEJAK: memori episodik + prediksi outcome
│   ├── mandiri/
│   │   ├── __init__.py
│   │   ├── organik.py           # primitif "state organik" + wadah `Organik`
│   │   └── kognisi_lanjut.py    # lima mekanisme komputasional opsional
│   ├── bahasa/
│   │   ├── __init__.py
│   │   └── tutur.py             # MESIN TUTUR L0–L3 + SA_SP + ciri linguistik
│   ├── lingkungan/
│   │   ├── __init__.py
│   │   └── dunia.py             # dunia uji: peta, objek, bahaya, cuaca, NPC
│   ├── dukungan/
│   │   ├── __init__.py
│   │   ├── konstanta.py         # nama drive bersama
│   │   ├── patching.py          # penjaga batas integrasi runtime antarlapisan
│   │   ├── sumber.py            # resolusi path sumber daya paket
│   │   ├── numerik.py           # jepit/float_hingga: penjagaan NaN dan batas
│   │   ├── diagnostik.py        # catatan kegagalan yang sebelumnya tersenyap
│   │   ├── periksa.py           # pemeriksaan kesehatan (`python -m pycos --periksa`)
│   │   ├── validasi_state.py, persistensi.py, parameter.py, batas_memori.py, leksikon.py
│   │   └── tolok.py             # tolok kinerja (`python -m pycos.dukungan.tolok`)
│   └── sumber_daya/
│       ├── __init__.py
│       ├── leksikon_pycos.json  # data leksikal yang ikut terpasang
│       └── korpus_contoh.jsonl  # korpus contoh berlabel (dilabeli penulis)
├── tests/                       # tes unittest: struktur paket, sumber daya,
│                                #   integrasi, perilaku kognitif, lingkungan uji,
│                                #   keselarasan ujaran, perbaikan analisis, SST
├── examples/                    # 4 contoh Python, Godot, inspector HTML
├── tools/                       # audit AST, gate coverage/performa/changelog
├── docs/                        # audit, rekomendasi, kontrak dan implementasi
├── CHANGELOG.md                 # riwayat perubahan & kompatibilitas save
├── CONTRIBUTING.md              # setup dan pemeriksaan kontribusi
├── pyproject.toml               # metadata paket; nol dependensi runtime
├── README.md                    # dokumen ini
├── VALIDATION.md                # pemetaan klaim docstring ke bukti
└── LICENSE                      # MIT
```

Tiga gaya impor berikut menunjuk objek yang sama:

```python
from pycos import Naluri              # fasad tingkat paket (impor malas)
from pycos.inti import Naluri         # subpaket
from pycos.inti.naluri import Naluri  # berkas modul
```

| Subpaket / berkas | Tanggung jawab | Titik masuk utama |
| --- | --- | --- |
| [`pycos/inti/naluri.py`](pycos/inti/naluri.py) | Fasad kompatibilitas untuk mesin `mesin.py`, state `keadaan.py`, kelas pemilik terpisah, serta ekstensi. Menyediakan enam drive, afek, tujuan, penilaian aksi, waktu/tidur, atensi, dan utilitas multi-NPC. Ekstensi opsional dihubungkan pada batas integrasi runtime; kegagalan impor lapisan opsional dicatat ke `dukungan.diagnostik`. | `Naluri`, `Kesadaran`, `Presentasi`, `KawananNPC`, `Reputasi` |
| [`pycos/konektor.py`](pycos/konektor.py) | Transformasi snapshot host terisolasi: persepsi ke events, pemilihan aksi pada clone, dan CLI request/response JSON. Tidak menerapkan aksi pada NPC host. | `observasi`, `aksi`, `python -m pycos.konektor --json` |
| [`pycos/inti/persona.py`](pycos/inti/persona.py) | Data murni profil `Persona` (sifat, register, kata pantangan) dan ringkasan `Keadaan` batin (valensi, gairah, ketidakpastian). Modul ringan agar CLI dan penilai tidak memuat mesin `Naluri`; kelas yang sama dire-ekspor dari `pycos.inti.naluri` untuk kompatibilitas. | `Persona`, `Keadaan`, `PERSONA_CONTOH` |
| [`pycos/refleksi/nurani.py`](pycos/refleksi/nurani.py) | Refleksi dan meta-plastisitas yang dapat membaca dan memengaruhi `Naluri`: memori afektif/sosial, kalibrasi, setpoint bergerak, keterkaitan interoseptif, persepsi, konflik/flow, state introspeksi/pelaporan, serta **penilaian keselarasan ujaran** (skor per dimensi, pelacak drift lintas giliran, kalibrasi korpus berlabel). | `Nurani`, `CalibrationReport`, `nilai_selaras`, `PelacakSelaras`, `laporan_kalibrasi` |
| [`pycos/memori/jejak_prediksi.py`](pycos/memori/jejak_prediksi.py) | Penyimpanan pengalaman episodik, retrieval berbasis cue, prediksi outcome, pemeringkatan aksi, penguatan, daur hidup memori, serta utilitas autobiografi/pola. Integrasi `Naluri` bersifat opsional dan duck-typed. | `JejakPrediksi` |
| [`pycos/mandiri/organik.py`](pycos/mandiri/organik.py) | Primitif state independen untuk topologi, pengecualian, batas identitas, waktu heterogen, penolakan tutur, rasa tidak pasti, keyakinan paralel, sinyal tubuh, residu, intrusi, detak internal fraksional, vacancy, kategori emergen, invensi, model kausal, dan perencanaan. | `Organik` dan kelas-kelas primitifnya |
| [`pycos/mandiri/kognisi_lanjut.py`](pycos/mandiri/kognisi_lanjut.py) | Lima mekanisme komputasional opsional: evolusi parameter berbasis TD, pemilihan aksi Boltzmann, pembaruan keyakinan log-odds, graf asosiasi, dan drift Ornstein–Uhlenbeck terbatas. | `EversiTD`, `boltzmann_pilih`, `MesinKepercayaan`, `GrafAsosiasi`, `ProsesOU`, `KognisiLanjut` |
| [`pycos/bahasa/tutur.py`](pycos/bahasa/tutur.py) | Generator dialog berbasis leksikon, penganalisis semantik/pragmatik ujaran yang terpisah, dan ciri linguistik dangkal berbasis leksikon (polaritas, formalitas, intensitas, keraguan; negasi berbatas klausa). | `TuturEngine`, `GenContext`, `SASPAnalyzer`, `sa_sp`, `sa_sp_literal`, `sa_sp_pragmatik`, `analisis_teks`, `LeksikonCiri` |
| [`pycos/lingkungan/dunia.py`](pycos/lingkungan/dunia.py) | Lingkungan uji interaksi: peta berpetak, medan yang bisa/tidak bisa dilewati, objek yang bisa diambil dan dipakai, bahaya yang memapar, cuaca serta siklus jam, antrean peristiwa, dan NPC lain yang bisa disapa. NPC dipanggil secara duck-typed (`choose_action`, `tick`, `reward_for`, `levels`), memori `JejakPrediksi` opsional per badan, dan state dunia dapat diserialisasi terpisah dari kognisi NPC. | `Lingkungan`, `Peta`, `ObjekDunia`, `Badan`, `peta_contoh`, `demo` |
| [`pycos/dukungan/patching.py`](pycos/dukungan/patching.py) | Utilitas integrasi runtime internal: impor opsional, pemasangan metode yang hanya menambah API, batch atomik, deteksi konflik, dan wrapper metode idempoten. | `optional_module`, `install_method(s)`, `wrap_method`, `PatchConflictError` |
| [`pycos/dukungan/numerik.py`](pycos/dukungan/numerik.py) | Penjagaan numerik bersama: `jepit` (NaN dijadikan 0, lalu dijepit), `jepit_drive` ([-1, 1]), `jepit_01` ([0, 1]), dan `float_hingga` yang menolak nilai non-finite di batas masuk. | `jepit`, `jepit_drive`, `jepit_01`, `float_hingga` |
| [`pycos/dukungan/diagnostik.py`](pycos/dukungan/diagnostik.py) | Ring buffer kecil untuk kegagalan yang sengaja tidak melempar galat (mis. kandidat aksi dengan kunci salah, leksikon yang gagal dimuat). Tidak pernah melempar dan tidak mengubah hasil fungsi. | `catat`, `laporan`, `kosongkan` |
| [`pycos/dukungan/periksa.py`](pycos/dukungan/periksa.py) | Pemeriksaan kesehatan: impor modul inti, kontrak startup, leksikon, smoke test NPC, determinisme seed, validasi input buruk, pipeline penilai keselarasan, korpus contoh, dan validator argumen batas. Kode keluar 0 atau 1. | `jalankan`, `main_periksa` |
| [`pycos/dukungan/tolok.py`](pycos/dukungan/tolok.py) | Tolok ringan: ms per tick Naluri, pemilihan aksi, peringkat JejakPrediksi, dan muat leksikon dingin vs hangat. | `jalankan_semua`, `main` |
| [`pycos/kontrak.py`](pycos/kontrak.py) | Kontrak antarlapisan: manifest `JANJI`/`KEBUTUHAN` (termasuk `Persona`, `Keadaan`, `PelacakSelaras`, dan kebutuhan penilai keselarasan), validasi startup, pemeriksaan operasi per fase (`kontrak_operasi`, termasuk `nilai_selaras` dan `pelacak.catat`), serta pemeriksaan argumen batas (`angka`, `teks_wajib`, `hanya_kunci`) yang melempar `ValueError` bernama argumen. | `verifikasi_startup`, `kontrak_operasi`, `ContractViolationError`, `angka`, `teks_wajib`, `hanya_kunci` |
| [`pycos/refleksi/ketidaktahuan.py`](pycos/refleksi/ketidaktahuan.py) | View reflektif murni tentang batas pengetahuan dan sikap ketidaktahuan dari data yang sudah ada. | `batas_pengetahuan`, `sikap_ketidaktahuan` |
| [`pycos/dukungan/sumber.py`](pycos/dukungan/sumber.py) | Resolusi berkas data paket: path absolut leksikon dan korpus contoh, serta daftar kandidat pencarian, sehingga aplikasi host tidak menyusun string path sendiri. | `jalur_leksikon`, `jalur_korpus`, `kandidat_leksikon`, `ada_sumber_daya` |
| [`pycos/sumber_daya/leksikon_pycos.json`](pycos/sumber_daya/leksikon_pycos.json) | Sumber daya leksikal terstruktur untuk `pycos.bahasa.tutur`: entri, bahasa dan kelas gramatikal, tipe semantik, kerangka predikat, serta data morfologi. Metadata menyatakan 4.229 entri: 3.824 bahasa Indonesia dan 405 bahasa Inggris. | Dimuat oleh `TuturEngine` / `Presentasi` |
| [`pycos/sumber_daya/korpus_contoh.jsonl`](pycos/sumber_daya/korpus_contoh.jsonl) | Korpus contoh berlabel untuk kalibrasi keselarasan (`--kalibrasi`): teks, polaritas, formalitas, dan label keselarasan. Dilabeli penulis, bukan penilai manusia — hanya indikatif. | Dimuat oleh `muat_korpus` / `laporan_kalibrasi` |
| [`tests/`](tests) | 20 berkas tes `unittest` (508 tes): struktur paket dan gaya impor, resolusi sumber daya, integrasi lintas lapisan, perilaku kognitif terpilih, kontrak lingkungan uji, kontrak ketidaktahuan, regresi perbaikan analisis, keselarasan ujaran (`test_selaras`, `test_selaras_lanjutan`), serta SST (`test_sst`) — orkestra seluruh fitur dalam satu NPC. | `python -m unittest discover` |
| [`LICENSE`](LICENSE) | Teks lisensi MIT. | — |

Paket didefinisikan oleh `pyproject.toml` (setuptools) dan hanya memerlukan
standard library Python; leksikon JSON dan korpus contoh JSONL dibundel sebagai
`package-data`, sehingga
runtime tidak memerlukan NumPy, Gymnasium, NetworkX, layanan model, atau web
server. Cara pemakaian:

```sh
pip install -e .                  # dari akar repositori, lalu impor dari mana saja
PYTHONPATH=/path/ke/Pycos python  # tanpa instalasi: tambahkan checkout ke sys.path
python -m pycos                   # cetak peta subpaket + status leksikon
python -m pycos.inti.naluri       # demo mandiri per modul (dari akar repo)
python3 pycos/inti/naluri.py      # demo yang sama, dari direktori mana pun
```

Eksekusi berkas langsung tetap didukung oleh shim `if not __package__` di kepala
`naluri.py`, `nurani.py`, `jejak_prediksi.py`, dan `lingkungan/dunia.py`, yang
menambahkan direktori induk paket ke `sys.path`. Lima modul ber-blok `__main__`
(naluri, nurani, jejak_prediksi, organik, lingkungan/dunia) menjalankan demo
atau uji-dirinya sendiri; `pycos/mandiri/kognisi_lanjut.py` dan
`pycos/bahasa/tutur.py` tidak mengimpor modul Pycos lain, jadi dapat diimpor
atau disalin sendirian.

## Gambaran model

### Drive dan putaran inti (`pycos.inti.naluri`)

`Naluri` memelihara enam level drive bernama `energi`, `keamanan`,
`keingintahuan`, `penguasaan`, `afiliasi`, dan `koherensi`. Rentang nominal
model adalah `[-1, 1]`; tanda digunakan untuk merepresentasikan defisit versus
surplus, dan transisi state normal membatasi nilainya ke rentang tersebut.
`initial_levels` harus berupa nilai numerik berhingga di dalam rentang itu;
konstruktor menolak nilai non-finite maupun nilai di luar `[-1, 1]`. Pemanggil
dapat memajukan model melalui
`tick(events=..., action_cost=...)`, memeriksa state dan tujuan, menilai
kandidat aksi, lalu melaporkan outcome. Tick, event, parameter, dan state
berupa data Python eksplisit, bukan layanan tersembunyi.

`Naluri` juga memuat subsistem opsional untuk afek diskret, kebijakan
tidur/mimpi, kalibrasi, atensi/workspace dan narasi diri, dialog serta
presentasi nonverbal, relasi sosial, reputasi, dan kawanan NPC. Sebagiannya
dikendalikan oleh metode atau parameter `enable_*`. Preset dapat mengaktifkan
fitur atau mengubah parameternya; karena itu “mati secara bawaan” berlaku bagi
konfigurasi default tertentu, bukan selalu untuk setiap preset. Periksa state
dan konfigurasi aktif saat menyusun simulasi.

### Refleksi dan adaptasi (`pycos.refleksi.nurani`)

`Nurani` adalah pendamping stateful, bukan pengganti `Naluri`. Mekanisme yang
diimplementasikan mencakup:

- pencatatan pengalaman afektif dan penyimpanan prior leksikal;
- laporan kalibrasi Brier/per-drive, pelacakan ketidakpastian, dan pemeriksaan
  hold-out sebelum perubahan skala;
- setpoint adaptif dan matriks interosepsi terpelajar;
- state kejutan struktural/persepsi, termasuk derau, ambang, adaptasi,
  habituasi, dan pembaruan sensitivitas;
- konflik tujuan, kompromi, ritme sirkadian, dan state flow;
- relasi sosial, kepercayaan, utang, prior sosial, dan pengamatan terhadap
  keyakinan agen lain;
- state opsional untuk rasa yang dilaporkan, tutur batin, emosi moral,
  penanda somatik, monitoring realitas, keraguan, narasi identitas, dan
  konfabulasi.

Flag fitur berada dalam kamus parameter. Nilai bawaan didefinisikan di
`NURANI_DEFAULTS`; `Naluri.enable_nurani()` mengendalikan pilar utama NURANI
bila integrasinya tersedia. Rumus dan ambang implementasi adalah keputusan
desain, bukan pengukuran psikologi seseorang.

### Memori episodik dan prediksi (`pycos.memori.jejak_prediksi`)

`JejakPrediksi` menyimpan episode stimulus/aksi/outcome, menormalkan nilai
outcome, mengambil episode berdasarkan cue teks dan konteks, lalu
menggabungkan memori, prior opsional `Naluri`/`Nurani`, dan bukti numerik
lingkungan yang juga opsional. Bobot nominal default konstruktor adalah 0,75
untuk memori, 0,15 untuk insting, dan 0,10 untuk lingkungan; bukti lingkungan
dibatasi sampai 0,20. Ini adalah bobot desain yang dapat dikonfigurasi, bukan
probabilitas universal atau gambaran empiris prediksi manusia.

Interaksi utamanya:

1. `record_experience(stimulus, action, outcome, context=..., tick=...)`
   mencatat hasil yang diamati.
2. `predict(stimulus, action=..., context=..., environment=..., tick=...)`
   menghasilkan forecast terstruktur, field ketidakpastian, kontribusi
   sumber, status retrieval, dan rekomendasi.
3. `rank_actions(stimulus, candidates, ...)` memberi skor pada kandidat aksi,
   dengan nilai eksplorasi/informasi opsional dan prediksi alternatif
   (“shadow”) yang disimpan.
4. `reinforce(prediction, actual_outcome, ...)` mencatat hasil aktual dan
   mengevaluasi galat prediksi serta alternatif.

Retrieval episode memakai fitur token dan indeks terbalik token untuk
membentuk kandidat; `set_retrieve_mode("coarse")` mengaktifkan mode kasar
berbasis MinHash. `performance_report()` melaporkan penghitung runtime, bukan
benchmark yang dipublikasikan. Sebagian state bersifat turunan (indeks, cache,
signature) dan dibangun ulang saat load. Retensi, eviksi, konsolidasi, serta
signature memori yang dilupakan/mati merupakan mekanisme berbeda.
Reconsolidation recall mati secara default dan hanya aktif lewat gate eksplisit
`enable_reconstructive_recall` / `enable_recall_rewrite()`.

### Primitif state organik (`pycos.mandiri.organik`)

Wadah `Organik` mengelompokkan komponen berikut, yang juga dapat digunakan
secara terpisah:

- **TopologiSlot** membedakan slot kosong/hilang dari nilai numerik nol.
- **LukaDomain** merepresentasikan domain yang dikecualikan; hasil untuk
  domain tersebut dapat berupa `None`, bukan skalar kecil.
- **BatasIdentitas** menerapkan batas identitas pada pembaruan state yang
  didukung.
- **WaktuHeterogen** menyimpan penyesuaian waktu/retensi per episode.
- **PenolakanTutur** memodelkan interupsi/penolakan tutur yang bersumber dari
  state.
- **Apersepsi** merepresentasikan state rasa yang jelas, tidak pasti, tak
  bernama, atau tidak ada.
- **LapisanParalel** mempertahankan beberapa lapisan keyakinan alih-alih
  selalu mereduksinya menjadi satu nilai.
- **TubuhSumber** memiliki dinamika state tubuh bocor dan terbatasnya sendiri.
- **Residu** menyimpan perubahan afektif pada ambang/plafon dan tambalan atau
  penimpaan eksplisit; tidak memiliki langkah peluruhan waktu.
- **Intrusi** mengambil sampel materi afektif untuk sebuah interupsi.
- **DetakInternal** memajukan peristiwa internal fraksional, terpisah dari
  batas tick global bilangan bulat.
- **Vacancy** memodelkan rentang waktu terbatas saat pemrosesan normal
  dilewati.
- **GejalaMurni**, **KategoriProto**, dan **Gejala** membentuk alur dari
  sinyal tanpa klasifikasi melalui kategori berulang/proto hingga kategori
  yang diklaim.
- **Invensi** mengusulkan, memberi skor, menerima, atau menggugurkan struktur
  baru.
- **ModelKausal** menyimpan relasi sebab/akibat dan mendukung penjelasan,
  penelusuran mekanisme, kontrafaktual, dan atribusi.
- **Perencana** memakai model kausal untuk perencanaan means/end bertahap.

Nama-nama ini menjelaskan perilaku kode. Itu bukan bukti bahwa program
memiliki pengalaman subjektif, trauma, identitas, atau sensasi tubuh.

### Mekanisme kognitif lanjutan (`pycos.mandiri.kognisi_lanjut`)

`KognisiLanjut` membundel lima mekanisme, yang juga dapat dipakai sendiri-sendiri:

- `EversiTD`: reward dari perubahan disonansi/kecemasan, TD(0) berbasis tabel,
  dan nilai parameter berbatas;
- `boltzmann_pilih` / `suhu_mental`: sampling Softmax/Boltzmann dengan
  temperatur yang dapat diatur;
- `MesinKepercayaan`: pembaruan posterior dalam bentuk log-odds menggunakan
  likelihood ratio dan bobot bukti;
- `GrafAsosiasi`: asosiasi tak berarah berbobot, koaktivasi, spreading
  activation, dan peluruhan;
- `ProsesOU`: drift stokastik terbatas di sekitar kecenderungan per-drive.

Integrasi `Naluri` bersifat opsional dan memakai hook runtime; mengaktifkan
mekanisme akan mengubah nilai dan pilihan simulasi sesuai persamaan yang
diimplementasikan.

### Dialog dan analisis ujaran (`pycos.bahasa.tutur`)

Jika diberi leksikon (`pycos/sumber_daya/leksikon_pycos.json`),
`TuturEngine` menjalankan empat tahap:
`L0` membangun proposisi dari tindak tutur dan konteks; `L1` memetakan
proposisi ke slot bertipe; `L2` menyaring/memberi skor pada pilihan leksikal;
dan `L3` menerapkan morfologi serta linearisasi. `GenContext` adalah snapshot
beku untuk satu proses generasi. Engine mengembalikan `Tutur` berisi teks,
status, tindak tutur, dan trace. Jika leksikon tidak diberikan atau tidak
terdapat pada path yang diminta, `TuturEngine.tersedia()` bernilai `False` dan
`ucap()` mengembalikan `None`.

Ini adalah sistem berbasis aturan dan leksikon berhingga, bukan LLM atau parser
umum bahasa Indonesia/Inggris. Predikat, pemetaan tindak tutur, kerangka
semantik, dan fallback sebagian ditentukan di kode; pilihan leksikal dilakukan
berdasarkan sumber daya dan konteks saat ini. `SASPAnalyzer` / fungsi `sa_sp*`
yang terpisah membedakan pendekatan literal bebas konteks dari hipotesis
pragmatik yang bergantung konteks. Keduanya bukan analisis linguistik lengkap.

### Lingkungan uji (`pycos.lingkungan.dunia`)

`Lingkungan` adalah dunia berpetak untuk menguji NPC di luar unit test rumus:
peta ASCII (`Peta.dari_ascii`), medan berbiaya atau terhalang, objek yang bisa
diambil lalu dipakai, bahaya yang memapar, cuaca dan siklus jam, serta NPC lain
yang bisa disapa atau dihampiri. Setiap `langkah()` melakukan persepsi →
penawaran kandidat aksi berformat `Naluri.choose_action` → penerapan aksi →
pengiriman peristiwa ke `npc.tick(events=..., action_cost=True)` → pencatatan
reward dan memori. Aksi yang diulang melemah (*satiasi*) sehingga NPC berotasi
alih-alih mengulang satu tindakan; perilaku ini juga terlihat pada kandidat
yang ditawarkan, jadi pilihan NPC dinilai atas efek efektif saat itu.

```python
from pycos.inti import Naluri
from pycos.lingkungan import Lingkungan

dunia = Lingkungan.dari_ascii([
    "########",
    "#..!...#",
    "#..H...#",
    "########",
], seed=3)
dunia.tambah_objek("bahaya", (3, 1), nama="api")
dunia.tambah_objek("tempat_aman", (3, 2), nama="rumah")
dunia.tambah_npc(Naluri(name="Rama", rng_seed=3,
                        initial_levels={"keamanan": -0.6}), (1, 1))
dunia.jalankan(langkah=12)
print(dunia.render(nama="Rama"))
print(dunia.statistik()["per_npc"]["Rama"]["aksi"])
```

Aplikasi host tetap pemilik kognisi NPC: `Lingkungan.to_dict()` hanya menyimpan
dunia (peta, objek, posisi, inventaris, satiasi, riwayat) dan tidak menyalin
drive, tujuan, atau memori; pulihkan NPC dengan `Naluri.from_dict` lalu
sambungkan lewat `Lingkungan.from_dict(data, npcs={...}, jejak={...})`.
Lingkungan ini adalah alat uji dan demo, bukan game loop produksi, engine
fisika, atau renderer grafis: "lingkungan nyata" berarti dunia dengan ruang,
sumber daya, bahaya, dan konsekuensi yang harus dihadapi NPC — bukan klaim
simulasi dunia fisik.

### Integrasi runtime dan penggunaan multi-NPC

`pycos.dukungan.patching` melindungi pemasangan metode lintas modul. `install_method(s)`
hanya mengisi atribut kelas yang belum terpakai, melaporkan konflik alih-alih
menimpa perilaku diam-diam, dan mendukung ID patch idempoten. `wrap_method`
merangkai wrapper di sekitar metode yang sudah ada sambil mempertahankan
implementasi yang dibungkus dan descriptor yang didukung. Impor opsional
memakai nama modul bertitik (`pycos.mandiri.organik`) dan mengembalikan
`None` bila modul tidak ada, sehingga lapisan inti tetap dapat dimuat
sendirian tanpa lapisan mandiri terpasang.

`KawananNPC` mengelola koleksi NPC bernama dan menyediakan operasi kelompok
termasuk tick, interaksi/presentasi, reputasi, pencarian spasial, pembangkitan
berdasarkan event, serta utilitas terpilih untuk pembelajaran sosial/gosip.
Metode-metode ini adalah helper simulasi; repositori tidak menyediakan game
loop produksi, renderer grafis, layanan jaringan, atau antarmuka pengguna.
`pycos.lingkungan` menambahkan loop langkah dan render ASCII khusus untuk
keperluan uji.

## Mulai cepat

Jalankan dari akar repositori (atau setelah `pip install -e .`):

```python
from pycos.inti import Naluri
from pycos.memori import JejakPrediksi

npc = Naluri(name="Ayu", rng_seed=7)
npc.tick(events=[{
    "drive": "keamanan",
    "delta": -0.2,
    "reason": "mendengar suara di lorong",
}])

jejak = JejakPrediksi(naluri=npc)
jejak.record_experience(
    "lorong berasap", "masuk",
    {
        "impact": -0.7,
        "drive_deltas": {"keamanan": -0.6},
        "label": "sesak",
    },
    context="malam", tick=1,
)
hasil = jejak.predict(
    "lorong berasap", action="masuk", context="malam", tick=2,
)
print(hasil["scope"], hasil["forecast"], hasil["memory"]["retrieval_status"])
```

Prediksi bertumpu pada contoh yang disimpan dan input model terkonfigurasi;
hasilnya bukan jaminan tentang lorong atau tindakan di dunia nyata.

Contoh minimal generasi ujaran:

```python
from pycos.bahasa import GenContext, TuturEngine
from pycos.dukungan.sumber import jalur_leksikon

engine = TuturEngine(path=jalur_leksikon())   # sumber daya yang dibundel paket
if engine.tersedia():
    utterance = engine.ucap(GenContext(
        act="menyatakan", topik="api", niat="aku melihat api", seed=2,
    ))
    print(utterance.teks if utterance else "generasi gagal")
```

`Presentasi` menyusun kandidat leksikon lewat
`pycos.dukungan.sumber.kandidat_leksikon()`: path pada parameter
`presentasi_leksikon`, berkas di samping modul, sumber daya paket, lalu
direktori kerja — karena itu `npc.presentasi.tutur_engine()` menemukan
`pycos/sumber_daya/leksikon_pycos.json` tanpa path manual.

Bila checkout hanya ditambahkan ke `PYTHONPATH` (tanpa instalasi), nama
impornya tetap `pycos.…`; alias tingkat atas lama seperti `import naluri`
atau `from Pycos.naluri import …` tidak ada lagi.

## Persistensi state

Komponen stateful yang sesuai menyediakan `to_dict()` / `from_dict()`;
`Naluri` dan `JejakPrediksi` juga menyediakan helper JSON/berkas. Contoh:

```python
state = npc.to_dict()
restored = Naluri.from_dict(state)
```

`Nurani` dapat digunakan mandiri atau ditempel ke `Naluri`. Dalam penggunaan
terintegrasi, parameternya berbagi kamus dengan `Naluri` pemilik dan disimpan
sebagai bagian dari state pemilik; serialisasi mandiri dapat menyertakan
parameter secara eksplisit. Cache turunan dan objek runtime eksternal tidak
seluruhnya diserialisasi. Saat memuat `JejakPrediksi` dengan pemilik, berikan
pemilik tersebut ke `JejakPrediksi.load(path, naluri=npc)` atau
`from_dict(..., naluri=npc)` untuk menyambungkan kembali integrasi opsional.

## Tes dan pemeliharaan

Proyek menggunakan test runner `unittest` dari standard library. Berkas tes
berada di `tests/` dan diimpor sebagai `tests.test_*`:

```sh
python -m unittest discover -v          # seluruh suite, dari akar repositori
python -m unittest tests.test_struktur_paket -v
python -m compileall -q pycos tests tools examples
python -m pycos --periksa [--json]      # pemeriksaan kesehatan; kode keluar 0/1 untuk CI
python -m pycos.dukungan.tolok [--json] [--ulang N]   # tolok kinerja ringan
python -m pycos --demo                  # skenario drift keselarasan ujaran
python -m pycos --teks "..." [--valensi V] [--gairah G] [--leksikon L.json] [--json]
python -m pycos --kalibrasi pycos/sumber_daya/korpus_contoh.jsonl [--json]
```

GitHub Actions (`.github/workflows/ci.yml`) menjalankan kompilasi, seluruh tes,
dan pemeriksaan kesehatan pada Python 3.9–3.14. Job Pyflakes 4.0.3 memeriksa
semua modul implementasi dan tes; berkas `__init__.py` dikecualikan karena
mengimpor ulang nama API publik di cabang `TYPE_CHECKING` secara sengaja.

Suite saat ini berjumlah **508 tes dalam 20 berkas tes**. Di antaranya terdapat
*Systematic-Structured Test* (SST) di `tests/test_sst.py`: satu orkestra yang
menjalankan **seluruh kelompok fitur wajib dalam manifest secara sistematis dan terstruktur sebagai
satu NPC utuh** (lahir → inti & kepribadian → kesadaran/presentasi/sosial →
dunia → bahasa → memori → nurani → primitif mandiri → ketidaktahuan/penilai →
tutup siklus), dengan tiga jaminan: (1) ledger fitur — setiap fitur wajib
harus benar-benar aktif beserta buktinya, `wajib - aktif == {}` atau tes
gagal; (2) cakupan API publik — setiap nama di `pycos.__all__` dipetakan ke
fitur yang dibuktikan aktif; (3) klasifikasi eksklusif — satu-satunya yang
boleh tidak diorkestrasi adalah titik masuk showcase (`demo_*`, `*.demo`)
yang dikunci di `LUAR_CAKUPAN_SST` dan dipantau pemindaian AST. Jalankan
`python3 tests/test_sst.py` untuk melihat laporan orkestra.

Pengaman SST menolak label fitur di luar manifest dan bukti kosong, serta
memastikan himpunan fitur aktif sama persis dengan manifest. Memori sosial
diaktifkan sebelum interaksi Sari. Direktori sementara dibersihkan saat
orkestra sukses maupun gagal; enam tes negatif/siklus hidup menguji pengaman
tersebut. Total SST: 14 tes. Pemetaan API adalah pemeriksaan keterhubungan
nama ekspor dengan kelompok fitur, **bukan bukti bahwa setiap metode, flag,
atau cabang telah dieksekusi**. Pemindaian AST mengunci daftar demo, bukan
inventaris seluruh fitur implementasi.

Selain tes struktur, suite
mencakup `test_perbaikan_analisis.py`: validasi batas masuk (NaN, kunci asing,
rentang), determinisme seed, batas memori `losses`, pemakaian ulang mimpi tertunda,
recency yang dapat direproduksi, integrasi demo JEJAK/NURANI, patching atomik,
cache leksikon, dan fitur `--periksa`/tolok. Suite mencakup struktur paket (susunan berkas, `__init__.py`, gaya impor),
resolusi sumber daya leksikon, integrasi lintas lapisan (memori, serialisasi,
state organik, kognisi), perilaku kognitif terpilih dari `test_struktur_kognitif.py`
dan `test_organik_lanjutan.py`, serta kontrak lingkungan uji di
`test_lingkungan.py` (peta, gerak, objek, bahaya, cuaca, satiasi, interaksi,
serialisasi). Lihat [`VALIDATION.md`](VALIDATION.md)
untuk pemetaan tes terhadap klaim, perintah yang dijalankan, serta klaim yang
hanya didukung struktur kode atau belum terbukti. Blok demo mandiri di beberapa
modul bersifat ilustratif dan bukan pengganti tes.

## Penomoran konsep dalam source

Komentar dan docstring memakai label bernomor seperti “konsep 4” atau
“konsep 17”. Penomoran itu mengikuti daftar konsep kognitif desain proyek
(lihat komentar di `pycos/inti/naluri.py`: “angkanya di Ringkasan konsep 17 di
folder analysis”) yang **tidak ikut disertakan** dalam repositori ini. Agar
pembaca source tidak kehilangan konteks, berikut pemetaan angka yang benar-
benar dipakai di kode saat ini:

| Angka | Rujukan di source |
| --- | --- |
| 1 | workspace global / konten sadar (`Kesadaran.workspace`, `isi_kesadaran`) |
| 2 | kesadaran terasa / felt quality (pilar H NURANI, bersama 5–6) |
| 3 | diri autobiografis & perjalanan waktu mental (JEJAK `autobiographical_timeline`) |
| 4 | kesadaran temporal & sense-of-agency (`state_origin`, dialog yang dipicu keadaan) |
| 5 | kesalahan terkendali & sensasi tubuh (`felt`, konfabulasi) |
| 6 | monitoring realitas & keraguan metakognitif (`confabulate`, `metacognitive_doubt`) |
| 7 | presentasi terintegrasi & atensi (PRESENTASI, ignition, attentional blink) |
| 8 | reputasi sosial (KawananNPC, `commit`/`forgive`/`betray`) |
| 10 | keyakinan (`hold_belief`) |
| 13 | mimpi buruk (`paksa_mimpi_buruk`) |
| 17 | NURANI: lapisan meta-plastisitas di atas Naluri (`pycos.refleksi.nurani`) |

Angka yang tidak muncul di tabel tidak dipakai oleh source pada checkout ini.

## Batasan dan interpretasi

- Repositori ini bukan model machine learning terlatih, sistem percakapan
  serbaguna, atau model kognitif/neurosains yang terverifikasi.
- Istilah seperti “memori”, “emosi”, “kesadaran”, “trauma”, atau “kehendak
  bebas” merujuk pada data dan transisi eksplisit yang diimplementasikan; istilah
  itu tidak menyiratkan pengalaman subjektif atau kesetaraan biologis.
- Prediksi dan inferensi sosial menggunakan fitur, persamaan, ambang, alias,
  dan/atau contoh tersimpan yang ditulis tangan. Skor yang tampak yakin belum
  tentu benar.
- `pycos.bahasa.tutur` bergantung pada leksikon JSON berhingga yang dapat
  diedit dan
  aturan dalam kode; cakupan, keidiomatisan, dan ketepatan semantik dibatasi
  sumber daya tersebut.
- Penilai keselarasan ujaran (di `pycos.refleksi.nurani`) memakai leksikon
  kecil, negasi berjendela tiga token dalam
  satu klausa, dan morfologi sederhana. Ia tidak mendeteksi sarkasme atau ironi,
  dan ambang skornya belum dikalibrasi terhadap penilaian manusia. `--kalibrasi`
  mengukur akurasi terhadap korpus berlabel yang diberikan pengguna; korpus
  contoh di repositori dilabeli oleh penulis, bukan oleh penilai independen.
- Tes unit mencakup skenario bernama, bukan setiap metode, kombinasi flag,
  bahasa, sistem operasi, atau kasus numerik. Checkout ini tidak menyertakan
  benchmark performa yang membuktikan percepatan untuk skala produksi.
- Source memuat beberapa rujukan historis ke berkas dan paket yang tidak ada
  pada checkout ini. Statusnya dijelaskan di `VALIDATION.md`, bukan dianggap
  sebagai dependensi yang tersedia.

## Audit seluruh source Python

[Audit ulang lengkap](docs/AUDIT_PYTHON_LANJUTAN.md) adalah snapshot historis
**39 berkas Python**, termasuk generator audit itu sendiri. Analisis per berkas dan
empat langkah implementasi berurutan melengkapi [audit historis](docs/AUDIT_PYTHON.md).
[Lampiran AST](docs/AUDIT_PYTHON_RINCI.md) mencantumkan hash, seluruh callable
termasuk nested/demo, lokasi handler, impor, dan indikator kontrol/mutasi.

```bash
python3 tools/audit_python.py          # perbarui indeks setelah source berubah
python3 tools/audit_python.py --check  # gagal bila indeks tertinggal
```

CI memeriksa indeks pada Python 3.11 agar render `ast.unparse` konsisten.
Indeks saat ini mencakup **82 berkas Python**, termasuk tes/contoh/tool;
venv, build, vendor dan direktori non-source dikecualikan. Audit AST bukan
bukti eksekusi semua cabang. Suite saat ini: **508 tes**.
Format graf `graf_asosiasi/2` menyimpan konfigurasi dan pasangan node tanpa
collision nama; loader tetap menerima save lama. Aktivasi graf merambat
hingga jumlah hop yang diminta, sekali per node per pemanggilan. State RNG
bundel KognisiLanjut dan konteks transisi TD Naluri kini dipersistensi; ini
**bukan** klaim exact resume semua RNG dalam NPC.


## Implementasi rekomendasi pengembangan

| Tahap | Implementasi dan rujukan |
| --- | --- |
| [R0](docs/IMPLEMENTASI_REKOMENDASI.md) | Validasi state, versi/migrasi eksplisit, save atomik ber-checksum, tautan NPC dan filter audit. |
| [R1](docs/IMPLEMENTASI_REKOMENDASI_FASE1.md) | Validasi event/parameter, kontrak nama, diagnostik dan health check. |
| [R2](docs/IMPLEMENTASI_REKOMENDASI_FASE2.md) | Profil persistence penuh/simpan/minimal; [retrieval terbatas](docs/IMPLEMENTASI_REKOMENDASI_FASE2_RETRIEVAL.md), [kawanan lazy](docs/IMPLEMENTASI_REKOMENDASI_FASE2_KAWANAN.md), [batas memori](docs/IMPLEMENTASI_REKOMENDASI_FASE2_BATAS_MEMORI.md). Target save ≤8 KB masih terbuka. |
| R3 | [Variasi Tutur](docs/IMPLEMENTASI_REKOMENDASI_FASE3_TUTUR.md), [leksikon impak](docs/IMPLEMENTASI_REKOMENDASI_FASE3_LEKSIKON.md), dan [evaluasi terpisah](docs/IMPLEMENTASI_REKOMENDASI_FASE3_EVALUASI.md). API evaluasi tersedia, bukan bukti evaluasi manusia independen. |
| R4 | [Pemecahan inti](docs/IMPLEMENTASI_REKOMENDASI_FASE4_STRUKTUR.md), [inventaris runtime patch](docs/IMPLEMENTASI_REKOMENDASI_FASE4_PATCH.md), [konstanta/numerik](docs/IMPLEMENTASI_REKOMENDASI_FASE4_KONSTANTA.md). Jalur impor lama dipertahankan. |
| [R5.1](docs/IMPLEMENTASI_REKOMENDASI_FASE5_GATE.md) | `py.typed`, typing bertahap, coverage ≥80% **per berkas target**, gate tick <2 ms dan predict 2.000/256 <5 ms. Kini strict **18 berkas** termasuk konektor; kontrak, Nurani dan Tutur sudah masuk coverage gate. |
| [R5.2](examples/README.md) | Empat contoh stdlib runnable dan lima tes integrasi subprocess. |
| [R5.3](docs/IMPLEMENTASI_REKOMENDASI_FASE5_CHANGELOG.md) | [Changelog](CHANGELOG.md), [kontribusi](CONTRIBUTING.md), gate PR catatan kompatibilitas save untuk perubahan AST `from_dict`. |
| [R5.4](docs/API_PUBLIK.md) | 64 alias publik baru, total 125 ekspor root, identitas objek dan impor malas tetap terjaga. Dua pengecualian nama dijelaskan eksplisit. |
| [R5.5](docs/KONEKTOR_HOST.md) | Adapter snapshot host, CLI JSON, contoh Godot dan inspector HTML lokal. |
| R5.6 | Adapter LLM opsional dengan guardrail: **belum diimplementasikan**. |

### Contoh runnable dan API publik

```sh
python -m examples.npc_dunia
python -m examples.dialog_hud
python -m examples.simpan_migrasi
python -m examples.kawanan_lod
```

Primitif `EversiTD`, `Perencana`, `ModelKausal`, dan `GrafAsosiasi` tersedia
melalui `from pycos import ...` dengan objek yang sama seperti subpaketnya.
`import pycos` dan `dir(pycos)` tetap malas; star import memuat semua ekspor.

### Adapter host

`pycos.konektor.observasi(snapshot, dunia)` mengembalikan events;
`aksi(snapshot, kandidat)` memilih pada clone tanpa memutasi input host.
Host tetap bertanggung jawab atas tick, penerapan aksi, reward, dan persistence.
Pilihan dan HUD pada CLI memakai snapshot awal, sebelum events diterapkan.

```sh
printf '%s' '{"seed":7,"dunia":{"ringkas":"api terlihat"},"kandidat":[{"name":"amati","drive_effects":{"keingintahuan":0.1}}]}' | python -m pycos.konektor --json
```

[Contoh Godot](examples/godot/pycos_host.gd) memakai subprocess tanpa shell,
namun belum diuji di engine. [Inspector HTML](examples/inspector.html) membaca
HUD/response JSON lokal tanpa jaringan; smoke test memakai DOM tiruan, bukan
browser visual. Lihat [batas integrasi lengkap](docs/KONEKTOR_HOST.md).

### Pemeriksaan pengembangan tambahan

```sh
python -m pip install -e '.[dev]'
python -m mypy
python -m coverage run --source=pycos,tools -m unittest discover -q
python -m coverage json -o coverage.json
python tools/periksa_gate.py --coverage coverage.json
python -m pycos.dukungan.tolok --json > tolok.json
python tools/periksa_gate.py --tolok tolok.json
python tools/periksa_changelog.py --base <commit-base-PR>
node tools/periksa_inspector.cjs  # opsional, Node stdlib; bukan dependensi runtime
```

Jangan mengukur benchmark di bawah tracing coverage. Laporan measurement tidak
perlu di-commit. Ikuti [CONTRIBUTING.md](CONTRIBUTING.md) untuk perintah lint,
audit, dan aturan kompatibilitas save. Riwayat hasil tiap tahap tersimpan di
[VALIDATION.md](VALIDATION.md), terpisah dari ringkasan terkini.
