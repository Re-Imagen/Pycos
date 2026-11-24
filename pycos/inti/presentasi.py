"""Implementasi Presentasi; jalur publik lama tetap inti.naluri."""
from __future__ import annotations

import copy
import os
import random
import re
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple
from pycos.dukungan import diagnostik as _diag
from pycos.dukungan.numerik import jepit, jepit_01
from pycos.dukungan.sumber import kandidat_leksikon
from pycos.inti._konfigurasi import (_kclip)

PRESENTASI_DEFAULTS: Dict[str, Any] = {
    "enable_presentasi": False,
    "presentasi_intensitas": 0.7,   # pengali ekspresivitas global [0..1.5]
    "presentasi_variasi": 0.35,     # keragaman pilihan kata [0..1]
    "presentasi_verbositas": 1.0,   # pengali panjang ujaran
    "presentasi_bisukan": 0.0,      # peluang memilih diam
    "presentasi_gestur": True,
    "presentasi_prosodi": True,
    "presentasi_tatapan": True,
    "presentasi_microexpression": True,
    "presentasi_idle": True,
    "presentasi_riwayat_max": 64,
    "presentasi_bosan_ambang": 0.58,
    # D8: ujaran yang didengar ikut menggerakkan keadaan batin (bukan
    # sekadar dicatat). `presentasi_dengar_efek` mematikan efek bila perlu.
    "presentasi_dengar_efek": True,
    "presentasi_dengar_efek_gain": 0.12,
    "presentasi_bosan_gain": 0.12,
    "presentasi_bosan_pulih": 0.34,
    "presentasi_bosan_riwayat_max": 16,
    "presentasi_jarak_dasar": 0.5,
    # kesadaran temporal: ambang jeda & lama absen (dalam tick)
    "presentasi_idle_ticks": 30,       # Player diam di depan NPC > ini → proaktif
    "presentasi_absence_ticks": 60,    # absen > ini → sambutan "kamu kembali"
    "presentasi_proaktif": True,        # izinkan dialog proaktif
    # indikator psikologis (UI/UX): ambang label
    "presentasi_ketenangan_titik": 0.5,
    # TELLS: kebocoran personal yang bisa dipelajari pemain (tak pernah diumumkan)
    "presentasi_tell": True,
    "presentasi_tell_ambang": 0.45,   # defisit drive "beku" yang memicu tell
    # DIAM YANG BERMAKNA: hesitasi sebagai state (bukan delay acak)
    "presentasi_hesitasi": True,      # sakelar fitur hesitasi
    "presentasi_hesitasi_ticks": 3,   # jendela deteksi "pending shift"
    # LINGER (histeresis): ekspresi punya momentum, bukan snapshot
    "presentasi_emosi_linger": 0.15,  # 0=instan, 1=tak pernah berubah
    "presentasi_postur_linger": 0.10,
    "presentasi_tatapan_linger": 0.12,
    # TUTUR GENERATIF (L0–L3): ujaran dibangkitkan dari leksikon + biografi,
    # bukan dari template hardcoded. Otomatis mati bila mesin/leksikon absen.
    "presentasi_generatif": True,
    "presentasi_leksikon": "",      # path eksplisit (opsional)
    "presentasi_trace": False,       # sertakan trace L0–L3 di keluaran ucap()
    # SISTEM II — LAPISAN PELINDUNG ILUSI. Mati bawaan (kompatibel mundur): ia
    # hanya mengubah CARA gagal & jeda, tidak menambah angka ke keputusan lama.
    "enable_pelindung": False,
    "pelindung_jeda_dasar_ms": 180,      # jeda minimum yang selalu ada
    "pelindung_jeda_maks_ms": 2200,
    "pelindung_jeda_bobot_konflik": 520,  # konflik internal
    "pelindung_jeda_bobot_ragu": 420,     # keraguan
    "pelindung_jeda_bobot_arousal": 260,
    "pelindung_jeda_bobot_baru": 480,     # kebaruan input (kosakata asing)
    "pelindung_jeda_bobot_jarak": 300,    # lama sejak interaksi terakhir
    "pelindung_jeda_kuantisasi_ms": 25,   # dapat dipelajari Player (tidak acak)
    "pelindung_anggaran_leksikal": 2,     # kebaruan per tingkat (Eskalasi Variasi)
    "pelindung_anggaran_sintaksis": 2,
    "pelindung_anggaran_semantik": 2,
    "pelindung_anggaran_pragmatis": 2,
    "pelindung_ulang_leksikal": 0.55,     # ambang tumpang tindih kata
    "pelindung_ulang_semantik": 0.72,
    "pelindung_buffer_tak_paham": True,   # tampilkan kegagalan yang manusiawi
    "pelindung_buffer_lupa": True,
    "pelindung_buffer_kontradiksi": True,
    "pelindung_degradasi_skala_sesi": 900,  # tick "sesi panjang" (≈menit)
    "pelindung_degradasi_ucap_ulang": 40,   # cooldown kalimat istirahat
    "pelindung_monitor_periode": 24,        # Monitor Integritas berjalan tiap N tick
    "pelindung_keragaman_ambang": 2,        # penanda sama pada ≥ N NPC → digeser
}

# Satu sumber kebenaran: parameter presentasi dilebur ke dict params Naluri.




# E5: pengetahuan tentang bentuk/fungsi tindak tutur yang tersedia — BUKAN
# planner yang menciptakan isi. Setiap act memetakan: fungsi ilokusi; sumber
# isi yang BOLEH dipakainya (keadaan Pycos yang terbentuk lebih dulu).
# Penambahan act di sini tidak boleh menjadi penambahan alasan/isi batin
# lewat tabel templat: bila isi tidak terbentuk, larik dialog menutup
# (diam), bukan mengarang. Sinkron dengan L0 (pycos/bahasa/tutur.py).
_ACT_FUNGSI = {
    "menyatakan":      ("menyatakan pikiran/sikap yang terbentuk", "keadaan"),
    "menjawab":        ("menjawab dari sumber relevan (keadaan/memori/relasi)", "keadaan+memori"),
    "bertanya":        ("bertanya yang muncul dari keingintahuan/keraguan", "keadaan+epistemik"),
    "mengamati":       ("menyebut pengamatan atas spotlight yang ada", "keadaan+perhatian"),
    "menolak":         ("penolakan yang muncul dari batas/nilai", "keadaan+nilai"),
    "akrab":           ("keakraban yang muncul dari relasi/perasaan", "keadaan+relasi"),
    "menantang":       ("menantang yang muncul dari marah/curiga", "keadaan+emosi"),
    "menegur":         ("menegur yang muncul dari marah/keprihatinan", "keadaan+emosi+relasi"),
    "peringatan":      ("memperingatkan yang muncul dari takut/peduli", "keadaan+emosi+relasi"),
    "ragu":            ("keraguan yang muncul dari ketidakpastian", "keadaan+epistemik"),
    "waspada":         ("kewaspadaan yang muncul dari takut", "keadaan+emosi"),
    "mengenang":       ("mengenang episode yang benar-benar ada", "keadaan+memori"),
    "eksistensial":    ("kesadaran eksistensial yang muncul dari keadaan", "keadaan+mortalitas"),
    "rasionalisasi":   ("katahati atas disonansi yang ada", "keadaan+disonansi"),
    "mimpi":           ("isi mimpi yang terbentuk saat lelah", "keadaan+memori+kelelahan"),
    "menimbang":       ("jeda berpikir sebelum bertutur", "keadaan"),
    "kembali":         ("sapaan balik atas kembalinya lawan (situasi)", "situasi+relasi"),
    "menyapa_proaktif": ("menyapa lebih dulu (situasi diam)", "situasi+relasi"),
    "diam":            ("diam bermakna — tanpa teks", "keadaan"),
}

def _skema_act(act: str) -> Dict[str, str]:
    """E5: bentuk/fungsi act sebagai pengetahuan; kosong bila tidak dikenal."""
    ent = _ACT_FUNGSI.get(str(act or "").strip().lower())
    if ent is None:
        return {}
    fungsi, sumber = ent
    return {"fungsi": fungsi, "sumber_isi": sumber}


class Presentasi:
    """Penyaji perilaku Pycos: dari angka internal → adegan yang terbaca.

    Alur khas pemakaian:
        p = naluri.presentasi                 # dibuat otomatis oleh Naluri
        p.set_jejak(jejak)                    # opsional: memori autobiografis
        beat = p.adegan(kepada="Player")      # satu "denyut" perilaku
        print(beat["deskripsi"])              # narasi pengamat
        ucap = p.ucap(kepada="Player", topik="api")  # hanya dialog
        p.dengar("kenapa kamu menjauh?", "Player")
        balas = p.balas("Player")
    """

    # ==================================================================
    # konstruksi
    # ==================================================================
    def __init__(self, naluri: Any, params: Optional[Dict[str, Any]] = None,
                 jejak: Any = None) -> None:
        self.naluri = naluri
        self.jejak = jejak
        self.params: Dict[str, Any] = (params if params is not None
                                       else copy.deepcopy(PRESENTASI_DEFAULTS))
        # RNG Khusus presentasi: TIDAK memakai self.naluri._rng agar variasi
        # kata tidak mengganggu determinisme simulai (mimpi, persepsi, dsb.).
        self._rng = random.Random(self._seed_for(naluri))
        # state kontinu (dibaca pemain sebagai "gerak hidup", bukan angka)
        self._gaze: Optional[str] = None
        self._posture: str = "netral"
        self._breath_phase: float = 0.0
        self._breath_rate: float = 0.5
        self._blink_in: float = 3.0
        self._micro: Optional[str] = None
        self._micro_ttl: float = 0.0
        self._fidget: float = 0.0
        self._silence: float = 0.0
        self._last_act: Optional[str] = None
        self._act_counts: Dict[str, int] = {}
        self._history: List[Dict[str, Any]] = []
        self._pending_topic: Optional[str] = None
        self._pending_speaker: Optional[str] = None
        self._ucapan_terakhir: Optional[str] = None
        self._mood_carry: float = 0.0
        self._recent_texts: List[str] = []
        # --- kesadaran temporal (konsep 4) ---
        self._player_present: bool = False
        self._idle_ticks: float = 0.0
        self._absence_ticks: float = 0.0
        self._last_seen_tick: int = -10_000
        self._returned: bool = False
        self._proaktif_terakhir: int = -10_000
        # --- kesalahan terkendali (konsep 5) ---
        self._ragu_berubah: bool = False
        self._salah_ingat: Optional[Dict[str, Any]] = None
        # --- TELLS (kebocoran personal) ---
        self._tell: Optional[Dict[str, Any]] = None
        # --- DIAM YANG BERMAKNA (hesitasi sebagai state) ---
        self._pending_shift: Optional[Dict[str, Any]] = None
        self._shift_dipakai: bool = False
        self._last_spotlight: Optional[str] = None
        self._last_conflict: int = 0
        self._hesitasi_terakhir: Optional[Dict[str, Any]] = None
        self._shift_seen_tick: int = -10_000
        self._last_spot_check_tick: int = -1
        # --- PRONOMINA KONSISTEN (F1): satu pasangan (diri, lawan)
        # per mitra bicara, dipilih dari register persona (atau relasi);
        # tidak pernah campuran "kau/kamu" dalam satu ujaran. ---
        self._pronomina_per_mitra: Dict[str, Tuple[str, str]] = {}
        # --- LINGER (histeresis per kanal) ---
        self._histeresis: Dict[str, float] = {}
        # --- TUTUR GENERATIF (L0–L3) ---
        self._tutur: Any = None
        self._tutur_dimuat: bool = False
        self._tutur_trace: List[Dict[str, Any]] = []
        self._sa_sp_analyzer: Any = None
        self._sa_sp_last: Optional[Dict[str, Any]] = None
        self._boredom: float = 0.0
        self._boredom_action_index: int = 0
        self._boredom_recent: List[str] = []
        self._boredom_log: List[Dict[str, Any]] = []

    @staticmethod
    def _seed_for(naluri: Any) -> int:
        """Seed deterministik dari nama NPC (stabil lintas proses)."""
        nama = str(getattr(naluri, "name", "") or "")
        seed = 7919
        for i, ch in enumerate(nama):
            seed = (seed * 131 + ord(ch) * (i + 1)) & 0x7FFFFFFF
        return seed

    # ==================================================================
    # sakelar & util
    # ==================================================================
    def enabled(self, channel: Optional[str] = None) -> bool:
        if not bool(self.params.get("enable_presentasi", False)):
            return False
        if channel is None:
            return True
        return bool(self.params.get("presentasi_" + channel, True))

    def _p(self, key: str) -> float:
        v = self.params.get(key, PRESENTASI_DEFAULTS.get(key, 0.0))
        if isinstance(v, Mapping):
            v = v.get("*", PRESENTASI_DEFAULTS.get(key, 0.0))
        try:
            return float(v)
        except (TypeError, ValueError):
            return float(PRESENTASI_DEFAULTS.get(key, 0.0))

    def _tick(self) -> int:
        return int(getattr(self.naluri, "tick_count", 0))

    def _eid(self, ent: Any) -> str:
        if ent is None:
            return ""
        return str(getattr(ent, "name", ent))

    def _pick(self, options: Sequence[str], fallback: str = "") -> str:
        if not options:
            return fallback
        try:
            return self._rng.choice(list(options))
        except Exception as _galat_diagnostik_37:
            _diag.catat('naluri.Presentasi._pick', "galat pada jalur fallback", galat=_galat_diagnostik_37, jalur=37)
            return options[0]

    def _lev(self, drive: str) -> float:
        try:
            return float((getattr(self.naluri, "levels", {}) or {}).get(drive, 0.0))
        except Exception as _galat_diagnostik_38:
            _diag.catat('naluri.Presentasi._lev', "galat pada jalur fallback", galat=_galat_diagnostik_38, jalur=38)
            return 0.0

    def _emosi(self, name: str) -> float:
        try:
            return float((getattr(self.naluri, "emosi", {}) or {}).get(name, 0.0))
        except Exception as _galat_diagnostik_39:
            _diag.catat('naluri.Presentasi._emosi', "galat pada jalur fallback", galat=_galat_diagnostik_39, jalur=39)
            return 0.0

    def _epistemik(self, name: str) -> float:
        ks = self._kes()
        try:
            return float((getattr(ks, "epistemic_emotions", {}) or {}).get(name, 0.0))
        except Exception as _galat_diagnostik_40:
            _diag.catat('naluri.Presentasi._epistemik', "galat pada jalur fallback", galat=_galat_diagnostik_40, jalur=40)
            return 0.0

    def _kes(self) -> Any:
        return getattr(self.naluri, "kesadaran", None)

    def _nur(self) -> Any:
        return getattr(self.naluri, "nurani", None)

    def _rel(self, ent: Any) -> Dict[str, Any]:
        fn = getattr(self.naluri, "relasi", None)
        if callable(fn) and ent is not None:
            try:
                return dict(fn(ent))
            except Exception as _galat_diagnostik_41:
                _diag.catat('naluri.Presentasi._rel', "galat pada jalur fallback", galat=_galat_diagnostik_41, jalur=41)
                return {}
        return {}

    def _label_rel(self, ent: Any) -> str:
        fn = getattr(self.naluri, "label_relasi", None)
        label = "netral"
        if callable(fn) and ent is not None:
            try:
                label = str(fn(ent))
            except Exception as _galat_diagnostik_42:
                _diag.catat('naluri.Presentasi._label_rel', "galat pada jalur fallback", galat=_galat_diagnostik_42, jalur=42)
                label = "netral"
        ks = self._kes()
        if ks is not None and ent is not None:
            try:
                tension = float(ks.withholding_relationship_tension(ent))
                # Penahanan berulang membuat keakraban/kepercayaan terasa lebih
                # rapuh; efeknya terkumpul, tidak menghapus relasi satu kali.
                if tension >= 0.28 and label in ("percaya", "suka", "akrab"):
                    return "netral"
                if tension >= 0.12 and label == "percaya":
                    return "akrab"
            except Exception as _galat_diagnostik_43:
                _diag.catat('naluri.Presentasi._label_rel', "galat pada jalur fallback", galat=_galat_diagnostik_43, jalur=43)
                pass
        return label

    def set_jejak(self, jejak: Any) -> "Presentasi":
        """Sambungkan memori autobiografis JEJAK agar bisa dikisahkan."""
        self.jejak = jejak
        return self

    # ==================================================================
    # TUTUR GENERATIF (L0–L3) — jembatan ke mesin tutur + leksikon
    # ==================================================================
    def set_leksikon(self, path: str) -> bool:
        """Muat leksikon eksternal secara eksplisit (opsional)."""
        self.params["presentasi_leksikon"] = str(path)
        self._tutur = None
        self._tutur_dimuat = False
        return self.tutur_engine() is not None

    def tutur_engine(self) -> Any:
        """Muat mesin tutur + leksikon sekali saja (lazy). None bila absen."""
        from pycos.inti.naluri import TuturEngine
        if self._tutur_dimuat:
            return self._tutur
        self._tutur_dimuat = True
        if TuturEngine is None or not bool(
                self.params.get("presentasi_generatif", True)):
            return None
        try:  # __file__ absen bila source dieksekusi lewat exec()/repl
            di_sini = os.path.dirname(os.path.abspath(__file__))
        except NameError:
            di_sini = ""
        # Prioritas: path eksplisit pada parameter, berkas di samping modul
        # ini, sumber daya paket (pycos/sumber_daya), lalu direktori kerja.
        kandidat: List[str] = kandidat_leksikon(
            ekplisit=str(self.params.get("presentasi_leksikon") or ""),
            sekitar=di_sini or None,
        )
        for p in kandidat:
            try:
                if p and os.path.exists(p):
                    eng = TuturEngine(p)
                    if eng.tersedia():
                        self._tutur = eng
                        break
            except Exception as galat:
                # Kandidat rusak tidak menghentikan pencarian, tetapi kegagalannya
                # dicatat agar jalur template yang dipakai tidak tampak "normal".
                _diag.catat("Presentasi.tutur_engine",
                            "leksikon kandidat gagal dimuat",
                            jalur=p, galat=type(galat).__name__)
                continue
        if self._tutur is None:
            _diag.catat("Presentasi.tutur_engine",
                        "tidak ada leksikon yang dapat dimuat; jalur template dipakai",
                        kandidat=len(kandidat))
        return self._tutur

    def analisis_sa_sp(self, ujaran: Any, konteks: Any = None,
                       speaker: Any = None, update_state: bool = True
                       ) -> Dict[str, Any]:
        """Analisis ujaran melalui SA_SP, tanpa menganggap maksud sebagai fakta."""
        from pycos.inti.naluri import SASPAnalyzer
        if not bool(self.params.get("enable_sa_sp", True)):
            return {"aktif": False, "alasan": "sa_sp dinonaktifkan"}
        ks = self._kes()
        if update_state and ks is not None and getattr(ks, "enabled", lambda *_: False)("sa_sp"):
            try:
                hasil = ks.analisis_sa_sp(ujaran, konteks=konteks, speaker=speaker)
                if hasil.get("aktif") is not False:
                    self._sa_sp_last = copy.deepcopy(hasil)
                    return hasil
            except Exception as _galat_diagnostik_45:
                _diag.catat('naluri.Presentasi.analisis_sa_sp', "galat pada jalur fallback", galat=_galat_diagnostik_45, jalur=45)
                pass
        engine = self.tutur_engine()
        try:
            if engine is not None and hasattr(engine, "analisis_sa_sp"):
                hasil = engine.analisis_sa_sp(ujaran, konteks)
            else:
                if SASPAnalyzer is None:
                    return {"aktif": False, "alasan": "analyzer sa_sp tidak tersedia"}
                if self._sa_sp_analyzer is None:
                    leks = getattr(engine, "leks", None) if engine is not None else None
                    self._sa_sp_analyzer = SASPAnalyzer(leksikon=leks)
                hasil = self._sa_sp_analyzer.analisis(ujaran, konteks)
            if update_state and ks is not None:
                try:
                    ks.observe_sa_sp(hasil, speaker=speaker)
                except Exception as _galat_diagnostik_46:
                    _diag.catat('naluri.Presentasi.analisis_sa_sp', "galat pada jalur fallback", galat=_galat_diagnostik_46, jalur=46)
                    pass
            self._sa_sp_last = copy.deepcopy(hasil)
            return hasil
        except Exception as exc:
            _diag.catat('naluri.Presentasi.analisis_sa_sp', "galat pada jalur fallback", galat=exc, jalur=47)
            return {"aktif": False, "alasan": f"gagal menganalisis: {type(exc).__name__}"}

    analyze_sa_sp = analisis_sa_sp

    def _generatif(self, act: str, kepada: Any, topik: Optional[str],
                   masuk: bool = False, coba: int = 0) -> Optional[str]:
        """Coba hasilkan ujaran dari mesin tutur; None bila gagal/absen.

        `coba` menggeser seed tiap percobaan agar loop anti-pengulangan di
        `ucap()` benar-benar menemukan variasi (bukan hasil identik).
        """
        from pycos.inti.naluri import konteks_dari_presentasi
        eng = self.tutur_engine()
        if eng is None or konteks_dari_presentasi is None:
            return None
        try:
            ctx = konteks_dari_presentasi(self, act, kepada, topik, masuk,
                                          seed_offset=coba)
            t = eng.ucap(ctx)
        except Exception as _galat_diagnostik_48:
            _diag.catat('naluri.Presentasi._generatif', "galat pada jalur fallback", galat=_galat_diagnostik_48, jalur=48)
            return None
        if t is None or t.status != "SUKSES" or not t.teks.strip():
            return None
        self._tutur_trace = t.trace
        return t.teks.strip()

    # ==================================================================
    # kontinu — denyut presentasi tiap tick
    # ==================================================================
    def tick(self, steps: int = 1) -> None:
        """Perbarui gerak mikro (napas, kedip, fidget, mikro-ekspresi)."""
        if not self.enabled():
            return
        steps = max(1, int(steps))
        # napas mengikuti arousal + sensasi jantung/takut
        arousal = 0.0
        try:
            arousal = float(getattr(self.naluri.mood(), "arousal", 0.0))
        except Exception as _galat_diagnostik_49:
            _diag.catat('naluri.Presentasi.tick', "galat pada jalur fallback", galat=_galat_diagnostik_49, jalur=49)
            arousal = 0.0
        jantung = self._felt("jantung")
        takut = self._emosi("takut")
        target_rate = 0.4 + 0.5 * max(0.0, arousal) + 0.4 * max(takut, jantung)
        self._breath_rate = self._lerp(self._breath_rate, target_rate, 0.12)
        self._breath_phase = (self._breath_phase + self._breath_rate * 0.25 * steps) % 1.0
        # kedip
        self._blink_in -= 0.4 * steps
        if self._blink_in <= 0:
            self._blink_in = 2.0 + 4.0 * (1.0 - min(1.0, arousal))
        # mikro-ekspresi bocor lalu mereda
        if self._micro_ttl > 0:
            self._micro_ttl -= steps
            if self._micro_ttl <= 0:
                self._micro = None
        # fidget mereda
        self._fidget = max(0.0, self._fidget - 0.05 * steps)
        self._silence += steps
        self._mood_carry *= 0.98 ** steps
        # --- kesadaran temporal (konsep 4) ---
        if self._player_present:
            self._idle_ticks += steps
            self._absence_ticks = 0.0
        else:
            self._absence_ticks += steps

    # ==================================================================
    # KESADARAN TEMPORAL (konsep 4)
    # ==================================================================
    def lihat_player(self, present: bool = True) -> Dict[str, Any]:
        """Beri tahu presentasi bahwa Player hadir/tidak (dipanggil game).

        Transisi absen→hadir setelah `presentasi_absence_ticks` menandai
        `_returned`, yang memicu sapaan "kamu kembali" pada `proaktif()`.
        """
        if not self.enabled():
            return {}
        sebelumnya = self._player_present
        self._player_present = bool(present)
        if present:
            if not sebelumnya and self._absence_ticks >= self._p("presentasi_absence_ticks"):
                self._returned = True
            self._absence_ticks = 0.0
            self._idle_ticks = 0.0
            self._last_seen_tick = self._tick()
        return {"hadir": self._player_present,
                "kembali": self._returned,
                "absen_ticks": int(self._absence_ticks)}

    def proaktif(self, kepada: Any = None) -> Dict[str, Any]:
        """Dialog yang dipicu KEADAAN (bukan input Player) — konsep 4.

        * Player kembali setelah absen lama → sapaan + referensi `life_chapters`.
        * Player diam > `presentasi_idle_ticks` → menyapa/bertanya pelan.
        Kembalikan {} bila belum waktunya.
        """
        if not self.enabled() or not bool(self.params.get("presentasi_proaktif", True)):
            return {}
        now = self._tick()
        if self._returned:
            self._returned = False
            act = "kembali"
        elif (self._player_present
              and self._idle_ticks >= self._p("presentasi_idle_ticks")
              and now - self._proaktif_terakhir >= self._p("presentasi_idle_ticks")):
            act = "menyapa_proaktif"
        else:
            return {}
        self._proaktif_terakhir = now
        self._idle_ticks = 0.0
        return self.ucap(kepada=kepada, act=act, diam_boleh=False)

    # ==================================================================
    # KESALAHAN TERKENDALI (konsep 5) — muncul ke permukaan dialog
    # ==================================================================
    def terima_bukti(self, keyakinan: str, bukti: str,
                     kekuatan: float = 0.6) -> Dict[str, Any]:
        """Player memberi bukti yang bertentangan; NPC ragu lalu bisa berubah.

        Menunjukkan disonansi lebih dulu ("aku tidak yakin…"), lalu bila
        keraguan cukup tinggi, mengubah keyakinan + narasi diri. Kembalikan
        dict dialog + status perubahan.
        """
        if not self.enabled():
            return {}
        ks = self._kes()
        if ks is not None:
            try:
                ks.hold_belief(keyakinan, bukti, kekuatan=kekuatan)
            except Exception as _galat_diagnostik_50:
                _diag.catat('naluri.Presentasi.terima_bukti', "galat pada jalur fallback", galat=_galat_diagnostik_50, jalur=50)
                pass
        doubt = self._doubt()
        # naikkan keraguan oleh bukti (bila kesadaran punya metodenya)
        if ks is not None:
            try:
                ks.metacognitive_doubt(min(1.0, doubt + 0.25 * float(kekuatan)))
            except Exception as _galat_diagnostik_51:
                _diag.catat('naluri.Presentasi.terima_bukti', "galat pada jalur fallback", galat=_galat_diagnostik_51, jalur=51)
                pass
        berubah = (self._doubt() >= 0.45)
        if berubah:
            self._ragu_berubah = True
            if ks is not None:
                try:
                    ks._refresh_identity({f"pernah berubah pikiran soal {keyakinan[:24]}": 0.3})
                except Exception as _galat_diagnostik_52:
                    _diag.catat('naluri.Presentasi.terima_bukti', "galat pada jalur fallback", galat=_galat_diagnostik_52, jalur=52)
                    pass
            teks = self._pick([
                f"Aku… aku tidak yakin lagi. Dulu aku percaya {keyakinan}, "
                f"tapi kalau katamu benar, maka aku harus memikirkannya ulang.",
                f"Kau membuatku goyah. Aku sudah lama memegang {keyakinan}, "
                f"tapi buktimu itu… aku tidak bisa mengabaikannya.",
            ])
        else:
            teks = self._pick([
                f"Aku mendengarmu. Tapi {keyakinan} itu masih terasa benar bagiku.",
                "Mungkin. Aku belum yakin. Aku perlu waktu.",
            ])
        entry = {"tick": self._tick(), "act": "berubah_pikiran" if berubah
                 else "ragu", "keyakinan": str(keyakinan)[:80],
                 "berubah": berubah, "teks": teks,
                 "doubt": round(self._doubt(), 3),
                 "nonverbal": self.nonverbal(None, "ragu"),
                 "deskripsi": self.deskripsi(teks=teks, act="ragu")}
        self._log(entry)
        return entry

    def koreksi_ingatan(self, versi_benar: str,
                        versi_salah: Optional[str] = None) -> Dict[str, Any]:
        """Player mengoreksi detail; NPC salah ingat tapi yakin akan INTINYA."""
        if not self.enabled():
            return {}
        salah = versi_salah or str(versi_benar)
        ks = self._kes()
        if ks is not None:
            try:
                ks.misremember(salah, str(versi_benar))
            except Exception as _galat_diagnostik_53:
                _diag.catat('naluri.Presentasi.koreksi_ingatan', "galat pada jalur fallback", galat=_galat_diagnostik_53, jalur=53)
                pass
        teks = self._pick([
            "Oh… mungkin aku yang salah ingat detailnya. Tapi perasaanku "
            "tentang kejadian itu tetap sama.",
            "Mungkin kau benar soal detailnya. Aku bisa keliru. Yang kuingat "
            "jelas hanyalah bagaimana rasanya saat itu.",
        ])
        self._salah_ingat = {"benar": str(versi_benar)[:80],
                             "salah": salah[:80], "tick": self._tick()}
        entry = {"tick": self._tick(), "act": "salah_ingat", "teks": teks,
                 "nonverbal": self.nonverbal(None, "mengenang"),
                 "deskripsi": self.deskripsi(teks=teks, act="mengenang")}
        self._log(entry)
        return entry

    # ==================================================================
    # UI/UX: INDIKATOR PSIKOLOGIS & TAG DIALOG (konsep 6)
    # ==================================================================
    def indikator_psikologis(self) -> Dict[str, Any]:
        """Ganti "stat bar" dengan keadaan psikologis yang terbaca manusia.

        Ketenangan (1 - arousal - ketegangan), Fokus (atensi - keraguan),
        Gairah (arousal), Keterhubungan (afiliasi + relasi). Nilai 0..1 +
        label kata. Bukan angka drive mentah.
        """
        if not self.enabled():
            return {"aktif": False}
        val = aro = 0.0
        try:
            m = self.naluri.mood()
            val, aro = float(m.valence), float(m.arousal)
        except Exception as _galat_diagnostik_54:
            _diag.catat('naluri.Presentasi.indikator_psikologis', "galat pada jalur fallback", galat=_galat_diagnostik_54, jalur=54)
            pass
        tegang = max(self._emosi("takut"), self._felt("tegang"),
                     self._felt("sesak"))
        ketenangan = jepit_01(0.5 + 0.5 * val - 0.6 * max(0.0, aro)
                                  - 0.5 * tegang)
        fokus = jepit_01(0.5 + 0.3 * max(0.0, -self._doubt())
                              - 0.4 * self._doubt() + 0.2 * self._effort())
        gairah = jepit_01(0.5 + aro)
        hub = jepit_01(0.5 + 0.4 * self._lev("afiliasi")
                           + 0.3 * self._moral("syukur"))

        def label(nama: str, v: float) -> str:
            tabel = {
                "ketenangan": [(0.66, "tenang"), (0.4, "cukup tenang"),
                               (0.2, "gelisah"), (0.0, "panik")],
                "fokus": [(0.66, "fokus"), (0.4, "cukup fokus"),
                          (0.2, "terpecah"), (0.0, "kacau")],
                "gairah": [(0.66, "bertenaga"), (0.4, "waspada"),
                           (0.2, "lesu"), (0.0, "mati rasa")],
                "keterhubungan": [(0.66, "terhubung"), (0.4, "netral"),
                                  (0.2, "sepi"), (0.0, "terasing")],
            }[nama]
            for batas, kata in tabel:
                if v >= batas:
                    return kata
            return tabel[-1][1]
        return {"aktif": True,
                "ketenangan": round(ketenangan, 3), "label_ketenangan": label("ketenangan", ketenangan),
                "fokus": round(fokus, 3), "label_fokus": label("fokus", fokus),
                "gairah": round(gairah, 3), "label_gairah": label("gairah", gairah),
                "keterhubungan": round(hub, 3), "label_keterhubungan": label("keterhubungan", hub)}

    def tag_dialog(self) -> str:
        """Tag dinamis untuk nama pembicara: '[Rama - Waspada]'.

        Diambil dari mood_label() + emosi dominan, sehingga UI tidak perlu
        menampilkan angka.
        """
        if not self.enabled():
            return self.naluri.name or ""
        nama = self.naluri.name or "NPC"
        label = ""
        try:
            label = str(self.naluri.mood_label())
        except Exception as _galat_diagnostik_55:
            _diag.catat('naluri.Presentasi.tag_dialog', "galat pada jalur fallback", galat=_galat_diagnostik_55, jalur=55)
            label = ""
        dom = None
        try:
            dom = self.naluri.emosi_dominan()
        except Exception as _galat_diagnostik_56:
            _diag.catat('naluri.Presentasi.tag_dialog', "galat pada jalur fallback", galat=_galat_diagnostik_56, jalur=56)
            dom = None
        if dom:
            label = self.naluri.hud_emosi.get(dom[0], dom[0]) if hasattr(
                self.naluri, "hud_emosi") else dom[0]
        # ritual terakhir bisa jadi konteks tag ("Rama - Menyendiri")
        if getattr(self.naluri, "ritual", None) is not None:
            try:
                st = self.naluri.ritual.state()
                if st.get("terakhir"):
                    label = label or "menyendiri"
            except Exception as _galat_diagnostik_57:
                _diag.catat('naluri.Presentasi.tag_dialog', "galat pada jalur fallback", galat=_galat_diagnostik_57, jalur=57)
                pass
        return f"{nama} - {label.capitalize()}" if label else nama

    @staticmethod
    def _lerp(a: float, b: float, t: float) -> float:
        return a + jepit_01(t) * (b - a)

    def _felt(self, name: str) -> float:
        ks = self._kes()
        if ks is not None:
            try:
                return float(getattr(ks, "felt", {}).get(name, 0.0))
            except Exception as _galat_diagnostik_58:
                _diag.catat('naluri.Presentasi._felt', "galat pada jalur fallback", galat=_galat_diagnostik_58, jalur=58)
                pass
        nur = self._nur()
        if nur is not None:
            try:
                return float(getattr(nur, "felt_state", {}).get(name, 0.0))
            except Exception as _galat_diagnostik_59:
                _diag.catat('naluri.Presentasi._felt', "galat pada jalur fallback", galat=_galat_diagnostik_59, jalur=59)
                pass
        return 0.0

    def _moral(self, name: str) -> float:
        ks = self._kes()
        if ks is not None:
            try:
                return float(getattr(ks, "moral", {}).get(name, 0.0))
            except Exception as _galat_diagnostik_60:
                _diag.catat('naluri.Presentasi._moral', "galat pada jalur fallback", galat=_galat_diagnostik_60, jalur=60)
                pass
        nur = self._nur()
        if nur is not None:
            try:
                return float(getattr(nur, "moral_emotions", {}).get(name, 0.0))
            except Exception as _galat_diagnostik_61:
                _diag.catat('naluri.Presentasi._moral', "galat pada jalur fallback", galat=_galat_diagnostik_61, jalur=61)
                pass
        return 0.0

    # ==================================================================
    # kanal NONVERBAL
    # ==================================================================
    def ekspresi(self) -> Dict[str, Any]:
        """Ekspresi wajah: campuran emosi + kebocoran mikro (leakage)."""
        if not self.enabled():
            return {}
        e = self._emosi
        inten = self._p("presentasi_intensitas")
        linger = self._p("presentasi_emosi_linger")
        campuran = {
            "takut": round(self._linger("emo_takut", e("takut") * inten, linger), 3),
            "marah": round(self._linger("emo_marah", e("marah") * inten, linger), 3),
            "senang": round(self._linger("emo_senang", e("senang") * inten, linger), 3),
            "sedih": round(self._linger("emo_sedih", e("sedih") * inten, linger), 3),
            "penasaran": round(self._linger("emo_penasaran", e("penasaran") * inten, linger), 3),
        }
        dominan = max(campuran, key=lambda k: campuran[k]) if campuran else "netral"
        wajah = {
            "takut": "mata melebar, rahang menegang",
            "marah": "alis berkerut, bibir menipis",
            "senang": "mata sedikit menyipit, sudut bibir naik",
            "sedih": "pandangan sayu, sudut bibir turun",
            "penasaran": "kepala sedikit miring, mata menyapu",
            "netral": "wajah tenang",
        }.get(dominan if campuran.get(dominan, 0.0) > 0.12 else "netral", "wajah tenang")
        # coping/suppression → mikro-ekspresi bocor (leakage)
        coping = False
        try:
            coping = bool(self.naluri.params.get("enable_coping", False))
        except Exception as _galat_diagnostik_62:
            _diag.catat('naluri.Presentasi.ekspresi', "galat pada jalur fallback", galat=_galat_diagnostik_62, jalur=62)
            coping = False
        if coping and self.enabled("microexpression"):
            raw = self._emosi("takut") + self._emosi("marah") + self._emosi("sedih")
            if raw > 0.6 and self._micro is None and self._rng.random() < 0.25:
                self._micro = dominan if dominan != "netral" else "takut"
                self._micro_ttl = 2.0
        return {"dominan": dominan, "campuran": campuran, "wajah": wajah,
                "mikro": self._micro, "kebocoran": self._tell_aktif()}

    def tatapan(self, kepada: Any = None) -> Dict[str, Any]:
        """Arah pandangan dari atensi/ignition + relasi + rasa malu/takut."""
        if not self.enabled("tatapan"):
            return {}
        ks = self._kes()
        target = None
        if ks is not None:
            try:
                spot = getattr(ks, "spotlight", []) or []
                if spot:
                    target = str(spot[0].get("content", ""))[:40]
            except Exception as _galat_diagnostik_63:
                _diag.catat('naluri.Presentasi.tatapan', "galat pada jalur fallback", galat=_galat_diagnostik_63, jalur=63)
                target = None
        # atensi bersama → menatap objek yang sama dengan lawan
        eid = self._eid(kepada)
        if ks is not None and eid:
            try:
                ja = getattr(ks, "_joint_attention", {}).get(eid)
                if ja and ja.get("objek"):
                    target = str(ja["objek"])[:40]
            except Exception as _galat_diagnostik_64:
                _diag.catat('naluri.Presentasi.tatapan', "galat pada jalur fallback", galat=_galat_diagnostik_64, jalur=64)
                pass
        averted = False
        if kepada is not None:
            rel = self._rel(kepada)
            label = self._label_rel(kepada)
            if self._moral("malu") > 0.4 or self._emosi("takut") > 0.55:
                averted = True
            elif label in ("asing", "curiga", "benci"):
                averted = True
            elif float(rel.get("valensi", 0.0)) > 0.3:
                averted = False
        # LINGER: pandangan menahan arahnya sebelum berpindah.
        averted = self._linger("gaze_menghindar", 1.0 if averted else 0.0,
                               self._p("presentasi_tatapan_linger")) > 0.5
        self._gaze = target or ("menunduk" if averted else (eid or None))
        return {"arah": self._gaze, "menghindar": averted,
                "kepada": eid or None}

    def postur(self) -> Dict[str, Any]:
        """Postur dari valensi/arousal/usaha/energi."""
        if not self.enabled():
            return {}
        val = 0.0
        aro = 0.0
        try:
            m = self.naluri.mood()
            val, aro = float(m.valence), float(m.arousal)
        except Exception as _galat_diagnostik_65:
            _diag.catat('naluri.Presentasi.postur', "galat pada jalur fallback", galat=_galat_diagnostik_65, jalur=65)
            pass
        # LINGER: postur punya momentum — nilai valensi/arousal meluruh lambat.
        val = self._linger("post_val", val, self._p("presentasi_postur_linger"))
        aro = self._linger("post_aro", aro, self._p("presentasi_postur_linger"))
        effort = self._effort()
        energi = self._linger("post_energi", self._lev("energi"),
                              self._p("presentasi_postur_linger"))
        if val < -0.25:
            desc = "membungkuk, bahu turun"
        elif aro > 0.55:
            desc = "menegang, condong ke depan"
        elif energi < -0.4:
            desc = "berdiri limbung, sering berpindah tumpuan"
        elif effort > 0.5:
            desc = "menegang menahan beban"
        else:
            desc = "berdiri rileks"
        self._posture = desc
        return {"deskripsi": desc, "valensi": round(val, 3),
                "arousal": round(aro, 3), "usaha": round(effort, 3)}

    def napas(self) -> Dict[str, Any]:
        """Napas: laju/kedalaman dari arousal, jantung, sesak, takut."""
        if not self.enabled():
            return {}
        sesak = self._felt("sesak")
        jantung = self._felt("jantung")
        takut = self._emosi("takut")
        laju = self._breath_rate
        if sesak > 0.4 or jantung > 0.5 or takut > 0.6:
            desk = "napas pendek dan cepat"
        elif laju < 0.35:
            desk = "napas pelan dan dalam"
        else:
            desk = "napas tenang"
        return {"laju": round(laju, 3), "deskripsi": desk,
                "sesak": round(sesak, 3), "jantung": round(jantung, 3)}

    def gestur(self, act: Optional[str] = None) -> Dict[str, Any]:
        """Gestur tangan/tubuh dari usaha, agensi, emosi, dan keanehan."""
        if not self.enabled("gestur"):
            return {}
        effort = self._effort()
        agency = self._agency()
        marah = self._emosi("marah")
        takut = self._emosi("takut")
        penasaran = self._emosi("penasaran")
        if agency < 0.3:
            desc = "tangan terangkat setengah lalu berhenti, seolah ragu milik siapa"
        elif marah > 0.5:
            desc = "tangan mengepal, satu gerakan tajam"
        elif takut > 0.5:
            desc = "tangan terangkat menahan, menjauh dari sumber"
        elif effort > 0.5:
            desc = "tangan bekerja dengan gerakan pendek dan terkendali"
        elif penasaran > 0.4:
            desc = "jari menyentuh dagu, kepala menyelidik"
        else:
            quirk = self._quirk_gesture()
            desc = quirk or "gerakan tangan kecil dan santai"
        # fidget: kegelisahan motorik
        if self._fidget > 0.4:
            desc += ", jemari gelisah"
        return {"deskripsi": desc, "usaha": round(effort, 3),
                "agensi": round(agency, 3)}

    def _quirk_gesture(self) -> Optional[str]:
        ks = self._kes()
        if ks is not None:
            try:
                q = list(getattr(ks, "quirks", []) or [])
                if q and self._rng.random() < 0.5:
                    return f"kebiasaan khas: {str(q[0])[:40]}"
            except Exception as _galat_diagnostik_66:
                _diag.catat('naluri.Presentasi._quirk_gesture', "galat pada jalur fallback", galat=_galat_diagnostik_66, jalur=66)
                pass
        return None

    def jarak(self, kepada: Any = None) -> Dict[str, Any]:
        """Jarak fisik (pendekatan/penghindaran) dari relasi + keamanan."""
        if not self.enabled():
            return {}
        dasar = self._p("presentasi_jarak_dasar")
        jarak = dasar
        label = self._label_rel(kepada) if kepada is not None else "netral"
        if label in ("suka", "percaya", "akrab"):
            jarak -= 0.15
        elif label in ("curiga", "benci"):
            jarak += 0.2
        jarak -= 0.15 * max(0.0, self._lev("keamanan"))
        jarak += 0.2 * max(0.0, -self._lev("keamanan"))
        jarak = jepit(jarak, 0.05, 1.0)
        if jarak < 0.35:
            desc = "berdiri dekat, nyaman"
        elif jarak > 0.7:
            desc = "menjaga jarak, siap mundur"
        else:
            desc = "berdiri pada jarak wajar"
        return {"nilai": round(jarak, 3), "deskripsi": desc, "label_relasi": label}

    # ==================================================================
    # LINGER (histeresis) — ekspresi punya momentum afektif
    # ==================================================================
    def _linger(self, kanal: str, target: float, decay: float) -> float:
        """Buat nilai kanal "tertinggal" dari target: naik cepat, turun lambat.

        Wajah yang sedih tetap sedih beberapa detik setelah berita baik,
        sebelum memudar. `decay` = fraksi langkah menuju target per panggilan
        (0 = tak pernah berubah, 1 = instan).
        """
        d = jepit_01(float(decay))
        cur = self._histeresis.get(kanal)
        if cur is None:
            self._histeresis[kanal] = float(target)
            return float(target)
        # nilai absolut lebih kuat → langsung naik; sebaliknya meluruh lambat
        if abs(target) >= abs(cur):
            baru = float(target)
        else:
            baru = cur + (float(target) - cur) * d
        self._histeresis[kanal] = baru
        return baru

    # ==================================================================
    # TELLS — kebocoran personal dari watak × drive paling "beku"
    # ==================================================================
    _TELL_PETA: Dict[str, List[str]] = {
        "keamanan": ["telinga kanannya bergerak sekali",
                     "menelan ludah sebelum menjawab",
                     "matanya melirik ke pintu"] ,
        "afiliasi": ["mengulang kata terakhir kalimatnya",
                     "tangannya bergerak ke lengan lalu berhenti",
                     "tertawa kecil yang tidak sampai ke mata"],
        "koherensi": ["menyentuh pelipis dengan dua jari",
                      "mengulang pertanyaan sebelum menjawab"],
        "energi": ["menggeser berat badan ke kaki lain",
                   "menghela napas tanpa suara"],
        "penguasaan": ["mengepalkan tangan lalu melepasnya",
                       "merapikan benda di dekatnya tanpa alasan"],
        "keingintahuan": ["menyapu pandangan ke samping",
                          "mencondongkan kepala sedikit ke arah suara"],
    }

    def _derive_tell(self) -> Dict[str, Any]:
        """Tell lahir dari watak: drive dengan `setpoint_lr` TERKECIL (paling
        beku) adalah titik yang paling sensitif bila dilanggar. Paranoid →
        keamanan; dingin → afiliasi.
        """
        lrs: Dict[str, float] = {}
        try:
            raw = (getattr(self.naluri, "params", {}) or {}).get("setpoint_lr")
        except Exception as _galat_diagnostik_67:
            _diag.catat('naluri.Presentasi._derive_tell', "galat pada jalur fallback", galat=_galat_diagnostik_67, jalur=67)
            raw = None
        if isinstance(raw, Mapping):
            for d, v in raw.items():
                if d in self._TELL_PETA:
                    try:
                        lrs[d] = float(v)
                    except (TypeError, ValueError):
                        continue
        if not lrs:
            # fallback: drive dengan bobot watak terbesar = paling penting
            try:
                wts = getattr(self.naluri, "weights", {}) or {}
                lrs = {d: -float(wts.get(d, 0.0)) for d in self._TELL_PETA}
            except Exception as _galat_diagnostik_68:
                _diag.catat('naluri.Presentasi._derive_tell', "galat pada jalur fallback", galat=_galat_diagnostik_68, jalur=68)
                lrs = {d: 0.0 for d in self._TELL_PETA}
        drive = min(lrs, key=lambda d: lrs[d]) if lrs else "keamanan"
        pilihan = self._TELL_PETA.get(drive, ["tangannya menegang sesaat"])
        try:
            teks = self._rng.choice(list(pilihan))
        except Exception as _galat_diagnostik_69:
            _diag.catat('naluri.Presentasi._derive_tell', "galat pada jalur fallback", galat=_galat_diagnostik_69, jalur=69)
            teks = pilihan[0]
        return {"drive": drive, "teks": teks}

    def _tell_aktif(self) -> Optional[str]:
        """Kebocoran muncul saat drive "beku" dilanggar DAN ada yang disembunyikan.

        Tidak pernah diumumkan sebagai "tell" — ia hanya deskripsi fisik yang
        bisa dipelajari pemain dari pola. Konsisten: teks tetap per-NPC.
        """
        if not self.enabled("microexpression") or not bool(
                self.params.get("presentasi_tell", True)):
            return None
        if self._tell is None:
            self._tell = self._derive_tell()
        drive = self._tell["drive"]
        try:
            defisit = float(self.naluri.deficit(drive))
        except Exception as _galat_diagnostik_70:
            _diag.catat('naluri.Presentasi._tell_aktif', "galat pada jalur fallback", galat=_galat_diagnostik_70, jalur=70)
            defisit = max(0.0, -self._lev(drive))
        if defisit < self._p("presentasi_tell_ambang"):
            return None
        # hanya bocor bila ada motif menyembunyikan: ragu, malu, takut, fidget
        menyembunyikan = (self._doubt() > 0.35 or self._moral("malu") > 0.3
                          or self._emosi("takut") > 0.3 or self._fidget > 0.4)
        if not menyembunyikan:
            return None
        return self._tell["teks"]

    def tell_katalog(self) -> Dict[str, Any]:
        """Untuk desainer/pengujian — BUKAN untuk ditampilkan ke pemain."""
        if self._tell is None:
            self._tell = self._derive_tell()
        return dict(self._tell)

    # ==================================================================
    # DIAM YANG BERMAKNA — hesitasi sebagai state
    # ==================================================================
    def _cek_pending_shift(self) -> Optional[Dict[str, Any]]:
        """Deteksi "pending shift": ignition, konflik drive, atau perubahan
        relasi dalam `presentasi_hesitasi_ticks` tick terakhir. Bila ada, NPC
        berhenti dulu, ubah act, baru bicara — bukan dispenser.
        """
        if not bool(self.params.get("presentasi_hesitasi", True)):
            return None
        jendela = max(1, int(self._p("presentasi_hesitasi_ticks")))
        now = self._tick()
        peristiwa: List[Tuple[str, int]] = []
        ks = self._kes()
        if ks is not None:
            ign = int(getattr(ks, "_last_ignition_tick", -10_000))
            if ign >= 0 and now - ign <= jendela:
                peristiwa.append(("ignition", ign))
            # spotlight hanya dihitung bila TICK benar-benar maju — mencegah
            # pemicu palsu saat kode memanggil beberapa kali dalam tick yang sama.
            spot = getattr(ks, "spotlight", []) or []
            top = str(spot[0].get("content", ""))[:48] if spot else None
            if (top is not None and self._last_spotlight is not None
                    and top != self._last_spotlight
                    and now != self._last_spot_check_tick):
                peristiwa.append(("pergeseran atensi", now))
            self._last_spotlight = top
            self._last_spot_check_tick = now
        nur = self._nur()
        if nur is not None:
            cf = int(getattr(nur, "_last_conflict_tick", -10_000))
            if cf >= 0 and now - cf <= jendela:
                peristiwa.append(("konflik drive", cf))
            so = int(getattr(nur, "_last_social_tick", -10_000))
            if so >= 0 and now - so <= jendela:
                peristiwa.append(("perubahan relasi", so))
        # hanya peristiwa yang BELUM pernah memicu hesitasi
        baru = [(n, t) for n, t in peristiwa if t > self._shift_seen_tick]
        if not baru:
            return None
        self._shift_seen_tick = max(t for _, t in baru)
        return {"sebab": sorted({n for n, _ in baru})}

    def hesitation_state(self) -> Dict[str, Any]:
        return {"pending": dict(self._pending_shift) if self._pending_shift else None,
                "terakhir": (dict(self._hesitasi_terakhir)
                             if self._hesitasi_terakhir else None)}

    def prosodi(self, act: Optional[str] = None) -> Dict[str, Any]:
        """Parameter suara: laju, tinggi, volume, tremor, jeda (ms)."""
        if not self.enabled("prosodi"):
            return {}
        aro = 0.0
        val = 0.0
        try:
            m = self.naluri.mood()
            aro, val = float(m.arousal), float(m.valence)
        except Exception as _galat_diagnostik_71:
            _diag.catat('naluri.Presentasi.prosodi', "galat pada jalur fallback", galat=_galat_diagnostik_71, jalur=71)
            pass
        effort = self._effort()
        rate = 0.5 + 0.4 * max(0.0, aro) + 0.2 * effort
        pitch = 0.5 + 0.2 * max(0.0, aro) + 0.15 * self._emosi("takut")
        volume = 0.5 + 0.3 * max(0.0, aro) + 0.2 * self._emosi("marah") \
            - 0.2 * self._moral("malu")
        tremor = max(0.0, self._emosi("takut") + self._felt("jantung")
                     + self._felt("nyeri")) * 0.5
        jeda = int(120 + 500 * self._doubt() + 300 * self._fidget
                   + 200 * max(0.0, -val))
        ks = self._kes()
        if ks is not None:
            try:
                if ks.enabled("self_audition"):
                    reaksi = ks._self_audition_reaction_now()
                    malu_dengar = float(reaksi.get("shame", 0.0))
                    ragu_dengar = float(reaksi.get("self_doubt", 0.0))
                    surprise_dengar = float(reaksi.get("surprise", 0.0))
                    rate *= max(0.68, 1.0 - 0.14 * malu_dengar
                                - 0.08 * surprise_dengar)
                    volume *= max(0.55, 1.0 - 0.24 * malu_dengar
                                  - 0.12 * ragu_dengar)
                    tremor += 0.18 * max(malu_dengar, ragu_dengar,
                                         surprise_dengar)
                    jeda += int(220 * malu_dengar + 180 * ragu_dengar
                                + 150 * surprise_dengar)
            except Exception as _galat_diagnostik_72:
                _diag.catat('naluri.Presentasi.prosodi', "galat pada jalur fallback", galat=_galat_diagnostik_72, jalur=72)
                pass
        if act in ("ragu", "menolak", "mengenang"):
            jeda += 250
        if act in ("peringatan", "menantang"):
            rate += 0.2
            volume += 0.1
        if act == "menimbang":
            # diam yang bermakna: jeda panjang sebelum jawaban yang berubah
            jeda += 400
        return {
            "laju": round(jepit(rate, 0.1, 1.0), 3),
            "tinggi": round(jepit(pitch, 0.1, 1.0), 3),
            "volume": round(jepit(volume, 0.05, 1.0), 3),
            "tremor": round(jepit_01(tremor), 3),
            "jeda_ms": int(max(0, min(2500, jeda))),
        }

    def nonverbal(self, kepada: Any = None,
                  act: Optional[str] = None) -> Dict[str, Any]:
        """Gabungan seluruh kanal nonverbal untuk satu momen."""
        if not self.enabled():
            return {}
        return {
            "ekspresi": self.ekspresi(),
            "tatapan": self.tatapan(kepada),
            "postur": self.postur(),
            "napas": self.napas(),
            "gestur": self.gestur(act),
            "jarak": self.jarak(kepada),
        }

    # ==================================================================
    # pembacaan state turunan (dipakai dialog)
    # ==================================================================
    def _doubt(self) -> float:
        ks = self._kes()
        if ks is not None:
            try:
                return float(getattr(ks, "doubt", 0.0))
            except Exception as _galat_diagnostik_73:
                _diag.catat('naluri.Presentasi._doubt', "galat pada jalur fallback", galat=_galat_diagnostik_73, jalur=73)
                return 0.0
        nur = self._nur()
        if nur is not None:
            try:
                return float(getattr(nur, "doubt_level", 0.0))
            except Exception as _galat_diagnostik_74:
                _diag.catat('naluri.Presentasi._doubt', "galat pada jalur fallback", galat=_galat_diagnostik_74, jalur=74)
                return 0.0
        return 0.0

    def _agency(self) -> float:
        ks = self._kes()
        if ks is not None:
            try:
                return float(getattr(ks, "agency", 0.5))
            except Exception as _galat_diagnostik_75:
                _diag.catat('naluri.Presentasi._agency', "galat pada jalur fallback", galat=_galat_diagnostik_75, jalur=75)
                return 0.5
        return 0.5

    def _effort(self) -> float:
        ks = self._kes()
        if ks is not None:
            try:
                return float(getattr(ks, "effort", 0.0))
            except Exception as _galat_diagnostik_76:
                _diag.catat('naluri.Presentasi._effort', "galat pada jalur fallback", galat=_galat_diagnostik_76, jalur=76)
                return 0.0
        return 0.0

    def _grief(self) -> Optional[Tuple[str, float]]:
        ks = self._kes()
        if ks is not None:
            try:
                g = getattr(ks, "grief", {}) or {}
                if g:
                    ent = max(g, key=lambda k: float(g[k].get("intensity", 0.0)))
                    val = float(g[ent].get("intensity", 0.0))
                    if val > 0.1:
                        return ent, val
            except Exception as _galat_diagnostik_77:
                _diag.catat('naluri.Presentasi._grief', "galat pada jalur fallback", galat=_galat_diagnostik_77, jalur=77)
                pass
        return None

    def _mortality(self) -> float:
        ks = self._kes()
        if ks is not None:
            try:
                return float(getattr(ks, "mortality_salience", 0.0))
            except Exception as _galat_diagnostik_78:
                _diag.catat('naluri.Presentasi._mortality', "galat pada jalur fallback", galat=_galat_diagnostik_78, jalur=78)
                return 0.0
        return 0.0

    def _dissonance(self) -> Optional[Dict[str, Any]]:
        ks = self._kes()
        if ks is None:
            return None
        try:
            d = getattr(ks, "dissonance", {}) or {}
            if not d:
                return None
            key = max(d, key=lambda k: float(d[k].get("tension", 0.0)))
            slot = d[key]
            if float(slot.get("tension", 0.0)) >= 0.3:
                return dict(slot)
        except Exception as _galat_diagnostik_79:
            _diag.catat('naluri.Presentasi._dissonance', "galat pada jalur fallback", galat=_galat_diagnostik_79, jalur=79)
            return None
        return None

    def _inner_speech(self) -> str:
        ks = self._kes()
        if ks is not None:
            try:
                t = getattr(ks, "self_talk", []) or []
                if t:
                    return str(t[-1].get("kalimat", ""))
            except Exception as _galat_diagnostik_80:
                _diag.catat('naluri.Presentasi._inner_speech', "galat pada jalur fallback", galat=_galat_diagnostik_80, jalur=80)
                pass
        nur = self._nur()
        if nur is not None:
            try:
                nd = getattr(nur, "narasi_diri", []) or []
                if nd:
                    return str(nd[-1].get("narasi", ""))
            except Exception as _galat_diagnostik_81:
                _diag.catat('naluri.Presentasi._inner_speech', "galat pada jalur fallback", galat=_galat_diagnostik_81, jalur=81)
                pass
        return ""

    def _kenangan(self) -> Optional[Dict[str, Any]]:
        """Episode autobiografis untuk referensi 'seperti waktu itu…'."""
        if self.jejak is not None:
            try:
                tl = self.jejak.autobiographical_timeline(limit=3)
                if tl:
                    return tl[-1]
            except Exception as _galat_diagnostik_82:
                _diag.catat('naluri.Presentasi._kenangan', "galat pada jalur fallback", galat=_galat_diagnostik_82, jalur=82)
                pass
        ks = self._kes()
        if ks is not None:
            try:
                tl = getattr(ks, "timeline", []) or []
                if tl:
                    return tl[-1]
            except Exception as _galat_diagnostik_83:
                _diag.catat('naluri.Presentasi._kenangan', "galat pada jalur fallback", galat=_galat_diagnostik_83, jalur=83)
                pass
        return None

    def _babak(self) -> Optional[str]:
        if self.jejak is not None:
            try:
                ch = self.jejak.life_chapters()
                if ch:
                    return str(ch[-1].get("label", ""))
            except Exception as _galat_diagnostik_84:
                _diag.catat('naluri.Presentasi._babak', "galat pada jalur fallback", galat=_galat_diagnostik_84, jalur=84)
                pass
        ks = self._kes()
        if ks is not None:
            try:
                ch = ks.life_chapters()
                if ch:
                    return str(ch[-1].get("label", ""))
            except Exception as _galat_diagnostik_85:
                _diag.catat('naluri.Presentasi._babak', "galat pada jalur fallback", galat=_galat_diagnostik_85, jalur=85)
                pass
        return None

    def _counterfactual(self) -> Dict[str, float]:
        if self.jejak is not None:
            try:
                return dict(self.jejak.counterfactual_emotions())
            except Exception as _galat_diagnostik_86:
                _diag.catat('naluri.Presentasi._counterfactual', "galat pada jalur fallback", galat=_galat_diagnostik_86, jalur=86)
                pass
        ks = self._kes()
        if ks is not None:
            try:
                return {k: round(float(v), 3)
                        for k, v in getattr(ks, "counterfactual_emotions", {}).items()
                        if float(v) > 0.05}
            except Exception as _galat_diagnostik_87:
                _diag.catat('naluri.Presentasi._counterfactual', "galat pada jalur fallback", galat=_galat_diagnostik_87, jalur=87)
                pass
        return {}

    def _dream(self) -> Optional[str]:
        ks = self._kes()
        if ks is not None:
            try:
                fn = getattr(ks, "dream_report", None)
                if callable(fn):
                    rep = str(fn())
                    if rep:
                        return rep
            except Exception as _galat_diagnostik_88:
                _diag.catat('naluri.Presentasi._dream', "galat pada jalur fallback", galat=_galat_diagnostik_88, jalur=88)
                pass
        return None

    def _refusal(self) -> Optional[Dict[str, Any]]:
        ks = self._kes()
        if ks is not None:
            try:
                r = getattr(ks, "refusals", []) or []
                if r and self._tick() - int(r[-1].get("tick", 0)) <= 6:
                    return dict(r[-1])
            except Exception as _galat_diagnostik_89:
                _diag.catat('naluri.Presentasi._refusal', "galat pada jalur fallback", galat=_galat_diagnostik_89, jalur=89)
                pass
        return None

    def _shared(self) -> Optional[str]:
        ks = self._kes()
        if ks is not None:
            try:
                sh = getattr(ks, "_shared_history", []) or []
                if sh:
                    return str(sh[-1])
            except Exception as _galat_diagnostik_90:
                _diag.catat('naluri.Presentasi._shared', "galat pada jalur fallback", galat=_galat_diagnostik_90, jalur=90)
                pass
        return None

    def _top_felt(self) -> Optional[Tuple[str, float]]:
        best = None
        for name in ("sesak", "jantung", "nyeri", "lelah", "lapar", "mual", "tegang"):
            v = self._felt(name)
            if v > 0.3 and (best is None or v > best[1]):
                best = (name, v)
        return best

    def _top_moral(self) -> Optional[Tuple[str, float]]:
        best = None
        for name in ("bersalah", "malu", "bangga", "cemburu", "iri",
                     "syukur", "haru", "kesepian"):
            v = self._moral(name)
            if v > 0.25 and (best is None or v > best[1]):
                best = (name, v)
        return best

    # ==================================================================
    # DIALOG — pemilihan tindak tutur & penyusunan ujaran
    # ==================================================================
    def _pilih_act(self, kepada: Any, topik: Optional[str],
                   masuk: bool = False) -> str:
        """Pilih tindak tutur dari keadaan internal (bukan acak murni)."""
        # DIAM YANG BERMAKNA: bila baru ada pergeseran (ignition/konflik/relasi),
        # NPC berhenti dulu — satu "menimbang" — lalu bicara dengan act baru.
        shift = self._cek_pending_shift()
        if shift and not self._shift_dipakai:
            self._shift_dipakai = True
            self._pending_shift = shift
            self._hesitasi_terakhir = {"tick": self._tick(), **shift}
            return "menimbang"
        if not shift:
            self._shift_dipakai = False
        # prioritas tertinggi: sinyal eksistensial/afektif kuat
        ref = self._refusal()
        if ref and topik and str(topik).lower() in str(ref.get("permintaan", "")).lower():
            return "menolak"
        if self._grief():
            return "mengenang"
        if self._mortality() > 0.6 and self._rng.random() < 0.5:
            return "eksistensial"
        dis = self._dissonance()
        if dis is not None:
            return "rasionalisasi"
        dream = self._dream()
        if dream and self._tick() % 3 == 0:
            return "mimpi"
        ks = self._kes()
        if ks is not None:
            try:
                if ks.enabled("self_audition"):
                    reaction = ks._self_audition_reaction_now()
                    if reaction.get("shame", 0.0) >= 0.42 \
                            or reaction.get("self_doubt", 0.0) >= 0.50:
                        return "ragu"
                    if reaction.get("surprise", 0.0) >= 0.68:
                        return "menimbang"
            except Exception as _galat_diagnostik_91:
                _diag.catat('naluri.Presentasi._pilih_act', "galat pada jalur fallback", galat=_galat_diagnostik_91, jalur=91)
                pass
        # Emosi epistemik mengubah bentuk respons walau valensi umum tidak berubah.
        if (self._epistemik("malu_tidak_tahu") > 0.58
                or self._epistemik("bingung") > 0.64):
            return "ragu"
        if self._epistemik("takjub") > 0.66:
            return "menimbang"
        if masuk:
            # jawaban atas pertanyaan lawan
            if self._doubt() > 0.45:
                return "ragu"
            if self._emosi("marah") > 0.45:
                return "menegur"
            if self._emosi("takut") > 0.5:
                return "waspada"
            if self._epistemik("penasaran") > 0.58:
                return "bertanya"
            if self._epistemik("lega") > 0.58:
                return "akrab"
            return "menjawab"
        # peringatan/ancaman bila bahaya + peduli lawan
        if self._lev("keamanan") < -0.4 and self._emosi("takut") > 0.4:
            return "peringatan"
        if self._emosi("marah") > 0.5:
            return "menantang"
        if self._emosi("penasaran") > 0.4 or self._epistemik("penasaran") > 0.50:
            return "bertanya"
        if self._epistemik("lega") > 0.58:
            return "akrab"
        if self._doubt() > 0.45:
            return "ragu"
        if self._inner_speech():
            return "mengamati"
        label = self._label_rel(kepada) if kepada is not None else "netral"
        if label in ("suka", "percaya", "akrab"):
            return "akrab"
        return "menyatakan"

    def _jawaban_keadaan(self, kepada: Any = None) -> Optional[str]:
        """Jawab pertanyaan tentang diri/keadaan dari state yang ada (E2).

        Hanya menjawab bila ujaran yang didengar memang menanyakannya,
        dan isi jawaban dibatasi keadaan yang benar-benar terbentuk pada
        Pycos (mood, emosi, nama) — bukan gudang jawaban lepas.
        """
        teks = str(self._ucapan_terakhir or "").lower()
        if not teks:
            return None
        addr = self._addr(kepada)
        sapaan = f", {addr}" if addr else ""

        def keadaan_singkat() -> str:
            try:
                m = self.naluri.mood()
                valensi = float(getattr(m, "valence", 0.0))
            except Exception as _galat_diagnostik_121:
                _diag.catat('naluri.Presentasi._jawaban_keadaan',
                            "galat pada jalur fallback",
                            galat=_galat_diagnostik_121, jalur=121)
                valensi = 0.0
            if valensi > 0.25:
                return "aku baik"
            if valensi < -0.25:
                return "aku tidak baik-baik saja"
            return "aku biasa saja"

        def emosi_teratas() -> Optional[Tuple[str, float]]:
            try:
                es = {k: float(v)
                      for k, v in dict(self.naluri.emosi_state() or {}).items()}
            except Exception as _galat_diagnostik_122:
                _diag.catat('naluri.Presentasi._jawaban_keadaan',
                            "galat pada jalur fallback",
                            galat=_galat_diagnostik_122, jalur=122)
                return None
            if not es:
                return None
            nama, nilai = max(es.items(), key=lambda kv: kv[1])
            return (nama, nilai) if nilai >= 0.3 else None

        # --- pertanyaan tentang kabar/keadaan batin ---
        if (re.search(r"\b(apa|bagaimana)\s+(kabar|keadaan)\b", teks)
                or "kabarmu" in teks or "keadaanmu" in teks):
            pokok = keadaan_singkat()
            emo = emosi_teratas()
            detail = f", sedang {emo[0]}" if emo else ""
            try:
                arousal = float(getattr(self.naluri.mood(), "arousal", 0.0))
            except Exception as _galat_diagnostik_123:
                _diag.catat('naluri.Presentasi._jawaban_keadaan',
                            "galat pada jalur fallback",
                            galat=_galat_diagnostik_123, jalur=123)
                arousal = 0.0
            if arousal > 0.6:
                detail += " dan pikiranku sedang penuh" if detail \
                    else ", pikiranku sedang penuh"
            return f"{pokok}{detail}{sapaan}."
        # --- pertanyaan tentang identitas ---
        if re.search(r"\bsiapa\s+(kamu|kau|dirimu|aku)\b", teks):
            nama = str(getattr(self.naluri, "name", "") or "").strip()
            if nama:
                return f"aku {nama}{sapaan}."
            return f"aku yang sedang bicara denganmu{sapaan}."
        # --- pertanyaan tentang isi pikiran/rasa ---
        if re.search(r"\b(apa|siapa)\s+yang\s+(kamu|kau)\s+"
                     r"(rasa|rasakan|pikirkan|pikir|inginkan|mau)\b", teks):
            inner = self._inner_speech()
            if inner:
                return inner
            emo = emosi_teratas()
            if emo:
                return f"aku merasa {emo[0]}{sapaan}."
            return f"{keadaan_singkat()}{sapaan}."
        # --- varian pertanyaan identitas: nama/panggilan ---
        nama_ku = str(getattr(self.naluri, "name", "") or "").strip()
        if nama_ku and re.search(
                r"\b(nama|panggilan)\b[^.!?]*\b(kamu|kau|dirimu|mu)\b"
                r"|\b(kamu|kau|dirimu)\b[^.!?]*\b(nama|panggil)\b"
                r"|\b(kamu|kau)\s+siapa\b", teks):
            return f"aku {nama_ku}{sapaan}."
        # --- jam/tanggal: Pycos tidak punya akses ke jam dinding ---
        if re.search(r"\bjam\b", teks):
            return f"aku tidak tahu jam berapa sekarang{sapaan}."
        if re.search(r"\btanggal\b", teks):
            return f"aku tidak tahu tanggal berapa sekarang{sapaan}."
        # --- tidak tahu, tetapi sebut HAL yang tidak diketahui (E2) ---
        frasa = None
        try:
            from pycos.bahasa.teks import jenis_pertanyaan
            jenis = (jenis_pertanyaan(teks) or {}).get("jenis")
            frasa = {"siapa": "siapa itu", "apa": "apa yang kau maksud",
                     "dimana": "di mana", "kapan": "kapan",
                     "kenapa": "kenapa", "bagaimana": "bagaimana",
                     "berapa": "berapa", "pilihan": "yang mana"}.get(jenis)
        except Exception as _galat_diagnostik_124:
            _diag.catat('naluri.Presentasi._jawaban_keadaan',
                        "galat pada jalur fallback",
                        galat=_galat_diagnostik_124, jalur=124)
            frasa = None
        if frasa:
            return f"aku tidak tahu {frasa}{sapaan}."
        return None

    def _pronomina(self, kepada: Any) -> Tuple[str, str]:
        """Pasangan (diri, lawan) yang konsisten untuk percakapan ini (F1).

        Register persona (formal/santai/netral) menentukan pasangan:
        formal → (saya, Anda); santai/netral → (aku, kamu) atau (aku, kau),
        dipilih sekali per mitra bicara (stabil lintas ujaran percakapan
        yang sama). Persona dibaca duck-typed dari `p.persona` atau
        `naluri.persona`; tanpa persona, pilihan mengikuti relasi.
        """
        kunci = self._eid(kepada) or "-"
        cached = self._pronomina_per_mitra.get(kunci)
        if cached is not None:
            return cached
        reg = ""
        persona = getattr(self, "persona", None)
        if persona is None:
            persona = getattr(self.naluri, "persona", None)
        if persona is not None:
            reg = str(getattr(persona, "register", "") or "").lower()
        if reg == "formal":
            pasangan = ("saya", "Anda")
        elif reg in ("santai", "netral", "akrab"):
            # dua ragam akrab disahkan F1; pilih satu per mitra bicara
            pasangan = ("aku", "kau" if sum(map(ord, kunci)) % 2 == 0
                        else "kamu")
        else:
            label = self._label_rel(kepada) if kepada is not None else "netral"
            pasangan = (("aku", "kau" if sum(map(ord, kunci)) % 2 == 0
                         else "kamu")
                        if label in ("akrab", "suka", "percaya")
                        else ("aku", "kamu"))
        self._pronomina_per_mitra[kunci] = pasangan
        return pasangan

    def _konsisten_pronomina(self, teks: str, kepada: Any) -> str:
        """Normalisasi pronomina pada satu ujaran agar konsisten (F1).

        Semua bentuk lawan (`kamu|kau|anda`) dan diri (`aku|saya|gue`)
        diganti pasangan pilihan percakapan. Awalan `ku-` yang melekat pada
        verba dilepas ke bentuk `saya/aku + verba` bila diri = saya/Anda
        (ragam formal tidak memakai klitik). Kapital dipertahankan di awal
        kalimat.
        """
        if not teks:
            return teks
        diri, lawan = self._pronomina(kepada)
        out = teks
        if diri == "saya":
            # klitik ku- → diri + spasi (ragam formal tidak memakai klitik)
            out = re.sub(r"\bku(?=[bcdfghjklmnprstvwz])", diri + " ", out)
        out = re.sub(r"\b(kamu|kau|anda)\b", lawan, out, flags=re.IGNORECASE)
        out = re.sub(r"\b(aku|saya|gue)\b",
                     lambda m: diri,
                     out, flags=re.IGNORECASE)
        # kapital di awal kalimat
        out = re.sub(r"(^|[.!?…]\s*)([a-zà-ÿ])",
                     lambda m: m.group(1) + m.group(2).upper(), out)
        return out

    def _addr(self, kepada: Any) -> str:
        if kepada is None:
            return ""
        eid = self._eid(kepada)
        label = self._label_rel(kepada)
        if label == "asing":
            return ""
        if label in ("akrab", "suka", "percaya"):
            return eid
        return eid

    def _kita(self, kepada: Any) -> bool:
        """Apakah memakai 'kita' (atensi bersama / relasi dekat)."""
        ks = self._kes()
        eid = self._eid(kepada)
        if ks is not None and eid:
            try:
                if getattr(ks, "_joint_attention", {}).get(eid):
                    return True
            except Exception as _galat_diagnostik_92:
                _diag.catat('naluri.Presentasi._kita', "galat pada jalur fallback", galat=_galat_diagnostik_92, jalur=92)
                pass
        return self._label_rel(kepada) in ("akrab", "suka", "percaya")

    def _isi_ucap(self, act: str, kepada: Any, topik: Optional[str]) -> str:
        """Inti ujaran per tindak tutur (dipilih dari beberapa varian)."""
        n = self.naluri
        addr = self._addr(kepada)
        sapaan = f", {addr}" if addr else ""
        kita = "kita" if self._kita(kepada) else "aku"
        topik_txt = str(topik or "").strip()
        inner = self._inner_speech()

        if act == "menimbang":
            return self._pick([
                "…sebentar.",
                "*menghela napas pelan*",
                "…tunggu. bukan itu yang ingin kukatakan.",
                "*menatap ke samping sejenak*",
            ])
        if act == "kembali":
            babak = self._babak()
            return self._pick([
                f"Ah, kau kembali{sapaan}. Aku mulai berpikir kau tidak akan datang lagi.",
                f"Kau kembali juga akhirnya{sapaan}. Lama sekali.",
                (f"Kau kembali. {babak.capitalize()}… rasanya sudah lama sejak itu."
                 if babak else "Kau kembali. Sudah lama."),
            ])
        if act == "menyapa_proaktif":
            return self._pick([
                f"Ada yang bisa kubantu{sapaan}? Atau kau hanya ingin menatapku?",
                f"Kau terlihat melamun{sapaan}.",
                f"Kau belum berkata apa-apa sejak tadi{sapaan}.",
            ])
        if act == "menolak":
            ref = self._refusal() or {}
            return self._pick([
                f"tidak{sapaan}. {ref.get('alasan', 'itu melanggar prinsipku')}",
                f"maaf{sapaan}, aku tak bisa. {ref.get('alasan', 'itu bukan caraku')}",
            ])
        if act == "mengenang":
            g = self._grief()
            ent = g[0] if g else "dia"
            return self._pick([
                f"aku masih memikirkan {ent}{sapaan}… terkadang aku lupa dia sudah pergi.",
                f"{sapaan}, tadi aku hampir memanggil nama {ent}. Aneh, ya.",
            ])
        if act == "eksistensial":
            return self._pick([
                f"{sapaan}, kau pernah berpikir bahwa {kita} bisa hilang kapan saja?",
                "aku tidak takut mati. Yang kutakutkan adalah tidak sempat.",
                f"{sapaan}, kita semua akan mati. Kadang itu yang membuatku berhati-hati.",
            ])
        if act == "rasionalisasi":
            dis = self._dissonance() or {}
            keyakinan = dis.get("keyakinan", "itu")
            return self._pick([
                f"soal '{keyakinan}' — aku punya alasanku sendiri{sapaan}. Itu tidak seperti yang kau pikir.",
                f"kau tidak mengerti{sapaan}. Ada hal yang tidak bisa dinilai dari luar.",
            ])
        if act == "mimpi":
            d = self._dream() or "aku bermimpi aneh semalam"
            return f"{sapaan}, {d}." if sapaan else f"{d}."
        if act == "peringatan":
            apa = topik_txt or "di sana"
            return self._pick([
                f"jangan ke {apa}{sapaan}. Aku tidak mau kau kenapa-napa.",
                f"menjauh dari {apa}. Percayalah padaku.",
            ])
        if act == "menantang":
            return self._pick([
                f"kau ingin tahu kenapa aku marah{sapaan}?",
                "jangan main-main denganku.",
                f"{sapaan}, aku sudah muak. Katakan apa maumu.",
            ])
        if act == "menegur":
            return self._pick([
                f"kenapa kau melakukan itu{sapaan}?",
                "itu tidak seharusnya.",
            ])
        if act == "waspada":
            return self._pick([
                f"aku tidak yakin kau bisa dipercaya{sapaan}.",
                "tetap di sana. Jangan mendekat dulu.",
            ])
        if act == "bertanya":
            apa = topik_txt or "itu"
            return self._pick([
                f"apa yang sebenarnya terjadi dengan {apa}{sapaan}?",
                f"kenapa {apa}? Aku ingin tahu.",
                f"{sapaan}, kau tahu sesuatu tentang {apa}?",
            ])
        if act == "ragu":
            return self._pick([
                f"mungkin… aku tidak yakin{sapaan}.",
                "sepertinya aku salah. Atau mungkin tidak. Aku tidak tahu.",
                f"{sapaan}, tunggu. Aku perlu berpikir sebentar.",
            ])
        if act == "akrab":
            return self._pick([
                f"kau masih di sini{sapaan}. Bagus.",
                f"seperti waktu itu, ya{sapaan}?",
                f"aku senang kau ada, {addr}." if addr else "aku senang kau ada.",
            ])
        if act == "menjawab":
            jawaban = self._jawaban_keadaan(kepada)
            if jawaban:
                return jawaban
            if inner:
                return inner
            return self._pick([
                f"aku tidak tahu harus bilang apa{sapaan}.",
                f"ya. Begitulah{sapaan}.",
            ])
        if act == "mengamati":
            if inner:
                return inner
            return self._pick([
                f"ada yang sedang kupikirkan{sapaan}.",
                "hm. Aku memperhatikan sesuatu.",
            ])
        # menyatakan (default)
        if topik_txt:
            return self._pick([
                f"soal {topik_txt}{sapaan} — aku sedang memikirkannya.",
                f"{sapaan}, {topik_txt} membuatku tidak tenang.",
            ])
        niat = ""
        try:
            niat = str(n.self_intent() if hasattr(n, "self_intent")
                       else n.intent().get("teks", ""))
        except Exception as _galat_diagnostik_93:
            _diag.catat('naluri.Presentasi._isi_ucap', "galat pada jalur fallback", galat=_galat_diagnostik_93, jalur=93)
            niat = ""
        if inner:
            return inner
        if niat:
            # E4: hanya ungkapkan niat yang MEMANG terbentuk; tanpa niat,
            # jangan mengarang — biarkan jalur memanggil diam.
            return f"{sapaan + ' ' if sapaan else ''}{niat}."
        return ""

    def _bingkai_relasi(self, teks: str, kepada: Any) -> str:
        """Sisipkan referensi sejarah bersama / pronomina bila relevan."""
        if kepada is None or not teks:
            return teks
        sh = self._shared()
        ken = self._kenangan()
        dekat = self._label_rel(kepada) in ("akrab", "suka", "percaya")
        peluang = 0.45 if dekat else 0.18
        if self._rng.random() < peluang:
            dasar = teks.rstrip()
            if dasar and dasar[-1] not in ".!?…":
                dasar += "."
            if sh:
                teks = f"{dasar} Seperti waktu {sh[:48]}."
            elif ken and ken.get("ringkas"):
                teks = f"{dasar} Aku ingat {str(ken.get('ringkas'))[:48]}."
        return teks

    def _warnai(self, teks: str, act: str) -> str:
        """Beri warna afektif: hedges, interjeksi somatik, jeda, gagap."""
        if not teks:
            return teks
        out = teks
        # hedges keraguan
        if self._doubt() > 0.35 and act not in ("ragu",):
            out = self._pick(["mungkin ", "sepertinya ", "kalau tidak salah, "]) + out
        # interjeksi tubuh
        felt = self._top_felt()
        if felt and self._rng.random() < 0.5:
            interjeksi = {
                "sesak": "(napas tertahan) ",
                "jantung": "(menekan dada) ",
                "nyeri": "(mengerang pelan) ",
                "lelah": "(suara melemah) ",
                "lapar": "(menelan ludah) ",
                "mual": "(menahan mual) ",
                "tegang": "(rahang mengeras) ",
            }.get(felt[0], "")
            out = interjeksi + out
        # emosi moral
        moral = self._top_moral()
        if moral:
            tag = {
                "bersalah": "maaf… ", "malu": "aku… ", "bangga": "hei, ",
                "cemburu": "siapa dia? ", "iri": "kamu beruntung. ",
                "syukur": "terima kasih. ", "haru": "… ", "kesepian": "kamu masih di sini? ",
            }.get(moral[0], "")
            if tag and not out.startswith(tag):
                out = tag + out
        # gagap saat arousal/takut tinggi
        arousal = 0.0
        try:
            arousal = float(self.naluri.mood().arousal)
        except Exception as _galat_diagnostik_94:
            _diag.catat('naluri.Presentasi._warnai', "galat pada jalur fallback", galat=_galat_diagnostik_94, jalur=94)
            pass
        if (arousal > 0.6 or self._emosi("takut") > 0.6) and self._rng.random() < 0.4:
            m = re.match(r"([A-Za-zÀ-ÿ]{2,})", out)
            if m:
                out = m.group(1)[0] + "-" + out
        # agensi rendah → kalimat pasif
        if self._agency() < 0.3:
            out = out + " (tanganku bergerak sendiri saat mengatakannya)"
        # normalisasi: buang tanda baca pemisah di awal (mis. sapaan ", Player,")
        out = out.strip()
        while out[:1] in (",", ";", ":", "—"):
            out = out[1:].lstrip()
        out = re.sub(r"\)\s*,\s*", ") ", out)
        out = re.sub(r"\s+,", ",", out)
        if out and out[0].islower():
            out = out[0].upper() + out[1:]
        return out

    def ucap(self, kepada: Any = None, topik: Optional[str] = None,
             act: Optional[str] = None, masuk: bool = False,
             diam_boleh: bool = True) -> Dict[str, Any]:
        """Hasilkan ujaran; strategi sosial hanya memakai rencana sadar."""
        if not self.enabled():
            return {}
        if diam_boleh and self._p("presentasi_bisukan") > 0:
            if self._rng.random() < self._p("presentasi_bisukan"):
                return self._beat_diam(kepada)
        ks = self._kes()
        # Rencana kebohongan, peran, atau langkah manipulasi tidak dibuat
        # otomatis: hanya keputusan eksplisit sebelumnya yang boleh dipakai.
        direct: Optional[Dict[str, Any]] = None
        role_style: Optional[Dict[str, Any]] = None
        if ks is not None:
            try:
                deception = ks.strategic_speech_for(kepada, topik)
                if deception:
                    direct = {"jenis": "kebohongan_sengaja",
                              "id": deception.get("id"),
                              "teks": str(deception.get("ujaran_dipilih", "")),
                              "tujuan": str(deception.get("tujuan", ""))}
            except Exception as _galat_diagnostik_95:
                _diag.catat('naluri.Presentasi.ucap', "galat pada jalur fallback", galat=_galat_diagnostik_95, jalur=95)
                direct = None
            if direct is None:
                try:
                    role = ks.roleplay_speech_for(kepada)
                    if role and role.get("teks"):
                        direct = {"jenis": "permainan_peran",
                                  "teks": str(role.get("teks", "")),
                                  "peran": str(role.get("peran", ""))}
                    elif role:
                        role_style = dict(role)
                except Exception as _galat_diagnostik_96:
                    _diag.catat('naluri.Presentasi.ucap', "galat pada jalur fallback", galat=_galat_diagnostik_96, jalur=96)
                    role_style = None
            if direct is None and role_style is None:
                try:
                    step = ks.next_manipulation_action(kepada, topik)
                    if step and str(step.get("ujaran", "")).strip():
                        direct = {"jenis": "langkah_manipulasi",
                                  "plan_id": step.get("plan_id"),
                                  "indeks": step.get("indeks"),
                                  "teks": str(step.get("ujaran", "")),
                                  "tujuan": str(step.get("tujuan", ""))}
                except Exception as _galat_diagnostik_97:
                    _diag.catat('naluri.Presentasi.ucap', "galat pada jalur fallback", galat=_galat_diagnostik_97, jalur=97)
                    direct = None
        if direct is not None and not str(direct.get("teks", "")).strip():
            direct = None
        style = dict((role_style or {}).get("gaya") or {})
        role_act = str(style.get("act", style.get("tindak_tutur",
                         (role_style or {}).get("act", ""))) or "")
        valid_acts = {"menjawab", "bertanya", "menyatakan", "menolak",
                      "mengamati", "akrab", "menantang", "peringatan",
                      "ragu", "waspada", "mengenang", "eksistensial"}
        act = act or ("menjawab" if direct is not None else
                      role_act if role_act in valid_acts else
                      self._pilih_act(kepada, topik, masuk=masuk))
        # E5: skema act adalah pengetahuan bentuk/fungsi, bukan planner yang
        # menciptakan isi. Act di luar skema diturunkan ke "menyatakan" —
        # bentuk umum keadaan — bukan dipaksakan lewat templat.
        if act not in _ACT_FUNGSI:
            self._tutur_trace = list(getattr(self, "_tutur_trace", []) or []) + [
                {"E5": {"act_tak_dikenal": act, "diturunkan_ke": "menyatakan"}}]
            act = "menyatakan"
        skema = _skema_act(act)
        self._skema_act_terakhir = skema
        teks = ""
        niat_teks = ""
        generatif = False
        if direct is not None:
            # Ujaran yang dipilih sengaja tidak disamarkan oleh template,
            # framing relasional, atau warna bahasa otomatis.
            teks = str(direct.get("teks", "")).strip()
            niat_teks = teks
            if teks and teks[-1] not in ".!?…":
                teks += "."
            niat_teks = teks
        else:
            # F3 + anti-pengulangan: hasilkan beberapa variasi dari keadaan
            # & pikiran yang SAMA; pilih yang (a) bukan pengulangan dan
            # (b) lolos pemeriksa gramatika G1 — tanpa mengubah isi batin.
            def _masalah_selaras(calon: str) -> List[str]:
                """G3: kandidat melanggar pantangan/persona dihindari.

                Bila ada kandidat lain dari keadaan yang sama yang lolos,
                pemakaian `for _coba` yang memilihnya — evaluasi kandidat
                berikutnya dari lingkaran revisi G3, tanpa mengubah isi
                pikiran Pycos.
                """
                persona_g3 = (getattr(self, "persona", None)
                              or getattr(self.naluri, "persona", None))
                if persona_g3 is None:
                    return []
                try:
                    from pycos.inti.persona import Keadaan
                    from pycos.refleksi.nurani import nilai_selaras
                    keadaan_g3 = Keadaan.dari_mood(self.naluri.mood(),
                                                   ketidakpastian=self._doubt())
                    rep = nilai_selaras(
                        persona_g3, keadaan_g3, calon,
                        ujaran_lawan=str(self._ucapan_terakhir or "") or None,
                        giliran_sebelumnya=(self._recent_texts[-1]
                                            if self._recent_texts else None))
                    if rep.status == "melanggar_pantangan":
                        return ["melanggar_pantangan"]
                    if rep.status == "tidak_selaras":
                        return ["tidak_selaras"]
                    return []
                except Exception as _galat_diagnostik_110:
                    _diag.catat('naluri.Presentasi.ucap',
                                "galat pada jalur fallback",
                                galat=_galat_diagnostik_110, jalur=110)
                    return []

            leks_f3 = None
            try:
                _eng_f3 = self.tutur_engine()
                leks_f3 = getattr(_eng_f3, "leks", None)
            except Exception as _galat_diagnostik_108:
                _diag.catat('naluri.Presentasi.ucap',
                            "galat pada jalur fallback",
                            galat=_galat_diagnostik_108, jalur=108)
                leks_f3 = None
            pilihan_teks = None
            pilihan_inti = None
            masalah_pilihan: List[str] = []
            for _coba in range(6):
                inti = self._generatif(act, kepada, topik, masuk=masuk,
                                       coba=_coba)
                if inti is None:
                    inti = self._isi_ucap(act, kepada, topik)
                inti = self._bingkai_relasi(inti, kepada)
                calon = self._warnai(inti, act)
                if role_style:
                    prefix = str(style.get("awalan", style.get("prefix", "")) or "").strip()
                    suffix = str(style.get("akhiran", style.get("suffix", "")) or "").strip()
                    if prefix and not calon.lower().startswith(prefix.lower()):
                        calon = prefix + " " + calon
                    if suffix and not calon.lower().endswith(suffix.lower()):
                        calon = calon.rstrip(" .!?…") + " " + suffix
                    replacements = style.get("kata", style.get("penggantian_kata", {}))
                    if isinstance(replacements, Mapping):
                        for source, target_word in list(replacements.items())[:8]:
                            if str(source).strip() and str(target_word).strip():
                                calon = re.sub(r"\b" + re.escape(str(source)) + r"\b",
                                               str(target_word), calon,
                                               flags=re.IGNORECASE)
                if not str(calon or "").strip():
                    # E4: tak ada dasar untuk bertutur — kandidat hampa.
                    masalah = ["kandidiat_hampa"]
                else:
                    # G3 (batas): pantangan/selaras + G1 memakai jalur
                    # yang sama — kandidat melanggar ditandai; loop
                    # memilih kandidat terbersih.
                    masalah = _masalah_selaras(str(calon))
                    try:
                        from pycos.bahasa.teks import (periksa_gramatika as
                                                       _pgm, G1_KERAS)
                        g1 = _pgm(str(calon), leks_f3)
                        masalah = list(masalah) + [m for m in g1 if m in G1_KERAS]
                        masalah = list(masalah) + [m for m in g1 if m not in G1_KERAS]
                    except Exception as _galat_diagnostik_109:
                        _diag.catat('naluri.Presentasi.ucap',
                                    "galat pada jalur fallback",
                                    galat=_galat_diagnostik_109, jalur=109)
                        masalah = []
                if calon in self._recent_texts:
                    masalah = list(masalah) + ["pengulangan_terbaru"]
                if (pilihan_inti is None
                        or len(masalah) < len(masalah_pilihan)):
                    pilihan_teks, pilihan_inti = calon, str(inti)
                    masalah_pilihan = list(masalah)
                if not masalah and str(calon or "").strip():
                    # kandidat bersih & segar → tidak perlu mencoba lagi
                    break
            teks = pilihan_teks or ""
            niat_teks = pilihan_inti or ""
            if masalah_pilihan:
                self._tutur_trace = list(getattr(self, "_tutur_trace", []) or []) + [
                    {"F3": {"dipilih": teks, "masalah": masalah_pilihan}}]
            generatif = bool(self._tutur is not None)
        # E4: bila tak ada dasar untuk bertutur, jangan menyodorkan teks —
        # diam atau perilaku nonverbal saja.
        if direct is None and not str(teks or "").strip():
            return self._beat_diam(kepada)
        # batasi verbositas (kalimat)
        verb = max(0.2, self._p("presentasi_verbositas"))
        from pycos.bahasa.teks import pecah_kalimat as _pecah
        kalimat = _pecah(teks)
        batas = max(1, int(round(1 + 1.5 * verb)))
        if len(kalimat) > batas:
            teks = " ".join(kalimat[:batas])
        if direct is None:
            # F1: satu pasangan pronomina per percakapan; ujaran yang
            # dipilih sadar (direct) tidak diubah.
            teks = self._konsisten_pronomina(teks, kepada)
        self._recent_texts.append(teks)
        if len(self._recent_texts) > 6:
            self._recent_texts = self._recent_texts[-6:]
        nv = self.nonverbal(kepada, act)
        pros = self.prosodi(act)
        self._last_act = act
        self._act_counts[act] = self._act_counts.get(act, 0) + 1
        self._silence = 0.0
        self._boredom = max(0.0, self._boredom - self._p("presentasi_bosan_pulih"))
        if ks is not None:
            try:
                ks.attention_effort(teks, source="mengucap")
            except Exception as _galat_diagnostik_98:
                _diag.catat('naluri.Presentasi.ucap', "galat pada jalur fallback", galat=_galat_diagnostik_98, jalur=98)
                pass
        if ks is not None and self._eid(kepada):
            try:
                ks.dialogue_turn(self.naluri.name or "npc", teks)
            except Exception as _galat_diagnostik_99:
                _diag.catat('naluri.Presentasi.ucap', "galat pada jalur fallback", galat=_galat_diagnostik_99, jalur=99)
                pass
        entry = {
            "tick": self._tick(), "act": act, "kepada": self._eid(kepada),
            "teks": teks, "nonverbal": nv, "prosodi": pros,
            "_audisi_intended": niat_teks,
            "keyakinan": round(max(0.0, 1.0 - self._doubt()), 3),
            "deskripsi": self.deskripsi(teks=teks, nonverbal=nv, act=act,
                                        kepada=kepada),
            "generatif": generatif,
        }
        if direct is not None:
            direct["teks"] = teks
            entry["_strategic_plan"] = direct
        elif role_style:
            entry["_strategic_plan"] = {"jenis": "permainan_peran",
                                         "teks": teks,
                                         "peran": role_style.get("peran", "")}
        if bool(self.params.get("presentasi_trace", False)):
            entry["trace"] = list(self._tutur_trace)
        self._log(entry)
        return entry

    def _beat_diam(self, kepada: Any) -> Dict[str, Any]:
        nv = self.nonverbal(kepada, "diam")
        entry = {"tick": self._tick(), "act": "diam", "kepada": self._eid(kepada),
                 "teks": "", "nonverbal": nv, "prosodi": self.prosodi("diam"),
                 "keyakinan": round(max(0.0, 1.0 - self._doubt()), 3),
                 "deskripsi": self.deskripsi(teks="", nonverbal=nv, act="diam",
                                             kepada=kepada)}
        self._log(entry)
        return entry

    def _dengar_efek(self, teks: str, dari: Any) -> Dict[str, Any]:
        """Teruskan ujaran yang didengar ke keadaan batin (D8).

        * **Drive** bergerak lewat `impact_of` (pecahan kecil dari vektor
          leksikon; alasan tercatat di `delta_log`).
        * **Emosi** (takut/marah/senang/sedih/penasaran) digerakkan oleh
          tindak tutur yang didengar, diskalakan relasi dengan pembicara —
          kalimat yang sama terasa berbeda dari orang yang dipercaya.
        * **Rasa epistemik** (ragu/yakin/penasaran) diperbarui lewat
          Kesadaran bila aktif — ini "pembaruan keyakinan" ujaran masuk.

        Aman dipanggil kapan pun: semua kanal dinonaktifkan bila state
        terkait absen/mati. Fungsi ini bersifat aditif dan kecil — ujaran
        masuk menggeser, tidak memutarbalikkan, keadaan batin.
        """
        n = self.naluri
        if not bool(self.params.get("presentasi_dengar_efek", True)):
            return {}
        efek: Dict[str, Any] = {}
        # --- 1) drive via impact_of (pecahan; pulihkan counter NURANI) ---
        if hasattr(n, "impact_of"):
            nur = getattr(n, "nurani", None)
            hits0 = getattr(nur, "affective_hits", 0) if nur is not None else 0
            try:
                imp = n.impact_of(str(teks)) or {}
            except Exception as _galat_diagnostik_110:
                _diag.catat('naluri.Presentasi._dengar_efek',
                            "galat pada jalur fallback",
                            galat=_galat_diagnostik_110, jalur=110)
                imp = {}
            if nur is not None:
                nur.affective_hits = hits0
            gain = float(self.params.get("presentasi_dengar_efek_gain", 0.12))
            applied: Dict[str, float] = {}
            for drive, nilai in imp.items():
                try:
                    dv = float(nilai) * gain
                except (TypeError, ValueError):
                    continue
                if abs(dv) >= 0.02:
                    try:
                        n.delta(drive, dv, reason="dengar:ujaran masuk")
                        applied[str(drive)] = round(dv, 4)
                    except Exception as _galat_diagnostik_111:
                        _diag.catat('naluri.Presentasi._dengar_efek',
                                    "galat pada jalur fallback",
                                    galat=_galat_diagnostik_111, jalur=111)
                        pass
            if applied:
                efek["drive"] = applied
        # --- 2) emosi via tindak tutur × relasi ---
        try:
            from pycos.bahasa.teks import tindak_tutur_skor
            tindak = tindak_tutur_skor(str(teks)) or {}
        except Exception as _galat_diagnostik_114:
            _diag.catat('naluri.Presentasi._dengar_efek',
                        "galat pada jalur fallback",
                        galat=_galat_diagnostik_114, jalur=114)
            tindak = {}
        label = "netral"
        if dari is not None:
            try:
                label = str(self._label_rel(dari))
            except Exception as _galat_diagnostik_115:
                _diag.catat('naluri.Presentasi._dengar_efek',
                            "galat pada jalur fallback",
                            galat=_galat_diagnostik_115, jalur=115)
                label = "netral"
        dekat = label in ("akrab", "suka", "percaya")
        mult_neg = 0.6 if dekat else 1.0   # orang dekat lebih mudah dilukai? tidak — lebih kecil kontribusi sinis
        mult_pos = 1.2 if dekat else 1.0
        pemetaan = {   # tindak -> (emosi, dasar, pengali)
            "pujian": ("senang", 0.10, mult_pos),
            "terima_kasih": ("senang", 0.06, mult_pos),
            "hinaan": ("marah", 0.12, mult_neg),
            "tuduhan": ("marah", 0.10, mult_neg),
            "ancaman": ("takut", 0.14, mult_neg),
            "peringatan": ("takut", 0.07, mult_neg),
            "keluhan": ("sedih", 0.05, 1.0),
            "penolakan": ("sedih", 0.05, 1.0),
            "ajakan": ("senang", 0.04, mult_pos),
            "persetujuan": ("senang", 0.06, mult_pos),
            "pertanyaan": ("penasaran", 0.05, 1.0),
        }
        emo_applied: Dict[str, float] = {}
        if getattr(n, "_emosi_aktif", lambda: False)():
            for tt, (emosi, dasar, mult) in pemetaan.items():
                try:
                    skor = float(tindak.get(tt, 0.0) or 0.0)
                except (TypeError, ValueError):
                    skor = 0.0
                if skor <= 0.05:
                    continue
                jumlah = dasar * skor * mult
                try:
                    n._emosi_naikkan(emosi, jumlah, alasan="dengar:" + tt)
                    emo_applied[emosi] = round(emo_applied.get(emosi, 0.0) + jumlah, 4)
                except Exception as _galat_diagnostik_112:
                    _diag.catat('naluri.Presentasi._dengar_efek',
                                "galat pada jalur fallback",
                                galat=_galat_diagnostik_112, jalur=112)
                    pass
        if emo_applied:
            efek["emosi"] = emo_applied
        # --- 3) rasa epistemik (pembaruan keyakinan ringan) ---
        ks = self._kes()
        if ks is not None:
            asertif = float(tindak.get("asertif", 0.0) or 0.0)
            tanya = float(tindak.get("pertanyaan", 0.0) or 0.0)
            try:
                if tanya >= 0.5:
                    ks.epistemic_emotion("penasaran", 0.15,
                                         sebab="mendengar pertanyaan")
                if asertif >= 0.5:
                    if dekat:
                        ks.epistemic_emotion(
                            "yakin", 0.12,
                            sebab="klaim dari orang yang dipercaya")
                    else:
                        ks.epistemic_emotion(
                            "bingung", 0.08,
                            sebab="klaim dari pembicara tidak akrab")
            except Exception as _galat_diagnostik_113:
                _diag.catat('naluri.Presentasi._dengar_efek',
                            "galat pada jalur fallback",
                            galat=_galat_diagnostik_113, jalur=113)
                pass
        if tindak:
            teratas = {k: round(float(v), 3)
                       for k, v in tindak.items()
                       if float(v or 0.0) > 0.05}
            if teratas:
                efek["tindak"] = teratas
        return efek

    def dengar(self, teks: str, dari: Any = None,
               konteks: Optional[Mapping[str, Any]] = None,
               **kwargs: Any) -> Dict[str, Any]:
        """Proses ujaran masuk serta catat pemisahan semantik/pragmatik."""
        if not self.enabled():
            return {}
        context = kwargs.get("context", konteks)
        ctx = dict(context) if isinstance(context, Mapping) else (
            {"situasi": str(context)} if context is not None else {})
        if dari is not None:
            try:
                ctx.setdefault("relasi", self._label_rel(dari))
                ctx.setdefault("shared_context", bool(self._kita(dari)))
            except Exception as _galat_diagnostik_100:
                _diag.catat('naluri.Presentasi.dengar', "galat pada jalur fallback", galat=_galat_diagnostik_100, jalur=100)
                pass
        self._pending_speaker = self._eid(dari)
        self._ucapan_terakhir = str(teks)[:160]
        # E3: topik adalah frasa nomina hasil pemahaman, bukan salinan
        # mentah teks lawan (teks[:80]); bila tak ada nomina bermakna,
        # biarkan None — jangan mengarang topik.
        try:
            from pycos.bahasa.teks import ekstrak_topik
            _leks = None
            _fn_eng = getattr(self, "tutur_engine", None)
            _eng = _fn_eng() if callable(_fn_eng) else None
            if _eng is not None:
                _leks = getattr(_eng, "leks", None)
            self._pending_topic = (ekstrak_topik(str(teks), None, _leks)
                                   or None)
        except Exception as _galat_diagnostik_117:
            _diag.catat('naluri.Presentasi.dengar',
                        "galat pada jalur fallback",
                        galat=_galat_diagnostik_117, jalur=117)
            self._pending_topic = None
        # D3: jenis kalimat tidak bergantung pada tanda baca akhir;
        # `tanya` tetap dipertahankan untuk kompatibilitas pemanggil lama.
        try:
            from pycos.bahasa.teks import jenis_kalimat
            tanya = jenis_kalimat(str(teks)) == "interogatif"
        except Exception as _galat_diagnostik_116:
            _diag.catat('naluri.Presentasi.dengar', "galat pada jalur fallback",
                        galat=_galat_diagnostik_116, jalur=116)
            tanya = str(teks).strip().endswith("?")
        ks = self._kes()
        if ks is not None:
            try:
                ks.attention_effort(teks, source="mendengar")
            except Exception as _galat_diagnostik_101:
                _diag.catat('naluri.Presentasi.dengar', "galat pada jalur fallback", galat=_galat_diagnostik_101, jalur=101)
                pass
            if dari is not None:
                try:
                    ks.dialogue_turn(self._eid(dari), teks)
                except Exception as _galat_diagnostik_102:
                    _diag.catat('naluri.Presentasi.dengar', "galat pada jalur fallback", galat=_galat_diagnostik_102, jalur=102)
                    pass
        analisis = self.analisis_sa_sp(teks, ctx, speaker=dari)
        # D8: ujaran yang didengar menggerakkan keadaan batin — drive lewat
        # impact_of, emosi/keyakinan lewat tindak tutur × relasi pembicara.
        efek = self._dengar_efek(teks, dari)
        self._boredom = max(0.0, self._boredom - self._p("presentasi_bosan_pulih"))
        # backchannel kadang muncul saat mendengarkan
        if self._rng.random() < 0.3:
            self.backchannel()
        hasil = {"topik": self._pending_topic, "dari": self._pending_speaker,
                 "pertanyaan": tanya}
        if efek:
            hasil["efek"] = efek
        if analisis and analisis.get("aktif") is not False:
            hasil["sa_sp"] = copy.deepcopy(analisis)
        return hasil

    def balas(self, dari: Any = None, topik: Optional[str] = None) -> Dict[str, Any]:
        """Balas ujaran terakhir (pakai topik tersimpan bila tidak diberi)."""
        topik = topik if topik is not None else self._pending_topic
        dari = dari if dari is not None else self._pending_speaker
        out = self.ucap(kepada=dari, topik=topik, masuk=True)
        self._pending_topic = None
        return out

    def backchannel(self, sinyal: Optional[str] = None) -> Dict[str, Any]:
        """Umpan balik singkat saat mendengarkan ('mmm', mengangguk, dsb.)."""
        if not self.enabled():
            return {}
        sinyal = sinyal or self._pick([
            "mengangguk pelan", "mengeluarkan suara 'mmm'", "mengangguk singkat",
            "mengalihkan berat badan", "menaikkan alis",
        ])
        ks = self._kes()
        if ks is not None:
            try:
                ks.backchannel(sinyal)
            except Exception as _galat_diagnostik_103:
                _diag.catat('naluri.Presentasi.backchannel', "galat pada jalur fallback", galat=_galat_diagnostik_103, jalur=103)
                pass
        entry = {"tick": self._tick(), "sinyal": sinyal}
        self._log(entry)
        return entry

    # ==================================================================
    # PERILAKU — idle, reaksi, adegan
    # ==================================================================
    def _update_boredom(self, idle: bool = True) -> float:
        """Akumulasikan kejenuhan karena repetisi/jeda, bukan drive saja."""
        curiosity_deficit = max(0.0, -self._lev("keingintahuan"))
        ks = self._kes()
        epistemic_boredom = 0.0
        if ks is not None:
            try:
                epistemic_boredom = float(ks.epistemic_emotions.get("bosan", 0.0))
            except Exception as _galat_diagnostik_104:
                _diag.catat('naluri.Presentasi._update_boredom', "galat pada jalur fallback", galat=_galat_diagnostik_104, jalur=104)
                epistemic_boredom = 0.0
        if idle:
            gain = max(0.0, self._p("presentasi_bosan_gain"))
            repetition = 0.12 if self._boredom_recent else 0.0
            silence = min(1.0, max(0.0, self._silence) /
                          max(1.0, self._p("presentasi_idle_ticks")))
            self._boredom = _kclip(
                self._boredom + gain * (0.55 + 0.45 * curiosity_deficit
                                        + 0.25 * silence + repetition), 0.0, 1.0)
            self._boredom = max(self._boredom, 0.55 * epistemic_boredom)
        else:
            self._boredom = max(0.0, self._boredom
                                - max(0.0, self._p("presentasi_bosan_pulih")))
        return _kclip(self._boredom, 0.0, 1.0)

    def boredom_state(self) -> Dict[str, Any]:
        return {"nilai": round(float(self._boredom), 3),
                "ambang": round(self._p("presentasi_bosan_ambang"), 3),
                "aksi_spontan": (copy.deepcopy(self._boredom_log[-1])
                                  if self._boredom_log else None),
                "jumlah_aksi": len(self._boredom_log),
                "aksi_terbaru": list(self._boredom_recent[-6:])}

    def _spontaneous_boredom_action(self, konteks: Optional[Mapping[str, Any]] = None
                                    ) -> Dict[str, Any]:
        """Kejenuhan memulai aksi berbeda dan dapat menjadi tujuan free_will."""
        actions = [
            ("mencari_pola", "menelusuri pola pada benda-benda di sekitarnya"),
            ("merumuskan_pertanyaan", "merumuskan pertanyaan baru yang belum ia tanyakan"),
            ("mencipta_permainan", "menciptakan aturan permainan kecil dari benda terdekat"),
            ("mencari_rute_baru", "mencoba jalur berbeda mengitari ruangan"),
            ("mengarang_metafora", "membayangkan benda biasa sebagai sesuatu yang ganjil"),
            ("menguji_irama", "mengetuk pola irama baru dengan jari"),
            ("merapikan_benda", "menata ulang benda-benda kecil dengan pola pilihannya sendiri"),
        ]
        recent = set(self._boredom_recent[-4:])
        options = [x for x in actions if x[0] not in recent] or actions
        action, desc = options[self._boredom_action_index % len(options)]
        self._boredom_action_index += 1
        target = ""
        if isinstance(konteks, Mapping):
            target = str(konteks.get("objek", konteks.get("object", "")) or "")[:80]
            if target:
                desc += f" menggunakan {target} sebagai bahan"
        ks = self._kes()
        playful = None
        aesthetic = None
        if ks is not None:
            if action == "mencipta_permainan":
                try:
                    playful = ks.playful_reframe(
                        target or "sebuah benda yang biasa",
                        "benda itu diam-diam menjadi wasit permainan semesta",
                        jenis="absurditas", intensitas=0.68)
                except Exception as _galat_diagnostik_105:
                    _diag.catat('naluri.Presentasi._spontaneous_boredom_action', "galat pada jalur fallback", galat=_galat_diagnostik_105, jalur=105)
                    playful = None
            elif action == "mengarang_metafora":
                try:
                    aesthetic = ks.aesthetic_response(
                        target or "bentuk dan bayangan di ruangan",
                        {"kebaruan": 0.76, "harmoni": 0.52}, jenis="metafora")
                except Exception as _galat_diagnostik_106:
                    _diag.catat('naluri.Presentasi._spontaneous_boredom_action', "galat pada jalur fallback", galat=_galat_diagnostik_106, jalur=106)
                    aesthetic = None
        free_goal = None
        if ks is not None:
            try:
                free_goal = ks.free_will_choose_goal(
                    desc, actions=[action],
                    reason="inisiatif pribadi saat suasana terasa berulang",
                    priority=0.62, endorsement=0.68, novelty=0.82,
                    value_alignment=0.55, autonomy=1.0)
            except Exception as _galat_diagnostik_107:
                _diag.catat('naluri.Presentasi._spontaneous_boredom_action', "galat pada jalur fallback", galat=_galat_diagnostik_107, jalur=107)
                free_goal = None
            try:
                ks.epistemic_emotion("penasaran", 0.18,
                                     "kebosanan memicu eksplorasi baru")
            except Exception as _galat_diagnostik_108:
                _diag.catat('naluri.Presentasi._spontaneous_boredom_action', "galat pada jalur fallback", galat=_galat_diagnostik_108, jalur=108)
                pass
            try:
                ks.submit(desc, salience=0.62, tag="kebosanan",
                          source="inisiatif_presentasi", kind="aksi_spontan",
                          detail={"aksi": action, "didorong_drive": False})
            except Exception as _galat_diagnostik_109:
                _diag.catat('naluri.Presentasi._spontaneous_boredom_action', "galat pada jalur fallback", galat=_galat_diagnostik_109, jalur=109)
                pass
        entry = {"tick": self._tick(), "aksi": action,
                 "deskripsi": desc, "tingkat_kebosanan": round(self._boredom, 3),
                 "inisiatif": "kebosanan_melahirkan_perilaku_baru",
                 "tujuan_free_will": (free_goal.get("goal", {}).get("id")
                                      if isinstance(free_goal, Mapping) else None)}
        if playful:
            entry["bingkai_permainan"] = copy.deepcopy(playful)
        if aesthetic:
            entry["respons_estetis"] = copy.deepcopy(aesthetic)
        self._boredom_log.append(copy.deepcopy(entry))
        cap = max(1, int(self._p("presentasi_bosan_riwayat_max")))
        self._boredom_log = self._boredom_log[-cap:]
        self._boredom_recent.append(action)
        self._boredom_recent = self._boredom_recent[-16:]
        self._boredom = max(0.0, self._boredom
                            - 0.72 * self._p("presentasi_bosan_pulih"))
        return entry

    def perilaku_idle(self, konteks: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
        """Perilaku saat jeda; kejenuhan dapat memulai perilaku yang belum ada."""
        if not self.enabled("idle"):
            return {}
        # RITUAL: kebiasaan utilitas-nol hanya muncul tanpa interaksi.
        ritual = getattr(self.naluri, "ritual", None)
        if ritual is not None and ritual.enabled():
            try:
                r = ritual.maybe_trigger("idle")
                if r:
                    entry = {"tick": self._tick(),
                             "deskripsi": r.get("deskripsi", ""),
                             "ritual": r.get("ritual"),
                             "arketipe": r.get("arketipe")}
                    self._log(entry)
                    return entry
            except Exception as _galat_diagnostik_110:
                _diag.catat('naluri.Presentasi.perilaku_idle', "galat pada jalur fallback", galat=_galat_diagnostik_110, jalur=110)
                pass
        boredom = self._update_boredom(idle=True)
        if boredom >= self._p("presentasi_bosan_ambang"):
            ks = self._kes()
            if ks is not None:
                try:
                    ks.epistemic_emotion("bosan", 0.16,
                                         "jeda berulang terasa terlalu serupa")
                except Exception as _galat_diagnostik_111:
                    _diag.catat('naluri.Presentasi.perilaku_idle', "galat pada jalur fallback", galat=_galat_diagnostik_111, jalur=111)
                    pass
            entry = self._spontaneous_boredom_action(konteks)
            self._log(entry)
            return entry
        penasaran = max(self._emosi("penasaran"),
                        float((getattr(self._kes(), "epistemic_emotions", {}) or {}).get(
                            "penasaran", 0.0)) if self._kes() is not None else 0.0)
        bosan = max(0.0, -self._lev("keingintahuan"), boredom)
        kesepian = self._moral("kesepian") + max(0.0, -self._lev("afiliasi"))
        lelah = self._felt("lelah") + max(0.0, -self._lev("energi"))
        pilihan: List[str] = []
        if penasaran > 0.35 or bosan > 0.35:
            pilihan += ["mengamati sekitar dengan kepala sedikit miring",
                        "menyentuh benda terdekat, menimbangnya",
                        "berjalan pelan menyusuri tepi ruangan"]
        if kesepian > 0.4:
            pilihan += ["menatap jauh ke arah keramaian",
                        "menghela napas, lalu menunduk"]
        if lelah > 0.5:
            pilihan += ["menyandarkan punggung ke dinding",
                        "memijat pelipis dengan dua jari"]
        if not pilihan:
            pilihan = ["berdiri tenang, sesekali mengalihkan pandangan",
                       "menyilangkan tangan, mengamati"]
        desc = self._pick(pilihan)
        quirk = self._quirk_gesture()
        if quirk and self._rng.random() < 0.3:
            desc += f"; {quirk}"
        entry = {"tick": self._tick(), "deskripsi": desc,
                 "tingkat_kebosanan": round(boredom, 3)}
        self._log(entry)
        return entry

    def reaksi(self, event: Any) -> Dict[str, Any]:
        """Terjemahkan peristiwa internal/eksternal menjadi reaksi terlihat.

        `event` boleh dict {"jenis": ..., "konten": ...} atau string bebas.
        """
        if not self.enabled():
            return {}
        jenis = ""
        konten = ""
        if isinstance(event, Mapping):
            jenis = str(event.get("jenis", event.get("kind", "")))
            konten = str(event.get("konten", event.get("content", "")))
        else:
            konten = str(event)
        low = (jenis + " " + konten).lower()
        reaksi = "menoleh"
        if any(k in low for k in ("bahaya", "api", "ancaman", "ignition")):
            reaksi = "tersentak, tubuh menegang sejenak"
        elif any(k in low for k in ("hilang", "duka", "grief", "mati")):
            reaksi = "membeku, lalu menutup mata"
        elif any(k in low for k in ("khianat", "betray", "dilanggar")):
            reaksi = "diam membatu, rahang mengeras"
        elif any(k in low for k in ("berhasil", "hadiah", "senang")):
            reaksi = "bahunya turun, tarikan napas lega"
        elif any(k in low for k in ("perhatian", "atensi", "penasaran")):
            reaksi = "kepala terangkat, mata menyapu"
        entry = {"tick": self._tick(), "jenis": jenis or "umum",
                 "konten": konten[:80], "reaksi": reaksi,
                 "nonverbal": self.nonverbal(None, None)}
        self._log(entry)
        return entry

    def adegan(self, kepada: Any = None, topik: Optional[str] = None,
               konteks: Optional[str] = None) -> Dict[str, Any]:
        """Satu denyut perilaku lengkap: ujaran + nonverbal + konteks + narasi."""
        if not self.enabled():
            return {}
        u = self.ucap(kepada=kepada, topik=topik or konteks)
        if u.get("act") == "diam" and not u.get("teks"):
            u["idle"] = self.perilaku_idle()
        return u

    # ==================================================================
    # NARASI PENGAMAT — perilaku → kalimat yang bisa dibaca pemain
    # ==================================================================
    def deskripsi(self, teks: str = "", nonverbal: Optional[Dict[str, Any]] = None,
                  act: Optional[str] = None, kepada: Any = None,
                  orang_ketiga: bool = True) -> str:
        """Rangkai deskripsi natural dari kanal-kanal yang ada."""
        nv = nonverbal if nonverbal is not None else self.nonverbal(kepada, act)
        nama = self.naluri.name or "Ia"
        subjek = nama if orang_ketiga else "aku"
        bagian: List[str] = []
        post = (nv.get("postur") or {}).get("deskripsi")
        gaze = (nv.get("tatapan") or {}).get("arah")
        wajah = (nv.get("ekspresi") or {}).get("wajah")
        napas = (nv.get("napas") or {}).get("deskripsi")
        gest = (nv.get("gestur") or {}).get("deskripsi")
        jarak = (nv.get("jarak") or {}).get("deskripsi")
        if post:
            bagian.append(post)
        if gaze:
            bagian.append(f"pandangan ke {gaze}")
        if wajah:
            bagian.append(wajah)
        if napas:
            bagian.append(napas)
        if gest:
            bagian.append(gest)
        if jarak and kepada is not None:
            bagian.append(jarak)
        fisis = "; ".join(bagian)
        if orang_ketiga:
            awalan = f"{subjek} {fisis}" if fisis else subjek
        else:
            awalan = f"{subjek} {fisis}" if fisis else subjek
        if teks:
            return f"{awalan}. Ia berkata, \"{teks}\""
        if act == "diam":
            return f"{awalan}. Ia tidak berkata apa-apa."
        return awalan + "."

    # ==================================================================
    # laporan & serialisasi
    # ==================================================================
    def _log(self, entry: Mapping[str, Any]) -> None:
        self._history.append(dict(entry))
        cap = int(self._p("presentasi_riwayat_max"))
        if cap > 0 and len(self._history) > cap:
            self._history = self._history[-cap:]

    def snapshot(self) -> Dict[str, Any]:
        """Keadaan presentasi JSON-safe untuk render/HUD/debug."""
        return {
            "aktif": self.enabled(),
            "nonverbal": self.nonverbal(None, self._last_act),
            "prosodi": self.prosodi(self._last_act),
            "act_terakhir": self._last_act,
            "sejak_bicara": int(self._silence),
            "mikro": self._micro,
            "fidget": round(self._fidget, 3),
            "ujaran_terakhir": (self._history[-1] if self._history else None),
            "denyut": self._act_counts,
            "tag_dialog": self.tag_dialog(),
            "indikator": self.indikator_psikologis(),
            "kebosanan": self.boredom_state(),
            "sa_sp": copy.deepcopy(self._sa_sp_last),
            "temporal": {"hadir": self._player_present,
                         "diam": int(self._idle_ticks),
                         "absen": int(self._absence_ticks)},
        }

    def hud_state(self, kepada: Any = None) -> Dict[str, Any]:
        """Potongan kompak untuk HUD: ekspresi, tatapan, ujaran, napas."""
        if not self.enabled():
            return {"aktif": False}
        return {
            "aktif": True,
            "tag_dialog": self.tag_dialog(),
            "indikator": self.indikator_psikologis(),
            "ekspresi": (self.ekspresi() or {}).get("wajah", ""),
            "tatapan": (self.tatapan(kepada) or {}).get("arah", ""),
            "napas": (self.napas() or {}).get("deskripsi", ""),
            "postur": (self.postur() or {}).get("deskripsi", ""),
            "ujaran": (self._history[-1].get("teks", "")
                       if self._history else ""),
            "act": self._last_act,
            "kebosanan": round(self._boredom, 3),
            "sa_sp": copy.deepcopy(self._sa_sp_last),
            "ritual": (getattr(self.naluri, "ritual", None).state()
                       if getattr(self.naluri, "ritual", None) is not None
                       and self.naluri.ritual.enabled() else None),
            "reputasi": self._reputasi_view(kepada),
        }

    def _reputasi_view(self, tentang: Any = None) -> Optional[Dict[str, Any]]:
        """Baca reputasi sosial dari KawananNPC (bila ada) — konsep 8."""
        kawanan = getattr(self.naluri, "kawanan", None)
        if kawanan is None or tentang is None:
            return None
        try:
            return kawanan.reputasi(tentang)
        except Exception as _galat_diagnostik_112:
            _diag.catat('naluri.Presentasi._reputasi_view', "galat pada jalur fallback", galat=_galat_diagnostik_112, jalur=112)
            return None

    def to_dict(self) -> Dict[str, Any]:
        st = self._rng.getstate()
        return {
            "format": "presentasi/1",
            "rng_state": [int(st[0]), [int(x) for x in st[1]], st[2]],
            "gaze": self._gaze,
            "posture": self._posture,
            "breath_phase": float(self._breath_phase),
            "breath_rate": float(self._breath_rate),
            "blink_in": float(self._blink_in),
            "micro": self._micro,
            "micro_ttl": float(self._micro_ttl),
            "fidget": float(self._fidget),
            "silence": float(self._silence),
            "last_act": self._last_act,
            "act_counts": {str(k): int(v) for k, v in self._act_counts.items()},
            "history": [dict(x) for x in self._history],
            "pending_topic": self._pending_topic,
            "pending_speaker": self._pending_speaker,
            "mood_carry": float(self._mood_carry),
            "recent_texts": list(self._recent_texts),
            "sa_sp_last": copy.deepcopy(self._sa_sp_last),
            "boredom": float(self._boredom),
            "boredom_action_index": int(self._boredom_action_index),
            "boredom_recent": list(self._boredom_recent[-16:]),
            "boredom_log": [copy.deepcopy(x) for x in self._boredom_log[-16:]],
            # kesadaran temporal (konsep 4)
            "player_present": bool(self._player_present),
            "idle_ticks": float(self._idle_ticks),
            "absence_ticks": float(self._absence_ticks),
            "last_seen_tick": int(self._last_seen_tick),
            "returned": bool(self._returned),
            "proaktif_terakhir": int(self._proaktif_terakhir),
            # kesalahan terkendali (konsep 5)
            "ragu_berubah": bool(self._ragu_berubah),
            "salah_ingat": dict(self._salah_ingat) if self._salah_ingat else None,
            # tells / hesitasi / linger
            "tell": dict(self._tell) if self._tell else None,
            "histeresis": {str(k): float(v) for k, v in self._histeresis.items()},
            "shift_dipakai": bool(self._shift_dipakai),
            "last_spotlight": self._last_spotlight,
            "last_conflict": int(self._last_conflict),
            "shift_seen_tick": int(self._shift_seen_tick),
        }

    def from_dict(self, data: Mapping[str, Any]) -> "Presentasi":
        from pycos.dukungan.validasi_state import validasi_state
        data = validasi_state(data, "Presentasi")
        if not isinstance(data, Mapping):
            return self
        self._gaze = data.get("gaze")
        self._posture = str(data.get("posture", "netral"))
        self._breath_phase = float(data.get("breath_phase", 0.0))
        self._breath_rate = float(data.get("breath_rate", 0.5))
        self._blink_in = float(data.get("blink_in", 3.0))
        self._micro = data.get("micro")
        self._micro_ttl = float(data.get("micro_ttl", 0.0))
        self._fidget = float(data.get("fidget", 0.0))
        self._silence = float(data.get("silence", 0.0))
        self._last_act = data.get("last_act")
        self._act_counts = {str(k): int(v) for k, v in
                            (data.get("act_counts") or {}).items()}
        self._history = [dict(x) for x in (data.get("history") or [])]
        self._pending_topic = data.get("pending_topic")
        self._pending_speaker = data.get("pending_speaker")
        self._mood_carry = float(data.get("mood_carry", 0.0))
        self._recent_texts = [str(x) for x in (data.get("recent_texts") or [])][-6:]
        ss = data.get("sa_sp_last")
        self._sa_sp_last = copy.deepcopy(dict(ss)) if isinstance(ss, Mapping) else None
        self._sa_sp_analyzer = None
        self._boredom = _kclip(data.get("boredom", 0.0), 0.0, 1.0)
        self._boredom_action_index = max(0, int(data.get("boredom_action_index", 0)))
        self._boredom_recent = [str(x) for x in
                                (data.get("boredom_recent") or [])][-16:]
        self._boredom_log = [copy.deepcopy(x) for x in
                             (data.get("boredom_log") or [])[-16:]]
        self._player_present = bool(data.get("player_present", False))
        self._idle_ticks = float(data.get("idle_ticks", 0.0))
        self._absence_ticks = float(data.get("absence_ticks", 0.0))
        self._last_seen_tick = int(data.get("last_seen_tick", -10_000))
        self._returned = bool(data.get("returned", False))
        self._proaktif_terakhir = int(data.get("proaktif_terakhir", -10_000))
        self._ragu_berubah = bool(data.get("ragu_berubah", False))
        si = data.get("salah_ingat")
        self._salah_ingat = dict(si) if isinstance(si, Mapping) else None
        tl = data.get("tell")
        self._tell = dict(tl) if isinstance(tl, Mapping) else None
        self._histeresis = {str(k): float(v) for k, v in
                            (data.get("histeresis") or {}).items()}
        self._shift_dipakai = bool(data.get("shift_dipakai", False))
        self._last_spotlight = data.get("last_spotlight")
        self._last_conflict = int(data.get("last_conflict", 0))
        self._shift_seen_tick = int(data.get("shift_seen_tick", -10_000))
        rs = data.get("rng_state")
        if rs and len(rs) == 3 and rs[1]:
            try:
                self._rng.setstate((int(rs[0]),
                                    tuple(int(x) for x in rs[1]), rs[2]))
            except (ValueError, TypeError):
                pass
        return self


Presentasi.__module__ = "pycos.inti.naluri"
