import numpy as np
import matplotlib.pyplot as plt

from read_data import readDisks
import scalar_analysis as sc

dst_dir = '../mjkl54461/'
src_dir = '../ass31'
simu_names = ['fnym94260', 'quho94281', 'tpac94258']
# simu_name = 'pois94245'

'''
if __name__ == '__main__':

    ifplot = False

    metadata, disks = readDisks(src_dir, dst_dir, simu_name)
    energy_curve = sc.getEnergyCurve(disks)

    for i in range(0, len(disks)):
        print('index: ', i, end='\t')
        d = disks[i]

        # nematic_orders.append(d.aveScalarOrder())
        # angle_diff_dist.append(d.angleClusterSizeDist())

        if ifplot:
            d.plotConfigurationOnly(True)
            # d.plotD4Field()
            # d.plotOrientationAngles(True)
            # d.plotScalarOrder(True)
            # d.plotNematicInterpolation()

    # sc.plotEnergySplit(disks)
    # sc.plotPhi4Phi6(disks)
    # sc.plotScalarOrderAndMeanCluster(disks)
    sc.imshowAngleDist(disks)

    '''
for name in simu_names:
    metadata, disks = readDisks(src_dir, dst_dir, name)
    print(metadata)
    sc.imshowAngleDist(disks)
    break
    # sc.plotPhi4Phi6(disks)
    # sc.plotScalarOrderAndMeanCluster(disks)
    # ovs = sc.getOverallScalarOrderNormalized(disks)
    # xs = sc.getIdealDensityCurve(disks)
    # plt.plot(xs, ovs)
