import os
import cv2
from multiprocessing import Pool

path = "/Volumes/KERTANOV_VIKTOR/itmo_screenology/frames"
# downscale_path = "/Volumes/KERTANOV_VIKTOR/itmo_screenology/frames_92x52"
downscale_path = "/Volumes/KERTANOV_VIKTOR/itmo_screenology/frames_43x24"

folders = os.listdir(path)

proper_folders = [os.path.join(path, f) for f in folders if "w360_h640" in f]

def resize_with_aspect_ratio(image, width=None, height=None, inter=cv2.INTER_CUBIC):
    (h, w) = image.shape[:2]


    if width is None and height is None:
        return image

    if width is None:
        aspect_ratio = height / float(h)
        new_dimensions = (int(round(w * aspect_ratio)), height)
    else:
        aspect_ratio = width / float(w)
        new_dimensions = (width, int(round(h * aspect_ratio)))

    # Resize the image
    resized_image = cv2.resize(image, new_dimensions, interpolation=inter)
    return resized_image

def resize_images_in_directory(input_dir, output_dir, width=None, height=None, inter=cv2.INTER_CUBIC):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for filename in os.listdir(input_dir):
        input_path = os.path.join(input_dir, filename)
        
        if os.path.isfile(input_path) and filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
            image = cv2.imread(input_path)
            resized_image = resize_with_aspect_ratio(image, width=width, height=height, inter=inter)
            
            output_path = os.path.join(output_dir, filename)
            cv2.imwrite(output_path, resized_image)
            # print(f"Resized image saved to {output_path}")
    print(f"{filename.split('__')[-1]} done")


# for f in proper_folders:
#     output_dir = f.replace("frames", "frames_92x52")
#     if os.path.exists(output_dir):
#         files = [f for f in os.listdir(output_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))]
#         if len(files) == int(output_dir.split('__frms_')[-1].split('_')[0]):
#             continue
#     resize_images_in_directory(f, output_dir, width=new_width)

def process_directory(f, new_width):
    output_dir = f.replace("frames", "frames_43x24")
    if os.path.exists(output_dir):
        files = [f for f in os.listdir(output_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))]
        if len(files) == int(output_dir.split('__frms_')[-1].split('_')[0]):
            print(f"Skipping {output_dir} as it already has the required number of files.")
            return
    resize_images_in_directory(f, output_dir, width=new_width)

def main(proper_folders, new_width):
    with Pool() as pool:
        pool.starmap(process_directory, [(f, new_width) for f in proper_folders])

if __name__ == '__main__':
    new_width = 24
    # max_workers = 4
    main(proper_folders, new_width)

    print("Hello world")