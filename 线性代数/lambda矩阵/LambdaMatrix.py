#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Union, List, Tuple, Iterable, Any
from fractions import Fraction as fraction

# 基本数值类型联合
Number = int | fraction | float | complex
CoefficientContinuousType = List[Number]
CoefficientChunk = Tuple[int, Number | CoefficientContinuousType]
CoefficientType = str | CoefficientContinuousType | List[CoefficientChunk]

# ------------------------------------------------------------
# Polynomial 类
# ------------------------------------------------------------
class Polynomial:
    """
    多项式类。
    coefficients: 支持三种输入：
        - 字符串，例如 "3x^2-2x+1"
        - 连续系数列表 [a0, a1, a2, ...]
        - 分块列表 [(start, coef_or_list), ...]
    dtype: 用于字符串解析与构造时的数域类型（例如 fractions.Fraction）
    """

    def __init__(self, coefficients: CoefficientType, dtype=complex) -> None:
        """
        初始化多项式对象，内部用 self._coeffs 存储系数（从 0 次到最高次）。
        dtype 用于把解析出的常数转换为目标数域类型。
        """
        self.dtype = dtype  # 保存 dtype 到实例

        # 辅助：判断是否为允许的数字类型
        def is_number(x):
            return isinstance(x, Number)

        # assign_degree: 把某个次数的系数写入 assigned（禁止重复赋值）
        def assign_degree(d: int, val):
            if d < 0 or not isinstance(d, int):
                raise TypeError(f"degree must be non-negative int (got {d!r})")
            if not is_number(val):
                raise TypeError("coefficient must be a number")
            if d in assigned:
                raise ValueError(f"coefficient for degree {d} assigned more than once")
            # 强制转换为当前 dtype（若 dtype 是 fraction，会把整数转换为 fraction）
            try:
                assigned[d] = dtype(val)
            except Exception:
                # 如果无法直接 dtype(val)，尝试使用 float 再转换（容错）
                assigned[d] = dtype(float(val))

        # process_chunk: 处理 (start, coef_or_list)
        def process_chunk(start: int, coef_or_list):
            if is_number(coef_or_list):
                assign_degree(start, coef_or_list)
            else:
                if not isinstance(coef_or_list, Iterable):
                    raise TypeError("continuous coefficients must be iterable")
                idx = start
                for c in coef_or_list:
                    if not is_number(c):
                        raise TypeError("continuous coefficients must contain numbers")
                    assign_degree(idx, c)
                    idx += 1

        # parse_string: 把表达式字符串解析到 assigned 中
        def parse_string(expr: str):
            # 将解析到的数字/系数转换为指定 dtype
            def to_dtype_from_str(s: str):
                s = s.strip()
                if dtype is fraction:
                    return fraction(s)
                if dtype is complex:
                    return complex(s)
                if dtype is float:
                    return float(s)
                if dtype is int:
                    try:
                        return int(s)
                    except Exception:
                        return int(float(s))
                try:
                    return dtype(s)
                except Exception:
                    return dtype(float(s))

            s = expr.replace(" ", "")
            if s == "":
                raise ValueError("empty string")

            if s[0] not in "+-":
                s = "+" + s

            import re
            token_re = re.compile(r'([+-])([^+-]+)')

            for sign, body in token_re.findall(s):
                coef_sign = -1 if sign == "-" else 1

                # 常数项
                if "x" not in body:
                    coef = to_dtype_from_str(body)
                    assign_degree(0, coef_sign * coef)
                    continue

                # 含 x
                if body == "x":
                    coef = to_dtype_from_str("1")
                    deg = 1
                elif body.startswith("x^"):
                    coef = to_dtype_from_str("1")
                    deg = int(body[2:])
                elif body.startswith("x"):
                    coef = to_dtype_from_str("1")
                    deg = 1
                else:
                    num, _, rest = body.partition("x")
                    if num == "" or num == "+" or num == "-":
                        coef = to_dtype_from_str("1")
                    else:
                        coef = to_dtype_from_str(num)
                    if rest.startswith("^"):
                        deg = int(rest[1:])
                    else:
                        deg = 1

                assign_degree(deg, coef_sign * coef)

        # 主体逻辑：解析 coefficients
        assigned: dict[int, Number] = {}

        if isinstance(coefficients, str):
            parse_string(coefficients)
        elif isinstance(coefficients, list) and all(isinstance(x, Number) for x in coefficients):
            for i, c in enumerate(coefficients):
                assign_degree(i, c)
        elif isinstance(coefficients, list):
            all_chunks = True
            for e in coefficients:
                if not (isinstance(e, tuple) and len(e) == 2 and isinstance(e[0], int)):
                    all_chunks = False
                    break
            if all_chunks:
                for start, coef_or_list in coefficients:
                    process_chunk(start, coef_or_list)
            else:
                raise TypeError("invalid coefficient list format")
        else:
            raise TypeError("coefficients must be string or list")

        # 填充 self._coeffs，并裁掉末尾多余的零
        if not assigned:
            self._coeffs = [dtype(0) if dtype is not complex else 0]  # 留下零多项式
        else:
            max_deg = max(assigned)
            coeffs = [dtype(0) if dtype is not complex else 0] * (max_deg + 1)
            for d, v in assigned.items():
                coeffs[d] = v
            while len(coeffs) > 1 and coeffs[-1] == 0:
                coeffs.pop()
            self._coeffs = coeffs

    # -------------------------
    # 辅助静态/实例方法
    # -------------------------
    @staticmethod
    def _trim(coeffs: List[Number]) -> List[Number]:
        """去掉尾部多余的零（保留零多项式为 [0]）。"""
        if not coeffs:
            return [0]
        while len(coeffs) > 1 and coeffs[-1] == 0:
            coeffs.pop()
        return coeffs

    def _coerce_to_poly(self, other: Any) -> 'Polynomial':
        """
        将 other 升格为 Polynomial：
          - 如果 other 是 Polynomial，直接返回；
          - 如果 other 是数值，则返回常数多项式，使用当前实例的 dtype；
          - 否则返回 None。
        """
        if isinstance(other, Polynomial):
            return other
        if isinstance(other, (int, float, complex, fraction)):
            return Polynomial([other], dtype=self.dtype)
        return None

    # -------------------------
    # 基本属性与表示
    # -------------------------
    def coeffs(self) -> List[Number]:
        """返回系数的只读副本（从 0 次到最高次）。"""
        return list(self._coeffs)

    def degree(self) -> int:
        """返回次数（零多项式的次数为 0）。"""
        return len(self._coeffs) - 1

    def __repr__(self) -> str:
        """调试友好的表示，展示内部系数列表。"""
        return f"Polynomial({self._coeffs!r})"

    def __str__(self) -> str:
        """较为可读的字符串表示（从高次到低次）。"""
        terms = []
        for i, a in enumerate(self._coeffs):
            if a == 0:
                continue
            if i == 0:
                terms.append(f"{a}")
            elif i == 1:
                if a == 1:
                    terms.append('x')
                else:
                    terms.append(f"{a}*x")
            else:
                if a == 1:
                    terms.append(f'x^{i}')
                else:
                    terms.append(f"{a}*x^{i}")
        if not terms:
            return "0"
        return " + ".join(reversed(terms))

    # -------------------------
    # 评估、加减乘除、求导、因式分解
    # -------------------------
    def __call__(self, x: Number) -> Number:
        """用 Horner 法评估多项式在 x 处的值。"""
        res: Number = 0
        for a in reversed(self._coeffs):
            res = res * x + a
        return res

    def __add__(self, other: Any) -> 'Polynomial':
        """加法（保持 dtype 为 self.dtype）。"""
        poly = self._coerce_to_poly(other)
        if poly is None:
            return NotImplemented
        n = max(len(self._coeffs), len(poly._coeffs))
        a = self._coeffs + [0] * (n - len(self._coeffs))
        b = poly._coeffs + [0] * (n - len(poly._coeffs))
        res = [a_i + b_i for a_i, b_i in zip(a, b)]
        return Polynomial(Polynomial._trim(res), dtype=self.dtype)

    def __radd__(self, other: Any) -> 'Polynomial':
        return self.__add__(other)

    def __sub__(self, other: Any) -> 'Polynomial':
        """减法（保持 dtype）。"""
        poly = self._coerce_to_poly(other)
        if poly is None:
            return NotImplemented
        n = max(len(self._coeffs), len(poly._coeffs))
        a = self._coeffs + [0] * (n - len(self._coeffs))
        b = poly._coeffs + [0] * (n - len(poly._coeffs))
        res = [a_i - b_i for a_i, b_i in zip(a, b)]
        return Polynomial(Polynomial._trim(res), dtype=self.dtype)

    def __rsub__(self, other: Any) -> 'Polynomial':
        poly = self._coerce_to_poly(other)
        if poly is None:
            return NotImplemented
        return poly.__sub__(self)

    def __mul__(self, other: Any) -> 'Polynomial':
        """多项式乘法或数乘（卷积实现）。"""
        if isinstance(other, (int, float, complex, fraction)):
            if other == 0:
                return Polynomial([0], dtype=self.dtype)
            return Polynomial([c * other for c in self._coeffs], dtype=self.dtype)
        if isinstance(other, Polynomial):
            deg_a = len(self._coeffs) - 1
            deg_b = len(other._coeffs) - 1
            res_len = deg_a + deg_b + 1
            res = [0] * res_len
            for i, ai in enumerate(self._coeffs):
                for j, bj in enumerate(other._coeffs):
                    res[i + j] += ai * bj
            # 结果的 dtype 采用 self.dtype（假设调用者希望保持该域）
            return Polynomial(Polynomial._trim(res), dtype=self.dtype)
        return NotImplemented

    def __rmul__(self, other: Any) -> 'Polynomial':
        return self.__mul__(other)

    def __neg__(self) -> 'Polynomial':
        return Polynomial([-c for c in self._coeffs], dtype=self.dtype)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Polynomial):
            return False
        return self._coeffs == other._coeffs

    def __divmod__(self, other: Any) -> tuple['Polynomial', 'Polynomial']:
        """带余除法：返回 (quotient, remainder)。"""
        if isinstance(other, (int, float, complex, fraction)):
            other = Polynomial([other], dtype=self.dtype)
        if not isinstance(other, Polynomial):
            return NotImplemented
        if all(c == 0 for c in other._coeffs):
            raise ZeroDivisionError("polynomial division by zero")

        a = list(self._coeffs)[:]
        b = other._coeffs[:]
        deg_a = len(a) - 1
        deg_b = len(b) - 1

        if deg_a < deg_b:
            return Polynomial([0], dtype=self.dtype), Polynomial(Polynomial._trim(a), dtype=self.dtype)

        q_len = deg_a - deg_b + 1
        q = [0] * q_len
        r = a[:]
        lead_b = b[-1]
        for k in range(q_len - 1, -1, -1):
            idx = deg_b + k
            coeff_at_idx = r[idx] if idx < len(r) else 0
            factor = coeff_at_idx / lead_b
            q[k] = factor
            for j, bj in enumerate(b):
                r[j + k] = r[j + k] - factor * bj
        r = r[:deg_b] if deg_b >= 0 else [0]
        r = Polynomial._trim(r)
        q = Polynomial._trim(q)
        return Polynomial(q, dtype=self.dtype), Polynomial(r, dtype=self.dtype)

    def __truediv__(self, other: Any) -> 'Polynomial':
        """除法（仅当除尽时返回商，否则抛出 ArithmeticError）"""
        div_result = self.__divmod__(other)
        if div_result is NotImplemented:
            return NotImplemented
        q, r = div_result
        if any(c != 0 for c in r._coeffs):
            raise ArithmeticError("polynomial division not exact")
        return q

    def __floordiv__(self, other: Any) -> 'Polynomial':
        """整除（商），要求除尽，否则抛出 ArithmeticError。"""
        return self.__truediv__(other)

    def derivation(self) -> 'Polynomial':
        """返回一阶导数，多项式域与 self.dtype 保持一致。"""
        if len(self._coeffs) <= 1:
            return Polynomial([0], dtype=self.dtype)
        deriv = []
        for i in range(1, len(self._coeffs)):
            deriv.append(self._coeffs[i] * i)
        return Polynomial(Polynomial._trim(deriv), dtype=self.dtype)

    def factorize(self) -> list['Polynomial']:
        """
        简单因式分解，仅尝试系数为整数 / Fraction 的情形用有理根定理剥离线性因子。
        返回的因子尽量为首一（monic）。
        """
        # 若包含 float 或 complex，不尝试
        if any(isinstance(c, float) or isinstance(c, complex) for c in self._coeffs):
            return [self]

        # 将系数转换为 fraction 以便使用有理根定理
        coeffs_frac = [fraction(c) if not isinstance(c, fraction) else c for c in self._coeffs]
        factors: list[Polynomial] = []
        remainder_poly = Polynomial(coeffs_frac, dtype=fraction)

        # 剥离 x 因子（若常数项为 0）
        while len(remainder_poly._coeffs) > 1 and remainder_poly._coeffs[0] == 0:
            factors.append(Polynomial([0, 1], dtype=fraction))
            new_coeffs = remainder_poly._coeffs[1:]
            remainder_poly = Polynomial(Polynomial._trim(new_coeffs), dtype=fraction)

        if remainder_poly.degree() <= 0:
            if remainder_poly.degree() == 0 and remainder_poly._coeffs != [1]:
                factors.append(remainder_poly)
            return factors if factors else [remainder_poly]

        from math import gcd
        def lcm(a: int, b: int) -> int:
            return a // gcd(a, b) * b

        denoms = [c.denominator for c in coeffs_frac]
        L = 1
        for d in denoms:
            L = lcm(L, d)
        int_coeffs = [int((c * L).numerator) for c in coeffs_frac]
        A = int_coeffs[-1]
        C = int_coeffs[0]

        def divisors(n: int) -> list[int]:
            n = abs(n)
            if n == 0:
                return [0]
            divs = []
            i = 1
            while i * i <= n:
                if n % i == 0:
                    divs.append(i)
                    if i != n // i:
                        divs.append(n // i)
                i += 1
            divs_all = divs + [-d for d in divs]
            return divs_all

        # 主循环：逐步查找并剥离有理根
        while True:
            found_root = None
            coeffs_frac_cur = [fraction(c) if not isinstance(c, fraction) else c for c in remainder_poly._coeffs]
            denoms = [c.denominator for c in coeffs_frac_cur]
            L = 1
            for d in denoms:
                L = lcm(L, d)
            int_coeffs = [int((c * L).numerator) for c in coeffs_frac_cur]
            A = int_coeffs[-1]
            C = int_coeffs[0]
            possible_p = divisors(C)
            possible_q = divisors(A) if A != 0 else [1]
            candidates = set()
            for p in possible_p:
                for q in possible_q:
                    if q == 0:
                        continue
                    candidates.add(fraction(p, q))
            for cand in sorted(candidates, key=lambda x: (abs(x.numerator) / (x.denominator if x.denominator != 0 else 1), x)):
                val = remainder_poly(cand)
                if val == 0:
                    found_root = cand
                    break
            if found_root is None:
                break
            linear = Polynomial([-found_root, fraction(1)], dtype=fraction)
            qpoly, rpoly = divmod(remainder_poly, linear)
            if any(c != 0 for c in rpoly._coeffs):
                break
            # linear 已经是首一
            factors.append(linear)
            remainder_poly = qpoly
            if remainder_poly.degree() <= 1:
                break

        # 归一化剩余多项式为首一并加入
        if remainder_poly.degree() >= 1:
            lc = remainder_poly._coeffs[-1]
            if lc != 1 and lc != 0:
                coeffs_norm = [c / lc for c in remainder_poly._coeffs]
                remainder_poly = Polynomial(Polynomial._trim(coeffs_norm), dtype=fraction)
            factors.append(remainder_poly)
        elif remainder_poly.degree() == 0 and remainder_poly._coeffs != [1]:
            factors.append(remainder_poly)

        return factors if factors else [self]

    @classmethod
    def gcd(cls, *args):
        """
        计算若干多项式的首一最大公因式（monic）。
        若没有参数，返回 0（约定）。
        """
        if len(args) == 0:
            return Polynomial([0], dtype=complex)

        # 将输入都转换为 Polynomial，尽量保留 fraction 信息
        polys = []
        for p in args:
            if isinstance(p, Polynomial):
                polys.append(p)
            elif isinstance(p, (int, float, complex, fraction)):
                chosen_dtype = fraction if isinstance(p, fraction) else complex
                polys.append(Polynomial([p], dtype=chosen_dtype))
            else:
                raise TypeError("gcd expects Polynomial or numeric arguments")

        def is_zero(poly: Polynomial) -> bool:
            return all(c == 0 for c in poly._coeffs)

        def _make_monic(p: Polynomial) -> Polynomial:
            if is_zero(p):
                return Polynomial([0], dtype=complex)
            lc = p._coeffs[-1]
            if lc == 1:
                return p
            coeffs = [c / lc for c in p._coeffs]
            use_frac = any(isinstance(c, fraction) for c in coeffs)
            return Polynomial(Polynomial._trim(coeffs), dtype=(fraction if use_frac else complex))

        def poly_gcd(a: Polynomial, b: Polynomial) -> Polynomial:
            A = a
            B = b
            if is_zero(A):
                return _make_monic(B)
            if is_zero(B):
                return _make_monic(A)
            while not is_zero(B):
                _, r = divmod(A, B)
                A, B = B, r
            return _make_monic(A)

        current = polys[0]
        for poly in polys[1:]:
            current = poly_gcd(current, poly)
            if current.degree() == 0 and current._coeffs == [1]:
                return current
        return _make_monic(current)

    @classmethod
    def lcm(cls, *args):
        """
        计算若干多项式的首一最小公倍式（monic）。
        采用 pairwise 公式 lcm(a,b) = monic((a*b)/gcd(a,b)).
        """
        if len(args) == 0:
            return Polynomial([1], dtype=complex)

        polys = []
        for p in args:
            if isinstance(p, Polynomial):
                polys.append(p)
            elif isinstance(p, (int, float, complex, fraction)):
                chosen_dtype = fraction if isinstance(p, fraction) else complex
                polys.append(Polynomial([p], dtype=chosen_dtype))
            else:
                raise TypeError("lcm expects Polynomial or numeric arguments")

        def is_zero(poly: Polynomial) -> bool:
            return all(c == 0 for c in poly._coeffs)

        def _make_monic(p: Polynomial) -> Polynomial:
            if is_zero(p):
                return Polynomial([0], dtype=complex)
            lc = p._coeffs[-1]
            if lc == 1:
                return p
            coeffs = [c / lc for c in p._coeffs]
            use_frac = any(isinstance(c, fraction) for c in coeffs)
            return Polynomial(Polynomial._trim(coeffs), dtype=(fraction if use_frac else complex))

        def pair_lcm(a: Polynomial, b: Polynomial) -> Polynomial:
            if is_zero(a) or is_zero(b):
                return Polynomial([0], dtype=complex)
            g = cls.gcd(a, b)
            prod = a * b
            q, r = divmod(prod, g)
            if any(c != 0 for c in r._coeffs):
                raise ArithmeticError("non-exact division when computing lcm")
            return _make_monic(q)

        current = polys[0]
        for poly in polys[1:]:
            current = pair_lcm(current, poly)
        return _make_monic(current)

# ------------------------------------------------------------
# PolynomialMatrix 类
# ------------------------------------------------------------
MatrixType1 = dict[tuple[int, int], Polynomial]
MatrixType2 = list[list[Polynomial]]
MatrixType = MatrixType1 | MatrixType2

class PolynomialMatrix:
    """
    多项式环上的矩阵类。
    支持输入为稀疏字典 {(i,j): val} 或 行主序嵌套列表 [[...],[...]]。
    内部统一将元素转换为 Polynomial 并存为二维列表 self._data。
    """

    def __init__(self, data: MatrixType, dtype=complex):
        """构造函数：归一化输入到 self._data（row-major list of list）。"""
        self.dtype = dtype

        def to_poly(x):
            """把单个条目转换为 Polynomial（支持 Polynomial、Number、str）。"""
            if isinstance(x, Polynomial):
                return x
            if isinstance(x, Number):
                return Polynomial([x], dtype=dtype)
            if isinstance(x, str):
                return Polynomial(x, dtype=dtype)
            raise TypeError(f"matrix elements must be Polynomial or numeric or str, got {type(x)}")

        if isinstance(data, dict):
            if not data:
                self._rows = 0
                self._cols = 0
                self._data = []
                return
            max_i = max(i for (i, j) in data.keys())
            max_j = max(j for (i, j) in data.keys())
            rows = max_i + 1
            cols = max_j + 1
            mat = [[Polynomial([0], dtype=dtype) for _ in range(cols)] for _ in range(rows)]
            for (i, j), v in data.items():
                if not (isinstance(i, int) and isinstance(j, int) and i >= 0 and j >= 0):
                    raise TypeError("dictionary keys must be non-negative integer index pairs")
                mat[i][j] = to_poly(v)
            self._rows = rows
            self._cols = cols
            self._data = mat
        elif isinstance(data, list):
            if not data:
                self._rows = 0
                self._cols = 0
                self._data = []
                return
            if any(not isinstance(r, list) for r in data):
                raise TypeError('Nested type not list')
            row_lens = [len(r) for r in data]
            if len(set(row_lens)) != 1:
                raise TypeError("MatrixType2 must be a rectangular list of lists")
            rows = len(data)
            cols = row_lens[0]
            mat = [[to_poly(data[i][j]) for j in range(cols)] for i in range(rows)]
            self._rows = rows
            self._cols = cols
            self._data = mat
        else:
            raise TypeError("data must be dict[(i,j)->val] or list[list[val]]")

    @property
    def shape(self):
        """返回 (rows, cols)。"""
        return (self._rows, self._cols)

    def __add__(self, other: Any):
        """矩阵加法（形状一致）。"""
        if not isinstance(other, PolynomialMatrix):
            return NotImplemented
        if self.shape != other.shape:
            raise ValueError("matrix shapes do not match for addition")
        rows, cols = self.shape
        res = [[self._data[i][j] + other._data[i][j] for j in range(cols)] for i in range(rows)]
        return PolynomialMatrix(res, dtype=self.dtype)

    def __radd__(self, other: Any):
        return self.__add__(other)

    def __mul__(self, other: Any):
        """标量乘法（逐元素）或矩阵乘法。"""
        if isinstance(other, (int, float, complex, fraction, Polynomial)):
            if isinstance(other, Polynomial):
                scalar = other
            else:
                scalar = Polynomial([other], dtype=self.dtype)
            rows, cols = self.shape
            res = [[scalar * self._data[i][j] for j in range(cols)] for i in range(rows)]
            return PolynomialMatrix(res, dtype=self.dtype)
        if isinstance(other, PolynomialMatrix):
            a_rows, a_cols = self.shape
            b_rows, b_cols = other.shape
            if a_cols != b_rows:
                raise ValueError("matrix shapes not aligned for multiplication")
            res = [[Polynomial([0], dtype=self.dtype) for _ in range(b_cols)] for _ in range(a_rows)]
            for i in range(a_rows):
                for j in range(b_cols):
                    acc = Polynomial([0], dtype=self.dtype)
                    for k in range(a_cols):
                        acc = acc + (self._data[i][k] * other._data[k][j])
                    res[i][j] = acc
            return PolynomialMatrix(res, dtype=self.dtype)
        return NotImplemented

    def __rmul__(self, other: Any):
        if isinstance(other, (int, float, complex, fraction, Polynomial)):
            return self.__mul__(other)
        return NotImplemented

    def __str__(self):
        """矩阵的可读字符串表示，每行元素以制表符分隔。"""
        if self._rows == 0 or self._cols == 0:
            return "[]"
        row_strs = []
        for i in range(self._rows):
            elems = []
            for j in range(self._cols):
                elems.append(str(self._data[i][j]))
            row_strs.append("[ " + "\t".join(elems) + " ]")
        return "\n".join(row_strs)

    def submatrix(self, row_indexes: list[int], column_indexes: list[int]):
        """返回由给定行索引与列索引交叉得到的子矩阵。"""
        if any((ri < 0 or ri >= self._rows) for ri in row_indexes):
            raise IndexError("row index out of range")
        if any((cj < 0 or cj >= self._cols) for cj in column_indexes):
            raise IndexError("column index out of range")
        mat = [[self._data[ri][cj] for cj in column_indexes] for ri in row_indexes]
        return PolynomialMatrix(mat, dtype=self.dtype)

    def algebraic_cofactor(self, i: int, j: int) -> Polynomial:
        """
        返回 (i,j) 元素的代数余子式 A_{ij} = (-1)^{i+j} * det(M_{ij})。
        索引以 0 为基准。
        """
        if i < 0 or i >= self._rows:
            raise IndexError("row index out of range")
        if j < 0 or j >= self._cols:
            raise IndexError("column index out of range")
        row_idxs = [r for r in range(self._rows) if r != i]
        col_idxs = [c for c in range(self._cols) if c != j]
        sub = self.submatrix(row_idxs, col_idxs)
        det_sub = sub.determinant()
        sign = -1 if ((i + j) % 2) else 1
        return det_sub if sign == 1 else -det_sub

    def determinant(self) -> Number:
        """
        计算方阵的行列式（返回 Polynomial）。
        - n==0: 返回 1
        - n==1: 返回唯一元素
        - n<=7: 使用 Leibniz 展开
        - n>7: 使用 Bareiss 算法（fraction-free）
        """
        if self._rows != self._cols:
            raise TypeError("determinant is defined only for square matrices")
        n = self._rows
        if n == 0:
            return Polynomial([1], dtype=self.dtype)
        if n == 1:
            return self._data[0][0]
        if n <= 7:
            from itertools import permutations
            det = Polynomial([0], dtype=self.dtype)
            sign = lambda perm: 1 if sum(1 for a in range(len(perm)) for b in range(a+1, len(perm)) if perm[a] > perm[b]) % 2 == 0 else -1
            cols = list(range(n))
            for perm in permutations(cols):
                prod = Polynomial([1], dtype=self.dtype)
                for i, j in enumerate(perm):
                    prod = prod * self._data[i][j]
                s = sign(perm)
                det = det + prod if s == 1 else det - prod
            return det
        # Bareiss algorithm (fraction-free) for exact arithmetic
        A = [[self._data[i][j] for j in range(n)] for i in range(n)]
        sign_mul = 1
        for k in range(0, n - 1):
            # 如果主对角为零，尝试交换行
            if all(c == 0 for c in A[k][k]._coeffs):
                swap_row = None
                for r in range(k + 1, n):
                    if not all(c == 0 for c in A[r][k]._coeffs):
                        swap_row = r
                        break
                if swap_row is None:
                    return Polynomial([0], dtype=self.dtype)
                A[k], A[swap_row] = A[swap_row], A[k]
                sign_mul *= -1
            D = Polynomial([1], dtype=self.dtype) if k == 0 else A[k - 1][k - 1]
            Akk = A[k][k]
            for i in range(k + 1, n):
                for j in range(k + 1, n):
                    numerator = A[i][j] * Akk - A[i][k] * A[k][j]
                    # Bareiss 的性质保证 numerator / D 是整除的（在适当环中）
                    A[i][j] = numerator / D
            for i in range(k + 1, n):
                A[i][k] = Polynomial([0], dtype=self.dtype)
        det = A[n - 1][n - 1]
        if sign_mul == -1:
            det = -det
        return det

    def ordinal_principal_minor(self, k: int) -> Number:
        """返回左上 k x k 子矩阵的行列式（k>=0，若 k==0 返回 1）。"""
        if k < 0 or k >= min(self._rows, self._cols):
            raise ValueError("k out of valid range")
        index_range = list(range(k + 1))
        sub = self.submatrix(index_range, index_range)
        return sub.determinant()

    def determinant_divisor(self, k: int) -> Number:
        """
        返回矩阵的 k 阶行列式因子 d_k（即所有 k 阶子式的首一最大公因式）。
        """
        from itertools import combinations
        if k < 0:
            raise ValueError("k must be non-negative")
        rows, cols = self._rows, self._cols
        if k == 0:
            return Polynomial([1], dtype=self.dtype)
        if k > min(rows, cols):
            raise ValueError("k is larger than matrix dimensions")
        minors: list[Polynomial] = []
        row_indices = range(rows)
        col_indices = range(cols)
        for row_idx_tuple in combinations(row_indices, k):
            for col_idx_tuple in combinations(col_indices, k):
                sub = self.submatrix(list(row_idx_tuple), list(col_idx_tuple))
                det = sub.determinant()
                minors.append(det)
        # 如果所有子式都为零，则返回零多项式
        if all(isinstance(m, Polynomial) and all(c == 0 for c in m._coeffs) for m in minors):
            return Polynomial([0], dtype=self.dtype)
        # 返回这些子式的首一最大公因式
        return Polynomial.gcd(*minors)

    def rank(self) -> int:
        """
        返回矩阵的秩（最大阶的非零子式的阶数）。
        通过从 min(rows,cols) 向下扫描 determinant_divisor 来判断是否存在非零子式。
        """
        rows, cols = self._rows, self._cols
        max_k = min(rows, cols)
        for k in range(max_k, 0, -1):
            try:
                dk = self.determinant_divisor(k)
            except ValueError:
                continue
            # 判断 dk 是否为零多项式
            if not (isinstance(dk, Polynomial) and all(c == 0 for c in dk._coeffs)):
                return k
        return 0

    def invariant_factor(self, k: int) -> Polynomial:
        """
        返回第 k 个不变量因子（基于行列式因子 d_k），以多项式形式给出。
        定义：f_k = d_k / d_{k-1}，并将结果首一化（monic）。
        """
        dk = self.determinant_divisor(k)
        if isinstance(dk, Polynomial) and all(c == 0 for c in dk._coeffs):
            return Polynomial([0], dtype=self.dtype)
        if k == 0:
            return dk
        dkm1 = self.determinant_divisor(k - 1)
        if isinstance(dkm1, Polynomial) and all(c == 0 for c in dkm1._coeffs):
            # d_{k-1} = 0，返回 dk
            return dk
        # 执行整除并标准化为首一
        q, r = divmod(dk, dkm1)
        if any(c != 0 for c in r._coeffs):
            raise ArithmeticError("invariant factor division not exact")
        # 将 q 标准化为首一
        lc = q._coeffs[-1]
        if lc != 1 and lc != 0:
            coeffs_norm = [c / lc for c in q._coeffs]
            return Polynomial(Polynomial._trim(coeffs_norm), dtype=(fraction if any(isinstance(c, fraction) for c in coeffs_norm) else complex))
        return q

# ------------------------------------------------------------
# 测试与演示
# ------------------------------------------------------------
if __name__ == '__main__':
    # 测试用例：Fraction 系数
    c = fraction(30)
    a_0 = fraction(100)
    a_1 = fraction(-50)
    a_2 = fraction(31)
    a_3 = fraction(231)
    a_4 = fraction(59)

    p1 = Polynomial([c], dtype=fraction)
    print(f'p1=\n\t{str(p1)}')
    p2 = Polynomial([0, 1], dtype=fraction)
    print(f'p2=\n\t{str(p2)}')
    p3 = Polynomial([a_0, a_1, a_2, a_3], dtype=fraction)
    print(f'p3=\n\t{str(p3)}')
    p4 = Polynomial([a_0, a_1, 0, a_3, a_4], dtype=fraction)
    print(f'p4=\n\t{str(p4)}')
    p5 = Polynomial([(0, a_0), (1, a_1), (3, a_3), (4, a_4)], dtype=fraction)
    print(f'p5=\n\t{str(p5)}')
    p6 = Polynomial([(0, [a_0, a_1]), (3, [a_3, a_4])], dtype=fraction)
    print(f'p6=\n\t{str(p6)}')

    print(f'deg p1=\n\t{str(p1.degree())}')
    print(f'deg p2=\n\t{str(p2.degree())}')
    print(f'deg p3=\n\t{str(p3.degree())}')

    print(f'p1+p2=\n\t{str(p1+p2)}')
    print(f'p5-p6=\n\t{str(p5-p6)}')
    print(f'-p3=\n\t{str(-p3)}')
    print(f'p2*p5=\n\t{p2*p5}')

    print(f'D(p1)=\n\t{str(p1.derivation())}')
    print(f'D(p2)=\n\t{str(p2.derivation())}')
    print(f'D(p5)=\n\t{str(p5.derivation())}')

    d1, m1 = divmod(p3, p1 + p2)
    print(f'divmod(p3,p1+p2)=\n\t{str(d1)}, {str(m1)}')
    d1, m1 = divmod(p5, p1 + p2)
    print(f'divmod(p5,p1+p2)=\n\t{str(d1)}, {str(m1)}')

    p7 = Polynomial('3x+1', dtype=fraction) * Polynomial('x+1', dtype=fraction) * Polynomial('x^2+x+1', dtype=fraction)
    print(f'p7=\n\t{str(p7)}')
    p7fs = p7.factorize()
    for factor in p7fs:
        print(f'\t\t{str(factor)}')

    pmA = PolynomialMatrix([
        ['x-2', '0', '0'],
        ['-1', 'x-2', '0'],
        ['0', '-1', 'x-2'],
    ], dtype=fraction)
    print(f'pmA=\n\t{str(pmA).replace("\\n", "\\n\\t")}')
    print(f'pmA.rank() ->\n\t{pmA.rank()}')
    print(f'pmA.submatrix([0], [0]) ->\n\t{str(pmA.submatrix([0,],[0,]))}')
    print(f'pmA.algebraic_cofactor(0, 0) ->\n\t{str(pmA.algebraic_cofactor(0, 0))}')
    for k in range(3):
        print(f'pmA.ordinal_principal_minor({k}) ->\n\t{str(pmA.ordinal_principal_minor(k))}')
    for k in range(3):
        print(f'pmA.invariant_factor({k}) ->\n\t{str(pmA.invariant_factor(k))}')

    pmB = PolynomialMatrix([
        ['x+1', 2, -6],
        [1, 'x', -3],
        [1, 1, 'x-4'],
    ], dtype=fraction)
    print(f'pmB=\n\t{str(pmB).replace("\\n", "\\n\\t")}')
    for k in range(3):
        print(f'pmB.invariant_factor({k}) ->\n\t{str(pmB.invariant_factor(k))}')
