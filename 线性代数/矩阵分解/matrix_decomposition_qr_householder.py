#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @see: https://mmids-textbook.github.io/chap02_ls/04_qr/roch-mmids-ls-qr.html

import numpy as np
import numpy.linalg as LA


def gramschmidt(A):
    (n,m) = A.shape
    Q = np.zeros((n,m))
    R = np.zeros((m,m))
    for j in range(m):
        v = np.copy(A[:,j])
        for i in range(j):
            R[i,j] = np.dot(Q[:,i], A[:,j])
            v -= R[i,j]*Q[:,i]
        R[j,j] = LA.norm(v)
        Q[:,j] = v/R[j,j]
    return Q, R


def backsubs(R,b):
    m = b.shape[0]
    x = np.zeros(m)
    for i in reversed(range(m)):
        x[i] = (b[i] - np.dot(R[i,i+1:m],x[i+1:m]))/R[i,i]
    return x


def forwardsubs(L,b):
    m = b.shape[0]
    x = np.zeros(m)
    for i in range(m):
        x[i] = (b[i] - np.dot(L[i,0:i],x[0:i]))/L[i,i]
    return x


def ls_by_qr(A, b):
    # the QR approach to least squares
    Q, R = gramschmidt(A)
    return backsubs(R, Q.T @ b)


def householder(A, b):
    n, m = A.shape
    R = np.copy(A)
    Qtb = np.copy(b)
    for k in range(m):

        y = R[k:n,k]
        e1 = np.zeros(n-k)
        e1[0] = 1
        z = np.sign(y[0]) * LA.norm(y) * e1 + y
        z = z / LA.norm(z)

        R[k:n,k:m] = R[k:n,k:m] - 2 * np.outer(z, z) @ R[k:n,k:m]
        Qtb[k:n] = Qtb[k:n] - 2 * np.outer(z, z) @ Qtb[k:n]

    return R[0:m,0:m], Qtb[0:m]


if __name__ == '__main__':
    def test():
        A = np.array([
            -3, 1, -2,
            1, 1, 1,
            1, -1, 0,
            1, -1, 1
        ], dtype=np.float32).reshape((4, 3))
        b = np.array([1, 0, -2, 1], dtype=np.float32)
        R, Qtb = householder(A, b)
        print(f'{R=}')
        print(f'{Qtb=}')
        x = backsubs(R, Qtb)
        print(x)

    test()
