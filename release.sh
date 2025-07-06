#!/bin/bash
# 这个脚本是在开发者本地工作站使用的

RELEASE_TAG=${RELEASE_TAG:-$(date +'%Y%m%d%H%M%S')-$(git log --format=%h -1)}  # 自动生成 git 标签
echo $RELEASE_TAG
