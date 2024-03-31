import numpy as np

from read_data import readDisks
from visualization import Disk, plotEnergySplit

dst_dir = '../pyOutput/'
src_dir = '../packingCpp5'
simu_name = 'fzpt'

if __name__ == '__main__':

    ifplot = False

    metadata, disks = readDisks(src_dir, dst_dir, simu_name)
    descent_curves = []
    best_angles = []
    nematic_orders = []
    energy_curve = []
    angle_diff_dist = []
    p6s = []
    p4s = []

    for i in range(0, len(disks)):
        print('index: ', i, end='\t')
        d = disks[i]

        descent_curves.append(d.energy_curve)
        energy_curve.append(d.energy_ref)
        # nematic_orders.append(d.aveScalarOrder())
        # angle_diff_dist.append(d.angleClusterSizeDist())
        
        # d_spheres = Disk.fromConfigurationC(d.toSpheres(), d)
        # p6s.append(d_spheres.averageBondOrientationalOrder(6))
        # p4s.append(d_spheres.averageSquareOrder(4))

        if ifplot:
            d.plotConfigurationOnly(True)
            d.plotVoronoiAsSpheres(True)
            # d.plotOrientationAngles(True)
            # d.plotScalarOrder(True)
            # d.plotPsi6AsSpheres(True)
            # d.plotPsi4AsSpheres(True)

    best_angles = np.array(best_angles)
    best_angles = (best_angles + np.pi / 2) % np.pi - np.pi / 2

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
