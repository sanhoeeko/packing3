import os

import json_output as jo

if __name__ == '__main__':
    def isDstPath(name: str):
        this_name = name.split('/')[-1]
        if this_name == 'temp' or this_name.isdigit():
            return True
        return False


    # call this script for emergent output
    current_dir = '..'
    os.chdir(current_dir)
    jo.createTempDir(os.path.join(current_dir, "__temp__"))

    for root, dirs, files in os.walk(current_dir):
        for d in dirs:
            if isDstPath(d):
                jo.extractData(d)
    jo.tempToZip(os.path.join(current_dir, "__temp__"))
