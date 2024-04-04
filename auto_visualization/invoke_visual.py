import json
import os

import pandas as pd

from visualization import Disk


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


src_dir = '../alljson'
dst_dir = makeDstDir(src_dir)

files = [f for f in os.listdir(src_dir) if os.path.isfile(os.path.join(src_dir, f))]
names = list(set(map(lambda x: x.split('.')[0], files)))
disks = []
meta_frame = pd.DataFrame(data=None, columns=['name', 'n', 'Gamma', 'phi_f', 'terminal A', 'terminal B'])
for name in names:
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
            disks.append(d)
            # make a list of name and metadata (name, n, Gamma, phi_f)
            meta_frame.loc[len(meta_frame)] = [name, d.ass_n, d.Gamma, d.ideal_packing_density(), d.La, d.Lb]
    except Exception as e:
        print("An error occurred when reading data: ", e)

# sort data
meta_frame = meta_frame.sort_values(by=['n', 'Gamma', 'phi_f'])
disks = [disks[i] for i in meta_frame.index.tolist()]
meta_frame = meta_frame.reset_index(drop=True)

# perform a set of visualization
ifplot = True
S_order = []
for d in disks:
    S_order.append(d.aveScalarOrder())
    if ifplot:
        if d.ass_n == 1:
            # d.plotConfigurationOnly(True)
            pass
        else:
            # d.plotOrientationAngles(True)
            # d.plotD4Field()
            d.plotD4Interpolation()

meta_frame['S order'] = S_order
meta_frame.to_csv("scalar results.csv")
