#!/usr/bin/env python
# -*- coding: utf-8 -*-

def solv_diff_eqn(fxy, x0, xn, h, y0, format: str = '.4f'):
    assert x0 < xn
    assert h > 0
    xy = [(x0, y0)]
    while True:
        _, y0 = xy[-1]
        x1 = x0 + h
        if x1 > xn + 0.5 * h:
            break
        y1 = y0 + h * fxy(x0, y0)
        xy.append((x1, y1))
        x0 = x1

    assert abs(xy[-1][0] - xn) < 0.5 * h, '求解区间不完整，请检查算法!'

    # print('原始数据:')
    # for x, y in xy:
    #     print(f'x = {x:{format}}, y = {y:{format}}')

    # print('='*10 + ' LaTeX 表达式 ' + '='*10)

    print('依次计算得：\\begin{align*}')
    for n, (x, y) in enumerate(xy[:-1]):
        sep = ', \\\\' if n + 2 < len(xy) else '.'
        print(
            f'    y_{{{n+1}}} &= y_{{{n}}} + h \\cdot f(x_{{{n}}},y_{{{n}}}) '
            f'= {y:{format}} + {h:{format}} \\cdot f({x:{format}},{y:{format}}) '
            # f'\\approx {(y + h * fxy(x, y)):{format}}{sep}'
            f'\\approx {xy[n+1][1]:{format}}{sep}'
        )
    print('\\end{align*}')

if __name__ == '__main__':
    # solv_diff_eqn(lambda x, y: y - 2.0 * x / y, 0.0, 1.0, 0.1, 1.0)
    solv_diff_eqn(
        lambda x, y: x * x + 100 * y * y,
        0.0,
        0.3,
        0.1,
        0.0,
    )
