# -*- coding: utf-8 -*-
"""pycos/bahasa/teks.py — fondasi teks bersama untuk sistem linguistik Pycos.

Modul ini menggantikan 9+ tokenizer dan 8 stoplist yang tersebar dengan satu
lapisan bersama (A1–A6), plus cakupan negasi (D2), jenis kalimat (D3),
pengurai dangkal subjek–predikat (D4), tindak tutur berskor (D5), jenis
pertanyaan (D6), ekstraksi entitas/topik (D7), deteksi bahasa (D12),
pemeriksa kegramatikalan (G1), pemotongan batas kata (H3), dan jejak
INPUT → FILTER → FORMATION → OUTPUT (E0).

Murni standard library (`re`, `unicodedata`, `difflib`, `collections`,
`dataclasses`). Tidak mengimpor modul Pycos lain, sehingga dapat dipakai
dari lapisan mana pun tanpa lingkaran impor. Leksikon (bila diperlukan)
diterima sebagai parameter duck-typed (objek dengan `ambil`/`kelas_dari`).
"""
from __future__ import annotations

import difflib
import re
import unicodedata
from collections import Counter
from functools import lru_cache
from dataclasses import dataclass, field
from typing import Any, Dict, List, Mapping, Optional, Sequence, Set, Tuple

__all__ = [
    "Token", "tokenisasi", "normalisasi_token", "normalisasi_teks",
    "pecah_kalimat", "stem", "kandidat_dasar", "cakupan_negasi",
    "jenis_kalimat", "jenis_pertanyaan", "urai_subjek_predikat",
    "tindak_tutur_skor", "ekstrak_entitas", "ekstrak_topik",
    "deteksi_bahasa", "kemiripan", "koreksi_ejaan", "periksa_gramatika",
    "potong_batas_kata", "analisis_ujaran", "JejakLinguistik",
    "jejak_pembentukan", "STOPWORDS", "NEGATOR_LOGIS",
    "NEGATOR_PROHIBITIF", "PENGURANG", "ABSORBER_NEGASI",
    "TRANSPARAN_NEGASI", "PENGUAT", "PELUNAK",
    "KATA_TANYA", "PENANDA_IMPERATIF", "PRONOMINA", "PREPOSISI",
    "IDIOM_SENTIMEN", "SINGKATAN",
]

# ===========================================================================
# kosakata bersama (A3)
# ===========================================================================
STOPWORDS: Set[str] = frozenset({
    "di", "ke", "dari", "itu", "ini", "yang", "dan", "atau", "sangat",
    "sangatlah", "amat", "sekali", "terlalu", "lah", "kah", "pun",
    "adalah", "sedang", "telah", "akan", "sudah", "belum", "para",
    "sebuah", "seorang", "seekor", "adalah", "merupakan", "yakni",
})

# Negator logis: membalik polaritas sentimen dalam cakupannya (D2).
NEGATOR_LOGIS: Set[str] = frozenset({
    "tidak", "tak", "bukan", "belum", "tiada", "tanpa",
    "nggak", "enggak", "gak", "ga", "gk", "tdk", "ngga",
})

# Prohibitifs: tidak membalik sentimen (imperatif larangan, bukan negasi logis).
NEGATOR_PROHIBITIF: Set[str] = frozenset({"jangan"})

# Pengurang: melemahkan, tidak membalik ("kurang suka" bukan positif).
PENGURANG: Set[str] = frozenset({"kurang", "agak", "sedikit", "sepi", "jarang"})

# Kata transparan: tidak membuka/menutup cakupan, tidak pula ter-flag
# ("tidak aman DAN juga tidak gagal" — kedua sisi tetap ternegasi).
TRANSPARAN_NEGASI: Set[str] = frozenset({
    "dan", "juga", "serta", "atau", "maupun", "adalah", "itu", "ini",
    "yang", "sangat", "sangatlah", "sekali", "amat", "banget",
    "dengan", "sama", "begitu",
})

# Penyerap negasi (modal/kuantifier): bila muncul SETELAH negator, cakupan
# negasi berhenti di kata ini (negator hanya menyangkal kata itu sendiri).
# "tidak mungkin aku melupakan hari bahagia itu" → "bahagia" tidak dibalik;
# "tidak sedikit orang yang kecewa" → "kecewa" tidak dibalik.
ABSORBER_NEGASI: Set[str] = frozenset({
    "mungkin", "pasti", "sedikit", "banyak", "terlalu", "terlampau",
    "sanggup", "mampu",
})

PENGUAT: Set[str] = frozenset({
    "sangat", "banget", "bgt", "sekali", "amat", "sungguh", "benar-benar",
    "paling", "terlalu", "nian", "betul-betul", "super", "sumpah",
    "bangettt", "sangattt",
})

PELUNAK: Set[str] = frozenset({
    "mungkin", "kayaknya", "sepertinya", "barangkali", "tampaknya",
    "agaknya", "rasanya", "kemungkinan", "sekiranya", "kiranya",
    "konon", "entah", "seingatku", "kelihatannya",
})

KATA_TANYA: Set[str] = frozenset({
    "apa", "siapa", "kapan", "dimana", "kenapa", "mengapa", "bagaimana",
    "berapa", "apakah", "bisakah", "maukah", "bolehkah", "adakah",
    "mungkinkah", "gimana", "bagaimanakah", "siapakah", "apakah",
})

PENANDA_IMPERATIF: Set[str] = frozenset({
    "tolong", "mohon", "silakan", "silahkan", "ayo", "mari", "yuk",
    "jangan", "coba", "tolonglah",
})

PRONOMINA: Set[str] = frozenset({
    "aku", "saya", "kamu", "kau", "dia", "ia", "kita", "kami",
    "mereka", "anda", "beliau", "gue", "gua", "lo", "lu",
})

PREPOSISI: Set[str] = frozenset({
    "di", "ke", "dari", "pada", "dengan", "untuk", "tentang",
    "kepada", "dalam", "seperti", "karena", "sebagai", "tanpa",
    "oleh", "antara", "selama", "sejak", "sampai", "hingga",
    "melalui", "menurut", "terhadap", "beserta", "bersama",
})

# Batas klausa untuk cakupan negasi (D2): negasi berhenti di sini.
BATAS_KLAUSA_KATA: Set[str] = frozenset({
    "tapi", "namun", "tetapi", "karena", "sebab", "kenapa", "mengapa",
    "bahwa", "kalau", "jika", "supaya", "agar", "meskipun", "walaupun",
    "padahal", "tahu", "mengerti", "paham",
})

# Singkatan informal → bentuk baku (A2).
SINGKATAN: Dict[str, str] = {
    "gk": "tidak", "tdk": "tidak", "nggak": "tidak", "enggak": "tidak",
    "gak": "tidak", "ga": "tidak", "ngga": "tidak",
    "yg": "yang", "dgn": "dengan", "bgt": "banget", "udh": "sudah",
    "blm": "belum", "gmn": "bagaimana", "knp": "kenapa", "gmn": "bagaimana",
    "d": "di", "k": "ke", "g": "tidak",
}

# Idiom multi-kata dengan makna utuh (C8). Nilai: "positif"/"negatif"/"netral".
IDIOM_SENTIMEN: Dict[str, str] = {
    "tak sabar": "negatif",
    "tidak sabar": "negatif",
    "tidak apa-apa": "netral",
    "tidak apa apa": "netral",
    "baik-baik saja": "positif",
    "putus asa": "negatif",
    "makan hati": "negatif",
    "angkat tangan": "netral",
    "terima kasih": "positif",
    "tidak tahu": "netral",
    "mana mungkin": "netral",
}

# Kata fungsi untuk deteksi bahasa (D12).
FUNGSI_ID: Set[str] = frozenset({
    "yang", "di", "ke", "dari", "dan", "atau", "tidak", "aku", "kamu",
    "kau", "saya", "ini", "itu", "dengan", "untuk", "pada", "adalah",
    "sedang", "telah", "akan", "sudah", "belum", "jangan", "bukan",
    "bagaimana", "kenapa", "kapan", "dimana", "siapa", "apa",
})
FUNGSI_EN: Set[str] = frozenset({
    "the", "is", "are", "was", "were", "and", "or", "not", "i", "you",
    "he", "she", "it", "this", "that", "with", "for", "to", "of", "in",
    "on", "at", "a", "an", "do", "does", "did", "can", "could", "will",
    "would", "what", "who", "when", "where", "why", "how",
})

# Verba imperatif umum (cadangan bila leksikon tidak tersedia).
VERBA_IMPERATIF_UMUM: Set[str] = frozenset({
    "pergi", "ambil", "ambilkan", "buka", "tutup", "makan", "minum",
    "lihat", "dengar", "duduk", "berdiri", "jalan", "lari", "tidur",
    "bangun", "masuk", "keluar", "tunggu", "cari", "beri", "berikan",
    "ambilkan", "tolong", "bantu", "dengarkan", "perhatikan", "jangan",
    "berhenti", "lanjut", "mulai", "selesai", "coba", "ingat", "lupa",
    "ingatlah", "pergilah", "duduklah", "berdirilah",
})

# Adjektiva emosi (untuk pemeriksaan adjektiva_bahwa).
EMOSI_ADJ: Set[str] = frozenset({
    "senang", "sedih", "takut", "marah", "malu", "benci", "cinta",
    "kesepian", "tenang", "harap", "terkejut", "jijik", "bangga",
    "cemburu", "syukur", "haru", "kecewa", "lega", "ceria", "gembira",
    "bahagia", "murung", "galau", "kesal", "bosan", "muak", "letih",
    "capek", "pusing", "panik", "trauma", "menyesal", "bersyukur",
    "pesimis", "optimis",
})

# Sapaan (D7).
SAPAAN: Set[str] = frozenset({
    "pak", "bu", "kak", "dik", "mbak", "mas", "bang", "dek", "neng",
    "bapak", "ibu", "tuan", "nyonya", "saudara", "bro", "sis",
})

# ===========================================================================
# A1 — tokenizer bersama
# ===========================================================================
@dataclass(frozen=True)
class Token:
    """Satu token dengan posisi, jenis, bentuk asli dan ternormalisasi."""
    asli: str
    bentuk: str
    posisi: Tuple[int, int]
    jenis: str  # kata | angka | tanda_baca | emotikon

    def __repr__(self) -> str:  # ringkas untuk debug
        return "Token({!r}->{!r},{})".format(self.asli, self.bentuk, self.jenis)


_TOKEN_RE = re.compile(
    r"(?P<emotikon>[:;8][\-~]?[\)\(\[\]{}DPp/\\]|<3|</3)"
    r"|(?P<kata>[^\W\d_]+(?:-[^\W\d_]+)*)"
    r"|(?P<angka>\d+(?:[.,]\d+)?)"
    r"|(?P<tanda>[.,!?;:…—–\-\"'()\[\]{}«»“”‘’])",
    flags=re.UNICODE,
)

_KLITIK = ("nya", "lah", "kah", "pun", "ku", "mu")
_MIN_STEM = 3


def _strip_klitik(kata: str) -> str:
    """Buang satu klitik/partikel bila sisa >= 3 huruf."""
    for k in _KLITIK:
        if kata.endswith(k) and len(kata) - len(k) >= _MIN_STEM:
            # "hanya" -> "ha" ditolak karena sisa < 3; "aku" -> "a" ditolak.
            return kata[: -len(k)]
    return kata


def normalisasi_token(kata: str) -> str:
    """Normalisasi satu kata: huruf kecil, huruf berulang, singkatan, klitik.

    * "senaaang" -> "senang" (3+ huruf berulang dilipat ke satu).
    * "gk"/"tdk" -> "tidak"; "yg" -> "yang"; "baik2" -> "baik-baik".
    * "bukannya" -> "bukan"; "senangnya" -> "senang"; "apakah" -> "apa".
    """
    s = unicodedata.normalize("NFC", str(kata or "")).strip().lower()
    if not s:
        return ""
    # reduplikasi angka: "baik2" -> "baik-baik"
    m = re.match(r"^(.+?)2$", s)
    if m and len(m.group(1)) >= 2 and "-" not in m.group(1):
        base = m.group(1)
        return "{}-{}".format(base, base)
    # huruf berulang 3+ -> 1
    s = re.sub(r"(.)\1{2,}", r"\1", s)
    # singkatan (hanya bila satu token penuh)
    if s in SINGKATAN:
        return SINGKATAN[s]
    # klitik/partikel (satu lapis; stem menangani lapis lanjutan)
    if "-" not in s:
        s = _strip_klitik(s)
    else:
        # hyphenated: normalisasi tiap bagian
        parts = s.split("-")
        s = "-".join(_strip_klitik(p) if p else p for p in parts)
    return s


def normalisasi_teks(teks: str) -> str:
    """Normalisasi seluruh teks (untuk pencocokan frasa/idiom)."""
    return " ".join(normalisasi_token(t.asli) for t in tokenisasi(teks)
                    if t.jenis == "kata")


def tokenisasi(teks: str) -> List[Token]:
    """Tokenisasi bersama (A1): posisi, jenis, bentuk asli & ternormalisasi."""
    s = unicodedata.normalize("NFC", str(teks or ""))
    out: List[Token] = []
    for m in _TOKEN_RE.finditer(s):
        asli = m.group(0)
        if m.group("emotikon"):
            out.append(Token(asli, asli, (m.start(), m.end()), "emotikon"))
        elif m.group("kata"):
            out.append(Token(asli, normalisasi_token(asli),
                             (m.start(), m.end()), "kata"))
        elif m.group("angka"):
            out.append(Token(asli, asli, (m.start(), m.end()), "angka"))
        else:
            out.append(Token(asli, asli, (m.start(), m.end()), "tanda_baca"))
    return out


def pecah_kalimat(teks: str) -> List[str]:
    """Pecah kalimat (A4): singkatan, elipsis, kutip, ?/! beruntun."""
    s = str(teks or "").strip()
    if not s:
        return []
    # lindungi singkatan umum agar tidak dipecah
    s = re.sub(r"\b(dr|mr|mrs|ms|prof|no|dll|dst|etc)\.",
               lambda m: m.group(0).replace(".", "<titik>"), s, flags=re.I)
    # pecah setelah . ! ? … (termasuk beruntun ?? !! ?!)
    parts = re.split(r"(?<=[.!?…])\s+(?=[A-ZÀ-Þ\"'“‘(])", s)
    out: List[str] = []
    for p in parts:
        p = p.strip().replace("<titik>", ".")
        if p:
            out.append(p)
    return out or [s]


# ===========================================================================
# B4 — stemmer Nazief–Adriani yang disederhanakan (validasi ke kosakata)
# ===========================================================================
# (prefiks, restorasi) — restorasi adalah huruf yang dikembalikan bila luluh.
_PREFIKS: Tuple[Tuple[str, str], ...] = (
    ("memper", ""), ("diper", ""), ("keber", ""),
    ("menge", ""), ("meny", "s"), ("peny", "s"), ("meny", "ny"), ("peny", "ny"),
    ("mensy", "sy"), ("peny", "sy"),
    ("mengkh", "kh"), ("pengkh", "kh"),
    ("meng", "k"), ("men", "t"), ("mem", "p"),
    ("peng", "k"), ("pen", "t"), ("pem", "p"),
    ("bel", ""),
    ("ber", ""), ("ter", ""), ("per", ""),
    ("ke", ""), ("se", ""), ("di", ""), ("pe", ""), ("me", ""),
)
_SUFIKS: Tuple[str, ...] = ("kan", "an", "i")
# Klaster awal yang legal di lema Indonesia (selain konsonan tunggal
# dan vokal). Dipakai memvalidasi restorasi alofon nasal.
_KLASTER_LEGAL = frozenset(
    ("pr", "br", "dr", "tr", "kr", "gr", "pl", "bl", "kl", "gl", "fl", "fr",
     "sw", "sp", "st", "sy", "kh", "ng", "ny"))


def kandidat_dasar(kata: str) -> List[str]:
    """Kandidat dasar terurut: sedikit afiks, sedikit karakter dibuang,
    tanpa restorasi dulu — agar "pemarah"→"marah" bukan "parah",
    "mengajar"→"ajar" bukan "kajar"."""
    w = unicodedata.normalize("NFC", str(kata or "")).strip().lower()
    w = re.sub(r"(.)\1{2,}", r"\1", w)
    if not w:
        return []
    # reduplikasi: "marah-marah" -> "marah"; "bolak-balik" -> tetap utuh dulu
    if "-" in w:
        parts = w.split("-")
        if len(parts) == 2 and parts[0] == parts[1]:
            base = parts[0]
            return list(dict.fromkeys([w, base] + kandidat_dasar(base)))
        # berimbuhan "menakut-nakuti": urai bagian pertama
        if len(parts) == 2 and parts[0] and parts[1]:
            base = parts[0]
            return list(dict.fromkeys([w, base] + kandidat_dasar(base)))
        return [w]
    # BFS: (bentuk, n_afiks, n_char_dibuang, n_restorasi)
    awal: List[Tuple[str, int, int, int]] = [(w, 0, 0, 0)]
    semua: List[Tuple[str, int, int, int]] = list(awal)
    # partikel & klitik
    for lapis in (_KLITIK,):
        baru: List[Tuple[str, int, int, int]] = []
        for bentuk, na, nc, nr in list(semua):
            for k in lapis:
                if bentuk.endswith(k) and len(bentuk) - len(k) >= _MIN_STEM:
                    baru.append((bentuk[: -len(k)], na + 1, nc + len(k), nr))
        semua.extend(baru)
    # sufiks (lapis 1)
    baru = []
    for bentuk, na, nc, nr in list(semua):
        for suf in _SUFIKS:
            if bentuk.endswith(suf) and len(bentuk) - len(suf) >= _MIN_STEM:
                baru.append((bentuk[: -len(suf)], na + 1, nc + len(suf), nr))
    semua.extend(baru)
    # prefiks; alofon nasal mengikuti fonotaktik alofon: ekstraksi polos
    # hanya diizinkan bila sisa diawali fonem yang ditoleransi alofon itu
    # ("mengajar" → meng+ajar, bukan men+gajar; "membaca" → mem+baca,
    # bukan me+mbaca). Restorasi (t/p/k/s/ny) hanya berlaku ke bentuk yang
    # dipulihkan. Kasus restorasi penuh ("penyanyi"→"nyanyi") diselesaikan
    # lewat validasi `kosakata` bila disediakan.
    _ALOFON_POLOS: Dict[str, Optional[str]] = {
        "me": "lmrwnyh", "pe": "lmrwnyh",
        "men": "aeioudjc", "pen": "aeioudjc",
        "mem": "aeioubf", "pem": "aeioubf",
        "meng": "aeiougkh", "peng": "aeiougkh",
        "meny": None, "peny": None,
        "mensy": "u", "peny": None,
        "mengkh": "a", "pengkh": "a",
    }
    baru = []
    for bentuk, na, nc, nr in list(semua):
        for awal_p, restor in _PREFIKS:
            if not bentuk.startswith(awal_p):
                continue
            sisa = bentuk[len(awal_p):]
            if len(sisa) < _MIN_STEM:
                continue
            alofon = _ALOFON_POLOS.get(awal_p, "")
            if alofon is None:
                # alofon nasal tanpa bentuk polos valid
                if not restor:
                    continue
            elif alofon and sisa[0] not in alofon:
                pass  # kandidat polos ditolak; restorasi (bila ada) tetap dicoba
            elif (awal_p in ("me", "pe") and sisa[0] in "mn"
                  and len(sisa) > 1 and sisa[1] not in "aeiou"):
                # klaster nasal+konsonan tak legal di awal lema ("mbaca",
                # "ngambil", "nyanyi") — alofon menempel via asimilasi
                pass
            else:
                baru.append((sisa, na + 1, nc + len(awal_p), nr))
            if restor:
                pulih = restor + sisa
                klaster = pulih[:2]
                if len(klaster) == 2 and klaster[0] not in "aeiou" \
                        and klaster[1] not in "aeiou" \
                        and klaster not in _KLASTER_LEGAL:
                    continue  # klaster awal tak legal ("tgajar", "pbaca")
                baru.append((pulih, na + 1, nc + len(awal_p), nr + 1))
    semua.extend(baru)
    # sufiks (lapis 2, mis. "diberdayakan" -> "berdaya")
    baru = []
    for bentuk, na, nc, nr in list(semua):
        for suf in _SUFIKS:
            if bentuk.endswith(suf) and len(bentuk) - len(suf) >= _MIN_STEM:
                baru.append((bentuk[: -len(suf)], na + 1, nc + len(suf), nr))
    semua.extend(baru)
    # urut: n_afiks, char dibuang, restorasi, terpanjang dulu
    semua.sort(key=lambda t: (t[1], t[2], t[3], -len(t[0])))
    hasil: List[str] = []
    for bentuk, *_ in semua:
        if bentuk and bentuk not in hasil:
            hasil.append(bentuk)
    # bentuk asli selalu pertama
    if w in hasil:
        hasil.remove(w)
    return [w] + hasil


@lru_cache(maxsize=1)
def kosakata_bawaan() -> frozenset:
    """Himpunan lema bahasa Indonesia dari sumber daya (lazy, sekali baca).

    Dipakai untuk memvalidasi kandidat stem (B4) sehingga "menghalangi"
    berhenti di "halangi", "mengetahui" di "tahu", "mensyukuri" di
    "syukur" — bukan berhenti di separuh afiks.
    """
    try:
        import json
        from pycos.dukungan.sumber import ada_sumber_daya, jalur_leksikon
        if not ada_sumber_daya():
            return frozenset()
        with open(jalur_leksikon(), encoding="utf-8") as f:
            dok = json.load(f)
        return frozenset(str(e.get("lema", "")).lower()
                         for e in dok.get("leksikon", [])
                         if e.get("bahasa") == "id" and e.get("lema"))
    except Exception:
        return frozenset()


def stem(kata: str, kosakata: Optional[Set[str]] = None) -> str:
    """Stem satu kata; validasi ke `kosakata` atau leksikon bawaan (B4)."""
    cands = kandidat_dasar(kata)
    if not cands:
        return str(kata or "").lower()
    if kosakata is None:
        kosakata = kosakata_bawaan()
    if kosakata:
        for c in cands[1:]:
            if c in kosakata:
                return c
    # tanpa yang cocok di leksikon: kandidat terpendek-afiks setelah bentuk asli
    for c in cands[1:]:
        if c != cands[0]:
            return c
    return cands[0]


# ===========================================================================
# D2 — cakupan negasi bersama
# ===========================================================================
def cakupan_negasi(tokens: Sequence[Token]) -> List[bool]:
    """True bila token berada dalam cakupan negasi logis.

    Cakupan berhenti di batas klausa (tanda baca, tapi/namun/karena,
    penanda klausa anak, "tahu" setelah negator) atau di kata penyerap
    (modal/kuantifier: "tidak mungkin … bahagia" → "bahagia" tidak
    dibalik). Negasi yang berdampingan menumpuk (paritas): "bukannya
    tidak senang" tidak dibalik; sebaliknya cakupan negasi yang didahului
    kata isi dibuka ulang segar ("tidak aman dan tidak gagal" → keduanya
    dibalik). "jangan" (prohibitif) tidak membuka cakupan. Kata transparan
    (dan/itu/yang/sangat/…) tidak men-flag maupun menutup cakupan.
    """
    out: List[bool] = [False] * len(tokens)
    neg = 0
    aktif = False
    last_negasi = False  # token kata yang relevan terakhir adalah negator
    for i, t in enumerate(tokens):
        if t.jenis == "tanda_baca":
            neg, aktif, last_negasi = 0, False, False
            continue
        if t.jenis != "kata":
            continue
        b = t.bentuk
        if b in BATAS_KLAUSA_KATA:
            neg, aktif, last_negasi = 0, False, False
            continue
        if b in ABSORBER_NEGASI and aktif:
            neg, aktif, last_negasi = 0, False, False
            continue
        if b in TRANSPARAN_NEGASI:
            # transparan: tidak mengubah status cakupan, tidak ter-flag
            continue
        if b in NEGATOR_LOGIS:
            # idiom "tidak apa-apa": jangan aktifkan cakupan
            nxt = tokens[i + 1].bentuk if i + 1 < len(tokens) else ""
            if nxt in ("apa", "apa-apa"):
                continue
            if last_negasi:
                neg += 1          # negasi menumpuk di sebelah negasi
            else:
                neg = 1           # cakupan dibuka segar
            aktif = True
            last_negasi = True
            continue
        if b in NEGATOR_PROHIBITIF:
            # larangan bukan negasi logis; tidak memakai paritas
            continue
        if aktif and (neg % 2 == 1):
            out[i] = True
        last_negasi = False
    return out


# ===========================================================================
# D3 — jenis kalimat; D6 — jenis pertanyaan
# ===========================================================================
def _kata_tokens(tokens: Sequence[Token]) -> List[Token]:
    return [t for t in tokens if t.jenis == "kata"]


def _kelas_dari(leksikon: Any, kata: str) -> List[str]:
    if leksikon is None:
        return []
    try:
        fn = getattr(leksikon, "kelas_dari", None)
        if callable(fn):
            return list(fn(kata) or [])
    except Exception:
        pass
    try:
        ent = leksikon.ambil("id", kata)  # type: ignore[attr-defined]
        if ent:
            return list(ent.get("kelas", []) or [])
    except Exception:
        pass
    return []


def _adalah_verba(leksikon: Any, kata: str) -> bool:
    if _kelas_dari(leksikon, kata):
        return "V" in _kelas_dari(leksikon, kata)
    return kata in VERBA_IMPERATIF_UMUM


def jenis_kalimat(teks: str, tokens: Optional[Sequence[Token]] = None,
                  leksikon: Any = None) -> str:
    """imperatif | interogatif | eksklamatif | deklaratif (D3).

    Tidak bergantung hanya pada tanda baca akhir: penanda imperatif,
    kata tanya, -kah, "kan?"/"ya?" ikut menentukan.
    """
    raw = str(teks or "").strip()
    toks = list(tokens) if tokens is not None else tokenisasi(raw)
    kata = [t.bentuk for t in _kata_tokens(toks)]
    if not kata:
        return "deklaratif"
    first = kata[0]
    low = raw.lower()
    ends_q = raw.rstrip().endswith("?")
    ends_excl = raw.rstrip().endswith("!")
    # 1) penanda imperatif kuat di awal
    if first in PENANDA_IMPERATIF:
        return "imperatif"
    # 2) interogatif: tanda tanya, kata tanya, -kah, kan?/ya?
    if ends_q:
        return "interogatif"
    if first in KATA_TANYA:
        return "interogatif"
    if any(t.bentuk.endswith("kah") for t in _kata_tokens(toks)):
        return "interogatif"
    if low.rstrip().endswith(("kan?", "ya?", "toh?", "sih?")):
        return "interogatif"
    if "apakah" in kata:
        return "interogatif"
    # 3) imperatif verba-di-awal (butuh leksikon atau daftar umum)
    if len(kata) >= 2 and first not in PRONOMINA and first not in KATA_TANYA:
        if _adalah_verba(leksikon, first):
            return "imperatif"
        # tanpa leksikon: verba umum + objek/keterangan
        if first in VERBA_IMPERATIF_UMUM:
            return "imperatif"
    if len(kata) == 1 and _adalah_verba(leksikon, first):
        return "imperatif"
    # 4) eksklamatif
    if ends_excl:
        return "eksklamatif"
    return "deklaratif"


def jenis_pertanyaan(teks: str, tokens: Optional[Sequence[Token]] = None) -> Dict[str, Any]:
    """Jenis pertanyaan + fokus jawaban (D6). Kosong bila bukan tanya."""
    toks = list(tokens) if tokens is not None else tokenisasi(teks)
    kata = [t.bentuk for t in _kata_tokens(toks)]
    if not kata:
        return {}
    raw = str(teks or "").strip()
    if not (raw.rstrip().endswith("?") or kata[0] in KATA_TANYA
            or any(k.endswith("kah") for k in kata)):
        return {}
    s = set(kata)
    if "siapa" in s:
        return {"jenis": "siapa", "fokus": "orang"}
    if "dimana" in s or ("di" in s and "mana" in s):
        return {"jenis": "dimana", "fokus": "tempat"}
    if "kapan" in s:
        return {"jenis": "kapan", "fokus": "waktu"}
    if "kenapa" in s or "mengapa" in s:
        return {"jenis": "kenapa", "fokus": "sebab"}
    if "bagaimana" in s or "gimana" in s:
        return {"jenis": "bagaimana", "fokus": "cara"}
    if "berapa" in s:
        return {"jenis": "berapa", "fokus": "jumlah"}
    if "apa" in s:
        return {"jenis": "apa", "fokus": "benda/keadaan"}
    if "atau" in s:
        return {"jenis": "pilihan", "fokus": "salah satu"}
    return {"jenis": "ya_tidak", "fokus": "benar/salah"}


# ===========================================================================
# D4 — pengurai dangkal subjek–predikat–objek–keterangan
# ===========================================================================
def urai_subjek_predikat(tokens: Sequence[Token],
                         leksikon: Any = None) -> Dict[str, Any]:
    """Uraian dangkal berbasis kelas kata (D4); pasif `di-` ditangani."""
    kata_toks = _kata_tokens(tokens)
    bentuk = [t.bentuk for t in kata_toks]
    if not bentuk:
        return {"subjek": None, "predikat": None, "objek": None,
                "keterangan": None}
    # predikat: verba pertama, lalu adjektiva, lalu kata isi terakhir
    idx_pred: Optional[int] = None
    for i, b in enumerate(bentuk):
        if "V" in _kelas_dari(leksikon, b):
            idx_pred = i
            break
    if idx_pred is None:
        for i, b in enumerate(bentuk):
            if "ADJ" in _kelas_dari(leksikon, b):
                idx_pred = i
                break
    if idx_pred is None:
        # kata isi terakhir (bukan stopword/pronomina/preposisi)
        for i in range(len(bentuk) - 1, -1, -1):
            b = bentuk[i]
            if b not in STOPWORDS and b not in PRONOMINA and b not in PREPOSISI:
                idx_pred = i
                break
    if idx_pred is None:
        idx_pred = len(bentuk) - 1
    predikat = bentuk[idx_pred]
    # subjek: pronomina/nomina sebelum predikat
    subjek: Optional[str] = None
    sebelum = bentuk[:idx_pred]
    for b in sebelum:
        if b in PRONOMINA:
            subjek = b
            break
    if subjek is None:
        # nomina sebelum predikat (bukan penanda imperatif/preposisi)
        for b in sebelum:
            if b not in PENANDA_IMPERATIF and b not in PREPOSISI and b not in STOPWORDS:
                subjek = b
                break
    if subjek is None and sebelum:
        # imperatif tanpa subjek eksplisit → subjek implisit "kamu"
        if bentuk[0] in PENANDA_IMPERATIF or _adalah_verba(leksikon, bentuk[0]):
            subjek = "kamu"
    # objek: nomina setelah predikat sebelum preposisi
    objek: Optional[str] = None
    sesudah = bentuk[idx_pred + 1:]
    for b in sesudah:
        if b in PREPOSISI:
            break
        if b in PRONOMINA or b in STOPWORDS:
            continue
        if "N" in _kelas_dari(leksikon, b) or leksikon is None:
            objek = b
            break
    # keterangan: frasa preposisional setelah predikat
    keterangan: Optional[str] = None
    for i, b in enumerate(sesudah):
        if b in PREPOSISI and i + 1 < len(sesudah):
            keterangan = "{} {}".format(b, sesudah[i + 1])
            break
    return {"subjek": subjek, "predikat": predikat, "objek": objek,
            "keterangan": keterangan}


# ===========================================================================
# D5 — tindak tutur berskor; D7 — entitas; D12 — bahasa
# ===========================================================================
def tindak_tutur_skor(teks: str, tokens: Optional[Sequence[Token]] = None,
                      semantik: Optional[Mapping[str, Any]] = None) -> Dict[str, float]:
    """Skor tiap tindak tutur (D5); bukan satu label tunggal."""
    toks = list(tokens) if tokens is not None else tokenisasi(teks)
    kata = [t.bentuk for t in _kata_tokens(toks)]
    # Cocokkan lintas bentuk (D5): klitik/afiks dibuang lewat stem, sehingga
    # "memukulmu"/"menghina" tetap terbaca sebagai leksemnya.
    lema = [stem(k) for k in kata]
    s = set(kata) | set(lema)
    low = " ".join(kata)
    sem = dict(semantik or {})
    jenis = sem.get("jenis_kalimat") or jenis_kalimat(teks, toks)
    skor: Dict[str, float] = {k: 0.0 for k in (
        "salam", "pamit", "terima_kasih", "maaf", "pujian", "hinaan",
        "tuduhan", "ancaman", "peringatan", "permintaan", "perintah",
        "tawaran", "janji", "keluhan", "ajakan", "persetujuan",
        "penolakan", "pertanyaan", "asertif")}
    if not kata:
        return skor
    if kata[0] in ("halo", "hai", "hei", "selamat", "assalamualaikum",
                   "pagi", "siang", "sore", "malam") or low.startswith(
                       ("selamat pagi", "selamat siang", "selamat malam",
                        "assalamualaikum")):
        skor["salam"] = 0.9
    if any(w in s for w in ("dadah", "permisi")) or "sampai jumpa" in low \
            or "selamat tinggal" in low:
        skor["pamit"] = 0.9
    if "terima kasih" in low or "makasih" in s or "terimakasih" in s:
        skor["terima_kasih"] = 0.9
    if any(w in s for w in ("maaf", "menyesal", "ampun")):
        skor["maaf"] = 0.85
    _PUJIAN = ("hebat", "bagus", "keren", "pintar", "mantap", "jenius",
               "cerdas", "brilian", "menakjubkan", "terbaik", "memukau")
    _HINAAN = ("bodoh", "tolol", "brengsek", "sialan", "payah", "kecut",
               "pengecut", "goblok", "dungu", "bajingan", "sampah",
               "pengkhianat", "kampungan", "pecundang", "lancang")
    _TUDUHAN = {"curang", "bohong", "pembohong", "penipu", "khianat",
                "mencuri", "licik", "culas", "tipu", "curi", "nipu"}
    if any(w in s for w in _PUJIAN) and (s & PRONOMINA):
        skor["pujian"] = 0.7
    if any(w in s for w in _HINAAN) and (s & PRONOMINA):
        skor["hinaan"] = 0.8
    if jenis == "interogatif" and (s & PRONOMINA) and (
            s & NEGATOR_LOGIS or "kenapa" in s):
        skor["tuduhan"] = 0.5
    if jenis == "deklaratif" and (s & _TUDUHAN) and (s & PRONOMINA):
        skor["tuduhan"] = max(skor["tuduhan"], 0.6)
    _ANCAMAN = {"bunuh", "hancur", "hajar", "bakar", "musnah", "sikat",
                "habisi", "lumat"}
    if "awas" in s or ("akan" in s and s & _ANCAMAN):
        skor["ancaman"] = 0.8
    if any(w in s for w in ("hati-hati", "waspada", "awas")) or (
            jenis == "imperatif" and s & {"bahaya", "ancaman", "risiko"}):
        skor["peringatan"] = 0.8
    if jenis == "imperatif":
        if s & {"tolong", "mohon", "silakan", "silahkan"}:
            skor["permintaan"] = 0.85
        else:
            skor["perintah"] = 0.8
    if jenis == "interogatif":
        skor["pertanyaan"] = 0.9
        if s & {"bisa", "boleh", "mau", "sudi"} and s & {"tolong", "bantu"}:
            skor["permintaan"] = max(skor["permintaan"], 0.8)
        if "mau" in s or "bagaimana kalau" in low or "gimana kalau" in low:
            skor["tawaran"] = max(skor["tawaran"], 0.7)
    if kata[0] in ("ayo", "mari", "yuk"):
        skor["ajakan"] = 0.9
    if "aku janji" in low or ("akan" in s and "aku" in s
                              and s & {"bantu", "datang", "bayar"}):
        skor["janji"] = 0.8
    if s & {"setuju", "sepakat", "oke"}:
        skor["persetujuan"] = 0.7
    if len(kata) <= 3 and (s & NEGATOR_LOGIS or "jangan" in s):
        skor["penolakan"] = 0.7
    if "tak mau" in low or "tidak mau" in low:
        skor["penolakan"] = max(skor["penolakan"], 0.8)
    # keluhan keadaan (D9): deklaratif + keadaan negatif
    if jenis == "deklaratif" and s & {"panas", "dingin", "lapar", "capek",
                                      "lelah", "gerah", "terik", "haus",
                                      "sakit", "pusing"}:
        skor["keluhan"] = 0.6
    if jenis == "deklaratif" and not any(v > 0.6 for v in skor.values()):
        skor["asertif"] = 0.6
    return skor


def ekstrak_entitas(teks: str, tokens: Optional[Sequence[Token]] = None,
                    leksikon: Any = None) -> List[Dict[str, str]]:
    """Entitas: nama diri, sapaan, kata ganti, rujukan diri pendengar (D7)."""
    toks = list(tokens) if tokens is not None else tokenisasi(teks)
    kata_toks = _kata_tokens(toks)
    out: List[Dict[str, str]] = []
    for i, t in enumerate(kata_toks):
        b = t.bentuk
        if b in SAPAAN:
            out.append({"teks": t.asli, "jenis": "sapaan"})
        elif b in PRONOMINA:
            jenis = "rujukan_diri" if b in ("aku", "saya", "kita", "kami") \
                else "kata_ganti"
            out.append({"teks": t.asli, "jenis": jenis})
        elif t.asli[:1].isupper() and len(t.asli) >= 3:
            # nama diri: kapital bukan di awal, atau di awal + verba/pronomina
            if i > 0:
                out.append({"teks": t.asli, "jenis": "nama_diri"})
            elif i == 0 and len(kata_toks) > 1:
                nxt = kata_toks[1].bentuk
                if nxt in PRONOMINA or _adalah_verba(leksikon, nxt) \
                        or nxt in ("adalah", "sedang", "telah", "akan"):
                    out.append({"teks": t.asli, "jenis": "nama_diri"})
    # dedup, pertahankan urutan
    seen: Set[Tuple[str, str]] = set()
    uniq: List[Dict[str, str]] = []
    for e in out:
        k = (e["teks"].lower(), e["jenis"])
        if k not in seen:
            seen.add(k)
            uniq.append(e)
    return uniq


def ekstrak_topik(teks: str, tokens: Optional[Sequence[Token]] = None,
                  leksikon: Any = None) -> str:
    """Frasa nomina topik (bukan kalimat mentah) untuk E3.

    Mengembalikan nomina pertama yang bermakna, atau "" bila tidak ada —
    pemanggil tidak boleh menempelkan kalimat utuh sebagai topik.
    """
    toks = list(tokens) if tokens is not None else tokenisasi(teks)
    kata = [t.bentuk for t in _kata_tokens(toks)]
    if not kata:
        return ""
    # nomina via leksikon
    for b in kata:
        if b in PRONOMINA or b in STOPWORDS or b in PREPOSISI \
                or b in KATA_TANYA or b in PENANDA_IMPERATIF:
            continue
        if b in NEGATOR_LOGIS or b in PENGUAT or b in PELUNAK:
            continue
        if "N" in _kelas_dari(leksikon, b):
            return b
    # tanpa leksikon: kata isi yang bukan verba/adjektiva umum
    for b in kata:
        if b in PRONOMINA or b in STOPWORDS or b in PREPOSISI \
                or b in KATA_TANYA or b in PENANDA_IMPERATIF:
            continue
        if b in NEGATOR_LOGIS or b in PENGUAT or b in PELUNAK:
            continue
        if b in VERBA_IMPERATIF_UMUM or b in EMOSI_ADJ:
            continue
        # akhiran verba/adjektiva umum dilewati
        if b.endswith(("kan", "an", "i")) and len(b) > 4:
            continue
        return b
    return ""


def deteksi_bahasa(teks: str) -> str:
    """id | en | campuran | tak_dikenal (D12)."""
    toks = tokenisasi(teks)
    kata = [t.bentuk for t in _kata_tokens(toks)]
    if not kata:
        return "tak_dikenal"
    id_n = sum(1 for k in kata if k in FUNGSI_ID)
    en_n = sum(1 for k in kata if k in FUNGSI_EN)
    if id_n > 0 and en_n == 0:
        return "id"
    if en_n > 0 and id_n == 0:
        return "en"
    if id_n > 0 and en_n > 0:
        return "campuran"
    return "tak_dikenal"


# ===========================================================================
# A5 — kemiripan; A6 — koreksi ejaan
# ===========================================================================
def _ngram(s: str, n: int = 3) -> Set[str]:
    s = " " + s + " "
    return {s[i:i + n] for i in range(len(s) - n + 1)} if len(s) >= n else {s}


def kemiripan(a: str, b: str) -> float:
    """Kemiripan teks bersama (A5): Jaccard lema + n-gram + difflib."""
    ta = [stem(t.bentuk) for t in _kata_tokens(tokenisasi(a))
          if t.bentuk not in STOPWORDS]
    tb = [stem(t.bentuk) for t in _kata_tokens(tokenisasi(b))
          if t.bentuk not in STOPWORDS]
    sa, sb = set(ta), set(tb)
    jac = (len(sa & sb) / float(len(sa | sb))) if (sa or sb) else 0.0
    na, nb = _ngram(normalisasi_teks(a)), _ngram(normalisasi_teks(b))
    jac_ng = (len(na & nb) / float(len(na | nb))) if (na or nb) else 0.0
    dif = difflib.SequenceMatcher(None, normalisasi_teks(a),
                                  normalisasi_teks(b)).ratio()
    return (jac + jac_ng + dif) / 3.0


def koreksi_ejaan(kata: str, kosakata: Sequence[str]) -> Optional[str]:
    """Koreksi ringan untuk kata tak dikenal (A6); None bila tidak ada."""
    w = normalisasi_token(kata)
    if not w or w in set(kosakata):
        return None
    cocok = difflib.get_close_matches(w, list(kosakata), n=1, cutoff=0.85)
    return cocok[0] if cocok else None


# ===========================================================================
# G1 — pemeriksa kegramatikalan keluaran
# ===========================================================================
def periksa_gramatika(teks: str, leksikon: Any = None) -> List[str]:
    """Daftar kode masalah gramatika (G1); kosong berarti lolos.

    Kode: tanda_baca_ganda, kata_berulang, preposisi_ganda,
    adjektiva_bahwa, verba_transitif_tanpa_objek, afiks_tak_valid,
    kalimat_tanpa_predikat.
    """
    s = str(teks or "").strip()
    if not s:
        return ["kalimat_tanpa_predikat"]
    masalah: List[str] = []
    # tanda baca ganda ("?.", "??", ".." — elipsis "..." dikecualikan)
    if re.search(r"[?!][.!?]|[.!?][?!]|\.\.(?!\.)", s):
        masalah.append("tanda_baca_ganda")
    toks = tokenisasi(s)
    kata = [t.bentuk for t in _kata_tokens(toks)]
    if not kata:
        return masalah + ["kalimat_tanpa_predikat"]
    # kata berulang berdampingan
    for i in range(1, len(kata)):
        if kata[i] == kata[i - 1]:
            masalah.append("kata_berulang")
            break
    # preposisi ganda
    for i in range(1, len(kata)):
        if kata[i] in PREPOSISI and kata[i - 1] in PREPOSISI:
            masalah.append("preposisi_ganda")
            break
    # adjektiva + bahwa
    for i, b in enumerate(kata):
        if b == "bahwa" and i > 0 and kata[i - 1] in EMOSI_ADJ:
            masalah.append("adjektiva_bahwa")
            break
    # verba -kan/-i transitif di akhir tanpa objek
    if kata:
        last = kata[-1]
        if (last.endswith("kan") or last.endswith("i")) and len(last) > 4:
            # verba berimbuhan di akhir kalimat tanpa nomina sesudahnya
            if "V" in _kelas_dari(leksikon, last) or last.startswith(
                    ("me", "mem", "men", "meng", "meny", "di", "pe")):
                masalah.append("verba_transitif_tanpa_objek")
    # afiks tak valid: "ii"/"uu" akhir, "yy", prefiks Indonesia + Inggris
    for b in kata:
        if re.search(r"(ii|uu)$", b) or "yy" in b:
            masalah.append("afiks_tak_valid")
            break
        if re.match(r"^(ber|me|pe|di|ke|se|ter|per)(fire|lonely|happy|sad|"
                    r"love|hate|good|bad)$", b):
            masalah.append("afiks_tak_valid")
            break
    # kalimat tanpa predikat (fragmen nomina tunggal)
    ada_pred = False
    for b in kata:
        kelas = _kelas_dari(leksikon, b)
        if "V" in kelas or "ADJ" in kelas:
            ada_pred = True
            break
        if b in VERBA_IMPERATIF_UMUM or b in EMOSI_ADJ:
            ada_pred = True
            break
    if not ada_pred and leksikon is not None:
        # hanya tegas bila leksikon tersedia (tanpa leksikon, fragmen lolos)
        masalah.append("kalimat_tanpa_predikat")
    elif not ada_pred and len(kata) == 1 and kata[0] not in (
            "sebentar", "tunggu", "hm", "eh", "anu"):
        # fragmen satu kata tanpa predikat (mis. "Api.")
        masalah.append("kalimat_tanpa_predikat")
    return list(dict.fromkeys(masalah))


# ===========================================================================
# H3 — pemotongan batas kata
# ===========================================================================
def potong_batas_kata(teks: str, maks_karakter: int) -> str:
    """Potong di batas kata (bukan tengah kata); tanpa sufiks."""
    s = str(teks or "")
    if len(s) <= maks_karakter:
        return s
    potong = s[:maks_karakter]
    spasi = potong.rfind(" ")
    if spasi > 0:
        potong = potong[:spasi]
    return potong.rstrip(" .,;:—-")


# ===========================================================================
# E0 — jejak INPUT → FILTER → FORMATION → OUTPUT
# ===========================================================================
@dataclass
class JejakLinguistik:
    """Jejak diagnostik kontribusi faktor pada satu ujaran (E0)."""
    input_teks: str = ""
    filter_keadaan: Dict[str, Any] = field(default_factory=dict)
    formation_faktor: Dict[str, Any] = field(default_factory=dict)
    output_teks: str = ""
    act: str = ""
    alasan_act: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {"input": self.input_teks, "filter": dict(self.filter_keadaan),
                "formation": dict(self.formation_faktor),
                "output": self.output_teks, "act": self.act,
                "alasan_act": self.alasan_act}


def jejak_pembentukan(input_teks: str = "", keadaan: Optional[Mapping[str, Any]] = None,
                      pengetahuan: Optional[Mapping[str, Any]] = None,
                      situasi: Optional[Mapping[str, Any]] = None,
                      sosial: Optional[Mapping[str, Any]] = None,
                      bahasa_kognisi: Optional[Mapping[str, Any]] = None,
                      biologis: Optional[Mapping[str, Any]] = None,
                      medium: Optional[Mapping[str, Any]] = None,
                      percakapan: Optional[Mapping[str, Any]] = None,
                      output_teks: str = "", act: str = "",
                      alasan_act: str = "") -> Dict[str, Any]:
    """Bangun jejak E0 dari delapan kelompok faktor FORMATION."""
    formation = {
        "keadaan_internal": dict(keadaan or {}),
        "pengetahuan": dict(pengetahuan or {}),
        "situasi_lingkungan": dict(situasi or {}),
        "sosial_audiens": dict(sosial or {}),
        "bahasa_kognisi": dict(bahasa_kognisi or {}),
        "biologis_fisiologis": dict(biologis or {}),
        "medium_saluran": dict(medium or {}),
        "konteks_percakapan": dict(percakapan or {}),
    }
    return JejakLinguistik(input_teks=input_teks,
                           filter_keadaan=dict(keadaan or {}),
                           formation_faktor=formation,
                           output_teks=output_teks, act=act,
                           alasan_act=alasan_act).to_dict()


# ===========================================================================
# Gabungan untuk CLI/diagnostik (J9)
# ===========================================================================
def analisis_ujaran(teks: str, leksikon: Any = None) -> Dict[str, Any]:
    """Analisis lengkap satu ujaran: token, lema, jenis, tindak, entitas."""
    toks = tokenisasi(teks)
    kata = [t.bentuk for t in _kata_tokens(toks)]
    lema = [stem(k) for k in kata]
    jenis = jenis_kalimat(teks, toks, leksikon)
    tanya = jenis_pertanyaan(teks, toks) if jenis == "interogatif" else {}
    proposisi = urai_subjek_predikat(toks, leksikon)
    sem = {"jenis_kalimat": jenis}
    skor = tindak_tutur_skor(teks, toks, sem)
    tindak = max(skor, key=lambda k: skor[k]) if skor else "asertif"
    return {
        "teks": str(teks or ""),
        "token": kata,
        "lema": lema,
        "jenis_kalimat": jenis,
        "jenis_pertanyaan": tanya,
        "proposisi": proposisi,
        "tindak_tutur": tindak,
        "skor_tindak": {k: round(v, 3) for k, v in skor.items() if v > 0},
        "entitas": ekstrak_entitas(teks, toks, leksikon),
        "topik": ekstrak_topik(teks, toks, leksikon),
        "bahasa": deteksi_bahasa(teks),
        "negasi": cakupan_negasi(toks),
        "gramatika": periksa_gramatika(teks, leksikon),
    }
