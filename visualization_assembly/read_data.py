import json
from multiprocessing import Pool
from os import getcwd

from visualization import Disk


def read_disks_prepare(src_dir: str, simu_name: str):
    # load metadata
    meta_file = '\\'.join([getcwd(), src_dir, simu_name + '.metadata.json'])
    with open(meta_file) as fp:
        metadata = json.load(fp)
    # get list of json
    data_file = '\\'.join([getcwd(), src_dir, simu_name + '.json'])
    with open(data_file) as fp:
        data = fp.read()
    data_lst = data.split('\n')
    data_lst = list(filter(lambda x: len(x) > 0 and x[0] == '{', data_lst))
    json_lst = list(map(json.loads, data_lst))
    return json_lst, metadata


def initialize_disk(dst_dir: str):
    def initialize_disk_curry(ith_disk_src: tuple):
        """
        :Parameter ith_disks_src:
            [0] i:int
            [1] disks_src[i]: json dict object of the data
            [2] metadata: json object of the metadata
        """
        data = ith_disk_src[1]
        metadata = ith_disk_src[2]
        return Disk(data, metadata, getcwd() + '\\' + dst_dir)

    return initialize_disk_curry


def read_disks_mp(dst_dir, metadata, disks_src: list) -> list[Disk]:
    n = len(disks_src)
    rng = range(n)
    meta = [metadata] * n
    # parallel code
    with Pool(4) as pool:  # using 4 processing
        res = pool.map(initialize_disk(dst_dir), zip(rng, disks_src, meta))
    return res


def read_disks_sp(dst_dir, metadata, disks_src: list) -> list[Disk]:
    n = len(disks_src)
    rng = range(n)
    meta = [metadata] * n
    # single processing code
    return list(map(initialize_disk(dst_dir), zip(rng, disks_src, meta)))


def readDisks(src_dir: str, dst_dir: str, simu_name: str, enable_mp=False):
    disks_src, metadata = read_disks_prepare(src_dir, simu_name)
    if enable_mp:
        disks = read_disks_mp(dst_dir, metadata, disks_src)
    else:
        disks = read_disks_sp(dst_dir, metadata, disks_src)
    return metadata, disks
