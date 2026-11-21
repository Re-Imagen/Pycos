# -*- coding: utf-8 -*-
"""pycos/bahasa/tutur.py — MESIN TUTUR GENERATIF Pycos (L0–L3).

Mengubah tindak tutur + keadaan internal/biografi NPC menjadi ujaran yang
TIDAK hardcoded, dengan sumber daya leksikon `pycos/sumber_daya/
leksikon_pycos.json` (path bawaan: `pycos.dukungan.sumber.jalur_leksikon()`;
mesin ini tetap memerlukan path eksplisit dan tidak memuat sendiri).

Arsitektur:
    GenContext (frozen)  ──▶  Orkestrator (bounded DFS)
                                   ├── L0  Rencana Konten  (proposisi)
                                   ├── L1  Bentuk Semantik (slot terisi)
                                   ├── L2  Leksikon        (isi slot)
                                   └── L3  Morfologi & Linearisasi
                                             │
                                             ▼
                                        Tutur (teks + trace)

Murni standard library — satu-satunya impor antarmodul adalah `pycos.kontrak`
(pemeriksaan argumen batas). Bila leksikon tidak ditemukan,
`TuturEngine.tersedia()` False dan
pemanggil harus jatuh ke jalur lama (backward-compatible).

Modul ini juga memuat **ciri linguistik ujaran** (`FiturTutur`,
`analisis_teks`, `LeksikonCiri`): analisis dangkal berbasis leksikon untuk
polaritas, formalitas, intensitas, dan keraguan, termasuk negasi berbatas
klausa dan stemming sederhana. Ciri itu dipakai penilai keselarasan di
`pycos.refleksi.nurani` dan tersedia mandiri bagi pemanggil lain.
"""
from __future__ import annotations

import json
import os
import math
import random
import re
import threading
from dataclasses import dataclass, field
from typing import (Any, Dict, FrozenSet, List, Mapping, Optional, Sequence,
                    Tuple, cast)

from pycos.kontrak import hanya_kunci, teks_wajib

# Fondasi teks bersama (A1–A6, D2–D4, G1, H3, E0). Dipakai untuk tokenizer,
# stemmer, cakupan negasi, jenis kalimat, dan pemeriksa gramatika agar
# tidak ada lagi 9 tokenizer / 8 stoplist yang terpecah.
from pycos.bahasa.teks import (  # noqa: E402
    cakupan_negasi as _cakupan_negasi,
    jenis_kalimat as _jenis_kalimat_teks,
    kandidat_dasar as _kandidat_dasar_teks,
    pecah_kalimat as _pecah_kalimat,
    periksa_gramatika as _periksa_gramatika,
    potong_batas_kata as _potong_batas_kata,
    stem as _stem_teks,
    tokenisasi as _tokenisasi_teks,
    urai_subjek_predikat as _urai_subjek_predikat,
)

# ===========================================================================
# util kecil
# ===========================================================================
def _clip(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    """Jepit ke [lo, hi]; NaN/tak-numerik menjadi `lo` (bukan `hi`).

    Varian disengaja dari aturan `pycos.dukungan.numerik.jepit` (di sana NaN
    menjadi netral 0): di sini `lo` adalah nilai-pengganti yang dipakai saat
    masukan hilang, jadi NaN/tak-numerik jatuh ke `lo`.
    """
    try:
        v = float(x)
    except (TypeError, ValueError):
        return lo
    if v != v:
        return lo
    return lo if v < lo else hi if v > hi else v


def _norm(s: Any) -> str:
    return " ".join(str(s or "").strip().lower().split())


# ===========================================================================
# lattice tipe semantik
# ===========================================================================
class Lattice:
    def __init__(self, peta: Dict[str, Optional[str]]) -> None:
        self.peta = dict(peta)

    def subtipe(self, a: str, b: str) -> bool:
        """True bila a sama dengan b atau a adalah turunan (transitif) dari b."""
        if not a or not b:
            return False
        a = str(a).upper()
        b = str(b).upper()
        cur: Optional[str] = a
        seen = 0
        while cur and seen < 64:
            if cur == b:
                return True
            cur = self.peta.get(cur)
            seen += 1
        return False

    def cocok(self, tipe_kata: Sequence[str], tipe_slot: str) -> bool:
        """Kata cocok bila salah satu tipe semantiknya subtipe dari slot."""
        if not tipe_slot:
            return True
        for t in (tipe_kata or []):
            if self.subtipe(str(t), tipe_slot):
                return True
        return False


# ===========================================================================
# leksikon
# ===========================================================================
# Pengecualian leksikal nasalisasi (B3): bentuk yang tidak mengikuti tabel umum.
_PENGECUALIAN_NASAL: Dict[str, str] = {
    "tahu": "mengetahui",
    "punya": "mempunyai",
    "percaya": "memercayai",
    "kaji": "mengkaji",
    "tari": "menari",
    "bom": "mengebom",
    "cat": "mengecat",
    "las": "mengelas",
}

# Koreksi tipe semantik (C3): lema yang salah kelompok di data.
_KOREKSI_TIPE: Dict[str, List[str]] = {
    "pesimis": ["KERAGUAN"],
    "lelah": ["LELAH"],
    "bingung": ["BINGUNG"],
    "curiga": ["CURIGA"],
    "waspada": ["CURIGA"],
    "haru": ["HARU"],
}

# Koreksi valensi (C1): tanda salah pada data (bodoh/kejam/buruk positif, dst).
_KOREKSI_VALENSI: Dict[str, float] = {
    "bodoh": -0.8, "kejam": -0.8, "buruk": -0.7, "jelek": -0.7,
    "malas": -0.5, "hangat": 0.4, "manis": 0.4, "membantu": 0.5,
    "setuju": 0.4, "tahu": 0.0,
}


class Leksikon:
    def __init__(self, dok: Dict[str, Any]) -> None:
        # Lattice diperbaiki (C4): TUMBUHAN di bawah HIDUP (bukan ANIMAT);
        # TEMPAT/WAKTU cabang sendiri; tambah MANUSIA/ALAT/MAKANAN/HIDUP.
        peta = dict(dok.get("lattice") or {})
        peta.setdefault("HIDUP", "ENTITAS")
        peta.setdefault("MANUSIA", "ANIMAT")
        peta.setdefault("ALAT", "BENDA")
        peta.setdefault("MAKANAN", "EDIBLE")
        peta.setdefault("LELAH", "KEADAAN")
        peta.setdefault("BINGUNG", "EMOSI")
        peta.setdefault("CURIGA", "EMOSI")
        peta.setdefault("HARU", "EMOSI")
        if peta.get("TUMBUHAN") == "ANIMAT":
            peta["TUMBUHAN"] = "HIDUP"
        if peta.get("TEMPAT") == "ABSTRAK":
            peta["TEMPAT"] = "ENTITAS"
        if peta.get("WAKTU") == "ABSTRAK":
            peta["WAKTU"] = "ENTITAS"
        self.lattice = Lattice(peta)
        self.morfologi = dok.get("morfologi") or {}
        self.predikat = dok.get("predikat") or {}
        self.fungsi = dok.get("fungsi") or {}
        self.entri: List[Dict[str, Any]] = list(dok.get("leksikon") or [])
        self._by_lema: Dict[Tuple[str, str], Dict[str, Any]] = {}
        # Lema polisem (mis. "siapa" sebagai PRON dan ADV) punya lebih dari satu
        # entri. `ambil` tetap mengembalikan sense pertama, tetapi daftar lengkapnya
        # disimpan agar kelas/tipe dari sense lain tidak hilang.
        self._senses: Dict[Tuple[str, str], List[Dict[str, Any]]] = {}
        self._by_kelas: Dict[str, List[Dict[str, Any]]] = {}
        self._by_tipe: Dict[str, List[Dict[str, Any]]] = {}
        for e in self.entri:
            # Koreksi tipe & valensi (C1, C3) diterapkan di atas data mentah
            # agar berkas JSON (dengan sha provenance) tidak perlu diubah.
            lema = e.get("lema", "")
            if lema in _KOREKSI_TIPE:
                e = dict(e)
                e["tipe_semantik"] = list(_KOREKSI_TIPE[lema])
            if lema in _KOREKSI_VALENSI:
                e = dict(e)
                e["valensi"] = _KOREKSI_VALENSI[lema]
            kunci = (e["bahasa"], e["lema"])
            self._by_lema.setdefault(kunci, e)
            self._senses.setdefault(kunci, []).append(e)
            for k in e.get("kelas", []):
                self._by_kelas.setdefault(k, []).append(e)
            for t in e.get("tipe_semantik", []):
                self._by_tipe.setdefault(t, []).append(e)

    def ambil(self, bahasa: str, lema: str) -> Optional[Dict[str, Any]]:
        return self._by_lema.get((bahasa, _norm(lema)))

    def kandidat(self, kelas: str, bahasa: str) -> List[Dict[str, Any]]:
        out = []
        for e in self._by_kelas.get(kelas, []):
            if e["bahasa"] == bahasa:
                out.append(e)
        return out

    def senses(self, lema: str, bahasa: str = "id") -> List[Dict[str, Any]]:
        """Seluruh entri untuk satu lema (lebih dari satu bila polisem)."""
        return list(self._senses.get((bahasa, _norm(lema)), []))

    def kelas_dari(self, lema: str, bahasa: str = "id") -> List[str]:
        out: List[str] = []
        for e in self.senses(lema, bahasa):
            for k in e.get("kelas", []):
                if k not in out:
                    out.append(k)
        return out

    def tipe_dari(self, lema: str, bahasa: str = "id") -> List[str]:
        out: List[str] = []
        for e in self.senses(lema, bahasa):
            for t in e.get("tipe_semantik", []):
                if t not in out:
                    out.append(t)
        return out

    # -- morfologi -------------------------------------------------------
    def nasalisasi(self, dasar: str) -> str:
        """Bentuk meN- dari dasar (B1–B3): tabel lengkap + pengecualian.

        Afiks JSON yang dibangkitkan mekanis tidak dipercaya di sini
        (mis. `mehalangii`, `berfire`); aturan + pengecualian yang dipakai.
        """
        d = _norm(dasar)
        if not d or " " in d or "-" in d:
            return d
        if d in _PENGECUALIAN_NASAL:
            return _PENGECUALIAN_NASAL[d]
        e = self.ambil("id", d)
        if e and e.get("tidak_di_nasalkan"):
            return d
        # Lema Inggris jangan diberi afiks Indonesia (C9).
        if e is None and self.ambil("en", d) is not None:
            return d
        dua = d[:2]
        # Gugus konsonan & serapan: konsonan tidak diluluh (B2) —
        # diperiksa SEBELUM hitungan suku kata agar "klaim"/"kritik"
        # tidak terambil aturan satu suku kata.
        if dua in ("kr", "kl", "pr", "tr", "st", "sp", "sk"):
            if dua in ("pr", "sp"):
                return "mem" + d
            if dua in ("tr", "st"):
                return "men" + d
            return "meng" + d
        # Digraf: sy, kh, ng, ny tidak diluluh (B2).
        if dua in ("sy", "st"):
            return "men" + d
        if dua == "kh":
            return "meng" + d
        if dua in ("ng", "ny"):
            return "me" + d
        # Dasar satu suku kata → menge- (B1).
        if len(re.findall(r"[aeiou]+", d)) == 1:
            return "menge" + d
        c = d[0]
        # mem-: b, f, v tetap; p luluh (B1).
        if c in ("b", "f", "v"):
            return "mem" + d
        if c == "p":
            return "mem" + d[1:]
        # men-: c, d, j, z tetap; t luluh (B1).
        if c in ("c", "d", "j", "z"):
            return "men" + d
        if c == "t":
            return "men" + d[1:]
        # meng-: vokal, g, h tetap; k luluh (B1).
        if c in "aeiou" or c in ("g", "h"):
            return "meng" + d
        if c == "k":
            return "meng" + d[1:]
        # meny-: s luluh (B1).
        if c == "s":
            return "meny" + d[1:]
        # me-: l, m, n, r, w, y tanpa asimilasi (B1).
        if c in ("l", "m", "n", "r", "w", "y"):
            return "me" + d
        return "meng" + d

    def nominalisasi(self, lema: str) -> Optional[str]:
        e = self.ambil("id", lema)
        if e:
            n = (e.get("afiks") or {}).get("nom")
            if n:
                return cast(str, n)
        return None

    def adjektiva_dasar(self, lema: str) -> str:
        return _norm(lema)


# ===========================================================================
# struktur semantik
# ===========================================================================
@dataclass
class Arg:
    """Argumen proposisi: berperan, bertipe, dan berisi rujukan.

    `mode` menentukan apakah isi sudah berupa RUJUKAN leksikal ("aku", "api",
    sebuah episode) atau masih berupa SPESIFIKASI semantik yang harus dipilihkan
    lema oleh L2. Ini yang membedakan "biografi sebagai argumen" dari template.
    """
    peran: str
    tipe: str
    isi: Any = None            # lema (str) | entitas | Node (SBAR)
    literal: Any = None        # nilai (mis. tingkat 0.6)
    opsional: bool = False
    mode: str = "rujuk"        # rujuk | isi

    def kosong(self) -> bool:
        return self.isi is None and self.literal is None


@dataclass
class Node:
    predikat: str
    args: List[Arg] = field(default_factory=list)
    modus: str = "nyata"        # nyata | ingkar | tanya
    aspek: str = "sedang"       # selesai | sedang | akan | pengalaman
    polaritas: str = "+"
    intensitas: float = 0.5
    anchor: Optional[str] = None
    komplemen: Optional[str] = None
    lema: Optional[str] = None  # predikat leksikal (opsional)

    def arg(self, peran: str) -> Optional[Arg]:
        for a in self.args:
            if a.peran == peran:
                return a
        return None


@dataclass(frozen=True)
class GenContext:
    """Potret keadaan internal + biografi yang dibekukan untuk satu ujaran."""
    act: str = "menyatakan"
    bahasa: str = "id"
    register: str = "netral"
    topik: str = ""
    kepada: str = ""
    dekat: bool = False
    spotlight: Tuple[str, ...] = ()
    timeline: Tuple[str, ...] = ()
    core: Tuple[str, ...] = ()
    values: Tuple[str, ...] = ()
    boundaries: Tuple[str, ...] = ()
    grief: Tuple[str, ...] = ()
    dissonance: Tuple[str, ...] = ()
    doubt: float = 0.0
    agency: float = 0.5
    valensi: float = 0.0
    arousal: float = 0.0
    mortality: float = 0.0
    urgency: float = 0.0
    inner: str = ""
    niat: str = ""
    permintaan: str = ""
    refusal: str = ""
    seed: int = 0
    # komitmen (dapat diubah oleh pemanggil)
    commitments: Tuple[str, ...] = ()
    # kejernihan pemilihan leksikal setelah pemrosesan berkepanjangan
    attention_fatigue: float = 0.0
    # --- dimensi state internal baru (dipetakan dari Pycos oleh
    #     `konteks_dari_presentasi`; semuanya opsional & default netral) ---
    # label emosi dominan yang BENAR-BENAR dirasakan, mis. ("TAKUT",) atau
    # ("SEDIH", "MARAH") — menyelaraskan leksikon dengan state, bukan hanya
    # dengan valensi/arousal rata-rata.
    emosi: Tuple[str, ...] = ()
    # modus apersepsi: jelas | kabut | gradien | tanpa_nama | kosong.
    # "aku tidak tahu kenapa aku begini" adalah state, bukan kegagalan.
    apersepsi: str = ""
    apersepsi_kalimat: str = ""
    # tekanan afektif [0..1]: seberapa sarat state (memaksa bahasa
    # menyederhanakan diri dan menekan penguat).
    tekanan: float = 0.0
    # penahanan sadar [0..1]: dorongan tutur yang sengaja ditahan.
    menahan: float = 0.0
    # sensasi tubuh dominan, mis. ("tegang",) — tubuh mendahului kognisi.
    tubuh: Tuple[str, ...] = ()

    def topik_aktif(self) -> str:
        return _norm(self.topik)


@dataclass
class Tutur:
    teks: str
    status: str = "SUKSES"       # SUKSES | GAGAL | MENYERAH
    act: str = ""
    trace: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {"teks": self.teks, "status": self.status, "act": self.act,
                "trace": self.trace}


# ===========================================================================
# L0 — RENCANA KONTEN
# ===========================================================================
class L0:
    """Tindak tutur → proposisi. Biografi masuk sebagai ARGUMEN, bukan hiasan."""

    def __init__(self, leks: Leksikon) -> None:
        self.leks = leks

    #: predikat emosi literal → idiom/metafora tak-konvensional (dipilih state:
    #: emosi dominan + registri + arousal; deterministik, tanpa rng).
    EKSPRESI_PAKAI = {
        "MARAH": "DARAH_MENDIDIH",
        "SEDIH": "HANCUR",
        "TAKUT": "MERINDING",
        "SENANG": "LULUH",
    }

    def _mungkin_ekspresif(self, node: Node, ctx: GenContext) -> Node:
        """Naikkan predikat emosi literal → idiom/metafora tak-konvensional.

        Nuansa register: ragam formal memilih bentuk literal; ragam akrab
        memakai idiom/metafora; ragam netral hanya saat tersulut (arousal).
        """
        alt = self.EKSPRESI_PAKAI.get(node.predikat)
        if not alt or alt not in self.leks.predikat:
            return node
        if ctx.register == "formal":
            return node
        if ctx.register == "netral" and ctx.arousal < 0.6:
            return node
        node.predikat = alt
        return node

    # -- pembantu pengambilan biografi ----------------------------------
    @staticmethod
    def _episode(ctx: GenContext, i: int = 0) -> Optional[str]:
        if ctx.core:
            return ctx.core[min(i, len(ctx.core) - 1)]
        if ctx.timeline:
            return ctx.timeline[min(i, len(ctx.timeline) - 1)]
        return None

    def rencana(self, ctx: GenContext) -> Tuple[Node, List[str]]:
        """Kembalikan (Node akar, daftar penurunan-anggun yang dipakai)."""
        turun: List[str] = []
        act = ctx.act
        ep = self._episode(ctx)
        topik = ctx.topik_aktif()

        if act == "menimbang":
            return Node("HESITASI", [
                Arg("EXPERIENCER", "ANIMAT", isi="aku"),
                Arg("SEBAB", "PROPOSISI", isi=topik or None, opsional=True),
            ], modus="nyata", intensitas=0.4), turun

        if act == "ragu":
            # KERAGUAN(proposisi=[KEYAKINAN(aku, X)], alasan=[EPISODE], tingkat)
            # Proposisi harus berupa KLAUSA (bukan kata topik telanjang).
            klaim = ctx.inner or (topik if " " in topik else "") or None
            if not klaim and not ep:
                turun.append("tanpa_proposisi")
            node = Node("RAGU", [
                Arg("EXPERIENCER", "ANIMAT", isi="aku"),
                Arg("PROPOSISI", "PROPOSISI", isi=klaim, opsional=True),
            ], modus="nyata", intensitas=_clip(ctx.doubt, 0.2, 0.95))
            if ep:
                node.args.append(Arg("ALASAN", "PERISTIWA", isi=ep, opsional=True))
            else:
                turun.append("alasan_dibuang")
            return node, turun

        if act == "menolak":
            alasan = None
            if ctx.refusal:
                alasan = ctx.refusal
            elif ctx.boundaries:
                alasan = ctx.boundaries[0]
            elif ctx.values:
                alasan = ctx.values[0]
            else:
                turun.append("tanpa_alasan")
            tindakan = ctx.permintaan or (topik if topik and " " in topik
                                          else None)
            node = Node("MENOLAK", [
                Arg("AGENT", "ANIMAT", isi="aku"),
                Arg("TINDAKAN", "TINDAKAN", isi=tindakan, opsional=True),
            ], modus="ingkar", intensitas=0.6)
            if alasan:
                node.args.append(Arg("ALASAN", "PROPOSISI", isi=alasan,
                                     opsional=True))
            return node, turun

        if act == "mengenang":
            node = Node("INGAT", [
                Arg("EXPERIENCER", "ANIMAT", isi="aku"),
                Arg("EPISODE", "PERISTIWA", isi=ep, opsional=ep is None),
            ], aspek="pengalaman", intensitas=0.6)
            if ctx.grief:
                node.args.append(Arg("OBJEK", "ANIMAT", isi=ctx.grief[0],
                                     opsional=True))
            if not ep:
                turun.append("episode_tak_ada")
            return node, turun

        if act == "eksistensial":
            node = Node("SADAR", [
                Arg("EXPERIENCER", "ANIMAT", isi="aku"),
                Arg("PROPOSISI", "PROPOSISI",
                    isi="kita semua akan mati", opsional=True),
            ], intensitas=_clip(ctx.mortality, 0.3, 1.0))
            return node, turun

        if act == "rasionalisasi":
            dis = ctx.dissonance[0] if ctx.dissonance else (topik or None)
            node = Node("MENOLAK", [
                Arg("AGENT", "ANIMAT", isi="aku"),
                Arg("TINDAKAN", "TINDAKAN", isi="menyesali " + str(dis),
                    opsional=True),
                Arg("ALASAN", "PROPOSISI",
                    isi=(ctx.values[0] if ctx.values else None),
                    opsional=not ctx.values),
            ], intensitas=0.55)
            if not ctx.values:
                turun.append("alasan_dibuang")
            return node, turun

        if act == "mimpi":
            return Node("INGAT", [
                Arg("EXPERIENCER", "ANIMAT", isi="aku"),
                Arg("EPISODE", "PERISTIWA", isi=ctx.inner or ep,
                    opsional=(ctx.inner or ep) is None),
            ], aspek="pengalaman", intensitas=0.35,
                anchor="malam tadi"), turun

        if act == "peringatan":
            node = Node("PERINGATAN", [
                Arg("AGENT", "ANIMAT", isi="aku"),
                Arg("TARGET", "ANIMAT", isi="kamu"),
                Arg("OBJEK", "ENTITAS", isi=topik or "bahaya",
                    opsional=True),
            ], intensitas=0.7)
            if ctx.spotlight and _norm(ctx.spotlight[0]) != _norm(topik):
                node.args.append(Arg("SEBAB", "PROPOSISI",
                                     isi=ctx.spotlight[0], opsional=True))
            return node, turun

        # tindak tutur bernama emosi (mis. dipakai penguji/penulis skenario)
        _EMO_ACT = {"marah": "MARAH", "sedih": "SEDIH", "bersedih": "SEDIH",
                    "senang": "SENANG", "bersenang": "SENANG", "suka": "SENANG",
                    "takut": "TAKUT", "bertakut": "TAKUT",
                    "malu": "MALU", "bermalu": "MALU",
                    "benci": "BENCI", "kesepian": "KESEPIAN",
                    "tenang": "TENANG", "harap": "HARAP", "berharap": "HARAP",
                    "terkejut": "TERKEJUT", "jijik": "JIJIK",
                    "bangga": "BANGGA", "cemburu": "CEMBURU",
                    "syukur": "BERSYUKUR", "bersyukur": "BERSYUKUR",
                    "penasaran": "PENASARAN",
                    "haru": "HARU", "mendidih": "DARAH_MENDIDIH",
                    "hancur": "HANCUR", "merinding": "MERINDING",
                    "luluh": "LULUH", "berbatu": "HATI_BERBATU",
                    "mengeluh": "SEDIH", "menggerutu": "MARAH",
                    "menyapa": "SENANG", "bergembira": "SENANG"}
        if act in _EMO_ACT:
            node = Node(_EMO_ACT[act], [
                Arg("EXPERIENCER", "ANIMAT", isi="aku"),
                Arg("STIMULUS", "ENTITAS", isi=topik or None, opsional=True),
                Arg("TARGET", "ANIMAT", isi="kamu", opsional=True),
            ], intensitas=0.6)
            return self._mungkin_ekspresif(node, ctx), turun

        if act == "menantang":
            node = Node("MARAH", [
                Arg("EXPERIENCER", "ANIMAT", isi="aku"),
                Arg("TARGET", "ANIMAT", isi="kamu", opsional=True),
            ], intensitas=0.8)
            return self._mungkin_ekspresif(node, ctx), turun

        if act == "menegur":
            return Node("BERTANYA", [
                Arg("AGENT", "ANIMAT", isi="aku"),
                Arg("TOPIK", "ENTITAS", isi=topik or "itu", opsional=False),
                Arg("TARGET", "ANIMAT", isi="kamu", opsional=True),
            ], modus="tanya", intensitas=0.6), turun

        if act == "waspada":
            return Node("RAGU", [
                Arg("EXPERIENCER", "ANIMAT", isi="aku"),
                Arg("PROPOSISI", "PROPOSISI", isi="kamu bisa dipercaya",
                    opsional=True),
            ], modus="nyata", intensitas=0.6), turun

        if act == "bertanya":
            return Node("BERTANYA", [
                Arg("AGENT", "ANIMAT", isi="aku"),
                Arg("TOPIK", "ENTITAS", isi=topik or "itu", opsional=False),
                Arg("TARGET", "ANIMAT", isi="kamu", opsional=True),
            ], modus="tanya", intensitas=0.5), turun

        if act == "akrab":
            return Node("SENANG", [
                Arg("EXPERIENCER", "ANIMAT", isi="aku"),
                Arg("STIMULUS", "ENTITAS", isi="kamu ada", opsional=True),
            ], intensitas=0.6), turun

        if act == "menjawab":
            isi = ctx.inner or ctx.niat or None
            if not isi:
                turun.append("tanpa_isi")
            return Node("BERKATA", [
                Arg("AGENT", "ANIMAT", isi="aku"),
                Arg("UJARAN", "UJARAN", isi=isi, opsional=isi is None),
                Arg("TARGET", "ANIMAT", isi="kamu", opsional=True),
            ], intensitas=0.35), turun

        if act == "mengamati":
            fokus = ctx.spotlight[0] if ctx.spotlight else (topik or None)
            if not fokus:
                turun.append("tanpa_fokus")
            return Node("MELIHAT", [
                Arg("EXPERIENCER", "ANIMAT", isi="aku"),
                Arg("OBJEK", "ENTITAS", isi=fokus, opsional=fokus is None),
            ], intensitas=0.4), turun

        if act == "menyapa_proaktif":
            return Node("MELIHAT", [
                Arg("EXPERIENCER", "ANIMAT", isi="aku"),
                Arg("OBJEK", "ENTITAS", isi="kamu", opsional=False),
            ], intensitas=0.3), turun

        if act == "kembali":
            return Node("SENANG", [
                Arg("EXPERIENCER", "ANIMAT", isi="aku"),
                Arg("STIMULUS", "ENTITAS", isi="kamu kembali", opsional=True),
            ], intensitas=0.6, anchor="sekarang"), turun

        # default: menyatakan — ujaran dari pikiran yang terbentuk (E4)
        isi = ctx.niat or ctx.inner or None
        if not isi:
            if ctx.menahan >= 0.6:
                # penahanan sadar: dorongan tutur ditahan → jeda, bukan isi kosong
                turun.append("ditahan_menjadi_hesitasi")
                return Node("HESITASI", [
                    Arg("EXPERIENCER", "ANIMAT", isi="aku"),
                ], modus="nyata", intensitas=0.45), turun
            # Titik fokus tanpa pikiran/keinginan terbentuk: ekspresikan
            # *persepsi* terhadap topik (E3/E4), bukan "topik." mentah. Bila
            # topik pun tidak ada, tidak ada yang dapat dinyatakan.
            fokus = topik or (ctx.spotlight[0] if ctx.spotlight else None)
            if fokus and " " not in _norm(fokus):
                return Node("MELIHAT", [
                    Arg("EXPERIENCER", "ANIMAT", isi="aku"),
                    Arg("OBJEK", "ENTITAS", isi=fokus, opsional=False),
                ], intensitas=0.4), turun
            if fokus:
                return Node("BERKATA", [
                    Arg("AGENT", "ANIMAT", isi="aku"),
                    Arg("UJARAN", "UJARAN", isi=fokus, opsional=False),
                ], intensitas=0.35), turun
            turun.append("tanpa_topik")
            return Node("HESITASI", [
                Arg("EXPERIENCER", "ANIMAT", isi="aku"),
            ], modus="nyata", intensitas=0.45), turun
        node = Node("BERKATA", [
            Arg("AGENT", "ANIMAT", isi="aku"),
            Arg("UJARAN", "UJARAN", isi=isi, opsional=False),
        ], intensitas=0.35)
        if ctx.values:
            node.args.append(Arg("ALASAN", "PROPOSISI", isi=ctx.values[0],
                                 opsional=True))
        return node, turun


# ===========================================================================
# L1 — REALISASI SEMANTIK → SLOT TERISI
# ===========================================================================
@dataclass
class Slot:
    nama: str
    kelas_wajib: str
    tipe_semantik: str
    opsional: bool
    afinitas_topik: float
    afinitas_fokus: float
    modifier: bool
    isi: Any = None
    terisi: bool = False
    topik: bool = False


@dataclass
class Kerangka:
    node: Node
    slot: List[Slot]
    urutan: List[str]
    voice: str = "aktif"
    topik_front: Optional[str] = None


class L1:
    def __init__(self, leks: Leksikon) -> None:
        self.leks = leks

    def realisasi(self, node: Node, ctx: GenContext
                  ) -> Tuple[Optional[Kerangka], List[str]]:
        catatan: List[str] = []
        spec = self.leks.predikat.get(node.predikat)
        if spec is None:
            catatan.append("predikat_tak_dikenal:" + node.predikat)
            return None, catatan
        slots: List[Slot] = []
        for s in spec.get("slot", []):
            slots.append(Slot(s["nama"], s["kelas_wajib"], s["tipe_semantik"],
                              bool(s.get("opsional")), float(s.get("afinitas_topik", 0.5)),
                              float(s.get("afinitas_fokus", 0.5)),
                              bool(s.get("modifier", False))))
        # isi slot dari argumen node (cocokkan nama peran, lalu posisi)
        sisa = list(node.args)
        for s in slots:
            a = node.arg(s.nama)
            if a is None:
                # coba peran yang setara
                alias = {"EXPERIENCER": ("AGENT", "PEMILIK"),
                         "AGENT": ("EXPERIENCER",),
                         "STIMULUS": ("OBJEK", "TARGET", "TOPIK"),
                         "OBJEK": ("STIMULUS", "TARGET", "PATIENT"),
                         "TARGET": ("PATIENT", "OBJEK"),
                         "PATIENT": ("TARGET", "OBJEK"),
                         "PROPOSISI": ("UJARAN", "EPISODE", "ALASAN"),
                         "UJARAN": ("PROPOSISI", "EPISODE"),
                         "EPISODE": ("PROPOSISI", "PERISTIWA"),
                         "TOPIK": ("OBJEK", "STIMULUS")}
                for alt in alias.get(s.nama, ()):
                    a = node.arg(alt)
                    if a is not None:
                        break
            if a is not None and not a.kosong():
                s.isi = a
                s.terisi = True
                if a in sisa:
                    sisa.remove(a)
        # argumen sisa → slot opsional kosong yang cocok tipenya
        for a in sisa:
            if a.kosong():
                continue
            for s in slots:
                if s.terisi:
                    continue
                if self.leks.lattice.cocok([a.tipe], s.tipe_semantik) or \
                        self.leks.lattice.cocok([s.tipe_semantik], a.tipe):
                    s.isi = a
                    s.terisi = True
                    break
        # Hard filter: restriksi seleksional pada slot NOMINAL.
        # Inilah yang mencegah "memakan api" — bukan aturan khusus, tapi
        # ketidakcocokan tipe pada lattice.
        NOMINAL = {"ENTITAS", "FISIK", "BENDA", "EDIBLE", "TAK_EDIBLE",
                   "MAKHLUK", "ANIMAT", "INANIMAT", "ORANG", "HEWAN",
                   "TUMBUHAN", "TEMPAT"}
        PRONOMINA = {"aku", "saya", "kamu", "kau", "dia", "ia", "kita",
                     "kami", "mereka", "-ku", "-mu", "-nya"}
        for s in slots:
            if not s.terisi or s.tipe_semantik not in NOMINAL:
                continue
            a = s.isi
            if not isinstance(a, Arg) or not isinstance(a.isi, str):
                continue
            kata = _norm(a.isi)
            if kata in PRONOMINA or " " in kata:
                continue
            tipe_kata = self.leks.tipe_dari(kata, ctx.bahasa)
            if not tipe_kata:
                continue
            if not self.leks.lattice.cocok(tipe_kata, s.tipe_semantik):
                if s.opsional:
                    s.isi = None
                    s.terisi = False
                    catatan.append("restriksi_dibuang:" + s.nama)
                else:
                    catatan.append("restriksi_gagal:" + s.nama)
                    return None, catatan
        # slot wajib kosong → Gagal (orkestrator boleh coba alternatif)
        kurang = [s.nama for s in slots if not s.terisi and not s.opsional]
        if kurang:
            catatan.append("slot_wajib_kosong:" + ",".join(kurang))
            return None, catatan
        # voice: keputusan topikal
        voice = "aktif"
        topik_front: Optional[str] = None
        topik = ctx.topik_aktif()
        if topik:
            for s in slots:
                if not s.terisi:
                    continue
                isi = s.isi.isi if isinstance(s.isi, Arg) else None
                if isinstance(isi, str) and _norm(isi) and (
                        _norm(isi) == topik or topik in _norm(isi)
                        or _norm(isi) in topik):
                    if s.nama in ("OBJEK", "STIMULUS", "TARGET", "PATIENT",
                                  "TOPIK"):
                        voice = "pasif"
                        topik_front = s.nama
                    break
        # spotlight memutuskan fokus: kalau spotlight menyebut subjek → aktif
        if ctx.spotlight:
            if any(_norm(x) in ("aku", "saya", "diri") for x in ctx.spotlight):
                voice = "aktif"
                topik_front = None
        kerangka = Kerangka(node, slots, list(spec.get("urutan")
                                              or [s.nama for s in slots]),
                            voice, topik_front)
        return kerangka, catatan


# ===========================================================================
# L2 — PEMILIHAN LEKSIKAL
# ===========================================================================
class L2:
    #: predikat semantik → tipe semantik kata yang boleh mengisinya
    PRED_TIPE = {
        "RAGU": "KERAGUAN", "MARAH": "MARAH", "SEDIH": "SEDIH",
        "SENANG": "SENANG", "TAKUT": "TAKUT", "BENCI": "BENCI",
        "CINTA": "CINTA", "MALU": "MALU", "HARAP": "HARAP",
        "KESEPIAN": "KESEPIAN", "TENANG": "TENANG",
    }
    # Kutub valensi yang konsisten dengan predikat emosi (F2): kandidat yang
    # berlawanan kutub tidak boleh dipakai ("terharu" +0,3 untuk SEDIH).
    PRED_KUTUB = {"SEDIH": -1.0, "TAKUT": -1.0, "MARAH": -1.0, "MALU": -1.0,
                  "BENCI": -1.0, "KESEPIAN": -1.0,
                  "SENANG": 1.0, "CINTA": 1.0, "TENANG": 1.0, "HARAP": 1.0}

    def __init__(self, leks: Leksikon, rng: random.Random,
                 riwayat: Optional[List[str]] = None) -> None:
        self.leks = leks
        self.rng = rng
        self.riwayat = riwayat if riwayat is not None else []
        self._last_choice: Optional[str] = None

    # -- hard filter ------------------------------------------------------
    def _lolos_hard(self, e: Dict[str, Any], slot: Slot, ctx: GenContext
                    ) -> Optional[str]:
        if ctx.register not in (e.get("register") or ["netral"]) and \
                "netral" not in (e.get("register") or []):
            return "register"
        if e.get("bahasa") != ctx.bahasa:
            return "bahasa"
        if not self.leks.lattice.cocok(e.get("tipe_semantik") or [],
                                       slot.tipe_semantik):
            return "tipe"
        return None

    # -- soft score -------------------------------------------------------
    def _skor(self, e: Dict[str, Any], slot: Slot, ctx: GenContext) -> float:
        topik = ctx.topik_aktif()
        fokus = _norm(ctx.spotlight[0]) if ctx.spotlight else ""
        fatigue = _clip(ctx.attention_fatigue, 0.0, 1.0)
        clarity = max(0.25, 1.0 - 0.65 * fatigue)
        align_topik = 0.0
        if topik and (_norm(e["lema"]) == topik or topik in _norm(e["lema"])):
            align_topik = 1.0
        elif topik and any(_norm(s) == topik for s in (e.get("sinonim") or [])):
            align_topik = 0.6
        align_fokus = 1.0 if (fokus and _norm(e["lema"]) == fokus) else 0.0
        # Kelelahan mengaburkan pemetaan topik/fokus tanpa mengganti drive atau
        # afek aktual; kata generik/frekuen relatif lebih mudah lolos.
        align_topik *= clarity
        align_fokus *= clarity
        # kedekatan afektif: kata yang valensinya searah keadaan lebih disukai
        afek = 0.0
        if ctx.valensi or ctx.arousal:
            afek = -(abs(float(e.get("valensi", 0.0)) - ctx.valensi) * 0.6
                     + abs(float(e.get("arousal", 0.0)) - ctx.arousal) * 0.4)
        afek *= clarity
        # keselarasan emosi: kata yang MENAMAI emosi yang benar-benar dirasakan
        # (state → leksikon), bukan hanya kecocokan valensi/arousal rata-rata.
        emosi_align = 0.0
        if ctx.emosi:
            tipe_kata = set(e.get("tipe_semantik") or [])
            if tipe_kata & set(ctx.emosi):
                emosi_align = 1.0
        beban = _clip(ctx.tekanan, 0.0, 1.0)
        # apersepsi gagal menamai (bukan "kosong"/tubuh sunyi): kata yang
        # terlalu spesifik justru dijauhi.
        kabur = ctx.apersepsi in ("kabut", "gradien", "tanpa_nama")
        formal = 1.0 - abs(float(e.get("register_formalitas", 0.5))
                           - (0.85 if ctx.register == "formal" else
                              0.25 if ctx.register == "akrab" else 0.5))
        formal *= 1.0 - 0.20 * fatigue
        s = (0.9 * slot.afinitas_topik * align_topik
             + 0.7 * slot.afinitas_fokus * align_fokus
             + 0.5 * afek
             + 0.3 * formal
             + 0.25 * float(e.get("frekuensi", 0.5))
             + 0.15 * float(e.get("intensitas_bawaan", 0.0)) * ctx.arousal
             + 0.15 * float(e.get("daya_tekan", 0.0)) * ctx.urgency
             + 0.4 * emosi_align
             + 0.2 * beban * float(e.get("frekuensi", 0.5)))
        if kabur:
            s -= 0.25 * emosi_align
        # Penalti frekuensi lebih panjang agar pilihan tidak berosilasi pada
        # dua lema yang sama. Domain/kelas tetap ditentukan hard filter.
        s -= 0.30 * self.riwayat[-32:].count(e["lema"])
        if e["lema"] in self.riwayat[-8:]:
            idx = self.riwayat[-8:][::-1].index(e["lema"])
            s -= 0.35 * (1.0 - idx / 8.0)
        return s

    def _pilih_beragam(self, lolos: List[Tuple[float, Dict[str, Any]]],
                        info: Dict[str, Any]) -> Dict[str, Any]:
        """Sampling berbobot pada kandidat kompatibel, bukan substitusi teks."""
        # Lema polisem tidak mendapat tiket ganda dalam sampling.
        unik = []
        terlihat = set()
        for skor, entri in lolos:
            if entri["lema"] not in terlihat:
                unik.append((skor, entri))
                terlihat.add(entri["lema"])
        terbaik = unik[0][0]
        pool = [(skor, e) for skor, e in unik[:12] if skor >= terbaik - 0.8]
        if not self.riwayat or len(pool) == 1:
            skor, pilih = pool[0]
        else:
            # Penalti riwayat telah masuk skor; seed memilih di antara opsi
            # yang masih dekat, bukan memilih nomor varian kosmetik.
            bobot = [math.exp((skor - terbaik) / 0.35) for skor, _ in pool]
            skor, pilih = self.rng.choices(pool, weights=bobot, k=1)[0]
        info.update(terpilih=pilih["lema"], skor=round(skor, 3),
                    pool_variasi=len(pool))
        self._last_choice = pilih["lema"]
        self.riwayat.append(pilih["lema"])
        if len(self.riwayat) > 32:
            del self.riwayat[:-32]
        return pilih

    #: predikat → tag kelas aksi (verba) di leksikon
    PRED_AKSI = {
        "MELIHAT": "persepsi", "BERTANYA": "tutur_tanya",
        "BERKATA": "tutur", "INGAT": "kognisi_ingat",
        "MENOLAK": "penolakan", "BUTUH": "kebutuhan",
        "PERINGATAN": "peringatan",
    }

    def _pilih_dalam(self, kandidat: List[Dict[str, Any]], slot: Slot,
                     ctx: GenContext) -> Tuple[Optional[Dict[str, Any]], Dict[str, Any]]:
        """Seperti `pilih` tetapi kandidat sudah dibatasi dari luar (kutub)."""
        info: Dict[str, Any] = {"slot": slot.nama,
                                "kandidat": len(kandidat),
                                "dibuang": {}, "terpilih": None,
                                "alternatif": 0}
        lolos: List[Tuple[float, Dict[str, Any]]] = []
        for e in kandidat:
            alasan = self._lolos_hard(e, slot, ctx)
            if alasan:
                info["dibuang"][alasan] = info["dibuang"].get(alasan, 0) + 1
                continue
            lolos.append((self._skor(e, slot, ctx), e))
        if not lolos:
            return None, info
        lolos.sort(key=lambda kv: kv[0], reverse=True)
        info["alternatif"] = len(lolos)
        pilih = self._pilih_beragam(lolos, info)
        return pilih, info

    # =======================================================================
    # PREDIKAT
    # =======================================================================
    def pilih_predikat(self, node: Node, ctx: GenContext
                       ) -> Tuple[Optional[Dict[str, Any]], Dict[str, Any]]:
        """Pilih LEMA predikat dari keadaan (bukan dari template)."""
        tipe = self.PRED_TIPE.get(node.predikat)
        if tipe:
            slot = Slot("PREDIKAT", "ADJ", tipe, False, 0.6, 0.5, True)
            kutub = self.PRED_KUTUB.get(node.predikat, 0.0)
            if kutub:
                asli = self.leks.kandidat(slot.kelas_wajib, ctx.bahasa)
                lolos_kutub = [
                    e for e in asli
                    if (kutub > 0 and float(e.get("valensi", 0.0)) >= -0.1)
                    or (kutub < 0 and float(e.get("valensi", 0.0)) <= 0.1)
                ]
                if lolos_kutub:
                    # pilih lewat skor biasa di antara yang kutubnya konsisten
                    pilih_k, info_k = self._pilih_dalam(lolos_kutub, slot, ctx)
                    if pilih_k is not None:
                        return pilih_k, info_k
            return self.pilih(slot, ctx)
        aksi = self.PRED_AKSI.get(node.predikat)
        if not aksi:
            return None, {"slot": "PREDIKAT", "dilewati": True}
        slot = Slot("PREDIKAT", "V", "TINDAKAN", False, 0.6, 0.5, True)
        kandidat = [e for e in self.leks.kandidat("V", ctx.bahasa)
                    if e.get("aksi") == aksi
                    and self._lolos_hard(e, slot, ctx) is None]
        if not kandidat:
            return None, {"slot": "PREDIKAT", "aksi": aksi,
                          "kandidat": 0}
        info = {"slot": "PREDIKAT", "aksi": aksi, "kandidat": len(kandidat)}
        skor = sorted(((self._skor(e, slot, ctx), e) for e in kandidat),
                      key=lambda kv: kv[0], reverse=True)
        pilih = skor[0][1]
        if pilih["lema"] == self._last_choice and len(skor) > 1:
            pilih = skor[1][1]
            info["anti_repetisi"] = True
        if len(skor) > 1 and self.rng.random() < 0.3:
            pilih = skor[self.rng.randrange(0, min(3, len(skor)))][1]
        info["terpilih"] = pilih["lema"]
        self._last_choice = pilih["lema"]
        self.riwayat.append(pilih["lema"])
        if len(self.riwayat) > 32:
            del self.riwayat[:-32]
        return pilih, info

    def pilih(self, slot: Slot, ctx: GenContext) -> Tuple[Optional[Dict[str, Any]],
                                                          Dict[str, Any]]:
        info: Dict[str, Any] = {"slot": slot.nama, "kandidat": 0, "dibuang": {},
                "terpilih": None, "alternatif": 0}
        kandidat = self.leks.kandidat(slot.kelas_wajib, ctx.bahasa)
        info["kandidat"] = len(kandidat)
        lolos: List[Tuple[float, Dict[str, Any]]] = []
        for e in kandidat:
            alasan = self._lolos_hard(e, slot, ctx)
            if alasan:
                info["dibuang"][alasan] = info["dibuang"].get(alasan, 0) + 1
                continue
            lolos.append((self._skor(e, slot, ctx), e))
        if not lolos:
            info["gagal"] = "RestriksiSeleksional"
            return None, info
        lolos.sort(key=lambda kv: kv[0], reverse=True)
        info["alternatif"] = len(lolos)
        pilih = self._pilih_beragam(lolos, info)
        return pilih, info


# ===========================================================================
# L3 — MORFOLOGI & LINEARISASI
# ===========================================================================
KATA_GANTI = {"aku": "aku", "saya": "aku", "kamu": "kamu", "kau": "kau",
              "dia": "dia", "ia": "dia", "kita": "kita", "kami": "kami"}
DETERMINAN = {"ini", "itu"}
PREPOSISI = {"di", "ke", "dari", "pada", "dengan", "untuk", "tentang",
             "kepada", "dalam", "seperti", "karena", "sebagai", "tanpa",
             "bagi", "antara", "terhadap", "oleh"}


class L3:
    def __init__(self, leks: Leksikon, rng: random.Random) -> None:
        self.leks = leks
        self.rng = rng

    # -- morfologi --------------------------------------------------------
    def bentuk_verba(self, dasar: str, voice: str, modus: str) -> str:
        """Realisi diatesis (B7): aktif meN-, pasif di-, ter-, ke-…-an,
        pasif pelaku orang pertama/kedua (kulihat/kaulihat), nom."""
        d = _norm(dasar)
        if not d:
            return ""
        if modus == "ingkar":
            return d
        if voice == "pasif":
            return "di" + d
        if voice == "pasif_1":
            return "ku" + d
        if voice == "pasif_2":
            return "kau" + d
        if voice == "ter":
            return "ter" + d
        if voice == "kean":
            return "ke" + d + "an"
        if voice == "nom":
            n = self.leks.nominalisasi(d)
            return n or d
        return self.leks.nasalisasi(d)

    def bentuk_partikel(self, kata: str, partikel: str) -> str:
        if not partikel:
            return kata
        if partikel == "-nya":
            return kata + "nya"
        if partikel == "-lah":
            return kata + "lah"
        if partikel == "-kah":
            return kata + "kah"
        return kata

    # -- frasa nomina -----------------------------------------------------
    def frasa_nomina(self, isi: Any, ctx: GenContext, topik: bool = False) -> str:
        """Frasa nomina (B9): posesif, demonstrativa, penggolong.

        Posesif/demonstrativa yang sudah ada pada `isi` dipertahankan;
        penggolong (seorang/seekor/sebuah) ditambahkan untuk topik
        berdasarkan tipe lattice.
        """
        if isinstance(isi, Node):
            return self.klausa(isi, ctx, nested=True)
        if not isinstance(isi, str):
            return str(isi or "")
        s = _norm(isi)
        if not s:
            return ""
        # rujukan pronominal
        if s in KATA_GANTI:
            if s in ("aku", "saya"):
                return "aku"
            if s in ("kamu", "kau"):
                return "kau" if not ctx.dekat else "kamu"
            return KATA_GANTI[s]
        if s in ("itu", "ini", "tersebut"):
            return s
        # posesif sudah terpasang (-ku/-mu/-nya): pertahankan
        if s.endswith(("-ku", "-mu", "-nya")) or s.endswith(
                ("ku", "mu", "nya")) and len(s) > 4 and " " not in s:
            # hanya bila bentuk dasarnya dikenal (bukan kata yang kebetulan
            # berakhiran sama, mis. "hanya")
            base = s[:-2] if s.endswith(("ku", "mu")) else s[:-3]
            if base and self.leks.ambil(ctx.bahasa, base) is not None:
                return s
        # topik dari ujaran: mungkin frasa multi-kata → pakai apa adanya
        if " " in s:
            return s
        e = self.leks.ambil(ctx.bahasa, s)
        if e is None:
            return s
        if topik:
            tipe = set(e.get("tipe_semantik") or [])
            if tipe & {"ORANG", "MANUSIA"}:
                return "seorang " + s
            if "HEWAN" in tipe:
                return "seekor " + s
            if tipe & {"BENDA", "EDIBLE", "TAK_EDIBLE", "ALAT", "MAKANAN"}:
                return "sebuah " + s
        return s

    def frasa_adjektiva(self, isi: Any, ctx: GenContext,
                        slot: Optional[Slot] = None,
                        kerangka: Optional[Kerangka] = None,
                        intensitas: float = 0.5) -> str:
        if isinstance(isi, str):
            s = _norm(isi)
            if " " in s:
                return s
            e = self.leks.ambil(ctx.bahasa, s)
            if e is None:
                return s
            # penguat/pelemah berdasarkan intensitas & arousal
            mod = ""
            if slot is not None and slot.modifier and isinstance(e.get("modifier"), dict):
                # tekanan afektif tinggi melumpuhkan penguat: bahasa mendatar.
                if (ctx.arousal > 0.7 or intensitas > 0.8) \
                        and _clip(ctx.tekanan, 0.0, 1.0) < 0.7:
                    kiri = (e["modifier"].get("penguat") or {}).get("kiri") or []
                    if kiri:
                        mod = self.rng.choice(kiri) + " "
                elif ctx.arousal < 0.3 and kerangka is not None and kerangka.node.intensitas < 0.4:
                    kiri = (e["modifier"].get("pelemah") or {}).get("kiri") or []
                    if kiri:
                        mod = self.rng.choice(kiri) + " "
            return mod + s
        return str(isi or "")

    @staticmethod
    def _placeholder(template: str) -> List[str]:
        """Nama slot yang dirujuk template, mis. '{STIMULUS}' -> ['STIMULUS']."""
        out: List[str] = []
        i = 0
        while True:
            s = template.find("{", i)
            if s < 0:
                break
            e = template.find("}", s)
            if e < 0:
                break
            out.append(template[s + 1:e])
            i = e + 1
        return out

    def _render_ekspresi(self, node: Node, spec: Dict[str, Any],
                         b: Dict[str, str], ctx: GenContext) -> str:
        """Render predikat tak-konvensional dari template `ekspresi`.

        Idiom/metafora kontekstual: template dipilih menurut register, dan
        hanya dipakai bila seluruh placeholder-nya terisi (tak pernah bocor
        '{...}'). Bila tak ada yang cocok, jatuh ke template bebas-placeholder.
        """
        eks = spec.get("ekspresi")
        if isinstance(eks, dict):
            templates = list(eks.get(ctx.register) or eks.get("netral")
                             or next(iter(eks.values())))
        else:
            templates = list(eks or [])
        if not templates:
            return f"aku {spec.get('lema', node.predikat.lower())}."
        if node.polaritas == "-" or node.modus == "ingkar":
            return f"aku tidak {spec.get('lema', node.predikat.lower())}."
        cocok = [t for t in templates
                 if all(ph in b for ph in self._placeholder(t))]
        bebas = [t for t in templates if not self._placeholder(t)]
        tpl = cast(str, self.rng.choice(cocok or bebas or templates))
        out = tpl
        for peran, frasa in b.items():
            out = out.replace("{" + peran + "}", frasa)
        # jaring pengaman: buang sisa placeholder tak terisi & rapikan spasi.
        while "{" in out and "}" in out:
            s = out.find("{")
            e = out.find("}", s)
            if e < 0:
                break
            out = out[:s] + out[e + 1:]
        out = " ".join(out.split()).replace(" .", ".").replace(" ,", ",")
        if node.modus == "tanya" and not out.rstrip().endswith("?"):
            out = out.rstrip(".!…") + "?"
        return out

    def _verba(self, node: Node, ctx: GenContext) -> str:
        """Bentuk verba aktif dari lema yang dipilih L2 (fallback: lema frame)."""
        lema = node.lema or (self.leks.predikat.get(node.predikat) or {}).get("lema") \
            or node.predikat.lower()
        if " " in _norm(lema) or "-" in lema:
            return lema
        # lema yang sudah berimbuhan jangan diberi prefiks lagi
        # (mis. "memperingatkan", "bertanya", "mendengar" sudah bentuk jadi).
        if lema.startswith(("mem", "men", "meng", "meny", "menge",
                            "ber", "ter", "di", "me")):
            return lema
        return self.leks.nasalisasi(lema)

    # -- klausa (rekursi maks 1 tingkat) ---------------------------------
    def klausa(self, node: Node, ctx: GenContext, nested: bool = False) -> str:
        spec = self.leks.predikat.get(node.predikat) or {}
        pred_lema = node.lema or spec.get("lema") or node.predikat.lower()
        # susun slot → teks
        bagian: Dict[str, str] = {}
        for a in node.args:
            if a.kosong():
                continue
            if isinstance(a.isi, Node):
                bagian[a.peran] = self.klausa(a.isi, ctx, nested=True)
            elif a.tipe in ("EMOSI", "KUALITAS", "TAKUT", "SENANG", "SEDIH",
                            "MARAH", "MALU", "CINTA", "BENCI", "KESEPIAN",
                            "TENANG", "HARAP", "TERKEJUT", "JIJIK",
                            "KERAGUAN", "KEPERCAYAAN", "LELAH", "BINGUNG",
                            "CURIGA", "HARU"):
                bagian[a.peran] = self.frasa_adjektiva(
                    a.isi, ctx, intensitas=node.intensitas)
            else:
                # Argumen entitas yang berupa kalimat utuh diringkas menjadi
                # frasa nomina (E3) — jangan tempel kalimat mentah.
                isi = a.isi
                if isinstance(isi, str) and " " in _norm(isi) and \
                        a.tipe in ("ENTITAS", "ANIMAT", "FISIK", "BENDA",
                                   "EDIBLE", "TAK_EDIBLE", "MAKHLUK",
                                   "INANIMAT", "ORANG", "HEWAN", "TUMBUHAN",
                                   "TEMPAT", "WAKTU", "PERISTIWA"):
                    from pycos.bahasa.teks import ekstrak_topik as _et
                    ringkas = _et(isi, leksikon=self.leks)
                    isi = ringkas or "itu"
                bagian[a.peran] = self.frasa_nomina(
                    isi, ctx, topik=(a.peran == "TOPIK"))
        # kalimat inti per predikat
        inti = self._kalimat_predikat(node, pred_lema, bagian, ctx)
        # modus tanya: pastikan ada tanda tanya (tanpa menggandakan)
        if node.modus == "tanya" and not inti.rstrip().endswith("?"):
            inti = inti.rstrip(".?!") + "?"
        return inti

    def _kalimat_predikat(self, node: Node, pred: str, b: Dict[str, str],
                          ctx: GenContext) -> str:
        P = node.predikat
        neg = "tidak " if node.polaritas == "-" or node.modus == "ingkar" else ""
        # predikat tak-konvensional (idiom/metafora) dirender dari template frame
        spec_eks = self.leks.predikat.get(node.predikat) or {}
        if spec_eks.get("ekspresi"):
            return self._render_ekspresi(node, spec_eks, b, ctx)
        if P == "HESITASI":
            seb = b.get("SEBAB", "")
            if seb:
                return f"sebentar… soal {seb}, aku perlu berpikir dulu."
            return self.rng.choice(["…sebentar.", "…tunggu.", "hm…"])
        if P in ("RAGU",):
            subj = b.get("EXPERIENCER", "aku")
            prop = b.get("PROPOSISI", "")
            lema = node.lema or "ragu"
            # Lema di luar kosakata ragu (mis. "mendua") diganti "ragu".
            if lema not in ("ragu", "bimbang", "waswas", "ragu-ragu",
                            "gamang", "dilema", "ragu-ragu"):
                lema = "ragu"
            neg = "tidak " if node.modus == "ingkar" else ""
            if prop:
                return f"{subj} {neg}{lema} apakah {prop}."
            return f"{subj} {neg}{lema} sekarang." if not neg \
                else f"{subj} {lema} untuk percaya."
        if P == "PERINGATAN":
            ob = b.get("OBJEK", "")
            sebab = b.get("SEBAB") or getattr(node.arg("SEBAB"), "isi", "")
            sebab = str(sebab).strip().rstrip(" .!?;:")
            v = self._verba(node, ctx)
            # Objek berupa kalimat diringkas; tanpa objek pakai "sana".
            if ob and " " in ob:
                from pycos.bahasa.teks import ekstrak_topik as _et2
                ob = _et2(ob, leksikon=self.leks) or "sana"
            inti = (f"jangan pergi ke {ob}" if ob else "jangan pergi ke sana")
            return (
                f"aku {v} kau: {inti}"
                + (f" karena {sebab}" if sebab else "")
                + ". Aku tidak mau kau kenapa-napa."
            )
        if P == "MENOLAK":
            t = b.get("TINDAKAN", "")
            al = b.get("ALASAN", "")
            v = self._verba(node, ctx)
            s = f"tidak, aku {v}"
            if t:
                s += f" {t}"
            s += "."
            if al:
                s += f" {al.capitalize()}."
            return s
        if P == "INGAT":
            subj = b.get("EXPERIENCER", "aku")
            ep = b.get("EPISODE", "")
            ob = b.get("OBJEK", "")
            v = self._verba(node, ctx)
            anchor = (" malam tadi" if node.anchor == "malam tadi" else "")
            if ep:
                return f"{subj} masih {v}{anchor}: {ep}."
            if ob:
                return f"{subj} masih memikirkan {ob}."
            return f"{subj} {v} sesuatu, tapi kabur."
        if P == "SADAR":
            prop = b.get("PROPOSISI", "")
            if prop:
                return f"aku sadar {prop}."
            return "aku sadar sesuatu, dan itu membuatku hati-hati."
        if P in ("SEDIH", "TAKUT", "MALU", "BENCI", "CINTA", "KESEPIAN",
                 "TENANG", "HARAP", "TERKEJUT", "JIJIK", "RINDU", "YAKIN",
                 "TAHU", "BANGGA", "CEMBURU", "PENASARAN", "HARU"):
            lema = node.lema or P.lower()
            st = b.get("STIMULUS", "") or b.get("TARGET", "")
            # apersepsi gagal menamai (ADA rasa tapi tak bisa dinamai — bukan
            # "kosong"/tubuh sunyi): ketiadaan nama adalah ucapan yang sah;
            # bila ada sensasi tubuh, tubuh melaporkan apa yang tak bisa
            # dinamai pikiran ("ada X yang kurasa, tapi aku tak tahu kenapa").
            if ctx.apersepsi in ("kabut", "gradien", "tanpa_nama"):
                if ctx.tubuh:
                    return f"ada {ctx.tubuh[0]} yang kurasa, tapi aku tak tahu kenapa."
                kal = ctx.apersepsi_kalimat or "aku tidak tahu kenapa aku begini"
                return kal if kal.endswith((".", "!", "?")) else kal + "."
            # tubuh membumikan emosi yang belum punya objek jelas.
            if not st and ctx.tubuh:
                return f"aku {lema}. Aku merasa {ctx.tubuh[0]}."
            if not st:
                return f"aku {lema}."
            # HARAP: "aku berharap X" (bukan "aku harap akan X").
            if P == "HARAP":
                return f"aku berharap {st}."
            # Stimulus berupa kalimat diringkas menjadi frasa nomina (E3).
            if " " in st:
                from pycos.bahasa.teks import ekstrak_topik as _et3
                st = _et3(st, leksikon=self.leks) or "itu"
            spec = self.leks.predikat.get(node.predikat) or {}
            hub = self.rng.choice(spec.get("konektor")
                                  or ["karena", "terhadap", "soal"])
            # "bahwa" hanya untuk klausa, bukan nomina tunggal.
            if hub == "bahwa" and " " not in st:
                hub = "karena"
            if ctx.bahasa == "en":
                hub_en = {"karena": "because", "sebab": "because",
                          "terhadap": "about", "soal": "about",
                          "pada": "about", "tentang": "about",
                          "kepada": "to", "akan": "will",
                          "untuk": "for"}.get(hub, "about")
                return f"I {lema} {hub_en} {st}."
            return f"aku {lema} {hub} {st}."
        if P == "BUTUH":
            subj = b.get("EXPERIENCER", "aku")
            ob = b.get("OBJEK", "")
            v = node.lema or "butuh"
            return f"{subj} {v} {ob}, dan aku tidak mau kehilanganmu."
        if P == "MARAH":
            lema = node.lema or "marah"
            tgt = b.get("TARGET", "")
            if tgt:
                return f"aku {lema} pada {tgt}. Jangan main-main denganku."
            return f"aku {lema}. Kau ingin tahu kenapa?"
        if P == "BERTANYA":
            topik = b.get("TOPIK", "") or b.get("OBJEK", "")
            if not topik:
                return "apa yang sebenarnya terjadi?"
            # Topik yang sudah berupa pertanyaan tidak diberi awalan lagi.
            if "?" in topik:
                return topik if topik.rstrip().endswith("?") else topik + "?"
            # Topik berupa kalimat diringkas menjadi frasa nomina (E3).
            if " " in topik:
                from pycos.bahasa.teks import ekstrak_topik as _et4
                topik = _et4(topik, leksikon=self.leks) or "itu"
            # kata tanya dipilih dari keadaan, bukan tetap
            q = ("kenapa" if ctx.arousal > 0.6 else
                 "bagaimana" if ctx.doubt > 0.5 else
                 "apa")
            if q == "kenapa":
                return f"kenapa {topik}?"
            if q == "bagaimana":
                return f"bagaimana sebenarnya {topik} itu?"
            return f"apa yang sebenarnya terjadi dengan {topik}?" if " " in topik \
                else f"apa itu {topik}?"
        if P == "SENANG":
            lema = node.lema or "senang"
            st = b.get("STIMULUS", "")
            if st:
                if " " in st:
                    from pycos.bahasa.teks import ekstrak_topik as _et5
                    # klausa stimulus dipertahankan; frasa diringkas
                    if st.count(" ") > 2:
                        st = _et5(st, leksikon=self.leks) or st
                spec = self.leks.predikat.get(node.predikat) or {}
                hub = self.rng.choice(spec.get("konektor")
                                      or ["karena", "sebab", "bahwa"])
                if hub == "bahwa" and " " not in st:
                    hub = "karena"
                if ctx.bahasa == "en":
                    hub_en = {"karena": "because", "sebab": "because",
                              "bahwa": "that"}.get(hub, "because")
                    return f"I {lema} {hub_en} {st}."
                return f"aku {lema} {hub} {st}."
            return f"aku {lema} kau masih di sini."
        if P == "BERKATA":
            uj = b.get("UJARAN", "")
            if uj:
                return uj if uj.endswith((".", "!", "?")) else uj + "."
            return "aku belum tahu harus bilang apa."
        if P == "MELIHAT":
            ob = b.get("OBJEK", "")
            if ctx.act == "menyapa_proaktif":
                return ("kau belum berkata apa-apa sejak tadi." if not ob
                        else "kau terlihat melamun. Ada yang mengganggumu?")
            v = self._verba(node, ctx)
            return f"aku {v} {ob}." if ob else f"aku {v} sesuatu."
        # --- cabang valensi untuk predikat tanpa cabang khusus (E11) ---
        _obj = (b.get("OBJEK", "") or b.get("STIMULUS", "")
                or b.get("TARGET", "") or b.get("TOPIK", ""))
        _subj = b.get("EXPERIENCER", b.get("AGENT", "aku"))
        if P == "ADA":
            return f"ada {_obj}." if _obj else "ada sesuatu."
        if P == "ADALAH":
            return f"itu {_obj}." if _obj else "begitulah."
        if P == "DATANG":
            return f"aku datang ke {_obj}." if _obj else "aku datang."
        if P == "PERGI":
            return f"aku pergi ke {_obj}." if _obj else "aku pergi."
        if P == "HILANG":
            return f"{_obj} hilang." if _obj else "aku hilang."
        if P == "INGIN":
            return f"aku ingin {_obj}." if _obj else "aku ingin tahu."
        if P == "JANJI":
            return f"aku janji untuk {_obj}." if _obj else "aku janji."
        if P == "LUPA":
            return f"aku lupa tentang {_obj}." if _obj else "aku lupa."
        if P == "MEMAAFKAN":
            return f"aku memaafkan {_obj or 'dia'}."
        if P == "PERCAYA":
            return f"aku percaya pada {_obj}." if _obj else "aku percaya."
        if P == "PUNYA":
            return f"aku punya {_obj or 'sesuatu'}."
        if P == "MENYESAL":
            return f"aku menyesal karena {_obj}." if _obj else "aku menyesal."
        if P == "MERASA":
            return f"aku merasa {_obj}." if _obj else "aku merasa sesuatu."
        if P in ("MENGKHIANATI", "MEMBUNUH", "MENINGGALKAN", "MEMAKAN",
                 "MENDENGAR", "MEMBUNUH"):
            v = self._verba(node, ctx)
            return f"aku {v} {_obj or 'itu'}."
        if P == "YAKIN":
            return f"aku yakin tentang {_obj}." if _obj else "aku yakin."
        if P == "TAHU":
            return f"aku tahu {_obj}." if _obj else "aku tahu."
        # fallback generik dari kerangka (objek bawaan untuk verba transitif)
        if pred.endswith("kan") and not _obj:
            _obj = "itu"
            return f"{_subj} {neg}{pred} {_obj}."
        return f"{_subj} {neg}{pred}."

    # -- linearisasi dengan pemindahan topik ------------------------------
    def linearisasi(self, kerangka: Kerangka, ctx: GenContext) -> str:
        node = kerangka.node
        inti = self.klausa(node, ctx)
        # topik depan: "apinya, aku takut" — pengalaman yang dirasakan pemain
        # (hindari pengulangan: bila topik sudah ada di inti, jangan tambah).
        topik = ctx.topik_aktif()
        if topik and kerangka.topik_front:
            arg = node.arg(kerangka.topik_front)
            kata_inti = {w.strip(".,!?;:…—–\"'") for w in inti.split()}
            if arg and isinstance(arg.isi, str) and " " not in _norm(arg.isi):
                front = _norm(arg.isi)
                if front and front not in ("aku", "kamu", "kau", "dia", "kita") \
                        and front not in kata_inti:
                    if ctx.bahasa == "en":
                        inti = f"about {front} — {inti}"
                    else:
                        inti = f"soal {front} — {inti}"
        # penahanan sadar: ujaran terbentuk, tapi tak habis diucapkan.
        if ctx.menahan >= 0.6 and inti and inti[-1] not in "…!?":
            inti = inti.rstrip(".") + "…"
        return inti


# ===========================================================================
# ORKESTRATOR — bounded DFS
# ===========================================================================
class Orkestrator:
    """DFS terbatas: L0 → L1 → L2 → L3 dengan alternatif & penurunan anggun."""

    def __init__(self, leks: Leksikon, riwayat: Optional[List[str]] = None
                 ) -> None:
        self.leks = leks
        self.l0 = L0(leks)
        self.l1 = L1(leks)
        self.riwayat = riwayat if riwayat is not None else []
        self._l2: Optional[L2] = None
        self._l3: Optional[L3] = None

    @staticmethod
    def _stabil(s: str) -> int:
        """Hash stabil lintas proses (bukan hash() bawaan yang di-random)."""
        h = 2166136261
        for ch in str(s):
            h = ((h ^ ord(ch)) * 16777619) & 0xFFFFFFFF
        return h

    def _rng(self, ctx: GenContext) -> random.Random:
        return random.Random(((ctx.seed * 2654435761) & 0x7FFFFFFF)
                             ^ (self._stabil(ctx.act) & 0xFFFF))

    def bangun(self, ctx: GenContext) -> Tutur:
        rng = self._rng(ctx)
        self._l2 = L2(self.leks, rng, self.riwayat)
        self._l3 = L3(self.leks, rng)
        trace: List[Dict[str, Any]] = []
        node, turun = self.l0.rencana(ctx)
        trace.append({"L0": {"predikat": node.predikat,
                             "args": [a.peran for a in node.args],
                             "penurunan": turun}})
        # DFS: coba node, lalu versi yang lebih sederhana (buang arg opsional)
        alternatif: List[Node] = [node]
        for i in range(len(node.args) - 1, -1, -1):
            if node.args[i].opsional:
                salinan = Node(node.predikat,
                               [a for j, a in enumerate(node.args) if j != i],
                               node.modus, node.aspek, node.polaritas,
                               node.intensitas, node.anchor, node.komplemen,
                               node.lema)
                alternatif.append(salinan)
        for depth, kandidat in enumerate(alternatif):
            kerangka, cat1 = self.l1.realisasi(kandidat, ctx)
            if kerangka is None:
                trace.append({"L1": {"depth": depth, "gagal": cat1}})
                continue
            trace.append({"L1": {"depth": depth,
                                 "slot": [s.nama for s in kerangka.slot],
                                 "voice": kerangka.voice,
                                 "catatan": cat1}})
            # L2a — lema predikat dipilih dari keadaan
            pl, pinfo = self._l2.pilih_predikat(kandidat, ctx)
            if pl is not None:
                kandidat.lema = pl["lema"]
                trace.append({"L2-predikat": pinfo})
            gagal = False
            urutan_slot = list(kerangka.slot)
            rng.shuffle(urutan_slot)
            trace.append({"L2-urutan": [s.nama for s in urutan_slot]})
            for slot in urutan_slot:
                if not slot.terisi:
                    continue
                arg = slot.isi if isinstance(slot.isi, Arg) else None
                # hanya slot ber-mode "isi" yang dipilihkan lema; rujukan
                # ("aku", "api", episode) lewat begitu saja
                if arg is None or arg.mode != "isi":
                    continue
                isi = arg.isi
                if isinstance(isi, Node) or slot.kelas_wajib == "SBAR":
                    continue
                if isinstance(isi, str) and " " in _norm(isi):
                    continue
                pilih, info = self._l2.pilih(slot, ctx)
                trace.append({"L2": info})
                if pilih is None:
                    gagal = True
                    break
                arg.isi = pilih["lema"]
            if gagal:
                continue
            teks = self._l3.linearisasi(kerangka, ctx)
            trace.append({"L3": {"teks": teks}})
            if teks and teks.strip():
                # G1: pemeriksa kegramatikalan — kandidat yang gagal berat
                # ditolak dan alternatif berikutnya dicoba (batas DFS).
                masalah = _periksa_gramatika(teks, self.leks)
                trace.append({"G1": {"masalah": masalah}})
                berat = [m for m in masalah if m in (
                    "tanda_baca_ganda", "kata_berulang", "preposisi_ganda",
                    "adjektiva_bahwa", "afiks_tak_valid",
                    "verba_transitif_tanpa_objek")]
                if berat and depth < len(alternatif) - 1:
                    continue
                # E0: jejak INPUT → FILTER → FORMATION → OUTPUT.
                from pycos.bahasa.teks import jejak_pembentukan as _jejak
                trace.append({"E0": _jejak(
                    input_teks=ctx.topik,
                    keadaan={"emosi": list(ctx.emosi), "valensi": ctx.valensi,
                             "arousal": ctx.arousal, "doubt": ctx.doubt,
                             "apersepsi": ctx.apersepsi,
                             "tekanan": ctx.tekanan},
                    pengetahuan={"core": list(ctx.core),
                                 "timeline": list(ctx.timeline)},
                    situasi={"topik": ctx.topik, "spotlight": list(ctx.spotlight)},
                    sosial={"kepada": ctx.kepada, "dekat": ctx.dekat,
                            "register": ctx.register},
                    bahasa_kognisi={"act": ctx.act, "predikat": kandidat.predikat,
                                    "voice": kerangka.voice},
                    biologis={"tubuh": list(ctx.tubuh)},
                    medium={"bahasa": ctx.bahasa},
                    percakapan={"inner": ctx.inner, "niat": ctx.niat},
                    output_teks=teks.strip(), act=ctx.act,
                    alasan_act="act dari keadaan internal; topik hanya faktor")})
                return Tutur(teks=teks.strip(), status="SUKSES",
                             act=ctx.act, trace=trace)
        return Tutur(teks="", status="MENYERAH", act=ctx.act, trace=trace)


# ===========================================================================
# SA_SP — ANALISIS SEMANTIK-PRAGMATIK
# ===========================================================================
class SASPAnalyzer:
    """Analisis dua lapis: isi literal tanpa konteks + maksud dalam konteks.

    Ini sengaja bukan parser sintaksis lengkap. Ia menyimpan *pemisahan* yang
    penting bagi Pycos: proposisi semantik dibangun dari ujaran saja, sedangkan
    tindak tutur dan implikatur adalah hipotesis yang dapat berubah mengikuti
    situasi, relasi, dan tindakan yang tersedia. Inferensi pragmatik tidak
    pernah dilaporkan sebagai fakta pasti.

    ``analisis()`` menerima ``konteks`` opsional berupa mapping (misalnya
    ``{"ruangan_panas": True, "pendingin_ruangan": True}``) atau teks bebas.
    Analyzer dapat memakai Leksikon Pycos untuk menampilkan kelas dan tipe
    semantik kata yang dikenali, tetapi tetap bekerja tanpa berkas leksikon.
    """

    _TOKEN = re.compile(r"[\wÀ-ÿ]+", flags=re.UNICODE)
    _PANAS = {"panas", "gerah", "terik", "hangat"}
    _LUAR = {"luar", "di luar", "luar ruangan", "di luar ruangan"}
    _NEGASI = {"tidak", "tak", "bukan", "nggak", "enggak", "gak"}
    _PENGUAT = {"sangat", "amat", "sekali", "terlalu", "benar-benar"}
    _STOP = {"di", "ke", "dari", "itu", "ini", "yang", "dan", "atau",
             "sangat", "sangatlah", "amat", "sekali", "terlalu", "lah",
             "kah", "pun", "aku", "saya", "kamu", "kau", "dia", "kami",
             "kita", "para", "adalah", "sedang", "telah", "akan"}

    _AKSI_PANAS = (
        ("menyalakan_pendingin_ruangan", "nyalakan pendingin ruangan", "ac"),
        ("membuka_jendela", "buka jendela", "jendela"),
        ("menggunakan_kipas", "gunakan kipas", "kipas"),
    )

    def __init__(self, leksikon: Optional[Leksikon] = None,
                 bahasa: str = "id") -> None:
        self.leksikon = leksikon
        self.bahasa = str(bahasa or "id")
        self.jumlah_analisis = 0
        self.analisis_terakhir: Optional[Dict[str, Any]] = None

    @staticmethod
    def _konteks(konteks: Any) -> Dict[str, Any]:
        if isinstance(konteks, Mapping):
            return dict(konteks)
        if konteks is None:
            return {}
        return {"situasi": str(konteks)}

    @staticmethod
    def _bool(konteks: Dict[str, Any], *nama: str) -> bool:
        return any(bool(konteks.get(n)) for n in nama)

    @staticmethod
    def _available(konteks: Dict[str, Any]) -> List[str]:
        raw = (konteks.get("available_actions")
               or konteks.get("aksi_tersedia")
               or konteks.get("affordances") or [])
        if isinstance(raw, str):
            return [raw.lower()]
        hasil = []
        try:
            for item in raw:
                if isinstance(item, Mapping):
                    item = item.get("name", item.get("aksi", item.get("id", "")))
                if item:
                    hasil.append(str(item).lower())
        except TypeError:
            pass
        return hasil

    def _leksikal(self, kata: Sequence[str]) -> List[Dict[str, Any]]:
        hasil: List[Dict[str, Any]] = []
        if self.leksikon is None:
            return hasil
        for w in kata:
            ent = self.leksikon.ambil(self.bahasa, w)
            if not ent:
                continue
            hasil.append({
                "lema": ent.get("lema", w),
                "kelas": list(ent.get("kelas", [])),
                "tipe_semantik": list(ent.get("tipe_semantik", [])),
                "sinonim": list(ent.get("sinonim", []))[:6],
                "catatan_konteks": list(ent.get("catatan_konteks", []))[:4],
            })
        return hasil

    def _semantik(self, ujaran: str, kata: Sequence[str]) -> Dict[str, Any]:
        """Lapisan kontekstual-bebas: hanya memakai bentuk ujarannya."""
        from pycos.bahasa.teks import (
            cakupan_negasi as _cn, jenis_kalimat as _jk,
            jenis_pertanyaan as _jp, tokenisasi as _tk,
            urai_subjek_predikat as _usp, ekstrak_entitas as _ee,
            ekstrak_topik as _et,
        )
        toks = _tk(ujaran)
        low = " ".join(kata)
        tipe = _jk(ujaran, toks, self.leksikon)
        neg_flags = _cn(toks)
        negasi = any(neg_flags[i] for i, t in enumerate(toks)
                     if t.jenis == "kata")
        penguat = [w for w in kata if w in self._PENGUAT
                   or w == "sangatlah" or w.startswith("sangatlah")]

        panas_luar = (any(frasa in low for frasa in self._LUAR)
                      and any(w in self._PANAS for w in kata))
        if panas_luar:
            adj = next((w for w in kata if w in self._PANAS), "panas")
            polaritas = "negatif" if negasi else "positif"
            intensitas = min(1.0, 0.55 + 0.15 * len(penguat))
            if "terlalu" in kata and not negasi:
                intensitas = 1.0
            proposisi: Dict[str, Any] = {"subjek": "suhu udara di luar ruangan",
                         "predikat": "tinggi" if not negasi else "tidak_tinggi",
                         "atribut_leksikal": adj, "polaritas": polaritas,
                         "intensitas": round(intensitas, 3)}
            makna = ("Kalimat menyatakan bahwa suhu udara di luar ruangan "
                     + ("tidak tinggi." if negasi else "sedang tinggi."))
        else:
            # Pengurai dangkal subjek–predikat–objek (D4) menggantikan
            # pembagian posisi yang memberi subjek "lapar" untuk "Aku lapar".
            urai = _usp(toks, self.leksikon)
            predikat = urai.get("predikat") or (kata[-1] if kata else "")
            subjek = urai.get("subjek")
            proposisi = {"subjek": subjek or None,
                         "predikat": predikat or None,
                         "objek": urai.get("objek"),
                         "keterangan": urai.get("keterangan"),
                         "polaritas": "negatif" if negasi else "positif",
                         "intensitas": round(min(1.0, 0.5 + 0.15 * len(penguat)), 3)}
            makna = (f"Ujaran mengatribusikan makna literal '{predikat}'"
                     + (f" kepada '{subjek}'." if subjek else ".")
                     if predikat else "Ujaran kosong; tidak ada proposisi literal.")

        return {"jenis_kalimat": tipe, "proposisi": proposisi,
                "makna_literal": makna, "negasi": negasi,
                "penguat": penguat,
                "jenis_pertanyaan": _jp(ujaran, toks) if tipe == "interogatif" else {},
                "entitas": _ee(ujaran, toks, self.leksikon),
                "topik": _et(ujaran, toks, self.leksikon),
                "leksikal": self._leksikal(kata),
                "bebas_konteks": True}

    def _pragmatik(self, ujaran: str, kata: Sequence[str],
                   semantik: Dict[str, Any], konteks: Dict[str, Any]
                   ) -> Dict[str, Any]:
        from pycos.bahasa.teks import tindak_tutur_skor as _tts
        low = " ".join(kata)
        tersedia = self._available(konteks)
        jenis = "asertif"
        bukti: List[str] = []
        maksud: List[Dict[str, Any]] = []
        kalimat = semantik.get("jenis_kalimat")
        # Skor tindak tutur diperluas (D5); label utama tetap kompatibel.
        skor_tindak = _tts(ujaran, semantik=semantik)
        request_markers = {"tolong", "mohon", "silakan", "please"}
        ability_markers = {"bisa", "dapat", "maukah", "sudi", "boleh"}
        imperative = kalimat == "imperatif" or bool(
            kata and kata[0] in request_markers) or low.startswith(
            ("jangan ", "tolong ", "mohon ", "silakan "))
        if imperative:
            jenis = "permintaan_atau_perintah_eksplisit"
            bukti.append("penanda imperatif/permintaan tampak pada bentuk ujaran")
        elif kalimat == "interogatif":
            if any(w in ability_markers for w in kata):
                jenis = "permintaan_tidak_langsung"
                maksud.append({"jenis": jenis,
                               "tujuan": "meminta pendengar melakukan tindakan",
                               "confidence": 0.72,
                               "diturunkan_dari": "pertanyaan kemampuan/kesediaan"})
                bukti.append("pertanyaan kemampuan atau kesediaan dapat berfungsi sebagai permintaan")
            else:
                jenis = "permintaan_informasi"
                bukti.append("intonasi/tanda tanya mengemas ujaran sebagai pertanyaan")
        # Tindak khusus (salam/pujian/hinaan/ancaman/dll) dicatat sebagai
        # maksud berskor tanpa menimpa label utama di atas.
        for nama, skor in sorted(skor_tindak.items(),
                                 key=lambda kv: -kv[1]):
            if skor >= 0.7 and nama not in ("asertif", "pertanyaan"):
                maksud.append({"jenis": nama, "confidence": round(skor, 3),
                               "status": "hipotesis, bukan fakta"})

        # Hints konvensional: informasi cuaca/suhu sering relevan sebagai
        # keluhan atau permintaan perubahan lingkungan. Ini tetap inferensi.
        proposisi = semantik.get("proposisi") or {}
        luar_panas = (proposisi.get("predikat") == "tinggi"
                      and "luar" in str(proposisi.get("subjek", "")))
        if luar_panas and not semantik.get("negasi"):
            kontekstual = self._bool(
                konteks, "ruangan_panas", "inside_hot", "butuh_tindakan",
                "need_action", "listener_can_act", "pendengar_bisa_bertindak")
            faktor = 0.40 + (0.18 if kontekstual else 0.0)
            if konteks.get("shared_context") or konteks.get("common_ground"):
                faktor += 0.08
                bukti.append("common ground mendukung relevansi keluhan")
            if konteks.get("relasi") in ("akrab", "dekat", "percaya"):
                faktor += 0.04
                bukti.append("relasi dekat membuat permintaan tidak langsung lebih wajar")
            faktor = min(0.9, faktor)
            pilihan = []
            for nama, teks, petunjuk in self._AKSI_PANAS:
                if tersedia and not any(petunjuk in aksi or nama in aksi
                                        for aksi in tersedia):
                    continue
                cocok = any(petunjuk in aksi or nama in aksi for aksi in tersedia)
                skor = min(0.95, faktor + (0.16 if cocok else 0.0))
                pilihan.append({"aksi": nama, "contoh_respons": teks,
                                "confidence": round(skor, 3),
                                "layak_konteks": bool(cocok) if tersedia else None})
            # Validasi/empati adalah respons sosial yang juga mungkin, bukan
            # tindakan fisik dan bukan interpretasi tunggal.
            pilihan.append({"aksi": "memvalidasi_keluhan",
                            "contoh_respons": "iya, memang terasa panas",
                            "confidence": round(min(0.9, faktor - 0.03), 3),
                            "layak_konteks": None})
            maksud.append({"jenis": "permintaan_tidak_langsung",
                           "tujuan": "mengurangi ketidaknyamanan panas atau memperoleh respons",
                           "confidence": round(faktor, 3),
                           "tindakan_kandidat": pilihan,
                           "status": "hipotesis, bukan fakta"})
            maksud.append({"jenis": "keluhan_atau_mencari_validasi",
                           "tujuan": "mendapat empati/konfirmasi",
                           "confidence": round(min(0.85, faktor - 0.02), 3),
                           "status": "hipotesis, bukan fakta"})
            bukti.append("pernyataan suhu dapat menjadi hint yang relevan untuk mengubah kenyamanan")
            if jenis == "asertif":
                jenis = "asertif_dengan_kemungkinan_hint"

        if "terima kasih" in low or ("terima" in kata and "kasih" in kata):
            maksud.append({"jenis": "ekspresif_terima_kasih",
                           "confidence": 0.85})
        if any(w in kata for w in ("maaf", "menyesal")):
            maksud.append({"jenis": "ekspresif_permohonan_maaf",
                           "confidence": 0.8})

        marker_humor = any(w in kata for w in
                           ("haha", "hahaha", "wkwk", "lucu", "bercanda",
                            "ironi", "ironis", "sarkas", "absurd"))
        marker_ironi = any(w in kata for w in ("ironi", "ironis", "sarkas"))
        konteks_humor = self._bool(konteks, "bercanda", "joke", "humor")
        frames = {
            "literal": semantik.get("makna_literal", ""),
            "sosial": maksud[0] if maksud else None,
            "dua_bingkai": bool(maksud),
            "potensi_humor": bool(marker_humor or konteks_humor),
            "potensi_ironi": bool(marker_ironi or konteks.get("ironi")),
        }
        return {"tindak_tutur": jenis,
                "maksud_tersirat": maksud,
                "bukti_kontekstual": bukti,
                "tindakan_tersedia": tersedia,
                "bingkai": frames,
                "bergantung_konteks": True}

    def analisis_literal(self, ujaran: Any) -> Dict[str, Any]:
        """Makna/proposisi literal; sengaja tidak menerima konteks."""
        asli = str(ujaran or "").strip()
        kata = [w.lower() for w in self._TOKEN.findall(asli)]
        return self._semantik(asli, kata)

    literal = analisis_literal
    analyze_literal = analisis_literal

    def analisis_pragmatik(self, ujaran: Any, konteks: Any = None,
                           semantik: Optional[Mapping[str, Any]] = None
                           ) -> Dict[str, Any]:
        """Inferensi konteks/tindak tutur, terpisah dan bersifat hipotesis."""
        asli = str(ujaran or "").strip()
        kata = [w.lower() for w in self._TOKEN.findall(asli)]
        sem = dict(semantik) if isinstance(semantik, Mapping) else self.analisis_literal(asli)
        return self._pragmatik(asli, kata, sem, self._konteks(konteks))

    pragmatic = analisis_pragmatik
    analyze_pragmatic = analisis_pragmatik
    analisis_maksud_kontekstual = analisis_pragmatik

    def analisis_tindak_tutur(self, ujaran: Any, konteks: Any = None) -> Dict[str, Any]:
        prag = self.analisis_pragmatik(ujaran, konteks)
        return {"tindak_tutur": prag.get("tindak_tutur"),
                "maksud_tersirat": prag.get("maksud_tersirat", []),
                "bukti_kontekstual": prag.get("bukti_kontekstual", []),
                "bergantung_konteks": True}

    speech_act = analisis_tindak_tutur

    def analisis(self, ujaran: Any, konteks: Any = None) -> Dict[str, Any]:
        """Kembalikan semantik literal dan pragmatik sebagai lapisan terpisah."""
        asli = str(ujaran or "").strip()
        sem = self.analisis_literal(asli)
        prag = self.analisis_pragmatik(asli, konteks, semantik=sem)
        hasil = {"sistem": "sa_sp/1", "ujaran": asli,
                 "semantik": sem, "pragmatik": prag}
        self.jumlah_analisis += 1
        self.analisis_terakhir = hasil
        return hasil

    analyze = analisis


# ===========================================================================
# FACADE
# ===========================================================================
# Cache leksikon bersama per proses. Leksikon tidak dimutasi selama generasi,
# jadi satu objek dapat dipakai banyak NPC. Tanpa cache, setiap NPC yang
# mengaktifkan presentasi generatif mem-parse JSON ~4,3 MB (sekitar 0,15 detik
# dan 17 MB per engine). Kunci cache memuat mtime dan ukuran, sehingga berkas
# yang berubah di disk dimuat ulang.
_CACHE_LEKSIKON: Dict[Tuple[str, int, int], "Leksikon"] = {}
_KUNCI_CACHE_LOCK = threading.Lock()


def muat_leksikon(path: str) -> "Leksikon":
    """Muat `Leksikon` dari berkas JSON, memakai cache per proses."""
    jalur = os.path.realpath(path)
    st = os.stat(jalur)
    kunci = (jalur, st.st_mtime_ns, st.st_size)
    with _KUNCI_CACHE_LOCK:
        hit = _CACHE_LEKSIKON.get(kunci)
    if hit is not None:
        return hit
    with open(jalur, "r", encoding="utf-8") as f:
        leks = Leksikon(json.load(f))
    with _KUNCI_CACHE_LOCK:
        for lama in [k for k in _CACHE_LEKSIKON if k[0] == jalur and k != kunci]:
            del _CACHE_LEKSIKON[lama]  # versi berkas lama tidak perlu disimpan
        _CACHE_LEKSIKON[kunci] = leks
    return leks


def kosongkan_cache_leksikon() -> None:
    """Buang cache leksikon proses ini (berguna untuk tolok dan pengujian)."""
    with _KUNCI_CACHE_LOCK:
        _CACHE_LEKSIKON.clear()


class TuturEngine:
    def __init__(self, path: Optional[str] = None,
                 leksikon: Optional[Leksikon] = None) -> None:
        self.leks: Optional[Leksikon] = None
        self.path = path
        if leksikon is not None:
            self.leks = leksikon
        elif path and os.path.exists(path):
            self.leks = muat_leksikon(path)
        self.orkestrator: Optional[Orkestrator] = None
        self.riwayat: List[str] = []
        self.trace_terakhir: List[Dict[str, Any]] = []
        self.analis_sa_sp = SASPAnalyzer(self.leks)

    def tersedia(self) -> bool:
        return self.leks is not None

    def info(self) -> Dict[str, Any]:
        if not self.leks:
            return {"aktif": False}
        return {"aktif": True, "jumlah_lema": len(self.leks.entri),
                "predikat": len(self.leks.predikat)}

    def ucap(self, ctx: GenContext) -> Optional[Tutur]:
        if not self.leks:
            return None
        if self.orkestrator is None:
            self.orkestrator = Orkestrator(self.leks, self.riwayat)
        t = self.orkestrator.bangun(ctx)
        self.trace_terakhir = t.trace
        return t

    def analisis_sa_sp(self, ujaran: Any,
                       konteks: Any = None) -> Dict[str, Any]:
        """Jalankan analisis semantik-pragmatik pada ujaran masuk/keluar."""
        return self.analis_sa_sp.analisis(ujaran, konteks)

    analyze_sa_sp = analisis_sa_sp

    def analisis_literal_sa_sp(self, ujaran: Any) -> Dict[str, Any]:
        return self.analis_sa_sp.analisis_literal(ujaran)

    analyze_literal_sa_sp = analisis_literal_sa_sp

    def analisis_pragmatik_sa_sp(self, ujaran: Any,
                                 konteks: Any = None) -> Dict[str, Any]:
        return self.analis_sa_sp.analisis_pragmatik(ujaran, konteks)

    analyze_pragmatic_sa_sp = analisis_pragmatik_sa_sp
    analisis_maksud_kontekstual_sa_sp = analisis_pragmatik_sa_sp


def sa_sp(ujaran: Any, konteks: Any = None,
          leksikon: Optional[Leksikon] = None) -> Dict[str, Any]:
    """Fungsi ringkas untuk memakai sistem analisis ``sa_sp`` secara mandiri."""
    return SASPAnalyzer(leksikon).analisis(ujaran, konteks)


def sa_sp_literal(ujaran: Any,
                  leksikon: Optional[Leksikon] = None) -> Dict[str, Any]:
    """API ringkas untuk semantik literal yang bebas konteks."""
    return SASPAnalyzer(leksikon).analisis_literal(ujaran)


def sa_sp_pragmatik(ujaran: Any, konteks: Any = None,
                    leksikon: Optional[Leksikon] = None) -> Dict[str, Any]:
    """API ringkas untuk maksud/tindak tutur dalam konteks."""
    return SASPAnalyzer(leksikon).analisis_pragmatik(ujaran, konteks)


# ===========================================================================
# jembatan: bangun GenContext dari objek Presentasi/Naluri (opsional)
# ===========================================================================
def konteks_dari_presentasi(p: Any, act: str, kepada: Any = None,
                            topik: Optional[str] = None,
                            masuk: bool = False,
                            seed_offset: int = 0) -> GenContext:
    """Petakan keadaan Presentasi/Naluri → GenContext (tanpa impor keras)."""
    def _call(name: str, default: Any = None) -> Any:
        fn = getattr(p, name, None)
        if callable(fn):
            try:
                return fn()
            except Exception:
                return default
        return default

    valensi = arousal = 0.0
    try:
        m = p.naluri.mood()
        valensi = float(getattr(m, "valence", 0.0))
        arousal = float(getattr(m, "arousal", 0.0))
    except Exception:
        pass
    spotlight: List[str] = []
    ks = getattr(p.naluri, "kesadaran", None)
    if ks is not None:
        try:
            spotlight = [str(c.get("content", "")) for c in
                         (getattr(ks, "spotlight", []) or [])][:3]
        except Exception:
            spotlight = []
    timeline: List[str] = []
    core: List[str] = []
    if ks is not None:
        try:
            timeline = [str(x.get("ringkas", "")) for x in
                        (getattr(ks, "timeline", []) or [])][-6:]
            core = [str(x.get("ringkas", "")) for x in
                    (getattr(ks, "core_memory", []) or [])][-3:]
        except Exception:
            pass
    values: List[str] = []
    boundaries: List[str] = []
    dissonance: List[str] = []
    if ks is not None:
        try:
            values = [k for k, _ in sorted(
                (getattr(ks, "values", {}) or {}).items(),
                key=lambda kv: -float(kv[1]))][:3]
            boundaries = [str(x) for x in
                          (getattr(ks, "boundaries", []) or [])][-3:]
            dissonance = [str(k) for k in (getattr(ks, "dissonance", {}) or {})][:2]
        except Exception:
            pass
    grief: List[str] = []
    try:
        g = getattr(ks, "grief", {}) if ks is not None else {}
        grief = [str(k) for k in (g or {})][:2]
    except Exception:
        pass
    attention_fatigue = 0.0
    if ks is not None:
        try:
            atensi = ks.attention_state()
            attention_fatigue = (_clip(atensi.get("fatigue", 0.0))
                                 if atensi.get("aktif", True) else 0.0)
        except Exception:
            pass
    # --- dimensi state internal baru (defensif; default netral) ---
    n = getattr(p, "naluri", p)            # Naluri (mesin emosi/state)
    # emosi dominan → label (TAKUT/MARAH/SENANG/SEDIH/PENASARAN)
    emosi_lbl: List[str] = []
    es: Dict[str, float] = {}
    try:
        es = dict(n.emosi_state() or {})
        for nama, nilai in sorted(es.items(), key=lambda kv: -float(kv[1]))[:2]:
            if float(nilai) >= 0.25:
                emosi_lbl.append(str(nama).upper())
    except Exception:
        pass
    # tekanan afektif = beban ko-aktivasi dua emosi teratas
    tekanan = _clip(sum(sorted((float(v) for v in es.values()),
                               reverse=True)[:2]), 0.0, 1.0)
    # apersepsi: sistem boleh gagal menamai perasaannya (itu sebuah state)
    apersepsi = apersepsi_kalimat = ""
    try:
        fn_ap = getattr(n, "apersepsi_state", None)
        if callable(fn_ap):
            st = fn_ap() or {}
            apersepsi = str(st.get("modus") or "")
            apersepsi_kalimat = str(st.get("kalimat") or "")
    except Exception:
        pass
    # penahanan sadar (withholding): dorongan tutur yang sengaja ditahan
    menahan = 0.0
    try:
        ws = (ks.withholding_state() if ks is not None
              and hasattr(ks, "withholding_state") else {}) or {}
        if ws.get("aktif"):
            menahan = _clip(0.55 + 0.1 * int(ws.get("jumlah", 0)), 0.0, 0.9)
    except Exception:
        pass
    # sensasi tubuh dominan (tubuh mendahului kognisi). `felt_state` bisa
    # berupa method ATAU property/dict tergantung build — tangani keduanya.
    tubuh_lbl: List[str] = []
    try:
        fs_attr = getattr(ks, "felt_state", None) if ks is not None else None
        fs = (fs_attr() if callable(fs_attr) else dict(fs_attr or {})) or {}
        for nama, nilai in sorted(fs.items(), key=lambda kv: -float(kv[1]))[:1]:
            if float(nilai) >= 0.3:
                tubuh_lbl.append(str(nama))
    except Exception:
        pass
    reg = "netral"
    label = "netral"
    if kepada is not None:
        fn = getattr(p, "_label_rel", None)
        if callable(fn):
            try:
                label = str(fn(kepada))
            except Exception:
                label = "netral"
    dekat = label in ("akrab", "suka", "percaya")
    # register (F2): persona formal/santai/netral → ragam formal/akrab/
    # netral (tiga register persona dipetakan, bukan hanya akrab/netral).
    # Tanpa persona pada presentasi/naluri, ragam mengikuti relasi.
    reg = ""
    for pembawa in (getattr(p, "persona", None),
                    getattr(getattr(p, "naluri", None), "persona", None)):
        reg_p = getattr(pembawa, "register", None) if pembawa is not None else None
        if isinstance(reg_p, str) and reg_p.strip():
            reg = reg_p.strip().lower()
            break
    if reg == "formal":
        reg = "formal"
    elif reg == "santai":
        reg = "akrab"
    elif reg == "netral":
        reg = "netral"
    else:
        reg = "akrab" if dekat else "netral"
    # bahasa (F2): dari konfigurasi (`params["bahasa"]` presentasi atau
    # naluri), bukan selalu "id".
    bahasa = "id"
    for sumber in (getattr(p, "params", None),
                   getattr(getattr(p, "naluri", None), "params", None)):
        if isinstance(sumber, Mapping):
            b = str(sumber.get("bahasa", "") or "").strip().lower()
            if b:
                bahasa = b
                break
    refusal = ""
    ref = _call("_refusal")
    if isinstance(ref, dict):
        refusal = str(ref.get("alasan", ""))
    return GenContext(
        act=act, bahasa=bahasa, register=reg,
        topik=str(topik or ""), kepada=str(getattr(kepada, "name", kepada) or ""),
        dekat=dekat,
        spotlight=tuple(x for x in spotlight if x),
        timeline=tuple(x for x in timeline if x),
        core=tuple(x for x in core if x),
        values=tuple(values), boundaries=tuple(boundaries),
        grief=tuple(grief), dissonance=tuple(dissonance),
        doubt=float(_call("_doubt", 0.0) or 0.0),
        agency=float(_call("_agency", 0.5) or 0.5),
        valensi=valensi, arousal=arousal,
        mortality=float(_call("_mortality", 0.0) or 0.0),
        inner=str(_call("_inner_speech", "") or ""),
        permintaan=str(topik or ""),
        refusal=refusal,
        seed=(int(getattr(p.naluri, "tick_count", 0)) * 17
              + int(seed_offset) * 7919),
        attention_fatigue=attention_fatigue,
        emosi=tuple(emosi_lbl),
        apersepsi=apersepsi, apersepsi_kalimat=apersepsi_kalimat,
        tekanan=tekanan, menahan=menahan, tubuh=tuple(tubuh_lbl),
    )


# ===========================================================================
# CIRI LINGUISTIK UJARAN (analisis dangkal berbasis leksikon; dulu modul
# tersendiri di subsistem selaras)
#
# Analisis ini dangkal dan berbasis leksikon. Ia tidak memakai parsing dan
# tidak memahami makna. Ciri yang diukur:
#
# * **polaritas**  — (positif − negatif) / (positif + negatif) dari kata
#   sentimen. Kata sentimen dikenali juga dalam bentuk berimbuhan sederhana
#   (mis. "menyenangkan" → "senang", "mengecewakan" → "kecewa"). Kata negasi
#   (tidak, tak, bukan, belum, jangan, tiada, enggak, nggak, gak) hingga
#   **tiga token** sebelum kata sentimen membalik polaritasnya, tetapi
#   pencarian negasi **berhenti di tanda baca** (`, . ! ? ; :`), sehingga
#   "tidak tahu. aku senang" tidak dibalik.
# * **formalitas** — (formal − informal) / (formal + informal) dari kata
#   register.
# * **intensitas** — campuran tanda seru, kata penguat, dan proporsi huruf
#   kapital.
# * **keraguan**   — proporsi kata pelunak per token.
#
# Leksikon dapat diganti host lewat `LeksikonCiri.from_dict` /
# `LeksikonCiri.dari_berkas`. Ciri tanpa bukti bernilai `None`, bukan 0.
#
# Batasan yang tetap ada: sarkasme dan ironi tidak terdeteksi; negasi di luar
# jendela tiga token tidak dibalik; morfologi hanya menangani afiks umum.
# ===========================================================================
# Kata (huruf Unicode, boleh dengan tanda hubung) atau tanda baca pemisah klausa.
_TOKEN_CIRI = re.compile(r"[^\W\d_]+(?:-[^\W\d_]+)*|[,.!?;:]")
_BATAS_KLAUSA = "|"
JENDELA_NEGASI = 3

_KATEGORI = ("positif", "negatif", "pelunak", "penguat", "formal", "informal",
             "negasi")


def _fs(*kata: str) -> FrozenSet[str]:
    return frozenset(kata)


@dataclass(frozen=True)
class LeksikonCiri:
    """Kumpulan kata per kategori ciri linguistik. Entri disimpan huruf kecil."""

    positif: FrozenSet[str]
    negatif: FrozenSet[str]
    pelunak: FrozenSet[str]
    penguat: FrozenSet[str]
    formal: FrozenSet[str]
    informal: FrozenSet[str]
    negasi: FrozenSet[str]

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "LeksikonCiri":
        """Bentuk leksikon dari dict; setiap kategori wajib berupa daftar string."""
        hanya_kunci(dict(data), _KATEGORI, "leksikon")
        kumpulan: Dict[str, FrozenSet[str]] = {}
        for kategori in _KATEGORI:
            if kategori not in data:
                raise ValueError("leksikon wajib memuat kategori {!r}".format(kategori))
            isi = data[kategori]
            if isinstance(isi, str) or not isinstance(isi, (list, tuple, set, frozenset)):
                raise ValueError("kategori {!r} harus daftar string".format(kategori))
            kata_kata = []
            for k in isi:
                kata = teks_wajib(k, "kata di {}".format(kategori)).lower()
                if len(kata.split()) != 1:
                    # pencocokan bekerja per token; frasa tidak akan pernah cocok
                    raise ValueError(
                        "kata di {} harus satu token, bukan frasa: {!r}".format(kategori, kata))
                kata_kata.append(kata)
            kumpulan[kategori] = frozenset(kata_kata)
        return cls(**kumpulan)

    @classmethod
    def dari_berkas(cls, path: str) -> "LeksikonCiri":
        with open(path, "r", encoding="utf-8") as f:
            return cls.from_dict(json.load(f))

    def to_dict(self) -> Dict[str, List[str]]:
        return {k: sorted(getattr(self, k)) for k in _KATEGORI}

    def kanonik(self, kata: str, kategori: str) -> Optional[str]:
        """Kembalikan bentuk dasar `kata` yang ada di `kategori`, atau None.

        Mencoba bentuk asli, lalu membuang klitik (-nya, -lah, -kah, -pun, -ku,
        -mu), sufiks (-kan, -an, -i), dan prefiks (ber-, ter-, per-, ke-, se-,
        di-, pe-, me-/meng-/meny-/men-/mem- dengan pemulihan huruf awal).
        """
        himpunan = getattr(self, kategori)
        for calon in _kandidat_dasar(kata):
            if calon in himpunan:
                return calon
        return None


_KLITIK = ("nya", "lah", "kah", "pun", "ku", "mu")
_SUFIKS = ("kan", "an", "i")
_PREFIKS: Tuple[Tuple[str, str], ...] = (
    ("meny", "s"), ("peny", "s"), ("meng", "k"), ("men", "t"), ("mem", "p"),
    ("peng", "k"), ("pen", "t"), ("pem", "p"), ("ber", ""), ("ter", ""),
    ("per", ""), ("ke", ""), ("se", ""), ("di", ""), ("pe", ""), ("me", ""),
)
_MIN_STEM = 3


def _kandidat_dasar(kata: str) -> List[str]:
    """Bentuk dasar yang mungkin untuk `kata` (B4: urut afiks tersedikit).

    Didelegasikan ke stemmer bersama di `pycos.bahasa.teks` agar
    "pemarah"→"marah" (bukan "parah") dan "mengajar"→"ajar".
    """
    return _kandidat_dasar_teks(kata)


def stem_kata(kata: str, kosakata: Optional[set] = None) -> str:
    """Stem satu kata dengan validasi opsional ke `kosakata` (B4)."""
    return _stem_teks(kata, kosakata)


LEKSIKON_CIRI_BAWAAN = LeksikonCiri(
    positif=_fs(
        "senang", "suka", "bagus", "hangat", "indah", "syukur", "bersyukur",
        "makasih", "terimakasih", "cinta", "aman", "tenang", "baik", "hebat",
        "gembira", "lega", "damai", "ceria", "manis", "sayang", "nyaman",
        "berhasil", "mantap", "keren", "asyik", "bahagia", "riang", "lucu",
        "cantik", "pintar", "menarik", "ramah", "tulus", "berani", "percaya",
        "harapan", "beruntung", "puas", "bangga", "menghibur", "setuju", "enak",
        "lezat", "semangat", "optimis", "istimewa", "menakjubkan",
        "menyenangkan", "menggembirakan", "membahagiakan", "memuaskan",
        "mulia", "bantu", "membantu", "bantuan",
    ),
    negatif=_fs(
        "takut", "sedih", "marah", "benci", "sakit", "cemas", "bahaya", "buruk",
        "kecewa", "sendiri", "hancur", "lelah", "khawatir", "gelap", "dingin",
        "sepi", "galau", "murung", "gagal", "sengsara", "jelek", "payah", "parah",
        "kesal", "bosan", "muak", "letih", "capek", "pusing", "malas", "bodoh",
        "tolol", "menderita", "menyesal", "malu", "panik", "trauma", "rusak",
        "kacau", "tragis", "musibah", "bencana", "kehilangan", "mati", "meninggal",
        "tewas", "sia-sia", "mengecewakan", "menyebalkan",
        "menyedihkan", "menakutkan", "menyakitkan", "sialan", "brengsek",
        "jahat", "kejam",
    ),
    pelunak=_fs(
        "mungkin", "kayaknya", "sepertinya", "barangkali", "tampaknya", "agaknya",
        "rasanya", "kurang", "kemungkinan", "sekiranya", "kiranya", "konon",
        "entah", "seingatku", "kelihatannya",
    ),
    penguat=_fs(
        "sangat", "banget", "bgt", "sekali", "amat", "sungguh", "benar-benar",
        "paling", "terlalu", "nian", "betul-betul", "super", "sumpah",
    ),
    formal=_fs(
        "saya", "anda", "bapak", "ibu", "mohon", "silakan", "silahkan", "tuan",
        "nyonya", "sudi", "berkenan", "hormat", "saudara", "beliau", "yth",
    ),
    informal=_fs(
        "aku", "kau", "kamu", "gue", "gua", "lo", "lu", "nih", "sih", "dong",
        "kok", "deh", "loh", "lho", "kak", "bro", "sis",
    ),
    negasi=_fs(
        "tidak", "tak", "bukan", "belum", "jangan", "tiada", "enggak", "nggak",
        "gak", "ga", "tidaklah", "bukanlah",
    ),
)


@dataclass(frozen=True)
class FiturTutur:
    token: int
    seru: int
    tanya: int
    positif: int
    negatif: int
    dinegasi: int
    pelunak: int
    penguat: int
    formal: int
    informal: int
    proporsi_kapital: float

    def polaritas(self) -> Optional[float]:
        sentimen = self.positif + self.negatif
        if sentimen == 0:
            return None
        return (self.positif - self.negatif) / sentimen

    def formalitas(self) -> Optional[float]:
        register = self.formal + self.informal
        if register == 0:
            return None
        return (self.formal - self.informal) / register

    def intensitas(self) -> Optional[float]:
        if self.token == 0:
            return None
        mentah = (0.3 * min(self.seru, 3) + 0.25 * min(self.penguat, 3)
                  + 0.5 * self.proporsi_kapital)
        return min(1.0, mentah)

    def keraguan(self) -> Optional[float]:
        if self.token == 0:
            return None
        return min(1.0, 4.0 * self.pelunak / self.token)


def _tokenkan(teks: str) -> List[str]:
    """Token ternormalisasi; tanda baca pemisah klausa menjadi `_BATAS_KLAUSA`.

    Memakai tokenizer bersama (A1–A2): "senaaang"→"senang", "gk"→"tidak",
    klitik dibuang, reduplikasi angka diurai.
    """
    keluar: List[str] = []
    for t in _tokenisasi_teks(teks):
        if t.jenis == "kata":
            keluar.append(t.bentuk)
        elif t.jenis == "tanda_baca" and t.asli in ",.!?;:":
            keluar.append(_BATAS_KLAUSA)
    return keluar


def _kata_saja(token: List[str]) -> List[str]:
    return [t for t in token if t != _BATAS_KLAUSA]


def _sentimen(token: List[str], leksikon: LeksikonCiri) -> Tuple[int, int, int]:
    """Hitung (positif, negatif, dinegasi) dengan cakupan negasi bersama (D2).

    Cakupan sampai batas klausa (bukan jendela tetap), negasi ganda
    membatalkan, "jangan" tidak membalik, "kurang"/"mana mungkin"
    melemahkan (tidak dihitung), idiom multi-kata dihitung utuh.
    """
    from pycos.bahasa import teks as _teks_mod
    from pycos.bahasa.teks import IDIOM_SENTIMEN as _IDIOM
    pos = neg = dinegasi = 0
    # idiom: tandai token yang sudah dikonsumsi idiom
    gabung = " ".join(t for t in token if t != _BATAS_KLAUSA)
    dikonsumsi: set = set()
    for frasa, polar in _IDIOM.items():
        if frasa in gabung:
            # tandai semua token yang membentuk frasa (cocok berurutan)
            ftoks = frasa.split()
            for i in range(len(token) - len(ftoks) + 1):
                if token[i:i + len(ftoks)] == ftoks:
                    for j in range(i, i + len(ftoks)):
                        dikonsumsi.add(j)
                    if polar == "positif":
                        pos += 1
                    elif polar == "negatif":
                        neg += 1
                    break
    # cakupan negasi: sumber tunggal di teks.cakupan_negasi (D2); "|" adalah
    # batas klausa.
    tks = [_teks_mod.Token(t, t, (0, len(t)),
                           "tanda_baca" if t == _BATAS_KLAUSA else "kata")
           for t in token]
    neg_flags = _cakupan_negasi(tks)
    # prohibitif ("jangan X"): X tidak dihitung sebagai sentimen pernyataan —
    # inklusi larangan bukan pernyataan keadaan ("jangan sedih" ≠ positif/negatif).
    larang: List[bool] = [False] * len(token)
    for i, w in enumerate(token):
        if w == "jangan":
            jml = 0
            for k in range(i + 1, len(token)):
                if token[k] == _BATAS_KLAUSA:
                    break
                jml += 1
                if jml > 4:
                    break
                larang[k] = True
    for i, w in enumerate(token):
        if w == _BATAS_KLAUSA or i in dikonsumsi or larang[i]:
            continue
        # pelemahan: "kurang" di dekat sebelum sentimen → jangan dihitung
        lemah = False
        for j in range(max(0, i - 2), i):
            if token[j] == _BATAS_KLAUSA:
                break
            if token[j] == "kurang":
                lemah = True
                break
        if lemah:
            continue
        # retorika: "mana mungkin" sebelum sentimen → jangan dihitung
        if i >= 2 and token[i - 2:i] == ["mana", "mungkin"]:
            continue
        kategori = None
        if w == "kasih" and i > 0 and token[i - 1] == "terima":
            kategori = "positif"
        elif leksikon.kanonik(w, "positif") is not None:
            kategori = "positif"
        elif leksikon.kanonik(w, "negatif") is not None:
            kategori = "negatif"
        if kategori is None:
            continue
        dibalik = neg_flags[i]
        positif = (kategori == "positif") != dibalik
        if dibalik:
            dinegasi += 1
        if positif:
            pos += 1
        else:
            neg += 1
    return pos, neg, dinegasi


def _hitung(kata: List[str], leksikon: LeksikonCiri, kategori: str) -> int:
    return sum(1 for w in kata if leksikon.kanonik(w, kategori) is not None)


def analisis_teks(teks: str, leksikon: Optional[LeksikonCiri] = None) -> FiturTutur:
    """Hitung ciri linguistik `teks`. Melempar TypeError bila bukan string."""
    if not isinstance(teks, str):
        raise TypeError("teks harus string, dapat {}".format(type(teks).__name__))
    lex = LEKSIKON_CIRI_BAWAAN if leksikon is None else leksikon
    token = _tokenkan(teks)
    kata = _kata_saja(token)
    huruf = [c for c in teks if c.isalpha()]
    kapital = sum(1 for c in huruf if c.isupper())
    pos, neg, dinegasi = _sentimen(token, lex)
    return FiturTutur(
        token=len(kata),
        seru=teks.count("!"),
        tanya=teks.count("?"),
        positif=pos,
        negatif=neg,
        dinegasi=dinegasi,
        pelunak=_hitung(kata, lex, "pelunak"),
        penguat=_hitung(kata, lex, "penguat"),
        formal=sum(1 for w in kata if w in lex.formal),
        informal=sum(1 for w in kata if w in lex.informal),
        proporsi_kapital=(kapital / len(huruf)) if huruf else 0.0,
    )


_TOKEN_MENTAH = re.compile(r"[^\W\d_]+(?:-[^\W\d_]+)*")


def token_dari(teks: str) -> List[str]:
    """Kata asli (huruf kecil, tanpa normalisasi) untuk pencocokan pantangan.

    Sengaja TIDAK men-strip klitik: "bodohnya" bukan "bodoh" sebagai token.
    """
    return [m.group(0).lower() for m in _TOKEN_MENTAH.finditer(str(teks or ""))]


__all__ = ["TuturEngine", "Leksikon", "Lattice", "GenContext", "Node", "Arg",
           "Tutur", "Orkestrator", "L0", "L1", "L2", "L3",
           "SASPAnalyzer", "sa_sp", "sa_sp_literal", "sa_sp_pragmatik",
           "konteks_dari_presentasi",
           "FiturTutur", "LeksikonCiri", "LEKSIKON_CIRI_BAWAAN",
           "JENDELA_NEGASI", "analisis_teks", "token_dari"]
