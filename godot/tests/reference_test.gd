extends SceneTree

func _init():
	var catalog=load("res://scripts/data/catalog.gd").new()
	if not catalog.load_all():
		printerr(catalog.errors); quit(1); return
	var factory=load("res://scripts/combat/fighter.gd")
	var vectors=JSON.parse_string(FileAccess.get_file_as_string("res://content/reference.json"))
	var failures=[]
	for vector in vectors:
		var p=factory.new(catalog.characters[vector.id],400)
		var target=factory.new(catalog.characters.vastor,1400)
		p.energy=p.profile.reiatsu
		if vector.command=="walk": p.movement=1
		else: p.execute(vector.command)
		for i in range(vector.steps): p.tick(1.0/120,target)
		for pair in [["x",p.x],["y",p.y],["energy",p.energy],["stamina",p.stamina]]:
			if absf(pair[1]-vector[pair[0]])>.001: failures.append("%s/%s %s: %s != %s" % [vector.id,vector.command,pair[0],pair[1],vector[pair[0]]])
		if p.state!=vector.state: failures.append("%s/%s state: %s != %s" % [vector.id,vector.command,p.state,vector.state])
	if not failures.is_empty(): printerr(failures); quit(1)
	else: print("PASS: 20 Python/Godot vectors, position/resources/state tolerance 0.001"); quit(0)
