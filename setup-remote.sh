#!/bin/bash
# 这个脚本是在开发者本地工作站使用的

URL_GITEE="git@gitee.com:kaiserkatze/mathematical-notes.git"
URL_GITHUB="git@github.com:KaiserKatze/mathematical-notes.git"

url_of_the_remote_named_as_origin=$(git remote get-url origin)

echo "Current Remote: $url_of_the_remote_named_as_origin"

if [[ "$url_of_the_remote_named_as_origin" = "$URL_GITEE" ]]; then
	url_of_the_backup_remote="$URL_GITHUB"
else
	url_of_the_backup_remote="$URL_GITEE"
fi

echo "Backup Remote: $url_of_the_backup_remote"

git remote add backup "$url_of_the_backup_remote"

git remote

for remote in $(git remote); do
	echo "[INFO] URL of '$remote': $(git remote get-url $remote)"
done
