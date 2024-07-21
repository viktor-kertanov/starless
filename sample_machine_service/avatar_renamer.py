import os
from os.path import isfile, join

def get_files_from_folder(folder_path):
    files = [f for f in os.listdir(folder_path) if isfile(join(folder_path, f)) if f != '.DS_Store']
    
    return files


def file_renamer(path):
    if path[-1] != '/':
        path += '/'
    items = os.listdir(path)
    items = [f"{path}{el}" for el in items]
    episode_counter = {
        3: "",
        2: "",
        3: "",
    }
    for item in items:
        if os.path.isfile(item):
            filename = item.split('/')[-1]
            if filename[0] == '.':
                continue
            else:
                episode_data = filename.split('_')[0]
                season = int(episode_data.split("e")[0].replace('s0', ''))
                episode = episode_data.split("e")[-1]
                episode = int(episode) if episode[0]!="0" else int(episode[1:])
                episode_index = (season-1)*20 + episode
                new_filename = f"{episode_index}_{filename}"
                print(new_filename)
                os.rename(item, f"{path}{new_filename}")


        if os.path.isdir(item):
            file_renamer(item)

if __name__ == '__main__':
    path = "/Volumes/CARTOONS/Avatar_The.Last.Air.Bender.2005-2008.bdrip_[teko]/"
    file_renamer(path)

    print('Hello world!')