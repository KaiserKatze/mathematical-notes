#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections.abc import Callable
import numpy as np


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


def solve_nonlinear_equation_with_Steffensen_method(x0, iter_fn, norm_fn, tol):
    print('使用[斯蒂芬森加速法]求解零点近似值 ...')
    xk = x0
    for i in range(1000):
        yk = iter_fn(xk)
        zk = iter_fn(yk)
        xk1 = xk - (yk - xk) ** 2 / (zk - 2 * yk + xk)
        # print(f'{yk=:.6e}')
        # print(f'{zk=:.6e}')
        # print(f'{xk1=:.6e}')
        print(f'第 {i} 轮算得近似零点 x ≈ {xk1:+.6e}.')
        if norm_fn(xk1 - xk) < tol:
            print(f'找到近似零点 x ≈ {xk1:+.6e}!')
            return xk1
        xk = xk1
    raise RuntimeError('已达到最大迭代次数!')


def solve_nonlinear_equation_with_Newton_method(x0: float, fn: Callable[[float], float], fn_derivative: Callable[[float], float], norm_fn: Callable[[float], float] = abs, xtol: float = 1e-8, max_nfev: int = 100):
    print('使用[牛顿法]求解零点近似值 ...')
    x = x0
    for i in range(max_nfev):
        delta = fn(x) / fn_derivative(x)
        x -= delta
        print(f'第 {i} 轮算得近似零点 x ≈ {x:+.6e}.')
        if norm_fn(delta) < xtol:
            print(f'找到近似零点 x ≈ {x:+.6e}!')
            return x
    raise RuntimeError('已达到最大迭代次数!')


def solve_nonlinear_equation_with_simplified_Newton_method(x0, fn, fn_derivative, norm_fn, xtol, max_nfev):
    print('使用[简化牛顿法]求解零点近似值 ...')
    x = x0
    fd = fn_derivative(x0)
    for i in range(max_nfev):
        delta = fn(x) / fd
        x -= delta
        print(f'第 {i} 轮算得近似零点 x ≈ {x:+.6e}.')
        if norm_fn(delta) < xtol:
            print(f'找到近似零点 x ≈ {x:+.6e}!')
            return x
    raise RuntimeError('已达到最大迭代次数!')


def solve_nonlinear_equation_with_downhill_Newton_method(x0, fn, fn_derivative, norm_fn, xtol, max_nfev):
    print('使用[牛顿下山法]求解零点近似值 ...')
    x = x0
    downhill_factor = 1.0
    for i in range(max_nfev):
        delta = downhill_factor * fn(x) / fn_derivative(x)
        x -= delta
        downhill_factor *= 0.5
        print(f'第 {i} 轮算得近似零点 x ≈ {x:+.6e}.')
        if norm_fn(delta) < xtol:
            print(f'找到近似零点 x ≈ {x:+.6e}!')
            return x
    raise RuntimeError('已达到最大迭代次数!')


if __name__ == '__main__':
    def test():
        solve_nonlinear_equation_with_Steffensen_method(
            1.5,
            lambda x: (1 + x ** 2) ** (1/3),
            abs,
            1e-5
        )

        solve_nonlinear_equation_with_Steffensen_method(
            1.5,
            lambda x: 1.0 / np.sqrt(x - 1),
            abs,
            1e-5
        )

        solve_nonlinear_equation_with_Newton_method(
            2.0,
            lambda x: x ** 3 - x ** 2 - 1,
            lambda x: 3 * x ** 2 - 2 * x,
            abs,
            1e-5
        )

    test()
