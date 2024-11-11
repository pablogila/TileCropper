try:
    import os
    from PIL import Image
    import cv2
    import numpy as np
except ImportError:
    print('Error importing required libraries. Run "pip install -r requirements.txt"')
    exit()


version = 'v1.1.0'
'''Version of the tool. Uses semantic versioning, as v<MAJOR>.<MINOR>.<PATCH>.'''


def main():
    '''Main function.'''
    files = get_files()
    print('')
    print('Welcome to TileCropper!')
    print('This tool will help you clean and manipulate your tilesets.')
    print('PNG, JPG, and JPEG image files are supported.')
    print('Run this script from the same folder as your image files.')
    print('More info at https://github.com/pablogila/TileCropper')
    print('')
    if len(files) == 0:
        print('No image files found. Remember that SVG files are not supported. Exiting...')
        exit()
    elif len(files) == 1:
        file_to_crop = files[0]
    else:
        print('Enter the number of the file to process:')
        for i, file in enumerate(files):
            print(f'{i + 1}. {file}')
        answer = int(input('> '))
        file_to_crop = files[answer - 1]
        print('')
    ask_for_operation(file_to_crop)


def get_files():
    '''Returns a list of image files in the current working directory.'''
    extensions = ['.png', '.jpg', '.jpeg']
    path = os.getcwd()
    files = os.listdir(path)
    target_files = []
    if not isinstance(extensions, list):
        extensions = [extensions]
    for extension in extensions:
        for file in files:
            if file.endswith(extension):
                target_files.append(file)
        if target_files:
            return target_files
    return None


def ask_for_operation(file_to_crop):
    '''Asks the user which operation to perform.'''
    print('File to be processed: ' + file_to_crop)
    print('Select the operation to perform:')
    print('1. Remove tile separation and margins')
    print('2. Create isometric tilemap')
    print('   (See https://github.com/pablogila/TileMapDual_godot_node)')
    answer2 = int(input('> '))
    print('')
    if answer2 == 1:
        ask_for_crop(file_to_crop)
    elif answer2 == 2:
        ask_for_iso(file_to_crop)
    else:
        print('Please enter a valid operation.')
        ask_for_operation(file_to_crop)


def ask_for_crop(file):
    '''Asks the user for the crop parameters.'''
    print('Cropping ' + file + ' ...')
    image = Image.open(file)
    tile_width  = int(input('Enter tile width (in px): '))
    tile_height = int(input('Enter tile height:        '))
    separation  = int(input('Enter separation:         '))
    margin      = int(input('Enter margin:             '))
    print('')
    remove_separation_and_margin(file, tile_width, tile_height, separation, margin)


def ask_for_iso(file):
    '''Asks the user for the separation between tiles.'''
    print('Creating isometric tilemap from ' + file + ' ...')
    separation = int(input('Enter the desired separation between tiles (in px): '))
    print('')
    create_iso_tilemap(file, separation)


def remove_separation_and_margin(input_file, tile_width, tile_height, separation, margin):
    '''Crops the input image to remove separation and margins.'''
    original = Image.open(input_file)
    output_file = 'output_' + input_file

    num_tiles_x = (original.width - 2 * margin + separation) // (tile_width + separation)
    num_tiles_y = (original.height - 2 * margin + separation) // (tile_height + separation)

    new = Image.new('RGBA', (num_tiles_x * tile_width, num_tiles_y * tile_height))

    for i in range(num_tiles_x):
        for j in range(num_tiles_y):
            left = margin + i * (tile_width + separation)
            upper = margin + j * (tile_height + separation)
            right = left + tile_width
            lower = upper + tile_height
            tile = original.crop((left, upper, right, lower))

            new.paste(tile, (i * tile_width, j * tile_height))

    new.save(output_file)
    print('Cropped and saved as ' + output_file)
    print('')


def create_iso_tilemap(image_file, separation:int=10):
    '''
    Take an input isometric tileset, and displace the tiles
    to be used as inputs for TileMapDual Godot Node.
    An optional separation in pixels can be added between the tiles.
    See https://github.com/pablogila/TileMapDual_godot_node
    '''
    out_file = 'output_' + image_file
    image = cv2.imread(image_file)
    # Create a blank destination image with a transparent background
    image_out = np.zeros((image.shape[0]+5*separation, image.shape[1]+5*separation, 4), dtype=np.uint8)
    # Width and height of the image
    h, w = image.shape[:2]
    # Separation nickname
    s = separation
    # Define the polygon points for the tile
    transformations = {
    # Final coordinates: initial corner coordinates
        (0+s,       0+s)       : ((w/2,   0),     (w*3/8, h/8),   (w/2,   h/4),   (w*5/8, h/8)),
        (0+s,       h/4+2*s)   : ((w*3/8, h/8),   (w/4,   h/4),   (w*3/8, h*3/8), (w/2,   h/4)),
        (0+s,       h/2+3*s)   : ((w/4,   h/4),   (w/8,   h*3/8), (w/4,   h/2),   (w*3/8, h*3/8)),
        (0+s,       h*3/4+4*s) : ((w/8,   h*3/8), (0,     h/2),   (w/8,   h*5/8), (w/4,   h/2)),
        (w/4+2*s,   0+s)       : ((w*5/8, h/8),   (w/2,   h/4),   (w*5/8, h*3/8), (w*3/4, h/4)),
        (w/4+2*s,   h/4+2*s)   : ((w/2,   h/4),   (w*3/8, h*3/8), (w/2,   h/2),   (w*5/8, h*3/8)),
        (w/4+2*s,   h/2+3*s)   : ((w*3/8, h*3/8), (w/4,   h/2),   (w*3/8, h*5/8), (w/2,   h/2)),
        (w/4+2*s,   h*3/4+4*s) : ((w/4,   h/2),   (w/8,   h*5/8), (w/4,   h*3/4), (w*3/8, h*5/8)),
        (w/2+3*s,   0+s)       : ((w*3/4, h/4),   (w*5/8, h*3/8), (w*3/4, h/2),   (w*7/8, h*3/8)),
        (w/2+3*s,   h/4+2*s)   : ((w*5/8, h*3/8), (w/2,   h/2),   (w*5/8, h*5/8), (w*3/4, h/2)),
        (w/2+3*s,   h/2+3*s)   : ((w/2,   h/2),   (w*3/8, h*5/8), (w/2,   h*3/4), (w*5/8, h*5/8)),
        (w/2+3*s,   h*3/4+4*s) : ((w*3/8, h*5/8), (w/4,   h*3/4), (w*3/8, h*7/8), (w/2,   h*3/4)),
        (w*3/4+4*s, 0+s)       : ((w*7/8, h*3/8), (w*3/4, h/2),   (w*7/8, h*5/8), (w,     h/2)),
        (w*3/4+4*s, h/4+2*s)   : ((w*3/4, h/2),   (w*5/8, h*5/8), (w*3/4, h*3/4), (w*7/8, h*5/8)),
        (w*3/4+4*s, h/2+3*s)   : ((w*5/8, h*5/8), (w/2,   h*3/4), (w*5/8, h*7/8), (w*3/4, h*3/4)),
        (w*3/4+4*s, h*3/4+4*s) : ((w/2,   h*3/4), (w*3/8, h*7/8), (w/2,   h),     (w*5/8, h*7/8))
    }
    for paste_coords, points in transformations.items():
        paste_x = int(paste_coords[0])
        paste_y = int(paste_coords[1])
        # Convert the points to a NumPy array
        pts = np.array(points, np.int32)
        pts = pts.reshape((-1, 1, 2))
        # Create a mask image
        mask = np.zeros_like(image)
        cv2.fillPoly(mask, [pts], (255, 255, 255))
        # Apply the mask to the image
        masked_img = cv2.bitwise_and(image, mask)
        # Find the bounding rectangle of the masked image
        x, y, w, h = cv2.boundingRect(pts)
        # Crop the masked image to the bounding rectangle
        cropped_tile = masked_img[y:y+h, x:x+w]
        # Create an alpha channel for the cropped tile
        alpha_channel = np.zeros((h, w), dtype=np.uint8)
        cv2.fillPoly(alpha_channel, [pts - [x, y]], 255)
        
        # Ensure the dimensions match exactly before combining
        if cropped_tile.shape[:2] != alpha_channel.shape:
            h_cropped, w_cropped = cropped_tile.shape[:2]
            alpha_channel = alpha_channel[:h_cropped, :w_cropped]
        # Combine the cropped tile with the alpha channel
        cropped_tile_with_alpha = np.dstack((cropped_tile, alpha_channel))
        
        # Ensure the dimensions match exactly before pasting
        dst_slice = image_out[paste_y:paste_y+h, paste_x:paste_x+w]
        h_dst, w_dst, _ = dst_slice.shape
        h_cropped, w_cropped, _ = cropped_tile_with_alpha.shape
        
        # Adjust the dimensions of cropped_tile_with_alpha if necessary
        if h_dst != h_cropped or w_dst != w_cropped:
            cropped_tile_with_alpha = cropped_tile_with_alpha[:min(h_dst, h_cropped), :min(w_dst, w_cropped), :]
        
        # Adjust the dimensions of dst_slice if necessary
        dst_slice = image_out[paste_y:paste_y+cropped_tile_with_alpha.shape[0], paste_x:paste_x+cropped_tile_with_alpha.shape[1]]
        
        image_out[paste_y:paste_y+cropped_tile_with_alpha.shape[0], paste_x:paste_x+cropped_tile_with_alpha.shape[1]] = cropped_tile_with_alpha

    # Save the result
    cv2.imwrite(out_file, image_out)
    print('Saved as ' + out_file)
    print('')


if __name__ == '__main__':
    main()

