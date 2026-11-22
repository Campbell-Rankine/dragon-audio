import os


def get_song_name(path: str):
    name = path.split("/")[-1]
    name = name.split(".")[0]
    return name


def mkdir_if_not_exist(path: str, subdirs=None):
    path = path.rstrip("/")
    os.makedirs(path, exist_ok=True)
    if subdirs is not None:
        assert isinstance(subdirs, list)
        for subdir in subdirs:
            os.makedirs(f"{path}/{subdir}", exist_ok=True)
