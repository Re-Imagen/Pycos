"""Ekstensi gejala: definisi terpisah, patch dipasang oleh registri eksplisit."""
from __future__ import annotations

import re
from typing import Any, Dict, List, Mapping, Optional
from pycos.dukungan import diagnostik as _diag
from pycos.dukungan.patching import install_method, optional_module, wrap_method
from pycos.dukungan.numerik import jepit, jepit_01, jepit_drive
from pycos.inti.kesadaran import Kesadaran

# >>> GEJALA-BLOCK-START (naluri) <<<
# =====================================================================
# SISTEM I — ORDE NOL: GEJALA MURNI → KATEGORI BARU
# =====================================================================
# State Pycos semuanya ber-orde: drive/emosi/memori (1), Kesadaran yang
# mengamati drive & NURANI yang mengamati naluri (2), organik yang mengubah
# sifat state (3 parsial). Yang tidak ada: orde nol — bahan mentah dari mana
# orde baru bisa mengkristal. Akibatnya tanpa blok ini Pycos hanya bisa
# mengombinasi kategori yang sudah ada; input yang benar-benar asing selalu
# dipetakan paksa ke kategori terdekat, dan pemetaan paksa itu terbaca sebagai
# ketidakpahaman.
#
# Blok ini TIDAK menambah modul dan tidak menambah fitur "kebaruan tiruan".
# Ia mengizinkan kebaruan muncul lewat enam langkah yang seluruhnya memakai
# mesin yang sudah ada:
#   1. Muncul   — tekanan masuk ke Kesadaran.workspace TANPA tag/source/kind;
#                 kalau ia cukup kuat, ignition terjadi.
#   2. Gagal    — tidak ada modul yang cocok. Kegagalan itu SENDIRI state:
#                 "ada sesuatu yang tidak bisa kunamai" (mode `tanpa_nama`
#                 Apersepsi, digeneralisasi dari felt ke seluruh state).
#   3. Tanda    — signature (NURANI.context_signature / crc32 stabil): penanda
#                 BEDA, bukan nama.
#   4. Calon    — drive, emosi, memori afektif, dan tutur mencoba mengklaim
#                 (semuanya bisa gagal). Berhasil = gejala menjadi state
#                 bertipe, dan tidak lagi baru.
#   5. Endapan  — berulang → kategori proto (nama sementara dari tutur, atau
#                 tetap tanpa nama); tak berulang → memudar dan meninggalkan
#                 BEKAS di Residu (catatan, bukan entri aktif).
#   6. Konsolidasi — proto yang bertahan cukup lama & sering → masuk NURANI
#                 sebagai sensitivitas baru + Kesadaran.narrative_identity
#                 sebagai klaim ("aku pernah mengalami sesuatu yang tidak bisa
#                 kujelaskan"). Kategori penuh: state yang belum pernah ada.
#
# Kategori proto disimpan di wadah organik (ikut terserialisasi), lalu
# DIMATERIALISASI lewat mekanisme yang sudah ada (core memory, klaim
# identitas, kanal sensitivitas NURANI). Tidak ada DRIVES/EMOSI baru yang
# disuntikkan, sehingga tidak ada invariant lama yang dilanggar.
#
# Sufficiency: setiap state yang belum pernah ada, menurut definisi, tidak
# cocok dengan kategori mana pun. Maka ia harus melewati momen tanpa kategori.
# Karena itu setiap state baru membutuhkan gejala murni — ia tidak bisa lahir
# langsung dari kategori lama. Primitifnya minimal: intensitas + polaritas
# (boleh None) + tanpa-tipe + menuntut. Tidak ada properti lain yang bisa
# dikurangi, dan yang tidak dimiliki (durasi, isi, sebab, tujuan) juga
# eksplisit: lihat ``GejalaMurni.state()["tidak_dimiliki"]``.
# =====================================================================


def _gejala_modul():
    """Akses modul organik (mesin orde nol) — impor malas, tanpa dependensi baru."""
    return optional_module("pycos.mandiri.organik")


def _gejala_dari(obj, seed=0):
    from pycos.inti.naluri import _organik_dari
    org = _organik_dari(obj, seed)
    if org is None:
        return None
    g = org.gejala
    # Knop desainer di KESADARAN_DEFAULTS menimpa default wadah (sekali saja).
    n = getattr(obj, "naluri", obj)
    params = getattr(n, "params", None) or {}
    if not getattr(g, "_gejala_knop", False):
        for kunci, nama, minimum in (("ambang_ulang", "gejala_ambang_ulang", 2),
                                     ("proto_min_ulang", "gejala_proto_min_ulang", 2),
                                     ("proto_min_umur", "gejala_proto_min_umur", 0),
                                     ("memudar_ticks", "gejala_memudar_ticks", 1),
                                     ("max_aktif", "gejala_max_aktif", 4)):
            if nama in params:
                try:
                    setattr(g, kunci, max(minimum, int(params[nama])))
                except (TypeError, ValueError):
                    pass
        g._gejala_knop = True
    return g


def _gejala_aktif(self) -> bool:
    return bool(self.params.get("enable_gejala", False))


# ---------------------------------------------------------------------
# LANGKAH 1–3: tekanan masuk tanpa tag/source/kind + pemberian batas
# ---------------------------------------------------------------------
def gejala_rasakan(self, intensitas: float, polaritas: Optional[float] = None,
                   sampel: str = "", tanda: Optional[str] = None,
                   tick: Optional[int] = None) -> Dict[str, Any]:
    """Rasakan tekanan yang belum punya kategori (gejala murni).

    ``intensitas`` [0..1] — seberapa keras ia menuntut.
    ``polaritas`` [-1..+1] atau ``None`` — arah belum tentu terasa; ``None``
    adalah jawaban yang sah, dan justru itulah yang membuat emosi/drive
    sering GAGAL mengklaimnya.
    ``sampel`` — bahan mentah (teks/asosiasi) bila ada; bukan label.

    Kembalian: keadaan gejala + keputusan pipeline bila ia langsung diproses.
    """
    if not _gejala_aktif(self):
        return {}
    OG = _gejala_modul()
    g = _gejala_dari(self, getattr(self, "rng_seed", 0) or 0)
    if OG is None or g is None:
        return {}
    kini = int(self.tick_count if tick is None else tick)
    x = jepit_01(float(intensitas))
    pol = (None if polaritas is None
           else jepit_drive(float(polaritas)))
    # LANGKAH 3 — tanda: signature yang sudah ada (NURANI) bila ada bahan
    # teks; kalau tidak, kuantisasi bahan mentah. Tanda bukan nama.
    if not tanda:
        nur = getattr(self, "nurani", None)
        if nur is not None and str(sampel).strip():
            tanda = "sig%08x" % (int(nur.context_signature(str(sampel))) & 0xFFFFFFFF)
        else:
            tanda = "raw" + OG.Gejala.tanda_dari(
                (round(x, 1), None if pol is None else round(pol, 1)))
    gejala = g.muncul(x, pol, tanda=tanda, tick=kini)
    self._gejala_sampel = getattr(self, "_gejala_sampel", {}) or {}
    self._gejala_sampel[str(tanda)] = str(sampel)[:120]
    if not gejala.get("baru", True):
        # Tanda ini sudah punya arti (pernah diklaim sebuah modul). Yang datang
        # bukan gejala murni: tidak ada kategori baru, jadi tidak ada yang
        # dimasukkan ke workspace sebagai "tak bernama".
        self._gejala_aktifkan_kembali(gejala)
        return {"gejala": gejala, "via_ignition": False, "dikenal": True,
                "catatan": "tanda sudah diklaim modul; bukan gejala murni"}
    detail = {"_tanpa_kategori": True, "signature": tanda,
              "intensitas": round(x, 4), "polaritas": pol,
              "sampel": str(sampel)[:120]}
    ks = getattr(self, "kesadaran", None)
    if ks is not None and ks.enabled("global_workspace"):
        # LANGKAH 1 — TANPA tag, tanpa source, tanpa kind: tak ada modul yang
        # bisa mengklaimnya lewat jalur biasa; hanya ignition yang membawanya.
        ks.submit(OG.KALIMAT_ADA_SESUATU, salience=jepit(0.15 + x, 0.3, 1.0),
                  tag="", source="", kind="", detail=dict(detail))
        hasil = {"gejala": gejala, "via_ignition": False,
                 "catatan": "masuk workspace tanpa tag/source/kind"}
        try:
            ks.attend()          # kompetisi atensi: gejala boleh memicu ignition
        except Exception as _galat_diagnostik_211:
            _diag.catat('naluri.gejala_rasakan', "galat pada jalur fallback", galat=_galat_diagnostik_211, jalur=211)
            pass
        if str(getattr(self, "_gejala_ignition_terakhir", "")) == str(tanda):
            hasil["via_ignition"] = True
        hasil["pipeline"] = dict(getattr(self, "_gejala_hasil", {}).get(tanda) or {})
        if not hasil["pipeline"]:
            hasil["catatan"] = "menunggu pemeriksaan tertunda tick berikutnya"
        return hasil
    # tanpa workspace: pipeline berjalan langsung (kesadaran tidak aktif)
    return {"gejala": gejala, "via_ignition": False,
            "pipeline": self._gejala_pipeline(tanda, tick=kini)}


def _gejala_aktifkan_kembali(self, gejala: Mapping[str, Any],
                             tick: Optional[int] = None) -> Dict[str, Any]:
    """Kategori yang sudah dimiliki dipakai ulang — dengan magnitude mengecil.

    Inilah kebalikan dari kebaruan: makin sering sesuatu dikenal, makin kecil
    pengaruhnya (habituasi). Tidak ada kategori baru dan tidak ada modul baru;
    hanya state lama yang dipakai ulang.
    """
    dikenal = dict((gejala or {}).get("dikenal") or {})
    jenis = str(dikenal.get("jenis") or "")
    kategori = dikenal.get("kategori")
    if jenis == "drive" and kategori in getattr(self, "levels", {}):
        ulang = max(1, int(dikenal.get("ulangan_dikenal", 1)))
        kecil = 0.05 / (1.0 + 0.1 * ulang)
        self.delta(str(kategori), kecil,
                   reason="gejala dikenal dipakai ulang (habituasi)")
        return {"dipakai": "drive", "kategori": kategori, "delta": round(kecil, 4)}
    if jenis == "emosi" and self._emosi_aktif() \
            and kategori in getattr(self, "emosi", {}):
        ulang = max(1, int(dikenal.get("ulangan_dikenal", 1)))
        kecil = 0.04 / (1.0 + 0.1 * ulang)
        self._emosi_naikkan(str(kategori), kecil, "gejala dikenal dipakai ulang")
        return {"dipakai": "emosi", "kategori": kategori, "delta": round(kecil, 4)}
    return {"dipakai": None, "kategori": kategori}


def _gejala_konten(self, kalimat: str, tanda: str, intensitas: float = 0.3,
                   tick: Optional[int] = None,
                   kind: str = "tanpa_nama") -> Dict[str, Any]:
    """Isi kesadaran yang lahir dari pipeline (bukan tekanan mentah)."""
    ks = getattr(self, "kesadaran", None)
    if ks is None or not ks.enabled("global_workspace"):
        return {}
    return ks.submit(str(kalimat), salience=jepit(0.2 + float(intensitas), 0.25, 1.0),
                     tag="tanpa_nama", source="apersepsi", kind=str(kind),
                     detail={"_gejala_balasan": True, "signature": str(tanda),
                             "tick_gejala": int(tick if tick is not None
                                                else self.tick_count)})


# ---------------------------------------------------------------------
# LANGKAH 4: pencalonan kategori — empat modul mencoba mengklaim
# ---------------------------------------------------------------------
def _gejala_klaim_drive(self, tanda, sampel, polaritas, intensitas, tick):
    """Drive mencoba memetakan gejala ke defisit/surplus (bisa gagal)."""
    if not str(sampel).strip():
        return None
    try:
        vektor = self.impact_of(str(sampel))
    except Exception as _galat_diagnostik_212:
        _diag.catat('naluri._gejala_klaim_drive', "galat pada jalur fallback", galat=_galat_diagnostik_212, jalur=212)
        return None
    if not vektor:
        return None
    drive, delta = max(vektor.items(), key=lambda kv: abs(float(kv[1])))
    kuat = abs(float(delta))
    amb = float(self.params.get("gejala_klaim_ambang", 0.14) or 0.14)
    if kuat < amb:
        # hampir-klaim: tidak cukup kuat untuk mengklaim, tetapi menandai
        # modul mana yang paling akrab dengan bahan ini (untuk endapan).
        return {"jenis": "drive", "kategori": str(drive), "kuat": kuat,
                "berhasil": False, "alasan": "keterkaitan terlalu lemah"}
    self.delta(str(drive), float(delta), reason="gejala diklaim drive")
    return {"jenis": "drive", "kategori": str(drive), "kuat": kuat,
            "berhasil": True}


def _gejala_klaim_emosi(self, tanda, sampel, polaritas, intensitas, tick):
    """Emosi mencocokkan pola afektif — butuh ARAH; ``None`` = gagal (sah)."""
    if polaritas is None or not self._emosi_aktif():
        return None
    dom = self.emosi_dominan(ambang=0.5)
    if not dom:
        return None
    nama, nilai = dom
    positif = {"senang", "penasaran"}
    if (float(polaritas) > 0.0) != (str(nama) in positif):
        return {"jenis": "emosi", "kategori": str(nama),
                "kuat": 0.5 * abs(float(polaritas)) * float(nilai),
                "berhasil": False, "alasan": "arah berlawanan dengan emosi dominan"}
    self._emosi_naikkan(str(nama), 0.12 * max(0.0, float(intensitas)),
                        "gejala diklaim emosi")
    return {"jenis": "emosi", "kategori": str(nama),
            "kuat": abs(float(polaritas)) * float(nilai), "berhasil": True}


def _gejala_klaim_memori(self, tanda, sampel, polaritas, intensitas, tick):
    """Memori afektif mencari slot serupa (bisa gagal: belum pernah dialami)."""
    nur = getattr(self, "nurani", None)
    if nur is None or not str(sampel).strip():
        return None
    if not nur.enabled("affective_memory"):
        return None
    try:
        prior, trust = nur.anticipate_detail(str(sampel))
    except Exception as _galat_diagnostik_213:
        _diag.catat('naluri._gejala_klaim_memori', "galat pada jalur fallback", galat=_galat_diagnostik_213, jalur=213)
        return None
    if not prior:
        return None
    drive, nilai = max(prior.items(), key=lambda kv: abs(float(kv[1])))
    kuat = abs(float(nilai))
    amb = float(self.params.get("gejala_klaim_ambang", 0.14) or 0.14)
    if kuat < amb or float(trust.get(drive, 0.0)) <= 0.0:
        return {"jenis": "memori", "kategori": str(drive), "kuat": kuat,
                "berhasil": False,
                "alasan": "pengalaman serupa belum pernah terjadi"}
    self.delta(str(drive), float(nilai), reason="gejala diklaim memori afektif")
    if hasattr(nur, "anticipate"):
        nur.anticipate(str(sampel))          # slot benar-benar dipakai
    return {"jenis": "memori", "kategori": str(drive), "kuat": kuat,
            "berhasil": True}


def _gejala_klaim_tutur(self, tanda, sampel, polaritas, intensitas, tick):
    """Tutur mencoba memberi NAMA dari kosakata yang sudah berarti (bisa gagal)."""
    teks = str(sampel).strip().lower()
    if not teks:
        return None
    kata = [w for w in re.findall(r"[a-z]{4,}", teks)][:6]
    if not kata:
        return None
    lexicon = getattr(self, "lexicon", {}) or {}
    kenal = [w for w in kata if w in lexicon]
    if not kenal:
        # tak ada nama yang sudah berarti: tutur mencalonkan diri tetapi gagal
        # (kuat = seberapa mirip kata-katanya dengan yang sudah dikenal).
        return {"jenis": "tutur", "kategori": kata[0], "kuat": 0.2,
                "berhasil": False, "alasan": "belum ada kata yang berarti"}
    return {"jenis": "tutur", "kategori": kenal[0], "kuat": 0.5,
            "nama": kenal[0], "berhasil": True}


def _gejala_nama_sementara(self, sampel: str) -> Optional[str]:
    """Tutur memberi nama SEMENTARA pada kategori proto (atau tetap tanpa nama)."""
    kata = re.findall(r"[a-z]{4,}", str(sampel).lower())[:4]
    if not kata:
        return None
    nama = str(kata[0])[:40]
    p = getattr(self, "presentasi", None)
    if p is not None and p.enabled():
        try:
            teks = p._generatif("bertanya", None, nama, masuk=False, coba=1)
        except Exception as _galat_diagnostik_214:
            _diag.catat('naluri._gejala_nama_sementara', "galat pada jalur fallback", galat=_galat_diagnostik_214, jalur=214)
            teks = None
        if not teks:
            return None                       # tutur tidak bisa menamainya
    return nama


# ---------------------------------------------------------------------
# LANGKAH 2 & 4–6: pipeline untuk satu gejala yang sudah muncul
# ---------------------------------------------------------------------
def _gejala_pipeline(self, tanda: Optional[str],
                     item: Optional[Mapping[str, Any]] = None,
                     tick: Optional[int] = None) -> Dict[str, Any]:
    """Jalankan langkah 2–6 untuk gejala yang sudah punya tanda."""
    if not _gejala_aktif(self) or not tanda:
        return {}
    OG = _gejala_modul()
    g = _gejala_dari(self, getattr(self, "rng_seed", 0) or 0)
    if OG is None or g is None:
        return {}
    # Idempoten per episode: ignition dan pemeriksaan tertunda boleh memanggil
    # berkali-kali; langkah 2–4 hanya berjalan sekali untuk satu gejala hidup.
    sudah = getattr(self, "_gejala_sudah", None)
    if sudah is None:
        sudah = {}
        self._gejala_sudah = sudah
    if str(tanda) in sudah:
        return dict(getattr(self, "_gejala_hasil", {}).get(tanda) or {})
    sudah[str(tanda)] = True
    if len(sudah) > 128:
        for kunci in list(sudah.keys())[:len(sudah) - 128]:
            sudah.pop(kunci, None)
    kini = int(self.tick_count if tick is None else tick)
    detail = dict((item or {}).get("detail") or {})
    x = float(detail.get("intensitas", 0.0) or 0.0)
    pol = detail.get("polaritas", None)
    sampel = str(detail.get("sampel", "") or "")
    # LANGKAH 2 — gagal-diklaim sebagai state (kegagalan itu sendiri state).
    gagal = g.gagal(tanda, tick=kini)
    if not gagal:
        return {"tanda": tanda, "pencalonan": [], "keputusan": {}, "gagal": {}}
    self._gejala_konten(gagal["kalimat"], tanda, x, tick=kini)
    # LANGKAH 4 — empat modul mencoba mengklaim, berurutan; semuanya boleh gagal.
    pencalonan: List[Dict[str, Any]] = []
    terklaim: Optional[Dict[str, Any]] = None
    for nama_modul, probe in (("drive", _gejala_klaim_drive),
                              ("emosi", _gejala_klaim_emosi),
                              ("memori", _gejala_klaim_memori),
                              ("tutur", _gejala_klaim_tutur)):
        hasil = probe(self, tanda, sampel, pol, x, kini)
        berhasil = bool(hasil and hasil.get("berhasil") and hasil.get("kategori"))
        pencalonan.append({"modul": nama_modul, "berhasil": berhasil,
                           "kategori": (hasil or {}).get("kategori"),
                           "kuat": round(float((hasil or {}).get("kuat", 0.0)), 4),
                           "alasan": (hasil or {}).get("alasan")})
        if berhasil and terklaim is None:
            terklaim = g.klaim(tanda, hasil.get("jenis", nama_modul),
                               hasil.get("kategori"), kuat=hasil.get("kuat", 0.0),
                               tick=kini)
            if terklaim:
                break
    if not terklaim:
        # Semua gagal → gejala tetap MURNI. Modul yang paling akrab dengan
        # bahannya (hampir-klaim terkuat) hanya menandai jenis untuk endapan.
        akrab = max(pencalonan, key=lambda c: float(c.get("kuat", 0.0)),
                    default=None)
        hint = str((akrab or {}).get("modul") or "tutur")
        g.jenis_hint(tanda, hint)
    # LANGKAH 5–6 — keputusan (diterapkan ke modul yang sudah ada di bawah).
    keputusan = g.proses(tick=kini)
    self._gejala_terapkan(keputusan, tick=kini)
    hasil = {"tanda": tanda, "pencalonan": pencalonan,
             "terklaim": terklaim, "gagal": gagal, "keputusan": keputusan}
    simpan = getattr(self, "_gejala_hasil", None)
    if simpan is None:
        simpan = {}
        self._gejala_hasil = simpan
    simpan[str(tanda)] = dict(hasil)
    if len(simpan) > 64:
        for kunci in list(simpan.keys())[:len(simpan) - 64]:
            simpan.pop(kunci, None)
    return hasil


def _gejala_terapkan(self, keputusan: Mapping[str, Any],
                     tick: Optional[int] = None) -> Dict[str, Any]:
    """Terapkan keputusan pipeline: bekas → Residu, proto, konsolidasi."""
    if not keputusan:
        return {}
    _gejala_modul()
    org = getattr(self, "_organik", None)
    kini = int(tick if tick is not None else self.tick_count)
    hasil: Dict[str, Any] = {"bekas": 0, "proto": 0, "konsolidasi": 0}
    # 5a) PEMUDARAN → bekas di Residu: catatan, bukan entri aktif.
    for bekas in keputusan.get("pemudaran", []) or []:
        if org is not None:
            org.residu.bekas("gejala", bekas.get("catatan"), tick=kini,
                             signature=bekas.get("signature"),
                             intensitas_puncak=bekas.get("intensitas_puncak"),
                             polaritas=bekas.get("polaritas"),
                             ulangan=bekas.get("ulangan"))
        self._gejala_konten("sesuatu yang tak bernama pernah terjadi",
                            str(bekas.get("signature")), 0.3, tick=kini,
                            kind="bekas")
        hasil["bekas"] = int(hasil["bekas"]) + 1
    # 5b) PENGENDAPAN → kategori proto (nama sementara dari tutur, bila bisa).
    for proto in keputusan.get("endapan", []) or []:
        nama = proto.get("nama")
        if proto.get("peristiwa") == "kategori_proto_lahir":
            nama = self._gejala_nama_sementara(
                (self._gejala_sampel or {}).get(str(proto.get("signature")), "")) or nama
        if nama:
            g = _gejala_dari(self, getattr(self, "rng_seed", 0) or 0)
            if g is not None:
                g.beri_nama(str(proto.get("signature")), nama)
        teks = ("ada sesuatu yang mulai punya bentuk"
                + (": " + str(nama) if nama else " (belum bernama)"))
        self._gejala_konten(teks, str(proto.get("signature")),
                            float(proto.get("intensitas_puncak", 0.0)) * 0.7,
                            tick=kini, kind="kategori_proto")
        hasil["proto"] = int(hasil["proto"]) + 1
    # 6) KONSOLIDASI → NURANI (sensitivitas baru) + identitas naratif.
    for penuh in keputusan.get("konsolidasi", []) or []:
        klaim = str(penuh.get("klaim_identitas")
                    or "pernah mengalami sesuatu yang tidak bisa kujelaskan")
        nur = getattr(self, "nurani", None)
        if nur is not None and hasattr(nur, "serap_kategori"):
            try:
                nur.serap_kategori(penuh.get("signature"), nama=penuh.get("nama"),
                                   jenis=penuh.get("jenis", "tutur"),
                                   kekuatan=min(0.9, 0.35 + 0.08 * float(
                                       penuh.get("jumlah", 1))),
                                   tick=kini, klaim=klaim)
            except Exception as _galat_diagnostik_215:
                _diag.catat('naluri._gejala_terapkan', "galat pada jalur fallback", galat=_galat_diagnostik_215, jalur=215)
                pass
        self._gejala_klaim_identitas(klaim, penuh, tick=kini)
        self._gejala_konten("aku pernah mengalami sesuatu yang tidak bisa kujelaskan",
                            str(penuh.get("signature")), 0.6, tick=kini,
                            kind="kategori_penuh")
        hasil["konsolidasi"] = int(hasil["konsolidasi"]) + 1
    return hasil


def _gejala_klaim_identitas(self, klaim: str, penuh: Mapping[str, Any],
                            tick: Optional[int] = None) -> Dict[str, Any]:
    """Klaim identitas lewat mekanisme yang sudah ada (bukan daftar baru)."""
    ks = getattr(self, "kesadaran", None)
    if ks is None:
        return {}
    bobot = min(0.9, 0.3 + 0.08 * float(penuh.get("jumlah", 1)))
    try:
        if ks.enabled("inner_speech"):
            ks._refresh_identity({str(klaim): bobot})
            return {"via": "refresh_identity", "klaim": str(klaim)}
        if bool(self.params.get("enable_kesadaran", False)):
            if not any(str(x.get("klaim")) == str(klaim)
                       for x in ks.narrative_identity):
                ks.narrative_identity.append({"tick": int(
                    tick if tick is not None else self.tick_count),
                    "klaim": str(klaim), "kekuatan": round(bobot, 3)})
            return {"via": "narrative_identity", "klaim": str(klaim)}
    except Exception as _galat_diagnostik_216:
        _diag.catat('naluri._gejala_klaim_identitas', "galat pada jalur fallback", galat=_galat_diagnostik_216, jalur=216)
        pass
    return {}


# ---------------------------------------------------------------------
# Pemicu: ignition (langkah 1) + pemeriksaan tertunda tiap tick
# ---------------------------------------------------------------------
def _gejala_ignite(original, self, item):
    ev = original(self, item)
    try:
        detail = dict((item or {}).get("detail") or {}) \
            if isinstance(item, Mapping) else {}
        if detail.get("_tanpa_kategori") and not detail.get("_gejala_balasan"):
            n = getattr(self, "naluri", None)
            if n is not None and _gejala_aktif(n):
                tanda = str(detail.get("signature", ""))
                n._gejala_ignition_terakhir = tanda
                # sampel mentah disimpan supaya langkah 5 bisa menamai proto
                n._gejala_sampel = getattr(n, "_gejala_sampel", {}) or {}
                n._gejala_sampel[tanda] = str(detail.get("sampel", ""))[:120]
                n._gejala_pipeline(tanda, item=item,
                                   tick=int(getattr(self, "_tick", lambda: 0)()))
    except Exception as _galat_diagnostik_217:
        _diag.catat('naluri._gejala_ignite', "galat pada jalur fallback", galat=_galat_diagnostik_217, jalur=217)
        pass
    return ev




def _gejala_proses_tertunda(self, kini: Optional[int] = None) -> int:
    """Gejala yang TIDAK mencapai ignition tetap diproses tick berikutnya."""
    ks = getattr(self, "kesadaran", None)
    if ks is None:
        return 0
    kini = int(self.tick_count if kini is None else kini)
    n = 0
    for item in list(getattr(ks, "workspace", []) or []):
        detail = dict((item or {}).get("detail") or {}) \
            if isinstance(item, dict) else {}
        if (detail.get("_tanpa_kategori") and not detail.get("_gejala_balasan")
                and int((item or {}).get("tick", kini)) < kini):
            tanda = str(detail.get("signature", ""))
            self._gejala_sampel = getattr(self, "_gejala_sampel", {}) or {}
            self._gejala_sampel[tanda] = str(detail.get("sampel", ""))[:120]
            if not (item.get("_gejala_diproses")):
                self._gejala_pipeline(tanda, item=item, tick=kini)
                try:
                    item["_gejala_diproses"] = True
                except Exception as _galat_diagnostik_218:
                    _diag.catat('naluri._gejala_proses_tertunda', "galat pada jalur fallback", galat=_galat_diagnostik_218, jalur=218)
                    pass
                n += 1
    return n


def _gejala_tick(original, self, *a, **k):
    hasil = original(self, *a, **k)
    if _gejala_aktif(self):
        try:
            self._gejala_proses_tertunda()
            g = _gejala_dari(self, getattr(self, "rng_seed", 0) or 0)
            if g is not None:
                keputusan = g.proses(tick=int(self.tick_count))
                if keputusan.get("pemudaran") or keputusan.get("endapan") \
                        or keputusan.get("konsolidasi"):
                    self._gejala_terapkan(keputusan, tick=int(self.tick_count))
        except Exception as _galat_diagnostik_219:
            _diag.catat('naluri._gejala_tick', "galat pada jalur fallback", galat=_galat_diagnostik_219, jalur=219)
            pass
    return hasil




def enable_gejala(self, aktif: bool = True) -> Dict[str, Any]:
    """Nyalakan/matikan SISTEM I (orde nol) — mati bawaan."""
    self.params["enable_gejala"] = bool(aktif)
    return {"enable_gejala": bool(self.params.get("enable_gejala", False)),
            "pipeline": "muncul → gagal → tanda → calon → endapan → konsolidasi"}


def gejala_state(self) -> Dict[str, Any]:
    """Keadaan orde nol: gejala hidup, proto, kategori penuh, bekas."""
    g = _gejala_dari(self, getattr(self, "rng_seed", 0) or 0)
    if g is None:
        return {"aktif": False}
    st = g.state()
    org = getattr(self, "_organik", None)
    st["aktif"] = bool(self.params.get("enable_gejala", False))
    st["residu_bekas"] = (org.residu.bekas_state()[-5:] if org is not None else [])
    st["sensitivitas_nurani"] = dict(
        getattr(getattr(self, "nurani", None), "kategori_proto", {}) or {})
    return st


def _gejala_hud_state(original, self):
    # Panggil implementasi HUD yang sudah menyertakan lapisan ORGANIK.
    st = original(self)
    try:
        st = dict(st or {})
        if _gejala_aktif(self.naluri):
            st["gejala"] = {
                "aktif": len([x for x in self.naluri.gejala_state().get("gejala", [])
                              if x.get("hidup")]),
                "proto": len(self.naluri.gejala_state().get("proto", [])),
                "kategori_penuh": len(self.naluri.gejala_state().get(
                    "kategori_penuh", [])),
                "bekas": len(self.naluri.gejala_state().get("residu_bekas", [])),
            }
    except Exception as _galat_diagnostik_220:
        _diag.catat('naluri._gejala_hud_state', "galat pada jalur fallback", galat=_galat_diagnostik_220, jalur=220)
        pass
    return st







# >>> GEJALA-BLOCK-END (naluri) <<<

def pasang(Naluri: type) -> None:
    """Pasang patch dengan urutan dan ID historis."""
    wrap_method(Kesadaran, "_ignite", _gejala_ignite,
                patch_id="naluri.gejala.ignite")

    wrap_method(Naluri, "tick", _gejala_tick,
                patch_id="naluri.gejala.tick")

    wrap_method(Kesadaran, "hud_state", _gejala_hud_state,
                patch_id="naluri.gejala.hud_state")

    for _nama, _fn in (("enable_gejala", enable_gejala),
                       ("gejala_rasakan", gejala_rasakan),
                       ("rasakan", gejala_rasakan),
                       ("gejala_state", gejala_state),
                       ("_gejala_pipeline", _gejala_pipeline),
                       ("_gejala_terapkan", _gejala_terapkan),
                       ("_gejala_klaim_drive", _gejala_klaim_drive),
                       ("_gejala_klaim_emosi", _gejala_klaim_emosi),
                       ("_gejala_klaim_memori", _gejala_klaim_memori),
                       ("_gejala_klaim_tutur", _gejala_klaim_tutur),
                       ("_gejala_klaim_identitas", _gejala_klaim_identitas),
                       ("_gejala_konten", _gejala_konten),
                       ("_gejala_aktifkan_kembali", _gejala_aktifkan_kembali),
                       ("_gejala_nama_sementara", _gejala_nama_sementara),
                       ("_gejala_proses_tertunda", _gejala_proses_tertunda)):
        install_method(Naluri, _nama, _fn,
                       patch_id="naluri.extension.Naluri." + _nama)

