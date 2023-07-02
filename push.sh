#!/bin/bash
# 这个脚本是在开发者本地工作站使用的

pid_ssh_agent=$(ps -ef | grep ssh-agent | grep -Po '^\w+\s+\K\d+')
if [ -n "$pid_ssh_agent" ]; then
	kill -9 "$pid_ssh_agent"  # 杀死已存在的 SSH Agent 进程
fi
eval $(ssh-agent) && ssh-add || exit 1  # 准备 SSH 密匙

OUTPUT_FILE="数学笔记.pdf"
mv math.pdf "$OUTPUT_FILE"  # 在本地重命名 texlive 输出的 PDF 文件

# 向 Github 推送发行版 PDF 文件
export REPO="KaiserKatze/mathematical-notes"  # Github 仓库
export RELEASE_TAG=${RELEASE_TAG:-$(date +'%Y%m%d%H%M%S')-$(git log --format=%h -1)}  # 自动生成 git 标签
git tag $RELEASE_TAG  # 打标签

# 开始推送
for remote in $(git remote); do
	git push $remote && git push --tags $remote ||\
		echo "[ERROR] Fail git push $remote!" 1>&2
done

export RELEASE_TITLE="Release $RELEASE_TAG"
export RELEASE_NOTES="Daily update"
cat github-token.ignore | awk 'match($0,/^\w+/){print $1}' | gh auth login -p ssh --with-token &&\
	echo "[INFO] Login successfully" &&\
	gh release create "$RELEASE_TAG" "$OUTPUT_FILE" --latest \
		--title "$RELEASE_TITLE" \
		--notes "$RELEASE_NOTES" \
		-R "$REPO" ||\
	echo "[ERROR] Fail to upload release $RELEASE_TAG!" 1>&2 && exit 1
