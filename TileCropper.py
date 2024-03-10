from PIL import Image
import os


def main():
    extensions = ['.png', '.jpg', '.jpeg']
    files = get_files(extensions)
    if len(files) == 0:
        print('No files found with extensions: ' + ', '.join(extensions) + '. Exiting...')
        exit()
    elif len(files) == 1:
        ask_for_crop(files[0])
    else:
        print('Enter the number of the file you want to crop:')
        for i, file in enumerate(files):
            print(f'{i + 1}. {file}')
        answer = int(input())
        ask_for_crop(files[answer - 1])


def ask_for_crop(file):
    print('Cropping ' + file + ' ...')
    tile_width = int(input('Enter tile width (in pixels): '))
    tile_height = int(input('Enter tile height: '))
    separation = int(input('Enter separation: '))
    margin = int(input('Enter margin: '))
    remove_separation_and_margin(file, tile_width, tile_height, separation, margin)


def remove_separation_and_margin(input_file, tile_width, tile_height, separation, margin):
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
    print('Saved as ' + output_file)


def get_files(extensions):
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


if __name__ == '__main__':
    main()

