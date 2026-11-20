"""Ekstensi organik: definisi terpisah, patch dipasang oleh registri eksplisit."""
from __future__ import annotations

import math
import re
from typing import Mapping
from pycos.dukungan import diagnostik as _diag
from pycos.dukungan.patching import install_method, install_methods, optional_module, wrap_method
from pycos.dukungan.numerik import jepit_01, jepit_drive
from pycos.inti._konfigurasi import DRIVES, EMOSI_ALIASES, FELT_STATES
from pycos.inti.kesadaran import Kesadaran
from pycos.inti.presentasi import Presentasi

# >>> ORGANIK-BLOCK-START (naluri) <<<
# =====================================================================
# INTEGRASI STATE ORGANIK (pycos.mandiri.organik)
#   1. TopologiSlot   -> Naluri (slot) + Kesadaran.future_simulation (veto)
#   3. BatasIdentitas -> Naluri._emosi_naikkan (emosi ditolak oleh state)
#   5. PenolakanTutur -> Presentasi.ucap (kalimat terbentuk, tidak terucap)
#   7. LapisanParalel -> kontradiksi sadar tidak dihukum koherensi
#   9. Residu         -> ambang/plafon emosi dan keputusan berubah permanen
#  10. Intrusi        -> sampel _affective menembus attend biasa
#  11. DetakInternal  -> checkpoint sub-tick + interupsi presentasi
#  12. Vacancy        -> waktu + decay dasar tanpa pemrosesan/log internal
# =====================================================================
def _organik_dari(obj, seed=0):
    org = getattr(obj, "_organik", None)
    if org is None:
        modul = optional_module("pycos.mandiri.organik")
        if modul is None:
            return None
        org = modul.Organik(seed=int(seed or 0))
        obj._organik = org
    return org


def _organik_bungkus_serialisasi(cls, ambil, pasang, kunci="organik"):
    """Sisipkan state Organik melalui wrapper yang mempertahankan serializer."""
    awalan = "naluri.organik.serialisasi." + cls.__name__

    def _ambil_state(original, self, *a, **kw):
        data = original(self, *a, **kw)
        if isinstance(data, dict):
            try:
                data[kunci] = ambil(self)
            except Exception as _galat_diagnostik_191:
                _diag.catat('naluri._organik_bungkus_serialisasi._ambil_state', "galat pada jalur fallback", galat=_galat_diagnostik_191, jalur=191)
                pass
        return data

    def _pasang_state(original, cls_asal, data, *a, **kw):
        hasil = original(cls_asal, data, *a, **kw)
        if isinstance(data, Mapping) and data.get(kunci):
            try:
                pasang(hasil, data[kunci])
            except Exception as _galat_diagnostik_192:
                _diag.catat('naluri._organik_bungkus_serialisasi._pasang_state', "galat pada jalur fallback", galat=_galat_diagnostik_192, jalur=192)
                pass
        return hasil

    wrap_method(cls, "to_dict", _ambil_state,
                patch_id=awalan + ".to_dict")
    wrap_method(cls, "from_dict", _pasang_state,
                patch_id=awalan + ".from_dict")


# ---------------- NALURI: topologi slot + batas identitas ----------------
def _naluri_organik(self):
    return _organik_dari(self, getattr(self, "rng_seed", 0) or 0)


def _naluri_organik_ambil(self):
    o = getattr(self, "_organik", None)
    return o.to_dict() if o is not None else {}


def _naluri_organik_pasang(self, d):
    modul = optional_module("pycos.mandiri.organik")
    if modul is None:
        return
    try:
        self._organik = modul.Organik.from_dict(
            d, seed=int(getattr(self, "rng_seed", 0) or 0))
        self._vacant = bool(self._organik.vacancy.aktif)
    except (AttributeError, TypeError, ValueError):
        pass


def _naluri_tick(self):
    return int(getattr(self, "tick_count", 0) or 0)


# --- 1. kehilangan topologis ---
def daftarkan_slot(self, ent, atribut=None):
    o = _naluri_organik(self)
    return None if o is None else o.topologi.daftar(ent, atribut, tick=_naluri_tick(self))


def kosongkan_slot(self, ent, alasan=""):
    o = _naluri_organik(self)
    return None if o is None else o.topologi.kosongkan(ent, alasan, tick=_naluri_tick(self))


def isi_ulang_slot(self, ent, alasan="kembali"):
    o = _naluri_organik(self)
    return None if o is None else o.topologi.isi_ulang(ent, tick=_naluri_tick(self), alasan=alasan)


def slot_terisi(self, ent):
    o = getattr(self, "_organik", None)
    return True if o is None else o.topologi.terisi(ent)


def intensitas_topologis(self, ent, skalar=0.0):
    """None bila slot kosong. Pemanggil yang butuh angka harus memutuskan sendiri."""
    o = getattr(self, "_organik", None)
    return float(skalar) if o is None else o.topologi.intensitas(ent, skalar)


def layak_cabang(self, ent):
    o = getattr(self, "_organik", None)
    return True if o is None else o.topologi.layak_cabang(ent)


def duka(self, ent):
    """1.0 bila slot ent kosong (berduka), 0.0 bila masih terisi (sedih biasa)."""
    o = getattr(self, "_organik", None)
    if o is None:
        return 0.0
    return 1.0 if o.topologi.peek(ent).get("status") == "kosong" else 0.0


def kehilangan_state(self):
    o = getattr(self, "_organik", None)
    if o is None:
        return {}
    kosong = o.topologi.kosong()
    return {"slot_kosong": kosong, "jumlah": len(kosong), "berduka": bool(kosong),
            "catatan": {e: o.topologi.peek(e) for e in kosong}}


def cabang_mustahil(self):
    ks = getattr(self, "kesadaran", None)
    return list(getattr(ks, "_cabang_mustahil", None) or []) if ks is not None else []


# --- 3. identitas yang membatasi ---
def tetapkan_identitas(self, klaim, batas=None):
    o = _naluri_organik(self)
    return None if o is None else o.identitas.tetapkan(klaim, batas)


def batas_identitas_state(self):
    o = getattr(self, "_organik", None)
    return {} if o is None else o.identitas.state()


def emosi_ditolak(self):
    o = getattr(self, "_organik", None)
    return [] if o is None else o.identitas.penolakan()


def tandai_stimulus_bertentangan(self, aktif=True):
    self._stimulus_bertentangan = bool(aktif)
    return self._stimulus_bertentangan


def organik_state(self):
    o = getattr(self, "_organik", None)
    return {} if o is None else o.ringkas()




def _organik_emosi_naikkan(original, self, emosi, jumlah, alasan="", *a, **k):
    """Identitas membatasi; Residu mengubah ambang/plafon, bukan intensitas."""
    o = getattr(self, "_organik", None)
    if o is not None and o.identitas.klaim:
        bertentangan = bool(getattr(self, "_stimulus_bertentangan", False))
        if "bertentangan" in str(alasan).lower():
            bertentangan = True
        izin, jml, sebab = o.identitas.izinkan(emosi, jumlah, bertentangan)
        if not izin:
            o.identitas.catat_penolakan(emosi, jumlah, sebab, _naluri_tick(self))
            return 0.0
        jumlah = jml
    nama = EMOSI_ALIASES.get(str(emosi).lower())
    if o is not None and nama is not None and float(jumlah) > 0.0:
        before = float(self.emosi.get(nama, 0.0))
        dasar = float(self.params.get("emosi_ambang", 0.02))
        ambang = o.residu.ambang_dimodifikasi(nama, dasar)
        langit = o.residu.langit_dimodifikasi(nama, 1.0)
        kandidat = before + float(jumlah)
        if kandidat < ambang:
            return before
        jumlah = max(0.0, min(kandidat, langit) - before)
        if jumlah <= 0.0:
            return before
    hasil = original(self, emosi, jumlah, alasan, *a, **k)
    # Emosi negatif ekstrem boleh mengendap menjadi perubahan aturan.
    if nama in ("sedih", "takut", "marah") and hasil >= 0.88:
        oo = _naluri_organik(self)
        if oo is not None:
            oo.residu.daftar(alasan or nama, nama, hasil,
                             tick=_naluri_tick(self))
    return hasil




# --- 1b. Kesadaran.future_simulation: cabang dengan slot kosong TIDAK dibangun ---
def _organik_future_simulation(original, self, skenario=None, horizon=24, *a, **k):
    ent = original(self, skenario, horizon, *a, **k)
    try:
        if not isinstance(ent, dict) or not ent:
            return ent
        if ent.get("dibatasi_tubuh"):
            return ent
        n = getattr(self, "naluri", None)
        o = getattr(n, "_organik", None) if n is not None else None
        if o is None:
            return ent
        mustahil = o.topologi.cabang_mustahil(ent.get("skenario", ""))
        if not mustahil:
            return ent
        # cabang DIBATALKAN (bukan diberi bobot rendah)
        try:
            if getattr(self, "future_sim", None) and self.future_sim[-1] is ent:
                self.future_sim.pop()
        except Exception as _galat_diagnostik_193:
            _diag.catat('naluri._organik_future_simulation', "galat pada jalur fallback", galat=_galat_diagnostik_193, jalur=193)
            pass
        log = getattr(self, "_cabang_mustahil", None)
        if log is None:
            log = []
            self._cabang_mustahil = log
        log.append({"tick": _naluri_tick(n),
                    "skenario": str(ent.get("skenario", ""))[:160],
                    "slot_kosong": mustahil,
                    "sebab": "slot kosong - cabang tidak dapat dibangun"})
        if len(log) > 32:
            del log[:-32]
        return {}
    except Exception as _galat_diagnostik_194:
        _diag.catat('naluri._organik_future_simulation', "galat pada jalur fallback", galat=_galat_diagnostik_194, jalur=194)
        pass
    return ent




# --- 5. Presentasi: tubuh menolak mengartikulasi yang sudah terbentuk ---
def _presentasi_organik(self):
    n = getattr(self, "naluri", None)
    if n is None:
        return None
    return _organik_dari(n, getattr(n, "rng_seed", 0) or 0)


def _organik_konteks_tubuh(pres):
    n = getattr(pres, "naluri", None)
    if n is None:
        return {}
    em = getattr(n, "emosi", None) or {}
    arousal = 0.0
    try:
        m = n.mood()
        arousal = float(getattr(m, "arousal", 0.0) or 0.0)
    except Exception as _galat_diagnostik_195:
        _diag.catat('naluri._organik_konteks_tubuh', "galat pada jalur fallback", galat=_galat_diagnostik_195, jalur=195)
        arousal = 0.0
    lv = getattr(n, "levels", None) or {}
    koher = 1.0 - max(0.0, -float(lv.get("koherensi", 0.0) or 0.0))
    o = getattr(n, "_organik", None)
    duka = 0.0
    batas = False
    if o is not None:
        k = len(o.topologi.kosong())
        if k:
            duka = min(1.0, 0.5 + 0.15 * k)
        batas = bool(o.identitas.klaim)
    return {"arousal": arousal,
            "takut": float(em.get("takut", 0.0) or 0.0),
            "malu": float(em.get("malu", 0.0) or 0.0),
            "koherensi": koher, "duka": duka, "batas_identitas": batas}


def kelayakan_tutur(self):
    o = _presentasi_organik(self)
    if o is None:
        return {"kelayakan": 1.0, "komponen": {}}
    kel, komp = o.tutur.kelayakan(_organik_konteks_tubuh(self))
    return {"kelayakan": round(kel, 3), "ambang": o.tutur.ambang,
            "komponen": {k: round(v, 3) for k, v in komp.items()}}


def penolakan_state(self):
    o = _presentasi_organik(self)
    return {"riwayat": []} if o is None else {"ambang": o.tutur.ambang,
                                              "riwayat": o.tutur.riwayat()}


def _organik_ucap(original, self, kepada=None, topik=None, *a, **k):
    ent = original(self, kepada, topik, *a, **k)
    try:
        if not isinstance(ent, dict):
            return ent
        o = _presentasi_organik(self)
        if o is None:
            return ent
        kel, komp = o.tutur.kelayakan(_organik_konteks_tubuh(self))
        if kel >= o.tutur.ambang or not o.tutur.tertahan(kel, o.rng):
            return ent
        teks = ent.get("teks", "")
        if not teks:
            return ent
        bentuk = o.tutur.bentuk(teks, o.rng)
        n = getattr(self, "naluri", None)
        o.tutur.catat(teks, bentuk, kel, komp, tick=_naluri_tick(n))
        ent["teks_terbentuk"] = teks
        ent["teks"] = bentuk
        ent["disembunyikan"] = True
        ent["alasan_penolakan"] = "tubuh menolak"
        ent["kelayakan_tutur"] = round(kel, 3)
        ent["komponen_penolakan"] = {kk: round(vv, 3) for kk, vv in komp.items()}
    except Exception as _galat_diagnostik_196:
        _diag.catat('naluri._organik_ucap', "galat pada jalur fallback", galat=_galat_diagnostik_196, jalur=196)
        pass
    return ent




# ---------------- 6. APERSEPSI: sistem boleh gagal menamai ----------------
def _organik_felt_mentah(self):
    felt = {}
    ks = getattr(self, "kesadaran", None)
    if ks is not None:
        try:
            f = getattr(ks, "felt_state", None)
            if isinstance(f, dict):
                felt = {k: float(v or 0.0) for k, v in f.items()}
        except Exception as _galat_diagnostik_197:
            _diag.catat('naluri._organik_felt_mentah', "galat pada jalur fallback", galat=_galat_diagnostik_197, jalur=197)
            felt = {}
    if not felt:
        nu = getattr(self, "nurani", None)
        if nu is not None:
            try:
                fr = nu.felt_report()
                if isinstance(fr, dict):
                    felt = {k: float(v) for k, v in fr.items()
                            if isinstance(v, (int, float))}
            except Exception as _galat_diagnostik_198:
                _diag.catat('naluri._organik_felt_mentah', "galat pada jalur fallback", galat=_galat_diagnostik_198, jalur=198)
                felt = {}
    return felt


def apersepsi_state(self):
    """Modus persepsi-diri: jelas / kabut / gradien / tanpa_nama / kosong.

    Ketidakhadiran nama adalah STATE yang terlihat, bukan kegagalan diam-diam.
    """
    o = _naluri_organik(self)
    if o is None:
        return {"modus": "jelas", "nama": None, "kalimat": "", "aktif": False}
    try:
        dikenal = list(FELT_STATES)
    except NameError:
        dikenal = None
    st = o.apersepsi.amati(_organik_felt_mentah(self),
                           getattr(self, "levels", {}) or {},
                           dikenal=dikenal, klaim_identitas=o.identitas.klaim)
    st["aktif"] = True
    return st


def rasa_kabut(self):
    return self.apersepsi_state().get("modus") in ("kabut", "gradien", "tanpa_nama")


def _organik_felt_report_jujur(self):
    """Laporan perasaan yang boleh berbunyi "aku tidak tahu kenapa aku begini"."""
    ap = self.apersepsi_state()
    return {"modus": ap.get("modus"), "nama": ap.get("nama"),
            "kalimat": ap.get("kalimat"),
            "keyakinan_nama": ap.get("keyakinan_nama"),
            "gradien": ap.get("gradien"),
            "signature": ap.get("signature")}


# ---------------- 7. LAPISAN PARALEL: tanpa penyelesaian ----------------
def pegang_dua(self, klaim_a, klaim_b, bobot_a=0.6, bobot_b=0.4,
               emosi_a=None, emosi_b=None, konteks_a=None, konteks_b=None):
    """Dua keyakinan bertentangan hidup berdampingan. Tidak ada resolusi."""
    o = _naluri_organik(self)
    if o is None:
        return {}
    t = _naluri_tick(self)
    a = o.paralel.tambah(klaim_a, bobot_a, emosi_a, konteks_a, tick=t)
    b = o.paralel.tambah(klaim_b, bobot_b, emosi_b, konteks_b, tick=t,
                         lawan_dari=a["id"])
    return {"a": a, "b": b}


def pegang_keyakinan(self, klaim, bobot=0.5, emosi=None, konteks=None):
    o = _naluri_organik(self)
    if o is None:
        return {}
    return o.paralel.tambah(klaim, bobot, emosi, konteks, tick=_naluri_tick(self))


def keyakinan_paralel(self):
    o = getattr(self, "_organik", None)
    return {} if o is None else o.paralel.state()


def pengaruh_paralel(self, konteks=None):
    o = getattr(self, "_organik", None)
    return {} if o is None else o.paralel.pengaruh(konteks)


def tanpa_resolusi(self):
    o = getattr(self, "_organik", None)
    return False if o is None else o.paralel.tanpa_resolusi()


def bertindak_dari_lapisan(self, konteks):
    o = getattr(self, "_organik", None)
    return {} if o is None else (o.paralel.bertindak_dari(konteks) or {})


# ---------------- 8. TUBUH SUMBER: mendahului kognisi ----------------
def _organik_tubuh_langkah(self):
    """Tubuh bergerak lebih dulu; drive menyusul."""
    o = getattr(self, "_organik", None)
    if o is None:
        return {}
    delta = o.tubuh.langkah(_organik_felt_mentah(self),
                            getattr(self, "emosi", {}) or {},
                            getattr(self, "levels", {}) or {})
    for d, v in delta.items():
        # Wrapper berjalan setelah fisika menjepit level; jangan merusak
        # domain snapshot lagi dengan delta tubuh pasca-tick.
        sekarang = float(self.levels.get(d, 0.0))
        v = jepit_drive(sekarang + float(v)) - sekarang
        diterapkan = False
        try:
            self.delta(d, v, reason="tubuh mendahului kognisi")
            diterapkan = True
        except Exception as _galat_diagnostik_199:
            _diag.catat('naluri._organik_tubuh_langkah', "galat pada jalur fallback", galat=_galat_diagnostik_199, jalur=199)
            diterapkan = False
        if not diterapkan:
            try:
                self.levels[d] = float(self.levels.get(d, 0.0)) + float(v)
            except Exception as _galat_diagnostik_200:
                _diag.catat('naluri._organik_tubuh_langkah', "galat pada jalur fallback", galat=_galat_diagnostik_200, jalur=200)
                pass
    return delta


def tubuh_state(self):
    o = getattr(self, "_organik", None)
    return {} if o is None else o.tubuh.state()


def suntik_tubuh(self, jumlah):
    """Perturbasi tubuh tanpa sebab kognitif (untuk membuktikan arah panah)."""
    o = _naluri_organik(self)
    return 0.0 if o is None else o.tubuh.suntik(jumlah)


def _organik_tick(original, self, *a, **k):
    from pycos.inti.naluri import _organik_tubuh_langkah
    vacant_sebelum = bool(getattr(self, "_vacancy_aktif", lambda: False)())
    hasil = original(self, *a, **k)
    if vacant_sebelum:
        return hasil
    try:
        _organik_tubuh_langkah(self)
    except Exception as _galat_diagnostik_201:
        _diag.catat('naluri._organik_tick', "galat pada jalur fallback", galat=_galat_diagnostik_201, jalur=201)
        pass
    return hasil


# ---------------- 4c. deteksi slot OTOMATIS dari jejak ----------------
_NAMA_STOP = {"aku", "kamu", "dia", "mereka", "kita", "kami", "ini", "itu",
              "dan", "tapi", "karena", "kalau", "jika", "saat", "ketika",
              "setelah", "sebelum", "yang", "tidak", "bukan", "sudah", "belum",
              "masih", "hari", "malam", "pagi", "pemain", "player"}


def _nama_dari_teks(teks):
    hasil = []
    for m in re.finditer(r"\b([A-Z][a-z]{2,})\b", str(teks or "")):
        nama = m.group(1)
        if m.start() == 0:
            continue
        if nama.lower() in _NAMA_STOP:
            continue
        hasil.append(nama)
    return hasil


def auto_deteksi_slot(self, min_kemunculan=1):
    """Daftarkan slot dari JEJAK: pola aktor + nama yang muncul di episode.

    Tidak perlu lagi memanggil daftarkan_slot() satu per satu.
    """
    o = _naluri_organik(self)
    if o is None:
        return {}
    kandidat = {}
    j = getattr(self, "jejak", None)
    if j is not None:
        # _actor_log mencatat SETIAP pengamatan aktor — termasuk yang belum
        # menyeberang ambang pola. Tanpa ini, aktor yang baru muncul sekali
        # (mis. "Budi menipu" tunggal) tidak pernah terdeteksi sebagai slot.
        for entri in (getattr(j, "_actor_log", None) or []):
            if isinstance(entri, dict):
                aktor = entri.get("actor")
                if aktor:
                    kunci_a = str(aktor)
                    kandidat[kunci_a] = kandidat.get(kunci_a, 0) + 1
        for key, slot in (getattr(j, "_patterns", None) or {}).items():
            aktor = slot.get("actor") if isinstance(slot, dict) else None
            if not aktor and isinstance(key, str) and "|" in key:
                aktor = key.split("|", 1)[0]
            if aktor:
                n = int(slot.get("count", 1)) if isinstance(slot, dict) else 1
                kandidat[str(aktor)] = kandidat.get(str(aktor), 0) + max(1, n)
        for ep in (getattr(j, "_episodes", None) or []):
            for teks in (ep.get("stimulus", ""), ep.get("label", ""),
                         ep.get("context", "")):
                for nama in _nama_dari_teks(teks):
                    kandidat[nama] = kandidat.get(nama, 0) + 1
    ks = getattr(self, "kesadaran", None)
    if ks is not None:
        for item in (getattr(ks, "timeline", None) or []):
            teks = item.get("ringkas", "") if isinstance(item, dict) else item
            for nama in _nama_dari_teks(teks):
                kandidat[nama] = kandidat.get(nama, 0) + 1
    baru = {}
    for nama, n in sorted(kandidat.items(), key=lambda kv: -kv[1]):
        if n < int(min_kemunculan):
            continue
        if o.topologi.peek(nama).get("status"):
            continue
        o.topologi.daftar(nama, {"sumber": "jejak", "kemunculan": n},
                          tick=_naluri_tick(self))
        baru[nama] = n
    return baru


# ---------------- hud_state: ketidakhadiran harus TERLIHAT ----------------
def _organik_hud_state(original, self):
    d = original(self)
    try:
        n = getattr(self, "naluri", None)
        o = getattr(n, "_organik", None) if n is not None else None
        if o is not None and isinstance(d, dict):
            ap = n.apersepsi_state()
            d["apersepsi"] = {"modus": ap.get("modus"), "nama": ap.get("nama"),
                              "kalimat": ap.get("kalimat"),
                              "keyakinan_nama": ap.get("keyakinan_nama")}
            d["identitas_ada"] = bool(str(o.identitas.klaim).strip())
            d["keyakinan_paralel"] = o.paralel.state()
            d["tubuh"] = {"tegang": round(o.tubuh.tegang, 4)}
    except Exception as _galat_diagnostik_202:
        _diag.catat('naluri._organik_hud_state', "galat pada jalur fallback", galat=_galat_diagnostik_202, jalur=202)
        pass
    return d



# ---------------- 9. RESIDU: aturan yang tidak decay ----------------
def daftarkan_residu(self, sumber, drive_emosi, magnitudo):
    o = _naluri_organik(self)
    if o is None:
        return {}
    return o.residu.daftar(sumber, drive_emosi, magnitudo,
                           tick=_naluri_tick(self))


def tambal_residu(self, peristiwa, target=None, kekuatan=0.25):
    o = _naluri_organik(self)
    if o is None:
        return {"ditambal": False}
    return o.residu.tambal(peristiwa, target=target, kekuatan=kekuatan,
                           tick=_naluri_tick(self))


def ambang_dimodifikasi(self, emosi, nilai_dasar):
    o = _naluri_organik(self)
    return float(nilai_dasar) if o is None else \
        o.residu.ambang_dimodifikasi(emosi, nilai_dasar)


def langit_dimodifikasi(self, emosi, nilai_dasar):
    o = _naluri_organik(self)
    return float(nilai_dasar) if o is None else \
        o.residu.langit_dimodifikasi(emosi, nilai_dasar)


def residu_state(self):
    o = getattr(self, "_organik", None)
    return {"aktif": {}, "tekanan": 0.0} if o is None else o.residu.state()


# ---------------- 12. VACANCY: waktu tanpa pemrosesan ----------------
def mulai_vacancy(self, durasi):
    o = _naluri_organik(self)
    if o is None:
        return {"aktif": False}
    state = o.vacancy.mulai(durasi, tick=_naluri_tick(self))
    self._vacant = bool(state.get("aktif"))
    return state


def vacancy_state(self):
    o = getattr(self, "_organik", None)
    if o is None:
        return {"aktif": bool(getattr(self, "_vacant", False)),
                "durasi": 0.0, "berlalu": 0.0, "sisa": 0.0}
    return o.vacancy.state()


def _vacancy_aktif(self):
    o = getattr(self, "_organik", None)
    aktif = bool(o is not None and o.vacancy.aktif)
    self._vacant = aktif
    return aktif


def _vacancy_lewat(self, dt=1.0):
    """Satu-satunya fisika vacancy: decay dasar dan akumulator waktu."""
    o = getattr(self, "_organik", None)
    if o is None or not o.vacancy.aktif:
        self._vacant = False
        return 0.0
    dipakai = o.vacancy.lewat(dt, tick=_naluri_tick(self))
    if dipakai > 0.0:
        factor = (1.0 - float(self.params.get("decay_per_tick", 0.0))) ** dipakai
        for drive in DRIVES:
            self.levels[drive] *= factor
        if bool(self.params.get("enable_emosi", False)):
            # Peluruhan emosi ini tidak mencatat event atau membangkitkan appraisal.
            self._emosi_peluruh(max(1, int(math.ceil(dipakai))))
    self._vacant = bool(o.vacancy.aktif)
    return dipakai


# ---------------- 10. INTRUSI: tidak melewati attend biasa ----------------
def _kesadaran_intrusi_spontan(self, paksa=False):
    n = getattr(self, "naluri", None)
    if n is None:
        return None
    # Tanpa residu, peluang harus benar-benar nol; jangan membuat Organik hanya
    # karena sebuah laporan workspace dibaca.
    o = (_naluri_organik(n) if paksa else getattr(n, "_organik", None))
    if o is None or (not paksa and o.residu.tekanan() <= 0.0):
        return None
    nu = getattr(n, "nurani", None)
    afektif = getattr(nu, "_affective", None) or {}
    if not afektif:
        return None
    try:
        arousal = float(n.mood().arousal)
    except Exception as _galat_diagnostik_203:
        _diag.catat('naluri._kesadaran_intrusi_spontan', "galat pada jalur fallback", galat=_galat_diagnostik_203, jalur=203)
        arousal = 0.0
    # Parameter bisa diubah setelah konstruksi (satu sumber kebenaran).
    o.intrusi.periode = max(1, int(n.params.get("intrusi_periode", 7)))
    o.intrusi.gain = max(0.0, float(n.params.get("intrusi_gain", 1.15)))
    entri = o.intrusi.coba(
        _naluri_tick(n), o.residu, arousal, afektif,
        spotlight=getattr(self, "spotlight", None),
        drives=getattr(n, "levels", None), rng=getattr(o, "rng", None),
        paksa=bool(paksa))
    if not entri:
        return None
    item = {"content": entri["content"], "salience": 0.92,
            "tag": "intrusi", "source": "tanpa_sebab", "kind": "intrusi",
            "tick": self._tick(), "detail": dict(entri),
            "datang_tanpa_sebab": True,
            "asal_diketahui": False}
    # Sengaja BUKAN submit() dan BUKAN attend(). Lantai kesadaran tetap bekerja
    # sebelum admission; jika lolos, intrusi langsung berada di workspace.
    if not self._lolos_lantai(item):
        return None
    self.workspace.append(item)
    if len(self.workspace) > 24:
        del self.workspace[:-24]
    return item


def paksa_intrusi(self):
    """Paksa satu kesempatan intrusi (alat skenario/uji, tetap sampel afektif)."""
    return self._intrusi_spontan(paksa=True)


def intrusi_state(self):
    o = getattr(self, "_organik", None)
    return {"jumlah": 0, "terakhir": None} if o is None else o.intrusi.state()




# ---------------- 11. DETAK INTERNAL: checkpoint sub-tick ----------------
def _detak_context(self):
    ks = getattr(self, "kesadaran", None)
    felt = getattr(ks, "felt", None) or {}
    grief = getattr(ks, "grief", None) or {}
    duka = max((float(x.get("intensity", 0.0)) for x in grief.values()),
               default=0.0)
    o = getattr(self, "_organik", None)
    return {"levels": getattr(self, "levels", {}) or {},
            "felt": felt, "emosi": getattr(self, "emosi", {}) or {},
            "spotlight": getattr(ks, "spotlight", None) or [],
            "duka": duka,
            "tekanan_residu": (o.residu.tekanan() if o is not None else 0.0)}


def _catat_interupsi(self, entri):
    item = {"tick": _naluri_tick(self), **dict(entri)}
    self._interupsi_internal.append(item)
    if len(self._interupsi_internal) > 64:
        self._interupsi_internal = self._interupsi_internal[-64:]
    return item


def _detak_checkpoint(self, dt=0.0, fase=""):
    o = _naluri_organik(self)
    if o is None:
        return []
    hasil = o.detak.maju(float(dt), _detak_context(self),
                          rng=getattr(o, "rng", None), fase=fase)
    keluar = []
    for mentah in hasil:
        entri = _catat_interupsi(self, mentah)
        proses = entri.get("proses")
        if proses == "mual":
            entri["langkah_dilewati"] = "introspeksi" if fase == "pasca_event" \
                else "fase_berikutnya"
            ks = getattr(self, "kesadaran", None)
            if ks is not None and hasattr(ks, "felt"):
                ks.felt["mual"] = min(1.0, max(
                    float(ks.felt.get("mual", 0.0)), 0.45))
        elif proses == "rindu":
            ks = getattr(self, "kesadaran", None)
            if ks is not None and ks.enabled("global_workspace"):
                item = {"content": "kenapa rasa rindu ini datang sekarang?",
                        "salience": 0.88, "tag": "rindu",
                        "source": "detak_internal", "kind": "interupsi",
                        "tick": _naluri_tick(self),
                        "detail": {"tanpa_keputusan": True}}
                # attend dipanggil ulang saat itu juga, bukan dijadwalkan.
                try:
                    ks.attend([item])
                    entri["attend_diulang"] = True
                except Exception as _galat_diagnostik_204:
                    _diag.catat('naluri._detak_checkpoint', "galat pada jalur fallback", galat=_galat_diagnostik_204, jalur=204)
                    entri["attend_diulang"] = False
        elif proses == "ingin_bicara":
            p = getattr(self, "presentasi", None)
            if p is not None and p.enabled():
                try:
                    ucapan = p.ucap(kepada=None, act="mengamati",
                                    diam_boleh=False)
                    if isinstance(ucapan, dict):
                        ucapan["dipicu_detak_internal"] = True
                        entri["ucapan"] = str(ucapan.get("teks", ""))[:100]
                except Exception as _galat_diagnostik_205:
                    _diag.catat('naluri._detak_checkpoint', "galat pada jalur fallback", galat=_galat_diagnostik_205, jalur=205)
                    entri["ucapan"] = ""
        keluar.append(entri)
    return keluar


def paksa_interupsi(self, proses):
    o = _naluri_organik(self)
    return False if o is None else o.detak.paksa(proses)


def detak_internal_state(self):
    o = getattr(self, "_organik", None)
    return {"jam": {}, "jumlah_interupsi": 0} if o is None else o.detak.state()


# ---------------- SELF MODEL: perilaku aktual boleh asing bagi diri ----------------
def _catat_selisih_self(self, prediksi, aktual, sebab=None):
    prediksi = prediksi or {}
    aktual = aktual or {}
    p_act, a_act = str(prediksi.get("act", "")), str(aktual.get("act", ""))
    p_teks, a_teks = str(prediksi.get("teks", "")), str(aktual.get("teks", ""))
    nilai = 0.0
    if p_act and a_act and p_act != a_act:
        nilai += 0.55
    if p_teks != a_teks:
        panjang = max(1, len(p_teks))
        nilai += min(0.35, abs(len(p_teks) - len(a_teks)) / panjang * 0.35)
        if p_teks and not a_teks:
            nilai += 0.10
    p_pros, a_pros = prediksi.get("prosodi") or {}, aktual.get("prosodi") or {}
    if p_pros and a_pros:
        volume_p = float(p_pros.get("volume", 0.0) or 0.0)
        volume_a = float(a_pros.get("volume", 0.0) or 0.0)
        nilai += min(0.10, abs(volume_p - volume_a) * 0.2)
    sebab = list(sebab or [])
    # Filter tersembunyi adalah deviasi kebijakan, bukan hanya edit-distance;
    # ujaran pendek tetap dapat sangat asing bagi diri yang memprediksinya.
    lantai = {"residu_duka": 0.28,
              "lapisan_paralel_bawah_sadar": 0.58,
              "konflik_di_bawah_gate": 0.52,
              "detak_mual": 0.42}
    nilai = max([nilai] + [lantai.get(x, 0.0) for x in sebab])
    nilai = jepit_01(nilai)
    self._selisih_self = nilai
    ambang = float(self.params.get("selisih_self_ambang", 0.18))
    if nilai >= ambang:
        self._selisih_self_beruntun += 1
    else:
        self._selisih_self_beruntun = 0
        self._disorientasi_identitas = max(
            0.0, self._disorientasi_identitas - 0.015)
    item = {"tick": _naluri_tick(self), "nilai": round(nilai, 4),
            "beruntun": self._selisih_self_beruntun,
            "prediksi": {"act": p_act, "panjang": len(p_teks)},
            "aktual": {"act": a_act, "panjang": len(a_teks)},
            "sebab_tersembunyi": list(sebab or [])}
    self._selisih_self_log.append(item)
    if len(self._selisih_self_log) > 64:
        self._selisih_self_log = self._selisih_self_log[-64:]
    ulang = max(2, int(self.params.get("selisih_self_ulang", 2)))
    if nilai >= ambang and self._selisih_self_beruntun >= ulang:
        kenaikan = min(0.2, 0.06 + 0.12 * nilai)
        self._disorientasi_identitas = min(
            1.0, self._disorientasi_identitas + kenaikan)
        ks = getattr(self, "kesadaran", None)
        if ks is not None:
            # Jalur ini sengaja tidak memanggil reality/prediction monitoring:
            # yang diragukan adalah diri sebagai agen konsisten.
            ks.doubt = min(1.0, float(getattr(ks, "doubt", 0.0)) + kenaikan)
            try:
                ks._refresh_identity({"tidak selalu mengenali diriku": kenaikan})
                ks.submit("aku tidak menyangka akan bertindak seperti itu",
                          salience=min(1.0, 0.55 + nilai * 0.35), tag="diri",
                          source="selisih_self", kind="disorientasi_identitas",
                          detail={"bukan_galat_pengetahuan": True})
            except Exception as _galat_diagnostik_206:
                _diag.catat('naluri._catat_selisih_self', "galat pada jalur fallback", galat=_galat_diagnostik_206, jalur=206)
                pass
        nu = getattr(self, "nurani", None)
        if nu is not None and hasattr(nu, "doubt_level"):
            nu.doubt_level = min(1.0, float(nu.doubt_level) + kenaikan)
        item["disorientasi_identitas"] = True
    return item


def selisih_self_state(self):
    return {"nilai": round(float(self._selisih_self), 4),
            "beruntun": int(self._selisih_self_beruntun),
            "disorientasi_identitas": round(
                float(self._disorientasi_identitas), 4),
            "terakhir": (dict(self._selisih_self_log[-1])
                         if self._selisih_self_log else None)}


def interupsi_internal_state(self):
    return {"jumlah": len(self._interupsi_internal),
            "terakhir": (dict(self._interupsi_internal[-1])
                         if self._interupsi_internal else None),
            "riwayat": [dict(x) for x in self._interupsi_internal[-8:]]}


# Presentasi aktual dapat diubah setelah kalimat terbentuk, sedangkan prediksi
# self-model tetap memegang rencana sebelum filter tersembunyi itu.
def _organik_lanjut_ucap(original, self, kepada=None, topik=None, *a, **k):
    ent = original(self, kepada, topik, *a, **k)
    if not isinstance(ent, dict) or not ent:
        return ent
    n = getattr(self, "naluri", None)
    if n is None:
        return ent
    prediksi = {"act": ent.get("act"),
                "teks": ent.get("teks_terbentuk", ent.get("teks", "")),
                "prosodi": dict(ent.get("prosodi") or {})}
    # Prediksi bukan pembacaan state aktual: ia memakai model_diri NURANI yang
    # tertinggal. Bila model tidak punya keyakinan kuat, rencana tutur normal
    # menjadi priornya.
    nu_model = getattr(n, "nurani", None)
    model_diri = dict(getattr(nu_model, "model_diri", None) or {})
    prediksi["model_diri"] = model_diri
    if float(model_diri.get("keamanan", 0.0) or 0.0) < -0.45:
        prediksi["act"] = "waspada"
    elif float(model_diri.get("koherensi", 0.0) or 0.0) < -0.45:
        prediksi["act"] = "ragu"
    elif (float(model_diri.get("afiliasi", 0.0) or 0.0) > 0.45
          and kepada is not None):
        prediksi["act"] = "akrab"
    sebab = []
    o = getattr(n, "_organik", None)
    # (a) Duka memendekkan ujaran akrab tanpa mengubah keyakinan self-model
    # bahwa ia sedang berbicara seperti biasa.
    tekanan_duka = 0.0
    if o is not None:
        tekanan_duka = max(o.residu.tekanan_target("duka"),
                            o.residu.tekanan_target("sedih"))
    label = "netral"
    try:
        label = self._label_rel(kepada) if kepada is not None else "netral"
    except Exception as _galat_diagnostik_207:
        _diag.catat('naluri._organik_lanjut_ucap', "galat pada jalur fallback", galat=_galat_diagnostik_207, jalur=207)
        pass
    akrab = ent.get("act") == "akrab" or label in ("suka", "percaya", "akrab")
    if tekanan_duka >= 0.55 and akrab and ent.get("teks"):
        kata = str(ent["teks"]).split()
        batas = max(3, int(round(9 - 5 * tekanan_duka)))
        if len(kata) > batas:
            ent["teks"] = " ".join(kata[:batas]).rstrip(".,;:") + "…"
        pros = dict(ent.get("prosodi") or {})
        if "volume" in pros:
            pros["volume"] = max(0.0, float(pros["volume"]) *
                                  (1.0 - 0.35 * tekanan_duka))
        pros["kontur"] = "datar"
        ent["prosodi"] = pros
        ent["tersaring_tanpa_disadari"] = "residu_duka"
        sebab.append("residu_duka")
    # (b) Arousal ekstrem membuka lapisan yang tak dilacak model utama.
    if o is not None and o.paralel.tanpa_resolusi():
        try:
            aro = float(n.mood().arousal)
        except Exception as _galat_diagnostik_208:
            _diag.catat('naluri._organik_lanjut_ucap', "galat pada jalur fallback", galat=_galat_diagnostik_208, jalur=208)
            aro = 0.0
        if aro >= 0.72 and o.paralel._lapisan:
            utama = o.paralel._lapisan[0]
            em_utama = utama.get("emosi") or {}
            # Model diri tetap memprediksi lapisan utama.
            if float(em_utama.get("marah", 0.0) or 0.0) > 0:
                prediksi["act"] = "menantang"
            elif float(em_utama.get("takut", 0.0) or 0.0) > 0:
                prediksi["act"] = "waspada"
            elif (float(em_utama.get("senang", 0.0) or 0.0) > 0 or
                  float(em_utama.get("afiliasi", 0.0) or 0.0) > 0):
                prediksi["act"] = "akrab"
            lap = o.paralel._lapisan[-1]
            em = lap.get("emosi") or {}
            if float(em.get("marah", 0.0) or 0.0) > 0:
                act_bawah = "menantang"
            elif float(em.get("takut", 0.0) or 0.0) > 0:
                act_bawah = "waspada"
            elif (float(em.get("senang", 0.0) or 0.0) > 0 or
                  float(em.get("afiliasi", 0.0) or 0.0) > 0):
                act_bawah = "akrab"
            else:
                act_bawah = "menolak"
            if act_bawah != ent.get("act"):
                ent["act"] = act_bawah
                ent["lapisan_bawah_sadar"] = int(lap.get("id", 0))
                sebab.append("lapisan_paralel_bawah_sadar")
    # (c) Goal yang sama-sama berada di bawah conflict gate dapat flip-flop
    # tanpa pernah masuk detektor konflik sadar.
    goals = list(getattr(n, "goals", None) or [])
    if len(goals) >= 2:
        gate = 0.3
        nu = getattr(n, "nurani", None)
        if nu is not None:
            try:
                gate = float(nu._p("conflict_urgency_gate"))
            except Exception as _galat_diagnostik_209:
                _diag.catat('naluri._organik_lanjut_ucap', "galat pada jalur fallback", galat=_galat_diagnostik_209, jalur=209)
                pass
        urg = [float(getattr(g, "urgency", 0.0) or 0.0) for g in goals[:2]]
        drives = [str(getattr(g, "drive", "")) for g in goals[:2]]
        if max(urg, default=0.0) <= gate and len(set(drives)) > 1:
            flip = "ragu" if len(getattr(self, "_history", [])) % 2 else "menyatakan"
            if flip != ent.get("act"):
                ent["act"] = flip
                ent["konflik_tak_terdeteksi"] = drives
                sebab.append("konflik_di_bawah_gate")
    # Ujaran sendiri memakan waktu fraksional. Mual dapat jatuh tempo di tengah
    # artikulasi dan memotong teks sekarang juga.
    if o is not None and ent.get("teks"):
        durasi = min(0.55, 0.04 + len(str(ent["teks"]).split()) / 80.0)
        jatuh = o.detak.maju(durasi, _detak_context(n),
                             rng=getattr(o, "rng", None), fase="di_tengah_ucap")
        for ev in jatuh:
            cat = _catat_interupsi(n, ev)
            if ev.get("proses") == "mual":
                teks = str(ent.get("teks", ""))
                potong = max(1, len(teks) // 2)
                ent["teks_sebelum_interupsi"] = teks
                ent["teks"] = teks[:potong].rstrip() + "—"
                ent["terpotong_internal"] = "mual"
                sebab.append("detak_mual")
                cat["ucapan_dipotong"] = True
                break
    if sebab:
        ent["deviasi_self"] = list(sebab)
    ent["prediksi_self"] = {"act": prediksi.get("act"),
                             "panjang": len(str(prediksi.get("teks", ""))),
                             "berdasarkan_model_diri": True}
    info = _catat_selisih_self(n, prediksi, ent, sebab)
    ent["selisih_self"] = round(float(info.get("nilai", 0.0)), 4)
    # Implementasi ucap lama sudah menulis salinan ke history. Sinkronkan hasil
    # final agar "perilaku aktual" di log benar-benar yang terlihat pemain.
    hist = getattr(self, "_history", None)
    if hist and int(hist[-1].get("tick", -1)) == int(ent.get("tick", -2)):
        hist[-1] = dict(ent)
    return ent




# ---------------- 5. KOHERENSI: kontradiksi paralel yang disadari aman ----------------
def _organik_hold_belief(original, self, keyakinan, bukti, kekuatan=0.6,
                          bertentangan=True):
    n = getattr(self, "naluri", None)
    o = getattr(n, "_organik", None) if n is not None else None
    sadar_paralel = bool(bertentangan and o is not None
                          and o.paralel.tanpa_resolusi())
    hasil = original(
        self, keyakinan, bukti, kekuatan,
        bertentangan=False if sadar_paralel else bertentangan)
    if sadar_paralel and isinstance(hasil, dict):
        slot = self.dissonance.get(str(keyakinan)[:80])
        if slot is not None:
            slot["disadari_sebagai_paralel"] = True
            slot["tension"] = 0.0
        hasil = dict(slot or hasil)
        hasil["tanpa_resolusi"] = True
        hasil["koherensi_dihukum"] = False
    elif bertentangan and isinstance(hasil, dict) and hasil and n is not None:
        # Yang tidak dikenali sebagai lapisan tetap menekan koherensi.
        try:
            n.delta("koherensi", -0.04 * jepit_01(float(kekuatan)),
                    reason="kontradiksi tak disadari")
            hasil = dict(hasil)
            hasil["koherensi_dihukum"] = True
        except Exception as _galat_diagnostik_210:
            _diag.catat('naluri._organik_hold_belief', "galat pada jalur fallback", galat=_galat_diagnostik_210, jalur=210)
            pass
    return hasil






# >>> ORGANIK-BLOCK-END (naluri) <<<

def pasang(Naluri: type) -> None:
    """Pasang patch dengan urutan dan ID historis."""
    for _nama, _fn in (("daftarkan_slot", daftarkan_slot),
                       ("kosongkan_slot", kosongkan_slot),
                       ("isi_ulang_slot", isi_ulang_slot),
                       ("slot_terisi", slot_terisi),
                       ("intensitas_topologis", intensitas_topologis),
                       ("layak_cabang", layak_cabang),
                       ("duka", duka),
                       ("kehilangan_state", kehilangan_state),
                       ("cabang_mustahil", cabang_mustahil),
                       ("tetapkan_identitas", tetapkan_identitas),
                       ("batas_identitas_state", batas_identitas_state),
                       ("emosi_ditolak", emosi_ditolak),
                       ("tandai_stimulus_bertentangan", tandai_stimulus_bertentangan),
                       ("organik_state", organik_state)):
        install_method(Naluri, _nama, _fn,
                       patch_id="naluri.extension.Naluri." + _nama)

    wrap_method(Naluri, "_emosi_naikkan", _organik_emosi_naikkan,
                patch_id="naluri.organik.emosi")

    _organik_bungkus_serialisasi(Naluri, _naluri_organik_ambil, _naluri_organik_pasang)

    wrap_method(Kesadaran, "future_simulation", _organik_future_simulation,
                patch_id="naluri.organik.future_simulation")

    wrap_method(Presentasi, "ucap", _organik_ucap,
                patch_id="naluri.organik.penolakan_tutur")

    install_methods(
        Presentasi,
        (("kelayakan_tutur", kelayakan_tutur),
         ("penolakan_state", penolakan_state)),
        patch_id="naluri.organik.presentasi_api",
    )

    for _nama, _fn in (("apersepsi_state", apersepsi_state),
                       ("rasa_kabut", rasa_kabut),
                       ("felt_report_jujur", _organik_felt_report_jujur),
                       ("pegang_dua", pegang_dua),
                       ("pegang_keyakinan", pegang_keyakinan),
                       ("keyakinan_paralel", keyakinan_paralel),
                       ("pengaruh_paralel", pengaruh_paralel),
                       ("tanpa_resolusi", tanpa_resolusi),
                       ("bertindak_dari_lapisan", bertindak_dari_lapisan),
                       ("tubuh_state", tubuh_state),
                       ("suntik_tubuh", suntik_tubuh),
                       ("auto_deteksi_slot", auto_deteksi_slot)):
        install_method(Naluri, _nama, _fn,
                       patch_id="naluri.extension.Naluri." + _nama)

    install_methods(
        Kesadaran,
        (("_intrusi_spontan", _kesadaran_intrusi_spontan),
         ("paksa_intrusi", paksa_intrusi),
         ("intrusi_state", intrusi_state)),
        patch_id="naluri.organik.intrusi_api",
    )

    wrap_method(Presentasi, "ucap", _organik_lanjut_ucap,
                patch_id="naluri.organik.self_model_tutur")

    wrap_method(Kesadaran, "hold_belief", _organik_hold_belief,
                patch_id="naluri.organik.hold_belief")

    for _nama, _fn in (("daftarkan_residu", daftarkan_residu),
                       ("register_residue", daftarkan_residu),
                       ("tambal_residu", tambal_residu),
                       ("ambang_dimodifikasi", ambang_dimodifikasi),
                       ("langit_dimodifikasi", langit_dimodifikasi),
                       ("residu_state", residu_state),
                       ("mulai_vacancy", mulai_vacancy),
                       ("enter_vacancy", mulai_vacancy),
                       ("vacancy_state", vacancy_state),
                       ("_vacancy_aktif", _vacancy_aktif),
                       ("_vacancy_lewat", _vacancy_lewat),
                       ("_detak_checkpoint", _detak_checkpoint),
                       ("paksa_interupsi", paksa_interupsi),
                       ("detak_internal_state", detak_internal_state),
                       ("selisih_self_state", selisih_self_state),
                       ("interupsi_internal_state", interupsi_internal_state)):
        install_method(Naluri, _nama, _fn,
                       patch_id="naluri.extension.Naluri." + _nama)

    wrap_method(Naluri, "tick", _organik_tick,
                patch_id="naluri.organik.tick")

    wrap_method(Kesadaran, "hud_state", _organik_hud_state,
                patch_id="naluri.organik.hud_state")

