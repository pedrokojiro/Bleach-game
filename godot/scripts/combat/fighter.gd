extends RefCounted

const FREE = ["IDLE","WALK","RUN","JUMP","FALL","EXHAUSTED"]
const LOCKED = ["HITSTUN","BLOCKSTUN","KNOCKDOWN","GET_UP","RELEASE","LAND","PARRY","DASH"]
var data: Dictionary
var profile: Dictionary
var kit: Dictionary
var moves: Dictionary
var x = 0.0
var y = 0.0
var vx = 0.0
var vy = 0.0
var direction = 1
var grounded = true
var hp = 0.0
var energy = 45.0
var stamina = 100.0
var state = "IDLE"
var state_time = 0.0
var animation_time = 0.0
var action: Dictionary = {}
var action_time = 0.0
var hit_slots = []
var confirmed = false
var form_index = -1
var form_time = 0.0
var exhaustion = 0.0
var invulnerability = 0.0
var barrier = 0.0
var combo = 0
var combo_damage = 0.0
var combo_time = 0.0
var last_damage = 0.0
var last_advantage = 0.0
var cooldowns = {}
var buffer = []
var movement = 0.0
var running = false
var guard = false
var charging = false
var charge_time = 0.0
var charge_ready = 0.0
var message = ""
var message_time = 0.0
var events = []

func _init(definition: Dictionary, spawn: float = 540.0):
	data = definition; profile = data.profile; kit = data.kit
	reset(spawn)

func reset(spawn: float, right: bool = true):
	x = spawn; y = 580.0-profile.altura; vx=0; vy=0; direction=1 if right else -1; grounded=true
	hp=profile.vida; energy=45; stamina=100; state="IDLE"; state_time=0; animation_time=0
	action={}; action_time=0; hit_slots=[]; confirmed=false; form_index=-1; form_time=0
	exhaustion=0; invulnerability=0; barrier=0; combo=0; combo_damage=0; combo_time=0
	cooldowns={}; buffer=[]; movement=0; running=false; guard=false; charging=false; charge_time=0; charge_ready=0
	message=""; message_time=0; events=[]; moves=data.moves.duplicate(true)

func form() -> Dictionary:
	return data.forms[form_index] if form_index>=0 else {}

func change(value: String, duration: float = 0):
	state=value; state_time=duration; animation_time=0

func can_act() -> bool:
	return hp>0 and state in FREE

func command(value: String):
	buffer.append([value,.15])
	if buffer.size()>4: buffer.pop_front()

func gain(value: float): energy=minf(profile.reiatsu,energy+value)
func rect() -> Rect2: return Rect2(round(x),round(y),profile.largura,profile.altura)
func hurtbox() -> Rect2: return rect().grow(-4)
func pushbox() -> Rect2: return Rect2(round(x)+5,round(y)+4,profile.largura-10,profile.altura-8)
func sync(): x=clampf(x,24,1700-profile.largura-24)

func hitbox() -> Rect2:
	if action.is_empty(): return Rect2()
	var reach=action.alcance*form().get("reach",1.0)
	var offset_y=20.0
	var height=profile.altura-30.0
	for box in action.get("hitboxes",[]):
		if action_time>=action.startup+box.time:
			reach=box.reach*form().get("reach",1.0); offset_y=box.y; height=box.height
	if action.tipo=="pulse": return rect().grow_individual(reach,40,reach,40)
	var center=rect().get_center().x
	return Rect2(center if direction>0 else center-reach-profile.largura/2,rect().position.y+offset_y,reach+profile.largura/2,height)

func cancel():
	action={}; buffer=[]; charging=false; charge_ready=0

func announce(value: String): message=value; message_time=1.25
func emit(value: String): events.append(value)

func execute(key: String) -> bool:
	if key=="light" and not grounded: key="air"
	if moves.has(key):
		if key=="exclusive" and form_index<0: return false
		var can_cancel=not action.is_empty() and confirmed and action.get("cancel_on_hit",false) and action_time>=action.startup
		if not (can_act() or can_cancel): return false
		var move=moves[key].duplicate(true)
		if key=="special" and charge_ready>0:
			move.dano*=1+charge_ready; move.custo+=10*charge_ready
		if cooldowns.get(key,0)>0 or energy<move.custo: return false
		energy-=move.custo; cooldowns[key]=move.cooldown
		action=move; action_time=0; hit_slots=[]; confirmed=false; charging=false; charge_ready=0
		change(move.estado); vx*=.2
		if move.custo>0: announce(move.nome); emit("special")
		return true
	if key=="parry":
		if not (can_act() or state=="BLOCK") or stamina<18: return false
		stamina-=18; change("PARRY",.32); return true
	if not can_act(): return false
	match key:
		"jump":
			if not grounded: return false
			vy=-740; grounded=false; change("JUMP"); emit("jump"); return true
		"dash":
			if stamina<kit.mobility.cost: return false
			stamina-=kit.mobility.cost; change("DASH",kit.mobility.duration)
			vx=(movement if movement!=0 else direction)*kit.mobility.speed
			invulnerability=kit.mobility.invulnerability; emit("dash"); return true
		"release":
			var next=form_index+1
			if next>=data.forms.size() or exhaustion>0: return false
			var f=data.forms[next]
			if energy<f.cost: return false
			energy-=f.cost; form_index=next; form_time=f.duration; charging=false
			moves=data.moves.duplicate(true); moves.exclusive.nome=f.technique
			if next>0:
				moves.exclusive.hits=[0,.10]; moves.exclusive.dano=27
			invulnerability=.7; change("RELEASE",.7); announce(f.name); emit("release"); return true
	return false

func set_charge(held: bool):
	if not kit.charge: return
	if held and can_act() and not charging: charging=true; charge_time=0
	elif not held and charging:
		charge_ready=minf(1,charge_time); charging=false; command("special")

func receive(move: Dictionary, attacker, projectile: bool = false) -> String:
	if hp<=0 or invulnerability>0: return "miss"
	var frontal=(attacker.rect().get_center().x-rect().get_center().x)*direction>=0
	if state=="PARRY" and state_time>.32-kit.parry_window and move.tipo!="grab" and frontal:
		gain(15); announce("PARRY"); emit("parry")
		if not projectile: attacker.cancel(); attacker.change("HITSTUN",.42)
		return "parry"
	var blocked=state in ["BLOCK","BLOCKSTUN"] and frontal and move.tipo!="grab"
	var counter=not action.is_empty() and action_time<action.startup
	var scale=maxf(.35,1-attacker.combo*.12) if attacker.combo_time>0 else 1
	var damage=move.dano*scale*(1-profile.defesa)*attacker.form().get("damage",1.0)
	if blocked:
		stamina=maxf(0,stamina-move.dano*.8); damage*=.15; change("BLOCKSTUN",move.blockstun); gain(kit.block_energy)
		if stamina<=0: change("HITSTUN",.7); announce("GUARDA QUEBRADA")
		emit("block")
	else:
		var armor=kit.armor and not action.is_empty() and action.estado=="ATTACK_HEAVY" and action_time<action.startup+action.active
		if barrier>0: damage*=.55
		damage*=form().get("absorption",1.0)
		if counter: damage*=1.15; attacker.announce("COUNTER")
		if not armor: cancel(); change("KNOCKDOWN" if move.queda else "HITSTUN",move.knockdown if move.queda else move.hitstun)
		emit("heavy" if move.queda else "hit")
		if attacker.combo_time<=0: attacker.combo=0; attacker.combo_damage=0
		attacker.combo+=1; attacker.combo_damage+=damage; attacker.combo_time=1.05
		attacker.gain(attacker.kit.hit_energy)
		if attacker.hp>0: attacker.hp=minf(attacker.profile.vida,attacker.hp+attacker.kit.heal_on_hit)
	hp=maxf(0,hp-damage); vx=attacker.direction*move.empurrao/profile.peso*(.4 if blocked else 1)
	gain(damage*.2); attacker.last_damage=damage
	attacker.last_advantage=(state_time-maxf(0,move.startup+move.active+move.recovery-attacker.action_time))*120
	if hp<=0: form_index=-1; form_time=0; moves=data.moves.duplicate(true); cancel(); change("DEFEAT"); emit("ko")
	return "block" if blocked else "hit"

func tick(dt: float, other):
	if charging:
		if can_act(): charge_time=minf(1,charge_time+dt)
		else: charging=false
	animation_time+=dt; message_time=maxf(0,message_time-dt)
	invulnerability=maxf(0,invulnerability-dt); barrier=maxf(0,barrier-dt); exhaustion=maxf(0,exhaustion-dt)
	combo_time=maxf(0,combo_time-dt)
	if combo_time<=0: combo=0; combo_damage=0
	for key in cooldowns: cooldowns[key]=maxf(0,cooldowns[key]-dt)
	if form_index>=0:
		gain(form().regen*dt)
		if form().duration>0:
			form_time-=dt
			if form_time<=0:
				exhaustion=form().exhaustion; form_index=-1; form_time=0; moves=data.moves.duplicate(true); announce("EXAUSTÃO")
	elif exhaustion<=0: gain(profile.regen*dt)
	stamina=minf(100,stamina+dt*(7 if guard else kit.stamina_regen))
	if hp<=0: return
	if state in LOCKED:
		state_time-=dt
		if state_time<=0:
			if state=="KNOCKDOWN": change("GET_UP",.25); invulnerability=.25
			else: change("IDLE")
	if state in FREE or state=="BLOCK":
		direction=1 if other.rect().get_center().x>=rect().get_center().x else -1
		if guard and grounded and stamina>0: state="BLOCK"; stamina=maxf(0,stamina-dt*12)
		elif state=="BLOCK": change("IDLE")
	for entry in buffer.duplicate():
		entry[1]-=dt
		if execute(entry[0]): buffer.erase(entry); break
		if entry[1]<=0: buffer.erase(entry)
	if not action.is_empty():
		action_time+=dt
		if action_time>=action.startup+action.active+action.recovery: action={}; change("IDLE")
	if can_act():
		var speed=profile.velocidade*(1.3 if running else 1)*form().get("speed",1.0)*(.72 if exhaustion>0 else 1)*(.45 if charging else 1)
		vx+=clampf(movement*speed-vx,-2300*dt,2300*dt)
		if grounded: state=("RUN" if running else "WALK") if movement!=0 else ("EXHAUSTED" if exhaustion>0 else "IDLE")
	elif state!="DASH": vx*=maxf(0,1-dt*8)
	if not action.is_empty() and action.tipo=="rush" and action_time<action.startup+action.active: vx=direction*650
	x+=vx*dt
	if not grounded:
		vy+=1900*dt; y+=vy*dt
		if can_act(): state="JUMP" if vy<0 else "FALL"
		if y+profile.altura>=580:
			y=580-profile.altura; vy=0; grounded=true; emit("land")
			if can_act(): change("LAND",.065)
	sync()
