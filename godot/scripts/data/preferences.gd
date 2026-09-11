extends RefCounted
const PATH="user://preferences.json"
var values={"music":.18,"sfx":.45,"shake":true,"flash":.4,"fullscreen":false,"resolution":0,"round_seconds":99,"wins":2,"difficulty":1,"dummy":"PARADO","training_resources":true,"training_restore":true,"training_health":1.0,"debug":false,"keys":{},"pads":{}}

func load_saved():
	if FileAccess.file_exists(PATH):
		var saved=JSON.parse_string(FileAccess.get_file_as_string(PATH))
		if saved is Dictionary:
			for key in values:
				if not saved.has(key): continue
				if typeof(saved[key])==typeof(values[key]): values[key]=saved[key]
				elif typeof(values[key])==TYPE_INT and typeof(saved[key])==TYPE_FLOAT and is_finite(saved[key]): values[key]=int(saved[key])
	for key in ["music","sfx","flash"]: values[key]=clampf(values[key],0,1)
	values.round_seconds=clampi(values.round_seconds,30,300); values.wins=clampi(values.wins,1,5)
	values.difficulty=clampi(values.difficulty,0,2); values.training_health=clampf(values.training_health,.25,2)
	values.resolution=clampi(values.resolution,0,2)
	if not values.dummy in ["PARADO","DEFESA","APÓS ACERTO","PARRY","CPU"]: values.dummy="PARADO"

func save():
	var file=FileAccess.open(PATH,FileAccess.WRITE)
	if file: file.store_string(JSON.stringify(values,"\t"))
	else: push_warning("Não foi possível salvar preferências.")
