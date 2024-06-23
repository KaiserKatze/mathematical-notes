#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os
import re

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

info_log_handler = logging.StreamHandler()
info_log_handler.setLevel(logging.INFO)
info_log_handler.setFormatter(logging.Formatter("%(levelname)s %(message)s"))
info_log_handler.addFilter(lambda record: record.levelno == logging.INFO)
logger.addHandler(info_log_handler)

error_log_handler = logging.StreamHandler()
error_log_handler.setLevel(logging.ERROR)
error_log_handler.setFormatter(logging.Formatter("%(levelname)s %(message)s"))
error_log_handler.addFilter(lambda record: record.levelno == logging.ERROR)
logger.addHandler(error_log_handler)

is_tex_project_problematic = False
error_counter = 0
total_line_counter = 0

def error(msg, _file, _line_num, _prev_line, _line):
    logger.error("{}\n{} 第{}行：\n\t{}>>>\t{}".format(msg, _file, _line_num, _prev_line, _line))
    global is_tex_project_problematic
    global error_counter
    is_tex_project_problematic = True
    error_counter += 1

def find_all_tex_files():
    for dirpath, dirnames, filenames in os.walk('.'):
        if ".git" in dirpath:
            continue
        for filename in filenames:
            if filename.endswith(".tex"):
                yield os.path.join(dirpath, filename)

def scan_math_environments(_file):
    with open(_file, mode='r', encoding="utf-8") as fd:
        prev_line = ""
        lines = iter(fd.readlines())
        line_num = 0

        line_num_begin = 0
        line_begin = None
        line_num_end = 0
        line_end = None

        def report():
            if not (line_num_begin < line_num_end):
                return
            error("【0008】在数学公式环境中存在中文全角标点符号！\n"
                    "环境参数【起：{}，止：{}】\n"
                    "起 >>> {}\n"
                    "止 >>> {}".format(line_num_begin, line_num_end, line_begin, line_end),
                    file, line_num, prev_line, line)

        def check(fn_begin, fn_end, _line_num, _line):
            nonlocal line_num_begin
            nonlocal line_num_end
            nonlocal line_begin
            nonlocal line_end
            line_num_begin = 0
            line_begin = None
            line_num_end = 0
            line_end = None
            if fn_begin(_line):
                logger.debug("{} 第{}行：数学公式环境 开始 >>> {}".format(file, _line_num, line))
                line_num_begin = _line_num
                line_begin = _line
                for _line_ in lines:
                    _line_num += 1
                    logger.debug("正在扫描 {} 第{}行 >>> {}".format(file, _line_num, _line_))
                    if fn_end(_line_):
                        logger.debug("{} 第{}行：数学公式环境 关闭 >>> {}".format(file, _line_num, line))
                        line_num_end = _line_num
                        line_end = _line_
                        break
                    if re.search(r"[\uff09\uff0c\uff1b]", _line_):
                        report()
                return True

        for line in lines:
            line_num += 1
            logger.debug("正在扫描 {} 第{}行 >>> {}".format(file, line_num, line))
            check(lambda l: re.search(r"\\\[", l),
                    lambda l: re.search(r"\\\]", l),
                    line_num, line)
            for env_name in [
                "align",
                "align*",
                "gather",
                "gather*",
            ]:
                if check(lambda l: re.search(r"\\begin\{"+env_name+r"\}", l),
                            lambda l: re.search(r"\\end\{"+env_name+r"\}", l),
                            line_num, line):
                    break  # 退出循环
            prev_line = line


# `\uff09` 是全角右圆括号 ）
# `\uff0c` 是全角逗号 ，
# `\uff1b` 是全角分号 ；
if __name__ == "__main__":
    pattern_env1 = re.compile(r'\\begin\{([^\}]+)\}')
    pattern_env2 = re.compile(r'\\end\{([^\}]+)\}')

    for file in find_all_tex_files():
        scan_math_environments(file)

        environment_counter = {}  # 对形如 `\begin{...}` 和 `\end{...}` 的控制序列计数

        with open(file, mode='r', encoding="utf-8") as fd:
            prev_line = ""
            for line_num, line in enumerate(fd.readlines()):

                for token in re.findall(pattern_env1, line):
                    environment_counter[token] = environment_counter.get(token, 0) + 1
                for token in re.findall(pattern_env2, line):
                    environment_counter[token] = environment_counter.get(token, 0) - 1

                line_num += 1  # enumerate 函数给出的序号是从0开始的，行号是从1开始的，进行修正
                total_line_counter += 1

                if re.search(r"\s+\\cref\b", line):
                    error("【0001】\cref 命令前不应有空格！", file, line_num, prev_line, line)

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
                    error("【0002】\cref 命令前不应换行！", file, line_num, prev_line, line)

                if re.search(r"\\labelcref\b", line):
                    if re.search(r" \\labelcref\b", line):
                        continue  # 已经添加过空格了，不必再加空格
                    if re.search(r"^\\labelcref\b", line) \
                        and not re.search(r"%[^$]+$", prev_line):
                        continue  # 换行的情况下不必另外添加空格，且上一行末尾不是由`%`结束的
                    error("【0003】\labelcref 命令前应添加空格！", file, line_num, prev_line, line)

                if re.search(r"\\cref\{[^\}]+\}\s+[\uff09\uff0c\uff1b]", line):
                    error("【0004】在 \cref 命令后若紧跟标点符号则不应另行添加空格！", file, line_num, prev_line, line)

                if re.search(r"\uff09\s+\\\(", line):
                    error("【0005】在全角右圆括号与行内数学公式开头命令之间存在空格！", file, line_num, prev_line, line)

                if any(re.search(pattern, line) for pattern in [
                    r"\\hyperref\[[^\]]+\]\{[^\}]+\}\s+?",
                    r"\s+\\hyperref\[[^\]]+\]\{[^\}]+\}",
                ]):
                    error("【0006】在\hyperref命令前后存在空格！", file, line_num, prev_line, line)

                if any(re.search(pattern, line) for pattern in [
                    r"\\\)\\DefineConcept\{[^\}]+\}",
                    r"\\DefineConcept\{[^\}]+\}\\\(",
                    r"\\DefineConcept\{[^\}]+\}$",
                ]):
                    error("【0007】在\DefineConcept命令前后存在空格！", file, line_num, prev_line, line)

                prev_line = line

        # 按计数结果，对不为零的计数，报警
        for k, v in environment_counter.items():
            if v == 0:
                continue
            error(f"【1000】环境 `{k}` 计数为 {v}，请检查文件 '{file_path}'!")

    if not is_tex_project_problematic:
        logger.info("检查完毕，没有任何错误！")
        logger.info("本次扫描总计{}行.".format(total_line_counter))
    else:
        logger.error("共计发现{}条错误！请注意检查你的文件！".format(error_counter))
        exit(1)
