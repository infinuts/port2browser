# Original MIT fixture. Shared native and web game logic; no imported game assets.
extends Node2D
var player_x: int = 24
var collected: int = 0
var started: int = 0
var sounds: int = 0
var saves: int = 0
var saving: int = 0
var tone := AudioStreamPlayer.new()
var smoke: bool = false
var save_path: String = "user://beacon.json"

func _ready() -> void:
	if not OS.has_feature("web") and OS.has_environment("P2B_GODOT_SAVE_PATH"):
		save_path = OS.get_environment("P2B_GODOT_SAVE_PATH")
	var sample := AudioStreamWAV.new()
	sample.format = AudioStreamWAV.FORMAT_16_BITS
	sample.mix_rate = 22050
	var pcm := PackedByteArray()
	pcm.resize(11024)
	for i in range(5512):
		pcm.encode_s16(i * 2, int(sin(TAU * 440.0 * i / 22050.0) * 4000))
	sample.data = pcm
	tone.stream = sample
	add_child(tone)
	_load_save()
	smoke = "--smoke" in OS.get_cmdline_user_args()
	if smoke:
		player_x = 24
		collected = 0
		started = 1
		for i in range(8):
			_action(KEY_RIGHT)
		_action(KEY_SPACE)
		_action(KEY_S)
		player_x = 0
		collected = 0
		_load_save()
		tone.stop()
		tone.stream = null
		if player_x != 120 or collected != 1 or saves != 1 or sounds != 1:
			get_tree().quit(2)
		else:
			print("Godot native smoke: movement, collect, audio submission, save/load passed")
			get_tree().quit(0)

func _load_save() -> void:
	if not FileAccess.file_exists(save_path):
		return
	var data = JSON.parse_string(FileAccess.get_file_as_string(save_path))
	if data is Dictionary and typeof(data.get("x")) in [TYPE_INT, TYPE_FLOAT] and int(data.x) >= 0 and int(data.x) <= 288 and data.get("collected") in [0.0, 1.0]:
		player_x = int(data.x)
		collected = int(data.collected)

func _unhandled_key_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo:
		if event.keycode == KEY_ENTER:
			started = 1
		elif started:
			_action(event.keycode)

func _action(key: int) -> void:
	if key == KEY_RIGHT:
		player_x = mini(288, player_x + 12)
	elif key == KEY_LEFT:
		player_x = maxi(0, player_x - 12)
	elif key == KEY_SPACE and absi(player_x - 120) <= 12 and collected == 0:
		collected = 1
		tone.play()
		sounds += 1
	elif key == KEY_S:
		var file := FileAccess.open(save_path, FileAccess.WRITE)
		if file == null:
			saving = -1
		else:
			file.store_string(JSON.stringify({"x": player_x, "collected": collected}))
			file.close()
			saves += 1
			# Godot asynchronously syncs user:// after FileAccess.close().
			# Browser test confirms durability by starting a fresh engine on reload.
			saving = 0

func _process(_delta: float) -> void:
	queue_redraw()
	if OS.has_feature("web"):
		var state := JSON.stringify({"x": player_x, "collected": collected, "started": started, "sounds": sounds, "saves": saves, "saving": saving})
		JavaScriptBridge.eval("window.beaconState = " + state)

func _draw() -> void:
	draw_rect(Rect2(0, 0, 320, 180), Color("0f172a"))
	draw_rect(Rect2(120, 64, 24, 24), Color("1eb43c") if collected else Color("ffbe3c"))
	draw_rect(Rect2(player_x, 100, 24, 24), Color("38bdf8"))
