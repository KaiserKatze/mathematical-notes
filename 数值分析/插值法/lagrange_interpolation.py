#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Callable
import numpy as np


def interpolate(xy: list[tuple[float, float]], x0: float, order: int) -> Callable[[float], float]:
    """
    拉格朗日插值

    :param xy: 已知点
    :type xy: list[tuple[float, float]]
    :param x0: 未知点的横坐标
    :type x0: float
    :param order: 阶数；当 n=1 时使用线性插值；当 n=2 时使用二次插值；以此类推
    :type order: int
    :return: 函数
    :rtype: Callable[[float], float]
    """
    if not order >= 1:
        raise ValueError('阶数 `order` 必须大于或等于 1 !')
    len_xy = len(xy)
    N = order + 1
    if len_xy < N:
        raise ValueError('已知点个数应该大于阶数!')
    # 首先从已知点中找出横坐标离 x0 最近的 N 个点
    vec_xy = np.array(xy, dtype=np.float32)
    vec_x = vec_xy[:, 0]
    vec_dist = np.abs(vec_x - x0)
    indices_nearest = np.argpartition(vec_dist, N-1)[:N]
    vec_z = vec_xy[indices_nearest, :]
    vec_z0 = vec_z[:, 0]

    def result_fn(t):
        acc = 0.0
        for iz, z in enumerate(vec_z0):
            kz = vec_z[iz, 1]
            for jw in range(len(vec_z)):
                if iz == jw:
                    continue
                w = vec_z0[jw]
                kz *= (t - w) / (z - w)
            acc += kz
        return acc

    return result_fn


if __name__ == '__main__':
    def test():
        xy = [
            (0.4, -0.916291),
            (0.5, -0.693147),
            (0.6, -0.510826),
            (0.7, -0.356657),
            (0.8, -0.223144),
        ]
        print('线性插值计算结果：')
        val = interpolate(
            xy,
            x0=0.54,
            order=1,
        )(0.54)
        print(f'\tf(0.54) = {val:.6f}')
        print('-' * 50)
        print('二次插值计算结果：')
        val = interpolate(
            xy,
            x0=0.54,
            order=2,
        )(0.54)
        print(f'\tf(0.54) = {val:.6f}')

    test()
