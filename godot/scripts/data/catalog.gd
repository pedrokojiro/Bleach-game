extends RefCounted

var characters = {}
var arenas = {}
var errors: Array[String] = []
var ids: Array = []
var arena_ids: Array = []
var palette_data={}
var effects_data={}
var audio_data={}

func read_json(path: String, expected_type: int = TYPE_DICTIONARY):
	if not FileAccess.file_exists(path):
		errors.append(path + ": arquivo ausente")
		return null
	var parser = JSON.new()
	if parser.parse(FileAccess.get_file_as_string(path)) != OK:
		errors.append("%s:%d: %s" % [path, parser.get_error_line(), parser.get_error_message()])
		return null
	if typeof(parser.data) != expected_type:
		errors.append(path + ": estrutura inválida")
		return null
	return parser.data

func load_all(root: String = "res://content") -> bool:
	errors.clear(); characters.clear(); arenas.clear()
	var manifest = read_json(root + "/manifest.json")
	if manifest == null: return false
	if not manifest.get("characters") is Array or not manifest.get("arenas") is Array:
		errors.append(root+"/manifest.json: characters e arenas devem ser listas"); return false
	palette_data=read_json(root+"/palettes/default.json")
	effects_data=read_json(root+"/effects/default.json")
	audio_data=read_json(root+"/audio/default.json")
	if palette_data==null or effects_data==null or audio_data==null: return false
	if not palette_data.get("names") is Array or not palette_data.get("colors") is Array:
		errors.append(root+"/palettes/default.json: names/colors devem ser listas"); return false
	if palette_data.names.is_empty() or palette_data.names.size()!=palette_data.colors.size():
		errors.append(root+"/palettes/default.json: names/colors devem ter o mesmo tamanho não vazio"); return false
	for color in palette_data.colors:
		if not color is Array or color.size()!=3:
			errors.append(root+"/palettes/default.json: colors requer RGB"); return false
		for component in color:
			if not _number(component): errors.append(root+"/palettes/default.json: componente RGB inválido"); return false
	for field in ["hitstop","heavy_hitstop","flash","shake"]:
		if not _number(effects_data.get(field)) or effects_data[field]<0: errors.append(root+"/effects/default.json: "+field+" inválido")
	if not audio_data.get("menu") is String: errors.append(root+"/audio/default.json: menu ausente")
	if not errors.is_empty(): return false
	ids = manifest.get("characters", [])
	arena_ids = manifest.get("arenas", [])
	for id in ids:
		if not id is String or "/" in id or ".." in id:
			errors.append(root+"/manifest.json: ID de personagem inválido"); continue
		var path = root + "/characters/" + id + ".json"
		var data = read_json(path)
		if data == null: continue
		for field in ["profile", "kit", "moves", "forms", "sprite", "released_sprite", "animation_states"]:
			if not data.has(field): errors.append(path + ": campo ausente: " + field)
		if not errors.is_empty(): continue
		if not data.profile is Dictionary or not data.kit is Dictionary or not data.moves is String or not data.forms is String or not data.animation_states is Array:
			errors.append(path+": tipos de profile/kit/moves/forms/animation_states inválidos"); continue
		data.moves = read_json(root + "/" + data.moves)
		data.forms = read_json(root + "/" + data.forms, TYPE_ARRAY)
		if data.moves == null or data.forms == null: continue
		validate_character(data,path)
		for stat in ["vida", "velocidade", "peso", "largura", "altura", "reiatsu"]:
			if not data.profile.has(stat) or not _number(data.profile[stat]) or data.profile[stat] <= 0:
				errors.append(path + ": profile." + stat + " deve ser positivo")
		for action in ["light", "heavy", "air", "grab", "special", "special2", "ultimate", "exclusive"]:
			if not data.moves.has(action):
				errors.append(path + ": moves." + action + " ausente"); continue
			var move = data.moves[action]
			if not move is Dictionary:
				errors.append(root+"/moves/"+id+".json: "+action+" deve ser objeto"); continue
			for field in ["startup", "active", "recovery", "dano", "alcance", "custo", "cooldown", "hitstun", "blockstun"]:
				if not move.has(field) or not _number(move[field]) or move[field] < 0:
					errors.append(path + ": moves." + action + "." + field + " inválido")
			if not move.get("tipo", "") in ["melee", "grab", "pulse", "rush", "wave", "trap", "projectile", "barrier"]:
				errors.append(path + ": moves." + action + ".tipo desconhecido")
		characters[id] = data
	for id in arena_ids:
		if not id is String or "/" in id or ".." in id:
			errors.append(root+"/manifest.json: ID de arena inválido"); continue
		var arena = read_json(root + "/arenas/" + id + ".json")
		if arena != null:
			_fields(arena,{"id":TYPE_STRING,"name":TYPE_STRING,"color":TYPE_ARRAY},root+"/arenas/"+id+".json")
			if not arena.get("color") is Array or arena.color.size()!=3: errors.append(root+"/arenas/"+id+".json: color requer RGB")
			arenas[id] = arena
	return errors.is_empty() and not characters.is_empty() and not arenas.is_empty()

func _fields(data: Dictionary, fields: Dictionary, path: String):
	for key in fields:
		if typeof(data.get(key))!=fields[key]: errors.append(path+": "+key+" ausente ou tipo inválido")

func _numbers(data: Dictionary, fields: Array, path: String):
	for key in fields:
		if not _number(data.get(key)) or data[key]<0: errors.append(path+": "+key+" deve ser número não negativo")

func validate_character(data: Dictionary,path: String):
	_fields(data.profile,{"id":TYPE_STRING,"nome":TYPE_STRING,"titulo":TYPE_STRING,"passiva":TYPE_STRING,"cor":TYPE_ARRAY},path+" profile")
	_numbers(data.profile,["defesa","regen","dano","alcance"],path+" profile")
	if data.profile.get("cor") is Array:
		if data.profile.cor.size()!=3: errors.append(path+": profile.cor requer RGB")
		for value in data.profile.cor:
			if not _number(value): errors.append(path+": profile.cor inválida")
	_fields(data.kit,{"id":TYPE_STRING,"origin":TYPE_STRING,"affiliation":TYPE_STRING,"archetype":TYPE_STRING,"visual":TYPE_STRING,"mobility":TYPE_DICTIONARY,"charge":TYPE_BOOL,"armor":TYPE_BOOL,"aerial_projectile":TYPE_BOOL},path+" kit")
	_numbers(data.kit,["tempo","hit_energy","block_energy","parry_window","projectile_speed","stamina_regen","heal_on_hit"],path+" kit")
	if data.kit.get("mobility") is Dictionary:
		_fields(data.kit.mobility,{"name":TYPE_STRING},path+" kit.mobility")
		_numbers(data.kit.mobility,["speed","duration","cost","invulnerability"],path+" kit.mobility")
	if data.forms.is_empty(): errors.append(path+": forms deve conter ao menos uma forma")
	for index in range(data.forms.size()):
		var form=data.forms[index]; var location=path+" forms[%d]"%index
		if not form is Dictionary: errors.append(location+": deve ser objeto"); continue
		_fields(form,{"name":TYPE_STRING,"technique":TYPE_STRING,"reflect":TYPE_BOOL},location)
		_numbers(form,["cost","duration","exhaustion","damage","speed","reach","absorption","regen"],location)
	for key in data.moves:
		var move=data.moves[key]; var location=path+" moves."+key
		if not move is Dictionary: continue
		_fields(move,{"nome":TYPE_STRING,"estado":TYPE_STRING,"tipo":TYPE_STRING,"queda":TYPE_BOOL,"cancel_on_hit":TYPE_BOOL,"hits":TYPE_ARRAY,"hitboxes":TYPE_ARRAY},location)
		_numbers(move,["empurrao","knockdown"],location)
		if move.get("hits") is Array:
			var previous=-1.0
			if move.hits.is_empty(): errors.append(location+": hits não pode ser vazio")
			for value in move.hits:
				if not _number(value): errors.append(location+": hits deve conter números"); continue
				if value<0 or value<=previous or (_number(move.get("active")) and value>=move.active): errors.append(location+": hits deve crescer dentro da janela ativa")
				previous=value
		if move.get("hitboxes") is Array:
			for box in move.hitboxes:
				if not box is Dictionary: errors.append(location+": hitboxes requer objetos"); continue
				_numbers(box,["time","reach","y","height"],location+" hitboxes")
	for field in ["sprite","released_sprite"]:
		if not data[field] is String or not ResourceLoader.exists(data[field]): errors.append(path+": "+field+" recurso ausente")

func _number(value) -> bool:
	return typeof(value) in [TYPE_INT, TYPE_FLOAT] and is_finite(float(value))
