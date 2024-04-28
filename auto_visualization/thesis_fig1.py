import matplotlib.pyplot as plt

import scalar_analysis as sc
from read_data import readDisks

ifplot = False

dst_dir = '../pyOutput/'
data = [#readDisks('../gamma1', dst_dir, 'dacl55513'),
        readDisks('../gamma106', dst_dir, 'ghyx49052'),
        readDisks('../gamma125', dst_dir, 'peyd97211'),
        #readDisks('../gamma150', dst_dir, 'mocl78355'),
        readDisks('../gamma175', dst_dir, 'mwho78905'),
        readDisks('../gamma2+', dst_dir, 'hjwl126001')
        ]

plt.rcParams.update({"font.size": 24})
for m, d in data:
    print(m)
    xs, disks = sc.densityUpTo(d, 2.0)
    ys = sc.getAveScalarOrderCurve(disks)
    plt.plot(xs, ys)
plt.legend(list(map(lambda x:'γ=' + str(x[0]['particle aspect ratio']), data)))
plt.xlabel('ρ')
plt.ylabel('S')