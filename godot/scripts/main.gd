extends Node2D
const Catalog=preload("res://scripts/data/catalog.gd")
const Preferences=preload("res://scripts/data/preferences.gd")
const Controls=preload("res://scripts/controllers/player_input.gd")
const MatchModel=preload("res://scripts/combat/match.gd")
const FighterView=preload("res://scripts/presentation/fighter_view.gd")
const ArenaView=preload("res://scripts/presentation/arena_view.gd")
const SLICE=false
const GOLD=Color("e8be76")
const ICE=Color("82dce7")
const WHITE=Color("e5eff3")
var catalog=Catalog.new()
var prefs=Preferences.new()
var inputs=Controls.new()
var world=Node2D.new()
var arena=ArenaView.new()
var ui=CanvasLayer.new()
var menu=Control.new()
var model
var views=[]
var selected=[0,1]
var palettes=[0,0]
var palette_colors=[Color.WHITE,Color(1,.76,.5),Color(.8,.6,1),Color(.6,1,1)]
var arena_index=0
var play_mode="PVE"
var screen="title"
var paused=false
var capture_binding=""
var capture_type="keys"
var binding_button: Button
var palette_names=[]
var camera_x=210.0
var elapsed=0.0
var shake=0.0
var impact=0.0
var particles=[]
var font=ThemeDB.fallback_font
var effect_rect=ColorRect.new()
var music=AudioStreamPlayer.new()
var sfx=[]
var roster=[]
var environments=[]
var frame_count=0
var smoke=false
var focus_assigned=false

func _ready():
	prefs.load_saved(); inputs.setup(prefs.values)
	add_child(world); world.show_behind_parent=true; world.add_child(arena)
	var light=PointLight2D.new()
	var gradient=Gradient.new(); gradient.colors=PackedColorArray([Color(1,.85,.6,.24),Color(1,.85,.6,0)])
	var texture=GradientTexture2D.new(); texture.gradient=gradient; texture.width=256; texture.height=256
	texture.fill=GradientTexture2D.FILL_RADIAL; texture.fill_from=Vector2(.5,.5); texture.fill_to=Vector2(1,.5)
	light.texture=texture; light.texture_scale=3; light.position=Vector2(800,390); light.energy=.5; world.add_child(light)
	var effects=CanvasLayer.new(); effects.layer=1; add_child(effects)
	effect_rect.size=Vector2(1280,720); effect_rect.mouse_filter=Control.MOUSE_FILTER_IGNORE
	var material=ShaderMaterial.new(); material.shader=load("res://shaders/impact.gdshader"); effect_rect.material=material; effects.add_child(effect_rect)
	ui.layer=2; add_child(ui); ui.add_child(menu); menu.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	var theme=Theme.new(); theme.default_font_size=19
	for state in ["normal","hover","pressed","focus"]:
		var style=StyleBoxFlat.new(); style.bg_color=Color("142637") if state=="normal" else Color("254758")
		style.border_color=ICE if state!="normal" else Color("3c5c6a")
		style.set_border_width_all(1); style.set_corner_radius_all(5); style.content_margin_left=14; style.content_margin_right=14
		theme.set_stylebox(state,"Button",style)
	theme.set_color("font_color","Button",WHITE); theme.set_color("font_hover_color","Button",GOLD); menu.theme=theme
	if not catalog.load_all():
		label("CONTEÚDO INVÁLIDO",Vector2(80,90),32,GOLD)
		label("\n".join(catalog.errors),Vector2(80,150),18,WHITE)
		push_error("\n".join(catalog.errors)); return
	roster=catalog.ids.slice(0,2) if SLICE else catalog.ids
	palette_names=catalog.palette_data.names; palette_colors=[]
	for color in catalog.palette_data.colors: palette_colors.append(Color(color[0],color[1],color[2]))
	environments=catalog.arena_ids.slice(0,1) if SLICE else catalog.arena_ids
	music.stream=load(catalog.audio_data.menu); add_child(music); music.finished.connect(func(): music.play())
	if DisplayServer.get_name()!="headless": music.play()
	for i in range(8):
		var player=AudioStreamPlayer.new(); add_child(player); sfx.append(player)
	apply_display()
	show_title()
	smoke="--smoke" in OS.get_cmdline_user_args()
	if "--training" in OS.get_cmdline_user_args(): play_mode="TREINO"; start_match()

func apply_display():
	if not OS.has_feature("web"):
		DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_FULLSCREEN if prefs.values.fullscreen else DisplayServer.WINDOW_MODE_WINDOWED)
		if not prefs.values.fullscreen:
			DisplayServer.window_set_size([Vector2i(1280,720),Vector2i(1600,900),Vector2i(1920,1080)][clampi(prefs.values.resolution,0,2)])

func clear_menu():
	focus_assigned=false
	for node in menu.get_children(): menu.remove_child(node); node.queue_free()
	menu.modulate.a=0
	create_tween().tween_property(menu,"modulate:a",1.0,.18)

func label(value: String,pos: Vector2,size: int=20,color: Color=WHITE,parent: Node=menu) -> Label:
	var node=Label.new(); node.text=value; node.position=pos; node.add_theme_font_size_override("font_size",size); node.add_theme_color_override("font_color",color); parent.add_child(node); return node

func button(value: String,pos: Vector2,size: Vector2,callback: Callable,parent: Node=menu) -> Button:
	var node=Button.new(); node.text=value; node.position=pos; node.size=size; node.pressed.connect(callback); parent.add_child(node)
	if not focus_assigned: focus_assigned=true; _focus_if_attached.call_deferred(node)
	return node

func _focus_if_attached(node):
	if is_instance_valid(node) and node.is_inside_tree(): node.grab_focus()

func panel(pos: Vector2,size: Vector2,parent: Node=menu):
	var node=Panel.new(); node.position=pos; node.size=size; node.mouse_filter=Control.MOUSE_FILTER_IGNORE
	var style=StyleBoxFlat.new(); style.bg_color=Color(.035,.07,.11,.96); style.border_color=Color("34505e"); style.set_border_width_all(1); style.set_corner_radius_all(8)
	node.add_theme_stylebox_override("panel",style); parent.add_child(node)

func show_title():
	screen="title"; paused=false; clear_menu()
	label("UM FAN GAME • PERSONAGENS ORIGINAIS",Vector2(78,106),16,ICE)
	label("BLEACH",Vector2(70,158),100)
	label("SPIRITUAL CROSSROADS",Vector2(80,278),31,GOLD)
	label("A lâmina. O vazio. O espírito.",Vector2(83,336),23)
	button("ENTRAR NA ARENA",Vector2(82,430),Vector2(350,54),show_select)
	button("CONFIGURAÇÕES",Vector2(82,500),Vector2(350,48),func(): show_options("title"))
	label("Godot Edition / Windows + Web",Vector2(82,652),15,ICE)
	if not OS.has_feature("web"): button("SAIR",Vector2(82,564),Vector2(350,44),func(): get_tree().quit())
	show_portrait(roster[0],Vector2(850,160),Vector2(320,370))

func show_portrait(id: String,pos: Vector2,size: Vector2):
	var p=catalog.characters[id]
	var image=TextureRect.new(); var atlas=AtlasTexture.new(); atlas.atlas=load(p.sprite)
	atlas.region=Rect2(95,211-p.profile.altura-25,100,190)
	image.texture=atlas; image.position=pos; image.size=size; image.stretch_mode=TextureRect.STRETCH_KEEP_ASPECT_CENTERED; image.expand_mode=TextureRect.EXPAND_IGNORE_SIZE
	menu.add_child(image)

func show_select():
	screen="select"; paused=false; clear_menu(); inputs.clear()
	label("ESCOLHA SEU DESTINO",Vector2(50,28),36)
	button("MODO: "+play_mode,Vector2(730,33),Vector2(230,40),func():
		var modes=["PVE","PVP","TREINO"]; play_mode=modes[(modes.find(play_mode)+1)%3]; show_select())
	button("VOLTAR",Vector2(980,33),Vector2(245,40),show_title)
	for side in range(2):
		var x=50+side*625; var p=catalog.characters[roster[selected[side]]]
		panel(Vector2(x,104),Vector2(575,443)); show_portrait(roster[selected[side]],Vector2(x+16,140),Vector2(150,245))
		label("P%d / %s" % [side+1,"BONECO" if side==1 and play_mode=="TREINO" else ("CPU" if side==1 and play_mode=="PVE" else "JOGADOR")],Vector2(x+190,126),15,ICE)
		label(p.profile.nome.to_upper(),Vector2(x+185,155),38)
		label(p.profile.titulo,Vector2(x+190,211),16,GOLD)
		label(p.kit.affiliation,Vector2(x+190,243),16)
		label(p.kit.archetype+" • "+p.kit.mobility.name,Vector2(x+190,277),16,ICE)
		label("VIDA %d  /  REIATSU %d" % [p.profile.vida,p.profile.reiatsu],Vector2(x+190,311),17)
		label(p.profile.passiva,Vector2(x+20,385),15)
		label(p.forms[0].name,Vector2(x+20,414),17,GOLD)
		button("<",Vector2(x+20,473),Vector2(65,42),func(): selected[side]=posmod(selected[side]-1,roster.size()); show_select())
		button(">",Vector2(x+100,473),Vector2(65,42),func(): selected[side]=(selected[side]+1)%roster.size(); show_select())
		button("COR: "+palette_names[palettes[side]],Vector2(x+205,473),Vector2(340,42),func(): palettes[side]=(palettes[side]+1)%palette_colors.size(); show_select())
	button("ARENA: "+catalog.arenas[environments[arena_index]].name,Vector2(50,573),Vector2(575,48),func(): arena_index=(arena_index+1)%environments.size(); arena.arena_id=environments[arena_index]; show_select())
	button("CONFIGURAR",Vector2(675,573),Vector2(240,48),func(): show_options("select"))
	button("INICIAR",Vector2(935,573),Vector2(315,48),start_match)
	label("A/D: P1 • Setas: P2 • Enter: iniciar • Tab: modo • Mouse ou controle nos botões",Vector2(85,665),17,ICE)

func start_match():
	for node in views: node.queue_free()
	views=[]; clear_menu(); screen="fight"; paused=false; inputs.clear()
	model=MatchModel.new(catalog.characters[roster[selected[0]]],catalog.characters[roster[selected[1]]],play_mode,prefs.values.duplicate(true))
	model.effects=catalog.effects_data
	arena.arena_id=environments[arena_index]
	for i in range(2):
		var view=FighterView.new(); view.setup(model.players[i],palette_colors[palettes[i]]); world.add_child(view); views.append(view)

func show_options(return_to: String):
	if model!=null:
		for fighter in model.players: fighter.charging=false; fighter.buffer=[]
	clear_menu(); screen="options"; paused=true; inputs.clear()
	panel(Vector2(140,20),Vector2(1000,680))
	label("CONFIGURAÇÕES",Vector2(170,36),30,GOLD)
	var scroll=ScrollContainer.new(); scroll.position=Vector2(165,94); scroll.size=Vector2(950,520); menu.add_child(scroll)
	var list=VBoxContainer.new(); list.custom_minimum_size.x=920; list.add_theme_constant_override("separation",10); scroll.add_child(list)
	for definition in [["music","Música",0,1,.05],["sfx","Efeitos sonoros",0,1,.05],["flash","Intensidade do flash",0,1,.05],["round_seconds","Segundos por round",30,300,1],["wins","Vitórias necessárias",1,5,1],["training_health","Vida no treino (multiplicador)",.25,2,.25]]:
		var row=HBoxContainer.new(); list.add_child(row)
		var title=Label.new(); title.text=definition[1]; title.custom_minimum_size.x=430; row.add_child(title)
		var slider=HSlider.new(); slider.custom_minimum_size=Vector2(310,34); slider.min_value=definition[2]; slider.max_value=definition[3]; slider.step=definition[4]; slider.value=prefs.values[definition[0]]; row.add_child(slider)
		var value=Label.new(); value.text=str(slider.value); row.add_child(value)
		slider.value_changed.connect(func(v): prefs.values[definition[0]]=v; value.text=str(v))
	for definition in [["shake","Tremor de câmera"],["fullscreen","Tela cheia"],["training_resources","Recursos infinitos no treino"],["training_restore","Restaurar vida após combo"],["debug","Mostrar hitboxes e hurtboxes"]]:
		var check=CheckButton.new(); check.text=definition[1]; check.button_pressed=prefs.values[definition[0]]; list.add_child(check)
		check.toggled.connect(func(v): prefs.values[definition[0]]=v)
	for definition in [["difficulty","Dificuldade",["Fácil","Normal","Difícil"]],["resolution","Resolução",["1280 × 720","1600 × 900","1920 × 1080"]]]:
		var row=HBoxContainer.new(); list.add_child(row)
		var title=Label.new(); title.text=definition[1]; title.custom_minimum_size.x=430; row.add_child(title)
		var option=OptionButton.new(); option.custom_minimum_size=Vector2(380,38)
		for item in definition[2]: option.add_item(item)
		option.selected=int(prefs.values[definition[0]]); row.add_child(option)
		option.item_selected.connect(func(v): prefs.values[definition[0]]=v)
	var info=Label.new(); info.text="Remapear: clique em uma ação e pressione a tecla, botão ou gatilho. Esc cancela."; list.add_child(info)
	for player in range(2):
		for action in Controls.ACTIONS:
			var row=HBoxContainer.new(); list.add_child(row)
			var name=inputs.action_name(player,action)
			var title=Label.new(); title.text="P%d / %s" % [player+1,action]; title.custom_minimum_size.x=280; row.add_child(title)
			for kind in ["keys","pads"]:
				var bind=Button.new(); bind.custom_minimum_size=Vector2(300,34); bind.text="Teclado: "+OS.get_keycode_string(int(prefs.values.keys.get(name,Controls.KEYS[player][Controls.ACTIONS.find(action)]))) if kind=="keys" else "Controle: "+str(prefs.values.pads.get(name,"padrão")); row.add_child(bind)
				bind.pressed.connect(func(): capture_binding=name; capture_type=kind; binding_button=bind; bind.text="PRESSIONE AGORA…")
	button("SALVAR E VOLTAR",Vector2(170,634),Vector2(940,44),func():
		prefs.save(); inputs.setup(prefs.values); apply_display(); capture_binding=""
		if return_to=="fight":
			model.options=prefs.values.duplicate(true); model.training_resources=prefs.values.training_resources; model.training_restore=prefs.values.training_restore
			clear_menu(); screen="fight"; paused=false
		elif return_to=="title": show_title()
		else: show_select())

func pause_menu():
	if model!=null:
		for fighter in model.players: fighter.charging=false; fighter.buffer=[]; fighter.movement=0; fighter.guard=false
	paused=true; inputs.clear(); clear_menu(); panel(Vector2(360,175),Vector2(560,380))
	label("PAUSA",Vector2(555,201),38,GOLD)
	button("CONTINUAR",Vector2(395,285),Vector2(490,48),func(): paused=false; clear_menu())
	button("CONFIGURAÇÕES / TREINO",Vector2(395,350),Vector2(490,48),func(): show_options("fight"))
	button("VOLTAR À SELEÇÃO",Vector2(395,415),Vector2(490,48),func():
		for view in views: view.queue_free()
		views=[]; model=null; show_select())

func _input(event):
	if capture_binding.is_empty() and event is InputEventJoypadButton and event.pressed and event.button_index==JOY_BUTTON_START and screen=="fight":
		if paused: paused=false; clear_menu()
		else: pause_menu()
		return
	if not capture_binding.is_empty():
		if event is InputEventKey and event.pressed:
			if event.keycode==KEY_ESCAPE: capture_binding=""; return
			if capture_type=="keys" and not event.keycode in [KEY_F1,KEY_F5,KEY_F6,KEY_F7,KEY_F8,KEY_F9,KEY_F10,KEY_F11,KEY_ESCAPE]:
				prefs.values.keys[capture_binding]=event.physical_keycode; capture_binding=""
		elif capture_type=="pads" and event is InputEventJoypadButton and event.pressed:
			prefs.values.pads[capture_binding]={"type":"button","index":event.button_index}; capture_binding=""
		elif capture_type=="pads" and event is InputEventJoypadMotion and absf(event.axis_value)>.65:
			prefs.values.pads[capture_binding]={"type":"axis","index":event.axis,"value":signf(event.axis_value)}; capture_binding=""
		if capture_binding.is_empty() and is_instance_valid(binding_button): binding_button.text="DEFINIDO"; inputs.setup(prefs.values)
		get_viewport().set_input_as_handled()
		return
	if event is InputEventKey and event.pressed and not event.echo:
		if event.keycode==KEY_F11: prefs.values.fullscreen=not prefs.values.fullscreen; apply_display(); return
		if screen=="title" and event.keycode==KEY_ENTER: show_select(); return
		if screen=="select":
			if event.keycode==KEY_ENTER: start_match(); return
			if event.keycode==KEY_ESCAPE: show_title(); return
			if event.keycode==KEY_TAB:
				var modes=["PVE","PVP","TREINO"]; play_mode=modes[(modes.find(play_mode)+1)%3]; show_select(); return
			for i in range(2):
				if event.keycode in [[KEY_A,KEY_D],[KEY_LEFT,KEY_RIGHT]][i]:
					selected[i]=posmod(selected[i]+(-1 if event.keycode in [KEY_A,KEY_LEFT] else 1),roster.size()); show_select(); return
		if screen=="fight":
			if event.keycode==KEY_ESCAPE:
				if paused: paused=false; clear_menu()
				else: pause_menu()
				return
			if event.keycode==KEY_F1: show_options("fight"); return
			if model.phase=="VICTORY" and event.keycode==KEY_ENTER: start_match(); return
			if play_mode=="TREINO":
				match event.keycode:
					KEY_F5: model.reset_training(); inputs.clear(); return
					KEY_F6:
						var modes=["PARADO","DEFESA","APÓS ACERTO","PARRY","CPU"]; model.dummy=modes[(modes.find(model.dummy)+1)%5]; model.after_hit=false
						prefs.values.dummy=model.dummy; prefs.save(); return
					KEY_F7: model.training_resources=not model.training_resources; prefs.values.training_resources=model.training_resources; prefs.save(); return
					KEY_F8: prefs.values.debug=not prefs.values.debug; prefs.save(); return
					KEY_F9:
						model.recording=not model.recording; model.playback=false
						if model.recording: model.tape=[]
						inputs.clear(); return
					KEY_F10: model.recording=false; model.playback=not model.playback; model.tape_index=0; inputs.clear(); return
	if screen=="fight" and not paused and model.phase=="FIGHT": inputs.accept(event)

func _notification(what):
	if what==NOTIFICATION_APPLICATION_FOCUS_OUT and model!=null and screen=="fight": pause_menu()
	if what==NOTIFICATION_EXIT_TREE:
		music.stop(); music.stream=null
		for player in sfx: player.stop(); player.stream=null

func _physics_process(dt):
	if model==null or screen!="fight" or paused: return
	var frames=[{},{}]
	if model.phase=="FIGHT" and model.hitstop<=0:
		frames=[inputs.frame(0,model.players[0]),inputs.frame(1,model.players[1])]
	var previous=model.phase
	model.tick(dt,frames)
	if previous!=model.phase:
		inputs.clear()
		if model.phase=="VICTORY":
			button("REVANCHE",Vector2(450,437),Vector2(380,48),start_match)
			button("SELEÇÃO",Vector2(450,495),Vector2(380,45),func():
				for view in views: view.queue_free()
				views=[]; model=null; show_select())
	for event in model.events:
		play_sound(event.kind)
		if event.kind in ["hit","heavy","parry","release","ko"]:
			impact=1; shake=catalog.effects_data.shake if event.kind in ["heavy","release","ko"] else catalog.effects_data.shake*.4
			for i in range(18): particles.append({"p":event.position,"v":Vector2(randf_range(-230,230),randf_range(-240,50)),"life":.5,"color":event.color})
	model.events.clear()

func play_sound(kind: String):
	if DisplayServer.get_name()=="headless": return
	var path=catalog.audio_data.get(kind,"res://assets/audio/"+kind+".wav")
	if not ResourceLoader.exists(path): return
	for player in sfx:
		if not player.playing:
			player.stream=load(path); player.volume_db=linear_to_db(maxf(.0001,prefs.values.sfx)); player.play(); break

func _process(dt):
	elapsed+=dt; frame_count+=1
	music.volume_db=linear_to_db(maxf(.0001,prefs.values.music))
	impact=maxf(0,impact-dt*5); shake=maxf(0,shake-dt*35)
	if model!=null:
		camera_x=lerpf(camera_x,clampf((model.players[0].x+model.players[1].x)/2-600,0,420),minf(1,dt*5))
	else: camera_x=210
	arena.camera_x=camera_x
	world.position=Vector2(-camera_x,0)+Vector2(randf_range(-shake,shake),randf_range(-shake,shake))*(1 if prefs.values.shake else 0)
	var effect_dt=dt*.2 if model!=null and model.phase=="KO" and model.phase_time>1.8 else dt
	for p in particles: p.life-=effect_dt; p.p+=p.v*effect_dt; p.v.y+=effect_dt*400
	particles=particles.filter(func(p): return p.life>0)
	effect_rect.material.set_shader_parameter("strength",impact)
	effect_rect.material.set_shader_parameter("flash",impact*catalog.effects_data.get("flash",.13)*prefs.values.flash)
	queue_redraw()
	if smoke and frame_count>=120: get_tree().quit()
	if "--capture" in OS.get_cmdline_user_args() and frame_count==100:
		await RenderingServer.frame_post_draw
		DirAccess.make_dir_recursive_absolute("res://qa")
		get_viewport().get_texture().get_image().save_png("res://qa/"+("training" if play_mode=="TREINO" else screen)+".png")
		get_tree().quit()

func text(value: String,pos: Vector2,size: int=20,color: Color=WHITE): draw_string(font,pos,value,HORIZONTAL_ALIGNMENT_LEFT,-1,size,color)

func _draw():
	if model==null or screen!="fight": return
	for q in model.projectiles:
		var c=Color(q.owner.profile.cor[0]/255.0,q.owner.profile.cor[1]/255.0,q.owner.profile.cor[2]/255.0)
		var pos=Vector2(q.x-camera_x,q.y)
		if q.move.tipo=="trap": draw_arc(pos,24,0,TAU,32,c,3,true); draw_line(pos+Vector2(-15,-15),pos+Vector2(15,15),c,3)
		else:
			draw_line(pos-Vector2(q.direction*65,0),pos,c,8,true); draw_circle(pos,12,c); draw_circle(pos,5,WHITE)
	for p in particles: draw_circle(p.p-Vector2(camera_x,0),2+p.life*5,Color(p.color,p.life*2))
	for i in range(2):
		var p=model.players[i]; var x=30+i*775
		draw_style_box(_hud_panel(),Rect2(x,20,445,128))
		text(p.profile.nome.to_upper(),Vector2(x+18,53),28)
		text("%d / %d" % [p.hp,p.profile.vida],Vector2(x+305,50),16,GOLD)
		draw_rect(Rect2(x+18,69,410,18),Color("14283a")); draw_rect(Rect2(x+18,69,410*clampf(p.hp/p.profile.vida,0,1),18),Color("d7e9cb"))
		draw_rect(Rect2(x+18,99,410*p.energy/p.profile.reiatsu,7),ICE)
		draw_rect(Rect2(x+18,115,410*p.stamina/100,5),GOLD)
		if p.form_index>=0: text(p.form().name+"  %.1fs"%p.form_time,Vector2(x+10,174),17,GOLD)
		if p.message_time>0: text(p.message,Vector2(x+12,205),19,ICE)
		if p.combo>1: text("%d HITS / %.1f DANO" % [p.combo,p.combo_damage],Vector2(x+15,265),25,GOLD)
		if prefs.values.debug:
			for box in [[p.hurtbox(),Color(0,.9,1,.8)],[p.pushbox(),Color(0,1,.2,.8)],[p.hitbox(),Color(1,.1,.2,.8)]]:
				draw_rect(Rect2(box[0].position-Vector2(camera_x,0),box[0].size),box[1],false,2)
	text("∞" if is_inf(model.time) else "%02d"%ceil(model.time),Vector2(610,70),48)
	text("TREINO" if play_mode=="TREINO" else "%d : %d"%[model.wins[0],model.wins[1]],Vector2(604,114),17,GOLD)
	draw_rect(Rect2(0,636,1280,84),Color("0a1523"))
	if play_mode=="TREINO":
		var p=model.players[0]
		text("F5 reset  •  F6 "+model.dummy+"  •  F7 recursos "+("∞" if model.training_resources else "normais")+"  •  F8 colisões  •  F9 gravar  •  F10 reproduzir",Vector2(32,660),16,ICE)
		text("Dano: %.1f / Vantagem estimada: %+.1f quadros / %s" % [p.last_damage,p.last_advantage," > ".join(model.input_history)],Vector2(32,685),15)
		if model.recording or model.playback: text(("GRAVANDO BONECO" if model.recording else "REPRODUZINDO")+" / %.1fs"%(model.tape.size()/120.0),Vector2(470,235),24,GOLD)
		if not p.action.is_empty(): text("Startup %.0ff / Ativo %.0ff / Recuperação %.0ff"%[p.action.startup*120,p.action.active*120,p.action.recovery*120],Vector2(32,711),14,GOLD)
	else: text("Esc pausa • F1 configurações • Q/O forma • F/G ataque • R/T especiais",Vector2(290,687),17,ICE)
	if model.phase in ["INTRO","KO","VICTORY"]:
		draw_style_box(_hud_panel(),Rect2(350,275,580,135))
		text(("ROUND %d"%model.round_number) if model.phase=="INTRO" else (model.players[model.winner].profile.nome+" VENCE" if model.phase=="VICTORY" else model.result),Vector2(460,350),40,GOLD)

func _hud_panel() -> StyleBoxFlat:
	var style=StyleBoxFlat.new(); style.bg_color=Color(.025,.05,.09,.95); style.border_color=Color("3d5d6e"); style.set_border_width_all(1); style.set_corner_radius_all(6); return style
