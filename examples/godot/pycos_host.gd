# Godot 4.x: pasang script pada Node dan atur path interpreter Python absolut.
extends Node

@export var python_executable: String = "/usr/bin/python3"

func _ready() -> void:
    # Interpreter harus sudah memasang Pycos: python -m pip install /path/Pycos.
    # Hindari shell: setiap argumen dikirim terpisah ke OS.execute.
    var path := "user://pycos-request-%s.json" % get_instance_id()
    var file := FileAccess.open(path, FileAccess.WRITE)
    if file == null:
        push_error("Tidak dapat menulis request Pycos")
        return
    file.store_string(JSON.stringify({
        "seed": 7,
        "dunia": {"ringkas": "NPC melihat api", "events": []},
        "kandidat": [
            {"name": "istirahat", "drive_effects": {"energi": 0.2}},
            {"name": "amati", "drive_effects": {"keingintahuan": 0.1}}
        ]
    }))
    file.close()
    var output: Array = []
    var code := OS.execute(python_executable, PackedStringArray([
        "-m", "pycos.konektor", "--json", "--input",
        ProjectSettings.globalize_path(path)
    ]), output, false)
    DirAccess.remove_absolute(ProjectSettings.globalize_path(path))
    if code != 0 or output.is_empty():
        push_error("Pycos gagal (%s): %s" % [code, str(output)])
        return
    var response = JSON.parse_string(str(output[0]))
    if not response is Dictionary or not response.get("ok", false):
        push_error("Respons Pycos tidak sah")
        return
    print("Aksi: ", response["pilihan"]["action"])
    print("HUD: ", response["hud"]["ringkasan"])
    # Host menerapkan pilihan dan menyimpan state sendiri. Demo ini stateless.
    # OS.execute memblokir: jangan panggil setiap frame; gunakan worker/proses
    # berumur panjang untuk integrasi produksi. Tidak didukung pada ekspor Web.
