"""Satu NPC dalam dunia ASCII; jalankan: python -m examples.npc_dunia."""
import json

from pycos.inti.naluri import Naluri
from pycos.lingkungan.dunia import Lingkungan


def main():
    npc = Naluri(name="Rama", rng_seed=7)
    dunia = Lingkungan.dari_ascii([".....", ".....", "....."], seed=7)
    dunia.tambah_npc(npc, (2, 1))
    riwayat = []
    for _ in range(4):
        riwayat.extend(dunia.langkah_semua())
    print(json.dumps({"nama": npc.name, "tick_dunia": dunia.tick,
                      "tick_npc": npc.tick_count,
                      "langkah": riwayat}, ensure_ascii=False))


if __name__ == "__main__":
    main()
