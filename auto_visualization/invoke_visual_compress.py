import json
import os

import pandas as pd
import math

from visualization import Disk
from visualization_paint import ScaleHelper
import scalar_analysis as sc


def makeDstDir(folder: str):
    dir_name = os.path.join(folder, "visualization")
    if not os.path.exists(dir_name):
        os.mkdir(dir_name)
    return dir_name


def makeDstDstDir(dst_dir: str, name: str):
    dir_name = os.path.join(dst_dir, name)
    if not os.path.exists(dir_name):
        os.mkdir(dir_name)
    return dir_name + '/'


src_dir = '../data/gamma175c'
dst_dir = makeDstDir(src_dir)


# rate = 0.99288  # gamma125c
# rate = 0.9936  # gamma150c
rate = 0.99418  # gamma175c
# rate = 0.99466  # gamma2c
# rate = 0.996  # gamma3c
# rate = 0.9968  # gamma4c

files = [f for f in os.listdir(src_dir) if os.path.isfile(os.path.join(src_dir, f))]
names = list(set(map(lambda x: x.split('.')[0], files)))
disk_groups = []
meta_frame = pd.DataFrame(data=None, columns=['name', 'n', 'Gamma', 'phi_f', 'terminal A', 'terminal B'])
for name in names:
    disks = []
    try:
        with open(os.path.join(src_dir, name + '.json'), 'r') as r:
            data = r.read()
        data_lst = data.split('\n')
        data_lst = list(filter(lambda x: len(x) > 0 and x[0] == '{', data_lst))
        json_lst = list(map(json.loads, data_lst))
        with open(os.path.join(src_dir, name + '.metadata.json'), 'r') as r:
            metadata = json.load(r)
        for i in range(len(json_lst)):
            d = Disk(json_lst[i], metadata, makeDstDstDir(dst_dir, name), sz=500)
            d.Lb = d.La * rate ** (i + 1)
            d.LbM = d.LaM * math.sqrt(d.Lb / d.La)
            d.helper = ScaleHelper(d.height / d.LbM, d.LaM, d.LbM)
            d.relative_helper = ScaleHelper(d.height / d.Lb, d.La, d.Lb)
            disks.append(d)
            # make a list of name and metadata (name, n, Gamma, phi_f)
            meta_frame.loc[len(meta_frame)] = [name, d.ass_n, d.Gamma, d.ideal_packing_density(), d.La, d.Lb]
    except Exception as e:
        print("An error occurred when reading data: ", e)
    disk_groups.append(disks)
disk_groups.sort(key=lambda x:x[0].Gamma)
    

xs = sc.getDensityCurve(disk_groups[0])
# phi4, phi6 = sc.getPhi4Phi6(disk_groups[0])
ys = sc.getScalarOrderByX(disk_groups[0])
# ys = sc.getAveScalarOrderCurve(disk_groups[0])

# perform a set of visualization
ifplot = False

for disks in disk_groups:
    for d in disks:
        if ifplot:
            if d.ass_n == 1:
                d.plotConfigurationOnly(True)
                pass
            else:
                d.plotOrientationAngles()
                # d.plotD4Field()
                # d.plotD4Interpolation()

