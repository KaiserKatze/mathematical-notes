2025年7月18日，遇到下面这道题目：

求极限
$
	\displaystyle
	\lim_{n\to\infty} \left( \sum_{k=1}^n \frac{n^2}{n^2 + k^2} - \frac{n \pi}{4} \right)
$.

朋友 `{d9dc8566-1754-4e62-9e8c-ef5d2a3b19bd}` 告诉我这道题需要用到“欧拉麦克劳林公式”.

虽然我在查阅了一些资料以后，觉得欧拉麦克劳林公式和面积原理非常相似，但是有的文档说这条公式是数值分析的内容，因此我决定把这道题作为数值分析部分的公式，暂存在这里.

```wolfram
Limit[Sum[n^2/(n^2 + k^2), {k, 1, n}] - (n \[Pi])/4, n -> Infinity]
```

下面是上述题目的部分解题步骤：
```latex
注意到\begin{align*}
	\lim_{n\to\infty} \sum_{k=1}^n \frac{n^2}{n^2 + k^2}
	&= \lim_{n\to\infty} \frac1n \sum_{k=1}^n \frac1{1 + (k/n)^2} \\
	&= \int_0^1 \frac{\dd{x}}{1 + x^2} \\
	&= \eval{\arctan x}_0^1
	= \frac\pi4.
\end{align*}
于是\begin{align*}
	\lim_{n\to\infty} \left( \sum_{k=1}^n \frac{n^2}{n^2 + k^2} - \frac{n \pi}{4} \right)
	&= \lim_{n\to\infty} n \left( \sum_{k=1}^n \frac{n}{n^2 + k^2} - \int_0^1 \frac{\dd{x}}{1 + x^2} \right) \\
	&= \frac{1-0}{2} (f(1) - f(0))
	= -\frac14.
		\tag{欧拉--麦克劳林公式}
\end{align*}
```
