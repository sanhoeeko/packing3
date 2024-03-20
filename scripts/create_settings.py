"""
mutable setting items:
PARTICLE_NUM            ASSEMBLY_NUM                SPHERE_DIST                 BOUNDARY_A
COMPRESSION_RATE        NUM_COMPRESSIONS            OUTPUT_STRIDE               BOUNDARY_B
MAX_ITERATIONS          MAX_INIT_ITERATIONS         SCALAR_POTENTIAL_TYPE       BSHAPE
"""

import re

header_head = """
#pragma once
#define RECORD_TIME
enum class ScalarF { Power, Exp };
"""


class SettingItem:
    def __init__(self, lst: list[str]):
        self.key = lst[0]
        self.value = lst[1]
        self.appendix = lst[2:]

    def toString(self):
        return ' '.join(['#define', self.key, self.value])


def itemsToFile(lst: list[SettingItem]):
    data = '\n'.join(list(map(lambda x: x.toString(), lst)))
    data = re.sub('\n\n', '\n', data)
    return header_head + '\n' + data


class SimulationOptions:
    def __init__(self, **kwargs):
        self.dic = kwargs

    def updateSettingItems(self, settings: list[SettingItem]):
        for k, v in self.dic.items():
            for s in settings:
                if s.key == k:
                    s.value = str(v)
                    break


def collectSettingItems(header_file: str):
    with open(header_file, 'r') as r:
        lines = r.readlines()
    items = []
    for line in lines:
        arr = line.split(' ')
        if len(arr) >= 3 and arr[0] == '#define':
            items.append(SettingItem(arr[1:]))
    return items
