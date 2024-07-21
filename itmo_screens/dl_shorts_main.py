import csv
import os
from sample_machine_service.yt_dl import dl_yt_video
from pytube.innertube import _default_clients

_default_clients["ANDROID"]["context"]["client"]["clientVersion"] = "19.08.35"
_default_clients["IOS"]["context"]["client"]["clientVersion"] = "19.08.35"
_default_clients["ANDROID_EMBED"]["context"]["client"]["clientVersion"] = "19.08.35"
_default_clients["IOS_EMBED"]["context"]["client"]["clientVersion"] = "19.08.35"
_default_clients["IOS_MUSIC"]["context"]["client"]["clientVersion"] = "6.41"
_default_clients["ANDROID_MUSIC"] = _default_clients["ANDROID_CREATOR"]

csv_file = "itmo_screens/data/shorts_for_dl.csv"
output_path = "/Volumes/KERTANOV_VIKTOR/itmo_screenology/yt_shorts"

urls = []
with open(csv_file, 'r', newline='', encoding='utf-8') as file:
    reader = csv.reader(file)
    for row in reader:
        urls.append(row[0])


# Directory path
downloaded = [f.split('_id_')[0] for f in os.listdir(output_path)]

to_download = list(set(urls).difference(set(downloaded)))
print(f"We have dl'ed {len(downloaded)}. We want to download: {len(to_download)}")

for idx, video_id in enumerate(to_download):
    url = "https://www.youtube.com/watch?v=" + video_id
    print(f"{idx} out of {len(to_download)}. URL: {url}")
    dl_yt_video(url, output_path)



print("Hello world!")