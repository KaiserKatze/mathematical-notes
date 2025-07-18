#!/bin/bash
# 这个脚本是在开发者本地工作站使用的

# 数据统计

find . -type f \( -name '*.tex' -o -name '*.sty' \) |\
	xargs cat | wc -lc|\
	awk '{print "LaTeX 代码共计：" $1 " 行，" $2 " 字节."}'
find . -type f -name '*.tex' | wc -l |\
	awk '{print ".tex 文件共计：" $1 " 个."}'
find . -type f -name '*.sty' | wc -l |\
	awk '{print ".sty 文件共计：" $1 " 个."}'

find . -type f -name "*.tex" -exec cat {} + |
	grep -oP '[\p{Han}]' |
	awk '{count[$0]++} END {for (char in count) print char, count[char]}' |
	sort -k2 -nr > word_count.txt
