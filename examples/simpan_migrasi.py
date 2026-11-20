"""Round-trip save tervalidasi dan migrasi snapshot v3 tanpa mengubah berkas."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from pycos.dukungan.validasi_state import migrasi
from pycos.inti.naluri import Naluri


def main():
    npc = Naluri(name="Rama", rng_seed=7)
    for _ in range(3):
        npc.tick()
    with TemporaryDirectory(prefix="pycos-example-") as folder:
        path = Path(folder) / "rama.json"
        npc.save(str(path))
        pulih = Naluri.load(str(path))
        # Snapshot lama di memori, bukan manipulasi checksum berkas save.
        lama = npc.to_dict()
        lama["format"] = "naluri/3"
        lama.pop("subjective_tick_count", None)
        baru = migrasi(lama, "naluri/4")
        hasil = Naluri.from_dict(baru)
        print(json.dumps({"nama": pulih.name, "format_asal": lama["format"],
                          "format_tujuan": baru["format"],
                          "tick_asli": npc.tick_count,
                          "tick_pulih": pulih.tick_count,
                          "tick_migrasi": hasil.tick_count,
                          "tick_subjektif": hasil.subjective_tick_count,
                          "state_pulih_sama": pulih.to_dict() == npc.to_dict(),
                          "save_ada": path.is_file()}, ensure_ascii=False))


if __name__ == "__main__":
    main()
