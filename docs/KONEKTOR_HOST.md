# Adapter host resmi (R5.5)

`pycos.konektor` menyediakan `observasi(npc, dunia)` → list events dan
`aksi(npc, kandidat)` → dict JSON. Tidak ada dependensi runtime tambahan.
Adapter menggunakan **snapshot JSON** agar input host tidak berubah; bukan
instance `Naluri` atau `Lingkungan` hidup. Snapshot dapat diperoleh dengan
`npc.to_dict()` profil penuh. Profil simpan/minimal tetap tunduk pada validasi
loader. Nama fungsi tidak dipromosikan ke root, agar `observasi`/`aksi` tidak
menjadi nama global ambigu; akses melalui modul eksplisit `pycos.konektor`.

```python
from pycos.inti.naluri import Naluri
from pycos.konektor import observasi, aksi

npc = Naluri(name="Rama", rng_seed=7)
state = npc.to_dict()
events = observasi(state, {"ringkas": "api terlihat", "events": [
    {"drive": "keamanan", "delta": -0.1, "reason": "ancaman"}
]})
choice = aksi(state, [
    {"name": "istirahat", "drive_effects": {"energi": 0.2}, "cost": 0.01},
    {"name": "amati", "drive_effects": {"keingintahuan": 0.1}}
])
assert choice["action"] in ("istirahat", "amati")
# Host menentukan kapan events diterapkan dan aksi benar-benar dieksekusi.
npc.tick(events=events)
```

## Kontrak dan kemurnian

- `observasi`: dunia berupa dict dengan hanya `ringkas` (string) dan `events`
  (list dict). Ringkasan nonkosong menjadi event stimulus sumber host. Event
  divalidasi dengan tick pada clone dengan strict events, bukan pada NPC host.
- `aksi`: kandidat mengikuti `choose_action`: `name`, `drive_effects`, `prob`
  0..1, `cost` non-negatif; hanya drive dikenal dan angka hingga, bukan bool.
  Mesin produksi memilih pada clone dengan `record_eligibility=False`.
  Kandidat kosong menghasilkan `action: null`, bukan exception.
- Keduanya tidak mengubah snapshot, kandidat, dunia, atau NPC hidup dan tidak
  melakukan I/O. Hasil tidak berbagi list/dict dengan input. Istilah murni
  di sini adalah transformasi snapshot terisolasi; mekanisme internal loader
  dan diagnostik produksi tetap berlaku, bukan jaminan bebas semua efek global.
- Pilihan memakai snapshot **sebelum events**. Jika ingin persepsi memengaruhi
  keputusan, host menerapkan events terlebih dahulu dan mengambil snapshot baru.
- Adapter tidak memajukan jam dunia, menerapkan aksi, memberi reward, atau
  merekam eligibility pada host. Simpan/muat snapshot bukan pengganti siklus
  dunia `langkah_semua()`. Host tetap pemilik lifecycle.
- Cloning memprioritaskan isolasi, bukan throughput real-time. Untuk 100 NPC
  per frame gunakan objek hidup di proses Python, bukan spawn CLI berulang.

## CLI JSON

```sh
printf '%s' '{"seed":7,"dunia":{"ringkas":"api terlihat"},"kandidat":[{"name":"amati","drive_effects":{"keingintahuan":0.1}}]}' | python -m pycos.konektor --json
python -m pycos.konektor --json --input request.json > response.json
```

Satu request per proses; tanpa state implisit antarpanggilan. Key request yang
sah: `npc` (snapshot opsional), `seed` (integer, default 7), `dunia`, `kandidat`.
Jika npc tidak diberikan/null, dibuat HostNPC baru. Seed hanya dipakai saat
pembuatan; snapshot yang diberikan memakai state yang disimpan.
Respons sukses: `{ok:true, events:[...], pilihan:{...}, hud:{...}}`.
HUD adalah `hud_state()` snapshot awal, bukan simulasi hasil aksi.
Galat input: `{ok:false,error:"..."}`, exit 2; sukses exit 0. Argumen CLI tidak
sah mengikuti argparse (stderr/exit 2). Batas request satu juta karakter;
JSON non-finite dan objek non-JSON ditolak. Ini bukan sandbox kode atau API
internet: hanya gunakan file lokal yang dipercaya, batasi request di host.

## Godot 4.x

Pasang [script Node](../examples/godot/pycos_host.gd), install Pycos pada
interpreter yang dipilih, dan isi `python_executable` dengan path absolut.
Script menulis JSON temporer di user:// lalu memanggil Python dengan array
argumen `OS.execute`, **tanpa shell**. File dihapus setelah subprocess selesai;
file dapat tertinggal jika engine dihentikan paksa. Demo stateless memilih aksi
dan mencetak HUD. Jangan spawn per frame: OS.execute memblokir; gunakan worker
atau proses berumur panjang pada integrasi produksi. Godot Web export tidak
mendukung subprocess lokal. Godot tidak tersedia pada lingkungan validasi ini;
script belum dieksekusi dalam engine. Protokol CLI-nya diuji via subprocess.

## HTML HUD inspector

Buka [examples/inspector.html](../examples/inspector.html) langsung di browser.
Pilih JSON `hud_state()` atau `response.json` CLI, atau tempel JSON dan tekan
Tampilkan HUD. Halaman menampilkan tag/nama, ringkasan, bar drive, dan detail.
Tidak ada fetch, CDN, server, atau pengiriman data; file dibaca lokal. Nilai
teks memakai textContent, bukan innerHTML. Bar divalidasi angka 0..1 dan
payload dibatasi 1 MB untuk file (satu juta karakter untuk teks).
Inspector hanya membaca; tidak dapat menerapkan aksi atau memodifikasi state.

Smoke test tambahan tanpa paket npm: `node tools/periksa_inspector.cjs`.
Ini memakai DOM tiruan untuk logika render/validasi dan payload seperti HTML,
bukan bukti layout visual atau perilaku file picker pada browser nyata.
