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

error_log_handler = logging.StreamHandler()
error_log_handler.setLevel(logging.ERROR)
error_log_handler.setFormatter(logging.Formatter("\033[31m%(levelname)s %(message)s\033[0m"))
error_log_handler.addFilter(lambda record: record.levelno == logging.ERROR)

logger.addHandler(info_log_handler)
logger.addHandler(error_log_handler)


def find_all_tex_files():
    for dirpath, dirnames, filenames in os.walk('.'):
        if ".git" in dirpath:
            continue
        for filename in filenames:
            if filename.endswith(".tex"):
                yield os.path.join(dirpath, filename)


if __name__ == "__main__":
    is_tex_project_problematic = False
    for file in find_all_tex_files():
        with open(file, mode='r', encoding="utf-8") as fd:
            for line_num, line in enumerate(fd.readlines()):
                def error(msg):
                    logger.error("{}\n{} 第{}行：\n{}\n".format(msg, file, line_num, line))
                    global is_tex_project_problematic
                    is_tex_project_problematic = True
                if re.match(r"\s+\\cref\b", line):
                    error("\cref 命令前不应有空格！")
                if re.match(r"^\\cref\b", line):
                    error("\cref 命令前不应换行！")
                if re.match(r"\\labelcref\b", line):
                    if re.match(r" \\labelcref\b", line):
                        continue  # 已经添加过空格了，不必再加空格
                    if re.match(r"^\\labelcref\b", line):
                        continue  # 换行的情况下不必另外添加空格
                    error("\labelcref 命令前应添加空格！")
    if not is_tex_project_problematic:
        logger.info("检查完毕，没有任何错误！")
    else:
        logger.error("请注意检查你的文件！")