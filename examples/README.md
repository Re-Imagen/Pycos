# Contoh runnable (R5.2)

Dari root checkout, dengan Python ≥3.9, tanpa dependensi runtime tambahan:

```sh
python -m examples.npc_dunia
python -m examples.dialog_hud
python -m examples.simpan_migrasi
python -m examples.kawanan_lod
python -m unittest tests.test_examples -v
```

Gunakan bentuk `-m` agar paket checkout ditemukan tanpa modifikasi `sys.path`.
Setiap contoh mencetak satu objek JSON ke stdout dan memakai seed tetap.

- `npc_dunia.py`: satu Rama, dunia ASCII, empat langkah; ≤40 baris.
  `langkah_semua()` memajukan jam dunia sekaligus NPC.
- `dialog_hud.py`: register formal versus akrab melalui `GenContext` dan
  leksikon bawaan; tag/indikator HUD berasal dari NPC yang sama. Register
  diatur eksplisit untuk demonstrasi, bukan hasil inferensi mood NPC.
- `simpan_migrasi.py`: save/load penuh dengan validasi checksum, lalu migrasi
  snapshot `naluri/3` ke `naluri/4` di memori. Berkas save tidak dimanipulasi;
  direktori temporer dibersihkan otomatis, termasuk jika terjadi exception.
- `kawanan_lod.py`: 100 NPC, masing-masing 20 pada penuh/ringan/latar/abstrak/
  beku berdasarkan jarak. Tick objektif tetap maju pada semua mode; LOD
  membatasi kerja internal. Ini demonstrasi API, bukan klaim benchmark.

Tes subprocess memeriksa exit code, JSON, aksi/posisi/tick dunia, perbedaan
register dan tag HUD, kesetaraan save/load, migrasi, distribusi LOD, serta
reproduksibilitas hasil. Contoh merupakan sumber checkout, bukan paket wheel.

## Integrasi host (R5.5)

- `godot/pycos_host.gd`: Node Godot 4.x memanggil CLI `pycos.konektor --json`
  dengan request berkas, tanpa shell. Interpreter harus memasang Pycos.
- `inspector.html`: buka langsung di browser untuk membaca JSON `hud_state()`
  atau respons CLI. Tanpa jaringan; tidak membutuhkan server.

Lihat [protokol, kontrak snapshot dan batas integrasi](../docs/KONEKTOR_HOST.md).
