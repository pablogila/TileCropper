import cv2
import numpy as np
import os


def get_files():
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




def iso(image, out, tile_points):
    """
    Extracts isometric tiles from a source image and pastes them onto a destination image.

    Args:
        image: Source image.
        out: Path to save the destination image.
        tile_points: A dictionary where keys are paste coordinates (x, y) and values are lists of points defining the polygon of the tile.
    """

    src_img = image

    # Create a blank destination image with a transparent background
    dst_img = np.zeros((src_img.shape[0], src_img.shape[1], 4), dtype=np.uint8)

    for paste_coords, points in tile_points.items():
        paste_x = int(paste_coords[0])
        paste_y = int(paste_coords[1])

        # Convert the points to a NumPy array
        pts = np.array(points, np.int32)
        pts = pts.reshape((-1, 1, 2))

        # Create a mask image
        mask = np.zeros_like(src_img)
        cv2.fillPoly(mask, [pts], (255, 255, 255))

        # Apply the mask to the image
        masked_img = cv2.bitwise_and(src_img, mask)

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

        # Paste the cropped tile onto the destination image
        #dst_img[paste_y:paste_y+h, paste_x:paste_x+w] = cropped_tile_with_alpha

        # Ensure the dimensions match exactly before pasting
        dst_slice = dst_img[paste_y:paste_y+h, paste_x:paste_x+w]
        if dst_slice.shape == cropped_tile_with_alpha.shape:
            dst_img[paste_y:paste_y+h, paste_x:paste_x+w] = cropped_tile_with_alpha
        else:
            h_dst, w_dst, _ = dst_slice.shape
            cropped_tile_with_alpha = cropped_tile_with_alpha[:h_dst, :w_dst]
            dst_img[paste_y:paste_y+h_dst, paste_x:paste_x+w_dst] = cropped_tile_with_alpha

    # Display or save the result
    #cv2.imshow("Result", dst_img)
    #cv2.waitKey(0)
    #cv2.destroyAllWindows()
    #cv2.waitKey(1)  # Ensure all windows are closed
    cv2.imwrite(out, dst_img)

# Example usage:
images = get_files()
print(images)
image = images[0]
out = "result.png"

image = cv2.imread(image)
# Obtain the width and height of the image
h, w = image.shape[:2]

angle = np.degrees(np.arctan(h / w))
side = (h/2) / np.sin(angle)
print(w, 'x', h, 'px size')
print(side, 'px side')
print(angle, 'º angle')


# Define the polygon points for the tile
transformations = {
    # Final coordinates: initial corner coordinates
    (0,     0)     : ((w/2,   0),     (w*3/8, h/8),   (w/2,   h/4),   (w*5/8, h/8)),
    (0,     h/4)   : ((w*3/8, h/8),   (w/4,   h/4),   (w*3/8, h*3/8), (w/2,   h/4)),
    (0,     h/2)   : ((w/4,   h/4),   (w/8,   h*3/8), (w/4,   h/2),   (w*3/8, h*3/8)),
    (0,     h*3/4) : ((w/8,   h*3/8), (0,     h/2),   (w/8,   h*5/8), (w/4,   h/2)),
    (w/4,   0)     : ((w*5/8, h/8),   (w/2,   h/4),   (w*5/8, h*3/8), (w*3/4, h/4)),
    (w/4,   h/4)   : ((w/2,   h/4),   (w*3/8, h*3/8), (w/2,   h/2),   (w*5/8, h*3/8)),
    (w/4,   h/2)   : ((w*3/8, h*3/8), (w/4,   h/2),   (w*3/8, h*5/8), (w/2,   h/2)),
    (w/4,   h*3/4) : ((w/4,   h/2),   (w/8,   h*5/8), (w/4,   h*3/4), (w*3/8, h*5/8)),
    (w/2,   0)     : ((w*3/4, h/4),   (w*5/8, h*3/8), (w*3/4, h/2),   (w*7/8, h*3/8)),
    (w/2,   h/4)   : ((w*5/8, h*3/8), (w/2,   h/2),   (w*5/8, h*5/8), (w*3/4, h/2)),
    (w/2,   h/2)   : ((w/2,   h/2),   (w*3/8, h*5/8), (w/2,   h*3/4), (w*5/8, h*5/8)),
    (w/2,   h*3/4) : ((w*3/8, h*5/8), (w/4,   h*3/4), (w*3/8, h*7/8), (w/2,   h*3/4)),
    (w*3/4, 0)     : ((w*7/8, h*3/8), (w*3/4, h/2),   (w*7/8, h*5/8), (w,     h/2)),
    (w*3/4, h/4)   : ((w*3/4, h/2),   (w*5/8, h*5/8), (w*3/4, h*3/4), (w*7/8, h*5/8)),
    (w*3/4, h/2)   : ((w*5/8, h*5/8), (w/2,   h*3/4), (w*5/8, h*7/8), (w*3/4, h*3/4)),
    (w*3/4, h*3/4) : ((w/2,   h*3/4), (w*3/8, h*7/8), (w/2,   h),     (w*5/8, h*7/8))
}

iso(image, out, transformations)
