"""Dua register Tutur dan tag HUD milik NPC yang sama."""
import json

from pycos.bahasa.tutur import GenContext, TuturEngine
from pycos.dukungan.sumber import jalur_leksikon
from pycos.inti.naluri import Naluri


def main():
    npc = Naluri(name="Rama", rng_seed=7)
    npc.enable_presentasi()
    dialog = []
    for register in ("formal", "akrab"):
        # Engine terpisah agar riwayat anti-pengulangan tidak mencampur register.
        engine = TuturEngine(jalur_leksikon())
        ujaran = engine.ucap(GenContext(act="senang", topik="pertemuan",
                                       register=register, seed=7,
                                       valensi=.8, arousal=.3))
        if ujaran is None or not ujaran.teks:
            raise RuntimeError("Leksikon tidak menghasilkan ujaran")
        dialog.append({"register": register, "teks": ujaran.teks,
                       "tag": npc.presentasi.tag_dialog()})
    print(json.dumps({"nama": npc.name, "dialog": dialog,
                      "hud": npc.hud_state()}, ensure_ascii=False))


if __name__ == "__main__":
    main()
