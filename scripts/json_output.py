import os
import shutil
import subprocess

from json_packer import CreateZipFile, zip_file_name


def chmodWait(dir: str):
    p = subprocess.Popen(f"sudo chmod 777 {dir}", shell=True)
    p.wait()
    p = subprocess.Popen(f"sudo chmod -R 777 {dir}", shell=True)
    p.wait()


# copy all json files in subdirectories to a temporary directory
if os.path.exists("temp"):
    chmodWait("temp")
    shutil.rmtree("temp")
os.mkdir("temp")
chmodWait("temp")

for root, folders, _ in os.walk(os.getcwd()):
    json_name_cache = ''
    for folder in folders:
        # if the name of the folder is a single character
        if os.path.exists(folder) and len(folder.split('/')[-1]) == 1:
            for file in os.listdir(folder):
                # file: file name, without path
                if file.endswith('.json'):
                    # get json name
                    json_name_cache = file[:4]
                    # extract json file
                    shutil.copy(os.path.join(folder, file), os.path.join("temp", file))
            # collect settings.h
            for file in os.listdir(folder):
                if file == 'settings.h':
                    shutil.copy(os.path.join(folder, file), os.path.join("temp", json_name_cache + ".settings.h"))
                elif file == 'nohup.out':
                    shutil.copy(os.path.join(folder, file), os.path.join("temp", json_name_cache + ".nohup.out"))

# create zip file
chmodWait("temp")
CreateZipFile("temp")
chmodWait(zip_file_name)
shutil.rmtree("temp")
