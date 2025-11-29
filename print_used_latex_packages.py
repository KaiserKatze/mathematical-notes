#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pathlib import Path
import re
import argparse
import sys

# 正则：匹配 \usepackage 或 \UsePackage（不区分大小写），支持可选方括号选项
USEPACKAGE_RE = re.compile(r"\\usepackage(?:\s*)?(?:\[[^\]]*\])?\s*{([^}]*)}", re.IGNORECASE)

# 用于去除行内注释（简单策略：移除未被反斜杠转义的 % 及其后面的内容）
INLINE_COMMENT_RE = re.compile(r"(?<!\\)%.*")

def strip_comments(text: str) -> str:
    """移除行内注释（% 后至行尾），返回处理后的文本"""
    # 按行处理，比较稳健
    lines = []
    for ln in text.splitlines():
        ln_no_comment = INLINE_COMMENT_RE.sub("", ln)
        lines.append(ln_no_comment)
    return "\n".join(lines)

def extract_packages_from_text(text: str):
    """从给定文本中提取 \\usepackage{...} 的包名，返回 set"""
    packages = set()
    text = strip_comments(text)
    for match in USEPACKAGE_RE.findall(text):
        # match 里可能是 "amsmath, amssymb"
        for pkg in match.split(","):
            pkg = pkg.strip()
            if pkg:
                packages.add(pkg)
    return packages

def extract_packages_from_file(path: Path):
    """从文件读取并提取 packages（安全地忽略读取错误）"""
    try:
        content = path.read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        return set()
    return extract_packages_from_text(content)

def main():
    p = argparse.ArgumentParser(description="从主 .tex 提取 \\usepackage 并合并 .sty 中的 usepackage")
    p.add_argument("main_tex", nargs="?", default="math.tex",
                   help="主入口 tex 文件（默认 math.tex）")
    args = p.parse_args()

    main_tex_path = Path(args.main_tex)
    if not main_tex_path.exists():
        sys.exit(2)

    # 1) 从主入口 .tex 提取 packages（set）
    packages = extract_packages_from_file(main_tex_path)

    # 2) 遍历当前目录下的 .sty 文件，提取文件名（不含路径），得到 sty_files 列表
    cwd = Path.cwd()
    sty_paths = sorted(cwd.rglob("*.sty"))

    # 3) 遍历每个 .sty 文件，提取其中的 \\usepackage 命令，更新 packages 集合
    for sty_path in sty_paths:
        packages.update(
            extract_packages_from_file(sty_path)
        )

    # 4) 将 sty 基名（去掉 .sty）从 packages 中去掉
    sty_basenames = {p.stem for p in sty_paths}  # stem 去掉扩展名
    packages -= sty_basenames

    print(
        ','.join(sorted(packages))
    )


if __name__ == "__main__":
    main()
