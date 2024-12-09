@tool
extends EditorPlugin
var tool


func _enter_tree():
	tool = preload("res://addons/TileCropper/TileCropper.tscn").instantiate()
	add_control_to_dock(EditorPlugin.DOCK_SLOT_LEFT_UR, tool)


func _exit_tree():
	if tool:
		remove_control_from_docks(tool)
		tool.free()
