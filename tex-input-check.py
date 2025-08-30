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
from collections import deque

def main():
    base_dir = os.getcwd()
    all_tex_files = set()
    referenced_tex_files = set()
    input_relations = []
    call_count = {}  # 记录每个文件调用其他文件的次数
    graph = {}  # 构建调用关系图
    reverse_graph = {}  # 反向图，用于计算深度

    # 收集所有.tex文件
    for root, _, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.tex'):
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, base_dir).replace('\\', '/')
                all_tex_files.add(rel_path)
                call_count[rel_path] = 0  # 初始化调用次数
                graph[rel_path] = []  # 初始化图的节点
                reverse_graph[rel_path] = []  # 初始化反向图的节点

    # 解析每个.tex文件，收集引用关系
    include_pattern = re.compile(r'\\(?:include|input)\s*{([^}]+)}')
    for tex_file in all_tex_files:
        full_path = os.path.join(base_dir, tex_file)
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"Error reading file {tex_file}: {e}")
            continue

        matches = include_pattern.findall(content)
        call_count[tex_file] = len(matches)  # 记录调用次数

        for match in matches:
            target = match.strip()
            if not target.endswith('.tex'):
                target += '.tex'

            # 如果目标文件存在，则记录关系
            if target in all_tex_files:
                input_relations.append((tex_file, target))
                referenced_tex_files.add(target)
                graph[tex_file].append(target)  # 添加到正向图
                reverse_graph[target].append(tex_file)  # 添加到反向图

    # 找出未被引用的文件
    noinput_files = all_tex_files - referenced_tex_files

    # 计算每个文件的深度
    depth_map = {}
    in_degree = {}  # 记录每个节点的入度

    # 初始化入度
    for node in all_tex_files:
        in_degree[node] = len(reverse_graph[node])

    # 使用拓扑排序计算深度
    queue = deque()
    for node in all_tex_files:
        if in_degree[node] == 0:
            depth_map[node] = 0
            queue.append(node)

    while queue:
        node = queue.popleft()
        for neighbor in graph[node]:
            in_degree[neighbor] -= 1
            # 深度为调用者深度加1
            depth_map[neighbor] = max(depth_map.get(neighbor, 0), depth_map[node] + 1)
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    # 对于可能存在的循环依赖，设置深度为-1（表示无法计算）
    for node in all_tex_files:
        if node not in depth_map:
            depth_map[node] = -1

    # 创建数据库并插入数据
    db_path = os.path.join(base_dir, 'tex_data.sqlite3.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 创建表
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

    # 插入数据
    cursor.executemany('INSERT OR IGNORE INTO tex_input (tex_file_path, target_path) VALUES (?, ?)', input_relations)
    cursor.executemany('INSERT OR IGNORE INTO tex_noinput (tex_file_path) VALUES (?)', [(f,) for f in noinput_files])

    # 插入深度和调用次数数据
    depth_data = []
    for tex_file in all_tex_files:
        depth = depth_map.get(tex_file, 0)
        count = call_count.get(tex_file, 0)
        depth_data.append((tex_file, depth, count))

    cursor.executemany('INSERT OR REPLACE INTO tex_input_depth (tex_file_path, tex_file_depth, tex_file_count) VALUES (?, ?, ?)', depth_data)

    conn.commit()
    conn.close()

    print("Data has been successfully written to tex_data.sqlite3.db")

if __name__ == '__main__':
    main()
