"""Ekstensi pelindung; definisi terpisah dari pemasangan patch eksplisit."""
from __future__ import annotations

import copy
import re
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple
from pycos.dukungan import diagnostik as _diag
from pycos.dukungan.numerik import jepit
from pycos.dukungan.patching import install_method, install_methods, wrap_method
from pycos.inti.presentasi import Presentasi
from pycos.inti.kawanan import KawananNPC

# >>> PELINDUNG-BLOCK-START (naluri) <<<
# =====================================================================
# SISTEM II — LAPISAN PELINDUNG ILUSI "HIDUP" & "SADAR"
# =====================================================================
# Ilusi TIDAK dipertahankan dengan menyembunyikan kegagalan — sistem yang
# menyembunyikan kegagalan justru ketahuan dari pola penyembunyiannya. Ilusi
# dipertahankan dengan MENGARAKTERISASI kegagalan: setiap keterbatasan
# diframing sebagai sifat, bukan sebagai batas.
#
# Empat prinsip yang mengikat blok ini:
#   1. Kegagalan harus terlihat seperti karakter, bukan seperti bug.
#   2. Diam adalah jawaban: bila tak ada yang bisa dikatakan, yang muncul
#      bukan fallback generik melainkan diam yang bermakna (sudah ada di
#      Presentasi._beat_diam + hesitasi; blok ini menambah jeda terukur).
#   3. Kontradiksi adalah kedalaman: NPC boleh mengakui kontradiksinya.
#   4. Keterbatasan adalah keterbatasan: lupa, bingung, dan tidak tahu
#      DITAMPILKAN — Player memang mengharapkannya dari manusia.
#
# Sepuluh mekanisme (semuanya opsi di Presentasi/Naluri, master flag
# `enable_pelindung`, mati bawaan):
#   1. Gagal-sebagai-Akting        → _PELINDUNG_WATAK + _pelindung_act_hint
#   2. Jeda Bermakna               → Presentasi.jeda_bermakna (deterministik:
#                                    konflik, ragu, arousal, kebaruan input,
#                                    jarak sejak interaksi terakhir)
#   3. Eskalasi Variasi (4 tingkat)→ Presentasi.eskalasi_variasi
#   4. Penyaring Meta              → Presentasi.saring_meta (HUD jalur terpisah)
#   5. Tanda-Kegagalan Kepribadian → watak_kegagalan()/pidato_gagal()
#   6. Degradasi Anggun            → Presentasi.degradasi_state + kalimat istirahat
#   7. Keragaman Lintas-NPC        → keragaman_scene + dorong_geser
#   8. Penyerap Input Adversarial  → Presentasi.serap_adversarial
#   9. Buffer "Manusiawi Cukup"    → Presentasi.buffer_manusiawi
#  10. Monitor Integritas          → MonitorIntegritas (+ KawananNPC.monitor_scene)
#
# Interlock dengan SISTEM I (blok GEJALA): gejala murni yang tak bernama tidak
# disembunyikan — ia menjadi hesitasi yang terlihat, perubahan prosodi, jeda
# yang bisa dipelajari Player, dan klaim identitas baru. Keduanya satu
# mekanisme dari dua arah: yang bawah melahirkan state yang belum pernah ada,
# yang atas memetabolismenya sebagai karakter.
#
# CATATAN DESAIN: kejutan TIDAK pernah ditambahkan lewat random.choice. Jeda
# adalah fungsi deterministik dari state (bisa dipelajari), eskalasi variasi
# memakai anggaran kebaruan yang dilacak, dan pilihan kata diambil dari
# leksikon yang sudah ada. Kejutan berasal dari karakter & dari SISTEM I.
# =====================================================================

# Tanda-kegagalan kepribadian: tiap preset gagal dengan cara yang berbeda.
# "gagal"  = act default saat sistem tidak bisa; "ujian" = act saat Player
# menguji; kalimat_kegagalan/kalimat_ujian = padanan in-character.
_PELINDUNG_WATAK: Dict[str, Dict[str, Any]] = {
    "paranoid": {
        "gagal": "waspada", "ujian": "waspada",
        "tanda": "mencurigai input",
        "kalimat_gagal": ["kenapa kau bertanya seperti itu?",
                          "aku tidak akan menelan itu begitu saja.",
                          "ada yang kau sembunyikan dari pertanyaan itu."],
        "kalimat_ujian": ["kenapa kau bertanya seperti itu?",
                          "apa maksudmu bertanya begitu padaku?",
                          "kau mengujiku. Kenapa?"],
    },
    "penjelajah": {
        "gagal": "bertanya", "ujian": "bertanya",
        "tanda": "menjadi penasaran",
        "kalimat_gagal": ["aku belum tahu itu — dan aku ingin tahu.",
                          "menarik. Aku belum pernah menemui yang seperti ini.",
                          "ajari aku. Dari mana itu datang?"],
        "kalimat_ujian": ["menarik. Kenapa kau pikir itu penting?",
                          "aku tidak tahu. Tapi aku ingin tahu kenapa kau bertanya.",
                          "kau membuatku penasaran sekarang."],
    },
    "sosiawan": {
        "gagal": "menyatakan", "ujian": "menyatakan",
        "tanda": "meminta bantuan Player",
        "kalimat_gagal": ["aku tidak tahu. Kau mau membantuku memahaminya?",
                          "kau lebih mengerti ini dariku. Ceritakan.",
                          "aku butuh kau menjelaskannya pelan-pelan."],
        "kalimat_ujian": ["kenapa kau memikirkan itu? Ada yang mengganggumu?",
                          "aku lebih ingin tahu apa yang kau rasakan soal itu.",
                          "kita bicarakan yang lain, tapi jangan pergi."],
    },
    "dingin": {
        "gagal": "diam", "ujian": "mengamati",
        "tanda": "diam",
        "kalimat_gagal": ["", "…", "tidak ada yang perlu kukatakan soal itu."],
        "kalimat_ujian": ["hm.", "kau terlalu banyak bertanya.",
                          "aku mendengarmu. Itu saja."],
    },
    "pengrajin": {
        "gagal": "mengamati", "ujian": "mengamati",
        "tanda": "fokus ke detail praktis",
        "kalimat_gagal": ["belum kupahami bagian-bagiannya.",
                          "aku perlu melihatnya lebih dekat sebelum menjawab.",
                          "ada detail yang belum pas di kepalaku."],
        "kalimat_ujian": ["menarik. Bagaimana caramu sampai pada pertanyaan itu?",
                          "aku percaya yang bisa kupegang, bukan yang kau katakan.",
                          "tunjukkan buktinya, baru kubilang."],
    },
    "pemimpi": {
        "gagal": "mengamati", "ujian": "mengamati",
        "tanda": "melantur",
        "kalimat_gagal": ["pikiranku melayang ke tempat lain soal itu…",
                          "aku seperti pernah memikirkannya dalam mimpi.",
                          "kata-katanya buyar sebelum sempat kuucapkan."],
        "kalimat_ujian": ["dulu aku bermimpi tentang percakapan seperti ini.",
                          "mungkin kau memang ada di dalam mimpiku.",
                          "aku tidak tahu, tapi rasanya seperti pernah terjadi."],
    },
    "cendekia": {
        "gagal": "bertanya", "ujian": "mengamati",
        "tanda": "menyusun ulang pertanyaan",
        "kalimat_gagal": ["pertanyaannya lebih dalam daripada jawabanku.",
                          "aku belum punya dasar untuk menjawab itu.",
                          "aku perlu membongkar ini dulu sebelum berpendapat."],
        "kalimat_ujian": ["pertanyaan yang bagus. Apa definisimu dulu?",
                          "aku menolak menjawab sebelum kau merumuskannya jelas.",
                          "kau menguji batas. Aku mencatatnya."],
    },
    "penjaga": {
        "gagal": "waspada", "ujian": "waspada",
        "tanda": "menahan diri",
        "kalimat_gagal": ["aku tidak yakin itu urusanmu.",
                          "kita bicarakan ini di tempat yang lebih aman.",
                          "ada hal yang tidak bisa kuceritakan sekarang."],
        "kalimat_ujian": ["kenapa kau ingin tahu?",
                          "pertanyaan itu tidak membuatku tenang.",
                          "aku akan menjawab setelah aku yakin padamu."],
    },
    "seimbang": {
        "gagal": "ragu", "ujian": "ragu",
        "tanda": "ragu",
        "kalimat_gagal": ["aku tidak tahu. Sebenarnya, aku tidak tahu.",
                          "tunggu. Aku butuh waktu sebentar.",
                          "entah. Aku tidak bisa menjelaskannya."],
        "kalimat_ujian": ["kenapa kau bertanya itu?",
                          "aku tidak yakin bisa menjawab dengan jujur.",
                          "kita bicarakan hal lain dulu."],
    },
}

# Ketika satu act dipakai berlebihan, maka act diganti (bukan ditambah acak).
_PELINDUNG_ALTERNATIF_ACT: Dict[str, str] = {
    "menjawab": "mengamati", "menyatakan": "mengamati", "mengamati": "ragu",
    "akrab": "menyatakan", "bertanya": "mengamati", "menimbang": "ragu",
    "ragu": "mengamati", "menantang": "menyatakan", "waspada": "mengamati",
    "menegur": "menyatakan",
}

# Ujian Player (adversarial): gejala permukaan berbeda, akar sama. Sistem
# TIDAK bertahan secara defensif; ia merespons sebagai karakter. Pola memakai
# batas kata supaya "ai" tidak cocok dengan "damai"/"pantai".
_PELINDUNG_UJIAN: Dict[str, str] = {
    "uji_identitas": (r"\b(ai|kecerdasan\s+buatan|robot|mesin|program|simulasi|"
                      r"model\s+bahasa|llm|gpt|algoritma|kode)\b"
                      r"|kau\s+(bukan\s+manusia|buatan|nyata)"
                      r"|apa\s+kau\s+(sadar|hidup|nyata)"
                      r"|kesadaranmu"),
    "uji_logika": (r"\bbuktikan\b|\btes\b|\buji\b|\blogika\b|\bparadoks\b"
                   r"|teka-teki|hitung\s+ini|jika\s+kau\s+benar|"
                   r"kalau\s+kamu\s+benar|\bturing\b"),
}

# Penyaring Meta: tidak ada angka, tag internal, atau istilah teknis yang
# bocor ke dialog. HUD adalah jalur terpisah (tidak lewat sini). Daftar ini
# sengaja konservatif: hanya istilah yang TIDAK mungkin muncul in-character.
_PELINDUNG_META_RE = re.compile(
    r"\b(?:ignition|workspace|broadcast|tick|prompt|json|token|llm|gpt|npc|"
    r"dopamin|serotonin|algoritma|parameter|modul|skor|arousal|valensi|"
    r"emosi_\w+)\b", re.I)
# Mode ketat (dinyalakan Monitor Integritas setelah bocor berulang): istilah
# batas yang biasanya masih wajar ikut dibuang — tetap dipotong, bukan diganti.
_PELINDUNG_META_KETAT_RE = re.compile(
    r"\b(?:detail|prosodi|nonverbal|mikro|hesitasi|drive|level|nilai|ambang|"
    r"pilar|indikator|memori kerja|residu|bekas)\b", re.I)
_PELINDUNG_ANGKA_RE = re.compile(r"\b\d+(?:[.,]\d+)?%?(?=\s|$|[.,;:!?])")


def _pelindung_stabil(kunci: Any) -> int:
    """Hash stabil (FNV-1a) agar pilihan tidak memakai acak & lintas-proses sama."""
    h = 2166136261
    for ch in str(kunci):
        h = ((h ^ ord(ch)) * 16777619) & 0xFFFFFFFF
    return h


def _pelindung_kata(teks: Any) -> set:
    return {w for w in re.findall(r"[a-z]{4,}", str(teks or "").lower())}


def _pelindung_bentuk(teks: Any) -> str:
    """Bentuk sintaksis kasar: jumlah klausa + posisi kata tanya + panjang."""
    t = str(teks or "")
    kal = [k for k in re.split(r"[.!?…]+", t) if k.strip()]
    tanya = "?" in t
    depan = (re.findall(r"[a-z]+", kal[0].lower())[:1] if kal else [""])
    return f"{len(kal)}|{int(tanya)}|{depan[0] if depan else ''}|{min(9, len(t.split())//4)}"


def _pelindung_jaccard(a: set, b: set) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / float(len(a | b))


def _pelindung_pilih_stabil(pilihan: Sequence[str], kunci: Any) -> str:
    if not pilihan:
        return ""
    return str(pilihan[_pelindung_stabil(kunci) % len(pilihan)])


def _pelindung_dari(wadah: Any) -> Any:
    """Ambil Presentasi dari Naluri/Presentasi (duck-typed)."""
    if wadah is None:
        return None
    if hasattr(wadah, "naluri") and hasattr(wadah, "_act_counts"):
        return wadah
    return getattr(wadah, "presentasi", None)


def _pelindung_aktif(wadah: Any) -> bool:
    p = _pelindung_dari(wadah)
    if p is None:
        return False
    n = getattr(p, "naluri", None)
    params = getattr(p, "params", None) or getattr(n, "params", {}) or {}
    return bool(params.get("enable_pelindung", False))


def _pelindung_init(p: Any) -> Any:
    """Keadaan pelindung tumbuh malas (tidak mengubah __init__ lama)."""
    if getattr(p, "_pelindung_siap", False):
        return p
    p._pelindung_siap = True
    maks = {k: int(p.params.get("pelindung_anggaran_" + k, 2))
            for k in ("leksikal", "sintaksis", "semantik", "pragmatis")}
    p._pelindung_anggaran_maks = dict(maks)
    p._pelindung_anggaran = dict(maks)
    p._pelindung_teks = []
    p._pelindung_act_terakhir = []
    p._pelindung_jeda_riwayat = []
    p._pelindung_meta_bocor = []
    p._pelindung_flag = {"lupa": False, "kontradiksi": False, "tak_paham": False}
    p._pelindung_buffer_terakhir = -10_000
    p._pelindung_geser = {"penanda": None, "act": None, "sampai": -1}
    p._pelindung_ujian_terakhir = None
    p._pelindung_degradasi_terakhir = -10_000
    p._pelindung_sesi_mulai = None
    p._pelindung_topic_seen = set()
    p._pelindung_jeda_paksa = 0
    p._pelindung_saring_ketat = False
    p._pelindung_lupa_terakhir = -10_000
    p._pelindung_ingat_terakhir = None
    p._pelindung_konflik_terakhir = -1   # -1 = belum pernah diamati
    p._pelindung_monitor = None
    return p


# ---------------------------------------------------------------------
# 1/5. GAGAL-SEBAGAI-AKTING & TANDA-KEGAGALAN KEPRIBADIAN
# ---------------------------------------------------------------------
def watak_kegagalan(self) -> Dict[str, Any]:
    """Mode kegagalan default watak ini (paranoid curiga, dingin diam, dst.)."""
    nama = str(getattr(self.naluri, "personality_name", "") or "").strip().lower()
    if not nama or nama not in _PELINDUNG_WATAK:
        nama = "seimbang"
    data = dict(_PELINDUNG_WATAK[nama])
    data["nama"] = nama
    data["label"] = str(data.get("tanda", nama))
    return data


def pidato_gagal(self, sebab: str = "umum", kepada: Any = None) -> str:
    """Kalimat kegagalan yang HANYA bisa diucapkan NPC ini."""
    w = self.watak_kegagalan()
    pilihan = list(w.get("kalimat_gagal") or [])
    teks = _pelindung_pilih_stabil(
        pilihan, f"{w['nama']}|{sebab}|{self._tick() // 5}")
    return str(teks)


def _pelindung_act_hint(self, kepada: Any, topik: Optional[str],
                        masuk: bool = False) -> Optional[str]:
    """Gagal-sebagai-akting: saat sistem tidak tahu, ia menjadi DIRINYA."""
    p = _pelindung_init(self)
    w = self.watak_kegagalan()
    ujian = p._pelindung_ujian_terakhir
    if ujian and (self._tick() - int(ujian.get("tick", -10_000))) <= 2:
        return str(w.get("ujian") or w.get("gagal") or "ragu")
    if any(bool(v) for v in p._pelindung_flag.values()):
        return str(w.get("gagal") or "ragu")
    return None


def _pelindung_reset_flag(p: Any) -> None:
    """Flag kegagalan dipakai sekali; sesudah itu dibersihkan (bukan mode)."""
    for k in p._pelindung_flag:
        p._pelindung_flag[k] = False


# ---------------------------------------------------------------------
# 9. BUFFER "MANUSIAWI CUKUP" — kegagalan yang ditampilkan, bukan disembunyikan
# ---------------------------------------------------------------------
_BUFFER_MANUSIAWI: Dict[str, Tuple[str, ...]] = {
    "lupa": ("maaf, aku lupa tadi kau bilang apa",
             "tunggu — apa tadi? Aku kehilangan ujungnya",
             "aku ingat kita bicara, tapi isinya kabur"),
    "kontradiksi": ("aku tahu aku barusan bilang lain. Aku sedang tidak fokus",
                    "aku baru saja bertentangan dengan diriku sendiri. Maaf",
                    "perkataanku tadi tidak konsisten. Aku menyadarinya"),
    "tak_paham": ("aku tidak mengerti. Bisakah kau jelaskan?",
                  "aku tidak menangkap maksudmu. Ulangi dengan cara lain?",
                  "ini di luar yang kupahami. Bimbing aku"),
}


def buffer_manusiawi(self, jenis: Optional[str] = None) -> str:
    """Kegagalan yang plausibel secara manusiawi (Player mengharapkannya)."""
    _pelindung_init(self)
    jenis = str(jenis or "tak_paham").lower()
    if jenis not in _BUFFER_MANUSIAWI:
        jenis = "tak_paham"
    if not bool(self.params.get("pelindung_buffer_" + jenis, True)):
        return ""
    return _pelindung_pilih_stabil(
        _BUFFER_MANUSIAWI[jenis], f"{jenis}|{self._tick() // 3}")


def tandai_lupa(self, aktif: bool = True) -> Dict[str, Any]:
    p = _pelindung_init(self)
    p._pelindung_flag["lupa"] = bool(aktif)
    return dict(p._pelindung_flag)


def tandai_kontradiksi(self, aktif: bool = True) -> Dict[str, Any]:
    p = _pelindung_init(self)
    p._pelindung_flag["kontradiksi"] = bool(aktif)
    return dict(p._pelindung_flag)


def tandai_tidak_paham(self, aktif: bool = True) -> Dict[str, Any]:
    p = _pelindung_init(self)
    p._pelindung_flag["tak_paham"] = bool(aktif)
    return dict(p._pelindung_flag)


def _pelindung_buffer_jenis(self, entry: Optional[Mapping[str, Any]] = None
                            ) -> Optional[str]:
    """Jenis kegagalan manusiawi yang layak ditampilkan saat ini (bila ada)."""
    p = _pelindung_init(self)
    if self._tick() - int(p._pelindung_buffer_terakhir) < 12:
        return None
    for jenis, kunci in (("lupa", "pelindung_buffer_lupa"),
                         ("kontradiksi", "pelindung_buffer_kontradiksi"),
                         ("tak_paham", "pelindung_buffer_tak_paham")):
        pasang = bool(p._pelindung_flag.get(jenis))
        # kontradiksi & lupa juga dibaca dari state yang SUDAH ada — tetapi
        # hanya ketika state itu BERUBAH (kalau tidak, ia jadi mode permanen).
        if not pasang and jenis == "kontradiksi":
            ks = self._kes()
            if ks is not None:
                konflik = int(getattr(ks, "_coherence_conflicts", 0)) + len(
                    getattr(ks, "dissonance", {}) or {})
                if konflik > 0 and konflik != int(p._pelindung_konflik_terakhir):
                    pasang = True
                p._pelindung_konflik_terakhir = konflik
        if not pasang and jenis == "lupa":
            # kesalahan terkendali yang BARU terjadi (bukan yang lama menempel)
            sekarang = getattr(self, "_salah_ingat", None)
            kunci = str((sekarang or {}).get("benar", "")) if sekarang else ""
            if kunci and kunci != str(p._pelindung_ingat_terakhir) and (
                    self._tick() - int(p._pelindung_lupa_terakhir) >= 60):
                pasang = True
                p._pelindung_ingat_terakhir = kunci
        if pasang and bool(self.params.get(kunci, True)):
            return jenis
    return None


# ---------------------------------------------------------------------
# 2. JEDA BERMAKNA — latensi yang bisa dipelajari Player, bukan acak
# ---------------------------------------------------------------------
def jeda_bermakna(self, kepada: Any = None,
                  topik: Optional[str] = None) -> Dict[str, Any]:
    """Latensi respons dari DISTRIBUSI yang berkorelasi dengan state.

    Komponen (semua terukur, tidak ada undian): konflik internal, keraguan,
    arousal, kebaruan input, dan waktu sejak interaksi terakhir. Hasilnya
    dikuantisasi supaya Player bisa belajar membacanya: "kalau Sarah diam
    dua detik, ia akan mengatakan sesuatu yang penting."
    """
    p = _pelindung_init(self)
    sebab: List[str] = []
    dasar = float(self._p("pelindung_jeda_dasar_ms"))
    # (a) konflik internal
    konflik = 0.0
    nur = self._nur()
    if nur is not None:
        cf = int(getattr(nur, "_last_conflict_tick", -10_000))
        if cf > -10_000 and self._tick() - cf <= 16:
            konflik = max(konflik, 1.0 - (self._tick() - cf) / 16.0)
    if self._dissonance() is not None:
        konflik = max(konflik, 0.7)
    if konflik > 0.0:
        sebab.append("konflik_internal")
    # (b) keraguan & (c) arousal
    ragu = self._doubt()
    aro = 0.0
    try:
        aro = float(self.naluri.mood().arousal)
    except Exception as _galat_diagnostik_242:
        _diag.catat('naluri.jeda_bermakna', "galat pada jalur fallback", galat=_galat_diagnostik_242, jalur=242)
        pass
    if ragu > 0.3:
        sebab.append("keraguan")
    if aro > 0.4:
        sebab.append("arousal")
    # (d) kebaruan input
    baru = self._pelindung_kebaruan_input(topik if topik is not None
                                          else getattr(self, "_pending_topic", ""))
    if baru > 0.3:
        sebab.append("kebaruan_input")
    # (e) waktu sejak interaksi terakhir
    jarak = 0.0
    if self._player_present and self._absence_ticks > 0:
        jarak = min(1.0, float(self._absence_ticks) /
                    max(1.0, self._p("presentasi_absence_ticks")))
    elif float(self._idle_ticks) > 0:
        jarak = min(1.0, float(self._idle_ticks) /
                    max(1.0, self._p("presentasi_idle_ticks")))
    if jarak > 0.3:
        sebab.append("jarak_interaksi")
    ms = (dasar
          + float(self._p("pelindung_jeda_bobot_konflik")) * konflik
          + float(self._p("pelindung_jeda_bobot_ragu")) * ragu
          + float(self._p("pelindung_jeda_bobot_arousal")) * aro
          + float(self._p("pelindung_jeda_bobot_baru")) * baru
          + float(self._p("pelindung_jeda_bobot_jarak")) * jarak
          + float(p._pelindung_jeda_paksa))
    maks = float(self._p("pelindung_jeda_maks_ms"))
    ms = jepit(ms, dasar, maks)
    kuantum = max(5.0, float(self._p("pelindung_jeda_kuantisasi_ms")))
    ms = int(round(ms / kuantum) * kuantum)
    p._pelindung_jeda_paksa = 0
    p._pelindung_jeda_riwayat.append(ms)
    if len(p._pelindung_jeda_riwayat) > 32:
        del p._pelindung_jeda_riwayat[:-32]
    return {"ms": ms, "sebab": sebab or ["dasar"], "komponen": {
        "konflik": round(konflik, 3), "ragu": round(ragu, 3),
        "arousal": round(aro, 3), "kebaruan": round(baru, 3),
        "jarak": round(jarak, 3)}, "dapat_dipelajari": True}


def _pelindung_kebaruan_input(self, teks: Any) -> float:
    """Fraksi kata yang belum pernah punya arti bagi NPC ini."""
    kata = _pelindung_kata(teks)
    if not kata:
        return 0.0
    p = _pelindung_init(self)
    lexicon = getattr(self.naluri, "lexicon", {}) or {}
    asing = [w for w in kata if w not in lexicon
             and w not in p._pelindung_topic_seen]
    return len(asing) / float(len(kata))


# ---------------------------------------------------------------------
# 3. ESKALASI VARIASI — empat tingkat anggaran kebaruan
# ---------------------------------------------------------------------
def eskalasi_variasi(self, teks: str, act: str, kepada: Any = None,
                     topik: Optional[str] = None
                     ) -> Tuple[str, str, Dict[str, Any]]:
    """Repetisi dilacak di empat tingkat; anggaran habis → naik satu tingkat.

      1. leksikal  → ganti pilihan kata (dari leksikon yang sudah ada)
      2. sintaksis → ganti struktur kalimat
      3. semantik  → ganti act (menjawab → mengamati/diam)
      4. pragmatis → NPC MENGAKUI repetisinya sendiri dalam karakter
    """
    p = _pelindung_init(self)
    teks = str(teks or "")
    if not teks:
        return teks, act, {}
    riwayat = [t for t in p._pelindung_teks[-5:] if t]
    p._pelindung_teks.append(teks)
    if len(p._pelindung_teks) > 6:
        del p._pelindung_teks[:-6]
    p._pelindung_act_terakhir.append(str(act))
    if len(p._pelindung_act_terakhir) > 6:
        del p._pelindung_act_terakhir[:-6]
    kata = _pelindung_kata(teks)
    sim_lex = max([_pelindung_jaccard(kata, _pelindung_kata(t))
                   for t in riwayat] or [0.0])
    deteksi = {
        "leksikal": sim_lex >= float(self._p("pelindung_ulang_leksikal")),
        "sintaksis": any(_pelindung_bentuk(teks) == _pelindung_bentuk(t)
                         and len(kata) > 2 for t in riwayat),
        "semantik": sim_lex >= float(self._p("pelindung_ulang_semantik")),
        "pragmatis": (len(p._pelindung_act_terakhir) >= 3
                      and all(a == act for a in p._pelindung_act_terakhir[-3:])),
    }
    # anggaran: terpakai saat pola terdeteksi, pulih saat bersih.
    for tingkat, kena in deteksi.items():
        maks = int(p._pelindung_anggaran_maks.get(tingkat, 2))
        kini = int(p._pelindung_anggaran.get(tingkat, maks))
        p._pelindung_anggaran[tingkat] = (max(0, kini - 1) if kena
                                          else min(maks, kini + 1))
    tingkat_aksi = None
    for tingkat in ("pragmatis", "semantik", "sintaksis", "leksikal"):
        if deteksi.get(tingkat) and int(p._pelindung_anggaran.get(tingkat, 1)) <= 0:
            tingkat_aksi = tingkat
            break
    # penanda yang digeser sistem (keragaman lintas-NPC) memaksa ganti kata
    geser = p._pelindung_geser or {}
    if tingkat_aksi is None and geser.get("penanda") and \
            geser["penanda"] in kata and self._tick() <= int(geser.get("sampai", -1)):
        tingkat_aksi = "leksikal"
    urutan = ["leksikal", "sintaksis", "semantik", "pragmatis"]
    if tingkat_aksi is None:
        return teks, act, {"tingkat": 0, "nama": None,
                           "deteksi": {k: bool(v) for k, v in deteksi.items()}}
    info: Dict[str, Any] = {"tingkat": urutan.index(tingkat_aksi) + 1,
                            "nama": tingkat_aksi,
                            "deteksi": {k: bool(v) for k, v in deteksi.items()}}
    p._pelindung_anggaran[tingkat_aksi] = int(
        p._pelindung_anggaran_maks.get(tingkat_aksi, 2))
    posisi = urutan.index(tingkat_aksi)
    while posisi < len(urutan):
        tingkat = urutan[posisi]
        if tingkat == "leksikal":
            baru = self._ganti_kata(teks)
            if baru and baru != teks:
                info["tingkat"] = urutan.index(tingkat) + 1
                info["nama"] = tingkat
                info["cara"] = "ganti_pilihan_kata"
                return baru, act, info
        elif tingkat == "sintaksis":
            baru = self._ganti_struktur(teks)
            if baru and baru != teks:
                info["tingkat"] = urutan.index(tingkat) + 1
                info["nama"] = tingkat
                info["cara"] = "ganti_struktur_kalimat"
                return baru, act, info
        elif tingkat == "semantik":
            act_baru = str(_PELINDUNG_ALTERNATIF_ACT.get(act, "mengamati"))
            inti = ""
            try:
                inti = self._generatif(act_baru, kepada, topik, masuk=False, coba=3) or ""
            except Exception as _galat_diagnostik_243:
                _diag.catat('naluri.eskalasi_variasi', "galat pada jalur fallback", galat=_galat_diagnostik_243, jalur=243)
                inti = ""
            if not inti:
                inti = self._isi_ucap(act_baru, kepada, topik or "")
            inti = self._bingkai_relasi(inti, kepada)
            if inti:
                info["tingkat"] = urutan.index(tingkat) + 1
                info["nama"] = tingkat
                info["cara"] = "ganti_act"
                info["act_baru"] = act_baru
                p._pelindung_anggaran["pragmatis"] = int(
                    p._pelindung_anggaran_maks.get("pragmatis", 2))
                return self._warnai(inti, act_baru), act_baru, info
        else:
            info["cara"] = "pengakuan_repetisi"
            return self._pengakuan_repetisi(act), act, info
        posisi += 1
    return teks, act, info


def _pengakuan_repetisi(self, act: str) -> str:
    """Tingkat 4: tell paling kuat — NPC menyadari repetisinya sendiri."""
    w = self.watak_kegagalan()
    tabel = {
        "menjawab": ("aku sudah bilang ini, kan?", "kurasa aku baru saja "
                     "mengatakannya", "kita berputar ke hal yang sama lagi"),
        "menyatakan": ("aku terdengar mengulang. Aku tahu",
                       "aku mengatakannya lagi. Maaf"),
        "bertanya": ("aku rasa aku pernah menanyakan ini",
                     "pertanyaanku sama seperti tadi, ya?"),
        "mengamati": ("aku memperhatikan hal yang sama lagi",
                      "pikiranku kembali ke tempat yang sama"),
    }
    pilihan = list(tabel.get(str(act), ("aku mengulang diriku sendiri",)))
    pilihan.append("aku sadar aku mengulang. Aku sedang tidak menemukan "
                   "kata lain")
    return _pelindung_pilih_stabil(pilihan,
                                   f"{w['nama']}|{act}|{self._tick() // 4}")


def _ganti_kata(self, teks: str) -> str:
    """Tingkat 1: ganti pilihan kata memakai kelas leksikon yang sudah ada."""
    eng = self.tutur_engine() if hasattr(self, "tutur_engine") else None
    leks = getattr(eng, "leks", None) if eng is not None else None
    if leks is None:
        return teks
    batas = [2]

    def ganti(m: Any) -> str:
        w = m.group(0)
        if batas[0] <= 0 or not w or w[0].isupper():
            return w
        lw = w.lower()
        kandidat: List[str] = []
        for kelas in (leks.kelas_dari(lw) or []):
            for e in leks.kandidat(kelas, "id"):
                lema = str(e.get("lema", ""))
                if lema and lema != lw:
                    kandidat.append(lema)
        if not kandidat:
            return w
        pilih = _pelindung_pilih_stabil(
            sorted(set(kandidat)), f"{lw}|{self._tick() // 6}")
        batas[0] -= 1
        return pilih

    return re.sub(r"\b[a-zA-Z]{4,}\b", ganti, str(teks))


def _ganti_struktur(self, teks: str) -> str:
    """Tingkat 2: ubah bangun kalimat (urutan klausa / posisi sapaan)."""
    t = str(teks or "")
    opsi: List[str] = []
    kal = [k.strip() for k in re.split(r"(?<=[.!?…])\s+", t) if k.strip()]
    if len(kal) >= 2:
        opsi.append(" ".join(kal[1:] + kal[:1]))
    if " — " in t:
        depan, belakang = t.split(" — ", 1)
        opsi.append(belakang.strip().rstrip(".") + " — " + depan.strip())
    if len(kal) == 1 and "," in t:
        depan, sisa = t.split(",", 1)
        sisa = sisa.strip()
        if sisa:
            opsi.append(sisa[0].upper() + sisa[1:] + ", " + depan.strip().lower())
    if not opsi:
        return t
    return _pelindung_pilih_stabil(opsi, f"{t[:24]}|{self._tick() // 7}")


def _pengakuan_istirahat(self, degradasi: Optional[Mapping[str, Any]] = None
                         ) -> str:
    """Degradasi level 3: NPC menyarankan mengakhiri interaksi, dalam karakter."""
    w = self.watak_kegagalan()
    pilihan = ["aku butuh istirahat sebentar",
               "kepalaku penuh. Kita lanjut nanti, ya",
               "aku tidak bisa berpikir jernih lagi. Beri aku waktu"]
    if w["nama"] == "dingin":
        pilihan.append("cukup untuk sekarang")
    if w["nama"] == "sosiawan":
        pilihan.append("maaf, aku harus berhenti dulu. Jangan pergi lama")
    if w["nama"] == "pengrajin":
        pilihan.append("tanganku mulai tidak teliti. Aku berhenti dulu")
    return _pelindung_pilih_stabil(pilihan, f"lelah|{self._tick() // 32}")


# ---------------------------------------------------------------------
# 4. PENYARING META — tidak ada state internal yang bocor ke dialog
# ---------------------------------------------------------------------
def saring_meta(self, teks: str) -> Tuple[str, List[str]]:
    """Buang angka, tag internal, dan istilah teknis; bila mustahil → padanan."""
    p = _pelindung_init(self)
    t = str(teks or "")
    if not t:
        return t, []
    bocor: List[str] = []
    out = t
    # Artefak linguistik dari mesin generatif ("A-aku bimbang…") terbaca
    # sebagai bug, bukan sebagai karakter. Diperbaiki sebelum apa pun.
    out2 = re.sub(r"^[A-Za-z]{1,2}-\s*(?=[a-zA-Z])", "", out)
    if out2 != out:
        bocor.append("artefak_linguistik")
        out = out2
    # Istilah internal dipotong, bukan dihukum: kalimat TENTANG state internal
    # masih bisa bicara setelah istilah teknisnya dibuang. Padanan in-character
    # hanya dipakai bila kalimatnya benar-benar tinggal remah.
    pola = _PELINDUNG_META_RE
    ketat = bool(p._pelindung_saring_ketat)
    cocok = list(pola.finditer(out))
    if ketat:
        cocok += list(_PELINDUNG_META_KETAT_RE.finditer(out))
    if cocok:
        bocor.append("istilah_internal")
        bersih = out
        for m in sorted(cocok, key=lambda x: x.start(), reverse=True):
            bersih = bersih[:m.start()] + " " + bersih[m.end():]
        bersih = re.sub(r"\s{2,}", " ", bersih).strip(" ,;:—-")
        isi = re.findall(r"[a-zA-Z]{4,}", bersih)
        if len(isi) < 2:
            # penyaringan tidak mungkin tanpa merusak kalimat → padanan karakter
            bocor.append("padanan_karakter")
            out = _pelindung_pilih_stabil(
                ["aku kehilangan kata untuk itu",
                 "ada sesuatu yang tidak bisa kujelaskan",
                 "aku tidak bisa mengatakannya seperti itu"],
                f"padanan|{t[:20]}|{self._tick() // 5}")
        else:
            out = bersih
    if _PELINDUNG_ANGKA_RE.search(out):
        # Angka (skor, tick, persentase) adalah bocoran meta; kuantor
        # in-character menyampaikan maksudnya tanpa angka.
        bocor.append("angka")
        out = _PELINDUNG_ANGKA_RE.sub(
            lambda m: self._kuantor_angka(m.group(0)), out)
        out = re.sub(r"\s{2,}", " ", out).strip()
    if bocor:
        p._pelindung_meta_bocor.append({"tick": self._tick(), "jenis": list(bocor)})
        if len(p._pelindung_meta_bocor) > 32:
            del p._pelindung_meta_bocor[:-32]
    return out, bocor


def _kuantor_angka(self, angka: str) -> str:
    """Angka → kuantor in-character (deterministik dari nilainya)."""
    digit = re.sub(r"[^0-9]", "", str(angka)) or "0"
    posisi = sum(int(d) for d in digit) % 4
    return ("beberapa", "banyak", "segelintir", "tak terhitung")[posisi]


# ---------------------------------------------------------------------
# 8. PENYERAP INPUT ADVERSARIAL
# ---------------------------------------------------------------------
def serap_adversarial(self, teks: str) -> Optional[Dict[str, Any]]:
    """Tes Player diserap sebagai KONTEN: NPC bereaksi sebagai karakter."""
    if not _pelindung_aktif(self):
        return None
    t = str(teks or "").strip().lower()
    if not t:
        return None
    jenis = None
    for nama, pola in _PELINDUNG_UJIAN.items():
        if re.search(pola, t):
            jenis = nama
            break
    if jenis is None:
        return None
    w = self.watak_kegagalan()
    p = _pelindung_init(self)
    balasan = _pelindung_pilih_stabil(
        list(w.get("kalimat_ujian") or w.get("kalimat_gagal") or [""]),
        f"ujian|{jenis}|{t[:24]}")
    entri = {"jenis": jenis, "tick": self._tick(), "act": str(w.get("ujian", "ragu")),
             "balasan": str(balasan), "teks": t[:80],
             "cara": "diubah menjadi konten percakapan"}
    p._pelindung_ujian_terakhir = entri
    return dict(entri)


# ---------------------------------------------------------------------
# 6. DEGRADASI ANGGUN — keterbatasan teknis menjadi narasi
# ---------------------------------------------------------------------
def degradasi_state(self) -> Dict[str, Any]:
    """Utang sesi: memori tertekan + pola terkuras + state basi.

    awal (kaya penuh) → menengah (sedikit repetisi) → panjang (lelah, dalam
    karakter) → sangat_panjang (NPC menyarankan mengakhiri interaksi).
    """
    p = _pelindung_init(self)
    if p._pelindung_sesi_mulai is None:
        p._pelindung_sesi_mulai = self._tick()
    ks = self._kes()
    memori = 0.0
    if ks is not None:
        memori = min(1.0, len(getattr(ks, "timeline", []) or []) / 150.0
                     + len(getattr(ks, "core_memory", []) or []) / 24.0)
    nur = self._nur()
    if nur is not None:
        memori = min(1.0, memori + len(getattr(nur, "_affective", {}) or {}) / 2000.0)
    total = sum(int(v) for v in p._pelindung_anggaran.values())
    maks = max(1, sum(int(v) for v in p._pelindung_anggaran_maks.values()))
    pola = 1.0 - (total / float(maks))
    sesi = min(1.0, (self._tick() - int(p._pelindung_sesi_mulai))
               / max(1.0, self._p("pelindung_degradasi_skala_sesi")))
    skor = 0.4 * memori + 0.3 * pola + 0.3 * sesi
    level = 0 if skor < 0.30 else 1 if skor < 0.50 else 2 if skor < 0.72 else 3
    return {"level": level, "mode": ("awal", "menengah", "panjang",
                                     "sangat_panjang")[level],
            "skor": round(skor, 4),
            "sebab": {"memori": round(memori, 3), "pola": round(pola, 3),
                      "sesi": round(sesi, 3)},
            "saran": ("kaya penuh" if level == 0 else
                      "sedikit repetisi" if level == 1 else
                      "lelah (dalam karakter)" if level == 2 else
                      "sarankan mengakhiri interaksi")}


def _pelindung_tanda_lelah(self, entry: Mapping[str, Any],
                           degradasi: Mapping[str, Any]) -> None:
    """Level 2: kelelahan ditampilkan lewat prosodi & satu sisipan in-character."""
    p = _pelindung_init(self)
    pros = dict(entry.get("prosodi") or {})
    if pros:
        pros["laju"] = round(max(0.1, float(pros.get("laju", 0.5)) * 0.9), 3)
        pros["volume"] = round(max(0.05, float(pros.get("volume", 0.5)) * 0.9), 3)
        pros["degradasi"] = "panjang"
        entry["prosodi"] = pros
    teks = str(entry.get("teks", ""))
    if teks and self._tick() - int(p._pelindung_degradasi_terakhir) >= 60:
        p._pelindung_degradasi_terakhir = self._tick()
        # lelah terlihat: satu kalimat pendek yang khas, bukan error
        lelah = _pelindung_pilih_stabil(
            ["aku lelah, tapi aku masih di sini",
             "suaraku menipis. Maaf",
             "aku perlu duduk sebentar setelah ini"],
            f"lelah2|{self._tick() // 24}")
        entry["teks"] = teks + " " + lelah


# ---------------------------------------------------------------------
# 7. KERAGAMAN LINTAS-NPC
# ---------------------------------------------------------------------
def keragaman_tanda(self) -> Dict[str, Any]:
    """Penanda khas NPC ini — dipakai sistem untuk menjaga keragaman scene."""
    p = _pelindung_init(self)
    teks = [str(x.get("teks", "")) for x in self._history[-12:]]
    frek: Dict[str, int] = {}
    for t in teks:
        for w in re.findall(r"[a-z]{5,}", t.lower()):
            frek[w] = frek.get(w, 0) + 1
    frasa = max(frek.items(), key=lambda kv: (kv[1], kv[0]))[0] if frek else None
    act = (max(self._act_counts.items(), key=lambda kv: (kv[1], kv[0]))[0]
           if self._act_counts else None)
    return {"act_khas": act, "frasa_khas": frasa,
            "hesitasi_khas": ("menimbang" if int(self._act_counts.get("menimbang", 0)) > 0
                              else None),
            "kekuatan_karakter": sum(int(v) for v in self._act_counts.values()),
            "dipakai_geser": dict(p._pelindung_geser)}


def dorong_geser(self, penanda: Optional[str] = None, jenis: str = "frasa",
                 sampai_tick: Optional[int] = None) -> Dict[str, Any]:
    """Sistem mendorong NPC bergeser dari penanda yang dipakai bersama."""
    p = _pelindung_init(self)
    if sampai_tick is None:
        sampai_tick = self._tick() + 2 * int(self._p("pelindung_monitor_periode"))
    if jenis in ("act", "hesitasi"):
        p._pelindung_geser["act"] = penanda
    else:
        p._pelindung_geser["penanda"] = penanda
    p._pelindung_geser["sampai"] = int(sampai_tick)
    return dict(p._pelindung_geser)


def keragaman_scene(npcs: Mapping[str, Any], tick: Optional[int] = None,
                    ambang: Optional[int] = None) -> List[Dict[str, Any]]:
    """Keragaman dijaga di TINGKAT SISTEM, bukan di tingkat NPC individual.

    Kalau dua NPC memakai penanda yang sama (act khas/frasa khas/hesitasi),
    salah satunya digeser — yang mempertahankan adalah yang karakternya paling
    terbentuk (paling banyak tanda). Tidak ada pengacakan: keputusan deterministik.
    """
    tanda: Dict[str, Dict[str, Any]] = {}
    for nama, n in dict(npcs or {}).items():
        p = _pelindung_dari(n)
        if p is None or not p.enabled():
            continue
        if not _pelindung_aktif(p):
            continue
        tanda[str(nama)] = p.keragaman_tanda()
    laporan: List[Dict[str, Any]] = []
    if ambang is None:
        contoh = next((_pelindung_dari(n) for n in dict(npcs or {}).values()
                       if _pelindung_dari(n) is not None), None)
        ambang = int(getattr(contoh, "params", {}).get(
            "pelindung_keragaman_ambang", 2))
    ambang = max(2, int(ambang))
    for kunci, jenis in (("act_khas", "act"), ("hesitasi_khas", "hesitasi"),
                         ("frasa_khas", "frasa")):
        peta: Dict[str, List[str]] = {}
        for nama, t in tanda.items():
            nilai = t.get(kunci)
            if nilai:
                peta.setdefault(str(nilai), []).append(nama)
        for nilai, kelompok in peta.items():
            if len(kelompok) < max(2, ambang):
                continue
            # pertahankan yang karakternya paling kuat; geser sisanya
            urut = sorted(kelompok,
                          key=lambda nm: (int(tanda[nm].get("kekuatan_karakter", 0)),
                                          nm))
            digeser = urut[:-1]
            dipertahankan = urut[-1]
            for nm in digeser:
                p = _pelindung_dari(dict(npcs or {})[nm])
                if p is not None:
                    p.dorong_geser(nilai, jenis=jenis, sampai_tick=tick)
            laporan.append({"jenis": jenis, "penanda": nilai,
                            "digeser": digeser, "dipertahankan": dipertahankan,
                            "tick": tick})
    return laporan


# ---------------------------------------------------------------------
# 10. MONITOR INTEGRITAS — proses latar yang mengawasi & mengoreksi
# ---------------------------------------------------------------------
class MonitorIntegritas:
    """Pengawas ilusi: repetisi lintas kanal, anomali latensi, monokultur
    kategori respons, kebasian memori, dan kebocoran meta.

    Ia tidak "menyembunyikan" temuan; ia memicu KOREKSI yang semuanya berupa
    perilaku khas manusia: memaksa variasi, memperkenalkan jeda, memicu momen
    (ritual/diam/tell), atau menyarankan rotasi NPC di tingkat Kawanan.
    """

    def __init__(self, npc: Any) -> None:
        self.npc = npc
        self.riwayat: List[Dict[str, Any]] = []
        self.koreksi: List[Dict[str, Any]] = []
        self._kebasian = 0
        self._terakhir = -10_000

    # -- pemeriksaan --------------------------------------------------
    def periksa(self, entry: Optional[Mapping[str, Any]] = None,
                tick: Optional[int] = None) -> Dict[str, Any]:
        p = _pelindung_dari(self.npc)
        if p is None or not p.enabled():
            return {"aktif": False}
        p = _pelindung_init(p)
        tick = int(tick if tick is not None else p._tick())
        temuan: List[Dict[str, Any]] = []
        koreksi: List[Dict[str, Any]] = []
        # (a) repetisi lintas kanal
        teks = [str(x.get("teks", "")) for x in p._history[-6:] if x.get("teks")]
        if len(teks) >= 3:
            sim = max(_pelindung_jaccard(_pelindung_kata(teks[-1]),
                                         _pelindung_kata(t)) for t in teks[:-1])
            if sim >= 0.7:
                temuan.append({"jenis": "repetisi_lintas_kanal", "nilai": round(sim, 3)})
                koreksi.append({"aksi": "paksa_variasi",
                                "alasan": "dua ujaran terakhir nyaris sama"})
                for k in p._pelindung_anggaran:
                    p._pelindung_anggaran[k] = 0
                p.dorong_geser(None, jenis="frasa", sampai_tick=tick + 12)
        # (b) anomali latensi: terlalu seragam atau melompat ekstrem
        jr = list(p._pelindung_jeda_riwayat[-6:])
        if len(jr) >= 4:
            rerata = sum(jr) / float(len(jr))
            variasi = max(jr) - min(jr)
            if variasi <= 25 and rerata > 0:
                temuan.append({"jenis": "latensi_monoton", "variasi": variasi})
                koreksi.append({"aksi": "perkenalkan_jeda",
                                "alasan": "latensi terlalu konsisten (terbaca mesin)"})
                p._pelindung_jeda_paksa = 350 + 150 * (len(jr) % 3)
        # (c) monokultur kategori respons
        act = [str(x.get("act", "")) for x in p._history[-12:] if x.get("act")]
        if len(act) >= 6:
            dominan = max(set(act), key=act.count)
            porsi = act.count(dominan) / float(len(act))
            if porsi >= 0.7:
                temuan.append({"jenis": "monokultur_act", "act": dominan,
                               "porsi": round(porsi, 3)})
                koreksi.append({"aksi": "paksa_variasi", "act": dominan,
                                "alasan": "satu kategori respons mendominasi"})
                p.dorong_geser(dominan, jenis="act", sampai_tick=tick + 16)
        # (d) kebasian memori (tidak ada konten baru yang mengendap)
        ks = p._kes()
        jumlah_timeline = len(getattr(ks, "timeline", []) or []) if ks else 0
        sidik = (jumlah_timeline, len(getattr(ks, "core_memory", []) or []) if ks else 0)
        sebelumnya = self.riwayat[-1].get("sidik") if self.riwayat else None
        if sebelumnya is not None and sidik == sebelumnya:
            self._kebasian += 1
        else:
            self._kebasian = 0
        if self._kebasian >= 3:
            temuan.append({"jenis": "kebasian_memori", "beruntun": self._kebasian})
            koreksi.append({"aksi": "picu_momen",
                            "alasan": "tidak ada pengalaman baru yang mengendap"})
            self._kebasian = 0
            self._picu_momen(p, koreksi)
        # (e) kebocoran meta
        bocor = [x for x in p._pelindung_meta_bocor if tick - int(x.get("tick", -10_000)) <= 48]
        if len(bocor) >= 2:
            temuan.append({"jenis": "kebocoran_meta", "jumlah": len(bocor)})
            koreksi.append({"aksi": "penyaring_meta_diperketat",
                            "alasan": "state internal berulang kali hampir bocor"})
            p._pelindung_saring_ketat = True
        elif p._pelindung_saring_ketat and len(bocor) == 0:
            p._pelindung_saring_ketat = False
        laporan = {"aktif": True, "tick": tick, "temuan": temuan,
                   "koreksi": koreksi,
                   "degradasi": p.degradasi_state()["mode"],
                   "sidik": sidik, "kebasian": self._kebasian}
        self.riwayat.append(laporan)
        if len(self.riwayat) > 32:
            del self.riwayat[:-32]
        for k in koreksi:
            self.koreksi.append(dict(k, tick=tick))
        if len(self.koreksi) > 64:
            del self.koreksi[:-64]
        return laporan

    # -- koreksi yang mengubah perilaku -------------------------------
    def _picu_momen(self, p: Any, koreksi: List[Dict[str, Any]]) -> None:
        """Momen = ritual / diam / tell. Semuanya mesin yang sudah ada."""
        dipakai = []
        ritual = getattr(self.npc, "ritual", None)
        if ritual is not None and getattr(ritual, "enabled", lambda: False)():
            try:
                peristiwa = ritual.maybe_trigger(konteks="monitor_integritas")
                if peristiwa:
                    dipakai.append("ritual")
            except Exception as _galat_diagnostik_244:
                _diag.catat('naluri.MonitorIntegritas._picu_momen', "galat pada jalur fallback", galat=_galat_diagnostik_244, jalur=244)
                pass
        tell = None
        try:
            tell = p.tell_katalog()
        except Exception as _galat_diagnostik_245:
            _diag.catat('naluri.MonitorIntegritas._picu_momen', "galat pada jalur fallback", galat=_galat_diagnostik_245, jalur=245)
            tell = None
        if tell:
            dipakai.append("tell")
        ks = p._kes()
        if ks is not None and ks.enabled("global_workspace"):
            try:
                ks.submit("aku butuh sesuatu yang bisa kupegang", salience=0.5,
                          tag="momen", source="monitor", kind="momen")
                dipakai.append("momen_kesadaran")
            except Exception as _galat_diagnostik_246:
                _diag.catat('naluri.MonitorIntegritas._picu_momen', "galat pada jalur fallback", galat=_galat_diagnostik_246, jalur=246)
                pass
        if "tell" in dipakai and tell:
            koreksi.append({"aksi": "picu_tell", "tanda": tell.get("drive")})
        if dipakai:
            koreksi.append({"aksi": "picu_momen", "dipakai": dipakai,
                            "alasan": "memberi pengalaman baru untuk diendapkan"})


# ---------------------------------------------------------------------
# PEMASANGAN: Presentasi
# ---------------------------------------------------------------------
def _pelindung_pilih_act(original, self, kepada, topik, masuk=False):
    if not _pelindung_aktif(self):
        return original(self, kepada, topik, masuk=masuk)
    hint = _pelindung_act_hint(self, kepada, topik, masuk=masuk)
    if hint:
        return hint
    act = original(self, kepada, topik, masuk=masuk)
    p = _pelindung_init(self)
    geser = dict(p._pelindung_geser or {})
    if (geser.get("act") == act
            and self._tick() <= int(geser.get("sampai", -1))):
        return str(_PELINDUNG_ALTERNATIF_ACT.get(act, act))
    return act




def _pelindung_ucap(original, self, kepada: Any = None,
                    topik: Optional[str] = None, act: Optional[str] = None,
                    masuk: bool = False,
                    diam_boleh: bool = True) -> Dict[str, Any]:
    if not _pelindung_aktif(self):
        return original(self, kepada, topik, act, masuk=masuk,
                        diam_boleh=diam_boleh)
    p = _pelindung_init(self)
    tick = self._tick()
    if p._pelindung_sesi_mulai is None:
        p._pelindung_sesi_mulai = tick
    # (6) DEGRADASI ANGGUN — sesi sangat panjang: sarankan berhenti.
    deg = self.degradasi_state()
    if deg["level"] >= 3 and (tick - int(p._pelindung_degradasi_terakhir)
                              >= int(self._p("pelindung_degradasi_ucap_ulang"))):
        p._pelindung_degradasi_terakhir = tick
        teks = _pengakuan_istirahat(self, deg)
        entry = self._pelindung_entry(teks, "istirahat", kepada, deg)
        entry["degradasi"] = deg
        return entry
    entry = original(self, kepada, topik, act, masuk=masuk,
                     diam_boleh=diam_boleh)
    if not isinstance(entry, dict) or not entry:
        return entry
    teks = str(entry.get("teks", ""))
    teks_awal = teks
    act_final = str(entry.get("act", ""))
    planned_social_speech = isinstance(entry.get("_strategic_plan"), Mapping)
    # Ujaran strategis sadar tidak boleh ditimpa tes/variasi/buffer otomatis.
    # Jeda dan monitor tetap bekerja, sementara pesan yang dipilih dipertahankan.
    ujian = None if planned_social_speech else p._pelindung_ujian_terakhir
    adversarial_dipakai = False
    if (ujian and teks
            and act_final not in ("diam", "menolak", "peringatan", "istirahat")
            and tick - int(ujian.get("tick", -10_000)) <= 2):
        teks = str(ujian.get("balasan") or teks)
        act_final = str(ujian.get("act") or act_final)
        entry["adversarial"] = {"jenis": ujian.get("jenis"),
                                "cara": ujian.get("cara")}
        adversarial_dipakai = True
    # (9) BUFFER "MANUSIAWI CUKUP" + (1/5) gagal-sebagai-akting.
    jenis_buffer = (None if adversarial_dipakai or planned_social_speech
                    else _pelindung_buffer_jenis(self, entry))
    # buffer berlaku pada ujaran-respons; act yang memang berupa tindakan
    # sadar (diam/menolak/peringatan/istirahat) tidak ditimpa.
    boleh_buffer = act_final not in ("diam", "menolak", "peringatan",
                                     "istirahat", "menantang", "mengenang")
    if jenis_buffer and boleh_buffer:
        kalimat = self.buffer_manusiawi(jenis_buffer)
        if kalimat:
            teks = kalimat
            entry["buffer_manusiawi"] = jenis_buffer
            act_final = act_final or str(self.watak_kegagalan().get("gagal", "ragu"))
            p._pelindung_buffer_terakhir = tick
            if jenis_buffer == "lupa":
                p._pelindung_lupa_terakhir = tick
            _pelindung_reset_flag(p)
    # (3) ESKALASI VARIASI — 4 tingkat anggaran kebaruan.
    if teks and not planned_social_speech:
        teks, act_final, eskalasi = self.eskalasi_variasi(teks, act_final,
                                                          kepada, topik)
        if int(eskalasi.get("tingkat", 0) or 0) > 0:
            entry["eskalasi_variasi"] = eskalasi
            entry["act"] = act_final
    # (4) PENYARING META — tidak ada state internal yang bocor ke dialog.
    if teks and not planned_social_speech:
        bersih, bocor = self.saring_meta(teks)
        if bocor:
            entry["meta_disaring"] = list(bocor)
            if bersih != teks:
                entry["teks_sebelum_saring"] = teks
            teks = bersih
    # (2) JEDA BERMAKNA — latensi yang dapat dipelajari Player.
    jeda = self.jeda_bermakna(kepada, topik)
    pros = dict(entry.get("prosodi") or {})
    pros["jeda_bermakna_ms"] = int(jeda["ms"])
    pros["sebab_jeda"] = list(jeda["sebab"])
    pros["jeda_ms"] = int(min(4000, int(pros.get("jeda_ms", 0)) + int(jeda["ms"])))
    entry["prosodi"] = pros
    # (6b) DEGRADASI level 2: lelah terlihat (dalam karakter).
    if deg["level"] == 2:
        _pelindung_tanda_lelah(self, entry, deg)
        teks = str(entry.get("teks", teks))
    entry["teks"] = teks
    if teks != teks_awal:
        try:
            entry["deskripsi"] = self.deskripsi(teks=teks,
                                                nonverbal=entry.get("nonverbal"),
                                                act=entry.get("act"), kepada=kepada)
        except Exception as _galat_diagnostik_247:
            _diag.catat('naluri._pelindung_ucap', "galat pada jalur fallback", galat=_galat_diagnostik_247, jalur=247)
            pass
    entry["pelindung"] = {"degradasi": deg["mode"], "jeda_ms": int(jeda["ms"]),
                          "sebab_jeda": list(jeda["sebab"])}
    # (10) MONITOR INTEGRITAS — mengawasi kanal & memicu koreksi.
    laporan = self.monitor_integritas().periksa(entry=entry, tick=tick)
    if laporan.get("koreksi"):
        entry["monitor_koreksi"] = laporan["koreksi"]
    # Riwayat harus berisi versi yang benar-benar dilihat Player; kalau tidak,
    # deteksi repetisi & HUD membaca teks mentah (bisa bocor meta).
    if self._history and self._history[-1].get("tick") == entry.get("tick"):
        self._history[-1] = dict(entry)
    return entry


def _pelindung_entry(self, teks: str, act: str, kepada: Any,
                     degradasi: Optional[Mapping[str, Any]] = None
                     ) -> Dict[str, Any]:
    """Entri ujaran lengkap untuk jalur yang TIDAK lewat mesin generatif."""
    nv = self.nonverbal(kepada, act)
    entry = {"tick": self._tick(), "act": act, "kepada": self._eid(kepada),
             "teks": str(teks), "nonverbal": nv, "prosodi": self.prosodi(act),
             "keyakinan": round(max(0.0, 1.0 - self._doubt()), 3),
             "generatif": False,
             "degradasi": dict(degradasi or {}),
             "pelindung": {"degradasi": (degradasi or {}).get("mode"),
                           "istirahat": True}}
    jeda = self.jeda_bermakna(kepada, None)
    pros = dict(entry.get("prosodi") or {})
    pros["jeda_ms"] = int(min(4000, int(pros.get("jeda_ms", 0)) + int(jeda["ms"])))
    pros["jeda_bermakna_ms"] = int(jeda["ms"])
    entry["prosodi"] = pros
    try:
        entry["deskripsi"] = self.deskripsi(teks=entry["teks"], nonverbal=nv,
                                            act=act, kepada=kepada)
    except Exception as _galat_diagnostik_248:
        _diag.catat('naluri._pelindung_entry', "galat pada jalur fallback", galat=_galat_diagnostik_248, jalur=248)
        pass
    self._log(entry)
    return entry




# PENAHANAN SADAR: sesudah ujaran biasa (termasuk filter pelindung/tubuh),
# sebuah isi yang memang ingin diucapkan dapat tetap tidak keluar atas pilihan
# NPC. Jalur ini tidak memanggil refuse() atau PenolakanTutur.
def _penahanan_ucap(original, self, kepada: Any = None,
                    topik: Optional[str] = None, act: Optional[str] = None,
                    masuk: bool = False,
                    diam_boleh: bool = True) -> Dict[str, Any]:
    ks = self._kes()
    pencarian = topik if topik is not None else self._pending_topic
    tertahan = None
    if ks is not None:
        try:
            tertahan = ks.withheld_for(pencarian, recipient=kepada)
        except Exception as _galat_diagnostik_249:
            _diag.catat('naluri._penahanan_ucap', "galat pada jalur fallback", galat=_galat_diagnostik_249, jalur=249)
            tertahan = None
    entry = original(
        self, kepada, topik, act, masuk=masuk, diam_boleh=diam_boleh)
    if (not isinstance(entry, dict) or not entry or tertahan is None
            or entry.get("disembunyikan")
            or entry.get("act") in ("menolak", "peringatan", "istirahat")
            or entry.get("alasan_penolakan")):
        return entry
    try:
        hasil_tahan = ks.record_withholding_attempt(tertahan.get("id"))
        if not hasil_tahan.get("aktif"):
            return entry
        jumlah = int(hasil_tahan.get("ditahan", 1))
        sakit = float(hasil_tahan.get("rasa_sakit", 0.0))
        kekuatan = float(tertahan.get("kekuatan", 0.65))
        if jumlah == 1:
            teks = "… Aku hampir mengatakan sesuatu. Bukan sekarang."
        elif jumlah < 4:
            teks = "Aku tahu kau bertanya. Tolong, biarkan aku menyimpannya dulu."
        else:
            teks = "Kata-katanya ada. Aku memilih untuk tidak mengeluarkannya."
        if entry.get("act") == "diam":
            entry["act"] = act or "menjawab"
        entry["teks"] = teks
        entry["penahanan_sadar"] = {
            "aktif": True, "mampu_mengucapkan": True,
            "pilihan_npc": True, "tidak_dapat_dipaksa": True,
            "ulangan": jumlah, "rasa_sakit": round(sakit, 3),
        }
        entry["penanda_terlihat"] = str(hasil_tahan.get("tell", ""))
        pros = dict(entry.get("prosodi") or {})
        pros["jeda_ms"] = int(min(4000, int(pros.get("jeda_ms", 0))
                                   + 360 + 300 * kekuatan + 90 * (jumlah - 1)))
        if "volume" in pros:
            pros["volume"] = round(max(0.05, float(pros["volume"])
                                       * (1.0 - 0.25 * kekuatan)), 3)
        if "laju" in pros:
            pros["laju"] = round(max(0.1, float(pros["laju"])
                                     * (1.0 - 0.15 * kekuatan)), 3)
        pros["kontur"] = "tertahan_sebelum_kata"
        pros["penahanan_sadar"] = True
        entry["prosodi"] = pros
        nv = copy.deepcopy(entry.get("nonverbal") or {})
        eksp = nv.setdefault("ekspresi", {})
        lama = str(eksp.get("kebocoran") or "").strip()
        tell = str(hasil_tahan.get("tell", "")).strip()
        eksp["kebocoran"] = (lama + "; " + tell).strip("; ") if lama else tell
        gestur = nv.setdefault("gestur", {})
        desc = str(gestur.get("deskripsi", "")).strip()
        if tell and tell not in desc:
            gestur["deskripsi"] = (desc + "; " + tell).strip("; ")
        tatapan = nv.setdefault("tatapan", {})
        tatapan["tell_penahanan"] = True
        entry["nonverbal"] = nv
        entry["deskripsi"] = self.deskripsi(
            teks=teks, nonverbal=nv, act=entry.get("act"), kepada=kepada)
        # Sinkronkan salinan yang benar-benar dilihat Player.
        if self._history and self._history[-1].get("tick") == entry.get("tick"):
            self._history[-1] = dict(entry)
        else:
            self._log(entry)
    except Exception as _galat_diagnostik_250:
        _diag.catat('naluri._penahanan_ucap', "galat pada jalur fallback", galat=_galat_diagnostik_250, jalur=250)
        pass
    return entry




# Audisi dijalankan sesudah seluruh kanal produksi/pelindung/penahanan selesai:
# yang masuk ke telinga batin adalah realisasi suara, bukan draf atau log giliran.
def _audisi_diri_ucap(original, self, kepada: Any = None,
                      topik: Optional[str] = None, act: Optional[str] = None,
                      masuk: bool = False,
                      diam_boleh: bool = True) -> Dict[str, Any]:
    entry = original(
        self, kepada, topik, act, masuk=masuk, diam_boleh=diam_boleh)
    if not isinstance(entry, dict) or not entry:
        return entry
    niat = entry.pop("_audisi_intended", None)
    ks = self._kes()
    strategic = entry.pop("_strategic_plan", None)
    if isinstance(strategic, Mapping):
        # Keputusan baru dianggap terlaksana bila kalimat yang dipilih benar-
        # benar keluar. Penolakan tubuh/penahanan dapat menggagalkan pengiriman.
        selected = str(strategic.get("teks", "")).strip()
        actual = str(entry.get("teks", "")).strip()
        delivered = (bool(selected) and actual == selected
                     and not entry.get("disembunyikan")
                     and not entry.get("penahanan_sadar"))
        if delivered and ks is not None:
            try:
                kind = str(strategic.get("jenis", ""))
                if kind == "kebohongan_sengaja":
                    ks.deliver_strategic_speech(strategic.get("id"))
                elif kind == "permainan_peran":
                    ks.record_roleplay_speech()
                elif kind == "langkah_manipulasi":
                    ks.record_manipulation_step(
                        strategic.get("plan_id"),
                        outcome={"ucapan": actual, "tindak_tutur_dikirim": True})
            except Exception as _galat_diagnostik_251:
                _diag.catat('naluri._audisi_diri_ucap', "galat pada jalur fallback", galat=_galat_diagnostik_251, jalur=251)
                pass
    # Penahanan sadar adalah pilihan bertutur yang memang disengaja; jangan
    # salah baca frasa pengganti sebagai ujaran tak sengaja.
    if entry.get("penahanan_sadar"):
        niat = entry.get("teks", "")
    elif entry.get("disembunyikan") and entry.get("teks_terbentuk"):
        niat = entry.get("teks_terbentuk")
    if ks is not None and str(entry.get("teks", "")).strip():
        try:
            ks.audition_self(
                entry.get("teks", ""), intended=niat,
                act=entry.get("act", act),
                topic=topik if topik is not None else self._pending_topic,
                audience=kepada, prosody=entry.get("prosodi"))
        except Exception as _galat_diagnostik_252:
            _diag.catat('naluri._audisi_diri_ucap', "galat pada jalur fallback", galat=_galat_diagnostik_252, jalur=252)
            pass
    # Hapus metadata niat internal dari salinan yang terlihat dan disimpan.
    if self._history and self._history[-1].get("tick") == entry.get("tick"):
        self._history[-1] = dict(entry)
    return entry




def _pelindung_dengar(original, self, teks: str, dari: Any = None,
                      konteks: Optional[Mapping[str, Any]] = None,
                      **kwargs: Any) -> Dict[str, Any]:
    hasil = original(self, teks, dari, konteks, **kwargs)
    if not _pelindung_aktif(self):
        return hasil
    p = _pelindung_init(self)
    kata = _pelindung_kata(teks)
    if kata:
        lexicon = getattr(self.naluri, "lexicon", {}) or {}
        asing = [w for w in kata if w not in lexicon
                 and w not in p._pelindung_topic_seen]
        p._pelindung_topic_seen |= set(kata)
        if len(p._pelindung_topic_seen) > 1024:
            p._pelindung_topic_seen = set(list(p._pelindung_topic_seen)[-512:])
        if len(asing) / float(len(kata)) >= 0.6:
            p._pelindung_flag["tak_paham"] = True
    # (8) tes Player dikenali & diserap; dialog berikutnya bereaksi sebagai karakter
    self.serap_adversarial(str(teks or ""))
    return hasil




def monitor_integritas(self) -> "MonitorIntegritas":
    """Monitor latar milik Presentasi (dibuat sekali)."""
    p = _pelindung_init(self)
    if p._pelindung_monitor is None:
        p._pelindung_monitor = MonitorIntegritas(self.naluri)
    return p._pelindung_monitor


def enable_pelindung(self, aktif: bool = True) -> Dict[str, Any]:
    """Nyalakan/matikan SISTEM II (lapisan pelindung ilusi) — mati bawaan."""
    self.params["enable_pelindung"] = bool(aktif)
    return {"enable_pelindung": bool(self.params.get("enable_pelindung", False)),
            "mekanisme": 10}


def pelindung_state(self) -> Dict[str, Any]:
    """Ringkasan pengawas ilusi untuk desainer (BUKAN untuk dialog)."""
    p = _pelindung_dari(self)
    if p is None:
        return {"aktif": False}
    p = _pelindung_init(p)
    return {"aktif": bool(self.params.get("enable_pelindung", False)),
            "watak": p.watak_kegagalan()["nama"],
            "tanda_kegagalan": p.watak_kegagalan()["label"],
            "degradasi": p.degradasi_state(),
            "anggaran_variasi": dict(p._pelindung_anggaran),
            "jeda_terakhir": (p._pelindung_jeda_riwayat[-1]
                              if p._pelindung_jeda_riwayat else None),
            "meta_disaring": len(p._pelindung_meta_bocor),
            "geser": dict(p._pelindung_geser),
            "ujian_terakhir": (dict(p._pelindung_ujian_terakhir)
                               if p._pelindung_ujian_terakhir else None),
            "monitor": (p.monitor_integritas().koreksi[-4:] if p._pelindung_monitor
                        else [])}


def _pelindung_to_dict(original, self) -> Dict[str, Any]:
    d = original(self)
    if getattr(self, "_pelindung_siap", False):
        d["pelindung"] = {
            "anggaran": dict(self._pelindung_anggaran),
            "anggaran_maks": dict(self._pelindung_anggaran_maks),
            "teks": list(self._pelindung_teks),
            "act_terakhir": list(self._pelindung_act_terakhir),
            "jeda_riwayat": list(self._pelindung_jeda_riwayat),
            "meta_bocor": [dict(x) for x in self._pelindung_meta_bocor],
            "flag": dict(self._pelindung_flag),
            "geser": dict(self._pelindung_geser),
            "ujian": (dict(self._pelindung_ujian_terakhir)
                      if self._pelindung_ujian_terakhir else None),
            "degradasi_terakhir": int(self._pelindung_degradasi_terakhir),
            "sesi_mulai": self._pelindung_sesi_mulai,
            "topic_seen": sorted(self._pelindung_topic_seen)[-256:],
        }
    return d




def _pelindung_from_dict(original, self, data: Mapping[str, Any]) -> "Presentasi":
    hasil = original(self, data)
    blok = (data or {}).get("pelindung") or {}
    if blok:
        p = _pelindung_init(self)
        p._pelindung_anggaran = {str(k): int(v) for k, v in
                                 (blok.get("anggaran") or {}).items()} or \
            p._pelindung_anggaran
        p._pelindung_anggaran_maks = {str(k): int(v) for k, v in
                                      (blok.get("anggaran_maks") or {}).items()} or \
            p._pelindung_anggaran_maks
        p._pelindung_teks = [str(x) for x in (blok.get("teks") or [])]
        p._pelindung_act_terakhir = [str(x) for x in
                                     (blok.get("act_terakhir") or [])]
        p._pelindung_jeda_riwayat = [int(x) for x in
                                     (blok.get("jeda_riwayat") or [])]
        p._pelindung_meta_bocor = [dict(x) for x in (blok.get("meta_bocor") or [])
                                   if isinstance(x, Mapping)]
        p._pelindung_flag = {str(k): bool(v) for k, v in
                             (blok.get("flag") or {}).items()} or \
            p._pelindung_flag
        p._pelindung_geser = dict(blok.get("geser") or p._pelindung_geser)
        p._pelindung_ujian_terakhir = (dict(blok["ujian"])
                                       if isinstance(blok.get("ujian"), Mapping)
                                       else None)
        p._pelindung_degradasi_terakhir = int(
            blok.get("degradasi_terakhir", -10_000))
        p._pelindung_sesi_mulai = blok.get("sesi_mulai")
        p._pelindung_topic_seen = set(str(x) for x in
                                      (blok.get("topic_seen") or []))
    return hasil



# API tingkat-Naluri (mem-baca/menulis params yang sama dengan Presentasi).

# API tingkat-Presentasi (dipakai mesin ilusi & pengujian perilaku).

# Presentasi yang sudah dibuat sebelum blok ini juga harus bisa memakai API
# di atas: atributnya diambil lewat getattr pada instance, jadi cukup dipasang
# di kelas (di atas). Tidak ada monkey-patch instance.


# ---------------------------------------------------------------------
# Kawanan: keragaman & monitor lintas-NPC
# ---------------------------------------------------------------------
def monitor_scene(self, tick: Optional[int] = None) -> Dict[str, Any]:
    """Keragaman + Monitor Integritas untuk SELURUH scene sekaligus."""
    laporan_keragaman = keragaman_scene(self.npcs, tick=tick)
    per_npc: Dict[str, Any] = {}
    for nama, n in self.npcs.items():
        p = getattr(n, "presentasi", None)
        if p is None or not p.enabled():
            continue
        try:
            per_npc[nama] = p.monitor_integritas().periksa(tick=tick)
        except Exception as _galat_diagnostik_253:
            _diag.catat('naluri.monitor_scene', "galat pada jalur fallback", galat=_galat_diagnostik_253, jalur=253)
            continue
    # rotasi NPC: bila dua NPC (atau lebih) memakai kategori respons yang sama,
    # salah satu disarankan untuk "diistirahatkan" dari sorotan scene.
    rotasi: List[Dict[str, Any]] = []
    for laporan in laporan_keragaman:
        if laporan.get("jenis") != "act":
            continue
        digeser = list(laporan.get("digeser") or [])
        if digeser:
            rotasi.append({"ganti": digeser[0],
                           "karena_act": laporan.get("penanda"),
                           "dipertahankan": laporan.get("dipertahankan"),
                           "cara": "geser act / istirahatkan dari sorotan"})
    return {"keragaman": laporan_keragaman, "per_npc": per_npc,
            "rotasi": rotasi, "tick": tick}


def keragaman(self, tick: Optional[int] = None) -> List[Dict[str, Any]]:
    """Alias ringkas untuk `KawananNPC.monitor_scene()["keragaman"]`."""
    return keragaman_scene(self.npcs, tick=tick)




def _pelindung_tick_all(original, self, events=None, action_cost=None, *a, **k):
    hasil = original(self, events, action_cost, *a, **k)
    try:
        p = next((_pelindung_dari(n) for n in self.npcs.values()
                  if _pelindung_aktif(n)), None)
        if p is not None:
            periode = max(1, int(p._p("pelindung_monitor_periode")))
            self._pelindung_ayun = int(getattr(self, "_pelindung_ayun", 0)) + 1
            if self._pelindung_ayun % periode == 0:
                self.monitor_scene(tick=int(getattr(p, "_tick", lambda: 0)()))
    except Exception as _galat_diagnostik_254:
        _diag.catat('naluri._pelindung_tick_all', "galat pada jalur fallback", galat=_galat_diagnostik_254, jalur=254)
        pass
    return hasil






# >>> PELINDUNG-BLOCK-END (naluri) <<<

MonitorIntegritas.__module__ = "pycos.inti.naluri"

def pasang(Naluri: type) -> None:
    """Pasang patch pelindung dengan ID dan urutan historis, idempoten."""
    wrap_method(Presentasi, "_pilih_act", _pelindung_pilih_act,
                patch_id="naluri.pelindung.pilih_act")

    wrap_method(Presentasi, "ucap", _pelindung_ucap,
                patch_id="naluri.pelindung.ucap")

    wrap_method(Presentasi, "ucap", _penahanan_ucap,
                patch_id="naluri.presentasi.penahanan_sadar")

    wrap_method(Presentasi, "ucap", _audisi_diri_ucap,
                patch_id="naluri.presentasi.audisi_diri")

    wrap_method(Presentasi, "dengar", _pelindung_dengar,
                patch_id="naluri.pelindung.dengar")

    wrap_method(Presentasi, "to_dict", _pelindung_to_dict,
                patch_id="naluri.pelindung.serialisasi")

    wrap_method(Presentasi, "from_dict", _pelindung_from_dict,
                patch_id="naluri.pelindung.deserialisasi")

    for _nama, _fn in (("enable_pelindung", enable_pelindung),
                       ("pelindung_state", pelindung_state)):
        install_method(Naluri, _nama, _fn,
                       patch_id="naluri.extension.Naluri." + _nama)

    for _nama, _fn in (("enable_pelindung", enable_pelindung),
                       ("pelindung_state", pelindung_state),
                       ("watak_kegagalan", watak_kegagalan),
                       ("pidato_gagal", pidato_gagal),
                       ("buffer_manusiawi", buffer_manusiawi),
                       ("tandai_lupa", tandai_lupa),
                       ("tandai_kontradiksi", tandai_kontradiksi),
                       ("tandai_tidak_paham", tandai_tidak_paham),
                       ("jeda_bermakna", jeda_bermakna),
                       ("eskalasi_variasi", eskalasi_variasi),
                       ("saring_meta", saring_meta),
                       ("serap_adversarial", serap_adversarial),
                       ("degradasi_state", degradasi_state),
                       ("keragaman_tanda", keragaman_tanda),
                       ("dorong_geser", dorong_geser),
                       ("monitor_integritas", monitor_integritas),
                       # util internal (dipakai antar-metode di blok ini)
                       ("_pelindung_kebaruan_input", _pelindung_kebaruan_input),
                       ("_ganti_kata", _ganti_kata),
                       ("_ganti_struktur", _ganti_struktur),
                       ("_pengakuan_repetisi", _pengakuan_repetisi),
                       ("_kuantor_angka", _kuantor_angka),
                       ("_pelindung_act_hint", _pelindung_act_hint),
                       ("_pelindung_buffer_jenis", _pelindung_buffer_jenis),
                       ("_pelindung_entry", _pelindung_entry),
                       ("_pelindung_tanda_lelah", _pelindung_tanda_lelah),
                       ("_pengakuan_istirahat", _pengakuan_istirahat)):
        install_method(Presentasi, _nama, _fn,
                       patch_id="naluri.extension.Presentasi." + _nama)

    install_methods(
        KawananNPC,
        (("monitor_scene", monitor_scene),
         ("keragaman", keragaman)),
        patch_id="naluri.kawanan.pelindung_api",
    )

    wrap_method(KawananNPC, "tick_all", _pelindung_tick_all,
                patch_id="naluri.kawanan.pelindung.tick_all")

