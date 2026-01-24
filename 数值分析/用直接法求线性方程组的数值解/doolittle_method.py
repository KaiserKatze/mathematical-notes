#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np


def doolittle_method(A: np.ndarray, format: str = '.4f'):
    print('使用[杜立特方法]进行 LU 分解 ...')
    dim_A = A.shape[0]
    assert A.shape[1] == dim_A
    result = A.copy()
    # 第一次迭代
    # 计算 U 矩阵
    for j in range(0, dim_A):
        print(f'u_{{1,{j+1}}} := a_{{1,{j+1}}}')
    # 计算 L 矩阵
    for i in range(1, dim_A):
        print(f'l_{{{i+1},1}} := a_{{{i+1},1}} / a_{{1,1}}')
        result[i, 0] /= result[0, 0]
    # 第二次以后
    for r in range(1, dim_A):
        # 先计算 U 矩阵
        for j in range(r, dim_A):
            print(f'u_{{{r+1},{j+1}}} := a_{{{r+1},{j+1}}}', end='')
            for k in range(0, r):
                print(f' - l_{{{r+1},{k+1}}} u_{{{k+1},{j+1}}}', end='')
                result[r, j] -= result[r, k] * result[k, j]
            print()
        # 再计算 L 矩阵
        for i in range(r + 1, dim_A):
            print(f'l_{{{i+1},{r+1}}} := ( a_{{{i+1},{r+1}}}', end='')
            for k in range(0, r):
                print(f' - l_{{{r+1},{k+1}}} u_{{{k+1},{j+1}}}', end='')
                result[i, r] -= result[i, k] * result[k, r]
            print(f' ) / u_{{{r+1},{r+1}}}')
            result[i, r] /= result[r, r]
    print('计算结果:\n', result)
    return result


if __name__ == '__main__':
    doolittle_method(
        np.array(
            [
                [1, 2, 3],
                [2, 5, 2],
                [3, 1, 5],
            ]
        )
    )
