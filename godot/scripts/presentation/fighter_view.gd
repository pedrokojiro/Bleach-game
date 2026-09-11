extends Node2D
var fighter
var sprite=Sprite2D.new()
var normal: Texture2D
var released: Texture2D
var tint=Color.WHITE

func setup(p,color: Color=Color.WHITE):
	fighter=p; tint=color
	normal=load(p.data.sprite); released=load(p.data.released_sprite)
	sprite.texture=normal; sprite.hframes=8; sprite.vframes=p.data.animation_states.size()
	sprite.position=Vector2(10,-96); add_child(sprite)

func _process(_dt):
	if fighter==null: return
	position=Vector2(fighter.rect().get_center().x,fighter.y+fighter.profile.altura)
	sprite.texture=released if fighter.form_index>=0 else normal
	var row=fighter.data.animation_states.find(fighter.state)
	sprite.frame=maxi(0,row)*8+int(fighter.animation_time*12)%8
	sprite.flip_h=fighter.direction<0
	sprite.modulate=tint.lerp(Color.WHITE,.65) if fighter.state=="HITSTUN" else tint
	queue_redraw()

func _draw():
	if fighter==null: return
	draw_set_transform(Vector2.ZERO,0,Vector2(1,.2)); draw_circle(Vector2.ZERO,48,Color(0,0,0,.4)); draw_set_transform(Vector2.ZERO)
	var c=Color(fighter.profile.cor[0]/255.0,fighter.profile.cor[1]/255.0,fighter.profile.cor[2]/255.0)
	if fighter.form_index>=0:
		for i in range(3):
			var r=55+i*9+sin(fighter.animation_time*4+i)*5
			draw_arc(Vector2(0,-75),r,0,TAU,48,Color(c,.18-i*.04),2,true)
	if fighter.state=="DASH":
		for i in range(4): draw_line(Vector2(-fighter.direction*(25+i*12),-70+i*10),Vector2(-fighter.direction*(100+i*16),-70+i*10),Color(c,.4-i*.08),3,true)
	if not fighter.action.is_empty() and fighter.action_time>=fighter.action.startup and fighter.action_time<fighter.action.startup+fighter.action.active:
		draw_arc(Vector2(fighter.direction*45,-80),75,-1.2 if fighter.direction>0 else 1.9,1.2 if fighter.direction>0 else 4.3,24,Color(c,.8),5,true)
	if fighter.charging: draw_arc(Vector2(fighter.direction*45,-75),12+fighter.charge_time*24,0,TAU,32,c,3,true)
