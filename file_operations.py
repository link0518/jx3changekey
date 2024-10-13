import os
import shutil

def get_subdirectories(path, cache=None):
    if cache is not None and path in cache:
        return cache[path]
    try:
        subdirs = [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]
        if cache is not None:
            cache[path] = subdirs
        return subdirs
    except PermissionError:
        return []

def copy_folder(src, dst):
    shutil.copytree(src, dst)

def delete_folder(path):
    shutil.rmtree(path)

def rename_folder(old_path, new_path):
    os.rename(old_path, new_path)
