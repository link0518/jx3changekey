import os
import shutil

def get_subdirectories(path):
    return [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]

def copy_folder(src, dst):
    shutil.copytree(src, dst)

def delete_folder(path):
    shutil.rmtree(path)

def rename_folder(old_path, new_path):
    os.rename(old_path, new_path)