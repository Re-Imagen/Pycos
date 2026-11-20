# -*- coding: utf-8 -*-
"""pycos/lingkungan/dunia.py — lingkungan uji interaksi NPC (stdlib saja).

Modul ini menyediakan *environment* kecil yang deterministik untuk menguji
NPC Pycos di dalam ruang yang menyerupai dunia nyata: peta berpetak dengan
medan yang bisa/tidak bisa dilewati, objek yang bisa diambil dan dipakai,
bahaya yang memapar, cuaca, siklus jam, serta NPC lain yang bisa disapa.

Pembagian tanggung jawab dijaga ketat:

* **Lingkungan memiliki dunia** — peta, objek, badan NPC (posisi, inventaris,
  riwayat), jam, cuaca, dan antrean peristiwa.
* **NPC memiliki kognisinya sendiri** — `pycos.inti.naluri.Naluri` tetap
  pemilik drive, tujuan, afek, dan serialisasinya. Lingkungan hanya memanggil
  API yang *duck-typed*: `choose_action(candidates)`, `tick(events=...,
  action_cost=...)`, `reward_for(deltas)`, `levels`, `name`.
* **Memori opsional per NPC** — bila sebuah `JejakPrediksi` ditautkan ke badan
  NPC, lingkungan memakai `predict` sebelum aksi dan `record_experience` /
  `reinforce` sesudahnya, sehingga pengalaman dunia nyata ikut terhitung.

Alur satu langkah (`Lingkungan.langkah`):

    observasi (persepsi)  →  kandidat aksi  →  pilihan NPC  →  efek diterapkan
        →  peristiwa drive/emosi  →  npc.tick(events=..., action_cost=True)
        →  reward & catatan memori  →  baris riwayat

Contoh pemakaian:

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
    dunia.tambah_npc(Naluri(name="Rama", rng_seed=3), (1, 1))
    for _ in range(24):
        dunia.langkah_semua()
    print(dunia.render(), dunia.statistik())

Semua keluaran berupa data Python eksplisit (dict/list) dan `random.Random`
ber-seed, sehingga hasilnya dapat diulang. Ini lingkungan *simulasi*: "nyata"
di sini berarti dunia yang punya ruang, sumber daya, bahaya, dan konsekuensi
yang harus dihadapi NPC — bukan klaim bahwa NPC berinteraksi dengan dunia
fisik sungguhan, punya persepsi biologis, atau bahwa perilakunya realistis.

Modul ini tidak mengimpor modul Pycos lain pada tingkat atas, jadi dapat
dipakai sendiri: `python -m pycos.lingkungan.dunia` atau
`python3 pycos/lingkungan/dunia.py` menjalankan demo di dalamnya.
"""

from __future__ import annotations

if not __package__:  # berkas dieksekusi langsung, bukan sebagai modul paket
    # `python3 pycos/lingkungan/dunia.py` di dalam checkout: kenalkan direktori
    # induk paket ke sys.path supaya impor `pycos.*` tetap resolve tanpa
    # instalasi maupun PYTHONPATH manual.
    import os as _os
    import sys as _sys

    _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.dirname(
        _os.path.abspath(__file__)))))
    del _os, _sys

import copy
import inspect
import math
import random
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

__all__ = [
    "ARAH",
    "Badan",
    "EFEK_JENIS",
    "LEGENDA_MEDAN",
    "Lingkungan",
    "ObjekDunia",
    "Peta",
    "JENIS_DAPAT_DIAMBIL",
    "SIMBOL_OBJEK",
    "demo",
    "peta_contoh",
]

# ---------------------------------------------------------------------------
# Konstanta dunia
# ---------------------------------------------------------------------------
Posisi = Tuple[int, int]

#: Delapan arah kompas -> pergeseran (dx, dy) pada petak.
ARAH: Dict[str, Posisi] = {
    "utara": (0, -1),
    "timur laut": (1, -1),
    "timur": (1, 0),
    "tenggara": (1, 1),
    "selatan": (0, 1),
    "barat daya": (-1, 1),
    "barat": (-1, 0),
    "barat laut": (-1, -1),
}

#: Simbol peta -> jenis medan. Simbol yang tidak dikenal dianggap tanah.
LEGENDA_MEDAN: Dict[str, str] = {
    "#": "dinding",
    ".": "tanah",
    ",": "rumput",
    ":": "jalan",
    "~": "air",
    "^": "batu",
}

#: Biaya energi relatif untuk menginjak medan; `None` = tidak bisa dilewati.
BIAYA_MEDAN: Dict[str, Optional[float]] = {
    "dinding": None,
    "air": None,
    "batu": None,
    "tanah": 1.0,
    "rumput": 1.15,
    "jalan": 0.70,
}

#: Simbol rendering untuk jenis objek.
SIMBOL_OBJEK: Dict[str, str] = {
    "makanan": "m",
    "air": "w",
    "obat": "o",
    "bahaya": "!",
    "tempat_aman": "H",
    "benda": "b",
    "penanda": "p",
}

#: Efek memakai objek per jenis: delta drive + emosi opsional.
EFEK_JENIS: Dict[str, Dict[str, Any]] = {
    "makanan": {"delta": {"energi": 0.30, "koherensi": 0.03},
                "sekali_pakai": True, "pesan": "memakan makanan"},
    "air": {"delta": {"energi": 0.14},
            "sekali_pakai": True, "pesan": "meminum air"},
    "obat": {"delta": {"koherensi": 0.16, "energi": 0.05},
             "sekali_pakai": True, "pesan": "memakai obat"},
    "bahaya": {"delta": {"keamanan": -0.40, "keingintahuan": 0.05},
               "emosi": {"takut": 0.60},
               "pesan": "menyentuh bahaya"},
    "tempat_aman": {"delta": {"keamanan": 0.32, "koherensi": 0.08},
                    "pesan": "berlindung di tempat aman"},
    "benda": {"delta": {"keingintahuan": 0.12, "penguasaan": 0.03},
              "pesan": "memeriksa benda"},
    "penanda": {"delta": {"keingintahuan": 0.08},
                "pesan": "membaca penanda"},
}

#: Jenis objek yang boleh masuk inventaris (sisanya hanya bisa dipakai).
JENIS_DAPAT_DIAMBIL = ("makanan", "air", "obat", "benda")

#: Satiasi aksi: aksi yang baru dipakai melemah (kali pengali ini), sedangkan
#: aksi lain pulih perlahan tiap langkah — sehingga NPC berotasi aksi alih-alih
#: mengulang satu aksi yang sama tanpa batas.
PENGURANGAN_ULANG = 0.35
PEMULIHAN_ULANG = 0.10
PLAFON_ULANG = 0.02

#: Aksi yang tidak mengalami satiasi (biaya/pergerakan sudah mengikatnya).
AKSI_TANPA_SATIASI = ("bergerak", "tunggu")

#: Rentang pengaruh bahaya (dalam petak) dan intensitas paparan maksimum.
RADIUS_BAHAYA = 2
PAPARAN_MAKS = 0.18

FASE_JAM: Tuple[Tuple[float, str], ...] = (
    (5.0, "malam"), (10.0, "pagi"), (15.0, "siang"),
    (19.0, "senja"), (24.0, "malam"),
)
CUACA_SAH = ("cerah", "berawan", "kabut", "hujan")


def _jarak(a: Posisi, b: Posisi) -> float:
    """Jarak Chebyshev: 1 berarti bersebelahan (termasuk diagonal)."""
    return float(max(abs(int(a[0]) - int(b[0])), abs(int(a[1]) - int(b[1]))))


def _arah_relatif(dari: Posisi, ke: Posisi) -> str:
    """Nama arah kompas dari `dari` menuju `ke` ("" bila sama)."""
    dx = int(ke[0]) - int(dari[0])
    dy = int(ke[1]) - int(dari[1])
    if dx == 0 and dy == 0:
        return ""
    potong = {(0, -1): "utara", (1, -1): "timur laut", (1, 0): "timur",
              (1, 1): "tenggara", (0, 1): "selatan", (-1, 1): "barat daya",
              (-1, 0): "barat", (-1, -1): "barat laut"}
    if (dx, dy) in potong:
        return potong[(dx, dy)]
    # bukan tetangga langsung: sebut sumbu dominan
    if abs(dx) >= abs(dy):
        return "timur" if dx > 0 else "barat"
    return "selatan" if dy > 0 else "utara"


def _menerima_action_cost(fungsi: Any) -> bool:
    """True bila `fungsi` punya parameter `action_cost` (atau **kwargs)."""
    try:
        params = inspect.signature(fungsi).parameters
    except (TypeError, ValueError):
        return False
    return "action_cost" in params or any(
        p.kind is inspect.Parameter.VAR_KEYWORD for p in params.values())


def _potong(nilai: float, bawah: float, atas: float) -> float:
    # NaN dijadikan 0 dulu: max/min akan meneruskan NaN sebagai `atas`.
    # Salinan aturan `pycos.dukungan.numerik.jepit` yang sengaja lokal agar
    # modul dunia tetap bisa disalin/dipakai sendirian (lihat tes struktur).
    try:
        nilai = 0.0 if isinstance(nilai, bool) else float(nilai)
    except (TypeError, ValueError, OverflowError):
        nilai = 0.0
    if math.isnan(nilai):
        nilai = 0.0
    return max(bawah, min(atas, nilai))


# ---------------------------------------------------------------------------
# Peta
# ---------------------------------------------------------------------------
class Peta:
    """Peta berpetak: medan per petak, biaya jalan, dan batas dunia.

    `medan` adalah daftar baris (list of list karakter) berukuran seragam.
    Gunakan :meth:`dari_ascii` untuk menulis peta sebagai baris teks.
    """

    def __init__(self, medan: Sequence[Sequence[str]], nama: str = "peta"):
        # Baris boleh berupa string ("###") maupun list karakter; jangan
        # mengubah list menjadi repr-nya sendiri (bug halus saat from_dict).
        baris = [list(r) if isinstance(r, (str, list, tuple)) else list(str(r))
                 for r in medan]
        if not baris or not baris[0]:
            raise ValueError("peta kosong: minimal satu baris satu kolom")
        lebar = len(baris[0])
        for i, r in enumerate(baris):
            if len(r) != lebar:
                raise ValueError(
                    "baris {} berisi {} petak, seharusnya {}".format(
                        i, len(r), lebar))
        self.medan: List[List[str]] = baris
        self.lebar: int = lebar
        self.tinggi: int = len(baris)
        self.nama: str = str(nama)

    # ---------- konstruktor ----------
    @classmethod
    def dari_ascii(cls, baris: Iterable[str],
                   nama: str = "peta") -> "Peta":
        """Bangun peta dari baris teks; baris kosong diabaikan."""
        bersih = [b.rstrip("\n") for b in baris if str(b).strip()]
        if not bersih:
            raise ValueError("tidak ada baris peta yang bisa dipakai")
        return cls(bersih, nama=nama)

    # ---------- kueri ----------
    def didalam(self, posisi: Any) -> bool:
        try:
            x, y = int(posisi[0]), int(posisi[1])
        except (TypeError, ValueError, IndexError, KeyError):
            return False
        return 0 <= x < self.lebar and 0 <= y < self.tinggi

    def simbol(self, posisi: Posisi) -> str:
        x, y = int(posisi[0]), int(posisi[1])
        return self.medan[y][x]

    def jenis(self, posisi: Posisi) -> str:
        return LEGENDA_MEDAN.get(self.simbol(posisi), "tanah")

    def bisa_dilewati(self, posisi: Any) -> bool:
        if not self.didalam(posisi):
            return False
        return BIAYA_MEDAN.get(self.jenis((int(posisi[0]), int(posisi[1])))
                               ) is not None

    def biaya(self, posisi: Any) -> float:
        if not self.didalam(posisi):
            return float("inf")
        nilai = BIAYA_MEDAN.get(
            self.jenis((int(posisi[0]), int(posisi[1]))), 1.0)
        return 1.0 if nilai is None else float(nilai)

    def petak(self) -> List[Posisi]:
        """Semua posisi peta, urut baris demi baris (deterministik)."""
        return [(x, y) for y in range(self.tinggi) for x in range(self.lebar)]

    def petak_bisa_dilewati(self) -> List[Posisi]:
        return [p for p in self.petak() if self.bisa_dilewati(p)]

    # ---------- serialisasi ----------
    def to_dict(self) -> Dict[str, Any]:
        return {"nama": self.nama, "lebar": self.lebar, "tinggi": self.tinggi,
                "medan": ["".join(r) for r in self.medan]}

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "Peta":
        return cls([r for r in (data.get("medan") or [])],
                   nama=str(data.get("nama", "peta")))

    def __repr__(self) -> str:  # pragma: no cover - bantuan debug
        return "Peta({}x{}, nama={!r})".format(self.lebar, self.tinggi,
                                               self.nama)


# ---------------------------------------------------------------------------
# Objek dunia
# ---------------------------------------------------------------------------
class ObjekDunia:
    """Satu objek di dalam dunia: sumber daya, bahaya, atau penanda.

    `tersembunyi=True` membuat objek tidak muncul di persepsi sampai aksi
    `amati` mengungkapnya — berguna untuk menguji perhatian dan eksplorasi.
    """

    def __init__(self, nama: str, jenis: str, posisi: Posisi,
                 atribut: Optional[Mapping[str, Any]] = None):
        self.nama = str(nama)
        self.jenis = str(jenis)
        self.posisi: Posisi = (int(posisi[0]), int(posisi[1]))
        self.atribut: Dict[str, Any] = dict(atribut or {})
        self.tersembunyi: bool = bool(self.atribut.get("tersembunyi", False))
        self.aktif: bool = True
        self.terpakai: int = 0

    def efek(self) -> Dict[str, Any]:
        """Efek standar jenis objek, atau efek kustom dari `atribut`."""
        bawaan = EFEK_JENIS.get(self.jenis, {"delta": {}, "pesan": self.jenis})
        efek = {"delta": dict(bawaan.get("delta", {})),
                "pesan": str(self.atribut.get("pesan", bawaan.get("pesan", ""))),
                "sekali_pakai": bool(self.atribut.get(
                    "sekali_pakai", bawaan.get("sekali_pakai", False)))}
        if bawaan.get("emosi"):
            efek["emosi"] = dict(bawaan["emosi"])
        for drive, nilai in (self.atribut.get("delta") or {}).items():
            efek["delta"][str(drive)] = float(nilai)
        return efek

    def to_dict(self) -> Dict[str, Any]:
        return {"nama": self.nama, "jenis": self.jenis,
                "posisi": list(self.posisi), "aktif": self.aktif,
                "terpakai": self.terpakai, "tersembunyi": self.tersembunyi,
                "atribut": copy.deepcopy(self.atribut)}

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "ObjekDunia":
        obj = cls(str(data["nama"]), str(data["jenis"]),
                  tuple(data.get("posisi", (0, 0))),
                  data.get("atribut") or {})
        obj.aktif = bool(data.get("aktif", True))
        obj.terpakai = int(data.get("terpakai", 0))
        obj.tersembunyi = bool(data.get("tersembunyi", obj.tersembunyi))
        return obj

    def __repr__(self) -> str:  # pragma: no cover - bantuan debug
        return "ObjekDunia({!r}, {!r}, {})".format(self.nama, self.jenis,
                                                   self.posisi)


# ---------------------------------------------------------------------------
# Badan NPC di dalam dunia
# ---------------------------------------------------------------------------
class Badan:
    """Kehadiran fisik satu NPC: posisi, inventaris, dan catatan interaksi.

    Kognisi tetap di objek `npc` milik pemanggil (biasanya `Naluri`). Badan
    hanya menyimpan state dunia, sehingga serialisasi lingkungan tidak pernah
    menyalin state kognitif.
    """

    def __init__(self, nama: str, npc: Any, posisi: Posisi,
                 jejak: Any = None):
        self.nama = str(nama)
        self.npc = npc
        self.jejak = jejak
        self.posisi: Posisi = (int(posisi[0]), int(posisi[1]))
        self.inventaris: List[str] = []
        self.dikunjungi: List[Posisi] = [self.posisi]
        self.berlindung: float = 0.0
        self.langkah: int = 0
        self.jarak_tempuh: int = 0
        self.terpapar: int = 0
        self.reward: float = 0.0
        self.aksi_terakhir: Optional[str] = None
        # satiasi aksi: pengali efek per nama aksi yang baru dipakai
        self.satiasi: Dict[str, float] = {}
        self.log: List[Dict[str, Any]] = []

    def to_dict(self) -> Dict[str, Any]:
        return {"nama": self.nama, "posisi": list(self.posisi),
                "inventaris": list(self.inventaris),
                "dikunjungi": [list(p) for p in self.dikunjungi],
                "berlindung": float(self.berlindung),
                "langkah": int(self.langkah),
                "jarak_tempuh": int(self.jarak_tempuh),
                "terpapar": int(self.terpapar),
                "reward": round(float(self.reward), 6),
                "aksi_terakhir": self.aksi_terakhir,
                "satiasi": {k: round(float(v), 4)
                            for k, v in sorted(self.satiasi.items())},
                "log": [dict(x) for x in self.log[-64:]]}

    @classmethod
    def from_dict(cls, data: Mapping[str, Any], npc: Any = None,
                  jejak: Any = None) -> "Badan":
        b = cls(str(data["nama"]), npc, tuple(data.get("posisi", (0, 0))),
                jejak=jejak)
        b.inventaris = [str(x) for x in (data.get("inventaris") or [])]
        b.dikunjungi = [tuple(int(v) for v in p)
                        for p in (data.get("dikunjungi") or [b.posisi])]
        b.berlindung = float(data.get("berlindung", 0.0))
        b.langkah = int(data.get("langkah", 0))
        b.jarak_tempuh = int(data.get("jarak_tempuh", 0))
        b.terpapar = int(data.get("terpapar", 0))
        b.reward = float(data.get("reward", 0.0))
        b.aksi_terakhir = data.get("aksi_terakhir")
        b.satiasi = {str(k): float(v)
                     for k, v in (data.get("satiasi") or {}).items()}
        b.log = [dict(x) for x in (data.get("log") or [])]
        return b

    def __repr__(self) -> str:  # pragma: no cover - bantuan debug
        return "Badan({!r}, posisi={})".format(self.nama, self.posisi)


# ---------------------------------------------------------------------------
# Lingkungan
# ---------------------------------------------------------------------------
class Lingkungan:
    """Dunia uji: peta, objek, NPC, waktu, cuaca, dan riwayat langkah.

    Parameter penting:

    * `peta` — objek :class:`Peta`; bila `None`, dipakai :func:`peta_contoh`.
    * `seed` — benih `random.Random` untuk cuaca dan undian lain, agar
      jalannya simulasi dapat diulang.
    * `pandangan` — radius persepsi NPC dalam petak (Chebyshev); metode
      `lihat_sekitar()` merender potongan peta di sekitar badan NPC.
    * `jam_per_langkah` — berapa jam dunia maju setiap `langkah_semua()`.

    NPC boleh berupa objek apa pun yang menyediakan sebagian API `Naluri`.
    Bila `choose_action` tidak ada, lingkungan memakai kebijakan defensif
    berbasis defisit drive; bila `tick` tidak ada, NPC tidak diberi peristiwa
    (tetap dicatat di riwayat) — berguna saat menulis tes dengan stub.
    """

    def __init__(self, peta: Optional[Peta] = None, seed: int = 0,
                 pandangan: int = 4, mulai_jam: float = 8.0,
                 jam_per_langkah: float = 1.0) -> None:
        self.peta: Peta = peta if peta is not None else peta_contoh()
        self.rng = random.Random(int(seed))
        self.seed = int(seed)
        self.pandangan = max(1, int(pandangan))
        self.tick: int = 0
        self.jam: float = float(mulai_jam) % 24.0
        self.jam_per_langkah = float(jam_per_langkah)
        self.cuaca: str = "cerah"
        self.cuaca_sisa: float = float(self.rng.randint(4, 9))
        self.objek: Dict[str, ObjekDunia] = {}
        self.badan: Dict[str, Badan] = {}
        self.riwayat: List[Dict[str, Any]] = []
        self.nama = "lingkungan"
        self._antrean: Dict[str, List[Dict[str, Any]]] = {}
        self._urutan_objek: Dict[str, int] = {}

    # ---------- konstruktor alternatif ----------
    @classmethod
    def dari_ascii(cls, baris: Iterable[str], **kwargs: Any) -> "Lingkungan":
        """Bangun lingkungan dari baris peta teks (lihat :meth:`Peta.dari_ascii`)."""
        return cls(peta=Peta.dari_ascii(baris), **kwargs)

    # ---------- registrasi ----------
    def tambah_objek(self, jenis: str, posisi: Any, nama: Optional[str] = None,
                     **atribut: Any) -> ObjekDunia:
        """Tempatkan objek di peta dan kembalikan objeknya.

        `nama` unik dipakai di dalam nama aksi (`ambil:apel#1`); bila kosong,
        nama dibangkitkan dari jenis dan nomor urut.
        """
        pos = (int(posisi[0]), int(posisi[1]))
        if not self.peta.didalam(pos):
            raise ValueError("posisi {} di luar peta".format(pos))
        if nama is None:
            nomor = self._urutan_objek.get(jenis, 0) + 1
            self._urutan_objek[jenis] = nomor
            nama = "{}{}".format(jenis, nomor)
        if nama in self.objek:
            raise ValueError("objek {!r} sudah ada".format(nama))
        obj = ObjekDunia(str(nama), str(jenis), pos, atribut)
        self.objek[obj.nama] = obj
        return obj

    def tambah_npc(self, npc: Any, posisi: Any, nama: Optional[str] = None,
                   jejak: Any = None) -> Badan:
        """Daftarkan NPC (biasanya `Naluri`) sebagai badan di dalam dunia."""
        pos = (int(posisi[0]), int(posisi[1]))
        if not self.peta.didalam(pos):
            raise ValueError("posisi {} di luar peta".format(pos))
        if not self.peta.bisa_dilewati(pos):
            raise ValueError("posisi {} tidak bisa dilewati".format(pos))
        nama = str(nama or getattr(npc, "name", None) or
                   "npc{}".format(len(self.badan) + 1))
        if nama in self.badan:
            raise ValueError("NPC {!r} sudah terdaftar".format(nama))
        badan = Badan(nama, npc, pos, jejak=jejak)
        self.badan[nama] = badan
        self._antrean.setdefault(nama, [])
        return badan

    def npc(self, nama: str) -> Any:
        """Objek kognitif (mis. `Naluri`) di balik nama badan."""
        return self.badan[str(nama)].npc

    def nama_badan(self) -> List[str]:
        """Nama badan, urut alfabetis agar langkah massal deterministik."""
        return sorted(self.badan)

    # ---------- waktu dan cuaca ----------
    def fase(self) -> str:
        """Fase hari dari jam dunia: malam/pagi/siang/senja/malam."""
        for batas, nama in FASE_JAM:
            if self.jam < batas:
                return nama
        return "malam"

    def konteks(self) -> str:
        """Konteks ringkas untuk `JejakPrediksi` / catatan."""
        return "{}|{}|{}".format(self.peta.nama, self.fase(), self.cuaca)

    def _maju_cuaca(self) -> None:
        self.cuaca_sisa -= float(self.jam_per_langkah)
        if self.cuaca_sisa > 0:
            return
        pilihan = [c for c in CUACA_SAH if c != self.cuaca]
        # transisi lunak: cuaca saat ini lebih mungkin bertahan
        berikut = self.rng.choice(pilihan if pilihan else list(CUACA_SAH))
        self.cuaca = berikut
        self.cuaca_sisa = float(self.rng.randint(4, 9))

    # ---------- persepsi ----------
    def observasi(self, nama: str) -> Dict[str, Any]:
        """Persepsi NPC pada tick ini: medan, objek, NPC lain, dan ringkasan teks."""
        if str(nama) not in self.badan:
            raise ValueError("NPC tidak dikenal: {!r}".format(nama))
        badan = self.badan[str(nama)]
        objek_terlihat: List[Dict[str, Any]] = []
        for o in sorted(self.objek.values(), key=lambda x: x.nama):
            if not o.aktif or o.tersembunyi:
                continue
            j = _jarak(badan.posisi, o.posisi)
            if j > self.pandangan:
                continue
            objek_terlihat.append({
                "nama": o.nama, "jenis": o.jenis, "jarak": j,
                "arah": _arah_relatif(badan.posisi, o.posisi),
                "posisi": list(o.posisi),
                "di_petak": j == 0.0,
            })
        npc_terlihat: List[Dict[str, Any]] = []
        for lain in self.nama_badan():
            if lain == badan.nama:
                continue
            b2 = self.badan[lain]
            j = _jarak(badan.posisi, b2.posisi)
            if j > self.pandangan:
                continue
            npc_terlihat.append({
                "nama": lain, "jarak": j,
                "arah": _arah_relatif(badan.posisi, b2.posisi),
                "posisi": list(b2.posisi), "di_petak": j == 0.0,
            })
        petak_medan = [{"posisi": list(p), "jenis": self.peta.jenis(p),
                        "jarak": _jarak(badan.posisi, p)}
                       for p in self.peta.petak()
                       if _jarak(badan.posisi, p) <= 1]
        paparan = self.paparan(badan.nama)
        ringkas = self._ringkas(badan, objek_terlihat, npc_terlihat)
        return {
            "nama": badan.nama,
            "tick": self.tick,
            "jam": round(self.jam, 2),
            "fase": self.fase(),
            "cuaca": self.cuaca,
            "posisi": list(badan.posisi),
            "medan": self.peta.jenis(badan.posisi),
            "petak_sekitar": petak_medan,
            "objek": objek_terlihat,
            "npc": npc_terlihat,
            "pandangan": self.pandangan,
            "paparan": paparan,
            "berlindung": badan.berlindung,
            "inventaris": list(badan.inventaris),
            "ringkas": ringkas,
        }

    def _ringkas(self, badan: Badan, objek: Sequence[Mapping[str, Any]],
                 npc_lain: Sequence[Mapping[str, Any]]) -> str:
        """Ringkasan tekstual persepsi — dipakai juga sebagai cue memori."""
        bagian = ["aku di {} pada petak {}".format(self.peta.jenis(badan.posisi),
                                                   list(badan.posisi))]
        if objek:
            dekat = sorted(objek, key=lambda x: (x["jarak"], str(x["nama"])))[:4]
            bagian.append("terlihat " + ", ".join(
                "{} {} langkah ke {}".format(x["nama"], int(x["jarak"]),
                                             x["arah"]) if x["jarak"] else
                "{} di petakku".format(x["nama"]) for x in dekat))
        if npc_lain:
            dekat = sorted(npc_lain, key=lambda x: (x["jarak"], str(x["nama"])))[:3]
            bagian.append("ada " + ", ".join(
                "{} {} langkah ke {}".format(x["nama"], int(x["jarak"]),
                                             x["arah"]) for x in dekat))
        bagian.append("{} dan {}".format(self.fase(), self.cuaca))
        return "; ".join(bagian)

    def paparan(self, nama: str) -> List[Dict[str, Any]]:
        """Paparan bahaya aktif di sekitar NPC (jarak <= RADIUS_BAHAYA)."""
        badan = self.badan[str(nama)]
        hasil = []
        for o in sorted(self.objek.values(), key=lambda x: x.nama):
            if not o.aktif or o.jenis != "bahaya":
                continue
            j = _jarak(badan.posisi, o.posisi)
            if j <= RADIUS_BAHAYA:
                intensitas = PAPARAN_MAKS * (1.0 - j / (RADIUS_BAHAYA + 1.0))
                hasil.append({"nama": o.nama, "jarak": j,
                              "intensitas": round(intensitas, 4)})
        return hasil

    # ---------- kandidat aksi ----------
    def aksi_tersedia(self, nama: str) -> List[Dict[str, Any]]:
        """Kandidat aksi berformat `Naluri.choose_action` (name/drive_effects)."""
        badan = self.badan[str(nama)]
        kandidat: List[Dict[str, Any]] = []
        # 1) menyapa NPC yang bersebelahan
        for lain in self.nama_badan():
            if lain == badan.nama:
                continue
            if _jarak(badan.posisi, self.badan[lain].posisi) <= 1.0:
                kandidat.append({
                    "name": "sapa:{}".format(lain),
                    "target": lain,
                    "drive_effects": {"afiliasi": 0.22, "energi": -0.01},
                    "cost": 0.01,
                    "meta": {"jenis": "sosial", "sasaran": lain},
                })
        # 1b) hampiri NPC yang terlihat tetapi belum bersebelahan
        for lain in self.nama_badan():
            if lain == badan.nama:
                continue
            jarak = _jarak(badan.posisi, self.badan[lain].posisi)
            if 1.0 < jarak <= self.pandangan:
                tujuan = self._satu_langkah_ke(badan, self.badan[lain].posisi)
                if tujuan is None:
                    continue
                kandidat.append({
                    "name": "hampiri:{}".format(lain),
                    "target": lain,
                    "drive_effects": {"afiliasi": 0.10,
                                      "energi": -0.03 * self.peta.biaya(tujuan)},
                    "cost": 0.01,
                    "meta": {"jenis": "hampiri", "sasaran": lain},
                })
        # 2) objek di petak yang sama: ambil / pakai
        for o in sorted(self.objek.values(), key=lambda x: x.nama):
            if not o.aktif or o.tersembunyi:
                continue
            if _jarak(badan.posisi, o.posisi) == 0.0:
                if o.jenis in JENIS_DAPAT_DIAMBIL:
                    kandidat.append({
                        "name": "ambil:{}".format(o.nama),
                        "drive_effects": {"penguasaan": 0.03, "energi": -0.01},
                        "cost": 0.01,
                        "meta": {"jenis": "ambil", "sasaran": o.nama},
                    })
                efek = o.efek()["delta"]
                if efek:
                    kandidat.append({
                        "name": "pakai:{}".format(o.nama),
                        "drive_effects": dict(efek),
                        "cost": 0.01,
                        "meta": {"jenis": "pakai", "sasaran": o.nama},
                    })
            elif _jarak(badan.posisi, o.posisi) <= 1.0 and \
                    o.jenis in ("tempat_aman", "benda", "penanda"):
                efek = o.efek()["delta"]
                kandidat.append({
                    "name": "pakai:{}".format(o.nama),
                    "drive_effects": dict(efek),
                    "cost": 0.01,
                    "meta": {"jenis": "pakai", "sasaran": o.nama},
                })
        # 2b) dekati objek berguna yang terlihat tetapi masih jauh: NPC perlu
        # menilai "pergi ke sana" sebagai afordansi, bukan hanya aksi di petak
        # kini. Efek yang ditawarkan adalah nilai harapan (separuh efek objek)
        # dikurangi biaya jalan; efek yang benar-benar diterapkan adalah gerak.
        for o in sorted(self.objek.values(), key=lambda x: x.nama):
            if not o.aktif or o.tersembunyi or o.jenis == "bahaya":
                continue
            jarak = _jarak(badan.posisi, o.posisi)
            if jarak <= 0.0 or jarak > self.pandangan:
                continue
            tujuan = self._satu_langkah_ke(badan, o.posisi)
            if tujuan is None:
                continue
            harapan = {d: float(v) * 0.5
                       for d, v in o.efek()["delta"].items()}
            harapan["energi"] = harapan.get("energi", 0.0) - \
                0.03 * self.peta.biaya(tujuan)
            kandidat.append({
                "name": "dekati:{}".format(o.nama),
                "drive_effects": harapan,
                "cost": 0.0,
                "meta": {"jenis": "dekati", "sasaran": o.nama,
                         "tujuan": list(tujuan)},
            })
        # 2c) isi inventaris tetap bisa dipakai walau objek dunianya sudah
        # tidak aktif (mis. makanan yang sudah diambil dari petaknya)
        for nama_item in sorted(set(badan.inventaris)):
            if any(c["name"] == "pakai:{}".format(nama_item) for c in kandidat):
                continue
            o = self.objek.get(nama_item)
            efek = o.efek()["delta"] if o is not None else {}
            kandidat.append({
                "name": "pakai:{}".format(nama_item),
                "drive_effects": dict(efek),
                "cost": 0.01,
                "meta": {"jenis": "pakai", "sasaran": nama_item,
                         "dari_inventaris": True},
            })

        # 3) bahaya: menjauh
        for p in self.paparan(badan.nama):
            if p["jarak"] <= 1.0:
                kandidat.append({
                    "name": "menjauh:{}".format(p["nama"]),
                    "drive_effects": {"keamanan": 0.20, "energi": -0.03},
                    "cost": 0.02,
                    "meta": {"jenis": "hindar", "sasaran": p["nama"]},
                })
        # 4) aksi mandiri
        kandidat.append({"name": "amati", "drive_effects":
                         {"keingintahuan": 0.15, "penguasaan": 0.02,
                          "energi": -0.01}, "cost": 0.01,
                         "meta": {"jenis": "amati"}})
        kandidat.append({"name": "istirahat",
                         "drive_effects": self._efek_istirahat(badan),
                         "cost": 0.0,
                         "meta": {"jenis": "istirahat",
                                  "bernaung": self._ada_tempat_aman(badan)}})
        # 5) bergerak: tiap arah yang sah, dengan bonus eksplorasi
        for arah, (dx, dy) in ARAH.items():
            tujuan = (badan.posisi[0] + dx, badan.posisi[1] + dy)
            if not self.peta.bisa_dilewati(tujuan):
                continue
            if self._ditempati(tujuan, kecuali=badan.nama):
                continue
            biaya = self.peta.biaya(tujuan)
            efek = {"energi": -0.03 * biaya}
            if tujuan not in badan.dikunjungi:
                efek["keingintahuan"] = 0.03
                efek["penguasaan"] = 0.02
            kandidat.append({
                "name": "bergerak:{}".format(arah),
                "drive_effects": efek,
                "cost": 0.0,
                "meta": {"jenis": "gerak", "arah": arah,
                         "tujuan": list(tujuan)},
            })
        # 6) tunggu: selalu tersedia agar kandidat tidak pernah kosong
        kandidat.append({"name": "tunggu", "drive_effects": {},
                         "cost": 0.0, "meta": {"jenis": "tunggu"}})
        # 7) satiasi: kandidat ditawarkan dengan efek efektif saat ini, bukan
        # efek mentah — NPC yang sudah bosan tidak "dipaksa" memilih aksi yang
        # sudah tidak berpengaruh, dan pilihan tercatat jujur di riwayat.
        for c in kandidat:
            jenis = str(c["name"]).split(":")[0]
            skala = 1.0 if jenis in AKSI_TANPA_SATIASI else float(
                badan.satiasi.get(str(c["name"]), 1.0))
            c["drive_effects"] = {d: float(v) * skala
                                  for d, v in (c.get("drive_effects") or {}).items()}
            c["meta"] = dict(c.get("meta") or {}, satiasi=round(skala, 4))
        return kandidat

    def _ada_tempat_aman(self, badan: Badan) -> bool:
        """True bila ada objek `tempat_aman` aktif dalam satu langkah dari NPC."""
        return any(o.aktif and not o.tersembunyi and o.jenis == "tempat_aman"
                   and _jarak(badan.posisi, o.posisi) <= 1.0
                   for o in self.objek.values())

    def _efek_istirahat(self, badan: Badan) -> Dict[str, float]:
        """Istirahat lebih memulihkan bila NPC bernaung di tempat aman."""
        if self._ada_tempat_aman(badan):
            return {"energi": 0.22, "koherensi": 0.03}
        return {"energi": 0.10}

    def _ditempati(self, posisi: Posisi, kecuali: Optional[str] = None) -> bool:
        for nama, b in self.badan.items():
            if nama == kecuali:
                continue
            if b.posisi == posisi:
                return True
        return False

    # ---------- pemilihan dan penerapan aksi ----------
    def pilih_aksi(self, nama: str,
                   kandidat: Optional[Sequence[Mapping[str, Any]]] = None
                   ) -> Dict[str, Any]:
        """Minta NPC memilih aksi; jatuh ke kebijakan defensif bila perlu."""
        badan = self.badan[str(nama)]
        kandidat = list(kandidat if kandidat is not None
                        else self.aksi_tersedia(nama))
        npc = badan.npc
        hasil: Optional[Mapping[str, Any]] = None
        if callable(getattr(npc, "choose_action", None)):
            bersih = [{k: v for k, v in c.items() if k != "meta"}
                      for c in kandidat]
            try:
                hasil = npc.choose_action(bersih)
            except Exception as galat:  # kebijakan NPC gagal: pakai cadangan
                hasil = None
                badan.log.append({"tick": self.tick, "catatan":
                                  "choose_action gagal: {}".format(galat)})
        nama_aksi = None
        sumber = "lingkungan"
        if isinstance(hasil, Mapping):
            nama_aksi = hasil.get("action")
            sumber = "npc"
        if nama_aksi is None or not any(c["name"] == nama_aksi
                                        for c in kandidat):
            nama_aksi = self._pilih_defensif(badan, kandidat)
            sumber = "defensif"
        return {"aksi": str(nama_aksi), "sumber": sumber,
                "skor": (hasil or {}).get("score") if isinstance(hasil, Mapping)
                else None,
                "kandidat": [c["name"] for c in kandidat]}

    def _pilih_defensif(self, badan: Badan,
                        kandidat: Sequence[Mapping[str, Any]]) -> str:
        """Kebijakan cadangan: aksi yang paling menutup defisit drive."""
        levels = getattr(badan.npc, "levels", None) or {}
        terbaik, skor_terbaik = kandidat[0]["name"], float("-inf")
        for c in kandidat:
            efek = c.get("drive_effects") or {}
            skor = 0.0
            for d, delta in efek.items():
                level = float(levels.get(d, 0.0) or 0.0)
                bobot = max(0.0, -level) + 0.25
                skor += bobot * (float(delta) if level < 0
                                 else float(delta) * 0.2)
            if skor > skor_terbaik:
                terbaik, skor_terbaik = str(c["name"]), skor
        return terbaik

    def terapkan(self, nama: str, aksi: str) -> Dict[str, Any]:
        """Jalankan aksi pada dunia dan kembalikan efeknya (belum di-tick)."""
        badan = self.badan[str(nama)]
        jenis, _, sasaran = str(aksi).partition(":")
        if jenis == "bergerak":
            return self._aksi_bergerak(badan, sasaran)
        if jenis == "ambil":
            return self._aksi_ambil(badan, sasaran)
        if jenis == "pakai":
            return self._aksi_pakai(badan, sasaran)
        if jenis == "menjauh":
            return self._aksi_menjauh(badan, sasaran)
        if jenis == "dekati":
            return self._aksi_dekati(badan, sasaran)
        if jenis == "hampiri":
            return self._aksi_hampiri(badan, sasaran)
        if jenis == "sapa":
            return self._aksi_sapa(badan, sasaran)
        if jenis == "amati":
            return self._aksi_amati(badan)
        if jenis == "istirahat":
            efek = self._efek_istirahat(badan)
            bernaung = self._ada_tempat_aman(badan)
            return self._hasil(True, "beristirahat di tempat aman"
                               if bernaung else "beristirahat",
                               efek,
                               catatan="energi pulih" + (" (bernaung)"
                                                         if bernaung else ""))
        if jenis == "tunggu":
            return self._hasil(True, "menunggu situasi", {},
                               catatan="tidak ada yang berubah")
        return self._hasil(False, "aksi tidak dikenal: {}".format(aksi), {},
                           catatan="gagal")

    @staticmethod
    def _hasil(berhasil: bool, pesan: str, delta: Mapping[str, float],
               emosi: Optional[Mapping[str, float]] = None,
               antre: Optional[Mapping[str, Sequence[Mapping[str, Any]]]] = None,
               catatan: str = "") -> Dict[str, Any]:
        return {"berhasil": bool(berhasil), "pesan": str(pesan),
                "delta": {str(k): float(v) for k, v in (delta or {}).items()},
                "emosi": {str(k): float(v) for k, v in (emosi or {}).items()},
                "antre": {str(k): [dict(e) for e in v]
                          for k, v in (antre or {}).items()},
                "catatan": str(catatan)}

    def _aksi_bergerak(self, badan: Badan, arah: str) -> Dict[str, Any]:
        if arah not in ARAH:
            return self._hasil(False, "arah tidak dikenal: {}".format(arah),
                               {}, catatan="gagal")
        dx, dy = ARAH[arah]
        tujuan = (badan.posisi[0] + dx, badan.posisi[1] + dy)
        if not self.peta.didalam(tujuan):
            return self._hasil(False, "batas peta menghalangi ke {}".format(arah),
                               {}, catatan="terhalang batas")
        if not self.peta.bisa_dilewati(tujuan):
            return self._hasil(False, "{} di {} tidak bisa dilewati".format(
                self.peta.jenis(tujuan), arah), {}, catatan="terhalang medan")
        if self._ditempati(tujuan, kecuali=badan.nama):
            return self._hasil(False, "petak {} ditempati NPC lain".format(
                list(tujuan)), {}, catatan="terhalang badan")
        baru = tujuan not in badan.dikunjungi
        biaya = self.peta.biaya(tujuan)
        delta = {"energi": -0.03 * biaya}
        catatan = "berpindah ke {}".format(list(tujuan))
        if baru:
            delta["keingintahuan"] = 0.03
            delta["penguasaan"] = 0.02
            badan.dikunjungi.append(tujuan)
            catatan += " (petak baru)"
        badan.posisi = tujuan
        badan.jarak_tempuh += 1
        return self._hasil(True, "bergerak ke {}".format(arah), delta,
                           catatan=catatan)

    def _aksi_ambil(self, badan: Badan, sasaran: str) -> Dict[str, Any]:
        o = self.objek.get(sasaran)
        if o is None or not o.aktif:
            return self._hasil(False, "objek {} tidak ada".format(sasaran), {},
                               catatan="gagal")
        if o.tersembunyi:
            return self._hasil(False, "objek {} belum terlihat".format(sasaran),
                               {}, catatan="gagal")
        if _jarak(badan.posisi, o.posisi) != 0.0:
            return self._hasil(False, "objek {} tidak di petak ini".format(
                sasaran), {}, catatan="gagal")
        o.aktif = False
        o.terpakai += 1
        badan.inventaris.append(o.nama)
        return self._hasil(True, "mengambil {}".format(o.nama),
                           {"penguasaan": 0.03, "energi": -0.01},
                           catatan="masuk inventaris")

    def _aksi_pakai(self, badan: Badan, sasaran: str) -> Dict[str, Any]:
        o = self.objek.get(sasaran)
        if o is None:
            if sasaran in badan.inventaris:
                o = ObjekDunia(sasaran, "benda", badan.posisi)
            else:
                return self._hasil(False, "objek {} tidak ada".format(sasaran),
                                   {}, catatan="gagal")
        if not o.aktif and sasaran not in badan.inventaris:
            return self._hasil(False, "objek {} sudah tidak aktif".format(
                sasaran), {}, catatan="gagal")
        if _jarak(badan.posisi, o.posisi) > 1.0 and sasaran not in badan.inventaris:
            return self._hasil(False, "terlalu jauh untuk memakai {}".format(
                sasaran), {}, catatan="gagal")
        efek = o.efek()
        catatan = "efek {}".format(o.jenis)
        if o.jenis == "tempat_aman":
            badan.berlindung = 2.0
            catatan += " (berlindung 2 langkah)"
        if sasaran in badan.inventaris:
            badan.inventaris.remove(sasaran)
            catatan += " (dari inventaris)"
        o.terpakai += 1
        if efek.get("sekali_pakai") and sasaran not in badan.inventaris:
            o.aktif = False
            catatan += " (habis terpakai)"
        return self._hasil(True, efek["pesan"], efek.get("delta", {}),
                           emosi=efek.get("emosi"), catatan=catatan)

    def _satu_langkah_ke(self, badan: Badan, target: Posisi) -> Optional[Posisi]:
        """Petak tetangga yang paling mendekati `target`, atau None."""
        kandidat = []
        for arah, (dx, dy) in ARAH.items():
            tujuan = (badan.posisi[0] + dx, badan.posisi[1] + dy)
            if not self.peta.bisa_dilewati(tujuan):
                continue
            if self._ditempati(tujuan, kecuali=badan.nama):
                continue
            kandidat.append((_jarak(tujuan, target), arah, tujuan))
        if not kandidat:
            return None
        kandidat.sort(key=lambda x: (x[0], x[1]))
        return kandidat[0][2]

    def _pindah_ke(self, badan: Badan, tujuan: Posisi) -> Dict[str, Any]:
        """Pindahkan badan satu petak dengan biaya energi dan bonus eksplorasi."""
        baru = tujuan not in badan.dikunjungi
        biaya = self.peta.biaya(tujuan)
        delta: Dict[str, float] = {"energi": -0.03 * biaya}
        catatan = "berpindah ke {}".format(list(tujuan))
        if baru:
            delta["keingintahuan"] = 0.03
            delta["penguasaan"] = 0.02
            badan.dikunjungi.append(tujuan)
            catatan += " (petak baru)"
        badan.posisi = tujuan
        badan.jarak_tempuh += 1
        return self._hasil(True, "berpindah ke {}".format(list(tujuan)), delta,
                           catatan=catatan)

    def _aksi_dekati(self, badan: Badan, sasaran: str) -> Dict[str, Any]:
        o = self.objek.get(sasaran)
        if o is None or not o.aktif:
            return self._hasil(False, "objek {} tidak ada".format(sasaran), {},
                               catatan="gagal")
        if o.tersembunyi:
            return self._hasil(False, "objek {} belum terlihat".format(sasaran),
                               {}, catatan="gagal")
        if _jarak(badan.posisi, o.posisi) == 0.0:
            return self._hasil(True, "sudah di petak {}".format(sasaran), {},
                               catatan="sudah di petak objek")
        tujuan = self._satu_langkah_ke(badan, o.posisi)
        if tujuan is None:
            return self._hasil(False, "tidak ada jalan menuju {}".format(
                sasaran), {}, catatan="jalan buntu")
        hasil = self._pindah_ke(badan, tujuan)
        hasil["pesan"] = "mendekati {}".format(sasaran)
        hasil["catatan"] = "mendekati {}; {}".format(sasaran, hasil["catatan"])
        return hasil

    def _aksi_hampiri(self, badan: Badan, sasaran: str) -> Dict[str, Any]:
        lain = self.badan.get(sasaran)
        if lain is None:
            return self._hasil(False, "NPC {} tidak ada".format(sasaran), {},
                               catatan="gagal")
        if _jarak(badan.posisi, lain.posisi) <= 1.0:
            return self._hasil(True, "sudah dekat dengan {}".format(sasaran),
                               {}, catatan="sudah bersebelahan")
        tujuan = self._satu_langkah_ke(badan, lain.posisi)
        if tujuan is None:
            return self._hasil(False, "tidak ada jalan ke {}".format(sasaran),
                               {}, catatan="jalan buntu")
        hasil = self._pindah_ke(badan, tujuan)
        hasil["pesan"] = "menghampiri {}".format(sasaran)
        hasil["catatan"] = "menghampiri {}; {}".format(sasaran, hasil["catatan"])
        return hasil

    def _aksi_menjauh(self, badan: Badan, sasaran: str) -> Dict[str, Any]:
        o = self.objek.get(sasaran)
        if o is None or not o.aktif:
            return self._hasil(False, "bahaya {} tidak ada".format(sasaran), {},
                               catatan="gagal")
        jarak_awal = _jarak(badan.posisi, o.posisi)
        kandidat = []
        for arah, (dx, dy) in ARAH.items():
            tujuan = (badan.posisi[0] + dx, badan.posisi[1] + dy)
            if not self.peta.bisa_dilewati(tujuan):
                continue
            if self._ditempati(tujuan, kecuali=badan.nama):
                continue
            kandidat.append((_jarak(tujuan, o.posisi), arah, tujuan))
        if not kandidat:
            return self._hasil(False, "tidak ada jalan menjauh", {},
                               catatan="terkepung")
        kandidat.sort(key=lambda x: (-x[0], x[1]))
        jarak_baru, arah, tujuan = kandidat[0]
        if jarak_baru <= jarak_awal:
            return self._hasil(True, "bertahan menjauh dari {}".format(sasaran),
                               {"keamanan": 0.05}, catatan="sudah aman")
        badan.posisi = tujuan
        badan.jarak_tempuh += 1
        if tujuan not in badan.dikunjungi:
            badan.dikunjungi.append(tujuan)
        return self._hasil(True, "menjauh dari {} ke {}".format(sasaran, arah),
                           {"keamanan": 0.20, "energi": -0.03},
                           catatan="jarak {} → {}".format(
                               int(jarak_awal), int(jarak_baru)))

    def _aksi_sapa(self, badan: Badan, sasaran: str) -> Dict[str, Any]:
        lain = self.badan.get(sasaran)
        if lain is None:
            return self._hasil(False, "NPC {} tidak ada".format(sasaran), {},
                               catatan="gagal")
        if _jarak(badan.posisi, lain.posisi) > 1.0:
            return self._hasil(False, "{} terlalu jauh untuk disapa".format(
                sasaran), {}, catatan="gagal")
        catatan = "menyapa {}".format(sasaran)
        npc = badan.npc
        if callable(getattr(npc, "berinteraksi", None)):
            try:
                npc.berinteraksi(sasaran, muatan=0.35, alasan="menyapa")
                catatan += " (lewat berinteraksi)"
            except Exception as galat:
                catatan += " (berinteraksi gagal: {})".format(galat)
        if callable(getattr(npc, "kenal", None)):
            try:
                npc.kenal(sasaran)
            except Exception:  # pragma: no cover - integrasi opsional
                pass
        antre = {sasaran: [
            {"drive": "afiliasi", "delta": 0.12,
             "reason": "disapa {}".format(badan.nama)}]}
        return self._hasil(True, "menyapa {}".format(sasaran),
                           {"afiliasi": 0.22, "energi": -0.01},
                           antre=antre, catatan=catatan)

    def _aksi_amati(self, badan: Badan) -> Dict[str, Any]:
        terungkap = []
        for o in sorted(self.objek.values(), key=lambda x: x.nama):
            if not o.aktif or not o.tersembunyi:
                continue
            if _jarak(badan.posisi, o.posisi) <= self.pandangan:
                o.tersembunyi = False
                terungkap.append(o.nama)
        catatan = "mengamati sekitar"
        if terungkap:
            catatan += "; terungkap: {}".format(", ".join(terungkap))
        return self._hasil(True, "mengamati lingkungan",
                           {"keingintahuan": 0.15, "penguasaan": 0.02,
                            "energi": -0.01}, catatan=catatan)

    # ---------- peristiwa lingkungan ----------
    def peristiwa_lingkungan(self, nama: str) -> List[Dict[str, Any]]:
        """Peristiwa latar untuk satu NPC: fase, cuaca, dan paparan bahaya."""
        badan = self.badan[str(nama)]
        peristiwa: List[Dict[str, Any]] = []
        berlindung = badan.berlindung > 0.0
        fase = self.fase()
        if fase == "malam":
            delta = -0.02 if berlindung else -0.05
            peristiwa.append({"drive": "keamanan", "delta": delta,
                              "reason": "malam di luar" if not berlindung
                              else "malam saat berlindung"})
        if self.cuaca == "hujan":
            peristiwa.append({"drive": "energi", "delta": -0.03,
                              "reason": "hujan"})
        elif self.cuaca == "kabut":
            peristiwa.append({"drive": "keingintahuan", "delta": 0.02,
                              "reason": "kabut menutupi pandangan"})
        elif self.cuaca == "berawan":
            peristiwa.append({"drive": "keingintahuan", "delta": 0.01,
                              "reason": "langit berawan"})
        for p in self.paparan(nama):
            intens = float(p["intensitas"]) * (0.4 if berlindung else 1.0)
            if intens <= 0.0:
                continue
            peristiwa.append({"drive": "keamanan", "delta": -intens,
                              "reason": "terpapar {}".format(p["nama"])})
            badan.terpapar += 1
        return peristiwa

    def _antre(self, nama: str, peristiwa: Sequence[Mapping[str, Any]]) -> None:
        self._antrean.setdefault(str(nama), []).extend(
            [dict(e) for e in peristiwa])

    def _ambil_antrean(self, nama: str) -> List[Dict[str, Any]]:
        keluar = self._antrean.get(str(nama), [])
        self._antrean[str(nama)] = []
        return [dict(e) for e in keluar]

    def _ke_events(self, peristiwa: Sequence[Mapping[str, Any]],
                   delta: Mapping[str, float], emosi: Mapping[str, float],
                   alasan: str) -> List[Dict[str, Any]]:
        events = [{str(k): v for k, v in e.items()} for e in peristiwa
                  if isinstance(e, Mapping)]
        for drive, nilai in (delta or {}).items():
            if abs(float(nilai)) > 1e-9:
                events.append({"drive": str(drive), "delta": float(nilai),
                               "reason": alasan})
        for nama_emosi, intensitas in (emosi or {}).items():
            events.append({"emosi": str(nama_emosi),
                           "intensitas": float(intensitas),
                           "reason": alasan})
        return events

    # ---------- satu langkah ----------
    def langkah(self, nama: str) -> Dict[str, Any]:
        """Satu langkah untuk satu NPC pada tick dunia yang sedang berjalan.

        Urutannya: bersihkan antrean peristiwa → persepsi → kandidat → pilihan
        NPC → terapkan aksi → `tick` + reward → catat memori → riwayat.
        Jam dunia tidak maju di sini; gunakan :meth:`langkah_semua`.
        """
        if str(nama) not in self.badan:
            raise ValueError("NPC tidak dikenal: {!r}".format(nama))
        badan = self.badan[str(nama)]
        # perlindungan dari langkah sebelumnya melebur lebih dulu, sehingga
        # berlindung 2 langkah berarti dua langkah penuh sesudah aksinya
        if badan.berlindung > 0.0:
            badan.berlindung = max(0.0, badan.berlindung - 1.0)
        peristiwa = self._ambil_antrean(badan.nama)
        pengamatan = self.observasi(badan.nama)
        kandidat = self.aksi_tersedia(badan.nama)
        pilihan = self.pilih_aksi(badan.nama, kandidat)
        hasil = self.terapkan(badan.nama, pilihan["aksi"])
        for lain, peristiwa_lain in (hasil.get("antre") or {}).items():
            if lain in self.badan and lain != badan.nama:
                self._antre(lain, peristiwa_lain)
        jenis_aksi = str(pilihan["aksi"]).split(":")[0]
        kunci_aksi = str(pilihan["aksi"])
        skala = 1.0
        if jenis_aksi not in AKSI_TANPA_SATIASI:
            skala = float(badan.satiasi.get(kunci_aksi, 1.0))
        delta = {str(k): float(v) * skala
                 for k, v in hasil["delta"].items()}
        # aksi lain pulih perlahan setiap langkah, termasuk saat aksi yang
        # dipakai bebas satiasi (bergerak/tunggu)
        for kunci in list(badan.satiasi):
            if kunci == kunci_aksi:
                continue
            lama = float(badan.satiasi[kunci])
            badan.satiasi[kunci] = min(
                1.0, lama + (1.0 - lama) * PEMULIHAN_ULANG)
        if jenis_aksi not in AKSI_TANPA_SATIASI:
            badan.satiasi[kunci_aksi] = max(
                PLAFON_ULANG, skala * PENGURANGAN_ULANG)
        events = self._ke_events(peristiwa, delta, hasil["emosi"],
                                 hasil["pesan"])
        prediksi = None
        if badan.jejak is not None and callable(
                getattr(badan.jejak, "predict", None)):
            try:
                prediksi = badan.jejak.predict(
                    pengamatan["ringkas"], action=pilihan["aksi"],
                    context=self.konteks(), tick=self.tick,
                    environment={"confidence": 0.6,
                                 "impact": _potong(sum(delta.values()), -1.0, 1.0),
                                 "drive_deltas": delta})
            except Exception as galat:
                prediksi = None
                badan.log.append({"tick": self.tick,
                                  "catatan": "predict gagal: {}".format(galat)})
        npc = badan.npc
        if callable(getattr(npc, "tick", None)):
            # Pilih bentuk pemanggilan dari signature, bukan dari TypeError: TypeError
            # yang berasal dari dalam tick() dulu memicu pemanggilan kedua (ganda).
            if _menerima_action_cost(npc.tick):
                npc.tick(events=events, action_cost=True)
            else:
                npc.tick(events)
        reward = 0.0
        if callable(getattr(npc, "reward_for", None)):
            try:
                reward = float(npc.reward_for(delta))
            except Exception as galat:
                # Reward yang gagal tidak menghentikan dunia, tetapi tidak lagi senyap.
                reward = 0.0
                badan.log.append({"tick": self.tick,
                                  "catatan": "reward_for gagal: {}".format(galat)})
        outcome = {"impact": round(sum(delta.values()), 6),
                   "drive_deltas": delta, "label": hasil["pesan"],
                   "berhasil": bool(hasil["berhasil"]),
                   "posisi": list(badan.posisi)}
        if badan.jejak is not None and callable(
                getattr(badan.jejak, "record_experience", None)):
            try:
                # `reinforce` sudah menyimpan hasil nyata sekaligus menilai
                # prediksi; `record_experience` dipakai bila tak ada prediksi
                # sehingga pengalaman tidak tercatat dua kali.
                if prediksi is not None and callable(
                        getattr(badan.jejak, "reinforce", None)):
                    badan.jejak.reinforce(
                        prediksi, outcome, stimulus=pengamatan["ringkas"],
                        action=pilihan["aksi"], context=self.konteks(),
                        tick=self.tick)
                else:
                    badan.jejak.record_experience(
                        pengamatan["ringkas"], pilihan["aksi"], outcome,
                        context=self.konteks(), tick=self.tick,
                        kind="real")
            except Exception as galat:
                badan.log.append({"tick": self.tick,
                                  "catatan": "catat memori gagal: {}".format(galat)})
        badan.langkah += 1
        badan.reward += reward
        badan.aksi_terakhir = pilihan["aksi"]
        baris = {
            "tick": self.tick,
            "jam": round(self.jam, 2),
            "fase": self.fase(),
            "cuaca": self.cuaca,
            "npc": badan.nama,
            "aksi": pilihan["aksi"],
            "sumber_pilihan": pilihan["sumber"],
            "berhasil": bool(hasil["berhasil"]),
            "pesan": hasil["pesan"],
            "catatan": hasil["catatan"],
            "skala_satiasi": round(skala, 4),
            "delta": delta,
            "paparan": [p["nama"] for p in pengamatan["paparan"]],
            "posisi": list(badan.posisi),
            "reward": round(reward, 6),
            "ringkas": pengamatan["ringkas"],
        }
        if prediksi is not None:
            baris["prediksi"] = prediksi.get("forecast") if isinstance(
                prediksi, Mapping) else None
        self.riwayat.append(baris)
        if len(self.riwayat) > 2000:
            self.riwayat = self.riwayat[-2000:]
        badan.log.append({"tick": self.tick, "aksi": pilihan["aksi"],
                          "berhasil": bool(hasil["berhasil"]),
                          "reward": round(reward, 4)})
        if len(badan.log) > 64:
            badan.log = badan.log[-64:]
        return baris

    def langkah_semua(self, nama: Optional[Iterable[str]] = None
                      ) -> List[Dict[str, Any]]:
        """Majukan jam dunia satu langkah dan langkahkan semua (atau sebagian) NPC."""
        urut = [str(n) for n in nama] if nama is not None else self.nama_badan()
        for n in urut:
            if n not in self.badan:
                raise KeyError("NPC {!r} tidak terdaftar".format(n))
        self.tick += 1
        self.jam = (self.jam + self.jam_per_langkah) % 24.0
        self._maju_cuaca()
        for n in urut:
            self._antre(n, self.peristiwa_lingkungan(n))
        return [self.langkah(n) for n in urut]

    def jalankan(self, langkah: int = 24,
                 nama: Optional[Iterable[str]] = None) -> Dict[str, Any]:
        """Jalankan `langkah` kali `langkah_semua`; kembalikan riwayat + statistik."""
        hasil = []
        for _ in range(max(0, int(langkah))):
            hasil.extend(self.langkah_semua(nama=nama))
        return {"riwayat": hasil, "statistik": self.statistik()}

    # ---------- laporan ----------
    def statistik(self) -> Dict[str, Any]:
        """Ringkasan kuantitatif interaksi: per NPC dan per aksi."""
        per_npc: Dict[str, Any] = {}
        for nama in self.nama_badan():
            b = self.badan[nama]
            aksi: Dict[str, int] = {}
            for baris in self.riwayat:
                if baris["npc"] != nama:
                    continue
                kunci = str(baris["aksi"]).split(":")[0]
                aksi[kunci] = aksi.get(kunci, 0) + 1
            levels = getattr(b.npc, "levels", None)
            per_npc[nama] = {
                "posisi": list(b.posisi),
                "langkah": b.langkah,
                "jarak_tempuh": b.jarak_tempuh,
                "terpapar": b.terpapar,
                "reward": round(b.reward, 4),
                "inventaris": list(b.inventaris),
                "berlindung": b.berlindung,
                "aksi": aksi,
                "levels": ({str(k): round(float(v), 4)
                            for k, v in dict(levels).items()}
                           if isinstance(levels, Mapping) else None),
            }
        return {
            "tick": self.tick,
            "jam": round(self.jam, 2),
            "fase": self.fase(),
            "cuaca": self.cuaca,
            "peta": self.peta.nama,
            "npcs": len(self.badan),
            "objek_aktif": sum(1 for o in self.objek.values() if o.aktif),
            "langkah_riwayat": len(self.riwayat),
            "per_npc": per_npc,
        }

    # ---------- rendering ----------
    def render(self, nama: Optional[str] = None) -> str:
        """Peta ASCII: objek, NPC, dan medan. `@` menandai NPC fokus."""
        kisi = [["." for _ in range(self.peta.lebar)]
                for _ in range(self.peta.tinggi)]
        for p in self.peta.petak():
            kisi[p[1]][p[0]] = self.peta.simbol(p)
        for o in sorted(self.objek.values(), key=lambda x: x.nama):
            if not o.aktif or o.tersembunyi:
                continue
            x, y = o.posisi
            kisi[y][x] = SIMBOL_OBJEK.get(o.jenis, "*")
        for i, nama_badan in enumerate(self.nama_badan()):
            b = self.badan[nama_badan]
            x, y = b.posisi
            kisi[y][x] = "@" if nama_badan == nama else chr(65 + i % 26)
        kepala = "{} — tick {} | {} | {}".format(
            self.peta.nama, self.tick, self.fase(), self.cuaca)
        if nama:
            kepala += " | fokus: {}".format(nama)
        return "\n".join([kepala] + ["".join(r) for r in kisi])

    def lihat_sekitar(self, nama: str, radius: Optional[int] = None) -> str:
        """Potongan peta di sekitar satu NPC (persepsi visual terbatas)."""
        b = self.badan[str(nama)]
        r = int(radius if radius is not None else self.pandangan)
        potong = []
        for y in range(b.posisi[1] - r, b.posisi[1] + r + 1):
            baris = []
            for x in range(b.posisi[0] - r, b.posisi[0] + r + 1):
                if (x, y) == b.posisi:
                    baris.append("@")
                elif not self.peta.didalam((x, y)):
                    baris.append(" ")
                elif self._ditempati((x, y)):
                    baris.append("N")
                else:
                    objek = next((o for o in self.objek.values()
                                  if o.aktif and not o.tersembunyi
                                  and o.posisi == (x, y)), None)
                    baris.append(SIMBOL_OBJEK.get(objek.jenis, "*")
                                 if objek is not None else self.peta.simbol((x, y)))
            potong.append("".join(baris))
        return "\n".join(potong)

    # ---------- serialisasi ----------
    def to_dict(self) -> Dict[str, Any]:
        """State dunia (tanpa kognisi NPC — simpan `Naluri` secara terpisah)."""
        return {
            "nama": self.nama,
            "seed": self.seed,
            "tick": self.tick,
            "jam": round(self.jam, 4),
            "cuaca": self.cuaca,
            "cuaca_sisa": round(self.cuaca_sisa, 4),
            "pandangan": self.pandangan,
            "jam_per_langkah": self.jam_per_langkah,
            "peta": self.peta.to_dict(),
            "objek": {k: v.to_dict() for k, v in sorted(self.objek.items())},
            "badan": {k: v.to_dict() for k, v in sorted(self.badan.items())},
            "riwayat": [dict(x) for x in self.riwayat[-128:]],
            "antrean": {k: [dict(e) for e in v]
                        for k, v in sorted(self._antrean.items())},
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any],
                  npcs: Optional[Mapping[str, Any]] = None,
                  jejak: Optional[Mapping[str, Any]] = None) -> "Lingkungan":
        """Pulihkan dunia; sambungkan kembali NPC lewat `npcs={nama: objek}`.

        Badan tanpa NPC yang cocok tetap dibuat dengan `npc=None`, sehingga
        lingkungan dapat diperiksa tanpa memaksa memuat kognisi apa pun.
        """
        npcs = dict(npcs or {})
        jejak = dict(jejak or {})
        dunia = cls(peta=Peta.from_dict(data.get("peta") or {}),
                    seed=int(data.get("seed", 0)),
                    pandangan=int(data.get("pandangan", 4)),
                    mulai_jam=float(data.get("jam", 8.0)),
                    jam_per_langkah=float(data.get("jam_per_langkah", 1.0)))
        dunia.nama = str(data.get("nama", "lingkungan"))
        dunia.tick = int(data.get("tick", 0))
        dunia.cuaca = str(data.get("cuaca", "cerah"))
        dunia.cuaca_sisa = float(data.get("cuaca_sisa", 0.0))
        for nama, o in (data.get("objek") or {}).items():
            dunia.objek[str(o.get("nama", nama))] = ObjekDunia.from_dict(o)
        for nama, b in (data.get("badan") or {}).items():
            kunci = str(nama)
            dunia.badan[kunci] = Badan.from_dict(
                b, npc=npcs.get(kunci), jejak=jejak.get(kunci))
            dunia._antrean.setdefault(kunci, [])
        for nama, daftar in (data.get("antrean") or {}).items():
            dunia._antre(str(nama), daftar)
        dunia.riwayat = [dict(x) for x in (data.get("riwayat") or [])]
        return dunia

    def __repr__(self) -> str:  # pragma: no cover - bantuan debug
        return "Lingkungan({!r}, npc={}, objek={}, tick={})".format(
            self.peta.nama, len(self.badan), len(self.objek), self.tick)


# ---------------------------------------------------------------------------
# Peta contoh dan demo
# ---------------------------------------------------------------------------
def peta_contoh() -> Peta:
    """Peta desa kecil 12x8: rumah, air, jalan, rumput, dan batu."""
    return Peta.dari_ascii([
        "############",
        "#..,....~..#",
        "#..,...~~..#",
        "#....:.....#",
        "#..,.:::.,.#",
        "#..,.:^:.,.#",
        "#..,.....,.#",
        "############",
    ], nama="desa")


def demo(seed: int = 7, langkah: int = 24) -> Dict[str, Any]:
    """Demo dua NPC di desa: ambil makanan, berlindung, hindari bahaya, sapa.

    Mengembalikan `{"lingkungan": ..., "statistik": ..., "render": ...}`.
    Modul `pycos.inti` diimpor di sini (bukan di tingkat atas) supaya berkas
    ini tetap dapat dipakai sendirian tanpa lapisan kognitif.
    """
    from pycos.inti import Naluri

    dunia = Lingkungan(peta=peta_contoh(), seed=seed, pandangan=4)
    dunia.tambah_objek("makanan", (2, 1), nama="roti", porsi=1)
    dunia.tambah_objek("makanan", (7, 5), nama="apel", porsi=1)
    dunia.tambah_objek("air", (9, 2), nama="sumur")
    dunia.tambah_objek("bahaya", (5, 5), nama="api")
    dunia.tambah_objek("tempat_aman", (2, 2), nama="rumah")
    dunia.tambah_objek("penanda", (6, 4), nama="papan", tersembunyi=True)
    rama = Naluri(name="Rama", personality="penjaga", rng_seed=seed,
                  initial_levels={"energi": -0.6, "keingintahuan": -0.4})
    ana = Naluri(name="Ana", personality="sosiawan", rng_seed=seed + 1,
                 initial_levels={"energi": -0.5, "afiliasi": -0.5,
                                 "keingintahuan": -0.3})
    dunia.tambah_npc(rama, (1, 1), nama="Rama")
    dunia.tambah_npc(ana, (1, 2), nama="Ana")
    print("=== Demo LINGKUNGAN: NPC berinteraksi di desa ===")
    print(dunia.render())
    for i in range(max(1, int(langkah))):
        baris = dunia.langkah_semua()
        if (i + 1) % 6 == 0:
            for b in baris:
                print("  [t{:03d}] {:<5} {:<22} {} ({})".format(
                    b["tick"], b["npc"], b["aksi"], b["pesan"],
                    b["sumber_pilihan"]))
    print()
    print(dunia.render(nama="Rama"))
    print()
    print(dunia.lihat_sekitar("Rama"))
    print()
    print("Statistik:", dunia.statistik())
    return {"lingkungan": dunia, "statistik": dunia.statistik(),
            "render": dunia.render()}


if __name__ == "__main__":
    demo()
