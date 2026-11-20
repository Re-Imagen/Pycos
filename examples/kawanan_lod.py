"""100 NPC, lima pita jarak/LOD; bukan benchmark latensi."""
from collections import Counter
import json

from pycos.inti.kawanan import KawananNPC


def main():
    kawanan = KawananNPC()
    jarak = (0, 12, 20, 40, 80)
    for i in range(100):
        nama = "NPC-{:03d}".format(i)
        kawanan.tambah(nama, rng_seed=i)
        kawanan.set_lod_by_distance(nama, jarak[i % len(jarak)])
    sebelum = {nama: npc.tick_count for nama, npc in kawanan.npcs.items()}
    for _ in range(3):
        kawanan.tick_all()
    print(json.dumps({"jumlah": len(kawanan.npcs),
                      "lod": dict(Counter(n.lod_mode for n in kawanan.npcs.values())),
                      "kemajuan": {nama: n.tick_count - sebelum[nama]
                                   for nama, n in kawanan.npcs.items()}},
                     ensure_ascii=False))


if __name__ == "__main__":
    main()
