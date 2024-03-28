import os
import shutil
import subprocess
import threading
import time

import psutil

import create_settings as cs
import json_output as jo

default_src = 'source code'  # located as the same directory as this script

counter_lock = threading.Lock()  # 用互斥锁保护跨线程全局变量
counter = 0


def duplicateFolder():
    global counter
    with counter_lock:  # 复制文件是单线程（阻塞）的，但不是耗时操作
        counter += 1
        dst = str(counter)
        if os.path.exists(dst):
            raise FileExistsError
        shutil.copytree(default_src, dst)
        return counter


def check_and_move_output(dirname):
    # 检测进程是否退出
    time.sleep(10)
    while True:
        all_procs = psutil.process_iter(['pid', 'name'])
        a_out_procs = [proc for proc in all_procs if proc.info['name'] == f'a{dirname}.out']
        if not a_out_procs:
            break
        time.sleep(1)

    # 提取数据
    jo.extractData(dirname)
    # 删除目录
    shutil.rmtree(dirname)


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
    compile_command = f"g++ *.cpp -o a{str(index)}.out -std=c++17 -O3 -Ofast -mavx -mfma -fopenmp -march=native"
    subprocess.run(compile_command, shell=True, cwd=f"{str(index)}")
    # run the project
    outfile = "nohup.out"
    run_command = f"nohup ./a{str(index)}.out 2>>{outfile} 1>>{outfile} &"
    subprocess.run(run_command, shell=True, cwd=f"{str(index)}")
    # print(f"Successfully started a simulation for project .")
    try:
        check_and_move_output(str(index))
        print(f"Simulation {index} successfully terminated.")
        return True
    except Exception as e:
        # If an exception occurs, print the error message and return False
        print(f"An exception occurred while processing: {e}")
        return False
