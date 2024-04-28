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


def createTempDir(dir_name=temp_dir_name):
    print("mkdir:", dir_name)
    if os.path.exists(dir_name):
        chmodWait(dir_name)
        shutil.rmtree(dir_name)
    os.mkdir(dir_name)
    chmodWait(dir_name)


def tempToZip(dir_name=temp_dir_name):
    chmodWait(dir_name)
    CreateZipFile(dir_name)
    chmodWait(zip_file_name)
    shutil.rmtree(dir_name)


def extractData(folder: str):
    if os.path.exists(folder):
        json_name_cache = None
        print("reading folder", folder)
        for file in os.listdir(folder):
            # file: file name, without path
            if file.endswith('.json'):
                # get json name
                json_name_cache = file.split('.')[0]
                # extract json file
                shutil.copy2(os.path.join(folder, file), os.path.join(temp_dir_name, file))
        # if the json data file is not complete, break
        if json_name_cache is None:
            return False
        # collect settings.h
        for file in os.listdir(folder):
            if file == 'settings.h':
                shutil.copy2(os.path.join(folder, file), os.path.join(temp_dir_name, json_name_cache + ".settings.h"))
            elif file == 'nohup.out':
                shutil.copy2(os.path.join(folder, file), os.path.join(temp_dir_name, json_name_cache + ".nohup.out"))
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
    createTempDir(temp_dir_name)
    for d in dirs:
        extractData(d)
    tempToZip(temp_dir_name)
