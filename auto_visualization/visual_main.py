import numpy as np

from read_data import readDisks
from scalar_analysis import plotEnergySplit, plotPhi4Phi6, getEnergyCurve
from scalar_analysis import getClusterSizeCurve, getAveScalarOrderCurve

dst_dir = '../pyOutput/'
src_dir = '../packingCpp5'
simu_name = 'qjfc94231'

if __name__ == '__main__':

    ifplot = True

    metadata, disks = readDisks(src_dir, dst_dir, simu_name)
    energy_curve = getEnergyCurve(disks)

    for i in range(0, len(disks)):
        print('index: ', i, end='\t')
        d = disks[i]

        # nematic_orders.append(d.aveScalarOrder())
        # angle_diff_dist.append(d.angleClusterSizeDist())

        if ifplot:
            # d.plotConfigurationOnly(False)
            # d.plotD4Field()
            # d.plotOrientationAngles(True)
            d.plotScalarOrder(True)
            # d.plotNematicInterpolation()

    # plotEnergySplit(disks)
    # plotPhi4Phi6(disks)

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
