extends SceneTree
const Catalog=preload("res://scripts/data/catalog.gd")
const Preferences=preload("res://scripts/data/preferences.gd")
const Controls=preload("res://scripts/controllers/player_input.gd")
const MatchModel=preload("res://scripts/combat/match.gd")
var checks=0
var failures=[]

func check(value,label):
	checks+=1
	if not value: failures.append(label)

func _init(): call_deferred("run")

func run():
	var catalog=Catalog.new()
	check(catalog.load_all(),"load catalog")
	check(catalog.ids.size()==5 and catalog.arena_ids.size()==3,"full roster")
	check(catalog.read_json("res://content/missing-test.json")==null and "missing-test.json" in catalog.errors[-1],"missing file diagnostic")
	check(not catalog._number("20") and catalog._number(20),"strict numeric validation")
	var invalid=catalog.characters.kensei.duplicate(true)
	invalid.moves.light.hits=[.1,0]; invalid.kit.mobility.speed="fast"
	catalog.errors.clear(); catalog.validate_character(invalid,"fixture/kensei.json")
	check(catalog.errors.size()>=2 and "fixture/kensei.json" in catalog.errors[0],"field-specific malformed content errors")
	var prefs=Preferences.new()
	# Preserve existing user settings even when a check fails.
	var existed=FileAccess.file_exists(Preferences.PATH)
	var original=FileAccess.get_file_as_string(Preferences.PATH) if existed else ""
	prefs.values.wins=4; prefs.values.resolution=2; prefs.values.round_seconds=77; prefs.values.music=.35
	prefs.values.keys.p0_light=KEY_Z; prefs.values.pads.p0_light={"type":"button","index":3}
	prefs.save()
	var restored=Preferences.new(); restored.load_saved()
	check(restored.values.wins==4 and restored.values.resolution==2 and restored.values.round_seconds==77,"integer persistence")
	check(is_equal_approx(restored.values.music,.35),"volume persistence")
	var controls=Controls.new(); controls.setup(restored.values)
	var key=InputEventKey.new(); key.physical_keycode=KEY_Z; key.pressed=true; controls.accept(key)
	check("light" in controls.pending[0],"keyboard remapping")
	controls.clear()
	var pad=InputEventJoypadButton.new(); pad.device=0; pad.button_index=3; pad.pressed=true; controls.accept(pad)
	check("light" in controls.pending[0],"gamepad remapping (synthetic)")
	controls.clear(); check(controls.pending==[[],[]],"input reset")
	if existed:
		var file=FileAccess.open(Preferences.PATH,FileAccess.WRITE); file.store_string(original); file.close()
	else: DirAccess.remove_absolute(Preferences.PATH)
	for id in catalog.ids:
		for arena in catalog.arena_ids:
			var model=MatchModel.new(catalog.characters[id],catalog.characters.vastor,"PVE",{"round_seconds":30,"wins":1})
			check(model.players[0].profile.id==id and catalog.arenas.has(arena),id+" / "+arena)
			for frame in range(120*40): model.tick(1.0/120); model.events.clear()
			check(model.phase=="VICTORY",id+" / AI finishes "+arena)
	print("SYSTEM CHECKS: %d; FAILURES: %d"%[checks,failures.size()])
	if not failures.is_empty(): printerr(failures)
	quit(0 if failures.is_empty() else 1)
