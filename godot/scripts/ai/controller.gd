extends RefCounted
var timer=0.0
var sequence=0

func tick(dt: float,p,other,projectiles: Array,difficulty: int):
	timer-=dt
	if timer>0: return
	timer=[.32,.19,.105][difficulty]
	var distance=absf(p.rect().get_center().x-other.rect().get_center().x)
	var direction=signf(other.x-p.x)
	p.guard=false; p.running=false
	var ranged=p.kit.archetype=="distância"
	var ideal=330 if ranged else 88
	for q in projectiles:
		if q.owner!=p and absf(q.x-p.x)<220 and (p.x-q.x)*q.vx>0:
			p.movement=0
			if difficulty>0: p.command("jump")
			else: p.guard=true
			return
	var threat=not other.action.is_empty() and distance<other.action.alcance+100
	if threat and p.action.is_empty():
		if p.moves.special2.tipo=="barrier" and p.barrier<=0 and p.energy>=p.moves.special2.custo and p.cooldowns.get("special2",0)<=0:
			p.command("special2"); return
		p.movement=0; p.guard=true
		if difficulty==2 and p.stamina>35 and sequence%3==0: p.command("parry")
		sequence+=1; return
	var next=p.form_index+1
	if next<p.data.forms.size() and p.energy>=p.data.forms[next].cost and p.hp<p.profile.vida*.65:
		p.command("release"); return
	if p.form_index>=0 and p.energy>=15 and distance<280 and p.cooldowns.get("exclusive",0)<=0:
		p.command("exclusive"); return
	if not p.action.is_empty() and p.confirmed and p.combo<difficulty+2:
		p.command("heavy" if p.combo>=2 else "light"); return
	p.movement=direction if distance>ideal+35 else (-direction if ranged and distance<ideal-75 else 0)
	if distance>420 and not ranged and p.stamina>50: p.command("dash")
	if p.energy>=p.moves.special.custo and distance<650 and p.cooldowns.get("special",0)<=0:
		if (p.moves.special.tipo=="projectile" and distance>160) or (p.moves.special.tipo!="projectile" and distance<190):
			p.command("special"); return
	var second=p.moves.special2
	if p.energy>=second.custo and p.cooldowns.get("special2",0)<=0:
		if (second.tipo=="trap" and distance>160 and distance<380) or (second.tipo=="wave" and distance<350):
			p.command("special2"); return
	if p.energy>=75 and distance<280 and not other.action.is_empty(): p.command("ultimate"); return
	if distance<130:
		sequence+=1
		p.command("grab" if other.state=="BLOCK" and distance<65 else ("heavy" if sequence%4==0 or not other.grounded else "light"))
