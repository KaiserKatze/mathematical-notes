#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np


def matrix_power_method(A: np.ndarray, tol: float = 1e-8, max_iter: int = 100, formatter: str = '.4f') -> tuple[float, np.ndarray]:
    """
    求出任意矩阵的按模最大特征值及其特征向量

    :param A: 待求特征值的矩阵
    :type A: np.ndarray
    :param tol: 精度要求
    :type tol: float
    :param max_iter: 最大迭代次数
    :type max_iter: int
    :param formatter: 浮点数输出格式
    :type formatter: str
    :return: 近似特征值及其特征向量
    :rtype: tuple[float, ndarray[_AnyShape, dtype[Any]]]
    """
    dim_A = A.shape[0]
    if A.ndim != 2 or A.shape[1] != dim_A:
        raise ValueError('矩阵必须为方阵.')
    muk = 0.0
    uk = np.ones(dim_A)

    # print(f'第 0 轮算得近似特征值、特征向量分别为:\n\t{muk}\t{uk}')
    print(
        '计算过程如下表所示.\n'
        '\\begin{center}\n'
        f'\t\\begin{{tblr}}{{c|*{{{dim_A}}}c|c}}\n'
        '\t\t\\hline\n'
        f'\t\tk & \\SetCell[c={dim_A}]{{c}} $u_k^T$ (规范化向量) '
        f'{"&" * dim_A}'
        ' $\\max v_k$ \\\\\n'
        '\t\t\\hline'
    )
    vec_str = ' & '.join(f'{x:{formatter}}' for x in uk)
    print(f'\t\t0 & {vec_str} & \\\\')
    for i in range(1, max_iter):
        vk1 = A @ uk                            # $v_{k+1} = A u_k$
        muk1 = vk1[np.argmax(np.abs(vk1))]      # 找出向量 $v_{k+1}$ 的、绝对值最大的分量 $\mu_{k+1}$
        uk1 = vk1 / muk1                        # 进行归一化 $u_{k+1} = v_{k+1} / \mu_{k+1}$
        # print(f'第 {i} 轮算得近似特征值、特征向量分别为:\n\t{muk1}\t{uk1}')
        vec_str = ' & '.join(f'{x:{formatter}}' for x in uk1)
        print(f'\t\t{i} & {vec_str} & {muk1:{formatter}} \\\\')
        if abs(muk1 - muk) < tol:
            uk = uk1    # 更新近似特征向量
            muk = muk1  # 更新近似特征值
            break
        uk = uk1        # 更新近似特征向量
        muk = muk1      # 更新近似特征值
    print(
        '\t\t\\hline\n'
        '\t\\end{tblr}\n'
        '\\end{center}'
    )
    return muk, uk

# TODO 加速方法：
# 1. 原点平移法
# 2. 瑞利商加速法

if __name__ == '__main__':
    def test():
        print("--- Test Case 1 ---")
        A = np.diag([2, 3, 4]).astype(np.float32)
        eig_A, _ = matrix_power_method(A, tol=1e-8, formatter='.7f')
        print(f'A 的按模最大特征值: {eig_A:.8f}')
        eig_A_baseline = (A_eig := np.linalg.eig(A).eigenvalues)[np.argmax(np.abs(A_eig))]
        print(f'A 的按模最大特征值 (baseline): {eig_A_baseline:.7f}')
        assert abs(eig_A - 4) < 1e-8, '矩阵 A 的按模最大特征值计算错误.'

        print("\n--- Test Case 2 ---")
        B = np.diag([-1, -5, -8, 4, 7]).astype(np.float32)
        eig_B, _ = matrix_power_method(B, tol=1e-8, formatter='.7f')
        print(f'B 的按模最大特征值: {eig_B:.8f}')
        eig_B_baseline = (B_eig := np.linalg.eig(B).eigenvalues)[np.argmax(np.abs(B_eig))]
        print(f'B 的按模最大特征值 (baseline): {eig_B_baseline:.7f}')
        assert abs(eig_B - (-8)) < 1e-8, '矩阵 A 的按模最大特征值计算错误.'

    test()
