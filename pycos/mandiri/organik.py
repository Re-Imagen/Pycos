"""pycos/mandiri/organik.py — mekanisme "state organik" Pycos (stdlib).

Usulan-usulan ini BUKAN penambahan fitur. Masing-masing mengubah SIFAT state,
bukan besarannya:

1. TopologiSlot     — kehilangan topologis. Bukan intensitas yang luruh, tapi
                      SLOT yang menjadi tidak terisi lagi. Slot kosong berbeda
                      dari bobot nol: ``intensitas()`` mengembalikan ``None``
                      (tidak berlaku), bukan ``0.0``. Cabang simulasi masa depan
                      yang menyertakan slot kosong TIDAK DAPAT DIBANGUN.
                      Perbedaan "bobot rendah" vs "tidak ada" = sedih vs berduka.

2. LukaDomain       — luka yang mengecualikan domain. Bukan penurunan skalar,
                      tapi LUBANG: "aku tidak akan lagi memercayainya soal uang,
                      apa pun yang terjadi setelah ini." Skalar bisa pulih;
                      lubang tetap lubang. ``terapkan()`` mengembalikan ``None``
                      (tidak berlaku), bukan nilai rendah.

3. BatasIdentitas   — identitas yang MEMBATASI, bukan mendeskripsi. Klaim diri
                      ("aku orang yang tidak percaya siapa pun") bukan ringkasan,
                      melainkan filter: emosi yang bertentangan DITOLAK oleh
                      state, bukan oleh if-else pemanggil.

4. WaktuHeterogen   — waktu yang tidak seragam. Half-life per-episode yang
                      DIPELAJARI: episode yang sering di-recall memanjang,
                      yang berkali-kali dikonfirmasi salah memendek
                      (reconsolidation). Ingatan berubah dari arsip → organisme.

5. PenolakanTutur   — kegagalan yang berasal dari DALAM. Bukan gagap kosmetik
                      ("s-s") dan bukan restriksi semantik (tidak ada kata).
                      "Aku tahu apa yang harus kukatakan, dan aku tidak bisa
                      mengatakannya" — kalimatnya TERBENTUK, tapi state tubuh
                      menolak mengartikulasikannya. Sebabnya BERTIPE: takut
                      memutus, malu mengalihkan, disosiasi mengacak, duka
                      memanggil yang hilang, arousal memotong, identitas
                      menolak eksplisit.

6. Apersepsi        — sistem boleh GAGAL menamai perasaannya. Pengurangan,
                      bukan penambahan: felt boleh kosong, kabut, gradien
                      tanpa arah, atau pola yang belum punya nama.
                      "Aku tidak tahu kenapa aku begini" adalah state.

7. LapisanParalel   — keyakinan yang saling meniadakan TIDAK diselesaikan.
                      Dua lapisan hidup berdampingan, keduanya memengaruhi
                      perilaku, disonansinya nol karena tak ada yang dianggap
                      perlu diselesaikan. Kognisi paralel, bukan konvergen.

8. TubuhSumber      — panah dibalik: tubuh mendahului kognisi. Tubuh punya
                      dinamika sendiri (integrator bocor) sehingga bisa
                      menggerakkan drive sebelum pikiran tahu apa yang terjadi.

9. Residu           — emosi yang terlalu kuat tidak tinggal sebagai angka.
                      Ia mengubah AMBANG dan LANGIT fungsi afektif, tak pernah
                      meluruh, dan hanya dapat ditimpa atau ditambal peristiwa.

10. Intrusi         — pikiran tanpa pemicu eksternal: sampel afektif berbobot
                      yang menembus kompetisi atensi biasa.

11. DetakInternal   — jam fraksional untuk mual, ingin bicara, dan rindu;
                      jatuh temponya tidak dikunci pada batas tick global.

12. Vacancy         — ketiadaan pemrosesan yang berdurasi. Bukan idle atau
                      diam: hanya waktu dan peluruhan dasar yang boleh lewat.

Semua kelas di sini bebas dari modul lain (tidak ada impor internal Pycos),
jadi bisa dipakai terpisah: diimpor sebagai `pycos.mandiri.organik`, atau
dijalankan lewat `python -m pycos.mandiri.organik` /
`python3 pycos/mandiri/organik.py` untuk uji-diri.
"""

from __future__ import annotations

import math
import random

# RNG cadangan bila pemanggil tidak menyerahkan `rng`. Modul ini sengaja tidak
# memakai `random` global agar seed proses tidak ikut mengubah hasilnya.
_RNG_CADANGAN = random.Random()
import re
import zlib
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

__all__ = [
    "TopologiSlot", "LukaDomain", "BatasIdentitas", "WaktuHeterogen",
    "PenolakanTutur", "Apersepsi", "LapisanParalel", "TubuhSumber",
    "Residu", "Intrusi", "DetakInternal", "Vacancy", "Organik",
    # orde nol: bahan mentah kategori baru
    "GejalaMurni", "KategoriProto", "Gejala",
    # pelita endogen: melahirkan struktur baru (hipotesis/rencana/kategori/tujuan)
    "Invensi",
    # model kausal: menjelaskan "kenapa" (rantai sebab, counterfactual, blame)
    "ModelKausal",
    # perencana multi-tingkat + meta-planning (means-end, chaining, dekomposisi)
    "Perencana",
    "PROPERTI_TERLARANG", "KALIMAT_ADA_SESUATU", "KALIMAT_TAK_BERNAMA",
    "TERISI", "KOSONG", "TAK_BERLAKU",
]

TERISI = "terisi"
KOSONG = "kosong"
TAK_BERLAKU = None  # sentinel makna: "tidak berlaku", BUKAN nol

# Taksonomi sebab penolakan tutur (tiap sebab menahan diri dengan cara berbeda).
_JENIS_PENOLAKAN = {
    "takut": "kalimat terputus di tengah",
    "malu": "menutup diri, mengalihkan",
    "disosiasi": "kalimat tidak koheren",
    "duka": "memanggil yang hilang",
    "arousal": "terlalu cepat, terpotong",
    "identitas": "penolakan eksplisit",
}


def _kclip(x: float, lo: float, hi: float) -> float:
    """Jepit ke [lo, hi]; NaN menjadi 0 lalu dijepit (bukan menjadi `hi`).

    Salinan aturan `pycos.dukungan.numerik.jepit` yang sengaja lokal agar
    modul ini tetap mandiri dan dapat disalin sendirian.
    """
    try:
        v = 0.0 if isinstance(x, bool) else float(x)
    except (TypeError, ValueError, OverflowError):
        v = 0.0
    if v != v:
        v = 0.0
    return lo if v < lo else hi if v > hi else v


def _teks(x: Any) -> str:
    return "" if x is None else str(x)


# =====================================================================
# 9. RESIDU — yang menetap adalah ATURAN, bukan bias angka
# =====================================================================
class Residu:
    """Bekas afektif yang mengubah fungsi aktivasi dan plafon.

    Sebuah entri hanya menyimpan ``(sumber, drive/emosi, magnitudo)``.  Tidak
    ada ``langkah()`` atau decay. Untuk sasaran yang sama, entri baru hanya
    aktif bila lebih kuat; entri lama tetap berada di arsip sebagai sesuatu
    yang *ditimpa*, bukan dihapus. ``tambal()`` juga mempertahankan entri asli
    dan mencatat peristiwa eksplisit yang mengurangi tekanan efektifnya.

    Peta lintas-sasaran di bawah sengaja kecil dan bersifat struktural. Duka,
    misalnya, menaikkan ambang senang dan menurunkan langit afiliasi; ia tidak
    pernah menambahkan ``+sedih`` pada state yang sedang berjalan.
    """

    _LAWAN: Dict[str, Tuple[str, ...]] = {
        "duka": ("senang", "penasaran"),
        "sedih": ("senang", "penasaran"),
        "takut": ("senang", "penguasaan"),
        "marah": ("senang", "afiliasi"),
        "malu": ("senang", "afiliasi"),
        "kehilangan": ("senang", "afiliasi"),
    }
    _LANGIT: Dict[str, Tuple[str, ...]] = {
        "duka": ("senang", "afiliasi", "terhubung", "memaafkan"),
        "sedih": ("senang", "afiliasi", "energi"),
        "takut": ("senang", "percaya", "penguasaan"),
        "marah": ("afiliasi", "memaafkan", "keamanan"),
        "malu": ("afiliasi", "terhubung", "bicara"),
        "kehilangan": ("senang", "afiliasi", "terhubung"),
    }

    def __init__(self) -> None:
        self._aktif: Dict[str, Dict[str, Any]] = {}
        self._arsip: List[Dict[str, Any]] = []
        self._tambalan: List[Dict[str, Any]] = []
        # BEKAS (orde nol): catatan bahwa sesuatu yang tak bernama PERNAH
        # terjadi. Ini bukan entri aktif — ia tidak menekan ambang/plafon,
        # tidak bisa ditambal, dan tidak luruh. Gejala murni yang memudar
        # meninggalkan bekas di sini alih-alih menjadi angka.
        self._bekas: List[Dict[str, Any]] = []
        self._berikut = 1

    @staticmethod
    def _nama(x: Any) -> str:
        return _teks(x).strip().lower()

    @staticmethod
    def _mag(x: Any) -> float:
        try:
            return _kclip(abs(float(x)), 0.0, 1.0)
        except (TypeError, ValueError):
            return 0.0

    def daftar(self, sumber: Any, drive_emosi: Any = None,
               magnitudo: float = 0.0, tick: int = 0,
               **nama_target: Any) -> Dict[str, Any]:
        """Daftarkan residu; yang lebih lemah tidak dapat menimpa yang aktif.

        ``emosi=`` atau ``drive=`` diterima sebagai alias keyword untuk
        ``drive_emosi`` agar API tetap natural di kedua domain.
        """
        if drive_emosi is None:
            drive_emosi = nama_target.get("emosi", nama_target.get("drive"))
        target = self._nama(drive_emosi)
        if not target:
            return {}
        mag = self._mag(magnitudo)
        lama = self._aktif.get(target)
        entri = {"id": self._berikut, "sumber": _teks(sumber)[:120],
                 "target": target, "magnitudo": mag, "tick": int(tick),
                 "tertambal": 0.0, "ditimpa_oleh": None}
        self._berikut += 1
        if lama is not None and float(lama.get("magnitudo", 0.0)) >= mag:
            entri["aktif"] = False
            entri["ditolak_oleh"] = int(lama.get("id", 0))
            self._arsip.append(entri)
            return dict(entri)
        if lama is not None:
            lama = dict(lama)
            lama["aktif"] = False
            lama["ditimpa_oleh"] = entri["id"]
            self._arsip.append(lama)
        entri["aktif"] = True
        self._aktif[target] = entri
        return dict(entri)

    def tekanan_target(self, target: Any) -> float:
        entri = self._aktif.get(self._nama(target))
        if entri is None:
            return 0.0
        return _kclip(float(entri.get("magnitudo", 0.0)) -
                      float(entri.get("tertambal", 0.0)), 0.0, 1.0)

    def tekanan(self) -> float:
        """Tekanan gabungan tanpa penjumlahan tak terbatas (probabilistic OR)."""
        sisa = 1.0
        for target in self._aktif:
            sisa *= 1.0 - self.tekanan_target(target)
        return _kclip(1.0 - sisa, 0.0, 1.0)

    def _pengaruh(self, sasaran: Any, jenis: str) -> float:
        nama = self._nama(sasaran)
        terbesar = 0.0
        tabel = self._LAWAN if jenis == "ambang" else self._LANGIT
        for asal in self._aktif:
            if nama == asal or nama in tabel.get(asal, ()):
                terbesar = max(terbesar, self.tekanan_target(asal))
        return terbesar

    def ambang_dimodifikasi(self, emosi: Any, nilai_dasar: float) -> float:
        """Ambang baru. Residu menaikkan gerbang; tidak menambah intensitas."""
        dasar = max(0.0, float(nilai_dasar))
        tekanan = self._pengaruh(emosi, "ambang")
        # Ada ruang hingga 1.0; magnitudo penuh tidak membuat aktivasi mustahil.
        return _kclip(dasar + (1.0 - dasar) * 0.45 * tekanan, 0.0, 1.0)

    def langit_dimodifikasi(self, emosi: Any, nilai_dasar: float) -> float:
        """Plafon baru. Residu menyempitkan rentang fungsi, bukan memberi bias."""
        dasar = max(0.0, float(nilai_dasar))
        tekanan = self._pengaruh(emosi, "langit")
        return max(0.0, dasar * (1.0 - 0.55 * tekanan))

    def tambal(self, peristiwa: Any, target: Optional[Any] = None,
               kekuatan: float = 0.25, tick: int = 0) -> Dict[str, Any]:
        """Tambal lewat peristiwa eksplisit; entri tidak pernah dihapus.

        ``peristiwa`` wajib bernama (mis. ritual, pengakuan, pertemuan). Patch
        mengurangi tekanan efektif dan tersimpan sebagai sejarah permanen.
        """
        nama_peristiwa = _teks(peristiwa).strip()
        if not nama_peristiwa:
            return {"ditambal": False, "alasan": "peristiwa eksplisit wajib"}
        sasaran = ([self._nama(target)] if target is not None
                   else list(self._aktif.keys()))
        k = self._mag(kekuatan)
        kena: List[str] = []
        for nama in sasaran:
            entri = self._aktif.get(nama)
            if entri is None:
                continue
            # Tambalan adalah proporsi magnitudo asli, bukan decay per waktu.
            sebelum = float(entri.get("tertambal", 0.0))
            maksimum = float(entri.get("magnitudo", 0.0))
            entri["tertambal"] = min(maksimum, sebelum + k * maksimum)
            kena.append(nama)
        patch = {"tick": int(tick), "peristiwa": nama_peristiwa[:120],
                 "target": kena, "kekuatan": k, "ditambal": bool(kena)}
        self._tambalan.append(patch)
        if len(self._tambalan) > 64:
            del self._tambalan[:-64]
        return dict(patch)

    # Alias eksplisit untuk integrator yang memilih verba alih-alih ``daftar``.
    mendaftarkan = daftar
    register = daftar
    patch = tambal

    def bekas(self, sumber: Any, catatan: Any = "", tick: int = 0,
              **rincian: Any) -> Dict[str, Any]:
        """Catat bekas gejala yang tak bernama — jejak, BUKAN entri aktif.

        Residu biasa mengubah aturan afektif (ambang/plafon). Bekas tidak:
        ia hanya menyimpan fakta bahwa sesuatu pernah terjadi tanpa nama.
        Karena itu ia tidak punya ``magnitudo`` yang menekan apa pun dan tidak
        bisa menimpa entri lain.
        """
        entri = {"tick": int(tick), "catatan": _teks(catatan)[:160],
                 "sumber": _teks(sumber)[:120]}
        for k, v in rincian.items():
            if k in ("signature", "intensitas_puncak", "polaritas", "ulangan",
                     "tick_lahir"):
                entri[k] = v
        self._bekas.append(entri)
        if len(self._bekas) > 64:
            del self._bekas[:-64]
        return dict(entri)

    def bekas_state(self) -> List[Dict[str, Any]]:
        return [dict(x) for x in self._bekas]

    def state(self) -> Dict[str, Any]:
        return {"aktif": {k: dict(v, tekanan=round(self.tekanan_target(k), 4))
                           for k, v in self._aktif.items()},
                "tekanan": round(self.tekanan(), 4),
                "arsip": [dict(x) for x in self._arsip[-16:]],
                "tambalan": [dict(x) for x in self._tambalan[-16:]],
                "bekas": [dict(x) for x in self._bekas[-16:]]}

    def to_dict(self) -> Dict[str, Any]:
        return {"aktif": {k: dict(v) for k, v in self._aktif.items()},
                "arsip": [dict(x) for x in self._arsip],
                "tambalan": [dict(x) for x in self._tambalan],
                "bekas": [dict(x) for x in self._bekas],
                "berikut": self._berikut}

    @classmethod
    def from_dict(cls, d: Optional[Mapping[str, Any]]) -> "Residu":
        o = cls()
        if isinstance(d, Mapping):
            o._aktif = {str(k): dict(v) for k, v in (d.get("aktif") or {}).items()
                        if isinstance(v, Mapping)}
            o._arsip = [dict(x) for x in (d.get("arsip") or [])
                        if isinstance(x, Mapping)]
            o._tambalan = [dict(x) for x in (d.get("tambalan") or [])
                           if isinstance(x, Mapping)]
            o._bekas = [dict(x) for x in (d.get("bekas") or [])
                        if isinstance(x, Mapping)]
            o._berikut = int(d.get("berikut", 1) or 1)
        return o


# =====================================================================
# 10. INTRUSI — isi kepala yang datang tanpa retrieval/query
# =====================================================================
class Intrusi:
    """Generator konten spontan dari kopling residu × arousal × memori.

    Kelas ini tidak mengetahui ``Kesadaran`` atau ``Nurani``. Pemanggil
    memberikan mapping ``_affective`` mentah; pemilihan adalah sampel berbobot,
    bukan query kemiripan dan bukan pemanggilan retrieval.
    """

    def __init__(self, periode: int = 7, gain: float = 1.15) -> None:
        self.periode = max(1, int(periode))
        self.gain = max(0.0, float(gain))
        self._terakhir_uji = -10_000
        self._log: List[Dict[str, Any]] = []

    @staticmethod
    def _acak(rng: Optional[Any]) -> float:
        try:
            return float(rng.random())
        except Exception:
            return _RNG_CADANGAN.random()

    def _pilih_slot(self, affective: Mapping[Any, Mapping[str, Any]],
                    residu: Residu, drives: Optional[Mapping[str, float]],
                    rng: Optional[Any]) -> Optional[Mapping[str, Any]]:
        calon: List[Tuple[Mapping[str, Any], float]] = []
        for slot in (affective or {}).values():
            if not isinstance(slot, Mapping) or not slot.get("sample"):
                continue
            dampak = slot.get("deltas") or {}
            coupling = 0.0
            for nama in residu._aktif:
                coupling += abs(float(dampak.get(nama, 0.0) or 0.0)) \
                            * (0.5 + residu.tekanan_target(nama))
            kesiapan = max(abs(float(v or 0.0)) for v in dampak.values()) \
                        if dampak else 0.0
            if drives:
                kesiapan += 0.15 * sum(abs(float(dampak.get(d, 0.0) or 0.0))
                                       * max(0.0, -float(drives.get(d, 0.0) or 0.0))
                                       for d in dampak)
            # n/importance membuat memori siap, tetapi bobot tidak dibuat
            # terlalu tajam: fragmen bukan selalu memori paling relevan.
            n = max(1, int(slot.get("n", 1) or 1))
            imp = abs(float(slot.get("importance", 0.0) or 0.0))
            bobot = 0.05 + 0.45 * kesiapan + 0.35 * coupling + \
                    0.10 * min(1.0, math.log1p(n) / math.log(11.0)) + 0.10 * imp
            calon.append((slot, max(1e-6, bobot)))
        if not calon:
            return None
        total = sum(w for _, w in calon)
        x = self._acak(rng) * total
        for slot, w in calon:
            x -= w
            if x <= 0.0:
                return slot
        return calon[-1][0]

    def coba(self, tick: int, residu: Residu, arousal: float,
             affective: Mapping[Any, Mapping[str, Any]],
             spotlight: Optional[Sequence[Mapping[str, Any]]] = None,
             drives: Optional[Mapping[str, float]] = None,
             rng: Optional[Any] = None, paksa: bool = False) -> Optional[Dict[str, Any]]:
        tick = int(tick)
        if not paksa and tick - self._terakhir_uji < self.periode:
            return None
        self._terakhir_uji = tick
        tekanan = residu.tekanan() if residu is not None else 0.0
        aro = _kclip(float(arousal), 0.0, 1.0)
        peluang = _kclip(tekanan * aro * self.gain, 0.0, 0.95)
        if not paksa and (peluang <= 0.0 or self._acak(rng) >= peluang):
            return None
        slot = self._pilih_slot(affective, residu, drives, rng)
        if slot is None:
            return None
        fragmen = _teks(slot.get("sample", "sesuatu"))[:100]
        fokus = ""
        if spotlight:
            fokus = _teks(spotlight[0].get("content", ""))[:80]
        jenis_roll = self._acak(rng)
        if jenis_roll < 0.50:
            jenis, konten = "fragmen_memori", fragmen
        elif jenis_roll < 0.76:
            asal = max(residu._aktif, key=residu.tekanan_target) \
                if residu._aktif else "ini"
            jenis = "pertanyaan"
            konten = "kenapa aku masih memikirkan {}?".format(
                fragmen if fragmen else asal)
        else:
            jenis = "asosiasi_aneh"
            kait = fokus or "hal yang ada di depanku"
            konten = "{} — aneh, ini mengingatkanku pada {}".format(kait, fragmen)
        entri = {"tick": tick, "content": konten[:160], "jenis": jenis,
                 "fragmen": fragmen, "peluang": round(peluang, 4),
                 "tekanan_residu": round(tekanan, 4), "arousal": round(aro, 4),
                 "datang_tanpa_sebab": True}
        self._log.append(entri)
        if len(self._log) > 64:
            del self._log[:-64]
        return dict(entri)

    def state(self) -> Dict[str, Any]:
        return {"periode": self.periode, "gain": self.gain,
                "terakhir_uji": self._terakhir_uji,
                "jumlah": len(self._log),
                "terakhir": dict(self._log[-1]) if self._log else None}

    def to_dict(self) -> Dict[str, Any]:
        return {"periode": self.periode, "gain": self.gain,
                "terakhir_uji": self._terakhir_uji,
                "log": [dict(x) for x in self._log]}

    @classmethod
    def from_dict(cls, d: Optional[Mapping[str, Any]]) -> "Intrusi":
        if not isinstance(d, Mapping):
            return cls()
        o = cls(d.get("periode", 7), d.get("gain", 1.15))
        o._terakhir_uji = int(d.get("terakhir_uji", -10_000))
        o._log = [dict(x) for x in (d.get("log") or []) if isinstance(x, Mapping)]
        return o


# =====================================================================
# 11. DETAK INTERNAL — beberapa jam fraksional, bukan tick global
# =====================================================================
class DetakInternal:
    """Akumulator jam lokal untuk ``mual``, ``ingin_bicara``, dan ``rindu``.

    ``maju(dt)`` menerima pecahan tick dan mengembalikan interupsi pada
    panggilan yang sama ketika ambang terlewati. Ambang berikut diberi jitter
    internal dan diserialisasi, sehingga snapshot drive eksternal saja tidak
    cukup untuk memprediksi kapan interupsi muncul.
    """

    PROSES: Tuple[str, ...] = ("mual", "ingin_bicara", "rindu")

    def __init__(self, rng: Optional[Any] = None) -> None:
        self._jam: Dict[str, Dict[str, float]] = {}
        self._log: List[Dict[str, Any]] = []
        for nama in self.PROSES:
            fase = 0.0
            try:
                fase = float(rng.random()) * 0.35
            except Exception:
                fase = _RNG_CADANGAN.random() * 0.35
            self._jam[nama] = {"akumulator": fase,
                               "ambang": self._ambang_baru(rng)}

    @staticmethod
    def _ambang_baru(rng: Optional[Any]) -> float:
        try:
            return 0.82 + 0.36 * float(rng.random())
        except Exception:
            return 0.82 + 0.36 * _RNG_CADANGAN.random()

    @staticmethod
    def _rate(nama: str, state: Mapping[str, Any]) -> float:
        levels = state.get("levels") or {}
        felt = state.get("felt") or {}
        emosi = state.get("emosi") or {}
        residu = max(0.0, float(state.get("tekanan_residu", 0.0) or 0.0))
        spotlight = state.get("spotlight") or []
        grief = max(0.0, float(state.get("duka", 0.0) or 0.0))
        if nama == "mual":
            return (0.018 + 0.24 * max(0.0, float(felt.get("mual", 0.0) or 0.0))
                    + 0.08 * max(0.0, -float(levels.get("koherensi", 0.0) or 0.0))
                    + 0.05 * max(0.0, float(emosi.get("takut", 0.0) or 0.0)))
        if nama == "ingin_bicara":
            return (0.025 + 0.15 * max(0.0, -float(levels.get("afiliasi", 0.0) or 0.0))
                    + 0.08 * (1.0 if spotlight else 0.0)
                    + 0.05 * max(0.0, float(emosi.get("penasaran", 0.0) or 0.0)))
        return (0.012 + 0.16 * grief + 0.12 * residu
                + 0.05 * max(0.0, float(emosi.get("sedih", 0.0) or 0.0)))

    def maju(self, dt: float, state: Mapping[str, Any],
             rng: Optional[Any] = None, fase: str = "") -> List[Dict[str, Any]]:
        dt = max(0.0, float(dt))
        keluar: List[Dict[str, Any]] = []
        if dt <= 0.0:
            return keluar
        for nama in self.PROSES:
            jam = self._jam[nama]
            rate = max(0.0, self._rate(nama, state))
            sebelum = float(jam["akumulator"])
            sesudah = sebelum + rate * dt
            ambang = float(jam["ambang"])
            if sesudah < ambang:
                jam["akumulator"] = sesudah
                continue
            fraksi = (ambang - sebelum) / max(1e-9, rate)
            jam["akumulator"] = max(0.0, sesudah - ambang)
            jam["ambang"] = self._ambang_baru(rng)
            entri = {"proses": nama, "fraksi": round(fraksi, 5),
                     "fase": _teks(fase)[:40], "rate": round(rate, 5),
                     "tanpa_keputusan": True}
            keluar.append(entri)
            self._log.append(dict(entri))
        if len(self._log) > 96:
            del self._log[:-96]
        return keluar

    def paksa(self, nama: Any, sisa: float = 0.0) -> bool:
        """Alat integrasi/uji: buat sebuah jam jatuh tempo pada checkpoint kini."""
        key = self._nama_proses(nama)
        if key not in self._jam:
            return False
        self._jam[key]["akumulator"] = self._jam[key]["ambang"] + max(0.0, float(sisa))
        return True

    @classmethod
    def _nama_proses(cls, nama: Any) -> str:
        raw = _teks(nama).strip().lower().replace(" ", "_")
        alias = {"nausea": "mual", "speak": "ingin_bicara", "talk": "ingin_bicara",
                 "longing": "rindu", "miss": "rindu"}
        return alias.get(raw, raw)

    def state(self) -> Dict[str, Any]:
        return {"jam": {k: {kk: round(vv, 6) for kk, vv in v.items()}
                         for k, v in self._jam.items()},
                "jumlah_interupsi": len(self._log),
                "terakhir": dict(self._log[-1]) if self._log else None}

    def to_dict(self) -> Dict[str, Any]:
        return {"jam": {k: dict(v) for k, v in self._jam.items()},
                "log": [dict(x) for x in self._log]}

    @classmethod
    def from_dict(cls, d: Optional[Mapping[str, Any]]) -> "DetakInternal":
        o = cls()
        if isinstance(d, Mapping):
            for nama, jam in (d.get("jam") or {}).items():
                if nama in o._jam and isinstance(jam, Mapping):
                    o._jam[nama] = {"akumulator": float(jam.get("akumulator", 0.0)),
                                    "ambang": max(1e-6, float(jam.get("ambang", 1.0)))}
            o._log = [dict(x) for x in (d.get("log") or []) if isinstance(x, Mapping)]
        return o


# =====================================================================
# 1. KEHILANGAN TOPOLOGIS — slot, bukan skalar
# =====================================================================
class TopologiSlot:
    """Entitas menempati SLOT di dalam topologi simulasi NPC.

    Perbedaan penting dari model skalar:

    * Skalar: ``intensitas(A) = 0.03`` → A masih ADA, hanya lemah.
      ``future_simulation()`` masih bisa membangun cabang yang menyertakan A.
    * Topologis: ``slot(A) = KOSONG`` → A TIDAK ADA. ``intensitas()``
      mengembalikan ``None`` (tidak berlaku), dan ``layak_cabang()`` False,
      sehingga cabang yang menyertakan A mustahil dibangun — bukan lemah,
      melainkan tidak dapat dibentuk.

    Itulah bedanya **sedih** (bobot rendah, masih tersimulasi) dan
    **berduka** (slot kosong, tidak tersimulasi).
    """

    def __init__(self) -> None:
        self._slot: Dict[str, Dict[str, Any]] = {}

    # ---------- pendaftaran ----------
    def daftar(self, ent: Any, atribut: Optional[Mapping[str, Any]] = None,
               tick: int = 0) -> Dict[str, Any]:
        """Pastikan slot ada. Tidak mengubah status bila sudah terdaftar."""
        e = _teks(ent)
        s = self._slot.get(e)
        if s is None:
            s = {"status": TERISI, "tick_isi": int(tick), "tick_kosong": None,
                 "alasan": "", "bekas": dict(atribut or {})}
            self._slot[e] = s
        elif atribut:
            s["bekas"].update(dict(atribut))
        return dict(s)

    def peek(self, ent: Any) -> Dict[str, Any]:
        """Baca tanpa membuat slot (read-only)."""
        return dict(self._slot.get(_teks(ent), {}))

    # ---------- perubahan topologi ----------
    def kosongkan(self, ent: Any, alasan: str = "", tick: int = 0) -> Dict[str, Any]:
        """Kosongkan slot: entitas hilang dari topologi. Operasi ini bukan
        peluruhan — statusnya berubah, bukan bobotnya."""
        e = _teks(ent)
        self.daftar(e, tick=tick)
        s = self._slot[e]
        if s["status"] == KOSONG:
            return dict(s)
        s["status"] = KOSONG
        s["tick_kosong"] = int(tick)
        s["alasan"] = _teks(alasan)[:120]
        return dict(s)

    def isi_ulang(self, ent: Any, tick: int = 0, alasan: str = "kembali") -> Dict[str, Any]:
        """Mengisi kembali slot yang kosong (peristiwa langka & eksplisit).
        Bukan pemulihan skalar: ini penambahan simpul baru ke topologi."""
        e = _teks(ent)
        self.daftar(e, tick=tick)
        s = self._slot[e]
        s["status"] = TERISI
        s["tick_isi"] = int(tick)
        s["alasan"] = _teks(alasan)[:120]
        s["bekas"]["pernah_kosong"] = True
        return dict(s)

    # ---------- kueri ----------
    def terisi(self, ent: Any) -> bool:
        return self._slot.get(_teks(ent), {}).get("status") == TERISI

    def kosong(self) -> List[str]:
        return [e for e, s in self._slot.items() if s.get("status") == KOSONG]

    def semua(self) -> List[str]:
        return list(self._slot.keys())

    def intensitas(self, ent: Any, skalar: float = 0.0) -> Optional[float]:
        """``None`` bila slot kosong — BUKAN 0.0.

        Inilah pembeda ontologis: nol berarti "ada tapi lemah"; None berarti
        "tidak ada". Pemanggil yang memperlakukan keduanya sama kehilangan
        perbedaan antara sedih dan berduka.
        """
        e = _teks(ent)
        if e in self._slot and not self.terisi(e):
            return TAK_BERLAKU
        return float(skalar)

    def layak_cabang(self, ent: Any) -> bool:
        """Bolehkah entitas ini muncul di cabang simulasi masa depan?"""
        return self.terisi(ent)

    def cabang_mustahil(self, teks: Any,
                        kandidat: Optional[Sequence[Any]] = None) -> List[str]:
        """Daftar entitas berslot-kosong yang disebut di dalam `teks`.

        Cabang yang menyebut mereka TIDAK DAPAT dibangun — bukan diberi bobot
        rendah, melainkan dibatalkan.
        """
        t = _teks(teks)
        if not t:
            return []
        sumber = self.kosong() if kandidat is None else [_teks(x) for x in kandidat]
        return [e for e in sumber if e and e in t]

    # ---------- serialisasi ----------
    def to_dict(self) -> Dict[str, Any]:
        return {"slot": {k: dict(v) for k, v in self._slot.items()}}

    @classmethod
    def from_dict(cls, d: Optional[Mapping[str, Any]]) -> "TopologiSlot":
        o = cls()
        if isinstance(d, Mapping):
            for k, v in (d.get("slot") or {}).items():
                if isinstance(v, Mapping):
                    o._slot[str(k)] = {
                        "status": v.get("status", TERISI),
                        "tick_isi": int(v.get("tick_isi", 0) or 0),
                        "tick_kosong": v.get("tick_kosong"),
                        "alasan": _teks(v.get("alasan", "")),
                        "bekas": dict(v.get("bekas") or {}),
                    }
        return o


# =====================================================================
# 2. LUKA YANG MENGECUALIKAN DOMAIN — lubang, bukan angka
# =====================================================================
class LukaDomain:
    """Luka kepercayaan yang bersifat MENGEcualikan domain.

    Model skalar: ``hancurkan_kepercayaan(A)`` menurunkan satu angka; angka itu
    bisa pulih lewat waktu. Model lubang: ``lukai(A, "uang")`` menandai domain
    uang sebagai TIDAK BERLAKU selamanya. ``bayar_utang()`` boleh menghapus
    daftar hutang, tetapi tidak bisa menambal lubang.

    ``terapkan()`` mengembalikan ``None`` (tidak berlaku) — bukan nilai rendah —
    sehingga pemanggil tidak dapat "memulihkan perlahan-lahan" sesuatu yang
    secara struktural sudah tidak ada.
    """

    def __init__(self) -> None:
        self._lubang: Dict[str, Dict[str, Dict[str, Any]]] = {}

    def lukai(self, ent: Any, domain: Any = "*", alasan: str = "",
              tick: int = 0, permanen: bool = True) -> Dict[str, Any]:
        e, dom = _teks(ent), _teks(domain) or "*"
        rec = {"tick": int(tick), "alasan": _teks(alasan)[:160],
               "permanen": bool(permanen)}
        self._lubang.setdefault(e, {})[dom] = rec
        return {"entitas": e, "domain": dom, **rec}

    def dikecualikan(self, ent: Any, domain: Any = "*") -> bool:
        e, dom = _teks(ent), _teks(domain) or "*"
        d = self._lubang.get(e) or {}
        return dom in d or "*" in d  # lubang menyeluruh menutup semua domain

    def domain_terluka(self, ent: Any) -> List[str]:
        return sorted((self._lubang.get(_teks(ent)) or {}).keys())

    def terapkan(self, ent: Any, domain: Any, skalar: float) -> Optional[float]:
        """``None`` bila domain adalah lubang. Skalar tidak berlaku di sana."""
        if self.dikecualikan(ent, domain):
            return TAK_BERLAKU
        return float(skalar)

    def tambal(self, ent: Any, domain: Any = "*") -> bool:
        """Hanya lubang NON-permanen yang dapat ditambal. Lubang permanen
        tetap lubang — inilah alasan skalar tidak setara dengan topologi."""
        e, dom = _teks(ent), _teks(domain) or "*"
        d = self._lubang.get(e) or {}
        rec = d.get(dom)
        if rec is None:
            return False
        if rec.get("permanen", True):
            return False
        del d[dom]
        if not d:
            self._lubang.pop(e, None)
        return True

    def ringkas(self) -> Dict[str, List[str]]:
        return {e: sorted(d.keys()) for e, d in self._lubang.items()}

    def to_dict(self) -> Dict[str, Any]:
        return {"lubang": {e: {k: dict(v) for k, v in d.items()}
                           for e, d in self._lubang.items()}}

    @classmethod
    def from_dict(cls, d: Optional[Mapping[str, Any]]) -> "LukaDomain":
        o = cls()
        if isinstance(d, Mapping):
            for e, doms in (d.get("lubang") or {}).items():
                if isinstance(doms, Mapping):
                    for k, v in doms.items():
                        if isinstance(v, Mapping):
                            o._lubang.setdefault(str(e), {})[str(k)] = {
                                "tick": int(v.get("tick", 0) or 0),
                                "alasan": _teks(v.get("alasan", "")),
                                "permanen": bool(v.get("permanen", True)),
                            }
        return o


# =====================================================================
# 3. IDENTITAS YANG MEMBATASI — filter emosi di level state
# =====================================================================
class BatasIdentitas:
    """Klaim identitas yang MEMFILTER emosi, bukan sekadar mendeskripsikan diri.

    ``narrative_identity`` lama adalah kesimpulan: NPC mengamati dirinya lalu
    menulis klaim. Di sini klaim itu menjadi PEMBATAS: emosi tertentu ditolak
    atau dibatasi langit-langitnya oleh state, tanpa pemanggil menulis if-else.

    Mode aturan:
      * ``"tolak"``                  — emosi tidak pernah boleh muncul.
      * ``"tolak_bila_bertentangan"`` — muncul hanya bila stimulus tidak
                                        bertentangan dengan identitas.
      * ``"langit"``                 — boleh muncul, tetapi dipotong pada
                                        nilai maksimum tertentu.
    """

    def __init__(self) -> None:
        self.klaim: str = ""
        self._batas: Dict[str, Dict[str, Any]] = {}
        self._ditolak: List[Dict[str, Any]] = []

    def tetapkan(self, klaim: Any, batas: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
        self.klaim = _teks(klaim)[:200]
        self._batas = {}
        for emosi, r in (batas or {}).items():
            if isinstance(r, Mapping):
                self._batas[_teks(emosi)] = {
                    "mode": _teks(r.get("mode", "tolak")),
                    "nilai": float(r.get("nilai", 0.0) or 0.0),
                    "alasan": _teks(r.get("alasan", "")) or self.klaim,
                }
            else:  # bentuk ringkas: emosi -> "tolak" | ("langit", 0.1)
                if isinstance(r, (tuple, list)) and len(r) == 2:
                    self._batas[_teks(emosi)] = {"mode": _teks(r[0]),
                                                 "nilai": float(r[1]),
                                                 "alasan": self.klaim}
                else:
                    self._batas[_teks(emosi)] = {"mode": _teks(r),
                                                 "nilai": 0.0,
                                                 "alasan": self.klaim}
        return self.state()

    def izinkan(self, emosi: Any, jumlah: float,
                bertentangan: bool = False) -> Tuple[bool, float, str]:
        """(diizinkan, jumlah_setelah_batas, alasan)."""
        r = self._batas.get(_teks(emosi))
        if r is None:
            return True, float(jumlah), ""
        mode = r.get("mode")
        if mode == "tolak":
            return False, 0.0, r.get("alasan", "ditolak identitas")
        if mode == "tolak_bila_bertentangan" and bertentangan:
            return False, 0.0, r.get("alasan", "bertentangan dengan identitas")
        if mode == "langit":
            return True, min(float(jumlah), float(r.get("nilai", 0.0))), r.get("alasan", "")
        return True, float(jumlah), ""

    def catat_penolakan(self, emosi: Any, diminta: float, alasan: str,
                        tick: int = 0) -> None:
        self._ditolak.append({"tick": int(tick), "emosi": _teks(emosi),
                              "diminta": round(float(diminta), 4),
                              "alasan": _teks(alasan)[:120], "klaim": self.klaim})
        if len(self._ditolak) > 64:
            del self._ditolak[:-64]

    def penolakan(self) -> List[Dict[str, Any]]:
        return [dict(x) for x in self._ditolak]

    def state(self) -> Dict[str, Any]:
        return {"klaim": self.klaim,
                "batas": {k: dict(v) for k, v in self._batas.items()},
                "jumlah_penolakan": len(self._ditolak),
                "penolakan_terakhir": dict(self._ditolak[-1]) if self._ditolak else None}

    def to_dict(self) -> Dict[str, Any]:
        return {"klaim": self.klaim,
                "batas": {k: dict(v) for k, v in self._batas.items()},
                "ditolak": [dict(x) for x in self._ditolak]}

    @classmethod
    def from_dict(cls, d: Optional[Mapping[str, Any]]) -> "BatasIdentitas":
        o = cls()
        if isinstance(d, Mapping):
            o.klaim = _teks(d.get("klaim", ""))
            for k, v in (d.get("batas") or {}).items():
                if isinstance(v, Mapping):
                    o._batas[str(k)] = {"mode": _teks(v.get("mode", "tolak")),
                                        "nilai": float(v.get("nilai", 0.0) or 0.0),
                                        "alasan": _teks(v.get("alasan", ""))}
            o._ditolak = [dict(x) for x in (d.get("ditolak") or [])]
        return o


# =====================================================================
# 4. WAKTU YANG TIDAK SERAGAM — half-life per-episode yang dipelajari
# =====================================================================
class WaktuHeterogen:
    """Setiap episode memiliki half-life-nya SENDIRI, dan half-life itu belajar.

    * Sering di-recall → half-life MEMANJANG (jalur ingatan diperkuat).
    * Berkali-kali dikonfirmasi salah → half-life MEMENDEK (reconsolidation:
      ingatan yang ternyata keliru ditulis ulang agar cepat pudar).

    ``half_life_ticks`` global lama menyamakan laju semua ingatan; di sini
    ingatan berubah dari arsip pasif menjadi organisme yang menyesuaikan diri.
    """

    def __init__(self, dasar: float = 600.0, min_: float = 30.0,
                 maks: float = 20000.0, laju_ingat: float = 0.35,
                 laju_salah: float = 0.30) -> None:
        self.dasar = max(1.0, float(dasar))
        self.min = max(1.0, float(min_))
        self.maks = max(self.min, float(maks))
        self.laju_ingat = float(laju_ingat)
        self.laju_salah = float(laju_salah)
        self._hl: Dict[str, float] = {}
        # Skala encoding subjektif per episode: nilai > 1 berarti momen terasa
        # memanjang dan mendapat half-life efektif lebih panjang; nilai < 1
        # menandai waktu yang melesat/episode yang terkompresi. _hl tetap
        # menyimpan half-life dasar agar recall/reconsolidation tetap terpisah.
        self._skala_subjektif: Dict[str, float] = {}
        self._durasi_subjektif: Dict[str, Dict[str, Any]] = {}
        self._ingat: Dict[str, int] = {}
        self._salah: Dict[str, int] = {}

    def daftar(self, eid: Any, hl: Optional[float] = None) -> float:
        k = _teks(eid)
        if k not in self._hl:
            self._hl[k] = _kclip(float(hl) if hl else self.dasar, self.min, self.maks)
        self._skala_subjektif.setdefault(k, 1.0)
        return self._hl[k]

    def skala_subjektif(self, eid: Any, faktor: Optional[float] = None,
                        durasi_objektif: Optional[float] = None,
                        durasi_subjektif: Optional[float] = None,
                        keadaan: str = "") -> float:
        """Baca/tetapkan pembesaran waktu yang dialami satu episode.

        Nilai ini bukan importance: ia mengubah half-life struktural episode
        dan disimpan terpisah dari penguatan oleh recall atau koreksi.
        """
        k = _teks(eid)
        self.daftar(k)
        if faktor is not None:
            self._skala_subjektif[k] = _kclip(faktor, 0.20, 3.50)
            self._durasi_subjektif[k] = {
                "durasi_objektif": (None if durasi_objektif is None else
                                     max(0.0, float(durasi_objektif))),
                "durasi_subjektif": (None if durasi_subjektif is None else
                                     max(0.0, float(durasi_subjektif))),
                "keadaan": str(keadaan or "")[:32],
            }
        return float(self._skala_subjektif.get(k, 1.0))

    def diingat(self, eid: Any, kali: int = 1) -> float:
        """Recall memperpanjang half-life."""
        k = _teks(eid)
        self.daftar(k)
        for _ in range(max(1, int(kali))):
            self._hl[k] = _kclip(self._hl[k] * (1.0 + self.laju_ingat),
                                 self.min, self.maks)
        self._ingat[k] = self._ingat.get(k, 0) + max(1, int(kali))
        return self.half_life(k)

    def dikoreksi_salah(self, eid: Any, kali: int = 1) -> float:
        """Konfirmasi bahwa ingatan itu keliru memendekkan half-life."""
        k = _teks(eid)
        self.daftar(k)
        for _ in range(max(1, int(kali))):
            self._hl[k] = _kclip(self._hl[k] * (1.0 - self.laju_salah),
                                 self.min, self.maks)
        self._salah[k] = self._salah.get(k, 0) + max(1, int(kali))
        return self.half_life(k)

    def half_life(self, eid: Any) -> float:
        k = _teks(eid)
        dasar = self.daftar(k)
        # Kompresi subjektif boleh menembus lantai pembelajaran dasar: episode
        # yang waktunya melesat memang dapat meluruh lebih cepat dari min.
        return _kclip(dasar * self._skala_subjektif.get(k, 1.0),
                      1.0, self.maks)

    def bobot(self, eid: Any, umur: float) -> float:
        hl = self.half_life(eid)
        return 0.5 ** (max(0.0, float(umur)) / hl)

    def ringkas(self, top: int = 8) -> Dict[str, Any]:
        efektif = {k: self.half_life(k) for k in self._hl}
        urut = sorted(efektif.items(), key=lambda kv: kv[1], reverse=True)
        return {"n": len(self._hl),
                "dasar": self.dasar,
                "terpanjang": [[k, round(v, 1)] for k, v in urut[:top]],
                "terpendek": [[k, round(v, 1)] for k, v in urut[-top:]],
                "skala_subjektif": {k: round(v, 3) for k, v in
                                    self._skala_subjektif.items()},
                "diingat": dict(self._ingat), "dikoreksi_salah": dict(self._salah)}

    def to_dict(self) -> Dict[str, Any]:
        return {"dasar": self.dasar, "min": self.min, "maks": self.maks,
                "laju_ingat": self.laju_ingat, "laju_salah": self.laju_salah,
                "hl": dict(self._hl),
                "skala_subjektif": dict(self._skala_subjektif),
                "durasi_subjektif": {k: dict(v) for k, v in
                                     self._durasi_subjektif.items()},
                "ingat": dict(self._ingat), "salah": dict(self._salah)}

    @classmethod
    def from_dict(cls, d: Optional[Mapping[str, Any]]) -> "WaktuHeterogen":
        if not isinstance(d, Mapping):
            return cls()
        o = cls(dasar=d.get("dasar", 600.0), min_=d.get("min", 30.0),
                maks=d.get("maks", 20000.0),
                laju_ingat=d.get("laju_ingat", 0.35),
                laju_salah=d.get("laju_salah", 0.30))
        o._hl = {str(k): _kclip(v, o.min, o.maks)
                 for k, v in (d.get("hl") or {}).items()}
        o._skala_subjektif = {
            str(k): _kclip(v, 0.20, 3.50)
            for k, v in (d.get("skala_subjektif") or {}).items()}
        o._durasi_subjektif = {
            str(k): dict(v) for k, v in
            (d.get("durasi_subjektif") or {}).items()
            if isinstance(v, Mapping)}
        for k in o._hl:
            o._skala_subjektif.setdefault(k, 1.0)
        o._ingat = {str(k): int(v) for k, v in (d.get("ingat") or {}).items()}
        o._salah = {str(k): int(v) for k, v in (d.get("salah") or {}).items()}
        return o


# =====================================================================
# 5. KEGAGALAN YANG BERASAL DARI DALAM — tubuh menolak mengartikulasi
# =====================================================================
class PenolakanTutur:
    """Kalimat sudah TERBENTUK, tetapi state tubuh menolak mengucapkannya.

    Berbeda dari:
      * gagap kosmetik ("s-s") — permukaan, tidak menyentuh isi;
      * ``restriksi_gagal`` semantik — tidak ada kata yang cocok di leksikon.

    Di sini leksikon MAMPU, sintaksis MAMPU, isi SUDAH ADA — dan tetap tidak
    terucap. Penyebabnya keadaan tubuh: panik, takut, malu, disosiasi, duka,
    atau klaim identitas yang melarang tindak tutur itu.

    ``kelayakan()`` mengembalikan skor 0..1 beserta rincian komponen, sehingga
    penolakan dapat dipertanggungjawabkan (bukan if-else tersembunyi).
    """

    def __init__(self, ambang: float = 0.45) -> None:
        self.ambang = float(ambang)
        self._riwayat: List[Dict[str, Any]] = []

    def kelayakan(self, konteks: Mapping[str, Any]) -> Tuple[float, Dict[str, float]]:
        k = konteks or {}
        komp: Dict[str, float] = {}
        komp["arousal"] = -0.90 * max(0.0, float(k.get("arousal", 0.0) or 0.0) - 0.55)
        komp["takut"] = -1.10 * max(0.0, float(k.get("takut", 0.0) or 0.0) - 0.35)
        komp["malu"] = -1.30 * max(0.0, float(k.get("malu", 0.0) or 0.0) - 0.30)
        _koher = k.get("koherensi", 1.0)
        if _koher is None:
            _koher = 1.0
        komp["disosiasi"] = -1.20 * max(0.0, 0.55 - float(_koher))
        komp["duka"] = -1.00 * max(0.0, float(k.get("duka", 0.0) or 0.0) - 0.25)
        if k.get("batas_identitas"):
            komp["identitas"] = -0.80
        skor = _kclip(1.0 + sum(komp.values()), 0.0, 1.0)
        return skor, komp

    def kelayakan_bertipe(self, konteks: Mapping[str, Any]):
        """(skor, komponen, jenis, label) — sebab penolakan sekaligus."""
        skor, komp = self.kelayakan(konteks)
        return skor, komp, self.jenis(komp), self.jenis_penolakan(komp)

    def tertahan(self, kelayakan: float, rng: Optional[random.Random] = None) -> bool:
        """Apakah tutur kali ini tertahan? Peluang naik saat kelayakan turun."""
        r = rng or _RNG_CADANGAN
        p = _kclip((self.ambang - float(kelayakan)) / max(1e-6, self.ambang),
                   0.0, 0.95)
        return r.random() < p

    def jenis(self, komponen: Optional[Mapping[str, float]] = None) -> str:
        """Sebab dominan penolakan: komponen yang paling negatif."""
        k = komponen or {}
        if not k:
            return "tanpa_sebab"
        return min(k, key=lambda n: float(k.get(n, 0.0) or 0.0))

    def bentuk(self, teks_terbentuk: Any,
               rng: Optional[random.Random] = None,
               komponen: Optional[Mapping[str, float]] = None) -> str:
        """Bentuk yang TERUCAP saat tubuh menolak — DIBEDAKAN menurut SEBAB.

        Gagap kosmetik hanya punya satu bentuk seragam. Di sini cara menahan
        diri berasal dari sebabnya: takut memutus kalimat, malu mengalihkan,
        disosiasi mengacak, duka memanggil yang hilang, arousal memotong di
        awal, dan identitas menolak secara eksplisit.
        """
        r = rng or _RNG_CADANGAN
        kata = _teks(teks_terbentuk).split()
        awal = kata[0] if kata else ""
        j = self.jenis(komponen)
        if j == "takut":
            return (awal + "\u2026 aku tidak\u2014") if awal else "aku tidak\u2014"
        if j == "malu":
            return r.choice(["\u2026", "bukan apa-apa.", "\u2026",
                             "tidak usah dibicarakan."])
        if j == "disosiasi":
            if len(kata) >= 2:
                acak = list(kata)
                r.shuffle(acak)
                return " ".join(acak[:2]) + "\u2026"
            return "\u2026"
        if j == "duka":
            return r.choice(["\u2026dia\u2026", "\u2026", "aku\u2026 belum bisa."])
        if j == "arousal":
            if len(kata) >= 2:
                return " ".join(kata[:2]) + "\u2014"
            return (awal + "\u2014") if awal else "\u2014"
        if j == "identitas":
            return "aku tidak akan mengatakannya."
        return r.choice(["\u2026", (awal + "\u2026") if awal else "\u2026",
                         "\u2026tidak.", ""])

    def jenis_penolakan(self, komponen: Optional[Mapping[str, float]] = None) -> str:
        """Label manusiawi untuk sebab penolakan."""
        return _JENIS_PENOLAKAN.get(self.jenis(komponen), "sebab tidak jelas")

    def catat(self, teks_terbentuk: str, teks_terucap: str, kelayakan: float,
              komponen: Mapping[str, float], tick: int = 0) -> Dict[str, Any]:
        rec = {"tick": int(tick),
               "teks_terbentuk": _teks(teks_terbentuk)[:200],
               "teks_terucap": _teks(teks_terucap)[:200],
               "kelayakan": round(float(kelayakan), 3),
               "komponen": {k: round(float(v), 3) for k, v in (komponen or {}).items()},
               "sebab": "tubuh menolak"}
        self._riwayat.append(rec)
        if len(self._riwayat) > 64:
            del self._riwayat[:-64]
        return dict(rec)

    def riwayat(self) -> List[Dict[str, Any]]:
        return [dict(x) for x in self._riwayat]

    def to_dict(self) -> Dict[str, Any]:
        return {"ambang": self.ambang, "riwayat": [dict(x) for x in self._riwayat]}

    @classmethod
    def from_dict(cls, d: Optional[Mapping[str, Any]]) -> "PenolakanTutur":
        o = cls(ambang=(d or {}).get("ambang", 0.45) if isinstance(d, Mapping) else 0.45)
        if isinstance(d, Mapping):
            o._riwayat = [dict(x) for x in (d.get("riwayat") or [])]
        return o


# =====================================================================
# 6. APERSEPSI — kemampuan untuk TIDAK tahu (alexithymia, kabut, tanpa nama)
# =====================================================================
class Apersepsi:
    """Sistem boleh GAGAL menamai perasaannya, dan kegagalan itu adalah state.

    Arsitektur lama mengasumsikan perasaan adalah kategori yang diketahui:
    FELT_STATES delapan nama, tiap tick kedelapannya terisi, selalu ada nama.
    Di sini yang ditambahkan justru PENGURANGAN: felt boleh kosong, boleh kabut,
    boleh berupa gradien tanpa arah, boleh pola yang belum punya nama.

    Modus yang dikembalikan:
      * ``jelas``      — satu kategori dominan, keyakinan tinggi.
      * ``kabut``      — ada yang salah tanpa tahu apa (entropi tinggi).
      * ``gradien``    — ada gerak di dalam, arahnya tak terbaca.
      * ``tanpa_nama`` — tekanan kuat tetapi tidak cocok kategori mana pun.
      * ``kosong``     — tidak ada yang terasa.

    ``hud_state()`` menampilkan ketidakhadiran ini secara eksplisit.
    """

    def __init__(self, ambang_jelas: float = 0.42, ambang_kosong: float = 0.06,
                 ambang_tekanan: float = 0.30, jendela: int = 8) -> None:
        self.ambang_jelas = float(ambang_jelas)
        self.ambang_kosong = float(ambang_kosong)
        self.ambang_tekanan = float(ambang_tekanan)
        self.jendela = max(2, int(jendela))
        self._riwayat: List[Dict[str, float]] = []

    def amati(self, felt: Mapping[str, float],
              levels: Optional[Mapping[str, float]] = None,
              dikenal: Optional[Sequence[str]] = None,
              klaim_identitas: str = "") -> Dict[str, Any]:
        f = {k: max(0.0, float(v or 0.0)) for k, v in (felt or {}).items()}
        kategor = list(dikenal) if dikenal else sorted(f.keys())
        total = sum(f.values())
        kekuatan = max(f.values()) if f else 0.0

        # --- gradien: arah gerak felt, dan apakah arahnya terbaca ---
        self._riwayat.append(dict(f))
        if len(self._riwayat) > self.jendela:
            del self._riwayat[:-self.jendela]
        gradien = self._gradien(f)

        # --- keyakinan nama: 1 - entropi ternormalisasi ---
        if total <= 1e-9:
            keyakinan = 0.0
        else:
            p = [v / total for v in f.values() if v > 0]
            h = -sum(x * math.log(x) for x in p if x > 0)
            h_norm = h / math.log(len(f)) if len(f) > 1 else 0.0
            keyakinan = _kclip(1.0 - h_norm, 0.0, 1.0)

        # --- tekanan drive: apakah ada sesuatu yang MENDESAK ---
        lv = levels or {}
        tekanan = max((abs(float(v or 0.0)) for v in lv.values()), default=0.0)
        nama_teratas = max(f, key=lambda k: f[k]) if f else None
        teratas_dikenal = nama_teratas in kategor if nama_teratas else False

        if kekuatan < self.ambang_kosong:
            modus, nama = "kosong", None
        elif keyakinan >= self.ambang_jelas:
            modus, nama = "jelas", nama_teratas
        elif tekanan >= self.ambang_tekanan and not teratas_dikenal:
            modus, nama = "tanpa_nama", None
        elif gradien["magnitudo"] > 0.02 and not gradien["arah_terbaca"]:
            modus, nama = "gradien", None
        else:
            modus, nama = "kabut", None

        kalimat = {
            "jelas": "aku merasa {n}.".format(n=nama or "sesuatu"),
            "kabut": "ada yang salah, tapi aku tidak tahu apa.",
            "gradien": "ada yang bergerak di dalam diriku dan aku tidak bisa "
                       "melihat arahnya.",
            "tanpa_nama": "ada sesuatu di dalam diriku yang belum punya nama.",
            "kosong": "aku tidak merasakan apa-apa.",
        }[modus]

        return {"modus": modus, "nama": nama,
                "kategori_dikenal": bool(modus == "jelas" and teratas_dikenal),
                "keyakinan_nama": round(keyakinan, 4),
                "kekuatan": round(kekuatan, 4),
                "tekanan_drive": round(tekanan, 4),
                "gradien": gradien,
                "signature": self._signature(f),
                "kalimat": kalimat,
                "identitas_ada": bool(_teks(klaim_identitas).strip())}

    def _gradien(self, f: Mapping[str, float]) -> Dict[str, Any]:
        """Arah gerak felt antar-tick; 'arah_terbaca' False bila berputar."""
        if len(self._riwayat) < 3:
            return {"magnitudo": 0.0, "arah_terbaca": False, "putaran": 0.0,
                    "delta": {}}
        kunci = sorted(set().union(*[set(x.keys()) for x in self._riwayat[-3:]]))
        vec = [[float(x.get(k, 0.0)) for k in kunci] for x in self._riwayat[-3:]]
        d1 = [vec[1][i] - vec[0][i] for i in range(len(kunci))]
        d2 = [vec[2][i] - vec[1][i] for i in range(len(kunci))]
        n1 = math.sqrt(sum(x * x for x in d1))
        n2 = math.sqrt(sum(x * x for x in d2))
        if n1 < 1e-9 or n2 < 1e-9:
            return {"magnitudo": round(max(n1, n2), 4), "arah_terbaca": True,
                    "putaran": 0.0,
                    "delta": {k: round(v, 4) for k, v in zip(kunci, d2) if abs(v) > 1e-4}}
        kosinus = sum(d1[i] * d2[i] for i in range(len(kunci))) / (n1 * n2)
        return {"magnitudo": round(n2, 4),
                "arah_terbaca": bool(kosinus > 0.35),
                "putaran": round(kosinus, 4),
                "delta": {k: round(v, 4) for k, v in zip(kunci, d2) if abs(v) > 1e-4}}

    @staticmethod
    def _signature(f: Mapping[str, float]) -> str:
        """Sidik jari pola untuk kategori yang belum punya nama."""
        aktif = sorted((k, round(float(v or 0.0), 2)) for k, v in f.items()
                       if float(v or 0.0) > 0.02)
        return "|".join("{}=".format(k) + str(v) for k, v in aktif) or "-"

    def to_dict(self) -> Dict[str, Any]:
        return {"riwayat": [dict(x) for x in self._riwayat]}

    @classmethod
    def from_dict(cls, d: Optional[Mapping[str, Any]]) -> "Apersepsi":
        o = cls()
        if isinstance(d, Mapping):
            o._riwayat = [dict(x) for x in (d.get("riwayat") or [])]
        return o


# =====================================================================
# 7. LAPISAN PARALEL — dua keyakinan bertentangan hidup berdampingan
# =====================================================================
class LapisanParalel:
    """Keyakinan yang saling meniadakan TIDAK diselesaikan — keduanya aktif.

    Arsitektur lama adalah pencari konsistensi: ``hold_belief`` menaikkan
    tension, ``terima_bukti``/``harden_belief``/``_defense`` menurunkannya.
    Semua jalur menuju resolusi, dan ``disonansi`` adalah SKALAR — ia mengukur
    seberapa besar ketegangan, bukan APA yang bertentangan.

    Di sini dua lapisan hidup berdampingan dan keduanya memengaruhi perilaku
    secara paralel. Tidak ada metode penyelesaian. Ketegangannya nol, justru
    karena tidak ada yang dianggap perlu diselesaikan.
    """

    def __init__(self, maks: int = 8) -> None:
        self.maks = max(1, int(maks))
        self._lapisan: List[Dict[str, Any]] = []
        self._berikut = 1

    def tambah(self, klaim: Any, bobot: float = 0.5,
               emosi: Optional[Mapping[str, float]] = None,
               konteks: Any = None, tick: int = 0,
               lawan_dari: Optional[int] = None,
               sumber: str = "") -> Dict[str, Any]:
        lap = {"id": self._berikut, "klaim": _teks(klaim)[:160],
               "bobot": _kclip(float(bobot), 0.0, 1.0),
               "emosi": {str(k): float(v) for k, v in (emosi or {}).items()},
               "konteks": _teks(konteks)[:60], "tick": int(tick),
               "lawan_dari": lawan_dari, "sumber": _teks(sumber)[:60]}
        self._berikut += 1
        self._lapisan.append(lap)
        if len(self._lapisan) > self.maks:
            del self._lapisan[:-self.maks]
        return dict(lap)

    def aktif(self, konteks: Any = None) -> List[Dict[str, Any]]:
        """Konteks kosong -> semua lapisan aktif (paralel penuh)."""
        k = _teks(konteks)
        if not k:
            return [dict(x) for x in self._lapisan]
        return [dict(x) for x in self._lapisan
                if not x["konteks"] or x["konteks"] in k]

    def pengaruh(self, konteks: Any = None) -> Dict[str, float]:
        """Pengaruh PARALEL: semua lapisan aktif dijumlahkan, tak saling meniadakan."""
        hasil: Dict[str, float] = {}
        for lap in self.aktif(konteks):
            for e, v in lap["emosi"].items():
                hasil[e] = hasil.get(e, 0.0) + float(v) * float(lap["bobot"])
        return {k: round(v, 4) for k, v in hasil.items()}

    def bertentangan(self) -> List[Dict[str, Any]]:
        """Pasangan lapisan yang saling meniadakan tetapi tetap berdampingan."""
        keluar = []
        for i, a in enumerate(self._lapisan):
            for b in self._lapisan[i + 1:]:
                tandai = (a.get("lawan_dari") == b["id"] or b.get("lawan_dari") == a["id"])
                if not tandai:
                    for e in set(a["emosi"]) & set(b["emosi"]):
                        if a["emosi"][e] * b["emosi"][e] < 0:
                            tandai = True
                            break
                if tandai:
                    keluar.append({"a": a["klaim"], "b": b["klaim"],
                                   "id_a": a["id"], "id_b": b["id"]})
        return keluar

    def disonansi_paralel(self) -> float:
        """Selalu 0.0: tidak ada ketegangan karena tidak ada yang perlu selesai."""
        return 0.0

    def tanpa_resolusi(self) -> bool:
        return len(self._lapisan) >= 2 and bool(self.bertentangan())

    def bertindak_dari(self, konteks: Any) -> Optional[Dict[str, Any]]:
        """Bertindak dari SATU lapisan sesuai situasi, tanpa menyadari peralihan."""
        k = _teks(konteks)
        cocok = [x for x in self._lapisan if x["konteks"] and x["konteks"] in k]
        if not cocok:
            return None
        return dict(max(cocok, key=lambda x: x["bobot"]) )

    def state(self) -> Dict[str, Any]:
        return {"jumlah": len(self._lapisan),
                "lapisan": [dict(x) for x in self._lapisan],
                "bertentangan": self.bertentangan(),
                "disonansi_paralel": 0.0,
                "tanpa_resolusi": self.tanpa_resolusi()}

    def to_dict(self) -> Dict[str, Any]:
        return {"maks": self.maks, "berikut": self._berikut,
                "lapisan": [dict(x) for x in self._lapisan]}

    @classmethod
    def from_dict(cls, d: Optional[Mapping[str, Any]]) -> "LapisanParalel":
        o = cls(maks=(d or {}).get("maks", 8) if isinstance(d, Mapping) else 8)
        if isinstance(d, Mapping):
            o._lapisan = [dict(x) for x in (d.get("lapisan") or [])]
            o._berikut = int(d.get("berikut", len(o._lapisan) + 1) or 1)
        return o


# =====================================================================
# 8. TUBUH SUMBER — tubuh mendahului kognisi
# =====================================================================
class TubuhSumber:
    """Tubuh bukan cermin: ia punya dinamikanya SENDIRI dan mendorong drive.

    Arsitektur lama mengalir satu arah: levels -> felt_state -> somatic_markers
    -> narrative_identity. Tubuh hanya menampilkan keputusan kognisi.

    Di sini panah itu DIBALIK. ``tegang`` adalah integrator bocor atas keadaan
    tubuh sendiri, sehingga ia punya inersia dan bisa MENDAHULUI kognisi:
    tubuh menegang dulu, drive bergerak kemudian, dan baru setelah itu
    ``felt_state`` menyesuaikan diri. Uji kausalnya jelas: apakah ada kasus di
    mana sinyal tubuh mengubah level sementara tidak ada masukan kognitif yang
    berubah? Bila tidak, cermin masih cermin.
    """

    def __init__(self, theta: float = 0.18, laju: float = 0.055,
                 batas: float = 0.35, langkah_maks: float = 0.05) -> None:
        self.theta = float(theta)
        self.laju = float(laju)
        self.batas = float(batas)
        self.langkah_maks = float(langkah_maks)
        self.tegang = 0.0
        self._jejak: List[Dict[str, Any]] = []
        # peta: isyarat tubuh -> drive yang didorong (arah = tanda)
        self.arah: Dict[str, Dict[str, float]] = {
            "nyeri": {"keamanan": -1.0, "energi": -0.5},
            "sesak": {"keamanan": -1.0, "energi": -0.3},
            "tegang": {"keamanan": -0.9, "koherensi": -0.4},
            "mual": {"keamanan": -0.7, "energi": -0.5},
            "jantung": {"keamanan": -0.6},
            "lelah": {"energi": -1.0},
            "lapar": {"energi": -0.8},
            "ringan": {"energi": 0.5, "keamanan": 0.4},
        }

    def masukan(self, felt: Mapping[str, float],
                emosi: Optional[Mapping[str, float]] = None) -> float:
        """Isyarat tubuh dari keadaannya sendiri (bukan dari levels)."""
        f = felt or {}
        negatif = sum(max(0.0, float(f.get(k, 0.0) or 0.0))
                      for k in ("nyeri", "sesak", "tegang", "mual", "jantung"))
        positif = max(0.0, float(f.get("ringan", 0.0) or 0.0))
        takut = max(0.0, float((emosi or {}).get("takut", 0.0) or 0.0))
        return negatif + 0.7 * takut - 0.8 * positif

    def langkah(self, felt: Mapping[str, float], emosi: Optional[Mapping[str, float]] = None,
                levels: Optional[Mapping[str, float]] = None, dt: float = 1.0) -> Dict[str, float]:
        """Perbarui tegangan tubuh, lalu dorong drive. Mengembalikan delta drive."""
        dt = max(0.0, float(dt))
        m = self.masukan(felt, emosi)
        self.tegang = _kclip(self.tegang * (1.0 - self.theta * dt) + m * self.theta * dt,
                             -self.batas, self.batas)
        delta: Dict[str, float] = {}
        if abs(self.tegang) > 1e-6:
            for isyarat, f in (felt or {}).items():
                w = max(0.0, float(f or 0.0))
                if w <= 0.02:
                    continue
                for drive, tanda in self.arah.get(isyarat, {}).items():
                    delta[drive] = delta.get(drive, 0.0) + self.laju * tanda * w * self.tegang
            if abs(self.tegang) > 0.05:
                delta.setdefault("keamanan", 0.0)
                delta["keamanan"] += self.laju * -0.5 * self.tegang
        delta = {k: _kclip(v, -self.langkah_maks, self.langkah_maks)
                 for k, v in delta.items() if abs(v) > 1e-6}
        self._jejak.append({"tegang": round(self.tegang, 4),
                            "masukan": round(m, 4),
                            "delta": {k: round(v, 4) for k, v in delta.items()}})
        if len(self._jejak) > 64:
            del self._jejak[:-64]
        return delta

    def suntik(self, jumlah: float) -> float:
        """Perturbasi tubuh eksplisit: tubuh bereaksi lebih dulu, tanpa sebab kognitif."""
        self.tegang = _kclip(self.tegang + float(jumlah), -self.batas, self.batas)
        return self.tegang

    def state(self) -> Dict[str, Any]:
        return {"tegang": round(self.tegang, 4), "batas": self.batas,
                "jejak": [dict(x) for x in self._jejak[-8:]]}

    def to_dict(self) -> Dict[str, Any]:
        return {"tegang": self.tegang, "theta": self.theta, "laju": self.laju,
                "batas": self.batas, "jejak": [dict(x) for x in self._jejak]}

    @classmethod
    def from_dict(cls, d: Optional[Mapping[str, Any]]) -> "TubuhSumber":
        if not isinstance(d, Mapping):
            return cls()
        o = cls(theta=d.get("theta", 0.18), laju=d.get("laju", 0.055),
                batas=d.get("batas", 0.35))
        o.tegang = float(d.get("tegang", 0.0) or 0.0)
        o._jejak = [dict(x) for x in (d.get("jejak") or [])]
        return o


class Vacancy:
    """State eksplisit tanpa pemrosesan, berakhir lewat akumulator waktunya.

    Tidak ada antrean peristiwa atau log pemikiran di sini. Metadata awal/akhir
    hanya mendeskripsikan durasi state, bukan aktivitas selama vacancy.
    """

    def __init__(self) -> None:
        self.aktif = False
        self.durasi = 0.0
        self.akumulator = 0.0
        self.tick_mulai: Optional[int] = None
        self.tick_selesai: Optional[int] = None

    def mulai(self, durasi: float, tick: int = 0) -> Dict[str, Any]:
        self.durasi = max(0.0, float(durasi))
        self.akumulator = 0.0
        self.tick_mulai = int(tick)
        self.tick_selesai = None
        self.aktif = self.durasi > 0.0
        return self.state()

    def lewat(self, dt: float = 1.0, tick: Optional[int] = None) -> float:
        """Lewatkan waktu dan kembalikan fraksi yang benar-benar vacant."""
        if not self.aktif:
            return 0.0
        sisa = max(0.0, self.durasi - self.akumulator)
        dipakai = min(max(0.0, float(dt)), sisa)
        self.akumulator += dipakai
        if self.akumulator + 1e-12 >= self.durasi:
            self.akumulator = self.durasi
            self.aktif = False
            if tick is not None:
                self.tick_selesai = int(tick)
        return dipakai

    def state(self) -> Dict[str, Any]:
        return {"aktif": self.aktif,
                "durasi": round(self.durasi, 6),
                "berlalu": round(self.akumulator, 6),
                "sisa": round(max(0.0, self.durasi - self.akumulator), 6),
                "tick_mulai": self.tick_mulai,
                "tick_selesai": self.tick_selesai}

    def to_dict(self) -> Dict[str, Any]:
        return {"aktif": self.aktif, "durasi": self.durasi,
                "akumulator": self.akumulator, "tick_mulai": self.tick_mulai,
                "tick_selesai": self.tick_selesai}

    @classmethod
    def from_dict(cls, d: Optional[Mapping[str, Any]]) -> "Vacancy":
        o = cls()
        if isinstance(d, Mapping):
            o.durasi = max(0.0, float(d.get("durasi", 0.0)))
            o.akumulator = max(0.0, min(o.durasi, float(d.get("akumulator", 0.0))))
            o.aktif = bool(d.get("aktif", False)) and o.akumulator < o.durasi
            o.tick_mulai = (None if d.get("tick_mulai") is None
                            else int(d.get("tick_mulai")))
            o.tick_selesai = (None if d.get("tick_selesai") is None
                              else int(d.get("tick_selesai")))
        return o


# =====================================================================
# 0. GEJALA MURNI — state orde nol: penampakan tanpa kategori
# =====================================================================
# State Pycos yang ada semuanya ber-orde: drive/emosi/memori (orde satu),
# kesadaran yang mengamati drive & NURANI yang mengamati naluri (orde dua),
# organik yang mengubah sifat state (orde tiga parsial). Yang tidak ada:
# orde nol — bahan mentah dari mana orde-orde baru bisa mengkristal.
#
# Tanpa orde nol, sistem hanya bisa mengombinasi kategori yang sudah ada; ia
# tidak bisa melahirkan kategori baru, dan setiap input yang benar-benar asing
# hanya bisa dipetakan paksa ke kategori terdekat (terbaca sebagai tidak paham).
#
# Gejala murni adalah penampakan TANPA kategori. Empat properti, tidak lebih:
#   1. intensitas — skalar [0..1]; bukan drive/emosi, hanya kuat.
#   2. polaritas  — [-1..+1] ATAU None; banyak state baru belum terasa
#                   baik/buruk, dan None adalah jawaban yang sah.
#   3. tanpa tipe — tidak ada label, drive, emosi, memori. Kalau ada label,
#                   ia sudah bukan gejala murni.
#   4. menuntut   — hadir di workspace dan mendesak; tidak bisa diabaikan.
#
# Yang sengaja TIDAK dimiliki: durasi (ia boleh memudar), isi (ia kosong),
# sebab (ia bisa muncul tanpa sebab), tujuan (ia tidak tahu apa yang ia
# inginkan). Tidak ada field untuk keempatnya; ``properti_terlarang()``
# menegakkan itu secara eksplisit supaya pembaca tidak menambahkannya diam-diam.
#
# Secara fenomenologis ini momen paling primitif: bukan "aku merasa X", tetapi
# "ada sesuatu". Sebelum pertanyaan *apa*, ada fakta *bahwa*.

PROPERTI_TERLARANG: Tuple[str, ...] = ("durasi", "isi", "sebab", "tujuan",
                                       "label", "nama", "tipe")

# Kalimat yang BUKAN nama: pernyataan keberadaan, bukan kategori.
KALIMAT_ADA_SESUATU = "ada sesuatu"
KALIMAT_TAK_BERNAMA = "ada sesuatu yang tidak bisa kunamai"


class GejalaMurni:
    """Satu penampakan tanpa kategori (state orde nol).

    Objek ini tidak punya ``step()`` dan tidak punya jam: gejala boleh memudar
    (diputuskan ``Gejala.proses()``), tetapi "durasi" bukan propertinya.
    ``perbarui()`` menandai gejala yang SAMA hadir lagi — itulah satu-satunya
    cara kebaruan berubah menjadi pola.
    """

    def __init__(self, intensitas: float, polaritas: Optional[float] = None,
                 signature: str = "", tick: int = 0, gejala_id: int = 0) -> None:
        self.id = int(gejala_id)
        self.signature = str(signature)
        self.intensitas = _kclip(float(intensitas), 0.0, 1.0)
        self.polaritas: Optional[float] = (
            None if polaritas is None else _kclip(float(polaritas), -1.0, 1.0))
        self.tick_lahir = int(tick)
        self.tick_terakhir = int(tick)
        self.ulangan = 1
        self.riwayat: List[Tuple[int, float, Optional[float]]] = [
            (int(tick), round(self.intensitas, 4), self.polaritas)]
        self.hidup = True
        # Terklaim = salah satu modul berhasil memetakannya → ia tidak lagi
        # baru, dan tidak lagi gejala murni.
        self.terklaim: Optional[Dict[str, Any]] = None

    # ------------------------------------------------------------------
    def perbarui(self, intensitas: float,
                 polaritas: Optional[float] = None,
                 tick: Optional[int] = None) -> Dict[str, Any]:
        """Gejala yang sama muncul lagi: kuatnya diperbarui, arah boleh menyusul.

        Polaritas yang tadinya ``None`` boleh menjadi terdefinisi (arah
        ditemukan belakangan); polaritas yang sudah ada dirata-ratakan perlahan
        — arah keyakinan tidak berubah karena satu kemunculan.
        """
        self.ulangan += 1
        self.intensitas = _kclip(max(self.intensitas, float(intensitas)), 0.0, 1.0)
        if polaritas is not None:
            baru = _kclip(float(polaritas), -1.0, 1.0)
            self.polaritas = (baru if self.polaritas is None
                              else _kclip(0.5 * (self.polaritas + baru), -1.0, 1.0))
        if tick is not None:
            self.tick_terakhir = int(tick)
        self.riwayat.append((self.tick_terakhir, round(self.intensitas, 4),
                             self.polaritas))
        if len(self.riwayat) > 16:
            del self.riwayat[:-16]
        return self.state()

    def tekanan(self) -> float:
        """Menuntut: selama hidup, ia tidak boleh turun ke nol (tak terabaikan)."""
        if not self.hidup:
            return 0.0
        return _kclip(max(self.intensitas, 0.05), 0.0, 1.0)

    def tandai_terklaim(self, jenis: str, kategori: Optional[str] = None,
                        tick: int = 0, kuat: float = 0.0) -> Dict[str, Any]:
        """Catat bahwa sebuah modul BERHASIL mengklaimnya (state menjadi betipe)."""
        self.terklaim = {"jenis": str(jenis), "kategori": kategori,
                         "tick": int(tick), "kuat": round(float(kuat), 4)}
        return dict(self.terklaim)

    def properti_terlarang(self) -> List[str]:
        """Properti yang seharusnya tidak pernah menempel pada gejala murni."""
        return [n for n in PROPERTI_TERLARANG if hasattr(self, n)]

    def state(self) -> Dict[str, Any]:
        return {
            "id": self.id, "signature": self.signature,
            "intensitas": round(self.intensitas, 4),
            "polaritas": (None if self.polaritas is None
                          else round(self.polaritas, 4)),
            "tanpa_tipe": True, "menuntut": bool(self.hidup),
            "tekanan": round(self.tekanan(), 4),
            "ulangan": int(self.ulangan), "hidup": bool(self.hidup),
            "tick_lahir": self.tick_lahir, "tick_terakhir": self.tick_terakhir,
            "terklaim": (dict(self.terklaim) if self.terklaim else None),
            "tidak_dimiliki": {"durasi": None, "isi": None, "sebab": None,
                               "tujuan": None},
        }

    def to_dict(self) -> Dict[str, Any]:
        return {"id": self.id, "signature": self.signature,
                "intensitas": self.intensitas, "polaritas": self.polaritas,
                "tick_lahir": self.tick_lahir, "tick_terakhir": self.tick_terakhir,
                "ulangan": self.ulangan,
                "riwayat": [[int(t), float(i), p] for t, i, p in self.riwayat],
                "hidup": bool(self.hidup),
                "terklaim": dict(self.terklaim) if self.terklaim else None}

    @classmethod
    def from_dict(cls, d: Optional[Mapping[str, Any]]) -> "GejalaMurni":
        d = d or {}
        g = cls(float(d.get("intensitas", 0.0)),
                d.get("polaritas"), str(d.get("signature", "")),
                int(d.get("tick_lahir", 0)), int(d.get("id", 0)))
        g.tick_terakhir = int(d.get("tick_terakhir", g.tick_lahir))
        g.ulangan = max(1, int(d.get("ulangan", 1)))
        g.hidup = bool(d.get("hidup", True))
        g.terklaim = (dict(d["terklaim"]) if isinstance(d.get("terklaim"), Mapping)
                      else None)
        g.riwayat = [(int(t), float(i), p) for t, i, p in (d.get("riwayat") or [])
                     if isinstance(t, (int, float))]
        return g


class KategoriProto:
    """Slot baru yang lahir dari gejala BERULANG — bukan nama, bukan label penuh.

    Proto adalah penanda beda (``signature``) + modul yang paling akrab
    (``jenis``) + nama sementara (boleh ``None``; hanya Tutur yang boleh
    memberikannya) + bukti kemunculan. Ia baru menjadi kategori penuh setelah
    BERTAHAN cukup lama DAN cukup sering muncul — bukan setelah sekali terasa.
    """

    def __init__(self, signature: str, jenis: str = "tutur",
                 nama: Optional[str] = None, intensitas: float = 0.0,
                 tick: int = 0) -> None:
        self.signature = str(signature)
        self.jenis = str(jenis or "tutur")
        self.nama = (str(nama)[:40] if nama else None)
        self.nama_dari = "tutur" if nama else None
        self.jumlah = 1
        self.intensitas_puncak = _kclip(float(intensitas), 0.0, 1.0)
        self.intensitas_rata = _kclip(float(intensitas), 0.0, 1.0)
        self.tick_lahir = int(tick)
        self.tick_terakhir = int(tick)

    def konfirmasi(self, intensitas: float, tick: int,
                   nama: Optional[str] = None) -> Dict[str, Any]:
        self.jumlah += 1
        x = _kclip(float(intensitas), 0.0, 1.0)
        self.intensitas_puncak = max(self.intensitas_puncak, x)
        self.intensitas_rata = _kclip(
            self.intensitas_rata + (x - self.intensitas_rata) / self.jumlah,
            0.0, 1.0)
        self.tick_terakhir = int(tick)
        if nama and not self.nama:
            self.nama = str(nama)[:40]
            self.nama_dari = "tutur"
        return self.state()

    def beri_nama(self, nama: Optional[str]) -> Optional[str]:
        """Tutur boleh (atau tidak) memberi nama sementara; nama bukan syarat."""
        if nama and not self.nama:
            self.nama = str(nama)[:40]
            self.nama_dari = "tutur"
        return self.nama

    def umur(self, kini: int) -> int:
        return max(0, int(kini) - self.tick_lahir)

    def layak_penuh(self, kini: int, min_ulang: int = 4,
                    min_umur: int = 40) -> bool:
        """Bobot dan usia diuji bersama: satu momen kuat pun belum kategori."""
        return (self.jumlah >= max(2, int(min_ulang))
                and self.umur(kini) >= max(0, int(min_umur)))

    def state(self) -> Dict[str, Any]:
        return {"signature": self.signature, "jenis": self.jenis,
                "nama": self.nama, "nama_dari": self.nama_dari,
                "jumlah": int(self.jumlah),
                "intensitas_puncak": round(self.intensitas_puncak, 4),
                "intensitas_rata": round(self.intensitas_rata, 4),
                "tick_lahir": self.tick_lahir,
                "tick_terakhir": self.tick_terakhir,
                "bernama": bool(self.nama)}

    def to_dict(self) -> Dict[str, Any]:
        return {"signature": self.signature, "jenis": self.jenis,
                "nama": self.nama, "nama_dari": self.nama_dari,
                "jumlah": self.jumlah,
                "intensitas_puncak": self.intensitas_puncak,
                "intensitas_rata": self.intensitas_rata,
                "tick_lahir": self.tick_lahir,
                "tick_terakhir": self.tick_terakhir}

    @classmethod
    def from_dict(cls, d: Optional[Mapping[str, Any]]) -> "KategoriProto":
        d = d or {}
        p = cls(str(d.get("signature", "")), str(d.get("jenis", "tutur")),
                d.get("nama"), float(d.get("intensitas_puncak", 0.0)),
                int(d.get("tick_lahir", 0)))
        p.nama_dari = d.get("nama_dari")
        p.jumlah = max(1, int(d.get("jumlah", 1)))
        p.intensitas_puncak = _kclip(float(d.get("intensitas_puncak", 0.0)), 0.0, 1.0)
        p.intensitas_rata = _kclip(float(d.get("intensitas_rata",
                                               p.intensitas_puncak)), 0.0, 1.0)
        p.tick_terakhir = int(d.get("tick_terakhir", p.tick_lahir))
        return p


class Gejala:
    """Pipeline gejala murni → (endapan | pemudaran) → kategori (proto → penuh).

    Seluruh langkah memakai mesin yang SUDAH ada; kelas ini hanya menyimpan
    bahan mentah dan keputusannya:

      1. ``muncul``    — tekanan masuk tanpa tag/source/kind; belum ada yang
                         mengklaimnya.
      2. ``gagal``     — tak ada modul yang cocok; kegagalan itu sendiri state
                         ("ada sesuatu yang tidak bisa kunamai").
      3. ``tanda``     — signature; penanda BEDA, bukan nama.
      4. ``klaim``     — modul (drive/emosi/memori/tutur) mencalonkan diri;
                         berhasil = gejala menjadi state betipe, bukan baru lagi.
      5. ``proses``    — berulang → kategori proto; tak berulang → memudar,
                         meninggalkan bekas (bukan entri aktif).
      6. konsolidasi   — proto yang bertahan lama & sering → kategori penuh;
                         diputuskan di sini, DITERAPKAN oleh modul pemanggil
                         lewat keputusan yang dikembalikan ``proses``.

    ``proses`` sengaja hanya MENGEMBALIKAN keputusan (``endapan``,
    ``pemudaran``, ``konsolidasi``) — modul pemanggil yang menerapkannya ke
    memori/identitas/NURANI. Dengan begitu kelas ini tetap bebas modul lain.
    """

    def __init__(self, ambang_ulang: int = 3, proto_min_ulang: int = 4,
                 proto_min_umur: int = 40, memudar_ticks: int = 12,
                 max_aktif: int = 24, max_bekas: int = 64) -> None:
        self.ambang_ulang = max(2, int(ambang_ulang))
        self.proto_min_ulang = max(2, int(proto_min_ulang))
        self.proto_min_umur = max(0, int(proto_min_umur))
        self.memudar_ticks = max(1, int(memudar_ticks))
        self.max_aktif = max(4, int(max_aktif))
        self.max_bekas = max(4, int(max_bekas))
        self._aktif: Dict[str, GejalaMurni] = {}
        self._proto: Dict[str, KategoriProto] = {}
        self._penuh: Dict[str, Dict[str, Any]] = {}
        self._terklaim: List[Dict[str, Any]] = []
        # Tanda yang SUDAH punya arti (terklaim modul atau kategori penuh):
        # kemunculan berikutnya bukan lagi gejala murni, melainkan perjumpaan
        # dengan sesuatu yang sudah dikenal.
        self._dikenal: Dict[str, Dict[str, Any]] = {}
        self._bekas: List[Dict[str, Any]] = []
        self._log: List[Dict[str, Any]] = []
        self._berikut = 1
        self._endapan_count = 0
        self._konsolidasi_count = 0

    # ------------------------------------------------------------------
    # 3) tanda — penanda beda, bukan nama
    # ------------------------------------------------------------------
    @staticmethod
    def tanda_dari(nilai: Any) -> str:
        """Signature stabil (crc32) dari bahan mentah; deterministik antar-proses."""
        bahan = repr(nilai).encode("utf-8")
        return format(zlib.crc32(bahan) & 0xFFFFFFFF, "08x")

    # ------------------------------------------------------------------
    # 1) muncul
    # ------------------------------------------------------------------
    def muncul(self, intensitas: float, polaritas: Optional[float] = None,
               tanda: Optional[str] = None, tick: int = 0) -> Dict[str, Any]:
        """Tekanan masuk. Tanpa tag, tanpa source, tanpa kind.

        Bila ``tanda`` tidak diberikan, signature diturunkan dari kuantisasi
        (intensitas, polaritas) — cukup sebagai penanda beda, bukan label.
        """
        x = _kclip(float(intensitas), 0.0, 1.0)
        pol = None if polaritas is None else _kclip(float(polaritas), -1.0, 1.0)
        sig = str(tanda) if tanda else self.tanda_dari(
            (round(x, 1), None if pol is None else round(pol, 1)))
        # Sudah dikenal? Maka ia bukan gejala murni lagi: yang datang adalah
        # sesuatu yang punya arti (dan artinya dipakai ulang oleh pemanggil).
        dikenal = self._dikenal.get(sig)
        if dikenal is not None:
            entri = dict(dikenal)
            entri["ulangan_dikenal"] = int(entri.get("ulangan_dikenal", 0)) + 1
            self._dikenal[sig] = entri
            return {"signature": sig, "baru": False, "dikenal": entri,
                    "intensitas": round(x, 4), "polaritas": pol,
                    "jenis": entri.get("jenis"),
                    "kategori": entri.get("kategori", entri.get("nama")),
                    "tanpa_tipe": False, "menuntut": False}
        lama = self._aktif.get(sig)
        if lama is not None and lama.hidup and lama.terklaim is None:
            lama.perbarui(x, pol, tick=tick)
            return dict(lama.state(), baru=False)
        if lama is not None and not lama.hidup:
            del self._aktif[sig]
        g = GejalaMurni(x, pol, signature=sig, tick=tick,
                        gejala_id=self._berikut)
        self._berikut += 1
        self._aktif[sig] = g
        self._catat("muncul", g, tick)
        self._pangkas(tick)
        return dict(g.state(), baru=True)

    # ------------------------------------------------------------------
    # 2) gagal-diklaim sebagai state
    # ------------------------------------------------------------------
    @staticmethod
    def kalimat_tanpa_nama() -> str:
        """Mode ``tanpa_nama`` yang digeneralisasi dari felt ke seluruh state.

        Bukan "aku tidak tahu apa yang kurasa", melainkan "aku tidak tahu apa
        yang sedang terjadi padaku".
        """
        return KALIMAT_TAK_BERNAMA

    def gagal(self, tanda: str, tick: int = 0) -> Dict[str, Any]:
        """Tandai bahwa tidak ada modul yang mengklaim; kegagalan itu state."""
        g = self._aktif.get(str(tanda))
        if g is None:
            return {}
        self._catat("gagal_diklaim", g, tick)
        return {"signature": g.signature, "kalimat": self.kalimat_tanpa_nama(),
                "intensitas": round(g.intensitas, 4),
                "polaritas": g.polaritas, "tick": int(tick)}

    # ------------------------------------------------------------------
    # 4) pencalonan kategori (modul yang ada mencoba mengklaim)
    # ------------------------------------------------------------------
    def klaim(self, tanda: str, jenis: str, kategori: Optional[str] = None,
              kuat: float = 0.0, tick: int = 0) -> Dict[str, Any]:
        """Salah satu modul BERHASIL memetakan gejala → ia menjadi state betipe."""
        g = self._aktif.get(str(tanda))
        if g is None or not g.hidup or g.terklaim is not None:
            return {}
        g.tandai_terklaim(jenis, kategori, tick, kuat)
        entri = {"signature": g.signature, "jenis": str(jenis),
                 "kategori": kategori, "kuat": round(float(kuat), 4),
                 "tick": int(tick), "intensitas": round(g.intensitas, 4),
                 "polaritas": g.polaritas}
        self._terklaim.append(entri)
        if len(self._terklaim) > 64:
            del self._terklaim[:-64]
        self._dikenal[g.signature] = dict(entri)
        self._pangkas(tick)
        del self._aktif[g.signature]
        self._catat("terklaim:" + str(jenis), g, tick)
        return entri

    def jenis_hint(self, tanda: str, jenis: str) -> None:
        """Modul yang paling akrab dengan gejala (untuk endapan bila berulang)."""
        g = self._aktif.get(str(tanda))
        if g is not None:
            setattr(g, "_jenis_hint", str(jenis))

    # ------------------------------------------------------------------
    # 5) & 6) pengendapan / pemudaran / konsolidasi
    # ------------------------------------------------------------------
    def proses(self, tick: int = 0) -> Dict[str, Any]:
        """Satu langkah pipeline; mengembalikan KEPUTUSAN untuk diterapkan luar."""
        kini = int(tick)
        endapan: List[Dict[str, Any]] = []
        pemudaran: List[Dict[str, Any]] = []
        konsolidasi: List[Dict[str, Any]] = []
        for sig, g in list(self._aktif.items()):
            if not g.hidup or g.terklaim is not None:
                continue
            if g.ulangan >= self.ambang_ulang:
                jenis = str(getattr(g, "_jenis_hint", "tutur"))
                proto = self._proto.get(sig)
                if proto is None:
                    # Bukti yang sudah terkumpul dibawa serta: proto lahir dari
                    # gejala yang SUDAH berulang, bukan dari satu kemunculan.
                    proto = KategoriProto(sig, jenis=jenis,
                                          intensitas=g.intensitas,
                                          tick=g.tick_lahir)
                    proto.jumlah = int(g.ulangan)
                    proto.tick_terakhir = kini
                    self._proto[sig] = proto
                    self._endapan_count += 1
                    peristiwa = "kategori_proto_lahir"
                else:
                    proto.konfirmasi(g.intensitas, kini)
                    peristiwa = "kategori_proto_bertahan"
                endapan.append(dict(proto.state(), peristiwa=peristiwa,
                                    tick=kini))
                if proto.layak_penuh(kini, self.proto_min_ulang,
                                     self.proto_min_umur) \
                        and sig not in self._penuh:
                    entri = {
                        "signature": sig, "jenis": proto.jenis,
                        "nama": proto.nama, "jumlah": proto.jumlah,
                        "umur": proto.umur(kini),
                        "klaim_identitas": (
                            "pernah mengalami sesuatu yang tidak bisa kujelaskan"),
                        "tick": kini,
                    }
                    self._penuh[sig] = dict(entri)
                    # Kategori penuh juga menjadi "sudah dikenal": perjumpaan
                    # berikutnya bukan lagi gejala murni.
                    self._dikenal[sig] = {"signature": sig,
                                          "jenis": proto.jenis,
                                          "kategori": proto.nama,
                                          "nama": proto.nama,
                                          "kuat": round(min(1.0, proto.jumlah / 8.0), 4),
                                          "penuh": True, "tick": kini}
                    self._konsolidasi_count += 1
                    konsolidasi.append(entri)
                self._catat(peristiwa, g, kini)
                continue
            if kini - g.tick_terakhir >= self.memudar_ticks:
                g.hidup = False
                bekas = {
                    "signature": sig, "catatan": KALIMAT_ADA_SESUATU,
                    "intensitas_puncak": round(g.intensitas, 4),
                    "polaritas": g.polaritas, "ulangan": int(g.ulangan),
                    "tick_lahir": g.tick_lahir, "tick": kini,
                }
                self._bekas.append(dict(bekas))
                if len(self._bekas) > self.max_bekas:
                    del self._bekas[:-self.max_bekas]
                pemudaran.append(bekas)
                self._catat("memudar", g, kini)
                del self._aktif[sig]
        return {"endapan": endapan, "pemudaran": pemudaran,
                "konsolidasi": konsolidasi, "tick": kini}

    def beri_nama(self, tanda: str, nama: Optional[str]) -> Optional[str]:
        """Tutur memberi nama SEMENTARA pada kategori proto (boleh tetap None)."""
        proto = self._proto.get(str(tanda))
        return None if proto is None else proto.beri_nama(nama)

    def bekas(self) -> List[Dict[str, Any]]:
        return [dict(x) for x in self._bekas]

    def kategori_penuh(self) -> List[Dict[str, Any]]:
        return [dict(x) for x in self._penuh.values()]

    def proto(self) -> List[Dict[str, Any]]:
        return [p.state() for p in self._proto.values()]

    def aktif(self) -> List[Dict[str, Any]]:
        return [g.state() for g in self._aktif.values() if g.hidup]

    def terklaim(self) -> List[Dict[str, Any]]:
        return [dict(x) for x in self._terklaim]

    # ------------------------------------------------------------------
    def _catat(self, peristiwa: str, g: GejalaMurni, tick: int) -> None:
        self._log.append({"tick": int(tick), "peristiwa": str(peristiwa),
                          "signature": g.signature,
                          "intensitas": round(g.intensitas, 4),
                          "polaritas": g.polaritas, "ulangan": int(g.ulangan)})
        if len(self._log) > 128:
            del self._log[:-128]

    def _pangkas(self, tick: int) -> None:
        """Batas keras jumlah gejala hidup; yang terlama & terlemah pergi."""
        if len(self._aktif) <= self.max_aktif:
            return
        urut = sorted(self._aktif.values(),
                      key=lambda g: (g.tick_terakhir, g.intensitas))
        for g in urut[:len(self._aktif) - self.max_aktif]:
            g.hidup = False
            self._catat("dipangkas", g, tick)
            del self._aktif[g.signature]
        # Daftar "sudah dikenal" juga dibatasi (tanpa memori tak terbatas).
        if len(self._dikenal) > 128:
            for kunci in list(self._dikenal.keys())[:len(self._dikenal) - 128]:
                self._dikenal.pop(kunci, None)

    def state(self) -> Dict[str, Any]:
        hidup = [g for g in self._aktif.values() if g.hidup]
        return {"aktif": len(hidup),
                "gejala": [g.state() for g in hidup],
                "proto": self.proto(),
                "kategori_penuh": self.kategori_penuh(),
                "bekas": len(self._bekas),
                "dikenal": len(self._dikenal),
                "terakhir": (self._bekas[-1] if self._bekas else None),
                "endapan": self._endapan_count,
                "konsolidasi": self._konsolidasi_count,
                "log": [dict(x) for x in self._log[-8:]]}

    def to_dict(self) -> Dict[str, Any]:
        return {"aktif": {k: v.to_dict() for k, v in self._aktif.items()},
                "proto": {k: v.to_dict() for k, v in self._proto.items()},
                "penuh": {k: dict(v) for k, v in self._penuh.items()},
                "terklaim": [dict(x) for x in self._terklaim],
                "dikenal": {k: dict(v) for k, v in self._dikenal.items()},
                "bekas": [dict(x) for x in self._bekas],
                "log": [dict(x) for x in self._log],
                "berikut": self._berikut,
                "endapan_count": self._endapan_count,
                "konsolidasi_count": self._konsolidasi_count,
                "setelan": {"ambang_ulang": self.ambang_ulang,
                            "proto_min_ulang": self.proto_min_ulang,
                            "proto_min_umur": self.proto_min_umur,
                            "memudar_ticks": self.memudar_ticks}}

    @classmethod
    def from_dict(cls, d: Optional[Mapping[str, Any]]) -> "Gejala":
        setelan = dict((d or {}).get("setelan") or {})
        o = cls(**{k: v for k, v in setelan.items() if v is not None})
        d = d or {}
        o._aktif = {str(k): GejalaMurni.from_dict(v)
                    for k, v in (d.get("aktif") or {}).items()
                    if isinstance(v, Mapping)}
        o._proto = {str(k): KategoriProto.from_dict(v)
                    for k, v in (d.get("proto") or {}).items()
                    if isinstance(v, Mapping)}
        o._penuh = {str(k): dict(v) for k, v in (d.get("penuh") or {}).items()
                    if isinstance(v, Mapping)}
        o._terklaim = [dict(x) for x in (d.get("terklaim") or [])
                       if isinstance(x, Mapping)]
        o._dikenal = {str(k): dict(v) for k, v in (d.get("dikenal") or {}).items()
                      if isinstance(v, Mapping)}
        o._bekas = [dict(x) for x in (d.get("bekas") or [])
                    if isinstance(x, Mapping)]
        o._log = [dict(x) for x in (d.get("log") or [])
                  if isinstance(x, Mapping)]
        o._berikut = int(d.get("berikut", 1) or 1)
        o._endapan_count = int(d.get("endapan_count", 0) or 0)
        o._konsolidasi_count = int(d.get("konsolidasi_count", 0) or 0)
        return o


# =====================================================================
# 0b. INVENSI — pelita STRUKTUR BARU (endogen)
# =====================================================================
# Semua mekanisme di atas MENAMBAH DIMENSI (drive, emosi, lapisan paralel,
# residu, bekas luka, waktu heterogen). Tidak satu pun MENGHASILKAN BENTUK
# BARU: tidak ada yang melahirkan hipotesis baru tentang dunia, rencana baru,
# kategori baru, atau tujuan baru. Gejala mendekati kategori baru tapi selalu
# dari tekan luar; objek yang asing tetap asing, Ia hanya memaklumi.
#
# Invensi menutup celah itu: MESIN GENERATIF ENDOGEN. Bukan rekombinasi, tapi
# delapan operasi yang menghasilkan isi yang belum pernah ada sebagai struktur:
#
#   1. negasi        — "mungkin tidak benar bahwa <keyakinan>" (hipotesis)
#   2. abstraksi     — "secara umum, situasi seperti <inti episode> cenderung
#                       memunculkan <emosi>" (hipotesis)
#   3. analogi       — "<b> dan <c> sejenis dalam konteks <a>" (hipotesis
#                       relasional, jembatan yang belum ada di graf)
#   4. pengisian     — abduksi di balik kekosongan & lubang luka yang belum
#                       bernama: "ada sebab tersembunyi di balik <kosong>",
#                       "yang membuat <ent> tak bisa lagi soal <domain> adalah
#                       peristiwa yang belum kunamai" (hipotesis + tujuan)
#   5. inventori     — menciptakan TUJUUAN BARU dari disonansi, pertentangan
#                       paralel, & rasa ingin tahu (menyelesaikan, memahami,
#                       meredam). Bukan derivasi drive; ini menambah isi.
#   6. konstruksi    — MERENCANAKAN: merangkai langkah (konsep dari graf)
#                       menuju sebuah tujuan, menyisipkan satu langkah
#                       counterfactual yang belum pernah dicoba (rencana)
#   7. pengelompokan — menamai KLUSTER BARU: konsep yang berbagi >=2 tetangga
#                       sama tapi belum terhubung → label kategori baru yang
#                       belum pernah ada (kategori)
#
# Setiap lahir dinilai pada tiga sumbu:
#   • kebaruan   — jarak (1-Jaccard) butirnya ke semua struktur yang sudah ada
#   • koherensi  — proporsi butir yang dikenal (kosakata internal)
#   • utilitas   — relevansi ke drive/emosi yang sedang aktif
# lalu dikristalkan (usul → kristal) bila lolos ambang. Hipotesis yang
# dikristalkan berubah jadi KEYAKINAN NYATA di MesinKepercayaan (bukan
# sekedar daftar kalimat); tujuan/rencana/kategori baru disimpan di sini
# BERSAMA provenance (operasi, tick, skor) — tidak disuntikkan ke Naluri.goals
# yang diturunkan-ulang dari drive setiap tick (rapuh). Invensi bebas impor
# Pycos: ia hanya makan "digest" data-polano + daftar struktur yang ada.
INVENSI_JENIS: Tuple[str, ...] = ("hipotesis", "rencana", "kategori", "tujuan")

_KATA_UMUM = frozenset({
    "aku", "kamu", "dia", "kita", "kami", "mereka", "yang", "dan", "atau",
    "tapi", "karena", "kalau", "jika", "saat", "ketika", "setelah", "sebelum",
    "ini", "itu", "akan", "sudah", "belum", "ada", "tak", "tidak", "bukan",
    "sangat", "sekali", "dengan", "untuk", "pada", "dari", "ke", "di", "juga",
    "lebih", "kurang", "para", "secara", "umum", "seperti", "mungkin", "mirip",
    "bisa", "dapat", "harus", "perlu", "sudah", "lagi", "saja", "hanya"})


class Invensi:
    """Mesin generatif endogen: melahirkan struktur baru dari dalam.

    Ia bekerja di atas sebuah "digest" (data-polano) dari state yang sudah ada:
    drive, emosi, tepi graf asosiasi, keyakinan, disonansi kesadaran,
    kekosongan topologi, lubang luka, kontradiksi lapisan paralel, episode, dan
    tujuan yang ada. Ia TIDAK mengambil tahu isi objek Pycos (bebas impor);
    hanya membandingkan terhadap daftar struktur yang sudah lahir untuk
    mengukur kebaruan. Semua operasi deterministik terhadap seed.
    """

    def __init__(self, seed: int = 0) -> None:
        self.rng = random.Random((int(seed) * 2654435761) & 0x7FFFFFFF)
        self.lahir: List[Dict[str, Any]] = []          # struktur yang pernah lahir
        self._id = 0                                    # penghitung id
        self.riwayat_usul: List[List[str]] = []         # butir usul terbaru (dedup kebaruan)
        self._knop = False                              # knob desainer sudah dipasang?
        # ambang & batas (dapat ditimpa lewat set_knob oleh pemanggil)
        self.ambang_kebaruan = 0.45
        self.ambang_koherensi = 0.12
        self.maks_usul = 6
        self.maks_lahir = 80

    # ---------------- util teks ----------------
    @staticmethod
    def _token(teks: Any) -> List[str]:
        return [w for w in re.findall(r"[a-z0-9]+", str(teks or "").lower())
                if len(w) >= 3 and w not in _KATA_UMUM]

    @staticmethod
    def _jaccard(a: Sequence[str], b: Sequence[str]) -> float:
        sa, sb = set(a), set(b)
        if not sa or not sb:
            return 0.0
        return len(sa & sb) / len(sa | sb)

    def _ada(self) -> List[List[str]]:
        return [s.get("butir", []) for s in self.lahir] + self.riwayat_usul

    def _kebaruan(self, butir: List[str]) -> float:
        if not butir:
            return 0.0
        sim = max((self._jaccard(butir, x) for x in self._ada()), default=0.0)
        return _kclip(1.0 - sim, 0.0, 1.0)

    @staticmethod
    def _koherensi(butir: List[str], kosakata: set) -> float:
        if not butir:
            return 0.0
        return sum(1 for t in butir if t in kosakata) / len(butir)

    @staticmethod
    def _utilitas(butir: List[str], drives: Mapping[str, float],
                  emosi: Mapping[str, float]) -> float:
        bobot: Dict[str, float] = {}
        for d, v in (drives or {}).items():
            for t in re.findall(r"[a-z0-9]+", str(d).lower()):
                bobot[t] = max(bobot.get(t, 0.0), _kclip(float(v), 0.0, 1.0))
        for e, v in (emosi or {}).items():
            bobot[e] = max(bobot.get(e, 0.0), _kclip(float(v), 0.0, 1.0))
        if not butir:
            return 0.0
        return _kclip(sum(bobot.get(t, 0.0) for t in butir) / len(butir), 0.0, 1.0)

    @staticmethod
    def _emosi_teratas(emosi: Mapping[str, float]) -> str:
        if not emosi:
            return ""
        e, v = max(emosi.items(), key=lambda kv: float(kv[1]))
        return e if float(v) > 0.2 else ""

    def _kosakata(self, d: Mapping[str, Any]) -> set:
        k: set = set()
        for a, b, _w in d.get("asosiasi", []):
            k.add(str(a).lower())
            k.add(str(b).lower())
        for key in d.get("keyakinan", []):
            k.update(self._token(key))
        for ep in d.get("episode", []):
            k.update(self._token(ep))
        for x in d.get("konsep", []):
            k.update(self._token(x))
        return k

    # ---------------- operasi generatif ----------------
    def _g_negasi(self, d):
        out = []
        for key in d.get("keyakinan", [])[:4]:
            key = str(key)
            # jangan menegasikan sebuah negasi (hindari dobel-negasi berulang:
            # hipotesis buatan sendiri yang sudah jadi keyakinan nyata)
            if key.startswith("mungkin tidak benar bahwa"):
                continue
            butir = self._token(key)
            if len(butir) < 2:
                continue
            out.append(("hipotesis", "mungkin tidak benar bahwa " + key,
                        "negasi", butir))
        return out

    def _g_abstraksi(self, d):
        out = []
        emo = self._emosi_teratas(d.get("emosi", {}))
        for ep in d.get("episode", [])[:3]:
            butir = self._token(ep)
            if len(butir) < 2:
                continue
            inti = " ".join(butir[:3])
            out.append(("hipotesis",
                        "secara umum, situasi seperti " + inti +
                        " cenderung memunculkan " + (emo or "sesuatu") + " padaku",
                        "abstraksi", butir + ([emo] if emo else [])))
        return out

    def _g_analogi(self, d):
        out = []
        edges = sorted(d.get("asosiasi", []), key=lambda t: -float(t[2]))[:6]
        tetangga: Dict[str, List[Tuple[str, float]]] = {}
        for a, b, w in edges:
            tetangga.setdefault(a, []).append((b, w))
            tetangga.setdefault(b, []).append((a, w))
        pasangan: set = set()
        for a, b, w in edges:
            for c, wc in tetangga.get(a, []):
                if c == b or c == a:
                    continue
                if frozenset((b, c)) in pasangan:   # hindari duplikat terbalik
                    continue
                pasangan.add(frozenset((b, c)))
                butir = self._token(a) + self._token(b) + self._token(c)
                out.append(("hipotesis",
                            "mungkin " + str(b) + " dan " + str(c) +
                            " sejenis dalam konteks " + str(a),
                            "analogi", butir))
        return out

    def _g_pengisian(self, d):
        out = []
        for nama in d.get("kekosongan", [])[:3]:
            butir = self._token(nama)
            out.append(("hipotesis",
                        "ada sebab tersembunyi di balik kekosongan " + str(nama),
                        "pengisian", butir + ["sebab", "tersembunyi"]))
            out.append(("tujuan",
                        "memahami mengapa " + str(nama) + " menjadi kosong",
                        "pengisian", butir + ["memahami", "kosong"]))
        for lub in d.get("lubang", [])[:3]:
            ent, dom = lub.get("ent"), lub.get("domain")
            butir = self._token(ent) + self._token(dom)
            out.append(("hipotesis",
                        "yang membuat " + str(ent) + " tak bisa lagi soal " +
                        str(dom) + " adalah peristiwa yang belum kunamai",
                        "pengisian", butir + ["belum", "namai"]))
            out.append(("tujuan",
                        "menemukan apa yang melukai " + str(ent) + " soal " + str(dom),
                        "pengisian", butir + ["menemukan", "melukai"]))
        return out

    def _g_inventori(self, d):
        out = []
        for kon in d.get("kontradiksi", [])[:3]:
            a, b = kon.get("a"), kon.get("b")
            butir = self._token(a) + self._token(b)
            out.append(("tujuan",
                        "menyelesaikan pertentangan antara '" + str(a) + "' dan '" + str(b) + "'",
                        "inventori", butir + ["menyelesaikan", "pertentangan"]))
        for dis in d.get("dissonance", [])[:3]:
            butir = self._token(dis)
            out.append(("tujuan",
                        "meredam ketegangan seputar " + str(dis),
                        "inventori", butir + ["meredam", "ketegangan"]))
        for a, b, w in sorted(d.get("asosiasi", []), key=lambda t: -float(t[2]))[:3]:
            butir = self._token(a) + self._token(b)
            out.append(("tujuan",
                        "memahami hubungan " + str(a) + " dan " + str(b),
                        "inventori", butir + ["memahami", "hubungan"]))
        return out

    def _g_konstruksi(self, d):
        out = []
        konsep = [c for c in d.get("konsep", [])][:8]
        if not konsep:
            return out
        target = list(d.get("tujuan", []))[:3] + [str(x) for x in d.get("dissonance", [])][:2]
        for t in target:
            butir_t = self._token(t)
            langkah = self.rng.sample(konsep, min(3, len(konsep)))
            inti = butir_t[0] if butir_t else "tujuannya"
            langkah = list(langkah) + ["mencoba jalan tak terduga menuju " + inti]
            isi = "rencana menuju «" + str(t) + "»: " + " → ".join(map(str, langkah))
            butir = butir_t + [self._token(x)[0] if self._token(x) else str(x) for x in langkah]
            out.append(("rencana", isi, "konstruksi", butir))
        return out

    def _g_pengelompokan(self, d):
        out = []
        tetangga: Dict[str, set] = {}
        for a, b, w in d.get("asosiasi", []):
            tetangga.setdefault(a, set()).add(b)
            tetangga.setdefault(b, set()).add(a)
        konsep = list(tetangga.keys())
        for i in range(len(konsep)):
            for j in range(i + 1, len(konsep)):
                a, b = konsep[i], konsep[j]
                bersama = tetangga[a] & tetangga[b]
                if len(bersama) >= 2 and b not in tetangga.get(a, set()):
                    anggota = sorted({a, b} | bersama)[:5]
                    isi = "kategori baru: {" + ", ".join(map(str, anggota)) + "}"
                    butir = [self._token(x)[0] if self._token(x) else str(x) for x in anggota]
                    out.append(("kategori", isi, "pengelompokan", butir))
        return out[:4]

    # ---------------- orkestrasi ----------------
    def lahirkan(self, digest: Mapping[str, Any], tick: int = 0) -> List[Dict[str, Any]]:
        """Hasilkan struktur baru (dinilai & disaring). Kembalikan yang diterima."""
        kandidat: List[Tuple[str, str, str, List[str]]] = []
        for gen in (self._g_negasi, self._g_abstraksi, self._g_analogi,
                    self._g_pengisian, self._g_inventori, self._g_konstruksi,
                    self._g_pengelompokan):
            try:
                kandidat.extend(gen(digest))
            except Exception:
                continue
        kosakata = self._kosakata(digest)
        drives = digest.get("drives", {})
        emosi = digest.get("emosi", {})
        dinilai: List[Dict[str, Any]] = []
        tanda: set = set()
        for jenis, isi, operasi, butir in kandidat:
            butir = list(dict.fromkeys(t for t in butir if t))   # unik, urutan
            if not butir:
                continue
            sig = frozenset(butir)                               # dedup butir (abaikan urutan)
            if sig in tanda:                                     # dedup dalam-batch
                continue
            tanda.add(sig)
            keb = self._kebaruan(butir)
            if keb < 0.30:                                       # terlalu mirip yg ada
                continue
            koh = self._koherensi(butir, kosakata)
            uti = self._utilitas(butir, drives, emosi)
            dinilai.append({"jenis": jenis, "isi": isi, "operasi": operasi,
                            "butir": butir, "kebaruan": round(keb, 3),
                            "koherensi": round(koh, 3), "utilitas": round(uti, 3),
                            "tick": int(tick), "status": "usul"})
        # urutkan dalam tiap jenis: kebaruan dominan, lalu utilitas, lalu koherensi
        dinilai.sort(key=lambda s: (s["kebaruan"], s["utilitas"], s["koherensi"]),
                     reverse=True)
        per: Dict[str, List[Dict[str, Any]]] = {}
        for s in dinilai:
            per.setdefault(s["jenis"], []).append(s)
        # seleksi SEIMBANG lintas jenis (per ronde), maks `batas_per` per jenis
        urut_jenis = sorted(per.keys(), key=lambda j: -per[j][0]["utilitas"])
        batas_per, ronde = 2, 0
        diterima: List[Dict[str, Any]] = []
        while len(diterima) < self.maks_usul:
            tambah = False
            for j in urut_jenis:
                if ronde < len(per[j]) and ronde < batas_per and len(diterima) < self.maks_usul:
                    diterima.append(per[j][ronde])
                    tambah = True
            if not tambah:
                break
            ronde += 1
        for s in diterima:
            self._id += 1
            s["id"] = self._id
            self.lahir.append(s)
            self.riwayat_usul.append(list(s["butir"]))
        if len(self.riwayat_usul) > 64:
            del self.riwayat_usul[:-64]
        if len(self.lahir) > self.maks_lahir:
            del self.lahir[:-self.maks_lahir]
        return diterima

    def kristal(self, tick: int = 0) -> List[Dict[str, Any]]:
        """Naikkan usul → kristal bila lolos ambang. Kembalikan yang naik."""
        naik = []
        for s in self.lahir:
            if s.get("status") != "usul":
                continue
            if s["kebaruan"] >= self.ambang_kebaruan and s["koherensi"] >= self.ambang_koherensi:
                s["status"] = "kristal"
                s["tick_kristal"] = int(tick)
                naik.append(s)
        return naik

    def gugur(self, tick: int = 0, horizon: int = 200) -> None:
        """Usul yang terlalu lama menggantung → gugur (bukan jadi struktur)."""
        for s in self.lahir:
            if s.get("status") == "usul" and int(tick) - int(s.get("tick", 0)) > horizon:
                s["status"] = "gugur"

    def set_knob(self, params: Optional[Mapping[str, Any]]) -> None:
        """Ambil ambang & batas dari parameter desainer (sekali saja)."""
        if self._knop or not params:
            return
        try:
            if "invensi_ambang_kebaruan" in params:
                self.ambang_kebaruan = _kclip(float(params["invensi_ambang_kebaruan"]), 0.0, 1.0)
            if "invensi_ambang_koherensi" in params:
                self.ambang_koherensi = _kclip(float(params["invensi_ambang_koherensi"]), 0.0, 1.0)
            if "invensi_maks_usul" in params:
                self.maks_usul = max(1, int(params["invensi_maks_usul"]))
        except Exception:
            pass
        self._knop = True

    # ---------------- representasi ----------------
    def state(self) -> Dict[str, Any]:
        jumlah = {j: sum(1 for s in self.lahir if s["jenis"] == j) for j in INVENSI_JENIS}
        kristal = [s for s in self.lahir if s.get("status") == "kristal"]
        return {"n_lahir": len(self.lahir), "n_kristal": len(kristal),
                "jenis": jumlah, "kristal": kristal[-8:],
                "terbaru": [s for s in self.lahir][-8:]}

    def ringkas(self) -> Dict[str, Any]:
        return {"n": len(self.lahir),
                "kristal": sum(1 for s in self.lahir if s.get("status") == "kristal"),
                "jenis": {j: sum(1 for s in self.lahir if s["jenis"] == j)
                          for j in INVENSI_JENIS}}

    def to_dict(self) -> Dict[str, Any]:
        return {"lahir": [dict(s) for s in self.lahir], "id": self._id,
                "riwayat_usul": [list(x) for x in self.riwayat_usul]}

    @classmethod
    def from_dict(cls, d: Optional[Mapping[str, Any]], seed: int = 0) -> "Invensi":
        inv = cls(seed=seed)
        if not d:
            return inv
        inv.lahir = [dict(s) for s in d.get("lahir", [])]
        inv._id = int(d.get("id", 0) or 0)
        inv.riwayat_usul = [list(x) for x in d.get("riwayat_usul", [])]
        return inv


# =====================================================================
# 0c. MODEL KAUSAL — menjelaskan "kenapa", bukan sekadar memprediksi
# =====================================================================
# JEJAK menyimpan stimulus→aksi→hasil; predict() mengagregasinya jadi ANGKA
# (korelasi → vektor). Sistem bisa memprediksi, tapi tak bisa MENJELASKAN:
# tak ada rantai sebab yang bisa diartikulasikan, counterfactual tak
# bermakna (tak ada "karena Z"), dan blame menyebar reward proporsional jadi
# tak bisa membedakan "berhasil karena aksiku" dari "berhasil karena
# kebetulan".
#
# ModelKausal menambang episode itu menjadi GRAF KAUASAL bernode+bertepinya:
#   node  : "s:…" situasi/stimulus · "a:…" aksi · "h:…" label-hasil · "d:…" drive
#   tepi  : JENISnya diturunkan dari ujung node —
#             a:→(h:|d:)  "mekanisme"  (aksi MENYEBABKAN akibat) — kausal
#             s:→a:       "pemicu"     (situasi memicu aksi)
#             s:→(h:)     "korelasi"   (situasi berkaitan hasil) — calon KONFOUNDER
# Kuat tepi = perataan eksponensial dari magnitudo bukti (impact/delta), jadi
# stabil & deterministik terhadap urutan episode.
#
# Kemampuan yang lahir dari graf itu:
#   • jelaskan(target)      → rantai sebab mundur (backward chaining) yang
#                             DIARTIKULASI: "X karena A karena S", bukan angka.
#   • counterfactual(s,a)   → "kalau aku a, Y akan terjadi KARENA Z" dengan
#                             mekanisme Z (drive yang digerakkan). Bila tak ada
#                             jalur mekanistis → jujur: "aku tak tahu Z-nya".
#   • blame(s,a,hasil)      → atribusi kausal: diskon konfounder situasi, bedakan
#                             "karena aksiku" dari "kebetulan situasi".
#   • mekanisme(a,b)        → jalur kausal terpendek a→b (BFS) untuk "bagaimana".
# Murni stdlib; tak mengimpor jejak — ia hanya makan daftar episode (digest).
class ModelKausal:
    """Graf kausal yang dijelaskan: rantai sebab, counterfactual bermekanisme,
    dan atribusi blame yang membedakan sebab dari kebetulan."""

    MAKS_TEPI = 4000

    def __init__(self, seed: int = 0) -> None:
        self.rng = random.Random((int(seed) * 40503) & 0x7FFFFFFF)
        self.tepi: Dict[Tuple[str, str], Dict[str, float]] = {}   # (a,b)->{kuat,n}
        self.keluar: Dict[str, Dict[str, int]] = {}               # a -> {b: n}
        self.masuk: Dict[str, Dict[str, int]] = {}                # b -> {a: n}
        self._id = 0

    # ---------------- util ----------------
    @staticmethod
    def _token(teks: Any) -> List[str]:
        return [w for w in re.findall(r"[a-z0-9]+", str(teks or "").lower())
                if len(w) >= 3 and w not in _KATA_UMUM]

    @staticmethod
    def _jenis(a: str, b: str) -> str:
        """Jenis tepi dari prefiks ujung node (membedakan kausal vs korelasi)."""
        if a.startswith("a:"):
            return "mekanisme"                 # aksi → akibat : kausal
        if a.startswith("s:") and b.startswith("a:"):
            return "pemicu"                    # situasi → aksi
        if a.startswith("s:") and b.startswith(("h:", "d:")):
            return "korelasi"                  # situasi → hasil/drive : konfounder?
        return "lain"

    def _tepi(self, a: str, b: str, w: float) -> None:
        if not a or not b or a == b:
            return
        rec = self.tepi.get((a, b))
        if rec is None:
            self.tepi[(a, b)] = {"kuat": _kclip(float(w), 0.0, 1.0), "n": 1.0}
            self.keluar.setdefault(a, {})[b] = 1.0
            self.masuk.setdefault(b, {})[a] = 1.0
        else:
            rec["kuat"] = _kclip(0.75 * rec["kuat"] + 0.25 * float(w), 0.0, 1.0)
            rec["n"] += 1.0
            self.keluar[a][b] += 1.0
            self.masuk[b][a] += 1.0

    def _pangkas(self) -> None:
        if len(self.tepi) <= self.MAKS_TEPI:
            return
        terlemah = sorted(self.tepi.items(), key=lambda kv: kv[1]["kuat"])[
            :len(self.tepi) - self.MAKS_TEPI]
        for (a, b), _ in terlemah:
            self.tepi.pop((a, b), None)
            self.keluar.get(a, {}).pop(b, None)
            self.masuk.get(b, {}).pop(a, None)

    # ---------------- belajar dari episode JEJAK ----------------
    def pelajari(self, episodes: Iterable[Mapping[str, Any]], tick: int = 0) -> Dict[str, Any]:
        """Tambang daftar episode (stimulus, action, impact, drive_deltas, label)."""
        for ep in episodes or []:
            self._pelajari_satu(ep, tick)
        self._pangkas()
        return self.ringkas()

    def _pelajari_satu(self, ep: Mapping[str, Any], tick: int) -> None:
        konsep = list(dict.fromkeys(
            self._token(ep.get("stimulus")) + self._token(ep.get("context"))))
        aksi = str(ep.get("action") or "").strip().lower()
        label = str(ep.get("label") or "").strip()
        impact = abs(_kclip(float(ep.get("impact") or 0.0), -1.0, 1.0))
        deltas = ep.get("drive_deltas") or {}
        a_node = ("a:" + aksi) if aksi else ""
        h_node = ("h:" + label) if label else ""
        for s in konsep:
            s_node = "s:" + s
            if a_node:
                self._tepi(s_node, a_node, 0.6)            # pemicu: situasi → aksi
            if h_node:
                self._tepi(s_node, h_node, 0.4 * impact)   # korelasi: situasi → hasil
        if a_node and h_node:
            self._tepi(a_node, h_node, impact)             # mekanisme: aksi → hasil
        if a_node:
            for d, dv in deltas.items():
                if abs(float(dv)) > 1e-6:
                    self._tepi(a_node, "d:" + str(d), abs(_kclip(float(dv), -1.0, 1.0)))

    # ---------------- kueri kausal ----------------
    def _node(self, target: Any) -> str:
        t = str(target or "").strip().lower()
        if t[:2] in ("s:", "a:", "h:", "d:"):
            return t
        for pref in ("h:", "a:", "s:", "d:"):        # coba node bernama sama
            if (pref + t) in self.masuk or (pref + t) in self.keluar:
                return pref + t
        toks = self._token(t)
        if toks:                                     # cari node yang memuat token
            for pref in ("h:", "a:", "s:", "d:"):
                kandidat = pref + toks[0]
                if kandidat in self.masuk or kandidat in self.keluar:
                    return kandidat
        return t

    def _sebab(self, node: str, jenis: Tuple[str, ...]) -> List[Tuple[float, float, str]]:
        cand = []
        for s in self.masuk.get(node, {}):
            if self._jenis(s, node) in jenis:
                rec = self.tepi[(s, node)]
                cand.append((rec["kuat"], rec["n"], s))
        cand.sort(reverse=True)
        return cand

    @staticmethod
    def _narasi(node: str) -> str:
        if node.startswith("a:"):
            return "aku " + node[2:]
        if node.startswith("h:"):
            return node[2:]
        if node.startswith("d:"):
            return "drive " + node[2:] + " bergerak"
        if node.startswith("s:"):
            return "situasi «" + node[2:] + "»"
        return node

    def jelaskan(self, target: Any, kedalaman: int = 4) -> Dict[str, Any]:
        """Rantai sebab mundur yang diartikulasikan: 'X karena A karena S'."""
        node = self._node(target)
        if node not in self.masuk and node not in self.keluar:
            return {"target": str(target), "rantai": [],
                    "narasi": "aku belum punya model sebab-akibat untuk «%s»." % target}
        rantai, cur = [], node
        for _ in range(max(1, int(kedalaman))):
            sebab = self._sebab(cur, ("mekanisme", "pemicu"))
            if not sebab:
                break
            kuat, n, s = sebab[0]
            rantai.append({"node": s, "kuat": round(kuat, 3), "n": int(n),
                           "jenis": self._jenis(s, cur)})
            cur = s
        if not rantai:
            narasi = "aku tahu «%s» terjadi, tapi aku tak bisa menelusuri sebabnya." % self._narasi(node)
        else:
            narasi = "%s karena %s" % (self._narasi(node),
                                       " karena ".join(self._narasi(r["node"]) for r in rantai))
        return {"target": str(target), "rantai": rantai, "narasi": narasi}

    def counterfactual(self, stimulus: Any, aksi_alt: Any) -> Dict[str, Any]:
        """'Kalau aku <aksi_alt>, <Y> akan terjadi KARENA <Z>' — bermekanisme."""
        a_node = "a:" + str(aksi_alt).strip().lower()
        konsep = self._token(stimulus)
        akibat = sorted(((self.tepi[(a_node, b)]["kuat"], b)
                         for b in self.keluar.get(a_node, {})
                         if self._jenis(a_node, b) == "mekanisme" and b.startswith("h:")),
                        reverse=True)
        dipicu = max((self.tepi.get(("s:" + s, a_node), {}).get("kuat", 0.0) for s in konsep),
                     default=0.0)
        if akibat:
            kuat, b = akibat[0]
            meka = self._mekanisme_dorong(a_node)
            z = meka or self._narasi(b)
            return {"mekanisme": True, "prediksi": self._narasi(b),
                    "kuat": round(kuat, 3), "dipicu": round(dipicu, 3),
                    "narasi": "kalau aku %s, %s akan terjadi karena %s"
                              % (aksi_alt, self._narasi(b), z)}
        return {"mekanisme": False, "prediksi": None, "dipicu": round(dipicu, 3),
                "narasi": "kalau aku %s, aku tak bisa memprediksi akibatnya dengan "
                          "mekanisme — aku belum pernah menguji hubungan itu (tak ada Z)."
                          % aksi_alt}

    def _mekanisme_dorong(self, a_node: str) -> Optional[str]:
        """Mekanisme 'karena Z': drive yang digerakkan aksi (mengapa hasil muncul)."""
        dorong = sorted(((self.tepi[(a_node, d)]["kuat"], d)
                         for d in self.keluar.get(a_node, {}) if d.startswith("d:")),
                        reverse=True)
        return self._narasi(dorong[0][1]) if dorong else None

    def _aksi_ke(self, h_node: str) -> List[float]:
        """Kuat semua aksi ber-mekanisme yang menuju hasil ini (untuk spesifisitas)."""
        return [self.tepi[(s, h_node)]["kuat"] for s in self.masuk.get(h_node, {})
                if self._jenis(s, h_node) == "mekanisme"]

    def blame(self, stimulus: Any, aksi: Any, hasil_label: Any) -> Dict[str, Any]:
        """Atribusi kausal: bedakan 'karena aksiku' dari 'kebetulan situasi'.

        Logika intervensi (bukan sekadar eligibilitas proporsional): aksi A
        menyebabkan O bila A SPESIFIK menuju O — kalau banyak aksi lain di situasi
        yang sama juga menuju O, maka A bukan pembeda dan O lebih karena situasi
        (kebetulan). Konfounder situasi (s→O) menurunkan kredit lebih lanjut.
        """
        a_node = "a:" + str(aksi).strip().lower()
        h_node = "h:" + str(hasil_label).strip().lower()
        sebab_aksi = (self.tepi.get((a_node, h_node), {}).get("kuat", 0.0)
                      if self._jenis(a_node, h_node) == "mekanisme" else 0.0)
        konsep = self._token(stimulus)
        confound = max((self.tepi.get(("s:" + s, h_node), {}).get("kuat", 0.0)
                        for s in konsep if self._jenis("s:" + s, h_node) == "korelasi"),
                       default=0.0)
        semua_aksi = self._aksi_ke(h_node)
        total_aksi = sum(semua_aksi)
        # spesifisitas: porsi O yang khusus lewat aksi ini (1 = hanya aksiku)
        spesifisitas = _kclip(sebab_aksi / total_aksi, 0.0, 1.0) if total_aksi > 1e-9 else 0.0
        kredit = _kclip(spesifisitas * sebab_aksi * (1.0 - 0.5 * confound), 0.0, 1.0)
        if spesifisitas >= 0.5 and sebab_aksi >= confound:
            sebab = "aksi"
            narasi = "%s terutama karena %s — itu aksiku (kredit %.2f)." % (hasil_label, aksi, kredit)
        elif spesifisitas < 0.5:
            sebab = "situasi"
            narasi = ("%s terjadi lewat banyak jalan, bukan khusus aksiku — lebih karena "
                      "situasinya (kebetulan; kredit %.2f)." % (hasil_label, kredit))
        else:
            sebab = "keduanya"
            narasi = "%s dari gabungan aksiku dan situasinya (kredit %.2f)." % (hasil_label, kredit)
        return {"kredit": round(kredit, 3), "sebab": sebab,
                "spesifisitas": round(spesifisitas, 3),
                "sebab_aksi": round(sebab_aksi, 3), "konfounder": round(confound, 3),
                "narasi": narasi}

    def mekanisme(self, a: Any, b: Any, max_langkah: int = 6) -> Dict[str, Any]:
        """Jalur kausal terpendek a→b (BFS) — menjawab 'bagaimana X mengarah ke Y'."""
        awal, tujuan = self._node(a), self._node(b)
        if awal == tujuan:
            return {"jalur": [awal], "narasi": self._narasi(awal)}
        dari = {awal: None}
        antrian = [awal]
        while antrian and len(dari) < 400:
            cur = antrian.pop(0)
            for nxt in self.keluar.get(cur, {}):
                if nxt in dari:
                    continue
                dari[nxt] = cur
                if nxt == tujuan:
                    jalur = [tujuan]
                    while dari[jalur[-1]] is not None:
                        jalur.append(dari[jalur[-1]])
                    jalur.reverse()
                    return {"jalur": jalur,
                            "narasi": " → ".join(self._narasi(x) for x in jalur)}
                antrian.append(nxt)
        return {"jalur": [], "narasi": "aku tak menemukan jalur sebab dari %s ke %s."
                                     % (self._narasi(awal), self._narasi(tujuan))}

    def keyakinan(self, a: Any, b: Any) -> Dict[str, Any]:
        """Keyakinan bahwa a→b kausal (bukan sekadar korelasi)."""
        na, nb = self._node(a), self._node(b)
        rec = self.tepi.get((na, nb))
        if not rec:
            return {"kausal": False, "kuat": 0.0, "jenis": "tak-diketahui"}
        jenis = self._jenis(na, nb)
        kepercayaan = rec["kuat"] * (1.0 if jenis == "mekanisme" else 0.5) \
            * _kclip(rec["n"] / 4.0, 0.2, 1.0)
        return {"kausal": jenis == "mekanisme", "kuat": round(rec["kuat"], 3),
                "n": int(rec["n"]), "jenis": jenis,
                "kepercayaan": round(_kclip(kepercayaan, 0.0, 1.0), 3)}

    # ---------------- representasi ----------------
    def state(self) -> Dict[str, Any]:
        jumlah = {"mekanisme": 0, "pemicu": 0, "korelasi": 0, "lain": 0}
        for (a, b) in self.tepi:
            jumlah[self._jenis(a, b)] += 1
        terkuat = sorted(self.tepi.items(), key=lambda kv: -kv[1]["kuat"])[:8]
        return {"n_tepi": len(self.tepi), "jenis": jumlah,
                "terkuat": [{"a": a, "b": b, "jenis": self._jenis(a, b),
                             "kuat": round(rec["kuat"], 3), "n": int(rec["n"])}
                            for (a, b), rec in terkuat]}

    def ringkas(self) -> Dict[str, Any]:
        return {"tepi": len(self.tepi), "node": len(set(self.keluar) | set(self.masuk))}

    def to_dict(self) -> Dict[str, Any]:
        return {"tepi": {f"{a}\x1f{b}": dict(rec) for (a, b), rec in self.tepi.items()},
                "id": self._id}

    @classmethod
    def from_dict(cls, d: Optional[Mapping[str, Any]], seed: int = 0) -> "ModelKausal":
        m = cls(seed=seed)
        if not d:
            return m
        for kunci, rec in (d.get("tepi", {}) or {}).items():
            a, _, b = kunci.partition("\x1f")
            if not a or not b:
                continue
            m.tepi[(a, b)] = {"kuat": float(rec.get("kuat", 0.0)), "n": float(rec.get("n", 1.0))}
            m.keluar.setdefault(a, {})[b] = float(rec.get("n", 1.0))
            m.masuk.setdefault(b, {})[a] = float(rec.get("n", 1.0))
        m._id = int(d.get("id", 0) or 0)
        return m


# =====================================================================
# 0d. PERENCANA — perencanaan multi-tingkat + META-PLANNING
# =====================================================================
# Goal.subgoals ada, tapi hanya SATU tingkat: satu lompatan. Tak ada means-end
# analysis, tak ada forward/backward chaining, tak ada dekomposisi rekursif.
# Manusia merencanakan 4–6 lompatan ("butuh makanan" → "ke pasar" → "tahu
# letaknya" → "bertanya"), dan justru di kedalaman itu kesadaran paling terasa
# — bukan karena sadar, tapi karena tahu bahwa kita SEDANG merencanakan
# (meta-planning).
#
# Perencana memakai ModelKausal sebagai MODEL DOMAIN:
#   • backward chaining : goal (h:) → aksi yang mencapainya (a:→h: mekanisme)
#   • precond           : situasi pemicu aksi (s:→a:) yang belum menjadi fakta
#   • rekursi           : precond tak terpenuhi → subgoal → dekomposisi lagi
#   • forward chaining  : dari fakta, terapkan aksi yang precond-nya terpenuhi
#   • meta-planning     : memutuskan STRATEGI & ANGGARAN KEDALAMAN dulu, lalu
#                         melaporkan "aku sadar aku sedang merencanakan".
# Berhenti saat precond = fakta, kedalaman maksimum, atau siklus (buntu).
class Perencana:
    """Perencana means-end rekursif dengan backward/forward chaining &
    meta-planning; bertumpu pada graf kausal sebagai model domain."""

    def __init__(self, seed: int = 0) -> None:
        self.rng = random.Random((int(seed) * 2246822519) & 0x7FFFFFFF)
        self.rencana_aktif: Optional[Dict[str, Any]] = None
        self.jejak_rencana: List[Dict[str, Any]] = []
        self._id = 0

    # ---------------- util ----------------
    @staticmethod
    def _fakta(node: str, fakta: Iterable[str]) -> bool:
        f = set(fakta or [])
        bare = node.split(":", 1)[-1]
        return node in f or bare in f or ("s:" + bare) in f

    def _aksi_capai(self, node: str, domain: Any) -> List[Tuple[float, str]]:
        """Aksi ber-mekanisme yang mencapai `node`, terkuat dulu (backward)."""
        keluar = [(domain.tepi[(a, node)]["kuat"], a)
                  for a in domain.masuk.get(node, {})
                  if domain._jenis(a, node) == "mekanisme"]
        keluar.sort(reverse=True)
        return keluar

    def _pemicu(self, a_node: str, domain: Any) -> List[str]:
        return [s for s in domain.masuk.get(a_node, {})
                if domain._jenis(s, a_node) == "pemicu"]

    # ---------------- backward chaining (means-end rekursif) ----------------
    def _mundur(self, tujuan: Any, domain: Any, fakta: Iterable[str],
                max_dalam: int, dalam: int, jalur: frozenset) -> Dict[str, Any]:
        node = domain._node(tujuan)
        if self._fakta(node, fakta):
            return {"tujuan": node, "jenis": "fakta", "aksi": None, "pra": [],
                    "lengkap": True, "dalam": dalam}
        if dalam >= max_dalam:
            return {"tujuan": node, "jenis": "buntu", "aksi": None, "pra": [],
                    "lengkap": False, "alasan": "kedalaman", "dalam": dalam}
        if node in jalur:
            return {"tujuan": node, "jenis": "buntu", "aksi": None, "pra": [],
                    "lengkap": False, "alasan": "siklus", "dalam": dalam}
        aksis = self._aksi_capai(node, domain)
        if not aksis:
            return {"tujuan": node, "jenis": "buntu", "aksi": None, "pra": [],
                    "lengkap": False, "alasan": "tak ada aksi", "dalam": dalam}
        kuat, a = aksis[0]
        pra_belum = [s for s in self._pemicu(a, domain) if not self._fakta(s, fakta)]
        pra_rencana: List[Dict[str, Any]] = []
        if pra_belum:
            # SATU cabang precond: capai outcome yang menutupi token terbanyak
            h = self._outcome_penutup(pra_belum, domain)
            if h is not None:
                sub = self._mundur(h, domain, fakta, max_dalam, dalam + 1, jalur | {node})
                pra_rencana.append({"tujuan": "pra:" + a, "jenis": "pra",
                                    "perlu": [s.split(":", 1)[-1] for s in pra_belum],
                                    "via": h, "pra": [sub], "lengkap": sub["lengkap"],
                                    "dalam": dalam})
            else:
                pra_rencana.append({"tujuan": "pra:" + a, "jenis": "buntu",
                                    "perlu": [s.split(":", 1)[-1] for s in pra_belum],
                                    "aksi": None, "pra": [], "lengkap": False,
                                    "alasan": "precond tak terjangka", "dalam": dalam})
        return {"tujuan": node, "jenis": "aksi", "aksi": a, "kuat": round(kuat, 3),
                "pra": pra_rencana, "lengkap": all(p["lengkap"] for p in pra_rencana),
                "dalam": dalam}

    def _outcome_penutup(self, tokens: Iterable[str], domain: Any) -> Optional[str]:
        """Outcome (h:) terjangka yang token-nya paling menutupi token precond."""
        need = {w for t in tokens for w in re.findall(r"[a-z0-9]+", t.split(":", 1)[-1].lower())}
        semua_h = sorted(n for n in (set(domain.masuk) | set(domain.keluar)) if n.startswith("h:"))
        terbaik, skor_terbaik = None, 0
        for h in semua_h:
            if not self._aksi_capai(h, domain):        # harus bisa dicapai sebuah aksi
                continue
            htok = set(re.findall(r"[a-z0-9]+", h[2:].lower()))
            skor = len(need & htok)
            if skor > skor_terbaik:
                terbaik, skor_terbaik = h, skor
        return terbaik

    # ---------------- forward chaining ----------------
    def maju(self, tujuan: Any, domain: Any, fakta: Iterable[str],
             max_langkah: int = 12) -> Dict[str, Any]:
        """Dari fakta, terapkan aksi yang precond-nya penuh sampai tujuan tercapai."""
        node = domain._node(tujuan)
        punya = set(fakta or [])
        langkah, dilihat = [], set()
        for _ in range(max_langkah):
            if self._fakta(node, punya):
                return {"tercapai": True, "langkah": langkah, "fakta": sorted(punya)}
            # aksi yang bisa dijalankan: semua pemicu-nya sudah fakta
            bisa = []
            for a in domain.keluar:
                if a in dilihat or not a.startswith("a:"):
                    continue
                pemicu = self._pemicu(a, domain)
                if pemicu and all(self._fakta(s, punya) for s in pemicu):
                    maju_ke = [b for b in domain.keluar.get(a, {})
                               if domain._jenis(a, b) == "mekanisme"]
                    bisa.append((len(maju_ke), a, maju_ke))
            if not bisa:
                break
            bisa.sort(reverse=True)
            _, a, maju_ke = bisa[0]
            dilihat.add(a)
            langkah.append(a)
            for b in maju_ke:
                punya.add(b)
        return {"tercapai": self._fakta(node, punya), "langkah": langkah,
                "fakta": sorted(punya)}

    # ---------------- meta-planning ----------------
    def _kompleksitas(self, tujuan: Any, domain: Any, horizon: int = 3) -> float:
        """Perkiraan kompleksitas: banyaknya aksi dalam cakram menuju tujuan."""
        node = domain._node(tujuan)
        kenal, batas = {node}, 0
        for _ in range(horizon):
            baru = set()
            for x in list(kenal):
                for s in domain.masuk.get(x, {}):
                    if domain._jenis(s, x) == "mekanisme" and s not in kenal:
                        baru.add(s)
                for b in domain.keluar.get(x, {}):
                    if domain._jenis(x, b) == "mekanisme" and b not in kenal:
                        baru.add(b)
            kenal |= baru
            batas += len(baru)
            if batas > 40:
                break
        return _kclip(batas / 24.0, 0.0, 1.0)

    def rencanakan_rencana(self, tujuan: Any, domain: Any, fakta: Iterable[str]
                           ) -> Dict[str, Any]:
        """META-PLAN: putuskan strategi & anggaran kedalaman, lalu rancang."""
        kompleksitas = self._kompleksitas(tujuan, domain)
        anggaran = 5 if kompleksitas < 0.4 else (6 if kompleksitas < 0.75 else 8)
        uji = self.maju(tujuan, domain, fakta)
        arah = "maju" if uji.get("tercapai") else "mundur"
        pohon = self.rancang(tujuan, domain, fakta, max_kedalaman=anggaran, arah=arah)
        buntu = self._buntu(pohon["akar"])
        meta = {"strategi": arah, "anggaran_kedalaman": anggaran,
                "kompleksitas": round(kompleksitas, 2),
                "kedalaman_tercapai": pohon["kedalaman"], "cabang_buntu": buntu,
                "sadar_merencanakan": True,
                "catatan": ("aku memutuskan merencanakan «%s» dengan chaining %s sampai "
                            "kedalaman %d; aku sadar aku sedang merencanakan."
                            % (tujuan, arah, anggaran))}
        return {"pohon": pohon, "meta": meta}

    # ---------------- orkestrasi & narasi ----------------
    def rancang(self, tujuan: Any, domain: Any, fakta: Iterable[str],
                max_kedalaman: int = 5, arah: str = "mundur") -> Dict[str, Any]:
        self._id += 1
        akar = self._mundur(tujuan, domain, fakta, max_kedalaman, 0, frozenset())
        pohon = {"id": self._id, "tujuan": str(tujuan), "arah": arah,
                 "akar": akar, "kedalaman": self._kedalaman(akar),
                 "lengkap": akar["lengkap"]}
        self.rencana_aktif = pohon
        self.jejak_rencana.append({"id": self._id, "tujuan": str(tujuan),
                                   "kedalaman": pohon["kedalaman"],
                                   "lengkap": akar["lengkap"]})
        if len(self.jejak_rencana) > 40:
            del self.jejak_rencana[:-40]
        return pohon

    def _kedalaman(self, node: Dict[str, Any]) -> int:
        if not node.get("pra"):
            return 0
        return 1 + max(self._kedalaman(p) for p in node["pra"])

    def _buntu(self, node: Dict[str, Any]) -> List[str]:
        keluar = []
        if node.get("jenis") == "buntu":
            keluar.append(self._buntu_label(node))
        for p in node.get("pra", []):
            keluar.extend(self._buntu(p))
        return keluar

    @staticmethod
    def _buntu_label(node: Mapping[str, Any]) -> str:
        return "%s (%s)" % (node.get("tujuan", "?"), node.get("alasan", "buntu"))

    def langkah(self, node: Optional[Dict[str, Any]] = None) -> List[str]:
        """Ratakan pohon jadi urutan aksi (daun fakta = precond sudah ada)."""
        if node is None:
            node = (self.rencana_aktif or {}).get("akar")
        keluar: List[str] = []
        if not node:
            return keluar
        for p in node.get("pra", []):
            keluar.extend(self.langkah(p))
        if node.get("jenis") == "aksi" and node.get("aksi"):
            keluar.append(node["aksi"])
        return keluar

    def narasi(self, node: Optional[Dict[str, Any]] = None, domain: Any = None,
               indent: int = 0) -> str:
        """Narasi multi-tingkat rencana (menunjukkan dekomposisi rekursif)."""
        if node is None:
            node = (self.rencana_aktif or {}).get("akar")
        if not node:
            return ""
        pad = "  " * indent
        if node["jenis"] == "fakta":
            nama = domain._narasi(node["tujuan"]) if domain is not None else node["tujuan"]
            return "%s• %s — sudah ada.\n" % (pad, nama)
        if node["jenis"] == "buntu":
            nama = domain._narasi(node["tujuan"]) if domain is not None else node["tujuan"]
            return "%s• %s — BUNTU (%s).\n" % (pad, nama, node.get("alasan", "?"))
        if node["jenis"] == "pra":
            perlu = " ".join(node.get("perlu", []))
            via = domain._narasi(node["via"]) if domain is not None else node.get("via", "")
            baris = "%s◦ untuk itu aku perlu %s → aku usahakan %s\n" % (pad, perlu, via)
            for p in node.get("pra", []):
                baris += self.narasi(p, domain, indent + 1)
            return baris
        nama = domain._narasi(node["tujuan"]) if domain is not None else node["tujuan"]
        aksi_narasi = domain._narasi(node["aksi"]) if domain is not None else node["aksi"]
        baris = "%s→ untuk %s: %s\n" % (pad, nama, aksi_narasi)
        for p in node.get("pra", []):
            baris += self.narasi(p, domain, indent + 1)
        return baris

    # ---------------- representasi ----------------
    def state(self) -> Dict[str, Any]:
        aktif = self.rencana_aktif or {}
        return {"rencana_aktif": aktif.get("tujuan"),
                "kedalaman": aktif.get("kedalaman", 0),
                "lengkap": aktif.get("lengkap"),
                "langkah": self.langkah(aktif.get("akar")) if aktif else [],
                "n_rencana": len(self.jejak_rencana)}

    def ringkas(self) -> Dict[str, Any]:
        return {"n_rencana": len(self.jejak_rencana),
                "terakhir": (self.jejak_rencana[-1] if self.jejak_rencana else None)}

    def to_dict(self) -> Dict[str, Any]:
        return {"rencana_aktif": self.rencana_aktif, "jejak": list(self.jejak_rencana),
                "id": self._id}

    @classmethod
    def from_dict(cls, d: Optional[Mapping[str, Any]], seed: int = 0) -> "Perencana":
        p = cls(seed=seed)
        if not d:
            return p
        p.rencana_aktif = d.get("rencana_aktif")
        p.jejak_rencana = list(d.get("jejak", []))
        p._id = int(d.get("id", 0) or 0)
        return p


# =====================================================================
# WADAH
# =====================================================================
class Organik:
    """Wadah mekanisme state organik, termasuk jam dan bekas non-decay."""

    def __init__(self, seed: int = 0) -> None:
        self.rng = random.Random(int(seed) & 0xFFFFFFFF)
        self.topologi = TopologiSlot()
        self.luka = LukaDomain()
        self.identitas = BatasIdentitas()
        self.waktu = WaktuHeterogen()
        self.tutur = PenolakanTutur()
        self.apersepsi = Apersepsi()
        self.paralel = LapisanParalel()
        self.tubuh = TubuhSumber()
        self.residu = Residu()
        self.intrusi = Intrusi()
        self.detak = DetakInternal(self.rng)
        self.vacancy = Vacancy()
        # Orde nol: bahan mentah dari mana kategori baru bisa mengkristal.
        self.gejala = Gejala()
        # Pelita endogen: melahirkan struktur baru (hipotesis/rencana/kategori/tujuan).
        self.invensi = Invensi()
        # Model kausal: menjelaskan "kenapa" (rantai sebab, counterfactual, blame).
        self.kausal = ModelKausal()
        # Perencana multi-tingkat + meta-planning (means-end, chaining, dekomposisi).
        self.perencana = Perencana()

    # ---------- ringkasan diagnostik ----------
    def ringkas(self) -> Dict[str, Any]:
        return {"slot_kosong": self.topologi.kosong(),
                "slot_total": len(self.topologi.semua()),
                "lubang": self.luka.ringkas(),
                "identitas": self.identitas.state(),
                "waktu": self.waktu.ringkas(),
                "penolakan_tutur": len(self.tutur.riwayat()),
                "lapisan_paralel": self.paralel.state(),
                "tubuh_tegang": round(self.tubuh.tegang, 4),
                "residu": self.residu.state(),
                "intrusi": self.intrusi.state(),
                "detak_internal": self.detak.state(),
                "vacancy": self.vacancy.state(),
                "gejala": self.gejala.state(),
                "invensi": self.invensi.state(),
                "kausal": self.kausal.state(),
                "perencana": self.perencana.state()}

    def to_dict(self) -> Dict[str, Any]:
        st = self.rng.getstate()
        return {"rng_state": [int(st[0]), [int(x) for x in st[1]], st[2]],
                "topologi": self.topologi.to_dict(),
                "luka": self.luka.to_dict(),
                "identitas": self.identitas.to_dict(),
                "waktu": self.waktu.to_dict(),
                "tutur": self.tutur.to_dict(),
                "apersepsi": self.apersepsi.to_dict(),
                "paralel": self.paralel.to_dict(),
                "tubuh": self.tubuh.to_dict(),
                "residu": self.residu.to_dict(),
                "intrusi": self.intrusi.to_dict(),
                "detak": self.detak.to_dict(),
                "vacancy": self.vacancy.to_dict(),
                "gejala": self.gejala.to_dict(),
                "invensi": self.invensi.to_dict(),
                "kausal": self.kausal.to_dict(),
                "perencana": self.perencana.to_dict()}

    @classmethod
    def from_dict(cls, d: Optional[Mapping[str, Any]], seed: int = 0) -> "Organik":
        o = cls(seed=seed)
        if isinstance(d, Mapping):
            rs = d.get("rng_state")
            if rs and len(rs) == 3 and rs[1]:
                try:
                    o.rng.setstate((int(rs[0]), tuple(int(x) for x in rs[1]), rs[2]))
                except (TypeError, ValueError):
                    pass
            o.topologi = TopologiSlot.from_dict(d.get("topologi"))
            o.luka = LukaDomain.from_dict(d.get("luka"))
            o.identitas = BatasIdentitas.from_dict(d.get("identitas"))
            o.waktu = WaktuHeterogen.from_dict(d.get("waktu"))
            o.tutur = PenolakanTutur.from_dict(d.get("tutur"))
            o.apersepsi = Apersepsi.from_dict(d.get("apersepsi"))
            o.paralel = LapisanParalel.from_dict(d.get("paralel"))
            o.tubuh = TubuhSumber.from_dict(d.get("tubuh"))
            o.residu = Residu.from_dict(d.get("residu"))
            o.intrusi = Intrusi.from_dict(d.get("intrusi"))
            o.detak = DetakInternal.from_dict(d.get("detak"))
            o.vacancy = Vacancy.from_dict(d.get("vacancy"))
            o.gejala = Gejala.from_dict(d.get("gejala"))
            o.invensi = Invensi.from_dict(d.get("invensi"))
            o.kausal = ModelKausal.from_dict(d.get("kausal"))
            o.perencana = Perencana.from_dict(d.get("perencana"))
        return o


# =====================================================================
# UJI-DIRI
# =====================================================================
if __name__ == "__main__":
    print("=== pycos.mandiri.organik — uji-diri lima mekanisme ===")

    # 1. topologis
    t = TopologiSlot()
    t.daftar("Ayu", {"peran": "sahabat"})
    assert t.intensitas("Ayu", 0.03) == 0.03
    t.kosongkan("Ayu", alasan="meninggal", tick=100)
    assert t.intensitas("Ayu", 0.03) is None, "slot kosong harus None, bukan 0.0"
    assert t.cabang_mustahil("besok aku pergi ke pasar bersama Ayu") == ["Ayu"]
    assert t.layak_cabang("Ayu") is False
    print("1. TOPOLOGIS: intensitas kosong =", t.intensitas("Ayu"), "| cabang mustahil:",
          t.cabang_mustahil("besok aku pergi ke pasar bersama Ayu"))

    # 2. luka domain
    lk = LukaDomain()
    lk.lukai("Budi", "uang", alasan="ia menipuku soal utang", tick=50)
    assert lk.terapkan("Budi", "uang", 0.9) is None
    assert lk.terapkan("Budi", "kesehatan", 0.9) == 0.9
    assert lk.tambal("Budi", "uang") is False, "lubang permanen tak bisa ditambal"
    print("2. LUKA DOMAIN: uang =", lk.terapkan("Budi", "uang", 0.9),
          "| kesehatan =", lk.terapkan("Budi", "kesehatan", 0.9),
          "| tambal =", lk.tambal("Budi", "uang"))

    # 3. identitas
    bi = BatasIdentitas()
    bi.tetapkan("aku orang yang tidak percaya siapa pun",
                {"senang": ("tolak_bila_bertentangan", 0.0),
                 "percaya": ("langit", 0.15)})
    assert bi.izinkan("senang", 0.8, bertentangan=True)[0] is False
    assert bi.izinkan("senang", 0.8, bertentangan=False)[0] is True
    ok, jml, _ = bi.izinkan("percaya", 0.9)
    assert ok and abs(jml - 0.15) < 1e-9
    print("3. IDENTITAS: senang(bertentangan) =", bi.izinkan("senang", 0.8, True)[:2],
          "| percaya dipotong →", bi.izinkan("percaya", 0.9)[1])

    # 4. waktu heterogen
    w = WaktuHeterogen(dasar=600.0)
    w.daftar("ep1"); w.daftar("ep2")
    for _ in range(4):
        w.diingat("ep1")
    for _ in range(4):
        w.dikoreksi_salah("ep2")
    assert w.half_life("ep1") > 600.0 > w.half_life("ep2")
    print("4. WAKTU: ep1(sering diingat) =", round(w.half_life("ep1"), 1),
          "| ep2(sering salah) =", round(w.half_life("ep2"), 1))

    # 5. penolakan tutur
    p = PenolakanTutur(ambang=0.45)
    tenang, _ = p.kelayakan({"arousal": 0.2, "takut": 0.1, "koherensi": 1.0})
    panik, komp = p.kelayakan({"arousal": 0.95, "takut": 0.9, "malu": 0.8,
                               "koherensi": 0.2, "duka": 0.8,
                               "batas_identitas": True})
    assert tenang > 0.9 and panik < 0.1
    print("5. TUTUR: kelayakan tenang =", round(tenang, 3),
          "| panik =", round(panik, 3), "| bentuk tertahan:", repr(p.bentuk("aku mencintaimu")))

    # 6. apersepsi: sistem boleh gagal menamai
    ap = Apersepsi()
    kosong = ap.amati({"tegang": 0.01, "mual": 0.0, "nyeri": 0.0})
    kabut = ap.amati({"tegang": 0.30, "mual": 0.28, "nyeri": 0.26, "sesak": 0.27})
    jelas = ap.amati({"tegang": 0.90, "mual": 0.01})
    assert kosong["modus"] == "kosong" and kosong["nama"] is None
    assert kabut["modus"] in ("kabut", "tanpa_nama", "gradien"), kabut
    assert jelas["modus"] == "jelas" and jelas["nama"] == "tegang"
    assert kosong["kalimat"] and kabut["kalimat"]
    print("6. APERSEPSI: kosong =", kosong["modus"], "| kabut =", kabut["modus"],
          "|", repr(kabut["kalimat"]), "| jelas =", jelas["nama"])

    # 7. lapisan paralel: dua keyakinan bertentangan, tanpa resolusi
    lp = LapisanParalel()
    a = lp.tambah("aku mencintai anakku", 0.7, {"senang": 0.6}, konteks="rumah")
    b = lp.tambah("kadang aku ingin dia hilang", 0.5, {"senang": -0.5, "marah": 0.3},
                  konteks="lelah")
    lp.tambah("dan aku tetap mencintainya", 0.6, {"senang": 0.4}, lawan_dari=b["id"])
    assert lp.disonansi_paralel() == 0.0
    assert lp.tanpa_resolusi() is True
    assert lp.bertentangan(), "harus terdeteksi bertentangan"
    assert lp.bertindak_dari("aku sedang di rumah")["klaim"] == "aku mencintai anakku"
    assert lp.bertindak_dari("aku sedang lelah")["klaim"] == "kadang aku ingin dia hilang"
    print("7. PARALEL: pasangan bertentangan =", len(lp.bertentangan()),
          "| disonansi =", lp.disonansi_paralel(), "| tanpa resolusi =", lp.tanpa_resolusi())

    # 8. tubuh sumber: mendahului kognisi
    tb = TubuhSumber()
    assert tb.langkah({}, {}, {}) == {}
    tb.suntik(0.9)
    lead = tb.tegang
    d = tb.langkah({"tegang": 0.8}, {}, {})
    assert lead > 0.3 and d, (lead, d)
    print("8. TUBUH: suntik -> tegang =", round(lead, 3),
          "| mendorong drive =", d)

    # taksonomi penolakan
    pt = PenolakanTutur()
    peta = {"takut": {"takut": 1.0}, "malu": {"malu": 1.0},
            "disosiasi": {"koherensi": 0.0}, "duka": {"duka": 0.8},
            "arousal": {"arousal": 0.95}, "identitas": {"batas_identitas": True}}
    for sebab, konteks in peta.items():
        _, komp = pt.kelayakan(konteks)
        assert pt.jenis(komp) == sebab, (sebab, pt.jenis(komp), komp)
        bentuk = pt.bentuk("aku mencintaimu", komponen=komp)
        assert bentuk is not None
        print("   penolakan", sebab, "->", repr(bentuk),
              "(", pt.jenis_penolakan(komp), ")")

    # wadah + roundtrip
    # 0. gejala murni: state orde nol → kategori proto → kategori penuh
    ge = Gejala(ambang_ulang=2, proto_min_ulang=3, proto_min_umur=5,
                memudar_ticks=3)
    g0 = ge.muncul(0.7, None, tanda="tanda-asing", tick=0)
    assert g0["tanpa_tipe"] is True and g0["polaritas"] is None
    assert g0["menuntut"] is True and g0["tekanan"] > 0.0
    assert g0["tidak_dimiliki"] == {"durasi": None, "isi": None,
                                    "sebab": None, "tujuan": None}
    hidup = ge._aktif["tanda-asing"]
    assert hidup.properti_terlarang() == [], hidup.properti_terlarang()
    ge.jenis_hint("tanda-asing", "emosi")
    ge.proses(tick=1)                       # sekali: belum apa-apa
    ge.muncul(0.8, -0.3, tanda="tanda-asing", tick=2)
    ge.muncul(0.6, None, tanda="tanda-asing", tick=3)
    keputusan = ge.proses(tick=4)
    assert keputusan["endapan"] and keputusan["endapan"][0]["jumlah"] == 3
    assert ge.kategori_penuh() == []        # belum bertahan cukup lama
    ge.proses(tick=6)                       # ulangan + umur terpenuhi
    penuh = ge.kategori_penuh()
    assert penuh and penuh[0]["jenis"] == "emosi"
    assert "tidak bisa kujelaskan" in penuh[0]["klaim_identitas"]
    print("0. GEJALA: murni =", {k: g0[k] for k in ("intensitas", "polaritas",
                                                    "tanpa_tipe", "menuntut")},
          "| proto → penuh =", penuh[0]["signature"], penuh[0]["jenis"])

    # gejala yang tak berulang memudar, tetapi meninggalkan BEKAS (bukan entri)
    ge.muncul(0.5, None, tanda="tanda-sekilas", tick=10)
    mudar = ge.proses(tick=20)
    assert mudar["pemudaran"], mudar
    assert ge.bekas()[-1]["catatan"] == KALIMAT_ADA_SESUATU
    r_uji = Residu()
    r_uji.bekas("gejala", KALIMAT_ADA_SESUATU, tick=20,
                signature="tanda-sekilas", intensitas_puncak=0.5)
    assert r_uji.tekanan() == 0.0, "bekas bukan entri aktif"
    assert r_uji.bekas_state()[-1]["signature"] == "tanda-sekilas"

    # klaim: begitu ada modul yang cocok, gejala tidak lagi murni/baru
    ge.muncul(0.9, 0.4, tanda="tanda-kenal", tick=30)
    klaim = ge.klaim("tanda-kenal", "drive", "keamanan", kuat=0.8, tick=31)
    assert klaim and ge._aktif.get("tanda-kenal") is None
    print("   BEKAS:", r_uji.bekas_state()[-1]["catatan"], "| KLAIM:",
          klaim["jenis"], "→", klaim["kategori"])

    # 0b. INVENSI: pelita endogen — melahirkan struktur baru dari dalam
    inv = Invensi(seed=7)
    _dg = {
        "drives": {"curiosity": 0.8, "social": 0.4},
        "emosi": {"penasaran": 0.6},
        "asosiasi": [("gajah", "besar", 0.5), ("gajah", "abu", 0.5),
                     ("badak", "besar", 0.5), ("badak", "abu", 0.5)],
        "keyakinan": ["manusia pada dasarnya egois", "dunia ini adil"],
        "dissonance": ["aku ingin dekat tapi aku takut terluka"],
        "kekosongan": ["teman lama"],
        "lubang": [{"ent": "ibu", "domain": "suara"}],
        "kontradiksi": [{"a": "aku percaya keadilan", "b": "dunia tidak adil"}],
        "episode": ["aku dimarahi bos di depan rekan kerja"],
        "konsep": ["gajah", "badak", "besar", "abu"],
        "tujuan": ["mencari penerimaan"],
    }
    _lahir = inv.lahirkan(_dg, tick=1)
    _jenis = {j: sum(1 for s in _lahir if s["jenis"] == j) for j in INVENSI_JENIS}
    _kris = inv.kristal(tick=2)
    assert _lahir and all(s["kebaruan"] >= 0.30 for s in _lahir)
    assert _kris and all(s["status"] == "kristal" for s in _kris)
    _inv2 = Invensi.from_dict(inv.to_dict(), seed=7)
    assert [s["isi"] for s in _inv2.lahir] == [s["isi"] for s in inv.lahir]
    print("0b. INVENSI: lahir =", len(_lahir), _jenis, "| kristal =", len(_kris),
          "| contoh:", _lahir[0]["isi"][:60])

    # 0c. MODEL KAUSAL: menjelaskan "kenapa", counterfactual bermekanisme, blame
    mk = ModelKausal(seed=1)
    _eps = []
    for _ in range(4):
        _eps.append({"stimulus": "api menyala di dapur", "action": "menyentuh api",
                     "impact": -0.9, "drive_deltas": {"keamanan": -0.8},
                     "label": "kulit terbakar", "context": "dapur"})
    for _act in ("diam di rumah", "menutup jendela", "perkuat atap"):
        for _ in range(3):
            _eps.append({"stimulus": "badai besar malam ini", "action": _act,
                         "impact": -0.7, "drive_deltas": {"keamanan": -0.5},
                         "label": "rumah rusak", "context": "malam"})
    mk.pelajari(_eps)
    _jel = mk.jelaskan("kulit terbakar")["narasi"]
    _cf = mk.counterfactual("api di dapur", "menyentuh api")
    _cf_x = mk.counterfactual("api di dapur", "menari")
    _b_api = mk.blame("api di dapur", "menyentuh api", "kulit terbakar")
    _b_badai = mk.blame("badai besar", "diam di rumah", "rumah rusak")
    assert _cf["mekanisme"] and "karena" in _cf["narasi"]        # counterfactual bermekanisme
    assert not _cf_x["mekanisme"]                                 # tak diuji -> jujur tak ada Z
    assert _b_api["sebab"] == "aksi" and _b_api["kredit"] > 0.5   # aksiku sebabnya
    assert _b_badai["sebab"] == "situasi" and _b_badai["kredit"] < 0.4  # kebetulan
    assert "karena" in _jel
    _mk2 = ModelKausal.from_dict(mk.to_dict(), seed=1)
    assert _mk2.jelaskan("kulit terbakar")["narasi"] == _jel      # roundtrip stabil
    print("0c. KAUSAL: jelas =", _jel)
    print("    cf =", _cf["narasi"])
    print("    blame aksi(kredit %.2f) vs kebetulan(kredit %.2f)"
          % (_b_api["kredit"], _b_badai["kredit"]))

    # 0d. PERENCANA: means-end multi-tingkat + meta-planning (pakai graf kausal)
    _dom = ModelKausal(seed=1)
    for _stim, _act, _lab, _imp in (
            ("tahu letak pasar", "beli di pasar", "dapat makanan", 0.7),
            ("ada orang terdekat", "bertanya pada orang", "tahu letak pasar", 0.6),
            ("tahu jalan ke alun-alun", "pergi ke alun-alun", "ada orang terdekat", 0.5),
            ("pernah lihat peta", "ingat peta", "tahu jalan ke alun-alun", 0.5)):
        for _ in range(3):
            _dom.pelajari([{"stimulus": _stim, "action": _act, "impact": _imp, "label": _lab}])
    _pl = Perencana(seed=1)
    _hasil = _pl.rencanakan_rencana("dapat makanan", _dom, {"pernah", "lihat", "peta"})
    _langkah = _pl.langkah(_hasil["pohon"]["akar"])
    assert _hasil["pohon"]["lengkap"] and not _hasil["meta"]["cabang_buntu"]
    assert _hasil["pohon"]["kedalaman"] >= 3                 # multi-tingkat (bukan 1 lompatan)
    assert _hasil["meta"]["sadar_merencanakan"]              # meta-planning
    assert _langkah[0].endswith("ingat peta") and _langkah[-1].endswith("beli di pasar")
    _pl2 = Perencana.from_dict(_pl.to_dict(), seed=1)
    assert _pl2.state()["kedalaman"] == _pl.state()["kedalaman"]
    print("0d. RENCANA: kedalaman =", _hasil["pohon"]["kedalaman"],
          "| langkah =", " → ".join(s.split(':', 1)[-1] for s in _langkah))

    o = Organik(seed=7)
    o.topologi.daftar("X"); o.topologi.kosongkan("X", "hilang", 9)
    o.luka.lukai("Y", "uang", "tipu", 3)
    o.identitas.tetapkan("aku penyendiri", {"senang": "tolak"})
    o.waktu.diingat("e1"); o.waktu.diingat("e1")
    o.tutur.catat("aku menyayangimu", "…", 0.2, {"takut": -0.6})
    o2 = Organik.from_dict(o.to_dict(), seed=7)
    assert o2.topologi.kosong() == ["X"]
    assert o2.luka.dikecualikan("Y", "uang")
    assert o2.identitas.klaim == "aku penyendiri"
    assert o2.waktu.half_life("e1") == o.waktu.half_life("e1")
    assert len(o2.tutur.riwayat()) == 1
    o.paralel.tambah("aku percaya keadilan", 0.6, {"senang": 0.3})
    o.paralel.tambah("aku menikmati ketidakadilan kecil", 0.4, {"senang": 0.2},
                     lawan_dari=1)
    o.tubuh.suntik(0.4)
    o3 = Organik.from_dict(o.to_dict(), seed=7)
    assert o3.paralel.state()["jumlah"] == 2
    assert abs(o3.tubuh.tegang - o.tubuh.tegang) < 1e-9
    # gejala + bekas ikut dalam serialisasi wadah
    o.gejala.muncul(0.6, None, tanda="t", tick=11)
    o.gejala.proses(tick=12)
    o.residu.bekas("gejala", KALIMAT_TAK_BERNAMA, tick=12, signature="t")
    o4 = Organik.from_dict(o.to_dict(), seed=7)
    assert o4.gejala.aktif() and o4.gejala.aktif()[0]["signature"] == "t"
    assert o4.residu.bekas_state()[-1]["signature"] == "t"
    # invensi ikut terserialisasi di wadah
    o.invensi.lahirkan(_dg, tick=11)
    o5 = Organik.from_dict(o.to_dict(), seed=7)
    assert o5.invensi.ringkas()["n"] >= 1
    # model kausal ikut terserialisasi di wadah
    o.kausal.pelajari(_eps[:4])
    o6 = Organik.from_dict(o.to_dict(), seed=7)
    assert o6.kausal.ringkas()["tepi"] == o.kausal.ringkas()["tepi"]
    print("ROUNDTRIP: OK |", o.ringkas())
    print("SEMUA MEKANISME ORGANIK (+ ORDE NOL) LULUS")
