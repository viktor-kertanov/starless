
import json
import csv

input_file = "itmo_screens/data/yt_watch_history.json"
csv_file = "itmo_screens/data/shorts_for_dl.csv"
input_with_keys = "itmo_screens/data/yt_watch_history_with_keys.json"


with open(input_file, 'r', encoding='utf-8') as file:
    data = json.load(file)

data_with_keys = {el["video_id"]:el for el in data}

with open(input_with_keys, 'w', encoding='utf-8') as file:
    json.dump(data_with_keys, file, ensure_ascii=False, indent=4)


shorts_for_dl = []
for d in data:
    if int(d["len_sec"]) < 61 and d["video_id"] not in shorts_for_dl:
        shorts_for_dl.append(d["video_id"])

with open(csv_file, 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    
    # Write rows
    for url in shorts_for_dl:
        writer.writerow([url])

print("Hello world!")