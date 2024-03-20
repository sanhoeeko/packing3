import os
import shutil
import subprocess

import create_settings as cs

default_src = 'source code'  # located as the same directory as this script
counter = 0


def duplicateFolder():
    global counter
    counter += 1
    dst = str(counter)
    if os.path.exists(dst):
        raise FileExistsError
    shutil.copytree(default_src, dst)
    return counter


def newExperiment(**kwargs):
    # duplicate the project
    index = duplicateFolder()
    # update the setting
    simu = cs.SimulationOptions(**kwargs)
    header_file = os.path.join(str(index), 'settings.h')
    setting_items = cs.collectSettingItems(header_file)
    simu.updateSettingItems(setting_items)
    with open(header_file, 'w') as w:
        w.write(cs.itemsToFile(setting_items))
    # compile the project
    compile_command = f"g++ *.cpp -o a.out -std=c++17 -O3 -Ofast -mavx -mfma -fopenmp -march=native"
    p = subprocess.Popen(compile_command, shell=True, cwd=f"{str(index)}")
    # wait the compiling terminating
    _compile_success = p.wait()
    # run the project
    outfile = f"nohup.out"
    run_command = f"nohup ./a.out 2>>{outfile} 1>>{outfile} &"
    subprocess.Popen(run_command, shell=True, cwd=f"{str(index)}")
    print("Successfully run a simulation.")
