import os
import cv2
from concurrent.futures import ProcessPoolExecutor, as_completed
from tqdm import tqdm  # Optional: for a nice progress bar

path = "/Volumes/transcend_ssd/itmo_screenology/frames"

folders = os.listdir(path)
proper_folders = [os.path.join(path, f) for f in folders if "w360_h640" in f]

def resize_with_aspect_ratio(image, width=None, height=None, inter=cv2.INTER_LINEAR):
    (h, w) = image.shape[:2]

    if width is None and height is None:
        return image

    if width is None:
        aspect_ratio = height / float(h)
        new_dimensions = (int(round(w * aspect_ratio)), height)
    else:
        aspect_ratio = width / float(w)
        new_dimensions = (width, int(round(h * aspect_ratio)))

    resized_image = cv2.resize(image, new_dimensions, interpolation=inter)
    return resized_image

def resize_images_in_directory(input_dir, output_dir, width=None, height=None, inter=cv2.INTER_LINEAR):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for filename in os.listdir(input_dir):
        input_path = os.path.join(input_dir, filename)
        
        if os.path.isfile(input_path) and filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
            image = cv2.imread(input_path)
            resized_image = resize_with_aspect_ratio(image, width=width, height=height, inter=inter)
            
            output_path = os.path.join(output_dir, filename)
            cv2.imwrite(output_path, resized_image)
    print(f"{input_dir.split('__')[-1]} done")

def process_directory(f, new_width):
    output_dir = f.replace("frames", "frames_184x104")
    if os.path.exists(output_dir):
        files = [f for f in os.listdir(output_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))]
        if len(files) == int(output_dir.split('__frms_')[-1].split('_')[0]):
            print(f"Skipping {output_dir} as it already has the required number of files.")
            return
    resize_images_in_directory(f, output_dir, width=new_width)

def main(proper_folders, new_width, max_workers):
    total_tasks = len(proper_folders)
    completed_tasks = 0
    
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(process_directory, f, new_width): f for f in proper_folders}
        
        for future in as_completed(futures):
            f = futures[future]
            try:
                future.result()
                completed_tasks += 1
                print(f"Completed {completed_tasks}/{total_tasks} tasks.")
            except Exception as e:
                print(f"Error processing {f}: {e}")

if __name__ == '__main__':
    new_width = 104
    max_workers = 10  # Set the number of workers
    main(proper_folders, new_width, max_workers)

    print("Hello world")
