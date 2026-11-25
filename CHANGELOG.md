# Changelog

Perubahan penting dicatat mengikuti [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Bagian **Unreleased** berisi pekerjaan yang belum dirilis, bukan janji tanggal rilis.
Versi paket saat ini `0.1.0`; belum ada riwayat rilis terverifikasi di dokumen ini.

## [Unreleased]

### Added

- Validasi state tersimpan dan registry migrasi eksplisit, pemeriksaan kontrak,
  diagnostik, serta pemeriksaan kesehatan paket.
- `py.typed`, mypy strict bertahap, gate coverage per berkas dan gate performa CI.
- Empat contoh runnable dengan tes integrasi subprocess: NPC+dunia,
  dialog bergaya+HUD, save/load+migrasi, dan kawanan 100 NPC dengan LOD.
- Panduan kontribusi dan gate changelog untuk perubahan implementasi `from_dict`.
- R5.4: 64 alias publik malas dari subpaket ke root `pycos`, termasuk
  `EversiTD`, `Perencana`, `ModelKausal`, dan `GrafAsosiasi`. API lama tetap
  tersedia; `demo` dan fungsi `dukungan.sumber_daya` tetap di jalur subpaket
  agar entry point showcase dan nama modul data tidak bertabrakan.
- Kebijakan ekspor pada `docs/API_PUBLIK.md` serta tes klasifikasi seluruh
  nama subpaket, identitas alias, star import, cache, dan impor malas.
- J2 ANALISIS_LINGUISTIK: tes sifat generator (`tests/test_sifat_generator.py`)
  untuk semua act × register × seed; G1 kini mengenali predikat berafiks
  (meN-/di-/ter-/ku-/ber-) dan verba dasar tanpa afiks, serta tidak menuntut
  predikat pada kalimat interogatif — sehingga keluaran sah tidak lagi
  dituduh fragmen.
- H7/H9 ANALISIS_LINGUISTIK: `eskalasi_variasi` tingkat pertama meminta
  kandidat baru dari mesin tutur dengan larangan bentuk yang baru dipakai
  (`cara: kandidat_baru_mesin_tutur`), isi asal tetap dipertahankan, dan
  pengakuan repetisi ditandai `langkah_terakhir`; `batas_identitas` dinilai
  proporsional terhadap `kedekatan_identitas` (bukan pinalti −0,80 tetap).
- H6/H8 ANALISIS_LINGUISTIK: `pycos/bahasa/teks.py` menyediakan `jejak_bentuk`
  dan `kata_isi` (jejak makna: bentuk boleh berubah, pikiran asal tetap
  dirujuk); `Presentasi.ucap` menyertakan `jejak_makna`/`pikiran_asal`, dan
  gaya peran yang menghapus isi ditolak sebelum dipilih.
- H8: modul `pycos/bahasa/keadaan.py` membangkitkan ujaran keadaan (act
  `kegagalan`, `penahanan`, `apersepsi`, `ujian_tutur`) lewat mesin tutur;
  `_PELINDUNG_WATAK`, buffer manusiawi, balasan ujian, penahanan sadar, dan
  `pidato_gagal` memakai jalur ini dengan tabel lama sebagai cadangan.
- F4–F7 ANALISIS_LINGUISTIK: skor leksikal kontekstual (sinonim fokus,
  kolokasi, antonim dua arah, kata favorit persona, penalti riwayat 0,80^langkah),
  slot `mode="isi"` yang boleh diisi tanpa argumen, variasi struktur (inversi,
  elipsis subjek), partikel wacana berpemisahan register, sapaan idiolek pada
  act `kembali`/`menyapa_proaktif`, serta `TuturEngine.to_dict()`/`muat_dict()`
  untuk riwayat lema (maks 32, disinkronkan ke orkestrator).

- R5.5: adapter snapshot `pycos.konektor.observasi`/`aksi`, CLI JSON satu
  request, contoh Node Godot dan HTML HUD inspector lokal. Tidak mengubah
  schema save atau lifecycle NPC host.

### Changed

- Implementasi mesin, state, ekstensi, dan demo inti dipisahkan dari fasad
  `naluri`; runtime patch dicatat secara eksplisit.
- Konstanta drive dan utilitas numerik bersama dipusatkan pada lapisan dukungan.
- Validasi loader menolak format asing, domain angka/counter tidak sah,
  serta referensi snapshot kompak yang tidak konsisten, bukan memperbaikinya diam-diam.
- Kompatibilitas save: `pycos/inti/mesin.py` — Naluri memakai `naluri/4`;
  `naluri/3` dimigrasikan dengan jam subjektif awal dari `tick_count`.
  Snapshot legacy tanpa format tetap melalui validasi; format tidak dikenal ditolak.
  Profil `naluri/4-simpan` dan `naluri/4-minimal` diperluas sebelum pemulihan.
- Kompatibilitas save: `pycos/dukungan/validasi_state.py` — registry juga mengenali
  kawanan/5, nurani/2, jejak/2, kesadaran/1, presentasi/1, ritual/1,
  reputasi/2 dan graf_asosiasi/2. Ini bukan janji migrasi semua versi terdahulu.
  Save berkas tetap divalidasi checksum; perubahan ini tidak menghapus pemeriksaan itu.

- Kompatibilitas save: `pycos/inti/naluri.py` — implementasi loader dipindah
  ke mesin/state; fasad Naluri dan format save tetap tersedia melalui API yang sama.
- Kompatibilitas save: `pycos/inti/keadaan.py` — loader state diekstrak tanpa
  mengganti skema; validasi dan migrasi tetap dijalankan oleh lapisan pemilik.
- Kompatibilitas save: `pycos/inti/persona.py` — `from_dict` mengenali lima
  bidang idiolek baru (kata_favorit, panjang_kalimat, partikel, sapaan,
  keterusterangan). Snapshot lama tanpa bidang ini tetap dimuat dengan nilai
  bawaan (netral/daftar kosong). Tidak ada bidang lama yang dihapus; snapshot
  dapat dimuat lalu disimpan ulang tanpa kehilangan data.

### Fixed

- Jalur frasa adjektiva Tutur dengan kerangka default `None` tidak lagi crash.
- Penolakan input dan postcondition kontrak diperkuat dengan tes regresi negatif.
