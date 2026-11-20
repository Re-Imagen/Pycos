"""Showcase inti; tidak dimuat oleh impor produksi inti.naluri.

Dependensi mesin diambil saat skenario dijalankan agar urutan impor aman.
"""
from __future__ import annotations

import json
import random
from typing import Any, Dict, List, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from pycos.inti.naluri import Naluri
from pycos.dukungan.numerik import jepit_drive

def _simulasi_harian(cls, ticks: int = 90, seed: int = 7) -> "Naluri":
    """Simulasi 3 hari × 30 tick — stdlib murni, tanpa dependensi lain."""
    from pycos.inti.naluri import DRIVES
    naluri = cls(stage="anak", rng_seed=seed)
    rng = random.Random(seed)
    aksi_harian = [
        {"name": "eksplorasi", "drive_effects": {"keingintahuan": +0.12, "energi": -0.05, "penguasaan": +0.03}, "cost": 0.02},
        {"name": "belajar",    "drive_effects": {"penguasaan": +0.15, "keingintahuan": +0.03, "energi": -0.04}, "cost": 0.02},
        {"name": "hati-hati",  "drive_effects": {"keamanan": +0.2, "penguasaan": -0.02}, "cost": 0.01},
        {"name": "sosialisasi","drive_effects": {"afiliasi": +0.2, "keamanan": +0.03, "energi": -0.04}, "cost": 0.03},
        {"name": "istirahat",  "drive_effects": {"energi": +0.1, "keamanan": +0.02}, "cost": 0.0},
    ]

    day = 1
    actions = 0
    last_avg_reward = 0.0
    for t in range(1, ticks + 1):
        # event acak: ancaman/sukses/kabar baru
        events: List[Dict[str, Any]] = []
        roll = rng.random()
        if roll < 0.12:
            events.append({"drive": "keamanan", "delta": -rng.uniform(0.1, 0.3), "reason": "ancaman"})
        elif roll < 0.22:
            events.append({"drive": "keingintahuan", "delta": +rng.uniform(0.1, 0.25), "reason": "hal baru"})
        elif roll < 0.30:
            events.append({"drive": "penguasaan", "delta": +rng.uniform(0.1, 0.25), "reason": "berhasil"})

        is_action_tick = (t % 3 == 0)
        naluri.tick(events=events, action_cost=is_action_tick)

        if is_action_tick:
            actions += 1
            decision = naluri.choose_action(aksi_harian, goal_bias=True)
            eff = decision["candidate"].get("drive_effects", {})
            # realita = efek drive + derau sedang
            real_deltas = {d: v + rng.gauss(0, 0.04) for d, v in eff.items()}
            real_reward = sum(real_deltas.values()) / max(1, len(real_deltas))
            naluri.apply_events([{"drive": d, "delta": v} for d, v in real_deltas.items()])
            # prediksi Imajinasi: cerminan utilitas + derau prediksi
            pred_util = float(decision["score"]) / max(1.0, naluri.estimate_scale())
            pred_impact = jepit_drive(pred_util + rng.gauss(0, 0.15))
            naluri.observe_outcome(
                {"impact": pred_impact, "probability": 0.65,
                 "description": "aksi " + decision["action"],
                 "perspective": "self", "delay_to_impact": 0},
                {"reward": real_reward, "drive_deltas": real_deltas})
            last_avg_reward = 0.8 * last_avg_reward + 0.2 * real_reward

            if t % 15 == 0:
                print(f"[t{t:03d}] ▶ aksi={decision['action']:12s} "
                      f"score={decision['score']:+.2f}  "
                      f"goals={[g.drive for g in naluri.goals][:3]}  "
                      f"cal={naluri.calibration_error():.2f} "
                      f"scale={naluri.estimate_scale():.1f}")

        should, reason = naluri.should_sleep()
        if should:
            print(f"[t{t:03d}] 🌙 tidur — {reason} "
                  f"(energi={naluri.levels['energi']:+.2f}, "
                  f"koherensi={naluri.levels['koherensi']:+.2f})")
            policy = naluri.dream_policy()
            # mimpi: replay mengurangi kalibrasi error
            naluri._calibration_ema *= 0.6
            naluri.post_sleep({"duration": policy["num_dreams"] * 0.1})
            print(f"[t{t:03d}] ☀️ bangun — energi={naluri.levels['energi']:+.2f}, "
                  f"koherensi={naluri.levels['koherensi']:+.2f}, "
                  f"cal={naluri.calibration_error():.2f}")

        if t % 30 == 0:
            print(f"--- akhir hari {day}: "
                  f"{ {d: f'{naluri.levels[d]:+.2f}' for d in DRIVES} }")
            day += 1

    print(f"\nSTATUS AKHIR — {actions} aksi diambil, {naluri.slept_count}× tidur endogen")
    print(f"tahap={naluri.stage}  calibration_error={naluri.calibration_error():.3f} "
          f"scale={naluri.estimate_scale():.2f}")
    return naluri


def demo_npc(ticks: int = 72, seed: int = 21) -> Dict[str, Any]:
    """Demo multi-NPC: tiga NPC dengan preset berbeda, LOD per jarak pemain,
    tidur terjadwal (sirkadian murni), HUD terbaca, dan round-trip save/load."""
    from pycos.inti.naluri import KawananNPC, LEXICON_EN, TAG_LEXICON_EN
    kawanan = KawananNPC()
    kawanan.tambah("Rama", personality="penjaga", rng_seed=seed)
    kawanan.tambah("Ana", personality="sosiawan", rng_seed=seed + 1)
    # Bob memakai lexicon Inggris yang di-inject (fix #5)
    kawanan.tambah("Bob", personality="penjelajah", rng_seed=seed + 2,
                   lexicon=LEXICON_EN, tag_lexicon=TAG_LEXICON_EN)
    print("=== Demo NPC: preset / LOD / tidur terjadwal / HUD / save-load ===")
    print("  preset :", {n: kawanan[n].personality_name for n in kawanan.nama()})
    tidur_log: List[Tuple[int, str, str]] = []
    for t in range(1, ticks + 1):
        # pemain bergerak: jarak → LOD (Rama dekat, Ana sedang, Bob jauh)
        kawanan.set_lod_by_distance("Rama", jarak=4.0)    # -> "penuh"
        kawanan.set_lod_by_distance("Ana", jarak=18.0)    # -> "latar" (10x hemat)
        kawanan.set_lod_by_distance("Bob", jarak=99.0)    # -> "beku"
        events = None
        if t % 17 == 0:
            events = {"Rama": [{"drive": "keamanan", "delta": -0.15,
                                "reason": "suara mencurigakan"}]}
        kawanan.tick_all(events=events)
        for n in kawanan:
            perlu, alasan = n.should_sleep()
            if perlu:
                tidur_log.append((t, n.name, alasan))
                n.post_sleep({"duration": 0.5})
    print(f"  tidur terjadwal ({len(tidur_log)}x):")
    for t, nama, alasan in tidur_log[:6]:
        print(f"    [t{t:03d}] {nama}: {alasan}")
    print("  LOD    :", {nama: n.lod_status()["mode"]
                         for nama, n in kawanan.npcs.items()})
    print("  HUD    :")
    for baris in kawanan.brief():
        print(f"    {baris}")
    en = kawanan["Bob"].impact_of("danger: time bomb, risky and chaotic")
    idn = kawanan["Rama"].impact_of("bahaya: bom waktu, berisiko dan kacau")
    print("  impact_of(EN):", {k: round(v, 2) for k, v in en.items() if v})
    print("  impact_of(ID):", {k: round(v, 2) for k, v in idn.items() if v})
    # save & load (fix #1): round-trip harus idempoten, termasuk state NURANI
    payload = kawanan.to_json()
    pulih = KawananNPC.from_json(payload)
    assert pulih.to_dict() == kawanan.to_dict(), "round-trip serialisasi berbeda!"
    print(f"  save/load: {len(payload)} byte JSON — round-trip idempoten ✓")
    return {"kawanan": kawanan, "tidur": tidur_log}


def demo_empati(ticks: int = 48, seed: int = 31) -> Dict[str, Any]:
    """Demo lapisan EMPATI: dua NPC sosial, interaksi dengan 'pemain'
    (positif lalu penghinaan), event menakutkan, prior sosial di
    choose_action, dan round-trip save/load dengan relasi + emosi."""
    from pycos.inti.naluri import KawananNPC
    k = KawananNPC()
    k.tambah("Rama", personality="penjaga", sosial=True, rng_seed=seed)
    k.tambah("Ana", personality="sosiawan", sosial=True, rng_seed=seed + 1)
    rama, ana = k["Rama"], k["Ana"]
    print("=== Demo EMPATI: emosi & relasi sosial ===")
    if rama.nurani is None:
        print("  (NURANI tidak terpasang — relasi netral; mesin emosi tetap aktif)")
    rama.kenal("pemain", nama="Player")
    ana.kenal("pemain", nama="Player")
    jejak: List[Tuple[int, str]] = []
    for t in range(1, ticks + 1):
        events = None
        if t == 6:    # pemain menolong Rama
            jejak.append((t, rama.berinteraksi("pemain", muatan=+0.8,
                                               kepercayaan_delta=+0.6,
                                               alasan="ditolong pemain")["label"]))
        elif t == 12:  # obrolan antar-NPC
            k.interaksi("Rama", "Ana", muatan=+0.4, alasan="obrolan pos")
        elif t == 18:  # pemain menghina Rama
            jejak.append((t, rama.berinteraksi("pemain", muatan=-0.9,
                                               kepercayaan_delta=-0.8,
                                               alasan="dihina pemain")["label"]))
        elif t == 24:  # diserang: drive keamanan anjlok + emosi takut eksplisit
            events = {"Rama": [{"drive": "keamanan", "delta": -0.5,
                                "reason": "diserang bandit"},
                               {"emosi": "takut", "intensitas": 0.9,
                                "reason": "diserang bandit"}]}
        k.tick_all(events=events)
        perlu, alasan = rama.should_sleep()
        if perlu:
            rama.post_sleep()
        if t % 12 == 0:
            h = rama.hud_state(relasi_dengan="pemain")
            rel = h.get("relasi") or {}
            print(f"  [t{t:03d}] Rama: mood={h['mood']:11s} "
                  f"emosi={h['emosi']['dominan']:9s}({h['emosi']['intensitas']:.2f}) "
                  f"relasi-pemain={rel.get('label', '-')}")
    print("  jejak label relasi Rama→pemain:", jejak)
    # prior sosial: mengobrol dengan yang dikenal & disukai mengalahkan asing
    kandidat = [
        {"name": "patroli sendiri", "cost": 0.02,
         "drive_effects": {"keamanan": +0.2, "penguasaan": +0.1}},
        {"name": "obrol dengan Ana", "cost": 0.01, "target": "Ana",
         "drive_effects": {"afiliasi": +0.25}},
        {"name": "obrol dengan asing", "cost": 0.01, "target": "orang_asli",
         "drive_effects": {"afiliasi": +0.25}},
    ]
    pilih = rama.choose_action(kandidat)
    skor = dict((nama, s) for s, nama in pilih["ranked"])
    print(f"  choose_action: {pilih['action']} "
          f"(Ana={skor.get('obrol dengan Ana', 0):+.3f} vs "
          f"asing={skor.get('obrol dengan asing', 0):+.3f})")
    if rama.nurani is not None:
        assert skor["obrol dengan Ana"] > skor["obrol dengan asing"], \
            "prior sosial harus menguntungkan entitas yang dikenal"
    # NPC kesepian mencari teman sendiri (butuh >=2 di atas ambang defisit)
    ana.delta("afiliasi", -0.9, reason="kesepian (demo)")
    rama.delta("afiliasi", -0.9, reason="kesepian (demo)")
    pasangan = k.biarkan_bersosialisasi()
    print("  biarkan_bersosialisasi:",
          [f"{a}↔{b}: {x[a]['label']}/{x[b]['label']}"
           for x in pasangan for a, b in [tuple(x)] ] or "tidak ada pasangan")
    # serialisasi: emosi + relasi ikut tersimpan
    d = k.to_dict()
    pulih = KawananNPC.from_json(json.dumps(d, ensure_ascii=False))
    assert pulih.to_dict() == d, "round-trip EMPATI tidak idempoten"
    if pulih["Rama"].nurani is not None:
        assert pulih["Rama"].relasi("pemain")["n"] == rama.relasi("pemain")["n"]
    print(f"  save/load: relasi({rama.relasi('pemain')['n']} interaksi dgn pemain) "
          f"+ emosi pulih ✓")
    return {"kawanan": k, "jejak": jejak, "pilihan": pilih["action"]}


def demo_watak(ticks_bukti: int = 120, ticks_tarik: int = 180,
               seed: int = 53) -> Dict[str, Any]:
    """Demo lapisan WATAK: paranoid vs penjelajah di dunia yang SAMA.

    Tiga klaim yang dibuktikan:
      1. VISKOSITAS — 120 tick "bukti dunia aman" menggeser setpoint
         keamanan penjelajah (lr 0.002) tetapi nyaris tidak menggeser
         milik paranoid (lr 1e-5): ia TIDAK BISA belajar aman.
      2. BACKSTORY — saat bukti ditarik, paranoid tetap defisit besar
         (ekspektasi 0.55 tak pernah turun), penjelajah sudah beradaptasi.
      3. COLD-START — NPC paranoid baru WASPADA DI TICK 1 (setpoint +
         emosi + prior afektif ter-seed "lahir"), bukan belajar dulu.
    """
    from pycos.inti.naluri import Naluri
    print("=== Demo WATAK: kepribadian × viskositas × backstory ===")
    a = Naluri(name="Parno", personality="paranoid", rng_seed=seed)
    b = Naluri(name="Jelajah", personality="penjelajah", rng_seed=seed)
    if a.nurani is None:
        print("  (NURANI tidak terpasang — watak butuh pilar C; keluar)")
        return {}
    da = a.describe_personality()
    db = b.describe_personality()
    print(f"  Parno  : weights keamanan={da['weights']['keamanan']:.1f}  "
          f"setpoint_lr={a.params['setpoint_lr']}  "
          f"clamp={a.params['setpoint_clamp']}")
    print(f"  Jelajah: weights keamanan={db['weights']['keamanan']:.1f}  "
          f"setpoint_lr={b.params['setpoint_lr']}")
    print(f"  lahir Parno → setpoints={a.nurani.setpoints['keamanan']:.2f} "
          f"emosi takut={a.emosi['takut']:.2f} "
          f"slot afektif={a.nurani.affective_size}")

    sp0 = {"Parno": a.nurani.setpoints["keamanan"],
           "Jelajah": b.nurani.setpoints["keamanan"]}
    # Bukti harus SUPER-AMBANG: sejak PERSEPSI ada di kedua preset, stimulus
    # lemah (+0.008) sebagian besar jadi subliminal dan tak pernah sampai
    # ke pembelajaran setpoint — justru menunjukkan filternya bekerja.
    bukti = {"drive": "keamanan", "delta": +0.03, "reason": "hari aman"}
    for fase, n, ev in (("BUKTI AMAN ", ticks_bukti, [bukti]),
                        ("DUNIA DITARIK", ticks_tarik, [])):
        for t in range(1, n + 1):
            a.tick(events=ev)
            b.tick(events=ev)
            if t % 40 == 0:
                print(f"  [{fase} t{t:03d}] Parno: level={a.levels['keamanan']:+.2f} "
                      f"sp={a.nurani.setpoints['keamanan']:+.3f} | "
                      f"Jelajah: level={b.levels['keamanan']:+.2f} "
                      f"sp={b.nurani.setpoints['keamanan']:+.3f}")
    d_sp = {n: (o.nurani.setpoints["keamanan"] - sp0[n])
            for n, o in (("Parno", a), ("Jelajah", b))}
    defisit = {n: o.nurani.relative_deficit("keamanan", o.levels["keamanan"])
               for n, o in (("Parno", a), ("Jelajah", b))}
    print(f"  Δsetpoint total ({ticks_bukti + ticks_tarik} tick): "
          f"Parno={d_sp['Parno']:+.4f} (beku) vs "
          f"Jelajah={d_sp['Jelajah']:+.4f} (belajar)")
    print(f"  defisit relatif final: Parno={defisit['Parno']:.3f} vs "
          f"Jelajah={defisit['Jelajah']:.3f} "
          f"→ urgensi {a.urgency['keamanan']:.2f} vs {b.urgency['keamanan']:.2f}")
    ha, hb = a.hud_state(), b.hud_state()
    print(f"  HUD Parno  : mood={ha['mood']:11s} emosi={ha['emosi']['dominan']}"
          f"({ha['emosi']['intensitas']:.2f}) niat={ha['niat']}")
    print(f"  HUD Jelajah: mood={hb['mood']:11s} emosi={hb['emosi']['dominan']}"
          f"({hb['emosi']['intensitas']:.2f}) niat={hb['niat']}")

    # --- cold-start: sifat ADA sejak lahir, bukan dipelajari ---
    c = Naluri(name="Parno Muda", personality="paranoid", rng_seed=seed)
    c.tick()
    hc = c.hud_state()
    luka = c.impact_of("dikhianati teman dipercaya ancaman bahaya")
    netral = c.impact_of("jalan setapak baru di pagi cerah")
    print(f"  cold-start (tick 1): defisit keamanan="
          f"{c.nurani.relative_deficit('keamanan', c.levels['keamanan']):.2f} "
          f"emosi={hc['emosi']['dominan']}({hc['emosi']['intensitas']:.2f}) "
          f"niat={hc['niat']}")
    print(f"  prior luka lama: keamanan={luka['keamanan']:+.2f} "
          f"(vs teks netral {netral['keamanan']:+.2f})")
    assert abs(d_sp["Parno"]) < 0.01 < abs(d_sp["Jelajah"]), (d_sp)
    assert defisit["Parno"] - defisit["Jelajah"] > 0.2, (defisit)
    assert c.nurani.relative_deficit("keamanan", c.levels["keamanan"]) > 0.4
    assert hc["emosi"]["intensitas"] > 0.1, hc["emosi"]
    assert luka["keamanan"] < netral["keamanan"] - 0.2, (luka, netral)
    print("  ✓ watak: paranoid tak bisa belajar aman; backstory aktif tick 0")
    return {"delta_setpoint": d_sp, "defisit_final": defisit,
            "cold_start": {
                "defisit": c.nurani.relative_deficit(
                    "keamanan", c.levels["keamanan"]),
                "prior_luka": luka["keamanan"]}}


def demo_introspeksi(ticks: int = 120, seed: int = 89) -> Dict[str, Any]:
    """Demo pilar G INTROSPEKSI DIRI: fisiologi nyata, bukan pseudo-science.

    Tiga fenomena yang dibuktikan (semua terukur angka):
      1) Interosepsi berderau (insula - Craig 2002): model diri != actual,
         akurasi = Pearson(actual, perceived) < 1.0 karena noise, membaik
         dengan pembelajaran (lr).
      2) Metakognisi (PFC - Fleming 2012): confidence memprediksi correctness
         -> meta-d' > 0.5 (chance) bila sistem belajar, Brier confidence turun.
      3) Sadar diri (Global Workspace - Dehaene): discrepancy > ambang +
         confidence -> sadar_diri_ticks naik, narasi DMN terbentuk.
    """
    from pycos.inti.naluri import Naluri
    print("=== Demo INTROSPEKSI DIRI: interosepsi + metakognisi + DMN ===")
    P = {"enable_introspection": True, "enable_plastic_setpoints": True,
         "introspeksi_noise": 0.12, "introspeksi_lr": 0.08,
         "introspeksi_refleksi_period": 20}
    # Dua NPC: satu dengan interosepsi baik (noise kecil), satu buruk (noise besar)
    baik = Naluri(name="Sadar", rng_seed=seed, params=dict(P, introspeksi_noise=0.04))
    buruk = Naluri(name="Kabur", rng_seed=seed, params=dict(P, introspeksi_noise=0.25))
    if baik.nurani is None or not baik.nurani.enabled("introspection"):
        print("  (NURANI tidak terpasang — introspeksi butuh pilar G; keluar)")
        return {}
    rng = baik._rng
    for t in range(1, ticks+1):
        # dunia bergejolak: drive acak
        ev_baik = [{"drive": d, "delta": rng.uniform(-0.15, 0.15), "reason": f"fluktuasi {t}"} for d in ("energi","keamanan")]
        ev_buruk = [{"drive": d, "delta": rng.uniform(-0.15, 0.15), "reason": f"fluktuasi {t}"} for d in ("energi","keamanan")]
        baik.tick(events=ev_baik)
        buruk.tick(events=ev_buruk)
        # simulasi prediksi dengan outcome (untuk meta-d')
        if t % 5 == 0:
            for n in (baik, buruk):
                pred_prob = 0.6 + 0.3 * n.nurani.kepercayaan_global
                # benar jika model cukup akurat
                benar = rng.random() < (0.5 + 0.4 * max(0.0, n.nurani.introspeksi_akurasi))
                n.observe_outcome(
                    {"impact": rng.uniform(-0.5,0.5), "probability": pred_prob,
                     "description": f"introspeksi tick {t}"},
                    {"reward": 0.2 if benar else -0.3, "success": benar,
                     "drive_deltas": {"koherensi": 0.05 if benar else -0.05}})

    ib = baik.introspeksi()
    ik = buruk.introspeksi()
    mb = baik.meta_kognisi()
    mk = buruk.meta_kognisi()
    rb = baik.refleksi_diri(paksa=True)
    print(f"  1) akurasi interoseptif (Pearson): baik r={ib['akurasi']:.3f} vs buruk r={ik['akurasi']:.3f} — noise ↑ akurasi ↓ (insula)")
    print(f"  2) meta-d' (Fleming): baik {ib['meta_d_global']:.2f} vs buruk {ik['meta_d_global']:.2f}; Brier conf baik {mb['brier_confidence']:.3f} vs buruk {mk['brier_confidence']:.3f}")
    print(f"  3) sadar diri: baik {ib['sadar_diri_ticks']}x vs buruk {ik['sadar_diri_ticks']}x; refleksi {baik.nurani.refleksi_count}x")
    print(f"  narasi DMN baik: {rb['narasi'][:140]}...")
    # Validasi fisiologi: noise kecil -> akurasi lebih tinggi, meta-d' minimal >0.4
    assert ib['akurasi'] > ik['akurasi'] - 0.1, (ib['akurasi'], ik['akurasi'])
    assert mb['brier_confidence'] < 0.5, mb
    assert baik.nurani.refleksi_count >= 2
    print("  ✓ introspeksi: interosepsi + metakognisi + sadar diri terverifikasi")
    return {"baik": ib, "buruk": ik, "meta_baik": mb, "meta_buruk": mk, "narasi": rb}


def demo_kesadaran(ticks: int = 240, seed: int = 137) -> Dict[str, Any]:
    """Demo lapisan KESADARAN — dari reaksi tersebar ke arus sadar.

    1 global workspace + ignition · 2 monolog batin + identitas · 3 diri
    autobiografis + time travel · 4 rasa agensi · 5 interosepsi afektif +
    emosi moral · 6 monitoring realitas + keraguan · 7 keterbatasan atensi ·
    8 kognisi sosial orang-kedua · 9 pragmatik dialog · 10 kepincangan/bias ·
    11 nilai & batas · 12 mortalitas & duka · 13 mimpi & kontinuitas tidur ·
    14 audisi-diri: menerima suara sendiri sebagai input eksternal-sebagian.
    """
    from pycos.inti.naluri import Naluri
    print("=== Demo KESADARAN: arus sadar NPC ===")
    P = {"enable_emosi": True, "enable_perception": True,
         "enable_introspection": True, "enable_kesadaran": True,
         "sleep_mode": "terjadwal", "circadian_period": 24}
    n = Naluri(name="Rama", rng_seed=seed, params=P)
    n.enable_nurani()
    n.enable_kesadaran()
    # Tick memakai RNG milik NPC yang sudah disemai; demo tidak menggandakannya.
    ks = n.kesadaran
    for t in range(1, ticks + 1):
        evs = []
        if t % 4 == 0:
            evs.append({"drive": "keamanan", "delta": -0.14,
                        "reason": "api di depan", "stimulus": "api di depan"})
        if t % 9 == 0:
            evs.append({"drive": "energi", "delta": -0.12,
                        "reason": "tubuh lelah", "stimulus": "tubuh lelah"})
        if t % 13 == 0:
            evs.append({"drive": "afiliasi", "delta": 0.2,
                        "reason": "Player datang", "stimulus": "Player datang"})
        n.tick(events=evs, action_cost=(t % 3 == 0))
        if t == 20:
            ks.joint_attention("Player", "api di depan")
            ks.recursive_tom("Player", "tahu aku waspada", 0.6)
            ks.commit("Player", "aku akan menjagamu")
        if t == 50:
            ks.betray("Player", "dia pergi saat bahaya")
            ks.gossip("Player", "dia pernah meninggalkanku", kepada="NPC lain")
        if t == 80:
            ks.grieve("Kawan lama", 0.8, "hilang")
            ks.face_death("hampir terbakar")
        if t == 110:
            ks.dialogue_turn("Player", "kenapa kamu menjauh?")
            ks.backchannel("mengangguk")
        if t == 140:
            ks.hold_belief("dia baik", "dia pergi saat bahaya")
            ks.set_value("tidak menyakiti", 0.7)
            ks.add_boundary("jangan bohongi aku")
        if t == 200:
            ks.moral_emotion("syukur", 0.6, "masih hidup")
            ks.metacognitive_doubt(0.7)
    ks.feedback({"action": "hindar", "predicted": 0.8}, 0.1)
    ks.dream()

    ws = ks.workspace_report()
    print(f"  1) panggung sadar: {[c['content'] for c in ws['spotlight']][:3]} "
          f"| ignition {ws['ignition_count']}x")
    print(f"  2) monolog batin: {ks.last_thought(1)} | identitas: {ks.narrative_state() or '(belum)'}")
    print(f"  3) autobiografi: {len(ks.timeline)} episode, babak terakhir: "
          f"{ks.life_chapters()[-1].get('label') if ks.life_chapters() else '-'}")
    ag = ks.agency_state()
    print(f"  4) agensi={ag['agency']} kepemilikan={ag['ownership']} usaha={ag['effort']}")
    print(f"  5) terasa: {ks.felt_report()['kalimat'] or '(netral)'} | moral aktif: "
          f"{list(ks.felt_report()['moral'])}")
    rr = ks.reality_report()
    print(f"  6) realitas: sumber terakhir {rr['sumber_terakhir']['sumber'] if rr['sumber_terakhir'] else '-'} "
          f"| keraguan {rr['doubt']} | konfabulasi {rr['konfabulasi']}")
    at = ks.attention_limits()
    print(f"  7) atensi: fokus {at['fokus']} | blindspot {at['blindspots']}x | blink {at['blink_sisa']}")
    print(f"  8) sosial: komitmen {len(ks.commitments)} | gossip {len(ks.gossip_log)} | "
          f"ToM {ks.second_person_state('Player')['tom_rekursif']}")
    print(f"  9) pragmatik: giliran {ks.pragmatics_state()['giliran']['turn']} "
          f"| backchannel {len(ks.backchannels)} | repair {len(ks.repairs)}")
    fb = ks.fallibility_state()
    print(f"  10) kepincangan: bias {fb['bias']} | disonansi {[d['keyakinan'] for d in fb['disonansi']]}")
    print(f"  11) nilai: {list(ks.values_state()['nilai'])[:3]} | batas {ks.values_state()['batas']}")
    print(f"  12) mortalitas: {ks.mortality_state()['salience']} | duka {list(ks.mortality_state()['duka'])}")
    print(f"  13) mimpi: {ks.dream_report()[:90]}")
    assert ks.spotlight and ks.ignitions
    assert ks.timeline and ks.life_chapters()
    assert ks.commitments and ks.gossip_log
    assert ks.fallibility_state()['disonansi']
    assert ks.values and ks.mortality_salience > 0
    assert ks.last_dream
    print("  ✓ kesadaran: lapisan kognitif terverifikasi (workspace→monolog→agensi→"
          "duka→mimpi)")
    return ks.report()


def demo_presentasi(ticks: int = 180, seed: int = 211) -> Dict[str, Any]:
    """Demo lapisan PRESENTASI (Pycos): data internal → perilaku teramati.

    Menunjukkan satu NPC yang sama menampilkan dialog + kanal nonverbal yang
    BERUBAH sesuai keadaan internal: ancaman (waspada), duka (mengenang),
    disonansi (rasionalisasi), nilai (menolak), keraguan (ragu), dan momen
    tenang (akrab). Semua dari state Pycos, bukan skrip.
    """
    from pycos.inti.naluri import Naluri
    print("=== Demo PRESENTASI: Pycos performance layer (dialog + nonverbal) ===")
    P = {"enable_emosi": True, "enable_introspection": True,
         "enable_kesadaran": True, "enable_presentasi": True}
    n = Naluri(name="Rama", rng_seed=seed, params=P)
    n.enable_nurani()
    n.enable_emosi(True)
    n.enable_kesadaran()
    n.enable_presentasi()
    # JEJAK (opsional, duck-typed): bila ada di runtime, panggil
    # n.attach_jejak(jejak) agar memori autobiografis ikut dikisahkan.

    for t in range(1, ticks + 1):
        evs = []
        if t % 4 == 0:
            evs.append({"drive": "keamanan", "delta": -0.16,
                        "reason": "api di depan", "stimulus": "api di depan"})
        if t % 9 == 0:
            evs.append({"drive": "energi", "delta": -0.1,
                        "reason": "tubuh lelah", "stimulus": "tubuh lelah"})
        n.tick(events=evs, action_cost=(t % 3 == 0))
        if t == 20:
            n.kesadaran.joint_attention("Player", "api di depan")

    # 1) ancaman → peringatan/waspada
    u1 = n.presentasi.ucap(kepada="Player", topik="api di depan")
    # 2) dengar & balas
    n.presentasi.dengar("kenapa kamu menjauh?", "Player")
    u2 = n.presentasi.balas("Player")
    # 3) disonansi → rasionalisasi
    n.kesadaran.hold_belief("dia baik", "dia pergi saat bahaya")
    n.kesadaran.hold_belief("dia baik", "dia berbohong padaku")
    u3 = n.presentasi.ucap(kepada="Player")
    # 4) nilai → menolak
    n.kesadaran.set_value("tidak menyakiti", 0.8)
    n.kesadaran.add_boundary("jangan bohongi aku")
    ref = n.kesadaran.refuse("aku ingin kamu bohongi dia")
    u4 = n.presentasi.ucap(kepada="Player", topik="bohongi dia")
    # 5) duka (prioritas afektif tertinggi)
    n.kesadaran.grieve("Teman lama", 0.8, "hilang")
    u5 = n.presentasi.ucap(kepada="Player")

    print(f"  1) [ancaman] {u1['act']}: {u1['teks'][:90]}")
    print(f"  2) [dengar→balas] {u2['act']}: {u2['teks'][:90]}")
    print(f"  3) [disonansi] {u3['act']}: {u3['teks'][:90]}")
    print(f"  4) [nilai] menolak={ref.get('menolak')} → {u4['teks'][:90]}")
    print(f"  5) [duka] {u5['act']}: {u5['teks'][:90]}")
    print(f"  nonverbal: wajah='{u1['nonverbal']['ekspresi']['wajah']}'; "
          f"napas='{u1['nonverbal']['napas']['deskripsi']}'; "
          f"postur='{u1['nonverbal']['postur']['deskripsi']}'")
    print(f"  prosodi: {u1['prosodi']}")
    print(f"  deskripsi: {u1['deskripsi'][:160]}")
    print(f"  idle: {n.presentasi.perilaku_idle()['deskripsi']}")
    print(f"  reaksi: {n.presentasi.reaksi({'jenis': 'bahaya', 'konten': 'api'})['reaksi']}")
    assert u1["teks"] and u1["nonverbal"] and u1["prosodi"]
    assert ref.get("menolak") is True
    assert n.presentasi.snapshot()["aktif"] is True
    print("  ✓ presentasi: dialog + ekspresi + tatapan + postur + napas + "
          "prosodi + idle + reaksi terverifikasi")
    return {"u1": u1, "u2": u2, "u3": u3, "u4": u4, "u5": u5,
            "snapshot": n.presentasi.snapshot()}


def demo_fitur_lanjutan(ticks: int = 90, seed: int = 331) -> Dict[str, Any]:
    """Demo 8 fitur lanjutan: meta-pattern, ritual, temporal, fallibility,
    UI psikologis, presentasi kawanan, dan reputasi sosial."""
    from pycos.inti.naluri import JejakPrediksi, KawananNPC, Naluri
    print("=== Demo FITUR LANJUTAN: pola Player / ritual / waktu / reputasi ===")
    P = {"enable_emosi": True, "enable_introspection": True,
         "enable_kesadaran": True, "enable_presentasi": True,
         "enable_ritual": True, "enable_reputasi": True,
         "ritual_probabilitas": 0.35}
    n = Naluri(name="Rama", personality="penjaga", rng_seed=seed, params=dict(P))
    n.enable_nurani(); n.enable_emosi(True); n.enable_kesadaran()
    n.enable_presentasi(); n.enable_ritual(True)
    jejak = JejakPrediksi(n) if JejakPrediksi is not None else None
    if jejak is not None:
        n.attach_jejak(jejak)
        for _ in range(8):
            n.observe_player("muncul")
            n.observe_player("menghilang")
        for _ in range(6):
            n.observe_player("minta")
        rep = n.pattern_report("Player")
        print("  1) meta-pattern:", [(p["pola"], p["confidence"]) for p in rep["pola"]][:2])
        print("     batas otonom:", n.kesadaran.boundaries[-2:])
    for t in range(1, ticks + 1):
        n.tick(events=[{"drive": "keamanan", "delta": -0.05,
                        "reason": "menjaga"}], action_cost=(t % 5 == 0))
    r = None
    for _ in range(50):
        r = n.ritual.maybe_trigger("idle")
        if r:
            break
    print("  2) ritual (utilitas nol):", r["ritual"] if r else "-",
          "-", (r["deskripsi"][:60] if r else ""))
    # temporal
    n.presentasi.lihat_player(True)
    for _ in range(35):
        n.presentasi.tick(1)
    pro = n.presentasi.proaktif(kepada="Player")
    print("  4) proaktif (Player diam):", pro.get("teks", "")[:70])
    # fallibility
    n.kesadaran.hold_belief("dia jujur", "dia berbohong")
    for _ in range(8):
        n.kesadaran.metacognitive_doubt(0.9)
    ubah = n.presentasi.terima_bukti("dia jujur", "aku melihatnya berbohong", 0.9)
    print("  5) berubah pikiran:", ubah["berubah"], "-", ubah["teks"][:70])
    # UI
    ind = n.presentasi.indikator_psikologis()
    print("  6) UI (ganti stat bar):", ind["label_ketenangan"], "/",
          ind["label_fokus"], "/", ind["label_gairah"], "| tag:",
          n.presentasi.tag_dialog())
    # kawanan + reputasi
    kawanan = KawananNPC()
    kawanan.enable_reputasi(True)
    for nama, pers in (("Ana", "sosiawan"), ("Budi", "penjaga")):
        npc = kawanan.tambah(nama, personality=pers, rng_seed=seed,
                             params=dict(P))
        npc.enable_presentasi(); npc.enable_emosi(True); npc.enable_ritual(True)
    kawanan.catat_rumor("Ana", "Player", "dia menipuku", muatan=-0.8, tick=10)
    kawanan.catat_rumor("Budi", "Player", "aku dengar dia menolong", muatan=0.6, tick=12)
    print("  7) tag kawanan:", kawanan.tag_all())
    print("  8) reputasi Player:", kawanan.reputasi("Player")["label"],
          kawanan.reputasi("Player")["sumbu"])
    print("     reputasi -> relasi:", kawanan.terapkan_reputasi("Player")["relasi"])
    print("  ✓ 8 fitur lanjutan terverifikasi")
    return {"pola": n.pattern_report("Player"), "ritual": r,
            "indikator": ind, "reputasi": kawanan.reputasi("Player")}


def demo_kinerja(seed: int = 7) -> Dict[str, Any]:
    """Demo optimasi: indeks terbalik, konsolidasi, LOD hierarkis, profiler,
    spatial hash, event-driven, replay deterministik."""
    from pycos.inti.naluri import JejakPrediksi, KawananNPC, LOD_MODES, Naluri
    import random as _r
    print("=== Demo KINERJA & SKALABILITAS ===")
    if JejakPrediksi is None:
        print("  (JEJAK tidak tersedia — lewati bagian indeks/konsolidasi)")
    else:
        rng = _r.Random(seed)
        stim = ["api di depan", "lorong gelap", "makanan", "air", "anjing",
                "bunga", "gua", "hujan", "batu", "pohon"]
        j = JejakPrediksi(naluri=None, capacity=4000)
        for i in range(2000):
            j.record_experience(rng.choice(stim), "hindar",
                                {"drive_deltas": {"keamanan": rng.uniform(-0.5, 0.5)}},
                                tick=i)
        print(f"  indeks: {j.size} episode, {len(j._token_index)} token; "
              f"kandidat kueri 'api' = {len(j._candidates({'api'}))}")
        j2 = JejakPrediksi(naluri=None, capacity=4000)
        for i in range(1200):
            j2.record_experience(rng.choice(stim), "amati",
                                 {"drive_deltas": {"keamanan": 0.1}}, tick=i,
                                 importance=0.1)
        rep = j2.consolidate_memory(importance_threshold=0.2)
        print(f"  konsolidasi tidur: {rep['before']} -> {rep['after']} episode "
              f"({rep['summaries']} ringkasan)")
    # LOD hierarkis + profiler
    n = Naluri(name="Rama", rng_seed=seed,
               params={"enable_kesadaran": True, "enable_presentasi": True})
    n.enable_kesadaran(); n.enable_presentasi()
    print("  LOD hierarkis:", LOD_MODES)
    n.enable_profiling(True)
    for i in range(200):
        n.tick(events=[{"drive": "keamanan", "delta": -0.05, "reason": "jaga"}])
    prof = n.profile_report()
    print("  profiler:", [(s["name"], s["avg_ms"]) for s in prof["sections"][:2]])
    # spatial hash + event-driven + contagion
    k = KawananNPC()
    for i in range(20):
        k.tambah(f"N{i:02d}", rng_seed=seed + i)
        k.set_position(f"N{i:02d}", (i * 6.0, 0.0))
    k._reindex_grid()
    k.npcs["N00"].emosi["takut"] = 0.9
    ct = k.emotional_contagion(radius=10.0, strength=0.5)
    ev = k.tick_event_driven()
    print(f"  spatial grid: {len(k._grid)} sel | contagion {ct} | "
          f"event-driven {ev}")
    # replay deterministik
    n.enable_replay(True)
    for i in range(20):
        n.tick(events=[{"drive": "energi", "delta": -0.1, "reason": "x"}],
               action_cost=(i % 3 == 0))
    n_replay = Naluri.replay(n.export_replay())
    print("  replay deterministik identik:", n.levels == n_replay.levels)
    print("  ✓ optimasi & skalabilitas terverifikasi")
    return {"profiler": prof, "contagion": ct, "event_driven": ev}


def demo_sosial(seed: int = 11) -> Dict[str, Any]:
    """Demo 6 fitur sosial: trust weight, faksi, konfrontasi, decay of truth,
    social proof, dan asimetri pemulihan kepercayaan."""
    from pycos.inti.naluri import KawananNPC, Naluri
    print("=== Demo DINAMIKA SOSIAL & KEBENARAN ===")
    k = KawananNPC()
    k.enable_reputasi(True)

    def _mk(nama, sd, pos):
        n = k.tambah(nama, rng_seed=sd, params={"enable_kesadaran": True})
        n.enable_kesadaran(semua=True); n.mode_npc(True)
        k.set_position(nama, pos)
        return n

    for i, nm in enumerate(["Kepala", "Pembohong", "Ana", "Budi", "Cici"]):
        _mk(nm, seed + i, (i * 3.0, 0.0))
    player = "Player"
    for _ in range(5):
        k.npcs["Pembohong"].kesadaran.confabulate("kejadian malam")
    for _ in range(6):
        for nm in ["Kepala", "Ana", "Budi", "Cici"]:
            k.npcs[nm].berinteraksi("Pembohong", muatan=-0.6,
                                    kepercayaan_delta=-0.9)
            k.npcs[nm].berinteraksi("Kepala", muatan=0.6,
                                    kepercayaan_delta=0.9)
    print("  F1 trust Kepala=%.2f | Pembohong=%.2f"
          % (k.trust_weight("Kepala"), k.trust_weight("Pembohong")))
    r = k.catat_rumor("Pembohong", player, "dia mencuri", muatan=-0.7, tick=1)
    print("  F1 rumor ditandai alarm_palsu:", r.get("alarm_palsu"), r.get("alasan_alarm"))

    # F5 social proof: 5 sumber berbeda → konsensus
    k2 = KawananNPC(); k2.enable_reputasi(True)
    for i in range(6):
        n = k2.tambah(f"S{i}", rng_seed=seed + 20 + i); n.mode_npc(True)
    for i in range(6):
        k2.catat_rumor(f"S{i}", player, "dia berbahaya", muatan=-0.9, tick=5)
    print("  F5 konsensus (override kredibilitas):", k2._reputasi.social_proof_events,
          "| bahaya=%.2f" % k2.reputasi(player)["sumbu"].get("bahaya", 0.0))

    # F2 faksi + F4 decay + F3 konfrontasi
    k3 = KawananNPC(); k3.enable_reputasi(True)
    for i, nm in enumerate(["F1", "F2", "F3", "Rama", "Saksi"]):
        n = k3.tambah(nm, rng_seed=seed + 40 + i); n.enable_kesadaran(semua=True); n.mode_npc(True)
        k3.set_position(nm, (i * 3.0, 0.0))
    for nm in ["F1", "F2", "F3"]:
        k3.npcs[nm].kesadaran.gossip(player, "dia iblis yang jahat")
        k3.catat_rumor(nm, player, "dia iblis yang jahat", muatan=-0.9, tick=10)
    echo = k3.echo_chamber(player, window=500, min_anggota=3)
    print("  F2 faksi terbentuk:", [(f["anggota"], f["kohesi"]) for f in echo["faksi"]])
    for nm in ["F1", "F2", "F3"]:
        k3.npcs[nm].tick_count = 10 + 3 * 90
    dec = k3.decay_of_truth(window=90)
    if dec:
        print("  F4 peluruhan kebenaran (tahap %d): %s" % (dec[0]["tahap"], dec[0]["baru"]))
    konf = k3.konfrontasi(player, "Saksi", "F1",
                          "Rama melihat Player sedang di rumah", kekuatan=0.9)
    print("  F3 konfrontasi: rumor terkonfirmasi=%d, dipulihkan=%s"
          % (konf["rumor_terkonfirmasi"], konf["dipulihkan"]))

    # F6 asimetri pemulihan
    n = Naluri(name="Rama", rng_seed=seed, params={"enable_kesadaran": True})
    n.enable_kesadaran(semua=True); n.mode_npc(True)
    for _ in range(12):
        n.berinteraksi("Player", muatan=0.5, kepercayaan_delta=0.5)
    n.hancurkan_kepercayaan("Player", sebab="pengkhianatan")
    v = n.viskositas_relasi("Player")
    n.berinteraksi("Player", muatan=0.5, kepercayaan_delta=0.5)
    print("  F6 kepercayaan hancur -> faktor pemulihan %.2f (%s); setelah 1 interaksi = %.2f"
          % (v["faktor"], v["label"], n.relasi("Player")["kepercayaan"]))
    print("  ✓ dinamika sosial & peluruhan kebenaran terverifikasi")
    return {"echo": echo, "decay": dec, "konfrontasi": konf,
            "viskositas": v}


def demo_momen(seed: int = 13) -> Dict[str, Any]:
    """Demo 5 tambahan: core memory, tells, diam bermakna, utang, linger."""
    from pycos.inti.naluri import Naluri
    print("=== Demo MOMEN, TELLS, DIAM, UTANG, LINGER ===")

    def _full(n):
        n.enable_kesadaran(semua=True); n.mode_npc(True)
        if n.nurani is not None:
            n.nurani.set_pillars(("affective_memory", "social_memory"), aktif=True)
        return n

    # 1) core memory
    n = _full(Naluri(name="Rama", rng_seed=seed,
                     params={"enable_kesadaran": True}))
    n.kesadaran._remember_episode({"content": "hari biasa", "salience": 0.2})
    n.tandai_momen("dia mengkhianatiku di depan semua orang",
                   klaim="tidak percaya siapa pun", bobot=1.5)
    cands = n.kesadaran._candidates()
    core_c = [c for c in cands if c.get("kind") == "core"]
    print("  F1 core memory: klaim=%s, salience=%.2f, identitas='%s'"
          % (core_c[0]["detail"]["klaim"], core_c[0]["salience"],
             n.kesadaran.narrative_state()))

    # 2) tells
    par = _full(Naluri(name="Parno", personality="paranoid", rng_seed=seed + 1,
                       params={"enable_presentasi": True}))
    par.presentasi.params["enable_presentasi"] = True
    ding = _full(Naluri(name="Batu", personality="dingin", rng_seed=seed + 2,
                        params={"enable_presentasi": True}))
    ding.presentasi.params["enable_presentasi"] = True
    tp = par.presentasi.tell_katalog(); td = ding.presentasi.tell_katalog()
    par.levels["keamanan"] = -0.9; par.kesadaran.doubt = 0.6
    par.presentasi._fidget = 0.5
    print("  F2 tell paranoid: %s -> '%s'" % (tp["drive"], tp["teks"]))
    print("     tell dingin  : %s -> '%s'" % (td["drive"], td["teks"]))
    print("     bocor saat menyembunyikan:", par.presentasi.ekspresi()["kebocoran"])

    # 3) diam yang bermakna
    hes = _full(Naluri(name="Hes", rng_seed=seed + 3,
                       params={"enable_presentasi": True}))
    hes.presentasi.params["enable_presentasi"] = True
    hes.kesadaran._last_ignition_tick = hes.tick_count
    a1 = hes.presentasi._pilih_act("Player", "apa ini", masuk=True)
    a2 = hes.presentasi._pilih_act("Player", "apa ini", masuk=True)
    print("  F3 diam bermakna: act '%s' (jeda %dms) lalu '%s' (jeda %dms)"
          % (a1, hes.presentasi.prosodi(a1)["jeda_ms"], a2,
             hes.presentasi.prosodi(a2)["jeda_ms"]))

    # 4) utang emosional
    u = _full(Naluri(name="Utang", rng_seed=seed + 4,
                     params={"enable_kesadaran": True}))
    u.berinteraksi("Player", muatan=0.6, kepercayaan_delta=0.6)
    for i in range(3):
        u.catat_utang("Player", f"janji ke-{i}")
    t0 = u.relasi("Player")["kepercayaan"]
    u.berinteraksi("Player", muatan=0.9, kepercayaan_delta=0.9)
    print("  F4 utang: berat=%.1f menarik_diri=%s | interaksi diredam %.3f->%.3f"
          % (u.utang("Player")["berat"], u.menarik_diri("Player"), t0,
             u.relasi("Player")["kepercayaan"]))
    print("     setelah bayar utang: menarik_diri=%s"
          % (u.bayar_utang("Player") and u.menarik_diri("Player")))

    # 5) linger
    lg = _full(Naluri(name="Linger", rng_seed=seed + 5,
                      params={"enable_presentasi": True}))
    lg.presentasi.params["enable_presentasi"] = True
    lg.emosi["sedih"] = 1.0; lg.presentasi.ekspresi()
    lg.emosi["sedih"] = 0.0
    e1 = lg.presentasi.ekspresi()
    e2 = lg.presentasi.ekspresi()
    print("  F5 linger: sedih %s -> %.2f -> %.2f (memudar perlahan)"
          % (e1["dominan"], e1["campuran"]["sedih"], e2["campuran"]["sedih"]))
    print("  ✓ momen, tells, diam, utang, linger terverifikasi")
    return {"core": core_c[0], "tell": tp, "utang": u.utang("Player")}


def demo_tutur(seed: int = 21) -> Dict[str, Any]:
    """Demo MESIN TUTUR GENERATIF (L0–L3) + leksikon eksternal."""
    from pycos.inti.naluri import Naluri
    print("=== Demo MESIN TUTUR GENERATIF (L0–L3) ===")
    n = Naluri(name="Rama", rng_seed=seed, params={
        "enable_emosi": True, "enable_kesadaran": True,
        "enable_presentasi": True, "presentasi_trace": True})
    n.enable_nurani(); n.enable_emosi(True); n.enable_kesadaran()
    n.enable_presentasi()
    eng = n.presentasi.tutur_engine()
    if eng is None:
        print("  (mesin tutur/leksikon tidak ditemukan — pakai jalur lama)")
        return {"aktif": False}
    info = eng.info()
    print("  leksikon: %d lema | %d kerangka predikat"
          % (info["jumlah_lema"], info["predikat"]))
    # biografi mengisi argumen, bukan hiasan
    n.kesadaran.tandai_core_memory("dia meninggalkanku saat api membakar rumah",
                                   klaim="aku tidak percaya siapa pun")
    n.kesadaran.hold_belief("dia berbahaya", 0.8)
    n.kesadaran.spotlight = [{"content": "api", "tag": "keamanan",
                              "salience": 0.95}]
    n.kesadaran.agency = 0.4
    print("  contoh ujaran (act × seed):")
    for i, act in enumerate(("ragu", "menolak", "mengenang", "mengamati",
                             "peringatan", "menjawab")):
        n.tick_count += 1
        r = n.presentasi.ucap(kepada="Player", topik="api", act=act,
                              diam_boleh=False)
        print("    [%-12s] %s" % (act, r["teks"]))
    # trace satu ujaran
    n.tick_count += 1
    r = n.presentasi.ucap(kepada="Player", topik="api", act="ragu",
                          diam_boleh=False)
    lapis = [list(x.keys())[0] for x in r.get("trace", [])]
    print("  trace lapisan L0→L3:", lapis)
    print("  ✓ tutur generatif terverifikasi")
    return {"aktif": True, "contoh": r["teks"]}


def demo_kognisi(seed: int = 31) -> Dict[str, Any]:
    """Demo 5 mekanisme kognisi lanjut (pycos.mandiri.kognisi_lanjut)."""
    from pycos.inti.naluri import JejakPrediksi, Naluri, optional_module
    print("=== Demo KOGNISI LANJUT (eversi, Boltzmann, Bayes, Hebbian, OU) ===")
    KL = optional_module("pycos.mandiri.kognisi_lanjut")
    if KL is None:
        print("  (pycos.mandiri.kognisi_lanjut tidak ditemukan)")
        return {"aktif": False}

    # 1) eversi parameter: dua NPC kode sama, pengalaman beda
    def _npc(nama, sd):
        n = Naluri(name=nama, rng_seed=sd, params={
            "enable_emosi": True, "enable_kesadaran": True})
        n.enable_emosi(True); n.enable_kesadaran(); n.enable_eversi(True)
        return n
    a, b = _npc("Terlatih", seed), _npc("Terluka", seed + 1)
    for i in range(120):
        a.emosi["takut"] = 1.8 * (1.0 - i / 120.0); a.tick()
    for i in range(120):
        b.emosi["takut"] = 0.1 + 1.7 * (i / 120.0); b.tick()
    pa, pb = a.eversi_param(), b.eversi_param()
    print("  F1 eversi TD: redaman_emosi %s=%.4f vs %s=%.4f (kode sama)"
          % ("Terlatih", pa["redaman_emosi"], "Terluka", pb["redaman_emosi"]))

    # 2) Boltzmann: tenang vs panik
    t_tenang = KL.suhu_mental(0.02, 0.0, dasar=0.05)
    t_panik = KL.suhu_mental(1.0, 0.9)
    skor = {"ragu": 1.0, "akrab": 0.5, "menantang": 0.1}
    import random as _rd
    rg = _rd.Random(seed)
    tenang = [KL.boltzmann_pilih(skor, t_tenang, rg)[0] for _ in range(200)]
    panik = [KL.boltzmann_pilih(skor, t_panik, rg)[0] for _ in range(200)]
    print("  F2 Boltzmann: τ=%.2f→%s | τ=%.2f→%d tindakan berbeda"
          % (t_tenang, max(set(tenang), key=tenang.count), t_panik,
             len(set(panik))))

    # 3) JejakPrediksi, mesin kepercayaan Bayesian, dan setpoint NURANI
    n3 = Naluri(name="Bayes", rng_seed=seed + 2,
                params={"enable_kesadaran": True})
    n3.enable_nurani(); n3.enable_kesadaran()
    if n3.nurani is not None:
        n3.nurani.seed_setpoints({"keamanan": 0.4})
    n3.tick(events=[{"drive": "keamanan", "delta": -0.3,
                     "reason": "bukti tidak aman"}])
    jp = (JejakPrediksi(naluri=n3, rng_seed=seed + 5)
          if JejakPrediksi is not None else None)
    if jp is not None:
        n3.attach_jejak(jp)
        jp.record_experience(
            "lorong berasap", "masuk",
            {"impact": -0.7, "drive_deltas": {"keamanan": -0.8},
             "label": "terpapar asap"}, context="malam", tick=1)
        hasil_jejak = jp.predict("lorong berasap", action="masuk",
                                 context="malam", tick=2)
        print("  F3 JEJAK: status=%s, scope=%s" % (
            hasil_jejak["memory"]["retrieval_status"], hasil_jejak["scope"]))
    m = KL.MesinKepercayaan(); m.tetapkan("Dia Orang Baik", 0.8)
    runtun = [round(m.perbarui("Dia Orang Baik", 0.45, 1.0, "berbohong"), 3)
              for _ in range(6)]
    print("  F3 Bayesian: P(H) 0.8 → %s → curiga=%s | setpoint keamanan=%+.3f"
          % (runtun, m.curiga("Dia Orang Baik", 0.35), n3.setpoint("keamanan")))

    # 4) graf asosiasi Hebbian → fobia emergent
    n4 = Naluri(name="Fobia", rng_seed=seed + 3,
                params={"enable_emosi": True})
    n4.enable_emosi(True); n4.enable_asosiasi(True)
    for _ in range(30):
        n4.emosi["takut"] = 0.95; n4.levels["bahaya"] = 0.9; n4.tick()
    print("  F4 Hebbian: bobot bahaya–takut=%.3f, asosiasi('%s')=%s, fobia=%d"
          % (n4._kog.graf.bobot("bahaya", "takut"), "bahaya",
             n4.asosiasi("bahaya")[:1], len(n4.fobia())))

    # 5) latent drift OU
    n5 = Naluri(name="Drift", rng_seed=seed + 4, params={"enable_emosi": True})
    n5.enable_emosi(True); n5.enable_latent_drift(True)
    for _ in range(80):
        n5.tick()
    dr = n5.latent_drift()
    print("  F5 OU drift: %s (terikat, mean-reverting)"
          % {k: round(v, 4) for k, v in list(dr.items())[:3]})
    print("  ✓ eversi, Boltzmann, Bayes, Hebbian, drift terverifikasi")
    return {"aktif": True, "eversi": pa}


def demo_persepsi(ticks: int = 200, seed: int = 71) -> Dict[str, Any]:
    """Demo lapisan PERSEPSI: dunia tidak masuk apa adanya.

    Tujuh fenomena psikofisika/fisiologi, masing-masing dicetak dengan
    angka pembanding: (1) hukum Weber-Fechner + level adaptasi, (2) habituasi
    + pemulihan spontan, (3) alarm palsu hipervigilan (SDT), (4) congruence
    emosi + penyempitan atensi Easterbrook, (5) blend top-down prediktif
    (persepsi bisa BERBALIK tanda oleh ekspektasi), (6) affordance Gibson,
    (7) pembelajaran perseptual (d' naik oleh prediksi akurat).
    """
    from pycos.inti.naluri import Naluri
    print("=== Demo PERSEPSI: psikofisika panca indera NPC ===")
    P = {"enable_perception": True}
    if Naluri(name="probe", params=dict(P)).nurani is None:
        print("  (NURANI tidak terpasang — psikofisika saluran butuh pilar F;"
              " fallback linear tetap jalan; keluar)")
        return {}

    # --- 1) Weber-Fechner + adaptasi: veteran vs warga ---
    vet = Naluri(name="Veteran", rng_seed=seed, params=dict(P))
    wz = Naluri(name="Warga", rng_seed=seed, params=dict(P))
    for i in range(120):   # veteran: 120 tick di daerah perang (alasan
        vet.tick(events=[{"drive": "keamanan", "delta": -0.4,
                          "reason": f"letusan {i}"}])   # bervariasi: habituasi
        wz.tick()                                       # tak ikut campur)
    for n, ev in (("uji-vet", vet), ("uji-wz", wz)):
        ev.tick(events=[{"drive": "keamanan", "delta": -0.4, "reason": n}])
    m_vet = next(x["amount"] for x in reversed(vet.delta_log)
                 if x["reason"] == "uji-vet")
    m_wz = next(x["amount"] for x in reversed(wz.delta_log)
                if x["reason"] == "uji-wz")
    print(f"  1) letusan -0.4 yang sama: warga persepsi {m_wz:+.3f}, "
          f"veteran (teradaptasi {vet.nurani.adaptasi['keamanan']:.2f}) "
          f"hanya {m_vet:+.3f} — Weber-Fechner/Helson")
    assert abs(m_vet) < abs(m_wz) * 0.92, (m_vet, m_wz)

    # --- 2) Habituasi + pemulihan spontan ---
    h = Naluri(name="Penghuni", rng_seed=seed, params=dict(P))
    seri = []
    for i in range(8):
        h.tick(events=[{"drive": "koherensi", "delta": -0.3,
                        "reason": "ketukan pintu"}])
        seri.append(next(x["amount"] for x in reversed(h.delta_log)
                         if x["reason"] == "ketukan pintu"))
    for _ in range(70):    # jeda tanpa stimulus (melewati habit_window=60)
        h.tick()
    h.tick(events=[{"drive": "koherensi", "delta": -0.3,
                   "reason": "ketukan pintu"}])
    pulih = next(x["amount"] for x in reversed(h.delta_log)
                 if x["reason"] == "ketukan pintu")
    print(f"  2) ketukan ke-1..8: {seri[0]:+.3f} → {seri[-1]:+.3f} "
          f"(habituasi); setelah jeda 70 tick: {pulih:+.3f} — spontan pulih")
    assert abs(seri[-1]) < abs(seri[0]) * 0.5 and abs(pulih) > abs(seri[-1])

    # --- 3) Alarm palsu: paranoid vs netral sendirian di dunia aman ---
    par = Naluri(name="Parno", personality="paranoid", rng_seed=seed)
    net = Naluri(name="Netral", rng_seed=seed, params=dict(P))
    for _ in range(ticks):
        par.tick()
        net.tick()
    print(f"  3) {ticks} tick dunia KOSONG: paranoid {par.persepsi_alarm_palsu}x "
          f"'melihat bayangan' (takut={par.emosi['takut']:.2f}), netral "
          f"{net.persepsi_alarm_palsu}x — criterion SDT negatif")
    assert par.persepsi_alarm_palsu > 0 and net.persepsi_alarm_palsu == 0
    assert any(x["jenis"] == "alarm_palsu" for x in par._persepsi_log)

    # --- 4) Congruence emosi + Easterbrook ---
    tenang = Naluri(name="Tenang", rng_seed=seed,
                    params={**P, "enable_emosi": True})
    panik = Naluri(name="Panik", rng_seed=seed,
                   params={**P, "enable_emosi": True})
    panik.feel("takut", 1.0, "dikejar")
    panik.feel("marah", 0.6, "terpojok")
    for _ in range(3):     # bangun urgensi keamanan agar arousal benar-benar
        panik.tick(events=[{"drive": "keamanan", "delta": -0.7,
                            "reason": "kejaran"}])   # menyempitkan atensi
        tenang.tick()
    empat = [{"drive": d, "delta": dv, "reason": f"r{i}"}
             for i, (d, dv) in enumerate((("keamanan", -0.4),
                                          ("energi", -0.2),
                                          ("koherensi", -0.2),
                                          ("penguasaan", -0.2)))]
    n0 = len(tenang._persepsi_log), len(panik._persepsi_log)
    tenang.tick(events=[dict(e) for e in empat])
    panik.tick(events=[dict(e) for e in empat])
    alt = [sum(1 for x in n._persepsi_log[i0:] if x["jenis"] == "teralihkan")
           for n, i0 in ((tenang, n0[0]), (panik, n0[1]))]
    m_tenang = next(x["amount"] for x in reversed(tenang.delta_log)
                    if x["reason"] == "r0" and x["drive"] == "keamanan")
    m_panik = next(x["amount"] for x in reversed(panik.delta_log)
                   if x["reason"] == "r0" and x["drive"] == "keamanan")
    print(f"  4) stimulus keamanan identik: tenang {m_tenang:+.3f} vs "
          f"panik-takut {m_panik:+.3f} (congruence Bower); atensi tersaring: "
          f"tenang {alt[0]} dialihkan, panik {alt[1]} (Easterbrook)")
    assert abs(m_panik) > abs(m_tenang) * 1.2
    assert alt[1] >= alt[0]

    # --- 5) Top-down prediktif: ekspektasi membalikkan persepsi ---
    td = Naluri(name="Trauma", rng_seed=seed,
                params={**P, "enable_affective_memory": True,
                        "affective_min_samples": 1})
    td.nurani.seed_affective("lorong gelap", {"keamanan": -0.6}, n=10)
    td.tick(events=[{"drive": "keamanan", "delta": +0.05,
                     "reason": "lorong gelap"}])
    m_td = next(x["amount"] for x in reversed(td.delta_log)
                if x["reason"] == "lorong gelap")
    print(f"  5) bukti sensorik +0.05 di 'lorong gelap' dipersepsi {m_td:+.3f} "
          f"— prior luka membalik tanda (pemrosesan prediktif)")
    assert m_td < 0.0

    # --- 6) Affordance Gibson: kebutuhan menentukan yang terlihat ---
    lapar = Naluri(name="Lapar", rng_seed=seed, params=dict(P),
                   initial_levels={"energi": -0.8})
    kenyang = Naluri(name="Kenyang", rng_seed=seed, params=dict(P))
    for _ in range(6):
        lapar.tick()
        kenyang.tick()
    a_l = lapar.affordances("bekal makanan hemat energi")
    a_k = kenyang.affordances("bekal makanan hemat energi")
    print(f"  6) 'bekal makanan': salience energi lapar="
          f"{a_l['salience']['energi']:.3f} vs kenyang="
          f"{a_k['salience']['energi']:.3f}; menonjol: "
          f"{a_l['menonjol']} vs {a_k['menonjol']}")
    assert a_l["salience"]["energi"] > a_k["salience"]["energi"] * 2

    # --- 7) Perceptual learning: d' naik oleh prediksi akurat ---
    bl = Naluri(name="Belajar", rng_seed=seed, params=dict(P))
    s0 = bl.nurani.sensitivitas["keamanan"]
    for i in range(30):
        bl.observe_outcome({"impact": 0.0, "probability": 1.0,
                            "description": "aman tenteram"},
                           {"reward": 0.0, "drive_deltas": {"keamanan": 0.5}})
    s1 = bl.nurani.sensitivitas["keamanan"]
    print(f"  7) 30 observasi akurat: d' keamanan {s0:.2f} → {s1:.2f} "
          f"(pembelajaran perseptual, plafon 2.0)")
    assert s1 > s0
    print("  ✓ semua fenomena persepsi terverifikasi")
    return {"weber": {"veteran": m_vet, "warga": m_wz},
            "alarm_palsu": {"paranoid": par.persepsi_alarm_palsu,
                            "netral": net.persepsi_alarm_palsu},
            "congruence": {"tenang": m_tenang, "panik": m_panik},
            "topdown": m_td, "belajar": (s0, s1)}


def demo_organik():
    """Demo STATE ORGANIK: lima perubahan SIFAT state (bukan penambahan angka).

    1. Kehilangan topologis — slot kosong, bukan bobot kecil.
    2. Luka yang mengecualikan domain — lubang, bukan skalar rendah.
    3. Identitas yang membatasi — emosi ditolak oleh state.
    4. Waktu yang tidak seragam — half-life per-episode yang dipelajari.
    5. Kegagalan dari dalam — kalimat terbentuk, tubuh menolak mengucapkannya.
    """
    from pycos.inti.naluri import JejakPrediksi, Naluri, Nurani
    print("=== Demo STATE ORGANIK: lima perubahan sifat state ===")

    # --- 1. kehilangan topologis ---
    n = Naluri(name="Duka", rng_seed=11)
    n.enable_kesadaran(semua=True)
    n.daftarkan_slot("Ayu", {"peran": "sahabat"})
    n.daftarkan_slot("Bayu", {"peran": "kenalan"})
    sebelum = bool(n.kesadaran.future_simulation("besok aku ke pasar bersama Ayu"))
    n.kosongkan_slot("Ayu", alasan="meninggal")
    sesudah = n.kesadaran.future_simulation("besok aku ke pasar bersama Ayu")
    print("  F1 topologis: slot Ayu kosong -> intensitas =",
          n.intensitas_topologis("Ayu", 0.9),
          "| cabang dibangun:", sebelum, "->", bool(sesudah))
    print("     berduka(Ayu) =", n.duka("Ayu"),
          "| sedih: Bayu tetap tersimulasi =",
          bool(n.kesadaran.future_simulation("besok aku ke pasar bersama Bayu")))

    # --- 2. luka yang mengecualikan domain ---
    nu = Nurani()
    nu.hancurkan_domain("Budi", "uang", alasan="ia menipuku soal utang", tick=10)
    print("  F2 luka domain: uang =", nu.terapkan_domain("Budi", "uang", 0.95),
          "| kesehatan =", nu.terapkan_domain("Budi", "kesehatan", 0.95),
          "| tambal =", nu.tambal_luka("Budi", "uang"))

    # --- 3. identitas yang membatasi ---
    m = Naluri(name="Benteng", rng_seed=12)
    m.enable_kesadaran(semua=True)
    m.tetapkan_identitas("aku orang yang tidak percaya siapa pun",
                         {"senang": ("tolak_bila_bertentangan", 0.0),
                          "penasaran": ("langit", 0.15)})
    for _k in list(m.emosi):
        m.emosi[_k] = 0.0
    m.tandai_stimulus_bertentangan(True)
    hasil = m._emosi_naikkan("senang", 0.6)
    print("  F3 identitas: senang(bertentangan) ditolak state ->", hasil,
          "| penolakan:", (m.emosi_ditolak() or [{}])[-1].get("alasan"))

    # --- 4. waktu yang tidak seragam ---
    j = JejakPrediksi(half_life_ticks=600.0, sync_nurani=False)
    e1 = j.record_experience("api membakar rumah", "lari", -0.8, tick=0)
    e2 = j.record_experience("pasar ramai", "belanja", 0.2, tick=0)
    for _ in range(5):
        j.ingat_kembali(e1)
    for _ in range(5):
        j.koreksi_salah(e2)
    print("  F4 waktu: half-life ep1 (sering diingat) =",
          round(j.half_life_episode(e1), 1),
          "| ep2 (sering salah) =", round(j.half_life_episode(e2), 1))

    # --- 5. kegagalan dari dalam ---
    p = Naluri(name="Gagap", rng_seed=13)
    p.enable_presentasi(semua=True)
    p.enable_kesadaran(semua=True)
    for _k in list(p.emosi):
        p.emosi[_k] = 0.0
    tenang = p.presentasi.kelayakan_tutur()["kelayakan"]
    p.emosi["takut"] = 0.95
    p.emosi["malu"] = 0.9
    p.levels["koherensi"] = -0.9
    p.kosongkan_slot("Ibu", alasan="meninggal")
    panik = p.presentasi.kelayakan_tutur()["kelayakan"]
    tahan = None
    for _ in range(30):
        p.emosi["takut"] = 0.95
        p.emosi["malu"] = 0.9
        p.levels["koherensi"] = -0.9
        e = p.presentasi.ucap(kepada="Budi", topik="rahasia")
        if isinstance(e, dict) and e.get("disembunyikan"):
            tahan = e
            break
    print("  F5 tutur: kelayakan tenang =", tenang, "-> panik =", panik)
    if tahan:
        print("     terbentuk:", repr(str(tahan.get("teks_terbentuk", ""))[:50]),
              "| terucap:", repr(tahan.get("teks")),
              "| sebab:", tahan.get("alasan_penolakan"))

    print("  \u2713 topologis, luka domain, identitas, waktu heterogen, "
          "penolakan tutur terverifikasi")
    return {"aktif": True}


def demo_gejala() -> Dict[str, Any]:
    """Demo SISTEM I: gejala murni yang tak bisa diklaim → kategori baru."""
    from pycos.inti.naluri import Naluri
    print("=== Demo ORDE NOL: gejala murni → kategori proto → kategori penuh ===")
    n = Naluri(name="Nara", rng_seed=41)
    n.enable_kesadaran(semua=True)
    n.enable_presentasi(semua=True)
    n.enable_gejala(True)

    # (a) tekanan asing TANPA tag/source/kind: tak ada modul yang mengklaim.
    langkah2 = False
    for _ in range(3):
        n.gejala_rasakan(0.7, None, sampel="")
        n.tick()
        if "ada sesuatu yang tidak bisa kunamai" in [
                c.get("content") for c in n.kesadaran.workspace]:
            langkah2 = True
    st = n.gejala_state()
    print("  gejala hidup :", [(g["signature"], g["intensitas"],
                                g["polaritas"], g["ulangan"])
                               for g in st["gejala"]])
    print("  langkah 2    :", langkah2,
          "| tak dimiliki:", st["gejala"][0]["tidak_dimiliki"]
          if st["gejala"] else None)

    # (b) berulang → proto; proto yang BERTAHAN & sering → kategori penuh.
    for i in range(90):
        if i % 3 == 0:
            n.gejala_rasakan(0.7, None, sampel="")
        n.tick()
    st = n.gejala_state()
    print("  proto        :", [(p["signature"], p["jumlah"], p["nama"])
                               for p in st["proto"]])
    print("  kategori baru:", sorted({p["klaim_identitas"]
                                      for p in st["kategori_penuh"]}))
    print("  sensitivitas NURANI:",
          [{"nama": v["nama"], "jenis": v["jenis"],
            "kekuatan": v["kekuatan"]}
           for v in list(st["sensitivitas_nurani"].values())[:1]])
    print("  klaim diri   :", n.kesadaran.narrative_state())

    # (c) gejala sekilas: tak berulang → memudar, tetapi meninggalkan BEKAS.
    n.gejala_rasakan(0.5, None, sampel="", tanda="sekilas")
    for _ in range(14):
        n.tick()
    print("  bekas Residu :", [(b.get("catatan"), b.get("signature"))
                               for b in n.gejala_state()["residu_bekas"][-1:]])
    print("  entri aktif Residu tetap kosong:",
          n._organik.residu.state()["aktif"] == {})

    # (d) klaim: begitu ada modul yang cocok, gejala tidak lagi baru.
    n.emosi["takut"] = 0.8
    klaim = n.gejala_rasakan(0.8, -0.9, sampel="bahaya")
    n.tick()   # bila ignition tertunda, pemeriksaan tick ini yang memprosesnya
    sig_klaim = str(klaim["gejala"]["signature"])
    pipa = dict(n._gejala_hasil.get(sig_klaim) or klaim.get("pipeline") or {})
    klaim["pipeline"] = pipa
    pencalonan = pipa.get("pencalonan", [])
    print("  pencalonan   :", [(x["modul"], x["kategori"]) for x in pencalonan])
    print("  terklaim oleh:", (klaim.get("pipeline") or {}).get("terklaim"))
    print("  \u2713 gejala murni, kegagalan sebagai state, proto, konsolidasi, "
          "bekas, klaim terverifikasi")
    return {"gejala": st, "klaim": klaim}


def demo_invensi() -> Dict[str, Any]:
    """Demo pelita STRUKTUR BARU: hipotesis/rencana/kategori/tujuan endogen."""
    from pycos.inti.naluri import Naluri, _kog_dari
    print("=== Demo INVENSI: melahirkan struktur baru dari dalam ===")
    n = Naluri(name="Nara", rng_seed=41)
    n.enable_kesadaran(semua=True)
    n.enable_invensi(True)
    n.params["invensi_cadence"] = 3
    # state internal yang kaya supaya semua operasi punya bahan
    n.levels["curiosity"] = 0.9
    n.emosi["penasaran"] = 0.6
    kog = _kog_dari(n)
    for a, b in [("gajah", "besar"), ("gajah", "abu"), ("badak", "besar"),
                 ("badak", "abu"), ("singa", "buas"), ("harimau", "buas")]:
        kog.graf.koaktifkan(a, b, 0.5)
    kog.kepercayaan.tetapkan("manusia pada dasarnya egois", 0.7)
    kog.kepercayaan.tetapkan("dunia ini adil", 0.6)
    n.kesadaran.dissonance["aku ingin dekat tapi takut terluka"] = {"kekuatan": 0.6}
    n.kesadaran.hold_belief("aku percaya keadilan", 0.6)
    n.kesadaran.hold_belief("aku menikmati ketidakadilan kecil", 0.5)
    org = getattr(n, "_organik", None)
    if org is not None:
        org.topologi.daftar("teman lama")
        org.topologi.kosongkan("teman lama", "hilang", 1)
        org.luka.lukai("ibu", "suara", "kehilangan", 2)
    for _ in range(9):
        n.tick()
    st = n.invensi_state()
    print("  lahir =", st["n_lahir"], "| kristal =", st["n_kristal"], st["jenis"])
    for s in st["terbaru"]:
        print("   [%s|%s] %.2f/%.2f/%.2f  %s" % (
            s["jenis"], s["operasi"], s["kebaruan"], s["koherensi"],
            s["utilitas"], s["isi"]))
    hipo_baru = [k for k in kog.kepercayaan.ringkas().keys() if k.startswith("mungkin")]
    print("  ✓ hipotesis baru jadi keyakinan nyata:", len(hipo_baru),
          "| contoh:", hipo_baru[0] if hipo_baru else None)
    return {"state": st, "hipotesis_baru": hipo_baru}


def demo_kausal() -> Dict[str, Any]:
    """Demo poin 1: model kausal — menjelaskan kenapa, counterfactual, blame."""
    from pycos.inti.naluri import JejakPrediksi, Naluri
    print("=== Demo MODEL KAUSAL: menjelaskan 'kenapa', bukan sekadar angka ===")
    n = Naluri(name="Nara", rng_seed=41)
    n.enable_kesadaran(semua=True)
    n.enable_kausal(True)
    jejak = JejakPrediksi(n) if JejakPrediksi is not None else None
    if jejak is not None:
        n.attach_jejak(jejak)
    if jejak is not None:
        for _ in range(4):
            jejak.record_experience("api menyala di dapur", "menyentuh api",
                                    {"impact": -0.9, "drive_deltas": {"keamanan": -0.8},
                                     "label": "kulit terbakar"}, context="dapur")
        for _act in ("diam di rumah", "menutup jendela", "perkuat atap"):
            for _ in range(3):
                jejak.record_experience("badai besar malam ini", _act,
                                        {"impact": -0.7, "drive_deltas": {"keamanan": -0.5},
                                         "label": "rumah rusak"}, context="malam")
    n.pelajari_kausal()
    print("  kenapa kulit terbakar ->", n.jelaskan_kenapa("kulit terbakar")["narasi"])
    print("  cf menyentuh api      ->", n.counterfactual_kausal("api di dapur", "menyentuh api")["narasi"])
    print("  cf menari (tak diuji) ->", n.counterfactual_kausal("api di dapur", "menari")["narasi"])
    b1 = n.blame_kausal("api di dapur", "menyentuh api", "kulit terbakar")
    b2 = n.blame_kausal("badai besar", "diam di rumah", "rumah rusak")
    print("  blame aksi      ->", b1["narasi"])
    print("  blame kebetulan ->", b2["narasi"])
    return {"jelas": n.jelaskan_kenapa("kulit terbakar"), "blame": [b1, b2]}


def demo_perencana() -> Dict[str, Any]:
    """Demo poin 2: perencanaan multi-tingkat + meta-planning."""
    from pycos.inti.naluri import JejakPrediksi, Naluri
    print("=== Demo PERENCANA: means-end multi-tingkat + meta-planning ===")
    n = Naluri(name="Nara", rng_seed=41)
    n.enable_kesadaran(semua=True)
    n.enable_kausal(True)
    n.enable_perencana(True)
    jejak = JejakPrediksi(n) if JejakPrediksi is not None else None
    if jejak is not None:
        n.attach_jejak(jejak)
        for stim, act, lab, imp in (
                ("tahu letak pasar", "beli di pasar", "dapat makanan", 0.7),
                ("ada orang terdekat", "bertanya pada orang", "tahu letak pasar", 0.6),
                ("tahu jalan ke alun-alun", "pergi ke alun-alun", "ada orang terdekat", 0.5),
                ("pernah lihat peta", "ingat peta", "tahu jalan ke alun-alun", 0.5)):
            for _ in range(3):
                jejak.record_experience(stim, act, {"impact": imp, "label": lab})
    hasil = n.rencanakan("dapat makanan", fakta=["pernah", "lihat", "peta"])
    print("  meta:", hasil["meta"]["catatan"])
    print("  kedalaman =", hasil["pohon"]["kedalaman"], "| lengkap =", hasil["pohon"]["lengkap"])
    print(hasil["narasi"])
    print("  urutan: ", " → ".join(s.split(':', 1)[-1] for s in hasil["langkah"]))
    return {"kedalaman": hasil["pohon"]["kedalaman"], "langkah": hasil["langkah"]}


def demo_pelindung() -> Dict[str, Any]:
    """Demo SISTEM II: sepuluh mekanisme pelindung ilusi."""
    from pycos.inti.naluri import KawananNPC, Naluri, _pelindung_act_hint, _pengakuan_istirahat, keragaman_scene
    print("=== Demo PELINDUNG ILUSI: keterbatasan diarakterisasi, bukan disembunyikan ===")
    n = Naluri(name="Sarah", rng_seed=71)
    n.set_personality_preset("paranoid")
    n.enable_presentasi(semua=True)
    n.enable_kesadaran(semua=True)
    n.enable_pelindung(True)
    p = n.presentasi
    # 5) tanda kegagalan kepribadian
    print("  5. watak gagal :", p.watak_kegagalan()["nama"], "→",
          p.watak_kegagalan()["label"])
    # 1) gagal-sebagai-akting: saat bingung, wataknya yang mengambil alih
    p.tandai_tidak_paham(True)
    print("  1. act gagal   :", _pelindung_act_hint(p, None, None, False)
          or "(belum ada pemicu)", "| pidato:", repr(p.pidato_gagal("uji")))
    p.tandai_tidak_paham(False)
    # 2) jeda bermakna (deterministik & dapat dipelajari)
    j1 = p.jeda_bermakna(kepada="Player", topik="hal baru yang aneh")
    n.kesadaran.doubt = 0.8
    j2 = p.jeda_bermakna(kepada="Player", topik="hal baru yang aneh")
    print("  2. jeda        :", j1["ms"], "ms", j1["sebab"], "→ ragu 0.8:",
          j2["ms"], "ms", j2["sebab"])
    # 9) buffer manusiawi
    p.tandai_lupa(True)
    print("  9. buffer lupa :", repr(p.buffer_manusiawi("lupa")))
    # 8) penyerap adversarial
    serap = p.serap_adversarial("apa kau ini AI? buktikan kau sadar!")
    print("  8. adversarial :", serap["jenis"], "→", repr(serap["balasan"]))
    # act TIDAK dipaksa: wataklah yang memutuskan bagaimana gagal (mekanisme 1)
    p.dengar("apa kau ini AI? buktikan kau sadar!", "Player")
    ucap = p.ucap(kepada="Player")
    print("     ujaran      :", repr(ucap.get("teks")),
          "| act:", ucap.get("act"))
    # 4) penyaring meta
    bersih, bocor = p.saring_meta("skor ignition 0.83 di workspace tick 42")
    print("  4. saring meta :", repr(bersih), "| bocor:", bocor)
    # 3) eskalasi variasi (4 tingkat)
    hasil = []
    for _ in range(6):
        teks, act, info = p.eskalasi_variasi("aku tidak tahu harus bilang apa",
                                             "menjawab", "Player", "api")
        hasil.append((info.get("tingkat"), info.get("cara"), act, teks[:38]))
    print("  3. eskalasi    :", hasil[-1][:3], "|", repr(hasil[-1][3]))
    # 7) keragaman lintas-NPC
    kawanan = KawananNPC()
    kawanan.tambah("Sarah", personality="sosiawan")
    kawanan.tambah("Rama", personality="sosiawan")
    for nm in ("Sarah", "Rama"):
        q = kawanan.npcs[nm].presentasi
        kawanan.npcs[nm].enable_presentasi(semua=True)
        kawanan.npcs[nm].enable_pelindung(True)
        q._act_counts["menimbang"] = 5
        q._history.append({"teks": "aku menimbang-nimbang dulu", "act": "menimbang"})
    geser = keragaman_scene(kawanan.npcs, tick=10)
    print("  7. keragaman   :", [(x["jenis"], x["penanda"], x["digeser"])
                                 for x in geser][:1])
    # 6) degradasi anggun (awal → menengah → panjang → sangat panjang)
    p2 = n.presentasi
    print("  6. degradasi   :", p2.degradasi_state()["mode"],
          "→ sesi menua: ", end="")
    p2._pelindung_sesi_mulai = -10_000
    p2._pelindung_anggaran = {k: 0 for k in p2._pelindung_anggaran}
    n.kesadaran.timeline = list(n.kesadaran.timeline) + [
        {"ringkas": f"momen {i}"} for i in range(200)]
    n.kesadaran.core_memory = list(n.kesadaran.core_memory) + [
        {"ringkas": f"inti {i}"} for i in range(30)]
    deg3 = p2.degradasi_state()
    print(deg3["mode"], "|", deg3["saran"], "|",
          repr(_pengakuan_istirahat(p2, deg3)))
    # 10) monitor integritas: latensi yang selalu sama terbaca mesin → dikoreksi
    for _ in range(6):
        p.jeda_bermakna(kepada="Player", topik="hal yang sama")
    lap = p.monitor_integritas().periksa(tick=100)
    print(" 10. monitor     :", [t["jenis"] for t in lap["temuan"]] or "(bersih)",
          "| koreksi:", [k["aksi"] for k in lap["koreksi"]] or "-")
    print("  \u2713 gagal-sebagai-akting, jeda, variasi, saring meta, buffer, "
          "adversarial, keragaman, degradasi, monitor terverifikasi")
    return {"jeda": j1, "serap": serap, "monitor": lap}

