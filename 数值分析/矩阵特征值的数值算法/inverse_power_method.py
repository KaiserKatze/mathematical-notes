#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
from scipy.linalg import lu, solve_triangular

def inverse_power_method(A: np.ndarray, p0: float = 0.0, tol: float = 1e-8, max_iter: int = 100, formatter: str = '.8f') -> tuple[float, np.ndarray]:
    """
    求出任意非奇异矩阵的按模最小特征值及其特征向量

    :param A: 待求特征值的矩阵
    :type A: np.ndarray
    :param p0: 平移量
    :type p0: float
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

    mB = A - p0 * np.eye(dim_A)             # 将矩阵 A 平移
    mP, mL, mU = lu(mB)                     # 进行 LU 分解，使得 A = P @ L @ U
    # 我们解方程 (A - pI) v = u
    # 相当于 P L U v = u
    # 相当于 L U v = P^T u (因为 P 是正交阵, P^-1 = P^T)
    # 不计算显式逆矩阵，避免精度灾难

    muk = 0.0
    uk = np.ones(dim_A)

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
        rhs = mP.T @ uk
        yk1 = solve_triangular(mL, rhs, lower=True)     # 解方程 $L y_{k+1} = P u_k$
        vk1 = solve_triangular(mU, yk1, lower=False)    # 解方程 $U v_{k+1} = y_{k+1}$
        muk1 = vk1[np.argmax(np.abs(vk1))]              # 找出向量 $v_{k+1}$ 的、绝对值最大的分量 $\mu_{k+1}$
        uk1 = vk1 / muk1
        vec_str = ' & '.join(f'{x:{formatter}}' for x in uk1)
        print(f'\t\t{i} & {vec_str} & {muk1:{formatter}} \\\\')
        if i > 1 and abs((muk1 - muk) / (muk1 * muk)) < tol:
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
    return p0 + 1.0 / muk, uk

if __name__ == '__main__':
    def test():

        print("--- Test Case 1 ---")
        A = np.diag([2, 3, 4]).astype(np.float32)
        eig_A, _ = inverse_power_method(A, p0 := 1.8, tol=1e-8, formatter='.7f')
        print(f'A 的按模最小特征值: {eig_A:.8f}')
        eig_A_baseline = (A_eig := np.linalg.eig(A).eigenvalues)[np.argmin(np.abs(A_eig - p0))]
        print(f'A 的按模最小特征值 (baseline): {eig_A_baseline:.7f}')
        assert abs(eig_A - 2) < 1e-8, '矩阵 A 的按模最小特征值计算错误.'

        print("\n--- Test Case 2 ---")
        B = np.array([
            [2.0, 1.0, 0.0],
            [1.0, 3.0, 1.0],
            [0.0, 1.0, 4.0],
        ], dtype=np.float64)
        eig_B, _ = inverse_power_method(B, p0 := 1.8, tol=1e-8, formatter='.7f')
        print(f'B 的按模最小特征值: {eig_B:.8f}')
        eig_B_baseline = (B_eig := np.linalg.eig(B).eigenvalues)[np.argmin(np.abs(B_eig - p0))]
        print(f'B 的按模最小特征值 (baseline): {eig_B_baseline:.7f}')
        assert abs(eig_B - (3 - np.sqrt(3))) < 1e-8, '矩阵 A 的按模最小特征值计算错误.'

    test()
