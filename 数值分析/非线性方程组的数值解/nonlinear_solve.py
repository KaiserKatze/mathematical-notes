#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections.abc import Callable


def solve_nonlinear_equation_with_bisection(a: float, b: float, fn: Callable[[float], float], norm_fn: Callable[[float], float] = abs, xtol: float = 1e-8, max_nfev: int = 1000):
    """
    二分法求函数零点

    :param a: 有根区间的左端点
    :type a: float
    :param b: 有根区间的右端点
    :type b: float
    :param fn: 零点待定的函数
    :type fn: Callable[[float], float]
    :param norm_fn: 范数
    :type norm_fn: Callable[[float], float]
    :param xtol: 预定精度
    :type xtol: float
    :param max_nfev: 最大迭代次数
    :type max_nfev: int
    """
    # 准备
    fa = fn(a)
    fb = fn(b)
    print(f'左端点函数值 f({a:+.6e}) ≈ {fa:+.6e}')
    print(f'右端点函数值 f({b:+.6e}) ≈ {fb:+.6e}')
    if fa * fb > 0.0:
        raise ValueError('二分法不适用!')
    if fa == 0.0:
        print(f'找到近似零点 x ≈ {a:+.6e}!')
        return a
    if fb == 0.0:
        print(f'找到近似零点 x ≈ {b:+.6e}!')
        return b
    for i in range(max_nfev):
        # 二分
        t = (a + b) * .5  # 求中点
        ft = fn(t)   # 求中点函数值
        print(f'第 {i} 轮中点函数值 f({t:+.6e}) ≈ {ft:+.6e}')
        # 判断
        if ft == 0.0:
            print(f'找到近似零点 x ≈ {t:+.6e}!')
            return t
        elif ft * fa < 0.0:
            b = t
            fb = ft
        else:  # ft * fa > 0.0
            a = t
            fa = ft
        # 判断
        if norm_fn(a - b) < xtol:
            print(f'找到近似零点 x ≈ {t:+.6e}!')
            return t
    raise ValueError('已达到最大迭代次数!')


if __name__ == '__main__':
    x = solve_nonlinear_equation_with_bisection(1.0, 1.5, lambda x: x ** 3 - x - 1, abs, 0.005)
