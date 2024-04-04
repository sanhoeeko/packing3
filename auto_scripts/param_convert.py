import math

import pandas as pd

from project_replica import newExperiment


def get_axis_from_fraction(n, N, R, Gamma, phi0):
    """
    :param n: assembly number
    :param N: particle number
    :param R: sphere distance
    :param Gamma: aspect ratio of boundary
    :param phi0: ideal packing fraction
    :return:
    """
    B = math.sqrt((math.pi + 2 * R * (n - 1)) * N / (math.pi * Gamma * phi0))
    A = Gamma * B
    return A, B


def get_axis_from_sphere_fraction(n, N, R, Gamma, rho0):
    """
    rho0 is the packing fraction of circumscribe spheres. suggest: rho0 < 0.4
    """
    gamma = 1 + (n - 1) * R / 2
    B = gamma * math.sqrt(N / (Gamma * rho0))
    A = Gamma * B
    return A, B


def get_boundary_type(gamma):
    return "BoundaryC" if gamma == 1 else "BoundaryE"


def ExperimentFixedSettings(N: int, R: float, rho0: float, phi_f: float):
    """
    :return: Callable which accepts a tuple: (n, Gamma, phi_f)
    """

    def _invokeNewExperiment(n: int, Gamma: float):
        a, b = get_axis_from_fraction(n, N, R, Gamma, phi_f)
        A, B = get_axis_from_sphere_fraction(n, N, R, Gamma, rho0)
        print(f"initial: A={A}, B={B}; final: a={a}, b={b}")
        return newExperiment(PARTICLE_NUM=N, ASSEMBLY_NUM=n, SPHERE_DIST=R, END_BOUNDARY_B=b,
                             BOUNDARY_A=A, BOUNDARY_B=B, BSHAPE=get_boundary_type(Gamma))

    def invokeNewExperiment(tup: tuple):
        assert len(tup) == 2
        return _invokeNewExperiment(*tup)

    return invokeNewExperiment


def read_csv_and_convert_to_dicts(csv_file):
    # 读取CSV文件
    df = pd.read_csv(csv_file, dtype=str)

    # 初始化一个空列表，用于存储字典
    result = []

    # 遍历每一行数据
    for _, row in df.iterrows():
        # 初始化一个空字典，用于存储每一行的参数
        params = {}

        # 遍历每一列
        for col in df.columns:
            value = row[col]

            # 如果单元格不为空
            if pd.notna(value):
                # 尝试将值转换为整数、浮点数或字符串
                try:
                    params[col] = int(value)
                except ValueError:
                    try:
                        params[col] = float(value)
                    except ValueError:
                        params[col] = str(value)

        # 将参数字典添加到结果列表中
        result.append(params)

    return result
