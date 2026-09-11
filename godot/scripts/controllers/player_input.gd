extends RefCounted
const ACTIONS=["left","right","jump","guard","light","heavy","special","special2","grab","dash","parry","release","ultimate","exclusive","run"]
const KEYS=[[KEY_A,KEY_D,KEY_W,KEY_S,KEY_F,KEY_G,KEY_R,KEY_T,KEY_V,KEY_SHIFT,KEY_C,KEY_Q,KEY_E,KEY_X,KEY_CTRL],[KEY_LEFT,KEY_RIGHT,KEY_UP,KEY_DOWN,KEY_J,KEY_K,KEY_U,KEY_I,KEY_N,KEY_PERIOD,KEY_M,KEY_O,KEY_L,KEY_COMMA,KEY_SLASH]]
const PAD={"jump":0,"heavy":1,"light":2,"special":3,"guard":9,"dash":10,"parry":7,"release":8,"exclusive":4,"grab":12,"run":11}
var pending=[[],[]]

func action_name(player: int,key: String) -> String: return "p%d_%s" % [player,key]

func setup(config: Dictionary):
	for player in range(2):
		for i in range(ACTIONS.size()):
			var key=ACTIONS[i]; var name=action_name(player,key)
			if InputMap.has_action(name): InputMap.erase_action(name)
			InputMap.add_action(name,.25)
			var event=InputEventKey.new(); event.physical_keycode=int(config.keys.get(name,KEYS[player][i])); InputMap.action_add_event(name,event)
			var bind=config.pads.get(name,{})
			if not bind.is_empty():
				if bind.get("type","")=="button":
					var button=InputEventJoypadButton.new(); button.device=player; button.button_index=int(bind.index); InputMap.action_add_event(name,button)
				else: _axis(name,player,int(bind.index),float(bind.value))
			elif PAD.has(key):
				var button=InputEventJoypadButton.new(); button.device=player; button.button_index=PAD[key]; InputMap.action_add_event(name,button)
			elif key in ["left","right"]: _axis(name,player,0,-1 if key=="left" else 1)
			elif key in ["special2","ultimate"]: _axis(name,player,4 if key=="special2" else 5,1)

func _axis(name: String,device: int,index: int,value: float):
	var event=InputEventJoypadMotion.new(); event.device=device; event.axis=index; event.axis_value=value
	InputMap.action_add_event(name,event)

func accept(event: InputEvent):
	if event is InputEventKey and event.echo: return
	for player in range(2):
		for action in ACTIONS:
			if action in ["left","right","guard","run"]: continue
			var name=action_name(player,action)
			if event.is_action_pressed(name): pending[player].append(action)
			elif action=="special" and event.is_action_released(name): pending[player].append("special_up")

func frame(player: int,fighter) -> Dictionary:
	var actions=[]
	for action in pending[player]:
		if action=="special_up":
			if fighter.kit.charge: actions.append("charge_end")
		elif action=="special" and fighter.kit.charge: actions.append("charge_start")
		else: actions.append(action)
	pending[player]=[]
	return {"movement":Input.get_axis(action_name(player,"left"),action_name(player,"right")),"guard":Input.is_action_pressed(action_name(player,"guard")),"run":Input.is_action_pressed(action_name(player,"run")),"actions":actions}

func clear():
	pending=[[],[]]
	for player in range(2):
		for action in ACTIONS: Input.action_release(action_name(player,action))
