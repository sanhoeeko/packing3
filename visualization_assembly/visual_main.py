import json
from multiprocessing import Pool
from os import getcwd

from visualization import *

dst_dir = '../pyOutput/'
src_dir = '../packingCpp5'


def read_disks_prepare(simu_name: str):
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


def initialize_disk(ith_disk_src: tuple):
    """
    :Parameter ith_disks_src: 
        [0] i:int
        [1] disks_src[i]: json dict object of the data
        [2] metadata: json object of the metadata
    """
    data = ith_disk_src[1]
    metadata = ith_disk_src[2]
    return Disk(data, metadata, getcwd() + '\\' + dst_dir)


def read_disks_mp(metadata, disks_src: list) -> list[Disk]:
    n = len(disks_src)
    rng = range(n)
    meta = [metadata] * n
    # parallel code
    with Pool(4) as pool:  # using 4 processing
        res = pool.map(initialize_disk, zip(rng, disks_src, meta))
    return res


def read_disks_sp(metadata, disks_src: list) -> list[Disk]:
    n = len(disks_src)
    rng = range(n)
    meta = [metadata] * n
    # single processing code
    return list(map(initialize_disk, zip(rng, disks_src, meta)))


simu_name = 'kolu'

if __name__ == '__main__':

    ifplot = True

    disks_src, metadata = read_disks_prepare(simu_name)
    disks = read_disks_sp(metadata, disks_src)
    energy_curve = metadata['energy curve']
    descent_curves = []
    orientation_order_dist = []
    best_angles = []
    nematic_orders = []
    # density_curve = []
    # p6s = []
    # p4s = []

    for i in range(0, len(disks)):
        print("index: ", i, end='\t')
        d = disks[i]

        descent_curves.append(d.energy_curve)
        orientation_order_dist.append(d.calOrientationOrder())
        best_angles.append(d.meanOrientation())
        nematic_orders.append(d.nematicOrder())
        # density_curve.append(d.number_density())
        # p6s.append(d.averageBondOrientationalOrder(6))
        # p4s.append(d.averageBondOrientationalOrder(4))

        if ifplot:
            # disks[i].plotConfigurationOnly()
            disks[i].plotOrientationAngles(True)
            disks[i].plotVoronoiNeighbors(False)
            # disks[i].plotPsi6(True)
            # disks[i].plotPsi5(True)
            # disks[i].plotPsi4(True)
            # disks[i].plotForceNetwork()

    # mat = np.array(orientation_order_dist).T
    # mat = move_ave(mat, 40).T

    # plt.rcParams.update({"font.size":22})
    plotEnergySplit(descent_curves[1:])
    # plt.ylim((-1, 0.5))
    # plt.xlabel('relaxation iterations t')
    # plt.ylabel('y(t)')

    '''
    plt.rcParams.update({"font.size":22})
    plt.plot(density_curve, p6s, 'x')
    plt.plot(density_curve, p4s, '+')
    plt.xlabel('packing fraction')
    plt.legend(['6-fold', '4-fold'])
    '''
    '''
    plt.plot(fraction_curve, contact_curve, 'x')
    plt.xlabel('packing fraction')
    plt.ylabel('contact number')
    
    interval = np.array(fraction_curve) > 0.84
    plt.plot(np.array(fraction_curve)[interval], np.array(energy_curve)[interval], 'x')
    plt.yscale('log')
    plt.xlabel('packing fraction')
    plt.ylabel('energy')
    '''
