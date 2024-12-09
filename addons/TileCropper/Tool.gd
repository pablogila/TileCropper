@tool
extends Control

var input_tileset_node: TilePicker
var input_tileset: Image
var input_mask_node: TilePicker
var input_mask: Image
var tiles_per_side_node: SpinBox
var tiles_per_side: int
var iso_button: Button
var info: Label
var iso_transformations: Dictionary
var slices: Array[Image]
var tile_size: Vector2i
var new_image: Image
var output_path: String


func _ready():
	input_tileset_node = $VBoxContainer/HBoxTileset/InputTileset
	input_mask_node = $VBoxContainer/HBoxMask/InputMask
	tiles_per_side_node = $VBoxContainer/HBoxTiles/TilesPerSide
	iso_button = $VBoxContainer/IsoCropButton
	info = $VBoxContainer/Info


func _on_iso_crop_button_pressed():
	# Check if everything is loaded, then run!
	#input_tileset = input_tileset_node.edited_resource.get_image()
	var input_tileset_resource = input_tileset_node.get_edited_resource()
	var input_mask_resource = input_mask_node.get_edited_resource()
	tiles_per_side = tiles_per_side_node.value
	if input_tileset_resource == null:
		_warning_empty_field('Input tileset')
		return
	if input_mask_resource == null:
		_warning_empty_field('Input tile mask')
		return
	input_tileset = input_tileset_resource.get_image()
	input_mask = input_mask_resource.get_image()
	_crop_iso_tileset()


func _warning_empty_field(section):
	info.text = "Wait! The field '" + section + "' is empty!"


func _crop_iso_tileset():
	info.text = 'Cropping the tileset... wait a second...'
	_calculate_iso_transformations(tiles_per_side)
	_build_iso_slices()
	_build_iso_image()


func _calculate_iso_transformations(side) -> Dictionary:
	var i_new: int
	var j_new: int
	for i in range(0, side-1):
		i_new = i - 1
		j_new = i + side
		for j in range(0, side-1):
			i_new += 1
			j_new -= 1
			iso_transformations[Vector2i(i, j)] = Vector2i(j_new,i_new)
	return iso_transformations


func _build_iso_slices() -> Array[Image]:
	slices.clear()
	# Convert the resources to Image resources
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
	print('Built iso slices...')
	return slices


func _build_iso_image() -> void:
	# Check we have image slice
	if slices.size() == 0:
		return
	print('building iso image...')
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
	output_path = "res://addons/TileCropper/output.png"
	# Save to a file. You could add a filename export if you wanted to
	new_image.save_png(output_path)
	info.text = 'Done!'
