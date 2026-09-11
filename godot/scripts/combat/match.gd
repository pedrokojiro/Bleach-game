extends RefCounted
const Fighter=preload("res://scripts/combat/fighter.gd")
const Bot=preload("res://scripts/ai/controller.gd")
var players=[]
var projectiles=[]
var bots=[Bot.new(),Bot.new()]
var mode="PVE"
var phase="INTRO"
var phase_time=2.4
var time=99.0
var wins=[0,0]
var round_number=1
var winner=-1
var result=""
var hitstop=0.0
var effects={"hitstop":.045,"heavy_hitstop":.09}
var events=[]
var options: Dictionary
var dummy="PARADO"
var after_hit=false
var training_resources=true
var training_restore=true
var recording=false
var playback=false
var tape=[]
var tape_index=0
var input_history=[]

func _init(first: Dictionary,second: Dictionary,play_mode: String="PVE",config: Dictionary={}):
	players=[Fighter.new(first,540),Fighter.new(second,1040)]
	mode=play_mode; options=config; dummy=options.get("dummy","PARADO")
	training_resources=options.get("training_resources",true); training_restore=options.get("training_restore",true)
	reset_round()

func reset_round():
	players[0].reset(540); players[1].reset(1040,false); projectiles=[]; hitstop=0; events=[]
	time=options.get("round_seconds",99); phase="INTRO"; phase_time=2.4; after_hit=false
	for bot in bots: bot.timer=0; bot.sequence=0
	if mode=="TREINO":
		phase="FIGHT"; time=INF
		for p in players:
			p.hp=p.profile.vida*options.get("training_health",1.0)
			if training_resources: p.energy=p.profile.reiatsu; p.stamina=100

func reset_training():
	reset_round(); recording=false; playback=false; tape_index=0; input_history=[]

func apply_input(p,frame: Dictionary):
	p.movement=frame.get("movement",0); p.guard=frame.get("guard",false); p.running=frame.get("run",false)
	for key in frame.get("actions",[]):
		if key=="charge_start": p.set_charge(true)
		elif key=="charge_end": p.set_charge(false)
		else: p.command(key)

func tick(dt: float,frames: Array=[]):
	if phase in ["INTRO","KO"]:
		phase_time-=dt
		if phase_time<=0:
			if phase=="INTRO": phase="FIGHT"
			elif winner>=0: phase="VICTORY"
			else:
				if result!="EMPATE": round_number+=1
				reset_round()
		return
	if phase!="FIGHT": return
	if hitstop>0: hitstop=maxf(0,hitstop-dt); return
	if frames.is_empty(): frames=[{},{}]
	var first=frames[0]
	var second=frames[1]
	if recording:
		second=first.duplicate(true); first={}
		if tape.size()<120*15: tape.append(second)
		else: recording=false
	elif playback and not tape.is_empty():
		second=tape[tape_index]; tape_index=(tape_index+1)%tape.size()
	for action_name in first.get("actions",[]):
		input_history.push_front(action_name)
		if input_history.size()>10: input_history.pop_back()
	apply_input(players[0],first)
	if mode=="PVP" or recording or playback: apply_input(players[1],second)
	elif mode=="PVE": bots[1].tick(dt,players[1],players[0],projectiles,options.get("difficulty",1))
	else:
		players[1].movement=0; players[1].running=false
		players[1].guard=dummy=="DEFESA" or (dummy=="APÓS ACERTO" and after_hit)
		if dummy=="PARRY": players[1].command("parry")
		elif dummy=="CPU": bots[1].tick(dt,players[1],players[0],projectiles,options.get("difficulty",1))
	if mode=="TREINO" and training_resources:
		for p in players: p.energy=p.profile.reiatsu; p.stamina=100
	players[0].tick(dt,players[1]); players[1].tick(dt,players[0]); separate()
	for q in projectiles:
		q.x+=q.vx*dt; q.y+=q.vy*dt; q.life-=dt
	resolve()
	for p in players:
		for event in p.events:
			events.append({"kind":event,"position":p.rect().get_center(),"color":Color(p.profile.cor[0]/255.0,p.profile.cor[1]/255.0,p.profile.cor[2]/255.0)})
			if event in ["hit","heavy","parry","ko"]: hitstop=maxf(hitstop,effects.heavy_hitstop if event in ["heavy","ko"] else effects.hitstop)
		p.events.clear()
	if mode=="TREINO":
		for p in players:
			if p.hp<=0:
				p.hp=p.profile.vida*options.get("training_health",1.0); p.cancel(); p.change("IDLE"); p.invulnerability=.6
			elif training_restore and players[0].combo_time<=0 and players[1].combo_time<=0 and p.state=="IDLE":
				p.hp=p.profile.vida*options.get("training_health",1.0)
	else:
		time=maxf(0,time-dt)
		if time<=0 or players[0].hp<=0 or players[1].hp<=0: finish_round()

func separate():
	var a=players[0]; var b=players[1]
	if not a.pushbox().intersects(b.pushbox()): return
	var left=a if a.x<b.x else b
	var right=b if a.x<b.x else a
	var overlap=left.pushbox().end.x-right.pushbox().position.x
	left.x-=overlap/2; right.x+=overlap/2; left.sync(); right.sync()
	overlap=left.pushbox().end.x-right.pushbox().position.x
	if overlap>0:
		if left.x<=24: right.x+=overlap
		else: left.x-=overlap
		left.sync(); right.sync()

func spawn_projectile(p,move: Dictionary):
	var q={"owner":p,"move":move.duplicate(true),"x":p.rect().get_center().x+p.direction*48,"y":p.rect().get_center().y,
		"vx":p.direction*p.kit.projectile_speed,"vy":240 if not p.grounded and p.kit.aerial_projectile else 0,"life":1.8,"direction":p.direction}
	if move.tipo=="wave": q.y=555; q.vx=p.direction*420
	if move.tipo=="trap": q.x+=p.direction*180; q.y=551; q.vx=0; q.life=3
	projectiles.append(q)

func resolve():
	var hits=[]
	for i in range(2):
		var p=players[i]; var target=players[1-i]; var move=p.action
		if move.is_empty() or p.action_time<move.startup or p.action_time>=move.startup+move.active: continue
		for slot in range(move.hits.size()):
			var end=move.hits[slot+1] if slot+1<move.hits.size() else move.active
			if slot in p.hit_slots or p.action_time<move.startup+move.hits[slot] or p.action_time>=move.startup+end: continue
			if move.tipo in ["projectile","wave","trap"]: spawn_projectile(p,move); p.hit_slots.append(slot)
			elif move.tipo=="barrier": p.barrier=2.5; p.hit_slots.append(slot); p.emit("parry")
			elif p.hitbox().intersects(target.hurtbox()) and (move.tipo!="grab" or (p.grounded and target.grounded)):
				hits.append([p,target,move,slot])
	for hit in hits:
		var result_hit=hit[1].receive(hit[2],hit[0])
		if result_hit!="miss": hit[0].confirmed=true; hit[0].hit_slots.append(hit[3])
		if hit[1]==players[1] and result_hit=="hit": after_hit=true
	for q in projectiles:
		if q.life<=0: continue
		for p in players:
			if p==q.owner or q.life<=0 or not Rect2(q.x-20,q.y-12,40,24).intersects(p.hurtbox()): continue
			if p.form().get("reflect",false) and p.barrier>0:
				q.owner=p; q.vx=-q.vx; q.direction=-q.direction; q.x+=q.direction*70; p.announce("REFLEXÃO"); break
			var outcome=p.receive(q.move,q.owner,true)
			if outcome!="miss": q.life=0
			if p==players[1] and outcome=="hit": after_hit=true
	projectiles=projectiles.filter(func(q): return q.life>0 and q.x>-80 and q.x<1780 and q.y<=600)

func finish_round():
	var a=players[0].hp/players[0].profile.vida
	var b=players[1].hp/players[1].profile.vida
	result="EMPATE"
	if absf(a-b)>0.00000001:
		var win=0 if a>b else 1
		wins[win]+=1; players[win].change("VICTORY")
		result="K.O." if minf(players[0].hp,players[1].hp)<=0 else "TEMPO ESGOTADO"
		if wins[win]>=options.get("wins",2): winner=win
	phase="KO"; phase_time=2.5
	for p in players: p.buffer=[]; p.movement=0
