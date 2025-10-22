#!/usr/bin/env python
# -*- coding: utf-8 -*-

#@credit: {deepseek}

# 假设我有一个目录下有若干 .tex 文件和子目录.
# 现在我需要查看当前目录下的所有 .tex 文件，并且递归地查看当前目录的各级子目录下的所有 .tex 文件，
# 并执行以下任务：
# 1. 记录各 .tex 文件的文件名，记录各 .tex 文件中 \include 或 \input 这两种命令的调用，记录上述数据时需要参照下面我用 DDL 描述的格式
# ```sql
# CREATE TABLE tex_input (
# 	-- \include 或 \input 命令出现的 .tex 文件的相对路径
#     tex_file_path TEXT NOT NULL,
# 	-- \include 或 \input 命令指向的 .tex 文件的相对路径（即该命令的参数）
#     target_path TEXT NOT NULL,

# 	PRIMARY KEY (tex_file_path, target_path),
# 	UNIQUE (tex_file_path, target_path)
# );
# ```
# 2. 记录没有被 \include 或 \input 命令指向的 .tex 文件，记录上述数据时需要参照下面我用 DDL 描述的格式
# ```sql
# CREATE TABLE tex_noinput (
# 	-- 没有被 \include 或 \input 命令指向的 .tex 文件的相对路径
# 	tex_file_path TEXT NOT NULL UNIQUE PRIMARY KEY
# );
# ```
# 请按上述要求，利用 python 编写程序，新建名为 `tex_data.sqlite3.db` 的 sqlite3 数据库，并把需要记录的数据存储到 `tex_data.sqlite3.db` 数据库中.

# 现在我新增了需求，我需要记录各个 .tex 文件的调用层级，
# 没有被 \include 或 \input 命令指向的 .tex 文件的调用层级为 0，
# 被 \include 或 \input 命令指向的 .tex 文件的调用层级是调用它的 .tex 文件的调用层级加 1，
# 假设 \include 或 \input 命令的调用关系构成一个有向无环图，
# 同时我需要记录各个 .tex 文件调用其他 .tex 文件的次数，
# 记录上述数据时需要参照下面我用 DDL 描述的格式
# ```sql
# CREATE TABLE tex_input_depth (
#     -- .tex 文件的相对路径
#     tex_file_path TEXT NOT NULL UNIQUE PRIMARY KEY,
#     -- PRIMARY KEY 对应的 .tex 文件的调用层级（未被调用的文件的调用层级为 0，被调用的子文件的调用层级等于调用该子文件的父文件的调用层架加 1）
#     tex_file_depth INTEGER NOT NULL
#     -- PRIMARY KEY 对应的 .tex 文件调用其他 .tex 文件的次数（即 \include 和 \input 命令在 PRIMARY KEY 对应的 .tex 文件中的出现次数）
#     tex_file_count INTEGER NOT NULL
# );
# ```

import os
import re
import sqlite3
from collections import deque, defaultdict
from typing import Dict, List, Set, Tuple, Optional

# --------- helpers ---------

def open_text(path: str) -> Optional[str]:
    '''Read text with sensible fallbacks. Return None on failure.'''
    for enc in ('utf-8', 'utf-8-sig', 'gb18030', 'latin-1'):
        try:
            with open(path, 'r', encoding=enc) as f:
                return f.read()
        except Exception:
            continue
    print(f'[warn] Failed to read text file: {path}')
    return None

def norm_relpath(base_dir: str, p: str) -> str:
    return os.path.relpath(os.path.normpath(p), base_dir).replace('\\', '/')

def resolve_include_target(base_dir: str, owner_rel: str, target: str, all_rel_paths: Set[str]) -> Optional[str]:
    '''
    Resolve an \include/\input target to a normalized relative path under base_dir, if exists.
    Try relative to the owner's directory first; then as-is; finally append .tex if needed.
    '''
    owner_dir = os.path.dirname(os.path.join(base_dir, owner_rel))

    candidates: List[str] = []

    # original target
    t0 = target
    # with .tex
    t1 = target if target.endswith('.tex') else (target + '.tex')

    # candidate paths (absolute)
    candidates_abs = [
        os.path.normpath(os.path.join(owner_dir, t0)),
        os.path.normpath(os.path.join(owner_dir, t1)),
        os.path.normpath(os.path.join(base_dir, t0)),
        os.path.normpath(os.path.join(base_dir, t1)),
    ]

    for cabs in candidates_abs:
        crel = norm_relpath(base_dir, cabs)
        if crel in all_rel_paths:
            return crel
    return None

def parse_math_bib_titles(bib_path: str) -> Set[str]:
    '''
    Parse @book entries and extract title fields (handles nested braces in a simple way).
    Returns a set of titles as plain strings, stripped.
    '''
    titles: Set[str] = set()
    text = open_text(bib_path)
    if text is None:
        return titles

    # Find all @book{ ... } blocks (non-greedy, DOTALL)
    book_blocks = re.findall(r'@book\s*{.*?}', text, flags=re.IGNORECASE | re.DOTALL)
    for block in book_blocks:
        # locate 'title' key
        m = re.search(r'(?i)\btitle\s*=', block)
        if not m:
            continue
        i = m.end()
        # skip spaces
        while i < len(block) and block[i].isspace():
            i += 1
        if i >= len(block):
            continue
        # detect delimiter
        if block[i] == '{':
            # balance braces
            depth = 0
            j = i
            while j < len(block):
                if block[j] == '{':
                    depth += 1
                elif block[j] == '}':
                    depth -= 1
                    if depth == 0:
                        j += 1
                        break
                j += 1
            value = block[i+1:j-1] if j > i+1 else ''
        elif block[i] == '"':
            j = i + 1
            while j < len(block) and block[j] != '"':
                # naive: ignore escapes
                j += 1
            value = block[i+1:j] if j > i+1 else ''
        else:
            # bare value until comma or newline
            j = i
            while j < len(block) and block[j] not in ',\n\r}':
                j += 1
            value = block[i:j]

        title = ' '.join(value.strip().split())
        if title:
            titles.add(title)
    return titles

def normalize_book_name(name: str) -> str:
    '''Normalize extracted book names a bit: trim spaces.'''
    return ' '.join(name.strip().split())

# --------- main workflow ---------

def main():
    base_dir = os.getcwd()
    # ---- scan all .tex files ----
    all_tex_files: Set[str] = set()
    referenced_tex_files: Set[str] = set()
    input_relations: List[Tuple[str, str]] = []
    call_count: Dict[str, int] = {}  # 记录每个文件调用其他文件的次数
    graph: Dict[str, List[str]] = {}  # 构建调用关系图
    reverse_graph: Dict[str, List[str]] = {}  # 反向图，用于计算深度

    # 收集所有.tex文件
    for root, _, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.tex'):
                full_path = os.path.join(root, file)
                rel_path = norm_relpath(base_dir, full_path)
                all_tex_files.add(rel_path)
                call_count[rel_path] = 0  # 初始化调用次数
                graph[rel_path] = []  # 初始化图的节点
                reverse_graph[rel_path] = []  # 初始化反向图的节点

    # 解析每个.tex文件，收集引用关系
    # ---- parse include/input relations ----
    include_pattern = re.compile(r'\\(?:include|input)\s*{([^}]+)}')
    for tex_rel in all_tex_files:
        full_path = os.path.join(base_dir, tex_rel)
        content = open_text(full_path)
        if content is None:
            continue

        matches = include_pattern.findall(content)
        call_count[tex_rel] = len(matches)

        for raw_target in matches:
            target = raw_target.strip()
            resolved = resolve_include_target(base_dir, tex_rel, target, all_tex_files)
            if resolved:
                input_relations.append((tex_rel, resolved))
                referenced_tex_files.add(resolved)
                graph[tex_rel].append(resolved)
                reverse_graph[resolved].append(tex_rel)

    # ---- noinput files ----
    noinput_files = all_tex_files - referenced_tex_files

    # ---- compute depth via topological order ----
    depth_map: Dict[str, int] = {}
    in_degree: Dict[str, int] = {node: len(reverse_graph[node]) for node in all_tex_files}

    q = deque([node for node in all_tex_files if in_degree[node] == 0])
    for node in q:
        depth_map[node] = 0

    while q:
        node = q.popleft()
        for nei in graph[node]:
            in_degree[nei] -= 1
            depth_map[nei] = max(depth_map.get(nei, 0), depth_map[node] + 1)
            if in_degree[nei] == 0:
                q.append(nei)

    # mark cycles (shouldn't happen per DAG assumption)
    for node in all_tex_files:
        if node not in depth_map:
            depth_map[node] = -1

    # ---- NEW: count book references from '#@see: 《...》' ----
    book_ref_pattern = re.compile(r'%@see:\s*《([^》]+)》')
    book_counter: Dict[str, int] = defaultdict(int)

    for tex_rel in all_tex_files:
        full_path = os.path.join(base_dir, tex_rel)
        content = open_text(full_path)
        if content is None:
            continue
        for m in book_ref_pattern.findall(content):
            book_name = normalize_book_name(m)
            if book_name:
                book_counter[book_name] += 1

    # print counts (Top 10)
    if book_counter:
        print('== 引用书籍统计（按引用次数降序，Top 10） ==')
        sorted_items = sorted(book_counter.items(), key=lambda kv: (-kv[1], kv[0]))
        for name, cnt in sorted_items[:10]:
            print(f'《{name}》: {cnt}')
        if len(sorted_items) > 10:
            print(f'(其余 {len(sorted_items) - 10} 项已省略)')
    else:
        print('== 未发现书籍引用 ==')

    # ---- write to sqlite ----
    db_path = os.path.join(base_dir, 'tex_data.sqlite3.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tex_input (
            tex_file_path TEXT NOT NULL,
            target_path TEXT NOT NULL,
            PRIMARY KEY (tex_file_path, target_path)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tex_noinput (
            tex_file_path TEXT NOT NULL UNIQUE PRIMARY KEY
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tex_input_depth (
            tex_file_path TEXT NOT NULL UNIQUE PRIMARY KEY,
            tex_file_depth INTEGER NOT NULL,
            tex_file_count INTEGER NOT NULL
        )
    ''')

    # NEW: book ref table per provided DDL (NUMBER is accepted by SQLite's type affinity)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tex_book_ref (
            book_name TEXT NOT NULL PRIMARY KEY UNIQUE,
            ref_count NUMBER NOT NULL
        )
    ''')

    # inserts
    if input_relations:
        cursor.executemany(
            'INSERT OR IGNORE INTO tex_input (tex_file_path, target_path) VALUES (?, ?)',
            input_relations
        )
    if noinput_files:
        cursor.executemany(
            'INSERT OR IGNORE INTO tex_noinput (tex_file_path) VALUES (?)',
            [(f,) for f in noinput_files]
        )

    depth_data = [(tex, depth_map.get(tex, 0), call_count.get(tex, 0)) for tex in all_tex_files]
    if depth_data:
        cursor.executemany(
            'INSERT OR REPLACE INTO tex_input_depth (tex_file_path, tex_file_depth, tex_file_count) VALUES (?, ?, ?)',
            depth_data
        )

    # NEW: write book references
    if book_counter:
        cursor.executemany(
            'INSERT OR REPLACE INTO tex_book_ref (book_name, ref_count) VALUES (?, ?)',
            [(name, cnt) for name, cnt in book_counter.items()]
        )

    conn.commit()
    conn.close()

    print('\nData has been successfully written to tex_data.sqlite3.db')

if __name__ == '__main__':
    main()
