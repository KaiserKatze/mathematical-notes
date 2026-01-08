#!/usr/bin/env python
# -*- coding: utf-8 -*-

def gcd(a: int , b: int):
    """
    计算两个正整数的最大公约数

    :param a: 正整数
    :type a: int
    :param b: 正整数
    :type b: int
    """
    while True:
        if a < b:
            a, b = b, a
        elif a == b:
            return a
        a -= b


if __name__ == '__main__':
    print(f'{gcd(517, 893)=}')

    from math import gcd as math_gcd
    assert gcd(517, 893) == math_gcd(517, 893), f'{math_gcd(517, 893)=}'
