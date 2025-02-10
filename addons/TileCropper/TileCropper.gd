@tool
extends ScrollContainer

var input_tileset_node: EditorResourcePicker
var input_tileset_resource: Texture2D
var input_tileset: Image
var input_mask_node: EditorResourcePicker
var input_mask_resource: Texture2D
var input_mask: Image
var tiles_per_side_node: SpinBox
var tiles_per_side: int
var iso_button: Button
var info: Label
var waiting_time: int = 10
var running: bool

var iso_transformations: Dictionary
var tile_size: Vector2i
var slices: Array[Image]
var new_image: Image
var output_path: String


func _ready():
	input_tileset_node = $VBoxContainer/HBoxTileset/InputTileset
	input_mask_node = $VBoxContainer/HBoxMask/InputMask
	tiles_per_side_node = $VBoxContainer/HBoxTiles/TilesPerSide
	iso_button = $VBoxContainer/IsoCropButton
	info = $VBoxContainer/Info
	input_tileset_node.base_type = "Texture2D"
	input_mask_node.base_type = "Texture2D"
	running = false
	_reset_info()


func _reset_info():
	info.text = 'Fill the input fields and start cropping!'


func _message(message):
	info.text = message
	print(message)
	await get_tree().create_timer(waiting_time).timeout
	if running == false:
		_reset_info()


func _set_output_path() -> void:
	var filename = input_tileset_resource.resource_path.get_basename()
	var extension = input_tileset_resource.resource_path.get_extension()
	output_path = filename + '_out.' + extension
	return


func _on_iso_crop_button_pressed():
	# Check if everything is loaded, then run!
	input_tileset_resource = input_tileset_node.get_edited_resource()
	input_mask_resource = input_mask_node.get_edited_resource()
	tiles_per_side = tiles_per_side_node.value
	if input_tileset_resource == null:
		_message("Wait! The field 'Input tileset' is empty!")
		return
	if input_mask_resource == null:
		_message("Wait! The field 'Input tile mask' is empty!")
		return
	if tiles_per_side < 2:
		_message("Wait! 'Tiles per side' must be >= 2")
		return
	_crop_iso_tileset()


func _crop_iso_tileset():
	running = true
	iso_button.disabled = true
	info.text = 'Cropping... wait a second...'
	_set_output_path()
	_calculate_iso_transformations()
	_build_iso_slices()
	_build_iso_image()
	EditorInterface.get_resource_filesystem().scan()
	info.text = "Done! output saved at '" + output_path + "'"
	await get_tree().create_timer(waiting_time).timeout
	iso_button.disabled = false
	running = false
	_reset_info()


func _calculate_iso_transformations() -> Dictionary:
	var i_new: int
	var j_new: int
	for i in range(0, tiles_per_side):
		i_new = i - 1
		j_new = i + tiles_per_side
		for j in range(0, tiles_per_side):
			i_new += 1
			j_new -= 1
			iso_transformations[Vector2i(i, j)] = Vector2i(j_new,i_new)
	return iso_transformations


func _build_iso_slices() -> Array[Image]:
	slices.clear()
	print('Building iso slices...')
	# Convert the resources to Image resources
	input_tileset = input_tileset_resource.get_image()
	input_mask = input_mask_resource.get_image()
	var tile_height:int = input_mask.get_height()
	var tile_width: int = input_mask.get_width()
	tile_size = Vector2i(tile_width, tile_height)
	for slice_position in iso_transformations.values():
		# Create an empty image the size of a tile
		var new_slice: Image = Image.create_empty(tile_size.x, tile_size.y, false, input_tileset.get_format())
		# Blit (copy) the rect onto the new image
		var blit_position: Vector2i = slice_position * (tile_size / 2)
		var slice_rect: Rect2i = Rect2i(blit_position, Vector2i(tile_size.x, tile_size.y))
		new_slice.blit_rect(input_tileset, slice_rect, Vector2i(0,0))
		# Mask the blitted slice, needs to happen after because the size needs to be the same.
		var masked_slice: Image = Image.create_empty(tile_size.x, tile_size.y, false, input_tileset.get_format())
		var mask_rect: Rect2i = Rect2i(Vector2i(0,0), tile_size)
		masked_slice.blit_rect_mask(new_slice, input_mask, mask_rect, Vector2i(0,0))
		# Add it to an array for later use
		slices.append(masked_slice)
	print('Iso slices built!')
	return slices


func _build_iso_image() -> void:
	# Check we have image slice
	if slices.size() == 0:
		print('Error: slices.size is zero!')
		return
	print('Building iso image...')
	# Create new image that's blank. The RGBA8 format should preserve alpha but I havent tested yet
	new_image = Image.create_empty(tiles_per_side * tile_size.x, tiles_per_side * tile_size.y, false, Image.FORMAT_RGBA8)
	# Loop through the slices to build the image in grid order. Again just using array positions for speed
	var i: int = 0
	for slice in slices:
		# Dst is the position on the new image, rect is the tile size
		var dst: Vector2i = iso_transformations.keys()[i] * tile_size
		print(dst)
		#var dst := grid_position[i] * tile_size
		var slice_rect = Rect2i(Vector2i(0,0), tile_size)
		new_image.blit_rect(slice, slice_rect, dst)
		i += 1
	new_image.save_png(output_path)
	print("New tileset saved at " + output_path)
