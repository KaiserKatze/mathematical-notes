#!/bin/bash
# 这个脚本是在开发者本地工作站使用的

# 在本地重命名 texlive 输出的 PDF 文件
SOURCE_FILE="math.pdf"
OUTPUT_FILE="数学笔记.pdf"
if [[ ! -f "$OUTPUT_FILE" || $(stat --printf="%s" $SOURCE_FILE) -ge $(( $(stat --printf="%s" $OUTPUT_FILE) * 8 / 10 )) ]]; then
	cp "$SOURCE_FILE" "$OUTPUT_FILE" &>/dev/null && echo "[INFO] 已生成最新版'数学笔记.pdf'文件." || echo "[ERROR] 生成最新版'数学笔记.pdf'失败！"
fi
