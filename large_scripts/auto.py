import concurrent.futures
import itertools

import pandas as pd

import json_output as jo
from param_convert import ExperimentFixedSettings
from multiprocessing import cpu_count

fixed_settings = ExperimentFixedSettings(100, 1, 0.1)

n = [1, 2, 3]
Gamma = [1, 2, 3]
phi_f = [1, 1.5, 2]
param_list = list(itertools.product(n, Gamma, phi_f))

suc = pd.DataFrame(index=range(len(param_list)), columns=["success"])

# 创建一个线程池（只能采用线程池，因为主函数不可pickle。由于编译c++是新开进程的，对性能无影响。）
jo.createTempDir()
with concurrent.futures.ThreadPoolExecutor(max_workers=cpu_count()) as executor:
    # 并行处理所有项目，并记录结果
    success_iterator = executor.map(fixed_settings, param_list)
suc["success"] = list(success_iterator)

# 转储结果
suc.to_csv('tasks_success.csv')
jo.tempToZip()
