"""Showcase mandiri inti; jalankan dengan python -m pycos.inti.demo."""
from __future__ import annotations


def jalankan() -> None:
    """Jalankan seluruh showcase dalam urutan historis."""
    from pycos.inti.naluri import Naluri
    from pycos.inti.demo import skenario
    Naluri.demo(ticks=90, seed=7)
    print()
    skenario.demo_npc()
    print()
    skenario.demo_watak()
    print()
    skenario.demo_persepsi()
    print()
    skenario.demo_introspeksi()
    print()
    skenario.demo_kesadaran()
    print()
    skenario.demo_presentasi()
    print()
    skenario.demo_gejala()
    print()
    skenario.demo_pelindung()
    print()
    skenario.demo_fitur_lanjutan()
    print()
    skenario.demo_kinerja()
    print()
    skenario.demo_sosial()
    print()
    skenario.demo_empati()
    print()
    skenario.demo_momen()
    print()
    skenario.demo_tutur()
    print()
    skenario.demo_kognisi()
    print()
    skenario.demo_organik()
    print()
    skenario.demo_invensi()
    print()
    skenario.demo_kausal()
    print()
    skenario.demo_perencana()

