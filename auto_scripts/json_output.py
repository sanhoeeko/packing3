import os
import shutil
import subprocess

from json_packer import CreateZipFile, zip_file_name

temp_dir_name = 'temp'
enable_sudo = False


def chmodWait(dir: str):
    if enable_sudo:
        p = subprocess.Popen(f"sudo chmod 777 {dir}", shell=True)
        p.wait()
        p = subprocess.Popen(f"sudo chmod -R 777 {dir}", shell=True)
        p.wait()


def createTempDir():
    if os.path.exists(temp_dir_name):
        chmodWait(temp_dir_name)
        shutil.rmtree(temp_dir_name)
    os.mkdir(temp_dir_name)
    chmodWait(temp_dir_name)


def tempToZip():
    chmodWait(temp_dir_name)
    CreateZipFile(temp_dir_name)
    chmodWait(zip_file_name)
    shutil.rmtree(temp_dir_name)


def extractData(folder: str):
    if os.path.exists(folder):
        for file in os.listdir(folder):
            # file: file name, without path
            if file.endswith('.json'):
                # get json name
                json_name_cache = file.split('.')[0]
                # extract json file
                shutil.copy(os.path.join(folder, file), os.path.join(temp_dir_name, file))
        # collect settings.h
        for file in os.listdir(folder):
            if file == 'settings.h':
                shutil.copy(os.path.join(folder, file), os.path.join(temp_dir_name, json_name_cache + ".settings.h"))
            elif file == 'nohup.out':
                shutil.copy(os.path.join(folder, file), os.path.join(temp_dir_name, json_name_cache + ".nohup.out"))
        return True
    else:
        return False


if __name__ == '__main__':
    def isDstPath(name: str):
        this_name = name.split('/')[-1]
        if this_name == 'temp' or this_name.isdigit():
            return True
        return False


    # call this script for emergent output
    temp_dir_name = "__temp__"
    current_dir = os.getcwd()
    dirs = list(filter(isDstPath, filter(os.path.isdir, os.listdir(current_dir))))
    createTempDir()
    for d in dirs:
        extractData(d)
    tempToZip()
