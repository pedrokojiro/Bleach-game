extends SceneTree
var game
func _init(): call_deferred("run")
func capture(name):
	await create_timer(.3).timeout
	await RenderingServer.frame_post_draw
	root.get_texture().get_image().save_png("res://qa/"+name+".png")
func run():
	DirAccess.make_dir_recursive_absolute("res://qa")
	game=load("res://scenes/flow/main.tscn").instantiate(); root.add_child(game)
	await capture("opening")
	game.show_select(); await capture("selection")
	game.show_options("select"); await capture("settings")
	game.play_mode="TREINO"
	for i in range(game.roster.size()):
		game.selected=[i,(i+1)%game.roster.size()]; game.arena_index=i%3
		game.start_match(); game.paused=true
		await capture(game.roster[i]+"_base")
		var fighter=game.model.players[0]
		for index in range(fighter.data.forms.size()):
			fighter.change("IDLE"); fighter.energy=fighter.profile.reiatsu; fighter.execute("release")
			await capture(game.roster[i]+"_form_"+str(index))
	game.pause_menu(); await capture("pause")
	game.play_mode="PVP"; game.start_match()
	game.model.winner=0; game.model.wins=[2,0]; game.model.phase="KO"; game.model.phase_time=.01
	await capture("victory")
	game.start_match(); await capture("rematch")
	game.queue_free(); await process_frame; await process_frame
	print("VISUAL REVIEW: captures written to godot/qa")
	quit()
