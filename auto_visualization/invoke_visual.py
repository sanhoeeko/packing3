import json
import os

import pandas as pd

from visualization import Disk
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


src_dir = '../data/gamma4'
dst_dir = makeDstDir(src_dir)

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
            disks.append(d)
            # make a list of name and metadata (name, n, Gamma, phi_f)
            meta_frame.loc[len(meta_frame)] = [name, d.ass_n, d.Gamma, d.ideal_packing_density(), d.La, d.Lb]
    except Exception as e:
        print("An error occurred when reading data: ", e)
    disk_groups.append(disks)
disk_groups.sort(key=lambda x:x[0].Gamma)
    

# sc.plotEnergys(disk_groups)
xs = sc.getDensityCurve(disk_groups[-1])
ys = sc.getScalarOrderByX(disk_groups[-1])


# perform a set of visualization
ifplot = False

for disks in disk_groups:
    for d in disks:
        if ifplot:
            if d.ass_n == 1:
                d.plotConfigurationOnly(True)
                pass
            else:
                # d.plotOrientationAngles()
                # d.plotVoronoiNeighbors(True)
                try:
                    d.plotPhi4(True)
                    d.plotPhi6(True)
                except:
                    pass
                # d.plotD4Field()

# meta_frame['S order'] = S_order
# meta_frame.to_csv("scalar results.csv")
