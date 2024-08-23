import os
import cv2
import json
import concurrent.futures

input_path = "/Volumes/LaCie/itmo_screenology/yt_shorts"
output_path = "/Volumes/LaCie/itmo_screenology/frames"
# log_file = "itmo_screens/data/frames_log_data.json"




def list_videos_in_folder(folder_path):
    files_and_dirs = os.listdir(folder_path)
    
    files = [f for f in files_and_dirs if os.path.isfile(os.path.join(folder_path, f)) and "_id_" in f]
    files_full_path = [os.path.join(input_path, f) for f in files]
    
    return files_full_path

def videos_processed():
    pass



def video_into_frames(video_path: str):
    video_id = video_path.split('/')[-1].split('_id_')[0]
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Could not open video {video_path}")
        # log_data[video_id] = {'status': 'error', 'message': 'Could not open video'}
        # save_log(log_data)
        return

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    duration = int(total_frames / fps) if fps != 0 else 0

    foldername = f"{video_id}__frms_{total_frames}_w{width}_h{height}_dur_{duration}_fps_{int(fps)}"

    # Doublecheking that the video was not processed already


    video_output_folder = os.path.join(output_path, foldername)
    if os.path.exists(video_output_folder):
        num_jpg_files = len([f for f in os.listdir(video_output_folder) if f.endswith('.jpg')])
        if num_jpg_files == total_frames:
            print(f"\n\n{video_id} exists {num_jpg_files} == {total_frames}. SKIPPING.\n\n")
            # update_log(video_id, {'status': 'processed', 'message': 'Folder already exists with correct number of frames'})
            cap.release()
            return
        elif num_jpg_files != total_frames:
            print(f"\n\n{video_id} exists {num_jpg_files} != {total_frames}. GOING ON.\n\n")
    
    os.makedirs(video_output_folder, exist_ok=True)
    
    
    frame_count = 0
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frame_filename = f"{video_id}_id_frame_{frame_count:05d}.jpg"
            frame_filepath = os.path.join(video_output_folder, frame_filename)
            cv2.imwrite(frame_filepath, frame)
            frame_count += 1
        
        cap.release()

    except Exception as e:
        cap.release()
        print(f"Error processing video {video_path}: {e}")


    pass


if __name__ == "__main__":
    files_to_process = list_videos_in_folder(input_path)
    # files_to_process = [f for f in files_to_process if f.split('/')[-1].split('_id_')[0] not in processed_ids]
    files_full_path = [os.path.join(input_path, f) for f in files_to_process]

    # for f_idx, f in enumerate(files_full_path, start=1):
    #     print(f"{f_idx} out of {len(files_to_process)}. {f.split('/')[-1].split('_id_')[0]}")
    #     video_into_frames(f)
    
    max_workers = 8  # Adjust this number as needed

    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(video_into_frames, video) for video in files_to_process]
        for i, future in enumerate(concurrent.futures.as_completed(futures), start=1):
            try:
                future.result()  # Get the result to raise any exceptions
                print(f"Processed {i} out of {len(files_to_process)} videos.")
            except Exception as e:
                print(f"Error processing video: {e}")


    print("hello world")