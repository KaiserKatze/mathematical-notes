#!/usr/bin/env python
# -*- coding: utf-8 -*-

def solv_diff_eqn(fxy, x0, xn, h, y0):
    assert x0 < xn
    assert h > 0
    xy = [(x0, y0)]
    while True:
        x1 = x0 + h
        if x1 > xn + 0.5 * h:
            break
        yp = y0 + h * fxy(x0, y0)
        yc = y0 + h * fxy(x1, yp)
        y1 = 0.5 * (yp + yc)
        xy.append((x1, y1))
        x0 = x1
        y0 = y1

    assert abs(xy[-1][0] - xn) < 0.5 * h, '求解区间不完整，请检查算法!'

    # print('原始数据:')
    # for x, y in xy:
    #     print(f'x = {x:.6f}, y = {y:.6f}')

    # print('='*10 + ' LaTeX 表达式 ' + '='*10)


    print('依次计算得：\\begin{align*}')
    for n, (x, y) in enumerate(xy[:-1]):
        sep = ', \\\\' if n + 2 < len(xy) else '.'
        yp = y + h * fxy(x, y)
        yc = y + h * fxy(x+h, yp)
        print(
            f'    y_p &= y_{{{n}}} + h \\cdot f(x_{{{n}}},y_{{{n}}}) \\approx {yp:.4f}, \\\\ \n'
            f'    y_c &= y_{{{n}}} + h \\cdot f(x_{{{n+1}}},y_{{{n}}}) \\approx {yc:.4f}, \\\\ \n'
            f'    y_{{{n+1}}} &= 0.5 \\cdot ( y_p + y_c ) '
            f'= 0.5 \\cdot ({yp:.4f} + {yc:.4f}) '
            f'\\approx {xy[n+1][1]:.4f}{sep}'
        )
    print('\end{align*}')


if __name__ == '__main__':
    # solv_diff_eqn(lambda x, y: y - 2.0 * x / y, 0.0, 1.0, 0.1, 1.0)
    solv_diff_eqn(
        lambda x, y:
        x * x + x - y,
        0.0,
        0.5,
        0.1,
        0.0,
    )
