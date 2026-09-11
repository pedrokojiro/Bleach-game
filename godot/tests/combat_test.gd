extends SceneTree
const Catalog=preload("res://scripts/data/catalog.gd")
const MatchModel=preload("res://scripts/combat/match.gd")
const Fighter=preload("res://scripts/combat/fighter.gd")
var c=Catalog.new()
var checks=0
var failures=[]

func check(value: bool,label: String):
	checks+=1
	if not value: failures.append(label)

func pair(a="kensei",b="vastor",mode="PVP"):
	var m=MatchModel.new(c.characters[a],c.characters[b],mode)
	m.phase="FIGHT"; m.players[0].x=600; m.players[1].x=690
	return m

func advance(m,seconds):
	for i in range(roundi(seconds*120)): m.tick(1.0/120); m.events.clear()

func _init():
	check(c.load_all(),"catalog load")
	if not failures.is_empty(): printerr(c.errors); quit(1); return
	var ids=["kensei","vastor"] if "--slice" in OS.get_cmdline_user_args() else c.ids
	for id in ids:
		var m=pair(id); var p=m.players[0]; var target=m.players[1]
		p.execute("light"); advance(m,.05); check(target.hp==target.profile.vida,id+" startup")
		advance(m,.15); check(target.hp<target.profile.vida,id+" hit")
		var hp=target.hp; advance(m,.4); check(target.hp==hp,id+" single hit")
		m=pair(id); p=m.players[0]; target=m.players[1]
		target.change("BLOCK"); target.direction=-1
		check(target.receive(p.moves.light,p)=="block",id+" block")
		target.change("PARRY",.32); hp=target.hp
		check(target.receive(p.moves.light,p)=="parry" and target.hp==hp,id+" parry")
		target.change("BLOCK"); check(target.receive(p.moves.grab,p)=="hit",id+" grab")
		m=pair(id); p=m.players[0]
		for form in p.data.forms:
			p.energy=p.profile.reiatsu
			check(p.execute("release"),id+" form "+form.name)
			advance(m,.75)
		check(p.form_index>=0,id+" form active")
		advance(m,p.form().duration+.1); check(p.form_index<0 and p.exhaustion>0,id+" exhaustion")
		m=pair(id); p=m.players[0]; target=m.players[1]; target.hp=999
		p.energy=130; p.execute("ultimate"); advance(m,1.1)
		check(p.combo>=1,id+" ultimate hits")
		m=pair(id); p=m.players[0]; p.execute("light"); check(not p.execute("heavy"),id+" whiff cancel")
		m=pair(id); p=m.players[0]; target=m.players[1]; target.x=p.x+p.profile.largura+9
		for action in ["light","light","heavy"]:
			var before=p.combo; p.command(action)
			for i in range(120):
				m.tick(1.0/120)
				if p.combo>before: break
			check(p.combo>before,id+" combo "+action)
		m=pair(id,"vastor","TREINO"); p=m.players[0]
		p.energy=0; m.tick(1.0/120)
		check(is_inf(m.time) and p.energy>0,id+" training resources")
		m.players[1].hp=0; m.tick(1.0/120)
		check(m.phase=="FIGHT" and m.players[1].hp>0,id+" training revive")
		m.recording=true
		m.tick(1.0/120,[{"actions":["light"]},{}])
		check(m.tape.size()==1 and not m.players[1].action.is_empty(),id+" recording dummy")
		m.recording=false; m.playback=true; m.tape_index=0; m.players[1].reset(900,false); m.tick(1.0/120)
		check(not m.players[1].action.is_empty(),id+" playback dummy")
		m=pair(id); m.players[0].hp=0; m.players[1].hp=0; m.finish_round()
		check(m.result=="EMPATE" and m.wins==[0,0],id+" double KO")
		m=pair(id)
		for round_index in range(2):
			m.phase="FIGHT"; m.players[1].hp=0; m.finish_round(); advance(m,2.6)
		check(m.phase=="VICTORY" and m.winner==0,id+" match victory")
	if not "--slice" in OS.get_cmdline_user_args():
		var m=pair("zephyr","kurogane"); var p=m.players[0]; var t=m.players[1]
		p.set_charge(true)
		for i in range(120): p.tick(1.0/120,t)
		p.set_charge(false); p.tick(1.0/120,t)
		check(absf(p.action.dano-34)<.001,"charge damage")
		t.energy=110; t.execute("release"); t.barrier=2; m.spawn_projectile(p,p.moves.special)
		m.projectiles[0].x=t.rect().get_center().x; m.projectiles[0].y=t.rect().get_center().y; m.resolve()
		check(m.projectiles[0].owner==t,"projectile reflection")
	print("CHECKS: %d; FAILURES: %d" % [checks,failures.size()])
	if not failures.is_empty(): printerr(failures)
	quit(0 if failures.is_empty() else 1)
