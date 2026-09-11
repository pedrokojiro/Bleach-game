extends Node2D
var arena_id="soul_society"
var elapsed=0.0
var camera_x=0.0

func _process(dt): elapsed+=dt; queue_redraw()

func _draw():
	for y in range(0,720,8):
		var c=Color("071221").lerp(Color("243c50"),float(y)/900)
		if arena_id=="hueco_mundo": c=Color("050c14").lerp(Color("263444"),float(y)/1100)
		draw_rect(Rect2(camera_x,y,1280,8),c)
	for i in range(90):
		var p=Vector2(fmod(i*137.7,1700),fmod(i*73.1,390))
		draw_circle(p,1 if i%3 else 1.6,Color(.55,.8,.9,.3+.2*sin(elapsed+i)))
	var moon=Vector2(1090-camera_x*.08,145)
	for i in range(8,0,-1): draw_circle(moon,62+i*7,Color(.5,.8,.9,.008))
	draw_circle(moon,61,Color("d6e9eb"))
	if arena_id=="hueco_mundo": draw_circle(moon+Vector2(22,-16),55,Color("0a1520"))
	if arena_id=="soul_society":
		for layer in range(3):
			for i in range(9):
				var x=i*240-camera_x*.08*(3-layer)
				var y=360+layer*60
				var c=Color(.045+layer*.025,.08+layer*.025,.13+layer*.03)
				draw_rect(Rect2(x,y,170,580-y),c)
				for tier in range(3):
					var yy=y-tier*24
					draw_colored_polygon(PackedVector2Array([Vector2(x-35,yy),Vector2(x+85,yy-38),Vector2(x+205,yy)]),c.lightened(.04))
		for x in range(70,1700,320):
			draw_rect(Rect2(x,385,20,195),Color("172a39")); draw_line(Vector2(x-28,389),Vector2(x+49,389),Color("74909a"),3)
			for i in range(4): draw_circle(Vector2(x+10,420),12+i*5,Color(1,.72,.3,.035))
			draw_rect(Rect2(x+4,411,12,20),Color("efc679"))
	elif arena_id=="karakura":
		for i in range(15):
			var h=160+fmod(i*91,160); var x=i*130
			draw_rect(Rect2(x,580-h,116,h),Color("132332"))
			for wx in range(5):
				for wy in range(6): draw_rect(Rect2(x+10+wx*20,585-h+wy*25,8,13),Color("b19b69") if (wx+wy+i)%3 else Color("263e50"))
		for x in range(100,1700,400):
			draw_line(Vector2(x,580),Vector2(x,360),Color("425b65"),5)
			draw_line(Vector2(x,360),Vector2(x+40,360),Color("86aeb8"),4)
			draw_colored_polygon(PackedVector2Array([Vector2(x+30,365),Vector2(x-50,580),Vector2(x+130,580)]),Color(.8,.9,1,.035))
	else:
		for i in range(13):
			var x=i*160; var y=380+fmod(i*53,100)
			draw_line(Vector2(x,580),Vector2(x+25,y),Color("6b8393"),8)
			draw_line(Vector2(x+18,y+45),Vector2(x-30,y+15),Color("6b8393"),5)
			draw_line(Vector2(x+22,y+30),Vector2(x+60,y-10),Color("6b8393"),4)
	var floor_color=Color("acbdc8") if arena_id=="hueco_mundo" else Color("263946")
	draw_rect(Rect2(0,580,1700,140),floor_color)
	draw_line(Vector2(0,580),Vector2(1700,580),Color("afc2c5"),3)
	for x in range(-300,1950,110): draw_line(Vector2(x,580),Vector2(x-100,720),floor_color.darkened(.18),2)
	for y in [610,655,710]: draw_line(Vector2(0,y),Vector2(1700,y),floor_color.darkened(.2),2)
	for i in range(30):
		var x=fmod(i*67+elapsed*(6+i%4),1700)
		var y=300+fmod(i*39+sin(elapsed+i)*15,260)
		draw_circle(Vector2(x,y),1.4,Color(.6,.87,1,.4))
