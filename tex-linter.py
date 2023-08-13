#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os
import re

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

info_log_handler = logging.StreamHandler()
info_log_handler.setLevel(logging.INFO)
info_log_handler.setFormatter(logging.Formatter("\033[32m%(levelname)s %(message)s\033[0m"))
info_log_handler.addFilter(lambda record: record.levelno == logging.INFO)
logger.addHandler(info_log_handler)

error_log_handler = logging.StreamHandler()
error_log_handler.setLevel(logging.ERROR)
error_log_handler.setFormatter(logging.Formatter("\033[31m%(levelname)s %(message)s\033[0m"))
error_log_handler.addFilter(lambda record: record.levelno == logging.ERROR)
logger.addHandler(error_log_handler)


def find_all_tex_files():
    for dirpath, dirnames, filenames in os.walk('.'):
        if ".git" in dirpath:
            continue
        for filename in filenames:
            if filename.endswith(".tex"):
                yield os.path.join(dirpath, filename)

# `\uff09` 是全角右圆括号 ）
# `\uff0c` 是全角逗号 ，
# `\uff1b` 是全角分号 ；
if __name__ == "__main__":
    is_tex_project_problematic = False
    error_counter = 0
    for file in find_all_tex_files():
        with open(file, mode='r', encoding="utf-8") as fd:
            prev_line = ""
            for line_num, line in enumerate(fd.readlines()):
                line_num += 1  # enumerate 函数给出的序号是从0开始的，行号是从1开始的，进行修正
                def error(msg):
                    logger.error("{}\n{} 第{}行：\n\t{}>>>\t{}".format(msg, file, line_num, prev_line, line))
                    global is_tex_project_problematic, error_counter
                    is_tex_project_problematic = True
                    error_counter += 1

                if re.search(r"\s+\\cref\b", line):
                    error("【0001】\cref 命令前不应有空格！")

                if re.search(r"^\\cref\b", line):
                    if re.search(r"%[^$]+$", prev_line):
                        continue  # 前一行末尾有注释，不算在 \cref 命令前换行了
                    if re.match(r"^\s*$", prev_line):
                        continue  # 前一行为空行，没关系
                    if re.search(r"\\(begin|end)\{[^\}]+\}$", prev_line) \
                        or re.search(r"\\\]$", prev_line):
                        continue  # 前一行是开始或结束环境的命令，没关系
                    if re.search(r"\\(part|chapter|(sub)*section)(\*)?", prev_line):
                        continue  # 前一行是章节命令，没关系
                    if re.search(r"\.$", prev_line):
                        continue  # 前一行最后一个字符是句号，没关系
                    if re.search(r"\uff0c$", prev_line):
                        continue  # 前一行最后一个字符是逗号，没关系
                    error("【0002】\cref 命令前不应换行！")

                if re.search(r"\\labelcref\b", line):
                    if re.search(r" \\labelcref\b", line):
                        continue  # 已经添加过空格了，不必再加空格
                    if re.search(r"^\\labelcref\b", line) \
                        and not re.search(r"%[^$]+$", prev_line):
                        continue  # 换行的情况下不必另外添加空格，且上一行末尾不是由`%`结束的
                    error("【0003】\labelcref 命令前应添加空格！")

                if re.search(r"\\cref\{[^\}]+\}\s+[\uff09\uff0c\uff1b]", line):
                    error("【0004】在 \cref 命令后若紧跟标点符号则不应另行添加空格！")

                if re.search(r"\uff09\s+\\\(", line):
                    error("【0005】在全角右圆括号与行内数学公式开头命令之间存在空格！")

                prev_line = line
    if not is_tex_project_problematic:
        logger.info("检查完毕，没有任何错误！")
    else:
        logger.error("共计发现{}条错误！请注意检查你的文件！".format(error_counter))
        exit(1)
