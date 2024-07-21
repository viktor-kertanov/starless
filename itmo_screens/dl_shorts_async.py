import csv
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from sample_machine_service.yt_dl import dl_yt_video
from pytube.innertube import _default_clients

# Adjusting client versions for pytube
_default_clients["ANDROID"]["context"]["client"]["clientVersion"] = "19.08.35"
_default_clients["IOS"]["context"]["client"]["clientVersion"] = "19.08.35"
_default_clients["ANDROID_EMBED"]["context"]["client"]["clientVersion"] = "19.08.35"
_default_clients["IOS_EMBED"]["context"]["client"]["clientVersion"] = "19.08.35"
_default_clients["IOS_MUSIC"]["context"]["client"]["clientVersion"] = "6.41"
_default_clients["ANDROID_MUSIC"] = _default_clients["ANDROID_CREATOR"]

# Paths
csv_file = "itmo_screens/data/shorts_for_dl.csv"
output_path = "/Volumes/KERTANOV_VIKTOR/itmo_screenology/yt_shorts"

# Read URLs from CSV
urls = []
with open(csv_file, 'r', newline='', encoding='utf-8') as file:
    reader = csv.reader(file)
    for row in reader:
        urls.append(row[0])

# Get list of already downloaded video IDs
downloaded = [f.split('_id_')[0] for f in os.listdir(output_path)]

# Find URLs to download that are not already downloaded
to_download = list(set(urls).difference(set(downloaded)))
print(f"We have downloaded {len(downloaded)}. We want to download: {len(to_download)}")

# Function to download a video
def download_video(video_id, output_path):
    url = "https://www.youtube.com/watch?v=" + video_id
    print(f"Downloading: {url}")
    try:
        dl_yt_video(url, output_path)
        return f"Successfully downloaded: {url}"
    except Exception as e:
        return f"Error downloading {url}: {e}"

# Download videos in parallel using ThreadPoolExecutor
max_workers = 4  # Adjust this number based on your system's capabilities
with ThreadPoolExecutor(max_workers=max_workers) as executor:
    futures = [executor.submit(download_video, video_id, output_path) for video_id in to_download]
    for idx, future in enumerate(as_completed(futures)):
        print(f"{idx + 1} out of {len(to_download)}: {future.result()}")

print("All downloads complete!")
