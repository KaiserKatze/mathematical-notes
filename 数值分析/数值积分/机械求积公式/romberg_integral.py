#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
本程序利用龙贝格求积算法计算定积分。
在计算时，以LaTeX的格式，打印超参数、梯形值和加速值。

@author: KaiserKatze
@date: 2025-11-29
"""

import numpy as np


def print_t_table(t_table: dict[tuple[int, int], float]):
    """
    打印 T 表
    """
    for i in range(100):
        for j in range(i):
            row = i - 1 - j
            col = j
            try:
                entry = t_table[col, row]
            except KeyError:
                return
            print(f'\t{entry:.8f}', end='')
            # print(f'\tT_{col}^{{({row})}}', end='')
        print()


def romberg_integral(fn, a, b, tol, min_iter=5, dtype=np.float32):
    """
    龙贝格求积算法

    Args
        fn          被积函数
        a           积分下限
        b           积分上限
        tol         近似精度
        min_iter    最低迭代次数

    Returns
        T[k,0]      积分近似值
    """

    h = b - a  # 初始步长
    k = 0  # 初始均分次数
    T = {}
    T[0,0] = .5 * h * ( fn(a) + fn(b) )

    print(f'''积分下限\\(a=\\num{{{a:.8f}}}\\)，积分上限\\(b=\\num{{{b:.8f}}}\\)，初始化步长\\(h=\\num{{{h:.8f}}}\\)，初始化均分次数\\(k={k}\\)，那么\\begin{{equation*}}
	T_0^{{(0)}} \\defeq \\frac{{h}}{{2}} ( f(a) + f(b) ) = \\num{{{T[0,0]:.8f}}}.
\\end{{equation*}}
''')

    while True:
        n = 2**k
        k += 1
        x = a + (np.arange(n, dtype=dtype) + .5) * h
        sum_fn_x = fn(x).sum()
        T[0,k] = .5 * T[0,k-1] + .5 * h * sum_fn_x
        for j in range(1, k+1):
            j4 = 4**j
            j41 = j4 - 1
            # 按你算法保存位置：T[j, k-j] 对应表中第 k 行第 j 列 (T_j^{(k-j)})
            T[j,k-j] = T[j-1,k-j+1] * j4 / j41 - T[j-1,k-j] / j41

        print(f'''令\\(n \\defeq 2^k = {n}, k \\defeq k+1 = {k}\\)，则\\begin{{align*}}''')
        print(f'\tT_0^{{({k})}} &= \\frac{{1}}{{2}} T_0^{{({k-1})}} + \\frac{{1}}{{2}} \\sum_{{i=0}}^{{n-1}} f(x_{{i+1/2}}) \\approx \\num{{{T[0,k]:.8f}}}, \\\\')
        for j in range(1, k):
            print(f'\tT_{j}^{{({k-j})}} &= \\frac{{4^{j}}}{{4^{j}-1}} T_{j-1}^{{({k-j+1})}} - \\frac{{1}}{{4^{j}-1}} T_{j-1}^{{(k-j)}} \\approx \\num{{{T[j,k-j]:.8f}}}, \\\\')
        j = k
        print(f'\tT_{j}^{{({k-j})}} &= \\frac{{4^{j}}}{{4^{j}-1}} T_{j-1}^{{({k-j+1})}} - \\frac{{1}}{{4^{j}-1}} T_{j-1}^{{(k-j)}} \\approx \\num{{{T[j,k-j]:.8f}}}.')
        print('\\end{align*}')

        diffTk0 = np.abs(T[k,0] - T[k-1,0])
        diffTkj = np.abs(T[k,0] - T[k-1,1])
        cond_stop_iter = diffTk0 < tol and diffTkj < tol and min_iter <= 0

        if cond_stop_iter:
            print(f'第 {k} 轮迭代的误差为\\(\\abs{{ T_{k}^{{(0)}} - T_{k-1}^{{(0)}} }} = \\num{{{diffTk0:.8f}}} < \\num{{{tol:.8f}}}\\)，停止计算! 所求积分近似值为\\(\\num{{{T[k,0]:.8f}}}\\).')
        else:
            print(f'令\\(h \\defeq h/2 = \\num{{{h/2:.8f}}}\\).')
        print()

        if cond_stop_iter:
            break
        min_iter -= 1
        h *= .5

    return T[k,0]


if __name__ == '__main__':
    # NIntegrate[x Sin[x],{x,0,2 Pi}]
    romberg_integral(lambda x: x * np.sin(x), 0, 2 * np.pi, 1e-5, min_iter=5)
